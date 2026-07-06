# B1/B7 Cone01 R9 R1 Reroute-Pressure Gate

- Target: `T-B1-004dk/T-B7-012t`
- Method: `b1_b7_cone01_r9_r1_reroute_pressure_gate_v0`
- Status: `cone01_r9_r1_reroute_pressure_not_checked_negative_lemma`
- Pressure packet: `B1-B7-cone01-R9-R1-reroute-pressure`
- Pressure hash: `6d91bce5a09c4407ef9d7bcac0a81a5983c186dc23b3c98edb1a91b4a4ef4505`
- R8 preflight hash: `e6d5be7ca79021780009f91fd17df8ec206db924e6d402c12472aa854bbac977`

## Result

The R9 reroute-pressure gate passes 8/8 requirements. It aggregates negative pressure against the current R1 route, but does not upgrade that pressure into a checked negative lemma or an R5 reroute.

## Pressure Evidence

- Leave-out parameter removal families / rows / exact passes: `5` / `31` / `0`
- Context widths tested: `[1, 2, 3, 4, 5]`
- Width-5 virtual tests: `173761280`
- Total context exact absorption parameter count: `0`
- Best context grid error: `0.001581991109333103`
- Commutation-corridor accepted candidates: `0`
- Physical cost-minus-credit: `365`

## Reroute Decision

- Reroute allowed: `False`
- Checked negative lemma present: `False`
- Why not reroute yet: The current evidence rejects many concrete R1 subroutes, but it is not a checked negative lemma covering all R1 parameter-elimination, absorption, symbolic, and physical-pricing possibilities.

## Next Gate

Submit a checked negative lemma artifact that binds these source hashes and states the covered R1 search domain, or submit a new R1 artifact that clears R8 Route A or Route B.

## Requirement Results

- `N1` PASS: R8 preflight rejects both R1 contract routes
- `N2` PASS: Leave-out parameter removal pressure covers all nonempty removal sizes
- `N3` PASS: Simple exact decomposition/source absorption accepts none of the five parameters
- `N4` PASS: Context absorption pressure covers widths one through five with zero exact absorptions
- `N5` PASS: Commutation-corridor pressure accepts no replay-safe candidate
- `N6` PASS: Physical pricing still misses Route B by 365
- `N7` PASS: All pressure sources are hash-bound and validation-clean
- `N8` PASS: Pressure is not upgraded into a checked negative lemma or reroute decision

## Claim Boundary

- Supported: R9 aggregates hash-bound R1 negative-pressure evidence and shows why a checked negative lemma would be valuable.
- Not supported: No checked negative lemma, R5 reroute, submitted R1 solution, occurrence removal, proxy-T reduction, B7 credit, resource saving, or impossibility theorem is supported.
- Next gate: Submit a checked negative lemma artifact that binds these source hashes and states the covered R1 search domain, or submit a new R1 artifact that clears R8 Route A or Route B.

This reroute-pressure gate does not claim resource saving, occurrence removal, proxy-T reduction, B7 ledger improvement, FT resource credit, a checked impossibility theorem, an R5 reroute, or a solved B1/B7 problem.

## Validation

- validation_error_count: `0`
