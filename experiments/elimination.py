#!/usr/bin/env python3
"""
elimination.py -- gate-elimination constraints for circuit_sat.Encoding (U2 only).

Lemma (proved in ENCODING.md §5). Let C be a U2 chain with k gates computing f, let x_v be an input,
N(v) the set of gates that read x_v, and for a gate g, S(g) the set of gates that read g.
  (a) For c in {0, 1}:  k >= C(f|x_v=c) + |N(v)|.
  (b) If g reads x_v and x_v = c makes g constant (every U2 gate has exactly one such value c for
      each of its inputs):  k >= C(f|x_v=c) + |N(v) u S(g)|.
So if L[v][c] is a proven lower bound on C(f|x_v=c), every k-gate chain computing f satisfies
|N(v)| <= k - L[v][c] and, whenever g reads x_v and x_v = c makes g constant, |N(v) u S(g)| <=
k - L[v][c]. These are properties of all k-gate chains, so adding them to the CNF keeps it
satisfiable whenever the symmetry-reduced CNF is (Theorem 1 of ENCODING.md gives an optimal chain
that obeys the rules at k = C(f); that chain also obeys these constraints).

Usage: python3 elimination.py NAME K [--l0 L --l1 L] [--budget CONFLICTS]   (solve without proofs)
"""
import argparse, time

import circuit_sat as C
import exact_circuit_complexity as E


def restriction(n, tt, v, c):
    """Truth table of f|x_v=c as a function of the other n-1 inputs (in their original order)."""
    out = []
    for t in range(1 << (n - 1)):
        low, high = t & ((1 << v) - 1), t >> v
        out.append(tt[low | (c << v) | (high << (v + 1))])
    return out


def add_elimination_constraints(enc, L, level=1):
    """Append the constraints of the lemma to enc (in place). L[v][c] is a lower bound on C(f|x_v=c).
    level 1: (E1) and (E2) of ENCODING.md §5; level 2 adds (E3), the union over all gates that x_v = c
    makes constant. Returns the number of clauses added."""
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    assert enc.basis == "U2"
    n, k = enc.n, enc.k
    G = range(n, n + k)
    before = len(enc.clauses)
    pool = IDPool(start_from=enc.nvars + 1)
    new = lambda key: pool.id(key)
    cls = []
    # rd[h][v]: gate h reads input v;  rg[h][g]: gate h reads gate g  (only the direction s -> rd is needed)
    rd = {(h, v): new(("rd", h, v)) for h in G for v in range(n)}
    rg = {(h, g): new(("rg", h, g)) for h in G for g in G if g < h}
    for h in G:
        for q, (j, l) in enumerate(enc.pairs[h]):
            for node in (j, l):
                if node < n:
                    cls.append([-enc.s[h][q], rd[(h, node)]])
                else:
                    cls.append([-enc.s[h][q], rg[(h, node)]])

    def atmost(lits, bound, enable=None):
        if bound >= len(lits):
            return
        if bound < 0:
            cls.append([-enable] if enable else [])
            return
        card = CardEnc.atmost(lits, bound, vpool=pool, encoding=EncType.seqcounter).clauses
        cls.extend([c + [-enable] for c in card] if enable else card)

    for v in range(n):
        # (a) fan-out of x_v
        atmost([rd[(h, v)] for h in G], k - max(L[v][0], L[v][1]))
        for g in G:
            # kill[c]: g reads x_v and x_v = c makes g constant. g's inputs (j, l), j < l, gate bits
            # (f01, f10, f11), f00 = 0: x_v = j is killed by 0 iff f01 = 0, by 1 iff f10 = f11;
            # x_v = l is killed by 0 iff f10 = 0, by 1 iff f01 = f11.
            kill = {0: new(("k0", g, v)), 1: new(("k1", g, v))}
            f01, f10, f11 = enc.f[g]
            for q, (j, l) in enumerate(enc.pairs[g]):
                sq = enc.s[g][q]
                if j == v:
                    cls.append([-sq, f01, kill[0]])
                    cls.append([-sq, -f10, -f11, kill[1]])
                    cls.append([-sq, f10, f11, kill[1]])
                if l == v:
                    cls.append([-sq, f10, kill[0]])
                    cls.append([-sq, -f01, -f11, kill[1]])
                    cls.append([-sq, f01, f11, kill[1]])
            # (b) |N(v) u S(g)| <= k - L[v][c] when kill[c]
            u = []
            for h in G:
                if h == g:
                    u.append(rd[(h, v)])
                    continue
                w = new(("u", g, v, h))
                cls.append([-rd[(h, v)], w])
                if h > g:
                    cls.append([-rg[(h, g)], w])
                u.append(w)
            for c in (0, 1):
                atmost(u, k - L[v][c], enable=kill[c])
    if level >= 2:
        # (E3) |N(v) u U{S(g) : g in N(v), x_v = c makes g constant}| <= k - L[v][c]
        for v in range(n):
            for c in (0, 1):
                u = []
                for h in G:
                    w = new(("e3", v, c, h))
                    cls.append([-rd[(h, v)], w])
                    for g in G:
                        if g < h:
                            cls.append([-rg[(h, g)], -pool.id(("k%d" % c, g, v)), w])
                    u.append(w)
                atmost(u, k - L[v][c])
    enc.clauses.extend(cls)
    enc.nvars = max(enc.nvars, pool.top)
    return len(enc.clauses) - before


