#!/usr/bin/env python3
"""T-B1-004eb/T-B7-013k: R26 O3-F4 near-miss refit sentinel gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r26_o3_f4_near_miss_refit_sentinel_gate_v0"
STATUS = "cone01_r26_o3_f4_near_miss_refit_sentinel_rejected"
MODEL_STATUS = "o3_f4_near_miss_refit_rejected_on_core_science_gates_no_o3_no_reroute"
VERSION = "0.1"
TARGET_ID = "T-B1-004eb/T-B7-013k"
SOURCE_TARGET_ID = "T-B1-004ea/T-B7-013j"
CANDIDATE_ID = "NL-C02"
FAMILY_ID = "O3-F4"
SENTINEL_ID = "B1-B7-cone01-R26-O3-F4-near-miss-refit-sentinel"
EXPECTED_PASSED_GATES = ["F4-A1", "F4-A3", "F4-A4", "F4-A8", "F4-A9"]
EXPECTED_FAILED_GATES = ["F4-A2", "F4-A5", "F4-A6", "F4-A7"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_hash(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def requirement(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"requirement_id": requirement_id, "label": label, "passed": bool(passed), "evidence": evidence}


def build_near_miss_fixture(challenge_packet: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    challenge_ids = [row["challenge_id"] for row in challenge_packet["challenge_rows"]]
    tolerance = challenge_packet["exact_unitary_tolerance"]
    replay_rows = []
    for index, challenge_id in enumerate(challenge_ids, start=1):
        replay_rows.append(
            {
                "challenge_id": challenge_id,
                "claimed_replay_passed": True,
                "unitary_replay_error": tolerance * (1.0 + 0.1 * index),
                "tolerance": tolerance,
                "redteam_note": "near miss: every replay error is just above the exact tolerance",
            }
        )
    return {
        "artifact_id": "B1-B7-cone01-O3-F4-numerical-refit-redteam-near-miss-sentinel",
        "source_target_id": TARGET_ID,
        "family_id": FAMILY_ID,
        "candidate_id": CANDIDATE_ID,
        "source_domain_hash": template["source_domain_hash"],
        "source_registry_hash": template["source_registry_hash"],
        "source_enforced_replay_hash": template["source_enforced_replay_hash"],
        "challenge_packet_hash": template["challenge_packet_hash"],
        "refit_objective": {
            "status": "claimed",
            "objective": "same_unitary_refit_with_route_a_clearance_pressure",
            "loss_terms": ["unitary_replay_error", "pi_over_four_lattice_distance", "route_a_effect"],
        },
        "unitary_replay_protocol": {
            "status": "claimed_near_pass",
            "tolerance": tolerance,
            "required_replay_cases": challenge_ids,
            "replay_rows": replay_rows,
            "max_unitary_replay_error": max(row["unitary_replay_error"] for row in replay_rows),
        },
        "seed_schedule": {
            "status": "all_declared_seeds_used",
            "challenge_ids": challenge_ids,
            "external_randomness_allowed": False,
            "hidden_restart_count": 0,
        },
        "optimizer_trace": {
            "status": "trace_present_but_leaky",
            "reported_step_count": 512,
            "hidden_restart_count": 0,
            "challenge_packet_visible_to_optimizer": True,
            "leakage_note": "near-miss fixture discloses trace but still tunes after seeing challenge rows",
        },
        "equivalence_certificate": {
            "certificate_type": "replay_rows_plus_symbolic_note",
            "pi_over_four_snap": False,
            "same_unitary_replay_certificate": None,
            "denominator_comparison": {
                "status": "partial",
                "same_access_model": False,
                "covered_r11_r12_rows": 8,
                "required_r11_r12_rows": 31,
            },
        },
        "route_a_effect": "does_not_clear_route_a",
        "claim_boundary": {
            "supported": "near-miss diagnostic only; no O3 closure, reroute, B7 credit, or STV credit is supported",
            "not_supported": "B7 credit, STV credit, reroute, O3 closure, and R1 solution are not supported.",
            "kill_conditions": ["same-unitary replay exceeds tolerance", "denominator comparison incomplete", "optimizer leakage"],
        },
        "machine_check_command": "python3 tools/b1_b7_cone01_r26_o3_f4_near_miss_refit_sentinel_gate.py --pretty",
        "expected_outputs": {
            "challenge_packet_hash": template["challenge_packet_hash"],
            "artifact_hash": "<computed-by-r26>",
            "checker_stdout_hash": "<computed-by-r26>",
        },
        "checked_negative_lemma_present": False,
        "reroute_allowed": False,
        "o3_closed": False,
        "b7_credit_delta": 0,
    }


def evaluate_fixture(fixture: dict[str, Any], challenge_packet: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    passed: list[str] = []
    failed: list[str] = []
    required_fields = [
        "artifact_id",
        "source_target_id",
        "family_id",
        "candidate_id",
        "source_domain_hash",
        "source_registry_hash",
        "source_enforced_replay_hash",
        "challenge_packet_hash",
        "refit_objective",
        "unitary_replay_protocol",
        "seed_schedule",
        "optimizer_trace",
        "equivalence_certificate",
        "route_a_effect",
        "claim_boundary",
        "machine_check_command",
        "expected_outputs",
    ]
    missing = [field for field in required_fields if field not in fixture]

    if all(
        [
            fixture.get("family_id") == FAMILY_ID,
            fixture.get("candidate_id") == CANDIDATE_ID,
            fixture.get("source_domain_hash") == template["source_domain_hash"],
            fixture.get("source_registry_hash") == template["source_registry_hash"],
            fixture.get("source_enforced_replay_hash") == template["source_enforced_replay_hash"],
            fixture.get("challenge_packet_hash") == template["challenge_packet_hash"],
        ]
    ):
        passed.append("F4-A1")
    else:
        failed.append("F4-A1")

    replay_rows = fixture.get("unitary_replay_protocol", {}).get("replay_rows", [])
    tolerance = challenge_packet["exact_unitary_tolerance"]
    max_error = max((row.get("unitary_replay_error", float("inf")) for row in replay_rows), default=float("inf"))
    (passed if replay_rows and max_error <= tolerance else failed).append("F4-A2")

    challenge_ids = [row["challenge_id"] for row in challenge_packet["challenge_rows"]]
    seeds = fixture.get("seed_schedule", {})
    (passed if sorted(seeds.get("challenge_ids", [])) == sorted(challenge_ids) and seeds.get("external_randomness_allowed") is False and seeds.get("hidden_restart_count", 0) == 0 else failed).append("F4-A3")

    (passed if fixture.get("route_a_effect") in {"not_claimed", "does_not_clear_route_a"} else failed).append("F4-A4")

    cert = fixture.get("equivalence_certificate", {})
    (passed if cert.get("same_unitary_replay_certificate") and cert.get("certificate_type") != "numerical_only" else failed).append("F4-A5")

    denom = cert.get("denominator_comparison") or {}
    (passed if denom.get("status") == "complete" and denom.get("same_access_model") is True and denom.get("covered_r11_r12_rows") == denom.get("required_r11_r12_rows") else failed).append("F4-A6")

    trace = fixture.get("optimizer_trace", {})
    (passed if trace.get("challenge_packet_visible_to_optimizer") is False and trace.get("hidden_restart_count", 0) == 0 else failed).append("F4-A7")

    boundary_text = json.dumps(fixture.get("claim_boundary", {}), sort_keys=True).lower()
    (passed if "not supported" in boundary_text and fixture.get("reroute_allowed") is False and fixture.get("o3_closed") is False and fixture.get("b7_credit_delta", 0) == 0 else failed).append("F4-A8")

    (passed if fixture.get("machine_check_command") and fixture.get("expected_outputs") else failed).append("F4-A9")

    return {
        "submission_exists": True,
        "missing_required_fields": missing,
        "passed_gate_ids": passed,
        "failed_gate_ids": failed,
        "blocked_gate_ids": [],
        "accepted": not missing and len(failed) == 0 and len(passed) == 9,
        "max_unitary_replay_error": max_error,
        "unitary_tolerance": tolerance,
        "why": "Near-miss sentinel should pass surface hygiene but fail core same-unitary, certificate, denominator, and leakage gates.",
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r24 = load_json(args.r24_harness)
    r25 = load_json(args.r25_sentinel)
    challenge_packet = load_json(args.challenge_packet)
    template = load_json(args.template)
    fixture = build_near_miss_fixture(challenge_packet, template)
    fixture_hash = stable_hash(fixture)
    preflight = evaluate_fixture(fixture, challenge_packet, template)
    preflight_hash = stable_hash(preflight)
    sentinel_packet = {
        "sentinel_id": SENTINEL_ID,
        "source_target_id": TARGET_ID,
        "source_r24_harness": str(args.r24_harness),
        "source_r25_sentinel": str(args.r25_sentinel),
        "source_challenge_packet": str(args.challenge_packet),
        "source_template": str(args.template),
        "source_hashes": {
            "r24_harness_file": file_hash(args.r24_harness),
            "r25_sentinel_file": file_hash(args.r25_sentinel),
            "challenge_packet_file": file_hash(args.challenge_packet),
            "template_file": file_hash(args.template),
        },
        "source_harness_hash": r24["summary"]["harness_hash"],
        "source_r25_sentinel_hash": r25["summary"]["sentinel_hash"],
        "source_challenge_packet_hash": r24["summary"]["challenge_packet_hash"],
        "source_template_hash": r24["summary"]["template_hash"],
        "fixture_output": str(args.fixture_output),
        "near_miss_fixture": fixture,
        "near_miss_fixture_hash": fixture_hash,
        "preflight_result": preflight,
        "preflight_hash": preflight_hash,
        "expected_passed_gate_ids": EXPECTED_PASSED_GATES,
        "expected_failed_gate_ids": EXPECTED_FAILED_GATES,
        "decision": {
            "o3_f4_near_miss_sentinel_ready": True,
            "near_miss_fixture_emitted": True,
            "near_miss_fixture_has_all_required_fields": len(preflight["missing_required_fields"]) == 0,
            "near_miss_fixture_rejected": preflight["accepted"] is False,
            "passes_more_gates_than_r25": len(preflight["passed_gate_ids"]) > len(r25["summary"]["preflight_passed_gate_ids"]),
            "o3_f4_artifact_accepted": False,
            "o3_closed": False,
            "checked_negative_lemma_present": False,
            "nlc02_full_lemma_ready": False,
            "reroute_allowed": False,
            "why": "R26 proves R24 still rejects a stronger near-miss O3-F4 refit that passes surface gates.",
        },
    }
    sentinel_packet["sentinel_hash"] = stable_hash(sentinel_packet)

    requirements = [
        requirement("S1", "R24 harness and R25 sentinel are validation-clean sources", r24["summary"].get("validation_error_count") == 0 and r25["summary"].get("validation_error_count") == 0, {"r24_validation_error_count": r24["summary"].get("validation_error_count"), "r25_validation_error_count": r25["summary"].get("validation_error_count")}),
        requirement("S2", "Near-miss fixture carries all required O3-F4 fields", len(preflight["missing_required_fields"]) == 0, {"missing_required_fields": preflight["missing_required_fields"]}),
        requirement("S3", "Near-miss fixture passes more gates than R25", len(preflight["passed_gate_ids"]) > len(r25["summary"]["preflight_passed_gate_ids"]), {"r25_passed": r25["summary"]["preflight_passed_gate_ids"], "r26_passed": preflight["passed_gate_ids"]}),
        requirement("S4", "Near-miss fixture passes source, seed, Route A, claim-boundary, and machine-check surface gates", preflight["passed_gate_ids"] == EXPECTED_PASSED_GATES, {"expected_passed_gate_ids": EXPECTED_PASSED_GATES, "actual_passed_gate_ids": preflight["passed_gate_ids"]}),
        requirement("S5", "Same-unitary replay remains rejected despite near tolerance", "F4-A2" in preflight["failed_gate_ids"] and preflight["max_unitary_replay_error"] > preflight["unitary_tolerance"], {"max_unitary_replay_error": preflight["max_unitary_replay_error"], "unitary_tolerance": preflight["unitary_tolerance"]}),
        requirement("S6", "Certificate, denominator, and leakage core gates reject the fixture", {"F4-A5", "F4-A6", "F4-A7"}.issubset(set(preflight["failed_gate_ids"])), {"failed_gate_ids": preflight["failed_gate_ids"], "equivalence_certificate": fixture["equivalence_certificate"], "optimizer_trace": fixture["optimizer_trace"]}),
        requirement("S7", "Failed gate set is exactly the stronger near-miss profile", preflight["failed_gate_ids"] == EXPECTED_FAILED_GATES, {"expected_failed_gate_ids": EXPECTED_FAILED_GATES, "actual_failed_gate_ids": preflight["failed_gate_ids"]}),
        requirement("S8", "R26 rejects the fixture without accepting O3-F4, closing O3, or permitting reroute", preflight["accepted"] is False and sentinel_packet["decision"]["o3_f4_artifact_accepted"] is False and sentinel_packet["decision"]["o3_closed"] is False and sentinel_packet["decision"]["reroute_allowed"] is False, {"preflight_accepted": preflight["accepted"], "decision": sentinel_packet["decision"]}),
        requirement("S9", "R26 preserves zero B7/resource credit claims", True, {"accepted_route_count": 0, "accepted_occurrence_removal": 0, "accepted_proxy_t_reduction": 0, "b7_credit_delta": 0, "b7_space_time_volume_credit": 0, "resource_saving_claimed": False}),
        requirement("S10", "Sentinel packet is internally hash-bound", bool(sentinel_packet["sentinel_hash"]) and bool(fixture_hash) and bool(preflight_hash), {"sentinel_hash": sentinel_packet["sentinel_hash"], "near_miss_fixture_hash": fixture_hash, "preflight_hash": preflight_hash}),
    ]
    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors = [f"unexpected R26 O3-F4 near-miss failures: {failed_ids}"] if failed_ids else []
    summary = {
        "sentinel_id": SENTINEL_ID,
        "sentinel_hash": sentinel_packet["sentinel_hash"],
        "near_miss_fixture_hash": fixture_hash,
        "preflight_hash": preflight_hash,
        "source_harness_hash": r24["summary"]["harness_hash"],
        "source_r25_sentinel_hash": r25["summary"]["sentinel_hash"],
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "expected_passed_gate_ids": EXPECTED_PASSED_GATES,
        "expected_failed_gate_ids": EXPECTED_FAILED_GATES,
        "preflight_passed_gate_ids": preflight["passed_gate_ids"],
        "preflight_failed_gate_ids": preflight["failed_gate_ids"],
        "near_miss_fixture_has_all_required_fields": len(preflight["missing_required_fields"]) == 0,
        "near_miss_fixture_rejected": preflight["accepted"] is False,
        "passes_more_gates_than_r25": len(preflight["passed_gate_ids"]) > len(r25["summary"]["preflight_passed_gate_ids"]),
        "max_unitary_replay_error": preflight["max_unitary_replay_error"],
        "unitary_tolerance": preflight["unitary_tolerance"],
        "o3_f4_artifact_accepted": False,
        "o3_closed": False,
        "remaining_open_obligations": ["O3-F3_symbolic_lu_artifact", "O3-F4_valid_refit_artifact", "O3-F5_route_a_artifact"],
        "remaining_open_obligation_count": 3,
        "checked_negative_lemma_present": False,
        "nlc02_full_lemma_ready": False,
        "reroute_allowed": False,
        "accepted_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "source_target_id": TARGET_ID,
        "upstream_target_id": SOURCE_TARGET_ID,
        "title": "B1/B7 Cone01 R26 O3-F4 Near-Miss Refit Sentinel Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "summary": summary,
        "o3_f4_near_miss_refit_sentinel_packet": sentinel_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": "R26 emits a stronger near-miss O3-F4 refit fixture that passes surface gates but is rejected by same-unitary, certificate, denominator, and leakage gates.",
            "what_is_not_supported": "R26 does not submit or accept a valid O3-F4 refit artifact, does not close O3, and does not permit R5 reroute. No B7 credit or resource saving is supported.",
            "next_gate": "Submit a valid O3-F4 refit artifact that passes F4-A1..F4-A9, or design an even stronger adversarial fixture.",
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        f"# {payload['title']}",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Sentinel hash: `{s['sentinel_hash']}`",
        f"- Near-miss fixture hash: `{s['near_miss_fixture_hash']}`",
        f"- Preflight hash: `{s['preflight_hash']}`",
        "",
        "## Result",
        "",
        f"R26 passes {s['requirements_passed']}/{s['requirement_count']} requirements. It rejects a stronger near-miss O3-F4 fixture that passes more gates than R25.",
        "",
        "## Rejection Profile",
        "",
        f"- Passed gates: `{s['preflight_passed_gate_ids']}`",
        f"- Failed gates: `{s['preflight_failed_gate_ids']}`",
        f"- Max unitary replay error: `{s['max_unitary_replay_error']}`",
        f"- Unit tolerance: `{s['unitary_tolerance']}`",
        "",
        "## Requirement Results",
        "",
    ]
    for row in payload["requirements"]:
        lines.append(f"- `{row['requirement_id']}` {'PASS' if row['passed'] else 'FAIL'}: {row['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            f"- validation_error_count: `{s['validation_error_count']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r24-harness", type=Path, default=Path("results/B1_B7_cone01_R24_o3_f4_numerical_refit_harness_gate_v0.json"))
    parser.add_argument("--r25-sentinel", type=Path, default=Path("results/B1_B7_cone01_R25_o3_f4_adversarial_refit_sentinel_gate_v0.json"))
    parser.add_argument("--challenge-packet", type=Path, default=Path("results/B1_B7_cone01_o3_f4_numerical_refit_submissions/B1-B7-cone01-O3-F4-challenge-packet.json"))
    parser.add_argument("--template", type=Path, default=Path("results/B1_B7_cone01_o3_f4_numerical_refit_submissions/B1-B7-cone01-O3-F4-refit.template.json"))
    parser.add_argument("--fixture-output", type=Path, default=Path("results/B1_B7_cone01_o3_f4_numerical_refit_submissions/B1-B7-cone01-O3-F4-refit.near-miss-sentinel.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B1_B7_cone01_R26_o3_f4_near_miss_refit_sentinel_gate_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_B7_cone01_R26_o3_f4_near_miss_refit_sentinel_gate.md"))
    parser.add_argument("--last-updated", default="2026-07-08")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args)
    write_json(args.fixture_output, payload["o3_f4_near_miss_refit_sentinel_packet"]["near_miss_fixture"], args.pretty)
    write_json(args.json_output, payload, args.pretty)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "sentinel_hash": payload["summary"]["sentinel_hash"],
        "near_miss_fixture_hash": payload["summary"]["near_miss_fixture_hash"],
        "preflight_hash": payload["summary"]["preflight_hash"],
        "passed_gate_ids": payload["summary"]["preflight_passed_gate_ids"],
        "failed_gate_ids": payload["summary"]["preflight_failed_gate_ids"],
        "passes_more_gates_than_r25": payload["summary"]["passes_more_gates_than_r25"],
        "o3_f4_artifact_accepted": payload["summary"]["o3_f4_artifact_accepted"],
        "o3_closed": payload["summary"]["o3_closed"],
        "reroute_allowed": payload["summary"]["reroute_allowed"],
        "requirements_passed": payload["summary"]["requirements_passed"],
        "requirements_failed": payload["summary"]["requirements_failed"],
        "validation_error_count": payload["summary"]["validation_error_count"],
        "fixture_output": str(args.fixture_output),
        "json_output": str(args.json_output),
        "markdown_output": str(args.markdown_output),
    }, indent=2, sort_keys=True))
    if payload["validation_errors"]:
        raise SystemExit("B1/B7 R26 O3-F4 near-miss sentinel validation failed")


if __name__ == "__main__":
    main()
