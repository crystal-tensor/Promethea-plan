# B1 Native T-Resource Optimizer Diagnostic v0.1

Last updated: 2026-06-15

Status: **native_t_resource_optimizer_positive_diagnostic_not_final_claim**

## Summary

- Input directory: `/Users/avalok/work/FurturePlan/results/b1_post_virtual_swap_1q_resynth`
- Output directory: `/Users/avalok/work/FurturePlan/results/b1_native_t_resource_optimizer`
- Rewritten circuits: 30
- Circuits changed: 26
- Canonicalization events: 1691
- Identity events removed: 4
- Native `rz` rewrite events: 1687
- Removed 1Q gates: 4
- Logical T-count proxy reduction: 1.000990x
- Logical T-depth proxy reduction: 1.000000x
- Non-Clifford rotation-count reduction: 1.000990x

## Aggregate Metrics

| metric | before | after | reduction |
|---|---:|---:|---:|
| operation_count | 5940 | 5936 | 0.0673% |
| single_qubit_gate_count | 3332 | 3328 | 0.1200% |
| two_qubit_gate_count | 2438 | 2438 | 0.0000% |
| logical_depth | 3719 | 3719 | 0.0000% |
| hardware_weighted_error_exposure | 19.4925 | 19.4923 | 0.0012% |
| idle_layer_proxy | 62283 | 62287 | -0.0064% |

## T-Resource Proxy

| metric | before | after | reduction |
|---|---:|---:|---:|
| logical_t_count_proxy | 60660 | 60600 | 1.000990x |
| logical_t_depth_proxy | 13480 | 13480 | 1.000000x |
| non_clifford_rotation_count | 3033 | 3030 | 1.000990x |
| unknown_rotation_count | 294 | 293 | 1.003413x |
| operation_count_scanned | 5770 | 5766 | 1.000694x |

## Top Circuit Changes

| circuit | T-count proxy delta | T-depth proxy delta | non-Clifford delta | unknown-rotation delta |
|---|---:|---:|---:|---:|
| qasmbench_small/bell_n4.qasm | 40 | 0 | 2 | 0 |
| qasmbench_small/basis_change_n3.qasm | 20 | 0 | 1 | 0 |
| b1_exact_extension/01_trotter_ladder_n6.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/02_ring_interaction_n8.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/03_qec_syndrome_phase_n7.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/04_arithmetic_phase_n6.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/05_qft_phase_ladder_n5.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/06_long_range_echo_n10.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/07_commuting_disjoint_windows_n8.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/08_chemistry_ansatz_n8.qasm | 0 | 0 | 0 | 0 |

## Aer Cross-Check

- Pair count: 30
- Passed/failed: 30 / 0
- Max TVD: 0.0
- Max threshold: 0.20077072080689917

## Claim Boundary

- This pass canonicalizes only theta=0 u3 gates into native Z-phase form.
- It is a narrow diagnostic for false T-resource proxy costs, not a complete non-Clifford optimizer.
- The rewrite treats global phase as irrelevant to measurement semantics.
- A positive proxy reduction must still be propagated through B7 factory schedules before it can support a system claim.
