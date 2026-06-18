# B3 Chemical State-Preparation Derivative Boundary v0.1

Last updated: 2026-06-17

Status: **chemical_state_prep_derivative_boundary_not_advantage_claim**

## Summary

- Source grouped covariance method: b3_grouped_covariance_shot_floor_v0
- Source selected-CI method: b3_selected_ci_grouped_pauli_boundary_v0
- Source mapper method: b3_larger_basis_hamiltonian_mapper_v0
- Instances: 4
- Derivative error propagation included: True
- Sampled chemical-state covariance included: False
- Chemical state-prep envelope included: True
- Chemical state-prep models: UCCSD, ADAPT-VQE-envelope, adiabatic-envelope
- Max source grouped-covariance shot floor: 1283900037
- Max three-point derivative total shot floor: 12839000370000
- Derivative shot-floor inflation range: 10000.000x-10000.000x
- Max UCCSD 2Q gates per preparation: 1493030
- Max ADAPT 2Q gates per preparation: 11248
- Max adiabatic 2Q gates per preparation: 28120
- Max UCCSD 2Q executions at derivative target: 18497517970970500000
- Selected-CI larger-basis denominator beaten count: 0
- Quantum advantage claimed: False
- Reaction-dynamics solution claimed: False
- Validation errors: 0

## Rows

| molecule | basis | center shots | derivative shots | inflation | UCCSD prep 2Q | ADAPT prep 2Q | adiabatic prep 2Q | UCCSD execs | beats denominator? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| h2_bond_stretch | cc-pvdz | 63465167 | 634651670000 | 10000.000x | 7182 | 3040 | 7600 | 4558068293940000 | False |
| lih_bond_stretch | cc-pvdz | 1283900037 | 12839000370000 | 10000.000x | 259148 | 11248 | 28120 | 3327201267884760000 | False |
| h2o_symmetric_oh_stretch | 3-21g | 215312646 | 2153126460000 | 10000.000x | 278000 | 5200 | 13000 | 598569155880000000 | False |
| n2_bond_stretch | 3-21g | 1238924735 | 12389247350000 | 10000.000x | 1493030 | 10080 | 25200 | 18497517970970500000 | False |

## Interpretation

This artifact moves B3 from per-coordinate energy measurement economics to derivative-level finite-difference accounting. Because the derivative uses two endpoint energy estimates, the shot budget inflates by roughly 1/delta^2. Chemical state-preparation costs are now explicit for UCCSD, ADAPT, and adiabatic envelopes, but sampled correlated-state covariance is still an open task.

## Claim Boundary

- Supported: propagation of grouped-covariance energy shot floors through three-point finite-difference derivative error.
- Supported: explicit UCCSD, ADAPT-VQE-envelope, and adiabatic-envelope two-qubit state-preparation cost models.
- Not supported: sampled correlated chemical-state covariance, converged UCC/ADAPT energies, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.

## Next Steps

- Generate actual sampled covariance from a small UCC or ADAPT state instead of using the HF covariance source.
- Replace the envelope gate counts with compiled ansatz circuits and optimizer-loop shot accounting.
- Retest against stricter selected-CI, DMRG, or tensor-network denominators at derivative-level observable error.
