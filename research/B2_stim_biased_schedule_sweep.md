# B2 Stim Biased-Schedule Circuit-Level Sweep v0.1

Last updated: 2026-06-13

Status: **stim_biased_schedule_circuit_sweep_not_new_code_claim**

## Summary

- Criterion: wilson_95_high
- Candidate variants: ['measurement_reset_hardened_schedule', 'data_memory_hardened_schedule', 'clifford_gate_hardened_schedule']
- Configurations: 90
- Total shots: 270000
- Target combinations: 40
- Baseline met count: 22
- Candidate met count: 26
- Candidate-only target hits: 4
- Candidate volume improvements: 0
- Mean volume reduction on improved rows: n/a
- Max volume reduction: n/a
- Max decoder runtime / shot: 1.33336e-05 s

## Candidate Variants

| variant | Clifford mult | data mult | measure mult | reset mult | description |
|---|---:|---:|---:|---:|---|
| measurement_reset_hardened_schedule | 1.0 | 1.0 | 0.5 | 0.5 | Halves measurement and reset flip probabilities while leaving data and Clifford depolarization unchanged. |
| data_memory_hardened_schedule | 1.0 | 0.5 | 1.0 | 1.0 | Halves before-round data depolarization while leaving reset, measurement, and Clifford depolarization unchanged. |
| clifford_gate_hardened_schedule | 0.5 | 1.0 | 1.0 | 1.0 | Halves Clifford-gate depolarization while leaving data, reset, and measurement noise unchanged. |

## Target Comparisons

| basis | p | target | baseline met | baseline volume | candidate met | variant | candidate d | candidate volume | volume reduction | interpretation |
|---|---:|---:|---|---:|---|---|---:|---:|---:|---|
| x | 0.001 | 0.1 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.001 | 0.05 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.001 | 0.01 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.001 | 0.001 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.003 | 0.1 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.003 | 0.05 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.003 | 0.01 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.003 | 0.001 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.005 | 0.1 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.005 | 0.05 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.005 | 0.01 | False | n/a | True | clifford_gate_hardened_schedule | 5 | 320 | n/a | candidate_meets_target_unmet_by_baseline |
| x | 0.005 | 0.001 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.007 | 0.1 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.007 | 0.05 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.007 | 0.01 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.007 | 0.001 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.01 | 0.1 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| x | 0.01 | 0.05 | False | n/a | True | clifford_gate_hardened_schedule | 3 | 78 | n/a | candidate_meets_target_unmet_by_baseline |
| x | 0.01 | 0.01 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.01 | 0.001 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.001 | 0.1 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.001 | 0.05 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.001 | 0.01 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.001 | 0.001 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.003 | 0.1 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.003 | 0.05 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.003 | 0.01 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.003 | 0.001 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.005 | 0.1 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.005 | 0.05 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.005 | 0.01 | False | n/a | True | clifford_gate_hardened_schedule | 5 | 320 | n/a | candidate_meets_target_unmet_by_baseline |
| z | 0.005 | 0.001 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.007 | 0.1 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.007 | 0.05 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.007 | 0.01 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.007 | 0.001 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.01 | 0.1 | True | 78 | True | clifford_gate_hardened_schedule | 3 | 78 | 1.000x | candidate_matches_baseline_target_without_volume_gain |
| z | 0.01 | 0.05 | False | n/a | True | clifford_gate_hardened_schedule | 3 | 78 | n/a | candidate_meets_target_unmet_by_baseline |
| z | 0.01 | 0.01 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.01 | 0.001 | False | n/a | False | n/a | n/a | n/a | n/a | no_candidate_advantage |

## Limits

- This is a real Stim circuit-level noise-parameter sweep, but it is not a new code-family claim.
- The candidate changes operation-class noise assumptions, so any advantage requires a physical mechanism for measurement/reset or data-memory hardening.
- The comparison uses the same Wilson target-volume contract as the surface-code baseline, but the baseline has not yet been retuned under identical biased hardware assumptions.
- The sweep is small: distances d=3/5/7, generated rotated-memory circuits, and finite shots.
