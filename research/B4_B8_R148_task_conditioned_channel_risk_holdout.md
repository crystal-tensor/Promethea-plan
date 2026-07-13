# B4/B8 R148 Task-Conditioned Channel-Risk Holdout

- Preregistered verdict: REJECT
- Groups / trial rows: `12` / `96`
- Three-arm executions / shots: `288` / `589824`
- Portfolio conditioned-automatic mean / bootstrap lower: `+0.00216544` / `+0.00055207`
- Portfolio conditioned-target mean / bootstrap lower: `-0.00486511` / `-0.00690479`
- Groups above -0.02 versus target: `11 / 12`
- Severe rows below -0.05 versus target: `0`
- Minimum target-snapshot mean: `-0.00762165`
- Minimum R147 failure-group mean / combined severe rows: `-0.02798808` / `0`
- Semantic passes: `24 / 24`
- Conditions passed / failed: `9` / `1`
- New credit delta: `0`

## Target Snapshot Evidence

- `FakeJakartaV2`: conditioned-target `-0.00762165`, conditioned-auto `-0.00160193` over `32` rows.
- `FakeLagosV2`: conditioned-target `-0.00336261`, conditioned-auto `+0.00153678` over `32` rows.
- `FakeOslo`: conditioned-target `-0.00361109`, conditioned-auto `+0.00656146` over `32` rows.

## R147 Failure-Group Repairs

- `FakeJakartaV2::dense_validation_complete_ising_n6`: mean `-0.00406249`, minimum `-0.00773353`, severe rows `0`.
- `FakeJakartaV2::dense_validation_xy_network_n6`: mean `-0.02798808`, minimum `-0.03821143`, severe rows `0`.
- `FakeLagosV2::dense_validation_complete_ising_n6`: mean `-0.00610122`, minimum `-0.01788604`, severe rows `0`.

## Acceptance Conditions

- A1 PASS: protocol, selector, route identities, and source bindings remain exact; value True, threshold True.
- A2 PASS: groups, rows, and executions; value [12, 96, 288], threshold [12, 96, 288].
- A3 PASS: all conditioned and target routes retain semantic fidelity; value [24, 0.9999999999999973], threshold [24, 0.9999999999].
- A4 PASS: portfolio conditioned versus automatic noninferiority; value [0.0021654388194870936, 0.0005520747789749848], threshold [-0.005, -0.01].
- A5 PASS: portfolio conditioned versus target-specific noninferiority; value [-0.004865114915543493, -0.006904793190435366], threshold [-0.005, -0.01].
- A6 PASS: groups above negative 0.02 versus target; value 11, threshold 11.
- A7 PASS: severe row regressions below negative 0.05; value 0, threshold 0.
- A8 FAIL: each-target and all R147 failure-group guards; value [-0.007621649124578148, -0.027988081524400993, 0], threshold [-0.01, -0.02, 0].
- A9 PASS: commitment, hidden rows, reveal, and transcript; value True, threshold True.
- A10 PASS: forbidden claims and credit remain false; value 0, threshold 0.

## Claim Boundary

Supported only if accepted: one preregistered finite six-qubit synthetic
task-conditioned foreign-route verdict. Not supported: scalable exact-output
evaluation, temporal same-device transfer, cross-machine transfer, provider
access, real hardware, mitigation, soundness, quantum advantage, BQP
separation, solved B4/B8/B10, or new credit.
