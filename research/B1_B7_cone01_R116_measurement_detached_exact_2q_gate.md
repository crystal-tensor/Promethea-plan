# B1/B7 Cone01 R116 Measurement-Detached Exact 2Q Gate

## Summary

- Target: `T-B1-004hn/T-B7-016w`
- Upstream target: `T-B1-004hm/T-B7-016v`
- Method: `b1_b7_cone01_r116_measurement_detached_exact_2q_gate_v0`
- Status: `cone01_r116_measurement_detached_exact_2q_accepted_finite_probe`
- Model status: `measurement_detached_core_compilation_passes_default_and_22_input_replay`
- Source CX count: `762`
- Candidate CX count: `528`
- CX reduction: `30.7087%`
- Default statevector equivalence: `1/0`
- Multi-input replay: `22/0`
- Maximum multi-input fidelity deficit: `9.992007221626409e-15`
- Final measurement distribution: `1/0`
- B7 credit: `0`

R116 isolates the final measurement before compilation. R115 showed that
transpiling a circuit while its final measurement is present can preserve the
measured bit while changing the unmeasured state. R116 compiles the terminal
measurement-free quantum core, restores the original classical measurement
map, and then checks both the default replay and a finite 22-input probe set.

This is a stronger B1 candidate than R115, but it is not a mathematical proof
of arbitrary-input unitary equivalence. It also does not establish hardware
layout improvement, T-resource reduction, or B7 fault-tolerant credit.

## Requirements

- `P1` PASS: candidate has a nonzero two-qubit reduction
- `P2` PASS: terminal measurements are detached before compilation
- `P3` PASS: default statevector replay passes
- `P4` PASS: final measurement distribution passes
- `P5` PASS: finite multi-input replay passes
- `P6` PASS: multi-input fidelity deficit stays within tolerance
- `P7` PASS: measurement error stays within tolerance
- `P8` PASS: candidate and all checker outputs are materialized
- `P9` PASS: B7 credit remains zero until hardware and resource ledgers are closed
- `P10` PASS: claim boundary excludes arbitrary proof and hardware claims

## Claim Boundary

Supported: a replayable 30.7087% CX reduction for this terminal-measurement
workload, with default statevector equivalence, final measurement-distribution
equivalence, and 22 finite input probes passing at the recorded tolerances.
Not supported: arbitrary-input proof, mid-circuit measurement semantics,
hardware layout improvement, T-resource reduction, or B7 credit.
