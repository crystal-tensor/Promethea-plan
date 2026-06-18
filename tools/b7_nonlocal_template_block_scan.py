#!/usr/bin/env python3
"""Nonlocal repeated-block scan for the gcm_h6 FT-ledger boundary.

This T-B7-007 probe looks beyond local same-axis rotation merging.  It mines
role-normalized repeated QASM blocks, checks for adjacent inverse/duplicate
blocks that would support a semantics-preserving cancellation, and quantifies
how many physical arbitrary-rotation occurrences would need to disappear for
the B7 ledger to clear 1.20x.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from b7_ft_synthesis_ledger import classify_rotation, gate_rotation_params, qasm_ft_resources


PARAM_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\((.*?)\)\s+(.*);$")
GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s+(.*);$")
QUBIT_RE = re.compile(r"q\[(\d+)\]")
ARBITRARY_FAMILY = "arbitrary_numeric_rotation"
WORKLOAD = "qasmbench_medium_exact/gcm_h6.qasm"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_eval_angle(expr: str) -> float | None:
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
    try:
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, allowed_nodes):
                return None
            if isinstance(node, ast.Name) and node.id != "pi":
                return None
        return float(eval(compile(tree, "<angle>", "eval"), {"__builtins__": {}}, {"pi": math.pi}))
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError):
        return None


def normalize_angle(value: float) -> float:
    while value <= -math.pi:
        value += 2 * math.pi
    while value > math.pi:
        value -= 2 * math.pi
    return value


def parse_qasm_ops(path: Path) -> list[dict]:
    ops = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        code = raw.split("//", 1)[0].strip()
        lower = code.lower()
        if (
            not code
            or lower.startswith("openqasm")
            or lower.startswith("include")
            or lower.startswith("qreg")
            or lower.startswith("creg")
            or lower.startswith("barrier")
            or lower.startswith("measure")
        ):
            continue
        param_match = PARAM_RE.match(code)
        gate_match = GATE_RE.match(code)
        if param_match:
            gate = param_match.group(1).lower()
            params = [part.strip() for part in param_match.group(2).split(",") if part.strip()]
            operand_text = param_match.group(3)
        elif gate_match:
            gate = gate_match.group(1).lower()
            params = []
            operand_text = gate_match.group(2)
        else:
            continue
        qubits = [int(q) for q in QUBIT_RE.findall(operand_text)]
        rotation_families = [classify_rotation(expr) for _axis, expr in gate_rotation_params(gate, params)]
        ops.append(
            {
                "index": len(ops),
                "line_number": line_number,
                "raw": code,
                "gate": gate,
                "params": params,
                "qubits": qubits,
                "rotation_families": rotation_families,
                "arbitrary_rotation_components": sum(1 for family in rotation_families if family == ARBITRARY_FAMILY),
            }
        )
    return ops


def param_token(expr: str) -> tuple:
    value = safe_eval_angle(expr)
    if value is None:
        return ("expr", expr.replace(" ", ""))
    return ("angle", round(normalize_angle(value), 12))


def op_token(op: dict, role_map: dict[int, str] | None = None) -> tuple:
    if role_map is None:
        qubit_tokens = tuple(op["qubits"])
    else:
        qubit_tokens = tuple(role_map[q] for q in op["qubits"])
    return (op["gate"], tuple(param_token(param) for param in op["params"]), qubit_tokens)


def role_signature(window: list[dict]) -> tuple:
    role_map: dict[int, str] = {}
    for op in window:
        for qubit in op["qubits"]:
            if qubit not in role_map:
                role_map[qubit] = f"r{len(role_map)}"
    return tuple(op_token(op, role_map) for op in window)


def actual_signature(window: list[dict]) -> tuple:
    return tuple(op_token(op) for op in window)


def op_inverse_token(op: dict) -> tuple | None:
    gate = op["gate"]
    if gate == "cx" and len(op["qubits"]) == 2:
        return op_token(op)
    if gate in {"rx", "ry", "rz", "u1"} and len(op["params"]) == 1 and len(op["qubits"]) == 1:
        value = safe_eval_angle(op["params"][0])
        if value is None:
            return None
        inverse = ("angle", round(normalize_angle(-value), 12))
        normalized_gate = "rz" if gate == "u1" else gate
        return (normalized_gate, (inverse,), tuple(op["qubits"]))
    return None


def inverse_actual_signature(window: list[dict]) -> tuple | None:
    inverse = []
    for op in reversed(window):
        token = op_inverse_token(op)
        if token is None:
            return None
        inverse.append(token)
    return tuple(inverse)


def greedy_nonoverlap(starts: list[int], width: int) -> list[int]:
    selected = []
    next_allowed = -1
    for start in sorted(starts):
        if start >= next_allowed:
            selected.append(start)
            next_allowed = start + width
    return selected


def binding_for_window(window: list[dict]) -> dict[str, int]:
    role_map: dict[int, str] = {}
    for op in window:
        for qubit in op["qubits"]:
            if qubit not in role_map:
                role_map[qubit] = f"r{len(role_map)}"
    return {role: qubit for qubit, role in role_map.items()}


def scan_repeated_templates(ops: list[dict], widths: list[int], top_k: int) -> tuple[list[dict], list[dict]]:
    candidates = []
    proof_rows = []
    for width in widths:
        starts_by_signature: dict[tuple, list[int]] = defaultdict(list)
        for start in range(0, len(ops) - width + 1):
            starts_by_signature[role_signature(ops[start : start + width])].append(start)
        for signature, starts in starts_by_signature.items():
            if len(starts) < 2:
                continue
            selected = greedy_nonoverlap(starts, width)
            if len(selected) < 2:
                continue
            first_window = ops[selected[0] : selected[0] + width]
            arbitrary_per_occurrence = sum(op["arbitrary_rotation_components"] for op in first_window)
            if arbitrary_per_occurrence <= 0:
                continue
            bindings = [binding_for_window(ops[start : start + width]) for start in selected]
            line_spans = [
                [ops[start]["line_number"], ops[start + width - 1]["line_number"]]
                for start in selected
            ]
            candidate = {
                "template_id": f"w{width}_{len(candidates) + 1}",
                "width": width,
                "raw_occurrences": len(starts),
                "nonoverlap_occurrences": len(selected),
                "arbitrary_rotations_per_occurrence": arbitrary_per_occurrence,
                "physical_arbitrary_occurrences_covered": arbitrary_per_occurrence * len(selected),
                "operation_occurrences_covered": width * len(selected),
                "unique_binding_count": len({tuple(sorted(binding.items())) for binding in bindings}),
                "selected_start_indices": selected[:16],
                "selected_line_spans": line_spans[:16],
                "first_binding": bindings[0],
                "first_ops": [op["raw"] for op in first_window[: min(width, 12)]],
            }
            candidates.append(candidate)
            proof_rows.append(
                {
                    "rule": "role_normalized_repeated_block_scan",
                    "certificate_type": "nonlocal_template_candidate",
                    **candidate,
                    "selected_start_indices": selected,
                    "selected_line_spans": line_spans,
                }
            )
    candidates.sort(
        key=lambda row: (
            row["physical_arbitrary_occurrences_covered"],
            row["operation_occurrences_covered"],
            row["nonoverlap_occurrences"],
        ),
        reverse=True,
    )
    return candidates[:top_k], proof_rows


def scan_cancellation_opportunities(ops: list[dict], widths: list[int]) -> dict:
    adjacent_inverse_pairs = []
    adjacent_duplicate_pairs = []
    for width in widths:
        for start in range(0, len(ops) - (2 * width) + 1):
            left = ops[start : start + width]
            right = ops[start + width : start + 2 * width]
            left_signature = actual_signature(left)
            right_signature = actual_signature(right)
            inverse = inverse_actual_signature(left)
            if inverse is not None and inverse == right_signature:
                adjacent_inverse_pairs.append(
                    {
                        "width": width,
                        "left_line_span": [left[0]["line_number"], left[-1]["line_number"]],
                        "right_line_span": [right[0]["line_number"], right[-1]["line_number"]],
                        "arbitrary_rotations_removed_if_cancelled": sum(
                            op["arbitrary_rotation_components"] for op in left + right
                        ),
                    }
                )
            if left_signature == right_signature:
                adjacent_duplicate_pairs.append(
                    {
                        "width": width,
                        "left_line_span": [left[0]["line_number"], left[-1]["line_number"]],
                        "right_line_span": [right[0]["line_number"], right[-1]["line_number"]],
                        "arbitrary_rotations_in_pair": sum(op["arbitrary_rotation_components"] for op in left + right),
                    }
                )
    return {
        "adjacent_inverse_pair_count": len(adjacent_inverse_pairs),
        "adjacent_duplicate_pair_count": len(adjacent_duplicate_pairs),
        "adjacent_inverse_pairs": adjacent_inverse_pairs[:16],
        "adjacent_duplicate_pairs": adjacent_duplicate_pairs[:16],
    }


def reschedule(schedule: dict, t_count: int, t_depth: int | None = None) -> dict:
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
        "logical_t_depth_ledger": int(schedule["logical_t_depth_ledger"] if t_depth is None else t_depth),
        "factory_rounds": factory_rounds,
        "critical_path_rounds": critical,
        "space_time_volume": int(schedule["total_physical_qubits"]) * critical,
        "bottleneck": "factory_path" if factory_rounds > int(schedule["data_rounds"]) else "data_path",
    }


def compare_with_after_t(row: dict, after_t: int) -> dict:
    after = reschedule(row["after"], after_t)
    before = row["before"]
    return {
        "workload": row["workload"],
        "factory_variant": row["factory_variant"],
        "space_time_volume_reduction": before["space_time_volume"] / after["space_time_volume"],
        "bottleneck_after": after["bottleneck"],
        "after_t_ledger": after_t,
    }


def portfolio_retest(ledger: dict, after_t: int) -> dict:
    comparisons = []
    for row in ledger["comparisons"]:
        if row["workload"] == WORKLOAD:
            comparisons.append(compare_with_after_t(row, after_t))
        else:
            comparisons.append(
                {
                    "workload": row["workload"],
                    "factory_variant": row["factory_variant"],
                    "space_time_volume_reduction": row["space_time_volume_reduction"],
                    "bottleneck_after": row["bottleneck_after"],
                }
            )
    reductions = [row["space_time_volume_reduction"] for row in comparisons]
    min_row = min(comparisons, key=lambda row: row["space_time_volume_reduction"])
    gcm_rows = [row for row in comparisons if row["workload"] == WORKLOAD]
    gcm_min = min(gcm_rows, key=lambda row: row["space_time_volume_reduction"])
    return {
        "comparison_count": len(comparisons),
        "min_space_time_volume_reduction": min(reductions),
        "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
        "min_workload": min_row["workload"],
        "min_factory_variant": min_row["factory_variant"],
        "gcm_h6_min_space_time_volume_reduction": gcm_min["space_time_volume_reduction"],
        "gcm_h6_min_factory_variant": gcm_min["factory_variant"],
        "clears_1_20_all_variant_min": min(reductions) >= 1.20,
        "clears_1_20_gcm_h6_min": gcm_min["space_time_volume_reduction"] >= 1.20,
    }


def target_sweep(ledger: dict, current_after_t: int, arbitrary_t_cost: int, max_remove: int) -> dict:
    rows = []
    first_all = None
    first_gcm = None
    for removed in range(max_remove + 1):
        after_t = max(0, current_after_t - removed * arbitrary_t_cost)
        retest = portfolio_retest(ledger, after_t)
        row = {
            "removed_arbitrary_occurrences": removed,
            "removed_t_ledger": removed * arbitrary_t_cost,
            "after_t_ledger": after_t,
            "min_space_time_volume_reduction": retest["min_space_time_volume_reduction"],
            "gcm_h6_min_space_time_volume_reduction": retest["gcm_h6_min_space_time_volume_reduction"],
            "clears_1_20_all_variant_min": retest["clears_1_20_all_variant_min"],
            "clears_1_20_gcm_h6_min": retest["clears_1_20_gcm_h6_min"],
        }
        if first_all is None and row["clears_1_20_all_variant_min"]:
            first_all = row
        if first_gcm is None and row["clears_1_20_gcm_h6_min"]:
            first_gcm = row
        if removed in {0, 1, 5, 10, 20, 30, 40, 50} or row["clears_1_20_all_variant_min"]:
            rows.append(row)
        if first_all is not None and first_gcm is not None and removed > first_all["removed_arbitrary_occurrences"] + 2:
            break
    return {
        "first_all_variant_1_20": first_all,
        "first_gcm_h6_1_20": first_gcm,
        "sampled_rows": rows[:32],
    }


def certificates_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def ft_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        pi_over_4_t_cost=args.pi_over_4_t_cost,
        pi_over_8_t_cost=args.pi_over_8_t_cost,
        arbitrary_rotation_t_cost=args.arbitrary_rotation_t_cost,
        unknown_rotation_t_cost=args.unknown_rotation_t_cost,
    )


def run(args: argparse.Namespace) -> dict:
    ops = parse_qasm_ops(args.input_qasm)
    widths = [int(item) for item in args.window_widths.split(",") if item.strip()]
    top_templates, proof_rows = scan_repeated_templates(ops, widths, args.top_templates)
    cancellation = scan_cancellation_opportunities(ops, widths)
    before_ft = qasm_ft_resources(args.input_qasm, ft_args(args))
    after_ft = before_ft
    ledger = read_json(args.ledger)
    current_after_t = int(after_ft["logical_t_count_ledger"])
    arbitrary_occurrences = int(after_ft["rotation_family_counts"].get(ARBITRARY_FAMILY, 0))
    sweep = target_sweep(ledger, current_after_t, args.arbitrary_rotation_t_cost, arbitrary_occurrences)
    retest = portfolio_retest(ledger, current_after_t)
    if args.output_qasm:
        args.output_qasm.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.input_qasm, args.output_qasm)
    certificates_jsonl(args.proof_log, proof_rows)

    best_template = top_templates[0] if top_templates else None
    status = (
        "nonlocal_template_block_rewrite_positive_proxy_not_physical_layout"
        if cancellation["adjacent_inverse_pair_count"] > 0
        else "nonlocal_template_block_scan_negative_boundary_not_physical_layout"
    )
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 nonlocal template block scan for gcm_h6",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": status,
        "method": "b7_nonlocal_template_block_scan_v0",
        "source_ledger": str(args.ledger),
        "input_qasm": str(args.input_qasm),
        "output_qasm": str(args.output_qasm) if args.output_qasm else None,
        "proof_log": str(args.proof_log),
        "window_widths": widths,
        "operation_count": len(ops),
        "top_template_count": len(top_templates),
        "candidate_certificate_count": len(proof_rows),
        "best_template": best_template,
        "top_templates": top_templates,
        "cancellation_opportunities": cancellation,
        "before_ft_resource": before_ft,
        "after_ft_resource": after_ft,
        "arbitrary_numeric_rotations_before": arbitrary_occurrences,
        "arbitrary_numeric_rotations_after": arbitrary_occurrences,
        "arbitrary_numeric_rotations_removed": 0,
        "logical_t_ledger_before": current_after_t,
        "logical_t_ledger_after": current_after_t,
        "logical_t_ledger_removed": 0,
        "portfolio_retest": retest,
        "target_sweep": sweep,
        "clears_1_20_all_variant_min": retest["clears_1_20_all_variant_min"],
        "clears_1_20_gcm_h6_min": retest["clears_1_20_gcm_h6_min"],
        "interpretation": (
            "Role-normalized nonlocal templates are abundant, but this scan finds no adjacent inverse "
            "or duplicate same-binding block that supports a certified occurrence-removing rewrite. "
            "A future positive result must replace a repeated block with a lower-arbitrary-rotation "
            "unitary and prove equivalence; macro naming or template reuse alone is not a physical ledger reduction."
        ),
        "next_actions": [
            "Target the highest-coverage templates with an actual unitary-synthesis subroutine, not a macro cache.",
            "Try exact small-block synthesis for the best template bindings and require fewer arbitrary rotations per executed block.",
            "If synthesis cannot beat the current block, promote this scan into a sharper block-family no-go memo.",
        ],
        "limits": [
            "The scan proves absence only for the configured window widths and adjacent inverse/duplicate criteria.",
            "Role-normalized repetition is a candidate generator, not by itself a semantics-preserving rewrite.",
            "No output QASM rewrite is emitted when cancellation_opportunities.adjacent_inverse_pair_count is zero.",
            "This remains an FT-ledger proxy, not a lattice-surgery layout or calibrated device claim.",
        ],
    }


def markdown(report: dict) -> str:
    retest = report["portfolio_retest"]
    sweep = report["target_sweep"]
    best = report["best_template"] or {}
    lines = [
        "# B7 Nonlocal Template Block Scan v0.1",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Input QASM: `{report['input_qasm']}`",
        f"- Proof log: `{report['proof_log']}`",
        f"- Window widths: {report['window_widths']}",
        f"- Operation count scanned: {report['operation_count']}",
        f"- Candidate certificates: {report['candidate_certificate_count']}",
        f"- Top repeated templates retained: {report['top_template_count']}",
        f"- Adjacent inverse block pairs: {report['cancellation_opportunities']['adjacent_inverse_pair_count']}",
        f"- Adjacent duplicate same-binding block pairs: {report['cancellation_opportunities']['adjacent_duplicate_pair_count']}",
        f"- Arbitrary numeric rotations before/after/removed: {report['arbitrary_numeric_rotations_before']} / {report['arbitrary_numeric_rotations_after']} / {report['arbitrary_numeric_rotations_removed']}",
        f"- Logical T ledger before/after/removed: {report['logical_t_ledger_before']} / {report['logical_t_ledger_after']} / {report['logical_t_ledger_removed']}",
        f"- Portfolio min STV after scan: {retest['min_space_time_volume_reduction']:.6f}x",
        f"- Clears 1.20x all-variant min: {report['clears_1_20_all_variant_min']}",
        f"- Interpretation: {report['interpretation']}",
        "",
        "## Best Repeated Template",
        "",
    ]
    if best:
        lines.extend(
            [
                f"- Template ID: `{best['template_id']}`",
                f"- Width: {best['width']}",
                f"- Non-overlap occurrences: {best['nonoverlap_occurrences']}",
                f"- Arbitrary rotations per occurrence: {best['arbitrary_rotations_per_occurrence']}",
                f"- Physical arbitrary occurrences covered: {best['physical_arbitrary_occurrences_covered']}",
                f"- Unique binding count: {best['unique_binding_count']}",
                f"- First binding: `{best['first_binding']}`",
                "",
                "First operations:",
                "",
            ]
        )
        lines.extend(f"- `{op}`" for op in best["first_ops"])
    else:
        lines.append("- No repeated arbitrary-rotation template found under the configured windows.")
    lines.extend(
        [
            "",
            "## Target Sweep",
            "",
            f"- First all-variant 1.20x row: `{sweep['first_all_variant_1_20']}`",
            f"- First gcm_h6 1.20x row: `{sweep['first_gcm_h6_1_20']}`",
            "",
            "| removed arbitrary occurrences | removed T ledger | after T ledger | portfolio min STV | gcm_h6 min STV | clears all 1.20x |",
            "|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in sweep["sampled_rows"]:
        lines.append(
            f"| {row['removed_arbitrary_occurrences']} | {row['removed_t_ledger']} | {row['after_t_ledger']} | "
            f"{row['min_space_time_volume_reduction']:.6f} | {row['gcm_h6_min_space_time_volume_reduction']:.6f} | "
            f"{row['clears_1_20_all_variant_min']} |"
        )
    lines.extend(["", "## Top Templates", ""])
    lines.extend(
        [
            "| template | width | non-overlap occ | arbitrary/occ | physical arbitrary covered | unique bindings | first line spans |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report["top_templates"]:
        lines.append(
            f"| `{row['template_id']}` | {row['width']} | {row['nonoverlap_occurrences']} | "
            f"{row['arbitrary_rotations_per_occurrence']} | {row['physical_arbitrary_occurrences_covered']} | "
            f"{row['unique_binding_count']} | `{row['selected_line_spans'][:3]}` |"
        )
    lines.extend(["", "## Next Actions", ""])
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
    parser.add_argument(
        "--output-qasm",
        type=Path,
        default=Path("results/b7_nonlocal_template_block_scan/qasmbench_medium_exact/gcm_h6.qasm"),
    )
    parser.add_argument(
        "--proof-log",
        type=Path,
        default=Path("results/b7_nonlocal_template_block_scan/proofs.jsonl"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B7_nonlocal_template_block_scan_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B7_nonlocal_template_block_scan.md"),
    )
    parser.add_argument("--window-widths", default="8,10,12,16,20,24,32,40,48,64")
    parser.add_argument("--top-templates", type=int, default=12)
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
        f"status={report['status']} top_templates={report['top_template_count']} "
        f"adjacent_inverse={report['cancellation_opportunities']['adjacent_inverse_pair_count']} "
        f"removed={report['arbitrary_numeric_rotations_removed']} "
        f"min_stv={report['portfolio_retest']['min_space_time_volume_reduction']:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
