#!/usr/bin/env python3
"""Eliminate routed SWAP macros by tracking virtual wire permutations."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\([^)]*\))?\s+(.+);$")
QREG_RE = re.compile(r"^qreg\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]\s*;")
MEASURE_RE = re.compile(r"^measure\s+(.+?)\s*->\s*(.+);$")
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


def qreg_size(lines: list[str]) -> tuple[str, int]:
    for line in lines:
        match = QREG_RE.match(strip_comment(line))
        if match:
            return match.group(1), int(match.group(2))
    raise ValueError("No qreg declaration found")


def has_nonterminal_measurements(lines: list[str]) -> bool:
    seen_measure = False
    for line in lines:
        code = strip_comment(line)
        if not code:
            continue
        if MEASURE_RE.match(code):
            seen_measure = True
            continue
        if seen_measure and not code.startswith("barrier"):
            return True
    return False


def has_unsupported_dynamic_features(lines: list[str]) -> bool:
    for line in lines:
        code = strip_comment(line)
        if not code:
            continue
        if code.startswith("reset ") or code.startswith("reset\t"):
            return True
        if code.startswith("if(") or code.startswith("if "):
            return True
    return False


def is_swap_macro(first: dict, second: dict, third: dict) -> bool:
    if first["gate"] != "cx" or second["gate"] != "cx" or third["gate"] != "cx":
        return False
    if len(first["qubits"]) != 2 or len(second["qubits"]) != 2 or len(third["qubits"]) != 2:
        return False
    left, right = first["qubits"]
    return second["qubits"] == (right, left) and third["qubits"] == (left, right)


def remap_qubit(token: str, wire_map: dict[str, str]) -> str:
    return wire_map.get(token, token)


def remap_operands(text: str, wire_map: dict[str, str]) -> str:
    def replace(match: re.Match) -> str:
        token = f"{match.group(1)}[{match.group(2)}]"
        return remap_qubit(token, wire_map)

    return QUBIT_RE.sub(replace, text)


def remap_gate_line(line: str, wire_map: dict[str, str]) -> str:
    code = strip_comment(line)
    comment = ""
    if "//" in line:
        comment = " //" + line.split("//", 1)[1].strip()
    measure = MEASURE_RE.match(code)
    if measure:
        return f"measure {remap_operands(measure.group(1), wire_map)} -> {measure.group(2)};{comment}"
    gate = GATE_RE.match(code)
    if gate:
        return f"{gate.group(1)}{gate.group(2) or ''} {remap_operands(gate.group(3), wire_map)};{comment}"
    return line


def rewrite_lines(lines: list[str], file_path: Path) -> tuple[list[str], list[dict], str]:
    if has_unsupported_dynamic_features(lines):
        return lines, [], "skipped_unsupported_dynamic_feature"

    qreg_name, size = qreg_size(lines)
    wire_map = {f"{qreg_name}[{index}]": f"{qreg_name}[{index}]" for index in range(size)}
    status = "rewritten_with_measurement_tracking" if has_nonterminal_measurements(lines) else "rewritten"
    output: list[str] = []
    certificates: list[dict] = []
    idx = 0
    while idx < len(lines):
        first = parse_gate(lines[idx])
        second = parse_gate(lines[idx + 1]) if idx + 1 < len(lines) else None
        third = parse_gate(lines[idx + 2]) if idx + 2 < len(lines) else None
        if first and second and third and is_swap_macro(first, second, third):
            left, right = first["qubits"]
            wire_map[left], wire_map[right] = wire_map[right], wire_map[left]
            certificates.append(
                {
                    "rule": "virtual_swap_elimination",
                    "certificate_type": "wire_permutation_tracking",
                    "input_file": str(file_path),
                    "input_line_numbers": [idx + 1, idx + 2, idx + 3],
                    "input_gates": [first["raw"], second["raw"], third["raw"]],
                    "removed_cx_gates": 3,
                    "left": left,
                    "right": right,
                    "wire_map_after": dict(sorted(wire_map.items())),
                }
            )
            idx += 3
            continue
        output.append(remap_gate_line(lines[idx], wire_map))
        idx += 1
    return output, certificates, status


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

    totals = {
        "circuit_count": 0,
        "rewritten_circuits": 0,
        "skipped_circuits": 0,
        "virtual_swaps_removed": 0,
        "removed_cx_gates": 0,
        "operation_reduction": 0,
    }
    rows = []
    with proof_log.open("w", encoding="utf-8") as handle:
        for source in qasm_files(input_dir):
            relative = source.relative_to(input_dir) if input_dir.is_dir() else Path(source.name)
            target = output_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            lines = source.read_text(encoding="utf-8").splitlines()
            rewritten, certificates, status = rewrite_lines(lines, source)
            target.write_text("\n".join(rewritten) + "\n", encoding="utf-8")
            for certificate in certificates:
                certificate = {"output_file": str(target), **certificate}
                handle.write(json.dumps(certificate, sort_keys=True) + "\n")
            row = {
                "input": str(source),
                "output": str(target),
                "relative_path": str(relative),
                "status": status,
                "virtual_swaps_removed": len(certificates),
                "removed_cx_gates": 3 * len(certificates),
                "operation_reduction": 3 * len(certificates),
            }
            rows.append(row)
            totals["circuit_count"] += 1
            if status.startswith("rewritten"):
                totals["rewritten_circuits"] += 1
            else:
                totals["skipped_circuits"] += 1
            totals["virtual_swaps_removed"] += row["virtual_swaps_removed"]
            totals["removed_cx_gates"] += row["removed_cx_gates"]
            totals["operation_reduction"] += row["operation_reduction"]
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
    end_to_end_aer_path: Path,
    input_dir: Path,
    output_dir: Path,
    proof_log: Path,
) -> dict:
    before = read_json(before_metrics_path)
    after = read_json(after_metrics_path)
    local_aer = read_json(local_aer_path)
    end_to_end_aer = read_json(end_to_end_aer_path)
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
        key=lambda row: (row["virtual_swaps_removed"], row["removed_cx_gates"]),
        reverse=True,
    )[:10]
    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 virtual SWAP elimination diagnostic",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "report_status": "virtual_swap_elimination_diagnostic_not_layout_final_claim",
        "method": "post_routing_virtual_swap_elimination_v0",
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "proof_log": str(proof_log),
        "before_metrics": str(before_metrics_path),
        "after_metrics": str(after_metrics_path),
        "circuit_count": rewrite_report["circuit_count"],
        "rewritten_circuits": rewrite_report["rewritten_circuits"],
        "skipped_circuits": rewrite_report["skipped_circuits"],
        "virtual_swaps_removed": rewrite_report["virtual_swaps_removed"],
        "removed_cx_gates": rewrite_report["removed_cx_gates"],
        "operation_reduction_from_rewrite": rewrite_report["operation_reduction"],
        "metrics": metric_summary,
        "local_aer_crosscheck": {
            "path": str(local_aer_path),
            "passed": local_aer.get("passed"),
            "failed": local_aer.get("failed"),
            "shots": local_aer.get("shots"),
            "max_total_variation_distance": local_aer.get("max_total_variation_distance"),
        },
        "end_to_end_aer_crosscheck": {
            "path": str(end_to_end_aer_path),
            "passed": end_to_end_aer.get("passed"),
            "failed": end_to_end_aer.get("failed"),
            "shots": end_to_end_aer.get("shots"),
            "max_total_variation_distance": end_to_end_aer.get("max_total_variation_distance"),
        },
        "top_circuits_by_virtual_swaps": top_circuits,
        "limits": [
            "The pass removes routed SWAP macros by tracking a virtual wire permutation and remapping later operations.",
            "Measurement operands are remapped through the same wire permutation when no classical control or reset is present.",
            "Circuits with classical control or reset are skipped in v0 because dynamic-layout semantics need a richer model.",
            "This is a post-routing transformation diagnostic, not a final calibrated backend layout claim.",
        ],
    }


def fmt_pct(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}%"


def markdown(report: dict) -> str:
    lines = [
        "# B1 Virtual SWAP Elimination Diagnostic v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['report_status']}**",
        "",
        "## Summary",
        "",
        f"- Circuits: {report['circuit_count']}",
        f"- Rewritten circuits: {report['rewritten_circuits']}",
        f"- Skipped circuits: {report['skipped_circuits']}",
        f"- Virtual SWAPs removed: {report['virtual_swaps_removed']}",
        f"- Removed CX gates: {report['removed_cx_gates']}",
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
            "## Top Circuits By Removed Virtual SWAPs",
            "",
            "| Circuit | Status | Virtual SWAPs removed | Removed CX |",
            "|---|---|---:|---:|",
        ]
    )
    for row in report["top_circuits_by_virtual_swaps"]:
        lines.append(
            f"| `{row['relative_path']}` | {row['status']} | "
            f"{row['virtual_swaps_removed']} | {row['removed_cx_gates']} |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("results/b1_heavyhex_end_to_end_30_level1_work/03_b1_heavyhex_d3_level1"))
    parser.add_argument("--source-logical-dir", type=Path, default=Path("results/b1_heavyhex_end_to_end_30_level1_work/00_source"))
    parser.add_argument("--work-dir", type=Path, default=Path("results/b1_virtual_swap_elimination_level1_work"))
    parser.add_argument("--results-dir", type=Path, default=Path("results/b1_virtual_swap_elimination_level1"))
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument("--aer-shots", type=int, default=2048)
    parser.add_argument("--aer-method", default="matrix_product_state")
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_virtual_swap_elimination_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_virtual_swap_elimination_report.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    output_dir = args.work_dir.resolve() / "01_virtual_swap_eliminated"
    results_dir = args.results_dir.resolve()
    results_dir.mkdir(parents=True, exist_ok=True)
    proof_log = results_dir / "virtual_swap_elimination_proofs.jsonl"
    before_metrics = results_dir / "before_virtual_swap_metrics.json"
    after_metrics = results_dir / "after_virtual_swap_metrics.json"
    local_aer = results_dir / "b1_routed_vs_virtual_swap_aer_crosscheck.json"
    end_to_end_aer = results_dir / "source_logical_vs_virtual_swap_aer_crosscheck.json"

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
    return 0 if report["local_aer_crosscheck"]["failed"] == 0 and report["end_to_end_aer_crosscheck"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
