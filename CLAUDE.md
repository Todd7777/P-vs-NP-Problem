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

- Every cost in `experiments/results/explicit_final.json` is exact and labelled Theorem or
  Machine-checked. The six intervals the first run left in `experiments/results/explicit_run.log`
  closed as MAJ_5 = 9, EXACTLY2_5 = 9, MOD3_5 = 10 and THR2_5 = 10 (B2), MOD3_4 = 10 (U2), and
  parity_5 = 12 (U2; Schnorr's theorem, docs/05 §5.2). Every B2 value agrees with Knuth's table of
  optimal 5-input chains (optimal5, parsed by `experiments/compare_optimal5.py`). No published value
  was found for MOD3_4 in U2. `crosscheck_old_encoding.py` independently re-derived its lower bound with
  the first encoding (elementary symmetry breaking only): k = 1..8 directly and k = 9 as 60 cubes, every
  proof checked by drat-trim (26 minutes on 4 cores for the cubes).
- Lower bounds come from `experiments/circuit_sat.py` (symmetry-reduced encoding; soundness proof in
  `experiments/ENCODING.md`) with DRAT proofs checked by drat-trim. The two 9-gate B2 refutations took
  about 16 minutes each to solve and about 50 minutes each to check (proofs of 0.8 GB). The proofs are
  not committed (about 2 GB); `certify_costs.py recheck` regenerates them bit for bit and checks them again.
- The U2 cost of all 65,536 functions of 4 variables is now complete (`results/n4_u2_complete.json`):
  the four NPN classes the earlier runs left open all cost 10 (`certify_n4_u2.py`, checked proofs).
  `summarize_u2_n4.py` cannot be rerun, because its input `results/n4_u2_closure.json` was never committed.
- Every citation the first session marked **[U]** was checked at its source on 2026-11-10 (verification
  log at the end of `docs/bibliography.md`); no [U] marker remains. Corrections included the
  Mishra–Santhanam preprint (ECCC TR26-260), whose 3 Nov 2026 revision claims a 4n − O(log n) B2 bound,
  and the Wesonga Lean paper, which does not cover Razborov–Smolensky. Reachable through the proxy:
  arXiv (pages and API), gitlab.com, Dagstuhl LIPIcs, acm-stoc.org, and ECCC through the WebFetch tool
  (curl gets empty replies). Not reachable: DBLP (bot check), the ACM DL, and Knuth's Stanford pages
  (TLS failure), so TAOCP itself was not consulted.

## Where the next steps are

`docs/07-open-subproblems.md` (24 sub-problems in three tiers) and `docs/04-attack-vectors.md`
(the next lemma for each attack vector).
