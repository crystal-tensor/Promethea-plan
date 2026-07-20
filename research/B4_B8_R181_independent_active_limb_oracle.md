# B4/B8/B10 R181 Independent Active-Limb Superaccumulator Oracle

- Status: `independent_active_limb_oracle_complete`
- Requirements: `12/12`
- Payload hash: `a1de6b1b1eb57353bbf3968a2c8232ae6c41d8ee8ca4b398b7992a6b24d9d388`

## Independent Check

A standard-library-only audit validates `52/52` worker hashes and `3200/3200` row hashes. It reproduces `2304/2304` standard outcomes and independently enumerates all `28/28` sub-ULP exact-oracle cells across source, BigUint, fixed-34, and active-limb policies.

It imports neither Qiskit nor the R181 execution module, performs zero Qiskit calls, simulations, routes, or shots, and recomputes the timing and peak-RSS ratios from immutable worker rows.

## Claim Boundary

This strengthens evidence integrity for the frozen R181 matrix. It does not make the experimental patch upstream accepted or production ready, establish a confirmed Qiskit bug, prove broad route-quality improvement or cross-platform overhead, provide hardware evidence, quantum advantage, BQP separation, solve B4/B8/B10, or add credit.
