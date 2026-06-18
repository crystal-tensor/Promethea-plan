#!/usr/bin/env python3
"""Aggregate exact-checked B1 pipeline summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


METRICS = [
    ("operation_count", "operation_count"),
    ("two_qubit_gate_count", "two_qubit_gate_count"),
    ("logical_depth", "logical_depth"),
    ("hardware_weighted_exposure", "hardware_weighted_exposure"),
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(before: float, after: float) -> float:
    return (before - after) / before * 100 if before else 0.0


def before_metrics_path(summary_path: Path) -> Path:
    name = summary_path.name
    if not name.endswith("_summary.json"):
        return summary_path.with_name("before_metrics.json")
    return summary_path.with_name(name.replace("_summary.json", "_before_metrics.json"))


def max_qubits_from_metrics(summary_path: Path) -> int | None:
    metrics_path = before_metrics_path(summary_path)
    if not metrics_path.exists():
        return None
    payload = load_json(metrics_path)
    return max(int(row.get("qubits", 0)) for row in payload.get("results", []))


def normalize(path: Path) -> dict:
    data = load_json(path)
    if "aggregate_circuit_count" in data:
        subsets = data.get("subsets", [])
        return {
            "name": path.stem.replace("_summary", ""),
            "summary": str(path),
            "circuits": int(data["aggregate_circuit_count"]),
            "equivalence_failed": int(data["aggregate_equivalence_failed"]),
            "operation_count_before": float(data["aggregate_operation_count_before"]),
            "operation_count_after": float(data["aggregate_operation_count_after"]),
            "two_qubit_gate_count_before": float(data["aggregate_two_qubit_gate_count_before"]),
            "two_qubit_gate_count_after": float(data["aggregate_two_qubit_gate_count_after"]),
            "logical_depth_before": float(data["aggregate_logical_depth_before"]),
            "logical_depth_after": float(data["aggregate_logical_depth_after"]),
            "hardware_weighted_exposure_before": float(data["aggregate_hardware_weighted_exposure_before"]),
            "hardware_weighted_exposure_after": float(data["aggregate_hardware_weighted_exposure_after"]),
            "subsets": subsets,
        }

    equivalence_failed = data.get("equivalence_failed")
    if equivalence_failed is None:
        raise ValueError(f"{path} is not an exact-checked summary")
    name = path.stem.replace("_summary", "")
    max_qubits = max_qubits_from_metrics(path)
    subset = {
        "name": name,
        "summary": str(path),
        "circuits": int(data["circuit_count"]),
        "max_qubits": max_qubits,
        "equivalence_failed": int(equivalence_failed),
        "operation_count_reduction_pct": data["operation_count_reduction_pct"],
        "two_qubit_gate_count_reduction_pct": data["two_qubit_gate_count_reduction_pct"],
        "logical_depth_reduction_pct": data["logical_depth_reduction_pct"],
        "heavy_hex_like_exposure_reduction_pct": data["hardware_weighted_exposure_reduction_pct"],
        "rzz_windows": [row["windows"] for row in data.get("rzz_passes", [])],
    }
    return {
        "name": name,
        "summary": str(path),
        "circuits": int(data["circuit_count"]),
        "equivalence_failed": int(equivalence_failed),
        "operation_count_before": float(data["operation_count_before"]),
        "operation_count_after": float(data["operation_count_after"]),
        "two_qubit_gate_count_before": float(data["two_qubit_gate_count_before"]),
        "two_qubit_gate_count_after": float(data["two_qubit_gate_count_after"]),
        "logical_depth_before": float(data["logical_depth_before"]),
        "logical_depth_after": float(data["logical_depth_after"]),
        "hardware_weighted_exposure_before": float(data["hardware_weighted_exposure_before"]),
        "hardware_weighted_exposure_after": float(data["hardware_weighted_exposure_after"]),
        "subsets": [subset],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summaries", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    rows = [normalize(path) for path in args.summaries]
    totals: dict[str, float] = {}
    for public_key, source_key in METRICS:
        totals[f"aggregate_{public_key}_before"] = sum(row[f"{source_key}_before"] for row in rows)
        totals[f"aggregate_{public_key}_after"] = sum(row[f"{source_key}_after"] for row in rows)
        totals[f"aggregate_{public_key}_reduction_pct"] = pct(
            totals[f"aggregate_{public_key}_before"],
            totals[f"aggregate_{public_key}_after"],
        )

    subsets: list[dict] = []
    for row in rows:
        subsets.extend(row["subsets"])

    payload = {
        "benchmark_id": "B1",
        "method": "fixed_point_commuting_1q_plus_iterative_rzz_v0",
        "aggregate_circuit_count": sum(row["circuits"] for row in rows),
        "aggregate_equivalence_failed": sum(row["equivalence_failed"] for row in rows),
        "input_summaries": [str(path) for path in args.summaries],
        "subsets": subsets,
        **totals,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["aggregate_equivalence_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
