# B1/B7 Cone01 R59 O3-F4 C3 Same-Unitary Replay Certificate Gate

- Target: `T-B1-004fi/T-B7-014r`
- Upstream target: `T-B1-004fh/T-B7-014q`
- Method: `b1_b7_cone01_r59_o3_f4_c3_same_unitary_replay_certificate_gate_v0`
- Status: `cone01_r59_o3_f4_c3_same_unitary_replay_certificate_passed_zero_b7_credit`
- R59 bundle hash: `fa7ab308e09644f3d58228a92ea580fb40f6ea88b8408cc75ddc21df79b84cbb`

## Result

R59 passes 8/8 requirements by replay-certifying all 8 R58 source-backed rows and rejecting all 8 negative-control perturbations. C4/C5, C6, C7, O3 closure, reroute, and B7 ledger credit remain blocked.

## C3 Evidence

- Row count: `8`
- Positive replay passed: `8`
- Negative controls rejected: `8`
- Evidence packet semantic hash matches: `8`
- Evidence packet stale file-SHA observations: `8`
- Max positive replay distance: `0.0`
- Min negative-control distance: `0.015624841054765663`
- C3 replay certificate complete: `True`
- B7 credit delta: `0`

## Requirement Results

- `S1` PASS: R58 upstream accepted all 8 C2 source-backed discriminator rows with zero B7 credit
- `S2` PASS: R59 parses exactly one OpenQASM 3.0 RZ angle for each source and candidate row
- `S3` PASS: All critical R58-bound files hash-match and evidence packets remain semantically bound
- `S4` PASS: Positive same-unitary replay certificates pass for all 8 rows
- `S5` PASS: Negative-control perturbations are rejected for all 8 rows
- `S6` PASS: R59 completes the restricted C3 replay certificate without promoting O3/reroute/B7 credit
- `S7` PASS: R59 leaves C4/C5, C6, C7, and B7 ledger retest open
- `S8` PASS: R59 bundle and per-row certificates are hash-bound

## Claim Boundary

- Supported: R59 completes the restricted C3 same-unitary replay certificate for the 8 O3-F4 single-qubit RZ rows accepted by R58, adds negative-control perturbations that the verifier rejects, and normalizes the observed R58 evidence-packet file-SHA staleness by rebinding actual file hashes.
- Not supported: R59 does not prove a global O3 theorem, does not compare against a same-access denominator, does not audit leakage, does not produce a machine-check replay bundle, and does not grant reroute or B7/STV credit.
- Next gate: Run C4/C5 same-access denominator comparison before C6 leakage-free trace, C7 machine-check bundle, or any B7 ledger retest.

## Remaining Open Obligations

- `C4_C5_same_access_denominator_comparison`
- `C6_leakage_free_optimizer_trace`
- `C7_machine_check_replay_bundle`
- `B7_ledger_retest_after_C4_C7`

- validation_error_count: `0`
