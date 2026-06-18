# B5 MPS/Schmidt-Truncation Response Reference v0.1

Last updated: 2026-06-18

Status: **mps_schmidt_truncation_response_reference_not_dmrg_or_advantage_claim**

## Summary

- Method: `b5_mps_schmidt_truncation_response_reference_v0`
- Dependency B10 table: `b10_t1_d5_observable_denominator_table_v0`
- Dependency non-oracle embedding denominator: `results/B5_non_oracle_response_embedding_baseline_v0.json`
- Instances: 9
- Sites: [4, 6, 8]
- U/t values: [2.0, 4.0, 8.0]
- Bond dimensions tested: [2, 4, 8, 16]
- Selected bond dimension: 16
- Selected mean / median / max relative response error: 0.000441626 / 0.000144526 / 0.0016954
- Selected mean / max energy error per site: 0.000243972 / 0.00115588
- Min selected overlap with exact ground state: 0.999101
- Min selected fixed-sector norm before normalization: 0.999101
- Rows beating non-oracle embedding denominator: 6
- Exact-state seeded: True
- Variational DMRG: False
- Validation errors: 0

## Interpretation

- This is a tensor-network pressure reference for B5/T-B5-003, not a completed DMRG baseline.
- It compresses the exact Hubbard ground state into an MPS by sequential Schmidt truncation, reconstructs it, projects back to the fixed particle-number sector, and evaluates the same shifted D5 response.
- Because the MPS is seeded by the exact state, it measures bond-dimension sensitivity rather than deployable variational optimization.
- A future B5 denominator still needs a variational DMRG/MPS solver or a costed quantum response-kernel comparison.

## Rows

| Sites | U/t | Bond dim | Exact D5 chi | MPS chi | Rel. response error | Energy error/site | Overlap | Fixed-sector norm |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 2.0 | 16 | 0.083606099 | 0.083606099 | 2.30892e-13 | 3.33067e-16 | 1 | 1 |
| 4 | 4.0 | 16 | 0.03622603 | 0.03622603 | 5.62853e-12 | 1.11022e-16 | 1 | 1 |
| 4 | 8.0 | 16 | 0.0083777764 | 0.0083777764 | 1.8114e-11 | 2.22045e-16 | 1 | 1 |
| 6 | 2.0 | 16 | 0.095784902 | 0.095880445 | 0.000997484 | 0.000517057 | 0.999732 | 0.999732 |
| 6 | 4.0 | 16 | 0.039368625 | 0.039374314 | 0.000144526 | 0.000147271 | 0.999926 | 0.999926 |
| 6 | 8.0 | 16 | 0.0084668667 | 0.0084705934 | 0.000440152 | 1.76638e-05 | 0.999994 | 0.999994 |
| 8 | 2.0 | 16 | 0.09780451 | 0.097638692 | 0.0016954 | 0.00115588 | 0.999101 | 0.999101 |
| 8 | 4.0 | 16 | 0.040469287 | 0.040441671 | 0.000682394 | 0.000320408 | 0.999742 | 0.999742 |
| 8 | 8.0 | 16 | 0.0085813023 | 0.0085811764 | 1.46743e-05 | 3.74685e-05 | 0.999983 | 0.999983 |

## Claim Boundary

- Now supported: A tensor-network pressure reference now measures how finite MPS bond dimension distorts the same B10 D5 Hubbard response rows after projecting back to the fixed particle-number sector.
- Still not supported: This is exact-state-seeded Schmidt truncation, not variational DMRG, not a deployable tensor solver, not a quantum response kernel, and not an accuracy-per-resource win.
- Next gate: Replace the exact-state-seeded MPS pressure reference with a variational DMRG/MPS solver or compare a real quantum response kernel against this reference after full cost accounting.
