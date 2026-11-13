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
- U2 costs for the rest of the explicit suite (`experiments/certify_u2_suite.py`, `results/u2_suite.json`):
  Machine-checked MUL2 bit3 = 3, MUL2 bit2 = 3, ADD2 carry-out = 5, MUL2 bit1 = 5, MAJ_3 xor x4 xor x5 = 10,
  MAJ_5 = 10, THR2_5 = 10. Open: EXACTLY2_5 in [13, 14] and MOD3_5 in [13, 15], with Machine-checked lower
  bounds. k = 11 was refuted cube by cube with drat-trim-verified proofs (`certify_cubes.py`,
  `results/cube_certificates.json`): 35 cubes for EXACTLY2_5 (its cube where gate 6 reads (x3,x4) needed
  a second split, `--refine 5:7`) and 15 for MOD3_5; about 8.4 and 5.8 CPU-hours including drat-trim;
  proofs 8.2 and 4.6 GB, not committed. The upper bounds are verified circuits. EXACTLY2_5: Kissat's
  15-gate circuit (k = 15, base constraints) shrunk to 14 by `local_improve.py` (SAT-based local
  improvement; a window's replacement only has to agree on the input combinations that occur). MOD3_5:
  the XOR expansion of a 12-gate B2 circuit with 2 XORs, one dead gate pruned (`upper_bound_search.py
  --max-xor`). Local improvement over every window of up to 10 gates (<= 11 inputs, 200k conflicts per
  call) improves neither circuit; windows of up to 9 gates do not improve MOD3_5's other 15-gate
  circuit (expansion of a 13-gate B2 circuit with one XOR), and windows of up to 8 take the expansion of
  EXACTLY2_5's optimal B2 circuit only from 21 to 17.
  Without result in 30-60 min: EXACTLY2_5 B2 with (10 gates, <= 2 XORs) and (11, <= 1); MOD3_5 B2 with
  (12, <= 1) and (10, <= 3); relaxed U2 searches at k = 13-19. k = 12 for MOD3_5, gauged without proofs
  (Numerical): split on gate 6, and the five hard cubes again on gate 7, gives 115 cubes; 74 are refuted
  (71 within seconds), 41 are undecided at 6M conflicts each (about 14 min), and none has a circuit.
- MOD3_5 >= 13 in U2 is Machine-checked with gate-elimination constraints (`elimination.py`,
  ENCODING.md §5: Lemma 5, Theorem 2). Fixing x_v = c deletes every gate reading x_v, and the readers of
  a gate that c makes constant, so a k-gate chain has |N(v)| <= k - C(f|x_v=c) and |N(v) u S(g)| <=
  k - C(f|x_v=c) when c kills g. Restriction costs certified by `certify_restrictions.py`
  (`results/restriction_costs.json`): MOD3_4 = 10, EXACTLY2_4 = 9, EXACTLY1_4 = 9. `certify_cubes.py
  MOD3_5 U2 12 --refine 0:7,1:7,2:7,5:7,12:7 --elim`: 115 cubes, 606 s solving + 800 s drat-trim, 1.1 GB
  of proofs (not committed), hardest cube 97 s. Validation: the constrained CNF stays satisfiable at
  k = C(f) for all 218 relevant 3-input functions (in tests) and 89 4-input ones (scratch run). Local
  improvement with plateau moves and resubstitution (`--plateau`, `--resub`) found nothing below 15
  for MOD3_5 (four starting circuits) or 14 for EXACTLY2_5 (two).
- EXACTLY2_5 >= 13 in U2 is Machine-checked the same way, with restriction costs EXACTLY2_4 = 9 and
  EXACTLY1_4 = 9 and the union constraint (E3, `--elim-level 2`): `certify_cubes.py EXACTLY2_5 U2 12
  --refine 0:7,1:7,2:7,5:7,12:7 --elim --elim-level 2 --delete-proofs`, 115 cubes, 2.5 CPU-hours of
  solving and 4.7 of drat-trim, 9.7 GB of proofs (deleted after checking; hashes recorded), hardest
  cube 690 s. Gauges before that: level 1 refuted 86 cubes within 1M conflicts, level 2 another 17
  within 3M, the last 12 needed 3.4M to 6.4M. Next: MOD3_5 at k = 13 (bounds 3 and 4; much harder), or
  better upper bounds (both upper bounds come from local search that converged from several starts).
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
