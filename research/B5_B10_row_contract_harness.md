# B5/B10 Row-Contract Harness v0.1

Last updated: 2026-07-01

Status: **row_contract_preserved_guardrail_ready**

## Summary

- Method: `b5_b10_row_contract_harness_v0`
- Model status: `w4_row_contract_harness_executed_no_positive_route`
- Row contract count: 9
- Row contract hash: `7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc`
- Source checks passed/failed: 10 / 0
- Conditions satisfied/failed: 6 / 0
- W4 row-contract harness executed: True
- Remaining positive-route packets: W1, W2, W3
- Validation errors: 0

## Contract Rows

| Row | Row ID | sites | U/t | eta | n_up/n_down | observable | Hilbert dim |
|---:|---|---:|---:|---:|---|---|---:|
| 0 | `D5H_s4_u2_eta0.25_n2x2_obs_density_site_2` | 4 | 2.0 | 0.25 | 2/2 | density_response_susceptibility_proxy | 36 |
| 1 | `D5H_s4_u4_eta0.25_n2x2_obs_density_site_2` | 4 | 4.0 | 0.25 | 2/2 | density_response_susceptibility_proxy | 36 |
| 2 | `D5H_s4_u8_eta0.25_n2x2_obs_density_site_2` | 4 | 8.0 | 0.25 | 2/2 | density_response_susceptibility_proxy | 36 |
| 3 | `D5H_s6_u2_eta0.25_n3x3_obs_density_site_3` | 6 | 2.0 | 0.25 | 3/3 | density_response_susceptibility_proxy | 400 |
| 4 | `D5H_s6_u4_eta0.25_n3x3_obs_density_site_3` | 6 | 4.0 | 0.25 | 3/3 | density_response_susceptibility_proxy | 400 |
| 5 | `D5H_s6_u8_eta0.25_n3x3_obs_density_site_3` | 6 | 8.0 | 0.25 | 3/3 | density_response_susceptibility_proxy | 400 |
| 6 | `D5H_s8_u2_eta0.25_n4x4_obs_density_site_4` | 8 | 2.0 | 0.25 | 4/4 | density_response_susceptibility_proxy | 4900 |
| 7 | `D5H_s8_u4_eta0.25_n4x4_obs_density_site_4` | 8 | 4.0 | 0.25 | 4/4 | density_response_susceptibility_proxy | 4900 |
| 8 | `D5H_s8_u8_eta0.25_n4x4_obs_density_site_4` | 8 | 8.0 | 0.25 | 4/4 | density_response_susceptibility_proxy | 4900 |

## Source Checks

| Source | Rows/count | Passed | Mismatches |
|---|---:|---:|---:|
| B10 D5 denominator table | 9 | True | 0 |
| B5 non-oracle embedding baseline | 9 | True | 0 |
| B5 exact-state-seeded MPS pressure | 9 | True | 0 |
| B5 variational MPS/ALS prototype | 9 | True | 0 |
| B5 two-site finite-DMRG-style prototype | 9 | True | 0 |
| B5 canonical-environment smoke gate | 9 | True | 0 |
| B5 canonical DMRG readiness gate | 9 | True | 0 |
| B10 same-access bridge | 9 | True | 0 |
| B5/B10 production contract | 9 | True | 0 |
| B5/B10 production implementation triage | 6 | True | 0 |

## Conditions

| Condition | Satisfied | Evidence |
|---|---:|---|
| R1: Reference D5 row contract has exactly nine rows | True | row_count=9 |
| R2: Reference rows preserve the 3x3 sites/u grid | True | row_keys=[[4, 2.0], [4, 4.0], [4, 8.0], [6, 2.0], [6, 4.0], [6, 8.0], [8, 2.0], [8, 4.0], [8, 8.0]] |
| R3: All row-bearing B5 sources preserve row order and shared fields | True | checked_sources=['B10 D5 denominator table', 'B5 non-oracle embedding baseline', 'B5 exact-state-seeded MPS pressure', 'B5 variational MPS/ALS prototype', 'B5 two-site finite-DMRG-style prototype', 'B5 canonical-environment smoke gate']; mismatch_counts={'B10 D5 denominator table': 0, 'B5 non-oracle embedding baseline': 0, 'B5 exact-state-seeded MPS pressure': 0, 'B5 variational MPS/ALS prototype': 0, 'B5 two-site finite-DMRG-style prototype': 0, 'B5 canonical-environment smoke gate': 0} |
| R4: Count-only gates preserve nine-instance scope | True | checked_sources=['B5 canonical DMRG readiness gate', 'B10 same-access bridge', 'B5/B10 production contract']; counts={'B5 canonical DMRG readiness gate': 9, 'B10 same-access bridge': 9, 'B5/B10 production contract': 9} |
| R5: Triage still exposes W4 as the row-contract packet | True | packet_ids=['W1', 'W2', 'W3', 'W4', 'W5', 'W6']; w4_status=ready_now |
| R6: No positive route or forbidden claim is introduced | True | production_dmrg_claimed=False; quantum_response_win_claimed=False; accuracy_per_resource_win_claimed=False; same_access_positive_route_claimed=False; quantum_advantage_claimed=False; bqp_separation_claimed=False; dequantization_theorem_claimed=False; sampling_access_theorem_claimed=False |

## Interpretation

W4 is now executed as an auditable harness instead of a prose reminder.
The harness does not improve B5/B10 accuracy. It prevents future W1/W2/W3 outputs from changing the benchmark rows while claiming a denominator win.
Any future positive route must preserve the contract hash before cost or accuracy comparisons are accepted.

## Claim Boundary

- what_is_supported: The B5/B10 D5 row contract is now machine-checkable across the current denominator ladder, readiness/smoke gates, production contract, and triage queue.
- what_is_not_supported: This harness is not a new denominator, not production DMRG, not a response oracle, not a positive same-access route, not quantum advantage, and not BQP separation.
- next_gate: Future W1/W2/W3 outputs must preserve the row_contract_hash and the nine row IDs before they can be compared against the current ladder.
- production_dmrg_claimed: False
- quantum_response_win_claimed: False
- accuracy_per_resource_win_claimed: False
- same_access_positive_route_claimed: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False
- dequantization_theorem_claimed: False
- sampling_access_theorem_claimed: False
