#!/usr/bin/env python3
"""
upper_bound_search.py -- look for a circuit with exactly k gates (an upper bound only).

Runs circuit_sat.Encoding at one k without proof logging. A SAT answer gives a circuit, which is
re-evaluated on the whole truth table before it is reported; nothing is concluded from UNSAT or
from a timeout. (The symmetry-breaking rules are only claimed sound at k = C(f), so an UNSAT answer
at k > C(f) would not even be a lower bound; for an upper bound only SAT matters.)

Usage: python3 upper_bound_search.py NAME BASIS K [--solver cadical195] [--rules ADLRV] [--out FILE.json]
"""
import argparse, json, time

import circuit_sat as C
import exact_circuit_complexity as E


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("basis", choices=["B2", "U2"])
    ap.add_argument("k", type=int)
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--rules", default=C.DEFAULT_RULES,
                    help="symmetry-breaking rules; above C(f) they may exclude every circuit, so fewer can help")
    ap.add_argument("--out")
    a = ap.parse_args()
    full, n, tt = C.suite_function(a.name)
    enc = C.Encoding(n, tt, a.k, a.basis, rules=a.rules)
    t0 = time.time()
    r = C.run_solver(enc, a.solver)
    rec = {"name": full, "basis": a.basis, "k": a.k, "result": r["result"], "seconds": round(time.time() - t0, 1),
           "solver": a.solver, "rules": a.rules}
    if r["result"] is True:
        gates = enc.decode(r["model"])
        assert E.verify(n, tt, gates), "decoded circuit does not compute the target"
        if a.basis == "U2":
            assert all(g[3] != (0, 1, 1, 0) for g in gates), "XOR gate in a U2 circuit"
        rec["circuit"] = E.gates_to_str(n, gates)
        rec["gates"] = [list(g[:3]) + [list(g[3])] for g in gates]
    print(json.dumps({x: rec.get(x) for x in ("name", "basis", "k", "result", "seconds", "circuit")}), flush=True)
    if a.out:
        json.dump(rec, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
