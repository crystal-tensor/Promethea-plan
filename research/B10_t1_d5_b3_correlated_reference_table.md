# B10-T1 Correlated B3 Reaction-Coordinate References v0.7

Last updated: 2026-06-13

Status: **correlated_b3_reaction_references_instantiated_not_quantum_advantage_claim**

## Summary

- Source target: B10-T1 / linear_systems_data_loading_negative_boundary
- Dependency benchmark: B3
- Builds on: b10_t1_d5_b3_reaction_observable_table_v0
- Instances: 4
- Methods: ['RHF', 'MP2', 'CCSD']
- Max |CCSD derivative shift vs RHF|: 2.818e-01
- Max |MP2 derivative shift vs RHF|: 3.601e-01
- Max |CCSD derivative shift vs MP2|: 7.836e-02
- Validation errors: 0
- Explicitly not a BQP separation: True

## Interpretation

- This table adds correlated classical references to the B3 reaction-coordinate denominator.
- It records RHF, MP2, and CCSD finite-difference energy derivatives on the same coordinates used by the Hamiltonian-derived D5 table.
- It remains a classical reference and claim-boundary artifact, not a quantum advantage result.

## Instance Table

| molecule | coordinate | RHF dE/dq | MP2 dE/dq | CCSD dE/dq | CCSD-RHF shift | CCSD-MP2 shift |
|---|---|---:|---:|---:|---:|---:|
| h2_bond_stretch | H-H bond length | 5.454623e-02 | 3.116863e-02 | 1.072984e-02 | -4.381640e-02 | -2.043879e-02 |
| lih_bond_stretch | Li-H bond length | 3.260775e-02 | 2.467242e-02 | 1.621940e-02 | -1.638836e-02 | -8.453021e-03 |
| h2o_symmetric_oh_stretch | symmetric O-H stretch scale | -1.356070e-01 | -2.141956e-01 | -2.571038e-01 | -1.214968e-01 | -4.290825e-02 |
| n2_bond_stretch | N-N bond length | -2.745440e-01 | -6.346611e-01 | -5.563035e-01 | -2.817595e-01 | 7.835764e-02 |

## Claim Boundary

- now_supported: B3 D5 reaction-coordinate denominator rows now have RHF, MP2, and CCSD finite-difference reference derivatives.
- still_not_supported: This is not a quantum implementation, not a full reaction-dynamics solution, not a basis-set-complete chemistry claim, and not a BQP/classical separation.
- next_proof_pressure: Use these references to define an accuracy-per-resource comparison for a concrete quantum observable-estimation circuit or selected-CI/FCI denominator.
