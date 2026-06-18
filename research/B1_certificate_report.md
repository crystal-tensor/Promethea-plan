# B1 Certificate Evidence Report v0.1

Last updated: 2026-06-13

Status: **evidence_package_not_final_claim**

## Supported Claim

The current pipeline can produce replayable local rewrite proof logs with semantic identity checks, exact statevector validation on a 30-circuit aggregate, and a 20.30% heavy-hex-like exposure reduction on one large interaction stress circuit.

## Claims Not Yet Supported

- No global exact equivalence proof for the hhl_n10 stress run.
- No routing-aware calibrated heavy-hex baseline has been added yet; the current validated Qiskit baseline is all-to-all u3/cx, while line-routing and heavy-hex topology results are diagnostic-only.
- No MQT Bench subset has been added yet; the new 12-circuit extension is generated and must be paired with more external benchmarks.
- The 30-circuit aggregate heavy-hex-like exposure reduction is 12.58%, below the 20% portfolio target.

## Proof-Log Results

| Result | Circuits | Equivalence | Audit | Replay | Semantic | Proof events | Exposure reduction |
|---|---:|---|---:|---:|---:|---:|---:|
| qasmbench_small_fixed_point_pipeline_with_proof_logs_v0 | 10 | 10 pass / 0 fail | True | True | True | 191 | 9.26% |
| b1_exact_extension_fixed_point_pipeline_v0 | 12 | 12 pass / 0 fail | True | True | True | 91 | 22.28% |
| qasmbench_interaction_stress_hhl_n10_with_proof_logs_v0 | 1 | skipped | True | True | True | 31173 | 20.30% |

## Exact-Checked Aggregate

- Circuits: 30
- Equivalence failures: 0
- Operation-count reduction: 34.17%
- Two-qubit-gate reduction: 10.72%
- Logical-depth reduction: 34.98%
- Heavy-hex-like exposure reduction: 12.58%

| Subset | Circuits | Max qubits | Equivalence failures | Exposure reduction |
|---|---:|---:|---:|---:|
| qasmbench_small | 10 | 7 | 0 | 9.26% |
| qasmbench_medium_exact | 6 | 15 | 0 | 7.70% |
| qasmbench_interaction_exact | 2 | 10 | 0 | 19.13% |
| b1_exact_extension_fixed_point | 12 | 10 | 0 | 22.28% |

## Gate Status

| Gate | Current | Passed |
|---|---|---:|
| minimum_circuit_count | 30 | True |
| exact_equivalence_failures | 0 | True |
| stress_hardware_exposure_reduction | 20.30% | True |
| aggregate_hardware_exposure_reduction | 12.58% | False |
| proof_log_verification | 3 proof-log runs passed audit/replay/semantic checks | True |
| ablation_table | present | True |
| baseline_comparison | present | True |
| routing_diagnostic | diagnostic_only_not_validated_baseline | True |
| routing_aware_calibrated_heavy_hex_baseline | heavy-hex topology diagnostic exists; no calibrated noise/device baseline | False |
| heavyhex_topology_diagnostic | device_like_topology_diagnostic_not_calibrated_noise_baseline | True |
| heavyhex_end_to_end_routed_benefit | topology_routed_benefit_suite_not_calibrated_noise_claim | True |
| post_routing_bottleneck_profile | post_routing_bottleneck_profile_diagnostic_not_calibrated_noise_claim | True |
| post_routing_swap_macro_compression | post_routing_swap_macro_diagnostic_not_native_basis_claim | True |
| virtual_swap_elimination | virtual_swap_elimination_diagnostic_not_layout_final_claim | True |
| virtual_swap_proof_replay | passed | True |
| synthetic_heavyhex_noise_proxy | synthetic_noise_proxy_not_calibrated_device_claim | True |
| global_equivalence_scope | exact for small/medium/interaction aggregate; skipped for hhl_n10 stress | False |

## Ablation Summary

- Report exists: True
- Report path: `research/B1_ablation_report.json`
- Largest hardware-exposure contributor: `after_adjacent_rzz`
- Largest depth contributor: `after_1q_resynthesis`

## Baseline Comparison Summary

- Report exists: True
- Report path: `research/B1_baseline_comparison.json`
- Best exact-valid Qiskit level by exposure: `1`
- B1 exposure delta versus best valid Qiskit: 25.94%
- Invalid Qiskit levels: [3]

## Routing Diagnostic Summary

