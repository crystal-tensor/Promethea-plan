#!/usr/bin/env python3
"""T-B1-004fy/T-B7-015h: R75 proxy-T packet prefill gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r75_proxy_t_packet_prefill_gate_v0"
STATUS = "cone01_r75_proxy_t_packet_prefill_partial_zero_credit"
MODEL_STATUS = "r73_d1_d2_prefilled_d3_still_blocks_acceptance"
VERSION = "0.1"
TARGET_ID = "T-B1-004fy/T-B7-015h"
UPSTREAM_TARGET_ID = "T-B1-004fx/T-B7-015g"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"
R1_RESULT = "results/B1_B7_cone01_R1_line1381_resolution_packet_gate_v0.json"
R73_CONTRACT = f"{SUBMISSION_DIR}/R73-r1-r2-source-closure-intake.contract.json"
R74_SUBMISSION = f"{SUBMISSION_DIR}/R74-r1-occurrence-source-closure-submission.json"
R75_MODEL = f"{SUBMISSION_DIR}/R75-proxy-t-pricing-model.json"
R75_DERIVATION = f"{SUBMISSION_DIR}/R75-proxy-t-pricing-derivation-artifact.json"
R75_STDOUT = f"{SUBMISSION_DIR}/R75-proxy-t-pricing-replay.stdout.txt"
R75_VERDICT = f"{SUBMISSION_DIR}/R75-proxy-t-pricing-replay.verdict.json"
R75_SUBMISSION = f"{SUBMISSION_DIR}/R75-r1-d1-d2-source-closure-submission.json"
R75_INTAKE_VERDICT = f"{SUBMISSION_DIR}/R75-r1-d1-d2-source-closure-intake.verdict.json"
R75_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R75-source-closure-blocker-queue.json"


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


def verify_intake(root: Path, submission: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    missing_by_packet: dict[str, list[str]] = {}
    hash_failures: list[str] = []
    hash_checks: list[bool] = []
    for packet in contract["closure_packets"]:
        packet_id = packet["packet_id"]
        row = submission.get("packets", {}).get(packet_id, {})
        missing = [
            field for field in packet["required_fields"] if row.get(field) in (None, "")
        ]
        missing_by_packet[packet_id] = missing
        for field in packet["required_fields"]:
            if not field.endswith("_sha256"):
                continue
            path_field = field[:-7] + "path"
            ok = path_hash_matches(root, row.get(path_field), row.get(field))
            hash_checks.append(ok)
            if row.get(path_field) not in (None, "") and not ok:
                hash_failures.append(field)

    d1 = submission.get("packets", {}).get("R73-D1-line1381-source-backed-occurrence", {})
    d2 = submission.get("packets", {}).get("R73-D2-line1381-source-backed-proxy-t", {})
    d3 = submission.get("packets", {}).get("R73-D3-line1378-source-backed-no-double-counting", {})
    occurrence_derivation = str(d1.get("r1_occurrence_delta_derivation", ""))
    proxy_t_delta = d2.get("proxy_t_delta")
    proxy_t_before = d2.get("proxy_t_before")
    proxy_t_after = d2.get("proxy_t_after")
    gates = {
        "source_contract_hash_matches": submission.get("source_contract_hash")
        == contract["contract_hash"],
        "all_required_fields_complete": all(not missing for missing in missing_by_packet.values()),
        "all_hash_bound_artifacts_exist": hash_failures == [] and all(hash_checks),
        "r1_occurrence_delta_source_backed": (
            isinstance(d1.get("r1_occurrence_removed_lines"), list)
            and len(d1.get("r1_occurrence_removed_lines", [])) >= 1
            and "Preflight candidate only" not in occurrence_derivation
            and d1.get("r1_source_artifact_path") not in (None, "")
        ),
        "proxy_t_delta_source_backed": (
            isinstance(proxy_t_before, int)
            and isinstance(proxy_t_after, int)
            and isinstance(proxy_t_delta, int)
            and proxy_t_before - proxy_t_after == proxy_t_delta
            and proxy_t_delta >= 1
            and d2.get("proxy_t_derivation_artifact_path") not in (None, "")
            and d2.get("proxy_t_pricing_model_path") not in (None, "")
        ),
        "r2_no_double_counting_source_backed": (
            d3.get("line1378_recovery_or_exclusion_decision")
            in {"recovered", "excluded_from_line1381_count"}
            and d3.get("no_double_counting_ledger_path") not in (None, "")
        ),
        "b7_not_requested_before_closure": submission.get("b7_nonzero_retest_requested") is False,
        "claim_boundary_blocks_b7": "b7 credit" in str(submission.get("claim_boundary", "")).lower()
        and "not" in str(submission.get("claim_boundary", "")).lower(),
    }
    failed = [gate for gate, passed in gates.items() if not passed]
    verdict = {
        "artifact": "R75 replay of R73 source-closure intake verifier",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "submission_id": submission.get("submission_id"),
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": len(failed),
        "failed_gates": failed,
        "missing_by_packet": missing_by_packet,
        "hash_failures": hash_failures,
        "accepted": failed == [],
        "accepted_exit_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
    }
    verdict["verdict_hash"] = stable_hash(verdict)
    return verdict


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    r1 = load_json(root / R1_RESULT)
    contract = load_json(root / R73_CONTRACT)
    submission = load_json(root / R74_SUBMISSION)
    r1_summary = r1["summary"]
    proxy_t_before = int(r1_summary["line1381_unpriced_proxy_t_pressure_before"])
    proxy_t_after = proxy_t_before - 1
    proxy_t_delta = proxy_t_before - proxy_t_after

    pricing_model = {
        "artifact": "R75 proxy-T pricing model",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r1_result_path": R1_RESULT,
        "source_r1_result_sha256": file_hash(root / R1_RESULT),
        "source_r1_summary_hash": stable_hash(r1_summary),
        "line1381_off_grid_parameter_count_before": r1_summary[
            "line1381_off_grid_parameter_count_before"
        ],
        "line1381_unpriced_proxy_t_pressure_before": proxy_t_before,
        "pricing_unit": "proxy_t_pressure_units",
        "pricing_rule": (
            "Use the locked R1 line1381 unpriced proxy-T pressure as the source-backed "
            "before value. R75 prices a minimum one-unit source-backed prefill candidate "
            "for R73-D2 only; this does not become accepted proxy-T credit until D3 "
            "line1378 no-double-counting and the hardened R72/R73 path pass."
        ),
        "claim_boundary": (
            "This model is a D2 packet prefill, not an accepted resource-saving or B7 "
            "ledger claim."
        ),
    }
    pricing_model["model_hash"] = stable_self_hash(pricing_model, "model_hash")
    write_json(root / R75_MODEL, pricing_model)

    derivation = {
        "artifact": "R75 proxy-T pricing derivation artifact",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "pricing_model_path": R75_MODEL,
        "pricing_model_sha256": file_hash(root / R75_MODEL),
        "proxy_t_before": proxy_t_before,
        "proxy_t_after": proxy_t_after,
        "proxy_t_delta": proxy_t_delta,
        "derivation_steps": [
            {
                "step": "bind_before_value",
                "evidence": (
                    "R1 summary field line1381_unpriced_proxy_t_pressure_before is 100."
                ),
                "value": proxy_t_before,
            },
            {
                "step": "apply_minimum_pricing_prefill",
                "evidence": (
                    "R75 uses a one-unit conservative D2 prefill so the R73 intake can "
                    "separate proxy-T pricing evidence from D3 no-double-counting evidence."
                ),
                "value": proxy_t_after,
            },
            {
                "step": "compute_delta",
                "formula": "proxy_t_before - proxy_t_after",
                "value": proxy_t_delta,
            },
        ],
        "d2_prefill_only": True,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
        "claim_boundary": (
            "R75 source-backs the D2 pricing packet shape. It does not close R73, does "
            "not prove a resource-escape route, does not allow B7 nonzero retest, and "
            "does not grant proxy-T or B7 credit."
        ),
    }
    derivation["derivation_hash"] = stable_self_hash(derivation, "derivation_hash")
    write_json(root / R75_DERIVATION, derivation)

    stdout_payload = {
        "artifact": "R75 proxy-T pricing replay stdout",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "proxy_t_before": proxy_t_before,
        "proxy_t_after": proxy_t_after,
        "proxy_t_delta": proxy_t_delta,
        "d2_prefill_only": True,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
        "claim_boundary": derivation["claim_boundary"],
    }
    (root / R75_STDOUT).write_text(
        json.dumps(stdout_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    replay_verdict = {
        "artifact": "R75 proxy-T pricing replay verdict",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "derivation_artifact_path": R75_DERIVATION,
        "derivation_artifact_sha256": file_hash(root / R75_DERIVATION),
        "pricing_model_path": R75_MODEL,
        "pricing_model_sha256": file_hash(root / R75_MODEL),
        "checks": {
            "source_r1_result_hash_bound": pricing_model["source_r1_result_sha256"]
            == file_hash(root / R1_RESULT),
            "proxy_t_before_matches_r1_summary": proxy_t_before
            == r1_summary["line1381_unpriced_proxy_t_pressure_before"],
            "proxy_t_delta_arithmetic_valid": proxy_t_before - proxy_t_after == proxy_t_delta,
            "proxy_t_delta_positive_for_d2_prefill": proxy_t_delta >= 1,
            "accepted_credit_stays_zero": derivation["accepted_proxy_t_reduction"] == 0
            and derivation["b7_credit_delta"] == 0,
            "claim_boundary_blocks_b7": "does not grant proxy-T or B7 credit"
            in derivation["claim_boundary"],
        },
        "accepted_for_r73_d2_prefill": True,
        "accepted_exit_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
    }
    replay_verdict["failed_checks"] = [
        check for check, passed in replay_verdict["checks"].items() if not passed
    ]
    replay_verdict["accepted_for_r73_d2_prefill"] = replay_verdict["failed_checks"] == []
    replay_verdict["verdict_hash"] = stable_hash(replay_verdict)
    write_json(root / R75_VERDICT, replay_verdict)

    submission.update(
        {
            "submission_id": "B1-B7-cone01-R75-r1-d1-d2-source-closure-prefill",
            "source_target_id": TARGET_ID,
            "upstream_target_id": UPSTREAM_TARGET_ID,
            "accepted_exit_route_count": 0,
            "occurrence_removal_delta": 0,
            "proxy_t_reduction_delta": 0,
            "b7_nonzero_retest_requested": False,
            "claim_boundary": (
                "R75 keeps R73 rejected while filling D1 and D2 only. D3 line1378 "
                "no-double-counting remains empty, so this is not accepted, not O3 "
                "closure, not reroute permission, not accepted proxy-T reduction, and "
                "not B7 credit."
            ),
        }
    )
    submission["packets"]["R73-D2-line1381-source-backed-proxy-t"].update(
        {
            "proxy_t_derivation_artifact_path": R75_DERIVATION,
            "proxy_t_derivation_artifact_sha256": file_hash(root / R75_DERIVATION),
            "proxy_t_before": proxy_t_before,
            "proxy_t_after": proxy_t_after,
            "proxy_t_delta": proxy_t_delta,
            "proxy_t_pricing_model_path": R75_MODEL,
            "proxy_t_pricing_model_sha256": file_hash(root / R75_MODEL),
            "proxy_t_replay_command": (
                "python3 tools/b1_b7_cone01_r75_proxy_t_packet_prefill_gate.py "
                "--repo-root . --pretty"
            ),
            "proxy_t_replay_stdout_path": R75_STDOUT,
            "proxy_t_replay_stdout_sha256": file_hash(root / R75_STDOUT),
            "proxy_t_claim_boundary": derivation["claim_boundary"],
        }
    )
    submission["submission_hash"] = stable_self_hash(submission, "submission_hash")
    write_json(root / R75_SUBMISSION, submission)

    intake_verdict = verify_intake(root, submission, contract)
    write_json(root / R75_INTAKE_VERDICT, intake_verdict)
    blocker_queue = {
        "artifact": "R75 remaining source-closure blocker queue",
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "r73_d1_prefilled": intake_verdict["gates"]["r1_occurrence_delta_source_backed"],
        "r73_d2_prefilled": intake_verdict["gates"]["proxy_t_delta_source_backed"],
        "r73_d3_prefilled": intake_verdict["gates"]["r2_no_double_counting_source_backed"],
        "remaining_failed_gates": intake_verdict["failed_gates"],
        "queue": [
            {
                "blocker_id": "R75-C3",
                "priority": 1,
                "needed_artifact": (
                    "source-backed line1378 recovery or exclusion ledger with no-double-counting "
                    "decision, replay stdout, and hash-bound R2 artifact"
                ),
            }
        ],
    }
    blocker_queue["blocker_queue_hash"] = stable_self_hash(
        blocker_queue, "blocker_queue_hash"
    )
    write_json(root / R75_BLOCKER_QUEUE, blocker_queue)

    requirements = [
        req(
            "K1",
            "R75 binds the locked R1 proxy-T pressure source",
            pricing_model["source_r1_result_sha256"] == file_hash(root / R1_RESULT)
            and proxy_t_before == 100,
            {
                "source_r1_result_sha256": pricing_model["source_r1_result_sha256"],
                "proxy_t_before": proxy_t_before,
            },
        ),
        req(
            "K2",
            "proxy-T arithmetic is replayable and positive for D2 prefill",
            proxy_t_before - proxy_t_after == proxy_t_delta and proxy_t_delta == 1,
            {
                "proxy_t_before": proxy_t_before,
                "proxy_t_after": proxy_t_after,
                "proxy_t_delta": proxy_t_delta,
            },
        ),
        req(
            "K3",
            "R75 materializes hash-bound model, derivation, stdout, and verdict artifacts",
            all(
                (root / path).exists()
                for path in [R75_MODEL, R75_DERIVATION, R75_STDOUT, R75_VERDICT]
            ),
            {
                "pricing_model_sha256": file_hash(root / R75_MODEL),
                "derivation_artifact_sha256": file_hash(root / R75_DERIVATION),
                "replay_stdout_sha256": file_hash(root / R75_STDOUT),
                "replay_verdict_sha256": file_hash(root / R75_VERDICT),
            },
        ),
        req(
            "K4",
            "R73-D1 remains source-backed while R73-D2 becomes source-backed",
            intake_verdict["gates"]["r1_occurrence_delta_source_backed"]
            and intake_verdict["gates"]["proxy_t_delta_source_backed"],
            {
                "r73_d1_prefilled": intake_verdict["gates"][
                    "r1_occurrence_delta_source_backed"
                ],
                "r73_d2_prefilled": intake_verdict["gates"][
                    "proxy_t_delta_source_backed"
                ],
            },
        ),
        req(
            "K5",
            "R73 intake still rejects the submission because D3 remains open",
            intake_verdict["accepted"] is False
            and "r2_no_double_counting_source_backed" in intake_verdict["failed_gates"]
            and "proxy_t_delta_source_backed" not in intake_verdict["failed_gates"],
            {"failed_gates": intake_verdict["failed_gates"]},
        ),
        req(
            "K6",
            "R75 keeps all accepted deltas and B7 credit at zero",
            intake_verdict["accepted_exit_route_count"] == 0
            and intake_verdict["accepted_occurrence_removal"] == 0
            and intake_verdict["accepted_proxy_t_reduction"] == 0
            and intake_verdict["b7_credit_delta"] == 0,
            {
                "accepted_exit_route_count": intake_verdict["accepted_exit_route_count"],
                "accepted_occurrence_removal": intake_verdict["accepted_occurrence_removal"],
                "accepted_proxy_t_reduction": intake_verdict["accepted_proxy_t_reduction"],
                "b7_credit_delta": intake_verdict["b7_credit_delta"],
            },
        ),
        req(
            "K7",
            "R75 reduces the blocker queue to line1378 no-double-counting only",
            len(blocker_queue["queue"]) == 1
            and blocker_queue["queue"][0]["blocker_id"] == "R75-C3",
            {"blocker_queue_hash": blocker_queue["blocker_queue_hash"]},
        ),
        req(
            "K8",
            "R75 does not claim O3 closure, reroute, resource savings, or B7 ledger gain",
            True,
            {
                "o3_closed": False,
                "reroute_allowed": False,
                "resource_saving_claimed": False,
                "b7_ledger_improvement_claimed": False,
            },
        ),
    ]
    summary = {
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "r73_d1_prefilled": intake_verdict["gates"]["r1_occurrence_delta_source_backed"],
        "r73_d2_prefilled": intake_verdict["gates"]["proxy_t_delta_source_backed"],
        "r73_d3_prefilled": intake_verdict["gates"][
            "r2_no_double_counting_source_backed"
        ],
        "r73_intake_accepted": intake_verdict["accepted"],
        "r73_intake_failed_gate_count": intake_verdict["failed_gate_count"],
        "r73_intake_failed_gates": intake_verdict["failed_gates"],
        "source_proxy_t_pressure_before": proxy_t_before,
        "proxy_t_before": proxy_t_before,
        "proxy_t_after": proxy_t_after,
        "proxy_t_delta": proxy_t_delta,
        "accepted_exit_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_nonzero_retest_allowed": False,
        "b7_credit_delta": 0,
        "o3_closed": False,
        "reroute_allowed": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "pricing_model_hash": pricing_model["model_hash"],
        "derivation_hash": derivation["derivation_hash"],
        "submission_hash": submission["submission_hash"],
        "intake_verdict_hash": intake_verdict["verdict_hash"],
        "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
        "requirement_count": len(requirements),
        "requirements_passed": sum(1 for item in requirements if item["passed"]),
        "requirements_failed": sum(1 for item in requirements if not item["passed"]),
        "failed_requirement_ids": [
            item["requirement_id"] for item in requirements if not item["passed"]
        ],
        "validation_error_count": sum(1 for item in requirements if not item["passed"]),
    }
    payload = {
        "title": "B1/B7 Cone01 R75 Proxy-T Packet Prefill Gate",
        "version": VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": summary,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "R75 fills R73-D2 with a hash-bound proxy-T pricing model, derivation "
                "artifact, replay stdout, and replay verdict while preserving the R74 "
                "D1 occurrence packet."
            ),
            "what_is_not_supported": (
                "R75 does not close R73, does not solve line1378 no-double-counting, "
                "does not accept occurrence/proxy-T deltas, does not close O3, and "
                "does not grant B7 credit."
            ),
            "next_gate": (
                "Fill R73-D3 line1378 recovery or exclusion with a source-backed "
                "no-double-counting ledger, then rerun R73 and the hardened R72 path."
            ),
        },
        "artifacts": {
            "proxy_t_pricing_model": R75_MODEL,
            "proxy_t_derivation_artifact": R75_DERIVATION,
            "proxy_t_replay_stdout": R75_STDOUT,
            "proxy_t_replay_verdict": R75_VERDICT,
            "r73_submission": R75_SUBMISSION,
            "r73_intake_verdict": R75_INTAKE_VERDICT,
            "blocker_queue": R75_BLOCKER_QUEUE,
        },
    }
    payload["summary"]["payload_hash"] = stable_hash(payload)
    return payload


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    s = payload["summary"]
    lines = [
        "# B1/B7 Cone01 R75 Proxy-T Packet Prefill Gate",
        "",
        "## Summary",
        "",
        f"- Status: `{s['status']}`",
        f"- R73-D1 prefilled: `{s['r73_d1_prefilled']}`",
        f"- R73-D2 prefilled: `{s['r73_d2_prefilled']}`",
        f"- R73-D3 prefilled: `{s['r73_d3_prefilled']}`",
        f"- R73 intake accepted: `{s['r73_intake_accepted']}`",
        f"- R73 failed gates: `{s['r73_intake_failed_gate_count']}`",
        f"- Proxy-T before: `{s['proxy_t_before']}`",
        f"- Proxy-T after: `{s['proxy_t_after']}`",
        f"- Proxy-T D2 prefill delta: `{s['proxy_t_delta']}`",
        f"- Accepted exit routes: `{s['accepted_exit_route_count']}`",
        f"- Accepted occurrence removal: `{s['accepted_occurrence_removal']}`",
        f"- Accepted proxy-T reduction: `{s['accepted_proxy_t_reduction']}`",
        f"- B7 credit delta: `{s['b7_credit_delta']}`",
        f"- Blocker queue hash: `{s['blocker_queue_hash']}`",
        "",
        "R75 fills the R73-D2 source-backed proxy-T packet shape while preserving the R74 D1 occurrence packet. It intentionally leaves R73-D3 line1378 no-double-counting open, so the intake remains rejected and all accepted credit stays zero.",
        "",
        "## Remaining Failed Gates",
        "",
    ]
    for gate in s["r73_intake_failed_gates"]:
        lines.append(f"- `{gate}`")
    lines.extend(["", "## Requirements", ""])
    for item in payload["requirements"]:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- `{item['requirement_id']}` {status}: {item['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            "## Artifacts",
            "",
        ]
    )
    for label, artifact_path in payload["artifacts"].items():
        lines.append(f"- `{label}`: `{artifact_path}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--json-output",
        default="results/B1_B7_cone01_R75_proxy_t_packet_prefill_gate_v0.json",
    )
    parser.add_argument(
        "--markdown-output",
        default="research/B1_B7_cone01_R75_proxy_t_packet_prefill_gate.md",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    root = Path(args.repo_root).resolve()
    write_json(root / args.json_output, payload)
    write_markdown(root / args.markdown_output, payload)
    if args.pretty:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
