# B9 Checked Transcript Provenance Manifest Gate

Status: `checked_transcript_provenance_manifest_open_missing_artifact`

## Summary

- Method: `b9_checked_transcript_provenance_manifest_gate_v0`
- Manifest: `B9-checked-width-locality-transcript-provenance-manifest`
- Priority packet: `B9-checked-width-locality-transcript`
- Manifest hash: `1b3716b5f1a8ca396557dad26298a99a469349733abcf6d345e9cd4bb467f1d1`
- Requirements passed/failed: `6` / `3`
- Failed requirement IDs: `['P6', 'P7', 'P8']`
- Required manifest keys / production manifest keys / evidence files: `13` / `8` / `10`
- Blocks acquisition requirements: `['A3', 'A4', 'A6']`
- Submitted manifest exists: `False`
- Checked transcript present: `False`
- Proof assistant checked: `False`
- validation_error_count: `0`

## Provenance Manifest Packet

- Submission path: `results/B9_checked_transcript_provenance_manifest_submissions/B9-checked-width-locality-transcript-provenance-manifest.json`
- Priority packet hash: `948afb38dab74a9612316173024f06228bda70fce37dd1a957b9d95536a07969`
- Lean module hash at gate time: `d885cfe38990798c8cbd281959ed995a17427b38991968a9f40801c2a3bfa43c`

Required evidence files:

- lean_toolchain_file
- lakefile_source
- lean_module_source
- lean_version_stdout_transcript
- lake_version_stdout_transcript
- lake_env_lean_width_locality_transcript
- checked_transcript_file
- offline_bundle_hash_manifest
- reproduction_environment_note
- claim_boundary_note

Acceptance predicates:

- manifest_id equals B9-checked-width-locality-transcript-provenance-manifest
- packet_id equals B9-checked-width-locality-transcript
- priority_packet_hash matches the source priority packet
- lean-toolchain, lakefile, and Lean module hashes match the submitted checked run
- Lean version, Lake version, and lake env lean transcripts are present and hash-bound
- returncode is 0 and checked_transcript_sha256 matches the checked transcript file
- source evidence files are present and replay hashes bind priority packet plus local source hashes
- claim_boundary forbids Quantum PCP, NLTS, formal theorem, and global impossibility claims

## Requirement Results

- P1 [PASS]: Priority checked transcript packet remains valid and blocked only on P6/P7/P8
- P2 [PASS]: Pinned Lean project sources remain present
- P3 [PASS]: Manifest packet carries locked provenance schema and evidence file classes
- P4 [PASS]: Manifest remains bound to acquisition blockers A3/A4/A6 and the priority packet hash
- P5 [PASS]: Current state has no checked transcript or theorem claim
- P6 [FAIL]: Provenance manifest artifact has been submitted
- P7 [FAIL]: Submitted manifest satisfies the locked checked-run provenance schema
- P8 [FAIL]: Submitted manifest is source-backed, packet-bound, replay-hash-bound, and returncode-zero
- P9 [PASS]: Forbidden Quantum PCP, NLTS, formal theorem, and global impossibility claims remain false

## Claim Boundary

- Supported: The first B9 checked-transcript route now has a provenance manifest packet that must bind Lean/Lake source hashes, version transcripts, checked-run transcript hash, returncode, replay hashes, and claim boundary.
- Not supported: No provenance manifest or checked transcript has been submitted or accepted; no proof-assistant checked theorem, Quantum PCP proof, NLTS theorem, or global impossibility theorem is supported.
- Next gate: Submit results/B9_checked_transcript_provenance_manifest_submissions/B9-checked-width-locality-transcript-provenance-manifest.json before the checked transcript priority artifact, then rerun this gate and the priority packet gate.
- proof_assistant_checked: False
- formal_theorem_proved: False
- explicit_not_quantum_pcp_proof: True
- nlts_theorem_claimed: False
- global_gap_amplification_impossibility_claimed: False

## Validation

- validation_error_count: 0
