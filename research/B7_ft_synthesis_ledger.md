# B7 FT Synthesis Ledger v0.1

Last updated: 2026-06-15

Status: **ft_synthesis_ledger_proxy_not_physical_layout**

## Summary

- Workloads: 6
- Factory variants: ['balanced_factories', 'serial_factory', 'throughput_heavy_factories']
- Comparisons: 18
- Minimum STV reduction: 1.086008x
- Mean STV reduction: 1.253640x
- Minimum row: `qasmbench_medium_exact/gcm_h6.qasm` / `throughput_heavy_factories`
- Minimum row bottleneck before/after: factory_path -> factory_path
- After rows bottlenecked by factory/data: 16 / 2
- Minimum logical T-count ledger reduction: 1.086118x
- Mean logical T-count ledger reduction: 1.199722x

## Cost Model

- clifford_rotation_t_cost: 0
- pi_over_4_rotation_t_cost: 1
- pi_over_8_rotation_t_cost: 4
- arbitrary_rotation_t_cost: 20
- unknown_rotation_t_cost: 20
- ccx_t_cost: 7

## Resource Ledger By Workload

| workload | before T ledger | after T ledger | T reduction | after families | after T cost by family |
|---|---:|---:|---:|---|---|
| aggregate_30_circuits | 31607 | 26928 | 1.17376x | `{'arbitrary_numeric_rotation': 1270, 'clifford_rotation': 2242, 'exact_pi_over_4_rotation': 1280, 'exact_pi_over_8_rotation': 62}` | `{'arbitrary_numeric_rotation': 25400, 'clifford_rotation': 0, 'exact_pi_over_4_rotation': 1280, 'exact_pi_over_8_rotation': 248}` |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | 6740 | 5060 | 1.33202x | `{'arbitrary_numeric_rotation': 252, 'clifford_rotation': 822, 'exact_pi_over_4_rotation': 20}` | `{'arbitrary_numeric_rotation': 5040, 'clifford_rotation': 0, 'exact_pi_over_4_rotation': 20}` |
| qasmbench_medium_exact/gcm_h6.qasm | 6760 | 6224 | 1.08612x | `{'arbitrary_numeric_rotation': 270, 'clifford_rotation': 476, 'exact_pi_over_4_rotation': 792, 'exact_pi_over_8_rotation': 8}` | `{'arbitrary_numeric_rotation': 5400, 'clifford_rotation': 0, 'exact_pi_over_4_rotation': 792, 'exact_pi_over_8_rotation': 32}` |
| qasmbench_medium_exact/qf21_n15.qasm | 1828 | 1442 | 1.26768x | `{'arbitrary_numeric_rotation': 67, 'clifford_rotation': 65, 'exact_pi_over_4_rotation': 34, 'exact_pi_over_8_rotation': 17}` | `{'arbitrary_numeric_rotation': 1340, 'clifford_rotation': 0, 'exact_pi_over_4_rotation': 34, 'exact_pi_over_8_rotation': 68}` |
| qasmbench_medium_exact/sat_n11.qasm | 294 | 262 | 1.12214x | `{'clifford_rotation': 131, 'exact_pi_over_4_rotation': 262}` | `{'clifford_rotation': 0, 'exact_pi_over_4_rotation': 262}` |
| qasmbench_small/hhl_n7.qasm | 7453 | 6126 | 1.21662x | `{'arbitrary_numeric_rotation': 303, 'clifford_rotation': 89, 'exact_pi_over_4_rotation': 18, 'exact_pi_over_8_rotation': 12}` | `{'arbitrary_numeric_rotation': 6060, 'clifford_rotation': 0, 'exact_pi_over_4_rotation': 18, 'exact_pi_over_8_rotation': 48}` |

## Schedule Comparisons

| workload | factory variant | bottleneck before | bottleneck after | STV reduction | T-count reduction | before/after T ledger |
|---|---|---|---|---:|---:|---:|
| aggregate_30_circuits | serial_factory | factory_path | factory_path | 1.173755x | 1.17376x | 31607 / 26928 |
| aggregate_30_circuits | balanced_factories | factory_path | factory_path | 1.173776x | 1.17376x | 31607 / 26928 |
| aggregate_30_circuits | throughput_heavy_factories | factory_path | factory_path | 1.173745x | 1.17376x | 31607 / 26928 |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | serial_factory | factory_path | factory_path | 1.331972x | 1.33202x | 6740 / 5060 |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | balanced_factories | factory_path | factory_path | 1.331806x | 1.33202x | 6740 / 5060 |
| qasmbench_interaction_exact/basis_trotter_n4.qasm | throughput_heavy_factories | factory_path | factory_path | 1.331230x | 1.33202x | 6740 / 5060 |
| qasmbench_medium_exact/gcm_h6.qasm | serial_factory | factory_path | factory_path | 1.086109x | 1.08612x | 6760 / 6224 |
| qasmbench_medium_exact/gcm_h6.qasm | balanced_factories | factory_path | factory_path | 1.086074x | 1.08612x | 6760 / 6224 |
| qasmbench_medium_exact/gcm_h6.qasm | throughput_heavy_factories | factory_path | factory_path | 1.086008x | 1.08612x | 6760 / 6224 |
| qasmbench_medium_exact/qf21_n15.qasm | serial_factory | factory_path | factory_path | 1.267560x | 1.26768x | 1828 / 1442 |
| qasmbench_medium_exact/qf21_n15.qasm | balanced_factories | factory_path | factory_path | 1.265340x | 1.26768x | 1828 / 1442 |
| qasmbench_medium_exact/qf21_n15.qasm | throughput_heavy_factories | factory_path | factory_path | 1.263736x | 1.26768x | 1828 / 1442 |
| qasmbench_medium_exact/sat_n11.qasm | serial_factory | factory_path | factory_path | 1.121827x | 1.12214x | 294 / 262 |
| qasmbench_medium_exact/sat_n11.qasm | balanced_factories | data_path | data_path | 1.611481x | 1.12214x | 294 / 262 |
| qasmbench_medium_exact/sat_n11.qasm | throughput_heavy_factories | data_path | data_path | 1.611481x | 1.12214x | 294 / 262 |
| qasmbench_small/hhl_n7.qasm | serial_factory | factory_path | factory_path | 1.216594x | 1.21662x | 7453 / 6126 |
| qasmbench_small/hhl_n7.qasm | balanced_factories | factory_path | factory_path | 1.216597x | 1.21662x | 7453 / 6126 |
| qasmbench_small/hhl_n7.qasm | throughput_heavy_factories | factory_path | factory_path | 1.216428x | 1.21662x | 7453 / 6126 |

## Limits

- This ledger classifies exact Pauli rotations by angle family; it is not a lattice-surgery or physical layout result.
- Exact odd pi/4 rotations are counted as one T gate using Clifford conjugation for X/Y axes.
- Unknown, symbolic, and arbitrary numeric rotations retain conservative fixed fallback costs.
- Data-path dominance after re-costing does not prove solved architecture; it identifies the next bottleneck after factory pressure is reduced.
