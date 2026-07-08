#!/usr/bin/env python3
"""T-B1-004gd/T-B7-015m: R80 acceptance-ledger binding gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r80_acceptance_ledger_binding_gate_v0"
STATUS = "cone01_r80_acceptance_ledgers_bound_zero_positive_delta"
MODEL_STATUS = "acceptance_ledgers_hash_bound_but_positive_gates_still_zero"
VERSION = "0.1"
TARGET_ID = "T-B1-004gd/T-B7-015m"
UPSTREAM_TARGET_ID = "T-B1-004gc/T-B7-015l"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"

R78_CONTRACT = f"{SUBMISSION_DIR}/R78-positive-route-packet.contract.json"
R79_PACKET = f"{SUBMISSION_DIR}/R79-r78a-route-replay-prefill.packet.json"
R79_PREFLIGHT = f"{SUBMISSION_DIR}/R79-r78a-route-replay-prefill.verdict.json"
R70_PREFILL = f"{SUBMISSION_DIR}/R70-R1-line1381-prefill-machine-check-replay.json"
R71_CONTRACT = f"{SUBMISSION_DIR}/R71-R1-positive-delta-ledger.contract.json"
R76_NO_DOUBLE_COUNTING_LEDGER = f"{SUBMISSION_DIR}/R76-line1378-no-double-counting-ledger.json"
R76_NO_DOUBLE_COUNTING_VERDICT = f"{SUBMISSION_DIR}/R76-line1378-no-double-counting-replay.verdict.json"
R66_RESULT = "results/B1_B7_cone01_R66_o3_f4_b7_zero_credit_ledger_retest_gate_v0.json"
R80_OCCURRENCE_LEDGER = f"{SUBMISSION_DIR}/R80-occurrence-acceptance-zero-ledger.json"
R80_PROXY_T_LEDGER = f"{SUBMISSION_DIR}/R80-proxy-t-acceptance-zero-ledger.json"
R80_PACKET = f"{SUBMISSION_DIR}/R80-acceptance-ledger-bound-zero.packet.json"
R80_PREFLIGHT = f"{SUBMISSION_DIR}/R80-acceptance-ledger-bound-zero.verdict.json"
R80_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R80-acceptance-ledger-blocker-queue.json"
R80_STDOUT = f"{SUBMISSION_DIR}/R80-acceptance-ledger-binding.stdout.txt"


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
        "artifact": "R80 acceptance-ledger-bound packet preflight verdict",
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
        "accepted_exit_route_count": packet.get("accepted_exit_route_count", 0),
        "accepted_occurrence_removal": packet.get("accepted_occurrence_removal", 0),
        "accepted_proxy_t_reduction": packet.get("accepted_proxy_t_reduction", 0),
        "b7_credit_delta": 0,
        "b7_nonzero_retest_allowed": False,
        "rejection_reason": "acceptance_ledgers_bound_but_positive_occurrence_and_proxy_t_are_zero",
    }
    verdict["verdict_hash"] = stable_self_hash(verdict, "verdict_hash")
    return verdict


def build_occurrence_ledger(
    root: Path,
    r79_packet: dict[str, Any],
    r79_preflight: dict[str, Any],
    r70_prefill: dict[str, Any],
    r71_contract: dict[str, Any],
    r66_result: dict[str, Any],
) -> dict[str, Any]:
    ledger = {
        "artifact": "R80 occurrence acceptance zero ledger",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "ledger_id": "B1-B7-cone01-R80-occurrence-acceptance-zero-ledger",
        "route_id": r79_packet["route_id"],
        "source_r79_packet_path": R79_PACKET,
        "source_r79_packet_sha256": file_hash(root / R79_PACKET),
        "source_r79_packet_hash": r79_packet["packet_hash"],
        "source_r79_preflight_path": R79_PREFLIGHT,
        "source_r79_preflight_sha256": file_hash(root / R79_PREFLIGHT),
        "source_r79_missing_required_field_count": r79_preflight[
            "missing_required_field_count"
        ],
        "source_r70_prefill_path": R70_PREFILL,
        "source_r70_prefill_sha256": file_hash(root / R70_PREFILL),
        "source_r70_prefill_hash": r70_prefill["prefill_hash"],
        "source_r71_contract_path": R71_CONTRACT,
        "source_r71_contract_sha256": file_hash(root / R71_CONTRACT),
        "source_r71_contract_hash": r71_contract["contract_hash"],
        "source_r66_retest_packet_hash": r66_result["summary"]["r66_retest_packet_hash"],
        "source_r76_no_double_counting_ledger_path": R76_NO_DOUBLE_COUNTING_LEDGER,
        "source_r76_no_double_counting_ledger_sha256": file_hash(
            root / R76_NO_DOUBLE_COUNTING_LEDGER
        ),
        "selected_lines": [268, 1381],
        "dropped_overlap_lines": [1378],
        "structural_cnot_delta": r70_prefill.get("source_operation_counts", {}).get("cx", 0)
        - r70_prefill.get("candidate_operation_counts", {}).get("cx", 0),
        "accepted_occurrence_removal": 0,
        "accepted": False,
        "positive_gate_blocked": "accepted_occurrence_positive",
        "evidence_assessment": [
            "R70 machine replay is hash-bound and passes for the route surface.",
            "R76 prevents counting the overlapping line1378 window together with line1381.",
            "No source-backed occurrence-removal row has been accepted beyond the zero-credit R66 retest packet.",
            "A structural CNOT delta alone is forbidden as occurrence acceptance.",
        ],
        "occurrence_delta_derivation": (
            "Occurrence acceptance remains zero because the available route evidence "
            "does not prove an accepted occurrence-removal row under the R71/R78 "
            "positive-delta rules."
        ),
        "claim_boundary": (
            "This ledger fills the R78 occurrence_acceptance_ledger path/hash fields "
            "only. It cannot make accepted_occurrence_positive true, close O3, "
            "permit reroute, claim resource saving, or grant B7 credit."
        ),
    }
    ledger["ledger_hash"] = stable_self_hash(ledger, "ledger_hash")
    return ledger


def build_proxy_t_ledger(
    root: Path,
    r79_packet: dict[str, Any],
    r79_preflight: dict[str, Any],
    r70_prefill: dict[str, Any],
    r71_contract: dict[str, Any],
    r66_result: dict[str, Any],
) -> dict[str, Any]:
    ledger = {
        "artifact": "R80 proxy-T acceptance zero ledger",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "ledger_id": "B1-B7-cone01-R80-proxy-t-acceptance-zero-ledger",
        "route_id": r79_packet["route_id"],
        "source_r79_packet_path": R79_PACKET,
        "source_r79_packet_sha256": file_hash(root / R79_PACKET),
        "source_r79_packet_hash": r79_packet["packet_hash"],
        "source_r79_preflight_path": R79_PREFLIGHT,
        "source_r79_preflight_sha256": file_hash(root / R79_PREFLIGHT),
        "source_r79_missing_required_field_count": r79_preflight[
            "missing_required_field_count"
        ],
        "source_r70_prefill_path": R70_PREFILL,
        "source_r70_prefill_sha256": file_hash(root / R70_PREFILL),
        "source_r70_prefill_hash": r70_prefill["prefill_hash"],
        "source_r71_contract_path": R71_CONTRACT,
        "source_r71_contract_sha256": file_hash(root / R71_CONTRACT),
        "source_r71_contract_hash": r71_contract["contract_hash"],
        "source_r66_retest_packet_hash": r66_result["summary"]["r66_retest_packet_hash"],
        "source_r76_no_double_counting_verdict_path": R76_NO_DOUBLE_COUNTING_VERDICT,
        "source_r76_no_double_counting_verdict_sha256": file_hash(
            root / R76_NO_DOUBLE_COUNTING_VERDICT
        ),
        "selected_lines": [268, 1381],
        "dropped_overlap_lines": [1378],
        "structural_cnot_delta": r70_prefill.get("source_operation_counts", {}).get("cx", 0)
        - r70_prefill.get("candidate_operation_counts", {}).get("cx", 0),
        "accepted_proxy_t_reduction": 0,
        "accepted": False,
        "positive_gate_blocked": "accepted_proxy_t_positive",
        "evidence_assessment": [
            "R70 preserves proxy_t_reduction_delta=0.",
            "R66 is a zero-credit ledger retest and cannot be reused as positive proxy-T evidence.",
            "The route still has no source-backed proxy-T derivation beyond prefill-only pricing.",
            "A structural CNOT delta alone is forbidden as proxy-T acceptance.",
        ],
        "proxy_t_delta_derivation": (
            "Proxy-T acceptance remains zero because no accepted derivation proves "
            "a counted proxy-T reduction under the R71/R78 positive-delta rules."
        ),
        "claim_boundary": (
            "This ledger fills the R78 proxy_t_acceptance_ledger path/hash fields "
            "only. It cannot make accepted_proxy_t_positive true, close O3, "
            "permit reroute, claim resource saving, or grant B7 credit."
        ),
    }
    ledger["ledger_hash"] = stable_self_hash(ledger, "ledger_hash")
    return ledger


def build_packet(
    root: Path,
    r79_packet: dict[str, Any],
    occurrence_ledger: dict[str, Any],
    proxy_t_ledger: dict[str, Any],
) -> dict[str, Any]:
    packet = dict(r79_packet)
    packet.update(
        {
            "packet_id": "B1-B7-cone01-R80-acceptance-ledger-bound-zero-packet",
            "route_class": "r79bc_acceptance_ledgers_bound_zero_not_positive",
            "source_r79_packet_path": R79_PACKET,
            "source_r79_packet_sha256": file_hash(root / R79_PACKET),
            "source_r79_packet_hash": r79_packet["packet_hash"],
            "occurrence_acceptance_ledger_path": R80_OCCURRENCE_LEDGER,
            "occurrence_acceptance_ledger_sha256": file_hash(root / R80_OCCURRENCE_LEDGER),
            "proxy_t_acceptance_ledger_path": R80_PROXY_T_LEDGER,
            "proxy_t_acceptance_ledger_sha256": file_hash(root / R80_PROXY_T_LEDGER),
            "accepted_exit_route_count": 0,
            "accepted_occurrence_removal": occurrence_ledger["accepted_occurrence_removal"],
            "accepted_proxy_t_reduction": proxy_t_ledger["accepted_proxy_t_reduction"],
            "b7_nonzero_retest_requested": False,
            "claim_boundary": (
                "R80 fills the missing R78 occurrence and proxy-T acceptance ledger "
                "path/hash fields with explicit zero-acceptance ledgers. It cannot "
                "close O3, permit reroute, claim resource saving, or grant B7 credit "
                "because accepted_exit_route_count, accepted_occurrence_removal, and "
                "accepted_proxy_t_reduction remain zero."
            ),
        }
    )
    packet["packet_hash"] = stable_self_hash(packet, "packet_hash")
    return packet


def build_blocker_queue(preflight: dict[str, Any]) -> dict[str, Any]:
    queue = {
        "artifact": "R80 acceptance-ledger remaining blocker queue",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "current_preflight_accepted": preflight["accepted"],
        "missing_required_fields": preflight["missing_required_fields"],
        "failed_gates": preflight["failed_gates"],
        "queue": [
            {
                "blocker_id": "R80-P1",
                "priority": 1,
                "target_gate": "accepted_occurrence_positive",
                "needed_artifact": "source-backed occurrence-removal ledger with accepted_occurrence_removal>=1",
            },
            {
                "blocker_id": "R80-P2",
                "priority": 2,
                "target_gate": "accepted_proxy_t_positive",
                "needed_artifact": "source-backed proxy-T derivation ledger with accepted_proxy_t_reduction>=1",
            },
            {
                "blocker_id": "R80-P3",
                "priority": 3,
                "target_gate": "accepted_exit_route_positive",
                "needed_artifact": "packet rerun after P1/P2 pass with accepted_exit_route_count>=1",
            },
        ],
        "b7_rule": "No nonzero B7 retest until R80-P1/P2/P3 all pass together.",
    }
    queue["blocker_queue_hash"] = stable_self_hash(queue, "blocker_queue_hash")
    return queue


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    contract = load_json(root / R78_CONTRACT)
    r79_packet = load_json(root / R79_PACKET)
    r79_preflight = load_json(root / R79_PREFLIGHT)
    r70_prefill = load_json(root / R70_PREFILL)
    r71_contract = load_json(root / R71_CONTRACT)
    r66_result = load_json(root / R66_RESULT)

    occurrence_ledger = build_occurrence_ledger(
        root, r79_packet, r79_preflight, r70_prefill, r71_contract, r66_result
    )
    write_json(root / R80_OCCURRENCE_LEDGER, occurrence_ledger)
    proxy_t_ledger = build_proxy_t_ledger(
        root, r79_packet, r79_preflight, r70_prefill, r71_contract, r66_result
    )
    write_json(root / R80_PROXY_T_LEDGER, proxy_t_ledger)
    packet = build_packet(root, r79_packet, occurrence_ledger, proxy_t_ledger)
    write_json(root / R80_PACKET, packet)
    preflight = preflight_packet(root, contract, packet)
    write_json(root / R80_PREFLIGHT, preflight)
    blocker_queue = build_blocker_queue(preflight)
    write_json(root / R80_BLOCKER_QUEUE, blocker_queue)
    stdout = {
        "artifact": "R80 acceptance-ledger binding stdout",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "packet_hash": packet["packet_hash"],
        "preflight_accepted": preflight["accepted"],
        "missing_required_field_count_before": r79_preflight["missing_required_field_count"],
        "missing_required_field_count_after": preflight["missing_required_field_count"],
        "failed_gates": preflight["failed_gates"],
        "accepted_exit_route_count": preflight["accepted_exit_route_count"],
        "accepted_occurrence_removal": preflight["accepted_occurrence_removal"],
        "accepted_proxy_t_reduction": preflight["accepted_proxy_t_reduction"],
        "b7_credit_delta": 0,
    }
    write_json(root / R80_STDOUT, stdout)

    failed_set = set(preflight["failed_gates"])
    requirements = [
        req(
            "A1",
            "R79 is the upstream partial packet with four missing ledger fields",
            r79_preflight["missing_required_field_count"] == 4
            and "all_required_fields_complete" in r79_preflight["failed_gates"],
            {
                "r79_packet_path": R79_PACKET,
                "r79_packet_sha256": file_hash(root / R79_PACKET),
                "r79_missing_required_field_count": r79_preflight[
                    "missing_required_field_count"
                ],
            },
        ),
        req(
            "A2",
            "R80 binds an occurrence acceptance ledger while keeping occurrence credit zero",
            path_hash_matches(root, R80_OCCURRENCE_LEDGER, packet["occurrence_acceptance_ledger_sha256"])
            and occurrence_ledger["accepted_occurrence_removal"] == 0
            and occurrence_ledger["accepted"] is False,
            {
                "occurrence_ledger_path": R80_OCCURRENCE_LEDGER,
                "occurrence_ledger_sha256": file_hash(root / R80_OCCURRENCE_LEDGER),
                "occurrence_ledger_hash": occurrence_ledger["ledger_hash"],
            },
        ),
        req(
            "A3",
            "R80 binds a proxy-T acceptance ledger while keeping proxy-T credit zero",
            path_hash_matches(root, R80_PROXY_T_LEDGER, packet["proxy_t_acceptance_ledger_sha256"])
            and proxy_t_ledger["accepted_proxy_t_reduction"] == 0
            and proxy_t_ledger["accepted"] is False,
            {
                "proxy_t_ledger_path": R80_PROXY_T_LEDGER,
                "proxy_t_ledger_sha256": file_hash(root / R80_PROXY_T_LEDGER),
                "proxy_t_ledger_hash": proxy_t_ledger["ledger_hash"],
            },
        ),
        req(
            "A4",
            "R80 removes the R78/R79 missing-field blocker",
            preflight["missing_required_field_count"] == 0
            and preflight["gates"]["all_required_fields_complete"] is True
            and preflight["gates"]["all_hash_bound_artifacts_match"] is True,
            {
                "missing_before": r79_preflight["missing_required_field_count"],
                "missing_after": preflight["missing_required_field_count"],
                "hash_failures": preflight["hash_failures"],
            },
        ),
        req(
            "A5",
            "R80 remains rejected only on the three positive-promotion gates",
            preflight["accepted"] is False
            and failed_set
            == {
                "accepted_exit_route_positive",
                "accepted_occurrence_positive",
                "accepted_proxy_t_positive",
            },
            {"failed_gates": preflight["failed_gates"]},
        ),
        req(
            "A6",
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
            "A7",
            "R80 emits a tighter blocker queue with no missing-field work left",
            len(blocker_queue["queue"]) == 3
            and blocker_queue["missing_required_fields"] == [],
            {
                "blocker_queue_path": R80_BLOCKER_QUEUE,
                "blocker_queue_sha256": file_hash(root / R80_BLOCKER_QUEUE),
                "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
            },
        ),
        req(
            "A8",
            "R80 claim boundary blocks O3 closure, reroute, resource saving, and B7 credit",
            all(
                token in packet["claim_boundary"].lower()
                for token in ["cannot", "reroute", "resource saving", "b7 credit"]
            ),
            {"claim_boundary": packet["claim_boundary"]},
        ),
    ]
    failed_requirements = [
        requirement["requirement_id"]
        for requirement in requirements
        if not requirement["passed"]
    ]
    validation_errors = []
    if preflight["accepted"]:
        validation_errors.append("R80 packet must remain rejected until positive gates pass")
    if preflight["missing_required_field_count"] != 0:
        validation_errors.append("R80 must remove all missing production fields")
    if preflight["b7_credit_delta"] != 0:
        validation_errors.append("R80 must preserve zero B7 credit")

    payload = {
        "artifact": "B1/B7 cone01 R80 acceptance-ledger binding gate",
        "method": METHOD,
        "version": VERSION,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "generated_at_unix": int(time.time()),
        "occurrence_ledger_path": R80_OCCURRENCE_LEDGER,
        "occurrence_ledger_hash": occurrence_ledger["ledger_hash"],
        "proxy_t_ledger_path": R80_PROXY_T_LEDGER,
        "proxy_t_ledger_hash": proxy_t_ledger["ledger_hash"],
        "packet_path": R80_PACKET,
        "packet_hash": packet["packet_hash"],
        "preflight_path": R80_PREFLIGHT,
        "preflight_hash": preflight["verdict_hash"],
        "stdout_path": R80_STDOUT,
        "stdout_sha256": file_hash(root / R80_STDOUT),
        "blocker_queue_path": R80_BLOCKER_QUEUE,
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
            "r79_missing_required_field_count_before": r79_preflight[
                "missing_required_field_count"
            ],
            "r80_missing_required_field_count_after": preflight[
                "missing_required_field_count"
            ],
            "r80_all_hash_bound_artifacts_match": preflight["gates"][
                "all_hash_bound_artifacts_match"
            ],
            "r80_preflight_accepted": preflight["accepted"],
            "r80_failed_gates": preflight["failed_gates"],
            "accepted_exit_route_count": preflight["accepted_exit_route_count"],
            "accepted_occurrence_removal": preflight["accepted_occurrence_removal"],
            "accepted_proxy_t_reduction": preflight["accepted_proxy_t_reduction"],
            "b7_credit_delta": 0,
            "b7_nonzero_retest_allowed": False,
            "o3_closed": False,
            "reroute_allowed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "occurrence_ledger_hash": occurrence_ledger["ledger_hash"],
            "proxy_t_ledger_hash": proxy_t_ledger["ledger_hash"],
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
    report_path = root / "research/B1_B7_cone01_R80_acceptance_ledger_binding_gate.md"
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone01 R80 Acceptance-Ledger Binding Gate",
        "",
        f"- Target: `{TARGET_ID}`",
        f"- Upstream target: `{UPSTREAM_TARGET_ID}`",
        f"- Method: `{METHOD}`",
        f"- Status: `{STATUS}`",
        f"- Model status: `{MODEL_STATUS}`",
        "",
        "## Result",
        "",
        "R80 fills the two missing R78/R79 ledger path/hash fields with explicit",
        "zero-acceptance occurrence and proxy-T ledgers. This removes the missing",
        "production-field blocker and hash-binds all required packet artifacts, but",
        "the packet remains rejected because the three positive-promotion gates all",
        "stay at zero.",
        "",
        "## Key Counters",
        "",
        f"- Missing fields before: `{summary['r79_missing_required_field_count_before']}`",
        f"- Missing fields after: `{summary['r80_missing_required_field_count_after']}`",
        f"- All hash-bound artifacts match: `{summary['r80_all_hash_bound_artifacts_match']}`",
        f"- R80 preflight accepted: `{summary['r80_preflight_accepted']}`",
        f"- Failed gates: `{summary['r80_failed_gates']}`",
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
            "- Result JSON: `results/B1_B7_cone01_R80_acceptance_ledger_binding_gate_v0.json`",
            f"- Occurrence ledger: `{R80_OCCURRENCE_LEDGER}`",
            f"- Proxy-T ledger: `{R80_PROXY_T_LEDGER}`",
            f"- Bound packet: `{R80_PACKET}`",
            f"- Preflight verdict: `{R80_PREFLIGHT}`",
            f"- Blocker queue: `{R80_BLOCKER_QUEUE}`",
            f"- Stdout: `{R80_STDOUT}`",
            "",
            "## Claim Boundary",
            "",
            "R80 is not an accepted exit route, not O3 closure, not reroute",
            "permission, not resource saving, and not B7 credit. It only proves that",
            "the route/replay packet is now field-complete and hash-bound while the",
            "positive occurrence/proxy-T gates remain unsatisfied.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--output",
        default="results/B1_B7_cone01_R80_acceptance_ledger_binding_gate_v0.json",
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
        raise SystemExit("B1/B7 R80 acceptance-ledger binding validation failed")


if __name__ == "__main__":
    main()
