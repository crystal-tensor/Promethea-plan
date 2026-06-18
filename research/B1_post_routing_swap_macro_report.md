# B1 Post-Routing SWAP Macro Compression Diagnostic v0.1

Last updated: 2026-06-13

Status: **post_routing_swap_macro_diagnostic_not_native_basis_claim**

## Summary

- Circuits: 30
- SWAP macros identified: 481
- Removed CX gates: 1443
- Inserted SWAP macros: 481
- Local Aer cross-check pass/fail: 30 / 0
- End-to-end Aer cross-check pass/fail: 30 / 0

## Metric Deltas

| Metric | Before | After | Delta | Reduction |
|---|---:|---:|---:|---:|
| operation_count | 7443 | 6481 | -962 | 12.92% |
| two_qubit_gate_count | 3881 | 2919 | -962 | 24.79% |
| logical_depth | 4923 | 4164 | -759 | 15.42% |
| hardware_weighted_error_exposure | 28.9537 | 22.6818 | -6.27188 | 21.66% |
| idle_layer_proxy | 82213 | 69716 | -12497 | 15.20% |

## Top Circuits By SWAP Macros

| Circuit | SWAP macros | Removed CX | 2Q macro reduction |
|---|---:|---:|---:|
| `qasmbench_medium_exact/gcm_h6.qasm` | 158 | 474 | 316 |
| `qasmbench_medium_exact/sat_n11.qasm` | 96 | 288 | 192 |
| `qasmbench_interaction_exact/basis_trotter_n4.qasm` | 60 | 180 | 120 |
| `qasmbench_medium_exact/qf21_n15.qasm` | 54 | 162 | 108 |
| `qasmbench_small/hhl_n7.qasm` | 37 | 111 | 74 |
| `qasmbench_medium_exact/seca_n11.qasm` | 19 | 57 | 38 |
| `qasmbench_medium_exact/multiply_n13.qasm` | 15 | 45 | 30 |
| `b1_exact_extension/10_qaoa_double_triangle_n6.qasm` | 8 | 24 | 16 |
| `qasmbench_small/basis_test_n4.qasm` | 6 | 18 | 12 |
| `qasmbench_small/error_correctiond3_n5.qasm` | 6 | 18 | 12 |

## Limits

- The pass rewrites a routed CX-CX-CX SWAP implementation into an OpenQASM swap macro.
- This is a routing-aware IR/macro compression diagnostic, not a calibrated native-basis hardware claim.
- If the target backend decomposes swap back into CX gates, the physical two-qubit-gate reduction does not hold without a native swap or a lower-cost swap implementation.
