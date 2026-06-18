# B2 Reduced-Round Artifact Boundary v0.1

Last updated: 2026-06-17

Status: **reduced_round_small_distance_aggressive_artifact_boundary**

## Summary

- Criterion: wilson_95_high
- Candidate positive rows: 22
- Robustness positive rows: 88
- Robust non-aggressive improved rows: 0
- All robustness improvements aggressive: True
- All robustness improvements at distance 3: True
- All robustness improvements at one candidate round: True
- Non-aggressive mechanism survives: False
- New code / threshold / calibrated device claimed: False / False / False
- Validation errors: 0

## Boundary Statement

The current reduced-round B2 signal is a useful diagnostic but should be treated as a small-distance aggressive-schedule artifact: all 22 original volume-positive rows and all 88 stress-preserved rows are aggressive, distance-3, one-round candidates, while the non-aggressive reduced-round mechanism has zero volume-improved rows under robustness stress.

## Candidate Positive Rows

- Variant counts: {'aggressive_round_reduced_all_ops_hardened': 22}
- Candidate distance counts: {'3': 22}
- Candidate round counts: {'1': 22}
- Target counts: {'0.01': 4, '0.05': 8, '0.1': 10}

## Robustness Positive Rows

- Variant counts: {'clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened': 22, 'higher_shot_reseed::aggressive_round_reduced_all_ops_hardened': 22, 'mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened': 22, 'moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened': 22}
- Candidate distance counts: {'3': 88}
- Candidate round counts: {'1': 88}
- Target counts: {'0.01': 16, '0.05': 32, '0.1': 40}

## Decision

close_T_B2_002_as_artifact_boundary_until_new_non_aggressive_mechanism_exists

## Claim Boundary

- Supported: finite-shot evidence that the current reduced-round lever does not survive as a non-aggressive volume-reducing mechanism.
- Supported: an explicit boundary that all preserved volume-positive rows are distance-3 one-round aggressive schedules.
- Not supported: a new quantum code, threshold theorem, calibrated-device schedule, or scalable low-overhead QEC solution.

## Next Steps

- Do not use the aggressive d-4 one-round signal as a low-overhead QEC claim.
- Open a new task only for a different mechanism: non-aggressive schedule, different code family, leakage-aware circuit model, or larger-distance validated decoder improvement.
- If the reduced-round idea is revisited, require distance 5/7 positive rows and non-aggressive volume improvement under noise mismatch before promoting it.
