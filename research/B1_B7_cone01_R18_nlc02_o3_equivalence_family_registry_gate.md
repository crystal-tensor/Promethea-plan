# B1/B7 Cone01 R18 NL-C02 O3 Equivalence-Family Registry Gate

- Target: `T-B1-004dt/T-B7-013c`
- Method: `b1_b7_cone01_r18_nlc02_o3_equivalence_family_registry_gate_v0`
- Status: `cone01_r18_nlc02_o3_equivalence_family_registry_ready_not_full_lemma`
- Candidate: `NL-C02`
- Registry hash: `3a4cd3b08574775d52ee0292e7e5861c968efd0dd281dd04481f6e3da1271eae`
- Family-table hash: `30c9aad9190657f55ed567bb162c4ec653f610ac866380b5c92eeb39671f178f`
- Falsifier-table hash: `08a4dca654af284027cc87b9b2f181094ef96aba506ea20687e3a99d53385faa`

## Result

The R18 O3 registry gate passes 10/10 requirements. It partitions O3 into concrete equivalence-family work items, but it does not close O3.

## Registry Statement

O3 is not closed. The only closed equivalence-family evidence is the Clifford-frame affine sublemma; general symbolic local-unitary reparameterization, numerical refit, and Route A candidate reparameterizations remain open or blocked.

## Equivalence Families

- `O3-F1` identity_and_periodic_pi_complement: covered_by_r14_screen
- `O3-F2` clifford_frame_affine_pi_over_2_periodic_sign: closed_sublemma_by_r16
- `O3-F3` symbolic_local_unitary_reparameterization: open_needs_symbolic_equivalence_argument
- `O3-F4` numerical_coordinate_refit_under_same_unitary: open_needs_adversarial_refit_harness
- `O3-F5` route_a_candidate_reparameterization: blocked_until_route_a_artifact_exists

## Falsifier Targets

- `O3-X1` -> `O3-F3`: valid symbolic local-unitary reparameterization reaches pi/4 lattice while preserving the source unitary
- `O3-X2` -> `O3-F4`: numerical refit finds an equivalent parameterization outside the leave-out table that clears Route A
- `O3-X3` -> `O3-F5`: submitted Route A artifact clears R7/R8 and invalidates the current R17 search-domain boundary

## Decision

- O3 attack surface partitioned: `True`
- O3 closed: `False`
- Closed sublemma count: `2`
- Open family count: `2`
- Blocked family count: `1`
- Falsifier count: `3`
- Checked negative lemma present: `False`
- Reroute allowed: `False`

## Requirement Results

- `I1` PASS: R13 source-domain binding is validation-clean and keeps O3 open
- `I2` PASS: R16 closes the Clifford-frame affine sublemma but not full O3
- `I3` PASS: R17 declares a search-domain boundary and still keeps O3 open
- `I4` PASS: Registry enumerates five equivalence-family rows
- `I5` PASS: Registry has at least two open families and one blocked Route A family
- `I6` PASS: Registry exposes falsifier-ready PR targets
- `I7` PASS: Registry is hash-bound to R13, R16, and R17
- `I8` PASS: Registry explicitly refuses to close full O3
- `I9` PASS: Registry is not upgraded into a checked negative lemma or reroute
- `I10` PASS: Registry preserves zero resource and B7 credit claims

## Claim Boundary

- Supported: R18 partitions O3 into concrete equivalence-family rows and falsifier-ready PR targets. It records that only the Clifford-frame affine sublemma is closed.
- Not supported: R18 does not close general local-unitary invariance, does not make NL-C02 a checked negative lemma, and does not permit R5 reroute. No R1 solution, occurrence removal, proxy-T reduction, B7 credit, resource saving, or impossibility theorem is supported.
- Next gate: Submit an O3-F3 symbolic local-unitary proof/counterexample, an O3-F4 numerical refit harness, or an O3-F5 Route A candidate artifact against the R7/R8 contract.

This registry gate does not claim resource saving, occurrence removal, proxy-T reduction, B7 ledger improvement, FT resource credit, a checked impossibility theorem, an R5 reroute, or a solved B1/B7 problem.

## Validation

- validation_error_count: `0`
