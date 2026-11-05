# 3. The frontier, as of 5 November 2026

**Provenance.** This section was compiled from six parallel literature surveys run during this
session (one per front), each of which tagged its claims by verification status, and
cross-checked against my own knowledge (training cutoff June 2026). The session's network
policy blocked direct fetches of arXiv, ECCC, ACM DL and the complexity blogs; surveys verified
citations through search-engine extracts of those pages and through GitHub, which was reachable.
Conventions: ★ marks results after June 2026; **[U]** marks items whose statement or venue could not
be verified online in this session and should be checked before being cited; everything else was
verified to the level of title, authors, venue and abstract. Numbers in parentheses after an item
are the sub-problems in `07-open-subproblems.md` it bears on.

## 3.0 Headline status

- **No proof of $\mathsf P=\mathsf{NP}$ or $\mathsf P\ne\mathsf{NP}$ is accepted** by the community. The Clay
  Mathematics Institute lists the problem as open. Fortnow (Computational Complexity blog, 10 June
  2026): "we don't even have a viable approach"; (4 Nov 2026 ★): AI now finds proofs, but P vs NP
  will need techniques it "won't come up with on its own". Aaronson (Shtetl-Optimized comment,
  26 Oct 2026 ★) raised his personal probability of $\mathsf P=\mathsf{NP}$ from 3% to 5%, which still reads
  as 95% for $\mathsf P\ne\mathsf{NP}$. Gasarch polls: 61% / 83% / 88% for $\mathsf P\ne\mathsf{NP}$ in 2002 / 2012 / 2019.
- **Claimed proofs continue to fail in the usual ways** (§3.10). Woeginger's list is frozen at 116
  entries (2016); Fortnow's "P v NP Papers Galore" (Apr 2025) documents the ongoing preprint flood.
- **The genuinely new event of 2026 is adjacent, not central** ★: on 26 Oct 2026 OpenAI
  (`github.com/openai/math`, family 378, "The Exponential Time Hypothesis is False") and Anthropic
  (`github.com/anthropics/formal-math/eth`, "A $2^{o(n)}$ Time Algorithm for 3-SAT", author "Claude")
  released AI-generated manuscripts with Lean 4 developments claiming deterministic $\#k$-SAT in
  time $2^{O(n\log\log n/\sqrt{\log n})}$, which would refute ETH and SETH and (via Williams 2013)
  give superlinear $\mathsf E^{\mathsf{NP}}$ circuit lower bounds. I verified that the Anthropic repository
  exists and makes this claim. Status: under examination by a working group (Impagliazzo, Paturi,
  Williams); no flaw announced; no human had audited statement fidelity of the Lean files at
  release. The authors themselves state it has **no bearing on P vs NP**: a $2^{o(n)}$ algorithm does
  not survive polynomial-time reductions, and the bound beats $2^n$ only for astronomically large $n$.
  This dossier treats it as a *machine-checked claim under review*, not a theorem.

## 3.1 Boolean circuit lower bounds

