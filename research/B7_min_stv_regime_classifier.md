# B7 Minimum-STV Regime Classifier v0.1

Last updated: 2026-06-15

Status: **min_stv_regime_classified_not_physical_layout_claim**

## Summary

- Source schedule: `results/B7_logical_t_factory_schedule_u3_phase_factored_v0.json`
- Comparisons: 18
- Workloads: 6
- Minimum STV reduction: 1.121951x
- Minimum workload: `qasmbench_medium_exact/sat_n11.qasm`
- Factory-bottleneck after rows: 18
- Deep factory-locked rows: 10
- Interpretation: The remaining minimum-STV row is factory-path dominated; U3 phase factoring improved portfolio mean STV but did not move the sat_n11 minimum row beyond the control-RZ boundary.

## Minimum Rows

| workload | variant | regime | STV reduction | T reduction | after T | after factory/data rounds | T to drop one batch |
|---|---|---|---:|---:|---:|---:|---:|
| qasmbench_medium_exact/sat_n11.qasm | throughput_heavy_factories | factory_locked_near_data_path | 1.121951x | 1.122137x | 5240 | 5240 / 1194 | 8 |

## Target Removal Requirements

| workload | variant | target STV | max after T proxy | additional T proxy to remove | needs data path reduction |
|---|---|---:|---:|---:|---|
| qasmbench_medium_exact/sat_n11.qasm | throughput_heavy_factories | 1.200x | 4896 | 344 | False |
| qasmbench_medium_exact/sat_n11.qasm | throughput_heavy_factories | 1.250x | 4696 | 544 | False |

## Workload Ranking

| workload | min STV | mean STV | min variant | regimes | all factory bottleneck |
|---|---:|---:|---|---|---|
| qasmbench_medium_exact/sat_n11.qasm | 1.121951x | 1.122045x | throughput_heavy_factories | factory_locked_deep, factory_locked_near_data_path | True |
| qasmbench_medium_exact/gcm_h6.qasm | 1.163527x | 1.163583x | balanced_factories | factory_locked_deep, factory_locked_near_data_path | True |
| aggregate_30_circuits | 1.181842x | 1.181865x | balanced_factories | factory_locked_deep, factory_locked_near_data_path | True |
| qasmbench_small/hhl_n7.qasm | 1.230216x | 1.230848x | throughput_heavy_factories | factory_locked_deep, factory_locked_near_data_path | True |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | 1.352423x | 1.352685x | throughput_heavy_factories | factory_locked_deep, factory_locked_near_data_path | True |
| qasmbench_medium_exact/qf21_n15.qasm | 1.354730x | 1.355337x | throughput_heavy_factories | factory_locked_deep, factory_locked_near_data_path | True |

## Stage Progression For Minimum Workload

| stage | min STV | mean STV | min T-count reduction | mean T-count reduction |
|---|---:|---:|---:|---:|
| virtual_swap | 1.000000x | 1.000000x | 1.000000x | 1.000000x |
| post_1q | 1.000000x | 1.000000x | 1.000000x | 1.000000x |
| native_z | 1.000000x | 1.000000x | 1.000000x | 1.000000x |
| control_rz | 1.121951x | 1.122045x | 1.122137x | 1.122137x |
| u3_phase_factored | 1.121951x | 1.122045x | 1.122137x | 1.122137x |

## Next Actions

- Attack sat_n11 logical T-count directly or prove it is a negative boundary for the current local phase passes.
- Replace fixed-cost rotation proxy with a fault-tolerant synthesis ledger to test whether pi/4, arbitrary, and unknown rotations have different factory pressure.
- Add physical layout and feed-forward assumptions before promoting any B7 result beyond proxy status.

## Limits

- This classifier consumes B7 logical T-factory schedule rows; it is not a physical layout or lattice-surgery result.
- The target-removal calculation assumes the same factory variant and total physical qubit footprint.
- Logical T-count proxy uses the scheduler fixed rotation cost and should not be treated as a calibrated synthesis cost.
