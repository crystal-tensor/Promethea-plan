# B1 Baseline Comparison Report v0.1

Last updated: 2026-06-13

On the 30-circuit exact suite, B1 outperforms the best exact-valid Qiskit all-to-all u3/cx baseline on operation count, two-qubit count, logical depth, and hardware-weighted exposure. Qiskit level 3 is not used as a valid baseline because exact equivalence fails on 7 circuits.

Remaining gap: This is still not a routing-aware calibrated heavy-hex comparison; the next baseline should include coupling maps, target basis, and layout/routing constraints without changing circuit semantics.

## Best Valid Comparison

| Method | Equiv failures | Operation | 2Q | Depth | Exposure |
|---|---:|---:|---:|---:|---:|
| B1 fixed-point | 0 | 34.17% | 10.72% | 34.98% | 12.58% |
| Qiskit level 1 | 0 | 14.60% | -25.63% | 15.25% | -13.36% |

## B1 Minus Best Valid Qiskit

| Metric | Delta |
|---|---:|
| Operation | 19.57% |
| 2Q | 36.35% |
| Depth | 19.73% |
| Exposure | 25.94% |

## Qiskit Baseline Levels

| Level | Exact pass/fail | Operation | 2Q | Depth | Exposure |
|---:|---:|---:|---:|---:|---:|
| 0 | 30/0 | -18.43% | -25.63% | -17.20% | -18.10% |
| 1 | 30/0 | 14.60% | -25.63% | 15.25% | -13.36% |
| 3 | 23/7 | 38.75% | 15.27% | 42.99% | 18.91% |

## Limits

- Qiskit baseline uses all-to-all connectivity and u3/cx basis without routing.
- This is an independent compiler baseline, not a calibrated heavy-hex hardware transpilation.
- Output equivalence is checked by the local exact statevector checker for the 30-circuit suite.
- Level 3 is reported for diagnostics only because exact equivalence failed.
