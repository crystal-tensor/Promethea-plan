# B4/B8 R124 Preregistered Holdout Block Replay

## Summary

- Target: `T-B4-002y/T-B8-003ac/T-B10-009q`
- Upstream target: `T-B4-002x/T-B8-003ab/T-B10-009p`
- Method: `b4_b8_r124_preregistered_holdout_block_replay_v0`
- Status: `preregistered_disjoint_holdout_block_acceptance_boundary`
- Public preregistration: https://github.com/crystal-tensor/Prometheus-plan/discussions/124
- Contract SHA-256: `18da0e4fe50a98f2830782c04563102371a608e87a0e5859c9b5a65839693604`
- Holdout seed blocks: `5`
- Trials per block/profile/task: `16`
- Total trial rows: `320`
- Control / candidate shots: `4096` / `8192`
- Global preregistered verdict: `ACCEPT`
- Fail-to-pass / pass-to-fail transitions: `26` / `0`

- `ideal` / `4096`: pooled point `0.7625`, pooled Wilson lower `0.6586`, minimum leave-one-block-out lower `0.5823`, blocks above floor `1/5`.
- `ideal` / `8192`: pooled point `0.9750`, pooled Wilson lower `0.9134`, minimum leave-one-block-out lower `0.8930`, blocks above floor `5/5`.
- `ideal` preregistered decision: `ACCEPT`; A1=PASS, A2=PASS, A3=PASS, A4=PASS, A5=PASS
- `light` / `4096`: pooled point `0.8375`, pooled Wilson lower `0.7416`, minimum leave-one-block-out lower `0.7003`, blocks above floor `4/5`.
- `light` / `8192`: pooled point `0.9500`, pooled Wilson lower `0.8784`, minimum leave-one-block-out lower `0.8500`, blocks above floor `5/5`.
- `light` preregistered decision: `ACCEPT`; A1=PASS, A2=PASS, A3=PASS, A4=PASS, A5=PASS

R124 was publicly preregistered before holdout execution. The contract fixes the
root seeds, trial count, profiles, tasks, shot budgets, error tolerance, Wilson
confidence rule, leave-one-block-out rule, all-block point rule, and paired
regression ceiling. Seeds may not be replaced and thresholds may not be revised
after observing the holdout.

## Requirements

- `P1` PASS: contract file matches the publicly posted SHA-256
- `P2` PASS: public preregistration predates holdout execution
- `P3` PASS: contract binds the accepted R123 result payload
- `P4` PASS: holdout root seeds are disjoint from R123
- `P5` PASS: all trial rows preserve paired prefixes and bundles
- `P6` PASS: the preregistered block/profile/task trial count is complete
- `P7` PASS: all schedules are bound to unique hashes
- `P8` PASS: block, pooled, leave-one-out, and transition ledgers are complete
- `P9` PASS: all five preregistered conditions are evaluated per profile
- `P10` PASS: no seed substitution, optional stopping, or threshold revision occurred
- `P11` PASS: all fixed profile circuits are materialized
- `P12` PASS: synthetic holdout verdict grants no hardware, advantage, or BQP credit

## Claim Boundary

Supported: one publicly preregistered synthetic Aer holdout verdict for the
fixed tasks, profiles, and 8,192-shot candidate. Not supported: an iid theorem,
universal shot threshold, calibrated backend evidence, real hardware execution,
protocol or cryptographic soundness, sampling hardness, quantum advantage, BQP
separation, or B10 credit.
