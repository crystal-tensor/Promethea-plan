#!/usr/bin/env python3
"""Conservative structural pass for repeated numeric rotations in gcm_h6.

The pass only merges same-axis numeric rx/ry/rz rotations on the same qubit
when intervening operations are disjoint from that qubit.  It does not commute
through CNOTs, different-axis rotations, measurement, or any gate touching the
same qubit.  A negative result is therefore useful: it says the remaining
numeric rotations are not removable by this local same-axis rule.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from b7_ft_synthesis_ledger import qasm_ft_resources


GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\([^)]*\))?\s+(.+);$")
MEASURE_RE = re.compile(r"^measure\s+(.+?)\s*->\s*(.+);$", re.IGNORECASE)
QUBIT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]")
ROTATION_GATES = {"rx", "ry", "rz", "u1"}
ARBITRARY_FAMILY = "arbitrary_numeric_rotation"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def strip_comment(line: str) -> tuple[str, str]:
    if "//" not in line:
        return line.strip(), ""
    code, comment = line.split("//", 1)
    return code.strip(), "//" + comment


def split_params(param_text: str | None) -> list[str]:
    if not param_text:
        return []
    inner = param_text.strip()[1:-1].strip()
    if not inner:
        return []
    return [part.strip() for part in inner.split(",")]


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
            "params": [],
            "operand_text": measure_match.group(1),
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


def output_rotation_line(axis: str, angle: float, qubit: str) -> str | None:
    if is_zero(angle):
        return None
    gate = "rz" if axis == "u1" else axis
    return f"{gate}({format_angle(angle)}) {qubit};"


def flush_qubits(
    qubits: list[str],
    pending: dict[str, dict],
    output: list[str],
    certificates: list[dict],
    line_number: int,
    reason: str,
) -> None:
    items = [pending.pop(qubit) for qubit in qubits if qubit in pending]
    items.sort(key=lambda item: item["first_line"])
    for item in items:
        output_gate = output_rotation_line(item["axis"], item["angle"], item["qubit"])
        if output_gate:
            output.append(output_gate)
        removed = len(item["input_gates"]) - (1 if output_gate else 0)
        if removed > 0 or item["disjoint_lines_crossed"]:
            certificates.append(
                {
                    "rule": "same_axis_numeric_rotation_merge_disjoint_only",
                    "certificate_type": "local_same_axis_rotation_accumulator",
                    "axis": item["axis"],
                    "operand": item["qubit"],
                    "input_line_numbers": item["line_numbers"],
                    "input_gates": item["input_gates"],
                    "output_before_line": line_number,
                    "flush_reason": reason,
                    "output_gate": output_gate,
                    "combined_angle": normalize_angle(item["angle"]),
                    "removed_rotation_gates": removed,
                    "disjoint_lines_crossed": item["disjoint_lines_crossed"],
                }
            )


def flush_all(
    pending: dict[str, dict],
    output: list[str],
    certificates: list[dict],
    line_number: int,
    reason: str,
) -> None:
    flush_qubits(sorted(pending, key=lambda q: pending[q]["first_line"]), pending, output, certificates, line_number, reason)


def add_pending(
    pending: dict[str, dict],
    axis: str,
    qubit: str,
    angle: float,
    line_number: int,
    code: str,
) -> None:
    item = pending.setdefault(
        qubit,
        {
            "axis": axis,
            "qubit": qubit,
            "angle": 0.0,
            "first_line": line_number,
            "line_numbers": [],
            "input_gates": [],
            "disjoint_lines_crossed": 0,
        },
    )
    item["angle"] = normalize_angle(item["angle"] + angle)
    item["line_numbers"].append(line_number)
    item["input_gates"].append(code)


def rewrite_file(input_path: Path, output_path: Path) -> dict:
    pending: dict[str, dict] = {}
    output: list[str] = []
    certificates: list[dict] = []
    line_count = 0
    absorbed_rotations = 0

    for line_count, raw in enumerate(input_path.read_text(encoding="utf-8").splitlines(), 1):
        parsed = parse_line(raw)
        gate = parsed.get("gate")
        qubits = parsed.get("qubits", [])

        for item in pending.values():
            if item["qubit"] not in qubits:
                item["disjoint_lines_crossed"] += 1

        if parsed["kind"] in {"empty", "other"} and not qubits:
            output.append(raw)
            continue

        if gate in ROTATION_GATES and len(qubits) == 1 and len(parsed.get("params", [])) == 1:
            qubit = qubits[0]
            axis = "rz" if gate == "u1" else gate
            try:
                angle = safe_eval_angle(parsed["params"][0])
            except ValueError:
                flush_qubits([qubit], pending, output, certificates, line_count, "unparsed_rotation")
                output.append(raw)
                continue

            current = pending.get(qubit)
            if current is not None and current["axis"] != axis:
                flush_qubits([qubit], pending, output, certificates, line_count, "different_axis_rotation")
            add_pending(pending, axis, qubit, angle, line_count, parsed["code"])
            absorbed_rotations += 1
            continue

        if qubits:
            flush_qubits(qubits, pending, output, certificates, line_count, f"{gate or parsed['kind']}_touch")
        output.append(raw)

    flush_all(pending, output, certificates, line_count + 1, "end_of_circuit")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(output) + "\n", encoding="utf-8")

    removed = sum(event["removed_rotation_gates"] for event in certificates)
    zero_groups = sum(1 for event in certificates if event["output_gate"] is None)
    return {
        "input": str(input_path),
        "output": str(output_path),
        "absorbed_rotation_gates": absorbed_rotations,
        "certificate_entries": len(certificates),
        "merge_or_move_groups": len(certificates),
        "removed_rotation_gates": removed,
        "zero_output_groups": zero_groups,
        "certificates": certificates,
    }


def ft_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        pi_over_4_t_cost=args.pi_over_4_t_cost,
        pi_over_8_t_cost=args.pi_over_8_t_cost,
        arbitrary_rotation_t_cost=args.arbitrary_rotation_t_cost,
        unknown_rotation_t_cost=args.unknown_rotation_t_cost,
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def reschedule(schedule: dict, t_count: int, t_depth: int) -> dict:
    if t_count <= 0:
        factory_rounds = 0
    else:
        factory_rounds = math.ceil(t_count / int(schedule["factory_count"])) * int(schedule["factory_cycle_rounds"])
    tail_rounds = int(schedule["critical_path_rounds"]) - max(
        int(schedule["data_rounds"]),
        int(schedule["factory_rounds"]),
    )
    critical = max(int(schedule["data_rounds"]), factory_rounds) + tail_rounds
    return {
        **schedule,
        "logical_t_count_ledger": t_count,
        "logical_t_depth_ledger": t_depth,
        "factory_rounds": factory_rounds,
        "critical_path_rounds": critical,
        "space_time_volume": int(schedule["total_physical_qubits"]) * critical,
        "bottleneck": "factory_path" if factory_rounds > int(schedule["data_rounds"]) else "data_path",
    }


def replacement_gcm_comparison(row: dict, after_ft: dict) -> dict:
    before = row["before"]
    after = reschedule(row["after"], after_ft["logical_t_count_ledger"], after_ft["logical_t_depth_ledger"])
    after["rotation_family_counts"] = after_ft["rotation_family_counts"]
    after["t_cost_by_family"] = after_ft["t_cost_by_family"]
    return {
        **row,
        "after": after,
        "space_time_volume_reduction": before["space_time_volume"] / after["space_time_volume"],
        "logical_t_count_reduction": before["logical_t_count_ledger"] / after["logical_t_count_ledger"]
        if after["logical_t_count_ledger"]
        else None,
        "logical_t_depth_reduction": before["logical_t_depth_ledger"] / after["logical_t_depth_ledger"]
        if after["logical_t_depth_ledger"]
        else None,
        "bottleneck_after": after["bottleneck"],
    }


def retest_portfolio(ledger: dict, after_ft: dict) -> dict:
    comparisons = []
    for row in ledger["comparisons"]:
        if row["workload"] == "qasmbench_medium_exact/gcm_h6.qasm":
            comparisons.append(replacement_gcm_comparison(row, after_ft))
        else:
            comparisons.append(row)
    reductions = [row["space_time_volume_reduction"] for row in comparisons if row["space_time_volume_reduction"]]
    min_row = min(comparisons, key=lambda row: row["space_time_volume_reduction"])
    gcm_rows = [row for row in comparisons if row["workload"] == "qasmbench_medium_exact/gcm_h6.qasm"]
    gcm_min = min(gcm_rows, key=lambda row: row["space_time_volume_reduction"])
    return {
        "comparison_count": len(comparisons),
        "min_space_time_volume_reduction": min(reductions),
        "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
        "min_workload": min_row["workload"],
        "min_factory_variant": min_row["factory_variant"],
        "min_bottleneck_after": min_row["bottleneck_after"],
        "gcm_h6_min_space_time_volume_reduction": gcm_min["space_time_volume_reduction"],
        "gcm_h6_min_factory_variant": gcm_min["factory_variant"],
        "factory_bottleneck_after_count": sum(1 for row in comparisons if row["bottleneck_after"] == "factory_path"),
        "data_bottleneck_after_count": sum(1 for row in comparisons if row["bottleneck_after"] == "data_path"),
    }


def family_delta(before: dict, after: dict) -> dict:
    families = sorted(set(before["rotation_family_counts"]) | set(after["rotation_family_counts"]))
    return {
        family: int(before["rotation_family_counts"].get(family, 0))
        - int(after["rotation_family_counts"].get(family, 0))
        for family in families
    }


def gate_delta(before: dict, after: dict) -> dict:
    gates = sorted(set(before["gate_counts"]) | set(after["gate_counts"]))
    return {gate: int(before["gate_counts"].get(gate, 0)) - int(after["gate_counts"].get(gate, 0)) for gate in gates}


def certificates_jsonl(path: Path, certificates: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in certificates), encoding="utf-8")


def run(args: argparse.Namespace) -> dict:
    if args.workdir.exists():
        shutil.rmtree(args.workdir)
    output_qasm = args.workdir / "qasmbench_medium_exact" / "gcm_h6.qasm"
    row = rewrite_file(args.input_qasm, output_qasm)
    certificates_jsonl(args.proof_log, row["certificates"])

    model_args = ft_args(args)
    before_ft = qasm_ft_resources(args.input_qasm, model_args)
    after_ft = qasm_ft_resources(output_qasm, model_args)
    ledger = read_json(args.ledger)
    retest = retest_portfolio(ledger, after_ft)
    arbitrary_before = int(before_ft["rotation_family_counts"].get(ARBITRARY_FAMILY, 0))
    arbitrary_after = int(after_ft["rotation_family_counts"].get(ARBITRARY_FAMILY, 0))
    exact_before_t = before_ft["logical_t_count_ledger"] - int(before_ft["t_cost_by_family"].get(ARBITRARY_FAMILY, 0))
    exact_after_t = after_ft["logical_t_count_ledger"] - int(after_ft["t_cost_by_family"].get(ARBITRARY_FAMILY, 0))
    status = (
        "gcm_h6_numeric_rotation_structure_positive_proxy_not_physical_layout"
        if arbitrary_after < arbitrary_before
        else "gcm_h6_numeric_rotation_structure_negative_boundary_not_physical_layout"
    )
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 gcm_h6 numeric-rotation structural pass",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": status,
        "method": "b7_gcm_h6_numeric_rotation_structure_v0",
        "source_ledger": str(args.ledger),
        "input_qasm": str(args.input_qasm),
        "output_qasm": str(output_qasm),
        "proof_log": str(args.proof_log),
        "aer_crosscheck": str(args.aer_crosscheck),
        "rewrite_rule": "same_axis_numeric_rotation_merge_disjoint_only",
        "rewrite_summary": {key: value for key, value in row.items() if key != "certificates"},
        "before_ft_resource": before_ft,
        "after_ft_resource": after_ft,
        "rotation_family_delta_removed": family_delta(before_ft, after_ft),
        "gate_delta_removed": gate_delta(before_ft, after_ft),
        "arbitrary_numeric_rotations_before": arbitrary_before,
        "arbitrary_numeric_rotations_after": arbitrary_after,
        "arbitrary_numeric_rotations_removed": arbitrary_before - arbitrary_after,
        "logical_t_ledger_before": before_ft["logical_t_count_ledger"],
        "logical_t_ledger_after": after_ft["logical_t_count_ledger"],
        "logical_t_ledger_removed": before_ft["logical_t_count_ledger"] - after_ft["logical_t_count_ledger"],
        "fixed_exact_t_ledger_before": exact_before_t,
        "fixed_exact_t_ledger_after": exact_after_t,
        "portfolio_retest": retest,
        "clears_1_20_all_variant_min": retest["min_space_time_volume_reduction"] >= 1.20,
        "clears_1_20_gcm_h6_min": retest["gcm_h6_min_space_time_volume_reduction"] >= 1.20,
        "interpretation": (
            "The conservative same-axis local pass does not reduce gcm_h6 arbitrary numeric rotations."
            if arbitrary_after >= arbitrary_before
            else "The conservative same-axis local pass reduces gcm_h6 arbitrary numeric rotations under the current proxy."
        ),
        "next_actions": [
            "If this is negative, test a nonlocal phase-polynomial or template-aware pass rather than more local same-axis merging.",
            "Separately test whether repeated-angle shared synthesis is only a classical compilation cache or can change a fault-tolerant resource ledger.",
            "Keep B7 claims marked as proxy until layout, feed-forward, factory, and certified synthesis assumptions are explicit.",
        ],
        "limits": [
            "This pass only commutes rotations across operations on disjoint qubits.",
            "It does not commute through CNOTs or different-axis rotations.",
            "It is not a certified Clifford+T synthesis or physical layout result.",
            "The retest changes only the gcm_h6 after-side QASM resource row inside the existing FT ledger.",
        ],
    }


def fmt(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    return f"{value:.6g}"


def markdown(report: dict) -> str:
    retest = report["portfolio_retest"]
    lines = [
        "# B7 gcm_h6 Numeric-Rotation Structure v0.1",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source ledger: `{report['source_ledger']}`",
        f"- Input QASM: `{report['input_qasm']}`",
        f"- Output QASM: `{report['output_qasm']}`",
        f"- Proof log: `{report['proof_log']}`",
        f"- Aer cross-check: `{report['aer_crosscheck']}`",
        f"- Rewrite rule: `{report['rewrite_rule']}`",
        f"- Arbitrary numeric rotations before/after/removed: {report['arbitrary_numeric_rotations_before']} / {report['arbitrary_numeric_rotations_after']} / {report['arbitrary_numeric_rotations_removed']}",
        f"- Logical T ledger before/after/removed: {report['logical_t_ledger_before']} / {report['logical_t_ledger_after']} / {report['logical_t_ledger_removed']}",
        f"- Clears 1.20x all-variant min: {report['clears_1_20_all_variant_min']}",
        f"- Clears 1.20x gcm_h6 min: {report['clears_1_20_gcm_h6_min']}",
        f"- Interpretation: {report['interpretation']}",
        "",
        "## Rewrite Summary",
        "",
    ]
    for key, value in report["rewrite_summary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Rotation Family Delta Removed",
            "",
            "| family | removed | before | after |",
            "|---|---:|---:|---:|",
        ]
    )
    for family, removed in report["rotation_family_delta_removed"].items():
        before = report["before_ft_resource"]["rotation_family_counts"].get(family, 0)
        after = report["after_ft_resource"]["rotation_family_counts"].get(family, 0)
        lines.append(f"| {family} | {removed} | {before} | {after} |")
    lines.extend(
        [
            "",
            "## Portfolio Retest",
            "",
            f"- Min STV reduction: {retest['min_space_time_volume_reduction']:.6f}x",
            f"- Mean STV reduction: {retest['mean_space_time_volume_reduction']:.6f}x",
            f"- Min row: `{retest['min_workload']}` / `{retest['min_factory_variant']}`",
            f"- gcm_h6 min STV reduction: {retest['gcm_h6_min_space_time_volume_reduction']:.6f}x",
            f"- gcm_h6 min variant: `{retest['gcm_h6_min_factory_variant']}`",
            f"- After factory/data bottleneck rows: {retest['factory_bottleneck_after_count']} / {retest['data_bottleneck_after_count']}",
            "",
            "## Next Actions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-qasm",
        type=Path,
        default=Path("results/b1_u3_phase_factored_optimizer/qasmbench_medium_exact/gcm_h6.qasm"),
    )
    parser.add_argument("--ledger", type=Path, default=Path("results/B7_ft_synthesis_ledger_v0.json"))
    parser.add_argument("--workdir", type=Path, default=Path("results/b7_gcm_h6_numeric_rotation_structure"))
    parser.add_argument(
        "--proof-log",
        type=Path,
        default=Path("results/b7_gcm_h6_numeric_rotation_structure/proofs.jsonl"),
    )
    parser.add_argument(
        "--aer-crosscheck",
        type=Path,
        default=Path("results/b7_gcm_h6_numeric_rotation_structure/aer_crosscheck.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B7_gcm_h6_numeric_rotation_structure_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B7_gcm_h6_numeric_rotation_structure.md"),
    )
    parser.add_argument("--pi-over-4-t-cost", type=int, default=1)
    parser.add_argument("--pi-over-8-t-cost", type=int, default=4)
    parser.add_argument("--arbitrary-rotation-t-cost", type=int, default=20)
    parser.add_argument("--unknown-rotation-t-cost", type=int, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run(args)
    write_json(args.json_output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")
    print(
        f"status={report['status']} arbitrary_removed={report['arbitrary_numeric_rotations_removed']} "
        f"t_removed={report['logical_t_ledger_removed']} min_stv={report['portfolio_retest']['min_space_time_volume_reduction']:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
