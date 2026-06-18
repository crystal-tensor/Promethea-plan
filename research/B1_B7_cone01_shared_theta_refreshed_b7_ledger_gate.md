# B1/B7 cone_01 Shared-Theta Refreshed-B7-Ledger Gate

Status: `cone01_shared_theta_refreshed_b7_ledger_rejected`

This artifact makes the CM-08 ledger-refresh decision explicit. It reads the current shared-theta cost-model gate and the B7 `gcm_h6` FT boundary, then asks whether the B7 ledger can accept theta sharing as a physical resource saving. The answer is no under current evidence.

It is a rejection gate, not a rewrite certificate, not a physical layout, and not a B7 resource-saving claim.

## Summary

- B7 ledger refresh attempted: `True`
- B7 ledger accepts theta sharing: `False`
- Cost model accepted: `False`
- Cost-model gates passed / failed: `6` / `2`
- CM-08 refreshed-B7-ledger gate passed: `False`
- Candidate windows / theta groups: `35` / `4`
- Optimistic cache proxy-T signal: `620`
- Occurrence-ledger removed occurrences / proxy-T reduction: `0` / `0`
- B7 proxy-T reduction before / after refresh: `0` / `0`
- Target / missing proxy-T reduction for 1.20x: `600` / `600`
- gcm_h6 current total T ledger: `6224`
- gcm_h6 target max after T ledger for 1.20x: `5632`
- gcm_h6 additional T ledger to remove for 1.20x: `592`
- gcm_h6 min row improved: `False`
- Current / refreshed min-STV reduction: `1.086007702182285` / `1.086007702182285`
- Physical layout / factory schedule / device-calibrated validation present: `False` / `False` / `False`
- Validation errors: `0`

## Decision

- Decision: `reject_theta_sharing_as_b7_resource_saving`
- Reason: The shared-theta cost model is not accepted, CM-01 and CM-08 remain failed, and the accepted occurrence-ledger proxy-T reduction is still 0.

## Conditions Required To Accept

- Produce at least 30 occurrence-removing semantic certificates, or accepted equivalent proxy-T ledger reduction.
- Remove all remaining physical cost-model failures.
- Refresh the B7 FT ledger with an accepted physical device/layout/factory interpretation.
- Show an actual gcm_h6 min-row improvement under the same B7 ledger denominator.

## Interpretation

The shared-theta route remains useful as a research target, but the B7 ledger cannot count it yet. The accepted ledger reduction is still 0, so the active route remains either occurrence-removing certificates or a stronger physical model that survives this refresh gate.
