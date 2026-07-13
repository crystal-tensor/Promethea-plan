# B4/B8 R144 Live Runtime Protocol

- Full executions: `1728`
- Successive-halving executions: `816`
- Shots per execution: `2048`
- Strategy order: post-preregistration secret
- Runtime reduction floor: `30%`
- Maximum selection disagreement: `2 / 12`
- Maximum full-budget LCB regret: `0.001`
- Measurement executed: `false`

Shared source loading, circuit preparation, semantic checks, and one warmup per
backend are excluded and reported separately. The timer covers fresh simulator
creation, automatic compilation, circuit execution, online LCB updates, and
candidate elimination.

This protocol does not yet support measured wall-clock savings,
cross-calibration transfer, hardware, advantage, BQP, or new credit.
