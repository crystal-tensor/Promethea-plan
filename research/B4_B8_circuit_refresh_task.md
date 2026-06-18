# B4/B8 Circuit-Level Hidden-Projection Refresh Task v0.1

Last updated: 2026-06-17

Status: **circuit_level_hidden_projection_refresh_boundary_not_quantum_advantage_claim**

## Summary

- Task family: random_cnot_hidden_projection_sampling
- Tasks: 3
- Configurations: 192
- Qubits: [12, 16, 20]
- Circuit depth factor: 4
- Invariants per task: 10
- Samples per trial: 4096
- Trials: 120
- Minimum honest completeness: 1.000
- Maximum adaptive soundness: 0.675
- No-refresh high-leakage max soundness: 0.675
- Best repair high-leakage max soundness: 0.000
- High-leakage repair modes passing <=5% soundness: ['challenge_refresh', 'projection_rotation', 'refresh_plus_rotation']

## Refresh Summary

| mode | leakage | max soundness | mean soundness | adversaries over 5% |
|---|---:|---:|---:|---|
| none | 0.00 | 0.000 | 0.000 | none |
| none | 0.25 | 0.000 | 0.000 | none |
| none | 0.50 | 0.000 | 0.000 | none |
| none | 0.75 | 0.675 | 0.156 | trap_aware_leakage_spoofer |
| projection_rotation | 0.00 | 0.000 | 0.000 | none |
| projection_rotation | 0.25 | 0.000 | 0.000 | none |
| projection_rotation | 0.50 | 0.000 | 0.000 | none |
| projection_rotation | 0.75 | 0.000 | 0.000 | none |
| challenge_refresh | 0.00 | 0.000 | 0.000 | none |
| challenge_refresh | 0.25 | 0.000 | 0.000 | none |
| challenge_refresh | 0.50 | 0.000 | 0.000 | none |
| challenge_refresh | 0.75 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.00 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.25 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.50 | 0.000 | 0.000 | none |
| refresh_plus_rotation | 0.75 | 0.000 | 0.000 | none |

## Worst Rows

| task | mode | leakage | adversary | soundness | known | guessed | mean max error |
|---|---|---:|---|---:|---:|---:|---:|
| cnot_hidden_projection_n20_d80 | none | 0.75 | trap_aware_leakage_spoofer | 0.675 | 8 | 2 | 0.441 |
| cnot_hidden_projection_n12_d48 | none | 0.75 | trap_aware_leakage_spoofer | 0.600 | 8 | 2 | 0.551 |
| cnot_hidden_projection_n16_d64 | none | 0.75 | trap_aware_leakage_spoofer | 0.592 | 8 | 2 | 0.438 |
| cnot_hidden_projection_n12_d48 | none | 0.00 | known_projection_replay_spoofer | 0.000 | 0 | 0 | 0.681 |
| cnot_hidden_projection_n12_d48 | none | 0.00 | metadata_only_adaptive_spoofer | 0.000 | 0 | 1 | 0.683 |
| cnot_hidden_projection_n12_d48 | none | 0.00 | surrogate_projection_learner | 0.000 | 0 | 4 | 0.713 |
| cnot_hidden_projection_n12_d48 | none | 0.00 | trap_aware_leakage_spoofer | 0.000 | 0 | 7 | 0.806 |
| cnot_hidden_projection_n12_d48 | none | 0.25 | known_projection_replay_spoofer | 0.000 | 2 | 2 | 0.704 |
| cnot_hidden_projection_n12_d48 | none | 0.25 | metadata_only_adaptive_spoofer | 0.000 | 2 | 2 | 0.711 |
| cnot_hidden_projection_n12_d48 | none | 0.25 | surrogate_projection_learner | 0.000 | 2 | 4 | 0.709 |
| cnot_hidden_projection_n12_d48 | none | 0.25 | trap_aware_leakage_spoofer | 0.000 | 2 | 6 | 0.773 |
| cnot_hidden_projection_n12_d48 | none | 0.50 | known_projection_replay_spoofer | 0.000 | 5 | 2 | 0.704 |

## Claim Boundary

- This is a circuit-level CNOT/hidden-projection proxy, not a quantum advantage protocol.
- The verifier checks task-relevant hidden projections rather than the full output distribution.
- Challenge refresh and projection rotation are instantiated as fresh hidden masks derived from explicit CNOT circuits, but not yet as hardware-executable randomized measurement circuits.
- Adaptive spoofers are heuristic projection-enforcement models, not trained generative attackers.
