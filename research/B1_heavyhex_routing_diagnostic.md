# B1 Heavy-Hex Routing Diagnostic v0.1

Last updated: 2026-06-13

Status: **device_like_topology_diagnostic_not_calibrated_noise_baseline**

## Summary

- Physical topology: heavy-hex distance 3
- Physical qubits: 19
- Coupling edges: 40
- Source circuits: 30
- Aer cross-check all passed: True
- Aer-valid levels: [0]
- Best diagnostic level by exposure: 0
- Best diagnostic exposure reduction: -164.71%

## Level Results

| Level | Aer pass/fail | Shots | Max TVD | Operation | 2Q gates | Depth | Exposure |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 30 / 0 | 2048 | 0.16455 | -66.25% | -196.71% | -72.71% | -164.71% |

Negative reduction means routing worsened that metric.

## Interpretation

- This is the first B1 topology-aware Qiskit heavy-hex routing diagnostic.
- The Qiskit heavy-hex distance-3 coupling map has 19 physical qubits and 40 directed edges.
- Level 0 passes independent Aer output-distribution cross-checks for all 30 circuit pairs under the current shot-based threshold model.
- Routing to this sparse physical topology substantially worsens operation count, two-qubit count, logical depth, and hardware-weighted exposure.
- This is not a calibrated device baseline because no backend-specific durations, error rates, readout errors, or noise model are used.

## Open Gates

- Run optimization levels 1 and 3 as a longer regression or optimize the runner to avoid long interactive waits.
- Add calibrated backend properties or a documented synthetic heavy-hex noise model.
- Compare B1 compressed circuits after routing, not only source circuits after routing, to quantify end-to-end routed benefit.
