# 2. Barriers: theorems about what a proof cannot look like

Four theorems constrain every attack on P vs NP. Each is stated precisely; the first is proved in
full, the others are proved in enough detail that the *mechanism* of the obstruction is visible.
The last section turns the four into a specification for the shape of an admissible proof.

## 2.1 Relativization (Baker–Gill–Solovay 1975)

An *oracle machine* $M^{A}$ is a Turing machine with an extra query tape; writing $q$ on it and
entering the query state returns $[q\in A]$ in one step. $\mathsf P^A$ and $\mathsf{NP}^A$ are the
polynomial-time (resp. nondeterministic polynomial-time) oracle classes.

> **Theorem 2.1 (BGS).** (a) There is an oracle $A$ with $\mathsf P^A=\mathsf{NP}^A$.
> (b) There is an oracle $B$ with $\mathsf P^B\ne\mathsf{NP}^B$.

**Proof of (a).** Let $A=\mathrm{TQBF}$, the PSPACE-complete language of true quantified Boolean formulas.
Then $\mathsf{NP}^A\subseteq\mathsf{NPSPACE}$: a nondeterministic polynomial-time oracle machine can be
simulated in polynomial space by evaluating each oracle query with the polynomial-space TQBF
algorithm (space is reused between queries). By Savitch, $\mathsf{NPSPACE}=\mathsf{PSPACE}$.
Conversely $\mathsf{PSPACE}\subseteq\mathsf P^A$ since every PSPACE language Karp-reduces to TQBF.
Hence $\mathsf P^A=\mathsf{NP}^A=\mathsf{PSPACE}$. $\square$

**Proof of (b).** For any oracle $B$ define the unary language
$$L_B=\{1^n:\ \exists y\in B\text{ with }|y|=n\}.$$
$L_B\in\mathsf{NP}^B$ for every $B$: guess $y$ of length $n$, query it. We build $B$ so that $L_B\notin\mathsf P^B$.

Fix an enumeration $M_1,M_2,\dots$ of deterministic oracle machines such that $M_i$ is equipped with a
clock stopping it after $n^i+i$ steps, and such that every polynomial-time oracle machine appears as
some $M_i$ (every machine appears with infinitely many indices, so the clock is eventually generous
enough). We construct finite sets $B_0=\emptyset\subseteq B_1\subseteq B_2\subseteq\cdots$ and numbers
$N_0=0<N_1<N_2<\cdots$ such that every string in $B_i\setminus B_{i-1}$ has length in $(N_{i-1},N_i]$.

*Stage $i$.* Choose $n=n_i>N_{i-1}$ so large that $2^n>n^i+i$. Run $M_i^{B_{i-1}}(1^n)$ (strings
outside $B_{i-1}$ are answered "no"). It halts within $n^i+i<2^n$ steps, so it queries fewer than
$2^n$ strings; in particular some $y_0\in\{0,1\}^n$ is never queried.
- If $M_i$ accepts, set $B_i=B_{i-1}$.
- If $M_i$ rejects, set $B_i=B_{i-1}\cup\{y_0\}$.

Let $N_i$ be the maximum of $n$ and the length of the longest string queried during this run.

Let $B=\bigcup_i B_i$. *Claim: for every $i$, $M_i^B(1^{n_i})\ne[1^{n_i}\in L_B]$.*
Every query made by $M_i$ at stage $i$ has length $\le N_i$, and strings added at later stages have
length $>N_i$; strings added at earlier stages are in $B_{i-1}$ and were answered correctly. So the
run of $M_i^B(1^{n_i})$ is identical to the run at stage $i$ (in the reject case $y_0$ was never queried,
so adding it changes nothing). If $M_i$ accepted, then no string of length $n_i$ is ever put into $B$
(stage $i$ added none, later stages add only longer strings, earlier stages only shorter), so
$1^{n_i}\notin L_B$ and $M_i$ is wrong. If $M_i$ rejected, then $y_0\in B$ and $1^{n_i}\in L_B$, and $M_i$ is
wrong. Since every polynomial-time oracle machine is some $M_i$, $L_B\notin\mathsf P^B$. $\square$

