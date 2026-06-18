# B7 w8_21 Bounded Three-CNOT Search

Status: **w8_21_three_cnot_search_negative_boundary_not_global_lower_bound**

## Scope

- Method: `b7_w8_21_three_cnot_search_v0`
- Template: `w8_21`
- Family count: 1480
- Total family count: 1480
- Family mode: `target-informed`
- Min source free slots: 3
- Seeds per family: 6
- Optimizer runs: 8880
- Exact tolerance: 1e-08

## Result

- Passing candidates: 0
- Best family: `cx01-cx10-cx10|fixed[mid1:q1:rz1=pi]|free[mid1:q1:rz0,mid1:q1:ry,post:q0:rz0,post:q1:rz0]`
- Best residual norm: 1.0352761804100845
- Best max entry error: 0.4895711241454502
- Candidate CNOT count: 3
- Candidate arbitrary rotations per occurrence: 4
- Baseline arbitrary rotations per occurrence: 5

## Claim Boundary

- three_cnot_four_rotation_search_found_exact_candidate: False
- allows_one_extra_cnot: True
- allows_local_euler_layers: True
- keeps_source_pi_scaffold: True
- would_reduce_arbitrary_occurrences_if_passing: 0
- would_reduce_t_ledger_if_passing_best: 0
- global_two_qubit_lower_bound_claimed: False
- all_three_cnot_clifford_scaffolds_claimed: False
- ancilla_or_measurement_claimed: False

## Interpretation

No exact four-arbitrary-angle candidate was found in this bounded target-informed three-CNOT search. This means that adding one extra CNOT did not rescue the specific four-arbitrary-angle compression families tested here. It is still not a global lower bound over all three-CNOT circuits, Clifford scaffolds, ancillas, measurements, or symbolic KAK decompositions.

## Next Actions

- If positive, emit QASM rewrites for all 20 w8_21 occurrences and rerun proof/Aer/resource checks.
- If negative, write a scoped minimality note covering T-B7-008/T-B7-009 searched families.
- Do not count any w8_21 ledger reduction until an exact rewrite is emitted and verified.
