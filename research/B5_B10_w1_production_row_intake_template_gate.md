# B5/B10 W1 Production Row Intake Template Gate v0.1

Status: **w1_production_row_intake_template_open_missing_submitted_rows**

## Summary

- Method: `b5_b10_w1_production_row_intake_template_gate_v0`
- Model status: `w1_submission_template_built_no_production_rows_accepted`
- Row contract count/hash: 9 / `7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc`
- Requirements passed/failed: 5 / 3
- Failed requirement IDs: ['I5', 'I6', 'I7']
- Required row keys / prefilled min / production-required keys: 17 / 9 / 8
- Template rows / template hashes: 9 / 9
- Template table hash: `9b65b1964bd1ad312608e767cc16e96a09e2a4d8ef77e9ecbe47a2d9807fb8ac`
- Prototype trace-hash rows: 9
- Submitted / accepted production rows: 0 / 0
- Missing required keys total / production missing keys total: 72 / 72

## Production Required Keys

`canonical_center_site`, `left_environment_hash`, `right_environment_hash`, `orthonormal_residual_norm`, `discarded_weight`, `wall_clock_seconds`, `peak_memory_mb`, `matvec_or_sweep_count`

## Requirement Results

- I1 [PASS]: W1 implementation contract and prototype scout are locked to the same row contract
- I2 [PASS]: Nine production-row intake templates are generated
- I3 [PASS]: Every template preserves the 17-key W1 row schema
- I4 [PASS]: Prototype trace hashes are carried into all templates as provenance only
- I5 [FAIL]: Submitted production-row artifacts exist for all locked rows
- I6 [FAIL]: Canonical environment, residual, discarded-weight, and cost keys are populated
- I7 [FAIL]: All submitted rows are accepted as production contract rows
- I8 [PASS]: Forbidden claims remain false while intake rows are missing

## Template Rows

| row_id | prefilled keys | missing production keys | template hash |
| --- | ---: | ---: | --- |
| D5H_s4_u2_eta0.25_n2x2_obs_density_site_2 | 9 | 8 | `8c092a98cd79f2511efc91b1db4a31b5fd414ec7816089aee3871c8ad5f493b9` |
| D5H_s4_u4_eta0.25_n2x2_obs_density_site_2 | 9 | 8 | `9840a50c0487fe14bafbf5e94f1e8e4c458bb10265ebd184cf7820f9b36b0a01` |
| D5H_s4_u8_eta0.25_n2x2_obs_density_site_2 | 9 | 8 | `d55326624e5c66cfef917a297ad2e33f907c2fc3900c41cd2354c29f441eb917` |
| D5H_s6_u2_eta0.25_n3x3_obs_density_site_3 | 9 | 8 | `5a7395fd1d4c84298287374ddd4830da90517b8e4da6b2053ef4fee5f6a2c39a` |
| D5H_s6_u4_eta0.25_n3x3_obs_density_site_3 | 9 | 8 | `77967834c56fb87bd342ef8e85ac1b11568bdc3c970a2733ecc253859b561f60` |
| D5H_s6_u8_eta0.25_n3x3_obs_density_site_3 | 9 | 8 | `18246ea58dcc063cbf8f20730621ffc25b772d058ca0319769d5549fc4bfc3d3` |
| D5H_s8_u2_eta0.25_n4x4_obs_density_site_4 | 9 | 8 | `5ab7ee67accd826db90f4b3662b4377850f795529fe9d01327725d0dc4ae92e3` |
| D5H_s8_u4_eta0.25_n4x4_obs_density_site_4 | 9 | 8 | `779b9d3e0a1e47a7e3e0ee05bdd9a5711e8387d8e40f11b984f65801a7c045d3` |
| D5H_s8_u8_eta0.25_n4x4_obs_density_site_4 | 9 | 8 | `0682e2788b86dcb00ac6cd2bf7edd47def6af1ff203e86c77f9410b51e13ebe5` |

## Claim Boundary

- Supported: The locked W1 row contract has been converted into nine row-level intake templates that carry prototype provenance and name the missing production fields explicitly.
- Not supported: No submitted production rows, canonical environment hashes, residual norms, production discarded weights, cost rows, production DMRG denominator, positive same-access route, quantum advantage, or BQP separation are supported.
- Next gate: Submit production-row artifacts for all nine templates with canonical center sites, left/right environment hashes, residual norms, discarded weights, wall-clock, memory, and sweep/matvec counts, then rerun the gate.
- production_dmrg_claimed: False
- same_access_positive_route_claimed: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False

## Validation

- validation_error_count: 0
