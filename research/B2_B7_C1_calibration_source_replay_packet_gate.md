# B2/B7 C1 Calibration Source Replay Packet Gate

- Target: `T-B2-010j/T-B7-012k`
- Method: `b2_b7_c1_calibration_source_replay_packet_gate_v0`
- Status: `c1_calibration_source_replay_packet_open_missing_artifact`
- C1 packet: `B2B7-C1-calibration-source-replay`
- C1 packet hash: `29e727e44df9f60d4ad25f760f54bbbfb5328877772675b4f229f631533d5047`
- Source triage hash: `df9285760dffbd92a3654e0e80d3a6dba15d6a7bcb7e333b596bd5c0f2e6c5ce`
- Source calibration manifest hash: `5e832922d1e2671a5ac0cc549e300d56e597210d66c97d5ef0f7e76242c6e46a`

## Result

The C1 gate passes 6/9 requirements and intentionally fails ['P6', 'P7', 'P8'] because no source-backed real-or-independent calibration replay artifact has been submitted.

## Locked C1 Packet

- Submission path: `results/B2_B7_C1_calibration_source_replay_submissions/B2B7-C1-calibration-source-replay.json`
- Required keys: `16`
- Production required keys: `10`
- Evidence file classes: `11`

Required evidence files:

- calibration_source_manifest
- provider_or_dataset_access_note
- acquisition_window_source
- backend_properties_or_noise_model_snapshot
- detector_trace_hash_manifest
- flag_event_schema_note
- confusion_matrix_or_labeling_plan
- holdout_partition_manifest
- independent_replay_bundle
- replay_command_transcript
- calibration_claim_boundary_note

Acceptance predicates:

- packet_id equals B2B7-C1-calibration-source-replay
- source_calibration_manifest_id equals B2-T5-calibration-source-manifest
- trace_packet_id equals B2-T5-calibrated-flag-observation-rows
- calibration_source_type is real_backend or independent_calibration
- backend or dataset access, acquisition window, backend/noise snapshot, detector trace hash manifest, flag schema, holdout partition, replay command, and independent replay bundle are present
- replay_hashes bind source_calibration_manifest_hash and trace_packet_id
- source evidence files are present and hash-bound
- claim_boundary forbids production decoder, threshold, calibrated-device, hardware-result, new-code, quantum-advantage, and B7 resource-credit claims

## Evidence Boundary

- Trace packet: `B2-T5-calibrated-flag-observation-rows`
- Challenges / source traces / holdout profile-shots: `3` / `576` / `864`
- Accepted calibrated trace rows: `0`
- C1 accepted: `False`
- B7 dependency / FT ledger / resource credit: `False` / `False` / `False`

## Requirement Results

- `P1` PASS: Post-boundary triage is valid and exposes C1 as a ready PR packet
- `P2` PASS: C4 B7 dependency replay remains blocked while accepted calibrated rows are zero
- `P3` PASS: Existing calibration source manifest gate remains the C1 source and is open on P6/P7/P8
- `P4` PASS: Locked calibrated trace scope is preserved
- `P5` PASS: C1 packet schema and evidence classes are locked
- `P6` FAIL: C1 calibration source replay artifact has been submitted
- `P7` FAIL: Submitted C1 replay artifact satisfies the locked schema
- `P8` FAIL: Submitted C1 replay artifact is source-backed, trace-bound, replay-bound, and source-type valid
- `P9` PASS: Forbidden B2/B7 decoder, hardware, threshold, advantage, and credit claims remain false

## Claim Boundary

- Supported: C1 now has a locked real-or-independent calibration source replay packet schema and acceptance boundary.
- Not supported: No C1 replay artifact, accepted calibrated trace row, production decoder, threshold, hardware result, calibrated-device result, quantum advantage, or B7 credit is supported.
- Next gate: Submit the C1 replay artifact with source-backed calibration source, backend or dataset access, acquisition window, backend/noise snapshot, detector trace hashes, flag schema, holdout partition, independent replay bundle, replay command, and claim boundary.

This packet gate does not claim a production decoder, threshold, hardware result, calibrated-device result, new code, quantum advantage, B7 dependency credit, FT ledger credit, or resource credit.

## Validation

- validation_error_count: `0`
