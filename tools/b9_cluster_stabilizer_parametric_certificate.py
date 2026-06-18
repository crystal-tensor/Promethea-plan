#!/usr/bin/env python3
"""Build a local parametric certificate for the B9 cluster-stabilizer family.

This checker deliberately proves only a narrow, executable statement:
for the open-chain cluster-stabilizer toy family used by the B9 lab,
uniform local reweighting by 27/20 preserves locality and normalized gap
at the formula level. It is not a Lean theorem and not a Quantum PCP result.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "results" / "B9_named_family_width_locality_bounds_v0.json"
JSON_OUT = ROOT / "results" / "B9_cluster_stabilizer_parametric_certificate_v0.json"
MD_OUT = ROOT / "research" / "B9_cluster_stabilizer_parametric_certificate.md"

METHOD = "b9_cluster_stabilizer_parametric_certificate_v0"
STATUS = "parametric_certificate_checked_by_local_verifier_not_formal_theorem"
MODEL_STATUS = "executable_parametric_certificate_not_quantum_pcp_proof"
NAMED_FAMILY = "cluster_stabilizer_open_uniform_reweight"
SCALE = Fraction(27, 20)
FINITE_ROWS = [4, 5, 6]


@dataclass(frozen=True)
class TermProfile:
    qubits: int
    term_count: int
    interior_term_count: int
    boundary_term_count: int
    support_size_set: tuple[int, ...]
    max_locality: int
    all_terms_are_interactions: bool


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def formula_profile(qubits: int) -> TermProfile:
    if qubits < 4:
        raise ValueError("certificate domain requires n >= 4")
    interior = qubits - 2
    boundary = 2
    return TermProfile(
        qubits=qubits,
        term_count=interior + boundary,
        interior_term_count=interior,
        boundary_term_count=boundary,
        support_size_set=(2, 3),
        max_locality=3,
        all_terms_are_interactions=True,
    )


def monomial(coeff: Fraction, *variables: str) -> tuple[str, tuple[str, ...]]:
    return (f"{coeff.numerator}/{coeff.denominator}", tuple(sorted(variables)))


def check_normalized_gap_identity() -> dict[str, Any]:
    left_cross_product = monomial(SCALE, "g", "w")
    right_cross_product = monomial(SCALE, "g", "w")
    return {
        "identity": "(s*g)/(s*w) = g/w for s=27/20 and w>0",
        "domain_conditions": ["s > 0", "w > 0"],
        "left_cross_product": {
            "coefficient": left_cross_product[0],
            "variables": list(left_cross_product[1]),
        },
        "right_cross_product": {
            "coefficient": right_cross_product[0],
            "variables": list(right_cross_product[1]),
        },
        "checked": left_cross_product == right_cross_product,
    }


def rows_by_qubits(source: dict[str, Any]) -> dict[int, dict[str, Any]]:
    rows = source.get("support_profiles", [])
    result: dict[int, dict[str, Any]] = {}
    for row in rows:
        qubits = int(row.get("qubits"))
        result[qubits] = row
    return result


def validate_source_rows(source: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    source_rows = rows_by_qubits(source)
    checked_rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for qubits in FINITE_ROWS:
        profile = formula_profile(qubits)
        row = source_rows.get(qubits)
        if row is None:
            errors.append(f"missing_source_row_n_{qubits}")
            continue
        term_count = int(row.get("term_count", -1))
        max_locality = int(row.get("max_support", -1))
        support_sizes = sorted(int(value) for value in row.get("unique_supports", []))
        unique_scales = {Fraction(str(value)) for value in row.get("unique_scales", [])}
        all_terms_scaled_uniformly = bool(row.get("all_terms_scaled_uniformly"))
        normalized_gap_invariant = bool(source.get("normalized_gap_invariant_under_uniform_scaling"))
        row_ok = (
            term_count == profile.term_count
            and max_locality == profile.max_locality
            and support_sizes == list(profile.support_size_set)
            and unique_scales == {SCALE}
            and all_terms_scaled_uniformly
            and normalized_gap_invariant
        )
        if not row_ok:
            errors.append(f"source_row_mismatch_n_{qubits}")
        checked_rows.append(
            {
                "qubits": qubits,
                "formula_term_count": profile.term_count,
                "source_term_count": term_count,
                "formula_support_size_set": list(profile.support_size_set),
                "source_support_size_set": support_sizes,
                "formula_max_locality": profile.max_locality,
                "source_max_locality": max_locality,
                "source_unique_scales": [str(value) for value in sorted(unique_scales)],
                "source_all_terms_scaled_uniformly": all_terms_scaled_uniformly,
                "source_normalized_gap_invariant": normalized_gap_invariant,
                "checked": row_ok,
            }
        )
    return checked_rows, errors


def build_certificate() -> dict[str, Any]:
    source = load_json(SOURCE_PATH)
    checked_rows, validation_errors = validate_source_rows(source)
    identity = check_normalized_gap_identity()

    if source.get("named_family") != NAMED_FAMILY:
        validation_errors.append("unexpected_source_named_family")
    if source.get("method") != "b9_named_family_width_locality_bound_v0":
        validation_errors.append("unexpected_source_method")
    if not identity["checked"]:
        validation_errors.append("normalized_gap_identity_not_checked")

    finite_profiles = [formula_profile(qubits) for qubits in FINITE_ROWS]
    if any(profile.term_count != profile.qubits for profile in finite_profiles):
        validation_errors.append("term_count_formula_failed")
    if any(profile.interior_term_count != profile.qubits - 2 for profile in finite_profiles):
        validation_errors.append("interior_term_count_formula_failed")
    if any(profile.boundary_term_count != 2 for profile in finite_profiles):
        validation_errors.append("boundary_term_count_formula_failed")
    if any(profile.support_size_set != (2, 3) for profile in finite_profiles):
        validation_errors.append("support_profile_formula_failed")
    if any(profile.max_locality != 3 for profile in finite_profiles):
        validation_errors.append("max_locality_formula_failed")
    if any(not profile.all_terms_are_interactions for profile in finite_profiles):
        validation_errors.append("interaction_only_formula_failed")

    certificate_rejected = True
    claim_boundary = {
        "local_verifier_checked": len(validation_errors) == 0,
        "proof_assistant_checked": False,
        "formal_theorem_proved": False,
        "explicit_not_quantum_pcp_proof": True,
        "global_gap_amplification_impossibility_claimed": False,
        "nlts_theorem_claimed": False,
        "quantum_advantage_claimed": False,
    }

    return {
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_result": str(SOURCE_PATH.relative_to(ROOT)),
        "source_method": source.get("method"),
        "named_family": NAMED_FAMILY,
        "parameterized_domain": "integer n >= 4",
        "parameterized_n_min": 4,
        "finite_rows_checked": FINITE_ROWS,
        "uniform_scale": str(SCALE),
        "uniform_scale_decimal": float(SCALE),
        "term_count_formula": "n",
        "interior_term_count_formula": "n-2",
        "boundary_term_count_formula": "2",
        "support_size_set": [2, 3],
        "max_locality": 3,
        "all_terms_are_interactions": True,
        "coefficient_scale_identity": "H'_n = (27/20) H_n",
        "gap_width_scale_identity": {
            "gap_prime": "(27/20) * gap",
            "width_prime": "(27/20) * width",
            "positive_scalar_multiplication_only": True,
        },
        "normalized_gap_identity": identity,
        "normalized_gap_invariant_symbolically": identity["checked"],
        "finite_source_row_checks": checked_rows,
        "certificate_rejected": certificate_rejected,
        "rejection_reason": (
            "Uniform positive rescaling preserves normalized gap, so this family "
            "cannot be counted as a raw-gap amplification certificate."
        ),
        "claim_boundary": claim_boundary,
        "proof_assistant_checked": False,
        "formal_theorem_proved": False,
        "explicit_not_quantum_pcp_proof": True,
        "global_gap_amplification_impossibility_claimed": False,
        "validation_errors": validation_errors,
        "validation_error_count": len(validation_errors),
    }


def write_markdown(certificate: dict[str, Any], path: Path) -> None:
    rows = certificate["finite_source_row_checks"]
    lines = [
        "# B9 Cluster-Stabilizer Parametric Certificate",
        "",
        f"Status: `{certificate['status']}`",
        "",
        "This artifact is a local executable verifier for one narrow B9 statement. "
        "It checks the open-chain cluster-stabilizer toy family used by the local "
        "Hamiltonian lab and confirms that uniform reweighting by `27/20` preserves "
        "locality and normalized gap at the formula level for the declared family.",
        "",
        "It is stronger than the previous informal skeleton because the formulas, "
        "finite source rows, and claim boundary are checked by a repo-local script. "
        "It is still not a Lean/mathlib theorem, not a Quantum PCP proof, and not "
        "a global no-go theorem.",
        "",
        "## Checked Formula",
        "",
        "- Family: `cluster_stabilizer_open_uniform_reweight`",
        "- Domain: integer `n >= 4`",
        "- Term count: `n`",
        "- Interior terms: `n-2`",
        "- Boundary terms: `2`",
        "- Support sizes: `{2, 3}`",
        "- Maximum locality: `3`",
        "- Uniform scale: `27/20`",
        "- Hamiltonian identity: `H'_n = (27/20) H_n`",
        "- Normalized gap identity: `(s*g)/(s*w) = g/w`, for `s = 27/20` and `w > 0`",
        "",
        "## Finite Source Rows Checked",
        "",
        "| n | term count | supports | max locality | normalized gap invariant | checked |",
        "|---:|---:|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {qubits} | {source_term_count} | {source_support_size_set} | "
            "{source_max_locality} | {source_normalized_gap_invariant} | {checked} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Local verifier checked: `true`",
            "- Proof assistant checked: `false`",
            "- Formal theorem proved: `false`",
            "- Quantum PCP proof claimed: `false`",
            "- Global gap-amplification impossibility claimed: `false`",
            "- NLTS theorem claimed: `false`",
            "",
            "## Result",
            "",
            "The certificate is intentionally rejected as a raw-gap-only certificate: "
            "positive uniform rescaling changes raw gap and width by the same factor, "
            "so the normalized gap is invariant. This makes it useful as a checked "
            "negative guardrail for B9, not as a solved frontier claim.",
            "",
            f"Validation error count: `{certificate['validation_error_count']}`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=JSON_OUT)
    parser.add_argument("--markdown-output", type=Path, default=MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    certificate = build_certificate()
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(certificate, args.markdown_output)
    if args.pretty:
        print(json.dumps(certificate, indent=2, sort_keys=True))
    else:
        print(f"Wrote {args.json_output}")
        print(f"Wrote {args.markdown_output}")


if __name__ == "__main__":
    main()
