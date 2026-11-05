# P vs NP: an honest attack dossier (November 2026)

**Status of the problem: open.** This repository does not contain a proof that P = NP or P ≠ NP, and
it does not claim one. It contains the output of one sustained, resourced attempt to attack the
problem with everything available in a single session: the exact theorems that constrain any
proof (with proofs), the state of the art on every live front as of 5 November 2026 (compiled by
six parallel literature surveys with verification tags), a log of nine concrete attack attempts
pushed until each one died at a precisely named obstruction, a ranked research program, a list of
24 open sub-problems ordered by leverage, and reproducible computational experiments.

If you are looking for the one-paragraph answer: see `docs/00-executive-summary.md`.

## Map

| File | What it is |
|---|---|
| `docs/00-executive-summary.md` | The findings in one page: what is known, what blocks every approach, what to do next |
| `docs/01-problem.md` | Precise definitions, 14 equivalent/adjacent formulations, the unconditional map, why experts believe P ≠ NP, logical status |
| `docs/02-barriers.md` | Relativization (full proof), natural proofs (full proof), algebrization, locality — and the resulting specification for the shape of any proof |
| `docs/03-frontier-2026.md` | State of the art by front, with 2025–2026 results flagged and verification caveats |
| `docs/04-attack-vectors.md` | Nine attack vectors ranked; for each: last position, obstruction, *next lemma*, barrier compliance |
| `docs/05-worked-mathematics.md` | Self-contained proofs: Shannon counting, Schnorr's 3(n−1) bound, Kannan, Cook–Reckhow, Karp–Lipton, the algorithmic method and why it stops short of NP |
| `docs/06-attempts.md` | Nine attempts from this session and exactly where each dies (including one tempting false derivation, dissected) |
| `docs/07-open-subproblems.md` | 24 open sub-problems in three tiers |
| `docs/bibliography.md` | Curated references, with unverified items marked |
| `experiments/` | SAT-based exact circuit synthesis (validated against Knuth's TAOCP 4A table) and a CDCL/proof-complexity experiment; results in `experiments/results/` |

## The short version

1. Any proof of P ≠ NP must be non-relativizing, non-algebrizing, and (if it goes through circuit
   lower bounds) non-natural and non-local. These are theorems (`docs/02-barriers.md`).
2. Exactly one family of techniques is known to evade the classical barriers — Williams' algorithmic
   method and its descendants (range avoidance, iterative win-win) — and it currently reaches
   NQP ⊄ ACC0 and Σ2E ⊄ SIZE(2^n/n). Every known route from there down to NP needs an argument that
   works at polynomial scale without a spare quantifier or an exponential time budget; none exists.
3. The 2026 frontier is an explicit-construction problem (Range Avoidance in FP^NP), a non-local
   lower-bound technique (hardness magnification), NP-hardness of meta-complexity problems, and
   AC0[p]-Frege lower bounds. None of these resolves P vs NP alone; each is where a new idea would
   first register.
4. The reported October 2026 AI-generated, Lean-checked refutations of the Exponential Time
   Hypothesis are under expert review and, by their authors' own statement, have no bearing on P vs NP.

## Experiments

```bash
pip install python-sat numpy
cd experiments
python3 exact_circuit_complexity.py n4        # all 222 NPN classes of 4-input functions; checks Knuth's distribution
python3 exact_circuit_complexity.py explicit  # explicit 4/5-input functions; intervals when the budget runs out
python3 proof_complexity_php.py               # CDCL on pigeonhole (exponential) vs ordering principle (polynomial)
```

## Provenance and caveats

- Written in one session on 5 November 2026 by Claude (Anthropic), with six parallel research
  sub-agents for the literature. The session's network policy blocked direct fetches of arXiv, ECCC
  and ACM DL; citations were verified through search-engine extracts of those pages and through
  GitHub. Items that could not be verified are marked **[U]** in the documents; results after June
  2026 are marked ★.
- All mathematics in `docs/02` and `docs/05` is standard; the proofs were written from scratch and
  should be checked like any other proof. `docs/06` contains one deliberately preserved false
  derivation with its error identified (§6.3).
- Nothing here is peer reviewed.
