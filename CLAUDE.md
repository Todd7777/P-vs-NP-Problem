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
pip install python-sat numpy
cd experiments && python3 -c "import exact_circuit_complexity as E; r = E.cost_bounds(3, E.tt_from_fn(3, lambda r: sum(r) % 2)); assert (r['lower'], r['upper']) == (2, 2); print('ok')"
```

There is no test suite yet. The line above checks the SAT pipeline in about a second (3-input parity has
B2 cost 2). The README's full runs take much longer.

## State on 2026-11-08

- Six functions in `experiments/results/explicit_run.log` still have cost intervals because the SAT budget
  ran out: MOD3_5, MAJ_5, EXACTLY2_5 and THR2_5 in B2, and parity_5 and MOD3_4 in U2.
- The session that wrote the docs could not fetch arXiv, ECCC or the ACM DL. Citations it could not verify
  are marked **[U]** and still need checking.
- There is no requirements file, so the README's install line is the reference. A stray
  `experiments/__pycache__/*.pyc` is tracked and should be removed.

## Where the next steps are

`docs/07-open-subproblems.md` (24 sub-problems in three tiers) and `docs/04-attack-vectors.md`
(the next lemma for each attack vector).
