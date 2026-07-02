# B6/B5 Observable Row Acceptance Packet Gate

Status: `observable_row_acceptance_packet_open_missing_artifact`

## Summary

- Method: `b6_b5_observable_row_acceptance_packet_gate_v0`
- Acceptance packet: `B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet`
- Priority material: `monolayer_FeSe_STO_2012`
- Row replay-validation manifest: `B6B5-O1-monolayer-FeSe-STO-row-replay-validation-manifest`
- Row replay-validation hash: `16fecc141f05a7b641e1d10009b1c0c2bb8e62927aa0a4d01360cef563a2edfb`
- Acceptance packet hash: `07ced6bc2f13d167a3107b0bc55d4b58b2f7f928a26104e5d65ca870aa84a2ef`
- Requirements passed/failed: `6` / `3`
- Failed requirement IDs: `['P6', 'P7', 'P8']`
- Required key / production key / evidence file count: `28` / `19` / `17`
- Replay scope records/families/negative controls: `56` / `28` / `18`
- Template rows / negative controls in top-k: `12` / `2`
- Submitted acceptance packet exists: `False`
- Accepted DFT/B5 row count: `0`
- validation_error_count: `0`

## Acceptance Packet

- Submission path: `results/B6_B5_observable_row_acceptance_packet_submissions/B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet.json`

Required evidence files:

- accepted_row_replay_validation_manifest
- priority_observable_packet
- accepted_provenance_manifest
- accepted_replay_validation_manifest
- source_formula_manifest
- structure_input_artifact
- dft_input_deck_manifest
- dft_output_bundle
- observable_table
- b5_correlation_observable_table
- negative_control_replay_table
- leakage_guardrail_report
- family_prior_denominator_table
- same_access_cost_ledger
- row_acceptance_ledger
- b5_mechanism_boundary_note
- claim_boundary_note

Acceptance predicates:

- acceptance_packet_id equals B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet
- material, provenance, replay-validation, row-replay-validation, and priority packet hashes match the source gates
- source formula, structure input, DFT input/output, observable table, B5 correlation observable, negative-control replay, leakage guardrail, family-prior denominator, same-access ledger, and row acceptance ledger are hash-bound
- accepted_dft_b5_row_count is positive only after the paired DFT/B5 row is source-backed and row-valid
- top_post_rank, negative-control top-k count, family count, and source-record count preserve the 56-record / 28-family / 18-negative-control denominator
- B5 mechanism boundary explicitly denies B5 mechanism, high-Tc mechanism, and quantum-advantage claims
- claim_boundary forbids DFT-observable, B5-observable, material-discovery, mechanism-solved, and solution claims until audited rows are accepted

## Requirement Results

- P1 [PASS]: Row replay-validation manifest gate remains valid and blocked only on P6/P7/P8
- P2 [PASS]: Priority observable packet remains fixed and source-shaped
- P3 [PASS]: Acceptance packet carries locked DFT/B5 observable row schema and evidence classes
- P4 [PASS]: Replay scope, template table, and negative-control denominator remain preserved
- P5 [PASS]: Current state has no accepted DFT/B5 observable rows and no discovery claim
- P6 [FAIL]: Observable row acceptance packet has been submitted
- P7 [FAIL]: Submitted acceptance packet satisfies the locked DFT/B5 observable row schema
- P8 [FAIL]: Submitted acceptance packet is source-backed, manifest-bound, row-valid, B5-boundary-bound, and claim-boundary-bound
- P9 [PASS]: Forbidden observable, discovery, mechanism, and solution claims remain false

## Claim Boundary

- Supported: The rank-1 B6/B5 observable route now has an acceptance packet gate after row replay-validation and before any paired DFT/B5 observable row can count.
- Not supported: No acceptance packet, DFT row, or B5-computed observable row has been submitted or accepted; no material discovery, mechanism-solved, observable, quantum advantage, or solution claim is supported.
- Next gate: Submit B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet with source formula, structure input, DFT input/output, observable table, B5 correlation observable, negative-control replay, leakage guardrail, family-prior denominator, same-access ledger, row acceptance ledger, B5 mechanism boundary, and claim boundary.
- accepted_dft_b5_row_count: 0
- accepted_priority_dft_rows: 0
- accepted_priority_b5_rows: 0
- dft_observable_claimed: False
- b5_computed_observable_claimed: False
- material_discovery_claimed: False
- mechanism_solved: False
- solution_claimed: False

## Validation

- validation_error_count: 0
