# Portfolio Status Report

Last updated: 2026-07-14

Overall audit: PASS

## Portfolio Inventory

- 100-problem catalog count: 100
- Catalog IDs contiguous 1..100: True
- Catalog metadata matrix count: 100
- Catalog metadata complete: True
- Catalog JSON status/freeze lock: frozen / True
- Catalog discipline/source groups: 9 / 4
- Catalog non-revision covenant present: True
- Top 20 evidence matches scoring: True
- Top 10 attack pack matches Tier 1: True
- Top 10 execution board directions: 10
- Top 10 execution board matches attack pack: True
- Top 10 problem dossiers: 10
- Top 10 problem dossiers complete: True
- Technical resolution directions: 10
- Technical resolution criterion: technical_resolution_before_publication_patent_financing_or_productization
- Translation pipeline status: deferred_until_b1_b10_technical_gates_pass

## Top 10 Attack IDs

25, 22, 49, 16, 38, 37, 21, 30, 17, 11

## Top 10 Execution Board

- Exists: True
- B IDs are B1..B10: True
- Lanes: {'coupled_application': ['B3', 'B5', 'B6'], 'technical_system_spine': ['B1', 'B2', 'B7'], 'theory_and_negative_results': ['B9', 'B10'], 'verification_protocol': ['B4', 'B8']}

## Top 10 Problem Dossiers

- JSON exists: True
- Markdown exists: True
- B IDs are B1..B10: True
- Problem IDs match attack pack: True
- All required fields present: True
- Maturity scores: {'B1': 63, 'B2': 48, 'B3': 28, 'B4': 29, 'B5': 30, 'B6': 24, 'B7': 59, 'B8': 41, 'B9': 15, 'B10': 53}

## Technical Resolution Program

- JSON exists: True
- Markdown exists: True
- B IDs are B1..B10: True
- All required fields present: True
- Current success criterion: technical_resolution_before_publication_patent_financing_or_productization

## Translation Pipeline

- JSON exists: True
- Markdown exists: True
- Status: deferred_until_b1_b10_technical_gates_pass
- Manuscripts/preprints: 5
- Patent disclosures: 5
- Fundable projects: 4
- Monetizable tools: 4
- Lead tool identified: True
- Declared targets met: True

## B1 Verification Status

| Result | Audit | Replay | Semantic | Proof events | Exposure reduction |
|---|---:|---:|---:|---:|---:|
| qasmbench_small_fixed_point_pipeline_with_proof_logs_v0 | True | True | True | 191 | 9.26% |
| b1_exact_extension_fixed_point_pipeline_v0 | True | True | True | 91 | 22.28% |
| qasmbench_interaction_stress_hhl_n10_with_proof_logs_v0 | True | True | True | 31173 | 20.30% |

## B1 Certificate Evidence Report

- Exists: True
- Status: evidence_package_not_final_claim
- Proof-log result rows: 3
- Exact circuit count: 30
- Exact equivalence failures: 0
- Proof-log verification passed: True
- Minimum circuit-count gate passed: True
- Aggregate exposure-reduction gate passed: False
- Ablation table gate passed: True
- Baseline comparison gate passed: True
- Routing diagnostic gate passed: True
- Calibrated heavy-hex routing baseline passed: False
- Heavy-hex topology diagnostic passed: True
- Heavy-hex end-to-end routed benefit passed: True
- Post-routing bottleneck profile passed: True
- Post-routing SWAP macro compression passed: True
- Virtual SWAP elimination passed: True
- Global equivalence scope gate passed: False
- Unsupported claim count: 4

## B1 Routing Diagnostic

- Exists: True
- Status: diagnostic_only_not_validated_baseline
- Full exact-valid baseline: False
- Full measurement-distribution-valid baseline: True
- Partial measurement-distribution levels: [0, 1, 3]
- Common measurement-distribution failures: []
- Aer cross-check all passed: True
- Aer cross-check total pairs: 90
- Aer cross-check max TVD: 0.049835205078125
- Best diagnostic exposure reduction: -31.86174843939919

## B1 Heavy-Hex Topology Diagnostic

- Exists: True
- Status: device_like_topology_diagnostic_not_calibrated_noise_baseline
- Distance: 3
- Physical qubits: 19
- Aer cross-check all passed: True
- Aer-valid levels: [0]
- Best diagnostic exposure reduction: -164.70733116017078

## B1 Heavy-Hex End-to-End Routed Benefit

- Exists: True
- Status: topology_routed_benefit_diagnostic_not_calibrated_noise_claim
- Aer cross-check pass/fail: 30 / 0
- Operation-count reduction after routing: 16.95001700102006
- Two-qubit reduction after routing: 0.0
- Logical-depth reduction after routing: 19.43796943796944
- Exposure reduction after routing: 2.931851434871905
- Suite exists: True
- Suite levels tested: [0, 1]
- Suite all Aer cross-checks passed: True
- Suite best exposure reduction: 2.931851434871905

## B1 Post-Routing Bottleneck Profile

- Exists: True
- Status: post_routing_bottleneck_profile_diagnostic_not_calibrated_noise_claim
- Levels tested: [0, 1]
- All Aer cross-checks passed: True
- Level 0 exposure reduction: 2.9318514348718887
- Level 1 exposure reduction: 0.00041445279796741913
- Benefit-erased circuits: 16
- Top level-1 2Q bottleneck: qasmbench_medium_exact/gcm_h6.qasm

## B1 Post-Routing SWAP Macro Diagnostic

- Exists: True
- Status: post_routing_swap_macro_diagnostic_not_native_basis_claim
- SWAP macros: 481
- Removed CX gates: 1443
- 2Q macro reduction: 24.78742592115434
- Exposure reduction under macro cost model: 21.661741565505224
- Local Aer failures: 0
- End-to-end Aer failures: 0
- Top SWAP macro circuit: qasmbench_medium_exact/gcm_h6.qasm

## B1 Virtual SWAP Elimination

- Exists: True
- Status: virtual_swap_elimination_diagnostic_not_layout_final_claim
- Rewritten circuits: 30
- Skipped circuits: 0
- Virtual SWAPs removed: 481
- Removed CX gates: 1443
- 2Q reduction: 37.18113888173151
- Exposure reduction: 32.64879262492005
- Local Aer failures: 0
- End-to-end Aer failures: 0
- Proof replay status: passed
- Proof replay events: 481 / 481
- Proof replay output mismatches: 0
- Proof replay errors: 0
- Top virtual-SWAP circuit: qasmbench_medium_exact/gcm_h6.qasm

## B1 Post-Virtual-SWAP 1Q Resynthesis

- Exists: True
- Status: post_virtual_swap_1q_resynthesis_t_resource_positive_diagnostic
- Rewritten circuits: 30
- Resynthesized 1Q runs: 60
- Removed 1Q gates: 60
- Certificate events: 60
- Logical T-count proxy reduction: 1.0178041543026706
- Logical T-depth proxy reduction: 1.0148367952522255
- Non-Clifford rotation reduction: 1.0178041543026706
- Aer failures: 0
- Aer pairs: 30
- Aer max TVD: 0.0

## B1 Native T-Resource Optimizer

- Exists: True
- Status: native_t_resource_optimizer_positive_diagnostic_not_final_claim
- Rewritten circuits: 30
- Circuits changed: 26
- Canonicalization events: 1691
- Identity events: 4
- Native RZ rewrite events: 1687
- Removed 1Q gates: 4
- Certificate events: 1691
- Logical T-count proxy reduction: 1.000990099009901
- Logical T-depth proxy reduction: 1.0
- Non-Clifford rotation reduction: 1.000990099009901
- Aer failures: 0
- Aer pairs: 30
- Aer max TVD: 0.0

## B1 Control-RZ Commute Optimizer

- Exists: True
- Status: control_rz_commute_positive_diagnostic_not_final_claim
- Rewritten circuits: 30
- Circuits changed: 16
- Absorbed RZ gates: 1687
- Certificate events: 1307
- Merged or moved groups: 183
- Removed RZ gates: 380
- CNOT-control commutations: 1172
- Logical T-count proxy reduction: 1.1193202807536018
- Logical T-depth proxy reduction: 1.0698412698412698
- Non-Clifford rotation reduction: 1.1193202807536018
- Aer failures: 0
- Aer pairs: 30
- Aer max TVD: 0.0

## B1 U3 Phase-Factored Optimizer

- Exists: True
- Status: u3_phase_factored_positive_diagnostic_not_final_claim
- Rewritten circuits: 30
- Circuits changed: 30
- U3 factorization events: 1641
- RZ components emitted: 2219
- RY components emitted: 1641
- Zero components removed: 1063
- Factorization certificate events: 1641
- RZ commute certificate events: 3242
- Removed RZ gates: 313
- CNOT-control commutations: 540
- Logical T-count proxy reduction: 1.0363705972434916
- Logical T-depth proxy reduction: 1.0277324632952691
- Non-Clifford rotation reduction: 1.0363705972434916
- Aer failures: 0
- Aer pairs: 30
- Aer max TVD: 0.0

## B1/B7 gcm_h6 Target Selector

- Exists: True
- Status: gcm_h6_target_selector_not_rewrite_or_resource_claim
- Arbitrary rotations / target removals / proxy-T target: 270 / 30 / 600
- Raw/canonical unique numeric parameters: 26 / 17
- Top angle / cone occurrences: 48 / 45
- Cone/angle/qubit classes meeting target: 3 / 2 / 4
- Rewrite/resource/semantic claims: False / False / False
- Validation errors: 0

## B1/B7 gcm_h6 Cone Feasibility Gate

- Exists: True
- Status: cone_feasibility_gate_candidate_windows_not_rewrite
- Target cone classes / total occurrences: 3 / 111
- Strict direct sandwiches / pair-local windows / pair-local single-arb windows: 4 / 106 / 86
- Cone classes meeting target by pair-local single windows: 1
- Leading feasible cone / windows / direct sandwiches: cone_01 / 35 / 1
- Rewrite/resource/semantic claims: False / False / False
- Validation errors: 0

## B1/B7 cone_01 Phase-Removal Gate

- Exists: True
- Status: cone01_phase_removal_restricted_negative_gate
- Target cone / candidate windows / required windows: cone_01 / 35 / 30
- Remove-only / fixed-phase / continuous-RZ exact passes: 0 / 0 / 0
- Best / median continuous-RZ residual: 0.36435162331705345 / 0.41976650460733583
- Best fixed-phase residual: 0.36435162331705345
- Restricted gate clears B7 target: False
- Rewrite/resource/semantic/obstruction claims: False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Euler-Reabsorption Gate

- Exists: True
- Status: cone01_euler_reabsorption_restricted_negative_gate
- Target cone / candidate windows / required windows: cone_01 / 35 / 30
- Exact RY candidates / optimizer seeds: 9 / 8
- Fixed-RY plus RZ-reabsorption exact passes: 0
- Best / median residual: 0.21253656711362606 / 0.3643516233170531
- Editable RZ parameter range: 0 - 2
- Restricted gate clears B7 target: False
- Rewrite/resource/semantic/obstruction claims: False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Parameter-Transfer Gate

- Exists: True
- Status: cone01_parameter_transfer_obligation_gate
- Target cone / candidate windows / required windows: cone_01 / 35 / 30
- Nonzero/zero parameter-sensitivity windows: 35 / 0
- Near pi/4-grid windows: 0
- Distinct theta / largest group / repeated occurrences: 4 / 16 / 35
- Minimum parameter-carrier obligation: 30
- Deletion without parameter carrier clears B7 target: False
- Rewrite/resource/semantic/obstruction claims: False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Local-Invariant Obligation Gate

- Exists: True
- Status: cone01_local_invariant_obligation_not_rewrite_certificate
- Target cone / candidate windows / required windows: cone_01 / 35 / 30
- Fingerprint: magic_basis_det_normalized_trace_m_m2
- Local-equivalence sensitive / flat windows: 24 / 11
- Nearest-grid invariant mismatch / match windows: 24 / 11
- Local-only absorption blocked / clears B7 target: 24 / False
- Invariant derivative min / median / max: 0.0 / 0.7128046122151909 / 2.006347280726594
- Nearest-grid invariant distance min / median / max: 0.0 / 0.13555913939041783 / 0.6976885899513073
- Rewrite/resource/semantic/KAK/obstruction claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Invariant-Flat Residual Gate

- Exists: True
- Status: cone01_invariant_flat_residual_obligation_not_rewrite_certificate
- Candidate / sensitive / invariant-flat windows: 35 / 24 / 11
- Flat theta groups / flat pattern groups / largest theta group: 3 / 3 / 8
- Shared flat-window partner / partner counts: True / {'14': 11}
- Max occurrence/proxy-T reduction if all flat windows are solved: 11 / 220
- All flat windows solved clears B7 target: False
- Missing occurrences/proxy-T after all flat windows are solved: 19 / 380
- Residual packets / pattern groups: 11 / 3
- Rewrite/resource/semantic/KAK/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Flat-Pattern KAK Packet

- Exists: True
- Status: cone01_flat_pattern_kak_packet_not_rewrite_certificate
- Pattern groups / covered occurrences: 3 / 11
- Unique nonlocal fingerprints / nearest-grid matches: 1 / 3
- Same-envelope grid exact passes / local-dressing obligations: 0 / 3
- Best/max same-envelope grid residual: 0.21253656711362615 / 0.3643516233170534
- All patterns solved clears B7 target: False
- Missing occurrences/proxy-T after all patterns are solved: 19 / 380
- Rewrite/semantic/KAK/resource/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Local-Dressing Search Gate

- Exists: True
- Status: cone01_local_dressing_search_not_resource_certificate
- Pattern groups / covered occurrences: 3 / 11
- Local-dressing exact passes / max residual: 3 / 4.710277376051325e-16
- Max off-grid dressing parameters: 9
- Accepted occurrence/proxy-T reduction: 0 / 0
- Missing occurrences/proxy-T after gate: 30 / 600
- Rewrite/semantic/KAK/resource/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Dressing Absorption Gate

- Exists: True
- Status: cone01_dressing_absorption_negative_gate
- Pattern groups / covered occurrences: 3 / 11
- Source local-dressing exact passes / pi-over-four projection exact passes: 3 / 0
- Projected residual min/max: 0.3000426259967881 / 0.8415525963596902
- Unique grid signatures / shared signature flag: 3 / False
- Off-grid / near-grid / far-off-grid local dressing parameters: 26 / 2 / 24
- Single-parameter snap exact passes: 0
- Accepted occurrence/proxy-T reduction: 0 / 0
- Missing occurrences/proxy-T after gate: 30 / 600
- Absorption/exactification/shared-dressing/rewrite/semantic/resource/B7-ledger claims: False / False / False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Local Clifford Dressing Gate

- Exists: True
- Status: cone01_local_clifford_dressing_negative_gate
- Clifford sizes: 24 one-qubit / 576 pair-local
- Left/right pair trials per pattern: 331776
- Pattern groups / covered occurrences: 3 / 11
- Local Clifford exact packet count / all-packets flag: 0 / False
- Best/max best local-Clifford residual: 0.2125365671136259 / 0.3643516233170526
- Accepted occurrence/proxy-T reduction: 0 / 0
- Missing occurrences/proxy-T after gate: 30 / 600
- Local-Clifford/rewrite/semantic/resource/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Single-Carrier Local Dressing Gate

- Exists: True
- Status: cone01_single_carrier_exact_packet_not_resource_certificate
- Carrier sources / coefficients / axes / local roles / sides: 2 / 6 / 3 / 2 / 2
- Pattern groups / covered occurrences: 3 / 11
- Total single-carrier trials: 143327232
- Single-carrier exact packet count / all-packets flag: 3 / True
- Best/max best single-carrier residual: 3.2009291313835888e-16 / 4.677452743560217e-16
- Accepted occurrence/proxy-T reduction: 0 / 0
- Missing occurrences/proxy-T after gate: 30 / 600
- Exact-packet/resource-certificate/rewrite/semantic/resource/B7-ledger claims: True / False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Single-Carrier Ledger Pressure Gate

- Exists: True
- Status: cone01_single_carrier_ledger_pressure_not_accepted_reduction
- Source exact packets / pattern groups / covered occurrences: 3 / 3 / 11
- Unique carrier signatures / all best carriers target-X: 3 / True
- Per-occurrence carrier insertions / net arbitrary occurrence delta: 11 / 0
- Optimistic carrier templates / duplicate occurrences / proxy-T reuse: 3 / 8 / 160
- Max removal if all carriers absorbed / clears B7 target / still-missing occurrences: 11 / False / 19
- Accepted occurrence/proxy-T reduction: 0 / 0
- Carrier-ledger/rewrite/semantic/resource/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Single-Carrier Shareability Gate

- Exists: True
- Status: cone01_single_carrier_shareability_negative_gate
- Source exact packets / carrier signatures / covered occurrences: 3 / 3 / 11
- Shareable objects / cross-pattern signatures / largest signature occurrences: 3 / 0 / 8
- One-signature / relaxed-source-axis-role shareability: False / False
- Optimistic shared objects / duplicate occurrences / proxy-T reuse: 3 / 8 / 160
- Optimistic shareability clears target: False
- Max accepted-all removal / clears B7 target / still-missing occurrences: 11 / False / 19
- Accepted occurrence/proxy-T reduction: 0 / 0
- Shareability/ledger/rewrite/semantic/resource/B7 claims: False / False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Carrier Absorption Inventory Gate

- Exists: True
- Status: cone01_carrier_absorption_inventory_negative_gate
- Inventory QASM / rotation arguments: results/b1_native_t_resource_optimizer/qasmbench_medium_exact/gcm_h6.qasm / 2049
- Pattern groups / covered occurrences / carrier signatures: 3 / 11 / 3
- Inventory / same-target / line-local candidate patterns: 2 / 2 / 0
- Patterns without inventory / same-target match: ['flat_pattern_02'] / ['flat_pattern_02']
- All-pattern inventory / same-target / line-local coverage: False / False / False
- Accepted certificates / occurrence / proxy-T reduction: 0 / 0 / 0
- Absorption/ledger/rewrite/semantic/resource/B7 claims: False / False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Carrier Neighborhood Commutation Gate

- Exists: True
- Status: cone01_carrier_neighborhood_commutation_negative_gate
- Inventory QASM: results/b1_native_t_resource_optimizer/qasmbench_medium_exact/gcm_h6.qasm
- Pattern groups / covered occurrences / carrier signatures: 3 / 11 / 3
- Same-target / radius-4 / radius-8 / radius-16 candidate patterns: 2 / 0 / 1 / 1
- Blocker-free radius-16 candidate patterns: 1
- Patterns without same-target / radius-16 / blocker-free radius-16 candidates: ['flat_pattern_02'] / ['flat_pattern_02', 'flat_pattern_03'] / ['flat_pattern_02', 'flat_pattern_03']
- All-pattern radius-16 / blocker-free radius-16 coverage: False / False
- Accepted certificates / occurrence / proxy-T reduction: 0 / 0 / 0
- Neighborhood/commutation/ledger/rewrite/semantic/resource/B7 claims: False / False / False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Carrier Source Alignment Gate

- Exists: True
- Status: cone01_carrier_source_alignment_negative_gate
- Reviewed / blocker-free radius-16 candidates: 5 / 1
- Source-aligned / blocker-free source-aligned candidates: 3 / 0
- Patterns with reviewed / blocker-free / source-aligned / accepted joint candidates: ['flat_pattern_01'] / ['flat_pattern_01'] / ['flat_pattern_01'] / []
- Accepted source-alignment certificates / occurrence / proxy-T reduction: 0 / 0 / 0
- Alignment/commutation/rewrite/semantic/resource/B7 claims: False / False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Carrier Blocker Stack Gate

- Exists: True
- Status: cone01_carrier_blocker_stack_negative_gate
- Source-aligned / blocked candidates: 3 / 3
- Target CNOT blockers / candidate-qubit blockers / other target blockers: 15 / 14 / 1
- Unique blocker lines / edge signatures: 11 / ['10-14', '2-14', '4-8']
- Accepted blocker-clearance certificates / occurrence / proxy-T reduction: 0 / 0 / 0
- Blocker/commutation/rewrite/semantic/resource/B7 claims: False / False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Carrier Blocker Motif Gate

- Exists: True
- Status: cone01_carrier_blocker_motif_negative_gate
- Motif candidates / exact motifs / edge-family motifs: 3 / 3 / 2
- Largest exact / edge-family candidate group: 1 / 2
- Single-edge / mixed-edge candidates: 2 / 1
- All share exact / all share edge-family / cross-pattern motif / template gate: False / False / False / False
- Accepted template motifs / occurrence / proxy-T reduction: 0 / 0 / 0
- Template/semantic/rewrite/resource/B7 claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Carrier Blocker CNOT Parity Gate

