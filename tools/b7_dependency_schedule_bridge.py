#!/usr/bin/env python3
"""Bridge B1 circuit compression and B2 surface-code target volumes into B7."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def circuit_key(path: str) -> str:
    parts = Path(path).parts
    for marker in (
        "b1_exact_extension",
        "qasmbench_interaction_exact",
        "qasmbench_medium_exact",
        "qasmbench_small",
    ):
        if marker in parts:
            index = parts.index(marker)
            return "/".join(parts[index:])
    return Path(path).name


def select_b2_target_row(payload: dict, physical_error: float, target_logical_error: float) -> dict:
    candidates = [
        row
        for row in payload["results"]
        if row.get("met")
        and float(row["physical_error"]) == physical_error
        and float(row["target_logical_error"]) == target_logical_error
    ]
    if not candidates:
        raise ValueError(
            f"no met B2 target-volume row for p={physical_error} target={target_logical_error}"
        )
    return min(candidates, key=lambda row: (row["space_time_volume"], row["distance"], row["memory_basis"]))


def load_metric_pairs(before_path: Path, after_path: Path) -> list[tuple[str, dict, dict]]:
    before_payload = read_json(before_path)
    after_payload = read_json(after_path)
    before_rows = {circuit_key(row["path"]): row for row in before_payload["results"]}
    after_rows = {circuit_key(row["path"]): row for row in after_payload["results"]}
    keys = sorted(set(before_rows) & set(after_rows))
    return [(key, before_rows[key], after_rows[key]) for key in keys]


def aggregate_metrics(rows: list[dict]) -> dict:
    fields = [
        "qubits",
        "operation_count",
        "two_qubit_gate_count",
        "logical_depth",
        "two_qubit_or_larger_depth_proxy",
        "hardware_weighted_error_exposure",
        "idle_layer_proxy",
    ]
    aggregate = {}
    for field in fields:
        if field == "qubits":
            aggregate[field] = max(float(row[field]) for row in rows)
        else:
            aggregate[field] = sum(float(row[field]) for row in rows)
    aggregate["path"] = "aggregate_30_circuits"
    return aggregate


def dependency_nodes(metrics: dict) -> list[dict]:
    twoq_layers = int(metrics.get("two_qubit_or_larger_depth_proxy", metrics["logical_depth"]))
    logical_depth = int(metrics["logical_depth"])
    single_or_idle_layers = max(0, logical_depth - twoq_layers)
    nodes = [
        {
            "id": "logical_memory_init",
            "kind": "memory",
            "layers": 1,
            "depends_on": [],
        },
        {
            "id": "single_qubit_and_idle_layers",
            "kind": "single_qubit_or_idle",
            "layers": single_or_idle_layers,
            "depends_on": ["logical_memory_init"],
        },
        {
            "id": "two_qubit_interaction_layers",
            "kind": "two_qubit_interaction",
            "layers": twoq_layers,
            "depends_on": ["single_qubit_and_idle_layers"],
        },
        {
            "id": "measurement_and_readout",
            "kind": "measurement",
            "layers": 1,
            "depends_on": ["two_qubit_interaction_layers"],
        },
    ]
    return nodes


def schedule_estimate(metrics: dict, b2_row: dict, label: str) -> dict:
    logical_qubits = int(metrics["qubits"])
    logical_depth = int(metrics["logical_depth"])
    twoq_depth = int(metrics.get("two_qubit_or_larger_depth_proxy", logical_depth))
    nodes = dependency_nodes(metrics)
    b2_rounds = int(b2_row["rounds"])
    b2_physical_qubits = int(b2_row["physical_qubits"])
    b2_volume = int(b2_row["space_time_volume"])

    logical_layer_count = sum(node["layers"] for node in nodes)
    schedule_rounds = logical_layer_count * b2_rounds
    physical_qubits = logical_qubits * b2_physical_qubits
    space_time_volume = logical_qubits * b2_volume * logical_layer_count
    twoq_layer_fraction = twoq_depth / logical_depth if logical_depth else 0.0
    exposure_per_logical_depth = (
        float(metrics["hardware_weighted_error_exposure"]) / logical_depth if logical_depth else 0.0
    )
    return {
        "label": label,
        "model_status": "dependency_schedule_bridge_not_physical_layout",
        "logical_qubits": logical_qubits,
        "logical_depth": logical_depth,
        "logical_layer_count_with_init_readout": logical_layer_count,
        "two_qubit_layers": twoq_depth,
        "two_qubit_layer_fraction": twoq_layer_fraction,
        "operation_count": int(metrics["operation_count"]),
        "two_qubit_gate_count": int(metrics["two_qubit_gate_count"]),
        "hardware_weighted_error_exposure": float(metrics["hardware_weighted_error_exposure"]),
        "exposure_per_logical_depth": exposure_per_logical_depth,
        "selected_b2_distance": int(b2_row["distance"]),
        "selected_b2_basis": b2_row["memory_basis"],
        "selected_b2_physical_error": float(b2_row["physical_error"]),
        "selected_b2_target_logical_error": float(b2_row["target_logical_error"]),
        "selected_b2_wilson_95_high": float(b2_row["wilson_95_high"]),
        "b2_physical_qubits_per_logical_tile": b2_physical_qubits,
        "b2_rounds_per_logical_layer": b2_rounds,
        "b2_space_time_volume_per_logical_layer": b2_volume,
        "estimated_physical_qubits": physical_qubits,
        "estimated_schedule_rounds": schedule_rounds,
        "estimated_space_time_volume": space_time_volume,
        "dependency_nodes": nodes,
    }


def compare_pair(name: str, before: dict, after: dict, b2_row: dict) -> dict:
    before_estimate = schedule_estimate(before, b2_row, "before_b1_virtual_swap")
    after_estimate = schedule_estimate(after, b2_row, "after_b1_virtual_swap")
    return {
        "workload": name,
        "before": before_estimate,
        "after": after_estimate,
        "logical_depth_reduction": before_estimate["logical_depth"] / after_estimate["logical_depth"]
        if after_estimate["logical_depth"]
        else None,
        "two_qubit_gate_reduction": before_estimate["two_qubit_gate_count"] / after_estimate["two_qubit_gate_count"]
        if after_estimate["two_qubit_gate_count"]
        else None,
        "space_time_volume_reduction": before_estimate["estimated_space_time_volume"]
        / after_estimate["estimated_space_time_volume"]
        if after_estimate["estimated_space_time_volume"]
        else None,
        "exposure_reduction": before_estimate["hardware_weighted_error_exposure"]
        / after_estimate["hardware_weighted_error_exposure"]
        if after_estimate["hardware_weighted_error_exposure"]
        else None,
    }


def run(args: argparse.Namespace) -> dict:
    b2_payload = read_json(args.b2_target_volume)
    b2_row = select_b2_target_row(
        b2_payload,
        physical_error=args.physical_error,
        target_logical_error=args.target_logical_error,
    )
    pairs = load_metric_pairs(args.before_metrics, args.after_metrics)
    top_keys = {
        "qasmbench_medium_exact/gcm_h6.qasm",
        "qasmbench_medium_exact/sat_n11.qasm",
        "qasmbench_interaction_exact/basis_trotter_n4.qasm",
        "qasmbench_small/hhl_n7.qasm",
        "qasmbench_medium_exact/qf21_n15.qasm",
    }
    selected_pairs = [(key, before, after) for key, before, after in pairs if key in top_keys]
    before_aggregate = aggregate_metrics([before for _key, before, _after in pairs])
    after_aggregate = aggregate_metrics([after for _key, _before, after in pairs])
    comparisons = [compare_pair(key, before, after, b2_row) for key, before, after in selected_pairs]
    comparisons.insert(0, compare_pair("aggregate_30_circuits", before_aggregate, after_aggregate, b2_row))
    reductions = [row["space_time_volume_reduction"] for row in comparisons if row["space_time_volume_reduction"]]
    exposure_reductions = [row["exposure_reduction"] for row in comparisons if row["exposure_reduction"]]
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 dependency-schedule bridge from B1 and B2",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "dependency_schedule_bridge_not_physical_layout",
        "method": "b1_b2_dependency_schedule_bridge_v0",
        "b1_source": str(args.before_metrics),
        "b1_after_source": str(args.after_metrics),
        "b2_source": str(args.b2_target_volume),
        "selected_b2_target": {
            "memory_basis": b2_row["memory_basis"],
            "physical_error": b2_row["physical_error"],
            "target_logical_error": b2_row["target_logical_error"],
            "criterion": b2_row["criterion"],
            "distance": b2_row["distance"],
            "physical_qubits": b2_row["physical_qubits"],
            "rounds": b2_row["rounds"],
            "space_time_volume": b2_row["space_time_volume"],
            "wilson_95_high": b2_row["wilson_95_high"],
        },
        "comparison_count": len(comparisons),
        "min_space_time_volume_reduction": min(reductions),
        "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
        "min_exposure_reduction": min(exposure_reductions),
        "mean_exposure_reduction": sum(exposure_reductions) / len(exposure_reductions),
        "comparisons": comparisons,
        "limits": [
            "This is a dependency-schedule bridge, not a physical layout or lattice-surgery compiler.",
            "The B2 target row is a small-distance Stim/PyMatching baseline and not a threshold or hardware-calibrated claim.",
            "The schedule maps QASM depth proxies to logical layers; it does not model magic-state factories or feed-forward.",
            "The aggregate row sums benchmark circuits for a portfolio-level sensitivity check, not a single executable algorithm.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B7 B1/B2 Dependency-Schedule Bridge v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Comparisons: {report['comparison_count']}",
        f"- Selected B2 target: d={report['selected_b2_target']['distance']}, "
        f"basis={report['selected_b2_target']['memory_basis']}, "
        f"p={report['selected_b2_target']['physical_error']}, "
        f"target={report['selected_b2_target']['target_logical_error']}",
        f"- B2 Wilson 95% high: {report['selected_b2_target']['wilson_95_high']:.6g}",
        f"- Minimum space-time-volume reduction: {report['min_space_time_volume_reduction']:.3f}x",
        f"- Mean space-time-volume reduction: {report['mean_space_time_volume_reduction']:.3f}x",
        f"- Minimum exposure reduction: {report['min_exposure_reduction']:.3f}x",
        "",
        "## Comparisons",
        "",
        "| workload | depth before | depth after | volume reduction | exposure reduction | 2Q reduction |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["comparisons"]:
        lines.append(
            f"| {row['workload']} | {row['before']['logical_depth']} | "
            f"{row['after']['logical_depth']} | {row['space_time_volume_reduction']:.3f}x | "
            f"{row['exposure_reduction']:.3f}x | {row['two_qubit_gate_reduction']:.3f}x |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--before-metrics",
        type=Path,
        default=Path("results/b1_virtual_swap_elimination_level1/before_virtual_swap_metrics.json"),
    )
    parser.add_argument(
        "--after-metrics",
        type=Path,
        default=Path("results/b1_virtual_swap_elimination_level1/after_virtual_swap_metrics.json"),
    )
    parser.add_argument(
        "--b2-target-volume",
        type=Path,
        default=Path("results/B2_stim_surface_code_target_volume_v0.json"),
    )
    parser.add_argument("--physical-error", type=float, default=0.001)
    parser.add_argument("--target-logical-error", type=float, default=0.01)
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_b1_b2_dependency_schedule_bridge_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B7_b1_b2_dependency_schedule_bridge.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "comparison_count": report["comparison_count"],
                    "min_space_time_volume_reduction": report["min_space_time_volume_reduction"],
                    "mean_space_time_volume_reduction": report["mean_space_time_volume_reduction"],
                    "min_exposure_reduction": report["min_exposure_reduction"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
