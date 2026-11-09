#!/usr/bin/env python3
"""
circuit_sat.py -- exact circuit complexity of small Boolean functions with a symmetry-reduced SAT
encoding and checkable UNSAT certificates (binary DRAT proofs, checked with drat-trim).

Cost model
----------
The same model as exact_circuit_complexity.py (Knuth, TAOCP Vol. 4A, Sec. 7.1.2): a chain of
2-input gates over x_1..x_n, each gate from B2 (all 16 binary functions) or U2 (B2 minus XOR and
XNOR). C(f) is the least number of gates in a chain that computes f or its complement; negations
are free. Every chain can be rewritten gate for gate as a *normal* chain (each gate g has
g(0,0) = 0), so we search for a normal chain computing the normal member of {f, not f}.

Encoding
--------
Nodes 0..n-1 are the inputs, nodes n..n+k-1 the gates; the last gate is the output.
  s[i][q]  gate i reads the q-th pair (j, l), j < l < i; pairs are listed in colex order (by l,
           then j), so the index of (j, l) is l(l-1)/2 + j for every gate;
  o[i][q]  order encoding of that index ("index of gate i's pair >= q");
  f[i]     the operator bits (g(0,1), g(1,0), g(1,1));
  v[i][t]  the value of gate i on truth-table row t = 1..2^n-1 (row 0 is 0 in a normal chain).
Base constraints (always on): exactly one pair per gate, the gate semantics (as in Kojevnikov,
Kulikov and Yaroslavtsev, SAT 2009), output = target, and every gate nontrivial (neither constant
nor a projection; in U2 also not XOR).
Symmetry-breaking rules, each switchable for testing (the letters of `rules`):
  A  every gate except the output is read by a later gate, and every input is read;
  D  gate functions are pairwise distinct, nonzero, different from every input, and (except at the
     output) different from the target;
  R  no re-application: if gate i reads (j, l), no later gate reads (j, i) or (l, i);
  L  lex-min numbering: for gates i < m, if both inputs of m are nodes < i, then
     (pair_i, op_i) < (pair_m, op_m) lexicographically (op = the operator bits as a 3-bit number);
  V  for each a such that f is symmetric in x_a and x_{a+1}, x_a is first read no later than
     x_{a+1}.
Soundness (proved in ENCODING.md): if f depends on all n inputs and C(f) = k >= 1, the CNF for k
gates with all rules is satisfiable. So UNSAT for every k < K proves C(f) >= K. The rules are only
claimed sound at k = C(f); for k > C(f) the CNF may be unsatisfiable, and the search never needs it.

Usage
-----
  python3 circuit_sat.py cost NAME BASIS [--proofs DIR]   # NAME from exact_circuit_complexity.explicit_suite()
  python3 circuit_sat.py solve NAME BASIS K [--proofs DIR] [--cube Q1,Q2,...]
"""
import argparse, hashlib, itertools, json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import exact_circuit_complexity as E  # noqa: E402  truth tables, verify(), gates_to_str(), explicit_suite()

DEFAULT_RULES = "ADRLV"
DRAT_TRIM = os.environ.get("DRAT_TRIM") or shutil.which("drat-trim") or os.path.expanduser("~/tools/drat-trim/drat-trim")


# ------------------------------------------------------------------ truth-table helpers
def pair_list(i):
    """All pairs (j, l) with j < l < i, in colex order; (j, l) has index l(l-1)/2 + j."""
    return [(j, l) for l in range(1, i) for j in range(l)]


def pair_index(j, l):
    return l * (l - 1) // 2 + j


def support(n, tt):
    """Indices of the variables that tt depends on."""
    return [a for a in range(n) if any(tt[t] != tt[t ^ (1 << a)] for t in range(1 << n))]


def restrict_to_support(n, tt):
    """(m, tt', sup): tt as a function of its m essential variables x_sup[0], ..., x_sup[m-1]."""
    sup = support(n, tt)
    m = len(sup)
    return m, [tt[sum(((r >> b) & 1) << sup[b] for b in range(m))] for r in range(1 << m)], sup


def symmetric_adjacent_pairs(n, tt):
    """All a such that tt is invariant under exchanging x_a and x_{a+1}."""
    out = []
    for a in range(n - 1):
        def swap(t):
            lo, hi = (t >> a) & 1, (t >> (a + 1)) & 1
            return (t & ~(3 << a)) | (hi << a) | (lo << (a + 1))
        if all(tt[t] == tt[swap(t)] for t in range(1 << n)):
            out.append(a)
    return out