**What it rules out.** Call a proof technique *relativizing* if it proves $\mathsf P^O\ne\mathsf{NP}^O$ (or
$=$) for every oracle $O$ whenever it proves the unrelativized statement. Diagonalization, simulation,
padding, the time/space hierarchy theorems, Karp–Lipton, Kannan, Ladner, Mahaney all relativize:
they treat the machine as a black box with a running time. By Theorem 2.1 none can settle P vs NP.

**What survives.** The only widely used non-relativizing ingredient is the *locality* of
computation (Cook–Levin), exploited through arithmetization: $\mathsf{IP}=\mathsf{PSPACE}$ (Shamir 1992)
fails relative to some oracle (Fortnow–Sipser 1988: $\mathsf{coNP}^O\not\subseteq\mathsf{IP}^O$),
and the random-oracle hypothesis is false (Chang–Chor–Goldreich–Hartmanis–Håstad–Ranjan–Rohatgi
1994). Williams' $\mathsf{NEXP}\not\subseteq\mathsf{ACC}^0$ also does not relativize: the $\mathsf{ACC}^0$-SAT
algorithm uses the gate structure, which oracle gates destroy. Bennett–Gill (1981): $\mathsf P^O\ne\mathsf{NP}^O$
for a random oracle $O$ with probability 1; this is *not* evidence about the real world, for the
same reason.

**Interpretation.** Oracle $A$ shows that nothing distinguishing P from NP survives if both classes
are handed the same enormous resource (PSPACE). So a proof must use that P-machines are *limited
in a specific, local way*, not merely that they are limited in quantity of information.

## 2.2 Natural proofs (Razborov–Rudich 1994, JCSS 1997)

Write $\mathcal F_n$ for the set of all $2^{2^n}$ Boolean functions on $n$ variables; identify $f$ with its
truth table, a string of length $N=2^n$. A *combinatorial property* is a sequence $\Phi=(\Phi_n)$,
$\Phi_n\subseteq\mathcal F_n$.

- $\Phi$ is **$\Gamma$-constructive** if $\{\mathrm{tt}(f): f\in\Phi_n\}\in\Gamma$ as a language over
  $N$-bit strings. "P-natural" means $\Gamma=\mathsf P$, i.e. decidable in time $\mathrm{poly}(N)=2^{O(n)}$.
- $\Phi$ is **large** if $|\Phi_n|\ge 2^{-O(n)}\,|\mathcal F_n|=|\mathcal F_n|/N^{O(1)}$.
- $\Phi$ is **useful against** a circuit class $\Lambda$ if for every family $(f_n)\in\Lambda$ we have
  $f_n\notin\Phi_n$ for all sufficiently large $n$. (So exhibiting $f_n\in\Phi_n$ for infinitely many
  $n$ proves $(f_n)\notin\Lambda$.)

A lower-bound proof is **natural** if it (implicitly or explicitly) establishes a constructive, large
property useful against the target class and shows the target function has the property. Almost
every known lower bound for restricted circuit classes is natural: random restrictions / the
switching lemma (the property "most restrictions do not collapse $f$ to a constant"), the
polynomial approximation method (the property "$f$ is far from every low-degree polynomial over
$\mathbb F_p$"), gate elimination (the property "every restriction of $f$ by few variables still
depends on all remaining variables"), and Shannon-style counting (the property "$C(f)\ge s$",
which is large; whether it is constructive is exactly the MCSP question, see §3 of `03-frontier-2026.md`).

