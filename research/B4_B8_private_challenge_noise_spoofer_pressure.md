# B4/B8 Private Challenge Noise Spoofer Pressure

- Gate: T-B4-002d / T-B8-003h
- Method: `b4_b8_private_challenge_noise_spoofer_pressure_v0`
- Status: `parametric_spoofer_pressure_model_not_hardware`
- Spoofer pressure rows: 2880
- Gates passed: 6 / 8

## Result

| Metric | Value |
| --- | ---: |
| max no-leak spoofer acceptance | 0.1196875 |
| max backend-like refreshed no-leak spoofer acceptance | 0.109140625 |
| max backend-like no-refresh no-leak spoofer acceptance | 0.1196875 |
| max one-private-bit leak spoofer acceptance | 0.1987890625 |
| max three-private-bit leak spoofer acceptance | 0.6575 |
| max full-private-material leak spoofer acceptance | 1.0 |

## Interpretation

The parametric spoofer pressure does not keep no-leak attacks under the 0.10 diagnostic gate: max no-leak pressure reaches 0.1196875 and backend-like refreshed no-leak pressure reaches 0.109140625. Three-bit leakage remains dangerous and full private-material leakage still breaks the protocol. This makes the next engineering target sharper: replace the parametric pressure model with fitted or learned attacks, then move to real-backend or hardware transcript generation.

## Claim Boundary

- This is a deterministic parametric spoofer-pressure model, not actual ML training.
- This is not hardware execution and does not use real backend properties.
- This does not prove cryptographic or protocol soundness.
- This does not claim sampling hardness, quantum advantage, or BQP separation.
