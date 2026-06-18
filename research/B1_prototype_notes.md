# B1 Prototype Notes: Circuit Compression Metrics v0.1

Last updated: 2026-06-13

Problem: **25. Quantum compilation and circuit compression**

The first executable prototype layer is now in place. It does not yet optimize
circuits; it measures them consistently so that future optimization claims can
be checked.

## Current Components

- Seed circuit manifest: `../benchmarks/B1_seed_manifest.yaml`
- Seed OpenQASM circuits: `../benchmarks/b1_seed_circuits/`
- Imported QASMBench small manifest:
  `../benchmarks/QASMBench_small_manifest.yaml`
- Imported QASMBench small circuits: `../benchmarks/qasmbench_small/`
- Imported QASMBench medium exact manifest:
  `../benchmarks/QASMBench_medium_exact_manifest.yaml`
- Imported QASMBench medium exact circuits:
  `../benchmarks/qasmbench_medium_exact/`
- Imported QASMBench interaction exact manifest:
  `../benchmarks/QASMBench_interaction_exact_manifest.yaml`
- Imported QASMBench interaction exact circuits:
  `../benchmarks/qasmbench_interaction_exact/`
- Imported QASMBench interaction stress manifest:
  `../benchmarks/QASMBench_interaction_stress_manifest.yaml`
- Imported QASMBench interaction stress circuits:
  `../benchmarks/qasmbench_interaction_stress/`
- Rewrite smoke circuit: `../benchmarks/b1_rewrite_smoke/redundant_pairs.qasm`
- Hardware profiles: `../benchmarks/hardware_profiles.json`
- Metrics runner: `../tools/b1_qasm_metrics.py`
- Conservative local rewrite baseline: `../tools/b1_local_rewriter.py`
- Exact small-circuit equivalence checker: `../tools/b1_equivalence_check.py`
- Rewrite baseline harness: `../tools/b1_run_rewrite_baseline.py`
- Single-qubit block resynthesizer:
  `../tools/b1_single_qubit_resynth.py`
- CX-RZ-CX to RZZ window resynthesizer: `../tools/b1_rzz_resynth.py`
- Fixed-point B1 pipeline runner: `../tools/b1_run_pipeline.py`
- Proof-log audit runner: `../tools/b1_proof_log_audit.py`
- Proof-log replay runner: `../tools/b1_proof_log_replay.py`
- Proof-log semantic checker: `../tools/b1_proof_log_semantic_check.py`
- Pipeline-local rewrite certificate summaries:
  `../results/qasmbench_small_cert_pipeline/qasmbench_small_cert_summary.json`
  and
  `../results/qasmbench_interaction_stress_cert_pipeline/qasmbench_interaction_stress_cert_summary.json`
- First saved result: `../results/B1_seed_metrics_heavy_hex_like_sparse.json`

## Current Seed Set

The v0.1 seed set contains 10 small OpenQASM circuits:

1. Bell pair smoke test.
2. 3-qubit QFT.
3. 2-qubit Grover-style search.
4. Toy arithmetic adder with Toffoli.
5. Toy H2-style VQE ansatz.
6. Toy QEC syndrome extraction.
7. Toffoli chain.
8. Toy random Clifford circuit.
9. Toy Hamiltonian Trotter circuit.
10. Toy phase-estimation circuit.

These circuits are intentionally small. Their purpose is parser validation,
metric regression tests, and early optimizer smoke tests. They should be
augmented with exact QASMBench and MQT Bench circuits in B1 v0.2.

## Imported QASMBench Small Set

The first real benchmark subset contains 10 QASMBench circuits imported from
commit `357b942`:

1. `adder_n4.qasm`
2. `basis_change_n3.qasm`
3. `basis_test_n4.qasm`
4. `bell_n4.qasm`
5. `cat_state_n4.qasm`
6. `deutsch_n2.qasm`
7. `error_correctiond3_n5.qasm`
8. `fredkin_n3.qasm`
9. `grover_n2.qasm`
10. `hhl_n7.qasm`

The imported set has 10 circuits, 1072 total operations, maximum 7 qubits, and
total `heavy_hex_like_sparse` exposure 2.58262 before rewriting.

## Metrics Produced

- Qubit count and classical-bit count.
- Operation count and gate counts.
- Gate-class counts: single-qubit, two-qubit, multi-qubit, measurement.
- Greedy logical-depth proxy.
- Two-qubit-or-larger gate count.
- T-count and T-depth proxies.
- Hardware-weighted error exposure under a selected profile.

## First Validation Results

Metrics runner:

- Parsed all 10 seed circuits successfully.
- Produced saved metrics for four hardware profiles:
  - `heavy_hex_like_sparse`
  - `linear_nearest_neighbor`
  - `all_to_all_ion_trap_like`
  - `neutral_atom_reconfigurable`

Rewrite smoke test under `heavy_hex_like_sparse`:

| Metric | Before | After |
|---|---:|---:|
| Operation count | 12 | 5 |
| Logical-depth proxy | 7 | 3 |
| Two-qubit-or-larger gate count | 3 | 1 |
| Hardware-weighted exposure | 0.05484 | 0.04222 |

Equivalence:

- Smoke rewrite pair: 1/1 passed.
- Fidelity: 1.0.
- Max global-phase-adjusted delta: 1.11e-16.

Seed-set rewrite test:

- Circuits parsed before and after rewrite: 10 -> 10.
- Total operations: 117 -> 117.
- Total hardware-weighted exposure: 0.6788 -> 0.6788.
- Exact statevector equivalence checks: 10/10 passed.
- Interpretation: the current seed set has no trivial adjacent cancellations,
  so the baseline correctly leaves it unchanged.

Harness outputs:

- Smoke summary: `../results/harness_smoke/smoke_summary.json`
- Seed summary: `../results/harness_seed/seed_summary.json`

