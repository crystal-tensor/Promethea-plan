# B1/B7 Cone 01 Local Clifford Dressing Gate

Status: `cone01_local_clifford_dressing_negative_gate`

This artifact performs a complete finite search over local Clifford dressings on both sides of each nearest-grid representative. It is a negative certificate route check, not a rewrite or resource-saving claim.

## Summary

- Single-qubit Clifford representatives: `24`
- Pair-local Clifford representatives: `576`
- Left/right pair trials per pattern: `331776`
- Pattern groups: `3`
- Covered invariant-flat occurrences: `11`
- Local Clifford exact packets: `0`
- Best/max best local-Clifford residual: `0.2125365671136259` / `0.3643516233170526`
- Accepted occurrence removal: `0`
- Missing occurrences after this gate: `30`

## Pattern Results

| Pattern | Occurrences | Grid | Same-envelope residual | Best Clifford residual | Exact Clifford passes | Best left | Best right |
|---|---:|---|---:|---:|---:|---|---|
| flat_pattern_01 | 8 | `-7*pi/4` | `0.364351623317` | `0.364351623317` | `0` | `HSSH|SSHSSH` | `HSSH|SSSHS` |
| flat_pattern_02 | 2 | `-7*pi/4` | `0.212536567114` | `0.212536567114` | `0` | `HSSH|HSSH` | `HSSH|HSSH` |
| flat_pattern_03 | 1 | `-4*pi/4` | `0.327756333139` | `0.327756333139` | `0` | `HSSH|SSHSSH` | `HSSH|SSHSSH` |

## Claim Boundary

- No exact local Clifford dressing was found for the three packets.
- Accepted occurrence removal and accepted proxy-T reduction remain 0.
- This does not rule out non-Clifford exact dressing or a broader two-qubit rewrite.
- No local Clifford certificate, semantic rewrite, resource saving, or B7 ledger improvement is claimed.

Validation error count: `0`
