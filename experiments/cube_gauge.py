#!/usr/bin/env python3
"""
cube_gauge.py -- solve the cubes of one instance WITHOUT proofs (exploration; results are Numerical).

Same cubes as certify_cubes.py: one per pair that gate GATE (default n + 1) can read, and with
--refine Q:G2 cube Q is split again over the pairs gate G2 can read. Both at-least-one clauses are in
the CNF, so if every cube is UNSAT the instance is UNSAT. A per-call conflict budget turns a cube
that takes too long into "None" (undecided). Prints one JSON line per cube; a satisfiable cube's
circuit is re-evaluated on the truth table and printed with it.

Usage: python3 cube_gauge.py NAME BASIS K [--gate G] [--refine Q:G2,...] [--budget CONFLICTS] [--workers 4] [--elim]
  --elim adds the gate-elimination constraints (elimination.py; restriction costs from results/restriction_costs.json).
  --undecided-from FILE reruns only the cubes that FILE (earlier output of this script) left undecided.
"""
import argparse, json, time
from multiprocessing import Pool

import circuit_sat as C
import elimination as EL
import exact_circuit_complexity as E

A = None


def job(cube):
    full, n, tt = C.suite_function(A.name)
    enc = C.Encoding(n, tt, A.k, A.basis)
    if A.elim:
        EL.add_elimination_constraints(enc, EL.certified_bounds(n, tt)[0], A.elim_level)
    t0 = time.time()
    r = C.run_solver(enc, extra_units=[enc.s[g][q] for g, q in cube], budget=A.budget)
    rec = {"cube": [[g, q, list(enc.pairs[g][q])] for g, q in cube], "result": r["result"],
           "seconds": round(time.time() - t0, 1), "conflicts": r["stats"].get("conflicts")}
    if r["result"] is True:                         # a circuit: re-evaluate it and print it
        gates = enc.decode(r["model"])
        assert E.verify(n, tt, gates), "decoded circuit does not compute the target"
        rec.update(circuit=E.gates_to_str(n, gates), gates=[list(g[:3]) + [list(g[3])] for g in gates])
    return rec


def cubes_of(a):
    from certify_cubes import parse_refine, split_cubes
    full, n, tt = C.suite_function(a.name)
    enc = C.Encoding(n, tt, a.k, a.basis)
    gate = a.gate if a.gate is not None else n + 1
    return split_cubes(enc, gate, parse_refine(a.refine))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("basis")
    ap.add_argument("k", type=int)
    ap.add_argument("--gate", type=int)
    ap.add_argument("--refine", default="")
    ap.add_argument("--budget", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--elim", action="store_true")
    ap.add_argument("--elim-level", type=int, default=1)
    ap.add_argument("--undecided-from")
    A = ap.parse_args()
    cubes = cubes_of(A)
    if A.undecided_from:
        prev = [json.loads(l) for l in open(A.undecided_from) if l.startswith("{")]
        left = {tuple((g, q) for g, q, _ in r["cube"]) for r in prev if r["result"] is None}
        cubes = [c for c in cubes if tuple(c) in left]
        assert len(cubes) == len(left), "some undecided cubes are not cubes of this split"
    with Pool(A.workers) as pool:
        for rec in pool.imap_unordered(job, cubes):
            print(json.dumps(rec), flush=True)
