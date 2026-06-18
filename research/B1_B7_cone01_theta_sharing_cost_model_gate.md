# B1/B7 Cone_01 Theta-Sharing Physical Cost-Model Gate

Status: `cone01_theta_sharing_cost_model_not_accepted`

This artifact asks whether the repeated-theta cache signal from T-B1-004f can already be promoted into a physical B7 cost model. The answer is no. A shared synthesis object proposal now exists for the four theta groups, a line-level replay verifier covers the shared objects, and a logical layout/routing scaffold assigns anchors and route packets. A factory-amortization scaffold now accounts for the 35-to-4 compilation-pressure change, a shared-error budget scaffold allocates the object-level synthesis-error budget, and an independent accounting baseline checks for double-counting. A refreshed-B7-ledger attempt is now explicit and rejects theta sharing under the current evidence. The current evidence still lacks occurrence-removing certificates, physical device layout, device-calibrated physical validation, and a passing refreshed B7 ledger.

It is not a rewrite certificate, not a resource-saving claim, and not a physical cost-model acceptance.

## Summary

- Candidate windows: `35`
- Distinct theta groups: `4`
- Duplicate theta occurrences: `31`
- Optimistic cache proxy-T signal: `620`
- Target proxy-T reduction: `600`
- Optimistic cache signal present: `True`
- Shared synthesis object proposals: `4`
- Shared object existence gate passed: `True`
- Shared-theta replay gate passed: `True`
- Replay-verified shared objects: `4`
- Logical layout/routing gate passed: `True`
- Layout-routed shared objects: `4`
- Layout-routed occurrences: `35`
- Layout total / max logical hops: `139` / `11`
- Factory-amortization gate passed: `True`
- Factory baseline/shared-object compilation counts: `35` / `4`
- Factory gross proxy-T delta: `620`
- Shared-error budget gate passed: `True`
- Shared-theta total error budget: `1e-06`
- Shared-theta aggregate per-occurrence error budget: `3.5e-07`
- Shared-theta correlation groups: `4`
- Independent-baseline gate passed: `True`
- Independent-baseline evidence present: `True`
- Double-counted occurrences / proxy-T: `0` / `0`
- Independent-baseline gross proxy-T delta: `620`
- Refreshed-B7-ledger attempt / passed: `True` / `False`
- B7 accepts theta sharing: `False`
- Refreshed B7 proxy-T reduction / gcm_h6 min-row improved: `0` / `False`
- Acceptance gates passed / total: `6` / `8`
- Cost model accepted: `False`
- B7 ledger proxy-T reduction after cost model: `0`
- Additional occurrence certificates required: `30`
- Additional cost-model gates required: `2`
- Validation errors: `0`

## Acceptance Gates

| gate | requirement | current evidence | required evidence | passed |
|---|---|---:|---:|---|
| CM-01 | At least 30 replayable occurrence-removing semantic certificates. | `0` | `30` | `False` |
| CM-02 | A shared synthesis object that replaces repeated theta occurrences, not only a classical template label. | `4` | `4` | `True` |
| CM-03 | A replay verifier for the shared-theta object across all affected windows. | `4` | `4` | `True` |
| CM-04 | An explicit layout/routing model showing where the shared object lives and how windows consume it. | `4` | `True` | `True` |
| CM-05 | A factory-amortization model proving lower T-factory pressure under the shared object. | `620` | `True` | `True` |
| CM-06 | A synthesis-error and correlation budget for shared theta reuse. | `True` | `True` | `True` |
| CM-07 | An independent baseline showing cache-only accounting is not double-counting occurrence cost. | `True` | `True` | `True` |
| CM-08 | A refreshed B7 FT ledger that accepts the model and improves the gcm_h6 min row. | `True` | `True` | `False` |

## Interpretation

The repeated-theta structure is valuable because it identifies where a future physical-sharing proposal would have leverage. The shared object proposal, replay verifier, logical layout/routing scaffold, and factory amortization plus error-budget and independent-baseline scaffolds close six bookkeeping gaps, but they are not enough by themselves. A future PR must satisfy the remaining gates, or bypass the cost-model route by producing 30 occurrence-removing certificates.
