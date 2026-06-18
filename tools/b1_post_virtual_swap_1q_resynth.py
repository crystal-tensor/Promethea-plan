#!/usr/bin/env python3
"""Post-process B1 virtual-SWAP circuits with 1Q run resynthesis.

This diagnostic asks whether the virtual-SWAP output still contains local
single-qubit fusion opportunities that reduce logical T-resource proxies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from b1_qasm_metrics import compute_metrics, find_qasm_files, load_profiles
from b1_single_qubit_resynth import rewrite_file
from b7_logical_t_factory_scheduler import qasm_t_resources


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def compute_directory_metrics(input_dir: Path, output_path: Path, profile_path: Path, profile: str) -> dict:
    profiles = load_profiles(profile_path)
    if profile not in profiles:
        raise ValueError(f"Unknown hardware profile {profile!r}; available={sorted(profiles)}")
    files = find_qasm_files([input_dir])
    if not files:
        raise ValueError(f"No .qasm files found under {input_dir}")
    rows = [compute_metrics(path, profiles[profile]) for path in files]
    payload = {
        "benchmark_id": "B1",
        "profile": profile,
        "circuit_count": len(rows),
        "results": rows,
    }
    write_json(output_path, payload)
    return payload


def metric_aggregate(metrics: dict) -> dict:
    rows = metrics["results"]
    return {
        "operation_count": sum(row["operation_count"] for row in rows),
        "single_qubit_gate_count": sum(row["gate_class_counts"]["single_qubit"] for row in rows),
        "two_qubit_gate_count": sum(row["two_qubit_gate_count"] for row in rows),
        "logical_depth": sum(row["logical_depth"] for row in rows),
        "hardware_weighted_error_exposure": sum(row["hardware_weighted_error_exposure"] for row in rows),
        "idle_layer_proxy": sum(row["idle_layer_proxy"] for row in rows),
    }


def pct_reduction(before: float, after: float) -> float | None:
    if before == 0:
        return None
    return 100.0 * (before - after) / before


def ratio(before: float, after: float) -> float | None:
    if after == 0:
        return None
    return before / after


def aggregate_t_resources(rows: list[dict]) -> dict:
    return {
        "logical_t_count_proxy": sum(row["logical_t_count_proxy"] for row in rows),
        "logical_t_depth_proxy": sum(row["logical_t_depth_proxy"] for row in rows),
        "direct_t_count": sum(row["direct_t_count"] for row in rows),
        "ccx_count": sum(row["ccx_count"] for row in rows),
        "non_clifford_rotation_count": sum(row["non_clifford_rotation_count"] for row in rows),
        "unknown_rotation_count": sum(row["unknown_rotation_count"] for row in rows),
        "operation_count_scanned": sum(row["operation_count_scanned"] for row in rows),
        "rotation_t_cost": rows[0]["rotation_t_cost"] if rows else 0,
    }


def relative_key(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def summarize_top_changes(before_metrics: dict, after_metrics: dict, input_dir: Path, output_dir: Path) -> list[dict]:
    before_by_key = {relative_key(Path(row["path"]), input_dir): row for row in before_metrics["results"]}
    after_by_key = {relative_key(Path(row["path"]), output_dir): row for row in after_metrics["results"]}
    rows = []
    for key in sorted(before_by_key):
        before = before_by_key[key]
        after = after_by_key[key]
        rows.append(
            {
                "relative_path": key,
                "operation_count_reduction": before["operation_count"] - after["operation_count"],
                "single_qubit_gate_reduction": before["gate_class_counts"]["single_qubit"]
                - after["gate_class_counts"]["single_qubit"],
                "logical_depth_reduction": before["logical_depth"] - after["logical_depth"],
                "exposure_reduction": before["hardware_weighted_error_exposure"]
                - after["hardware_weighted_error_exposure"],
            }
        )
    rows.sort(key=lambda row: (row["single_qubit_gate_reduction"], row["operation_count_reduction"]), reverse=True)
    return rows[:10]


def load_crosscheck(path: Path | None) -> dict | None:
    if path is None or not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": str(path),
        "check": payload.get("check"),
        "method": payload.get("method"),
        "shots": payload.get("shots"),
        "pair_count": payload.get("pair_count"),
        "passed": payload.get("passed"),
        "failed": payload.get("failed"),
        "max_total_variation_distance": payload.get("max_total_variation_distance"),
        "max_threshold": payload.get("max_threshold"),
    }


def classify_status(t_summary: dict, rewrite_stats: dict) -> str:
    if rewrite_stats["resynthesized_runs"] == 0:
        return "post_virtual_swap_1q_resynthesis_no_remaining_runs"
    if (t_summary["logical_t_count_reduction"] or 0) > 1.0:
        return "post_virtual_swap_1q_resynthesis_t_resource_positive_diagnostic"
    if (t_summary["logical_t_depth_reduction"] or 0) > 1.0:
        return "post_virtual_swap_1q_resynthesis_t_depth_positive_diagnostic"
    return "post_virtual_swap_1q_resynthesis_t_resource_boundary"


def run(args: argparse.Namespace) -> dict:
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    if not input_dir.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")

    qasm_files = find_qasm_files([input_dir])
    if not qasm_files:
        raise ValueError(f"No .qasm files found under {input_dir}")
    if args.certificate_log and args.certificate_log.exists():
        args.certificate_log.unlink()

    rewrite_rows = []
    for input_path in qasm_files:
        output_path = output_dir / input_path.relative_to(input_dir)
        rewrite_rows.append(
            rewrite_file(
                input_path,
                output_path,
                args.min_run_length,
                args.commute_disjoint,
                args.certificate_log,
            )
        )

    rewrite_stats = {
        "rewritten_circuits": len(rewrite_rows),
        "resynthesized_runs": sum(int(row["resynthesized_runs"]) for row in rewrite_rows),
        "input_single_qubit_gates_in_runs": sum(int(row["input_single_qubit_gates_in_runs"]) for row in rewrite_rows),
        "output_u3_gates": sum(int(row["output_u3_gates"]) for row in rewrite_rows),
        "removed_identity_gates": sum(int(row["removed_identity_gates"]) for row in rewrite_rows),
        "removed_single_qubit_gates": sum(int(row["removed_single_qubit_gates"]) for row in rewrite_rows),
        "certificate_entries": sum(int(row.get("certificate_entries", 0)) for row in rewrite_rows),
    }

    before_metrics = compute_directory_metrics(
        input_dir,
        args.before_metrics_output,
        args.hardware_profiles,
        args.profile,
    )
    after_metrics = compute_directory_metrics(
        output_dir,
        args.after_metrics_output,
        args.hardware_profiles,
        args.profile,
    )
    before_agg = metric_aggregate(before_metrics)
    after_agg = metric_aggregate(after_metrics)
    metric_summary = {
        "before": before_agg,
        "after": after_agg,
        "reduction_pct": {
            key: pct_reduction(before_agg[key], after_agg[key])
            for key in before_agg
        },
    }

    before_t_rows = [qasm_t_resources(path, args.rotation_t_cost) for path in qasm_files]
    after_t_rows = [
        qasm_t_resources(output_dir / path.relative_to(input_dir), args.rotation_t_cost)
        for path in qasm_files
    ]
    before_t = aggregate_t_resources(before_t_rows)
    after_t = aggregate_t_resources(after_t_rows)
    t_summary = {
        "before": before_t,
        "after": after_t,
        "logical_t_count_reduction": ratio(before_t["logical_t_count_proxy"], after_t["logical_t_count_proxy"]),
        "logical_t_depth_reduction": ratio(before_t["logical_t_depth_proxy"], after_t["logical_t_depth_proxy"]),
        "non_clifford_rotation_count_reduction": ratio(
            before_t["non_clifford_rotation_count"],
            after_t["non_clifford_rotation_count"],
        ),
    }

    report = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 post-virtual-SWAP single-qubit resynthesis diagnostic",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": classify_status(t_summary, rewrite_stats),
        "method": "post_virtual_swap_1q_run_to_u3_resynthesis_v0",
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "min_run_length": args.min_run_length,
        "commute_disjoint": args.commute_disjoint,
        "rotation_synthesis_t_cost": args.rotation_t_cost,
        "rewrite_stats": rewrite_stats,
        "metrics": metric_summary,
        "t_resource_proxy": t_summary,
        "top_circuits_by_single_qubit_reduction": summarize_top_changes(
            before_metrics,
            after_metrics,
            input_dir,
            output_dir,
        ),
        "before_metrics": str(args.before_metrics_output),
        "after_metrics": str(args.after_metrics_output),
        "certificate_log": str(args.certificate_log) if args.certificate_log else None,
        "aer_crosscheck": load_crosscheck(args.aer_crosscheck),
        "limits": [
            "This is a post-virtual-SWAP local 1Q fusion diagnostic, not a final T-optimized compiler.",
            "Arbitrary non-Clifford rotations use the same fixed T synthesis cost proxy as the B7 logical T-factory schedule.",
            "A positive gate-count reduction does not by itself imply a T-factory resource reduction.",
            "The result is intended to decide whether B1 currently supplies a T-resource lever for B7 or only a data-path/routing lever.",
        ],
    }
    return report


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}%"


def fmt_ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}x"


def markdown(report: dict) -> str:
    rewrite = report["rewrite_stats"]
    metrics = report["metrics"]
    t_proxy = report["t_resource_proxy"]
    aer = report.get("aer_crosscheck")
    lines = [
        "# B1 Post-Virtual-SWAP 1Q Resynthesis Diagnostic v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Circuits rewritten: {rewrite['rewritten_circuits']}",
        f"- Resynthesized 1Q runs: {rewrite['resynthesized_runs']}",
        f"- Removed 1Q gates: {rewrite['removed_single_qubit_gates']}",
        f"- Proof/certificate events: {rewrite['certificate_entries']}",
        f"- Operation-count reduction: {fmt_pct(metrics['reduction_pct']['operation_count'])}",
        f"- Single-qubit gate-count reduction: {fmt_pct(metrics['reduction_pct']['single_qubit_gate_count'])}",
        f"- Logical-depth reduction: {fmt_pct(metrics['reduction_pct']['logical_depth'])}",
        f"- Exposure reduction: {fmt_pct(metrics['reduction_pct']['hardware_weighted_error_exposure'])}",
        f"- Logical T-count proxy reduction: {fmt_ratio(t_proxy['logical_t_count_reduction'])}",
        f"- Logical T-depth proxy reduction: {fmt_ratio(t_proxy['logical_t_depth_reduction'])}",
        f"- Non-Clifford rotation-count reduction: {fmt_ratio(t_proxy['non_clifford_rotation_count_reduction'])}",
        "",
        "## T-Resource Proxy",
        "",
        "| metric | before | after | reduction |",
        "|---|---:|---:|---:|",
        f"| logical T-count proxy | {t_proxy['before']['logical_t_count_proxy']} | {t_proxy['after']['logical_t_count_proxy']} | {fmt_ratio(t_proxy['logical_t_count_reduction'])} |",
        f"| logical T-depth proxy | {t_proxy['before']['logical_t_depth_proxy']} | {t_proxy['after']['logical_t_depth_proxy']} | {fmt_ratio(t_proxy['logical_t_depth_reduction'])} |",
        f"| non-Clifford rotations | {t_proxy['before']['non_clifford_rotation_count']} | {t_proxy['after']['non_clifford_rotation_count']} | {fmt_ratio(t_proxy['non_clifford_rotation_count_reduction'])} |",
        "",
        "## Top Circuit Changes",
        "",
        "| circuit | removed 1Q gates | operation reduction | depth reduction | exposure reduction |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report["top_circuits_by_single_qubit_reduction"]:
        lines.append(
            f"| {row['relative_path']} | {row['single_qubit_gate_reduction']} | "
            f"{row['operation_count_reduction']} | {row['logical_depth_reduction']} | "
            f"{row['exposure_reduction']:.6g} |"
        )
    lines.extend(["", "## Verification", ""])
    if aer:
        lines.extend(
            [
                f"- Aer cross-check pairs: {aer['pair_count']}",
                f"- Aer failed pairs: {aer['failed']}",
                f"- Max TVD: {aer['max_total_variation_distance']}",
                f"- Max threshold: {aer['max_threshold']}",
            ]
        )
    else:
        lines.append("- Aer cross-check not attached yet.")
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("results/b1_virtual_swap_elimination_level1_work/01_virtual_swap_eliminated"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results/b1_post_virtual_swap_1q_resynth"))
    parser.add_argument("--min-run-length", type=int, default=2)
    parser.add_argument("--commute-disjoint", action="store_true")
    parser.add_argument("--rotation-t-cost", type=int, default=20)
    parser.add_argument("--hardware-profiles", type=Path, default=Path("benchmarks/hardware_profiles.json"))
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument(
        "--before-metrics-output",
        type=Path,
        default=Path("results/b1_post_virtual_swap_1q_resynth/before_metrics.json"),
    )
    parser.add_argument(
        "--after-metrics-output",
        type=Path,
        default=Path("results/b1_post_virtual_swap_1q_resynth/after_metrics.json"),
    )
    parser.add_argument(
        "--certificate-log",
        type=Path,
        default=Path("results/b1_post_virtual_swap_1q_resynth/proofs.jsonl"),
    )
    parser.add_argument(
        "--aer-crosscheck",
        type=Path,
        default=Path("results/b1_post_virtual_swap_1q_resynth/aer_crosscheck.json"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("results/B1_post_virtual_swap_1q_resynth_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_post_virtual_swap_1q_resynth.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    report = run(args)
    write_json(args.json_output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "rewritten_circuits": report["rewrite_stats"]["rewritten_circuits"],
                    "resynthesized_runs": report["rewrite_stats"]["resynthesized_runs"],
                    "removed_single_qubit_gates": report["rewrite_stats"]["removed_single_qubit_gates"],
                    "logical_t_count_reduction": report["t_resource_proxy"]["logical_t_count_reduction"],
                    "logical_t_depth_reduction": report["t_resource_proxy"]["logical_t_depth_reduction"],
                    "aer_failed": None
                    if report["aer_crosscheck"] is None
                    else report["aer_crosscheck"]["failed"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
