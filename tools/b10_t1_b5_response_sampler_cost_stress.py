#!/usr/bin/env python3
"""Cost an optimistic B5 response sampler against the B10-T1 denominator ladder."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


METHOD = "b10_t1_b5_response_sampler_cost_stress_v0"
STATUS = "b5_response_sampler_cost_stress_no_positive_same_access_route"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def row_key(row: dict[str, Any]) -> tuple[int, float]:
    return int(row["sites"]), float(row["u_over_t"])


def shot_floor_for_response_half_width(
    epsilon_abs: float,
    eta: float,
    confidence_z: float,
    density_variance_upper_bound: float,
) -> dict[str, Any]:
    if epsilon_abs <= 0.0:
        return {
            "shots_per_side": None,
            "total_measurement_shots": None,
            "finite": False,
        }
    shots_per_side = math.ceil(
        (confidence_z**2 * density_variance_upper_bound)
        / (2.0 * eta**2 * epsilon_abs**2)
    )
    return {
        "shots_per_side": int(shots_per_side),
        "total_measurement_shots": int(2 * shots_per_side),
        "finite": True,
    }


def target_payload(
    exact_response: float,
    relative_error: float,
    eta: float,
    confidence_z: float,
    density_variance_upper_bound: float,
) -> dict[str, Any]:
    epsilon_abs = max(abs(exact_response) * abs(relative_error), 1e-15)
    payload = shot_floor_for_response_half_width(
        epsilon_abs=epsilon_abs,
        eta=eta,
        confidence_z=confidence_z,
        density_variance_upper_bound=density_variance_upper_bound,
    )
    payload.update(
        {
            "target_relative_error": relative_error,
            "target_absolute_error": epsilon_abs,
        }
    )
    return payload


def build_rows(
    d5: dict[str, Any],
    non_oracle: dict[str, Any],
    seeded_mps: dict[str, Any],
    variational_mps: dict[str, Any],
    confidence_z: float,
    density_variance_upper_bound: float,
    prep_two_qubit_gate_floor_per_site: int,
) -> list[dict[str, Any]]:
    non_oracle_by_key = {row_key(row): row for row in non_oracle["rows"]}
    seeded_by_key = {row_key(row): row for row in seeded_mps["rows"]}
    variational_by_key = {row_key(row): row for row in variational_mps["rows"]}
    rows = []
    for d5_row in d5["rows"]:
        key = row_key(d5_row)
        non_oracle_row = non_oracle_by_key[key]
        seeded_row = seeded_by_key[key]
        variational_row = variational_by_key[key]
        sites = int(d5_row["sites"])
        exact_response = float(d5_row["susceptibility_proxy"])
        eta = float(d5_row["eta"])
        exact_matvec_ops = int(d5_row["matvec_equivalent_ops"])
        prep_two_qubit_floor = prep_two_qubit_gate_floor_per_site * sites
        targets = {
            "match_non_oracle_embedding": target_payload(
                exact_response=exact_response,
                relative_error=float(non_oracle_row["selected_relative_response_error"]),
                eta=eta,
                confidence_z=confidence_z,
                density_variance_upper_bound=density_variance_upper_bound,
            ),
            "match_one_site_variational_mps_als": target_payload(
                exact_response=exact_response,
                relative_error=float(variational_row["selected_relative_response_error"]),
                eta=eta,
                confidence_z=confidence_z,
                density_variance_upper_bound=density_variance_upper_bound,
            ),
            "match_exact_state_seeded_mps_pressure": target_payload(
                exact_response=exact_response,
                relative_error=float(seeded_row["selected_relative_response_error"]),
                eta=eta,
                confidence_z=confidence_z,
                density_variance_upper_bound=density_variance_upper_bound,
            ),
        }
        for payload in targets.values():
            shots = payload["total_measurement_shots"]
            payload["optimistic_state_preparation_two_qubit_gate_floor"] = (
                int(shots * prep_two_qubit_floor) if shots is not None else None
            )
            payload["beats_explicit_d5_matvec_ops_by_shots"] = (
                bool(shots < exact_matvec_ops) if shots is not None else False
            )
        seeded_target = targets["match_exact_state_seeded_mps_pressure"]
        rows.append(
            {
                "sites": sites,
                "u_over_t": float(d5_row["u_over_t"]),
                "eta": eta,
                "exact_response": exact_response,
                "exact_d5_hilbert_dimension": int(d5_row["hilbert_dimension"]),
                "exact_d5_matvec_equivalent_ops": exact_matvec_ops,
                "optimistic_prep_two_qubit_gate_floor_per_circuit": prep_two_qubit_floor,
                "density_variance_upper_bound": density_variance_upper_bound,
                "confidence_z": confidence_z,
                "targets": targets,
                "sampler_beats_seeded_mps_pressure_by_shots": bool(
                    seeded_target["total_measurement_shots"] is not None
                    and seeded_target["total_measurement_shots"] < exact_matvec_ops
                ),
                "same_access_positive_route_ready": False,
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    seeded_shots = [
        row["targets"]["match_exact_state_seeded_mps_pressure"]["total_measurement_shots"]
        for row in rows
    ]
    als_shots = [
        row["targets"]["match_one_site_variational_mps_als"]["total_measurement_shots"]
        for row in rows
    ]
    non_oracle_shots = [
        row["targets"]["match_non_oracle_embedding"]["total_measurement_shots"]
        for row in rows
    ]
    seeded_prep = [
        row["targets"]["match_exact_state_seeded_mps_pressure"][
            "optimistic_state_preparation_two_qubit_gate_floor"
        ]
        for row in rows
    ]
    return {
        "instance_count": len(rows),
        "confidence_z": rows[0]["confidence_z"] if rows else None,
        "density_variance_upper_bound": rows[0]["density_variance_upper_bound"] if rows else None,
        "max_exact_d5_hilbert_dimension": max(row["exact_d5_hilbert_dimension"] for row in rows),
        "max_exact_d5_matvec_equivalent_ops": max(row["exact_d5_matvec_equivalent_ops"] for row in rows),
        "min_total_shots_to_match_non_oracle_embedding": min(non_oracle_shots),
        "max_total_shots_to_match_non_oracle_embedding": max(non_oracle_shots),
        "min_total_shots_to_match_one_site_variational_mps_als": min(als_shots),
        "max_total_shots_to_match_one_site_variational_mps_als": max(als_shots),
        "min_total_shots_to_match_seeded_mps_pressure": min(seeded_shots),
        "max_total_shots_to_match_seeded_mps_pressure": max(seeded_shots),
        "median_total_shots_to_match_seeded_mps_pressure": sorted(seeded_shots)[len(seeded_shots) // 2],
        "max_optimistic_seeded_target_prep_2q_gate_floor": max(seeded_prep),
        "rows_where_sampler_shots_beat_explicit_d5_matvec_ops_for_seeded_target": sum(
            1 for row in rows if row["sampler_beats_seeded_mps_pressure_by_shots"]
        ),
        "sampling_oracle_constructed": False,
        "same_access_positive_route_ready": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
    }


def validate(report: dict[str, Any]) -> list[str]:
    errors = []
    summary = report["summary"]
    claims = report["claim_boundary"]
    if summary["instance_count"] != 9:
        errors.append("expected nine B5 Hubbard response instances")
    if summary["max_total_shots_to_match_seeded_mps_pressure"] <= summary["max_exact_d5_matvec_equivalent_ops"]:
        errors.append("seeded-pressure shot floor should exceed explicit D5 matvec pressure")
    if summary["rows_where_sampler_shots_beat_explicit_d5_matvec_ops_for_seeded_target"] != 0:
        errors.append("sampler should not beat explicit D5 matvec ops for seeded target")
    for key in [
        "sampling_oracle_constructed",
        "same_access_positive_route_ready",
        "quantum_advantage_claimed",
        "bqp_separation_claimed",
        "production_dmrg_available",
    ]:
        if claims.get(key) is not False:
            errors.append(f"{key} must remain False")
    return errors


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    d5 = load_json(args.d5_result)
    non_oracle = load_json(args.non_oracle_result)
    seeded_mps = load_json(args.seeded_mps_result)
    variational_mps = load_json(args.variational_mps_result)
    rows = build_rows(
        d5=d5,
        non_oracle=non_oracle,
        seeded_mps=seeded_mps,
        variational_mps=variational_mps,
        confidence_z=args.confidence_z,
        density_variance_upper_bound=args.density_variance_upper_bound,
        prep_two_qubit_gate_floor_per_site=args.prep_two_qubit_gate_floor_per_site,
    )
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T1 B5 response sampler cost stress",
        "version": "0.1",
        "status": STATUS,
        "method": METHOD,
        "source_target_id": "B10-T1",
        "dependency_benchmarks": ["B5", "B10"],
        "source_d5_denominator_method": d5["method"],
        "source_non_oracle_embedding_method": non_oracle["method"],
        "source_seeded_mps_method": seeded_mps["method"],
        "source_variational_mps_method": variational_mps["method"],
        "sampling_model": {
            "name": "optimistic_bounded_density_finite_difference_sampler",
            "density_observable_range": [0.0, 2.0],
            "density_variance_upper_bound": args.density_variance_upper_bound,
            "confidence_z": args.confidence_z,
            "response_estimator": "(E[n_i | +eta] - E[n_i | -eta]) / (2 eta)",
            "shots_are_independent": True,
            "state_preparation_floor_per_circuit_2q_gates": "sites * prep_two_qubit_gate_floor_per_site",
            "mixing_cost_included": False,
            "readout_error_included": False,
        },
        "summary": summarize(rows),
        "claim_boundary": {
            "sampling_oracle_constructed": False,
            "same_access_positive_route_ready": False,
            "production_dmrg_available": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "what_is_supported": (
                "An optimistic finite-difference response sampler lower bound was costed "
                "against the same nine B5/B10 Hubbard response rows and denominator ladder."
            ),
            "what_is_not_supported": (
                "This is not a constructed quantum response oracle, not a state-preparation "
                "algorithm, not production DMRG, not a sampling theorem, not quantum advantage, "
                "and not a BQP separation."
            ),
        },
        "rows": rows,
    }
    report["validation_errors"] = validate(report)
    return report


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# B10-T1 B5 Response Sampler Cost Stress v0.1",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: {report['method']}",
        f"- Sampling model: {report['sampling_model']['name']}",
        f"- Instances: {summary['instance_count']}",
        f"- Confidence z: {summary['confidence_z']}",
        f"- Max explicit D5 matvec-equivalent ops: {summary['max_exact_d5_matvec_equivalent_ops']}",
        f"- Max shots to match non-oracle embedding: {summary['max_total_shots_to_match_non_oracle_embedding']}",
        f"- Max shots to match one-site variational MPS/ALS: {summary['max_total_shots_to_match_one_site_variational_mps_als']}",
        f"- Max shots to match exact-state-seeded MPS pressure: {summary['max_total_shots_to_match_seeded_mps_pressure']}",
        f"- Median shots to match exact-state-seeded MPS pressure: {summary['median_total_shots_to_match_seeded_mps_pressure']}",
        f"- Max optimistic seeded-target prep 2Q gate floor: {summary['max_optimistic_seeded_target_prep_2q_gate_floor']}",
        f"- Rows where sampler shots beat explicit D5 matvec ops for seeded target: {summary['rows_where_sampler_shots_beat_explicit_d5_matvec_ops_for_seeded_target']}",
        f"- Sampling oracle constructed: {summary['sampling_oracle_constructed']}",
        f"- Same-access positive route ready: {summary['same_access_positive_route_ready']}",
        f"- Validation errors: {report['validation_errors']}",
        "",
        "## Row Pressure",
        "",
        "| sites | U/t | exact response | D5 matvec ops | shots vs ALS | shots vs seeded MPS | seeded prep 2Q floor |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        als = row["targets"]["match_one_site_variational_mps_als"]
        seeded = row["targets"]["match_exact_state_seeded_mps_pressure"]
        lines.append(
            f"| {row['sites']} | {row['u_over_t']:.1f} | {row['exact_response']:.6g} | "
            f"{row['exact_d5_matvec_equivalent_ops']} | {als['total_measurement_shots']} | "
            f"{seeded['total_measurement_shots']} | "
            f"{seeded['optimistic_state_preparation_two_qubit_gate_floor']} |"
        )
    lines.extend(["", "## Claim Boundary", ""])
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Next Gate",
            "",
            "This closes only an optimistic sampler-cost stress. A positive B10-T1 route",
            "still requires either a real same-access response oracle with state-preparation,",
            "mixing, measurement, and confidence costs, or a mature production DMRG/MPS",
            "reference that is not exact-state seeded.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--d5-result", type=Path, default=Path("results/B10_t1_d5_observable_denominator_table_v0.json"))
    parser.add_argument("--non-oracle-result", type=Path, default=Path("results/B5_non_oracle_response_embedding_baseline_v0.json"))
    parser.add_argument("--seeded-mps-result", type=Path, default=Path("results/B5_mps_truncation_response_reference_v0.json"))
    parser.add_argument("--variational-mps-result", type=Path, default=Path("results/B5_variational_mps_als_response_reference_v0.json"))
    parser.add_argument("--confidence-z", type=float, default=2.576)
    parser.add_argument("--density-variance-upper-bound", type=float, default=1.0)
    parser.add_argument("--prep-two-qubit-gate-floor-per-site", type=int, default=1)
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t1_b5_response_sampler_cost_stress_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t1_b5_response_sampler_cost_stress.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_report(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(report, args.markdown_output)
    print(
        json.dumps(
            {
                "status": report["status"],
                "method": report["method"],
                **report["summary"],
                "validation_errors": report["validation_errors"],
            },
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
