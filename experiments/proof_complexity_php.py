#!/usr/bin/env python3
"""
proof_complexity_php.py -- CDCL (a Resolution-based prover) on two unsatisfiable families.

  PHP_n : pigeonhole principle, n+1 pigeons into n holes.  Haken (1985): every Resolution
          refutation has size 2^{Omega(n)}.  Since CDCL solvers with clause learning produce
          Resolution refutations, their running time on PHP_n must grow exponentially.
  GT_n  : the ordering principle ("every finite total order has a least element").  It has
          polynomial-size Resolution refutations (Stalmarck 1996), so CDCL *can* be fast on it.

This is the empirical face of Cook-Reckhow: NP = coNP iff some proof system is polynomially
bounded; Resolution is provably not, and a SAT solver inherits that lower bound.
"""
import json, os, time
from pysat.solvers import Solver
from pysat.formula import CNF

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
os.makedirs(RESULTS, exist_ok=True)

def php(n):
    """n+1 pigeons, n holes. var p(i,j) = 1 + i*n + j."""
    p = lambda i, j: 1 + i * n + j
    cnf = CNF()
    for i in range(n + 1):
        cnf.append([p(i, j) for j in range(n)])            # pigeon i sits somewhere
    for j in range(n):
        for i in range(n + 1):
            for i2 in range(i + 1, n + 1):
                cnf.append([-p(i, j), -p(i2, j)])          # hole j holds at most one pigeon
    return cnf

def gt(n):
    """Ordering principle on n elements: var x(i,j) means i<j (i!=j).
    Clauses: antisymmetry, transitivity, totality, and 'no minimal element'."""
    idx = {}
    k = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                k += 1; idx[(i, j)] = k
    x = lambda i, j: idx[(i, j)]
    cnf = CNF()
    for i in range(n):
        for j in range(n):
            if i == j: continue
            cnf.append([-x(i, j), -x(j, i)])                  # antisymmetry
            cnf.append([x(i, j), x(j, i)])                    # totality
            for l in range(n):
                if l in (i, j): continue
                cnf.append([-x(i, j), -x(j, l), x(i, l)])     # transitivity
    for j in range(n):
        cnf.append([x(i, j) for i in range(n) if i != j])     # every j has a predecessor (no minimum)
    return cnf

def run(name, gen, sizes, time_cap=120.0):
    rows = []
    for n in sizes:
        cnf = gen(n)
        t0 = time.time()
        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as S:
            res = S.solve()
            dt = time.time() - t0
            st = S.accum_stats()
        rows.append({"family": name, "n": n, "vars": cnf.nv, "clauses": len(cnf.clauses), "sat": res,
                     "seconds": round(dt, 3), "conflicts": st.get("conflicts"), "decisions": st.get("decisions")})
        print(f"{name:5s} n={n:3d} vars={cnf.nv:5d} clauses={len(cnf.clauses):6d} sat={res} "
              f"conflicts={st.get('conflicts'):>10} time={dt:8.3f}s", flush=True)
        assert res is False
        if dt > time_cap:
            print(f"   (stopping {name}: exceeded {time_cap}s)")
            break
    return rows

if __name__ == "__main__":
    out = []
    out += run("GT", gt, [10, 20, 30, 40, 50, 60, 70, 80])
    out += run("PHP", php, [6, 7, 8, 9, 10, 11, 12, 13, 14])
    with open(os.path.join(RESULTS, "proof_complexity_php.json"), "w") as fh:
        json.dump(out, fh, indent=1)
