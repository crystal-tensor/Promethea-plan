# B1/B7 cone_01 OpenQASM 3 Phase-Consistent Replay Gate

Status: `cone01_openqasm3_phase_consistent_replay_passed_not_symbolic_certificate`

This artifact consumes T-B1-004by and adds overlap-phase and superposition pressure to the project-local OpenQASM 3 replay path.

## Summary

- Source QASM: `results/b1_native_t_resource_optimizer/qasmbench_medium_exact/gcm_h6.qasm`
- OpenQASM 3 candidate: `results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`
- Project-local parser passed / errors: `True` / `0`
- Input cases: `8` total; `4` phase anchors and `4` superposition inputs
- Source / OpenQASM 3 CNOT count / delta: `795` / `789` / `6`
- Phase-consistent replay passed: `True`
- Overlap phase spread radians: `1.3722356584366935e-13`
- Min overlap magnitude: `0.9999999999999772`
- Min state fidelity / max infidelity: `0.9999999999999547` / `4.529709940470639e-14`
- Max global-phase-aligned amplitude delta: `1.392888964263601e-13`
- Max probability delta: `1.074140776324839e-14`
- Accepted OpenQASM 3 phase replay / Qiskit loader / symbolic equivalence artifacts: `1` / `0` / `0`
- Accepted replay certificate / local-U3 pricing / occurrence / proxy-T reduction: `0` / `0` / `0` / `0`
- Validation errors: `0`

## Input Cases

| Case | Kind | Overlap phase | Fidelity | Max probability delta | Passed |
|---|---|---:|---:|---:|---|
| `zero` | `basis_phase_anchor` | `-2.4388324596671658` | `0.9999999999999551` | `5.551115123125783e-16` | `True` |
| `x_q0` | `basis_phase_anchor` | `-2.4388324596671658` | `0.9999999999999551` | `5.551115123125783e-16` | `True` |
| `x_q4` | `basis_phase_anchor` | `-2.438832459667149` | `0.9999999999999547` | `4.996003610813204e-16` | `True` |
| `x_q14` | `basis_phase_anchor` | `-2.438832459667166` | `0.9999999999999589` | `4.996003610813204e-16` | `True` |
| `sup_zero_xq4` | `basis_superposition` | `-2.438832459667139` | `0.9999999999999578` | `1.074140776324839e-14` | `True` |
| `sup_xq0_xq14` | `basis_superposition` | `-2.4388324596671653` | `0.9999999999999576` | `5.551115123125783e-16` | `True` |
| `sup_zero_product17` | `basis_product_superposition` | `-2.4388324596672057` | `1.000000000000147` | `4.182851981449076e-16` | `True` |
| `sup_product17_i_product29` | `product_superposition` | `-2.4388324596672764` | `1.0000000000000022` | `1.4784180824012338e-15` | `True` |

## Claim Boundary

The project-local OpenQASM 3 parser can construct the candidate and match the optimized source across phase-anchor and superposition statevector replay pressure while maintaining tiny overlap-phase spread.

Unsupported claims:

- This is not a Qiskit OpenQASM 3 loader parse.
- This is not symbolic unitary equivalence or arbitrary-input equivalence.
- This is not an exhaustive input-space replay certificate.
- This does not price or eliminate local-U3 burden.
- This does not create B7 occurrence, proxy-T, or space-time-volume credit.

## Next Required Gate

Move from project-local OpenQASM 3 phase replay to Qiskit-loader replay, symbolic/local-unitary evidence, or a global-phase anchored certificate; then separately price or eliminate the remaining local-U3 burden before any B7 resource credit is accepted.
