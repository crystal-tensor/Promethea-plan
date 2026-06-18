#!/usr/bin/env python3
"""Build non-oracle B5 Hubbard response embedding baselines."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from b5_boundary_field_embedding_baseline import (  # noqa: E402
    ETA,
    FIELD_GRID,
    best_energy_proxy_row,
    embedded_response_for_field,
    load_json,
    solve_cluster_response,
)


METHOD = "b5_non_oracle_response_embedding_baseline_v0"
STATUS = "non_oracle_response_embedding_denominator_not_quantum_advantage_claim"


def relative_error(candidate: float, target: float) -> float:
    return abs(candidate - target) / max(abs(target), 1e-12)


def zero_field_embedding(sites: int, u_over_t: float, t_value: float) -> dict[str, Any]:
    result = embedded_response_for_field(
        full_sites=sites,
        u_over_t=u_over_t,
        t_value=t_value,
        edge_field=0.0,
    )
    result["method"] = "open_cluster_zero_field"
    result["selection_rule"] = "fixed zero edge field; no exact-response target used"
    return result


def density_self_consistent_embedding(
    sites: int,
    u_over_t: float,
    t_value: float,
    field_grid: tuple[float, ...],
) -> dict[str, Any]:
    candidates = []
    for edge_field in field_grid:
        candidate = embedded_response_for_field(
            full_sites=sites,
            u_over_t=u_over_t,
            t_value=t_value,
            edge_field=edge_field,
        )
        density_scores = [
            abs(float(row["density_mean"]) - 1.0)
            for row in candidate["cluster_rows"]
        ]
        candidate["density_self_consistency_score"] = float(np.mean(density_scores))
        candidate["density_self_consistency_max_deviation"] = float(np.max(density_scores))
        candidates.append(candidate)

    selected = min(
        candidates,
        key=lambda item: (
            float(item["density_self_consistency_score"]),
            abs(float(item["edge_field"])),
        ),
    )
    selected = dict(selected)
    selected["method"] = "density_self_consistent_edge_field"
    selected["selection_rule"] = (
        "choose the field minimizing cluster center-density deviation from half filling; "
        "no exact-response target used"
    )
    selected["field_grid"] = list(field_grid)
    selected["field_candidates"] = [
        {
            "edge_field": item["edge_field"],
            "embedded_susceptibility_proxy": item["embedded_susceptibility_proxy"],
            "density_self_consistency_score": item["density_self_consistency_score"],
            "density_self_consistency_max_deviation": item["density_self_consistency_max_deviation"],
        }
        for item in candidates
    ]
    return selected


def finite_cluster_inverse_size_extrapolation(sites: int, u_over_t: float, t_value: float) -> dict[str, Any]:
    cluster2 = solve_cluster_response(2, u_over_t, t_value, 0.0)
    cluster4 = solve_cluster_response(4, u_over_t, t_value, 0.0)
    if sites <= 4:
        predicted = float(cluster4["susceptibility_proxy"])
        slope = 0.0
        intercept = predicted
        selection_rule = "use the exact same zero-field four-site cluster when the target chain has four sites"
    else:
        x2 = 1.0 / 2.0
        x4 = 1.0 / 4.0
        x_target = 1.0 / float(sites)
        chi2 = float(cluster2["susceptibility_proxy"])
        chi4 = float(cluster4["susceptibility_proxy"])
        slope = (chi2 - chi4) / (x2 - x4)
        intercept = chi4 - slope * x4
        predicted = intercept + slope * x_target
        selection_rule = (
            "linear extrapolation of zero-field two- and four-site cluster responses in inverse cluster size; "
            "no exact-response target used"
        )
    return {
        "method": "finite_cluster_inverse_size_extrapolation",
        "selection_rule": selection_rule,
        "clusters": [2, 4],
        "edge_field": 0.0,
        "embedded_susceptibility_proxy": float(predicted),
        "fit_intercept": float(intercept),
        "fit_slope_inverse_cluster_size": float(slope),
        "cluster_rows": [cluster2, cluster4],
        "max_cluster_relative_residual": max(cluster2["relative_residual"], cluster4["relative_residual"]),
        "max_cluster_hilbert_dimension": max(cluster2["hilbert_dimension"], cluster4["hilbert_dimension"]),
    }


def error_payload(candidate: dict[str, Any], exact_susceptibility: float) -> dict[str, Any]:
    embedded = float(candidate["embedded_susceptibility_proxy"])
    return {
        "method": candidate["method"],
        "selection_rule": candidate["selection_rule"],
        "edge_field": candidate.get("edge_field"),
        "clusters": candidate.get("clusters"),
        "embedded_susceptibility_proxy": embedded,
        "absolute_response_error": abs(embedded - exact_susceptibility),
        "relative_response_error": relative_error(embedded, exact_susceptibility),
        "max_cluster_hilbert_dimension": int(candidate["max_cluster_hilbert_dimension"]),
        "max_cluster_relative_residual": float(candidate["max_cluster_relative_residual"]),
    }


def build_rows(
    d5_source: dict[str, Any],
    energy_source: dict[str, Any],
    oracle_source: dict[str, Any],
    field_grid: tuple[float, ...],
) -> list[dict[str, Any]]:
    oracle_rows = {
        (int(row["sites"]), float(row["u_over_t"])): row
        for row in oracle_source.get("rows", [])
    }
    rows: list[dict[str, Any]] = []
    for d5_row in d5_source.get("rows", []):
        sites = int(d5_row["sites"])
        u_over_t = float(d5_row["u_over_t"])
        t_value = float(d5_row.get("t", 1.0))
        exact_susceptibility = float(d5_row["susceptibility_proxy"])

        zero = zero_field_embedding(sites, u_over_t, t_value)
        density = density_self_consistent_embedding(sites, u_over_t, t_value, field_grid)
        extrapolated = finite_cluster_inverse_size_extrapolation(sites, u_over_t, t_value)
        candidates = {
            "open_cluster_zero_field": error_payload(zero, exact_susceptibility),
            "density_self_consistent_edge_field": error_payload(density, exact_susceptibility),
            "finite_cluster_inverse_size_extrapolation": error_payload(extrapolated, exact_susceptibility),
        }

        selected_key = (
            "open_cluster_zero_field"
            if sites <= 4
            else "finite_cluster_inverse_size_extrapolation"
        )
        selected = candidates[selected_key]
        energy_proxy = best_energy_proxy_row(energy_source, sites, u_over_t)
        oracle_row = oracle_rows.get((sites, u_over_t), {})
        oracle_error = oracle_row.get("relative_response_error")
        meaningful_oracle_win = (
            bool(selected["relative_response_error"] + 1e-9 < float(oracle_error))
            if oracle_error is not None
            else False
        )

        rows.append(
            {
                "model": "one_dimensional_fermi_hubbard_half_filled_density_response",
                "sites": sites,
                "u_over_t": u_over_t,
                "t": t_value,
                "eta": float(d5_row.get("eta", ETA)),
                "exact_d5_susceptibility_proxy": exact_susceptibility,
                "exact_d5_hilbert_dimension": int(d5_row["hilbert_dimension"]),
                "exact_d5_relative_residual": float(d5_row["relative_residual"]),
                "uses_exact_target_for_selection": False,
                "oracle_tuned_boundary_field": False,
                "selection_policy": (
                    "predeclared: use open_cluster_zero_field for four-site rows; "
                    "use finite_cluster_inverse_size_extrapolation for larger rows"
                ),
                "selected_non_oracle_method": selected_key,
                "selected_non_oracle_susceptibility_proxy": selected["embedded_susceptibility_proxy"],
                "selected_absolute_response_error": selected["absolute_response_error"],
                "selected_relative_response_error": selected["relative_response_error"],
                "selected_max_cluster_hilbert_dimension": selected["max_cluster_hilbert_dimension"],
                "selected_max_cluster_relative_residual": selected["max_cluster_relative_residual"],
                "non_oracle_candidates": candidates,
                "density_self_consistent_field": density["edge_field"],
                "density_self_consistency_score": density["density_self_consistency_score"],
                "density_self_consistency_max_deviation": density["density_self_consistency_max_deviation"],
                "finite_extrapolation_fit": {
                    "intercept": extrapolated["fit_intercept"],
                    "slope_inverse_cluster_size": extrapolated["fit_slope_inverse_cluster_size"],
                },
                "oracle_boundary_field_relative_response_error": (
                    float(oracle_error) if oracle_error is not None else None
                ),
                "non_oracle_beats_oracle_boundary_field": meaningful_oracle_win,
                "best_cluster_product_energy_error_per_site": (
                    float(energy_proxy["energy_error_per_site"]) if energy_proxy else None
                ),
                "best_cluster_product_cluster_size": int(energy_proxy["cluster_size"]) if energy_proxy else None,
                "candidate_quantum_response_beats_non_oracle_denominator": False,
            }
        )
    return rows


def method_error_summary(rows: list[dict[str, Any]], method: str) -> dict[str, float]:
    rel_errors = [
        float(row["non_oracle_candidates"][method]["relative_response_error"])
        for row in rows
    ]
    return {
        "mean_relative_response_error": float(np.mean(rel_errors)),
        "median_relative_response_error": float(np.median(rel_errors)),
        "max_relative_response_error": float(np.max(rel_errors)),
    }


def summarize(rows: list[dict[str, Any]], field_grid: tuple[float, ...]) -> dict[str, Any]:
    selected_errors = [float(row["selected_relative_response_error"]) for row in rows]
    oracle_errors = [
        float(row["oracle_boundary_field_relative_response_error"])
        for row in rows
        if row["oracle_boundary_field_relative_response_error"] is not None
    ]
    method_summaries = {
        method: method_error_summary(rows, method)
        for method in [
            "open_cluster_zero_field",
            "density_self_consistent_edge_field",
            "finite_cluster_inverse_size_extrapolation",
        ]
    }
    return {
        "instance_count": len(rows),
        "site_values": sorted({row["sites"] for row in rows}),
        "u_over_t_values": sorted({row["u_over_t"] for row in rows}),
        "field_grid": list(field_grid),
        "field_grid_count": len(field_grid),
        "selected_policy": "open_cluster_zero_field for sites<=4; finite_cluster_inverse_size_extrapolation otherwise",
        "selected_mean_relative_response_error": float(np.mean(selected_errors)),
        "selected_median_relative_response_error": float(np.median(selected_errors)),
        "selected_max_relative_response_error": float(np.max(selected_errors)),
        "method_error_summaries": method_summaries,
        "oracle_boundary_field_mean_relative_response_error": float(np.mean(oracle_errors)) if oracle_errors else None,
        "oracle_boundary_field_max_relative_response_error": float(np.max(oracle_errors)) if oracle_errors else None,
        "non_oracle_rows_beating_oracle_boundary_field": sum(
            bool(row["non_oracle_beats_oracle_boundary_field"]) for row in rows
        ),
        "max_exact_d5_hilbert_dimension": max(row["exact_d5_hilbert_dimension"] for row in rows),
        "max_selected_cluster_hilbert_dimension": max(row["selected_max_cluster_hilbert_dimension"] for row in rows),
        "quantum_response_win_claimed": False,
        "accuracy_per_resource_win_claimed": False,
        "oracle_tuned_boundary_field": False,
        "uses_exact_target_for_selection": False,
    }


def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status must remain a non-oracle denominator, not an advantage claim")
    if report.get("benchmark_id") != "B5":
        errors.append("benchmark_id must be B5")
    if report.get("method") != METHOD:
        errors.append("method mismatch")
    if report.get("dependency_b10_table") != "b10_t1_d5_observable_denominator_table_v0":
        errors.append("B5 non-oracle response baseline must depend on the B10 D5 observable table")
    if report.get("explicit_not_quantum_advantage") is not True:
        errors.append("report must explicitly avoid quantum-advantage claims")
    if report.get("uses_exact_target_for_selection") is not False:
        errors.append("report must not use exact D5 targets for model selection")
    if report.get("oracle_tuned_boundary_field") is not False:
        errors.append("report must disclose that it is not oracle tuned")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 9:
        errors.append("non-oracle response baseline must cover the 9 D5 B5 rows")
    if summary.get("field_grid_count", 0) < 7:
        errors.append("density self-consistency field grid must contain at least seven fields")
    if summary.get("quantum_response_win_claimed") is not False:
        errors.append("quantum response win must not be claimed")
    if summary.get("accuracy_per_resource_win_claimed") is not False:
        errors.append("accuracy-per-resource win must not be claimed")
    if summary.get("uses_exact_target_for_selection") is not False:
        errors.append("summary must not use exact D5 targets for selection")
    if int(summary.get("max_selected_cluster_hilbert_dimension", 10**9)) >= int(
        summary.get("max_exact_d5_hilbert_dimension", 0)
    ):
        errors.append("selected non-oracle denominator should reduce max cluster Hilbert dimension below exact D5")

    allowed_methods = {
        "open_cluster_zero_field",
        "density_self_consistent_edge_field",
        "finite_cluster_inverse_size_extrapolation",
    }
    for row in report.get("rows", []):
        label = f"sites={row.get('sites')} U/t={row.get('u_over_t')}"
        if row.get("uses_exact_target_for_selection") is not False:
            errors.append(f"{label} uses exact target for selection")
        if row.get("oracle_tuned_boundary_field") is not False:
            errors.append(f"{label} must not be oracle tuned")
        if row.get("selected_non_oracle_method") not in allowed_methods:
            errors.append(f"{label} selected an unknown non-oracle method")
        if not math.isfinite(float(row.get("selected_relative_response_error", math.inf))):
            errors.append(f"{label} has non-finite selected response error")
        if float(row.get("selected_max_cluster_relative_residual", 1.0)) > 1e-6:
            errors.append(f"{label} selected cluster residual too high")
        if row.get("candidate_quantum_response_beats_non_oracle_denominator") is not False:
            errors.append(f"{label} claims a quantum win")
        candidates = row.get("non_oracle_candidates", {})
        if set(candidates) != allowed_methods:
            errors.append(f"{label} candidate set mismatch")
    return errors


def build_report(
    d5_source_path: Path,
    energy_source_path: Path,
    oracle_source_path: Path,
    field_grid: tuple[float, ...],
) -> dict[str, Any]:
    started = time.perf_counter()
    d5_source = load_json(d5_source_path)
    energy_source = load_json(energy_source_path)
    oracle_source = load_json(oracle_source_path)
    rows = build_rows(d5_source, energy_source, oracle_source, field_grid)
    report = {
        "benchmark_id": "B5",
        "problem_id": 38,
        "title": "B5 non-oracle response embedding baselines for Hubbard density response",
        "version": "0.1",
        "last_updated": "2026-06-18",
        "status": STATUS,
        "method": METHOD,
        "model_status": "non_oracle_classical_response_embedding_denominator",
        "dependency_b10_table": d5_source.get("method"),
        "dependency_b10_result": str(d5_source_path),
        "dependency_energy_baseline": energy_source.get("method"),
        "dependency_energy_result": str(energy_source_path),
        "dependency_oracle_boundary_field_result": str(oracle_source_path),
        "explicit_not_quantum_advantage": True,
        "explicit_not_bqp_separation": True,
        "uses_exact_target_for_selection": False,
        "oracle_tuned_boundary_field": False,
        "summary": summarize(rows, field_grid),
        "rows": rows,
        "runtime_seconds": time.perf_counter() - started,
        "claim_boundary": {
            "now_supported": (
                "A non-oracle B5 response denominator now covers the same nine B10 D5 Hubbard rows. "
                "It selects among zero-field cluster embedding and inverse-size cluster extrapolation "
                "by a predeclared rule, while density self-consistency is reported as a blind diagnostic."
            ),
            "still_not_supported": (
                "This is not DMRG, not a two-dimensional correlated-matter result, not a quantum kernel, "
                "and not an accuracy-per-resource win. Exact D5 susceptibilities are used only for evaluation."
            ),
            "next_gate": (
                "Replace this small-cluster denominator with a real tensor/DMRG reference or compare a quantum "
                "impurity/response kernel after state-preparation, measurement, and optimizer-loop costs."
            ),
        },
    }
    report["validation_errors"] = validate(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    method_summaries = summary["method_error_summaries"]
    lines = [
        "# B5 Non-Oracle Response Embedding Baseline v0.1",
        "",
        f"Last updated: {report['last_updated']}",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{report['method']}`",
        f"- Dependency B10 table: `{report['dependency_b10_table']}`",
        f"- Dependency oracle denominator for comparison only: `{report['dependency_oracle_boundary_field_result']}`",
        f"- Instances: {summary['instance_count']}",
        f"- Sites: {summary['site_values']}",
        f"- U/t values: {summary['u_over_t_values']}",
        f"- Selection policy: {summary['selected_policy']}",
        f"- Selected mean / median / max relative response error: {summary['selected_mean_relative_response_error']:.6g} / {summary['selected_median_relative_response_error']:.6g} / {summary['selected_max_relative_response_error']:.6g}",
        f"- Oracle boundary-field mean / max relative error, comparison only: {summary['oracle_boundary_field_mean_relative_response_error']:.6g} / {summary['oracle_boundary_field_max_relative_response_error']:.6g}",
        f"- Non-oracle rows beating oracle boundary-field: {summary['non_oracle_rows_beating_oracle_boundary_field']}",
        f"- Max exact D5 Hilbert dimension: {summary['max_exact_d5_hilbert_dimension']}",
        f"- Max selected cluster Hilbert dimension: {summary['max_selected_cluster_hilbert_dimension']}",
        f"- Uses exact target for selection: {summary['uses_exact_target_for_selection']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        f"- Explicitly not quantum advantage: {report['explicit_not_quantum_advantage']}",
        "",
        "## Blind Method Comparison",
        "",
        "| Method | Mean rel. error | Median rel. error | Max rel. error |",
        "|---|---:|---:|---:|",
    ]
    for method, values in method_summaries.items():
        lines.append(
            "| {method} | {mean:.6g} | {median:.6g} | {maxerr:.6g} |".format(
                method=method,
                mean=values["mean_relative_response_error"],
                median=values["median_relative_response_error"],
                maxerr=values["max_relative_response_error"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This artifact closes the oracle-tuning loophole in B5/T-B5-002 for the current 1D Hubbard D5 rows.",
            "- The selected denominator does not inspect the exact D5 susceptibility when choosing a method or field.",
            "- Exact D5 values are used only after selection to compute residuals and compare against the previous oracle-tuned pressure baseline.",
            "- The result is still a small-cluster classical denominator, not a DMRG replacement and not a deployable quantum many-body solver.",
            "",
            "## Rows",
            "",
            "| Sites | U/t | Selected method | Exact D5 chi | Selected chi | Rel. error | Oracle rel. error | Max cluster dim |",
            "|---:|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["rows"]:
        lines.append(
            "| {sites} | {u:.1f} | {method} | {exact:.8g} | {selected:.8g} | {rel:.6g} | {oracle:.6g} | {dim} |".format(
                sites=row["sites"],
                u=row["u_over_t"],
                method=row["selected_non_oracle_method"],
                exact=row["exact_d5_susceptibility_proxy"],
                selected=row["selected_non_oracle_susceptibility_proxy"],
                rel=row["selected_relative_response_error"],
                oracle=row["oracle_boundary_field_relative_response_error"],
                dim=row["selected_max_cluster_hilbert_dimension"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Now supported: {report['claim_boundary']['now_supported']}",
            f"- Still not supported: {report['claim_boundary']['still_not_supported']}",
            f"- Next gate: {report['claim_boundary']['next_gate']}",
        ]
    )
    if report["validation_errors"]:
        lines.extend(["", "## Validation Errors", ""])
        lines.extend(f"- {error}" for error in report["validation_errors"])
    return "\n".join(lines) + "\n"


def parse_float_tuple(value: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in value.split(",") if item.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--d5-source", type=Path, default=Path("results/B10_t1_d5_observable_denominator_table_v0.json"))
    parser.add_argument("--energy-source", type=Path, default=Path("results/B5_hubbard_embedding_baseline_v0.json"))
    parser.add_argument("--oracle-source", type=Path, default=Path("results/B5_boundary_field_embedding_baseline_v0.json"))
    parser.add_argument("--field-grid", default=",".join(str(item) for item in FIELD_GRID))
    parser.add_argument("--json-output", type=Path, default=Path("results/B5_non_oracle_response_embedding_baseline_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B5_non_oracle_response_embedding_baseline.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(
        d5_source_path=args.d5_source,
        energy_source_path=args.energy_source,
        oracle_source_path=args.oracle_source,
        field_grid=parse_float_tuple(args.field_grid),
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if not report["validation_errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
