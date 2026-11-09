#!/usr/bin/env python3
"""
certify_costs.py -- certified exact costs for the explicit functions of exact_circuit_complexity.py.

For a function f with best known upper bound U (a verified circuit), the driver runs the
symmetry-reduced encoding of circuit_sat.py at every k = 1..U:
  * k < U: the CNF must be UNSAT. CaDiCaL writes a binary DRAT proof, drat-trim checks it against
    the exact CNF file, and the record keeps the SHA-256 of both files;
  * k = U: the CNF must be SAT; the decoded circuit is re-evaluated on the full truth table.
If some k < U turns out SAT, that k is the new upper bound and larger k are not needed.
Jobs run in parallel (one solver per process). Records are appended to a progress file as they
finish, so an interrupted run can be resumed; `summarize` writes results/certificates.json.

Usage:
  python3 certify_costs.py run --proofs DIR [--workers 4] [--only NAME[,NAME]] [--kmin K] [--kmax K]
                                [--skip NAME:BASIS:K[,...]]
  python3 certify_costs.py summarize
"""
import argparse, json, os, sys, time
from multiprocessing import Pool

import circuit_sat as C
import exact_circuit_complexity as E

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
PROGRESS = os.path.join(R, "certificates_progress.jsonl")
FINAL = os.path.join(R, "certificates.json")

# Best upper bounds known before this run (verified circuits in results/explicit_costs.json).
# parity_5 in U2 is settled by Schnorr's theorem (docs/05 §5.2) and is not run here.
TARGETS = [
    ("parity_2", "B2", 1), ("parity_2", "U2", 3), ("parity_3", "B2", 2), ("parity_3", "U2", 6),
    ("parity_4", "B2", 3), ("parity_4", "U2", 9), ("parity_5", "B2", 4),
    ("MAJ_5", "B2", 10), ("MOD3_5", "B2", 10), ("MOD3_4", "B2", 7), ("MOD3_4", "U2", 10),
    ("EXACTLY2_5", "B2", 9), ("THR2_5", "B2", 10), ("MAJ_3 xor x4 xor x5", "B2", 6),
    ("ADD2 carry-out", "B2", 5), ("MUL2 bit3", "B2", 3), ("MUL2 bit2", "B2", 3), ("MUL2 bit1", "B2", 3),
]


def short(name):
    return name.split(" ")[0] if name.split(" ")[0] not in ("MUL2", "MAJ_3", "ADD2") else name.replace(" ", "_")


def job(args):
    name, basis, k, proofs = args
    full, n, tt = C.suite_function(name)
    enc = C.Encoding(n, tt, k, basis)
    rec = C.certify(enc, proofs, f"{short(full)}_{basis}_k{k}")
    rec["name"], rec["basis"] = full, basis
    gates = rec.pop("gates", None)
    if gates is not None:
        rec["gates"] = [list(g[:3]) + [list(g[3])] for g in gates]
    return rec


def load_progress():
    recs = {}
    if os.path.exists(PROGRESS):
        for line in open(PROGRESS):
            r = json.loads(line)
            recs[(r["name"], r["basis"], r["k"])] = r
    return recs


def done_ok(r):
    if r["result"] is True:
        return True
    return r["result"] is False and r.get("drat_trim", {}).get("verified") is True


def run(a):
    os.makedirs(a.proofs, exist_ok=True)
    have = load_progress()
    only = set(a.only.split(",")) if a.only else None
    skip = set(tuple(x.rsplit(":", 2)) for x in a.skip.split(",")) if a.skip else set()
    jobs = []
    for name, basis, U in TARGETS:
        full = C.suite_function(name)[0]
        if only and name not in only and full not in only:
            continue
        sat = [k for (nm, b, k), r in have.items() if nm == full and b == basis and r["result"] is True]
        U = min([U] + sat)                               # never go past a k already shown SAT
        for k in range(max(1, a.kmin), min(U, a.kmax) + 1):
            r = have.get((full, basis, k))
            if (r and done_ok(r)) or (name, basis, str(k)) in skip:
                continue
            jobs.append((name, basis, k, a.proofs))
    jobs.sort(key=lambda j: -j[2])                      # hardest (largest k) first
    print(f"{len(jobs)} jobs, {a.workers} workers", flush=True)
    t0 = time.time()
    with Pool(a.workers, maxtasksperchild=1) as pool:
        for rec in pool.imap_unordered(job, jobs):
            with open(PROGRESS, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            chk = rec.get("drat_trim", {})
            print(f"[{time.time() - t0:7.0f}s] {rec['name']:24s} {rec['basis']} k={rec['k']:2d}: {rec['result']} "
                  f"solve {rec['solve_seconds']}s" + (f", proof {rec['proof_bytes'] / 1e6:.1f} MB, drat-trim "
                  f"{'VERIFIED' if chk.get('verified') else chk.get('verified')} {chk.get('seconds')}s"
                  if rec["result"] is False else "") + (f"  {rec.get('circuit', '')}" if rec["result"] else ""),
                  flush=True)


def summarize():
    recs = load_progress()
    out = []
    for name, basis, U in TARGETS:
        full = C.suite_function(name)[0]
        ks = sorted(k for (nm, b, k) in recs if nm == full and b == basis)
        sat = [k for k in ks if recs[(full, basis, k)]["result"] is True]
        cost = min(sat) if sat else None
        lower = 1
        while (full, basis, lower) in recs and recs[(full, basis, lower)]["result"] is False:
            lower += 1                                   # contiguous refuted prefix 1..lower-1
        verified = all(recs[(full, basis, k)].get("drat_trim", {}).get("verified") is True for k in range(1, lower))
        entry = {"name": full, "basis": basis, "lower": lower, "upper": cost,
                 "exact": cost is not None and lower == cost, "all_refutations_drat_verified": verified,
                 "circuit": recs[(full, basis, cost)]["circuit"] if cost else None,
                 "refutations": [{k2: recs[(full, basis, k)].get(k2) for k2 in
                                  ("k", "nvars", "nclauses", "cnf_sha256", "solver", "solve_seconds", "stats",
                                   "proof_bytes", "proof_sha256")} | {"drat_trim_verified":
                                  recs[(full, basis, k)].get("drat_trim", {}).get("verified"),
                                  "drat_trim_seconds": recs[(full, basis, k)].get("drat_trim", {}).get("seconds")}
                                 for k in range(1, lower)]}
        out.append(entry)
        print(f"{full:24s} {basis}: [{lower}, {cost}] exact={entry['exact']} drat-verified={verified}")
    json.dump({"rules": C.DEFAULT_RULES, "encoding": "circuit_sat.py", "results": out}, open(FINAL, "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "summarize"])
    ap.add_argument("--proofs", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "proofs"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only")
    ap.add_argument("--kmin", type=int, default=1)
    ap.add_argument("--kmax", type=int, default=99)
    ap.add_argument("--skip", default="", help="comma-separated NAME:BASIS:K jobs to leave out")
    a = ap.parse_args()
    run(a) if a.cmd == "run" else summarize()
