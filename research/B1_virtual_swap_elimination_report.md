# B1 Virtual SWAP Elimination Diagnostic v0.1

Last updated: 2026-06-13

Status: **virtual_swap_elimination_diagnostic_not_layout_final_claim**

## Summary

- Circuits: 30
- Rewritten circuits: 30
- Skipped circuits: 0
- Virtual SWAPs removed: 481
- Removed CX gates: 1443
- Local Aer cross-check pass/fail: 30 / 0
- End-to-end Aer cross-check pass/fail: 30 / 0

## Metric Deltas

| Metric | Before | After | Delta | Reduction |
|---|---:|---:|---:|---:|
| operation_count | 7443 | 6000 | -1443 | 19.39% |
| two_qubit_gate_count | 3881 | 2438 | -1443 | 37.18% |
| logical_depth | 4923 | 3725 | -1198 | 24.33% |
| hardware_weighted_error_exposure | 28.9537 | 19.5007 | -9.45304 | 32.65% |
| idle_layer_proxy | 82213 | 62337 | -19876 | 24.18% |

## Top Circuits By Removed Virtual SWAPs

| Circuit | Status | Virtual SWAPs removed | Removed CX |
|---|---|---:|---:|
| `qasmbench_medium_exact/gcm_h6.qasm` | rewritten | 158 | 474 |
| `qasmbench_medium_exact/sat_n11.qasm` | rewritten | 96 | 288 |
| `qasmbench_interaction_exact/basis_trotter_n4.qasm` | rewritten | 60 | 180 |
| `qasmbench_medium_exact/qf21_n15.qasm` | rewritten | 54 | 162 |
| `qasmbench_small/hhl_n7.qasm` | rewritten | 37 | 111 |
| `qasmbench_medium_exact/seca_n11.qasm` | rewritten_with_measurement_tracking | 19 | 57 |
| `qasmbench_medium_exact/multiply_n13.qasm` | rewritten | 15 | 45 |
| `b1_exact_extension/10_qaoa_double_triangle_n6.qasm` | rewritten | 8 | 24 |
| `qasmbench_small/basis_test_n4.qasm` | rewritten | 6 | 18 |
| `qasmbench_small/error_correctiond3_n5.qasm` | rewritten | 6 | 18 |

## Limits

- The pass removes routed SWAP macros by tracking a virtual wire permutation and remapping later operations.
- Measurement operands are remapped through the same wire permutation when no classical control or reset is present.
- Circuits with classical control or reset are skipped in v0 because dynamic-layout semantics need a richer model.
- This is a post-routing transformation diagnostic, not a final calibrated backend layout claim.
