# B3 Cross-Molecule UCC/ADAPT Pressure and Demotion Boundary

- Status: `cross_molecule_ucc_adapt_pressure_demote_boundary_not_advantage_claim`
- Method: `b3_cross_molecule_ucc_adapt_pressure_v0`
- Source derivative boundary: `b3_chemical_state_prep_derivative_boundary_v0`
- Source grouped covariance: `b3_grouped_covariance_shot_floor_v0`
- Source compiled pilot: `b3_compiled_ucc_adapt_covariance_pilot_v0`
- Molecules: 4
- Total sampled groups: 35
- Pilot shots per group: 384
- Pilot basis cap: 12
- Pilot max terms per molecule: 96
- Mean/max relative variance error across molecules: 0.083282 / 0.502937
- Max optimizer-loop shots lower bound: 475043013690000
- Max optimizer-loop 2Q executions lower bound: 281225464104480000
- Demotion recommended: True
- Recommendation: `demote_to_negative_boundary_until_multi_parameter_state_prep_or_new_measurement_strategy`

## Rows

| Molecule | qubits | source QWC groups | subset terms | subset groups | sampled | mean err | max err | HF derivative floor | optimizer shots lower bound | optimizer 2Q lower bound | demote? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| h2_bond_stretch | 20 | 886 | 96 | 9 | 2 | 0.042557 | 0.058692 | 634651670000 | 23482111790000 | 7138561984160000 | yes |
| lih_bond_stretch | 38 | 19644 | 96 | 16 | 1 | 0.033127 | 0.033127 | 12839000370000 | 475043013690000 | 281225464104480000 | yes |
| h2o_symmetric_oh_stretch | 26 | 3129 | 96 | 15 | 24 | 0.226191 | 0.502937 | 2153126460000 | 79665679020000 | 31866271608000000 | yes |
| n2_bond_stretch | 36 | 9475 | 96 | 9 | 8 | 0.031253 | 0.085672 | 12389247350000 | 458402151950000 | 256705205092000000 | yes |

## Claim Boundary

- Supported: bounded high-coefficient sampled covariance pressure test on H2, LiH, H2O, and N2 using one-parameter compiled UCC-double / ADAPT-seed states.
- Supported: optimizer-loop lower-bound accounting using the source HF grouped-covariance derivative floors.
- Supported: a B3 demotion recommendation under the current one-parameter ansatz and QWC-only measurement strategy.
- Not supported: full cross-molecule QWC cover construction under the compiled state, full compiled covariance, converged UCCSD/ADAPT/VQE chemistry, all-group sampled covariance, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.

## Next Steps

- Demote B3 to a negative-boundary track unless a real multi-parameter UCCSD/ADAPT ansatz or stronger measurement strategy changes the denominator comparison.
- If continuing B3, require full covariance for at least one multi-parameter UCCSD/ADAPT state and a selected-CI/DMRG/tensor denominator comparison.
- Prioritize B5/B10 or B4/B8 if B3 remains optimizer-loop dominated after the next multi-parameter attempt.
