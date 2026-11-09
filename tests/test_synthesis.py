"""Tests for the exact circuit synthesis code in experiments/.

Run from the repository root with `pytest` (about 15 seconds). `RUN_SLOW=1 pytest` adds the
slower checks (all 222 NPN classes of 4-input functions against Knuth's distribution, more rule
ablations).
"""
import itertools
import json
import os
import random
from collections import Counter

import pytest

import brute_force as BF
import circuit_sat as C
import exact_circuit_complexity as E

RESULTS = os.path.join(os.path.dirname(os.path.abspath(C.__file__)), "results")
slow = pytest.mark.skipif(not os.environ.get("RUN_SLOW"), reason="slow; set RUN_SLOW=1")
needs_drat = pytest.mark.skipif(not (C.DRAT_TRIM and os.path.exists(C.DRAT_TRIM)),
                                reason="drat-trim not found (set DRAT_TRIM or put it on PATH)")


def tt_int(n, x):
    return [(x >> t) & 1 for t in range(1 << n)]


def sym_tt(n, accept):
    """Truth table of the symmetric function that is 1 iff the number of ones is in `accept`."""
    return [int(bin(t).count("1") in accept) for t in range(1 << n)]


# ------------------------------------------------------------------ old encoding (exact_circuit_complexity.py)
def test_claude_md_quick_check():
    r = E.cost_bounds(3, E.tt_from_fn(3, lambda r: sum(r) % 2))
    assert (r["lower"], r["upper"]) == (2, 2)


@pytest.mark.parametrize("name,basis,cost", [("parity_2", "U2", 3), ("parity_3", "U2", 6),
                                             ("ADD2 carry-out", "B2", 5), ("MUL2 bit2", "B2", 3)])
def test_old_encoding_known_costs(name, basis, cost):
    full, n, tt = C.suite_function(name)
    r = E.cost_bounds(n, tt, basis)
    assert r["status"] == "exact" and r["upper"] == cost
    assert E.verify(n, tt, r["circuit"])


def test_verify_rejects_wrong_chain():
    xor = E.tt_from_fn(2, lambda r: r[0] ^ r[1])
    assert E.verify(2, xor, [(2, 0, 1, (0, 1, 1, 0))])
    assert not E.verify(2, xor, [(2, 0, 1, (0, 0, 0, 1))])                # AND is not XOR
    assert E.verify(2, [1 - b for b in xor], [(2, 0, 1, (0, 1, 1, 0))])   # output complement is free


