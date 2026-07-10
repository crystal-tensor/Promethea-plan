# B1/B7 Cone01 R113 Adversarial 2Q Reduction Gate

## Summary

- Target: `T-B1-004hk/T-B7-016t`
- Upstream target: `T-B1-004hj/T-B7-016s`
- Method: `b1_b7_cone01_r113_adversarial_2q_reduction_gate_v0`
- Status: `cone01_r113_adversarial_2q_reduction_rejected_non_equivalent`
- Model status: `qiskit_level3_two_qubit_reduction_fails_exact_equivalence`
- Source two-qubit gates: `762.0`
- Candidate two-qubit gates: `528.0`
- Apparent two-qubit reduction: `30.7087%`
- Exact equivalence: `0/1`
- Candidate accepted: `False`

R113 runs an adversarial Qiskit level-3 all-to-all `u3/cx` optimization. It
appears to save two-qubit gates, but the local exact statevector checker rejects
the candidate. This is a useful negative result: a nonzero two-qubit delta is
not enough to enter the B1/B7 ledger.

## Requirements

- `P1` PASS: source and candidate metrics are materialized
- `P2` PASS: candidate shows a nonzero two-qubit reduction
- `P3` PASS: exact equivalence checker rejects the candidate
- `P4` PASS: candidate acceptance is gated on exact equivalence
- `P5` PASS: rejection keeps counters and credit at zero
- `P6` PASS: adversarial claim boundary is recorded
- `P7` PASS: candidate circuit is hashable and replayable
- `P8` PASS: no B7 promotion occurs from the rejected 2Q delta

## Claim Boundary

R113 supports only the rejection of this candidate on this workload. It does
not claim that Qiskit level 3 is generally incorrect, nor does it claim a
minimality theorem. No occurrence removal, proxy-T reduction, layout credit,
or B7 credit is accepted.
