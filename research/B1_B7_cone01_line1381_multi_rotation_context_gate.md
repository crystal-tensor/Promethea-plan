# B1/B7 Cone_01 Line-1381 Multi-Rotation Context Gate

Status: `cone01_line1381_multi_rotation_context_not_accepted`

This artifact consumes T-B1-004ao and tests whether the five remaining line-1381 local-U3 parameters can be absorbed by signed sums of two or three nearby same-support context rotations in the native optimized `gcm_h6` QASM.

## Summary

- Target candidate line: `1381`
- Support qubits: `[4, 8]`
- Source window: `1369`-`1379`
- Context radius: `+/-64` lines
- Context rotation arguments reviewed: `44`
- Parameters tested: `5`
- Signed combinations per parameter, width 2 / width 3: `3784` / `105952`
- Total signed combination tests: `548680`
- Width-2 / width-3 exact absorption parameters: `0` / `0`
- Min best width-2 / width-3 grid error: `2.746555212048e-03` / `1.581991109334e-03`
- Accepted replay / occurrence / proxy-T reduction: `0` / `0` / `0`
- Validation errors: `0`

## Parameter Rows

| Param index | Value/pi | Best width-2 error | Best width-3 error | Best overall width | Accepted |
|---:|---:|---:|---:|---:|---|
| 3 | 0.454632085623 | 2.665955e-02 | 2.665955e-02 | 3 | False |
| 4 | -0.365263446443 | 2.746555e-03 | 2.746555e-03 | 2 | False |
| 9 | -0.335026659005 | 1.576537e-02 | 1.576537e-02 | 2 | False |
| 16 | 0.177917927571 | 2.490124e-02 | 1.581991e-03 | 3 | False |
| 17 | 0.134736553557 | 2.746555e-03 | 2.746555e-03 | 2 | False |

## Claim Boundary

This closes only a bounded two-/three-rotation context-combination route. It does not rule out four-or-more-rotation symbolic absorption, commutation-aware rewriting, broader symbolic synthesis, or full-circuit replay. The B7 ledger remains unchanged at zero accepted occurrence removals and zero accepted proxy-T reduction.

## Next Required Gate

The next route must either build a commutation-aware symbolic/full-circuit replay certificate for the repaired packet route, or abandon this local context route and find a different occurrence-removing scaffold with honest B7 resource accounting.