- Exists: True
- Status: cone01_carrier_blocker_parity_negative_gate
- Parity candidates / CNOT-only parity identity / odd parity candidates: 3 / 1 / 2
- Repeated same-edge pairs / clean cancel pairs: 11 / 0
- Target single-qubit interleavings / parity-identity but interleaved candidates: 18 / 1
- Parity gate passed / accepted occurrence / proxy-T reduction: False / 0 / 0
- CNOT-parity/semantic/rewrite/resource/B7 claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Carrier Interleaving Commutation Gate

- Exists: True
- Status: cone01_carrier_interleaving_commutation_negative_gate
- Candidates / interleaving ops / unique lines: 3 / 18 / 13
- Cheap control phases / target-side phase obstructions / non-diagonal obstructions: 7 / 4 / 7
- Candidates with non-diagonal interleavings / accepted commutation clearances: 3 / 0
- Interleaving gate passed / accepted occurrence / proxy-T reduction: False / 0 / 0
- Commutation/semantic/rewrite/resource/B7 claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Semantic Replay Packet Gate

- Exists: True
- Status: cone01_semantic_replay_packet_constructed_not_solved
- Replay packets / two-qubit packets / support range: 3 / 3 / 2-2
- Window gates / CNOT / 1Q gates: 32 / 14 / 18
- Unique semantic fingerprints / exact matrix targets: 3 / True
- Targets constructed / certificate / rewrite / resource / B7 claims: True / False / False / False / False
- Accepted occurrence / proxy-T reduction: 0 / 0
- Validation errors: 0

## B1/B7 cone_01 Packet Synthesis Search Gate

- Exists: True
- Status: cone01_packet_synthesis_search_candidate_not_replay_certificate
- Packets / scaffolds searched / seeds per scaffold: 3 / 12 / 10
- Exact reduced-scaffold packets / min exact CNOT count / candidate CNOT reduction: 3 / 1 / 9
- Candidate found / accepted replay certificates: True / 0
- Candidate-as-saving / semantic / rewrite / resource / B7 claims: False / False / False / False / False
- Accepted occurrence / proxy-T reduction: 0 / 0
- Validation errors: 0

## B1/B7 cone_01 Packet Replay Resource Gate

- Exists: True
- Status: cone01_packet_replay_resource_accounting_rejects_ledger_acceptance
- Bounded packet replay count / candidate CNOT reduction: 3 / 9
- Source off-grid params / replacement local U3 gates / replacement off-grid params: 1 / 16 / 40
- Incremental proxy-T pressure / local-U3 burden packets: 780 / 3
- Accepted full-circuit replay / occurrence / proxy-T reduction: 0 / 0 / 0
- Candidate accepted after accounting / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Local-U3 Exactification Gate

- Exists: True
- Status: cone01_local_u3_exactification_negative_gate
- Snap packets / exact passes / exact fails: 3 / 0 / 3
- Snapped residual range: 0.47574352650518004 - 0.7803612880646379
- Replacement off-grid params / projected off-grid params / residual burden params: 40 / 40 / 40
- Accepted exactification / absorption / full-circuit replay: 0 / 0 / 0
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Sparse Local-U3 Repair Gate

- Exists: True
- Status: cone01_sparse_local_u3_repair_partial_not_ledger_accepted
- Sparse candidates / max free parameters: 420 / 2
- One-param exact / <=2-param exact / unresolved packets: 1 / 1 / 2
- All-packet candidate CNOT reduction / partial candidate CNOT reduction: 9 / 3
- Replacement off-grid params / exact-repair off-grid params / unrepaired off-grid params: 40 / 0 / 30
- Accepted rewrite / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Three-Parameter Local-U3 Repair Gate

- Exists: True
- Status: cone01_three_parameter_local_u3_repair_partial_not_ledger_accepted
- Three-parameter candidates / exact packets / unresolved packets: 1632 / 1 / 1
- Total exact packets after gate / total unresolved after gate: 2 / 1
- All-packet candidate CNOT reduction / partial candidate CNOT reduction: 9 / 6
- Remaining unrepaired off-grid params / exact-repair off-grid params: 15 / 0
- Accepted rewrite / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Four-Parameter Line-1381 Repair Pressure Gate

- Exists: True
- Status: cone01_four_parameter_line1381_pressure_no_exact_repair
- Four-parameter candidates / exact packets / unresolved packets: 3060 / 0 / 1
- Total exact packets after gate / total unresolved after gate: 2 / 1
- Best three-parameter residual / best four-parameter residual / improvement: 0.049865177666770955 / 0.02997767950993884 / 0.019887498156832113
- All-packet candidate CNOT reduction / partial candidate CNOT reduction: 9 / 6
- Accepted rewrite / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Five-Parameter Line-1381 Exact Repair Gate

- Exists: True
- Status: cone01_five_parameter_line1381_exact_packet_repair_not_ledger_accepted
- Five-parameter total combinations / searched until exact: 8568 / 5795
- Five-parameter exact packets / unresolved packets: 1 / 0
- Total exact packets after gate / total unresolved after gate: 3 / 0
- Best four-parameter residual / best five-parameter residual / improvement: 0.02997767950993884 / 6.513934436930801e-13 / 0.02997767950928745
- All-packet candidate CNOT reduction / partial candidate CNOT reduction: 9 / 9
- Exact repair off-grid params / accepted rewrite / occurrence / proxy-T reduction / B7 claim: 5 / 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Repaired Packet Resource Boundary Gate

- Exists: True
- Status: cone01_repaired_packet_resource_boundary_not_ledger_accepted
- Bounded exact repairs / packet count: 3 / 3
- Candidate CNOT reduction if all packets accepted: 9
- Source / original replacement / repaired off-grid params: 1 / 40 / 5
- Original / repaired incremental off-grid params: 39 / 4
- Original / repaired incremental proxy-T pressure: 780 / 80
- Off-grid/proxy-T reduction vs original candidate: 35 / 700
- Remaining off-grid repair packets / accepted full-circuit replay: 1 / 0
- Accepted occurrence/proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Exact-Decomposition Pressure Gate

- Exists: True
- Status: cone01_line1381_exact_decomposition_pressure_not_accepted
- Target line / remaining off-grid parameters: 1381 / 5
- Parameter indices: [3, 4, 9, 16, 17]
- Pi/4 / dyadic-pi / rational-pi exact parameters: 0 / 0 / 0
- Source-absorbed / accepted exact-decomposition parameters: 0 / 0
- Remaining unaccepted parameters: 5
- Min / max best rational-pi error: 9.065022593679473e-07 / 0.00027215955680759407
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Context Absorption Gate

- Exists: True
- Status: cone01_line1381_context_absorption_not_accepted
- Target line / support qubits: 1381 / [4, 8]
- Window / context radius: 1369-1379 / 64
- Full inventory / context rotation arguments: 2049 / 44
- Tested parameters / inventory abs matches / context abs matches: 5 / 0 / 0
- One-step context grid-cancellation exact parameters: 0
- Min / max best context grid-cancellation error: 0.0027465552120480297 / 0.09773822449711567
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Multi-Rotation Context Gate

- Exists: True
- Status: cone01_line1381_multi_rotation_context_not_accepted
- Target line / support qubits: 1381 / [4, 8]
- Window / context radius: 1369-1379 / 64
- Search widths / context rotation arguments: [2, 3] / 44
- Signed combinations per parameter, width 2 / width 3: 3784 / 105952
- Total signed combination tests: 548680
- Width-2 / width-3 exact absorption parameters: 0 / 0
- Min best width-2 / width-3 context grid error: 0.0027465552120480297 / 0.0015819911093339911
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Four-Rotation Context Gate

- Exists: True
- Status: cone01_line1381_four_rotation_context_not_accepted
- Target line / support qubits: 1381 / [4, 8]
- Window / context radius: 1369-1379 / 64
- Search width / context rotation arguments: 4 / 44
- Signed combinations per parameter / total tests: 2172016 / 10860080
- Width-4 exact absorption parameters: 0
- Min / max best width-4 context grid error: 0.0015819911093339911 / 0.026659551749408372
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Five-Rotation Context Gate

- Exists: True
- Status: cone01_line1381_five_rotation_context_not_accepted
- Target line / support qubits: 1381 / [4, 8]
- Window / context radius: 1369-1379 / 64
- Search width / MITM split / context rotation arguments: 5 / 2+3 / 44
- Signed combinations per parameter / virtual tests: 34752256 / 173761280
- Width-5 exact absorption parameters: 0
- Min / max best width-5 context grid error: 0.001581991109333103 / 0.026659551749407484
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Commutation Corridor Gate

- Exists: True
- Status: cone01_line1381_commutation_corridor_not_accepted
- Target line / support qubits: 1381 / [4, 8]
- Window: 1369-1379
- Best candidates / context references / unique context lines: 10 / 32 / 8
- Inside-packet / non-standalone / blocked references: 7 / 13 / 21
- Clear external standalone-Z references / all-reference accepted candidates: 0 / 0
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Route Triage Decision Gate

- Exists: True
- Status: cone01_route_triage_rejects_current_shortcuts_no_b7_credit
- Routes triaged / accepted / rejected: 5 / 0 / 5
- Failed resource blockers / width-5 exact absorptions / accepted corridor candidates: 5 / 0 / 0
- Theta accepted / refreshed B7 accepts theta / optimistic cache proxy-T: False / False / 620
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Recommended next route count / gates passed-failed: 4 / 6-0
- Validation errors: 0

## B1/B7 cone_01 Full-Circuit Replay Obligation Gate

- Exists: True
- Status: cone01_full_circuit_replay_obligations_not_satisfied
- Packets / bounded exact repairs: 3 / 3
- Resource-clean packets / unpriced off-grid packets: 2 / 1
- Symbolic exactness / replay events / QASM patches: 0 / 0 / 0
- Occurrence lift / B7 ledger acceptance / line-1381 context-or-pricing: 0 / 0 / 0
- Blocking obligations total/max: 17 / 7
- Candidate CNOT reduction if accepted: 9
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Bounded Replacement Patch Gate

- Exists: True
- Status: cone01_bounded_replacement_patches_not_composable_full_circuit
- Bounded QASM3 patches / exact-pass patches: 3 / 3
- Candidate CNOT reduction if accepted: 9
- Remaining off-grid parameters: 5
- Overlapping window pairs / composable patch set: 1 / False
- Accepted full-circuit patch / replay / occurrence / proxy-T reduction: 0 / 0 / 0 / 0
- B7 ledger improvement claimed: False
- Validation errors: 0

## B1/B7 cone_01 Non-Overlap Patch Subset Gate

- Exists: True
- Status: cone01_nonoverlap_bounded_patch_subset_not_full_circuit_replay
- Input patches / naive CNOT reduction: 3 / 9
- Selected lines / dropped lines: [268, 1381] / [1378]
- Selected CNOT reduction / lost overlap delta: 6 / 3
- Source dialect / dialect bridge required: OPENQASM 2.0 / True
- Full-circuit QASM rewrite emitted / accepted patch count: False / 0
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 QASM2 Candidate Rewrite Gate

- Exists: True
- Status: cone01_qasm2_candidate_rewrite_emitted_not_replay_certified
- Selected lines / dropped overlap lines: [268, 1381] / [1378]
- Source / candidate dialect: OPENQASM 2.0 / OPENQASM 2.0
- Candidate QASM emitted / path: True / results/B1_B7_cone01_qasm2_candidate_rewrite_gate/gcm_h6_line268_line1381_candidate.qasm
- Source / candidate CNOT count / delta: 795 / 789 / 6
- Replacement windows / QASM2 bridge patches: 2 / 2
- Accepted full-circuit patch / replay / occurrence / proxy-T reduction: 0 / 0 / 0 / 0
- B7 ledger improvement claimed: False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Candidate Export Gate

- Exists: True
- Status: cone01_openqasm3_candidate_exported_not_replay_certified
- Source / export dialect: OPENQASM 2.0 / OPENQASM 3.0
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Header / stdgates / operation counts preserved: True / True / True
- Legacy qelib/qreg/creg/u3/measure-arrow remnants: False / False / False / False
- u3->U conversions / measurement conversions: 487 / 1
- Candidate CNOT count / delta: 789 / 6
- Accepted export / replay / local-U3 pricing / occurrence / proxy-T reduction: 1 / 0 / 0 / 0 / 0
- B7 ledger improvement claimed: False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Parser-Readiness Gate

- Exists: True
- Status: cone01_openqasm3_local_parse_passed_qiskit_loader_dependency_missing
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Local parser passed / error count: True / 0
- Local operation counts: {'U': 487, 'cx': 789, 'measure': 1, 'other_operation': 0, 'rz': 601}
- Qubits / bits / statements / operation rows: 19 / 1 / 1884 / 1878
- Qiskit available / qiskit_qasm3_import available: True / False
- Qiskit loader attempted / passed / status: True / False / optional_dependency_missing
- Accepted local parse / Qiskit loader parse artifacts: 1 / 0
- Accepted replay / local-U3 pricing / occurrence / proxy-T reduction: 0 / 0 / 0 / 0
- B7 ledger improvement claimed: False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Structural Roundtrip Gate

- Exists: True
- Status: cone01_openqasm3_structural_roundtrip_matches_legacy_candidate
- QASM2 / OpenQASM 3 paths: results/B1_B7_cone01_qasm2_candidate_rewrite_gate/gcm_h6_line268_line1381_candidate.qasm / results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Normalized instruction counts QASM2 / OpenQASM 3 / selected: 1878 / 1878 / 1878
- Streams match / mismatch count / length delta: True / 0 / 0
- Operation counts: {'U': 487, 'cx': 789, 'measure': 1, 'rz': 601}
- Stream hash: 7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343
- Accepted structural roundtrip / Qiskit loader / replay / local-U3 pricing artifacts: 1 / 0 / 0 / 0
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Local Semantic Replay Gate

- Exists: True
- Status: cone01_openqasm3_local_semantic_replay_passed_default_input_only
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Project-local parser passed / error count: True / 0
- Operation counts: {'U': 487, 'cx': 789, 'measure': 1, 'rz': 601}
- Qubits / bits / statements / operation rows: 19 / 1 / 1884 / 1878
- Source / OpenQASM 3 CNOT count / delta: 795 / 789 / 6
- State fidelity / infidelity: 0.9999999999999551 / 4.4853010194856324e-14
- Max amplitude / probability / measured marginal delta: 1.3908205762322243e-13 / 5.551115123125783e-16 / 5.551115123125783e-16
- Accepted local replay / Qiskit loader / symbolic equivalence artifacts: 1 / 0 / 0
- Accepted replay certificate / local-U3 pricing / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Multi-Input Replay Gate

- Exists: True
- Status: cone01_openqasm3_multi_input_replay_pressure_passed_not_symbolic_certificate
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Project-local parser passed / error count: True / 0
- Input cases / failed cases: 8 / 0
- Basis / product-state inputs: 6 / 2
- Source / OpenQASM 3 CNOT count / delta: 795 / 789 / 6
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max amplitude / probability delta: 1.392888964263601e-13 / 1.8214596497756474e-15
- Multi-input replay passed / symbolic unitary claimed / arbitrary input claimed: True / False / False
- Accepted OpenQASM 3 multi-input replay / occurrence / proxy-T reduction / B7 claim: 1 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Phase-Consistent Replay Gate

- Exists: True
- Status: cone01_openqasm3_phase_consistent_replay_passed_not_symbolic_certificate
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Project-local parser passed / error count: True / 0
- Input cases / failed cases: 8 / 0
- Phase anchors / superposition inputs: 4 / 4
- Source / OpenQASM 3 CNOT count / delta: 795 / 789 / 6
- Phase spread / min overlap magnitude: 1.3722356584366935e-13 / 0.9999999999999772
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max amplitude / probability delta: 1.392888964263601e-13 / 1.074140776324839e-14
- Phase-consistent replay passed / symbolic unitary claimed / arbitrary input claimed: True / False / False
- Accepted OpenQASM 3 phase replay / occurrence / proxy-T reduction / B7 claim: 1 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Global-Phase Subspace Replay Gate

- Exists: True
- Status: cone01_openqasm3_global_phase_subspace_replay_passed_not_symbolic_certificate
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Project-local parser passed / error count: True / 0
- Input cases / failed cases: 21 / 0
- Basis anchors / coherent superpositions: 6 / 15
- Global phase anchor / radians: zero / -2.4388324596671658
- Source / OpenQASM 3 CNOT count / delta: 795 / 789 / 6
- Max anchor phase delta / min overlap magnitude: 3.142993331217661e-14 / 0.9999999999999772
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max anchored amplitude / probability delta: 1.3928889642636009e-13 / 1.074140776324839e-14
- Subspace replay passed / symbolic unitary claimed / arbitrary input claimed: True / False / False
- Accepted OpenQASM 3 anchored replay / occurrence / proxy-T reduction / B7 claim: 1 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Linear-Span Replay Certificate Gate

- Exists: True
- Status: cone01_openqasm3_linear_span_replay_certificate_passed_not_full_unitary
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Project-local parser passed / error count: True / 0
- Certified subspace / full space / fraction: 6 / 524288 / 1.1444091796875e-05
- Linear-span spectral / Frobenius norm: 2.7889440543898627e-13 / 6.134324404657074e-13
- Max basis L2 / amplitude / probability delta: 2.534056605707275e-13 / 1.3928889642636009e-13 / 7.771561172376096e-16
- Max source-candidate Gram / cross-Gram delta: 1.9984014443252818e-15 / 4.403624367368429e-14
- Coherent pair witnesses passed / count: True / 15
- Source / OpenQASM 3 CNOT count / delta: 795 / 789 / 6
- Accepted OpenQASM 3 linear-span / Qiskit loader / symbolic artifacts: 1 / 0 / 0
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Composable Patch Lift Gate

- Exists: True
- Status: cone01_openqasm3_composable_patch_lift_passed_without_b7_resource_credit
- QASM2 / OpenQASM 3 paths: results/B1_B7_cone01_qasm2_candidate_rewrite_gate/gcm_h6_line268_line1381_candidate.qasm / results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Normalized stream match / mismatches / length delta: True / 0 / 0
- Normalized instruction count / stream hash: 1878 / 7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343
- Selected patches / lines / dropped overlap lines: 2 / [268, 1381] / [1378]
- Non-overlap / local-unitary certificates / lift passed: True / True / True
- Max selected patch residual / entry error / OpenQASM 3 span spectral error: 6.513210005207597e-13 / 4.525273102184799e-13 / 2.7889440543898627e-13
- OpenQASM 3 finite-span certificate / subspace / full space: True / 6 / 524288
- Source / OpenQASM 3 CNOT count / delta: 795 / 789 / 6
- Accepted OpenQASM 3 patch lift / Qiskit loader / symbolic artifacts: 1 / 0 / 0
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Provenance Seal Gate

- Exists: True
- Status: cone01_openqasm3_provenance_seal_passed_without_b7_resource_credit
- QASM2 / OpenQASM 3 paths: results/B1_B7_cone01_qasm2_candidate_rewrite_gate/gcm_h6_line268_line1381_candidate.qasm / results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Raw QASM2 / OpenQASM 3 line counts: 1884 / 1884
- Normalized stream match / instruction count / hash: True / 1878 / 7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343
- Provenance seal hash: 159c9b1d99a607d463fe712a190b35460603712561a4ea8eb4033bf4de495902
- Selected lines / dropped overlap lines: [268, 1381] / [1378]
- Max selected patch residual / entry error / OpenQASM 3 span spectral error: 6.513210005207597e-13 / 4.525273102184799e-13 / 2.7889440543898627e-13
- Accepted provenance seal / Qiskit loader / symbolic artifacts: 1 / 0 / 0
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Source-Map Gate

- Exists: True
- Status: cone01_openqasm3_source_map_passed_without_b7_resource_credit
- QASM2 / OpenQASM 3 paths: results/B1_B7_cone01_qasm2_candidate_rewrite_gate/gcm_h6_line268_line1381_candidate.qasm / results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Raw QASM2 / OpenQASM 3 line counts: 1884 / 1884
- Normalized stream match / instruction count / hash: True / 1878 / 7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343
- Source-map rows / raw-line drift count / hash: 1878 / 0 / 92a499ea6d549426095fbb0fc878f7033027991621a6d5ea1c03cd25d82e9e1e
- Selected lines / dropped overlap lines: [268, 1381] / [1378]
- Patch instruction indices / operations: [263, 1375, 1372] / ['rz', 'U', 'U']
- Accepted source-map / Qiskit loader / symbolic artifacts: 1 / 0 / 0
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Patch Witness Packet Gate

