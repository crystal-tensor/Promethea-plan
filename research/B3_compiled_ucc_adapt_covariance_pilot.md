# B3 Compiled UCC/ADAPT Covariance Pilot v0.1

Last updated: 2026-06-18

Status: **compiled_ucc_adapt_covariance_pilot_not_advantage_claim**

## Summary

- Source derivative method: b3_chemical_state_prep_derivative_boundary_v0
- Molecule: h2_bond_stretch
- Ansatz model: compiled_one_parameter_ucc_double_adapt_seed
- Compiled UCC/ADAPT covariance included: True
- Pilot sampled covariance included: True
- Optimizer-loop shot accounting included: True
- Converged VQE/ADAPT energy: False
- Pilot groups / max basis weight / shots per group: 48 / 12 / 512
- Pilot mean/max relative variance error: 0.007 / 0.083
- Compiled 2Q gates per preparation: 304
- Center grouped-covariance shot floor: 66955026
- Three-point derivative shot floor: 669550260000
- Optimizer evaluation multiplier: 37
- Optimizer-loop total shots: 24773359620000
- Optimizer-loop 2Q executions: 7531101324480000
- Selected-CI larger-basis denominator beaten count: 0
- Quantum advantage claimed: False
- Reaction-dynamics solution claimed: False
- Validation errors: 0

## Pilot Row

| molecule | basis | random terms | QWC groups | center shots | derivative shots | optimizer shots | prep 2Q | optimizer 2Q execs | beats denominator? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| h2_bond_stretch | cc-pvdz | 2808 | 887 | 66955026 | 669550260000 | 24773359620000 | 304 | 7531101324480000 | False |

## Sampled Group Preview

| group | size | basis weight | exact variance | sample variance | rel error |
|---:|---:|---:|---:|---:|---:|
| 274 | 2 | 11 | 1.222170e-03 | 1.245328e-03 | 0.019 |
| 249 | 2 | 11 | 1.020764e-03 | 1.064836e-03 | 0.043 |
| 250 | 2 | 11 | 1.020764e-03 | 1.018380e-03 | 0.002 |
| 259 | 2 | 11 | 1.020764e-03 | 9.912370e-04 | 0.029 |
| 248 | 2 | 11 | 1.020764e-03 | 1.105135e-03 | 0.083 |
| 257 | 2 | 11 | 1.020764e-03 | 1.084628e-03 | 0.063 |
| 627 | 1 | 12 | 9.389962e-04 | 9.376037e-04 | 0.001 |
| 283 | 1 | 8 | 7.721805e-04 | 7.735028e-04 | 0.002 |

## Claim Boundary

- Supported: one H2/cc-pVDZ compiled one-parameter UCC-double/ADAPT-seed covariance pilot.
- Supported: sampled covariance estimates for the top sampleable groups with basis weight <= 12, plus exact full-cover covariance and optimizer-loop shot accounting for that pilot state.
- Not supported: sampled covariance for every QWC group, converged UCC/ADAPT/VQE chemistry, sampled covariance for all B3 molecules, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.

## Next Steps

- Compile a real multi-parameter UCCSD or ADAPT circuit and repeat covariance sampling beyond the one-parameter seed.
- Extend the sampled covariance pilot from H2 to LiH/H2O/N2 or demote B3 if optimizer-loop costs remain prohibitive.
- Compare against stricter selected-CI, DMRG, or tensor-network denominators at derivative-level observable error.
