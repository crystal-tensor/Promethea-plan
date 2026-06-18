# B5 Variational MPS/ALS Response Reference v0.1

Last updated: 2026-06-18

Status: **variational_mps_als_pressure_reference_not_production_dmrg_or_advantage_claim**

## Summary

- Method: `b5_variational_mps_als_response_reference_v0`
- Dependency B10 table: `b10_t1_d5_observable_denominator_table_v0`
- Dependency seeded MPS pressure reference: `results/B5_mps_truncation_response_reference_v0.json`
- Instances: 9
- Sites: [4, 6, 8]
- U/t values: [2.0, 4.0, 8.0]
- Bond dimensions tested: [2, 4]
- Selected bond dimensions: [4]
- Restarts per instance/bond dimension: 3
- Sweeps per restart: 8
- Selected mean / median / max relative response error: 0.0180555 / 0.0167952 / 0.039072
- Selected mean / max energy error per site: 0.00302537 / 0.00853475
- Min selected overlap with exact ground state: 0.962614
- Rows beating exact-state-seeded MPS pressure reference: 0
- Exact-state seeded: False
- Variational MPS/ALS: True
- Production DMRG: False
- Validation errors: 0

## Interpretation

- This is a non-exact-state-seeded variational MPS/ALS pressure reference for B5/T-B5-003.
- It initializes from a product state plus random perturbations, then performs one-site generalized-eigenproblem sweeps over MPS tensors.
- Selection is by lowest variational energy across restarts, not by response-target error.
- The D5 exact response target is used only for evaluation; the exact ground energy is still used as the response-operator shift to match the existing D5 denominator definition.
- This is not a mature canonical-environment DMRG implementation, not a quantum response kernel, and not an accuracy-per-resource win.

## Rows

| Sites | U/t | Bond dim | Exact D5 chi | Var-MPS chi | Rel. response error | Energy error/site | Overlap | Beats seeded pressure? |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 4 | 2.0 | 4 | 0.083606099 | 0.083603978 | 2.53641e-05 | 4.19542e-08 | 1 | False |
| 4 | 4.0 | 4 | 0.03622603 | 0.036226846 | 2.25111e-05 | 1.07553e-08 | 1 | False |
| 4 | 8.0 | 4 | 0.0083777764 | 0.0083777866 | 1.21915e-06 | 1.4403e-09 | 1 | False |
| 6 | 2.0 | 4 | 0.095784902 | 0.094176171 | 0.0167952 | 0.00401623 | 0.995057 | False |
| 6 | 4.0 | 4 | 0.039368625 | 0.037830413 | 0.039072 | 0.00442318 | 0.989766 | False |
| 6 | 8.0 | 4 | 0.0084668667 | 0.0081948769 | 0.032124 | 0.00275538 | 0.990166 | False |
| 8 | 2.0 | 4 | 0.09780451 | 0.098269928 | 0.00475866 | 0.00550393 | 0.991923 | False |
| 8 | 4.0 | 4 | 0.040469287 | 0.039015497 | 0.0359233 | 0.00853475 | 0.962614 | False |
| 8 | 8.0 | 4 | 0.0085813023 | 0.0082914513 | 0.033777 | 0.00199483 | 0.987522 | False |

## Claim Boundary

- Now supported: A non-exact-state-seeded variational MPS/ALS optimizer now provides a small-scale tensor reference attempt on the same B10 D5 Hubbard response rows.
- Still not supported: This is not canonical-environment production DMRG, not a 2D/doped correlated-matter solver, not a quantum response kernel, and not an accuracy-per-resource win.
- Next gate: Replace this prototype with a mature variational DMRG/MPS implementation or compare a real quantum response kernel against the D5 and tensor references after full cost accounting.
