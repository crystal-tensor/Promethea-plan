# B4/B8 R167 New-Input Complete-Candidate Replay

- Status: `new_input_candidate_replay_incomplete`
- Classification: `new_input_candidate_replay_incomplete`
- Profiles / replays: `3` / `192`
- Yielded complete candidates: `0`
- Source-return matches: `0` / `192`
- Payload hash: `4feb927bcbd51807faa07e161e58b53b970e5944eaee784bbca6e0af24931164`

## Research Question

Does the candidate-selection signal survive on a newly frozen OpenQASM 3 interaction graph rather than only the R157 input?

## Method

R167 runs the hash-bound candidate instrumentation on a new six-active-qubit path-with-chord input over FakeNairobiV2. It retains every complete VF2 candidate and replays source binary64, compensated `math.fsum`, exact retained-binary64 leaves, and 1-ULP tie-aware selection without changing the search traversal.

## Result

Across `3` profiles and `192` calls, `0` candidates were yielded, source-return validation matched `0/192`, and policy-change counts were `{'source_f64': 0, 'compensated_fsum': 0, 'exact_binary64_leaf': 0, 'tie_aware_1ulp': 0}`.

## Claim Boundary

This is one new-input candidate-level result. It does not establish cross-input generality, a production mapping change, an alternate search path, a confirmed Qiskit bug, hardware relevance, route advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.
