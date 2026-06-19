#!/usr/bin/env python3
"""Ledger pressure gate for B1/B7 cone_01 single-carrier packets.

T-B1-004u found an exact one-carrier representation for each residual flat
packet. This gate asks the accounting question that matters for B7: does that
exact packet remove arbitrary-rotation occurrences, or does it merely replace
the original arbitrary RY with an arbitrary carrier rotation?

The current accepted ledger remains occurrence-based. A per-occurrence carrier
therefore counts as a new arbitrary occurrence unless a later certificate
absorbs, shares, or physically accepts it.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "results" / "B1_B7_cone01_single_carrier_dressing_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_single_carrier_ledger_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_single_carrier_ledger_gate.md"

METHOD = "b1_b7_cone01_single_carrier_ledger_gate_v0"
STATUS = "cone01_single_carrier_ledger_pressure_not_accepted_reduction"
MODEL_STATUS = "single_carrier_exact_packets_replace_not_remove_arbitrary_occurrences"
PROXY_T_PER_OCCURRENCE = 20
REQUIRED_OCCURRENCE_REMOVALS = 30


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def carrier_signature(row: dict[str, Any]) -> str:
    candidate = row["best_single_carrier_candidate"]
    return "|".join(
        [
            str(candidate["carrier_source"]),
            str(candidate["carrier_coefficient"]),
            str(candidate["axis"]),
            str(candidate["local_role"]),
            str(candidate["side"]),
            str(candidate["left_pair_label"]),
            str(candidate["right_pair_label"]),
            f"{float(candidate['carrier_angle']):.12g}",
        ]
    )


def carrier_row(row: dict[str, Any]) -> dict[str, Any]:
    candidate = row["best_single_carrier_candidate"]
    occurrence_count = int(row["occurrence_count"])
    accepted_removed = 0
    inserted_carrier_occurrences = occurrence_count
    optimistic_template_count = 1
    optimistic_duplicate_occurrences = max(0, occurrence_count - optimistic_template_count)
    max_removed_if_carrier_absorbed = occurrence_count
    return {
        "pattern_id": row["pattern_id"],
        "occurrence_count": occurrence_count,
        "line_model_original_arbitrary_occurrences": occurrence_count,
        "per_occurrence_inserted_carrier_occurrences": inserted_carrier_occurrences,
        "per_occurrence_net_arbitrary_occurrence_delta": inserted_carrier_occurrences - occurrence_count,
        "optimistic_template_carrier_count": optimistic_template_count,
        "optimistic_template_duplicate_carrier_occurrences": optimistic_duplicate_occurrences,
        "optimistic_template_proxy_t_reuse": optimistic_duplicate_occurrences * PROXY_T_PER_OCCURRENCE,
        "max_removed_if_carrier_absorbed": max_removed_if_carrier_absorbed,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": accepted_removed * PROXY_T_PER_OCCURRENCE,
        "best_residual_norm": row["best_single_carrier_residual_norm"],
        "carrier_signature": carrier_signature(row),
        "carrier_source": candidate["carrier_source"],
        "carrier_coefficient": candidate["carrier_coefficient"],
        "carrier_angle": candidate["carrier_angle"],
        "carrier_axis": candidate["axis"],
        "carrier_local_role": candidate["local_role"],
        "carrier_side": candidate["side"],
        "left_pair_label": candidate["left_pair_label"],
        "right_pair_label": candidate["right_pair_label"],
        "next_required_evidence": [
            "absorb the carrier into Clifford/exact-grid operations",
            "or replay-certify an occurrence-removing broader rewrite",
            "or provide an accepted physical cost model where this carrier is shared/countable",
        ],
    }


def build_payload() -> dict[str, Any]:
    source = load_json(SOURCE_PATH)
    source_summary = source.get("summary", {})
    rows = [carrier_row(row) for row in source.get("pattern_single_carrier_results", [])]
    signature_counts = Counter(row["carrier_signature"] for row in rows)
    axis_counts = Counter(row["carrier_axis"] for row in rows)
    role_counts = Counter(row["carrier_local_role"] for row in rows)
    source_counts = Counter(row["carrier_source"] for row in rows)

    covered_occurrences = sum(row["occurrence_count"] for row in rows)
    per_occurrence_inserted = sum(row["per_occurrence_inserted_carrier_occurrences"] for row in rows)
    accepted_removed = sum(row["accepted_occurrence_removal"] for row in rows)
    optimistic_template_count = len(signature_counts)
    optimistic_duplicate_occurrences = covered_occurrences - optimistic_template_count
    max_removed_if_absorbed = sum(row["max_removed_if_carrier_absorbed"] for row in rows)
    missing_after_absorption = max(0, REQUIRED_OCCURRENCE_REMOVALS - max_removed_if_absorbed)
    missing_after_acceptance = max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed)

    summary = {
        "source_method": source.get("method"),
        "source_status": source.get("status"),
        "source_exact_packet_count": source_summary.get("single_carrier_exact_packet_count"),
        "pattern_group_count": len(rows),
        "covered_invariant_flat_occurrence_count": covered_occurrences,
        "unique_carrier_signature_count": optimistic_template_count,
        "all_best_carriers_target_x": axis_counts == {"x": len(rows)} and role_counts == {"target": len(rows)},
        "carrier_source_counts": dict(sorted(source_counts.items())),
        "per_occurrence_inserted_carrier_occurrences": per_occurrence_inserted,
        "per_occurrence_net_arbitrary_occurrence_delta": per_occurrence_inserted - covered_occurrences,
        "optimistic_template_carrier_count": optimistic_template_count,
        "optimistic_duplicate_carrier_occurrences": optimistic_duplicate_occurrences,
        "optimistic_template_proxy_t_reuse": optimistic_duplicate_occurrences * PROXY_T_PER_OCCURRENCE,
        "max_occurrence_removal_if_all_carriers_absorbed": max_removed_if_absorbed,
        "max_proxy_t_reduction_if_all_carriers_absorbed": max_removed_if_absorbed * PROXY_T_PER_OCCURRENCE,
        "all_carriers_absorbed_clears_b7_target": max_removed_if_absorbed >= REQUIRED_OCCURRENCE_REMOVALS,
        "missing_occurrences_even_if_all_carriers_absorbed": missing_after_absorption,
        "missing_proxy_t_even_if_all_carriers_absorbed": missing_after_absorption * PROXY_T_PER_OCCURRENCE,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": accepted_removed * PROXY_T_PER_OCCURRENCE,
        "missing_occurrences_after_gate": missing_after_acceptance,
        "missing_proxy_t_after_gate": missing_after_acceptance * PROXY_T_PER_OCCURRENCE,
        "single_carrier_exact_packet_found": bool(source_summary.get("single_carrier_exact_packet_found")),
        "single_carrier_resource_certificate_claimed": False,
        "carrier_ledger_reduction_claimed": False,
        "rewrite_claimed": False,
        "semantic_certificate_claimed": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": None,
    }
    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 cone_01 single-carrier ledger pressure gate",
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_result": display_path(SOURCE_PATH),
        "source_method": source.get("method"),
        "workload": source.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "summary": summary,
        "carrier_ledger_rows": rows,
        "claim_boundary": {
            "single_carrier_exact_packet_found": bool(source_summary.get("single_carrier_exact_packet_found")),
            "single_carrier_resource_certificate_claimed": False,
            "carrier_ledger_reduction_claimed": False,
            "rewrite_claimed": False,
            "semantic_certificate_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "The exact single-carrier packet replaces the original arbitrary rotations with "
                "carrier rotations under the current occurrence model; it does not remove accepted occurrences."
            ),
            "unsupported_claims": [
                "This is not an occurrence-removing rewrite certificate.",
                "The optimistic carrier-template reuse signal is not an accepted B7 resource reduction.",
                "Even absorbing all 11 carrier-covered occurrences would still miss the 30-occurrence target.",
                "No physical carrier-sharing cost model is accepted.",
            ],
        },
    }
    errors = validate(payload)
    payload["summary"]["validation_error_count"] = len(errors)
    payload["validation_errors"] = errors
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload["summary"]
    claims = payload["claim_boundary"]
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    if payload.get("source_method") != "b1_b7_cone01_single_carrier_dressing_gate_v0":
        errors.append("source_method_mismatch")
    if summary.get("source_exact_packet_count") != 3:
        errors.append("source_exact_packet_count_mismatch")
    if summary.get("pattern_group_count") != 3:
        errors.append("pattern_group_count_mismatch")
    if summary.get("covered_invariant_flat_occurrence_count") != 11:
        errors.append("covered_occurrence_count_mismatch")
    if summary.get("unique_carrier_signature_count") != 3:
        errors.append("unique_carrier_signature_count_mismatch")
    if summary.get("all_best_carriers_target_x") is not True:
        errors.append("best_carriers_should_all_be_target_x")
    if summary.get("per_occurrence_inserted_carrier_occurrences") != 11:
        errors.append("per_occurrence_carrier_count_mismatch")
    if summary.get("per_occurrence_net_arbitrary_occurrence_delta") != 0:
        errors.append("single_carrier_should_replace_not_reduce_occurrences")
    if summary.get("optimistic_template_carrier_count") != 3:
        errors.append("optimistic_template_carrier_count_mismatch")
    if summary.get("optimistic_duplicate_carrier_occurrences") != 8:
        errors.append("optimistic_duplicate_carrier_occurrence_mismatch")
    if summary.get("optimistic_template_proxy_t_reuse") != 160:
        errors.append("optimistic_template_proxy_t_reuse_mismatch")
    if summary.get("max_occurrence_removal_if_all_carriers_absorbed") != 11:
        errors.append("max_absorbed_occurrence_mismatch")
    if summary.get("all_carriers_absorbed_clears_b7_target") is not False:
        errors.append("absorbed_carriers_must_not_clear_target")
    if summary.get("missing_occurrences_even_if_all_carriers_absorbed") != 19:
        errors.append("missing_absorbed_occurrence_mismatch")
    if summary.get("accepted_occurrence_removal") != 0:
        errors.append("accepted_occurrence_removal_must_remain_zero")
    if summary.get("accepted_proxy_t_reduction") != 0:
        errors.append("accepted_proxy_t_reduction_must_remain_zero")
    if summary.get("missing_occurrences_after_gate") != 30:
        errors.append("missing_occurrences_after_gate_mismatch")
    for field in [
        "single_carrier_resource_certificate_claimed",
        "carrier_ledger_reduction_claimed",
        "rewrite_claimed",
        "semantic_certificate_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field}_must_remain_false")
        if claims.get(field) is not False:
            errors.append(f"claim_boundary_{field}_must_remain_false")
    return errors


def markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone_01 Single-Carrier Ledger Pressure Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes the exact single-carrier packets from T-B1-004u "
        "and applies the current B7 occurrence-ledger rule. The result is a "
        "ledger boundary: the carrier exactifies the three packets, but it "
        "replaces rather than removes arbitrary occurrences unless a later "
        "certificate absorbs or shares the carrier.",
        "",
        "## Summary",
        "",
        f"- Source exact packets: `{summary['source_exact_packet_count']}`",
        f"- Pattern groups / covered occurrences: `{summary['pattern_group_count']}` / `{summary['covered_invariant_flat_occurrence_count']}`",
        f"- Unique carrier signatures: `{summary['unique_carrier_signature_count']}`",
        f"- All best carriers target-X: `{summary['all_best_carriers_target_x']}`",
        f"- Per-occurrence inserted carrier occurrences: `{summary['per_occurrence_inserted_carrier_occurrences']}`",
        f"- Net arbitrary occurrence delta under current ledger: `{summary['per_occurrence_net_arbitrary_occurrence_delta']}`",
        f"- Optimistic template carriers / duplicate occurrences: `{summary['optimistic_template_carrier_count']}` / `{summary['optimistic_duplicate_carrier_occurrences']}`",
        f"- Optimistic template proxy-T reuse: `{summary['optimistic_template_proxy_t_reuse']}`",
        f"- Max removals if all carriers are later absorbed: `{summary['max_occurrence_removal_if_all_carriers_absorbed']}`",
        f"- Missing occurrences even if all carriers are absorbed: `{summary['missing_occurrences_even_if_all_carriers_absorbed']}`",
        f"- Accepted occurrence/proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Carrier Rows",
        "",
        "| Pattern | Occurrences | Carrier | Ledger inserted | Net delta | Optimistic duplicates | Accepted reduction |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for row in payload["carrier_ledger_rows"]:
        carrier = (
            f"{row['carrier_coefficient']}*{row['carrier_source']} "
            f"{row['carrier_axis'].upper()}[{row['carrier_local_role']}]/{row['carrier_side']}"
        )
        lines.append(
            "| {pattern_id} | {occurrence_count} | `{carrier}` | {inserted} | {delta} | {duplicates} | {accepted} |".format(
                pattern_id=row["pattern_id"],
                occurrence_count=row["occurrence_count"],
                carrier=carrier,
                inserted=row["per_occurrence_inserted_carrier_occurrences"],
                delta=row["per_occurrence_net_arbitrary_occurrence_delta"],
                duplicates=row["optimistic_template_duplicate_carrier_occurrences"],
                accepted=row["accepted_occurrence_removal"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Single-carrier exact packets are confirmed from T-B1-004u.",
            "- Under the current per-occurrence ledger, they insert 11 carrier occurrences for 11 covered original occurrences.",
            "- Accepted occurrence removal and proxy-T reduction remain 0.",
            "- Even a future absorption of all 11 would still miss the 30-occurrence B7 target by 19 occurrences.",
            "- No rewrite, semantic certificate, physical cost model, or B7 ledger improvement is claimed.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--print-summary", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    write_json(args.json_out, payload, args.pretty)
    write_text(args.md_out, markdown(payload))
    if args.print_summary or args.pretty:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0 if payload["summary"]["validation_error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
