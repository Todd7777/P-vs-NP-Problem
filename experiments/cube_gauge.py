#!/usr/bin/env python3
"""
cube_gauge.py -- solve the cubes of one instance WITHOUT proofs (exploration; results are Numerical).

Same cubes as certify_cubes.py: one per pair that gate GATE (default n + 1) can read, and with
--refine Q:G2 cube Q is split again over the pairs gate G2 can read. Both at-least-one clauses are in
the CNF, so if every cube is UNSAT the instance is UNSAT. A per-call conflict budget turns a cube
that takes too long into "None" (undecided). Prints one JSON line per cube.

Usage: python3 cube_gauge.py NAME BASIS K [--gate G] [--refine Q:G2,...] [--budget CONFLICTS] [--workers 4]
"""
import argparse, json, time
from multiprocessing import Pool

import circuit_sat as C

A = None


def job(cube):
    full, n, tt = C.suite_function(A.name)
    enc = C.Encoding(n, tt, A.k, A.basis)
    t0 = time.time()
    r = C.run_solver(enc, extra_units=[enc.s[g][q] for g, q in cube], budget=A.budget)
    return {"cube": [[g, q, list(enc.pairs[g][q])] for g, q in cube], "result": r["result"],
            "seconds": round(time.time() - t0, 1), "conflicts": r["stats"].get("conflicts")}


def cubes_of(a):
    full, n, tt = C.suite_function(a.name)
    enc = C.Encoding(n, tt, a.k, a.basis)
    gate = a.gate if a.gate is not None else n + 1
    assert list(enc.s[gate]) in enc.clauses
    refine = {int(x.split(":")[0]): int(x.split(":")[1]) for x in a.refine.split(",") if x}
    out = []
    for q in range(len(enc.s[gate])):
        if q in refine:
            assert list(enc.s[refine[q]]) in enc.clauses
            out += [[(gate, q), (refine[q], q2)] for q2 in range(len(enc.s[refine[q]]))]
        else:
            out.append([(gate, q)])
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("basis")
    ap.add_argument("k", type=int)
    ap.add_argument("--gate", type=int)
    ap.add_argument("--refine", default="")
    ap.add_argument("--budget", type=int)
    ap.add_argument("--workers", type=int, default=4)
    A = ap.parse_args()
    with Pool(A.workers) as pool:
        for rec in pool.imap_unordered(job, cubes_of(A)):
            print(json.dumps(rec), flush=True)
