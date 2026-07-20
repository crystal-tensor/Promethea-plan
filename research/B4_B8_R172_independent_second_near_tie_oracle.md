# B4/B8 R172 Independent Second-Graph Near-Tie Oracle

- Status: `independent_near_tie_oracle_complete`
- Classification: `independent_reproduction_confirmed_policy_split`
- Rows / candidates: `192` / `576`
- Source-return matches: `192` / `192`
- Policy-change counts: `{'source_f64': 0, 'compensated_fsum': 192, 'exact_binary64_leaf': 192, 'tie_aware_1ulp': 192}`
- Payload hash: `e0a5b61c653ff5f6d1eb0d5bbc74464513eaa2d5a99bcfa403b75fd374506e4d`

## Heuristic question

Can a standard-library oracle reproduce the second-graph one-ULP policy split without importing Qiskit?

The oracle reads only the R172 worker manifests. It reconstructs source scores from binary64 bits, compensated sums from retained leaf bits, exact rational leaf sums, and the declared 1-ULP tie rule. It verifies row hashes, candidate records, source-return mappings, all three operation-order profiles, and the aggregate policy split.

## Claim boundary

This is independent evidence integrity and arithmetic recomputation for one frozen nonisomorphic R172 input. It is not a new Qiskit execution, a production mapping change, a confirmed bug, broad cross-input generality, hardware evidence, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.
