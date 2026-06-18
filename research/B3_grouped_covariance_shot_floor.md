# B3 Grouped Covariance Shot-Floor Boundary v0.1

Last updated: 2026-06-17

Status: **grouped_covariance_shot_floor_boundary_not_advantage_claim**

## Summary

- Source mapper method: b3_larger_basis_hamiltonian_mapper_v0
- Source QWC method: b3_larger_basis_qwc_grouping_v0
- Instances: 4
- Covariance model: exact_HF_product_state_covariance_inside_each_QWC_group
- QWC grouping included: True
- Grouped covariance included: True
- Max total qubits: 38
- Max Pauli terms after cutoff: 77858
- Max QWC group count: 19644
- Max previous independent-term shot floor: 6464114739
- Max grouped-covariance shot floor: 1283900037
- Grouped-covariance reduction range: 4.907x-5.583x
- Max nonzero covariance pairs: 73474
- Max ansatz two-qubit executions at grouped-covariance target: 190017205476
- Selected-CI larger-basis denominator beaten count: 0
- Quantum advantage claimed: False
- Reaction-dynamics solution claimed: False
- Validation errors: 0

## Rows

| molecule | basis | QWC groups | previous shots | grouped-cov shots | reduction | covariance pairs | ansatz 2q executions | beats denominator? |
|---|---|---:|---:|---:|---:|---:|---:|---|
| h2_bond_stretch | cc-pvdz | 886 | 354329749 | 63465167 | 5.583x | 2176 | 4823352692 | False |
| lih_bond_stretch | cc-pvdz | 19644 | 6464114739 | 1283900037 | 5.035x | 73474 | 190017205476 | False |
| h2o_symmetric_oh_stretch | 3-21g | 3129 | 1154398231 | 215312646 | 5.361x | 13510 | 21531264600 | False |
| n2_bond_stretch | 3-21g | 9475 | 6079672376 | 1238924735 | 4.907x | 33747 | 173449462900 | False |

## Interpretation

This report turns the previous QWC measurement-setting reduction into an explicit grouped-observable variance calculation. The covariance model is still the Hartree-Fock product-state model used by the existing B3 Pauli estimators; it is useful for bounding measurement economics, but it is not a correlated chemical state-preparation result.

## Claim Boundary

- Supported: grouped-observable covariance propagation for the four larger-basis B3 QWC Hamiltonian covers under a Hartree-Fock product-state measurement model.
- Supported: group-level Neyman shot-floor estimates using N=(sum_g sqrt(Var_g)/epsilon)^2.
- Not supported: correlated chemical-state covariance, UCC/ADAPT/adiabatic preparation, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.

## Next Steps

- Replace the Hartree-Fock covariance model with sampled covariance from UCC, ADAPT-VQE, or adiabatic state-preparation states.
- Propagate grouped observable covariance through three-point reaction-coordinate derivatives rather than per-coordinate Hamiltonian energy only.
- Retest against stricter selected-CI, DMRG, or tensor-network denominators at fixed observable error.
