#!/usr/bin/env python3
"""Formula-derived B6 descriptor screen with B5-linked correlation proxies."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from b6_curated_materials_leakage_audit import MATERIALS


METHOD = "b6_formula_descriptor_screen_v0"
STATUS = "formula_descriptor_screen_not_material_discovery_claim"


ELEMENTS = {
    "H": {"z": 1, "mass": 1.008, "en": 2.20, "valence": 1, "block": "s"},
    "B": {"z": 5, "mass": 10.81, "en": 2.04, "valence": 3, "block": "p"},
    "C": {"z": 6, "mass": 12.011, "en": 2.55, "valence": 4, "block": "p"},
    "N": {"z": 7, "mass": 14.007, "en": 3.04, "valence": 5, "block": "p"},
    "O": {"z": 8, "mass": 15.999, "en": 3.44, "valence": 6, "block": "p"},
    "F": {"z": 9, "mass": 18.998, "en": 3.98, "valence": 7, "block": "p"},
    "Mg": {"z": 12, "mass": 24.305, "en": 1.31, "valence": 2, "block": "s"},
    "Cl": {"z": 17, "mass": 35.45, "en": 3.16, "valence": 7, "block": "p"},
    "K": {"z": 19, "mass": 39.098, "en": 0.82, "valence": 1, "block": "s"},
    "Ca": {"z": 20, "mass": 40.078, "en": 1.00, "valence": 2, "block": "s"},
    "Ge": {"z": 32, "mass": 72.630, "en": 2.01, "valence": 4, "block": "p"},
    "As": {"z": 33, "mass": 74.922, "en": 2.18, "valence": 5, "block": "p"},
    "Se": {"z": 34, "mass": 78.971, "en": 2.55, "valence": 6, "block": "p"},
    "Sr": {"z": 38, "mass": 87.62, "en": 0.95, "valence": 2, "block": "s"},
    "Y": {"z": 39, "mass": 88.906, "en": 1.22, "valence": 3, "block": "d"},
    "Nb": {"z": 41, "mass": 92.906, "en": 1.60, "valence": 5, "block": "d"},
    "Ru": {"z": 44, "mass": 101.07, "en": 2.20, "valence": 8, "block": "d"},
    "Cs": {"z": 55, "mass": 132.91, "en": 0.79, "valence": 1, "block": "s"},
    "Ba": {"z": 56, "mass": 137.33, "en": 0.89, "valence": 2, "block": "s"},
    "La": {"z": 57, "mass": 138.91, "en": 1.10, "valence": 3, "block": "f"},
    "Ce": {"z": 58, "mass": 140.12, "en": 1.12, "valence": 3, "block": "f"},
    "Pr": {"z": 59, "mass": 140.91, "en": 1.13, "valence": 3, "block": "f"},
    "Nd": {"z": 60, "mass": 144.24, "en": 1.14, "valence": 3, "block": "f"},
    "Sm": {"z": 62, "mass": 150.36, "en": 1.17, "valence": 3, "block": "f"},
    "Bi": {"z": 83, "mass": 208.98, "en": 2.02, "valence": 5, "block": "p"},
    "Tl": {"z": 81, "mass": 204.38, "en": 1.62, "valence": 3, "block": "p"},
    "Hg": {"z": 80, "mass": 200.59, "en": 2.00, "valence": 2, "block": "d"},
    "Co": {"z": 27, "mass": 58.933, "en": 1.88, "valence": 9, "block": "d"},
    "Cu": {"z": 29, "mass": 63.546, "en": 1.90, "valence": 11, "block": "d"},
    "Fe": {"z": 26, "mass": 55.845, "en": 1.83, "valence": 8, "block": "d"},
    "In": {"z": 49, "mass": 114.82, "en": 1.78, "valence": 3, "block": "p"},
    "Li": {"z": 3, "mass": 6.94, "en": 0.98, "valence": 1, "block": "s"},
    "Na": {"z": 11, "mass": 22.990, "en": 0.93, "valence": 1, "block": "s"},
    "Ni": {"z": 28, "mass": 58.693, "en": 1.91, "valence": 10, "block": "d"},
    "S": {"z": 16, "mass": 32.06, "en": 2.58, "valence": 6, "block": "p"},
}


D_OR_F_ELEMENTS = {symbol for symbol, row in ELEMENTS.items() if row["block"] in {"d", "f"}}
PAIRING_ELEMENTS = {"Cu", "Fe", "Ni", "Ru", "Co"}
LAYERING_ELEMENTS = {"O", "As", "Se", "S", "Cl"}


NEGATIVE_CONTROLS = [
    {
        "material_id": "La2CuO4_parent_negative",
        "formula": "La2CuO4",
        "family": "cuprate_parent_negative",
        "discovery_year": 1986,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "undoped cuprate parent negative control",
    },
    {
        "material_id": "BaFe2As2_parent_negative",
        "formula": "BaFe2As2",
        "family": "iron_pnictide_parent_negative",
        "discovery_year": 2008,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "iron-pnictide parent negative control",
    },
    {
        "material_id": "NdNiO3_negative",
        "formula": "NdNiO3",
        "family": "nickelate_parent_negative",
        "discovery_year": 1991,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "rare-earth nickelate non-superconducting control",
    },
    {
        "material_id": "LaNiO3_negative",
        "formula": "LaNiO3",
        "family": "nickelate_parent_negative",
        "discovery_year": 1971,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "metallic nickelate negative control",
    },
    {
        "material_id": "CuO_negative",
        "formula": "CuO",
        "family": "binary_oxide_negative",
        "discovery_year": 1900,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "binary oxide negative control",
    },
    {
        "material_id": "FeSe_ambient_low_tc_control",
        "formula": "FeSe",
        "family": "iron_chalcogenide_low_tc_control",
        "discovery_year": 2008,
        "tc_k": 8.0,
        "pressure_gpa": 0.0,
        "source_lineage": "ambient FeSe low-Tc control",
    },
    {
        "material_id": "MgO_negative",
        "formula": "MgO",
        "family": "wide_gap_oxide_negative",
        "discovery_year": 1900,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "wide-gap oxide negative control",
    },
    {
        "material_id": "Graphite_negative",
        "formula": "C",
        "family": "carbon_negative",
        "discovery_year": 1900,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "graphitic carbon negative control",
    },
    {
        "material_id": "NaCl_negative",
        "formula": "NaCl",
        "family": "ionic_salt_negative",
        "discovery_year": 1900,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "simple ionic insulator negative control",
    },
    {
        "material_id": "Bi2O3_negative",
        "formula": "Bi2O3",
        "family": "bismuth_oxide_negative",
        "discovery_year": 1900,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "bismuth oxide negative control",
    },
    {
        "material_id": "PrNiO2_parent_negative",
        "formula": "PrNiO2",
        "family": "nickelate_parent_negative",
        "discovery_year": 2020,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "infinite-layer nickelate parent negative control",
    },
    {
        "material_id": "H2S_low_pressure_negative",
        "formula": "H2S",
        "family": "hydride_low_pressure_negative",
        "discovery_year": 2014,
        "tc_k": 0.0,
        "pressure_gpa": 0.0,
        "source_lineage": "hydride without megabar pressure negative control",
    },
]


def parse_formula(formula: str) -> tuple[Counter[str], list[str]]:
    cleaned = formula
    cleaned = re.sub(r"^[a-z]+-", "", cleaned)
    cleaned = cleaned.replace("delta", "d")
    tokens = re.findall(r"([A-Z][a-z]?)([0-9]*\.?[0-9]*)?", cleaned)
    counts: Counter[str] = Counter()
    unknown: list[str] = []
    for symbol, number in tokens:
        if symbol not in ELEMENTS:
            unknown.append(symbol)
            continue
        count = float(number) if number else 1.0
        counts[symbol] += count
    return counts, unknown


def weighted_mean(counts: Counter[str], key: str) -> float:
    total = sum(counts.values()) or 1.0
    return sum(ELEMENTS[element][key] * count for element, count in counts.items()) / total


def weighted_std(counts: Counter[str], key: str) -> float:
    avg = weighted_mean(counts, key)
    total = sum(counts.values()) or 1.0
    variance = sum(count * (ELEMENTS[element][key] - avg) ** 2 for element, count in counts.items()) / total
    return math.sqrt(variance)


def fraction(counts: Counter[str], symbols: set[str]) -> float:
    total = sum(counts.values()) or 1.0
    return sum(count for element, count in counts.items() if element in symbols) / total


def formula_descriptors(record: dict) -> dict:
    counts, unknown = parse_formula(record["formula"])
    total_atoms = sum(counts.values()) or 1.0
    formula_mass = sum(ELEMENTS[element]["mass"] * count for element, count in counts.items())
    transition_fraction = fraction(counts, D_OR_F_ELEMENTS)
    active_pairing_fraction = fraction(counts, PAIRING_ELEMENTS)
    anion_layer_fraction = fraction(counts, LAYERING_ELEMENTS)
    hydrogen_fraction = fraction(counts, {"H"})
    oxygen_fraction = fraction(counts, {"O"})
    light_element_fraction = sum(count for element, count in counts.items() if ELEMENTS[element]["z"] <= 16) / total_atoms
    valence_mean = weighted_mean(counts, "valence")
    valence_std = weighted_std(counts, "valence")
    en_mean = weighted_mean(counts, "en")
    en_std = weighted_std(counts, "en")
    z_mean = weighted_mean(counts, "z")
    z_std = weighted_std(counts, "z")
    b5_correlation_pressure_proxy = (
        (0.45 * transition_fraction + 0.35 * active_pairing_fraction + 0.20 * valence_std / 4.0)
        * (1.0 + 0.4 * anion_layer_fraction)
    )
    b5_hubbard_screening_proxy = active_pairing_fraction * (1.0 + en_std) / (1.0 + hydrogen_fraction)
    pressure_penalty = min(1.0, float(record.get("pressure_gpa", 0.0)) / 80.0)
    layered_pairing_proxy = active_pairing_fraction * anion_layer_fraction * (1.0 + oxygen_fraction)
    hydride_pressure_proxy = hydrogen_fraction * (1.0 - pressure_penalty)
    formula_score = (
        1.25 * b5_correlation_pressure_proxy
        + 0.90 * layered_pairing_proxy
        + 0.55 * b5_hubbard_screening_proxy
        + 0.35 * light_element_fraction
        - 0.50 * pressure_penalty
        - 0.45 * hydride_pressure_proxy
    )
    return {
        "parsed_elements": dict(sorted(counts.items())),
        "unknown_formula_tokens": sorted(set(unknown)),
        "total_parsed_atoms": total_atoms,
        "formula_mass": formula_mass,
        "mean_atomic_number": z_mean,
        "atomic_number_std": z_std,
        "mean_electronegativity": en_mean,
        "electronegativity_std": en_std,
        "mean_valence_proxy": valence_mean,
        "valence_std_proxy": valence_std,
        "transition_or_f_fraction": transition_fraction,
        "active_pairing_element_fraction": active_pairing_fraction,
        "anion_layer_fraction": anion_layer_fraction,
        "hydrogen_fraction": hydrogen_fraction,
        "oxygen_fraction": oxygen_fraction,
        "light_element_fraction": light_element_fraction,
        "pressure_penalty": pressure_penalty,
        "layered_pairing_proxy": layered_pairing_proxy,
        "b5_correlation_pressure_proxy": b5_correlation_pressure_proxy,
        "b5_hubbard_screening_proxy": b5_hubbard_screening_proxy,
        "formula_descriptor_score": formula_score,
    }


def average_precision(rows: list[dict], top_k: int, positive_key: str = "is_high_tc") -> float:
    hits = 0
    precision_sum = 0.0
    positives = sum(1 for row in rows if row[positive_key])
    if positives == 0:
        return 0.0
    for index, row in enumerate(rows[:top_k], start=1):
        if row[positive_key]:
            hits += 1
            precision_sum += hits / index
    return precision_sum / min(positives, top_k)


def precision_at_k(rows: list[dict], top_k: int, positive_key: str = "is_high_tc") -> float:
    if top_k <= 0:
        return 0.0
    return sum(1 for row in rows[:top_k] if row[positive_key]) / top_k


def family_prior_score(records: list[dict]) -> dict[str, float]:
    grouped: dict[str, list[bool]] = defaultdict(list)
    for record in records:
        grouped[record["family"]].append(record["is_high_tc"])
    return {family: sum(values) / len(values) for family, values in grouped.items()}


def enrich_records(high_tc_threshold: float) -> list[dict]:
    records = []
    for source, rows in [("curated", MATERIALS), ("negative_control", NEGATIVE_CONTROLS)]:
        for row in rows:
            record = dict(row)
            record.setdefault("correlation_strength", None)
            record.setdefault("spin_fluctuation", None)
            record.setdefault("phonon_lambda", None)
            record.setdefault("dimensionality", None)
            record.setdefault("carrier_tunability", None)
            record.setdefault("disorder_risk", None)
            record.setdefault("competing_order", None)
            record["source_subset"] = source
            record["is_high_tc"] = float(record["tc_k"]) >= high_tc_threshold
            record.update(formula_descriptors(record))
            records.append(record)
    return records


def build_report(high_tc_threshold: float, split_year: int, top_k: int) -> dict:
    records = enrich_records(high_tc_threshold)
    formula_ranked = sorted(records, key=lambda row: row["formula_descriptor_score"], reverse=True)
    priors = family_prior_score(records)
    family_ranked = sorted(records, key=lambda row: priors[row["family"]], reverse=True)
    post_split = [row for row in records if int(row["discovery_year"]) > split_year]
    post_formula_ranked = sorted(post_split, key=lambda row: row["formula_descriptor_score"], reverse=True)
    post_family_ranked = sorted(post_split, key=lambda row: priors[row["family"]], reverse=True)
    expanded_negative_count = sum(1 for row in records if row["source_subset"] == "negative_control")
    validation_errors = []
    if len(records) <= len(MATERIALS):
        validation_errors.append("expanded negative controls were not added")
    if expanded_negative_count < 10:
        validation_errors.append("expected at least 10 expanded negative controls")
    if any(row["b5_correlation_pressure_proxy"] is None for row in records):
        validation_errors.append("missing B5-linked correlation proxy")
    if not any(row["unknown_formula_tokens"] for row in records):
        validation_errors.append("parser should expose unknown tokens for complex formulas instead of hiding them")
    if average_precision(formula_ranked, top_k) <= 0:
        validation_errors.append("formula descriptor ranking AP must be positive")
    return {
        "benchmark_id": "B6",
        "problem_id": 37,
        "title": "B6 formula-derived descriptor screen",
        "status": STATUS,
        "method": METHOD,
        "model_status": "formula_element_table_descriptors_with_b5_correlation_proxy_not_material_discovery",
        "high_tc_threshold_k": high_tc_threshold,
        "split_year": split_year,
        "top_k": top_k,
        "record_count": len(records),
        "curated_record_count": len(MATERIALS),
        "expanded_negative_control_count": expanded_negative_count,
        "family_count": len({row["family"] for row in records}),
        "post_split_record_count": len(post_split),
        "post_split_positive_count": sum(1 for row in post_split if row["is_high_tc"]),
        "metrics": {
            "formula_precision_at_k": precision_at_k(formula_ranked, top_k),
            "formula_average_precision_at_k": average_precision(formula_ranked, top_k),
            "family_prior_precision_at_k": precision_at_k(family_ranked, top_k),
            "family_prior_average_precision_at_k": average_precision(family_ranked, top_k),
            "post_split_formula_precision_at_k": precision_at_k(post_formula_ranked, min(top_k, len(post_split))),
            "post_split_formula_average_precision_at_k": average_precision(post_formula_ranked, min(top_k, len(post_split))),
            "post_split_family_prior_average_precision_at_k": average_precision(post_family_ranked, min(top_k, len(post_split))),
        },
        "descriptor_channels": [
            "formula_mass",
            "mean_atomic_number",
            "electronegativity_std",
            "valence_std_proxy",
            "active_pairing_element_fraction",
            "anion_layer_fraction",
            "light_element_fraction",
            "b5_correlation_pressure_proxy",
            "b5_hubbard_screening_proxy",
            "formula_descriptor_score",
        ],
        "claim_boundary": {
            "material_discovery_claimed": False,
            "mechanism_solved": False,
            "complete_materials_database": False,
            "computed_quantum_observable_claimed": False,
            "uses_formula_derived_descriptors": True,
            "uses_b5_linked_proxy": True,
            "what_is_supported": (
                "A deterministic formula parser and embedded element table now produce structural/electronic "
                "descriptor proxies plus B5-linked correlation/screening proxies over the curated table and "
                "expanded negative controls."
            ),
            "what_is_not_supported": (
                "The result is not a materials discovery, not a solved high-Tc mechanism, not a complete "
                "database, and not a computed DFT/DMRG/quantum observable."
            ),
        },
        "top_formula_rows": formula_ranked[:top_k],
        "top_post_split_formula_rows": post_formula_ranked[: min(top_k, len(post_split))],
        "records": records,
        "validation_errors": validation_errors,
    }


def markdown(report: dict) -> str:
    lines = [
        "# B6 Formula-Derived Descriptor Screen v0.1",
        "",
        f"- Status: {report['status']}",
        f"- Method: {report['method']}",
        f"- Model status: {report['model_status']}",
        f"- Records: {report['record_count']}",
        f"- Curated records: {report['curated_record_count']}",
        f"- Expanded negative controls: {report['expanded_negative_control_count']}",
        f"- Families: {report['family_count']}",
        f"- High-Tc threshold: {report['high_tc_threshold_k']} K",
        f"- Formula AP@{report['top_k']}: {report['metrics']['formula_average_precision_at_k']}",
        f"- Family-prior AP@{report['top_k']}: {report['metrics']['family_prior_average_precision_at_k']}",
        f"- Post-split formula AP: {report['metrics']['post_split_formula_average_precision_at_k']}",
        f"- Post-split family-prior AP: {report['metrics']['post_split_family_prior_average_precision_at_k']}",
        f"- Validation errors: {report['validation_errors']}",
        "",
        "## Top Formula-Descriptor Rows",
        "",
        "| rank | material | formula | family | Tc K | source | score | B5 corr proxy | B5 screen proxy | parsed elements |",
        "|---:|---|---|---|---:|---|---:|---:|---:|---|",
    ]
    for index, row in enumerate(report["top_formula_rows"], start=1):
        lines.append(
            f"| {index} | {row['material_id']} | {row['formula']} | {row['family']} | "
            f"{row['tc_k']} | {row['source_subset']} | {row['formula_descriptor_score']:.4f} | "
            f"{row['b5_correlation_pressure_proxy']:.4f} | {row['b5_hubbard_screening_proxy']:.4f} | "
            f"{row['parsed_elements']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
        ]
    )
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Next Gate",
            "",
            "Replace these formula-derived proxies with computed structural/electronic descriptors",
            "from crystallographic records, DFT summaries, or B5 tensor/DMRG observables. Expand",
            "the post-2008 negative set so family priors and random baselines cannot saturate.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--high-tc-threshold", type=float, default=30.0)
    parser.add_argument("--split-year", type=int, default=2008)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--json-output", type=Path, default=Path("results/B6_formula_descriptor_screen_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B6_formula_descriptor_screen.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.high_tc_threshold, args.split_year, args.top_k)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "method": report["method"],
                "record_count": report["record_count"],
                "expanded_negative_control_count": report["expanded_negative_control_count"],
                **report["metrics"],
                "validation_errors": report["validation_errors"],
            },
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
