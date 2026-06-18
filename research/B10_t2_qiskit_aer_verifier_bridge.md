# B10-T2 Qiskit/Aer Circuit-Level Verifier Bridge v0.1

Last updated: 2026-06-17

Status: **qiskit_aer_circuit_level_verifier_bridge_not_hardware_execution**

## Summary

- Source target: B10-T2
- Source device-noise bridge: b10_t2_device_noise_transcript_bridge_v0
- Method: b10_t2_qiskit_aer_verifier_bridge_v0
- Qiskit/Aer bridge instantiated: True
- Hardware-executable randomized measurement circuits instantiated: True
- Hardware execution performed: False
- Aer circuit count: 216
- Max circuit qubits including verifier ancillas: 30
- Aer semantic mismatch count: 0
- Minimum Aer honest completeness: 1.000
- Source device-noise safe high-leakage max soundness: 0.020833333333333332
- Source margin-sensitive refresh modes: ['projection_rotation']
- Source unsafe device profiles: ['calibration_side_channel']
- Sampling hardness proved: False
- Explicitly not a BQP separation: True
- Validation errors: 0

## Aer Circuit Semantic Checks

| task | mode | data qubits | ancillas | circuits | mismatches | bit error | honest completeness |
|---|---|---:|---:|---:|---:|---:|---:|
| cnot_hidden_projection_n12_d48 | projection_rotation | 12 | 10 | 24 | 0 | 0.000 | 1.000 |
| cnot_hidden_projection_n12_d48 | challenge_refresh | 12 | 10 | 24 | 0 | 0.000 | 1.000 |
| cnot_hidden_projection_n12_d48 | refresh_plus_rotation | 12 | 10 | 24 | 0 | 0.000 | 1.000 |
| cnot_hidden_projection_n16_d64 | projection_rotation | 16 | 10 | 24 | 0 | 0.000 | 1.000 |
| cnot_hidden_projection_n16_d64 | challenge_refresh | 16 | 10 | 24 | 0 | 0.000 | 1.000 |
| cnot_hidden_projection_n16_d64 | refresh_plus_rotation | 16 | 10 | 24 | 0 | 0.000 | 1.000 |
| cnot_hidden_projection_n20_d80 | projection_rotation | 20 | 10 | 24 | 0 | 0.000 | 1.000 |
| cnot_hidden_projection_n20_d80 | challenge_refresh | 20 | 10 | 24 | 0 | 0.000 | 1.000 |
| cnot_hidden_projection_n20_d80 | refresh_plus_rotation | 20 | 10 | 24 | 0 | 0.000 | 1.000 |

## Claim Boundary

- Supported: the hidden-predicate verifier has explicit Qiskit circuits with randomized ancilla challenge flips and ideal Aer semantic checks.
- Inherited: device-noise/adversary soundness comes from the transcript-level device-noise bridge, where challenge_refresh and refresh_plus_rotation remain bridge-safe.
- Not claimed: real hardware execution, sampling hardness, cryptographic soundness, or BQP/classical separation.

## Limits

- Qiskit/Aer executes ideal randomized parity verifier circuits, not real hardware.
- The adversary and device-noise stress metrics are inherited from the transcript-level device-noise bridge.
- The circuit bridge proves semantic consistency of the verifier circuit construction, not sampling hardness.
- No BQP/classical separation, cryptographic soundness theorem, or calibrated-device claim is made.
