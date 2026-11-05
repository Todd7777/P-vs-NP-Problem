#!/usr/bin/env python3
"""
exact_circuit_complexity.py  --  exact circuit complexity of small Boolean functions via SAT.

Model (Knuth, TAOCP Vol. 4A, Sec. 7.1.2 convention)
-------------------------------------------------
A circuit ("chain") over inputs x_1..x_n is a sequence of 2-input gates; every gate computes an
arbitrary binary Boolean function of its two inputs (basis B2 = all 16 binary functions), or a
function from the restricted basis U2 = B2 minus {XOR, XNOR}.  The cost C(f) is the minimum number
of gates in a chain computing f *or its complement* (output negation is free: complement the last
gate's operator; input negation is free too, since it is absorbed by every gate reading it; hence
C is invariant under the NPN group).  We use Knuth's "normal chain" trick: every gate g satisfies
g(0,0)=0, so every wire is a normal function, and we synthesise the normal one of {f, not f}.

Encoding: exact synthesis in the style of Kojevnikov, Kulikov, Yaroslavtsev (SAT 2009) / Knuth.
Per gate i: selection variables s[i][(j,l)] (inputs are nodes j<l<i), three function bits
f[i][01], f[i][10], f[i][11], and value variables v[i][t] for every nonzero truth-table row t.
Symmetry breaking used (all sound for minimum-size chains): no constant/projection gates; every
non-output gate is used; no two gates are identical (same inputs, same operator); the output is
the last gate.

A SAT answer at k gates gives the upper bound C(f) <= k (with an explicit circuit); an UNSAT answer
at k gives C(f) >= k+1.  When a conflict budget runs out at some k we keep going upward and report
an interval [lower, upper] honestly.

Usage
-----
  python3 exact_circuit_complexity.py n4         # all 222 NPN classes of 4-input functions
  python3 exact_circuit_complexity.py explicit   # explicit 4/5-input functions (parallel workers)
  python3 exact_circuit_complexity.py all
"""
import itertools, json, sys, time, os
from multiprocessing import Pool
import numpy as np
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
os.makedirs(RESULTS, exist_ok=True)
SOLVER = "cadical195"

class VarPool:
    def __init__(self): self.n = 0
    def new(self):
        self.n += 1; return self.n

def truth_rows(n):
    """Row t (0..2^n-1) has x_j = bit j of t."""
    return [[(t >> j) & 1 for j in range(n)] for t in range(1 << n)]

