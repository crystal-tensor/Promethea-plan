# B2 Calibrated Trace Row Provenance Manifest Gate

Status: `calibrated_trace_provenance_manifest_open_missing_artifact`

## Summary

- Method: `b2_calibrated_trace_provenance_manifest_gate_v0`
- Manifest: `B2-T5-calibrated-trace-row-provenance-manifest`
- Calibration source manifest: `B2-T5-calibration-source-manifest`
- Trace packet: `B2-T5-calibrated-flag-observation-rows`
- Calibration source manifest hash: `5e832922d1e2671a5ac0cc549e300d56e597210d66c97d5ef0f7e76242c6e46a`
- Manifest hash: `05ae214885638ff10adf13fdf017063929d728d00e40ca4ed858b90b0844c208`
- Requirements passed/failed: `6` / `3`
- Failed requirement IDs: `['P6', 'P7', 'P8']`
- Required key / production key / evidence file count: `16` / `11` / `13`
- Challenge count / source traces / holdout profile shots: `3` / `576` / `864`
- Submitted manifest exists: `False`
- Accepted priority trace rows: `0`
- B7 dependency credit allowed: `False`
- validation_error_count: `0`

## Manifest Packet

- Submission path: `results/B2_calibrated_trace_provenance_manifest_submissions/B2-T5-calibrated-trace-row-provenance-manifest.json`

Required evidence files:

- accepted_calibration_source_manifest
- row_batch_manifest
- detector_trace_hash_manifest
- flag_event_schema_note
- confusion_matrix_artifact
- decoder_profile_manifest
- holdout_partition_manifest
- posterior_likelihood_profile
- baseline_prediction_manifest
- injected_prediction_manifest
- replay_command_transcript
- b7_credit_boundary_note
- claim_boundary_note

Acceptance predicates:

- manifest_id equals B2-T5-calibrated-trace-row-provenance-manifest
- calibration_source_manifest_id equals B2-T5-calibration-source-manifest
- trace_packet_id equals B2-T5-calibrated-flag-observation-rows
- calibration_source_manifest_hash matches the accepted source-manifest gate hash
- row batch, detector trace hashes, flag schema, confusion matrix, decoder profile, holdout partition, posterior likelihood profile, baseline predictions, and injected predictions are hash-bound
- replay_hashes bind calibration_source_manifest_hash and trace_packet_id
- source evidence files are present and hash-bound
- b7_credit_boundary keeps dependency_credit_allowed false until accepted calibrated trace rows and all-challenge holdout non-regression exist
- claim_boundary forbids production decoder, threshold, calibrated-device, hardware-result, new-code, quantum-advantage, and B7 resource-credit claims

## Requirement Results

- P1 [PASS]: Calibration source manifest gate remains valid and blocked only on P6/P7/P8
- P2 [PASS]: Trace provenance manifest is bound to the source manifest and calibrated trace row packet
- P3 [PASS]: Manifest packet carries locked trace-row provenance schema and evidence classes
- P4 [PASS]: Existing B2 trace denominator shape is preserved
- P5 [PASS]: B7 dependency credit remains blocked before accepted calibrated trace rows
- P6 [FAIL]: Calibrated trace row provenance manifest artifact has been submitted
- P7 [FAIL]: Submitted manifest satisfies the locked trace-row provenance schema
- P8 [FAIL]: Submitted manifest is source-backed, source-manifest-bound, replay-bound, and B7-boundary-bound
- P9 [PASS]: Forbidden decoder, threshold, hardware, advantage, and B7-credit claims remain false

## Claim Boundary

- Supported: The B2/B7 calibrated-trace path now has a row-level provenance manifest packet that must bind calibration-source hashes, row-batch hashes, decoder inputs, holdout partitions, replay commands, and a zero-credit B7 boundary.
- Not supported: No calibrated trace provenance manifest or calibrated trace row has been submitted or accepted; no production decoder, threshold, hardware result, calibrated-device result, new-code result, quantum advantage, or B7 resource credit is supported.
- Next gate: Submit B2-T5-calibrated-trace-row-provenance-manifest with the accepted calibration source manifest hash, row-batch and detector trace hashes, decoder profile hashes, holdout partition hash, baseline/injected prediction hashes, replay command hash, and explicit B7 zero-credit boundary.
- production_decoder_claimed: False
- threshold_claimed: False
- hardware_result_claimed: False
- calibrated_device_claimed: False
- quantum_advantage_claimed: False
- b7_dependency_credit_allowed: False

## Validation

- validation_error_count: 0
