#!/usr/bin/env python3
"""
certify_restrictions.py -- Machine-checked U2 costs of the one-variable restrictions of a function.

These are the inputs of the gate-elimination constraints (elimination.py, ENCODING.md §5). For each
NAME (a suite function of n inputs) and every restriction f|x_v=c, a function of n - 1 inputs, the
exact U2 cost is certified as in certify_n4_u2.py: every smaller k is refuted by a DRAT proof that
drat-trim checks, and a circuit at the cost is re-evaluated. Restrictions are deduplicated by their
normalized truth table. Results go to results/restriction_costs.json.

Usage: python3 certify_restrictions.py NAME [NAME ...] --proofs DIR [--workers 4]
"""
import argparse, json, os, time
from multiprocessing import Pool

import circuit_sat as C
import elimination as EL
import exact_circuit_complexity as E

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
OUT = os.path.join(R, "restriction_costs.json")


def certify_cost(args):
    n, key, proofs = args
    tt = E.int_to_tt(int(key, 16), n)
    assert C.support(n, tt) == list(range(n)), "restrictions are expected to depend on every input"
    refuted, k, t0 = [], 1, time.time()
    while True:
        rec = C.certify(C.Encoding(n, tt, k, "U2"), proofs, f"restr_n{n}_{key}_U2_k{k}")
        if rec["result"] is True:
            return {"n": n, "tt": key, "basis": "U2", "cost": k, "circuit": rec["circuit"],
                    "gates": [list(g[:3]) + [list(g[3])] for g in rec["gates"]], "refutations": refuted,
                    "all_refutations_drat_verified": all(r["drat_trim_verified"] for r in refuted),
                    "seconds": round(time.time() - t0, 1)}
        assert rec["result"] is False
        refuted.append({"k": k, "cnf_sha256": rec["cnf_sha256"], "proof_sha256": rec["proof_sha256"],
                        "proof_bytes": rec["proof_bytes"], "solve_seconds": rec["solve_seconds"],
                        "drat_trim_verified": rec["drat_trim"]["verified"], "drat_trim_seconds": rec["drat_trim"]["seconds"]})
        k += 1


def main(a):
    data = json.load(open(OUT)) if os.path.exists(OUT) else []
    have = {(r["n"], r["tt"]) for r in data}
    jobs, origin = [], {}
    for name in a.names:
        full, n, tt = C.suite_function(name)
        for v in range(n):
            for c in (0, 1):
                key = EL.tt_hex(EL.restriction(n, tt, v, c))
                origin.setdefault((n - 1, key), set()).add(f"{full}: x{v + 1}={c}")
                if (n - 1, key) not in have and (n - 1, key, a.proofs) not in jobs:
                    jobs.append((n - 1, key, a.proofs))
    os.makedirs(a.proofs, exist_ok=True)
    with Pool(a.workers, maxtasksperchild=1) as pool:
        for rec in pool.imap_unordered(certify_cost, jobs):
            data.append(rec)
            print(f"n={rec['n']} {rec['tt']}: U2 cost {rec['cost']}, refutations drat-verified "
                  f"{rec['all_refutations_drat_verified']} ({rec['seconds']}s)", flush=True)
    for r in data:
        r["restriction_of"] = sorted(set(r.get("restriction_of", [])) | origin.get((r["n"], r["tt"]), set()))
    data.sort(key=lambda r: (r["n"], int(r["tt"], 16)))
    json.dump(data, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="+")
    ap.add_argument("--proofs", required=True)
    ap.add_argument("--workers", type=int, default=4)
    main(ap.parse_args())
