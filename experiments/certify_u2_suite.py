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
       python3 certify_u2_suite.py --upper-from-b2 NAME | --upper RECORD.json   (record a verified upper bound)
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
    name, proofs, budget, kmax, kmin = args
    full, n, tt = C.suite_function(name)
    per_k, lower, t0 = [], kmin, time.time()      # with kmin > 1, k < kmin must be certified by another run
    for k in range(kmin, kmax + 1):
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
            return {"name": full, "n": n, "basis": "U2", "kmin": kmin, "lower": lower, "upper": k, "exact": lower == k,
                    "label": ("Machine-checked" if certified else "Numerical") if lower == k else "Open",
                    "circuit": E.gates_to_str(n, gates), "gates": [list(g[:3]) + [list(g[3])] for g in gates],
                    "per_k": per_k, "seconds": round(time.time() - t0, 1)}
        if res is False and lower == k:
            lower = k + 1
    return {"name": full, "n": n, "basis": "U2", "kmin": kmin, "lower": lower, "upper": None, "exact": False, "label": "Open",
            "per_k": per_k, "seconds": round(time.time() - t0, 1)}


def main(a):
    global OUT
    OUT = a.out or OUT
    names = a.only.split(",") if a.only else TARGETS
    done = json.load(open(OUT)) if os.path.exists(OUT) else []
    if a.proofs:
        os.makedirs(a.proofs, exist_ok=True)
    jobs = [(nm, a.proofs, a.budget, a.kmax, a.kmin) for nm in names]
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


def xor_expanded_b2(name):
    """A U2 circuit from the B2-optimal circuit in results/explicit_final.json: each XOR(a,b) becomes
    OR(a AND NOT b, NOT a AND b), three U2 gates. Returns verified gates."""
    full, n, tt = C.suite_function(name)
    fin = {(e["name"], e["basis"]): e for e in json.load(open(os.path.join(R, "explicit_final.json")))["functions"]}
    remap, out, nxt = {i: i for i in range(n)}, [], n
    for (i, j, l, op) in [(g[0], g[1], g[2], tuple(g[3])) for g in fin[(full, "B2")]["gates"]]:
        a, b = remap[j], remap[l]
        if op == (0, 1, 1, 0):
            out += [(nxt, a, b, (0, 0, 1, 0)), (nxt + 1, a, b, (0, 1, 0, 0)), (nxt + 2, nxt, nxt + 1, (0, 1, 1, 1))]
            remap[i], nxt = nxt + 2, nxt + 3
        else:
            out.append((nxt, a, b, op))
            remap[i], nxt = nxt, nxt + 1
    assert E.verify(n, tt, out) and all(g[3] != (0, 1, 1, 0) for g in out)
    return out


def prune(n, gates):
    """Drop gates the output (last gate) does not depend on, and renumber the rest."""
    by_id = {g[0]: g for g in gates}
    live, stack = set(), [gates[-1][0]]
    while stack:
        i = stack.pop()
        if i >= n and i not in live:
            live.add(i)
            stack += [by_id[i][1], by_id[i][2]]
    kept = [g for g in gates if g[0] in live]
    new_id = {i: i for i in range(n)}
    for pos, g in enumerate(kept):
        new_id[g[0]] = n + pos
    return [(new_id[i], new_id[j], new_id[l], op) for (i, j, l, op) in kept]


def record_upper(name, gates, source):
    """Attach a verified U2 circuit as the upper bound of an entry if it improves on the current one."""
    full, n, tt = C.suite_function(name)
    gates = prune(n, [(g[0], g[1], g[2], tuple(g[3])) for g in gates])
    assert E.verify(n, tt, gates) and all(g[3] != (0, 1, 1, 0) for g in gates), "not a U2 circuit for " + full
    done = json.load(open(OUT))
    rec = [d for d in done if d["name"] == full][0]
    if rec["upper"] is not None and rec["upper"] <= len(gates):
        print(f"{full}: keeping upper bound {rec['upper']} (offered {len(gates)})")
        return
    rec.update(upper=len(gates), circuit=E.gates_to_str(n, gates), upper_source=source,
               gates=[list(g[:3]) + [list(g[3])] for g in gates])
    rec["exact"] = rec["lower"] == rec["upper"]
    json.dump(done, open(OUT, "w"), indent=1)
    print(f"{full}: U2 cost in [{rec['lower']}, {rec['upper']}] ({source})")


def table():
    """Markdown table of results/u2_suite.json next to the B2 costs of results/explicit_final.json."""
    b2 = {e["name"]: e["upper"] for e in json.load(open(os.path.join(R, "explicit_final.json")))["functions"]
          if e["basis"] == "B2"}
    order = {nm: i for i, nm in enumerate(TARGETS)}
    rows = sorted(json.load(open(OUT)), key=lambda d: (d["n"], order.get(d["name"].split(" (")[0], 99)))
    print("| function | n | B2 cost | U2 cost | label |")
    print("|---|---|---|---|---|")
    for d in rows:
        if d["exact"]:
            u2, label = str(d["upper"]), d["label"]
        else:
            u2 = f"≥ {d['lower']}" if d["upper"] is None else f"[{d['lower']}, {d['upper']}]"
            label = "Open; lower bound Machine-checked" if d.get("lower_bound_machine_checked") else "Open"
        print(f"| {d['name']} | {d['n']} | {b2.get(d['name'], '—')} | {u2} | {label} |")


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--table"]:
        table()
        sys.exit()
    if len(sys.argv) == 3 and sys.argv[1] == "--upper-from-b2":
        record_upper(sys.argv[2], xor_expanded_b2(sys.argv[2]), "XOR expansion of the B2-optimal circuit")
        sys.exit()
    if len(sys.argv) == 3 and sys.argv[1] == "--upper":        # a record written by upper_bound_search.py --out
        r = json.load(open(sys.argv[2]))
        assert r["basis"] == "U2" and r["result"] is True
        record_upper(r["name"], r["gates"], f"upper_bound_search.py at k = {r['k']} ({r['solver']})")
        sys.exit()
    ap = argparse.ArgumentParser()
    ap.add_argument("--proofs")
    ap.add_argument("--budget", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only")
    ap.add_argument("--kmax", type=int, default=16)
    ap.add_argument("--kmin", type=int, default=1, help="start at this k (smaller k certified elsewhere)")
    ap.add_argument("--out", help="results file (default results/u2_suite.json)")
    main(ap.parse_args())
