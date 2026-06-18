# B7 gcm_h6 FT-Ledger Boundary v0.1

Last updated: 2026-06-15

Status: **gcm_h6_ft_boundary_quantified_not_physical_layout**

## Summary

- Source ledger: `results/B7_ft_synthesis_ledger_v0.json`
- Current min workload: `qasmbench_medium_exact/gcm_h6.qasm`
- Current min factory variant: `throughput_heavy_factories`
- Current min STV reduction: 1.086008x
- Current min bottleneck after: factory_path
- gcm_h6 after arbitrary numeric rotations: 270
- gcm_h6 arbitrary numeric T cost: 5400
- gcm_h6 after total T ledger: 6224
- Interpretation: The FT ledger moved sat_n11 out of the parallel-factory minimum row; gcm_h6 is now limited by arbitrary numeric rotations. Under the current footprint, the gcm_h6 throughput row needs a large reduction in after-ledger T pressure or a lower arbitrary-rotation synthesis cost to push portfolio min STV beyond 1.20x.

## Target Requirements For Current Min Row

| target STV | max after T ledger | additional T ledger to remove | equivalent arbitrary rotations at cost 20 | needs data path reduction |
|---:|---:|---:|---:|---|
| 1.200x | 5632 | 592 | 30 | False |
| 1.250x | 5400 | 824 | 42 | False |

## Portfolio Arbitrary-Rotation Cost Sweep

| arbitrary T cost | min STV | mean STV | min workload | min variant | after factory/data rows |
|---:|---:|---:|---|---|---:|
| 0 | 1.121827x | 1.308554x | qasmbench_medium_exact/sat_n11.qasm | serial_factory | 4 / 14 |
| 1 | 1.121827x | 1.311473x | qasmbench_medium_exact/sat_n11.qasm | serial_factory | 6 / 12 |
| 2 | 1.121827x | 1.310410x | qasmbench_medium_exact/sat_n11.qasm | serial_factory | 7 / 11 |
| 3 | 1.121827x | 1.303964x | qasmbench_medium_exact/sat_n11.qasm | serial_factory | 10 / 8 |
| 4 | 1.121806x | 1.293694x | qasmbench_medium_exact/gcm_h6.qasm | serial_factory | 12 / 6 |
| 5 | 1.115420x | 1.285123x | qasmbench_medium_exact/gcm_h6.qasm | serial_factory | 12 / 6 |
| 6 | 1.110445x | 1.284383x | qasmbench_medium_exact/gcm_h6.qasm | serial_factory | 12 / 6 |
| 7 | 1.105914x | 1.288109x | qasmbench_medium_exact/gcm_h6.qasm | balanced_factories | 12 / 6 |
| 8 | 1.103107x | 1.286399x | qasmbench_medium_exact/gcm_h6.qasm | balanced_factories | 14 / 4 |
| 9 | 1.100471x | 1.280808x | qasmbench_medium_exact/gcm_h6.qasm | serial_factory | 14 / 4 |
| 10 | 1.098165x | 1.275786x | qasmbench_medium_exact/gcm_h6.qasm | serial_factory | 15 / 3 |
| 11 | 1.095810x | 1.269523x | qasmbench_medium_exact/gcm_h6.qasm | balanced_factories | 15 / 3 |
| 12 | 1.094414x | 1.268718x | qasmbench_medium_exact/gcm_h6.qasm | balanced_factories | 15 / 3 |
| 13 | 1.092971x | 1.268314x | qasmbench_medium_exact/gcm_h6.qasm | serial_factory | 15 / 3 |
| 14 | 1.091646x | 1.266486x | qasmbench_medium_exact/gcm_h6.qasm | serial_factory | 16 / 2 |
| 15 | 1.090179x | 1.261605x | qasmbench_medium_exact/gcm_h6.qasm | balanced_factories | 16 / 2 |
| 16 | 1.089369x | 1.258121x | qasmbench_medium_exact/gcm_h6.qasm | balanced_factories | 16 / 2 |
| 17 | 1.088463x | 1.254212x | qasmbench_medium_exact/gcm_h6.qasm | serial_factory | 16 / 2 |
| 18 | 1.087079x | 1.254362x | qasmbench_medium_exact/gcm_h6.qasm | throughput_heavy_factories | 16 / 2 |
| 19 | 1.085791x | 1.254016x | qasmbench_medium_exact/gcm_h6.qasm | throughput_heavy_factories | 16 / 2 |
| 20 | 1.086008x | 1.253640x | qasmbench_medium_exact/gcm_h6.qasm | throughput_heavy_factories | 16 / 2 |

## Portfolio Thresholds

- Target 1.200x: max arbitrary-rotation T cost None (min row `n/a` / `n/a`)
- Target 1.250x: max arbitrary-rotation T cost None (min row `n/a` / `n/a`)

## Next Actions

- Implement a gcm_h6-targeted arbitrary-rotation synthesis ledger with precision/error budgeting.
- Try a semantic-preserving numeric rotation merge/cancellation pass for adjacent or commute-safe rotations.
- If no local pass can reduce the 270 arbitrary numeric rotations, record a negative boundary for local phase passes.

## Limits

- This analysis sweeps synthesis costs inside the existing B7 ledger; it is not a physical layout result.
- Lower arbitrary-rotation costs must later be justified by a precision-aware FT synthesis method.
- Removing arbitrary rotations here means equivalent T-ledger reduction, not necessarily deleting QASM gates.
