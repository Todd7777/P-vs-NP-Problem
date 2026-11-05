# 4. Attack vectors, ranked

For each live approach: the statement it would prove, the last known position, the obstruction,
the *next lemma* (a single precise statement whose proof would be recognized as progress), how it
fares against the barrier specification of §2.6, and my assessment. Ranking is by expected
information gained per unit of effort, not by probability of resolving P vs NP outright — nothing
on this list does that in one step.

Barrier codes: **R** relativizes (fatal), **A** algebrizes (fatal alone), **N** natural (fatal against
$\mathsf{P/poly}$ if PRFs exist), **L** local (fatal for magnification). ✓ = evades.

---

## V1. Explicit constructions: Range Avoidance and near-maximum lower bounds

**Would prove.** $\mathsf E^{\mathsf{NP}}\not\subseteq\mathrm{SIZE}[2^n/2n]$ (equivalently Avoid $\in\mathsf{FP}^{\mathsf{NP}}$, Korten
2021); further down, $\mathsf E$ or $\mathsf{NE}$ hard functions would need Avoid in $\mathsf{FP}$ or single-valued $\mathsf{FNP}$.

**Position (Nov 2026).** Single-valued $\mathsf{FS}_2\mathsf P$ on all lengths (Li 2024) ⟹ $\mathsf S_2\mathsf E$,
$\Sigma_2\mathsf E\cap\Pi_2\mathsf E$, $\mathsf{ZPE}^{\mathsf{NP}}$ near-maximum; $\mathsf E^{\mathsf{prMA}}/1$ (Ren–Williams FOCS 2026).
Avoid is in $\mathsf{AM}\cap\mathsf{coAM}$-land (GLS STOC 2026), hard under iO/LWE-type assumptions, and the
Li technique cannot reach strong Avoid (Korten–Pitassi 2024).

**Obstruction.** Avoid $\in\mathsf{FP}^{\mathsf{NP}}$ is a derandomization of Li's canonical-output
$\mathsf{ZPP}^{\mathsf{NP}}$ computation; the hardness needed for that derandomization (Klivans–van Melkebeek)
is of the same strength as the conclusion. Korten's TR26-302 (Nov 2026) shows black-box stretch
amplification cannot shortcut the depth cost.

**Next lemma.** *A single-valued $\mathsf{FP}^{\mathsf{NP}}$ algorithm for Avoid restricted to circuits of depth
$O(\log n)$ with stretch $n\to 2n$*, or, more modestly, a $\mathsf{P}^{\mathsf{NP}}$ reduction from weak Avoid to
the Linear Ordering Principle with a *deterministic* tie-breaking rule. Either would be the first
$\Delta_2$-level progress.

**Barriers.** R ✓ (the Jeřábek–Korten reduction uses the structure of circuits; the Avoid formulation
is itself non-relativizing in spirit, though Li's result is stated to hold in relativized worlds — the
descent to $\mathsf{FP}^{\mathsf{NP}}$ would have to be non-relativizing), A ✓, N ✓ (no large property), L n/a.

**Assessment.** Highest-leverage *unconditional* front; richest in tools (iterative win-win,
pseudodeterminism, PCP theorem); clearest equivalence to a lower bound. Its ceiling is $\mathsf E^{\mathsf{NP}}$.
For P vs NP it matters because it is where the field is learning how much nondeterminism it costs
to *name* a hard object — the quantity every descent argument needs to control.

---

## V2. The algorithmic method: $\mathsf{TC}^0$ and the descent to NP

**Would prove.** $\mathsf{NEXP}\not\subseteq\mathsf{TC}^0$ (from a depth-2 threshold SAT/CAPP algorithm);
$\mathsf{NP}\not\subseteq\mathsf{ACC}^0$ (from a sharper easy-witness lemma or a new contradiction engine).

**Position.** $\mathsf{NQP}\not\subseteq\mathsf{ACC}^0\circ\mathsf{THR}$ (Murray–Williams 2018), average-case and a.e.
versions (Chen 2019; Chen–Ren 2020; Chen–Lyu–Williams 2020); $\mathsf E^{\mathsf{NP}}\not\subseteq\mathsf{THR}\circ\mathsf{THR}[n^{2.5-\varepsilon}]$
gates (Chen–Tal–Wang STOC 2026).

**Obstruction.** (i) For $\mathsf{TC}^0$: no depth reduction for arbitrary-weight thresholds; known SAT
algorithms stop at $n^{1+\varepsilon_d}$ wires. (ii) For NP: polynomial overhead in the easy-witness lemma
versus polylogarithmic savings on $O(\log n)$-input witness circuits (§5.6).

