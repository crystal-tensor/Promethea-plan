# B3 Sampled Pauli Estimator Confidence Intervals v0.1

Last updated: 2026-06-17

Status: **sampled_pauli_estimator_confidence_intervals_not_advantage_claim**

## Summary

- Source mapper method: b3_hamiltonian_pauli_mapper_comparison_v0
- Source FCI method: b10_t1_d5_b3_fci_reference_table_v0
- Instances: 4
- Pilot shots per random Pauli term: 2048
- Max random Pauli terms: 2740
- Max pilot total shots: 5611520
- Max target shot floor (Neyman): 6570468
- Max previous upper-bound shot floor: 30504129929
- Shot reduction range vs upper bound: 442.417x-34544.057x
- All pilot CIs contain exact HF energy: True
- FCI denominator beaten count: 0
- Quantum advantage claimed: False
- Reaction-dynamics solution claimed: False
- Validation errors: 0

## Rows

| molecule | random terms | pilot shots | pilot abs error | CI half-width | target shots | previous floor | reduction | beats FCI? |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| h2_bond_stretch | 4 | 8192 | 7.524194e-04 | 5.159402e-03 | 32866 | 14540490 | 442.417x | False |
| lih_bond_stretch | 552 | 1130496 | 1.478526e-04 | 1.058085e-02 | 6570468 | 18648635838 | 2838.251x | False |
| h2o_symmetric_oh_stretch | 980 | 2007040 | 5.950440e-02 | 7.176279e-02 | 1619027 | 22424525124 | 13850.618x | False |
| n2_bond_stretch | 2740 | 5611520 | 3.552440e-02 | 7.296979e-02 | 883050 | 30504129929 | 34544.057x | False |

## Claim Boundary

- Supported: reproducible pilot Pauli-estimator confidence intervals for four B3 Hamiltonian-mapped rows.
- Supported: Neyman-style target shot floors replacing the previous coefficient-squared upper-bound floor for Hartree-Fock bitstring measurements.
- Not supported: selected-CI scaling, larger active-space denominators, quantum advantage, chemistry accuracy, or complete reaction dynamics.

## Next Steps

- Replace Hartree-Fock bitstring expectations with ansatz or adiabatic state-preparation samples.
- Attach selected-CI or larger-active-space denominators to the same coordinates.
- Group commuting Pauli terms instead of measuring each random Pauli independently.
- Only promote if preparation, grouped measurement, and strong denominator costs are all beaten at fixed observable error.
