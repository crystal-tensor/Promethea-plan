#!/usr/bin/env python3
"""Target B1/B7 factory-boundary workloads with control-RZ commuting.

The rewrite is deliberately narrow:

- pending rz(theta) gates are accumulated per qubit;
- pending rz on a CNOT control is allowed to commute through the CNOT;
- pending rz on a CNOT target is flushed before the CNOT;
- any other gate touching a pending qubit flushes that qubit first.

This preserves semantics while combining repeated Z rotations that current B7
T-resource proxies count as separate synthesis costs.
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
MEASURE_RE = re.compile(r"^measure\s+(.+?)\s*->\s*(.+);$", re.IGNORECASE)
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


def split_params(param_text: str | None) -> list[str]:
    if not param_text:
        return []
    inner = param_text.strip()[1:-1].strip()
    if not inner:
        return []
    return [part.strip() for part in inner.split(",")]


def parse_line(line: str) -> dict:
    code, comment = strip_comment(line)
    if not code:
        return {"kind": "empty", "raw": line, "code": code, "comment": comment, "gate": None, "qubits": []}
    measure_match = MEASURE_RE.match(code)
    if measure_match:
        return {
            "kind": "measure",
            "raw": line,
            "code": code,
            "comment": comment,
            "gate": "measure",
            "qubits": [f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(measure_match.group(1))],
        }
    match = GATE_RE.match(code)
    if not match:
        return {"kind": "other", "raw": line, "code": code, "comment": comment, "gate": None, "qubits": []}
    return {
        "kind": "gate",
        "raw": line,
        "code": code,
        "comment": comment,
        "gate": match.group(1).lower(),
        "params": split_params(match.group(2)),
        "operand_text": match.group(3),
        "qubits": [f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(match.group(3))],
    }


def pending_gate_line(qubit: str, angle: float) -> str | None:
    angle = normalize_angle(angle)
    if is_zero(angle):
        return None
    return f"rz({format_angle(angle)}) {qubit};"


def flush_qubit(
    qubit: str,
    pending: dict[str, dict],
    output: list[str],
    certificates: list[dict],
    line_number: int,
    reason: str,
) -> None:
    item = pending.pop(qubit, None)
    if item is None:
        return
    output_gate = pending_gate_line(qubit, item["angle"])
    if output_gate:
        output.append(output_gate)
    certificates.append(
        {
            "rule": "commute_control_rz_and_merge",
            "certificate_type": "rz_control_commutation_accumulator",
            "operand": qubit,
            "input_line_numbers": item["line_numbers"],
            "input_gates": item["input_gates"],
            "output_before_line": line_number,
            "flush_reason": reason,
            "output_gate": output_gate,
            "combined_angle": normalize_angle(item["angle"]),
            "removed_rz_gates": len(item["input_gates"]) - (1 if output_gate else 0),
            "commuted_across_cx_as_control": item["commuted_cx_count"],
        }
    )


def flush_all(
    pending: dict[str, dict],
    output: list[str],
    certificates: list[dict],
    line_number: int,
    reason: str,
) -> None:
    for qubit in sorted(list(pending)):
        flush_qubit(qubit, pending, output, certificates, line_number, reason)


def add_pending_rz(pending: dict[str, dict], qubit: str, angle: float, line_number: int, code: str) -> None:
    item = pending.setdefault(
        qubit,
        {
            "angle": 0.0,
            "line_numbers": [],
            "input_gates": [],
            "commuted_cx_count": 0,
        },
    )
    item["angle"] = normalize_angle(item["angle"] + angle)
    item["line_numbers"].append(line_number)
    item["input_gates"].append(code)


def rewrite_file(input_path: Path, output_path: Path) -> dict:
    output: list[str] = []
    certificates: list[dict] = []
    pending: dict[str, dict] = {}
    absorbed_rz = 0
    line_count = 0

    for line_count, raw in enumerate(input_path.read_text(encoding="utf-8").splitlines(), 1):
        parsed = parse_line(raw)
        gate = parsed.get("gate")
        qubits = parsed.get("qubits", [])

        if parsed["kind"] in {"empty", "other"} and not qubits:
            output.append(raw)
            continue

        if gate == "rz" and len(qubits) == 1 and len(parsed.get("params", [])) == 1:
            try:
                angle = safe_eval_angle(parsed["params"][0])
            except ValueError:
                flush_qubit(qubits[0], pending, output, certificates, line_count, "unparsed_rz")
                output.append(raw)
                continue
            add_pending_rz(pending, qubits[0], angle, line_count, parsed["code"])
            absorbed_rz += 1
            continue

        if gate == "cx" and len(qubits) == 2:
            control, target = qubits
            flush_qubit(target, pending, output, certificates, line_count, "cx_target_noncommuting")
            if control in pending:
                pending[control]["commuted_cx_count"] += 1
            output.append(raw)
            continue

        for qubit in qubits:
            flush_qubit(qubit, pending, output, certificates, line_count, f"{gate or parsed['kind']}_touch")
        output.append(raw)

    flush_all(pending, output, certificates, line_count + 1, "end_of_circuit")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(output) + "\n", encoding="utf-8")
    return {
        "input": str(input_path),
        "output": str(output_path),
        "absorbed_rz_gates": absorbed_rz,
        "certificate_entries": len(certificates),
        "merged_or_moved_groups": sum(1 for event in certificates if event["removed_rz_gates"] > 0 or event["commuted_across_cx_as_control"] > 0),
        "removed_rz_gates": sum(event["removed_rz_gates"] for event in certificates),
        "commuted_cx_count": sum(event["commuted_across_cx_as_control"] for event in certificates),
        "zero_output_groups": sum(1 for event in certificates if event["output_gate"] is None),
        "certificates": certificates,
    }


def compute_directory_metrics(input_dir: Path, output_path: Path, profile_path: Path, profile: str) -> dict:
    profiles = load_profiles(profile_path)
    rows = [compute_metrics(path, profiles[profile]) for path in find_qasm_files([input_dir])]
    payload = {"benchmark_id": "B1", "profile": profile, "circuit_count": len(rows), "results": rows}
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


def ratio(before: float, after: float) -> float | None:
    if after == 0:
        return None
    return before / after


def pct_reduction(before: float, after: float) -> float | None:
    if before == 0:
        return None
    return 100.0 * (before - after) / before


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
                "non_clifford_rotation_count_reduction": before["non_clifford_rotation_count"] - after["non_clifford_rotation_count"],
            }
        )
    changes.sort(key=lambda row: (row["logical_t_count_proxy_reduction"], row["logical_t_depth_proxy_reduction"]), reverse=True)
    return changes[:12]


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
    if rewrite_stats["removed_rz_gates"] == 0:
        return "control_rz_commute_no_t_count_gain_boundary"
    if (t_summary["logical_t_count_reduction"] or 0) > 1.0:
        return "control_rz_commute_positive_diagnostic_not_final_claim"
    return "control_rz_commute_boundary"


def run(args: argparse.Namespace) -> dict:
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
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
        certificate_events.extend({**event, "relative_path": str(input_path.relative_to(input_dir))} for event in row["certificates"])

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
        "non_clifford_rotation_count_reduction": ratio(before_t["non_clifford_rotation_count"], after_t["non_clifford_rotation_count"]),
    }
    rewrite_stats = {
        "rewritten_circuits": len(rewrite_rows),
        "circuits_changed": sum(1 for row in rewrite_rows if row["removed_rz_gates"] > 0 or row["commuted_cx_count"] > 0),
        "absorbed_rz_gates": sum(row["absorbed_rz_gates"] for row in rewrite_rows),
        "certificate_entries": len(certificate_events),
        "merged_or_moved_groups": sum(row["merged_or_moved_groups"] for row in rewrite_rows),
        "removed_rz_gates": sum(row["removed_rz_gates"] for row in rewrite_rows),
        "commuted_cx_count": sum(row["commuted_cx_count"] for row in rewrite_rows),
        "zero_output_groups": sum(row["zero_output_groups"] for row in rewrite_rows),
    }

    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 targeted control-RZ commute optimizer diagnostic",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": status(t_summary, rewrite_stats),
        "method": "control_rz_commute_and_merge_v0",
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
            "Only RZ gates are accumulated; arbitrary U3 rotations are not resynthesized.",
            "RZ gates commute only across CNOTs where their qubit is the control; target-side RZ gates are flushed.",
            "This is a factory-boundary diagnostic, not a complete phase-polynomial optimizer.",
            "Any B7 claim must be based on the propagated factory schedule, not only local T-count reduction.",
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
        "# B1 Targeted Control-RZ Commute Optimizer v0.1",
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
        f"- Absorbed RZ gates: {rewrite['absorbed_rz_gates']}",
        f"- Certificate events: {rewrite['certificate_entries']}",
        f"- Merged or moved groups: {rewrite['merged_or_moved_groups']}",
        f"- Removed RZ gates: {rewrite['removed_rz_gates']}",
        f"- CNOT-control commutations: {rewrite['commuted_cx_count']}",
        f"- Zero-output groups: {rewrite['zero_output_groups']}",
        f"- Logical T-count proxy reduction: {fmt_ratio(t_proxy['logical_t_count_reduction'])}",
        f"- Logical T-depth proxy reduction: {fmt_ratio(t_proxy['logical_t_depth_reduction'])}",
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
    for key in ["logical_t_count_proxy", "logical_t_depth_proxy", "non_clifford_rotation_count", "operation_count_scanned"]:
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
    parser.add_argument("--input-dir", type=Path, default=Path("results/b1_native_t_resource_optimizer"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/b1_control_rz_commute_optimizer"))
    parser.add_argument("--hardware-profiles", type=Path, default=Path("benchmarks/hardware_profiles.json"))
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument("--rotation-t-cost", type=int, default=20)
    parser.add_argument("--clean-output", action="store_true")
    parser.add_argument("--before-metrics-output", type=Path, default=Path("results/b1_control_rz_commute_optimizer/before_metrics.json"))
    parser.add_argument("--after-metrics-output", type=Path, default=Path("results/b1_control_rz_commute_optimizer/after_metrics.json"))
    parser.add_argument("--certificate-log", type=Path, default=Path("results/b1_control_rz_commute_optimizer/proofs.jsonl"))
    parser.add_argument("--aer-crosscheck", type=Path, default=Path("results/b1_control_rz_commute_optimizer/aer_crosscheck.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B1_control_rz_commute_optimizer_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_control_rz_commute_optimizer.md"))
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
                    "removed_rz_gates": report["rewrite_stats"]["removed_rz_gates"],
                    "commuted_cx_count": report["rewrite_stats"]["commuted_cx_count"],
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
