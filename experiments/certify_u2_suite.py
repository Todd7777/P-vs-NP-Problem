#!/usr/bin/env python3
"""
certify_u2_suite.py -- U2 costs of the explicit functions that so far have only a B2 cost.

The explicit suite (exact_circuit_complexity.explicit_suite) computes U2 costs only for parity and
MOD3_4. This script runs circuit_sat.py in U2 for the other functions: for k = 1, 2, ... until the
CNF is SAT. With --proofs, every UNSAT k gets a binary DRAT proof that drat-trim checks (the value
is then Machine-checked); without it the run is exploratory (solver answers only, Numerical). A
conflict budget per call (--budget) turns an unresolved k into an interval instead of a hang.
Functions run in parallel, one process each; results go to results/u2_suite.json as they finish.

Usage: python3 certify_u2_suite.py [--proofs DIR] [--budget CONFLICTS] [--workers 4] [--only NAME,...]
       python3 certify_u2_suite.py --table        (Markdown table of the recorded results)
"""
import argparse, json, os, re, time
from multiprocessing import Pool

import circuit_sat as C
import exact_circuit_complexity as E

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
OUT = os.path.join(R, "u2_suite.json")
TARGETS = ["ADD2 carry-out", "MUL2 bit3", "MUL2 bit2", "MUL2 bit1", "MAJ_3 xor x4 xor x5",
           "MAJ_5", "EXACTLY2_5", "THR2_5", "MOD3_5"]


def tag_for(name, k):
    """File stem for the CNF/proof of one instance. Must be unique per (function, k): functions that
    share a first word (MUL2 bit1/bit2/bit3) once collided here and overwrote each other's files."""
    return "u2suite_" + re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") + f"_k{k}"


def run_one(args):
    name, proofs, budget, kmax = args
    full, n, tt = C.suite_function(name)
    per_k, lower, t0 = [], 1, time.time()
    for k in range(1, kmax + 1):
        enc = C.Encoding(n, tt, k, "U2")
        if proofs:
            rec = C.certify(enc, proofs, tag_for(full, k), budget=budget)
            res = rec["result"]
            step = {"k": k, "result": res, "solve_seconds": rec["solve_seconds"], "cnf_sha256": rec["cnf_sha256"]}
            if res is False:
                step.update(proof_sha256=rec["proof_sha256"], proof_bytes=rec["proof_bytes"],
                            drat_trim_verified=rec["drat_trim"]["verified"], drat_trim_seconds=rec["drat_trim"]["seconds"])
            gates = rec.get("gates")
        else:
            r = C.run_solver(enc, budget=budget)
            res, step = r["result"], {"k": k, "result": r["result"], "solve_seconds": r["seconds"],
                                      "conflicts": r["stats"].get("conflicts")}
            gates = enc.decode(r["model"]) if res is True else None
        per_k.append(step)
        print(f"  {full:24s} U2 k={k:2d}: {res} ({step['solve_seconds']}s"
              + (f", drat-trim {step.get('drat_trim_verified')} {step.get('drat_trim_seconds')}s" if 'drat_trim_verified' in step else "")
              + ")", flush=True)
        if res is True:
            assert E.verify(n, tt, gates), "decoded circuit does not compute the target"
            certified = bool(proofs) and all(s.get("drat_trim_verified") for s in per_k if s["result"] is False)
            return {"name": full, "n": n, "basis": "U2", "lower": lower, "upper": k, "exact": lower == k,
                    "label": ("Machine-checked" if certified else "Numerical") if lower == k else "Open",
                    "circuit": E.gates_to_str(n, gates), "gates": [list(g[:3]) + [list(g[3])] for g in gates],
                    "per_k": per_k, "seconds": round(time.time() - t0, 1)}
        if res is False and lower == k:
            lower = k + 1
    return {"name": full, "n": n, "basis": "U2", "lower": lower, "upper": None, "exact": False, "label": "Open",
            "per_k": per_k, "seconds": round(time.time() - t0, 1)}


def main(a):
    names = a.only.split(",") if a.only else TARGETS
    done = json.load(open(OUT)) if os.path.exists(OUT) else []
    if a.proofs:
        os.makedirs(a.proofs, exist_ok=True)
    jobs = [(nm, a.proofs, a.budget, a.kmax) for nm in names]
    with Pool(a.workers, maxtasksperchild=1) as pool:
        for rec in pool.imap_unordered(run_one, jobs):
            done = json.load(open(OUT)) if os.path.exists(OUT) else []     # re-read: another run may have written
            old = [d for d in done if d["name"] == rec["name"]]
            if old and old[0].get("label") == "Machine-checked" and rec["label"] != "Machine-checked":
                print(f"keeping the certified record for {rec['name']}", flush=True)
                continue                                             # never replace a certified record
            done = [d for d in done if d["name"] != rec["name"]] + [rec]
            json.dump(sorted(done, key=lambda d: (d["n"], d["name"])), open(OUT, "w"), indent=1)
            rng = f"= {rec['upper']}" if rec["exact"] else f"in [{rec['lower']}, {rec['upper']}]"
            print(f"{rec['name']:24s} U2 cost {rng} ({rec['label']}, {rec['seconds']}s)", flush=True)


def table():
    """Markdown table of results/u2_suite.json next to the B2 costs of results/explicit_final.json."""
    b2 = {e["name"]: e["upper"] for e in json.load(open(os.path.join(R, "explicit_final.json")))["functions"]
          if e["basis"] == "B2"}
    order = {nm: i for i, nm in enumerate(TARGETS)}
    rows = sorted(json.load(open(OUT)), key=lambda d: (d["n"], order.get(d["name"].split(" (")[0], 99)))
    print("| function | n | B2 cost | U2 cost | label |")
    print("|---|---|---|---|---|")
    for d in rows:
        u2 = str(d["upper"]) if d["exact"] else f"[{d['lower']}, {d['upper']}]"
        print(f"| {d['name']} | {d['n']} | {b2.get(d['name'], '—')} | {u2} | {d['label']} |")


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--table"]:
        table()
        sys.exit()
    ap = argparse.ArgumentParser()
    ap.add_argument("--proofs")
    ap.add_argument("--budget", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only")
    ap.add_argument("--kmax", type=int, default=16)
    main(ap.parse_args())
