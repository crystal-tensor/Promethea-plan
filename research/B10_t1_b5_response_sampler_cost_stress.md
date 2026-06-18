# B10-T1 B5 Response Sampler Cost Stress v0.1

Status: **b5_response_sampler_cost_stress_no_positive_same_access_route**

## Summary

- Method: b10_t1_b5_response_sampler_cost_stress_v0
- Sampling model: optimistic_bounded_density_finite_difference_sampler
- Instances: 9
- Confidence z: 2.576
- Max explicit D5 matvec-equivalent ops: 1014300
- Max shots to match non-oracle embedding: 33647381717520329727157267857408
- Max shots to match one-site variational MPS/ALS: 1017740833188413568
- Max shots to match exact-state-seeded MPS pressure: 284916076006665507134714675200
- Median shots to match exact-state-seeded MPS pressure: 7644706432712
- Max optimistic seeded-target prep 2Q gate floor: 1139664304026662028538858700800
- Rows where sampler shots beat explicit D5 matvec ops for seeded target: 0
- Sampling oracle constructed: False
- Same-access positive route ready: False
- Validation errors: []

## Row Pressure

| sites | U/t | exact response | D5 matvec ops | shots vs ALS | shots vs seeded MPS | seeded prep 2Q floor |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 2.0 | 0.0836061 | 1620 | 23609989803634 | 284916076006665507134714675200 | 1139664304026662028538858700800 |
| 4 | 4.0 | 0.036226 | 1620 | 159653417022792 | 2553758443925336829286416384 | 10215033775701347317145665536 |
| 4 | 8.0 | 0.00837778 | 1440 | 1017740833188413568 | 4610241870596310791037648896 | 18440967482385243164150595584 |
| 6 | 2.0 | 0.0957849 | 50400 | 41024686 | 11630698994 | 69784193964 |
| 6 | 4.0 | 0.0393686 | 47600 | 44872442 | 3279589736230 | 19677538417380 |
| 6 | 8.0 | 0.00846687 | 42000 | 1435179920 | 7644706432712 | 45868238596272 |
| 8 | 2.0 | 0.0978045 | 1014300 | 490144880 | 3861425434 | 30891403472 |
| 8 | 4.0 | 0.0404693 | 926100 | 50235256 | 139216418548 | 1113731348384 |
| 8 | 8.0 | 0.0085813 | 705600 | 1263752568 | 6695603121926592 | 53564824975412736 |

## Claim Boundary

- sampling_oracle_constructed: False
- same_access_positive_route_ready: False
- production_dmrg_available: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False
- what_is_supported: An optimistic finite-difference response sampler lower bound was costed against the same nine B5/B10 Hubbard response rows and denominator ladder.
- what_is_not_supported: This is not a constructed quantum response oracle, not a state-preparation algorithm, not production DMRG, not a sampling theorem, not quantum advantage, and not a BQP separation.

## Next Gate

This closes only an optimistic sampler-cost stress. A positive B10-T1 route
still requires either a real same-access response oracle with state-preparation,
mixing, measurement, and confidence costs, or a mature production DMRG/MPS
reference that is not exact-state seeded.
