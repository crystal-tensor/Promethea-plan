#!/usr/bin/env python3
"""T-B1-004fv/T-B7-015e: cost-aware packet synthesis search.

The earlier packet synthesis gate selected the smallest numerical residual for
each fixed CNOT scaffold.  R72 keeps the exact replay tolerance but records a
second objective: the pinned fault-tolerant rotation-family cost of every
local-U3 parameter.  This prevents an exact local synthesis candidate from
being treated as progress when its added arbitrary rotations cost more than
the source packet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
from scipy.optimize import least_squares

from b1_b7_cone01_packet_synthesis_search_gate import (
    EXACT_TOLERANCE,
    pair_layer,
    phase_align,
    residual_vector,
    scaffold_unitary,
    seed_points,
    target_matrix,
    wrap_angles,
)
from b7_ft_synthesis_ledger import classify_rotation, rotation_cost


METHOD = "b1_b7_cone01_r72_cost_aware_packet_synthesis_gate_v0"
STATUS = "cone01_r72_exact_packet_scaffolds_cost_dominated_boundary"
MODEL_STATUS = "fixed_direction_exact_synthesis_has_no_ft_rotation_cost_improvement"
VERSION = "0.1"
TARGET_ID = "T-B1-004fv/T-B7-015e"
UPSTREAM_TARGET_ID = "T-B1-004fu/T-B7-015d"
SEMANTIC_PACKET = "results/B1_B7_cone01_semantic_replay_packet_gate_v0.json"
R71_RESULT = "results/B1_B7_cone01_R71_resource_delta_ledger_gate_v0.json"
DEFAULT_SEED_COUNT = 16
DEFAULT_MAX_NFEV = 2200


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def req(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def cost_args() -> SimpleNamespace:
    return SimpleNamespace(
        pi_over_4_t_cost=1,
        pi_over_8_t_cost=4,
        arbitrary_rotation_t_cost=20,
        unknown_rotation_t_cost=20,
    )


def source_rotation_cost(packet: dict[str, Any], args: SimpleNamespace) -> dict[str, Any]:
    total = 0
    families: dict[str, int] = {}
    for operation in packet["normalized_ops"]:
        if operation["gate"] == "cx":
            continue
        expression = operation["raw_args"][0]
        cost, family = rotation_cost(expression, args)
        total += cost
        families[family] = families.get(family, 0) + 1
    return {"rotation_cost": total, "rotation_family_counts": dict(sorted(families.items()))}


def candidate_rotation_cost(parameters: list[float], args: SimpleNamespace) -> dict[str, Any]:
    total = 0
    families: dict[str, int] = {}
    for value in parameters:
        cost, family = rotation_cost(str(value), args)
        total += cost
        families[family] = families.get(family, 0) + 1
    return {
        "rotation_cost": total,
        "rotation_family_counts": dict(sorted(families.items())),
        "parameter_count": len(parameters),
        "off_pi_over_four_parameter_count": sum(
            1 for value in parameters if classify_rotation(str(value)) == "arbitrary_numeric_rotation"
        ),
    }


def first_cnot_orientation(packet: dict[str, Any]) -> tuple[int, int]:
    for operation in packet["normalized_ops"]:
        if operation["gate"] == "cx":
            return int(operation["local_control"]), int(operation["local_target"])
    raise ValueError(f"packet has no CNOT orientation: {packet['candidate_line_number']}")


def solve_scaffold(
    packet: dict[str, Any],
    target: np.ndarray,
    cnot_count: int,
    control: int,
    target_qubit: int,
    seed_count: int,
    max_nfev: int,
    args: SimpleNamespace,
) -> list[dict[str, Any]]:
    def objective(values: np.ndarray) -> np.ndarray:
        return residual_vector(scaffold_unitary(values, cnot_count, control, target_qubit), target)

    solutions: list[dict[str, Any]] = []
    for seed_index, seed in enumerate(seed_points(packet, cnot_count, seed_count)):
        result = least_squares(
            objective,
            seed,
            method="trf",
            max_nfev=max_nfev,
            ftol=1e-12,
            xtol=1e-12,
            gtol=1e-12,
        )
        residual = float(np.linalg.norm(result.fun))
        candidate = scaffold_unitary(result.x, cnot_count, control, target_qubit)
        aligned_error = phase_align(candidate, target) - target
        wrapped = wrap_angles(result.x)
        candidate_cost = candidate_rotation_cost(wrapped, args)
        solutions.append(
            {
                "seed_index": seed_index,
                "cnot_count": cnot_count,
                "control": control,
                "target": target_qubit,
                "residual_norm": residual,
                "max_abs_entry_error": float(np.max(np.abs(aligned_error))),
                "optimizer_success": bool(result.success),
                "optimizer_nfev": int(result.nfev),
                "exact_pass": residual <= EXACT_TOLERANCE,
                "wrapped_parameters": wrapped,
                "candidate_rotation_cost": candidate_cost,
            }
        )
    return solutions


def analyze_packet(
    packet: dict[str, Any], seed_count: int, max_nfev: int, args: SimpleNamespace
) -> dict[str, Any]:
    target = target_matrix(packet)
    control, target_qubit = first_cnot_orientation(packet)
    source_cost = source_rotation_cost(packet, args)
    source_cnot_count = int(packet["cx_count"])
    all_solutions: list[dict[str, Any]] = []
    for cnot_count in range(min(3, source_cnot_count - 1) + 1):
        all_solutions.extend(
            solve_scaffold(
                packet,
                target,
                cnot_count,
                control,
                target_qubit,
                seed_count,
                max_nfev,
                args,
            )
        )
    exact = [row for row in all_solutions if row["exact_pass"]]
    exact_sorted_by_cost = sorted(
        exact,
        key=lambda row: (
            row["candidate_rotation_cost"]["rotation_cost"],
            row["cnot_count"],
            row["residual_norm"],
        ),
    )
    best_by_cost = exact_sorted_by_cost[0] if exact_sorted_by_cost else None
    return {
        "candidate_line_number": int(packet["candidate_line_number"]),
        "pattern_id": packet["pattern_id"],
        "support_qubits": packet["support_qubits"],
        "source_cnot_count": source_cnot_count,
        "source_rotation_cost": source_cost,
        "search_cnot_counts": list(range(min(3, source_cnot_count - 1) + 1)),
        "seed_count_per_scaffold": seed_count,
        "max_nfev": max_nfev,
        "attempt_count": len(all_solutions),
        "exact_solution_count": len(exact),
        "best_exact_by_cost": best_by_cost,
        "best_exact_rotation_cost": (
            best_by_cost["candidate_rotation_cost"]["rotation_cost"] if best_by_cost else None
        ),
        "source_minus_best_exact_rotation_cost": (
            source_cost["rotation_cost"] - best_by_cost["candidate_rotation_cost"]["rotation_cost"]
            if best_by_cost
            else None
        ),
        "cost_improving_exact_solution_found": bool(
            best_by_cost
            and best_by_cost["candidate_rotation_cost"]["rotation_cost"] < source_cost["rotation_cost"]
        ),
        "cnot_reducing_exact_solution_found": any(
            row["cnot_count"] < source_cnot_count for row in exact
        ),
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "all_exact_solutions": exact_sorted_by_cost,
    }


def build_payload(root: Path, seed_count: int, max_nfev: int) -> dict[str, Any]:
    started = time.time()
    semantic_path = root / SEMANTIC_PACKET
    r71_path = root / R71_RESULT
    semantic = load_json(semantic_path)
    r71 = load_json(r71_path)
    args = cost_args()
    rows = [analyze_packet(packet, seed_count, max_nfev, args) for packet in semantic["semantic_replay_packets"]]
    exact_solution_count = sum(row["exact_solution_count"] for row in rows)
    cnot_reducing_count = sum(1 for row in rows if row["cnot_reducing_exact_solution_found"])
    cost_improving_count = sum(1 for row in rows if row["cost_improving_exact_solution_found"])
    requirements = [
        req(
            "R1",
            "Three source semantic replay packets are available",
            len(rows) == 3,
            {"packet_count": len(rows), "source_method": semantic["method"]},
        ),
        req(
            "R2",
            "R71 upstream remains a verified full-circuit resource regression boundary",
            r71["summary"]["requirements_failed"] == 0
            and r71["summary"]["full_circuit_ft_resource_regression"] is True,
            {
                "r71_requirements_failed": r71["summary"]["requirements_failed"],
                "r71_full_circuit_ft_resource_regression": r71["summary"][
                    "full_circuit_ft_resource_regression"
                ],
            },
        ),
        req(
            "R3",
            "The rotation-family cost model is pinned",
            args.pi_over_4_t_cost == 1
            and args.pi_over_8_t_cost == 4
            and args.arbitrary_rotation_t_cost == 20
            and args.unknown_rotation_t_cost == 20,
            {
                "pi_over_4_t_cost": args.pi_over_4_t_cost,
                "pi_over_8_t_cost": args.pi_over_8_t_cost,
                "arbitrary_rotation_t_cost": args.arbitrary_rotation_t_cost,
                "unknown_rotation_t_cost": args.unknown_rotation_t_cost,
            },
        ),
        req(
            "R4",
            "Each packet has exact solutions under the strict replay tolerance",
            all(row["exact_solution_count"] > 0 for row in rows),
            {"exact_solution_count_by_packet": [row["exact_solution_count"] for row in rows]},
        ),
        req(
            "R5",
            "Exact reduced-CNOT packet solutions are found",
            cnot_reducing_count == 3,
            {"cnot_reducing_packet_count": cnot_reducing_count},
        ),
        req(
            "R6",
            "No exact reduced-CNOT packet solution beats its source rotation cost",
            cost_improving_count == 0
            and all(
                row["source_minus_best_exact_rotation_cost"] is not None
                and row["source_minus_best_exact_rotation_cost"] < 0
                for row in rows
            ),
            {
                "cost_improving_packet_count": cost_improving_count,
                "source_minus_best_exact_rotation_cost": [
                    row["source_minus_best_exact_rotation_cost"] for row in rows
                ],
            },
        ),
        req(
            "R7",
            "The cost-aware search emits no accepted B7 delta",
            all(row["accepted_occurrence_removal"] == 0 for row in rows)
            and all(row["accepted_proxy_t_reduction"] == 0 for row in rows),
            {
                "accepted_occurrence_removal": 0,
                "accepted_proxy_t_reduction": 0,
            },
        ),
        req(
            "R8",
            "The search packet is reproducibly serialized",
            exact_solution_count > 0 and all(row["attempt_count"] > 0 for row in rows),
            {
                "attempt_count_by_packet": [row["attempt_count"] for row in rows],
                "exact_solution_count": exact_solution_count,
            },
        ),
    ]
    summary = {
        "packet_count": len(rows),
        "seed_count_per_scaffold": seed_count,
        "max_nfev": max_nfev,
        "total_attempt_count": sum(row["attempt_count"] for row in rows),
        "exact_solution_count": exact_solution_count,
        "cnot_reducing_packet_count": cnot_reducing_count,
        "cost_improving_packet_count": cost_improving_count,
        "source_minus_best_exact_rotation_cost": [
            row["source_minus_best_exact_rotation_cost"] for row in rows
        ],
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "accepted_exit_route_count": 0,
        "b7_credit_delta": 0,
        "requirements_passed": sum(1 for item in requirements if item["passed"]),
        "requirements_failed": sum(1 for item in requirements if not item["passed"]),
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "o3_closed": False,
        "reroute_allowed": False,
        "runtime_seconds": round(time.time() - started, 6),
    }
    payload: dict[str, Any] = {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "version": VERSION,
        "target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_semantic_packet": rel(root, semantic_path),
        "source_semantic_packet_sha256": file_hash(semantic_path),
        "source_r71_result": rel(root, r71_path),
        "source_r71_result_sha256": file_hash(r71_path),
        "cost_model": {
            "clifford_rotation_t_cost": 0,
            "pi_over_4_rotation_t_cost": args.pi_over_4_t_cost,
            "pi_over_8_rotation_t_cost": args.pi_over_8_t_cost,
            "arbitrary_rotation_t_cost": args.arbitrary_rotation_t_cost,
            "unknown_rotation_t_cost": args.unknown_rotation_t_cost,
        },
        "requirements": requirements,
        "summary": summary,
        "packet_rows": rows,
        "claim_boundary": {
            "supported_claim": (
                "Within the tested fixed-direction local-U3 scaffold family and strict "
                "numerical replay tolerance, exact reduced-CNOT packet solutions exist, "
                "but none beats the source packet's pinned FT rotation cost."
            ),
            "unsupported_claims": [
                "This is not a global synthesis lower bound.",
                "This does not produce a full-circuit rewrite or arbitrary-input proof.",
                "This does not accept occurrence removal, proxy-T reduction, reroute, or B7 credit.",
            ],
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }
    payload["payload_hash"] = stable_hash(payload)
    return payload


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone01 R72 Cost-Aware Packet Synthesis Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Requirements: `{summary['requirements_passed']}/{len(payload['requirements'])}`",
        f"- Search attempts: `{summary['total_attempt_count']}`",
        f"- Exact solution count: `{summary['exact_solution_count']}`",
        f"- Packets with reduced-CNOT exact solutions: `{summary['cnot_reducing_packet_count']}`",
        f"- Packets with FT-cost improvement: `{summary['cost_improving_packet_count']}`",
        f"- Source minus best exact rotation cost: `{summary['source_minus_best_exact_rotation_cost']}`",
        f"- Accepted occurrence removal / proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- B7 credit: `{summary['b7_credit_delta']}`",
        "",
        "## Interpretation",
        "",
        "The search finds exact local solutions with fewer CNOTs, but every best exact solution is rotation-cost dominated by its source packet under the pinned FT proxy ledger. This strengthens the R71 conclusion: residual-zero local synthesis is not enough; the candidate must also lower the non-Clifford resource burden.",
        "",
        "## Claim Boundary",
        "",
        "- This is a scoped fixed-direction numerical search, not a global lower-bound theorem.",
        "- No full-circuit rewrite, occurrence removal, proxy-T reduction, reroute, or B7 credit is accepted.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--seed-count", type=int, default=DEFAULT_SEED_COUNT)
    parser.add_argument("--max-nfev", type=int, default=DEFAULT_MAX_NFEV)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R72_cost_aware_packet_synthesis_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R72_cost_aware_packet_synthesis_gate.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    payload = build_payload(root, args.seed_count, args.max_nfev)
    json_output = args.json_output if args.json_output.is_absolute() else root / args.json_output
    markdown_output = args.markdown_output if args.markdown_output.is_absolute() else root / args.markdown_output
    write_json(json_output, payload)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.write_text(report(payload), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": payload["status"],
                    "requirements_passed": payload["summary"]["requirements_passed"],
                    "requirements_failed": payload["summary"]["requirements_failed"],
                    "total_attempt_count": payload["summary"]["total_attempt_count"],
                    "exact_solution_count": payload["summary"]["exact_solution_count"],
                    "source_minus_best_exact_rotation_cost": payload["summary"][
                        "source_minus_best_exact_rotation_cost"
                    ],
                    "payload_hash": payload["payload_hash"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
