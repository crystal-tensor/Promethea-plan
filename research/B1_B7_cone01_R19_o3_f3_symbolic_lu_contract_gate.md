# B1/B7 Cone01 R19 O3-F3 Symbolic Local-Unitary Contract Gate

- Target: `T-B1-004du/T-B7-013d`
- Method: `b1_b7_cone01_r19_o3_f3_symbolic_lu_contract_gate_v0`
- Status: `cone01_r19_o3_f3_symbolic_lu_contract_ready_not_submitted`
- Candidate: `NL-C02`
- Family: `O3-F3`
- Contract hash: `d7b0e3fdac82bde9c3c312e9294ed2f80feb46b90d0bc167083d2ad408954f9f`
- Required-field table hash: `ba37ed01483992f1732dea047f5533b499c40fcbc0973357e9cce025d925674a`
- Acceptance-gate table hash: `1e2c310ab096c52b3a58f62481d2ea5788b62971ebaea770f7e9e06e6732ad96`
- Rejection-rule hash: `0bdee678ace47847a1eda0a8fa090685324ccc466614bc36ee5aeca1f1a06efc`

## Result

The R19 O3-F3 contract gate passes 10/10 requirements. It prepares a strict symbolic local-unitary submission contract, but no O3-F3 artifact is submitted or accepted.

## Required Fields

- `artifact_id`: stable artifact identifier for the symbolic local-unitary proof or counterexample
- `source_target_id`: must cite T-B1-004du/T-B7-013d or descendant
- `family_id`: must equal O3-F3
- `candidate_id`: must equal NL-C02
- `source_registry_hash`: must equal the R18 registry hash consumed by this contract
- `symbolic_transform_definition`: defines the local-unitary coordinate transformation with domains and codomains
- `source_unitary_preservation_certificate`: proves or checks that the transformed coordinates preserve the source local unitary
- `leaveout_domain_mapping`: maps the transformed coordinates back to the R13/R17 leave-out domain or explains the escape
- `pi_over_four_lattice_relation`: states whether the transform preserves, reaches, or escapes the pi/4 lattice
- `route_a_effect`: states whether the artifact clears Route A against the R7/R8 contract
- `counterexample_payload`: required when claiming a falsifier; contains exact symbolic values or a replayable construction
- `claim_boundary`: states what is supported, not supported, and what would kill the result
- `machine_check_command`: command that reproduces the proof check, symbolic replay, or counterexample verification
- `expected_outputs`: hashes or exact outputs for the checker result

## Acceptance Gates

- `A1` family_and_source_binding: family_id == O3-F3 and source_registry_hash matches R18 registry_hash
- `A2` local_unitary_preservation: source_unitary_preservation_certificate is present and machine-checkable
- `A3` domain_mapping: leaveout_domain_mapping covers the five R13 line1381 parameters or gives an explicit escape
- `A4` lattice_relation: pi_over_four_lattice_relation is symbolic, replayable, and not only numerical
- `A5` route_a_effect: Route A impact is explicitly positive, negative, or not claimed
- `A6` claim_boundary: artifact refuses B7 credit unless Route A/B and resource ledgers are accepted
- `A7` checker_replay: machine_check_command reproduces expected_outputs
- `A8` no_silent_upgrade: artifact does not set checked_negative_lemma_present or reroute_allowed without all acceptance gates

## Rejection Rules

- Reject if the transform is only a numerical fit without a symbolic local-unitary preservation certificate.
- Reject if the artifact reaches the pi/4 lattice but does not preserve the source local unitary.
- Reject if the artifact claims B7 credit before an accepted Route A/B artifact and refreshed B7 ledger replay.
- Reject if the artifact silently changes the R13 five-parameter source domain.
- Reject if the machine-check command is missing, nondeterministic, or not hash-bound.

## Decision

- O3-F3 contract ready: `True`
- O3-F3 artifact submitted: `False`
- O3-F3 accepted: `False`
- O3 closed: `False`
- Checked negative lemma present: `False`
- Reroute allowed: `False`

## Requirement Results

- `J1` PASS: R18 registry is validation-clean and keeps O3-F3 open
- `J2` PASS: R18 exposes the O3-X1 falsifier target for O3-F3
- `J3` PASS: Contract defines fourteen required submission fields
- `J4` PASS: Contract defines eight acceptance gates
- `J5` PASS: Contract defines explicit rejection rules for overclaims
- `J6` PASS: Artifact template is bound to O3-F3 and the R18 registry hash
- `J7` PASS: Contract is hash-bound to the R18 registry and internal tables
- `J8` PASS: No O3-F3 artifact is silently accepted
- `J9` PASS: Contract does not close O3 or allow reroute
- `J10` PASS: Contract preserves zero resource and B7 credit claims

## Claim Boundary

- Supported: R19 creates a strict submission contract for O3-F3 symbolic local-unitary proof or counterexample artifacts.
- Not supported: R19 does not submit or accept an O3-F3 artifact, does not close O3, and does not permit R5 reroute. No R1 solution, occurrence removal, proxy-T reduction, B7 credit, resource saving, or impossibility theorem is supported.
- Next gate: Submit an O3-F3 artifact satisfying the fourteen required fields and eight acceptance gates, or move to O3-F4/O3-F5 under the R18 registry.

This contract gate does not claim resource saving, occurrence removal, proxy-T reduction, B7 ledger improvement, FT resource credit, a checked impossibility theorem, an R5 reroute, or a solved B1/B7 problem.

## Validation

- validation_error_count: `0`
