# B7 Shared-Synthesis Cache Boundary v0.1

Last updated: 2026-06-15

Status: **shared_synthesis_cache_no_ft_t_ledger_reduction_boundary**

## Summary

- Source ledger: `results/B7_ft_synthesis_ledger_v0.json`
- Before QASM: `/Users/avalok/work/FurturePlan/results/b1_heavyhex_end_to_end_30_level1_work/03_b1_heavyhex_d3_level1/qasmbench_medium_exact/gcm_h6.qasm`
- After QASM: `/Users/avalok/work/FurturePlan/results/b1_u3_phase_factored_optimizer/qasmbench_medium_exact/gcm_h6.qasm`
- Arbitrary rotation T cost: 20
- After numeric occurrences / unique instructions: 270 / 26
- Classical catalog reduction factor: 10.384615x
- FT T-ledger reduction from cache: 0
- Physical occurrence model clears 1.20x: False
- Invalid unique-template model clears 1.20x: False
- Invalid after-only unique-template model clears 1.20x: False
- Interpretation: Repeated gcm_h6 numeric angles support a classical synthesis-template cache, but the physical FT resource ledger remains occurrence-based.  Counting only unique numeric instructions would create an apparent resource win by changing the execution model, not by solving the circuit.

## Ledger Models

| model | before T ledger | after T ledger | min STV | gcm_h6 min STV | clears 1.20x | validity |
|---|---:|---:|---:|---:|---|---|
| physical_occurrence_injection | 6760 | 6224 | 1.086008x | 1.086008x | False | valid occurrence-execution ledger |
| invalid_unique_template_execution | 980 | 1344 | 0.729301x | 0.729301x | False | invalid for FT execution |
| invalid_after_only_unique_template_execution | 6760 | 1344 | 1.121827x | 1.508357x | False | invalid and unfair after-only charging |

## After Numeric Catalog

| numeric instruction | occurrences |
|---|---:|
| `ry(0.36485735178627743)` | 24 |
| `rz(0.36485735178627726)` | 24 |
| `rz(1.4922506383856682)` | 24 |
| `rz(2.1870074319274799)` | 24 |
| `ry(0.52538524712872736)` | 24 |
| `rz(2.538142068316358)` | 24 |
| `ry(1.1254377896453873)` | 24 |
| `rz(0.28861107553559073)` | 24 |
| `ry(0.42054081161117118)` | 24 |
| `ry(0.42054081161117135)` | 21 |
| `ry(0.99803486463019042)` | 4 |
| `ry(2.8134684478406049)` | 4 |
| `ry(1.9798156269941374)` | 4 |
| `ry(0.42054081161117129)` | 3 |
| `ry(0.99803486463018931)` | 2 |
| `ry(0.99803486463018953)` | 2 |

## Claim Boundary

- shared_synthesis_cache_can_reduce_classical_template_count: True
- shared_synthesis_cache_reduces_ft_t_ledger_under_occurrence_injection_model: False
- would_clear_1_20_if_miscounted_as_unique_execution: False
- would_clear_gcm_h6_1_20_if_miscounted_as_unique_execution: False
- would_clear_1_20_if_miscounted_after_only: False
- would_clear_gcm_h6_1_20_if_miscounted_after_only: True

## Next Actions

- A real T-ledger reduction must reduce physical rotation occurrences or replace a repeated block with a proven lower-cost unitary template.
- Try a nonlocal template-aware pass on repeated gcm_h6 blocks and verify it with Aer/proof logs.
- Keep shared-synthesis/cache as a compile-time optimization unless a physical reusable-state protocol is specified.

## Limits

- This is a resource-accounting boundary, not a certified no-go theorem for all possible circuit identities.
- The unique-template model is intentionally marked invalid for FT execution accounting.
- A future block-template rewrite could still reduce T ledger if it changes the implemented unitary with a proof.
