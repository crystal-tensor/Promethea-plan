# B1/B7 Cone_01 Three-CNOT Multi-Rotation Context Gate

Status: `cone01_three_cnot_multi_rotation_context_not_accepted`

This artifact consumes T-B1-004br and tests whether the 18 off-pi/4 local-U3 parameters in the best exact 3-CNOT priced candidate can be absorbed by signed sums of two or three nearby same-support context rotations in the native optimized `gcm_h6` QASM.

## Summary

- Selected sequence: `10-10-01`
- Selected off-grid parameters / proxy-T pressure: `18` / `360`
- Source window: `[1369, 1379]`
- Context radius: `+/-64` lines
- Context rotation arguments reviewed: `44`
- Parameters tested: `18`
- Signed combinations per parameter, width 2 / width 3: `3784` / `105952`
- Total signed combination tests: `1975248`
- Width-2 / width-3 exact absorption parameters: `0` / `0`
- Min best width-2 / width-3 grid error: `6.557999011454e-04` / `6.557999011454e-04`
- Accepted replay / occurrence / proxy-T reduction: `0` / `0` / `0`
- Validation errors: `0`

## Parameter Rows

| Param index | Value/pi | Best width-2 error | Best width-3 error | Best overall width | Accepted |
|---:|---:|---:|---:|---:|---|
| 2 | -0.465712363752 | 5.203433e-02 | 5.785812e-03 | 3 | False |
| 3 | 0.484317257958 | 6.414673e-03 | 6.414673e-03 | 3 | False |
| 4 | -0.814501764722 | 6.967977e-03 | 6.967977e-03 | 2 | False |
| 5 | -0.844984590994 | 3.997122e-02 | 3.997122e-02 | 3 | False |
| 7 | -0.367945756891 | 5.680172e-03 | 5.680172e-03 | 2 | False |
| 8 | 0.632054243109 | 5.680172e-03 | 5.680172e-03 | 3 | False |
| 9 | -0.750743960797 | 2.337222e-03 | 2.337222e-03 | 2 | False |
| 10 | 0.618913741868 | 8.721186e-03 | 8.721186e-03 | 3 | False |
| 11 | 0.509154655999 | 2.692326e-02 | 2.276965e-03 | 3 | False |
| 13 | -0.999791252408 | 6.557999e-04 | 6.557999e-04 | 2 | False |
| 15 | -0.704988646181 | 2.777972e-02 | 2.777972e-02 | 3 | False |
| 16 | -0.318066903839 | 1.816819e-02 | 1.103203e-02 | 3 | False |
| 17 | -0.131454105108 | 7.565561e-03 | 7.565561e-03 | 2 | False |
| 19 | 0.166037819118 | 1.242122e-02 | 1.242122e-02 | 2 | False |
| 20 | -0.299883292226 | 1.247407e-02 | 1.247407e-02 | 3 | False |
| 21 | -0.837381112213 | 2.316211e-02 | 2.316211e-02 | 2 | False |
| 22 | 0.674031978995 | 1.269318e-02 | 1.269318e-02 | 2 | False |
| 23 | -0.662316278828 | 2.411278e-02 | 2.411278e-02 | 2 | False |

## Claim Boundary

This closes only a bounded two-/three-rotation context-combination route for the direct 3-CNOT candidate. It does not rule out four-or-more-rotation symbolic absorption, commutation-aware rewriting, broader symbolic synthesis, or full-circuit replay. The B7 ledger remains unchanged at zero accepted occurrence removals and zero accepted proxy-T reduction.

## Next Required Gate

The next route must either build a different scaffold that beats the current 5-parameter / 100-proxy-T line-1381 boundary, attempt a justified four-or-more-rotation symbolic absorption route, or abandon this direct 3-CNOT route for another occurrence-removing scaffold with honest B7 resource accounting.
