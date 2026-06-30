# B4/B8 Real-Backend Transcript Readiness Gate

- Gate: T-B4-002f / T-B8-003j
- Method: `b4_b8_real_backend_transcript_readiness_gate_v0`
- Status: `real_backend_transcript_readiness_failed`
- Model status: `synthetic_fitted_spoofer_and_generic_backend_bridge_not_real_backend_transcripts`
- Readiness gates passed / failed: 5 / 5
- Missing readiness gates: R5, R6, R7, R8, R9

## Evidence

| Metric | Value |
| --- | ---: |
| synthetic transcript cases | 720 |
| fitted train / holdout / eval rows | 560 / 160 / 640 |
| backend-calibrated Aer circuits | 5760 |
| private-safe no-leak fitted acceptance | 0.0625 |
| leakage-blind no-leak fitted acceptance | 0.35 |
| full-private-material leakage fitted acceptance | 1.0 |
| real backend transcript rows | 0 |

## Readiness Gates

| gate | passed | label | missing to promote |
| --- | ---: | --- | --- |
| R1 | True | Synthetic private-challenge transcript bridge is present | Keep the synthetic bridge as a control denominator for real transcripts. |
| R2 | True | Fitted train/holdout diagnostic is present | Reuse the same split discipline on real-backend or hardware transcripts. |
| R3 | True | GenericBackendV2 calibrated Aer bridge exists | Replace GenericBackendV2-style simulated calibration with real backend properties. |
| R4 | True | Private-safe no-leak fitted acceptance stays below 0.10 | Re-test this margin on real-backend leakage-separated holdout rows. |
| R5 | False | Real backend properties are used | Attach backend properties from an actual device snapshot or provider calibration export. |
| R6 | False | Hardware execution is performed | Run randomized-measurement circuits on hardware or independently supplied hardware traces. |
| R7 | False | Leakage-separated fitted training uses real transcripts | Train and hold out leakage-separated spoofers on real-backend or hardware transcript rows. |
| R8 | False | Leakage-blind no-leak fitted acceptance is below 0.10 | Separate leakage regimes or redesign private predicates so leakage-blind training cannot lift no-leak acceptance. |
| R9 | False | Full private-material leakage is bounded | Redesign the challenge material so full leakage is outside the claim boundary or cryptographically protected. |
| R10 | True | No forbidden advantage or soundness claim is made | Keep all claims bounded until real-backend transcript readiness passes. |

## Claim Boundary

- real_backend_transcript_readiness_gate_built: True
- real_backend_transcript_readiness: False
- hardware_execution_performed: False
- real_backend_properties_used: False
- protocol_soundness_proved: False
- cryptographic_soundness_proved: False
- sampling_hardness_proved: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False
- what_is_supported: Synthetic transcript controls, fitted holdout spoofers, and a GenericBackendV2-style calibrated Aer bridge are present.
- what_is_not_supported: No real backend properties, no hardware execution, no real transcript rows, leakage-blind fitting is unsafe, and full private-material leakage still breaks the protocol.

## Next Gate

The next B4/B8 gate must ingest real backend properties or hardware
randomized-measurement transcripts, keep leakage-separated train/holdout
splits, and rerun fitted/generative spoofers before any soundness or
advantage claim is promoted.
