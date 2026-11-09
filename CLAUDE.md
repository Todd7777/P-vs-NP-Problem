# CLAUDE.md

Guidance for Claude Code sessions in this repository, local or cloud.

## What this is

An attack dossier on P vs NP: the barrier theorems with proofs, the 2026 frontier, nine attack attempts
followed to their obstructions, 24 open sub-problems, and SAT-based exact circuit-synthesis experiments.
P vs NP is open, and this repository does not resolve it.

## Ground rules

- Do not claim or imply that P vs NP is resolved. Label every new claim as **Theorem** (complete proof here),
  **Machine-checked**, **Cited** (only after reading the source), **Numerical**, or **Conjecture/Heuristic**.
- A proposed proof must meet the barrier specification in `docs/02-barriers.md` before it is worth writing up.
- A pattern in small cases is evidence, not proof. Try to construct a counterexample before building on it.
- Commit verified work in small steps and push before the session ends. Work left only inside a cloud
  session can be lost with it.

## Setup and checks

```bash
pip install -r requirements.txt
pytest                      # about 15 s; RUN_SLOW=1 pytest adds about 30 s of slower checks
cd experiments && python3 -c "import exact_circuit_complexity as E; r = E.cost_bounds(3, E.tt_from_fn(3, lambda r: sum(r) % 2)); assert (r['lower'], r['upper']) == (2, 2); print('ok')"
```

The one-liner checks the first SAT pipeline in about a second (3-input parity has B2 cost 2).
drat-trim is not on PyPI: `git clone https://github.com/marijnheule/drat-trim && make -C drat-trim`,
then put it on `PATH` or set `DRAT_TRIM`; tests that need it are skipped without it. The README's
full runs take much longer.

## State on 2026-11-09

- Of the six intervals the first run left in `experiments/results/explicit_run.log`, four are closed
  and Machine-checked or Theorem: MAJ_5 = 9 and EXACTLY2_5 = 9 (B2), MOD3_4 = 10 (U2), and
  parity_5 = 12 (U2, Schnorr's theorem, docs/05 §5.2). For MOD3_5 and THR2_5 (B2) the 9-gate
  instance is UNSAT according to CaDiCaL and its DRAT proof (about 0.8 GB each) was still being
  checked by drat-trim at the last commit; until that check is recorded they stay [9, 10] in
  `experiments/results/explicit_final.json`. Knuth's table gives 10 for both.
- Lower bounds come from `experiments/circuit_sat.py` (symmetry-reduced encoding; soundness proof in
  `experiments/ENCODING.md`) with DRAT proofs checked by drat-trim. The proofs are not committed
  (about 2 GB): `certify_costs.py recheck` regenerates them bit for bit and checks them again.
- Every B2 value agrees with Knuth's table of optimal 5-input chains, as packaged by optimal5 and
  parsed by `experiments/compare_optimal5.py`. No published value was found for MOD3_4 in U2;
  `crosscheck_old_encoding.py` re-derives its refutations with the first, independently written encoding.
- `summarize_u2_n4.py` cannot be rerun: its input `results/n4_u2_closure.json` was never committed.
  `certify_n4_u2.py` replaces it (the four 4-input U2 classes it left open).
- The session that wrote the docs could not fetch arXiv, ECCC or the ACM DL. Citations it could not verify
  are marked **[U]** and still need checking. On 2026-11-09 arXiv and gitlab.com were reachable through
  the proxy; Knuth's Stanford pages failed TLS verification, so TAOCP itself was not consulted.

## Where the next steps are

`docs/07-open-subproblems.md` (24 sub-problems in three tiers) and `docs/04-attack-vectors.md`
(the next lemma for each attack vector).
