# B1/B7 Cone_01 Carrier Blocker Motif Gate

Status: `cone01_carrier_blocker_motif_negative_gate`

This artifact consumes T-B1-004aa and checks whether blocked source-aligned carrier candidates share a reusable CNOT-stack motif.

## Summary

- Blocker motif candidates: `3`
- Unique exact stack motifs: `3`
- Unique edge-family motifs: `2`
- Largest exact stack / edge-family candidate group: `1` / `2`
- Single-edge / mixed-edge stack candidates: `2` / `1`
- Cross-pattern motif present: `False`
- Template generalization gate passed: `False`
- Accepted occurrence/proxy-T reduction: `0` / `0`
- Validation errors: `0`

## Rows

| Pattern | Candidates | Exact motifs | Edge-family motifs | Largest exact | Largest family | Accepted motifs |
|---|---:|---:|---:|---:|---:|---:|
| flat_pattern_01 | 3 | 3 | 2 | 1 | 2 | 0 |
| flat_pattern_02 | 0 | 0 | 0 | 0 | 0 | 0 |
| flat_pattern_03 | 0 | 0 | 0 | 0 | 0 | 0 |

## Claim Boundary

- The exact blocker stacks are three distinct motifs.
- The largest edge-family group covers only two candidates and no cross-pattern motif exists.
- No CNOT-stack template rewrite, semantic replay, occurrence removal, or B7 ledger improvement is claimed.
