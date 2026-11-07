"""Combine the n=4 U2 results into one distribution.

Sources (all in results/): n4_exact_costs.json (first run, 400k-conflict budget),
n4_u2_closure.json or n4_u2_closure_progress.jsonl (closure run, 50M budget per call), and
n4_u2_closure_k8.json (8-gate refutations for the classes the closure run had not finished), and
explicit_costs.json (the 4-input U2 entries of the explicit-function run, mapped to their NPN class;
U2 cost is invariant under permuting and negating inputs and under complementing the output).
Prints the exact part of the U2 cost distribution over all 65,536 functions of 4 variables and
the classes that are still only bracketed, and writes results/n4_u2_summary.json.
"""
import json, os, collections, itertools
import exact_circuit_complexity as E

def npn_min(x, n=4):
    """Smallest truth-table integer in the NPN orbit of x (the canonical form used by npn_classes)."""
    best = None
    for perm in itertools.permutations(range(n)):
        for neg in range(1 << n):
            for oneg in (0, 1):
                y = 0
                for t in range(1 << n):
                    src = sum((((t >> perm[j]) & 1) ^ ((neg >> j) & 1)) << j for j in range(n))
                    y |= (((x >> src) & 1) ^ oneg) << t
                best = y if best is None or y < best else best
    return best
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
base = json.load(open(os.path.join(R, "n4_exact_costs.json")))
closed = {}
final = os.path.join(R, "n4_u2_closure.json")
if os.path.exists(final):
    for r in json.load(open(final))["closed"]:
        closed[r["canonical"]] = r
else:
    for line in open(os.path.join(R, "n4_u2_closure_progress.jsonl")):
        r = json.loads(line); closed[r["canonical"]] = r
k8 = {}
k8f = os.path.join(R, "n4_u2_closure_k8.json")
if os.path.exists(k8f):
    for r in json.load(open(k8f)):
        k8[r["canonical"]] = r
explicit = {}   # canonical -> (lower, upper) from the explicit-function run, U2, n=4
ex_file = os.path.join(R, "explicit_costs.json")
if os.path.exists(ex_file):
    fns = {name: fn for name, n, fn, _ in E.explicit_suite() if n == 4}
    for e in json.load(open(ex_file)):
        if e["n"] == 4 and e["basis"] == "U2" and e["name"] in fns:
            tt = sum(int(bool(fns[e["name"]]([(t >> j) & 1 for j in range(4)]))) << t for t in range(16))
            explicit[npn_min(tt)] = (e["lower"], e["upper"], e["name"])
dist, open_classes = collections.Counter(), []
for c in base["classes"]:
    lo, hi, st = c["U2_lower"], c["U2_upper"], c["U2_status"]
    r = closed.get(c["canonical"])
    if r:
        lo, hi, st = r["U2_lower"], r["U2_upper"], r["U2_status"]
    if st != "exact":
        x = k8.get(c["canonical"])
        if x and x["result"] is False and lo <= 8:
            lo = 9
        if x and x["result"] is True:
            hi = min(hi, 8)
        ex = explicit.get(c["canonical"])
        if ex:
            lo, hi = max(lo, ex[0]), min(hi, ex[1])
        st = "exact" if lo == hi else "interval"
    if st == "exact":
        dist[lo] += c["size"]
    else:
        open_classes.append({"canonical": hex(c["canonical"]), "size": c["size"], "cost_B2": c["cost_B2"], "U2_lower": lo, "U2_upper": hi})
summary = {"distribution_U2_exact_part": {int(k): v for k, v in sorted(dist.items())},
           "functions_exact": sum(dist.values()), "functions_total": 65536,
           "open_classes": open_classes, "functions_open": sum(o["size"] for o in open_classes),
           "max_exact": max(dist), "distribution_B2": base["distribution_B2"]}
json.dump(summary, open(os.path.join(R, "n4_u2_summary.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))
