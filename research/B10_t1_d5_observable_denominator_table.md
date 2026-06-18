# B10-T1 D5 Observable Denominator Table v0.4

Last updated: 2026-06-13

Status: **d5_observable_denominator_table_instantiated_not_quantum_speedup_claim**

## Summary

- Source target: B10-T1 / linear_systems_data_loading_negative_boundary
- Dependency benchmark: B5
- Builds on: b10_t1_numerical_denominator_table_v0
- Instances: 9
- Sites: [4, 6, 8]
- U/t values: [2.0, 4.0, 8.0]
- Max Hilbert dimension: 4900
- Max Hamiltonian nnz: 44100
- Max relative residual: 9.788e-09
- Median CG iterations: 16.0
- Validation errors: 0
- Explicitly not a BQP separation: True

## Interpretation

- This table maps B10-T1 D5 to a concrete B5 observable task.
- The observable is a local density-response proxy in a half-filled 1D Hubbard model.
- The denominator solves `(H - E0 + eta I) x = (n_i - <n_i>) |psi0>` with classical CG.
- Only one scalar observable is read out, so the table separates observable-output accounting from full-vector readout.
- It is a classical denominator and claim-boundary artifact, not a quantum-speedup result.

## Instance Table

| sites | U/t | dim | nnz | density mean | susceptibility proxy | iterations | residual | explicit-I/O floor | matvec-equivalent ops |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 2.0 | 36 | 180 | 1.000000 | 0.083606 | 9 | 1.225e-15 | 273 | 1620 |
| 4 | 4.0 | 36 | 180 | 1.000000 | 0.036226 | 9 | 3.097e-14 | 273 | 1620 |
| 4 | 8.0 | 36 | 180 | 1.000000 | 0.008378 | 8 | 4.996e-10 | 273 | 1440 |
| 6 | 2.0 | 400 | 2800 | 1.000000 | 0.095785 | 18 | 6.486e-09 | 3259 | 50400 |
| 6 | 4.0 | 400 | 2800 | 1.000000 | 0.039369 | 17 | 8.364e-09 | 3259 | 47600 |
| 6 | 8.0 | 400 | 2800 | 1.000000 | 0.008467 | 15 | 6.051e-09 | 3259 | 42000 |
| 8 | 2.0 | 4900 | 44100 | 1.000000 | 0.097805 | 23 | 4.489e-09 | 49061 | 1014300 |
| 8 | 4.0 | 4900 | 44100 | 1.000000 | 0.040469 | 21 | 4.599e-09 | 49061 | 926100 |
| 8 | 8.0 | 4900 | 44100 | 1.000000 | 0.008581 | 16 | 9.788e-09 | 49061 | 705600 |

## Claim Boundary

- now_supported: D5 has a concrete B5 Hubbard density-response denominator with explicit Hamiltonian input, observable output, residual target, and CG iteration accounting.
- still_not_supported: This is not a quantum implementation, not a BQP/classical separation, and not evidence of a B5 accuracy-per-resource improvement.
- next_proof_pressure: Compare a candidate quantum impurity/response subroutine against this D5 table, or extend D5 from 1D Hubbard response to B3 molecular reaction observables.
