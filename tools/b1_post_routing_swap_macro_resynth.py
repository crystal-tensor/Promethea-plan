#!/usr/bin/env python3
"""Compress post-routing CX-CX-CX SWAP macros in B1 routed circuits."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\([^)]*\))?\s+(.+);$")
QUBIT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]")


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def parse_gate(line: str) -> dict | None:
    code = strip_comment(line)
    if not code or code.startswith("measure"):
        return None
    match = GATE_RE.match(code)
    if not match:
        return None
    return {
        "gate": match.group(1).lower(),
        "params": match.group(2) or "",
        "qubits": tuple(f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(match.group(3))),
        "raw": code,
    }


def is_swap_macro(first: dict, second: dict, third: dict) -> bool:
    if first["gate"] != "cx" or second["gate"] != "cx" or third["gate"] != "cx":
        return False
    if len(first["qubits"]) != 2 or len(second["qubits"]) != 2 or len(third["qubits"]) != 2:
        return False
    left, right = first["qubits"]
    return second["qubits"] == (right, left) and third["qubits"] == (left, right)


def swap_line(first: dict) -> str:
    left, right = first["qubits"]
    return f"swap {left},{right};"


def rewrite_lines(lines: list[str], file_path: Path) -> tuple[list[str], list[dict]]:
    output: list[str] = []
    certificates: list[dict] = []
    idx = 0
    while idx < len(lines):
        first = parse_gate(lines[idx])
        second = parse_gate(lines[idx + 1]) if idx + 1 < len(lines) else None
        third = parse_gate(lines[idx + 2]) if idx + 2 < len(lines) else None
        if first and second and third and is_swap_macro(first, second, third):
            output.append(swap_line(first))
            certificates.append(
                {
                    "rule": "cx_cx_cx_to_swap_macro",
                    "certificate_type": "local_2q_swap_macro_identity",
                    "input_file": str(file_path),
                    "input_line_numbers": [idx + 1, idx + 2, idx + 3],
                    "input_gates": [first["raw"], second["raw"], third["raw"]],
                    "output_gate": swap_line(first),
                    "left": first["qubits"][0],
                    "right": first["qubits"][1],
                    "removed_cx_gates": 3,
                    "inserted_swap_gates": 1,
                    "operation_reduction": 2,
                    "two_qubit_macro_reduction": 2,
                }
            )
            idx += 3
            continue
        output.append(lines[idx])
        idx += 1
    return output, certificates


def qasm_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix == ".qasm":
        return [path]
    return sorted(path.rglob("*.qasm"))


def rewrite_tree(input_dir: Path, output_dir: Path, proof_log: Path) -> dict:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    proof_log.parent.mkdir(parents=True, exist_ok=True)
    if proof_log.exists():
        proof_log.unlink()

    rows = []
    totals = {
        "circuit_count": 0,
        "swap_macros": 0,
        "removed_cx_gates": 0,
        "inserted_swap_gates": 0,
        "operation_reduction": 0,
        "two_qubit_macro_reduction": 0,
    }
    with proof_log.open("w", encoding="utf-8") as handle:
        for source in qasm_files(input_dir):
            relative = source.relative_to(input_dir) if input_dir.is_dir() else Path(source.name)
            target = output_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            lines = source.read_text(encoding="utf-8").splitlines()
            rewritten, certificates = rewrite_lines(lines, source)
            target.write_text("\n".join(rewritten) + "\n", encoding="utf-8")
            for certificate in certificates:
                certificate = {"output_file": str(target), **certificate}
                handle.write(json.dumps(certificate, sort_keys=True) + "\n")
            row = {
                "input": str(source),
                "output": str(target),
                "relative_path": str(relative),
                "swap_macros": len(certificates),
                "removed_cx_gates": 3 * len(certificates),
                "inserted_swap_gates": len(certificates),
                "operation_reduction": 2 * len(certificates),
                "two_qubit_macro_reduction": 2 * len(certificates),
            }
            rows.append(row)
            totals["circuit_count"] += 1
            for key in [
                "swap_macros",
                "removed_cx_gates",
                "inserted_swap_gates",
                "operation_reduction",
                "two_qubit_macro_reduction",
            ]:
                totals[key] += row[key]
    return {**totals, "circuits": rows}


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess:
    completed = subprocess.run(command, check=check, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def totals(metrics: dict) -> dict[str, float]:
    rows = metrics["results"]
    return {
        key: sum(float(row[key]) for row in rows)
        for key in [
            "operation_count",
            "two_qubit_gate_count",
            "logical_depth",
            "hardware_weighted_error_exposure",
            "idle_layer_proxy",
        ]
    }


def reduction(before: float, after: float) -> float:
    return (before - after) / before * 100 if before else 0.0


def summarize(
    rewrite_report: dict,
    before_metrics_path: Path,
    after_metrics_path: Path,
    local_aer_path: Path,
    end_to_end_aer_path: Path | None,
    input_dir: Path,
    output_dir: Path,
    proof_log: Path,
) -> dict:
    before = read_json(before_metrics_path)
    after = read_json(after_metrics_path)
    local_aer = read_json(local_aer_path)
    end_to_end_aer = read_json(end_to_end_aer_path) if end_to_end_aer_path and end_to_end_aer_path.exists() else None
    before_totals = totals(before)
    after_totals = totals(after)
    metric_summary = {}
    for key in before_totals:
        metric_summary[key] = {
            "before": before_totals[key],
            "after": after_totals[key],
            "delta": after_totals[key] - before_totals[key],
            "reduction_pct": reduction(before_totals[key], after_totals[key]),
        }
    top_circuits = sorted(
        rewrite_report["circuits"],
        key=lambda row: (row["swap_macros"], row["two_qubit_macro_reduction"]),
        reverse=True,
    )[:10]
    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 post-routing SWAP macro compression diagnostic",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "report_status": "post_routing_swap_macro_diagnostic_not_native_basis_claim",
        "method": "post_routing_cx_cx_cx_to_swap_macro_v0",
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "proof_log": str(proof_log),
        "before_metrics": str(before_metrics_path),
        "after_metrics": str(after_metrics_path),
        "circuit_count": rewrite_report["circuit_count"],
        "swap_macros": rewrite_report["swap_macros"],
        "removed_cx_gates": rewrite_report["removed_cx_gates"],
        "inserted_swap_gates": rewrite_report["inserted_swap_gates"],
        "operation_reduction_from_rewrite": rewrite_report["operation_reduction"],
        "two_qubit_macro_reduction_from_rewrite": rewrite_report["two_qubit_macro_reduction"],
        "metrics": metric_summary,
        "local_aer_crosscheck": {
            "path": str(local_aer_path),
            "passed": local_aer.get("passed"),
            "failed": local_aer.get("failed"),
            "shots": local_aer.get("shots"),
            "max_total_variation_distance": local_aer.get("max_total_variation_distance"),
        },
        "end_to_end_aer_crosscheck": {
            "path": str(end_to_end_aer_path) if end_to_end_aer_path else None,
            "passed": end_to_end_aer.get("passed") if end_to_end_aer else None,
            "failed": end_to_end_aer.get("failed") if end_to_end_aer else None,
            "shots": end_to_end_aer.get("shots") if end_to_end_aer else None,
            "max_total_variation_distance": end_to_end_aer.get("max_total_variation_distance") if end_to_end_aer else None,
        },
        "top_circuits_by_swap_macros": top_circuits,
        "limits": [
            "The pass rewrites a routed CX-CX-CX SWAP implementation into an OpenQASM swap macro.",
            "This is a routing-aware IR/macro compression diagnostic, not a calibrated native-basis hardware claim.",
            "If the target backend decomposes swap back into CX gates, the physical two-qubit-gate reduction does not hold without a native swap or a lower-cost swap implementation.",
        ],
    }


def fmt_pct(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}%"


def markdown(report: dict) -> str:
    lines = [
        "# B1 Post-Routing SWAP Macro Compression Diagnostic v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['report_status']}**",
        "",
        "## Summary",
        "",
        f"- Circuits: {report['circuit_count']}",
        f"- SWAP macros identified: {report['swap_macros']}",
        f"- Removed CX gates: {report['removed_cx_gates']}",
        f"- Inserted SWAP macros: {report['inserted_swap_gates']}",
        f"- Local Aer cross-check pass/fail: {report['local_aer_crosscheck']['passed']} / {report['local_aer_crosscheck']['failed']}",
        f"- End-to-end Aer cross-check pass/fail: {report['end_to_end_aer_crosscheck']['passed']} / {report['end_to_end_aer_crosscheck']['failed']}",
        "",
        "## Metric Deltas",
        "",
        "| Metric | Before | After | Delta | Reduction |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, row in report["metrics"].items():
        lines.append(
            f"| {key} | {row['before']:.6g} | {row['after']:.6g} | "
            f"{row['delta']:.6g} | {fmt_pct(row['reduction_pct'])} |"
        )
    lines.extend(
        [
            "",
            "## Top Circuits By SWAP Macros",
            "",
            "| Circuit | SWAP macros | Removed CX | 2Q macro reduction |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in report["top_circuits_by_swap_macros"]:
        lines.append(
            f"| `{row['relative_path']}` | {row['swap_macros']} | "
            f"{row['removed_cx_gates']} | {row['two_qubit_macro_reduction']} |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("results/b1_heavyhex_end_to_end_30_level1_work/03_b1_heavyhex_d3_level1"))
    parser.add_argument("--source-logical-dir", type=Path, default=Path("results/b1_heavyhex_end_to_end_30_level1_work/00_source"))
    parser.add_argument("--work-dir", type=Path, default=Path("results/b1_post_routing_swap_macro_level1_work"))
    parser.add_argument("--results-dir", type=Path, default=Path("results/b1_post_routing_swap_macro_level1"))
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument("--aer-shots", type=int, default=2048)
    parser.add_argument("--aer-method", default="matrix_product_state")
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_post_routing_swap_macro_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_post_routing_swap_macro_report.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    output_dir = args.work_dir.resolve() / "01_swap_macro"
    results_dir = args.results_dir.resolve()
    results_dir.mkdir(parents=True, exist_ok=True)
    proof_log = results_dir / "swap_macro_proofs.jsonl"
    before_metrics = results_dir / "before_swap_macro_metrics.json"
    after_metrics = results_dir / "after_swap_macro_metrics.json"
    local_aer = results_dir / "b1_routed_vs_swap_macro_aer_crosscheck.json"
    end_to_end_aer = results_dir / "source_logical_vs_swap_macro_aer_crosscheck.json"

    rewrite_report = rewrite_tree(input_dir, output_dir, proof_log)
    for directory, output in [(input_dir, before_metrics), (output_dir, after_metrics)]:
        run(
            [
                sys.executable,
                "tools/b1_qasm_metrics.py",
                str(directory),
                "--profile",
                args.profile,
                "--pretty",
                "--output",
                str(output),
            ]
        )
    run(
        [
            sys.executable,
            "tools/b1_aer_measurement_crosscheck.py",
            str(input_dir),
            str(output_dir),
            "--shots",
            str(args.aer_shots),
            "--method",
            args.aer_method,
            "--pretty",
            "--output",
            str(local_aer),
        ],
        check=False,
    )
    run(
        [
            sys.executable,
            "tools/b1_aer_measurement_crosscheck.py",
            str(args.source_logical_dir.resolve()),
            str(output_dir),
            "--shots",
            str(args.aer_shots),
            "--method",
            args.aer_method,
            "--pretty",
            "--output",
            str(end_to_end_aer),
        ],
        check=False,
    )
    report = summarize(
        rewrite_report,
        before_metrics,
        after_metrics,
        local_aer,
        end_to_end_aer,
        input_dir,
        output_dir,
        proof_log,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if report["local_aer_crosscheck"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
