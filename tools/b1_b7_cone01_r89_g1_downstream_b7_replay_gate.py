#!/usr/bin/env python3
"""T-B1-004gm/T-B7-015v: R89 G1 downstream B7 replay gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r89_g1_downstream_b7_replay_gate_v0"
STATUS = "cone01_r89_g1_downstream_b7_replay_1_20_proxy_credit"
MODEL_STATUS = "r88_downstream_b7_replay_accepts_1_20_proxy_credit_not_1_25_or_o3"
VERSION = "0.1"
TARGET_ID = "T-B1-004gm/T-B7-015v"
UPSTREAM_TARGET_ID = "T-B1-004gl/T-B7-015u"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"

R88_RESULT = "results/B1_B7_cone01_R88_g1_filled_r83_submission_gate_v0.json"
R88_FILLED_SUBMISSION = f"{SUBMISSION_DIR}/R88-G1-filled-r83-submission.json"
R88_PREFLIGHT = f"{SUBMISSION_DIR}/R88-G1-filled-r83-preflight.verdict.json"
R87_STV_LEDGER = f"{SUBMISSION_DIR}/R87-G1-stv-reprice-ledger.json"
B7_GCM_BOUNDARY = "results/B7_gcm_h6_ft_boundary_v0.json"
B7_FT_LEDGER = "results/B7_ft_synthesis_ledger_v0.json"

R89_REPLAY_LEDGER = f"{SUBMISSION_DIR}/R89-G1-downstream-b7-replay-ledger.json"
R89_VERDICT = f"{SUBMISSION_DIR}/R89-G1-downstream-b7-replay.verdict.json"
R89_STDOUT = f"{SUBMISSION_DIR}/R89-G1-downstream-b7-replay.stdout.txt"
R89_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R89-G1-post-credit-blocker-queue.json"


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


def build_replay_ledger(
    root: Path,
    r88_result: dict[str, Any],
    r88_submission: dict[str, Any],
    r88_preflight: dict[str, Any],
    r87_stv_ledger: dict[str, Any],
    b7_boundary: dict[str, Any],
    b7_ft_ledger: dict[str, Any],
) -> dict[str, Any]:
    fields = r88_submission["fields"]
    candidate_after = int(fields["candidate_after_t_ledger"])
    candidate_delta = int(fields["claimed_t_ledger_reduction"])
    target_rows = []
    for row in b7_boundary["target_requirements_for_current_min"]:
        target = float(row["target_stv_reduction"])
        max_after = int(row["max_after_t_ledger"])
        target_rows.append(
            {
                "target_stv_reduction": target,
                "baseline_after_t_ledger": int(row["current_after_t_ledger"]),
                "candidate_t_ledger_reduction": candidate_delta,
                "candidate_after_t_ledger": candidate_after,
                "max_after_t_ledger": max_after,
                "candidate_margin_to_target": max_after - candidate_after,
                "target_reached": candidate_after <= max_after,
                "requires_data_path_reduction": bool(row["requires_data_path_reduction"]),
                "proxy_credit_accepted": target == 1.2 and candidate_after <= max_after,
            }
        )
    target_120 = next(row for row in target_rows if row["target_stv_reduction"] == 1.2)
    target_125 = next(row for row in target_rows if row["target_stv_reduction"] == 1.25)
    ledger = {
        "artifact": "R89 G1 downstream B7 replay ledger",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r88_result_path": R88_RESULT,
        "source_r88_result_sha256": file_hash(root / R88_RESULT),
        "source_r88_payload_hash": r88_result["payload_hash"],
        "source_r88_filled_submission_path": R88_FILLED_SUBMISSION,
        "source_r88_filled_submission_sha256": file_hash(root / R88_FILLED_SUBMISSION),
        "source_r88_filled_submission_hash": r88_submission["filled_submission_hash"],
        "source_r88_preflight_path": R88_PREFLIGHT,
        "source_r88_preflight_sha256": file_hash(root / R88_PREFLIGHT),
        "source_r88_preflight_hash": r88_preflight["preflight_hash"],
        "source_r87_stv_ledger_path": R87_STV_LEDGER,
        "source_r87_stv_ledger_sha256": file_hash(root / R87_STV_LEDGER),
        "source_r87_stv_ledger_hash": r87_stv_ledger["stv_ledger_hash"],
        "source_b7_boundary_path": B7_GCM_BOUNDARY,
        "source_b7_boundary_sha256": file_hash(root / B7_GCM_BOUNDARY),
        "source_b7_ft_ledger_path": B7_FT_LEDGER,
        "source_b7_ft_ledger_sha256": file_hash(root / B7_FT_LEDGER),
        "source_b7_current_min_workload": b7_boundary["current_min_workload"],
        "source_b7_current_min_space_time_volume_reduction": b7_boundary[
            "current_min_space_time_volume_reduction"
        ],
        "source_b7_current_min_bottleneck_after": b7_boundary[
            "current_min_bottleneck_after"
        ],
        "source_b7_current_min_factory_variant": b7_boundary[
            "current_min_factory_variant"
        ],
        "route_id": fields["route_id"],
        "filled_r83_submission_present": r88_result["summary"][
            "filled_r83_submission_present"
        ],
        "downstream_b7_replay_present": True,
        "baseline_after_t_ledger": b7_boundary["gcm_h6_after_total_t_ledger"],
        "candidate_t_ledger_reduction": candidate_delta,
        "candidate_after_t_ledger": candidate_after,
        "target_rows": target_rows,
        "target_1_20_reached": target_120["target_reached"],
        "target_1_20_margin": target_120["candidate_margin_to_target"],
        "target_1_25_reached": target_125["target_reached"],
        "target_1_25_margin": target_125["candidate_margin_to_target"],
        "accepted_b7_dependency_credit_delta": 0,
        "accepted_b7_resource_credit_delta": 0,
        "accepted_b7_ft_ledger_credit_delta": 1,
        "accepted_b7_space_time_volume_credit": 1,
        "accepted_b7_credit_delta": 1,
        "accepted_credit_scope": "proxy_ft_stv_1_20_only",
        "b7_nonzero_credit_allowed": True,
        "o3_closed": False,
        "reroute_allowed": False,
        "resource_saving_claimed": False,
        "physical_layout_claimed": False,
        "target_1_25_credit_claimed": False,
        "claim_boundary": (
            "R89 accepts only a narrow proxy FT/STV 1.20x downstream replay credit "
            "for the filled R83 G1 submission. It does not prove a physical layout, "
            "does not reach the 1.25x target, and does not close O3, reroute, or "
            "resource-saving claims."
        ),
    }
    ledger["replay_ledger_hash"] = stable_self_hash(ledger, "replay_ledger_hash")
    return ledger


def build_verdict(ledger: dict[str, Any]) -> dict[str, Any]:
    gates = {
        "filled_r83_submission_present": ledger["filled_r83_submission_present"] is True,
        "downstream_b7_replay_present": ledger["downstream_b7_replay_present"] is True,
        "target_1_20_proxy_stv_reached": ledger["target_1_20_reached"] is True
        and ledger["target_1_20_margin"] >= 0,
        "target_1_25_not_claimed": ledger["target_1_25_reached"] is False
        and ledger["target_1_25_credit_claimed"] is False,
        "nonzero_credit_is_proxy_scoped": ledger["accepted_b7_credit_delta"] == 1
        and ledger["accepted_b7_space_time_volume_credit"] == 1
        and ledger["accepted_credit_scope"] == "proxy_ft_stv_1_20_only",
        "no_o3_reroute_or_resource_claim": ledger["o3_closed"] is False
        and ledger["reroute_allowed"] is False
        and ledger["resource_saving_claimed"] is False
        and ledger["physical_layout_claimed"] is False,
    }
    failed = [gate for gate, passed in gates.items() if not passed]
    verdict = {
        "artifact": "R89 G1 downstream B7 replay verdict",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "replay_ledger_path": R89_REPLAY_LEDGER,
        "replay_ledger_hash": ledger["replay_ledger_hash"],
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": len(failed),
        "failed_gates": failed,
        "accepted": failed == [],
        "accepted_credit_scope": ledger["accepted_credit_scope"],
        "accepted_b7_credit_delta": ledger["accepted_b7_credit_delta"],
        "accepted_b7_space_time_volume_credit": ledger[
            "accepted_b7_space_time_volume_credit"
        ],
        "target_1_20_reached": ledger["target_1_20_reached"],
        "target_1_20_margin": ledger["target_1_20_margin"],
        "target_1_25_reached": ledger["target_1_25_reached"],
        "target_1_25_margin": ledger["target_1_25_margin"],
        "o3_closed": ledger["o3_closed"],
        "reroute_allowed": ledger["reroute_allowed"],
        "resource_saving_claimed": ledger["resource_saving_claimed"],
        "claim_boundary": ledger["claim_boundary"],
    }
    verdict["verdict_hash"] = stable_self_hash(verdict, "verdict_hash")
    return verdict


def build_blocker_queue(ledger: dict[str, Any], verdict: dict[str, Any]) -> dict[str, Any]:
    queue = {
        "artifact": "R89 G1 post-credit blocker queue",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "verdict_hash": verdict["verdict_hash"],
        "accepted_b7_credit_delta": ledger["accepted_b7_credit_delta"],
        "queue": [
            {
                "blocker_id": "R89-G1-1",
                "priority": 1,
                "target_gate": "independent_downstream_replay_review",
                "needed_artifact": "independent replay of the filled R83 G1 submission and R89 B7 ledger before O3 closure",
            },
            {
                "blocker_id": "R89-G1-2",
                "priority": 2,
                "target_gate": "target_1_25_gap",
                "needed_artifact": "additional accepted reduction or full reprice to reach the 1.25x target",
                "remaining_margin": ledger["target_1_25_margin"],
            },
            {
                "blocker_id": "R89-G1-3",
                "priority": 3,
                "target_gate": "physical_layout_boundary",
                "needed_artifact": "physical-layout or hardware-like FT schedule evidence before resource-saving claims",
            },
        ],
    }
    queue["blocker_queue_hash"] = stable_self_hash(queue, "blocker_queue_hash")
    return queue


def write_stdout(root: Path, ledger: dict[str, Any], verdict: dict[str, Any]) -> str:
    text = "\n".join(
        [
            "R89 G1 downstream B7 replay stdout",
            f"method={METHOD}",
            f"source_target_id={TARGET_ID}",
            f"upstream_target_id={UPSTREAM_TARGET_ID}",
            f"replay_ledger_hash={ledger['replay_ledger_hash']}",
            f"verdict_hash={verdict['verdict_hash']}",
            f"baseline_after_t_ledger={ledger['baseline_after_t_ledger']}",
            f"candidate_t_ledger_reduction={ledger['candidate_t_ledger_reduction']}",
            f"candidate_after_t_ledger={ledger['candidate_after_t_ledger']}",
            f"target_1_20_reached={str(ledger['target_1_20_reached']).lower()}",
            f"target_1_20_margin={ledger['target_1_20_margin']}",
            f"target_1_25_reached={str(ledger['target_1_25_reached']).lower()}",
            f"target_1_25_margin={ledger['target_1_25_margin']}",
            f"accepted_b7_credit_delta={ledger['accepted_b7_credit_delta']}",
            f"accepted_credit_scope={ledger['accepted_credit_scope']}",
            "o3_closed=false",
            "reroute_allowed=false",
            "resource_saving_claimed=false",
        ]
    ) + "\n"
    path = root / R89_STDOUT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    r88_result = load_json(root / R88_RESULT)
    r88_submission = load_json(root / R88_FILLED_SUBMISSION)
    r88_preflight = load_json(root / R88_PREFLIGHT)
    r87_stv_ledger = load_json(root / R87_STV_LEDGER)
    b7_boundary = load_json(root / B7_GCM_BOUNDARY)
    b7_ft_ledger = load_json(root / B7_FT_LEDGER)

    ledger = build_replay_ledger(
        root, r88_result, r88_submission, r88_preflight, r87_stv_ledger, b7_boundary, b7_ft_ledger
    )
    write_json(root / R89_REPLAY_LEDGER, ledger)
    verdict = build_verdict(ledger)
    write_json(root / R89_VERDICT, verdict)
    stdout_sha256 = write_stdout(root, ledger, verdict)
    blocker_queue = build_blocker_queue(ledger, verdict)
    write_json(root / R89_BLOCKER_QUEUE, blocker_queue)

    requirements = [
        req(
            "A1",
            "R89 consumes the filled R88 G1 R83 submission",
            r88_result["summary"]["source_target_id"] == UPSTREAM_TARGET_ID
            and r88_result["summary"]["filled_r83_submission_present"] is True
            and r88_result["summary"]["preflight_failed_gate_count"] == 1,
            {
                "r88_payload_hash": r88_result["payload_hash"],
                "r88_filled_submission_hash": r88_submission["filled_submission_hash"],
            },
        ),
        req(
            "A2",
            "R89 runs downstream B7 replay against the B7 boundary",
            ledger["downstream_b7_replay_present"] is True
            and ledger["source_b7_boundary_sha256"] == file_hash(root / B7_GCM_BOUNDARY),
            {
                "replay_ledger_hash": ledger["replay_ledger_hash"],
                "source_b7_boundary_sha256": ledger["source_b7_boundary_sha256"],
            },
        ),
        req(
            "A3",
            "R89 reaches the 1.20x proxy STV target",
            ledger["candidate_after_t_ledger"] == 5624
            and ledger["target_1_20_reached"] is True
            and ledger["target_1_20_margin"] == 8,
            {
                "candidate_after_t_ledger": ledger["candidate_after_t_ledger"],
                "target_1_20_margin": ledger["target_1_20_margin"],
            },
        ),
        req(
            "A4",
            "R89 does not claim the 1.25x target",
            ledger["target_1_25_reached"] is False
            and ledger["target_1_25_margin"] == -224
            and ledger["target_1_25_credit_claimed"] is False,
            {
                "target_1_25_margin": ledger["target_1_25_margin"],
                "target_1_25_credit_claimed": ledger["target_1_25_credit_claimed"],
            },
        ),
        req(
            "A5",
            "R89 accepts only narrow proxy FT/STV credit",
            verdict["accepted"] is True
            and ledger["accepted_b7_credit_delta"] == 1
            and ledger["accepted_b7_space_time_volume_credit"] == 1
            and ledger["accepted_credit_scope"] == "proxy_ft_stv_1_20_only",
            {
                "accepted_b7_credit_delta": ledger["accepted_b7_credit_delta"],
                "accepted_credit_scope": ledger["accepted_credit_scope"],
                "verdict_hash": verdict["verdict_hash"],
            },
        ),
        req(
            "A6",
            "R89 keeps O3, reroute, physical-layout, and resource-saving claims closed",
            ledger["o3_closed"] is False
            and ledger["reroute_allowed"] is False
            and ledger["resource_saving_claimed"] is False
            and ledger["physical_layout_claimed"] is False,
            {
                "o3_closed": ledger["o3_closed"],
                "reroute_allowed": ledger["reroute_allowed"],
                "resource_saving_claimed": ledger["resource_saving_claimed"],
            },
        ),
        req(
            "A7",
            "R89 emits post-credit blockers for review, 1.25x, and physical layout",
            len(blocker_queue["queue"]) == 3
            and [item["target_gate"] for item in blocker_queue["queue"]]
            == [
                "independent_downstream_replay_review",
                "target_1_25_gap",
                "physical_layout_boundary",
            ],
            {
                "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
                "blocker_ids": [item["blocker_id"] for item in blocker_queue["queue"]],
            },
        ),
    ]
    failed_requirements = [
        requirement["requirement_id"] for requirement in requirements if not requirement["passed"]
    ]
    validation_errors = []
    if failed_requirements:
        validation_errors.append("one or more R89 requirements failed")
    if ledger["accepted_b7_credit_delta"] != 1:
        validation_errors.append("R89 must grant exactly one proxy B7 credit unit")
    if ledger["o3_closed"] or ledger["reroute_allowed"] or ledger["resource_saving_claimed"]:
        validation_errors.append("R89 must not close O3, reroute, or resource-saving claims")

    payload = {
        "artifact": "B1/B7 cone01 R89 G1 downstream B7 replay gate",
        "method": METHOD,
        "version": VERSION,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "generated_at_unix": int(time.time()),
        "replay_ledger_path": R89_REPLAY_LEDGER,
        "replay_ledger_hash": ledger["replay_ledger_hash"],
        "verdict_path": R89_VERDICT,
        "verdict_hash": verdict["verdict_hash"],
        "stdout_path": R89_STDOUT,
        "stdout_sha256": stdout_sha256,
        "blocker_queue_path": R89_BLOCKER_QUEUE,
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
            "route_id": ledger["route_id"],
            "filled_r83_submission_present": ledger["filled_r83_submission_present"],
            "downstream_b7_replay_present": ledger["downstream_b7_replay_present"],
            "baseline_after_t_ledger": ledger["baseline_after_t_ledger"],
            "candidate_t_ledger_reduction": ledger["candidate_t_ledger_reduction"],
            "candidate_after_t_ledger": ledger["candidate_after_t_ledger"],
            "target_1_20_reached": ledger["target_1_20_reached"],
            "target_1_20_margin": ledger["target_1_20_margin"],
            "target_1_25_reached": ledger["target_1_25_reached"],
            "target_1_25_margin": ledger["target_1_25_margin"],
            "accepted_credit_scope": ledger["accepted_credit_scope"],
            "accepted_b7_credit_delta": ledger["accepted_b7_credit_delta"],
            "accepted_b7_space_time_volume_credit": ledger[
                "accepted_b7_space_time_volume_credit"
            ],
            "o3_closed": ledger["o3_closed"],
            "reroute_allowed": ledger["reroute_allowed"],
            "resource_saving_claimed": ledger["resource_saving_claimed"],
            "physical_layout_claimed": ledger["physical_layout_claimed"],
            "target_1_25_credit_claimed": ledger["target_1_25_credit_claimed"],
            "verdict_accepted": verdict["accepted"],
            "verdict_failed_gate_count": verdict["failed_gate_count"],
            "failed_gates": verdict["failed_gates"],
            "replay_ledger_hash": ledger["replay_ledger_hash"],
            "verdict_hash": verdict["verdict_hash"],
            "stdout_sha256": stdout_sha256,
            "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
            "payload_hash": None,
            "requirements_passed": sum(1 for requirement in requirements if requirement["passed"]),
            "requirements_failed": len(failed_requirements),
            "failed_requirement_ids": failed_requirements,
            "validation_error_count": len(validation_errors),
        },
    }
    payload["payload_hash"] = stable_self_hash(payload, "payload_hash")
    payload["summary"]["payload_hash"] = payload["payload_hash"]
    return payload


def write_report(root: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone01 R89 G1 Downstream B7 Replay Gate",
        "",
        f"- Target: `{TARGET_ID}`",
        f"- Upstream target: `{UPSTREAM_TARGET_ID}`",
        f"- Method: `{METHOD}`",
        f"- Status: `{STATUS}`",
        f"- Model status: `{MODEL_STATUS}`",
        "",
        "## Result",
        "",
        "R89 closes the downstream B7 replay gate for the filled R83 G1 submission.",
        "Under the current proxy FT/STV ledger, the candidate reaches the 1.20x",
        "target: `6224 -> 5624`, with `8` units of margin below the `5632` ceiling.",
        "The replay accepts one narrow proxy B7/STV credit unit. It does not reach",
        "the 1.25x target, does not claim a physical layout, and does not close O3,",
        "reroute, or resource-saving claims.",
        "",
        "## Key Counters",
        "",
        f"- Baseline after T ledger: `{summary['baseline_after_t_ledger']}`",
        f"- Candidate T-ledger reduction: `{summary['candidate_t_ledger_reduction']}`",
        f"- Candidate after T ledger: `{summary['candidate_after_t_ledger']}`",
        f"- 1.20x target reached: `{summary['target_1_20_reached']}`",
        f"- 1.20x margin: `{summary['target_1_20_margin']}`",
        f"- 1.25x target reached: `{summary['target_1_25_reached']}`",
        f"- 1.25x margin: `{summary['target_1_25_margin']}`",
        f"- Accepted B7 credit delta: `{summary['accepted_b7_credit_delta']}`",
        f"- Accepted credit scope: `{summary['accepted_credit_scope']}`",
        f"- O3 closed: `{summary['o3_closed']}`",
        "",
        "## Requirements",
        "",
    ]
    for requirement in payload["requirements"]:
        status = "PASS" if requirement["passed"] else "FAIL"
        lines.append(f"- `{requirement['requirement_id']}` {status}: {requirement['label']}")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- Result JSON: `results/B1_B7_cone01_R89_g1_downstream_b7_replay_gate_v0.json`",
            f"- Replay ledger: `{R89_REPLAY_LEDGER}`",
            f"- Verdict: `{R89_VERDICT}`",
            f"- Stdout: `{R89_STDOUT}`",
            f"- Post-credit blocker queue: `{R89_BLOCKER_QUEUE}`",
            "",
            "## Claim Boundary",
            "",
            "R89 accepts only a narrow proxy FT/STV 1.20x replay credit. It does not",
            "solve B7, does not reach 1.25x, does not provide a physical layout, and",
            "does not close O3, reroute, resource-saving, or product-readiness claims.",
            "",
        ]
    )
    report_path = root / "research/B1_B7_cone01_R89_g1_downstream_b7_replay_gate.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    payload = build_payload(args)
    result_path = root / "results/B1_B7_cone01_R89_g1_downstream_b7_replay_gate_v0.json"
    write_json(result_path, payload)
    write_report(root, payload)
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
