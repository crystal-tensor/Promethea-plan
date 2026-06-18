# B7 Precision-Aware Rotation Ledger v0.1

Last updated: 2026-06-15

Status: **precision_aware_rotation_ledger_negative_boundary_not_physical_layout**

## Summary

- Source ledger: `results/B7_ft_synthesis_ledger_v0.json`
- Source boundary: `results/B7_gcm_h6_ft_boundary_v0.json`
- Method: `b7_precision_aware_rotation_ledger_v0`
- Current portfolio min row: `qasmbench_medium_exact/gcm_h6.qasm` / `throughput_heavy_factories`
- Current portfolio min STV reduction: 1.086008x
- gcm_h6 arbitrary numeric rotations after B1/B7 passes: 270
- gcm_h6 non-arbitrary exact T ledger after passes: 824
- gcm_h6 current total T ledger after passes: 6224
- Precision budgets clear 1.20x all-variant min: False
- Precision budgets clear 1.20x gcm_h6 min: False
- Interpretation: Under the explicit uniform synthesis-error budgets tested here, the implied arbitrary-rotation T cost is above the previous fixed cost 20 assumption, so precision-aware synthesis does not close the gcm_h6 1.20x boundary.  The one-sided 1.20x gcm_h6 throughput row would need after-row average arbitrary-rotation cost at or below the reported target-cost requirement; when a synthesis-cost change is applied to both before and after rows, the portfolio still does not clear 1.20x.  A real solution therefore needs a structural reduction in arbitrary rotations, data rounds, factory timing, or layout.

## Cost Model

- Name: `ross_selinger_style_proxy`
- Formula: `ceil(alpha * log2(1 / per_rotation_error_budget) + beta)`
- alpha / beta: 3.0 / 0.0
- Allocation: uniform_total_synthesis_error_budget_over_after_arbitrary_numeric_rotations
- Caveat: planning proxy only; not a certified Clifford+T synthesis run

## Target Cost Requirements For gcm_h6 Throughput Row

| target STV | max after T ledger | exact after T ledger | arbitrary rotations | max avg arbitrary T cost | total error budget needed at max cost proxy | fixed cost 20 meets target |
|---:|---:|---:|---:|---:|---:|---|
| 1.200x | 5632 | 824 | 270 | 17 | 5.31529 | False |
| 1.250x | 5400 | 824 | 270 | 16 | 6.69685 | False |

## Precision Budget Sweep

| total error budget | per-rotation budget | implied arbitrary T cost | portfolio min STV | gcm_h6 min STV | min row |
|---:|---:|---:|---:|---:|---|
| 0.1 | 3.704e-04 | 35 | 1.079316x | 1.079316x | qasmbench_medium_exact/gcm_h6.qasm / throughput_heavy_factories |
| 0.01 | 3.704e-05 | 45 | 1.077921x | 1.077921x | qasmbench_medium_exact/gcm_h6.qasm / serial_factory |
| 0.001 | 3.704e-06 | 55 | 1.076492x | 1.076492x | qasmbench_medium_exact/gcm_h6.qasm / throughput_heavy_factories |
| 1.000e-04 | 3.704e-07 | 65 | 1.075702x | 1.075702x | qasmbench_medium_exact/gcm_h6.qasm / serial_factory |
| 1.000e-06 | 3.704e-09 | 85 | 1.074491x | 1.074491x | qasmbench_medium_exact/gcm_h6.qasm / serial_factory |

## Relaxed Fixed-Cost Rows

| arbitrary T cost | portfolio min STV | gcm_h6 min STV | min row | after factory/data rows |
|---:|---:|---:|---|---:|
| 16 | 1.089369x | 1.089369x | qasmbench_medium_exact/gcm_h6.qasm / balanced_factories | 16 / 2 |
| 17 | 1.088463x | 1.088463x | qasmbench_medium_exact/gcm_h6.qasm / serial_factory | 16 / 2 |
| 18 | 1.087079x | 1.087079x | qasmbench_medium_exact/gcm_h6.qasm / throughput_heavy_factories | 16 / 2 |
| 20 | 1.086008x | 1.086008x | qasmbench_medium_exact/gcm_h6.qasm / throughput_heavy_factories | 16 / 2 |

## Numeric Rotation Reuse Probe

- QASM path: `results/b1_u3_phase_factored_optimizer/qasmbench_medium_exact/gcm_h6.qasm`
- Numeric parameter occurrences: 270
- Unique numeric parameters: 26
- Numeric instruction occurrences: 270
- Unique numeric instructions: 26

| numeric parameter | count |
|---|---:|
| `0.36485735178627743` | 24 |
| `0.36485735178627726` | 24 |
| `1.4922506383856682` | 24 |
| `2.1870074319274799` | 24 |
| `0.52538524712872736` | 24 |
| `2.538142068316358` | 24 |
| `1.1254377896453873` | 24 |
| `0.28861107553559073` | 24 |
| `0.42054081161117118` | 24 |
| `0.42054081161117135` | 21 |
| `0.99803486463019042` | 4 |
| `2.8134684478406049` | 4 |

## Next Actions

- Attempt a gcm_h6 numeric-rotation structure pass that merges or cancels repeated arbitrary angles.
- Test shared-synthesis/cache assumptions for repeated numeric angles as a separate non-physical proxy.
- Add layout/factory/feed-forward timing assumptions only after the synthesis/error-budget claim is explicit.
- If no structural pass reduces arbitrary rotations, move B7 attention to layout/factory or B1 semantic rewrites.

## Limits

- This is not a physical layout, lattice-surgery, or certified synthesis result.
- The Ross-Selinger-style proxy is used only to expose the error-budget direction of pressure.
- The uniform error allocation is deliberately simple; better allocation can be tested as a future PR.
- The QASM reuse probe counts textual numeric parameters/instructions and is not an equivalence proof.