def encode(n, target, k, basis="B2", symmetry=True):
    assert target[0] == 0
    rows = truth_rows(n)
    R = range(1, 1 << n)
    N = n + k
    vp = VarPool()
    s, f, v = {}, {}, {}
    for i in range(n, N):
        s[i] = {(j, l): vp.new() for j in range(i) for l in range(j + 1, i)}
        f[i] = {ab: vp.new() for ab in [(0, 1), (1, 0), (1, 1)]}
        v[i] = {t: vp.new() for t in R}
    cls = []
    def val_lit(node, t, want):
        if node < n:
            return (rows[t][node] == want)
        return v[node][t] if want else -v[node][t]
    for i in range(n, N):
        cls.append(list(s[i].values()))
        pairs = list(s[i].keys())
        for p in range(len(pairs)):
            for q in range(p + 1, len(pairs)):
                cls.append([-s[i][pairs[p]], -s[i][pairs[q]]])
        for (j, l), sv in s[i].items():
            for t in R:
                for a in (0, 1):
                    for b in (0, 1):
                        la = val_lit(j, t, a); lb = val_lit(l, t, b)
                        if la is False or lb is False:
                            continue
                        base = [-sv]
                        if la is not True: base.append(-la)
                        if lb is not True: base.append(-lb)
                        if (a, b) == (0, 0):
                            cls.append(base + [-v[i][t]])
                        else:
                            cls.append(base + [-v[i][t], f[i][(a, b)]])
                            cls.append(base + [v[i][t], -f[i][(a, b)]])
        f01, f10, f11 = f[i][(0, 1)], f[i][(1, 0)], f[i][(1, 1)]
        cls.append([f01, f10, f11])          # not constant 0
        cls.append([f01, -f10, -f11])        # not projection on first input
        cls.append([-f01, f10, -f11])        # not projection on second input
        if basis == "U2":
            cls.append([-f01, -f10, f11])    # exclude XOR
    last = N - 1
    for t in R:
        cls.append([v[last][t] if target[t] else -v[last][t]])
    if symmetry:
        for i in range(n, N - 1):            # every non-output gate is used later
            cls.append([s[i2][(j, l)] for i2 in range(i + 1, N) for (j, l) in s[i2] if i in (j, l)])
        for i in range(n, N):                # no two identical gates
            for i2 in range(i + 1, N):
                for (j, l) in s[i]:
                    if (j, l) in s[i2]:
                        # same inputs -> operators differ
                        cls.append([-s[i][(j, l)], -s[i2][(j, l)],
                                    f[i][(0,1)], f[i2][(0,1)], f[i][(1,0)], f[i2][(1,0)], f[i][(1,1)], f[i2][(1,1)]])
                        # (weak form: at least one bit set somewhere) plus pairwise difference:
                        d = vp.new()
                        # d <-> (f_i != f_i2) is expensive to encode fully; use the simple sound clause set:
                        for ab in [(0,1),(1,0),(1,1)]:
                            pass
                        # The pairwise-difference constraint:  not(s_i & s_i2 & f_i == f_i2).
                        # Encode via 8 clauses over the 3 bits each (one per equal assignment pattern):
                        for bits in itertools.product((0,1), repeat=3):
                            cl = [-s[i][(j, l)], -s[i2][(j, l)]]
                            for (ab, bval) in zip([(0,1),(1,0),(1,1)], bits):
                                cl.append(-f[i][ab] if bval else f[i][ab])
                                cl.append(-f[i2][ab] if bval else f[i2][ab])
                            cls.append(cl)
    def decode(model):
        ms = set(x for x in model if x > 0)
        gates = []
        for i in range(n, N):
            (j, l) = [p for p, var in s[i].items() if var in ms][0]
            tt = (0, int(f[i][(0, 1)] in ms), int(f[i][(1, 0)] in ms), int(f[i][(1, 1)] in ms))
            gates.append((i, j, l, tt))
        return gates
    return cls, decode

def depends_on_all(n, target):
    rows = truth_rows(n)
    for j in range(n):
        if not any(target[t] != target[t | (1 << j)] for t in range(1 << n) if not rows[t][j]):
            return False
    return True

def normalize(target):
    return target if target[0] == 0 else [1 - b for b in target]

def verify(n, target, gates):
    """Independent check that the decoded chain computes target (or its complement)."""
    rows = truth_rows(n)
    out = []
    for t in range(1 << n):
        vals = list(rows[t])
        for (i, j, l, tt) in gates:
            a, b = vals[j], vals[l]
            vals.append(tt[2 * a + b])
        out.append(vals[-1] if gates else None)
    return out == target or out == [1 - b for b in target]

def cost_bounds(n, target, basis="B2", kmax=16, conf_budget=None, verbose=False):
    """Return dict with lower, upper, status ('exact' or 'interval'), circuit, per_k info."""
    target = normalize(target)
    rows = truth_rows(n)
    if all(b == 0 for b in target) or any(all(target[t] == rows[t][j] for t in range(1 << n)) for j in range(n)):
        return {"lower": 0, "upper": 0, "status": "exact", "circuit": [], "per_k": {}}
    sym = depends_on_all(n, target)
    info, lower = {}, 1
    for k in range(1, kmax + 1):
        cls, decode = encode(n, target, k, basis=basis, symmetry=sym)
        t0 = time.time()
        with Solver(name=SOLVER, bootstrap_with=cls) as S:
            if conf_budget:
                S.conf_budget(conf_budget); res = S.solve_limited()
            else:
                res = S.solve()
            dt = time.time() - t0
            info[k] = {"result": res, "seconds": round(dt, 3), "clauses": len(cls)}
            if verbose:
                print(f"   k={k}: {res} ({dt:.2f}s, {len(cls)} clauses)", flush=True)
            if res is True:
                gates = decode(S.get_model())
                assert verify(n, target, gates), "decoded circuit does not compute target!"
                status = "exact" if lower == k else "interval"
                return {"lower": lower, "upper": k, "status": status, "circuit": gates, "per_k": info}
            if res is False and lower == k:
                lower = k + 1          # contiguous UNSAT prefix -> proven lower bound
    return {"lower": lower, "upper": None, "status": "interval", "circuit": [], "per_k": info}

