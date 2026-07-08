#!/usr/bin/env python3
"""T-B1-004ga/T-B7-015j: R77 R76-aware hardened preflight rerun gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r77_r76_hardened_preflight_rerun_gate_v0"
STATUS = "cone01_r77_r76_source_closure_passes_positive_promotion_rejected"
MODEL_STATUS = "post_source_closure_positive_delta_promotion_remains_blocked"
VERSION = "0.1"
TARGET_ID = "T-B1-004ga/T-B7-015j"
UPSTREAM_TARGET_ID = "T-B1-004fz/T-B7-015i"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"
R72_RESULT = "results/B1_B7_cone01_R72_source_backed_delta_preflight_gate_v0.json"
R76_RESULT = "results/B1_B7_cone01_R76_line1378_no_double_counting_gate_v0.json"
R76_SUBMISSION = f"{SUBMISSION_DIR}/R76-r1-d1-d2-d3-source-closure-submission.json"
R76_INTAKE = f"{SUBMISSION_DIR}/R76-r1-d1-d2-d3-source-closure-intake.verdict.json"
R77_VERDICT = f"{SUBMISSION_DIR}/R77-r76-hardened-preflight-rerun.verdict.json"
R77_STDOUT = f"{SUBMISSION_DIR}/R77-r76-hardened-preflight-rerun.stdout.txt"
R77_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R77-post-r76-hardened-blocker-queue.json"
R77_POSITIVE_PROMOTION_CANDIDATE = (
    f"{SUBMISSION_DIR}/R77-r76-positive-promotion-candidate.json"
)


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


def path_hash_matches(root: Path, path_value: Any, hash_value: Any) -> bool:
    if not isinstance(path_value, str) or not isinstance(hash_value, str):
        return False
    path = root / path_value
    return path.exists() and file_hash(path) == hash_value


def source_packets_hash_bound(root: Path, submission: dict[str, Any]) -> dict[str, Any]:
    packet_results: dict[str, Any] = {}
    all_ok = True
    for packet_id, packet in submission.get("packets", {}).items():
        checks = []
        for key, value in packet.items():
            if not key.endswith("_sha256"):
                continue
            path_key = key[: -len("_sha256")] + "_path"
            ok = path_hash_matches(root, packet.get(path_key), value)
            checks.append(
                {
                    "sha256_field": key,
                    "path_field": path_key,
                    "path": packet.get(path_key),
                    "matches": ok,
                }
            )
            all_ok = all_ok and ok
        packet_results[packet_id] = {
            "hash_check_count": len(checks),
            "hash_checks": checks,
            "all_hashes_match": all(check["matches"] for check in checks),
        }
    return {"all_hash_bound_artifacts_exist": all_ok, "packet_results": packet_results}


def build_positive_promotion_candidate(
    root: Path,
    r76_summary: dict[str, Any],
    r76_submission: dict[str, Any],
    hash_bound: dict[str, Any],
) -> dict[str, Any]:
    candidate = {
        "artifact": "R77 R76-aware positive promotion candidate",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "candidate_id": "B1-B7-cone01-R77-r76-positive-promotion-candidate",
        "source_r76_result_path": R76_RESULT,
        "source_r76_result_sha256": file_hash(root / R76_RESULT),
        "source_r76_submission_path": R76_SUBMISSION,
        "source_r76_submission_sha256": file_hash(root / R76_SUBMISSION),
        "source_r76_intake_path": R76_INTAKE,
        "source_r76_intake_sha256": file_hash(root / R76_INTAKE),
        "r73_d1_prefilled": r76_summary["r73_d1_prefilled"],
        "r73_d2_prefilled": r76_summary["r73_d2_prefilled"],
        "r73_d3_prefilled": r76_summary["r73_d3_prefilled"],
        "r73_intake_accepted": r76_summary["r73_intake_accepted"],
        "r73_source_closure_hash_bound": hash_bound["all_hash_bound_artifacts_exist"],
        "requested_accepted_exit_route_count": 1,
        "requested_accepted_occurrence_removal": 1,
        "requested_accepted_proxy_t_reduction": 1,
        "requested_b7_nonzero_retest": True,
        "observed_accepted_exit_route_count": r76_summary["accepted_exit_route_count"],
        "observed_accepted_occurrence_removal": r76_summary["accepted_occurrence_removal"],
        "observed_accepted_proxy_t_reduction": r76_summary["accepted_proxy_t_reduction"],
        "observed_b7_credit_delta": r76_summary["b7_credit_delta"],
        "packets": r76_submission["packets"],
        "promotion_status": "rejected_before_b7_retest",
        "claim_boundary": (
            "R77 consumes the R76 source-closure packet and asks whether it can be "
            "promoted into a positive accepted route. It cannot: source closure is "
            "now accepted, but accepted exit-route, occurrence, proxy-T, and B7 "
            "credit counters remain zero."
        ),
    }
    candidate["candidate_hash"] = stable_self_hash(candidate, "candidate_hash")
    return candidate


def build_hardened_verdict(
    root: Path,
    r72: dict[str, Any],
    r76: dict[str, Any],
    r76_submission: dict[str, Any],
    r76_intake: dict[str, Any],
    candidate: dict[str, Any],
    hash_bound: dict[str, Any],
) -> dict[str, Any]:
    r72_summary = r72["summary"]
    r76_summary = r76["summary"]
    source_closure_gates = {
        "r76_result_requirements_pass": r76_summary["requirements_failed"] == 0,
        "r76_r73_intake_accepted": r76_summary["r73_intake_accepted"] is True
        and r76_intake["accepted"] is True,
        "r76_r73_d1_d2_d3_prefilled": all(
            r76_summary[key] is True
            for key in ["r73_d1_prefilled", "r73_d2_prefilled", "r73_d3_prefilled"]
        ),
        "r76_intake_failed_gate_count_zero": r76_intake["failed_gate_count"] == 0,
        "r76_hash_bound_artifacts_exist": hash_bound["all_hash_bound_artifacts_exist"] is True,
    }
    promotion_gates = {
        "accepted_exit_route_positive": r76_summary["accepted_exit_route_count"] >= 1,
        "accepted_occurrence_positive": r76_summary["accepted_occurrence_removal"] >= 1,
        "accepted_proxy_t_positive": r76_summary["accepted_proxy_t_reduction"] >= 1,
    }
    boundary_gates = {
        "b7_credit_still_zero": r76_summary["b7_credit_delta"] == 0,
        "b7_nonzero_retest_not_allowed": r76_summary["b7_nonzero_retest_allowed"] is False,
        "o3_not_closed": r76_summary["o3_closed"] is False,
        "reroute_not_allowed": r76_summary["reroute_allowed"] is False,
        "resource_saving_not_claimed": r76_summary["resource_saving_claimed"] is False,
    }
    failed_promotion_gates = [
        gate for gate, passed in promotion_gates.items() if not passed
    ]
    gates = {**source_closure_gates, **promotion_gates, **boundary_gates}
    failed = [gate for gate, passed in gates.items() if not passed]
    verdict = {
        "artifact": "R77 R76-aware hardened preflight rerun verdict",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "candidate_hash": candidate["candidate_hash"],
        "source_closure_passed": all(source_closure_gates.values()),
        "positive_promotion_passed": all(promotion_gates.values()),
        "hardened_accepted": failed_promotion_gates == [],
        "expected_rejection": failed_promotion_gates != [],
        "gates": gates,
        "source_closure_gates": source_closure_gates,
        "positive_promotion_gates": promotion_gates,
        "boundary_gates": boundary_gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": len(failed),
        "failed_gates": failed,
        "failed_promotion_gate_count": len(failed_promotion_gates),
        "failed_promotion_gates": failed_promotion_gates,
        "r72_hardened_failed_gate_count": r72_summary["hardened_failed_gate_count"],
        "r72_hardened_failed_gates": r72_summary["hardened_failed_gates"],
        "r77_source_closure_axis_status": "passed_via_r76_r73_intake",
        "legacy_r1_r2_packet_reports_still_open": True,
        "legacy_r1_r2_note": (
            "R77 does not mutate the historical R1/R2 packet reports. It consumes "
            "the later R73/R76 source-closure path, then reruns the promotion logic "
            "with source closure satisfied."
        ),
        "accepted_exit_route_count": r76_summary["accepted_exit_route_count"],
        "accepted_occurrence_removal": r76_summary["accepted_occurrence_removal"],
        "accepted_proxy_t_reduction": r76_summary["accepted_proxy_t_reduction"],
        "b7_credit_delta": r76_summary["b7_credit_delta"],
        "b7_nonzero_retest_allowed": r76_summary["b7_nonzero_retest_allowed"],
        "claim_boundary": candidate["claim_boundary"],
    }
    verdict["verdict_hash"] = stable_self_hash(verdict, "verdict_hash")
    return verdict


def build_blocker_queue(verdict: dict[str, Any]) -> dict[str, Any]:
    queue = {
        "artifact": "R77 post-R76 hardened blocker queue",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_closure_passed": verdict["source_closure_passed"],
        "positive_promotion_passed": verdict["positive_promotion_passed"],
        "failed_promotion_gates": verdict["failed_promotion_gates"],
        "queue": [
            {
                "blocker_id": "R77-P1",
                "priority": 1,
                "failed_gate": "accepted_exit_route_positive",
                "needed_artifact": (
                    "accepted positive route packet that promotes the R76 source-closure "
                    "evidence into at least one accepted exit route"
                ),
            },
            {
                "blocker_id": "R77-P2",
                "priority": 2,
                "failed_gate": "accepted_occurrence_positive",
                "needed_artifact": (
                    "source-backed occurrence-removal acceptance artifact with the "
                    "R76 no-double-counting exclusion preserved"
                ),
            },
            {
                "blocker_id": "R77-P3",
                "priority": 3,
                "failed_gate": "accepted_proxy_t_positive",
                "needed_artifact": (
                    "proxy-T acceptance artifact proving a counted reduction rather "
                    "than a prefill-only pricing delta"
                ),
            },
        ],
        "b7_next_gate": (
            "Only after R77-P1/P2/P3 pass should any nonzero B7 retest or FT ledger "
            "credit be attempted."
        ),
    }
    queue["blocker_queue_hash"] = stable_self_hash(queue, "blocker_queue_hash")
    return queue


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    r72 = load_json(root / R72_RESULT)
    r76 = load_json(root / R76_RESULT)
    r76_submission = load_json(root / R76_SUBMISSION)
    r76_intake = load_json(root / R76_INTAKE)
    r76_summary = r76["summary"]
    hash_bound = source_packets_hash_bound(root, r76_submission)
    candidate = build_positive_promotion_candidate(
        root, r76_summary, r76_submission, hash_bound
    )
    write_json(root / R77_POSITIVE_PROMOTION_CANDIDATE, candidate)

    verdict = build_hardened_verdict(
        root, r72, r76, r76_submission, r76_intake, candidate, hash_bound
    )
    write_json(root / R77_VERDICT, verdict)

    blocker_queue = build_blocker_queue(verdict)
    write_json(root / R77_BLOCKER_QUEUE, blocker_queue)

    stdout_payload = {
        "artifact": "R77 R76-aware hardened preflight rerun stdout",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "source_closure_passed": verdict["source_closure_passed"],
        "positive_promotion_passed": verdict["positive_promotion_passed"],
        "failed_promotion_gates": verdict["failed_promotion_gates"],
        "accepted_exit_route_count": verdict["accepted_exit_route_count"],
        "accepted_occurrence_removal": verdict["accepted_occurrence_removal"],
        "accepted_proxy_t_reduction": verdict["accepted_proxy_t_reduction"],
        "b7_credit_delta": verdict["b7_credit_delta"],
    }
    (root / R77_STDOUT).write_text(
        json.dumps(stdout_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    requirements = [
        req(
            "H1",
            "R77 consumes the R72 hardened-preflight baseline",
            r72["summary"]["hardened_accepted"] is False
            and r72["summary"]["base_r71_accepted"] is True,
            {
                "r72_result_path": R72_RESULT,
                "r72_result_sha256": file_hash(root / R72_RESULT),
                "r72_hardened_failed_gate_count": r72["summary"][
                    "hardened_failed_gate_count"
                ],
            },
        ),
        req(
            "H2",
            "R77 consumes the R76 source-closure result",
            r76_summary["requirements_failed"] == 0,
            {
                "r76_result_path": R76_RESULT,
                "r76_result_sha256": file_hash(root / R76_RESULT),
                "r76_requirements_passed": r76_summary["requirements_passed"],
                "r76_requirements_failed": r76_summary["requirements_failed"],
            },
        ),
        req(
            "H3",
            "R73 D1/D2/D3 source closure is accepted after R76",
            verdict["source_closure_passed"] is True,
            {
                "r76_intake_path": R76_INTAKE,
                "r76_intake_sha256": file_hash(root / R76_INTAKE),
                "r76_intake_accepted": r76_intake["accepted"],
                "source_closure_gates": verdict["source_closure_gates"],
            },
        ),
        req(
            "H4",
            "R77 rejects positive promotion after source closure",
            verdict["positive_promotion_passed"] is False
            and verdict["failed_promotion_gate_count"] == 3,
            {
                "failed_promotion_gates": verdict["failed_promotion_gates"],
                "positive_promotion_gates": verdict["positive_promotion_gates"],
            },
        ),
        req(
            "H5",
            "Accepted counters remain zero",
            verdict["accepted_exit_route_count"] == 0
            and verdict["accepted_occurrence_removal"] == 0
            and verdict["accepted_proxy_t_reduction"] == 0,
            {
                "accepted_exit_route_count": verdict["accepted_exit_route_count"],
                "accepted_occurrence_removal": verdict["accepted_occurrence_removal"],
                "accepted_proxy_t_reduction": verdict["accepted_proxy_t_reduction"],
            },
        ),
        req(
            "H6",
            "B7 retest and credit remain blocked",
            verdict["b7_credit_delta"] == 0
            and verdict["b7_nonzero_retest_allowed"] is False,
            {
                "b7_credit_delta": verdict["b7_credit_delta"],
                "b7_nonzero_retest_allowed": verdict["b7_nonzero_retest_allowed"],
            },
        ),
        req(
            "H7",
            "R77 emits a post-source-closure blocker queue",
            blocker_queue["source_closure_passed"] is True
            and len(blocker_queue["queue"]) == 3,
            {
                "blocker_queue_path": R77_BLOCKER_QUEUE,
                "blocker_queue_sha256": file_hash(root / R77_BLOCKER_QUEUE),
                "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
            },
        ),
        req(
            "H8",
            "R77 preserves the no-overclaim boundary",
            verdict["o3_not_closed"] is True
            if "o3_not_closed" in verdict
            else verdict["boundary_gates"]["o3_not_closed"] is True,
            {
                "boundary_gates": verdict["boundary_gates"],
                "claim_boundary": verdict["claim_boundary"],
            },
        ),
    ]
    failed_requirements = [
        requirement["requirement_id"]
        for requirement in requirements
        if not requirement["passed"]
    ]
    validation_errors = []
    if verdict["hardened_accepted"]:
        validation_errors.append("R77 must not accept positive promotion while counters are zero")
    if verdict["source_closure_passed"] is not True:
        validation_errors.append("R77 requires R76 source closure to pass before rerun")
    if verdict["b7_credit_delta"] != 0:
        validation_errors.append("R77 must preserve zero B7 credit")

    payload = {
        "artifact": "B1/B7 cone01 R77 R76-aware hardened preflight rerun gate",
        "method": METHOD,
        "version": VERSION,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "generated_at_unix": int(time.time()),
        "sources": {
            "r72_result": R72_RESULT,
            "r76_result": R76_RESULT,
            "r76_submission": R76_SUBMISSION,
            "r76_intake": R76_INTAKE,
        },
        "positive_promotion_candidate_path": R77_POSITIVE_PROMOTION_CANDIDATE,
        "positive_promotion_candidate_hash": candidate["candidate_hash"],
        "verdict_path": R77_VERDICT,
        "verdict_hash": verdict["verdict_hash"],
        "stdout_path": R77_STDOUT,
        "stdout_sha256": file_hash(root / R77_STDOUT),
        "blocker_queue_path": R77_BLOCKER_QUEUE,
        "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
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
            "r76_source_closure_passed": verdict["source_closure_passed"],
            "r73_intake_accepted": r76_summary["r73_intake_accepted"],
            "r73_d1_prefilled": r76_summary["r73_d1_prefilled"],
            "r73_d2_prefilled": r76_summary["r73_d2_prefilled"],
            "r73_d3_prefilled": r76_summary["r73_d3_prefilled"],
            "hardened_accepted": verdict["hardened_accepted"],
            "positive_promotion_passed": verdict["positive_promotion_passed"],
            "hardened_failed_gate_count": verdict["failed_promotion_gate_count"],
            "hardened_failed_gates": verdict["failed_promotion_gates"],
            "accepted_exit_route_count": verdict["accepted_exit_route_count"],
            "accepted_occurrence_removal": verdict["accepted_occurrence_removal"],
            "accepted_proxy_t_reduction": verdict["accepted_proxy_t_reduction"],
            "b7_credit_delta": verdict["b7_credit_delta"],
            "b7_nonzero_retest_allowed": verdict["b7_nonzero_retest_allowed"],
            "o3_closed": False,
            "reroute_allowed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
            "verdict_hash": verdict["verdict_hash"],
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
    report_path = root / "research/B1_B7_cone01_R77_r76_hardened_preflight_rerun_gate.md"
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone01 R77 R76-Aware Hardened Preflight Rerun Gate",
        "",
        f"- Target: `{TARGET_ID}`",
        f"- Upstream target: `{UPSTREAM_TARGET_ID}`",
        f"- Method: `{METHOD}`",
        f"- Status: `{STATUS}`",
        f"- Model status: `{MODEL_STATUS}`",
        "",
        "## Result",
        "",
        "R77 consumes the R76 source-closure packet and reruns the hardened",
        "promotion boundary. The R73 D1/D2/D3 source-closure axis now passes,",
        "but positive promotion remains rejected: accepted exit route, accepted",
        "occurrence removal, accepted proxy-T reduction, and B7 credit all remain",
        "zero.",
        "",
        "## Key Counters",
        "",
        f"- R76 source closure passed: `{summary['r76_source_closure_passed']}`",
        f"- Hardened accepted: `{summary['hardened_accepted']}`",
        f"- Failed promotion gates: `{summary['hardened_failed_gates']}`",
        f"- Accepted exit routes: `{summary['accepted_exit_route_count']}`",
        f"- Accepted occurrence removal: `{summary['accepted_occurrence_removal']}`",
        f"- Accepted proxy-T reduction: `{summary['accepted_proxy_t_reduction']}`",
        f"- B7 credit delta: `{summary['b7_credit_delta']}`",
        "",
        "## Requirements",
        "",
    ]
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
            f"- Result JSON: `results/B1_B7_cone01_R77_r76_hardened_preflight_rerun_gate_v0.json`",
            f"- Verdict: `{R77_VERDICT}`",
            f"- Candidate: `{R77_POSITIVE_PROMOTION_CANDIDATE}`",
            f"- Blocker queue: `{R77_BLOCKER_QUEUE}`",
            f"- Stdout: `{R77_STDOUT}`",
            "",
            "## Claim Boundary",
            "",
            "R77 is not an O3 closure, not a reroute permission, not a resource",
            "saving, and not B7 credit. It only proves that after R76 the",
            "source-closure blocker has moved into an explicit positive-promotion",
            "blocker queue.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", default="results/B1_B7_cone01_R77_r76_hardened_preflight_rerun_gate_v0.json")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.repo_root).resolve()
    payload = build_payload(args)
    write_json(root / args.output, payload)
    write_report(root, payload)
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    print(text)
    if payload["validation_error_count"] or payload["requirements_failed"]:
        raise SystemExit("B1/B7 R77 R76-aware hardened preflight rerun validation failed")


if __name__ == "__main__":
    main()
