#!/usr/bin/env python3
"""
local_improve.py -- shrink a circuit by re-synthesizing small windows with a SAT solver.
Upper bounds only: the method never proves that a smaller circuit does not exist.

A window is a set W of gates that is convex (no path leaves W and re-enters it). Its inputs are
the nodes outside W that feed it; its outputs are the gates of W that are read outside W, or the
circuit output. Kulikov, Pechenev and Slezkin ("SAT-based circuit local improvement", MFCS 2022)
replace a window by a smaller sub-circuit that computes the same outputs from the same inputs.
This script does the same with one relaxation that is cheap because n is small: the replacement
only has to agree with W on the combinations of W's inputs that actually occur as x ranges over
{0,1}^n (the care set), and each output may come out complemented, since negations are free in
this cost model (a consumer absorbs a complemented input by changing its gate type). Convexity
keeps the rewired circuit acyclic.

Every accepted replacement is re-evaluated on the full truth table, and the final circuit is
checked with exact_circuit_complexity.verify (and, for U2, for the absence of XOR gates).

Usage: python3 local_improve.py NAME BASIS [--start suite|b2opt|FILE.json] [--max-window 7]
           [--max-inputs 9] [--budget CONFLICTS] [--minutes M] [--plateau N --seed S] [--resub R]
           [--solver cadical195] [--record]
  --start suite   the circuit recorded in results/u2_suite.json (U2) or explicit_final.json (B2)
  --start b2opt   (U2) the XOR expansion of the optimal B2 circuit in results/explicit_final.json
  --start FILE    a JSON object with "gates" ([[i, j, l, [tt]], ...]) and "basis"; a B2 circuit is
                  XOR-expanded first when BASIS is U2
  --record        (U2) record the result in results/u2_suite.json if it beats the recorded bound
"""
import argparse, json, os, time

import circuit_sat as C
import exact_circuit_complexity as E

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# Gate functions are 4-tuples tt with tt[2a + b] = f(a, b). Forbidden patterns per basis: B2 excludes
# the constants and the projections; U2 (no XOR/XNOR) excludes every even-weight pattern.
_ALL = [tuple((v >> s) & 1 for s in (3, 2, 1, 0)) for v in range(16)]
FORBIDDEN = {
    "B2": [t for t in _ALL if t in {(0, 0, 0, 0), (1, 1, 1, 1), (0, 0, 1, 1), (1, 1, 0, 0), (0, 1, 0, 1), (1, 0, 1, 0)}],
    "U2": [t for t in _ALL if sum(t) % 2 == 0],
}


class Reject(Exception):
    pass


# ------------------------------------------------------------------ circuits as {gate: [a, b, tt]}
def full_mask(n):
    return (1 << (1 << n)) - 1


def input_masks(n):
    """Bit t of mask j is x_j on row t (row t has x_j = bit j of t, as in E.truth_rows)."""
    return [sum(1 << t for t in range(1 << n) if (t >> j) & 1) for j in range(n)]


def apply_tt(tt, A, B, full):
    nA, nB = full ^ A, full ^ B
    return ((nA & nB) if tt[0] else 0) | ((nA & B) if tt[1] else 0) | ((A & nB) if tt[2] else 0) | ((A & B) if tt[3] else 0)


def topo(G, out, n):
    """Gates the output depends on, in topological order."""
    order, seen, stack = [], set(), [(out, False)]
    while stack:
        v, post = stack.pop()
        if v < n:
            continue
        if post:
            order.append(v)
        elif v not in seen:
            seen.add(v)
            stack.append((v, True))
            stack += [(G[v][0], False), (G[v][1], False)]
    return order


def evaluate(n, G, order):
    full, val = full_mask(n), dict(enumerate(input_masks(n)))
    for g in order:
        a, b, tt = G[g]
        val[g] = apply_tt(tt, val[a], val[b], full)
    return val


def from_chain(n, gates):
    """Repository chain [(i, j, l, tt)] -> (G, out, out_pol); the output is the last gate."""
    G = {g[0]: [g[1], g[2], tuple(g[3])] for g in gates}
    return G, gates[-1][0], 0


def to_chain(n, G, out, out_pol):
    """(G, out, out_pol) -> repository chain: gates renumbered n, n+1, ..., every tt with tt[0] = 0
    (complements pushed into the consumers), output last. Its output may be the complement of the
    target, which E.verify accepts (negations are free)."""
    order = topo(G, out, n)
    flip, new_id, chain = {j: 0 for j in range(n)}, {j: j for j in range(n)}, []
    for pos, g in enumerate(order):
        a, b, tt = G[g]
        t2 = tuple(tt[2 * (x ^ flip[a]) + (y ^ flip[b])] for x in (0, 1) for y in (0, 1))
        flip[g] = t2[0]
        if t2[0]:
            t2 = tuple(1 - v for v in t2)
        new_id[g] = n + pos
        chain.append((n + pos, new_id[a], new_id[b], t2))
    return chain


