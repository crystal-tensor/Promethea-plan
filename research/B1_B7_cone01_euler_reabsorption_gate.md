# B1/B7 cone_01 Restricted Euler Reabsorption Gate

- Status: `cone01_euler_reabsorption_restricted_negative_gate`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- Target cone: `cone_01`
- Candidate windows: 35
- Required exact windows for B7 one-sided target: 30
- Exact RY candidate angle count: 9
- Optimizer seed count per angle: 8
- Fixed RY + RZ reabsorption exact pass count: 0
- Best residual: 0.21253656711362606
- Median residual: 0.3643516233170531
- Editable RZ parameter count range: 0 - 2
- Restricted gate clears B7 target: False
- Validation errors: 0

## Interpretation

This closes another narrow route.  Even when the arbitrary RY is locked to
an exact candidate angle and neighboring target-qubit RZ phases are allowed
to reoptimize inside the same two-CNOT envelope, no cone_01 window passes
the exact gate.  This is not a global obstruction theorem; it is a
restricted numerical gate that points T-B1-004 toward broader two-qubit
synthesis or KAK/Clifford scaffolding.

## Claim Boundary

- Rewrite claimed: False
- Resource saving claimed: False
- Semantic certificate claimed: False
- Obstruction theorem claimed: False

## Best Attempts

| line | qubit | partner | original theta | best fixed RY | residual | editable RZs |
|---:|---:|---:|---:|---:|---:|---:|
| 139 | 2 | 14 | 0.99803486463018931 | pi/4 | 0.21253656711362606 | 1 |
| 1588 | 4 | 14 | 0.99803486463018931 | pi/4 | 0.21253656711362606 | 1 |
| 155 | 10 | 14 | 0.99803486463018953 | pi/4 | 0.21253656711362634 | 1 |
| 1602 | 15 | 14 | 0.99803486463018953 | pi/4 | 0.21253656711362634 | 1 |
| 152 | 10 | 14 | 0.99803486463019042 | pi/4 | 0.2125365671136273 | 2 |
| 1599 | 15 | 14 | 0.99803486463019042 | pi/4 | 0.2125365671136273 | 2 |
| 462 | 16 | 14 | 2.8134684478406058 | pi | 0.32775633313891805 | 2 |
| 477 | 5 | 14 | 2.8134684478406053 | pi | 0.3277563331389185 | 2 |
| 474 | 5 | 14 | 2.8134684478406049 | pi | 0.327756333138919 | 0 |
| 97 | 13 | 14 | 0.42054081161117135 | pi/4 | 0.36435162331705295 | 1 |
| 255 | 2 | 14 | 0.42054081161117135 | pi/4 | 0.36435162331705295 | 1 |
| 348 | 10 | 14 | 0.42054081161117135 | pi/4 | 0.36435162331705295 | 1 |
