# B2 Biased-Noise Schedule Target-Volume Proxy v0.1

Last updated: 2026-06-13

Status: **biased_schedule_proxy_not_new_code_claim**

## Summary

- Criterion: wilson_95_high
- Candidate variants: ['balanced_bias_aligned_schedule', 'x_memory_bias_aligned_schedule', 'z_memory_bias_aligned_schedule']
- Target combinations: 40
- Baseline met count: 22
- Candidate met count: 28
- Candidate volume improvements: 0
- Candidate-only target hits: 6
- Mean volume reduction on improved rows: n/a
- Max volume reduction: n/a

## Candidate Variants

| variant | x multiplier | z multiplier | qubit multiplier | round multiplier |
|---|---:|---:|---:|---:|
| balanced_bias_aligned_schedule | 0.72 | 0.78 | 1.08 | 1.05 |
| z_memory_bias_aligned_schedule | 0.9 | 0.55 | 1.12 | 1.08 |
| x_memory_bias_aligned_schedule | 0.55 | 0.9 | 1.12 | 1.08 |

## Comparisons

| basis | p | target | baseline met | baseline volume | candidate met | candidate variant | candidate volume | volume reduction | interpretation |
|---|---:|---:|---|---:|---|---|---:|---:|---|
| x | 0.001 | 0.1 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.001 | 0.05 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.001 | 0.01 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.001 | 0.001 | False | n/a | True | balanced_bias_aligned_schedule | 116 | n/a | candidate_meets_target_unmet_by_baseline |
| x | 0.003 | 0.1 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.003 | 0.05 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.003 | 0.01 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.003 | 0.001 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.005 | 0.1 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.005 | 0.05 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.005 | 0.01 | False | n/a | True | x_memory_bias_aligned_schedule | 1064 | n/a | candidate_meets_target_unmet_by_baseline |
| x | 0.005 | 0.001 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.007 | 0.1 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.007 | 0.05 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.007 | 0.01 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.007 | 0.001 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.01 | 0.1 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| x | 0.01 | 0.05 | False | n/a | True | x_memory_bias_aligned_schedule | 120 | n/a | candidate_meets_target_unmet_by_baseline |
| x | 0.01 | 0.01 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| x | 0.01 | 0.001 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.001 | 0.1 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.001 | 0.05 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.001 | 0.01 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.001 | 0.001 | False | n/a | True | balanced_bias_aligned_schedule | 420 | n/a | candidate_meets_target_unmet_by_baseline |
| z | 0.003 | 0.1 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.003 | 0.05 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.003 | 0.01 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.003 | 0.001 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.005 | 0.1 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.005 | 0.05 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.005 | 0.01 | False | n/a | True | z_memory_bias_aligned_schedule | 1064 | n/a | candidate_meets_target_unmet_by_baseline |
| z | 0.005 | 0.001 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.007 | 0.1 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.007 | 0.05 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.007 | 0.01 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.007 | 0.001 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.01 | 0.1 | True | 78 | True | balanced_bias_aligned_schedule | 116 | 0.672x | no_candidate_advantage |
| z | 0.01 | 0.05 | False | n/a | True | balanced_bias_aligned_schedule | 116 | n/a | candidate_meets_target_unmet_by_baseline |
| z | 0.01 | 0.01 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |
| z | 0.01 | 0.001 | False | n/a | False | n/a | n/a | n/a | no_candidate_advantage |

## Limits

- This is a parameterized biased-schedule proxy, not a circuit-level biased-noise simulation.
- The proxy scales Wilson/observed logical error metrics from the existing Stim/PyMatching baseline and adds explicit qubit/round overhead.
- A candidate-only target is a hypothesis to test with real biased-noise circuits, not proof of low-overhead QEC.
- The comparison is useful because it uses the same target-volume contract as the surface-code baseline.
