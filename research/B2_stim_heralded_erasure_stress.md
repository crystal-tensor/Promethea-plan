# B2 Stim Heralded-Erasure Leakage Stress v0.1

Status: **stim_heralded_erasure_stress_boundary_not_full_leakage_decoder**

## Summary

- Method: b2_stim_heralded_erasure_stress_v0
- Model status: stim_generated_surface_code_with_tick_level_unheralded_vs_heralded_erasure_noise
- Toolchain: Stim HERALDED_ERASE / DEPOLARIZE1 plus PyMatching detector-error-model decoder
- Configurations: 108
- Total shots: 216000
- Target comparisons: 72
- Baseline met count: 53
- Candidate met count: 59
- Candidate-only target hits: 7
- Improved target-volume rows: 10
- Improved rows with candidate distance 5 or 7: 10
- Max volume reduction after flag overhead: 4.5978260869565215
- Mean volume reduction after flag overhead: 2.622552373934098
- Validation errors: []

## Mode Summary

| mode | configs | shots | mean Wilson high | min Wilson high | max Wilson high | max decode s/shot |
|---|---:|---:|---:|---:|---:|---:|
| heralded_erasure_proxy | 54 | 108000 | 0.0195278 | 0.00191712 | 0.0745088 | 1.66526e-05 |
| unheralded_depolarizing_leakage_proxy | 54 | 108000 | 0.0273511 | 0.00191712 | 0.0809545 | 1.84771e-05 |

## Improved Target-Volume Rows

| basis | p | leakage/tick | target | baseline d | candidate d | baseline volume | candidate volume | reduction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| x | 0.001 | 0.01 | 0.02 | 9 | 5 | 1692.00 | 368.00 | 4.598x |
| z | 0.001 | 0.01 | 0.02 | 9 | 5 | 1692.00 | 368.00 | 4.598x |
| x | 0.001 | 0.005 | 0.01 | 7 | 5 | 826.00 | 368.00 | 2.245x |
| z | 0.001 | 0.005 | 0.01 | 7 | 5 | 826.00 | 368.00 | 2.245x |
| x | 0.003 | 0.005 | 0.02 | 7 | 5 | 826.00 | 368.00 | 2.245x |
| z | 0.003 | 0.005 | 0.02 | 7 | 5 | 826.00 | 368.00 | 2.245x |
| x | 0.003 | 0.01 | 0.05 | 7 | 5 | 826.00 | 368.00 | 2.245x |
| z | 0.003 | 0.01 | 0.05 | 7 | 5 | 826.00 | 368.00 | 2.245x |
| z | 0.003 | 0.005 | 0.01 | 9 | 7 | 1692.00 | 949.90 | 1.781x |
| z | 0.005 | 0.003 | 0.02 | 9 | 7 | 1692.00 | 949.90 | 1.781x |

## Claim Boundary

- new_code_claimed: False
- threshold_claimed: False
- calibrated_device_claimed: False
- full_physical_leakage_decoder_claimed: False
- shot_conditioned_erasure_decoder_claimed: False
- circuit_derived_stim_evidence: True
- reduced_rounds_used: False
- distance_3_candidate_used: False
- what_is_supported: Under a Stim generated rotated-surface-code memory circuit with tick-level DEPOLARIZE1 versus HERALDED_ERASE leakage proxies, the heralded-erasure proxy can lower Wilson target-volume pressure on some d=5/d=7 rows after a declared flag-overhead penalty.
- what_is_not_supported: This is not a calibrated leakage model, threshold estimate, new code, hardware result, or full shot-conditioned erasure decoder.

## Next Gate

Replace this detector-error-model stress with either a shot-conditioned erasure
decoder, a more realistic leakage circuit model, or calibrated backend leakage
data. The result should be demoted if the d=5/d=7 volume rows disappear under
that stronger model.
