# B1/B7 Cone01 R39 O3-F4 C2 Single-Row Source-Provenance Gate

- Target: `T-B1-004eo/T-B7-013x`
- Upstream target: `T-B1-004en/T-B7-013w`
- Method: `b1_b7_cone01_r39_o3_f4_c2_single_row_source_provenance_gate_v0`
- Status: `cone01_r39_o3_f4_c2_single_row_source_provenance_partial_rejected`
- Fixture hash: `4b448b8e5e8879bb8e04bc7928a3091188a51b754a15fb624c042320ad81d357`
- Evaluation hash: `6f7d781074ac6f195f8a7c69995f9f5996b6f5ec627e573522e5073aabf04c29`

## Result

R39 passes 8/8 requirements by adding source provenance for one row while keeping C2 rejected.

## Rejection Surface

- Materialized rows passed: `8`
- Source-provenance rows passed: `1`
- Source-provenance failures: `7`
- Source-backed rows passed: `0`
- Source-backed flag failures: `8`
- Witness schema failures: `8`
- C2 accepted: `False`

## Requirement Results

- `S1` PASS: R38 source-backed discriminator is validation-clean and rejects smoke rows
- `S2` PASS: R39 emits source dataset, trace, and replay-environment files for one row
- `S3` PASS: All materialized C2 files remain hash-valid
- `S4` PASS: The enriched row is still not accepted without source-backed replay flags
- `S5` PASS: Same-unitary witness schema and verifier remain missing
- `S6` PASS: R39 keeps C2/O3/reroute/B7 zero-credit boundaries
- `S7` PASS: R39 claims no C3-C7 or ledger progress
- `S8` PASS: R39 output is hash-bound

## Claim Boundary

- Supported: R39 adds hash-verifiable source dataset, source trace, and replay environment files for one C2 row, reducing source-provenance failures from 8 to 7.
- Not supported: R39 does not mark the row source-backed, does not provide an accepted same-unitary witness schema/verifier, does not accept C2, does not close O3, and does not permit reroute, B7 credit, STV credit, or resource-saving claims.
- Next gate: Add real source-backed replay flags and a same-unitary witness schema/verifier for the enriched row, then repeat source-provenance packets for the remaining 7 rows.

- validation_error_count: `0`
