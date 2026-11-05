# 7. Open sub-problems, ranked by leverage

Each entry is a single precise statement, what it would give, why it is believed approachable
(or not), and the barrier it must evade. "Leverage" = (size of consequence) × (plausibility of
progress with known tools). The list merges the five-per-front lists produced by the surveys in
this session with the dead ends in `06-attempts.md`. Items marked ◆ are the ones I would put a
research group on first.

## Tier 1 — unconditional results that would move the field

1. ◆ **Range Avoidance in $\mathsf{FP}^{\mathsf{NP}}$ for all input lengths**, equivalently
   $\mathsf E^{\mathsf{NP}}\not\subseteq\text{i.o.-}\mathrm{SIZE}[2^n/2n]$. *Gives:* the first near-maximum lower bound
   for a $\Delta_2$-type class, explicit rigid matrices and Ramsey graphs in $\mathsf{FP}^{\mathsf{NP}}$.
   *Why approachable:* Li's single-valued $\mathsf{FS}_2\mathsf P$ algorithm and Ren–Williams' $\mathsf E^{\mathsf{prMA}}/1$
   bound bracket it from above; it is a derandomization of a canonical-output $\mathsf{ZPP}^{\mathsf{NP}}$
   computation. *Barrier:* Korten–Pitassi (no black-box route to strong Avoid); Korten TR26-302
   (depth limits on stretch amplification); the Klivans–van Melkebeek derandomization needed is of
   the same strength as the conclusion.
2. ◆ **$\mathsf{NP}\not\subseteq\mathsf{ACC}^0$** (or $\mathsf E^{\mathsf{NP}}\not\subseteq\mathsf{ACC}^0$). *Gives:* the first superpolynomial
   lower bound for NP against a class that computes parity and counting. *Routes:* an easy-witness
   lemma for NP with polylogarithmic overhead (§5.6 option ii), or a magnification engine replacing
   the hierarchy theorem. *Barrier:* polynomial overheads in Murray–Williams; locality for the
   magnification route.
3. **$\mathsf{NEXP}\not\subseteq\mathsf{TC}^0$** via a $2^n/n^{\omega(1)}$-time SAT or CAPP algorithm for polynomial-size
   depth-2 threshold circuits (THR∘THR) with superquadratic wires. *Why approachable:* Chen–Tal–Wang
   (2026) already have a CAPP algorithm for XORs of two $n^{2.5-\varepsilon}$-gate THR∘THR circuits.
   *Barrier:* no depth-reduction template for arbitrary-weight thresholds.
4. **A non-local lower bound**: prove that $\mathrm{MCSP}[(\log n)^c]$ has no $n^{2+\varepsilon}$-size probabilistic
   formulas (sharp threshold of Chen–Jin–Williams 2020), or that some $2^{n^{o(1)}}$-sparse NP language
   has no $n^{1+\varepsilon}$-size circuits (Chen–Jin–Williams 2019), by a technique that *fails* against
   circuits with $n^{o(1)}$-fan-in oracle gates. *Gives:* $\mathsf{NP}\not\subseteq\mathrm{Formula}[n^k]$ (resp.
   $\mathrm{SIZE}[n^k]$) for all $k$. *Barrier:* this *is* the locality barrier; the technique must exploit
   that sub-circuits cannot compute hard functions, i.e. be self-referential.
5. **$\mathsf{NP}\not\subseteq\mathrm{SIZE}(n^k)$ for one fixed $k$** (even $k=1$, i.e. superlinear). *Routes:* $\mathsf{MA}=\mathsf{NP}$
   from derandomization (then Santhanam 2007 applies); or a direct argument. *Barrier:* Kannan/Cai/
   Santhanam all spend an extra quantifier; §6.3 shows the obvious composition argument fails.
6. **Frege, or even $\mathsf{AC}^0[p]$-Frege, superpolynomial lower bounds** for an explicit CNF family.
   *Routes:* constant-depth IPS lower bounds over $\mathbb F_p$ for CNFs (Elbaz–Govindasamy–Lu–Tzameret
   2025 transfer); dag-like Res($\oplus$) first (the Sept 2026 bit-PHP claim, if it holds); Razborov's
   NW-generator conjecture one level up from $\mathsf{AC}^0$-Frege. *Barrier:* feasible interpolation fails
   under factoring; Pich–Santhanam 2023: EF bounds for natural meta-formulas are $\mathsf P\ne\mathsf{NP}$-hard.
7. **Beat $3.5n$ / $n^3$.** A $4n$ (or any $\omega(n)$) $B_2$ circuit lower bound, or an $n^{3+\varepsilon}$ De Morgan
   formula bound (KRW composition conjecture), for an explicit function. *Barrier:* GHKK gate-elimination
   limits; the KRW conjecture itself.
8. **$2^{\omega(\sqrt n)}$ depth-3 lower bound** for an explicit function, toward Valiant's
   $2^{\omega(n/\log\log n)}$ threshold for superlinear log-depth bounds. *Barrier (new):* Loff et al.
   2026 rule out $\mathsf{AC}^0$-natural (switching-lemma) proofs.

## Tier 2 — structural results that would reorganize the attack

9. ◆ **Unconditional NP-hardness of MCSP** (total, under randomized Turing reductions), without
   the three hypotheses of Hirahara–Ilango 2025. *Gives:* by Murray–Williams / Saks–Santhanam, an
   NP-hardness proof under deterministic reductions must come packaged with $\mathsf{EXP}\ne\mathsf{ZPP}$-type
   separations; under randomized reductions it would (Hirahara 2023) make "NP hard ⟹ OWF" a theorem
   once DistK$^t$ hardness is in hand. *Barrier:* Mazor–Pass (no Levin reductions in Obfustopia);
   Ilango's random-oracle result says the proof cannot relativize naively.