| Model | Best explicit bound | Reference | Status |
|---|---|---|---|
| General circuits ($B_2$) | $3.5n-o(n)$ ★ **[preprint]**; previously $3.1n-o(n)$ | Mishra–Santhanam, ECCC TR26-260 (Oct 2026); Li–Yang STOC 2022 | gate elimination by "reparameterisation"; whether it escapes the Golovnev–Hirsch–Knop–Kulikov limits is open (4) |
| $U_2$ circuits | $5n-o(n)$ | Iwama–Morizumi 2002 | unchanged **[U]** |
| De Morgan formulas | $n^{3-o(1)}$ | Håstad 1998; Tal 2014 | cubic barrier unchanged since 2014; KRW conjecture is the bottleneck (4) |
| $B_2$ formulas | $\Omega(n^2/\log n)$ | Nechiporuk 1966 | unchanged |
| Depth-3 $\mathsf{AC}^0$ | $2^{\Omega(\sqrt n)}$ (parity) | Håstad 1986 | no $2^{\omega(\sqrt n)}$ for any explicit function; Valiant's $2^{\omega(n/\log\log n)}$ threshold for log-depth consequences untouched (5) |
| $\mathsf{AC}^0$ depth $d$ | $2^{\Omega(n^{1/(d-1)})}$ | Håstad 1986 | ★ Loff–Sherif–Talebanfard–Ugazio (arXiv 2606.12631): *unconditional* barrier, switching-lemma / $\mathsf{AC}^0$-natural proofs cannot improve the exponent significantly |
| $\mathsf{ACC}^0$, $\mathsf{ACC}^0\circ\mathsf{THR}$ | superpolynomial for $\mathsf{NQP}$ | Williams 2011/2014; Murray–Williams STOC 2018; Chen FOCS 2019; Chen–Ren STOC 2020; Chen–Lyu–Williams FOCS 2020 | $\mathsf{NP}\not\subseteq\mathsf{ACC}^0$ and $\mathsf E^{\mathsf{NP}}\not\subseteq\mathsf{ACC}^0$ open (2) |
| $\mathsf{TC}^0$ | nothing superpolynomial, even depth 2, even for $\mathsf{NEXP}$ | — | depth-2 threshold: $\tilde\Omega(n^{1.5})$ gates for a P function (Kane–Williams STOC 2016); ★ $n^{2.5-\varepsilon}$ gates for a function in $\mathsf E^{\mathsf{NP}}$ (Chen–Tal–Wang STOC 2026) via a CAPP algorithm for XORs of two circuits + the algorithmic method |
| Monotone circuits | $2^{n^{1/2-o(1)}}$ | Cavalar–Kumar–Rossman 2020 (robust sunflowers) | monotone formulas/span programs $2^{\Omega(n)}$ (Pitassi–Robere STOC 2017) |
| Near-maximum $2^n/n$ for uniform classes | $\Sigma_2\mathsf E$, $\mathsf S_2\mathsf E$ (a.e.), $\mathsf{ZPE}^{\mathsf{NP}}$ | Chen–Hirahara–Ren STOC 2024; Li STOC 2024 | ★ $\mathsf E^{\mathsf{prMA}}/1$ (Ren–Williams FOCS 2026, uses the PCP theorem); $\mathsf{AMEXP}$ with subexponential advice (Chen–Li–Liang STOC 2025); $\mathsf{BPE}^{\mathrm{MCSP}}$ (Hirahara–Lu–Ren CCC 2023); fixed-polynomial for $\mathsf O_2\mathsf P$ (Gajulapalli–Li–Volkovich 2024). **$\mathsf E^{\mathsf{NP}}$ remains open and is equivalent to Avoid $\in\mathsf{FP}^{\mathsf{NP}}$** (1) |

## 3.2 Range Avoidance and the explicit-construction frontier

Avoid: given $C:\{0,1\}^n\to\{0,1\}^m$, $m>n$, output a string outside the range. Korten (FOCS 2021):
Avoid $\in\mathsf{FP}^{\mathsf{NP}}$ on all lengths $\iff$ $\mathsf E^{\mathsf{NP}}$ requires circuits of size $2^n/(2n)$
almost everywhere; Avoid $\in\mathsf{FP}$ would give maximally hard functions in $\mathsf E$ and hence
$\mathsf{prBPP}=\mathsf{prP}$. State of the art:

- **Upper bounds.** Single-valued $\mathsf{FS}_2\mathsf P$ algorithm on all input lengths (Li STOC 2024;
  Chen–Hirahara–Ren STOC 2024 for infinitely many lengths), hence pseudodeterministic
  $\mathsf{FZPP}^{\mathsf{NP}}$ constructions of Ramsey graphs, rigid matrices, hard truth tables, two-source
  extractors. Korten–Pitassi (FOCS 2024): Li's algorithm is a reduction to the Linear Ordering
  Principle, and the technique provably cannot solve *strong* Avoid (stretch $n+1$).
  Hirsch–Volkovich (STACS 2026): $\mathsf P^{\mathsf{prMA}}\subseteq\mathsf L_2\mathsf P\subseteq\mathsf P^{\mathsf{prSBP}}$.
