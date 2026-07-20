# B4/B8/B10 R175 Integrated Rust Exact-Score Protocol

- Status: `preregistered_unopened`
- Protocol payload hash: `da6c45dcf78242c55d8580baaa4d090b69dedec8cc0a5d623084f0585d5183b2`
- Contract payload hash: `f3d3bb02d3ebeb8afc354b7091ce4e262df108fdd0fd136d4fc23a44023e8230`

## Research Question

Can an exact retained-binary64 accumulator inside Qiskit's compiled Rust VF2 path repair true ties and sub-ULP non-ties while preserving ordinary mappings at bounded runtime and memory cost?

## Frozen Matrix

- R169 ordinary non-tie: 3 profiles x 64 calls x 2 policies.
- R170 first true-tie graph: 3 profiles x 64 calls x 2 policies.
- R172 second true-tie graph: 3 profiles x 64 calls x 2 policies.
- R157/R160 sub-ULP controls: 4 ErrorMap modes x 7 cases x 8 calls x 2 policies.
- Total recorded calls: 1,600; each policy contributes 800.
- Each of 26 isolated workers performs 16 unrecorded warmups before measurement.

## Frozen Performance Gates

- Every exact/source median-time ratio must be at most 3.0.
- The aggregate exact/source median-time ratio must be at most 2.5.
- The maximum exact/source worker peak-RSS ratio must be at most 1.25.

## Claim Boundary

This is a source-bound experimental Rust entry point built from Qiskit 2.4.1 commit `0fd015a22b84c9082173597a5d2304dc0aaec08c`. It is not an upstream-accepted or production Qiskit patch, a confirmed Qiskit bug, a route-quality result, a hardware result, quantum advantage, BQP separation, a solved frontier, or new credit.
