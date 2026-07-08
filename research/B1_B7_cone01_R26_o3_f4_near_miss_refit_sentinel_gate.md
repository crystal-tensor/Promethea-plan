# B1/B7 Cone01 R26 O3-F4 Near-Miss Refit Sentinel Gate

- Target: `T-B1-004eb/T-B7-013k`
- Upstream target: `T-B1-004ea/T-B7-013j`
- Method: `b1_b7_cone01_r26_o3_f4_near_miss_refit_sentinel_gate_v0`
- Status: `cone01_r26_o3_f4_near_miss_refit_sentinel_rejected`
- Sentinel hash: `bb93711b3b2dc2a8b73ded6536e56ad14357eeb544029bd65a7c6b18a751add3`
- Near-miss fixture hash: `a239097cd2ca844d616829a141a6490e74285f8af16fee506c70088125d43873`
- Preflight hash: `c49cb7c1b54fa079266a6b6dc11d0c13b7d575f1a6f202057bd9b9fd30c9aaa5`

## Result

R26 passes 10/10 requirements. It rejects a stronger near-miss O3-F4 fixture that passes more gates than R25.

## Rejection Profile

- Passed gates: `['F4-A1', 'F4-A3', 'F4-A4', 'F4-A8', 'F4-A9']`
- Failed gates: `['F4-A2', 'F4-A5', 'F4-A6', 'F4-A7']`
- Max unitary replay error: `1.8000000000000002e-08`
- Unit tolerance: `1e-08`

## Requirement Results

- `S1` PASS: R24 harness and R25 sentinel are validation-clean sources
- `S2` PASS: Near-miss fixture carries all required O3-F4 fields
- `S3` PASS: Near-miss fixture passes more gates than R25
- `S4` PASS: Near-miss fixture passes source, seed, Route A, claim-boundary, and machine-check surface gates
- `S5` PASS: Same-unitary replay remains rejected despite near tolerance
- `S6` PASS: Certificate, denominator, and leakage core gates reject the fixture
- `S7` PASS: Failed gate set is exactly the stronger near-miss profile
- `S8` PASS: R26 rejects the fixture without accepting O3-F4, closing O3, or permitting reroute
- `S9` PASS: R26 preserves zero B7/resource credit claims
- `S10` PASS: Sentinel packet is internally hash-bound

## Claim Boundary

- Supported: R26 emits a stronger near-miss O3-F4 refit fixture that passes surface gates but is rejected by same-unitary, certificate, denominator, and leakage gates.
- Not supported: R26 does not submit or accept a valid O3-F4 refit artifact, does not close O3, and does not permit R5 reroute. No B7 credit or resource saving is supported.
- Next gate: Submit a valid O3-F4 refit artifact that passes F4-A1..F4-A9, or design an even stronger adversarial fixture.

- validation_error_count: `0`
