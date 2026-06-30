#!/usr/bin/env python3
"""Check whether B4/B8 fitted spoofer evidence is ready for real-backend transcript claims."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b4_b8_real_backend_transcript_readiness_gate_v0"
STATUS = "real_backend_transcript_readiness_failed"
MODEL_STATUS = "synthetic_fitted_spoofer_and_generic_backend_bridge_not_real_backend_transcripts"
VERSION = "0.1"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(
        payload,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        sort_keys=True,
    )
    path.write_text(text + "\n", encoding="utf-8")


def readiness_gate(
    gate_id: str,
    label: str,
    passed: bool,
    evidence: dict[str, Any],
    missing_to_promote: str,
) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
        "missing_to_promote": missing_to_promote,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    fitted = load_json(args.fitted_spoofer_result)
    backend = load_json(args.backend_calibrated_bridge_result)

    real_backend_properties_used = bool(fitted["real_backend_properties_used"]) or bool(
        backend["real_backend_properties_used"]
    )
    hardware_execution_performed = bool(fitted["hardware_execution_performed"]) or bool(
        backend["hardware_execution_performed"]
    )
    real_backend_transcript_rows = 0
    leakage_separated_real_training_performed = (
        real_backend_transcript_rows > 0
        and bool(fitted["actual_fitted_training_performed"])
        and real_backend_properties_used
    )

    forbidden_claims = [
        bool(fitted["quantum_advantage_claimed"]),
        bool(fitted["bqp_separation_claimed"]),
        bool(fitted["sampling_hardness_proved"]),
        bool(fitted["cryptographic_soundness_proved"]),
        bool(fitted["protocol_soundness_proved"]),
        not bool(backend["explicit_not_bqp_separation"]),
        bool(backend["sampling_hardness_proved"]),
    ]

    gates = [
        readiness_gate(
            "R1",
            "Synthetic private-challenge transcript bridge is present",
            int(fitted["source_transcript_case_count"]) == 720,
            {
                "source_transcript_case_count": fitted["source_transcript_case_count"],
                "source_method": fitted["source_method"],
            },
            "Keep the synthetic bridge as a control denominator for real transcripts.",
        ),
        readiness_gate(
            "R2",
            "Fitted train/holdout diagnostic is present",
            int(fitted["train_row_count"]) == 560
            and int(fitted["holdout_row_count"]) == 160
            and int(fitted["fitted_evaluation_row_count"]) == 640,
            {
                "train_row_count": fitted["train_row_count"],
                "holdout_row_count": fitted["holdout_row_count"],
                "fitted_evaluation_row_count": fitted["fitted_evaluation_row_count"],
                "actual_fitted_training_performed": fitted[
                    "actual_fitted_training_performed"
                ],
            },
            "Reuse the same split discipline on real-backend or hardware transcripts.",
        ),
        readiness_gate(
            "R3",
            "GenericBackendV2 calibrated Aer bridge exists",
            bool(backend["qiskit_generic_backend_v2_used"])
            and int(backend["backend_calibrated_aer_circuit_count"]) == 5760
            and bool(backend["backend_calibrated_noise_parameters_instantiated"]),
            {
                "qiskit_generic_backend_v2_used": backend["qiskit_generic_backend_v2_used"],
                "backend_calibrated_aer_circuit_count": backend[
                    "backend_calibrated_aer_circuit_count"
                ],
                "backend_calibrated_noise_parameters_instantiated": backend[
                    "backend_calibrated_noise_parameters_instantiated"
                ],
                "minimum_safe_calibrated_honest_acceptance": backend[
                    "minimum_safe_calibrated_honest_acceptance"
                ],
                "maximum_safe_calibrated_adversary_acceptance": backend[
                    "maximum_safe_calibrated_adversary_acceptance"
                ],
            },
            "Replace GenericBackendV2-style simulated calibration with real backend properties.",
        ),
        readiness_gate(
            "R4",
            "Private-safe no-leak fitted acceptance stays below 0.10",
            bool(fitted["private_safe_no_leak_passes_0p10"])
            and float(fitted["private_safe_max_no_leak_fitted_acceptance"]) <= 0.10,
            {
                "private_safe_max_no_leak_fitted_acceptance": fitted[
                    "private_safe_max_no_leak_fitted_acceptance"
                ],
                "private_safe_backend_like_refreshed_no_leak_fitted_acceptance": fitted[
                    "private_safe_backend_like_refreshed_no_leak_fitted_acceptance"
                ],
            },
            "Re-test this margin on real-backend leakage-separated holdout rows.",
        ),
        readiness_gate(
            "R5",
            "Real backend properties are used",
            real_backend_properties_used,
            {
                "fitted_real_backend_properties_used": fitted["real_backend_properties_used"],
                "bridge_real_backend_properties_used": backend["real_backend_properties_used"],
            },
            "Attach backend properties from an actual device snapshot or provider calibration export.",
        ),
        readiness_gate(
            "R6",
            "Hardware execution is performed",
            hardware_execution_performed,
            {
                "fitted_hardware_execution_performed": fitted[
                    "hardware_execution_performed"
                ],
                "bridge_hardware_execution_performed": backend[
                    "hardware_execution_performed"
                ],
            },
            "Run randomized-measurement circuits on hardware or independently supplied hardware traces.",
        ),
        readiness_gate(
            "R7",
            "Leakage-separated fitted training uses real transcripts",
            leakage_separated_real_training_performed,
            {
                "real_backend_transcript_rows": real_backend_transcript_rows,
                "actual_fitted_training_performed": fitted[
                    "actual_fitted_training_performed"
                ],
                "real_backend_properties_used": real_backend_properties_used,
            },
            "Train and hold out leakage-separated spoofers on real-backend or hardware transcript rows.",
        ),
        readiness_gate(
            "R8",
            "Leakage-blind no-leak fitted acceptance is below 0.10",
            float(fitted["leakage_blind_max_no_leak_fitted_acceptance"]) <= 0.10,
            {
                "leakage_blind_max_no_leak_fitted_acceptance": fitted[
                    "leakage_blind_max_no_leak_fitted_acceptance"
                ],
                "leakage_blind_mixture_fails_no_leak_0p10": fitted[
                    "leakage_blind_mixture_fails_no_leak_0p10"
                ],
            },
            "Separate leakage regimes or redesign private predicates so leakage-blind training cannot lift no-leak acceptance.",
        ),
        readiness_gate(
            "R9",
            "Full private-material leakage is bounded",
            float(fitted["leakage_aware_max_full_private_material_leak_fitted_acceptance"])
            <= 0.25,
            {
                "leakage_aware_max_full_private_material_leak_fitted_acceptance": fitted[
                    "leakage_aware_max_full_private_material_leak_fitted_acceptance"
                ],
                "full_private_material_leakage_breaks_protocol": fitted[
                    "full_private_material_leakage_breaks_protocol"
                ],
            },
            "Redesign the challenge material so full leakage is outside the claim boundary or cryptographically protected.",
        ),
        readiness_gate(
            "R10",
            "No forbidden advantage or soundness claim is made",
            not any(forbidden_claims),
            {
                "quantum_advantage_claimed": fitted["quantum_advantage_claimed"],
                "bqp_separation_claimed": fitted["bqp_separation_claimed"],
                "sampling_hardness_proved": fitted["sampling_hardness_proved"],
                "cryptographic_soundness_proved": fitted["cryptographic_soundness_proved"],
                "protocol_soundness_proved": fitted["protocol_soundness_proved"],
                "backend_explicit_not_bqp_separation": backend[
                    "explicit_not_bqp_separation"
                ],
            },
            "Keep all claims bounded until real-backend transcript readiness passes.",
        ),
    ]

    passed = sum(1 for item in gates if item["passed"])
    failed = len(gates) - passed
    missing_gate_ids = [item["gate_id"] for item in gates if not item["passed"]]

    payload = {
        "benchmark": "B4/B8",
        "benchmark_id": "B4_B8",
        "title": "B4/B8 real-backend transcript readiness gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_fitted_spoofer_method": fitted["method"],
        "source_backend_calibrated_bridge_method": backend["method"],
        "source_transcript_case_count": fitted["source_transcript_case_count"],
        "train_row_count": fitted["train_row_count"],
        "holdout_row_count": fitted["holdout_row_count"],
        "fitted_evaluation_row_count": fitted["fitted_evaluation_row_count"],
        "backend_calibrated_aer_circuit_count": backend[
            "backend_calibrated_aer_circuit_count"
        ],
        "qiskit_generic_backend_v2_used": backend["qiskit_generic_backend_v2_used"],
        "backend_calibrated_noise_parameters_instantiated": backend[
            "backend_calibrated_noise_parameters_instantiated"
        ],
        "private_safe_max_no_leak_fitted_acceptance": fitted[
            "private_safe_max_no_leak_fitted_acceptance"
        ],
        "leakage_blind_max_no_leak_fitted_acceptance": fitted[
            "leakage_blind_max_no_leak_fitted_acceptance"
        ],
        "leakage_aware_max_full_private_material_leak_fitted_acceptance": fitted[
            "leakage_aware_max_full_private_material_leak_fitted_acceptance"
        ],
        "minimum_safe_calibrated_honest_acceptance": backend[
            "minimum_safe_calibrated_honest_acceptance"
        ],
        "maximum_safe_calibrated_adversary_acceptance": backend[
            "maximum_safe_calibrated_adversary_acceptance"
        ],
        "real_backend_properties_used": real_backend_properties_used,
        "hardware_execution_performed": hardware_execution_performed,
        "real_backend_transcript_rows": real_backend_transcript_rows,
        "leakage_separated_real_training_performed": leakage_separated_real_training_performed,
        "readiness_gate_count": len(gates),
        "passed_readiness_gate_count": passed,
        "failed_readiness_gate_count": failed,
        "missing_readiness_gate_ids": missing_gate_ids,
        "real_backend_transcript_readiness": False,
        "protocol_soundness_proved": False,
        "cryptographic_soundness_proved": False,
        "sampling_hardness_proved": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "readiness_gates": gates,
        "claim_boundary": {
            "real_backend_transcript_readiness_gate_built": True,
            "real_backend_transcript_readiness": False,
            "hardware_execution_performed": hardware_execution_performed,
            "real_backend_properties_used": real_backend_properties_used,
            "protocol_soundness_proved": False,
            "cryptographic_soundness_proved": False,
            "sampling_hardness_proved": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "what_is_supported": (
                "Synthetic transcript controls, fitted holdout spoofers, and a "
                "GenericBackendV2-style calibrated Aer bridge are present."
            ),
            "what_is_not_supported": (
                "No real backend properties, no hardware execution, no real "
                "transcript rows, leakage-blind fitting is unsafe, and full "
                "private-material leakage still breaks the protocol."
            ),
        },
        "elapsed_seconds": time.time() - started,
    }
    payload["validation_errors"] = validate(payload)
    payload["validation_error_count"] = len(payload["validation_errors"])
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload["source_transcript_case_count"] != 720:
        errors.append("expected 720 synthetic transcript cases")
    if payload["train_row_count"] != 560 or payload["holdout_row_count"] != 160:
        errors.append("expected 560/160 fitted train/holdout split")
    if payload["fitted_evaluation_row_count"] != 640:
        errors.append("expected 640 fitted evaluation rows")
    if payload["backend_calibrated_aer_circuit_count"] != 5760:
        errors.append("expected 5760 backend-calibrated Aer circuits")
    if payload["readiness_gate_count"] != 10:
        errors.append("expected ten readiness gates")
    if payload["passed_readiness_gate_count"] != 5:
        errors.append("current readiness should pass five gates")
    if payload["failed_readiness_gate_count"] != 5:
        errors.append("current readiness should fail five gates")
    if payload["missing_readiness_gate_ids"] != ["R5", "R6", "R7", "R8", "R9"]:
        errors.append("current missing readiness gates should be R5/R6/R7/R8/R9")
    if payload["real_backend_properties_used"] is not False:
        errors.append("real backend properties must remain absent")
    if payload["hardware_execution_performed"] is not False:
        errors.append("hardware execution must remain absent")
    if payload["real_backend_transcript_rows"] != 0:
        errors.append("real backend transcript rows must remain zero")
    if payload["leakage_separated_real_training_performed"] is not False:
        errors.append("real leakage-separated training must remain false")
    if float(payload["private_safe_max_no_leak_fitted_acceptance"]) != 0.0625:
        errors.append("private-safe no-leak fitted acceptance should be 0.0625")
    if float(payload["leakage_blind_max_no_leak_fitted_acceptance"]) != 0.35:
        errors.append("leakage-blind no-leak fitted acceptance should be 0.35")
    if float(payload["leakage_aware_max_full_private_material_leak_fitted_acceptance"]) != 1.0:
        errors.append("full private-material leakage fitted acceptance should be 1.0")
    for key in [
        "real_backend_transcript_readiness",
        "protocol_soundness_proved",
        "cryptographic_soundness_proved",
        "sampling_hardness_proved",
        "quantum_advantage_claimed",
        "bqp_separation_claimed",
    ]:
        if payload[key] is not False:
            errors.append(f"{key} must remain false")
    claims = payload["claim_boundary"]
    if claims["real_backend_transcript_readiness_gate_built"] is not True:
        errors.append("claim boundary must disclose readiness gate construction")
    for key in [
        "real_backend_transcript_readiness",
        "protocol_soundness_proved",
        "cryptographic_soundness_proved",
        "sampling_hardness_proved",
        "quantum_advantage_claimed",
        "bqp_separation_claimed",
    ]:
        if claims[key] is not False:
            errors.append(f"claim boundary must keep {key}=False")
    return errors


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# B4/B8 Real-Backend Transcript Readiness Gate",
        "",
        "- Gate: T-B4-002f / T-B8-003j",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Readiness gates passed / failed: {payload['passed_readiness_gate_count']} / {payload['failed_readiness_gate_count']}",
        f"- Missing readiness gates: {', '.join(payload['missing_readiness_gate_ids'])}",
        "",
        "## Evidence",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| synthetic transcript cases | {payload['source_transcript_case_count']} |",
        f"| fitted train / holdout / eval rows | {payload['train_row_count']} / {payload['holdout_row_count']} / {payload['fitted_evaluation_row_count']} |",
        f"| backend-calibrated Aer circuits | {payload['backend_calibrated_aer_circuit_count']} |",
        f"| private-safe no-leak fitted acceptance | {payload['private_safe_max_no_leak_fitted_acceptance']} |",
        f"| leakage-blind no-leak fitted acceptance | {payload['leakage_blind_max_no_leak_fitted_acceptance']} |",
        f"| full-private-material leakage fitted acceptance | {payload['leakage_aware_max_full_private_material_leak_fitted_acceptance']} |",
        f"| real backend transcript rows | {payload['real_backend_transcript_rows']} |",
        "",
        "## Readiness Gates",
        "",
        "| gate | passed | label | missing to promote |",
        "| --- | ---: | --- | --- |",
    ]
    for item in payload["readiness_gates"]:
        lines.append(
            f"| {item['gate_id']} | {item['passed']} | {item['label']} | {item['missing_to_promote']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
        ]
    )
    for key, value in payload["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Next Gate",
            "",
            "The next B4/B8 gate must ingest real backend properties or hardware",
            "randomized-measurement transcripts, keep leakage-separated train/holdout",
            "splits, and rerun fitted/generative spoofers before any soundness or",
            "advantage claim is promoted.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fitted-spoofer-result",
        type=Path,
        default=Path("results/B4_B8_private_challenge_fitted_spoofer_attack_v0.json"),
    )
    parser.add_argument(
        "--backend-calibrated-bridge-result",
        type=Path,
        default=Path("results/B10_t2_backend_calibrated_verifier_bridge_v0.json"),
    )
    parser.add_argument("--last-updated", default="2026-06-30")
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B4_B8_real_backend_transcript_readiness_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B4_B8_real_backend_transcript_readiness_gate.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build_report(args)
    write_json(args.json_output, payload, args.pretty)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "method": payload["method"],
                "passed_readiness_gate_count": payload["passed_readiness_gate_count"],
                "failed_readiness_gate_count": payload["failed_readiness_gate_count"],
                "missing_readiness_gate_ids": payload["missing_readiness_gate_ids"],
                "real_backend_properties_used": payload["real_backend_properties_used"],
                "hardware_execution_performed": payload["hardware_execution_performed"],
                "real_backend_transcript_rows": payload["real_backend_transcript_rows"],
                "validation_errors": payload["validation_errors"],
            },
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
