#!/usr/bin/env python3
"""
build_final_table.py -- one labelled table of the explicit-function costs.

Inputs (all in results/): certificates.json (certify_costs.py summarize), explicit_costs.json (the
first run: old intervals and circuits), optimal5_comparison.json (Knuth's 5-input table).
Output: results/explicit_final.json and a Markdown table on stdout.

Labels
  Theorem          lower and upper bound both proved in docs/05-worked-mathematics.md (parity);
  Machine-checked  upper bound: a circuit re-evaluated on the whole truth table; lower bound: every
                   k below it refuted by a DRAT proof that drat-trim verified (see ENCODING.md §4);
  Numerical        exact, but some refutation has no verified proof (solver answer only);
  Open             only an interval is known.
"""
import json, os

import circuit_sat as C
import exact_circuit_complexity as E

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# Published values that were read at the source (see docs/bibliography.md):
#   Knuth's optimal 5-input chains (optimal5/knuthies.dat), via optimal5_comparison.json, for every B2 entry;
#   Kulikov-Pechenev-Slezkin, arXiv:2102.12579v3, §1.1, quoting Knuth (TAOCP 4 Fasc. 6, answer to
#   exercise 7.2.2.2-480): size(MOD3^{4,0}) = 7, size(MOD3^{5,0}) = 10;
#   Schnorr (1974), proved in docs/05 §5.2 (Theorem 5.3): C_U2(parity_n) = 3(n-1).
KPS = {"MOD3_4 (sum=0 mod 3)": 7, "MOD3_5 (sum=0 mod 3)": 10}


def parse_circuit(n, s):
    """Inverse of exact_circuit_complexity.gates_to_str."""
    ops = {"AND": (0, 0, 0, 1), "x>y": (0, 0, 1, 0), "x<y": (0, 1, 0, 0), "XOR": (0, 1, 1, 0), "OR": (0, 1, 1, 1)}
    gates = []
    for part in s.split("; "):
        lhs, rhs = part.split(" = ")
        op, args = rhs[:-1].split("(")
        a, b = args.split(",")
        node = lambda w: int(w[1:]) - 1
        gates.append((node(lhs), node(a), node(b), ops[op]))
    return gates


def main():
    certs = {(c["name"], c["basis"]): c for c in json.load(open(os.path.join(R, "certificates.json")))["results"]}
    old = {(r["name"], r["basis"]): r for r in json.load(open(os.path.join(R, "explicit_costs.json")))}
    knuth = {r["name"]: r["knuth_B2_cost"] for r in json.load(open(os.path.join(R, "optimal5_comparison.json")))["functions"]}
    rows = []
    for name, n, fn, bases in E.explicit_suite():
        tt = E.tt_from_fn(n, fn)
        for basis in bases:
            o = old[(name, basis)]
            c = certs.get((name, basis))
            e = {"name": name, "n": n, "basis": basis, "previous_interval": [o["lower"], o["upper"]]}
            if name.startswith("parity_") and basis == "U2":
                circuit = o["circuit"]                       # verified circuit of the first run
                e.update(lower=3 * (n - 1), upper=3 * (n - 1), label="Theorem",
                         lower_evidence="Schnorr's theorem C_U2(parity_n) = 3(n-1), docs/05 Theorem 5.3")
            elif name.startswith("parity_") and basis == "B2":
                circuit = c["circuit"]
                e.update(lower=n - 1, upper=n - 1, label="Theorem",
                         lower_evidence="each gate joins at most two components of the wiring graph (docs/05 §5.2)")
            elif c and c["exact"]:
                circuit = c["circuit"]
                e.update(lower=c["lower"], upper=c["upper"],
                         label="Machine-checked" if c["all_refutations_drat_verified"] else "Numerical",
                         lower_evidence=f"k = 1..{c['upper'] - 1} refuted (circuit_sat.py; DRAT proofs "
                                        f"{'verified by drat-trim' if c['all_refutations_drat_verified'] else 'NOT all verified'})")
            else:
                lo = max(o["lower"], c["lower"] if c else 0)
                hi = min(x for x in (o["upper"], c["upper"] if c else None) if x is not None)
                circuit = c["circuit"] if c and c["upper"] == hi else o["circuit"]
                e.update(lower=lo, upper=hi, label="Open", lower_evidence=f"k = 1..{lo - 1} refuted")
            gates = parse_circuit(n, circuit)
            assert len(gates) == e["upper"] and E.verify(n, tt, gates), (name, basis)
            e["circuit"], e["gates"] = circuit, [list(g[:3]) + [list(g[3])] for g in gates]
            e["also_machine_checked"] = bool(c and c["exact"] and c["all_refutations_drat_verified"]
                                             and c["upper"] == e["upper"])
            if basis == "B2":
                e["published"] = {"value": knuth[name], "source": "Knuth's optimal 5-input chains (optimal5 knuthies.dat)"}
                if name in KPS:
                    e["published"]["also"] = {"value": KPS[name], "source": "Knuth via Kulikov-Pechenev-Slezkin, arXiv:2102.12579"}
            elif name.startswith("parity_"):
                e["published"] = {"value": 3 * (n - 1), "source": "Schnorr 1974 (docs/05 Theorem 5.3)"}
            else:
                e["published"] = None
            pub = e["published"]
            e["agrees_with_published"] = None if pub is None else (
                e["lower"] <= pub["value"] <= e["upper"] and ("also" not in pub or e["lower"] <= pub["also"]["value"] <= e["upper"]))
            rows.append(e)
    rows.sort(key=lambda r: (r["basis"], r["n"], r["name"]))
    json.dump({"description": __doc__.strip().splitlines()[0], "functions": rows},
              open(os.path.join(R, "explicit_final.json"), "w"), indent=1)
    print("| function | n | basis | before | now | label | published | agrees |")
    print("|---|---|---|---|---|---|---|---|")
    for e in rows:
        before = "[{}, {}]".format(*e["previous_interval"]) if e["previous_interval"][0] != e["previous_interval"][1] else str(e["previous_interval"][0])
        now = str(e["upper"]) if e["lower"] == e["upper"] else f"[{e['lower']}, {e['upper']}]"
        pub = "—" if e["published"] is None else str(e["published"]["value"])
        agree = {None: "—", True: "yes", False: "**NO**"}[e["agrees_with_published"]]
        print(f"| {e['name']} | {e['n']} | {e['basis']} | {before} | {now} | {e['label']} | {pub} | {agree} |")


if __name__ == "__main__":
    main()
