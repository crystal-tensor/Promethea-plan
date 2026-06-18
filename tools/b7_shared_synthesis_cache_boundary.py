#!/usr/bin/env python3
"""Boundary analysis for shared synthesis/cache claims on gcm_h6.

Repeated numeric angles can reduce a classical synthesis catalog, but unless a
single synthesized ancilla/resource can be reused physically, each circuit
occurrence still consumes the rotation's fault-tolerant execution resources.
This tool makes that distinction explicit and quantifies how misleading a
unique-angle-only ledger would be.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from b7_ft_synthesis_ledger import qasm_ft_resources


ANGLE_RE = re.compile(r"^\s*([a-z][a-z0-9_]*)\(([^)]*)\)\s+(.+);", re.IGNORECASE)
NUMERIC_RE = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?")
ROTATION_GATES = {"rx", "ry", "rz", "u1"}
ARBITRARY_FAMILY = "arbitrary_numeric_rotation"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def metric_path(metrics_path: Path, workload: str) -> Path:
    payload = read_json(metrics_path)
    for row in payload.get("results", []):
        path = Path(row["path"])
        if str(path).endswith(workload):
            return path
    raise ValueError(f"workload {workload} not found in {metrics_path}")


def numeric_catalog(path: Path) -> dict:
    parameter_counter: Counter[str] = Counter()
    instruction_counter: Counter[str] = Counter()
    gate_counter: Counter[str] = Counter()
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = ANGLE_RE.match(raw)
        if not match:
            continue
        gate, params, _operands = match.groups()
        gate = gate.lower()
        if gate not in ROTATION_GATES:
            continue
        numbers = NUMERIC_RE.findall(params)
        if not numbers:
            continue
        for number in numbers:
            parameter_counter[number] += 1
            gate_counter[gate] += 1
            instruction_counter[f"{gate}({number})"] += 1
    return {
        "path": str(path),
        "numeric_parameter_occurrences": sum(parameter_counter.values()),
        "unique_numeric_parameters": len(parameter_counter),
        "numeric_instruction_occurrences": sum(instruction_counter.values()),
        "unique_numeric_instructions": len(instruction_counter),
        "top_numeric_parameters": [
            {"value": value, "count": count} for value, count in parameter_counter.most_common(16)
        ],
        "top_numeric_instructions": [
            {"instruction": value, "count": count} for value, count in instruction_counter.most_common(16)
        ],
        "gate_counts_with_numeric_parameters": dict(sorted(gate_counter.items())),
    }


def ft_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        pi_over_4_t_cost=args.pi_over_4_t_cost,
        pi_over_8_t_cost=args.pi_over_8_t_cost,
        arbitrary_rotation_t_cost=args.arbitrary_rotation_t_cost,
        unknown_rotation_t_cost=args.unknown_rotation_t_cost,
    )


def exact_t_ledger(ft_row: dict) -> int:
    return int(ft_row["logical_t_count_ledger"]) - int(ft_row["t_cost_by_family"].get(ARBITRARY_FAMILY, 0))


def injection_t_ledger(ft_row: dict) -> int:
    return int(ft_row["logical_t_count_ledger"])


def unique_catalog_t_ledger(ft_row: dict, catalog: dict, cost: int) -> int:
    return exact_t_ledger(ft_row) + int(catalog["unique_numeric_instructions"]) * cost


def occurrence_t_ledger(ft_row: dict, cost: int) -> int:
    arbitrary_count = int(ft_row["rotation_family_counts"].get(ARBITRARY_FAMILY, 0))
    return exact_t_ledger(ft_row) + arbitrary_count * cost


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


def compare_with_t_counts(row: dict, before_t: int, after_t: int) -> dict:
    before = reschedule(row["before"], before_t)
    after = reschedule(row["after"], after_t)
    return {
        "workload": row["workload"],
        "factory_variant": row["factory_variant"],
        "before_t_ledger": before_t,
        "after_t_ledger": after_t,
        "before_space_time_volume": before["space_time_volume"],
        "after_space_time_volume": after["space_time_volume"],
        "space_time_volume_reduction": before["space_time_volume"] / after["space_time_volume"],
        "bottleneck_before": before["bottleneck"],
        "bottleneck_after": after["bottleneck"],
    }


def portfolio_retest(ledger: dict, before_t: int, after_t: int, mode_name: str) -> dict:
    comparisons = []
    for row in ledger["comparisons"]:
        if row["workload"] == "qasmbench_medium_exact/gcm_h6.qasm":
            comparisons.append(compare_with_t_counts(row, before_t, after_t))
        else:
            comparisons.append(
                {
                    "workload": row["workload"],
                    "factory_variant": row["factory_variant"],
                    "space_time_volume_reduction": row["space_time_volume_reduction"],
                    "bottleneck_after": row["bottleneck_after"],
                }
            )
    reductions = [row["space_time_volume_reduction"] for row in comparisons if row["space_time_volume_reduction"]]
    min_row = min(comparisons, key=lambda row: row["space_time_volume_reduction"])
    gcm_rows = [row for row in comparisons if row["workload"] == "qasmbench_medium_exact/gcm_h6.qasm"]
    gcm_min = min(gcm_rows, key=lambda row: row["space_time_volume_reduction"])
    return {
        "mode": mode_name,
        "comparison_count": len(comparisons),
        "gcm_h6_before_t_ledger": before_t,
        "gcm_h6_after_t_ledger": after_t,
        "min_space_time_volume_reduction": min(reductions),
        "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
        "min_workload": min_row["workload"],
        "min_factory_variant": min_row["factory_variant"],
        "gcm_h6_min_space_time_volume_reduction": gcm_min["space_time_volume_reduction"],
        "gcm_h6_min_factory_variant": gcm_min["factory_variant"],
        "clears_1_20_all_variant_min": min(reductions) >= 1.20,
        "clears_1_20_gcm_h6_min": gcm_min["space_time_volume_reduction"] >= 1.20,
    }


def run(args: argparse.Namespace) -> dict:
    workload = "qasmbench_medium_exact/gcm_h6.qasm"
    ledger = read_json(args.ledger)
    model_args = ft_args(args)
    before_qasm = metric_path(args.before_metrics, workload)
    after_qasm = metric_path(args.after_metrics, workload)
    before_ft = qasm_ft_resources(before_qasm, model_args)
    after_ft = qasm_ft_resources(after_qasm, model_args)
    before_catalog = numeric_catalog(before_qasm)
    after_catalog = numeric_catalog(after_qasm)

    occurrence_before_t = occurrence_t_ledger(before_ft, args.arbitrary_rotation_t_cost)
    occurrence_after_t = occurrence_t_ledger(after_ft, args.arbitrary_rotation_t_cost)
    unique_before_t = unique_catalog_t_ledger(before_ft, before_catalog, args.arbitrary_rotation_t_cost)
    unique_after_t = unique_catalog_t_ledger(after_ft, after_catalog, args.arbitrary_rotation_t_cost)
    invalid_after_only_t = unique_after_t

    occurrence_retest = portfolio_retest(ledger, occurrence_before_t, occurrence_after_t, "physical_occurrence_injection")
    unique_retest = portfolio_retest(ledger, unique_before_t, unique_after_t, "invalid_unique_template_execution")
    after_only_retest = portfolio_retest(
        ledger,
        occurrence_before_t,
        invalid_after_only_t,
        "invalid_after_only_unique_template_execution",
    )
    after_occ = int(after_ft["rotation_family_counts"].get(ARBITRARY_FAMILY, 0))
    after_unique = int(after_catalog["unique_numeric_instructions"])
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 shared-synthesis/cache boundary for repeated gcm_h6 rotations",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": "shared_synthesis_cache_no_ft_t_ledger_reduction_boundary",
        "method": "b7_shared_synthesis_cache_boundary_v0",
        "source_ledger": str(args.ledger),
        "before_qasm": str(before_qasm),
        "after_qasm": str(after_qasm),
        "arbitrary_rotation_t_cost": args.arbitrary_rotation_t_cost,
        "before_numeric_catalog": before_catalog,
        "after_numeric_catalog": after_catalog,
        "before_ft_resource": before_ft,
        "after_ft_resource": after_ft,
        "physical_occurrence_injection_model": {
            "semantics": "each rotation occurrence consumes a physical fault-tolerant rotation injection",
            "before_t_ledger": occurrence_before_t,
            "after_t_ledger": occurrence_after_t,
            "after_arbitrary_occurrences": after_occ,
            "after_unique_numeric_instructions": after_unique,
            "after_classical_catalog_synthesis_count": after_unique,
            "after_physical_rotation_injection_count": after_occ,
            "classical_catalog_reduction_factor": after_occ / after_unique if after_unique else None,
            "ft_t_ledger_reduction_from_cache": 0,
            "portfolio_retest": occurrence_retest,
        },
        "invalid_unique_template_execution_model": {
            "semantics": "counts unique synthesized numeric instructions as if one physical rotation resource served all occurrences",
            "why_invalid": "a compiled template can be reused as classical instructions, but the quantum circuit still applies each rotation occurrence",
            "before_t_ledger": unique_before_t,
            "after_t_ledger": unique_after_t,
            "portfolio_retest": unique_retest,
        },
        "invalid_after_only_unique_template_model": {
            "semantics": "applies unique-template charging only to the optimized after-row",
            "why_invalid": "unfair baseline accounting plus the same physical occurrence reuse error",
            "before_t_ledger": occurrence_before_t,
            "after_t_ledger": invalid_after_only_t,
            "portfolio_retest": after_only_retest,
        },
        "claim_boundary": {
            "shared_synthesis_cache_can_reduce_classical_template_count": True,
            "shared_synthesis_cache_reduces_ft_t_ledger_under_occurrence_injection_model": False,
            "would_clear_1_20_if_miscounted_as_unique_execution": unique_retest["clears_1_20_all_variant_min"],
            "would_clear_gcm_h6_1_20_if_miscounted_as_unique_execution": unique_retest["clears_1_20_gcm_h6_min"],
            "would_clear_1_20_if_miscounted_after_only": after_only_retest["clears_1_20_all_variant_min"],
            "would_clear_gcm_h6_1_20_if_miscounted_after_only": after_only_retest["clears_1_20_gcm_h6_min"],
        },
        "interpretation": (
            "Repeated gcm_h6 numeric angles support a classical synthesis-template cache, but the physical FT resource "
            "ledger remains occurrence-based.  Counting only unique numeric instructions would create an apparent "
            "resource win by changing the execution model, not by solving the circuit."
        ),
        "next_actions": [
            "A real T-ledger reduction must reduce physical rotation occurrences or replace a repeated block with a proven lower-cost unitary template.",
            "Try a nonlocal template-aware pass on repeated gcm_h6 blocks and verify it with Aer/proof logs.",
            "Keep shared-synthesis/cache as a compile-time optimization unless a physical reusable-state protocol is specified.",
        ],
        "limits": [
            "This is a resource-accounting boundary, not a certified no-go theorem for all possible circuit identities.",
            "The unique-template model is intentionally marked invalid for FT execution accounting.",
            "A future block-template rewrite could still reduce T ledger if it changes the implemented unitary with a proof.",
        ],
    }


def fmt(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    return f"{value:.6g}"


def markdown(report: dict) -> str:
    physical = report["physical_occurrence_injection_model"]
    invalid_unique = report["invalid_unique_template_execution_model"]
    invalid_after = report["invalid_after_only_unique_template_model"]
    lines = [
        "# B7 Shared-Synthesis Cache Boundary v0.1",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source ledger: `{report['source_ledger']}`",
        f"- Before QASM: `{report['before_qasm']}`",
        f"- After QASM: `{report['after_qasm']}`",
        f"- Arbitrary rotation T cost: {report['arbitrary_rotation_t_cost']}",
        f"- After numeric occurrences / unique instructions: {physical['after_arbitrary_occurrences']} / {physical['after_unique_numeric_instructions']}",
        f"- Classical catalog reduction factor: {physical['classical_catalog_reduction_factor']:.6f}x",
        f"- FT T-ledger reduction from cache: {physical['ft_t_ledger_reduction_from_cache']}",
        f"- Physical occurrence model clears 1.20x: {physical['portfolio_retest']['clears_1_20_all_variant_min']}",
        f"- Invalid unique-template model clears 1.20x: {invalid_unique['portfolio_retest']['clears_1_20_all_variant_min']}",
        f"- Invalid after-only unique-template model clears 1.20x: {invalid_after['portfolio_retest']['clears_1_20_all_variant_min']}",
        f"- Interpretation: {report['interpretation']}",
        "",
        "## Ledger Models",
        "",
        "| model | before T ledger | after T ledger | min STV | gcm_h6 min STV | clears 1.20x | validity |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for model, validity in [
        (physical, "valid occurrence-execution ledger"),
        (invalid_unique, "invalid for FT execution"),
        (invalid_after, "invalid and unfair after-only charging"),
    ]:
        retest = model["portfolio_retest"]
        lines.append(
            f"| {retest['mode']} | {model['before_t_ledger']} | {model['after_t_ledger']} | "
            f"{retest['min_space_time_volume_reduction']:.6f}x | "
            f"{retest['gcm_h6_min_space_time_volume_reduction']:.6f}x | "
            f"{retest['clears_1_20_all_variant_min']} | {validity} |"
        )
    lines.extend(
        [
            "",
            "## After Numeric Catalog",
            "",
            "| numeric instruction | occurrences |",
            "|---|---:|",
        ]
    )
    for row in report["after_numeric_catalog"]["top_numeric_instructions"]:
        lines.append(f"| `{row['instruction']}` | {row['count']} |")
    lines.extend(["", "## Claim Boundary", ""])
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=Path("results/B7_ft_synthesis_ledger_v0.json"))
    parser.add_argument(
        "--before-metrics",
        type=Path,
        default=Path("results/b1_virtual_swap_elimination_level1/before_virtual_swap_metrics.json"),
    )
    parser.add_argument(
        "--after-metrics",
        type=Path,
        default=Path("results/b1_u3_phase_factored_optimizer/after_metrics.json"),
    )
    parser.add_argument("--pi-over-4-t-cost", type=int, default=1)
    parser.add_argument("--pi-over-8-t-cost", type=int, default=4)
    parser.add_argument("--arbitrary-rotation-t-cost", type=int, default=20)
    parser.add_argument("--unknown-rotation-t-cost", type=int, default=20)
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_shared_synthesis_cache_boundary_v0.json"))
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B7_shared_synthesis_cache_boundary.md"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run(args)
    write_json(args.json_output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    physical = report["physical_occurrence_injection_model"]
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")
    print(
        f"status={report['status']} occurrence_t={physical['before_t_ledger']}->{physical['after_t_ledger']} "
        f"catalog={physical['after_arbitrary_occurrences']}->{physical['after_unique_numeric_instructions']} "
        f"clears_1_20={physical['portfolio_retest']['clears_1_20_all_variant_min']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