QASMBench small harness v2 under `heavy_hex_like_sparse`:

| Metric | Before | After |
|---|---:|---:|
| Circuits | 10 | 10 |
| Operation count | 1072 | 1071 |
| Logical-depth proxy | 768 | 768 |
| Hardware-weighted exposure | 2.58262 | 2.58256 |
| Exact equivalence failures | 0 | 0 |

Interpretation: conservative local rewriting found only one real simplification
in the imported QASMBench subset, an `id` gate removal in
`error_correctiond3_n5.qasm`. This is a useful correctness milestone, but it is
not yet a meaningful compression result. The next real research step is a
hardware-aware search that can commute, regroup, and resynthesize small
windows while proving or testing equivalence.

QASMBench harness outputs:

- Metrics probe:
  `../results/QASMBench_small_metrics_heavy_hex_like_sparse.json`
- v2 harness summary:
  `../results/qasmbench_small_harness_v2/qasmbench_small_v2_summary.json`

Single-qubit block resynthesis v0:

This prototype compresses adjacent runs of single-qubit gates on the same
qubit into one OpenQASM `u3` gate, then validates the rewritten circuit with
the exact statevector equivalence checker. It is a first hardware-aware window
resynthesis step because it reduces single-qubit exposure and idle-layer
pressure while preserving all multi-qubit structure.

QASMBench small result under `heavy_hex_like_sparse`:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Operation count | 1072 | 851 | 20.62% |
| Logical-depth proxy | 768 | 569 | 25.91% |
| Hardware-weighted exposure | 2.58262 | 2.51468 | 2.63% |
| Exact equivalence failures | 0 | 0 | n/a |

Hardware-profile exposure reductions:

| Profile | Before | After | Reduction |
|---|---:|---:|---:|
| `linear_nearest_neighbor` | 3.25295 | 3.15145 | 3.12% |
| `heavy_hex_like_sparse` | 2.58262 | 2.51468 | 2.63% |
| `all_to_all_ion_trap_like` | 1.25331 | 1.21934 | 2.71% |
| `neutral_atom_reconfigurable` | 4.18928 | 4.05422 | 3.22% |

Outputs:

- Rewritten circuits: `../results/qasmbench_small_1q_resynth/`
- Main summary: `../results/qasmbench_small_1q_summary.json`
- Profile summary: `../results/qasmbench_small_1q_profile_summary.json`
- Equivalence report: `../results/qasmbench_small_1q_equivalence.json`

Interpretation: this is the first non-trivial, equivalence-checked compression
result on real imported benchmark circuits. It does **not** yet satisfy the B1
paper-quality threshold because the benchmark has only 10 circuits and
hardware-weighted exposure reduction is far below the target 20% median
reduction. It does validate the methodology needed for stronger 2-4 qubit
window search.

Commuting-aware single-qubit block resynthesis v0:

This variant lets pending single-qubit blocks cross operations that touch only
other qubits. It remains conservative: whenever a later operation touches the
same qubit, the pending block is flushed before that operation. Exact
statevector equivalence remains the acceptance gate.

QASMBench small result under `heavy_hex_like_sparse`:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Operation count | 1072 | 840 | 21.64% |
| Logical-depth proxy | 768 | 565 | 26.43% |
| Hardware-weighted exposure | 2.58262 | 2.51332 | 2.68% |
| Exact equivalence failures | 0 | 0 | n/a |

Increment over adjacent-only 1Q resynthesis:

- Operation count: 851 -> 840.
- Logical-depth proxy: 569 -> 565.
- Hardware-weighted exposure: 2.51468 -> 2.51332.

Hardware-profile exposure reductions:

| Profile | Before | After | Reduction |
|---|---:|---:|---:|
| `linear_nearest_neighbor` | 3.25295 | 3.14870 | 3.20% |
| `heavy_hex_like_sparse` | 2.58262 | 2.51332 | 2.68% |
| `all_to_all_ion_trap_like` | 1.25331 | 1.21866 | 2.76% |
| `neutral_atom_reconfigurable` | 4.18928 | 4.05008 | 3.32% |

Outputs:

- Rewritten circuits: `../results/qasmbench_small_1q_commute/`
- Main summary: `../results/qasmbench_small_1q_commute_summary.json`
- Profile summary:
  `../results/qasmbench_small_1q_commute_profile_summary.json`
- Equivalence report:
  `../results/qasmbench_small_1q_commute_equivalence.json`

RZZ interaction-window resynthesis v0:

This 2Q prototype rewrites adjacent interaction windows of the form
`cx control,target; rz(theta) target; cx control,target;` into one
`rzz(theta) control,target;`. This is hardware-aware because several platforms
can expose native or lower-overhead ZZ-type interactions, and because it
directly reduces two-qubit gate pressure. The equivalence checker was extended
with exact `rzz` statevector semantics.

QASMBench small result for `commuting_1q + rzz` under
`heavy_hex_like_sparse`:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Operation count | 1072 | 790 | 26.31% |
| Two-qubit-or-larger gate count | 320 | 295 | 7.81% |
| Logical-depth proxy | 768 | 535 | 30.34% |
| Hardware-weighted exposure | 2.58262 | 2.35662 | 8.75% |
| Exact equivalence failures | 0 | 0 | n/a |

Increment over commuting-aware 1Q resynthesis:

- Operation count: 840 -> 790.
- Logical-depth proxy: 565 -> 535.
- Hardware-weighted exposure: 2.51332 -> 2.35662.

Hardware-profile exposure reductions:

| Profile | Before | After | Reduction |
|---|---:|---:|---:|
| `linear_nearest_neighbor` | 3.25295 | 2.93845 | 9.67% |
| `heavy_hex_like_sparse` | 2.58262 | 2.35662 | 8.75% |
| `all_to_all_ion_trap_like` | 1.25331 | 1.14031 | 9.02% |
| `neutral_atom_reconfigurable` | 4.18928 | 3.78628 | 9.62% |

