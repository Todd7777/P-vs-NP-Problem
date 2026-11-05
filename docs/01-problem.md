# 1. The problem, stated precisely

This file fixes definitions and lists the formulations of P vs NP that are actually used in
attacks on it. Everything here is standard; the point is to have one precise reference that the
rest of the dossier can lean on. (Sources: Arora–Barak, *Computational Complexity*; Jukna, *Boolean
Function Complexity*; Cook's official Clay problem description; Aaronson, "P =? NP" (2016).)

## 1.1 Machines, classes, reductions

**Deterministic time.** For a function $t:\mathbb N\to\mathbb N$, $\mathrm{DTIME}(t)$ is the set of
languages $L\subseteq\{0,1\}^*$ decided by a (multi-tape) deterministic Turing machine that halts
within $O(t(n))$ steps on every input of length $n$.

$$\mathsf P=\bigcup_{k\ge 1}\mathrm{DTIME}(n^k).$$

**NP, verifier form.** $L\in\mathsf{NP}$ iff there are a polynomial $p$ and a polynomial-time
deterministic machine $V$ (the *verifier*) such that for all $x$,

$$x\in L\iff \exists w\in\{0,1\}^{p(|x|)}:\ V(x,w)=1 .$$

The string $w$ is a *witness* (certificate). Equivalently, $\mathsf{NP}=\bigcup_k \mathrm{NTIME}(n^k)$,
languages accepted by nondeterministic machines in polynomial time.

**Complements and the hierarchy.** $\mathsf{coNP}=\{\overline L: L\in\mathsf{NP}\}$.
$\Sigma_k^p,\Pi_k^p$ are defined by $k$ alternating polynomially bounded quantifiers in front of a
polynomial-time predicate; $\mathsf{PH}=\bigcup_k\Sigma_k^p$. $\mathsf{PSPACE}$, $\mathsf{EXP}=\mathrm{DTIME}(2^{n^{O(1)}})$,
$\mathsf{NEXP}=\mathrm{NTIME}(2^{n^{O(1)}})$, $\mathsf E=\mathrm{DTIME}(2^{O(n)})$, $\mathsf{NE}$, $\mathsf{NQP}=\mathrm{NTIME}(2^{(\log n)^{O(1)}})$.

**Circuits.** A Boolean circuit over the basis $B_2$ (all 16 binary functions) with $n$ inputs is a
DAG of fan-in-2 gates. $\mathrm{SIZE}(s(n))$ is the set of languages $L$ for which there is a family
$(C_n)$ with $C_n$ of size $\le s(n)$ and $C_n(x)=[x\in L]$ for all $x\in\{0,1\}^n$.
$\mathsf{P/poly}=\bigcup_k\mathrm{SIZE}(n^k)$. Standard inclusions: $\mathsf P\subseteq\mathsf{P/poly}$ (Cook–Levin
tableau), and $\mathsf{P/poly}$ contains undecidable languages (it is non-uniform). Restricted
classes: $\mathsf{AC}^0$ (constant depth, unbounded fan-in AND/OR/NOT, poly size), $\mathsf{AC}^0[m]$
(plus $\mathrm{MOD}_m$ gates), $\mathsf{ACC}^0=\bigcup_m\mathsf{AC}^0[m]$, $\mathsf{TC}^0$ (constant depth
threshold gates), $\mathsf{NC}^1$ (log depth, fan-in 2, equivalently poly-size formulas).

**Reductions and completeness.** $A\le_p B$ (Karp, many-one) if there is a polynomial-time
computable $f$ with $x\in A\iff f(x)\in B$. $B$ is NP-complete if $B\in\mathsf{NP}$ and $A\le_p B$ for
every $A\in\mathsf{NP}$. Cook–Turing reductions ($A\in\mathsf P^B$) are the adaptive version.

**Theorem (Cook 1971, Levin 1973).** SAT is NP-complete. *Proof idea:* given a verifier $V$ running
in time $t=p(|x|)$, the $t\times t$ tableau of its computation on $(x,w)$ is described by $O(t^2)$
Boolean variables, and correctness of the tableau is a conjunction of *local* constraints, each
involving $O(1)$ cells (the transition function acts on a window of constant width). The resulting
CNF $\phi_x$ has size $\mathrm{poly}(|x|)$ and is satisfiable iff some $w$ makes $V$ accept. The locality
of computation is the non-relativizing heart of the theorem and reappears in every modern
technique (arithmetization, PCPs, the easy-witness lemma).

By Karp (1972) and thousands of later reductions, NP-completeness is ubiquitous: 3SAT, CLIQUE,
VERTEX COVER, HAMILTONIAN CYCLE, SUBSET SUM, 3-COLORING, ... all have the property that a
polynomial-time algorithm for any one of them gives one for all of NP.

## 1.2 The question

$$\textbf{Is } \mathsf P=\mathsf{NP}\,?\qquad\text{equivalently:}\qquad \textbf{Is SAT}\in\mathsf P\,?$$

As a sentence of arithmetic, $\mathsf P=\mathsf{NP}$ is $\Sigma_2$:

$$\exists (M,k)\ \forall x\ \big[M \text{ halts on } x \text{ within } |x|^k+k \text{ steps and } M(x)=\mathrm{SAT}(x)\big],$$

and $\mathsf P\ne\mathsf{NP}$ is $\Pi_2$. (The inner predicate is decidable, so both are
genuine arithmetic sentences; this matters for the independence discussion in §1.6.)

## 1.3 Equivalent and adjacent formulations

Each line below is a theorem; the right column records what it buys an attacker.

| # | Statement | Why it holds | Use |
|---|-----------|--------------|-----|
| 1 | $\mathsf P=\mathsf{NP}\iff \mathrm{SAT}\in\mathsf P \iff$ any one NP-complete problem is in P | Cook–Levin, Karp | Pick the most convenient complete problem |
| 2 | $\mathsf P=\mathsf{NP}\Rightarrow$ every NP search problem is solvable in polynomial time ($\mathsf{FP}=\mathsf{FNP}$) | self-reducibility of SAT: fix $x_1$, ask the oracle, continue | Decision and search are interchangeable |
| 3 | $\mathsf P=\mathsf{NP}\Rightarrow \mathsf{PH}=\mathsf P$ | induction on quantifier depth | A P-time SAT solver collapses all finite quantifier alternation |
| 4 | $\mathsf{NP}\ne\mathsf{coNP}\Rightarrow\mathsf P\ne\mathsf{NP}$ | P is closed under complement | The proof-complexity route (Cook–Reckhow) proves something *stronger* |
| 5 | $\mathsf{NP}\not\subseteq\mathsf{P/poly}\Rightarrow\mathsf P\ne\mathsf{NP}$ | $\mathsf P\subseteq\mathsf{P/poly}$ | The circuit route proves something *stronger*; conversely $\mathsf{NP}\subseteq\mathsf{P/poly}\Rightarrow\mathsf{PH}=\Sigma_2^p$ (Karp–Lipton 1980) |
| 6 | one-way functions exist $\Rightarrow\mathsf P\ne\mathsf{NP}$ | inversion is an NP search problem | Cryptography lives strictly inside the $\mathsf P\ne\mathsf{NP}$ world; the converse is open (Impagliazzo's worlds) |
| 7 | $\mathsf{NP}=\mathsf{coNP}\iff$ some propositional proof system is polynomially bounded | Cook–Reckhow 1979 | Superpolynomial lower bounds for *every* proof system would give $\mathsf{NP}\ne\mathsf{coNP}$ |
| 8 | $\mathsf{NP}=$ existential second-order logic on finite structures; $\mathsf P=\mathrm{FO}(\mathrm{LFP})$ on *ordered* finite structures | Fagin 1974; Immerman–Vardi 1982 | P vs NP is a question about logical expressiveness; the "order" caveat is exactly where it gets hard |
| 9 | If a sparse language is NP-complete then $\mathsf P=\mathsf{NP}$ | Mahaney 1982 | NP-complete problems carry exponentially much information per length |
| 10 | $\mathsf{NP}=\mathrm{PCP}(\log n, 1)$; hence $\mathsf P\ne\mathsf{NP}\iff$ no poly-time $(7/8+\varepsilon)$-approximation for MAX-3SAT | Arora–Safra, ALMSS 1992; Håstad 2001 | P vs NP is equivalent to the inapproximability of a specific optimization problem |
| 11 | $\mathsf{MCSP}\in\mathsf{NP}$, so $\mathsf{MCSP}\notin\mathsf P\Rightarrow\mathsf P\ne\mathsf{NP}$ | definition | The meta-complexity route: prove that deciding "has a small circuit" is itself hard |
| 12 | Levin's universal search: there is one fixed algorithm $U$ such that $U$ solves SAT-search in polynomial time iff $\mathsf P=\mathsf{NP}$ | dovetail all programs, verify answers | The question is not "which algorithm" but "is there one"; also $\mathsf P=\mathsf{NP}$ is *witnessed* by an explicit program |
| 13 | If $\mathsf P\ne\mathsf{NP}$ then NP contains problems that are neither in P nor NP-complete | Ladner 1975 | The landscape is not two-valued |
| 14 | $\mathsf{P/poly}$ version: $\mathsf{NEXP}\subseteq\mathsf{P/poly}\iff\mathsf{NEXP}=\mathsf{MA}$ | Impagliazzo–Kabanets–Wigderson 2002 | Non-uniform lower bounds and derandomization are the same subject |

## 1.4 What is known unconditionally

The honest map, as of the writing of this dossier (details and citations in `03-frontier-2026.md`):

**Inclusions.** $\mathsf L\subseteq\mathsf{NL}\subseteq\mathsf P\subseteq\mathsf{NP}\subseteq\mathsf{PH}\subseteq\mathsf{PSPACE}\subseteq\mathsf{EXP}\subseteq\mathsf{NEXP}\subseteq\mathsf{EXPSPACE}$.

**Separations (all by diagonalization/hierarchy theorems, hence relativizing).**
$\mathsf P\ne\mathsf{EXP}$, $\mathsf{NP}\ne\mathsf{NEXP}$, $\mathsf{NL}\ne\mathsf{PSPACE}$, $\mathsf{PSPACE}\ne\mathsf{EXPSPACE}$.
Nothing is known that separates any two adjacent classes in the chain
$\mathsf L\subseteq\mathsf{NL}\subseteq\mathsf P\subseteq\mathsf{NP}\subseteq\mathsf{PH}\subseteq\mathsf{PSPACE}$:
not even $\mathsf L\ne\mathsf{NP}$ or $\mathsf P\ne\mathsf{PSPACE}$.

**Lower bounds that touch NP directly.**
- SAT cannot be solved simultaneously in time $n^{c}$ and space $n^{o(1)}$ for $c<2\cos(\pi/7)\approx1.801$
  (Fortnow 1997 → Williams 2008). Buss–Williams (2012) prove that *this proof template* (alternation
  trading) cannot push $c$ past $2\cos(\pi/7)$.
- Explicit functions in P require $3.1n-o(n)$ gates over $B_2$ (Li–Yang 2022), $n^{3-o(1)}$ De Morgan
  formula size (Håstad 1998, Tal 2014), exponential $\mathsf{AC}^0$ size (Håstad 1986),
  exponential $\mathsf{AC}^0[p]$ size for $p$ prime (Razborov 1987, Smolensky 1987),
  superpolynomial *monotone* circuit size for CLIQUE (Razborov 1985; exponential by Alon–Boppana 1987).
- No explicit function in NP is known to require superlinear circuit size, i.e. $\mathsf{NP}\not\subseteq\mathrm{SIZE}(O(n))$ is open.

**Lower bounds for larger uniform classes.**
$\mathsf{NEXP}\not\subseteq\mathsf{ACC}^0$ (Williams 2011); $\mathsf{NQP}\not\subseteq\mathsf{ACC}^0$ (Murray–Williams 2018);
$\mathsf{MA}_{\mathsf{EXP}}\not\subseteq\mathsf{P/poly}$ (Buhrman–Fortnow–Thierauf 1998);
$\Sigma_2^p\not\subseteq\mathrm{SIZE}(n^k)$ for every fixed $k$ (Kannan 1982; $\mathsf S_2^p$: Cai 2001; $\mathsf{PP}$: Vinodchandran 2005);
$\Sigma_2\mathsf E$ requires circuits of size $2^n/n$ (Li 2024; $\mathsf S_2\mathsf E$: Chen–Hirahara–Ren 2024).

**Oracle facts.** There are oracles $A,B$ with $\mathsf P^A=\mathsf{NP}^A$ and $\mathsf P^B\ne\mathsf{NP}^B$
(Baker–Gill–Solovay 1975); relative to a random oracle, $\mathsf P\ne\mathsf{NP}$ with probability 1
(Bennett–Gill 1981). See `02-barriers.md`.

## 1.5 Why the consensus is $\mathsf P\ne\mathsf{NP}$

Condensed from Aaronson (2016) and the Gasarch polls (2002/2012/2019: roughly 61%/83%/88% of
respondents believe $\mathsf P\ne\mathsf{NP}$):

1. **The empirical hierarchy.** Thousands of NP-complete problems have been attacked independently by
   many communities for fifty years with no polynomial-time algorithm; the problems that *did* fall
   (linear programming, primality, graph isomorphism to quasi-polynomial) were never NP-complete and
   had structure (duality, algebra, group theory) that NP-complete problems lack.
2. **Self-improvement.** $\mathsf P=\mathsf{NP}$ would make mathematics itself feasibly automatable
   (find proofs of length $n$ in time $\mathrm{poly}(n)$), which contradicts the apparent asymmetry between
   finding and checking that we observe everywhere.
3. **Relativized and restricted worlds.** In every restricted model where we *can* prove things
   (monotone circuits, $\mathsf{AC}^0$, communication complexity, proof systems like Resolution, random
   oracles) the NP-side object is hard.
4. **Average-case and cryptography.** A consistent, highly structured theory (one-way functions,
   PRFs, lattice crypto, the Impagliazzo worlds) exists on the $\mathsf P\ne\mathsf{NP}$ side and would
   be a mirage otherwise.

None of this is evidence of the kind a proof needs. The same list would have "predicted" that
linear programming is hard (until Khachiyan 1979) and that primality is hard (until AKS 2002).

## 1.6 The logical status of the question

- $\mathsf P\ne\mathsf{NP}$ is $\Pi_2$. If it is *false*, this is witnessed by a specific machine
  and its correctness is $\Pi_1$-checkable in the limit but not finitely verifiable.
- **Ben-David–Halevi (1992).** If $\mathsf P\ne\mathsf{NP}$ is independent of $\mathrm{PA}+\Pi_1\text{-}\mathrm{Th}(\mathbb N)$ (Peano
  arithmetic plus all true $\Pi_1$ sentences), then SAT has an algorithm running in time
  $n^{\alpha(n)}$ for some unbounded but extremely slow-growing $\alpha$; informally, *independence
  would imply "almost $\mathsf P=\mathsf{NP}$"*. So independence from strong theories is not a comfortable
  way out.
- Unprovability in *weak* theories (bounded arithmetic $\mathrm{PV}$, $\mathrm S^1_2$, $\mathrm{APC}_1$) is a
  live and productive research line (Krajíček; Pich–Santhanam 2021; Chen–Li–Oliveira 2024): it
  formalizes the barriers as unprovability statements. See `03-frontier-2026.md`, proof complexity section.

## 1.7 What a solution must contain

A proof of $\mathsf P\ne\mathsf{NP}$ must exhibit a property of polynomial-time computation that
fails relative to some oracle, fails for low-degree extensions of some oracle, and (if it goes
through $\mathsf{P/poly}$ lower bounds) is not a large, efficiently checkable property of truth tables.
A proof of $\mathsf P=\mathsf{NP}$ must exhibit an algorithm whose correctness analysis does not
relativize either. These three constraints are theorems, not opinions; they are proved in
`02-barriers.md`.