- **Hardness evidence.** Ilango–Li–Williams (STOC 2023): under subexponentially secure iO,
  Avoid $\in\mathsf{FP}$ implies $\mathsf{NP}=\mathsf{coNP}$; also $\mathrm{PV}_1\ne\mathrm{APC}_1$ under these assumptions.
  Chen–Li (STOC 2024): under LWE/LPN-type assumptions Avoid $\notin\mathsf{SearchNP}$. Ren–Wang–Zhong
  (ITCS 2026): demi-bits generators suffice for nondeterministic hardness. ★ Korten, ECCC TR26-302
  (5 Nov 2026): tight depth lower bounds for black-box stretch amplification; relativized $\mathrm S^1_2$
  cannot pass from $\mathsf{NC}$-hardness to $\mathsf{P/poly}$-hardness.
- **Not NP-hard unless PH collapses.** ★ Ghentiyala–Li–Stephens-Davidowitz (STOC 2026):
  $\mathsf{prBPP}^{\mathrm{Avoid}}\subseteq\mathsf{AM}\cap\mathsf{coAM}$, via an AM protocol for *upper*-bounding image size
  (a dual Goldwasser–Sipser). Avoid therefore sits in the factoring/graph-isomorphism zone.
- **Derandomization link.** ★ Li, ECCC TR26-270 (Oct 2026): a fragment of $\mathsf{prAM}$ containing all of
  $\mathsf{prMA}$ (the Structured Set Lower Bound fragment) derandomizes via targeted hitting sets exactly
  when Avoid does; progress on Avoid now feeds AM derandomization.
- **Average-case analogue.** Huang–Li–Zhong (ITCS 2026): $\mathsf{FP}^{\mathsf{NP}}$ for Remote Point $\iff$
  average-case circuit lower bounds for $\mathsf E^{\mathsf{NP}}$; new $\mathsf{NC}^0$-Avoid algorithms.

**Reading.** The field has converted "prove a circuit lower bound for an exponential class with one
NP oracle" into "deterministically name a non-image of a stretching circuit", and has shown that
this naming problem is neither easy (under crypto) nor NP-hard (unless PH collapses). It is the
most active unconditional front, and its descent to NP is the same missing bridge as everywhere
else (§6.9 of `06-attempts.md`).

## 3.3 The algorithmic method

Base theorem: a $2^n/n^{\omega(1)}$-time satisfiability (or CAPP) algorithm for polynomial-size
$\mathcal C$-circuits implies $\mathsf{NEXP}\not\subseteq\mathcal C$ (Williams 2010/2013); the easy-witness lemma
for $\mathsf{NQP}$ and a fixed-polynomial one for $\mathsf{NP}$ (Murray–Williams STOC 2018) give
$\mathsf{NQP}\not\subseteq\mathsf{ACC}^0\circ\mathsf{THR}$; Chen–Williams (CCC 2019) weaken the hypothesis to Gap-UNSAT/CAPP
through PCPs of proximity; Chen–Lyu–Williams (FOCS 2020) give almost-everywhere versions; Williams
(2013/2016) shows constructivity is unavoidable, so the method is in a weak sense "natural" and
necessary. ★ Chen–Tal–Wang (STOC 2026) is the $\mathsf E^{\mathsf{NP}}$ variant (CAPP for XOR of two circuits).
**Unmoved:** $\mathsf{ACC}^0\to\mathsf{TC}^0$ needs a non-trivial SAT/CAPP algorithm for depth-2 threshold
circuits with superquadratic wires (the SYM∘AND depth-reduction template has no analogue for
arbitrary-weight thresholds); $\mathsf{NQP}\to\mathsf{NP}$ needs either polynomial savings on $O(\log n)$-input
circuits (impossible as stated) or an easy-witness lemma with polylogarithmic overhead (§5.6) (2).

## 3.4 Hardness magnification and the locality barrier

