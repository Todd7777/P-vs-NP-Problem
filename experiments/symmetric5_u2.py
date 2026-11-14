#!/usr/bin/env python3
"""
symmetric5_u2.py -- U2 costs of the symmetric Boolean functions of 5 inputs, one per class.

A symmetric function of 5 inputs is given by its values b_0..b_5 on inputs of weight 0..5 and is
named SYM5:<b_0...b_5> (circuit_sat.suite_function). Negating the output, or every input (weight
w -> 5 - w), does not change the cost (negations are free), so the 62 nonconstant functions fall
into 19 classes; each is represented by its smallest vector with b_0 = 0.

For each class the record combines:
  - lower bounds. (1) Lemma 5(a) of ENCODING.md: every circuit for f reads each input, so
    C(f) >= C(f|x_v=c) + 1, with the 4-input restriction costs Machine-checked in
    results/restriction_costs.json (certify_restrictions.py). (2) Refutations of larger k, each with
    a drat-trim-verified proof, in results/symmetric5_refutations.json (certify_u2_suite.py --only
    SYM5:... --proofs ... --out results/symmetric5_refutations.json) or results/cube_certificates.json
    (certify_cubes.py, with or without --elim), accepted only in increasing k from (1). (3) For a class that contains an
    explicit-suite function, the value already recorded in results/u2_suite.json or
    results/explicit_final.json.
  - upper bounds: verified circuits (results/symmetric5_upper.json, from the XOR expansion of a B2
    circuit at Knuth's B2 cost followed by local_improve.py, or from the suite records).
  - the B2 cost of the class from Knuth's optimal 5-input chains (optimal5; see compare_optimal5.py),
    stored in results/symmetric5_upper.json with the hash of knuthies.dat.
Every circuit is re-evaluated here. Writes results/symmetric5_u2.json; --table prints the table.

Usage: python3 symmetric5_u2.py [--table]            (assemble results/symmetric5_u2.json)
       python3 symmetric5_u2.py --knuth PATH/knuthies.dat   (B2 costs from optimal5)
       python3 symmetric5_u2.py --upper V1,V2,... [MINUTES]  (upper bounds; keeps the best circuit)
"""
import json, os, sys

import circuit_sat as C
import elimination as EL
import exact_circuit_complexity as E

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
OUT = os.path.join(R, "symmetric5_u2.json")
REFS = os.path.join(R, "symmetric5_refutations.json")     # certify_u2_suite.py --only SYM5:... --out
SUITE = {"010101": "parity_5", "000111": "MAJ_5", "000011": "THR2_5", "000100": "EXACTLY2_5", "001001": "MOD3_5"}
SUITE_VECTOR = {"parity_5": "010101", "MAJ_5": "000111", "THR2_5": "001111", "EXACTLY2_5": "001000", "MOD3_5": "100100"}


def negate_inputs(n, gates):
    """A chain computing f(not x_1, ..., not x_n) from one computing f: every gate that reads an input
    reads its negation instead (absorbed into the operator), then the chain is renormalized."""
    import local_improve as L
    G = {}
    for (i, j, l, tt) in gates:
        tt = tuple(tt)
        if j < n:
            tt = (tt[2], tt[3], tt[0], tt[1])
        if l < n:
            tt = (tt[1], tt[0], tt[3], tt[2])
        G[i] = [j, l, tt]
    return L.to_chain(n, G, gates[-1][0], 0)


def members(v):
    out = set()
    for w in (v, v[::-1]):
        for x in (w, "".join("1" if b == "0" else "0" for b in w)):
            out.add(x)
    return sorted(out)


def classes():
    reps = set()
    for m in range(64):
        v = "".join(str((m >> s) & 1) for s in range(6))
        if "1" in v and "0" in v:
            reps.add(min(x for x in members(v) if x[0] == "0"))
    return sorted(reps)


