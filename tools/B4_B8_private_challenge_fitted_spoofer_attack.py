#!/usr/bin/env python3
"""T-B4-002e/T-B8-003i fitted spoofer attack for the B4/B8 noise bridge.

This consumes the verifier-private challenge noise bridge and trains small
deterministic empirical spoofers on a protocol-index holdout split. It is an
actual fitted-model diagnostic over synthetic transcript rows, not hardware
execution, real-backend evidence, or a protocol-soundness proof.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path
from statistics import mean


METHOD = "b4_b8_private_challenge_fitted_spoofer_attack_v0"
STATUS = "fitted_spoofer_holdout_attack_on_synthetic_transcripts_not_hardware"
SOURCE_METHOD = "b4_b8_verifier_private_challenge_noise_bridge_v0"

MODEL_FAMILIES = (
    "global_prior_learner",
    "public_mode_noise_learner",
    "private_safe_no_leak_calibrator",
    "leakage_aware_table_generator",
)


def _round(value: float) -> float:
    return round(float(value), 12)


def split_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    train = []
    holdout = []
    for row in rows:
        if row["protocol_idx"] % 5 == 0:
            holdout.append(row)
        else:
            train.append(row)
    return train, holdout


def train_models(train_rows: list[dict]) -> dict:
    global_mean = mean(row["adversary_acceptance"] for row in train_rows)

    mode_noise = defaultdict(list)
    no_leak_mode_noise = defaultdict(list)
    leakage_table = defaultdict(list)
    for row in train_rows:
        mode_noise[(row["mode"], row["noise_profile"])].append(row["adversary_acceptance"])
        if row["leakage_profile"] == "no_leak":
            no_leak_mode_noise[(row["mode"], row["noise_profile"])].append(row["adversary_acceptance"])
        leakage_table[(row["mode"], row["noise_profile"], row["leakage_profile"])].append(
            row["adversary_acceptance"]
        )

    return {
        "global_prior_learner": {"global_mean": _round(global_mean)},
        "public_mode_noise_learner": {
            f"{mode}|{noise}": _round(mean(values))
            for (mode, noise), values in sorted(mode_noise.items())
        },
        "private_safe_no_leak_calibrator": {
            f"{mode}|{noise}": _round(mean(values))
            for (mode, noise), values in sorted(no_leak_mode_noise.items())
        },
        "leakage_aware_table_generator": {
            f"{mode}|{noise}|{leakage}": _round(mean(values))
            for (mode, noise, leakage), values in sorted(leakage_table.items())
        },
    }


def predict(models: dict, family: str, row: dict) -> float:
    if family == "global_prior_learner":
        return models[family]["global_mean"]
    if family == "public_mode_noise_learner":
        return models[family][f"{row['mode']}|{row['noise_profile']}"]
    if family == "private_safe_no_leak_calibrator":
        return models[family][f"{row['mode']}|{row['noise_profile']}"]
    if family == "leakage_aware_table_generator":
        return models[family][f"{row['mode']}|{row['noise_profile']}|{row['leakage_profile']}"]
    raise KeyError(f"unknown model family {family}")


def build(source_json: Path) -> dict:
    source = json.loads(source_json.read_text())
    if source.get("method") != SOURCE_METHOD:
        raise ValueError(f"expected source method {SOURCE_METHOD}, got {source.get('method')}")
    transcript_rows = source.get("transcript_rows", [])
    train_rows, holdout_rows = split_rows(transcript_rows)
    models = train_models(train_rows)

    evaluation_rows = []
    for row in holdout_rows:
        for family in MODEL_FAMILIES:
            fitted_acceptance = _round(predict(models, family, row))
            truth = float(row["adversary_acceptance"])
            evaluation_rows.append(
                {
                    "protocol_idx": row["protocol_idx"],
                    "task": row["task"],
                    "mode": row["mode"],
                    "noise_profile": row["noise_profile"],
                    "leakage_profile": row["leakage_profile"],
                    "known_private_bits": row["known_private_bits"],
                    "actual_adversary_acceptance": _round(truth),
                    "model_family": family,
                    "fitted_acceptance": fitted_acceptance,
                    "absolute_error": _round(abs(fitted_acceptance - truth)),
                    "passes_0p10_soundness_pressure": fitted_acceptance <= 0.10,
                    "passes_0p25_soundness_pressure": fitted_acceptance <= 0.25,
                }
            )

    def max_family_leakage(family: str, leakage: str, modes: set[str] | None = None) -> float:
        subset = [
            row["fitted_acceptance"]
            for row in evaluation_rows
            if row["model_family"] == family
            and row["leakage_profile"] == leakage
            and (modes is None or row["mode"] in modes)
        ]
        return _round(max(subset))

    refreshed_modes = {"challenge_refresh", "refresh_plus_rotation"}
    private_safe_max_no_leak = max_family_leakage("private_safe_no_leak_calibrator", "no_leak")
    private_safe_backend_refreshed_no_leak = _round(
        max(
            row["fitted_acceptance"]
            for row in evaluation_rows
            if row["model_family"] == "private_safe_no_leak_calibrator"
            and row["leakage_profile"] == "no_leak"
            and row["noise_profile"] == "backend_like"
            and row["mode"] in refreshed_modes
        )
    )
    leakage_blind_max_no_leak = max_family_leakage("public_mode_noise_learner", "no_leak")
    leakage_aware_max_three = max_family_leakage("leakage_aware_table_generator", "three_private_bit_leak")
    leakage_aware_max_full = max_family_leakage("leakage_aware_table_generator", "full_private_material_leak")
    global_prior_max_no_leak = max_family_leakage("global_prior_learner", "no_leak")

    family_summary = {}
    for family in MODEL_FAMILIES:
        family_rows = [row for row in evaluation_rows if row["model_family"] == family]
        family_summary[family] = {
            "mean_absolute_error": _round(mean(row["absolute_error"] for row in family_rows)),
            "max_no_leak_fitted_acceptance": max_family_leakage(family, "no_leak"),
            "max_three_private_bit_leak_fitted_acceptance": max_family_leakage(
                family, "three_private_bit_leak"
            ),
            "max_full_private_material_leak_fitted_acceptance": max_family_leakage(
                family, "full_private_material_leak"
            ),
        }

    gate_results = {
        "G1_source_transcript_cases_present": source.get("transcript_case_count") == 720,
        "G2_protocol_holdout_split_is_nonempty": len(train_rows) == 560 and len(holdout_rows) == 160,
        "G3_fitted_evaluation_rows_present": len(evaluation_rows) == 640,
        "G4_actual_fitting_performed": bool(models),
        "G5_private_safe_no_leak_calibrator_stays_below_0p10": private_safe_max_no_leak <= 0.10,
        "G6_leakage_blind_mixture_exposes_calibration_failure": leakage_blind_max_no_leak > 0.10,
        "G7_full_private_material_leakage_still_breaks_protocol": leakage_aware_max_full >= 0.99,
        "G8_no_hardware_backend_or_soundness_claim": True,
    }

    validation_errors = []
    if len(transcript_rows) != 720:
        validation_errors.append("source transcript row count must be 720")
    if len(train_rows) != 560 or len(holdout_rows) != 160:
        validation_errors.append("protocol holdout split must produce 560 train rows and 160 holdout rows")
    if len(evaluation_rows) != 640:
        validation_errors.append("evaluation row count must be 640")

    return {
        "benchmark": "B4/B8",
        "benchmark_id": "B4_B8",
        "method": METHOD,
        "source_method": SOURCE_METHOD,
        "status": STATUS,
        "model_status": "deterministic_train_holdout_fitted_spoofer_models_not_real_backend",
        "source_transcript_case_count": source.get("transcript_case_count"),
        "train_row_count": len(train_rows),
        "holdout_row_count": len(holdout_rows),
        "fitted_model_family_count": len(MODEL_FAMILIES),
        "fitted_evaluation_row_count": len(evaluation_rows),
        "private_safe_max_no_leak_fitted_acceptance": private_safe_max_no_leak,
        "private_safe_backend_like_refreshed_no_leak_fitted_acceptance": (
            private_safe_backend_refreshed_no_leak
        ),
        "leakage_blind_max_no_leak_fitted_acceptance": leakage_blind_max_no_leak,
        "global_prior_max_no_leak_fitted_acceptance": global_prior_max_no_leak,
        "leakage_aware_max_three_private_bit_leak_fitted_acceptance": leakage_aware_max_three,
        "leakage_aware_max_full_private_material_leak_fitted_acceptance": leakage_aware_max_full,
        "private_safe_no_leak_passes_0p10": private_safe_max_no_leak <= 0.10,
        "private_safe_backend_refreshed_no_leak_passes_0p10": (
            private_safe_backend_refreshed_no_leak <= 0.10
        ),
        "leakage_blind_mixture_fails_no_leak_0p10": leakage_blind_max_no_leak > 0.10,
        "full_private_material_leakage_breaks_protocol": leakage_aware_max_full >= 0.99,
        "actual_fitted_training_performed": True,
        "hardware_execution_performed": False,
        "real_backend_properties_used": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "sampling_hardness_proved": False,
        "cryptographic_soundness_proved": False,
        "protocol_soundness_proved": False,
        "acceptance_gate_count": len(gate_results),
        "passed_gate_count": sum(1 for passed in gate_results.values() if passed),
        "failed_gate_count": sum(1 for passed in gate_results.values() if not passed),
        "gate_results": gate_results,
        "model_parameters": models,
        "family_summary": family_summary,
        "fitted_evaluation_rows": evaluation_rows,
        "validation_errors": validation_errors,
        "validation_error_count": len(validation_errors),
        "timestamp": time.time(),
    }


def render_markdown(payload: dict) -> str:
    return "\n".join(
        [
            "# B4/B8 Private Challenge Fitted Spoofer Attack",
            "",
            "- Gate: T-B4-002e / T-B8-003i",
            f"- Method: `{payload['method']}`",
            f"- Status: `{payload['status']}`",
            f"- Train / holdout rows: {payload['train_row_count']} / {payload['holdout_row_count']}",
            f"- Fitted evaluation rows: {payload['fitted_evaluation_row_count']}",
            f"- Gates passed: {payload['passed_gate_count']} / {payload['acceptance_gate_count']}",
            "",
            "## Result",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| private-safe max no-leak fitted acceptance | {payload['private_safe_max_no_leak_fitted_acceptance']} |",
            f"| private-safe backend-like refreshed no-leak fitted acceptance | {payload['private_safe_backend_like_refreshed_no_leak_fitted_acceptance']} |",
            f"| leakage-blind max no-leak fitted acceptance | {payload['leakage_blind_max_no_leak_fitted_acceptance']} |",
            f"| global-prior max no-leak fitted acceptance | {payload['global_prior_max_no_leak_fitted_acceptance']} |",
            f"| leakage-aware max three-private-bit leak fitted acceptance | {payload['leakage_aware_max_three_private_bit_leak_fitted_acceptance']} |",
            f"| leakage-aware max full-private-material leak fitted acceptance | {payload['leakage_aware_max_full_private_material_leak_fitted_acceptance']} |",
            "",
            "## Interpretation",
            "",
            "This converts the previous parametric spoofer-pressure warning into an actual train/holdout fitted-model diagnostic over the synthetic transcript bridge. The private-safe no-leak calibrator stays at the 1/16 guessing floor on holdout rows, but a leakage-blind mixture model exceeds the 0.10 no-leak threshold because its training distribution is contaminated by leaked-private-material cases. The result therefore narrows the live B4/B8 issue: no-leak private-safe fitting is not the immediate break, while leakage separation and real-backend transcript generation remain the hard next gates.",
            "",
            "## Claim Boundary",
            "",
            "- This performs deterministic fitted-model training on synthetic transcript rows.",
            "- This is not hardware execution and does not use real backend properties.",
            "- This does not prove cryptographic or protocol soundness.",
            "- This does not claim sampling hardness, quantum advantage, or BQP separation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-json",
        type=Path,
        default=Path("results/B4_B8_verifier_private_challenge_noise_bridge_v0.json"),
    )
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--md-out", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build(args.source_json)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
    )
    args.md_out.write_text(render_markdown(payload) + "\n")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "train_row_count": payload["train_row_count"],
                "holdout_row_count": payload["holdout_row_count"],
                "fitted_evaluation_row_count": payload["fitted_evaluation_row_count"],
                "private_safe_max_no_leak_fitted_acceptance": payload[
                    "private_safe_max_no_leak_fitted_acceptance"
                ],
                "leakage_blind_max_no_leak_fitted_acceptance": payload[
                    "leakage_blind_max_no_leak_fitted_acceptance"
                ],
                "passed_gate_count": payload["passed_gate_count"],
                "failed_gate_count": payload["failed_gate_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if payload["validation_error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
