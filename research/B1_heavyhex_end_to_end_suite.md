# B1 Heavy-Hex End-to-End Routed Benefit Suite v0.1

Last updated: 2026-06-13

Status: **topology_routed_benefit_suite_not_calibrated_noise_claim**

## Level Results

| Qiskit level | Aer pass/fail | Operation | 2Q gates | Depth | Exposure | Idle proxy |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 30 / 0 | 16.95% | 0.00% | 19.44% | 2.93% | 20.55% |
| 1 | 30 / 0 | 0.03% | 0.00% | 0.00% | 0.00% | -0.00% |

Best level by exposure reduction: `0` (2.93%).

## Interpretation

- B1 retains measurable routed benefits under Qiskit heavy-hex level 0.
- Qiskit heavy-hex level 1 nearly erases the current B1 pre-routing benefits after routing.
- Post-routing two-qubit count does not improve at either tested level.
- The next B1 algorithmic step should be routing-aware 2-4 qubit optimization rather than more isolated 1Q compression.
