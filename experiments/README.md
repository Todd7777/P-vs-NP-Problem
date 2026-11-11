# experiments/

Exact circuit size of small Boolean functions by SAT, and one proof-complexity experiment.
Commands and the results table are in the top-level `README.md`; the encoding and its soundness
proof are in `ENCODING.md`.

## Scripts

| File | What it does |
|---|---|
| `exact_circuit_complexity.py` | First encoding (Kojevnikov–Kulikov–Yaroslavtsev style, light symmetry breaking). `n4`: all 222 NPN classes of 4-input functions; `explicit`: the explicit suite, with a conflict budget per call. Also the shared helpers (`verify`, `explicit_suite`, `gates_to_str`). |
| `circuit_sat.py` | Symmetry-reduced encoding (rules A, D, R, L, V of `ENCODING.md`), binary DRAT proofs from CaDiCaL, drat-trim checking. |
| `certify_costs.py` | Certified exact costs of the explicit suite: refutes every k below the known upper bound with a checked proof; `summarize`, `recheck` (bit-identical regeneration plus drat-trim), `merge`. |
| `build_final_table.py` | Labels every value (Theorem / Machine-checked / Numerical / Open) and writes `results/explicit_final.json`. |
| `validate_encoding.py` | Cross-checks of `circuit_sat.py`: brute force for n = 3, Knuth's distribution for n = 4 in B2, the first encoding for n = 4 in U2. |
| `brute_force.py` | Exhaustive enumeration of chains (no SAT), for the n = 3 cross-check. |
| `compare_optimal5.py` | Parses Knuth's optimal 5-input chains (optimal5 `knuthies.dat`) and compares every B2 value. |
| `crosscheck_old_encoding.py` | Re-derives refutations with the first encoding, as an independent check (`--cubes` splits a hard instance on the first two gates' input pairs). |
| `certify_n4_u2.py` | Settles the 4-input NPN classes whose U2 cost the first runs left open; writes the complete U2 distribution. |
| `certify_cubes.py` | Fallback for very large refutations: splits one instance into cubes on a gate's input pair, each with its own checked proof. |
| `certify_u2_suite.py` | U2 costs of the explicit functions that had only a B2 cost (`--proofs` for checked refutations, `--table` for the README table). |
| `upper_bound_search.py` | Looks for a circuit with exactly k gates (upper bounds only; the circuit is re-evaluated before it is reported). |
| `close_u2_n4.py`, `close_u2_n4_k8.py`, `summarize_u2_n4.py` | Earlier attempts at the n = 4 U2 distribution (budgeted first encoding). `summarize_u2_n4.py` cannot be rerun: one of its inputs was never committed. |
| `proof_complexity_php.py` | CDCL on pigeonhole formulas (exponential) vs the ordering principle (polynomial). |

## Results (`results/`)

| File | Contents |
|---|---|
| `explicit_final.json` | Final labelled costs of the explicit suite, with a verified circuit for every upper bound. |
| `certificates.json` | Per refutation: k, CNF and proof SHA-256, solver statistics, drat-trim verdict and time. |
| `explicit_costs.json`, `explicit_run.log` | First run of the explicit suite (intervals where the budget ran out). |
| `n4_exact_costs.json`, `n4_run.log` | First run over the 222 NPN classes of 4-input functions. |
| `n4_u2_complete.json`, `n4_u2_open_classes.json` | Complete U2 distribution for n = 4; certificates for the four classes that were open. |
| `u2_suite.json` | U2 costs of the other explicit functions, with per-k refutation records (hashes, drat-trim verdicts). |
| `n4_u2_summary.json`, `n4_u2_closure_k8.json` | Earlier U2 distribution for n = 4 with four classes open. |
| `validation_encoding.json` | Output of `validate_encoding.py`. |
| `optimal5_comparison.json` | Output of `compare_optimal5.py`. |
| `crosscheck_old_encoding.json`, `crosscheck_old_encoding_cubes.json` | Output of `crosscheck_old_encoding.py` (MOD3_4 in U2: k = 1..8, and k = 9 as 60 cubes). |
| `proof_complexity_php.json`, `.log` | Output of `proof_complexity_php.py`. |

Proof files are not committed (about 2 GB); see `ENCODING.md` §4 for how to regenerate and recheck them.
