# B10-T1 Numerical Denominator Table v0.3

Last updated: 2026-06-13

Status: **numerical_denominator_table_instantiated_not_quantum_speedup_claim**

## Summary

- Source target: B10-T1 / linear_systems_data_loading_negative_boundary
- Builds on: b10_t1_source_backed_boundaries_v0
- Denominator families: 2
- Total instances: 16
- CG instances: 12
- LSQR instances: 4
- Max relative residual: 3.886e-06
- Validation errors: 0
- Explicitly not a BQP separation: True

## Interpretation

- This is the first runnable denominator table for B10-T1, not a quantum-speedup benchmark.
- D1 covers explicit sparse SPD full-vector output with conjugate gradient.
- D2 covers explicit general sparse least-squares style instances with LSQR.
- The explicit-I/O floor records sparse input entries plus full-vector output bits; any HHL-style end-to-end claim must charge those terms before comparing subroutine complexity.

## Family Summary

| Family | Instances | n values | Median iterations | Max residual | Max explicit-I/O floor | Max matvec-equivalent ops |
|---|---:|---|---:|---:|---:|---:|
| D1_explicit_spd_full_solution_cg | 12 | 64,128,256,512 | 96.0 | 9.991e-09 | 29182 | 762398 |
| D2_explicit_general_sparse_least_squares | 4 | 64,128,256,512 | 20.0 | 3.886e-06 | 29418 | 34120 |

## Instance Table

| Solver | n | shape | nnz | condition estimate | iterations | residual | explicit-I/O floor | matvec-equivalent ops |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| cg | 64 | 64x64 | 190 | 4.004e+01 | 58 | 7.279e-09 | 3646 | 11020 |
| cg | 64 | 64x64 | 190 | 3.249e+02 | 64 | 4.243e-15 | 3646 | 12160 |
| cg | 64 | 64x64 | 190 | 1.199e+03 | 64 | 2.878e-15 | 3646 | 12160 |
| cg | 128 | 128x128 | 382 | 4.075e+01 | 59 | 9.475e-09 | 7294 | 22538 |
| cg | 128 | 128x128 | 382 | 3.785e+02 | 128 | 1.113e-14 | 7294 | 48896 |
| cg | 128 | 128x128 | 382 | 2.511e+03 | 128 | 8.792e-15 | 7294 | 48896 |
| cg | 256 | 256x256 | 766 | 4.094e+01 | 59 | 9.381e-09 | 14590 | 45194 |
| cg | 256 | 256x256 | 766 | 3.951e+02 | 176 | 9.885e-09 | 14590 | 134816 |
| cg | 256 | 256x256 | 766 | 3.481e+03 | 256 | 2.224e-14 | 14590 | 196096 |
| cg | 512 | 512x512 | 1534 | 4.098e+01 | 59 | 7.674e-09 | 29182 | 90506 |
| cg | 512 | 512x512 | 1534 | 3.995e+02 | 180 | 9.937e-09 | 29182 | 276120 |
| cg | 512 | 512x512 | 1534 | 3.856e+03 | 497 | 9.991e-09 | 29182 | 762398 |
| lsqr | 64 | 72x64 | 213 | 2.112e+01 | 20 | 2.769e-06 | 3677 | 4260 |
| lsqr | 128 | 144x128 | 425 | 2.120e+01 | 20 | 3.886e-06 | 7353 | 8500 |
| lsqr | 256 | 288x256 | 853 | 2.121e+01 | 20 | 2.795e-06 | 14709 | 17060 |
| lsqr | 512 | 576x512 | 1706 | 2.119e+01 | 20 | 2.879e-06 | 29418 | 34120 |

## Claim Boundary

- now_supported: D1 and D2 denominator regimes have runnable sparse-CG/LSQR measurements with explicit input and full-output accounting.
- still_not_supported: This table does not benchmark a quantum implementation, does not prove BQP/classical separation, and does not settle dequantized sampling-access regimes.
- next_proof_pressure: Map one B3/B5 observable to a D5 linear-response denominator, or write the D4 sampling-access theorem note.
