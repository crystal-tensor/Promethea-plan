# B3 Quantum Observable Circuit vs FCI Denominator v0.1

Last updated: 2026-06-17

Status: **quantum_observable_circuit_vs_fci_denominator_proxy_not_advantage_claim**

## Summary

- Source denominator method: b10_t1_d5_b3_reaction_observable_table_v0
- Source FCI method: b10_t1_d5_b3_fci_reference_table_v0
- Instances: 4
- QASM files: 4
- Max qubits: 21
- Max controlled-phase gates: 441
- Max measurement shot floor: 1000000
- FCI denominator beaten count: 0
- Quantum advantage claimed: False
- Reaction-dynamics solution claimed: False
- Validation errors: 0

## Circuit Rows

| molecule | qubits | controlled phases | shot floor | FCI derivative | target error | QASM | beats FCI? |
|---|---:|---:|---:|---:|---:|---|---|
| h2_bond_stretch | 5 | 1 | 1000000 | 1.072984e-02 | 1.000000e-03 | `results/b3_quantum_observable_fci_comparison/circuits/h2_bond_stretch_observable_estimation.qasm` | False |
| lih_bond_stretch | 13 | 64 | 1000000 | 1.620684e-02 | 1.000000e-03 | `results/b3_quantum_observable_fci_comparison/circuits/lih_bond_stretch_observable_estimation.qasm` | False |
| h2o_symmetric_oh_stretch | 15 | 100 | 6030 | -2.575706e-01 | 1.287853e-02 | `results/b3_quantum_observable_fci_comparison/circuits/h2o_symmetric_oh_stretch_observable_estimation.qasm` | False |
| n2_bond_stretch | 21 | 441 | 1221 | -5.725567e-01 | 2.862783e-02 | `results/b3_quantum_observable_fci_comparison/circuits/n2_bond_stretch_observable_estimation.qasm` | False |

## Claim Boundary

- Supported: four OpenQASM observable-estimation proxy circuits aligned to B3 reaction-coordinate FCI derivative denominators.
- Supported: explicit measurement-shot and controlled-phase budget floors for the proxy circuits.
- Not supported: quantum advantage, chemistry accuracy, complete reaction dynamics, basis-set completeness, or beating the FCI denominator.

## Next Steps

- Replace phase-kickback proxies with Hamiltonian Pauli-term circuits from a chemistry mapper.
- Add state-preparation cost and observable variance estimates from sampled simulation.
- Scale the denominator beyond STO-3G FCI to selected-CI or larger active spaces.
- Only promote if a concrete circuit beats the declared denominator at fixed observable error after all preparation/readout costs.
