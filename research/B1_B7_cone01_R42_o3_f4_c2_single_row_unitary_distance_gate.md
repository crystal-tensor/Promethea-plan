# B1/B7 Cone01 R42 O3-F4 C2 Single-Row Unitary-Distance Gate

- Target: `T-B1-004er/T-B7-014a`
- Upstream target: `T-B1-004eq/T-B7-013z`
- Method: `b1_b7_cone01_r42_o3_f4_c2_single_row_unitary_distance_gate_v0`
- Status: `cone01_r42_o3_f4_c2_single_row_unitary_distance_computed_rejected`
- Fixture hash: `6588f37a519d94058f8b0cffc9698a8aeeb574cb0dea325e79ce8823e5ae58de`
- Evaluation hash: `0fefc6f3c95580ac37aea5e54ff2982058fc5f5676b25f9e8c57098da9468c98`

## Result

R42 passes 8/8 requirements by computing one actual unitary-distance witness while keeping C2 rejected.

## Rejection Surface

- Source-provenance rows passed: `1`
- Witness-schema rows passed: `1`
- Witness-preflight rows passed: `1`
- Unitary-distance rows passed: `1`
- Unitary-distance failures: `7`
- C01 computed unitary distance: `0.0`
- Source-backed rows passed: `0`
- Source-backed flag failures: `8`
- C2 accepted: `False`

## Requirement Results

- `S1` PASS: R41 preflight gate is validation-clean with one preflight row
- `S2` PASS: R42 computes one actual unitary-distance witness
- `S3` PASS: The row keeps provenance, witness schema, and preflight intact
- `S4` PASS: All materialized C2 files remain hash-valid
- `S5` PASS: R42 does not claim source-backed replay or same-unitary acceptance
- `S6` PASS: R42 keeps C2/O3/reroute/B7 zero-credit boundaries
- `S7` PASS: R42 claims no C3-C7 or ledger progress
- `S8` PASS: R42 output is hash-bound

## Claim Boundary

- Supported: R42 computes an actual single-qubit RZ operator-norm unitary distance for one C2 smoke row and binds the witness plus transcript by hash.
- Not supported: R42 does not mark the row source-backed, does not turn the numeric distance into a same-unitary certificate, does not accept C2, does not close O3, and does not permit reroute, B7 credit, STV credit, or resource-saving claims.
- Next gate: Replace smoke flags with real source-backed replay flags only after independent source lineage and replay evidence exist, then replicate provenance, witness, preflight, and unitary distance packets for the remaining 7 rows.

- validation_error_count: `0`
