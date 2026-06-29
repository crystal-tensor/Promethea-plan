# B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Evidence Seal Gate

- Method: `b1_b7_cone01_openqasm3_qiskit_loader_evidence_seal_gate_v0`
- Status: `cone01_openqasm3_qiskit_loader_evidence_seal_passed_without_b7_credit`
- Model status: `qiskit_loader_openqasm3_patch_lift_evidence_chain_hash_sealed_without_b7_credit`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- OpenQASM 3 candidate: `results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`
- Source artifacts sealed: 7
- Evidence seal SHA-256: `d06c1fdae3ad7cad1971cdcdcea1f890d3931924a7e70affc25fdf89737e09a8`
- Qiskit / qiskit-qasm3-import / openqasm3: 2.4.1 / 0.6.0 / 1.0.1
- Qubits / clbits / depth: 19 / 1 / 1483
- Operation counts: {'cx': 789, 'measure': 1, 'rz': 601, 'u': 487}
- Multi / phase / global input cases: 8 / 8 / 21
- Failed replay cases total: 0
- Qiskit-loader global-phase / finite-span / patch-lift support passed: True / True / True
- Certified span / full space: 6 / 524288
- Span spectral / max basis L2 / max probability / max cross-Gram delta: 2.7889440543898627e-13 / 2.534056605707275e-13 / 7.771561172376096e-16 / 4.403624367368429e-14
- Selected lines / dropped overlap lines: [268, 1381] / [1378]
- Stream mismatch / instruction count: 0 / 1878
- Accepted Qiskit-loader evidence seal count: 1
- Accepted occurrence removal / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## Claim Boundary

The OpenQASM 3 Qiskit-loader evidence chain is hash-sealed across the candidate QASM file and the replay, multi-input, phase, global-phase, finite-span, and composable patch-lift support artifacts.

Unsupported claims:
- This is a reproducibility and drift-detection seal, not a new equivalence theorem.
- This does not extend coverage beyond the 6-dimensional certified span.
- This does not price the remaining line-1381 local-U3 burden.
- This does not recover the dropped line-1378 overlap delta.
- This does not improve the B7 resource ledger.

## Source Artifact Hashes

- `results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`: `258bda18c5b77aa58dd36463357b3431a406ce33205994dfdc875aa6373d16a3`
- `results/B1_B7_cone01_openqasm3_qiskit_loader_replay_gate_v0.json`: `cba9eb6b2a2fc0aefb6a89f8a991c5717bedb70fdbc2f7ac20afcd864643f58d`
- `results/B1_B7_cone01_openqasm3_qiskit_loader_multi_input_replay_gate_v0.json`: `7aae71dfca4363440a4bf97c8d5cd7c2cfb83c598fb64c1b695ddea29fa73608`
- `results/B1_B7_cone01_openqasm3_qiskit_loader_phase_consistent_replay_gate_v0.json`: `4d4909779aad3dfe7691209d5ffbac19bbfbc3d00750893aaeade1b045c1a025`
- `results/B1_B7_cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_gate_v0.json`: `4d828f176c4898d872ea74cc6d5dbd04a1d3a70230c55165e445f01dcef5dc79`
- `results/B1_B7_cone01_openqasm3_qiskit_loader_linear_span_replay_certificate_gate_v0.json`: `52abacb53f0cf3b235ea81856bda9d76917e24f44041858d9533f8ecdccac45b`
- `results/B1_B7_cone01_openqasm3_qiskit_loader_composable_patch_lift_gate_v0.json`: `217ae0ea4cad8d2a4a2ba65734bae104eebad9cc2d5e6fe7308cbc3bd40bc54c`