**Next lemma.** (i) *A $2^{n-n^{\varepsilon}}$-time CAPP algorithm for THR∘THR circuits with $n^{2+\varepsilon}$ wires.*
(ii) *If $\mathsf{NP}\subseteq\mathrm{SIZE}[n^k]$ then every NP verifier has witnesses computable by circuits of size
$n^{k}\cdot\mathrm{polylog}(n)$* (an easy-witness lemma with polylogarithmic loss).

**Barriers.** R ✓, A ✓, N ✓ (Williams 2016: weakly constructive, not large). Open question (Tier 3,
item 21): whether a $\mathsf{TC}^0$-computable PRF makes the *next* targets natural-proofs-sensitive.

**Assessment.** The only method with a track record of unconditional lower bounds for classes above
$\mathsf{AC}^0[p]$. Lemma (ii) is the most direct known route to "NP is hard for something nontrivial";
I found no barrier against it, and no idea for it either. An AI-assisted search for (i) — the
algorithm, not the lower bound — is a concrete, checkable task (§4.10).

---

## V3. Hardness magnification with a non-local technique

**Would prove.** $\mathsf{NP}\not\subseteq\mathrm{SIZE}[n^k]$ for all $k$ (CJW 2019), $\mathsf{NP}\not\subseteq\mathrm{Formula}[n^k]$ (CJW 2020),
or $\mathsf{NP}\not\subseteq\mathsf{P/poly}$ (OPS 2019; MMW 2019), from lower bounds a hair above current ones.

**Position.** Every hypothesis is just beyond the state of the art *for other functions* and just
inside the locality barrier for the target functions.

**Obstruction.** Locality (Theorem 2.4).

**Next lemma.** *Any* lower bound for a natural problem in any weak model whose proof provably fails
when $n^{o(1)}$-fan-in oracle gates are added. Even a toy: a function $f$ and a proof that $f\notin\mathrm{Formula}[n^{1.5}]$
such that $f$ *does* have $n^{1.5}$-size formulas with $\mathrm{polylog}(n)$-fan-in oracle gates. That would be
the first non-local technique and would immediately be tested against the magnification targets.

**Barriers.** N ✓ by construction (targets are sparse); L ✗ — the whole problem.

**Assessment.** Highest payoff per theorem, lowest number of ideas. It is self-referential (the
proof must use that sub-circuits cannot compute hard functions) in a way that suggests the technique,
if it exists, will come from V1 or V4, not from classical combinatorics.

---

## V4. Meta-complexity

**Would prove.** NP-hardness of MCSP/MINKT (with class-separation consequences under deterministic
reductions, Murray–Williams 2017; Saks–Santhanam 2020); "$\mathsf{NP}$ hard ⟹ OWF" (Hirahara 2023 + NP-hardness
of DistK$^t$); "chain rule fails iff $\mathsf P\ne\mathsf{NP}$" (Kabanets–Kolokolova 2026, under Gap-McK$^t$P hardness).

**Position.** Partial MCSP, multi-output MCSP, oracle MCSP, McK$^t$P, MINnKT: NP-hard. Total MCSP:
NP-hard only under three strong assumptions (Hirahara–Ilango FOCS 2025) or relative to a random
oracle (Ilango 2023). OWF characterizations: many and sharp. Pessiland: a polylog window.

**Obstruction.** NP-hardness of total MCSP under deterministic reductions would *force* circuit
lower bounds (Murray–Williams), so any proof must carry one; under randomized reductions it must be
non-witness-preserving (Mazor–Pass) and must use oracle-specific structure (Hirahara–Watanabe).

**Next lemma.** *DistK$^t$ is NP-hard under randomized polynomial-time reductions* (or the Padding
Conjecture). This single lemma would make "NP is hard ⟹ one-way functions exist" a theorem and
collapse two of Impagliazzo's five worlds.

**Barriers.** R ✓ (non-black-box, Hirahara 2018), A ✓, N ✓ (these are reductions, not truth-table
properties), L: bears on V3 by supplying candidate non-local ingredients.

**Assessment.** The most conceptually active front and the one most likely to supply the *missing
ingredient* for V3. It cannot by itself refute $\mathsf P=\mathsf{NP}$ (consistent-world principle, §6.8).

---

## V5. Proof complexity

**Would prove.** $\mathsf{NP}\ne\mathsf{coNP}$ (hence $\mathsf P\ne\mathsf{NP}$) via lower bounds for *every* proof system;
intermediate goals: $\mathsf{AC}^0[p]$-Frege, Frege, Extended Frege lower bounds.

