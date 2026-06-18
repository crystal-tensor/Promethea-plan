# B8 Trained Generative Spoofer Refresh Stress v0.1

Last updated: 2026-06-17

Status: **trained_generative_spoofer_refresh_boundary_not_soundness_proof**

## Summary

- Source task: b4_b8_circuit_hidden_projection_refresh_v0
- Tasks: 3
- Configurations: 144
- Learners tested: ['correlation_mask_learner', 'generative_projection_learner', 'leakage_augmented_generator']
- Training samples per trial: 4096
- Verification samples per trial: 4096
- Minimum honest completeness: 1.000
- Maximum learned soundness: 1.000
- Safe high-leakage refresh modes: ['challenge_refresh', 'projection_rotation', 'refresh_plus_rotation']
- Unsafe high-leakage refresh modes: ['none']

## Refresh Summary

| mode | leakage | max learned soundness | mean learned soundness | learners over 5% |
|---|---:|---:|---:|---|
| none | 0.00 | 0.000 | 0.000 | none |
| none | 0.25 | 0.025 | 0.004 | none |
| none | 0.50 | 0.525 | 0.194 | generative_projection_learner, leakage_augmented_generator |
| none | 0.75 | 1.000 | 0.726 | correlation_mask_learner, generative_projection_learner, leakage_augmented_generator |
| projection_rotation | 0.00 | 0.000 | 0.000 | none |
| projection_rotation | 0.25 | 0.000 | 0.000 | none |
| projection_rotation | 0.50 | 0.000 | 0.000 | none |
| projection_rotation | 0.75 | 0.025 | 0.004 | none |
| challenge_refresh | 0.00 | 0.000 | 0.000 | none |
| challenge_refresh | 0.25 | 0.000 | 0.000 | none |
| challenge_refresh | 0.50 | 0.000 | 0.000 | none |
| challenge_refresh | 0.75 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.00 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.25 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.50 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.75 | 0.000 | 0.000 | none |

## Worst Learned Rows

| task | mode | leakage | learner | soundness | true masks selected | mean max error |
|---|---|---:|---|---:|---:|---:|
| cnot_hidden_projection_n12_d48 | none | 0.75 | generative_projection_learner | 1.000 | 10.00 | 0.032 |
| cnot_hidden_projection_n12_d48 | none | 0.75 | leakage_augmented_generator | 1.000 | 10.00 | 0.033 |
| cnot_hidden_projection_n16_d64 | none | 0.75 | generative_projection_learner | 1.000 | 10.00 | 0.031 |
| cnot_hidden_projection_n16_d64 | none | 0.75 | leakage_augmented_generator | 1.000 | 10.00 | 0.030 |
| cnot_hidden_projection_n20_d80 | none | 0.75 | generative_projection_learner | 1.000 | 10.00 | 0.031 |
| cnot_hidden_projection_n20_d80 | none | 0.75 | leakage_augmented_generator | 1.000 | 10.00 | 0.030 |
| cnot_hidden_projection_n12_d48 | none | 0.50 | leakage_augmented_generator | 0.525 | 9.43 | 0.236 |
| cnot_hidden_projection_n16_d64 | none | 0.50 | leakage_augmented_generator | 0.525 | 9.40 | 0.287 |
| cnot_hidden_projection_n20_d80 | none | 0.50 | leakage_augmented_generator | 0.512 | 9.38 | 0.267 |
| cnot_hidden_projection_n20_d80 | none | 0.75 | correlation_mask_learner | 0.212 | 8.55 | 0.437 |
| cnot_hidden_projection_n16_d64 | none | 0.75 | correlation_mask_learner | 0.188 | 8.45 | 0.513 |
| cnot_hidden_projection_n12_d48 | none | 0.75 | correlation_mask_learner | 0.138 | 8.55 | 0.446 |

## Claim Boundary

- This is a trained correlation/generative proxy, not a cryptographic soundness proof.
- Candidate parity masks are sampled from a side-channel quality model rather than learned from unrestricted circuit access.
- The task remains a CNOT hidden-projection proxy, not a hardware randomized-measurement verifier.
- Unsafe modes should be treated as B10-T2 proof obligations, not as final protocol failures.