- Exists: True
- Status: cone01_openqasm3_patch_witness_packet_passed_without_b7_resource_credit
- QASM2 / OpenQASM 3 paths: results/B1_B7_cone01_qasm2_candidate_rewrite_gate/gcm_h6_line268_line1381_candidate.qasm / results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Normalized instruction count / stream hash: 1878 / 7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343
- Source-map hash / raw-line drift count: 92a499ea6d549426095fbb0fc878f7033027991621a6d5ea1c03cd25d82e9e1e / 0
- Witness rows / selected / dropped-overlap: 3 / 2 / 1
- Witness candidate lines / instruction indices / OpenQASM 3 lines: [268, 1378, 1381] / [263, 1372, 1375] / [268, 1378, 1381]
- Witness packet hash: e0d2e63f3f2c16be685baef3360ff68d5765db549c5e17e655a6e74c6fb82dc8
- Selected CNOT delta / lost overlap delta: 6 / 3
- Max witness residual / entry error / off-grid selected local-U3 count: 9.049428032408627e-13 / 6.398911863522162e-13 / 5
- Accepted witness packet / Qiskit loader / symbolic artifacts: 1 / 0 / 0
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Replay Gate

- Exists: True
- Status: cone01_openqasm3_qiskit_loader_replay_passed_default_input_only
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Loader attempted / passed / replay passed: True / True / True
- Qubits / clbits / depth / operation counts: 19 / 1 / 1483 / {'cx': 789, 'measure': 1, 'rz': 601, 'u': 487}
- State fidelity / infidelity: 0.9999999999999551 / 4.4853010194856324e-14
- Max amplitude / probability / measured marginal delta: 1.3908205762322243e-13 / 5.551115123125783e-16 / 5.551115123125783e-16
- Accepted Qiskit-loader parse / replay / symbolic artifacts: 1 / 1 / 0
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Multi-Input Replay Gate

- Exists: True
- Status: cone01_openqasm3_qiskit_loader_multi_input_replay_passed_sampled_inputs
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Qubits / clbits / depth / operation counts: 19 / 1 / 1483 / {'cx': 789, 'measure': 1, 'rz': 601, 'u': 487}
- Input cases / failed cases: 8 / 0
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max amplitude / probability delta: 1.392888964263601e-13 / 1.8214596497756474e-15
- Accepted Qiskit-loader parse / replay / multi-input artifacts: 1 / 1 / 1
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Phase-Consistent Replay Gate

- Exists: True
- Status: cone01_openqasm3_qiskit_loader_phase_consistent_replay_passed
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Qubits / clbits / depth / operation counts: 19 / 1 / 1483 / {'cx': 789, 'measure': 1, 'rz': 601, 'u': 487}
- Input cases / failed cases: 8 / 0
- Overlap phase spread / min overlap magnitude: 1.3722356584366935e-13 / 0.9999999999999772
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max amplitude / probability delta: 1.392888964263601e-13 / 1.074140776324839e-14
- Accepted Qiskit-loader parse / replay / phase artifacts: 1 / 1 / 1
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Global-Phase Subspace Replay Gate

- Exists: True
- Status: cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_passed
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Qubits / clbits / depth / operation counts: 19 / 1 / 1483 / {'cx': 789, 'measure': 1, 'rz': 601, 'u': 487}
- Global phase anchor / input cases / failed cases: zero / 21 / 0
- Basis anchors / coherent superpositions: 6 / 15
- Max global-anchor phase delta / min overlap magnitude: 3.142993331217661e-14 / 0.9999999999999772
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max amplitude / probability delta: 1.3928889642636009e-13 / 1.074140776324839e-14
- Accepted Qiskit-loader parse / replay / phase / global-anchor artifacts: 1 / 1 / 1 / 1
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Linear-Span Replay Certificate Gate

- Exists: True
- Status: cone01_openqasm3_qiskit_loader_linear_span_replay_certificate_passed
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Qubits / clbits / depth / operation counts: 19 / 1 / 1483 / {'cx': 789, 'measure': 1, 'rz': 601, 'u': 487}
- Global phase anchor / certified subspace / full space: zero / 6 / 524288
- Linear-span spectral / Frobenius error: 2.7889440543898627e-13 / 6.134324404657074e-13
- Max basis L2 / amplitude / probability delta: 2.534056605707275e-13 / 1.3928889642636009e-13 / 7.771561172376096e-16
- Max source-candidate Gram / cross-Gram delta: 1.9984014443252818e-15 / 4.403624367368429e-14
- Source / Qiskit CNOT count / delta: 795 / 789 / 6
- Accepted Qiskit-loader parse / replay / global-anchor / linear-span artifacts: 1 / 1 / 1 / 1
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Composable Patch Lift Support Gate

- Exists: True
- Status: cone01_openqasm3_qiskit_loader_composable_patch_lift_supported_without_b7_credit
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Selected lines / dropped overlap lines: [268, 1381] / [1378]
- Nonoverlap / local-unitary certificates: True / True
- Qiskit global-phase / finite-span passed: True / True
- Qiskit span spectral / max basis L2 / max probability delta: 2.7889440543898627e-13 / 2.534056605707275e-13 / 7.771561172376096e-16
- Accepted parse / global-phase / linear-span / patch-lift support artifacts: 1 / 1 / 1 / 1
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Evidence Seal Gate

- Exists: True
- Status: cone01_openqasm3_qiskit_loader_evidence_seal_passed_without_b7_credit
- OpenQASM 3 path: results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm
- Source artifact count / seal hash: 7 / d06c1fdae3ad7cad1971cdcdcea1f890d3931924a7e70affc25fdf89737e09a8
- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Qubits / clbits / depth / operation counts: 19 / 1 / 1483 / {'cx': 789, 'measure': 1, 'rz': 601, 'u': 487}
- Default / multi / phase / global replay cases: True / 8 / 8 / 21
- Failed replay cases total: 0
- Global-phase / finite-span / patch-lift support passed: True / True / True
- Certified span / full space: 6 / 524288
- Span spectral / max basis L2 / max probability / max cross-Gram delta: 2.7889440543898627e-13 / 2.534056605707275e-13 / 7.771561172376096e-16 / 4.403624367368429e-14
- Selected lines / dropped overlap lines / stream mismatch: [268, 1381] / [1378] / 0
- Accepted evidence seal / occurrence / proxy-T reduction / B7 claim: 1 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Evidence Seal Reproduction Gate

- Exists: True
- Status: cone01_openqasm3_qiskit_loader_evidence_seal_reproduced_without_b7_credit
- Input evidence-seal report: results/B1_B7_cone01_openqasm3_qiskit_loader_evidence_seal_gate_v0.json
- Source artifact count / matching hashes / mismatches: 7 / 7 / 0
- Expected / independent / reproduced seal: d06c1fdae3ad7cad1971cdcdcea1f890d3931924a7e70affc25fdf89737e09a8 / d06c1fdae3ad7cad1971cdcdcea1f890d3931924a7e70affc25fdf89737e09a8 / d06c1fdae3ad7cad1971cdcdcea1f890d3931924a7e70affc25fdf89737e09a8
- Reproduction / source hashes / JSON byte-stable / Markdown byte-stable: True / True / True / True
- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Depth / operation counts: 1483 / {'cx': 789, 'measure': 1, 'rz': 601, 'u': 487}
- Multi / phase / global replay cases / failed total: 8 / 8 / 21 / 0
- Accepted evidence seal / reproduction / occurrence / proxy-T reduction / B7 claim: 1 / 1 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Seeded Product-State Replay Gate

- Exists: True
- Status: cone01_openqasm3_qiskit_loader_seeded_product_replay_passed_without_b7_credit
- Source phase / seal reproduction gates: results/B1_B7_cone01_openqasm3_qiskit_loader_phase_consistent_replay_gate_v0.json / results/B1_B7_cone01_openqasm3_qiskit_loader_evidence_seal_reproduction_gate_v0.json
- Qiskit / qiskit-qasm3-import / openqasm3 versions: 2.4.1 / 0.6.0 / 1.0.1
- Depth / operation counts: 1483 / {'cx': 789, 'measure': 1, 'rz': 601, 'u': 487}
- Input cases / axis sequence / seeds: 16 / ['rx', 'ry', 'rz'] / [17, 29, 41, 53, 67, 79, 83, 97, 101, 113, 127, 131, 149, 163, 181, 191]
- Replay passed / failed cases: True / 0
- Min fidelity / max infidelity: 0.9999999999999389 / 6.106226635438361e-14
- Max amplitude / L2 amplitude / probability delta: 1.3496991625769186e-14 / 2.8917153762798005e-13 / 8.020927672047762e-16
- Accepted seeded-product replay / occurrence / proxy-T reduction / B7 claim: 1 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Seeded Resource-Boundary Gate

- Exists: True
- Status: cone01_openqasm3_qiskit_loader_seeded_resource_boundary_no_b7_credit
- Source seeded replay / line-1381 / theta cost / refreshed B7 gates: results/B1_B7_cone01_openqasm3_qiskit_loader_seeded_product_replay_gate_v0.json / results/B1_B7_cone01_line1381_local_u3_pricing_gate_v0.json / results/B1_B7_cone01_theta_sharing_cost_model_gate_v0.json / results/B1_B7_cone01_shared_theta_refreshed_b7_ledger_gate_v0.json
- Seeded replay passed / cases / min fidelity / max probability delta: True / 16 / 0.9999999999999389 / 8.020927672047762e-16
- Line-1381 off-grid local-U3 / proxy-T pressure / line-1378 recovered: 5 / 100 / False
- Theta cost accepted / pass / fail / refreshed B7 accepts theta sharing: False / 6 / 2 / False
- Missing proxy-T ledger reduction / blocker failed count: 600 / 5
- Accepted boundary / occurrence / proxy-T reduction / B7 claim: 1 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Full-Statevector Replay Probe Gate

- Exists: True
- Status: cone01_default_input_statevector_replay_probe_passed_not_symbolic_certificate
- Qubits / statevector dimension: 19 / 524288
- Source / candidate CNOT count / delta: 795 / 789 / 6
- State fidelity / infidelity: 0.9999999999999551 / 4.4853010194856324e-14
- Max amplitude / probability / measured marginal delta: 1.3908205762322243e-13 / 5.551115123125783e-16 / 5.551115123125783e-16
- Replay probe passed / symbolic unitary claimed / arbitrary input claimed: True / False / False
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Multi-Input Statevector Replay Gate

- Exists: True
- Status: cone01_multi_input_statevector_replay_pressure_passed_not_symbolic_certificate
- Input cases / failed cases: 8 / 0
- Basis / product-state inputs: 6 / 2
- Source / candidate CNOT count / delta: 795 / 789 / 6
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max amplitude / probability delta: 1.392888964263601e-13 / 1.8214596497756474e-15
- Multi-input replay passed / symbolic unitary claimed / arbitrary input claimed: True / False / False
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Phase-Consistent Replay Gate

- Exists: True
- Status: cone01_phase_consistent_sampled_replay_passed_not_symbolic_certificate
- Input cases / failed cases: 8 / 0
- Phase anchors / superposition inputs: 4 / 4
- Source / candidate CNOT count / delta: 795 / 789 / 6
- Phase spread / min overlap magnitude: 1.3722356584366935e-13 / 0.9999999999999772
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max amplitude / probability delta: 1.392888964263601e-13 / 1.074140776324839e-14
- Phase-consistent replay passed / symbolic unitary claimed / arbitrary input claimed: True / False / False
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Global-Phase Subspace Replay Gate

- Exists: True
- Status: cone01_global_phase_subspace_replay_passed_not_symbolic_certificate
- Input cases / failed cases: 21 / 0
- Basis anchors / coherent superpositions: 6 / 15
- Global phase anchor / radians: zero / -2.4388324596671658
- Source / candidate CNOT count / delta: 795 / 789 / 6
- Max anchor phase delta / min overlap magnitude: 3.142993331217661e-14 / 0.9999999999999772
- Min fidelity / max infidelity: 0.9999999999999547 / 4.529709940470639e-14
- Max anchored amplitude / probability delta: 1.3928889642636009e-13 / 1.074140776324839e-14
- Subspace replay passed / symbolic unitary claimed / arbitrary input claimed: True / False / False
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Linear-Span Replay Certificate Gate

- Exists: True
- Status: cone01_linear_span_replay_certificate_passed_not_full_unitary
- Certified input subspace / full input space / fraction: 6 / 524288 / 1.1444091796875e-05
- Linear-span spectral / Frobenius error: 2.7889440543898627e-13 / 6.134324404657074e-13
- Max basis L2 / amplitude / probability delta: 2.534056605707275e-13 / 1.3928889642636009e-13 / 7.771561172376096e-16
- Max source-candidate Gram / cross-Gram delta: 1.9984014443252818e-15 / 4.403624367368429e-14
- Coherent witnesses passed / count: True / 15
- Source / candidate CNOT count / delta: 795 / 789 / 6
- Linear-span passed / symbolic unitary claimed / full-space claimed: True / False / False
- Accepted replay / occurrence / proxy-T reduction / B7 claim: 0 / 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Composable Patch Certificate Gate

- Exists: True
- Status: cone01_composable_patch_certificate_passed_without_b7_resource_credit
- Selected patches / lines / dropped overlap lines: 2 / [268, 1381] / [1378]
- Non-overlap / local-unitary certificates / semantic certificate: True / True / True
- QASM2 candidate exists / emitted: True / True
- Source / candidate CNOT count / delta: 795 / 789 / 6
- Max selected patch residual / entry error: 6.513210005207597e-13 / 4.525273102184799e-13
- Selected CNOT reduction / off-grid local-U3 params: 6 / 5
- Accepted replay / QASM patch / occurrence / proxy-T reduction: 1 / 1 / 0 / 0
- Symbolic equivalence / local-U3 pricing / line1378 recovered / B7 claim: False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Local-U3 Pricing Gate

- Exists: True
- Status: cone01_line1381_local_u3_pricing_boundary_no_b7_credit
- Semantic patch certificate passed: True
- Selected lines / dropped overlap lines: [268, 1381] / [1378]
- Selected CNOT delta / lost line-1378 delta / possible recovered delta: 6 / 3 / 9
- Line-268 / line-1381 / selected off-grid local-U3 params: 0 / 5 / 5
- Line-1381 / selected unpriced proxy-T pressure: 100 / 100
- Boundary passed / local-U3 pricing accepted: True / False
- Accepted replay / QASM patch artifacts: 1 / 1
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Physical Synthesis Pricing Gate

- Exists: True
- Status: cone01_physical_synthesis_pricing_rejects_line1381_b7_credit
- Line-1381 off-grid params / all-grid exact pass count: 5 / 0
- Error budget aggregate / per parameter: 1e-08 / 2e-09
- Single-parameter / total physical synthesis T-count bound: 97 / 485
- Selected CNOT delta / proxy credit / physical cost minus credit: 6 / 120 / 365
- Physical synthesis pricing accepted / line-1378 recovered: False / False
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Gates passed-failed / validation errors: 6-0 / 0

## B1/B7 cone_01 Overlap Additivity Bound Gate

- Exists: True
- Status: cone01_overlap_additivity_bound_blocks_line1378_delta_recovery
- Line-1378 / line-1381 / union windows: [1369, 1377] / [1369, 1379] / [1369, 1379]
- Contained overlap / same support: True / True
- Union source CNOT / additive pair delta / required replacement CNOT: 5 / 6 / -1
- Additive recovery impossible / max extra delta vs line 1381 / full lost delta recoverable: True / 2 / False
- Accepted replay / QASM patch artifacts: 1 / 1
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Union-Region Low-CNOT Search Gate

- Exists: True
- Status: cone01_union_region_low_cnot_search_no_extra_delta
- Union window / support: [1369, 1379] / [4, 8]
- Source CNOT / current replacement CNOT / current delta: 5 / 2 / 3
- Searched CNOT counts / orientations / seeds: [0, 1] / 3 / 16
- 0-CNOT / 1-CNOT exact pass count: 0 / 0
- Best low-CNOT residual / entry error / orientation: 0.2548908758679516 / 0.12724247975106365 / [1, 0]
- Extra delta beyond current line-1381 replacement / global lower bound claimed: 0 / False
- Accepted occurrence / proxy-T reduction / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Union-Region Two-CNOT Orientation Census Gate

- Exists: True
- Status: cone01_union_region_two_cnot_orientation_census_candidate_only
- Union window / support: [1369, 1379] / [4, 8]
- Source CNOT / current replacement CNOT / current delta: 5 / 2 / 3
- Searched CNOT count / orientation sequences / seeds: 2 / 4 / 18
- Exact 2-CNOT sequences: 4 / ['01-01', '01-10', '10-01', '10-10']
- Best exact sequence / residual / entry error: 01-10 / 5.812946138498332e-13 / 3.4095575404049453e-13
- Best exact off-grid / nonzero / total U3 parameters: 13 / 17 / 18
- Extra delta beyond current replacement / replay certificates / B7 claim: 0 / 0 / False
- Validation errors: 0

## B1/B7 cone_01 Union-Region Pricing Dominance Gate

- Exists: True
- Status: cone01_union_region_two_cnot_candidates_pricing_dominated
- Union window / support: [1369, 1379] / [4, 8]
- Current line-1381 off-grid / proxy-T pressure: 5 / 100
- Best priced census sequence / off-grid / proxy-T pressure: 01-10 / 13 / 260
- Delta vs current line-1381 off-grid / proxy-T pressure: 8 / 160
- Census dominates current / current dominates census: False / True
- Selected replacement changed / adopted for B7 / B7 claim: False / False / False
- Validation errors: 0

## B1/B7 cone_01 Union-Region Grid-Snap Pricing Gate

- Exists: True
- Status: cone01_union_region_grid_snap_pricing_rejected
- Orientation sequences: ['01-01', '01-10', '10-01', '10-10']
- Grid-snap exact pass / fail: 0 / 4
- Best grid-snap residual / sequence: 0.36435162331693166 / 10-10
- Worst grid-snap residual / sequence: 1.021457442072864 / 10-01
- Best source off-grid / proxy-T pressure: 13 / 260
- Current line-1381 proxy-T pressure: 100
- Grid-snap pricing accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Union-Region One-Free-Parameter Pricing Gate

- Exists: True
- Status: cone01_union_region_one_free_parameter_pricing_rejected
- Orientation sequences: ['01-01', '01-10', '10-01', '10-10']
- One-free exact pass / fail: 0 / 72
- Best one-free residual / sequence / parameter: 0.25709607640616583 / 10-10 / 7
- Worst best-sequence residual / sequence: 0.6857140007440164 / 10-01
- One-free proxy-T if accepted / current line-1381 proxy-T / source census proxy-T: 20 / 100 / 260
- One-free pricing accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Union-Region Two-Free-Parameter Pricing Gate

- Exists: True
- Status: cone01_union_region_two_free_parameter_pricing_rejected
- Orientation sequences: ['01-01', '01-10', '10-01', '10-10']
- Two-free exact pass / fail: 0 / 612
- Best two-free residual / sequence / pair: 0.1831095797026285 / 10-10 / [5, 7]
- Worst best-sequence residual / sequence: 0.46644639853601 / 10-01
- Two-free proxy-T if accepted / current line-1381 proxy-T / source census proxy-T: 40 / 100 / 260
- Two-free pricing accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Union-Region Targeted Three-Free Expansion Pricing Gate

- Exists: True
- Status: cone01_union_region_targeted_three_free_expansion_rejected
- Probe scope / exhaustive for three-free: best_two_free_pair_plus_one_parameter_per_sequence / False
- Orientation sequences: ['01-01', '01-10', '10-01', '10-10']
- Targeted three-free exact pass / fail: 0 / 64
- Best targeted three-free residual / sequence / triple: 0.04582709543239648 / 10-10 / [5, 7, 4]
- Worst best-sequence residual / sequence: 0.3812803680403496 / 10-01
- Targeted three-free proxy-T if accepted / current line-1381 proxy-T / source census proxy-T: 60 / 100 / 260
- Targeted three-free pricing accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Union-Region Three-CNOT Pricing Screen Gate

- Exists: True
- Status: cone01_union_region_three_cnot_pricing_screen_rejected
- Orientation sequences / exact sequences: 8 / 8
- Best residual / sequence: 5.810128819011275e-13 / 10-01-10
- Best exact sequence / off-grid / proxy-T: 10-10-01 / 18 / 360
- Current line-1381 off-grid / proxy-T / replacement CNOT: 5 / 100 / 2
- Prices below current / structurally dominates current: False / False
- Three-CNOT pricing accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Three-CNOT Context-Absorption Gate

- Exists: True
- Status: cone01_three_cnot_context_absorption_not_accepted
- Selected sequence / off-grid / proxy-T: 10-10-01 / 18 / 360
- Current line-1381 off-grid / proxy-T: 5 / 100
- Inventory exact / abs-match parameter counts: 0 / 0
- Same-support / context abs-match parameter counts: 0 / 0
- Context rotations / one-step exact cancellations: 44 / 0
- Best one-step grid-cancellation error range: 0.000655799901145393 / 0.0945879123733615
- Context absorption accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Three-CNOT Multi-Rotation Context Gate

