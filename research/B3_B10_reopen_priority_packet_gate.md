# B3/B10 Reopen Priority Packet Gate

Status: **b3_b10_reopen_priority_packet_open_missing_artifact**

## Summary

- Method: `b3_b10_reopen_priority_packet_gate_v0`
- Model status: `priority_full_covariance_reopen_packet_ready_no_artifact_submitted`
- Priority packet: `B3-R1-full-compiled-covariance`
- Packet hash: `373a08c345cd80c3b5e1e55e0367d08468ba92fb0bb95cb287a3833b282360ca`
- Requirements passed/failed: 6 / 3
- Failed requirement IDs: ['P6', 'P7', 'P8']
- Required row keys: 10
- Required evidence file classes: 8
- Row-aligned / compiled-pilot instances: 4 / 1
- Full compiled-state covariance computed: False
- Submitted artifact exists: False
- Accepted priority reopen rows: 0

## Submission Packet

- Submission path: `results/B3_B10_reopen_priority_submissions/B3-R1-full-compiled-covariance.json`
- Blocks gate: `M5`
- Owner role: `chemistry_measurement_agent`
- Downstream gate: `rerun b3_b10_same_access_measurement_rescue_gate_v0`

Required evidence files:

- compiled_state_covariance_tables
- state_preparation_circuit_provenance
- grouped_observable_variance_covariance_ledger
- derivative_level_shot_floor_table
- sampled_vs_reference_covariance_validation
- source_rescue_gate_manifest
- source_negative_boundary_manifest
- claim_boundary_note

Acceptance predicates:

- all four row-aligned B3 reaction-coordinate rows have compiled-state covariance tables
- state-preparation circuit provenance exists for every row
- grouped observable covariance and derivative shot-floor ledgers are replayable
- sampled covariance validation rows compare against exact or high-confidence references
- source rescue and negative-boundary artifacts are hash-bound
- claim_boundary forbids B3 reopen, reaction solution, quantum advantage, and BQP separation claims

## Requirement Results

- P1 [PASS]: Reopen queue remains valid and aligned to M5-M9 blockers
- P2 [PASS]: Priority packet is fixed to full compiled-state covariance
- P3 [PASS]: Packet preserves the four-row B3 reaction-coordinate scope
- P4 [PASS]: Packet binds required evidence file classes
- P5 [PASS]: Current B3/B10 route stays demoted before submission
- P6 [FAIL]: Priority reopen artifact has been submitted
- P7 [FAIL]: Submitted artifact satisfies the locked full-covariance schema
- P8 [FAIL]: Submitted artifact is source-backed and covers all four rows
- P9 [PASS]: Forbidden reopen, solution, advantage, and BQP claims remain false

## Claim Boundary

- Supported: The first B3/B10 reopen blocker now has a concrete source-backed submission packet for full compiled-state covariance evidence.
- Not supported: No full-covariance artifact has been submitted or accepted; B3 remains demoted and no reaction-dynamics solution, quantum advantage, or BQP separation is supported.
- Next gate: Submit results/B3_B10_reopen_priority_submissions/B3-R1-full-compiled-covariance.json with all required full-covariance rows, state-prep provenance, covariance ledgers, derivative shot floors, and validation hashes.
- b3_reopen_ready: False
- reaction_dynamics_solution_claimed: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False

## Validation

- validation_error_count: 0
