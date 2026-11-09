#!/usr/bin/env python3
"""
certify_cubes.py -- refute one hard instance as a set of cubes, each with its own checked DRAT proof.

The CNF F of circuit_sat.Encoding contains, for every gate i, the clause s[i][0] v ... v s[i][P-1]
("gate i reads some pair"). Hence F is unsatisfiable iff F & s[i][q] is unsatisfiable for every q:
a model of F satisfies that clause, so it satisfies one of the cubes. This script solves every cube
F & s[i][q] for a chosen gate i (default: the second gate, i = n + 1) in parallel, keeps each proof,
and checks it with drat-trim. Smaller proofs are much faster to check than one large proof.

Usage: python3 certify_cubes.py NAME BASIS K --proofs DIR [--gate I] [--workers 4]
Writes results/cube_certificates.json (one entry per instance, one record per cube).
"""
import argparse, json, os, time
from multiprocessing import Pool

import circuit_sat as C

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def cube_job(args):
    name, basis, k, gate, q, proofs = args
    full, n, tt = C.suite_function(name)
    enc = C.Encoding(n, tt, k, basis)
    unit = enc.s[gate][q]
    rec = C.certify(enc, proofs, f"{full.split(' ')[0]}_{basis}_k{k}_g{gate}_q{q}", extra_units=[unit])
    rec.pop("gates", None)
    rec.update(name=full, gate=gate, pair=list(enc.pairs[gate][q]), cube_literal=unit)
    return rec


def main(a):
    full, n, tt = C.suite_function(a.name)
    gate = a.gate if a.gate is not None else n + 1
    enc = C.Encoding(n, tt, a.k, a.basis)
    alo = list(enc.s[gate])
    assert alo in enc.clauses, "the at-least-one clause of this gate must be in the CNF"
    jobs = [(a.name, a.basis, a.k, gate, q, a.proofs) for q in range(len(alo))]
    os.makedirs(a.proofs, exist_ok=True)
    t0, recs = time.time(), []
    with Pool(a.workers, maxtasksperchild=1) as pool:
        for rec in pool.imap_unordered(cube_job, jobs):
            recs.append(rec)
            d = rec.get("drat_trim", {})
            print(f"[{time.time() - t0:6.0f}s] cube s[{gate}]{tuple(rec['pair'])}: {rec['result']} "
                  f"solve {rec['solve_seconds']}s, drat-trim {d.get('verified')} {d.get('seconds')}s", flush=True)
    recs.sort(key=lambda r: r["cube_literal"])
    entry = {"name": full, "basis": a.basis, "k": a.k, "gate": gate, "full_cnf_sha256": C.sha256(enc.dimacs()),
             "coverage": f"clause s[{gate}][0..{len(alo) - 1}] is in the CNF; one cube per literal",
             "all_unsat_and_verified": all(r["result"] is False and r.get("drat_trim", {}).get("verified") for r in recs),
             "cubes": recs}
    path = os.path.join(R, "cube_certificates.json")
    data = json.load(open(path)) if os.path.exists(path) else []
    data = [d for d in data if (d["name"], d["basis"], d["k"]) != (full, a.basis, a.k)] + [entry]
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
    main(ap.parse_args())
