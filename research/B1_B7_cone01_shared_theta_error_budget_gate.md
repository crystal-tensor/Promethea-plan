# B1/B7 Cone_01 Shared-Theta Error-Budget Scaffold

Status: `cone01_shared_theta_error_budget_scaffold`

This artifact adds CM-06 bookkeeping for the replayed, logically routed, and factory-amortized shared-theta objects. It gives each shared object a scaffold-level synthesis-error allocation and records the correlation group that would need independent validation before theta sharing could be accepted as a physical cost model.

It is not a hardware noise model, not an independent calibration, not a semantic rewrite certificate, and not a B7 resource-saving claim.

## Summary

- Candidate windows: `35`
- Shared objects: `4`
- Layout-routed occurrences: `35`
- Total shared-theta error budget: `1e-06`
- Per-object error budget: `2.5e-07`
- Per-occurrence error budget: `1e-08`
- Aggregate per-occurrence error budget: `3.5e-07`
- Aggregate object error budget: `1e-06`
- Correlation groups: `4`
- Max correlated occurrences: `16`
- Shared-error budget gate passed: `True`
- Independent calibration present: `False`
- Hardware noise model present: `False`
- Cost model accepted: `False`
- B7 ledger improvement claimed: `False`
- Validation errors: `0`

## Object Budgets

| object | occurrences | per-object budget | per-occurrence total | margin | correlated occurrences |
|---|---:|---:|---:|---:|---:|
| cone01_shared_theta_01 | 16 | `2.5e-07` | `1.6e-07` | `9e-08` | `16` |
| cone01_shared_theta_02 | 10 | `2.5e-07` | `1e-07` | `1.5e-07` | `10` |
| cone01_shared_theta_03 | 6 | `2.5e-07` | `6e-08` | `1.9e-07` | `6` |
| cone01_shared_theta_04 | 3 | `2.5e-07` | `3e-08` | `2.2e-07` | `3` |

## Interpretation

This closes the CM-06 bookkeeping gap, but only as a scaffold. A future PR must still supply an independent baseline and a refreshed B7 ledger, or bypass the cost-model route by producing 30 occurrence-removing semantic certificates.
