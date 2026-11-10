#!/usr/bin/env python3
"""
crosscheck_old_encoding.py -- refute one instance with the first encoding (exact_circuit_complexity.encode)
and keep a DRAT proof, as an independent check of a lower bound found with circuit_sat.py.

The first encoding was written separately and uses only symmetry breaking whose soundness is
immediate (nontrivial gates, every non-output gate used, no two gates with the same inputs and
operator, output last). It is much slower, so it is used only where no published value exists to
compare with (MOD3_4 in U2).

Usage: python3 crosscheck_old_encoding.py NAME BASIS K PROOF_DIR   (writes results/crosscheck_old_encoding.json)
       python3 crosscheck_old_encoding.py --cubes NAME BASIS K PROOF_DIR [WORKERS]
           splits the instance into cubes on the first two gates' input pairs (no symmetry assumed),
           each with its own checked proof (writes results/crosscheck_old_encoding_cubes.json)
"""
import json, os, sys, time

import circuit_sat as C
import exact_circuit_complexity as E

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


class OldEncoding:
    """Adapter so that circuit_sat.certify can run the first encoding."""

    def __init__(self, n, tt, k, basis):
        self.n, self.k, self.basis, self.target = n, k, basis, tt
        self.rules = "first encoding (exact_circuit_complexity.encode, symmetry=True)"
        self.clauses, self._decode = E.encode(n, tt, k, basis=basis, symmetry=True)
        self.nvars = max(abs(l) for c in self.clauses for l in c)

    def dimacs(self, extra_units=()):
        cls = self.clauses + [[u] for u in extra_units]
        return (f"p cnf {self.nvars} {len(cls)}\n" + "".join(" ".join(map(str, c)) + " 0\n" for c in cls)).encode()

    def decode(self, model):
        return self._decode(model)


def main(name, basis, k, proofs):
    full, n, tt = C.suite_function(name)
    assert E.depends_on_all(n, tt)
    enc = OldEncoding(n, tt, int(k), basis)
    t0 = time.time()
    rec = C.certify(enc, proofs, f"old_{full.split(' ')[0]}_{basis}_k{k}")
    rec.pop("gates", None)
    rec.update(name=full, wall_seconds=round(time.time() - t0, 1))
    path = os.path.join(R, "crosscheck_old_encoding.json")
    data = json.load(open(path)) if os.path.exists(path) else []
    data = [d for d in data if (d["name"], d["basis"], d["k"]) != (full, basis, int(k))] + [rec]
    json.dump(data, open(path, "w"), indent=1)
    print(json.dumps({x: rec.get(x) for x in ("name", "basis", "k", "result", "solve_seconds", "proof_bytes")}),
          rec.get("drat_trim", {}).get("verified"))




# ---------------------------------------------------------------- cube mode
def _old_selection_vars(n, k):
    """Selection variables of the first encoding, by replaying its variable allocation order
    (per gate: one variable per pair (j, l) with j < l < i, then 3 operator bits, then 2^n - 1 values)."""
    nxt, sel = 1, {}
    for i in range(n, n + k):
        pairs = [(j, l) for j in range(i) for l in range(j + 1, i)]
        sel[i] = {p: nxt + q for q, p in enumerate(pairs)}
        nxt += len(pairs) + 3 + (1 << n) - 1
    return sel


def _cube_job(args):
    name, basis, k, proofs, units, tag = args
    full, n, tt = C.suite_function(name)
    enc = OldEncoding(n, tt, k, basis)
    rec = C.certify(enc, proofs, tag, extra_units=units)
    rec.pop("gates", None)
    return rec


def main_cubes(name, basis, k, proofs, workers=4):
    """Refute the first encoding at k as the cubes 'gate n reads pair p, gate n+1 reads pair q'.
    Both at-least-one clauses are in the CNF, so the cubes cover every model; no symmetry is assumed."""
    from multiprocessing import Pool
    full, n, tt = C.suite_function(name)
    k = int(k)
    enc = OldEncoding(n, tt, k, basis)
    sel = _old_selection_vars(n, k)
    for g in (n, n + 1):
        assert sorted(sel[g].values()) in [sorted(c) for c in enc.clauses], "allocation replay does not match"
    cubes = [(p, q) for p in sel[n] for q in sel[n + 1]]
    short = full.split(" ")[0]
    jobs = [(name, basis, k, proofs, [sel[n][p], sel[n + 1][q]], f"oldcube_{short}_{basis}_k{k}_{p[0]}{p[1]}_{q[0]}{q[1]}")
            for p, q in cubes]
    t0, recs = time.time(), []
    with Pool(int(workers), maxtasksperchild=1) as pool:
        for rec in pool.imap_unordered(_cube_job, jobs):
            recs.append(rec)
            d = rec.get("drat_trim", {})
            print(f"[{time.time() - t0:6.0f}s] {len(recs)}/{len(jobs)} {rec['tag']}: {rec['result']} "
                  f"solve {rec['solve_seconds']}s drat-trim {d.get('verified')} {d.get('seconds')}s", flush=True)
    recs.sort(key=lambda r: r["tag"])
    out = {"name": full, "basis": basis, "k": k, "encoding": enc.rules, "full_cnf_sha256": C.sha256(enc.dimacs()),
           "coverage": f"cubes over the at-least-one clauses of gates {n} and {n + 1} (both in the CNF)",
           "cubes": len(recs), "all_unsat_and_verified": all(r["result"] is False and r.get("drat_trim", {}).get("verified")
                                                            for r in recs),
           "wall_seconds": round(time.time() - t0, 1), "records": recs}
    json.dump(out, open(os.path.join(R, "crosscheck_old_encoding_cubes.json"), "w"), indent=1)
    print(full, basis, "k =", k, "refuted by", len(recs), "cubes:", out["all_unsat_and_verified"])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cubes":
        main_cubes(*sys.argv[2:7])
    else:
        main(*sys.argv[1:5])
