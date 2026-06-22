# B1/B7 cone_01 Non-Overlap Patch Subset Gate

## Summary

- Method: `b1_b7_cone01_nonoverlap_patch_subset_gate_v0`
- Status: `cone01_nonoverlap_bounded_patch_subset_not_full_circuit_replay`
- Input bounded patches / exact-pass patches: `3` / `3`
- Naive candidate CNOT reduction before overlap handling: `9`
- Selected non-overlap patches: `[268, 1381]`
- Dropped overlap patches: `[1378]`
- Selected candidate CNOT reduction: `6`
- Lost candidate CNOT reduction due to overlap: `3`
- Source / replacement dialect: `OPENQASM 2.0` / `OPENQASM 3 bounded snippets`
- Full-circuit QASM rewrite emitted: `False`
- Accepted full-circuit patch / replay / occurrence / proxy-T reduction: `0` / `0` / `0` / `0`
- Validation errors: `0`

## Selected Rows

| Line | Window | Support | CNOT delta | QASM3 lines | Off-grid params |
|---:|---|---|---:|---:|---:|
| 268 | 256-267 | [2, 14] | 3 | 9 | 0 |
| 1381 | 1369-1379 | [4, 8] | 3 | 9 | 5 |

## Dropped Rows

| Line | Window | Reason |
|---:|---|---|
| 1378 | 1369-1377 | contained in the selected line-1381 window under the same bounded patch family |

## Claim Boundary

The best non-overlapping bounded patch subset keeps line 1381 and line 268, dropping line 1378 because its window is contained inside the line-1381 window.

Unsupported claims:

- The selected bounded subset is not yet a full-circuit QASM rewrite.
- The selected bounded subset is not yet a full-circuit replay certificate.
- The selected bounded subset does not recover the dropped line-1378 CNOT delta.
- No occurrence or proxy-T reduction is accepted by B7.

## Interpretation

This gate prevents double-counting the overlapping line-1378 and line-1381 bounded patch snippets. The best current composable bounded subset carries a candidate 6-CNOT reduction, not the naive 9-CNOT signal. Recovering the lost 3-CNOT delta requires a merged-region synthesis/replay gate or a different occurrence-removing route.
