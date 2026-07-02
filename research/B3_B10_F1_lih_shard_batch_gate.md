# B3/B10 F1 LiH Prefix Shard Gate

- Target: `T-B3-038/T-B10-015y`
- Method: `b3_b10_f1_lih_shard_batch_gate_v0`
- Status: `lih_full_covariance_shard_batch_recorded_zero_credit`
- LiH prefix batch hash: `90696fee6a697a71a102fae1e6de02b623d7182bb86d7d2c990619eede78ff12`
- LiH prefix shards: 39/39
- Global shards: 65/65

## Result

The gate records the first 39 LiH shard outputs for the F1 route. It passes 8/10 requirements and intentionally fails ['P9', 'P10'] because the rest of LiH, assembled rows, and the accepted four-row F1 artifact do not exist yet.

## LiH Prefix Metrics

- Prefix groups: 19645
- Compiled cover groups: 19645
- Planning proxy groups: 19644
- Nonzero covariance pairs: 77283
- Variance sum: 2.088567890506452
- Remaining LiH shards: 0
- Remaining global shards: 0

## Requirements

- `P1` PASS: Work-order gate is current and recognizes the worker
- `P2` PASS: All expected LiH prefix shard files exist
- `P3` PASS: Every LiH prefix shard was produced by the full-covariance worker
- `P4` PASS: LiH prefix shards form one contiguous compiled QWC prefix
- `P5` PASS: LiH prefix shard hashes are stable
- `P6` PASS: Required worker hashes are present on every prefix shard
- `P7` PASS: Claim boundaries preserve zero credit
- `P8` PASS: All 65 global F1 shard outputs have been produced
- `P9` FAIL: LiH/H2O/N2 rows are assembled from all shards
- `P10` FAIL: Four-row F1 artifact is accepted

## Claim Boundary

- Supported: All 39 LiH compiled-state full-covariance shard outputs exist and form a complete compiled QWC batch.
- Not supported: This is not an assembled F1 row, not a four-row F1 artifact, not a denominator win, not B3/B10 credit, and not quantum advantage.