- Exists: True
- Status: cone01_three_cnot_multi_rotation_context_not_accepted
- Selected sequence / off-grid / proxy-T: 10-10-01 / 18 / 360
- Context rotations / tested off-grid parameters: 44 / 18
- Search widths / total signed-combination tests: [2, 3] / 1975248
- Width-2 / width-3 combinations per parameter: 3784 / 105952
- Width-2 / width-3 exact absorption parameter counts: 0 / 0
- Best width-2 / width-3 error ranges: 0.000655799901145393 to 0.05203432631989813 / 0.000655799901145393 to 0.039971223258799427
- Multi-rotation absorption accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Three-CNOT Four-Rotation Context Gate

- Exists: True
- Status: cone01_three_cnot_four_rotation_context_not_accepted
- Selected sequence / off-grid / proxy-T: 10-10-01 / 18 / 360
- Context rotations / tested off-grid parameters: 44 / 18
- Search width / total signed-combination tests: 4 / 39096288
- Width-4 combinations per parameter / exact absorption parameters: 2172016 / 0
- Best width-4 error range: 0.000655799901145393 to 0.027779719778975753
- Four-rotation absorption accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Leave-One-Out Parameter Gate

- Exists: True
- Status: cone01_line1381_no_single_parameter_free_removal
- Current off-grid parameter indices: [3, 4, 9, 16, 17]
- Leave-one-out exact pass / fail: 0 / 5
- Best leave-one-out residual / fixed index: 0.09892087709180968 / 3
- Residual ratio to exact tolerance min / max: 9892087.709180968 / 28831484.798395302
- Single-parameter removal accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Leave-Two-Out Parameter Gate

- Exists: True
- Status: cone01_line1381_no_two_parameter_free_removal
- Current off-grid parameter indices: [3, 4, 9, 16, 17]
- Leave-two-out exact pass / fail: 0 / 10
- Best leave-two-out residual / fixed pair: 0.13583443746892182 / [9, 16]
- Worst leave-two-out residual / fixed pair: 0.41204448255804876 / [16, 17]
- Residual ratio to exact tolerance min / max: 13583443.746892182 / 41204448.255804874
- Two-parameter removal accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Leave-Three-Out Parameter Gate

- Exists: True
- Status: cone01_line1381_no_three_parameter_free_removal
- Current off-grid parameter indices: [3, 4, 9, 16, 17]
- Leave-three-out exact pass / fail: 0 / 10
- Best leave-three-out residual / fixed triple: 0.29673862906454757 / [4, 9, 16]
- Worst leave-three-out residual / fixed triple: 0.7449029676343185 / [4, 16, 17]
- Residual ratio to exact tolerance min / max: 29673862.906454757 / 74490296.76343185
- Three-parameter removal accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Leave-Four-Out Parameter Gate

- Exists: True
- Status: cone01_line1381_no_four_parameter_free_removal
- Current off-grid parameter indices: [3, 4, 9, 16, 17]
- Leave-four-out exact pass / fail: 0 / 5
- Best leave-four-out residual / fixed quadruple: 0.45761708677312707 / [3, 4, 9, 16]
- Worst leave-four-out residual / fixed quadruple: 0.8369082341779268 / [4, 9, 16, 17]
- Residual ratio to exact tolerance min / max: 45761708.67731271 / 83690823.41779268
- Four-parameter removal accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Line-1381 Leave-Five-Out Parameter Gate

- Exists: True
- Status: cone01_line1381_no_all_grid_parameter_free_removal
- Current off-grid parameter indices: [3, 4, 9, 16, 17]
- Leave-five-out exact pass / fail: 0 / 1
- All-grid residual / fixed set: 0.8415210419190079 / [3, 4, 9, 16, 17]
- Residual ratio to exact tolerance: 84152104.19190079
- Five-parameter removal accepted / B7 claim: False / False
- Validation errors: 0

## B1/B7 cone_01 Theta-Sharing Ledger Gate

- Exists: True
- Status: cone01_theta_sharing_ledger_guardrail
- Candidate windows / theta groups / duplicate theta occurrences: 35 / 4 / 31
- Optimistic cache proxy-T reuse / target proxy-T: 620 / 600
- Optimistic cache model clears target: True
- Occurrence-ledger removed occurrences / proxy-T reduction: 0 / 0
- Occurrence-ledger clears target: False
- Additional occurrence certificates required: 30
- Cache model accepted as FT ledger: False
- Rewrite/resource/semantic/physical/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Shared-Theta Synthesis Object Gate

- Exists: True
- Status: cone01_shared_theta_synthesis_object_proposal
- Candidate windows / shared objects / covered occurrences: 35 / 4 / 35
- Duplicate theta occurrences / optimistic cache signal: 31 / 620
- Object existence / all windows covered: True / True
- Replay/layout/B7-accepted object counts: 0 / 0 / 0
- Occurrence-ledger removed occurrences / proxy-T reduction: 0 / 0
- Cost model accepted: False
- Rewrite/resource/semantic/physical/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Shared-Theta Replay Verifier Gate

- Exists: True
- Status: cone01_shared_theta_replay_verifier_scaffold
- Candidate windows / shared objects: 35 / 4
- Replay-verified objects / replayed occurrences: 4 / 35
- Coverage matches parameter transfer: True
- Duplicate/missing/theta-mismatch/object-mismatch counts: 0 / 0 / 0 / 0
- Shared-theta replay gate passed: True
- Semantic rewrite verified / cost model accepted: False / False
- Occurrence-ledger removed occurrences / proxy-T reduction: 0 / 0
- Rewrite/resource/semantic/physical/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Shared-Theta Layout/Routing Gate

- Exists: True
- Status: cone01_shared_theta_logical_layout_routing_scaffold
- Candidate windows / shared objects: 35 / 4
- Layout-routed objects / occurrences: 4 / 35
- Logical anchors / route packets: 4 / 35
- Logical topology qubits / total hops / max hops: 16 / 139 / 11
- Missing routes / layout gate passed: 0 / True
- Physical layout / factory model / error budget present: False / False / False
- Occurrence-ledger removed occurrences / proxy-T reduction: 0 / 0
- Rewrite/resource/semantic/physical/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Shared-Theta Factory-Amortization Gate

- Exists: True
- Status: cone01_shared_theta_factory_amortization_scaffold
- Candidate windows / shared objects / routed occurrences: 35 / 4 / 35
- Baseline/shared factory compilation counts: 35 / 4
- Amortized saved compiles / gross proxy-T delta: 31 / 620
- Baseline/shared proxy-T pressure: 700 / 80
- Factory gate passed: True
- Physical factory schedule / error budget / independent baseline / refreshed B7 ledger: False / False / False / False
- Occurrence-ledger removed occurrences / proxy-T reduction: 0 / 0
- Rewrite/resource/semantic/physical/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Shared-Theta Error-Budget Gate

- Exists: True
- Status: cone01_shared_theta_error_budget_scaffold
- Candidate windows / shared objects / routed occurrences: 35 / 4 / 35
- Total / per-object / per-occurrence error budget: 1e-06 / 2.5e-07 / 1e-08
- Aggregate occurrence / object error budget: 3.5e-07 / 1e-06
- Correlation groups / max correlated occurrences: 4 / 16
- Shared-error gate / factory gate passed: True / True
- Independent calibration / hardware noise / independent baseline / refreshed B7 ledger: False / False / False / False
- Occurrence-ledger removed occurrences / proxy-T reduction: 0 / 0
- Rewrite/resource/semantic/physical/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Shared-Theta Independent-Baseline Gate

- Exists: True
- Status: cone01_shared_theta_independent_baseline_scaffold
- Candidate windows / shared objects / duplicate theta occurrences: 35 / 4 / 31
- Baseline/shared proxy-T pressure: 700 / 80
- Gross proxy-T delta: 620
- Double-counted occurrences / proxy-T: 0 / 0
- Independent-baseline gate / evidence present: True / True
- Independent physical baseline / device-calibrated baseline / refreshed B7 ledger: False / False / False
- Rewrite/resource/semantic/physical/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Shared-Theta Refreshed-B7-Ledger Gate

- Exists: True
- Status: cone01_shared_theta_refreshed_b7_ledger_rejected
- Refresh attempted / CM-08 passed: True / False
- B7 accepts theta sharing / cost model accepted: False / False
- Cost-model gates passed / failed: 6 / 2
- Occurrence removals / occurrence proxy-T reduction: 0 / 0
- B7 proxy-T reduction before / after refresh: 0 / 0
- Target / missing proxy-T reduction: 600 / 600
- gcm_h6 current T ledger / target max: 6224 / 5632
- gcm_h6 min row improved: False
- Physical layout / factory schedule / device validation: False / False / False
- Rewrite/resource/semantic/physical/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1/B7 cone_01 Theta-Sharing Cost-Model Gate

- Exists: True
- Status: cone01_theta_sharing_cost_model_not_accepted
- Candidate windows / theta groups / duplicate theta occurrences: 35 / 4 / 31
- Optimistic cache signal / target proxy-T: 620 / 600
- Shared object gate / replay gate: True / True
- Replay-verified shared objects / replayed occurrences: 4 / 35
- Layout gate / routed objects / routed occurrences: True / 4 / 35
- Layout total / max logical hops: 139 / 11
- Factory gate / baseline compiles / shared compiles: True / 35 / 4
- Factory gross proxy-T delta: 620
- Error-budget gate / total budget / aggregate occurrence budget: True / 1e-06 / 3.5e-07
- Error-budget correlation groups / max correlated occurrences: 4 / 16
- Independent-baseline gate / gross delta: True / 620
- Double-counted occurrences / proxy-T: 0 / 0
- Refreshed-B7-ledger attempt / passed: True / False
- B7 accepts theta sharing / refreshed proxy-T reduction / gcm_h6 improved: False / 0 / False
- Acceptance gates passed / failed / total: 6 / 2 / 8
- Cost model accepted: False
- B7 ledger proxy-T reduction after cost model: 0
- Additional occurrence certificates / cost-model gates required: 30 / 2
- Rewrite/resource/semantic/physical/B7-ledger claims: False / False / False / False / False
- Validation errors: 0

## B1 Synthetic Heavy-Hex Noise Proxy

- Exists: True
- Status: synthetic_noise_proxy_not_calibrated_device_claim
- Profile: heavy_hex_like_sparse
- Best comparison: source_level1_routed_vs_virtual_swap
- Source routed vs virtual-SWAP exposure reduction: 32.649071763883484
- Source routed vs virtual-SWAP success proxy ratio: 12748.386582112853

## B2 Baseline Status

- Status: control_baseline
- Configurations: 40
- Shots per configuration: 20000
- Result exists: True
- Target-volume combinations: 32
- Target-volume met/unmet: 27 / 5
- Target-volume result exists: True
- Surface-code rough estimate status: rough_analytic_estimate_not_circuit_level_simulation
- Surface-code rough estimate met/unmet: 13 / 7
- Surface-code rough estimate result exists: True
- Phenomenological decoder status: phenomenological_decoder_fallback_not_surface_code_claim
- Phenomenological decoder configurations: 12
- Phenomenological decoder improved configurations: 2
- Phenomenological decoder best relative reduction: 0.8571428571428571
- Phenomenological decoder result exists: True
- Stim/PyMatching surface-code baseline status: stim_pymatching_surface_code_memory_baseline
- Stim/PyMatching surface-code configurations: 30
- Stim/PyMatching surface-code total shots: 90000
- Stim/PyMatching surface-code distances: [3, 5, 7]
- Stim/PyMatching surface-code memory bases: ['x', 'z']
- Stim/PyMatching surface-code nonincreasing trend checks: 4 / 10
- Stim/PyMatching surface-code max decoder runtime / shot: 1.461244466675756e-05
- Stim/PyMatching surface-code result exists: True
- Stim surface-code target-volume status: stim_surface_code_target_volume_baseline
- Stim surface-code target-volume criterion: wilson_95_high
- Stim surface-code target-volume combinations: 40
- Stim surface-code target-volume met/unmet: 22 / 18
- Stim surface-code target-volume result exists: True
- Biased schedule proxy status: biased_schedule_proxy_not_new_code_claim
- Biased schedule proxy target combinations: 40
- Biased schedule proxy baseline/candidate met: 22 / 28
- Biased schedule proxy candidate-only target hits: 6
- Biased schedule proxy volume improvements: 0
- Biased schedule proxy result exists: True
- Stim biased schedule sweep status: stim_biased_schedule_circuit_sweep_not_new_code_claim
- Stim biased schedule sweep configurations: 90
- Stim biased schedule sweep total shots: 270000
- Stim biased schedule sweep baseline/candidate met: 22 / 26
- Stim biased schedule sweep candidate-only target hits: 4
- Stim biased schedule sweep volume improvements: 0
- Stim biased schedule sweep max decoder runtime / shot: 1.3333611001144163e-05
- Stim biased schedule sweep result exists: True
- Same-hardware schedule status: same_hardware_schedule_candidate_volume_positive_diagnostic_not_new_code_claim
- Same-hardware schedule configurations / shots: 120 / 360000
- Same-hardware schedule baseline/candidate met: 22 / 30
- Same-hardware schedule candidate-only target hits: 8
- Same-hardware schedule volume improvements / max reduction: 22 / 3.0
- Same-hardware schedule new-code/threshold/device claims: False / False / False
- Same-hardware schedule result exists: True
- Same-hardware robustness status: same_hardware_schedule_robustness_boundary_aggressive_only_or_negative
- Same-hardware robustness configurations / shots: 240 / 1200000
- Same-hardware robustness profiles / comparisons: 4 / 160
- Same-hardware robustness improved rows aggressive/non-aggressive: 88 / 0
- Same-hardware robustness aggressive-only dependence: True
- Same-hardware robustness new-code/threshold/device claims: False / False / False
- Same-hardware robustness result exists: True
- Reduced-round artifact boundary status: reduced_round_small_distance_aggressive_artifact_boundary
- Reduced-round artifact boundary candidate/robust improved rows: 22 / 88
- Reduced-round artifact boundary robust non-aggressive rows: 0
- Reduced-round artifact boundary aggressive/distance-3/one-round flags: True / True / True
- Reduced-round artifact boundary small-distance/aggressive dependency: True / True
- Reduced-round artifact boundary new-code/threshold/device claims: False / False / False
- Reduced-round artifact boundary validation errors: 0
- Reduced-round artifact boundary result/markdown exists: True / True
- Leakage-flagged erasure boundary status: leakage_flagged_erasure_boundary_proxy_not_new_code_claim
- Leakage-flagged erasure boundary configurations: 480
- Leakage-flagged erasure boundary baseline/candidate met: 264 / 335
- Leakage-flagged erasure boundary improved rows / d5-d7 rows: 42 / 33
- Leakage-flagged erasure boundary high-efficiency d5-d7 rows: 19
- Leakage-flagged erasure boundary max/mean volume reduction: 23.904170363797693 / 4.836897786181641
- Leakage-flagged erasure boundary non-aggressive/reduced-round flags: True / False
- Leakage-flagged erasure boundary new-code/threshold/device/circuit claims: False / False / False / False
- Leakage-flagged erasure boundary validation errors: 0
- Leakage-flagged erasure boundary result/markdown exists: True / True
- Stim heralded-erasure stress status: stim_heralded_erasure_stress_boundary_not_full_leakage_decoder
- Stim heralded-erasure stress configurations / shots: 108 / 216000
- Stim heralded-erasure stress baseline/candidate met: 53 / 59
- Stim heralded-erasure stress candidate-only hits: 7
- Stim heralded-erasure stress improved rows / d5-d7 rows: 10 / 10
- Stim heralded-erasure stress max/mean volume reduction: 4.5978260869565215 / 2.622552373934098
- Stim heralded-erasure stress reduced-round/d3 flags: False / False
- Stim heralded-erasure stress new-code/threshold/device/full-decoder/shot-conditioned claims: False / False / False / False / False
- Stim heralded-erasure stress validation errors: 0
- Stim heralded-erasure stress result/markdown exists: True / True
- Heralded-erasure false-positive stress status: heralded_erasure_false_positive_boundary_not_shot_conditioned_decoder
- Heralded-erasure false-positive stress configurations / shots: 270 / 324000
- Heralded-erasure false-positive stress candidate met / improved rows: 207 / 13
- Heralded-erasure false-positive stress positive-fp improved / d5-d7 rows: 5 / 5
- Heralded-erasure false-positive stress fp=0.001 / fp=0.003 improved rows: 5 / 0
- Heralded-erasure false-positive stress max/mean volume reduction: 4.5978260869565215 / 2.4620014545995943
- Heralded-erasure false-positive stress new-code/threshold/device/full-decoder/shot-conditioned claims: False / False / False / False / False
- Heralded-erasure false-positive stress validation errors: 0
- Heralded-erasure false-positive stress result/markdown exists: True / True
- Shot-conditioned erasure boundary status: shot_conditioned_calibrated_leakage_boundary_partial_survival_not_threshold
- Shot-conditioned erasure boundary source positive-fp d5/d7 rows: 5
- Shot-conditioned erasure boundary profiles / evaluated rows: 4 / 1152
- Shot-conditioned erasure boundary surviving profiles / max rows: 3 / 4
- Shot-conditioned erasure boundary strict surviving / all-profile robust: 0 / False
- Shot-conditioned erasure boundary calibration model / production decoder / threshold / hardware: True / False / False / False
- Shot-conditioned erasure boundary validation errors: 0
- Shot-conditioned erasure boundary result/markdown exists: True / True
- Posterior-risk ledger status: posterior_weighted_decoder_risk_boundary_not_production_decoder
- Posterior-risk ledger budgets / evaluated rows: 4 / 4608
- Posterior-risk ledger raw / mild / nominal / conservative / strict survivors: 6 / 6 / 5 / 3 / 3
- Posterior-risk ledger strict high-purity / all-profile robust: 0 / False
- Posterior-risk ledger conservative / strict max adjusted reduction: 1.9936373276776251 / 1.7942735949098625
- Posterior-risk ledger risk model / circuit decoder / production decoder / threshold / hardware: True / False / False / False / False
- Posterior-risk ledger validation errors: 0
- Posterior-risk ledger result/markdown exists: True / True
- Decoder input contract status: decoder_input_contract_failed_calibrated_data_or_decoder_required
- Decoder input contract available/missing inputs: 4 / 6
- Decoder input contract gates passed/failed/critical failed: 4 / 5 / 5
- Decoder input contract raw/conservative/strict survivors: 6 / 3 / 3
- Decoder input contract satisfied / demotion recommended: False / True
- Decoder input contract circuit decoder / production decoder / threshold / hardware: False / False / False / False
- Decoder input contract validation errors: 0
- Decoder input contract result/markdown exists: True / True
- Per-shot trace packet status: per_shot_trace_packet_available_decoder_injection_still_missing
- Per-shot trace packet challenges / shots each / total traces: 3 / 192 / 576
- Per-shot trace packet failures / max detectors / synthetic flags: 22 / 120 / 482
- Per-shot trace packet detector bits / observables / synthetic flags persisted: True / True / True
- Per-shot trace packet posterior injection / real calibrated flags: False / False
- Per-shot trace packet circuit decoder / production decoder / threshold / hardware: False / False / False / False
- Per-shot trace packet validation errors: 0
- Per-shot trace packet result/markdown exists: True / True
- Posterior injection gate status: posterior_likelihood_injection_interface_negative_boundary
- Posterior injection gate challenges / profiles / shots: 3 / 3 / 1728
- Posterior injection gate best profile / injected failures / delta: mild_flag_weight_shift / 22 / 0
- Posterior injection gate fixed / introduced / changed predictions: 0 / 0 / 0
- Posterior injection gate injection / synthetic flags / calibrated data / hardware: True / True / False / False
- Posterior injection gate improvement / non-regression / demotion: False / True / True
- Posterior injection gate circuit decoder / production decoder / threshold / hardware: False / False / False / False
- Posterior injection gate validation errors: 0
- Posterior injection gate result/markdown exists: True / True
- DEM edge semantics gate status: dem_informed_detector_edge_semantics_negative_boundary
- DEM edge semantics gate challenges / profiles / shots: 3 / 3 / 1728
- DEM edge semantics gate best profile / injected failures / delta: conservative_dem_responsibility / 22 / 0
- DEM edge semantics gate fixed / introduced / changed predictions: 0 / 0 / 0
- DEM edge semantics gate aggressive injected / introduced failures: 23 / 1
- DEM edge semantics gate DEM semantics / synthetic flags / calibrated data / hardware: True / True / False / False
- DEM edge semantics gate improvement / non-regression / demotion: False / True / True
- DEM edge semantics gate production decoder / threshold / hardware: False / False / False
- DEM edge semantics gate validation errors: 0
- DEM edge semantics gate result/markdown exists: True / True
- Hardware-like leakage gate status: hardware_like_leakage_model_negative_boundary
- Hardware-like leakage gate challenges / profiles / shots / holdout shots: 3 / 3 / 1728 / 864
- Hardware-like leakage gate best profile / injected failures / delta: conservative_hardware_like_leakage / 22 / 0
- Hardware-like leakage gate holdout injected / delta / introduced: 16 / 0 / 0
- Hardware-like leakage gate model flags best / stress: 415 / 727
- Hardware-like leakage gate model / detector bits / synthetic fixture / calibrated data / hardware: True / True / False / False / False
- Hardware-like leakage gate holdout improvement / non-regression / demotion: False / True / True
- Hardware-like leakage gate production decoder / threshold / hardware: False / False / False
- Hardware-like leakage gate validation errors: 0
- Hardware-like leakage gate result/markdown exists: True / True
- Calibration transfer guardrail status: calibration_transfer_guardrail_failed
- Calibration transfer guardrail challenges / traces / profiles / profile rows: 3 / 576 / 3 / 9
- Calibration transfer guardrail passed / failed / missing gates: 6 / 3 / ['C4', 'C5', 'C6']
- Calibration transfer guardrail calibrated flags / hardware traces / holdout improvement: False / False / False
- Calibration transfer guardrail non-regression / transfer ready / production decoder / threshold: True / False / False / False
- Calibration transfer guardrail validation errors: 0
- Calibration transfer guardrail result/markdown exists: True / True
- Calibrated evidence contract status: calibrated_evidence_contract_open_missing_hardware_data
- Calibrated evidence contract source gates / contract failures: ['C4', 'C5', 'C6'] / ['K4', 'K5', 'K6']
- Calibrated evidence contract passed / failed / packets: 5 / 3 / 3
- Calibrated evidence contract data required flags: calibrated=True / hardware=True / holdout=True
- Calibrated evidence contract transfer ready / production decoder / threshold: False / False / False
- Calibrated evidence contract validation errors: 0
- Calibrated evidence contract result/markdown exists: True / True
- Calibrated trace scout status: calibrated_trace_scout_failed_missing_real_calibration
- Calibrated trace scout passed / failed / failed IDs: 5 / 3 / ['S5', 'S6', 'S7']
- Calibrated trace scout traces / trace hashes / synthetic flags: 576 / 3 / 482
- Calibrated trace scout profiles / profile shots / holdout shots: 9 / 1728 / 864
- Calibrated trace scout best profile / holdout baseline / injected / delta: conservative_hardware_like_leakage / 16 / 16 / 0
- Calibrated trace scout calibrated rows / hardware rows / strict holdout improvements: 0 / 0 / 0
- Calibrated trace scout ready / transfer ready / production decoder / threshold: False / False / False / False
- Calibrated trace scout validation errors: 0
- Calibrated trace scout result/markdown exists: True / True

