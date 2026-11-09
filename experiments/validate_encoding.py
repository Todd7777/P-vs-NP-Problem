#!/usr/bin/env python3
"""
validate_encoding.py -- cross-check the symmetry-reduced encoding of circuit_sat.py.

1. n = 3: SAT costs vs exhaustive enumeration (brute_force.py) for all 256 functions, in B2 (all
   costs) and in U2 (all costs up to 4; everything else must be refuted at every k <= 4).
2. n = 4, B2: exact cost of all 222 NPN classes; the distribution over all 65,536 functions must
   equal Knuth's table (TAOCP 4A §7.1.2, reproduced by the first run) and every class must get the
   same cost as in results/n4_exact_costs.json (old encoding, fewer symmetry-breaking rules).
3. n = 4, U2 (optional, slower): every class whose U2 cost the old runs determined exactly must get
   the same value; for the classes they left open, the new values are reported.
Writes results/validation_encoding.json.

Usage: python3 validate_encoding.py [b2|u2|all] [workers]
"""
import json, os, sys, time
from collections import Counter
from multiprocessing import Pool

import brute_force as BF
import circuit_sat as C
import exact_circuit_complexity as E

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
KNUTH_N4 = {0: 10, 1: 60, 2: 456, 3: 2474, 4: 10624, 5: 24184, 6: 25008, 7: 2720}


def check_n3():
    out = {}
    for basis, kmax in (("B2", 4), ("U2", 4)):
        tab = BF.chain_costs(3, kmax, basis)
        mismatches, dist = [], Counter()
        for x in range(256):
            tt = [(x >> t) & 1 for t in range(8)]
            bf = BF.cost_of(3, tt, tab)
            r = C.cost(3, tt, basis, kmax=kmax)
            sat = r["upper"] if r["status"] == "exact" else None
            if bf != sat or (sat is None and r["lower"] != kmax + 1):
                mismatches.append(x)
            dist[str(bf) if bf is not None else f">{kmax}"] += 1
        out[basis] = {"kmax": kmax, "mismatches": mismatches, "distribution": dict(sorted(dist.items()))}
        print(f"n=3 {basis}: {len(mismatches)} mismatches; distribution {dict(sorted(dist.items()))}", flush=True)
    return out


def _class_job(args):
    canon, basis = args
    t0 = time.time()
    r = C.cost(4, E.int_to_tt(canon, 4), basis)
    return canon, basis, r["lower"], r["upper"], r["status"], round(time.time() - t0, 2)


def check_n4(basis, workers):
    base = {c["canonical"]: c for c in json.load(open(os.path.join(R, "n4_exact_costs.json")))["classes"]}
    old_u2 = {}
    if basis == "U2":
        summ = json.load(open(os.path.join(R, "n4_u2_summary.json")))
        open_cls = {int(o["canonical"], 16): (o["U2_lower"], o["U2_upper"]) for o in summ["open_classes"]}
        for canon, c in base.items():
            old_u2[canon] = open_cls.get(canon, (c["U2_lower"], c["U2_upper"]))
            # classes closed by the 50M-budget run are not in n4_exact_costs.json; take them from the summary
    t0 = time.time()
    with Pool(workers) as pool:
        res = pool.map(_class_job, [(c, basis) for c in sorted(base)], chunksize=1)
    dist, disagree, newly = Counter(), [], []
    for canon, b, lo, hi, st, sec in res:
        assert st == "exact", (canon, lo, hi)
        dist[hi] += base[canon]["size"]
        if basis == "B2" and hi != base[canon]["cost_B2"]:
            disagree.append((hex(canon), base[canon]["cost_B2"], hi))
        if basis == "U2":
            olo, ohi = old_u2[canon]
            if not (olo <= hi <= (ohi if ohi is not None else hi)):
                disagree.append((hex(canon), olo, ohi, hi))
            elif olo != ohi:
                newly.append({"canonical": hex(canon), "old_interval": [olo, ohi], "new": hi})
    out = {"basis": basis, "seconds": round(time.time() - t0, 1), "distribution": dict(sorted(dist.items())),
           "disagreements": disagree, "classes": [{"canonical": hex(c), "cost": hi, "seconds": s}
                                                 for c, b, lo, hi, st, s in res]}
    if basis == "B2":
        out["matches_knuth"] = dict(sorted(dist.items())) == KNUTH_N4
    else:
        out["previously_open"] = newly
    print(f"n=4 {basis}: {len(disagree)} disagreements; distribution {dict(sorted(dist.items()))}; "
          f"{out['seconds']}s" + (f"; matches Knuth: {out['matches_knuth']}" if basis == "B2" else ""), flush=True)
    return out


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "b2"
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    path = os.path.join(R, "validation_encoding.json")
    out = json.load(open(path)) if os.path.exists(path) else {}
    out["rules"] = C.DEFAULT_RULES
    if what in ("b2", "all"):
        out["n3"] = check_n3()
        out["n4_B2"] = check_n4("B2", workers)
    if what in ("u2", "all"):
        out["n4_U2"] = check_n4("U2", workers)
    json.dump(out, open(path, "w"), indent=1)
