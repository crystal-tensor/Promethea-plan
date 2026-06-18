# B10-T1 Asymptotic Access Contract v0.1

- Status: access_contract_skeleton_sampling_bridge_refuted_for_current_evidence
- Method: b10_t1_asymptotic_access_contract_v0
- Source missing-assumption method: b10_t1_missing_assumption_note_v0
- Family contracts: 2
- Access contract rows: 8
- Bridge conditions: 5
- Sampling-access bridge proved: False
- Sampling-access bridge refuted for current evidence: True
- General dequantization theorem proved: False
- BQP separation claimed: False
- Validation errors: []

## Family Contracts

### F_B3_reaction_derivative_family

- Track: B3
- Family parameter: n = spin-orbital count plus basis/active-space growth
- Observable: finite-difference derivative of molecular energy along a reaction coordinate
- Explicit input contract: A Hamiltonian term list, geometry grid, basis/active-space rule, target derivative error, and classical denominator must be explicitly available.
- Oracle contract: Sparse-Hamiltonian or Pauli-term query access is allowed only if construction and indexing costs are charged.
- Sampling access contract: Sampling access would require a sampler for correlated-state Pauli groups with variance certificates under the same state-preparation and optimizer-loop budget.
- Current portfolio status: finite_instances_only_not_asymptotic_theorem
- Current blocker: B3 one-parameter UCC/ADAPT pressure is demoted and has no multi-parameter covariance rescue.

### F_B5_hubbard_response_family

- Track: B5
- Family parameter: n = lattice sites with U/t, filling, boundary field, and response observable scaling
- Observable: density or boundary-field response in strongly correlated Hubbard-like instances
- Explicit input contract: The lattice, interaction profile, field protocol, response target, tolerance, and denominator solver must be explicit.
- Oracle contract: Local-term oracle access is allowed only when the oracle build, response observable, and precision costs are charged.
- Sampling access contract: Sampling access would require a classical or quantum sampler whose response-estimator variance, mixing/preparation cost, and error propagation are all certified.
- Current portfolio status: finite_d5_pressure_plus_nonproduction_mps
- Current blocker: B5 has strong classical pressure, but the current variational MPS/ALS prototype is not production DMRG.

## Access Contract Matrix

| family | mode | bridge status | equivalence requirement |
|---|---|---|---|
| F_B3_reaction_derivative_family | explicit | specified_for_next_theorem_target | Both sides receive the same explicit Hamiltonian/observable description and tolerance. |
| F_B3_reaction_derivative_family | sparse_or_local_oracle | specified_but_not_instantiated | Both sides receive equivalent term-query access with oracle construction and precision charged. |
| F_B3_reaction_derivative_family | sampling_or_query_access | refuted_for_current_portfolio_evidence | Both sides receive comparable sampling/query access, including preparation, variance, and failure probability. |
| F_B3_reaction_derivative_family | quantum_state_preparation_or_block_encoding | not_positive_ready | Quantum state preparation, block encoding, measurement, and optimizer-loop costs are charged end to end. |
| F_B5_hubbard_response_family | explicit | specified_for_next_theorem_target | Both sides receive the same explicit Hamiltonian/observable description and tolerance. |
| F_B5_hubbard_response_family | sparse_or_local_oracle | specified_but_not_instantiated | Both sides receive equivalent term-query access with oracle construction and precision charged. |
| F_B5_hubbard_response_family | sampling_or_query_access | refuted_for_current_portfolio_evidence | Both sides receive comparable sampling/query access, including preparation, variance, and failure probability. |
| F_B5_hubbard_response_family | quantum_state_preparation_or_block_encoding | not_positive_ready | Quantum state preparation, block encoding, measurement, and optimizer-loop costs are charged end to end. |

## Bridge Conditions

### C1_asymptotic_scaling_law

- Status: defined_as_contract_not_proved
- Current evidence: Two family contracts are now stated, but no all-n scaling theorem is proved.
- Blocks general theorem: True

### C2_equivalent_access_models

- Status: specified_as_contract_not_instantiated
- Current evidence: Explicit, oracle, sampling, and quantum-preparation modes are separated in the matrix.
- Blocks general theorem: True

### C3_sampling_oracle_constructor

- Status: refuted_for_current_portfolio_evidence
- Current evidence: No current B3/B5 artifact constructs comparable sampling/query access; B3 max optimizer-loop shots lower bound is 475043013690000.
- Blocks general theorem: True

### C4_classical_denominator_under_same_contract

- Status: partially_satisfied_for_finite_instances
- Current evidence: B3 selected-CI wins remain 0; B5 variational-over-seeded MPS wins remain 0.
- Blocks general theorem: True

### C5_positive_quantum_kernel_after_full_costs

- Status: refuted_for_current_portfolio_evidence
- Current evidence: B3 demoted = True; B5 positive ready = False; B5 production DMRG = False.
- Blocks general theorem: True

## Theorem Targets

### T1_explicit_input_negative_boundary_contract

- Status: theorem_target_contract_ready_not_proved
- Statement: For explicit B3/B5 inputs, a positive quantum claim must beat the best same-input selected-CI, FCI, tensor/MPS, embedding, or response denominator after state-preparation, measurement, and optimizer costs.

### T2_sampling_access_bridge_failure_current_portfolio

- Status: supported_as_current_evidence_refutation_not_general_impossibility
- Statement: The current B3/B5 portfolio does not instantiate the sampling/query access bridge required to turn the finite denominator pressure into a dequantization or sampling-access theorem.

## Claim Boundary

- sampling_access_bridge_proved: False
- sampling_access_bridge_refuted_for_current_evidence: True
- general_dequantization_theorem_proved: False
- general_sampling_access_theorem_proved: False
- bqp_separation_claimed: False
- quantum_advantage_claimed: False
- what_is_supported: Two asymptotic-family contracts and eight access-contract rows are now explicit. For the current portfolio evidence, the sampling/query access bridge is refuted because no comparable sampling oracle or positive quantum response kernel is instantiated.
- what_is_not_supported: This is not a general dequantization theorem, not a sampling-access theorem, not a BQP separation, and not a quantum advantage result.