## B3 Resource Proxy Status

- Status: calibration_resource_proxy
- Molecules: 4
- Basis: sto-3g
- Proxy T-count reduction range: 6.11x-6.25x
- Result exists: True
- Quantum observable vs FCI status: quantum_observable_circuit_vs_fci_denominator_proxy_not_advantage_claim
- Quantum observable vs FCI instances/qasm: 4 / 4
- Quantum observable vs FCI max qubits/controlled phases: 21 / 441
- Quantum observable vs FCI beaten count: 0
- Quantum observable vs FCI advantage/reaction claims: False / False
- Quantum observable vs FCI validation errors: 0
- Quantum observable vs FCI result/markdown/qasm exists: True / True / True
- Hamiltonian Pauli mapper status: hamiltonian_pauli_mapper_circuits_vs_fci_denominator_not_advantage_claim
- Hamiltonian Pauli mapper instances/qasm: 4 / 4
- Hamiltonian Pauli mapper max qubits/Pauli terms: 20 / 2951
- Hamiltonian Pauli mapper max packet terms / shot floor: 16 / 30504129929
- Hamiltonian Pauli mapper state-prep/variance included: True / True
- Hamiltonian Pauli mapper beaten count: 0
- Hamiltonian Pauli mapper advantage/reaction claims: False / False
- Hamiltonian Pauli mapper validation errors: 0
- Hamiltonian Pauli mapper result/markdown/qasm exists: True / True / True
- Sampled Pauli confidence status: sampled_pauli_estimator_confidence_intervals_not_advantage_claim
- Sampled Pauli confidence instances / z: 4 / 2.576
- Sampled Pauli confidence max random terms / pilot shots: 2740 / 5611520
- Sampled Pauli confidence max Neyman shot floor: 6570468
- Sampled Pauli confidence reduction range: 442.41739183350575 / 34544.05744748315
- Sampled Pauli confidence all CIs contain exact HF energy: True
- Sampled Pauli confidence selected-CI included / FCI wins: False / 0
- Sampled Pauli confidence advantage/reaction claims: False / False
- Sampled Pauli confidence validation errors: 0
- Sampled Pauli confidence result/markdown exists: True / True
- Selected-CI grouped Pauli status: selected_ci_larger_basis_grouped_pauli_boundary_not_advantage_claim
- Selected-CI grouped Pauli rows / max orbitals / max spin qubits: 4 / 19 / 38
- Selected-CI grouped Pauli max determinant product / max QWC groups: 400 / 809
- Selected-CI grouped Pauli packet reduction range: 1.0 / 4.170212765957447
- Selected-CI grouped Pauli ansatz surcharge / denominator wins: 289100592 / 0
- Selected-CI grouped Pauli large-basis mapper / advantage claims: False / False
- Selected-CI grouped Pauli validation errors: 0
- Selected-CI grouped Pauli result/markdown exists: True / True
- Larger-basis Hamiltonian mapper status: larger_basis_hamiltonian_mapper_boundary_not_advantage_claim
- Larger-basis Hamiltonian mapper included / same denominator basis: True / True
- Larger-basis Hamiltonian mapper max qubits / Pauli terms: 38 / 77858
- Larger-basis Hamiltonian mapper max buckets / Neyman shots: 77116 / 6464114739
- Larger-basis Hamiltonian mapper ansatz executions / denominator wins: 956688981372 / 0
- Larger-basis Hamiltonian mapper advantage/reaction claims: False / False
- Larger-basis Hamiltonian mapper validation errors: 0
- Larger-basis Hamiltonian mapper result/markdown exists: True / True
- Larger-basis QWC grouping status: larger_basis_qwc_grouping_boundary_not_advantage_claim
- Larger-basis QWC grouping included / algorithm: True / bitmask_first_fit_qwc_cover_weight_ascending
- Larger-basis QWC grouping max previous buckets / QWC groups: 77116 / 19644
- Larger-basis QWC grouping reduction range: 3.0925507900677203 / 3.956535634387983
- Larger-basis QWC grouping shot-floor reduced / denominator wins: False / 0
- Larger-basis QWC grouping advantage/reaction claims: False / False
- Larger-basis QWC grouping validation errors: 0
- Larger-basis QWC grouping result/markdown exists: True / True
- Grouped covariance shot-floor status: grouped_covariance_shot_floor_boundary_not_advantage_claim
- Grouped covariance model: exact_HF_product_state_covariance_inside_each_QWC_group
- Grouped covariance max previous/grouped shot floor: 6464114739 / 1283900037
- Grouped covariance reduction range: 4.907216882710797 / 5.58305864065559
- Grouped covariance max pairs / ansatz executions: 73474 / 190017205476
- Grouped covariance denominator wins / advantage claims: 0 / False
- Grouped covariance validation errors: 0
- Grouped covariance result/markdown exists: True / True
- Chemical prep derivative status: chemical_state_prep_derivative_boundary_not_advantage_claim
- Chemical prep derivative propagation / sampled covariance: True / False
- Chemical prep max source/derivative shot floor: 1283900037 / 12839000370000
- Chemical prep derivative inflation range: 10000.0 / 10000.0
- Chemical prep UCCSD/ADAPT/adiabatic 2Q prep max: 1493030 / 11248 / 28120
- Chemical prep denominator wins / advantage claims: 0 / False
- Chemical prep validation errors: 0
- Chemical prep result/markdown exists: True / True
- Compiled UCC/ADAPT covariance pilot status: compiled_ucc_adapt_covariance_pilot_not_advantage_claim
- Compiled UCC/ADAPT pilot molecule / groups / basis cap: h2_bond_stretch / 48 / 12
- Compiled UCC/ADAPT sampled covariance / optimizer accounting: True / True
- Compiled UCC/ADAPT pilot variance error mean/max: 0.006841894985135478 / 0.08265558952228451
- Compiled UCC/ADAPT HF/compiled center floors: 63465167 / 66955026
- Compiled UCC/ADAPT derivative floor / optimizer shots: 669550260000 / 24773359620000
- Compiled UCC/ADAPT denominator wins / advantage claims: 0 / False
- Compiled UCC/ADAPT validation errors: 0
- Compiled UCC/ADAPT result/markdown exists: True / True
- Cross-molecule UCC/ADAPT pressure status: cross_molecule_ucc_adapt_pressure_demote_boundary_not_advantage_claim
- Cross-molecule pressure instances / sampled groups: 4 / 35
- Cross-molecule pressure variance error mean/max: 0.08328222449703826 / 0.50293717180872
- Cross-molecule pressure optimizer shots / 2Q lower bound: 475043013690000 / 281225464104480000
- Cross-molecule pressure demotion recommendation: True / demote_to_negative_boundary_until_multi_parameter_state_prep_or_new_measurement_strategy
- Cross-molecule pressure validation errors: 0
- Cross-molecule pressure result/markdown exists: True / True
- B3/B10 same-access rescue status: same_access_measurement_rescue_failed_not_advantage_claim
- B3/B10 same-access gates passed/failed: 5 / 5
- B3/B10 same-access failed gates: ['M5', 'M6', 'M7', 'M8', 'M9']
- B3/B10 denominator wins / optimizer shots: 0 / 475043013690000
- B3/B10 rescue ready / B3 demoted / BQP separation / quantum advantage: False / True / False / False
- B3/B10 same-access validation errors: 0
- B3/B10 same-access result/markdown exists: True / True
- B3/B10 negative boundary status: same_access_negative_boundary_note_not_advantage_claim
- B3/B10 negative boundary conditions satisfied/unsatisfied: 9 / 0
- B3/B10 negative boundary failed source gates: ['M5', 'M6', 'M7', 'M8', 'M9']
- B3/B10 negative boundary demoted / positive route: True / False
- B3/B10 negative boundary result/markdown exists: True / True

## B4 Trap Protocol Status

- Status: toy_statistical_protocol
- Model status: toy_statistical_protocol_not_quantum_advantage_claim
- Configurations: 36
- Spoofing families tested: 4
- Spoofing families failing batch rule: 4
- Batch completeness range: 0.849536-0.999999
- Result exists: True
- Circuit refresh status: circuit_level_hidden_projection_refresh_boundary_not_quantum_advantage_claim
- Circuit refresh configurations: 192
- Circuit refresh honest completeness: 1.0
- Circuit refresh no-refresh high-leakage max soundness: 0.675
- Circuit refresh best repaired high-leakage max soundness: 0.0
- Circuit refresh result/markdown exists: True / True
- OpenQASM 3 packet status: openqasm3_randomized_measurement_packet_not_hardware_execution_or_advantage_claim
- OpenQASM 3 packet circuits / max qubits: 36 / 30
- OpenQASM 3 packet headers / Aer mismatches / honest completeness: True / 0 / 1.0
- OpenQASM 3 packet hardware execution / advantage / BQP separation: False / False / False
- OpenQASM 3 packet result/markdown/directory exists: True / True / True
- Public-QASM spoofer status: public_qasm_packet_spoofer_boundary_not_protocol_soundness
- Public-QASM spoofer parsed circuits / prediction success: 36 / 1.0
- Public-QASM packet soundness rejected / late-bound private challenges required: True / True
- Public-QASM spoofer hardware execution / advantage / BQP separation: False / False / False
- Public-QASM spoofer result/markdown exists: True / True
- Late-bound contract status: late_bound_private_challenge_contract_partial_not_protocol_soundness
- Late-bound public skeletons / hide private material: 36 / True
- Late-bound deterministic data blocker / late-binding alone sufficient: True / False
- Late-bound gates passed/failed: 4 / 4
- Late-bound contract result/markdown/skeleton-dir exists: True / True / True
- Non-stabilizer pilot status: nonstabilizer_late_bound_transcript_pilot_not_soundness_or_advantage
- Non-stabilizer pilot circuits / deterministic blocker removed: 36 / True
- Non-stabilizer pilot entropy / max output probability: 4.0 / 0.0625
- Non-stabilizer pilot gates passed/failed: 6 / 2
- Non-stabilizer pilot hardware execution / advantage / BQP separation: False / False / False
- Non-stabilizer pilot result/markdown/directory exists: True / True / True
- Support-spoofer gate status: support_aware_spoofer_boundary_not_protocol_soundness
- Support-spoofer circuits / spoofers / rows: 36 / 4 / 144
- Support-spoofer exact success / support acceptance: 0.0625 / 1.0
- Support-spoofer support-only soundness rejected / exact blocker survives: True / True
- Support-spoofer result/markdown exists: True / True
- Private-predicate gate status: verifier_private_predicate_pressure_not_protocol_soundness
- Private-predicate public support / hidden acceptance: 1.0 / 0.0625
- Private-predicate suppression / full leakage breaks gate: 16.0 / True
- Private-predicate result/markdown exists: True / True
- Private-challenge protocol status: formal_verifier_private_challenge_protocol_not_hardware
- Private-challenge protocol rows / gates passed-failed: 36 / 8-0
- Private-challenge support / hidden / full-leak acceptance: 0.5 / 0.0625 / 1.0
- Private-challenge hardware / protocol soundness claim: False / False
- Private-challenge result/markdown exists: True / True
- Private-challenge noise bridge status: private_challenge_noise_transcript_bridge_not_hardware
- Private-challenge noise bridge transcript cases / gates passed-failed: 720 / 8-0
- Private-challenge noise bridge backend-like honest no-refresh / challenge / rotation: 0.747047070414 / 0.805169120213 / 0.866618491942
- Private-challenge noise bridge no-leak / three-leak / full-leak acceptance: 0.0625 / 0.5 / 1.0
- Private-challenge noise bridge hardware / protocol soundness claim: False / False
- Private-challenge noise bridge result/markdown exists: True / True
- Private-challenge spoofer pressure status: parametric_spoofer_pressure_model_not_hardware
- Private-challenge spoofer pressure rows / gates passed-failed: 2880 / 6-2
- Private-challenge spoofer pressure no-leak / backend-refreshed / full-leak max acceptance: 0.1196875 / 0.109140625 / 1.0
- Private-challenge spoofer pressure actual ML / hardware / protocol soundness claim: False / False / False
- Private-challenge spoofer pressure result/markdown exists: True / True
- Private-challenge fitted spoofer status: fitted_spoofer_holdout_attack_on_synthetic_transcripts_not_hardware
- Private-challenge fitted spoofer train/holdout/eval rows: 560 / 160 / 640
- Private-challenge fitted spoofer private-safe / leakage-blind / full-leak acceptance: 0.0625 / 0.35 / 1.0
- Private-challenge fitted spoofer training / hardware / protocol soundness claim: True / False / False
- Private-challenge fitted spoofer result/markdown exists: True / True
- Real-backend transcript readiness status: real_backend_transcript_readiness_failed
- Real-backend transcript readiness passed / failed / missing gates: 5 / 5 / ['R5', 'R6', 'R7', 'R8', 'R9']
- Real-backend transcript readiness real backend / hardware / transcript rows: False / False / 0
- Real-backend transcript readiness private-safe / leakage-blind / full-leak acceptance: 0.0625 / 0.35 / 1.0
- Real-backend transcript readiness result/markdown exists: True / True
- Real-backend transcript contract status: real_backend_transcript_contract_open_missing_hardware_evidence
- Real-backend transcript contract source gates / contract failures: ['R5', 'R6', 'R7', 'R8', 'R9'] / ['K5', 'K6', 'K7', 'K8', 'K9']
- Real-backend transcript contract passed / failed / packets: 5 / 5 / 5
- Real-backend transcript contract required backend / hardware / leakage split: True / True / True
- Real-backend transcript contract readiness / soundness / advantage: False / False / False
- Real-backend transcript contract validation errors: 0
- Real-backend transcript contract result/markdown exists: True / True
- Real-backend packet scout status: real_backend_packet_scout_failed_missing_real_backend_evidence
- Real-backend packet scout passed / failed / failed IDs: 4 / 5 / ['S5', 'S6', 'S7', 'S8', 'S9']
- Real-backend packet scout packets / bridge circuits / fitted rows / holdout rows: 5 / 5760 / 640 / 160
- Real-backend packet scout backend / hardware / transcript rows / real training: False / False / 0 / False
- Real-backend packet scout leakage-blind / full-leak acceptance: 0.35 / 1.0
- Real-backend packet scout readiness / soundness / advantage: False / False / False
- Real-backend packet scout validation errors: 0
- Real-backend packet scout result/markdown exists: True / True

## B5 Hubbard Embedding Status