Outputs:

- Rewritten circuits: `../results/qasmbench_small_1q_commute_rzz/`
- Main summary: `../results/qasmbench_small_1q_rzz_summary.json`
- Profile summary: `../results/qasmbench_small_1q_rzz_profile_summary.json`
- Equivalence report: `../results/qasmbench_small_1q_rzz_equivalence.json`

Interpretation: this is the first B1 prototype that directly reduces
two-qubit gate pressure on imported benchmark circuits. It is still below the
20% hardware-weighted exposure target, but it moves from a single-qubit cleanup
result into genuine hardware-aware interaction-window resynthesis.

Iterative commuting-aware RZZ resynthesis v0:

The strongest current pipeline has been automated in
`../tools/b1_run_pipeline.py`:

1. Run commuting-aware 1Q block resynthesis.
2. Run adjacent `cx-rz-cx -> rzz`.
3. Run commuting-aware RZZ scans until a fixed point is reached.

The QASMBench small run converged after three RZZ passes:

| Pass | Mode | Windows |
|---:|---|---:|
| 1 | adjacent | 25 |
| 2 | commute-disjoint | 2 |
| 3 | commute-disjoint | 0 |

QASMBench small result under `heavy_hex_like_sparse`:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Operation count | 1072 | 786 | 26.68% |
| Two-qubit-or-larger gate count | 320 | 293 | 8.44% |
| Logical-depth proxy | 768 | 531 | 30.86% |
| Hardware-weighted exposure | 2.58262 | 2.34354 | 9.26% |
| Exact equivalence failures | 0 | 0 | n/a |

Increment over single-pass RZZ:

- Operation count: 790 -> 786.
- Two-qubit-or-larger gate count: 295 -> 293.
- Logical-depth proxy: 535 -> 531.
- Hardware-weighted exposure: 2.35662 -> 2.34354.

Hardware-profile exposure reductions:

| Profile | Before | After | Reduction |
|---|---:|---:|---:|
| `linear_nearest_neighbor` | 3.25295 | 2.92095 | 10.21% |
| `heavy_hex_like_sparse` | 2.58262 | 2.34354 | 9.26% |
| `all_to_all_ion_trap_like` | 1.25331 | 1.13377 | 9.54% |
| `neutral_atom_reconfigurable` | 4.18928 | 3.76436 | 10.14% |

Outputs:

- Rewritten circuits: `../results/qasmbench_small_1q_rzz_commute_secondpass/`
- Main summary: `../results/qasmbench_small_1q_iterative_rzz_summary.json`
- Profile summary:
  `../results/qasmbench_small_1q_iterative_rzz_profile_summary.json`
- Equivalence report:
  `../results/qasmbench_small_1q_rzz_commute_secondpass_equivalence.json`
- Automated fixed-point pipeline work directory:
  `../results/qasmbench_small_fixed_point_pipeline_work/`
- Automated fixed-point pipeline summary:
  `../results/qasmbench_small_fixed_point_pipeline/qasmbench_small_fixed_point_summary.json`
- Automated fixed-point profile summary:
  `../results/qasmbench_small_fixed_point_pipeline/profile_summary.json`

QASMBench medium exact subset:

The fixed-point pipeline was also run on a 6-circuit medium subset selected for
exact statevector verification up to 15 qubits:

1. `sat_n11.qasm`
2. `seca_n11.qasm`
3. `multiply_n13.qasm`
4. `bv_n14.qasm`
5. `qf21_n15.qasm`
6. `gcm_h6.qasm`

QASMBench medium exact result under `heavy_hex_like_sparse`:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Operation count | 3465 | 2145 | 38.10% |
| Two-qubit-or-larger gate count | 921 | 921 | 0.00% |
| Logical-depth proxy | 2611 | 1622 | 37.88% |
| Hardware-weighted exposure | 7.70228 | 7.10932 | 7.70% |
| Exact equivalence failures | 0 | 0 | n/a |

Medium interpretation: this subset has no `cx-rz-cx` windows after 1Q
resynthesis, so the gain comes almost entirely from commuting-aware 1Q block
resynthesis. This is useful evidence that the pipeline generalizes beyond the
small set, while also showing that stronger 2Q search needs benchmark families
with more interaction-simulation structure.

Small + medium aggregate under `heavy_hex_like_sparse`:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Circuits | 16 | 16 | n/a |
| Operation count | 4537 | 2931 | 35.40% |
| Two-qubit-or-larger gate count | 1241 | 1214 | 2.18% |
| Logical-depth proxy | 3379 | 2153 | 36.28% |
| Hardware-weighted exposure | 10.28490 | 9.45286 | 8.09% |
| Exact equivalence failures | 0 | 0 | n/a |

Outputs:

- Medium summary:
  `../results/qasmbench_medium_exact_fixed_point_pipeline/qasmbench_medium_exact_fixed_point_summary.json`
- Medium profile summary:
  `../results/qasmbench_medium_exact_fixed_point_pipeline/profile_summary.json`
- Small + medium aggregate:
  `../results/B1_qasmbench_small_medium_fixed_point_summary.json`

QASMBench interaction exact subset:

To specifically test whether RZZ interaction-window resynthesis helps
simulation-like circuits, the pipeline was run on:

1. `basis_trotter_n4.qasm`
2. `ising_n10.qasm`

QASMBench interaction exact result under `heavy_hex_like_sparse`:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Operation count | 2000 | 1359 | 32.05% |
| Two-qubit-or-larger gate count | 552 | 447 | 19.02% |
| Logical-depth proxy | 886 | 645 | 27.20% |
| Hardware-weighted exposure | 3.68012 | 2.97604 | 19.13% |
| Exact equivalence failures | 0 | 0 | n/a |

RZZ pass windows: 105 -> 0.

