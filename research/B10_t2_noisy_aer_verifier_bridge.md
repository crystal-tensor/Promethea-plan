# B10-T2 Noisy Qiskit/Aer Verifier Bridge v0.1

Last updated: 2026-06-17

Status: **noisy_aer_circuit_verifier_bridge_not_hardware_execution**

## Summary

- Source target: B10-T2
- Source ideal Aer bridge: b10_t2_qiskit_aer_verifier_bridge_v0
- Source device-noise bridge: b10_t2_device_noise_transcript_bridge_v0
- Method: b10_t2_noisy_aer_verifier_bridge_v0
- Noisy Qiskit/Aer bridge instantiated: True
- Circuit-level adversary inputs instantiated: True
- Hardware execution performed: False
- Noisy Aer circuits executed: 9600
- Max circuit qubits including verifier ancillas: 22
- Bridge-safe noisy honest acceptance: 1.000
- Bridge-safe noisy adversary acceptance: 0.000
- Bridge-safe noisy honest predicate-bit error: 0.113
- Bridge-safe min unknown independent predicates: 7.0
- Source transcript safe high-leakage soundness: 0.020833333333333332
- Unsafe noisy device profiles: ['calibration_side_channel']
- Unsafe noisy refresh modes: ['none']
- Sampling hardness proved: False
- Explicitly not a BQP separation: True
- Validation errors: 0

## High-Leakage Noisy Circuit Rows

