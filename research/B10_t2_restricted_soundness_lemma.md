# B10-T2 Restricted Refresh-Independence Soundness Lemma v0.1

Last updated: 2026-06-17

Status: **restricted_soundness_lemma_proved_under_refresh_independence_model**

## Summary

- Source target: B10-T2 / sampling_advantage_verification_layer_target
- Method: b10_t2_restricted_soundness_lemma_v0
- Source gate: b10_t2_refresh_proof_obligation_gate_v0
- Source B8 stress: b8_generative_spoofer_refresh_v0
- Explicitly not a BQP separation: True
- Hardware randomized-measurement circuits instantiated: False
- Sampling hardness proved: False
- Verifier samples: 4096
- Minimum honest signal: 0.300
- Tolerance: 0.080
- Signal gap: 0.220
- Single-unknown-mask bound: 8.940e-44
- Validation errors: 0

## Validation Claim

- Admissible claim: B10-T2 has a restricted, conditional verifier-soundness lemma when refresh independence guarantees at least one hidden predicate unknown to the adversary.
- Rejected claim: This proves a hardware-verifier protocol, cryptographic soundness, sampling hardness, or a BQP/classical separation.
- Operational rule: A verifier claim may cite this lemma only if it declares the leakage channel, proves at least one refreshed predicate remains unknown, and reports verifier sample overhead.

## B10-T2-L1: refresh_independence_hidden_predicate_soundness_bound

- Type: restricted_soundness_lemma
- Status: proved_under_refresh_independence_model_not_cryptographic_soundness
- Statement: In the declared transcript model, suppose challenge refresh or projection rotation leaves at least one verifier predicate unknown and statistically independent of the adversary's generated transcript after bounded leakage. If the honest verifier expects parity mean at least mu and accepts within tolerance tau < mu using N independent samples, then any adversary whose transcript is unbiased on that unknown predicate passes that predicate with probability at most exp(-N(mu-tau)^2/2).

### Assumptions

- The leakage channel is bounded leakage: it may reveal public parameters and a declared subset of predicates, but at least one tested predicate remains hidden.
- The challenge-refresh schedule provides refresh independence: the remaining unknown predicate is sampled after, or independently of, the adversary's transcript-generation strategy.
- For every unknown predicate, the adversary's generated samples have parity mean 0 conditional on the leaked transcript.
- Verifier samples are independent enough for a Hoeffding tail bound at the tested predicate.
- The honest signal gap mu - tau is positive and all verifier runtime/sample costs are included separately.

### Proof Sketch

- Condition on the complete leaked transcript and all public verifier parameters.
- For one refreshed unknown predicate, the adversary's parity variables are bounded in [-1, 1] with conditional mean 0.
- Acceptance on that predicate requires the empirical parity mean to deviate upward by at least mu - tau.
- Hoeffding's inequality gives probability at most exp(-N(mu-tau)^2/2) for that deviation.
- If several unknown predicates are independently refreshed, multiply the one-predicate bound under the declared independence assumption; otherwise keep the single-predicate bound only.

## B10-T2-C1: current_proxy_parameters_clear_five_percent_if_one_predicate_remains_unknown

- Statement: With N=4096 verifier samples, minimum honest signal mu=0.30, and tolerance tau=0.08, the single-refreshed-predicate bound is below the 5% soundness gate.
- Computed bound: 8.940e-44
- Status: parameterized_corollary_for_current_proxy_only

## High-Leakage Empirical Boundary From B8

| refresh mode | max learned soundness | mean learned soundness | learners over 5% |
|---|---:|---:|---|
| challenge_refresh | 0.000 | 0.000 | none |
| none | 1.000 | 0.726 | correlation_mask_learner, generative_projection_learner, leakage_augmented_generator |
| projection_rotation | 0.025 | 0.004 | none |
| refresh_plus_rotation | 0.000 | 0.000 | none |

## Remaining Obligations

- B10-T2-R1 (open): Instantiate a hardware-executable randomized-measurement verifier whose transcript actually satisfies refresh independence.
- B10-T2-R2 (open): Replace the empirical CNOT hidden-projection proxy with a distribution family tied to a sampling-hardness assumption.
- B10-T2-R3 (open): Stress unrestricted learned/generative adversaries against the formal leakage channel, not only side-channel candidate masks.
- B10-T2-R4 (open): Account for verifier overhead so the refresh schedule does not erase the claimed advantage denominator.

## Limits

- This is a restricted conditional lemma, not a cryptographic verification theorem.
- The proof covers only the case where at least one tested predicate remains hidden and independent after leakage.
- The empirical B8 rows are still required to catch full-cover leakage cases such as no-refresh high leakage.
- The result does not prove sampling hardness, hardware feasibility, or BQP versus classical separation.