def gates_to_str(n, gates):
    names = {(0,0,0,1):"AND",(0,0,1,0):"x>y",(0,1,0,0):"x<y",(0,1,1,0):"XOR",(0,1,1,1):"OR"}
    out = []
    for (i, j, l, tt) in gates:
        nj = f"x{j+1}" if j < n else f"g{j+1}"
        nl = f"x{l+1}" if l < n else f"g{l+1}"
        out.append(f"g{i+1} = {names.get(tt, str(tt))}({nj},{nl})")
    return "; ".join(out)

# ---------------------------------------------------------------- NPN classes of 4-input functions
def npn_classes(n):
    N = 1 << n
    rows = np.array(truth_rows(n), dtype=np.uint8)
    weights = (1 << np.arange(N)).astype(np.int64)
    F = ((np.arange(1 << N)[:, None] >> np.arange(N)[None, :]) & 1).astype(np.uint8)
    best = np.full(1 << N, (1 << N) - 1, dtype=np.int64)
    for perm in itertools.permutations(range(n)):
        for mask in range(1 << n):
            xp = rows[:, list(perm)] ^ np.array([(mask >> j) & 1 for j in range(n)], dtype=np.uint8)
            idx = (xp * (1 << np.arange(n))).sum(axis=1)
            vals = (F[:, idx].astype(np.int64) * weights).sum(axis=1)
            vals = np.minimum(vals, ((1 << N) - 1) ^ vals)
            best = np.minimum(best, vals)
    canon, counts = np.unique(best, return_counts=True)
    return {int(c): int(cnt) for c, cnt in zip(canon, counts)}

def int_to_tt(x, n):
    return [(x >> t) & 1 for t in range(1 << n)]

def _n4_worker(args):
    c, size = args
    tt = int_to_tt(c, 4)
    rB = cost_bounds(4, tt, "B2")                       # exact, no budget (fast: cost <= 7)
    rU = cost_bounds(4, tt, "U2", conf_budget=400_000)   # bounded effort
    return {"canonical": c, "size": size,
            "cost_B2": rB["upper"], "circuit_B2": gates_to_str(4, rB["circuit"]),
            "U2_lower": rU["lower"], "U2_upper": rU["upper"], "U2_status": rU["status"],
            "circuit_U2": gates_to_str(4, rU["circuit"])}

