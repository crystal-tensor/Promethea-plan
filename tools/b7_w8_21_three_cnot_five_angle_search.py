#!/usr/bin/env python3
"""Search a target-side three-CX/five-angle family for w8_21 contexts.

The two-CX five-angle family cannot absorb the selected external local
contexts.  This gate changes the nonlocal word itself: it allows three CX
gates, keeps the source pi scaffold fixed, and places five arbitrary angles
on target-side Euler slots.  Only families retaining at least four of the
five source target-side slots are included, so the result is a bounded
resource-frontier experiment rather than a global synthesis theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import b7_w8_21_neighborhood_transfer as neighborhood
from tools import b7_w8_21_three_cnot_search as base


METHOD = "b7_w8_21_three_cnot_five_angle_search_v0"
TEMPLATE_ID = "w8_21"
RESULT_PATH = "results/B7_w8_21_three_cnot_five_angle_search_v0.json"
REPORT_PATH = "research/B7_w8_21_three_cnot_five_angle_search.md"
EXACT_TOLERANCE = 1e-10
MIN_SOURCE_SLOT_OVERLAP = 4


def stable_hash(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_side_slots() -> tuple[int, ...]:
    return tuple(
        slot["index"]
        for slot in base.SLOTS
        if slot["qubit"] == 1 and slot["index"] != base.SOURCE_PI_SLOT
    )


def families(min_source_overlap: int) -> list[dict[str, Any]]:
    source_slots = set(base.SOURCE_ARBITRARY_SLOTS)
    output: list[dict[str, Any]] = []
    for free_slots in itertools.combinations(target_side_slots(), 5):
        overlap = len(set(free_slots) & source_slots)
        if overlap < min_source_overlap:
            continue
        for cnot_directions in itertools.product(base.CNOT_DIRS, repeat=3):
            output.append(
                {
                    "free_slots": free_slots,
                    "free_slot_labels": [base.SLOTS[index]["label"] for index in free_slots],
                    "source_slot_overlap": overlap,
                    "cnot_directions": cnot_directions,
                    "fixed_angles": {base.SOURCE_PI_SLOT: math.pi},
                    "fixed_angle_labels": [base.SLOTS[base.SOURCE_PI_SLOT]["label"] + "=pi"],
                }
            )
    return output


def context_targets(root: Path) -> list[dict[str, Any]]:
    source = neighborhood.source_unitary(neighborhood.BASE_PARAMS)
    targets = []
    for row in neighborhood.context_rows(root):
        local = neighborhood.target_local_matrix(row["context_operation"], row["target"])
        if local is None:
            raise ValueError(f"unsupported context operation: {row['context_operation']}")
        matrix = local @ source if row["direction"] == "after" else source @ local
        targets.append({"row": row, "matrix": matrix})
    return targets


def optimize_family(
    target: np.ndarray,
    family: dict[str, Any],
    seed_count: int,
    max_nfev: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    seeds = base.initial_points(tuple(family["free_slots"]), seed_count, rng)
    fit = base.optimize_family(
        target,
        tuple(family["cnot_directions"]),
        family["fixed_angles"],
        tuple(family["free_slots"]),
        seeds,
        max_nfev,
    )
    return fit


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve()
    all_families = families(args.min_source_overlap)
    selected = all_families[: args.family_limit] if args.family_limit else all_families
    targets = context_targets(root)
    rng = np.random.default_rng(args.random_seed)
    context_results = []
    optimizer_runs = 0
    for context_index, context in enumerate(targets, start=1):
        best: dict[str, Any] | None = None
        exact_count = 0
        for family_index, family in enumerate(selected, start=1):
            fit = optimize_family(context["matrix"], family, args.seed_count, args.max_nfev, rng)
            optimizer_runs += args.seed_count
            candidate = {"family_index": family_index, **family, "fit": fit}
            if best is None or fit["residual_norm"] < best["fit"]["residual_norm"]:
                best = candidate
            if fit["residual_norm"] <= args.exact_tolerance:
                exact_count += 1
        assert best is not None
        context_results.append(
            {
                "context_index": context_index,
                "direction": context["row"]["direction"],
                "line_span": context["row"]["line_span"],
                "context_operation": context["row"]["context_operation"],
                "tested_family_count": len(selected),
                "exact_family_count": exact_count,
                "best_candidate": best,
                "accepted_occurrence_removal": 0,
                "accepted_proxy_t_reduction": 0,
                "b7_credit": 0,
            }
        )

    exact_context_count = sum(row["exact_family_count"] > 0 for row in context_results)
    summary = {
        "tested_context_count": len(context_results),
        "exact_context_count": exact_context_count,
        "total_exact_family_count": sum(row["exact_family_count"] for row in context_results),
        "best_residual_norm": min(row["best_candidate"]["fit"]["residual_norm"] for row in context_results),
        "attempted_optimizer_runs": optimizer_runs,
        "baseline_cnot_count": 2,
        "candidate_cnot_count": 3,
        "baseline_arbitrary_parameter_count": 6,
        "candidate_arbitrary_parameter_count": 5,
        "potential_arbitrary_parameter_saving_if_exact": 1,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_credit": 0,
        "validation_error_count": 0,
        "rewrite_claimed": False,
        "resource_saving_claimed": False,
        "global_lower_bound_claimed": False,
    }
    status = (
        "three_cnot_five_angle_search_complete_bounded_exact_candidate"
        if exact_context_count
        else "three_cnot_five_angle_search_complete_no_exact_context_replay"
    )
    payload: dict[str, Any] = {
        "title": "B7 w8_21 bounded three-CX five-angle target-side search",
        "version": 0,
        "method": METHOD,
        "status": status,
        "classification": "bounded_three_cnot_five_angle_resource_frontier",
        "template_id": TEMPLATE_ID,
        "last_updated": args.last_updated,
        "question": "Can one additional CX replace the sixth arbitrary angle needed to absorb the selected external local contexts?",
        "candidate_family": {
            "description": "three CX gates, fixed source target-side Rz(pi) scaffold, five arbitrary target-side Euler slots, and all CX direction sequences",
            "family_count": len(selected),
            "total_family_count": len(all_families),
            "family_selection": "exhaustive" if not args.family_limit else "prefix_subset",
            "target_side_slot_count": len(target_side_slots()),
            "min_source_slot_overlap": args.min_source_overlap,
            "cnot_direction_count": 8,
            "seed_count_per_family": args.seed_count,
            "max_nfev_per_seed": args.max_nfev,
            "free_angle_count": 5,
            "fixed_source_pi_slot": base.SLOTS[base.SOURCE_PI_SLOT]["label"],
        },
        "fit_configuration": {
            "seed_count": args.seed_count,
            "max_nfev": args.max_nfev,
            "exact_tolerance": args.exact_tolerance,
            "objective": "global-phase-aligned 4x4 unitary residual",
        },
        "summary": summary,
        "source_bindings": {
            neighborhood.SOURCE_QASM: {
                "path": neighborhood.SOURCE_QASM,
                "sha256": file_sha256(root / neighborhood.SOURCE_QASM),
            },
            neighborhood.SCAN_PATH: {
                "path": neighborhood.SCAN_PATH,
                "sha256": file_sha256(root / neighborhood.SCAN_PATH),
            },
            "results/B7_w8_21_neighborhood_transfer_v0.json": {
                "path": "results/B7_w8_21_neighborhood_transfer_v0.json",
                "sha256": file_sha256(root / "results/B7_w8_21_neighborhood_transfer_v0.json"),
            },
        },
        "contexts": context_results,
        "claim_boundary": {
            "supported_claim": "The declared target-side three-CX families were tested against all seven source-bound contexts with the recorded bounded optimizer configuration.",
            "unsupported_claims": [
                "No global synthesis lower bound is claimed.",
                "No exact candidate is a rewrite until arbitrary-input QASM replay and resource pricing pass.",
                "No occurrence removal, proxy-T reduction, B7 credit, quantum advantage, or solved B1/B7 frontier is claimed.",
            ],
            "global_lower_bound_claimed": False,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
        },
        "artifacts": {"result": RESULT_PATH, "markdown_report": REPORT_PATH},
        "payload_hash": "",
    }
    payload["payload_hash"] = stable_hash({key: value for key, value in payload.items() if key != "payload_hash"})
    return payload


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    family = payload["candidate_family"]
    lines = [
        "# B7 w8_21 Three-CX Five-Angle Search",
        "",
        f"- Status: `{payload['status']}`",
        f"- Classification: `{payload['classification']}`",
        f"- Families tested per context: `{family['family_count']}`",
        f"- Contexts tested: `{summary['tested_context_count']}`",
        f"- Optimizer runs: `{summary['attempted_optimizer_runs']}`",
        f"- Exact context replays: `{summary['exact_context_count']}/{summary['tested_context_count']}`",
        f"- Best residual norm: `{summary['best_residual_norm']:.16g}`",
        f"- Payload hash: `{payload['payload_hash']}`",
        "",
        "## Heuristic question",
        "",
        "Can one additional CX replace the sixth arbitrary angle needed to absorb a non-grid external local rotation?",
        "",
        "## Search scope",
        "",
        "The candidate changes the nonlocal word itself: three CX gates, the source target-side `Rz(pi)` scaffold fixed, and five arbitrary angles placed on target-side Euler slots across four layers. Families retain at least four of the five source target-side slots and exhaust all eight CX direction sequences. This is a bounded resource-frontier test, not a global synthesis claim.",
        "",
        "## Result",
        "",
        "| Context | Exact families | Best residual | Best family |",
        "|---:|---:|---:|---|",
    ]
    for row in payload["contexts"]:
        best = row["best_candidate"]
        family_label = f"CX {''.join(best['cnot_directions'])}; " + ", ".join(best["free_slot_labels"])
        lines.append(f"| {row['context_index']} | {row['exact_family_count']} | {best['fit']['residual_norm']:.16g} | `{family_label}` |")
    lines.extend(
        [
            "",
            "No bounded exact replay was found in this family." if summary["exact_context_count"] == 0 else "A bounded exact candidate exists, but it is not yet a rewrite or resource credit.",
            "",
            "## Resource boundary",
            "",
            "The candidate spends one additional CX to retain five arbitrary angles against a baseline of two CX and six arbitrary angles for the selected contexts. Occurrence removal, proxy-T reduction, and B7 credit remain zero until a concrete arbitrary-input rewrite and full ledger pass.",
            "",
            "## Claim boundary",
            "",
            "This closes only the declared target-side family with minimum source-slot overlap four. It is not a global three-CX lower bound, an exhaustive local-Euler search, a full-circuit rewrite, or a solved B1/B7 frontier.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json-output", type=Path, default=Path(RESULT_PATH))
    parser.add_argument("--markdown-output", type=Path, default=Path(REPORT_PATH))
    parser.add_argument("--family-limit", type=int, default=0)
    parser.add_argument("--seed-count", type=int, default=2)
    parser.add_argument("--max-nfev", type=int, default=160)
    parser.add_argument("--exact-tolerance", type=float, default=EXACT_TOLERANCE)
    parser.add_argument("--min-source-overlap", type=int, default=MIN_SOURCE_SLOT_OVERLAP)
    parser.add_argument("--random-seed", type=int, default=17015)
    parser.add_argument("--last-updated", default="2026-07-15")
    args = parser.parse_args()
    result = run(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(report(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "payload_hash": result["payload_hash"], **result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
