# B8 Adaptive Leakage Spoofer Stress Test v0.1

Last updated: 2026-06-13

Status: **adaptive_leakage_stress_test_not_full_distribution_verification**

## Summary

- Tasks: 3
- Configurations: 48
- Samples per trial: 4096
- Trials: 120
- Leakage fractions: [0.0, 0.25, 0.5, 0.75]
- Adversaries tested: ['known_projection_replay_spoofer', 'metadata_only_adaptive_spoofer', 'surrogate_projection_learner', 'trap_aware_leakage_spoofer']
- Minimum honest completeness: 1.000
- Maximum adaptive soundness: 0.792
- Dangerous leakage threshold: 0.75

## Leakage Summary

| leakage | max soundness | mean soundness | adversaries over 5% |
|---:|---:|---:|---|
| 0.00 | 0.000 | 0.000 | none |
| 0.25 | 0.000 | 0.000 | none |
| 0.50 | 0.000 | 0.000 | none |
| 0.75 | 0.792 | 0.188 | trap_aware_leakage_spoofer |

## Worst Rows

| task | leakage | adversary | soundness | mean max error | known | guessed hidden |
|---|---:|---|---:|---:|---:|---:|
| adaptive_hidden_projection_n16 | 0.75 | trap_aware_leakage_spoofer | 0.792 | 0.300 | 8 | 2 |
| adaptive_hidden_projection_n12 | 0.75 | trap_aware_leakage_spoofer | 0.742 | 0.291 | 8 | 2 |
| adaptive_hidden_projection_n20 | 0.75 | trap_aware_leakage_spoofer | 0.725 | 0.377 | 8 | 2 |
| adaptive_hidden_projection_n12 | 0.00 | known_projection_replay_spoofer | 0.000 | 0.680 | 0 | 0 |
| adaptive_hidden_projection_n12 | 0.00 | metadata_only_adaptive_spoofer | 0.000 | 0.929 | 0 | 2 |
| adaptive_hidden_projection_n12 | 0.00 | surrogate_projection_learner | 0.000 | 0.907 | 0 | 4 |
| adaptive_hidden_projection_n12 | 0.00 | trap_aware_leakage_spoofer | 0.000 | 0.982 | 0 | 7 |
| adaptive_hidden_projection_n12 | 0.25 | known_projection_replay_spoofer | 0.000 | 0.669 | 2 | 2 |
| adaptive_hidden_projection_n12 | 0.25 | metadata_only_adaptive_spoofer | 0.000 | 0.670 | 2 | 3 |
| adaptive_hidden_projection_n12 | 0.25 | surrogate_projection_learner | 0.000 | 0.711 | 2 | 5 |
| adaptive_hidden_projection_n12 | 0.25 | trap_aware_leakage_spoofer | 0.000 | 0.739 | 2 | 6 |
| adaptive_hidden_projection_n12 | 0.50 | known_projection_replay_spoofer | 0.000 | 0.694 | 5 | 3 |

## Limits

- This is an adaptive synthetic stress test, not real quantum-output verification.
- Spoofers observe controlled leakage fractions and use simple projection-enforcement heuristics, not trained generative models.
- The verifier still uses hidden parity projections, not classical shadows or randomized measurement data.
- A high-leakage failure should be read as a design warning: hidden challenges must remain hidden or be refreshed.