> **Theorem 2.2 (RR).** Suppose there is a pseudorandom function family
> $\{F_s:\{0,1\}^m\to\{0,1\}\}_{s\in\{0,1\}^{m}}$ computable by circuits of size $\mathrm{poly}(m)$ and
> secure against all circuits of size $2^{m^{\varepsilon}}$ (for some $\varepsilon>0$): no such circuit,
> given oracle access to $F_s$ for random $s$ versus a uniformly random function, distinguishes the
> two with advantage $\ge 2^{-m^{\varepsilon}}$. Then there is no P-natural property useful against $\mathsf{P/poly}$.

**Proof.** Let $\Phi$ be P-natural and useful against $\mathsf{P/poly}$. Fix $n$ and put $m=n^{2/\varepsilon}$.
Define $G_s:\{0,1\}^n\to\{0,1\}$ by $G_s(x)=F_s(x0^{m-n})$. The family $(G_s)_s$ is computable by circuits
of size $\mathrm{poly}(m)=\mathrm{poly}(n)$ in the $n$ input bits, so for every $s$ the function $G_s$ lies in a
$\mathsf{P/poly}$ family; by usefulness, $G_s\notin\Phi_n$ for all large $n$ and all $s$. Consider the
distinguisher $D$ that, with oracle access to $g:\{0,1\}^n\to\{0,1\}$, queries all $N=2^n$ inputs,
writes the truth table, and outputs $[g\in\Phi_n]$. $D$ is a circuit of size $2^{O(n)}$ (constructivity).
If $g=G_s$ then $D$ outputs 0. If $g$ is uniformly random then $D$ outputs 1 with probability
$|\Phi_n|/|\mathcal F_n|\ge 2^{-O(n)}$ (largeness). So $D$ distinguishes with advantage $2^{-O(n)}$ using
size $2^{O(n)}$. But $D$ is also a distinguisher for $F_s$ (it only ever queries inputs of the form
$x0^{m-n}$), of size $2^{O(n)}\ll 2^{m^\varepsilon}=2^{n^2}$ and advantage $2^{-O(n)}\gg 2^{-n^2}$,
contradicting security. $\square$

Such PRFs follow from any one-way function with $2^{m^\varepsilon}$ security (Håstad–Impagliazzo–Levin–Luby
1999 + Goldreich–Goldwasser–Micali 1986), e.g. from subexponential hardness of factoring or of
lattice problems. The theorem relativizes to $\Lambda$-natural properties for any $\Lambda$ that can
compute PRFs: $\mathsf{TC}^0$ computes candidate PRFs (Naor–Reingold 1997), so natural proofs are
also barred for $\mathsf{TC}^0$ under standard assumptions; $\mathsf{AC}^0[p]$ and $\mathsf{AC}^0$ cannot
compute PRFs, which is consistent with the fact that we *have* natural lower bounds for them.

**Escapes, with their costs.**
1. *Give up constructivity.* Use a property that is large but hard to decide. Example: $\Phi_n=\{f:C(f)\ge s\}$.
   But then proving $\mathrm{SAT}_n\in\Phi_n$ is the original problem. No known lower bound uses a
   provably non-constructive property.
2. *Give up largeness.* Use a property that singles out structured functions, e.g. "$f$ is
   downward self-reducible and NP-complete". This is the uniform route: it must exploit what SAT
   *is*, not what its truth table looks like. Chow (2011) shows largeness cannot be relaxed only
   slightly: under stronger PRF assumptions even properties of density $2^{-\mathrm{quasipoly}(n)}$ are barred.
3. *Prove a uniform separation.* $\mathsf P\ne\mathsf{NP}$ does not assert $\mathsf{NP}\not\subseteq\mathsf{P/poly}$,
   so a proof that never produces a truth-table property is not touched by Theorem 2.2. It is then
   fully exposed to §2.1 and §2.3.
4. *The algorithmic method.* Williams' proofs are not natural: they do not exhibit a large
   property. Williams (2016, "Natural proofs versus derandomization") shows that constructivity,
   unlike largeness, is *unavoidable* for $\mathsf{NEXP}$ lower bounds: $\mathsf{NEXP}\not\subseteq\mathsf{P/poly}$
   holds if and only if there is a constructive (in an appropriate nondeterministic sense) property
   useful against $\mathsf{P/poly}$, with no largeness requirement. So the escape is *drop largeness,
   keep constructivity*, and that is exactly what the method does.