Hardware-profile exposure reductions:

| Profile | Before | After | Reduction |
|---|---:|---:|---:|
| `linear_nearest_neighbor` | 4.91370 | 3.94090 | 19.80% |
| `heavy_hex_like_sparse` | 3.68012 | 2.97604 | 19.13% |
| `all_to_all_ion_trap_like` | 1.82606 | 1.47402 | 19.28% |
| `neutral_atom_reconfigurable` | 6.24528 | 5.00376 | 19.88% |

Interpretation: this is the strongest evidence so far that the B1 method is
near the 20% hardware-weighted exposure target on the intended circuit family:
interaction-simulation workloads. The sample is still only 2 circuits, so it is
not yet a paper-quality claim; it is a high-priority signal for targeted
benchmark expansion.

Small + medium + interaction aggregate under `heavy_hex_like_sparse`:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Circuits | 18 | 18 | n/a |
| Operation count | 6537 | 4290 | 34.37% |
| Two-qubit-or-larger gate count | 1793 | 1661 | 7.36% |
| Logical-depth proxy | 4265 | 2798 | 34.40% |
| Hardware-weighted exposure | 13.96502 | 12.42890 | 11.00% |
| Exact equivalence failures | 0 | 0 | n/a |

Outputs:

- Interaction summary:
  `../results/qasmbench_interaction_exact_fixed_point_pipeline/qasmbench_interaction_exact_fixed_point_summary.json`
- Interaction profile summary:
  `../results/qasmbench_interaction_exact_fixed_point_pipeline/profile_summary.json`
- Small + medium + interaction aggregate:
  `../results/B1_qasmbench_small_medium_interaction_fixed_point_summary.json`

QASMBench interaction stress sample:

The `hhl_n10.qasm` stress sample has 10 qubits but 186,801 operations. The
pipeline was run with global exact statevector equivalence intentionally
skipped; the result is therefore not part of the exact-verified aggregate.
The transformations are still local-rule certified: commuting-aware 1Q block
resynthesis and `cx-rz-cx -> rzz` are applied by construction.

Stress result under `heavy_hex_like_sparse`:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Operation count | 186801 | 136441 | 26.96% |
| Two-qubit-or-larger gate count | 72449 | 58433 | 19.35% |
| Logical-depth proxy | 147739 | 109399 | 25.95% |
| Hardware-weighted exposure | 494.92620 | 394.43484 | 20.30% |
| Global exact equivalence | skipped | skipped | n/a |

RZZ pass windows: 14013 -> 3 -> 0.

Hardware-profile exposure reductions:

| Profile | Before | After | Reduction |
|---|---:|---:|---:|
| `linear_nearest_neighbor` | 663.42820 | 528.08020 | 20.40% |
| `heavy_hex_like_sparse` | 494.92620 | 394.43484 | 20.30% |
| `all_to_all_ion_trap_like` | 247.45710 | 197.21142 | 20.30% |
| `neutral_atom_reconfigurable` | 831.97220 | 661.76756 | 20.46% |

Interpretation: this is the first stress result above the 20%
hardware-weighted exposure target, but it is not yet an exact-verified claim.
It should drive the next verifier milestone: scalable local-certificate or
chunked equivalence validation for large-operation circuits.

Outputs:

- Stress summary:
  `../results/qasmbench_interaction_stress_fixed_point_pipeline/qasmbench_interaction_stress_fixed_point_summary.json`
- Stress profile summary:
  `../results/qasmbench_interaction_stress_fixed_point_pipeline/profile_summary.json`

Local rewrite certificate summaries:

The fixed-point runner now records machine-readable local certificate totals in
its JSON summary. These certificates do not replace global equivalence checks;
they make the applied transformations auditable when global statevector
simulation is impractical.

QASMBench small certificate rerun:

- Summary:
  `../results/qasmbench_small_cert_pipeline/qasmbench_small_cert_summary.json`
- Certificate mode: `local_rewrite_certificates_plus_exact_statevector`
- Exact equivalence failures: 0/10.
- 1Q certificates: 163 resynthesized runs, 231 removed 1Q gates, 1 removed
  identity gate, 1,299 disjoint-commuted 1Q gates.
- RZZ certificates: 27 windows, 2 disjoint-commuting windows, 54 removed CX
  gates, 27 inserted RZZ gates.

QASMBench interaction stress certificate rerun:

- Summary:
  `../results/qasmbench_interaction_stress_cert_pipeline/qasmbench_interaction_stress_cert_summary.json`
- Certificate mode: `local_rewrite_certificates_without_global_statevector`
- Global exact equivalence: skipped.
- 1Q certificates: 17,157 resynthesized runs, 22,328 removed 1Q gates,
  553,005 disjoint-commuted 1Q gates.
- RZZ certificates: 14,016 windows, 3 disjoint-commuting windows, 28,032
  removed CX gates, 14,016 inserted RZZ gates.
- Compression result remains unchanged from the prior stress run: 20.30%
  heavy-hex-like exposure reduction and 19.35% two-qubit-or-larger gate
  reduction.

Interpretation: the stress result is now better bounded. It is still not a
global exact-equivalence claim, but it is no longer merely a verbal structural
claim: the pipeline records the exact classes and counts of local identities
used to produce the large-circuit compression.

Proof-log audit layer:

The certificate layer has been upgraded from aggregate counts to JSONL
per-rewrite proof logs. Each event records the rule, input/output files, input
line numbers, input gate text, output gate text, and commute-disjoint evidence
where relevant. The audit runner checks that proof-log counts match the
pipeline summary and that referenced input QASM lines match the recorded gate
text.

QASMBench small proof-log rerun:

- Summary:
  `../results/qasmbench_small_prooflog_pipeline/qasmbench_small_prooflog_summary.json`
