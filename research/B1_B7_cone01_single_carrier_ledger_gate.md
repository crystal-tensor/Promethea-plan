# B1/B7 Cone_01 Single-Carrier Ledger Pressure Gate

Status: `cone01_single_carrier_ledger_pressure_not_accepted_reduction`

This artifact consumes the exact single-carrier packets from T-B1-004u and applies the current B7 occurrence-ledger rule. The result is a ledger boundary: the carrier exactifies the three packets, but it replaces rather than removes arbitrary occurrences unless a later certificate absorbs or shares the carrier.

## Summary

- Source exact packets: `3`
- Pattern groups / covered occurrences: `3` / `11`
- Unique carrier signatures: `3`
- All best carriers target-X: `True`
- Per-occurrence inserted carrier occurrences: `11`
- Net arbitrary occurrence delta under current ledger: `0`
- Optimistic template carriers / duplicate occurrences: `3` / `8`
- Optimistic template proxy-T reuse: `160`
- Max removals if all carriers are later absorbed: `11`
- Missing occurrences even if all carriers are absorbed: `19`
- Accepted occurrence/proxy-T reduction: `0` / `0`
- Validation errors: `0`

## Carrier Rows

| Pattern | Occurrences | Carrier | Ledger inserted | Net delta | Optimistic duplicates | Accepted reduction |
|---|---:|---|---:|---:|---:|---:|
| flat_pattern_01 | 8 | `1.0*theta_delta X[target]/right` | 8 | 0 | 7 | 0 |
| flat_pattern_02 | 2 | `-1.0*theta_delta X[target]/left` | 2 | 0 | 1 | 0 |
| flat_pattern_03 | 1 | `-1.0*theta X[target]/left` | 1 | 0 | 0 | 0 |

## Claim Boundary

- Single-carrier exact packets are confirmed from T-B1-004u.
- Under the current per-occurrence ledger, they insert 11 carrier occurrences for 11 covered original occurrences.
- Accepted occurrence removal and proxy-T reduction remain 0.
- Even a future absorption of all 11 would still miss the 30-occurrence B7 target by 19 occurrences.
- No rewrite, semantic certificate, physical cost model, or B7 ledger improvement is claimed.
