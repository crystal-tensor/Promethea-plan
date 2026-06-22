# B1/B7 cone_01 OpenQASM 3 Local Semantic Replay Gate

Status: `cone01_openqasm3_local_semantic_replay_passed_default_input_only`

This artifact consumes T-B1-004bw and checks whether the project-local OpenQASM 3 parser can construct a replayable circuit for the forward-facing artifact.

## Summary

- Source QASM: `results/b1_native_t_resource_optimizer/qasmbench_medium_exact/gcm_h6.qasm`
- OpenQASM 3 candidate: `results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`
- Project-local parser passed / errors: `True` / `0`
- Operation counts: `{'U': 487, 'rz': 601, 'cx': 789, 'measure': 1}`
- Qubits / bits / statements / operation rows: `19` / `1` / `1884` / `1878`
- Statevector dimension: `524288`
- Source / OpenQASM 3 CNOT count / delta: `795` / `789` / `6`
- State fidelity / infidelity: `0.9999999999999551` / `4.4853010194856324e-14`
- Max global-phase-aligned amplitude delta: `1.3908205762322243e-13`
- Max probability / measured marginal delta: `5.551115123125783e-16` / `5.551115123125783e-16`
- Local semantic replay passed: `True`
- Accepted local replay / Qiskit loader / symbolic equivalence artifacts: `1` / `0` / `0`
- Accepted replay certificate / local-U3 pricing / occurrence / proxy-T reduction: `0` / `0` / `0` / `0`
- Validation errors: `0`

## Claim Boundary

The project-local OpenQASM 3 parser can construct and replay the candidate against the optimized source on the benchmark default-input statevector.

Unsupported claims:

- This is not a Qiskit OpenQASM 3 loader parse.
- This is not symbolic unitary equivalence or arbitrary-input equivalence.
- This does not price or eliminate local-U3 burden.
- This does not create B7 occurrence, proxy-T, or space-time-volume credit.

## Next Required Gate

Move from default-input local replay to reproducible loader replay, symbolic or broader-input semantic evidence, and separate local-U3 pricing before any B7 resource credit is accepted.
