# B1 Synthetic Heavy-Hex Noise Proxy v0.1

Last updated: 2026-06-13

Status: **synthetic_noise_proxy_not_calibrated_device_claim**

## Noise Profile

- Profile: `heavy_hex_like_sparse`
- Description: Sparse superconducting-style profile with expensive two-qubit operations.
- Single-qubit error: 0.0001
- Two-qubit error: 0.006
- Measurement error: 0.012
- Idle error per layer: 4e-05

## Aggregate Comparisons

| Comparison | Exposure before | Exposure after | Reduction | Success proxy ratio | 2Q reduction |
|---|---:|---:|---:|---:|---:|
| source_level1_routed_vs_b1_level1_routed | 28.9538 | 28.9537 | 0.00% | 1.00012x | 0.00% |
| b1_level1_routed_vs_virtual_swap | 28.9537 | 19.5007 | 32.65% | 12746.9x | 37.18% |
| source_level1_routed_vs_virtual_swap | 28.9538 | 19.5007 | 32.65% | 12748.4x | 37.18% |

## Top Exposure Improvements

### source_level1_routed_vs_b1_level1_routed

| Circuit | Before | After | Delta | Reduction |
|---|---:|---:|---:|---:|
| `qasmbench_small/bell_n4.qasm` | 0.09778 | 0.09766 | -0.00012 | 0.12% |
| `b1_exact_extension/01_trotter_ladder_n6.qasm` | 0.2813 | 0.2813 | 0 | 0.00% |
| `b1_exact_extension/02_ring_interaction_n8.qasm` | 0.4052 | 0.4052 | 0 | 0.00% |
| `b1_exact_extension/03_qec_syndrome_phase_n7.qasm` | 0.15282 | 0.15282 | 0 | 0.00% |
| `b1_exact_extension/04_arithmetic_phase_n6.qasm` | 0.25372 | 0.25372 | 0 | 0.00% |

### b1_level1_routed_vs_virtual_swap

| Circuit | Before | After | Delta | Reduction |
|---|---:|---:|---:|---:|
| `qasmbench_medium_exact/gcm_h6.qasm` | 9.0847 | 5.91686 | -3.16784 | 34.87% |
| `qasmbench_medium_exact/sat_n11.qasm` | 3.99522 | 2.10406 | -1.89116 | 47.34% |
| `qasmbench_interaction_exact/basis_trotter_n4.qasm` | 4.09204 | 2.93524 | -1.1568 | 28.27% |
| `qasmbench_medium_exact/qf21_n15.qasm` | 2.04572 | 1.00004 | -1.04568 | 51.12% |
| `qasmbench_small/hhl_n7.qasm` | 2.40718 | 1.69458 | -0.7126 | 29.60% |

### source_level1_routed_vs_virtual_swap

| Circuit | Before | After | Delta | Reduction |
|---|---:|---:|---:|---:|
| `qasmbench_medium_exact/gcm_h6.qasm` | 9.0847 | 5.91686 | -3.16784 | 34.87% |
| `qasmbench_medium_exact/sat_n11.qasm` | 3.99522 | 2.10406 | -1.89116 | 47.34% |
| `qasmbench_interaction_exact/basis_trotter_n4.qasm` | 4.09204 | 2.93524 | -1.1568 | 28.27% |
| `qasmbench_medium_exact/qf21_n15.qasm` | 2.04572 | 1.00004 | -1.04568 | 51.12% |
| `qasmbench_small/hhl_n7.qasm` | 2.40718 | 1.69458 | -0.7126 | 29.60% |

## Limits

- This is a documented synthetic heavy-hex-like noise proxy using fixed gate, readout, and idle error rates.
- It is not calibrated from a live backend and does not close the true calibrated-device baseline gate.
- The success proxy is exp(-hardware_weighted_error_exposure), useful for relative comparison rather than absolute device prediction.
- Metric inputs are routed QASM metrics; no stochastic noisy simulation is performed here.
