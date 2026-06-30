# B4/B8 Private Challenge Fitted Spoofer Attack

- Gate: T-B4-002e / T-B8-003i
- Method: `b4_b8_private_challenge_fitted_spoofer_attack_v0`
- Status: `fitted_spoofer_holdout_attack_on_synthetic_transcripts_not_hardware`
- Train / holdout rows: 560 / 160
- Fitted evaluation rows: 640
- Gates passed: 8 / 8

## Result

| Metric | Value |
| --- | ---: |
| private-safe max no-leak fitted acceptance | 0.0625 |
| private-safe backend-like refreshed no-leak fitted acceptance | 0.0625 |
| leakage-blind max no-leak fitted acceptance | 0.35 |
| global-prior max no-leak fitted acceptance | 0.328031573074 |
| leakage-aware max three-private-bit leak fitted acceptance | 0.5 |
| leakage-aware max full-private-material leak fitted acceptance | 1.0 |

## Interpretation

This converts the previous parametric spoofer-pressure warning into an actual train/holdout fitted-model diagnostic over the synthetic transcript bridge. The private-safe no-leak calibrator stays at the 1/16 guessing floor on holdout rows, but a leakage-blind mixture model exceeds the 0.10 no-leak threshold because its training distribution is contaminated by leaked-private-material cases. The result therefore narrows the live B4/B8 issue: no-leak private-safe fitting is not the immediate break, while leakage separation and real-backend transcript generation remain the hard next gates.

## Claim Boundary

- This performs deterministic fitted-model training on synthetic transcript rows.
- This is not hardware execution and does not use real backend properties.
- This does not prove cryptographic or protocol soundness.
- This does not claim sampling hardness, quantum advantage, or BQP separation.

