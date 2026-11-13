"""Tests for experiments/elimination.py (gate-elimination constraints, ENCODING.md §5)."""
import json
import os
import random

import pytest

import circuit_sat as C
import elimination as EL
import exact_circuit_complexity as E

RESULTS = os.path.join(os.path.dirname(os.path.abspath(C.__file__)), "results")
U2_GATES = [(0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0), (0, 1, 1, 1)]       # normalized AND-type gates


def evaluate(n, gates, fixed=None):
    """Values of every node on every row (row t has x_j = bit j of t); fixed = (v, c) overrides x_v."""
    vals = []
    for t in range(1 << n):
        val = {j: (t >> j) & 1 for j in range(n)}
        if fixed:
            val[fixed[0]] = fixed[1]
        for (i, j, l, tt) in gates:
            val[i] = tt[2 * val[j] + val[l]]
        vals.append(val)
    return vals


def test_restriction_of_mod3():
    full, n, tt = C.suite_function("MOD3_5")
    r0, r1 = EL.restriction(n, tt, 2, 0), EL.restriction(n, tt, 2, 1)
    weights = [bin(t).count("1") for t in range(16)]
    assert E.normalize(r0) == E.normalize([int(w % 3 == 0) for w in weights])          # MOD3_4
    assert E.normalize(r1) == E.normalize([int(w == 2) for w in weights])               # EXACTLY2_4


def test_substitution_deletes_what_the_lemma_says():
    """Setting x_v = c deletes every gate reading x_v, plus the readers of every gate that c makes
    constant, and what is left computes f|x_v=c."""
    rng = random.Random(4)
    for _ in range(300):
        n, k = rng.randint(2, 5), rng.randint(1, 12)
        gates = []
        for i in range(n, n + k):
            j, l = sorted(rng.sample(range(i), 2))
            gates.append((i, j, l, rng.choice(U2_GATES)))
        for v in range(n):
            for c in (0, 1):
                kept, removed, out = EL.substitute(n, gates, v, c)
                assert len(kept) + len(removed) == k
                readers = {g[0] for g in gates if v in g[1:3]}
                assert readers <= removed
                for (i, j, l, tt) in gates:
                    if v in (j, l):
                        first = (j == v)
                        killed = (tt[2 * c] == tt[2 * c + 1]) if first else (tt[c] == tt[2 + c])
                        if killed:
                            assert readers | {h[0] for h in gates if i in h[1:3]} <= removed
                # what is left computes f|x_v=c on every row
                want = [row[gates[-1][0]] for row in evaluate(n, gates, (v, c))]
                got = []
                for row in evaluate(n, kept, (v, c)):
                    got.append(out[1] if out[0] == "const" else row[out[1]] ^ out[2])
                assert got == want


@pytest.mark.parametrize("level", [1, 2])
def test_constraints_keep_an_optimal_circuit_for_every_3_input_function(level):
    """At k = C(f), with the exact restriction costs, the CNF plus the elimination constraints is
    satisfiable for every function of 3 inputs that depends on all of them."""
    cost2 = {}
    count = 0
    for v in range(256):
        tt = E.normalize([(v >> t) & 1 for t in range(8)])
        if C.support(3, tt) != [0, 1, 2]:
            continue
        c = C.cost(3, tt, "U2")["upper"]
        L = []
        for x in range(3):
            row = []
            for b in (0, 1):
                r = tuple(E.normalize(EL.restriction(3, tt, x, b)))
                if r not in cost2:
                    cost2[r] = C.cost(2, list(r), "U2")["upper"]
                row.append(cost2[r])
            L.append(row)
        enc = C.Encoding(3, tt, c, "U2")
        EL.add_elimination_constraints(enc, L, level)
        r = C.run_solver(enc)
        assert r["result"] is True, (tt, c, L)
        assert E.verify(3, tt, enc.decode(r["model"]))
        count += 1
    assert count == 218


@pytest.mark.parametrize("level", [1, 2])
def test_constraints_bind(level):
    """The constraints are not vacuous: with an (unjustified) bound that forbids any fan-out above 1,
    a function whose every circuit needs an input of fan-out 2 becomes unsatisfiable."""
    full, n, tt = C.suite_function("parity_3")             # U2 cost 6; each XOR reads its inputs twice
    enc = C.Encoding(n, tt, 6, "U2")
    EL.add_elimination_constraints(enc, [[5, 5]] * 3, level)      # claims |N(v)| <= 1
    assert C.run_solver(enc)["result"] is False