Sharpest statements: Oliveira–Santhanam (FOCS 2018): if $\mathrm{MCSP}[2^{\sqrt n}]$ has no zero-error
average-case *linear-size formulas*, then NP has no polynomial-size formulas. McKay–Murray–Williams
(STOC 2019): $N^{1+\varepsilon}$ circuit or streaming lower bounds for search-MCSP / MKtP imply
$\mathsf{NP}\not\subseteq\mathsf{P/poly}$ / $\mathsf P\ne\mathsf{NP}$. Chen–Jin–Williams (FOCS 2019): for *every*
$2^{n^{o(1)}}$-sparse NP language $L$, $L\notin\mathrm{Circuit}[n^{1+\varepsilon}]$ implies $\mathsf{NP}\not\subseteq\mathrm{SIZE}[n^k]$
for all $k$. Chen–Jin–Williams (STOC 2020): a sharp threshold at formula exponent 2 for
$\mathrm{MCSP}[(\log n)^c]$: $n^{2-o(1)}$ is proved, $n^{2+\varepsilon}$ would give $\mathsf{NP}\not\subseteq\mathrm{Formula}[n^k]$
for all $k$. Oliveira–Pich–Santhanam (CCC 2019): Gap-MKtP / Gap-MCSP versions near current bounds.

Locality barrier (Chen–Hirahara–Oliveira–Pich–Rajgopal–Santhanam, ITCS 2020 / JACM 2022): every
magnification theorem's target has small circuits once oracle gates of fan-in $n^{o(1)}$ are
allowed, and every current technique for the weak models (restrictions, shrinkage, Nechiporuk,
gate elimination, communication games) is insensitive to such gates. The magnification hypotheses
are *not* naturalizable (they would themselves imply no natural proofs exist), so locality, not
natural proofs, is the live obstruction. No non-local technique exists (3).

## 3.5 Meta-complexity

- **MCSP is not known NP-hard unconditionally under any reduction notion.** Sharpest: Hirahara–Ilango
  (FOCS 2025): NP-hard under deterministic quasi-polynomial non-adaptive reductions assuming
  subexponentially secure NIWI for SAT, coNP hard for subexponential nondeterministic circuits, and
  $\mathsf P^{\mathsf{NP}}/\mathrm{poly}$ requiring circuits of size $\Omega(2^n/n)$ — hypotheses that already imply
  circuit lower bounds, so no new unconditional separation results. Ilango (FOCS 2023): SAT reduces to
  Gap-MCSP relative to a random oracle. Unconditional NP-hardness holds for partial MCSP and
  learning programs (Hirahara FOCS 2022, randomized reductions), for conditional $K^t$
  ($\mathrm{McK}^t\mathrm P$, Liu–Pass CCC 2022), and ★ for nondeterministic $K^t$ (MINnKT: Hu–Lu–Oliveira CCC
  2026, whose hardness *characterizes* $\mathsf{NP}\not\subseteq\mathsf{BPP}$). Non-hardness: not under local
  reductions (Murray–Williams 2017); Gap-MCSP not Levin-NP-complete in Obfustopia (Mazor–Pass CCC 2024).
- **Consequences of easiness.** MCSP $\in\mathsf P$ ⟹ no PRFs (Kabanets–Cai 2000), SZK, factoring,
  discrete log easy, $\mathsf{P/poly}$ learnable (CIKK 2016); Gap-MINKT $\in\mathsf P$ ⟸ DistNP $\subseteq$ AvgP
  (Hirahara FOCS 2018, the first non-black-box worst-to-average reduction within NP).
- **One-way functions are now characterized many ways**: $K^t$ mildly hard on average (Liu–Pass FOCS
  2020); MCSP hard on average on *some* samplable distribution (Ilango–Ren–Santhanam STOC 2022);
  failure of average-case symmetry of information (Hirahara–Ilango–Lu–Nanashima–Oliveira STOC 2023);
  NP worst-case hard **and** DistK$^t$ NP-hard under randomized reductions (Hirahara STOC 2023);
  NP $\subseteq$ CZK and NP hard (Hirahara–Nanashima STOC 2024); boundary hardness of $K^{\mathrm{poly}}$
  under derandomization (Liu–Pass CRYPTO 2025, ITCS 2026).
- **Pessiland has a sharp characterization** (★ Hirahara–Nanashima STOC 2026): NP is hard on average
  iff minimum description length in agnostic learning is hard to approximate within $\ell/\mathrm{polylog}(\ell)$;
  OWFs do not exist iff it is easy within $O(\ell)$. Excluding Pessiland = closing a polylog gap.
