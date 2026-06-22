# B1/B7 cone_01 Union-Region Low-CNOT Search Gate

- Method: `b1_b7_cone01_union_region_low_cnot_search_gate_v0`
- Status: `cone01_union_region_low_cnot_search_no_extra_delta`
- Model status: `union_region_zero_one_cnot_scaffolds_fail_both_orientations`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- Source semantic packet: `results/B1_B7_cone01_semantic_replay_packet_gate_v0.json`
- Source packet synthesis: `results/B1_B7_cone01_packet_synthesis_search_gate_v0.json`
- Source overlap bound: `results/B1_B7_cone01_overlap_additivity_bound_gate_v0.json`

## Result

- Union window: `[1369, 1379]`
- Support qubits: `[4, 8]`
- Source CNOT count: `5`
- Current exact replacement CNOT count: `2`
- Current candidate CNOT delta: `3`
- Searched CNOT counts: `[0, 1]`
- Searched orientations: `3`
- 0-CNOT / 1-CNOT exact pass count: `0` / `0`
- Best low-CNOT residual / entry error: `0.2548908758679516` / `0.12724247975106365`
- Extra delta found beyond current replacement: `0`
- Global lower bound claimed: `False`
- Accepted occurrence / proxy-T reduction: `0` / `0`

## Claim Boundary

- This is a scoped numerical search failure for 0/1-CNOT union-region scaffolds, not a theorem.
- The current branch still has no accepted occurrence removal, proxy-T reduction, or B7 ledger improvement.