def run_n4(workers=3):
    print("Computing NPN classes of all 65536 4-input functions ...", flush=True)
    classes = npn_classes(4)
    print(f"  {len(classes)} NPN classes (expected 222)", flush=True)
    KNUTH = [10, 60, 456, 2474, 10624, 24184, 25008, 2720]
    t0 = time.time()
    with Pool(workers) as pool:
        recs = []
        for idx, rec in enumerate(pool.imap_unordered(_n4_worker, sorted(classes.items()))):
            recs.append(rec)
            if idx % 20 == 0:
                print(f"  {idx+1}/{len(classes)} classes done ({time.time()-t0:.0f}s)", flush=True)
    recs.sort(key=lambda r: r["canonical"])
    distB = {}
    for r in recs:
        distB[r["cost_B2"]] = distB.get(r["cost_B2"], 0) + r["size"]
    distB = {int(k): v for k, v in sorted(distB.items())}
    distU_exact = {}; n_interval = 0
    for r in recs:
        if r["U2_status"] == "exact":
            distU_exact[r["U2_upper"]] = distU_exact.get(r["U2_upper"], 0) + r["size"]
        else:
            n_interval += 1
    out = {"n": 4, "classes": recs, "distribution_B2": distB, "knuth_B2": KNUTH,
           "match_knuth": list(distB.values()) == KNUTH,
           "distribution_U2_exact_part": {int(k): v for k, v in sorted(distU_exact.items())},
           "U2_classes_unresolved": n_interval, "seconds": round(time.time() - t0, 1)}
    print("\nDistribution of C_B2(f) over all 65536 functions of 4 variables:")
    print("  cost :", list(distB.keys())); print("  count:", list(distB.values())); print("  Knuth:", KNUTH)
    print("  MATCH" if out["match_knuth"] else "  MISMATCH")
    print(f"U2: exact for {len(recs)-n_interval}/{len(recs)} classes; distribution (exact part):", out["distribution_U2_exact_part"])
    print(f"total time {time.time()-t0:.1f}s")
    with open(os.path.join(RESULTS, "n4_exact_costs.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    return out

# ---------------------------------------------------------------- explicit functions
def tt_from_fn(n, fn):
    return [int(fn(r)) for r in truth_rows(n)]

def explicit_suite():
    S = []
    for n in (2, 3, 4, 5):
        S.append((f"parity_{n}", n, lambda r: sum(r) % 2, ["B2", "U2"]))
    S.append(("MAJ_5", 5, lambda r: sum(r) >= 3, ["B2"]))
    S.append(("MOD3_5 (sum=0 mod 3)", 5, lambda r: sum(r) % 3 == 0, ["B2"]))
    S.append(("MOD3_4 (sum=0 mod 3)", 4, lambda r: sum(r) % 3 == 0, ["B2", "U2"]))
    S.append(("EXACTLY2_5", 5, lambda r: sum(r) == 2, ["B2"]))
    S.append(("THR2_5 (sum>=2)", 5, lambda r: sum(r) >= 2, ["B2"]))
    S.append(("MAJ_3 xor x4 xor x5", 5, lambda r: ((sum(r[:3]) >= 2) ^ r[3] ^ r[4]), ["B2"]))
    S.append(("ADD2 carry-out", 4, lambda r: (r[0] + 2*r[1] + r[2] + 2*r[3]) >> 2 & 1, ["B2"]))
    S.append(("MUL2 bit3", 4, lambda r: ((r[0] + 2*r[1]) * (r[2] + 2*r[3])) >> 3 & 1, ["B2"]))
    S.append(("MUL2 bit2", 4, lambda r: ((r[0] + 2*r[1]) * (r[2] + 2*r[3])) >> 2 & 1, ["B2"]))
    S.append(("MUL2 bit1", 4, lambda r: ((r[0] + 2*r[1]) * (r[2] + 2*r[3])) >> 1 & 1, ["B2"]))
    return S

def _explicit_worker(args):
    name, n, idx, basis, budget = args
    fn = explicit_suite()[idx][2]
    tt = tt_from_fn(n, fn)
    t0 = time.time()
    r = cost_bounds(n, tt, basis, conf_budget=budget)
    r["name"], r["n"], r["basis"] = name, n, basis
    r["circuit"] = gates_to_str(n, r["circuit"]); r["seconds"] = round(time.time() - t0, 1)
    rng = f"= {r['upper']}" if r["status"] == "exact" else f"in [{r['lower']}, {r['upper']}]"
    print(f"{name:28s} n={n} {basis}: cost {rng}  ({r['seconds']}s)  {r['circuit']}", flush=True)
    return r

def run_explicit(workers=3, budget=1_500_000):
    jobs = []
    for idx, (name, n, fn, bases) in enumerate(explicit_suite()):
        for basis in bases:
            jobs.append((name, n, idx, basis, budget))
    with Pool(workers) as pool:
        results = list(pool.imap_unordered(_explicit_worker, jobs))
    results.sort(key=lambda r: (r["n"], r["name"], r["basis"]))
    with open(os.path.join(RESULTS, "explicit_costs.json"), "w") as fh:
        json.dump(results, fh, indent=1)
    return results

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("n4", "all"):
        run_n4()
    if what in ("explicit", "all"):
        run_explicit()