**A self-defeating twist.** If $2^{m^\varepsilon}$-secure PRFs exist (against non-uniform adversaries) then
one-way functions secure against $\mathsf{P/poly}$ exist, hence $\mathsf{NP}\not\subseteq\mathsf{P/poly}$ is *true*
(inversion is an NP search problem, and search reduces to decision by self-reducibility). Natural
proofs are therefore barred precisely in the worlds where their conclusion holds. The barrier is not
a statement that the lower bound is false; it is a statement that its proof must be *about SAT*,
not about random-looking truth tables.

## 2.3 Algebrization (Aaronson–Wigderson 2008; IKK 2009; Aydınlıoğlu–Bach 2018)

Let $A=(A_n)$ be an oracle with $A_n:\{0,1\}^n\to\{0,1\}$. For a field $\mathbb F$, an **extension** of $A$
is a family $\tilde A=(\tilde A_{n,\mathbb F})$ of polynomials $\tilde A_{n,\mathbb F}:\mathbb F^n\to\mathbb F$ that
agree with $A_n$ on $\{0,1\}^n$ and have degree bounded by a polynomial in $n$ (the multilinear extension
is the canonical choice; AW allow any low-degree extension). A machine with oracle $\tilde A$ may
query $\tilde A_{n,\mathbb F}$ at arbitrary points of $\mathbb F^n$, for any finite field (or the integers) it names.

> **Definition.** An inclusion $\mathcal C\subseteq\mathcal D$ *algebrizes* if $\mathcal C^{A}\subseteq\mathcal D^{\tilde A}$
> for every oracle $A$ and every extension $\tilde A$. A separation $\mathcal C\not\subseteq\mathcal D$ algebrizes if
> $\mathcal C^{\tilde A}\not\subseteq\mathcal D^{A}$ for every $A,\tilde A$.

(The asymmetry — one side gets the extension — is what makes arithmetization-based proofs fit: the
prover side uses the polynomial, the verifier side only the Boolean oracle.)

> **Theorem 2.3 (AW).**
> 1. $\mathsf{PSPACE}^{A}\subseteq\mathsf{IP}^{\tilde A}$ and $\mathsf{NEXP}^{A}\subseteq\mathsf{MIP}^{\tilde A}$ for all $A,\tilde A$: the interactive-proof
>    theorems algebrize.
> 2. There exist $A,\tilde A$ with $\mathsf{NP}^{\tilde A}\subseteq\mathsf P^{A}$. Hence no algebrizing proof shows $\mathsf P\ne\mathsf{NP}$.
> 3. There exist $A,\tilde A$ with $\mathsf{NP}^{A}\not\subseteq\mathsf P^{\tilde A}$. Hence no algebrizing proof shows $\mathsf P=\mathsf{NP}$.
> 4. Likewise, $\mathsf{NEXP}\not\subseteq\mathsf{P/poly}$ and $\mathsf{NP}\not\subseteq\mathrm{SIZE}(n)$ (among others) require non-algebrizing techniques.

**Mechanism of (2).** Take $A$ PSPACE-complete and $\tilde A$ its multilinear extension. Evaluating a
multilinear extension at a point of $\mathbb F^n$ is a sum over the Boolean cube weighted by products of
$x_i$ or $(1-x_i)$, computable in polynomial space given $A$. So $\mathsf{NP}^{\tilde A}\subseteq\mathsf{PSPACE}=\mathsf P^{A}$.

