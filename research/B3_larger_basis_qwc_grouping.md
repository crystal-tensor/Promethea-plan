# B3 Larger-Basis QWC Grouping Boundary v0.1

Last updated: 2026-06-17

Status: **larger_basis_qwc_grouping_boundary_not_advantage_claim**

## Summary

- Source mapper method: b3_larger_basis_hamiltonian_mapper_v0
- Instances: 4
- QWC grouping included: True
- Algorithm: bitmask_first_fit_qwc_cover_weight_ascending
- Max total qubits: 38
- Max Pauli terms after cutoff: 77858
- Max previous bucket count: 77116
- Max QWC group count: 19644
- QWC reduction range: 3.093x-3.957x
- Max group size: 291
- Max Neyman target shot floor: 6464114739
- Shot floor reduced by grouping: False
- Max ansatz two-qubit executions at target: 956688981372
- Selected-CI larger-basis denominator beaten count: 0
- Quantum advantage claimed: False
- Reaction-dynamics solution claimed: False
- Validation errors: 0

## Rows

| molecule | basis | random terms | previous buckets | QWC groups | reduction | max group | Neyman shots | ansatz 2q executions | beats denominator? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| h2_bond_stretch | cc-pvdz | 2740 | 2740 | 886 | 3.093x | 58 | 354329749 | 26929060924 | False |
| lih_bond_stretch | cc-pvdz | 77116 | 77116 | 19644 | 3.926x | 291 | 6464114739 | 956688981372 | False |
| h2o_symmetric_oh_stretch | 3-21g | 12380 | 12380 | 3129 | 3.957x | 180 | 1154398231 | 115439823100 | False |
| n2_bond_stretch | 3-21g | 33988 | 33988 | 9475 | 3.587x | 197 | 6079672376 | 851154132640 | False |

## Claim Boundary

- Supported: actual qubit-wise commuting grouping covers for four larger-basis B3 Hamiltonians.
- Supported: measurement-setting reductions versus the previous same-basis bucket upper bound.
- Not supported: reduced shot floor from covariance propagation, chemical state preparation, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.

## Next Steps

- Propagate grouped-observable covariance to decide whether shot floors actually decrease.
- Replace the generic two-layer ansatz surcharge with UCC, ADAPT-VQE, or adiabatic preparation costs.
- Retest against stricter selected-CI, DMRG, or tensor-network denominators at fixed observable error.
