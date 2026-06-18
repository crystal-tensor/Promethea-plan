# B7 w8_21 Bounded Broad-Skeleton Search

Status: **w8_21_broad_skeleton_search_negative_boundary_not_global_lower_bound**

## Scope

- Method: `b7_w8_21_broad_skeleton_search_v0`
- Template: `w8_21`
- Family count: 15360
- Seeds per family: 2
- Optimizer runs: 30720
- Exact tolerance: 1e-08

## Result

- Passing candidates: 0
- Best family: `ry_q1-cx01-rz_q1-cx01-rz_q1-ry_q1`
- Best residual norm: 0.24437773599006635
- Best max entry error: 0.12522813855335146
- Candidate arbitrary rotations per occurrence: 4
- Baseline arbitrary rotations per occurrence: 5

## Claim Boundary

- bounded_four_rotation_two_cnot_search_found_exact_candidate: False
- would_reduce_arbitrary_occurrences_if_passing: 0
- would_reduce_t_ledger_if_passing_best: 0
- global_two_qubit_lower_bound_claimed: False
- basis_complete_claimed: False

## Interpretation

No exact four-arbitrary-rotation candidate was found in the bounded two-CNOT Rz/Ry skeleton search. This broadens T-B7-008 beyond the same two-CNOT skeleton, but it is not a global lower bound because it does not search arbitrary one-qubit Euler blocks, more CNOTs, measurements, ancillas, or all KAK-equivalent decompositions.

## Next Actions

- If positive, emit QASM rewrites for all 20 w8_21 occurrences and run proof/Aer/resource checks.
- If negative, broaden the basis to Euler-local/KAK templates or allow three CNOTs while tracking arbitrary-rotation count.
- Convert repeated negative searches into a scoped minimality note rather than a global no-go theorem.
