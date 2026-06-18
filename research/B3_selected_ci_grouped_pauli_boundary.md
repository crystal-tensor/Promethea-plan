# B3 Selected-CI Larger-Basis Denominator and Grouped Pauli Boundary v0.1

Last updated: 2026-06-17

Status: **selected_ci_larger_basis_grouped_pauli_boundary_not_advantage_claim**

## Summary

- Source sampled Pauli method: b3_sampled_pauli_estimator_confidence_v0
- Source mapper method: b3_hamiltonian_pauli_mapper_comparison_v0
- Instances: 4
- Selected-CI/larger-basis rows: 4
- All selected-CI points converged: True
- Max selected-CI spatial orbitals: 19
- Max selected-CI determinant product: 400
- Max selected-CI three-point determinant product: 1200
- QWC packet reduction range: 1.000x-4.170x
- Max QWC group count: 809
- Max ansatz two-qubit gate executions at target: 289100592
- Selected-CI/larger-basis denominator beaten count: 0
- Quantum advantage claimed: False
- Reaction-dynamics solution claimed: False
- Validation errors: 0

## Rows

| molecule | selected-CI basis | orbitals | selected det product | derivative shift vs STO-3G FCI | QWC groups | packet reduction | target shots | ansatz 2q executions | beats denominator? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| h2_bond_stretch | cc-pvdz | 10 | 100 | -3.802053e-02 | 4 | 1.000x | 32866 | 394392 | False |
| lih_bond_stretch | cc-pvdz | 19 | 64 | -2.184123e-02 | 143 | 3.860x | 6570468 | 289100592 | False |
| h2o_symmetric_oh_stretch | 3-21g | 13 | 256 | 3.083903e-01 | 235 | 4.170x | 1619027 | 84189404 | False |
| n2_bond_stretch | 3-21g | 18 | 400 | 5.273152e-01 | 809 | 3.387x | 883050 | 67111800 | False |

## Claim Boundary

- Supported: selected-CI finite-difference denominator rows in larger orbital bases for the same four B3 reaction coordinates.
- Supported: QWC grouped measurement-setting counts and an explicit two-layer ansatz state-preparation surcharge on the sampled Pauli side.
- Not supported: a large-basis quantum Hamiltonian mapper, selected-CI chemical benchmark quality, quantum advantage, or complete reaction dynamics.

## Next Steps

- Map the same larger-basis Hamiltonians to qubits instead of comparing STO-3G Pauli estimators to larger-basis selected-CI denominators.
- Replace the hardware-efficient ansatz surcharge with a chemically motivated UCC/ADAPT/adiabatic preparation cost.
- Use a stricter selected-CI schedule or DMRG denominator for H2O and N2 once determinant spaces become larger than this v0 stress table.
