"""Close the U2 intervals left open by the n=4 run of exact_circuit_complexity.py.

The first run (results/n4_exact_costs.json) used a 400,000-conflict budget per SAT call and left
43 NPN classes with U2 cost only bracketed: each has a proven lower bound of 8 (every k <= 7 was
refuted) and an upper bound in 9..12 from a verified circuit. This script resumes each such class at
its proven lower bound, with a much larger budget per call, and writes the outcome to
results/n4_u2_closure.json together with the resulting U2 cost distribution over all 65,536
functions of 4 variables (exact where every class is resolved).

Same model and encoding as the main script: Knuth's normal-chain convention (a circuit for f or
for its complement; constants and literals are free), gates from U2 = B2 minus {XOR, XNOR}.

Usage:  python3 close_u2_n4.py [workers] [conflict_budget]
"""
import json, sys, time
from multiprocessing import Pool
from pysat.solvers import Solver
import exact_circuit_complexity as E

def close_one(args):
    canon, size, lower, upper, budget = args
    tt = E.normalize(E.int_to_tt(canon, 4))
    sym = E.depends_on_all(4, tt)
    per_k, circuit, t_start = {}, None, time.time()
    k = lower
    while k < upper:
        cls, decode = E.encode(4, tt, k, basis="U2", symmetry=sym)
        t0 = time.time()
        with Solver(name=E.SOLVER, bootstrap_with=cls) as S:
            S.conf_budget(budget)
            res = S.solve_limited()
            per_k[k] = {"result": res, "seconds": round(time.time() - t0, 1), "clauses": len(cls)}
            if res is True:
                gates = decode(S.get_model())
                assert E.verify(4, tt, gates), "decoded circuit does not compute target"
                circuit, upper = E.gates_to_str(4, gates), k
                break
        if res is False and lower == k:
            lower = k + 1            # contiguous refuted prefix: proven lower bound
            k += 1
            continue
        break                        # budget exhausted: leave the interval as it is
    return {"canonical": canon, "size": size, "U2_lower": lower, "U2_upper": upper,
            "U2_status": "exact" if lower == upper else "interval",
            "circuit_U2_new": circuit, "per_k": per_k, "seconds": round(time.time() - t_start, 1)}

def describe(r):
    cost = f"= {r['U2_upper']}" if r["U2_status"] == "exact" else f"in [{r['U2_lower']}, {r['U2_upper']}]"
    steps = ", ".join(f"k={k}: {v['result']} ({v['seconds']}s)" for k, v in r["per_k"].items())
    return f"class {r['canonical']:#06x} (size {r['size']}): U2 {cost}; {steps}"

def main(workers=3, budget=50_000_000):
    base = json.load(open("results/n4_exact_costs.json"))
    open_classes = [c for c in base["classes"] if c["U2_status"] != "exact"]
    print(f"{len(open_classes)} open classes covering {sum(c['size'] for c in open_classes)} functions; "
          f"budget {budget} conflicts per call; {workers} workers", flush=True)
    jobs = sorted(((c["canonical"], c["size"], c["U2_lower"], c["U2_upper"], budget) for c in open_classes),
                  key=lambda j: j[3] - j[2])
    t0, out = time.time(), []
    with Pool(workers) as pool:
        for r in pool.imap_unordered(close_one, jobs):
            out.append(r)
            with open("results/n4_u2_closure_progress.jsonl", "a") as fh:   # survives an early stop
                fh.write(json.dumps(r) + "\n")
            print(f"  [{len(out)}/{len(jobs)}] {describe(r)}  t={time.time() - t0:.0f}s", flush=True)
    closed = {r["canonical"]: r for r in out}
    dist, unresolved = {}, []
    for c in base["classes"]:
        r = closed.get(c["canonical"])
        lo, hi, st = (r["U2_lower"], r["U2_upper"], r["U2_status"]) if r else (c["U2_lower"], c["U2_upper"], c["U2_status"])
        if st == "exact":
            dist[lo] = dist.get(lo, 0) + c["size"]
        else:
            unresolved.append({"canonical": c["canonical"], "size": c["size"], "lower": lo, "upper": hi})
    result = {"budget_conflicts_per_call": budget, "seconds": round(time.time() - t0, 1),
              "closed": sorted(out, key=lambda r: r["canonical"]),
              "distribution_U2_exact_part": {int(k): v for k, v in sorted(dist.items())},
              "functions_with_exact_U2": sum(dist.values()),
              "unresolved": unresolved}
    json.dump(result, open("results/n4_u2_closure.json", "w"), indent=1)
    print(f"done in {time.time()-t0:.0f}s; exact U2 known for {sum(dist.values())}/65536 functions; "
          f"{len(unresolved)} classes still open", flush=True)
    print("U2 distribution (exact part):", result["distribution_U2_exact_part"], flush=True)

if __name__ == "__main__":
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 50_000_000
    main(w, b)
