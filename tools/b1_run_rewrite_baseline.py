#!/usr/bin/env python3
"""Run the B1 local-rewrite baseline with metrics and equivalence checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(before_path: Path, after_path: Path, equivalence_path: Path) -> dict:
    before = load_json(before_path)
    after = load_json(after_path)
    equivalence = load_json(equivalence_path)

    before_results = before["results"]
    after_results = after["results"]

    def total(key: str, results: list[dict]) -> float:
        return sum(float(result[key]) for result in results)

    before_exposure = total("hardware_weighted_error_exposure", before_results)
    after_exposure = total("hardware_weighted_error_exposure", after_results)
    before_ops = total("operation_count", before_results)
    after_ops = total("operation_count", after_results)
    before_depth = total("logical_depth", before_results)
    after_depth = total("logical_depth", after_results)

    return {
        "benchmark_id": "B1",
        "profile": before["profile"],
        "circuit_count": before["circuit_count"],
        "equivalence_passed": equivalence["passed"],
        "equivalence_failed": equivalence["failed"],
        "total_operation_count_before": before_ops,
        "total_operation_count_after": after_ops,
        "operation_count_delta": after_ops - before_ops,
        "total_logical_depth_before": before_depth,
        "total_logical_depth_after": after_depth,
        "logical_depth_delta": after_depth - before_depth,
        "total_hardware_weighted_exposure_before": before_exposure,
        "total_hardware_weighted_exposure_after": after_exposure,
        "hardware_weighted_exposure_delta": after_exposure - before_exposure,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Input OpenQASM file or directory")
    parser.add_argument("--rewritten-dir", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument("--label", default="rewrite_baseline")
    args = parser.parse_args(argv)

    args.results_dir.mkdir(parents=True, exist_ok=True)
    before_path = args.results_dir / f"{args.label}_before_metrics.json"
    after_path = args.results_dir / f"{args.label}_after_metrics.json"
    equivalence_path = args.results_dir / f"{args.label}_equivalence.json"
    summary_path = args.results_dir / f"{args.label}_summary.json"

    run(
        [
            sys.executable,
            "tools/b1_local_rewriter.py",
            str(args.input),
            "--output-dir",
            str(args.rewritten_dir),
        ]
    )
    run(
        [
            sys.executable,
            "tools/b1_qasm_metrics.py",
            str(args.input),
            "--profile",
            args.profile,
            "--pretty",
            "--output",
            str(before_path),
        ]
    )
    run(
        [
            sys.executable,
            "tools/b1_qasm_metrics.py",
            str(args.rewritten_dir),
            "--profile",
            args.profile,
            "--pretty",
            "--output",
            str(after_path),
        ]
    )
    run(
        [
            sys.executable,
            "tools/b1_equivalence_check.py",
            str(args.input),
            str(args.rewritten_dir),
            "--pretty",
            "--output",
            str(equivalence_path),
        ]
    )

    summary = summarize(before_path, after_path, equivalence_path)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
