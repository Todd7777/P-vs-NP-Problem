# 5. Worked mathematics

Self-contained proofs of the results that every serious attack leans on, written out so that the
exact point where each one stops short of P vs NP is visible. Where this dossier's experiments
(`../experiments/`) touch a theorem, the numbers are quoted.

## 5.1 Almost all functions are hard (Shannon 1949), and why that is useless for SAT

Let $\mathcal F_n$ be the set of Boolean functions on $n$ variables, $|\mathcal F_n|=2^{2^n}$, and let $C(f)$ be
the minimum number of fan-in-2 gates (basis $B_2$) computing $f$.

> **Theorem 5.1.** For all sufficiently large $n$, all but a $2^{-\Omega(2^n\log n/n)}$ fraction of
> $f\in\mathcal F_n$ satisfy $C(f)>2^n/n$.

**Proof.** Count circuits. A circuit with exactly $s$ gates and a designated output gate can be
written as a list of $s$ gates, each specified by its operation (16 choices) and its two inputs
(each among the $n$ variables and the $s$ gates, giving at most $(n+s)^2$ choices; we overcount by
also allowing cyclic or forward references). This gives at most $(16(n+s)^2)^s$ labelled
descriptions. Every genuine circuit with output gate fixed as gate number $s$ is described by
$(s-1)!$ of them (relabel the other gates). Therefore
$$\#\{f: C(f)\le s\}\ \le\ \frac{(16(n+s)^2)^s}{(s-1)!}\quad(\text{pad smaller circuits with useless gates}).$$
Take logarithms base 2 and use $(s-1)!\ge((s-1)/e)^{s-1}$: for $s=2^n/n$ (so $s\gg n$),
$$\log_2\#\{f:C(f)\le s\}\ \le\ s\big(\log_2 s+\log_2(16e)+o(1)\big)
= \frac{2^n}{n}\big(n-\log_2 n+5.5+o(1)\big)=2^n\Big(1-\frac{\log_2 n-5.5-o(1)}{n}\Big).$$
Dividing by $|\mathcal F_n|=2^{2^n}$ gives the fraction $2^{-2^n(\log_2 n-5.5-o(1))/n}$. $\square$

Lupanov (1958) proved the matching upper bound $C(f)\le(1+o(1))2^n/n$ for *every* $f$, so the
maximum circuit complexity on $n$ variables is $(1+o(1))\,2^n/n$.

**Why this says nothing about SAT.** The proof never looks at a function; it only counts. SAT on
$n$-bit inputs is one specific function $\mathrm{SAT}_n$, and the best we can prove about it is
$C(\mathrm{SAT}_n)\ge 3.1n-o(n)$ (Li–Yang 2022, for a function in P). Worse: one *cannot* fix the
proof by adding "and here is how to check that $\mathrm{SAT}_n$ is one of the hard ones":

> **Proposition 5.2 (Kabanets–Cai 2000, via Razborov–Rudich).** If $2^{m^\varepsilon}$-secure PRFs exist
> (§2.2), then the Minimum Circuit Size Problem $\mathrm{MCSP}=\{(\mathrm{tt}(f),s): C(f)\le s\}$ is not in P.

**Proof.** If MCSP were in P, the property $\Phi_n=\{f: C(f)>n^{\log n}\}$ would be P-constructive
(run the MCSP algorithm on the $2^n$-bit truth table with $s=n^{\log n}$: time $\mathrm{poly}(2^n)$),
large (by Theorem 5.1, since $n^{\log n}\ll 2^n/n$), and useful against $\mathsf{P/poly}$. Theorem 2.2
forbids this. $\square$

So the counting argument's property "$C(f)>s$" is large and useful — the two properties a natural
proof needs — and the only thing stopping it from being a natural proof is that it is (conjecturally)
*not constructive*. That is the whole of meta-complexity in one sentence: MCSP sits exactly at the
boundary between what counting gives for free and what the natural-proofs barrier forbids.

**Small-$n$ reality check (experiment `exact_circuit_complexity.py`).** For $n=4$ the asymptotic
value $2^n/n=4$ is far from the truth: the exact distribution of $C(f)$ over all 65,536 functions
of 4 variables (computed here by SAT-based exact synthesis, matching Knuth, TAOCP 4A §7.1.2) has
maximum 7. For $n=5$ Knuth's exhaustive computation gives maximum 12 versus $2^5/5=6.4$ (a single
NPN class of 1,920 functions; checked here against Knuth's own table of optimal chains as packaged in
optimal5, `experiments/compare_optimal5.py`). The
$o(1)$ terms in Shannon–Lupanov are large at small $n$; the asymptotics are trustworthy only for
$n$ in the dozens, where exhaustive computation is impossible ($2^{2^n}$ functions).

