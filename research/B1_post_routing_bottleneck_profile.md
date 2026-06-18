# B1 Post-Routing Bottleneck Profile v0.1

Last updated: 2026-06-13

Status: **post_routing_bottleneck_profile_diagnostic_not_calibrated_noise_claim**

## Level Summary

| Qiskit level | Aer all pass | Operation | 2Q gates | Depth | Exposure | Idle proxy |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | True | 16.95% | 0.00% | 19.44% | 2.93% | 20.55% |
| 1 | True | 0.03% | 0.00% | 0.00% | 0.00% | -0.00% |

## Level 0 Exposure Contributors

| Circuit | Source | Optimized | Improvement | Reduction |
|---|---:|---:|---:|---:|
| `qasmbench_medium_exact/gcm_h6.qasm` | 11.6332 | 10.6875 | 0.94574 | 8.13% |
| `qasmbench_small/hhl_n7.qasm` | 3.47782 | 3.31714 | 0.16068 | 4.62% |
| `qasmbench_interaction_exact/basis_trotter_n4.qasm` | 4.41268 | 4.32324 | 0.08944 | 2.03% |
| `qasmbench_interaction_exact/ising_n10.qasm` | 1.57456 | 1.53554 | 0.03902 | 2.48% |
| `qasmbench_medium_exact/sat_n11.qasm` | 6.1301 | 6.12242 | 0.00768 | 0.13% |
| `qasmbench_small/basis_test_n4.qasm` | 0.54996 | 0.54498 | 0.00498 | 0.91% |
| `b1_exact_extension/09_bv_phase_oracle_n9.qasm` | 0.55794 | 0.55512 | 0.00282 | 0.51% |
| `qasmbench_small/bell_n4.qasm` | 0.2164 | 0.21364 | 0.00276 | 1.28% |
| `qasmbench_small/grover_n2.qasm` | 0.065 | 0.06248 | 0.00252 | 3.88% |
| `qasmbench_medium_exact/seca_n11.qasm` | 1.70188 | 1.70064 | 0.00124 | 0.07% |

## Level 0 Depth Contributors

| Circuit | Source | Optimized | Improvement | Reduction |
|---|---:|---:|---:|---:|
| `qasmbench_medium_exact/gcm_h6.qasm` | 3255 | 2113 | 1142 | 35.08% |
| `qasmbench_small/hhl_n7.qasm` | 727 | 532 | 195 | 26.82% |
| `qasmbench_interaction_exact/basis_trotter_n4.qasm` | 917 | 814 | 103 | 11.23% |
| `qasmbench_interaction_exact/ising_n10.qasm` | 131 | 99 | 32 | 24.43% |
| `qasmbench_medium_exact/sat_n11.qasm` | 912 | 903 | 9 | 0.99% |
| `qasmbench_small/basis_test_n4.qasm` | 87 | 81 | 6 | 6.90% |
| `b1_exact_extension/09_bv_phase_oracle_n9.qasm` | 61 | 58 | 3 | 4.92% |
| `qasmbench_small/bell_n4.qasm` | 25 | 22 | 3 | 12.00% |
| `qasmbench_small/grover_n2.qasm` | 14 | 11 | 3 | 21.43% |
| `b1_exact_extension/07_commuting_disjoint_windows_n8.qasm` | 19 | 18 | 1 | 5.26% |

## Level 1 Exposure Contributors

| Circuit | Source | Optimized | Improvement | Reduction |
|---|---:|---:|---:|---:|
| `qasmbench_small/bell_n4.qasm` | 0.09778 | 0.09766 | 0.00012 | 0.12% |

## Level 1 Exposure Regressions

| Circuit | Source | Optimized | Improvement | Reduction |
|---|---:|---:|---:|---:|
| n/a | n/a | n/a | n/a | n/a |

## Level 1 Benefit Erasure

| Circuit | L0 exposure | L1 exposure | L0 depth | L1 depth | L1 2Q delta |
|---|---:|---:|---:|---:|---:|
| `qasmbench_medium_exact/gcm_h6.qasm` | 8.13% | 0.00% | 35.08% | 0.00% | 0 |
| `qasmbench_small/hhl_n7.qasm` | 4.62% | 0.00% | 26.82% | 0.00% | 0 |
| `qasmbench_small/grover_n2.qasm` | 3.88% | 0.00% | 21.43% | 0.00% | 0 |
| `qasmbench_interaction_exact/ising_n10.qasm` | 2.48% | 0.00% | 24.43% | 0.00% | 0 |
| `qasmbench_interaction_exact/basis_trotter_n4.qasm` | 2.03% | 0.00% | 11.23% | 0.00% | 0 |
| `qasmbench_small/bell_n4.qasm` | 1.28% | 0.12% | 12.00% | 0.00% | 0 |
| `qasmbench_small/basis_test_n4.qasm` | 0.91% | 0.00% | 6.90% | 0.00% | 0 |
| `b1_exact_extension/09_bv_phase_oracle_n9.qasm` | 0.51% | 0.00% | 4.92% | 0.00% | 0 |
| `b1_exact_extension/07_commuting_disjoint_windows_n8.qasm` | 0.33% | 0.00% | 5.26% | 0.00% | 0 |
| `qasmbench_small/adder_n4.qasm` | 0.30% | 0.00% | 3.12% | 0.00% | 0 |

## Level 1 Two-Qubit Bottlenecks

| Circuit | Source 2Q | Optimized 2Q | Delta | Reduction | Optimized exposure |
|---|---:|---:|---:|---:|---:|
| `qasmbench_medium_exact/gcm_h6.qasm` | 1269 | 1269 | 0 | 0.00% | 9.0847 |
| `qasmbench_interaction_exact/basis_trotter_n4.qasm` | 582 | 582 | 0 | 0.00% | 4.09204 |
| `qasmbench_medium_exact/sat_n11.qasm` | 581 | 581 | 0 | 0.00% | 3.99522 |
| `qasmbench_small/hhl_n7.qasm` | 334 | 334 | 0 | 0.00% | 2.40718 |
| `qasmbench_medium_exact/qf21_n15.qasm` | 292 | 292 | 0 | 0.00% | 2.04572 |
| `qasmbench_medium_exact/seca_n11.qasm` | 159 | 159 | 0 | 0.00% | 1.0663 |
| `qasmbench_medium_exact/multiply_n13.qasm` | 91 | 91 | 0 | 0.00% | 0.64288 |
| `qasmbench_interaction_exact/ising_n10.qasm` | 90 | 90 | 0 | 0.00% | 0.69302 |
| `qasmbench_small/error_correctiond3_n5.qasm` | 67 | 67 | 0 | 0.00% | 0.5264 |
| `b1_exact_extension/10_qaoa_double_triangle_n6.qasm` | 60 | 60 | 0 | 0.00% | 0.46444 |

## Interpretation

- Level 0 preserves B1 operation, depth, idle-layer, and small exposure benefits after heavy-hex routing.
- Level 1 nearly erases the current routed benefit, so the present B1 rewrites are not robust to stronger routing optimization.
- Post-routing two-qubit count remains the dominant unsolved bottleneck; the next optimizer should operate on routing-aware 2-4 qubit windows rather than isolated 1Q cleanup.
