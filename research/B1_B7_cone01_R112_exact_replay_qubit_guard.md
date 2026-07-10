# B1/B7 Cone01 R112 Exact Replay Qubit Guard

## Summary

- Target: `T-B1-004hj/T-B7-016s`
- Upstream target: `T-B1-004hi/T-B7-016r`
- Method: `b1_b7_cone01_r112_exact_replay_qubit_guard_v0`
- Status: `cone01_r112_exact_replay_passed_qubit_guard_explicit`
- Model status: `13_qubit_exact_replay_passes_but_no_two_qubit_or_b7_credit`
- Source: `benchmarks/qasmbench_medium_exact/gcm_h6.qasm`
- Qubit count: `13`
- Exact equivalence at max 13 qubits: `1/0`
- Operation reduction: `41.1877%`
- Logical-depth reduction: `40.0899%`
- Hardware-exposure reduction: `9.9003%`
- Two-qubit gate delta: `0.0`

R112 makes the qubit-limit boundary executable. The default `max-qubits=12`
guard rejects this 13-qubit workload; rerunning with `max-qubits=13` passes exact
statevector equivalence. The local rewrite certificates are valid, but the
two-qubit count does not change, so this is not a B7 resource-saving claim.

## Requirements

- `P1` PASS: source workload has 13 qubits
- `P2` PASS: max-qubits=12 rejects the 13-qubit workload explicitly
- `P3` PASS: max-qubits=13 exact equivalence passes
- `P4` PASS: local rewrite certificates are emitted
- `P5` PASS: operation, depth, and exposure improve on this workload
- `P6` PASS: two-qubit gate count does not receive false credit
- `P7` PASS: replay artifacts are materialized and hashable
- `P8` PASS: claim boundary keeps B7 credit at zero

## Claim Boundary

R112 supports one exact replay of the fixed-point local-rewrite pipeline on
`gcm_h6.qasm`. It does not establish arbitrary-input equivalence, a reduction
in two-qubit gates, a non-Clifford/T-resource reduction, a layout improvement,
or any B7 credit.
