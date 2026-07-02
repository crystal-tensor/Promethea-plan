# B6/B5 Observable Priority Packet Gate

Status: **observable_priority_packet_open_missing_artifact**

## Summary

- Method: `b6_b5_observable_priority_packet_gate_v0`
- Model status: `priority_dft_b5_observable_packet_ready_no_rows_submitted`
- Priority material: `monolayer_FeSe_STO_2012`
- Packet hash: `042ad8fefae63f62f11cd575bee8d1472664d080152c1cd78f8b58b68070cd4d`
- Requirements passed/failed: 6 / 3
- Failed requirement IDs: ['P6', 'P7', 'P8']
- DFT/B5 required key counts: 11 / 11
- Combined schema keys: 22
- Required evidence file classes: 10
- Submitted artifact exists: False
- Accepted priority DFT/B5 rows: 0 / 0

## Submission Packet

- Submission path: `results/B6_B5_observable_priority_submissions/monolayer_FeSe_STO_2012.json`
- Rank / family: 1 / iron_chalcogenide
- Template hash: `6509e5e23825f69e18d60cf78f678a2d312c8b107c5983c28d6282e85ec8bf81`

Required evidence files:

- structure_reference_or_cif
- dft_input_manifest
- dft_output_or_parser_log
- dft_calculation_hash_source
- effective_model_derivation_note
- b5_solver_trace_artifact
- same_access_cost_ledger
- observable_join_key_audit
- source_replay_hash_manifest
- claim_boundary_note

Acceptance predicates:

- dft_row contains all 11 DFT keys
- b5_row contains all 11 B5-computed observable keys
- material_id matches the rank-1 intake template
- source_table_hash, replay_formula_hash, and replay_table_hash are preserved
- DFT calculation_hash and B5 solver_trace_hash bind source artifacts
- same_access_cost_units is present for the B5 row
- claim_boundary forbids material discovery, mechanism-solved, and solution claims

## DFT Row Schema

material_id, structure_ref, functional, pseudopotential_or_basis, kpoint_density, energy_per_atom_ev, fermi_level_ev, density_of_states_at_fermi, magnetic_moment_mu_b, relaxation_status, calculation_hash

## B5 Row Schema

material_id, effective_model, orbital_basis, interaction_u_ev, hopping_t_ev, filling, response_observable, response_value, denominator_method, solver_trace_hash, same_access_cost_units

## Requirement Results

- P1 [PASS]: Observable intake template remains valid and open on DFT/B5 rows
- P2 [PASS]: Priority material is fixed to the rank-1 top-post replay template
- P3 [PASS]: Priority packet carries both 11-key observable schemas
- P4 [PASS]: Packet binds required source evidence classes
- P5 [PASS]: Source, formula, replay, and schema hashes are preserved from intake
- P6 [FAIL]: Priority observable artifact has been submitted
- P7 [FAIL]: Submitted artifact satisfies both locked observable schemas
- P8 [FAIL]: Submitted rows are source-backed and preserve replay hashes
- P9 [PASS]: Forbidden observable, discovery, mechanism, and solution claims remain false

## Claim Boundary

- Supported: The first B6/B5 observable blocker now has a concrete source-backed submission packet for a paired DFT and B5-computed observable row.
- Not supported: No DFT row or B5-computed observable row has been submitted or accepted; no material discovery, high-Tc mechanism solution, or B6 solution claim is supported.
- Next gate: Submit results/B6_B5_observable_priority_submissions/monolayer_FeSe_STO_2012.json with dft_row and b5_row blocks satisfying all 22 combined schema keys while preserving source/replay hashes.
- material_discovery_claimed: False
- mechanism_solved: False
- solution_claimed: False

## Validation

- validation_error_count: 0
