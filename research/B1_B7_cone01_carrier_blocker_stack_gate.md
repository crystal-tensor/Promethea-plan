# B1/B7 Cone_01 Carrier Blocker Stack Gate

Status: `cone01_carrier_blocker_stack_negative_gate`

This artifact consumes T-B1-004z and checks whether source-aligned carrier candidates can be cleared by a simple blocker-stack condition.

## Summary

- Source-aligned candidates: `3`
- Source-aligned blocked candidates: `3`
- Target-touching CNOT blockers across source-aligned candidates: `15`
- Candidate-qubit blockers / other target blockers: `14` / `1`
- Unique blocker lines: `11`
- Unique blocker edge signatures: `10-14, 2-14, 4-8`
- Accepted simple commutation-clearance certificates: `0`
- Accepted occurrence/proxy-T reduction: `0` / `0`
- Validation errors: `0`

## Rows

| Pattern | Source-aligned | Blocked | Target CNOT blockers | Candidate-qubit blockers | Other target blockers | Accepted |
|---|---:|---:|---:|---:|---:|---:|
| flat_pattern_01 | 3 | 3 | 15 | 14 | 1 | 0 |
| flat_pattern_02 | 0 | 0 | 0 | 0 | 0 | 0 |
| flat_pattern_03 | 0 | 0 | 0 | 0 | 0 | 0 |

## Claim Boundary

- Every source-aligned candidate is blocked by target-touching CNOTs.
- Fourteen of fifteen blockers touch the candidate qubit directly, so this is not a single-qubit commute-through issue.
- No blocker-clearance, commutation, semantic rewrite, occurrence removal, or B7 ledger improvement is claimed.
