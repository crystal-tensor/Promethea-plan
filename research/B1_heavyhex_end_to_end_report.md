# B1 Heavy-Hex End-to-End Routed Benefit v0.1

Last updated: 2026-06-13

Status: **topology_routed_benefit_diagnostic_not_calibrated_noise_claim**

## Summary

- Circuits: 30
- Heavy-hex physical qubits: 19
- Coupling edges: 40
- Aer cross-check pass/fail: 30 / 0
- Aer shots per pair: 2048
- Aer max TVD: 0.16455

## Routed Benefit

| Metric | Reduction after routing |
|---|---:|
| Operation count | 16.95% |
| Two-qubit gates | 0.00% |
| Logical depth | 19.44% |
| Hardware-weighted exposure | 2.93% |
| Idle-layer proxy | 20.55% |

## Interpretation

- B1 fixed-point compression retains measurable routed benefits after both source and optimized circuits are routed to the same heavy-hex distance-3 topology.
- The strongest routed benefits in this first diagnostic are operation count, logical depth, and idle-layer proxy reductions.
- Two-qubit gate count is unchanged after routing at Qiskit level 0, so the current B1 two-qubit logical reduction is mostly absorbed by routing overhead.
- Hardware-weighted exposure improves only modestly after routing, far below the 20% portfolio target.
- This is a topology-routed diagnostic, not a calibrated backend noise or duration claim.

## Open Gates

- Run optimization levels 1 and 3 as a longer regression to see whether routing optimization preserves or erases B1 benefits.
- Route both source and B1 optimized circuits through a calibrated or synthetic-noise heavy-hex backend model.
- Add routing-aware optimization passes so B1 reduces post-routing two-qubit count and exposure, not only pre-routing logical depth.
