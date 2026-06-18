# B7 Workload-DAG Factory-Throughput Schedule v0.1

Last updated: 2026-06-13

Status: **workload_dag_factory_schedule_not_physical_layout**

## Summary

- Workloads: 6
- Factory variants: ['balanced_factories', 'serial_factory', 'throughput_heavy_factories']
- Comparisons: 18
- Magic-state density proxy: 0.5
- Minimum STV reduction: 1.194x
- Mean STV reduction: 1.475x
- Comparisons with a factory bottleneck: 6

## Comparisons

| workload | factory variant | bottleneck before | bottleneck after | critical path reduction | STV reduction | magic demand reduction |
|---|---|---|---|---:|---:|---:|
| aggregate_30_circuits | serial_factory | factory_path | factory_path | 1.592x | 1.592x | 1.592x |
| aggregate_30_circuits | balanced_factories | data_path | data_path | 1.321x | 1.321x | 1.592x |
| aggregate_30_circuits | throughput_heavy_factories | data_path | data_path | 1.321x | 1.321x | 1.592x |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | serial_factory | factory_path | factory_path | 1.446x | 1.446x | 1.448x |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | balanced_factories | data_path | data_path | 1.194x | 1.194x | 1.448x |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | throughput_heavy_factories | data_path | data_path | 1.194x | 1.194x | 1.448x |
| qasmbench_medium_exact/gcm_h6.qasm | serial_factory | factory_path | factory_path | 1.594x | 1.594x | 1.595x |
| qasmbench_medium_exact/gcm_h6.qasm | balanced_factories | data_path | data_path | 1.318x | 1.318x | 1.595x |
| qasmbench_medium_exact/gcm_h6.qasm | throughput_heavy_factories | data_path | data_path | 1.318x | 1.318x | 1.595x |
| qasmbench_medium_exact/qf21_n15.qasm | serial_factory | factory_path | factory_path | 2.234x | 2.234x | 2.246x |
| qasmbench_medium_exact/qf21_n15.qasm | balanced_factories | data_path | data_path | 1.464x | 1.464x | 2.246x |
| qasmbench_medium_exact/qf21_n15.qasm | throughput_heavy_factories | data_path | data_path | 1.464x | 1.464x | 2.246x |
| qasmbench_medium_exact/sat_n11.qasm | serial_factory | factory_path | factory_path | 1.975x | 1.975x | 1.980x |
| qasmbench_medium_exact/sat_n11.qasm | balanced_factories | data_path | data_path | 1.611x | 1.611x | 1.980x |
| qasmbench_medium_exact/sat_n11.qasm | throughput_heavy_factories | data_path | data_path | 1.611x | 1.611x | 1.980x |
| qasmbench_small/hhl_n7.qasm | serial_factory | factory_path | factory_path | 1.488x | 1.488x | 1.491x |
| qasmbench_small/hhl_n7.qasm | balanced_factories | data_path | data_path | 1.200x | 1.200x | 1.491x |
| qasmbench_small/hhl_n7.qasm | throughput_heavy_factories | data_path | data_path | 1.200x | 1.200x | 1.491x |

## Limits

- This is a workload-DAG and factory-throughput schedule, not a lattice-surgery or physical-layout compiler.
- Magic-state demand is a two-qubit-gate density proxy, not a T-count extracted from a fault-tolerant logical circuit.
- Factory footprints and cycle rounds are scenario parameters, not hardware-calibrated measurements.
- The purpose is to test whether B1/B2 gains survive explicit factory throughput bottlenecks before investing in a full layout model.