- **A Kolmogorov route to P vs NP** (★ Kabanets–Kolokolova STOC 2026): assuming Gap-McK$^t$P is
  NP-hard (true under witness encryption), the chain rule for conditional $K^t$ with $o(N)$ error
  holds iff $\mathsf P=\mathsf{NP}$.
- **Perebor is false non-uniformly**: MK$^t$P has circuits of size $2^{4n/5+o(n)}$ (Mazor–Pass ITCS
  2024; Hirahara–Ilango–Williams STOC 2024).
- Survey: ★ Goldberg–Nanashima–Oliveira, "Learning, Compression, and Meta-Complexity" (Oct 2026).

## 3.6 Proof complexity and bounded arithmetic

- **Lower bounds.** Resolution, Res($k$), PC/PCR, Cutting Planes (random $\Theta(\log n)$-CNFs:
  Hrubeš–Pudlák / Fleming–Pankratov–Pitassi–Robere 2017, Sokolov 2023; bit-PHP $2^{\Omega(n^{1/4})}$:
  Beame–Whitmeyer ICALP 2025), SoS degree, bounded-depth Frege: all closed. **Open:**
  $\mathsf{AC}^0[p]$-Frege ("open for almost three decades"), Frege, Extended Frege. Progress is one
  level down: Res($\oplus$) regular / bounded-depth / near-quadratic-depth exponential bounds
  (STOC 2024, STOC 2025, STOC 2026, CCC 2026); dag-like Res($\oplus$) open as of Apr 2026, with a ★
  Sept 2026 preprint (arXiv 2609.23015) claiming an exponential bit-PHP bound **[U]**. Sideways:
  constant-depth IPS lower bounds over $\mathbb F_p$ for CNFs would give $\mathsf{AC}^0[p]$-Frege bounds
  (Elbaz–Govindasamy–Lu–Tzameret 2025); ★ Hakoniemi–Limaye–Tzameret (FOCS 2026) give hard CNFs for
  ROABP-IPS; ★ Garlík–Gryaznov–Ren–Tzameret (STOC 2026) tie the weak rank principle to $\mathsf{NC}^2$ and
  $\mathsf{AC}^0[p]$ lower bounds (3).
- **Automatability.** Resolution not automatable unless $\mathsf P=\mathsf{NP}$ (Atserias–Müller 2019/2020);
  likewise regular Resolution, Res($k$), Cutting Planes (Göös–Koroth–Mertz–Pitassi 2020), NS/PC
  (de Rezende–Göös–Nordström–Pitassi–Robere–Sokolov 2021), bounded-depth Frege (Papamakarios **[U]**);
  Frege/EF under factoring/RSA; SoS open. Automatability of Resolution is thus a *second
  equivalent formulation* of P vs NP.
- **Unprovability.** Pich–Santhanam (STOC 2021): PV does not prove average-case
  co-nondeterministic lower bounds for NP of size $2^{n^{o(1)}}$ (unconditional). Li–Oliveira (STOC
  2023): $\mathrm{APC}_1$ does not prove strong PH-level separations. Chen–Li–Oliveira (FOCS 2024):
  reverse mathematics over $\mathrm{PV}_1$, equivalences between lower bounds and combinatorial
  principles. Chen–Li–Oliveira (LMCS 2025): fixed-polynomial coNSIZE bounds for SAT are
  *independent* of intuitionistic $\mathrm{IS}^1_2$. Pich–Santhanam (2023): EF lower bounds for
  circuit-lower-bound formulas are essentially $\mathsf P\ne\mathsf{NP}$-hard under provability conditions.
  ★ Lu–Santhanam–Tzameret (ITCS 2026): $\mathsf{AC}^0[p]$-Frege cannot prove that constant-depth IPS
  cannot prove permanent lower bounds. Consistency: Atserias–Buss–Müller (STOC 2023): $\mathrm V^0_2$ is
  consistent with $\mathsf{NEXP}\not\subseteq\mathsf{P/poly}$.
