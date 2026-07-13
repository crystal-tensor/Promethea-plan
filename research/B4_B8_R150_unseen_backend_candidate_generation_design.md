# B4/B8 R150 Unseen-Backend Candidate Generation Design

- New fake backends: `3`
- Enumerated mappings: `15120`
- Generated candidates / denominator pool: `144` / `240`
- Selection / diagnostic / total executions: `792` / `48` / `840`
- Semantic passes: `384 / 384`
- Public diagnostic groups above -0.02: `2 / 3`
- Minimum public diagnostic delta: `-0.02514781`
- R149 hidden rows read: `0`
- Holdout executed: `false`

- `FakeCasablancaV2`: generated `[1, 6, 3, 4, 5, 2]` / `selected_o3_default` / `15001`, denominator seed `150144`, public diagnostic delta `-0.02514781`.
- `FakeNairobiV2`: generated `[2, 1, 4, 3, 0, 5]` / `selected_o3_default` / `15001`, denominator seed `150144`, public diagnostic delta `+0.00966658`.
- `FakePerth`: generated `[3, 0, 2, 1, 6, 5]` / `selected_o3_lookahead` / `15001`, denominator seed `150144`, public diagnostic delta `+0.00345661`.

The same R149 generation recipe is applied independently to Casablanca,
Nairobi, and Perth, which were absent from the R125-R149 portfolio. Each
generated route is pressure-tested against the best calibration-exposure route
from 80 independently seeded optimization-level-3 compilations. Diagnostics
are recorded only after selection and cannot alter the chosen route.

This design does not establish a hidden holdout result, temporal or real-device
transfer, hardware performance, general route-generation advantage, quantum
advantage, BQP separation, a solved frontier, or new credit.