def lex_less(A, B, cond):
    """Clauses for: cond -> A < B lexicographically (A[0] most significant)."""
    cls = []
    w = len(A)
    for p in range(w):
        for vals in itertools.product((0, 1), repeat=p):
            pre = []
            for r, val in enumerate(vals):        # falsify "A[r] = B[r] = val"
                pre += [-A[r], -B[r]] if val else [A[r], B[r]]
            if p < w - 1:
                cls.append([-cond] + pre + [-A[p], B[p]])
            else:
                cls.append([-cond] + pre + [-A[p]])
                cls.append([-cond] + pre + [B[p]])
    return cls


# ------------------------------------------------------------------ the encoding
class Encoding:
    """CNF stating: a normal chain with exactly k gates over basis computes target (target[0] == 0),
    together with the symmetry-breaking rules named in `rules`."""

    def __init__(self, n, target, k, basis="B2", rules=DEFAULT_RULES, sym=None):
        assert basis in ("B2", "U2") and k >= 1
        assert len(target) == 1 << n and target[0] == 0, "target must be normal (value 0 on row 0)"
        if set(rules) & set("ADV"):
            assert support(n, target) == list(range(n)), "rules A, D, V assume the target depends on every input"
        self.n, self.k, self.basis, self.rules = n, k, basis, "".join(sorted(set(rules)))
        self.target = list(target)
        self.sym = symmetric_adjacent_pairs(n, target) if sym is None else list(sym)
        self.nvars, self.clauses = 0, []
        self._build()

    def _new(self):
        self.nvars += 1
        return self.nvars

    def _build(self):
        n, k, rules, C = self.n, self.k, self.rules, self.clauses
        N, last = n + self.k, n + self.k - 1
        G, T = range(n, N), range(1, 1 << n)
        self.pairs = {i: pair_list(i) for i in G}
        s = {i: [self._new() for _ in self.pairs[i]] for i in G}
        f = {i: [self._new() for _ in range(3)] for i in G}
        v = {i: {t: self._new() for t in T} for i in G}
        o = {i: {q: self._new() for q in range(1, len(self.pairs[i]))} for i in G}
        self.s, self.f, self.v, self.o = s, f, v, o

        # exactly one pair per gate (order encoding); the plain at-least-one clause is kept explicitly
        for i in G:
            P = len(self.pairs[i])
            C.append(list(s[i]))
            if P > 1:
                C.append([o[i][1], s[i][0]])
            for q in range(1, P):
                C.append([-s[i][q], o[i][q]])
                if q + 1 < P:
                    C.append([-o[i][q + 1], o[i][q]])
                    C.append([-o[i][q], s[i][q], o[i][q + 1]])
                else:
                    C.append([-o[i][q], s[i][q]])
            for q in range(P - 1):
                C.append([-s[i][q], -o[i][q + 1]])

        # semantics, nontrivial operators, basis
        def lit(node, t, val):
            if node < n:
                return ((t >> node) & 1) == val
            return v[node][t] if val else -v[node][t]
        for i in G:
            f01, f10, f11 = f[i]
            fb = {(0, 1): f01, (1, 0): f10, (1, 1): f11}
            for q, (j, l) in enumerate(self.pairs[i]):
                sv = s[i][q]
                for t in T:
                    for a in (0, 1):
                        la = lit(j, t, a)
                        if la is False:
                            continue
                        for b in (0, 1):
                            lb = lit(l, t, b)
                            if lb is False:
                                continue
                            base = [-sv] + ([] if la is True else [-la]) + ([] if lb is True else [-lb])
                            if (a, b) == (0, 0):
                                C.append(base + [-v[i][t]])
                            else:
                                C.append(base + [-v[i][t], fb[(a, b)]])
                                C.append(base + [v[i][t], -fb[(a, b)]])
            C.append([f01, f10, f11])          # not the constant 0
            C.append([f01, -f10, -f11])        # not g(a,b) = a
            C.append([-f01, f10, -f11])        # not g(a,b) = b
            if self.basis == "U2":
                C.append([-f01, -f10, f11])    # not XOR
        for t in T:
            C.append([v[last][t] if self.target[t] else -v[last][t]])

        if "A" in rules:
            for i in range(n, last):
                C.append([s[m][q] for m in range(i + 1, N) for q, (j, l) in enumerate(self.pairs[m]) if i in (j, l)])
            for a in range(n):
                C.append([s[m][q] for m in G for q, (j, l) in enumerate(self.pairs[m]) if a in (j, l)])

        if "D" in rules:
            for i in G:
                C.append([v[i][t] for t in T])
                for a in range(n):
                    C.append([-v[i][t] if (t >> a) & 1 else v[i][t] for t in T])
                if i != last:
                    C.append([-v[i][t] if self.target[t] else v[i][t] for t in T])
            for i in G:
                for m in range(i + 1, N):
                    ys = []
                    for t in T:
                        y = self._new()
                        ys.append(y)
                        C.append([-y, v[i][t], v[m][t]])
                        C.append([-y, -v[i][t], -v[m][t]])
                    C.append(ys)

        if "R" in rules:
            for i in G:
                for q, (j, l) in enumerate(self.pairs[i]):
                    for m in range(i + 1, N):
                        C.append([-s[i][q], -s[m][pair_index(j, i)]])
                        C.append([-s[i][q], -s[m][pair_index(l, i)]])

        if "L" in rules:
            for i in G:
                P = len(self.pairs[i])
                for m in range(i + 1, N):
                    for q in range(P - 1):
                        C.append([-s[m][q], -o[i][q + 1]])
                    e = self._new()
                    for q in range(P):
                        C.append([-s[i][q], -s[m][q], e])
                    C.extend(lex_less(f[i], f[m], e))

        if "V" in rules:
            for a in self.sym:
                u_prev = None
                for p in G:
                    u = self._new()
                    reads_a = [s[p][q] for q, (j, l) in enumerate(self.pairs[p]) if a in (j, l)]
                    C.append([-u] + ([u_prev] if u_prev else []) + reads_a)
                    for q, (j, l) in enumerate(self.pairs[p]):
                        if a + 1 in (j, l):
                            C.append([-s[p][q], u])
                    u_prev = u

    def decode(self, model):
        pos = set(x for x in model if x > 0)
        gates = []
        for i in range(self.n, self.n + self.k):
            qs = [q for q, var in enumerate(self.s[i]) if var in pos]
            assert len(qs) == 1, "model violates exactly-one"
            j, l = self.pairs[i][qs[0]]
            gates.append((i, j, l, (0,) + tuple(int(var in pos) for var in self.f[i])))
        return gates

    def dimacs(self, extra_units=()):
        cls = self.clauses + [[u] for u in extra_units]
        body = "".join(" ".join(map(str, c)) + " 0\n" for c in cls)
        return f"p cnf {self.nvars} {len(cls)}\n{body}".encode()


