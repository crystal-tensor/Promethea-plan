# B4/B8/B10 R174 Exact-Score Comparator Protocol

- Status: `preregistered_unopened`
- Protocol payload hash: `7edc13ee94b1bd568061253685dd3977042106211d728dc60f3616fe7e822aa9`
- Contract payload hash: `16187c545a7000102b7e7ef836055bb16b3c2e4a01d1d804ea61807521a9fb24`

## Research Question

Can a fixed-grid exact accumulator repair the two observed one-ULP false winners while preserving every declared non-tie and first-seen tie control?

## Frozen Comparator

Each finite binary64 leaf is decoded into an integer coefficient on the exact `2^-1074` grid. Candidate scores are compared as arbitrary-precision integers, and equality preserves the first candidate seen. The candidate set, Qiskit source, routing output, and target are not modified.

## Frozen Matrix

- R169: 192 target-compatible non-tie replays.
- R170: 192 path-graph exact ties with a source-order one-ULP split.
- R172: 192 nonisomorphic T-tree exact ties with a source-order one-ULP split.
- R160: 4 exact-tie and 28 exact non-tie controls.
- All six candidate permutations per replay must select the first exact minimizer in that permutation.

## Claim Boundary

This is a preregistered shadow-comparator experiment. It is not a Qiskit source patch, production remedy, performance result, hardware result, quantum advantage, BQP separation, solved frontier, or new credit.
