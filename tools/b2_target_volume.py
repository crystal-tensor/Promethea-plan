#!/usr/bin/env python3
"""Compute B2 space-time volume needed to hit target logical error rates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def compute_targets(baseline: dict, targets: list[float]) -> dict:
    rows = baseline["results"]
    physical_errors = sorted({float(row["physical_error"]) for row in rows})
    output_rows = []
    for physical_error in physical_errors:
        candidates = [row for row in rows if float(row["physical_error"]) == physical_error]
        candidates.sort(key=lambda row: (float(row["space_time_volume"]), int(row["distance"])))
        for target in targets:
            feasible = [
                row
                for row in candidates
                if float(row["logical_error_rate_exact"]) <= target
            ]
            if feasible:
                best = feasible[0]
                output_rows.append(
                    {
                        "physical_error": physical_error,
                        "target_logical_error": target,
                        "met": True,
                        "distance": best["distance"],
                        "physical_qubits": best["physical_qubits"],
                        "rounds": best["rounds"],
                        "space_time_volume": best["space_time_volume"],
                        "logical_error_rate_exact": best["logical_error_rate_exact"],
                        "logical_error_rate_mc": best["logical_error_rate_mc"],
                    }
                )
            else:
                best_available = min(candidates, key=lambda row: float(row["logical_error_rate_exact"]))
                output_rows.append(
                    {
                        "physical_error": physical_error,
                        "target_logical_error": target,
                        "met": False,
                        "distance": None,
                        "physical_qubits": None,
                        "rounds": None,
                        "space_time_volume": None,
                        "best_available_distance": best_available["distance"],
                        "best_available_logical_error_exact": best_available["logical_error_rate_exact"],
                    }
                )
    met_count = sum(1 for row in output_rows if row["met"])
    return {
        "benchmark_id": "B2",
        "method": "target_space_time_volume_from_repetition_baseline_v0",
        "source_method": baseline["method"],
        "source_seed": baseline["seed"],
        "source_shots": baseline["shots"],
        "target_count": len(targets),
        "physical_error_count": len(physical_errors),
        "met_count": met_count,
        "unmet_count": len(output_rows) - met_count,
        "results": output_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("--targets", default="1e-2,1e-3,1e-4,1e-5")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    targets = [float(item.strip()) for item in args.targets.split(",") if item.strip()]
    payload = compute_targets(baseline, targets)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
