# B3 Larger-Basis Hamiltonian Mapper Boundary v0.1

Last updated: 2026-06-17

Status: **larger_basis_hamiltonian_mapper_boundary_not_advantage_claim**

## Summary

- Source selected-CI boundary method: b3_selected_ci_grouped_pauli_boundary_v0
- Instances: 4
- Larger-basis quantum mapper included: True
- Same basis as selected-CI denominator: True
- Max total qubits: 38
- Max Pauli terms after cutoff: 77858
- Max conservative same-basis bucket count: 77116
- Conservative bucket reduction range: 1.000x-1.000x
- Max Neyman target shot floor: 6464114739
- Max ansatz two-qubit executions at Neyman target: 956688981372
- Selected-CI larger-basis denominator beaten count: 0
- Quantum advantage claimed: False
- Reaction-dynamics solution claimed: False
- Validation errors: 0

## Rows

| molecule | basis | qubits | Pauli terms | random terms | buckets | bucket reduction | Neyman shots | ansatz 2q executions | beats denominator? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| h2_bond_stretch | cc-pvdz | 20 | 2951 | 2740 | 2740 | 1.000x | 354329749 | 26929060924 | False |
| lih_bond_stretch | cc-pvdz | 38 | 77858 | 77116 | 77116 | 1.000x | 6464114739 | 956688981372 | False |
| h2o_symmetric_oh_stretch | 3-21g | 26 | 12732 | 12380 | 12380 | 1.000x | 1154398231 | 115439823100 | False |
| n2_bond_stretch | 3-21g | 36 | 34655 | 33988 | 33988 | 1.000x | 6079672376 | 851154132640 | False |

## Claim Boundary

- Supported: Jordan-Wigner qubit Hamiltonians for the same larger bases used by the selected-CI denominator rows.
- Supported: conservative same-basis measurement bucket counts, Neyman shot floors, and a two-layer ansatz state-preparation surcharge.
- Not supported: optimal Pauli grouping, chemical ansatz preparation, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.

## Next Steps

- Replace conservative same-basis buckets with an actual QWC or commuting-cover optimizer on the larger-basis Pauli sets.
- Replace the generic two-layer ansatz surcharge with UCC, ADAPT-VQE, or adiabatic preparation costs.
- Retest against stricter selected-CI, DMRG, or tensor-network denominators at fixed observable error.
