# B10-T1 Hamiltonian-Derived B3 Reaction Observable Denominator Table v0.6

Last updated: 2026-06-13

Status: **hamiltonian_derived_b3_reaction_observable_denominator_not_reaction_solution**

## Summary

- Source target: B10-T1 / linear_systems_data_loading_negative_boundary
- Dependency benchmark: B3
- Builds on: b10_t1_d5_b3_molecular_observable_table_v0
- Instances: 4
- Molecules: ['h2_bond_stretch', 'lih_bond_stretch', 'h2o_symmetric_oh_stretch', 'n2_bond_stretch']
- Max response dimension: 21
- Max response nnz: 441
- Max relative residual: 3.154e-13
- Median CG iterations: 3.0
- Validation errors: 0
- Explicitly not a BQP separation: True

## Interpretation

- This table replaces the previous B3 proxy response matrix with Hamiltonian-derived finite-difference sources.
- Each row uses a reaction-coordinate perturbation, central RHF molecular orbitals, and a singles response denominator.
- It remains a denominator and claim-boundary artifact, not a reaction-dynamics solution or quantum-speedup result.

## Instance Table

| molecule | coordinate | response dim | nnz | source norm | response proxy | iterations | residual | explicit-I/O floor |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| h2_bond_stretch | H-H bond length | 1 | 1 | 1.512e-14 | 1.749712e-28 | 1 | 0.000e+00 | 75 |
| lih_bond_stretch | Li-H bond length | 8 | 64 | 7.967e-01 | 2.608022e-01 | 4 | 2.924e-16 | 511 |
| h2o_symmetric_oh_stretch | symmetric O-H stretch scale | 10 | 100 | 9.239e+00 | 2.638630e+01 | 4 | 3.154e-13 | 1439 |
| n2_bond_stretch | N-N bond length | 21 | 441 | 2.128e+01 | 9.897487e+01 | 2 | 9.242e-15 | 3535 |

## Claim Boundary

- now_supported: B10-T1 D5 now has Hamiltonian-derived B3 reaction-coordinate denominator rows using PySCF finite-difference one-electron Hamiltonians and singles response equations.
- still_not_supported: This is not a full reaction-dynamics simulation, not a quantum implementation, not a chemistry accuracy claim, and not a BQP/classical separation.
- next_proof_pressure: Add correlated classical references such as MP2/CCSD or selected-CI along the coordinate, then compare a concrete quantum observable-estimation circuit against this denominator.