def tt_hex(tt):
    """Key of a normalized truth table in results/restriction_costs.json."""
    return hex(sum(b << t for t, b in enumerate(E.normalize(list(tt)))))


def certified_bounds(n, tt, path=None):
    """L[v][c]: the Machine-checked U2 cost of f|x_v=c from results/restriction_costs.json (written by
    certify_restrictions.py; every smaller k refuted by a drat-trim-verified proof), and the records used."""
    import json, os
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "restriction_costs.json")
    table = {(r["n"], r["tt"]): r for r in json.load(open(path))}
    L, used = [], {}
    for v in range(n):
        row = []
        for c in (0, 1):
            key = (n - 1, tt_hex(restriction(n, tt, v, c)))
            rec = table[key]
            assert rec["basis"] == "U2" and rec["all_refutations_drat_verified"]
            assert [r["k"] for r in rec["refutations"]] == list(range(1, rec["cost"]))
            row.append(rec["cost"])
            used[key[1]] = rec["cost"]
        L.append(row)
    return L, used


def substitute(n, gates, v, c):
    """Set x_v = c in a chain and delete every gate that becomes constant or a copy (or complement) of
    one node -- the construction in the proof of the lemma. Returns (kept, removed, out) where kept
    lists the surviving gates (id, a, b, tt) over the original node ids, removed is the set of deleted
    gate ids, and out is the output as ("const", bit) or ("node", id, pol)."""
    rep = {u: ("node", u, 0) for u in range(n)}
    rep[v] = ("const", c)
    kept, removed = [], set()
    for (i, j, l, tt) in gates:
        tt = list(tt)
        a, b = rep[j], rep[l]
        if a[0] == "const" or b[0] == "const" or a[1] == b[1]:
            removed.add(i)
            if a[0] == "const" and b[0] == "const":
                rep[i] = ("const", tt[2 * a[1] + b[1]])
                continue
            if a[0] == "const":                       # function of b only
                h = [tt[2 * a[1] + y] for y in (0, 1)]
                node = b
            elif b[0] == "const":                     # function of a only
                h = [tt[2 * x + b[1]] for x in (0, 1)]
                node = a
            else:                                     # both inputs are (complements of) one node
                h = [tt[2 * (y ^ a[2]) + (y ^ b[2])] for y in (0, 1)]
                node = ("node", a[1], 0)
            if h[0] == h[1]:
                rep[i] = ("const", h[0])
            else:
                rep[i] = ("node", node[1], node[2] ^ h[0])
            continue
        t2 = tuple(tt[2 * (x ^ a[2]) + (y ^ b[2])] for x in (0, 1) for y in (0, 1))
        kept.append((i, a[1], b[1], t2))
        rep[i] = ("node", i, 0)
    return kept, removed, rep[gates[-1][0]]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("k", type=int)
    ap.add_argument("--l0", type=int, required=True, help="lower bound on C(f|x=0) (symmetric f)")
    ap.add_argument("--l1", type=int, required=True, help="lower bound on C(f|x=1) (symmetric f)")
    ap.add_argument("--budget", type=int)
    ap.add_argument("--solver", default="cadical195")
    a = ap.parse_args()
    full, n, tt = C.suite_function(a.name)
    enc = C.Encoding(n, tt, a.k, "U2")
    added = add_elimination_constraints(enc, [[a.l0, a.l1] for _ in range(n)])
    print(f"{full} U2 k={a.k}: {len(enc.clauses)} clauses ({added} from elimination), {enc.nvars} vars", flush=True)
    t0 = time.time()
    r = C.run_solver(enc, a.solver, budget=a.budget)
    print(f"result {r['result']} in {time.time() - t0:.1f}s, conflicts {r['stats'].get('conflicts')}")