- Status: exact_small_system_reference
- Model status: exact_small_system_reference_plus_cluster_product_proxy
- Configurations: 15
- Exact Hilbert dimension range: 36-4900
- Mean error/site by cluster size: {'cluster2': 0.09552580663805466, 'cluster4': 0.020619822536401395}
- Result exists: True
- Boundary-field response status: classical_response_denominator
- Boundary-field response instances: 9
- Boundary-field response mean/max relative error: 0.05410039803669608 / 0.12158654151084188
- Boundary-field exact/cluster max Hilbert dimension: 4900 / 36
- Boundary-field oracle tuned / quantum win claimed: True / False
- Boundary-field validation errors: 0
- Boundary-field result/markdown exists: True / True
- Non-oracle response status: non_oracle_response_embedding_denominator_not_quantum_advantage_claim
- Non-oracle response instances: 9
- Non-oracle selected mean/max relative error: 0.050983452310434746 / 0.12308129218169694
- Non-oracle rows beating oracle boundary-field: 4
- Non-oracle exact/cluster max Hilbert dimension: 4900 / 36
- Non-oracle uses exact target / oracle tuned / quantum win claimed: False / False / False
- Non-oracle validation errors: 0
- Non-oracle result/markdown exists: True / True
- MPS truncation response status: mps_schmidt_truncation_response_reference_not_dmrg_or_advantage_claim
- MPS truncation instances / bond dimensions / selected bond dimension: 9 / [2, 4, 8, 16] / 16
- MPS truncation selected mean/max relative error: 0.0004416259745141554 / 0.0016954037598740704
- MPS truncation selected mean/max energy error per site: 0.00024397248715074744 / 0.001155884563244336
- MPS truncation min overlap / fixed-sector norm: 0.9991007973730949 / 0.9991007973728403
- MPS rows beating non-oracle embedding: 6
- MPS exact-state seeded / variational DMRG / quantum win claimed: True / False / False
- MPS validation errors: 0
- MPS result/markdown exists: True / True
- Two-site finite-DMRG status: two_site_finite_dmrg_pressure_reference_not_production_dmrg_or_advantage_claim
- Two-site finite-DMRG instances / bond dimensions / restarts x sweeps: 9 / [4] / 2 x 4
- Two-site finite-DMRG selected mean/max relative error: 0.08196129814275509 / 0.2771034796538877
- Two-site finite-DMRG rows beating ALS / seeded pressure: 4 / 0
- Two-site finite-DMRG production DMRG / quantum win claimed: False / False
- Two-site finite-DMRG validation errors: 0
- Two-site finite-DMRG result/markdown exists: True / True
- Canonical-environment smoke gate status: canonical_environment_smoke_gate_failed_not_production_dmrg
- Canonical-environment smoke gate instances / ledger rows / smoke-passed rows: 9 / 9 / 0
- Canonical-environment smoke gate fixed-sector / variance / discarded-weight / monotonicity rows: 3 / 3 / 3 / 3
- Canonical-environment smoke gate response-close / beats seeded / beats ALS: 0 / 0 / 4
- Canonical-environment smoke gate mean/max response error: 0.08196129814275509 / 0.2771034796538877
- Canonical-environment smoke gate min norm / max discarded / max variance: 0.0004341448345871234 / 0.23370810023566455 / 1.798245465474567
- Canonical-environment smoke gate mature DMRG / production DMRG / quantum win: False / False / False
- Canonical-environment smoke gate validation errors: 0
- Canonical-environment smoke gate result/markdown exists: True / True
- Variational MPS/ALS status: variational_mps_als_pressure_reference_not_production_dmrg_or_advantage_claim
- Variational MPS/ALS instances / bond dimensions / selected bond dimensions: 9 / [2, 4] / [4]
- Variational MPS/ALS restarts x sweeps: 3 x 8
- Variational MPS/ALS selected mean/max relative error: 0.01805548365563228 / 0.03907201105154143
- Variational MPS/ALS selected mean/max energy error per site: 0.0030253726531345435 / 0.008534748468465136
- Variational MPS/ALS min overlap / fixed-sector norm: 0.9626138997075306 / 0.0001648333575571581
- Variational MPS/ALS rows beating seeded MPS pressure: 0
- Variational MPS/ALS exact-state seeded / production DMRG / quantum win claimed: False / False / False
- Variational MPS/ALS validation errors: 0
- Variational MPS/ALS result/markdown exists: True / True
- Canonical DMRG readiness status: canonical_dmrg_readiness_gate_failed_not_production_dmrg
- Canonical DMRG readiness gates passed/failed: 0 / 8
- Canonical DMRG readiness seeded reference strongest / prototype fixed-sector norms pass: True / False
- Canonical DMRG readiness production DMRG / quantum win / same-access positive route: False / False / False
- Canonical DMRG readiness validation errors: 0
- Canonical DMRG readiness result/markdown exists: True / True
- B5/B10 same-access production contract status: same_access_production_contract_failed
- B5/B10 same-access production contract gates passed/failed: 2 / 8
- B5/B10 same-access production contract smoke/readiness/sampling blockers: 0 smoke-passed rows / 0 readiness gates / 5 blocking sampling requirements
- B5/B10 same-access production contract production DMRG / oracle / positive route: False / False / False
- B5/B10 same-access production contract validation errors: 0
- B5/B10 same-access production contract result/markdown exists: True / True
- B5/B10 production implementation triage status: production_implementation_triage_ready_no_positive_route
- B5/B10 production implementation triage source gates passed/failed: 2 / 8
- B5/B10 production implementation triage work packets ready/blocked: 2 / 4
- B5/B10 production implementation triage conditions satisfied/unsatisfied: 6 / 0
- B5/B10 production implementation triage DMRG / oracle / positive route / catalog change: False / False / False / False
- B5/B10 production implementation triage result/markdown exists: True / True
- B5/B10 row-contract harness status: row_contract_preserved_guardrail_ready
- B5/B10 row-contract harness rows/hash: 9 / 7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc
- B5/B10 row-contract harness source checks passed/failed: 10 / 0
- B5/B10 row-contract harness conditions satisfied/failed: 6 / 0
- B5/B10 row-contract harness remaining positive-route packets: ['W1', 'W2', 'W3']
- B5/B10 row-contract harness result/markdown exists: True / True
- B5 seeded-pressure replacement audit status: seeded_pressure_replacement_failed_remains_blocker
- B5 seeded-pressure replacement audit seeded/best mean error: 0.0004416259745141553 / 0.01805548365563228
- B5 seeded-pressure replacement audit best candidate / rows beating seeded: variational_mps_als / 0
- B5 seeded-pressure replacement audit deployable replacements / seeded replaced: 0 / False
- B5 seeded-pressure replacement audit remaining positive-route packets: ['W1', 'W3']
- B5 seeded-pressure replacement audit result/markdown exists: True / True
- B5/B10 response-oracle cost ledger status: same_access_response_oracle_cost_ledger_failed_no_oracle
- B5/B10 response-oracle cost ledger requirements passed/failed: 3 / 5
- B5/B10 response-oracle cost ledger failed IDs: ['O3', 'O4', 'O5', 'O6', 'O7']
- B5/B10 response-oracle cost ledger oracle constructed / remaining packets: False / ['W1']
- B5/B10 response-oracle cost ledger result/markdown exists: True / True
- B5/B10 W1 production DMRG/MPS acceptance status: production_dmrg_mps_acceptance_gate_failed_no_w1_denominator
- B5/B10 W1 production DMRG/MPS acceptance requirements passed/failed: 3 / 7
- B5/B10 W1 production DMRG/MPS failed IDs: ['D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9']
- B5/B10 W1 production DMRG/MPS denominator available / remaining packets: False / ['W1']
- B5/B10 W1 production DMRG/MPS result/markdown exists: True / True
- B5 W1 denominator engine status: w1_denominator_engine_v0_failed_not_production_dmrg
- B5 W1 denominator engine requirements passed/failed: 4 / 4
- B5 W1 denominator engine failed IDs: ['E4', 'E5', 'E6', 'E7']
- B5 W1 denominator engine convergence / seeded wins: 0 / 0
- B5 W1 denominator engine result/markdown exists: True / True
- B5 W1 canonical residual blocker status: w1_canonical_residual_blocker_gate_failed_missing_production_evidence
- B5 W1 canonical residual blocker requirements passed/failed: 4 / 4
- B5 W1 canonical residual blocker failed IDs: ['C3', 'C4', 'C5', 'C7']
- B5 W1 canonical residual blocker env/residual/convergence rows: 0 / 0 / 0
- B5 W1 canonical residual blocker PR packets: 4
- B5 W1 canonical residual blocker result/markdown exists: True / True
- B5/B10 W1 implementation contract status: w1_implementation_contract_open_not_production_dmrg
- B5/B10 W1 implementation contract requirements passed/failed: 5 / 5
- B5/B10 W1 implementation contract failed IDs: ['K5', 'K6', 'K7', 'K8', 'K9']
- B5/B10 W1 implementation contract packets: ['W1-E4-env-residuals', 'W1-E5-convergence', 'W1-E6-seeded-pressure', 'W1-E7-cost-ledger']
- B5/B10 W1 implementation contract result/markdown exists: True / True
- B5/B10 W1 prototype environment scout status: w1_prototype_environment_scout_failed_not_canonical_contract
- B5/B10 W1 prototype environment scout requirements passed/failed: 5 / 3
- B5/B10 W1 prototype environment scout failed IDs: ['P5', 'P6', 'P7']
- B5/B10 W1 prototype/contract env rows: 9 / 0
- B5/B10 W1 prototype trace/residual/accepted rows: 9 / 0 / 0
- B5/B10 W1 prototype environment scout result/markdown exists: True / True
- B5/B10 W1 production-row intake status: w1_production_row_intake_template_open_missing_submitted_rows
- B5/B10 W1 production-row intake requirements passed/failed: 5 / 3
- B5/B10 W1 production-row intake failed IDs: ['I5', 'I6', 'I7']
- B5/B10 W1 production-row intake templates / production keys / missing keys: 9 / 8 / 72
- B5/B10 W1 production-row intake submitted/accepted rows: 0 / 0
- B5/B10 W1 production-row intake result/markdown exists: True / True

## B6 Superconductivity Descriptor Status

- Status: toy_descriptor_ranking
- Model status: toy_descriptor_ranking_not_material_discovery_claim
- Candidates: 72
- Top-k: 12
- Known high-Tc precision@k: 0.8333333333333334
- Known high-Tc recall@k: 0.2777777777777778
- Top family counts: {'cuprate_like': 8, 'iron_pnictide_like': 2, 'nickelate_like': 2}
- Result exists: True
- Curated leakage audit status: curated_retrospective_leakage_audit
- Curated records / families / split year: 26 / 12 / 2008
- Curated post-split records / positives: 8 / 7
- Curated all physics AP@k / random AP@k mean: 0.89 / 0.5345944165426587
- Curated post-split physics AP / family-prior AP / random AP mean: 0.9093537414965986 / 0.9379251700680272 / 0.9030476057610545
- Curated family-holdout physics AP / random AP mean: 0.9722222222222222 / 0.8528645833333333
- Curated discovery/mechanism/database claims: False / False / False
- Curated validation errors: 0
- Curated result/markdown exists: True / True
- Formula descriptor screen status: formula_descriptor_screen_not_material_discovery_claim
- Formula records / expanded negatives / families: 38 / 12 / 22
- Formula AP@k / family-prior AP@k: 0.09999999999999999 / 1.0
- Formula post-split AP / family-prior post-split AP: 0.5947278911564625 / 0.9821428571428571
- Formula discovery/mechanism/database/computed-observable claims: False / False / False / False
- Formula uses formula descriptors / B5-linked proxy: True / True
- Formula validation errors: 0
- Formula result/markdown exists: True / True
- Structural/electronic proxy status: structural_electronic_proxy_boundary_not_material_discovery_claim
- Structural/electronic records / expanded negatives / families: 38 / 12 / 22
- Structural/electronic AP@k / formula AP@k / family-prior AP@k: 0.6110119047619047 / 0.09999999999999999 / 1.0
- Structural/electronic post-split AP / family-prior post-split AP: 0.6899659863945579 / 0.9821428571428571
- Structural/electronic holdout AP / top-k negative controls: 0.8958333333333333 / 3
- Structural/electronic discovery/mechanism/database/DFT/crystal claims: False / False / False / False / False
- Structural/electronic validation errors: 0
- Structural/electronic result/markdown exists: True / True
- Crystallographic reproducibility gate status: crystallographic_reproducibility_gate_failed_not_material_discovery_claim
- Crystallographic reproducibility gates passed/failed: 6 / 5
- Crystallographic reproducibility failed requirements: ['R6', 'R7', 'R8', 'R9', 'R10']
- Crystallographic records / families / negatives: 56 / 28 / 18
- Crystallographic post-split AP / family-prior AP: 0.2476190476190476 / 0.4901360544217687
- Crystallographic source validation errors / pymatgen available: 2 / False
- Crystallographic gate result/markdown exists: True / True
- Crystallographic evidence contract status: crystallographic_evidence_contract_open_not_material_discovery_claim
- Crystallographic evidence contract source failures / contract failures: ['R6', 'R7', 'R8', 'R9', 'R10'] / ['K4', 'K5', 'K6', 'K7', 'K8']
- Crystallographic evidence contract passed / failed / packets: 3 / 5 / 5
- Crystallographic evidence contract packet IDs: ['B6-R6-reproducible-crystallographic-backend', 'B6-R7-source-validation-cleanup', 'B6-R8-family-prior-denominator', 'B6-R9-dft-observable-channel', 'B6-R10-b5-observable-channel']
- Crystallographic evidence contract result/markdown exists: True / True
- Crystallographic packet scout status: crystallographic_packet_scout_failed_missing_computed_evidence
- Crystallographic packet scout passed / failed / failed IDs: 3 / 5 / ['S4', 'S5', 'S6', 'S7', 'S8']
- Crystallographic packet scout packets / records / families / negatives: 5 / 56 / 28 / 18
- Crystallographic packet scout AP / family prior / validation errors / backend: 0.2476190476190476 / 0.4901360544217687 / 2 / False
- Crystallographic packet scout DFT rows / B5 rows / ready: 0 / 0 / False
- Crystallographic packet scout discovery/mechanism/solution claims: False / False / False
- Crystallographic packet scout validation errors: 0
- Crystallographic packet scout result/markdown exists: True / True
- Validation rescue scout status: validation_rescue_candidate_found_not_material_discovery_claim
- Validation rescue scout selected variant / candidates: physics_risk_adjusted_v0 / 4
- Validation rescue scout passed / failed / failed IDs: 5 / 3 / ['V6', 'V7', 'V8']
- Validation rescue scout selected AP / family prior / negative controls: 1.0 / 0.4901360544217687 / 2
- Validation rescue scout backend / DFT rows / B5 rows: False / 0 / 0
- Validation rescue scout discovery/mechanism/solution claims: False / False / False
- Validation rescue scout validation errors: 0
- Validation rescue scout result/markdown exists: True / True
- Backend replay scout status: backend_replay_candidate_built_missing_observables
- Backend replay scout selected variant: physics_risk_adjusted_v0
- Backend replay scout passed / failed / failed IDs: 6 / 2 / ['R7', 'R8']
- Backend replay scout selected AP / family prior / negative controls: 1.0 / 0.4901360544217687 / 2
- Backend replay scout source/formula/replay hashes: ce134d0a5d295af982b77be0a8a43e90ea19e828af20cc80ac3f20b7664d2fdc / e23239648dd11aa8e0db8ecdeb5824506a5a379c9ba2777965c3aafa5d5d8230 / c44099194d0bc04d74cd3c4c4e068bf51a9e114d11c6e0b5e3890786cda5b8de
- Backend replay scout DFT rows / B5 rows: 0 / 0
- Backend replay scout discovery/mechanism/solution claims: False / False / False
- Backend replay scout validation errors: 0
- Backend replay scout result/markdown exists: True / True
- Observable contract gate status: observable_contract_open_missing_dft_b5_rows
- Observable contract gate passed / failed / failed IDs: 4 / 2 / ['O5', 'O6']
- Observable contract gate packets / DFT keys / B5 keys: 5 / 11 / 11
- Observable contract gate DFT/B5 schema hashes: e9215a51f2736f1c29890577b201ad5980b835dd787bd9bde4f2484293f17388 / 79217e965af5e0d4ed95f143fcfd0aa3936edef001a292f559a70cf9e688c576
- Observable contract gate DFT rows / B5 rows: 0 / 0
- Observable contract gate discovery/mechanism/solution claims: False / False / False
- Observable contract gate validation errors: 0
- Observable contract gate result/markdown exists: True / True

## B7 Fault-Tolerance Co-Design Status

- Status: planning_level_resource_model
- Model status: planning_level_resource_model_not_physical_layout
- Workloads: 3
- Configurations: 6
- Minimum space-time-volume reduction: 6.774167409448178
- Mean space-time-volume reduction: 7.198862199777527
- Workloads meeting 25% reduction: 3
- Result exists: True
- B1/B2 dependency bridge status: dependency_schedule_bridge_not_physical_layout
- B1/B2 dependency bridge comparisons: 6
- B1/B2 dependency bridge min STV reduction: 1.1948051948051948
- B1/B2 dependency bridge mean STV reduction: 1.353572610789181
- B1/B2 dependency bridge selected B2 distance/target: d=3 / 0.01
- B1/B2 dependency bridge result exists: True
- Workload DAG factory schedule status: workload_dag_factory_schedule_not_physical_layout
- Workload DAG factory comparisons: 18
- Workload DAG factory variants: ['serial_factory', 'balanced_factories', 'throughput_heavy_factories']
- Workload DAG min STV reduction: 1.1939655172413792
- Workload DAG mean STV reduction: 1.4748795826243428
- Workload DAG factory bottleneck comparisons: 6
- Workload DAG result exists: True
- Logical T factory schedule status: logical_t_factory_schedule_proxy_not_physical_layout
- Logical T factory comparisons: 18
- Logical T factory bottleneck comparisons: 18
- Logical T factory mean STV reduction: 1.0
- Logical T-count mean reduction: 1.0
- Logical T factory result exists: True
- Post-1Q logical T factory status: logical_t_factory_schedule_proxy_not_physical_layout
- Post-1Q logical T factory comparisons: 18
- Post-1Q logical T factory bottleneck comparisons: 18
- Post-1Q logical T factory min STV reduction: 1.0
- Post-1Q logical T factory mean STV reduction: 1.0344368482291184
- Post-1Q logical T-count mean reduction: 1.0344608655439516
- Post-1Q logical T factory result exists: True
- Native logical T factory status: logical_t_factory_schedule_proxy_not_physical_layout
- Native logical T factory comparisons: 18
- Native logical T factory bottleneck comparisons: 18
- Native logical T factory min STV reduction: 1.0
- Native logical T factory mean STV reduction: 1.0346085233083853
- Native logical T-count mean reduction: 1.0346288200248595
- Native logical T factory result exists: True
- Control-RZ logical T factory status: logical_t_factory_schedule_proxy_not_physical_layout
- Control-RZ logical T factory comparisons: 18
- Control-RZ logical T factory bottleneck comparisons: 18
- Control-RZ logical T factory min STV reduction: 1.1219512195121952
- Control-RZ logical T factory mean STV reduction: 1.1839213595354279
- Control-RZ logical T-count mean reduction: 1.1841020176930053
- Control-RZ logical T factory result exists: True
- U3 phase-factored logical T factory status: logical_t_factory_schedule_proxy_not_physical_layout
- U3 phase-factored logical T factory comparisons: 18
- U3 phase-factored logical T factory bottleneck comparisons: 18
- U3 phase-factored logical T factory min STV reduction: 1.1219512195121952
- U3 phase-factored logical T factory mean STV reduction: 1.2343939344748929
- U3 phase-factored logical T-count mean reduction: 1.2346077339597366
- U3 phase-factored logical T factory result exists: True
- Minimum-STV regime classifier status: min_stv_regime_classified_not_physical_layout_claim
- Minimum-STV regime classifier min workload: qasmbench_medium_exact/sat_n11.qasm
- Minimum-STV regime classifier min STV reduction: 1.1219512195121952
- Minimum-STV regime classifier factory-bottleneck rows: 18
- Minimum-STV regime classifier deep factory-locked rows: 10
- T proxy still needed for 1.20x / 1.25x STV: 344 / 544
- Minimum-STV regime classifier result exists: True
- FT synthesis ledger status: ft_synthesis_ledger_proxy_not_physical_layout
- FT synthesis ledger min workload: qasmbench_medium_exact/gcm_h6.qasm
- FT synthesis ledger min STV reduction: 1.086007702182285
- FT synthesis ledger mean STV reduction: 1.253640000721326
- FT synthesis ledger after factory/data bottlenecks: 16 / 2
- FT synthesis ledger sat_n11 T ledger before/after: 294 / 262
- FT synthesis ledger sat_n11 balanced/throughput STV: 1.6114808652246255 / 1.6114808652246255
- FT synthesis ledger result exists: True
- gcm_h6 FT boundary status: gcm_h6_ft_boundary_quantified_not_physical_layout
- gcm_h6 FT boundary current min workload/variant: qasmbench_medium_exact/gcm_h6.qasm / throughput_heavy_factories
- gcm_h6 FT boundary current min STV: 1.086007702182285
- gcm_h6 arbitrary numeric rotations/cost: 270 / 5400
- gcm_h6 T ledger still needed for 1.20x / 1.25x STV: 592 / 824
- Cost sweep alone clears 1.20x all-variant min: False
- gcm_h6 FT boundary result exists: True
- Precision-aware rotation ledger status: precision_aware_rotation_ledger_negative_boundary_not_physical_layout
- Precision-aware rotation ledger arbitrary/unique numeric rotations: 270 / 26
- Precision-aware one-sided max arbitrary T cost for 1.20x / 1.25x: 17 / 16
- Best tested precision budget arbitrary T cost / min STV: 35 / 1.0793157076205289
- Precision budgets clear 1.20x all-variant/gcm_h6 min: False / False
- Precision-aware rotation ledger result exists: True
- gcm_h6 numeric-rotation structure status: gcm_h6_numeric_rotation_structure_negative_boundary_not_physical_layout
- gcm_h6 numeric rotations before/after/removed: 270 / 270 / 0
- gcm_h6 numeric-structure T ledger before/after/removed: 6224 / 6224 / 0
- gcm_h6 numeric-structure proof events / Aer failed: 172 / 0
- gcm_h6 numeric-structure min STV / clears 1.20x: 1.086007702182285 / False
- gcm_h6 numeric-rotation structure result exists: True
- Shared synthesis/cache boundary status: shared_synthesis_cache_no_ft_t_ledger_reduction_boundary
- Shared synthesis/cache occurrences / unique numeric instructions: 270 / 26
- Shared synthesis/cache classical catalog reduction factor: 10.384615384615385
- Shared synthesis/cache physical T ledger before/after: 6760 / 6224
- Shared synthesis/cache FT T-ledger reduction from cache: 0
- Shared synthesis/cache physical min STV / clears 1.20x: 1.086007702182285 / False
- Invalid after-only unique-template gcm_h6/all-variant clears 1.20x: True / False
- Shared synthesis/cache boundary result exists: True
- Nonlocal template block scan status: nonlocal_template_block_scan_negative_boundary_not_physical_layout
- Nonlocal template candidate certificates / top templates: 2633 / 12
- Best nonlocal template id/width/occurrences: w8_21 / 8 / 20
- Best nonlocal template arbitrary coverage: 5 per occurrence, 100 physical occurrences covered
- Nonlocal template adjacent inverse/duplicate pairs: 0 / 0
- Nonlocal template removed arbitrary/T ledger: 0 / 0
- Nonlocal template min STV / gcm_h6 occurrence target for 1.20x: 1.086007702182285 / 30
- Nonlocal template all-variant 1.20x by gcm_h6-only removals: False
- Nonlocal template block scan result exists: True
- Template priority gate status: template_priority_gate_no_single_one_angle_template_clears_gcm_h6
- Template priority gate templates / target removed arbitrary / one-angle clear count: 12 / 30 / 0
- Template priority gate best template / required removals per occurrence / one-angle shortfall: w8_21 / 2 / 10
- Template priority gate w8_21 prior optimizer runs / exact rewrite found: 43480 / False
- Template priority gate all-variant 1.20x / physical claim / global lower bound: False / False / False
- Template priority gate validation errors / result/markdown exists: 0 / True / True
- w8_21 small-block synthesis status: w8_21_small_block_synthesis_negative_boundary_not_physical_layout
- w8_21 synthesis attempts / passing candidates: 55 / 0
- w8_21 best fixed parameter/label/residual: a / pi/2 / 0.03936333737388844
- w8_21 local rank / five-degree support: 5 / True
- w8_21 same-skeleton exact replacement found: False
- w8_21 small-block synthesis result/proof exists: True / True
- w8_21 broad-skeleton search status: w8_21_broad_skeleton_search_negative_boundary_not_global_lower_bound
- w8_21 broad-skeleton families total/scanned/selection: 15360 / 15360 / exhaustive
- w8_21 broad-skeleton optimizer runs / passing candidates: 30720 / 0
- w8_21 broad-skeleton best family/residual: ry_q1-cx01-rz_q1-cx01-rz_q1-ry_q1 / 0.24437773599006635
- w8_21 broad-skeleton exact found / global lower bound claimed: False / False
- w8_21 broad-skeleton result/proof exists: True / True
- w8_21 Euler-local search status: w8_21_euler_local_search_negative_boundary_not_global_lower_bound
- w8_21 Euler-local families total/scanned/mode: 500 / 500 / target-informed
- w8_21 Euler-local optimizer runs / passing candidates: 3000 / 0
- w8_21 Euler-local best family/residual: cx01-cx01|fixed[mid:q1:rz1=pi]|free[pre:q1:ry,mid:q1:rz0,post:q1:rz0,post:q1:ry] / 0.24437773599006604
- w8_21 Euler-local exact found / global lower bound claimed: False / False
- w8_21 Euler-local result/proof exists: True / True
- w8_21 three-CNOT search status: w8_21_three_cnot_search_negative_boundary_not_global_lower_bound
- w8_21 three-CNOT families total/scanned/mode: 1480 / 1480 / target-informed
- w8_21 three-CNOT optimizer runs / passing candidates: 8880 / 0
- w8_21 three-CNOT best family/residual: cx01-cx10-cx10|fixed[mid1:q1:rz1=pi]|free[mid1:q1:rz0,mid1:q1:ry,post:q0:rz0,post:q1:rz0] / 1.0352761804100845
- w8_21 three-CNOT exact found / global lower bound claimed: False / False
- w8_21 three-CNOT result/proof exists: True / True
- w8_21 scoped minimality note status: scoped_minimality_note_not_global_lower_bound
- w8_21 scoped minimality optimizer runs / exact rewrite found: 43480 / False
- w8_21 scoped minimality arbitrary/T ledger removed: 0 / 0
- w8_21 scoped minimality markdown exists: True
- w8_21 claim-boundary fragment status: claim_boundary_fragment_not_minimality_theorem
- w8_21 claim-boundary optimizer runs / exact rewrite found: 43480 / False
- w8_21 claim-boundary arbitrary/T ledger removed: 0 / 0
- w8_21 claim-boundary global minimality theorem claimed: False
- w8_21 claim-boundary markdown exists/has claim: True / True