**Position.** Everything up to bounded-depth Frege, Cutting Planes with $\Theta(\log n)$ width, SoS
degree: done. $\mathsf{AC}^0[p]$-Frege open for ~30 years; 2026 progress is in Res($\oplus$) and in the
reduction of $\mathsf{AC}^0[p]$-Frege to constant-depth IPS over $\mathbb F_p$ (EGLT 2025).

**Obstruction.** Feasible interpolation fails for Frege-type systems under factoring; Pich–Santhanam
(2019, 2023): random tautologies are the wrong place to look for strong systems, and EF lower bounds
for circuit-lower-bound formulas are $\mathsf P\ne\mathsf{NP}$-hard under provability conditions.

**Next lemma.** *An explicit CNF family with superpolynomial-size proofs required in dag-like
Res($\oplus$)* (if the Sept 2026 bit-PHP claim holds, this is done; verify), then *a constant-depth IPS
lower bound over $\mathbb F_p$ for an explicit CNF*, which transfers to $\mathsf{AC}^0[p]$-Frege.

**Barriers.** Its own analogue of natural proofs (Razborov's conjecture; Pich–Santhanam 2019); R/A
not directly applicable.

**Assessment.** Steady, with the clearest next lemma on the whole list (dag-like Res($\oplus$)); but
the distance from $\mathsf{AC}^0[p]$-Frege to "all systems" is the distance from $\mathsf{AC}^0[p]$ circuits to
$\mathsf{P/poly}$, and the generators program that would bridge it rests on cryptographic hypotheses
that already imply $\mathsf P\ne\mathsf{NP}$.

---

## V6. Derandomization and uniform hardness

**Would prove.** $\mathsf{prBPP}=\mathsf{prP}$ ⟺ almost-all-inputs uniform hardness (Chen–Tell 2021 and
successors); $\mathsf{NEXP}\not\subseteq\mathsf{P/poly}$ from CAPP; nothing about P vs NP conditionally (Tell's ceiling).

**Position.** A web of equivalences (Chen–Tell, Liu–Pass, Chen–Tell–Williams, van Melkebeek–Sdroievski,
Ball–Chen–Tell 2025); i.o. pseudodeterministic primes; Avoid-based derandomization of a prMA fragment (Li 2026).

**Obstruction.** Every equivalence has a hard side of the same strength; even $\mathsf{BPTIME}$ hierarchy
theorems are open; $\mathsf{EXP}\ne\mathsf{BPP}$ is open.

**Next lemma.** *$\mathsf{NEXP}\ne\mathsf{BPP}$*, or *a deterministic refuter for some $f\in\mathsf{FP}$ against
$\mathsf{TC}^0$-type streaming compressors* (which by Chen–Tell–Williams already yields $\mathsf{prBPP}=\mathsf{prP}$).

**Barriers.** R ✗ for most of it (IW-style arguments relativize), A ✓ where PCP-based, N n/a.

**Assessment.** Essential infrastructure (V1 and V2 are derandomization in disguise), but by Tell's
observation it cannot be the *last* step of a P vs NP proof.

---

## V7. Algebraic complexity and GCT

**Would prove.** $\mathsf{VP}\ne\mathsf{VNP}$ (permanent vs determinant); via Bürgisser's bridge theorems,
Boolean consequences under GRH or over finite fields; PIT in P ⟹ $\mathsf{NEXP}\not\subseteq\mathsf{P/poly}$ or
$\mathrm{perm}\notin\mathsf{VP}$ (Kabanets–Impagliazzo).

**Position.** Superpolynomial constant-depth bounds (LST 2021; exponent sharpened and shown optimal
for the LST measure by Bhargav–Dutta–Saxena 2022/2024; all fields by Forbes 2024; FOCS 2026 depth-3
small characteristic); general circuits, formulas, ABPs and determinantal complexity stuck at
$\Omega(n\log d)$, $\Omega(n^2)$, $\Omega(n^2)$, $n^2/2$. GCT: occurrence obstructions ruled out (BIP 2016/2019);
multiplicity obstructions work at toy scale (product-plus-power 2025; graph isomorphism, June 2026)
but no route to permanent vs determinant is claimed (Bläser–Ikenmeyer survey, May 2025). Details in §3.8.

**Obstruction.** Algebraic natural proofs barrier (FSV, GKSS 2017) for the standard techniques over
$\mathbb C$ (vacuous over finite fields and for bounded coefficients, CKRST 2020/2022, so the real
question is whether VP has VP-succinct hitting sets); the LST measure is provably maxed out (BDS);
the bridge to Boolean classes needs non-uniform hypotheses and GRH over $\mathbb C$ (Bürgisser 2000).

**Next lemma.** *Superpolynomial lower bounds for depth-$\omega(1)$ (e.g. depth $\log\log n$) algebraic
circuits for an explicit polynomial*, or *any multiplicity obstruction separating a small case of
permanent from determinant*.

**Assessment.** $\mathsf{VP}\ne\mathsf{VNP}$ is the "Boolean P vs NP without the Boolean" and may well fall
first; its bridge to $\mathsf P\ne\mathsf{NP}$ is conditional and one-directional. Important, adjacent.

---

## V8. Uniform time–space methods

**Would prove.** $\mathsf P\ne\mathsf{PSPACE}$ (from $\mathrm{TIME}[t]\subseteq\mathrm{SPACE}[t^{\varepsilon}]$); SAT exponent above $2\cos(\pi/7)$.

**Position.** Williams 2025 ($\sqrt{t\log t}$, formalized); nothing on NTIME or RAMs; SAT tradeoffs unchanged.

**Next lemma.** *$\mathrm{TIME}[t]\subseteq\mathrm{SPACE}[t^{1/2-\varepsilon}]$*, or *a nondeterministic analogue
$\mathrm{NTIME}[t]\subseteq\mathrm{NSPACE}[t^{1-\Omega(1)}]$* — the latter would be a genuinely new kind of statement.

**Assessment.** Orthogonal to P vs NP (it is about space), but it is the one front where a
*uniform* non-relativizing-flavored simulation technique appeared recently, and uniform techniques
are exactly what Attempt 7 lacked.

---

## V9. Fine-grained hardness and the 2026 ETH claims

**Would prove.** If the October 2026 algorithms stand: ETH, SETH, $\#$ETH, Gap-ETH false; $\mathsf E^{\mathsf{NP}}\not\subseteq\mathrm{SIZE}(O(n))$
via Williams 2013. If they extend to Circuit-SAT with $2^n/n^{\omega(1)}$ savings: $\mathsf{NEXP}\not\subseteq\mathsf{P/poly}$.

**Position.** Two machine-checked manuscripts under review; the authors state the method is confined
to bounded-width CNFs and has no bearing on P vs NP.

**Next lemma.** *Either a flaw, or a precise ceiling theorem for the tensor-network / eight-square
method* (e.g. $2^{\Omega(\sqrt n)}$ on expander formulas).

**Assessment.** Not a route to P vs NP, but if correct it would be the first time the algorithmic
method's *hypothesis* side was supplied by an AI system, which bears directly on §4.10.

---

## 4.10 What I would actually do next (an AI-assisted program)

The attack vectors share one bottleneck: a non-relativizing, non-algebrizing, non-natural, non-local
argument at polynomial scale (§6.10). No one knows how to make one. What *can* be done now, with
the resources a session like this one has:

1. **Search for algorithms, not lower bounds.** The algorithmic method converts lower bounds into
   algorithm design, which is checkable. Targets: CAPP/SAT for THR∘THR with $n^{2+\varepsilon}$ wires (V2);
   Circuit-SAT with $2^n/n^{\omega(1)}$ savings; the ceiling of the 2026 CNF method (V9). An AI system can
   generate candidate algorithms with proofs and have them kernel-checked; the October 2026 corpus
   shows this is now operational, and also shows statement-fidelity auditing is the gate.
2. **Audit locality.** Formalize (in Lean) the statement "proof technique T is local" for the
   standard techniques and prove it; then any new lower-bound proof can be *mechanically tested* for
   locality before anyone spends a year on it (Tier 3, item 20).
3. **Formalize the barrier theorems.** BGS, RR, AW and the locality barrier are short and
   self-contained (§2); a Lean library of them would let an AI-generated "proof of $\mathsf P\ne\mathsf{NP}$"
   be checked against the barriers automatically — exactly the test that caught Blum 2017 by hand.
4. **Explicit-construction experiments.** Avoid instances for small $n$ and structured circuit
   classes are concrete search problems; SAT-solver-aided exact synthesis (this repository's
   `experiments/`) is the right tool for exploring stretch amplification and $\mathsf{NC}^0$-Avoid at scale.
5. **Keep the meta-complexity reductions machine-checked.** Hirahara-style non-black-box reductions
   are intricate and are the most likely source of a non-local ingredient; they are also the most
   likely place for an error to hide.

None of these is a proof. Each converts a piece of the problem into something that can be
verified, which is the only kind of progress that has ever stuck.
