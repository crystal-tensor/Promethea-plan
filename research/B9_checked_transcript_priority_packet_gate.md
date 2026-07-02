# B9 Checked Transcript Priority Packet Gate

Status: **checked_transcript_priority_packet_open_missing_artifact**

## Summary

- Method: `b9_checked_transcript_priority_packet_gate_v0`
- Model status: `priority_checked_transcript_packet_ready_no_checked_run_submitted`
- Priority packet: `B9-checked-width-locality-transcript`
- Packet hash: `948afb38dab74a9612316173024f06228bda70fce37dd1a957b9d95536a07969`
- Requirements passed/failed: 6 / 3
- Failed requirement IDs: ['P6', 'P7', 'P8']
- Required keys: 10
- Required evidence file classes: 8
- Blocks acquisition requirements: ['A3', 'A4', 'A6']
- Lean 4 / Lake available: False / False
- Checked transcript present: False
- Submitted artifact exists: False

## Submission Packet

- Submission path: `results/B9_checked_transcript_priority_submissions/B9-checked-width-locality-transcript.json`
- Expected checked transcript: `results/B9_checked_run_width_locality_transcript_v0.txt`

Required evidence files:

- lean_toolchain_file
- lean_version_transcript
- lake_version_transcript
- lake_env_lean_width_locality_transcript
- checked_transcript_file
- lean_module_source_hash
- offline_bundle_hash_manifest
- claim_boundary_note

Acceptance predicates:

- lean --version reports Lean 4.12.0 or the declared pinned toolchain equivalent
- lake --version exits successfully under the same toolchain
- lake env lean B9/ClusterStabilizer/WidthLocality.lean exits with returncode 0
- checked transcript hash matches the submitted transcript file
- lean module hash matches the current scaffold source
- claim_boundary forbids Quantum PCP, NLTS, formal theorem, and global impossibility claims

## Requirement Results

- P1 [PASS]: Checked-run acquisition gate remains valid and blocked only on A3/A4/A6
- P2 [PASS]: Pinned Lean toolchain and module source are present
- P3 [PASS]: Priority packet binds the three acquisition blockers
- P4 [PASS]: Packet carries checked transcript schema and evidence file classes
- P5 [PASS]: Current state has no proof-assistant checked theorem
- P6 [FAIL]: Priority checked transcript artifact has been submitted
- P7 [FAIL]: Submitted artifact satisfies the locked checked-run schema
- P8 [FAIL]: Submitted transcript is source-backed and returncode-zero
- P9 [PASS]: Forbidden Quantum PCP, NLTS, formal theorem, and global impossibility claims remain false

## Claim Boundary

- Supported: The first B9 proof-assistant blocker now has a concrete source-backed submission packet for a Lean/Lake checked transcript.
- Not supported: No checked transcript artifact has been submitted or accepted; no proof-assistant checked theorem, Quantum PCP proof, NLTS theorem, or global impossibility theorem is supported.
- Next gate: Submit results/B9_checked_transcript_priority_submissions/B9-checked-width-locality-transcript.json plus the checked transcript for lean --version, lake --version, and lake env lean B9/ClusterStabilizer/WidthLocality.lean.
- proof_assistant_checked: False
- formal_theorem_proved: False
- explicit_not_quantum_pcp_proof: True
- nlts_theorem_claimed: False

## Validation

- validation_error_count: 0
