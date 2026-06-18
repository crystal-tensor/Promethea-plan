#!/usr/bin/env python3
"""Compute target space-time volumes from the B2 Stim surface-code baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def metric_value(row: dict, criterion: str) -> float:
    if criterion == "wilson_95_high":
        return float(row["wilson_95_high"])
    if criterion == "observed_logical_error_rate":
        return float(row["logical_error_rate"])
    raise ValueError(f"unsupported target criterion: {criterion}")


def compute_targets(baseline: dict, targets: list[float], criterion: str) -> dict:
    rows = baseline["results"]
    bases = sorted({row["memory_basis"] for row in rows})
    physical_errors = sorted({float(row["physical_error"]) for row in rows})
    output_rows = []
    for basis in bases:
        for physical_error in physical_errors:
            candidates = [
                {
                    **row,
                    "space_time_volume": int(row["physical_qubits_in_stim_circuit"]) * int(row["rounds"]),
                    "target_metric_value": metric_value(row, criterion),
                }
                for row in rows
                if row["memory_basis"] == basis and float(row["physical_error"]) == physical_error
            ]
            candidates.sort(key=lambda row: (row["space_time_volume"], int(row["distance"])))
            for target in targets:
                feasible = [row for row in candidates if row["target_metric_value"] <= target]
                if feasible:
                    best = feasible[0]
                    output_rows.append(
                        {
                            "memory_basis": basis,
                            "physical_error": physical_error,
                            "target_logical_error": target,
                            "criterion": criterion,
                            "met": True,
                            "distance": best["distance"],
                            "rounds": best["rounds"],
                            "physical_qubits": best["physical_qubits_in_stim_circuit"],
                            "space_time_volume": best["space_time_volume"],
                            "logical_failures": best["logical_failures"],
                            "shots": best["shots"],
                            "logical_error_rate": best["logical_error_rate"],
                            "wilson_95_high": best["wilson_95_high"],
                            "decoder_runtime_seconds_per_shot": best["decoder_runtime_seconds_per_shot"],
                        }
                    )
                else:
                    best_available = min(candidates, key=lambda row: row["target_metric_value"])
                    output_rows.append(
                        {
                            "memory_basis": basis,
                            "physical_error": physical_error,
                            "target_logical_error": target,
                            "criterion": criterion,
                            "met": False,
                            "distance": None,
                            "rounds": None,
                            "physical_qubits": None,
                            "space_time_volume": None,
                            "best_available_distance": best_available["distance"],
                            "best_available_logical_error_rate": best_available["logical_error_rate"],
                            "best_available_wilson_95_high": best_available["wilson_95_high"],
                            "best_available_logical_failures": best_available["logical_failures"],
                            "best_available_shots": best_available["shots"],
                        }
                    )
    met_count = sum(1 for row in output_rows if row["met"])
    return {
        "benchmark_id": "B2",
        "problem_id": 22,
        "title": "B2 target volumes from Stim/PyMatching surface-code baseline",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "stim_surface_code_target_volume_baseline",
        "method": "target_space_time_volume_from_stim_surface_code_baseline_v0",
        "source_method": baseline["method"],
        "source_status": baseline["status"],
        "source_seed": baseline["seed"],
        "source_shots_per_configuration": baseline["shots_per_configuration"],
        "criterion": criterion,
        "target_count": len(targets),
        "memory_basis_count": len(bases),
        "physical_error_count": len(physical_errors),
        "target_combinations": len(output_rows),
        "met_count": met_count,
        "unmet_count": len(output_rows) - met_count,
        "results": output_rows,
        "limits": [
            "This target-volume table is only as strong as the small d=3/5/7 baseline sweep.",
            "The default criterion uses Wilson 95% upper bounds, so zero-failure rows remain conservative instead of proof of very low pL.",
            "The space-time volume uses Stim circuit qubits times rounds; it is not yet a full architecture layout or factory cost model.",
            "This is a baseline table, not evidence that a new low-overhead code beats surface code.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B2 Stim Surface-Code Target Volume v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source status: {report['source_status']}",
        f"- Criterion: {report['criterion']}",
        f"- Target combinations: {report['target_combinations']}",
        f"- Met / unmet: {report['met_count']} / {report['unmet_count']}",
        f"- Source shots per configuration: {report['source_shots_per_configuration']}",
        "",
        "## Target Volumes",
        "",
        "| basis | p | target pL | met | d | physical qubits | rounds | volume | pL observed | Wilson high |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["results"]:
        if row["met"]:
            lines.append(
                f"| {row['memory_basis']} | {row['physical_error']:.4g} | {row['target_logical_error']:.4g} | "
                f"True | {row['distance']} | {row['physical_qubits']} | {row['rounds']} | "
                f"{row['space_time_volume']} | {row['logical_error_rate']:.6g} | {row['wilson_95_high']:.6g} |"
            )
        else:
            lines.append(
                f"| {row['memory_basis']} | {row['physical_error']:.4g} | {row['target_logical_error']:.4g} | "
                f"False | {row['best_available_distance']} | n/a | n/a | n/a | "
                f"{row['best_available_logical_error_rate']:.6g} | {row['best_available_wilson_95_high']:.6g} |"
            )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("results/B2_stim_surface_code_memory_baseline_v0.json"),
    )
    parser.add_argument("--targets", default="1e-1,5e-2,1e-2,1e-3")
    parser.add_argument(
        "--criterion",
        choices=["wilson_95_high", "observed_logical_error_rate"],
        default="wilson_95_high",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B2_stim_surface_code_target_volume_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B2_stim_surface_code_target_volume.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    targets = parse_float_list(args.targets)
    report = compute_targets(baseline, targets, args.criterion)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(json.dumps({key: report[key] for key in ["status", "criterion", "target_combinations", "met_count", "unmet_count"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