def suite_record(v):
    """(lower, upper, label, source, gates) for a class that contains an explicit-suite function; the
    gates are turned into a circuit for the representative v (negating every input if needed)."""
    name = SUITE.get(v)
    if name is None:
        return None
    full = C.suite_function(name)[0]
    found = None
    for d in json.load(open(os.path.join(R, "u2_suite.json"))):
        if d["name"] == full:
            found = d["lower"], d["upper"], d["label"], "results/u2_suite.json", d["gates"]
    for d in json.load(open(os.path.join(R, "explicit_final.json")))["functions"]:
        if found is None and d["name"] == full and d["basis"] == "U2":
            found = d["lower"], d["upper"], d["label"], "results/explicit_final.json", d["gates"]
    if found is None:
        return None
    gates = [(g[0], g[1], g[2], tuple(g[3])) for g in found[4]]
    sv = SUITE_VECTOR[name]
    if v not in (sv, "".join("1" if b == "0" else "0" for b in sv)):      # v is the mirror image
        gates = negate_inputs(5, gates)
    return found[:4] + (gates,)


def build():
    upper = {u["v"]: u for u in load_upper()["classes"]}
    certs = json.load(open(os.path.join(R, "cube_certificates.json")))
    refs = {d["name"]: d for d in json.load(open(REFS))} if os.path.exists(REFS) else {}
    rows = []
    for v in classes():
        full, n, tt = C.suite_function("SYM5:" + v)
        weights = [w for w in range(6) if v[w] == "1"]
        rec = {"class": v, "true_on_weights": weights, "members": members(v),
               "b2_knuth": load_upper()["b2_knuth"][v]}
        known = suite_record(v)
        if v == "000001":                                    # AND of 5 inputs: 4 gates, and n - 1 are needed
            rec.update(lower=4, upper=4, label="Theorem", lower_source="a circuit reading 5 inputs needs 4 gates")
            gates = [[5, 0, 1, [0, 0, 0, 1]], [6, 2, 5, [0, 0, 0, 1]], [7, 3, 6, [0, 0, 0, 1]], [8, 4, 7, [0, 0, 0, 1]]]
        else:
            L, used = EL.certified_bounds(n, tt)
            lower = max(max(row) for row in L) + 1
            rec["restriction_costs"] = used
            rec["lower_from_restrictions"] = lower
            src = ["Lemma 5(a) with the restriction costs in results/restriction_costs.json"]
            ref = refs.get(full, {})
            plain = {st["k"] for st in ref.get("per_k", []) if st["result"] is False and st.get("drat_trim_verified")}
            for k in range(lower, 20):                       # raise by certified refutations, in order
                ok = [c for c in certs if c["name"] == full and c["basis"] == "U2" and c["k"] == k
                      and c["all_unsat_and_verified"]]
                if k in plain:
                    src.append(f"k = {k}: results/symmetric5_refutations.json")
                elif ok:
                    src.append(f"k = {k}: results/cube_certificates.json"
                               + (f" (elimination level {ok[0]['elimination'].get('level', 1)})" if "elimination" in ok[0] else ""))
                else:
                    break
                lower = k + 1
            gates = upper[v]["gates"] if v in upper else None
            if ref.get("upper") == lower and ref.get("gates"):  # a circuit at the lower bound: exact
                gates = ref["gates"]
            if known:                                        # the suite records may be stronger
                kl, ku, klabel, ksrc, kgates = known
                if kl > lower:
                    lower, src = kl, [ksrc]
                if ku is not None and (gates is None or ku < len(gates)):
                    gates = kgates
            rec.update(lower=lower, lower_source="; ".join(src))
            rec["upper"] = len(gates)
            rec["label"] = "Machine-checked" if rec["lower"] == rec["upper"] else "Open"
            if known and known[2] == "Theorem" and known[0] == rec["upper"]:
                rec["label"] = "Theorem"
        g = [(x[0], x[1], x[2], tuple(x[3])) for x in gates]
        assert E.verify(n, tt, g) and all(x[3] != (0, 1, 1, 0) for x in g), v
        assert rec["lower"] <= len(g)
        rec.update(circuit=E.gates_to_str(n, g), gates=[list(x[:3]) + [list(x[3])] for x in g],
                   suite_function=SUITE.get(v))
        rows.append(rec)
    json.dump({"classes": rows, "knuth_source": load_upper()["knuth_source"]}, open(OUT, "w"), indent=1)
    return rows


