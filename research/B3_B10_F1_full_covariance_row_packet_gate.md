# B3/B10 F1 Full-Covariance Row Packet Gate

- Target: `T-B3-022/T-B10-015i`
- Method: `b3_b10_f1_full_covariance_row_packet_gate_v0`
- Status: `f1_full_covariance_row_packet_open_missing_artifact`
- F1 packet: `B3B10-F1-full-compiled-state-covariance-rows`
- F1 packet hash: `dce2291e5ee21b7b2ccda8024d7da7afeb25565541e8dbe13035d1d9828612d7`
- Source triage hash: `74c8adb47c2505b314376585e02931c55d1e4eeffb9a1cebc15527c88d987f4b`
- Source acceptance packet hash: `24b94105d0b0de8d88fb1a6f456cdf1769dcd2efac8186594900c3bc3fff1f69`

## Result

The F1 gate passes 6/9 requirements and intentionally fails ['P6', 'P7', 'P8'] because no source-backed full compiled-state covariance row artifact has been submitted.

## Locked F1 Packet

- Submission path: `results/B3_B10_F1_full_covariance_row_submissions/B3B10-F1-full-compiled-state-covariance-rows.json`
- Required keys: `16`
- Production required keys: `9`
- Evidence file classes: `11`

Required evidence files:

- row_manifest
- compiled_state_replay_bundle
- full_covariance_matrix_bundle
- qwc_group_manifest
- shot_allocation_or_exact_covariance_note
- stateprep_circuit_manifest
- measurement_replay_transcript
- derivative_propagation_manifest
- same_access_denominator_contract
- optimizer_loop_cost_ledger
- claim_boundary_note

Acceptance predicates:

- packet_id equals B3B10-F1-full-compiled-state-covariance-rows
- downstream_packet_id equals B3-R1-full-compiled-covariance
- four row_aligned_instance_ids are supplied for the current B3/B10 reopen scope
- compiled state replay hashes and full covariance matrix hashes are source-backed
- QWC group manifests, state-prep circuit hashes, measurement replay commands, derivative propagation, denominator contract, and optimizer-loop cost ledger are present
- source_provenance_manifest_hash matches the accepted provenance-manifest gate hash
- claim_boundary forbids reaction-dynamics solution, quantum advantage, B3 reopen credit, B10-T1 credit, and BQP separation claims

## Evidence Boundary

- Downstream packet: `B3-R1-full-compiled-covariance`
- Row-aligned instances / compiled pilot: `4` / `1`
- Accepted full-covariance rows: `0`
- Denominator wins: `0`
- Optimizer-loop lower-bound shots: `475043013690000`
- F1 accepted: `False`
- B3 reopen / B10-T1 credit: `False` / `False`

## Requirement Results

- `P1` PASS: Post-boundary triage is valid and exposes F1 as a ready PR packet
- `P2` PASS: F5 B10 access replay remains blocked while accepted rows and denominator wins are zero
- `P3` PASS: Existing row acceptance gate remains the F1 source and is open on P6/P7/P8
- `P4` PASS: Locked B3/B10 full-covariance scope is preserved
- `P5` PASS: F1 packet schema and evidence classes are locked
- `P6` FAIL: F1 full-covariance row artifact has been submitted
- `P7` FAIL: Submitted F1 row artifact satisfies the locked schema
- `P8` FAIL: Submitted F1 row artifact is source-backed, downstream-bound, provenance-bound, and row-scope valid
- `P9` PASS: Forbidden B3/B10 reaction, advantage, reopen, credit, and BQP claims remain false

## Claim Boundary

- Supported: F1 now has a locked full compiled-state covariance row packet schema and acceptance boundary.
- Not supported: No F1 row artifact, accepted full-covariance row, denominator win, B3 reopen credit, B10-T1 credit, reaction-dynamics solution, quantum advantage, or BQP separation is supported.
- Next gate: Submit the F1 row artifact with four source-backed full compiled-state covariance rows, compiled-state replay, covariance matrices, QWC group manifests, state-prep circuit hashes, measurement replay, derivative propagation, denominator contract, optimizer-loop ledger, and claim boundary.

This packet gate does not claim a reaction-dynamics solution, quantum advantage, B3 reopen credit, B10-T1 credit, or BQP separation.

## Validation

- validation_error_count: `0`
