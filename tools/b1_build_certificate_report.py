#!/usr/bin/env python3
"""Build the B1 circuit-compression certificate evidence report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


PROOFLOG_KEYS = [
    "qasmbench_small_fixed_point_pipeline_with_proof_logs_v0",
    "b1_exact_extension_fixed_point_pipeline_v0",
    "qasmbench_interaction_stress_hhl_n10_with_proof_logs_v0",
]

EXACT_AGGREGATE_KEY = "b1_30_circuit_exact_aggregate_fixed_point_pipeline_v0"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def percent(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}%"


def resolve_from_benchmarks(root: Path, value: str) -> Path:
    return (root / "benchmarks" / value).resolve()


def result_row(root: Path, manifest_row: dict) -> dict:
    summary_path = resolve_from_benchmarks(root, manifest_row["summary"])
    summary = read_json(summary_path)
    audit = read_json(resolve_from_benchmarks(root, manifest_row["audit"]))
    replay = read_json(resolve_from_benchmarks(root, manifest_row["replay"]))
    semantic = read_json(resolve_from_benchmarks(root, manifest_row["semantic"]))
    oneq = semantic["single_qubit"]
    rzz = semantic["rzz"]
    proof_events = {
        "single_qubit": int(oneq["count"]),
        "rzz": int(rzz["count"]),
        "total": int(oneq["count"]) + int(rzz["count"]),
    }
    return {
        "key": manifest_row["key"],
        "summary_path": str(summary_path.relative_to(root)),
        "audit_path": str(resolve_from_benchmarks(root, manifest_row["audit"]).relative_to(root)),
        "replay_path": str(resolve_from_benchmarks(root, manifest_row["replay"]).relative_to(root)),
        "semantic_path": str(resolve_from_benchmarks(root, manifest_row["semantic"]).relative_to(root)),
        "circuit_count": summary["circuit_count"],
        "method": summary["method"],
        "profile": summary["profile"],
        "equivalence_mode": summary["equivalence_mode"],
        "equivalence_passed": summary["equivalence_passed"],
        "equivalence_failed": summary["equivalence_failed"],
        "certificate_mode": summary["certificate_mode"],
        "audit_passed": bool(audit["passed"]),
        "replay_passed": bool(replay["passed"]),
        "semantic_passed": bool(semantic["passed"]),
        "operation_count_reduction_pct": summary["operation_count_reduction_pct"],
        "two_qubit_gate_count_reduction_pct": summary["two_qubit_gate_count_reduction_pct"],
        "logical_depth_reduction_pct": summary["logical_depth_reduction_pct"],
        "hardware_weighted_exposure_reduction_pct": summary["hardware_weighted_exposure_reduction_pct"],
        "proof_events": proof_events,
        "semantic_max_delta": {
            "single_qubit": oneq["max_delta"],
            "rzz": rzz["max_delta"],
        },
        "semantic_breakdown": {
            "single_qubit_rules": oneq.get("rules", {}),
            "rzz_modes": rzz.get("modes", {}),
        },
        "replay_stages": replay["stages"],
    }


def build_report(root: Path) -> dict:
    manifest_path = root / "benchmarks" / "B1_circuit_compression.yaml"
    ablation_path = root / "research" / "B1_ablation_report.json"
    baseline_comparison_path = root / "research" / "B1_baseline_comparison.json"
    routing_diagnostic_path = root / "research" / "B1_routing_baseline_diagnostic.json"
    heavyhex_diagnostic_path = root / "research" / "B1_heavyhex_routing_diagnostic.json"
    heavyhex_e2e_path = root / "research" / "B1_heavyhex_end_to_end_report.json"
    heavyhex_e2e_suite_path = root / "research" / "B1_heavyhex_end_to_end_suite.json"
    post_routing_profile_path = root / "research" / "B1_post_routing_bottleneck_profile.json"
    swap_macro_path = root / "research" / "B1_post_routing_swap_macro_report.json"
    virtual_swap_path = root / "research" / "B1_virtual_swap_elimination_report.json"
    virtual_swap_replay_path = root / "research" / "B1_virtual_swap_replay_report.json"
    synthetic_noise_path = root / "research" / "B1_synthetic_noise_proxy_report.json"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    current_results = manifest["current_results"]
    rows = []
    for key in PROOFLOG_KEYS:
        manifest_row = dict(current_results[key])
        manifest_row["key"] = key
        rows.append(result_row(root, manifest_row))

    aggregate_summary_path = resolve_from_benchmarks(root, current_results[EXACT_AGGREGATE_KEY]["summary"])
    aggregate = read_json(aggregate_summary_path)
    exact_subsets = aggregate.get("subsets", [])
    exact_circuit_count = int(aggregate["aggregate_circuit_count"])
    exact_equivalence_failed = int(aggregate["aggregate_equivalence_failed"])
    stress_row = next(row for row in rows if row["equivalence_mode"] == "skipped")
    small_row = next(row for row in rows if row["equivalence_mode"] == "exact_statevector")
    ablation = read_json(ablation_path) if ablation_path.exists() else None
    baseline_comparison = read_json(baseline_comparison_path) if baseline_comparison_path.exists() else None
    routing_diagnostic = read_json(routing_diagnostic_path) if routing_diagnostic_path.exists() else None
    heavyhex_diagnostic = read_json(heavyhex_diagnostic_path) if heavyhex_diagnostic_path.exists() else None
    heavyhex_e2e = read_json(heavyhex_e2e_path) if heavyhex_e2e_path.exists() else None
    heavyhex_e2e_suite = read_json(heavyhex_e2e_suite_path) if heavyhex_e2e_suite_path.exists() else None
    post_routing_profile = read_json(post_routing_profile_path) if post_routing_profile_path.exists() else None
    swap_macro = read_json(swap_macro_path) if swap_macro_path.exists() else None
    virtual_swap = read_json(virtual_swap_path) if virtual_swap_path.exists() else None
    virtual_swap_replay = read_json(virtual_swap_replay_path) if virtual_swap_replay_path.exists() else None
    synthetic_noise = read_json(synthetic_noise_path) if synthetic_noise_path.exists() else None

    gates = {
        "minimum_circuit_count": {
            "target": int(str(manifest["acceptance_threshold"]["minimum_circuit_count"])),
            "current_exact_circuit_count": exact_circuit_count,
            "passed": exact_circuit_count >= int(str(manifest["acceptance_threshold"]["minimum_circuit_count"])),
        },
        "exact_equivalence_failures": {
            "target": int(str(manifest["acceptance_threshold"]["equivalence_failures"])),
            "current_exact_failures": exact_equivalence_failed,
            "passed": exact_equivalence_failed == int(str(manifest["acceptance_threshold"]["equivalence_failures"])),
        },
        "stress_hardware_exposure_reduction": {
            "target": ">=20% on at least one stress circuit",
            "current": stress_row["hardware_weighted_exposure_reduction_pct"],
            "passed": stress_row["hardware_weighted_exposure_reduction_pct"] >= 20.0,
        },
        "aggregate_hardware_exposure_reduction": {
            "target": ">=20% on the exact aggregate",
            "current": aggregate["aggregate_hardware_weighted_exposure_reduction_pct"],
            "passed": aggregate["aggregate_hardware_weighted_exposure_reduction_pct"] >= 20.0,
        },
        "proof_log_verification": {
            "target": "audit, replay, and semantic checks pass for proof-log runs",
            "current": f"{len(rows)} proof-log runs passed audit/replay/semantic checks",
            "passed": all(row["audit_passed"] and row["replay_passed"] and row["semantic_passed"] for row in rows),
        },
        "ablation_table": {
            "target": "30-circuit ablation table separating 1Q, adjacent RZZ, and final passes",
            "current": "present" if ablation else "missing",
            "passed": bool(ablation and ablation.get("circuit_count") == exact_circuit_count),
        },
        "baseline_comparison": {
            "target": "at least one exact-valid independent compiler baseline comparison",
            "current": "present" if baseline_comparison else "missing",
            "passed": bool(
                baseline_comparison
                and baseline_comparison.get("best_valid_qiskit_by_exposure", {}).get("equivalence_failed") == 0
            ),
        },
        "routing_diagnostic": {
            "target": "routing-aware diagnostic is recorded without being promoted to a validated baseline",
            "current": routing_diagnostic.get("report_status") if routing_diagnostic else "missing",
            "passed": bool(
                routing_diagnostic
                and routing_diagnostic.get("report_status") == "diagnostic_only_not_validated_baseline"
            ),
        },
        "routing_aware_calibrated_heavy_hex_baseline": {
            "target": "validated calibrated heavy-hex routing baseline",
            "current": "heavy-hex topology diagnostic exists; no calibrated noise/device baseline",
            "passed": False,
        },
        "heavyhex_topology_diagnostic": {
            "target": "device-like heavy-hex topology routing diagnostic is recorded without calibrated-noise overclaiming",
            "current": heavyhex_diagnostic.get("report_status") if heavyhex_diagnostic else "missing",
            "passed": bool(
                heavyhex_diagnostic
                and heavyhex_diagnostic.get("report_status")
                == "device_like_topology_diagnostic_not_calibrated_noise_baseline"
                and heavyhex_diagnostic.get("aer_crosscheck_all_passed") is True
            ),
        },
        "heavyhex_end_to_end_routed_benefit": {
            "target": "source-routed vs B1-routed heavy-hex diagnostic suite with output cross-check",
            "current": heavyhex_e2e_suite.get("report_status") if heavyhex_e2e_suite else "missing",
            "passed": bool(
                heavyhex_e2e_suite
                and heavyhex_e2e_suite.get("report_status")
                == "topology_routed_benefit_suite_not_calibrated_noise_claim"
                and heavyhex_e2e_suite.get("all_aer_crosschecks_passed") is True
            ),
        },
        "post_routing_bottleneck_profile": {
            "target": "per-circuit diagnosis of routed-benefit erasure and 2Q bottlenecks",
            "current": post_routing_profile.get("report_status") if post_routing_profile else "missing",
            "passed": bool(
                post_routing_profile
                and post_routing_profile.get("report_status")
                == "post_routing_bottleneck_profile_diagnostic_not_calibrated_noise_claim"
                and post_routing_profile.get("all_aer_crosschecks_passed") is True
            ),
        },
        "post_routing_swap_macro_compression": {
            "target": "routing-aware post-routing SWAP macro compression diagnostic with output cross-checks",
            "current": swap_macro.get("report_status") if swap_macro else "missing",
            "passed": bool(
                swap_macro
                and swap_macro.get("report_status")
                == "post_routing_swap_macro_diagnostic_not_native_basis_claim"
                and swap_macro.get("local_aer_crosscheck", {}).get("failed") == 0
                and swap_macro.get("end_to_end_aer_crosscheck", {}).get("failed") == 0
            ),
        },
        "virtual_swap_elimination": {
            "target": "post-routing virtual SWAP elimination with wire-permutation tracking and output cross-checks",
            "current": virtual_swap.get("report_status") if virtual_swap else "missing",
            "passed": bool(
                virtual_swap
                and virtual_swap.get("report_status")
                == "virtual_swap_elimination_diagnostic_not_layout_final_claim"
                and virtual_swap.get("local_aer_crosscheck", {}).get("failed") == 0
                and virtual_swap.get("end_to_end_aer_crosscheck", {}).get("failed") == 0
            ),
        },
        "virtual_swap_proof_replay": {
            "target": "virtual-SWAP proof log replays all removed SWAPs and reconstructs generated QASM",
            "current": virtual_swap_replay.get("report_status") if virtual_swap_replay else "missing",
            "passed": bool(
                virtual_swap_replay
                and virtual_swap_replay.get("report_status") == "passed"
                and virtual_swap_replay.get("proof_events") == virtual_swap_replay.get("replayed_events")
                and virtual_swap_replay.get("output_mismatches") == 0
                and virtual_swap_replay.get("error_count") == 0
            ),
        },
        "synthetic_heavyhex_noise_proxy": {
            "target": "documented synthetic heavy-hex-like noise proxy with source-routed vs virtual-SWAP comparison",
            "current": synthetic_noise.get("report_status") if synthetic_noise else "missing",
            "passed": bool(
                synthetic_noise
                and synthetic_noise.get("report_status") == "synthetic_noise_proxy_not_calibrated_device_claim"
                and synthetic_noise.get("best_comparison_by_exposure_reduction")
                == "source_level1_routed_vs_virtual_swap"
            ),
        },
        "global_equivalence_scope": {
            "target": "global exact equivalence or scalable verifier for all claimed circuits",
            "current": "exact for small/medium/interaction aggregate; skipped for hhl_n10 stress",
            "passed": False,
        },
    }

    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "Certified hardware-aware quantum circuit compression evidence package",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "report_status": "evidence_package_not_final_claim",
        "manifest": str(manifest_path.relative_to(root)),
        "method": "fixed_point_commuting_1q_plus_iterative_rzz_v0",
        "claim_supported_now": (
            "The current pipeline can produce replayable local rewrite proof logs "
            "with semantic identity checks, exact statevector validation on a "
            "30-circuit aggregate, and a 20.30% heavy-hex-like exposure reduction "
            "on one large interaction stress circuit."
        ),
        "claim_not_supported_yet": [
            "No global exact equivalence proof for the hhl_n10 stress run.",
            "No routing-aware calibrated heavy-hex baseline has been added yet; the current validated Qiskit baseline is all-to-all u3/cx, while line-routing and heavy-hex topology results are diagnostic-only.",
            "No MQT Bench subset has been added yet; the new 12-circuit extension is generated and must be paired with more external benchmarks.",
            "The 30-circuit aggregate heavy-hex-like exposure reduction is 12.58%, below the 20% portfolio target.",
        ],
        "prooflog_results": rows,
        "exact_aggregate": {
            "summary_path": str(aggregate_summary_path.relative_to(root)),
            "circuit_count": exact_circuit_count,
            "equivalence_failed": exact_equivalence_failed,
            "operation_count_reduction_pct": aggregate["aggregate_operation_count_reduction_pct"],
            "two_qubit_gate_count_reduction_pct": aggregate["aggregate_two_qubit_gate_count_reduction_pct"],
            "logical_depth_reduction_pct": aggregate["aggregate_logical_depth_reduction_pct"],
            "hardware_weighted_exposure_reduction_pct": aggregate[
                "aggregate_hardware_weighted_exposure_reduction_pct"
            ],
            "subsets": exact_subsets,
        },
        "gates": gates,
        "ablation": {
            "path": str(ablation_path.relative_to(root)),
            "exists": ablation is not None,
            "largest_hardware_exposure_contributor": ablation.get("interpretation", {}).get("largest_hardware_exposure_contributor") if ablation else None,
            "largest_depth_contributor": ablation.get("interpretation", {}).get("largest_depth_contributor") if ablation else None,
        },
        "baseline_comparison": {
            "path": str(baseline_comparison_path.relative_to(root)),
            "exists": baseline_comparison is not None,
            "best_valid_qiskit_level": baseline_comparison.get("best_valid_qiskit_by_exposure", {}).get("optimization_level") if baseline_comparison else None,
            "b1_minus_best_valid_qiskit_exposure_pct": baseline_comparison.get("b1_minus_best_valid_qiskit", {}).get("hardware_weighted_exposure_reduction_pct") if baseline_comparison else None,
            "invalid_qiskit_levels": baseline_comparison.get("baseline_suite", {}).get("invalid_optimization_levels") if baseline_comparison else None,
        },
        "routing_diagnostic": {
            "path": str(routing_diagnostic_path.relative_to(root)),
            "exists": routing_diagnostic is not None,
            "status": routing_diagnostic.get("report_status") if routing_diagnostic else None,
            "full_exact_valid_baseline": routing_diagnostic.get("full_exact_valid_baseline") if routing_diagnostic else None,
            "full_measurement_distribution_valid_baseline": routing_diagnostic.get("full_measurement_distribution_valid_baseline") if routing_diagnostic else None,
            "partial_measurement_distribution_levels": routing_diagnostic.get("measurement_distribution_partial_valid_levels") if routing_diagnostic else None,
            "common_measurement_distribution_failures": routing_diagnostic.get("common_measurement_distribution_failures") if routing_diagnostic else None,
            "aer_crosscheck_all_passed": routing_diagnostic.get("aer_crosscheck", {}).get("all_passed") if routing_diagnostic else None,
            "aer_crosscheck_total_pairs": routing_diagnostic.get("aer_crosscheck", {}).get("total_pairs") if routing_diagnostic else None,
            "aer_crosscheck_max_tvd": routing_diagnostic.get("aer_crosscheck", {}).get("max_total_variation_distance") if routing_diagnostic else None,
            "best_diagnostic_exposure_reduction_pct": routing_diagnostic.get("best_diagnostic_exposure_reduction_pct") if routing_diagnostic else None,
        },
        "heavyhex_diagnostic": {
            "path": str(heavyhex_diagnostic_path.relative_to(root)),
            "exists": heavyhex_diagnostic is not None,
            "status": heavyhex_diagnostic.get("report_status") if heavyhex_diagnostic else None,
            "distance": heavyhex_diagnostic.get("distance") if heavyhex_diagnostic else None,
            "physical_qubits": heavyhex_diagnostic.get("physical_qubits") if heavyhex_diagnostic else None,
            "aer_crosscheck_all_passed": heavyhex_diagnostic.get("aer_crosscheck_all_passed") if heavyhex_diagnostic else None,
            "aer_crosscheck_valid_levels": heavyhex_diagnostic.get("aer_crosscheck_valid_levels") if heavyhex_diagnostic else None,
            "best_diagnostic_exposure_reduction_pct": heavyhex_diagnostic.get("best_diagnostic_exposure_reduction_pct") if heavyhex_diagnostic else None,
        },
        "heavyhex_end_to_end": {
            "path": str(heavyhex_e2e_path.relative_to(root)),
            "exists": heavyhex_e2e is not None,
            "status": heavyhex_e2e.get("report_status") if heavyhex_e2e else None,
            "aer_crosscheck_passed": heavyhex_e2e.get("aer_crosscheck_passed") if heavyhex_e2e else None,
            "aer_crosscheck_failed": heavyhex_e2e.get("aer_crosscheck_failed") if heavyhex_e2e else None,
            "operation_count_reduction_pct": heavyhex_e2e.get("operation_count_reduction_pct") if heavyhex_e2e else None,
            "two_qubit_gate_count_reduction_pct": heavyhex_e2e.get("two_qubit_gate_count_reduction_pct") if heavyhex_e2e else None,
            "logical_depth_reduction_pct": heavyhex_e2e.get("logical_depth_reduction_pct") if heavyhex_e2e else None,
            "hardware_weighted_exposure_reduction_pct": heavyhex_e2e.get("hardware_weighted_exposure_reduction_pct") if heavyhex_e2e else None,
            "idle_layer_proxy_reduction_pct": heavyhex_e2e.get("idle_layer_proxy_reduction_pct") if heavyhex_e2e else None,
        },
        "heavyhex_end_to_end_suite": {
            "path": str(heavyhex_e2e_suite_path.relative_to(root)),
            "exists": heavyhex_e2e_suite is not None,
            "status": heavyhex_e2e_suite.get("report_status") if heavyhex_e2e_suite else None,
            "levels_tested": heavyhex_e2e_suite.get("levels_tested") if heavyhex_e2e_suite else None,
            "all_aer_crosschecks_passed": heavyhex_e2e_suite.get("all_aer_crosschecks_passed") if heavyhex_e2e_suite else None,
            "best_level_by_exposure": heavyhex_e2e_suite.get("best_level_by_exposure") if heavyhex_e2e_suite else None,
            "best_exposure_reduction_pct": heavyhex_e2e_suite.get("best_exposure_reduction_pct") if heavyhex_e2e_suite else None,
            "levels": heavyhex_e2e_suite.get("levels") if heavyhex_e2e_suite else None,
        },
        "post_routing_bottleneck_profile": {
            "path": str(post_routing_profile_path.relative_to(root)),
            "exists": post_routing_profile is not None,
            "status": post_routing_profile.get("report_status") if post_routing_profile else None,
            "levels_tested": post_routing_profile.get("levels_tested") if post_routing_profile else None,
            "all_aer_crosschecks_passed": post_routing_profile.get("all_aer_crosschecks_passed") if post_routing_profile else None,
            "level0_exposure_reduction_pct": post_routing_profile.get("level_summary", {}).get("0", {}).get(
                "hardware_weighted_exposure_reduction_pct"
            )
            if post_routing_profile
            else None,
            "level1_exposure_reduction_pct": post_routing_profile.get("level_summary", {}).get("1", {}).get(
                "hardware_weighted_exposure_reduction_pct"
            )
            if post_routing_profile
            else None,
            "erased_circuit_count": post_routing_profile.get("bottlenecks", {}).get("erased_circuit_count")
            if post_routing_profile
            else None,
            "top_level1_two_qubit_bottleneck": (
                post_routing_profile.get("bottlenecks", {})
                .get("level1_two_qubit_bottlenecks", [{}])[0]
                .get("circuit")
            )
            if post_routing_profile
            else None,
        },
        "post_routing_swap_macro": {
            "path": str(swap_macro_path.relative_to(root)),
            "exists": swap_macro is not None,
            "status": swap_macro.get("report_status") if swap_macro else None,
            "swap_macros": swap_macro.get("swap_macros") if swap_macro else None,
            "removed_cx_gates": swap_macro.get("removed_cx_gates") if swap_macro else None,
            "two_qubit_reduction_pct": swap_macro.get("metrics", {}).get("two_qubit_gate_count", {}).get(
                "reduction_pct"
            )
            if swap_macro
            else None,
            "exposure_reduction_pct": swap_macro.get("metrics", {})
            .get("hardware_weighted_error_exposure", {})
            .get("reduction_pct")
            if swap_macro
            else None,
            "local_aer_failed": swap_macro.get("local_aer_crosscheck", {}).get("failed") if swap_macro else None,
            "end_to_end_aer_failed": swap_macro.get("end_to_end_aer_crosscheck", {}).get("failed")
            if swap_macro
            else None,
            "top_swap_macro_circuit": (
                swap_macro.get("top_circuits_by_swap_macros", [{}])[0].get("relative_path")
            )
            if swap_macro
            else None,
        },
        "virtual_swap_elimination": {
            "path": str(virtual_swap_path.relative_to(root)),
            "exists": virtual_swap is not None,
            "status": virtual_swap.get("report_status") if virtual_swap else None,
            "proof_replay_path": str(virtual_swap_replay_path.relative_to(root)),
            "proof_replay_exists": virtual_swap_replay is not None,
            "proof_replay_status": virtual_swap_replay.get("report_status") if virtual_swap_replay else None,
            "proof_replay_events": virtual_swap_replay.get("proof_events") if virtual_swap_replay else None,
            "proof_replayed_events": virtual_swap_replay.get("replayed_events") if virtual_swap_replay else None,
            "proof_replay_output_mismatches": virtual_swap_replay.get("output_mismatches")
            if virtual_swap_replay
            else None,
            "proof_replay_error_count": virtual_swap_replay.get("error_count") if virtual_swap_replay else None,
            "rewritten_circuits": virtual_swap.get("rewritten_circuits") if virtual_swap else None,
            "skipped_circuits": virtual_swap.get("skipped_circuits") if virtual_swap else None,
            "virtual_swaps_removed": virtual_swap.get("virtual_swaps_removed") if virtual_swap else None,
            "removed_cx_gates": virtual_swap.get("removed_cx_gates") if virtual_swap else None,
            "two_qubit_reduction_pct": virtual_swap.get("metrics", {}).get("two_qubit_gate_count", {}).get(
                "reduction_pct"
            )
            if virtual_swap
            else None,
            "exposure_reduction_pct": virtual_swap.get("metrics", {})
            .get("hardware_weighted_error_exposure", {})
            .get("reduction_pct")
            if virtual_swap
            else None,
            "local_aer_failed": virtual_swap.get("local_aer_crosscheck", {}).get("failed") if virtual_swap else None,
            "end_to_end_aer_failed": virtual_swap.get("end_to_end_aer_crosscheck", {}).get("failed")
            if virtual_swap
            else None,
            "top_virtual_swap_circuit": (
                virtual_swap.get("top_circuits_by_virtual_swaps", [{}])[0].get("relative_path")
            )
            if virtual_swap
            else None,
        },
        "synthetic_noise_proxy": {
            "path": str(synthetic_noise_path.relative_to(root)),
            "exists": synthetic_noise is not None,
            "status": synthetic_noise.get("report_status") if synthetic_noise else None,
            "profile": synthetic_noise.get("profile_name") if synthetic_noise else None,
            "best_comparison_by_exposure_reduction": synthetic_noise.get("best_comparison_by_exposure_reduction")
            if synthetic_noise
            else None,
            "source_vs_virtual_swap_exposure_reduction_pct": next(
                (
                    row["metrics"]["hardware_weighted_error_exposure"]["reduction_pct"]
                    for row in synthetic_noise.get("comparisons", [])
                    if row.get("name") == "source_level1_routed_vs_virtual_swap"
                ),
                None,
            )
            if synthetic_noise
            else None,
            "source_vs_virtual_swap_success_proxy_ratio": next(
                (
                    row["aggregate_success_proxy_ratio"]
                    for row in synthetic_noise.get("comparisons", [])
                    if row.get("name") == "source_level1_routed_vs_virtual_swap"
                ),
                None,
            )
            if synthetic_noise
            else None,
        },
        "next_technical_steps": [
            "Add external exact-checkable circuits, especially MQT Bench or additional QASMBench families.",
            "Promote the line-routing diagnostic into a richer routing verifier, then add a calibrated heavy-hex transpiler baseline comparison.",
            "Implement a scalable equivalence strategy for stress circuits.",
            "Raise 30-circuit aggregate heavy-hex-like exposure reduction toward the 20% target.",
            "Extend virtual SWAP elimination to dynamic circuits with classical control/reset, independently verify wire-permutation certificates, and integrate it into a native-basis-aware 2-4 qubit routing optimizer.",
            "Connect B1 compressed circuits to B7 resource estimation.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B1 Certificate Evidence Report v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['report_status']}**",
        "",
        "## Supported Claim",
        "",
        report["claim_supported_now"],
        "",
        "## Claims Not Yet Supported",
        "",
    ]
    lines.extend(f"- {item}" for item in report["claim_not_supported_yet"])
    lines.extend(
        [
            "",
            "## Proof-Log Results",
            "",
            "| Result | Circuits | Equivalence | Audit | Replay | Semantic | Proof events | Exposure reduction |",
            "|---|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["prooflog_results"]:
        equivalence = (
            f"{row['equivalence_passed']} pass / {row['equivalence_failed']} fail"
            if row["equivalence_mode"] == "exact_statevector"
            else row["equivalence_mode"]
        )
        lines.append(
            "| "
            + row["key"]
            + f" | {row['circuit_count']} | {equivalence} | {row['audit_passed']} | "
            + f"{row['replay_passed']} | {row['semantic_passed']} | {row['proof_events']['total']} | "
            + f"{percent(row['hardware_weighted_exposure_reduction_pct'])} |"
        )

    aggregate = report["exact_aggregate"]
    lines.extend(
        [
            "",
            "## Exact-Checked Aggregate",
            "",
            f"- Circuits: {aggregate['circuit_count']}",
            f"- Equivalence failures: {aggregate['equivalence_failed']}",
            f"- Operation-count reduction: {percent(aggregate['operation_count_reduction_pct'])}",
            f"- Two-qubit-gate reduction: {percent(aggregate['two_qubit_gate_count_reduction_pct'])}",
            f"- Logical-depth reduction: {percent(aggregate['logical_depth_reduction_pct'])}",
            f"- Heavy-hex-like exposure reduction: {percent(aggregate['hardware_weighted_exposure_reduction_pct'])}",
            "",
            "| Subset | Circuits | Max qubits | Equivalence failures | Exposure reduction |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for subset in aggregate["subsets"]:
        lines.append(
            f"| {subset['name']} | {subset['circuits']} | {subset['max_qubits']} | "
            f"{subset['equivalence_failed']} | {percent(subset['heavy_hex_like_exposure_reduction_pct'])} |"
        )

    lines.extend(["", "## Gate Status", "", "| Gate | Current | Passed |", "|---|---|---:|"])
    for name, gate in report["gates"].items():
        current = gate.get("current", gate.get("current_exact_circuit_count", gate.get("current_exact_failures", "")))
        if isinstance(current, float):
            current = percent(current)
        lines.append(f"| {name} | {current} | {gate['passed']} |")

    ablation = report["ablation"]
    lines.extend(
        [
            "",
            "## Ablation Summary",
            "",
            f"- Report exists: {ablation['exists']}",
            f"- Report path: `{ablation['path']}`",
            f"- Largest hardware-exposure contributor: `{ablation['largest_hardware_exposure_contributor']}`",
            f"- Largest depth contributor: `{ablation['largest_depth_contributor']}`",
        ]
    )

    baseline = report["baseline_comparison"]
    exposure_delta = baseline["b1_minus_best_valid_qiskit_exposure_pct"]
    exposure_delta_text = "n/a" if exposure_delta is None else percent(exposure_delta)
    lines.extend(
        [
            "",
            "## Baseline Comparison Summary",
            "",
            f"- Report exists: {baseline['exists']}",
            f"- Report path: `{baseline['path']}`",
            f"- Best exact-valid Qiskit level by exposure: `{baseline['best_valid_qiskit_level']}`",
            f"- B1 exposure delta versus best valid Qiskit: {exposure_delta_text}",
            f"- Invalid Qiskit levels: {baseline['invalid_qiskit_levels']}",
        ]
    )

    routing = report["routing_diagnostic"]
    routing_exposure = routing["best_diagnostic_exposure_reduction_pct"]
    routing_exposure_text = "n/a" if routing_exposure is None else percent(routing_exposure)
    aer_tvd = routing["aer_crosscheck_max_tvd"]
    aer_tvd_text = "n/a" if aer_tvd is None else f"{float(aer_tvd):.5f}"
    lines.extend(
        [
            "",
            "## Routing Diagnostic Summary",
            "",
            f"- Report exists: {routing['exists']}",
            f"- Report path: `{routing['path']}`",
            f"- Status: `{routing['status']}`",
            f"- Full exact-valid baseline: {routing['full_exact_valid_baseline']}",
            f"- Full measurement-distribution-valid baseline: {routing['full_measurement_distribution_valid_baseline']}",
            f"- Partial measurement-distribution levels: {routing['partial_measurement_distribution_levels']}",
            f"- Common measurement-distribution failure: {routing['common_measurement_distribution_failures']}",
            f"- Aer cross-check all passed: {routing['aer_crosscheck_all_passed']}",
            f"- Aer cross-check total pairs: {routing['aer_crosscheck_total_pairs']}",
            f"- Aer cross-check max TVD: {aer_tvd_text}",
            f"- Best diagnostic exposure reduction: {routing_exposure_text}",
        ]
    )

    heavyhex = report["heavyhex_diagnostic"]
    heavyhex_exposure = heavyhex["best_diagnostic_exposure_reduction_pct"]
    heavyhex_exposure_text = "n/a" if heavyhex_exposure is None else percent(heavyhex_exposure)
    lines.extend(
        [
            "",
            "## Heavy-Hex Topology Diagnostic Summary",
            "",
            f"- Report exists: {heavyhex['exists']}",
            f"- Report path: `{heavyhex['path']}`",
            f"- Status: `{heavyhex['status']}`",
            f"- Distance: {heavyhex['distance']}",
            f"- Physical qubits: {heavyhex['physical_qubits']}",
            f"- Aer cross-check all passed: {heavyhex['aer_crosscheck_all_passed']}",
            f"- Aer-valid levels: {heavyhex['aer_crosscheck_valid_levels']}",
            f"- Best diagnostic exposure reduction: {heavyhex_exposure_text}",
        ]
    )

    e2e = report["heavyhex_end_to_end"]
    e2e_suite = report["heavyhex_end_to_end_suite"]
    lines.extend(
        [
            "",
            "## Heavy-Hex End-to-End Routed Benefit",
            "",
            f"- Report exists: {e2e['exists']}",
            f"- Report path: `{e2e['path']}`",
            f"- Status: `{e2e['status']}`",
            f"- Aer cross-check pass/fail: {e2e['aer_crosscheck_passed']} / {e2e['aer_crosscheck_failed']}",
            f"- Operation-count reduction after routing: {percent(e2e['operation_count_reduction_pct'])}",
            f"- Two-qubit-gate reduction after routing: {percent(e2e['two_qubit_gate_count_reduction_pct'])}",
            f"- Logical-depth reduction after routing: {percent(e2e['logical_depth_reduction_pct'])}",
            f"- Heavy-hex-like exposure reduction after routing: {percent(e2e['hardware_weighted_exposure_reduction_pct'])}",
            f"- Idle-layer proxy reduction after routing: {percent(e2e['idle_layer_proxy_reduction_pct'])}",
            f"- Suite report exists: {e2e_suite['exists']}",
            f"- Suite levels tested: {e2e_suite['levels_tested']}",
            f"- Suite all Aer cross-checks passed: {e2e_suite['all_aer_crosschecks_passed']}",
            f"- Suite best level by exposure: {e2e_suite['best_level_by_exposure']}",
            f"- Suite best exposure reduction: {percent(e2e_suite['best_exposure_reduction_pct'])}",
        ]
    )

    profile = report["post_routing_bottleneck_profile"]
    lines.extend(
        [
            "",
            "## Post-Routing Bottleneck Profile",
            "",
            f"- Report exists: {profile['exists']}",
            f"- Report path: `{profile['path']}`",
            f"- Status: `{profile['status']}`",
            f"- Levels tested: {profile['levels_tested']}",
            f"- All Aer cross-checks passed: {profile['all_aer_crosschecks_passed']}",
            f"- Level 0 exposure reduction: {percent(profile['level0_exposure_reduction_pct'])}",
            f"- Level 1 exposure reduction: {percent(profile['level1_exposure_reduction_pct'])}",
            f"- Circuits with level-1 benefit erasure: {profile['erased_circuit_count']}",
            f"- Top level-1 2Q bottleneck: `{profile['top_level1_two_qubit_bottleneck']}`",
        ]
    )

    swap_macro = report["post_routing_swap_macro"]
    lines.extend(
        [
            "",
            "## Post-Routing SWAP Macro Diagnostic",
            "",
            f"- Report exists: {swap_macro['exists']}",
            f"- Report path: `{swap_macro['path']}`",
            f"- Status: `{swap_macro['status']}`",
            f"- SWAP macros: {swap_macro['swap_macros']}",
            f"- Removed CX gates: {swap_macro['removed_cx_gates']}",
            f"- 2Q macro reduction: {percent(swap_macro['two_qubit_reduction_pct'])}",
            f"- Exposure reduction under macro cost model: {percent(swap_macro['exposure_reduction_pct'])}",
            f"- Local Aer failures: {swap_macro['local_aer_failed']}",
            f"- End-to-end Aer failures: {swap_macro['end_to_end_aer_failed']}",
            f"- Top SWAP macro circuit: `{swap_macro['top_swap_macro_circuit']}`",
        ]
    )

    virtual_swap = report["virtual_swap_elimination"]
    lines.extend(
        [
            "",
            "## Virtual SWAP Elimination Diagnostic",
            "",
            f"- Report exists: {virtual_swap['exists']}",
            f"- Report path: `{virtual_swap['path']}`",
            f"- Status: `{virtual_swap['status']}`",
            f"- Rewritten circuits: {virtual_swap['rewritten_circuits']}",
            f"- Skipped circuits: {virtual_swap['skipped_circuits']}",
            f"- Virtual SWAPs removed: {virtual_swap['virtual_swaps_removed']}",
            f"- Removed CX gates: {virtual_swap['removed_cx_gates']}",
            f"- 2Q reduction: {percent(virtual_swap['two_qubit_reduction_pct'])}",
            f"- Exposure reduction: {percent(virtual_swap['exposure_reduction_pct'])}",
            f"- Local Aer failures: {virtual_swap['local_aer_failed']}",
            f"- End-to-end Aer failures: {virtual_swap['end_to_end_aer_failed']}",
            f"- Proof replay status: {virtual_swap['proof_replay_status']}",
            f"- Proof replay events: {virtual_swap['proof_replayed_events']} / {virtual_swap['proof_replay_events']}",
            f"- Proof replay output mismatches: {virtual_swap['proof_replay_output_mismatches']}",
            f"- Proof replay errors: {virtual_swap['proof_replay_error_count']}",
            f"- Top virtual-SWAP circuit: `{virtual_swap['top_virtual_swap_circuit']}`",
        ]
    )

    synthetic_noise = report["synthetic_noise_proxy"]
    lines.extend(
        [
            "",
            "## Synthetic Heavy-Hex Noise Proxy",
            "",
            f"- Report exists: {synthetic_noise['exists']}",
            f"- Report path: `{synthetic_noise['path']}`",
            f"- Status: `{synthetic_noise['status']}`",
            f"- Profile: `{synthetic_noise['profile']}`",
            f"- Best comparison: `{synthetic_noise['best_comparison_by_exposure_reduction']}`",
            f"- Source routed vs virtual-SWAP exposure reduction: {percent(synthetic_noise['source_vs_virtual_swap_exposure_reduction_pct'])}",
            f"- Source routed vs virtual-SWAP success proxy ratio: {synthetic_noise['source_vs_virtual_swap_success_proxy_ratio']:.2f}x",
        ]
    )

    lines.extend(["", "## Next Technical Steps", ""])
    lines.extend(f"- {step}" for step in report["next_technical_steps"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_certificate_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_certificate_report.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    report = build_report(root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