- **Generators.** Krajíček, *Proof Complexity Generators* (CUP 2025); Razborov's NW-generator
  conjecture proven only up to $\mathsf{AC}^0$-Frege (Khaniki CCC 2022); demi-bits $\Rightarrow$ generators
  $\Rightarrow$ Avoid hardness (Ren–Wang–Zhong ITCS 2026; ★ Li–Ren–Zhong FOCS 2026). A generator hard
  for *all* systems would give $\mathsf{NP}\ne\mathsf{coNP}$; Krajíček conjectures his gadget generator is one.
- **Independence.** No credible result (2015–2026) on independence of P vs NP from ZFC or PA;
  Ben-David–Halevi (1992) remains the one substantive theorem (independence from
  $\mathrm{PA}+\Pi_1$-truths ⟹ $\mathsf{NP}\subseteq\mathrm{DTIME}(n^{\alpha(n)})$ with $\alpha$ ultra-slow). Since
  $\mathsf P=\mathsf{NP}$ is arithmetical, forcing cannot show ZFC-independence (Shoenfield absoluteness).

## 3.7 Derandomization and time–space

- **Equivalences.** $\mathsf{prBPP}=\mathsf{prP}$ is near-equivalent to almost-all-inputs hardness of a
  multi-output function in P against probabilistic $n^c$-time algorithms (Chen–Tell FOCS 2021), to
  hardness of conditional Levin complexity (Liu–Pass CCC 2022), to leakage-resilient hardness
  (Liu–Pass CCC 2023), to deterministic refuters against low-space streaming algorithms
  (Chen–Tell–Williams FOCS 2023), with AM analogues (van Melkebeek–Sdroievski, journal 2025).
  Free-lunch derandomization from necessary assumptions: Ball–Chen–Tell (CCC 2025).
- **The ceiling (Tell 2019).** $\mathsf P=\mathsf{NP}\Rightarrow\mathsf{PH}=\mathsf P\Rightarrow\mathsf{prBPP}=\mathsf{prP}$ and
  $\mathsf{NP}\subseteq\mathsf{P/poly}$, so any theorem "derandomization ⟹ $\mathsf P\ne\mathsf{NP}$" would already prove
  $\mathsf P\ne\mathsf{NP}$ unconditionally. Derandomization can conditionally deliver at most
  $\mathsf{NEXP}\not\subseteq\mathsf{P/poly}$ (IKW 2002) and "almost-NP" $\not\subseteq\mathsf{P/poly}$ (Tell).
- **Williams 2025.** $\mathrm{TIME}[t]\subseteq\mathrm{SPACE}[O(\sqrt{t\log t})]$ for multitape TMs (STOC 2025 best
  paper; JACM June 2026), via Cook–Mertz tree evaluation; corollaries $\mathrm{SPACE}[s]\not\subseteq\mathrm{TIME}[s^{2-\varepsilon}]$.
  ★ Lean formalization reported complete (complexitylib, 1 Nov 2026). No accepted improvement (a
  preprint claiming $O(\sqrt t)$ is reported flawed); no RAM or NTIME analogue; $\mathrm{TIME}[t]\subseteq\mathrm{SPACE}[t^{\varepsilon}]$
  for all $\varepsilon$ would give $\mathsf P\ne\mathsf{PSPACE}$. First application-style use: Wehar (Nov 2025),
  unconditional $\tilde\Omega(n^2)$ time for DFA intersection non-emptiness.
- **SAT time–space.** Unchanged: $\mathrm{SAT}\notin\mathrm{TIME}[n^c]\cap\mathrm{SPACE}[n^{o(1)}]$ for $c<2\cos(\pi/7)$
  (Williams 2008); Buss–Williams (2012/2015): optimal for alternation-trading proofs.
- **Pseudodeterminism.** Polynomial-time pseudodeterministic primes infinitely often
  (Chen–Lu–Oliveira–Ren–Santhanam FOCS 2023 / JACM); removing "infinitely often" is open;
  TFZPP studied systematically (Fleming et al. ITCS 2026).

## 3.8 Algebraic complexity and GCT