- 1Q proof log:
  `../results/qasmbench_small_prooflog_pipeline/qasmbench_small_prooflog_1q_proofs.jsonl`
- RZZ proof logs:
  `../results/qasmbench_small_prooflog_pipeline/qasmbench_small_prooflog_rzz_pass_1_proofs.jsonl`
  and
  `../results/qasmbench_small_prooflog_pipeline/qasmbench_small_prooflog_rzz_pass_2_proofs.jsonl`
- Audit:
  `../results/qasmbench_small_prooflog_pipeline/qasmbench_small_prooflog_audit.json`
- Audit result: passed, 0 errors.
- Proof events: 164 1Q events and 27 RZZ events.
- Exact equivalence failures: 0/10.

QASMBench interaction stress proof-log rerun:

- Summary:
  `../results/qasmbench_interaction_stress_prooflog_pipeline/qasmbench_interaction_stress_prooflog_summary.json`
- 1Q proof log:
  `../results/qasmbench_interaction_stress_prooflog_pipeline/qasmbench_interaction_stress_prooflog_1q_proofs.jsonl`
- RZZ proof logs:
  `../results/qasmbench_interaction_stress_prooflog_pipeline/qasmbench_interaction_stress_prooflog_rzz_pass_1_proofs.jsonl`
  and
  `../results/qasmbench_interaction_stress_prooflog_pipeline/qasmbench_interaction_stress_prooflog_rzz_pass_2_proofs.jsonl`
- Audit:
  `../results/qasmbench_interaction_stress_prooflog_pipeline/qasmbench_interaction_stress_prooflog_audit.json`
- Audit result: passed, 0 errors.
- Proof events: 17,157 1Q events and 14,016 RZZ events.
- Global exact equivalence: skipped.

Interpretation: this creates the first scalable verifier substrate for B1.
The audit still does not prove full-circuit equivalence by itself, but it makes
every local transformation traceable to concrete QASM lines and checks the
commutation side condition used by the current RZZ pass.

Proof-log replay checker:

The proof-log layer now has a replay checker that reconstructs every emitted
pass output from the previous QASM stage plus the JSONL proof log, then compares
the replayed output with the actual rewritten QASM files. This is stronger than
the audit runner: audit checks that events reference real input lines; replay
checks that the events and pass scheduling reproduce the exact output files.

QASMBench small replay:

- Replay report:
  `../results/qasmbench_small_prooflog_pipeline/qasmbench_small_prooflog_replay.json`
- Replay result: passed, 0 errors.
- Stages replayed: 1Q resynthesis plus 3 RZZ passes.
- Files checked per stage: 10.
- Proof events replayed: 164 1Q events and 27 RZZ events.

QASMBench interaction stress replay:

- Replay report:
  `../results/qasmbench_interaction_stress_prooflog_pipeline/qasmbench_interaction_stress_prooflog_replay.json`
- Replay result: passed, 0 errors.
- Stages replayed: 1Q resynthesis plus 3 RZZ passes.
- Files checked per stage: 1.
- Proof events replayed: 17,157 1Q events and 14,016 RZZ events.

Interpretation: B1 now has a scalable syntactic verifier for large-operation
circuits. The hhl_n10 stress result is still not a global exact-equivalence
claim, but its transformation trace is reproducible from proof logs down to
the emitted QASM. The next verifier milestone is semantic replay: independently
checking each local identity's unitary or channel semantics and then composing
the checked identities into a circuit-level certificate.

Proof-log local semantic checker:

The proof-log layer now checks local unitary semantics for every recorded
rewrite event. For 1Q resynthesis events, the checker multiplies the input
single-qubit gate matrices and compares the result with the emitted `u3` matrix
up to global phase. For RZZ events, it compares the 4x4 unitary of
`cx; rz(theta); cx` with the emitted `rzz(theta)` unitary under the same RZZ
semantics as the exact statevector checker.

QASMBench small semantic check:

- Semantic report:
  `../results/qasmbench_small_prooflog_pipeline/qasmbench_small_prooflog_semantic.json`
- Semantic result: passed, 0 errors.
- Events checked: 164 1Q events and 27 RZZ events.
- Max 1Q global-phase-adjusted delta: 3.15e-16.
- Max RZZ global-phase-adjusted delta: 0.0.

QASMBench interaction stress semantic check:

- Semantic report:
  `../results/qasmbench_interaction_stress_prooflog_pipeline/qasmbench_interaction_stress_prooflog_semantic.json`
- Semantic result: passed, 0 errors.
- Events checked: 17,157 1Q events and 14,016 RZZ events.
- Max 1Q global-phase-adjusted delta: 3.56e-16.
- Max RZZ global-phase-adjusted delta: 0.0.

Interpretation: the hhl_n10 stress result is now supported by three scalable
certificate layers: proof-log audit, syntactic replay, and per-event local
semantic identity checking. This still does not replace full-circuit exact
statevector verification, but it materially narrows the verification gap for
large-operation circuits where global simulation is impractical.

## Exact-Checkable Extension to 30 Circuits

B1 now has a deterministic exact-checkable extension suite generated by
`../tools/b1_generate_exact_extension.py`:

- Manifest: `../benchmarks/B1_exact_extension_manifest.yaml`
- Circuits: `../benchmarks/b1_exact_extension/`
- Pipeline summary:
  `../results/b1_exact_extension_fixed_point_pipeline/b1_exact_extension_fixed_point_summary.json`
- Audit/replay/semantic reports:
  `../results/b1_exact_extension_fixed_point_pipeline/b1_exact_extension_fixed_point_audit.json`,
  `../results/b1_exact_extension_fixed_point_pipeline/b1_exact_extension_fixed_point_replay.json`,
  and
  `../results/b1_exact_extension_fixed_point_pipeline/b1_exact_extension_fixed_point_semantic.json`
- 30-circuit aggregate summary:
  `../results/B1_exact_30_circuit_fixed_point_summary.json`