def table(rows):
    print("| class (b_0..b_5) | true on weights | B2 (Knuth) | U2 cost | label |")
    print("|---|---|---|---|---|")
    for r in rows:
        u2 = str(r["upper"]) if r["lower"] == r["upper"] else f"[{r['lower']}, {r['upper']}]"
        name = f" ({r['suite_function']})" if r.get("suite_function") else ""
        print(f"| {r['class']}{name} | {r['true_on_weights']} | {r['b2_knuth']} | {u2} | "
              + ("lower bound Machine-checked" if r["label"] == "Open" else r["label"]) + " |")


UPPER = os.path.join(R, "symmetric5_upper.json")


def load_upper():
    return json.load(open(UPPER)) if os.path.exists(UPPER) else {"b2_knuth": {}, "knuth_source": None, "classes": []}


def save_upper(data):
    data["classes"].sort(key=lambda c: c["v"])
    json.dump(data, open(UPPER, "w"), indent=1)


def record_upper_circuit(data, v, gates, source):
    """Keep the smaller of the stored and the offered circuit for class v (each re-evaluated)."""
    full, n, tt = C.suite_function("SYM5:" + v)
    g = [(x[0], x[1], x[2], tuple(x[3])) for x in gates]
    assert E.verify(n, tt, g) and all(x[3] != (0, 1, 1, 0) for x in g), v
    old = [c for c in data["classes"] if c["v"] == v]
    if old and len(old[0]["gates"]) <= len(g):
        return False
    data["classes"] = [c for c in data["classes"] if c["v"] != v] + [
        {"v": v, "u2_upper": len(g), "gates": [list(x[:3]) + [list(x[3])] for x in g], "source": source}]
    return True


def knuth_costs(path):
    """B2 cost of every class from Knuth's optimal 5-input chains (optimal5 knuthies.dat)."""
    import compare_optimal5 as K
    table_, digest = K.parse(path)
    data = load_upper()
    for v in classes():
        full, n, tt = C.suite_function("SYM5:" + v)
        data["b2_knuth"][v] = K.lookup(table_, n, tt)[0]
    data["knuth_source"] = {"file": "https://gitlab.com/apgoucher/optimal5 knuthies.dat", "sha256": digest}
    save_upper(data)


def upper_job(args):
    v, minutes = args
    import time
    import certify_u2_suite as U
    import local_improve as L
    name = "SYM5:" + v
    full, n, tt = C.suite_function(name)
    k = load_upper()["b2_knuth"][v]
    enc = C.Encoding(n, tt, k, "B2")                  # satisfiable at k = C_B2(f) (Theorem 1)
    r = C.run_solver(enc, budget=20000000)
    if r["result"] is not True:
        return v, None, f"no B2 circuit at k = {k} within the budget"
    b2 = enc.decode(r["model"])
    u2 = U.expand_xors(name, b2)
    best = L.improve(n, tt, u2, "U2", max_window=7, max_inputs=10, budget=50000, resub=4, plateau=40, seed=1,
                     log=lambda s: None, deadline=time.time() + 60 * minutes)
    nx = sum(tuple(g[3]) == (0, 1, 1, 0) for g in b2)
    return v, best, (f"XOR expansion ({len(u2)} gates) of a {k}-gate B2 circuit with {nx} XORs, then "
                     f"local_improve.py (windows <= 7, resub 4, plateau 40, {minutes:g} min)")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--knuth":
        knuth_costs(sys.argv[2])
        sys.exit()
    if len(sys.argv) >= 3 and sys.argv[1] == "--upper":        # --upper V1,V2,... [minutes]
        from multiprocessing import Pool
        minutes = float(sys.argv[3]) if len(sys.argv) > 3 else 12
        with Pool(4, maxtasksperchild=1) as pool:
            for v, best, source in pool.imap_unordered(upper_job, [(v, minutes) for v in sys.argv[2].split(",")]):
                data = load_upper()
                if best is not None and record_upper_circuit(data, v, best, source):
                    save_upper(data)
                print(v, len(best) if best else None, source, flush=True)
        sys.exit()
    rows = build()
    if sys.argv[1:] == ["--table"]:
        table(rows)
    else:
        for r in rows:
            print(r["class"], r["lower"], r["upper"], r["label"])