- **Lower bounds.** General algebraic circuits: $\Omega(n\log d)$ (Baur–Strassen 1983), unchanged for
  forty years; general formulas and ABPs: $\Omega(n^2)$ (Chatterjee–Kumar–She–Volk 2022; Kumar 2019 for
  homogeneous ABPs). Constant depth: superpolynomial for $\mathrm{IMM}_{n,d}$, $d=O(\log n/\log\log n)$
  (Limaye–Srinivasan–Tavenas FOCS 2021, best paper), exponent improved to $n^{\Omega(d^{1/\varphi^{2\Delta}})}$
  with a proof that the LST measure can go no further (Bhargav–Dutta–Saxena MFCS 2022 / ToCT 2024), and
  extended to every field (Forbes CCC 2024, best paper). Set-multilinear formulas: tight constant-depth
  bounds for a VNP polynomial (Kush–Saraf CCC 2022/2023); $n^{\Omega(\log n)}$ for IMM in unbounded depth
  still open. Determinantal complexity of $\mathrm{perm}_n$: $\ge n^2/2$ (Mignon–Ressayre 2004), $\ge(n-1)^2+1$
  over $\mathbb R$ (Yabe 2015), border $\ge n^2/2$ (Landsberg–Manivel–Ressayre 2013); upper bound $2^n-1$
  (Grenet). *No explicit polynomial has determinantal complexity superlinear in $\max\{n,d\}$*
  (record $1.5n-3$, Kumar–Volk 2022). ★ FOCS 2026: Forbes (exponential depth-3 in small
  characteristic), Raz (non-commutative circuits), Narayanan (sumset-expansion bounds, explicitly
  short of superpolynomial).
- **GCT.** Occurrence obstructions cannot separate padded permanent from determinant
  (Bürgisser–Ikenmeyer–Panova FOCS 2016 / JAMS 2019); Kronecker positivity is NP-hard
  (Ikenmeyer–Mulmuley–Walter 2017). Multiplicity obstructions remain possible and now work at toy
  scale: product-plus-power (Dutta–Gesmundo–Ikenmeyer–Jindal–Lysikov, rev. May 2025) and ★ graph
  isomorphism (Grochow–Urisman, ECCC TR26-106, June 2026), where multiplicities provably beat
  occurrences. Consensus statement: Bläser–Ikenmeyer, *Introduction to GCT* (ToC Graduate Surveys,
  May 2025): occurrence obstructions "essentially cannot" work, multiplicity obstructions "may still be
  the route". No concrete computable route to permanent vs determinant is claimed by anyone.
- **Bridge theorems (Bürgisser, TCS 2000).** Over $\mathbb F_q$, unconditionally: $\mathsf{VP}=\mathsf{VNP}$ ⟹
  $\mathsf{NC}^2/\mathrm{poly}=\mathsf{P/poly}=\mathsf{NP/poly}=\mathsf{PH/poly}$, hence $\mathsf{PH}=\Sigma_2^p$. Over $\mathbb C$ under
  GRH: $\mathsf{VP}=\mathsf{VNP}$ ⟹ $\#\mathsf P/\mathrm{poly}\subseteq\mathsf{NC}^3/\mathrm{poly}$ and $\mathsf{PH}=\Sigma_2^p$. Usable
  direction: $\mathsf{NP}\not\subseteq\mathsf{P/poly}$ ⟹ $\mathsf{VP}\ne\mathsf{VNP}$ over every finite field (and over
  $\mathbb C$ under GRH). *$\mathsf P\ne\mathsf{NP}$ alone is not known to imply $\mathsf{VP}\ne\mathsf{VNP}$* (Valiant's classes
  are non-uniform), and $\mathsf{VP}\ne\mathsf{VNP}$ has no known Boolean separation consequence; the only
  reverse transfers are derandomizations (Kabanets–Impagliazzo 2004; Carmosino–Impagliazzo–Kabanets–Kolokolova
  CCC 2015 uniform equivalences).
- **PIT.** Deterministic $(sn)^{O(n^\varepsilon)}$-time PIT for constant depth over any field (LST + Chou–Kumar–Solomon;
  Andrews–Forbes STOC 2022; Forbes 2024); no quasi-polynomial PIT for depth 3 or 4. Lower bounds and
  PIT for low depth now move in lockstep via the KI/CKS translation.
