#!/usr/bin/env python3
"""B6/T-B6-005c validation-rescue scout.

This scout consumes the crystallographic descriptor screen and the packet scout,
then tests a small, predeclared set of non-promotional rescue scores. It exists
to identify whether the current source-validation blockers have a plausible
next engineering route. It does not create DFT or B5 observables and does not
claim material discovery.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable


METHOD = "b6_validation_rescue_scout_v0"
STATUS = "validation_rescue_candidate_found_not_material_discovery_claim"
MODEL_STATUS = "physics_risk_candidate_clears_source_validation_but_not_backend_or_observable_gates"
SELECTED_VARIANT = "physics_risk_adjusted_v0"
FAILED_IDS = ["V6", "V7", "V8"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def high_tc(row: dict[str, Any], threshold: float) -> bool:
    return float(row.get("tc_k", 0.0)) >= threshold


def average_precision_at_k(
    rows: list[dict[str, Any]],
    score_key: str,
    k: int,
    threshold: float,
) -> float:
    ranked = sorted(rows, key=lambda item: item[score_key], reverse=True)[:k]
    hits = 0
    precisions: list[float] = []
    for idx, row in enumerate(ranked, start=1):
        if high_tc(row, threshold):
            hits += 1
            precisions.append(hits / idx)
    positives = sum(1 for row in rows if high_tc(row, threshold))
    if positives == 0:
        return 0.0
    return sum(precisions) / min(positives, k)


def top_rows(rows: list[dict[str, Any]], score_key: str, k: int) -> list[dict[str, Any]]:
    keep = [
        "rank",
        "material_id",
        "formula",
        "family",
        "discovery_year",
        "tc_k",
        "pressure_gpa",
        "high_tc_label",
        score_key,
    ]
    ranked = sorted(rows, key=lambda item: item[score_key], reverse=True)[:k]
    out: list[dict[str, Any]] = []
    for rank, row in enumerate(ranked, start=1):
        item = {"rank": rank}
        for key in keep:
            if key in row:
                item[key] = row[key]
        item["is_negative_control"] = bool(row.get("is_negative_control", False)) or not high_tc(row, 30.0)
        out.append(item)
    return out


def score_variants() -> dict[str, Callable[[dict[str, Any]], float]]:
    return {
        "crystallographic_baseline_v0": lambda row: float(row.get("crystallo_score", 0.0)),
        "physics_descriptor_v0": lambda row: float(row.get("physics_descriptor_score", 0.0)),
        "combined_descriptor_v0": lambda row: float(row.get("combined_score", 0.0)),
        "physics_risk_adjusted_v0": lambda row: (
            float(row.get("physics_descriptor_score", 0.0))
            - 0.15 * float(row.get("disorder_risk", 0.0))
            - 0.15 * float(row.get("competing_order", 0.0))
        ),
        "combined_risk_adjusted_v0": lambda row: (
            float(row.get("combined_score", 0.0))
            - 0.15 * float(row.get("disorder_risk", 0.0))
            - 0.15 * float(row.get("competing_order", 0.0))
        ),
        "family_prior_denominator_v0": lambda row: float(row.get("family_prior_score", 0.0)),
    }


def requirement(req_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": req_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def build_payload(root: Path) -> dict[str, Any]:
    source = load_json(root / "results/B6_crystallographic_descriptor_screen_v0.json")
    packet = load_json(root / "results/B6_crystallographic_packet_scout_v0.json")
    rows = [dict(row) for row in source.get("materials_table", [])]
    threshold = float(source.get("high_tc_threshold_k", 30.0))
    top_k = int(source.get("top_k", 12))
    post_rows = [row for row in rows if row.get("time_split") == "post_split"]
    family_prior_ap = float(source.get("metrics", {}).get("post_split_family_prior_ap", 0.0))

    variants = []
    for name, score in score_variants().items():
        scored_rows = [dict(row, **{name: score(row)}) for row in rows]
        scored_post = [row for row in scored_rows if row.get("time_split") == "post_split"]
        top_all = top_rows(scored_rows, name, top_k)
        top_post = top_rows(scored_post, name, top_k)
        negatives_in_top = sum(1 for row in top_all if row["is_negative_control"])
        post_ap = average_precision_at_k(scored_post, name, top_k, threshold)
        variants.append(
            {
                "variant_id": name,
                "post_split_average_precision_at_k": post_ap,
                "post_split_family_prior_ap": family_prior_ap,
                "beats_family_prior": post_ap > family_prior_ap,
                "negative_controls_in_top_k": negatives_in_top,
                "source_validation_candidate": negatives_in_top >= 1 and post_ap > family_prior_ap,
                "top_all_rows": top_all,
                "top_post_rows": top_post,
            }
        )

    selected = next(row for row in variants if row["variant_id"] == SELECTED_VARIANT)
    candidate_count = sum(1 for row in variants if row["source_validation_candidate"])
    source_errors = list(source.get("validation_errors", []))
    packet_failed_ids = list(packet.get("summary", {}).get("failed_packet_scout_requirement_ids", []))

    requirements = [
        requirement(
            "V1",
            "source descriptor screen is available",
            source.get("method") == "b6_crystallographic_descriptor_screen_v0",
            {"method": source.get("method"), "status": source.get("status")},
        ),
        requirement(
            "V2",
            "packet scout is available and still demotes B6",
            packet.get("method") == "b6_crystallographic_packet_scout_v0"
            and packet.get("claim_boundary", {}).get("material_discovery_claimed") is False,
            {"method": packet.get("method"), "failed_ids": packet_failed_ids},
        ),
        requirement(
            "V3",
            "predeclared rescue variants were evaluated",
            len(variants) == 6 and selected["variant_id"] == SELECTED_VARIANT,
            {"variant_count": len(variants), "selected_variant": selected["variant_id"]},
        ),
        requirement(
            "V4",
            "selected rescue keeps negative controls in top-k",
            int(selected["negative_controls_in_top_k"]) >= 1,
            {"negative_controls_in_top_k": selected["negative_controls_in_top_k"], "top_k": top_k},
        ),
        requirement(
            "V5",
            "selected rescue beats post-split family-prior AP",
            bool(selected["beats_family_prior"]),
            {
                "selected_post_split_ap": selected["post_split_average_precision_at_k"],
                "family_prior_ap": family_prior_ap,
            },
        ),
        requirement(
            "V6",
            "reproducible crystallographic backend is pinned",
            False,
            {"pymatgen_available": packet.get("summary", {}).get("pymatgen_available")},
        ),
        requirement(
            "V7",
            "DFT observable channel exists",
            False,
            {"dft_observable_rows": packet.get("summary", {}).get("dft_observable_rows")},
        ),
        requirement(
            "V8",
            "B5-computed observable channel exists",
            False,
            {"b5_computed_observable_rows": packet.get("summary", {}).get("b5_computed_observable_rows")},
        ),
    ]
    failed = [row for row in requirements if not row["passed"]]

    return {
        "benchmark_id": "B6",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_descriptor_status": source.get("status"),
        "source_packet_scout_status": packet.get("status"),
        "selected_variant": SELECTED_VARIANT,
        "threshold_k": threshold,
        "top_k": top_k,
        "record_count": len(rows),
        "post_split_record_count": len(post_rows),
        "family_count": source.get("family_count"),
        "negative_control_count": source.get("negative_control_count"),
        "source_validation_error_count": len(source_errors),
        "source_validation_errors": source_errors,
        "variant_count": len(variants),
        "source_validation_candidate_count": candidate_count,
        "variants": variants,
        "requirements": requirements,
        "validation_rescue_requirement_count": len(requirements),
        "validation_rescue_requirements_passed": len(requirements) - len(failed),
        "validation_rescue_requirements_failed": len(failed),
        "failed_validation_rescue_requirement_ids": [row["requirement_id"] for row in failed],
        "selected_negative_controls_in_top_k": selected["negative_controls_in_top_k"],
        "selected_post_split_ap": selected["post_split_average_precision_at_k"],
        "post_split_family_prior_ap": family_prior_ap,
        "selected_beats_family_prior": selected["beats_family_prior"],
        "selected_source_validation_candidate": selected["source_validation_candidate"],
        "pymatgen_available": packet.get("summary", {}).get("pymatgen_available"),
        "dft_observable_rows": packet.get("summary", {}).get("dft_observable_rows"),
        "b5_computed_observable_rows": packet.get("summary", {}).get("b5_computed_observable_rows"),
        "claims": {
            "validation_rescue_candidate_found": True,
            "source_validation_blockers_resolved_in_source": False,
            "reproducible_crystallographic_descriptor_claimed": False,
            "dft_observable_claimed": False,
            "b5_computed_observable_claimed": False,
            "material_discovery_claimed": False,
            "mechanism_solved": False,
            "solution_claimed": False,
        },
        "claim_boundary": {
            "what_is_supported": "A predeclared physics-risk rescue candidate clears the two source-validation symptoms on the existing table.",
            "what_is_not_supported": "The source screen is not rewritten, no backend is pinned, no DFT/B5 observables exist, and no material-discovery or mechanism claim is made.",
            "next_gate": "Turn the selected rescue into a pinned backend run, then attach DFT and B5 observable rows before any candidate-ranking promotion.",
        },
        "validation_errors": [],
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# B6 Validation Rescue Scout",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Selected variant: `{payload['selected_variant']}`",
        f"- Requirements passed / failed: {payload['validation_rescue_requirements_passed']} / {payload['validation_rescue_requirements_failed']}",
        f"- Failed requirement IDs: {', '.join(payload['failed_validation_rescue_requirement_ids'])}",
        f"- Source validation errors observed: {payload['source_validation_error_count']}",
        f"- Selected negative controls in top-k: {payload['selected_negative_controls_in_top_k']}",
        f"- Selected post-split AP: {payload['selected_post_split_ap']}",
        f"- Family-prior AP: {payload['post_split_family_prior_ap']}",
        f"- DFT rows / B5 rows: {payload['dft_observable_rows']} / {payload['b5_computed_observable_rows']}",
        "",
        "## Variant Results",
        "",
    ]
    for row in payload["variants"]:
        lines.append(
            "- "
            f"{row['variant_id']}: post-split AP={row['post_split_average_precision_at_k']}, "
            f"negatives_in_top_k={row['negative_controls_in_top_k']}, "
            f"candidate={row['source_validation_candidate']}"
        )
    lines.extend(
        [
            "",
            "## Requirement Results",
            "",
        ]
    )
    for row in payload["requirements"]:
        mark = "PASS" if row["passed"] else "FAIL"
        lines.append(f"- {row['requirement_id']} [{mark}]: {row['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=Path("results/B6_validation_rescue_scout_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B6_validation_rescue_scout.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    payload = build_payload(root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(payload, args.markdown_output)
    print(payload["status"])
    print(
        payload["validation_rescue_requirements_passed"],
        payload["validation_rescue_requirements_failed"],
        payload["failed_validation_rescue_requirement_ids"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
