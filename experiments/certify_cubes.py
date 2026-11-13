#!/usr/bin/env python3
"""
certify_cubes.py -- refute one hard instance as a set of cubes, each with its own checked DRAT proof.

The CNF F of circuit_sat.Encoding contains, for every gate i, the clause s[i][0] v ... v s[i][P-1]
("gate i reads some pair"). Hence F is unsatisfiable iff F & s[i][q] is unsatisfiable for every q:
a model of F satisfies that clause, so it satisfies one of the cubes. This script solves every cube
F & s[i][q] for a chosen gate i (default: the second gate, i = n + 1) in parallel, keeps each proof,
and checks it with drat-trim. Smaller proofs are much faster to check than one large proof.

Usage: python3 certify_cubes.py NAME BASIS K --proofs DIR [--gate I] [--workers 4] [--refine Q:GATE,...] [--elim]
  --refine splits first-level cube Q again over the pairs that GATE can read (two-level cubes).
  --elim   (U2) adds the gate-elimination constraints of elimination.py, with the restriction costs
           certified in results/restriction_costs.json (soundness: ENCODING.md §5).
Writes results/cube_certificates.json (one entry per instance, one record per cube).
"""
import argparse, json, os, re, time
from multiprocessing import Pool

import circuit_sat as C
import elimination as EL

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def encoding(name, basis, k, L=None, level=1):
    full, n, tt = C.suite_function(name)
    enc = C.Encoding(n, tt, k, basis)
    if L is not None:
        EL.add_elimination_constraints(enc, L, level)
    return enc


def cube_job(args):
    name, basis, k, cube, proofs, L, level = args        # cube: list of (gate, q); L: elimination bounds or None
    full, n, tt = C.suite_function(name)
    enc = encoding(name, basis, k, L, level)
    units = [enc.s[g][q] for g, q in cube]
    tag = (f"{re.sub(r'[^A-Za-z0-9]+', '_', full).strip('_')}_{basis}_k{k}_" + ("" if not L else "elim_" if level == 1 else f"elim{level}_")
           + "_".join(f"g{g}q{q}" for g, q in cube))
    rec = C.certify(enc, proofs, tag, extra_units=units)
    rec.pop("gates", None)
    rec.update(name=full, cube=[[g, q, list(enc.pairs[g][q])] for g, q in cube], cube_literals=units)
    return rec


def main(a):
    full, n, tt = C.suite_function(a.name)
    gate = a.gate if a.gate is not None else n + 1
    L, used = EL.certified_bounds(n, tt) if getattr(a, "elim", False) else (None, None)
    level = getattr(a, "elim_level", 1)
    enc = encoding(a.name, a.basis, a.k, L, level)
    alo = list(enc.s[gate])
    assert alo in enc.clauses, "the at-least-one clause of this gate must be in the CNF"
    refine = {}                                         # q -> second gate whose pairs split cube q further
    for item in (getattr(a, "refine", None) or "").split(","):
        if item:
            q, g2 = map(int, item.split(":"))
            assert list(enc.s[g2]) in enc.clauses
            refine[q] = g2
    cubes = []
    for q in range(len(alo)):
        if q in refine:
            cubes += [[(gate, q), (refine[q], q2)] for q2 in range(len(enc.s[refine[q]]))]
        else:
            cubes.append([(gate, q)])
    jobs = [(a.name, a.basis, a.k, cube, a.proofs, L, level) for cube in cubes]
    os.makedirs(a.proofs, exist_ok=True)
    t0, recs = time.time(), []
    with Pool(a.workers, maxtasksperchild=1) as pool:
        for rec in pool.imap_unordered(cube_job, jobs):
            recs.append(rec)
            d = rec.get("drat_trim", {})
            print(f"[{time.time() - t0:6.0f}s] cube {[tuple(c[2]) for c in rec['cube']]}: {rec['result']} "
                  f"solve {rec['solve_seconds']}s, drat-trim {d.get('verified')} {d.get('seconds')}s", flush=True)
    recs.sort(key=lambda r: r["cube_literals"])
    entry = {"name": full, "basis": a.basis, "k": a.k, "gate": gate, "refine": refine,
             "full_cnf_sha256": C.sha256(enc.dimacs()),
             "coverage": (f"clause s[{gate}][0..{len(alo) - 1}] is in the CNF; one cube per literal"
                          + (f"; cubes {sorted(refine)} are split again over the at-least-one clause of gate(s) "
                             f"{sorted(set(refine.values()))}, also in the CNF" if refine else "")),
             "all_unsat_and_verified": all(r["result"] is False and r.get("drat_trim", {}).get("verified") for r in recs),
             "cubes": recs}
    if L is not None:
        entry["elimination"] = {"L": L, "level": level, "restriction_costs": used,
                                "source": "results/restriction_costs.json", "soundness": "ENCODING.md §5"}
    path = os.path.join(R, "cube_certificates.json")
    data = json.load(open(path)) if os.path.exists(path) else []
    data = [d for d in data if (d["name"], d["basis"], d["k"], "elimination" in d) != (full, a.basis, a.k, L is not None)]
    data.append(entry)
    json.dump(data, open(path, "w"), indent=1)
    print(full, a.basis, "k =", a.k, "refuted by cubes:", entry["all_unsat_and_verified"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("basis")
    ap.add_argument("k", type=int)
    ap.add_argument("--proofs", required=True)
    ap.add_argument("--gate", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--refine", default="", help="Q:GATE[,...]: split cube Q again over the pairs of GATE")
    ap.add_argument("--elim", action="store_true", help="add the gate-elimination constraints (U2)")
    ap.add_argument("--elim-level", type=int, default=1, help="1: (E1), (E2); 2: also (E3) (ENCODING.md §5)")
    main(ap.parse_args())
