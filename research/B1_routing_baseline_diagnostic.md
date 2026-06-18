# B1 Routing Baseline Diagnostic v0.1

Last updated: 2026-06-13

Status: **diagnostic_only_not_validated_baseline**

## Summary

This report records a Qiskit line-coupling routing diagnostic for the 30-circuit B1 exact suite. It is useful evidence, but it is not a validated calibrated heavy-hex baseline.

- Source circuits: 30
- Full exact-valid baseline: False
- Full measurement-distribution-valid baseline: True
- Partial measurement-distribution-valid levels: [0, 1, 3]
- Common unsupported/failing circuit: []
- Aer cross-check all passed: True
- Aer cross-check pairs: 90
- Aer cross-check max TVD: 0.04984
- Best diagnostic level by exposure: 3
- Best diagnostic exposure reduction: -31.86%

## Level Results

| Level | Statevector pass/fail | Measurement distribution pass/fail | Operation | 2Q gates | Depth | Exposure |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 11 / 19 | 30 / 0 | -59.81% | -173.66% | -68.46% | -131.42% |
| 1 | 10 / 20 | 30 / 0 | -9.31% | -111.02% | -14.43% | -78.76% |
| 3 | 7 / 23 | 30 / 0 | 8.99% | -50.10% | 14.83% | -31.86% |

Negative reduction means the routed baseline worsened that metric.

## Aer Cross-Check

| Level | Pairs pass/fail | Shots | Max TVD | Max threshold |
|---:|---:|---:|---:|---:|
| 0 | 30 / 0 | 32768 | 0.04984 | 0.20066 |
| 1 | 30 / 0 | 32768 | 0.04672 | 0.20066 |
| 3 | 30 / 0 | 32768 | 0.04819 | 0.20066 |

## Interpretation

- No line-routing optimization level currently passes the bare statevector checker on all 30 circuits.
- The sequential measurement-distribution checker models mid-circuit measurement by branching and collapse, so it is the relevant diagnostic for circuits that keep using measured qubits.
- All tested line-routing levels pass measurement-distribution equivalence on the 30-circuit suite under the sequential measurement model.
- Observed measurement-distribution pass counts across levels: 30/30.
- Independent Qiskit Aer shot-based cross-check passes all routed pairs.
- All tested line-routing levels worsen hardware-weighted exposure on this sparse line coupling map, so this diagnostic does not weaken the current B1 advantage versus all-to-all exact-valid Qiskit baselines.
- This is not a calibrated heavy-hex routing baseline; that gate remains open.

## Open Gates

- Add calibrated heavy-hex routing baseline with a device-like coupling map and noise/error model.
- Turn the Aer shot-based cross-check into either an exact independent probability check or a larger-shot statistical regression before promoting it beyond diagnostic evidence.
- Decide whether routing baseline comparison should use output-distribution equivalence, unitary equivalence with layout recovery, or both.