- Report exists: True
- Report path: `research/B1_routing_baseline_diagnostic.json`
- Status: `diagnostic_only_not_validated_baseline`
- Full exact-valid baseline: False
- Full measurement-distribution-valid baseline: True
- Partial measurement-distribution levels: [0, 1, 3]
- Common measurement-distribution failure: []
- Aer cross-check all passed: True
- Aer cross-check total pairs: 90
- Aer cross-check max TVD: 0.04984
- Best diagnostic exposure reduction: -31.86%

## Heavy-Hex Topology Diagnostic Summary

- Report exists: True
- Report path: `research/B1_heavyhex_routing_diagnostic.json`
- Status: `device_like_topology_diagnostic_not_calibrated_noise_baseline`
- Distance: 3
- Physical qubits: 19
- Aer cross-check all passed: True
- Aer-valid levels: [0]
- Best diagnostic exposure reduction: -164.71%

## Heavy-Hex End-to-End Routed Benefit

- Report exists: True
- Report path: `research/B1_heavyhex_end_to_end_report.json`
- Status: `topology_routed_benefit_diagnostic_not_calibrated_noise_claim`
- Aer cross-check pass/fail: 30 / 0
- Operation-count reduction after routing: 16.95%
- Two-qubit-gate reduction after routing: 0.00%
- Logical-depth reduction after routing: 19.44%
- Heavy-hex-like exposure reduction after routing: 2.93%
- Idle-layer proxy reduction after routing: 20.55%
- Suite report exists: True
- Suite levels tested: [0, 1]
- Suite all Aer cross-checks passed: True
- Suite best level by exposure: 0
- Suite best exposure reduction: 2.93%

## Post-Routing Bottleneck Profile

- Report exists: True
- Report path: `research/B1_post_routing_bottleneck_profile.json`
- Status: `post_routing_bottleneck_profile_diagnostic_not_calibrated_noise_claim`
- Levels tested: [0, 1]
- All Aer cross-checks passed: True
- Level 0 exposure reduction: 2.93%
- Level 1 exposure reduction: 0.00%
- Circuits with level-1 benefit erasure: 16
- Top level-1 2Q bottleneck: `qasmbench_medium_exact/gcm_h6.qasm`

## Post-Routing SWAP Macro Diagnostic

- Report exists: True
- Report path: `research/B1_post_routing_swap_macro_report.json`
- Status: `post_routing_swap_macro_diagnostic_not_native_basis_claim`
- SWAP macros: 481
- Removed CX gates: 1443
- 2Q macro reduction: 24.79%
- Exposure reduction under macro cost model: 21.66%
- Local Aer failures: 0
- End-to-end Aer failures: 0
- Top SWAP macro circuit: `qasmbench_medium_exact/gcm_h6.qasm`

## Virtual SWAP Elimination Diagnostic

- Report exists: True
- Report path: `research/B1_virtual_swap_elimination_report.json`
- Status: `virtual_swap_elimination_diagnostic_not_layout_final_claim`
- Rewritten circuits: 30
- Skipped circuits: 0
- Virtual SWAPs removed: 481
- Removed CX gates: 1443
- 2Q reduction: 37.18%
- Exposure reduction: 32.65%
- Local Aer failures: 0
- End-to-end Aer failures: 0
- Proof replay status: passed
- Proof replay events: 481 / 481
- Proof replay output mismatches: 0
- Proof replay errors: 0
- Top virtual-SWAP circuit: `qasmbench_medium_exact/gcm_h6.qasm`

## Synthetic Heavy-Hex Noise Proxy

- Report exists: True
- Report path: `research/B1_synthetic_noise_proxy_report.json`
- Status: `synthetic_noise_proxy_not_calibrated_device_claim`
- Profile: `heavy_hex_like_sparse`
- Best comparison: `source_level1_routed_vs_virtual_swap`
- Source routed vs virtual-SWAP exposure reduction: 32.65%
- Source routed vs virtual-SWAP success proxy ratio: 12748.39x

## Next Technical Steps

- Add external exact-checkable circuits, especially MQT Bench or additional QASMBench families.
- Promote the line-routing diagnostic into a richer routing verifier, then add a calibrated heavy-hex transpiler baseline comparison.
- Implement a scalable equivalence strategy for stress circuits.
- Raise 30-circuit aggregate heavy-hex-like exposure reduction toward the 20% target.
- Extend virtual SWAP elimination to dynamic circuits with classical control/reset, independently verify wire-permutation certificates, and integrate it into a native-basis-aware 2-4 qubit routing optimizer.
- Connect B1 compressed circuits to B7 resource estimation.
