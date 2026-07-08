#!/usr/bin/env python3
"""T-B1-004gc/T-B7-015l: R79 R78-A route/replay prefill gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r79_r78a_route_replay_prefill_gate_v0"
STATUS = "cone01_r79_r78a_route_replay_prefilled_zero_credit"
MODEL_STATUS = "route_replay_certificate_surface_filled_occurrence_proxy_t_acceptance_still_missing"
VERSION = "0.1"
TARGET_ID = "T-B1-004gc/T-B7-015l"
UPSTREAM_TARGET_ID = "T-B1-004gb/T-B7-015k"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"
R78_RESULT = "results/B1_B7_cone01_R78_positive_route_packet_contract_gate_v0.json"
R78_CONTRACT = f"{SUBMISSION_DIR}/R78-positive-route-packet.contract.json"
R78_EMPTY_PREFLIGHT = f"{SUBMISSION_DIR}/R78-positive-route-packet.current-empty-preflight.verdict.json"
R70_RESULT = "results/B1_B7_cone01_R70_machine_check_replay_prefill_gate_v0.json"
R70_PREFILL = f"{SUBMISSION_DIR}/R70-R1-line1381-prefill-machine-check-replay.json"
R76_NO_DOUBLE_COUNTING_VERDICT = f"{SUBMISSION_DIR}/R76-line1378-no-double-counting-replay.verdict.json"
R79_PACKET = f"{SUBMISSION_DIR}/R79-r78a-route-replay-prefill.packet.json"
R79_PREFLIGHT = f"{SUBMISSION_DIR}/R79-r78a-route-replay-prefill.verdict.json"
R79_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R79-r78a-route-replay-blocker-queue.json"
R79_STDOUT = f"{SUBMISSION_DIR}/R79-r78a-route-replay-prefill.stdout.txt"


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


def preflight_packet(root: Path, contract: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    missing = [
        field for field in contract["production_required_fields"] if packet.get(field) in (None, "")
    ]
    hash_failures = []
    hash_fields_seen = 0
    for field in contract["production_required_fields"]:
        if not field.endswith("_sha256"):
            continue
        path_field = field[: -len("_sha256")] + "_path"
        value = packet.get(field)
        path_value = packet.get(path_field)
        if value in (None, "") or path_value in (None, ""):
            continue
        hash_fields_seen += 1
        if not path_hash_matches(root, path_value, value):
            hash_failures.append(field)

    gates = {
        "all_required_fields_complete": missing == [],
        "all_hash_bound_artifacts_match": missing == [] and hash_failures == [],
        "source_r77_payload_hash_matches": packet.get("source_r77_payload_hash")
        == contract["source_r77_payload_hash"],
        "r76_no_double_counting_preserved": packet.get(
            "source_r76_no_double_counting_ledger_sha256"
        )
        == contract["r76_no_double_counting_ledger_sha256"],
        "accepted_exit_route_positive": packet.get("accepted_exit_route_count", 0) >= 1,
        "accepted_occurrence_positive": packet.get("accepted_occurrence_removal", 0) >= 1,
        "accepted_proxy_t_positive": packet.get("accepted_proxy_t_reduction", 0) >= 1,
        "b7_not_requested_inside_packet": packet.get("b7_nonzero_retest_requested") is False,
        "claim_boundary_blocks_b7": "b7 credit" in str(packet.get("claim_boundary", "")).lower()
        and "cannot" in str(packet.get("claim_boundary", "")).lower(),
    }
    failed = [gate for gate, passed in gates.items() if not passed]
    verdict = {
        "artifact": "R79 R78-A route/replay partial packet preflight verdict",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "contract_id": contract["contract_id"],
        "contract_hash": contract["contract_hash"],
        "packet_id": packet["packet_id"],
        "packet_hash": packet["packet_hash"],
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": len(failed),
        "failed_gates": failed,
        "missing_required_fields": missing,
        "missing_required_field_count": len(missing),
        "hash_fields_seen": hash_fields_seen,
        "hash_failures": hash_failures,
        "accepted": failed == [],
        "accepted_exit_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
        "b7_nonzero_retest_allowed": False,
        "rejection_reason": "route_replay_surface_prefilled_but_positive_acceptance_ledgers_missing",
    }
    verdict["verdict_hash"] = stable_self_hash(verdict, "verdict_hash")
    return verdict


def build_packet(root: Path, contract: dict[str, Any], r70_prefill: dict[str, Any]) -> dict[str, Any]:
    packet = {
        "packet_id": "B1-B7-cone01-R79-r78a-route-replay-prefill",
        "contract_id": contract["contract_id"],
        "contract_hash": contract["contract_hash"],
        "route_id": r70_prefill["route_id"],
        "route_class": "r78a_route_replay_certificate_prefilled_not_accepted",
        "source_r77_payload_hash": contract["source_r77_payload_hash"],
        "source_r67_contract_hash": contract["source_r67_contract_hash"],
        "source_r71_contract_hash": contract["source_r71_contract_hash"],
        "source_r76_no_double_counting_ledger_path": contract[
            "r76_no_double_counting_ledger_path"
        ],
        "source_r76_no_double_counting_ledger_sha256": contract[
            "r76_no_double_counting_ledger_sha256"
        ],
        "accepted_route_artifact_path": r70_prefill["full_circuit_rewrite_artifact_path"],
        "accepted_route_artifact_sha256": r70_prefill[
            "full_circuit_rewrite_artifact_sha256"
        ],
        "full_circuit_or_route_bounded_replay_command": r70_prefill[
            "machine_check_replay_command"
        ],
        "full_circuit_or_route_bounded_replay_stdout_path": r70_prefill[
            "machine_check_replay_stdout_path"
        ],
        "full_circuit_or_route_bounded_replay_stdout_sha256": r70_prefill[
            "machine_check_replay_stdout_sha256"
        ],
        "same_unitary_or_symbolic_certificate_path": r70_prefill[
            "semantic_or_symbolic_equivalence_certificate_path"
        ],
        "same_unitary_or_symbolic_certificate_sha256": r70_prefill[
            "semantic_or_symbolic_equivalence_certificate_sha256"
        ],
        "occurrence_acceptance_ledger_path": None,
        "occurrence_acceptance_ledger_sha256": None,
        "proxy_t_acceptance_ledger_path": None,
        "proxy_t_acceptance_ledger_sha256": None,
        "no_double_counting_preservation_verdict_path": R76_NO_DOUBLE_COUNTING_VERDICT,
        "no_double_counting_preservation_verdict_sha256": file_hash(
            root / R76_NO_DOUBLE_COUNTING_VERDICT
        ),
        "accepted_exit_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_nonzero_retest_requested": False,
        "claim_boundary": (
            "R79 prefills the R78-A route artifact, replay stdout, and "
            "same-unitary/symbolic certificate surface from R70 while preserving "
            "R76 no-double-counting. It cannot close O3, permit reroute, claim "
            "resource saving, or grant B7 credit because occurrence and proxy-T "
            "acceptance ledgers remain missing and all accepted counters stay zero."
        ),
        "source_r70_prefill_path": R70_PREFILL,
        "source_r70_prefill_sha256": file_hash(root / R70_PREFILL),
        "source_r70_prefill_hash": r70_prefill["prefill_hash"],
    }
    packet["packet_hash"] = stable_self_hash(packet, "packet_hash")
    return packet


def build_blocker_queue(preflight: dict[str, Any]) -> dict[str, Any]:
    queue = {
        "artifact": "R79 R78-A route/replay remaining blocker queue",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "current_preflight_accepted": preflight["accepted"],
        "missing_required_fields": preflight["missing_required_fields"],
        "failed_gates": preflight["failed_gates"],
        "queue": [
            {
                "blocker_id": "R79-B",
                "priority": 1,
                "target_gate": "accepted_occurrence_positive",
                "needed_artifact": "occurrence acceptance ledger with at least one counted removal",
            },
            {
                "blocker_id": "R79-C",
                "priority": 2,
                "target_gate": "accepted_proxy_t_positive",
                "needed_artifact": "proxy-T acceptance ledger proving counted reduction beyond prefill pricing",
            },
            {
                "blocker_id": "R79-A2",
                "priority": 3,
                "target_gate": "accepted_exit_route_positive",
                "needed_artifact": "acceptance verdict that turns the prefilled route/replay surface into one accepted exit route after B/C ledgers pass",
            },
        ],
        "b7_rule": "Do not run nonzero B7 retest until R79-B/C and accepted_exit_route_positive pass together.",
    }
    queue["blocker_queue_hash"] = stable_self_hash(queue, "blocker_queue_hash")
    return queue


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    r78 = load_json(root / R78_RESULT)
    r78_contract = load_json(root / R78_CONTRACT)
    r78_empty_preflight = load_json(root / R78_EMPTY_PREFLIGHT)
    r70 = load_json(root / R70_RESULT)
    r70_prefill = load_json(root / R70_PREFILL)
    packet = build_packet(root, r78_contract, r70_prefill)
    write_json(root / R79_PACKET, packet)
    preflight = preflight_packet(root, r78_contract, packet)
    write_json(root / R79_PREFLIGHT, preflight)
    blocker_queue = build_blocker_queue(preflight)
    write_json(root / R79_BLOCKER_QUEUE, blocker_queue)
    stdout = {
        "artifact": "R79 R78-A route/replay prefill stdout",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "packet_hash": packet["packet_hash"],
        "preflight_accepted": preflight["accepted"],
        "missing_required_field_count_before": r78_empty_preflight[
            "missing_required_field_count"
        ],
        "missing_required_field_count_after": preflight["missing_required_field_count"],
        "accepted_exit_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
    }
    write_json(root / R79_STDOUT, stdout)

    r78_summary = r78["summary"]
    requirements = [
        req(
            "A1",
            "R78 contract is the upstream packet contract",
            r78_summary["requirements_failed"] == 0
            and r78_summary["template_preflight_accepted"] is False,
            {
                "r78_result_path": R78_RESULT,
                "r78_result_sha256": file_hash(root / R78_RESULT),
                "r78_contract_hash": r78_summary["contract_hash"],
            },
        ),
        req(
            "A2",
            "R70 supplies the route artifact, replay stdout, and certificate paths",
            r70["summary"]["machine_check_replay_passed"] is True
            and all(
                path_hash_matches(root, r70_prefill[path_key], r70_prefill[sha_key])
                for path_key, sha_key in [
                    ("full_circuit_rewrite_artifact_path", "full_circuit_rewrite_artifact_sha256"),
                    ("machine_check_replay_stdout_path", "machine_check_replay_stdout_sha256"),
                    ("semantic_or_symbolic_equivalence_certificate_path", "semantic_or_symbolic_equivalence_certificate_sha256"),
                ]
            ),
            {
                "r70_prefill_path": R70_PREFILL,
                "r70_prefill_sha256": file_hash(root / R70_PREFILL),
                "machine_check_replay_passed": r70["summary"]["machine_check_replay_passed"],
            },
        ),
        req(
            "A3",
            "R79 fills the R78-A route/replay/certificate surface",
            all(
                packet.get(field) not in (None, "")
                for field in [
                    "accepted_route_artifact_path",
                    "accepted_route_artifact_sha256",
                    "full_circuit_or_route_bounded_replay_command",
                    "full_circuit_or_route_bounded_replay_stdout_path",
                    "full_circuit_or_route_bounded_replay_stdout_sha256",
                    "same_unitary_or_symbolic_certificate_path",
                    "same_unitary_or_symbolic_certificate_sha256",
                ]
            ),
            {
                "packet_path": R79_PACKET,
                "packet_sha256": file_hash(root / R79_PACKET),
                "packet_hash": packet["packet_hash"],
            },
        ),
        req(
            "A4",
            "R79 preserves the R76 no-double-counting boundary",
            path_hash_matches(
                root,
                packet["source_r76_no_double_counting_ledger_path"],
                packet["source_r76_no_double_counting_ledger_sha256"],
            )
            and path_hash_matches(
                root,
                packet["no_double_counting_preservation_verdict_path"],
                packet["no_double_counting_preservation_verdict_sha256"],
            ),
            {
                "source_r76_no_double_counting_ledger_path": packet[
                    "source_r76_no_double_counting_ledger_path"
                ],
                "no_double_counting_preservation_verdict_path": packet[
                    "no_double_counting_preservation_verdict_path"
                ],
            },
        ),
        req(
            "A5",
            "R79 reduces missing production fields versus the R78 empty template",
            preflight["missing_required_field_count"]
            < r78_empty_preflight["missing_required_field_count"],
            {
                "missing_before": r78_empty_preflight["missing_required_field_count"],
                "missing_after": preflight["missing_required_field_count"],
                "missing_required_fields_after": preflight["missing_required_fields"],
            },
        ),
        req(
            "A6",
            "R79 remains rejected until positive occurrence and proxy-T acceptance exist",
            preflight["accepted"] is False
            and "accepted_occurrence_positive" in preflight["failed_gates"]
            and "accepted_proxy_t_positive" in preflight["failed_gates"],
            {"failed_gates": preflight["failed_gates"]},
        ),
        req(
            "A7",
            "Accepted counters and B7 credit remain zero",
            preflight["accepted_exit_route_count"] == 0
            and preflight["accepted_occurrence_removal"] == 0
            and preflight["accepted_proxy_t_reduction"] == 0
            and preflight["b7_credit_delta"] == 0
            and preflight["b7_nonzero_retest_allowed"] is False,
            {
                "accepted_exit_route_count": preflight["accepted_exit_route_count"],
                "accepted_occurrence_removal": preflight["accepted_occurrence_removal"],
                "accepted_proxy_t_reduction": preflight["accepted_proxy_t_reduction"],
                "b7_credit_delta": preflight["b7_credit_delta"],
            },
        ),
        req(
            "A8",
            "R79 emits the next blocker queue",
            len(blocker_queue["queue"]) == 3,
            {
                "blocker_queue_path": R79_BLOCKER_QUEUE,
                "blocker_queue_sha256": file_hash(root / R79_BLOCKER_QUEUE),
                "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
            },
        ),
    ]
    failed_requirements = [
        requirement["requirement_id"]
        for requirement in requirements
        if not requirement["passed"]
    ]
    validation_errors = []
    if preflight["accepted"]:
        validation_errors.append("R79 partial packet must remain rejected")
    if preflight["b7_credit_delta"] != 0:
        validation_errors.append("R79 must preserve zero B7 credit")
    if preflight["missing_required_field_count"] >= r78_empty_preflight["missing_required_field_count"]:
        validation_errors.append("R79 must reduce the R78 missing-field count")

    payload = {
        "artifact": "B1/B7 cone01 R79 R78-A route/replay prefill gate",
        "method": METHOD,
        "version": VERSION,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "generated_at_unix": int(time.time()),
        "packet_path": R79_PACKET,
        "packet_hash": packet["packet_hash"],
        "preflight_path": R79_PREFLIGHT,
        "preflight_hash": preflight["verdict_hash"],
        "stdout_path": R79_STDOUT,
        "stdout_sha256": file_hash(root / R79_STDOUT),
        "blocker_queue_path": R79_BLOCKER_QUEUE,
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
            "r78_missing_required_field_count_before": r78_empty_preflight[
                "missing_required_field_count"
            ],
            "r79_missing_required_field_count_after": preflight[
                "missing_required_field_count"
            ],
            "r79_filled_route_replay_surface": True,
            "r79_preflight_accepted": preflight["accepted"],
            "r79_failed_gates": preflight["failed_gates"],
            "accepted_exit_route_count": 0,
            "accepted_occurrence_removal": 0,
            "accepted_proxy_t_reduction": 0,
            "b7_credit_delta": 0,
            "b7_nonzero_retest_allowed": False,
            "o3_closed": False,
            "reroute_allowed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "packet_hash": packet["packet_hash"],
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
    report_path = root / "research/B1_B7_cone01_R79_r78a_route_replay_prefill_gate.md"
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone01 R79 R78-A Route/Replay Prefill Gate",
        "",
        f"- Target: `{TARGET_ID}`",
        f"- Upstream target: `{UPSTREAM_TARGET_ID}`",
        f"- Method: `{METHOD}`",
        f"- Status: `{STATUS}`",
        f"- Model status: `{MODEL_STATUS}`",
        "",
        "## Result",
        "",
        "R79 fills the R78-A route artifact, replay stdout, and certificate",
        "surface from the existing R70 machine-check replay path while preserving",
        "the R76 no-double-counting boundary. The packet remains rejected because",
        "occurrence and proxy-T acceptance ledgers are still missing and all",
        "accepted counters stay zero.",
        "",
        "## Key Counters",
        "",
        f"- Missing fields before: `{summary['r78_missing_required_field_count_before']}`",
        f"- Missing fields after: `{summary['r79_missing_required_field_count_after']}`",
        f"- R79 preflight accepted: `{summary['r79_preflight_accepted']}`",
        f"- Failed gates: `{summary['r79_failed_gates']}`",
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
            f"- Result JSON: `results/B1_B7_cone01_R79_r78a_route_replay_prefill_gate_v0.json`",
            f"- Partial packet: `{R79_PACKET}`",
            f"- Preflight verdict: `{R79_PREFLIGHT}`",
            f"- Blocker queue: `{R79_BLOCKER_QUEUE}`",
            f"- Stdout: `{R79_STDOUT}`",
            "",
            "## Claim Boundary",
            "",
            "R79 is not an accepted exit route, not O3 closure, not reroute",
            "permission, not resource saving, and not B7 credit. It only reduces",
            "the R78 packet surface by filling route/replay/certificate evidence.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--output",
        default="results/B1_B7_cone01_R79_r78a_route_replay_prefill_gate_v0.json",
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
        raise SystemExit("B1/B7 R79 R78-A route/replay prefill validation failed")


if __name__ == "__main__":
    main()
