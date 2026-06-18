# B1 Post-Virtual-SWAP 1Q Resynthesis Diagnostic v0.1

Last updated: 2026-06-13

Status: **post_virtual_swap_1q_resynthesis_t_resource_positive_diagnostic**

## Summary

- Circuits rewritten: 30
- Resynthesized 1Q runs: 60
- Removed 1Q gates: 60
- Proof/certificate events: 60
- Operation-count reduction: 1.00%
- Single-qubit gate-count reduction: 1.77%
- Logical-depth reduction: 0.16%
- Exposure reduction: 0.04%
- Logical T-count proxy reduction: 1.018x
- Logical T-depth proxy reduction: 1.015x
- Non-Clifford rotation-count reduction: 1.018x

## T-Resource Proxy

| metric | before | after | reduction |
|---|---:|---:|---:|
| logical T-count proxy | 61740 | 60660 | 1.018x |
| logical T-depth proxy | 13680 | 13480 | 1.015x |
| non-Clifford rotations | 3087 | 3033 | 1.018x |

## Top Circuit Changes

| circuit | removed 1Q gates | operation reduction | depth reduction | exposure reduction |
|---|---:|---:|---:|---:|
| qasmbench_interaction_exact/basis_trotter_n4.qasm | 54 | 54 | 0 | 0.00324 |
| qasmbench_medium_exact/qf21_n15.qasm | 6 | 6 | 6 | 0.00492 |
| b1_exact_extension/01_trotter_ladder_n6.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/02_ring_interaction_n8.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/03_qec_syndrome_phase_n7.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/04_arithmetic_phase_n6.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/05_qft_phase_ladder_n5.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/06_long_range_echo_n10.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/07_commuting_disjoint_windows_n8.qasm | 0 | 0 | 0 | 0 |
| b1_exact_extension/08_chemistry_ansatz_n8.qasm | 0 | 0 | 0 | 0 |

## Verification

- Aer cross-check pairs: 30
- Aer failed pairs: 0
- Max TVD: 0.0
- Max threshold: 0.20077072080689917

## Limits

- This is a post-virtual-SWAP local 1Q fusion diagnostic, not a final T-optimized compiler.
- Arbitrary non-Clifford rotations use the same fixed T synthesis cost proxy as the B7 logical T-factory schedule.
- A positive gate-count reduction does not by itself imply a T-factory resource reduction.
- The result is intended to decide whether B1 currently supplies a T-resource lever for B7 or only a data-path/routing lever.
