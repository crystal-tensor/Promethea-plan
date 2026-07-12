#!/usr/bin/env python3
"""T-B4-002al/T-B8-003ap: bind R136 artifacts to a private challenge transcript."""

from __future__ import annotations

import argparse
import copy
import hashlib
import hmac
import json
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any

from qiskit import qasm3

from b4_b8_r119_private_observable_bundle_gate import stable_hash, write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


METHOD = "b4_b8_r137_artifact_bound_private_challenge_v0"
STATUS = "artifact_bound_private_challenge_integrity_acceptance_boundary"
MODEL_STATUS = "r136_qasm_cost_and_nonce_bound_with_adversarial_rejection"
TARGET_ID = "T-B4-002al/T-B8-003ap/T-B10-009ad"
UPSTREAM_TARGET_ID = "T-B4-002ak/T-B8-003ao/T-B10-009ac"
R136_RESULT_PATH = "results/B4_B8_R136_route_realization_margin_v0.json"
OUT_DIR = "results/B4_B8_R137_artifact_bound_private_challenge"
RESULT_PATH = "results/B4_B8_R137_artifact_bound_private_challenge_v0.json"
REPORT_PATH = "research/B4_B8_R137_artifact_bound_private_challenge.md"
COMMITMENT_PATH = f"{OUT_DIR}/commitment.json"
REVEAL_PATH = f"{OUT_DIR}/challenge_reveal.json"
CHALLENGES_PATH = f"{OUT_DIR}/challenges.json"
RESPONSES_PATH = f"{OUT_DIR}/responses.json"
TRANSCRIPT_PATH = f"{OUT_DIR}/verifier_transcript.json"
PROBE_TYPES = (
    "byte_range_hash",
    "source_window_hash",
    "operation_count",
    "structural_value",
)
PROTOCOL_NONCE = "r137-artifact-holdout-001"
FORBIDDEN_PRECOMMIT_FIELDS = {
    "challenge_rows",
    "challenge_secret",
    "challenge_secret_hex",
    "response_rows",
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def semantic_record(qasm_text: str) -> dict[str, Any]:
    circuit = qasm3.loads(qasm_text)
    operations = dict(sorted((str(key), int(value)) for key, value in circuit.count_ops().items()))
    record = {
        "num_qubits": circuit.num_qubits,
        "num_clbits": circuit.num_clbits,
        "depth": circuit.depth(),
        "size": circuit.size(),
        "operation_counts": operations,
    }
    record["semantic_fingerprint"] = stable_hash(record)
    return record


def hmac_bytes(secret: bytes, *parts: object) -> bytes:
    message = "|".join(str(part) for part in parts).encode()
    return hmac.new(secret, message, hashlib.sha256).digest()


def deterministic_index(secret: bytes, modulus: int, *parts: object) -> int:
    if modulus <= 0:
        return 0
    return int.from_bytes(hmac_bytes(secret, *parts)[:8], "big") % modulus


def artifact_records(root: Path, r136: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for row in sorted(
        r136["validation_group_rows"], key=lambda item: (item["snapshot"], item["task_id"])
    ):
        relative_path = row["selected_circuit_path"]
        path = root / relative_path
        data = path.read_bytes()
        semantic = semantic_record(data.decode())
        records.append(
            {
                "artifact_id": f"{row['snapshot']}::{row['task_id']}",
                "snapshot": row["snapshot"],
                "task_id": row["task_id"],
                "path": relative_path,
                "sha256": sha256_bytes(data),
                "byte_count": len(data),
                "selected_mapping": row["selected_mapping"],
                "selected_policy_id": row["selected_policy_id"],
                "selected_realization_seed": row["selected_realization_seed"],
                "selected_combined_any_error_proxy": row[
                    "selected_combined_any_error_proxy"
                ],
                **semantic,
            }
        )
    return records


def build_commitment(
    root: Path, r136_path: Path, r136: dict[str, Any], secret_commitment: str
) -> dict[str, Any]:
    summary = r136["summary"]
    artifacts = artifact_records(root, r136)
    return {
        "protocol_id": "B4-B8-R137-artifact-bound-private-challenge-v0",
        "protocol_nonce": PROTOCOL_NONCE,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "r136_result_path": R136_RESULT_PATH,
        "r136_result_sha256": file_sha256(r136_path),
        "r136_payload_hash": r136["payload_hash"],
        "challenge_secret_commitment_sha256": secret_commitment,
        "probe_types": list(PROBE_TYPES),
        "probes_per_artifact": len(PROBE_TYPES),
        "expected_artifact_count": 12,
        "expected_challenge_count": 12 * len(PROBE_TYPES),
        "selection_cost_ledger": {
            "group_count": summary["validation_group_count"],
            "top_candidate_count_per_group": summary["top_candidate_count_per_group"],
            "realization_seed_count": summary["realization_seed_count"],
            "route_realization_compilation_count": summary[
                "route_realization_compilation_count"
            ],
            "automatic_validation_compilation_count": summary[
                "automatic_validation_compilation_count"
            ],
            "total_compilation_count": summary["total_compilation_count"],
            "selection_attempts_per_artifact": summary[
                "top_candidate_count_per_group"
            ]
            * summary["realization_seed_count"],
            "selection_cost_must_be_charged": True,
        },
        "acceptance_contract": {
            "all_artifact_hashes_match": True,
            "all_semantic_fingerprints_match": True,
            "all_challenges_regenerate_from_reveal": True,
            "all_responses_match": True,
            "all_artifacts_receive_every_probe_type": True,
            "selection_cost_ledger_is_exact": True,
            "all_adversarial_mutations_are_rejected": True,
        },
        "artifacts": artifacts,
    }


def challenge_rows(
    commitment: dict[str, Any], commitment_hash: str, secret: bytes
) -> list[dict[str, Any]]:
    rows = []
    for artifact in commitment["artifacts"]:
        artifact_id = artifact["artifact_id"]
        for probe_type in PROBE_TYPES:
            entropy = hmac_bytes(
                secret, commitment_hash, PROTOCOL_NONCE, artifact_id, probe_type
            )
            parameters: dict[str, Any]
            if probe_type == "byte_range_hash":
                length = 32 + entropy[0] % 65
                length = min(length, artifact["byte_count"])
                offset = deterministic_index(
                    secret,
                    artifact["byte_count"] - length + 1,
                    commitment_hash,
                    artifact_id,
                    probe_type,
                    "offset",
                )
                parameters = {"offset": offset, "length": length}
            elif probe_type == "source_window_hash":
                parameters = {
                    "line_index_entropy": int.from_bytes(entropy[:4], "big"),
                    "window_size": 3,
                }
            elif probe_type == "operation_count":
                operation_names = sorted(artifact["operation_counts"])
                operation = operation_names[
                    deterministic_index(
                        secret,
                        len(operation_names),
                        commitment_hash,
                        artifact_id,
                        probe_type,
                    )
                ]
                parameters = {"operation": operation}
            else:
                fields = ["num_qubits", "num_clbits", "depth", "size"]
                field = fields[
                    deterministic_index(
                        secret,
                        len(fields),
                        commitment_hash,
                        artifact_id,
                        probe_type,
                    )
                ]
                parameters = {"field": field}
            core = {
                "protocol_nonce": PROTOCOL_NONCE,
                "commitment_hash": commitment_hash,
                "artifact_id": artifact_id,
                "probe_type": probe_type,
                "parameters": parameters,
            }
            rows.append({"challenge_id": stable_hash(core), **core})
    return rows


def response_value(
    root: Path, artifact: dict[str, Any], challenge: dict[str, Any]
) -> Any:
    data = (root / artifact["path"]).read_bytes()
    parameters = challenge["parameters"]
    probe_type = challenge["probe_type"]
    if probe_type == "byte_range_hash":
        start = parameters["offset"]
        end = start + parameters["length"]
        return sha256_bytes(data[start:end])
    if probe_type == "source_window_hash":
        lines = data.decode().splitlines()
        window_size = min(parameters["window_size"], len(lines))
        start = parameters["line_index_entropy"] % (len(lines) - window_size + 1)
        return {
            "start_line": start,
            "window_sha256": sha256_bytes("\n".join(lines[start : start + window_size]).encode()),
        }
    if probe_type == "operation_count":
        return artifact["operation_counts"].get(parameters["operation"], 0)
    return artifact[parameters["field"]]


def build_responses(
    root: Path, commitment: dict[str, Any], challenges: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    artifacts = {row["artifact_id"]: row for row in commitment["artifacts"]}
    return [
        {
            "challenge_id": challenge["challenge_id"],
            "artifact_id": challenge["artifact_id"],
            "probe_type": challenge["probe_type"],
            "response": response_value(root, artifacts[challenge["artifact_id"]], challenge),
        }
        for challenge in challenges
    ]


def verify(
    root: Path,
    commitment: dict[str, Any],
    expected_commitment_hash: str,
    reveal: dict[str, Any],
    challenges: list[dict[str, Any]],
    responses: list[dict[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    observed_commitment_hash = stable_hash(commitment)
    if observed_commitment_hash != expected_commitment_hash:
        errors.append("commitment_hash_mismatch")
    secret_hex = reveal.get("challenge_secret_hex", "")
    try:
        secret = bytes.fromhex(secret_hex)
    except ValueError:
        secret = b""
        errors.append("challenge_secret_not_hex")
    if sha256_bytes(secret) != commitment.get("challenge_secret_commitment_sha256"):
        errors.append("challenge_secret_commitment_mismatch")
    if reveal.get("protocol_nonce") != commitment.get("protocol_nonce"):
        errors.append("protocol_nonce_mismatch")
    forbidden = sorted(FORBIDDEN_PRECOMMIT_FIELDS & set(commitment))
    if forbidden:
        errors.append("precommit_contains_private_material:" + ",".join(forbidden))

    artifacts = commitment.get("artifacts", [])
    if len(artifacts) != commitment.get("expected_artifact_count"):
        errors.append("artifact_count_mismatch")
    artifact_ids = [row.get("artifact_id") for row in artifacts]
    if len(set(artifact_ids)) != len(artifact_ids):
        errors.append("duplicate_artifact_id")
    for artifact in artifacts:
        path = root / artifact.get("path", "")
        if not path.is_file():
            errors.append(f"artifact_missing:{artifact.get('artifact_id')}")
            continue
        data = path.read_bytes()
        if sha256_bytes(data) != artifact.get("sha256"):
            errors.append(f"artifact_hash_mismatch:{artifact.get('artifact_id')}")
            continue
        observed_semantic = semantic_record(data.decode())
        if observed_semantic["semantic_fingerprint"] != artifact.get(
            "semantic_fingerprint"
        ):
            errors.append(f"semantic_fingerprint_mismatch:{artifact.get('artifact_id')}")

    ledger = commitment.get("selection_cost_ledger", {})
    expected_route = (
        ledger.get("group_count", 0)
        * ledger.get("top_candidate_count_per_group", 0)
        * ledger.get("realization_seed_count", 0)
    )
    if expected_route != 1536 or ledger.get("route_realization_compilation_count") != expected_route:
        errors.append("selection_cost_underreported_or_inconsistent")
    if ledger.get("automatic_validation_compilation_count") != 120:
        errors.append("automatic_validation_cost_mismatch")
    if ledger.get("total_compilation_count") != expected_route + 120:
        errors.append("total_compilation_cost_mismatch")
    if ledger.get("selection_attempts_per_artifact") != 128:
        errors.append("selection_attempts_per_artifact_mismatch")

    regenerated = challenge_rows(commitment, expected_commitment_hash, secret) if secret else []
    if challenges != regenerated:
        errors.append("challenge_regeneration_mismatch")
    if len(challenges) != commitment.get("expected_challenge_count"):
        errors.append("challenge_count_mismatch")
    coverage = Counter((row.get("artifact_id"), row.get("probe_type")) for row in challenges)
    if any(coverage[(artifact_id, probe_type)] != 1 for artifact_id in artifact_ids for probe_type in PROBE_TYPES):
        errors.append("challenge_coverage_mismatch")

    response_by_id = {row.get("challenge_id"): row for row in responses}
    if len(response_by_id) != len(responses) or len(responses) != len(challenges):
        errors.append("response_count_or_uniqueness_mismatch")
    artifact_by_id = {row.get("artifact_id"): row for row in artifacts}
    for challenge in challenges:
        response = response_by_id.get(challenge.get("challenge_id"))
        artifact = artifact_by_id.get(challenge.get("artifact_id"))
        if response is None or artifact is None:
            errors.append(f"missing_response_or_artifact:{challenge.get('challenge_id')}")
            continue
        expected = response_value(root, artifact, challenge)
        if response.get("artifact_id") != challenge.get("artifact_id") or response.get(
            "probe_type"
        ) != challenge.get("probe_type") or response.get("response") != expected:
            errors.append(f"response_mismatch:{challenge.get('challenge_id')}")
    return {
        "accepted": not errors,
        "error_count": len(errors),
        "errors": sorted(set(errors)),
        "observed_commitment_hash": observed_commitment_hash,
        "challenge_count": len(challenges),
        "response_count": len(responses),
        "artifact_count": len(artifacts),
    }


def adversarial_rows(
    root: Path,
    commitment: dict[str, Any],
    commitment_hash: str,
    reveal: dict[str, Any],
    challenges: list[dict[str, Any]],
    responses: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cases = []

    def add(
        attack_id: str,
        mutated_commitment: dict[str, Any] | None = None,
        mutated_reveal: dict[str, Any] | None = None,
        mutated_challenges: list[dict[str, Any]] | None = None,
        mutated_responses: list[dict[str, Any]] | None = None,
    ) -> None:
        verdict = verify(
            root,
            mutated_commitment if mutated_commitment is not None else commitment,
            commitment_hash,
            mutated_reveal if mutated_reveal is not None else reveal,
            mutated_challenges if mutated_challenges is not None else challenges,
            mutated_responses if mutated_responses is not None else responses,
        )
        cases.append(
            {
                "attack_id": attack_id,
                "rejected": not verdict["accepted"],
                "verifier_errors": verdict["errors"],
            }
        )

    mutated = copy.deepcopy(commitment)
    mutated["artifacts"][0]["sha256"] = "0" * 64
    add("post_commit_artifact_hash_substitution", mutated_commitment=mutated)

    swapped = copy.deepcopy(responses)
    swapped[0]["response"], swapped[1]["response"] = swapped[1]["response"], swapped[0]["response"]
    add("cross_challenge_response_swap", mutated_responses=swapped)

    replayed = copy.deepcopy(challenges)
    replayed[0]["protocol_nonce"] = "stale-r136-nonce"
    add("stale_nonce_replay", mutated_challenges=replayed)

    false_reveal = copy.deepcopy(reveal)
    false_reveal["challenge_secret_hex"] = (b"wrong-secret" * 4)[:32].hex()
    add("challenge_secret_substitution", mutated_reveal=false_reveal)

    add("challenge_deletion", mutated_challenges=copy.deepcopy(challenges[:-1]))

    underreported = copy.deepcopy(commitment)
    underreported["selection_cost_ledger"]["route_realization_compilation_count"] = 96
    underreported["selection_cost_ledger"]["total_compilation_count"] = 216
    add("selection_cost_underreporting", mutated_commitment=underreported)

    forged = copy.deepcopy(responses)
    forged[2]["response"] = -1
    add("forged_probe_response", mutated_responses=forged)

    leaked = copy.deepcopy(commitment)
    leaked["challenge_secret_hex"] = reveal["challenge_secret_hex"]
    add("private_material_injected_before_commit", mutated_commitment=leaked)

    omitted = copy.deepcopy(commitment)
    omitted["artifacts"] = omitted["artifacts"][:-1]
    add("artifact_omission", mutated_commitment=omitted)

    duplicate = copy.deepcopy(responses)
    duplicate[-1] = copy.deepcopy(duplicate[0])
    add("duplicate_response_replay", mutated_responses=duplicate)
    return cases


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    requirements = "\n".join(
        f"- `{row['requirement_id']}` {'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    attacks = "\n".join(
        f"- `{row['attack_id']}`: {'REJECTED' if row['rejected'] else 'ACCEPTED'}; "
        f"errors `{', '.join(row['verifier_errors'])}`."
        for row in payload["adversarial_rows"]
    )
    return f"""# B4/B8 R137 Artifact-Bound Private Challenge

## Result

- Frozen R136 QASM artifacts: `{summary['artifact_count']}`
- Late-bound challenges / responses: `{summary['challenge_count']}` / `{summary['response_count']}`
- Probe types: `{summary['probe_type_count']}`
- Positive transcript accepted: `{summary['positive_transcript_accepted']}`
- Adversarial mutations rejected: `{summary['adversarial_mutations_rejected']}` / `{summary['adversarial_mutation_count']}`
- Route-realization search cost disclosed: `{summary['route_realization_compilation_count']}`
- Total compiler calls disclosed: `{summary['total_compilation_count']}`
- Selection attempts per artifact: `{summary['selection_attempts_per_artifact']}`
- Phase artifacts replayed across processes: `{summary['phase_artifact_replay_match_count']}` / `5`
- New credit delta: `0`

R137 binds the exact 12 R136 QASM files, their parsed semantic fingerprints,
the R136 result hash, the 1,536-compilation selection ledger, a secret
commitment, and a protocol nonce before generating 48 private probes. The
secret is revealed only after responses exist inside the local execution, so
the verifier can regenerate every challenge and independently recompute every
response.

## Adversarial Pressure

{attacks}

## Requirements

{requirements}

## Claim Boundary

Supported: local artifact-integrity verifier acceptance for a commit-challenge-
response-reveal transcript that binds all 12 R136 QASM artifacts and charges the
full compiler-selection ledger. Not supported: externally timestamped
preregistration, independent secret custody, statistical performance
acceptance, device calibration, hardware execution, protocol or cryptographic
soundness, sampling hardness, quantum advantage, BQP separation, or new B10
credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    r136_path = root / R136_RESULT_PATH
    r136 = json.loads(r136_path.read_text(encoding="utf-8"))
    if r136.get("status") != "route_realization_lower_tail_margin_boundary":
        raise ValueError("R137 requires the accepted R136 route-realization boundary")
    if not r136["summary"].get("automatic_baseline_no_loss_gate_passed"):
        raise ValueError("R137 requires the R136 compiler no-loss gate")

    output = root / OUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    phase_paths = [
        root / COMMITMENT_PATH,
        root / REVEAL_PATH,
        root / CHALLENGES_PATH,
        root / RESPONSES_PATH,
        root / TRANSCRIPT_PATH,
    ]
    preexisting = {str(path): path.read_bytes() for path in phase_paths if path.exists()}
    reveal_path = root / REVEAL_PATH
    if reveal_path.exists():
        prior_reveal = json.loads(reveal_path.read_text(encoding="utf-8"))
        secret = bytes.fromhex(prior_reveal["challenge_secret_hex"])
    else:
        secret = os.urandom(32)
    secret_commitment = sha256_bytes(secret)
    commitment = build_commitment(root, r136_path, r136, secret_commitment)
    commitment_hash = stable_hash(commitment)
    write_json(
        root / COMMITMENT_PATH,
        {"commitment_hash": commitment_hash, "commitment": commitment},
    )
    challenges = challenge_rows(commitment, commitment_hash, secret)
    write_json(
        root / CHALLENGES_PATH,
        {"commitment_hash": commitment_hash, "challenge_rows": challenges},
    )
    responses = build_responses(root, commitment, challenges)
    write_json(
        root / RESPONSES_PATH,
        {"commitment_hash": commitment_hash, "response_rows": responses},
    )
    reveal = {
        "protocol_nonce": PROTOCOL_NONCE,
        "commitment_hash": commitment_hash,
        "challenge_secret_commitment_sha256": secret_commitment,
        "challenge_secret_hex": secret.hex(),
        "reveal_purpose": "post_response_challenge_regeneration",
    }
    write_json(root / REVEAL_PATH, reveal)
    positive = verify(root, commitment, commitment_hash, reveal, challenges, responses)
    attacks = adversarial_rows(
        root, commitment, commitment_hash, reveal, challenges, responses
    )
    transcript = {
        "protocol_id": commitment["protocol_id"],
        "commitment_hash": commitment_hash,
        "positive_verdict": positive,
        "adversarial_verdicts": attacks,
        "verifier_acceptance_scope": "artifact_integrity_only",
    }
    write_json(root / TRANSCRIPT_PATH, transcript)
    replay_matches = sum(
        path.read_bytes() == preexisting.get(str(path), b"") for path in phase_paths
    )

    probe_counts = Counter(row["probe_type"] for row in challenges)
    summary = {
        "artifact_count": len(commitment["artifacts"]),
        "artifact_hash_match_count": sum(
            file_sha256(root / row["path"]) == row["sha256"]
            for row in commitment["artifacts"]
        ),
        "semantic_fingerprint_match_count": sum(
            semantic_record((root / row["path"]).read_text(encoding="utf-8"))[
                "semantic_fingerprint"
            ]
            == row["semantic_fingerprint"]
            for row in commitment["artifacts"]
        ),
        "challenge_count": len(challenges),
        "response_count": len(responses),
        "probe_type_count": len(PROBE_TYPES),
        "probe_counts": dict(sorted(probe_counts.items())),
        "positive_transcript_accepted": positive["accepted"],
        "positive_transcript_error_count": positive["error_count"],
        "adversarial_mutation_count": len(attacks),
        "adversarial_mutations_rejected": sum(row["rejected"] for row in attacks),
        "route_realization_compilation_count": commitment["selection_cost_ledger"][
            "route_realization_compilation_count"
        ],
        "automatic_validation_compilation_count": commitment[
            "selection_cost_ledger"
        ]["automatic_validation_compilation_count"],
        "total_compilation_count": commitment["selection_cost_ledger"][
            "total_compilation_count"
        ],
        "selection_attempts_per_artifact": commitment["selection_cost_ledger"][
            "selection_attempts_per_artifact"
        ],
        "selection_to_validation_cost_ratio": commitment["selection_cost_ledger"][
            "route_realization_compilation_count"
        ]
        / commitment["selection_cost_ledger"]["automatic_validation_compilation_count"],
        "phase_artifact_count": len(phase_paths),
        "phase_artifact_preexisting_count": len(preexisting),
        "phase_artifact_replay_match_count": replay_matches,
        "private_until_response_within_local_execution": True,
        "artifact_integrity_private_challenge_executed": True,
        "artifact_integrity_verifier_accepted": positive["accepted"],
        "selection_cost_ledger_bound": True,
        "scientific_performance_holdout_executed": False,
        "externally_timestamped_preregistration": False,
        "independent_secret_custody": False,
        "current_backend_calibration_used": False,
        "hardware_execution_performed": False,
        "protocol_soundness_claimed": False,
        "cryptographic_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    requirements = [
        ("P1", "R136 no-loss source and payload are hash-bound", r136["source_target_id"] == UPSTREAM_TARGET_ID and bool(commitment["r136_result_sha256"])),
        ("P2", "all 12 exact QASM artifacts and semantic fingerprints match", summary["artifact_hash_match_count"] == 12 and summary["semantic_fingerprint_match_count"] == 12),
        ("P3", "secret commitment and protocol nonce precede challenge generation", positive["accepted"] and commitment["challenge_secret_commitment_sha256"] == secret_commitment),
        ("P4", "48 late-bound challenges cover four probe types on every artifact", len(challenges) == 48 and all(probe_counts[kind] == 12 for kind in PROBE_TYPES)),
        ("P5", "all challenge responses independently recompute", positive["accepted"] and positive["error_count"] == 0),
        ("P6", "full 1,536-selection and 1,656-total cost ledger is bound", summary["route_realization_compilation_count"] == 1536 and summary["total_compilation_count"] == 1656 and summary["selection_attempts_per_artifact"] == 128),
        ("P7", "all ten adversarial transcript mutations are rejected", summary["adversarial_mutations_rejected"] == 10),
        ("P8", "all five phase artifacts replay identically in a fresh process", summary["phase_artifact_preexisting_count"] == 5 and summary["phase_artifact_replay_match_count"] == 5),
        ("P9", "acceptance is restricted to local artifact integrity", summary["artifact_integrity_verifier_accepted"] and not summary["scientific_performance_holdout_executed"] and not summary["externally_timestamped_preregistration"] and not summary["independent_secret_custody"]),
        ("P10", "hardware, soundness, advantage, BQP, and new credit remain excluded", not summary["hardware_execution_performed"] and not summary["protocol_soundness_claimed"] and not summary["cryptographic_soundness_claimed"] and not summary["quantum_advantage_claimed"] and not summary["bqp_separation_claimed"] and summary["new_credit_delta"] == 0),
    ]
    requirement_rows = [
        {"requirement_id": identifier, "label": label, "passed": passed}
        for identifier, label, passed in requirements
    ]
    failed = [row["requirement_id"] for row in requirement_rows if not row["passed"]]
    payload: dict[str, Any] = {
        "title": "B4/B8 R137 artifact-bound private challenge",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "commitment_hash": commitment_hash,
        "requirements": requirement_rows,
        "requirement_count": len(requirement_rows),
        "requirements_passed": len(requirement_rows) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
        "summary": summary,
        "commitment": commitment,
        "challenge_rows": challenges,
        "response_rows": responses,
        "positive_verifier_transcript": positive,
        "adversarial_rows": attacks,
        "artifacts": {
            "r136_result": R136_RESULT_PATH,
            "commitment": COMMITMENT_PATH,
            "challenge_reveal": REVEAL_PATH,
            "challenges": CHALLENGES_PATH,
            "responses": RESPONSES_PATH,
            "verifier_transcript": TRANSCRIPT_PATH,
        },
        "claim_boundary": {
            "what_is_supported": "Local artifact-integrity acceptance for a nonce-bound commit-challenge-response-reveal transcript covering all R136 QASM files and the complete selection-cost ledger.",
            "what_is_not_supported": "External preregistration, independent secret custody, statistical performance acceptance, current calibration, hardware execution, protocol or cryptographic soundness, quantum advantage, BQP separation, or new B10 credit.",
            "next_gate": "Give the commitment hash to an independent verifier before that verifier privately samples a statistical performance challenge over the frozen QASM bundle.",
        },
    }
    payload["payload_hash"] = stable_hash(payload)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    payload = run_gate(args.root)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