def test_recorded_restriction_costs():
    path = os.path.join(RESULTS, "restriction_costs.json")
    if not os.path.exists(path):
        pytest.skip("results/restriction_costs.json not written yet")
    for r in json.load(open(path)):
        tt = E.int_to_tt(int(r["tt"], 16), r["n"])
        gates = [(g[0], g[1], g[2], tuple(g[3])) for g in r["gates"]]
        assert len(gates) == r["cost"] and E.verify(r["n"], tt, gates)
        assert all(g[3] != (0, 1, 1, 0) for g in gates)
        assert [x["k"] for x in r["refutations"]] == list(range(1, r["cost"]))
        assert r["all_refutations_drat_verified"] and all(x["drat_trim_verified"] for x in r["refutations"])


@pytest.mark.skipif(not (C.DRAT_TRIM and os.path.exists(C.DRAT_TRIM)), reason="drat-trim not found")
def test_cube_certificate_with_elimination(tmp_path, monkeypatch):
    """certify_cubes.py --elim: proofs for the CNF with the constraints, checked by drat-trim, and the
    bounds used recorded in the entry. parity_3 has U2 cost 6; its restrictions (parity_2) cost 3."""
    import argparse
    import certify_cubes as Q
    monkeypatch.setattr(Q, "R", str(tmp_path))
    monkeypatch.setattr(EL, "certified_bounds", lambda n, tt: ([[3, 3]] * n, {"0x6": 3}))
    Q.main(argparse.Namespace(name="parity_3", basis="U2", k=5, proofs=str(tmp_path), gate=None, workers=1,
                              refine="", elim=True))
    entry = json.load(open(tmp_path / "cube_certificates.json"))[0]
    assert entry["all_unsat_and_verified"] and entry["elimination"]["L"] == [[3, 3]] * 3
    assert all("_elim_" in c["tag"] for c in entry["cubes"])


def test_recorded_cube_certificates_cover_every_model():
    """Every entry of results/cube_certificates.json: all cubes refuted with verified proofs, and the
    recorded cubes are exactly the split that the entry's gate and refinement define (which covers
    every model, since each split uses an at-least-one clause of the CNF); an entry with elimination
    constraints used the certified bounds."""
    import certify_cubes as Q
    path = os.path.join(RESULTS, "cube_certificates.json")
    if not os.path.exists(path):
        pytest.skip("results/cube_certificates.json not written yet")
    for e in json.load(open(path)):
        full, n, tt = C.suite_function(e["name"])
        assert e["all_unsat_and_verified"]
        assert all(c["result"] is False and c["drat_trim"]["verified"] for c in e["cubes"])
        enc = C.Encoding(n, tt, e["k"], e["basis"])
        refine = Q.parse_refine(",".join(f"{p}:{g}" for p, g in e.get("refine", {}).items()))  # older: none
        expected = sorted(tuple(cube) for cube in Q.split_cubes(enc, e["gate"], refine))
        recorded = []
        for c in e["cubes"]:
            if "cube" in c:
                assert all(list(enc.pairs[g][q]) == pair for g, q, pair in c["cube"])
                recorded.append(tuple((g, q) for g, q, _ in c["cube"]))
            else:                                   # older format: one first-level cube per record
                q = enc.pairs[c["gate"]].index(tuple(c["pair"]))
                assert enc.s[c["gate"]][q] == c["cube_literal"] and c["units"] == [c["cube_literal"]]
                recorded.append(((c["gate"], q),))
        assert sorted(recorded) == expected, e["name"]
        if "elimination" in e:
            assert e["elimination"]["L"] == EL.certified_bounds(n, tt)[0]


def test_multi_level_split():
    """'0:6,0/3:7' splits first-level cube 0 over gate 6, and its sub-cube 3 again over gate 7."""
    import certify_cubes as Q
    full, n, tt = C.suite_function("MOD3_4")
    enc = C.Encoding(n, tt, 6, "B2")
    refine = Q.parse_refine("0:6,0/3:7")
    assert refine == {(0,): 6, (0, 3): 7}
    cubes = Q.split_cubes(enc, 5, refine)
    # gate 5 reads one of 10 pairs, gate 6 one of 15, gate 7 one of 21
    assert len(cubes) == 9 + 14 + 21 and len(set(map(tuple, cubes))) == len(cubes)
    assert sorted(len(c) for c in cubes) == [1] * 9 + [2] * 14 + [3] * 21