def simplify(G, out, out_pol, n):
    """Remove gates that read one node twice or ignore an input (they can appear when two window
    outputs are mapped to the same node). Raises Reject if a gate becomes constant."""
    G = {g: list(v) for g, v in G.items()}
    while True:
        hit = None
        for g in topo(G, out, n):
            a, b, tt = G[g]
            if a == b:
                hit = (g, a, tt[0], tt[3])
            elif tt[0] == tt[2] and tt[1] == tt[3]:
                hit = (g, b, tt[0], tt[1])
            elif tt[0] == tt[1] and tt[2] == tt[3]:
                hit = (g, a, tt[0], tt[2])
            if hit:
                break
        if hit is None:
            return G, out, out_pol
        g, src, h0, h1 = hit
        if h0 == h1:
            raise Reject("constant gate")
        G, out, out_pol = rewire(G, out, out_pol, {g: (src, h0)})   # g = src XOR h0
        del G[g]


def rewire(G, out, out_pol, repl):
    """Replace every read of node o by (node, pol) = repl[o], adjusting tt for complemented inputs."""
    G2 = {}
    for g, (a, b, tt) in G.items():
        if a in repl:
            a, p = repl[a]
            if p:
                tt = (tt[2], tt[3], tt[0], tt[1])
        if b in repl:
            b, p = repl[b]
            if p:
                tt = (tt[1], tt[0], tt[3], tt[2])
        G2[g] = [a, b, tuple(tt)]
    if out in repl:
        out, p = repl[out]
        out_pol ^= p
    return G2, out, out_pol


# ------------------------------------------------------------------ windows
def windows(G, order, n, out, max_size):
    """Connected (as an undirected graph) convex gate sets with 2..max_size gates, smallest first.
    Yields (W, inputs, outputs, descendants of W outside W)."""
    adj = {g: set() for g in order}
    cons = {g: set() for g in order}
    for g in order:
        for p in G[g][:2]:
            if p >= n:
                adj[g].add(p)
                adj[p].add(g)
                cons[p].add(g)
    level = {frozenset([g]) for g in order}
    for size in range(2, max_size + 1):
        nxt = set()
        for W in level:
            for g in W:
                for h in adj[g]:
                    if h not in W:
                        nxt.add(W | {h})
        level = nxt
        for W in sorted(level, key=lambda s: sorted(s)):
            ins = {p for g in W for p in G[g][:2]} - W
            desc, stack = set(), [c for g in W for c in cons[g] if c not in W]
            while stack:
                v = stack.pop()
                if v not in desc:
                    desc.add(v)
                    stack += list(cons[v])
            if ins & desc:
                continue                                   # not convex
            outs = sorted(g for g in W if g == out or cons[g] - W)
            yield W, sorted(ins), outs, desc


# ------------------------------------------------------------------ multi-output synthesis on a care set
def synthesize(m, rows, n_out, k, basis, solver="cadical195", budget=None, phases_seed=None):
    """rows: list of (input bits, output bits) -- the care set. Find k gates over m inputs such that
    every output equals some node, possibly complemented, on every care row.
    Returns (gates [(p, q, tt)], outmap [(node, pol)]) with nodes 0..m-1 the inputs, or None
    (no such circuit, or none found within the conflict budget)."""
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    from pysat.solvers import Solver
    pool, cls, R = IDPool(), [], len(rows)
    sel, f, x = [], [], []
    for t in range(k):
        i = m + t
        sel.append({(p, q): pool.id(("s", t, p, q)) for p in range(i) for q in range(p + 1, i)})
        f.append([pool.id(("f", t, ab)) for ab in range(4)])
        x.append([pool.id(("x", t, r)) for r in range(R)])
    for t in range(k):
        cls += CardEnc.equals(list(sel[t].values()), 1, vpool=pool, encoding=EncType.seqcounter).clauses
        cls += [[-f[t][ab] if pat[ab] else f[t][ab] for ab in range(4)] for pat in FORBIDDEN[basis]]
        for (p, q), s in sel[t].items():
            for r in range(R):
                for a in (0, 1):
                    if p < m and rows[r][0][p] != a:
                        continue
                    for b in (0, 1):
                        if q < m and rows[r][0][q] != b:
                            continue
                        base = [-s]
                        if p >= m:
                            base.append(x[p - m][r] if a == 0 else -x[p - m][r])
                        if q >= m:
                            base.append(x[q - m][r] if b == 0 else -x[q - m][r])
                        fv, xv = f[t][2 * a + b], x[t][r]
                        cls += [base + [-xv, fv], base + [xv, -fv]]
    ys = []
    for o in range(n_out):
        cand = []
        for node in range(m + k):
            for pol in (0, 1):
                if node < m:
                    if all((row[0][node] ^ pol) == row[1][o] for row in rows):
                        cand.append(((node, pol), None))
                    continue
                y = pool.id(("y", o, node, pol))
                cand.append(((node, pol), y))
                for r, row in enumerate(rows):
                    xv = x[node - m][r]
                    cls.append([-y, xv if row[1][o] ^ pol else -xv])
        if any(y is None for _, y in cand):
            ys.append([c for c in cand if c[1] is None][:1])         # an input already provides it
            continue
        if not cand:
            return None
        cls.append([y for _, y in cand])
        ys.append(cand)
    if k == 0:
        return ([], [c[0][0] for c in ys]) if all(c and c[0][1] is None for c in ys) else None
    with Solver(name=solver, bootstrap_with=cls) as S:
        if phases_seed is not None:
            import random
            r = random.Random(phases_seed)
            S.set_phases([v if r.random() < 0.5 else -v for v in range(1, pool.top + 1)])
        if budget:
            S.conf_budget(budget)
        if (S.solve_limited() if budget else S.solve()) is not True:
            return None
        model = set(v for v in S.get_model() if v > 0)
    gates = []
    for t in range(k):
        (p, q), = [pq for pq, s in sel[t].items() if s in model]
        gates.append((p, q, tuple(int(v in model) for v in f[t])))
    outmap = []
    for cand in ys:
        outmap.append(next(nd for nd, y in cand if y is None or y in model))
    return gates, outmap