The extension adds 12 generated circuits covering Hamiltonian/Trotter,
ring-interaction, QEC-syndrome, arithmetic-phase, QFT, long-range echo,
commuting-window, chemistry-ansatz, BV-oracle, QAOA, stabilizer, and
Toffoli-phase patterns.

Extension result:

- Exact equivalence: 12 passed, 0 failed.
- Proof-log audit/replay/semantic: all passed.
- Proof events: 11 1Q events and 80 RZZ events.
- Operation-count reduction: 31.73%.
- Two-qubit-gate reduction: 43.24%.
- Logical-depth reduction: 47.09%.
- Heavy-hex-like exposure reduction: 22.28%.

30-circuit exact aggregate:

- Circuit count: 30.
- Equivalence failures: 0.
- Operation-count reduction: 34.17%.
- Two-qubit-gate reduction: 10.72%.
- Logical-depth reduction: 34.98%.
- Heavy-hex-like exposure reduction: 12.58%.

Interpretation: the exact circuit-count gate is now met. The result is still
not a full B1 acceptance claim because the 30-circuit aggregate exposure
reduction remains below the 20% portfolio target, the added 12 circuits are
generated rather than external MQT/QASMBench circuits, and the hhl_n10 stress
run still lacks global exact equivalence.

## 30-Circuit Ablation

B1 now has a generated ablation report:

- Markdown report: `B1_ablation_report.md`
- Machine-readable report: `B1_ablation_report.json`
- Generator: `../tools/b1_build_ablation_report.py`

Aggregate stage reductions on the 30 exact-checkable circuits:

| Stage | Operation reduction | 2Q reduction | Depth reduction | Exposure reduction |
|---|---:|---:|---:|---:|
| after 1Q resynthesis | 28.18% | 0.00% | 29.66% | 4.42% |
| after adjacent RZZ | 34.12% | 10.62% | 34.89% | 12.50% |
| final | 34.17% | 10.72% | 34.98% | 12.58% |

Contribution share:

- 1Q resynthesis contributes 82.46% of operation-count reduction and 84.78%
  of depth reduction.
- Adjacent RZZ contributes 99.06% of two-qubit-gate reduction and 64.23% of
  hardware-exposure reduction.
- Later fixed-point RZZ passes contribute less than 1% of total reduction on
  this 30-circuit exact aggregate.

Interpretation: to reach the 20% aggregate exposure target, the next optimizer
work should either find more RZZ-like two-qubit structure in external circuits
or add a genuinely hardware-aware 2-4 qubit window pass. More 1Q resynthesis
alone is unlikely to close the exposure gap.

## Qiskit Baseline Comparison

B1 now has an independent Qiskit all-to-all `u3/cx` baseline comparison:

- Runner: `../tools/b1_qiskit_baseline.py`
- Baseline suite summary:
  `../results/b1_qiskit_baseline_30/qiskit_baseline_suite_summary.json`
- Comparison report: `B1_baseline_comparison.md`
- Machine-readable comparison: `B1_baseline_comparison.json`

On the 30-circuit exact suite:

| Method | Equivalence failures | Operation | 2Q | Depth | Exposure |
|---|---:|---:|---:|---:|---:|
| B1 fixed-point | 0 | 34.17% | 10.72% | 34.98% | 12.58% |
| Qiskit level 1 | 0 | 14.60% | -25.63% | 15.25% | -13.36% |

Qiskit level 0 and level 1 both pass exact equivalence. Qiskit level 3 is
kept only as a diagnostic row because it fails exact equivalence on 7 of 30
circuits under the local statevector checker.

Interpretation: B1 now has a first independent compiler baseline comparison
and beats the best exact-valid Qiskit row on operation count, two-qubit count,
logical depth, and hardware-weighted exposure. This is still not a calibrated
heavy-hex routing baseline; the current Qiskit comparison uses all-to-all
connectivity and `u3/cx/measure` basis.

## Qiskit Line-Routing Diagnostic

B1 also has a line-coupling Qiskit routing diagnostic:

- Runner: `../tools/b1_qiskit_line_routing_baseline.py`
- Measurement-distribution checker:
  `../tools/b1_measurement_distribution_check.py`
- Diagnostic builder: `../tools/b1_build_routing_baseline_diagnostic.py`
- Aer cross-check: `../tools/b1_aer_measurement_crosscheck.py`
- Suite summary:
  `../results/b1_qiskit_line_routing_30/qiskit_line_routing_suite_summary.json`
- Diagnostic report: `B1_routing_baseline_diagnostic.md`
- Machine-readable diagnostic: `B1_routing_baseline_diagnostic.json`

On the 30-circuit exact suite:

| Qiskit level | Statevector pass/fail | Measurement distribution pass/fail | Operation | 2Q | Depth | Exposure |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 11 / 19 | 30 / 0 | -59.81% | -173.66% | -68.46% | -131.42% |
| 1 | 10 / 20 | 30 / 0 | -9.31% | -111.02% | -14.43% | -78.76% |
| 3 | 7 / 23 | 30 / 0 | 8.99% | -50.10% | 14.83% | -31.86% |

Negative reduction means the routed baseline worsened that metric.

Independent Qiskit Aer shot-based cross-check:

| Qiskit level | Pairs pass/fail | Shots per pair | Max TVD | Max threshold |
|---:|---:|---:|---:|---:|
| 0 | 30 / 0 | 32768 | 0.04984 | 0.20066 |
| 1 | 30 / 0 | 32768 | 0.04672 | 0.20066 |
| 3 | 30 / 0 | 32768 | 0.04819 | 0.20066 |

