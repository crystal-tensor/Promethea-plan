# B5/B10 W1 Implementation Contract Gate v0.1

Status: **w1_implementation_contract_open_not_production_dmrg**

## Summary

- Method: `b5_b10_w1_implementation_contract_gate_v0`
- Row contract count/hash: 9 / `7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc`
- Requirements passed/failed: 5 / 5
- Failed requirement IDs: ['K5', 'K6', 'K7', 'K8', 'K9']
- Source blocker failed IDs: ['C3', 'C4', 'C5', 'C7']
- Implementation packet IDs: ['W1-E4-env-residuals', 'W1-E5-convergence', 'W1-E6-seeded-pressure', 'W1-E7-cost-ledger']
- Environment / residual / discarded rows: 0 / 0 / 0
- Convergence-passed rows: 0
- Rows beating seeded pressure: 0
- Same-access production cost ledger complete: False

## Requirement Ledger

| ID | Requirement | Passed | Evidence |
| --- | --- | --- | --- |
| K1 | Canonical residual blocker source is valid and negative | True | source_status=w1_canonical_residual_blocker_gate_failed_missing_production_evidence; source_validation_error_count=0 |
| K2 | Locked B5/B10 row contract hash is preserved | True | row_contract_hash=7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc; blocker_hash=7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc; denominator_hash=7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc |
| K3 | Source blocker packets are complete | True | source_packet_ids=['W1-E4-env-residuals', 'W1-E5-convergence', 'W1-E6-seeded-pressure', 'W1-E7-cost-ledger'] |
| K4 | Implementation contract schema is declared | True | required_row_key_count=17; implementation_packet_count=4 |
| K5 | Canonical environment rows are supplied | False | environment_rows=0; required_rows=9 |
| K6 | Orthonormal residual and discarded-weight rows are supplied | False | orthonormal_residual_rows=0; discarded_weight_rows=0; required_rows=9 |
| K7 | All nine rows pass convergence | False | convergence_passed_rows=0; required_rows=9 |
| K8 | Candidate beats seeded pressure on all rows | False | rows_beating_seeded_pressure=0; required_rows=9 |
| K9 | Same-access production cost ledger is complete | False | same_access_production_cost_ledger_complete=False |
| K10 | Forbidden claims remain false | True | production_dmrg_claimed=False; same_access_positive_route_claimed=False; quantum_advantage_claimed=False; bqp_separation_claimed=False |

## Row Artifact Schema

- required_row_count: 9
- row_contract_hash: `7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc`
- required_row_keys: ['row_id', 'sites', 'u_over_t', 'row_contract_hash', 'canonical_center_site', 'left_environment_hash', 'right_environment_hash', 'orthonormal_residual_norm', 'discarded_weight', 'sweep_count', 'energy_variance', 'fixed_sector_norm', 'relative_response_error', 'seeded_pressure_relative_response_error', 'wall_clock_seconds', 'peak_memory_mb', 'matvec_or_sweep_count']

## Implementation Packets

| Packet | Owner role | Required files | Acceptance |
| --- | --- | --- | --- |
| W1-E4-env-residuals | DMRG Solver Agent | results/B5_w1_environment_rows_v*.json, research/B5_w1_environment_rows.md | contains nine rows under the locked row-contract hash; stores left/right environment hashes for every row; stores orthonormal residual norms for every row |
| W1-E5-convergence | Baseline Adversary | results/B5_w1_convergence_ledger_v*.json, research/B5_w1_convergence_ledger.md | fixed-sector, energy-variance, discarded-weight, and monotonicity checks pass for all nine rows; all convergence thresholds are declared before comparing against seeded pressure |
| W1-E6-seeded-pressure | Tensor Denominator Agent | results/B5_w1_seeded_pressure_comparison_v*.json, research/B5_w1_seeded_pressure_comparison.md | compares against the exact-state-seeded MPS pressure row by row; records rows_beating_seeded_pressure == 9 before any positive B5/B10 route claim |
| W1-E7-cost-ledger | Cost Ledger Agent | results/B5_w1_same_access_cost_ledger_v*.json, research/B5_w1_same_access_cost_ledger.md | includes wall-clock, memory, sweep/matvec, and optimizer-loop costs; uses the same nine-row access contract without hidden exact-state access |

## Claim Boundary

- what_is_supported: The W1 production-DMRG blocker has been converted into an implementation contract with row-level schema, four packetized deliverables, and acceptance predicates tied to the locked B5/B10 row-contract hash.
- what_is_not_supported: This does not supply production DMRG, canonical environments, residual ledgers, converged rows, seeded-pressure wins, same-access cost evidence, a positive B5/B10 route, quantum advantage, or BQP separation.
- next_gate: A future W1 solver PR must submit all four implementation packets and pass K5-K9 before the B5/B10 route can be reconsidered.
- production_dmrg_claimed: False
- same_access_positive_route_claimed: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False

## Validation

- validation_error_count: 0
