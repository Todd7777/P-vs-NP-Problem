"""Tests for experiments/symmetric5_u2.py (U2 costs of the symmetric functions of 5 inputs)."""
import json
import os
import random

import pytest

import circuit_sat as C
import exact_circuit_complexity as E
import symmetric5_u2 as S

RESULTS = os.path.join(os.path.dirname(os.path.abspath(C.__file__)), "results")


def test_nineteen_classes_partition_the_nonconstant_functions():
    reps = S.classes()
    assert len(reps) == 19
    seen = {}
    for v in reps:
        assert v[0] == "0" and v == min(m for m in S.members(v) if m[0] == "0")
        for m in S.members(v):
            assert m not in seen
            seen[m] = v
    assert sorted(seen) == sorted(format(m, "06b")[::-1] for m in range(1, 63))


def test_negating_every_input():
    """negate_inputs(chain) computes f(not x), up to the free output negation (the same on every row)."""
    rng = random.Random(2)
    gates_u2 = [(0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0), (0, 1, 1, 1)]

    def value(chain, n, row):
        val = {j: (row >> j) & 1 for j in range(n)}
        for (i, j, l, tt) in chain:
            val[i] = tt[2 * val[j] + val[l]]
        return val[chain[-1][0]]

    for _ in range(100):
        n, k = 5, rng.randint(1, 10)
        gates = [(i, *sorted(rng.sample(range(i), 2)), rng.choice(gates_u2)) for i in range(n, n + k)]
        neg = S.negate_inputs(n, gates)
        assert len(neg) <= k and all(g[3][0] == 0 for g in neg)
        flip = {value(gates, n, t) ^ value(neg, n, (1 << n) - 1 - t) for t in range(1 << n)}
        assert len(flip) == 1


def test_class_members_have_the_same_suite_value():
    """The suite records reused for a class are turned into circuits for its representative."""
    for v in S.SUITE:
        rec = S.suite_record(v)
        if rec is None:
            continue
        full, n, tt = C.suite_function("SYM5:" + v)
        assert E.verify(n, tt, rec[4])


def test_recorded_symmetric5():
    path = os.path.join(RESULTS, "symmetric5_u2.json")
    if not os.path.exists(path):
        pytest.skip("results/symmetric5_u2.json not written yet")
    data = json.load(open(path))
    assert sorted(r["class"] for r in data["classes"]) == S.classes()
    for r in data["classes"]:
        full, n, tt = C.suite_function("SYM5:" + r["class"])
        gates = [(g[0], g[1], g[2], tuple(g[3])) for g in r["gates"]]
        assert len(gates) == r["upper"] and E.verify(n, tt, gates)
        assert all(g[3] != (0, 1, 1, 0) for g in gates)
        assert r["lower"] <= r["upper"]
        assert (r["label"] == "Open") == (r["lower"] < r["upper"])
        if "lower_from_restrictions" in r:
            assert r["lower_from_restrictions"] == max(r["restriction_costs"].values()) + 1


def test_shannon_start_both_paths():
    """f = x5 ? f1 : f0: from a joint SAT synthesis of (f0, f1), or, when that finds nothing within the
    budget, from the certified optimal circuits of f0 and f1 side by side."""
    if not os.path.exists(os.path.join(RESULTS, "restriction_costs.json")):
        pytest.skip("results/restriction_costs.json not written yet")
    full, n, tt = C.suite_function("SYM5:011110")                      # NAE5, U2 cost 9
    chain, how = S.shannon_start("011110")
    assert E.verify(n, tt, chain) and "jointly" in how and len(chain) == 9
    chain, how = S.shannon_start("011110", budget=1, kmax=2)            # forces the fallback
    assert E.verify(n, tt, chain) and "side by side" in how
