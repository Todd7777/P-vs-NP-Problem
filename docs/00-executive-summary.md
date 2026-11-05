# 0. Executive summary

**Question.** Is P = NP?
**Answer after this session.** Unknown. No proof exists in either direction as of 5 November 2026, and
this repository does not supply one. What it supplies is a precise account of *why* every known
approach stops where it stops, the state of every live front including results from the last five
months, and a ranked list of the next lemmas.

## What is actually established

1. **Three barrier theorems plus one** (`02-barriers.md`, with proofs). Any proof of P ≠ NP must use a
   property of polynomial-time computation that (a) fails relative to some oracle
   (Baker–Gill–Solovay 1975), (b) fails relative to low-degree algebraic extensions of some oracle
   (Aaronson–Wigderson 2008), (c) if it goes through circuit lower bounds, is not a large, efficiently
   checkable property of truth tables, assuming pseudorandom functions exist (Razborov–Rudich 1994),
   and (d) if it goes through hardness magnification, exploits that the sub-circuits of a small
   circuit cannot compute hard functions (the locality barrier, 2020). Diagonalization, counting,
   collapse arguments, random restrictions and the approximation method each fail at least one test.
2. **Exactly one family of techniques evades (a)–(c)**: Williams' algorithmic method, in which a
   slightly-better-than-brute-force satisfiability algorithm for a circuit class, combined with the
   easy-witness lemma and a hierarchy theorem, yields a lower bound. Its descendants (range avoidance,
   iterative win-win) have produced the only unconditional lower bounds above $\mathsf{AC}^0[p]$:
   $\mathsf{NQP}\not\subseteq\mathsf{ACC}^0$ (2018), $\mathsf S_2\mathsf E$ requires circuits of size $2^n/n$ (2024),
   $\mathsf E^{\mathsf{prMA}}/1$ likewise (FOCS 2026), $\mathsf E^{\mathsf{NP}}\not\subseteq\mathsf{THR}\circ\mathsf{THR}[n^{2.5-\varepsilon}]$ (STOC 2026).
3. **All of these stop one step above NP for the same reason.** They pay for a witness search with
   either an exponential time budget or a spare quantifier ($\Sigma_2$, $\mathsf S_2$, MA). Nothing is
   known to work at polynomial scale without that resource. In `06-attempts.md` nine independent
   attack lines are pushed until each dies, and each dies at this bridge.
4. **The best explicit lower bounds for functions in NP** remain linear for circuits ($3.5n$, Oct 2026
   preprint; $3.1n$ refereed), cubic for formulas, and nothing superpolynomial against $\mathsf{TC}^0$;
   $\mathsf{NP}\not\subseteq\mathrm{SIZE}(n^k)$ is open for every fixed $k$, including superlinear.

## What changed recently (verified to the extent the session's network allowed)

- Range Avoidance is now the central explicit-construction problem: single-valued $\mathsf{FS}_2\mathsf P$
  algorithms exist (2024); it is *not* NP-hard unless PH collapses (STOC 2026); it is hard under
  iO/LWE-type assumptions; Avoid $\in\mathsf{FP}^{\mathsf{NP}}$ is equivalent to $\mathsf E^{\mathsf{NP}}$ needing
  maximum circuits and remains open.
- MCSP is still not known NP-hard unconditionally; NP-hardness holds under three strong assumptions
  (FOCS 2025) and for several variants; one-way functions have a dozen equivalent meta-complexity
  characterizations; Pessiland has been reduced to a polylogarithmic approximation window (STOC 2026).
- $\mathsf{AC}^0[p]$-Frege lower bounds remain open after three decades; progress is in Res($\oplus$) and
  in reductions to constant-depth algebraic proof systems; unprovability results in bounded arithmetic
  are now unconditional and sharp.
- Williams' $\mathrm{TIME}[t]\subseteq\mathrm{SPACE}[\sqrt{t\log t}]$ (2025) stands unimproved and has been formalized
  in Lean (Nov 2026); it is about space, not about NP.
- On 26 October 2026 two AI labs released AI-generated, Lean-checked manuscripts claiming a
  deterministic $2^{o(n)}$ algorithm for $k$-SAT (refuting the Exponential Time Hypothesis). The claim
  is under expert review, no flaw has been announced, and by its authors' own statement it has no
  bearing on P vs NP. A June 2026 "Lean-verified P = NP" turned out to have proved `True`.
- Community belief: ~88–95% for P ≠ NP (Gasarch 2019; Aaronson's 5% for P = NP, Oct 2026).

## What this session did beyond surveying

- Wrote from scratch, and checked, full proofs of the relativization and natural-proofs theorems,
  Shannon's counting bound, Schnorr's $3(n-1)$ lower bound for parity over $U_2$ (the complete
  anatomy of a gate-elimination argument), Kannan's theorem, Cook–Reckhow and Karp–Lipton, and a
  quantitative account of why the algorithmic method stops at $\mathsf{NQP}$ (`05-worked-mathematics.md`).
- Found and dissected a tempting false derivation of "$\mathsf{NP}\not\subseteq\mathrm{SIZE}(n^k)$ for all $k$" from
  Kannan's theorem; the error is that $\mathrm{SIZE}(n^k)$ is not closed under polynomial blow-up of
  witness length (`06-attempts.md`, §6.3). Proved the folklore dichotomy "P ≠ NP or EXP ⊄ P/poly" (§6.4).
- Built a SAT-based exact circuit synthesizer, validated it against Knuth's exhaustive table of the
  circuit complexity of all 65,536 four-variable functions, and used it to confirm Schnorr's bound at
  $n=2,3,4$ and to compute exact or bracketed complexities of explicit five-variable functions
  (`experiments/`). Measured the exponential growth of CDCL on pigeonhole formulas against polynomial
  behavior on the ordering principle, the empirical face of Haken's theorem.
- Ranked nine attack vectors by the next lemma each needs (`04-attack-vectors.md`) and listed 24
  open sub-problems in three tiers (`07-open-subproblems.md`).

## What to do next

The single shared bottleneck is a non-relativizing, non-algebrizing, non-natural, non-local argument
at polynomial scale. The highest-leverage concrete targets are: Range Avoidance in $\mathsf{FP}^{\mathsf{NP}}$;
an easy-witness lemma for NP with polylogarithmic overhead, or a CAPP algorithm for depth-2 threshold
circuits; any lower-bound technique that provably fails when small-fan-in oracle gates are added;
NP-hardness of DistK$^t$ under randomized reductions; and a dag-like Res($\oplus$) lower bound on the way
to $\mathsf{AC}^0[p]$-Frege. For AI-assisted work specifically: search for *algorithms* (which the algorithmic
method converts into lower bounds and which can be kernel-checked), formalize the barrier theorems so
candidate proofs can be tested against them mechanically, and audit statement fidelity of
machine-generated Lean corpora before treating any of them as theorems.
