# B3 Hamiltonian Pauli Mapper Comparison v0.1

Last updated: 2026-06-17

Status: **hamiltonian_pauli_mapper_circuits_vs_fci_denominator_not_advantage_claim**

## Summary

- Source FCI method: b10_t1_d5_b3_fci_reference_table_v0
- Instances: 4
- QASM files: 4
- Max qubits: 20
- Max mapped Pauli terms: 2951
- Max measurement packet terms: 16
- Max variance upper bound: 8.471619e+03
- Max total measurement shot floor: 30504129929
- FCI denominator beaten count: 0
- State-preparation cost included: True
- Observable-variance estimate included: True
- Quantum advantage claimed: False
- Reaction-dynamics solution claimed: False
- Validation errors: 0

## Rows

| molecule | qubits | Pauli terms | packet terms | HF X gates | variance upper | total shot floor | FCI derivative | QASM | beats FCI? |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| h2_bond_stretch | 4 | 15 | 15 | 2 | 9.693655e-01 | 14540490 | 1.072984e-02 | `results/b3_hamiltonian_pauli_mapper_comparison/circuits/h2_bond_stretch_hamiltonian_pauli_measurements.qasm` | False |
| lih_bond_stretch | 12 | 631 | 16 | 4 | 2.955410e+01 | 18648635838 | 1.620684e-02 | `results/b3_hamiltonian_pauli_mapper_comparison/circuits/lih_bond_stretch_hamiltonian_pauli_measurements.qasm` | False |
| h2o_symmetric_oh_stretch | 14 | 1086 | 16 | 10 | 3.424726e+03 | 22424525124 | -2.575706e-01 | `results/b3_hamiltonian_pauli_mapper_comparison/circuits/h2o_symmetric_oh_stretch_hamiltonian_pauli_measurements.qasm` | False |
| n2_bond_stretch | 20 | 2951 | 16 | 14 | 8.471619e+03 | 30504129929 | -5.725567e-01 | `results/b3_hamiltonian_pauli_mapper_comparison/circuits/n2_bond_stretch_hamiltonian_pauli_measurements.qasm` | False |

## Claim Boundary

- Supported: four chemistry-mapper Jordan-Wigner Hamiltonian Pauli-term measurement packets.
- Supported: Hartree-Fock state-preparation X-gate counts and conservative Pauli-estimator variance shot floors.
- Not supported: quantum advantage, FCI denominator win, basis-set completeness, chemistry accuracy, or complete reaction dynamics.

## Next Steps

- Replace Hartree-Fock bitstring preparation with an ansatz or adiabatic/state-preparation cost model.
- Run sampled Pauli-estimator simulation to replace the variance upper bound with observed confidence intervals.
- Scale the denominator to selected-CI or larger active spaces.
- Only promote if a mapped circuit beats the declared denominator at fixed observable error after preparation and measurement costs.
