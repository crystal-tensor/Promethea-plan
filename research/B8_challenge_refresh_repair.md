# B8 Challenge-Refresh Repair Baseline v0.1

Last updated: 2026-06-13

Status: **challenge_refresh_projection_rotation_toy_repair_not_full_distribution_verification**

## Summary

- Tasks: 3
- Configurations: 192
- Samples per trial: 4096
- Trials: 120
- Leakage fractions: [0.0, 0.25, 0.5, 0.75]
- Refresh modes: ['none', 'projection_rotation', 'challenge_refresh', 'refresh_plus_rotation']
- Minimum honest completeness: 1.000
- Maximum adaptive soundness: 0.750
- High-leakage repair modes passing <=5% soundness: ['challenge_refresh', 'projection_rotation', 'refresh_plus_rotation']

## Summary By Refresh Mode

| mode | leakage | effective leakage | max soundness | mean soundness | adversaries over 5% |
|---|---:|---:|---:|---:|---|
| none | 0.00 | 0.000 | 0.000 | 0.000 | none |
| none | 0.25 | 0.250 | 0.000 | 0.000 | none |
| none | 0.50 | 0.500 | 0.000 | 0.000 | none |
| none | 0.75 | 0.750 | 0.750 | 0.181 | trap_aware_leakage_spoofer |
| projection_rotation | 0.00 | 0.000 | 0.000 | 0.000 | none |
| projection_rotation | 0.25 | 0.125 | 0.000 | 0.000 | none |
| projection_rotation | 0.50 | 0.250 | 0.000 | 0.000 | none |
| projection_rotation | 0.75 | 0.375 | 0.000 | 0.000 | none |
| challenge_refresh | 0.00 | 0.000 | 0.000 | 0.000 | none |
| challenge_refresh | 0.25 | 0.062 | 0.000 | 0.000 | none |
| challenge_refresh | 0.50 | 0.125 | 0.000 | 0.000 | none |
| challenge_refresh | 0.75 | 0.188 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.00 | 0.000 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.25 | 0.025 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.50 | 0.050 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.75 | 0.075 | 0.000 | 0.000 | none |

## Limits

- This is a toy repair baseline, not a proof of classical verification.
- Refresh and rotation are modeled as reducing effective leakage; a real protocol must instantiate fresh circuits or randomized measurement settings.
- Spoofers are heuristic projection-enforcement adversaries, not trained generative models.
- The result is useful only as a design gate for the next circuit-level B4/B8 task.
