# B10-T2 Transcript Leakage Simulator v0.1

Last updated: 2026-06-17

Status: **transcript_leakage_simulator_supports_restricted_lemma_not_hardware_verifier**

## Summary

- Source target: B10-T2
- Source lemma: b10_t2_restricted_soundness_lemma_v0
- Method: b10_t2_transcript_leakage_simulator_v0
- Configurations: 192
- Minimum honest completeness: 1.000
- Maximum empirical soundness: 1.000
- Max refreshed high-leakage soundness: 0.025
- Min refreshed high-leakage unknown independent predicates: 6.0
- Refresh-independent high-leakage modes: ['challenge_refresh', 'projection_rotation', 'refresh_plus_rotation']
- Unsafe high-leakage modes: ['none']
- Hardware randomized-measurement circuits instantiated: False
- Sampling hardness proved: False
- Explicitly not a BQP separation: True
- Validation errors: 0

## Transcript Boundary By Mode

| mode | leakage | refresh independence | min unknown independent | max soundness | mean soundness | adversaries over 5% |
|---|---:|---:|---:|---:|---:|---|
| none | 0.00 | False | 0.0 | 1.000 | 0.250 | oracle_cover_spoofer |
| none | 0.25 | False | 0.0 | 1.000 | 0.250 | oracle_cover_spoofer |
| none | 0.50 | False | 0.0 | 1.000 | 0.250 | oracle_cover_spoofer |
| none | 0.75 | False | 0.0 | 1.000 | 0.250 | oracle_cover_spoofer |
| projection_rotation | 0.00 | True | 10.0 | 0.000 | 0.000 | none |
| projection_rotation | 0.25 | True | 9.0 | 0.000 | 0.000 | none |
| projection_rotation | 0.50 | True | 8.0 | 0.013 | 0.001 | none |
| projection_rotation | 0.75 | True | 6.0 | 0.000 | 0.000 | none |
| challenge_refresh | 0.00 | True | 10.0 | 0.013 | 0.001 | none |
| challenge_refresh | 0.25 | True | 9.0 | 0.000 | 0.000 | none |
| challenge_refresh | 0.50 | True | 9.0 | 0.000 | 0.000 | none |
| challenge_refresh | 0.75 | True | 8.0 | 0.025 | 0.003 | none |
| refresh_plus_rotation | 0.00 | True | 10.0 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.25 | True | 10.0 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.50 | True | 10.0 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.75 | True | 9.0 | 0.000 | 0.000 | none |

## Claim Boundary

- Supported: in this transcript model, refreshed modes retain at least one unknown independent predicate at high leakage and pass the empirical 5% soundness gate.
- Rejected: no-refresh high leakage still fails because stale transcript learning violates refresh independence.
- Not claimed: hardware execution, cryptographic soundness, sampling hardness, or BQP/classical separation.

## Limits

- This is a transcript-level simulator, not a hardware randomized-measurement verifier.
- It tests whether declared refresh schedules satisfy the independence assumption used by the B10-T2 restricted lemma.
- It does not prove sampling hardness or BQP/classical separation.
- Unrestricted hardware noise, calibration leakage, and device-specific side channels are not modeled.
