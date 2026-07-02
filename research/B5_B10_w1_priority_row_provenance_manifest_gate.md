# B5/B10 W1 Priority Row Provenance Manifest Gate

Status: `w1_priority_row_provenance_manifest_open_missing_artifact`

## Summary

- Method: `b5_b10_w1_priority_row_provenance_manifest_gate_v0`
- Manifest: `B5B10-W1-priority-row-provenance-manifest`
- Priority row: `D5H_s8_u2_eta0.25_n4x4_obs_density_site_4`
- Manifest hash: `2616aae62cc6af33da763faac1d7275e975ca9699dd752231b600975cff74b90`
- Requirements passed/failed: `6` / `3`
- Failed requirement IDs: `['P6', 'P7', 'P8']`
- Required manifest keys / production manifest keys / evidence files: `13` / `6` / `10`
- Priority row schema keys / production keys: `17` / `8`
- Submitted manifest exists: `False`
- Accepted priority rows: `0`
- validation_error_count: `0`

## Provenance Manifest Packet

- Submission path: `results/B5_B10_w1_priority_row_provenance_manifest_submissions/B5B10-W1-priority-row-provenance-manifest.json`
- Row contract hash: `7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc`
- Priority packet hash: `0d3620e8c5540bfd419718ab9d7ac5e4044e9f7736e0b23888f51114c13a3b8c`
- Template hash: `5ab7ee67accd826db90f4b3662b4377850f795529fe9d01327725d0dc4ae92e3`
- Prototype trace hash: `0c5c5b059eafffa41eac3d17754a26440fec114a2c58e40abf9bcc3958d9d547`

Required evidence files:

- canonical_state_manifest_source
- left_environment_hash_source
- right_environment_hash_source
- orthonormal_residual_protocol_note
- discarded_weight_protocol_note
- wall_clock_memory_measurement_note
- sweep_or_matvec_count_note
- same_access_replay_command_manifest
- row_contract_hash_replay_note
- claim_boundary_note

Acceptance predicates:

- manifest_id equals B5B10-W1-priority-row-provenance-manifest
- row_id equals D5H_s8_u2_eta0.25_n4x4_obs_density_site_4
- row_contract_hash, priority_packet_hash, template_hash, and prototype_trace_hash match the source priority packet
- canonical-state, environment-source, residual, discarded-weight, cost-ledger, and replay protocol hashes are present
- same_access_replay_hashes bind row_contract_hash, priority_packet_hash, and template_hash
- source evidence files are present and hash-bound
- claim_boundary forbids production-DMRG, positive-route, quantum-advantage, and BQP-separation claims

## Requirement Results

- P1 [PASS]: Priority-row submission packet remains valid and blocked only on P6/P7/P8
- P2 [PASS]: Priority row and locked W1 row contract are preserved
- P3 [PASS]: Manifest packet carries locked provenance schema and evidence file classes
- P4 [PASS]: Priority-row schema, production keys, and evidence classes remain preserved
- P5 [PASS]: Current state has no accepted priority row or production route credit
- P6 [FAIL]: Provenance manifest artifact has been submitted
- P7 [FAIL]: Submitted manifest satisfies the locked provenance schema
- P8 [FAIL]: Submitted manifest is source-backed, row-bound, and replay-hash-bound
- P9 [PASS]: Forbidden production, positive-route, advantage, and BQP claims remain false

## Claim Boundary

- Supported: The first B5/B10 W1 production-row obligation now has a pre-row provenance manifest packet that must bind state, environment, residual, discarded-weight, cost-ledger, and replay evidence before any priority row can be accepted.
- Not supported: No provenance manifest or priority production row has been submitted or accepted; no production DMRG denominator, same-access positive route, quantum advantage, or BQP separation is supported.
- Next gate: Submit results/B5_B10_w1_priority_row_provenance_manifest_submissions/B5B10-W1-priority-row-provenance-manifest.json before the priority-row JSON artifact, then rerun this gate and the priority-row submission gate.
- production_dmrg_claimed: False
- same_access_positive_route_claimed: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False

## Validation

- validation_error_count: 0