**Mechanism of (3).** Diagonalize as in BGS, but the adversary now queries the *polynomial* $\tilde A_n$ at
field points, which could in principle leak information about all of $\{0,1\}^n$. The key lemma is an
*algebraic query complexity* bound: any algorithm that makes $q<2^n$ queries to a (multilinear or
low-degree) extension cannot decide whether $A_n$ is identically zero on $\{0,1\}^n$, because the space of
multilinear polynomials on $n$ variables has dimension $2^n$, so for any $q<2^n$ query points there is a
nonzero multilinear polynomial vanishing at all of them, which can be added to $\tilde A_n$ without
changing any answer the algorithm has seen but changing a value on the cube. The construction then
proceeds stage by stage with the language $L_A=\{1^n:\exists y\in A, |y|=n\}$ exactly as in Theorem 2.1(b).

**What it rules out.** Every relativizing technique (trivially) and every technique whose only
non-relativizing ingredient is arithmetization of local computation. IKK (2009) make this axiomatic:
a theory consisting of relativizing reasoning plus an "arithmetic checkability" axiom proves
$\mathsf{IP}=\mathsf{PSPACE}$ and $\mathsf{MIP}=\mathsf{NEXP}$ but is consistent with both $\mathsf P=\mathsf{NP}$ and $\mathsf P\ne\mathsf{NP}$.
Aydınlıoğlu–Bach (2018) give the cleaner *affine relativization*, under which the known
"non-relativizing" results relativize while P vs NP does not.

**What survives.** Williams' algorithmic method: the $\mathsf{ACC}^0$-SAT algorithm exploits the
*Yao–Beigel–Tarui* structure of $\mathsf{ACC}^0$ circuits, which is destroyed by an oracle gate, Boolean or
algebraic. More generally, any argument that uses the *specific algorithmic structure* of the lower
class (as opposed to its ability to compute a fixed algebraic encoding) is a candidate to evade both
§2.1 and §2.3.

## 2.4 Locality (Chen–Hirahara–Oliveira–Pich–Rajgopal–Santhanam, ITCS 2020; JACM 2022)

*Hardness magnification* (Oliveira–Santhanam 2018 and successors) proves implications of the form

$$\text{"problem } Q\text{ on } N\text{-bit inputs requires circuits of size } N^{1+\varepsilon}\text{ (or formulas of size } N^{3+\varepsilon}\text{, or ...)"}\ \Longrightarrow\ \mathsf{NP}\not\subseteq\mathsf{P/poly},$$

for carefully chosen $Q$ (gap versions of MCSP, MKtP, compression problems), where the hypothesised
lower bound is only *slightly* beyond what is known for *some* explicit functions in the same model.
The locality barrier explains why the known-lower-bound side does not meet the hypothesis.

> **Definition.** A lower-bound technique for a circuit model $\mathcal M$ is *local* if it establishes the
> same lower bound against $\mathcal M$-circuits augmented with arbitrary oracle gates of small fan-in
> (fan-in $\ell(N)$, typically $N^{o(1)}$ or $\mathrm{polylog}(N)$), i.e. it never uses that the sub-functions
> computed inside the circuit are themselves easy.

> **Theorem 2.4 (CHOPRS, schematically).** The magnification targets $Q$ admit $\mathcal M$-circuits of
> size below the magnification threshold when oracle gates of fan-in $N^{o(1)}$ are allowed. Hence no
> local technique can prove the hypothesis of the magnification theorem for $Q$.

All currently known lower-bound techniques for the relevant weak models (gate elimination, random
restrictions, the switching lemma, polynomial approximation, Nechiporuk, communication-based
formula bounds, Andreev-type function bounds) are local in this sense: they go through unchanged if
one inserts a few small-fan-in black boxes, because they only ever argue about restrictions and
about counting sub-functions. A technique that proves the magnification hypothesis must therefore
*use that the oracle-free circuit cannot compute the hard sub-functions*, which is self-referential:
one must already know something is hard to prove that MCSP is hard.

## 2.5 Smaller, sharper obstructions

