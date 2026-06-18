# B7 w8_21 Euler-Local Synthesis Search

Status: **w8_21_euler_local_search_negative_boundary_not_global_lower_bound**

## Scope

- Method: `b7_w8_21_euler_local_search_v0`
- Template: `w8_21`
- Family count: 500
- Total family count: 500
- Family mode: `target-informed`
- Scaffold mode: `zero-or-one-pi`
- Seeds per family: 6
- Optimizer runs: 3000
- Exact tolerance: 1e-08

## Result

- Passing candidates: 0
- Best family: `cx01-cx01|fixed[mid:q1:rz1=pi]|free[pre:q1:ry,mid:q1:rz0,post:q1:rz0,post:q1:ry]`
- Best residual norm: 0.24437773599006604
- Best max entry error: 0.1252281345437596
- Candidate arbitrary rotations per occurrence: 4
- Baseline arbitrary rotations per occurrence: 5

## Claim Boundary

- euler_local_four_rotation_search_found_exact_candidate: False
- allows_local_euler_layers: True
- allows_one_exact_pi_scaffold: True
- would_reduce_arbitrary_occurrences_if_passing: 0
- would_reduce_t_ledger_if_passing_best: 0
- global_two_qubit_lower_bound_claimed: False
- all_exact_clifford_scaffolds_claimed: False
- ancilla_or_measurement_claimed: False

## Interpretation

No exact four-arbitrary-angle candidate was found in the bounded Euler-local two-CNOT search with zero/one-pi scaffold. This strengthens the previous broad-skeleton negative result by allowing local Euler layers around the two CNOTs, but it is still not a global lower bound over arbitrary Clifford scaffolds, three-CNOT circuits, ancillas, measurement, or symbolic KAK minimality.

## Next Actions

- If positive, emit QASM rewrites for all 20 w8_21 occurrences and rerun proof/Aer/resource checks.
- If negative, either test a limited three-CNOT/four-arbitrary family or write a scoped minimality note covering the searched families.
- Do not claim a global lower bound without symbolic KAK or exhaustive Clifford-local proof.
