# B1/B7 cone_01 Linear-Span Replay Certificate Gate

- Method: `b1_b7_cone01_linear_span_replay_certificate_gate_v0`
- Status: `cone01_linear_span_replay_certificate_passed_not_full_unitary`
- Model status: `qasm2_candidate_has_six_dimensional_linear_span_replay_certificate_without_b7_credit`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- Source candidate: `results/B1_B7_cone01_qasm2_candidate_rewrite_gate_v0.json`
- Source subspace replay: `results/B1_B7_cone01_global_phase_subspace_replay_gate_v0.json`

## Result

- Finite linear-span certificate passed: `True`
- Certified input subspace dimension: `6` of `524288`
- Certified input subspace fraction: `1.1444091796875e-05`
- Linear-span error spectral norm: `2.7889440543898627e-13`
- Max basis L2 error: `2.534056605707275e-13`
- Max basis amplitude delta: `1.3928889642636009e-13`
- Max basis probability delta: `7.771561172376096e-16`
- Max source/candidate Gram delta: `1.9984014443252818e-15`
- Max cross-Gram delta: `4.403624367368429e-14`
- Coherent pair witnesses passed: `True` across `15` cases
- Candidate CNOT count: `789` vs source `795`

## Claim Boundary

- This certifies only a six-dimensional finite input span under a fixed numerical tolerance.
- It is not a symbolic full-circuit unitary-equivalence proof.
- It is not arbitrary-input coverage and does not count as B7 resource credit.
- Accepted occurrence removal, proxy-T reduction, and B7 ledger improvement remain 0.
