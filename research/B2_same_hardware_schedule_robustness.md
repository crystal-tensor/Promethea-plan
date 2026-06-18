# B2 Same-Hardware Schedule Robustness Stress v0.1

Last updated: 2026-06-17

Status: **same_hardware_schedule_robustness_boundary_aggressive_only_or_negative**

## Summary

- Criterion: wilson_95_high
- Shots per configuration: 5000
- Profiles: higher_shot_reseed, mild_noise_mismatch_0p60, moderate_noise_mismatch_0p75, clifford_only_mechanism
- Base variants: round_reduced_all_ops_hardened, aggressive_round_reduced_all_ops_hardened
- Configurations: 240
- Total shots: 1200000
- Robust non-aggressive volume improvements: False
- Any aggressive volume improvement under stress: True
- Positive signal depends on aggressive schedule: True

## Profile Results

| profile | candidate met | candidate-only | improved volume | non-aggressive improved | aggressive improved | max reduction | interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| higher_shot_reseed | 35 | 13 | 22 | 0 | 22 | 3.000x | positive_signal_only_aggressive_under_profile |
| mild_noise_mismatch_0p60 | 35 | 13 | 22 | 0 | 22 | 3.000x | positive_signal_only_aggressive_under_profile |
| moderate_noise_mismatch_0p75 | 33 | 11 | 22 | 0 | 22 | 3.000x | positive_signal_only_aggressive_under_profile |
| clifford_only_mechanism | 33 | 11 | 22 | 0 | 22 | 3.000x | positive_signal_only_aggressive_under_profile |

## Improved Rows By Profile

| profile | basis | p | target | baseline volume | candidate variant | candidate d | candidate rounds | candidate volume | reduction |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|
| note | showing first 80 of 88 improved rows | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| higher_shot_reseed | x | 0.001 | 0.1 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | x | 0.001 | 0.05 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | x | 0.001 | 0.01 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | x | 0.003 | 0.1 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | x | 0.003 | 0.05 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | x | 0.003 | 0.01 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | x | 0.005 | 0.1 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | x | 0.005 | 0.05 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | x | 0.007 | 0.1 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | x | 0.007 | 0.05 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | x | 0.01 | 0.1 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.001 | 0.1 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.001 | 0.05 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.001 | 0.01 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.003 | 0.1 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.003 | 0.05 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.003 | 0.01 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.005 | 0.1 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.005 | 0.05 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.007 | 0.1 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.007 | 0.05 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| higher_shot_reseed | z | 0.01 | 0.1 | 78 | higher_shot_reseed::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.001 | 0.1 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.001 | 0.05 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.001 | 0.01 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.003 | 0.1 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.003 | 0.05 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.003 | 0.01 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.005 | 0.1 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.005 | 0.05 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.007 | 0.1 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.007 | 0.05 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | x | 0.01 | 0.1 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.001 | 0.1 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.001 | 0.05 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.001 | 0.01 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.003 | 0.1 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.003 | 0.05 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.003 | 0.01 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.005 | 0.1 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.005 | 0.05 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.007 | 0.1 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.007 | 0.05 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| mild_noise_mismatch_0p60 | z | 0.01 | 0.1 | 78 | mild_noise_mismatch_0p60::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.001 | 0.1 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.001 | 0.05 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.001 | 0.01 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.003 | 0.1 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.003 | 0.05 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.003 | 0.01 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.005 | 0.1 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.005 | 0.05 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.007 | 0.1 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.007 | 0.05 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | x | 0.01 | 0.1 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.001 | 0.1 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.001 | 0.05 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.001 | 0.01 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.003 | 0.1 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.003 | 0.05 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.003 | 0.01 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.005 | 0.1 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.005 | 0.05 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.007 | 0.1 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.007 | 0.05 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| moderate_noise_mismatch_0p75 | z | 0.01 | 0.1 | 78 | moderate_noise_mismatch_0p75::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.001 | 0.1 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.001 | 0.05 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.001 | 0.01 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.003 | 0.1 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.003 | 0.05 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.003 | 0.01 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.005 | 0.1 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.005 | 0.05 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.007 | 0.1 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.007 | 0.05 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | x | 0.01 | 0.1 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | z | 0.001 | 0.1 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | z | 0.001 | 0.05 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| clifford_only_mechanism | z | 0.001 | 0.01 | 78 | clifford_only_mechanism::aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |

## Claim Boundary

- robust_non_aggressive_volume_improvement_found: False
- any_aggressive_volume_improvement_under_stress: True
- positive_signal_depends_on_aggressive_schedule: True
- new_code_claimed: False
- threshold_claimed: False
- calibrated_device_claimed: False

## Limits

- This is a finite-shot robustness stress test, not a threshold proof.
- Noise-mismatch profiles are synthetic parameter stressors, not calibrated hardware drift models.
- A positive aggressive reduced-round row does not by itself justify a hardware schedule claim.
- B2 should not strengthen beyond diagnostic status until a non-aggressive or physically motivated schedule survives larger distances and calibrated/noise-mismatch checks.
