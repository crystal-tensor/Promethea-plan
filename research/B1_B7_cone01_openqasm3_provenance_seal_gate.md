# B1/B7 cone_01 OpenQASM 3 Provenance Seal Gate

- Method: `b1_b7_cone01_openqasm3_provenance_seal_gate_v0`
- Status: `cone01_openqasm3_provenance_seal_passed_without_b7_resource_credit`
- Model status: `openqasm3_patch_lift_artifacts_are_file_hash_sealed_without_b7_credit`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- QASM2 candidate: `results/B1_B7_cone01_qasm2_candidate_rewrite_gate/gcm_h6_line268_line1381_candidate.qasm`
- OpenQASM 3 artifact: `results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`

## Evidence

- Raw QASM2 / OpenQASM 3 line counts: 1884 / 1884
- Normalized stream match / instruction count: True / 1878
- Normalized stream SHA-256: `7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343`
- Provenance seal SHA-256: `159c9b1d99a607d463fe712a190b35460603712561a4ea8eb4033bf4de495902`
- Selected lines / dropped overlap lines: [268, 1381] / [1378]
- Max patch residual / entry error: 6.513210005207597e-13 / 4.525273102184799e-13
- OpenQASM 3 span spectral error: 2.7889440543898627e-13

## Source Hashes

- `results/B1_B7_cone01_composable_patch_certificate_gate_v0.json`: `220fea09694bd2d57f800a7d88842eed3713e28a1d76b4bf6136f97ac694371d`
- `results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`: `258bda18c5b77aa58dd36463357b3431a406ce33205994dfdc875aa6373d16a3`
- `results/B1_B7_cone01_openqasm3_composable_patch_lift_gate_v0.json`: `38e700c22376fc1356f5a1dc8e4770c7e9c2538edd3aae164c6a23afc6a04779`
- `results/B1_B7_cone01_openqasm3_linear_span_replay_certificate_gate_v0.json`: `f391bf34932121c7d6f1835ef8e301240a9d81c3c4b5c26b2e6d385f287fafa4`
- `results/B1_B7_cone01_openqasm3_structural_roundtrip_gate_v0.json`: `154b9fbd611aabed424ae19d1432d33b2a606a0f6d9f8a0a70e5723030eb99f5`
- `results/B1_B7_cone01_qasm2_candidate_rewrite_gate/gcm_h6_line268_line1381_candidate.qasm`: `2dfd0bee2dcdf02282839a6a5216d1fffda000ebb439581130d57b9cca455a38`

## Claim Boundary

The OpenQASM 3 patch-lift evidence chain is file-hash sealed: the QASM2 candidate, OpenQASM 3 candidate, source patch certificate, roundtrip certificate, finite-span certificate, and patch-lift certificate all match the recorded provenance seal.

Unsupported claims:

- This is not a Qiskit OpenQASM 3 loader parse.
- This is not a symbolic exact full-circuit unitary proof.
- This is not arbitrary-input or full-Hilbert-space coverage.
- This does not price or eliminate the remaining local-U3 parameters.
- This does not improve the B7 resource ledger.
