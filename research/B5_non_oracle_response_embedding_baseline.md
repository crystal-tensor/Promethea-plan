# B5 Non-Oracle Response Embedding Baseline v0.1

Last updated: 2026-06-18

Status: **non_oracle_response_embedding_denominator_not_quantum_advantage_claim**

## Summary

- Method: `b5_non_oracle_response_embedding_baseline_v0`
- Dependency B10 table: `b10_t1_d5_observable_denominator_table_v0`
- Dependency oracle denominator for comparison only: `results/B5_boundary_field_embedding_baseline_v0.json`
- Instances: 9
- Sites: [4, 6, 8]
- U/t values: [2.0, 4.0, 8.0]
- Selection policy: open_cluster_zero_field for sites<=4; finite_cluster_inverse_size_extrapolation otherwise
- Selected mean / median / max relative response error: 0.0509835 / 0.0172621 / 0.123081
- Oracle boundary-field mean / max relative error, comparison only: 0.0541004 / 0.121587
- Non-oracle rows beating oracle boundary-field: 4
- Max exact D5 Hilbert dimension: 4900
- Max selected cluster Hilbert dimension: 36
- Uses exact target for selection: False
- Validation errors: 0
- Explicitly not quantum advantage: True

## Blind Method Comparison

| Method | Mean rel. error | Median rel. error | Max rel. error |
|---|---:|---:|---:|
| open_cluster_zero_field | 0.0733776 | 0.102086 | 0.145171 |
| density_self_consistent_edge_field | 0.0733776 | 0.102086 | 0.145171 |
| finite_cluster_inverse_size_extrapolation | 0.0509835 | 0.0172621 | 0.123081 |

## Interpretation

- This artifact closes the oracle-tuning loophole in B5/T-B5-002 for the current 1D Hubbard D5 rows.
- The selected denominator does not inspect the exact D5 susceptibility when choosing a method or field.
- Exact D5 values are used only after selection to compute residuals and compare against the previous oracle-tuned pressure baseline.
- The result is still a small-cluster classical denominator, not a DMRG replacement and not a deployable quantum many-body solver.

## Rows

| Sites | U/t | Selected method | Exact D5 chi | Selected chi | Rel. error | Oracle rel. error | Max cluster dim |
|---:|---:|---|---:|---:|---:|---:|---:|
| 4 | 2.0 | open_cluster_zero_field | 0.083606099 | 0.083606099 | 2.12467e-14 | 3.05422e-14 | 36 |
| 4 | 4.0 | open_cluster_zero_field | 0.03622603 | 0.03622603 | 2.08322e-11 | 1.85903e-11 | 36 |
| 4 | 8.0 | open_cluster_zero_field | 0.0083777764 | 0.0083777764 | 8.59309e-13 | 1.24238e-15 | 36 |
| 6 | 2.0 | finite_cluster_inverse_size_extrapolation | 0.095784902 | 0.085046436 | 0.11211 | 0.121587 | 36 |
| 6 | 4.0 | finite_cluster_inverse_size_extrapolation | 0.039368625 | 0.03868904 | 0.0172621 | 0.108267 | 36 |
| 6 | 8.0 | finite_cluster_inverse_size_extrapolation | 0.0084668667 | 0.0091530338 | 0.0810414 | 0.0839472 | 36 |
| 8 | 2.0 | finite_cluster_inverse_size_extrapolation | 0.09780451 | 0.085766605 | 0.123081 | 0.114912 | 36 |
| 8 | 4.0 | finite_cluster_inverse_size_extrapolation | 0.040469287 | 0.039920545 | 0.0135595 | 0.0550626 | 36 |
| 8 | 8.0 | finite_cluster_inverse_size_extrapolation | 0.0085813023 | 0.0095406625 | 0.111797 | 0.00312785 | 36 |

## Claim Boundary

- Now supported: A non-oracle B5 response denominator now covers the same nine B10 D5 Hubbard rows. It selects among zero-field cluster embedding and inverse-size cluster extrapolation by a predeclared rule, while density self-consistency is reported as a blind diagnostic.
- Still not supported: This is not DMRG, not a two-dimensional correlated-matter result, not a quantum kernel, and not an accuracy-per-resource win. Exact D5 susceptibilities are used only for evaluation.
- Next gate: Replace this small-cluster denominator with a real tensor/DMRG reference or compare a quantum impurity/response kernel after state-preparation, measurement, and optimizer-loop costs.