# ------------------------------------------------------------------ the improvement loop
def care_rows(n, val, ins, outs):
    """The care set of a window: each combination of its input values that occurs on some row,
    with the output values on that row (they are functions of the inputs, so they agree)."""
    care = {}
    for t in range(1 << n):
        key = tuple((val[i] >> t) & 1 for i in ins)
        assert care.setdefault(key, tuple((val[g] >> t) & 1 for g in outs)) == care[key]
    return sorted(care.items())


def replace(n, G, out, out_pol, W, ins, outs, sol, next_id):
    """Replace window W by the synthesized gates; returns (G, out, out_pol, next_id). Raises Reject."""
    new_gates, outmap = sol
    G2 = {g: v for g, v in G.items() if g not in W}
    ids, nid = list(ins), next_id
    for (p, q, tt) in new_gates:
        G2[nid] = [ids[p], ids[q], tt]
        ids.append(nid)
        nid += 1
    G2, out2, pol2 = rewire(G2, out, out_pol, {o: (ids[nd], pol) for o, (nd, pol) in zip(outs, outmap)})
    G2, out2, pol2 = simplify(G2, out2, pol2, n)
    if out2 < n:
        raise Reject("the output became an input")    # a chain needs at least one gate
    return {g: G2[g] for g in topo(G2, out2, n)}, out2, pol2, nid


