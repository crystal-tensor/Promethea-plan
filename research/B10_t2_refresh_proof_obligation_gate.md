# B10-T2 Refresh Proof-Obligation Gate v0.1

Last updated: 2026-06-17

Status: **proof_obligation_gate_proxy_supports_rejection_rule_not_soundness_lemma**

## Summary

- Source target: B10-T2 / sampling_advantage_verification_layer_target
- Method: b10_t2_refresh_proof_obligation_gate_v0
- Source B8 stress: b8_generative_spoofer_refresh_v0
- Lemma status: not_proved_proxy_insufficient_for_general_soundness
- Explicitly not a BQP separation: True
- Configurations: 144
- Minimum honest completeness: 1.000
- Maximum learned soundness: 1.000
- Soundness gate: 0.05
- High leakage fraction: 0.75
- Safe high-leakage refresh modes: ['challenge_refresh', 'projection_rotation', 'refresh_plus_rotation']
- Unsafe high-leakage refresh modes: ['none']
- Validation errors: 0

## Validation Claim

- Rejected claim: A B10-T2 sampling-advantage verification layer with fixed hidden projections, no challenge refresh, and lambda=0.75 leakage can claim soundness <= 0.05.
- Supported rejection rule: Reject no-refresh verifier claims at lambda=0.75 in this CNOT hidden-projection proxy, because trained/generative spoofers reach learned soundness 1.0.
- Admissible next claim: A restricted soundness lemma may be attempted only after projection rotation or challenge refresh is formalized as an unpredictable post-sampling challenge with a declared leakage channel and asymptotic adversary model.

## High-Leakage Refresh Boundary

| refresh mode | max learned soundness | mean learned soundness | learners over 5% |
|---|---:|---:|---|
| challenge_refresh | 0.000 | 0.000 | none |
| none | 1.000 | 0.726 | correlation_mask_learner, generative_projection_learner, leakage_augmented_generator |
| projection_rotation | 0.025 | 0.004 | none |
| refresh_plus_rotation | 0.000 | 0.000 | none |

## Candidate Lemma Schema

- Name: minimum_refresh_soundness_gate_for_hidden_projection_verifiers
- Not-yet-proved statement: For a sampling verifier with independent projection rotation or challenge refresh, bounded leakage lambda, and adversaries limited to the declared transcript model, adaptive-spoofer pass probability is at most s(lambda, m, N) below the declared soundness gate while honest completeness stays above c.

### Why The Current Proxy Is Insufficient

- The B8 task uses finite CNOT hidden-projection proxies rather than a hardware randomized-measurement circuit family.
- Candidate true masks are exposed through a side-channel quality model, not derived from unrestricted transcript access.
- The adversary class is empirical and finite, not an asymptotic or cryptographic adaptive adversary model.
- The refresh operations are modeled as projection rotation/challenge reset effects, not yet as a fully specified verifier protocol with seed timing and transcript distribution.
- The stress result has strong negative evidence for no-refresh high leakage, but finite positive rows do not prove universal soundness for every learner.

## Proof Obligations

- B10-T2-O1 (open): Define the verifier transcript distribution, seed timing, and challenge-refresh schedule as a formal protocol.
- B10-T2-O2 (open): Replace the side-channel candidate-mask model with a leakage channel L that maps transcripts to adversary information.
- B10-T2-O3 (open): State an adversary class with allowed computation, samples, adaptivity, and access to refreshed challenges.
- B10-T2-O4 (open): Prove or bound soundness as a function of leakage lambda, invariant count, verifier samples, and refresh entropy.
- B10-T2-O5 (open): Instantiate hardware-executable randomized-measurement circuits or clearly declare that the result remains a proxy.
- B10-T2-O6 (open): Separate the verifier soundness statement from the external sampling-hardness assumption used for advantage.
- B10-T2-O7 (open): Audit verifier overhead so refresh does not erase the claimed sampling-advantage denominator.

## Worst Learned Rows

| task | mode | leakage | learner | soundness | true masks selected | mean max error |
|---|---|---:|---|---:|---:|---:|
| cnot_hidden_projection_n12_d48 | none | 0.75 | generative_projection_learner | 1.000 | 10.00 | 0.032 |
| cnot_hidden_projection_n12_d48 | none | 0.75 | leakage_augmented_generator | 1.000 | 10.00 | 0.033 |
| cnot_hidden_projection_n16_d64 | none | 0.75 | generative_projection_learner | 1.000 | 10.00 | 0.031 |
| cnot_hidden_projection_n16_d64 | none | 0.75 | leakage_augmented_generator | 1.000 | 10.00 | 0.030 |
| cnot_hidden_projection_n20_d80 | none | 0.75 | generative_projection_learner | 1.000 | 10.00 | 0.031 |
| cnot_hidden_projection_n20_d80 | none | 0.75 | leakage_augmented_generator | 1.000 | 10.00 | 0.030 |
| cnot_hidden_projection_n12_d48 | none | 0.50 | leakage_augmented_generator | 0.525 | 9.43 | 0.236 |
| cnot_hidden_projection_n16_d64 | none | 0.50 | leakage_augmented_generator | 0.525 | 9.40 | 0.287 |

## Limits

- This gate is a proof-pressure artifact, not a cryptographic soundness proof.
- It supports a rejection rule for no-refresh high-leakage claims in the current proxy.
- It does not establish a BQP/classical separation or a universal verification theorem.
- It should be used to drive B4/B8 protocol formalization, not to advertise a solved B10 result.
