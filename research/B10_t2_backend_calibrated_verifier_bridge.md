# B10-T2 Backend-Calibrated Aer Verifier Bridge v0.1

Last updated: 2026-06-17

Status: **backend_calibrated_aer_verifier_bridge_not_hardware_execution**

## Summary

- Source target: B10-T2
- Source noisy Aer bridge: b10_t2_noisy_aer_verifier_bridge_v0
- Source device-noise bridge: b10_t2_device_noise_transcript_bridge_v0
- Method: b10_t2_backend_calibrated_verifier_bridge_v0
- Backend-calibrated noise parameters instantiated: True
- Qiskit GenericBackendV2 used: True
- Real backend properties used: False
- Hardware execution performed: False
- Backend-calibrated Aer circuits executed: 5760
- Max circuit qubits including verifier ancillas: 22
- Bridge-safe calibrated honest acceptance: 1.000
- Bridge-safe calibrated adversary acceptance: 0.250
- Bridge-safe calibrated honest predicate-bit error: 0.070
- Bridge-safe min unknown independent predicates: 7.0
- Source noisy Aer safe adversary acceptance: 0.0
- Source transcript safe high-leakage soundness: 0.020833333333333332
- Unsafe calibrated refresh modes: ['none']
- Sampling hardness proved: False
- Explicitly not a BQP separation: True
- Validation errors: 0

## Calibration Snapshots

| snapshot | seed | mean x err | max x err | mean cx err | max cx err | mean readout err | max readout err |
|---|---:|---:|---:|---:|---:|---:|---:|
| generic_v2_nominal_seed_1201 | 1201 | 0.000094 | 0.000099 | 0.002450 | 0.004995 | 0.002644 | 0.004945 |
| generic_v2_cx_stress_seed_1202 | 1202 | 0.000167 | 0.000174 | 0.004328 | 0.008668 | 0.002858 | 0.004737 |
| generic_v2_readout_stress_seed_1203 | 1203 | 0.000095 | 0.000100 | 0.002456 | 0.004998 | 0.004627 | 0.008502 |

## Backend-Calibrated Circuit Rows

| task | snapshot | mode | adversary | honest accept | adversary accept | honest bit error | adversary bit error | unknown predicates | independence |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | none | generative_mask_searcher | 1.000 | 0.000 | 0.038 | 0.245 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | none | leaked_predicate_replayer | 1.000 | 0.000 | 0.038 | 0.252 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | none | oracle_cover_spoofer | 1.000 | 0.250 | 0.038 | 0.171 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | none | stale_transcript_learner | 1.000 | 0.250 | 0.038 | 0.191 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | challenge_refresh | generative_mask_searcher | 1.000 | 0.000 | 0.031 | 0.395 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | challenge_refresh | leaked_predicate_replayer | 1.000 | 0.000 | 0.031 | 0.387 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | challenge_refresh | oracle_cover_spoofer | 1.000 | 0.000 | 0.031 | 0.352 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | challenge_refresh | stale_transcript_learner | 1.000 | 0.000 | 0.031 | 0.423 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | refresh_plus_rotation | generative_mask_searcher | 1.000 | 0.000 | 0.036 | 0.429 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | refresh_plus_rotation | leaked_predicate_replayer | 1.000 | 0.000 | 0.036 | 0.439 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | refresh_plus_rotation | oracle_cover_spoofer | 1.000 | 0.250 | 0.036 | 0.387 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_nominal_seed_1201 | refresh_plus_rotation | stale_transcript_learner | 1.000 | 0.000 | 0.036 | 0.435 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | none | generative_mask_searcher | 1.000 | 0.000 | 0.047 | 0.247 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | none | leaked_predicate_replayer | 1.000 | 0.000 | 0.047 | 0.245 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | none | oracle_cover_spoofer | 1.000 | 0.500 | 0.047 | 0.195 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | none | stale_transcript_learner | 1.000 | 0.000 | 0.047 | 0.208 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | challenge_refresh | generative_mask_searcher | 1.000 | 0.000 | 0.070 | 0.393 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | challenge_refresh | leaked_predicate_replayer | 1.000 | 0.000 | 0.070 | 0.430 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | challenge_refresh | oracle_cover_spoofer | 1.000 | 0.000 | 0.070 | 0.440 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | challenge_refresh | stale_transcript_learner | 1.000 | 0.000 | 0.070 | 0.377 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | refresh_plus_rotation | generative_mask_searcher | 1.000 | 0.000 | 0.047 | 0.409 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | refresh_plus_rotation | leaked_predicate_replayer | 1.000 | 0.000 | 0.047 | 0.434 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | refresh_plus_rotation | oracle_cover_spoofer | 1.000 | 0.000 | 0.047 | 0.504 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_cx_stress_seed_1202 | refresh_plus_rotation | stale_transcript_learner | 1.000 | 0.000 | 0.047 | 0.434 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | none | generative_mask_searcher | 1.000 | 0.000 | 0.044 | 0.257 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | none | leaked_predicate_replayer | 1.000 | 0.000 | 0.044 | 0.252 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | none | oracle_cover_spoofer | 1.000 | 0.000 | 0.044 | 0.193 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | none | stale_transcript_learner | 1.000 | 0.750 | 0.044 | 0.182 | 0.0 | False |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | challenge_refresh | generative_mask_searcher | 1.000 | 0.000 | 0.026 | 0.416 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | challenge_refresh | leaked_predicate_replayer | 1.000 | 0.000 | 0.026 | 0.418 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | challenge_refresh | oracle_cover_spoofer | 1.000 | 0.000 | 0.026 | 0.347 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | challenge_refresh | stale_transcript_learner | 1.000 | 0.000 | 0.026 | 0.401 | 7.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | refresh_plus_rotation | generative_mask_searcher | 1.000 | 0.000 | 0.052 | 0.442 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | refresh_plus_rotation | leaked_predicate_replayer | 1.000 | 0.000 | 0.052 | 0.415 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | refresh_plus_rotation | oracle_cover_spoofer | 1.000 | 0.000 | 0.052 | 0.468 | 8.0 | True |
| cnot_hidden_projection_n12_d48 | generic_v2_readout_stress_seed_1203 | refresh_plus_rotation | stale_transcript_learner | 1.000 | 0.000 | 0.052 | 0.423 | 8.0 | True |

## Claim Boundary

- Supported: the B10-T2 randomized parity verifier can be driven by backend-property-derived Aer noise models.
- Upgraded from the previous noisy bridge: noise parameters now come from backend target InstructionProperties instead of only hand-labeled transcript profiles.
- Still open: replace GenericBackendV2 snapshots with real backend properties or execute randomized-measurement verifier jobs on hardware.
- Not claimed: real hardware execution, hardware calibration validation, sampling hardness, cryptographic soundness, or BQP/classical separation.

## Limits

- This uses Qiskit GenericBackendV2 calibration-style target properties, not IBM Runtime backend properties.
- The bridge derives per-qubit readout errors and per-gate depolarizing errors from backend target InstructionProperties.
- No physical backend job was submitted and no real-device calibration history was accessed.
- The transcript bridge remains the source of the stricter empirical soundness boundary.
- No BQP/classical separation, sampling-hardness proof, cryptographic soundness theorem, or hardware-verifier claim is made.
