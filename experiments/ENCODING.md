# The SAT encoding behind the exact circuit costs, and why its lower bounds are sound

`circuit_sat.py` decides "is there a chain of exactly k gates computing f?" with a CNF that
contains, besides the gate semantics, several symmetry-breaking rules. An UNSAT answer is used as a
**lower bound**, so every rule must keep at least one minimum chain. This file states the model,
lists the clauses, and proves that (Theorem 1). It also says what the label **Machine-checked**
means for the numbers in `results/`.

## 1. Model

A *chain* over inputs $x_1,\dots,x_n$ is a sequence of gates $g_{n+1},\dots,g_{n+k}$; gate $g_i$
applies a binary operator $\circ_i$ to two earlier nodes (inputs or gates). In the basis $B_2$ every
one of the 16 binary operators is allowed; in $U_2$ all except $\oplus$ and $\equiv$. The chain
computes $f$ if some gate (w.l.o.g. the last) computes $f$. The cost $C_B(f)$ is the least $k$ such
that a $k$-gate chain over $B$ computes $f$ or $\neg f$; constants and literals have cost 0. This is
Knuth's convention (TAOCP 4A §7.1.2) and the one used in `docs/05-worked-mathematics.md`.

Truth tables are indexed by rows $t=0,\dots,2^n-1$ with $x_a$ = bit $a$ of $t$ (0-based in code).
A function is *normal* if its value on row 0 is 0; an operator $\circ$ is normal if $0\circ 0=0$.

**Lemma 1 (normal chains; Knuth).** If a $k$-gate chain over $B$ computes $f$ or $\neg f$, then a
$k$-gate chain over $B$ with only normal operators computes the normal member of $\{f,\neg f\}$.

*Proof.* Walk through the gates in order. If gate $g$ currently computes a non-normal function,
replace $\circ_g$ by $\neg\circ_g$ and, in every gate that reads $g$, replace the operator $\circ$ by
the operator with that argument negated. Both bases are closed under negating an argument or the
result, so the chain stays in $B$; every gate now computes a normal function, and the output computes
$f$ or $\neg f$, whichever is normal. A gate computing a normal function from normal arguments has a
normal operator. $\square$

The five normal operators that depend on both arguments are $a\wedge b$, $a\wedge\bar b$,
$\bar a\wedge b$, $a\oplus b$, $a\vee b$; $U_2$ has the four without $\oplus$. The other three
normal operators are the constant 0 and the two projections.

## 2. The CNF $\Phi_B(f,k)$

Fix a normal $f$ that depends on all $n\ge 2$ inputs (the code first restricts $f$ to its essential
variables; that does not change the cost). Nodes $0..n-1$ are inputs, $n..n+k-1$ gates, and gate
$n+k-1$ is the output. All pairs $(j,l)$ with $j<l$ are listed in colex order (by $l$, then $j$);
the index of $(j,l)$ is $l(l-1)/2+j$, the same for every gate that can read it.

Variables: $s_{i,q}$ (gate $i$ reads pair $q$), $o_{i,q}$ (order encoding: pair index of gate
$i$ is $\ge q$), $f_i=(f_i^{01},f_i^{10},f_i^{11})$ (operator bits $\circ_i(0,1),\circ_i(1,0),\circ_i(1,1)$;
$\circ_i(0,0)=0$), $v_{i,t}$ (value of gate $i$ on row $t\ge 1$; row 0 is 0), plus auxiliaries.
The *opcode* of a gate is the 3-bit number $f^{01}f^{10}f^{11}$ (most significant first).

Base clauses (always present):
- exactly one pair per gate (order encoding, and the plain at-least-one clause);
- semantics: $s_{i,(j,l)}\wedge[\text{node } j=a \text{ on row } t]\wedge[\text{node } l=b]\Rightarrow (v_{i,t}\Leftrightarrow \circ_i(a,b))$;
- output: $v_{n+k-1,t}=f(t)$ for every row $t$;
- every operator is one of the normal operators that depend on both arguments, and in $U_2$ not $\oplus$.

Symmetry-breaking rules (letters as in the code):
- **A** every gate except the output is read by a later gate; every input is read by some gate.
- **D** the functions computed by the gates are pairwise distinct, nonzero, different from every
  input $x_a$, and (except at the output) different from $f$.
