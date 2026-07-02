# B3/B10 F1 N2 Shard Batch Gate

- Target: `T-B3-030/T-B10-015q`
- Method: `b3_b10_f1_n2_shard_batch_gate_v0`
- Status: `n2_full_covariance_shard_batch_recorded_zero_credit`
- N2 shard batch hash: `114210ba9469fce622225f85bd8ef0315f5f7d406d83da803a8619d517f7710d`
- N2 shards: 19/19
- Global shards: 26/65

## Result

The gate records a complete N2 shard batch for the F1 route. It passes 7/10 requirements and intentionally fails ['P8', 'P9', 'P10'] because LiH shards, assembled rows, and the accepted four-row F1 artifact do not exist yet.

## N2 Batch Metrics

- Compiled cover groups: 9476
- Planning proxy groups: 9475
- Nonzero covariance pairs: 36162
- Variance sum: 51.76304837681597
- Remaining global shards: 39

## Requirements

- `P1` PASS: Work-order gate is current and recognizes the worker
- `P2` PASS: All expected N2 shard files exist
- `P3` PASS: Every N2 shard was produced by the full-covariance worker
- `P4` PASS: N2 shards form one contiguous compiled QWC cover
- `P5` PASS: N2 shard batch hash is stable
- `P6` PASS: Required worker hashes are present on every N2 shard
- `P7` PASS: Claim boundaries preserve zero credit
- `P8` FAIL: All 65 global F1 shard outputs have been produced
- `P9` FAIL: LiH/H2O/N2 rows are assembled from all shards
- `P10` FAIL: Four-row F1 artifact is accepted

## Claim Boundary

- Supported: All nineteen N2 compiled-state full-covariance shard outputs exist and form one contiguous compiled QWC cover.
- Not supported: This is not an assembled F1 row, not a LiH result, not a four-row F1 artifact, not a denominator win, not B3/B10 credit, and not quantum advantage.
