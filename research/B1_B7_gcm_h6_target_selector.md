# B1/B7 gcm_h6 Target Selector v0.1

Status: **gcm_h6_target_selector_not_rewrite_or_resource_claim**

This artifact converts the B7 `gcm_h6` resource boundary into ranked B1
rewrite targets. It does not rewrite the circuit, does not remove any
rotation, and does not claim a physical or semantic certificate.

## Summary

- Source QASM: `results/b1_u3_phase_factored_optimizer/qasmbench_medium_exact/gcm_h6.qasm`
- Arbitrary decimal rotations: 270
- Raw unique numeric parameters: 26
- Canonical unique numeric parameters: 17
- B7 one-sided `gcm_h6` 1.20x target: 30 removed arbitrary occurrences / 600 proxy-T ledger units
- Target fraction of current arbitrary rotations: 0.111111
- Top qubit target: q[2] with 42 arbitrary rotations
- Top canonical angle target: 0.364857351786 with 48 occurrences
- Top local CNOT-cone class occurrences: 45
- Cone classes meeting the 30-occurrence target: 3

## Top Cone Targets

| Cone | Gate | Prev CNOT | Next CNOT | Occurrences | Qubits | Angles | Certificate? |
|---|---|---|---|---:|---|---|---|
| cone_01 | ry | target:14 | target:14 | 45 | [1, 2, 4, 5, 8, 10, 12, 13, 15, 16] | ['0.364857351786', '0.420540811611', '0.525385247129', '0.99803486463'] | False |
| cone_02 | ry | target:16 | target:16 | 34 | [1, 2, 5, 10, 13, 14] | ['0.364857351786', '0.420540811611', '0.525385247129', '1.97981562699'] | False |
| cone_03 | ry | target:4 | target:4 | 32 | [3, 8, 11, 12, 14, 15] | ['0.364857351786', '0.420540811611', '0.525385247129', '1.97981562699'] | False |
| cone_04 | rz | target:14 | target:14 | 18 | [1, 2, 8, 10, 13, 16] | ['1.49225063839', '2.18700743193'] | False |
| cone_05 | rz | target:4 | target:4 | 14 | [3, 8, 12, 14, 15] | ['1.49225063839', '2.18700743193'] | False |
| cone_06 | rz | target:16 | target:16 | 14 | [2, 10, 13, 14] | ['1.49225063839', '2.18700743193'] | False |
| cone_07 | rz | target:4 | target:14 | 6 | [8, 15] | ['0.288611075536', '0.364857351786', '2.53814206832'] | False |
| cone_08 | rz | target:4 | target:15 | 6 | [3, 14] | ['0.288611075536', '0.364857351786', '2.53814206832'] | False |

## Top Canonical Angle Targets

| Canonical angle | Occurrences | Meets 30-occurrence target? | Shortfall |
|---|---:|---|---:|
| 0.364857351786 | 48 | True | 0 |
| 0.420540811611 | 48 | True | 0 |
| 1.49225063839 | 24 | False | 6 |
| 2.18700743193 | 24 | False | 6 |
| 0.525385247129 | 24 | False | 6 |
| 2.53814206832 | 24 | False | 6 |
| 1.12543778965 | 24 | False | 6 |
| 0.288611075536 | 24 | False | 6 |

## Top Qubit Targets

| Qubit | Occurrences | Meets 30-occurrence target? | Shortfall |
|---|---:|---|---:|
| q[2] | 42 | True | 0 |
| q[10] | 42 | True | 0 |
| q[13] | 41 | True | 0 |
| q[14] | 36 | True | 0 |
| q[15] | 24 | False | 6 |
| q[1] | 20 | False | 10 |
| q[8] | 20 | False | 10 |
| q[16] | 14 | False | 16 |

## Claim Boundary

- No rewrite is claimed.
- No resource reduction is claimed.
- No replayable semantic certificate is claimed.
- No physical layout result is claimed.

## Next Gate

A useful `T-B1-004` PR must choose one ranked family, produce an actual
semantic rewrite certificate, reduce at least the required `gcm_h6`
arbitrary rotation occurrences, and then re-run the B7 FT ledger.
