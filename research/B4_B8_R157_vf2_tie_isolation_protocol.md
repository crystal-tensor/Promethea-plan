# B4/B8 R157 VF2 Tie-Isolation Protocol

- Input QASM hash / size / depth: `ce216610e995b4c8b4bd9de6547ac6069961e1eb8881997aa05e0068ea16ab98` / `77` / `39`
- Target descriptor: `702c8fd9dcf67a069e7af63e31a57c74c17aaa5e3c5b6d8c2e28ec0c049c0de7`
- Profiles / OS processes / direct replays: `5` / `98` / `160`
- VF2 seed / strict direction / max trials: `-1` / `false` / `250000`
- Recomputed mapping score A / B: `0.45894321220828727` / `0.45894321220828727`
- Scores exactly equal: `true`
- Simulation executions / shots: `0` / `0`
- Contract SHA-256: `f45f7e7fe285dc86307201063a3351a40293d888625f7bd790446f25a7d50dc4`
- Execution started: `false`

## Frozen Isolation

R157 removes the first sixteen full-pipeline passes from the experimental
surface. Every direct replay reads the same 77-operation OpenQASM 3 input whose
hash equals the R156 callback-16 circuit hash, then runs the exact R156
`VF2PostLayout` configuration. Three independent-process profiles compare the
native FakeNairobi target with targets rebuilt in ascending and descending
operation/qargs order. Two same-process profiles distinguish fresh target
construction from repeated use of one shared target.

The two R156 endpoint mappings have the same independently recomputed average-
error score, `0.45894321220828727`. This motivates a tie-order experiment but
does not establish the lower-level mechanism. Mapping collapse, continued
variation, a new mapping, or no solution are all valid diagnostic outcomes.
The unopened protocol makes no confirmed Qiskit-bug, general determinism,
hardware, transfer, route-advantage, quantum-advantage, BQP, solved-frontier,
or research-credit claim.
