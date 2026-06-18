# B10-T2 Device-Noise Transcript Bridge v0.1

Last updated: 2026-06-17

Status: **device_noise_transcript_bridge_supports_bounded_noise_not_hardware_verifier**

## Summary

- Source target: B10-T2
- Source simulator: b10_t2_transcript_leakage_simulator_v0
- Method: b10_t2_device_noise_transcript_bridge_v0
- Configurations: 480
- Device profiles: ['ideal_transcript', 'low_noise_bridge', 'readout_biased_bridge', 'drift_correlated_bridge', 'calibration_side_channel']
- Minimum honest completeness: 1.000
- Bridge-safe high-leakage honest completeness: 1.000
- Bridge-safe high-leakage max soundness: 0.021
- Bridge-safe min unknown independent predicates: 7.0
- Bridge-safe refresh modes: ['challenge_refresh', 'refresh_plus_rotation']
- Bridge-safe device profiles: ['drift_correlated_bridge', 'ideal_transcript', 'low_noise_bridge', 'readout_biased_bridge']
- Margin-sensitive refresh modes: ['projection_rotation']
- Margin-sensitive profile/mode rows: [{'device_profile': 'low_noise_bridge', 'refresh_mode': 'projection_rotation', 'leakage_fraction': 0.75, 'max_empirical_soundness': 0.0625}]
- Unsafe device profiles: ['calibration_side_channel']
- Unsafe high-leakage refresh modes: ['challenge_refresh', 'none', 'projection_rotation', 'refresh_plus_rotation']
- Device-noise transcript bridge instantiated: True
- Hardware randomized-measurement circuits instantiated: False
- Sampling hardness proved: False
- Explicitly not a BQP separation: True
- Validation errors: 0

## High-Leakage Boundary By Profile

| profile | mode | bounded | honest | independence | min unknown | max soundness | adversaries over 5% |
|---|---|---:|---:|---:|---:|---:|---|
| ideal_transcript | none | True | 1.000 | False | 0.0 | 1.000 | oracle_cover_spoofer, stale_transcript_learner |
| ideal_transcript | projection_rotation | True | 1.000 | True | 6.0 | 0.042 | none |
| ideal_transcript | challenge_refresh | True | 1.000 | True | 8.0 | 0.000 | none |
| ideal_transcript | refresh_plus_rotation | True | 1.000 | True | 9.0 | 0.000 | none |
| low_noise_bridge | none | True | 1.000 | False | 0.0 | 1.000 | oracle_cover_spoofer, stale_transcript_learner |
| low_noise_bridge | projection_rotation | True | 1.000 | True | 6.0 | 0.062 | oracle_cover_spoofer |
| low_noise_bridge | challenge_refresh | True | 1.000 | True | 8.0 | 0.000 | none |
| low_noise_bridge | refresh_plus_rotation | True | 1.000 | True | 9.0 | 0.000 | none |
| readout_biased_bridge | none | True | 1.000 | False | 0.0 | 1.000 | oracle_cover_spoofer, stale_transcript_learner |
| readout_biased_bridge | projection_rotation | True | 1.000 | True | 6.0 | 0.021 | none |
| readout_biased_bridge | challenge_refresh | True | 1.000 | True | 8.0 | 0.000 | none |
| readout_biased_bridge | refresh_plus_rotation | True | 1.000 | True | 9.0 | 0.021 | none |
| drift_correlated_bridge | none | True | 1.000 | False | 0.0 | 1.000 | oracle_cover_spoofer, stale_transcript_learner |
| drift_correlated_bridge | projection_rotation | True | 1.000 | True | 5.0 | 0.021 | none |
| drift_correlated_bridge | challenge_refresh | True | 1.000 | True | 7.0 | 0.021 | none |
| drift_correlated_bridge | refresh_plus_rotation | True | 1.000 | True | 8.0 | 0.000 | none |
| calibration_side_channel | none | False | 1.000 | False | 0.0 | 1.000 | generative_mask_searcher, leaked_predicate_replayer, oracle_cover_spoofer, stale_transcript_learner |
| calibration_side_channel | projection_rotation | False | 1.000 | False | 0.0 | 1.000 | generative_mask_searcher, leaked_predicate_replayer, oracle_cover_spoofer, stale_transcript_learner |
| calibration_side_channel | challenge_refresh | False | 1.000 | False | 1.0 | 0.562 | generative_mask_searcher, oracle_cover_spoofer |
| calibration_side_channel | refresh_plus_rotation | False | 1.000 | False | 2.0 | 0.229 | oracle_cover_spoofer |

## Claim Boundary

- Supported: bounded device-noise transcript profiles preserve calibrated honest completeness and keep challenge_refresh / refresh_plus_rotation high-leakage empirical soundness below 5% in this proxy.
- Margin-sensitive: projection_rotation can exceed the 5% empirical gate under low-noise transcript calibration and should not be counted as bridge-safe without extra margin.
- Rejected: no-refresh and calibration-side-channel profiles do not satisfy the B10-T2 refresh-independence bridge.
- Not claimed: real hardware execution, cryptographic soundness, sampling hardness, or BQP/classical separation.

## Limits

- This is a device-noise transcript bridge, not hardware execution.
- Noise is calibrated through transcript-level honest reference samples, not through real device calibration data.
- The calibration_side_channel profile is intentionally rejected because it violates refresh independence.
- The bridge does not prove sampling hardness, cryptographic soundness, or BQP/classical separation.
