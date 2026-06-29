# B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Global-Phase Subspace Replay Gate

- Method: `b1_b7_cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_gate_v0`
- Status: `cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_passed`
- Model status: `qiskit_loader_openqasm3_has_global_phase_anchored_subspace_replay_without_b7_credit`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- Supported claim: The Qiskit-loaded OpenQASM 3 candidate matches the optimized source under one zero-input global phase anchor across 6 basis anchors and 15 coherent pair superpositions after final measurements are removed.

## Inputs

- Qiskit-loader phase-consistent gate: `results/B1_B7_cone01_openqasm3_qiskit_loader_phase_consistent_replay_gate_v0.json`
- Project-local global-phase subspace gate: `results/B1_B7_cone01_openqasm3_global_phase_subspace_replay_gate_v0.json`
- OpenQASM 3 candidate: `results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`

## Loader Evidence

- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Qubits / clbits / depth: 19 / 1 / 1483
- Operation counts: {'cx': 789, 'rz': 601, 'u': 487, 'measure': 1}

## Global-Phase Subspace Replay Evidence

- Global phase anchor: `zero` / `-2.4388324596671658` radians
- Input cases: 21 (6 basis anchors, 15 coherent superpositions)
- Max global-anchor phase delta: 3.142993331217661e-14
- Min overlap magnitude: 0.9999999999999772
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max amplitude / probability delta: 1.3928889642636009e-13 / 1.074140776324839e-14
- Failed cases: []
- Accepted Qiskit-loader parse / replay / phase / global-anchor artifacts: 1 / 1 / 1 / 1
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False

## Input Cases

| Case | Kind | Anchor phase delta | Fidelity | Max probability delta | Passed |
|---|---|---:|---:|---:|---|
| `zero` | `basis_subspace_anchor` | `-0.0` | `0.9999999999999551` | `5.551115123125783e-16` | `True` |
| `x_q0` | `basis_subspace_anchor` | `-0.0` | `0.9999999999999551` | `5.551115123125783e-16` | `True` |
| `x_q4` | `basis_subspace_anchor` | `1.677392667334493e-14` | `0.9999999999999547` | `4.996003610813204e-16` | `True` |
| `x_q14` | `basis_subspace_anchor` | `-5.083008082831797e-16` | `0.9999999999999589` | `4.996003610813204e-16` | `True` |
| `x_q0_q4` | `basis_subspace_anchor` | `1.677392667334493e-14` | `0.9999999999999547` | `4.996003610813204e-16` | `True` |
| `x_q4_q14` | `basis_subspace_anchor` | `1.609619226230069e-14` | `0.9999999999999583` | `7.771561172376096e-16` | `True` |
| `sup_zero_plus_x_q0` | `coherent_pair_superposition` | `1.2707520207079492e-15` | `0.9999999999999583` | `1.249000902703301e-16` | `True` |
| `sup_zero_minus_x_q0` | `coherent_pair_superposition` | `1.2707520207079492e-15` | `0.9999999999999583` | `1.249000902703301e-16` | `True` |
| `sup_zero_iplus_x_q0` | `coherent_pair_superposition` | `1.2707520207079492e-15` | `0.9999999999999583` | `1.249000902703301e-16` | `True` |
| `sup_zero_plus_x_q4` | `coherent_pair_superposition` | `2.6431642030725342e-14` | `0.9999999999999578` | `1.074140776324839e-14` | `True` |
| `sup_zero_minus_x_q4` | `coherent_pair_superposition` | `-8.556396939433526e-15` | `0.9999999999999587` | `1.066507993030541e-14` | `True` |
| `sup_zero_iplus_x_q4` | `coherent_pair_superposition` | `-3.142993331217661e-14` | `0.9999999999999591` | `4.697631172945194e-15` | `True` |
| `sup_x_q0_plus_x_q14` | `coherent_pair_superposition` | `4.235840069026497e-16` | `0.9999999999999576` | `5.551115123125783e-16` | `True` |
| `sup_x_q0_minus_x_q14` | `coherent_pair_superposition` | `4.235840069026497e-16` | `0.9999999999999576` | `5.551115123125783e-16` | `True` |
| `sup_x_q0_iplus_x_q14` | `coherent_pair_superposition` | `5.930176096637096e-16` | `0.9999999999999576` | `5.551115123125783e-16` | `True` |
| `sup_x_q4_plus_x_q0_q4` | `coherent_pair_superposition` | `1.75363778857697e-14` | `0.9999999999999576` | `1.1102230246251565e-16` | `True` |
| `sup_x_q4_minus_x_q0_q4` | `coherent_pair_superposition` | `1.75363778857697e-14` | `0.9999999999999576` | `1.1102230246251565e-16` | `True` |
| `sup_x_q4_iplus_x_q0_q4` | `coherent_pair_superposition` | `1.75363778857697e-14` | `0.9999999999999576` | `1.1102230246251565e-16` | `True` |
| `sup_x_q0_q4_plus_x_q4_q14` | `coherent_pair_superposition` | `1.685864347472546e-14` | `0.9999999999999576` | `3.885780586188048e-16` | `True` |
| `sup_x_q0_q4_minus_x_q4_q14` | `coherent_pair_superposition` | `1.685864347472546e-14` | `0.9999999999999576` | `3.885780586188048e-16` | `True` |
| `sup_x_q0_q4_iplus_x_q4_q14` | `coherent_pair_superposition` | `1.685864347472546e-14` | `0.9999999999999578` | `3.885780586188048e-16` | `True` |

## Claim Boundary

- This is sampled fixed-anchor subspace replay, not arbitrary-input equivalence.
- This is not a symbolic exact full-circuit unitary proof.
- This does not price or eliminate the remaining line-1381 off-grid local-U3 parameters.
- This does not recover the dropped line-1378 overlap delta.
- This does not improve the B7 resource ledger.

## Validation

- Qiskit-loader global-phase subspace replay passed: True
- Validation errors: 0
