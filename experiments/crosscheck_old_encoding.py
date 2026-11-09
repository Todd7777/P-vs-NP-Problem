#!/usr/bin/env python3
"""
crosscheck_old_encoding.py -- refute one instance with the first encoding (exact_circuit_complexity.encode)
and keep a DRAT proof, as an independent check of a lower bound found with circuit_sat.py.

The first encoding was written separately and uses only symmetry breaking whose soundness is
immediate (nontrivial gates, every non-output gate used, no two gates with the same inputs and
operator, output last). It is much slower, so it is used only where no published value exists to
compare with (MOD3_4 in U2).

Usage: python3 crosscheck_old_encoding.py NAME BASIS K PROOF_DIR   (writes results/crosscheck_old_encoding.json)
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


if __name__ == "__main__":
    main(*sys.argv[1:5])
