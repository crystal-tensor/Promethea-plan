# B10 Formal Theorem Targets v0.1

Last updated: 2026-06-13

Status: **formal_theorem_targets_not_proofs**

## Summary

- Source result: B10_bqp_boundary_graph_v0
- Method: bqp_boundary_formal_theorem_targets_v0
- Target count: 2
- Target types: ['negative_boundary', 'restricted_advantage_preservation']
- Cross-B dependencies: ['B10', 'B3', 'B4', 'B5', 'B8']
- Validation errors: 0

## B10-T1: linear_systems_data_loading_negative_boundary

- Type: negative_boundary
- Source graph target: `phase_estimation_observables__to__linear_systems_hhl_negative_boundary`
- Status: formal_model_ready_not_proved
- Informal claim: An HHL-style exponential speedup claim collapses to at most a polynomial or undefined advantage when state preparation, block encoding, condition-number control, and output readout are charged explicitly.
- Dependencies: ['B3', 'B5', 'B10']
- Failure modes controlled: ['data_loading', 'condition_number', 'readout', 'dequantization']

### Input Model

- Instance: Sparse or block-encoded linear system Ax=b with n-dimensional solution vector x.
- Access: Classical sparse-row oracle or explicit sparse matrix description for A.
- Access: State-preparation procedure P_b for |b> with declared cost C_prep.
- Access: Block-encoding or Hamiltonian simulation oracle U_A with declared cost C_block.
- Access: Observable family O_1..O_m whose expectation values on |x> are the requested outputs.
- Cost accounting: C_prep is included in the quantum runtime.
- Cost accounting: C_block is included per query or simulation segment.
- Cost accounting: Condition number kappa and target precision epsilon are explicit parameters.
- Cost accounting: Readout cost scales with the number and precision of requested observables.

### Promise

- A is Hermitian or embedded into a Hermitian block matrix with spectral norm <= 1.
- Nonzero singular values of A are in [1/kappa, 1].
- P_b prepares a state within trace distance eta_prep of |b>.
- Each requested observable has operator norm <= 1.
- The output is not the full vector x unless full readout cost is paid.

### Output Model

- accepted_output: Estimates of m observable expectations <x|O_j|x> within additive error epsilon.
- rejected_output: A claim of full-vector recovery without O(n) or equivalent readout cost.
- success_probability: At least 2/3, boostable by standard repetition or amplitude-estimation schedules.

### Verifier Model

- Input: Classical description of A or sparse-row oracle access.
- Input: Classical descriptions of O_j.
- Input: Declared costs C_prep, C_block, kappa, epsilon, eta_prep, m.
- Check: Reject if C_prep or C_block is hidden inside an oracle and not charged.
- Check: Reject if kappa or 1/epsilon grows fast enough to erase the claimed speedup.
- Check: Reject if m or requested output dimension implies full readout.
- Check: Compare against classical iterative or sampling baselines at the same observable precision.

### Proof Obligations

- State a theorem bounding end-to-end quantum runtime in terms of C_prep, C_block, kappa, epsilon, and m.
- State a negative corollary showing that if C_prep + C_block + readout is Omega(n) or worse, exponential speedup cannot be claimed for full-output tasks.
- List classical baselines and denominator metrics before any advantage claim.

## B10-T2: sampling_advantage_verification_layer_target

- Type: restricted_advantage_preservation
- Source graph target: `random_circuit_sampling__to__interactive_verification`
- Status: formal_model_ready_not_proved
- Informal claim: A sampling-advantage task can retain a restricted advantage claim after adding a classical verification layer only if the verifier's challenge refresh and leakage budget keep adaptive spoofing soundness below an explicit threshold.
- Dependencies: ['B4', 'B8', 'B10']
- Failure modes controlled: ['verification', 'protocol_overhead', 'noise', 'adaptive_leakage']

### Input Model

- Instance: Distribution-sampling circuit family C_n plus hidden verifier challenges generated after or independently of the prover's sampling strategy.
- Access: Classical circuit descriptions for C_n.
- Access: Verifier challenge generator G_chal with public parameters and hidden seed.
- Access: A leakage channel L exposing a bounded fraction lambda of hidden challenge information.
- Access: A finite adversary class A or a formally specified adaptive spoofing model.
- Cost accounting: Verifier runtime and sample count are included.
- Cost accounting: Challenge refresh/projection rotation overhead is included.
- Cost accounting: Soundness is reported against the declared leakage fraction lambda.

### Promise

- Honest quantum samples pass the verifier with completeness at least c.
- Adaptive classical spoofers receive at most lambda leakage about hidden challenges.
- The verifier uses refresh or projection rotation so repeated transcripts do not reveal a fixed invariant too quickly.
- The task's sampling hardness assumption is stated separately from the verifier's property test.

### Output Model

- accepted_output: A transcript, pass/fail decision, empirical completeness, and empirical or proven soundness bound.
- rejected_output: A sampling-advantage claim based only on an easily inferred invariant or unrefreshed trap.
- success_probability: Completeness >= c and adaptive-spoofer soundness <= s for declared lambda.

### Verifier Model

- Input: Circuit family C_n.
- Input: Challenge generator G_chal.
- Input: Leakage budget lambda.
- Input: Completeness threshold c and soundness threshold s.
- Input: Adversary family or reduction assumptions.
- Check: Reject if no leakage budget is declared.
- Check: Reject if the verifier's hidden invariant is fixed across too many trials.
- Check: Require a challenge-refresh or projection-rotation schedule.
- Check: Report empirical stress-test curves from B8 before using the target in B4.

### Proof Obligations

- Define a theorem relating leakage fraction lambda, refresh schedule, sample count, and soundness s.
- Prove or empirically bound the adaptive-spoofer pass probability for the declared adversary class.
- Separate sampling hardness assumptions from verifier soundness assumptions.

## Limits

- These are theorem-target specifications, not proved theorems.
- Each target is designed to prevent overclaiming by making input, promise, output, verifier, and cost assumptions explicit.
- The next step is to prove at least one restricted theorem or negative lemma, or to record a failed proof attempt as a B9/B10 guardrail.
