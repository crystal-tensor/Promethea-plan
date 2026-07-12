# B4/B8 R123 Independent-Seed Block Replay

## Summary

- Target: `T-B4-002x/T-B8-003ab/T-B10-009p`
- Upstream target: `T-B4-002w/T-B8-003aa/T-B10-009o`
- Method: `b4_b8_r123_independent_seed_block_replay_v0`
- Status: `independent_seed_block_confidence_stability_boundary`
- Independent seed blocks: `5`
- Trials per block/profile/task: `12`
- Total trial rows: `240`
- Shot budgets: `4096, 8192`
- Honest completeness floor: `0.8`
- Pooled point first crossing: `{'ideal': 8192, 'light': 4096}`
- Pooled confidence first crossing: `{'ideal': 8192, 'light': 8192}`
- Leave-one-block-out confidence first crossing: `{'ideal': None, 'light': 8192}`
- All-block point first crossing: `{'ideal': 8192, 'light': 8192}`
- Fail-to-pass / pass-to-fail transitions: `18` / `3`

- `ideal` / `4096`: pooled weakest point `0.7833`, pooled Wilson lower `0.6638`, minimum leave-one-block-out Wilson lower `0.6122`, point-stable blocks `3/5`.
- `ideal` / `8192`: pooled weakest point `0.9167`, pooled Wilson lower `0.8193`, minimum leave-one-block-out Wilson lower `0.7783`, point-stable blocks `5/5`.
- `light` / `4096`: pooled weakest point `0.8333`, pooled Wilson lower `0.7197`, minimum leave-one-block-out Wilson lower `0.6574`, point-stable blocks `2/5`.
- `light` / `8192`: pooled weakest point `0.9500`, pooled Wilson lower `0.8630`, minimum leave-one-block-out Wilson lower `0.8316`, point-stable blocks `5/5`.

R123 asks whether the R122 boundary survives independent randomization rather
than merely adding more trials to one seed family. Every block has a distinct
root seed. Within a trial, 4,096 shots remain a prefix of the same 8,192-shot
stream and the hidden observable bundle is unchanged. The acceptance summary
reports block-level point stability, pooled Wilson bounds, and the weakest
leave-one-block-out Wilson bound so that one favorable block cannot determine
the confidence result.

## Requirements

- `P1` PASS: accepted R122 confidence boundary is consumed
- `P2` PASS: five distinct root seeds define independent replay blocks
- `P3` PASS: all trial rows preserve matched prefixes and hidden bundles
- `P4` PASS: every block/profile/task has twelve trial rows
- `P5` PASS: every trial binds its declared block seed
- `P6` PASS: block, pooled, and leave-one-block-out statistics are materialized
- `P7` PASS: paired 4096-to-8192 transitions are materialized per block/task
- `P8` PASS: all profile circuits are materialized
- `P9` PASS: synthetic evidence is not promoted to hardware or soundness credit
- `P10` PASS: point, pooled-confidence, and block-robust crossings remain separate

## Claim Boundary

Supported: an independent-seed-block synthetic Aer stability test of the R122
4,096/8,192-shot boundary. Not supported: iid proof, a universal concentration
law, calibrated backend evidence, real hardware execution, protocol or
cryptographic soundness, sampling hardness, quantum advantage, BQP separation,
or B10 credit.
