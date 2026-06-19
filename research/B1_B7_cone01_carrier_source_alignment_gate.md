# B1/B7 Cone_01 Carrier Source Alignment Gate

Status: `cone01_carrier_source_alignment_negative_gate`

This artifact consumes T-B1-004y and checks whether nearby carrier candidates align with their nearest source lines.

## Summary

- Reviewed radius-16 candidates: `5`
- Blocker-free radius-16 candidates: `1`
- Source-qubit-aligned candidates: `3`
- Blocker-free and source-qubit-aligned candidates: `0`
- Accepted source-alignment certificates: `0`
- Accepted occurrence/proxy-T reduction: `0` / `0`
- Validation errors: `0`

## Rows

| Pattern | Reviewed | Blocker-free | Source-aligned | Blocker-free source-aligned | Accepted |
|---|---:|---:|---:|---:|---:|
| flat_pattern_01 | 5 | 1 | 3 | 0 | 0 |
| flat_pattern_02 | 0 | 0 | 0 | 0 | 0 |
| flat_pattern_03 | 0 | 0 | 0 | 0 | 0 |

## Claim Boundary

- The only blocker-free radius-16 candidate is not aligned with the nearest source-line qubit.
- A source-line alignment pass would still be only a replay precondition.
- No commutation, semantic rewrite, occurrence removal, or B7 ledger improvement is claimed.
