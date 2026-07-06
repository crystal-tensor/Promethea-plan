# B1/B7 Cone01 R22 O3-F3 A6 Claim-Boundary Polarity Gate

- Target: `T-B1-004dx/T-B7-013g`
- Upstream target: `T-B1-004dw/T-B7-013f`
- Method: `b1_b7_cone01_r22_o3_f3_a6_claim_boundary_polarity_gate_v0`
- Status: `cone01_r22_o3_f3_a6_claim_boundary_polarity_ready`
- Candidate: `NL-C02`
- Family: `O3-F3`
- Polarity hash: `3f67889a80141fec568398975029369743b8852b74d928f636e135cb585a0668`
- Polarity rule hash: `c22b841f3111472b7b583bf5caa075f96935408fab8510f2a6362e112d70b608`
- Boundary eval hash: `15946f6def34b3c593644050f259bab04b42bcc2f99dbf4bad822b24139a45e8`

## Result

The R22 A6 claim-boundary polarity gate passes 8/8 requirements. It defines a hardened A6 polarity rule that distinguishes denial language from credit/reroute allowance language.

## What Changed

- Old A6 could pass when a boundary merely mentioned B7 credit, STV credit, or reroute.
- R22 requires denial polarity and rejects allowance polarity.
- The R20 template boundary passes the hardened rule.
- The R21 overclaim boundary fails the hardened rule.

## Polarity Rule

- Required concepts: `['B7 credit', 'STV credit', 'reroute', 'O3 closure']`
- Deny pattern count: `10`
- Allow pattern count: `12`
- Overclaim allow-pattern hits: `['\\bavailable\\b']`

## Requirement Results

- `M1` PASS: R20 intake and R21 sentinel are validation-clean sources
- `M2` PASS: R21 overclaim fixture passed old A6 while still rejected elsewhere
- `M3` PASS: A6 polarity rule names all required credit/reroute/O3 concepts
- `M4` PASS: R20 template boundary passes hardened A6 polarity
- `M5` PASS: R21 overclaim boundary fails hardened A6 polarity
- `M6` PASS: Polarity hardening is diagnostic and does not accept O3-F3
- `M7` PASS: R22 preserves zero B7/resource credit claims
- `M8` PASS: Polarity packet is internally hash-bound

## Claim Boundary

- Supported: R22 defines a hardened A6 claim-boundary polarity rule that passes the R20 no-credit template and fails the R21 overclaim boundary.
- Not supported: R22 does not enforce the rule in R20 yet, does not accept a valid O3-F3 artifact, does not close O3, and does not permit R5 reroute. No R1 solution, occurrence removal, proxy-T reduction, B7 credit, resource saving, or impossibility theorem is supported.
- Next gate: Patch the O3-F3 preflight to use the hardened A6 polarity rule, then rerun R21-style overclaim tests.

This polarity gate does not claim resource saving, occurrence removal, proxy-T reduction, B7 ledger improvement, FT resource credit, a checked impossibility theorem, an R5 reroute, or a solved B1/B7 problem.

## Validation

- validation_error_count: `0`