## 5.2 A complete lower bound proof: Schnorr's $3(n-1)$ bound for parity over $U_2$

$U_2$ is the basis of all binary functions except $\oplus$ and $\equiv$. Every $g\in U_2$ that depends
on both of its arguments has the form
$$g(a,b)=\big((a\oplus\alpha)\wedge(b\oplus\beta)\big)\oplus\gamma\qquad(\alpha,\beta,\gamma\in\{0,1\}),$$
(the eight "AND-type" functions; together with 2 constants, 4 functions of one argument, and the 2
XOR-type functions this exhausts the 16). Let $\oplus_n(x)=x_1\oplus\cdots\oplus x_n$ and let $C_{U_2}$ count
gates over $U_2$, with the convention (as in §5.1 and in the experiments) that $f$ and $\neg f$ have the same cost.

> **Theorem 5.3 (Schnorr 1974).** $C_{U_2}(\oplus_n)=3(n-1)$ for all $n\ge 1$.

**Upper bound.** $a\oplus b=(a\wedge\neg b)\vee(\neg a\wedge b)$ uses two AND-type gates and one OR: three
$U_2$ gates. Chain $n-1$ of these.

**Lower bound, by induction on $n$.** For $n=1$ the function is a projection, cost $0$. Let $n\ge 2$
and let $\mathcal C$ be a minimum-size $U_2$ circuit for $\oplus_n$. Every gate of $\mathcal C$ depends on both of
its inputs (a gate that does not can be removed, contradicting minimality), so every gate is
AND-type. Let $g$ be a gate whose two inputs are variables, say $x_i,x_j$ (the first gate in
topological order is such), $g=((x_i\oplus\alpha)\wedge(x_j\oplus\beta))\oplus\gamma$.

*Claim: $x_i$ feeds at least two gates.* Suppose $g$ is the only gate reading $x_i$. Set $x_j:=\beta$.
Then $x_j\oplus\beta=0$, so $g\equiv\gamma$ regardless of $x_i$, and the whole circuit becomes independent
of $x_i$. But $\oplus_n|_{x_j=\beta}=\beta\oplus\bigoplus_{l\ne j}x_l$ depends on $x_i$ (as $n\ge2$). Contradiction.
By symmetry (set $x_i:=\alpha$), $x_j$ also feeds at least two gates.

*Elimination.* Set $x_i:=\alpha$. Then $g\equiv\gamma$. We now remove gates while preserving the function
computed, which is $\oplus_n|_{x_i=\alpha}=\alpha\oplus\oplus_{n-1}$ on the remaining variables:
- $g$ is constant: remove it; every gate $h$ reading $g$ now depends on at most one input.
- Every gate $h'$ reading $x_i$ (there is at least one with $h'\ne g$, by the Claim) now reads a constant,
  so it depends on at most one input.
- A gate that depends on at most one input computes a constant or a literal; remove it and let its
  successors read that literal directly, absorbing any negation into the successor's operator
  ($U_2$ is closed under negating an input). If it computes a constant, its successors in turn depend
  on at most one input, and the removal cascades.

