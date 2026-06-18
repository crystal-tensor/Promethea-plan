#!/usr/bin/env python3
"""Compare biased-noise schedule proxies against the B2 surface-code target table."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


VARIANTS = {
    "balanced_bias_aligned_schedule": {
        "basis_metric_multipliers": {"x": 0.72, "z": 0.78},
        "qubit_multiplier": 1.08,
        "round_multiplier": 1.05,
        "description": "Symmetric biased-noise schedule proxy with modest overhead and modest logical-error suppression.",
    },
    "z_memory_bias_aligned_schedule": {
        "basis_metric_multipliers": {"x": 0.90, "z": 0.55},
        "qubit_multiplier": 1.12,
        "round_multiplier": 1.08,
        "description": "Z-memory-favored schedule proxy with stronger suppression for z-memory rows.",
    },
    "x_memory_bias_aligned_schedule": {
        "basis_metric_multipliers": {"x": 0.55, "z": 0.90},
        "qubit_multiplier": 1.12,
        "round_multiplier": 1.08,
        "description": "X-memory-favored schedule proxy with stronger suppression for x-memory rows.",
    },
}


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def metric_value(row: dict, criterion: str) -> float:
    if criterion == "wilson_95_high":
        return float(row["wilson_95_high"])
    if criterion == "observed_logical_error_rate":
        return float(row["logical_error_rate"])
    raise ValueError(f"unsupported criterion: {criterion}")


def baseline_volume_rows(target_report: dict) -> dict[tuple[str, float, float], dict]:
    out = {}
    for row in target_report["results"]:
        out[(row["memory_basis"], float(row["physical_error"]), float(row["target_logical_error"]))] = row
    return out


def candidate_rows_for_baseline(baseline: dict, criterion: str) -> list[dict]:
    rows = []
    for source in baseline["results"]:
        basis = source["memory_basis"]
        for variant_name, variant in VARIANTS.items():
            metric_multiplier = float(variant["basis_metric_multipliers"][basis])
            physical_qubits = math.ceil(int(source["physical_qubits_in_stim_circuit"]) * float(variant["qubit_multiplier"]))
            rounds = math.ceil(int(source["rounds"]) * float(variant["round_multiplier"]))
            rows.append(
                {
                    "variant": variant_name,
                    "variant_description": variant["description"],
                    "code_family": "biased_schedule_surface_code_proxy",
                    "source_code_family": source["code_family"],
                    "memory_basis": basis,
                    "distance": source["distance"],
                    "source_rounds": source["rounds"],
                    "rounds": rounds,
                    "source_physical_qubits": source["physical_qubits_in_stim_circuit"],
                    "physical_qubits": physical_qubits,
                    "physical_error": float(source["physical_error"]),
                    "shots": source["shots"],
                    "source_logical_error_rate": source["logical_error_rate"],
                    "source_wilson_95_high": source["wilson_95_high"],
                    "metric_multiplier": metric_multiplier,
                    "candidate_logical_error_rate_proxy": min(1.0, float(source["logical_error_rate"]) * metric_multiplier),
                    "candidate_wilson_95_high_proxy": min(1.0, float(source["wilson_95_high"]) * metric_multiplier),
                    "space_time_volume": physical_qubits * rounds,
                    "source_space_time_volume": int(source["physical_qubits_in_stim_circuit"]) * int(source["rounds"]),
                }
            )
    return rows


def candidate_metric_value(row: dict, criterion: str) -> float:
    if criterion == "wilson_95_high":
        return float(row["candidate_wilson_95_high_proxy"])
    if criterion == "observed_logical_error_rate":
        return float(row["candidate_logical_error_rate_proxy"])
    raise ValueError(f"unsupported criterion: {criterion}")


def best_candidate_for(rows: list[dict], basis: str, physical_error: float, target: float, criterion: str) -> dict | None:
    candidates = [
        row
        for row in rows
        if row["memory_basis"] == basis
        and float(row["physical_error"]) == physical_error
        and candidate_metric_value(row, criterion) <= target
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda row: (row["space_time_volume"], row["distance"], row["variant"]))


def compare(baseline: dict, target_report: dict, targets: list[float], criterion: str) -> dict:
    candidate_rows = candidate_rows_for_baseline(baseline, criterion)
    baseline_by_key = baseline_volume_rows(target_report)
    bases = sorted({row["memory_basis"] for row in baseline["results"]})
    physical_errors = sorted({float(row["physical_error"]) for row in baseline["results"]})
    comparisons = []
    for basis in bases:
        for physical_error in physical_errors:
            for target in targets:
                baseline_row = baseline_by_key[(basis, physical_error, target)]
                candidate = best_candidate_for(candidate_rows, basis, physical_error, target, criterion)
                candidate_met = candidate is not None
                baseline_met = bool(baseline_row["met"])
                baseline_volume = baseline_row["space_time_volume"] if baseline_met else None
                candidate_volume = candidate["space_time_volume"] if candidate_met else None
                volume_reduction = (
                    baseline_volume / candidate_volume
                    if baseline_volume and candidate_volume
                    else None
                )
                candidate_only = candidate_met and not baseline_met
                improved = bool(volume_reduction is not None and volume_reduction > 1.0)
                comparisons.append(
                    {
                        "memory_basis": basis,
                        "physical_error": physical_error,
                        "target_logical_error": target,
                        "criterion": criterion,
                        "baseline_met": baseline_met,
                        "baseline_distance": baseline_row.get("distance"),
                        "baseline_space_time_volume": baseline_volume,
                        "baseline_metric_value": baseline_row.get("wilson_95_high")
                        if baseline_met
                        else baseline_row.get("best_available_wilson_95_high"),
                        "candidate_met": candidate_met,
                        "candidate_variant": candidate["variant"] if candidate else None,
                        "candidate_distance": candidate["distance"] if candidate else None,
                        "candidate_space_time_volume": candidate_volume,
                        "candidate_metric_value": candidate_metric_value(candidate, criterion) if candidate else None,
                        "candidate_metric_multiplier": candidate["metric_multiplier"] if candidate else None,
                        "volume_reduction_vs_baseline": volume_reduction,
                        "improved_volume": improved,
                        "candidate_only_meets_target": candidate_only,
                        "interpretation": (
                            "candidate_beats_baseline_volume"
                            if improved
                            else "candidate_meets_target_unmet_by_baseline"
                            if candidate_only
                            else "no_candidate_advantage"
                        ),
                    }
                )
    improved_rows = [row for row in comparisons if row["improved_volume"]]
    candidate_only_rows = [row for row in comparisons if row["candidate_only_meets_target"]]
    met_rows = [row for row in comparisons if row["candidate_met"]]
    reductions = [row["volume_reduction_vs_baseline"] for row in improved_rows]
    return {
        "benchmark_id": "B2",
        "problem_id": 22,
        "title": "B2 biased-noise schedule target-volume proxy",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "biased_schedule_proxy_not_new_code_claim",
        "method": "biased_schedule_target_volume_proxy_v0",
        "source_baseline": "B2_stim_surface_code_memory_baseline_v0",
        "source_target_volume": "B2_stim_surface_code_target_volume_v0",
        "criterion": criterion,
        "target_combinations": len(comparisons),
        "candidate_rows": len(candidate_rows),
        "candidate_variants": sorted(VARIANTS),
        "candidate_met_count": len(met_rows),
        "baseline_met_count": sum(1 for row in comparisons if row["baseline_met"]),
        "improved_volume_count": len(improved_rows),
        "candidate_only_meets_target_count": len(candidate_only_rows),
        "mean_volume_reduction_on_improved": sum(reductions) / len(reductions) if reductions else None,
        "max_volume_reduction": max(reductions) if reductions else None,
        "comparisons": comparisons,
        "limits": [
            "This is a parameterized biased-schedule proxy, not a circuit-level biased-noise simulation.",
            "The proxy scales Wilson/observed logical error metrics from the existing Stim/PyMatching baseline and adds explicit qubit/round overhead.",
            "A candidate-only target is a hypothesis to test with real biased-noise circuits, not proof of low-overhead QEC.",
            "The comparison is useful because it uses the same target-volume contract as the surface-code baseline.",
        ],
    }


def fmt(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"


def fmt_ratio(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}x"


def markdown(report: dict) -> str:
    lines = [
        "# B2 Biased-Noise Schedule Target-Volume Proxy v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Criterion: {report['criterion']}",
        f"- Candidate variants: {report['candidate_variants']}",
        f"- Target combinations: {report['target_combinations']}",
        f"- Baseline met count: {report['baseline_met_count']}",
        f"- Candidate met count: {report['candidate_met_count']}",
        f"- Candidate volume improvements: {report['improved_volume_count']}",
        f"- Candidate-only target hits: {report['candidate_only_meets_target_count']}",
        f"- Mean volume reduction on improved rows: {fmt_ratio(report['mean_volume_reduction_on_improved'])}",
        f"- Max volume reduction: {fmt_ratio(report['max_volume_reduction'])}",
        "",
        "## Candidate Variants",
        "",
        "| variant | x multiplier | z multiplier | qubit multiplier | round multiplier |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, variant in VARIANTS.items():
        lines.append(
            f"| {name} | {variant['basis_metric_multipliers']['x']} | "
            f"{variant['basis_metric_multipliers']['z']} | {variant['qubit_multiplier']} | "
            f"{variant['round_multiplier']} |"
        )
    lines.extend(
        [
            "",
            "## Comparisons",
            "",
            "| basis | p | target | baseline met | baseline volume | candidate met | candidate variant | candidate volume | volume reduction | interpretation |",
            "|---|---:|---:|---|---:|---|---|---:|---:|---|",
        ]
    )
    for row in report["comparisons"]:
        lines.append(
            f"| {row['memory_basis']} | {row['physical_error']:.4g} | {row['target_logical_error']:.4g} | "
            f"{row['baseline_met']} | {row['baseline_space_time_volume'] or 'n/a'} | "
            f"{row['candidate_met']} | {row['candidate_variant'] or 'n/a'} | "
            f"{row['candidate_space_time_volume'] or 'n/a'} | "
            f"{fmt_ratio(row['volume_reduction_vs_baseline'])} | {row['interpretation']} |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=Path("results/B2_stim_surface_code_memory_baseline_v0.json"))
    parser.add_argument("--target-volume", type=Path, default=Path("results/B2_stim_surface_code_target_volume_v0.json"))
    parser.add_argument("--targets", default="1e-1,5e-2,1e-2,1e-3")
    parser.add_argument("--criterion", choices=["wilson_95_high", "observed_logical_error_rate"], default="wilson_95_high")
    parser.add_argument("--json-output", type=Path, default=Path("results/B2_biased_schedule_proxy_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B2_biased_schedule_proxy.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    target_report = json.loads(args.target_volume.read_text(encoding="utf-8"))
    report = compare(baseline, target_report, parse_float_list(args.targets), args.criterion)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "target_combinations": report["target_combinations"],
                    "candidate_met_count": report["candidate_met_count"],
                    "improved_volume_count": report["improved_volume_count"],
                    "candidate_only_meets_target_count": report["candidate_only_meets_target_count"],
                    "mean_volume_reduction_on_improved": report["mean_volume_reduction_on_improved"],
                    "max_volume_reduction": report["max_volume_reduction"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
