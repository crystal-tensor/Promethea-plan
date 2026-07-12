# B4/B8 R121 Private Bundle Shot Sweep

## Summary

- Target: `T-B4-002v/T-B8-003z/T-B10-009n`
- Upstream target: `T-B4-002u/T-B8-003y/T-B10-009m`
- Method: `b4_b8_r121_private_bundle_shot_sweep_v0`
- Status: `private_signed_observable_bundle_shot_budget_boundary`
- Model status: `r120_bundle_shot_budget_sweep_with_ideal_and_light_aer_profiles`
- Tasks: `2` ideal six-qubit entangled tasks
- Profiles: `ideal, light`
- Shot budgets: `512, 1024, 2048, 4096, 8192`
- Trials per profile/task/budget: `12`
- Bundle size: `3`
- Fixed estimator tolerance: `0.6`
- Honest completeness floor: `0.8`

Profile results:

- `ideal`: 512: 0.5, 1024: 0.6666666666666666, 2048: 0.5, 4096: 0.8333333333333334, 8192: 0.9166666666666666
- `light`: 512: 0.25, 1024: 0.5833333333333334, 2048: 0.75, 4096: 1.0, 8192: 0.8333333333333334

R121 keeps the R120/R119 private signed observable bundle fixed and varies only
the shot budget under ideal and light Qiskit Aer profiles. Within this seeded
12-trial run, the first empirical floor crossing for the weakest task is ideal
at 4096 shots and light at 4096 shots; at
8,192 shots the corresponding values are `0.9166666666666666` and `0.8333333333333334`.
Intermediate values fluctuate, so matched-seed repeats are required before
interpreting profile ordering or monotonicity. This is synthetic shot-budget
sensitivity evidence only; no profile is treated as calibrated hardware
evidence.

## Requirements

- `P1` PASS: accepted R120 boundary is consumed
- `P2` PASS: ideal and light Aer profiles are replayed
- `P3` PASS: same three-observable bundle contract is retained
- `P4` PASS: five shot budgets are materialized as a sampling sweep
- `P5` PASS: completeness is reported per profile/task/budget
- `P6` PASS: no noise profile is mislabeled as calibrated hardware evidence
- `P7` PASS: R120 boundary is carried without a new soundness claim
- `P8` PASS: all profile circuits and shot-budget rows are materialized
- `P9` PASS: B4/B8/B10 advantage and BQP claims remain false
- `P10` PASS: shot-budget fluctuation is recorded as a caveat

## Claim Boundary

Supported: an explicit synthetic shot-budget sensitivity ledger for the R120
private bundle. Not supported: a monotonic noise law, calibrated backend
evidence, real hardware execution, general protocol soundness, cryptographic
soundness, sampling hardness, quantum advantage, BQP separation, or
full-distribution verification.
