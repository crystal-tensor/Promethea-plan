# B5 Boundary-Field Embedding Baseline v0.1

Last updated: 2026-06-18

Status: **boundary_field_response_embedding_denominator_not_quantum_advantage_claim**

## Summary

- Method: `b5_boundary_field_response_embedding_baseline_v0`
- Dependency B10 table: `b10_t1_d5_observable_denominator_table_v0`
- Dependency energy baseline: `small_hubbard_exact_diagonalization_cluster_proxy_v0`
- Instances: 9
- Sites: [4, 6, 8]
- U/t values: [2.0, 4.0, 8.0]
- Boundary-field grid: [-0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75]
- Mean / median / max relative response error: 0.0541004 / 0.0550626 / 0.121587
- Zero-error instances: 3
- Max exact D5 Hilbert dimension: 4900
- Max embedded cluster Hilbert dimension: 36
- Mean best cluster-product energy error/site: 0.0470259
- Validation errors: 0
- Explicitly not quantum advantage: True

## Interpretation

- This is a denominator and pressure-test artifact for B5/T-B5-001.
- It uses the exact B10 D5 Hubbard density-response rows as the target.
- It partitions the chain into small clusters and adds a scalar edge field on each cluster.
- The field is oracle-tuned against the exact D5 response, so this is intentionally a strong classical baseline, not a deployable blind solver.
- Any future B5 quantum response kernel must beat this baseline after state-preparation, measurement, optimizer-loop, and classical denominator costs are charged.

## Rows

| Sites | U/t | Partition | Best field | Exact D5 chi | Embedded chi | Rel. response error | Best energy error/site |
|---:|---:|---|---:|---:|---:|---:|---:|
| 4 | 2.0 | 4 | 0.00 | 0.083606099 | 0.083606099 | 3.05422e-14 | 0 |
| 4 | 4.0 | 4 | 0.00 | 0.03622603 | 0.03622603 | 1.85903e-11 | 0 |
| 4 | 8.0 | 4 | 0.00 | 0.0083777764 | 0.0083777764 | 1.24238e-15 | 0 |
| 6 | 2.0 | 4 + 2 | -0.75 | 0.095784902 | 0.084138747 | 0.121587 | 0.139685 |
| 6 | 4.0 | 4 + 2 | 0.75 | 0.039368625 | 0.035106295 | 0.108267 | 0.101214 |
| 6 | 8.0 | 4 + 2 | 0.75 | 0.0084668667 | 0.007756097 | 0.0839472 | 0.0586151 |
| 8 | 2.0 | 4 + 4 | 0.75 | 0.09780451 | 0.086565577 | 0.114912 | 0.0592186 |
| 8 | 4.0 | 4 + 4 | 0.75 | 0.040469287 | 0.038240942 | 0.0550626 | 0.0411895 |
| 8 | 8.0 | 4 + 4 | 0.75 | 0.0085813023 | 0.0086081433 | 0.00312785 | 0.0233108 |

## Claim Boundary

- Now supported: A B5 observable-response denominator now exists for the same nine Hubbard D5 rows: a small-cluster boundary-field embedding approximation is oracle-tuned against the exact D5 susceptibility, making it a strong classical pressure baseline.
- Still not supported: This is not a quantum subroutine, not an accuracy-per-resource win, not a tensor-network or DMRG replacement, and not evidence for broad strongly correlated matter advantage.
- Next gate: A candidate B5 quantum impurity/response kernel must beat this boundary-field denominator and a non-oracle tensor/DMRG/embedding baseline after state preparation and measurement costs.
