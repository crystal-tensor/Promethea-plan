#!/usr/bin/env python3
"""Expose U3 Z phases, then reuse control-RZ commuting.

This T-B1-003 diagnostic is deliberately conservative. It rewrites

    u3(theta, phi, lambda) q[i]

into the OpenQASM-equivalent native Euler sequence

    rz(lambda) q[i]; ry(theta) q[i]; rz(phi) q[i];

up to global phase. OpenQASM executes gates in program order, so this sequence
realizes the matrix product Rz(phi) Ry(theta) Rz(lambda). The tool then applies
the existing control-RZ commute/merge pass. The purpose is to expose Z phases
hidden inside U3 gates so the B1/B7 T-resource proxy can test whether
additional magic-state factory pressure is removable without making a broad
final compiler claim.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import shutil
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from b1_control_rz_commute_optimizer import (
    aggregate_t_resources,
    compute_directory_metrics,
    load_crosscheck,
    metric_aggregate,
    pct_reduction,
    ratio,
    rewrite_file as commute_rz_file,
    top_t_changes,
)
from b1_qasm_metrics import find_qasm_files
from b7_logical_t_factory_scheduler import qasm_t_resources


GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\([^)]*\))?\s+(.+);$")
QUBIT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def strip_comment(line: str) -> tuple[str, str]:
    if "//" not in line:
        return line.strip(), ""
    code, comment = line.split("//", 1)
    return code.strip(), "//" + comment


def safe_eval_angle(expr: str) -> float:
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Constant,
        ast.Name,
        ast.Load,
    )
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(expr)
        if isinstance(node, ast.Name) and node.id != "pi":
            raise ValueError(expr)
    return float(eval(compile(tree, "<angle>", "eval"), {"__builtins__": {}}, {"pi": math.pi}))


def split_params(param_text: str | None) -> list[str]:
    if not param_text:
        return []
    inner = param_text.strip()[1:-1].strip()
    if not inner:
        return []
    return [part.strip() for part in inner.split(",")]


def normalize_angle(value: float) -> float:
    while value <= -math.pi:
        value += 2 * math.pi
    while value > math.pi:
        value -= 2 * math.pi
    return value


def is_zero(value: float, tolerance: float = 1e-12) -> bool:
    return abs(normalize_angle(value)) <= tolerance


def format_angle(value: float) -> str:
    value = normalize_angle(value)
    if abs(value) < 1e-12:
        return "0"
    candidates = [
        (-1, "-pi"),
        (-0.875, "-7*pi/8"),
        (-0.75, "-3*pi/4"),
        (-0.625, "-5*pi/8"),
        (-0.5, "-pi/2"),
        (-0.375, "-3*pi/8"),
        (-0.25, "-pi/4"),
        (-0.125, "-pi/8"),
        (0.125, "pi/8"),
        (0.25, "pi/4"),
        (0.375, "3*pi/8"),
        (0.5, "pi/2"),
        (0.625, "5*pi/8"),
        (0.75, "3*pi/4"),
        (0.875, "7*pi/8"),
        (1, "pi"),
    ]
    units = value / math.pi
    for candidate, text in candidates:
        if abs(units - candidate) < 1e-12:
            return text
    return f"{value:.17g}"


def gate_line(gate: str, angle: float, operand: str) -> str | None:
    if is_zero(angle):
        return None
    return f"{gate}({format_angle(angle)}) {operand};"


def factor_u3_line(line: str, line_number: int) -> tuple[list[str], dict | None]:
    code, comment = strip_comment(line)
    match = GATE_RE.match(code)
    if not match or match.group(1).lower() not in {"u3", "u"}:
        return [line], None

    params = split_params(match.group(2))
    qubits = QUBIT_RE.findall(match.group(3))
    if len(params) != 3 or len(qubits) != 1:
        return [line], None

    try:
        theta, phi, lam = [safe_eval_angle(param) for param in params]
    except ValueError:
        return [line], None

    operand = f"{qubits[0][0]}[{qubits[0][1]}]"
    components = [
        ("rz", normalize_angle(lam), "right_z_phase_emitted_first"),
        ("ry", normalize_angle(theta), "middle_y_rotation"),
        ("rz", normalize_angle(phi), "left_z_phase_emitted_last"),
    ]
    output: list[str] = []
    skipped = []
    for gate, angle, role in components:
        rewritten = gate_line(gate, angle, operand)
        if rewritten is None:
            skipped.append(role)
            continue
        output.append(rewritten)

    if comment:
        if output:
            output[-1] = f"{output[-1]} {comment}"
        else:
            output.append(comment)

    certificate = {
        "rule": "u3_to_rz_ry_rz_native_euler",
        "certificate_type": "constructive_u3_euler_factorization_global_phase_ignored",
        "input_line_number": line_number,
        "operand": operand,
        "input_gate": code,
        "theta": normalize_angle(theta),
        "phi": normalize_angle(phi),
        "lambda": normalize_angle(lam),
        "output_gates": [item.split("//", 1)[0].strip() for item in output if not item.strip().startswith("//")],
        "zero_components_removed": skipped,
        "global_phase_ignored": True,
    }
    return output, certificate


def factor_file(input_path: Path, output_path: Path) -> dict:
    output_lines: list[str] = []
    certificates: list[dict] = []
    for line_number, line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), 1):
        rewritten, certificate = factor_u3_line(line, line_number)
        output_lines.extend(rewritten)
        if certificate is not None:
            certificates.append(certificate)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    emitted = [gate for event in certificates for gate in event["output_gates"]]
    return {
        "input": str(input_path),
        "output": str(output_path),
        "u3_factorization_events": len(certificates),
        "identity_u3_removed": sum(1 for event in certificates if not event["output_gates"]),
        "rz_components_emitted": sum(1 for gate in emitted if gate.startswith("rz(")),
        "ry_components_emitted": sum(1 for gate in emitted if gate.startswith("ry(")),
        "zero_components_removed": sum(len(event["zero_components_removed"]) for event in certificates),
        "certificates": certificates,
    }


def factor_directory(input_dir: Path, factorized_dir: Path) -> tuple[list[dict], list[dict]]:
    rows = []
    certificates = []
    for input_path in find_qasm_files([input_dir]):
        output_path = factorized_dir / input_path.relative_to(input_dir)
        row = factor_file(input_path, output_path)
        rows.append({key: value for key, value in row.items() if key != "certificates"})
        certificates.extend(
            {**event, "relative_path": str(input_path.relative_to(input_dir))}
            for event in row["certificates"]
        )
    return rows, certificates


def commute_directory(factorized_dir: Path, output_dir: Path) -> tuple[list[dict], list[dict]]:
    rows = []
    certificates = []
    for input_path in find_qasm_files([factorized_dir]):
        output_path = output_dir / input_path.relative_to(factorized_dir)
        row = commute_rz_file(input_path, output_path)
        rows.append({key: value for key, value in row.items() if key != "certificates"})
        certificates.extend(
            {**event, "relative_path": str(input_path.relative_to(factorized_dir))}
            for event in row["certificates"]
        )
    return rows, certificates


def factor_stats(rows: list[dict], certificates: list[dict]) -> dict:
    return {
        "rewritten_circuits": len(rows),
        "circuits_changed": sum(1 for row in rows if row["u3_factorization_events"] > 0),
        "u3_factorization_events": sum(row["u3_factorization_events"] for row in rows),
        "identity_u3_removed": sum(row["identity_u3_removed"] for row in rows),
        "rz_components_emitted": sum(row["rz_components_emitted"] for row in rows),
        "ry_components_emitted": sum(row["ry_components_emitted"] for row in rows),
        "zero_components_removed": sum(row["zero_components_removed"] for row in rows),
        "certificate_entries": len(certificates),
    }


def commute_stats(rows: list[dict], certificates: list[dict]) -> dict:
    return {
        "rewritten_circuits": len(rows),
        "circuits_changed": sum(1 for row in rows if row["removed_rz_gates"] > 0 or row["commuted_cx_count"] > 0),
        "absorbed_rz_gates": sum(row["absorbed_rz_gates"] for row in rows),
        "certificate_entries": len(certificates),
        "merged_or_moved_groups": sum(row["merged_or_moved_groups"] for row in rows),
        "removed_rz_gates": sum(row["removed_rz_gates"] for row in rows),
        "commuted_cx_count": sum(row["commuted_cx_count"] for row in rows),
        "zero_output_groups": sum(row["zero_output_groups"] for row in rows),
    }


def status(t_summary: dict, factor: dict, commute: dict) -> str:
    if factor["u3_factorization_events"] == 0:
        return "u3_phase_factored_no_u3_boundary"
    if commute["removed_rz_gates"] == 0:
        return "u3_phase_factored_no_additional_merge_boundary"
    if (t_summary["logical_t_count_reduction"] or 0) > 1.0:
        return "u3_phase_factored_positive_diagnostic_not_final_claim"
    return "u3_phase_factored_boundary"


def run(args: argparse.Namespace) -> dict:
    input_dir = args.input_dir.resolve()
    factorized_dir = args.factorized_dir.resolve()
    output_dir = args.output_dir.resolve()
    if not input_dir.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    if args.clean_output:
        for path in [factorized_dir, output_dir]:
            if path.exists():
                shutil.rmtree(path)

    qasm_files = find_qasm_files([input_dir])
    if not qasm_files:
        raise ValueError(f"No .qasm files found under {input_dir}")

    factor_rows, factor_certificates = factor_directory(input_dir, factorized_dir)
    commute_rows, commute_certificates = commute_directory(factorized_dir, output_dir)

    if args.certificate_log:
        args.certificate_log.parent.mkdir(parents=True, exist_ok=True)
        with args.certificate_log.open("w", encoding="utf-8") as handle:
            for event in factor_certificates:
                handle.write(json.dumps({"stage": "u3_factorization", **event}, sort_keys=True) + "\n")
            for event in commute_certificates:
                handle.write(json.dumps({"stage": "control_rz_commute", **event}, sort_keys=True) + "\n")

    before_metrics = compute_directory_metrics(input_dir, args.before_metrics_output, args.hardware_profiles, args.profile)
    after_metrics = compute_directory_metrics(output_dir, args.after_metrics_output, args.hardware_profiles, args.profile)
    before_agg = metric_aggregate(before_metrics)
    after_agg = metric_aggregate(after_metrics)
    metric_summary = {
        "before": before_agg,
        "after": after_agg,
        "reduction_pct": {key: pct_reduction(before_agg[key], after_agg[key]) for key in before_agg},
    }

    before_t_rows = [qasm_t_resources(path, args.rotation_t_cost) for path in qasm_files]
    after_t_rows = [qasm_t_resources(output_dir / path.relative_to(input_dir), args.rotation_t_cost) for path in qasm_files]
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
        "unknown_rotation_count_reduction": ratio(before_t["unknown_rotation_count"], after_t["unknown_rotation_count"]),
    }
    factor = factor_stats(factor_rows, factor_certificates)
    commute = commute_stats(commute_rows, commute_certificates)

    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 U3 phase-factored optimizer diagnostic",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": status(t_summary, factor, commute),
        "method": "u3_native_euler_factorization_plus_control_rz_commute_v0",
        "input_dir": str(input_dir),
        "factorized_dir": str(factorized_dir),
        "output_dir": str(output_dir),
        "rotation_synthesis_t_cost": args.rotation_t_cost,
        "factorization_stats": factor,
        "commute_stats": commute,
        "factorization_rows": factor_rows,
        "commute_rows": commute_rows,
        "metrics": metric_summary,
        "t_resource_proxy": t_summary,
        "top_circuits_by_t_reduction": top_t_changes(before_t_rows, after_t_rows, input_dir, output_dir),
        "before_metrics": str(args.before_metrics_output),
        "after_metrics": str(args.after_metrics_output),
        "certificate_log": str(args.certificate_log) if args.certificate_log else None,
        "aer_crosscheck": load_crosscheck(args.aer_crosscheck),
        "limits": [
            "U3 factorization is exact only up to global phase, which is irrelevant for measurement distributions.",
            "This pass exposes U3 Z phases and reuses the narrow control-RZ commute rule; it is not a complete phase-polynomial optimizer.",
            "Operation count may increase because U3 gates become native rotation components; the relevant diagnostic target is logical T-resource pressure.",
            "Any B7 improvement remains a logical T-factory proxy until checked against a full fault-tolerant synthesis/layout ledger.",
        ],
    }


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}%"


def fmt_ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}x"


def markdown(report: dict) -> str:
    factor = report["factorization_stats"]
    commute = report["commute_stats"]
    metrics = report["metrics"]
    t_proxy = report["t_resource_proxy"]
    lines = [
        "# B1 U3 Phase-Factored Optimizer Diagnostic v0.1",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Input directory: `{report['input_dir']}`",
        f"- Factorized directory: `{report['factorized_dir']}`",
        f"- Output directory: `{report['output_dir']}`",
        f"- U3 factorization events: {factor['u3_factorization_events']}",
        f"- RZ components emitted: {factor['rz_components_emitted']}",
        f"- RY components emitted: {factor['ry_components_emitted']}",
        f"- Zero components removed: {factor['zero_components_removed']}",
        f"- RZ commute certificate events: {commute['certificate_entries']}",
        f"- Removed RZ gates after factoring: {commute['removed_rz_gates']}",
        f"- CNOT-control commutations after factoring: {commute['commuted_cx_count']}",
        f"- Logical T-count proxy reduction: {fmt_ratio(t_proxy['logical_t_count_reduction'])}",
        f"- Logical T-depth proxy reduction: {fmt_ratio(t_proxy['logical_t_depth_reduction'])}",
        f"- Non-Clifford rotation-count reduction: {fmt_ratio(t_proxy['non_clifford_rotation_count_reduction'])}",
        "",
        "## Aggregate Metrics",
        "",
        "| metric | before | after | reduction |",
        "|---|---:|---:|---:|",
    ]
    for key, before in metrics["before"].items():
        after = metrics["after"][key]
        lines.append(f"| {key} | {before:.6g} | {after:.6g} | {fmt_pct(metrics['reduction_pct'][key])} |")

    lines.extend(["", "## T-Resource Proxy", "", "| metric | before | after | reduction |", "|---|---:|---:|---:|"])
    for key in [
        "logical_t_count_proxy",
        "logical_t_depth_proxy",
        "non_clifford_rotation_count",
        "unknown_rotation_count",
        "operation_count_scanned",
    ]:
        before = t_proxy["before"][key]
        after = t_proxy["after"][key]
        lines.append(f"| {key} | {before} | {after} | {fmt_ratio(ratio(before, after))} |")

    lines.extend(
        [
            "",
            "## Top Circuit Changes",
            "",
            "| circuit | T-count proxy delta | T-depth proxy delta | non-Clifford delta |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in report["top_circuits_by_t_reduction"]:
        lines.append(
            f"| {row['relative_path']} | {row['logical_t_count_proxy_reduction']} | "
            f"{row['logical_t_depth_proxy_reduction']} | {row['non_clifford_rotation_count_reduction']} |"
        )

    if report["aer_crosscheck"]:
        cross = report["aer_crosscheck"]
        lines.extend(
            [
                "",
                "## Aer Cross-Check",
                "",
                f"- Pair count: {cross['pair_count']}",
                f"- Passed/failed: {cross['passed']} / {cross['failed']}",
                f"- Max TVD: {cross['max_total_variation_distance']}",
                f"- Max threshold: {cross['max_threshold']}",
            ]
        )

    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("results/b1_control_rz_commute_optimizer"))
    parser.add_argument("--factorized-dir", type=Path, default=Path("results/b1_u3_phase_factored_intermediate"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/b1_u3_phase_factored_optimizer"))
    parser.add_argument("--hardware-profiles", type=Path, default=Path("benchmarks/hardware_profiles.json"))
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument("--rotation-t-cost", type=int, default=20)
    parser.add_argument("--clean-output", action="store_true")
    parser.add_argument("--before-metrics-output", type=Path, default=Path("results/b1_u3_phase_factored_optimizer/before_metrics.json"))
    parser.add_argument("--after-metrics-output", type=Path, default=Path("results/b1_u3_phase_factored_optimizer/after_metrics.json"))
    parser.add_argument("--certificate-log", type=Path, default=Path("results/b1_u3_phase_factored_optimizer/proofs.jsonl"))
    parser.add_argument("--aer-crosscheck", type=Path, default=Path("results/b1_u3_phase_factored_optimizer/aer_crosscheck.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B1_u3_phase_factored_optimizer_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_u3_phase_factored_optimizer.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.json_output, report)
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "u3_factorization_events": report["factorization_stats"]["u3_factorization_events"],
                    "removed_rz_gates": report["commute_stats"]["removed_rz_gates"],
                    "commuted_cx_count": report["commute_stats"]["commuted_cx_count"],
                    "logical_t_count_reduction": report["t_resource_proxy"]["logical_t_count_reduction"],
                    "logical_t_depth_reduction": report["t_resource_proxy"]["logical_t_depth_reduction"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
