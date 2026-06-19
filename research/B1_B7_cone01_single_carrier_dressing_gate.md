# B1/B7 Cone 01 Single-Carrier Local Dressing Gate

Status: `cone01_single_carrier_exact_packet_not_resource_certificate`

This artifact performs a finite route check: one theta- or delta-derived local carrier rotation is wrapped by pair-local Cliffords and tested against each residual flat packet. All three packets exactify, but this is still not an occurrence-removing rewrite or resource-saving claim because one arbitrary local carrier remains.

## Summary

- Carrier sources: `theta, theta_delta`
- Carrier coefficients: `-2.0, -1.0, -0.5, 0.5, 1.0, 2.0`
- Pair-local Clifford representatives: `576`
- Pattern groups: `3`
- Total single-carrier trials: `143327232`
- Single-carrier exact packets: `3`
- Best/max best single-carrier residual: `3.2009291313835888e-16` / `4.677452743560217e-16`
- Accepted occurrence removal: `0`
- Missing occurrences after this gate: `30`

## Pattern Results

| Pattern | Occurrences | Carrier variants | Trials | Best residual | Exact passes | Best carrier | Best side | Best left | Best right |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| flat_pattern_01 | 8 | 72 | 47775744 | `4.67745274356e-16` | 32 | `1.0*theta_delta X[target]` | `right` | `I|I` | `I|I` |
| flat_pattern_02 | 2 | 72 | 47775744 | `4.29987528495e-16` | 32 | `-1.0*theta_delta X[target]` | `left` | `I|I` | `I|I` |
| flat_pattern_03 | 1 | 72 | 47775744 | `3.20092913138e-16` | 128 | `-1.0*theta X[target]` | `left` | `I|SSHSSH` | `I|SS` |

## Claim Boundary

- A single-carrier local-Clifford-wrapped exact packet was found for each of the three packets.
- Accepted occurrence removal and accepted proxy-T reduction remain 0.
- The carrier is still an arbitrary local rotation, so this does not clear the B7 occurrence ledger.
- No semantic rewrite, resource saving, or B7 ledger improvement is claimed.

Validation error count: `0`
