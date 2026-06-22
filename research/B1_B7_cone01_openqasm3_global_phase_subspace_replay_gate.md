# B1/B7 cone_01 OpenQASM 3 Global-Phase Subspace Replay Gate

Status: `cone01_openqasm3_global_phase_subspace_replay_passed_not_symbolic_certificate`

This artifact consumes T-B1-004bz and fixes one global phase anchor before replaying basis anchors and coherent superpositions through the project-local OpenQASM 3 candidate.

## Summary

- Source QASM: `results/b1_native_t_resource_optimizer/qasmbench_medium_exact/gcm_h6.qasm`
- OpenQASM 3 candidate: `results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`
- Project-local parser passed / errors: `True` / `0`
- Global phase anchor: `zero` / `-2.4388324596671658` radians
- Input cases: `21` total; `6` basis anchors and `15` coherent pair superpositions
- Source / OpenQASM 3 CNOT count / delta: `795` / `789` / `6`
- Global-phase subspace replay passed: `True`
- Max global-anchor phase delta radians: `3.142993331217661e-14`
- Min overlap magnitude: `0.9999999999999772`
- Min state fidelity / max infidelity: `0.9999999999999547` / `4.529709940470639e-14`
- Max global-anchor-aligned amplitude delta: `1.3928889642636009e-13`
- Max probability delta: `1.074140776324839e-14`
- Accepted OpenQASM 3 anchored replay / Qiskit loader / symbolic equivalence artifacts: `1` / `0` / `0`
- Accepted replay certificate / local-U3 pricing / occurrence / proxy-T reduction: `0` / `0` / `0` / `0`
- Validation errors: `0`

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

The project-local OpenQASM 3 parser can construct the candidate and match the optimized source under one global phase anchor across basis anchors and coherent pair superpositions.

Unsupported claims:

- This is not a Qiskit OpenQASM 3 loader parse.
- This is not symbolic unitary equivalence or arbitrary-input equivalence.
- This is not an exhaustive input-space replay certificate.
- This does not price or eliminate local-U3 burden.
- This does not create B7 occurrence, proxy-T, or space-time-volume credit.

## Next Required Gate

Move from project-local OpenQASM 3 anchored replay to Qiskit-loader replay or symbolic/local-unitary evidence; then separately price or eliminate the remaining local-U3 burden before any B7 resource credit is accepted.
