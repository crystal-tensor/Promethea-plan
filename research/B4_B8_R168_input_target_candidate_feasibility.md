# R168 Input-Target Candidate Feasibility Diagnostic

**Method:** `b4_b8_r168_input_target_candidate_feasibility_v0`
**Status:** `candidate_feasibility_diagnostic_complete`
**Classification:** `candidate_free_due_to_target_topology_cycle_mismatch`

## Heuristic question

Was R167 unable to produce a candidate because the arithmetic policy failed, or because its interaction graph cannot fit the declared target?

## Frozen objects

The diagnostic reuses the hash-bound R167 OpenQASM 3 input and `FakeNairobiV2` target. It treats the six active qubits as an undirected interaction graph, matching the R167 `strict_direction=false` boundary. It exhaustively enumerates every injective assignment of the six logical vertices into the seven target vertices and checks every logical interaction edge.

| Structural measure | R167 input | FakeNairobiV2 target |
|---|---:|---:|
| Vertices | `6` | `7` |
| Unique interaction edges | `6` | `6` |
| Cycle rank | `1` | `0` |
| Complete injective embeddings | `0` | - |
| Embeddings after removing q[2]-q[4] chord only | `0` | - |
| Embeddings for target-compatible six-vertex tree template | `8` | - |

## Result

The R167 input has one cycle created by the q[2]-q[4] chord. The target graph is acyclic. Exhaustive edge-preserving enumeration finds `0` complete embeddings. Removing only that chord still yields `0` embeddings because the resulting six-vertex path is longer than the target diameter. A target-derived six-vertex tree template yields `8` embeddings. This structurally explains the candidate-free boundary under the frozen matching boundary; it is not evidence of a Qiskit bug or a numerical-policy failure.

The upstream R167 evidence remains unchanged: `192` calls, `0` candidate events, `0` yielded candidates, and `0` simulation shots. The control does not prove a production compiler fix or generalize beyond this input-target pair.

## Next gate

Freeze a target-compatible candidate input with a nonzero embedding count, then rerun the candidate-level arithmetic-policy replay. Keep a separate no-candidate branch for inputs that intentionally test infeasibility. Do not count a route or policy improvement until candidate generation, source-return validation, and the declared denominator all become observable.

**Requirements:** `10/10`
**Payload hash:** `1ac6f4a5f1265ba5718b35bd0f91714c7dafda6dc736cb2bc7dc5f13eecf8693`
