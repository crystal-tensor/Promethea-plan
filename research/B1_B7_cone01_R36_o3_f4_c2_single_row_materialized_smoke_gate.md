# B1/B7 Cone01 R36 O3-F4 C2 Single-Row Materialized Smoke Gate

- Target: `T-B1-004el/T-B7-013u`
- Upstream target: `T-B1-004ek/T-B7-013t`
- Method: `b1_b7_cone01_r36_o3_f4_c2_single_row_materialized_smoke_gate_v0`
- Status: `cone01_r36_o3_f4_c2_single_row_materialized_smoke_partial`
- Fixture hash: `6565d611d2b0ca01af2de0c73054b765278f450e60f6ad35107fef0ddacb0144`
- Preflight hash: `7a5d901ba75e0bc9f1d7d06d8530a4a08ea3a93f70afb8711c8143a925437042`

## Result

R36 passes 8/8 requirements by materializing one hash-matched smoke row while rejecting the incomplete 8-row C2 bundle.

## Rejection Surface

- Surface rows passed / failed: `8` / `0`
- Materialized rows passed / failed: `1` / `7`
- Smoke materialized row IDs: `['O3-F4-C01']`
- Missing materialized files: `28`
- C2 accepted: `False`

## Requirement Results

- `S1` PASS: R35 source sentinel is validation-clean and blocks missing files
- `S2` PASS: R36 materializes exactly one smoke row with hash-matched files
- `S3` PASS: All 8 rows still pass the metadata surface
- `S4` PASS: Incomplete materialization rejects C2 acceptance
- `S5` PASS: Materialized smoke row is explicitly not promoted to same-unitary proof
- `S6` PASS: Fixture and preflight are hash-bound
- `S7` PASS: R36 preserves zero-credit B1/B7 boundaries
- `S8` PASS: R36 remains scoped to materialization plumbing and claims no C3-C7 progress

## Claim Boundary

- Supported: R36 materializes one hash-matched smoke row and proves the materialization verifier can distinguish one real file bundle from seven missing rows.
- Not supported: R36 does not accept C2, does not provide a source-backed same-unitary certificate, does not close O3, and does not permit reroute, B7 credit, STV credit, or resource-saving claims.
- Next gate: Replace the smoke row with source-backed replay outputs and materialize the remaining seven C2 rows before rerunning C2/C3-C7.

- validation_error_count: `0`
