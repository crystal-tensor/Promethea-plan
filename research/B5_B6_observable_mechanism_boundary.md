# B5/B6 Observable Mechanism Boundary

Status: `b5_b6_observable_mechanism_boundary_synced`

## Summary

- Method: `b5_b6_observable_mechanism_boundary_v0`
- Boundary: `B5-B6-observable-mechanism-boundary`
- Boundary hash: `31c564b89fd0577301932f59eb908f4b3aec6ef5b40d6c0921531869c5a645fb`
- Source acceptance packet: `B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet`
- Source acceptance packet hash: `07ced6bc2f13d167a3107b0bc55d4b58b2f7f928a26104e5d65ca870aa84a2ef`
- Material: `monolayer_FeSe_STO_2012`
- Row replay-validation manifest: `B6B5-O1-monolayer-FeSe-STO-row-replay-validation-manifest`
- Requirements passed/failed: `7` / `0`
- Failed requirement IDs: `[]`
- Source failed acceptance IDs: `['P6', 'P7', 'P8']`
- Denominator records / families / negative controls: `56` / `28` / `18`
- Selected negative controls in top-k: `2`
- Accepted DFT/B5 row count: `0`
- Accepted priority DFT/B5 rows: `0` / `0`
- B5 mechanism / observable / high-Tc / discovery credit allowed: `False` / `False` / `False` / `False`
- validation_error_count: `0`

## Required Downstream Evidence Before B5 Mechanism Credit

- accepted B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet
- source-backed DFT input and output bundle
- source-backed B5 correlation observable table
- same-access cost ledger linking B6 descriptor evidence to B5 observable computation
- negative-control replay preserving the 56-record / 28-family / 18-negative-control denominator
- family-prior denominator result showing the observable route beats the family prior
- claim boundary that still forbids discovery, mechanism-solved, solution, and quantum-advantage claims until rows are accepted

## Requirement Results

- S1 [PASS]: Source B6/B5 observable row acceptance packet gate is present and current
- S2 [PASS]: Source acceptance gate remains blocked on missing submitted packet evidence
- S3 [PASS]: B6/B5 denominator scope remains preserved
- S4 [PASS]: No DFT/B5 observable row has been accepted
- S5 [PASS]: B5 mechanism, observable, material-discovery, and solution credit remain disabled
- S6 [PASS]: Forbidden observable, discovery, mechanism, and solution claims remain absent
- S7 [PASS]: Boundary records downstream evidence required before B5 mechanism credit

## Claim Boundary

- Supported: B5 is now explicitly synchronized to the B6/B5 observable row acceptance packet as a zero-credit mechanism boundary.
- Not supported: No accepted DFT row, B5 computed observable row, high-Tc mechanism, material discovery, mechanism solution, or B5 mechanism credit is supported.
- Next gate: Submit and accept the B6/B5 observable row acceptance packet with source-backed DFT, B5 correlation observable, negative-control replay, family-prior denominator, same-access ledger, and claim boundary before B5 mechanism credit can count.
- b5_mechanism_credit_allowed: False
- b5_computed_observable_credit_allowed: False
- high_tc_mechanism_credit_allowed: False
- material_discovery_credit_allowed: False

## Validation

- validation_error_count: 0
