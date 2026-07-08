#!/usr/bin/env python3
"""T-B1-004fp/T-B7-014y: R66 B7 zero-credit ledger retest boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r66_o3_f4_b7_zero_credit_ledger_retest_gate_v0"
STATUS = "cone01_r66_b7_zero_credit_ledger_retest_boundary_passed"
MODEL_STATUS = "r65_replay_rows_retested_against_b7_ledger_with_zero_credit"
VERSION = "0.1"
TARGET_ID = "T-B1-004fp/T-B7-014y"
UPSTREAM_TARGET_ID = "T-B1-004fo/T-B7-014x"
ROW_DIR = "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows"


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def req(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def build_retest_row(root: Path, verdict: dict[str, Any]) -> dict[str, Any]:
    digest = verdict["replay_semantic_digest"]
    challenge_id = verdict["challenge_id"]
    row = {
        "challenge_id": challenge_id,
        "source_r65_verdict_file": verdict["verdict_file"],
        "source_r65_verdict_file_sha256": verdict["verdict_file_sha256"],
        "source_r65_verdict_hash": verdict["verdict_hash"],
        "machine_check_replay_passed": verdict["machine_check_replay_passed"],
        "semantic_digest_hash": verdict["semantic_digest_hash"],
        "source_circuit_file": digest["source_circuit_file"],
        "source_circuit_sha256": digest["source_circuit_sha256"],
        "candidate_circuit_file": digest["candidate_circuit_file"],
        "candidate_circuit_sha256": digest["candidate_circuit_sha256"],
        "denominator_distance": digest["denominator_distance"],
        "negative_control_rejected": digest["negative_control_rejected"],
        "forbidden_inputs_used": digest["forbidden_inputs_used"],
        "full_circuit_rewrite_artifact_present": False,
        "accepted_exit_route_present": False,
        "occurrence_removal_delta": 0,
        "proxy_t_reduction_delta": 0,
        "logical_t_count_delta": 0,
        "logical_t_depth_delta": 0,
        "space_time_volume_delta": 0,
        "b7_dependency_credit_allowed": False,
        "b7_resource_credit_allowed": False,
        "b7_ft_ledger_credit_allowed": False,
        "ledger_credit_admissible": False,
        "blocked_reasons": [
            "R65 replay verdict is row-level denominator evidence, not a full-circuit rewrite",
            "no accepted exit route is attached to the row",
            "occurrence_removal_delta is 0",
            "proxy_t_reduction_delta is 0",
            "logical-T and STV deltas are 0",
        ],
    }
    row["row_hash"] = stable_hash(row)
    row_path = root / ROW_DIR / f"{challenge_id}.r66_b7_zero_credit_ledger_retest_row.json"
    write_json(row_path, row)
    row["row_file"] = str(row_path.relative_to(root))
    row["row_file_sha256"] = file_hash(row_path)
    return row


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r65 = load_json(args.r65_result)
    b7_boundary = load_json(args.b7_resource_boundary)
    r4_block = load_json(args.r4_block_gate)
    ft_ledger = load_json(args.ft_ledger)
    verdicts = r65["r65_c7_machine_check_replay_packet"]["verdicts"]
    retest_rows = [build_retest_row(args.root, verdict) for verdict in verdicts]
    b7_summary = b7_boundary["summary"]
    r4_summary = r4_block["summary"]
    ledger_summary = ft_ledger.get("summary", {})
    if not ledger_summary:
        ledger_summary = {
            "comparison_count": ft_ledger.get("comparison_count"),
            "min_space_time_volume_reduction": ft_ledger.get(
                "min_space_time_volume_reduction"
            ),
            "mean_space_time_volume_reduction": ft_ledger.get(
                "mean_space_time_volume_reduction"
            ),
        }
    retest_packet = {
        "artifact": "R66 B7 zero-credit ledger retest boundary",
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "method": METHOD,
        "source_r65_result": str(args.r65_result),
        "source_r65_file_sha256": file_hash(args.r65_result),
        "source_r65_bundle_hash": r65["summary"]["r65_bundle_hash"],
        "source_b7_resource_boundary": str(args.b7_resource_boundary),
        "source_b7_boundary_file_sha256": file_hash(args.b7_resource_boundary),
        "source_b7_boundary_hash": b7_summary["boundary_hash"],
        "source_r4_block_gate": str(args.r4_block_gate),
        "source_r4_block_file_sha256": file_hash(args.r4_block_gate),
        "source_r4_block_packet_hash": r4_summary["r4_block_packet_hash"],
        "source_ft_ledger": str(args.ft_ledger),
        "source_ft_ledger_file_sha256": file_hash(args.ft_ledger),
        "source_ft_ledger_summary": ledger_summary,
        "retest_row_count": len(retest_rows),
        "machine_checked_row_count": sum(
            1 for row in retest_rows if row["machine_check_replay_passed"]
        ),
        "ledger_credit_admissible_row_count": sum(
            1 for row in retest_rows if row["ledger_credit_admissible"]
        ),
        "accepted_exit_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "logical_t_count_delta": 0,
        "logical_t_depth_delta": 0,
        "space_time_volume_delta": 0,
        "b7_dependency_credit_allowed": False,
        "b7_resource_credit_allowed": False,
        "b7_ft_ledger_credit_allowed": False,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "o3_closed": False,
        "reroute_allowed": False,
        "ledger_retest_boundary_complete": True,
        "retest_rows": {
            row["challenge_id"]: row["row_file"] for row in retest_rows
        },
        "row_hashes": {row["challenge_id"]: row["row_hash"] for row in retest_rows},
        "claim_boundary": (
            "R66 retests the R65 machine-checked row set against the B7 ledger boundary "
            "and confirms zero admissible ledger credit. It does not close O3, allow "
            "reroute, or grant dependency/resource/FT/STV credit."
        ),
    }
    retest_packet["retest_packet_hash"] = stable_hash(retest_packet)
    write_json(args.packet_output, retest_packet)
    requirements = [
        req(
            "Z1",
            "R65 upstream completed C7 with zero B7 credit",
            r65["summary"]["c7_machine_check_replay_complete"] is True
            and r65["summary"]["passed_verdict_count"] == 8
            and r65["summary"]["b7_credit_delta"] == 0,
            {
                "source_r65_bundle_hash": r65["summary"]["r65_bundle_hash"],
                "passed_verdict_count": r65["summary"]["passed_verdict_count"],
                "b7_credit_delta": r65["summary"]["b7_credit_delta"],
            },
        ),
        req(
            "Z2",
            "B7 resource boundary still denies resource, dependency, FT, and STV credit",
            b7_summary["b7_resource_credit_allowed"] is False
            and b7_summary["b7_ft_ledger_credit_allowed"] is False
            and b7_summary["b7_space_time_volume_credit"] == 0
            and b7_summary["b7_credit_delta"] == 0,
            {
                "boundary_hash": b7_summary["boundary_hash"],
                "b7_resource_credit_allowed": b7_summary["b7_resource_credit_allowed"],
                "b7_ft_ledger_credit_allowed": b7_summary["b7_ft_ledger_credit_allowed"],
                "b7_space_time_volume_credit": b7_summary["b7_space_time_volume_credit"],
                "b7_credit_delta": b7_summary["b7_credit_delta"],
            },
        ),
        req(
            "Z3",
            "R4 refreshed B7 ledger replay remains blocked before accepted exit routes",
            r4_summary["r4_replay_allowed"] is False
            and r4_summary["accepted_exit_route_count"] == 0
            and r4_summary["accepted_occurrence_removal"] == 0
            and r4_summary["accepted_proxy_t_reduction"] == 0,
            {
                "r4_block_packet_hash": r4_summary["r4_block_packet_hash"],
                "r4_replay_allowed": r4_summary["r4_replay_allowed"],
                "accepted_exit_route_count": r4_summary["accepted_exit_route_count"],
            },
        ),
        req(
            "Z4",
            "All 8 R65 rows are machine checked but none are ledger-credit admissible",
            retest_packet["retest_row_count"] == 8
            and retest_packet["machine_checked_row_count"] == 8
            and retest_packet["ledger_credit_admissible_row_count"] == 0,
            {
                "retest_row_count": retest_packet["retest_row_count"],
                "machine_checked_row_count": retest_packet["machine_checked_row_count"],
                "ledger_credit_admissible_row_count": retest_packet[
                    "ledger_credit_admissible_row_count"
                ],
            },
        ),
        req(
            "Z5",
            "Retest rows carry zero occurrence, proxy-T, logical-T, depth, and STV deltas",
            sum(row["occurrence_removal_delta"] for row in retest_rows) == 0
            and sum(row["proxy_t_reduction_delta"] for row in retest_rows) == 0
            and sum(row["logical_t_count_delta"] for row in retest_rows) == 0
            and sum(row["logical_t_depth_delta"] for row in retest_rows) == 0
            and sum(row["space_time_volume_delta"] for row in retest_rows) == 0,
            {
                "accepted_occurrence_removal": retest_packet["accepted_occurrence_removal"],
                "accepted_proxy_t_reduction": retest_packet["accepted_proxy_t_reduction"],
                "logical_t_count_delta": retest_packet["logical_t_count_delta"],
                "logical_t_depth_delta": retest_packet["logical_t_depth_delta"],
                "space_time_volume_delta": retest_packet["space_time_volume_delta"],
            },
        ),
        req(
            "Z6",
            "R66 preserves O3, reroute, and B7 zero-credit boundaries",
            retest_packet["o3_closed"] is False
            and retest_packet["reroute_allowed"] is False
            and retest_packet["b7_credit_delta"] == 0
            and retest_packet["b7_space_time_volume_credit"] == 0
            and retest_packet["resource_saving_claimed"] is False
            and retest_packet["b7_ledger_improvement_claimed"] is False,
            {
                "o3_closed": retest_packet["o3_closed"],
                "reroute_allowed": retest_packet["reroute_allowed"],
                "b7_credit_delta": retest_packet["b7_credit_delta"],
                "b7_space_time_volume_credit": retest_packet[
                    "b7_space_time_volume_credit"
                ],
            },
        ),
        req(
            "Z7",
            "R66 binds the FT ledger as read-only evidence rather than mutating it",
            bool(retest_packet["source_ft_ledger_file_sha256"])
            and retest_packet["logical_t_count_delta"] == 0
            and retest_packet["space_time_volume_delta"] == 0,
            {
                "source_ft_ledger_file_sha256": retest_packet[
                    "source_ft_ledger_file_sha256"
                ],
                "logical_t_count_delta": retest_packet["logical_t_count_delta"],
                "space_time_volume_delta": retest_packet["space_time_volume_delta"],
            },
        ),
        req(
            "Z8",
            "R66 writes an auditable retest packet and per-row retest files",
            bool(retest_packet["retest_packet_hash"])
            and all((args.root / row["row_file"]).is_file() for row in retest_rows),
            {
                "retest_packet_hash": retest_packet["retest_packet_hash"],
                "row_file_count": len(retest_packet["retest_rows"]),
            },
        ),
    ]
    failed = [item["requirement_id"] for item in requirements if not item["passed"]]
    summary = {
        "source_r65_bundle_hash": r65["summary"]["r65_bundle_hash"],
        "source_b7_boundary_hash": b7_summary["boundary_hash"],
        "source_r4_block_packet_hash": r4_summary["r4_block_packet_hash"],
        "r66_retest_packet_hash": retest_packet["retest_packet_hash"],
        "r66_retest_packet_file_sha256": file_hash(args.packet_output),
        "retest_row_count": retest_packet["retest_row_count"],
        "machine_checked_row_count": retest_packet["machine_checked_row_count"],
        "ledger_credit_admissible_row_count": retest_packet[
            "ledger_credit_admissible_row_count"
        ],
        "accepted_exit_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "logical_t_count_delta": 0,
        "logical_t_depth_delta": 0,
        "space_time_volume_delta": 0,
        "b7_dependency_credit_allowed": False,
        "b7_resource_credit_allowed": False,
        "b7_ft_ledger_credit_allowed": False,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "o3_closed": False,
        "reroute_allowed": False,
        "ledger_retest_boundary_complete": True,
        "remaining_open_obligations": [
            "accepted_exit_route_or_full_circuit_rewrite_artifact",
            "nonzero_occurrence_or_proxy_t_delta",
            "B7_ledger_retest_after_nonzero_delta",
        ],
        "remaining_open_obligation_count": 3,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
        "validation_error_count": len(failed),
    }
    return {
        "title": "B1/B7 Cone01 R66 O3-F4 B7 Zero-Credit Ledger Retest Gate",
        "version": VERSION,
        "last_updated": "2026-07-09",
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "r66_b7_zero_credit_ledger_retest_packet": {
            "source_r65_result": str(args.r65_result),
            "source_b7_resource_boundary": str(args.b7_resource_boundary),
            "source_r4_block_gate": str(args.r4_block_gate),
            "source_ft_ledger": str(args.ft_ledger),
            "packet_output": str(args.packet_output),
            "packet": retest_packet,
            "retest_rows": retest_rows,
        },
        "requirements": requirements,
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": (
                "R66 binds the R65 machine-checked row set into a B7 ledger retest "
                "boundary and proves the current row set admits zero dependency, "
                "resource, FT, STV, occurrence-removal, proxy-T, or ledger credit."
            ),
            "what_is_not_supported": (
                "R66 does not close O3, prove a full-circuit rewrite, allow reroute, "
                "or grant any B7 ledger promotion."
            ),
            "next_gate": (
                "Submit an accepted exit route or full-circuit rewrite with nonzero "
                "occurrence/proxy-T delta before any nonzero B7 ledger retest."
            ),
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": failed,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    s = payload["summary"]
    lines = [
        "# B1/B7 Cone01 R66 O3-F4 B7 Zero-Credit Ledger Retest Gate",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- R66 retest packet hash: `{s['r66_retest_packet_hash']}`",
        "",
        "## Result",
        "",
        (
            f"R66 passes {s['requirements_passed']}/{s['requirement_count']} "
            "requirements by binding the R65 machine-checked row set into a B7 "
            "ledger retest boundary while preserving zero admissible ledger credit. "
            "The retest is complete as a boundary, not as a promotion."
        ),
        "",
        "## Evidence",
        "",
        f"- Retest rows: `{s['retest_row_count']}`",
        f"- Machine-checked rows: `{s['machine_checked_row_count']}`",
        f"- Ledger-credit-admissible rows: `{s['ledger_credit_admissible_row_count']}`",
        f"- Accepted exit routes: `{s['accepted_exit_route_count']}`",
        f"- Accepted occurrence removal: `{s['accepted_occurrence_removal']}`",
        f"- Accepted proxy-T reduction: `{s['accepted_proxy_t_reduction']}`",
        f"- Logical-T count delta: `{s['logical_t_count_delta']}`",
        f"- Logical-T depth delta: `{s['logical_t_depth_delta']}`",
        f"- Space-time-volume delta: `{s['space_time_volume_delta']}`",
        f"- B7 dependency/resource/FT credit allowed: `{s['b7_dependency_credit_allowed']}` / `{s['b7_resource_credit_allowed']}` / `{s['b7_ft_ledger_credit_allowed']}`",
        f"- B7 credit delta: `{s['b7_credit_delta']}`",
        "",
        "## Requirement Results",
        "",
    ]
    for item in payload["requirements"]:
        lines.append(f"- `{item['requirement_id']}` {'PASS' if item['passed'] else 'FAIL'}: {item['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            "## Remaining Open Obligations",
            "",
        ]
    )
    for item in s["remaining_open_obligations"]:
        lines.append(f"- `{item}`")
    lines.extend(["", f"- validation_error_count: `{s['validation_error_count']}`", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--r65-result",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_R65_o3_f4_c7_machine_check_replay_gate_v0.json"
        ),
    )
    parser.add_argument(
        "--b7-resource-boundary",
        type=Path,
        default=Path("results/B7_B1_cone01_resource_escape_boundary_v0.json"),
    )
    parser.add_argument(
        "--r4-block-gate",
        type=Path,
        default=Path("results/B1_B7_cone01_R4_b7_ledger_replay_blocked_gate_v0.json"),
    )
    parser.add_argument(
        "--ft-ledger",
        type=Path,
        default=Path("results/B7_ft_synthesis_ledger_v0.json"),
    )
    parser.add_argument(
        "--packet-output",
        type=Path,
        default=Path(f"{ROW_DIR}/O3-F4-all8.r66_b7_zero_credit_ledger_retest_packet.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_R66_o3_f4_b7_zero_credit_ledger_retest_gate_v0.json"
        ),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(
            "research/B1_B7_cone01_R66_o3_f4_b7_zero_credit_ledger_retest_gate.md"
        ),
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    write_json(args.json_output, payload)
    write_markdown(args.markdown_output, payload)
    if args.pretty:
        s = payload["summary"]
        print(
            json.dumps(
                {
                    "status": payload["status"],
                    "requirements_passed": s["requirements_passed"],
                    "requirements_failed": s["requirements_failed"],
                    "retest_row_count": s["retest_row_count"],
                    "machine_checked_row_count": s["machine_checked_row_count"],
                    "ledger_credit_admissible_row_count": s[
                        "ledger_credit_admissible_row_count"
                    ],
                    "ledger_retest_boundary_complete": s[
                        "ledger_retest_boundary_complete"
                    ],
                    "b7_credit_delta": s["b7_credit_delta"],
                    "r66_retest_packet_hash": s["r66_retest_packet_hash"],
                    "json_output": str(args.json_output),
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
