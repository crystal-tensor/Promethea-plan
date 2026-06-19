# B1/B7 Cone_01 Packet Replay Resource Gate

Status: `cone01_packet_replay_resource_accounting_rejects_ledger_acceptance`

This artifact consumes T-B1-004ae/T-B1-004af and asks whether the reduced-CNOT packet candidates can be accepted after local-U3 resource accounting.

## Summary

- Packets checked: `3`
- Bounded packet replay numerically consistent: `3`
- Candidate CNOT reduction if accepted: `9`
- Source off-grid parameter count: `1`
- Replacement local U3 gates / parameters / off-grid parameters: `16` / `48` / `40`
- Incremental off-grid parameters / proxy-T pressure: `39` / `780`
- Accepted full-circuit replay certificates: `0`
- Accepted occurrence/proxy-T reduction: `0` / `0`
- Validation errors: `0`

## Packet Rows

| Candidate line | Source CX | Replacement CX | CNOT delta | Source off-grid params | Replacement off-grid params | Incremental proxy-T pressure | Accepted replay |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1378 | 4 | 1 | 3 | 0 | 10 | 200 | False |
| 1381 | 5 | 2 | 3 | 1 | 15 | 280 | False |
| 268 | 5 | 2 | 3 | 0 | 15 | 300 | False |

## Claim Boundary

The reduced-CNOT packet candidates are useful synthesis evidence, but they are not accepted B7 savings. The local U3 replacements introduce off-grid synthesis pressure that is larger than the off-grid burden in the source windows, and no symbolic exact decomposition or full-circuit QASM replay certificate has been emitted.

## Next Required Gate

The next route must either exactify the local U3 layers into a cheaper Clifford+T/native basis, absorb them into surrounding circuit context with replay certificates, or abandon this reduced-CNOT scaffold in favor of a route that lowers the actual B7 ledger.
