# B7 Logical T-Resource Factory Schedule v0.1

Last updated: 2026-06-13

Status: **logical_t_factory_schedule_proxy_not_physical_layout**

## Summary

- Workloads: 6
- Factory variants: ['balanced_factories', 'serial_factory', 'throughput_heavy_factories']
- Comparisons: 18
- Rotation synthesis T-cost proxy: 20
- Minimum STV reduction: 1.000x
- Mean STV reduction: 1.035x
- Comparisons with factory bottleneck: 18
- Minimum logical T-count reduction: 1.000x
- Mean logical T-count reduction: 1.035x

## Comparisons

| workload | factory variant | bottleneck before | bottleneck after | STV reduction | T-count reduction | T-depth reduction |
|---|---|---|---|---:|---:|---:|
| aggregate_30_circuits | serial_factory | factory_path | factory_path | 1.019x | 1.019x | 1.190x |
| aggregate_30_circuits | balanced_factories | factory_path | factory_path | 1.019x | 1.019x | 1.190x |
| aggregate_30_circuits | throughput_heavy_factories | factory_path | factory_path | 1.019x | 1.019x | 1.190x |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | serial_factory | factory_path | factory_path | 1.150x | 1.150x | 1.046x |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | balanced_factories | factory_path | factory_path | 1.150x | 1.150x | 1.046x |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | throughput_heavy_factories | factory_path | factory_path | 1.150x | 1.150x | 1.046x |
| qasmbench_medium_exact/gcm_h6.qasm | serial_factory | factory_path | factory_path | 1.000x | 1.000x | 1.169x |
| qasmbench_medium_exact/gcm_h6.qasm | balanced_factories | factory_path | factory_path | 1.000x | 1.000x | 1.169x |
| qasmbench_medium_exact/gcm_h6.qasm | throughput_heavy_factories | factory_path | factory_path | 1.000x | 1.000x | 1.169x |
| qasmbench_medium_exact/qf21_n15.qasm | serial_factory | factory_path | factory_path | 1.039x | 1.039x | 1.632x |
| qasmbench_medium_exact/qf21_n15.qasm | balanced_factories | factory_path | factory_path | 1.039x | 1.039x | 1.632x |
| qasmbench_medium_exact/qf21_n15.qasm | throughput_heavy_factories | factory_path | factory_path | 1.039x | 1.039x | 1.632x |
| qasmbench_medium_exact/sat_n11.qasm | serial_factory | factory_path | factory_path | 1.000x | 1.000x | 1.114x |
| qasmbench_medium_exact/sat_n11.qasm | balanced_factories | factory_path | factory_path | 1.000x | 1.000x | 1.114x |
| qasmbench_medium_exact/sat_n11.qasm | throughput_heavy_factories | factory_path | factory_path | 1.000x | 1.000x | 1.114x |
| qasmbench_small/hhl_n7.qasm | serial_factory | factory_path | factory_path | 1.000x | 1.000x | 1.445x |
| qasmbench_small/hhl_n7.qasm | balanced_factories | factory_path | factory_path | 1.000x | 1.000x | 1.445x |
| qasmbench_small/hhl_n7.qasm | throughput_heavy_factories | factory_path | factory_path | 1.000x | 1.000x | 1.445x |

## Limits

- This is a logical T-resource proxy schedule, not a fault-tolerant synthesis result.
- Arbitrary u3/rz/rx/ry non-Clifford rotations are assigned a fixed T synthesis cost.
- The current B1 virtual-SWAP pass mostly removes CX/SWAP work, so T-resource reductions may be absent even when routing depth improves.
- The purpose is to expose when factory-dominated workloads erase routing/compression gains.
