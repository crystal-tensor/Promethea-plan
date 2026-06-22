# B1/B7 cone_01 Union-Region One-Free-Parameter Pricing Gate

- Method: `b1_b7_cone01_union_region_one_free_parameter_pricing_gate_v0`
- Status: `cone01_union_region_one_free_parameter_pricing_rejected`
- Model status: `one_free_parameter_union_census_candidates_do_not_recover_exactness`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- Union window: `[1369, 1379]`
- Support qubits: `[4, 8]`
- Orientation sequences: `['01-01', '01-10', '10-01', '10-10']`
- One-free trials: `72`
- Exact pass / fail: `0` / `72`
- Best one-free residual: `0.25709607640616583`
- Best one-free sequence / parameter: `10-10` / `7`
- Worst best-sequence residual: `0.6857140007440164`
- One-free proxy-T pressure if accepted: `20`
- Current line-1381 proxy-T pressure: `100`
- B7 ledger improvement claimed: `False`

## Claim Boundary

Within the T-B1-004bf union-region two-CNOT census candidates, no one-free-parameter pi/4-grid repair reaches exact replay.

Unsupported claims:
- This is not a global lower bound for the union target.
- This does not rule out two or more free parameters, a different scaffold, or symbolic absorption.
- This does not accept local-U3 pricing, occurrence removal, or a B7 ledger improvement.

## Sequence Best Rows

- `01-01`: best parameter `10`, residual `0.38978167843451345`, exact passes `0` / `18`
- `01-10`: best parameter `11`, residual `0.3891819621525939`, exact passes `0` / `18`
- `10-01`: best parameter `7`, residual `0.6857140007440164`, exact passes `0` / `18`
- `10-10`: best parameter `7`, residual `0.25709607640616583`, exact passes `0` / `18`
