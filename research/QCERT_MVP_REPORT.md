# Q-Cert Compiler Audit MVP Report

Generated on: 2026-06-13

Status: **mvp_report_not_live_device_claim**

Headline: Measurement-aware virtual-SWAP elimination produced replayable proof evidence on the current 30-circuit B1 suite.

## Customer Value

- Shows whether a routing/compiler change removes real two-qubit work or only shifts bookkeeping.
- Packages proof replay, Aer cross-checks, and limitation labels into one report.
- Creates a pilot-ready audit artifact before live calibrated hardware integration.

## B1 Virtual-SWAP Evidence

- Report status: virtual_swap_elimination_diagnostic_not_layout_final_claim
- Rewritten circuits: 30
- Virtual SWAPs removed: 481
- Removed CX gates: 1443
- Two-qubit reduction: 37.18%
- Exposure reduction: 32.65%
- Local Aer failures: 0
- End-to-end Aer failures: 0
- Top circuit: qasmbench_medium_exact/gcm_h6.qasm

## Proof Replay

- Status: passed
- Events replayed: 481 / 481
- Output mismatches: 0
- Errors: 0

## Synthetic Noise Proxy

- Status: synthetic_noise_proxy_not_calibrated_device_claim
- Profile: heavy_hex_like_sparse
- Source routed vs virtual-SWAP exposure reduction: 32.65%
- Success proxy ratio: 12748.386582112853

## B7 Resource Bridge Signal

- Status: dependency_schedule_bridge_not_physical_layout
- Comparisons: 6
- Minimum STV reduction: 1.1948051948051948
- Mean STV reduction: 1.353572610789181

## Certificate Gate Summary

- Status: evidence_package_not_final_claim
- Exact circuit count: 30
- Exact equivalence failures: 0
- Proof-log verification passed: True
- Global equivalence scope passed: False
- Calibrated heavy-hex baseline passed: False
- Unsupported claim count: 4

## Limitations

- This is a topology/layout and synthetic-noise diagnostic, not a calibrated hardware claim.
- Dynamic-circuit semantics and native-basis local optimization are not yet complete.
- The current CLI packages existing artifacts; it does not yet run customer circuits end to end.

## Next Customer Pilot Steps

- Accept a customer QASM bundle and hardware profile.
- Run baseline transpilation, virtual-SWAP audit, proof replay, and Aer cross-check.
- Emit a signed JSON/HTML audit report with unsupported-claim warnings.
