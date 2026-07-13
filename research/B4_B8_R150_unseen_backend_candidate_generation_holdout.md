# B4/B8 R150 Unseen-Backend Candidate-Generation Holdout

- Preregistered verdict: REJECT
- Groups / trial rows / executions: `3` / `24` / `72`
- Portfolio generated-automatic mean / bootstrap lower: `+0.01858639` / `+0.01034859`
- Portfolio generated-denominator mean / bootstrap lower: `-0.00240671` / `-0.00965945`
- Groups above -0.02 versus denominator: `2 / 3`
- Severe rows below -0.05: `0`
- Semantic passes: `6 / 6`
- Conditions passed / failed: `8` / `2`
- New credit delta: `0`

## Backend Evidence

- `FakeCasablancaV2`: generated-denominator `-0.02570231`, generated-auto `-0.00242319`, minimum `-0.03723049`, severe rows `0`.
- `FakeNairobiV2`: generated-denominator `+0.01164795`, generated-auto `+0.03896111`, minimum `+0.00548623`, severe rows `0`.
- `FakePerth`: generated-denominator `+0.00683421`, generated-auto `+0.01922124`, minimum `+0.00010215`, severe rows `0`.

## Acceptance Conditions

- A1 PASS: contract, protocol, routes, denominators, and bindings remain exact; value True, threshold True.
- A2 PASS: groups, rows, executions, and same-seed arms; value [3, 24, 72], threshold [3, 24, 72].
- A3 PASS: all generated and denominator routes retain semantics; value [6, 0.9999999999999956], threshold [6, 0.9999999999].
- A4 PASS: portfolio generated versus automatic noninferiority; value [0.018586386307028763, 0.010348594294917694], threshold [-0.005, -0.01].
- A5 PASS: portfolio generated versus strong denominator noninferiority; value [-0.002406714433797613, -0.009659452970277791], threshold [-0.005, -0.015].
- A6 FAIL: all groups above negative 0.02 versus denominator; value 2, threshold 3.
- A7 PASS: severe row regressions below negative 0.05; value 0, threshold 0.
- A8 FAIL: each backend mean clears negative 0.02; value -0.02570230814978848, threshold -0.02.
- A9 PASS: commitment, hidden rows, reveal, and transcript; value True, threshold True.
- A10 PASS: forbidden claims and credit remain false; value 0, threshold 0.

## Claim Boundary

Supported only if accepted: one preregistered finite dense-XY simulated-noise
verdict on three previously unused fake backend classes. Not supported:
temporal transfer, real-device transfer, hardware performance, general
route-generation advantage, quantum advantage, BQP separation, solved
B4/B8/B10, or new credit.