## B8 Output Invariant Verification Status

### R155 Execution-Mode Attribution

- Status: execution_mode_attribution_diagnostic_complete
- Processes / rows / circuits / shots: 8 / 768 / 2304 / 4718592
- Unstable cells / mismatch rows / automatic QASM variants: 3 / 3 / 2
- Automatic fidelity / implied 96-row mean delta: 0.00021077592739027207 / 2.1955825769820006e-06
- First divergence / Aer-only excluded: automatic_transpilation / True
- Causal attribution supported: False
- Requirements passed/failed: 10 / 0
- Result/report exists: True / True

### R156 Transpiler Variant-Capture Protocol

- Status: transpiler_variant_capture_protocol_frozen_before_execution
- Frozen row / trial / seed: FakeNairobiV2 / 21 / 105203961
- Processes / compilations: 32 / 32
- Simulation executions / shots: 0 / 0
- Expected R155 variants: 2
- Execution started: False
- Requirements passed/failed: 10 / 0

### R156 Transpiler Variant Capture

- Status: transpiler_variant_capture_diagnostic_complete
- Processes / callback rows / final variants: 32 / 1600 / 2
- Variant process counts / known R155 variants reproduced: [20, 12] / True
- First property divergence: VF2PostLayout at callback 17
- First circuit divergence: ApplyLayout at callback 18
- Simulation executions / shots: 0 / 0
- Requirements passed/failed: 10 / 0
- Result/report exists: True / True

### R157 VF2 Tie-Isolation Protocol

- Status: vf2_tie_isolation_protocol_frozen_before_execution
- Profiles / processes / direct replays: 5 / 98 / 160
- Shared mapping score / exactly tied: 0.45894321220828727 / True
- Simulation executions / shots: 0 / 0
- Execution started: False
- Requirements passed/failed: 10 / 0
- Protocol/contract/input/report exists: True / True / True / True

### R157 VF2 Tie Isolation

- Status: vf2_tie_isolation_diagnostic_complete
- Profiles / processes / direct replays: 5 / 98 / 160
- Mapping-class counts: {'endpoint_4_to_0': 103, 'endpoint_4_to_2': 57, 'no_solution': 0, 'other_mapping': 0}
- Profile collapse / variation: 0 / 5
- Target-order hashes / implementation-smoke replays: 3 / 5
- Blinded confirmation claimed: False
- Simulation executions / shots: 0 / 0
- Requirements passed/failed: 10 / 0
- Result/report exists: True / True

### R158 VF2 Accelerator-Boundary Protocol

- Status: vf2_accelerator_boundary_protocol_frozen_before_execution
- Profiles / processes / direct replays: 4 / 4 / 256
- Qiskit source commit: 0fd015a22b84c9082173597a5d2304dc0aaec08c
- Installed accelerator SHA-256: a299d48f8d174481d389b30f1fd240a845144922f32ef918925b17243fc5f007
- Simulation executions / shots: 0 / 0
- Execution started: False
- Requirements passed/failed: 10 / 0
- Protocol/contract/source/report exists: True / True / True / True

### R158 VF2 Accelerator Boundary

- Status: vf2_accelerator_boundary_diagnostic_complete
- Profiles / processes / direct replays: 4 / 4 / 256
- Mapping-class counts: {'endpoint_4_to_0': 180, 'endpoint_4_to_2': 76, 'no_solution': 0, 'other_mapping': 0}
- Profile collapse / variation: 1 / 3
- Classification / fully shared outcome: internal_error_map_boundary / collapse
- Simulation executions / shots: 0 / 0
- Requirements passed/failed: 10 / 0
- Result/report exists: True / True

### R159 ErrorMap Accumulation Trace Protocol

- Status: error_map_accumulation_trace_protocol_frozen_before_execution
- Profiles / processes / traced calls: 3 / 3 / 256
- Patched source SHA-256: ab0f531947caee2667d2be3f3cc63701dc925c1cc60b16d32e9c1b1f97dc526f
- Instrumented binary SHA-256: b24cf71992cdedc71dd648f6ef758862f253cea8d51274d92d9082b3ed3ec903
- Execution started: False
- Requirements passed/failed: 10 / 0
- Protocol/contract/build/patch/report exists: True / True / True / True / True

### R159 ErrorMap Accumulation Trace

- Status / classification: error_map_accumulation_trace_complete / operation_order_f64_path_supported
- Profiles / processes / traced calls: 3 / 3 / 256
- Mapping-class counts: {'endpoint_4_to_0': 199, 'endpoint_4_to_2': 57, 'no_solution': 0, 'other_mapping': 0}
- Native order/error-bit hashes: 128 / 16
- Native order-to-bits / bits-to-mapping functional: True / True
- Sorted profiles collapse: True
- Simulation executions / shots: 0 / 0
- Requirements passed/failed: 10 / 0
- Result/report/trace directory exists: True / True / True

### R160 Deterministic ErrorMap Remediation Protocol

- Status: deterministic_error_map_remediation_protocol_frozen_before_execution
- Profiles / processes / cases / direct calls: 4 / 16 / 33 / 1056
- Operation inventory hash: 716c841307327f62da7679c77c76bc60cfec5231c26736e328d4594aca67b086
- Margin protection threshold: 1e-16
- Execution started: False
- Requirements passed/failed: 10 / 0
- Protocol/contract/report/executor/generator exists: True / True / True / True / True

### R160 Deterministic ErrorMap Remediation Adjudication

- Raw status / executor classification: deterministic_error_map_remediation_complete / deterministic_external_map_remediation_supported
- Audited classification / support rule passed: tie_stabilized_but_non_tied_guardrail_failed / False
- Profiles / processes / cases / direct calls: 4 / 16 / 33 / 1056
- Exact-oracle pass / fail / failure cases: 832 / 224 / 7
- Margin-protected cases / failures: 12 / 0
- Raw execution integrity passed: True
- Requirements passed/failed: 10 / 0
- Result/report/trace/adjudication/report/tool exists: True / True / True / True / True / True

### R161 Source-Faithful VF2 Score Audit

- Status / classification: source_faithful_score_audit_complete / source_f64_consistent_but_exact_rational_gap_remains
- Profiles / processes / cases / replays: 4 / 16 / 33 / 1056
- R160 exact failures / source-faithful exact failures: 224 / 224
- R160 failures that remain source-f64 minima: 224 / 224
- Source-f64 nonminimum rows: 32
- Requirements passed/failed: 10 / 0
- Protocol/contract/executor/result/report exists: True / True / True / True / True

### R162 Source Score-Combination Trace

- Status / classification: score_trace_diagnostic_complete / source_score_shadow_divergence_localized
- Profiles / processes / replays: 3 / 3 / 256
- Score events / strict Decreasing comparisons / returned candidates: 44800 / 6912 / 256
- Shadow class counts: {'no_candidate': 0, 'source_differs_from_fsum': 141, 'source_equals_fsum_but_exact_binary64_differs': 115, 'source_equals_fsum_equals_exact_binary64': 0}
- Requirements passed/failed: 10 / 0
- Protocol/contract/build/patch/executor/result/report exists: True / True / True / True / True / True / True

### R163 Comparison-Policy Shadow

- Status / classification: comparison_policy_shadow_complete / comparison_policies_agree_on_reconstructable_events
- Profiles / replays: 3 / 256
- Source comparisons / reconstructable / skipped: 6912 / 1180 / 5732
- Tie-aware ties: 24
- Requirements passed/failed: 10 / 0
- Protocol/contract/executor/result/profile/transcript/report exists: True / True / True / True / True / True / True

### R164 Combine-Bound Comparison Shadow

- Status / classification: comparison_policy_shadow_complete / source_combine_bound_policy_differences_observed
- Profiles / replays: 3 / 256
- Source comparisons / reconstructable / skipped: 6912 / 6912 / 0
- Tie-aware ties / policy disagreements: 256 / 49 per alternate policy
- Requirements passed/failed: 10 / 0
- Protocol/contract/executor/result/profile/transcript/report exists: True / True / True / True / True / True / True

- Status: toy_invariant_property_test
- Model status: toy_invariant_property_test_not_full_distribution_verification
- Tasks: 3
- Configurations: 15
- Samples per trial: 4096
- Adversaries tested: 5
- Adversaries failing invariant rule: 5
- Minimum honest completeness: 1.0
- Maximum adversary soundness: 0.0
- Result exists: True
- Adaptive leakage status: adaptive_leakage_stress_test_not_full_distribution_verification
- Adaptive leakage configurations: 48
- Adaptive leakage fractions: [0.0, 0.25, 0.5, 0.75]
- Adaptive leakage maximum soundness: 0.7916666666666666
- Adaptive leakage dangerous threshold: 0.75
- Adaptive leakage result exists: True
- Challenge-refresh repair status: challenge_refresh_projection_rotation_toy_repair_not_full_distribution_verification
- Challenge-refresh repair configurations: 192
- Challenge-refresh repair modes: ['none', 'projection_rotation', 'challenge_refresh', 'refresh_plus_rotation']
- High-leakage repair modes passing: ['challenge_refresh', 'projection_rotation', 'refresh_plus_rotation']
- Challenge-refresh repair result exists: True
- Circuit refresh status: circuit_level_hidden_projection_refresh_boundary_not_quantum_advantage_claim
- Circuit refresh configurations: 192
- Circuit refresh no-refresh high-leakage max soundness: 0.675
- Circuit refresh best repaired high-leakage max soundness: 0.0
- Circuit refresh high-leakage repair modes passing: ['challenge_refresh', 'projection_rotation', 'refresh_plus_rotation']
- Circuit refresh result/markdown exists: True / True
- OpenQASM 3 packet status: openqasm3_randomized_measurement_packet_not_hardware_execution_or_advantage_claim
- OpenQASM 3 packet circuits / max qubits: 36 / 30
- OpenQASM 3 packet headers / Aer mismatches / honest completeness: True / 0 / 1.0
- OpenQASM 3 packet hardware execution / advantage / BQP separation: False / False / False
- OpenQASM 3 packet result/markdown/directory exists: True / True / True
- Public-QASM spoofer status: public_qasm_packet_spoofer_boundary_not_protocol_soundness
- Public-QASM spoofer parsed circuits / prediction success: 36 / 1.0
- Public-QASM packet soundness rejected / late-bound private challenges required: True / True
- Public-QASM spoofer hardware execution / advantage / BQP separation: False / False / False
- Public-QASM spoofer result/markdown exists: True / True
- Late-bound contract status: late_bound_private_challenge_contract_partial_not_protocol_soundness
- Late-bound public skeletons / hide private material: 36 / True
- Late-bound deterministic data blocker / late-binding alone sufficient: True / False
- Late-bound gates passed/failed: 4 / 4
- Late-bound contract result/markdown/skeleton-dir exists: True / True / True
- Non-stabilizer pilot status: nonstabilizer_late_bound_transcript_pilot_not_soundness_or_advantage
- Non-stabilizer pilot circuits / deterministic blocker removed: 36 / True
- Non-stabilizer pilot entropy / max output probability: 4.0 / 0.0625
- Non-stabilizer pilot gates passed/failed: 6 / 2
- Non-stabilizer pilot hardware execution / advantage / BQP separation: False / False / False
- Non-stabilizer pilot result/markdown/directory exists: True / True / True
- Support-spoofer gate status: support_aware_spoofer_boundary_not_protocol_soundness
- Support-spoofer circuits / spoofers / rows: 36 / 4 / 144
- Support-spoofer exact success / support acceptance: 0.0625 / 1.0
- Support-spoofer support-only soundness rejected / exact blocker survives: True / True
- Support-spoofer result/markdown exists: True / True
- Private-predicate gate status: verifier_private_predicate_pressure_not_protocol_soundness
- Private-predicate public support / hidden acceptance: 1.0 / 0.0625
- Private-predicate suppression / full leakage breaks gate: 16.0 / True
- Private-predicate result/markdown exists: True / True
- Private-challenge protocol status: formal_verifier_private_challenge_protocol_not_hardware
- Private-challenge protocol rows / gates passed-failed: 36 / 8-0
- Private-challenge support / hidden / full-leak acceptance: 0.5 / 0.0625 / 1.0
- Private-challenge hardware / protocol soundness claim: False / False
- Private-challenge result/markdown exists: True / True
- Private-challenge noise bridge status: private_challenge_noise_transcript_bridge_not_hardware
- Private-challenge noise bridge transcript cases / gates passed-failed: 720 / 8-0
- Private-challenge noise bridge backend-like honest no-refresh / challenge / rotation: 0.747047070414 / 0.805169120213 / 0.866618491942
- Private-challenge noise bridge no-leak / three-leak / full-leak acceptance: 0.0625 / 0.5 / 1.0
- Private-challenge noise bridge hardware / protocol soundness claim: False / False
- Private-challenge noise bridge result/markdown exists: True / True
- Private-challenge spoofer pressure status: parametric_spoofer_pressure_model_not_hardware
- Private-challenge spoofer pressure rows / gates passed-failed: 2880 / 6-2
- Private-challenge spoofer pressure no-leak / backend-refreshed / full-leak max acceptance: 0.1196875 / 0.109140625 / 1.0
- Private-challenge spoofer pressure actual ML / hardware / protocol soundness claim: False / False / False
- Private-challenge spoofer pressure result/markdown exists: True / True
- Private-challenge fitted spoofer status: fitted_spoofer_holdout_attack_on_synthetic_transcripts_not_hardware
- Private-challenge fitted spoofer train/holdout/eval rows: 560 / 160 / 640
- Private-challenge fitted spoofer private-safe / leakage-blind / full-leak acceptance: 0.0625 / 0.35 / 1.0
- Private-challenge fitted spoofer training / hardware / protocol soundness claim: True / False / False
- Private-challenge fitted spoofer result/markdown exists: True / True
- Real-backend transcript readiness status: real_backend_transcript_readiness_failed
- Real-backend transcript readiness passed / failed / missing gates: 5 / 5 / ['R5', 'R6', 'R7', 'R8', 'R9']
- Real-backend transcript readiness real backend / hardware / transcript rows: False / False / 0
- Real-backend transcript readiness private-safe / leakage-blind / full-leak acceptance: 0.0625 / 0.35 / 1.0
- Real-backend transcript readiness result/markdown exists: True / True
- Real-backend transcript contract status: real_backend_transcript_contract_open_missing_hardware_evidence
- Real-backend transcript contract source gates / contract failures: ['R5', 'R6', 'R7', 'R8', 'R9'] / ['K5', 'K6', 'K7', 'K8', 'K9']
- Real-backend transcript contract passed / failed / packets: 5 / 5 / 5
- Real-backend transcript contract required backend / hardware / leakage split: True / True / True
- Real-backend transcript contract readiness / soundness / advantage: False / False / False
- Real-backend transcript contract validation errors: 0
- Real-backend transcript contract result/markdown exists: True / True
- Real-backend packet scout status: real_backend_packet_scout_failed_missing_real_backend_evidence
- Real-backend packet scout passed / failed / failed IDs: 4 / 5 / ['S5', 'S6', 'S7', 'S8', 'S9']
- Real-backend packet scout packets / bridge circuits / fitted rows / holdout rows: 5 / 5760 / 640 / 160
- Real-backend packet scout backend / hardware / transcript rows / real training: False / False / 0 / False
- Real-backend packet scout leakage-blind / full-leak acceptance: 0.35 / 1.0
- Real-backend packet scout readiness / soundness / advantage: False / False / False
- Real-backend packet scout validation errors: 0
- Real-backend packet scout result/markdown exists: True / True
- Generative spoofer status: trained_generative_spoofer_refresh_boundary_not_soundness_proof
- Generative spoofer configurations: 144
- Generative spoofer maximum learned soundness: 1.0
- Generative spoofer safe high-leakage refresh modes: ['challenge_refresh', 'projection_rotation', 'refresh_plus_rotation']
- Generative spoofer unsafe high-leakage refresh modes: ['none']
- Generative spoofer result/markdown exists: True / True

## B9 Local Hamiltonian Gap Lab Status

- Status: exact_small_instance_gap_lab
- Model status: exact_small_instance_lab_not_quantum_pcp_proof
- Configurations: 18
- Locality-preserving candidates: 9
- Candidate passes: 0
- Counterexample candidates: 4
- Max local normalized-gap ratio: 1.000000000000002
- Max dense-filter raw gap ratio: 2.4142428682853314
- Result exists: True
- Failed gap-amplification lemma status: finite_instance_negative_gap_amplification_lemma_not_quantum_pcp_proof
- Failed gap-amplification theorem count: 1
- Failed gap-amplification strict counterexamples: 4
- Failed gap-amplification dense locality traps: 9
- Failed gap-amplification proof obligations: 5
- Failed gap-amplification explicitly not Quantum PCP proof: True
- Failed gap-amplification global impossibility claimed: False
- Failed gap-amplification validation errors: 0
- Failed gap-amplification result/markdown exists: True / True
- Symbolic gap skeleton status: symbolic_proof_skeleton_not_formalized_theorem
- Symbolic gap skeleton target: Lean-style skeleton
- Symbolic gap skeleton definitions/theorems: 5 / 3
- Symbolic gap skeleton open obligations: 5
- Symbolic gap skeleton checked/formal theorem: False / False
- Symbolic gap skeleton explicitly not Quantum PCP proof: True
- Symbolic gap skeleton validation errors: 0
- Symbolic gap skeleton result/markdown/lean exists: True / True / True
- Named-family bound status: named_family_width_locality_bound_skeleton_not_checked_theorem
- Named-family bound family: cluster_stabilizer_open_uniform_reweight
- Named-family bound rows/scaling/locality: 3 / 1.35 / 3
- Named-family bound uniform/locality/raw/norm-invariant/rejected: True / True / True / True / True
- Named-family bound checked/formal theorem: True / False
- Named-family bound proof-check status: passed
- Named-family bound explicitly not Quantum PCP proof: True
- Named-family bound validation errors: 0
- Named-family bound result/markdown/lean exists: True / True / True
- Parametric certificate status: parametric_certificate_checked_by_local_verifier_not_formal_theorem
- Parametric certificate family: cluster_stabilizer_open_uniform_reweight
- Parametric certificate n-min/rows: 4 / [4, 5, 6]
- Parametric certificate support/locality/scale: [2, 3] / 3 / 27/20
- Parametric certificate normalized-gap invariant/rejected: True / True
- Parametric certificate local/formal theorem: True / False
- Parametric certificate explicitly not Quantum PCP proof: True
- Parametric certificate validation errors: 0
- Parametric certificate result/markdown exists: True / True
- Proof-environment readiness status: proof_environment_readiness_blocked_not_formal_theorem
- Proof-environment readiness gates passed/total: 6 / 9
- Proof-environment failed gate IDs: ['PE-03', 'PE-04', 'PE-09']
- Proof-environment blocking obligations: 5
- Proof-environment ready/formal theorem: False / False
- Proof-environment Lean/Lake/project/placeholder: 0 / False / True / False
- Proof-environment explicitly not Quantum PCP proof: True
- Proof-environment validation errors: 0
- Proof-environment result/markdown exists: True / True
- Proof-environment contract status: proof_environment_contract_open_not_formal_theorem
- Proof-environment contract source failures / contract failures: ['PE-03', 'PE-04', 'PE-09'] / ['K4', 'K5', 'K8']
- Proof-environment contract passed / failed / packets: 5 / 3 / 3
- Proof-environment contract packet IDs: ['B9-PE03-lean-toolchain', 'B9-PE04-lake-tooling', 'B9-PE09-checked-formal-output']
- Proof-environment closed packet IDs: ['B9-PE05-mathlib-project', 'B9-PE08-indexed-theorem']
- Proof-environment contract result/markdown exists: True / True
- Proof-project scaffold status: proof_project_scaffold_open_not_checked
- Proof-project scaffold passed / failed: 6 / 2
- Proof-project scaffold failed IDs: ['S7', 'S8']
- Proof-project scaffold Lean4/Lake/checked theorem: False / False / False
- Proof-project scaffold result/markdown exists: True / True
- Toolchain CI contract status: toolchain_ci_contract_workflow_scope_blocked
- Toolchain CI contract passed / failed: 7 / 3
- Toolchain CI contract failed IDs: ['C2', 'C3', 'C10']
- Toolchain CI run artifact / formal theorem: False / False
- Toolchain CI template/result/markdown exists: True / True / True
- Disjoint Pauli action-commutation status: pauli_action_disjoint_commutation_checked_not_linear_or_spectral_proof
- Disjoint Pauli action-commutation requirements passed/failed: 11 / 0
- Disjoint Pauli action-commutation checked/proof-assistant/fresh zero commands: True / True / 3
- Disjoint Pauli action-commutation validation errors: 0
- Disjoint Pauli action-commutation result/markdown exists: True / True