- **Gate elimination ceiling.** Golovnev–Hirsch–Knop–Kulikov (2016) formalize the gate-elimination
  method with "measure" arguments and show it cannot prove lower bounds better than a small constant
  times $n$ for general circuits. Combined with Li–Yang's $3.1n$, the method is near its end.
- **Alternation-trading ceiling.** Buss–Williams (2012) prove that the indirect-diagonalization
  template behind every known SAT time-space lower bound cannot exceed exponent $2\cos(\pi/7)$.
- **Feasible interpolation fails for strong proof systems.** Krajíček–Pudlák (1998) and
  Bonet–Pitassi–Raz (2000): Frege and Extended Frege do not admit feasible interpolation unless
  factoring/RSA is easy, so the main lower-bound technique for weak proof systems (Resolution,
  Cutting Planes) is barred for the systems whose lower bounds would approach $\mathsf{NP}\ne\mathsf{coNP}$.
- **Unprovability in bounded arithmetic.** Razborov (1995): under PRF existence, the theory
  $\mathrm S^2_2(\alpha)$ cannot prove superpolynomial circuit lower bounds (a formalization of §2.2).
  Pich–Santhanam (2021) and Chen–Li–Oliveira (2024) sharpen this to specific statements about
  $\mathsf{NP}$ and the theory $\mathrm{APC}_1$ / $\mathrm{PV}$; see `03-frontier-2026.md`.
- **Black-box worst-to-average amplification within NP.** Feigenbaum–Fortnow (1993),
  Bogdanov–Trevisan (2006): non-adaptive black-box reductions from worst-case NP hardness to
  average-case NP hardness collapse PH. So "P≠NP ⟹ cryptography" cannot be proved by the standard
  reduction template; Hirahara's non-black-box reductions (2018–) are the response.

## 2.6 The specification: what a proof of $\mathsf P\ne\mathsf{NP}$ must do

| Technique | Relativizes | Algebrizes | Natural | Local | Verdict |
|-----------|:-----------:|:----------:|:-------:|:-----:|---------|
| Diagonalization / hierarchy theorems | yes | yes | — | — | cannot work alone (§2.1) |
| Karp–Lipton, Kannan, Ladner, Mahaney | yes | yes | — | — | give structure, not separations |
| Arithmetization (IP, MIP, PCP) | **no** | yes | — | — | not enough alone (§2.3) |
| Random restrictions, approximation method, gate elimination | — | — | **yes** | **yes** | capped at weak classes (§2.2, §2.4) |
| Shannon counting | — | — | large, non-constructive | — | says nothing about explicit functions |
| Williams' algorithmic method | **no** | **no** | **no** | — | reaches $\mathsf{NQP}\not\subseteq\mathsf{ACC}^0$; needs faster SAT algorithms and a route from NEXP/NQP down to NP |
| Range avoidance / single-valued $\mathsf{F}\Sigma_2\mathsf P$ algorithms | no | no | no | — | reaches $\Sigma_2\mathsf E\not\subseteq\mathrm{SIZE}(2^n/n)$; same descent problem |
| Magnification with a *non-local* lower bound | — | — | — | must be **no** | no non-local technique is known |
| Proof complexity (Frege lower bounds) | — | — | needs non-interpolation methods | — | Frege open; would give $\mathsf{NP}\ne\mathsf{coNP}$ only if *all* systems fall |

**Consequence.** A proof of $\mathsf P\ne\mathsf{NP}$ must (i) exploit the locality/uniformity of
polynomial-time computation in a way that is destroyed by low-degree algebraic oracles — in
practice, exploit the *algorithmic* structure of the class being lower-bounded, as the algorithmic
method does; (ii) either prove a uniform separation (no truth-table property at all) or exhibit a
property that is not large, i.e. one that is *about SAT specifically*; and (iii) if it routes through
a weak lower bound for a meta-computational problem, use the hardness of the sub-functions inside
the circuit. No existing technique satisfies all three at the scale of NP. The dossier's attack
vectors (`04-attack-vectors.md`) are ranked by how much of this specification they already meet.
