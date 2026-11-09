#!/usr/bin/env python3
"""
brute_force.py -- exhaustive enumeration of Boolean chains, used to cross-check the SAT encodings.

It shares no code with the SAT encodings. A depth-first search lists every chain of at most
`kmax` gates over n inputs, where each gate reads two distinct earlier nodes and applies one of
the normal, nontrivial operators of the basis (B2: AND, a&~b, ~a&b, XOR, OR; U2: the same without
XOR). For every function that appears at some gate it records the least number of gates needed.
Normal operators lose nothing (Knuth, TAOCP 4A §7.1.2): complementing a gate's output can be
absorbed by the gates that read it, and output complementation is free in the cost model, so
cost(f) = cost of the normal member of {f, not f}.

Truth tables are integers: bit t is the value on input row t, where x_a = bit a of t.
"""

OPS = {"B2": [(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)],
       "U2": [(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)]}


def input_tables(n):
    return [sum(((t >> a) & 1) << t for t in range(1 << n)) for a in range(n)]


def chain_costs(n, kmax, basis="B2"):
    """Dict: normal truth table -> least number of gates (<= kmax) of a chain with that function
    at some gate. Inputs and the constant 0 have cost 0."""
    full = (1 << (1 << n)) - 1
    ops = OPS[basis]
    nodes = input_tables(n)
    best = {x: 0 for x in nodes}
    best[0] = 0

    def gate(op, A, B):
        f01, f10, f11 = op
        r = 0
        if f01:
            r |= ~A & B
        if f10:
            r |= A & ~B
        if f11:
            r |= A & B
        return r & full

    def dfs(depth):
        m = len(nodes)
        for l in range(1, m):
            B = nodes[l]
            for j in range(l):
                A = nodes[j]
                for op in ops:
                    g = gate(op, A, B)
                    if best.get(g, kmax + 1) > depth:
                        best[g] = depth
                    if depth < kmax:
                        nodes.append(g)
                        dfs(depth + 1)
                        nodes.pop()

    if kmax >= 1:
        dfs(1)
    return best


def cost_of(n, tt_bits, table):
    """Cost of the function with truth-table list tt_bits, looked up in a chain_costs table
    (None if it is above the table's kmax)."""
    x = sum(b << t for t, b in enumerate(tt_bits))
    if x & 1:
        x ^= (1 << (1 << n)) - 1
    return table.get(x)
