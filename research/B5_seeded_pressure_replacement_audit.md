# B5 Seeded-Pressure Replacement Audit v0.1

Last updated: 2026-07-01

Status: **seeded_pressure_replacement_failed_remains_blocker**

## Summary

- Method: `b5_seeded_pressure_replacement_audit_v0`
- Model status: `w2_replacement_audit_completed_no_deployable_denominator`
- Row contract hash: `7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc`
- Seeded mean relative response error: 0.000441626
- Best replacement candidate: `variational_mps_als`
- Best replacement mean relative response error: 0.0180555
- Best replacement rows beating seeded pressure: 0 / 9
- Deployable replacement count: 0
- Seeded pressure replaced: False
- Conditions satisfied/failed: 6 / 0
- Validation errors: 0

## Candidate Replay

| Candidate | Mean error | Rows beating seeded | Deployable selection | Production ready | Replaces seeded |
|---|---:|---:|---:|---:|---:|
| non_oracle_embedding | 0.0509835 | 2 / 9 | True | False | False |
| variational_mps_als | 0.0180555 | 0 / 9 | True | False | False |
| two_site_finite_dmrg_style | 0.0819613 | 0 / 9 | True | False | False |

## Conditions

| Condition | Satisfied | Evidence |
|---|---:|---|
| S1: Row contract from W4 is present and preserved | True | row_contract_hash=7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc; row_contract_count=9; source_checks_failed=0 |
| S2: Seeded MPS pressure is identified as exact-state seeded and non-deployable | True | seeded_exact_state_seeded=True; explicit_not_variational_dmrg=True; seeded_mean_relative_response_error=0.0004416259745141553 |
| S3: Replacement candidates are replayed on all nine rows | True | non_oracle_embedding=9; variational_mps_als=9; two_site_finite_dmrg_style=9 |
| S4: No replacement candidate globally beats seeded pressure | True | deployable_replacement_count=0; best_candidate_by_mean=variational_mps_als; best_candidate_mean_relative_response_error=0.01805548365563228; seeded_mean_relative_response_error=0.0004416259745141553; max_rows_beating_seeded_pressure=2 |
| S5: B10 same-access bridge remains blocked | True | same_access_positive_route_ready=False; production_dmrg_available=False; sampling_oracle_constructed=False |
| S6: Forbidden claims remain false | True | production_dmrg_claimed=False; quantum_response_win_claimed=False; same_access_positive_route_claimed=False; quantum_advantage_claimed=False; bqp_separation_claimed=False |

## Interpretation

W2 has been audited, but not solved. The exact-state-seeded MPS pressure reference remains the blocker.
The non-oracle embedding denominator beats seeded pressure on a small number of rows, but it does not replace it globally.
The non-exact-state-seeded MPS/ALS and two-site finite-DMRG-style prototypes also fail to replace seeded pressure.
A positive B5/B10 route must now come from W1 production DMRG/MPS or W3 same-access response-oracle evidence, or a stronger W2 retry.

## Claim Boundary

- what_is_supported: The current non-exact-state-seeded or non-oracle replacements do not globally replace the exact-state-seeded MPS pressure reference under the locked 9-row B5/B10 contract.
- what_is_not_supported: This is not production DMRG, not a deployable replacement denominator, not a response oracle, not a same-access positive route, not quantum advantage, and not BQP separation.
- next_gate: Run W1 production DMRG/MPS or W3 same-access response oracle. Any W2 retry must preserve the row-contract hash and beat seeded pressure globally without exact-state seeding.
- production_dmrg_claimed: False
- quantum_response_win_claimed: False
- accuracy_per_resource_win_claimed: False
- same_access_positive_route_claimed: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False
- dequantization_theorem_claimed: False
- sampling_access_theorem_claimed: False
