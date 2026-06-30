# B4/B8 Real-Backend Soundness Margin Gate v0.1

Status: **real_backend_soundness_margin_failed_missing_real_backend_rows**

## Summary

- Method: `b4_b8_real_backend_soundness_margin_gate_v0`
- Model status: `synthetic_holdout_acceptance_margins_quantified_not_soundness`
- Requirements passed/failed: 5 / 3
- Failed requirement IDs: ['M4', 'M5', 'M6']
- Holdout rows / real backend rows: 160 / 0
- Private-safe no-leak accepts: 10 / 160
- Leakage-blind no-leak accepts: 56 / 160 (excess 40)
- Full-leakage accepts: 160 / 160 (excess 120)

## Acceptance Budgets

| channel | threshold | observed accepts | allowed accepts | excess accepts | passes |
| --- | ---: | ---: | ---: | ---: | --- |
| private-safe no-leak | 0.1 | 10 | 16 | 0 | True |
| leakage-blind no-leak | 0.1 | 56 | 16 | 40 | False |
| full private-material leakage | 0.25 | 160 | 40 | 120 | False |

## Requirement Results

- M1 [PASS]: Real-backend packet scout is present and still blocks promotion
- M2 [PASS]: Holdout denominator and fitted-evaluation rows are explicit
- M3 [PASS]: Private-safe no-leak fitted acceptance is within the no-leak threshold
- M4 [FAIL]: Leakage-blind no-leak fitted acceptance is within the no-leak threshold
- M5 [FAIL]: Full-private-material leakage is contained within the leakage threshold
- M6 [FAIL]: Real backend transcript rows exist before claiming soundness margins
- M7 [PASS]: Next PR acceptance budgets are computable from the current holdout denominator
- M8 [PASS]: Forbidden soundness, advantage, and BQP claims remain false

## Claim Boundary

- Supported: The synthetic fitted-spoofer holdout margins are quantified as acceptance budgets for the next real-backend PR.
- Not supported: No real backend transcript rows exist, leakage-blind no-leak acceptance still exceeds the 0.10 threshold, full leakage is not contained, and no protocol soundness, quantum advantage, or BQP separation is established.
- Next gate: Collect real backend transcript rows and make leakage-blind no-leak acceptance <= 16/160 while full-private-material leakage is either excluded or <= 40/160.
- protocol_soundness_proved: False
- quantum_advantage_claimed: False
- bqp_separation_claimed: False

## Validation

- validation_error_count: 0
