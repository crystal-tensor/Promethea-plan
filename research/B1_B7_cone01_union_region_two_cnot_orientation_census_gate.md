# B1/B7 cone_01 Union-Region Two-CNOT Orientation Census Gate

- Method: `b1_b7_cone01_union_region_two_cnot_orientation_census_gate_v0`
- Status: `cone01_union_region_two_cnot_orientation_census_candidate_only`
- Model status: `two_cnot_union_candidate_confirmed_without_replay_or_b7_credit`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- Source semantic packet: `results/B1_B7_cone01_semantic_replay_packet_gate_v0.json`
- Source packet synthesis: `results/B1_B7_cone01_packet_synthesis_search_gate_v0.json`
- Source low-CNOT gate: `results/B1_B7_cone01_union_region_low_cnot_search_gate_v0.json`

## Result

- Union window: `[1369, 1379]`
- Support qubits: `[4, 8]`
- Source CNOT / current replacement CNOT / current delta: `5` / `2` / `3`
- Searched 2-CNOT orientation sequences: `4`
- Seeds / max evaluations per sequence: `18` / `3000`
- Exact 2-CNOT sequence count: `4`
- Exact 2-CNOT sequence ids: `['01-01', '01-10', '10-01', '10-10']`
- Best sequence / residual / entry error: `01-10` / `5.812946138498332e-13` / `3.4095575404049453e-13`
- Best exact sequence / residual / entry error: `01-10` / `5.812946138498332e-13` / `3.4095575404049453e-13`
- Best exact off-grid / nonzero / total U3 parameters: `13` / `17` / `18`
- Extra delta beyond current replacement: `0`
- Replay certificates / QASM patches / B7 claim: `0` / `0` / `False`

## Claim Boundary

- This is a numerical 2-CNOT orientation census for the union-region target.
- It keeps the branch at candidate-only status until full-circuit replay, QASM patching, and local-U3 fault-tolerant pricing are completed.
