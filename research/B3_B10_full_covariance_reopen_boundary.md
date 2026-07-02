# B3/B10 Full-Covariance Reopen Boundary

Status: `b3_b10_full_covariance_reopen_boundary_synced`

## Summary

- Method: `b3_b10_full_covariance_reopen_boundary_v0`
- Boundary: `B3-B10-full-covariance-reopen-boundary`
- Boundary hash: `ddeecdff97f61bf096acf6601ed7a09cbaaa4b566cc1d333828992c6f5cf1b5d`
- Source acceptance packet: `B3-R1-full-covariance-row-acceptance-packet`
- Source acceptance packet hash: `24b94105d0b0de8d88fb1a6f456cdf1769dcd2efac8186594900c3bc3fff1f69`
- Downstream packet: `B3-R1-full-compiled-covariance`
- Row replay-validation manifest: `B3-R1-full-covariance-row-replay-validation-manifest`
- Requirements passed/failed: `7` / `0`
- Failed requirement IDs: `[]`
- Source failed acceptance IDs: `['P8']`
- Row-aligned / compiled-pilot instances: `4` / `1`
- Accepted full-covariance rows / priority reopen rows: `0` / `0`
- Denominator wins / selected-CI larger-basis wins: `0` / `0`
- Optimizer-loop lower-bound shots: `475043013690000`
- B3 reopen / B3 credit / B10-T1 credit / positive route allowed: `False` / `False` / `False` / `False`
- validation_error_count: `0`

## Required Downstream Evidence Before B3 Reopen

- submitted B3-R1-full-covariance-row-acceptance-packet
- accepted full compiled-state covariance row table for all 4 row-aligned instances
- compiled-state replay and covariance replay for multi-parameter/converged chemistry states
- derivative estimator replay and optimizer-loop cost ledger beating the current lower-bound pressure
- same-access denominator win ledger with denominator_win_count > 0
- B10 access-boundary replay accepting the positive route without oracle or data-loading leakage
- B3 reopen boundary that preserves claim discipline until rows are accepted
- claim boundary forbidding reaction-dynamics solution, quantum advantage, and BQP separation before acceptance

## Requirement Results

- S1 [PASS]: Source B3/B10 full-covariance row acceptance packet gate is present and current
- S2 [PASS]: Source acceptance gate remains blocked before row credit
- S3 [PASS]: B3 full-covariance row scope and current denominator pressure are preserved
- S4 [PASS]: No full-covariance row, reopen row, or denominator win has been accepted
- S5 [PASS]: B3 reopen, B3 credit, B10-T1 credit, and positive same-access route remain disabled
- S6 [PASS]: Forbidden solution, advantage, BQP, and positive-route claims remain absent
- S7 [PASS]: Boundary records downstream evidence required before B3 can reopen

## Claim Boundary

- Supported: B3 is explicitly synchronized to the B3/B10 full-covariance row acceptance packet as a zero-credit reopen boundary.
- Not supported: No accepted full-covariance row, B3 reopen, reaction-dynamics solution, positive same-access route, quantum advantage, BQP separation, or B10-T1 credit is supported.
- Next gate: Submit and accept the full-covariance row acceptance packet with four source-backed full-covariance rows, compiled-state and covariance replay, optimizer-loop cost replay, same-access denominator wins, B10 access-boundary acceptance, and claim boundary before B3 can reopen.
- b3_reopen_ready: False
- b3_full_covariance_credit_allowed: False
- positive_same_access_route_allowed: False
- b10_t1_credit_allowed: False

## Validation

- validation_error_count: 0
