# B5/B10 W1 Priority-Row Acceptance Packet Gate

Status: `w1_priority_row_acceptance_packet_open_missing_artifact`

## Summary

- Method: `b5_b10_w1_priority_row_acceptance_packet_gate_v0`
- Acceptance packet: `B5B10-W1-priority-row-acceptance-packet`
- Priority row: `D5H_s8_u2_eta0.25_n4x4_obs_density_site_4`
- Replay-validation manifest: `B5B10-W1-priority-row-replay-validation-manifest`
- Replay-validation manifest hash: `21de29a096bd3c6534b4420a7d69afca1bc4c95e80750657f3a3d357dd17dd97`
- Priority packet hash: `0d3620e8c5540bfd419718ab9d7ac5e4044e9f7736e0b23888f51114c13a3b8c`
- Acceptance packet hash: `3b03c6a4463a4b4c0de589c5e170840f80d4c9e753de6f0af8df98def45e2037`
- Row contract hash: `7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc`
- Requirements passed/failed: `6` / `3`
- Failed requirement IDs: `['P6', 'P7', 'P8']`
- Required key / production key / evidence file count: `25` / `18` / `16`
- Row contracts / prototype trace hashes / discarded-weight metric rows: `9` / `9` / `9`
- Production contract rows accepted: `0`
- Submitted acceptance packet exists: `False`
- Accepted priority rows: `0`
- B10-T1 positive route ready: `False`
- validation_error_count: `0`

## Acceptance Packet

- Submission path: `results/B5_B10_w1_priority_row_acceptance_packet_submissions/B5B10-W1-priority-row-acceptance-packet.json`
- Packet hash: `3b03c6a4463a4b4c0de589c5e170840f80d4c9e753de6f0af8df98def45e2037`

Required evidence files:

- accepted_replay_validation_manifest
- priority_row_packet_contract
- accepted_provenance_manifest
- canonical_state_replay_manifest
- canonical_center_site_table
- left_environment_tensor_hash_manifest
- right_environment_tensor_hash_manifest
- orthonormal_residual_table
- discarded_weight_table
- convergence_ledger
- sweep_matvec_ledger
- wall_clock_memory_ledger
- seeded_pressure_comparison_manifest
- same_access_cost_ledger
- b10_access_boundary_note
- claim_boundary_note

Acceptance predicates:

- acceptance_packet_id equals B5B10-W1-priority-row-acceptance-packet
- priority row, provenance manifest, replay-validation manifest, priority packet hash, and row-contract hash match the source gates
- canonical state replay, center site, left/right environment hashes, residual norm, discarded weight, convergence, sweep/matvec, wall-clock/memory, seeded-pressure, and same-access cost ledgers are hash-bound
- accepted_priority_row_count and production_contract_rows_accepted are positive only after source evidence exists
- orthonormal_residual_norm is at or below 1e-8 for the accepted priority row
- B10 access boundary remains zero-credit and explicitly denies same-access positive-route or BQP-separation credit
- claim_boundary forbids production DMRG, same-access positive route, quantum advantage, and BQP separation claims until a larger audited denominator route closes

## Requirement Results

- P1 [PASS]: Replay-validation manifest gate remains valid and blocked only on P6/P7/P8
- P2 [PASS]: Priority row packet remains fixed and source-shaped
- P3 [PASS]: Acceptance packet carries locked W1 production-row schema and evidence classes
- P4 [PASS]: Replay scope and prototype blockers remain preserved
- P5 [PASS]: Current state has no accepted priority row or forbidden claims
- P6 [FAIL]: Priority-row acceptance packet has been submitted
- P7 [FAIL]: Submitted acceptance packet satisfies the locked W1 production-row schema
- P8 [FAIL]: Submitted acceptance packet is source-backed, manifest-bound, row-valid, B10-boundary-bound, and claim-boundary-bound
- P9 [PASS]: Forbidden production, positive-route, advantage, and BQP claims remain false

## Claim Boundary

- Supported: The B5/B10 W1 route now has a priority-row acceptance packet defining what the first source-backed production-row artifact must contain before it can count.
- Not supported: No priority-row acceptance packet or production row has been submitted or accepted; no production DMRG denominator, same-access positive route, quantum advantage, or BQP separation is supported.
- Next gate: Submit B5B10-W1-priority-row-acceptance-packet with the accepted replay-validation manifest hash, canonical center and environment hashes, residual and discarded-weight evidence, convergence and resource ledgers, seeded-pressure comparison, same-access cost ledger, B10 access boundary, and claim boundary.
- production_dmrg_claimed: False
- same_access_positive_route_claimed: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False

## Validation

- validation_error_count: 0
