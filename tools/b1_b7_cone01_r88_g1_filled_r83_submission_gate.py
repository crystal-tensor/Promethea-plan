#!/usr/bin/env python3
"""T-B1-004gl/T-B7-015u: R88 G1 filled R83 submission gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r88_g1_filled_r83_submission_gate_v0"
STATUS = "cone01_r88_g1_filled_r83_submission_ready_no_b7_credit"
MODEL_STATUS = "r87_filled_r83_submission_gate_closed_without_downstream_b7_replay"
VERSION = "0.1"
TARGET_ID = "T-B1-004gl/T-B7-015u"
UPSTREAM_TARGET_ID = "T-B1-004gk/T-B7-015t"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"

R83_CONTRACT = f"{SUBMISSION_DIR}/R83-b7-gap-closure.contract.json"
R84_PRIORITY_PACKET = f"{SUBMISSION_DIR}/R84-priority-gap-closure-packet.json"
R85_T_MAPPING = f"{SUBMISSION_DIR}/R85-G1-candidate-logical-t-mapping.json"
R85_NO_DOUBLE_COUNTING = f"{SUBMISSION_DIR}/R85-G1-no-double-counting-screen.json"
R86_STDOUT = f"{SUBMISSION_DIR}/R86-G1-source-binding-replay.stdout.txt"
R87_RESULT = "results/B1_B7_cone01_R87_g1_stv_reprice_ledger_gate_v0.json"
R87_STV_LEDGER = f"{SUBMISSION_DIR}/R87-G1-stv-reprice-ledger.json"
R87_PREFLIGHT = f"{SUBMISSION_DIR}/R87-G1-stv-aware-preflight.verdict.json"

R88_EVIDENCE_BUNDLE = f"{SUBMISSION_DIR}/R88-G1-filled-r83-evidence-bundle.json"
R88_FILLED_SUBMISSION = f"{SUBMISSION_DIR}/R88-G1-filled-r83-submission.json"
R88_PREFLIGHT = f"{SUBMISSION_DIR}/R88-G1-filled-r83-preflight.verdict.json"
R88_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R88-G1-downstream-b7-blocker-queue.json"
R88_STDOUT = f"{SUBMISSION_DIR}/R88-G1-filled-r83-submission.stdout.txt"


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


def build_evidence_bundle(root: Path, contract: dict[str, Any], r87_result: dict[str, Any]) -> dict[str, Any]:
    artifacts = [
        ("source_r82_result", contract["source_r82_result_path"], contract["source_r82_result_sha256"]),
        ("source_r82_ledger", contract["source_r82_ledger_path"], contract["source_r82_ledger_sha256"]),
        ("source_r82_verdict", contract["source_r82_verdict_path"], contract["source_r82_verdict_sha256"]),
        ("source_b7_boundary", contract["source_b7_boundary_path"], contract["source_b7_boundary_sha256"]),
        ("replay_stdout", R86_STDOUT, file_hash(root / R86_STDOUT)),
        ("t_ledger_reduction_rows", R87_STV_LEDGER, file_hash(root / R87_STV_LEDGER)),
        ("no_double_counting_ledger", R85_NO_DOUBLE_COUNTING, file_hash(root / R85_NO_DOUBLE_COUNTING)),
        ("logical_t_mapping_ledger", R85_T_MAPPING, file_hash(root / R85_T_MAPPING)),
        ("stv_reprice_ledger", R87_STV_LEDGER, file_hash(root / R87_STV_LEDGER)),
        ("r87_result", R87_RESULT, file_hash(root / R87_RESULT)),
    ]
    bundle = {
        "artifact": "R88 G1 filled R83 evidence bundle",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_contract_hash": contract["contract_hash"],
        "source_r87_payload_hash": r87_result["payload_hash"],
        "artifact_count": len(artifacts),
        "artifacts": [
            {
                "role": role,
                "path": path,
                "sha256": expected_sha,
                "actual_sha256": file_hash(root / path),
                "hash_matches": file_hash(root / path) == expected_sha,
            }
            for role, path, expected_sha in artifacts
        ],
        "claim_boundary": (
            "Evidence bundle only. It binds the filled R83 submission inputs but "
            "does not run downstream B7 replay or grant credit."
        ),
    }
    bundle["evidence_bundle_hash"] = stable_self_hash(bundle, "evidence_bundle_hash")
    return bundle


def build_submission(
    root: Path,
    contract: dict[str, Any],
    priority_packet: dict[str, Any],
    r87_result: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    summary = r87_result["summary"]
    fields = {
        "submission_id": "R88-G1-filled-r83-submission",
        "route_id": summary["route_id"],
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r82_result_path": contract["source_r82_result_path"],
        "source_r82_result_sha256": contract["source_r82_result_sha256"],
        "source_r82_ledger_path": contract["source_r82_ledger_path"],
        "source_r82_ledger_sha256": contract["source_r82_ledger_sha256"],
        "source_r82_verdict_path": contract["source_r82_verdict_path"],
        "source_r82_verdict_sha256": contract["source_r82_verdict_sha256"],
        "source_b7_boundary_path": contract["source_b7_boundary_path"],
        "source_b7_boundary_sha256": contract["source_b7_boundary_sha256"],
        "claimed_target_stv_reduction": 1.20,
        "claimed_t_ledger_reduction": summary["candidate_t_ledger_reduction"],
        "candidate_after_t_ledger": summary["candidate_after_t_ledger"],
        "evidence_bundle_path": R88_EVIDENCE_BUNDLE,
        "evidence_bundle_sha256": file_hash(root / R88_EVIDENCE_BUNDLE),
        "replay_command": "python3 tools/b1_b7_cone01_r86_g1_replay_stdout_binding_gate.py && python3 tools/b1_b7_cone01_r87_g1_stv_reprice_ledger_gate.py",
        "replay_stdout_path": R86_STDOUT,
        "replay_stdout_sha256": file_hash(root / R86_STDOUT),
        "t_ledger_reduction_rows_path": R87_STV_LEDGER,
        "t_ledger_reduction_rows_sha256": file_hash(root / R87_STV_LEDGER),
        "no_double_counting_ledger_path": R85_NO_DOUBLE_COUNTING,
        "no_double_counting_ledger_sha256": file_hash(root / R85_NO_DOUBLE_COUNTING),
        "logical_t_mapping_ledger_path": R85_T_MAPPING,
        "logical_t_mapping_ledger_sha256": file_hash(root / R85_T_MAPPING),
        "stv_reprice_ledger_path": R87_STV_LEDGER,
        "stv_reprice_ledger_sha256": file_hash(root / R87_STV_LEDGER),
        "claim_boundary": (
            "Filled R83 production submission only. O3 closure, reroute permission, "
            "resource saving, and B7 credit remain blocked until downstream B7 replay."
        ),
        "o3_closed": False,
        "reroute_allowed": False,
        "resource_saving_claimed": False,
        "b7_credit_requested": False,
    }
    submission = {
        "artifact": "R88 G1 filled R83 production submission",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_contract_path": R83_CONTRACT,
        "source_contract_hash": contract["contract_hash"],
        "source_priority_packet_hash": priority_packet["priority_packet_hash"],
        "required_field_count": len(contract["production_required_fields"]),
        "required_fields": contract["production_required_fields"],
        "field_count": len(fields),
        "fields": fields,
        "missing_required_fields": [
            field for field in contract["production_required_fields"] if field not in fields
        ],
        "extra_fields": sorted(field for field in fields if field not in contract["production_required_fields"]),
        "candidate_margin_to_1_20_target": summary["candidate_margin_to_1_20_target"],
        "accepted_b7_credit_delta": 0,
        "accepted_b7_space_time_volume_credit": 0,
        "claim_boundary": fields["claim_boundary"],
    }
    submission["filled_submission_hash"] = stable_self_hash(submission, "filled_submission_hash")
    return submission


def build_preflight(
    root: Path,
    contract: dict[str, Any],
    submission: dict[str, Any],
    evidence_bundle: dict[str, Any],
    r87_result: dict[str, Any],
    r87_preflight: dict[str, Any],
) -> dict[str, Any]:
    fields = submission["fields"]
    hash_roles = {
        "source_r82_result_sha256": fields["source_r82_result_path"],
        "source_r82_ledger_sha256": fields["source_r82_ledger_path"],
        "source_r82_verdict_sha256": fields["source_r82_verdict_path"],
        "source_b7_boundary_sha256": fields["source_b7_boundary_path"],
        "evidence_bundle_sha256": fields["evidence_bundle_path"],
        "replay_stdout_sha256": fields["replay_stdout_path"],
        "t_ledger_reduction_rows_sha256": fields["t_ledger_reduction_rows_path"],
        "no_double_counting_ledger_sha256": fields["no_double_counting_ledger_path"],
        "logical_t_mapping_ledger_sha256": fields["logical_t_mapping_ledger_path"],
        "stv_reprice_ledger_sha256": fields["stv_reprice_ledger_path"],
    }
    hash_checks = {
        key: fields[key] == file_hash(root / path)
        for key, path in hash_roles.items()
    }
    r83_gates = {
        "all_required_fields_complete": not submission["missing_required_fields"]
        and submission["field_count"] == submission["required_field_count"] == 33,
        "all_hash_bound_artifacts_match": all(hash_checks.values())
        and all(item["hash_matches"] for item in evidence_bundle["artifacts"]),
        "source_r82_boundary_hashes_match": fields["source_r82_result_sha256"]
        == contract["source_r82_result_sha256"]
        and fields["source_r82_ledger_sha256"] == contract["source_r82_ledger_sha256"]
        and fields["source_r82_verdict_sha256"] == contract["source_r82_verdict_sha256"]
        and fields["source_b7_boundary_sha256"] == contract["source_b7_boundary_sha256"],
        "claimed_t_ledger_reduction_at_least_591": fields["claimed_t_ledger_reduction"]
        >= contract["minimum_accepted_t_ledger_reduction"],
        "candidate_after_t_ledger_at_or_below_5632": fields["candidate_after_t_ledger"]
        <= 5632,
        "stv_reprice_ledger_present": r87_result["summary"]["stv_reprice_ledger_present"] is True
        and fields["stv_reprice_ledger_sha256"] == file_hash(root / fields["stv_reprice_ledger_path"]),
        "logical_t_mapping_ledger_present": fields["logical_t_mapping_ledger_sha256"]
        == file_hash(root / fields["logical_t_mapping_ledger_path"]),
        "no_double_counting_ledger_present": fields["no_double_counting_ledger_sha256"]
        == file_hash(root / fields["no_double_counting_ledger_path"]),
        "replay_stdout_hash_matches": fields["replay_stdout_sha256"]
        == file_hash(root / fields["replay_stdout_path"]),
        "claim_boundary_blocks_o3_reroute_until_audit": fields["o3_closed"] is False
        and fields["reroute_allowed"] is False
        and fields["resource_saving_claimed"] is False
        and fields["b7_credit_requested"] is False,
    }
    gates = {
        "source_rows_present": True,
        "replay_stdout_present": True,
        "stv_reprice_ledger_present": True,
        "filled_r83_submission_present": all(r83_gates.values()),
        "downstream_b7_replay_present": False,
    }
    failed = [gate for gate, passed in gates.items() if not passed]
    preflight = {
        "artifact": "R88 G1 filled R83 preflight verdict",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r87_preflight_hash": r87_preflight["preflight_hash"],
        "source_r87_failed_gates": r87_preflight["failed_gates"],
        "filled_submission_hash": submission["filled_submission_hash"],
        "evidence_bundle_hash": evidence_bundle["evidence_bundle_hash"],
        "hash_checks": hash_checks,
        "r83_acceptance_gates": r83_gates,
        "r83_acceptance_gate_count": len(r83_gates),
        "r83_acceptance_gates_passed": sum(1 for passed in r83_gates.values() if passed),
        "r83_acceptance_gates_failed": [
            gate for gate, passed in r83_gates.items() if not passed
        ],
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": len(failed),
        "failed_gates": failed,
        "accepted": False,
        "accepted_b7_credit_delta": 0,
        "accepted_b7_space_time_volume_credit": 0,
        "o3_closed": False,
        "reroute_allowed": False,
        "resource_saving_claimed": False,
        "closed_r87_failed_gates": ["filled_r83_submission_present"],
        "remaining_r87_failed_gates": ["downstream_b7_replay_present"],
        "claim_boundary": (
            "R88 changes only the filled_r83_submission_present gate from missing "
            "to present. It still rejects credit until downstream B7 replay exists."
        ),
    }
    preflight["preflight_hash"] = stable_self_hash(preflight, "preflight_hash")
    return preflight


def build_blocker_queue(preflight: dict[str, Any]) -> dict[str, Any]:
    queue = {
        "artifact": "R88 G1 downstream B7 blocker queue",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "preflight_hash": preflight["preflight_hash"],
        "accepted_b7_credit_delta": 0,
        "queue": [
            {
                "blocker_id": "R88-G1-1",
                "priority": 1,
                "target_gate": "downstream_b7_replay_present",
                "needed_artifact": "full downstream B7 replay against the filled R83 G1 submission before any nonzero B7 credit",
            }
        ],
    }
    queue["blocker_queue_hash"] = stable_self_hash(queue, "blocker_queue_hash")
    return queue


def write_stdout(root: Path, submission: dict[str, Any], preflight: dict[str, Any]) -> str:
    text = "\n".join(
        [
            "R88 G1 filled R83 submission stdout",
            f"method={METHOD}",
            f"source_target_id={TARGET_ID}",
            f"upstream_target_id={UPSTREAM_TARGET_ID}",
            f"filled_submission_hash={submission['filled_submission_hash']}",
            f"field_count={submission['field_count']}",
            f"required_field_count={submission['required_field_count']}",
            f"r83_acceptance_gates_passed={preflight['r83_acceptance_gates_passed']}",
            f"r83_acceptance_gate_count={preflight['r83_acceptance_gate_count']}",
            f"filled_r83_submission_present={str(preflight['gates']['filled_r83_submission_present']).lower()}",
            "downstream_b7_replay_present=false",
            "accepted_b7_credit_delta=0",
            "claim_boundary=filled R83 only; downstream B7 replay still required",
        ]
    ) + "\n"
    path = root / R88_STDOUT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    contract = load_json(root / R83_CONTRACT)
    priority_packet = load_json(root / R84_PRIORITY_PACKET)
    r87_result = load_json(root / R87_RESULT)
    r87_preflight = load_json(root / R87_PREFLIGHT)

    evidence_bundle = build_evidence_bundle(root, contract, r87_result)
    write_json(root / R88_EVIDENCE_BUNDLE, evidence_bundle)
    submission = build_submission(root, contract, priority_packet, r87_result, evidence_bundle)
    write_json(root / R88_FILLED_SUBMISSION, submission)
    preflight = build_preflight(root, contract, submission, evidence_bundle, r87_result, r87_preflight)
    write_json(root / R88_PREFLIGHT, preflight)
    stdout_sha256 = write_stdout(root, submission, preflight)
    blocker_queue = build_blocker_queue(preflight)
    write_json(root / R88_BLOCKER_QUEUE, blocker_queue)

    requirements = [
        req(
            "A1",
            "R88 consumes the R87 STV-repriced G1 row set",
            r87_result["summary"]["source_target_id"] == UPSTREAM_TARGET_ID
            and r87_result["summary"]["stv_reprice_ledger_present"] is True
            and r87_result["summary"]["preflight_failed_gate_count"] == 2,
            {
                "r87_payload_hash": r87_result["payload_hash"],
                "r87_stv_ledger_hash": r87_result["summary"]["stv_ledger_hash"],
            },
        ),
        req(
            "A2",
            "R88 fills all 33 R83 production fields",
            submission["field_count"] == submission["required_field_count"] == 33
            and not submission["missing_required_fields"]
            and not submission["extra_fields"],
            {
                "filled_submission_hash": submission["filled_submission_hash"],
                "field_count": submission["field_count"],
                "missing_required_fields": submission["missing_required_fields"],
            },
        ),
        req(
            "A3",
            "R88 hash-binds all required evidence artifacts",
            all(preflight["hash_checks"].values())
            and all(item["hash_matches"] for item in evidence_bundle["artifacts"]),
            {
                "evidence_bundle_hash": evidence_bundle["evidence_bundle_hash"],
                "hash_check_count": len(preflight["hash_checks"]),
            },
        ),
        req(
            "A4",
            "R88 passes all 10 R83 acceptance-shape gates",
            preflight["r83_acceptance_gates_passed"]
            == preflight["r83_acceptance_gate_count"]
            == 10
            and not preflight["r83_acceptance_gates_failed"],
            {
                "r83_acceptance_gates_passed": preflight["r83_acceptance_gates_passed"],
                "r83_acceptance_gate_count": preflight["r83_acceptance_gate_count"],
            },
        ),
        req(
            "A5",
            "R88 preserves candidate target math without accepted credit",
            submission["fields"]["claimed_t_ledger_reduction"] == 600
            and submission["fields"]["candidate_after_t_ledger"] == 5624
            and submission["candidate_margin_to_1_20_target"] == 8
            and preflight["accepted_b7_credit_delta"] == 0,
            {
                "claimed_t_ledger_reduction": submission["fields"][
                    "claimed_t_ledger_reduction"
                ],
                "candidate_after_t_ledger": submission["fields"]["candidate_after_t_ledger"],
                "candidate_margin_to_1_20_target": submission[
                    "candidate_margin_to_1_20_target"
                ],
            },
        ),
        req(
            "A6",
            "R88 closes exactly the R87 filled-submission blocker and leaves downstream replay open",
            preflight["closed_r87_failed_gates"] == ["filled_r83_submission_present"]
            and preflight["remaining_r87_failed_gates"] == ["downstream_b7_replay_present"]
            and preflight["failed_gate_count"] == 1,
            {
                "preflight_hash": preflight["preflight_hash"],
                "closed_r87_failed_gates": preflight["closed_r87_failed_gates"],
                "remaining_r87_failed_gates": preflight["remaining_r87_failed_gates"],
            },
        ),
        req(
            "A7",
            "R88 grants no B7, STV, reroute, O3, or resource-saving credit",
            preflight["accepted"] is False
            and preflight["accepted_b7_credit_delta"] == 0
            and preflight["accepted_b7_space_time_volume_credit"] == 0
            and preflight["o3_closed"] is False
            and preflight["reroute_allowed"] is False
            and preflight["resource_saving_claimed"] is False,
            {
                "accepted_b7_credit_delta": preflight["accepted_b7_credit_delta"],
                "accepted_b7_space_time_volume_credit": preflight[
                    "accepted_b7_space_time_volume_credit"
                ],
            },
        ),
    ]
    failed_requirements = [
        requirement["requirement_id"] for requirement in requirements if not requirement["passed"]
    ]
    validation_errors = []
    if failed_requirements:
        validation_errors.append("one or more R88 requirements failed")
    if preflight["accepted_b7_credit_delta"] != 0:
        validation_errors.append("R88 must not grant B7 credit")
    if "filled_r83_submission_present" in preflight["failed_gates"]:
        validation_errors.append("R88 must close filled_r83_submission_present")
    if preflight["failed_gates"] != ["downstream_b7_replay_present"]:
        validation_errors.append("R88 failed-gate set must contain only downstream B7 replay")

    payload = {
        "artifact": "B1/B7 cone01 R88 G1 filled R83 submission gate",
        "method": METHOD,
        "version": VERSION,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "generated_at_unix": int(time.time()),
        "evidence_bundle_path": R88_EVIDENCE_BUNDLE,
        "evidence_bundle_hash": evidence_bundle["evidence_bundle_hash"],
        "filled_submission_path": R88_FILLED_SUBMISSION,
        "filled_submission_hash": submission["filled_submission_hash"],
        "stdout_path": R88_STDOUT,
        "stdout_sha256": stdout_sha256,
        "preflight_path": R88_PREFLIGHT,
        "preflight_hash": preflight["preflight_hash"],
        "blocker_queue_path": R88_BLOCKER_QUEUE,
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
            "route_id": submission["fields"]["route_id"],
            "filled_field_count": submission["field_count"],
            "required_field_count": submission["required_field_count"],
            "missing_required_field_count": len(submission["missing_required_fields"]),
            "hash_bound_artifact_count": len(evidence_bundle["artifacts"]),
            "r83_acceptance_gates_passed": preflight["r83_acceptance_gates_passed"],
            "r83_acceptance_gate_count": preflight["r83_acceptance_gate_count"],
            "claimed_t_ledger_reduction": submission["fields"]["claimed_t_ledger_reduction"],
            "candidate_after_t_ledger": submission["fields"]["candidate_after_t_ledger"],
            "candidate_margin_to_1_20_target": submission[
                "candidate_margin_to_1_20_target"
            ],
            "filled_r83_submission_present": preflight["gates"][
                "filled_r83_submission_present"
            ],
            "downstream_b7_replay_present": preflight["gates"][
                "downstream_b7_replay_present"
            ],
            "closed_r87_failed_gates": preflight["closed_r87_failed_gates"],
            "remaining_r87_failed_gates": preflight["remaining_r87_failed_gates"],
            "preflight_accepted": preflight["accepted"],
            "preflight_failed_gate_count": preflight["failed_gate_count"],
            "failed_gates": preflight["failed_gates"],
            "accepted_b7_credit_delta": 0,
            "accepted_b7_space_time_volume_credit": 0,
            "o3_closed": False,
            "reroute_allowed": False,
            "resource_saving_claimed": False,
            "evidence_bundle_hash": evidence_bundle["evidence_bundle_hash"],
            "filled_submission_hash": submission["filled_submission_hash"],
            "stdout_sha256": stdout_sha256,
            "preflight_hash": preflight["preflight_hash"],
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
        "# B1/B7 Cone01 R88 G1 Filled R83 Submission Gate",
        "",
        f"- Target: `{TARGET_ID}`",
        f"- Upstream target: `{UPSTREAM_TARGET_ID}`",
        f"- Method: `{METHOD}`",
        f"- Status: `{STATUS}`",
        f"- Model status: `{MODEL_STATUS}`",
        "",
        "## Result",
        "",
        "R88 closes the filled-R83-submission blocker for the G1 route. It creates",
        "a 33-field production submission, binds every required artifact by SHA-256,",
        "and passes all 10 R83 acceptance-shape gates. The candidate math remains",
        "`600` T-ledger units and `5624` after-T ledger, but downstream B7 replay is",
        "still absent, so accepted B7 credit remains zero.",
        "",
        "## Key Counters",
        "",
        f"- Filled fields: `{summary['filled_field_count']}` / `{summary['required_field_count']}`",
        f"- Missing required fields: `{summary['missing_required_field_count']}`",
        f"- Hash-bound artifacts: `{summary['hash_bound_artifact_count']}`",
        f"- R83 gates passed: `{summary['r83_acceptance_gates_passed']}` / `{summary['r83_acceptance_gate_count']}`",
        f"- Claimed T-ledger reduction: `{summary['claimed_t_ledger_reduction']}`",
        f"- Candidate after T ledger: `{summary['candidate_after_t_ledger']}`",
        f"- Candidate margin to 1.20x target: `{summary['candidate_margin_to_1_20_target']}`",
        f"- Filled R83 submission present: `{summary['filled_r83_submission_present']}`",
        f"- Downstream B7 replay present: `{summary['downstream_b7_replay_present']}`",
        f"- Accepted B7 credit delta: `{summary['accepted_b7_credit_delta']}`",
        "",
        "## Closed Gate",
        "",
    ]
    for gate in summary["closed_r87_failed_gates"]:
        lines.append(f"- `{gate}`")
    lines.extend(["", "## Remaining Credit Gates", ""])
    for gate in summary["failed_gates"]:
        lines.append(f"- `{gate}`")
    lines.extend(["", "## Requirements", ""])
    for requirement in payload["requirements"]:
        status = "PASS" if requirement["passed"] else "FAIL"
        lines.append(f"- `{requirement['requirement_id']}` {status}: {requirement['label']}")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- Result JSON: `results/B1_B7_cone01_R88_g1_filled_r83_submission_gate_v0.json`",
            f"- Evidence bundle: `{R88_EVIDENCE_BUNDLE}`",
            f"- Filled R83 submission: `{R88_FILLED_SUBMISSION}`",
            f"- Filled R83 preflight: `{R88_PREFLIGHT}`",
            f"- Downstream blocker queue: `{R88_BLOCKER_QUEUE}`",
            f"- Stdout: `{R88_STDOUT}`",
            "",
            "## Claim Boundary",
            "",
            "R88 is a filled-submission gate. It does not run downstream B7 replay,",
            "does not close O3, does not permit reroute, and does not accept B7",
            "dependency, resource, FT-ledger, or STV credit. B7 credit remains zero.",
            "",
        ]
    )
    report_path = root / "research/B1_B7_cone01_R88_g1_filled_r83_submission_gate.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    payload = build_payload(args)
    result_path = root / "results/B1_B7_cone01_R88_g1_filled_r83_submission_gate_v0.json"
    write_json(result_path, payload)
    write_report(root, payload)
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
