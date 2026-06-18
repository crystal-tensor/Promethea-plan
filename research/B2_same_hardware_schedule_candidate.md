# B2 Same-Hardware Schedule Candidate v0.1

Last updated: 2026-06-16

Status: **same_hardware_schedule_candidate_volume_positive_diagnostic_not_new_code_claim**

## Summary

- Criterion: wilson_95_high
- Candidate variants: ['round_reduced_baseline_noise', 'round_reduced_clifford_hardened', 'round_reduced_all_ops_hardened', 'aggressive_round_reduced_all_ops_hardened']
- Configurations: 120
- Total shots: 360000
- Target combinations: 40
- Baseline met count: 22
- Candidate met count: 30
- Candidate-only target hits: 8
- Candidate volume improvements: 22
- Mean volume reduction on improved rows: 3.0
- Max volume reduction: 3.0

## Candidate Variants

| variant | round delta | Clifford mult | data mult | measure mult | reset mult | description |
|---|---:|---:|---:|---:|---:|---|
| round_reduced_baseline_noise | -2 | 1.0 | 1.0 | 1.0 | 1.0 | Same distance and physical qubits as baseline, but uses d-2 syndrome rounds without changing operation-class noise. |
| round_reduced_clifford_hardened | -2 | 0.5 | 1.0 | 1.0 | 1.0 | Same hardware footprint with d-2 syndrome rounds and half Clifford depolarization, testing whether schedule-level hardening can buy lower target volume. |
| round_reduced_all_ops_hardened | -2 | 0.5 | 0.5 | 0.5 | 0.5 | Same hardware footprint with d-2 syndrome rounds and half noise multipliers for Clifford, data, measurement, and reset operations. |
| aggressive_round_reduced_all_ops_hardened | -4 | 0.5 | 0.5 | 0.5 | 0.5 | Same hardware footprint with d-4 syndrome rounds and half operation-class noise; included as an aggressive schedule boundary test. |

## Improved Target-Volume Rows

| basis | p | target | baseline d | baseline volume | candidate variant | candidate d | candidate rounds | candidate volume | reduction |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| x | 0.001 | 0.1 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| x | 0.001 | 0.05 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| x | 0.001 | 0.01 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| x | 0.003 | 0.1 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| x | 0.003 | 0.05 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| x | 0.003 | 0.01 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| x | 0.005 | 0.1 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| x | 0.005 | 0.05 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| x | 0.007 | 0.1 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| x | 0.007 | 0.05 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| x | 0.01 | 0.1 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.001 | 0.1 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.001 | 0.05 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.001 | 0.01 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.003 | 0.1 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.003 | 0.05 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.003 | 0.01 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.005 | 0.1 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.005 | 0.05 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.007 | 0.1 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.007 | 0.05 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |
| z | 0.01 | 0.1 | 3 | 78 | aggressive_round_reduced_all_ops_hardened | 3 | 1 | 26 | 3.000x |

## Claim Boundary

- same_hardware_volume_improvement_found: True
- improved_volume_count: 22
- max_volume_reduction: 3.0
- candidate_only_meets_target_count: 8
- new_code_claimed: False
- threshold_claimed: False
- calibrated_device_claimed: False

## Limits

- This is a same-code-family schedule/noise candidate, not a new quantum code.
- The candidate uses reduced syndrome rounds, so positive rows must be interpreted as schedule-level target-volume diagnostics.
- The noise hardening variants require a physical mechanism before any hardware claim.
- The sweep is finite-shot and small-distance; Wilson upper bounds are conservative but not a threshold proof.
