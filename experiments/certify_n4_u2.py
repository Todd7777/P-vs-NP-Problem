#!/usr/bin/env python3
"""
certify_n4_u2.py -- the complete U2 cost distribution over all 65,536 functions of 4 variables.

The first runs (results/n4_exact_costs.json, results/n4_u2_summary.json) left four NPN classes with
only an interval. For each of them this script runs circuit_sat.py at k = 1, 2, ...: every k that is
UNSAT is refuted by a DRAT proof that drat-trim checks, and the first SAT k gives a circuit that is
re-evaluated on the whole truth table. The other 218 classes take the value computed by
validate_encoding.py with the same encoding (results/validation_encoding.json; solver answers
without proofs, equal to the first runs wherever those were exact).

Writes results/n4_u2_open_classes.json (the four classes, with certificates) and then
results/n4_u2_complete.json (needs validate_encoding.py u2 to have run). (summarize_u2_n4.py cannot be rerun from the repository: the
per-class output of the 50M-budget closure run, results/n4_u2_closure.json, was never committed.)

Usage: python3 certify_n4_u2.py --proofs DIR [--workers 4]
"""
import argparse, json, os, time
from collections import Counter
from multiprocessing import Pool

import circuit_sat as C
import exact_circuit_complexity as E

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def close_class(args):
    canon, proofs = args
    tt = E.normalize(E.int_to_tt(canon, 4))
    refuted, k, t0 = [], 1, time.time()
    while True:
        rec = C.certify(C.Encoding(4, tt, k, "U2"), proofs, f"n4class_{canon:04x}_U2_k{k}")
        if rec["result"] is True:
            return {"canonical": hex(canon), "cost": k, "circuit": rec["circuit"],
                    "gates": [list(g[:3]) + [list(g[3])] for g in rec["gates"]], "refutations": refuted,
                    "all_refutations_drat_verified": all(r["drat_trim_verified"] for r in refuted),
                    "seconds": round(time.time() - t0, 1)}
        assert rec["result"] is False
        refuted.append({"k": k, "cnf_sha256": rec["cnf_sha256"], "proof_sha256": rec["proof_sha256"],
                        "proof_bytes": rec["proof_bytes"], "solve_seconds": rec["solve_seconds"],
                        "drat_trim_verified": rec["drat_trim"]["verified"], "drat_trim_seconds": rec["drat_trim"]["seconds"]})
        print(f"  class {canon:#06x}: k={k} refuted ({rec['solve_seconds']}s, drat-trim "
              f"{rec['drat_trim']['verified']} {rec['drat_trim']['seconds']}s)", flush=True)
        k += 1


def main(a):
    summ = json.load(open(os.path.join(R, "n4_u2_summary.json")))
    base = {c["canonical"]: c for c in json.load(open(os.path.join(R, "n4_exact_costs.json")))["classes"]}
    open_cls = [int(o["canonical"], 16) for o in summ["open_classes"]]
    os.makedirs(a.proofs, exist_ok=True)
    with Pool(a.workers, maxtasksperchild=1) as pool:
        closed = pool.map(close_class, [(c, a.proofs) for c in open_cls], chunksize=1)
    for r, o in zip(closed, summ["open_classes"]):
        r["old_interval"] = [o["U2_lower"], o["U2_upper"]]
        r["size"] = o["size"]
        assert o["U2_lower"] <= r["cost"] <= o["U2_upper"], r
        print(f"class {r['canonical']} (size {r['size']}): U2 cost {r['cost']} (was {r['old_interval']}); "
              f"drat-verified: {r['all_refutations_drat_verified']}", flush=True)
    json.dump(closed, open(os.path.join(R, "n4_u2_open_classes.json"), "w"), indent=1)
    val = json.load(open(os.path.join(R, "validation_encoding.json")))["n4_U2"]     # needs validate_encoding.py u2
    numerical = {int(c["canonical"], 16): c["cost"] for c in val["classes"]}
    cost = dict(numerical)
    cost.update({int(r["canonical"], 16): r["cost"] for r in closed})
    assert sorted(cost) == sorted(base), "every NPN class needs a value"
    dist = Counter()
    for canon, c in cost.items():
        dist[c] += base[canon]["size"]
    dist = {int(k): v for k, v in sorted(dist.items())}
    # the 218 classes outside the open ones must reproduce the exact part of the old summary
    old_part = Counter()
    for canon, c in numerical.items():
        old_part[c] += base[canon]["size"]
    same_as_old = {str(k): v for k, v in sorted(old_part.items())} == summ["distribution_U2_exact_part"]
    out = {"distribution_U2": dist, "functions": sum(dist.values()), "classes": len(cost),
           "previously_open_classes": closed, "other_classes_source": "results/validation_encoding.json (n4_U2)",
           "other_classes_reproduce_old_exact_part": same_as_old,
           "distribution_B2": summ["distribution_B2"]}
    json.dump(out, open(os.path.join(R, "n4_u2_complete.json"), "w"), indent=1)
    print("U2 distribution over all 65,536 functions:", dist, "| other classes reproduce the old exact part:", same_as_old)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--proofs", required=True)
    ap.add_argument("--workers", type=int, default=4)
    main(ap.parse_args())