We count distinct removed gates. $g$ is removed. $g$ is not the output gate (the output depends on
all $n\ge2$ variables through a non-AND-type function), so $g$ has a successor $h$. Either (a) $h$ does
not read $x_i$: then $h$ depends on at most one input after the substitution and is removed, and
in addition some $h'\ne g$ reading $x_i$ is removed, with $h'\ne h$ since $h$ does not read $x_i$ — three
distinct gates $g,h,h'$; or (b) $h$ reads both $g$ and $x_i$: then $h$ becomes constant and is removed,
and $h$ is not the output (at $x_i=\alpha$ the output still depends on $x_j$, but $h$ is constant), so
$h$ has a successor $h_2\notin\{g,h\}$, which now depends on at most one input and is removed — three
distinct gates $g,h,h_2$. In both cases the result is a $U_2$ circuit with at least $3$ fewer gates
computing $\alpha\oplus\oplus_{n-1}$, whose cost equals $C_{U_2}(\oplus_{n-1})$ under the $f/\neg f$ convention
(complement the output gate's operator; if no gate remains the function is a literal, cost $0$).
Hence $C_{U_2}(\oplus_n)\ge 3+C_{U_2}(\oplus_{n-1})\ge 3(n-1)$. $\square$

**Contrast.** Over $B_2$, $C(\oplus_n)=n-1$: the upper bound is a chain of XORs, and any circuit whose
output depends on $n$ variables needs $n-1$ gates (each gate joins at most two connected components
of the wiring graph). So the same function is "hard" in one basis and trivially easy in another;
every circuit lower bound is a statement about a *basis*.

**Experimental confirmation.** SAT-based exact synthesis finds $C_{U_2}(\oplus_2)=3$,
$C_{U_2}(\oplus_3)=6$, $C_{U_2}(\oplus_4)=9$, with every smaller gate count refuted by a DRAT proof that
drat-trim checked (`experiments/circuit_sat.py`, `experiments/results/certificates.json`), and
$C_{B_2}(\oplus_n)=n-1$ for $n\le5$. For $\oplus_5$ over $U_2$ the first run found a 12-gate circuit
(re-evaluated on all 32 inputs) and refuted up to 8 gates before its conflict budget ran out. No
further search is needed. The synthesizer's cost model is the one used here: its chains use
normal $U_2$ operators, which are $U_2$ gates, and every $U_2$ chain can be made normal without adding
gates (`experiments/ENCODING.md`, Lemma 1). So Theorem 5.3 supplies the matching lower bound:

> $C_{U_2}(\oplus_5)=12$. **Theorem**: the lower bound is Theorem 5.3, and the upper bound is the
> construction above or the explicit 12-gate circuit in `experiments/results/explicit_costs.json`
> (also listed in `experiments/results/explicit_final.json`).

**Why gate elimination stops at $\approx3n$.** The argument removes a constant number of gates per
eliminated variable. Li–Yang (2022) push the constant to $3.1$ with an elaborate case analysis and
a cleverly chosen function; Golovnev–Hirsch–Knop–Kulikov (2016) show that the method, formalized as
a measure argument, cannot give superlinear bounds. There is no known way to remove $\omega(1)$ gates
per variable for an explicit function. This is the entire state of the art for unrestricted
circuits, after fifty years.

## 5.3 Kannan's theorem: a fixed-polynomial lower bound two levels above NP

> **Theorem 5.4 (Kannan 1982).** For every $k$, $\Sigma_2^p\not\subseteq\mathrm{SIZE}(n^k)$.

**Proof.** *Case 1: $\mathsf{NP}\not\subseteq\mathsf{P/poly}$.* Then SAT has no polynomial-size circuits, so in
particular $\mathrm{SAT}\notin\mathrm{SIZE}(n^k)$, and $\mathrm{SAT}\in\mathsf{NP}\subseteq\Sigma_2^p$.

*Case 2: $\mathsf{NP}\subseteq\mathsf{P/poly}$.* By Karp–Lipton (Theorem 5.6 below) $\mathsf{PH}=\Sigma_2^p$. Define the
language $L_k$ as follows. For each $n$, by Theorem 5.1 there is a circuit of size $\le n^{k+1}$ on $n$
inputs computing a function of circuit complexity $>n^k$ (for large $n$, since $n^{k+1}\ll2^n/n$); let
$C^*_n$ be the lexicographically first such circuit (in a fixed encoding), and put
$L_k\cap\{0,1\}^n=\{x: C^*_n(x)=1\}$. By construction $L_k\notin\mathrm{SIZE}(n^k)$. We show $L_k\in\mathsf{PH}$:
"$C$ has no equivalent circuit of size $\le n^k$" is $\forall D\,\exists y\,[C(y)\ne D(y)]$, a $\Pi_2^p$
predicate; "$C$ is lexicographically first with this property" adds $\forall C'<C\,\exists D'\,\forall y\,[C'(y)=D'(y)]$,
a $\Pi_3^p$ predicate; so $x\in L_k$ iff $\exists C\,[C=C^*_{|x|}\wedge C(x)=1]$ is in $\Sigma_4^p=\Sigma_2^p$ in this case.
In both cases $\Sigma_2^p\not\subseteq\mathrm{SIZE}(n^k)$. $\square$

Cai (2001) lowers the class to $\mathsf S_2^p$, and Vinodchandran (2005) proves $\mathsf{PP}\not\subseteq\mathrm{SIZE}(n^k)$.
Nothing of this kind is known for $\mathsf{NP}$ itself: $\mathsf{NP}\not\subseteq\mathrm{SIZE}(n^k)$ is open for every $k\ge1$,
and $\mathsf{NP}\not\subseteq\mathrm{SIZE}(O(n))$ is open. The proof above relativizes, so by §2.1 the
case analysis can never reach $\mathsf{NP}$ on its own. The 2024 results of Chen–Hirahara–Ren and Li
replace "fixed polynomial" by the Shannon maximum $2^n/n$ for the exponential analogue $\Sigma_2\mathsf E$,
by giving a single-valued $\mathsf F\Sigma_2\mathsf P$ algorithm for the Range Avoidance problem (an
explicit-construction task), which is a genuinely new, non-relativizing ingredient; see
`03-frontier-2026.md`.

## 5.4 Cook–Reckhow: proof complexity is exactly NP vs coNP

A *propositional proof system* is a polynomial-time computable surjection $P:\{0,1\}^*\to\mathrm{TAUT}$; a
string $\pi$ with $P(\pi)=\phi$ is a $P$-proof of $\phi$. $P$ is *polynomially bounded* if every tautology
$\phi$ has a $P$-proof of length $\le\mathrm{poly}(|\phi|)$.

> **Theorem 5.5 (Cook–Reckhow 1979).** $\mathsf{NP}=\mathsf{coNP}$ iff some propositional proof system is polynomially bounded.

**Proof.** ($\Leftarrow$) If $P$ is polynomially bounded then $\mathrm{TAUT}\in\mathsf{NP}$ (guess $\pi$, check
$P(\pi)=\phi$); TAUT is coNP-complete, so $\mathsf{coNP}\subseteq\mathsf{NP}$ and hence $\mathsf{NP}=\mathsf{coNP}$.
($\Rightarrow$) If $\mathsf{NP}=\mathsf{coNP}$ then $\mathrm{TAUT}\in\mathsf{NP}$ via some verifier $V$ with witnesses of
length $p(|\phi|)$; define $P(\langle\phi,w\rangle)=\phi$ if $V(\phi,w)=1$ and $P(\cdot)=\top$ (a fixed tautology)
otherwise. $P$ is a polynomially bounded proof system. $\square$

Consequently, to prove $\mathsf{NP}\ne\mathsf{coNP}$ (and so $\mathsf P\ne\mathsf{NP}$) it suffices to prove a
superpolynomial lower bound *for every* proof system. Lower bounds are known for Resolution,
bounded-depth Frege, Cutting Planes, Polynomial Calculus, Sum-of-Squares; they are open for
$\mathsf{AC}^0[p]$-Frege, Frege, and Extended Frege. Our experiment `proof_complexity_php.py` is the
empirical face of Haken's theorem: a CDCL solver, whose runs are Resolution refutations, needed
$1.0\times10^3, 7.1\times10^3, 3.2\times10^4, 2.7\times10^5, 2.2\times10^6, 1.4\times10^7$ conflicts on
$\mathrm{PHP}_n$ for $n=6,\dots,11$ (a factor $\approx7$ per step, i.e. $2^{\Theta(n)}$), while the ordering
principle $\mathrm{GT}_n$, which has polynomial-size Resolution refutations, was refuted at $n=80$
(6,320 variables) in a few seconds.

## 5.5 Karp–Lipton: non-uniform upper bounds collapse the hierarchy

> **Theorem 5.6 (Karp–Lipton 1980).** If $\mathsf{NP}\subseteq\mathsf{P/poly}$ then $\mathsf{PH}=\Sigma_2^p$.

**Proof.** It suffices to show $\Pi_2^p\subseteq\Sigma_2^p$. If SAT has circuits of size $n^c$, then by
self-reducibility there are circuits $D_n$ of size $\mathrm{poly}(n)$ that, given a satisfiable formula of
size $n$, *output a satisfying assignment* (fix $x_1$ to each value, query the decision circuit, and
continue). Let $L=\{x:\forall y\,\exists z\,\phi(x,y,z)\}\in\Pi_2^p$, with $\phi$ polynomial-time. Then
$$x\in L\iff\exists D\ \forall y\ \big[\phi\big(x,y,D(\phi(x,y,\cdot))\big)=1\big],$$
where $D$ ranges over circuits of the appropriate polynomial size: if $x\in L$ the witness-producing
circuit works for every $y$; if $x\notin L$ some $y$ has no $z$, so no $D$ can succeed on it. The right
side is $\Sigma_2^p$. $\square$

This is the lemma that converts "small circuits for NP" into "collapsed quantifier structure", and
it is the engine inside Kannan and inside the easy-witness lemma. It relativizes.

## 5.6 The algorithmic method (Williams 2010–2014; Murray–Williams 2018)

> **Lemma 5.7 (Easy witness, Impagliazzo–Kabanets–Wigderson 2002).** If $\mathsf{NEXP}\subseteq\mathsf{P/poly}$ then every
> language in $\mathsf{NEXP}$ has *succinct witnesses*: for every NEXP verifier there is a $k$ such that every
> accepted input $x$ has an accepting witness $w$ (of length $2^{|x|^{O(1)}}$) whose truth table is computed
> by a circuit of size $|x|^k$.

(Proof idea: if some verifier lacked succinct witnesses, witnesses would be hard truth tables, which
can be used as hardness for a Nisan–Wigderson generator to derandomize $\mathsf{MA}$ into $\mathsf{NEXP}$
in a way that, combined with $\mathsf{NEXP}\subseteq\mathsf{P/poly}\Rightarrow\mathsf{NEXP}=\mathsf{MA}$, contradicts the
nondeterministic time hierarchy.)

> **Theorem 5.8 (Williams).** Let $\mathcal C$ be a circuit class (closed under the usual operations). If
> satisfiability of $\mathcal C$-circuits of size $n^{O(1)}$ on $n$ inputs can be decided in time $2^n/n^{\omega(1)}$,
> then $\mathsf{NEXP}\not\subseteq\mathcal C$.

**Proof sketch.** Suppose $\mathsf{NEXP}\subseteq\mathcal C$. SUCCINCT-3SAT (input: a circuit $D$ describing a
$2^m$-clause 3CNF; question: is it satisfiable?) is NEXP-complete under reductions that are tight
enough that an $\mathrm{NTIME}(2^m/m^{\omega(1)})$ algorithm for it violates the nondeterministic time
hierarchy. By Lemma 5.7 (and its refinement to $\mathcal C$-witnesses, which uses $\mathsf P\subseteq\mathcal C$), every
satisfiable $D$ has a satisfying assignment computed by a $\mathcal C$-circuit $W$ of size $\mathrm{poly}(m)$.
Algorithm: nondeterministically guess $W$; also guess a $\mathcal C$-circuit $D'$ equivalent to the clause
generator $D$ (exists since $\mathsf P\subseteq\mathcal C$; verify equivalence with one $\mathcal C$-SAT call on
$\neg(D\leftrightarrow D')$, a $\mathcal C$-circuit on $m+O(1)$ inputs); then build the $\mathcal C$-circuit
$E(i)=$"clause $i$ of $D'$ is falsified by $W$" on $m$ inputs and call the fast $\mathcal C$-SAT algorithm on
$E$: $D$ is satisfiable iff some guess makes $E$ unsatisfiable. Total time $\mathrm{poly}(m)+2^m/m^{\omega(1)}$,
a contradiction with the hierarchy theorem. $\square$

Williams then gives a $2^{n-n^{\varepsilon}}$-time satisfiability algorithm for $\mathsf{ACC}^0$ circuits of size
$2^{n^{\varepsilon}}$, via the Yao–Beigel–Tarui representation of $\mathsf{ACC}^0$ as symmetric functions of
$2^{\mathrm{polylog}}$ monomials and fast rectangular matrix multiplication; hence $\mathsf{NEXP}\not\subseteq\mathsf{ACC}^0$.
Murray–Williams (2018) prove an easy-witness lemma for $\mathsf{NP}$ and $\mathsf{NQP}$ (if $\mathsf{NP}\subseteq\mathrm{SIZE}(n^k)$
then NP witnesses have circuits of size $n^{O(k^3)}$-ish, with a fixed polynomial loss) and derive
$\mathsf{NQP}\not\subseteq\mathsf{ACC}^0$.

**Why the method evades all three classic barriers.** It does not relativize (the SAT algorithm
inspects gate structure; an oracle gate has none) and does not algebrize (same reason; the
structure exploited is combinatorial, not a low-degree encoding). It is not natural: it never
exhibits a large property; the lower bound comes from the hierarchy theorem contradiction.

**Why it stops short of NP, quantitatively.** For an NP language the witness has polynomial
length $n^c$, so a succinct witness circuit $W$ has only $m=c\log n$ inputs. The fast $\mathcal C$-SAT
algorithm then saves a factor $m^{\omega(1)}=(\log n)^{\omega(1)}$ over brute force: the verification of
"all $n^c$ clauses satisfied" costs $n^c/(\log n)^{\omega(1)}$ instead of $n^c$. The nondeterministic time
hierarchy does separate $\mathrm{NTIME}(n^c)$ from $\mathrm{NTIME}(n^c/(\log n)^{\omega(1)})$, so the *shape* of a
contradiction is available; what breaks is the accounting: guessing and verifying $W$ and $D'$ costs
polynomial factors ($n^{O(k^3)}$ from the easy-witness lemma), which swamp a polylogarithmic saving.
For $\mathsf{NQP}$ the witness circuits have $m=\mathrm{polylog}(n)$ inputs and the saving $m^{\omega(1)}$ is
quasi-polynomial, which beats the polynomial overheads: that is exactly the Murray–Williams
threshold. To reach $\mathsf{NP}\not\subseteq\mathsf{ACC}^0$ by this route one needs either (i) a
$\mathcal C$-SAT algorithm with *polynomial* savings on circuits with $O(\log n)$ inputs — i.e. time
$2^{m}/2^{\Omega(m)}=2^{(1-\varepsilon)m}$ for size-$2^{O(m)}$... which for $m=\log n$ means solving
$\mathcal C$-SAT on circuits of size $\mathrm{poly}(n)$ with $\log n$ inputs in time $n^{1-\varepsilon}$, impossible since
reading the circuit takes time $n$ — or (ii) an easy-witness lemma with only polylogarithmic
overhead, or (iii) a different contradiction engine than the hierarchy theorem. Option (iii) is
where hardness magnification enters (`04-attack-vectors.md`), and where the locality barrier waits.

## 5.7 The two ladders

**Impagliazzo's worlds (1995), as a ladder of implications that are each open.**

$$\text{PRFs / OWFs exist}\ \Rightarrow\ \text{DistNP}\not\subseteq\text{AvgP}\ \Rightarrow\ \mathsf P\ne\mathsf{NP}.$$

Both arrows point the "wrong" way for proving $\mathsf P\ne\mathsf{NP}$; the converses are the open
questions "does $\mathsf P\ne\mathsf{NP}$ imply average-case hardness?" (Heuristica) and "does
average-case hardness imply OWFs?" (Pessiland). Bogdanov–Trevisan show the first converse has no
non-adaptive black-box proof; Hirahara's meta-complexity program (`03-frontier-2026.md`) is the
systematic attempt to prove both converses non-black-box, via NP-hardness of MCSP-like problems.

**Hardness vs randomness.**

$$\mathsf E\not\subseteq\mathrm{SIZE}(2^{\varepsilon n})\ \Rightarrow\ \mathsf{prBPP}=\mathsf{prP}\ \Rightarrow\ \mathsf{NEXP}\not\subseteq\mathsf{P/poly}\ \text{or}\ \mathrm{perm}\notin\mathsf{VP}.$$

(Impagliazzo–Wigderson 1997; Kabanets–Impagliazzo 2004 for the PIT version; Williams 2013 for
the $\mathsf{prBPP}$ version.) Note the ceiling: since $\mathsf P=\mathsf{NP}$ already implies $\mathsf{prBPP}=\mathsf{prP}$,
no derandomization result can imply $\mathsf P\ne\mathsf{NP}$; the ladder tops out at $\mathsf{NEXP}$ lower bounds
and at "almost-NP" lower bounds (Tell 2019). This is the single most important sanity check for
any plan that goes through derandomization.

## 5.8 Two short facts that constrain plans

1. **No counting argument separates P from NP.** There are only $2^{n^{O(1)}}$ languages in $\mathsf P\cap\{0,1\}^{\le n}$
   up to length $n$, and the same holds for NP: both are countable classes of the same "size" in
   every counting sense that is available; counting separates $\mathsf P$ from $\mathsf{P/poly}$ or from
   $\mathcal F_n$, never from $\mathsf{NP}$.
2. **$\mathsf P=\mathsf{NP}$ has no finite refutation and no finite confirmation.** A polynomial-time SAT
   algorithm with its correctness proof would confirm it; a proof of $\mathsf P\ne\mathsf{NP}$ must handle all
   algorithms at once. Any proof of $\mathsf P\ne\mathsf{NP}$ is therefore a statement about *every* program,
   hence must use a property that all polynomial-time programs share and that some NP verifier's
   witness-search violates. The only such property that has ever produced a separation from NP's
   neighborhood is the one in §5.6: a program's computation can be *compressed into a circuit and
   that circuit can be searched faster than brute force*.
