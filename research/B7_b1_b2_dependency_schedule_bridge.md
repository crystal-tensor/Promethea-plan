# B7 B1/B2 Dependency-Schedule Bridge v0.1

Last updated: 2026-06-13

Status: **dependency_schedule_bridge_not_physical_layout**

## Summary

- Comparisons: 6
- Selected B2 target: d=3, basis=x, p=0.001, target=0.01
- B2 Wilson 95% high: 0.0012789
- Minimum space-time-volume reduction: 1.195x
- Mean space-time-volume reduction: 1.354x
- Minimum exposure reduction: 1.394x

## Comparisons

| workload | depth before | depth after | volume reduction | exposure reduction | 2Q reduction |
|---|---:|---:|---:|---:|---:|
| aggregate_30_circuits | 4923 | 3725 | 1.321x | 1.485x | 1.592x |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | 734 | 614 | 1.195x | 1.394x | 1.448x |
| qasmbench_medium_exact/gcm_h6.qasm | 1967 | 1491 | 1.319x | 1.535x | 1.596x |
| qasmbench_medium_exact/qf21_n15.qasm | 355 | 241 | 1.469x | 2.046x | 2.246x |
| qasmbench_medium_exact/sat_n11.qasm | 641 | 396 | 1.616x | 1.899x | 1.983x |
| qasmbench_small/hhl_n7.qasm | 433 | 360 | 1.202x | 1.421x | 1.498x |

## Limits

- This is a dependency-schedule bridge, not a physical layout or lattice-surgery compiler.
- The B2 target row is a small-distance Stim/PyMatching baseline and not a threshold or hardware-calibrated claim.
- The schedule maps QASM depth proxies to logical layers; it does not model magic-state factories or feed-forward.
- The aggregate row sums benchmark circuits for a portfolio-level sensitivity check, not a single executable algorithm.