- **Algebraic natural proofs barrier** (Forbes–Shpilka–Volk 2017; Grochow–Kumar–Saks–Saraf 2017):
  VP-succinct hitting sets for a class rule out VP-natural proofs against it. Counter-evidence
  (Chatterjee–Kumar–Ramya–Saptharishi–Tengse FOCS 2020; Kumar–Ramya–Saptharishi–Tengse STACS 2022):
  efficient equations for VP *do* exist over finite fields and for bounded integer coefficients, so
  the barrier over $\mathbb C$ is really about huge constants. LST is itself an algebraically natural
  proof (rank of a partial-derivative matrix), consistent with the barrier, which predicts such
  techniques stop at some unknown depth/structure threshold.
- **Reading.** $\mathsf{VP}\ne\mathsf{VNP}$ is "P vs NP without the Boolean" and may fall first; its link to
  $\mathsf P\ne\mathsf{NP}$ is conditional (non-uniform hypotheses, GRH over $\mathbb C$) and one-directional.

## 3.9 Formalization and AI

- **Formal complexity theory.** Cook–Levin in Isabelle (Balbach, AFP 2023) and Coq (Gäher–Kunze, ITP
  2021). Lean 4: Mathlib has Turing machines but no complexity classes; **complexitylib**
  (cslib-community) claims Cook–Levin, time hierarchy, Savitch, Barrington, PCP, Williams 2025 and
  more, AI-assisted and with "coverage and source audits incomplete"; ★ descriptive complexity in
  Lean (Senellart–Gnatenko, Sept 2026, 212k lines, 73 completeness results, mostly written with
  Claude); ★ Håstad's switching lemma and Razborov–Smolensky in Lean (Wesonga, Sept 2026).
  Problem statements: `LeanMillenniumPrizeProblems` (a Sept 2026 fix repaired a certificate-encoding
  bug under which every language was in NP — a cautionary example), DeepMind `formal-conjectures`.
- **AI results.** AlphaEvolve gadgets for MAX-4-CUT inapproximability (Nagda–Raghavan–Thakurta 2025)
  and Ramsey bounds (2026): real but incremental. ★ The October 2026 ETH claims (§3.0). OpenAI's
  corpus also contains *unreviewed* Lean-accompanied claims of the Unique Games Conjecture and a
  $2^{\omega(\sqrt n)}$ depth-3 lower bound; none community-verified; nothing claims P vs NP.
- **Failed AI-era claims.** Arthanari (June 2026): "Lean-verified $\mathsf P=\mathsf{NP}$" whose main theorem
  proved `True` and then an axiom. The lesson for this dossier: a kernel-checked proof is only as
  good as its *statement*, and no one has yet audited statement fidelity for the large AI corpora.

## 3.10 Claimed proofs, 2017–2026, and why they failed

| Claim | Direction | Failure |
|---|---|---|
| Blum 2017 (arXiv 1708.03486) | $\ne$ | Theorem 6 (transfer of Berg–Ulfberg approximators to circuits with negations) applies verbatim to Tardos' function, a monotone function in P with exponential monotone complexity, yielding a false bound; withdrawn |
| Xu–Zhou 2023 ("SAT requires exhaustive search"; *FCS* 2025) | $\ne$ | relies on an unwarranted assumption about every SAT algorithm (Chavrimootoo et al. 2023; Allender–Williams, *FCS* 2026) |
| Deng 2025 ($\mathsf P=\mathsf{NP}$ via SDP for 3-coloring) | $=$ | Lemma 3 conflates subgraphs with induced subgraphs; dual SDP unjustified (Humphreys et al. 2025) |
| Arthanari 2026 (Lean, pedigree polytopes) | $=$ | main theorem was `True`, then an axiom; polytope type `Unit` |
| assorted 2025–26 arXiv "homological", "observer-theoretic", Lean "0 sorries, 2 axioms" | both | undefined P/NP or declared axioms; no endorsement |

The failures share a template: a correct restricted-model argument (monotone, specific algorithm
family) silently extended to the general model, where a known counterexample (Tardos' function; a
non-exhaustive algorithm) refutes the extension. `02-barriers.md` is the checklist that catches
each of them.
