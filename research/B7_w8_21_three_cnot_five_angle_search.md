# B7 w8_21 Three-CX Five-Angle Search

- Status: `three_cnot_five_angle_search_complete_no_exact_context_replay`
- Classification: `bounded_three_cnot_five_angle_resource_frontier`
- Families tested per context: `248`
- Contexts tested: `7`
- Optimizer runs: `3472`
- Exact context replays: `0/7`
- Best residual norm: `1.531091569077196`
- Payload hash: `02e5c14b99174ce311e20bffbaf5fcacffe035de1f2a01bd45ad3c4d00f71b51`

## Heuristic question

Can one additional CX replace the sixth arbitrary angle needed to absorb a non-grid external local rotation?

## Search scope

The candidate changes the nonlocal word itself: three CX gates, the source target-side `Rz(pi)` scaffold fixed, and five arbitrary angles placed on target-side Euler slots across four layers. Families retain at least four of the five source target-side slots and exhaust all eight CX direction sequences. This is a bounded resource-frontier test, not a global synthesis claim.

## Result

| Context | Exact families | Best residual | Best family |
|---:|---:|---:|---|
| 1 | 0 | 1.531091569077196 | `CX 010101; mid1:q1:rz0, mid1:q1:ry, mid2:q1:ry, post:q1:rz0, post:q1:ry` |
| 2 | 0 | 1.531091569077196 | `CX 010101; mid1:q1:rz0, mid1:q1:ry, mid2:q1:ry, post:q1:rz0, post:q1:ry` |
| 3 | 0 | 1.531091569077196 | `CX 010101; mid1:q1:rz0, mid1:q1:ry, mid2:q1:ry, post:q1:rz0, post:q1:ry` |
| 4 | 0 | 1.531091569077196 | `CX 010101; mid1:q1:rz0, mid1:q1:ry, mid2:q1:ry, post:q1:rz0, post:q1:ry` |
| 5 | 0 | 1.531091569077196 | `CX 010101; mid1:q1:rz0, mid1:q1:ry, mid2:q1:ry, post:q1:rz0, post:q1:ry` |
| 6 | 0 | 1.531091569077196 | `CX 010101; mid1:q1:rz0, mid1:q1:ry, mid2:q1:ry, post:q1:rz0, post:q1:ry` |
| 7 | 0 | 1.531091569077196 | `CX 010101; mid1:q1:rz0, mid1:q1:ry, mid2:q1:ry, post:q1:rz0, post:q1:ry` |

No bounded exact replay was found in this family.

## Resource boundary

The candidate spends one additional CX to retain five arbitrary angles against a baseline of two CX and six arbitrary angles for the selected contexts. Occurrence removal, proxy-T reduction, and B7 credit remain zero until a concrete arbitrary-input rewrite and full ledger pass.

## Claim boundary

This closes only the declared target-side family with minimum source-slot overlap four. It is not a global three-CX lower bound, an exhaustive local-Euler search, a full-circuit rewrite, or a solved B1/B7 frontier.
