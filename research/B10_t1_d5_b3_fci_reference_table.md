# B10-T1 FCI-Strength B3 Reaction-Coordinate References v0.8

Last updated: 2026-06-15

Status: **fci_b3_reaction_references_instantiated_not_quantum_advantage_claim**

## Summary

- Source target: B10-T1 / linear_systems_data_loading_negative_boundary
- Dependency benchmark: B3
- Builds on: b10_t1_d5_b3_correlated_reference_table_v0
- Instances: 4
- Methods: ['RHF', 'MP2', 'CCSD', 'FCI']
- Max |FCI derivative shift vs RHF|: 2.980e-01
- Max |FCI derivative shift vs CCSD|: 1.625e-02
- Max |CCSD derivative shift vs RHF|: 2.818e-01
- Validation errors: 0
- Explicitly not a BQP separation: True

## Interpretation

- This table upgrades the B3 reaction-coordinate denominator to include FCI in the same small-basis settings.
- It records RHF, MP2, CCSD, and FCI finite-difference energy derivatives on the same coordinates used by the Hamiltonian-derived D5 table.
- It remains a classical reference and claim-boundary artifact, not a quantum advantage result.

## Instance Table

| molecule | coordinate | RHF dE/dq | MP2 dE/dq | CCSD dE/dq | FCI dE/dq | FCI-RHF shift | FCI-CCSD shift |
|---|---|---:|---:|---:|---:|---:|---:|
| h2_bond_stretch | H-H bond length | 5.454623e-02 | 3.116863e-02 | 1.072984e-02 | 1.072984e-02 | -4.381640e-02 | -1.302625e-10 |
| lih_bond_stretch | Li-H bond length | 3.260775e-02 | 2.467242e-02 | 1.621940e-02 | 1.620684e-02 | -1.640092e-02 | -1.255936e-05 |
| h2o_symmetric_oh_stretch | symmetric O-H stretch scale | -1.356070e-01 | -2.141956e-01 | -2.571038e-01 | -2.575706e-01 | -1.219635e-01 | -4.667114e-04 |
| n2_bond_stretch | N-N bond length | -2.745440e-01 | -6.346611e-01 | -5.563035e-01 | -5.725567e-01 | -2.980127e-01 | -1.625318e-02 |

## Claim Boundary

- now_supported: B3 D5 reaction-coordinate denominator rows now have RHF, MP2, CCSD, and FCI finite-difference reference derivatives in STO-3G.
- still_not_supported: This is not a quantum implementation, not a full reaction-dynamics solution, not a basis-set-complete chemistry claim, and not a BQP/classical separation.
- next_proof_pressure: Compare a concrete quantum observable-estimation circuit against the FCI reference denominator, then scale to an active-space or selected-CI setting.

