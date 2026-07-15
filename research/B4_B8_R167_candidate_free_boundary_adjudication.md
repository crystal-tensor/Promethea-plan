# R167 Candidate-Free Boundary Adjudication

**Method:** `b4_b8_r167_candidate_free_boundary_adjudication_v0`
**Status:** `candidate_free_input_boundary_complete`
**Classification:** `candidate_free_input_diagnostic`

## Heuristic question

What does a new interaction graph teach us when it produces no candidate at all?

## Evidence

The R167 raw replay remains preserved as `new_input_candidate_replay_incomplete` with its original `6/10` acceptance conditions. The three declared operation-order profiles completed `192` calls on the hash-bound six-active-qubit path-with-chord OpenQASM 3 input:

| Measure | Result |
|---|---:|
| Profiles | `3` |
| Replay calls | `192` |
| Candidate events | `0/192` |
| Yielded complete candidates | `0/192` |
| Returned candidates | `0/192` |
| Source-return matches | `0/192` |
| Arithmetic-policy mapping changes | `0` for every policy |
| Simulation calls / shots | `0 / 0` |

## Adjudication

This is a candidate-free feasibility boundary, not evidence of a wrong winner. The raw replay's `source_return_match=false` field is false by construction when no candidate exists, so policy correctness is not estimable on this input. The result does not establish why the input is candidate-free, and it does not claim cross-input generality, a Qiskit bug, a numerical remedy, hardware relevance, quantum advantage, BQP separation, a solved frontier, or new credit.

## Next gate

Before another arithmetic-policy replay, design a target-compatible input that is guaranteed to exercise the candidate path, or freeze an explicit no-candidate branch with its own acceptance rule. The next contribution should identify the graph/target compatibility invariant that makes candidate generation a testable precondition.

**Requirements:** `10/10`
**Raw result preserved:** `True`
**Payload hash:** `07d7f64151b3b5e4366654f5ff94a93f014d15bbfafa6e7ef8b2b9061acbd878`
