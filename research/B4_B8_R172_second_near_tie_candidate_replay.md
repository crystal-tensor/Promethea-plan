# B4/B8 R172 Second-Graph Near-Tie Complete-Candidate Replay

- Status: `new_input_candidate_replay_complete`
- Classification: `new_input_candidate_replay_complete`
- Profiles / replays: `3` / `192`
- Yielded complete candidates: `576`
- Source-return matches: `192` / `192`
- Payload hash: `4c3fa5782a467b3e4eea94c2897a6a52a7257e512704fdc4876cfb18578bd99e`

## Research Question

Does the arithmetic-policy split survive a nonisomorphic weighted T-tree interaction graph?

## Method

R172 runs the hash-bound candidate instrumentation on a five-active-qubit weighted T-tree over FakeNairobiV2. Its degree sequence `(3,2,1,1,1)` differs from the R170 path `(2,2,2,1,1)`, proving the graphs are not isomorphic. The bounded design scan identified a one-ULP source-score gap. The replay retains every complete VF2 candidate and applies source binary64, compensated `math.fsum`, exact retained-binary64 leaves, and 1-ULP tie-aware selection without changing the search traversal.

## Result

Across `3` profiles and `192` calls, `576` candidates were yielded, source-return validation matched `192/192`, and policy-change counts were `{'source_f64': 0, 'compensated_fsum': 192, 'exact_binary64_leaf': 192, 'tie_aware_1ulp': 192}`.

## Claim Boundary

This is a second near-tie candidate-level result on one nonisomorphic weighted graph. It does not establish broad cross-input generality, a production mapping change, an alternate search path, a confirmed Qiskit bug, hardware relevance, route advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.
