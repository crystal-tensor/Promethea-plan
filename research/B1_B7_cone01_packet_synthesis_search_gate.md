# B1/B7 Cone_01 Packet Synthesis Search Gate

Status: `cone01_packet_synthesis_search_candidate_not_replay_certificate`

This artifact consumes T-B1-004ae and searches fixed-direction reduced-CNOT scaffolds with arbitrary local U3 layers against the three exact packet unitary targets.

## Summary

- Packets searched: `3`
- Scaffolds searched: `12`
- Optimizer seeds per scaffold: `10`
- Exact reduced-CNOT scaffold packets: `3`
- Minimum exact reduced CNOT count: `1`
- Candidate CNOT reduction if accepted: `9`
- Accepted replay certificates: `0`
- Accepted occurrence/proxy-T reduction: `0` / `0`
- Validation errors: `0`

## Packet Rows

| Candidate line | Source CX | Best residual | Exact reduced scaffold | Best exact CX | Candidate CX reduction | Accepted replay |
|---:|---:|---:|---|---:|---:|---|
| 1378 | 4 | 9.051e-13 | True | 1 | 3 | False |
| 1381 | 5 | 5.935e-13 | True | 2 | 3 | False |
| 268 | 5 | 4.537e-13 | True | 2 | 3 | False |

## Claim Boundary

A reduced-CNOT numerical scaffold is not yet an accepted rewrite. The current gate does not emit a symbolic exact decomposition, does not replay a candidate inside the full `gcm_h6` circuit, does not price the new local U3 layers, and does not change the B7 ledger.

## Next Required Gate

The next gate must convert any numerical reduced-CNOT candidate into a replayable full-circuit certificate with explicit local-layer resource accounting, or prove that the searched scaffold cannot support an accepted occurrence-removing rewrite.
