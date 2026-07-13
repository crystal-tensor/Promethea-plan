# B4/B8 R145 Counterbalanced Repeated-Order Runtime Protocol

- Schedule family: `ABBA` or `BAAB`, selected by a post-preregistration secret
- Repeats per strategy: `2`
- Full / halving executions per repeat: `1728` / `816`
- Full / halving charged executions total: `3456` / `1632`
- Shots per execution: `2048`
- Pooled runtime-reduction floor: `30%`
- Each paired runtime-reduction floor: `20%`
- Maximum pair-reduction spread: `15%`
- Required selection replay: `24 / 24` per strategy
- Measurement executed: `false`

The two adjacent full/halving pairs attack first-run, warm-cache, and order
effects while preserving the R144 timer boundary. Shared preparation and warmup
remain excluded and disclosed separately.

This protocol does not yet support a repeated-order runtime result,
cross-machine or calibration transfer, hardware or billing savings, advantage,
BQP separation, solved-frontier status, or new credit.
