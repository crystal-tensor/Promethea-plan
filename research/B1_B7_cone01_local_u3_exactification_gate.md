# B1/B7 Cone_01 Local-U3 Exactification Gate

Status: `cone01_local_u3_exactification_negative_gate`

This artifact consumes T-B1-004af/T-B1-004ag and tests whether the arbitrary local-U3 replacement layers can be cheaply exactified by direct pi/4-grid snapping.

## Summary

- Packets checked: `3`
- Exact pi/4-snap passes/fails: `0` / `3`
- Snapped residual range: `4.757435e-01` - `7.803613e-01`
- Candidate CNOT reduction if accepted: `9`
- Replacement off-grid local-U3 parameters before snapping: `40`
- Accepted exactified off-grid parameters: `0`
- Residual resource-burden parameters: `40`
- Accepted occurrence/proxy-T reduction: `0` / `0`
- Validation errors: `0`

## Packet Rows

| Candidate line | Replacement CX | Projected off-grid params | Snapped residual | Exact pass | Accepted absorption |
|---:|---:|---:|---:|---|---|
| 1378 | 1 | 10 | 7.803613e-01 | False | False |
| 1381 | 2 | 15 | 4.757435e-01 | False | False |
| 268 | 2 | 15 | 7.803613e-01 | False | False |

## Claim Boundary

Direct pi/4 snapping does put the replacement local-U3 parameters on the cheap grid, but it breaks the bounded packet replay for all three packets. Therefore this artifact does not accept the reduced-CNOT route as a symbolic exact decomposition, an absorption certificate, a full-circuit rewrite, or a B7 ledger improvement.

## Next Required Gate

The next route must use a stronger exact synthesis/absorption mechanism than direct snapping, or abandon this reduced-CNOT scaffold and search for an occurrence-removing route that lowers the actual gcm_h6 B7 ledger.
