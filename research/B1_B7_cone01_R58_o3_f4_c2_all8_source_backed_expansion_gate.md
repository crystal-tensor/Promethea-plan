# B1/B7 Cone01 R58 O3-F4 C2 All-8 Source-Backed Expansion Gate

- Target: `T-B1-004fh/T-B7-014q`
- Upstream target: `T-B1-004fg/T-B7-014p`
- Method: `b1_b7_cone01_r58_o3_f4_c2_all8_source_backed_expansion_gate_v0`
- Status: `cone01_r58_o3_f4_c2_all8_source_backed_rows_accepted_zero_b7_credit`
- R58 fixture hash: `d0d637b0c262f29dc0665ee0c33fe4a115cb774effe946cce6d65353376431b4`
- R58 evaluation hash: `fe7faded3f89bebd0a55d83ad273cf2925fcfcb6b314d47dac06f9fc4403f77d`
- Discriminator hash: `9545943101fea7807122aa36c6c048dc742fce6af761c5229cd69b899b4cc99a`

## Result

R58 passes 8/8 requirements by expanding the R47/R38 source-backed discriminator from exactly one row to all 8 rows. C3-C7, O3 closure, reroute, and B7 ledger credit remain blocked.

## R47/R38 Evidence

- Row count: `8` / required `8`
- Source-backed rows passed: `8`
- Source-backed flag failures: `0`
- Source provenance failures: `0`
- Witness schema failures: `0`
- Binding mismatch count: `0`
- R47 all-8 rows accepted: `True`
- C2 strict replay rows accepted: `True`
- B7 credit delta: `0`

## Requirement Results

- `S1` PASS: R57 upstream accepted exactly one source-backed row and left all-8 scaling open
- `S2` PASS: R58 creates 8 source-backed evidence packets with same-unitary certificates
- `S3` PASS: R58 fixture contains 8 rows and is bound to the unchanged R38 replacement contract
- `S4` PASS: Every row passes materialized files, binding, replay tolerance, flags, source provenance, witness schema, and zero-credit boundary
- `S5` PASS: R47/R38 all-8 discriminator accepts the R58 fixture under the required row count
- `S6` PASS: R58 promotes C2 row-level strict replay only, with no O3/reroute/B7/STV/resource credit
- `S7` PASS: R58 leaves C3-C7 and B7 ledger retest as open obligations
- `S8` PASS: R58 fixture, evaluation, and evidence rows are hash-bound

## Claim Boundary

- Supported: R58 generates source-backed replay evidence for all 8 O3-F4 rows and passes the unchanged R47/R38 all-row discriminator under strict tolerance.
- Not supported: R58 does not close O3, does not prove a theorem-level same-unitary replay certificate beyond the single-qubit RZ check, does not permit reroute, and does not grant B7/STV/resource/ledger credit.
- Next gate: Run C3 same-unitary replay certificate pressure, then C4/C5 denominator, C6 leakage-free trace, C7 machine-check bundle, and only then B7 ledger retest.

## Remaining Open Obligations

- `C3_same_unitary_replay_certificate`
- `C4_C5_same_access_denominator_comparison`
- `C6_leakage_free_optimizer_trace`
- `C7_machine_check_replay_bundle`
- `B7_ledger_retest_after_full_C2_closure`

- validation_error_count: `0`
