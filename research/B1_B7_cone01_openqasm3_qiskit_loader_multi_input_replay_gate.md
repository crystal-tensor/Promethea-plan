# B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Multi-Input Replay Gate

- Method: `b1_b7_cone01_openqasm3_qiskit_loader_multi_input_replay_gate_v0`
- Status: `cone01_openqasm3_qiskit_loader_multi_input_replay_passed_sampled_inputs`
- Model status: `qiskit_loader_openqasm3_matches_source_sampled_inputs_without_b7_credit`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- Supported claim: The Qiskit-loaded OpenQASM 3 candidate matches the optimized source on the same deterministic 8-input suite used by the project-local multi-input replay gate after final measurements are removed.

## Inputs

- Qiskit-loader default-input gate: `results/B1_B7_cone01_openqasm3_qiskit_loader_replay_gate_v0.json`
- Project-local multi-input gate: `results/B1_B7_cone01_openqasm3_multi_input_replay_gate_v0.json`
- OpenQASM 3 candidate: `results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`

## Loader Evidence

- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Qubits / clbits / depth: 19 / 1 / 1483
- Operation counts: {'cx': 789, 'rz': 601, 'u': 487, 'measure': 1}

## Multi-Input Replay Evidence

- Input cases: 8 (6 computational-basis, 2 product-state)
- Product-state seeds: [17, 29]
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max amplitude / probability delta: 1.392888964263601e-13 / 1.8214596497756474e-15
- Failed cases: []
- Accepted Qiskit-loader parse / replay / multi-input replay artifacts: 1 / 1 / 1
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False

## Claim Boundary

- This is sampled multi-input statevector evidence, not arbitrary-input equivalence.
- This is not a symbolic exact full-circuit unitary proof.
- This does not price or eliminate the remaining line-1381 off-grid local-U3 parameters.
- This does not recover the dropped line-1378 overlap delta.
- This does not improve the B7 resource ledger.

## Validation

- Qiskit-loader multi-input replay passed: True
- Validation errors: 0
