#!/usr/bin/env python3
"""T-B1-004gf/T-B7-015o: R82 downstream B7 retest gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r82_b7_downstream_retest_gate_v0"
STATUS = "cone01_r82_downstream_b7_retest_completed_zero_credit_boundary"
MODEL_STATUS = "r81_positive_route_retested_against_b7_thresholds_credit_still_zero"
VERSION = "0.1"
TARGET_ID = "T-B1-004gf/T-B7-015o"
UPSTREAM_TARGET_ID = "T-B1-004ge/T-B7-015n"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"

R81_RESULT = "results/B1_B7_cone01_R81_positive_route_promotion_gate_v0.json"
R81_PACKET = f"{SUBMISSION_DIR}/R81-positive-route-accepted.packet.json"
R81_PREFLIGHT = f"{SUBMISSION_DIR}/R81-positive-route-accepted.verdict.json"
R81_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R81-b7-retest-blocker-queue.json"
R66_RESULT = "results/B1_B7_cone01_R66_o3_f4_b7_zero_credit_ledger_retest_gate_v0.json"
B7_FT_LEDGER = "results/B7_ft_synthesis_ledger_v0.json"
B7_GCM_BOUNDARY = "results/B7_gcm_h6_ft_boundary_v0.json"

R82_LEDGER = f"{SUBMISSION_DIR}/R82-b7-downstream-retest-ledger.json"
R82_VERDICT = f"{SUBMISSION_DIR}/R82-b7-downstream-retest.verdict.json"
R82_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R82-b7-next-blocker-queue.json"
R82_STDOUT = f"{SUBMISSION_DIR}/R82-b7-downstream-retest.stdout.txt"


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def stable_self_hash(payload: dict[str, Any], hash_key: str) -> str:
    copy = dict(payload)
    copy.pop(hash_key, None)
    return stable_hash(copy)


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


def target_gap_after_delta(
    boundary: dict[str, Any], accepted_proxy_t_reduction: int
) -> list[dict[str, Any]]:
    rows = []
    for row in boundary["target_requirements_for_current_min"]:
        before = int(row["additional_t_ledger_to_remove"])
        after = max(0, before - int(accepted_proxy_t_reduction))
        rows.append(
            {
                "target_stv_reduction": row["target_stv_reduction"],
                "additional_t_ledger_to_remove_before_r81": before,
                "candidate_r81_proxy_t_reduction": int(accepted_proxy_t_reduction),
                "additional_t_ledger_to_remove_after_r81": after,
                "target_reached": after == 0,
                "equivalent_arbitrary_rotations_remaining_at_cost_20": (after + 19) // 20,
            }
        )
    return rows


def build_retest_ledger(
    root: Path,
    r81_result: dict[str, Any],
    r81_packet: dict[str, Any],
    r81_preflight: dict[str, Any],
    r81_blocker_queue: dict[str, Any],
    r66_result: dict[str, Any],
    b7_ft_ledger: dict[str, Any],
    b7_gcm_boundary: dict[str, Any],
) -> dict[str, Any]:
    accepted_proxy_t_reduction = int(r81_packet["accepted_proxy_t_reduction"])
    gap_rows = target_gap_after_delta(b7_gcm_boundary, accepted_proxy_t_reduction)
    min_gap_after_r81 = min(row["additional_t_ledger_to_remove_after_r81"] for row in gap_rows)
    min_target_reached = any(row["target_reached"] for row in gap_rows)

    ledger = {
        "artifact": "R82 downstream B7 retest ledger",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "ledger_id": "B1-B7-cone01-R82-downstream-B7-retest-ledger",
        "source_r81_result": R81_RESULT,
        "source_r81_result_sha256": file_hash(root / R81_RESULT),
        "source_r81_payload_hash": r81_result["payload_hash"],
        "source_r81_packet": R81_PACKET,
        "source_r81_packet_sha256": file_hash(root / R81_PACKET),
        "source_r81_packet_hash": r81_packet["packet_hash"],
        "source_r81_preflight": R81_PREFLIGHT,
        "source_r81_preflight_sha256": file_hash(root / R81_PREFLIGHT),
        "source_r81_preflight_hash": r81_preflight["verdict_hash"],
        "source_r81_blocker_queue": R81_BLOCKER_QUEUE,
        "source_r81_blocker_queue_sha256": file_hash(root / R81_BLOCKER_QUEUE),
        "source_r81_blocker_queue_hash": r81_blocker_queue["blocker_queue_hash"],
        "source_r66_zero_credit_boundary": R66_RESULT,
        "source_r66_zero_credit_boundary_sha256": file_hash(root / R66_RESULT),
        "source_r66_retest_packet_hash": r66_result["summary"]["r66_retest_packet_hash"],
        "source_b7_ft_ledger": B7_FT_LEDGER,
        "source_b7_ft_ledger_sha256": file_hash(root / B7_FT_LEDGER),
        "source_b7_min_space_time_volume_reduction": b7_ft_ledger[
            "min_space_time_volume_reduction"
        ],
        "source_b7_mean_space_time_volume_reduction": b7_ft_ledger[
            "mean_space_time_volume_reduction"
        ],
        "source_b7_current_min_row": b7_ft_ledger["min_row"],
        "source_b7_gcm_boundary": B7_GCM_BOUNDARY,
        "source_b7_gcm_boundary_sha256": file_hash(root / B7_GCM_BOUNDARY),
        "source_b7_current_after_t_ledger": b7_gcm_boundary["gcm_h6_after_total_t_ledger"],
        "source_b7_current_arbitrary_rotation_count": b7_gcm_boundary[
            "gcm_h6_after_arbitrary_numeric_rotation_count"
        ],
        "source_b7_target_gap_rows": gap_rows,
        "accepted_exit_route_count": int(r81_packet["accepted_exit_route_count"]),
        "accepted_occurrence_removal": int(r81_packet["accepted_occurrence_removal"]),
        "accepted_proxy_t_reduction": accepted_proxy_t_reduction,
        "candidate_logical_t_count_delta": accepted_proxy_t_reduction,
        "candidate_logical_t_depth_delta": 0,
        "candidate_space_time_volume_delta": 0,
        "accepted_b7_dependency_credit_delta": 0,
        "accepted_b7_resource_credit_delta": 0,
        "accepted_b7_ft_ledger_credit_delta": 0,
        "accepted_b7_space_time_volume_credit": 0,
        "accepted_b7_credit_delta": 0,
        "b7_downstream_retest_completed": True,
        "b7_nonzero_credit_allowed": False,
        "min_t_ledger_gap_after_r81": min_gap_after_r81,
        "minimum_target_reached": min_target_reached,
        "o3_closed": False,
        "reroute_allowed": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "claim_boundary": (
            "R82 consumes the R81 accepted B1 route as a downstream B7 retest input. "
            "The one-unit proxy-T delta is too small to satisfy the current gcm_h6 "
            "B7 target gaps, so no dependency, resource, FT-ledger, STV, O3, reroute, "
            "or B7 credit is granted."
        ),
    }
    ledger["ledger_hash"] = stable_self_hash(ledger, "ledger_hash")
    return ledger


def build_verdict(ledger: dict[str, Any]) -> dict[str, Any]:
    gates = {
        "r81_positive_packet_accepted": ledger["accepted_exit_route_count"] == 1
        and ledger["accepted_occurrence_removal"] == 1
        and ledger["accepted_proxy_t_reduction"] == 1,
        "b7_retest_consumed_r81_packet": ledger["b7_downstream_retest_completed"] is True,
        "candidate_logical_t_delta_bound": ledger["candidate_logical_t_count_delta"] == 1,
        "b7_threshold_gap_remains_positive": ledger["min_t_ledger_gap_after_r81"] > 0,
        "no_b7_credit_granted": ledger["accepted_b7_credit_delta"] == 0
        and ledger["accepted_b7_space_time_volume_credit"] == 0,
        "no_overclaim_flags": ledger["o3_closed"] is False
        and ledger["reroute_allowed"] is False
        and ledger["resource_saving_claimed"] is False
        and ledger["b7_ledger_improvement_claimed"] is False,
    }
    failed = [gate for gate, passed in gates.items() if not passed]
    verdict = {
        "artifact": "R82 downstream B7 retest verdict",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "ledger_path": R82_LEDGER,
        "ledger_hash": ledger["ledger_hash"],
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": len(failed),
        "failed_gates": failed,
        "accepted": failed == [],
        "b7_downstream_retest_completed": ledger["b7_downstream_retest_completed"],
        "candidate_logical_t_count_delta": ledger["candidate_logical_t_count_delta"],
        "min_t_ledger_gap_after_r81": ledger["min_t_ledger_gap_after_r81"],
        "accepted_b7_credit_delta": ledger["accepted_b7_credit_delta"],
        "accepted_b7_space_time_volume_credit": ledger["accepted_b7_space_time_volume_credit"],
        "claim_boundary": ledger["claim_boundary"],
    }
    verdict["verdict_hash"] = stable_self_hash(verdict, "verdict_hash")
    return verdict


def build_blocker_queue(ledger: dict[str, Any], verdict: dict[str, Any]) -> dict[str, Any]:
    target_120 = next(
        row
        for row in ledger["source_b7_target_gap_rows"]
        if float(row["target_stv_reduction"]) == 1.2
    )
    target_125 = next(
        row
        for row in ledger["source_b7_target_gap_rows"]
        if float(row["target_stv_reduction"]) == 1.25
    )
    queue = {
        "artifact": "R82 B7 next blocker queue",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "verdict_hash": verdict["verdict_hash"],
        "b7_downstream_retest_completed": ledger["b7_downstream_retest_completed"],
        "accepted_exit_route_count": ledger["accepted_exit_route_count"],
        "accepted_occurrence_removal": ledger["accepted_occurrence_removal"],
        "accepted_proxy_t_reduction": ledger["accepted_proxy_t_reduction"],
        "accepted_b7_credit_delta": ledger["accepted_b7_credit_delta"],
        "queue": [
            {
                "blocker_id": "R82-B7-1",
                "priority": 1,
                "target_gate": "gcm_h6_1_20x_stv_threshold",
                "needed_artifact": "remove at least 591 additional T-ledger units or provide an equivalent B7 reprice that reaches the 1.20x target",
                "remaining_t_ledger_gap_after_r81": target_120[
                    "additional_t_ledger_to_remove_after_r81"
                ],
            },
            {
                "blocker_id": "R82-B7-2",
                "priority": 2,
                "target_gate": "gcm_h6_1_25x_stv_threshold",
                "needed_artifact": "remove at least 823 additional T-ledger units or provide an equivalent B7 reprice that reaches the 1.25x target",
                "remaining_t_ledger_gap_after_r81": target_125[
                    "additional_t_ledger_to_remove_after_r81"
                ],
            },
            {
                "blocker_id": "R82-B7-3",
                "priority": 3,
                "target_gate": "claim_boundary_audit",
                "needed_artifact": "independent audit that any future B7 credit derives from a full downstream B7 ledger replay, not from B1 route acceptance alone",
            },
        ],
    }
    queue["blocker_queue_hash"] = stable_self_hash(queue, "blocker_queue_hash")
    return queue


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    r81_result = load_json(root / R81_RESULT)
    r81_packet = load_json(root / R81_PACKET)
    r81_preflight = load_json(root / R81_PREFLIGHT)
    r81_blocker_queue = load_json(root / R81_BLOCKER_QUEUE)
    r66_result = load_json(root / R66_RESULT)
    b7_ft_ledger = load_json(root / B7_FT_LEDGER)
    b7_gcm_boundary = load_json(root / B7_GCM_BOUNDARY)

    ledger = build_retest_ledger(
        root,
        r81_result,
        r81_packet,
        r81_preflight,
        r81_blocker_queue,
        r66_result,
        b7_ft_ledger,
        b7_gcm_boundary,
    )
    write_json(root / R82_LEDGER, ledger)
    verdict = build_verdict(ledger)
    write_json(root / R82_VERDICT, verdict)
    blocker_queue = build_blocker_queue(ledger, verdict)
    write_json(root / R82_BLOCKER_QUEUE, blocker_queue)
    stdout = {
        "artifact": "R82 downstream B7 retest stdout",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "verdict_accepted": verdict["accepted"],
        "accepted_exit_route_count": ledger["accepted_exit_route_count"],
        "accepted_proxy_t_reduction": ledger["accepted_proxy_t_reduction"],
        "candidate_logical_t_count_delta": ledger["candidate_logical_t_count_delta"],
        "min_t_ledger_gap_after_r81": ledger["min_t_ledger_gap_after_r81"],
        "accepted_b7_credit_delta": ledger["accepted_b7_credit_delta"],
    }
    write_json(root / R82_STDOUT, stdout)

    requirements = [
        req(
            "A1",
            "R81 accepted packet is the retest input",
            r81_preflight["accepted"] is True
            and r81_packet["accepted_exit_route_count"] == 1
            and r81_packet["accepted_occurrence_removal"] == 1
            and r81_packet["accepted_proxy_t_reduction"] == 1,
            {
                "r81_packet_path": R81_PACKET,
                "r81_packet_hash": r81_packet["packet_hash"],
                "r81_preflight_hash": r81_preflight["verdict_hash"],
            },
        ),
        req(
            "A2",
            "R81 and B7 source artifacts are hash-bound",
            ledger["source_r81_packet_sha256"] == file_hash(root / R81_PACKET)
            and ledger["source_b7_ft_ledger_sha256"] == file_hash(root / B7_FT_LEDGER)
            and ledger["source_b7_gcm_boundary_sha256"] == file_hash(root / B7_GCM_BOUNDARY),
            {
                "source_r81_packet_sha256": ledger["source_r81_packet_sha256"],
                "source_b7_ft_ledger_sha256": ledger["source_b7_ft_ledger_sha256"],
                "source_b7_gcm_boundary_sha256": ledger["source_b7_gcm_boundary_sha256"],
            },
        ),
        req(
            "A3",
            "R82 derives a candidate logical-T delta from R81 proxy-T evidence",
            ledger["candidate_logical_t_count_delta"] == ledger["accepted_proxy_t_reduction"] == 1,
            {
                "accepted_proxy_t_reduction": ledger["accepted_proxy_t_reduction"],
                "candidate_logical_t_count_delta": ledger["candidate_logical_t_count_delta"],
            },
        ),
        req(
            "A4",
            "B7 gcm_h6 target gap remains positive after R81",
            ledger["min_t_ledger_gap_after_r81"] > 0
            and all(not row["target_reached"] for row in ledger["source_b7_target_gap_rows"]),
            {
                "target_gap_rows": ledger["source_b7_target_gap_rows"],
                "min_t_ledger_gap_after_r81": ledger["min_t_ledger_gap_after_r81"],
            },
        ),
        req(
            "A5",
            "R82 grants no B7 dependency/resource/FT/STV credit",
            ledger["accepted_b7_dependency_credit_delta"] == 0
            and ledger["accepted_b7_resource_credit_delta"] == 0
            and ledger["accepted_b7_ft_ledger_credit_delta"] == 0
            and ledger["accepted_b7_space_time_volume_credit"] == 0
            and ledger["accepted_b7_credit_delta"] == 0,
            {
                "accepted_b7_credit_delta": ledger["accepted_b7_credit_delta"],
                "accepted_b7_space_time_volume_credit": ledger[
                    "accepted_b7_space_time_volume_credit"
                ],
            },
        ),
        req(
            "A6",
            "R82 completes the downstream retest without O3/reroute/resource overclaim",
            verdict["accepted"] is True
            and ledger["o3_closed"] is False
            and ledger["reroute_allowed"] is False
            and ledger["resource_saving_claimed"] is False
            and ledger["b7_ledger_improvement_claimed"] is False,
            {
                "verdict_hash": verdict["verdict_hash"],
                "failed_gates": verdict["failed_gates"],
            },
        ),
        req(
            "A7",
            "R82 emits concrete next blockers",
            len(blocker_queue["queue"]) == 3
            and blocker_queue["queue"][0]["remaining_t_ledger_gap_after_r81"] == 591
            and blocker_queue["queue"][1]["remaining_t_ledger_gap_after_r81"] == 823,
            {
                "blocker_queue_path": R82_BLOCKER_QUEUE,
                "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
            },
        ),
        req(
            "A8",
            "R82 claim boundary blocks B7 overclaim",
            all(
                token in ledger["claim_boundary"].lower()
                for token in ["too small", "no dependency", "b7 credit"]
            ),
            {"claim_boundary": ledger["claim_boundary"]},
        ),
    ]
    failed_requirements = [
        requirement["requirement_id"]
        for requirement in requirements
        if not requirement["passed"]
    ]
    validation_errors = []
    if failed_requirements:
        validation_errors.append("one or more R82 requirements failed")
    if ledger["accepted_b7_credit_delta"] != 0:
        validation_errors.append("R82 must not grant B7 credit")
    if ledger["min_t_ledger_gap_after_r81"] <= 0:
        validation_errors.append("R82 unexpectedly closes the B7 target gap")

    payload = {
        "artifact": "B1/B7 cone01 R82 downstream B7 retest gate",
        "method": METHOD,
        "version": VERSION,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "generated_at_unix": int(time.time()),
        "ledger_path": R82_LEDGER,
        "ledger_hash": ledger["ledger_hash"],
        "verdict_path": R82_VERDICT,
        "verdict_hash": verdict["verdict_hash"],
        "blocker_queue_path": R82_BLOCKER_QUEUE,
        "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
        "stdout_path": R82_STDOUT,
        "stdout_sha256": file_hash(root / R82_STDOUT),
        "requirement_count": len(requirements),
        "requirements_passed": sum(1 for requirement in requirements if requirement["passed"]),
        "requirements_failed": len(failed_requirements),
        "failed_requirement_ids": failed_requirements,
        "requirements": requirements,
        "validation_error_count": len(validation_errors),
        "validation_errors": validation_errors,
        "summary": {
            "method": METHOD,
            "status": STATUS,
            "model_status": MODEL_STATUS,
            "source_target_id": TARGET_ID,
            "upstream_target_id": UPSTREAM_TARGET_ID,
            "b7_downstream_retest_completed": ledger["b7_downstream_retest_completed"],
            "r81_preflight_accepted": r81_preflight["accepted"],
            "accepted_exit_route_count": ledger["accepted_exit_route_count"],
            "accepted_occurrence_removal": ledger["accepted_occurrence_removal"],
            "accepted_proxy_t_reduction": ledger["accepted_proxy_t_reduction"],
            "candidate_logical_t_count_delta": ledger["candidate_logical_t_count_delta"],
            "min_t_ledger_gap_after_r81": ledger["min_t_ledger_gap_after_r81"],
            "target_gap_rows": ledger["source_b7_target_gap_rows"],
            "accepted_b7_credit_delta": ledger["accepted_b7_credit_delta"],
            "accepted_b7_space_time_volume_credit": ledger[
                "accepted_b7_space_time_volume_credit"
            ],
            "b7_nonzero_credit_allowed": ledger["b7_nonzero_credit_allowed"],
            "o3_closed": ledger["o3_closed"],
            "reroute_allowed": ledger["reroute_allowed"],
            "resource_saving_claimed": ledger["resource_saving_claimed"],
            "b7_ledger_improvement_claimed": ledger["b7_ledger_improvement_claimed"],
            "ledger_hash": ledger["ledger_hash"],
            "verdict_hash": verdict["verdict_hash"],
            "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
            "payload_hash": None,
            "requirements_passed": sum(
                1 for requirement in requirements if requirement["passed"]
            ),
            "requirements_failed": len(failed_requirements),
            "failed_requirement_ids": failed_requirements,
            "validation_error_count": len(validation_errors),
        },
    }
    payload["payload_hash"] = stable_self_hash(payload, "payload_hash")
    payload["summary"]["payload_hash"] = payload["payload_hash"]
    return payload


def write_report(root: Path, payload: dict[str, Any]) -> None:
    report_path = root / "research/B1_B7_cone01_R82_b7_downstream_retest_gate.md"
    summary = payload["summary"]
    target_rows = summary["target_gap_rows"]
    lines = [
        "# B1/B7 Cone01 R82 Downstream B7 Retest Gate",
        "",
        f"- Target: `{TARGET_ID}`",
        f"- Upstream target: `{UPSTREAM_TARGET_ID}`",
        f"- Method: `{METHOD}`",
        f"- Status: `{STATUS}`",
        f"- Model status: `{MODEL_STATUS}`",
        "",
        "## Result",
        "",
        "R82 completes the downstream B7 retest requested by R81. It consumes the",
        "R81 accepted B1 positive-route packet as the input delta and compares that",
        "one-unit proxy-T reduction against the current gcm_h6 B7 FT boundary. The",
        "result is deliberately a zero-credit boundary: the retest is complete, but",
        "the B7 target gaps remain far above the R81 delta.",
        "",
        "## Key Counters",
        "",
        f"- Downstream B7 retest completed: `{summary['b7_downstream_retest_completed']}`",
        f"- Accepted exit routes from R81: `{summary['accepted_exit_route_count']}`",
        f"- Accepted occurrence removal from R81: `{summary['accepted_occurrence_removal']}`",
        f"- Accepted proxy-T reduction from R81: `{summary['accepted_proxy_t_reduction']}`",
        f"- Candidate logical-T count delta: `{summary['candidate_logical_t_count_delta']}`",
        f"- Minimum T-ledger gap after R81: `{summary['min_t_ledger_gap_after_r81']}`",
        f"- Accepted B7 credit delta: `{summary['accepted_b7_credit_delta']}`",
        f"- Accepted B7 STV credit: `{summary['accepted_b7_space_time_volume_credit']}`",
        "",
        "## B7 Target Gap",
        "",
    ]
    for row in target_rows:
        lines.append(
            "- Target `{target}`: gap `{before}` before R81, candidate R81 delta `{delta}`, "
            "gap `{after}` after R81, target reached `{reached}`.".format(
                target=row["target_stv_reduction"],
                before=row["additional_t_ledger_to_remove_before_r81"],
                delta=row["candidate_r81_proxy_t_reduction"],
                after=row["additional_t_ledger_to_remove_after_r81"],
                reached=row["target_reached"],
            )
        )
    lines.extend(
        [
            "",
            "## Requirements",
            "",
        ]
    )
    for requirement in payload["requirements"]:
        status = "PASS" if requirement["passed"] else "FAIL"
        lines.append(
            f"- `{requirement['requirement_id']}` {status}: {requirement['label']}"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- Result JSON: `results/B1_B7_cone01_R82_b7_downstream_retest_gate_v0.json`",
            f"- Retest ledger: `{R82_LEDGER}`",
            f"- Retest verdict: `{R82_VERDICT}`",
            f"- Next blocker queue: `{R82_BLOCKER_QUEUE}`",
            f"- Stdout: `{R82_STDOUT}`",
            "",
            "## Claim Boundary",
            "",
            "R82 is a completed downstream B7 retest, not a B7 win. It does not close",
            "O3, does not allow reroute, does not claim resource saving, and does not",
            "grant dependency, resource, FT-ledger, STV, or B7 credit. The next gate",
            "must remove at least 591 additional T-ledger units or provide an",
            "equivalent full B7 reprice that reaches the current 1.20x STV target.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--output",
        default="results/B1_B7_cone01_R82_b7_downstream_retest_gate_v0.json",
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.repo_root).resolve()
    payload = build_payload(args)
    write_json(root / args.output, payload)
    write_report(root, payload)
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    if payload["validation_error_count"] or payload["requirements_failed"]:
        raise SystemExit("B1/B7 R82 downstream B7 retest validation failed")


if __name__ == "__main__":
    main()