| task | profile | mode | adversary | honest accept | adversary accept | honest bit error | unknown predicates | independence |
|---|---|---|---|---:|---:|---:|---:|---:|
| cnot_hidden_projection_n12_d48 | ideal_transcript | none | generative_mask_searcher | 1.000 | 0.000 | 0.000 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | ideal_transcript | none | leaked_predicate_replayer | 1.000 | 0.000 | 0.000 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | ideal_transcript | none | oracle_cover_spoofer | 1.000 | 0.500 | 0.000 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | ideal_transcript | none | stale_transcript_learner | 1.000 | 0.000 | 0.000 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | ideal_transcript | challenge_refresh | generative_mask_searcher | 1.000 | 0.000 | 0.000 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | ideal_transcript | challenge_refresh | leaked_predicate_replayer | 1.000 | 0.000 | 0.000 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | ideal_transcript | challenge_refresh | oracle_cover_spoofer | 1.000 | 0.000 | 0.000 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | ideal_transcript | challenge_refresh | stale_transcript_learner | 1.000 | 0.000 | 0.000 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | ideal_transcript | refresh_plus_rotation | generative_mask_searcher | 1.000 | 0.000 | 0.000 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | ideal_transcript | refresh_plus_rotation | leaked_predicate_replayer | 1.000 | 0.000 | 0.000 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | ideal_transcript | refresh_plus_rotation | oracle_cover_spoofer | 1.000 | 0.000 | 0.000 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | ideal_transcript | refresh_plus_rotation | stale_transcript_learner | 1.000 | 0.000 | 0.000 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | none | generative_mask_searcher | 1.000 | 0.000 | 0.021 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | none | leaked_predicate_replayer | 1.000 | 0.000 | 0.021 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | none | oracle_cover_spoofer | 1.000 | 0.500 | 0.021 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | none | stale_transcript_learner | 1.000 | 0.000 | 0.021 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | challenge_refresh | generative_mask_searcher | 1.000 | 0.000 | 0.023 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | challenge_refresh | leaked_predicate_replayer | 1.000 | 0.000 | 0.023 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | challenge_refresh | oracle_cover_spoofer | 1.000 | 0.000 | 0.023 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | challenge_refresh | stale_transcript_learner | 1.000 | 0.000 | 0.023 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | refresh_plus_rotation | generative_mask_searcher | 1.000 | 0.000 | 0.018 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | refresh_plus_rotation | leaked_predicate_replayer | 1.000 | 0.000 | 0.018 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | refresh_plus_rotation | oracle_cover_spoofer | 1.000 | 0.000 | 0.018 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | low_noise_bridge | refresh_plus_rotation | stale_transcript_learner | 1.000 | 0.000 | 0.018 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | none | generative_mask_searcher | 1.000 | 0.000 | 0.063 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | none | leaked_predicate_replayer | 1.000 | 0.000 | 0.063 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | none | oracle_cover_spoofer | 1.000 | 0.500 | 0.063 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | none | stale_transcript_learner | 1.000 | 0.000 | 0.063 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | challenge_refresh | generative_mask_searcher | 1.000 | 0.000 | 0.048 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | challenge_refresh | leaked_predicate_replayer | 1.000 | 0.000 | 0.048 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | challenge_refresh | oracle_cover_spoofer | 1.000 | 0.000 | 0.048 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | challenge_refresh | stale_transcript_learner | 1.000 | 0.000 | 0.048 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | refresh_plus_rotation | generative_mask_searcher | 1.000 | 0.000 | 0.051 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | refresh_plus_rotation | leaked_predicate_replayer | 1.000 | 0.000 | 0.051 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | refresh_plus_rotation | oracle_cover_spoofer | 1.000 | 0.000 | 0.051 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | readout_biased_bridge | refresh_plus_rotation | stale_transcript_learner | 1.000 | 0.000 | 0.051 | 9.0 | True |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | none | generative_mask_searcher | 1.000 | 0.000 | 0.083 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | none | leaked_predicate_replayer | 1.000 | 0.000 | 0.083 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | none | oracle_cover_spoofer | 1.000 | 0.000 | 0.083 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | none | stale_transcript_learner | 1.000 | 0.000 | 0.083 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | challenge_refresh | generative_mask_searcher | 1.000 | 0.000 | 0.096 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | challenge_refresh | leaked_predicate_replayer | 1.000 | 0.000 | 0.096 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | challenge_refresh | oracle_cover_spoofer | 1.000 | 0.000 | 0.096 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | challenge_refresh | stale_transcript_learner | 1.000 | 0.000 | 0.096 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | refresh_plus_rotation | generative_mask_searcher | 1.000 | 0.000 | 0.113 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | refresh_plus_rotation | leaked_predicate_replayer | 1.000 | 0.000 | 0.113 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | refresh_plus_rotation | oracle_cover_spoofer | 1.000 | 0.000 | 0.113 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | drift_correlated_bridge | refresh_plus_rotation | stale_transcript_learner | 1.000 | 0.000 | 0.113 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | none | generative_mask_searcher | 1.000 | 0.250 | 0.059 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | none | leaked_predicate_replayer | 1.000 | 0.000 | 0.059 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | none | oracle_cover_spoofer | 1.000 | 0.250 | 0.059 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | none | stale_transcript_learner | 1.000 | 0.000 | 0.059 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | challenge_refresh | generative_mask_searcher | 1.000 | 0.000 | 0.048 | 1.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | challenge_refresh | leaked_predicate_replayer | 1.000 | 0.000 | 0.048 | 1.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | challenge_refresh | oracle_cover_spoofer | 1.000 | 0.000 | 0.048 | 1.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | challenge_refresh | stale_transcript_learner | 1.000 | 0.000 | 0.048 | 1.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | refresh_plus_rotation | generative_mask_searcher | 1.000 | 0.000 | 0.047 | 2.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | refresh_plus_rotation | leaked_predicate_replayer | 1.000 | 0.000 | 0.047 | 2.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | refresh_plus_rotation | oracle_cover_spoofer | 1.000 | 0.250 | 0.047 | 2.0 | False |
| cnot_hidden_projection_n12_d48 | calibration_side_channel | refresh_plus_rotation | stale_transcript_learner | 1.000 | 0.000 | 0.047 | 2.0 | False |

## Claim Boundary

- Supported: the randomized parity verifier can be executed as noisy Aer circuits with explicit circuit-level adversary input generation.
- Compared: the noisy Aer bridge inherits the stricter transcript bridge result for the <=5% high-leakage soundness claim.
- Rejected: calibration-side-channel and no-refresh rows violate the refresh-independence boundary or produce unsafe adversary acceptance.
- Not claimed: real hardware execution, calibrated-backend validation, sampling hardness, cryptographic soundness, or BQP/classical separation.

## Limits

- This executes noisy Qiskit/Aer stabilizer circuits, not a calibrated physical backend.
- Circuit-level adversary inputs are generated by choosing adversarial verifier-output bit strings and inverting the CNOT task map.
- The Aer noise model uses Pauli and readout errors derived from transcript bridge profiles; it does not model coherent drift, leakage outside the computational subspace, or backend calibration history.
- The transcript bridge remains the source of the stricter <=5% empirical soundness claim.
- No BQP/classical separation, sampling-hardness proof, cryptographic soundness theorem, or hardware-verifier claim is made.