- **R** no re-application: if gate $i$ reads $(j,l)$, no later gate reads $(j,i)$ or $(l,i)$.
- **L** lex-min numbering: for gates $i<m$, if both inputs of $m$ are nodes $<i$, then
  $(\text{pair index}_i,\text{opcode}_i) < (\text{pair index}_m,\text{opcode}_m)$ lexicographically.
- **V** for every $a$ such that $f$ is invariant under exchanging $x_a$ and $x_{a+1}$: the first gate
  that reads $x_{a+1}$ is not earlier than the first gate that reads $x_a$.

## 3. Soundness

**Theorem 1.** Let $f$ be normal and depend on all $n\ge2$ inputs, let $B\in\{B_2,U_2\}$ and
$k=C_B(f)$. Then $\Phi_B(f,k)$ with all rules A, D, R, L, V is satisfiable.

**Corollary.** If $\Phi_B(f,k')$ is unsatisfiable for every $k'=1,\dots,K-1$, then $C_B(f)\ge K$.
(Indeed $C_B(f)\ge1$ because $f$ is not a constant or a literal, and $\Phi_B(f,C_B(f))$ is satisfiable.)

The proof is a sequence of normalisations of a minimum chain. Call a chain *minimum* if it has
$C_B(f)$ gates, uses only normal operators, and its last gate computes $f$ (Lemma 1 gives one).

**Lemma 2.** In every minimum chain: (a) no gate computes $0$, an input, or the same function as an
earlier gate; in particular every operator depends on both arguments; (b) no gate other than the
last computes $f$; (c) every gate other than the last is read by a later gate; (d) every input is
read; (e) the last gate is the only gate that no gate reads, so it is last in every topological order.

*Proof.* (b) If gate $g$ before the last computes $f$, drop every gate after $g$: fewer gates.
(c) An unread non-last gate can be deleted. (d) An unread input cannot influence the output, but
$f$ depends on it. (e) follows from (c): from any gate, following readers forward ends at a gate
with no reader, which by (c) is the last gate. (a) Suppose some gate violates (a) and let $g$ be the
**last** such gate. If $g$ computes 0, then $g$ is not the last gate ($f\ne0$), so by (c) some gate
$h$ reads $g$ and another node $c$; since $\circ_h$ is normal, $h$ computes $\circ_h(0,c)\in\{0,c\}$, so
$h$ violates (a) and comes after $g$ — contradiction. So $g$ computes the same function as an earlier
node $w$ (an input or a gate). Redirect every read of $g$ to $w$ and delete $g$; all other gates
compute what they computed before. If $g$ was the last gate, $w$ computes $f$, so $w$ is a gate
($f$ is not a literal) and we drop everything after $w$. Either way we get fewer gates. A gate whose
operator ignores an argument computes 0 or the function of one of its inputs, so it is covered. $\square$

**Lemma 3.** There is a minimum chain with no re-application (rule R).

*Proof.* Suppose gate $h$ reads $(g,a)$ and $g$ reads $(a,b)$ (in some order). Replace $h$ by a gate
$h'$ that reads $(a,b)$ and has operator $\circ'(a,b)=\circ_h(g(a,b),a)$ (arguments reordered as
needed). $h'$ computes the same function as $h$, so the chain still computes $f$ with the same
number of gates, all other gates are unchanged, and $\circ'$ is normal because
$\circ_h(\circ_g(0,0),0)=\circ_h(0,0)=0$. In $U_2$: by Lemma 2(a) $\circ_h$ depends on both arguments,
so it has the form $((y\oplus\alpha)\wedge(a\oplus\beta))\oplus\gamma$; then $\circ'(\beta,b)=\gamma$ for
both values of $b$, whereas $\oplus$ and $\equiv$ restricted to $a=\beta$ are not constant. So
$\circ'\in U_2$. The new chain is again minimum, so Lemma 2 applies to it. Each step replaces the
input $g$ of $h$ by $b$, which comes before $g$ in a fixed topological order; so the sum over gates
of the positions of their inputs strictly decreases and the process stops. $\square$

**Lemma 4 (canonical labelling).** Let $\mathcal G$ be the group generated by the transpositions
$(x_a\,x_{a+1})$ under which $f$ is invariant. Take a minimum chain without re-application. Among all
ways to (i) rename the inputs by some $\sigma\in\mathcal G$ and (ii) number the gates in a topological
order, pick one whose sequence
$S=(e_n,e_{n+1},\dots,e_{n+k-1})$, $e_p=(\text{pair index of gate } p,\ \text{opcode of gate } p)$,
is lexicographically smallest. (After renaming, a gate reading two inputs lists them in increasing
order, transposing its operator if necessary.) Then rules L and V hold.

*Proof.* Renaming by $\sigma\in\mathcal G$ gives a chain for $f\circ\sigma=f$; renaming and renumbering
change none of the properties in Lemmas 2 and 3, and they preserve normality.

L: let $p<m$ and suppose gate $m$ reads only nodes $<p$. Move gate $m$ to position $p$ and shift
gates $p,\dots,m-1$ up by one. This is still a topological order: the moved gate reads only nodes
$<p$, and the shifted gates were before $m$, so none reads it. Entries $e_{p'}$ for $p'<p$ do not
change, and the new $e_p$ is the old $e_m$. By minimality $e_p\le e_m$. Equality would mean the same
inputs and the same operator, hence the same function, which Lemma 2(a) excludes; so $e_p<e_m$.

V: suppose $f$ is invariant under $\tau=(x_a\,x_{a+1})$ but $x_{a+1}$ is first read at position $p$
and $x_a$ only later (or at no earlier position). Rename by $\tau$. Gates before $p$ read neither
variable and are unchanged. Gate $p$ reads $x_{a+1}$ but not $x_a$; after renaming it reads $x_a$
instead, and its pair index strictly decreases (if the other input is a gate, the smaller element of
the pair decreases; if it is an input $x_c$ with $c\ne a,a+1$, either the larger element decreases or
the smaller one does while the larger stays). So $S$ decreases — contradiction. $\square$

*Proof of Theorem 1.* Take the chain of Lemma 4 and set every variable to its meaning: $s,o,f,v$ from
the chain; the auxiliaries of D to "rows where the two functions differ"; the auxiliary of L for
$(i,m)$ to "gates $i$ and $m$ read the same pair"; the auxiliaries of V to "$x_a$ has been read by
some gate at or before this position". The base clauses hold because the chain is normal, in $B$,
computes $f$ at its last gate, and its operators depend on both arguments (Lemma 2a). A and D hold
by Lemma 2, R by Lemma 3, L and V by Lemma 4. $\square$

The rules are claimed only at $k=C_B(f)$. For $k>C_B(f)$ the CNF may be unsatisfiable (for instance,
rule A forbids padding a chain with unused gates); the search never needs those $k$.

## 4. What "Machine-checked" means for a lower bound

For each refuted $k$ the run keeps the exact DIMACS file and CaDiCaL's binary DRAT proof, and
`drat-trim` checks the proof against that file (`s VERIFIED`). The SHA-256 of both files is in
`results/certificates.json`. So a lower bound $C_B(f)\ge K$ labelled **Machine-checked** rests on:

1. drat-trim's verdict for every $k<K$ (independent of the solver);
2. Theorem 1 above (a proof written here, not formalised); and
3. the encoder producing the CNF that Section 2 describes. This is tested, not proved: the encoder
   agrees with exhaustive enumeration (`brute_force.py`) on all 256 functions of 3 variables in
   both bases, reproduces Knuth's cost distribution over all 65,536 functions of 4 variables, and
   agrees class by class with the older, independently written encoding of
   `exact_circuit_complexity.py` (see `results/validation_encoding.json` and `tests/`).

Upper bounds need no trust in the encoding at all: every circuit is re-evaluated on the full truth
table by `exact_circuit_complexity.verify`.

**Where the proofs are.** The DRAT files total about 2 GB (the two 9-gate refutations are about
0.8 GB each), too large for this repository. They are reproducible: CaDiCaL is deterministic, so
with the pinned `python-sat` the command

    python3 certify_costs.py recheck --proofs DIR [--only MOD3_5] [--kmin 9]

regenerates each CNF and proof, requires both to be bit-identical to the SHA-256 recorded in
`results/certificates.json`, and runs drat-trim on them again. (Bit-identical regeneration was
confirmed for the 55 MB proof of MAJ_5 at k = 8, under a different machine load.)
