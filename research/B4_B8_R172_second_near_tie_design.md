# B4/B8 R172 Second Near-Tie Graph Design

- Status: `second_near_tie_design_complete`
- Weighted variants scanned: `625`
- Observable / one-ULP variants: `524` / `21`
- Selected multiplicities: `[2, 1, 1, 1]`
- Best-two gap: `1.0 ULP`

## Heuristic question

Does the one-ULP selection split survive when the interaction graph changes from a path into a nonisomorphic T-tree?

The degree sequences `(2,2,2,1,1)` and `(3,2,1,1,1)` prove that the R170 and R172 interaction graphs are not isomorphic. The bounded scan selects the lowest-two-qubit-cost one-ULP weighted variant under the declared search order.

## Claim boundary

This is a design scan and frozen control, not the full R172 replay. It performs no simulation or hardware execution and makes no compiler-bug, numerical-remedy, advantage, BQP, solved-frontier, or credit claim.
