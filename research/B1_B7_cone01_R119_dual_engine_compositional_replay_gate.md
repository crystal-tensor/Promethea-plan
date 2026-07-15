# B1/B7 Cone01 R119 Dual-Engine Compositional Replay Gate

## Summary

- Target: `T-B1-004hq/T-B7-016z`
- Upstream target: `T-B1-004hp/T-B7-016y`
- Method: `b1_b7_cone01_r119_dual_engine_compositional_replay_gate_v0`
- Status: `cone01_r119_dual_engine_composition_accepted_finite_evidence`
- Full probes: `24/24`
- Composition rows: `48/48`
- Maximum cross-engine fidelity deficit: `3.3306690738754696e-16`
- Maximum prefix/suffix composition deficit: `2.220446049250313e-16`
- Source/Candidate CX: `762 -> 528`
- B7 credit: `0`

R119 subjects the R116 candidate to two independent replay semantics. The
Qiskit Statevector engine and the repository's NumPy gate engine receive the
same 24 structured inputs. Each source and candidate circuit is also split at
three gate frontiers; prefix output is fed into the suffix and compared with
the unsplit replay in both engines. An inserted-X candidate is retained as a
negative control.

The composition check validates replay structure and cross-engine agreement;
it does not turn finite probes into an exact arbitrary-input theorem. The
candidate still has no hardware, T-resource, or B7 ledger credit.

## Requirements

- `P1` PASS: accepted R116 and R118 artifacts are consumed
- `P2` PASS: same 24 probes are replayed by NumPy and Qiskit
- `P3` PASS: source/candidate semantics agree in both engines
- `P4` PASS: NumPy and Qiskit agree on full replay outputs
- `P5` PASS: prefix/suffix composition agrees at three frontiers
- `P6` PASS: composition and cross-engine deficits stay within tolerance
- `P7` PASS: inserted-X negative control is detected
- `P8` PASS: source measurement map and CX reduction are preserved
- `P9` PASS: replay and composition artifacts are materialized
- `P10` PASS: formal arbitrary-input, hardware, and B7 claims remain excluded

## Claim Boundary

Supported: dual-engine finite replay and prefix/suffix composition agree for
the R116 source/candidate pair, while the negative control is detected. Not
supported: formal arbitrary-input unitary equality, mid-circuit measurement
semantics, hardware layout improvement, T-resource reduction, or B7 credit.
