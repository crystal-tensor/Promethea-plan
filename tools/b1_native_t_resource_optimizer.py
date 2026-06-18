#!/usr/bin/env python3
"""Canonicalize native Z-phase gates to reduce B1 logical T-resource proxies.

This first native-basis pass is intentionally conservative. It only rewrites
OpenQASM u3 gates whose theta parameter is zero, because in that case
u3(0, phi, lambda) is equivalent up to global phase to rz(phi + lambda). This
removes false non-Clifford parameter costs from the B7 logical T factory proxy
without changing measurement semantics.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import shutil
import sys
from pathlib import Path
import re

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from b1_qasm_metrics import compute_metrics, find_qasm_files, load_profiles
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


def format_angle(value: float) -> str:
    value = normalize_angle(value)
    if abs(value) < 1e-12:
        return "0"
    candidates = [
        (-2, "-2*pi"),
        (-1, "-pi"),
        (-0.75, "-3*pi/4"),
        (-0.5, "-pi/2"),
        (-0.25, "-pi/4"),
        (0.25, "pi/4"),
        (0.5, "pi/2"),
        (0.75, "3*pi/4"),
        (1, "pi"),
        (2, "2*pi"),
    ]
    units = value / math.pi
    for candidate, text in candidates:
        if abs(units - candidate) < 1e-12:
            return text
    return f"{value:.17g}"


def is_zero(value: float, tolerance: float = 1e-12) -> bool:
    return abs(normalize_angle(value)) <= tolerance


def rewrite_line(line: str, line_number: int) -> tuple[list[str], dict | None]:
    code, comment = strip_comment(line)
    match = GATE_RE.match(code)
    if not match or match.group(1).lower() != "u3":
        return [line], None

    params = split_params(match.group(2))
    qubits = QUBIT_RE.findall(match.group(3))
    if len(params) != 3 or len(qubits) != 1:
        return [line], None

    try:
        theta, phi, lam = [safe_eval_angle(param) for param in params]
    except ValueError:
        return [line], None

    if not is_zero(theta):
        return [line], None

    operand = f"{qubits[0][0]}[{qubits[0][1]}]"
    phase = normalize_angle(phi + lam)
    certificate = {
        "rule": "u3_zero_theta_to_native_rz",
        "certificate_type": "z_phase_canonicalization",
        "input_line_number": line_number,
        "operand": operand,
        "input_gate": code,
        "theta": theta,
        "phi": phi,
        "lambda": lam,
        "combined_phase": phase,
        "global_phase_ignored": True,
    }
    if is_zero(phase):
        certificate["output_gate"] = None
        certificate["removed_single_qubit_gates"] = 1
        return ([] if not comment else [comment]), certificate

    output = f"rz({format_angle(phase)}) {operand};"
    if comment:
        output = f"{output} {comment}"
    certificate["output_gate"] = output.split("//", 1)[0].strip()
    certificate["removed_single_qubit_gates"] = 0
    return [output], certificate


def rewrite_file(input_path: Path, output_path: Path) -> dict:
    output_lines: list[str] = []
    certificates: list[dict] = []
    for line_number, line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), 1):
        rewritten, certificate = rewrite_line(line, line_number)
        output_lines.extend(rewritten)
        if certificate is not None:
            certificates.append(certificate)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    return {
        "input": str(input_path),
        "output": str(output_path),
        "canonicalization_events": len(certificates),
        "identity_events": sum(1 for event in certificates if event["output_gate"] is None),
        "rz_rewrite_events": sum(1 for event in certificates if event["output_gate"] is not None),
        "removed_single_qubit_gates": sum(event["removed_single_qubit_gates"] for event in certificates),
        "certificates": certificates,
    }


def compute_directory_metrics(input_dir: Path, output_path: Path, profile_path: Path, profile: str) -> dict:
    profiles = load_profiles(profile_path)
    if profile not in profiles:
        raise ValueError(f"Unknown hardware profile {profile!r}; available={sorted(profiles)}")
    rows = [compute_metrics(path, profiles[profile]) for path in find_qasm_files([input_dir])]
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


def top_t_changes(before_rows: list[dict], after_rows: list[dict], input_dir: Path, output_dir: Path) -> list[dict]:
    before_by_key = {relative_key(Path(row["path"]), input_dir): row for row in before_rows}
    after_by_key = {relative_key(Path(row["path"]), output_dir): row for row in after_rows}
    changes = []
    for key in sorted(before_by_key):
        before = before_by_key[key]
        after = after_by_key[key]
        changes.append(
            {
                "relative_path": key,
                "logical_t_count_proxy_reduction": before["logical_t_count_proxy"] - after["logical_t_count_proxy"],
                "logical_t_depth_proxy_reduction": before["logical_t_depth_proxy"] - after["logical_t_depth_proxy"],
                "non_clifford_rotation_count_reduction": before["non_clifford_rotation_count"]
                - after["non_clifford_rotation_count"],
                "unknown_rotation_count_reduction": before["unknown_rotation_count"] - after["unknown_rotation_count"],
            }
        )
    changes.sort(
        key=lambda row: (
            row["logical_t_count_proxy_reduction"],
            row["non_clifford_rotation_count_reduction"],
        ),
        reverse=True,
    )
    return changes[:10]


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


def status(t_summary: dict, rewrite_stats: dict) -> str:
    if rewrite_stats["canonicalization_events"] == 0:
        return "native_t_resource_optimizer_no_opportunity"
    if (t_summary["logical_t_count_reduction"] or 0) > 1.0:
        return "native_t_resource_optimizer_positive_diagnostic_not_final_claim"
    return "native_t_resource_optimizer_canonicalization_boundary"


def run(args: argparse.Namespace) -> dict:
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    if not input_dir.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    if output_dir.exists() and args.clean_output:
        shutil.rmtree(output_dir)

    qasm_files = find_qasm_files([input_dir])
    if not qasm_files:
        raise ValueError(f"No .qasm files found under {input_dir}")

    rewrite_rows = []
    certificate_events = []
    for input_path in qasm_files:
        output_path = output_dir / input_path.relative_to(input_dir)
        row = rewrite_file(input_path, output_path)
        rewrite_rows.append({key: value for key, value in row.items() if key != "certificates"})
        certificate_events.extend(
            {**event, "relative_path": str(input_path.relative_to(input_dir))}
            for event in row["certificates"]
        )
    if args.certificate_log:
        args.certificate_log.parent.mkdir(parents=True, exist_ok=True)
        args.certificate_log.write_text(
            "".join(json.dumps(event, sort_keys=True) + "\n" for event in certificate_events),
            encoding="utf-8",
        )

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
    rewrite_stats = {
        "rewritten_circuits": len(rewrite_rows),
        "canonicalization_events": sum(row["canonicalization_events"] for row in rewrite_rows),
        "identity_events": sum(row["identity_events"] for row in rewrite_rows),
        "rz_rewrite_events": sum(row["rz_rewrite_events"] for row in rewrite_rows),
        "removed_single_qubit_gates": sum(row["removed_single_qubit_gates"] for row in rewrite_rows),
        "certificate_entries": len(certificate_events),
        "circuits_changed": sum(1 for row in rewrite_rows if row["canonicalization_events"] > 0),
    }

    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 native T-resource optimizer diagnostic",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": status(t_summary, rewrite_stats),
        "method": "u3_zero_theta_native_z_phase_canonicalization_v0",
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "rotation_synthesis_t_cost": args.rotation_t_cost,
        "rewrite_stats": rewrite_stats,
        "rewrite_rows": rewrite_rows,
        "metrics": metric_summary,
        "t_resource_proxy": t_summary,
        "top_circuits_by_t_reduction": top_t_changes(before_t_rows, after_t_rows, input_dir, output_dir),
        "before_metrics": str(args.before_metrics_output),
        "after_metrics": str(args.after_metrics_output),
        "certificate_log": str(args.certificate_log) if args.certificate_log else None,
        "aer_crosscheck": load_crosscheck(args.aer_crosscheck),
        "limits": [
            "This pass canonicalizes only theta=0 u3 gates into native Z-phase form.",
            "It is a narrow diagnostic for false T-resource proxy costs, not a complete non-Clifford optimizer.",
            "The rewrite treats global phase as irrelevant to measurement semantics.",
            "A positive proxy reduction must still be propagated through B7 factory schedules before it can support a system claim.",
        ],
    }


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}%"


def fmt_ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}x"


def markdown(report: dict) -> str:
    rewrite = report["rewrite_stats"]
    metrics = report["metrics"]
    t_proxy = report["t_resource_proxy"]
    lines = [
        "# B1 Native T-Resource Optimizer Diagnostic v0.1",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Input directory: `{report['input_dir']}`",
        f"- Output directory: `{report['output_dir']}`",
        f"- Rewritten circuits: {rewrite['rewritten_circuits']}",
        f"- Circuits changed: {rewrite['circuits_changed']}",
        f"- Canonicalization events: {rewrite['canonicalization_events']}",
        f"- Identity events removed: {rewrite['identity_events']}",
        f"- Native `rz` rewrite events: {rewrite['rz_rewrite_events']}",
        f"- Removed 1Q gates: {rewrite['removed_single_qubit_gates']}",
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
    lines.extend(
        [
            "",
            "## T-Resource Proxy",
            "",
            "| metric | before | after | reduction |",
            "|---|---:|---:|---:|",
        ]
    )
    t_before = t_proxy["before"]
    t_after = t_proxy["after"]
    for key in [
        "logical_t_count_proxy",
        "logical_t_depth_proxy",
        "non_clifford_rotation_count",
        "unknown_rotation_count",
        "operation_count_scanned",
    ]:
        lines.append(f"| {key} | {t_before[key]} | {t_after[key]} | {fmt_ratio(ratio(t_before[key], t_after[key]))} |")
    lines.extend(
        [
            "",
            "## Top Circuit Changes",
            "",
            "| circuit | T-count proxy delta | T-depth proxy delta | non-Clifford delta | unknown-rotation delta |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["top_circuits_by_t_reduction"]:
        lines.append(
            f"| {row['relative_path']} | {row['logical_t_count_proxy_reduction']} | "
            f"{row['logical_t_depth_proxy_reduction']} | {row['non_clifford_rotation_count_reduction']} | "
            f"{row['unknown_rotation_count_reduction']} |"
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
    parser.add_argument("--input-dir", type=Path, default=Path("results/b1_post_virtual_swap_1q_resynth"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/b1_native_t_resource_optimizer"))
    parser.add_argument("--hardware-profiles", type=Path, default=Path("benchmarks/hardware_profiles.json"))
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument("--rotation-t-cost", type=int, default=20)
    parser.add_argument("--clean-output", action="store_true")
    parser.add_argument("--before-metrics-output", type=Path, default=Path("results/b1_native_t_resource_optimizer/before_metrics.json"))
    parser.add_argument("--after-metrics-output", type=Path, default=Path("results/b1_native_t_resource_optimizer/after_metrics.json"))
    parser.add_argument("--certificate-log", type=Path, default=Path("results/b1_native_t_resource_optimizer/proofs.jsonl"))
    parser.add_argument("--aer-crosscheck", type=Path, default=Path("results/b1_native_t_resource_optimizer/aer_crosscheck.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B1_native_t_resource_optimizer_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_native_t_resource_optimizer.md"))
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
                    "canonicalization_events": report["rewrite_stats"]["canonicalization_events"],
                    "circuits_changed": report["rewrite_stats"]["circuits_changed"],
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
