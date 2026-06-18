# B7 gcm_h6 Numeric-Rotation Structure v0.1

Last updated: 2026-06-15

Status: **gcm_h6_numeric_rotation_structure_negative_boundary_not_physical_layout**

## Summary

- Source ledger: `results/B7_ft_synthesis_ledger_v0.json`
- Input QASM: `results/b1_u3_phase_factored_optimizer/qasmbench_medium_exact/gcm_h6.qasm`
- Output QASM: `results/b7_gcm_h6_numeric_rotation_structure/qasmbench_medium_exact/gcm_h6.qasm`
- Proof log: `results/b7_gcm_h6_numeric_rotation_structure/proofs.jsonl`
- Aer cross-check: `results/b7_gcm_h6_numeric_rotation_structure/aer_crosscheck.json`
- Rewrite rule: `same_axis_numeric_rotation_merge_disjoint_only`
- Arbitrary numeric rotations before/after/removed: 270 / 270 / 0
- Logical T ledger before/after/removed: 6224 / 6224 / 0
- Clears 1.20x all-variant min: False
- Clears 1.20x gcm_h6 min: False
- Interpretation: The conservative same-axis local pass does not reduce gcm_h6 arbitrary numeric rotations.

## Rewrite Summary

- input: `results/b1_u3_phase_factored_optimizer/qasmbench_medium_exact/gcm_h6.qasm`
- output: `results/b7_gcm_h6_numeric_rotation_structure/qasmbench_medium_exact/gcm_h6.qasm`
- absorbed_rotation_gates: `1546`
- certificate_entries: `172`
- merge_or_move_groups: `172`
- removed_rotation_gates: `0`
- zero_output_groups: `0`

## Rotation Family Delta Removed

| family | removed | before | after |
|---|---:|---:|---:|
| arbitrary_numeric_rotation | 0 | 270 | 270 |
| clifford_rotation | 0 | 476 | 476 |
| exact_pi_over_4_rotation | 0 | 792 | 792 |
| exact_pi_over_8_rotation | 0 | 8 | 8 |

## Portfolio Retest

- Min STV reduction: 1.086008x
- Mean STV reduction: 1.253640x
- Min row: `qasmbench_medium_exact/gcm_h6.qasm` / `throughput_heavy_factories`
- gcm_h6 min STV reduction: 1.086008x
- gcm_h6 min variant: `throughput_heavy_factories`
- After factory/data bottleneck rows: 16 / 2

## Next Actions

- If this is negative, test a nonlocal phase-polynomial or template-aware pass rather than more local same-axis merging.
- Separately test whether repeated-angle shared synthesis is only a classical compilation cache or can change a fault-tolerant resource ledger.
- Keep B7 claims marked as proxy until layout, feed-forward, factory, and certified synthesis assumptions are explicit.

## Limits

- This pass only commutes rotations across operations on disjoint qubits.
- It does not commute through CNOTs or different-axis rotations.
- It is not a certified Clifford+T synthesis or physical layout result.
- The retest changes only the gcm_h6 after-side QASM resource row inside the existing FT ledger.
