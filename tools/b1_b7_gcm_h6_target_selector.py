#!/usr/bin/env python3
"""Select B1 rewrite targets for the B7 gcm_h6 bottleneck.

This tool does not rewrite a circuit. It reads the current B1 optimized gcm_h6
QASM and the B7 template-priority gate, then ranks the smallest visible
rotation families that could satisfy the one-sided gcm_h6 1.20x requirement if
a future B1 rewrite proves an occurrence-removing certificate.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


METHOD = "b1_b7_gcm_h6_target_selector_v0"
STATUS = "gcm_h6_target_selector_not_rewrite_or_resource_claim"
MODEL_STATUS = "posthoc_b1_b7_target_selection_not_semantic_certificate"
VERSION = "0.1"
PROXY_T_COST_PER_ARBITRARY_ROTATION = 20

GATE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(([^)]*)\))?\s+(.+);")
QUBIT_RE = re.compile(r"q\[(\d+)\]")
DECIMAL_RE = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?")
ROTATION_GATES = {"rx", "ry", "rz"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict, pretty: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def canonical_angle(value: float, digits: int = 12) -> str:
    return f"{normalize_angle(value):.{digits}g}"


def parse_qasm(path: Path) -> list[dict]:
    ops = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        code = raw.split("//", 1)[0].strip()
        if not code or code.startswith(("OPENQASM", "include", "qreg", "creg")):
            continue
        match = GATE_RE.match(code)
        if not match:
            continue
        gate = match.group(1).lower()
        params = match.group(2) or ""
        qubits = [int(item) for item in QUBIT_RE.findall(match.group(3))]
        ops.append(
            {
                "op_index": len(ops),
                "line_number": line_number,
                "gate": gate,
                "params": params,
                "qubits": qubits,
                "text": code,
            }
        )
    return ops


def is_arbitrary_decimal_rotation(op: dict) -> bool:
    return op["gate"] in ROTATION_GATES and bool(op["qubits"]) and bool(DECIMAL_RE.search(op["params"]))


def cx_role(op: dict, qubit: int) -> tuple[str, int] | None:
    if op["gate"] != "cx" or len(op["qubits"]) != 2 or qubit not in op["qubits"]:
        return None
    control, target = op["qubits"]
    if qubit == control:
        return ("control", target)
    return ("target", control)


def nearest_cx_context(ops: list[dict], op_index: int, qubit: int) -> tuple[dict | None, dict | None]:
    previous = None
    following = None
    for idx in range(op_index - 1, -1, -1):
        role = cx_role(ops[idx], qubit)
        if role:
            previous = {"line_number": ops[idx]["line_number"], "role": role[0], "partner": role[1]}
            break
    for idx in range(op_index + 1, len(ops)):
        role = cx_role(ops[idx], qubit)
        if role:
            following = {"line_number": ops[idx]["line_number"], "role": role[0], "partner": role[1]}
            break
    return previous, following


def rotation_rows(ops: list[dict]) -> list[dict]:
    rows = []
    for op in ops:
        if not is_arbitrary_decimal_rotation(op):
            continue
        qubit = op["qubits"][0]
        try:
            angle_value = safe_eval_angle(op["params"])
        except ValueError:
            continue
        previous, following = nearest_cx_context(ops, op["op_index"], qubit)
        cone_signature = (
            op["gate"],
            previous["role"] if previous else "none",
            previous["partner"] if previous else -1,
            following["role"] if following else "none",
            following["partner"] if following else -1,
        )
        rows.append(
            {
                "line_number": op["line_number"],
                "op_index": op["op_index"],
                "gate": op["gate"],
                "angle_text": op["params"],
                "angle_value": normalize_angle(angle_value),
                "canonical_angle": canonical_angle(angle_value),
                "qubit": qubit,
                "previous_cx": previous,
                "next_cx": following,
                "cone_signature": cone_signature,
            }
        )
    return rows


def sorted_counter_rows(counter: Counter, target: int, limit: int) -> list[dict]:
    rows = []
    for key, count in counter.most_common(limit):
        rows.append(
            {
                "key": key,
                "occurrence_count": count,
                "meets_gcm_h6_one_sided_target_if_one_removed_per_occurrence": count >= target,
                "target_shortfall": max(0, target - count),
            }
        )
    return rows


def cone_rows(rows: list[dict], target: int, limit: int) -> list[dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["cone_signature"]].append(row)
    ranked = sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))
    output = []
    for idx, (signature, members) in enumerate(ranked[:limit], 1):
        gate, prev_role, prev_partner, next_role, next_partner = signature
        output.append(
            {
                "cone_id": f"cone_{idx:02d}",
                "gate": gate,
                "previous_cx_role": prev_role,
                "previous_cx_partner": None if prev_partner == -1 else prev_partner,
                "next_cx_role": next_role,
                "next_cx_partner": None if next_partner == -1 else next_partner,
                "occurrence_count": len(members),
                "distinct_qubits": sorted({member["qubit"] for member in members}),
                "distinct_canonical_angles": sorted({member["canonical_angle"] for member in members}),
                "first_lines": [member["line_number"] for member in members[:8]],
                "meets_gcm_h6_one_sided_target_if_one_removed_per_occurrence": len(members) >= target,
                "target_shortfall": max(0, target - len(members)),
                "exact_rewrite_certificate_available": False,
            }
        )
    return output


def cnot_pair_incidence_rows(rows: list[dict], target: int, limit: int) -> list[dict]:
    pair_to_lines: dict[tuple[int, int], set[int]] = defaultdict(set)
    for row in rows:
        for context_name in ("previous_cx", "next_cx"):
            context = row[context_name]
            if not context:
                continue
            pair = tuple(sorted((row["qubit"], context["partner"])))
            pair_to_lines[pair].add(row["line_number"])
    ranked = sorted(pair_to_lines.items(), key=lambda item: (-len(item[1]), item[0]))
    return [
        {
            "pair": list(pair),
            "incident_arbitrary_rotation_count": len(lines),
            "meets_gcm_h6_one_sided_target_if_one_removed_per_occurrence": len(lines) >= target,
            "target_shortfall": max(0, target - len(lines)),
        }
        for pair, lines in ranked[:limit]
    ]


def build_payload(args: argparse.Namespace) -> dict:
    template_gate = read_json(args.b7_template_gate)
    target = int(template_gate["summary"]["target_removed_arbitrary_occurrences_for_gcm_h6_1_20"])
    ops = parse_qasm(args.qasm)
    rotations = rotation_rows(ops)
    by_qubit = Counter(row["qubit"] for row in rotations)
    by_gate = Counter(row["gate"] for row in rotations)
    by_raw_angle = Counter(row["angle_text"] for row in rotations)
    by_canonical_angle = Counter(row["canonical_angle"] for row in rotations)
    cones = cone_rows(rotations, target, args.limit)
    angle_rows = sorted_counter_rows(by_canonical_angle, target, args.limit)
    qubit_rows = sorted_counter_rows(by_qubit, target, args.limit)
    pair_rows = cnot_pair_incidence_rows(rotations, target, args.limit)
    summary = {
        "arbitrary_rotation_count": len(rotations),
        "raw_unique_numeric_parameter_count": len(by_raw_angle),
        "canonical_unique_numeric_parameter_count": len(by_canonical_angle),
        "target_removed_arbitrary_occurrences_for_gcm_h6_1_20": target,
        "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": target * PROXY_T_COST_PER_ARBITRARY_ROTATION,
        "target_fraction_of_arbitrary_rotations": target / len(rotations) if rotations else None,
        "top_qubit": qubit_rows[0]["key"] if qubit_rows else None,
        "top_qubit_occurrences": qubit_rows[0]["occurrence_count"] if qubit_rows else 0,
        "top_canonical_angle": angle_rows[0]["key"] if angle_rows else None,
        "top_canonical_angle_occurrences": angle_rows[0]["occurrence_count"] if angle_rows else 0,
        "top_cone_occurrences": cones[0]["occurrence_count"] if cones else 0,
        "cone_classes_meeting_target_if_one_removed_per_occurrence": sum(
            1 for row in cones if row["meets_gcm_h6_one_sided_target_if_one_removed_per_occurrence"]
        ),
        "canonical_angle_classes_meeting_target_if_one_removed_per_occurrence": sum(
            1 for row in angle_rows if row["meets_gcm_h6_one_sided_target_if_one_removed_per_occurrence"]
        ),
        "qubit_classes_meeting_target_if_one_removed_per_occurrence": sum(
            1 for row in qubit_rows if row["meets_gcm_h6_one_sided_target_if_one_removed_per_occurrence"]
        ),
        "resource_saving_claimed": False,
        "rewrite_claimed": False,
        "semantic_certificate_claimed": False,
    }
    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 gcm_h6 target selector for T-resource rewrites",
        "version": VERSION,
        "last_updated": args.last_updated,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_qasm": str(args.qasm),
        "source_b7_template_gate": str(args.b7_template_gate),
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "proxy_t_cost_per_arbitrary_rotation": PROXY_T_COST_PER_ARBITRARY_ROTATION,
        "summary": summary,
        "gate_counts": dict(sorted(by_gate.items())),
        "top_qubit_targets": qubit_rows,
        "top_canonical_angle_targets": angle_rows,
        "top_cone_targets": cones,
        "top_cnot_pair_incidence_targets": pair_rows,
        "claim_boundary": {
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "semantic_certificate_claimed": False,
            "physical_layout_claimed": False,
            "interpretation": "ranked_target_selection_only_for_future_b1_rewrites",
            "next_gate": (
                "A future B1 PR must turn one ranked target family into a replayable semantic "
                "certificate that removes enough arbitrary rotations from gcm_h6 and then re-run "
                "the B7 FT ledger."
            ),
        },
    }
    errors = validate(payload)
    payload["summary"]["validation_error_count"] = len(errors)
    payload["validation_errors"] = errors
    return payload


def validate(payload: dict) -> list[str]:
    errors = []
    summary = payload["summary"]
    claims = payload["claim_boundary"]
    if payload.get("benchmark_id") != "B1":
        errors.append("benchmark_id must be B1")
    if payload.get("method") != METHOD:
        errors.append("method mismatch")
    if payload.get("status") != STATUS:
        errors.append("status mismatch")
    if summary.get("arbitrary_rotation_count") != 270:
        errors.append("gcm_h6 arbitrary rotation count must remain 270")
    if summary.get("raw_unique_numeric_parameter_count") != 26:
        errors.append("raw unique numeric parameter count must remain 26")
    if summary.get("target_removed_arbitrary_occurrences_for_gcm_h6_1_20") != 30:
        errors.append("target removed arbitrary occurrence count must remain 30")
    if summary.get("target_proxy_t_ledger_reduction_for_gcm_h6_1_20") != 600:
        errors.append("target proxy-T reduction must remain 600")
    if summary.get("top_cone_occurrences", 0) < 30:
        errors.append("at least one cone class should meet the occurrence target")
    if summary.get("canonical_angle_classes_meeting_target_if_one_removed_per_occurrence", 0) < 1:
        errors.append("at least one canonical angle class should meet the occurrence target")
    for key in (
        "rewrite_claimed",
        "resource_saving_claimed",
        "semantic_certificate_claimed",
        "physical_layout_claimed",
    ):
        if claims.get(key) is not False:
            errors.append(f"claim boundary must keep {key}=False")
    return errors


def markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 gcm_h6 Target Selector v0.1",
        "",
        f"Status: **{payload['status']}**",
        "",
        "This artifact converts the B7 `gcm_h6` resource boundary into ranked B1",
        "rewrite targets. It does not rewrite the circuit, does not remove any",
        "rotation, and does not claim a physical or semantic certificate.",
        "",
        "## Summary",
        "",
        f"- Source QASM: `{payload['source_qasm']}`",
        f"- Arbitrary decimal rotations: {summary['arbitrary_rotation_count']}",
        f"- Raw unique numeric parameters: {summary['raw_unique_numeric_parameter_count']}",
        f"- Canonical unique numeric parameters: {summary['canonical_unique_numeric_parameter_count']}",
        "- B7 one-sided `gcm_h6` 1.20x target: "
        f"{summary['target_removed_arbitrary_occurrences_for_gcm_h6_1_20']} removed arbitrary occurrences / "
        f"{summary['target_proxy_t_ledger_reduction_for_gcm_h6_1_20']} proxy-T ledger units",
        f"- Target fraction of current arbitrary rotations: {summary['target_fraction_of_arbitrary_rotations']:.6f}",
        f"- Top qubit target: q[{summary['top_qubit']}] with {summary['top_qubit_occurrences']} arbitrary rotations",
        f"- Top canonical angle target: {summary['top_canonical_angle']} with {summary['top_canonical_angle_occurrences']} occurrences",
        f"- Top local CNOT-cone class occurrences: {summary['top_cone_occurrences']}",
        f"- Cone classes meeting the 30-occurrence target: {summary['cone_classes_meeting_target_if_one_removed_per_occurrence']}",
        "",
        "## Top Cone Targets",
        "",
        "| Cone | Gate | Prev CNOT | Next CNOT | Occurrences | Qubits | Angles | Certificate? |",
        "|---|---|---|---|---:|---|---|---|",
    ]
    for row in payload["top_cone_targets"][:8]:
        prev = f"{row['previous_cx_role']}:{row['previous_cx_partner']}"
        nxt = f"{row['next_cx_role']}:{row['next_cx_partner']}"
        lines.append(
            f"| {row['cone_id']} | {row['gate']} | {prev} | {nxt} | {row['occurrence_count']} | "
            f"{row['distinct_qubits']} | {row['distinct_canonical_angles'][:4]} | "
            f"{row['exact_rewrite_certificate_available']} |"
        )
    lines.extend(
        [
            "",
            "## Top Canonical Angle Targets",
            "",
            "| Canonical angle | Occurrences | Meets 30-occurrence target? | Shortfall |",
            "|---|---:|---|---:|",
        ]
    )
    for row in payload["top_canonical_angle_targets"][:8]:
        lines.append(
            f"| {row['key']} | {row['occurrence_count']} | "
            f"{row['meets_gcm_h6_one_sided_target_if_one_removed_per_occurrence']} | "
            f"{row['target_shortfall']} |"
        )
    lines.extend(
        [
            "",
            "## Top Qubit Targets",
            "",
            "| Qubit | Occurrences | Meets 30-occurrence target? | Shortfall |",
            "|---|---:|---|---:|",
        ]
    )
    for row in payload["top_qubit_targets"][:8]:
        lines.append(
            f"| q[{row['key']}] | {row['occurrence_count']} | "
            f"{row['meets_gcm_h6_one_sided_target_if_one_removed_per_occurrence']} | "
            f"{row['target_shortfall']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- No rewrite is claimed.",
            "- No resource reduction is claimed.",
            "- No replayable semantic certificate is claimed.",
            "- No physical layout result is claimed.",
            "",
            "## Next Gate",
            "",
            "A useful `T-B1-004` PR must choose one ranked family, produce an actual",
            "semantic rewrite certificate, reduce at least the required `gcm_h6`",
            "arbitrary rotation occurrences, and then re-run the B7 FT ledger.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--qasm",
        type=Path,
        default=Path("results/b1_u3_phase_factored_optimizer/qasmbench_medium_exact/gcm_h6.qasm"),
    )
    parser.add_argument(
        "--b7-template-gate",
        type=Path,
        default=Path("results/B7_template_priority_gate_v0.json"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("results/B1_B7_gcm_h6_target_selector_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_B7_gcm_h6_target_selector.md"))
    parser.add_argument("--last-updated", default="2026-06-18")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    payload = build_payload(args)
    write_json(args.json_output, payload, pretty=args.pretty)
    write_text(args.markdown_output, markdown(payload))
    if payload["validation_errors"]:
        for error in payload["validation_errors"]:
            print(f"validation error: {error}", file=sys.stderr)
        return 1
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
