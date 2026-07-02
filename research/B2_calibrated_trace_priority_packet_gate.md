# B2 Calibrated Trace Priority Packet Gate

Status: **calibrated_trace_priority_packet_open_missing_artifact**

## Summary

- Method: `b2_calibrated_trace_priority_packet_gate_v0`
- Priority packet: `B2-T5-calibrated-flag-observation-rows`
- Packet hash: `abec5e9114f6a6dcdc4d2b0bf7cc580c22fc6d8007fc68bdc2b1e9c7aae9378d`
- Requirements passed/failed: 6 / 3
- Failed requirement IDs: ['P6', 'P7', 'P8']
- Required row keys / production keys: 21 / 10
- Required evidence files: 8
- Challenge count / source traces / holdout profile shots: 3 / 576 / 864
- Submitted artifact exists: False

## Priority Packet

- packet_id: `B2-T5-calibrated-flag-observation-rows`
- submission_artifact_path: `results/B2_calibrated_trace_priority_submissions/B2-T5-calibrated-flag-observation-rows.json`
- blocks_contract_gate: `K4`
- blocks_scout_gate: `S5`

## Required Evidence Files

- backend_or_calibration_source_manifest
- backend_properties_hash_source
- detector_bitstring_artifact
- calibrated_flag_events_artifact
- flag_confusion_matrix_artifact
- decoder_profile_manifest
- raw_trace_artifact
- postprocess_script

## Acceptance Conditions

- all 21 required trace-row keys are present
- all 10 production-required keys are non-null and source-backed
- challenge_trace_hash is preserved from the existing B2 trace scout
- holdout_partition is declared before decoder comparison
- baseline_prediction and injected_prediction are replayable from source artifacts
- claim_boundary forbids production decoder, threshold, hardware, new-code, and advantage claims

## Requirement Results

- P1 [PASS]: Intake template remains valid and open on calibrated rows
- P2 [PASS]: Priority packet is fixed to calibrated flag observation rows
- P3 [PASS]: Priority packet carries the 21-key trace schema and 10 production keys
- P4 [PASS]: Packet binds required source evidence classes
- P5 [PASS]: Existing 3-challenge / 576-trace shape remains preserved
- P6 [FAIL]: Priority calibrated trace artifact has been submitted
- P7 [FAIL]: Submitted artifact satisfies the locked 21-key schema
- P8 [FAIL]: Submitted production keys are source-backed and non-null
- P9 [PASS]: Forbidden decoder, threshold, hardware, new-code, and advantage claims remain false

## Claim Boundary

- Supported: The first B2 calibrated-trace blocker now has a concrete source-backed row submission packet for calibrated flag observations.
- Not supported: No calibrated trace row has been submitted or accepted; no production decoder, threshold, hardware result, calibrated-device result, new-code result, or quantum advantage is supported.
- Next gate: Submit results/B2_calibrated_trace_priority_submissions/B2-T5-calibrated-flag-observation-rows.json with all 21 row keys, all 10 source-backed production keys, and replayable baseline/injected decoder predictions.
- production_decoder_claimed: False
- threshold_claimed: False
- hardware_result_claimed: False
- calibrated_device_claimed: False
- quantum_advantage_claimed: False

## Validation

- validation_error_count: 0
