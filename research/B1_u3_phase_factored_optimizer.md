# B1 U3 Phase-Factored Optimizer Diagnostic v0.1

Last updated: 2026-06-15

Status: **u3_phase_factored_positive_diagnostic_not_final_claim**

## Summary

- Input directory: `/Users/avalok/work/FurturePlan/results/b1_control_rz_commute_optimizer`
- Factorized directory: `/Users/avalok/work/FurturePlan/results/b1_u3_phase_factored_intermediate`
- Output directory: `/Users/avalok/work/FurturePlan/results/b1_u3_phase_factored_optimizer`
- U3 factorization events: 1641
- RZ components emitted: 2219
- RY components emitted: 1641
- Zero components removed: 1063
- RZ commute certificate events: 3242
- Removed RZ gates after factoring: 313
- CNOT-control commutations after factoring: 540
- Logical T-count proxy reduction: 1.036371x
- Logical T-depth proxy reduction: 1.027732x
- Non-Clifford rotation-count reduction: 1.036371x

## Aggregate Metrics

| metric | before | after | reduction |
|---|---:|---:|---:|
| operation_count | 5556 | 7462 | -34.3053% |
| single_qubit_gate_count | 2948 | 4854 | -64.6540% |
| two_qubit_gate_count | 2438 | 2438 | 0.0000% |
| logical_depth | 3624 | 4777 | -31.8157% |
| hardware_weighted_error_exposure | 19.3973 | 20.3879 | -5.1071% |
| idle_layer_proxy | 60862 | 80863 | -32.8629% |

## T-Resource Proxy

| metric | before | after | reduction |
|---|---:|---:|---:|
| logical_t_count_proxy | 54140 | 52240 | 1.036371x |
| logical_t_depth_proxy | 12600 | 12260 | 1.027732x |
| non_clifford_rotation_count | 2707 | 2612 | 1.036371x |
| unknown_rotation_count | 270 | 296 | 0.912162x |
| operation_count_scanned | 5386 | 7292 | 0.738618x |

## Top Circuit Changes

| circuit | T-count proxy delta | T-depth proxy delta | non-Clifford delta |
|---|---:|---:|---:|
| qasmbench_interaction_exact/basis_trotter_n4.qasm | 960 | 220 | 48 |
| qasmbench_interaction_exact/ising_n10.qasm | 340 | 0 | 17 |
| qasmbench_small/hhl_n7.qasm | 320 | 40 | 16 |
| qasmbench_small/basis_change_n3.qasm | 180 | 80 | 9 |
| b1_exact_extension/05_qft_phase_ladder_n5.qasm | 60 | 0 | 3 |
| qasmbench_medium_exact/gcm_h6.qasm | 40 | 0 | 2 |
| b1_exact_extension/01_trotter_ladder_n6.qasm | 0 | 0 | 0 |
| b1_exact_extension/02_ring_interaction_n8.qasm | 0 | 0 | 0 |
| b1_exact_extension/03_qec_syndrome_phase_n7.qasm | 0 | 0 | 0 |
| b1_exact_extension/04_arithmetic_phase_n6.qasm | 0 | 0 | 0 |
| b1_exact_extension/06_long_range_echo_n10.qasm | 0 | 0 | 0 |
| b1_exact_extension/07_commuting_disjoint_windows_n8.qasm | 0 | 0 | 0 |

## Aer Cross-Check

- Pair count: 30
- Passed/failed: 30 / 0
- Max TVD: 0.0
- Max threshold: 0.20077072080689917

## Claim Boundary

- U3 factorization is exact only up to global phase, which is irrelevant for measurement distributions.
- This pass exposes U3 Z phases and reuses the narrow control-RZ commute rule; it is not a complete phase-polynomial optimizer.
- Operation count may increase because U3 gates become native rotation components; the relevant diagnostic target is logical T-resource pressure.
- Any B7 improvement remains a logical T-factory proxy until checked against a full fault-tolerant synthesis/layout ledger.