## B10 BQP Boundary Graph Status

- Status: taxonomy_reduction_graph
- Model status: taxonomy_and_reduction_planning_not_complexity_theorem
- Nodes: 12
- Edges: 14
- Connected components: 2
- Advantage-preserving edges: 8
- Fragile edges: 6
- Restricted theorem targets: 11
- Top failure modes: ['data_loading', 'oracle_construction', 'protocol_overhead', 'noise', 'measurement_gap']
- Result exists: True
- Formal theorem target status: formal_theorem_targets_not_proofs
- Formal theorem target count: 2
- Formal theorem target types: ['negative_boundary', 'restricted_advantage_preservation']
- Formal theorem target dependencies: ['B10', 'B3', 'B4', 'B5', 'B8']
- Formal theorem target validation errors: 0
- Formal theorem target result exists: True
- B10-T2 refresh-boundary status: t2_minimum_refresh_boundary_from_trained_spoofer_not_soundness_proof
- B10-T2 refresh-boundary maximum learned soundness: 1.0
- B10-T2 refresh-boundary safe modes: ['challenge_refresh', 'projection_rotation', 'refresh_plus_rotation']
- B10-T2 refresh-boundary unsafe modes: ['none']
- B10-T2 refresh-boundary explicitly not BQP separation: True
- B10-T2 refresh-boundary result/markdown exists: True / True
- B10-T2 proof-gate status: proof_obligation_gate_proxy_supports_rejection_rule_not_soundness_lemma
- B10-T2 proof-gate lemma status: not_proved_proxy_insufficient_for_general_soundness
- B10-T2 proof-gate obligations: 7
- B10-T2 proof-gate unsafe modes: ['none']
- B10-T2 proof-gate hardware verifier instantiated: False
- B10-T2 proof-gate validation errors: 0
- B10-T2 proof-gate result/markdown exists: True / True
- B10-T2 restricted lemma status: restricted_soundness_lemma_proved_under_refresh_independence_model
- B10-T2 restricted lemma theorem/corollary count: 1 / 1
- B10-T2 restricted lemma single-unknown-mask bound: 8.940076013143436e-44
- B10-T2 restricted lemma hardware verifier instantiated: False
- B10-T2 restricted lemma sampling hardness proved: False
- B10-T2 restricted lemma validation errors: 0
- B10-T2 restricted lemma result/markdown exists: True / True
- B10-T2 transcript simulator status: transcript_leakage_simulator_supports_restricted_lemma_not_hardware_verifier
- B10-T2 transcript simulator configurations: 192
- B10-T2 transcript simulator honest completeness: 1.0
- B10-T2 transcript simulator max refreshed high-leakage soundness: 0.025
- B10-T2 transcript simulator min refreshed high-leakage unknown independent predicates: 6.0
- B10-T2 transcript simulator unsafe modes: ['none']
- B10-T2 transcript simulator hardware verifier instantiated: False
- B10-T2 transcript simulator sampling hardness proved: False
- B10-T2 transcript simulator validation errors: 0
- B10-T2 transcript simulator result/markdown exists: True / True
- B10-T2 device-noise bridge status: device_noise_transcript_bridge_supports_bounded_noise_not_hardware_verifier
- B10-T2 device-noise bridge configurations/profiles: 480 / 5
- B10-T2 device-noise bridge safe refresh modes: ['challenge_refresh', 'refresh_plus_rotation']
- B10-T2 device-noise bridge max safe high-leakage soundness: 0.020833333333333332
- B10-T2 device-noise bridge margin-sensitive modes: ['projection_rotation']
- B10-T2 device-noise bridge unsafe profiles: ['calibration_side_channel']
- B10-T2 device-noise bridge hardware verifier instantiated: False
- B10-T2 device-noise bridge validation errors: 0
- B10-T2 device-noise bridge result/markdown exists: True / True
- B10-T2 Qiskit/Aer bridge status: qiskit_aer_circuit_level_verifier_bridge_not_hardware_execution
- B10-T2 Qiskit/Aer bridge circuits: 216
- B10-T2 Qiskit/Aer bridge max qubits incl. ancilla: 30
- B10-T2 Qiskit/Aer bridge semantic mismatches: 0
- B10-T2 Qiskit/Aer bridge honest completeness: 1.0
- B10-T2 Qiskit/Aer bridge source soundness: 0.020833333333333332
- B10-T2 Qiskit/Aer bridge hardware circuits instantiated: True
- B10-T2 Qiskit/Aer bridge hardware execution performed: False
- B10-T2 Qiskit/Aer bridge validation errors: 0
- B10-T2 Qiskit/Aer bridge result/markdown exists: True / True
- B10-T2 noisy Aer bridge status: noisy_aer_circuit_verifier_bridge_not_hardware_execution
- B10-T2 noisy Aer bridge circuits: 9600
- B10-T2 noisy Aer bridge max qubits incl. ancilla: 22
- B10-T2 noisy Aer bridge safe honest/adversary acceptance: 1.0 / 0.0
- B10-T2 noisy Aer bridge honest predicate-bit error: 0.1125
- B10-T2 noisy Aer bridge safe unknown predicates: 7.0
- B10-T2 noisy Aer bridge unsafe profiles: ['calibration_side_channel']
- B10-T2 noisy Aer bridge hardware execution performed: False
- B10-T2 noisy Aer bridge validation errors: 0
- B10-T2 noisy Aer bridge result/markdown exists: True / True
- B10-T2 backend-calibrated bridge status: backend_calibrated_aer_verifier_bridge_not_hardware_execution
- B10-T2 backend-calibrated bridge circuits: 5760
- B10-T2 backend-calibrated bridge max qubits incl. ancilla: 22
- B10-T2 backend-calibrated bridge safe honest/adversary acceptance: 1.0 / 0.25
- B10-T2 backend-calibrated bridge honest predicate-bit error: 0.0703125
- B10-T2 backend-calibrated bridge safe unknown predicates: 7.0
- B10-T2 backend-calibrated bridge unsafe refresh modes: ['none']
- B10-T2 backend-calibrated bridge GenericBackendV2 used: True
- B10-T2 backend-calibrated bridge real backend properties used: False
- B10-T2 backend-calibrated bridge hardware execution performed: False
- B10-T2 backend-calibrated bridge validation errors: 0
- B10-T2 backend-calibrated bridge result/markdown exists: True / True
- B10-T1 proof status: negative_boundary_accounting_lemma_proved_under_explicit_io_model_not_bqp_separation
- B10-T1 proof result: restricted_negative_boundary_accounting_lemma
- B10-T1 theorem count: 2
- B10-T1 open obligations: 3
- B10-T1 validation errors: 0
- B10-T1 explicitly not BQP separation: True
- B10-T1 result exists: True
- B10-T1 source-backed status: source_backed_denominator_baselines_instantiated_not_publishable_theorem
- B10-T1 source count: 6
- B10-T1 denominator baselines: 5
- B10-T1 boundary checks: 4
- B10-T1 source-backed validation errors: 0
- B10-T1 source-backed explicitly not BQP separation: True
- B10-T1 source-backed result exists: True
- B10-T1 numerical-table status: numerical_denominator_table_instantiated_not_quantum_speedup_claim
- B10-T1 numerical-table families: 2
- B10-T1 numerical-table instances: 16
- B10-T1 numerical-table CG instances: 12
- B10-T1 numerical-table LSQR instances: 4
- B10-T1 numerical-table max residual: 3.885650409058836e-06
- B10-T1 numerical-table validation errors: 0
- B10-T1 numerical-table explicitly not BQP separation: True
- B10-T1 numerical-table result exists: True
- B10-T1 D5 table status: d5_observable_denominator_table_instantiated_not_quantum_speedup_claim
- B10-T1 D5 table dependency: B5
- B10-T1 D5 table instances: 9
- B10-T1 D5 table max Hilbert dimension: 4900
- B10-T1 D5 table max residual: 9.788055078561953e-09
- B10-T1 D5 table validation errors: 0
- B10-T1 D5 table explicitly not BQP separation: True
- B10-T1 D5 table result exists: True
- B10-T1 D5-B3 table status: b3_d5_molecular_observable_denominator_proxy_not_reaction_solution
- B10-T1 D5-B3 table dependency: B3
- B10-T1 D5-B3 table instances: 4
- B10-T1 D5-B3 table max matrix dimension: 160
- B10-T1 D5-B3 table max residual: 9.151682258593394e-09
- B10-T1 D5-B3 table validation errors: 0
- B10-T1 D5-B3 table explicitly not BQP separation: True
- B10-T1 D5-B3 table result exists: True
- B10-T1 D5-B3 reaction table status: hamiltonian_derived_b3_reaction_observable_denominator_not_reaction_solution
- B10-T1 D5-B3 reaction table dependency: B3
- B10-T1 D5-B3 reaction table instances: 4
- B10-T1 D5-B3 reaction table max response dimension: 21
- B10-T1 D5-B3 reaction table max residual: 3.154302814054436e-13
- B10-T1 D5-B3 reaction table validation errors: 0
- B10-T1 D5-B3 reaction table explicitly not BQP separation: True
- B10-T1 D5-B3 reaction table result exists: True
- B10-T1 D5-B3 correlated table status: correlated_b3_reaction_references_instantiated_not_quantum_advantage_claim
- B10-T1 D5-B3 correlated table dependency: B3
- B10-T1 D5-B3 correlated table instances: 4
- B10-T1 D5-B3 correlated table methods: 3
- B10-T1 D5-B3 correlated table max |CCSD-RHF derivative shift|: 0.2817594828918857
- B10-T1 D5-B3 correlated table validation errors: 0
- B10-T1 D5-B3 correlated table explicitly not BQP separation: True
- B10-T1 D5-B3 correlated table result exists: True
- B10-T1 D5-B3 FCI table status: fci_b3_reaction_references_instantiated_not_quantum_advantage_claim
- B10-T1 D5-B3 FCI table dependency: B3
- B10-T1 D5-B3 FCI table instances: 4
- B10-T1 D5-B3 FCI table methods: 4
- B10-T1 D5-B3 FCI table max |FCI-RHF derivative shift|: 0.2980126599013033
- B10-T1 D5-B3 FCI table max |FCI-CCSD derivative shift|: 0.01625317700941764
- B10-T1 D5-B3 FCI table validation errors: 0
- B10-T1 D5-B3 FCI table explicitly not BQP separation: True
- B10-T1 D5-B3 FCI table result exists: True
- B10-T1 B3/B5 denominator comparison status: b3_b5_denominator_boundary_comparison_not_bqp_separation
- B10-T1 B3/B5 routes / negative-boundary routes: 4 / 1
- B10-T1 B3 denominator wins / max optimizer-loop shots: 0 / 475043013690000
- B10-T1 B5 non-oracle wins / seeded MPS wins / variational-over-seeded wins: 4 / 6 / 0
- B10-T1 B3 demoted / B5 positive-ready / BQP separation / quantum advantage: True / False / False / False
- B10-T1 B3/B5 comparison validation errors: 0
- B10-T1 B3/B5 comparison result/markdown exists: True / True
- B10-T1 B3 same-access rescue status: same_access_measurement_rescue_failed_not_advantage_claim
- B10-T1 B3 same-access gates passed/failed: 5 / 5
- B10-T1 B3 same-access failed gates: ['M5', 'M6', 'M7', 'M8', 'M9']
- B10-T1 B3 same-access rescue ready / B3 demoted: False / True
- B10-T1 B3 same-access validation errors: 0
- B10-T1 B3 same-access result/markdown exists: True / True
- B10-T1 B3 negative boundary status: same_access_negative_boundary_note_not_advantage_claim
- B10-T1 B3 negative boundary conditions satisfied/unsatisfied: 9 / 0
- B10-T1 B3 negative boundary demoted / positive route: True / False
- B10-T1 B3 negative boundary result/markdown exists: True / True
- B10-T1 missing-assumption note status: missing_assumption_note_not_dequantization_theorem
- B10-T1 missing-assumption theorem skeletons / missing assumptions / proof obligations: 2 / 5 / 5
- B10-T1 missing-assumption dequantization theorem / sampling-access theorem / BQP separation / quantum advantage: False / False / False / False
- B10-T1 missing-assumption validation errors: 0
- B10-T1 missing-assumption result/markdown exists: True / True
- B10-T1 asymptotic access status: access_contract_skeleton_sampling_bridge_refuted_for_current_evidence
- B10-T1 asymptotic families / access rows / bridge conditions: 2 / 8 / 5
- B10-T1 sampling bridge proved / refuted for current evidence: False / True
- B10-T1 general dequantization theorem / sampling-access theorem / BQP separation / quantum advantage: False / False / False / False
- B10-T1 asymptotic access validation errors: 0
- B10-T1 asymptotic access result/markdown exists: True / True
- B10-T1 B5 same-access bridge status: b5_same_access_sampling_oracle_not_constructed_dmrg_required
- B10-T1 B5 denominator ladder / sampling requirements / blocking requirements: 4 / 5 / 5
- B10-T1 B5 seeded-MPS-over-non-oracle / variational-over-seeded rows: 6 / 0
- B10-T1 B5 sampling oracle / production DMRG / same-access positive route: False / False / False
- B10-T1 B5 dequantization theorem / sampling-access theorem / BQP separation / quantum advantage: False / False / False / False
- B10-T1 B5 same-access bridge validation errors: 0
- B10-T1 B5 same-access bridge result/markdown exists: True / True
- B10-T1 B5 response sampler stress status: b5_response_sampler_cost_stress_no_positive_same_access_route
- B10-T1 B5 response sampler stress instances / confidence z: 9 / 2.576
- B10-T1 B5 response sampler stress min/median/max shots to match seeded MPS: 3861425434 / 7644706432712 / 284916076006665507134714675200
- B10-T1 B5 response sampler stress max seeded-target prep 2Q floor: 1139664304026662028538858700800
- B10-T1 B5 response sampler stress rows beating D5 matvec ops for seeded target: 0
- B10-T1 B5 response sampler stress sampling oracle / same-access positive route / quantum advantage: False / False / False
- B10-T1 B5 response sampler stress validation errors: 0
- B10-T1 B5 response sampler stress result/markdown exists: True / True
- B10-T1 B5 production triage status: production_implementation_triage_ready_no_positive_route
- B10-T1 B5 production triage work packets ready/blocked: 2 / 4
- B10-T1 B5 production triage conditions satisfied/unsatisfied: 6 / 0
- B10-T1 B5 production triage DMRG / oracle / positive route / catalog change: False / False / False / False
- B10-T1 B5 production triage result/markdown exists: True / True
- B10-T1 B5 row-contract harness status: row_contract_preserved_guardrail_ready
- B10-T1 B5 row-contract harness rows/hash: 9 / 7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc
- B10-T1 B5 row-contract harness source checks passed/failed: 10 / 0
- B10-T1 B5 row-contract harness remaining positive-route packets: ['W1', 'W2', 'W3']
- B10-T1 B5 row-contract harness result/markdown exists: True / True
- B10-T1 B5 seeded-pressure replacement audit status: seeded_pressure_replacement_failed_remains_blocker
- B10-T1 B5 seeded-pressure replacement audit seeded/best mean error: 0.0004416259745141553 / 0.01805548365563228
- B10-T1 B5 seeded-pressure replacement audit deployable replacements / seeded replaced: 0 / False
- B10-T1 B5 seeded-pressure replacement audit remaining positive-route packets: ['W1', 'W3']
- B10-T1 B5 seeded-pressure replacement audit result/markdown exists: True / True
- B10-T1 B5 response-oracle cost ledger status: same_access_response_oracle_cost_ledger_failed_no_oracle
- B10-T1 B5 response-oracle cost ledger requirements passed/failed: 3 / 5
- B10-T1 B5 response-oracle cost ledger failed IDs: ['O3', 'O4', 'O5', 'O6', 'O7']
- B10-T1 B5 response-oracle cost ledger oracle constructed / remaining packets: False / ['W1']
- B10-T1 B5 response-oracle cost ledger result/markdown exists: True / True
- B10-T1 B5 W1 production DMRG/MPS acceptance status: production_dmrg_mps_acceptance_gate_failed_no_w1_denominator
- B10-T1 B5 W1 production DMRG/MPS requirements passed/failed: 3 / 7
- B10-T1 B5 W1 production DMRG/MPS failed IDs: ['D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9']
- B10-T1 B5 W1 production DMRG/MPS denominator available / remaining packets: False / ['W1']
- B10-T1 B5 W1 production DMRG/MPS result/markdown exists: True / True
- B10-T1 B5 W1 denominator engine status: w1_denominator_engine_v0_failed_not_production_dmrg
- B10-T1 B5 W1 denominator engine requirements passed/failed: 4 / 4
- B10-T1 B5 W1 denominator engine failed IDs: ['E4', 'E5', 'E6', 'E7']
- B10-T1 B5 W1 denominator engine convergence / seeded wins: 0 / 0
- B10-T1 B5 W1 denominator engine result/markdown exists: True / True
- B10-T1 B5 W1 canonical residual blocker status: w1_canonical_residual_blocker_gate_failed_missing_production_evidence
- B10-T1 B5 W1 canonical residual blocker requirements passed/failed: 4 / 4
- B10-T1 B5 W1 canonical residual blocker failed IDs: ['C3', 'C4', 'C5', 'C7']
- B10-T1 B5 W1 canonical residual blocker PR packets: 4
- B10-T1 B5 W1 canonical residual blocker result/markdown exists: True / True
- B10-T1 B5 W1 implementation contract status: w1_implementation_contract_open_not_production_dmrg
- B10-T1 B5 W1 implementation contract requirements passed/failed: 5 / 5
- B10-T1 B5 W1 implementation contract failed IDs: ['K5', 'K6', 'K7', 'K8', 'K9']
- B10-T1 B5 W1 implementation contract packets: ['W1-E4-env-residuals', 'W1-E5-convergence', 'W1-E6-seeded-pressure', 'W1-E7-cost-ledger']
- B10-T1 B5 W1 implementation contract result/markdown exists: True / True
- B10-T1 B5 W1 prototype environment scout status: w1_prototype_environment_scout_failed_not_canonical_contract
- B10-T1 B5 W1 prototype environment scout requirements passed/failed: 5 / 3
- B10-T1 B5 W1 prototype environment scout failed IDs: ['P5', 'P6', 'P7']
- B10-T1 B5 W1 prototype/contract env rows: 9 / 0
- B10-T1 B5 W1 prototype scout result/markdown exists: True / True
- B10-T1 B5 W1 production-row intake status: w1_production_row_intake_template_open_missing_submitted_rows
- B10-T1 B5 W1 production-row intake requirements passed/failed: 5 / 3
- B10-T1 B5 W1 production-row intake failed IDs: ['I5', 'I6', 'I7']
- B10-T1 B5 W1 production-row intake templates / production keys / missing keys: 9 / 8 / 72
- B10-T1 B5 W1 production-row intake result/markdown exists: True / True

## Errors

- None

## Warnings

- None