# ------------------------------------------------------------------ building blocks of circuit_sat.py
def test_pair_index_matches_pair_list():
    for i in range(2, 14):
        assert [C.pair_index(j, l) for (j, l) in C.pair_list(i)] == list(range(i * (i - 1) // 2))


def test_support_and_restriction():
    tt = E.tt_from_fn(4, lambda r: int(r[1] and not r[3]))     # x2 AND NOT x4
    assert C.support(4, tt) == [1, 3]
    m, rtt, sup = C.restrict_to_support(4, tt)
    assert (m, sup, rtt) == (2, [1, 3], [0, 1, 0, 0])


def test_symmetric_adjacent_pairs():
    assert C.symmetric_adjacent_pairs(5, C.suite_function("MAJ_5")[2]) == [0, 1, 2, 3]
    assert C.symmetric_adjacent_pairs(2, E.tt_from_fn(2, lambda r: int(r[0] and not r[1]))) == []
    # MAJ_3(x1,x2,x3) xor x4 xor x5: symmetric in x1,x2,x3 and in x4,x5, but not across
    assert C.symmetric_adjacent_pairs(5, C.suite_function("MAJ_3 xor x4 xor x5")[2]) == [0, 1, 3]


def test_lex_less_clauses_exhaustive():
    A, B, cond = [1, 2, 3], [4, 5, 6], 7
    cls = C.lex_less(A, B, cond)
    for bits in itertools.product((0, 1), repeat=7):
        holds = all(any(bits[abs(lit) - 1] == (lit > 0) for lit in c) for c in cls)
        a, b = bits[0] * 4 + bits[1] * 2 + bits[2], bits[3] * 4 + bits[4] * 2 + bits[5]
        assert holds == (not bits[6] or a < b)


def test_exactly_one_pair_per_gate():
    enc = C.Encoding(3, tt_int(3, 0x96), 2, "B2", rules="")
    for i in (3, 4):
        vs = list(enc.s[i]) + list(enc.o[i].values())
        cls = [c for c in enc.clauses if all(abs(lit) in vs for lit in c)]
        for bits in itertools.product((0, 1), repeat=len(vs)):
            val = dict(zip(vs, bits))
            holds = all(any(val[abs(lit)] == (lit > 0) for lit in c) for c in cls)
            chosen = [q for q, v in enumerate(enc.s[i]) if val[v]]
            expect = len(chosen) == 1 and all(val[o] == (chosen[0] >= q) for q, o in enc.o[i].items())
            assert holds == expect


# ------------------------------------------------------------------ new encoding vs exhaustive enumeration
def test_brute_force_distribution_n3_b2():
    table = BF.chain_costs(3, 4, "B2")
    dist = Counter(BF.cost_of(3, tt_int(3, x), table) for x in range(256))
    assert dict(dist) == {0: 8, 1: 30, 2: 114, 3: 80, 4: 24}     # regression value, every function covered


@pytest.mark.parametrize("basis", ["B2", "U2"])
def test_new_encoding_matches_brute_force_n3(basis):
    kmax = 4
    table = BF.chain_costs(3, kmax, basis)
    for x in range(256):
        tt = tt_int(3, x)
        r = C.cost(3, tt, basis, kmax=kmax)
        bf = BF.cost_of(3, tt, table)
        if bf is None:
            assert r["status"] == "interval" and r["lower"] == kmax + 1
        else:
            assert r["status"] == "exact" and r["upper"] == bf
            if bf > 0:                                   # cost 0: a constant or literal, no gates
                assert E.verify(3, tt, r["circuit"])


@pytest.mark.parametrize("name,basis,cost", [("parity_3", "U2", 6), ("parity_4", "B2", 3), ("MOD3_4", "B2", 7),
                                             ("MUL2 bit1", "B2", 3), ("MAJ_3 xor x4 xor x5", "B2", 6)])
def test_new_encoding_known_costs(name, basis, cost):
    full, n, tt = C.suite_function(name)
    r = C.cost(n, tt, basis)
    assert r["status"] == "exact" and r["upper"] == cost
    assert E.verify(n, tt, r["circuit"])


def test_function_with_irrelevant_inputs():
    # x1 xor x3 as a function of four inputs: cost 1, and the chain must use the right inputs
    tt = E.tt_from_fn(4, lambda r: r[0] ^ r[2])
    r = C.cost(4, tt, "B2")
    assert r["upper"] == 1 and E.verify(4, tt, r["circuit"])


ABLATION_FUNCS = [("B2", 4, sym_tt(4, {0, 3})), ("B2", 4, sym_tt(4, {2})), ("B2", 4, tt_int(4, 0x1ee8)),
                  ("U2", 3, sym_tt(3, {1, 3})), ("U2", 3, sym_tt(3, {1}))]


@pytest.mark.parametrize("drop", list(C.DEFAULT_RULES))
def test_dropping_a_rule_never_lowers_the_cost(drop):
    """Every rule is claimed sound, so removing one may only make the search slower, never cheaper."""
    for basis, n, tt in ABLATION_FUNCS:
        full = C.cost(n, tt, basis)
        fewer = C.cost(n, tt, basis, rules=C.DEFAULT_RULES.replace(drop, ""))
        assert full["status"] == fewer["status"] == "exact"
        assert full["upper"] == fewer["upper"], (basis, tt, drop)


@slow
@pytest.mark.parametrize("drop", list(C.DEFAULT_RULES))
def test_dropping_a_rule_random_functions(drop):
    rng = random.Random(2026)
    for _ in range(12):
        tt = tt_int(4, rng.randrange(1 << 16))
        assert C.cost(4, tt, "B2")["upper"] == C.cost(4, tt, "B2", rules=C.DEFAULT_RULES.replace(drop, ""))["upper"]


@slow
def test_knuth_distribution_all_4_input_functions():
    classes = E.npn_classes(4)
    dist = Counter()
    for canon, size in classes.items():
        dist[C.cost(4, E.int_to_tt(canon, 4), "B2")["upper"]] += size
    assert [dist[c] for c in range(8)] == [10, 60, 456, 2474, 10624, 24184, 25008, 2720]


# ------------------------------------------------------------------ certificates
@needs_drat
def test_drat_certificate_roundtrip(tmp_path):
    full, n, tt = C.suite_function("MOD3_4")
    rec = C.certify(C.Encoding(n, tt, 6, "B2"), str(tmp_path), "mod3_4_k6")
    assert rec["result"] is False and rec["drat_trim"]["verified"] is True
    assert C.sha256(str(tmp_path / "mod3_4_k6.cnf")) == rec["cnf_sha256"]
    assert C.sha256(str(tmp_path / "mod3_4_k6.drat")) == rec["proof_sha256"]
    empty = tmp_path / "empty.drat"
    empty.write_bytes(b"")
    assert C.drat_check(str(tmp_path / "mod3_4_k6.cnf"), str(empty))["verified"] is False


def test_certify_sat_returns_verified_circuit(tmp_path):
    full, n, tt = C.suite_function("MOD3_4")
    rec = C.certify(C.Encoding(n, tt, 7, "B2"), str(tmp_path), "mod3_4_k7", check=False)
    assert rec["result"] is True and E.verify(n, tt, rec["gates"])
    assert not (tmp_path / "mod3_4_k7.drat").exists()


# ------------------------------------------------------------------ recorded results
def _final():
    path = os.path.join(RESULTS, "explicit_final.json")
    if not os.path.exists(path):
        pytest.skip("results/explicit_final.json not written yet")
    return json.load(open(path))


def test_recorded_circuits_compute_their_functions():
    for e in _final()["functions"]:
        if e["gates"]:
            full, n, tt = C.suite_function(e["name"])
            gates = [(g[0], g[1], g[2], tuple(g[3])) for g in e["gates"]]
            assert len(gates) == e["upper"], e["name"]
            assert E.verify(n, tt, gates), e["name"]


def test_recorded_labels_are_justified():
    final = _final()
    certs = json.load(open(os.path.join(RESULTS, "certificates.json")))["results"]
    by_key = {(c["name"], c["basis"]): c for c in certs}
    for e in final["functions"]:
        assert e["label"] in ("Theorem", "Machine-checked", "Numerical", "Open")
        if e["label"] == "Machine-checked":
            c = by_key[(e["name"], e["basis"])]
            assert c["exact"] and c["upper"] == e["upper"] and c["all_refutations_drat_verified"]
            assert [r["k"] for r in c["refutations"]] == list(range(1, e["upper"]))
        if e["label"] == "Open":
            assert e["lower"] < e["upper"]


# ------------------------------------------------------------------ helpers of the result scripts
def test_parse_circuit_roundtrip():
    import build_final_table as B
    full, n, tt = C.suite_function("MOD3_4")
    r = C.cost(n, tt, "B2")
    s = E.gates_to_str(n, r["circuit"])
    assert E.gates_to_str(n, B.parse_circuit(n, s)) == s
    assert E.verify(n, tt, B.parse_circuit(n, s))


def test_optimal5_record_decoder(tmp_path):
    import compare_optimal5 as O
    # one record: x1 & x2 (operator code 0, operand indices 1 and 2 stored as 0 and 1), then x1 ^ gate6
    g1 = (0 << 8) | (1 << 4) | 0
    g2 = (2 << 8) | (5 << 4) | 0
    x = g1 | (g2 << 10)
    rec = x.to_bytes(5, "little") + bytes(10)
    path = tmp_path / "one.dat"
    path.write_bytes(rec)
    table, _ = O.parse(str(path))
    x1, x2 = O.INPUTS[0], O.INPUTS[1]
    assert table == {x1 ^ (x1 & x2): (2, [(1, "&", 2), (1, "^", 6)])}


@needs_drat
def test_cube_split_refutation(tmp_path, monkeypatch):
    import argparse
    import certify_cubes as Q
    monkeypatch.setattr(Q, "R", str(tmp_path))          # keep results/ untouched
    Q.main(argparse.Namespace(name="MOD3_4", basis="B2", k=6, proofs=str(tmp_path), gate=None, workers=1))
    entry = json.load(open(tmp_path / "cube_certificates.json"))[0]
    assert entry["all_unsat_and_verified"] and len(entry["cubes"]) == 10   # gate 5 can read 10 pairs
