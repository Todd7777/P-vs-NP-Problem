"""Tests for experiments/local_improve.py (SAT-based local improvement with care sets)."""
import random

import exact_circuit_complexity as E
import local_improve as L

AND, OR, XOR = (0, 0, 0, 1), (0, 1, 1, 1), (0, 1, 1, 0)


def value(n, chain_or_G, out=None, pol=0):
    if out is None:
        chain_or_G, out, pol = L.from_chain(n, chain_or_G)
    full = L.full_mask(n)
    return L.evaluate(n, chain_or_G, L.topo(chain_or_G, out, n))[out] ^ (full if pol else 0)


def test_majority3_reaches_its_optimum():
    """(x1&x2) | (x1&x3) | (x2&x3) has 5 gates; MAJ_3 costs 4 in U2."""
    tt = E.normalize(E.tt_from_fn(3, lambda r: int(sum(r) >= 2)))
    naive = [(3, 0, 1, AND), (4, 0, 2, AND), (5, 1, 2, AND), (6, 3, 4, OR), (7, 5, 6, OR)]
    out = L.improve(3, tt, naive, "U2", max_window=5, log=lambda s: None)
    assert len(out) == 4 and E.verify(3, tt, out)


def test_chain_conversion_keeps_the_function():
    """to_chain pushes complements into consumers: same function up to complement, every tt[0] = 0."""
    rng = random.Random(7)
    allowed = [t for t in L._ALL if t not in L.FORBIDDEN["B2"]]
    for _ in range(200):
        n, k = rng.randint(2, 5), rng.randint(1, 8)
        G = {i: [*rng.sample(range(i), 2), rng.choice(allowed)] for i in range(n, n + k)}
        pol = rng.randint(0, 1)
        v = value(n, G, n + k - 1, pol)
        chain = L.to_chain(n, G, n + k - 1, pol)
        assert all(g[3][0] == 0 for g in chain)
        assert value(n, chain) in (v, L.full_mask(n) ^ v)


def test_care_set_allows_smaller_replacements():
    """Window {x1|x2, out} of out = (x1&x2) & (x1|x2), with inputs (x1, x2, g = x1&x2): on the
    combinations that occur the output equals g, so zero gates suffice; on all eight combinations
    it is g & (x1|x2), which needs two."""
    occurring = [((0, 0, 0), (0,)), ((0, 1, 0), (0,)), ((1, 0, 0), (0,)), ((1, 1, 1), (1,))]
    assert L.synthesize(3, occurring, 1, 0, "U2") == ([], [(2, 0)])
    every = [((a, b, g), (g & (a | b),)) for a in (0, 1) for b in (0, 1) for g in (0, 1)]
    assert L.synthesize(3, every, 1, 0, "U2") is None
    assert L.synthesize(3, every, 1, 1, "U2") is None
    assert L.synthesize(3, every, 1, 2, "U2") is not None
    tt = E.normalize(E.tt_from_fn(2, lambda r: r[0] & r[1]))
    out = L.improve(2, tt, [(2, 0, 1, AND), (3, 0, 1, OR), (4, 2, 3, AND)], "U2", max_window=2, log=lambda s: None)
    assert len(out) == 1 and E.verify(2, tt, out)


def test_u2_synthesis_never_uses_xor():
    rows = [((a, b), (a ^ b,)) for a in (0, 1) for b in (0, 1)]
    assert L.synthesize(2, rows, 1, 1, "B2")[0][0][2] in (XOR, (1, 0, 0, 1))
    assert L.synthesize(2, rows, 1, 2, "U2") is None
    gates, _ = L.synthesize(2, rows, 1, 3, "U2")
    assert all(sum(tt) % 2 == 1 for _, _, tt in gates)


def test_simplify_removes_degenerate_gates():
    """A gate that reads one node twice is that node (or its complement)."""
    G = {2: [0, 1, AND], 3: [2, 2, AND]}
    G2, out, pol = L.simplify(G, 3, 0, 2)
    assert (sorted(G2), out, pol) == ([2], 2, 0)
    G2, out, pol = L.simplify({2: [0, 1, AND], 3: [2, 2, (1, 1, 1, 0)]}, 3, 0, 2)   # NAND(g, g) = not g
    assert (out, pol) == (2, 1)


def test_plateau_moves_preserve_the_function(monkeypatch):
    """Same-size replacements with random phases must keep the function and never grow the circuit."""
    rng = random.Random(3)
    allowed = [t for t in L._ALL if t not in L.FORBIDDEN["B2"]]
    G = {i: [i - 1, rng.randrange(i - 1), rng.choice(allowed)] for i in range(5, 16)}   # every gate live
    G[4] = [0, 1, AND]
    chain = L.to_chain(4, G, 15, 0)
    v = value(4, chain)
    tt = E.normalize([(v >> t) & 1 for t in range(16)])
    start = L.improve(4, tt, chain, "B2", max_window=3, log=lambda s: None)
    calls, synth = [], L.synthesize
    monkeypatch.setattr(L, "synthesize", lambda *a, **k: calls.append(k.get("phases_seed")) or synth(*a, **k))
    out = L.improve(4, tt, start, "B2", max_window=4, plateau=8, seed=1, log=lambda s: None)
    assert E.verify(4, tt, out) and len(out) <= len(start)
    assert any(c is not None for c in calls)                        # plateau moves were attempted


def test_improvement_preserves_random_functions():
    rng = random.Random(3)
    allowed = [t for t in L._ALL if t not in L.FORBIDDEN["U2"]]
    for _ in range(6):
        n, k = 4, 14
        G = {i: [*rng.sample(range(i), 2), rng.choice(allowed)] for i in range(n, n + k)}
        chain = L.to_chain(n, G, n + k - 1, 0)
        v = value(n, chain)
        tt = E.normalize([(v >> t) & 1 for t in range(1 << n)])
        if sum(tt) == 0 or E.cost_bounds(n, tt, "U2", kmax=0)["upper"] == 0:
            continue
        out = L.improve(n, tt, chain, "U2", max_window=4, log=lambda s: None)
        assert E.verify(n, tt, out) and len(out) <= len(L.topo(*L.from_chain(n, chain)[:2], n))
