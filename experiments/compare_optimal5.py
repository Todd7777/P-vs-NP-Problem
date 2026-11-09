#!/usr/bin/env python3
"""
compare_optimal5.py -- compare B2 costs with Knuth's exhaustive table of all 5-input functions.

A. P. Goucher's `optimal5` (https://gitlab.com/apgoucher/optimal5) stores one optimal chain for each
of the 616,126 NPN classes of 5-input Boolean functions in a binary file, `knuthies.dat`. Its README
says the chains were computed by Knuth for TAOCP with his BOOLCHAINS programs, and its checktab.py
asserts the number of classes and functions per cost "agrees with chapter 7.1.2 of Knuth" (we have
not read Knuth's text itself). Same cost model as ours: 2-input gates cost 1, negations are free.
This script parses the file with its own code (the record layout is documented in optimal5.h: 15
bytes per class, up to twelve 10-bit gates; operators &, |, ^, &~), recomputes the function of every
stored chain (so each stored chain is a verified upper bound), and then

  1. checks that the number of classes per cost equals the table in checktab.py, and
  2. looks up every function of the explicit suite (n <= 5; a function of fewer inputs is a 5-input
     function that ignores the rest, with the same cost) by trying all 7,680 NPN transforms of its
     truth table against the stored class representatives, and
  3. compares the B2 cost of each of the 222 NPN classes of 4-input functions in
     results/n4_exact_costs.json the same way.

Usage: python3 compare_optimal5.py PATH/TO/knuthies.dat   (writes results/optimal5_comparison.json)
"""
import hashlib, itertools, json, os, sys

import exact_circuit_complexity as E

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
# Classes and functions per cost 0..12, as asserted in optimal5/checktab.py (Knuth, TAOCP 4A §7.1.2).
KNUTH_TABLE2 = {0: (2, 12), 1: (2, 100), 2: (5, 1140), 3: (20, 11570), 4: (93, 109826), 5: (389, 995240),
                6: (1988, 8430800), 7: (11382, 63401728), 8: (60713, 383877392), 9: (221541, 1519125536),
                10: (293455, 2123645248), 11: (26535, 195366784), 12: (1, 1920)}
INPUTS = [0x0000ffff, 0x00ff00ff, 0x0f0f0f0f, 0x33333333, 0x55555555]   # optimal5's x1..x5
FULL = 0xffffffff


def parse(path):
    """Dict: truth table (32-bit, bit t = value on row t) -> (number of gates, chain)."""
    data = open(path, "rb").read()
    assert len(data) % 15 == 0
    table = {}
    for off in range(0, len(data), 15):
        b = data[off:off + 15]
        g = []
        for i in range(3):
            x = int.from_bytes(b[5 * i:5 * i + 5], "little")
            g += [(x >> s) & 1023 for s in (0, 10, 20, 30)]
        calcs = [0] + INPUTS
        chain = []
        for gi in g:
            if gi == 0:
                break
            op = "&|^\\"[gi >> 8]
            i1, i2 = (gi & 15) + 1, ((gi >> 4) & 15) + 1
            a, c = calcs[i1], calcs[i2]
            val = {"&": a & c, "|": a | c, "^": a ^ c, "\\": a & ~c & FULL}[op]
            calcs.append(val)
            chain.append((i1, op, i2))
        w = calcs[-1]
        assert w not in table, "two records for one function"
        table[w] = (len(chain), chain)
    return table, hashlib.sha256(data).hexdigest()


_MAPS = [[sum((((t >> perm[j]) & 1) ^ ((neg >> j) & 1)) << j for j in range(5)) for t in range(32)]
         for perm in itertools.permutations(range(5)) for neg in range(32)]


def npn_orbit(tt32):
    """All 7,680 images of a 5-input truth table under permuting/negating inputs and negating the output."""
    out = set()
    for src in _MAPS:
        y = 0
        for t in range(32):
            y |= ((tt32 >> src[t]) & 1) << t
        out.add(y)
        out.add(y ^ FULL)
    return out


def tt32_of(n, tt):
    """Truth table of an n-input function as a 5-input function ignoring x_{n+1}..x_5."""
    return sum(tt[t & ((1 << n) - 1)] << t for t in range(32))


def lookup(table, n, tt):
    hits = npn_orbit(tt32_of(n, tt)) & table.keys()
    if not hits:
        return None, None
    assert len(hits) == 1, "class found twice"
    w = hits.pop()
    return table[w][0], w


def main(path):
    table, digest = parse(path)
    dist = {}
    for cnt, _ in table.values():
        dist[cnt] = dist.get(cnt, 0) + 1
    dist[0] = dist.get(0, 0) + 2              # constant 0 and x1 are not stored
    dist = dict(sorted(dist.items()))
    table2_ok = all(dist.get(c) == KNUTH_TABLE2[c][0] for c in KNUTH_TABLE2) and len(dist) == len(KNUTH_TABLE2)
    print(f"{len(table)} stored classes; classes per cost {dist}; equals Knuth's Table 2: {table2_ok}")
    readme_example = lookup(table, 5, [(0x169ae443 >> t) & 1 for t in range(32)])[0]
    print("optimal5 README example 0x169ae443 needs", readme_example, "gates (README shows 12)")
    rows = []
    for name, n, fn, bases in E.explicit_suite():
        tt = E.tt_from_fn(n, fn)
        cost, rep = lookup(table, n, tt)
        rows.append({"name": name, "n": n, "knuth_B2_cost": cost, "class_representative": hex(rep) if rep is not None else None})
        print(f"  {name:28s} n={n}: Knuth/optimal5 B2 cost {cost}")
    # all 222 NPN classes of 4-input functions, against the first run (results/n4_exact_costs.json)
    n4 = json.load(open(os.path.join(R, "n4_exact_costs.json")))["classes"]
    n4_mismatch, n4_dist = [], {}
    for c in n4:
        cost, _ = lookup(table, 4, E.int_to_tt(c["canonical"], 4))
        cost = 0 if cost is None else cost          # constants and literals are not stored
        n4_dist[cost] = n4_dist.get(cost, 0) + c["size"]
        if cost != c["cost_B2"]:
            n4_mismatch.append((hex(c["canonical"]), c["cost_B2"], cost))
    n4_dist = dict(sorted(n4_dist.items()))
    print(f"n=4: {len(n4)} classes compared, {len(n4_mismatch)} disagreements; distribution from Knuth's chains {n4_dist}")
    out = {"source": "https://gitlab.com/apgoucher/optimal5 knuthies.dat (Knuth's optimal 5-input chains)",
           "knuthies_sha256": digest, "classes_per_cost": dist, "matches_knuth_table2": table2_ok,
           "readme_example_0x169ae443": readme_example, "functions": rows,
           "n4_classes_compared": len(n4), "n4_disagreements": n4_mismatch, "n4_distribution_from_optimal5": n4_dist}
    json.dump(out, open(os.path.join(R, "optimal5_comparison.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    main(sys.argv[1])