Interpretation: the line-routing result is useful but diagnostic-only. The
sequential measurement-distribution checker now branches on mid-circuit
measurements and shows 30/30 output-distribution equivalence for all tested
line-routing levels. Qiskit Aer independently cross-checks those output
distributions with 32,768 shots per pair across 90 routed pairs. The bare
statevector checker still fails because it is not layout- and
measurement-mapping aware. This does not close the calibrated heavy-hex
routing-baseline gate.

## Qiskit Heavy-Hex Topology Diagnostic

B1 now has a first heavy-hex distance-3 routing diagnostic:

- Runner: `../tools/b1_qiskit_heavyhex_routing_baseline.py`
- Diagnostic builder: `../tools/b1_build_heavyhex_routing_report.py`
- Diagnostic report: `B1_heavyhex_routing_diagnostic.md`
- Machine-readable diagnostic: `B1_heavyhex_routing_diagnostic.json`

The Qiskit heavy-hex distance-3 coupling map has 19 physical qubits and 40
directed coupling edges. The first interactive diagnostic uses optimization
level 0 and Qiskit Aer cross-checks with 2,048 shots per pair.

| Qiskit level | Aer pass/fail | Shots | Operation | 2Q | Depth | Exposure |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 30 / 0 | 2048 | -66.25% | -196.71% | -72.71% | -164.71% |

Interpretation: routing to a sparse heavy-hex physical topology creates large
operation, two-qubit, depth, and exposure overhead on the source circuits. This
is a real topology-aware baseline, but not a calibrated device baseline because
it does not include backend-specific gate durations, error rates, readout
errors, or a noise model.

## Heavy-Hex End-to-End Routed Benefit

B1 now has a source-routed versus B1-routed heavy-hex comparison:

- Runner: `../tools/b1_heavyhex_end_to_end_compare.py`
- Report builder: `../tools/b1_build_heavyhex_end_to_end_report.py`
- Report: `B1_heavyhex_end_to_end_report.md`
- Machine-readable report: `B1_heavyhex_end_to_end_report.json`

Both the original source circuits and B1 fixed-point output circuits are routed
to the same heavy-hex distance-3 topology with Qiskit level 0. Output
distributions are cross-checked by Qiskit Aer between the source logical
circuits and the B1 optimized routed circuits.

| Metric | Reduction after routing |
|---|---:|
| Operation count | 16.95% |
| Two-qubit gates | 0.00% |
| Logical depth | 19.44% |
| Hardware-weighted exposure | 2.93% |
| Idle-layer proxy | 20.55% |

Aer cross-check: 30 pass / 0 fail with 2,048 shots per pair.

The level-0 result is now paired with a level-1 suite result in
`B1_heavyhex_end_to_end_suite.md`:

| Qiskit level | Operation | 2Q | Depth | Exposure | Idle proxy |
|---:|---:|---:|---:|---:|---:|
| 0 | 16.95% | 0.00% | 19.44% | 2.93% | 20.55% |
| 1 | 0.03% | 0.00% | 0.00% | 0.00% | -0.00% |

Interpretation: B1's current fixed-point compression retains operation, depth,
idle-layer, and small exposure benefits after conservative heavy-hex level-0
routing, but Qiskit level 1 nearly erases those benefits. It does not reduce
post-routing two-qubit count at either level. This makes a routing-aware 2-4
qubit window pass the next most important algorithmic step.

## Post-Routing Bottleneck Profile

B1 now has a per-circuit post-routing bottleneck profile:

- Profiler: `../tools/b1_post_routing_bottleneck_profiler.py`
- Report: `B1_post_routing_bottleneck_profile.md`
- Machine-readable report: `B1_post_routing_bottleneck_profile.json`

Key findings:

- Level 0 preserves 2.93% exposure reduction and 19.44% depth reduction after
  heavy-hex routing.
- Level 1 leaves only 0.0004% exposure reduction and 0.00% depth reduction.
- 16 circuits have level-0 exposure or depth benefits that are erased by level
  1 routing.
- The largest level-1 two-qubit bottlenecks are
  `qasmbench_medium_exact/gcm_h6.qasm`,
  `qasmbench_interaction_exact/basis_trotter_n4.qasm`,
  `qasmbench_medium_exact/sat_n11.qasm`, and
  `qasmbench_small/hhl_n7.qasm`.
- The top bottleneck, `gcm_h6.qasm`, has 1,269 optimized routed 2Q gates at
  level 1 and no 2Q reduction from B1.

Interpretation: the next B1 algorithm should stop optimizing only the logical
pre-routing circuit. It should search for 2-4 qubit rewrites whose cost model
includes the target coupling graph, expected swaps, and route-induced depth.

## Post-Routing SWAP Macro Compression

B1 now has a first routing-aware post-routing macro pass:

- Runner: `../tools/b1_post_routing_swap_macro_resynth.py`
- Report: `B1_post_routing_swap_macro_report.md`
- Machine-readable report: `B1_post_routing_swap_macro_report.json`
- Proof log:
  `../results/b1_post_routing_swap_macro_level1/swap_macro_proofs.jsonl`

The pass scans Qiskit heavy-hex level-1 routed B1 outputs for
`cx a,b; cx b,a; cx a,b` and rewrites each triple to `swap a,b`.

On the 30-circuit level-1 routed B1 suite:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Operation count | 7443 | 6481 | 12.92% |
| Two-qubit macro count | 3881 | 2919 | 24.79% |
| Logical depth | 4923 | 4164 | 15.42% |
| Hardware-weighted exposure | 28.95372 | 22.68184 | 21.66% |
| Idle-layer proxy | 82213 | 69716 | 15.20% |

Proof and output checks:

- SWAP macros identified: 481.
- CX gates removed: 1,443.
- SWAP macro gates inserted: 481.
- Local Aer cross-check, original B1 routed vs SWAP macro: 30 pass / 0 fail.
- End-to-end Aer cross-check, source logical vs SWAP macro: 30 pass / 0 fail.

Top SWAP macro circuits:

| Circuit | SWAP macros | Removed CX |
|---|---:|---:|
| `qasmbench_medium_exact/gcm_h6.qasm` | 158 | 474 |
| `qasmbench_medium_exact/sat_n11.qasm` | 96 | 288 |
| `qasmbench_interaction_exact/basis_trotter_n4.qasm` | 60 | 180 |
| `qasmbench_medium_exact/qf21_n15.qasm` | 54 | 162 |
| `qasmbench_small/hhl_n7.qasm` | 37 | 111 |

Interpretation: this is the first B1 result that directly attacks the
post-routing 2Q bottleneck found in the bottleneck profile. It remains a
diagnostic macro-IR result, not a native-basis hardware claim: if a target
backend decomposes `swap` back into three CX gates, the physical 2Q reduction
does not survive. The next step is to turn this into a native-basis-aware
2-4 qubit optimizer that either finds lower-cost swap implementations or
co-designs with routing so the macro never appears.

## Virtual SWAP Elimination

B1 now has a first native-CX-reducing post-routing transformation:

- Runner: `../tools/b1_virtual_swap_elimination.py`
- Report: `B1_virtual_swap_elimination_report.md`
- Machine-readable report: `B1_virtual_swap_elimination_report.json`
- Proof log:
  `../results/b1_virtual_swap_elimination_level1/virtual_swap_elimination_proofs.jsonl`
- Proof-log replay: `B1_virtual_swap_replay_report.md`

Instead of replacing a routed `cx-cx-cx` SWAP with a `swap` macro, this pass
removes the SWAP entirely and tracks a virtual wire permutation. Later gates
are rewritten onto the permuted wires, and measurements are remapped through
the same line-label permutation when no classical control or reset is present.
The v0 pass still skips dynamic circuits with classical control or reset
because those require a richer measurement/layout semantics model.

On the 30-circuit level-1 routed B1 suite:

| Metric | Before | After | Reduction |
|---|---:|---:|---:|
| Operation count | 7443 | 6000 | 19.39% |
| Two-qubit gate count | 3881 | 2438 | 37.18% |
| Logical depth | 4923 | 3725 | 24.33% |
| Hardware-weighted exposure | 28.95372 | 19.50068 | 32.65% |
| Idle-layer proxy | 82213 | 62337 | 24.18% |

Proof and output checks:

- Rewritten circuits: 30.
- Skipped circuits: 0.
- Virtual SWAPs removed: 481.
- CX gates removed: 1,443.
- Local Aer cross-check, original B1 routed vs virtual-SWAP output: 30 pass /
  0 fail.
- End-to-end Aer cross-check, source logical vs virtual-SWAP output: 30 pass /
  0 fail.
- Independent proof-log replay: 481 / 481 events consumed, 0 output
  mismatches, 0 replay errors.

Interpretation: this is the strongest B1 post-routing signal so far. It shows
that the level-1 routed benefit erasure is not inevitable: a layout-aware
compiler can remove route-induced SWAPs by carrying a virtual permutation
instead of paying three CX gates. The replay report now independently checks
that each wire-permutation certificate reconstructs the generated QASM. The
remaining work is to support dynamic-circuit semantics with classical
control/reset and integrate this strategy during routing rather than after
Qiskit has already emitted a route.

## Synthetic Heavy-Hex Noise Proxy

B1 now has a documented synthetic noise-proxy report for the level-1 routed
suite:

- Runner: `../tools/b1_synthetic_noise_proxy.py`
- Report: `B1_synthetic_noise_proxy_report.md`
- Machine-readable report: `B1_synthetic_noise_proxy_report.json`
- Profile: `heavy_hex_like_sparse` from `../benchmarks/hardware_profiles.json`

The proxy maps hardware-weighted exposure to a relative success proxy using
`exp(-exposure)`. It is intentionally a relative comparison tool, not a live
backend calibration.

Aggregate comparisons:

| Comparison | Exposure reduction | Success proxy ratio | 2Q reduction |
|---|---:|---:|---:|
| source level-1 routed vs B1 level-1 routed | 0.00% | 1.00x | 0.00% |
| B1 level-1 routed vs virtual-SWAP | 32.65% | 12746.86x | 37.18% |
| source level-1 routed vs virtual-SWAP | 32.65% | 12748.39x | 37.18% |

Interpretation: the level-1 Qiskit routed comparison still shows that normal
routing erases nearly all B1 benefit. The virtual-SWAP result changes the
post-routing cost model: under the fixed synthetic heavy-hex-like profile, it
substantially improves exposure and the relative success proxy. This does not
close the calibrated-device baseline gate, but it gives the next native-basis
routing optimizer a concrete noise-aware target.

## Next Algorithmic Step

Deepen the first compression baseline:

1. Parse each circuit into a minimal IR.
2. Move beyond adjacent-only rewrites:
   - commute diagonal gates when it reduces depth without changing controls;
   - generalize `cx-rz-cx -> rzz` to repeated fixed-point passes;
   - resynthesize 2-4 qubit windows against a target hardware cost model;
   - decompose multi-qubit gates only when the target basis requires it.
3. Add external exact-checkable circuits, especially MQT Bench or additional
   QASMBench families.
4. Extend the routing diagnostic into a verifier that handles measurement and
   classical-register semantics, then add a calibrated heavy-hex transpiler
   baseline.
5. Re-run `b1_qasm_metrics.py` before and after rewrites across all profiles.
6. Add exact or statistical equivalence checks for larger imported benchmark
   circuits that exceed the statevector cutoff.
7. Compose local semantic checks into a circuit-level certificate format that
   can be independently verified without rerunning the optimizer.

## Research Hypothesis to Test First

Even simple local rewrites, if made hardware-aware and combined with routing
pressure estimates, should show measurable reductions in the
hardware-weighted exposure metric on arithmetic, phase-estimation, and
Hamiltonian-simulation circuits.