def improve(n, target, gates, basis, max_window=7, max_inputs=9, solver="cadical195", log=print, deadline=None,
            budget=None, plateau=0, seed=0, resub=0):
    """Greedy local improvement: replace a window by a strictly smaller one while possible. With
    plateau > 0, when no window shrinks, up to that many times replace a random window by one of the
    same size that changes the set of gate functions (randomized solver phases), then continue.
    With resub = r > 0, the replacement of a window of at most r gates may read every node that is not
    a descendant of the window (resubstitution), not only the window's own inputs; the circuit stays
    acyclic because none of those nodes depends on the window.
    Returns a verified chain."""
    import random
    rng = random.Random(seed)
    full = full_mask(n)
    tmask = sum(1 << t for t in range(1 << n) if target[t])
    G, out, out_pol = from_chain(n, gates)
    G = {g: G[g] for g in topo(G, out, n)}
    next_id = max(G) + 1

    def check(G2, out2, pol2):
        v = evaluate(n, G2, topo(G2, out2, n))[out2] ^ (full if pol2 else 0)
        if v not in (tmask, full ^ tmask):
            raise AssertionError("replacement changed the function")   # would be a bug

    def signature(G2, out2):
        val2 = evaluate(n, G2, topo(G2, out2, n))
        return frozenset(min(val2[g], full ^ val2[g]) for g in G2)

    moves = 0
    while not (deadline and time.time() > deadline):
        order = topo(G, out, n)
        val = evaluate(n, G, order)
        check(G, out, out_pol)
        cands = list(windows(G, order, n, out, max_window))
        best = None
        for W, ins, outs, desc in cands:
            if deadline and time.time() > deadline:
                break
            if len(W) <= resub:
                ins = sorted((set(range(n)) | set(order)) - W - desc)
            elif len(ins) > max_inputs:
                continue
            rows = care_rows(n, val, ins, outs)
            k, sol = len(W) - 1, None
            while k >= 0:
                s = synthesize(len(ins), rows, len(outs), k, basis, solver, budget)
                if s is None:
                    break
                sol, k = s, k - 1
            if sol is None:
                continue
            try:
                G2, out2, pol2, nid = replace(n, G, out, out_pol, W, ins, outs, sol, next_id)
            except Reject:
                continue
            check(G2, out2, pol2)
            if len(G2) < len(G):
                best = (G2, out2, pol2, nid)
                log(f"  window of {len(W)} gates -> {len(sol[0])}: circuit now {len(G2)} gates"
                    + (f" (after {moves} plateau moves)" if moves else ""))
                break
        if best is None and moves < plateau:
            sig = signature(G, out)
            rng.shuffle(cands)
            for W, ins, outs, desc in [c for c in cands if len(c[1]) <= max_inputs][:60]:
                sol = synthesize(len(ins), care_rows(n, val, ins, outs), len(outs), len(W), basis, solver, budget,
                                 phases_seed=rng.random())
                if sol is None:
                    continue
                try:
                    G2, out2, pol2, nid = replace(n, G, out, out_pol, W, ins, outs, sol, next_id)
                except Reject:
                    continue
                check(G2, out2, pol2)
                if len(G2) <= len(G) and signature(G2, out2) != sig:
                    best, moves = (G2, out2, pol2, nid), moves + 1
                    if len(G2) < len(G):
                        log(f"  plateau move {moves} shrank the circuit to {len(G2)} gates")
                    break
        if best is None:
            break
        G, out, out_pol, next_id = best
    chain = to_chain(n, G, out, out_pol)
    assert E.verify(n, target, chain)
    if basis == "U2":
        assert all(g[3] != (0, 1, 1, 0) for g in chain)
    return chain


def start_circuit(name, basis, start):
    full, n, tt = C.suite_function(name)
    if start in ("suite", "b2opt"):
        if basis == "U2" and start == "suite":
            rec = [d for d in json.load(open(os.path.join(R, "u2_suite.json"))) if d["name"] == full][0]
            return rec["gates"], "results/u2_suite.json"
        fin = {(e["name"], e["basis"]): e for e in json.load(open(os.path.join(R, "explicit_final.json")))["functions"]}
        src = fin[(full, "B2" if start == "b2opt" else basis)]
        g = src["gates"]
        if basis == "U2":
            import certify_u2_suite as U
            return U.expand_xors(name, g), "XOR expansion of the B2 circuit in results/explicit_final.json"
        return g, "results/explicit_final.json"
    d = json.load(open(start))
    g = d["gates"]
    if basis == "U2" and d.get("basis") == "B2":
        import certify_u2_suite as U
        return U.expand_xors(name, g), f"XOR expansion of {os.path.basename(start)}"
    return g, os.path.basename(start)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name")
    ap.add_argument("basis", choices=["B2", "U2"])
    ap.add_argument("--start", default="suite")
    ap.add_argument("--max-window", type=int, default=7)
    ap.add_argument("--max-inputs", type=int, default=9)
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--minutes", type=float, help="stop looking for improvements after this long")
    ap.add_argument("--budget", type=int, help="conflict budget per SAT call (unknown counts as no improvement)")
    ap.add_argument("--plateau", type=int, default=0, help="allow this many same-size random replacements")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--resub", type=int, default=0,
                    help="windows of at most this many gates may read every non-descendant node")
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()
    full, n, tt = C.suite_function(a.name)
    gates, source = start_circuit(a.name, a.basis, a.start)
    gates = [(g[0], g[1], g[2], tuple(g[3])) for g in gates]
    assert E.verify(n, tt, gates)
    print(f"{full} ({a.basis}): start {len(gates)} gates from {source}", flush=True)
    t0 = time.time()
    chain = improve(n, tt, gates, a.basis, a.max_window, a.max_inputs, a.solver,
                    log=lambda s: print(s, flush=True), deadline=t0 + 60 * a.minutes if a.minutes else None,
                    budget=a.budget, plateau=a.plateau, seed=a.seed, resub=a.resub)
    print(f"result: {len(chain)} gates in {time.time() - t0:.0f}s: {E.gates_to_str(n, chain)}")
    print(json.dumps({"name": full, "basis": a.basis, "gates": [list(g[:3]) + [list(g[3])] for g in chain]}))
    if a.record and a.basis == "U2" and len(chain) < len(gates):
        import certify_u2_suite as U
        U.record_upper(a.name, chain, f"local_improve.py (window <= {a.max_window}, inputs <= {a.max_inputs}) from {source}")