10. **NP-hardness of DistK$^t$ under randomized reductions** (or the Meta-Complexity Padding
    Conjecture). *Gives:* $\mathsf{NP}\not\subseteq\mathsf{BPP}\Rightarrow$ OWFs (collapsing Heuristica and Pessiland into
    Algorithmica-or-Cryptomania).
11. **$\mathsf{NP}\not\subseteq\mathsf{BPP}\Rightarrow$ Gap-MINKT $\notin\mathsf{BPP}$** (worst-case NP-hardness of approximating
    $K^t$ within Hirahara's gap). *Gives:* unconditional exclusion of errorless Heuristica.
    Current best replaces the hypothesis by $\mathsf{UP}\not\subseteq\mathrm{DTIME}(2^{O(n/\log n)})$ (Hirahara 2021).
12. **Close the polylog window in the 2026 Pessiland characterization** (Hirahara–Nanashima), or the
    two-sided/one-sided error gap for pK$^t$ (Hirahara–Lu–Oliveira 2024). *Gives:* OWFs from
    average-case hardness of NP.
13. **Unconditional NP-hardness of Gap-McK$^t$P**, which activates Kabanets–Kolokolova (STOC 2026):
    "the chain rule for conditional $K^t$ fails iff $\mathsf P\ne\mathsf{NP}$" — Kolmogorov's 1960s proposal made precise.
14. **A pseudodeterministic polynomial-time construction of primes for all $n$** (remove "infinitely
    often" from Chen–Lu–Oliveira–Ren–Santhanam). *Gives:* the first a.e. result of the iterative
    win-win paradigm outside $\mathsf S_2\mathsf E$.
15. **$\mathrm{TIME}[t]\subseteq\mathrm{SPACE}[t^{1/2-\varepsilon}]$** for multitape machines, or
    $\mathrm{TIME}_{\mathrm{RAM}}[t]\subseteq\mathrm{SPACE}[t^{1-\Omega(1)}]$; the all-$\varepsilon$ version gives $\mathsf P\ne\mathsf{PSPACE}$.
16. **$\mathrm{SAT}\notin\mathrm{TIME}[n^c]\cap\mathrm{SPACE}[n^{o(1)}]$ for some $c>2\cos(\pi/7)$**, which Buss–Williams
    show requires a non-alternation-trading argument.
17. **$\mathsf{EXP}\ne\mathsf{BPP}$** (or $\mathsf{NEXP}\ne\mathsf{BPP}$), the uniform analogue of $\mathsf E\not\subseteq\mathsf{P/poly}$;
    gives i.o. subexponential average-case derandomization (Impagliazzo–Wigderson 1998).
18. **Frege non-automatability from $\mathsf P\ne\mathsf{NP}$ alone**, or a proof that any such reduction yields
    efficient learning of $\mathsf{P/poly}$ (Pich–Santhanam 2022 direction).
19. **$\mathrm{PV}_1\ne\mathrm{APC}_1$ unconditionally** (an EF-hard proof complexity generator would do it;
    known only under iO by Ilango–Li–Williams 2023).

## Tier 3 — barrier and meta questions

20. ◆ **Characterize non-local techniques.** Is there any lower-bound argument for formulas or
    branching programs that provably fails for circuits with $n^{o(1)}$-fan-in oracle gates? A
    formal theorem of the form "every argument of type T localizes" for a broad type T would turn
    the locality barrier into a specification, as Buss–Williams did for alternation trading.
21. **Does the algorithmic method have a PRF obstacle at its next targets?** Is there a PRF
    candidate computable in $\mathsf{ACC}^0\circ\mathsf{THR}$ or $\mathsf{TC}^0$ strong enough that Razborov–Rudich bites
    on the *weakly constructive* properties the method produces (Williams 2016)?
22. **Where exactly is the provability frontier?** Decide whether $\mathrm{PV}_1$ (then $\mathrm S^1_2$,
    $\mathrm{APC}_1$) proves $\mathsf{NP}\not\subseteq\mathrm{SIZE}[n^k]$ for a fixed $k$, extending Krajíček–Oliveira 2017
    and Chen–Li–Oliveira 2025 from upper bounds and intuitionistic theories to classical lower bounds.
23. **Can the 2026 tensor-network / eight-square technique (if it survives review) give a
    $2^n/n^{\omega(1)}$ Circuit-SAT algorithm**, which by Williams 2013 would give $\mathsf{NEXP}\not\subseteq\mathsf{P/poly}$?
    The method's reported internal ceilings on expander formulas suggest it is confined to
    bounded-width CNFs; settling this is the first question to ask of the working group's review.
24. **Statement-fidelity audits for machine-generated Lean corpora.** Not a mathematical problem,
    but the one that now gates whether items 23 and the ETH claim count as theorems.

## What is *not* on the list

- Direct attacks on $\mathsf P\ne\mathsf{NP}$ by diagonalization, counting, or collapse arguments (§6.1–6.3):
  provably insufficient.
- Independence from ZFC or PA: no technique, and Ben-David–Halevi make it unattractive.
- $\mathsf P=\mathsf{NP}$ via a clever SAT algorithm: the empirical and structural evidence in §1.5, plus the
  fact that every proposed algorithm since 1971 has failed on a specific family, make this the
  lowest-leverage direction; but note that an algorithm's correctness proof would also have to be
  non-relativizing and non-algebrizing (Theorems 2.1, 2.3), which no proposed algorithm has acknowledged.
