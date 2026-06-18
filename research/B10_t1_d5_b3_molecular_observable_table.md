# B10-T1 D5 B3 Molecular Observable Denominator Proxy v0.5

Last updated: 2026-06-13

Status: **b3_d5_molecular_observable_denominator_proxy_not_reaction_solution**

## Summary

- Source target: B10-T1 / linear_systems_data_loading_negative_boundary
- Dependency benchmark: B3
- Builds on: b10_t1_d5_observable_denominator_table_v0
- Source result: results/B3_pyscf_resource_estimate_v0.json
- Instances: 4
- Molecules: ['h2_calibration', 'lih_calibration', 'h2o_calibration', 'n2_calibration']
- Max matrix dimension: 160
- Max matrix nnz: 834
- Max relative residual: 9.152e-09
- Median CG iterations: 6.5
- Validation errors: 0
- Explicitly not a BQP separation: True

## Interpretation

- This table extends B10-T1 D5 from B5 Hubbard response to the B3 molecular calibration set.
- It uses the existing PySCF resource-proxy output and builds a deterministic molecular response denominator proxy.
- The table is a claim-boundary artifact for observable-first chemistry claims, not a reaction-dynamics solution.
- The next serious step is replacing this proxy matrix with a Hamiltonian-derived observable along a reaction coordinate.

## Instance Table

| molecule | spin orbitals | matrix dim | nnz | observable fraction | iterations | residual | observable response | explicit-I/O floor | observable/full T proxy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| h2_calibration | 4 | 64 | 322 | 0.20 | 9 | 9.152e-09 | 4.990530e-01 | 395 | 0.164 |
| lih_calibration | 12 | 96 | 498 | 0.20 | 8 | 1.131e-09 | 3.282195e-01 | 937 | 0.160 |
| h2o_calibration | 14 | 112 | 582 | 0.20 | 5 | 1.490e-09 | 1.213639e-01 | 1911 | 0.160 |
| n2_calibration | 20 | 160 | 834 | 0.20 | 5 | 6.408e-10 | 1.057971e-01 | 3903 | 0.160 |

## Claim Boundary

- now_supported: B10-T1 D5 now has a B3 molecular observable denominator proxy tied to the existing PySCF calibration resource estimates.
- still_not_supported: This is not a reaction-coordinate simulation, not a quantum implementation, not a chemistry accuracy claim, and not a BQP/classical separation.
- next_proof_pressure: Replace the proxy response matrix with an OpenFermion/PySCF Hamiltonian-derived observable along a reaction coordinate, then compare against coupled-cluster or selected-CI references.
