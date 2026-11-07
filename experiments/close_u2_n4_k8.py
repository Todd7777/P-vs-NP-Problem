# Refute 8-gate U2 circuits for the four classes still open in the closure run (one core, sequential).
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exact_circuit_complexity as E
from pysat.solvers import Solver
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'n4_u2_closure_k8.json')
res = []
for canon in [0x1683, 0x1681, 0x166b, 0x1669]:
    tt = E.normalize(E.int_to_tt(canon, 4)); sym = E.depends_on_all(4, tt)
    cls, decode = E.encode(4, tt, 8, basis="U2", symmetry=sym)
    t0 = time.time()
    with Solver(name=E.SOLVER, bootstrap_with=cls) as S:
        S.conf_budget(50_000_000); r = S.solve_limited()
        circ = None
        if r is True:
            g = decode(S.get_model()); assert E.verify(4, tt, g); circ = E.gates_to_str(4, g)
    res.append({"canonical": canon, "k": 8, "result": r, "seconds": round(time.time() - t0, 1), "circuit": circ})
    print(res[-1], flush=True)
    json.dump(res, open(out, 'w'), indent=1)