# ------------------------------------------------------------------ solving and certificates
def sha256(data_or_path):
    h = hashlib.sha256()
    if isinstance(data_or_path, (bytes, bytearray)):
        h.update(data_or_path)
    else:
        with open(data_or_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    return h.hexdigest()


def run_solver(enc, solver="cadical195", extra_units=(), proof_path=None, budget=None, phases=None):
    """Solve enc (+ unit clauses). Returns dict(result, model, seconds, stats).
    With proof_path, CaDiCaL writes a binary DRAT proof there (UNSAT certificate)."""
    from pysat.solvers import Solver
    clauses = enc.clauses + [[u] for u in extra_units]
    t0 = time.time()
    kw = {}
    if proof_path:
        assert solver.startswith("cadical"), "proof logging is only wired up for CaDiCaL"
        kw["with_proof"] = True
        tempfile.tempdir = os.path.dirname(os.path.abspath(proof_path))
    with Solver(name=solver, bootstrap_with=clauses, **kw) as S:
        if phases:
            S.set_phases(phases)
        if budget:
            S.conf_budget(budget)
            res = S.solve_limited()
        else:
            res = S.solve()
        out = {"result": res, "model": S.get_model() if res is True else None,
               "seconds": round(time.time() - t0, 3)}
        try:
            out["stats"] = S.accum_stats()
        except Exception:
            out["stats"] = {}
        if proof_path and res is False:
            import pysolvers
            inner = S.solver
            pysolvers.flushpr(inner.prfp)
            inner.prfile.seek(0)
            with open(proof_path, "wb") as fh:
                shutil.copyfileobj(inner.prfile, fh, 1 << 22)
    return out


def drat_check(cnf_path, proof_path, timeout=500000, lrat_path=None):
    """Run drat-trim (backward mode, binary proof). Returns dict(verified, seconds, output tail)."""
    if not (DRAT_TRIM and os.path.exists(DRAT_TRIM)):
        return {"verified": None, "seconds": 0, "output": "drat-trim not found"}
    cmd = [DRAT_TRIM, cnf_path, proof_path, "-i", "-w", "-t", str(timeout)]
    if lrat_path:
        cmd += ["-L", lrat_path]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    lines = p.stdout.splitlines()
    return {"verified": "s VERIFIED" in [x.strip() for x in lines], "seconds": round(time.time() - t0, 1),
            "output": "\n".join(lines[-12:])}


def certify(enc, workdir, tag, solver="cadical195", extra_units=(), budget=None, check=True, keep_cnf=True):
    """Solve one instance; on UNSAT keep the CNF + DRAT proof under workdir and check it with drat-trim.
    Returns a JSON-serialisable record (no model)."""
    os.makedirs(workdir, exist_ok=True)
    cnf = enc.dimacs(extra_units)
    cnf_path = os.path.join(workdir, tag + ".cnf")
    proof_path = os.path.join(workdir, tag + ".drat")
    with open(cnf_path, "wb") as fh:
        fh.write(cnf)
    r = run_solver(enc, solver, extra_units, proof_path=proof_path, budget=budget)
    rec = {"tag": tag, "n": enc.n, "k": enc.k, "basis": enc.basis, "rules": enc.rules, "units": list(extra_units),
           "nvars": enc.nvars, "nclauses": len(enc.clauses) + len(extra_units), "cnf_sha256": sha256(cnf),
           "solver": solver, "result": r["result"], "solve_seconds": r["seconds"], "stats": r["stats"]}
    if r["result"] is True:
        gates = enc.decode(r["model"])
        assert E.verify(enc.n, enc.target, gates), "decoded circuit does not compute the target"
        rec["circuit"] = E.gates_to_str(enc.n, gates)
        rec["gates"] = gates
    if r["result"] is False:
        rec["proof_bytes"] = os.path.getsize(proof_path)
        rec["proof_sha256"] = sha256(proof_path)
        if check:
            rec["drat_trim"] = drat_check(cnf_path, proof_path)
    if r["result"] is not False and os.path.exists(proof_path):
        os.remove(proof_path)
    if not keep_cnf and r["result"] is not False:
        os.remove(cnf_path)
    return rec


# ------------------------------------------------------------------ cost search
def lift_gates(n, sup, m, gates):
    """Map a chain over the m essential variables back to the original n variables."""
    def node(x):
        return sup[x] if x < m else x + (n - m)
    return [(i + (n - m), node(j), node(l), tt) for (i, j, l, tt) in gates]


def cost(n, tt, basis="B2", kmax=20, solver="cadical195", rules=DEFAULT_RULES, budget=None, verbose=False):
    """Exact cost (no proofs): smallest k whose CNF is SAT; every smaller k must be UNSAT.
    Returns dict(lower, upper, status, circuit, per_k)."""
    tt = E.normalize(list(tt))
    m, rtt, sup = restrict_to_support(n, tt)
    if m <= 1:
        return {"lower": 0, "upper": 0, "status": "exact", "circuit": [], "per_k": {}}
    lower, per_k = 1, {}
    for k in range(1, kmax + 1):
        enc = Encoding(m, rtt, k, basis, rules)
        r = run_solver(enc, solver, budget=budget)
        per_k[k] = {"result": r["result"], "seconds": r["seconds"]}
        if verbose:
            print(f"   k={k}: {r['result']} ({r['seconds']}s, {enc.nvars} vars, {len(enc.clauses)} clauses)", flush=True)
        if r["result"] is True:
            gates = lift_gates(n, sup, m, enc.decode(r["model"]))
            assert E.verify(n, tt, gates), "decoded circuit does not compute the target"
            return {"lower": lower, "upper": k, "status": "exact" if lower == k else "interval",
                    "circuit": gates, "per_k": per_k}
        if r["result"] is False and lower == k:
            lower = k + 1
    return {"lower": lower, "upper": None, "status": "interval", "circuit": [], "per_k": per_k}


def suite_function(name):
    for nm, n, fn, bases in E.explicit_suite():
        if nm == name or nm.split(" ")[0] == name:
            return nm, n, E.normalize(E.tt_from_fn(n, fn))
    raise KeyError(name)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["cost", "solve"])
    ap.add_argument("name")
    ap.add_argument("basis", choices=["B2", "U2"])
    ap.add_argument("k", nargs="?", type=int)
    ap.add_argument("--proofs", help="directory for CNF + DRAT files (solve only)")
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--rules", default=DEFAULT_RULES)
    ap.add_argument("--budget", type=int)
    ap.add_argument("--cube", default="", help="comma-separated unit literals added to the CNF")
    a = ap.parse_args(argv)
    full, n, tt = suite_function(a.name)
    if a.cmd == "cost":
        r = cost(n, tt, a.basis, solver=a.solver, rules=a.rules, budget=a.budget, verbose=True)
        print(full, a.basis, r["lower"], r["upper"], r["status"], E.gates_to_str(n, r["circuit"]))
        return
    m, rtt, sup = restrict_to_support(n, tt)
    assert m == n
    enc = Encoding(n, tt, a.k, a.basis, a.rules)
    units = [int(x) for x in a.cube.split(",") if x]
    if a.proofs:
        tag = f"{full.split(' ')[0]}_{a.basis}_k{a.k}" + (f"_cube{'_'.join(map(str, units))}" if units else "")
        rec = certify(enc, a.proofs, tag, a.solver, units, a.budget)
        rec.pop("gates", None)
        print(json.dumps(rec, indent=1))
    else:
        r = run_solver(enc, a.solver, units, budget=a.budget)
        print(full, a.basis, "k =", a.k, r["result"], r["seconds"], "s", r["stats"])
        if r["result"] is True:
            print(E.gates_to_str(n, enc.decode(r["model"])))


if __name__ == "__main__":
    main()
