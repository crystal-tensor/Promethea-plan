# B4/B8 Real-Backend Provider Manifest Gate

Status: `real_backend_provider_manifest_open_missing_artifact`

## Summary

- Method: `b4_b8_real_backend_provider_manifest_gate_v0`
- Priority packet: `B4B8-M6-provider-session-manifest`
- Downstream transcript packet: `B4B8-M6-real-backend-transcript-rows`
- Packet hash: `2a8779ab19f55f9dcf88ef6af26c5c3d33e9043f603060b5da07a49d93b25072`
- Requirements passed/failed: `6` / `3`
- Failed requirement IDs: `['P6', 'P7', 'P8']`
- Required key / production key / evidence file count: `10` / `7` / `8`
- Holdout row count: `160`
- No-leak / full-leak accepts per 160: `16` / `40`
- Real-backend transcript rows: `0`
- Provider manifest accepted: `False`
- validation_error_count: `0`

## Submission Packet

- Submission path: `results/B4_B8_real_backend_provider_manifest_submissions/B4B8-M6-provider-session-manifest.json`

Required evidence files:

- provider_access_manifest
- backend_properties_snapshot
- calibration_window_source
- runnable_circuit_manifest
- shot_budget_or_job_plan
- private_predicate_handling_plan
- hashing_and_redaction_manifest
- claim_boundary_note

Acceptance predicates:

- packet_id equals B4B8-M6-provider-session-manifest
- downstream_transcript_packet_id equals B4B8-M6-real-backend-transcript-rows
- provider, backend, access mode, calibration window, backend properties hash, runnable circuit manifest, and shot budget are present
- shot_budget covers at least the locked 160-row denominator or declares a reviewed replacement denominator
- source evidence files are present and hash-bound
- claim_boundary forbids protocol soundness, quantum advantage, sampling hardness, cryptographic soundness, and BQP separation claims

## Requirement Results

- P1 [PASS]: Transcript priority gate remains valid and blocked only on P6/P7/P8
- P2 [PASS]: Provider manifest is bound to the M6 real-backend transcript packet
- P3 [PASS]: Provider packet carries locked schema and evidence file classes
- P4 [PASS]: Locked margin budgets are preserved before hardware execution
- P5 [PASS]: Current state has no accepted hardware transcript or soundness claim
- P6 [FAIL]: Provider/session manifest artifact has been submitted
- P7 [FAIL]: Submitted manifest satisfies the locked provider schema
- P8 [FAIL]: Submitted manifest is source-backed, transcript-bound, and budget-sufficient
- P9 [PASS]: Forbidden soundness, advantage, and BQP claims remain false

## Claim Boundary

- Supported: The first B4/B8 hardware execution step now has a concrete provider/session manifest packet before any real-backend transcript can be accepted.
- Not supported: No provider/session manifest or real-backend transcript row has been submitted or accepted; no protocol soundness, quantum advantage, sampling hardness, cryptographic soundness, or BQP separation claim is supported.
- Next gate: Submit B4B8-M6-provider-session-manifest with provider/backend, access mode, calibration window, backend properties hash, runnable circuit manifest, shot budget, and claim boundary.
- protocol_soundness_proved: False
- cryptographic_soundness_proved: False
- sampling_hardness_proved: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False

## Validation

- validation_error_count: 0
