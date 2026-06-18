# B1 Targeted Control-RZ Commute Optimizer v0.1

Last updated: 2026-06-15

Status: **control_rz_commute_positive_diagnostic_not_final_claim**

## Summary

- Input directory: `/Users/avalok/work/FurturePlan/results/b1_native_t_resource_optimizer`
- Output directory: `/Users/avalok/work/FurturePlan/results/b1_control_rz_commute_optimizer`
- Rewritten circuits: 30
- Circuits changed: 16
- Absorbed RZ gates: 1687
- Certificate events: 1307
- Merged or moved groups: 183
- Removed RZ gates: 380
- CNOT-control commutations: 1172
- Zero-output groups: 0
- Logical T-count proxy reduction: 1.119320x
- Logical T-depth proxy reduction: 1.069841x

## Aggregate Metrics

| metric | before | after | reduction |
|---|---:|---:|---:|
| operation_count | 5936 | 5556 | 6.4016% |
| single_qubit_gate_count | 3328 | 2948 | 11.4183% |
| two_qubit_gate_count | 2438 | 2438 | 0.0000% |
| logical_depth | 3719 | 3624 | 2.5545% |
| hardware_weighted_error_exposure | 19.4923 | 19.3973 | 0.4874% |
| idle_layer_proxy | 62287 | 60862 | 2.2878% |

## T-Resource Proxy

| metric | before | after | reduction |
|---|---:|---:|---:|
| logical_t_count_proxy | 60600 | 54140 | 1.119320x |
| logical_t_depth_proxy | 13480 | 12600 | 1.069841x |
| non_clifford_rotation_count | 3030 | 2707 | 1.119320x |
| operation_count_scanned | 5766 | 5386 | 1.070553x |

## Top Circuit Changes

| circuit | T-count proxy delta | T-depth proxy delta | non-Clifford delta |
|---|---:|---:|---:|
| qasmbench_medium_exact/gcm_h6.qasm | 3460 | 700 | 173 |
| qasmbench_small/hhl_n7.qasm | 1220 | 100 | 61 |
| qasmbench_medium_exact/qf21_n15.qasm | 720 | 20 | 36 |
| qasmbench_medium_exact/sat_n11.qasm | 640 | 40 | 32 |
| qasmbench_interaction_exact/ising_n10.qasm | 160 | 20 | 8 |
| b1_exact_extension/08_chemistry_ansatz_n8.qasm | 80 | 0 | 4 |
| b1_exact_extension/05_qft_phase_ladder_n5.qasm | 60 | 0 | 3 |
| b1_exact_extension/04_arithmetic_phase_n6.qasm | 40 | 0 | 2 |
| qasmbench_medium_exact/multiply_n13.qasm | 40 | 0 | 2 |
| qasmbench_medium_exact/seca_n11.qasm | 40 | 0 | 2 |
| b1_exact_extension/01_trotter_ladder_n6.qasm | 0 | 0 | 0 |
| b1_exact_extension/02_ring_interaction_n8.qasm | 0 | 0 | 0 |

## Aer Cross-Check

- Pair count: 30
- Passed/failed: 30 / 0
- Max TVD: 0.0
- Max threshold: 0.20077072080689917

## Claim Boundary

- Only RZ gates are accumulated; arbitrary U3 rotations are not resynthesized.
- RZ gates commute only across CNOTs where their qubit is the control; target-side RZ gates are flushed.
- This is a factory-boundary diagnostic, not a complete phase-polynomial optimizer.
- Any B7 claim must be based on the propagated factory schedule, not only local T-count reduction.
