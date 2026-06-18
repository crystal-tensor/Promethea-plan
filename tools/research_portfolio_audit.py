#!/usr/bin/env python3
"""Audit the long-horizon quantum research portfolio files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import yaml


CATALOG_RE = re.compile(r"^(\d+)\.\s+\*\*(.+?)\*\*")
TABLE_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|")
ATTACK_ID_RE = re.compile(r"^\*\*Problem ID:\*\*\s*(\d+)")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_catalog(path: Path) -> dict[int, str]:
    problems: dict[int, str] = {}
    for line in read(path).splitlines():
        match = CATALOG_RE.match(line)
        if match:
            problems[int(match.group(1))] = match.group(2).strip()
    return problems


def split_markdown_table_row(line: str) -> list[str]:
    return [re.sub(r"\s+", " ", cell.strip()) for cell in line.strip().strip("|").split("|")]


def parse_catalog_metadata_matrix(path: Path) -> list[dict[str, str]]:
    text = read(path)
    marker = "## Frozen Metadata Matrix"
    if marker not in text:
        return []

    columns = [
        "id",
        "problem",
        "discipline_cluster",
        "source_lineage",
        "unresolved_age",
        "core_difficulty",
        "prior_approaches_and_milestones",
        "frozen_project_positioning",
    ]
    rows: list[dict[str, str]] = []
    in_table = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            if in_table and rows:
                break
            continue
        cells = split_markdown_table_row(line)
        if cells[:3] == ["ID", "Problem", "Discipline cluster"]:
            in_table = True
            continue
        if not in_table or set(cells[0]) <= {"-", ":"}:
            continue
        if len(cells) == len(columns):
            rows.append(dict(zip(columns, cells)))
    return rows


def parse_rank_table(path: Path, heading: str | None = None) -> list[dict]:
    rows: list[dict] = []
    active = heading is None
    for line in read(path).splitlines():
        if heading and line.strip() == heading:
            active = True
            continue
        if heading and active and line.startswith("## ") and line.strip() != heading:
            break
        if not active:
            continue
        match = TABLE_ROW_RE.match(line)
        if match:
            rows.append(
                {
                    "rank": int(match.group(1)),
                    "id": int(match.group(2)),
                    "problem": match.group(3).strip(),
                }
            )
    return rows


def parse_attack_ids(path: Path) -> list[int]:
    ids: list[int] = []
    for line in read(path).splitlines():
        match = ATTACK_ID_RE.match(line)
        if match:
            ids.append(int(match.group(1)))
    return ids


def path_exists_from(base: Path, maybe_relative: str) -> bool:
    return (base / maybe_relative).resolve().exists()


def audit(root: Path) -> dict:
    research = root / "research"
    benchmarks = root / "benchmarks"
    results = root / "results"
    catalog_path = research / "problem_catalog_100.md"
    catalog_json_path = research / "problem_catalog_100.json"
    scoring_path = research / "scoring_matrix.md"
    attack_path = research / "attack_pack_10.md"
    evidence_path = research / "top20_evidence_map.md"
    roadmap_path = research / "roadmap_12_months.md"
    status_html_path = research / "project_status_plan.html"
    execution_board_path = research / "top10_execution_board.json"
    dossier_path = research / "top10_problem_dossiers.json"
    dossier_markdown_path = research / "top10_problem_dossiers.md"
    technical_resolution_path = research / "technical_resolution_program.json"
    technical_resolution_markdown_path = research / "technical_resolution_program.md"
    translation_path = research / "translation_pipeline.json"
    translation_markdown_path = research / "translation_pipeline.md"
    b1_certificate_report_path = research / "B1_certificate_report.json"
    b1_routing_diagnostic_path = research / "B1_routing_baseline_diagnostic.json"
    b1_heavyhex_diagnostic_path = research / "B1_heavyhex_routing_diagnostic.json"
    b1_heavyhex_e2e_path = research / "B1_heavyhex_end_to_end_report.json"
    b1_heavyhex_e2e_suite_path = research / "B1_heavyhex_end_to_end_suite.json"
    b1_post_routing_profile_path = research / "B1_post_routing_bottleneck_profile.json"
    b1_swap_macro_path = research / "B1_post_routing_swap_macro_report.json"
    b1_virtual_swap_path = research / "B1_virtual_swap_elimination_report.json"
    b1_virtual_swap_replay_path = research / "B1_virtual_swap_replay_report.json"
    b1_post_virtual_swap_1q_path = results / "B1_post_virtual_swap_1q_resynth_v0.json"
    b1_native_t_resource_path = results / "B1_native_t_resource_optimizer_v0.json"
    b1_control_rz_commute_path = results / "B1_control_rz_commute_optimizer_v0.json"
    b1_u3_phase_factored_path = results / "B1_u3_phase_factored_optimizer_v0.json"
    b1_b7_gcm_h6_target_selector_path = results / "B1_B7_gcm_h6_target_selector_v0.json"
    b1_b7_gcm_h6_cone_feasibility_path = results / "B1_B7_gcm_h6_cone_feasibility_gate_v0.json"
    b1_b7_cone01_phase_removal_path = results / "B1_B7_cone01_phase_removal_gate_v0.json"
    b1_b7_cone01_euler_reabsorption_path = results / "B1_B7_cone01_euler_reabsorption_gate_v0.json"
    b1_b7_cone01_parameter_transfer_path = results / "B1_B7_cone01_parameter_transfer_gate_v0.json"
    b1_b7_cone01_theta_sharing_path = results / "B1_B7_cone01_theta_sharing_ledger_gate_v0.json"
    b1_b7_cone01_shared_theta_synthesis_object_path = (
        results / "B1_B7_cone01_shared_theta_synthesis_object_gate_v0.json"
    )
    b1_b7_cone01_shared_theta_replay_verifier_path = (
        results / "B1_B7_cone01_shared_theta_replay_verifier_gate_v0.json"
    )
    b1_b7_cone01_shared_theta_layout_routing_path = (
        results / "B1_B7_cone01_shared_theta_layout_routing_gate_v0.json"
    )
    b1_b7_cone01_shared_theta_factory_amortization_path = (
        results / "B1_B7_cone01_shared_theta_factory_amortization_gate_v0.json"
    )
    b1_b7_cone01_shared_theta_error_budget_path = (
        results / "B1_B7_cone01_shared_theta_error_budget_gate_v0.json"
    )
    b1_b7_cone01_theta_sharing_cost_model_path = (
        results / "B1_B7_cone01_theta_sharing_cost_model_gate_v0.json"
    )
    b1_synthetic_noise_path = research / "B1_synthetic_noise_proxy_report.json"
    b1_manifest_path = benchmarks / "B1_circuit_compression.yaml"
    b2_manifest_path = benchmarks / "B2_qec_overhead.yaml"
    b3_manifest_path = benchmarks / "B3_molecular_reaction_dynamics.yaml"
    b4_manifest_path = benchmarks / "B4_verifiable_quantum_advantage.yaml"
    b5_manifest_path = benchmarks / "B5_strongly_correlated_matter.yaml"
    b6_manifest_path = benchmarks / "B6_high_temperature_superconductivity.yaml"
    b7_manifest_path = benchmarks / "B7_fault_tolerance_codesign.yaml"
    b8_manifest_path = benchmarks / "B8_classical_verification_outputs.yaml"
    b9_manifest_path = benchmarks / "B9_quantum_pcp_local_hamiltonian.yaml"
    b10_manifest_path = benchmarks / "B10_bqp_boundary_map.yaml"

    errors: list[str] = []
    warnings: list[str] = []

    catalog = parse_catalog(catalog_path)
    catalog_ids = sorted(catalog)
    expected_ids = list(range(1, 101))
    if catalog_ids != expected_ids:
        missing = sorted(set(expected_ids) - set(catalog_ids))
        extra = sorted(set(catalog_ids) - set(expected_ids))
        errors.append(f"catalog ids are not exactly 1..100; missing={missing}, extra={extra}")
    catalog_metadata_rows = parse_catalog_metadata_matrix(catalog_path)
    catalog_metadata_ids = sorted(int(row["id"]) for row in catalog_metadata_rows if row.get("id", "").isdigit())
    required_catalog_metadata_fields = [
        "problem",
        "discipline_cluster",
        "source_lineage",
        "unresolved_age",
        "core_difficulty",
        "prior_approaches_and_milestones",
        "frozen_project_positioning",
    ]
    incomplete_catalog_metadata = [
        int(row["id"])
        for row in catalog_metadata_rows
        if row.get("id", "").isdigit()
        and any(not row.get(field, "").strip() for field in required_catalog_metadata_fields)
    ]
    if catalog_metadata_ids != expected_ids:
        missing = sorted(set(expected_ids) - set(catalog_metadata_ids))
        extra = sorted(set(catalog_metadata_ids) - set(expected_ids))
        errors.append(f"catalog metadata matrix ids are not exactly 1..100; missing={missing}, extra={extra}")
    if incomplete_catalog_metadata:
        errors.append(f"catalog metadata rows have incomplete frozen fields: {incomplete_catalog_metadata}")
    if "Non-revision covenant" not in read(catalog_path):
        errors.append("catalog missing final non-revision covenant")
    catalog_json = json.loads(read(catalog_json_path)) if catalog_json_path.exists() else {}
    if not catalog_json_path.exists():
        errors.append(f"missing catalog JSON export: {catalog_json_path}")
    if catalog_json.get("record_count") != 100:
        errors.append("catalog JSON record_count must remain 100")
    if catalog_json.get("status") != "frozen" or catalog_json.get("freeze_lock") is not True:
        errors.append("catalog JSON must remain frozen with freeze_lock=true")
    if catalog_json.get("user_freeze_directive_date") != "2026-06-18":
        errors.append("catalog JSON must retain the final user freeze directive date")
    if not str(catalog_json.get("user_freeze_directive", "")).strip():
        errors.append("catalog JSON must retain the final user freeze directive")
    expected_completion_scope = {
        "stable_id",
        "problem_name",
        "discipline_cluster",
        "discipline_supergroup",
        "source_lineage",
        "source_lineage_group",
        "approximate_unresolved_age",
        "problem_statement",
        "quantum_relevance",
        "origin_or_source",
        "source_confidence",
        "core_difficulty",
        "prior_approaches_and_milestones",
        "frozen_project_positioning",
        "top10_membership_flag",
    }
    observed_completion_scope = set(catalog_json.get("metadata_completion_scope", []))
    if observed_completion_scope != expected_completion_scope:
        errors.append("catalog JSON metadata_completion_scope changed or is incomplete")
    expected_source_confidence_labels = {"A", "B", "C", "D"}
    observed_source_confidence_labels = set(catalog_json.get("source_confidence_labels", {}).keys())
    if observed_source_confidence_labels != expected_source_confidence_labels:
        errors.append("catalog JSON source_confidence_labels must retain A/B/C/D")
    if catalog_json.get("top10_mapping") != {
        "B1": 25,
        "B2": 22,
        "B3": 49,
        "B4": 16,
        "B5": 38,
        "B6": 37,
        "B7": 21,
        "B8": 30,
        "B9": 17,
        "B10": 11,
    }:
        errors.append("catalog JSON Top 10 mapping changed")
    json_record_ids = [int(record.get("id")) for record in catalog_json.get("records", []) if "id" in record]
    if json_record_ids != expected_ids:
        errors.append("catalog JSON records must preserve the frozen 1..100 id sequence")
    if len(catalog_json.get("discipline_supergroups", [])) != 9:
        errors.append("catalog JSON must retain 9 discipline supergroups")
    if len(catalog_json.get("source_lineage_groups", {})) != 4:
        errors.append("catalog JSON must retain 4 source-lineage audit groups")
    required_json_record_fields = [
        "discipline_supergroup",
        "discipline_cluster",
        "source_lineage_group",
        "source_lineage",
        "unresolved_age",
        "core_difficulty",
        "prior_approaches_and_milestones",
        "frozen_project_positioning",
        "title",
        "problem_statement",
        "quantum_relevance",
        "origin",
        "who_proposed_or_source",
        "first_formulated_or_crystallized",
        "unresolved_age_years_as_of_2026",
        "difficulty_core",
        "prior_approaches",
        "major_milestones",
        "project_positioning",
        "source_confidence",
        "source_confidence_reason",
        "catalog_work_status",
    ]
    incomplete_json_records = [
        int(record.get("id"))
        for record in catalog_json.get("records", [])
        if "id" in record
        and any(not str(record.get(field, "")).strip() for field in required_json_record_fields)
    ]
    if incomplete_json_records:
        errors.append(
            "catalog JSON records must retain final per-record discipline/source metadata; "
            f"incomplete ids={incomplete_json_records}"
        )
    expected_json_supergroups = {
        "Mathematics and complexity foundations",
        "Quantum computing core",
        "Physics and cosmology",
        "Chemistry, materials, and energy",
        "Life science and medicine",
        "AI, cognition, and automated science",
        "Earth, climate, and ecology",
        "Cryptography, security, and social systems",
        "Engineering, space, and long-term civilization",
    }
    observed_json_supergroups = {
        str(record.get("discipline_supergroup"))
        for record in catalog_json.get("records", [])
        if record.get("discipline_supergroup")
    }
    observed_json_source_groups = {
        str(record.get("source_lineage_group"))
        for record in catalog_json.get("records", [])
        if record.get("source_lineage_group")
    }
    if observed_json_supergroups != expected_json_supergroups:
        errors.append(
            "catalog JSON per-record discipline supergroups changed: "
            f"{sorted(observed_json_supergroups)}"
        )
    if observed_json_source_groups != set(catalog_json.get("source_lineage_groups", {}).keys()):
        errors.append(
            "catalog JSON per-record source-lineage groups must match source_lineage_groups keys"
        )
    if "Per-record final routing lock" not in read(catalog_path):
        errors.append("catalog Markdown missing per-record final routing lock")
    if "Final user freeze seal" not in read(catalog_path):
        errors.append("catalog Markdown missing final user freeze seal")
    completion_audit = catalog_json.get("completion_audit", {})
    if completion_audit.get("record_count") != 100:
        errors.append("catalog JSON completion_audit must confirm 100 records")
    if completion_audit.get("records_with_problem_statement") != 100:
        errors.append("catalog JSON completion_audit must confirm 100 problem statements")
    if completion_audit.get("records_with_quantum_relevance") != 100:
        errors.append("catalog JSON completion_audit must confirm 100 quantum relevance notes")
    if completion_audit.get("records_with_source_confidence") != 100:
        errors.append("catalog JSON completion_audit must confirm 100 source confidence labels")
    if completion_audit.get("final_action") != "catalog metadata complete; stop further 100-problem catalog work":
        errors.append("catalog JSON completion_audit must retain the final stop action")

    scoring_rows = parse_rank_table(scoring_path, "## Top 20 First-Pass Scores")
    scoring_top20_ids = [row["id"] for row in scoring_rows[:20]]
    if len(scoring_top20_ids) != 20:
        errors.append(f"scoring matrix has {len(scoring_top20_ids)} Top 20 rows, expected 20")
    unknown_scoring = [pid for pid in scoring_top20_ids if pid not in catalog]
    if unknown_scoring:
        errors.append(f"scoring matrix references ids absent from catalog: {unknown_scoring}")

    evidence_rows = parse_rank_table(evidence_path)
    evidence_top20_ids = [row["id"] for row in evidence_rows[:20]]
    if evidence_top20_ids != scoring_top20_ids:
        errors.append(
            "Top 20 evidence ids differ from scoring ids: "
            f"scoring={scoring_top20_ids}, evidence={evidence_top20_ids}"
        )

    attack_ids = parse_attack_ids(attack_path)
    if len(attack_ids) != 10:
        errors.append(f"attack pack has {len(attack_ids)} problem ids, expected 10")
    expected_tier1 = scoring_top20_ids[:10]
    if attack_ids != expected_tier1:
        errors.append(f"attack pack ids differ from Tier 1 ids: attack={attack_ids}, tier1={expected_tier1}")

    execution_board = {}
    execution_summary = {
        "path": str(execution_board_path),
        "exists": execution_board_path.exists(),
        "direction_count": 0,
        "problem_ids_match_attack_pack": False,
        "b_ids_are_b1_to_b10": False,
        "lanes": {},
    }
    if not execution_board_path.exists():
        errors.append(f"missing Top 10 execution board: {execution_board_path}")
    else:
        execution_board = json.loads(read(execution_board_path))
        directions = execution_board.get("directions", [])
        direction_problem_ids = [row.get("problem_id") for row in directions]
        direction_b_ids = [row.get("b_id") for row in directions]
        expected_b_ids = [f"B{i}" for i in range(1, 11)]
        execution_summary.update(
            {
                "direction_count": len(directions),
                "problem_ids_match_attack_pack": direction_problem_ids == attack_ids,
                "b_ids_are_b1_to_b10": direction_b_ids == expected_b_ids,
                "lanes": execution_board.get("lanes", {}),
            }
        )
        if len(directions) != 10:
            errors.append(f"execution board has {len(directions)} directions, expected 10")
        if direction_problem_ids != attack_ids:
            errors.append(
                "execution board problem ids differ from attack pack ids: "
                f"execution={direction_problem_ids}, attack={attack_ids}"
            )
        if direction_b_ids != expected_b_ids:
            errors.append(f"execution board b_ids differ from B1..B10: {direction_b_ids}")
        required_fields = [
            "b_id",
            "problem_id",
            "title",
            "priority_lane",
            "current_maturity",
            "strongest_evidence",
            "30_day_gate",
            "next_artifact",
            "kill_condition",
            "downstream_translation_route",
        ]
        for row in directions:
            missing_fields = [field for field in required_fields if not row.get(field)]
            if missing_fields:
                errors.append(f"execution board {row.get('b_id', '<unknown>')} missing fields: {missing_fields}")
        if len(execution_board.get("lanes", {})) < 4:
            errors.append("execution board should define at least 4 portfolio lanes")
        if len(execution_board.get("next_30_days", {})) != 4:
            errors.append("execution board should define exactly 4 next-30-day week buckets")

    dossier_summary = {
        "path": str(dossier_path),
        "markdown_path": str(dossier_markdown_path),
        "exists": dossier_path.exists(),
        "markdown_exists": dossier_markdown_path.exists(),
        "dossier_count": 0,
        "problem_ids_match_attack_pack": False,
        "b_ids_are_b1_to_b10": False,
        "all_required_fields_present": False,
        "maturity_scores": {},
    }
    if not dossier_path.exists():
        errors.append(f"missing Top 10 problem dossier JSON: {dossier_path}")
    if not dossier_markdown_path.exists():
        errors.append(f"missing Top 10 problem dossier markdown: {dossier_markdown_path}")
    if dossier_path.exists():
        dossier_payload = json.loads(read(dossier_path))
        dossiers = dossier_payload.get("dossiers", [])
        dossier_problem_ids = [row.get("problem_id") for row in dossiers]
        dossier_b_ids = [row.get("b_id") for row in dossiers]
        expected_b_ids = [f"B{i}" for i in range(1, 11)]
        required_dossier_fields = [
            "b_id",
            "problem_id",
            "title",
            "what_to_solve",
            "lineage",
            "unresolved_duration",
            "current_difficulty",
            "prior_approaches",
            "our_solution",
            "completed",
            "remaining_steps",
            "maturity_score",
        ]
        missing_by_id = {}
        for row in dossiers:
            missing_fields = [field for field in required_dossier_fields if row.get(field) in (None, "", [])]
            if missing_fields:
                missing_by_id[row.get("b_id", "<unknown>")] = missing_fields
            score = row.get("maturity_score")
            if not isinstance(score, int) or not 0 <= score <= 100:
                errors.append(f"dossier {row.get('b_id', '<unknown>')} has invalid maturity_score: {score}")
        dossier_summary.update(
            {
                "dossier_count": len(dossiers),
                "problem_ids_match_attack_pack": dossier_problem_ids == attack_ids,
                "b_ids_are_b1_to_b10": dossier_b_ids == expected_b_ids,
                "all_required_fields_present": not missing_by_id,
                "maturity_scores": {row.get("b_id"): row.get("maturity_score") for row in dossiers},
            }
        )
        if len(dossiers) != 10:
            errors.append(f"problem dossier has {len(dossiers)} dossiers, expected 10")
        if dossier_problem_ids != attack_ids:
            errors.append(
                "problem dossier ids differ from attack pack ids: "
                f"dossier={dossier_problem_ids}, attack={attack_ids}"
            )
        if dossier_b_ids != expected_b_ids:
            errors.append(f"problem dossier b_ids differ from B1..B10: {dossier_b_ids}")
        for b_id, missing_fields in missing_by_id.items():
            errors.append(f"problem dossier {b_id} missing fields: {missing_fields}")
        if "progress_scale" not in dossier_payload:
            errors.append("problem dossier JSON must define progress_scale")

    technical_resolution_summary = {
        "path": str(technical_resolution_path),
        "markdown_path": str(technical_resolution_markdown_path),
        "exists": technical_resolution_path.exists(),
        "markdown_exists": technical_resolution_markdown_path.exists(),
        "direction_count": 0,
        "b_ids_are_b1_to_b10": False,
        "all_required_fields_present": False,
        "success_criterion": None,
    }
    if not technical_resolution_path.exists():
        errors.append(f"missing technical resolution program JSON: {technical_resolution_path}")
    if not technical_resolution_markdown_path.exists():
        errors.append(f"missing technical resolution program markdown: {technical_resolution_markdown_path}")
    if technical_resolution_path.exists():
        technical_payload = json.loads(read(technical_resolution_path))
        technical_rows = technical_payload.get("directions", [])
        technical_b_ids = [row.get("b_id") for row in technical_rows]
        expected_b_ids = [f"B{i}" for i in range(1, 11)]
        required_technical_fields = [
            "b_id",
            "technical_solution_target",
            "current_evidence",
            "main_blocker",
            "next_experiment",
            "gate_status",
        ]
        missing_by_id = {}
        for row in technical_rows:
            missing_fields = [field for field in required_technical_fields if row.get(field) in (None, "", [])]
            if missing_fields:
                missing_by_id[row.get("b_id", "<unknown>")] = missing_fields
        technical_resolution_summary.update(
            {
                "direction_count": len(technical_rows),
                "b_ids_are_b1_to_b10": technical_b_ids == expected_b_ids,
                "all_required_fields_present": not missing_by_id,
                "success_criterion": technical_payload.get("current_success_criterion"),
            }
        )
        if len(technical_rows) != 10:
            errors.append(f"technical resolution program has {len(technical_rows)} directions, expected 10")
        if technical_b_ids != expected_b_ids:
            errors.append(f"technical resolution program b_ids differ from B1..B10: {technical_b_ids}")
        for b_id, missing_fields in missing_by_id.items():
            errors.append(f"technical resolution program {b_id} missing fields: {missing_fields}")
        if technical_payload.get("current_success_criterion") != (
            "technical_resolution_before_publication_patent_financing_or_productization"
        ):
            errors.append("technical resolution program must keep technical resolution as the current success criterion")

    translation_summary = {
        "path": str(translation_path),
        "markdown_path": str(translation_markdown_path),
        "exists": translation_path.exists(),
        "markdown_exists": translation_markdown_path.exists(),
        "status": None,
        "manuscript_count": 0,
        "patent_disclosure_count": 0,
        "fundable_project_count": 0,
        "tool_count": 0,
        "has_lead_tool": False,
        "targets_met": False,
    }
    if not translation_path.exists():
        errors.append(f"missing translation pipeline JSON: {translation_path}")
    if not translation_markdown_path.exists():
        errors.append(f"missing translation pipeline markdown: {translation_markdown_path}")
    if translation_path.exists():
        translation_payload = json.loads(read(translation_path))
        manuscripts = translation_payload.get("manuscripts", [])
        patent_disclosures = translation_payload.get("patent_disclosures", [])
        fundable_projects = translation_payload.get("fundable_projects", [])
        tools = translation_payload.get("tools", [])
        target_counts = translation_payload.get("targets_12_months", {})
        translation_summary.update(
            {
                "status": translation_payload.get("status"),
                "manuscript_count": len(manuscripts),
                "patent_disclosure_count": len(patent_disclosures),
                "fundable_project_count": len(fundable_projects),
                "tool_count": len(tools),
                "has_lead_tool": any(tool.get("lead") for tool in tools),
                "targets_met": (
                    len(manuscripts) >= int(target_counts.get("manuscripts_or_preprints", 0))
                    and len(patent_disclosures) >= int(target_counts.get("patent_disclosures", 0))
                    and len(fundable_projects) >= int(target_counts.get("fundable_project_packages", 0))
                    and len(tools) >= int(target_counts.get("monetizable_tools", 0))
                ),
            }
        )
        required_by_section = {
            "manuscripts": ["id", "title", "lanes", "evidence_now", "claim_gate", "next_artifact"],
            "patent_disclosures": ["id", "title", "lanes", "invention_summary", "evidence_now", "pre_filing_tasks"],
            "fundable_projects": ["id", "title", "lanes", "route", "first_customer", "mvp"],
        }
        for section_name, rows in [
            ("manuscripts", manuscripts),
            ("patent_disclosures", patent_disclosures),
            ("fundable_projects", fundable_projects),
        ]:
            for row in rows:
                required_fields = required_by_section[section_name]
                missing_fields = [field for field in required_fields if row.get(field) in (None, "", [])]
                if missing_fields:
                    errors.append(
                        f"translation pipeline {section_name} {row.get('id', '<unknown>')} missing fields: {missing_fields}"
                    )
        for tool in tools:
            missing_fields = [field for field in ["id", "name", "lanes", "mvp", "paying_user"] if tool.get(field) in (None, "", [])]
            if missing_fields:
                errors.append(f"translation pipeline tool {tool.get('id', '<unknown>')} missing fields: {missing_fields}")
        if not translation_summary["targets_met"]:
            errors.append("translation pipeline does not meet declared 12-month target counts")
        if not translation_summary["has_lead_tool"]:
            errors.append("translation pipeline must identify one lead monetizable tool")
        if translation_payload.get("status") != "deferred_until_b1_b10_technical_gates_pass":
            errors.append("translation pipeline must remain deferred until B1-B10 technical gates pass")

    b1_manifest = yaml.safe_load(read(b1_manifest_path))
    current_results = b1_manifest.get("current_results", {})
    routing_diagnostic_manifest = current_results.get("qiskit_line_routing_diagnostic_suite_v0")
    heavyhex_diagnostic_manifest = current_results.get("qiskit_heavyhex_d3_routing_diagnostic_suite_v0")
    heavyhex_e2e_manifest = current_results.get("b1_heavyhex_end_to_end_routed_benefit_v0")
    heavyhex_e2e_suite_manifest = current_results.get("b1_heavyhex_end_to_end_routed_benefit_suite_v0")
    post_routing_profile_manifest = current_results.get("b1_post_routing_bottleneck_profile_v0")
    swap_macro_manifest = current_results.get("b1_post_routing_swap_macro_compression_v0")
    virtual_swap_manifest = current_results.get("b1_virtual_swap_elimination_v0")
    post_virtual_swap_1q_manifest = current_results.get("b1_post_virtual_swap_1q_resynthesis_v0")
    native_t_resource_manifest = current_results.get("b1_native_t_resource_optimizer_v0")
    control_rz_commute_manifest = current_results.get("b1_control_rz_commute_optimizer_v0")
    u3_phase_factored_manifest = current_results.get("b1_u3_phase_factored_optimizer_v0")
    b1_b7_gcm_h6_target_selector_manifest = current_results.get("b1_b7_gcm_h6_target_selector_v0")
    b1_b7_gcm_h6_cone_feasibility_manifest = current_results.get(
        "b1_b7_gcm_h6_cone_feasibility_gate_v0"
    )
    b1_b7_cone01_phase_removal_manifest = current_results.get(
        "b1_b7_cone01_phase_removal_gate_v0"
    )
    b1_b7_cone01_euler_reabsorption_manifest = current_results.get(
        "b1_b7_cone01_euler_reabsorption_gate_v0"
    )
    b1_b7_cone01_parameter_transfer_manifest = current_results.get(
        "b1_b7_cone01_parameter_transfer_gate_v0"
    )
    b1_b7_cone01_theta_sharing_manifest = current_results.get(
        "b1_b7_cone01_theta_sharing_ledger_gate_v0"
    )
    b1_b7_cone01_shared_theta_synthesis_object_manifest = current_results.get(
        "b1_b7_cone01_shared_theta_synthesis_object_gate_v0"
    )
    b1_b7_cone01_shared_theta_replay_verifier_manifest = current_results.get(
        "b1_b7_cone01_shared_theta_replay_verifier_gate_v0"
    )
    b1_b7_cone01_shared_theta_layout_routing_manifest = current_results.get(
        "b1_b7_cone01_shared_theta_layout_routing_gate_v0"
    )
    b1_b7_cone01_shared_theta_factory_amortization_manifest = current_results.get(
        "b1_b7_cone01_shared_theta_factory_amortization_gate_v0"
    )
    b1_b7_cone01_shared_theta_error_budget_manifest = current_results.get(
        "b1_b7_cone01_shared_theta_error_budget_gate_v0"
    )
    b1_b7_cone01_theta_sharing_cost_model_manifest = current_results.get(
        "b1_b7_cone01_theta_sharing_cost_model_gate_v0"
    )
    synthetic_noise_manifest = current_results.get("b1_synthetic_heavyhex_noise_proxy_v0")
    b1_routing_diagnostic = {
        "path": str(b1_routing_diagnostic_path),
        "exists": b1_routing_diagnostic_path.exists(),
    }
    if not routing_diagnostic_manifest:
        errors.append("B1 manifest missing current result: qiskit_line_routing_diagnostic_suite_v0")
    else:
        if routing_diagnostic_manifest.get("status") != "diagnostic_only_not_validated_baseline":
            errors.append("B1 line-routing diagnostic must remain marked diagnostic_only_not_validated_baseline")
        for field in ["diagnostic", "suite_summary"]:
            value = routing_diagnostic_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 line-routing diagnostic missing existing {field} path: {value}")
        for level, value in routing_diagnostic_manifest.get("aer_crosschecks", {}).items():
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 line-routing diagnostic missing existing Aer cross-check path for {level}: {value}")
    if b1_routing_diagnostic_path.exists():
        routing_payload = json.loads(read(b1_routing_diagnostic_path))
        b1_routing_diagnostic.update(
            {
                "status": routing_payload.get("report_status"),
                "full_exact_valid_baseline": routing_payload.get("full_exact_valid_baseline"),
                "full_measurement_distribution_valid_baseline": routing_payload.get(
                    "full_measurement_distribution_valid_baseline"
                ),
                "partial_measurement_distribution_levels": routing_payload.get(
                    "measurement_distribution_partial_valid_levels"
                ),
                "common_measurement_distribution_failures": routing_payload.get(
                    "common_measurement_distribution_failures"
                ),
                "best_diagnostic_exposure_reduction_pct": routing_payload.get(
                    "best_diagnostic_exposure_reduction_pct"
                ),
                "aer_crosscheck_all_passed": routing_payload.get("aer_crosscheck", {}).get("all_passed"),
                "aer_crosscheck_total_pairs": routing_payload.get("aer_crosscheck", {}).get("total_pairs"),
                "aer_crosscheck_max_tvd": routing_payload.get("aer_crosscheck", {}).get(
                    "max_total_variation_distance"
                ),
            }
        )
        if routing_payload.get("report_status") != "diagnostic_only_not_validated_baseline":
            errors.append("B1 routing diagnostic report must remain diagnostic-only")
        if routing_payload.get("line_routing_is_calibrated_heavy_hex") is not False:
            errors.append("B1 routing diagnostic must not claim calibrated heavy-hex status")
        if routing_payload.get("aer_crosscheck", {}).get("all_passed") is not True:
            errors.append("B1 routing diagnostic Aer cross-check must be present and passing")
    else:
        errors.append(f"missing B1 routing diagnostic report: {b1_routing_diagnostic_path}")

    b1_heavyhex_diagnostic = {
        "path": str(b1_heavyhex_diagnostic_path),
        "exists": b1_heavyhex_diagnostic_path.exists(),
    }
    if not heavyhex_diagnostic_manifest:
        errors.append("B1 manifest missing current result: qiskit_heavyhex_d3_routing_diagnostic_suite_v0")
    else:
        if heavyhex_diagnostic_manifest.get("status") != "device_like_topology_diagnostic_not_calibrated_noise_baseline":
            errors.append("B1 heavy-hex diagnostic must remain marked as not a calibrated noise baseline")
        for field in ["diagnostic", "suite_summary"]:
            value = heavyhex_diagnostic_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 heavy-hex diagnostic missing existing {field} path: {value}")
        for level, value in heavyhex_diagnostic_manifest.get("aer_crosschecks", {}).items():
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 heavy-hex diagnostic missing existing Aer cross-check path for {level}: {value}")
    if b1_heavyhex_diagnostic_path.exists():
        heavyhex_payload = json.loads(read(b1_heavyhex_diagnostic_path))
        b1_heavyhex_diagnostic.update(
            {
                "status": heavyhex_payload.get("report_status"),
                "distance": heavyhex_payload.get("distance"),
                "physical_qubits": heavyhex_payload.get("physical_qubits"),
                "aer_crosscheck_all_passed": heavyhex_payload.get("aer_crosscheck_all_passed"),
                "aer_crosscheck_valid_levels": heavyhex_payload.get("aer_crosscheck_valid_levels"),
                "best_diagnostic_exposure_reduction_pct": heavyhex_payload.get(
                    "best_diagnostic_exposure_reduction_pct"
                ),
            }
        )
        if heavyhex_payload.get("report_status") != "device_like_topology_diagnostic_not_calibrated_noise_baseline":
            errors.append("B1 heavy-hex diagnostic report must remain topology diagnostic only")
        if heavyhex_payload.get("calibrated_noise_model") is not False:
            errors.append("B1 heavy-hex diagnostic must not claim a calibrated noise model")
        if heavyhex_payload.get("aer_crosscheck_all_passed") is not True:
            errors.append("B1 heavy-hex diagnostic Aer cross-check must be present and passing")
    else:
        errors.append(f"missing B1 heavy-hex diagnostic report: {b1_heavyhex_diagnostic_path}")

    b1_heavyhex_e2e = {
        "path": str(b1_heavyhex_e2e_path),
        "exists": b1_heavyhex_e2e_path.exists(),
    }
    if not heavyhex_e2e_manifest:
        errors.append("B1 manifest missing current result: b1_heavyhex_end_to_end_routed_benefit_v0")
    else:
        if heavyhex_e2e_manifest.get("status") != "topology_routed_benefit_diagnostic_not_calibrated_noise_claim":
            errors.append("B1 heavy-hex end-to-end result must remain marked as topology diagnostic")
        for field in ["report", "summary", "aer_crosscheck"]:
            value = heavyhex_e2e_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 heavy-hex end-to-end missing existing {field} path: {value}")
    if b1_heavyhex_e2e_path.exists():
        e2e_payload = json.loads(read(b1_heavyhex_e2e_path))
        b1_heavyhex_e2e.update(
            {
                "status": e2e_payload.get("report_status"),
                "aer_crosscheck_passed": e2e_payload.get("aer_crosscheck_passed"),
                "aer_crosscheck_failed": e2e_payload.get("aer_crosscheck_failed"),
                "operation_count_reduction_pct": e2e_payload.get("operation_count_reduction_pct"),
                "two_qubit_gate_count_reduction_pct": e2e_payload.get("two_qubit_gate_count_reduction_pct"),
                "logical_depth_reduction_pct": e2e_payload.get("logical_depth_reduction_pct"),
                "hardware_weighted_exposure_reduction_pct": e2e_payload.get(
                    "hardware_weighted_exposure_reduction_pct"
                ),
            }
        )
        if e2e_payload.get("report_status") != "topology_routed_benefit_diagnostic_not_calibrated_noise_claim":
            errors.append("B1 heavy-hex end-to-end report must remain diagnostic-only")
        if e2e_payload.get("aer_crosscheck_failed") != 0:
            errors.append("B1 heavy-hex end-to-end Aer cross-check must have zero failures")
    else:
        errors.append(f"missing B1 heavy-hex end-to-end report: {b1_heavyhex_e2e_path}")

    b1_heavyhex_e2e_suite = {
        "path": str(b1_heavyhex_e2e_suite_path),
        "exists": b1_heavyhex_e2e_suite_path.exists(),
    }
    if not heavyhex_e2e_suite_manifest:
        errors.append("B1 manifest missing current result: b1_heavyhex_end_to_end_routed_benefit_suite_v0")
    else:
        if heavyhex_e2e_suite_manifest.get("status") != "topology_routed_benefit_suite_not_calibrated_noise_claim":
            errors.append("B1 heavy-hex end-to-end suite must remain marked as topology diagnostic")
        for field in ["report", "level0_summary", "level1_summary"]:
            value = heavyhex_e2e_suite_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 heavy-hex end-to-end suite missing existing {field} path: {value}")
    if b1_heavyhex_e2e_suite_path.exists():
        suite_payload = json.loads(read(b1_heavyhex_e2e_suite_path))
        b1_heavyhex_e2e_suite.update(
            {
                "status": suite_payload.get("report_status"),
                "levels_tested": suite_payload.get("levels_tested"),
                "all_aer_crosschecks_passed": suite_payload.get("all_aer_crosschecks_passed"),
                "best_level_by_exposure": suite_payload.get("best_level_by_exposure"),
                "best_exposure_reduction_pct": suite_payload.get("best_exposure_reduction_pct"),
            }
        )
        if suite_payload.get("report_status") != "topology_routed_benefit_suite_not_calibrated_noise_claim":
            errors.append("B1 heavy-hex end-to-end suite report must remain diagnostic-only")
        if suite_payload.get("all_aer_crosschecks_passed") is not True:
            errors.append("B1 heavy-hex end-to-end suite Aer cross-checks must all pass")
    else:
        errors.append(f"missing B1 heavy-hex end-to-end suite report: {b1_heavyhex_e2e_suite_path}")

    b1_post_routing_profile = {
        "path": str(b1_post_routing_profile_path),
        "exists": b1_post_routing_profile_path.exists(),
    }
    if not post_routing_profile_manifest:
        errors.append("B1 manifest missing current result: b1_post_routing_bottleneck_profile_v0")
    else:
        if (
            post_routing_profile_manifest.get("status")
            != "post_routing_bottleneck_profile_diagnostic_not_calibrated_noise_claim"
        ):
            errors.append("B1 post-routing bottleneck profile must remain marked as diagnostic")
        for field in ["report", "level0_source_metrics", "level0_optimized_metrics", "level1_source_metrics", "level1_optimized_metrics"]:
            value = post_routing_profile_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 post-routing bottleneck profile missing existing {field} path: {value}")
    if b1_post_routing_profile_path.exists():
        profile_payload = json.loads(read(b1_post_routing_profile_path))
        b1_post_routing_profile.update(
            {
                "status": profile_payload.get("report_status"),
                "levels_tested": profile_payload.get("levels_tested"),
                "all_aer_crosschecks_passed": profile_payload.get("all_aer_crosschecks_passed"),
                "level0_exposure_reduction_pct": profile_payload.get("level_summary", {})
                .get("0", {})
                .get("hardware_weighted_exposure_reduction_pct"),
                "level1_exposure_reduction_pct": profile_payload.get("level_summary", {})
                .get("1", {})
                .get("hardware_weighted_exposure_reduction_pct"),
                "erased_circuit_count": profile_payload.get("bottlenecks", {}).get("erased_circuit_count"),
                "top_level1_two_qubit_bottleneck": (
                    profile_payload.get("bottlenecks", {})
                    .get("level1_two_qubit_bottlenecks", [{}])[0]
                    .get("circuit")
                ),
            }
        )
        if (
            profile_payload.get("report_status")
            != "post_routing_bottleneck_profile_diagnostic_not_calibrated_noise_claim"
        ):
            errors.append("B1 post-routing bottleneck profile report must remain diagnostic-only")
        if profile_payload.get("all_aer_crosschecks_passed") is not True:
            errors.append("B1 post-routing bottleneck profile must inherit passing Aer cross-checks")
        if int(profile_payload.get("bottlenecks", {}).get("erased_circuit_count", 0)) < 1:
            errors.append("B1 post-routing bottleneck profile should record level-1 benefit erasure")
    else:
        errors.append(f"missing B1 post-routing bottleneck profile: {b1_post_routing_profile_path}")

    b1_swap_macro = {
        "path": str(b1_swap_macro_path),
        "exists": b1_swap_macro_path.exists(),
    }
    if not swap_macro_manifest:
        errors.append("B1 manifest missing current result: b1_post_routing_swap_macro_compression_v0")
    else:
        if swap_macro_manifest.get("status") != "post_routing_swap_macro_diagnostic_not_native_basis_claim":
            errors.append("B1 SWAP macro result must remain marked as diagnostic, not native-basis claim")
        for field in ["report", "proof_log", "before_metrics", "after_metrics", "local_aer_crosscheck", "end_to_end_aer_crosscheck"]:
            value = swap_macro_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 SWAP macro result missing existing {field} path: {value}")
    if b1_swap_macro_path.exists():
        swap_payload = json.loads(read(b1_swap_macro_path))
        b1_swap_macro.update(
            {
                "status": swap_payload.get("report_status"),
                "swap_macros": swap_payload.get("swap_macros"),
                "removed_cx_gates": swap_payload.get("removed_cx_gates"),
                "two_qubit_reduction_pct": swap_payload.get("metrics", {})
                .get("two_qubit_gate_count", {})
                .get("reduction_pct"),
                "exposure_reduction_pct": swap_payload.get("metrics", {})
                .get("hardware_weighted_error_exposure", {})
                .get("reduction_pct"),
                "local_aer_failed": swap_payload.get("local_aer_crosscheck", {}).get("failed"),
                "end_to_end_aer_failed": swap_payload.get("end_to_end_aer_crosscheck", {}).get("failed"),
                "top_swap_macro_circuit": swap_payload.get("top_circuits_by_swap_macros", [{}])[0].get(
                    "relative_path"
                ),
            }
        )
        if swap_payload.get("report_status") != "post_routing_swap_macro_diagnostic_not_native_basis_claim":
            errors.append("B1 SWAP macro report must remain diagnostic-only")
        if int(swap_payload.get("swap_macros", 0)) < 1:
            errors.append("B1 SWAP macro report should identify at least one routed SWAP macro")
        if swap_payload.get("local_aer_crosscheck", {}).get("failed") != 0:
            errors.append("B1 SWAP macro local Aer cross-check must have zero failures")
        if swap_payload.get("end_to_end_aer_crosscheck", {}).get("failed") != 0:
            errors.append("B1 SWAP macro end-to-end Aer cross-check must have zero failures")
    else:
        errors.append(f"missing B1 SWAP macro report: {b1_swap_macro_path}")

    b1_virtual_swap = {
        "path": str(b1_virtual_swap_path),
        "exists": b1_virtual_swap_path.exists(),
    }
    if not virtual_swap_manifest:
        errors.append("B1 manifest missing current result: b1_virtual_swap_elimination_v0")
    else:
        if virtual_swap_manifest.get("status") != "virtual_swap_elimination_diagnostic_not_layout_final_claim":
            errors.append("B1 virtual SWAP result must remain diagnostic, not final layout claim")
        for field in [
            "report",
            "proof_replay_report",
            "proof_log",
            "before_metrics",
            "after_metrics",
            "local_aer_crosscheck",
            "end_to_end_aer_crosscheck",
        ]:
            value = virtual_swap_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 virtual SWAP result missing existing {field} path: {value}")
    if b1_virtual_swap_path.exists():
        virtual_payload = json.loads(read(b1_virtual_swap_path))
        b1_virtual_swap.update(
            {
                "status": virtual_payload.get("report_status"),
                "rewritten_circuits": virtual_payload.get("rewritten_circuits"),
                "skipped_circuits": virtual_payload.get("skipped_circuits"),
                "virtual_swaps_removed": virtual_payload.get("virtual_swaps_removed"),
                "removed_cx_gates": virtual_payload.get("removed_cx_gates"),
                "two_qubit_reduction_pct": virtual_payload.get("metrics", {})
                .get("two_qubit_gate_count", {})
                .get("reduction_pct"),
                "exposure_reduction_pct": virtual_payload.get("metrics", {})
                .get("hardware_weighted_error_exposure", {})
                .get("reduction_pct"),
                "local_aer_failed": virtual_payload.get("local_aer_crosscheck", {}).get("failed"),
                "end_to_end_aer_failed": virtual_payload.get("end_to_end_aer_crosscheck", {}).get("failed"),
                "top_virtual_swap_circuit": virtual_payload.get("top_circuits_by_virtual_swaps", [{}])[0].get(
                    "relative_path"
                ),
            }
        )
        if virtual_payload.get("report_status") != "virtual_swap_elimination_diagnostic_not_layout_final_claim":
            errors.append("B1 virtual SWAP report must remain diagnostic-only")
        if int(virtual_payload.get("virtual_swaps_removed", 0)) < 1:
            errors.append("B1 virtual SWAP report should remove at least one routed SWAP")
        if virtual_payload.get("local_aer_crosscheck", {}).get("failed") != 0:
            errors.append("B1 virtual SWAP local Aer cross-check must have zero failures")
        if virtual_payload.get("end_to_end_aer_crosscheck", {}).get("failed") != 0:
            errors.append("B1 virtual SWAP end-to-end Aer cross-check must have zero failures")
    else:
        errors.append(f"missing B1 virtual SWAP report: {b1_virtual_swap_path}")

    if b1_virtual_swap_replay_path.exists():
        replay_payload = json.loads(read(b1_virtual_swap_replay_path))
        b1_virtual_swap.update(
            {
                "proof_replay_status": replay_payload.get("report_status"),
                "proof_replay_events": replay_payload.get("proof_events"),
                "proof_replayed_events": replay_payload.get("replayed_events"),
                "proof_replay_output_mismatches": replay_payload.get("output_mismatches"),
                "proof_replay_error_count": replay_payload.get("error_count"),
            }
        )
        if replay_payload.get("report_status") != "passed":
            errors.append("B1 virtual SWAP proof replay must pass")
        if replay_payload.get("proof_events") != replay_payload.get("replayed_events"):
            errors.append("B1 virtual SWAP proof replay must consume every proof event")
        if replay_payload.get("output_mismatches") != 0:
            errors.append("B1 virtual SWAP proof replay must have zero output mismatches")
        if replay_payload.get("error_count") != 0:
            errors.append("B1 virtual SWAP proof replay must have zero errors")
    else:
        errors.append(f"missing B1 virtual SWAP proof replay report: {b1_virtual_swap_replay_path}")

    b1_post_virtual_swap_1q = {
        "path": str(b1_post_virtual_swap_1q_path),
        "exists": b1_post_virtual_swap_1q_path.exists(),
    }
    if not post_virtual_swap_1q_manifest:
        errors.append("B1 manifest missing current result: b1_post_virtual_swap_1q_resynthesis_v0")
    else:
        if post_virtual_swap_1q_manifest.get("status") != "post_virtual_swap_1q_resynthesis_t_resource_positive_diagnostic":
            errors.append("B1 post-virtual-SWAP 1Q result must remain marked as a positive diagnostic")
        for field in ["report", "markdown_report", "proof_log", "before_metrics", "after_metrics", "aer_crosscheck"]:
            value = post_virtual_swap_1q_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 post-virtual-SWAP 1Q result missing existing {field} path: {value}")
    if b1_post_virtual_swap_1q_path.exists():
        post_1q_payload = json.loads(read(b1_post_virtual_swap_1q_path))
        b1_post_virtual_swap_1q.update(
            {
                "status": post_1q_payload.get("status"),
                "rewritten_circuits": post_1q_payload.get("rewrite_stats", {}).get("rewritten_circuits"),
                "resynthesized_runs": post_1q_payload.get("rewrite_stats", {}).get("resynthesized_runs"),
                "removed_single_qubit_gates": post_1q_payload.get("rewrite_stats", {}).get("removed_single_qubit_gates"),
                "certificate_entries": post_1q_payload.get("rewrite_stats", {}).get("certificate_entries"),
                "logical_t_count_reduction": post_1q_payload.get("t_resource_proxy", {}).get(
                    "logical_t_count_reduction"
                ),
                "logical_t_depth_reduction": post_1q_payload.get("t_resource_proxy", {}).get(
                    "logical_t_depth_reduction"
                ),
                "non_clifford_rotation_count_reduction": post_1q_payload.get("t_resource_proxy", {}).get(
                    "non_clifford_rotation_count_reduction"
                ),
                "aer_failed": post_1q_payload.get("aer_crosscheck", {}).get("failed"),
                "aer_pair_count": post_1q_payload.get("aer_crosscheck", {}).get("pair_count"),
                "aer_max_tvd": post_1q_payload.get("aer_crosscheck", {}).get("max_total_variation_distance"),
            }
        )
        if post_1q_payload.get("benchmark_id") != "B1":
            errors.append("B1 post-virtual-SWAP 1Q report must have benchmark_id B1")
        if post_1q_payload.get("status") != "post_virtual_swap_1q_resynthesis_t_resource_positive_diagnostic":
            errors.append("B1 post-virtual-SWAP 1Q report status mismatch")
        if post_1q_payload.get("rewrite_stats", {}).get("rewritten_circuits") != 30:
            errors.append("B1 post-virtual-SWAP 1Q report should rewrite all 30 circuits")
        if int(post_1q_payload.get("rewrite_stats", {}).get("resynthesized_runs", 0)) < 1:
            errors.append("B1 post-virtual-SWAP 1Q report should resynthesize at least one run")
        if post_1q_payload.get("aer_crosscheck", {}).get("failed") != 0:
            errors.append("B1 post-virtual-SWAP 1Q Aer cross-check must have zero failures")
        if float(post_1q_payload.get("t_resource_proxy", {}).get("logical_t_count_reduction", 0.0)) <= 1.0:
            errors.append("B1 post-virtual-SWAP 1Q report should show a positive logical T-count proxy reduction")
    else:
        errors.append(f"missing B1 post-virtual-SWAP 1Q report: {b1_post_virtual_swap_1q_path}")

    b1_native_t_resource = {
        "path": str(b1_native_t_resource_path),
        "exists": b1_native_t_resource_path.exists(),
    }
    if not native_t_resource_manifest:
        errors.append("B1 manifest missing current result: b1_native_t_resource_optimizer_v0")
    else:
        if native_t_resource_manifest.get("status") != "native_t_resource_optimizer_positive_diagnostic_not_final_claim":
            errors.append("B1 native T-resource optimizer must remain marked as a positive diagnostic, not final claim")
        for field in ["report", "markdown_report", "proof_log", "before_metrics", "after_metrics", "aer_crosscheck"]:
            value = native_t_resource_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 native T-resource optimizer missing existing {field} path: {value}")
    if b1_native_t_resource_path.exists():
        native_payload = json.loads(read(b1_native_t_resource_path))
        b1_native_t_resource.update(
            {
                "status": native_payload.get("status"),
                "rewritten_circuits": native_payload.get("rewrite_stats", {}).get("rewritten_circuits"),
                "circuits_changed": native_payload.get("rewrite_stats", {}).get("circuits_changed"),
                "canonicalization_events": native_payload.get("rewrite_stats", {}).get("canonicalization_events"),
                "identity_events": native_payload.get("rewrite_stats", {}).get("identity_events"),
                "rz_rewrite_events": native_payload.get("rewrite_stats", {}).get("rz_rewrite_events"),
                "removed_single_qubit_gates": native_payload.get("rewrite_stats", {}).get("removed_single_qubit_gates"),
                "certificate_entries": native_payload.get("rewrite_stats", {}).get("certificate_entries"),
                "logical_t_count_reduction": native_payload.get("t_resource_proxy", {}).get("logical_t_count_reduction"),
                "logical_t_depth_reduction": native_payload.get("t_resource_proxy", {}).get("logical_t_depth_reduction"),
                "non_clifford_rotation_count_reduction": native_payload.get("t_resource_proxy", {}).get(
                    "non_clifford_rotation_count_reduction"
                ),
                "aer_failed": native_payload.get("aer_crosscheck", {}).get("failed"),
                "aer_pair_count": native_payload.get("aer_crosscheck", {}).get("pair_count"),
                "aer_max_tvd": native_payload.get("aer_crosscheck", {}).get("max_total_variation_distance"),
            }
        )
        if native_payload.get("benchmark_id") != "B1":
            errors.append("B1 native T-resource optimizer report must have benchmark_id B1")
        if native_payload.get("status") != "native_t_resource_optimizer_positive_diagnostic_not_final_claim":
            errors.append("B1 native T-resource optimizer report status mismatch")
        if native_payload.get("rewrite_stats", {}).get("rewritten_circuits") != 30:
            errors.append("B1 native T-resource optimizer should rewrite all 30 circuits")
        if int(native_payload.get("rewrite_stats", {}).get("canonicalization_events", 0)) < 1:
            errors.append("B1 native T-resource optimizer should emit at least one canonicalization event")
        if native_payload.get("aer_crosscheck", {}).get("failed") != 0:
            errors.append("B1 native T-resource optimizer Aer cross-check must have zero failures")
        if float(native_payload.get("t_resource_proxy", {}).get("logical_t_count_reduction", 0.0)) <= 1.0:
            errors.append("B1 native T-resource optimizer should show a positive logical T-count proxy reduction")
    else:
        errors.append(f"missing B1 native T-resource optimizer report: {b1_native_t_resource_path}")

    b1_control_rz_commute = {
        "path": str(b1_control_rz_commute_path),
        "exists": b1_control_rz_commute_path.exists(),
    }
    if not control_rz_commute_manifest:
        errors.append("B1 manifest missing current result: b1_control_rz_commute_optimizer_v0")
    else:
        if control_rz_commute_manifest.get("status") != "control_rz_commute_positive_diagnostic_not_final_claim":
            errors.append("B1 control-RZ commute optimizer must remain marked as a positive diagnostic, not final claim")
        for field in ["report", "markdown_report", "proof_log", "before_metrics", "after_metrics", "aer_crosscheck"]:
            value = control_rz_commute_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 control-RZ commute optimizer missing existing {field} path: {value}")
    if b1_control_rz_commute_path.exists():
        control_payload = json.loads(read(b1_control_rz_commute_path))
        b1_control_rz_commute.update(
            {
                "status": control_payload.get("status"),
                "rewritten_circuits": control_payload.get("rewrite_stats", {}).get("rewritten_circuits"),
                "circuits_changed": control_payload.get("rewrite_stats", {}).get("circuits_changed"),
                "absorbed_rz_gates": control_payload.get("rewrite_stats", {}).get("absorbed_rz_gates"),
                "certificate_entries": control_payload.get("rewrite_stats", {}).get("certificate_entries"),
                "merged_or_moved_groups": control_payload.get("rewrite_stats", {}).get("merged_or_moved_groups"),
                "removed_rz_gates": control_payload.get("rewrite_stats", {}).get("removed_rz_gates"),
                "commuted_cx_count": control_payload.get("rewrite_stats", {}).get("commuted_cx_count"),
                "logical_t_count_reduction": control_payload.get("t_resource_proxy", {}).get("logical_t_count_reduction"),
                "logical_t_depth_reduction": control_payload.get("t_resource_proxy", {}).get("logical_t_depth_reduction"),
                "non_clifford_rotation_count_reduction": control_payload.get("t_resource_proxy", {}).get(
                    "non_clifford_rotation_count_reduction"
                ),
                "aer_failed": control_payload.get("aer_crosscheck", {}).get("failed"),
                "aer_pair_count": control_payload.get("aer_crosscheck", {}).get("pair_count"),
                "aer_max_tvd": control_payload.get("aer_crosscheck", {}).get("max_total_variation_distance"),
            }
        )
        if control_payload.get("benchmark_id") != "B1":
            errors.append("B1 control-RZ commute optimizer report must have benchmark_id B1")
        if control_payload.get("status") != "control_rz_commute_positive_diagnostic_not_final_claim":
            errors.append("B1 control-RZ commute optimizer report status mismatch")
        if control_payload.get("rewrite_stats", {}).get("rewritten_circuits") != 30:
            errors.append("B1 control-RZ commute optimizer should rewrite all 30 circuits")
        if int(control_payload.get("rewrite_stats", {}).get("removed_rz_gates", 0)) < 1:
            errors.append("B1 control-RZ commute optimizer should remove at least one RZ gate")
        if int(control_payload.get("rewrite_stats", {}).get("commuted_cx_count", 0)) < 1:
            errors.append("B1 control-RZ commute optimizer should commute at least one RZ across CNOT controls")
        if control_payload.get("aer_crosscheck", {}).get("failed") != 0:
            errors.append("B1 control-RZ commute optimizer Aer cross-check must have zero failures")
        if float(control_payload.get("t_resource_proxy", {}).get("logical_t_count_reduction", 0.0)) <= 1.0:
            errors.append("B1 control-RZ commute optimizer should show a positive logical T-count proxy reduction")
    else:
        errors.append(f"missing B1 control-RZ commute optimizer report: {b1_control_rz_commute_path}")

    b1_u3_phase_factored = {
        "path": str(b1_u3_phase_factored_path),
        "exists": b1_u3_phase_factored_path.exists(),
    }
    if not u3_phase_factored_manifest:
        errors.append("B1 manifest missing current result: b1_u3_phase_factored_optimizer_v0")
    else:
        if u3_phase_factored_manifest.get("status") != "u3_phase_factored_positive_diagnostic_not_final_claim":
            errors.append("B1 U3 phase-factored optimizer must remain marked as a positive diagnostic, not final claim")
        for field in ["report", "markdown_report", "proof_log", "before_metrics", "after_metrics", "aer_crosscheck"]:
            value = u3_phase_factored_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 U3 phase-factored optimizer missing existing {field} path: {value}")
    if b1_u3_phase_factored_path.exists():
        u3_payload = json.loads(read(b1_u3_phase_factored_path))
        b1_u3_phase_factored.update(
            {
                "status": u3_payload.get("status"),
                "rewritten_circuits": u3_payload.get("factorization_stats", {}).get("rewritten_circuits"),
                "circuits_changed": u3_payload.get("factorization_stats", {}).get("circuits_changed"),
                "u3_factorization_events": u3_payload.get("factorization_stats", {}).get("u3_factorization_events"),
                "rz_components_emitted": u3_payload.get("factorization_stats", {}).get("rz_components_emitted"),
                "ry_components_emitted": u3_payload.get("factorization_stats", {}).get("ry_components_emitted"),
                "zero_components_removed": u3_payload.get("factorization_stats", {}).get("zero_components_removed"),
                "factorization_certificate_entries": u3_payload.get("factorization_stats", {}).get("certificate_entries"),
                "rz_commute_certificate_entries": u3_payload.get("commute_stats", {}).get("certificate_entries"),
                "removed_rz_gates": u3_payload.get("commute_stats", {}).get("removed_rz_gates"),
                "commuted_cx_count": u3_payload.get("commute_stats", {}).get("commuted_cx_count"),
                "logical_t_count_reduction": u3_payload.get("t_resource_proxy", {}).get("logical_t_count_reduction"),
                "logical_t_depth_reduction": u3_payload.get("t_resource_proxy", {}).get("logical_t_depth_reduction"),
                "non_clifford_rotation_count_reduction": u3_payload.get("t_resource_proxy", {}).get(
                    "non_clifford_rotation_count_reduction"
                ),
                "aer_failed": u3_payload.get("aer_crosscheck", {}).get("failed"),
                "aer_pair_count": u3_payload.get("aer_crosscheck", {}).get("pair_count"),
                "aer_max_tvd": u3_payload.get("aer_crosscheck", {}).get("max_total_variation_distance"),
            }
        )
        if u3_payload.get("benchmark_id") != "B1":
            errors.append("B1 U3 phase-factored optimizer report must have benchmark_id B1")
        if u3_payload.get("status") != "u3_phase_factored_positive_diagnostic_not_final_claim":
            errors.append("B1 U3 phase-factored optimizer report status mismatch")
        if u3_payload.get("factorization_stats", {}).get("rewritten_circuits") != 30:
            errors.append("B1 U3 phase-factored optimizer should rewrite all 30 circuits")
        if int(u3_payload.get("factorization_stats", {}).get("u3_factorization_events", 0)) < 1:
            errors.append("B1 U3 phase-factored optimizer should factor at least one U3 gate")
        if int(u3_payload.get("commute_stats", {}).get("removed_rz_gates", 0)) < 1:
            errors.append("B1 U3 phase-factored optimizer should remove at least one RZ gate after factoring")
        if u3_payload.get("aer_crosscheck", {}).get("failed") != 0:
            errors.append("B1 U3 phase-factored optimizer Aer cross-check must have zero failures")
        if float(u3_payload.get("t_resource_proxy", {}).get("logical_t_count_reduction", 0.0)) <= 1.0:
            errors.append("B1 U3 phase-factored optimizer should show a positive logical T-count proxy reduction")
    else:
        errors.append(f"missing B1 U3 phase-factored optimizer report: {b1_u3_phase_factored_path}")

    b1_b7_gcm_h6_target_selector = {
        "path": str(b1_b7_gcm_h6_target_selector_path),
        "exists": b1_b7_gcm_h6_target_selector_path.exists(),
    }
    if not b1_b7_gcm_h6_target_selector_manifest:
        errors.append("B1 manifest missing current result: b1_b7_gcm_h6_target_selector_v0")
    else:
        if b1_b7_gcm_h6_target_selector_manifest.get("status") != "gcm_h6_target_selector_not_rewrite_or_resource_claim":
            errors.append("B1/B7 gcm_h6 target selector must remain a non-rewrite target selector")
        for field in ["report", "markdown_report", "source_qasm", "source_b7_template_gate"]:
            value = b1_b7_gcm_h6_target_selector_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 gcm_h6 target selector missing existing {field} path: {value}")
    if b1_b7_gcm_h6_target_selector_path.exists():
        selector_payload = json.loads(read(b1_b7_gcm_h6_target_selector_path))
        selector_summary = selector_payload.get("summary", {})
        selector_claims = selector_payload.get("claim_boundary", {})
        b1_b7_gcm_h6_target_selector.update(
            {
                "status": selector_payload.get("status"),
                "model_status": selector_payload.get("model_status"),
                "method": selector_payload.get("method"),
                "workload": selector_payload.get("workload"),
                "arbitrary_rotation_count": selector_summary.get("arbitrary_rotation_count"),
                "raw_unique_numeric_parameter_count": selector_summary.get(
                    "raw_unique_numeric_parameter_count"
                ),
                "canonical_unique_numeric_parameter_count": selector_summary.get(
                    "canonical_unique_numeric_parameter_count"
                ),
                "target_removed_arbitrary_occurrences_for_gcm_h6_1_20": selector_summary.get(
                    "target_removed_arbitrary_occurrences_for_gcm_h6_1_20"
                ),
                "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": selector_summary.get(
                    "target_proxy_t_ledger_reduction_for_gcm_h6_1_20"
                ),
                "top_canonical_angle_occurrences": selector_summary.get("top_canonical_angle_occurrences"),
                "top_cone_occurrences": selector_summary.get("top_cone_occurrences"),
                "cone_classes_meeting_target_if_one_removed_per_occurrence": selector_summary.get(
                    "cone_classes_meeting_target_if_one_removed_per_occurrence"
                ),
                "canonical_angle_classes_meeting_target_if_one_removed_per_occurrence": selector_summary.get(
                    "canonical_angle_classes_meeting_target_if_one_removed_per_occurrence"
                ),
                "qubit_classes_meeting_target_if_one_removed_per_occurrence": selector_summary.get(
                    "qubit_classes_meeting_target_if_one_removed_per_occurrence"
                ),
                "rewrite_claimed": selector_claims.get("rewrite_claimed"),
                "resource_saving_claimed": selector_claims.get("resource_saving_claimed"),
                "semantic_certificate_claimed": selector_claims.get("semantic_certificate_claimed"),
                "validation_error_count": selector_summary.get("validation_error_count"),
            }
        )
        if selector_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 gcm_h6 target selector report must have benchmark_id B1")
        if selector_payload.get("method") != "b1_b7_gcm_h6_target_selector_v0":
            errors.append("B1/B7 gcm_h6 target selector method mismatch")
        if selector_payload.get("status") != "gcm_h6_target_selector_not_rewrite_or_resource_claim":
            errors.append("B1/B7 gcm_h6 target selector status mismatch")
        for field in [
            "arbitrary_rotation_count",
            "raw_unique_numeric_parameter_count",
            "canonical_unique_numeric_parameter_count",
            "target_removed_arbitrary_occurrences_for_gcm_h6_1_20",
            "target_proxy_t_ledger_reduction_for_gcm_h6_1_20",
            "top_canonical_angle_occurrences",
            "top_cone_occurrences",
            "cone_classes_meeting_target_if_one_removed_per_occurrence",
            "canonical_angle_classes_meeting_target_if_one_removed_per_occurrence",
            "qubit_classes_meeting_target_if_one_removed_per_occurrence",
        ]:
            if selector_summary.get(field) != b1_b7_gcm_h6_target_selector_manifest.get(field):
                errors.append(f"B1/B7 gcm_h6 target selector {field} mismatch")
        if selector_summary.get("arbitrary_rotation_count") != 270:
            errors.append("B1/B7 gcm_h6 target selector must count 270 arbitrary rotations")
        if selector_summary.get("target_removed_arbitrary_occurrences_for_gcm_h6_1_20") != 30:
            errors.append("B1/B7 gcm_h6 target selector target occurrence count must be 30")
        if selector_summary.get("target_proxy_t_ledger_reduction_for_gcm_h6_1_20") != 600:
            errors.append("B1/B7 gcm_h6 target selector target proxy-T reduction must be 600")
        if selector_summary.get("top_cone_occurrences", 0) < 30:
            errors.append("B1/B7 gcm_h6 target selector should expose at least one 30-occurrence cone")
        if selector_claims.get("rewrite_claimed") is not False:
            errors.append("B1/B7 gcm_h6 target selector must not claim a rewrite")
        if selector_claims.get("resource_saving_claimed") is not False:
            errors.append("B1/B7 gcm_h6 target selector must not claim resource savings")
        if selector_claims.get("semantic_certificate_claimed") is not False:
            errors.append("B1/B7 gcm_h6 target selector must not claim a semantic certificate")
        if selector_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 gcm_h6 target selector validation errors must remain zero")
    else:
        errors.append(f"missing B1/B7 gcm_h6 target selector report: {b1_b7_gcm_h6_target_selector_path}")

    b1_b7_gcm_h6_cone_feasibility = {
        "path": str(b1_b7_gcm_h6_cone_feasibility_path),
        "exists": b1_b7_gcm_h6_cone_feasibility_path.exists(),
    }
    if not b1_b7_gcm_h6_cone_feasibility_manifest:
        errors.append("B1 manifest missing current result: b1_b7_gcm_h6_cone_feasibility_gate_v0")
    else:
        if b1_b7_gcm_h6_cone_feasibility_manifest.get("status") != "cone_feasibility_gate_candidate_windows_not_rewrite":
            errors.append("B1/B7 gcm_h6 cone feasibility gate must remain a non-rewrite gate")
        for field in ["report", "markdown_report", "source_qasm"]:
            value = b1_b7_gcm_h6_cone_feasibility_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 gcm_h6 cone feasibility gate missing existing {field} path: {value}")
    if b1_b7_gcm_h6_cone_feasibility_path.exists():
        cone_payload = json.loads(read(b1_b7_gcm_h6_cone_feasibility_path))
        cone_summary = cone_payload.get("summary", {})
        cone_claims = cone_payload.get("claim_boundary", {})
        b1_b7_gcm_h6_cone_feasibility.update(
            {
                "status": cone_payload.get("status"),
                "model_status": cone_payload.get("model_status"),
                "method": cone_payload.get("method"),
                "workload": cone_payload.get("workload"),
                "target_removed_arbitrary_occurrences_for_gcm_h6_1_20": cone_summary.get(
                    "target_removed_arbitrary_occurrences_for_gcm_h6_1_20"
                ),
                "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": cone_summary.get(
                    "target_proxy_t_ledger_reduction_for_gcm_h6_1_20"
                ),
                "target_cone_class_count": cone_summary.get("target_cone_class_count"),
                "target_cone_total_occurrences": cone_summary.get("target_cone_total_occurrences"),
                "strict_direct_sandwich_total": cone_summary.get("strict_direct_sandwich_total"),
                "pair_local_window_total": cone_summary.get("pair_local_window_total"),
                "pair_local_single_arbitrary_window_total": cone_summary.get(
                    "pair_local_single_arbitrary_window_total"
                ),
                "cone_classes_meeting_target_by_pair_local_single_windows": cone_summary.get(
                    "cone_classes_meeting_target_by_pair_local_single_windows"
                ),
                "leading_feasible_cone_id": cone_summary.get("leading_feasible_cone_id"),
                "leading_feasible_pair_local_single_window_count": cone_summary.get(
                    "leading_feasible_pair_local_single_window_count"
                ),
                "leading_feasible_direct_sandwich_count": cone_summary.get(
                    "leading_feasible_direct_sandwich_count"
                ),
                "rewrite_claimed": cone_claims.get("rewrite_claimed"),
                "resource_saving_claimed": cone_claims.get("resource_saving_claimed"),
                "semantic_certificate_claimed": cone_claims.get("semantic_certificate_claimed"),
                "validation_error_count": cone_summary.get("validation_error_count"),
            }
        )
        if cone_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 gcm_h6 cone feasibility gate report must have benchmark_id B1")
        if cone_payload.get("method") != "b1_b7_gcm_h6_cone_feasibility_gate_v0":
            errors.append("B1/B7 gcm_h6 cone feasibility gate method mismatch")
        if cone_payload.get("status") != "cone_feasibility_gate_candidate_windows_not_rewrite":
            errors.append("B1/B7 gcm_h6 cone feasibility gate status mismatch")
        for field in [
            "target_removed_arbitrary_occurrences_for_gcm_h6_1_20",
            "target_proxy_t_ledger_reduction_for_gcm_h6_1_20",
            "target_cone_class_count",
            "target_cone_total_occurrences",
            "strict_direct_sandwich_total",
            "pair_local_window_total",
            "pair_local_single_arbitrary_window_total",
            "cone_classes_meeting_target_by_pair_local_single_windows",
            "leading_feasible_cone_id",
            "leading_feasible_pair_local_single_window_count",
            "leading_feasible_direct_sandwich_count",
        ]:
            if cone_summary.get(field) != b1_b7_gcm_h6_cone_feasibility_manifest.get(field):
                errors.append(f"B1/B7 gcm_h6 cone feasibility gate {field} mismatch")
        if cone_summary.get("leading_feasible_cone_id") != "cone_01":
            errors.append("B1/B7 gcm_h6 cone feasibility gate leading cone must remain cone_01")
        if cone_summary.get("leading_feasible_pair_local_single_window_count") != 35:
            errors.append("B1/B7 gcm_h6 cone feasibility gate cone_01 single-window count must remain 35")
        if cone_summary.get("cone_classes_meeting_target_by_pair_local_single_windows") != 1:
            errors.append("B1/B7 gcm_h6 cone feasibility gate should have exactly one cone meeting target")
        if cone_summary.get("strict_direct_sandwich_total") != 4:
            errors.append("B1/B7 gcm_h6 cone feasibility gate direct-sandwich total must remain 4")
        if cone_claims.get("rewrite_claimed") is not False:
            errors.append("B1/B7 gcm_h6 cone feasibility gate must not claim a rewrite")
        if cone_claims.get("resource_saving_claimed") is not False:
            errors.append("B1/B7 gcm_h6 cone feasibility gate must not claim resource savings")
        if cone_claims.get("semantic_certificate_claimed") is not False:
            errors.append("B1/B7 gcm_h6 cone feasibility gate must not claim a semantic certificate")
        if cone_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 gcm_h6 cone feasibility gate validation errors must remain zero")
    else:
        errors.append(f"missing B1/B7 gcm_h6 cone feasibility gate report: {b1_b7_gcm_h6_cone_feasibility_path}")

    b1_b7_cone01_phase_removal = {
        "path": str(b1_b7_cone01_phase_removal_path),
        "exists": b1_b7_cone01_phase_removal_path.exists(),
    }
    if not b1_b7_cone01_phase_removal_manifest:
        errors.append("B1 manifest missing current result: b1_b7_cone01_phase_removal_gate_v0")
    else:
        if b1_b7_cone01_phase_removal_manifest.get("status") != "cone01_phase_removal_restricted_negative_gate":
            errors.append("B1/B7 cone_01 phase-removal gate must remain a restricted negative gate")
        for field in ["report", "markdown_report", "source_qasm"]:
            value = b1_b7_cone01_phase_removal_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 cone_01 phase-removal gate missing existing {field} path: {value}")
    if b1_b7_cone01_phase_removal_path.exists():
        phase_payload = json.loads(read(b1_b7_cone01_phase_removal_path))
        phase_summary = phase_payload.get("summary", {})
        phase_claims = phase_payload.get("claim_boundary", {})
        b1_b7_cone01_phase_removal.update(
            {
                "status": phase_payload.get("status"),
                "model_status": phase_payload.get("model_status"),
                "method": phase_payload.get("method"),
                "workload": phase_payload.get("workload"),
                "target_cone_id": phase_summary.get("target_cone_id"),
                "candidate_window_count": phase_summary.get("candidate_window_count"),
                "required_exact_windows_for_b7_target": phase_summary.get(
                    "required_exact_windows_for_b7_target"
                ),
                "remove_only_exact_pass_count": phase_summary.get("remove_only_exact_pass_count"),
                "fixed_phase_exact_pass_count": phase_summary.get("fixed_phase_exact_pass_count"),
                "continuous_rz_exact_pass_count": phase_summary.get("continuous_rz_exact_pass_count"),
                "best_continuous_rz_residual_norm": phase_summary.get(
                    "best_continuous_rz_residual_norm"
                ),
                "median_continuous_rz_residual_norm": phase_summary.get(
                    "median_continuous_rz_residual_norm"
                ),
                "best_fixed_phase_residual_norm": phase_summary.get("best_fixed_phase_residual_norm"),
                "restricted_gate_clears_b7_target": phase_summary.get("restricted_gate_clears_b7_target"),
                "rewrite_claimed": phase_claims.get("rewrite_claimed"),
                "resource_saving_claimed": phase_claims.get("resource_saving_claimed"),
                "semantic_certificate_claimed": phase_claims.get("semantic_certificate_claimed"),
                "obstruction_theorem_claimed": phase_claims.get("obstruction_theorem_claimed"),
                "validation_error_count": phase_summary.get("validation_error_count"),
            }
        )
        if phase_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 cone_01 phase-removal gate report must have benchmark_id B1")
        if phase_payload.get("method") != "b1_b7_cone01_phase_removal_gate_v0":
            errors.append("B1/B7 cone_01 phase-removal gate method mismatch")
        if phase_payload.get("status") != "cone01_phase_removal_restricted_negative_gate":
            errors.append("B1/B7 cone_01 phase-removal gate status mismatch")
        for field in [
            "target_cone_id",
            "candidate_window_count",
            "required_exact_windows_for_b7_target",
            "remove_only_exact_pass_count",
            "fixed_phase_exact_pass_count",
            "continuous_rz_exact_pass_count",
            "best_continuous_rz_residual_norm",
            "median_continuous_rz_residual_norm",
            "best_fixed_phase_residual_norm",
            "restricted_gate_clears_b7_target",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "obstruction_theorem_claimed",
        ]:
            if phase_summary.get(field) != b1_b7_cone01_phase_removal_manifest.get(field):
                errors.append(f"B1/B7 cone_01 phase-removal gate {field} mismatch")
        if phase_summary.get("target_cone_id") != "cone_01":
            errors.append("B1/B7 cone_01 phase-removal gate target cone must remain cone_01")
        if phase_summary.get("candidate_window_count") != 35:
            errors.append("B1/B7 cone_01 phase-removal gate must test 35 windows")
        if phase_summary.get("required_exact_windows_for_b7_target") != 30:
            errors.append("B1/B7 cone_01 phase-removal gate B7 target must remain 30 windows")
        if phase_summary.get("continuous_rz_exact_pass_count") != 0:
            errors.append("B1/B7 cone_01 phase-removal gate should have 0 continuous-RZ exact passes")
        if phase_summary.get("restricted_gate_clears_b7_target") is not False:
            errors.append("B1/B7 cone_01 phase-removal gate must not clear the B7 target")
        for field in [
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "obstruction_theorem_claimed",
        ]:
            if phase_claims.get(field) is not False:
                errors.append(f"B1/B7 cone_01 phase-removal gate must not claim {field}")
        if phase_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 cone_01 phase-removal gate validation errors must remain zero")
    else:
        errors.append(f"missing B1/B7 cone_01 phase-removal gate report: {b1_b7_cone01_phase_removal_path}")

    b1_b7_cone01_euler_reabsorption = {
        "path": str(b1_b7_cone01_euler_reabsorption_path),
        "exists": b1_b7_cone01_euler_reabsorption_path.exists(),
    }
    if not b1_b7_cone01_euler_reabsorption_manifest:
        errors.append("B1 manifest missing current result: b1_b7_cone01_euler_reabsorption_gate_v0")
    else:
        if (
            b1_b7_cone01_euler_reabsorption_manifest.get("status")
            != "cone01_euler_reabsorption_restricted_negative_gate"
        ):
            errors.append("B1/B7 cone_01 Euler-reabsorption gate must remain a restricted negative gate")
        for field in ["report", "markdown_report", "source_qasm"]:
            value = b1_b7_cone01_euler_reabsorption_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 cone_01 Euler-reabsorption gate missing existing {field} path: {value}")
    if b1_b7_cone01_euler_reabsorption_path.exists():
        euler_payload = json.loads(read(b1_b7_cone01_euler_reabsorption_path))
        euler_summary = euler_payload.get("summary", {})
        euler_claims = euler_payload.get("claim_boundary", {})
        b1_b7_cone01_euler_reabsorption.update(
            {
                "status": euler_payload.get("status"),
                "model_status": euler_payload.get("model_status"),
                "method": euler_payload.get("method"),
                "workload": euler_payload.get("workload"),
                "target_cone_id": euler_summary.get("target_cone_id"),
                "candidate_window_count": euler_summary.get("candidate_window_count"),
                "required_exact_windows_for_b7_target": euler_summary.get(
                    "required_exact_windows_for_b7_target"
                ),
                "exact_ry_candidate_angle_count": euler_summary.get("exact_ry_candidate_angle_count"),
                "optimizer_seed_count": euler_summary.get("optimizer_seed_count"),
                "fixed_ry_with_rz_reabsorption_exact_pass_count": euler_summary.get(
                    "fixed_ry_with_rz_reabsorption_exact_pass_count"
                ),
                "best_residual_norm": euler_summary.get("best_residual_norm"),
                "median_residual_norm": euler_summary.get("median_residual_norm"),
                "editable_rz_parameter_count_min": euler_summary.get("editable_rz_parameter_count_min"),
                "editable_rz_parameter_count_max": euler_summary.get("editable_rz_parameter_count_max"),
                "restricted_gate_clears_b7_target": euler_summary.get("restricted_gate_clears_b7_target"),
                "rewrite_claimed": euler_claims.get("rewrite_claimed"),
                "resource_saving_claimed": euler_claims.get("resource_saving_claimed"),
                "semantic_certificate_claimed": euler_claims.get("semantic_certificate_claimed"),
                "obstruction_theorem_claimed": euler_claims.get("obstruction_theorem_claimed"),
                "validation_error_count": euler_summary.get("validation_error_count"),
            }
        )
        if euler_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 cone_01 Euler-reabsorption gate report must have benchmark_id B1")
        if euler_payload.get("method") != "b1_b7_cone01_euler_reabsorption_gate_v0":
            errors.append("B1/B7 cone_01 Euler-reabsorption gate method mismatch")
        if euler_payload.get("status") != "cone01_euler_reabsorption_restricted_negative_gate":
            errors.append("B1/B7 cone_01 Euler-reabsorption gate status mismatch")
        for field in [
            "target_cone_id",
            "candidate_window_count",
            "required_exact_windows_for_b7_target",
            "exact_ry_candidate_angle_count",
            "optimizer_seed_count",
            "fixed_ry_with_rz_reabsorption_exact_pass_count",
            "best_residual_norm",
            "median_residual_norm",
            "editable_rz_parameter_count_min",
            "editable_rz_parameter_count_max",
            "restricted_gate_clears_b7_target",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "obstruction_theorem_claimed",
        ]:
            if euler_summary.get(field) != b1_b7_cone01_euler_reabsorption_manifest.get(field):
                errors.append(f"B1/B7 cone_01 Euler-reabsorption gate {field} mismatch")
        if euler_summary.get("target_cone_id") != "cone_01":
            errors.append("B1/B7 cone_01 Euler-reabsorption gate target cone must remain cone_01")
        if euler_summary.get("candidate_window_count") != 35:
            errors.append("B1/B7 cone_01 Euler-reabsorption gate must test 35 windows")
        if euler_summary.get("required_exact_windows_for_b7_target") != 30:
            errors.append("B1/B7 cone_01 Euler-reabsorption gate B7 target must remain 30 windows")
        if euler_summary.get("fixed_ry_with_rz_reabsorption_exact_pass_count") != 0:
            errors.append("B1/B7 cone_01 Euler-reabsorption gate should have 0 exact passes")
        if euler_summary.get("restricted_gate_clears_b7_target") is not False:
            errors.append("B1/B7 cone_01 Euler-reabsorption gate must not clear the B7 target")
        for field in [
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "obstruction_theorem_claimed",
        ]:
            if euler_claims.get(field) is not False:
                errors.append(f"B1/B7 cone_01 Euler-reabsorption gate must not claim {field}")
        if euler_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 cone_01 Euler-reabsorption gate validation errors must remain zero")
    else:
        errors.append(
            f"missing B1/B7 cone_01 Euler-reabsorption gate report: {b1_b7_cone01_euler_reabsorption_path}"
        )

    b1_b7_cone01_parameter_transfer = {
        "path": str(b1_b7_cone01_parameter_transfer_path),
        "exists": b1_b7_cone01_parameter_transfer_path.exists(),
    }
    if not b1_b7_cone01_parameter_transfer_manifest:
        errors.append("B1 manifest missing current result: b1_b7_cone01_parameter_transfer_gate_v0")
    else:
        if (
            b1_b7_cone01_parameter_transfer_manifest.get("status")
            != "cone01_parameter_transfer_obligation_gate"
        ):
            errors.append("B1/B7 cone_01 parameter-transfer gate must remain an obligation gate")
        for field in ["report", "markdown_report", "source_qasm"]:
            value = b1_b7_cone01_parameter_transfer_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 cone_01 parameter-transfer gate missing existing {field} path: {value}")
    if b1_b7_cone01_parameter_transfer_path.exists():
        transfer_payload = json.loads(read(b1_b7_cone01_parameter_transfer_path))
        transfer_summary = transfer_payload.get("summary", {})
        transfer_claims = transfer_payload.get("claim_boundary", {})
        b1_b7_cone01_parameter_transfer.update(
            {
                "status": transfer_payload.get("status"),
                "model_status": transfer_payload.get("model_status"),
                "method": transfer_payload.get("method"),
                "workload": transfer_payload.get("workload"),
                "target_cone_id": transfer_summary.get("target_cone_id"),
                "candidate_window_count": transfer_summary.get("candidate_window_count"),
                "required_exact_windows_for_b7_target": transfer_summary.get(
                    "required_exact_windows_for_b7_target"
                ),
                "nonzero_parameter_sensitivity_count": transfer_summary.get(
                    "nonzero_parameter_sensitivity_count"
                ),
                "parameter_sensitivity_zero_count": transfer_summary.get("parameter_sensitivity_zero_count"),
                "near_pi_over_four_grid_count": transfer_summary.get("near_pi_over_four_grid_count"),
                "distinct_canonical_theta_count": transfer_summary.get("distinct_canonical_theta_count"),
                "largest_repeated_theta_group": transfer_summary.get("largest_repeated_theta_group"),
                "repeated_theta_occurrence_count": transfer_summary.get("repeated_theta_occurrence_count"),
                "minimum_parameter_carrier_obligation_for_b7_target": transfer_summary.get(
                    "minimum_parameter_carrier_obligation_for_b7_target"
                ),
                "deletion_without_parameter_carrier_clears_b7_target": transfer_summary.get(
                    "deletion_without_parameter_carrier_clears_b7_target"
                ),
                "rewrite_claimed": transfer_claims.get("rewrite_claimed"),
                "resource_saving_claimed": transfer_claims.get("resource_saving_claimed"),
                "semantic_certificate_claimed": transfer_claims.get("semantic_certificate_claimed"),
                "obstruction_theorem_claimed": transfer_claims.get("obstruction_theorem_claimed"),
                "validation_error_count": transfer_summary.get("validation_error_count"),
            }
        )
        if transfer_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 cone_01 parameter-transfer gate report must have benchmark_id B1")
        if transfer_payload.get("method") != "b1_b7_cone01_parameter_transfer_gate_v0":
            errors.append("B1/B7 cone_01 parameter-transfer gate method mismatch")
        if transfer_payload.get("status") != "cone01_parameter_transfer_obligation_gate":
            errors.append("B1/B7 cone_01 parameter-transfer gate status mismatch")
        for field in [
            "target_cone_id",
            "candidate_window_count",
            "required_exact_windows_for_b7_target",
            "nonzero_parameter_sensitivity_count",
            "parameter_sensitivity_zero_count",
            "near_pi_over_four_grid_count",
            "distinct_canonical_theta_count",
            "largest_repeated_theta_group",
            "repeated_theta_occurrence_count",
            "minimum_parameter_carrier_obligation_for_b7_target",
            "deletion_without_parameter_carrier_clears_b7_target",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "obstruction_theorem_claimed",
        ]:
            if transfer_summary.get(field) != b1_b7_cone01_parameter_transfer_manifest.get(field):
                errors.append(f"B1/B7 cone_01 parameter-transfer gate {field} mismatch")
        if transfer_summary.get("target_cone_id") != "cone_01":
            errors.append("B1/B7 cone_01 parameter-transfer gate target cone must remain cone_01")
        if transfer_summary.get("candidate_window_count") != 35:
            errors.append("B1/B7 cone_01 parameter-transfer gate must test 35 windows")
        if transfer_summary.get("required_exact_windows_for_b7_target") != 30:
            errors.append("B1/B7 cone_01 parameter-transfer gate B7 target must remain 30 windows")
        if transfer_summary.get("nonzero_parameter_sensitivity_count") != 35:
            errors.append("B1/B7 cone_01 parameter-transfer gate should find all 35 windows parameter-sensitive")
        if transfer_summary.get("parameter_sensitivity_zero_count") != 0:
            errors.append("B1/B7 cone_01 parameter-transfer gate should find zero insensitive windows")
        if transfer_summary.get("near_pi_over_four_grid_count") != 0:
            errors.append("B1/B7 cone_01 parameter-transfer gate should find zero pi/4-grid windows")
        if transfer_summary.get("deletion_without_parameter_carrier_clears_b7_target") is not False:
            errors.append("B1/B7 cone_01 parameter-transfer gate must not clear B7 without parameter carrier")
        for field in [
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "obstruction_theorem_claimed",
        ]:
            if transfer_claims.get(field) is not False:
                errors.append(f"B1/B7 cone_01 parameter-transfer gate must not claim {field}")
        if transfer_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 cone_01 parameter-transfer gate validation errors must remain zero")
    else:
        errors.append(
            f"missing B1/B7 cone_01 parameter-transfer gate report: {b1_b7_cone01_parameter_transfer_path}"
        )

    b1_b7_cone01_theta_sharing = {
        "path": str(b1_b7_cone01_theta_sharing_path),
        "exists": b1_b7_cone01_theta_sharing_path.exists(),
    }
    if not b1_b7_cone01_theta_sharing_manifest:
        errors.append("B1 manifest missing current result: b1_b7_cone01_theta_sharing_ledger_gate_v0")
    else:
        if b1_b7_cone01_theta_sharing_manifest.get("status") != "cone01_theta_sharing_ledger_guardrail":
            errors.append("B1/B7 cone_01 theta-sharing gate must remain a ledger guardrail")
        for field in ["report", "markdown_report"]:
            value = b1_b7_cone01_theta_sharing_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 cone_01 theta-sharing gate missing existing {field} path: {value}")
    if b1_b7_cone01_theta_sharing_path.exists():
        theta_payload = json.loads(read(b1_b7_cone01_theta_sharing_path))
        theta_summary = theta_payload.get("summary", {})
        theta_claims = theta_payload.get("claim_boundary", {})
        b1_b7_cone01_theta_sharing.update(
            {
                "status": theta_payload.get("status"),
                "model_status": theta_payload.get("model_status"),
                "method": theta_payload.get("method"),
                "workload": theta_payload.get("workload"),
                "candidate_window_count": theta_summary.get("candidate_window_count"),
                "distinct_theta_group_count": theta_summary.get("distinct_theta_group_count"),
                "duplicate_theta_occurrence_count": theta_summary.get("duplicate_theta_occurrence_count"),
                "proxy_t_cost_per_arbitrary_rotation": theta_summary.get("proxy_t_cost_per_arbitrary_rotation"),
                "optimistic_cache_proxy_t_reuse": theta_summary.get("optimistic_cache_proxy_t_reuse"),
                "target_removed_arbitrary_occurrences_for_gcm_h6_1_20": theta_summary.get(
                    "target_removed_arbitrary_occurrences_for_gcm_h6_1_20"
                ),
                "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": theta_summary.get(
                    "target_proxy_t_ledger_reduction_for_gcm_h6_1_20"
                ),
                "optimistic_cache_model_clears_target": theta_summary.get("optimistic_cache_model_clears_target"),
                "occurrence_ledger_removed_occurrences": theta_summary.get(
                    "occurrence_ledger_removed_occurrences"
                ),
                "occurrence_ledger_proxy_t_reduction": theta_summary.get("occurrence_ledger_proxy_t_reduction"),
                "occurrence_ledger_clears_target": theta_summary.get("occurrence_ledger_clears_target"),
                "additional_occurrence_certificates_required": theta_summary.get(
                    "additional_occurrence_certificates_required"
                ),
                "cache_model_not_accepted_as_ft_ledger": theta_summary.get("cache_model_not_accepted_as_ft_ledger"),
                "rewrite_claimed": theta_claims.get("rewrite_claimed"),
                "resource_saving_claimed": theta_claims.get("resource_saving_claimed"),
                "semantic_certificate_claimed": theta_claims.get("semantic_certificate_claimed"),
                "physical_resource_reduction_claimed": theta_claims.get("physical_resource_reduction_claimed"),
                "b7_ledger_improvement_claimed": theta_claims.get("b7_ledger_improvement_claimed"),
                "validation_error_count": theta_summary.get("validation_error_count"),
            }
        )
        if theta_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 cone_01 theta-sharing gate report must have benchmark_id B1")
        if theta_payload.get("method") != "b1_b7_cone01_theta_sharing_ledger_gate_v0":
            errors.append("B1/B7 cone_01 theta-sharing gate method mismatch")
        if theta_payload.get("status") != "cone01_theta_sharing_ledger_guardrail":
            errors.append("B1/B7 cone_01 theta-sharing gate status mismatch")
        for field in [
            "candidate_window_count",
            "distinct_theta_group_count",
            "duplicate_theta_occurrence_count",
            "proxy_t_cost_per_arbitrary_rotation",
            "optimistic_cache_proxy_t_reuse",
            "target_removed_arbitrary_occurrences_for_gcm_h6_1_20",
            "target_proxy_t_ledger_reduction_for_gcm_h6_1_20",
            "optimistic_cache_model_clears_target",
            "occurrence_ledger_removed_occurrences",
            "occurrence_ledger_proxy_t_reduction",
            "occurrence_ledger_clears_target",
            "additional_occurrence_certificates_required",
            "cache_model_not_accepted_as_ft_ledger",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "physical_resource_reduction_claimed",
        ]:
            if theta_summary.get(field) != b1_b7_cone01_theta_sharing_manifest.get(field):
                errors.append(f"B1/B7 cone_01 theta-sharing gate {field} mismatch")
        if theta_summary.get("candidate_window_count") != 35:
            errors.append("B1/B7 cone_01 theta-sharing gate must account for 35 windows")
        if theta_summary.get("distinct_theta_group_count") != 4:
            errors.append("B1/B7 cone_01 theta-sharing gate should preserve 4 theta groups")
        if theta_summary.get("duplicate_theta_occurrence_count") != 31:
            errors.append("B1/B7 cone_01 theta-sharing gate should record 31 duplicate occurrences")
        if theta_summary.get("optimistic_cache_proxy_t_reuse") != 620:
            errors.append("B1/B7 cone_01 theta-sharing gate optimistic cache proxy-T should be 620")
        if theta_summary.get("optimistic_cache_model_clears_target") is not True:
            errors.append("B1/B7 cone_01 theta-sharing gate optimistic cache model should clear target")
        if theta_summary.get("occurrence_ledger_removed_occurrences") != 0:
            errors.append("B1/B7 cone_01 theta-sharing gate occurrence ledger removed occurrences must be 0")
        if theta_summary.get("occurrence_ledger_proxy_t_reduction") != 0:
            errors.append("B1/B7 cone_01 theta-sharing gate occurrence ledger proxy-T reduction must be 0")
        if theta_summary.get("occurrence_ledger_clears_target") is not False:
            errors.append("B1/B7 cone_01 theta-sharing gate occurrence ledger must not clear target")
        if theta_summary.get("cache_model_not_accepted_as_ft_ledger") is not True:
            errors.append("B1/B7 cone_01 theta-sharing gate must reject cache model as FT ledger")
        for field in [
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if theta_claims.get(field) is not False:
                errors.append(f"B1/B7 cone_01 theta-sharing gate must not claim {field}")
        if theta_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 cone_01 theta-sharing gate validation errors must remain zero")
    else:
        errors.append(f"missing B1/B7 cone_01 theta-sharing gate report: {b1_b7_cone01_theta_sharing_path}")

    b1_b7_cone01_shared_theta_synthesis_object = {
        "path": str(b1_b7_cone01_shared_theta_synthesis_object_path),
        "exists": b1_b7_cone01_shared_theta_synthesis_object_path.exists(),
    }
    if not b1_b7_cone01_shared_theta_synthesis_object_manifest:
        errors.append("B1 manifest missing current result: b1_b7_cone01_shared_theta_synthesis_object_gate_v0")
    else:
        if (
            b1_b7_cone01_shared_theta_synthesis_object_manifest.get("status")
            != "cone01_shared_theta_synthesis_object_proposal"
        ):
            errors.append("B1/B7 cone_01 shared-theta object gate must remain a proposal")
        for field in ["report", "markdown_report"]:
            value = b1_b7_cone01_shared_theta_synthesis_object_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 cone_01 shared-theta object gate missing existing {field} path: {value}")
    if b1_b7_cone01_shared_theta_synthesis_object_path.exists():
        shared_payload = json.loads(read(b1_b7_cone01_shared_theta_synthesis_object_path))
        shared_summary = shared_payload.get("summary", {})
        shared_claims = shared_payload.get("claim_boundary", {})
        b1_b7_cone01_shared_theta_synthesis_object.update(
            {
                "status": shared_payload.get("status"),
                "model_status": shared_payload.get("model_status"),
                "method": shared_payload.get("method"),
                "workload": shared_payload.get("workload"),
                "candidate_window_count": shared_summary.get("candidate_window_count"),
                "shared_synthesis_object_count": shared_summary.get("shared_synthesis_object_count"),
                "distinct_theta_group_count": shared_summary.get("distinct_theta_group_count"),
                "covered_occurrence_count": shared_summary.get("covered_occurrence_count"),
                "duplicate_theta_occurrence_count": shared_summary.get("duplicate_theta_occurrence_count"),
                "optimistic_cache_proxy_t_reuse": shared_summary.get("optimistic_cache_proxy_t_reuse"),
                "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": shared_summary.get(
                    "target_proxy_t_ledger_reduction_for_gcm_h6_1_20"
                ),
                "shared_object_existence_gate_passed": shared_summary.get("shared_object_existence_gate_passed"),
                "all_candidate_windows_covered": shared_summary.get("all_candidate_windows_covered"),
                "semantic_replay_verified_object_count": shared_summary.get("semantic_replay_verified_object_count"),
                "physical_layout_assigned_object_count": shared_summary.get("physical_layout_assigned_object_count"),
                "b7_ledger_accepted_object_count": shared_summary.get("b7_ledger_accepted_object_count"),
                "occurrence_ledger_removed_occurrences": shared_summary.get("occurrence_ledger_removed_occurrences"),
                "occurrence_ledger_proxy_t_reduction": shared_summary.get("occurrence_ledger_proxy_t_reduction"),
                "cost_model_accepted": shared_summary.get("cost_model_accepted"),
                "rewrite_claimed": shared_claims.get("rewrite_claimed"),
                "resource_saving_claimed": shared_claims.get("resource_saving_claimed"),
                "semantic_certificate_claimed": shared_claims.get("semantic_certificate_claimed"),
                "physical_resource_reduction_claimed": shared_claims.get("physical_resource_reduction_claimed"),
                "b7_ledger_improvement_claimed": shared_claims.get("b7_ledger_improvement_claimed"),
                "validation_error_count": shared_summary.get("validation_error_count"),
            }
        )
        if shared_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 cone_01 shared-theta object gate report must have benchmark_id B1")
        if shared_payload.get("method") != "b1_b7_cone01_shared_theta_synthesis_object_gate_v0":
            errors.append("B1/B7 cone_01 shared-theta object gate method mismatch")
        if shared_payload.get("status") != "cone01_shared_theta_synthesis_object_proposal":
            errors.append("B1/B7 cone_01 shared-theta object gate status mismatch")
        if (
            shared_payload.get("model_status")
            != "shared_theta_objects_exist_without_replay_or_resource_acceptance"
        ):
            errors.append("B1/B7 cone_01 shared-theta object gate model_status mismatch")
        for field in [
            "candidate_window_count",
            "shared_synthesis_object_count",
            "distinct_theta_group_count",
            "covered_occurrence_count",
            "duplicate_theta_occurrence_count",
            "optimistic_cache_proxy_t_reuse",
            "target_proxy_t_ledger_reduction_for_gcm_h6_1_20",
            "shared_object_existence_gate_passed",
            "all_candidate_windows_covered",
            "semantic_replay_verified_object_count",
            "physical_layout_assigned_object_count",
            "b7_ledger_accepted_object_count",
            "occurrence_ledger_removed_occurrences",
            "occurrence_ledger_proxy_t_reduction",
            "cost_model_accepted",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if shared_summary.get(field) != b1_b7_cone01_shared_theta_synthesis_object_manifest.get(field):
                errors.append(f"B1/B7 cone_01 shared-theta object gate {field} mismatch")
        if shared_summary.get("candidate_window_count") != 35:
            errors.append("B1/B7 cone_01 shared-theta object gate must cover 35 candidate windows")
        if shared_summary.get("shared_synthesis_object_count") != 4:
            errors.append("B1/B7 cone_01 shared-theta object gate must define 4 shared objects")
        if shared_summary.get("covered_occurrence_count") != 35:
            errors.append("B1/B7 cone_01 shared-theta object gate must cover 35 occurrences")
        if shared_summary.get("shared_object_existence_gate_passed") is not True:
            errors.append("B1/B7 cone_01 shared-theta object gate should pass object existence")
        if shared_summary.get("all_candidate_windows_covered") is not True:
            errors.append("B1/B7 cone_01 shared-theta object gate should cover all windows")
        for field in [
            "semantic_replay_verified_object_count",
            "physical_layout_assigned_object_count",
            "b7_ledger_accepted_object_count",
            "occurrence_ledger_removed_occurrences",
            "occurrence_ledger_proxy_t_reduction",
        ]:
            if shared_summary.get(field) != 0:
                errors.append(f"B1/B7 cone_01 shared-theta object gate {field} must remain 0")
        for field in [
            "cost_model_accepted",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if shared_summary.get(field) is not False:
                errors.append(f"B1/B7 cone_01 shared-theta object gate summary must not claim {field}")
            if shared_claims.get(field) is not False:
                errors.append(f"B1/B7 cone_01 shared-theta object gate must not claim {field}")
        if shared_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 cone_01 shared-theta object gate validation errors must remain zero")
    else:
        errors.append(
            f"missing B1/B7 cone_01 shared-theta object gate report: "
            f"{b1_b7_cone01_shared_theta_synthesis_object_path}"
        )

    b1_b7_cone01_shared_theta_replay_verifier = {
        "path": str(b1_b7_cone01_shared_theta_replay_verifier_path),
        "exists": b1_b7_cone01_shared_theta_replay_verifier_path.exists(),
    }
    if not b1_b7_cone01_shared_theta_replay_verifier_manifest:
        errors.append("B1 manifest missing current result: b1_b7_cone01_shared_theta_replay_verifier_gate_v0")
    else:
        if (
            b1_b7_cone01_shared_theta_replay_verifier_manifest.get("status")
            != "cone01_shared_theta_replay_verifier_scaffold"
        ):
            errors.append("B1/B7 cone_01 shared-theta replay verifier must remain a scaffold")
        for field in ["report", "markdown_report"]:
            value = b1_b7_cone01_shared_theta_replay_verifier_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 cone_01 shared-theta replay verifier missing existing {field} path: {value}")
    if b1_b7_cone01_shared_theta_replay_verifier_path.exists():
        replay_payload = json.loads(read(b1_b7_cone01_shared_theta_replay_verifier_path))
        replay_summary = replay_payload.get("summary", {})
        replay_claims = replay_payload.get("claim_boundary", {})
        b1_b7_cone01_shared_theta_replay_verifier.update(
            {
                "status": replay_payload.get("status"),
                "model_status": replay_payload.get("model_status"),
                "method": replay_payload.get("method"),
                "workload": replay_payload.get("workload"),
                "candidate_window_count": replay_summary.get("candidate_window_count"),
                "shared_synthesis_object_count": replay_summary.get("shared_synthesis_object_count"),
                "replay_verified_object_count": replay_summary.get("replay_verified_object_count"),
                "replayed_occurrence_count": replay_summary.get("replayed_occurrence_count"),
                "parameter_transfer_expected_occurrence_count": replay_summary.get(
                    "parameter_transfer_expected_occurrence_count"
                ),
                "coverage_matches_parameter_transfer": replay_summary.get("coverage_matches_parameter_transfer"),
                "duplicate_line_count": replay_summary.get("duplicate_line_count"),
                "missing_qasm_line_count": replay_summary.get("missing_qasm_line_count"),
                "line_theta_mismatch_count": replay_summary.get("line_theta_mismatch_count"),
                "object_group_mismatch_count": replay_summary.get("object_group_mismatch_count"),
                "shared_theta_replay_gate_passed": replay_summary.get("shared_theta_replay_gate_passed"),
                "semantic_rewrite_verified": replay_summary.get("semantic_rewrite_verified"),
                "semantic_certificate_claimed": replay_summary.get("semantic_certificate_claimed"),
                "occurrence_ledger_removed_occurrences": replay_summary.get("occurrence_ledger_removed_occurrences"),
                "occurrence_ledger_proxy_t_reduction": replay_summary.get("occurrence_ledger_proxy_t_reduction"),
                "cost_model_accepted": replay_summary.get("cost_model_accepted"),
                "rewrite_claimed": replay_claims.get("rewrite_claimed"),
                "resource_saving_claimed": replay_claims.get("resource_saving_claimed"),
                "physical_resource_reduction_claimed": replay_claims.get("physical_resource_reduction_claimed"),
                "b7_ledger_improvement_claimed": replay_claims.get("b7_ledger_improvement_claimed"),
                "validation_error_count": replay_summary.get("validation_error_count"),
            }
        )
        if replay_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 cone_01 shared-theta replay verifier report must have benchmark_id B1")
        if replay_payload.get("method") != "b1_b7_cone01_shared_theta_replay_verifier_gate_v0":
            errors.append("B1/B7 cone_01 shared-theta replay verifier method mismatch")
        if replay_payload.get("status") != "cone01_shared_theta_replay_verifier_scaffold":
            errors.append("B1/B7 cone_01 shared-theta replay verifier status mismatch")
        if replay_payload.get("model_status") != "shared_theta_replay_verified_without_semantic_rewrite":
            errors.append("B1/B7 cone_01 shared-theta replay verifier model_status mismatch")
        for field in [
            "candidate_window_count",
            "shared_synthesis_object_count",
            "replay_verified_object_count",
            "replayed_occurrence_count",
            "parameter_transfer_expected_occurrence_count",
            "coverage_matches_parameter_transfer",
            "duplicate_line_count",
            "missing_qasm_line_count",
            "line_theta_mismatch_count",
            "object_group_mismatch_count",
            "shared_theta_replay_gate_passed",
            "semantic_rewrite_verified",
            "semantic_certificate_claimed",
            "occurrence_ledger_removed_occurrences",
            "occurrence_ledger_proxy_t_reduction",
            "cost_model_accepted",
            "rewrite_claimed",
            "resource_saving_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if replay_summary.get(field) != b1_b7_cone01_shared_theta_replay_verifier_manifest.get(field):
                errors.append(f"B1/B7 cone_01 shared-theta replay verifier {field} mismatch")
        if replay_summary.get("candidate_window_count") != 35:
            errors.append("B1/B7 cone_01 shared-theta replay verifier must cover 35 candidate windows")
        if replay_summary.get("shared_synthesis_object_count") != 4:
            errors.append("B1/B7 cone_01 shared-theta replay verifier must see 4 shared objects")
        if replay_summary.get("replay_verified_object_count") != 4:
            errors.append("B1/B7 cone_01 shared-theta replay verifier must verify 4 shared objects")
        if replay_summary.get("replayed_occurrence_count") != 35:
            errors.append("B1/B7 cone_01 shared-theta replay verifier must replay 35 occurrences")
        if replay_summary.get("coverage_matches_parameter_transfer") is not True:
            errors.append("B1/B7 cone_01 shared-theta replay verifier must match parameter transfer coverage")
        if replay_summary.get("shared_theta_replay_gate_passed") is not True:
            errors.append("B1/B7 cone_01 shared-theta replay verifier gate should pass")
        for field in [
            "duplicate_line_count",
            "missing_qasm_line_count",
            "line_theta_mismatch_count",
            "object_group_mismatch_count",
            "occurrence_ledger_removed_occurrences",
            "occurrence_ledger_proxy_t_reduction",
        ]:
            if replay_summary.get(field) != 0:
                errors.append(f"B1/B7 cone_01 shared-theta replay verifier {field} must remain 0")
        for field in [
            "semantic_rewrite_verified",
            "semantic_certificate_claimed",
            "cost_model_accepted",
            "rewrite_claimed",
            "resource_saving_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if replay_summary.get(field) is not False:
                errors.append(f"B1/B7 cone_01 shared-theta replay verifier summary must not claim {field}")
            if replay_claims.get(field) is not False:
                errors.append(f"B1/B7 cone_01 shared-theta replay verifier must not claim {field}")
        if replay_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 cone_01 shared-theta replay verifier validation errors must remain zero")
    else:
        errors.append(
            f"missing B1/B7 cone_01 shared-theta replay verifier report: "
            f"{b1_b7_cone01_shared_theta_replay_verifier_path}"
        )

    b1_b7_cone01_shared_theta_layout_routing = {
        "path": str(b1_b7_cone01_shared_theta_layout_routing_path),
        "exists": b1_b7_cone01_shared_theta_layout_routing_path.exists(),
    }
    if not b1_b7_cone01_shared_theta_layout_routing_manifest:
        errors.append("B1 manifest missing current result: b1_b7_cone01_shared_theta_layout_routing_gate_v0")
    else:
        if (
            b1_b7_cone01_shared_theta_layout_routing_manifest.get("status")
            != "cone01_shared_theta_logical_layout_routing_scaffold"
        ):
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate must remain a logical scaffold")
        for field in ["report", "markdown_report"]:
            value = b1_b7_cone01_shared_theta_layout_routing_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 cone_01 shared-theta layout/routing gate missing existing {field} path: {value}")
    if b1_b7_cone01_shared_theta_layout_routing_path.exists():
        layout_payload = json.loads(read(b1_b7_cone01_shared_theta_layout_routing_path))
        layout_summary = layout_payload.get("summary", {})
        layout_claims = layout_payload.get("claim_boundary", {})
        b1_b7_cone01_shared_theta_layout_routing.update(
            {
                "status": layout_payload.get("status"),
                "model_status": layout_payload.get("model_status"),
                "method": layout_payload.get("method"),
                "workload": layout_payload.get("workload"),
                "candidate_window_count": layout_summary.get("candidate_window_count"),
                "shared_synthesis_object_count": layout_summary.get("shared_synthesis_object_count"),
                "replay_verified_object_count": layout_summary.get("replay_verified_object_count"),
                "replayed_occurrence_count": layout_summary.get("replayed_occurrence_count"),
                "layout_routed_object_count": layout_summary.get("layout_routed_object_count"),
                "layout_routed_occurrence_count": layout_summary.get("layout_routed_occurrence_count"),
                "logical_anchor_object_count": layout_summary.get("logical_anchor_object_count"),
                "logical_route_packet_count": layout_summary.get("logical_route_packet_count"),
                "logical_line_topology_qubit_count": layout_summary.get("logical_line_topology_qubit_count"),
                "total_logical_hop_count": layout_summary.get("total_logical_hop_count"),
                "max_logical_hop_count": layout_summary.get("max_logical_hop_count"),
                "missing_route_count": layout_summary.get("missing_route_count"),
                "layout_routing_gate_passed": layout_summary.get("layout_routing_gate_passed"),
                "physical_layout_claimed": layout_summary.get("physical_layout_claimed"),
                "factory_amortization_model_present": layout_summary.get("factory_amortization_model_present"),
                "shared_error_budget_present": layout_summary.get("shared_error_budget_present"),
                "semantic_rewrite_verified": layout_summary.get("semantic_rewrite_verified"),
                "semantic_certificate_claimed": layout_summary.get("semantic_certificate_claimed"),
                "occurrence_ledger_removed_occurrences": layout_summary.get("occurrence_ledger_removed_occurrences"),
                "occurrence_ledger_proxy_t_reduction": layout_summary.get("occurrence_ledger_proxy_t_reduction"),
                "cost_model_accepted": layout_summary.get("cost_model_accepted"),
                "rewrite_claimed": layout_claims.get("rewrite_claimed"),
                "resource_saving_claimed": layout_claims.get("resource_saving_claimed"),
                "physical_resource_reduction_claimed": layout_claims.get("physical_resource_reduction_claimed"),
                "b7_ledger_improvement_claimed": layout_claims.get("b7_ledger_improvement_claimed"),
                "validation_error_count": layout_summary.get("validation_error_count"),
            }
        )
        if layout_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate report must have benchmark_id B1")
        if layout_payload.get("method") != "b1_b7_cone01_shared_theta_layout_routing_gate_v0":
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate method mismatch")
        if layout_payload.get("status") != "cone01_shared_theta_logical_layout_routing_scaffold":
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate status mismatch")
        if layout_payload.get("model_status") != "logical_layout_routing_scaffold_not_physical_layout":
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate model_status mismatch")
        for field in [
            "candidate_window_count",
            "shared_synthesis_object_count",
            "replay_verified_object_count",
            "replayed_occurrence_count",
            "layout_routed_object_count",
            "layout_routed_occurrence_count",
            "logical_anchor_object_count",
            "logical_route_packet_count",
            "logical_line_topology_qubit_count",
            "total_logical_hop_count",
            "max_logical_hop_count",
            "missing_route_count",
            "layout_routing_gate_passed",
            "physical_layout_claimed",
            "factory_amortization_model_present",
            "shared_error_budget_present",
            "semantic_rewrite_verified",
            "semantic_certificate_claimed",
            "occurrence_ledger_removed_occurrences",
            "occurrence_ledger_proxy_t_reduction",
            "cost_model_accepted",
            "rewrite_claimed",
            "resource_saving_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if layout_summary.get(field) != b1_b7_cone01_shared_theta_layout_routing_manifest.get(field):
                errors.append(f"B1/B7 cone_01 shared-theta layout/routing gate {field} mismatch")
        if layout_summary.get("candidate_window_count") != 35:
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate must cover 35 candidate windows")
        if layout_summary.get("shared_synthesis_object_count") != 4:
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate must see 4 shared objects")
        if layout_summary.get("layout_routed_object_count") != 4:
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate must route 4 objects")
        if layout_summary.get("layout_routed_occurrence_count") != 35:
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate must route 35 occurrences")
        if layout_summary.get("logical_route_packet_count") != 35:
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate must emit 35 route packets")
        if layout_summary.get("total_logical_hop_count") != 139:
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate total hop count must be 139")
        if layout_summary.get("max_logical_hop_count") != 11:
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate max hop count must be 11")
        if layout_summary.get("missing_route_count") != 0:
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate missing routes must remain zero")
        if layout_summary.get("layout_routing_gate_passed") is not True:
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate should pass")
        for field in [
            "physical_layout_claimed",
            "factory_amortization_model_present",
            "shared_error_budget_present",
            "semantic_rewrite_verified",
            "semantic_certificate_claimed",
            "cost_model_accepted",
            "rewrite_claimed",
            "resource_saving_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if layout_summary.get(field) is not False:
                errors.append(f"B1/B7 cone_01 shared-theta layout/routing gate summary must not claim {field}")
            if field in layout_claims and layout_claims.get(field) is not False:
                errors.append(f"B1/B7 cone_01 shared-theta layout/routing gate must not claim {field}")
        for field in ["occurrence_ledger_removed_occurrences", "occurrence_ledger_proxy_t_reduction"]:
            if layout_summary.get(field) != 0:
                errors.append(f"B1/B7 cone_01 shared-theta layout/routing gate {field} must remain 0")
        if layout_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 cone_01 shared-theta layout/routing gate validation errors must remain zero")
    else:
        errors.append(
            f"missing B1/B7 cone_01 shared-theta layout/routing gate report: "
            f"{b1_b7_cone01_shared_theta_layout_routing_path}"
        )

    b1_b7_cone01_shared_theta_factory_amortization = {
        "path": str(b1_b7_cone01_shared_theta_factory_amortization_path),
        "exists": b1_b7_cone01_shared_theta_factory_amortization_path.exists(),
    }
    if not b1_b7_cone01_shared_theta_factory_amortization_manifest:
        errors.append("B1 manifest missing current result: b1_b7_cone01_shared_theta_factory_amortization_gate_v0")
    else:
        if (
            b1_b7_cone01_shared_theta_factory_amortization_manifest.get("status")
            != "cone01_shared_theta_factory_amortization_scaffold"
        ):
            errors.append("B1/B7 cone_01 shared-theta factory-amortization gate must remain a scaffold")
        for field in ["report", "markdown_report"]:
            value = b1_b7_cone01_shared_theta_factory_amortization_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 cone_01 shared-theta factory-amortization gate missing existing {field} path: {value}")
    if b1_b7_cone01_shared_theta_factory_amortization_path.exists():
        factory_payload = json.loads(read(b1_b7_cone01_shared_theta_factory_amortization_path))
        factory_summary = factory_payload.get("summary", {})
        factory_claims = factory_payload.get("claim_boundary", {})
        b1_b7_cone01_shared_theta_factory_amortization.update(
            {
                "status": factory_payload.get("status"),
                "model_status": factory_payload.get("model_status"),
                "method": factory_payload.get("method"),
                "workload": factory_payload.get("workload"),
                "candidate_window_count": factory_summary.get("candidate_window_count"),
                "shared_synthesis_object_count": factory_summary.get("shared_synthesis_object_count"),
                "layout_routed_occurrence_count": factory_summary.get("layout_routed_occurrence_count"),
                "distinct_theta_group_count": factory_summary.get("distinct_theta_group_count"),
                "duplicate_theta_occurrence_count": factory_summary.get("duplicate_theta_occurrence_count"),
                "proxy_t_cost_per_arbitrary_rotation": factory_summary.get("proxy_t_cost_per_arbitrary_rotation"),
                "baseline_factory_compilation_count": factory_summary.get("baseline_factory_compilation_count"),
                "shared_object_factory_compilation_count": factory_summary.get("shared_object_factory_compilation_count"),
                "amortized_saved_compilation_count": factory_summary.get("amortized_saved_compilation_count"),
                "baseline_proxy_t_pressure": factory_summary.get("baseline_proxy_t_pressure"),
                "shared_object_proxy_t_pressure": factory_summary.get("shared_object_proxy_t_pressure"),
                "gross_proxy_t_pressure_delta": factory_summary.get("gross_proxy_t_pressure_delta"),
                "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": factory_summary.get(
                    "target_proxy_t_ledger_reduction_for_gcm_h6_1_20"
                ),
                "factory_amortization_gate_passed": factory_summary.get("factory_amortization_gate_passed"),
                "physical_factory_schedule_present": factory_summary.get("physical_factory_schedule_present"),
                "shared_error_budget_present": factory_summary.get("shared_error_budget_present"),
                "independent_baseline_present": factory_summary.get("independent_baseline_present"),
                "refreshed_b7_ledger_present": factory_summary.get("refreshed_b7_ledger_present"),
                "occurrence_ledger_removed_occurrences": factory_summary.get("occurrence_ledger_removed_occurrences"),
                "occurrence_ledger_proxy_t_reduction": factory_summary.get("occurrence_ledger_proxy_t_reduction"),
                "cost_model_accepted": factory_summary.get("cost_model_accepted"),
                "rewrite_claimed": factory_claims.get("rewrite_claimed"),
                "resource_saving_claimed": factory_claims.get("resource_saving_claimed"),
                "semantic_certificate_claimed": factory_claims.get("semantic_certificate_claimed"),
                "physical_resource_reduction_claimed": factory_claims.get("physical_resource_reduction_claimed"),
                "b7_ledger_improvement_claimed": factory_claims.get("b7_ledger_improvement_claimed"),
                "validation_error_count": factory_summary.get("validation_error_count"),
            }
        )
        if factory_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 cone_01 shared-theta factory-amortization gate report must have benchmark_id B1")
        if factory_payload.get("method") != "b1_b7_cone01_shared_theta_factory_amortization_gate_v0":
            errors.append("B1/B7 cone_01 shared-theta factory-amortization gate method mismatch")
        if factory_payload.get("status") != "cone01_shared_theta_factory_amortization_scaffold":
            errors.append("B1/B7 cone_01 shared-theta factory-amortization gate status mismatch")
        if factory_payload.get("model_status") != "factory_amortization_scaffold_not_physical_cost_model":
            errors.append("B1/B7 cone_01 shared-theta factory-amortization gate model_status mismatch")
        for field in [
            "candidate_window_count",
            "shared_synthesis_object_count",
            "layout_routed_occurrence_count",
            "distinct_theta_group_count",
            "duplicate_theta_occurrence_count",
            "proxy_t_cost_per_arbitrary_rotation",
            "baseline_factory_compilation_count",
            "shared_object_factory_compilation_count",
            "amortized_saved_compilation_count",
            "baseline_proxy_t_pressure",
            "shared_object_proxy_t_pressure",
            "gross_proxy_t_pressure_delta",
            "target_proxy_t_ledger_reduction_for_gcm_h6_1_20",
            "factory_amortization_gate_passed",
            "physical_factory_schedule_present",
            "shared_error_budget_present",
            "independent_baseline_present",
            "refreshed_b7_ledger_present",
            "occurrence_ledger_removed_occurrences",
            "occurrence_ledger_proxy_t_reduction",
            "cost_model_accepted",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if factory_summary.get(field) != b1_b7_cone01_shared_theta_factory_amortization_manifest.get(field):
                errors.append(f"B1/B7 cone_01 shared-theta factory-amortization gate {field} mismatch")
        expected_factory_values = {
            "candidate_window_count": 35,
            "shared_synthesis_object_count": 4,
            "layout_routed_occurrence_count": 35,
            "distinct_theta_group_count": 4,
            "duplicate_theta_occurrence_count": 31,
            "proxy_t_cost_per_arbitrary_rotation": 20,
            "baseline_factory_compilation_count": 35,
            "shared_object_factory_compilation_count": 4,
            "amortized_saved_compilation_count": 31,
            "baseline_proxy_t_pressure": 700,
            "shared_object_proxy_t_pressure": 80,
            "gross_proxy_t_pressure_delta": 620,
            "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": 600,
        }
        for field, value in expected_factory_values.items():
            if factory_summary.get(field) != value:
                errors.append(f"B1/B7 cone_01 shared-theta factory-amortization gate {field} must be {value}")
        if factory_summary.get("factory_amortization_gate_passed") is not True:
            errors.append("B1/B7 cone_01 shared-theta factory-amortization gate should pass")
        for field in [
            "physical_factory_schedule_present",
            "shared_error_budget_present",
            "independent_baseline_present",
            "refreshed_b7_ledger_present",
            "cost_model_accepted",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if factory_summary.get(field) is not False:
                errors.append(f"B1/B7 cone_01 shared-theta factory-amortization gate summary must not claim {field}")
            if field in factory_claims and factory_claims.get(field) is not False:
                errors.append(f"B1/B7 cone_01 shared-theta factory-amortization gate must not claim {field}")
        for field in ["occurrence_ledger_removed_occurrences", "occurrence_ledger_proxy_t_reduction"]:
            if factory_summary.get(field) != 0:
                errors.append(f"B1/B7 cone_01 shared-theta factory-amortization gate {field} must remain 0")
        if factory_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 cone_01 shared-theta factory-amortization gate validation errors must remain zero")
    else:
        errors.append(
            f"missing B1/B7 cone_01 shared-theta factory-amortization gate report: "
            f"{b1_b7_cone01_shared_theta_factory_amortization_path}"
        )

    b1_b7_cone01_shared_theta_error_budget = {
        "path": str(b1_b7_cone01_shared_theta_error_budget_path),
        "exists": b1_b7_cone01_shared_theta_error_budget_path.exists(),
    }
    if not b1_b7_cone01_shared_theta_error_budget_manifest:
        errors.append("B1 manifest missing current result: b1_b7_cone01_shared_theta_error_budget_gate_v0")
    else:
        if (
            b1_b7_cone01_shared_theta_error_budget_manifest.get("status")
            != "cone01_shared_theta_error_budget_scaffold"
        ):
            errors.append("B1/B7 cone_01 shared-theta error-budget gate must remain a scaffold")
        for field in ["report", "markdown_report"]:
            value = b1_b7_cone01_shared_theta_error_budget_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 cone_01 shared-theta error-budget gate missing existing {field} path: {value}")
    if b1_b7_cone01_shared_theta_error_budget_path.exists():
        error_budget_payload = json.loads(read(b1_b7_cone01_shared_theta_error_budget_path))
        error_budget_summary = error_budget_payload.get("summary", {})
        error_budget_claims = error_budget_payload.get("claim_boundary", {})
        b1_b7_cone01_shared_theta_error_budget.update(
            {
                "status": error_budget_payload.get("status"),
                "model_status": error_budget_payload.get("model_status"),
                "method": error_budget_payload.get("method"),
                "workload": error_budget_payload.get("workload"),
                "candidate_window_count": error_budget_summary.get("candidate_window_count"),
                "shared_synthesis_object_count": error_budget_summary.get("shared_synthesis_object_count"),
                "layout_routed_occurrence_count": error_budget_summary.get("layout_routed_occurrence_count"),
                "distinct_theta_group_count": error_budget_summary.get("distinct_theta_group_count"),
                "duplicate_theta_occurrence_count": error_budget_summary.get("duplicate_theta_occurrence_count"),
                "total_shared_theta_error_budget": error_budget_summary.get("total_shared_theta_error_budget"),
                "per_object_error_budget": error_budget_summary.get("per_object_error_budget"),
                "per_occurrence_error_budget": error_budget_summary.get("per_occurrence_error_budget"),
                "aggregate_per_occurrence_error_budget": error_budget_summary.get(
                    "aggregate_per_occurrence_error_budget"
                ),
                "aggregate_object_error_budget": error_budget_summary.get("aggregate_object_error_budget"),
                "unused_total_error_budget": error_budget_summary.get("unused_total_error_budget"),
                "correlation_group_count": error_budget_summary.get("correlation_group_count"),
                "max_correlated_occurrence_count": error_budget_summary.get("max_correlated_occurrence_count"),
                "shared_error_budget_gate_passed": error_budget_summary.get("shared_error_budget_gate_passed"),
                "factory_amortization_gate_passed": error_budget_summary.get("factory_amortization_gate_passed"),
                "independent_calibration_present": error_budget_summary.get("independent_calibration_present"),
                "hardware_noise_model_present": error_budget_summary.get("hardware_noise_model_present"),
                "independent_baseline_present": error_budget_summary.get("independent_baseline_present"),
                "refreshed_b7_ledger_present": error_budget_summary.get("refreshed_b7_ledger_present"),
                "occurrence_ledger_removed_occurrences": error_budget_summary.get("occurrence_ledger_removed_occurrences"),
                "occurrence_ledger_proxy_t_reduction": error_budget_summary.get("occurrence_ledger_proxy_t_reduction"),
                "cost_model_accepted": error_budget_summary.get("cost_model_accepted"),
                "rewrite_claimed": error_budget_claims.get("rewrite_claimed"),
                "resource_saving_claimed": error_budget_claims.get("resource_saving_claimed"),
                "semantic_certificate_claimed": error_budget_claims.get("semantic_certificate_claimed"),
                "physical_resource_reduction_claimed": error_budget_claims.get("physical_resource_reduction_claimed"),
                "b7_ledger_improvement_claimed": error_budget_claims.get("b7_ledger_improvement_claimed"),
                "validation_error_count": error_budget_summary.get("validation_error_count"),
            }
        )
        if error_budget_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 cone_01 shared-theta error-budget gate report must have benchmark_id B1")
        if error_budget_payload.get("method") != "b1_b7_cone01_shared_theta_error_budget_gate_v0":
            errors.append("B1/B7 cone_01 shared-theta error-budget gate method mismatch")
        if error_budget_payload.get("status") != "cone01_shared_theta_error_budget_scaffold":
            errors.append("B1/B7 cone_01 shared-theta error-budget gate status mismatch")
        if error_budget_payload.get("model_status") != "shared_error_budget_scaffold_not_physical_cost_model":
            errors.append("B1/B7 cone_01 shared-theta error-budget gate model_status mismatch")
        for field in [
            "candidate_window_count",
            "shared_synthesis_object_count",
            "layout_routed_occurrence_count",
            "distinct_theta_group_count",
            "duplicate_theta_occurrence_count",
            "total_shared_theta_error_budget",
            "per_object_error_budget",
            "per_occurrence_error_budget",
            "aggregate_per_occurrence_error_budget",
            "aggregate_object_error_budget",
            "unused_total_error_budget",
            "correlation_group_count",
            "max_correlated_occurrence_count",
            "shared_error_budget_gate_passed",
            "factory_amortization_gate_passed",
            "independent_calibration_present",
            "hardware_noise_model_present",
            "independent_baseline_present",
            "refreshed_b7_ledger_present",
            "occurrence_ledger_removed_occurrences",
            "occurrence_ledger_proxy_t_reduction",
            "cost_model_accepted",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if error_budget_summary.get(field) != b1_b7_cone01_shared_theta_error_budget_manifest.get(field):
                errors.append(f"B1/B7 cone_01 shared-theta error-budget gate {field} mismatch")
        expected_error_budget_values = {
            "candidate_window_count": 35,
            "shared_synthesis_object_count": 4,
            "layout_routed_occurrence_count": 35,
            "distinct_theta_group_count": 4,
            "duplicate_theta_occurrence_count": 31,
            "total_shared_theta_error_budget": 1.0e-6,
            "per_object_error_budget": 2.5e-7,
            "per_occurrence_error_budget": 1.0e-8,
            "aggregate_per_occurrence_error_budget": 3.5e-7,
            "aggregate_object_error_budget": 1.0e-6,
            "unused_total_error_budget": 0.0,
            "correlation_group_count": 4,
            "max_correlated_occurrence_count": 16,
        }
        for field, value in expected_error_budget_values.items():
            if error_budget_summary.get(field) != value:
                errors.append(f"B1/B7 cone_01 shared-theta error-budget gate {field} must be {value}")
        if error_budget_summary.get("shared_error_budget_gate_passed") is not True:
            errors.append("B1/B7 cone_01 shared-theta error-budget gate should pass")
        if error_budget_summary.get("factory_amortization_gate_passed") is not True:
            errors.append("B1/B7 cone_01 shared-theta error-budget gate should depend on passed factory gate")
        for field in [
            "independent_calibration_present",
            "hardware_noise_model_present",
            "independent_baseline_present",
            "refreshed_b7_ledger_present",
            "cost_model_accepted",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if error_budget_summary.get(field) is not False:
                errors.append(f"B1/B7 cone_01 shared-theta error-budget gate summary must not claim {field}")
            if field in error_budget_claims and error_budget_claims.get(field) is not False:
                errors.append(f"B1/B7 cone_01 shared-theta error-budget gate must not claim {field}")
        for field in ["occurrence_ledger_removed_occurrences", "occurrence_ledger_proxy_t_reduction"]:
            if error_budget_summary.get(field) != 0:
                errors.append(f"B1/B7 cone_01 shared-theta error-budget gate {field} must remain 0")
        if error_budget_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 cone_01 shared-theta error-budget gate validation errors must remain zero")
    else:
        errors.append(
            f"missing B1/B7 cone_01 shared-theta error-budget gate report: "
            f"{b1_b7_cone01_shared_theta_error_budget_path}"
        )

    b1_b7_cone01_theta_sharing_cost_model = {
        "path": str(b1_b7_cone01_theta_sharing_cost_model_path),
        "exists": b1_b7_cone01_theta_sharing_cost_model_path.exists(),
    }
    if not b1_b7_cone01_theta_sharing_cost_model_manifest:
        errors.append("B1 manifest missing current result: b1_b7_cone01_theta_sharing_cost_model_gate_v0")
    else:
        if (
            b1_b7_cone01_theta_sharing_cost_model_manifest.get("status")
            != "cone01_theta_sharing_cost_model_not_accepted"
        ):
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must remain not accepted")
        for field in ["report", "markdown_report"]:
            value = b1_b7_cone01_theta_sharing_cost_model_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1/B7 cone_01 theta-sharing cost-model gate missing existing {field} path: {value}")
    if b1_b7_cone01_theta_sharing_cost_model_path.exists():
        cost_payload = json.loads(read(b1_b7_cone01_theta_sharing_cost_model_path))
        cost_summary = cost_payload.get("summary", {})
        cost_claims = cost_payload.get("claim_boundary", {})
        b1_b7_cone01_theta_sharing_cost_model.update(
            {
                "status": cost_payload.get("status"),
                "model_status": cost_payload.get("model_status"),
                "method": cost_payload.get("method"),
                "workload": cost_payload.get("workload"),
                "candidate_window_count": cost_summary.get("candidate_window_count"),
                "distinct_theta_group_count": cost_summary.get("distinct_theta_group_count"),
                "duplicate_theta_occurrence_count": cost_summary.get("duplicate_theta_occurrence_count"),
                "optimistic_cache_proxy_t_reuse": cost_summary.get("optimistic_cache_proxy_t_reuse"),
                "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": cost_summary.get(
                    "target_proxy_t_ledger_reduction_for_gcm_h6_1_20"
                ),
                "optimistic_cache_signal_present": cost_summary.get("optimistic_cache_signal_present"),
                "shared_synthesis_object_count": cost_summary.get("shared_synthesis_object_count"),
                "shared_object_existence_gate_passed": cost_summary.get("shared_object_existence_gate_passed"),
                "shared_object_all_windows_covered": cost_summary.get("shared_object_all_windows_covered"),
                "shared_theta_replay_gate_passed": cost_summary.get("shared_theta_replay_gate_passed"),
                "shared_theta_replay_verified_object_count": cost_summary.get(
                    "shared_theta_replay_verified_object_count"
                ),
                "shared_theta_replayed_occurrence_count": cost_summary.get(
                    "shared_theta_replayed_occurrence_count"
                ),
                "shared_theta_layout_routing_gate_passed": cost_summary.get(
                    "shared_theta_layout_routing_gate_passed"
                ),
                "shared_theta_layout_routed_object_count": cost_summary.get(
                    "shared_theta_layout_routed_object_count"
                ),
                "shared_theta_layout_routed_occurrence_count": cost_summary.get(
                    "shared_theta_layout_routed_occurrence_count"
                ),
                "shared_theta_layout_total_logical_hop_count": cost_summary.get(
                    "shared_theta_layout_total_logical_hop_count"
                ),
                "shared_theta_layout_max_logical_hop_count": cost_summary.get(
                    "shared_theta_layout_max_logical_hop_count"
                ),
                "shared_theta_factory_amortization_gate_passed": cost_summary.get(
                    "shared_theta_factory_amortization_gate_passed"
                ),
                "shared_theta_factory_baseline_compilation_count": cost_summary.get(
                    "shared_theta_factory_baseline_compilation_count"
                ),
                "shared_theta_factory_shared_object_compilation_count": cost_summary.get(
                    "shared_theta_factory_shared_object_compilation_count"
                ),
                "shared_theta_factory_gross_proxy_t_delta": cost_summary.get(
                    "shared_theta_factory_gross_proxy_t_delta"
                ),
                "shared_theta_error_budget_gate_passed": cost_summary.get(
                    "shared_theta_error_budget_gate_passed"
                ),
                "shared_theta_total_error_budget": cost_summary.get("shared_theta_total_error_budget"),
                "shared_theta_aggregate_per_occurrence_error_budget": cost_summary.get(
                    "shared_theta_aggregate_per_occurrence_error_budget"
                ),
                "shared_theta_correlation_group_count": cost_summary.get(
                    "shared_theta_correlation_group_count"
                ),
                "shared_theta_max_correlated_occurrence_count": cost_summary.get(
                    "shared_theta_max_correlated_occurrence_count"
                ),
                "cost_model_acceptance_gate_count": cost_summary.get("cost_model_acceptance_gate_count"),
                "cost_model_acceptance_pass_count": cost_summary.get("cost_model_acceptance_pass_count"),
                "cost_model_acceptance_fail_count": cost_summary.get("cost_model_acceptance_fail_count"),
                "cost_model_accepted": cost_summary.get("cost_model_accepted"),
                "occurrence_ledger_removed_occurrences": cost_summary.get(
                    "occurrence_ledger_removed_occurrences"
                ),
                "occurrence_ledger_proxy_t_reduction": cost_summary.get("occurrence_ledger_proxy_t_reduction"),
                "b7_ledger_proxy_t_reduction_after_cost_model": cost_summary.get(
                    "b7_ledger_proxy_t_reduction_after_cost_model"
                ),
                "additional_occurrence_certificates_required": cost_summary.get(
                    "additional_occurrence_certificates_required"
                ),
                "additional_cost_model_gates_required": cost_summary.get("additional_cost_model_gates_required"),
                "rewrite_claimed": cost_claims.get("rewrite_claimed"),
                "resource_saving_claimed": cost_claims.get("resource_saving_claimed"),
                "semantic_certificate_claimed": cost_claims.get("semantic_certificate_claimed"),
                "physical_resource_reduction_claimed": cost_claims.get("physical_resource_reduction_claimed"),
                "b7_ledger_improvement_claimed": cost_claims.get("b7_ledger_improvement_claimed"),
                "validation_error_count": cost_summary.get("validation_error_count"),
            }
        )
        if cost_payload.get("benchmark_id") != "B1":
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate report must have benchmark_id B1")
        if cost_payload.get("method") != "b1_b7_cone01_theta_sharing_cost_model_gate_v0":
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate method mismatch")
        if cost_payload.get("status") != "cone01_theta_sharing_cost_model_not_accepted":
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate status mismatch")
        if cost_payload.get("model_status") != "physical_theta_sharing_cost_model_requirements_error_budget_scaffolded":
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate model_status mismatch")
        for field in [
            "candidate_window_count",
            "distinct_theta_group_count",
            "duplicate_theta_occurrence_count",
            "optimistic_cache_proxy_t_reuse",
            "target_proxy_t_ledger_reduction_for_gcm_h6_1_20",
            "optimistic_cache_signal_present",
            "shared_synthesis_object_count",
            "shared_object_existence_gate_passed",
            "shared_object_all_windows_covered",
            "shared_theta_replay_gate_passed",
            "shared_theta_replay_verified_object_count",
            "shared_theta_replayed_occurrence_count",
            "shared_theta_layout_routing_gate_passed",
            "shared_theta_layout_routed_object_count",
            "shared_theta_layout_routed_occurrence_count",
            "shared_theta_layout_total_logical_hop_count",
            "shared_theta_layout_max_logical_hop_count",
            "shared_theta_factory_amortization_gate_passed",
            "shared_theta_factory_baseline_compilation_count",
            "shared_theta_factory_shared_object_compilation_count",
            "shared_theta_factory_gross_proxy_t_delta",
            "shared_theta_error_budget_gate_passed",
            "shared_theta_total_error_budget",
            "shared_theta_aggregate_per_occurrence_error_budget",
            "shared_theta_correlation_group_count",
            "shared_theta_max_correlated_occurrence_count",
            "cost_model_acceptance_gate_count",
            "cost_model_acceptance_pass_count",
            "cost_model_acceptance_fail_count",
            "cost_model_accepted",
            "occurrence_ledger_removed_occurrences",
            "occurrence_ledger_proxy_t_reduction",
            "b7_ledger_proxy_t_reduction_after_cost_model",
            "additional_occurrence_certificates_required",
            "additional_cost_model_gates_required",
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if cost_summary.get(field) != b1_b7_cone01_theta_sharing_cost_model_manifest.get(field):
                errors.append(f"B1/B7 cone_01 theta-sharing cost-model gate {field} mismatch")
        if cost_summary.get("candidate_window_count") != 35:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must account for 35 windows")
        if cost_summary.get("duplicate_theta_occurrence_count") != 31:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate should record 31 duplicate occurrences")
        if cost_summary.get("optimistic_cache_proxy_t_reuse") != 620:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate optimistic signal should be 620")
        if cost_summary.get("optimistic_cache_signal_present") is not True:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must preserve optimistic signal")
        if cost_summary.get("cost_model_acceptance_gate_count") != 8:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must have 8 acceptance gates")
        if cost_summary.get("shared_synthesis_object_count") != 4:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 4 shared objects")
        if cost_summary.get("shared_object_existence_gate_passed") is not True:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate CM-02 evidence must pass")
        if cost_summary.get("shared_object_all_windows_covered") is not True:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate shared objects must cover all windows")
        if cost_summary.get("shared_theta_replay_gate_passed") is not True:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate CM-03 replay evidence must pass")
        if cost_summary.get("shared_theta_replay_verified_object_count") != 4:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 4 replay-verified objects")
        if cost_summary.get("shared_theta_replayed_occurrence_count") != 35:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 35 replayed occurrences")
        if cost_summary.get("shared_theta_layout_routing_gate_passed") is not True:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate CM-04 layout evidence must pass")
        if cost_summary.get("shared_theta_layout_routed_object_count") != 4:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 4 layout-routed objects")
        if cost_summary.get("shared_theta_layout_routed_occurrence_count") != 35:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 35 layout-routed occurrences")
        if cost_summary.get("shared_theta_layout_total_logical_hop_count") != 139:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 139 total logical hops")
        if cost_summary.get("shared_theta_layout_max_logical_hop_count") != 11:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 11 max logical hops")
        if cost_summary.get("shared_theta_factory_amortization_gate_passed") is not True:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate CM-05 factory evidence must pass")
        if cost_summary.get("shared_theta_factory_baseline_compilation_count") != 35:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 35 baseline factory requests")
        if cost_summary.get("shared_theta_factory_shared_object_compilation_count") != 4:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 4 shared factory requests")
        if cost_summary.get("shared_theta_factory_gross_proxy_t_delta") != 620:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 620 gross factory proxy-T delta")
        if cost_summary.get("shared_theta_error_budget_gate_passed") is not True:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate CM-06 error-budget evidence must pass")
        if cost_summary.get("shared_theta_total_error_budget") != 1.0e-6:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see total error budget 1e-6")
        if cost_summary.get("shared_theta_aggregate_per_occurrence_error_budget") != 3.5e-7:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see aggregate occurrence error budget 3.5e-7")
        if cost_summary.get("shared_theta_correlation_group_count") != 4:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see 4 correlation groups")
        if cost_summary.get("shared_theta_max_correlated_occurrence_count") != 16:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate must see max correlated occurrence count 16")
        if cost_summary.get("cost_model_acceptance_pass_count") != 5:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate pass count must now be 5")
        if cost_summary.get("cost_model_acceptance_fail_count") != 3:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate fail count must now be 3")
        if cost_summary.get("cost_model_accepted") is not False:
            errors.append("B1/B7 cone_01 theta-sharing cost model must not be accepted")
        if cost_summary.get("b7_ledger_proxy_t_reduction_after_cost_model") != 0:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate B7 reduction must remain 0")
        for field in [
            "rewrite_claimed",
            "resource_saving_claimed",
            "semantic_certificate_claimed",
            "physical_resource_reduction_claimed",
            "b7_ledger_improvement_claimed",
        ]:
            if cost_claims.get(field) is not False:
                errors.append(f"B1/B7 cone_01 theta-sharing cost-model gate must not claim {field}")
        if cost_summary.get("validation_error_count") != 0:
            errors.append("B1/B7 cone_01 theta-sharing cost-model gate validation errors must remain zero")
    else:
        errors.append(
            f"missing B1/B7 cone_01 theta-sharing cost-model gate report: "
            f"{b1_b7_cone01_theta_sharing_cost_model_path}"
        )

    b1_synthetic_noise = {
        "path": str(b1_synthetic_noise_path),
        "exists": b1_synthetic_noise_path.exists(),
    }
    if not synthetic_noise_manifest:
        errors.append("B1 manifest missing current result: b1_synthetic_heavyhex_noise_proxy_v0")
    else:
        if synthetic_noise_manifest.get("status") != "synthetic_noise_proxy_not_calibrated_device_claim":
            errors.append("B1 synthetic noise proxy must remain a non-calibrated-device claim")
        for field in ["report", "source_routed_metrics", "b1_routed_metrics", "virtual_swap_metrics"]:
            value = synthetic_noise_manifest.get(field)
            if not value or not path_exists_from(benchmarks, value):
                errors.append(f"B1 synthetic noise proxy missing existing {field} path: {value}")
    if b1_synthetic_noise_path.exists():
        synthetic_payload = json.loads(read(b1_synthetic_noise_path))
        source_vs_virtual = next(
            (
                row
                for row in synthetic_payload.get("comparisons", [])
                if row.get("name") == "source_level1_routed_vs_virtual_swap"
            ),
            {},
        )
        b1_synthetic_noise.update(
            {
                "status": synthetic_payload.get("report_status"),
                "profile": synthetic_payload.get("profile_name"),
                "best_comparison_by_exposure_reduction": synthetic_payload.get(
                    "best_comparison_by_exposure_reduction"
                ),
                "source_vs_virtual_swap_exposure_reduction_pct": source_vs_virtual.get("metrics", {})
                .get("hardware_weighted_error_exposure", {})
                .get("reduction_pct"),
                "source_vs_virtual_swap_success_proxy_ratio": source_vs_virtual.get(
                    "aggregate_success_proxy_ratio"
                ),
            }
        )
        if synthetic_payload.get("report_status") != "synthetic_noise_proxy_not_calibrated_device_claim":
            errors.append("B1 synthetic noise proxy status must not claim calibrated device validation")
        if synthetic_payload.get("best_comparison_by_exposure_reduction") != "source_level1_routed_vs_virtual_swap":
            errors.append("B1 synthetic noise proxy should identify source-routed vs virtual-SWAP as best comparison")
        if (
            b1_synthetic_noise.get("source_vs_virtual_swap_exposure_reduction_pct") is None
            or b1_synthetic_noise["source_vs_virtual_swap_exposure_reduction_pct"] <= 0
        ):
            errors.append("B1 synthetic noise proxy should show positive source-routed vs virtual-SWAP exposure reduction")
    else:
        errors.append(f"missing B1 synthetic noise proxy report: {b1_synthetic_noise_path}")

    prooflog_keys = [
        "qasmbench_small_fixed_point_pipeline_with_proof_logs_v0",
        "b1_exact_extension_fixed_point_pipeline_v0",
        "qasmbench_interaction_stress_hhl_n10_with_proof_logs_v0",
    ]
    b1_verification = {}
    for key in prooflog_keys:
        row = current_results.get(key)
        if not row:
            errors.append(f"B1 manifest missing current result: {key}")
            continue
        for flag in ["proof_log_audit_passed", "proof_log_replay_passed", "proof_log_semantic_passed"]:
            if row.get(flag) is not True:
                errors.append(f"{key} has {flag}={row.get(flag)!r}, expected true")
        for field in ["summary", "audit", "replay", "semantic"]:
            if field not in row or not path_exists_from(benchmarks, row[field]):
                errors.append(f"{key} missing existing {field} path: {row.get(field)}")
        b1_verification[key] = {
            "audit": row.get("proof_log_audit_passed"),
            "replay": row.get("proof_log_replay_passed"),
            "semantic": row.get("proof_log_semantic_passed"),
            "proof_events": row.get("proof_events", {}),
            "heavy_hex_like_exposure_reduction": row.get("heavy_hex_like_exposure_reduction"),
        }

    b1_certificate_report = {
        "path": str(b1_certificate_report_path),
        "exists": b1_certificate_report_path.exists(),
    }
    if not b1_certificate_report_path.exists():
        errors.append(f"missing B1 certificate evidence report: {b1_certificate_report_path}")
    else:
        payload = json.loads(read(b1_certificate_report_path))
        prooflog_rows = payload.get("prooflog_results", [])
        gates = payload.get("gates", {})
        b1_certificate_report.update(
            {
                "status": payload.get("report_status"),
                "prooflog_result_count": len(prooflog_rows),
                "exact_circuit_count": payload.get("exact_aggregate", {}).get("circuit_count"),
                "exact_equivalence_failed": payload.get("exact_aggregate", {}).get("equivalence_failed"),
                "unsupported_claim_count": len(payload.get("claim_not_supported_yet", [])),
                "proof_log_verification_passed": gates.get("proof_log_verification", {}).get("passed"),
                "minimum_circuit_count_passed": gates.get("minimum_circuit_count", {}).get("passed"),
                "aggregate_hardware_exposure_reduction_passed": gates.get("aggregate_hardware_exposure_reduction", {}).get("passed"),
                "ablation_table_passed": gates.get("ablation_table", {}).get("passed"),
                "baseline_comparison_passed": gates.get("baseline_comparison", {}).get("passed"),
                "routing_diagnostic_passed": gates.get("routing_diagnostic", {}).get("passed"),
                "routing_aware_calibrated_heavy_hex_baseline_passed": gates.get(
                    "routing_aware_calibrated_heavy_hex_baseline", {}
                ).get("passed"),
                "heavyhex_topology_diagnostic_passed": gates.get("heavyhex_topology_diagnostic", {}).get("passed"),
                "heavyhex_end_to_end_routed_benefit_passed": gates.get(
                    "heavyhex_end_to_end_routed_benefit", {}
                ).get("passed"),
                "post_routing_bottleneck_profile_passed": gates.get(
                    "post_routing_bottleneck_profile", {}
                ).get("passed"),
                "post_routing_swap_macro_compression_passed": gates.get(
                    "post_routing_swap_macro_compression", {}
                ).get("passed"),
                "virtual_swap_elimination_passed": gates.get("virtual_swap_elimination", {}).get("passed"),
                "virtual_swap_proof_replay_passed": gates.get("virtual_swap_proof_replay", {}).get("passed"),
                "synthetic_heavyhex_noise_proxy_passed": gates.get(
                    "synthetic_heavyhex_noise_proxy", {}
                ).get("passed"),
                "global_equivalence_scope_passed": gates.get("global_equivalence_scope", {}).get("passed"),
            }
        )
        if payload.get("benchmark_id") != "B1":
            errors.append(f"B1 certificate report benchmark_id={payload.get('benchmark_id')!r}, expected 'B1'")
        if payload.get("report_status") != "evidence_package_not_final_claim":
            errors.append("B1 certificate report must remain marked as evidence_package_not_final_claim")
        if len(prooflog_rows) != 3:
            errors.append(f"B1 certificate report has {len(prooflog_rows)} proof-log rows, expected 3")
        for row in prooflog_rows:
            if not (row.get("audit_passed") and row.get("replay_passed") and row.get("semantic_passed")):
                errors.append(f"B1 certificate report row {row.get('key')} has incomplete proof-log checks")
        if payload.get("exact_aggregate", {}).get("equivalence_failed") != 0:
            errors.append("B1 certificate report exact aggregate should have 0 equivalence failures")
        if not payload.get("claim_not_supported_yet"):
            errors.append("B1 certificate report must list unsupported claims to avoid overclaiming")
        if gates.get("routing_diagnostic", {}).get("passed") is not True:
            errors.append("B1 certificate report should include the line-routing diagnostic gate")
        if gates.get("routing_aware_calibrated_heavy_hex_baseline", {}).get("passed") is not False:
            errors.append("B1 certificate report must keep calibrated heavy-hex routing baseline open")
        if gates.get("heavyhex_topology_diagnostic", {}).get("passed") is not True:
            errors.append("B1 certificate report should include the heavy-hex topology diagnostic gate")
        if gates.get("heavyhex_end_to_end_routed_benefit", {}).get("passed") is not True:
            errors.append("B1 certificate report should include the heavy-hex end-to-end routed-benefit gate")
        if gates.get("post_routing_bottleneck_profile", {}).get("passed") is not True:
            errors.append("B1 certificate report should include the post-routing bottleneck profile gate")
        if gates.get("post_routing_swap_macro_compression", {}).get("passed") is not True:
            errors.append("B1 certificate report should include the post-routing SWAP macro gate")
        if gates.get("virtual_swap_elimination", {}).get("passed") is not True:
            errors.append("B1 certificate report should include the virtual SWAP elimination gate")
        ablation = payload.get("ablation", {})
        ablation_path = research / "B1_ablation_report.json"
        if not ablation_path.exists():
            errors.append(f"missing B1 ablation report: {ablation_path}")
        else:
            ablation_payload = json.loads(read(ablation_path))
            if ablation_payload.get("circuit_count") != payload.get("exact_aggregate", {}).get("circuit_count"):
                errors.append("B1 ablation circuit count differs from B1 certificate exact aggregate")
            if ablation_payload.get("interpretation", {}).get("largest_hardware_exposure_contributor") is None:
                errors.append("B1 ablation report missing largest hardware-exposure contributor")
        baseline_path = research / "B1_baseline_comparison.json"
        if not baseline_path.exists():
            errors.append(f"missing B1 baseline comparison report: {baseline_path}")
        else:
            baseline_payload = json.loads(read(baseline_path))
            best_valid = baseline_payload.get("best_valid_qiskit_by_exposure", {})
            if best_valid.get("equivalence_failed") != 0:
                errors.append("B1 baseline comparison best valid Qiskit row must have 0 equivalence failures")
            if not baseline_payload.get("baseline_suite", {}).get("valid_optimization_levels"):
                errors.append("B1 baseline comparison has no valid Qiskit levels")

    b2_manifest = yaml.safe_load(read(b2_manifest_path))
    b2_results = b2_manifest.get("current_results", {})
    b2_baseline = b2_results.get("repetition_code_memory_majority_baseline_v0")
    b2_target_volume = b2_results.get("repetition_code_target_volume_v0")
    b2_surface_estimate = b2_results.get("surface_code_threshold_law_estimate_v0")
    b2_decoder = b2_results.get("phenomenological_repetition_decoder_v0")
    b2_stim_surface = b2_results.get("stim_surface_code_memory_baseline_v0")
    b2_stim_target_volume = b2_results.get("stim_surface_code_target_volume_v0")
    b2_biased_schedule = b2_results.get("biased_schedule_target_volume_proxy_v0")
    b2_stim_biased_schedule = b2_results.get("stim_biased_schedule_circuit_sweep_v0")
    b2_same_hardware_schedule = b2_results.get("same_hardware_schedule_candidate_v0")
    b2_same_hardware_robustness = b2_results.get("same_hardware_schedule_robustness_v0")
    b2_reduced_round_boundary = b2_results.get("reduced_round_artifact_boundary_v0")
    b2_leakage_flagged_erasure = b2_results.get("leakage_flagged_erasure_boundary_v0")
    b2_stim_heralded_erasure = b2_results.get("stim_heralded_erasure_stress_v0")
    b2_false_positive_erasure = b2_results.get("heralded_erasure_false_positive_stress_v0")
    b2_shot_conditioned_erasure = b2_results.get("shot_conditioned_erasure_decoder_boundary_v0")
    b2_posterior_risk_ledger = b2_results.get("posterior_weighted_decoder_risk_ledger_v0")
    b2_decoder_input_contract = b2_results.get("decoder_input_contract_feasibility_gate_v0")
    b2_per_shot_trace_packet = b2_results.get("per_shot_decoder_trace_packet_v0")
    b2_posterior_injection_gate = b2_results.get(
        "posterior_likelihood_decoder_injection_gate_v0"
    )
    b2_dem_edge_semantics_gate = b2_results.get(
        "dem_informed_detector_edge_semantics_gate_v0"
    )
    b2_hardware_like_leakage_gate = b2_results.get(
        "hardware_like_leakage_model_gate_v0"
    )
    b2_status = {}
    if not b2_baseline:
        warnings.append("B2 manifest has no repetition-code control baseline result")
    else:
        result_path = b2_baseline.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B2 baseline result path missing: {result_path}")
        b2_status = {
            "status": b2_baseline.get("status"),
            "configurations": b2_baseline.get("configurations"),
            "shots_per_configuration": b2_baseline.get("shots_per_configuration"),
            "result_exists": result_exists,
            "result": result_path,
        }
    b2_target_status = {}
    if not b2_target_volume:
        warnings.append("B2 manifest has no target-volume result")
    else:
        result_path = b2_target_volume.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B2 target-volume result path missing: {result_path}")
        b2_target_status = {
            "status": b2_target_volume.get("status"),
            "target_combinations": b2_target_volume.get("target_combinations"),
            "met_count": b2_target_volume.get("met_count"),
            "unmet_count": b2_target_volume.get("unmet_count"),
            "result_exists": result_exists,
            "result": result_path,
        }
    b2_surface_status = {}
    if not b2_surface_estimate:
        warnings.append("B2 manifest has no surface-code threshold-law estimate")
    else:
        result_path = b2_surface_estimate.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B2 surface-code estimate result path missing: {result_path}")
        b2_surface_status = {
            "status": b2_surface_estimate.get("status"),
            "target_combinations": b2_surface_estimate.get("target_combinations"),
            "met_count": b2_surface_estimate.get("met_count"),
            "unmet_count": b2_surface_estimate.get("unmet_count"),
            "result_exists": result_exists,
            "result": result_path,
        }
    b2_decoder_status = {}
    if not b2_decoder:
        warnings.append("B2 manifest has no phenomenological decoder fallback")
    else:
        result_path = b2_decoder.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B2 phenomenological decoder result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b2_decoder_status = {
            "status": b2_decoder.get("status"),
            "configurations": b2_decoder.get("configurations"),
            "shots_per_configuration": b2_decoder.get("shots_per_configuration"),
            "improved_configurations": summary.get("improved_configurations"),
            "best_relative_reduction": summary.get("best_relative_reduction"),
            "max_decoder_runtime_seconds_per_shot": summary.get("max_decoder_runtime_seconds_per_shot"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "phenomenological_decoder_fallback_not_surface_code_claim":
            errors.append("B2 phenomenological decoder must remain marked as fallback, not surface-code claim")
        if summary.get("configuration_count") != b2_decoder.get("configurations"):
            errors.append("B2 phenomenological decoder configuration count mismatch")
        if summary.get("max_decoder_runtime_seconds_per_shot") is None:
            errors.append("B2 phenomenological decoder must report decoder runtime")
    b2_stim_surface_status = {}
    if not b2_stim_surface:
        warnings.append("B2 manifest has no Stim/PyMatching surface-code memory baseline")
    else:
        result_path = b2_stim_surface.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B2 Stim/PyMatching surface-code baseline result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b2_stim_surface_status = {
            "status": b2_stim_surface.get("status"),
            "configurations": b2_stim_surface.get("configurations"),
            "shots_per_configuration": b2_stim_surface.get("shots_per_configuration"),
            "total_shots": summary.get("total_shots"),
            "memory_bases": summary.get("memory_bases"),
            "distance_values": summary.get("distance_values"),
            "physical_error_rates": summary.get("physical_error_rates"),
            "nonincreasing_trend_count": summary.get("nonincreasing_trend_count"),
            "distance_trend_checks": len(summary.get("distance_trend_checks", [])),
            "max_decoder_runtime_seconds_per_shot": summary.get("max_decoder_runtime_seconds_per_shot"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "stim_pymatching_surface_code_memory_baseline":
            errors.append("B2 Stim/PyMatching surface-code result must remain marked as a baseline")
        if summary.get("configuration_count") != b2_stim_surface.get("configurations"):
            errors.append("B2 Stim/PyMatching surface-code configuration count mismatch")
        if summary.get("total_shots") != b2_stim_surface.get("total_shots"):
            errors.append("B2 Stim/PyMatching surface-code total-shot count mismatch")
        if summary.get("max_decoder_runtime_seconds_per_shot") is None:
            errors.append("B2 Stim/PyMatching surface-code baseline must report decoder runtime")
    b2_stim_target_status = {}
    if not b2_stim_target_volume:
        warnings.append("B2 manifest has no Stim surface-code target-volume table")
    else:
        result_path = b2_stim_target_volume.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B2 Stim surface-code target-volume result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b2_stim_target_status = {
            "status": b2_stim_target_volume.get("status"),
            "criterion": payload.get("criterion"),
            "target_combinations": payload.get("target_combinations"),
            "met_count": payload.get("met_count"),
            "unmet_count": payload.get("unmet_count"),
            "source_status": payload.get("source_status"),
            "source_shots_per_configuration": payload.get("source_shots_per_configuration"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "stim_surface_code_target_volume_baseline":
            errors.append("B2 Stim surface-code target-volume result must remain marked as a baseline")
        if payload.get("criterion") != b2_stim_target_volume.get("criterion"):
            errors.append("B2 Stim surface-code target-volume criterion mismatch")
        if payload.get("target_combinations") != b2_stim_target_volume.get("target_combinations"):
            errors.append("B2 Stim surface-code target-volume combination count mismatch")
        if payload.get("met_count") != b2_stim_target_volume.get("met_count"):
            errors.append("B2 Stim surface-code target-volume met_count mismatch")
        if payload.get("unmet_count") != b2_stim_target_volume.get("unmet_count"):
            errors.append("B2 Stim surface-code target-volume unmet_count mismatch")

    b2_biased_schedule_status = {}
    if not b2_biased_schedule:
        warnings.append("B2 manifest has no biased schedule proxy candidate comparison")
    else:
        result_path = b2_biased_schedule.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B2 biased schedule proxy result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b2_biased_schedule_status = {
            "status": b2_biased_schedule.get("status"),
            "method": b2_biased_schedule.get("method"),
            "criterion": payload.get("criterion"),
            "target_combinations": payload.get("target_combinations"),
            "baseline_met_count": payload.get("baseline_met_count"),
            "candidate_met_count": payload.get("candidate_met_count"),
            "candidate_only_meets_target_count": payload.get("candidate_only_meets_target_count"),
            "improved_volume_count": payload.get("improved_volume_count"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "biased_schedule_proxy_not_new_code_claim":
            errors.append("B2 biased schedule proxy must remain marked as a proxy, not a new-code claim")
        if payload.get("method") != b2_biased_schedule.get("method"):
            errors.append("B2 biased schedule proxy method mismatch")
        if payload.get("target_combinations") != b2_biased_schedule.get("target_combinations"):
            errors.append("B2 biased schedule proxy target combination count mismatch")
        if payload.get("candidate_met_count") != b2_biased_schedule.get("candidate_met_count"):
            errors.append("B2 biased schedule proxy candidate met count mismatch")
        if payload.get("candidate_only_meets_target_count") != b2_biased_schedule.get("candidate_only_meets_target_count"):
            errors.append("B2 biased schedule proxy candidate-only target count mismatch")
        if int(payload.get("candidate_met_count", 0)) <= int(payload.get("baseline_met_count", 0)):
            errors.append("B2 biased schedule proxy should improve target feasibility count over baseline")
        if int(payload.get("improved_volume_count", -1)) != 0:
            errors.append("B2 biased schedule proxy should not claim volume improvement in this diagnostic")

    b2_stim_biased_schedule_status = {}
    if not b2_stim_biased_schedule:
        warnings.append("B2 manifest has no Stim biased schedule circuit-level sweep")
    else:
        result_path = b2_stim_biased_schedule.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B2 Stim biased schedule sweep result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b2_stim_biased_schedule_status = {
            "status": b2_stim_biased_schedule.get("status"),
            "method": b2_stim_biased_schedule.get("method"),
            "criterion": payload.get("criterion"),
            "configurations": summary.get("configuration_count"),
            "total_shots": summary.get("total_shots"),
            "target_combinations": payload.get("target_combinations"),
            "baseline_met_count": payload.get("baseline_met_count"),
            "candidate_met_count": payload.get("candidate_met_count"),
            "candidate_only_meets_target_count": payload.get("candidate_only_meets_target_count"),
            "improved_volume_count": payload.get("improved_volume_count"),
            "max_decoder_runtime_seconds_per_shot": summary.get("max_decoder_runtime_seconds_per_shot"),
            "candidate_variants": payload.get("candidate_variants"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "stim_biased_schedule_circuit_sweep_not_new_code_claim":
            errors.append("B2 Stim biased schedule sweep must remain marked as a circuit sweep, not a new-code claim")
        if payload.get("method") != b2_stim_biased_schedule.get("method"):
            errors.append("B2 Stim biased schedule sweep method mismatch")
        if payload.get("target_combinations") != b2_stim_biased_schedule.get("target_combinations"):
            errors.append("B2 Stim biased schedule sweep target combination count mismatch")
        if summary.get("configuration_count") != b2_stim_biased_schedule.get("configurations"):
            errors.append("B2 Stim biased schedule sweep configuration count mismatch")
        if summary.get("total_shots") != b2_stim_biased_schedule.get("total_shots"):
            errors.append("B2 Stim biased schedule sweep total-shot count mismatch")
        if payload.get("candidate_met_count") != b2_stim_biased_schedule.get("candidate_met_count"):
            errors.append("B2 Stim biased schedule sweep candidate met count mismatch")
        if payload.get("candidate_only_meets_target_count") != b2_stim_biased_schedule.get("candidate_only_meets_target_count"):
            errors.append("B2 Stim biased schedule sweep candidate-only target count mismatch")
        if payload.get("improved_volume_count") != b2_stim_biased_schedule.get("improved_volume_count"):
            errors.append("B2 Stim biased schedule sweep volume-improvement count mismatch")
        if int(payload.get("candidate_met_count", 0)) <= int(payload.get("baseline_met_count", 0)):
            errors.append("B2 Stim biased schedule sweep should improve target feasibility count over baseline")
        if int(payload.get("improved_volume_count", -1)) != 0:
            errors.append("B2 Stim biased schedule sweep should not claim target-volume reduction yet")

    b2_same_hardware_status = {}
    if not b2_same_hardware_schedule:
        warnings.append("B2 manifest has no same-hardware schedule candidate")
    else:
        result_path = b2_same_hardware_schedule.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B2 same-hardware schedule candidate result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        contract = payload.get("same_hardware_contract", {})
        b2_same_hardware_status = {
            "status": b2_same_hardware_schedule.get("status"),
            "method": b2_same_hardware_schedule.get("method"),
            "criterion": payload.get("criterion"),
            "configurations": summary.get("configuration_count"),
            "total_shots": summary.get("total_shots"),
            "target_combinations": summary.get("target_combinations"),
            "baseline_met_count": summary.get("baseline_met_count"),
            "candidate_met_count": summary.get("candidate_met_count"),
            "candidate_only_meets_target_count": summary.get("candidate_only_meets_target_count"),
            "improved_volume_count": summary.get("improved_volume_count"),
            "max_volume_reduction": summary.get("max_volume_reduction"),
            "mean_volume_reduction_on_improved": summary.get("mean_volume_reduction_on_improved"),
            "max_decoder_runtime_seconds_per_shot": summary.get("max_decoder_runtime_seconds_per_shot"),
            "same_physical_qubits_per_distance": contract.get("same_physical_qubits_per_distance"),
            "volume_lever": contract.get("volume_lever"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "same_hardware_schedule_candidate_volume_positive_diagnostic_not_new_code_claim":
            errors.append("B2 same-hardware schedule candidate should remain a positive diagnostic, not a new-code claim")
        if payload.get("method") != b2_same_hardware_schedule.get("method"):
            errors.append("B2 same-hardware schedule candidate method mismatch")
        if payload.get("criterion") != b2_same_hardware_schedule.get("criterion"):
            errors.append("B2 same-hardware schedule candidate criterion mismatch")
        if summary.get("configuration_count") != b2_same_hardware_schedule.get("configurations"):
            errors.append("B2 same-hardware schedule candidate configuration count mismatch")
        if summary.get("total_shots") != b2_same_hardware_schedule.get("total_shots"):
            errors.append("B2 same-hardware schedule candidate total-shot count mismatch")
        if summary.get("target_combinations") != b2_same_hardware_schedule.get("target_combinations"):
            errors.append("B2 same-hardware schedule candidate target combination count mismatch")
        if summary.get("candidate_met_count") != b2_same_hardware_schedule.get("candidate_met_count"):
            errors.append("B2 same-hardware schedule candidate candidate met count mismatch")
        if summary.get("candidate_only_meets_target_count") != b2_same_hardware_schedule.get("candidate_only_meets_target_count"):
            errors.append("B2 same-hardware schedule candidate candidate-only count mismatch")
        if summary.get("improved_volume_count") != b2_same_hardware_schedule.get("improved_volume_count"):
            errors.append("B2 same-hardware schedule candidate improved-volume count mismatch")
        if float(summary.get("max_volume_reduction", 0.0)) != float(b2_same_hardware_schedule.get("max_volume_reduction", 0.0)):
            errors.append("B2 same-hardware schedule candidate max-volume reduction mismatch")
        if int(summary.get("improved_volume_count", 0)) < 1:
            errors.append("B2 same-hardware schedule candidate should show at least one Wilson target-volume improvement")
        if contract.get("same_physical_qubits_per_distance") is not True:
            errors.append("B2 same-hardware schedule candidate must keep physical qubits per distance fixed")
        if contract.get("volume_lever") != "reduced_syndrome_rounds_only":
            errors.append("B2 same-hardware schedule candidate volume lever must be reduced syndrome rounds")
        if claims.get("new_code_claimed") is not False:
            errors.append("B2 same-hardware schedule candidate must not claim a new code")
        if claims.get("threshold_claimed") is not False:
            errors.append("B2 same-hardware schedule candidate must not claim a threshold")
        if claims.get("calibrated_device_claimed") is not False:
            errors.append("B2 same-hardware schedule candidate must not claim calibrated device evidence")

    b2_same_hardware_robustness_status = {}
    if not b2_same_hardware_robustness:
        warnings.append("B2 manifest has no same-hardware schedule robustness stress result")
    else:
        result_path = b2_same_hardware_robustness.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B2 same-hardware schedule robustness result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        overall = payload.get("overall_summary", {})
        claims = payload.get("claim_boundary", {})
        contract = payload.get("same_hardware_contract", {})
        b2_same_hardware_robustness_status = {
            "status": b2_same_hardware_robustness.get("status"),
            "method": b2_same_hardware_robustness.get("method"),
            "criterion": payload.get("criterion"),
            "configurations": overall.get("configuration_count"),
            "total_shots": overall.get("total_shots"),
            "profile_count": overall.get("profile_count"),
            "target_comparisons": overall.get("target_comparisons"),
            "total_improved_volume_rows": overall.get("total_improved_volume_rows"),
            "total_non_aggressive_improved_volume_rows": overall.get("total_non_aggressive_improved_volume_rows"),
            "total_aggressive_improved_volume_rows": overall.get("total_aggressive_improved_volume_rows"),
            "robust_non_aggressive_volume_improvement_found": claims.get("robust_non_aggressive_volume_improvement_found"),
            "any_aggressive_volume_improvement_under_stress": claims.get("any_aggressive_volume_improvement_under_stress"),
            "positive_signal_depends_on_aggressive_schedule": claims.get("positive_signal_depends_on_aggressive_schedule"),
            "same_physical_qubits_per_distance": contract.get("same_physical_qubits_per_distance"),
            "volume_lever": contract.get("volume_lever"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != b2_same_hardware_robustness.get("status"):
            errors.append("B2 same-hardware schedule robustness status mismatch")
        if payload.get("method") != b2_same_hardware_robustness.get("method"):
            errors.append("B2 same-hardware schedule robustness method mismatch")
        if payload.get("criterion") != b2_same_hardware_robustness.get("criterion"):
            errors.append("B2 same-hardware schedule robustness criterion mismatch")
        if overall.get("configuration_count") != b2_same_hardware_robustness.get("configurations"):
            errors.append("B2 same-hardware schedule robustness configuration count mismatch")
        if overall.get("total_shots") != b2_same_hardware_robustness.get("total_shots"):
            errors.append("B2 same-hardware schedule robustness total-shot count mismatch")
        if overall.get("profile_count") != len(b2_same_hardware_robustness.get("stress_profiles", [])):
            errors.append("B2 same-hardware schedule robustness profile count mismatch")
        if overall.get("target_comparisons") != b2_same_hardware_robustness.get("target_comparisons"):
            errors.append("B2 same-hardware schedule robustness target comparison count mismatch")
        if overall.get("total_improved_volume_rows") != b2_same_hardware_robustness.get("total_improved_volume_rows"):
            errors.append("B2 same-hardware schedule robustness improved-volume count mismatch")
        if overall.get("total_non_aggressive_improved_volume_rows") != b2_same_hardware_robustness.get("total_non_aggressive_improved_volume_rows"):
            errors.append("B2 same-hardware schedule robustness non-aggressive count mismatch")
        if overall.get("total_aggressive_improved_volume_rows") != b2_same_hardware_robustness.get("total_aggressive_improved_volume_rows"):
            errors.append("B2 same-hardware schedule robustness aggressive count mismatch")
        if claims.get("robust_non_aggressive_volume_improvement_found") is not False:
            errors.append("B2 same-hardware schedule robustness must not claim robust non-aggressive volume improvement")
        if claims.get("any_aggressive_volume_improvement_under_stress") is not True:
            errors.append("B2 same-hardware schedule robustness should preserve only the aggressive stress signal")
        if claims.get("positive_signal_depends_on_aggressive_schedule") is not True:
            errors.append("B2 same-hardware schedule robustness must flag aggressive-only dependence")
        if contract.get("same_physical_qubits_per_distance") is not True:
            errors.append("B2 same-hardware schedule robustness must keep physical qubits per distance fixed")
        if contract.get("volume_lever") != "reduced_syndrome_rounds_only":
            errors.append("B2 same-hardware schedule robustness volume lever must remain reduced syndrome rounds")
        if claims.get("new_code_claimed") is not False:
            errors.append("B2 same-hardware schedule robustness must not claim a new code")
        if claims.get("threshold_claimed") is not False:
            errors.append("B2 same-hardware schedule robustness must not claim a threshold")
        if claims.get("calibrated_device_claimed") is not False:
            errors.append("B2 same-hardware schedule robustness must not claim calibrated device evidence")

    b2_reduced_round_boundary_status = {}
    if not b2_reduced_round_boundary:
        warnings.append("B2 manifest has no reduced-round artifact boundary")
    else:
        result_path = b2_reduced_round_boundary.get("result")
        markdown_path = b2_reduced_round_boundary.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 reduced-round artifact boundary result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 reduced-round artifact boundary markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        candidate_rows = payload.get("candidate_positive_rows", {})
        robustness_rows = payload.get("robustness_positive_rows", {})
        b2_reduced_round_boundary_status = {
            "status": b2_reduced_round_boundary.get("status"),
            "method": b2_reduced_round_boundary.get("method"),
            "criterion": payload.get("criterion"),
            "candidate_improved_volume_count": candidate_rows.get("improved_volume_count"),
            "robustness_improved_volume_count": robustness_rows.get("improved_volume_count"),
            "robustness_non_aggressive_improved_volume_count": robustness_rows.get(
                "non_aggressive_improved_volume_count"
            ),
            "all_robustness_improvements_aggressive": robustness_rows.get("all_improvements_are_aggressive"),
            "all_robustness_improvements_distance_3": robustness_rows.get("all_improvements_at_min_distance_3"),
            "all_robustness_improvements_one_round": robustness_rows.get("all_improvements_at_one_round"),
            "non_aggressive_mechanism_survives": payload.get("non_aggressive_mechanism_survives"),
            "small_distance_artifact_flag": payload.get("small_distance_artifact_flag"),
            "aggressive_schedule_dependency_flag": payload.get("aggressive_schedule_dependency_flag"),
            "new_code_claimed": payload.get("new_code_claimed"),
            "threshold_claimed": payload.get("threshold_claimed"),
            "calibrated_device_claimed": payload.get("calibrated_device_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "reduced_round_small_distance_aggressive_artifact_boundary":
            errors.append("B2 reduced-round artifact boundary status mismatch")
        if payload.get("method") != b2_reduced_round_boundary.get("method"):
            errors.append("B2 reduced-round artifact boundary method mismatch")
        if payload.get("criterion") != b2_reduced_round_boundary.get("criterion"):
            errors.append("B2 reduced-round artifact boundary criterion mismatch")
        if candidate_rows.get("improved_volume_count") != b2_reduced_round_boundary.get("candidate_improved_volume_count"):
            errors.append("B2 reduced-round artifact boundary candidate improved count mismatch")
        if robustness_rows.get("improved_volume_count") != b2_reduced_round_boundary.get(
            "robustness_improved_volume_count"
        ):
            errors.append("B2 reduced-round artifact boundary robustness improved count mismatch")
        if robustness_rows.get("non_aggressive_improved_volume_count") != b2_reduced_round_boundary.get(
            "robustness_non_aggressive_improved_volume_count"
        ):
            errors.append("B2 reduced-round artifact boundary non-aggressive count mismatch")
        if robustness_rows.get("all_improvements_are_aggressive") is not True:
            errors.append("B2 reduced-round artifact boundary should flag all improvements as aggressive")
        if robustness_rows.get("all_improvements_at_min_distance_3") is not True:
            errors.append("B2 reduced-round artifact boundary should flag all improvements at distance 3")
        if robustness_rows.get("all_improvements_at_one_round") is not True:
            errors.append("B2 reduced-round artifact boundary should flag all improvements as one-round candidates")
        if payload.get("non_aggressive_mechanism_survives") is not False:
            errors.append("B2 reduced-round artifact boundary must not claim a surviving non-aggressive mechanism")
        if payload.get("small_distance_artifact_flag") is not True:
            errors.append("B2 reduced-round artifact boundary must set small-distance artifact flag")
        if payload.get("aggressive_schedule_dependency_flag") is not True:
            errors.append("B2 reduced-round artifact boundary must set aggressive-schedule dependency flag")
        if payload.get("new_code_claimed") is not False:
            errors.append("B2 reduced-round artifact boundary must not claim a new code")
        if payload.get("threshold_claimed") is not False:
            errors.append("B2 reduced-round artifact boundary must not claim a threshold")
        if payload.get("calibrated_device_claimed") is not False:
            errors.append("B2 reduced-round artifact boundary must not claim calibrated device evidence")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B2 reduced-round artifact boundary validation errors must be zero")

    b2_leakage_flagged_erasure_status = {}
    if not b2_leakage_flagged_erasure:
        warnings.append("B2 manifest has no leakage-flagged erasure boundary")
    else:
        result_path = b2_leakage_flagged_erasure.get("result")
        markdown_path = b2_leakage_flagged_erasure.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 leakage-flagged erasure boundary result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 leakage-flagged erasure boundary markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        b2_leakage_flagged_erasure_status = {
            "status": b2_leakage_flagged_erasure.get("status"),
            "method": b2_leakage_flagged_erasure.get("method"),
            "model_status": payload.get("model_status"),
            "configuration_count": summary.get("configuration_count"),
            "baseline_met_count": summary.get("baseline_met_count"),
            "candidate_met_count": summary.get("candidate_met_count"),
            "improved_volume_count": summary.get("improved_volume_count"),
            "distance_5_7_improved_count": summary.get("distance_5_7_improved_count"),
            "high_efficiency_distance_5_7_improved_count": summary.get(
                "high_efficiency_distance_5_7_improved_count"
            ),
            "max_volume_reduction": summary.get("max_volume_reduction"),
            "mean_volume_reduction_on_improved": summary.get("mean_volume_reduction_on_improved"),
            "minimum_detection_efficiency_with_improvement": summary.get(
                "minimum_detection_efficiency_with_improvement"
            ),
            "non_aggressive_mechanism": claims.get("non_aggressive_mechanism"),
            "reduced_rounds_used": claims.get("reduced_rounds_used"),
            "distance_3_candidate_used": claims.get("distance_3_candidate_used"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "circuit_level_decoder_claimed": claims.get("circuit_level_decoder_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b2_leakage_flagged_erasure.get("status"):
            errors.append("B2 leakage-flagged erasure boundary status mismatch")
        if payload.get("method") != b2_leakage_flagged_erasure.get("method"):
            errors.append("B2 leakage-flagged erasure boundary method mismatch")
        if payload.get("model_status") != b2_leakage_flagged_erasure.get("model_status"):
            errors.append("B2 leakage-flagged erasure boundary model-status mismatch")
        if summary.get("configuration_count") != b2_leakage_flagged_erasure.get("configurations"):
            errors.append("B2 leakage-flagged erasure boundary configuration count mismatch")
        if summary.get("candidate_met_count") != b2_leakage_flagged_erasure.get("candidate_met_count"):
            errors.append("B2 leakage-flagged erasure boundary candidate met count mismatch")
        if summary.get("improved_volume_count") != b2_leakage_flagged_erasure.get("improved_volume_count"):
            errors.append("B2 leakage-flagged erasure boundary improved-volume count mismatch")
        if summary.get("distance_5_7_improved_count") != b2_leakage_flagged_erasure.get(
            "distance_5_7_improved_count"
        ):
            errors.append("B2 leakage-flagged erasure boundary d5/d7 count mismatch")
        if int(summary.get("improved_volume_count", 0)) < 1:
            errors.append("B2 leakage-flagged erasure boundary should show at least one proxy volume improvement")
        if int(summary.get("distance_5_7_improved_count", 0)) < 1:
            errors.append("B2 leakage-flagged erasure boundary should include distance-5/7 improvements")
        if claims.get("non_aggressive_mechanism") is not True:
            errors.append("B2 leakage-flagged erasure boundary must be marked non-aggressive")
        if claims.get("reduced_rounds_used") is not False:
            errors.append("B2 leakage-flagged erasure boundary must not use reduced rounds")
        if claims.get("distance_3_candidate_used") is not False:
            errors.append("B2 leakage-flagged erasure boundary must not use distance-3 candidates")
        if claims.get("new_code_claimed") is not False:
            errors.append("B2 leakage-flagged erasure boundary must not claim a new code")
        if claims.get("threshold_claimed") is not False:
            errors.append("B2 leakage-flagged erasure boundary must not claim a threshold")
        if claims.get("calibrated_device_claimed") is not False:
            errors.append("B2 leakage-flagged erasure boundary must not claim calibrated device evidence")
        if claims.get("circuit_level_decoder_claimed") is not False:
            errors.append("B2 leakage-flagged erasure boundary must not claim circuit-level decoder evidence")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B2 leakage-flagged erasure boundary validation errors must be zero")

    b2_stim_heralded_erasure_status = {}
    if not b2_stim_heralded_erasure:
        warnings.append("B2 manifest has no Stim heralded-erasure stress result")
    else:
        result_path = b2_stim_heralded_erasure.get("result")
        markdown_path = b2_stim_heralded_erasure.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 Stim heralded-erasure stress result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 Stim heralded-erasure stress markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        b2_stim_heralded_erasure_status = {
            "status": b2_stim_heralded_erasure.get("status"),
            "method": b2_stim_heralded_erasure.get("method"),
            "model_status": payload.get("model_status"),
            "toolchain": payload.get("toolchain"),
            "configuration_count": summary.get("configuration_count"),
            "total_shots": summary.get("total_shots"),
            "target_comparisons": summary.get("target_comparisons"),
            "baseline_met_count": summary.get("baseline_met_count"),
            "candidate_met_count": summary.get("candidate_met_count"),
            "candidate_only_meets_target_count": summary.get("candidate_only_meets_target_count"),
            "improved_volume_count": summary.get("improved_volume_count"),
            "distance_5_7_improved_count": summary.get("distance_5_7_improved_count"),
            "max_volume_reduction": summary.get("max_volume_reduction"),
            "mean_volume_reduction_on_improved": summary.get("mean_volume_reduction_on_improved"),
            "reduced_rounds_used": claims.get("reduced_rounds_used"),
            "distance_3_candidate_used": claims.get("distance_3_candidate_used"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "full_physical_leakage_decoder_claimed": claims.get("full_physical_leakage_decoder_claimed"),
            "shot_conditioned_erasure_decoder_claimed": claims.get("shot_conditioned_erasure_decoder_claimed"),
            "circuit_derived_stim_evidence": claims.get("circuit_derived_stim_evidence"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b2_stim_heralded_erasure.get("status"):
            errors.append("B2 Stim heralded-erasure stress status mismatch")
        if payload.get("method") != b2_stim_heralded_erasure.get("method"):
            errors.append("B2 Stim heralded-erasure stress method mismatch")
        if payload.get("model_status") != b2_stim_heralded_erasure.get("model_status"):
            errors.append("B2 Stim heralded-erasure stress model-status mismatch")
        if summary.get("configuration_count") != b2_stim_heralded_erasure.get("configurations"):
            errors.append("B2 Stim heralded-erasure stress configuration count mismatch")
        if summary.get("total_shots") != b2_stim_heralded_erasure.get("total_shots"):
            errors.append("B2 Stim heralded-erasure stress total-shot count mismatch")
        if summary.get("target_comparisons") != b2_stim_heralded_erasure.get("target_comparisons"):
            errors.append("B2 Stim heralded-erasure stress target comparison count mismatch")
        if summary.get("candidate_met_count") != b2_stim_heralded_erasure.get("candidate_met_count"):
            errors.append("B2 Stim heralded-erasure stress candidate met count mismatch")
        if summary.get("improved_volume_count") != b2_stim_heralded_erasure.get("improved_volume_count"):
            errors.append("B2 Stim heralded-erasure stress improved-volume count mismatch")
        if summary.get("distance_5_7_improved_count") != b2_stim_heralded_erasure.get(
            "distance_5_7_improved_count"
        ):
            errors.append("B2 Stim heralded-erasure stress d5/d7 count mismatch")
        if int(summary.get("improved_volume_count", 0)) < 1:
            errors.append("B2 Stim heralded-erasure stress should show at least one volume improvement")
        if int(summary.get("distance_5_7_improved_count", 0)) < 1:
            errors.append("B2 Stim heralded-erasure stress should include distance-5/7 improvements")
        if claims.get("circuit_derived_stim_evidence") is not True:
            errors.append("B2 Stim heralded-erasure stress must be marked as circuit-derived Stim evidence")
        if claims.get("reduced_rounds_used") is not False:
            errors.append("B2 Stim heralded-erasure stress must not use reduced rounds")
        if claims.get("distance_3_candidate_used") is not False:
            errors.append("B2 Stim heralded-erasure stress must not use distance-3 candidates")
        if claims.get("new_code_claimed") is not False:
            errors.append("B2 Stim heralded-erasure stress must not claim a new code")
        if claims.get("threshold_claimed") is not False:
            errors.append("B2 Stim heralded-erasure stress must not claim a threshold")
        if claims.get("calibrated_device_claimed") is not False:
            errors.append("B2 Stim heralded-erasure stress must not claim calibrated device evidence")
        if claims.get("full_physical_leakage_decoder_claimed") is not False:
            errors.append("B2 Stim heralded-erasure stress must not claim a full physical leakage decoder")
        if claims.get("shot_conditioned_erasure_decoder_claimed") is not False:
            errors.append("B2 Stim heralded-erasure stress must not claim a shot-conditioned erasure decoder")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B2 Stim heralded-erasure stress validation errors must be zero")

    b2_false_positive_erasure_status = {}
    if not b2_false_positive_erasure:
        warnings.append("B2 manifest has no heralded-erasure false-positive stress result")
    else:
        result_path = b2_false_positive_erasure.get("result")
        markdown_path = b2_false_positive_erasure.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 heralded-erasure false-positive stress result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 heralded-erasure false-positive stress markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        fp_breakdown = summary.get("by_false_positive_rate", {})
        b2_false_positive_erasure_status = {
            "status": b2_false_positive_erasure.get("status"),
            "method": b2_false_positive_erasure.get("method"),
            "model_status": payload.get("model_status"),
            "configuration_count": summary.get("configuration_count"),
            "total_shots": summary.get("total_shots"),
            "target_comparisons": summary.get("target_comparisons"),
            "candidate_met_count": summary.get("candidate_met_count"),
            "improved_volume_count": summary.get("improved_volume_count"),
            "false_positive_positive_improved_volume_count": summary.get(
                "false_positive_positive_improved_volume_count"
            ),
            "false_positive_positive_d5_d7_improved_count": summary.get(
                "false_positive_positive_d5_d7_improved_count"
            ),
            "false_positive_rates_per_tick": summary.get("false_positive_rates_per_tick"),
            "fp_0p001_improved_volume_count": fp_breakdown.get("0.001", {}).get("improved_volume_count"),
            "fp_0p003_improved_volume_count": fp_breakdown.get("0.003", {}).get("improved_volume_count"),
            "max_volume_reduction": summary.get("max_volume_reduction"),
            "mean_volume_reduction_on_improved": summary.get("mean_volume_reduction_on_improved"),
            "reduced_rounds_used": claims.get("reduced_rounds_used"),
            "distance_3_candidate_used": claims.get("distance_3_candidate_used"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "full_physical_leakage_decoder_claimed": claims.get("full_physical_leakage_decoder_claimed"),
            "shot_conditioned_erasure_decoder_claimed": claims.get("shot_conditioned_erasure_decoder_claimed"),
            "false_positive_overhead_stress_performed": claims.get("false_positive_overhead_stress_performed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b2_false_positive_erasure.get("status"):
            errors.append("B2 heralded-erasure false-positive stress status mismatch")
        if payload.get("method") != b2_false_positive_erasure.get("method"):
            errors.append("B2 heralded-erasure false-positive stress method mismatch")
        if payload.get("model_status") != b2_false_positive_erasure.get("model_status"):
            errors.append("B2 heralded-erasure false-positive stress model-status mismatch")
        if summary.get("configuration_count") != b2_false_positive_erasure.get("configurations"):
            errors.append("B2 heralded-erasure false-positive stress configuration count mismatch")
        if summary.get("total_shots") != b2_false_positive_erasure.get("total_shots"):
            errors.append("B2 heralded-erasure false-positive stress total-shot count mismatch")
        if summary.get("target_comparisons") != b2_false_positive_erasure.get("target_comparisons"):
            errors.append("B2 heralded-erasure false-positive stress target comparison count mismatch")
        if summary.get("candidate_met_count") != b2_false_positive_erasure.get("candidate_met_count"):
            errors.append("B2 heralded-erasure false-positive stress candidate met count mismatch")
        if summary.get("improved_volume_count") != b2_false_positive_erasure.get("improved_volume_count"):
            errors.append("B2 heralded-erasure false-positive stress improved-volume count mismatch")
        if summary.get("false_positive_positive_improved_volume_count") != b2_false_positive_erasure.get(
            "false_positive_positive_improved_volume_count"
        ):
            errors.append("B2 heralded-erasure false-positive positive-improved count mismatch")
        if summary.get("false_positive_positive_d5_d7_improved_count") != b2_false_positive_erasure.get(
            "false_positive_positive_d5_d7_improved_count"
        ):
            errors.append("B2 heralded-erasure false-positive positive d5/d7 count mismatch")
        if int(summary.get("false_positive_positive_improved_volume_count", 0)) < 1:
            errors.append("B2 heralded-erasure false-positive stress should preserve some positive-fp rows")
        if int(summary.get("false_positive_positive_d5_d7_improved_count", 0)) < 1:
            errors.append("B2 heralded-erasure false-positive stress should preserve positive-fp d5/d7 rows")
        if fp_breakdown.get("0.001", {}).get("improved_volume_count") != 5:
            errors.append("B2 false-positive stress expected five improved rows at fp=0.001")
        if fp_breakdown.get("0.003", {}).get("improved_volume_count") != 0:
            errors.append("B2 false-positive stress expected zero improved rows at fp=0.003")
        if claims.get("false_positive_overhead_stress_performed") is not True:
            errors.append("B2 false-positive stress must disclose false-positive overhead stress")
        if claims.get("reduced_rounds_used") is not False:
            errors.append("B2 false-positive stress must not use reduced rounds")
        if claims.get("distance_3_candidate_used") is not False:
            errors.append("B2 false-positive stress must not use distance-3 candidates")
        if claims.get("new_code_claimed") is not False:
            errors.append("B2 false-positive stress must not claim a new code")
        if claims.get("threshold_claimed") is not False:
            errors.append("B2 false-positive stress must not claim a threshold")
        if claims.get("calibrated_device_claimed") is not False:
            errors.append("B2 false-positive stress must not claim calibrated device evidence")
        if claims.get("full_physical_leakage_decoder_claimed") is not False:
            errors.append("B2 false-positive stress must not claim a full physical leakage decoder")
        if claims.get("shot_conditioned_erasure_decoder_claimed") is not False:
            errors.append("B2 false-positive stress must not claim a shot-conditioned erasure decoder")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B2 false-positive stress validation errors must be zero")

    b2_shot_conditioned_erasure_status = {}
    if not b2_shot_conditioned_erasure:
        warnings.append("B2 manifest has no shot-conditioned erasure decoder boundary result")
    else:
        result_path = b2_shot_conditioned_erasure.get("result")
        markdown_path = b2_shot_conditioned_erasure.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 shot-conditioned erasure boundary result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 shot-conditioned erasure boundary markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        b2_shot_conditioned_erasure_status = {
            "status": b2_shot_conditioned_erasure.get("status"),
            "method": b2_shot_conditioned_erasure.get("method"),
            "model_status": payload.get("model_status"),
            "source_target_comparisons": summary.get("source_target_comparisons"),
            "source_positive_fp_d5_d7_improved_rows": summary.get(
                "source_positive_fp_d5_d7_improved_rows"
            ),
            "calibration_profile_count": summary.get("calibration_profile_count"),
            "evaluated_profile_rows": summary.get("evaluated_profile_rows"),
            "profiles_with_surviving_rows": summary.get("profiles_with_surviving_rows"),
            "max_surviving_d5_d7_improved_rows_in_profile": summary.get(
                "max_surviving_d5_d7_improved_rows_in_profile"
            ),
            "strict_high_purity_surviving_rows": summary.get("strict_high_purity_surviving_rows"),
            "robust_all_profile_survival": summary.get("robust_all_profile_survival"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "full_physical_leakage_decoder_claimed": claims.get("full_physical_leakage_decoder_claimed"),
            "production_decoder_claimed": claims.get("production_decoder_claimed"),
            "shot_conditioned_calibration_model_performed": claims.get(
                "shot_conditioned_calibration_model_performed"
            ),
            "shot_conditioned_erasure_decoder_claimed": claims.get(
                "shot_conditioned_erasure_decoder_claimed"
            ),
            "hardware_result_claimed": claims.get("hardware_result_claimed"),
            "reduced_rounds_used": claims.get("reduced_rounds_used"),
            "distance_3_candidate_used": claims.get("distance_3_candidate_used"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b2_shot_conditioned_erasure.get("status"):
            errors.append("B2 shot-conditioned erasure boundary status mismatch")
        if payload.get("method") != b2_shot_conditioned_erasure.get("method"):
            errors.append("B2 shot-conditioned erasure boundary method mismatch")
        if payload.get("model_status") != b2_shot_conditioned_erasure.get("model_status"):
            errors.append("B2 shot-conditioned erasure boundary model-status mismatch")
        for key in [
            "source_target_comparisons",
            "source_positive_fp_d5_d7_improved_rows",
            "calibration_profile_count",
            "evaluated_profile_rows",
            "profiles_with_surviving_rows",
            "max_surviving_d5_d7_improved_rows_in_profile",
            "strict_high_purity_surviving_rows",
            "robust_all_profile_survival",
        ]:
            if summary.get(key) != b2_shot_conditioned_erasure.get(key):
                errors.append(f"B2 shot-conditioned erasure boundary {key} mismatch")
        if int(summary.get("source_positive_fp_d5_d7_improved_rows", 0)) != 5:
            errors.append("B2 shot-conditioned boundary expected five source positive-fp d5/d7 rows")
        if int(summary.get("max_surviving_d5_d7_improved_rows_in_profile", 0)) != 4:
            errors.append("B2 shot-conditioned boundary expected four max surviving rows")
        if summary.get("robust_all_profile_survival") is not False:
            errors.append("B2 shot-conditioned boundary must not claim robust all-profile survival")
        if claims.get("shot_conditioned_calibration_model_performed") is not True:
            errors.append("B2 shot-conditioned boundary must disclose calibration modeling")
        for key in [
            "new_code_claimed",
            "threshold_claimed",
            "calibrated_device_claimed",
            "full_physical_leakage_decoder_claimed",
            "production_decoder_claimed",
            "shot_conditioned_erasure_decoder_claimed",
            "hardware_result_claimed",
            "reduced_rounds_used",
            "distance_3_candidate_used",
        ]:
            if claims.get(key) is not False:
                errors.append(f"B2 shot-conditioned boundary must keep {key}=False")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B2 shot-conditioned boundary validation errors must be zero")

    b2_posterior_risk_ledger_status = {}
    if not b2_posterior_risk_ledger:
        warnings.append("B2 manifest has no posterior-weighted decoder-risk ledger result")
    else:
        result_path = b2_posterior_risk_ledger.get("result")
        markdown_path = b2_posterior_risk_ledger.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 posterior-risk ledger result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 posterior-risk ledger markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        b2_posterior_risk_ledger_status = {
            "status": b2_posterior_risk_ledger.get("status"),
            "method": b2_posterior_risk_ledger.get("method"),
            "model_status": payload.get("model_status"),
            "risk_budget_count": summary.get("risk_budget_count"),
            "evaluated_budget_profile_rows": summary.get("evaluated_budget_profile_rows"),
            "source_raw_surviving_d5_d7_rows": summary.get("source_raw_surviving_d5_d7_rows"),
            "mild_adjusted_surviving_d5_d7_rows": summary.get("mild_adjusted_surviving_d5_d7_rows"),
            "nominal_adjusted_surviving_d5_d7_rows": summary.get("nominal_adjusted_surviving_d5_d7_rows"),
            "conservative_adjusted_surviving_d5_d7_rows": summary.get(
                "conservative_adjusted_surviving_d5_d7_rows"
            ),
            "strict_adjusted_surviving_d5_d7_rows": summary.get("strict_adjusted_surviving_d5_d7_rows"),
            "strict_high_purity_adjusted_survivors": summary.get(
                "strict_high_purity_adjusted_survivors"
            ),
            "robust_all_profile_adjusted_survival": summary.get(
                "robust_all_profile_adjusted_survival"
            ),
            "conservative_max_decoder_adjusted_reduction": summary.get(
                "conservative_max_decoder_adjusted_reduction"
            ),
            "strict_max_decoder_adjusted_reduction": summary.get("strict_max_decoder_adjusted_reduction"),
            "posterior_weighted_decoder_risk_model_performed": claims.get(
                "posterior_weighted_decoder_risk_model_performed"
            ),
            "new_code_claimed": claims.get("new_code_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "full_physical_leakage_decoder_claimed": claims.get("full_physical_leakage_decoder_claimed"),
            "production_decoder_claimed": claims.get("production_decoder_claimed"),
            "circuit_level_decoder_claimed": claims.get("circuit_level_decoder_claimed"),
            "shot_conditioned_erasure_decoder_claimed": claims.get(
                "shot_conditioned_erasure_decoder_claimed"
            ),
            "hardware_result_claimed": claims.get("hardware_result_claimed"),
            "reduced_rounds_used": claims.get("reduced_rounds_used"),
            "distance_3_candidate_used": claims.get("distance_3_candidate_used"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b2_posterior_risk_ledger.get("status"):
            errors.append("B2 posterior-risk ledger status mismatch")
        if payload.get("method") != b2_posterior_risk_ledger.get("method"):
            errors.append("B2 posterior-risk ledger method mismatch")
        if payload.get("model_status") != b2_posterior_risk_ledger.get("model_status"):
            errors.append("B2 posterior-risk ledger model-status mismatch")
        for key in [
            "risk_budget_count",
            "evaluated_budget_profile_rows",
            "source_raw_surviving_d5_d7_rows",
            "mild_adjusted_surviving_d5_d7_rows",
            "nominal_adjusted_surviving_d5_d7_rows",
            "conservative_adjusted_surviving_d5_d7_rows",
            "strict_adjusted_surviving_d5_d7_rows",
            "strict_high_purity_adjusted_survivors",
            "robust_all_profile_adjusted_survival",
            "conservative_max_decoder_adjusted_reduction",
            "strict_max_decoder_adjusted_reduction",
        ]:
            if summary.get(key) != b2_posterior_risk_ledger.get(key):
                errors.append(f"B2 posterior-risk ledger {key} mismatch")
        if int(summary.get("conservative_adjusted_surviving_d5_d7_rows", 0)) >= int(
            summary.get("source_raw_surviving_d5_d7_rows", 0)
        ):
            errors.append("B2 posterior-risk ledger must shrink survivors under conservative risk")
        if summary.get("strict_high_purity_adjusted_survivors") != 0:
            errors.append("B2 posterior-risk ledger strict high-purity survivors must be zero")
        if summary.get("robust_all_profile_adjusted_survival") is not False:
            errors.append("B2 posterior-risk ledger must not claim all-profile survival")
        if claims.get("posterior_weighted_decoder_risk_model_performed") is not True:
            errors.append("B2 posterior-risk ledger must disclose posterior risk modeling")
        for key in [
            "new_code_claimed",
            "threshold_claimed",
            "calibrated_device_claimed",
            "full_physical_leakage_decoder_claimed",
            "production_decoder_claimed",
            "circuit_level_decoder_claimed",
            "shot_conditioned_erasure_decoder_claimed",
            "hardware_result_claimed",
            "reduced_rounds_used",
            "distance_3_candidate_used",
        ]:
            if claims.get(key) is not False:
                errors.append(f"B2 posterior-risk ledger must keep {key}=False")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B2 posterior-risk ledger validation errors must be zero")

    b2_decoder_input_contract_status = {}
    if not b2_decoder_input_contract:
        warnings.append("B2 manifest has no decoder input contract feasibility gate result")
    else:
        result_path = b2_decoder_input_contract.get("result")
        markdown_path = b2_decoder_input_contract.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 decoder input contract result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 decoder input contract markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        b2_decoder_input_contract_status = {
            "status": b2_decoder_input_contract.get("status"),
            "method": b2_decoder_input_contract.get("method"),
            "model_status": payload.get("model_status"),
            "contract_input_count": summary.get("contract_input_count"),
            "available_contract_input_count": summary.get("available_contract_input_count"),
            "missing_contract_input_count": summary.get("missing_contract_input_count"),
            "feasibility_gate_count": summary.get("feasibility_gate_count"),
            "passed_gate_count": summary.get("passed_gate_count"),
            "failed_gate_count": summary.get("failed_gate_count"),
            "failed_critical_gate_count": summary.get("failed_critical_gate_count"),
            "source_raw_surviving_d5_d7_rows": summary.get("source_raw_surviving_d5_d7_rows"),
            "conservative_adjusted_surviving_d5_d7_rows": summary.get(
                "conservative_adjusted_surviving_d5_d7_rows"
            ),
            "strict_adjusted_surviving_d5_d7_rows": summary.get(
                "strict_adjusted_surviving_d5_d7_rows"
            ),
            "strict_high_purity_adjusted_survivors": summary.get(
                "strict_high_purity_adjusted_survivors"
            ),
            "robust_all_profile_adjusted_survival": summary.get(
                "robust_all_profile_adjusted_survival"
            ),
            "decoder_contract_satisfied": summary.get("decoder_contract_satisfied"),
            "demotion_recommended_until_decoder_or_calibration": summary.get(
                "demotion_recommended_until_decoder_or_calibration"
            ),
            "circuit_level_decoder_claimed": claims.get("circuit_level_decoder_claimed"),
            "shot_conditioned_erasure_decoder_claimed": claims.get(
                "shot_conditioned_erasure_decoder_claimed"
            ),
            "production_decoder_claimed": claims.get("production_decoder_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "hardware_result_claimed": claims.get("hardware_result_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b2_decoder_input_contract.get("status"):
            errors.append("B2 decoder input contract status mismatch")
        if payload.get("method") != b2_decoder_input_contract.get("method"):
            errors.append("B2 decoder input contract method mismatch")
        if payload.get("model_status") != b2_decoder_input_contract.get("model_status"):
            errors.append("B2 decoder input contract model-status mismatch")
        for key in [
            "contract_input_count",
            "available_contract_input_count",
            "missing_contract_input_count",
            "feasibility_gate_count",
            "passed_gate_count",
            "failed_gate_count",
            "failed_critical_gate_count",
            "source_raw_surviving_d5_d7_rows",
            "conservative_adjusted_surviving_d5_d7_rows",
            "strict_adjusted_surviving_d5_d7_rows",
            "strict_high_purity_adjusted_survivors",
            "robust_all_profile_adjusted_survival",
            "decoder_contract_satisfied",
            "demotion_recommended_until_decoder_or_calibration",
        ]:
            if summary.get(key) != b2_decoder_input_contract.get(key):
                errors.append(f"B2 decoder input contract {key} mismatch")
        if summary.get("contract_input_count") != 10:
            errors.append("B2 decoder input contract must track ten decoder inputs")
        if summary.get("available_contract_input_count") != 4:
            errors.append("B2 decoder input contract should have four currently available inputs")
        if summary.get("missing_contract_input_count") != 6:
            errors.append("B2 decoder input contract should have six missing inputs")
        if summary.get("failed_critical_gate_count") < 5:
            errors.append("B2 decoder input contract should fail at least five critical gates")
        if summary.get("strict_high_purity_adjusted_survivors") != 0:
            errors.append("B2 decoder input contract strict high-purity survivors must be zero")
        if summary.get("robust_all_profile_adjusted_survival") is not False:
            errors.append("B2 decoder input contract must not claim all-profile survival")
        if summary.get("decoder_contract_satisfied") is not False:
            errors.append("B2 decoder input contract must not be marked satisfied")
        if summary.get("demotion_recommended_until_decoder_or_calibration") is not True:
            errors.append("B2 decoder input contract must recommend demotion until decoder or calibration")
        if len(payload.get("decoder_contract_inputs", [])) != summary.get("contract_input_count"):
            errors.append("B2 decoder input contract input count mismatch")
        if len(payload.get("feasibility_gates", [])) != summary.get("feasibility_gate_count"):
            errors.append("B2 decoder input contract feasibility gate count mismatch")
        if not any(
            row.get("input") == "per_shot_syndrome_bitstrings" and row.get("available") is False
            for row in payload.get("decoder_contract_inputs", [])
        ):
            errors.append("B2 decoder input contract must record missing per-shot syndrome bitstrings")
        if not any(
            row.get("critical") is True and row.get("passed") is False
            for row in payload.get("feasibility_gates", [])
        ):
            errors.append("B2 decoder input contract must have failed critical gates")
        if claims.get("decoder_input_contract_built") is not True:
            errors.append("B2 decoder input contract claim boundary must disclose contract construction")
        if claims.get("demotion_recommended_until_decoder_or_calibration") is not True:
            errors.append("B2 decoder input contract claim boundary must recommend demotion")
        for key in [
            "circuit_level_decoder_claimed",
            "shot_conditioned_erasure_decoder_claimed",
            "production_decoder_claimed",
            "threshold_claimed",
            "new_code_claimed",
            "hardware_result_claimed",
            "calibrated_device_claimed",
        ]:
            if claims.get(key) is not False:
                errors.append(f"B2 decoder input contract must keep {key}=False")

    b2_per_shot_trace_packet_status = {}
    if not b2_per_shot_trace_packet:
        warnings.append("B2 manifest has no per-shot decoder trace packet result")
    else:
        result_path = b2_per_shot_trace_packet.get("result")
        markdown_path = b2_per_shot_trace_packet.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 per-shot trace packet result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 per-shot trace packet markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        b2_per_shot_trace_packet_status = {
            "status": b2_per_shot_trace_packet.get("status"),
            "method": b2_per_shot_trace_packet.get("method"),
            "model_status": payload.get("model_status"),
            "challenge_count": summary.get("challenge_count"),
            "shots_per_challenge": summary.get("shots_per_challenge"),
            "total_shot_traces": summary.get("total_shot_traces"),
            "total_logical_failures": summary.get("total_logical_failures"),
            "max_detector_count": summary.get("max_detector_count"),
            "total_synthetic_flag_events": summary.get("total_synthetic_flag_events"),
            "mean_synthetic_flag_events_per_shot": summary.get(
                "mean_synthetic_flag_events_per_shot"
            ),
            "max_decoder_runtime_seconds_per_shot": summary.get(
                "max_decoder_runtime_seconds_per_shot"
            ),
            "per_shot_detector_bitstrings_persisted": summary.get(
                "per_shot_detector_bitstrings_persisted"
            ),
            "stim_observable_bitstrings_persisted": summary.get(
                "stim_observable_bitstrings_persisted"
            ),
            "synthetic_detector_tick_flag_events_persisted": summary.get(
                "synthetic_detector_tick_flag_events_persisted"
            ),
            "real_hardware_or_calibrated_flag_events": summary.get(
                "real_hardware_or_calibrated_flag_events"
            ),
            "posterior_likelihood_decoder_injection_performed": summary.get(
                "posterior_likelihood_decoder_injection_performed"
            ),
            "per_shot_trace_packet_built": claims.get("per_shot_trace_packet_built"),
            "circuit_level_decoder_claimed": claims.get("circuit_level_decoder_claimed"),
            "posterior_likelihood_decoder_claimed": claims.get(
                "posterior_likelihood_decoder_claimed"
            ),
            "production_decoder_claimed": claims.get("production_decoder_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "hardware_result_claimed": claims.get("hardware_result_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b2_per_shot_trace_packet.get("status"):
            errors.append("B2 per-shot trace packet status mismatch")
        if payload.get("method") != b2_per_shot_trace_packet.get("method"):
            errors.append("B2 per-shot trace packet method mismatch")
        if payload.get("model_status") != b2_per_shot_trace_packet.get("model_status"):
            errors.append("B2 per-shot trace packet model-status mismatch")
        for key in [
            "challenge_count",
            "shots_per_challenge",
            "total_shot_traces",
            "total_logical_failures",
            "max_detector_count",
            "total_synthetic_flag_events",
            "mean_synthetic_flag_events_per_shot",
            "max_decoder_runtime_seconds_per_shot",
            "per_shot_detector_bitstrings_persisted",
            "stim_observable_bitstrings_persisted",
            "synthetic_detector_tick_flag_events_persisted",
            "real_hardware_or_calibrated_flag_events",
            "posterior_likelihood_decoder_injection_performed",
        ]:
            if summary.get(key) != b2_per_shot_trace_packet.get(key):
                errors.append(f"B2 per-shot trace packet {key} mismatch")
        if summary.get("challenge_count") != 3:
            errors.append("B2 per-shot trace packet should include three strict challenge rows")
        if summary.get("shots_per_challenge") != 192:
            errors.append("B2 per-shot trace packet should use 192 shots per challenge")
        if summary.get("total_shot_traces") != 576:
            errors.append("B2 per-shot trace packet should persist 576 shot traces")
        if summary.get("per_shot_detector_bitstrings_persisted") is not True:
            errors.append("B2 per-shot trace packet must persist detector bitstrings")
        if summary.get("stim_observable_bitstrings_persisted") is not True:
            errors.append("B2 per-shot trace packet must persist observable bitstrings")
        if summary.get("synthetic_detector_tick_flag_events_persisted") is not True:
            errors.append("B2 per-shot trace packet must persist synthetic detector/tick flag events")
        if summary.get("real_hardware_or_calibrated_flag_events") is not False:
            errors.append("B2 per-shot trace packet must not claim real calibrated flag events")
        if summary.get("posterior_likelihood_decoder_injection_performed") is not False:
            errors.append("B2 per-shot trace packet must not claim posterior decoder injection")
        if len(payload.get("challenge_packets", [])) != summary.get("challenge_count"):
            errors.append("B2 per-shot trace packet challenge packet count mismatch")
        for packet in payload.get("challenge_packets", []):
            if len(packet.get("shot_traces", [])) != summary.get("shots_per_challenge"):
                errors.append("B2 per-shot trace packet shot trace count mismatch")
            detector_count = packet.get("circuit_summary", {}).get("detectors")
            for trace in packet.get("shot_traces", [])[:5]:
                if len(trace.get("detector_bitstring", "")) != detector_count:
                    errors.append("B2 per-shot trace packet detector bitstring length mismatch")
        if claims.get("per_shot_trace_packet_built") is not True:
            errors.append("B2 per-shot trace packet must disclose trace packet construction")
        if claims.get("real_flag_events_claimed") is not False:
            errors.append("B2 per-shot trace packet must not claim real flag events")
        for key in [
            "circuit_level_decoder_claimed",
            "posterior_likelihood_decoder_claimed",
            "production_decoder_claimed",
            "threshold_claimed",
            "new_code_claimed",
            "hardware_result_claimed",
            "calibrated_device_claimed",
        ]:
            if claims.get(key) is not False:
                errors.append(f"B2 per-shot trace packet must keep {key}=False")

    b2_posterior_injection_gate_status = {}
    if not b2_posterior_injection_gate:
        warnings.append("B2 manifest has no posterior-likelihood decoder injection gate result")
    else:
        result_path = b2_posterior_injection_gate.get("result")
        markdown_path = b2_posterior_injection_gate.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 posterior injection gate result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 posterior injection gate markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        b2_posterior_injection_gate_status = {
            "status": b2_posterior_injection_gate.get("status"),
            "method": b2_posterior_injection_gate.get("method"),
            "model_status": payload.get("model_status"),
            "source_challenge_count": summary.get("source_challenge_count"),
            "injection_profile_count": summary.get("injection_profile_count"),
            "profile_result_count": summary.get("profile_result_count"),
            "total_profile_shots": summary.get("total_profile_shots"),
            "baseline_total_failures": summary.get("baseline_total_failures"),
            "best_profile": summary.get("best_profile"),
            "best_profile_injected_failures": summary.get("best_profile_injected_failures"),
            "best_profile_failure_delta": summary.get("best_profile_failure_delta"),
            "best_profile_fixed_failures": summary.get("best_profile_fixed_failures"),
            "best_profile_introduced_failures": summary.get(
                "best_profile_introduced_failures"
            ),
            "best_profile_changed_predictions": summary.get("best_profile_changed_predictions"),
            "posterior_likelihood_injection_performed": summary.get(
                "posterior_likelihood_injection_performed"
            ),
            "synthetic_flag_likelihoods_consumed": summary.get(
                "synthetic_flag_likelihoods_consumed"
            ),
            "calibrated_flag_data_used": summary.get("calibrated_flag_data_used"),
            "real_hardware_trace_used": summary.get("real_hardware_trace_used"),
            "improvement_gate_passed": summary.get("improvement_gate_passed"),
            "all_challenge_nonregression_gate_passed": summary.get(
                "all_challenge_nonregression_gate_passed"
            ),
            "route_demotion_recommended": summary.get("route_demotion_recommended"),
            "posterior_likelihood_injection_interface_built": claims.get(
                "posterior_likelihood_injection_interface_built"
            ),
            "circuit_level_decoder_claimed": claims.get("circuit_level_decoder_claimed"),
            "production_decoder_claimed": claims.get("production_decoder_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "hardware_result_claimed": claims.get("hardware_result_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "quantum_advantage_claimed": claims.get("quantum_advantage_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b2_posterior_injection_gate.get("status"):
            errors.append("B2 posterior injection gate status mismatch")
        if payload.get("method") != b2_posterior_injection_gate.get("method"):
            errors.append("B2 posterior injection gate method mismatch")
        if payload.get("model_status") != b2_posterior_injection_gate.get("model_status"):
            errors.append("B2 posterior injection gate model-status mismatch")
        for key in [
            "source_challenge_count",
            "injection_profile_count",
            "profile_result_count",
            "total_profile_shots",
            "baseline_total_failures",
            "best_profile",
            "best_profile_injected_failures",
            "best_profile_failure_delta",
            "best_profile_fixed_failures",
            "best_profile_introduced_failures",
            "best_profile_changed_predictions",
            "posterior_likelihood_injection_performed",
            "synthetic_flag_likelihoods_consumed",
            "calibrated_flag_data_used",
            "real_hardware_trace_used",
            "improvement_gate_passed",
            "all_challenge_nonregression_gate_passed",
            "route_demotion_recommended",
        ]:
            if summary.get(key) != b2_posterior_injection_gate.get(key):
                errors.append(f"B2 posterior injection gate {key} mismatch")
        if summary.get("source_challenge_count") != 3:
            errors.append("B2 posterior injection gate should consume three challenge rows")
        if summary.get("injection_profile_count") != 3:
            errors.append("B2 posterior injection gate should evaluate three injection profiles")
        if summary.get("total_profile_shots") != 1728:
            errors.append("B2 posterior injection gate should evaluate 1728 profile shots")
        if summary.get("posterior_likelihood_injection_performed") is not True:
            errors.append("B2 posterior injection gate must perform posterior likelihood injection")
        if summary.get("synthetic_flag_likelihoods_consumed") is not True:
            errors.append("B2 posterior injection gate must consume synthetic flag likelihoods")
        if summary.get("calibrated_flag_data_used") is not False:
            errors.append("B2 posterior injection gate must not claim calibrated flag data")
        if summary.get("real_hardware_trace_used") is not False:
            errors.append("B2 posterior injection gate must not claim real hardware traces")
        if summary.get("improvement_gate_passed") is not False:
            errors.append("B2 posterior injection gate must not pass improvement gate")
        if summary.get("route_demotion_recommended") is not True:
            errors.append("B2 posterior injection gate must keep route demoted")
        if claims.get("posterior_likelihood_injection_interface_built") is not True:
            errors.append("B2 posterior injection gate must disclose injection interface construction")
        if claims.get("posterior_likelihood_injection_performed") is not True:
            errors.append("B2 posterior injection gate must disclose injection execution")
        if claims.get("real_flag_events_claimed") is not False:
            errors.append("B2 posterior injection gate must not claim real flag events")
        for key in [
            "circuit_level_decoder_claimed",
            "production_decoder_claimed",
            "threshold_claimed",
            "new_code_claimed",
            "hardware_result_claimed",
            "calibrated_device_claimed",
            "quantum_advantage_claimed",
        ]:
            if claims.get(key) is not False:
                errors.append(f"B2 posterior injection gate must keep {key}=False")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B2 posterior injection gate validation errors must be zero")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B2 decoder input contract validation errors must be zero")

    b2_dem_edge_semantics_gate_status = {}
    if not b2_dem_edge_semantics_gate:
        warnings.append("B2 manifest has no DEM-informed detector-edge semantics gate")
    else:
        result_path = b2_dem_edge_semantics_gate.get("result")
        markdown_path = b2_dem_edge_semantics_gate.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 DEM edge semantics gate result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 DEM edge semantics gate markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        by_profile = summary.get("by_profile", {})
        aggressive_profile = by_profile.get("aggressive_dem_responsibility", {})
        b2_dem_edge_semantics_gate_status = {
            "status": b2_dem_edge_semantics_gate.get("status"),
            "method": b2_dem_edge_semantics_gate.get("method"),
            "model_status": payload.get("model_status"),
            "source_challenge_count": summary.get("source_challenge_count"),
            "semantic_profile_count": summary.get("semantic_profile_count"),
            "profile_result_count": summary.get("profile_result_count"),
            "total_profile_shots": summary.get("total_profile_shots"),
            "baseline_total_failures": summary.get("baseline_total_failures"),
            "best_profile": summary.get("best_profile"),
            "best_profile_injected_failures": summary.get("best_profile_injected_failures"),
            "best_profile_failure_delta": summary.get("best_profile_failure_delta"),
            "best_profile_fixed_failures": summary.get("best_profile_fixed_failures"),
            "best_profile_introduced_failures": summary.get("best_profile_introduced_failures"),
            "best_profile_changed_predictions": summary.get("best_profile_changed_predictions"),
            "best_profile_max_adjusted_edge_probability": summary.get(
                "best_profile_max_adjusted_edge_probability"
            ),
            "aggressive_profile_injected_failures": aggressive_profile.get("injected_failures"),
            "aggressive_profile_introduced_failures": aggressive_profile.get("introduced_failures"),
            "dem_edge_probability_semantics_performed": summary.get(
                "dem_edge_probability_semantics_performed"
            ),
            "synthetic_flag_likelihoods_consumed": summary.get("synthetic_flag_likelihoods_consumed"),
            "calibrated_flag_data_used": summary.get("calibrated_flag_data_used"),
            "real_hardware_trace_used": summary.get("real_hardware_trace_used"),
            "improvement_gate_passed": summary.get("improvement_gate_passed"),
            "all_challenge_nonregression_gate_passed": summary.get(
                "all_challenge_nonregression_gate_passed"
            ),
            "route_demotion_recommended": summary.get("route_demotion_recommended"),
            "dem_edge_probability_semantics_built": claims.get(
                "dem_edge_probability_semantics_built"
            ),
            "production_decoder_claimed": claims.get("production_decoder_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "hardware_result_claimed": claims.get("hardware_result_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "quantum_advantage_claimed": claims.get("quantum_advantage_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b2_dem_edge_semantics_gate.get("status"):
            errors.append("B2 DEM edge semantics gate status mismatch")
        if payload.get("method") != b2_dem_edge_semantics_gate.get("method"):
            errors.append("B2 DEM edge semantics gate method mismatch")
        if payload.get("model_status") != b2_dem_edge_semantics_gate.get("model_status"):
            errors.append("B2 DEM edge semantics gate model-status mismatch")
        for key in [
            "source_challenge_count",
            "semantic_profile_count",
            "profile_result_count",
            "total_profile_shots",
            "baseline_total_failures",
            "best_profile",
            "best_profile_injected_failures",
            "best_profile_failure_delta",
            "best_profile_fixed_failures",
            "best_profile_introduced_failures",
            "best_profile_changed_predictions",
            "best_profile_max_adjusted_edge_probability",
            "dem_edge_probability_semantics_performed",
            "synthetic_flag_likelihoods_consumed",
            "calibrated_flag_data_used",
            "real_hardware_trace_used",
            "improvement_gate_passed",
            "all_challenge_nonregression_gate_passed",
            "route_demotion_recommended",
        ]:
            if summary.get(key) != b2_dem_edge_semantics_gate.get(key):
                errors.append(f"B2 DEM edge semantics gate {key} mismatch")
        if aggressive_profile.get("injected_failures") != b2_dem_edge_semantics_gate.get(
            "aggressive_profile_injected_failures"
        ):
            errors.append("B2 DEM edge semantics gate aggressive injected-failure mismatch")
        if aggressive_profile.get("introduced_failures") != b2_dem_edge_semantics_gate.get(
            "aggressive_profile_introduced_failures"
        ):
            errors.append("B2 DEM edge semantics gate aggressive introduced-failure mismatch")
        if summary.get("source_challenge_count") != 3:
            errors.append("B2 DEM edge semantics gate should consume three challenge rows")
        if summary.get("semantic_profile_count") != 3:
            errors.append("B2 DEM edge semantics gate should evaluate three semantic profiles")
        if summary.get("total_profile_shots") != 1728:
            errors.append("B2 DEM edge semantics gate should evaluate 1728 profile shots")
        if summary.get("dem_edge_probability_semantics_performed") is not True:
            errors.append("B2 DEM edge semantics gate must perform DEM edge-probability semantics")
        if summary.get("synthetic_flag_likelihoods_consumed") is not True:
            errors.append("B2 DEM edge semantics gate must consume synthetic flag likelihoods")
        if summary.get("calibrated_flag_data_used") is not False:
            errors.append("B2 DEM edge semantics gate must not claim calibrated flag data")
        if summary.get("real_hardware_trace_used") is not False:
            errors.append("B2 DEM edge semantics gate must not claim real hardware traces")
        if summary.get("improvement_gate_passed") is not False:
            errors.append("B2 DEM edge semantics gate must not pass improvement gate")
        if summary.get("route_demotion_recommended") is not True:
            errors.append("B2 DEM edge semantics gate must keep route demoted")
        if claims.get("dem_edge_probability_semantics_built") is not True:
            errors.append("B2 DEM edge semantics gate must disclose DEM semantics construction")
        if claims.get("dem_edge_probability_semantics_performed") is not True:
            errors.append("B2 DEM edge semantics gate must disclose DEM semantics execution")
        if claims.get("real_flag_events_claimed") is not False:
            errors.append("B2 DEM edge semantics gate must not claim real flag events")
        for key in [
            "production_decoder_claimed",
            "threshold_claimed",
            "new_code_claimed",
            "hardware_result_claimed",
            "calibrated_device_claimed",
            "quantum_advantage_claimed",
        ]:
            if claims.get(key) is not False:
                errors.append(f"B2 DEM edge semantics gate must keep {key}=False")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B2 DEM edge semantics gate validation errors must be zero")

    b2_hardware_like_leakage_gate_status = {}
    if not b2_hardware_like_leakage_gate:
        warnings.append("B2 manifest has no hardware-like leakage model gate")
    else:
        result_path = b2_hardware_like_leakage_gate.get("result")
        markdown_path = b2_hardware_like_leakage_gate.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B2 hardware-like leakage gate result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B2 hardware-like leakage gate markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        by_profile = summary.get("by_profile", {})
        stress_profile = by_profile.get("stress_hardware_like_leakage", {})
        b2_hardware_like_leakage_gate_status = {
            "status": b2_hardware_like_leakage_gate.get("status"),
            "method": b2_hardware_like_leakage_gate.get("method"),
            "model_status": payload.get("model_status"),
            "source_challenge_count": summary.get("source_challenge_count"),
            "observation_profile_count": summary.get("observation_profile_count"),
            "profile_result_count": summary.get("profile_result_count"),
            "total_profile_shots": summary.get("total_profile_shots"),
            "holdout_profile_shots": summary.get("holdout_profile_shots"),
            "baseline_total_failures": summary.get("baseline_total_failures"),
            "best_profile": summary.get("best_profile"),
            "best_profile_injected_failures": summary.get("best_profile_injected_failures"),
            "best_profile_failure_delta": summary.get("best_profile_failure_delta"),
            "best_profile_fixed_failures": summary.get("best_profile_fixed_failures"),
            "best_profile_introduced_failures": summary.get("best_profile_introduced_failures"),
            "best_profile_changed_predictions": summary.get("best_profile_changed_predictions"),
            "best_profile_model_flag_events": summary.get("best_profile_model_flag_events"),
            "best_profile_max_adjusted_edge_probability": summary.get(
                "best_profile_max_adjusted_edge_probability"
            ),
            "best_profile_holdout_baseline_failures": summary.get(
                "best_profile_holdout_baseline_failures"
            ),
            "best_profile_holdout_injected_failures": summary.get(
                "best_profile_holdout_injected_failures"
            ),
            "best_profile_holdout_failure_delta": summary.get(
                "best_profile_holdout_failure_delta"
            ),
            "best_profile_holdout_fixed_failures": summary.get(
                "best_profile_holdout_fixed_failures"
            ),
            "best_profile_holdout_introduced_failures": summary.get(
                "best_profile_holdout_introduced_failures"
            ),
            "best_profile_holdout_changed_predictions": summary.get(
                "best_profile_holdout_changed_predictions"
            ),
            "stress_profile_model_flag_events": stress_profile.get("model_flag_events"),
            "hardware_like_leakage_model_used": summary.get("hardware_like_leakage_model_used"),
            "detector_bitstrings_consumed": summary.get("detector_bitstrings_consumed"),
            "synthetic_flag_fixture_consumed": summary.get("synthetic_flag_fixture_consumed"),
            "calibrated_flag_data_used": summary.get("calibrated_flag_data_used"),
            "real_hardware_trace_used": summary.get("real_hardware_trace_used"),
            "holdout_improvement_gate_passed": summary.get("holdout_improvement_gate_passed"),
            "holdout_nonregression_gate_passed": summary.get("holdout_nonregression_gate_passed"),
            "route_demotion_recommended": summary.get("route_demotion_recommended"),
            "hardware_like_leakage_model_built": claims.get("hardware_like_leakage_model_built"),
            "production_decoder_claimed": claims.get("production_decoder_claimed"),
            "threshold_claimed": claims.get("threshold_claimed"),
            "new_code_claimed": claims.get("new_code_claimed"),
            "hardware_result_claimed": claims.get("hardware_result_claimed"),
            "calibrated_device_claimed": claims.get("calibrated_device_claimed"),
            "quantum_advantage_claimed": claims.get("quantum_advantage_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b2_hardware_like_leakage_gate.get("status"):
            errors.append("B2 hardware-like leakage gate status mismatch")
        if payload.get("method") != b2_hardware_like_leakage_gate.get("method"):
            errors.append("B2 hardware-like leakage gate method mismatch")
        if payload.get("model_status") != b2_hardware_like_leakage_gate.get("model_status"):
            errors.append("B2 hardware-like leakage gate model-status mismatch")
        for key in [
            "source_challenge_count",
            "observation_profile_count",
            "profile_result_count",
            "total_profile_shots",
            "holdout_profile_shots",
            "baseline_total_failures",
            "best_profile",
            "best_profile_injected_failures",
            "best_profile_failure_delta",
            "best_profile_fixed_failures",
            "best_profile_introduced_failures",
            "best_profile_changed_predictions",
            "best_profile_model_flag_events",
            "best_profile_max_adjusted_edge_probability",
            "best_profile_holdout_baseline_failures",
            "best_profile_holdout_injected_failures",
            "best_profile_holdout_failure_delta",
            "best_profile_holdout_fixed_failures",
            "best_profile_holdout_introduced_failures",
            "best_profile_holdout_changed_predictions",
            "hardware_like_leakage_model_used",
            "detector_bitstrings_consumed",
            "synthetic_flag_fixture_consumed",
            "calibrated_flag_data_used",
            "real_hardware_trace_used",
            "holdout_improvement_gate_passed",
            "holdout_nonregression_gate_passed",
            "route_demotion_recommended",
        ]:
            if summary.get(key) != b2_hardware_like_leakage_gate.get(key):
                errors.append(f"B2 hardware-like leakage gate {key} mismatch")
        if stress_profile.get("model_flag_events") != b2_hardware_like_leakage_gate.get(
            "stress_profile_model_flag_events"
        ):
            errors.append("B2 hardware-like leakage gate stress flag-event mismatch")
        if summary.get("source_challenge_count") != 3:
            errors.append("B2 hardware-like leakage gate should consume three challenge rows")
        if summary.get("observation_profile_count") != 3:
            errors.append("B2 hardware-like leakage gate should evaluate three observation profiles")
        if summary.get("total_profile_shots") != 1728:
            errors.append("B2 hardware-like leakage gate should evaluate 1728 profile shots")
        if summary.get("holdout_profile_shots") != 864:
            errors.append("B2 hardware-like leakage gate should evaluate 864 holdout profile shots")
        if summary.get("hardware_like_leakage_model_used") is not True:
            errors.append("B2 hardware-like leakage gate must use hardware-like leakage model")
        if summary.get("detector_bitstrings_consumed") is not True:
            errors.append("B2 hardware-like leakage gate must consume detector bitstrings")
        if summary.get("synthetic_flag_fixture_consumed") is not False:
            errors.append("B2 hardware-like leakage gate must not consume synthetic flag fixture")
        if summary.get("calibrated_flag_data_used") is not False:
            errors.append("B2 hardware-like leakage gate must not claim calibrated flag data")
        if summary.get("real_hardware_trace_used") is not False:
            errors.append("B2 hardware-like leakage gate must not claim real hardware traces")
        if summary.get("holdout_improvement_gate_passed") is not False:
            errors.append("B2 hardware-like leakage gate must not pass holdout improvement gate")
        if summary.get("route_demotion_recommended") is not True:
            errors.append("B2 hardware-like leakage gate must keep route demoted")
        if claims.get("hardware_like_leakage_model_built") is not True:
            errors.append("B2 hardware-like leakage gate must disclose model construction")
        if claims.get("hardware_like_leakage_model_used") is not True:
            errors.append("B2 hardware-like leakage gate must disclose model execution")
        if claims.get("synthetic_flag_fixture_consumed") is not False:
            errors.append("B2 hardware-like leakage gate must not claim synthetic fixture consumption")
        if claims.get("real_flag_events_claimed") is not False:
            errors.append("B2 hardware-like leakage gate must not claim real flag events")
        for key in [
            "production_decoder_claimed",
            "threshold_claimed",
            "new_code_claimed",
            "hardware_result_claimed",
            "calibrated_device_claimed",
            "quantum_advantage_claimed",
        ]:
            if claims.get(key) is not False:
                errors.append(f"B2 hardware-like leakage gate must keep {key}=False")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B2 hardware-like leakage gate validation errors must be zero")

    b3_manifest = yaml.safe_load(read(b3_manifest_path))
    b3_results = b3_manifest.get("current_results", {})
    b3_resource = b3_results.get("pyscf_small_molecule_resource_proxy_v0")
    b3_quantum_observable_fci = b3_results.get("quantum_observable_fci_comparison_v0")
    b3_hamiltonian_pauli_mapper = b3_results.get("hamiltonian_pauli_mapper_comparison_v0")
    b3_sampled_pauli_confidence = b3_results.get("sampled_pauli_estimator_confidence_v0")
    b3_selected_ci_grouped_pauli = b3_results.get("selected_ci_grouped_pauli_boundary_v0")
    b3_larger_basis_hamiltonian_mapper = b3_results.get("larger_basis_hamiltonian_mapper_v0")
    b3_larger_basis_qwc_grouping = b3_results.get("larger_basis_qwc_grouping_v0")
    b3_grouped_covariance_shot_floor = b3_results.get("grouped_covariance_shot_floor_v0")
    b3_chemical_state_prep_derivative = b3_results.get("chemical_state_prep_derivative_boundary_v0")
    b3_compiled_ucc_adapt_covariance = b3_results.get("compiled_ucc_adapt_covariance_pilot_v0")
    b3_cross_molecule_ucc_adapt_pressure = b3_results.get("cross_molecule_ucc_adapt_pressure_v0")
    b3_status = {}
    if not b3_resource:
        warnings.append("B3 manifest has no PySCF resource proxy result")
    else:
        result_path = b3_resource.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B3 resource proxy result path missing: {result_path}")
        b3_status = {
            "status": b3_resource.get("status"),
            "molecule_count": b3_resource.get("molecule_count"),
            "basis": b3_resource.get("basis"),
            "proxy_t_count_reduction_range": b3_resource.get("proxy_t_count_reduction_range"),
            "result_exists": result_exists,
            "result": result_path,
        }

    b3_quantum_observable_fci_status = {}
    if not b3_quantum_observable_fci:
        warnings.append("B3 manifest has no quantum observable vs FCI comparison result")
    else:
        result_path = b3_quantum_observable_fci.get("result")
        markdown_path = b3_quantum_observable_fci.get("markdown_report")
        qasm_directory = b3_quantum_observable_fci.get("qasm_directory")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        qasm_directory_exists = bool(qasm_directory and path_exists_from(benchmarks, qasm_directory))
        if not result_exists:
            errors.append(f"B3 quantum observable vs FCI result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B3 quantum observable vs FCI markdown missing: {markdown_path}")
        if not qasm_directory_exists:
            errors.append(f"B3 quantum observable vs FCI qasm directory missing: {qasm_directory}")

        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        rows = payload.get("rows", [])
        qasm_paths_exist = [
            bool(row.get("qasm_path") and (root / str(row.get("qasm_path"))).exists())
            for row in rows
        ]
        if payload.get("benchmark_id") != "B3":
            errors.append("B3 quantum observable vs FCI payload must have benchmark_id B3")
        if payload.get("dependency_benchmark") != "B3":
            errors.append("B3 quantum observable vs FCI dependency_benchmark must be B3")
        if payload.get("status") != b3_quantum_observable_fci.get("status"):
            errors.append("B3 quantum observable vs FCI payload status differs from manifest")
        if payload.get("method") != b3_quantum_observable_fci.get("method"):
            errors.append("B3 quantum observable vs FCI payload method differs from manifest")
        if payload.get("source_denominator_method") != "b10_t1_d5_b3_reaction_observable_table_v0":
            errors.append("B3 quantum observable vs FCI source denominator method changed")
        if payload.get("source_fci_method") != "b10_t1_d5_b3_fci_reference_table_v0":
            errors.append("B3 quantum observable vs FCI source FCI method changed")
        if summary.get("instance_count") != b3_quantum_observable_fci.get("reaction_coordinate_instances"):
            errors.append("B3 quantum observable vs FCI instance count differs from manifest")
        if summary.get("qasm_file_count") != b3_quantum_observable_fci.get("qasm_file_count"):
            errors.append("B3 quantum observable vs FCI qasm count differs from manifest")
        if summary.get("max_total_qubits") != b3_quantum_observable_fci.get("max_total_qubits"):
            errors.append("B3 quantum observable vs FCI max qubits differs from manifest")
        if summary.get("max_controlled_phase_gates") != b3_quantum_observable_fci.get(
            "max_controlled_phase_gates"
        ):
            errors.append("B3 quantum observable vs FCI controlled-phase count differs from manifest")
        if summary.get("fci_denominator_beaten_count") != b3_quantum_observable_fci.get(
            "fci_denominator_beaten_count"
        ):
            errors.append("B3 quantum observable vs FCI beaten count differs from manifest")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B3 quantum observable vs FCI must not claim quantum advantage")
        if summary.get("reaction_dynamics_solution_claimed") is not False:
            errors.append("B3 quantum observable vs FCI must not claim reaction dynamics solution")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B3 quantum observable vs FCI validation errors must be zero")
        if len(rows) != b3_quantum_observable_fci.get("reaction_coordinate_instances"):
            errors.append("B3 quantum observable vs FCI row count differs from manifest")
        if qasm_paths_exist and not all(qasm_paths_exist):
            errors.append("B3 quantum observable vs FCI includes missing qasm_path rows")
        if any(row.get("quantum_beats_fci_denominator") is not False for row in rows):
            errors.append("B3 quantum observable vs FCI rows must not claim FCI denominator wins")
        if any(float(row.get("measurement_shot_floor", 0)) <= 0 for row in rows):
            errors.append("B3 quantum observable vs FCI rows must retain positive shot floors")
        if any(int(row.get("controlled_phase_gates", 0)) <= 0 for row in rows):
            errors.append("B3 quantum observable vs FCI rows must retain positive controlled-phase counts")

        b3_quantum_observable_fci_status = {
            "status": b3_quantum_observable_fci.get("status"),
            "method": b3_quantum_observable_fci.get("method"),
            "reaction_coordinate_instances": b3_quantum_observable_fci.get("reaction_coordinate_instances"),
            "qasm_file_count": b3_quantum_observable_fci.get("qasm_file_count"),
            "max_total_qubits": b3_quantum_observable_fci.get("max_total_qubits"),
            "max_controlled_phase_gates": b3_quantum_observable_fci.get("max_controlled_phase_gates"),
            "fci_denominator_beaten_count": b3_quantum_observable_fci.get("fci_denominator_beaten_count"),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "reaction_dynamics_solution_claimed": summary.get("reaction_dynamics_solution_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "all_qasm_paths_exist": bool(qasm_paths_exist) and all(qasm_paths_exist),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "qasm_directory_exists": qasm_directory_exists,
            "result": result_path,
            "markdown_report": markdown_path,
            "qasm_directory": qasm_directory,
        }

    b3_hamiltonian_pauli_mapper_status = {}
    if not b3_hamiltonian_pauli_mapper:
        warnings.append("B3 manifest has no Hamiltonian Pauli mapper comparison result")
    else:
        result_path = b3_hamiltonian_pauli_mapper.get("result")
        markdown_path = b3_hamiltonian_pauli_mapper.get("markdown_report")
        qasm_directory = b3_hamiltonian_pauli_mapper.get("qasm_directory")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        qasm_directory_exists = bool(qasm_directory and path_exists_from(benchmarks, qasm_directory))
        if not result_exists:
            errors.append(f"B3 Hamiltonian Pauli mapper result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B3 Hamiltonian Pauli mapper markdown missing: {markdown_path}")
        if not qasm_directory_exists:
            errors.append(f"B3 Hamiltonian Pauli mapper qasm directory missing: {qasm_directory}")

        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        rows = payload.get("rows", [])
        qasm_paths_exist = [
            bool(row.get("qasm_path") and (root / str(row.get("qasm_path"))).exists())
            for row in rows
        ]
        if payload.get("benchmark_id") != "B3":
            errors.append("B3 Hamiltonian Pauli mapper payload must have benchmark_id B3")
        if payload.get("dependency_benchmark") != "B3":
            errors.append("B3 Hamiltonian Pauli mapper dependency_benchmark must be B3")
        if payload.get("status") != b3_hamiltonian_pauli_mapper.get("status"):
            errors.append("B3 Hamiltonian Pauli mapper payload status differs from manifest")
        if payload.get("method") != b3_hamiltonian_pauli_mapper.get("method"):
            errors.append("B3 Hamiltonian Pauli mapper payload method differs from manifest")
        if payload.get("source_fci_method") != "b10_t1_d5_b3_fci_reference_table_v0":
            errors.append("B3 Hamiltonian Pauli mapper source FCI method changed")
        if summary.get("instance_count") != b3_hamiltonian_pauli_mapper.get("reaction_coordinate_instances"):
            errors.append("B3 Hamiltonian Pauli mapper instance count differs from manifest")
        if summary.get("qasm_file_count") != b3_hamiltonian_pauli_mapper.get("qasm_file_count"):
            errors.append("B3 Hamiltonian Pauli mapper qasm count differs from manifest")
        if summary.get("max_total_qubits") != b3_hamiltonian_pauli_mapper.get("max_total_qubits"):
            errors.append("B3 Hamiltonian Pauli mapper max qubits differs from manifest")
        if summary.get("max_pauli_terms_after_cutoff") != b3_hamiltonian_pauli_mapper.get(
            "max_pauli_terms_after_cutoff"
        ):
            errors.append("B3 Hamiltonian Pauli mapper max Pauli terms differs from manifest")
        if summary.get("max_total_measurement_shot_floor") != b3_hamiltonian_pauli_mapper.get(
            "max_total_measurement_shot_floor"
        ):
            errors.append("B3 Hamiltonian Pauli mapper max shot floor differs from manifest")
        if summary.get("fci_denominator_beaten_count") != b3_hamiltonian_pauli_mapper.get(
            "fci_denominator_beaten_count"
        ):
            errors.append("B3 Hamiltonian Pauli mapper beaten count differs from manifest")
        if summary.get("state_preparation_cost_included") is not True:
            errors.append("B3 Hamiltonian Pauli mapper must include state-preparation cost")
        if summary.get("observable_variance_estimate_included") is not True:
            errors.append("B3 Hamiltonian Pauli mapper must include observable variance estimate")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B3 Hamiltonian Pauli mapper must not claim quantum advantage")
        if summary.get("reaction_dynamics_solution_claimed") is not False:
            errors.append("B3 Hamiltonian Pauli mapper must not claim reaction dynamics solution")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B3 Hamiltonian Pauli mapper validation errors must be zero")
        if len(rows) != b3_hamiltonian_pauli_mapper.get("reaction_coordinate_instances"):
            errors.append("B3 Hamiltonian Pauli mapper row count differs from manifest")
        if qasm_paths_exist and not all(qasm_paths_exist):
            errors.append("B3 Hamiltonian Pauli mapper includes missing qasm_path rows")
        if any(row.get("quantum_beats_fci_denominator") is not False for row in rows):
            errors.append("B3 Hamiltonian Pauli mapper rows must not claim FCI denominator wins")
        if any(int(row.get("pauli_terms_after_cutoff", 0)) <= 0 for row in rows):
            errors.append("B3 Hamiltonian Pauli mapper rows must have mapped Pauli terms")
        if any(float(row.get("variance_upper_bound", 0.0)) <= 0.0 for row in rows):
            errors.append("B3 Hamiltonian Pauli mapper rows must have positive variance bounds")

        b3_hamiltonian_pauli_mapper_status = {
            "status": b3_hamiltonian_pauli_mapper.get("status"),
            "method": b3_hamiltonian_pauli_mapper.get("method"),
            "reaction_coordinate_instances": b3_hamiltonian_pauli_mapper.get("reaction_coordinate_instances"),
            "qasm_file_count": b3_hamiltonian_pauli_mapper.get("qasm_file_count"),
            "max_total_qubits": b3_hamiltonian_pauli_mapper.get("max_total_qubits"),
            "max_pauli_terms_after_cutoff": b3_hamiltonian_pauli_mapper.get("max_pauli_terms_after_cutoff"),
            "max_measurement_packet_terms": b3_hamiltonian_pauli_mapper.get("max_measurement_packet_terms"),
            "max_total_measurement_shot_floor": b3_hamiltonian_pauli_mapper.get(
                "max_total_measurement_shot_floor"
            ),
            "fci_denominator_beaten_count": b3_hamiltonian_pauli_mapper.get("fci_denominator_beaten_count"),
            "state_preparation_cost_included": summary.get("state_preparation_cost_included"),
            "observable_variance_estimate_included": summary.get("observable_variance_estimate_included"),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "reaction_dynamics_solution_claimed": summary.get("reaction_dynamics_solution_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "all_qasm_paths_exist": bool(qasm_paths_exist) and all(qasm_paths_exist),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "qasm_directory_exists": qasm_directory_exists,
            "result": result_path,
            "markdown_report": markdown_path,
            "qasm_directory": qasm_directory,
        }

    b3_sampled_pauli_confidence_status = {}
    if not b3_sampled_pauli_confidence:
        warnings.append("B3 manifest has no sampled Pauli estimator confidence result")
    else:
        result_path = b3_sampled_pauli_confidence.get("result")
        markdown_path = b3_sampled_pauli_confidence.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B3 sampled Pauli confidence result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B3 sampled Pauli confidence markdown missing: {markdown_path}")

        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        rows = payload.get("rows", [])
        if payload.get("benchmark_id") != "B3":
            errors.append("B3 sampled Pauli confidence payload must have benchmark_id B3")
        if payload.get("dependency_benchmark") != "B3":
            errors.append("B3 sampled Pauli confidence dependency_benchmark must be B3")
        if payload.get("status") != b3_sampled_pauli_confidence.get("status"):
            errors.append("B3 sampled Pauli confidence payload status differs from manifest")
        if payload.get("method") != b3_sampled_pauli_confidence.get("method"):
            errors.append("B3 sampled Pauli confidence payload method differs from manifest")
        if payload.get("source_mapper_method") != "b3_hamiltonian_pauli_mapper_comparison_v0":
            errors.append("B3 sampled Pauli confidence source mapper method changed")
        if payload.get("source_fci_method") != "b10_t1_d5_b3_fci_reference_table_v0":
            errors.append("B3 sampled Pauli confidence source FCI method changed")
        if summary.get("instance_count") != b3_sampled_pauli_confidence.get("reaction_coordinate_instances"):
            errors.append("B3 sampled Pauli confidence instance count differs from manifest")
        if summary.get("pilot_shots_per_random_term") != b3_sampled_pauli_confidence.get(
            "pilot_shots_per_random_term"
        ):
            errors.append("B3 sampled Pauli confidence pilot shots differ from manifest")
        if summary.get("confidence_z") != b3_sampled_pauli_confidence.get("confidence_z"):
            errors.append("B3 sampled Pauli confidence z score differs from manifest")
        if summary.get("max_random_pauli_terms") != b3_sampled_pauli_confidence.get("max_random_pauli_terms"):
            errors.append("B3 sampled Pauli confidence max random terms differs from manifest")
        if summary.get("max_target_total_shot_floor_neyman") != b3_sampled_pauli_confidence.get(
            "max_target_total_shot_floor_neyman"
        ):
            errors.append("B3 sampled Pauli confidence max Neyman shot floor differs from manifest")
        if summary.get("all_pilot_cis_contain_exact_energy") is not True:
            errors.append("B3 sampled Pauli confidence pilot CIs should contain exact HF energy")
        if summary.get("sampled_confidence_intervals_included") is not True:
            errors.append("B3 sampled Pauli confidence must include sampled intervals")
        if summary.get("selected_ci_or_larger_active_space_included") is not False:
            errors.append("B3 sampled Pauli confidence must not claim selected-CI/larger-active-space denominator")
        if summary.get("fci_denominator_beaten_count") != 0:
            errors.append("B3 sampled Pauli confidence must not claim FCI wins")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B3 sampled Pauli confidence must not claim quantum advantage")
        if summary.get("reaction_dynamics_solution_claimed") is not False:
            errors.append("B3 sampled Pauli confidence must not claim reaction dynamics solution")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B3 sampled Pauli confidence validation errors must be zero")
        if len(rows) != b3_sampled_pauli_confidence.get("reaction_coordinate_instances"):
            errors.append("B3 sampled Pauli confidence row count differs from manifest")
        if any(row.get("quantum_beats_fci_denominator") is not False for row in rows):
            errors.append("B3 sampled Pauli confidence rows must not claim FCI denominator wins")
        if any(float(row.get("shot_reduction_vs_upper_bound", 0.0)) <= 1.0 for row in rows):
            errors.append("B3 sampled Pauli confidence rows should improve over upper-bound shot floors")

        b3_sampled_pauli_confidence_status = {
            "status": b3_sampled_pauli_confidence.get("status"),
            "method": b3_sampled_pauli_confidence.get("method"),
            "reaction_coordinate_instances": b3_sampled_pauli_confidence.get("reaction_coordinate_instances"),
            "pilot_shots_per_random_term": b3_sampled_pauli_confidence.get("pilot_shots_per_random_term"),
            "confidence_z": b3_sampled_pauli_confidence.get("confidence_z"),
            "max_random_pauli_terms": b3_sampled_pauli_confidence.get("max_random_pauli_terms"),
            "max_pilot_total_shots": b3_sampled_pauli_confidence.get("max_pilot_total_shots"),
            "max_target_total_shot_floor_neyman": b3_sampled_pauli_confidence.get(
                "max_target_total_shot_floor_neyman"
            ),
            "min_shot_reduction_vs_upper_bound": b3_sampled_pauli_confidence.get(
                "min_shot_reduction_vs_upper_bound"
            ),
            "max_shot_reduction_vs_upper_bound": b3_sampled_pauli_confidence.get(
                "max_shot_reduction_vs_upper_bound"
            ),
            "all_pilot_cis_contain_exact_energy": summary.get("all_pilot_cis_contain_exact_energy"),
            "sampled_confidence_intervals_included": summary.get("sampled_confidence_intervals_included"),
            "selected_ci_or_larger_active_space_included": summary.get(
                "selected_ci_or_larger_active_space_included"
            ),
            "fci_denominator_beaten_count": summary.get("fci_denominator_beaten_count"),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "reaction_dynamics_solution_claimed": summary.get("reaction_dynamics_solution_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }

    b3_selected_ci_grouped_pauli_status = {}
    if not b3_selected_ci_grouped_pauli:
        warnings.append("B3 manifest has no selected-CI grouped Pauli boundary result")
    else:
        result_path = b3_selected_ci_grouped_pauli.get("result")
        markdown_path = b3_selected_ci_grouped_pauli.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B3 selected-CI grouped Pauli result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B3 selected-CI grouped Pauli markdown missing: {markdown_path}")

        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        rows = payload.get("rows", [])
        if payload.get("benchmark_id") != "B3":
            errors.append("B3 selected-CI grouped Pauli payload must have benchmark_id B3")
        if payload.get("dependency_benchmark") != "B3":
            errors.append("B3 selected-CI grouped Pauli dependency_benchmark must be B3")
        if payload.get("status") != b3_selected_ci_grouped_pauli.get("status"):
            errors.append("B3 selected-CI grouped Pauli payload status differs from manifest")
        if payload.get("method") != b3_selected_ci_grouped_pauli.get("method"):
            errors.append("B3 selected-CI grouped Pauli payload method differs from manifest")
        if payload.get("source_sampled_pauli_method") != "b3_sampled_pauli_estimator_confidence_v0":
            errors.append("B3 selected-CI grouped Pauli source sampled-Pauli method changed")
        if payload.get("source_mapper_method") != "b3_hamiltonian_pauli_mapper_comparison_v0":
            errors.append("B3 selected-CI grouped Pauli source mapper method changed")
        if payload.get("source_fci_method") != "b10_t1_d5_b3_fci_reference_table_v0":
            errors.append("B3 selected-CI grouped Pauli source FCI method changed")
        if summary.get("instance_count") != b3_selected_ci_grouped_pauli.get("reaction_coordinate_instances"):
            errors.append("B3 selected-CI grouped Pauli instance count differs from manifest")
        if summary.get("selected_ci_larger_basis_rows") != b3_selected_ci_grouped_pauli.get(
            "selected_ci_larger_basis_rows"
        ):
            errors.append("B3 selected-CI grouped Pauli larger-basis row count differs from manifest")
        if summary.get("max_selected_ci_spatial_orbitals") != b3_selected_ci_grouped_pauli.get(
            "max_selected_ci_spatial_orbitals"
        ):
            errors.append("B3 selected-CI grouped Pauli max selected-CI orbitals differs from manifest")
        if summary.get("max_selected_ci_spin_orbital_qubits") != b3_selected_ci_grouped_pauli.get(
            "max_selected_ci_spin_orbital_qubits"
        ):
            errors.append("B3 selected-CI grouped Pauli max selected-CI spin qubits differs from manifest")
        if summary.get("max_selected_ci_determinant_product") != b3_selected_ci_grouped_pauli.get(
            "max_selected_ci_determinant_product"
        ):
            errors.append("B3 selected-CI grouped Pauli determinant product differs from manifest")
        if summary.get("all_selected_ci_points_converged") is not True:
            errors.append("B3 selected-CI grouped Pauli selected-CI points should converge")
        if summary.get("selected_ci_or_larger_active_space_included") is not True:
            errors.append("B3 selected-CI grouped Pauli must include selected-CI/larger active space")
        if summary.get("pauli_grouping_included") is not True:
            errors.append("B3 selected-CI grouped Pauli must include Pauli grouping")
        if summary.get("ansatz_state_preparation_surcharge_included") is not True:
            errors.append("B3 selected-CI grouped Pauli must include ansatz state-preparation surcharge")
        if summary.get("large_basis_quantum_mapper_included") is not False:
            errors.append("B3 selected-CI grouped Pauli must not claim large-basis quantum mapper")
        if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
            errors.append("B3 selected-CI grouped Pauli must not claim larger-basis denominator wins")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B3 selected-CI grouped Pauli must not claim quantum advantage")
        if summary.get("reaction_dynamics_solution_claimed") is not False:
            errors.append("B3 selected-CI grouped Pauli must not claim reaction dynamics solution")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B3 selected-CI grouped Pauli validation errors must be zero")
        if len(rows) != b3_selected_ci_grouped_pauli.get("reaction_coordinate_instances"):
            errors.append("B3 selected-CI grouped Pauli row count differs from manifest")
        if any(row.get("selected_ci_larger_than_sto3g_orbitals") is not True for row in rows):
            errors.append("B3 selected-CI grouped Pauli rows must all be larger than STO-3G orbitals")
        if any(row.get("candidate_beats_selected_ci_larger_basis_denominator") is not False for row in rows):
            errors.append("B3 selected-CI grouped Pauli rows must not claim larger-basis denominator wins")
        if any(row.get("grouped_pauli_estimator", {}).get("qwc_group_count", 0) <= 0 for row in rows):
            errors.append("B3 selected-CI grouped Pauli rows must have QWC groups")

        b3_selected_ci_grouped_pauli_status = {
            "status": b3_selected_ci_grouped_pauli.get("status"),
            "method": b3_selected_ci_grouped_pauli.get("method"),
            "reaction_coordinate_instances": b3_selected_ci_grouped_pauli.get(
                "reaction_coordinate_instances"
            ),
            "selected_ci_larger_basis_rows": b3_selected_ci_grouped_pauli.get(
                "selected_ci_larger_basis_rows"
            ),
            "max_selected_ci_spatial_orbitals": b3_selected_ci_grouped_pauli.get(
                "max_selected_ci_spatial_orbitals"
            ),
            "max_selected_ci_spin_orbital_qubits": b3_selected_ci_grouped_pauli.get(
                "max_selected_ci_spin_orbital_qubits"
            ),
            "max_selected_ci_determinant_product": b3_selected_ci_grouped_pauli.get(
                "max_selected_ci_determinant_product"
            ),
            "max_selected_ci_total_determinant_product_three_point": b3_selected_ci_grouped_pauli.get(
                "max_selected_ci_total_determinant_product_three_point"
            ),
            "all_selected_ci_points_converged": summary.get("all_selected_ci_points_converged"),
            "pauli_grouping_included": summary.get("pauli_grouping_included"),
            "ansatz_state_preparation_surcharge_included": summary.get(
                "ansatz_state_preparation_surcharge_included"
            ),
            "large_basis_quantum_mapper_included": summary.get("large_basis_quantum_mapper_included"),
            "max_qwc_group_count": b3_selected_ci_grouped_pauli.get("max_qwc_group_count"),
            "min_packet_reduction_vs_ungrouped": b3_selected_ci_grouped_pauli.get(
                "min_packet_reduction_vs_ungrouped"
            ),
            "max_packet_reduction_vs_ungrouped": b3_selected_ci_grouped_pauli.get(
                "max_packet_reduction_vs_ungrouped"
            ),
            "max_ansatz_two_qubit_gate_executions_at_target": b3_selected_ci_grouped_pauli.get(
                "max_ansatz_two_qubit_gate_executions_at_target"
            ),
            "selected_ci_larger_basis_denominator_beaten_count": summary.get(
                "selected_ci_larger_basis_denominator_beaten_count"
            ),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "reaction_dynamics_solution_claimed": summary.get("reaction_dynamics_solution_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }

    b3_larger_basis_hamiltonian_mapper_status = {}
    if not b3_larger_basis_hamiltonian_mapper:
        warnings.append("B3 manifest has no larger-basis Hamiltonian mapper result")
    else:
        result_path = b3_larger_basis_hamiltonian_mapper.get("result")
        markdown_path = b3_larger_basis_hamiltonian_mapper.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B3 larger-basis Hamiltonian mapper result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B3 larger-basis Hamiltonian mapper markdown missing: {markdown_path}")

        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        rows = payload.get("rows", [])
        if payload.get("benchmark_id") != "B3":
            errors.append("B3 larger-basis Hamiltonian mapper payload must have benchmark_id B3")
        if payload.get("dependency_benchmark") != "B3":
            errors.append("B3 larger-basis Hamiltonian mapper dependency_benchmark must be B3")
        if payload.get("status") != b3_larger_basis_hamiltonian_mapper.get("status"):
            errors.append("B3 larger-basis Hamiltonian mapper payload status differs from manifest")
        if payload.get("method") != b3_larger_basis_hamiltonian_mapper.get("method"):
            errors.append("B3 larger-basis Hamiltonian mapper payload method differs from manifest")
        if payload.get("source_selected_ci_grouped_pauli_method") != "b3_selected_ci_grouped_pauli_boundary_v0":
            errors.append("B3 larger-basis Hamiltonian mapper source selected-CI method changed")
        if summary.get("instance_count") != b3_larger_basis_hamiltonian_mapper.get(
            "reaction_coordinate_instances"
        ):
            errors.append("B3 larger-basis Hamiltonian mapper instance count differs from manifest")
        if summary.get("larger_basis_quantum_mapper_included") is not True:
            errors.append("B3 larger-basis Hamiltonian mapper must include larger-basis mapper")
        if summary.get("same_basis_as_selected_ci_denominator") is not True:
            errors.append("B3 larger-basis Hamiltonian mapper must use same basis as selected-CI denominator")
        if summary.get("pauli_measurement_cost_included") is not True:
            errors.append("B3 larger-basis Hamiltonian mapper must include Pauli measurement cost")
        if summary.get("ansatz_state_preparation_surcharge_included") is not True:
            errors.append("B3 larger-basis Hamiltonian mapper must include ansatz state-prep surcharge")
        if summary.get("max_total_qubits") != b3_larger_basis_hamiltonian_mapper.get("max_total_qubits"):
            errors.append("B3 larger-basis Hamiltonian mapper max qubits differs from manifest")
        if summary.get("max_pauli_terms_after_cutoff") != b3_larger_basis_hamiltonian_mapper.get(
            "max_pauli_terms_after_cutoff"
        ):
            errors.append("B3 larger-basis Hamiltonian mapper max Pauli terms differs from manifest")
        if summary.get("max_conservative_same_basis_bucket_count") != b3_larger_basis_hamiltonian_mapper.get(
            "max_conservative_same_basis_bucket_count"
        ):
            errors.append("B3 larger-basis Hamiltonian mapper max bucket count differs from manifest")
        if summary.get("max_neyman_target_total_shot_floor") != b3_larger_basis_hamiltonian_mapper.get(
            "max_neyman_target_total_shot_floor"
        ):
            errors.append("B3 larger-basis Hamiltonian mapper max Neyman shot floor differs from manifest")
        if summary.get("max_ansatz_two_qubit_gate_executions_at_neyman_target") != b3_larger_basis_hamiltonian_mapper.get(
            "max_ansatz_two_qubit_gate_executions_at_neyman_target"
        ):
            errors.append("B3 larger-basis Hamiltonian mapper max ansatz execution count differs from manifest")
        if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
            errors.append("B3 larger-basis Hamiltonian mapper must not claim denominator wins")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B3 larger-basis Hamiltonian mapper must not claim quantum advantage")
        if summary.get("reaction_dynamics_solution_claimed") is not False:
            errors.append("B3 larger-basis Hamiltonian mapper must not claim reaction dynamics solution")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B3 larger-basis Hamiltonian mapper validation errors must be zero")
        if len(rows) != b3_larger_basis_hamiltonian_mapper.get("reaction_coordinate_instances"):
            errors.append("B3 larger-basis Hamiltonian mapper row count differs from manifest")
        if any(row.get("larger_basis_quantum_mapper_included") is not True for row in rows):
            errors.append("B3 larger-basis Hamiltonian mapper rows must include mapper")
        if any(row.get("spin_orbital_qubits") != row.get("selected_ci_spin_orbital_qubits") for row in rows):
            errors.append("B3 larger-basis Hamiltonian mapper rows must match selected-CI qubits")
        if any(row.get("candidate_beats_selected_ci_larger_basis_denominator") is not False for row in rows):
            errors.append("B3 larger-basis Hamiltonian mapper rows must not claim denominator wins")

        b3_larger_basis_hamiltonian_mapper_status = {
            "status": b3_larger_basis_hamiltonian_mapper.get("status"),
            "method": b3_larger_basis_hamiltonian_mapper.get("method"),
            "reaction_coordinate_instances": b3_larger_basis_hamiltonian_mapper.get(
                "reaction_coordinate_instances"
            ),
            "larger_basis_quantum_mapper_included": summary.get("larger_basis_quantum_mapper_included"),
            "same_basis_as_selected_ci_denominator": summary.get("same_basis_as_selected_ci_denominator"),
            "pauli_measurement_cost_included": summary.get("pauli_measurement_cost_included"),
            "conservative_measurement_bucket_model": summary.get("conservative_measurement_bucket_model"),
            "ansatz_state_preparation_surcharge_included": summary.get(
                "ansatz_state_preparation_surcharge_included"
            ),
            "max_total_qubits": b3_larger_basis_hamiltonian_mapper.get("max_total_qubits"),
            "max_pauli_terms_after_cutoff": b3_larger_basis_hamiltonian_mapper.get(
                "max_pauli_terms_after_cutoff"
            ),
            "max_pauli_weight": b3_larger_basis_hamiltonian_mapper.get("max_pauli_weight"),
            "max_conservative_same_basis_bucket_count": b3_larger_basis_hamiltonian_mapper.get(
                "max_conservative_same_basis_bucket_count"
            ),
            "min_conservative_bucket_reduction_vs_ungrouped": b3_larger_basis_hamiltonian_mapper.get(
                "min_conservative_bucket_reduction_vs_ungrouped"
            ),
            "max_conservative_bucket_reduction_vs_ungrouped": b3_larger_basis_hamiltonian_mapper.get(
                "max_conservative_bucket_reduction_vs_ungrouped"
            ),
            "max_neyman_target_total_shot_floor": b3_larger_basis_hamiltonian_mapper.get(
                "max_neyman_target_total_shot_floor"
            ),
            "max_ansatz_two_qubit_gate_executions_at_neyman_target": b3_larger_basis_hamiltonian_mapper.get(
                "max_ansatz_two_qubit_gate_executions_at_neyman_target"
            ),
            "selected_ci_larger_basis_denominator_beaten_count": summary.get(
                "selected_ci_larger_basis_denominator_beaten_count"
            ),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "reaction_dynamics_solution_claimed": summary.get("reaction_dynamics_solution_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }

    b3_larger_basis_qwc_grouping_status = {}
    if not b3_larger_basis_qwc_grouping:
        warnings.append("B3 manifest has no larger-basis QWC grouping result")
    else:
        result_path = b3_larger_basis_qwc_grouping.get("result")
        markdown_path = b3_larger_basis_qwc_grouping.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B3 larger-basis QWC grouping result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B3 larger-basis QWC grouping markdown missing: {markdown_path}")

        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        rows = payload.get("rows", [])
        if payload.get("benchmark_id") != "B3":
            errors.append("B3 larger-basis QWC grouping payload must have benchmark_id B3")
        if payload.get("dependency_benchmark") != "B3":
            errors.append("B3 larger-basis QWC grouping dependency_benchmark must be B3")
        if payload.get("status") != b3_larger_basis_qwc_grouping.get("status"):
            errors.append("B3 larger-basis QWC grouping payload status differs from manifest")
        if payload.get("method") != b3_larger_basis_qwc_grouping.get("method"):
            errors.append("B3 larger-basis QWC grouping payload method differs from manifest")
        if payload.get("source_larger_basis_mapper_method") != "b3_larger_basis_hamiltonian_mapper_v0":
            errors.append("B3 larger-basis QWC grouping source mapper method changed")
        if summary.get("instance_count") != b3_larger_basis_qwc_grouping.get("reaction_coordinate_instances"):
            errors.append("B3 larger-basis QWC grouping instance count differs from manifest")
        if summary.get("larger_basis_quantum_mapper_included") is not True:
            errors.append("B3 larger-basis QWC grouping must include larger-basis mapper")
        if summary.get("qwc_grouping_included") is not True:
            errors.append("B3 larger-basis QWC grouping must include QWC grouping")
        if summary.get("qwc_grouping_algorithm") != b3_larger_basis_qwc_grouping.get("qwc_grouping_algorithm"):
            errors.append("B3 larger-basis QWC grouping algorithm differs from manifest")
        if summary.get("max_qwc_group_count") != b3_larger_basis_qwc_grouping.get("max_qwc_group_count"):
            errors.append("B3 larger-basis QWC grouping max group count differs from manifest")
        if summary.get("min_qwc_reduction_vs_previous_bucket_count") != b3_larger_basis_qwc_grouping.get(
            "min_qwc_reduction_vs_previous_bucket_count"
        ):
            errors.append("B3 larger-basis QWC grouping min reduction differs from manifest")
        if summary.get("max_qwc_reduction_vs_previous_bucket_count") != b3_larger_basis_qwc_grouping.get(
            "max_qwc_reduction_vs_previous_bucket_count"
        ):
            errors.append("B3 larger-basis QWC grouping max reduction differs from manifest")
        if summary.get("neyman_shot_floor_reduced_by_grouping") is not False:
            errors.append("B3 larger-basis QWC grouping must not claim shot-floor reduction")
        if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
            errors.append("B3 larger-basis QWC grouping must not claim denominator wins")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B3 larger-basis QWC grouping must not claim quantum advantage")
        if summary.get("reaction_dynamics_solution_claimed") is not False:
            errors.append("B3 larger-basis QWC grouping must not claim reaction dynamics solution")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B3 larger-basis QWC grouping validation errors must be zero")
        if len(rows) != b3_larger_basis_qwc_grouping.get("reaction_coordinate_instances"):
            errors.append("B3 larger-basis QWC grouping row count differs from manifest")
        if any(row.get("qwc_group_count", 0) >= row.get("previous_conservative_same_basis_bucket_count", 0) for row in rows):
            errors.append("B3 larger-basis QWC grouping rows must reduce previous bucket counts")
        if any(row.get("neyman_shot_floor_reduced_by_grouping") is not False for row in rows):
            errors.append("B3 larger-basis QWC grouping rows must not claim shot-floor reduction")
        if any(row.get("selected_ci_larger_basis_denominator_beaten") is not False for row in rows):
            errors.append("B3 larger-basis QWC grouping rows must not claim denominator wins")

        b3_larger_basis_qwc_grouping_status = {
            "status": b3_larger_basis_qwc_grouping.get("status"),
            "method": b3_larger_basis_qwc_grouping.get("method"),
            "reaction_coordinate_instances": b3_larger_basis_qwc_grouping.get("reaction_coordinate_instances"),
            "larger_basis_quantum_mapper_included": summary.get("larger_basis_quantum_mapper_included"),
            "qwc_grouping_included": summary.get("qwc_grouping_included"),
            "qwc_grouping_algorithm": summary.get("qwc_grouping_algorithm"),
            "max_total_qubits": b3_larger_basis_qwc_grouping.get("max_total_qubits"),
            "max_pauli_terms_after_cutoff": b3_larger_basis_qwc_grouping.get("max_pauli_terms_after_cutoff"),
            "max_previous_conservative_same_basis_bucket_count": b3_larger_basis_qwc_grouping.get(
                "max_previous_conservative_same_basis_bucket_count"
            ),
            "max_qwc_group_count": b3_larger_basis_qwc_grouping.get("max_qwc_group_count"),
            "min_qwc_reduction_vs_previous_bucket_count": b3_larger_basis_qwc_grouping.get(
                "min_qwc_reduction_vs_previous_bucket_count"
            ),
            "max_qwc_reduction_vs_previous_bucket_count": b3_larger_basis_qwc_grouping.get(
                "max_qwc_reduction_vs_previous_bucket_count"
            ),
            "max_group_size": b3_larger_basis_qwc_grouping.get("max_group_size"),
            "max_neyman_target_total_shot_floor": b3_larger_basis_qwc_grouping.get(
                "max_neyman_target_total_shot_floor"
            ),
            "neyman_shot_floor_reduced_by_grouping": summary.get("neyman_shot_floor_reduced_by_grouping"),
            "max_ansatz_two_qubit_gate_executions_at_neyman_target": b3_larger_basis_qwc_grouping.get(
                "max_ansatz_two_qubit_gate_executions_at_neyman_target"
            ),
            "selected_ci_larger_basis_denominator_beaten_count": summary.get(
                "selected_ci_larger_basis_denominator_beaten_count"
            ),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "reaction_dynamics_solution_claimed": summary.get("reaction_dynamics_solution_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }

    b3_grouped_covariance_shot_floor_status = {}
    if not b3_grouped_covariance_shot_floor:
        warnings.append("B3 manifest has no grouped covariance shot-floor result")
    else:
        result_path = b3_grouped_covariance_shot_floor.get("result")
        markdown_path = b3_grouped_covariance_shot_floor.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B3 grouped covariance shot-floor result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B3 grouped covariance shot-floor markdown missing: {markdown_path}")

        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        rows = payload.get("rows", [])
        if payload.get("benchmark_id") != "B3":
            errors.append("B3 grouped covariance shot-floor payload must have benchmark_id B3")
        if payload.get("dependency_benchmark") != "B3":
            errors.append("B3 grouped covariance shot-floor dependency_benchmark must be B3")
        if payload.get("status") != b3_grouped_covariance_shot_floor.get("status"):
            errors.append("B3 grouped covariance shot-floor payload status differs from manifest")
        if payload.get("method") != b3_grouped_covariance_shot_floor.get("method"):
            errors.append("B3 grouped covariance shot-floor payload method differs from manifest")
        if payload.get("source_larger_basis_mapper_method") != "b3_larger_basis_hamiltonian_mapper_v0":
            errors.append("B3 grouped covariance shot-floor source mapper method changed")
        if payload.get("source_larger_basis_qwc_grouping_method") != "b3_larger_basis_qwc_grouping_v0":
            errors.append("B3 grouped covariance shot-floor source QWC grouping method changed")
        if summary.get("instance_count") != b3_grouped_covariance_shot_floor.get(
            "reaction_coordinate_instances"
        ):
            errors.append("B3 grouped covariance shot-floor instance count differs from manifest")
        if summary.get("larger_basis_quantum_mapper_included") is not True:
            errors.append("B3 grouped covariance shot-floor must include larger-basis mapper")
        if summary.get("qwc_grouping_included") is not True:
            errors.append("B3 grouped covariance shot-floor must include QWC grouping")
        if summary.get("grouped_covariance_included") is not True:
            errors.append("B3 grouped covariance shot-floor must include grouped covariance")
        if summary.get("qwc_grouping_algorithm") != b3_grouped_covariance_shot_floor.get(
            "qwc_grouping_algorithm"
        ):
            errors.append("B3 grouped covariance shot-floor algorithm differs from manifest")
        if summary.get("covariance_model") != b3_grouped_covariance_shot_floor.get("covariance_model"):
            errors.append("B3 grouped covariance shot-floor covariance model differs from manifest")
        if summary.get("max_qwc_group_count") != b3_grouped_covariance_shot_floor.get(
            "max_qwc_group_count"
        ):
            errors.append("B3 grouped covariance shot-floor max QWC group count differs from manifest")
        if summary.get("max_previous_independent_term_neyman_shot_floor") != b3_grouped_covariance_shot_floor.get(
            "max_previous_independent_term_neyman_shot_floor"
        ):
            errors.append("B3 grouped covariance shot-floor previous shot floor differs from manifest")
        if summary.get("max_grouped_covariance_shot_floor") != b3_grouped_covariance_shot_floor.get(
            "max_grouped_covariance_shot_floor"
        ):
            errors.append("B3 grouped covariance shot-floor grouped shot floor differs from manifest")
        if summary.get(
            "min_grouped_covariance_reduction_vs_previous_independent_floor"
        ) != b3_grouped_covariance_shot_floor.get(
            "min_grouped_covariance_reduction_vs_previous_independent_floor"
        ):
            errors.append("B3 grouped covariance shot-floor min reduction differs from manifest")
        if summary.get(
            "max_grouped_covariance_reduction_vs_previous_independent_floor"
        ) != b3_grouped_covariance_shot_floor.get(
            "max_grouped_covariance_reduction_vs_previous_independent_floor"
        ):
            errors.append("B3 grouped covariance shot-floor max reduction differs from manifest")
        if summary.get("max_nonzero_covariance_pair_count") != b3_grouped_covariance_shot_floor.get(
            "max_nonzero_covariance_pair_count"
        ):
            errors.append("B3 grouped covariance shot-floor covariance-pair count differs from manifest")
        if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
            errors.append("B3 grouped covariance shot-floor must not claim denominator wins")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B3 grouped covariance shot-floor must not claim quantum advantage")
        if summary.get("reaction_dynamics_solution_claimed") is not False:
            errors.append("B3 grouped covariance shot-floor must not claim reaction dynamics solution")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B3 grouped covariance shot-floor validation errors must be zero")
        if len(rows) != b3_grouped_covariance_shot_floor.get("reaction_coordinate_instances"):
            errors.append("B3 grouped covariance shot-floor row count differs from manifest")
        if any(row.get("qwc_group_count_matches_source") is not True for row in rows):
            errors.append("B3 grouped covariance shot-floor rows must match source QWC group counts")
        if any(
            row.get("grouped_covariance_shot_floor", 0)
            >= row.get("previous_independent_term_neyman_shot_floor", 0)
            for row in rows
        ):
            errors.append("B3 grouped covariance shot-floor rows must reduce independent shot floors")
        if any(row.get("selected_ci_larger_basis_denominator_beaten") is not False for row in rows):
            errors.append("B3 grouped covariance shot-floor rows must not claim denominator wins")

        b3_grouped_covariance_shot_floor_status = {
            "status": b3_grouped_covariance_shot_floor.get("status"),
            "method": b3_grouped_covariance_shot_floor.get("method"),
            "reaction_coordinate_instances": b3_grouped_covariance_shot_floor.get(
                "reaction_coordinate_instances"
            ),
            "larger_basis_quantum_mapper_included": summary.get("larger_basis_quantum_mapper_included"),
            "qwc_grouping_included": summary.get("qwc_grouping_included"),
            "qwc_grouping_algorithm": summary.get("qwc_grouping_algorithm"),
            "grouped_covariance_included": summary.get("grouped_covariance_included"),
            "covariance_model": summary.get("covariance_model"),
            "max_total_qubits": b3_grouped_covariance_shot_floor.get("max_total_qubits"),
            "max_pauli_terms_after_cutoff": b3_grouped_covariance_shot_floor.get(
                "max_pauli_terms_after_cutoff"
            ),
            "max_qwc_group_count": b3_grouped_covariance_shot_floor.get("max_qwc_group_count"),
            "max_previous_independent_term_neyman_shot_floor": b3_grouped_covariance_shot_floor.get(
                "max_previous_independent_term_neyman_shot_floor"
            ),
            "max_grouped_covariance_shot_floor": b3_grouped_covariance_shot_floor.get(
                "max_grouped_covariance_shot_floor"
            ),
            "min_grouped_covariance_reduction_vs_previous_independent_floor": b3_grouped_covariance_shot_floor.get(
                "min_grouped_covariance_reduction_vs_previous_independent_floor"
            ),
            "max_grouped_covariance_reduction_vs_previous_independent_floor": b3_grouped_covariance_shot_floor.get(
                "max_grouped_covariance_reduction_vs_previous_independent_floor"
            ),
            "max_nonzero_covariance_pair_count": b3_grouped_covariance_shot_floor.get(
                "max_nonzero_covariance_pair_count"
            ),
            "max_ansatz_two_qubit_gate_executions_at_grouped_covariance_target": b3_grouped_covariance_shot_floor.get(
                "max_ansatz_two_qubit_gate_executions_at_grouped_covariance_target"
            ),
            "selected_ci_larger_basis_denominator_beaten_count": summary.get(
                "selected_ci_larger_basis_denominator_beaten_count"
            ),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "reaction_dynamics_solution_claimed": summary.get("reaction_dynamics_solution_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }

    b3_chemical_state_prep_derivative_status = {}
    if not b3_chemical_state_prep_derivative:
        warnings.append("B3 manifest has no chemical state-prep derivative boundary result")
    else:
        result_path = b3_chemical_state_prep_derivative.get("result")
        markdown_path = b3_chemical_state_prep_derivative.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B3 chemical state-prep derivative result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B3 chemical state-prep derivative markdown missing: {markdown_path}")

        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        rows = payload.get("rows", [])
        if payload.get("benchmark_id") != "B3":
            errors.append("B3 chemical state-prep derivative payload must have benchmark_id B3")
        if payload.get("dependency_benchmark") != "B3":
            errors.append("B3 chemical state-prep derivative dependency_benchmark must be B3")
        if payload.get("status") != b3_chemical_state_prep_derivative.get("status"):
            errors.append("B3 chemical state-prep derivative payload status differs from manifest")
        if payload.get("method") != b3_chemical_state_prep_derivative.get("method"):
            errors.append("B3 chemical state-prep derivative payload method differs from manifest")
        if payload.get("source_grouped_covariance_method") != "b3_grouped_covariance_shot_floor_v0":
            errors.append("B3 chemical state-prep derivative source grouped covariance method changed")
        if payload.get("source_selected_ci_method") != "b3_selected_ci_grouped_pauli_boundary_v0":
            errors.append("B3 chemical state-prep derivative source selected-CI method changed")
        if payload.get("source_larger_basis_mapper_method") != "b3_larger_basis_hamiltonian_mapper_v0":
            errors.append("B3 chemical state-prep derivative source mapper method changed")
        if summary.get("instance_count") != b3_chemical_state_prep_derivative.get(
            "reaction_coordinate_instances"
        ):
            errors.append("B3 chemical state-prep derivative instance count differs from manifest")
        if summary.get("derivative_error_propagation_included") is not True:
            errors.append("B3 chemical state-prep derivative must include derivative propagation")
        if summary.get("sampled_chemical_state_covariance_included") is not False:
            errors.append("B3 chemical state-prep derivative must not claim sampled chemical covariance")
        if summary.get("chemical_state_prep_cost_envelope_included") is not True:
            errors.append("B3 chemical state-prep derivative must include prep cost envelope")
        if summary.get("chemical_state_prep_models") != b3_chemical_state_prep_derivative.get(
            "chemical_state_prep_models"
        ):
            errors.append("B3 chemical state-prep derivative prep model list differs from manifest")
        if summary.get("max_source_grouped_covariance_shot_floor") != b3_chemical_state_prep_derivative.get(
            "max_source_grouped_covariance_shot_floor"
        ):
            errors.append("B3 chemical state-prep derivative source shot floor differs from manifest")
        if summary.get("max_three_point_derivative_total_shot_floor") != b3_chemical_state_prep_derivative.get(
            "max_three_point_derivative_total_shot_floor"
        ):
            errors.append("B3 chemical state-prep derivative total shot floor differs from manifest")
        if summary.get(
            "min_derivative_shot_floor_inflation_vs_center_energy_floor"
        ) != b3_chemical_state_prep_derivative.get(
            "min_derivative_shot_floor_inflation_vs_center_energy_floor"
        ):
            errors.append("B3 chemical state-prep derivative min inflation differs from manifest")
        if summary.get(
            "max_derivative_shot_floor_inflation_vs_center_energy_floor"
        ) != b3_chemical_state_prep_derivative.get(
            "max_derivative_shot_floor_inflation_vs_center_energy_floor"
        ):
            errors.append("B3 chemical state-prep derivative max inflation differs from manifest")
        if summary.get("max_uccsd_two_qubit_gates_per_preparation") != b3_chemical_state_prep_derivative.get(
            "max_uccsd_two_qubit_gates_per_preparation"
        ):
            errors.append("B3 chemical state-prep derivative UCCSD prep cost differs from manifest")
        if summary.get("max_adapt_two_qubit_gates_per_preparation") != b3_chemical_state_prep_derivative.get(
            "max_adapt_two_qubit_gates_per_preparation"
        ):
            errors.append("B3 chemical state-prep derivative ADAPT prep cost differs from manifest")
        if summary.get(
            "max_adiabatic_two_qubit_gates_per_preparation"
        ) != b3_chemical_state_prep_derivative.get("max_adiabatic_two_qubit_gates_per_preparation"):
            errors.append("B3 chemical state-prep derivative adiabatic prep cost differs from manifest")
        if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
            errors.append("B3 chemical state-prep derivative must not claim denominator wins")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B3 chemical state-prep derivative must not claim quantum advantage")
        if summary.get("reaction_dynamics_solution_claimed") is not False:
            errors.append("B3 chemical state-prep derivative must not claim reaction dynamics solution")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B3 chemical state-prep derivative validation errors must be zero")
        if len(rows) != b3_chemical_state_prep_derivative.get("reaction_coordinate_instances"):
            errors.append("B3 chemical state-prep derivative row count differs from manifest")
        if any(row.get("derivative_error_propagation_included") is not True for row in rows):
            errors.append("B3 chemical state-prep derivative rows must include derivative propagation")
        if any(row.get("sampled_chemical_state_covariance_included") is not False for row in rows):
            errors.append("B3 chemical state-prep derivative rows must not claim sampled chemical covariance")
        if any(
            row.get("derivative_shot_floor", {}).get("three_point_derivative_total_shot_floor", 0)
            <= row.get("source_grouped_covariance_shot_floor", 0)
            for row in rows
        ):
            errors.append("B3 chemical state-prep derivative rows must inflate derivative shot floors")
        if any(row.get("candidate_beats_selected_ci_larger_basis_denominator") is not False for row in rows):
            errors.append("B3 chemical state-prep derivative rows must not claim denominator wins")

        b3_chemical_state_prep_derivative_status = {
            "status": b3_chemical_state_prep_derivative.get("status"),
            "method": b3_chemical_state_prep_derivative.get("method"),
            "reaction_coordinate_instances": b3_chemical_state_prep_derivative.get(
                "reaction_coordinate_instances"
            ),
            "derivative_error_propagation_included": summary.get(
                "derivative_error_propagation_included"
            ),
            "sampled_chemical_state_covariance_included": summary.get(
                "sampled_chemical_state_covariance_included"
            ),
            "chemical_state_prep_cost_envelope_included": summary.get(
                "chemical_state_prep_cost_envelope_included"
            ),
            "chemical_state_prep_models": summary.get("chemical_state_prep_models"),
            "max_total_qubits": b3_chemical_state_prep_derivative.get("max_total_qubits"),
            "max_source_grouped_covariance_shot_floor": b3_chemical_state_prep_derivative.get(
                "max_source_grouped_covariance_shot_floor"
            ),
            "max_three_point_derivative_total_shot_floor": b3_chemical_state_prep_derivative.get(
                "max_three_point_derivative_total_shot_floor"
            ),
            "min_derivative_shot_floor_inflation_vs_center_energy_floor": b3_chemical_state_prep_derivative.get(
                "min_derivative_shot_floor_inflation_vs_center_energy_floor"
            ),
            "max_derivative_shot_floor_inflation_vs_center_energy_floor": b3_chemical_state_prep_derivative.get(
                "max_derivative_shot_floor_inflation_vs_center_energy_floor"
            ),
            "max_uccsd_two_qubit_gates_per_preparation": b3_chemical_state_prep_derivative.get(
                "max_uccsd_two_qubit_gates_per_preparation"
            ),
            "max_adapt_two_qubit_gates_per_preparation": b3_chemical_state_prep_derivative.get(
                "max_adapt_two_qubit_gates_per_preparation"
            ),
            "max_adiabatic_two_qubit_gates_per_preparation": b3_chemical_state_prep_derivative.get(
                "max_adiabatic_two_qubit_gates_per_preparation"
            ),
            "max_uccsd_two_qubit_gate_executions_at_derivative_target": b3_chemical_state_prep_derivative.get(
                "max_uccsd_two_qubit_gate_executions_at_derivative_target"
            ),
            "max_adapt_two_qubit_gate_executions_at_derivative_target": b3_chemical_state_prep_derivative.get(
                "max_adapt_two_qubit_gate_executions_at_derivative_target"
            ),
            "max_adiabatic_two_qubit_gate_executions_at_derivative_target": b3_chemical_state_prep_derivative.get(
                "max_adiabatic_two_qubit_gate_executions_at_derivative_target"
            ),
            "selected_ci_larger_basis_denominator_beaten_count": summary.get(
                "selected_ci_larger_basis_denominator_beaten_count"
            ),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "reaction_dynamics_solution_claimed": summary.get("reaction_dynamics_solution_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }

    b3_compiled_ucc_adapt_covariance_status = {}
    if not b3_compiled_ucc_adapt_covariance:
        warnings.append("B3 manifest has no compiled UCC/ADAPT covariance pilot result")
    else:
        result_path = b3_compiled_ucc_adapt_covariance.get("result")
        markdown_path = b3_compiled_ucc_adapt_covariance.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B3 compiled UCC/ADAPT covariance result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B3 compiled UCC/ADAPT covariance markdown missing: {markdown_path}")

        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        rows = payload.get("rows", [])
        if payload.get("benchmark_id") != "B3":
            errors.append("B3 compiled UCC/ADAPT covariance payload must have benchmark_id B3")
        if payload.get("dependency_benchmark") != "B3":
            errors.append("B3 compiled UCC/ADAPT covariance dependency_benchmark must be B3")
        if payload.get("status") != b3_compiled_ucc_adapt_covariance.get("status"):
            errors.append("B3 compiled UCC/ADAPT covariance payload status differs from manifest")
        if payload.get("method") != b3_compiled_ucc_adapt_covariance.get("method"):
            errors.append("B3 compiled UCC/ADAPT covariance payload method differs from manifest")
        if payload.get("source_derivative_boundary_method") != "b3_chemical_state_prep_derivative_boundary_v0":
            errors.append("B3 compiled UCC/ADAPT covariance source derivative method changed")
        if summary.get("instance_count") != b3_compiled_ucc_adapt_covariance.get("pilot_instances"):
            errors.append("B3 compiled UCC/ADAPT covariance pilot instance count differs from manifest")
        if summary.get("molecule") != b3_compiled_ucc_adapt_covariance.get("pilot_molecule"):
            errors.append("B3 compiled UCC/ADAPT covariance pilot molecule differs from manifest")
        if summary.get("compiled_ucc_adapt_covariance_included") is not True:
            errors.append("B3 compiled UCC/ADAPT covariance must include compiled covariance")
        if summary.get("pilot_sampled_covariance_included") is not True:
            errors.append("B3 compiled UCC/ADAPT covariance must include sampled covariance")
        if summary.get("optimizer_loop_shot_accounting_included") is not True:
            errors.append("B3 compiled UCC/ADAPT covariance must include optimizer-loop accounting")
        if summary.get("converged_vqe_or_adapt_energy") is not False:
            errors.append("B3 compiled UCC/ADAPT covariance must not claim converged VQE/ADAPT energy")
        if summary.get("pilot_group_count") != b3_compiled_ucc_adapt_covariance.get("pilot_group_count"):
            errors.append("B3 compiled UCC/ADAPT covariance pilot group count differs from manifest")
        if summary.get("pilot_max_basis_weight") != b3_compiled_ucc_adapt_covariance.get(
            "pilot_max_basis_weight"
        ):
            errors.append("B3 compiled UCC/ADAPT covariance pilot basis-weight cap differs from manifest")
        if summary.get("pilot_shots_per_group") != b3_compiled_ucc_adapt_covariance.get(
            "pilot_shots_per_group"
        ):
            errors.append("B3 compiled UCC/ADAPT covariance pilot shots differ from manifest")
        if summary.get("pilot_max_relative_variance_error") != b3_compiled_ucc_adapt_covariance.get(
            "pilot_max_relative_variance_error"
        ):
            errors.append("B3 compiled UCC/ADAPT covariance pilot max variance error differs from manifest")
        if summary.get("compiled_state_center_grouped_covariance_shot_floor") != b3_compiled_ucc_adapt_covariance.get(
            "compiled_state_center_grouped_covariance_shot_floor"
        ):
            errors.append("B3 compiled UCC/ADAPT covariance center floor differs from manifest")
        if summary.get("compiled_state_three_point_derivative_shot_floor") != b3_compiled_ucc_adapt_covariance.get(
            "compiled_state_three_point_derivative_shot_floor"
        ):
            errors.append("B3 compiled UCC/ADAPT covariance derivative floor differs from manifest")
        if summary.get("optimizer_loop_total_shots") != b3_compiled_ucc_adapt_covariance.get(
            "optimizer_loop_total_shots"
        ):
            errors.append("B3 compiled UCC/ADAPT covariance optimizer shots differ from manifest")
        if summary.get("optimizer_loop_two_qubit_executions") != b3_compiled_ucc_adapt_covariance.get(
            "optimizer_loop_two_qubit_executions"
        ):
            errors.append("B3 compiled UCC/ADAPT covariance optimizer 2Q executions differ from manifest")
        if summary.get("optimizer_loop_total_shots", 0) <= summary.get(
            "compiled_state_three_point_derivative_shot_floor", 0
        ):
            errors.append("B3 compiled UCC/ADAPT covariance optimizer loop must add shot overhead")
        if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
            errors.append("B3 compiled UCC/ADAPT covariance must not claim denominator wins")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B3 compiled UCC/ADAPT covariance must not claim quantum advantage")
        if summary.get("reaction_dynamics_solution_claimed") is not False:
            errors.append("B3 compiled UCC/ADAPT covariance must not claim reaction dynamics solution")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B3 compiled UCC/ADAPT covariance validation errors must be zero")
        if len(rows) != b3_compiled_ucc_adapt_covariance.get("pilot_instances"):
            errors.append("B3 compiled UCC/ADAPT covariance row count differs from manifest")
        if any(row.get("pilot_sampled_covariance_included") is not True for row in rows):
            errors.append("B3 compiled UCC/ADAPT covariance rows must include sampled covariance")
        if any(row.get("candidate_beats_selected_ci_larger_basis_denominator") is not False for row in rows):
            errors.append("B3 compiled UCC/ADAPT covariance rows must not claim denominator wins")

        b3_compiled_ucc_adapt_covariance_status = {
            "status": b3_compiled_ucc_adapt_covariance.get("status"),
            "method": b3_compiled_ucc_adapt_covariance.get("method"),
            "pilot_instances": b3_compiled_ucc_adapt_covariance.get("pilot_instances"),
            "pilot_molecule": b3_compiled_ucc_adapt_covariance.get("pilot_molecule"),
            "ansatz_model": summary.get("ansatz_model"),
            "ansatz_parameter_count": summary.get("ansatz_parameter_count"),
            "compiled_ucc_adapt_covariance_included": summary.get(
                "compiled_ucc_adapt_covariance_included"
            ),
            "pilot_sampled_covariance_included": summary.get("pilot_sampled_covariance_included"),
            "optimizer_loop_shot_accounting_included": summary.get(
                "optimizer_loop_shot_accounting_included"
            ),
            "converged_vqe_or_adapt_energy": summary.get("converged_vqe_or_adapt_energy"),
            "pilot_group_count": b3_compiled_ucc_adapt_covariance.get("pilot_group_count"),
            "pilot_max_basis_weight": b3_compiled_ucc_adapt_covariance.get("pilot_max_basis_weight"),
            "pilot_shots_per_group": b3_compiled_ucc_adapt_covariance.get("pilot_shots_per_group"),
            "pilot_total_group_measurement_shots": b3_compiled_ucc_adapt_covariance.get(
                "pilot_total_group_measurement_shots"
            ),
            "pilot_mean_relative_variance_error": b3_compiled_ucc_adapt_covariance.get(
                "pilot_mean_relative_variance_error"
            ),
            "pilot_max_relative_variance_error": b3_compiled_ucc_adapt_covariance.get(
                "pilot_max_relative_variance_error"
            ),
            "compiled_two_qubit_gates_per_preparation": b3_compiled_ucc_adapt_covariance.get(
                "compiled_two_qubit_gates_per_preparation"
            ),
            "source_hf_center_grouped_covariance_shot_floor": b3_compiled_ucc_adapt_covariance.get(
                "source_hf_center_grouped_covariance_shot_floor"
            ),
            "compiled_state_center_grouped_covariance_shot_floor": b3_compiled_ucc_adapt_covariance.get(
                "compiled_state_center_grouped_covariance_shot_floor"
            ),
            "source_hf_three_point_derivative_shot_floor": b3_compiled_ucc_adapt_covariance.get(
                "source_hf_three_point_derivative_shot_floor"
            ),
            "compiled_state_three_point_derivative_shot_floor": b3_compiled_ucc_adapt_covariance.get(
                "compiled_state_three_point_derivative_shot_floor"
            ),
            "optimizer_evaluation_multiplier": b3_compiled_ucc_adapt_covariance.get(
                "optimizer_evaluation_multiplier"
            ),
            "optimizer_loop_total_shots": b3_compiled_ucc_adapt_covariance.get(
                "optimizer_loop_total_shots"
            ),
            "optimizer_loop_two_qubit_executions": b3_compiled_ucc_adapt_covariance.get(
                "optimizer_loop_two_qubit_executions"
            ),
            "selected_ci_larger_basis_denominator_beaten_count": summary.get(
                "selected_ci_larger_basis_denominator_beaten_count"
            ),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "reaction_dynamics_solution_claimed": summary.get("reaction_dynamics_solution_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }

    b3_cross_molecule_ucc_adapt_pressure_status = {}
    if not b3_cross_molecule_ucc_adapt_pressure:
        warnings.append("B3 manifest has no cross-molecule UCC/ADAPT pressure result")
    else:
        result_path = b3_cross_molecule_ucc_adapt_pressure.get("result")
        markdown_path = b3_cross_molecule_ucc_adapt_pressure.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B3 cross-molecule UCC/ADAPT pressure result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B3 cross-molecule UCC/ADAPT pressure markdown missing: {markdown_path}")

        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        rows = payload.get("rows", [])
        if payload.get("benchmark_id") != "B3":
            errors.append("B3 cross-molecule UCC/ADAPT pressure payload must have benchmark_id B3")
        if payload.get("dependency_benchmark") != "B3":
            errors.append("B3 cross-molecule UCC/ADAPT pressure dependency_benchmark must be B3")
        if payload.get("status") != b3_cross_molecule_ucc_adapt_pressure.get("status"):
            errors.append("B3 cross-molecule UCC/ADAPT pressure payload status differs from manifest")
        if payload.get("method") != b3_cross_molecule_ucc_adapt_pressure.get("method"):
            errors.append("B3 cross-molecule UCC/ADAPT pressure payload method differs from manifest")
        if payload.get("source_derivative_boundary_method") != "b3_chemical_state_prep_derivative_boundary_v0":
            errors.append("B3 cross-molecule UCC/ADAPT pressure source derivative method changed")
        if payload.get("source_grouped_covariance_method") != "b3_grouped_covariance_shot_floor_v0":
            errors.append("B3 cross-molecule UCC/ADAPT pressure source grouped covariance method changed")
        if payload.get("source_compiled_ucc_adapt_pilot_method") != "b3_compiled_ucc_adapt_covariance_pilot_v0":
            errors.append("B3 cross-molecule UCC/ADAPT pressure source compiled pilot method changed")
        if summary.get("instance_count") != b3_cross_molecule_ucc_adapt_pressure.get("pressure_instances"):
            errors.append("B3 cross-molecule UCC/ADAPT pressure instance count differs from manifest")
        if summary.get("molecule_count") != b3_cross_molecule_ucc_adapt_pressure.get("molecule_count"):
            errors.append("B3 cross-molecule UCC/ADAPT pressure molecule count differs from manifest")
        if summary.get("compiled_ucc_adapt_sampled_covariance_extended") is not True:
            errors.append("B3 cross-molecule UCC/ADAPT pressure must extend sampled covariance")
        if summary.get("full_compiled_state_covariance_computed") is not False:
            errors.append("B3 cross-molecule UCC/ADAPT pressure must not claim full compiled covariance")
        if summary.get("converged_vqe_or_adapt_energy") is not False:
            errors.append("B3 cross-molecule UCC/ADAPT pressure must not claim converged VQE/ADAPT")
        if summary.get("pilot_group_count_total") != b3_cross_molecule_ucc_adapt_pressure.get(
            "pilot_group_count_total"
        ):
            errors.append("B3 cross-molecule UCC/ADAPT pressure pilot group total differs from manifest")
        if summary.get("pilot_max_terms_per_molecule") != b3_cross_molecule_ucc_adapt_pressure.get(
            "pilot_max_terms_per_molecule"
        ):
            errors.append("B3 cross-molecule UCC/ADAPT pressure term cap differs from manifest")
        if summary.get("pilot_max_basis_weight") != b3_cross_molecule_ucc_adapt_pressure.get(
            "pilot_max_basis_weight"
        ):
            errors.append("B3 cross-molecule UCC/ADAPT pressure basis cap differs from manifest")
        if summary.get("pilot_shots_per_group") != b3_cross_molecule_ucc_adapt_pressure.get(
            "pilot_shots_per_group"
        ):
            errors.append("B3 cross-molecule UCC/ADAPT pressure shots/group differs from manifest")
        if summary.get("max_optimizer_loop_total_shots_lower_bound") != b3_cross_molecule_ucc_adapt_pressure.get(
            "max_optimizer_loop_total_shots_lower_bound"
        ):
            errors.append("B3 cross-molecule UCC/ADAPT pressure optimizer shots differ from manifest")
        if summary.get("max_optimizer_loop_two_qubit_executions_lower_bound") != b3_cross_molecule_ucc_adapt_pressure.get(
            "max_optimizer_loop_two_qubit_executions_lower_bound"
        ):
            errors.append("B3 cross-molecule UCC/ADAPT pressure optimizer 2Q differs from manifest")
        if summary.get("max_optimizer_loop_total_shots_lower_bound", 0) <= 10**13:
            errors.append("B3 cross-molecule UCC/ADAPT pressure should expose prohibitive optimizer shots")
        if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
            errors.append("B3 cross-molecule UCC/ADAPT pressure must not claim denominator wins")
        if summary.get("demotion_recommended") is not True:
            errors.append("B3 cross-molecule UCC/ADAPT pressure should recommend demotion")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B3 cross-molecule UCC/ADAPT pressure must not claim quantum advantage")
        if summary.get("reaction_dynamics_solution_claimed") is not False:
            errors.append("B3 cross-molecule UCC/ADAPT pressure must not claim reaction dynamics solution")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B3 cross-molecule UCC/ADAPT pressure validation errors must be zero")
        if len(rows) != b3_cross_molecule_ucc_adapt_pressure.get("pressure_instances"):
            errors.append("B3 cross-molecule UCC/ADAPT pressure row count differs from manifest")
        if any(row.get("pilot_sampled_covariance_included") is not True for row in rows):
            errors.append("B3 cross-molecule UCC/ADAPT pressure rows must include sampled covariance")
        if any(row.get("full_compiled_state_covariance_computed") is not False for row in rows):
            errors.append("B3 cross-molecule UCC/ADAPT pressure rows must not claim full covariance")
        if any(row.get("candidate_beats_selected_ci_larger_basis_denominator") is not False for row in rows):
            errors.append("B3 cross-molecule UCC/ADAPT pressure rows must not claim denominator wins")

        b3_cross_molecule_ucc_adapt_pressure_status = {
            "status": b3_cross_molecule_ucc_adapt_pressure.get("status"),
            "method": b3_cross_molecule_ucc_adapt_pressure.get("method"),
            "pressure_instances": b3_cross_molecule_ucc_adapt_pressure.get("pressure_instances"),
            "molecule_count": b3_cross_molecule_ucc_adapt_pressure.get("molecule_count"),
            "ansatz_model": summary.get("ansatz_model"),
            "ansatz_parameter_count": summary.get("ansatz_parameter_count"),
            "compiled_ucc_adapt_sampled_covariance_extended": summary.get(
                "compiled_ucc_adapt_sampled_covariance_extended"
            ),
            "full_compiled_state_covariance_computed": summary.get(
                "full_compiled_state_covariance_computed"
            ),
            "converged_vqe_or_adapt_energy": summary.get("converged_vqe_or_adapt_energy"),
            "pilot_groups_per_molecule": b3_cross_molecule_ucc_adapt_pressure.get(
                "pilot_groups_per_molecule"
            ),
            "pilot_max_terms_per_molecule": b3_cross_molecule_ucc_adapt_pressure.get(
                "pilot_max_terms_per_molecule"
            ),
            "pilot_group_count_total": b3_cross_molecule_ucc_adapt_pressure.get(
                "pilot_group_count_total"
            ),
            "pilot_max_basis_weight": b3_cross_molecule_ucc_adapt_pressure.get(
                "pilot_max_basis_weight"
            ),
            "pilot_shots_per_group": b3_cross_molecule_ucc_adapt_pressure.get(
                "pilot_shots_per_group"
            ),
            "pilot_total_group_measurement_shots": b3_cross_molecule_ucc_adapt_pressure.get(
                "pilot_total_group_measurement_shots"
            ),
            "pilot_mean_relative_variance_error_across_molecules": b3_cross_molecule_ucc_adapt_pressure.get(
                "pilot_mean_relative_variance_error_across_molecules"
            ),
            "pilot_max_relative_variance_error_across_molecules": b3_cross_molecule_ucc_adapt_pressure.get(
                "pilot_max_relative_variance_error_across_molecules"
            ),
            "optimizer_loop_shot_accounting_included": summary.get(
                "optimizer_loop_shot_accounting_included"
            ),
            "optimizer_evaluation_multiplier": b3_cross_molecule_ucc_adapt_pressure.get(
                "optimizer_evaluation_multiplier"
            ),
            "max_optimizer_loop_total_shots_lower_bound": b3_cross_molecule_ucc_adapt_pressure.get(
                "max_optimizer_loop_total_shots_lower_bound"
            ),
            "max_optimizer_loop_two_qubit_executions_lower_bound": b3_cross_molecule_ucc_adapt_pressure.get(
                "max_optimizer_loop_two_qubit_executions_lower_bound"
            ),
            "selected_ci_larger_basis_denominator_beaten_count": summary.get(
                "selected_ci_larger_basis_denominator_beaten_count"
            ),
            "demotion_recommended": summary.get("demotion_recommended"),
            "b3_status_recommendation": summary.get("b3_status_recommendation"),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "reaction_dynamics_solution_claimed": summary.get("reaction_dynamics_solution_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }

    def audit_late_bound_contract(entry, label):
        status = {}
        if not entry:
            warnings.append(f"{label} manifest has no late-bound private challenge contract gate")
            return status
        result_path = entry.get("result")
        markdown_path = entry.get("markdown_report")
        skeleton_dir = entry.get("public_skeleton_directory")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        skeleton_dir_exists = bool(skeleton_dir and path_exists_from(benchmarks, skeleton_dir))
        if not result_exists:
            errors.append(f"{label} late-bound contract result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"{label} late-bound contract markdown missing: {markdown_path}")
        if not skeleton_dir_exists:
            errors.append(f"{label} late-bound contract skeleton directory missing: {skeleton_dir}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        status = {
            "status": entry.get("status"),
            "method": entry.get("method"),
            "packet_circuit_count": payload.get("packet_circuit_count"),
            "public_skeleton_file_count": payload.get("public_skeleton_file_count"),
            "public_skeletons_hide_private_material": payload.get("public_skeletons_hide_private_material"),
            "public_data_transcript_classically_predictable": payload.get(
                "public_data_transcript_classically_predictable"
            ),
            "late_bound_private_challenge_alone_sufficient_for_soundness": payload.get(
                "late_bound_private_challenge_alone_sufficient_for_soundness"
            ),
            "passed_gate_count": payload.get("passed_gate_count"),
            "failed_gate_count": payload.get("failed_gate_count"),
            "hardware_execution_performed": payload.get("hardware_execution_performed"),
            "quantum_advantage_claimed": payload.get("quantum_advantage_claimed"),
            "bqp_separation_claimed": payload.get("bqp_separation_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "public_skeleton_directory_exists": skeleton_dir_exists,
            "result": result_path,
            "markdown_report": markdown_path,
            "public_skeleton_directory": skeleton_dir,
        }
        if payload.get("benchmark_id") != "B4_B8":
            errors.append(f"{label} late-bound contract benchmark_id must be B4_B8")
        if payload.get("status") != entry.get("status"):
            errors.append(f"{label} late-bound contract status mismatch")
        if payload.get("method") != entry.get("method"):
            errors.append(f"{label} late-bound contract method mismatch")
        for field in [
            "packet_circuit_count",
            "public_skeleton_file_count",
            "source_private_material_embedded_file_count",
            "public_skeleton_private_material_embedded_file_count",
            "public_skeletons_hide_private_material",
            "public_data_transcript_classically_predictable",
            "late_bound_private_challenge_contract_defined",
            "late_bound_private_challenge_alone_sufficient_for_soundness",
            "non_stabilizer_or_hardware_entropy_source_present",
            "real_backend_or_hardware_execution_present",
            "acceptance_gate_count",
            "passed_gate_count",
            "failed_gate_count",
            "hardware_execution_performed",
            "real_backend_properties_used",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "protocol_soundness_proved",
        ]:
            if payload.get(field) != entry.get(field):
                errors.append(f"{label} late-bound contract {field} mismatch")
        if payload.get("packet_circuit_count") != 36:
            errors.append(f"{label} late-bound contract should cover 36 packet circuits")
        if payload.get("public_skeleton_private_material_embedded_file_count") != 0:
            errors.append(f"{label} late-bound contract public skeletons must not embed private material")
        if payload.get("public_skeletons_hide_private_material") is not True:
            errors.append(f"{label} late-bound contract must separate public skeletons from private material")
        if payload.get("public_data_transcript_classically_predictable") is not True:
            errors.append(f"{label} late-bound contract should preserve the deterministic-data blocker")
        if payload.get("late_bound_private_challenge_alone_sufficient_for_soundness") is not False:
            errors.append(f"{label} late-bound contract must not mark late-binding alone sufficient")
        if int(payload.get("failed_gate_count", 0)) < 3:
            errors.append(f"{label} late-bound contract should keep failed gates visible")
        for field in [
            "hardware_execution_performed",
            "real_backend_properties_used",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "protocol_soundness_proved",
        ]:
            if payload.get(field) is not False:
                errors.append(f"{label} late-bound contract must keep {field}=False")
        for row in payload.get("rows", []):
            skeleton_path = row.get("public_skeleton_path")
            if not skeleton_path or not path_exists_from(root, skeleton_path):
                errors.append(f"{label} late-bound contract skeleton missing: {skeleton_path}")
                continue
            skeleton_text = read((root / skeleton_path).resolve())
            if not skeleton_text.startswith("OPENQASM 3.0;"):
                errors.append(f"{label} late-bound contract skeleton header invalid: {skeleton_path}")
            if hashlib.sha256(skeleton_text.encode("utf-8")).hexdigest() != row.get("public_skeleton_sha256"):
                errors.append(f"{label} late-bound contract skeleton sha256 mismatch: {skeleton_path}")
        if len(payload.get("validation_errors", [])) != entry.get("validation_error_count"):
            errors.append(f"{label} late-bound contract validation-error count mismatch")
        return status

    def audit_nonstabilizer_pilot(entry, label):
        status = {}
        if not entry:
            warnings.append(f"{label} manifest has no non-stabilizer late-bound transcript pilot")
            return status
        result_path = entry.get("result")
        markdown_path = entry.get("markdown_report")
        pilot_dir = entry.get("nonstabilizer_pilot_directory")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        pilot_dir_exists = bool(pilot_dir and path_exists_from(benchmarks, pilot_dir))
        if not result_exists:
            errors.append(f"{label} non-stabilizer pilot result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"{label} non-stabilizer pilot markdown missing: {markdown_path}")
        if not pilot_dir_exists:
            errors.append(f"{label} non-stabilizer pilot directory missing: {pilot_dir}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        status = {
            "status": entry.get("status"),
            "method": entry.get("method"),
            "circuit_count": payload.get("circuit_count"),
            "nonstabilizer_file_count": payload.get("nonstabilizer_file_count"),
            "deterministic_emulator_broken_count": payload.get("deterministic_emulator_broken_count"),
            "public_deterministic_transcript_blocker_removed": payload.get(
                "public_deterministic_transcript_blocker_removed"
            ),
            "minimum_min_entropy_bits": payload.get("minimum_min_entropy_bits"),
            "maximum_output_probability": payload.get("maximum_output_probability"),
            "passed_gate_count": payload.get("passed_gate_count"),
            "failed_gate_count": payload.get("failed_gate_count"),
            "hardware_execution_performed": payload.get("hardware_execution_performed"),
            "quantum_advantage_claimed": payload.get("quantum_advantage_claimed"),
            "bqp_separation_claimed": payload.get("bqp_separation_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "nonstabilizer_pilot_directory_exists": pilot_dir_exists,
            "result": result_path,
            "markdown_report": markdown_path,
            "nonstabilizer_pilot_directory": pilot_dir,
        }
        if payload.get("benchmark_id") != "B4_B8":
            errors.append(f"{label} non-stabilizer pilot benchmark_id must be B4_B8")
        if payload.get("status") != entry.get("status"):
            errors.append(f"{label} non-stabilizer pilot status mismatch")
        if payload.get("method") != entry.get("method"):
            errors.append(f"{label} non-stabilizer pilot method mismatch")
        if payload.get("source_method") != "b4_b8_late_bound_private_challenge_contract_gate_v0":
            errors.append(f"{label} non-stabilizer pilot source method mismatch")
        for field in [
            "circuit_count",
            "nonstabilizer_file_count",
            "challenge_qubit_count_per_circuit",
            "deterministic_emulator_broken_count",
            "public_deterministic_transcript_blocker_removed",
            "minimum_min_entropy_bits",
            "maximum_output_probability",
            "exact_probability_ledger_file_count",
            "public_skeleton_private_material_hidden",
            "nonstabilizer_basis_layer_present",
            "hardware_execution_performed",
            "real_backend_properties_used",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "protocol_soundness_proved",
            "acceptance_gate_count",
            "passed_gate_count",
            "failed_gate_count",
        ]:
            if payload.get(field) != entry.get(field):
                errors.append(f"{label} non-stabilizer pilot {field} mismatch")
        if payload.get("circuit_count") != 36:
            errors.append(f"{label} non-stabilizer pilot should cover 36 circuits")
        if payload.get("nonstabilizer_file_count") != payload.get("circuit_count"):
            errors.append(f"{label} non-stabilizer pilot should emit one pilot file per circuit")
        if payload.get("deterministic_emulator_broken_count") != payload.get("circuit_count"):
            errors.append(f"{label} non-stabilizer pilot should break deterministic transcripts for all circuits")
        if payload.get("public_deterministic_transcript_blocker_removed") is not True:
            errors.append(f"{label} non-stabilizer pilot should remove the deterministic transcript blocker")
        if float(payload.get("minimum_min_entropy_bits", 0.0)) < 4.0:
            errors.append(f"{label} non-stabilizer pilot minimum entropy should be at least 4 bits")
        if float(payload.get("maximum_output_probability", 1.0)) != 0.0625:
            errors.append(f"{label} non-stabilizer pilot max output probability should be 0.0625")
        for field in [
            "hardware_execution_performed",
            "real_backend_properties_used",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "protocol_soundness_proved",
        ]:
            if payload.get(field) is not False:
                errors.append(f"{label} non-stabilizer pilot must keep {field}=False")
        if len(payload.get("validation_errors", [])) != entry.get("validation_error_count"):
            errors.append(f"{label} non-stabilizer pilot validation-error count mismatch")
        if payload.get("validation_error_count") != len(payload.get("validation_errors", [])):
            errors.append(f"{label} non-stabilizer pilot payload validation-error count mismatch")
        for row in payload.get("rows", []):
            pilot_path = row.get("nonstabilizer_pilot_path")
            if not pilot_path or not path_exists_from(root, pilot_path):
                errors.append(f"{label} non-stabilizer pilot QASM missing: {pilot_path}")
                continue
            qasm_text = read((root / pilot_path).resolve())
            if not qasm_text.startswith("OPENQASM 3.0;"):
                errors.append(f"{label} non-stabilizer pilot QASM header invalid: {pilot_path}")
            if hashlib.sha256(qasm_text.encode("utf-8")).hexdigest() != row.get("nonstabilizer_pilot_sha256"):
                errors.append(f"{label} non-stabilizer pilot QASM sha256 mismatch: {pilot_path}")
            if "h q[" not in qasm_text or ("t q[" not in qasm_text and "rz(pi/4)" not in qasm_text):
                errors.append(f"{label} non-stabilizer pilot QASM missing H plus T/RZ basis layer: {pilot_path}")
        return status

    def audit_nonstabilizer_support_spoofer(entry, label):
        status = {}
        if not entry:
            warnings.append(f"{label} manifest has no non-stabilizer support spoofer gate")
            return status
        result_path = entry.get("result")
        markdown_path = entry.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"{label} support-spoofer result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"{label} support-spoofer markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        status = {
            "status": entry.get("status"),
            "method": entry.get("method"),
            "circuit_count": payload.get("circuit_count"),
            "spoofer_count": payload.get("spoofer_count"),
            "attack_row_count": payload.get("attack_row_count"),
            "max_exact_transcript_success_probability": payload.get(
                "max_exact_transcript_success_probability"
            ),
            "max_support_acceptance_rate": payload.get("max_support_acceptance_rate"),
            "support_only_verifier_soundness_rejected": payload.get(
                "support_only_verifier_soundness_rejected"
            ),
            "deterministic_exact_transcript_blocker_survives": payload.get(
                "deterministic_exact_transcript_blocker_survives"
            ),
            "passed_gate_count": payload.get("passed_gate_count"),
            "failed_gate_count": payload.get("failed_gate_count"),
            "hardware_execution_performed": payload.get("hardware_execution_performed"),
            "quantum_advantage_claimed": payload.get("quantum_advantage_claimed"),
            "bqp_separation_claimed": payload.get("bqp_separation_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B4_B8":
            errors.append(f"{label} support-spoofer benchmark_id must be B4_B8")
        if payload.get("status") != entry.get("status"):
            errors.append(f"{label} support-spoofer status mismatch")
        if payload.get("method") != entry.get("method"):
            errors.append(f"{label} support-spoofer method mismatch")
        if payload.get("source_method") != "b4_b8_nonstabilizer_late_bound_transcript_pilot_v0":
            errors.append(f"{label} support-spoofer source method mismatch")
        for field in [
            "circuit_count",
            "spoofer_count",
            "attack_row_count",
            "challenge_qubit_count_per_circuit",
            "max_exact_transcript_success_probability",
            "min_exact_transcript_success_probability",
            "max_support_acceptance_rate",
            "min_support_acceptance_rate",
            "support_only_verifier_soundness_rejected",
            "deterministic_exact_transcript_blocker_survives",
            "public_support_template_attack_performed",
            "learned_generative_spoofer_attack_performed",
            "hardware_execution_performed",
            "real_backend_properties_used",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "protocol_soundness_proved",
            "acceptance_gate_count",
            "passed_gate_count",
            "failed_gate_count",
        ]:
            if payload.get(field) != entry.get(field):
                errors.append(f"{label} support-spoofer {field} mismatch")
        if payload.get("circuit_count") != 36:
            errors.append(f"{label} support-spoofer should cover 36 pilot circuits")
        if payload.get("spoofer_count") != 4:
            errors.append(f"{label} support-spoofer should cover four spoofer families")
        if payload.get("attack_row_count") != 144:
            errors.append(f"{label} support-spoofer should emit 144 attack rows")
        if payload.get("max_exact_transcript_success_probability") != 0.0625:
            errors.append(f"{label} support-spoofer exact transcript ceiling should be 0.0625")
        if payload.get("max_support_acceptance_rate") != 1.0:
            errors.append(f"{label} support-spoofer should fully pass support-only verification")
        if payload.get("support_only_verifier_soundness_rejected") is not True:
            errors.append(f"{label} support-spoofer must reject support-only verifier soundness")
        if payload.get("deterministic_exact_transcript_blocker_survives") is not True:
            errors.append(f"{label} support-spoofer exact transcript blocker must survive")
        for field in [
            "hardware_execution_performed",
            "real_backend_properties_used",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "protocol_soundness_proved",
        ]:
            if payload.get(field) is not False:
                errors.append(f"{label} support-spoofer must keep {field}=False")
        if len(payload.get("validation_errors", [])) != entry.get("validation_error_count"):
            errors.append(f"{label} support-spoofer validation-error count mismatch")
        if payload.get("validation_error_count") != len(payload.get("validation_errors", [])):
            errors.append(f"{label} support-spoofer payload validation-error count mismatch")
        return status

    b4_manifest = yaml.safe_load(read(b4_manifest_path))
    b4_results = b4_manifest.get("current_results", {})
    b4_trap = b4_results.get("toy_hidden_trap_protocol_sim_v0")
    b4_circuit_refresh = b4_results.get("circuit_hidden_projection_refresh_v0")
    b4_openqasm3_packet = b4_results.get("openqasm3_randomized_measurement_packet_v0")
    b4_public_qasm_spoofer = b4_results.get("public_qasm_packet_spoofer_gate_v0")
    b4_late_bound_contract = b4_results.get("late_bound_private_challenge_contract_gate_v0")
    b4_nonstabilizer_pilot = b4_results.get("nonstabilizer_late_bound_transcript_pilot_v0")
    b4_support_spoofer = b4_results.get("nonstabilizer_support_spoofer_gate_v0")
    b4_status = {}
    if not b4_trap:
        warnings.append("B4 manifest has no toy hidden-trap protocol result")
    else:
        result_path = b4_trap.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B4 trap protocol result path missing: {result_path}")
        if b4_trap.get("model_status") != "toy_statistical_protocol_not_quantum_advantage_claim":
            errors.append("B4 result must be explicitly marked as not a quantum advantage claim")
        if int(b4_trap.get("spoofing_families_failing_count", 0)) < 2:
            errors.append("B4 trap protocol has fewer than 2 spoofing families failing the batch rule")
        if result_exists:
            payload = json.loads(read((benchmarks / result_path).resolve()))
            if payload.get("benchmark_id") != "B4":
                errors.append(f"B4 result benchmark_id={payload.get('benchmark_id')!r}, expected 'B4'")
            if payload.get("method") != "toy_hidden_trap_protocol_sim_v0":
                errors.append(f"B4 result method={payload.get('method')!r}, expected toy_hidden_trap_protocol_sim_v0")
            if payload.get("configuration_count") != b4_trap.get("configuration_count"):
                errors.append("B4 result configuration_count differs from manifest")
            if payload.get("model_status") != b4_trap.get("model_status"):
                errors.append("B4 result model_status differs from manifest")
        b4_status = {
            "status": b4_trap.get("status"),
            "model_status": b4_trap.get("model_status"),
            "configuration_count": b4_trap.get("configuration_count"),
            "spoofing_families_tested": b4_trap.get("spoofing_families_tested"),
            "spoofing_families_failing_count": b4_trap.get("spoofing_families_failing_count"),
            "batch_completeness_range": b4_trap.get("batch_completeness_range"),
            "result_exists": result_exists,
            "result": result_path,
        }

    b4_circuit_refresh_status = {}
    if not b4_circuit_refresh:
        warnings.append("B4 manifest has no circuit-level hidden-projection refresh task")
    else:
        result_path = b4_circuit_refresh.get("result")
        markdown_path = b4_circuit_refresh.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B4/B8 circuit refresh result path missing from B4 manifest: {result_path}")
        if not markdown_exists:
            errors.append(f"B4/B8 circuit refresh markdown missing from B4 manifest: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b4_circuit_refresh_status = {
            "status": b4_circuit_refresh.get("status"),
            "method": b4_circuit_refresh.get("method"),
            "task_family": b4_circuit_refresh.get("task_family"),
            "task_count": b4_circuit_refresh.get("task_count"),
            "configuration_count": b4_circuit_refresh.get("configuration_count"),
            "minimum_honest_completeness": payload.get("minimum_honest_completeness"),
            "maximum_adaptive_soundness": payload.get("maximum_adaptive_soundness"),
            "none_high_leakage_max_soundness": payload.get("none_high_leakage_max_soundness"),
            "best_repair_high_leakage_max_soundness": payload.get("best_repair_high_leakage_max_soundness"),
            "high_leakage_repair_modes_passing": payload.get("high_leakage_repair_modes_passing"),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B4_B8":
            errors.append("B4/B8 circuit refresh benchmark_id must be B4_B8")
        if payload.get("status") != "circuit_level_hidden_projection_refresh_boundary_not_quantum_advantage_claim":
            errors.append("B4/B8 circuit refresh must remain marked as not a quantum advantage claim")
        if payload.get("method") != b4_circuit_refresh.get("method"):
            errors.append("B4/B8 circuit refresh method mismatch in B4 manifest")
        if payload.get("configuration_count") != b4_circuit_refresh.get("configuration_count"):
            errors.append("B4/B8 circuit refresh configuration count mismatch in B4 manifest")
        if float(payload.get("minimum_honest_completeness", 0.0)) < 0.8:
            errors.append("B4/B8 circuit refresh honest completeness below threshold")
        if float(payload.get("none_high_leakage_max_soundness", 0.0)) <= 0.05:
            errors.append("B4/B8 circuit refresh should expose high-leakage no-refresh risk")
        if float(payload.get("best_repair_high_leakage_max_soundness", 1.0)) > 0.05:
            errors.append("B4/B8 circuit refresh repair should reduce high-leakage soundness to <=5%")
        if not payload.get("high_leakage_repair_modes_passing"):
            errors.append("B4/B8 circuit refresh should identify at least one passing high-leakage repair mode")

    b4_openqasm3_packet_status = {}
    if not b4_openqasm3_packet:
        warnings.append("B4 manifest has no OpenQASM 3 randomized-measurement packet")
    else:
        result_path = b4_openqasm3_packet.get("result")
        markdown_path = b4_openqasm3_packet.get("markdown_report")
        qasm_directory = b4_openqasm3_packet.get("qasm_directory")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        qasm_directory_exists = bool(qasm_directory and path_exists_from(benchmarks, qasm_directory))
        if not result_exists:
            errors.append(f"B4/B8 OpenQASM 3 packet result path missing from B4 manifest: {result_path}")
        if not markdown_exists:
            errors.append(f"B4/B8 OpenQASM 3 packet markdown missing from B4 manifest: {markdown_path}")
        if not qasm_directory_exists:
            errors.append(f"B4/B8 OpenQASM 3 packet directory missing from B4 manifest: {qasm_directory}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b4_openqasm3_packet_status = {
            "status": b4_openqasm3_packet.get("status"),
            "method": b4_openqasm3_packet.get("method"),
            "qasm_version": payload.get("qasm_version"),
            "task_count": payload.get("task_count"),
            "refresh_mode_count": payload.get("refresh_mode_count"),
            "packet_circuits_per_task_mode": payload.get("packet_circuits_per_task_mode"),
            "circuit_file_count": payload.get("circuit_file_count"),
            "max_total_qubits": payload.get("max_total_qubits"),
            "all_qasm3_headers_valid": payload.get("all_qasm3_headers_valid"),
            "aer_semantic_mismatch_count": payload.get("aer_semantic_mismatch_count"),
            "minimum_aer_honest_completeness": payload.get("minimum_aer_honest_completeness"),
            "hardware_execution_performed": payload.get("hardware_execution_performed"),
            "quantum_advantage_claimed": payload.get("quantum_advantage_claimed"),
            "bqp_separation_claimed": payload.get("bqp_separation_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "qasm_directory_exists": qasm_directory_exists,
            "result": result_path,
            "markdown_report": markdown_path,
            "qasm_directory": qasm_directory,
        }
        if payload.get("benchmark_id") != "B4_B8":
            errors.append("B4 OpenQASM 3 packet benchmark_id must be B4_B8")
        if payload.get("status") != b4_openqasm3_packet.get("status"):
            errors.append("B4 OpenQASM 3 packet status mismatch")
        if payload.get("method") != b4_openqasm3_packet.get("method"):
            errors.append("B4 OpenQASM 3 packet method mismatch")
        if payload.get("qasm_version") != "OPENQASM 3.0":
            errors.append("B4 OpenQASM 3 packet must export OPENQASM 3.0 circuits")
        for field in [
            "task_count",
            "refresh_mode_count",
            "packet_circuits_per_task_mode",
            "circuit_file_count",
            "max_total_qubits",
            "openqasm3_files_exported",
            "all_qasm3_headers_valid",
            "hardware_executable_randomized_measurement_circuits_instantiated",
            "qiskit_aer_semantic_check_performed",
            "aer_semantic_mismatch_count",
            "minimum_aer_honest_completeness",
            "maximum_predicate_bit_error_rate",
            "hardware_execution_performed",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "full_distribution_verification_claimed",
        ]:
            if payload.get(field) != b4_openqasm3_packet.get(field):
                errors.append(f"B4 OpenQASM 3 packet {field} mismatch")
        if payload.get("circuit_file_count") != 36:
            errors.append("B4 OpenQASM 3 packet should export 36 circuits")
        if len(payload.get("circuits", [])) != payload.get("circuit_file_count"):
            errors.append("B4 OpenQASM 3 packet circuit metadata count mismatch")
        if payload.get("aer_semantic_mismatch_count") != 0:
            errors.append("B4 OpenQASM 3 packet must have zero Aer semantic mismatches")
        if payload.get("hardware_execution_performed") is not False:
            errors.append("B4 OpenQASM 3 packet must not claim hardware execution")
        for field in [
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "full_distribution_verification_claimed",
        ]:
            if payload.get(field) is not False:
                errors.append(f"B4 OpenQASM 3 packet must keep {field}=False")
        for row in payload.get("circuits", []):
            qasm_path = row.get("path")
            if not qasm_path or not path_exists_from(root, qasm_path):
                errors.append(f"B4 OpenQASM 3 circuit file missing: {qasm_path}")
                continue
            qasm_text = read((root / qasm_path).resolve())
            if not qasm_text.startswith("OPENQASM 3.0;"):
                errors.append(f"B4 OpenQASM 3 circuit header invalid: {qasm_path}")
            if hashlib.sha256(qasm_text.encode("utf-8")).hexdigest() != row.get("sha256"):
                errors.append(f"B4 OpenQASM 3 circuit sha256 mismatch: {qasm_path}")
        if len(payload.get("validation_errors", [])) != b4_openqasm3_packet.get("validation_error_count"):
            errors.append("B4 OpenQASM 3 packet validation-error count mismatch")

    b4_public_qasm_spoofer_status = {}
    if not b4_public_qasm_spoofer:
        warnings.append("B4 manifest has no public-QASM packet spoofer gate")
    else:
        result_path = b4_public_qasm_spoofer.get("result")
        markdown_path = b4_public_qasm_spoofer.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B4 public-QASM spoofer result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B4 public-QASM spoofer markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b4_public_qasm_spoofer_status = {
            "status": b4_public_qasm_spoofer.get("status"),
            "method": b4_public_qasm_spoofer.get("method"),
            "packet_circuit_count": payload.get("packet_circuit_count"),
            "parsed_circuit_count": payload.get("parsed_circuit_count"),
            "public_stabilizer_emulator_prediction_success_rate": payload.get(
                "public_stabilizer_emulator_prediction_success_rate"
            ),
            "public_packet_contract_soundness_rejected": payload.get(
                "public_packet_contract_soundness_rejected"
            ),
            "late_bound_private_challenges_required": payload.get("late_bound_private_challenges_required"),
            "hardware_execution_performed": payload.get("hardware_execution_performed"),
            "quantum_advantage_claimed": payload.get("quantum_advantage_claimed"),
            "bqp_separation_claimed": payload.get("bqp_separation_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B4_B8":
            errors.append("B4 public-QASM spoofer benchmark_id must be B4_B8")
        if payload.get("status") != b4_public_qasm_spoofer.get("status"):
            errors.append("B4 public-QASM spoofer status mismatch")
        if payload.get("method") != b4_public_qasm_spoofer.get("method"):
            errors.append("B4 public-QASM spoofer method mismatch")
        for field in [
            "packet_circuit_count",
            "parsed_circuit_count",
            "deterministic_classical_file_count",
            "unsupported_file_count",
            "public_stabilizer_emulator_prediction_success_rate",
            "public_packet_spoofer_acceptance_rate",
            "public_packet_contract_soundness_rejected",
            "late_bound_private_challenges_required",
            "real_backend_or_hardware_execution_still_required",
            "hardware_execution_performed",
            "real_backend_properties_used",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "protocol_soundness_proved",
        ]:
            if payload.get(field) != b4_public_qasm_spoofer.get(field):
                errors.append(f"B4 public-QASM spoofer {field} mismatch")
        if payload.get("source_method") != "b4_b8_openqasm3_randomized_measurement_packet_v0":
            errors.append("B4 public-QASM spoofer source method mismatch")
        if payload.get("public_stabilizer_emulator_prediction_success_rate") != 1.0:
            errors.append("B4 public-QASM spoofer should predict the current public packet exactly")
        if payload.get("public_packet_contract_soundness_rejected") is not True:
            errors.append("B4 public-QASM spoofer should reject public-packet protocol soundness")
        if len(payload.get("validation_errors", [])) != b4_public_qasm_spoofer.get("validation_error_count"):
            errors.append("B4 public-QASM spoofer validation-error count mismatch")

    b4_late_bound_contract_status = audit_late_bound_contract(b4_late_bound_contract, "B4")
    b4_nonstabilizer_pilot_status = audit_nonstabilizer_pilot(b4_nonstabilizer_pilot, "B4")
    b4_support_spoofer_status = audit_nonstabilizer_support_spoofer(b4_support_spoofer, "B4")

    b5_manifest = yaml.safe_load(read(b5_manifest_path))
    b5_results = b5_manifest.get("current_results", {})
    b5_hubbard = b5_results.get("hubbard_exact_diagonalization_cluster_proxy_v0")
    b5_canonical_smoke = b5_results.get("canonical_environment_smoke_gate_v0")
    b5_dmrg_readiness = b5_results.get("canonical_dmrg_readiness_gate_v0")
    b5_b10_production_contract = b5_results.get("b5_b10_same_access_production_contract_gate_v0")
    b5_two_site_dmrg = b5_results.get("two_site_finite_dmrg_response_reference_v0")
    b5_var_mps = b5_results.get("variational_mps_als_response_reference_v0")
    b5_mps = b5_results.get("mps_schmidt_truncation_response_reference_v0")
    b5_non_oracle = b5_results.get("non_oracle_response_embedding_baseline_v0")
    b5_boundary_field = b5_results.get("boundary_field_response_embedding_baseline_v0")
    b5_status = {}
    if not b5_hubbard:
        warnings.append("B5 manifest has no Hubbard exact-diagonalization cluster proxy result")
    else:
        result_path = b5_hubbard.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B5 Hubbard result path missing: {result_path}")
        if b5_hubbard.get("model_status") != "exact_small_system_reference_plus_cluster_product_proxy":
            errors.append("B5 result must be explicitly marked as exact reference plus cluster proxy")
        if result_exists:
            payload = json.loads(read((benchmarks / result_path).resolve()))
            if payload.get("benchmark_id") != "B5":
                errors.append(f"B5 result benchmark_id={payload.get('benchmark_id')!r}, expected 'B5'")
            if payload.get("method") != "small_hubbard_exact_diagonalization_cluster_proxy_v0":
                errors.append(f"B5 result method={payload.get('method')!r}, expected small_hubbard_exact_diagonalization_cluster_proxy_v0")
            if payload.get("configuration_count") != b5_hubbard.get("configuration_count"):
                errors.append("B5 result configuration_count differs from manifest")
            if payload.get("model_status") != b5_hubbard.get("model_status"):
                errors.append("B5 result model_status differs from manifest")
            summary = payload.get("summary_by_cluster_size", {})
            if sorted(summary) != ["2", "4"]:
                errors.append(f"B5 summary has unexpected cluster sizes: {sorted(summary)}")
            if summary.get("4", {}).get("mean_error_per_site", 1.0) >= summary.get("2", {}).get("mean_error_per_site", 0.0):
                errors.append("B5 4-site cluster proxy should improve mean error per site over 2-site proxy")
        b5_status = {
            "status": b5_hubbard.get("status"),
            "model_status": b5_hubbard.get("model_status"),
            "configuration_count": b5_hubbard.get("configuration_count"),
            "exact_hilbert_dimension_range": b5_hubbard.get("exact_hilbert_dimension_range"),
            "mean_error_per_site_by_cluster_size": b5_hubbard.get("mean_error_per_site_by_cluster_size"),
            "result_exists": result_exists,
            "result": result_path,
        }

    b5_canonical_smoke_status = {}
    if not b5_canonical_smoke:
        warnings.append("B5 manifest has no canonical-environment smoke gate")
    else:
        result_path = b5_canonical_smoke.get("result")
        markdown_path = b5_canonical_smoke.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B5 canonical-environment smoke gate result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B5 canonical-environment smoke gate markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        b5_canonical_smoke_status = {
            "status": b5_canonical_smoke.get("status"),
            "method": b5_canonical_smoke.get("method"),
            "model_status": payload.get("model_status"),
            "instance_count": summary.get("instance_count"),
            "environment_ledger_rows": summary.get("environment_ledger_rows"),
            "smoke_passed_row_count": summary.get("smoke_passed_row_count"),
            "fixed_sector_norm_passed_rows": summary.get("fixed_sector_norm_passed_rows"),
            "energy_variance_passed_rows": summary.get("energy_variance_passed_rows"),
            "discarded_weight_passed_rows": summary.get("discarded_weight_passed_rows"),
            "energy_monotonicity_passed_rows": summary.get("energy_monotonicity_passed_rows"),
            "response_close_to_seeded_rows": summary.get("response_close_to_seeded_rows"),
            "rows_beating_seeded_mps_pressure_reference": summary.get(
                "rows_beating_seeded_mps_pressure_reference"
            ),
            "rows_beating_variational_mps_als_reference": summary.get(
                "rows_beating_variational_mps_als_reference"
            ),
            "mean_relative_response_error": summary.get("mean_relative_response_error"),
            "max_relative_response_error": summary.get("max_relative_response_error"),
            "min_fixed_sector_norm_before_normalization": summary.get(
                "min_fixed_sector_norm_before_normalization"
            ),
            "max_relative_discarded_weight": summary.get("max_relative_discarded_weight"),
            "max_energy_variance": summary.get("max_energy_variance"),
            "mature_canonical_dmrg_ready": summary.get("mature_canonical_dmrg_ready"),
            "canonical_environment_solver_claimed": claims.get("canonical_environment_solver_claimed"),
            "production_dmrg_claimed": claims.get("production_dmrg_claimed"),
            "same_access_positive_route_claimed": claims.get("same_access_positive_route_claimed"),
            "quantum_response_win_claimed": claims.get("quantum_response_win_claimed"),
            "accuracy_per_resource_win_claimed": claims.get("accuracy_per_resource_win_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B5":
            errors.append("B5 canonical-environment smoke gate benchmark_id must be B5")
        if payload.get("method") != b5_canonical_smoke.get("method"):
            errors.append("B5 canonical-environment smoke gate method mismatch")
        if payload.get("status") != b5_canonical_smoke.get("status"):
            errors.append("B5 canonical-environment smoke gate status mismatch")
        if payload.get("model_status") != b5_canonical_smoke.get("model_status"):
            errors.append("B5 canonical-environment smoke gate model-status mismatch")
        for field in [
            "instance_count",
            "environment_ledger_rows",
            "smoke_passed_row_count",
            "fixed_sector_norm_passed_rows",
            "energy_variance_passed_rows",
            "discarded_weight_passed_rows",
            "energy_monotonicity_passed_rows",
            "response_close_to_seeded_rows",
            "rows_beating_seeded_mps_pressure_reference",
            "rows_beating_variational_mps_als_reference",
            "mean_relative_response_error",
            "max_relative_response_error",
            "min_fixed_sector_norm_before_normalization",
            "max_relative_discarded_weight",
            "max_energy_variance",
            "mature_canonical_dmrg_ready",
        ]:
            if summary.get(field) != b5_canonical_smoke.get(field):
                errors.append(f"B5 canonical-environment smoke gate {field} mismatch")
        if summary.get("instance_count") != 9:
            errors.append("B5 canonical-environment smoke gate must cover all nine D5 rows")
        if summary.get("environment_ledger_rows") != 9:
            errors.append("B5 canonical-environment smoke gate must expose ledgers for all rows")
        if summary.get("smoke_passed_row_count") != 0:
            errors.append("B5 canonical-environment smoke gate must not pass full smoke gate yet")
        if summary.get("response_close_to_seeded_rows") != 0:
            errors.append("B5 canonical-environment smoke gate must not be response-close to seeded pressure yet")
        if summary.get("rows_beating_seeded_mps_pressure_reference") != 0:
            errors.append("B5 canonical-environment smoke gate must not beat seeded pressure")
        if summary.get("mature_canonical_dmrg_ready") is not False:
            errors.append("B5 canonical-environment smoke gate must not mark mature DMRG ready")
        for field in [
            "canonical_environment_solver_claimed",
            "production_dmrg_claimed",
            "same_access_positive_route_claimed",
            "quantum_response_win_claimed",
            "accuracy_per_resource_win_claimed",
        ]:
            if claims.get(field) is not False:
                errors.append(f"B5 canonical-environment smoke gate must keep {field}=False")
        if len(payload.get("validation_errors", [])) != b5_canonical_smoke.get("validation_error_count"):
            errors.append("B5 canonical-environment smoke gate validation-error count mismatch")

    b5_dmrg_readiness_status = {}
    if not b5_dmrg_readiness:
        warnings.append("B5 manifest has no canonical DMRG readiness gate")
    else:
        result_path = b5_dmrg_readiness.get("result")
        markdown_path = b5_dmrg_readiness.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B5 canonical DMRG readiness result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B5 canonical DMRG readiness markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b5_dmrg_readiness_status = {
            "status": b5_dmrg_readiness.get("status"),
            "method": b5_dmrg_readiness.get("method"),
            "model_status": b5_dmrg_readiness.get("model_status"),
            "instance_count": summary.get("instance_count"),
            "readiness_gate_count": summary.get("readiness_gate_count"),
            "passed_gate_count": summary.get("passed_gate_count"),
            "failed_gate_count": summary.get("failed_gate_count"),
            "two_site_mean_relative_response_error": summary.get("two_site_mean_relative_response_error"),
            "variational_mps_als_mean_relative_response_error": summary.get(
                "variational_mps_als_mean_relative_response_error"
            ),
            "seeded_mps_pressure_mean_relative_response_error": summary.get(
                "seeded_mps_pressure_mean_relative_response_error"
            ),
            "two_site_rows_beating_variational_mps_als_reference": summary.get(
                "two_site_rows_beating_variational_mps_als_reference"
            ),
            "two_site_rows_beating_seeded_mps_pressure_reference": summary.get(
                "two_site_rows_beating_seeded_mps_pressure_reference"
            ),
            "variational_mps_rows_beating_seeded_mps_pressure_reference": summary.get(
                "variational_mps_rows_beating_seeded_mps_pressure_reference"
            ),
            "prototype_fixed_sector_norms_pass": summary.get("prototype_fixed_sector_norms_pass"),
            "exact_state_seeded_reference_is_strongest": summary.get("exact_state_seeded_reference_is_strongest"),
            "mature_canonical_dmrg_ready": summary.get("mature_canonical_dmrg_ready"),
            "canonical_environment_production_dmrg": summary.get("canonical_environment_production_dmrg"),
            "production_dmrg": summary.get("production_dmrg"),
            "same_access_positive_route_claimed": summary.get("same_access_positive_route_claimed"),
            "quantum_response_win_claimed": summary.get("quantum_response_win_claimed"),
            "accuracy_per_resource_win_claimed": summary.get("accuracy_per_resource_win_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B5":
            errors.append("B5 canonical DMRG readiness result benchmark_id must be B5")
        if payload.get("method") != b5_dmrg_readiness.get("method"):
            errors.append("B5 canonical DMRG readiness method mismatch")
        if payload.get("status") != "canonical_dmrg_readiness_gate_failed_not_production_dmrg":
            errors.append("B5 canonical DMRG readiness status must remain a failed readiness gate")
        if payload.get("model_status") != "cross_reference_readiness_gate_not_solver":
            errors.append("B5 canonical DMRG readiness model_status must disclose that it is not a solver")
        for field in [
            "instance_count",
            "readiness_gate_count",
            "passed_gate_count",
            "failed_gate_count",
            "two_site_rows_beating_variational_mps_als_reference",
            "two_site_rows_beating_seeded_mps_pressure_reference",
            "variational_mps_rows_beating_seeded_mps_pressure_reference",
        ]:
            if summary.get(field) != b5_dmrg_readiness.get(field):
                errors.append(f"B5 canonical DMRG readiness {field} mismatch")
        if summary.get("instance_count") != 9:
            errors.append("B5 canonical DMRG readiness must cover all nine D5 B5 instances")
        if summary.get("readiness_gate_count") != 8:
            errors.append("B5 canonical DMRG readiness should evaluate eight gates")
        if summary.get("passed_gate_count") != 0 or summary.get("failed_gate_count") != 8:
            errors.append("B5 canonical DMRG readiness should currently fail all readiness gates")
        if summary.get("mature_canonical_dmrg_ready") is not False:
            errors.append("B5 canonical DMRG readiness must not mark mature canonical DMRG ready")
        if summary.get("canonical_environment_production_dmrg") is not False:
            errors.append("B5 canonical DMRG readiness must not claim canonical production DMRG")
        if summary.get("production_dmrg") is not False:
            errors.append("B5 canonical DMRG readiness must not claim production DMRG")
        if summary.get("same_access_positive_route_claimed") is not False:
            errors.append("B5 canonical DMRG readiness must not claim a same-access positive route")
        if summary.get("quantum_response_win_claimed") is not False:
            errors.append("B5 canonical DMRG readiness must not claim a quantum response win")
        if summary.get("accuracy_per_resource_win_claimed") is not False:
            errors.append("B5 canonical DMRG readiness must not claim an accuracy-per-resource win")
        if summary.get("exact_state_seeded_reference_is_strongest") is not True:
            errors.append("B5 canonical DMRG readiness must preserve the seeded pressure reference as strongest")
        if summary.get("prototype_fixed_sector_norms_pass") is not False:
            errors.append("B5 canonical DMRG readiness should fail the prototype fixed-sector norm gate")
        if int(summary.get("two_site_rows_beating_seeded_mps_pressure_reference", -1)) != 0:
            errors.append("B5 canonical DMRG readiness two-site rows should not beat seeded pressure")
        if int(summary.get("variational_mps_rows_beating_seeded_mps_pressure_reference", -1)) != 0:
            errors.append("B5 canonical DMRG readiness ALS rows should not beat seeded pressure")
        if len(payload.get("readiness_gates", [])) != summary.get("readiness_gate_count"):
            errors.append("B5 canonical DMRG readiness gate count mismatch")
        if any(gate.get("passed") for gate in payload.get("readiness_gates", [])):
            errors.append("B5 canonical DMRG readiness payload unexpectedly has a passing gate")
        if len(payload.get("validation_errors", [])) != b5_dmrg_readiness.get("validation_error_count"):
            errors.append("B5 canonical DMRG readiness validation-error count mismatch")
        claim_boundary = payload.get("claim_boundary", {})
        for field in [
            "mature_canonical_dmrg_ready",
            "production_dmrg",
            "canonical_environment_production_dmrg",
            "quantum_response_win_claimed",
            "accuracy_per_resource_win_claimed",
            "same_access_positive_route_claimed",
        ]:
            if claim_boundary.get(field) is not False:
                errors.append(f"B5 canonical DMRG readiness claim boundary must keep {field}=False")

    b5_b10_production_contract_status = {}
    if not b5_b10_production_contract:
        warnings.append("B5 manifest has no B5/B10 same-access production contract gate")
    else:
        result_path = b5_b10_production_contract.get("result")
        markdown_path = b5_b10_production_contract.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B5/B10 same-access production contract result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B5/B10 same-access production contract markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        b5_b10_production_contract_status = {
            "status": b5_b10_production_contract.get("status"),
            "method": b5_b10_production_contract.get("method"),
            "model_status": b5_b10_production_contract.get("model_status"),
            "instance_count": summary.get("instance_count"),
            "contract_gate_count": summary.get("contract_gate_count"),
            "contract_pass_count": summary.get("contract_pass_count"),
            "contract_fail_count": summary.get("contract_fail_count"),
            "contract_acceptance_passed": summary.get("contract_acceptance_passed"),
            "production_contract_ready": summary.get("production_contract_ready"),
            "production_dmrg_available": summary.get("production_dmrg_available"),
            "canonical_environment_smoke_passed_rows": summary.get(
                "canonical_environment_smoke_passed_rows"
            ),
            "readiness_passed_gate_count": summary.get("readiness_passed_gate_count"),
            "blocking_sampling_requirement_count": summary.get("blocking_sampling_requirement_count"),
            "sampling_oracle_constructed": summary.get("sampling_oracle_constructed"),
            "same_access_positive_route_ready": summary.get("same_access_positive_route_ready"),
            "b10_t1_positive_route_ready": summary.get("b10_t1_positive_route_ready"),
            "production_dmrg_claimed": summary.get("production_dmrg_claimed"),
            "quantum_response_win_claimed": summary.get("quantum_response_win_claimed"),
            "accuracy_per_resource_win_claimed": summary.get("accuracy_per_resource_win_claimed"),
            "same_access_positive_route_claimed": summary.get("same_access_positive_route_claimed"),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "bqp_separation_claimed": summary.get("bqp_separation_claimed"),
            "dequantization_theorem_claimed": summary.get("dequantization_theorem_claimed"),
            "sampling_access_theorem_claimed": summary.get("sampling_access_theorem_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B5":
            errors.append("B5/B10 same-access production contract benchmark_id must be B5")
        if payload.get("linked_benchmark_id") != "B10":
            errors.append("B5/B10 same-access production contract linked_benchmark_id must be B10")
        if payload.get("method") != b5_b10_production_contract.get("method"):
            errors.append("B5/B10 same-access production contract method mismatch")
        if payload.get("status") != b5_b10_production_contract.get("status"):
            errors.append("B5/B10 same-access production contract status mismatch")
        if payload.get("model_status") != b5_b10_production_contract.get("model_status"):
            errors.append("B5/B10 same-access production contract model-status mismatch")
        for field in [
            "instance_count",
            "contract_gate_count",
            "contract_pass_count",
            "contract_fail_count",
            "contract_acceptance_passed",
            "production_contract_ready",
            "production_dmrg_available",
            "canonical_environment_smoke_passed_rows",
            "readiness_passed_gate_count",
            "blocking_sampling_requirement_count",
            "sampling_oracle_constructed",
            "same_access_positive_route_ready",
            "b10_t1_positive_route_ready",
            "production_dmrg_claimed",
            "quantum_response_win_claimed",
            "accuracy_per_resource_win_claimed",
            "same_access_positive_route_claimed",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "dequantization_theorem_claimed",
            "sampling_access_theorem_claimed",
        ]:
            if summary.get(field) != b5_b10_production_contract.get(field):
                errors.append(f"B5/B10 same-access production contract {field} mismatch")
        if summary.get("instance_count") != 9:
            errors.append("B5/B10 same-access production contract must cover all nine D5 rows")
        if summary.get("contract_gate_count") != 10:
            errors.append("B5/B10 same-access production contract must expose ten gates")
        if summary.get("contract_pass_count") != 2 or summary.get("contract_fail_count") != 8:
            errors.append("B5/B10 same-access production contract should currently pass 2/10 gates")
        if summary.get("contract_acceptance_passed") is not False:
            errors.append("B5/B10 same-access production contract must not pass acceptance")
        if summary.get("production_contract_ready") is not False:
            errors.append("B5/B10 same-access production contract must not be production-ready")
        if summary.get("production_dmrg_available") is not False:
            errors.append("B5/B10 same-access production contract must not claim production DMRG availability")
        if summary.get("canonical_environment_smoke_passed_rows") != 0:
            errors.append("B5/B10 same-access production contract must keep smoke-passed rows at 0")
        if summary.get("readiness_passed_gate_count") != 0:
            errors.append("B5/B10 same-access production contract must keep readiness-passed gates at 0")
        if summary.get("blocking_sampling_requirement_count") != 5:
            errors.append("B5/B10 same-access production contract must keep five blocking sampling requirements")
        if len(payload.get("contract_gates", [])) != 10:
            errors.append("B5/B10 same-access production contract gate row count mismatch")
        if sum(1 for gate in payload.get("contract_gates", []) if gate.get("passed")) != 2:
            errors.append("B5/B10 same-access production contract payload should have two passing gates")
        for field in [
            "production_dmrg_claimed",
            "quantum_response_win_claimed",
            "accuracy_per_resource_win_claimed",
            "same_access_positive_route_claimed",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "dequantization_theorem_claimed",
            "sampling_access_theorem_claimed",
        ]:
            if summary.get(field) is not False:
                errors.append(f"B5/B10 same-access production contract must keep {field}=False")
            if claims.get(field) is not False:
                errors.append(f"B5/B10 same-access production contract claim boundary must keep {field}=False")
        if len(payload.get("validation_errors", [])) != b5_b10_production_contract.get("validation_error_count"):
            errors.append("B5/B10 same-access production contract validation-error count mismatch")

    b5_boundary_field_status = {}
    if not b5_boundary_field:
        warnings.append("B5 manifest has no boundary-field response embedding baseline")
    else:
        result_path = b5_boundary_field.get("result")
        markdown_path = b5_boundary_field.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B5 boundary-field result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B5 boundary-field markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b5_boundary_field_status = {
            "status": b5_boundary_field.get("status"),
            "method": b5_boundary_field.get("method"),
            "model_status": b5_boundary_field.get("model_status"),
            "dependency_b10_table": b5_boundary_field.get("dependency_b10_table"),
            "instance_count": summary.get("instance_count"),
            "mean_relative_response_error": summary.get("mean_relative_response_error"),
            "max_relative_response_error": summary.get("max_relative_response_error"),
            "max_exact_d5_hilbert_dimension": summary.get("max_exact_d5_hilbert_dimension"),
            "max_cluster_hilbert_dimension": summary.get("max_cluster_hilbert_dimension"),
            "oracle_tuned_boundary_field": summary.get("oracle_tuned_boundary_field"),
            "quantum_response_win_claimed": summary.get("quantum_response_win_claimed"),
            "accuracy_per_resource_win_claimed": summary.get("accuracy_per_resource_win_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B5":
            errors.append("B5 boundary-field result benchmark_id must be B5")
        if payload.get("method") != b5_boundary_field.get("method"):
            errors.append("B5 boundary-field method mismatch")
        if payload.get("status") != "boundary_field_response_embedding_denominator_not_quantum_advantage_claim":
            errors.append("B5 boundary-field status must remain a denominator, not an advantage claim")
        if payload.get("model_status") != b5_boundary_field.get("model_status"):
            errors.append("B5 boundary-field model_status mismatch")
        if payload.get("dependency_b10_table") != b5_boundary_field.get("dependency_b10_table"):
            errors.append("B5 boundary-field B10 dependency mismatch")
        if payload.get("explicit_not_quantum_advantage") is not True:
            errors.append("B5 boundary-field must explicitly avoid quantum-advantage claims")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B5 boundary-field must explicitly avoid BQP separation claims")
        if summary.get("instance_count") != b5_boundary_field.get("instance_count"):
            errors.append("B5 boundary-field instance_count mismatch")
        if summary.get("boundary_field_grid_count") != len(b5_boundary_field.get("boundary_field_grid", [])):
            errors.append("B5 boundary-field grid count mismatch")
        if summary.get("oracle_tuned_boundary_field") is not True:
            errors.append("B5 boundary-field must disclose oracle tuning")
        if summary.get("quantum_response_win_claimed") is not False:
            errors.append("B5 boundary-field must not claim a quantum response win")
        if summary.get("accuracy_per_resource_win_claimed") is not False:
            errors.append("B5 boundary-field must not claim an accuracy-per-resource win")
        if len(payload.get("validation_errors", [])) != b5_boundary_field.get("validation_error_count"):
            errors.append("B5 boundary-field validation-error count mismatch")
        if float(summary.get("max_relative_response_error", 1.0)) > 0.25:
            errors.append("B5 boundary-field max response error is above the denominator sanity bound")
        if int(summary.get("max_cluster_hilbert_dimension", 10**9)) >= int(
            summary.get("max_exact_d5_hilbert_dimension", 0)
        ):
            errors.append("B5 boundary-field should reduce the largest embedded cluster dimension below exact D5")
        if len(payload.get("rows", [])) != 9:
            errors.append("B5 boundary-field rows must cover all nine D5 B5 instances")

    b5_non_oracle_status = {}
    if not b5_non_oracle:
        warnings.append("B5 manifest has no non-oracle response embedding baseline")
    else:
        result_path = b5_non_oracle.get("result")
        markdown_path = b5_non_oracle.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B5 non-oracle response result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B5 non-oracle response markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b5_non_oracle_status = {
            "status": b5_non_oracle.get("status"),
            "method": b5_non_oracle.get("method"),
            "model_status": b5_non_oracle.get("model_status"),
            "dependency_b10_table": b5_non_oracle.get("dependency_b10_table"),
            "instance_count": summary.get("instance_count"),
            "selected_mean_relative_response_error": summary.get("selected_mean_relative_response_error"),
            "selected_max_relative_response_error": summary.get("selected_max_relative_response_error"),
            "oracle_boundary_field_mean_relative_response_error": summary.get(
                "oracle_boundary_field_mean_relative_response_error"
            ),
            "oracle_boundary_field_max_relative_response_error": summary.get(
                "oracle_boundary_field_max_relative_response_error"
            ),
            "non_oracle_rows_beating_oracle_boundary_field": summary.get(
                "non_oracle_rows_beating_oracle_boundary_field"
            ),
            "max_exact_d5_hilbert_dimension": summary.get("max_exact_d5_hilbert_dimension"),
            "max_selected_cluster_hilbert_dimension": summary.get("max_selected_cluster_hilbert_dimension"),
            "uses_exact_target_for_selection": summary.get("uses_exact_target_for_selection"),
            "oracle_tuned_boundary_field": summary.get("oracle_tuned_boundary_field"),
            "quantum_response_win_claimed": summary.get("quantum_response_win_claimed"),
            "accuracy_per_resource_win_claimed": summary.get("accuracy_per_resource_win_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B5":
            errors.append("B5 non-oracle response result benchmark_id must be B5")
        if payload.get("method") != b5_non_oracle.get("method"):
            errors.append("B5 non-oracle response method mismatch")
        if payload.get("status") != "non_oracle_response_embedding_denominator_not_quantum_advantage_claim":
            errors.append("B5 non-oracle response status must remain a denominator, not an advantage claim")
        if payload.get("model_status") != b5_non_oracle.get("model_status"):
            errors.append("B5 non-oracle response model_status mismatch")
        if payload.get("dependency_b10_table") != b5_non_oracle.get("dependency_b10_table"):
            errors.append("B5 non-oracle response B10 dependency mismatch")
        if payload.get("explicit_not_quantum_advantage") is not True:
            errors.append("B5 non-oracle response must explicitly avoid quantum-advantage claims")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B5 non-oracle response must explicitly avoid BQP separation claims")
        if payload.get("uses_exact_target_for_selection") is not False:
            errors.append("B5 non-oracle response must not use exact targets for selection")
        if payload.get("oracle_tuned_boundary_field") is not False:
            errors.append("B5 non-oracle response must not be oracle tuned")
        if summary.get("instance_count") != b5_non_oracle.get("instance_count"):
            errors.append("B5 non-oracle response instance_count mismatch")
        if summary.get("field_grid_count") != len(b5_non_oracle.get("field_grid", [])):
            errors.append("B5 non-oracle response field-grid count mismatch")
        if summary.get("uses_exact_target_for_selection") is not False:
            errors.append("B5 non-oracle response summary must not use exact targets for selection")
        if summary.get("oracle_tuned_boundary_field") is not False:
            errors.append("B5 non-oracle response summary must disclose non-oracle selection")
        if summary.get("quantum_response_win_claimed") is not False:
            errors.append("B5 non-oracle response must not claim a quantum response win")
        if summary.get("accuracy_per_resource_win_claimed") is not False:
            errors.append("B5 non-oracle response must not claim an accuracy-per-resource win")
        if len(payload.get("validation_errors", [])) != b5_non_oracle.get("validation_error_count"):
            errors.append("B5 non-oracle response validation-error count mismatch")
        if float(summary.get("selected_max_relative_response_error", 1.0)) > 0.25:
            errors.append("B5 non-oracle response max response error is above the denominator sanity bound")
        if int(summary.get("max_selected_cluster_hilbert_dimension", 10**9)) >= int(
            summary.get("max_exact_d5_hilbert_dimension", 0)
        ):
            errors.append("B5 non-oracle response should reduce max selected cluster dimension below exact D5")
        if len(payload.get("rows", [])) != 9:
            errors.append("B5 non-oracle response rows must cover all nine D5 B5 instances")
        for row in payload.get("rows", []):
            label = f"sites={row.get('sites')} U/t={row.get('u_over_t')}"
            if row.get("uses_exact_target_for_selection") is not False:
                errors.append(f"B5 non-oracle response row uses exact target for selection: {label}")
            if row.get("oracle_tuned_boundary_field") is not False:
                errors.append(f"B5 non-oracle response row is oracle tuned: {label}")
            if row.get("candidate_quantum_response_beats_non_oracle_denominator") is not False:
                errors.append(f"B5 non-oracle response row claims a quantum win: {label}")

    b5_mps_status = {}
    if not b5_mps:
        warnings.append("B5 manifest has no MPS/Schmidt truncation response reference")
    else:
        result_path = b5_mps.get("result")
        markdown_path = b5_mps.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B5 MPS truncation response result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B5 MPS truncation response markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b5_mps_status = {
            "status": b5_mps.get("status"),
            "method": b5_mps.get("method"),
            "model_status": b5_mps.get("model_status"),
            "dependency_b10_table": b5_mps.get("dependency_b10_table"),
            "instance_count": summary.get("instance_count"),
            "bond_dimensions_tested": summary.get("bond_dimensions_tested"),
            "selected_bond_dimension": summary.get("selected_bond_dimension"),
            "selected_mean_relative_response_error": summary.get("selected_mean_relative_response_error"),
            "selected_max_relative_response_error": summary.get("selected_max_relative_response_error"),
            "selected_mean_energy_error_per_site": summary.get("selected_mean_energy_error_per_site"),
            "selected_max_energy_error_per_site": summary.get("selected_max_energy_error_per_site"),
            "selected_min_overlap_with_exact_ground_state": summary.get(
                "selected_min_overlap_with_exact_ground_state"
            ),
            "selected_min_fixed_sector_norm_before_normalization": summary.get(
                "selected_min_fixed_sector_norm_before_normalization"
            ),
            "mps_rows_beating_non_oracle_embedding": summary.get("mps_rows_beating_non_oracle_embedding"),
            "max_exact_d5_hilbert_dimension": summary.get("max_exact_d5_hilbert_dimension"),
            "max_full_local_basis_dimension": summary.get("max_full_local_basis_dimension"),
            "exact_state_seeded": summary.get("exact_state_seeded"),
            "variational_dmrg": summary.get("variational_dmrg"),
            "quantum_response_win_claimed": summary.get("quantum_response_win_claimed"),
            "accuracy_per_resource_win_claimed": summary.get("accuracy_per_resource_win_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B5":
            errors.append("B5 MPS truncation response result benchmark_id must be B5")
        if payload.get("method") != b5_mps.get("method"):
            errors.append("B5 MPS truncation response method mismatch")
        if payload.get("status") != "mps_schmidt_truncation_response_reference_not_dmrg_or_advantage_claim":
            errors.append("B5 MPS truncation response status must remain a reference, not an advantage claim")
        if payload.get("model_status") != b5_mps.get("model_status"):
            errors.append("B5 MPS truncation response model_status mismatch")
        if payload.get("dependency_b10_table") != b5_mps.get("dependency_b10_table"):
            errors.append("B5 MPS truncation response B10 dependency mismatch")
        if payload.get("explicit_not_quantum_advantage") is not True:
            errors.append("B5 MPS truncation response must explicitly avoid quantum-advantage claims")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B5 MPS truncation response must explicitly avoid BQP separation claims")
        if payload.get("explicit_not_variational_dmrg") is not True:
            errors.append("B5 MPS truncation response must explicitly say it is not variational DMRG")
        if payload.get("exact_state_seeded") is not True:
            errors.append("B5 MPS truncation response must disclose exact-state seeding")
        if summary.get("instance_count") != b5_mps.get("instance_count"):
            errors.append("B5 MPS truncation response instance_count mismatch")
        if summary.get("bond_dimensions_tested") != b5_mps.get("bond_dimensions_tested"):
            errors.append("B5 MPS truncation response bond-dimension list mismatch")
        if summary.get("selected_bond_dimension") != b5_mps.get("selected_bond_dimension"):
            errors.append("B5 MPS truncation response selected bond dimension mismatch")
        if summary.get("exact_state_seeded") is not True:
            errors.append("B5 MPS truncation response summary must disclose exact-state seeding")
        if summary.get("variational_dmrg") is not False:
            errors.append("B5 MPS truncation response summary must not claim variational DMRG")
        if summary.get("quantum_response_win_claimed") is not False:
            errors.append("B5 MPS truncation response must not claim a quantum response win")
        if summary.get("accuracy_per_resource_win_claimed") is not False:
            errors.append("B5 MPS truncation response must not claim an accuracy-per-resource win")
        if len(payload.get("validation_errors", [])) != b5_mps.get("validation_error_count"):
            errors.append("B5 MPS truncation response validation-error count mismatch")
        if float(summary.get("selected_max_relative_response_error", 1.0)) > 0.01:
            errors.append("B5 MPS truncation response max response error is above the reference sanity bound")
        if float(summary.get("selected_min_overlap_with_exact_ground_state", 0.0)) < 0.99:
            errors.append("B5 MPS truncation response selected overlap is below the reference sanity bound")
        if len(payload.get("rows", [])) != 9:
            errors.append("B5 MPS truncation response rows must cover all nine D5 B5 instances")
        for row in payload.get("rows", []):
            label = f"sites={row.get('sites')} U/t={row.get('u_over_t')}"
            if row.get("exact_state_seeded") is not True:
                errors.append(f"B5 MPS truncation response row must disclose exact-state seeding: {label}")
            if row.get("variational_dmrg") is not False:
                errors.append(f"B5 MPS truncation response row must not claim variational DMRG: {label}")
            if row.get("candidate_quantum_response_beats_mps_reference") is not False:
                errors.append(f"B5 MPS truncation response row claims a quantum win: {label}")
            if float(row.get("selected_response_relative_residual", 1.0)) > 1e-6:
                errors.append(f"B5 MPS truncation response row residual exceeds tolerance: {label}")

    b5_two_site_dmrg_status = {}
    if not b5_two_site_dmrg:
        warnings.append("B5 manifest has no two-site finite-DMRG response reference")
    else:
        result_path = b5_two_site_dmrg.get("result")
        markdown_path = b5_two_site_dmrg.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B5 two-site finite-DMRG response result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B5 two-site finite-DMRG response markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b5_two_site_dmrg_status = {
            "status": b5_two_site_dmrg.get("status"),
            "method": b5_two_site_dmrg.get("method"),
            "model_status": b5_two_site_dmrg.get("model_status"),
            "dependency_b10_table": b5_two_site_dmrg.get("dependency_b10_table"),
            "instance_count": summary.get("instance_count"),
            "bond_dimensions_tested": summary.get("bond_dimensions_tested"),
            "selected_bond_dimensions": summary.get("selected_bond_dimensions"),
            "restarts_per_instance_bond_dimension": summary.get("restarts_per_instance_bond_dimension"),
            "sweeps_per_restart": summary.get("sweeps_per_restart"),
            "selected_mean_relative_response_error": summary.get("selected_mean_relative_response_error"),
            "selected_max_relative_response_error": summary.get("selected_max_relative_response_error"),
            "selected_mean_energy_error_per_site": summary.get("selected_mean_energy_error_per_site"),
            "selected_max_energy_error_per_site": summary.get("selected_max_energy_error_per_site"),
            "selected_min_overlap_with_exact_ground_state": summary.get(
                "selected_min_overlap_with_exact_ground_state"
            ),
            "selected_min_fixed_sector_norm_before_normalization": summary.get(
                "selected_min_fixed_sector_norm_before_normalization"
            ),
            "two_site_dmrg_rows_beating_seeded_mps_pressure_reference": summary.get(
                "two_site_dmrg_rows_beating_seeded_mps_pressure_reference"
            ),
            "two_site_dmrg_rows_beating_variational_mps_als_reference": summary.get(
                "two_site_dmrg_rows_beating_variational_mps_als_reference"
            ),
            "two_site_finite_dmrg_style": summary.get("two_site_finite_dmrg_style"),
            "canonical_environment_production_dmrg": summary.get("canonical_environment_production_dmrg"),
            "production_dmrg": summary.get("production_dmrg"),
            "exact_state_seeded": summary.get("exact_state_seeded"),
            "quantum_response_win_claimed": summary.get("quantum_response_win_claimed"),
            "accuracy_per_resource_win_claimed": summary.get("accuracy_per_resource_win_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B5":
            errors.append("B5 two-site finite-DMRG response result benchmark_id must be B5")
        if payload.get("method") != b5_two_site_dmrg.get("method"):
            errors.append("B5 two-site finite-DMRG response method mismatch")
        if payload.get("status") != "two_site_finite_dmrg_pressure_reference_not_production_dmrg_or_advantage_claim":
            errors.append("B5 two-site finite-DMRG response status mismatch")
        if payload.get("model_status") != b5_two_site_dmrg.get("model_status"):
            errors.append("B5 two-site finite-DMRG response model_status mismatch")
        if payload.get("dependency_b10_table") != b5_two_site_dmrg.get("dependency_b10_table"):
            errors.append("B5 two-site finite-DMRG response B10 dependency mismatch")
        for field in [
            "instance_count",
            "bond_dimensions_tested",
            "selected_bond_dimensions",
            "restarts_per_instance_bond_dimension",
            "sweeps_per_restart",
            "two_site_dmrg_rows_beating_seeded_mps_pressure_reference",
            "two_site_dmrg_rows_beating_variational_mps_als_reference",
        ]:
            if summary.get(field) != b5_two_site_dmrg.get(field):
                errors.append(f"B5 two-site finite-DMRG response {field} mismatch")
        if summary.get("instance_count") != 9:
            errors.append("B5 two-site finite-DMRG response must cover all nine D5 B5 instances")
        if summary.get("two_site_finite_dmrg_style") is not True:
            errors.append("B5 two-site finite-DMRG response must disclose two-site finite-DMRG style")
        if summary.get("canonical_environment_production_dmrg") is not False:
            errors.append("B5 two-site finite-DMRG response must not claim canonical production DMRG")
        if summary.get("production_dmrg") is not False:
            errors.append("B5 two-site finite-DMRG response must not claim production DMRG")
        if summary.get("exact_state_seeded") is not False:
            errors.append("B5 two-site finite-DMRG response must not be exact-state seeded")
        if summary.get("quantum_response_win_claimed") is not False:
            errors.append("B5 two-site finite-DMRG response must not claim a quantum response win")
        if summary.get("accuracy_per_resource_win_claimed") is not False:
            errors.append("B5 two-site finite-DMRG response must not claim an accuracy-per-resource win")
        if int(summary.get("two_site_dmrg_rows_beating_variational_mps_als_reference", -1)) < 1:
            errors.append("B5 two-site finite-DMRG response should beat one-site ALS on at least one row")
        if int(summary.get("two_site_dmrg_rows_beating_seeded_mps_pressure_reference", -1)) != 0:
            errors.append("B5 two-site finite-DMRG response should not beat the exact-state-seeded pressure reference")
        if len(payload.get("validation_errors", [])) != b5_two_site_dmrg.get("validation_error_count"):
            errors.append("B5 two-site finite-DMRG response validation-error count mismatch")
        claim_boundary = payload.get("claim_boundary", {})
        if claim_boundary.get("production_dmrg") is not False:
            errors.append("B5 two-site finite-DMRG response payload claims production DMRG")
        if claim_boundary.get("quantum_response_win_claimed") is not False:
            errors.append("B5 two-site finite-DMRG response payload claims quantum response win")
        for row in payload.get("rows", []):
            label = f"sites={row.get('sites')} U/t={row.get('u_over_t')}"
            if row.get("two_site_finite_dmrg_style") is not True:
                errors.append(f"B5 two-site finite-DMRG row must disclose optimizer style: {label}")
            if row.get("production_dmrg") is not False:
                errors.append(f"B5 two-site finite-DMRG row must not claim production DMRG: {label}")
            if row.get("exact_state_seeded") is not False:
                errors.append(f"B5 two-site finite-DMRG row must not be exact-state seeded: {label}")
            if row.get("quantum_response_win_claimed") is not False:
                errors.append(f"B5 two-site finite-DMRG row claims quantum response win: {label}")
            if float(row.get("selected_response_relative_residual", 1.0)) > 1e-6:
                errors.append(f"B5 two-site finite-DMRG row residual exceeds tolerance: {label}")

    b5_var_mps_status = {}
    if not b5_var_mps:
        warnings.append("B5 manifest has no variational MPS/ALS response reference")
    else:
        result_path = b5_var_mps.get("result")
        markdown_path = b5_var_mps.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B5 variational MPS/ALS response result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B5 variational MPS/ALS response markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b5_var_mps_status = {
            "status": b5_var_mps.get("status"),
            "method": b5_var_mps.get("method"),
            "model_status": b5_var_mps.get("model_status"),
            "dependency_b10_table": b5_var_mps.get("dependency_b10_table"),
            "instance_count": summary.get("instance_count"),
            "bond_dimensions_tested": summary.get("bond_dimensions_tested"),
            "selected_bond_dimensions": summary.get("selected_bond_dimensions"),
            "restarts_per_instance_bond_dimension": summary.get("restarts_per_instance_bond_dimension"),
            "sweeps_per_restart": summary.get("sweeps_per_restart"),
            "selected_mean_relative_response_error": summary.get("selected_mean_relative_response_error"),
            "selected_max_relative_response_error": summary.get("selected_max_relative_response_error"),
            "selected_mean_energy_error_per_site": summary.get("selected_mean_energy_error_per_site"),
            "selected_max_energy_error_per_site": summary.get("selected_max_energy_error_per_site"),
            "selected_min_overlap_with_exact_ground_state": summary.get(
                "selected_min_overlap_with_exact_ground_state"
            ),
            "selected_min_fixed_sector_norm_before_normalization": summary.get(
                "selected_min_fixed_sector_norm_before_normalization"
            ),
            "variational_mps_rows_beating_seeded_mps_pressure_reference": summary.get(
                "variational_mps_rows_beating_seeded_mps_pressure_reference"
            ),
            "max_exact_d5_hilbert_dimension": summary.get("max_exact_d5_hilbert_dimension"),
            "exact_state_seeded": summary.get("exact_state_seeded"),
            "variational_mps_als": summary.get("variational_mps_als"),
            "production_dmrg": summary.get("production_dmrg"),
            "uses_exact_target_for_selection": summary.get("uses_exact_target_for_selection"),
            "exact_energy_used_for_response_shift": summary.get("exact_energy_used_for_response_shift"),
            "quantum_response_win_claimed": summary.get("quantum_response_win_claimed"),
            "accuracy_per_resource_win_claimed": summary.get("accuracy_per_resource_win_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B5":
            errors.append("B5 variational MPS/ALS response result benchmark_id must be B5")
        if payload.get("method") != b5_var_mps.get("method"):
            errors.append("B5 variational MPS/ALS response method mismatch")
        if payload.get("status") != "variational_mps_als_pressure_reference_not_production_dmrg_or_advantage_claim":
            errors.append("B5 variational MPS/ALS response status must remain a prototype reference")
        if payload.get("model_status") != b5_var_mps.get("model_status"):
            errors.append("B5 variational MPS/ALS response model_status mismatch")
        if payload.get("dependency_b10_table") != b5_var_mps.get("dependency_b10_table"):
            errors.append("B5 variational MPS/ALS response B10 dependency mismatch")
        if payload.get("explicit_not_quantum_advantage") is not True:
            errors.append("B5 variational MPS/ALS response must explicitly avoid quantum-advantage claims")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B5 variational MPS/ALS response must explicitly avoid BQP separation claims")
        if payload.get("explicit_not_production_dmrg") is not True:
            errors.append("B5 variational MPS/ALS response must explicitly avoid production-DMRG claims")
        if payload.get("exact_state_seeded") is not False:
            errors.append("B5 variational MPS/ALS response must not be exact-state seeded")
        if payload.get("production_dmrg") is not False:
            errors.append("B5 variational MPS/ALS response must not claim production DMRG")
        if payload.get("uses_exact_target_for_selection") is not False:
            errors.append("B5 variational MPS/ALS response must not use exact target for selection")
        if summary.get("instance_count") != b5_var_mps.get("instance_count"):
            errors.append("B5 variational MPS/ALS response instance_count mismatch")
        if summary.get("bond_dimensions_tested") != b5_var_mps.get("bond_dimensions_tested"):
            errors.append("B5 variational MPS/ALS response bond-dimension list mismatch")
        if summary.get("selected_bond_dimensions") != b5_var_mps.get("selected_bond_dimensions"):
            errors.append("B5 variational MPS/ALS response selected bond dimensions mismatch")
        if summary.get("restarts_per_instance_bond_dimension") != b5_var_mps.get("restarts_per_instance_bond_dimension"):
            errors.append("B5 variational MPS/ALS response restart count mismatch")
        if summary.get("sweeps_per_restart") != b5_var_mps.get("sweeps_per_restart"):
            errors.append("B5 variational MPS/ALS response sweep count mismatch")
        if summary.get("exact_state_seeded") is not False:
            errors.append("B5 variational MPS/ALS response summary must not be exact-state seeded")
        if summary.get("variational_mps_als") is not True:
            errors.append("B5 variational MPS/ALS response summary must disclose variational MPS/ALS")
        if summary.get("production_dmrg") is not False:
            errors.append("B5 variational MPS/ALS response summary must not claim production DMRG")
        if summary.get("uses_exact_target_for_selection") is not False:
            errors.append("B5 variational MPS/ALS response summary must not use exact target for selection")
        if summary.get("quantum_response_win_claimed") is not False:
            errors.append("B5 variational MPS/ALS response must not claim a quantum response win")
        if summary.get("accuracy_per_resource_win_claimed") is not False:
            errors.append("B5 variational MPS/ALS response must not claim an accuracy-per-resource win")
        if len(payload.get("validation_errors", [])) != b5_var_mps.get("validation_error_count"):
            errors.append("B5 variational MPS/ALS response validation-error count mismatch")
        if float(summary.get("selected_max_relative_response_error", 1.0)) > 0.05:
            errors.append("B5 variational MPS/ALS response max response error is above the prototype bound")
        if float(summary.get("selected_min_overlap_with_exact_ground_state", 0.0)) < 0.95:
            errors.append("B5 variational MPS/ALS response selected overlap is below the prototype bound")
        if int(summary.get("variational_mps_rows_beating_seeded_mps_pressure_reference", -1)) != 0:
            errors.append("B5 variational MPS/ALS response should not beat the seeded pressure reference")
        if len(payload.get("rows", [])) != 9:
            errors.append("B5 variational MPS/ALS response rows must cover all nine D5 B5 instances")
        for row in payload.get("rows", []):
            label = f"sites={row.get('sites')} U/t={row.get('u_over_t')}"
            if row.get("exact_state_seeded") is not False:
                errors.append(f"B5 variational MPS/ALS row must not be exact-state seeded: {label}")
            if row.get("variational_mps_als") is not True:
                errors.append(f"B5 variational MPS/ALS row must disclose optimizer: {label}")
            if row.get("production_dmrg") is not False:
                errors.append(f"B5 variational MPS/ALS row must not claim production DMRG: {label}")
            if row.get("candidate_quantum_response_beats_variational_mps_reference") is not False:
                errors.append(f"B5 variational MPS/ALS row claims a quantum win: {label}")
            if float(row.get("selected_response_relative_residual", 1.0)) > 1e-6:
                errors.append(f"B5 variational MPS/ALS row residual exceeds tolerance: {label}")

    b6_manifest = yaml.safe_load(read(b6_manifest_path))
    b6_results = b6_manifest.get("current_results", {})
    b6_descriptor = b6_results.get("toy_superconductivity_descriptor_ranker_v0")
    b6_curated = b6_results.get("b6_curated_materials_leakage_audit_v0")
    b6_formula = b6_results.get("b6_formula_descriptor_screen_v0")
    b6_structural = b6_results.get("b6_structural_electronic_proxy_screen_v0")
    b6_status = {}
    b6_curated_status = {}
    b6_formula_status = {}
    b6_structural_status = {}
    if not b6_descriptor:
        warnings.append("B6 manifest has no superconductivity descriptor ranking result")
    else:
        result_path = b6_descriptor.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B6 descriptor result path missing: {result_path}")
        if b6_descriptor.get("model_status") != "toy_descriptor_ranking_not_material_discovery_claim":
            errors.append("B6 result must be explicitly marked as not a material discovery claim")
        if float(b6_descriptor.get("known_high_tc_precision_at_k", 0.0)) < 0.5:
            errors.append("B6 descriptor precision@k is below the first-pass threshold")
        top_family_counts = b6_descriptor.get("top_family_counts", {})
        if len(top_family_counts) < 2:
            errors.append("B6 descriptor top-k contains fewer than 2 families")
        if result_exists:
            payload = json.loads(read((benchmarks / result_path).resolve()))
            if payload.get("benchmark_id") != "B6":
                errors.append(f"B6 result benchmark_id={payload.get('benchmark_id')!r}, expected 'B6'")
            if payload.get("method") != "toy_superconductivity_descriptor_ranker_v0":
                errors.append(f"B6 result method={payload.get('method')!r}, expected toy_superconductivity_descriptor_ranker_v0")
            if payload.get("candidate_count") != b6_descriptor.get("candidate_count"):
                errors.append("B6 result candidate_count differs from manifest")
            if payload.get("top_k") != b6_descriptor.get("top_k"):
                errors.append("B6 result top_k differs from manifest")
            if payload.get("model_status") != b6_descriptor.get("model_status"):
                errors.append("B6 result model_status differs from manifest")
            if payload.get("top_family_counts") != top_family_counts:
                errors.append("B6 result top_family_counts differs from manifest")
        b6_status = {
            "status": b6_descriptor.get("status"),
            "model_status": b6_descriptor.get("model_status"),
            "candidate_count": b6_descriptor.get("candidate_count"),
            "top_k": b6_descriptor.get("top_k"),
            "known_high_tc_precision_at_k": b6_descriptor.get("known_high_tc_precision_at_k"),
            "known_high_tc_recall_at_k": b6_descriptor.get("known_high_tc_recall_at_k"),
            "top_family_counts": b6_descriptor.get("top_family_counts"),
            "result_exists": result_exists,
            "result": result_path,
        }
    if not b6_curated:
        warnings.append("B6 manifest has no curated materials leakage audit result")
    else:
        result_path = b6_curated.get("result")
        markdown_path = b6_curated.get("markdown")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B6 curated leakage audit result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B6 curated leakage audit markdown path missing: {markdown_path}")
        if b6_curated.get("model_status") != "curated_materials_table_with_time_family_leakage_audit":
            errors.append("B6 curated leakage audit must disclose curated leakage-audit model status")
        if b6_curated.get("material_discovery_claimed") is not False:
            errors.append("B6 curated leakage audit must not claim material discovery")
        if b6_curated.get("mechanism_solved") is not False:
            errors.append("B6 curated leakage audit must not claim solved high-Tc mechanism")
        if b6_curated.get("complete_materials_database") is not False:
            errors.append("B6 curated leakage audit must not claim complete database coverage")
        if int(b6_curated.get("record_count", 0)) < 24:
            errors.append("B6 curated leakage audit must contain at least 24 records")
        if int(b6_curated.get("family_count", 0)) < 8:
            errors.append("B6 curated leakage audit must contain at least 8 families")
        if int(b6_curated.get("post_split_record_count", 0)) < 6:
            errors.append("B6 curated leakage audit post-split set is too small")
        if int(b6_curated.get("validation_error_count", -1)) != 0:
            errors.append("B6 curated leakage audit validation errors must be zero")
        if result_exists:
            payload = json.loads(read((benchmarks / result_path).resolve()))
            if payload.get("benchmark_id") != "B6":
                errors.append(f"B6 curated leakage audit benchmark_id={payload.get('benchmark_id')!r}, expected 'B6'")
            if payload.get("method") != "b6_curated_materials_leakage_audit_v0":
                errors.append("B6 curated leakage audit method mismatch")
            if payload.get("status") != "curated_retrospective_leakage_audit_not_material_discovery_claim":
                errors.append("B6 curated leakage audit status must be a non-discovery claim")
            if payload.get("record_count") != b6_curated.get("record_count"):
                errors.append("B6 curated leakage audit record_count differs from manifest")
            if payload.get("family_count") != b6_curated.get("family_count"):
                errors.append("B6 curated leakage audit family_count differs from manifest")
            if payload.get("post_split_record_count") != b6_curated.get("post_split_record_count"):
                errors.append("B6 curated leakage audit post_split_record_count differs from manifest")
            if len(payload.get("validation_errors", [])) != b6_curated.get("validation_error_count"):
                errors.append("B6 curated leakage audit validation-error count mismatch")
            claim_boundary = payload.get("claim_boundary", {})
            if claim_boundary.get("material_discovery_claimed") is not False:
                errors.append("B6 curated leakage audit payload claims material discovery")
            if claim_boundary.get("mechanism_solved") is not False:
                errors.append("B6 curated leakage audit payload claims solved mechanism")
            metrics = payload.get("metrics", {})
            if metrics.get("post_split_physics_average_precision_at_k") != b6_curated.get("post_split_physics_average_precision_at_k"):
                errors.append("B6 curated leakage audit post-split physics AP differs from manifest")
        b6_curated_status = {
            "status": b6_curated.get("status"),
            "model_status": b6_curated.get("model_status"),
            "record_count": b6_curated.get("record_count"),
            "family_count": b6_curated.get("family_count"),
            "split_year": b6_curated.get("split_year"),
            "post_split_record_count": b6_curated.get("post_split_record_count"),
            "post_split_positive_count": b6_curated.get("post_split_positive_count"),
            "top_k": b6_curated.get("top_k"),
            "all_physics_average_precision_at_k": b6_curated.get("all_physics_average_precision_at_k"),
            "all_random_average_precision_at_k_mean": b6_curated.get("all_random_average_precision_at_k_mean"),
            "post_split_physics_average_precision_at_k": b6_curated.get("post_split_physics_average_precision_at_k"),
            "post_split_family_prior_average_precision_at_k": b6_curated.get("post_split_family_prior_average_precision_at_k"),
            "post_split_random_average_precision_at_k_mean": b6_curated.get("post_split_random_average_precision_at_k_mean"),
            "family_holdout_mean_physics_ap": b6_curated.get("family_holdout_mean_physics_ap"),
            "family_holdout_mean_random_ap": b6_curated.get("family_holdout_mean_random_ap"),
            "validation_error_count": b6_curated.get("validation_error_count"),
            "material_discovery_claimed": b6_curated.get("material_discovery_claimed"),
            "mechanism_solved": b6_curated.get("mechanism_solved"),
            "complete_materials_database": b6_curated.get("complete_materials_database"),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown": markdown_path,
        }
    if not b6_formula:
        warnings.append("B6 manifest has no formula-derived descriptor screen result")
    else:
        result_path = b6_formula.get("result")
        markdown_path = b6_formula.get("markdown")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B6 formula descriptor screen result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B6 formula descriptor screen markdown path missing: {markdown_path}")
        if b6_formula.get("method") != "b6_formula_descriptor_screen_v0":
            errors.append("B6 formula descriptor screen method mismatch")
        if b6_formula.get("status") != "formula_descriptor_screen_not_material_discovery_claim":
            errors.append("B6 formula descriptor screen status must be a non-discovery claim")
        if b6_formula.get("model_status") != "formula_element_table_descriptors_with_b5_correlation_proxy_not_material_discovery":
            errors.append("B6 formula descriptor screen model status mismatch")
        if int(b6_formula.get("expanded_negative_control_count", 0)) < 10:
            errors.append("B6 formula descriptor screen must contain at least 10 expanded negative controls")
        if int(b6_formula.get("validation_error_count", -1)) != 0:
            errors.append("B6 formula descriptor screen validation errors must be zero")
        for claim_key in [
            "material_discovery_claimed",
            "mechanism_solved",
            "complete_materials_database",
            "computed_quantum_observable_claimed",
        ]:
            if b6_formula.get(claim_key) is not False:
                errors.append(f"B6 formula descriptor screen must not claim {claim_key}")
        if b6_formula.get("uses_formula_derived_descriptors") is not True:
            errors.append("B6 formula descriptor screen must disclose formula-derived descriptors")
        if b6_formula.get("uses_b5_linked_proxy") is not True:
            errors.append("B6 formula descriptor screen must disclose B5-linked proxy usage")
        if result_exists:
            payload = json.loads(read((benchmarks / result_path).resolve()))
            if payload.get("benchmark_id") != "B6":
                errors.append(f"B6 formula descriptor screen benchmark_id={payload.get('benchmark_id')!r}, expected 'B6'")
            if payload.get("method") != b6_formula.get("method"):
                errors.append("B6 formula descriptor screen payload method differs from manifest")
            if payload.get("status") != b6_formula.get("status"):
                errors.append("B6 formula descriptor screen payload status differs from manifest")
            if payload.get("model_status") != b6_formula.get("model_status"):
                errors.append("B6 formula descriptor screen payload model status differs from manifest")
            for field in [
                "record_count",
                "curated_record_count",
                "expanded_negative_control_count",
                "family_count",
                "post_split_record_count",
                "post_split_positive_count",
                "top_k",
            ]:
                if payload.get(field) != b6_formula.get(field):
                    errors.append(f"B6 formula descriptor screen {field} differs from manifest")
            if len(payload.get("validation_errors", [])) != b6_formula.get("validation_error_count"):
                errors.append("B6 formula descriptor screen validation-error count mismatch")
            metrics = payload.get("metrics", {})
            for metric in [
                "formula_average_precision_at_k",
                "family_prior_average_precision_at_k",
                "post_split_formula_average_precision_at_k",
                "post_split_family_prior_average_precision_at_k",
            ]:
                if metrics.get(metric) != b6_formula.get(metric):
                    errors.append(f"B6 formula descriptor screen {metric} differs from manifest")
            claim_boundary = payload.get("claim_boundary", {})
            for claim_key in [
                "material_discovery_claimed",
                "mechanism_solved",
                "complete_materials_database",
                "computed_quantum_observable_claimed",
            ]:
                if claim_boundary.get(claim_key) is not False:
                    errors.append(f"B6 formula descriptor screen payload claims {claim_key}")
            if claim_boundary.get("uses_formula_derived_descriptors") is not True:
                errors.append("B6 formula descriptor screen payload hides formula-derived descriptor status")
            if claim_boundary.get("uses_b5_linked_proxy") is not True:
                errors.append("B6 formula descriptor screen payload hides B5-linked proxy status")
        b6_formula_status = {
            "status": b6_formula.get("status"),
            "method": b6_formula.get("method"),
            "model_status": b6_formula.get("model_status"),
            "record_count": b6_formula.get("record_count"),
            "curated_record_count": b6_formula.get("curated_record_count"),
            "expanded_negative_control_count": b6_formula.get("expanded_negative_control_count"),
            "family_count": b6_formula.get("family_count"),
            "split_year": b6_formula.get("split_year"),
            "post_split_record_count": b6_formula.get("post_split_record_count"),
            "post_split_positive_count": b6_formula.get("post_split_positive_count"),
            "top_k": b6_formula.get("top_k"),
            "formula_average_precision_at_k": b6_formula.get("formula_average_precision_at_k"),
            "family_prior_average_precision_at_k": b6_formula.get("family_prior_average_precision_at_k"),
            "post_split_formula_average_precision_at_k": b6_formula.get("post_split_formula_average_precision_at_k"),
            "post_split_family_prior_average_precision_at_k": b6_formula.get("post_split_family_prior_average_precision_at_k"),
            "validation_error_count": b6_formula.get("validation_error_count"),
            "material_discovery_claimed": b6_formula.get("material_discovery_claimed"),
            "mechanism_solved": b6_formula.get("mechanism_solved"),
            "complete_materials_database": b6_formula.get("complete_materials_database"),
            "computed_quantum_observable_claimed": b6_formula.get("computed_quantum_observable_claimed"),
            "uses_formula_derived_descriptors": b6_formula.get("uses_formula_derived_descriptors"),
            "uses_b5_linked_proxy": b6_formula.get("uses_b5_linked_proxy"),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown": markdown_path,
        }

    if not b6_structural:
        warnings.append("B6 manifest has no structural/electronic proxy screen result")
    else:
        result_path = b6_structural.get("result")
        markdown_path = b6_structural.get("markdown")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B6 structural/electronic proxy result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B6 structural/electronic proxy markdown path missing: {markdown_path}")
        if b6_structural.get("method") != "b6_structural_electronic_proxy_screen_v0":
            errors.append("B6 structural/electronic proxy method mismatch")
        if b6_structural.get("status") != "structural_electronic_proxy_boundary_not_material_discovery_claim":
            errors.append("B6 structural/electronic proxy status must be a non-discovery claim")
        if b6_structural.get("model_status") != "curated_structural_electronic_proxies_not_dft_or_crystallographic_database":
            errors.append("B6 structural/electronic proxy model status mismatch")
        if int(b6_structural.get("expanded_negative_control_count", 0)) < 10:
            errors.append("B6 structural/electronic proxy must keep expanded negative controls")
        if int(b6_structural.get("top_k_negative_control_count", 0)) < 1:
            errors.append("B6 structural/electronic proxy should expose top-k negative-control pressure")
        if int(b6_structural.get("validation_error_count", -1)) != 0:
            errors.append("B6 structural/electronic proxy validation errors must be zero")
        if float(b6_structural.get("structural_average_precision_at_k", 0.0)) <= float(
            b6_structural.get("formula_average_precision_at_k", 0.0)
        ):
            errors.append("B6 structural/electronic proxy should improve over formula AP")
        if float(b6_structural.get("structural_average_precision_at_k", 0.0)) >= float(
            b6_structural.get("family_prior_average_precision_at_k", 0.0)
        ):
            errors.append("B6 structural/electronic proxy must not overclaim beating family prior")
        for claim_key in [
            "material_discovery_claimed",
            "mechanism_solved",
            "complete_materials_database",
            "computed_quantum_observable_claimed",
            "real_dft_claimed",
            "real_crystallographic_database_claimed",
        ]:
            if b6_structural.get(claim_key) is not False:
                errors.append(f"B6 structural/electronic proxy must not claim {claim_key}")
        if b6_structural.get("uses_structural_electronic_proxies") is not True:
            errors.append("B6 structural/electronic proxy must disclose structural/electronic proxies")
        if b6_structural.get("uses_b5_linked_proxy") is not True:
            errors.append("B6 structural/electronic proxy must disclose B5-linked proxy usage")
        if result_exists:
            payload = json.loads(read((benchmarks / result_path).resolve()))
            if payload.get("benchmark_id") != "B6":
                errors.append(f"B6 structural/electronic proxy benchmark_id={payload.get('benchmark_id')!r}, expected 'B6'")
            if payload.get("method") != b6_structural.get("method"):
                errors.append("B6 structural/electronic proxy payload method differs from manifest")
            if payload.get("status") != b6_structural.get("status"):
                errors.append("B6 structural/electronic proxy payload status differs from manifest")
            if payload.get("model_status") != b6_structural.get("model_status"):
                errors.append("B6 structural/electronic proxy payload model status differs from manifest")
            for field in [
                "record_count",
                "curated_record_count",
                "expanded_negative_control_count",
                "family_count",
                "post_split_record_count",
                "post_split_positive_count",
                "top_k",
            ]:
                if payload.get(field) != b6_structural.get(field):
                    errors.append(f"B6 structural/electronic proxy {field} differs from manifest")
            if len(payload.get("validation_errors", [])) != b6_structural.get("validation_error_count"):
                errors.append("B6 structural/electronic proxy validation-error count mismatch")
            metrics = payload.get("metrics", {})
            for metric in [
                "structural_average_precision_at_k",
                "formula_average_precision_at_k",
                "family_prior_average_precision_at_k",
                "post_split_structural_average_precision_at_k",
                "post_split_family_prior_average_precision_at_k",
                "family_holdout_structural_mean_ap",
                "top_k_negative_control_count",
                "structural_minus_formula_ap",
                "structural_minus_family_prior_ap",
            ]:
                if metrics.get(metric) != b6_structural.get(metric):
                    errors.append(f"B6 structural/electronic proxy {metric} differs from manifest")
            claim_boundary = payload.get("claim_boundary", {})
            for claim_key in [
                "material_discovery_claimed",
                "mechanism_solved",
                "complete_materials_database",
                "computed_quantum_observable_claimed",
                "real_dft_claimed",
                "real_crystallographic_database_claimed",
            ]:
                if claim_boundary.get(claim_key) is not False:
                    errors.append(f"B6 structural/electronic proxy payload claims {claim_key}")
            if claim_boundary.get("uses_structural_electronic_proxies") is not True:
                errors.append("B6 structural/electronic proxy payload hides proxy status")
            if claim_boundary.get("uses_b5_linked_proxy") is not True:
                errors.append("B6 structural/electronic proxy payload hides B5-linked proxy status")
        b6_structural_status = {
            "status": b6_structural.get("status"),
            "method": b6_structural.get("method"),
            "model_status": b6_structural.get("model_status"),
            "record_count": b6_structural.get("record_count"),
            "expanded_negative_control_count": b6_structural.get("expanded_negative_control_count"),
            "family_count": b6_structural.get("family_count"),
            "top_k": b6_structural.get("top_k"),
            "structural_average_precision_at_k": b6_structural.get("structural_average_precision_at_k"),
            "formula_average_precision_at_k": b6_structural.get("formula_average_precision_at_k"),
            "family_prior_average_precision_at_k": b6_structural.get("family_prior_average_precision_at_k"),
            "post_split_structural_average_precision_at_k": b6_structural.get(
                "post_split_structural_average_precision_at_k"
            ),
            "post_split_family_prior_average_precision_at_k": b6_structural.get(
                "post_split_family_prior_average_precision_at_k"
            ),
            "family_holdout_structural_mean_ap": b6_structural.get("family_holdout_structural_mean_ap"),
            "top_k_negative_control_count": b6_structural.get("top_k_negative_control_count"),
            "structural_minus_formula_ap": b6_structural.get("structural_minus_formula_ap"),
            "structural_minus_family_prior_ap": b6_structural.get("structural_minus_family_prior_ap"),
            "validation_error_count": b6_structural.get("validation_error_count"),
            "material_discovery_claimed": b6_structural.get("material_discovery_claimed"),
            "mechanism_solved": b6_structural.get("mechanism_solved"),
            "complete_materials_database": b6_structural.get("complete_materials_database"),
            "computed_quantum_observable_claimed": b6_structural.get("computed_quantum_observable_claimed"),
            "real_dft_claimed": b6_structural.get("real_dft_claimed"),
            "real_crystallographic_database_claimed": b6_structural.get("real_crystallographic_database_claimed"),
            "uses_structural_electronic_proxies": b6_structural.get("uses_structural_electronic_proxies"),
            "uses_b5_linked_proxy": b6_structural.get("uses_b5_linked_proxy"),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown": markdown_path,
        }

    b7_manifest = yaml.safe_load(read(b7_manifest_path))
    b7_results = b7_manifest.get("current_results", {})
    b7_codesign = b7_results.get("fault_tolerance_codesign_resource_model_v0")
    b7_bridge = b7_results.get("b1_b2_dependency_schedule_bridge_v0")
    b7_workload_dag = b7_results.get("workload_dag_factory_schedule_v0")
    b7_logical_t = b7_results.get("logical_t_factory_schedule_v0")
    b7_logical_t_post_1q = b7_results.get("logical_t_factory_schedule_post_1q_v0")
    b7_logical_t_native = b7_results.get("logical_t_factory_schedule_native_v0")
    b7_logical_t_control_rz = b7_results.get("logical_t_factory_schedule_control_rz_v0")
    b7_logical_t_u3_phase_factored = b7_results.get("logical_t_factory_schedule_u3_phase_factored_v0")
    b7_min_stv_classifier = b7_results.get("min_stv_regime_classifier_v0")
    b7_ft_synthesis_ledger = b7_results.get("ft_synthesis_ledger_v0")
    b7_gcm_h6_boundary = b7_results.get("gcm_h6_ft_boundary_v0")
    b7_precision_rotation_ledger = b7_results.get("precision_aware_rotation_ledger_v0")
    b7_gcm_h6_numeric_structure = b7_results.get("gcm_h6_numeric_rotation_structure_v0")
    b7_shared_synthesis_cache = b7_results.get("shared_synthesis_cache_boundary_v0")
    b7_nonlocal_template_block_scan = b7_results.get("nonlocal_template_block_scan_v0")
    b7_template_priority_gate = b7_results.get("template_priority_gate_v0")
    b7_w8_21_small_block_synthesis = b7_results.get("w8_21_small_block_synthesis_v0")
    b7_w8_21_broad_skeleton_search = b7_results.get("w8_21_broad_skeleton_search_v0")
    b7_w8_21_euler_local_search = b7_results.get("w8_21_euler_local_search_v0")
    b7_w8_21_three_cnot_search = b7_results.get("w8_21_three_cnot_search_v0")
    b7_w8_21_scoped_minimality_note = b7_results.get("w8_21_scoped_minimality_note_v0")
    b7_w8_21_claim_boundary_fragment = b7_results.get("w8_21_claim_boundary_fragment_v0")
    b7_status = {}
    if not b7_codesign:
        warnings.append("B7 manifest has no fault-tolerance co-design resource result")
    else:
        result_path = b7_codesign.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 co-design result path missing: {result_path}")
        if b7_codesign.get("model_status") != "planning_level_resource_model_not_physical_layout":
            errors.append("B7 result must be explicitly marked as planning-level, not physical layout")
        if float(b7_codesign.get("min_space_time_volume_reduction", 0.0)) < 1.25:
            errors.append("B7 minimum space-time-volume reduction is below the first-pass threshold")
        if int(b7_codesign.get("workloads_meeting_25_percent_reduction", 0)) < 2:
            errors.append("B7 has fewer than 2 workloads meeting the 25% reduction threshold")
        if result_exists:
            payload = json.loads(read((benchmarks / result_path).resolve()))
            if payload.get("benchmark_id") != "B7":
                errors.append(f"B7 result benchmark_id={payload.get('benchmark_id')!r}, expected 'B7'")
            if payload.get("method") != "fault_tolerance_codesign_resource_model_v0":
                errors.append(f"B7 result method={payload.get('method')!r}, expected fault_tolerance_codesign_resource_model_v0")
            if payload.get("configuration_count") != b7_codesign.get("configuration_count"):
                errors.append("B7 result configuration_count differs from manifest")
            if payload.get("model_status") != b7_codesign.get("model_status"):
                errors.append("B7 result model_status differs from manifest")
            if payload.get("workloads_meeting_25_percent_reduction") != b7_codesign.get("workloads_meeting_25_percent_reduction"):
                errors.append("B7 result workload-threshold count differs from manifest")
        b7_status = {
            "status": b7_codesign.get("status"),
            "model_status": b7_codesign.get("model_status"),
            "workload_count": b7_codesign.get("workload_count"),
            "configuration_count": b7_codesign.get("configuration_count"),
            "min_space_time_volume_reduction": b7_codesign.get("min_space_time_volume_reduction"),
            "mean_space_time_volume_reduction": b7_codesign.get("mean_space_time_volume_reduction"),
            "workloads_meeting_25_percent_reduction": b7_codesign.get("workloads_meeting_25_percent_reduction"),
            "result_exists": result_exists,
            "result": result_path,
        }
    b7_bridge_status = {}
    if not b7_bridge:
        warnings.append("B7 manifest has no B1/B2 dependency-schedule bridge")
    else:
        result_path = b7_bridge.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 dependency-schedule bridge result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b7_bridge_status = {
            "status": b7_bridge.get("status"),
            "method": b7_bridge.get("method"),
            "comparison_count": b7_bridge.get("comparison_count"),
            "min_space_time_volume_reduction": b7_bridge.get("min_space_time_volume_reduction"),
            "mean_space_time_volume_reduction": b7_bridge.get("mean_space_time_volume_reduction"),
            "min_exposure_reduction": b7_bridge.get("min_exposure_reduction"),
            "selected_b2_distance": b7_bridge.get("selected_b2_distance"),
            "selected_b2_target_logical_error": b7_bridge.get("selected_b2_target_logical_error"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "dependency_schedule_bridge_not_physical_layout":
            errors.append("B7 dependency bridge must be marked as not a physical layout")
        if payload.get("method") != b7_bridge.get("method"):
            errors.append("B7 dependency bridge method mismatch")
        if payload.get("comparison_count") != b7_bridge.get("comparison_count"):
            errors.append("B7 dependency bridge comparison count mismatch")
        if payload.get("min_space_time_volume_reduction") != b7_bridge.get("min_space_time_volume_reduction"):
            errors.append("B7 dependency bridge min space-time reduction mismatch")

    b7_workload_dag_status = {}
    if not b7_workload_dag:
        warnings.append("B7 manifest has no workload DAG factory schedule")
    else:
        result_path = b7_workload_dag.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 workload DAG factory schedule result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b7_workload_dag_status = {
            "status": b7_workload_dag.get("status"),
            "method": b7_workload_dag.get("method"),
            "workload_count": b7_workload_dag.get("workload_count"),
            "comparison_count": b7_workload_dag.get("comparison_count"),
            "factory_variants": b7_workload_dag.get("factory_variants"),
            "magic_state_density_proxy": b7_workload_dag.get("magic_state_density_proxy"),
            "min_space_time_volume_reduction": payload.get("min_space_time_volume_reduction"),
            "mean_space_time_volume_reduction": payload.get("mean_space_time_volume_reduction"),
            "factory_bottleneck_comparisons": payload.get("factory_bottleneck_comparisons"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "workload_dag_factory_schedule_not_physical_layout":
            errors.append("B7 workload DAG factory schedule must remain marked as not physical layout")
        if payload.get("method") != b7_workload_dag.get("method"):
            errors.append("B7 workload DAG factory schedule method mismatch")
        if payload.get("comparison_count") != b7_workload_dag.get("comparison_count"):
            errors.append("B7 workload DAG factory schedule comparison count mismatch")
        if float(payload.get("min_space_time_volume_reduction", 0.0)) <= 1.0:
            errors.append("B7 workload DAG factory schedule should preserve >1x minimum STV reduction")
        if int(payload.get("factory_bottleneck_comparisons", 0)) < 1:
            errors.append("B7 workload DAG factory schedule should include at least one factory bottleneck comparison")

    b7_logical_t_status = {}
    if not b7_logical_t:
        warnings.append("B7 manifest has no logical T factory schedule")
    else:
        result_path = b7_logical_t.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 logical T factory schedule result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b7_logical_t_status = {
            "status": b7_logical_t.get("status"),
            "method": b7_logical_t.get("method"),
            "workload_count": b7_logical_t.get("workload_count"),
            "comparison_count": b7_logical_t.get("comparison_count"),
            "factory_variants": b7_logical_t.get("factory_variants"),
            "rotation_synthesis_t_cost": b7_logical_t.get("rotation_synthesis_t_cost"),
            "min_space_time_volume_reduction": payload.get("min_space_time_volume_reduction"),
            "mean_space_time_volume_reduction": payload.get("mean_space_time_volume_reduction"),
            "factory_bottleneck_comparisons": payload.get("factory_bottleneck_comparisons"),
            "mean_logical_t_count_reduction": payload.get("mean_logical_t_count_reduction"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "logical_t_factory_schedule_proxy_not_physical_layout":
            errors.append("B7 logical T factory schedule must remain marked as proxy, not physical layout")
        if payload.get("method") != b7_logical_t.get("method"):
            errors.append("B7 logical T factory schedule method mismatch")
        if payload.get("comparison_count") != b7_logical_t.get("comparison_count"):
            errors.append("B7 logical T factory schedule comparison count mismatch")
        if int(payload.get("factory_bottleneck_comparisons", 0)) < int(payload.get("comparison_count", 0)):
            errors.append("B7 logical T factory schedule should expose factory dominance in every comparison")
        if float(payload.get("mean_logical_t_count_reduction", 0.0)) != 1.0:
            errors.append("B7 logical T factory schedule should record no T-count reduction for the current B1 virtual-SWAP pass")

    b7_logical_t_post_1q_status = {}
    if not b7_logical_t_post_1q:
        warnings.append("B7 manifest has no post-1Q logical T factory schedule")
    else:
        result_path = b7_logical_t_post_1q.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 post-1Q logical T factory schedule result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b7_logical_t_post_1q_status = {
            "status": b7_logical_t_post_1q.get("status"),
            "method": b7_logical_t_post_1q.get("method"),
            "workload_count": b7_logical_t_post_1q.get("workload_count"),
            "comparison_count": b7_logical_t_post_1q.get("comparison_count"),
            "factory_variants": b7_logical_t_post_1q.get("factory_variants"),
            "rotation_synthesis_t_cost": b7_logical_t_post_1q.get("rotation_synthesis_t_cost"),
            "min_space_time_volume_reduction": payload.get("min_space_time_volume_reduction"),
            "mean_space_time_volume_reduction": payload.get("mean_space_time_volume_reduction"),
            "factory_bottleneck_comparisons": payload.get("factory_bottleneck_comparisons"),
            "min_logical_t_count_reduction": payload.get("min_logical_t_count_reduction"),
            "mean_logical_t_count_reduction": payload.get("mean_logical_t_count_reduction"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "logical_t_factory_schedule_proxy_not_physical_layout":
            errors.append("B7 post-1Q logical T factory schedule must remain marked as proxy, not physical layout")
        if payload.get("method") != b7_logical_t_post_1q.get("method"):
            errors.append("B7 post-1Q logical T factory schedule method mismatch")
        if payload.get("comparison_count") != b7_logical_t_post_1q.get("comparison_count"):
            errors.append("B7 post-1Q logical T factory schedule comparison count mismatch")
        if int(payload.get("factory_bottleneck_comparisons", 0)) < int(payload.get("comparison_count", 0)):
            errors.append("B7 post-1Q logical T factory schedule should keep exposing factory dominance")
        if float(payload.get("mean_space_time_volume_reduction", 0.0)) <= 1.0:
            errors.append("B7 post-1Q logical T factory schedule should show a positive mean STV signal")
        if float(payload.get("min_space_time_volume_reduction", 0.0)) != 1.0:
            errors.append("B7 post-1Q logical T factory schedule should preserve the unsolved min-STV boundary")

    b7_logical_t_native_status = {}
    if not b7_logical_t_native:
        errors.append("B7 manifest missing native logical T factory schedule")
    else:
        result_path = b7_logical_t_native.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 native logical T factory schedule result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b7_logical_t_native_status = {
            "status": b7_logical_t_native.get("status"),
            "method": b7_logical_t_native.get("method"),
            "workload_count": b7_logical_t_native.get("workload_count"),
            "comparison_count": b7_logical_t_native.get("comparison_count"),
            "factory_variants": b7_logical_t_native.get("factory_variants"),
            "rotation_synthesis_t_cost": b7_logical_t_native.get("rotation_synthesis_t_cost"),
            "min_space_time_volume_reduction": payload.get("min_space_time_volume_reduction"),
            "mean_space_time_volume_reduction": payload.get("mean_space_time_volume_reduction"),
            "factory_bottleneck_comparisons": payload.get("factory_bottleneck_comparisons"),
            "min_logical_t_count_reduction": payload.get("min_logical_t_count_reduction"),
            "mean_logical_t_count_reduction": payload.get("mean_logical_t_count_reduction"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "logical_t_factory_schedule_proxy_not_physical_layout":
            errors.append("B7 native logical T factory schedule must remain marked as proxy, not physical layout")
        if payload.get("method") != b7_logical_t_native.get("method"):
            errors.append("B7 native logical T factory schedule method mismatch")
        if payload.get("comparison_count") != b7_logical_t_native.get("comparison_count"):
            errors.append("B7 native logical T factory schedule comparison count mismatch")
        if int(payload.get("factory_bottleneck_comparisons", 0)) < int(payload.get("comparison_count", 0)):
            errors.append("B7 native logical T factory schedule should keep exposing factory dominance")
        if float(payload.get("mean_space_time_volume_reduction", 0.0)) <= float(
            b7_logical_t_post_1q_status.get("mean_space_time_volume_reduction", 0.0)
        ):
            errors.append("B7 native logical T factory schedule should improve mean STV beyond post-1Q")
        if float(payload.get("min_space_time_volume_reduction", 0.0)) != 1.0:
            errors.append("B7 native logical T factory schedule should preserve the unsolved min-STV boundary")

    b7_logical_t_control_rz_status = {}
    if not b7_logical_t_control_rz:
        errors.append("B7 manifest missing control-RZ logical T factory schedule")
    else:
        result_path = b7_logical_t_control_rz.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 control-RZ logical T factory schedule result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b7_logical_t_control_rz_status = {
            "status": b7_logical_t_control_rz.get("status"),
            "method": b7_logical_t_control_rz.get("method"),
            "workload_count": b7_logical_t_control_rz.get("workload_count"),
            "comparison_count": b7_logical_t_control_rz.get("comparison_count"),
            "factory_variants": b7_logical_t_control_rz.get("factory_variants"),
            "rotation_synthesis_t_cost": b7_logical_t_control_rz.get("rotation_synthesis_t_cost"),
            "min_space_time_volume_reduction": payload.get("min_space_time_volume_reduction"),
            "mean_space_time_volume_reduction": payload.get("mean_space_time_volume_reduction"),
            "factory_bottleneck_comparisons": payload.get("factory_bottleneck_comparisons"),
            "min_logical_t_count_reduction": payload.get("min_logical_t_count_reduction"),
            "mean_logical_t_count_reduction": payload.get("mean_logical_t_count_reduction"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "logical_t_factory_schedule_proxy_not_physical_layout":
            errors.append("B7 control-RZ logical T factory schedule must remain marked as proxy, not physical layout")
        if payload.get("method") != b7_logical_t_control_rz.get("method"):
            errors.append("B7 control-RZ logical T factory schedule method mismatch")
        if payload.get("comparison_count") != b7_logical_t_control_rz.get("comparison_count"):
            errors.append("B7 control-RZ logical T factory schedule comparison count mismatch")
        if int(payload.get("factory_bottleneck_comparisons", 0)) < int(payload.get("comparison_count", 0)):
            errors.append("B7 control-RZ logical T factory schedule should keep exposing factory dominance")
        if float(payload.get("mean_space_time_volume_reduction", 0.0)) <= float(
            b7_logical_t_native_status.get("mean_space_time_volume_reduction", 0.0)
        ):
            errors.append("B7 control-RZ logical T factory schedule should improve mean STV beyond native")
        if float(payload.get("min_space_time_volume_reduction", 0.0)) <= 1.0:
            errors.append("B7 control-RZ logical T factory schedule should break the previous 1x min-STV boundary")

    b7_logical_t_u3_phase_factored_status = {}
    if not b7_logical_t_u3_phase_factored:
        errors.append("B7 manifest missing U3 phase-factored logical T factory schedule")
    else:
        result_path = b7_logical_t_u3_phase_factored.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 U3 phase-factored logical T factory schedule result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b7_logical_t_u3_phase_factored_status = {
            "status": b7_logical_t_u3_phase_factored.get("status"),
            "method": b7_logical_t_u3_phase_factored.get("method"),
            "workload_count": b7_logical_t_u3_phase_factored.get("workload_count"),
            "comparison_count": b7_logical_t_u3_phase_factored.get("comparison_count"),
            "factory_variants": b7_logical_t_u3_phase_factored.get("factory_variants"),
            "rotation_synthesis_t_cost": b7_logical_t_u3_phase_factored.get("rotation_synthesis_t_cost"),
            "min_space_time_volume_reduction": payload.get("min_space_time_volume_reduction"),
            "mean_space_time_volume_reduction": payload.get("mean_space_time_volume_reduction"),
            "factory_bottleneck_comparisons": payload.get("factory_bottleneck_comparisons"),
            "min_logical_t_count_reduction": payload.get("min_logical_t_count_reduction"),
            "mean_logical_t_count_reduction": payload.get("mean_logical_t_count_reduction"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "logical_t_factory_schedule_proxy_not_physical_layout":
            errors.append("B7 U3 phase-factored logical T factory schedule must remain marked as proxy, not physical layout")
        if payload.get("method") != b7_logical_t_u3_phase_factored.get("method"):
            errors.append("B7 U3 phase-factored logical T factory schedule method mismatch")
        if payload.get("comparison_count") != b7_logical_t_u3_phase_factored.get("comparison_count"):
            errors.append("B7 U3 phase-factored logical T factory schedule comparison count mismatch")
        if int(payload.get("factory_bottleneck_comparisons", 0)) < int(payload.get("comparison_count", 0)):
            errors.append("B7 U3 phase-factored logical T factory schedule should keep exposing factory dominance")
        if float(payload.get("mean_space_time_volume_reduction", 0.0)) <= float(
            b7_logical_t_control_rz_status.get("mean_space_time_volume_reduction", 0.0)
        ):
            errors.append("B7 U3 phase-factored logical T factory schedule should improve mean STV beyond control-RZ")
        if float(payload.get("min_space_time_volume_reduction", 0.0)) < float(
            b7_logical_t_control_rz_status.get("min_space_time_volume_reduction", 0.0)
        ):
            errors.append("B7 U3 phase-factored logical T factory schedule should not regress min STV below control-RZ")

    b7_min_stv_classifier_status = {}
    if not b7_min_stv_classifier:
        errors.append("B7 manifest missing minimum-STV regime classifier")
    else:
        result_path = b7_min_stv_classifier.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 minimum-STV classifier result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        min_rows = payload.get("min_rows", [])
        min_row = min_rows[0] if min_rows else {}
        requirements = {
            round(float(row.get("target_stv_reduction", 0.0)), 2): row
            for row in min_row.get("target_requirements", [])
        }
        target_1_20 = requirements.get(1.20, {})
        target_1_25 = requirements.get(1.25, {})
        b7_min_stv_classifier_status = {
            "status": b7_min_stv_classifier.get("status"),
            "method": b7_min_stv_classifier.get("method"),
            "source_schedule": b7_min_stv_classifier.get("source_schedule"),
            "comparison_count": b7_min_stv_classifier.get("comparison_count"),
            "workload_count": b7_min_stv_classifier.get("workload_count"),
            "min_space_time_volume_reduction": payload.get("min_space_time_volume_reduction"),
            "min_workload": payload.get("min_workload"),
            "factory_bottleneck_after_count": payload.get("factory_bottleneck_after_count"),
            "deep_factory_locked_count": payload.get("deep_factory_locked_count"),
            "target_1_20_additional_t_count_proxy_to_remove": target_1_20.get(
                "additional_t_count_proxy_to_remove"
            ),
            "target_1_25_additional_t_count_proxy_to_remove": target_1_25.get(
                "additional_t_count_proxy_to_remove"
            ),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "min_stv_regime_classified_not_physical_layout_claim":
            errors.append("B7 minimum-STV classifier must remain marked as not physical layout")
        if payload.get("method") != b7_min_stv_classifier.get("method"):
            errors.append("B7 minimum-STV classifier method mismatch")
        if payload.get("comparison_count") != b7_min_stv_classifier.get("comparison_count"):
            errors.append("B7 minimum-STV classifier comparison count mismatch")
        if payload.get("workload_count") != b7_min_stv_classifier.get("workload_count"):
            errors.append("B7 minimum-STV classifier workload count mismatch")
        if payload.get("min_workload") != b7_min_stv_classifier.get("min_workload"):
            errors.append("B7 minimum-STV classifier min workload mismatch")
        if payload.get("factory_bottleneck_after_count") != payload.get("comparison_count"):
            errors.append("B7 minimum-STV classifier should show factory bottleneck in every comparison")
        if int(payload.get("deep_factory_locked_count", 0)) < 1:
            errors.append("B7 minimum-STV classifier should include at least one deep factory-locked row")
        if not min_rows:
            errors.append("B7 minimum-STV classifier should include min rows")
        if target_1_20.get("additional_t_count_proxy_to_remove") != b7_min_stv_classifier.get(
            "target_1_20_additional_t_count_proxy_to_remove"
        ):
            errors.append("B7 minimum-STV classifier 1.20x target-removal mismatch")
        if target_1_25.get("additional_t_count_proxy_to_remove") != b7_min_stv_classifier.get(
            "target_1_25_additional_t_count_proxy_to_remove"
        ):
            errors.append("B7 minimum-STV classifier 1.25x target-removal mismatch")
        if float(payload.get("min_space_time_volume_reduction", 0.0)) != float(
            b7_logical_t_u3_phase_factored_status.get("min_space_time_volume_reduction", 0.0)
        ):
            errors.append("B7 minimum-STV classifier min STV should match the U3 phase-factored schedule")

    b7_ft_synthesis_ledger_status = {}
    if not b7_ft_synthesis_ledger:
        errors.append("B7 manifest missing FT synthesis ledger")
    else:
        result_path = b7_ft_synthesis_ledger.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 FT synthesis ledger result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        resource_rows = {row.get("workload"): row for row in payload.get("resource_rows", [])}
        sat_row = resource_rows.get("qasmbench_medium_exact/sat_n11.qasm", {})
        comparisons = payload.get("comparisons", [])
        sat_balanced = next(
            (
                row
                for row in comparisons
                if row.get("workload") == "qasmbench_medium_exact/sat_n11.qasm"
                and row.get("factory_variant") == "balanced_factories"
            ),
            {},
        )
        sat_throughput = next(
            (
                row
                for row in comparisons
                if row.get("workload") == "qasmbench_medium_exact/sat_n11.qasm"
                and row.get("factory_variant") == "throughput_heavy_factories"
            ),
            {},
        )
        min_row = payload.get("min_row", {})
        b7_ft_synthesis_ledger_status = {
            "status": b7_ft_synthesis_ledger.get("status"),
            "method": b7_ft_synthesis_ledger.get("method"),
            "source_schedule": b7_ft_synthesis_ledger.get("source_schedule"),
            "comparison_count": b7_ft_synthesis_ledger.get("comparison_count"),
            "workload_count": b7_ft_synthesis_ledger.get("workload_count"),
            "min_space_time_volume_reduction": payload.get("min_space_time_volume_reduction"),
            "mean_space_time_volume_reduction": payload.get("mean_space_time_volume_reduction"),
            "factory_bottleneck_after_count": payload.get("factory_bottleneck_after_count"),
            "data_bottleneck_after_count": payload.get("data_bottleneck_after_count"),
            "min_workload": min_row.get("workload"),
            "sat_n11_before_t_ledger": sat_row.get("before_logical_t_count_ledger"),
            "sat_n11_after_t_ledger": sat_row.get("after_logical_t_count_ledger"),
            "sat_n11_balanced_stv_reduction": sat_balanced.get("space_time_volume_reduction"),
            "sat_n11_throughput_stv_reduction": sat_throughput.get("space_time_volume_reduction"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "ft_synthesis_ledger_proxy_not_physical_layout":
            errors.append("B7 FT synthesis ledger must remain marked as proxy, not physical layout")
        if payload.get("method") != b7_ft_synthesis_ledger.get("method"):
            errors.append("B7 FT synthesis ledger method mismatch")
        if payload.get("comparison_count") != b7_ft_synthesis_ledger.get("comparison_count"):
            errors.append("B7 FT synthesis ledger comparison count mismatch")
        if payload.get("workload_count") != b7_ft_synthesis_ledger.get("workload_count"):
            errors.append("B7 FT synthesis ledger workload count mismatch")
        if min_row.get("workload") != b7_ft_synthesis_ledger.get("min_workload"):
            errors.append("B7 FT synthesis ledger min workload mismatch")
        if float(payload.get("min_space_time_volume_reduction", 0.0)) <= 1.0:
            errors.append("B7 FT synthesis ledger should preserve >1x minimum STV reduction")
        if int(payload.get("factory_bottleneck_after_count", 0)) + int(
            payload.get("data_bottleneck_after_count", 0)
        ) != int(payload.get("comparison_count", 0)):
            errors.append("B7 FT synthesis ledger bottleneck counts should cover every comparison")
        if sat_row.get("before_logical_t_count_ledger") != 294 or sat_row.get("after_logical_t_count_ledger") != 262:
            errors.append("B7 FT synthesis ledger should re-cost sat_n11 as 294 -> 262 T ledger")
        if sat_row.get("after_rotation_family_counts") != {
            "clifford_rotation": 131,
            "exact_pi_over_4_rotation": 262,
        }:
            errors.append("B7 FT synthesis ledger should classify sat_n11 after rotations as Clifford plus exact pi/4 only")
        if float(sat_balanced.get("space_time_volume_reduction", 0.0)) <= 1.25:
            errors.append("B7 FT synthesis ledger should move sat_n11 balanced factories beyond 1.25x STV")
        if float(sat_throughput.get("space_time_volume_reduction", 0.0)) <= 1.25:
            errors.append("B7 FT synthesis ledger should move sat_n11 throughput factories beyond 1.25x STV")

    b7_gcm_h6_boundary_status = {}
    if not b7_gcm_h6_boundary:
        errors.append("B7 manifest missing gcm_h6 FT boundary analysis")
    else:
        result_path = b7_gcm_h6_boundary.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 gcm_h6 FT boundary result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        target_rows = {
            round(float(row.get("target_stv_reduction", 0.0)), 2): row
            for row in payload.get("target_requirements_for_current_min", [])
        }
        target_1_20 = target_rows.get(1.20, {})
        target_1_25 = target_rows.get(1.25, {})
        thresholds = {
            round(float(row.get("target_stv_reduction", 0.0)), 2): row
            for row in payload.get("portfolio_thresholds", [])
        }
        b7_gcm_h6_boundary_status = {
            "status": b7_gcm_h6_boundary.get("status"),
            "method": b7_gcm_h6_boundary.get("method"),
            "source_ledger": b7_gcm_h6_boundary.get("source_ledger"),
            "current_min_workload": payload.get("current_min_workload"),
            "current_min_factory_variant": payload.get("current_min_factory_variant"),
            "current_min_space_time_volume_reduction": payload.get("current_min_space_time_volume_reduction"),
            "current_min_bottleneck_after": payload.get("current_min_bottleneck_after"),
            "gcm_h6_after_arbitrary_numeric_rotation_count": payload.get(
                "gcm_h6_after_arbitrary_numeric_rotation_count"
            ),
            "gcm_h6_after_arbitrary_numeric_t_cost": payload.get("gcm_h6_after_arbitrary_numeric_t_cost"),
            "gcm_h6_target_1_20_additional_t_ledger_to_remove": target_1_20.get(
                "additional_t_ledger_to_remove"
            ),
            "gcm_h6_target_1_25_additional_t_ledger_to_remove": target_1_25.get(
                "additional_t_ledger_to_remove"
            ),
            "portfolio_cost_sweep_reaches_1_20": thresholds.get(1.20, {}).get(
                "max_arbitrary_rotation_t_cost_meeting_target"
            )
            is not None,
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "gcm_h6_ft_boundary_quantified_not_physical_layout":
            errors.append("B7 gcm_h6 FT boundary must remain marked as not physical layout")
        if payload.get("method") != b7_gcm_h6_boundary.get("method"):
            errors.append("B7 gcm_h6 FT boundary method mismatch")
        if payload.get("current_min_workload") != b7_gcm_h6_boundary.get("current_min_workload"):
            errors.append("B7 gcm_h6 FT boundary current min workload mismatch")
        if payload.get("current_min_factory_variant") != b7_gcm_h6_boundary.get("current_min_factory_variant"):
            errors.append("B7 gcm_h6 FT boundary current min factory variant mismatch")
        if float(payload.get("current_min_space_time_volume_reduction", 0.0)) != float(
            b7_gcm_h6_boundary.get("current_min_space_time_volume_reduction", 0.0)
        ):
            errors.append("B7 gcm_h6 FT boundary current min STV mismatch")
        if payload.get("gcm_h6_after_arbitrary_numeric_rotation_count") != 270:
            errors.append("B7 gcm_h6 FT boundary should expose 270 after arbitrary numeric rotations")
        if payload.get("gcm_h6_after_arbitrary_numeric_t_cost") != 5400:
            errors.append("B7 gcm_h6 FT boundary should expose 5400 arbitrary numeric T cost")
        if target_1_20.get("additional_t_ledger_to_remove") != b7_gcm_h6_boundary.get(
            "gcm_h6_target_1_20_additional_t_ledger_to_remove"
        ):
            errors.append("B7 gcm_h6 FT boundary 1.20x target requirement mismatch")
        if target_1_25.get("additional_t_ledger_to_remove") != b7_gcm_h6_boundary.get(
            "gcm_h6_target_1_25_additional_t_ledger_to_remove"
        ):
            errors.append("B7 gcm_h6 FT boundary 1.25x target requirement mismatch")
        if thresholds.get(1.20, {}).get("max_arbitrary_rotation_t_cost_meeting_target") is not None:
            errors.append("B7 gcm_h6 FT boundary should show cost sweep alone does not clear 1.20x all-variant min")

    b7_precision_rotation_status = {}
    if not b7_precision_rotation_ledger:
        errors.append("B7 manifest missing precision-aware rotation ledger")
    else:
        result_path = b7_precision_rotation_ledger.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 precision-aware rotation ledger result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        target_rows = {
            round(float(row.get("target_stv_reduction", 0.0)), 2): row
            for row in payload.get("gcm_h6_one_sided_after_target_cost_requirements", [])
        }
        target_1_20 = target_rows.get(1.20, {})
        target_1_25 = target_rows.get(1.25, {})
        reuse_probe = payload.get("numeric_rotation_reuse_probe", {})
        best_budget = payload.get("best_precision_budget_row", {})
        b7_precision_rotation_status = {
            "status": b7_precision_rotation_ledger.get("status"),
            "method": b7_precision_rotation_ledger.get("method"),
            "source_ledger": b7_precision_rotation_ledger.get("source_ledger"),
            "source_boundary": b7_precision_rotation_ledger.get("source_boundary"),
            "synthesis_cost_model": b7_precision_rotation_ledger.get("synthesis_cost_model"),
            "gcm_h6_after_arbitrary_numeric_rotation_count": payload.get(
                "gcm_h6_throughput_after_arbitrary_numeric_rotation_count"
            ),
            "gcm_h6_after_unique_numeric_parameters": reuse_probe.get("unique_numeric_parameters"),
            "gcm_h6_after_current_total_t_ledger": payload.get("gcm_h6_throughput_after_current_total_t_ledger"),
            "gcm_h6_after_fixed_exact_t_ledger": payload.get("gcm_h6_throughput_after_fixed_exact_t_ledger"),
            "gcm_h6_one_sided_target_1_20_max_average_arbitrary_t_cost": target_1_20.get(
                "max_average_arbitrary_rotation_t_cost"
            ),
            "gcm_h6_one_sided_target_1_25_max_average_arbitrary_t_cost": target_1_25.get(
                "max_average_arbitrary_rotation_t_cost"
            ),
            "best_tested_precision_budget_arbitrary_t_cost": best_budget.get("arbitrary_rotation_t_cost"),
            "best_tested_precision_budget_min_stv_reduction": best_budget.get("min_space_time_volume_reduction"),
            "portfolio_precision_budgets_clear_1_20": payload.get("portfolio_precision_budgets_clear_1_20"),
            "gcm_h6_precision_budgets_clear_1_20": payload.get("gcm_h6_precision_budgets_clear_1_20"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "precision_aware_rotation_ledger_negative_boundary_not_physical_layout":
            errors.append("B7 precision-aware rotation ledger must remain marked as negative boundary, not physical layout")
        if payload.get("method") != b7_precision_rotation_ledger.get("method"):
            errors.append("B7 precision-aware rotation ledger method mismatch")
        if payload.get("current_min_workload") != b7_gcm_h6_boundary_status.get("current_min_workload"):
            errors.append("B7 precision-aware rotation ledger current min workload should match gcm_h6 boundary")
        if payload.get("gcm_h6_throughput_after_arbitrary_numeric_rotation_count") != b7_precision_rotation_ledger.get(
            "gcm_h6_after_arbitrary_numeric_rotation_count"
        ):
            errors.append("B7 precision-aware rotation ledger arbitrary rotation count mismatch")
        if reuse_probe.get("unique_numeric_parameters") != b7_precision_rotation_ledger.get(
            "gcm_h6_after_unique_numeric_parameters"
        ):
            errors.append("B7 precision-aware rotation ledger unique numeric parameter count mismatch")
        if payload.get("gcm_h6_throughput_after_current_total_t_ledger") != b7_precision_rotation_ledger.get(
            "gcm_h6_after_current_total_t_ledger"
        ):
            errors.append("B7 precision-aware rotation ledger total T ledger mismatch")
        if target_1_20.get("max_average_arbitrary_rotation_t_cost") != b7_precision_rotation_ledger.get(
            "gcm_h6_one_sided_target_1_20_max_average_arbitrary_t_cost"
        ):
            errors.append("B7 precision-aware rotation ledger 1.20x one-sided target cost mismatch")
        if target_1_25.get("max_average_arbitrary_rotation_t_cost") != b7_precision_rotation_ledger.get(
            "gcm_h6_one_sided_target_1_25_max_average_arbitrary_t_cost"
        ):
            errors.append("B7 precision-aware rotation ledger 1.25x one-sided target cost mismatch")
        if payload.get("portfolio_precision_budgets_clear_1_20") is not False:
            errors.append("B7 precision-aware rotation ledger should show precision budgets do not clear portfolio 1.20x")
        if payload.get("gcm_h6_precision_budgets_clear_1_20") is not False:
            errors.append("B7 precision-aware rotation ledger should show precision budgets do not clear gcm_h6 1.20x")
        if int(best_budget.get("arbitrary_rotation_t_cost", 0)) <= 20:
            errors.append("B7 precision-aware rotation ledger should show tested precision budgets imply cost above fixed 20")

    b7_gcm_h6_numeric_structure_status = {}
    if not b7_gcm_h6_numeric_structure:
        errors.append("B7 manifest missing gcm_h6 numeric-rotation structural pass")
    else:
        result_path = b7_gcm_h6_numeric_structure.get("result")
        proof_path = b7_gcm_h6_numeric_structure.get("proof_log")
        aer_path = b7_gcm_h6_numeric_structure.get("aer_crosscheck")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        proof_exists = bool(proof_path and path_exists_from(benchmarks, proof_path))
        aer_exists = bool(aer_path and path_exists_from(benchmarks, aer_path))
        if not result_exists:
            errors.append(f"B7 gcm_h6 numeric-rotation structure result path missing: {result_path}")
        if not proof_exists:
            errors.append(f"B7 gcm_h6 numeric-rotation structure proof log missing: {proof_path}")
        if not aer_exists:
            errors.append(f"B7 gcm_h6 numeric-rotation structure Aer crosscheck missing: {aer_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        aer_payload = json.loads(read((benchmarks / aer_path).resolve())) if aer_exists else {}
        retest = payload.get("portfolio_retest", {})
        rewrite = payload.get("rewrite_summary", {})
        b7_gcm_h6_numeric_structure_status = {
            "status": b7_gcm_h6_numeric_structure.get("status"),
            "method": b7_gcm_h6_numeric_structure.get("method"),
            "rewrite_rule": b7_gcm_h6_numeric_structure.get("rewrite_rule"),
            "arbitrary_numeric_rotations_before": payload.get("arbitrary_numeric_rotations_before"),
            "arbitrary_numeric_rotations_after": payload.get("arbitrary_numeric_rotations_after"),
            "arbitrary_numeric_rotations_removed": payload.get("arbitrary_numeric_rotations_removed"),
            "logical_t_ledger_before": payload.get("logical_t_ledger_before"),
            "logical_t_ledger_after": payload.get("logical_t_ledger_after"),
            "logical_t_ledger_removed": payload.get("logical_t_ledger_removed"),
            "proof_events": rewrite.get("certificate_entries"),
            "aer_crosscheck_passed": aer_payload.get("passed"),
            "aer_crosscheck_failed": aer_payload.get("failed"),
            "portfolio_min_space_time_volume_reduction": retest.get("min_space_time_volume_reduction"),
            "portfolio_clears_1_20": payload.get("clears_1_20_all_variant_min"),
            "result_exists": result_exists,
            "proof_exists": proof_exists,
            "aer_exists": aer_exists,
            "result": result_path,
        }
        if payload.get("status") != "gcm_h6_numeric_rotation_structure_negative_boundary_not_physical_layout":
            errors.append("B7 gcm_h6 numeric-rotation structure pass must remain marked as negative boundary")
        if payload.get("method") != b7_gcm_h6_numeric_structure.get("method"):
            errors.append("B7 gcm_h6 numeric-rotation structure method mismatch")
        if payload.get("arbitrary_numeric_rotations_before") != b7_gcm_h6_numeric_structure.get(
            "arbitrary_numeric_rotations_before"
        ):
            errors.append("B7 gcm_h6 numeric-rotation structure before arbitrary count mismatch")
        if payload.get("arbitrary_numeric_rotations_after") != b7_gcm_h6_numeric_structure.get(
            "arbitrary_numeric_rotations_after"
        ):
            errors.append("B7 gcm_h6 numeric-rotation structure after arbitrary count mismatch")
        if payload.get("arbitrary_numeric_rotations_removed") != 0:
            errors.append("B7 gcm_h6 numeric-rotation structure should record zero arbitrary rotations removed")
        if payload.get("logical_t_ledger_removed") != 0:
            errors.append("B7 gcm_h6 numeric-rotation structure should record zero T ledger removed")
        if rewrite.get("certificate_entries") != b7_gcm_h6_numeric_structure.get("proof_events"):
            errors.append("B7 gcm_h6 numeric-rotation structure proof event count mismatch")
        if aer_payload.get("failed") != 0 or aer_payload.get("passed") != b7_gcm_h6_numeric_structure.get(
            "aer_crosscheck_passed"
        ):
            errors.append("B7 gcm_h6 numeric-rotation structure Aer crosscheck mismatch")
        if payload.get("clears_1_20_all_variant_min") is not False:
            errors.append("B7 gcm_h6 numeric-rotation structure should not clear 1.20x all-variant min")
        if float(retest.get("min_space_time_volume_reduction", 0.0)) != float(
            b7_gcm_h6_numeric_structure.get("portfolio_min_space_time_volume_reduction", 0.0)
        ):
            errors.append("B7 gcm_h6 numeric-rotation structure min STV mismatch")

    b7_shared_synthesis_cache_status = {}
    if not b7_shared_synthesis_cache:
        errors.append("B7 manifest missing shared synthesis/cache boundary")
    else:
        result_path = b7_shared_synthesis_cache.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B7 shared synthesis/cache boundary result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        physical = payload.get("physical_occurrence_injection_model", {})
        invalid_after_only = payload.get("invalid_after_only_unique_template_model", {})
        physical_retest = physical.get("portfolio_retest", {})
        invalid_after_only_retest = invalid_after_only.get("portfolio_retest", {})
        claims = payload.get("claim_boundary", {})
        b7_shared_synthesis_cache_status = {
            "status": b7_shared_synthesis_cache.get("status"),
            "method": b7_shared_synthesis_cache.get("method"),
            "after_numeric_occurrences": physical.get("after_arbitrary_occurrences"),
            "after_unique_numeric_instructions": physical.get("after_unique_numeric_instructions"),
            "classical_catalog_reduction_factor": physical.get("classical_catalog_reduction_factor"),
            "physical_occurrence_before_t_ledger": physical.get("before_t_ledger"),
            "physical_occurrence_after_t_ledger": physical.get("after_t_ledger"),
            "ft_t_ledger_reduction_from_cache": physical.get("ft_t_ledger_reduction_from_cache"),
            "physical_occurrence_min_stv_reduction": physical_retest.get("min_space_time_volume_reduction"),
            "physical_occurrence_clears_1_20": physical_retest.get("clears_1_20_all_variant_min"),
            "invalid_after_only_unique_gcm_h6_clears_1_20": invalid_after_only_retest.get(
                "clears_1_20_gcm_h6_min"
            ),
            "invalid_after_only_unique_all_variant_clears_1_20": invalid_after_only_retest.get(
                "clears_1_20_all_variant_min"
            ),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "shared_synthesis_cache_no_ft_t_ledger_reduction_boundary":
            errors.append("B7 shared synthesis/cache boundary must remain marked as no-FT-ledger-reduction")
        if payload.get("method") != b7_shared_synthesis_cache.get("method"):
            errors.append("B7 shared synthesis/cache boundary method mismatch")
        if physical.get("after_arbitrary_occurrences") != b7_shared_synthesis_cache.get("after_numeric_occurrences"):
            errors.append("B7 shared synthesis/cache occurrence count mismatch")
        if physical.get("after_unique_numeric_instructions") != b7_shared_synthesis_cache.get(
            "after_unique_numeric_instructions"
        ):
            errors.append("B7 shared synthesis/cache unique-instruction count mismatch")
        if float(physical.get("classical_catalog_reduction_factor", 0.0)) != float(
            b7_shared_synthesis_cache.get("classical_catalog_reduction_factor", 0.0)
        ):
            errors.append("B7 shared synthesis/cache catalog-reduction factor mismatch")
        if physical.get("before_t_ledger") != b7_shared_synthesis_cache.get(
            "physical_occurrence_before_t_ledger"
        ):
            errors.append("B7 shared synthesis/cache physical before T ledger mismatch")
        if physical.get("after_t_ledger") != b7_shared_synthesis_cache.get(
            "physical_occurrence_after_t_ledger"
        ):
            errors.append("B7 shared synthesis/cache physical after T ledger mismatch")
        if physical.get("ft_t_ledger_reduction_from_cache") != 0:
            errors.append("B7 shared synthesis/cache must record zero FT T-ledger reduction from cache")
        if physical_retest.get("clears_1_20_all_variant_min") is not False:
            errors.append("B7 shared synthesis/cache physical occurrence model should not clear 1.20x")
        if claims.get("shared_synthesis_cache_reduces_ft_t_ledger_under_occurrence_injection_model") is not False:
            errors.append("B7 shared synthesis/cache claim boundary should reject FT T-ledger reduction")
        if invalid_after_only_retest.get("clears_1_20_gcm_h6_min") is not True:
            errors.append("B7 shared synthesis/cache invalid after-only model should expose gcm_h6-only false positive")
        if invalid_after_only_retest.get("clears_1_20_all_variant_min") is not False:
            errors.append("B7 shared synthesis/cache invalid after-only model should still fail all-variant 1.20x")

    b7_nonlocal_template_status = {}
    if not b7_nonlocal_template_block_scan:
        errors.append("B7 manifest missing nonlocal template block scan")
    else:
        result_path = b7_nonlocal_template_block_scan.get("result")
        proof_path = b7_nonlocal_template_block_scan.get("proof_log")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        proof_exists = bool(proof_path and path_exists_from(benchmarks, proof_path))
        if not result_exists:
            errors.append(f"B7 nonlocal template block scan result path missing: {result_path}")
        if not proof_exists:
            errors.append(f"B7 nonlocal template block scan proof log missing: {proof_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        cancellation = payload.get("cancellation_opportunities", {})
        best_template = payload.get("best_template") or {}
        retest = payload.get("portfolio_retest", {})
        target_sweep = payload.get("target_sweep", {})
        first_gcm = target_sweep.get("first_gcm_h6_1_20") or {}
        b7_nonlocal_template_status = {
            "status": b7_nonlocal_template_block_scan.get("status"),
            "method": b7_nonlocal_template_block_scan.get("method"),
            "operation_count": payload.get("operation_count"),
            "candidate_certificate_count": payload.get("candidate_certificate_count"),
            "top_template_count": payload.get("top_template_count"),
            "best_template_id": best_template.get("template_id"),
            "best_template_width": best_template.get("width"),
            "best_template_nonoverlap_occurrences": best_template.get("nonoverlap_occurrences"),
            "best_template_arbitrary_rotations_per_occurrence": best_template.get(
                "arbitrary_rotations_per_occurrence"
            ),
            "best_template_physical_arbitrary_occurrences_covered": best_template.get(
                "physical_arbitrary_occurrences_covered"
            ),
            "adjacent_inverse_pair_count": cancellation.get("adjacent_inverse_pair_count"),
            "adjacent_duplicate_pair_count": cancellation.get("adjacent_duplicate_pair_count"),
            "arbitrary_numeric_rotations_removed": payload.get("arbitrary_numeric_rotations_removed"),
            "logical_t_ledger_removed": payload.get("logical_t_ledger_removed"),
            "portfolio_min_space_time_volume_reduction": retest.get("min_space_time_volume_reduction"),
            "first_gcm_h6_1_20_removed_arbitrary_occurrences": first_gcm.get("removed_arbitrary_occurrences"),
            "first_gcm_h6_1_20_removed_t_ledger": first_gcm.get("removed_t_ledger"),
            "first_gcm_h6_1_20_after_t_ledger": first_gcm.get("after_t_ledger"),
            "first_gcm_h6_1_20_gcm_h6_min_stv": first_gcm.get("gcm_h6_min_space_time_volume_reduction"),
            "all_variant_1_20_by_gcm_h6_only": target_sweep.get("first_all_variant_1_20") is not None,
            "result_exists": result_exists,
            "proof_exists": proof_exists,
            "result": result_path,
        }
        if payload.get("status") != "nonlocal_template_block_scan_negative_boundary_not_physical_layout":
            errors.append("B7 nonlocal template block scan must remain marked as negative boundary")
        if payload.get("method") != b7_nonlocal_template_block_scan.get("method"):
            errors.append("B7 nonlocal template block scan method mismatch")
        if payload.get("operation_count") != b7_nonlocal_template_block_scan.get("operation_count"):
            errors.append("B7 nonlocal template block scan operation count mismatch")
        if payload.get("candidate_certificate_count") != b7_nonlocal_template_block_scan.get(
            "candidate_certificate_count"
        ):
            errors.append("B7 nonlocal template block scan certificate count mismatch")
        if best_template.get("template_id") != b7_nonlocal_template_block_scan.get("best_template_id"):
            errors.append("B7 nonlocal template block scan best template id mismatch")
        if best_template.get("physical_arbitrary_occurrences_covered") != b7_nonlocal_template_block_scan.get(
            "best_template_physical_arbitrary_occurrences_covered"
        ):
            errors.append("B7 nonlocal template block scan best template coverage mismatch")
        if cancellation.get("adjacent_inverse_pair_count") != 0:
            errors.append("B7 nonlocal template block scan should find zero adjacent inverse blocks")
        if cancellation.get("adjacent_duplicate_pair_count") != 0:
            errors.append("B7 nonlocal template block scan should find zero adjacent duplicate same-binding blocks")
        if payload.get("arbitrary_numeric_rotations_removed") != 0:
            errors.append("B7 nonlocal template block scan should not remove arbitrary rotations")
        if payload.get("logical_t_ledger_removed") != 0:
            errors.append("B7 nonlocal template block scan should not remove T ledger")
        if float(retest.get("min_space_time_volume_reduction", 0.0)) != float(
            b7_nonlocal_template_block_scan.get("portfolio_min_space_time_volume_reduction", 0.0)
        ):
            errors.append("B7 nonlocal template block scan min STV mismatch")
        if first_gcm.get("removed_arbitrary_occurrences") != b7_nonlocal_template_block_scan.get(
            "first_gcm_h6_1_20_removed_arbitrary_occurrences"
        ):
            errors.append("B7 nonlocal template block scan gcm_h6 1.20x occurrence target mismatch")
        if (target_sweep.get("first_all_variant_1_20") is not None) != bool(
            b7_nonlocal_template_block_scan.get("all_variant_1_20_by_gcm_h6_only")
        ):
            errors.append("B7 nonlocal template block scan all-variant target flag mismatch")

    b7_template_priority_status = {}
    if not b7_template_priority_gate:
        errors.append("B7 manifest missing template priority gate")
    else:
        result_path = b7_template_priority_gate.get("result")
        markdown_path = b7_template_priority_gate.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B7 template priority gate result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B7 template priority gate markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        rows = payload.get("template_priority_rows", [])
        b7_template_priority_status = {
            "status": b7_template_priority_gate.get("status"),
            "model_status": b7_template_priority_gate.get("model_status"),
            "method": b7_template_priority_gate.get("method"),
            "template_count": summary.get("template_count"),
            "target_removed_arbitrary_occurrences_for_gcm_h6_1_20": summary.get(
                "target_removed_arbitrary_occurrences_for_gcm_h6_1_20"
            ),
            "target_removed_t_ledger_for_gcm_h6_1_20": summary.get(
                "target_removed_t_ledger_for_gcm_h6_1_20"
            ),
            "single_template_one_angle_clear_count": summary.get("single_template_one_angle_clear_count"),
            "single_template_all_components_clear_count": summary.get(
                "single_template_all_components_clear_count"
            ),
            "best_template_id": summary.get("best_template_id"),
            "best_template_nonoverlap_occurrences": summary.get("best_template_nonoverlap_occurrences"),
            "best_template_required_arbitrary_removed_per_occurrence": summary.get(
                "best_template_required_arbitrary_removed_per_occurrence"
            ),
            "best_template_one_angle_shortfall": summary.get("best_template_one_angle_shortfall"),
            "w8_21_prior_optimizer_runs": summary.get("w8_21_prior_optimizer_runs"),
            "w8_21_prior_exact_rewrite_found": summary.get("w8_21_prior_exact_rewrite_found"),
            "all_variant_1_20_by_gcm_h6_only": summary.get("all_variant_1_20_by_gcm_h6_only"),
            "physical_resource_reduction_claimed": summary.get("physical_resource_reduction_claimed"),
            "global_lower_bound_claimed": summary.get("global_lower_bound_claimed"),
            "new_rewrite_claimed": claims.get("new_rewrite_claimed"),
            "validation_error_count": summary.get("validation_error_count"),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B7":
            errors.append("B7 template priority gate benchmark id mismatch")
        if payload.get("status") != "template_priority_gate_no_single_one_angle_template_clears_gcm_h6":
            errors.append("B7 template priority gate status mismatch")
        if payload.get("method") != b7_template_priority_gate.get("method"):
            errors.append("B7 template priority gate method mismatch")
        if payload.get("model_status") != b7_template_priority_gate.get("model_status"):
            errors.append("B7 template priority gate model_status mismatch")
        if summary.get("template_count") != b7_template_priority_gate.get("template_count"):
            errors.append("B7 template priority gate template count mismatch")
        if len(rows) != b7_template_priority_gate.get("template_count"):
            errors.append("B7 template priority gate row count mismatch")
        if summary.get("target_removed_arbitrary_occurrences_for_gcm_h6_1_20") != b7_template_priority_gate.get(
            "target_removed_arbitrary_occurrences_for_gcm_h6_1_20"
        ):
            errors.append("B7 template priority gate target occurrence mismatch")
        if summary.get("target_removed_t_ledger_for_gcm_h6_1_20") != b7_template_priority_gate.get(
            "target_removed_t_ledger_for_gcm_h6_1_20"
        ):
            errors.append("B7 template priority gate target T-ledger mismatch")
        if summary.get("single_template_one_angle_clear_count") != 0:
            errors.append("B7 template priority gate should have zero one-angle template clears")
        if summary.get("single_template_all_components_clear_count") != 12:
            errors.append("B7 template priority gate all-components template count mismatch")
        if summary.get("best_template_id") != "w8_21":
            errors.append("B7 template priority gate best template should remain w8_21")
        if summary.get("best_template_required_arbitrary_removed_per_occurrence") != 2:
            errors.append("B7 template priority gate w8_21 required removals per occurrence mismatch")
        if summary.get("best_template_one_angle_shortfall") != 10:
            errors.append("B7 template priority gate w8_21 one-angle shortfall mismatch")
        if summary.get("w8_21_prior_optimizer_runs") != 43480:
            errors.append("B7 template priority gate prior optimizer-run total mismatch")
        if summary.get("w8_21_prior_exact_rewrite_found") is not False:
            errors.append("B7 template priority gate must keep prior exact rewrite false")
        if summary.get("all_variant_1_20_by_gcm_h6_only") is not False:
            errors.append("B7 template priority gate must keep all-variant 1.20x false")
        if summary.get("physical_resource_reduction_claimed") is not False:
            errors.append("B7 template priority gate must not claim physical resource reduction")
        if summary.get("global_lower_bound_claimed") is not False:
            errors.append("B7 template priority gate must not claim a global lower bound")
        if claims.get("new_rewrite_claimed") is not False:
            errors.append("B7 template priority gate must not claim a new rewrite")
        if claims.get("all_variant_1_20_claimed") is not False:
            errors.append("B7 template priority gate must not claim all-variant 1.20x")
        if summary.get("validation_error_count") != 0:
            errors.append("B7 template priority gate validation errors must remain zero")

    b7_w8_21_synthesis_status = {}
    if not b7_w8_21_small_block_synthesis:
        errors.append("B7 manifest missing w8_21 small-block synthesis")
    else:
        result_path = b7_w8_21_small_block_synthesis.get("result")
        proof_path = b7_w8_21_small_block_synthesis.get("proof_log")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        proof_exists = bool(proof_path and path_exists_from(benchmarks, proof_path))
        if not result_exists:
            errors.append(f"B7 w8_21 small-block synthesis result path missing: {result_path}")
        if not proof_exists:
            errors.append(f"B7 w8_21 small-block synthesis proof log missing: {proof_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        family = payload.get("candidate_family", {})
        best = payload.get("best_candidate") or {}
        rank = payload.get("finite_difference_rank") or {}
        claims = payload.get("claim_boundary") or {}
        b7_w8_21_synthesis_status = {
            "status": b7_w8_21_small_block_synthesis.get("status"),
            "method": b7_w8_21_small_block_synthesis.get("method"),
            "template_id": payload.get("template_id"),
            "template_width": payload.get("template_width"),
            "template_nonoverlap_occurrences": payload.get("template_nonoverlap_occurrences"),
            "baseline_arbitrary_rotations_per_occurrence": payload.get(
                "baseline_arbitrary_rotations_per_occurrence"
            ),
            "candidate_attempt_count": family.get("attempt_count"),
            "seed_count_per_attempt": family.get("seed_count_per_attempt"),
            "exact_tolerance": payload.get("exact_tolerance"),
            "passing_candidate_count": payload.get("passing_candidate_count"),
            "best_fixed_parameter": best.get("fixed_parameter"),
            "best_fixed_label": best.get("fixed_label"),
            "best_residual_norm": best.get("residual_norm"),
            "best_max_abs_entry_error": best.get("max_abs_entry_error"),
            "finite_difference_rank": rank.get("numerical_rank"),
            "rank_supports_five_independent_continuous_degrees": claims.get(
                "rank_supports_five_independent_continuous_degrees"
            ),
            "same_skeleton_one_rotation_exact_replacement_found": claims.get(
                "same_skeleton_one_rotation_exact_replacement_found"
            ),
            "result_exists": result_exists,
            "proof_exists": proof_exists,
            "result": result_path,
        }
        if payload.get("status") != "w8_21_small_block_synthesis_negative_boundary_not_physical_layout":
            errors.append("B7 w8_21 small-block synthesis must remain marked as negative boundary")
        if payload.get("method") != b7_w8_21_small_block_synthesis.get("method"):
            errors.append("B7 w8_21 small-block synthesis method mismatch")
        if payload.get("template_id") != b7_w8_21_small_block_synthesis.get("template_id"):
            errors.append("B7 w8_21 small-block synthesis template id mismatch")
        if payload.get("template_width") != b7_w8_21_small_block_synthesis.get("template_width"):
            errors.append("B7 w8_21 small-block synthesis template width mismatch")
        if family.get("attempt_count") != b7_w8_21_small_block_synthesis.get("candidate_attempt_count"):
            errors.append("B7 w8_21 small-block synthesis attempt count mismatch")
        if family.get("seed_count_per_attempt") != b7_w8_21_small_block_synthesis.get("seed_count_per_attempt"):
            errors.append("B7 w8_21 small-block synthesis seed count mismatch")
        if payload.get("passing_candidate_count") != 0:
            errors.append("B7 w8_21 small-block synthesis should have zero passing candidates")
        if claims.get("same_skeleton_one_rotation_exact_replacement_found") is not False:
            errors.append("B7 w8_21 synthesis should reject same-skeleton one-rotation exact replacement")
        if best.get("fixed_parameter") != b7_w8_21_small_block_synthesis.get("best_fixed_parameter"):
            errors.append("B7 w8_21 synthesis best fixed parameter mismatch")
        if best.get("fixed_label") != b7_w8_21_small_block_synthesis.get("best_fixed_label"):
            errors.append("B7 w8_21 synthesis best fixed label mismatch")
        if float(best.get("residual_norm", 0.0)) != float(
            b7_w8_21_small_block_synthesis.get("best_residual_norm", 0.0)
        ):
            errors.append("B7 w8_21 synthesis best residual mismatch")
        if float(best.get("residual_norm", 0.0)) <= float(payload.get("exact_tolerance", 0.0)):
            errors.append("B7 w8_21 synthesis best residual should remain above exact tolerance")
        if rank.get("numerical_rank") != b7_w8_21_small_block_synthesis.get("finite_difference_rank"):
            errors.append("B7 w8_21 synthesis finite-difference rank mismatch")
        if claims.get("rank_supports_five_independent_continuous_degrees") is not True:
            errors.append("B7 w8_21 synthesis rank should support five independent degrees")

    b7_w8_21_broad_search_status = {}
    if not b7_w8_21_broad_skeleton_search:
        warnings.append("B7 manifest missing w8_21 broad-skeleton search first pass")
    else:
        result_path = b7_w8_21_broad_skeleton_search.get("result")
        proof_path = b7_w8_21_broad_skeleton_search.get("proof_log")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        proof_exists = bool(proof_path and path_exists_from(benchmarks, proof_path))
        if not result_exists:
            errors.append(f"B7 w8_21 broad-skeleton search result path missing: {result_path}")
        if not proof_exists:
            errors.append(f"B7 w8_21 broad-skeleton search proof log missing: {proof_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        family = payload.get("candidate_family", {})
        best = payload.get("best_candidate") or {}
        claims = payload.get("claim_boundary") or {}
        b7_w8_21_broad_search_status = {
            "status": b7_w8_21_broad_skeleton_search.get("status"),
            "method": b7_w8_21_broad_skeleton_search.get("method"),
            "template_id": payload.get("template_id"),
            "total_family_count": family.get("total_family_count"),
            "family_count": family.get("family_count"),
            "family_selection": family.get("family_selection"),
            "seed_count_per_family": family.get("seed_count_per_family"),
            "attempted_optimizer_runs": payload.get("attempted_optimizer_runs"),
            "exact_tolerance": payload.get("exact_tolerance"),
            "passing_candidate_count": payload.get("passing_candidate_count"),
            "best_family_label": best.get("family_label"),
            "best_residual_norm": best.get("residual_norm"),
            "best_max_abs_entry_error": best.get("max_abs_entry_error"),
            "bounded_four_rotation_two_cnot_search_found_exact_candidate": claims.get(
                "bounded_four_rotation_two_cnot_search_found_exact_candidate"
            ),
            "global_two_qubit_lower_bound_claimed": claims.get("global_two_qubit_lower_bound_claimed"),
            "result_exists": result_exists,
            "proof_exists": proof_exists,
            "result": result_path,
        }
        if payload.get("status") != "w8_21_broad_skeleton_search_negative_boundary_not_global_lower_bound":
            errors.append("B7 w8_21 broad-skeleton search should remain a bounded negative boundary")
        if payload.get("method") != b7_w8_21_broad_skeleton_search.get("method"):
            errors.append("B7 w8_21 broad-skeleton search method mismatch")
        if family.get("total_family_count") != b7_w8_21_broad_skeleton_search.get("total_family_count"):
            errors.append("B7 w8_21 broad-skeleton total family count mismatch")
        if family.get("family_count") != b7_w8_21_broad_skeleton_search.get("family_count"):
            errors.append("B7 w8_21 broad-skeleton scanned family count mismatch")
        if family.get("family_selection") != b7_w8_21_broad_skeleton_search.get("family_selection"):
            errors.append("B7 w8_21 broad-skeleton family selection mismatch")
        if payload.get("passing_candidate_count") != 0:
            errors.append("B7 w8_21 broad-skeleton first pass should have zero passing candidates")
        if claims.get("bounded_four_rotation_two_cnot_search_found_exact_candidate") is not False:
            errors.append("B7 w8_21 broad-skeleton first pass should reject exact four-rotation candidate")
        if claims.get("global_two_qubit_lower_bound_claimed") is not False:
            errors.append("B7 w8_21 broad-skeleton search must not claim a global lower bound")
        if best.get("family_label") != b7_w8_21_broad_skeleton_search.get("best_family_label"):
            errors.append("B7 w8_21 broad-skeleton best family mismatch")
        if float(best.get("residual_norm", 0.0)) != float(
            b7_w8_21_broad_skeleton_search.get("best_residual_norm", 0.0)
        ):
            errors.append("B7 w8_21 broad-skeleton best residual mismatch")
        if float(best.get("residual_norm", 0.0)) <= float(payload.get("exact_tolerance", 0.0)):
            errors.append("B7 w8_21 broad-skeleton best residual should remain above exact tolerance")

    b7_w8_21_euler_local_status = {}
    if not b7_w8_21_euler_local_search:
        warnings.append("B7 manifest missing w8_21 Euler-local search")
    else:
        result_path = b7_w8_21_euler_local_search.get("result")
        proof_path = b7_w8_21_euler_local_search.get("proof_log")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        proof_exists = bool(proof_path and path_exists_from(benchmarks, proof_path))
        if not result_exists:
            errors.append(f"B7 w8_21 Euler-local search result path missing: {result_path}")
        if not proof_exists:
            errors.append(f"B7 w8_21 Euler-local search proof log missing: {proof_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        family = payload.get("candidate_family", {})
        best = payload.get("best_candidate") or {}
        claims = payload.get("claim_boundary") or {}
        b7_w8_21_euler_local_status = {
            "status": b7_w8_21_euler_local_search.get("status"),
            "method": b7_w8_21_euler_local_search.get("method"),
            "template_id": payload.get("template_id"),
            "family_mode": family.get("family_mode"),
            "min_source_free_slots": family.get("min_source_free_slots"),
            "total_family_count": family.get("total_family_count"),
            "family_count": family.get("family_count"),
            "family_selection": family.get("family_selection"),
            "seed_count_per_family": family.get("seed_count_per_family"),
            "attempted_optimizer_runs": payload.get("attempted_optimizer_runs"),
            "exact_tolerance": payload.get("exact_tolerance"),
            "passing_candidate_count": payload.get("passing_candidate_count"),
            "best_family_label": best.get("family_label"),
            "best_residual_norm": best.get("residual_norm"),
            "best_max_abs_entry_error": best.get("max_abs_entry_error"),
            "euler_local_four_rotation_search_found_exact_candidate": claims.get(
                "euler_local_four_rotation_search_found_exact_candidate"
            ),
            "global_two_qubit_lower_bound_claimed": claims.get("global_two_qubit_lower_bound_claimed"),
            "all_exact_clifford_scaffolds_claimed": claims.get("all_exact_clifford_scaffolds_claimed"),
            "result_exists": result_exists,
            "proof_exists": proof_exists,
            "result": result_path,
        }
        if payload.get("status") != "w8_21_euler_local_search_negative_boundary_not_global_lower_bound":
            errors.append("B7 w8_21 Euler-local search should remain a bounded negative boundary")
        if payload.get("method") != b7_w8_21_euler_local_search.get("method"):
            errors.append("B7 w8_21 Euler-local search method mismatch")
        if family.get("family_mode") != b7_w8_21_euler_local_search.get("family_mode"):
            errors.append("B7 w8_21 Euler-local family mode mismatch")
        if family.get("min_source_free_slots") != b7_w8_21_euler_local_search.get("min_source_free_slots"):
            errors.append("B7 w8_21 Euler-local min source slots mismatch")
        if family.get("total_family_count") != b7_w8_21_euler_local_search.get("total_family_count"):
            errors.append("B7 w8_21 Euler-local total family count mismatch")
        if family.get("family_count") != b7_w8_21_euler_local_search.get("family_count"):
            errors.append("B7 w8_21 Euler-local scanned family count mismatch")
        if family.get("family_selection") != b7_w8_21_euler_local_search.get("family_selection"):
            errors.append("B7 w8_21 Euler-local family selection mismatch")
        if payload.get("attempted_optimizer_runs") != b7_w8_21_euler_local_search.get("attempted_optimizer_runs"):
            errors.append("B7 w8_21 Euler-local optimizer run count mismatch")
        if payload.get("passing_candidate_count") != 0:
            errors.append("B7 w8_21 Euler-local search should have zero passing candidates")
        if claims.get("euler_local_four_rotation_search_found_exact_candidate") is not False:
            errors.append("B7 w8_21 Euler-local search should reject exact four-rotation candidate")
        if claims.get("global_two_qubit_lower_bound_claimed") is not False:
            errors.append("B7 w8_21 Euler-local search must not claim a global lower bound")
        if claims.get("all_exact_clifford_scaffolds_claimed") is not False:
            errors.append("B7 w8_21 Euler-local search must not claim all exact Clifford scaffolds")
        if best.get("family_label") != b7_w8_21_euler_local_search.get("best_family_label"):
            errors.append("B7 w8_21 Euler-local best family mismatch")
        if float(best.get("residual_norm", 0.0)) != float(
            b7_w8_21_euler_local_search.get("best_residual_norm", 0.0)
        ):
            errors.append("B7 w8_21 Euler-local best residual mismatch")
        if float(best.get("residual_norm", 0.0)) <= float(payload.get("exact_tolerance", 0.0)):
            errors.append("B7 w8_21 Euler-local best residual should remain above exact tolerance")

    b7_w8_21_three_cnot_status = {}
    if not b7_w8_21_three_cnot_search:
        warnings.append("B7 manifest missing w8_21 three-CNOT search")
    else:
        result_path = b7_w8_21_three_cnot_search.get("result")
        proof_path = b7_w8_21_three_cnot_search.get("proof_log")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        proof_exists = bool(proof_path and path_exists_from(benchmarks, proof_path))
        if not result_exists:
            errors.append(f"B7 w8_21 three-CNOT search result path missing: {result_path}")
        if not proof_exists:
            errors.append(f"B7 w8_21 three-CNOT search proof log missing: {proof_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        family = payload.get("candidate_family", {})
        best = payload.get("best_candidate") or {}
        claims = payload.get("claim_boundary") or {}
        b7_w8_21_three_cnot_status = {
            "status": b7_w8_21_three_cnot_search.get("status"),
            "method": b7_w8_21_three_cnot_search.get("method"),
            "template_id": payload.get("template_id"),
            "family_mode": family.get("family_mode"),
            "min_source_free_slots": family.get("min_source_free_slots"),
            "total_family_count": family.get("total_family_count"),
            "family_count": family.get("family_count"),
            "family_selection": family.get("family_selection"),
            "seed_count_per_family": family.get("seed_count_per_family"),
            "attempted_optimizer_runs": payload.get("attempted_optimizer_runs"),
            "exact_tolerance": payload.get("exact_tolerance"),
            "passing_candidate_count": payload.get("passing_candidate_count"),
            "best_family_label": best.get("family_label"),
            "best_residual_norm": best.get("residual_norm"),
            "best_max_abs_entry_error": best.get("max_abs_entry_error"),
            "three_cnot_four_rotation_search_found_exact_candidate": claims.get(
                "three_cnot_four_rotation_search_found_exact_candidate"
            ),
            "global_two_qubit_lower_bound_claimed": claims.get("global_two_qubit_lower_bound_claimed"),
            "all_three_cnot_clifford_scaffolds_claimed": claims.get(
                "all_three_cnot_clifford_scaffolds_claimed"
            ),
            "result_exists": result_exists,
            "proof_exists": proof_exists,
            "result": result_path,
        }
        if payload.get("status") != "w8_21_three_cnot_search_negative_boundary_not_global_lower_bound":
            errors.append("B7 w8_21 three-CNOT search should remain a bounded negative boundary")
        if payload.get("method") != b7_w8_21_three_cnot_search.get("method"):
            errors.append("B7 w8_21 three-CNOT search method mismatch")
        if family.get("family_mode") != b7_w8_21_three_cnot_search.get("family_mode"):
            errors.append("B7 w8_21 three-CNOT family mode mismatch")
        if family.get("min_source_free_slots") != b7_w8_21_three_cnot_search.get("min_source_free_slots"):
            errors.append("B7 w8_21 three-CNOT min source slots mismatch")
        if family.get("total_family_count") != b7_w8_21_three_cnot_search.get("total_family_count"):
            errors.append("B7 w8_21 three-CNOT total family count mismatch")
        if family.get("family_count") != b7_w8_21_three_cnot_search.get("family_count"):
            errors.append("B7 w8_21 three-CNOT scanned family count mismatch")
        if family.get("family_selection") != b7_w8_21_three_cnot_search.get("family_selection"):
            errors.append("B7 w8_21 three-CNOT family selection mismatch")
        if payload.get("attempted_optimizer_runs") != b7_w8_21_three_cnot_search.get("attempted_optimizer_runs"):
            errors.append("B7 w8_21 three-CNOT optimizer run count mismatch")
        if payload.get("passing_candidate_count") != 0:
            errors.append("B7 w8_21 three-CNOT search should have zero passing candidates")
        if claims.get("three_cnot_four_rotation_search_found_exact_candidate") is not False:
            errors.append("B7 w8_21 three-CNOT search should reject exact four-rotation candidate")
        if claims.get("global_two_qubit_lower_bound_claimed") is not False:
            errors.append("B7 w8_21 three-CNOT search must not claim a global lower bound")
        if claims.get("all_three_cnot_clifford_scaffolds_claimed") is not False:
            errors.append("B7 w8_21 three-CNOT search must not claim all three-CNOT Clifford scaffolds")
        if best.get("family_label") != b7_w8_21_three_cnot_search.get("best_family_label"):
            errors.append("B7 w8_21 three-CNOT best family mismatch")
        if float(best.get("residual_norm", 0.0)) != float(
            b7_w8_21_three_cnot_search.get("best_residual_norm", 0.0)
        ):
            errors.append("B7 w8_21 three-CNOT best residual mismatch")
        if float(best.get("residual_norm", 0.0)) <= float(payload.get("exact_tolerance", 0.0)):
            errors.append("B7 w8_21 three-CNOT best residual should remain above exact tolerance")

    b7_w8_21_minimality_note_status = {}
    if not b7_w8_21_scoped_minimality_note:
        warnings.append("B7 manifest missing w8_21 scoped minimality note")
    else:
        markdown_path = b7_w8_21_scoped_minimality_note.get("markdown_report")
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not markdown_exists:
            errors.append(f"B7 w8_21 scoped minimality note missing markdown path: {markdown_path}")
        b7_w8_21_minimality_note_status = {
            "status": b7_w8_21_scoped_minimality_note.get("status"),
            "method": b7_w8_21_scoped_minimality_note.get("method"),
            "template_id": b7_w8_21_scoped_minimality_note.get("template_id"),
            "total_optimizer_runs_across_searches": b7_w8_21_scoped_minimality_note.get(
                "total_optimizer_runs_across_searches"
            ),
            "exact_rewrite_found": b7_w8_21_scoped_minimality_note.get("exact_rewrite_found"),
            "w8_21_arbitrary_rotations_removed": b7_w8_21_scoped_minimality_note.get(
                "w8_21_arbitrary_rotations_removed"
            ),
            "w8_21_proxy_t_ledger_removed": b7_w8_21_scoped_minimality_note.get(
                "w8_21_proxy_t_ledger_removed"
            ),
            "global_two_qubit_lower_bound_claimed": b7_w8_21_scoped_minimality_note.get(
                "global_two_qubit_lower_bound_claimed"
            ),
            "markdown_exists": markdown_exists,
            "markdown_report": markdown_path,
        }
        if b7_w8_21_scoped_minimality_note.get("status") != "scoped_minimality_note_not_global_lower_bound":
            errors.append("B7 w8_21 scoped minimality note must remain a non-global-lower-bound note")
        if b7_w8_21_scoped_minimality_note.get("exact_rewrite_found") is not False:
            errors.append("B7 w8_21 scoped minimality note must not claim an exact rewrite")
        if b7_w8_21_scoped_minimality_note.get("w8_21_arbitrary_rotations_removed") != 0:
            errors.append("B7 w8_21 scoped minimality note must keep removed arbitrary rotations at 0")
        if b7_w8_21_scoped_minimality_note.get("w8_21_proxy_t_ledger_removed") != 0:
            errors.append("B7 w8_21 scoped minimality note must keep removed T ledger at 0")
        if b7_w8_21_scoped_minimality_note.get("global_two_qubit_lower_bound_claimed") is not False:
            errors.append("B7 w8_21 scoped minimality note must not claim a global lower bound")

    b7_w8_21_claim_boundary_status = {}
    if not b7_w8_21_claim_boundary_fragment:
        warnings.append("B7 manifest missing w8_21 claim-boundary fragment")
    else:
        markdown_path = b7_w8_21_claim_boundary_fragment.get("markdown_report")
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        markdown_has_claim = False
        if markdown_exists:
            markdown_text = read((benchmarks / markdown_path).resolve())
            markdown_has_claim = (
                "Repeated synthesis templates are not physical resource savings without"
                in markdown_text
                and "occurrence-removing certificates" in markdown_text
            )
        if not markdown_exists:
            errors.append(f"B7 w8_21 claim-boundary fragment missing markdown path: {markdown_path}")
        if markdown_exists and not markdown_has_claim:
            errors.append("B7 w8_21 claim-boundary fragment missing paper claim text")
        b7_w8_21_claim_boundary_status = {
            "status": b7_w8_21_claim_boundary_fragment.get("status"),
            "method": b7_w8_21_claim_boundary_fragment.get("method"),
            "template_id": b7_w8_21_claim_boundary_fragment.get("template_id"),
            "total_optimizer_runs_across_searches": b7_w8_21_claim_boundary_fragment.get(
                "total_optimizer_runs_across_searches"
            ),
            "exact_rewrite_found": b7_w8_21_claim_boundary_fragment.get("exact_rewrite_found"),
            "w8_21_arbitrary_rotations_removed": b7_w8_21_claim_boundary_fragment.get(
                "w8_21_arbitrary_rotations_removed"
            ),
            "w8_21_proxy_t_ledger_removed": b7_w8_21_claim_boundary_fragment.get(
                "w8_21_proxy_t_ledger_removed"
            ),
            "global_minimality_theorem_claimed": b7_w8_21_claim_boundary_fragment.get(
                "global_minimality_theorem_claimed"
            ),
            "paper_claim": b7_w8_21_claim_boundary_fragment.get("paper_claim"),
            "markdown_exists": markdown_exists,
            "markdown_has_claim": markdown_has_claim,
            "markdown_report": markdown_path,
        }
        if b7_w8_21_claim_boundary_fragment.get("status") != "claim_boundary_fragment_not_minimality_theorem":
            errors.append("B7 w8_21 claim-boundary fragment must remain a non-minimality-theorem boundary")
        if b7_w8_21_claim_boundary_fragment.get("exact_rewrite_found") is not False:
            errors.append("B7 w8_21 claim-boundary fragment must not claim an exact rewrite")
        if b7_w8_21_claim_boundary_fragment.get("w8_21_arbitrary_rotations_removed") != 0:
            errors.append("B7 w8_21 claim-boundary fragment must keep removed arbitrary rotations at 0")
        if b7_w8_21_claim_boundary_fragment.get("w8_21_proxy_t_ledger_removed") != 0:
            errors.append("B7 w8_21 claim-boundary fragment must keep removed T ledger at 0")
        if b7_w8_21_claim_boundary_fragment.get("global_minimality_theorem_claimed") is not False:
            errors.append("B7 w8_21 claim-boundary fragment must not claim a global minimality theorem")
        if b7_w8_21_claim_boundary_fragment.get("total_optimizer_runs_across_searches") != 43480:
            errors.append("B7 w8_21 claim-boundary fragment optimizer-run total must remain 43480")

    b8_manifest = yaml.safe_load(read(b8_manifest_path))
    b8_results = b8_manifest.get("current_results", {})
    b8_verifier = b8_results.get("toy_hidden_invariant_output_verifier_v0")
    b8_adaptive = b8_results.get("adaptive_leakage_spoofer_stress_v0")
    b8_refresh = b8_results.get("challenge_refresh_projection_rotation_repair_v0")
    b8_circuit_refresh = b8_results.get("circuit_hidden_projection_refresh_v0")
    b8_openqasm3_packet = b8_results.get("openqasm3_randomized_measurement_packet_v0")
    b8_public_qasm_spoofer = b8_results.get("public_qasm_packet_spoofer_gate_v0")
    b8_late_bound_contract = b8_results.get("late_bound_private_challenge_contract_gate_v0")
    b8_nonstabilizer_pilot = b8_results.get("nonstabilizer_late_bound_transcript_pilot_v0")
    b8_support_spoofer = b8_results.get("nonstabilizer_support_spoofer_gate_v0")
    b8_generative_spoofer = b8_results.get("generative_spoofer_refresh_stress_v0")
    b8_status = {}
    if not b8_verifier:
        warnings.append("B8 manifest has no hidden-invariant output verifier result")
    else:
        result_path = b8_verifier.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B8 verifier result path missing: {result_path}")
        if b8_verifier.get("model_status") != "toy_invariant_property_test_not_full_distribution_verification":
            errors.append("B8 result must be explicitly marked as not full distribution verification")
        if float(b8_verifier.get("minimum_honest_completeness", 0.0)) < 0.8:
            errors.append("B8 honest completeness is below the first-pass threshold")
        if float(b8_verifier.get("maximum_adversary_soundness", 1.0)) > 0.05:
            errors.append("B8 adversary soundness is above the first-pass threshold")
        if int(b8_verifier.get("adversaries_failing_count", 0)) < 3:
            errors.append("B8 has fewer than 3 adversaries failing the invariant rule")
        if result_exists:
            payload = json.loads(read((benchmarks / result_path).resolve()))
            if payload.get("benchmark_id") != "B8":
                errors.append(f"B8 result benchmark_id={payload.get('benchmark_id')!r}, expected 'B8'")
            if payload.get("method") != "toy_hidden_invariant_output_verifier_v0":
                errors.append(f"B8 result method={payload.get('method')!r}, expected toy_hidden_invariant_output_verifier_v0")
            if payload.get("configuration_count") != b8_verifier.get("configuration_count"):
                errors.append("B8 result configuration_count differs from manifest")
            if payload.get("model_status") != b8_verifier.get("model_status"):
                errors.append("B8 result model_status differs from manifest")
            if payload.get("adversaries_failing_count") != b8_verifier.get("adversaries_failing_count"):
                errors.append("B8 result adversary-failure count differs from manifest")
        b8_status = {
            "status": b8_verifier.get("status"),
            "model_status": b8_verifier.get("model_status"),
            "task_count": b8_verifier.get("task_count"),
            "configuration_count": b8_verifier.get("configuration_count"),
            "sample_count": b8_verifier.get("sample_count"),
            "adversaries_tested": b8_verifier.get("adversaries_tested"),
            "adversaries_failing_count": b8_verifier.get("adversaries_failing_count"),
            "minimum_honest_completeness": b8_verifier.get("minimum_honest_completeness"),
            "maximum_adversary_soundness": b8_verifier.get("maximum_adversary_soundness"),
            "result_exists": result_exists,
            "result": result_path,
        }
    b8_adaptive_status = {}
    if not b8_adaptive:
        warnings.append("B8 manifest has no adaptive leakage spoofer stress test")
    else:
        result_path = b8_adaptive.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B8 adaptive leakage result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        leakage_summary = payload.get("leakage_summary", [])
        low_mid_entries = [
            row for row in leakage_summary if float(row.get("leakage_fraction", 1.0)) <= 0.5
        ]
        high_entries = [
            row for row in leakage_summary if float(row.get("leakage_fraction", 0.0)) >= 0.75
        ]
        b8_adaptive_status = {
            "status": b8_adaptive.get("status"),
            "method": b8_adaptive.get("method"),
            "configuration_count": b8_adaptive.get("configuration_count"),
            "leakage_fractions": b8_adaptive.get("leakage_fractions"),
            "maximum_adaptive_soundness": payload.get("maximum_adaptive_soundness"),
            "dangerous_leakage_threshold": payload.get("dangerous_leakage_threshold"),
            "minimum_honest_completeness": payload.get("minimum_honest_completeness"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "adaptive_leakage_stress_test_not_full_distribution_verification":
            errors.append("B8 adaptive leakage result must remain marked as not full distribution verification")
        if payload.get("method") != b8_adaptive.get("method"):
            errors.append("B8 adaptive leakage method mismatch")
        if payload.get("configuration_count") != b8_adaptive.get("configuration_count"):
            errors.append("B8 adaptive leakage configuration count mismatch")
        if payload.get("dangerous_leakage_threshold") != b8_adaptive.get("dangerous_leakage_threshold"):
            errors.append("B8 adaptive leakage dangerous threshold mismatch")
        if any(float(row.get("max_adaptive_soundness", 1.0)) > 0.05 for row in low_mid_entries):
            errors.append("B8 adaptive leakage should reject low/mid leakage spoofers under the current rule")
        if high_entries and max(float(row.get("max_adaptive_soundness", 0.0)) for row in high_entries) <= 0.05:
            errors.append("B8 adaptive leakage stress test should expose at least one high-leakage risk")

    b8_refresh_status = {}
    if not b8_refresh:
        warnings.append("B8 manifest has no challenge-refresh repair baseline")
    else:
        result_path = b8_refresh.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B8 challenge-refresh repair result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b8_refresh_status = {
            "status": b8_refresh.get("status"),
            "method": b8_refresh.get("method"),
            "configuration_count": b8_refresh.get("configuration_count"),
            "refresh_modes": b8_refresh.get("refresh_modes"),
            "maximum_adaptive_soundness": payload.get("maximum_adaptive_soundness"),
            "minimum_honest_completeness": payload.get("minimum_honest_completeness"),
            "high_leakage_repair_modes_passing": payload.get("high_leakage_repair_modes_passing"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "challenge_refresh_projection_rotation_toy_repair_not_full_distribution_verification":
            errors.append("B8 challenge-refresh repair must remain marked as a toy repair baseline")
        if payload.get("method") != b8_refresh.get("method"):
            errors.append("B8 challenge-refresh repair method mismatch")
        if payload.get("configuration_count") != b8_refresh.get("configuration_count"):
            errors.append("B8 challenge-refresh repair configuration count mismatch")
        if not payload.get("high_leakage_repair_modes_passing"):
            errors.append("B8 challenge-refresh repair should identify at least one passing high-leakage repair mode")

    b8_circuit_refresh_status = {}
    if not b8_circuit_refresh:
        warnings.append("B8 manifest has no circuit-level hidden-projection refresh task")
    else:
        result_path = b8_circuit_refresh.get("result")
        markdown_path = b8_circuit_refresh.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B4/B8 circuit refresh result path missing from B8 manifest: {result_path}")
        if not markdown_exists:
            errors.append(f"B4/B8 circuit refresh markdown missing from B8 manifest: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b8_circuit_refresh_status = {
            "status": b8_circuit_refresh.get("status"),
            "method": b8_circuit_refresh.get("method"),
            "task_family": b8_circuit_refresh.get("task_family"),
            "task_count": b8_circuit_refresh.get("task_count"),
            "configuration_count": b8_circuit_refresh.get("configuration_count"),
            "minimum_honest_completeness": payload.get("minimum_honest_completeness"),
            "maximum_adaptive_soundness": payload.get("maximum_adaptive_soundness"),
            "none_high_leakage_max_soundness": payload.get("none_high_leakage_max_soundness"),
            "best_repair_high_leakage_max_soundness": payload.get("best_repair_high_leakage_max_soundness"),
            "high_leakage_repair_modes_passing": payload.get("high_leakage_repair_modes_passing"),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B4_B8":
            errors.append("B8 circuit refresh benchmark_id must be B4_B8")
        if payload.get("status") != "circuit_level_hidden_projection_refresh_boundary_not_quantum_advantage_claim":
            errors.append("B8 circuit refresh must remain a circuit-level boundary, not a final claim")
        if payload.get("method") != b8_circuit_refresh.get("method"):
            errors.append("B8 circuit refresh method mismatch")
        if payload.get("configuration_count") != b8_circuit_refresh.get("configuration_count"):
            errors.append("B8 circuit refresh configuration count mismatch")
        if b4_circuit_refresh and b4_circuit_refresh.get("result") != b8_circuit_refresh.get("result"):
            errors.append("B4 and B8 circuit refresh manifests must point to the same result")
        if float(payload.get("minimum_honest_completeness", 0.0)) < 0.8:
            errors.append("B8 circuit refresh honest completeness below threshold")
        if float(payload.get("none_high_leakage_max_soundness", 0.0)) <= 0.05:
            errors.append("B8 circuit refresh should expose high-leakage no-refresh risk")
        if float(payload.get("best_repair_high_leakage_max_soundness", 1.0)) > 0.05:
            errors.append("B8 circuit refresh repair should reduce high-leakage soundness to <=5%")

    b8_openqasm3_packet_status = {}
    if not b8_openqasm3_packet:
        warnings.append("B8 manifest has no OpenQASM 3 randomized-measurement packet")
    else:
        result_path = b8_openqasm3_packet.get("result")
        markdown_path = b8_openqasm3_packet.get("markdown_report")
        qasm_directory = b8_openqasm3_packet.get("qasm_directory")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        qasm_directory_exists = bool(qasm_directory and path_exists_from(benchmarks, qasm_directory))
        if not result_exists:
            errors.append(f"B8 OpenQASM 3 packet result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B8 OpenQASM 3 packet markdown missing: {markdown_path}")
        if not qasm_directory_exists:
            errors.append(f"B8 OpenQASM 3 packet directory missing: {qasm_directory}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b8_openqasm3_packet_status = {
            "status": b8_openqasm3_packet.get("status"),
            "method": b8_openqasm3_packet.get("method"),
            "qasm_version": payload.get("qasm_version"),
            "circuit_file_count": payload.get("circuit_file_count"),
            "max_total_qubits": payload.get("max_total_qubits"),
            "all_qasm3_headers_valid": payload.get("all_qasm3_headers_valid"),
            "aer_semantic_mismatch_count": payload.get("aer_semantic_mismatch_count"),
            "minimum_aer_honest_completeness": payload.get("minimum_aer_honest_completeness"),
            "hardware_execution_performed": payload.get("hardware_execution_performed"),
            "quantum_advantage_claimed": payload.get("quantum_advantage_claimed"),
            "bqp_separation_claimed": payload.get("bqp_separation_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "qasm_directory_exists": qasm_directory_exists,
            "result": result_path,
            "markdown_report": markdown_path,
            "qasm_directory": qasm_directory,
        }
        if payload.get("benchmark_id") != "B4_B8":
            errors.append("B8 OpenQASM 3 packet benchmark_id must be B4_B8")
        if payload.get("status") != b8_openqasm3_packet.get("status"):
            errors.append("B8 OpenQASM 3 packet status mismatch")
        if payload.get("method") != b8_openqasm3_packet.get("method"):
            errors.append("B8 OpenQASM 3 packet method mismatch")
        if payload.get("qasm_version") != "OPENQASM 3.0":
            errors.append("B8 OpenQASM 3 packet must export OPENQASM 3.0 circuits")
        if payload.get("circuit_file_count") != b8_openqasm3_packet.get("circuit_file_count"):
            errors.append("B8 OpenQASM 3 packet circuit count mismatch")
        if payload.get("all_qasm3_headers_valid") is not True:
            errors.append("B8 OpenQASM 3 packet must report valid QASM3 headers")
        if payload.get("aer_semantic_mismatch_count") != 0:
            errors.append("B8 OpenQASM 3 packet must have zero Aer semantic mismatches")
        if payload.get("minimum_aer_honest_completeness") != 1.0:
            errors.append("B8 OpenQASM 3 packet must preserve ideal honest completeness")
        if payload.get("hardware_execution_performed") is not False:
            errors.append("B8 OpenQASM 3 packet must not claim hardware execution")
        for field in [
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "full_distribution_verification_claimed",
        ]:
            if payload.get(field) is not False:
                errors.append(f"B8 OpenQASM 3 packet must keep {field}=False")
        if b4_openqasm3_packet and b4_openqasm3_packet.get("result") != b8_openqasm3_packet.get("result"):
            errors.append("B4 and B8 OpenQASM 3 packet manifests must point to the same result")
        if len(payload.get("validation_errors", [])) != b8_openqasm3_packet.get("validation_error_count"):
            errors.append("B8 OpenQASM 3 packet validation-error count mismatch")

    b8_public_qasm_spoofer_status = {}
    if not b8_public_qasm_spoofer:
        warnings.append("B8 manifest has no public-QASM packet spoofer gate")
    else:
        result_path = b8_public_qasm_spoofer.get("result")
        markdown_path = b8_public_qasm_spoofer.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B8 public-QASM spoofer result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B8 public-QASM spoofer markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b8_public_qasm_spoofer_status = {
            "status": b8_public_qasm_spoofer.get("status"),
            "method": b8_public_qasm_spoofer.get("method"),
            "packet_circuit_count": payload.get("packet_circuit_count"),
            "parsed_circuit_count": payload.get("parsed_circuit_count"),
            "public_stabilizer_emulator_prediction_success_rate": payload.get(
                "public_stabilizer_emulator_prediction_success_rate"
            ),
            "public_packet_contract_soundness_rejected": payload.get(
                "public_packet_contract_soundness_rejected"
            ),
            "late_bound_private_challenges_required": payload.get("late_bound_private_challenges_required"),
            "hardware_execution_performed": payload.get("hardware_execution_performed"),
            "quantum_advantage_claimed": payload.get("quantum_advantage_claimed"),
            "bqp_separation_claimed": payload.get("bqp_separation_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B4_B8":
            errors.append("B8 public-QASM spoofer benchmark_id must be B4_B8")
        if payload.get("status") != b8_public_qasm_spoofer.get("status"):
            errors.append("B8 public-QASM spoofer status mismatch")
        if payload.get("method") != b8_public_qasm_spoofer.get("method"):
            errors.append("B8 public-QASM spoofer method mismatch")
        if payload.get("packet_circuit_count") != b8_public_qasm_spoofer.get("packet_circuit_count"):
            errors.append("B8 public-QASM spoofer packet circuit count mismatch")
        if payload.get("parsed_circuit_count") != b8_public_qasm_spoofer.get("parsed_circuit_count"):
            errors.append("B8 public-QASM spoofer parsed circuit count mismatch")
        if payload.get("public_stabilizer_emulator_prediction_success_rate") != 1.0:
            errors.append("B8 public-QASM spoofer should exactly predict public packet transcripts")
        if payload.get("public_packet_contract_soundness_rejected") is not True:
            errors.append("B8 public-QASM spoofer should reject public-packet protocol soundness")
        if payload.get("late_bound_private_challenges_required") is not True:
            errors.append("B8 public-QASM spoofer should require late-bound private challenges")
        if payload.get("hardware_execution_performed") is not False:
            errors.append("B8 public-QASM spoofer must not claim hardware execution")
        for field in [
            "real_backend_properties_used",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "sampling_hardness_proved",
            "cryptographic_soundness_proved",
            "protocol_soundness_proved",
        ]:
            if payload.get(field) is not False:
                errors.append(f"B8 public-QASM spoofer must keep {field}=False")
        if b4_public_qasm_spoofer and b4_public_qasm_spoofer.get("result") != b8_public_qasm_spoofer.get("result"):
            errors.append("B4 and B8 public-QASM spoofer manifests must point to the same result")
        if len(payload.get("validation_errors", [])) != b8_public_qasm_spoofer.get("validation_error_count"):
            errors.append("B8 public-QASM spoofer validation-error count mismatch")

    b8_late_bound_contract_status = audit_late_bound_contract(b8_late_bound_contract, "B8")
    b8_nonstabilizer_pilot_status = audit_nonstabilizer_pilot(b8_nonstabilizer_pilot, "B8")
    b8_support_spoofer_status = audit_nonstabilizer_support_spoofer(b8_support_spoofer, "B8")

    b8_generative_spoofer_status = {}
    if not b8_generative_spoofer:
        warnings.append("B8 manifest has no trained generative spoofer refresh stress")
    else:
        result_path = b8_generative_spoofer.get("result")
        markdown_path = b8_generative_spoofer.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B8 generative spoofer result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B8 generative spoofer markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b8_generative_spoofer_status = {
            "status": b8_generative_spoofer.get("status"),
            "method": b8_generative_spoofer.get("method"),
            "source_task": b8_generative_spoofer.get("source_task"),
            "configuration_count": b8_generative_spoofer.get("configuration_count"),
            "learners_tested": payload.get("learners_tested"),
            "minimum_honest_completeness": payload.get("minimum_honest_completeness"),
            "maximum_learned_soundness": payload.get("maximum_learned_soundness"),
            "safe_high_leakage_refresh_modes": payload.get("safe_high_leakage_refresh_modes"),
            "unsafe_high_leakage_refresh_modes": payload.get("unsafe_high_leakage_refresh_modes"),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("benchmark_id") != "B8":
            errors.append("B8 generative spoofer benchmark_id must be B8")
        if payload.get("status") != "trained_generative_spoofer_refresh_boundary_not_soundness_proof":
            errors.append("B8 generative spoofer must remain marked as not a soundness proof")
        if payload.get("method") != b8_generative_spoofer.get("method"):
            errors.append("B8 generative spoofer method mismatch")
        if payload.get("configuration_count") != b8_generative_spoofer.get("configuration_count"):
            errors.append("B8 generative spoofer configuration count mismatch")
        if float(payload.get("minimum_honest_completeness", 0.0)) < 0.8:
            errors.append("B8 generative spoofer honest completeness below threshold")
        if float(payload.get("maximum_learned_soundness", 0.0)) <= 0.05:
            errors.append("B8 generative spoofer should expose at least one learned attack risk")
        if "none" not in (payload.get("unsafe_high_leakage_refresh_modes") or []):
            errors.append("B8 generative spoofer should mark no-refresh high leakage as unsafe")
        if not {"projection_rotation", "challenge_refresh", "refresh_plus_rotation"}.issubset(
            set(payload.get("safe_high_leakage_refresh_modes") or [])
        ):
            errors.append("B8 generative spoofer should keep projection rotation or stronger modes safe in this proxy")

    b9_manifest = yaml.safe_load(read(b9_manifest_path))
    b9_results = b9_manifest.get("current_results", {})
    b9_gap_lab = b9_results.get("small_local_hamiltonian_gap_lab_v0")
    b9_failed_gap_lemma = b9_results.get("failed_gap_amplification_negative_lemma_v0")
    b9_symbolic_gap_skeleton = b9_results.get("symbolic_gap_amplification_skeleton_v0")
    b9_named_family_bound = b9_results.get("named_family_width_locality_bound_v0")
    b9_parametric_certificate = b9_results.get("cluster_stabilizer_parametric_certificate_v0")
    b9_status = {}
    if not b9_gap_lab:
        warnings.append("B9 manifest has no local-Hamiltonian gap-lab result")
    else:
        result_path = b9_gap_lab.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B9 gap-lab result path missing: {result_path}")
        if b9_gap_lab.get("model_status") != "exact_small_instance_lab_not_quantum_pcp_proof":
            errors.append("B9 result must be explicitly marked as not a Quantum PCP proof")
        if int(b9_gap_lab.get("counterexample_candidate_count", 0)) < 1:
            errors.append("B9 gap lab must track at least one counterexample candidate or explain none")
        if result_exists:
            payload = json.loads(read((benchmarks / result_path).resolve()))
            if payload.get("benchmark_id") != "B9":
                errors.append(f"B9 result benchmark_id={payload.get('benchmark_id')!r}, expected 'B9'")
            if payload.get("method") != "small_local_hamiltonian_gap_lab_v0":
                errors.append(f"B9 result method={payload.get('method')!r}, expected small_local_hamiltonian_gap_lab_v0")
            if payload.get("configuration_count") != b9_gap_lab.get("configuration_count"):
                errors.append("B9 result configuration_count differs from manifest")
            if payload.get("model_status") != b9_gap_lab.get("model_status"):
                errors.append("B9 result model_status differs from manifest")
            if payload.get("counterexample_candidate_count") != b9_gap_lab.get("counterexample_candidate_count"):
                errors.append("B9 result counterexample count differs from manifest")
        b9_status = {
            "status": b9_gap_lab.get("status"),
            "model_status": b9_gap_lab.get("model_status"),
            "configuration_count": b9_gap_lab.get("configuration_count"),
            "locality_preserving_candidate_count": b9_gap_lab.get("locality_preserving_candidate_count"),
            "candidate_pass_count": b9_gap_lab.get("candidate_pass_count"),
            "counterexample_candidate_count": b9_gap_lab.get("counterexample_candidate_count"),
            "max_local_candidate_normalized_gap_ratio": b9_gap_lab.get("max_local_candidate_normalized_gap_ratio"),
            "max_dense_filter_gap_ratio": b9_gap_lab.get("max_dense_filter_gap_ratio"),
            "result_exists": result_exists,
            "result": result_path,
        }
    b9_failed_gap_lemma_status = {}
    if not b9_failed_gap_lemma:
        warnings.append("B9 manifest has no failed gap-amplification negative lemma")
    else:
        result_path = b9_failed_gap_lemma.get("result")
        markdown_path = b9_failed_gap_lemma.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B9 failed gap-amplification lemma result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B9 failed gap-amplification lemma markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b9_failed_gap_lemma_status = {
            "status": b9_failed_gap_lemma.get("status"),
            "method": b9_failed_gap_lemma.get("method"),
            "theorem_count": payload.get("theorem_count"),
            "local_candidate_pass_count": payload.get("local_candidate_pass_count"),
            "strict_counterexample_count": payload.get("strict_counterexample_count"),
            "tolerance_counterexample_count": payload.get("tolerance_counterexample_count"),
            "dense_locality_trap_count": payload.get("dense_locality_trap_count"),
            "proof_obligation_count": len(payload.get("proof_obligations", [])),
            "explicit_not_quantum_pcp_proof": payload.get("explicit_not_quantum_pcp_proof"),
            "global_gap_amplification_impossibility_claimed": payload.get(
                "global_gap_amplification_impossibility_claimed"
            ),
            "proof_assistant_formalized": payload.get("proof_assistant_formalized"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "finite_instance_negative_gap_amplification_lemma_not_quantum_pcp_proof":
            errors.append("B9 failed gap-amplification lemma status mismatch")
        if payload.get("method") != b9_failed_gap_lemma.get("method"):
            errors.append("B9 failed gap-amplification lemma method mismatch")
        if payload.get("source_benchmark_id") != "B9":
            errors.append("B9 failed gap-amplification lemma source benchmark must be B9")
        if payload.get("source_method") != "small_local_hamiltonian_gap_lab_v0":
            errors.append("B9 failed gap-amplification lemma source method mismatch")
        if int(payload.get("theorem_count", 0)) < 1:
            errors.append("B9 failed gap-amplification lemma should contain a finite-instance lemma")
        if int(payload.get("local_candidate_pass_count", 1)) != 0:
            errors.append("B9 failed gap-amplification lemma should preserve zero local passes")
        if int(payload.get("strict_counterexample_count", 0)) < 4:
            errors.append("B9 failed gap-amplification lemma should preserve four strict counterexamples")
        if int(payload.get("dense_locality_trap_count", 0)) < 3:
            errors.append("B9 failed gap-amplification lemma should include dense locality traps")
        if len(payload.get("proof_obligations", [])) < 3:
            errors.append("B9 failed gap-amplification lemma should record proof obligations")
        if payload.get("explicit_not_quantum_pcp_proof") is not True:
            errors.append("B9 failed gap-amplification lemma must explicitly avoid Quantum PCP proof claims")
        if payload.get("global_gap_amplification_impossibility_claimed") is not False:
            errors.append("B9 failed gap-amplification lemma must not claim global impossibility")
        if payload.get("proof_assistant_formalized") is not False:
            errors.append("B9 failed gap-amplification lemma proof assistant status should remain false")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B9 failed gap-amplification lemma validation errors must be zero")
    b9_symbolic_gap_skeleton_status = {}
    if not b9_symbolic_gap_skeleton:
        warnings.append("B9 manifest has no symbolic gap-amplification skeleton")
    else:
        result_path = b9_symbolic_gap_skeleton.get("result")
        markdown_path = b9_symbolic_gap_skeleton.get("markdown_report")
        lean_path = b9_symbolic_gap_skeleton.get("lean_skeleton")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        lean_exists = bool(lean_path and path_exists_from(benchmarks, lean_path))
        if not result_exists:
            errors.append(f"B9 symbolic gap skeleton result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B9 symbolic gap skeleton markdown missing: {markdown_path}")
        if not lean_exists:
            errors.append(f"B9 symbolic gap skeleton Lean file missing: {lean_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b9_symbolic_gap_skeleton_status = {
            "status": b9_symbolic_gap_skeleton.get("status"),
            "method": b9_symbolic_gap_skeleton.get("method"),
            "proof_assistant_target": payload.get("proof_assistant_target"),
            "symbolic_definition_count": payload.get("symbolic_definition_count"),
            "theorem_skeleton_count": payload.get("theorem_skeleton_count"),
            "open_obligation_count": payload.get("open_obligation_count"),
            "strict_counterexample_count_inherited": payload.get("strict_counterexample_count_inherited"),
            "dense_locality_trap_count_inherited": payload.get("dense_locality_trap_count_inherited"),
            "proof_assistant_checked": payload.get("proof_assistant_checked"),
            "formal_theorem_proved": payload.get("formal_theorem_proved"),
            "explicit_not_quantum_pcp_proof": payload.get("explicit_not_quantum_pcp_proof"),
            "global_gap_amplification_impossibility_claimed": payload.get(
                "global_gap_amplification_impossibility_claimed"
            ),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "lean_exists": lean_exists,
            "result": result_path,
            "markdown_report": markdown_path,
            "lean_skeleton": lean_path,
        }
        if payload.get("status") != "symbolic_proof_skeleton_not_formalized_theorem":
            errors.append("B9 symbolic gap skeleton status mismatch")
        if payload.get("method") != b9_symbolic_gap_skeleton.get("method"):
            errors.append("B9 symbolic gap skeleton method mismatch")
        if payload.get("source_method") != "b9_failed_gap_amplification_negative_lemma_v0":
            errors.append("B9 symbolic gap skeleton source method mismatch")
        if int(payload.get("symbolic_definition_count", 0)) < 4:
            errors.append("B9 symbolic gap skeleton should expose symbolic definitions")
        if int(payload.get("theorem_skeleton_count", 0)) < 3:
            errors.append("B9 symbolic gap skeleton should expose theorem skeletons")
        if int(payload.get("open_obligation_count", 0)) < 5:
            errors.append("B9 symbolic gap skeleton should preserve open obligations")
        if payload.get("proof_assistant_checked") is not False:
            errors.append("B9 symbolic gap skeleton must not claim proof-assistant checking")
        if payload.get("formal_theorem_proved") is not False:
            errors.append("B9 symbolic gap skeleton must not claim a formal theorem")
        if payload.get("explicit_not_quantum_pcp_proof") is not True:
            errors.append("B9 symbolic gap skeleton must explicitly avoid Quantum PCP proof claims")
        if payload.get("global_gap_amplification_impossibility_claimed") is not False:
            errors.append("B9 symbolic gap skeleton must not claim global impossibility")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B9 symbolic gap skeleton validation errors must be zero")

    b9_named_family_bound_status = {}
    if not b9_named_family_bound:
        warnings.append("B9 manifest has no named-family width/locality bound skeleton")
    else:
        result_path = b9_named_family_bound.get("result")
        markdown_path = b9_named_family_bound.get("markdown_report")
        lean_path = b9_named_family_bound.get("lean_skeleton")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        lean_exists = bool(lean_path and path_exists_from(benchmarks, lean_path))
        if not result_exists:
            errors.append(f"B9 named-family bound result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B9 named-family bound markdown missing: {markdown_path}")
        if not lean_exists:
            errors.append(f"B9 named-family bound Lean file missing: {lean_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b9_named_family_bound_status = {
            "status": b9_named_family_bound.get("status"),
            "method": b9_named_family_bound.get("method"),
            "named_family": payload.get("named_family"),
            "rows_matched": payload.get("rows_matched"),
            "scaling_factor": payload.get("scaling_factor"),
            "max_locality": payload.get("max_locality"),
            "all_terms_scaled_uniformly": payload.get("all_terms_scaled_uniformly"),
            "locality_bound_preserved": payload.get("locality_bound_preserved"),
            "raw_gap_amplifies": payload.get("raw_gap_amplifies"),
            "normalized_gap_invariant_under_uniform_scaling": payload.get(
                "normalized_gap_invariant_under_uniform_scaling"
            ),
            "certificate_rejected": payload.get("certificate_rejected"),
            "proof_assistant_checked": payload.get("proof_assistant_checked"),
            "proof_assistant_check_status": payload.get("proof_assistant_check_status"),
            "formal_theorem_proved": payload.get("formal_theorem_proved"),
            "explicit_not_quantum_pcp_proof": payload.get("explicit_not_quantum_pcp_proof"),
            "global_gap_amplification_impossibility_claimed": payload.get(
                "global_gap_amplification_impossibility_claimed"
            ),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "lean_exists": lean_exists,
            "result": result_path,
            "markdown_report": markdown_path,
            "lean_skeleton": lean_path,
        }
        if payload.get("status") != "named_family_width_locality_bound_skeleton_not_checked_theorem":
            errors.append("B9 named-family bound status mismatch")
        if payload.get("method") != b9_named_family_bound.get("method"):
            errors.append("B9 named-family bound method mismatch")
        if payload.get("source_method") != "small_local_hamiltonian_gap_lab_v0":
            errors.append("B9 named-family bound source method mismatch")
        if payload.get("named_family") != "cluster_stabilizer_open_uniform_reweight":
            errors.append("B9 named-family bound family mismatch")
        if int(payload.get("rows_matched", 0)) < 3:
            errors.append("B9 named-family bound should include at least three finite rows")
        if payload.get("all_terms_scaled_uniformly") is not True:
            errors.append("B9 named-family bound should prove uniform term scaling for this family")
        if payload.get("locality_bound_preserved") is not True:
            errors.append("B9 named-family bound should preserve locality")
        if payload.get("max_locality") != 3:
            errors.append("B9 named-family bound should keep max locality at 3")
        if payload.get("raw_gap_amplifies") is not True:
            errors.append("B9 named-family bound should record raw gap amplification")
        if payload.get("normalized_gap_invariant_under_uniform_scaling") is not True:
            errors.append("B9 named-family bound should record normalized-gap invariance")
        if payload.get("certificate_rejected") is not True:
            errors.append("B9 named-family bound should reject uniform scaling as a certificate")
        if payload.get("proof_assistant_checked") is not False:
            errors.append("B9 named-family bound must not claim proof-assistant checking")
        if payload.get("formal_theorem_proved") is not False:
            errors.append("B9 named-family bound must not claim a formal theorem")
        if payload.get("explicit_not_quantum_pcp_proof") is not True:
            errors.append("B9 named-family bound must explicitly avoid Quantum PCP proof claims")
        if payload.get("global_gap_amplification_impossibility_claimed") is not False:
            errors.append("B9 named-family bound must not claim global impossibility")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B9 named-family bound validation errors must be zero")

    b9_parametric_certificate_status = {}
    if not b9_parametric_certificate:
        warnings.append("B9 manifest has no cluster-stabilizer parametric certificate")
    else:
        result_path = b9_parametric_certificate.get("result")
        markdown_path = b9_parametric_certificate.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B9 parametric certificate result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B9 parametric certificate markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        claim_boundary = payload.get("claim_boundary", {})
        b9_parametric_certificate_status = {
            "status": b9_parametric_certificate.get("status"),
            "method": b9_parametric_certificate.get("method"),
            "source_method": payload.get("source_method"),
            "named_family": payload.get("named_family"),
            "parameterized_n_min": payload.get("parameterized_n_min"),
            "finite_rows_checked": payload.get("finite_rows_checked"),
            "support_size_set": payload.get("support_size_set"),
            "max_locality": payload.get("max_locality"),
            "uniform_scale": payload.get("uniform_scale"),
            "term_count_formula": payload.get("term_count_formula"),
            "interior_term_count_formula": payload.get("interior_term_count_formula"),
            "boundary_term_count_formula": payload.get("boundary_term_count_formula"),
            "normalized_gap_invariant_symbolically": payload.get("normalized_gap_invariant_symbolically"),
            "certificate_rejected": payload.get("certificate_rejected"),
            "local_verifier_checked": claim_boundary.get("local_verifier_checked"),
            "proof_assistant_checked": payload.get("proof_assistant_checked"),
            "formal_theorem_proved": payload.get("formal_theorem_proved"),
            "explicit_not_quantum_pcp_proof": payload.get("explicit_not_quantum_pcp_proof"),
            "global_gap_amplification_impossibility_claimed": payload.get(
                "global_gap_amplification_impossibility_claimed"
            ),
            "validation_error_count": payload.get("validation_error_count"),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "parametric_certificate_checked_by_local_verifier_not_formal_theorem":
            errors.append("B9 parametric certificate status mismatch")
        if payload.get("method") != b9_parametric_certificate.get("method"):
            errors.append("B9 parametric certificate method mismatch")
        if payload.get("source_method") != "b9_named_family_width_locality_bound_v0":
            errors.append("B9 parametric certificate source method mismatch")
        if payload.get("named_family") != "cluster_stabilizer_open_uniform_reweight":
            errors.append("B9 parametric certificate family mismatch")
        if payload.get("parameterized_n_min") != 4:
            errors.append("B9 parametric certificate should target n >= 4")
        if payload.get("finite_rows_checked") != [4, 5, 6]:
            errors.append("B9 parametric certificate should check finite rows n=4,5,6")
        if payload.get("support_size_set") != [2, 3]:
            errors.append("B9 parametric certificate support set mismatch")
        if payload.get("max_locality") != 3:
            errors.append("B9 parametric certificate max locality should be 3")
        if payload.get("uniform_scale") != "27/20":
            errors.append("B9 parametric certificate uniform scale should be 27/20")
        if payload.get("term_count_formula") != "n":
            errors.append("B9 parametric certificate term-count formula mismatch")
        if payload.get("interior_term_count_formula") != "n-2":
            errors.append("B9 parametric certificate interior formula mismatch")
        if payload.get("boundary_term_count_formula") != "2":
            errors.append("B9 parametric certificate boundary formula mismatch")
        if payload.get("normalized_gap_invariant_symbolically") is not True:
            errors.append("B9 parametric certificate should symbolically check normalized-gap invariance")
        if payload.get("certificate_rejected") is not True:
            errors.append("B9 parametric certificate should reject raw-gap-only certificate")
        if claim_boundary.get("local_verifier_checked") is not True:
            errors.append("B9 parametric certificate local verifier should pass")
        if payload.get("proof_assistant_checked") is not False:
            errors.append("B9 parametric certificate must not claim proof-assistant checking")
        if payload.get("formal_theorem_proved") is not False:
            errors.append("B9 parametric certificate must not claim a formal theorem")
        if payload.get("explicit_not_quantum_pcp_proof") is not True:
            errors.append("B9 parametric certificate must explicitly avoid Quantum PCP proof claims")
        if payload.get("global_gap_amplification_impossibility_claimed") is not False:
            errors.append("B9 parametric certificate must not claim global impossibility")
        if payload.get("validation_error_count") != 0 or len(payload.get("validation_errors", [])) != 0:
            errors.append("B9 parametric certificate validation errors must be zero")

    b10_manifest = yaml.safe_load(read(b10_manifest_path))
    b10_results = b10_manifest.get("current_results", {})
    b10_graph = b10_results.get("bqp_boundary_reduction_graph_v0")
    b10_formal_targets = b10_results.get("formal_theorem_targets_v0")
    b10_t2_refresh_boundary = b10_results.get("b10_t2_minimum_refresh_spoofer_boundary_v0")
    b10_t2_proof_gate = b10_results.get("b10_t2_refresh_proof_obligation_gate_v0")
    b10_t2_restricted_lemma = b10_results.get("b10_t2_restricted_soundness_lemma_v0")
    b10_t2_transcript_simulator = b10_results.get("b10_t2_transcript_leakage_simulator_v0")
    b10_t2_device_noise_bridge = b10_results.get("b10_t2_device_noise_transcript_bridge_v0")
    b10_t2_qiskit_aer_bridge = b10_results.get("b10_t2_qiskit_aer_verifier_bridge_v0")
    b10_t2_noisy_aer_bridge = b10_results.get("b10_t2_noisy_aer_verifier_bridge_v0")
    b10_t2_backend_calibrated_bridge = b10_results.get("b10_t2_backend_calibrated_verifier_bridge_v0")
    b10_t1_proof = b10_results.get("b10_t1_negative_boundary_proof_v0")
    b10_t1_source_backed = b10_results.get("b10_t1_source_backed_boundaries_v0")
    b10_t1_numerical_table = b10_results.get("b10_t1_numerical_denominator_table_v0")
    b10_t1_d5_table = b10_results.get("b10_t1_d5_observable_denominator_table_v0")
    b10_t1_d5_b3_table = b10_results.get("b10_t1_d5_b3_molecular_observable_table_v0")
    b10_t1_d5_b3_reaction_table = b10_results.get("b10_t1_d5_b3_reaction_observable_table_v0")
    b10_t1_d5_b3_correlated_table = b10_results.get("b10_t1_d5_b3_correlated_reference_table_v0")
    b10_t1_d5_b3_fci_table = b10_results.get("b10_t1_d5_b3_fci_reference_table_v0")
    b10_t1_b3_b5_comparison = b10_results.get("b10_t1_b3_b5_denominator_boundary_comparison_v0")
    b10_t1_missing_assumption_note = b10_results.get("b10_t1_missing_assumption_note_v0")
    b10_t1_asymptotic_access_contract = b10_results.get("b10_t1_asymptotic_access_contract_v0")
    b10_t1_b5_same_access_bridge = b10_results.get("b10_t1_b5_same_access_sampling_or_dmrg_bridge_v0")
    b10_t1_b5_response_sampler_stress = b10_results.get("b10_t1_b5_response_sampler_cost_stress_v0")
    b10_status = {}
    if not b10_graph:
        warnings.append("B10 manifest has no BQP-boundary graph result")
    else:
        result_path = b10_graph.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B10 boundary graph result path missing: {result_path}")
        if b10_graph.get("model_status") != "taxonomy_and_reduction_planning_not_complexity_theorem":
            errors.append("B10 result must be explicitly marked as not a complexity theorem")
        if int(b10_graph.get("node_count", 0)) < 10:
            errors.append("B10 boundary graph has fewer than 10 nodes")
        if int(b10_graph.get("edge_count", 0)) < 12:
            errors.append("B10 boundary graph has fewer than 12 edges")
        if int(b10_graph.get("restricted_theorem_target_count", 0)) < 2:
            errors.append("B10 has fewer than 2 restricted theorem targets")
        if int(b10_graph.get("fragile_edge_count", 0)) < 1:
            errors.append("B10 must track fragile boundary edges")
        if result_exists:
            payload = json.loads(read((benchmarks / result_path).resolve()))
            if payload.get("benchmark_id") != "B10":
                errors.append(f"B10 result benchmark_id={payload.get('benchmark_id')!r}, expected 'B10'")
            if payload.get("method") != "bqp_boundary_reduction_graph_v0":
                errors.append(f"B10 result method={payload.get('method')!r}, expected bqp_boundary_reduction_graph_v0")
            if payload.get("node_count") != b10_graph.get("node_count"):
                errors.append("B10 result node_count differs from manifest")
            if payload.get("edge_count") != b10_graph.get("edge_count"):
                errors.append("B10 result edge_count differs from manifest")
            if payload.get("model_status") != b10_graph.get("model_status"):
                errors.append("B10 result model_status differs from manifest")
            if payload.get("restricted_theorem_target_count") != b10_graph.get("restricted_theorem_target_count"):
                errors.append("B10 result theorem target count differs from manifest")
        b10_status = {
            "status": b10_graph.get("status"),
            "model_status": b10_graph.get("model_status"),
            "node_count": b10_graph.get("node_count"),
            "edge_count": b10_graph.get("edge_count"),
            "connected_component_count": b10_graph.get("connected_component_count"),
            "advantage_preserving_edge_count": b10_graph.get("advantage_preserving_edge_count"),
            "fragile_edge_count": b10_graph.get("fragile_edge_count"),
            "restricted_theorem_target_count": b10_graph.get("restricted_theorem_target_count"),
            "top_failure_modes": b10_graph.get("top_failure_modes"),
            "result_exists": result_exists,
            "result": result_path,
        }
    b10_formal_target_status = {}
    if not b10_formal_targets:
        warnings.append("B10 manifest has no formal theorem target cards")
    else:
        result_path = b10_formal_targets.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B10 formal theorem targets result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_formal_target_status = {
            "status": b10_formal_targets.get("status"),
            "method": b10_formal_targets.get("method"),
            "target_count": payload.get("target_count"),
            "target_types": payload.get("target_types"),
            "dependency_ids": payload.get("dependency_ids"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "formal_theorem_targets_not_proofs":
            errors.append("B10 formal theorem targets must remain marked as targets, not proofs")
        if payload.get("method") != b10_formal_targets.get("method"):
            errors.append("B10 formal theorem targets method mismatch")
        if payload.get("target_count") != b10_formal_targets.get("target_count"):
            errors.append("B10 formal theorem targets count mismatch")
        if len(payload.get("validation_errors", [])) != b10_formal_targets.get("validation_error_count"):
            errors.append("B10 formal theorem target validation-error count mismatch")
        if int(payload.get("target_count", 0)) < 2:
            errors.append("B10 formal theorem target package should include at least two targets")
        for target in payload.get("targets", []):
            if target.get("current_status") != "formal_model_ready_not_proved":
                errors.append(f"B10 target {target.get('id')} should not claim proof completion")
    b10_t2_refresh_boundary_status = {}
    if not b10_t2_refresh_boundary:
        warnings.append("B10 manifest has no B10-T2 minimum-refresh spoofer boundary")
    else:
        result_path = b10_t2_refresh_boundary.get("result")
        markdown_path = b10_t2_refresh_boundary.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T2 refresh-boundary result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T2 refresh-boundary markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_t2_refresh_boundary_status = {
            "status": b10_t2_refresh_boundary.get("status"),
            "method": b10_t2_refresh_boundary.get("method"),
            "source_target_id": b10_t2_refresh_boundary.get("source_target_id"),
            "dependency_benchmark": b10_t2_refresh_boundary.get("dependency_benchmark"),
            "configuration_count": b10_t2_refresh_boundary.get("configuration_count"),
            "maximum_learned_soundness": payload.get("maximum_learned_soundness"),
            "safe_high_leakage_refresh_modes": payload.get("safe_high_leakage_refresh_modes"),
            "unsafe_high_leakage_refresh_modes": payload.get("unsafe_high_leakage_refresh_modes"),
            "explicit_not_bqp_separation": b10_t2_refresh_boundary.get("explicit_not_bqp_separation"),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if b10_t2_refresh_boundary.get("source_target_id") != "B10-T2":
            errors.append("B10-T2 refresh-boundary source target must be B10-T2")
        if b10_t2_refresh_boundary.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T2 refresh-boundary must explicitly avoid BQP separation claims")
        if payload.get("status") != "trained_generative_spoofer_refresh_boundary_not_soundness_proof":
            errors.append("B10-T2 refresh-boundary source result must remain not a soundness proof")
        if payload.get("method") != b10_t2_refresh_boundary.get("method"):
            errors.append("B10-T2 refresh-boundary method mismatch")
        if payload.get("configuration_count") != b10_t2_refresh_boundary.get("configuration_count"):
            errors.append("B10-T2 refresh-boundary configuration count mismatch")
        if "none" not in (payload.get("unsafe_high_leakage_refresh_modes") or []):
            errors.append("B10-T2 refresh-boundary should keep no-refresh high leakage unsafe")
        if not payload.get("safe_high_leakage_refresh_modes"):
            errors.append("B10-T2 refresh-boundary should identify at least one safe high-leakage refresh mode")
    b10_t2_proof_gate_status = {}
    if not b10_t2_proof_gate:
        warnings.append("B10 manifest has no B10-T2 refresh proof-obligation gate")
    else:
        result_path = b10_t2_proof_gate.get("result")
        markdown_path = b10_t2_proof_gate.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T2 proof gate result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T2 proof gate markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_t2_proof_gate_status = {
            "status": b10_t2_proof_gate.get("status"),
            "method": b10_t2_proof_gate.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "lemma_status": payload.get("lemma_status"),
            "configuration_count": payload.get("configuration_count"),
            "proof_obligation_count": len(payload.get("proof_obligations", [])),
            "maximum_learned_soundness": payload.get("maximum_learned_soundness"),
            "soundness_gate": payload.get("soundness_gate"),
            "safe_high_leakage_refresh_modes": payload.get("safe_high_leakage_refresh_modes"),
            "unsafe_high_leakage_refresh_modes": payload.get("unsafe_high_leakage_refresh_modes"),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "hardware_randomized_measurement_circuits_instantiated": payload.get(
                "hardware_randomized_measurement_circuits_instantiated"
            ),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "proof_obligation_gate_proxy_supports_rejection_rule_not_soundness_lemma":
            errors.append("B10-T2 proof gate must remain a proof-obligation gate, not a soundness lemma")
        if payload.get("method") != b10_t2_proof_gate.get("method"):
            errors.append("B10-T2 proof gate method mismatch")
        if payload.get("source_target_id") != "B10-T2":
            errors.append("B10-T2 proof gate source target must be B10-T2")
        if payload.get("lemma_status") != "not_proved_proxy_insufficient_for_general_soundness":
            errors.append("B10-T2 proof gate must state the proxy cannot support a general soundness lemma")
        if payload.get("configuration_count") != b10_t2_proof_gate.get("configuration_count"):
            errors.append("B10-T2 proof gate configuration count mismatch")
        if len(payload.get("proof_obligations", [])) != b10_t2_proof_gate.get("proof_obligation_count"):
            errors.append("B10-T2 proof gate obligation count mismatch")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T2 proof gate must explicitly avoid BQP separation claims")
        if payload.get("hardware_randomized_measurement_circuits_instantiated") is not False:
            errors.append("B10-T2 proof gate must not imply hardware randomized-measurement circuits are done")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B10-T2 proof gate validation errors must be zero")
        if "none" not in (payload.get("unsafe_high_leakage_refresh_modes") or []):
            errors.append("B10-T2 proof gate should reject no-refresh high leakage")
        if float(payload.get("maximum_learned_soundness", 0.0)) <= float(payload.get("soundness_gate", 0.05)):
            errors.append("B10-T2 proof gate should expose an unsafe learned-spoofer row")
    b10_t2_restricted_lemma_status = {}
    if not b10_t2_restricted_lemma:
        warnings.append("B10 manifest has no B10-T2 restricted soundness lemma")
    else:
        result_path = b10_t2_restricted_lemma.get("result")
        markdown_path = b10_t2_restricted_lemma.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T2 restricted lemma result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T2 restricted lemma markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_t2_restricted_lemma_status = {
            "status": b10_t2_restricted_lemma.get("status"),
            "method": b10_t2_restricted_lemma.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "theorem_count": payload.get("theorem_count"),
            "corollary_count": payload.get("corollary_count"),
            "single_unknown_mask_soundness_bound": payload.get("single_unknown_mask_soundness_bound"),
            "signal_gap": payload.get("signal_gap"),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "hardware_randomized_measurement_circuits_instantiated": payload.get(
                "hardware_randomized_measurement_circuits_instantiated"
            ),
            "sampling_hardness_proved": payload.get("sampling_hardness_proved"),
            "empirical_stress_still_required": payload.get("empirical_stress_still_required"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "restricted_soundness_lemma_proved_under_refresh_independence_model":
            errors.append("B10-T2 restricted lemma status mismatch")
        if payload.get("method") != b10_t2_restricted_lemma.get("method"):
            errors.append("B10-T2 restricted lemma method mismatch")
        if payload.get("source_target_id") != "B10-T2":
            errors.append("B10-T2 restricted lemma source target must be B10-T2")
        if payload.get("theorem_count") != b10_t2_restricted_lemma.get("theorem_count"):
            errors.append("B10-T2 restricted lemma theorem count mismatch")
        if payload.get("corollary_count") != b10_t2_restricted_lemma.get("corollary_count"):
            errors.append("B10-T2 restricted lemma corollary count mismatch")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T2 restricted lemma must explicitly avoid BQP separation claims")
        if payload.get("hardware_randomized_measurement_circuits_instantiated") is not False:
            errors.append("B10-T2 restricted lemma must not claim hardware verifier instantiation")
        if payload.get("sampling_hardness_proved") is not False:
            errors.append("B10-T2 restricted lemma must not claim sampling hardness")
        if payload.get("empirical_stress_still_required") is not True:
            errors.append("B10-T2 restricted lemma must keep empirical stress testing required")
        if len(payload.get("validation_errors", [])) != b10_t2_restricted_lemma.get("validation_error_count"):
            errors.append("B10-T2 restricted lemma validation-error count mismatch")
        if float(payload.get("single_unknown_mask_soundness_bound", 1.0)) >= 0.05:
            errors.append("B10-T2 restricted lemma bound should clear the 5% soundness gate")
    b10_t2_transcript_simulator_status = {}
    if not b10_t2_transcript_simulator:
        warnings.append("B10 manifest has no B10-T2 transcript leakage simulator")
    else:
        result_path = b10_t2_transcript_simulator.get("result")
        markdown_path = b10_t2_transcript_simulator.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T2 transcript simulator result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T2 transcript simulator markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_t2_transcript_simulator_status = {
            "status": b10_t2_transcript_simulator.get("status"),
            "method": b10_t2_transcript_simulator.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "configuration_count": payload.get("configuration_count"),
            "minimum_honest_completeness": payload.get("minimum_honest_completeness"),
            "maximum_empirical_soundness": payload.get("maximum_empirical_soundness"),
            "max_soundness_refresh_independent_high_leakage": payload.get(
                "max_soundness_refresh_independent_high_leakage"
            ),
            "min_unknown_independent_count_refresh_high_leakage": payload.get(
                "min_unknown_independent_count_refresh_high_leakage"
            ),
            "refresh_independent_high_leakage_modes": payload.get("refresh_independent_high_leakage_modes"),
            "unsafe_high_leakage_modes": payload.get("unsafe_high_leakage_modes"),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "hardware_randomized_measurement_circuits_instantiated": payload.get(
                "hardware_randomized_measurement_circuits_instantiated"
            ),
            "sampling_hardness_proved": payload.get("sampling_hardness_proved"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "transcript_leakage_simulator_supports_restricted_lemma_not_hardware_verifier":
            errors.append("B10-T2 transcript simulator status mismatch")
        if payload.get("method") != b10_t2_transcript_simulator.get("method"):
            errors.append("B10-T2 transcript simulator method mismatch")
        if payload.get("source_target_id") != "B10-T2":
            errors.append("B10-T2 transcript simulator source target must be B10-T2")
        if payload.get("configuration_count") != b10_t2_transcript_simulator.get("configuration_count"):
            errors.append("B10-T2 transcript simulator configuration count mismatch")
        if int(payload.get("configuration_count", 0)) != 192:
            errors.append("B10-T2 transcript simulator should cover 192 configurations")
        if float(payload.get("minimum_honest_completeness", 0.0)) < 0.95:
            errors.append("B10-T2 transcript simulator honest completeness should be at least 0.95")
        if float(payload.get("max_soundness_refresh_independent_high_leakage", 1.0)) > 0.05:
            errors.append("B10-T2 transcript simulator refreshed high-leakage soundness should clear the 5% gate")
        if float(payload.get("min_unknown_independent_count_refresh_high_leakage", 0.0)) < 1:
            errors.append("B10-T2 transcript simulator should retain at least one unknown independent predicate")
        if "none" not in (payload.get("unsafe_high_leakage_modes") or []):
            errors.append("B10-T2 transcript simulator should keep no-refresh high leakage unsafe")
        required_refresh_modes = {"projection_rotation", "challenge_refresh", "refresh_plus_rotation"}
        if not required_refresh_modes.issubset(set(payload.get("refresh_independent_high_leakage_modes") or [])):
            errors.append("B10-T2 transcript simulator missing required refreshed high-leakage modes")
        if payload.get("hardware_randomized_measurement_circuits_instantiated") is not False:
            errors.append("B10-T2 transcript simulator must not claim hardware verifier instantiation")
        if payload.get("sampling_hardness_proved") is not False:
            errors.append("B10-T2 transcript simulator must not claim sampling hardness")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T2 transcript simulator must explicitly avoid BQP separation claims")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B10-T2 transcript simulator validation errors must be zero")
    b10_t2_device_noise_bridge_status = {}
    if not b10_t2_device_noise_bridge:
        warnings.append("B10 manifest has no B10-T2 device-noise transcript bridge")
    else:
        result_path = b10_t2_device_noise_bridge.get("result")
        markdown_path = b10_t2_device_noise_bridge.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T2 device-noise bridge result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T2 device-noise bridge markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_t2_device_noise_bridge_status = {
            "status": b10_t2_device_noise_bridge.get("status"),
            "method": b10_t2_device_noise_bridge.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "configuration_count": payload.get("configuration_count"),
            "device_profile_count": payload.get("device_profile_count"),
            "minimum_honest_completeness": payload.get("minimum_honest_completeness"),
            "minimum_honest_completeness_bridge_safe_high_leakage": payload.get(
                "minimum_honest_completeness_bridge_safe_high_leakage"
            ),
            "max_soundness_bridge_safe_high_leakage": payload.get("max_soundness_bridge_safe_high_leakage"),
            "min_unknown_independent_count_bridge_safe_high_leakage": payload.get(
                "min_unknown_independent_count_bridge_safe_high_leakage"
            ),
            "bridge_safe_refresh_modes": payload.get("bridge_safe_refresh_modes"),
            "bridge_safe_device_profiles": payload.get("bridge_safe_device_profiles"),
            "margin_sensitive_refresh_modes": payload.get("margin_sensitive_refresh_modes"),
            "unsafe_device_profiles": payload.get("unsafe_device_profiles"),
            "device_noise_transcript_bridge_instantiated": payload.get(
                "device_noise_transcript_bridge_instantiated"
            ),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "hardware_randomized_measurement_circuits_instantiated": payload.get(
                "hardware_randomized_measurement_circuits_instantiated"
            ),
            "sampling_hardness_proved": payload.get("sampling_hardness_proved"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "device_noise_transcript_bridge_supports_bounded_noise_not_hardware_verifier":
            errors.append("B10-T2 device-noise bridge status mismatch")
        if payload.get("method") != b10_t2_device_noise_bridge.get("method"):
            errors.append("B10-T2 device-noise bridge method mismatch")
        if payload.get("source_target_id") != "B10-T2":
            errors.append("B10-T2 device-noise bridge source target must be B10-T2")
        if payload.get("configuration_count") != b10_t2_device_noise_bridge.get("configuration_count"):
            errors.append("B10-T2 device-noise bridge configuration count mismatch")
        if int(payload.get("configuration_count", 0)) != 480:
            errors.append("B10-T2 device-noise bridge should cover 480 configurations")
        if int(payload.get("device_profile_count", 0)) != 5:
            errors.append("B10-T2 device-noise bridge should cover 5 device profiles")
        if float(payload.get("minimum_honest_completeness_bridge_safe_high_leakage", 0.0)) < 0.95:
            errors.append("B10-T2 device-noise bridge should preserve honest completeness")
        if float(payload.get("max_soundness_bridge_safe_high_leakage", 1.0)) > 0.05:
            errors.append("B10-T2 device-noise bridge safe refresh modes should clear the 5% gate")
        if float(payload.get("min_unknown_independent_count_bridge_safe_high_leakage", 0.0)) < 1:
            errors.append("B10-T2 device-noise bridge should retain unknown independent predicates")
        required_bridge_modes = {"challenge_refresh", "refresh_plus_rotation"}
        if not required_bridge_modes.issubset(set(payload.get("bridge_safe_refresh_modes") or [])):
            errors.append("B10-T2 device-noise bridge missing required bridge-safe refresh modes")
        if "projection_rotation" not in (payload.get("margin_sensitive_refresh_modes") or []):
            errors.append("B10-T2 device-noise bridge should mark projection_rotation margin-sensitive")
        if "calibration_side_channel" not in (payload.get("unsafe_device_profiles") or []):
            errors.append("B10-T2 device-noise bridge should reject calibration side-channel")
        if payload.get("device_noise_transcript_bridge_instantiated") is not True:
            errors.append("B10-T2 device-noise bridge must instantiate a transcript bridge")
        if payload.get("hardware_randomized_measurement_circuits_instantiated") is not False:
            errors.append("B10-T2 device-noise bridge must not claim hardware verifier instantiation")
        if payload.get("sampling_hardness_proved") is not False:
            errors.append("B10-T2 device-noise bridge must not claim sampling hardness")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T2 device-noise bridge must explicitly avoid BQP separation claims")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B10-T2 device-noise bridge validation errors must be zero")
    b10_t2_qiskit_aer_bridge_status = {}
    if not b10_t2_qiskit_aer_bridge:
        warnings.append("B10 manifest has no B10-T2 Qiskit/Aer verifier bridge")
    else:
        result_path = b10_t2_qiskit_aer_bridge.get("result")
        markdown_path = b10_t2_qiskit_aer_bridge.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T2 Qiskit/Aer bridge result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T2 Qiskit/Aer bridge markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_t2_qiskit_aer_bridge_status = {
            "status": b10_t2_qiskit_aer_bridge.get("status"),
            "method": b10_t2_qiskit_aer_bridge.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "aer_circuit_count": payload.get("aer_circuit_count"),
            "max_circuit_qubits_with_ancilla": payload.get("max_circuit_qubits_with_ancilla"),
            "aer_semantic_mismatch_count": payload.get("aer_semantic_mismatch_count"),
            "minimum_aer_honest_completeness": payload.get("minimum_aer_honest_completeness"),
            "maximum_aer_predicate_bit_error_rate": payload.get("maximum_aer_predicate_bit_error_rate"),
            "source_device_noise_max_safe_high_leakage_soundness": payload.get(
                "source_device_noise_max_safe_high_leakage_soundness"
            ),
            "source_margin_sensitive_refresh_modes": payload.get("source_margin_sensitive_refresh_modes"),
            "hardware_executable_randomized_measurement_circuits_instantiated": payload.get(
                "hardware_executable_randomized_measurement_circuits_instantiated"
            ),
            "qiskit_aer_bridge_instantiated": payload.get("qiskit_aer_bridge_instantiated"),
            "hardware_execution_performed": payload.get("hardware_execution_performed"),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "sampling_hardness_proved": payload.get("sampling_hardness_proved"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "qiskit_aer_circuit_level_verifier_bridge_not_hardware_execution":
            errors.append("B10-T2 Qiskit/Aer bridge status mismatch")
        if payload.get("method") != b10_t2_qiskit_aer_bridge.get("method"):
            errors.append("B10-T2 Qiskit/Aer bridge method mismatch")
        if payload.get("source_target_id") != "B10-T2":
            errors.append("B10-T2 Qiskit/Aer bridge source target must be B10-T2")
        if payload.get("aer_circuit_count") != b10_t2_qiskit_aer_bridge.get("aer_circuit_count"):
            errors.append("B10-T2 Qiskit/Aer bridge circuit count mismatch")
        if int(payload.get("aer_circuit_count", 0)) != 216:
            errors.append("B10-T2 Qiskit/Aer bridge should run 216 Aer circuits")
        if int(payload.get("max_circuit_qubits_with_ancilla", 0)) < 20:
            errors.append("B10-T2 Qiskit/Aer bridge should include verifier ancilla circuits")
        if int(payload.get("aer_semantic_mismatch_count", -1)) != 0:
            errors.append("B10-T2 Qiskit/Aer bridge should have zero semantic mismatches")
        if float(payload.get("minimum_aer_honest_completeness", 0.0)) < 0.99:
            errors.append("B10-T2 Qiskit/Aer bridge should preserve ideal honest completeness")
        if float(payload.get("maximum_aer_predicate_bit_error_rate", 1.0)) > 0.0:
            errors.append("B10-T2 Qiskit/Aer bridge should have zero ideal predicate bit errors")
        if float(payload.get("source_device_noise_max_safe_high_leakage_soundness", 1.0)) > 0.05:
            errors.append("B10-T2 Qiskit/Aer bridge source device-noise soundness should clear 5%")
        if "projection_rotation" not in (payload.get("source_margin_sensitive_refresh_modes") or []):
            errors.append("B10-T2 Qiskit/Aer bridge should preserve projection_rotation margin boundary")
        if payload.get("hardware_executable_randomized_measurement_circuits_instantiated") is not True:
            errors.append("B10-T2 Qiskit/Aer bridge should instantiate hardware-executable verifier circuits")
        if payload.get("qiskit_aer_bridge_instantiated") is not True:
            errors.append("B10-T2 Qiskit/Aer bridge must instantiate Qiskit/Aer bridge")
        if payload.get("hardware_execution_performed") is not False:
            errors.append("B10-T2 Qiskit/Aer bridge must not claim hardware execution")
        if payload.get("sampling_hardness_proved") is not False:
            errors.append("B10-T2 Qiskit/Aer bridge must not claim sampling hardness")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T2 Qiskit/Aer bridge must explicitly avoid BQP separation claims")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B10-T2 Qiskit/Aer bridge validation errors must be zero")
    b10_t2_noisy_aer_bridge_status = {}
    if not b10_t2_noisy_aer_bridge:
        warnings.append("B10 manifest has no B10-T2 noisy Aer verifier bridge")
    else:
        result_path = b10_t2_noisy_aer_bridge.get("result")
        markdown_path = b10_t2_noisy_aer_bridge.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T2 noisy Aer bridge result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T2 noisy Aer bridge markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_t2_noisy_aer_bridge_status = {
            "status": b10_t2_noisy_aer_bridge.get("status"),
            "method": b10_t2_noisy_aer_bridge.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "noisy_aer_circuit_count": payload.get("noisy_aer_circuit_count"),
            "max_circuit_qubits_with_ancilla": payload.get("max_circuit_qubits_with_ancilla"),
            "minimum_safe_noisy_honest_acceptance": payload.get("minimum_safe_noisy_honest_acceptance"),
            "maximum_safe_noisy_adversary_acceptance": payload.get("maximum_safe_noisy_adversary_acceptance"),
            "maximum_safe_noisy_honest_predicate_bit_error_rate": payload.get(
                "maximum_safe_noisy_honest_predicate_bit_error_rate"
            ),
            "minimum_safe_noisy_unknown_independent_count": payload.get(
                "minimum_safe_noisy_unknown_independent_count"
            ),
            "source_device_noise_max_safe_high_leakage_soundness": payload.get(
                "source_device_noise_max_safe_high_leakage_soundness"
            ),
            "bridge_safe_refresh_modes": payload.get("bridge_safe_refresh_modes"),
            "bridge_safe_noisy_device_profiles": payload.get("bridge_safe_noisy_device_profiles"),
            "unsafe_noisy_device_profiles": payload.get("unsafe_noisy_device_profiles"),
            "noisy_qiskit_aer_bridge_instantiated": payload.get("noisy_qiskit_aer_bridge_instantiated"),
            "circuit_level_adversary_inputs_instantiated": payload.get(
                "circuit_level_adversary_inputs_instantiated"
            ),
            "hardware_execution_performed": payload.get("hardware_execution_performed"),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "sampling_hardness_proved": payload.get("sampling_hardness_proved"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "noisy_aer_circuit_verifier_bridge_not_hardware_execution":
            errors.append("B10-T2 noisy Aer bridge status mismatch")
        if payload.get("method") != b10_t2_noisy_aer_bridge.get("method"):
            errors.append("B10-T2 noisy Aer bridge method mismatch")
        if payload.get("source_target_id") != "B10-T2":
            errors.append("B10-T2 noisy Aer bridge source target must be B10-T2")
        if payload.get("noisy_aer_circuit_count") != b10_t2_noisy_aer_bridge.get("noisy_aer_circuit_count"):
            errors.append("B10-T2 noisy Aer bridge circuit count mismatch")
        if int(payload.get("noisy_aer_circuit_count", 0)) < 9000:
            errors.append("B10-T2 noisy Aer bridge should run at least 9000 noisy circuits")
        if float(payload.get("minimum_safe_noisy_honest_acceptance", 0.0)) < 0.95:
            errors.append("B10-T2 noisy Aer bridge should preserve safe noisy honest acceptance")
        if float(payload.get("maximum_safe_noisy_adversary_acceptance", 1.0)) > 0.05:
            errors.append("B10-T2 noisy Aer bridge should reject circuit-level adversaries in safe modes")
        if float(payload.get("maximum_safe_noisy_honest_predicate_bit_error_rate", 1.0)) > 0.15:
            errors.append("B10-T2 noisy Aer bridge honest predicate-bit error exceeds audit threshold")
        if float(payload.get("minimum_safe_noisy_unknown_independent_count", 0.0)) < 1:
            errors.append("B10-T2 noisy Aer bridge should retain unknown independent predicates")
        if float(payload.get("source_device_noise_max_safe_high_leakage_soundness", 1.0)) > 0.05:
            errors.append("B10-T2 noisy Aer bridge source transcript soundness should clear 5%")
        required_noisy_modes = {"challenge_refresh", "refresh_plus_rotation"}
        if not required_noisy_modes.issubset(set(payload.get("bridge_safe_refresh_modes") or [])):
            errors.append("B10-T2 noisy Aer bridge missing bridge-safe refresh modes")
        if "calibration_side_channel" not in (payload.get("unsafe_noisy_device_profiles") or []):
            errors.append("B10-T2 noisy Aer bridge should reject calibration side-channel")
        if payload.get("noisy_qiskit_aer_bridge_instantiated") is not True:
            errors.append("B10-T2 noisy Aer bridge must instantiate noisy Qiskit/Aer bridge")
        if payload.get("circuit_level_adversary_inputs_instantiated") is not True:
            errors.append("B10-T2 noisy Aer bridge must instantiate circuit-level adversary inputs")
        if payload.get("hardware_execution_performed") is not False:
            errors.append("B10-T2 noisy Aer bridge must not claim hardware execution")
        if payload.get("sampling_hardness_proved") is not False:
            errors.append("B10-T2 noisy Aer bridge must not claim sampling hardness")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T2 noisy Aer bridge must explicitly avoid BQP separation claims")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B10-T2 noisy Aer bridge validation errors must be zero")
    b10_t2_backend_calibrated_bridge_status = {}
    if not b10_t2_backend_calibrated_bridge:
        warnings.append("B10 manifest has no B10-T2 backend-calibrated verifier bridge")
    else:
        result_path = b10_t2_backend_calibrated_bridge.get("result")
        markdown_path = b10_t2_backend_calibrated_bridge.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T2 backend-calibrated bridge result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T2 backend-calibrated bridge markdown missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_t2_backend_calibrated_bridge_status = {
            "status": b10_t2_backend_calibrated_bridge.get("status"),
            "method": b10_t2_backend_calibrated_bridge.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "backend_calibrated_aer_circuit_count": payload.get("backend_calibrated_aer_circuit_count"),
            "max_circuit_qubits_with_ancilla": payload.get("max_circuit_qubits_with_ancilla"),
            "minimum_safe_calibrated_honest_acceptance": payload.get(
                "minimum_safe_calibrated_honest_acceptance"
            ),
            "maximum_safe_calibrated_adversary_acceptance": payload.get(
                "maximum_safe_calibrated_adversary_acceptance"
            ),
            "maximum_safe_calibrated_honest_predicate_bit_error_rate": payload.get(
                "maximum_safe_calibrated_honest_predicate_bit_error_rate"
            ),
            "minimum_safe_calibrated_unknown_independent_count": payload.get(
                "minimum_safe_calibrated_unknown_independent_count"
            ),
            "source_noisy_aer_max_safe_adversary_acceptance": payload.get(
                "source_noisy_aer_max_safe_adversary_acceptance"
            ),
            "source_device_noise_max_safe_high_leakage_soundness": payload.get(
                "source_device_noise_max_safe_high_leakage_soundness"
            ),
            "bridge_safe_refresh_modes": payload.get("bridge_safe_refresh_modes"),
            "bridge_safe_backend_snapshots": payload.get("bridge_safe_backend_snapshots"),
            "unsafe_calibrated_refresh_modes": payload.get("unsafe_calibrated_refresh_modes"),
            "backend_calibrated_noise_parameters_instantiated": payload.get(
                "backend_calibrated_noise_parameters_instantiated"
            ),
            "qiskit_generic_backend_v2_used": payload.get("qiskit_generic_backend_v2_used"),
            "real_backend_properties_used": payload.get("real_backend_properties_used"),
            "hardware_execution_performed": payload.get("hardware_execution_performed"),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "sampling_hardness_proved": payload.get("sampling_hardness_proved"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "backend_calibrated_aer_verifier_bridge_not_hardware_execution":
            errors.append("B10-T2 backend-calibrated bridge status mismatch")
        if payload.get("method") != b10_t2_backend_calibrated_bridge.get("method"):
            errors.append("B10-T2 backend-calibrated bridge method mismatch")
        if payload.get("source_target_id") != "B10-T2":
            errors.append("B10-T2 backend-calibrated bridge source target must be B10-T2")
        if payload.get("backend_calibrated_aer_circuit_count") != b10_t2_backend_calibrated_bridge.get(
            "backend_calibrated_aer_circuit_count"
        ):
            errors.append("B10-T2 backend-calibrated bridge circuit count mismatch")
        if int(payload.get("backend_calibrated_aer_circuit_count", 0)) < 5000:
            errors.append("B10-T2 backend-calibrated bridge should run at least 5000 circuits")
        if float(payload.get("minimum_safe_calibrated_honest_acceptance", 0.0)) < 0.95:
            errors.append("B10-T2 backend-calibrated bridge should preserve safe calibrated honest acceptance")
        if float(payload.get("maximum_safe_calibrated_adversary_acceptance", 1.0)) > 0.35:
            errors.append("B10-T2 backend-calibrated bridge adversary acceptance exceeds audit threshold")
        if float(payload.get("maximum_safe_calibrated_honest_predicate_bit_error_rate", 1.0)) > 0.20:
            errors.append("B10-T2 backend-calibrated bridge honest predicate-bit error exceeds audit threshold")
        if float(payload.get("minimum_safe_calibrated_unknown_independent_count", 0.0)) < 1:
            errors.append("B10-T2 backend-calibrated bridge should retain unknown independent predicates")
        if float(payload.get("source_noisy_aer_max_safe_adversary_acceptance", 1.0)) > 0.05:
            errors.append("B10-T2 backend-calibrated bridge should inherit a safe noisy-Aer source")
        if float(payload.get("source_device_noise_max_safe_high_leakage_soundness", 1.0)) > 0.05:
            errors.append("B10-T2 backend-calibrated bridge source transcript soundness should clear 5%")
        required_calibrated_modes = {"challenge_refresh", "refresh_plus_rotation"}
        if not required_calibrated_modes.issubset(set(payload.get("bridge_safe_refresh_modes") or [])):
            errors.append("B10-T2 backend-calibrated bridge missing bridge-safe refresh modes")
        if "none" not in (payload.get("unsafe_calibrated_refresh_modes") or []):
            errors.append("B10-T2 backend-calibrated bridge should keep no-refresh unsafe")
        if len(payload.get("bridge_safe_backend_snapshots") or []) < 3:
            errors.append("B10-T2 backend-calibrated bridge should include all three backend snapshots")
        if payload.get("backend_calibrated_noise_parameters_instantiated") is not True:
            errors.append("B10-T2 backend-calibrated bridge must instantiate backend-calibrated noise parameters")
        if payload.get("qiskit_generic_backend_v2_used") is not True:
            errors.append("B10-T2 backend-calibrated bridge must record GenericBackendV2 use")
        if payload.get("real_backend_properties_used") is not False:
            errors.append("B10-T2 backend-calibrated bridge must not claim real backend properties")
        if payload.get("hardware_execution_performed") is not False:
            errors.append("B10-T2 backend-calibrated bridge must not claim hardware execution")
        if payload.get("sampling_hardness_proved") is not False:
            errors.append("B10-T2 backend-calibrated bridge must not claim sampling hardness")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T2 backend-calibrated bridge must explicitly avoid BQP separation claims")
        if len(payload.get("validation_errors", [])) != 0:
            errors.append("B10-T2 backend-calibrated bridge validation errors must be zero")
    b10_t1_proof_status = {}
    if not b10_t1_proof:
        warnings.append("B10 manifest has no B10-T1 negative-boundary proof attempt")
    else:
        result_path = b10_t1_proof.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B10-T1 negative-boundary proof result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_t1_proof_status = {
            "status": b10_t1_proof.get("status"),
            "method": b10_t1_proof.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "proof_result": payload.get("proof_result"),
            "theorem_count": payload.get("theorem_count"),
            "open_obligation_count": payload.get("open_obligation_count"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "negative_boundary_accounting_lemma_proved_under_explicit_io_model_not_bqp_separation":
            errors.append("B10-T1 proof attempt must remain marked as restricted explicit-I/O accounting, not broad separation")
        if payload.get("method") != b10_t1_proof.get("method"):
            errors.append("B10-T1 proof attempt method mismatch")
        if payload.get("source_target_id") != b10_t1_proof.get("source_target_id"):
            errors.append("B10-T1 proof attempt source target mismatch")
        if payload.get("theorem_count") != b10_t1_proof.get("theorem_count"):
            errors.append("B10-T1 proof attempt theorem count mismatch")
        if payload.get("open_obligation_count") != b10_t1_proof.get("open_obligation_count"):
            errors.append("B10-T1 proof attempt open-obligation count mismatch")
        if len(payload.get("validation_errors", [])) != b10_t1_proof.get("validation_error_count"):
            errors.append("B10-T1 proof attempt validation-error count mismatch")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T1 proof attempt must explicitly avoid BQP separation claims")
        if payload.get("proof_result") != "restricted_negative_boundary_accounting_lemma":
            errors.append("B10-T1 proof attempt proof result must remain a restricted accounting lemma")
    b10_t1_source_backed_status = {}
    if not b10_t1_source_backed:
        warnings.append("B10 manifest has no B10-T1 source-backed boundary note")
    else:
        result_path = b10_t1_source_backed.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B10-T1 source-backed boundary result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        b10_t1_source_backed_status = {
            "status": b10_t1_source_backed.get("status"),
            "method": b10_t1_source_backed.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "source_count": payload.get("source_count"),
            "baseline_count": payload.get("baseline_count"),
            "boundary_check_count": len(payload.get("boundary_checks", [])),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "source_backed_denominator_baselines_instantiated_not_publishable_theorem":
            errors.append("B10-T1 source-backed note must not claim to be a publishable theorem")
        if payload.get("method") != b10_t1_source_backed.get("method"):
            errors.append("B10-T1 source-backed note method mismatch")
        if payload.get("source_target_id") != b10_t1_source_backed.get("source_target_id"):
            errors.append("B10-T1 source-backed note source target mismatch")
        if payload.get("source_count") != b10_t1_source_backed.get("source_count"):
            errors.append("B10-T1 source-backed note source count mismatch")
        if payload.get("baseline_count") != b10_t1_source_backed.get("baseline_count"):
            errors.append("B10-T1 source-backed note baseline count mismatch")
        if len(payload.get("boundary_checks", [])) != b10_t1_source_backed.get("boundary_check_count"):
            errors.append("B10-T1 source-backed note boundary-check count mismatch")
        if len(payload.get("validation_errors", [])) != b10_t1_source_backed.get("validation_error_count"):
            errors.append("B10-T1 source-backed note validation-error count mismatch")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T1 source-backed note must explicitly avoid BQP separation claims")
    b10_t1_numerical_table_status = {}
    if not b10_t1_numerical_table:
        warnings.append("B10 manifest has no B10-T1 numerical denominator table")
    else:
        result_path = b10_t1_numerical_table.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B10-T1 numerical denominator result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b10_t1_numerical_table_status = {
            "status": b10_t1_numerical_table.get("status"),
            "method": b10_t1_numerical_table.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "family_count": summary.get("family_count"),
            "instance_count": summary.get("instance_count"),
            "cg_instance_count": summary.get("cg_instance_count"),
            "lsqr_instance_count": summary.get("lsqr_instance_count"),
            "max_relative_residual": summary.get("max_relative_residual"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "numerical_denominator_table_instantiated_not_quantum_speedup_claim":
            errors.append("B10-T1 numerical denominator table must not claim quantum speedup")
        if payload.get("method") != b10_t1_numerical_table.get("method"):
            errors.append("B10-T1 numerical denominator table method mismatch")
        if payload.get("source_target_id") != b10_t1_numerical_table.get("source_target_id"):
            errors.append("B10-T1 numerical denominator table source target mismatch")
        if summary.get("family_count") != b10_t1_numerical_table.get("family_count"):
            errors.append("B10-T1 numerical denominator table family count mismatch")
        if summary.get("instance_count") != b10_t1_numerical_table.get("instance_count"):
            errors.append("B10-T1 numerical denominator table instance count mismatch")
        if summary.get("cg_instance_count") != b10_t1_numerical_table.get("cg_instance_count"):
            errors.append("B10-T1 numerical denominator table CG instance count mismatch")
        if summary.get("lsqr_instance_count") != b10_t1_numerical_table.get("lsqr_instance_count"):
            errors.append("B10-T1 numerical denominator table LSQR instance count mismatch")
        if len(payload.get("validation_errors", [])) != b10_t1_numerical_table.get("validation_error_count"):
            errors.append("B10-T1 numerical denominator table validation-error count mismatch")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T1 numerical denominator table must explicitly avoid BQP separation claims")
        if summary.get("max_relative_residual", 1.0) > 1e-5:
            errors.append("B10-T1 numerical denominator table residual exceeds audit threshold")
    b10_t1_d5_table_status = {}
    if not b10_t1_d5_table:
        warnings.append("B10 manifest has no B10-T1 D5 observable denominator table")
    else:
        result_path = b10_t1_d5_table.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B10-T1 D5 observable denominator result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b10_t1_d5_table_status = {
            "status": b10_t1_d5_table.get("status"),
            "method": b10_t1_d5_table.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "dependency_benchmark": payload.get("dependency_benchmark"),
            "instance_count": summary.get("instance_count"),
            "max_hilbert_dimension": summary.get("max_hilbert_dimension"),
            "max_relative_residual": summary.get("max_relative_residual"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "d5_observable_denominator_table_instantiated_not_quantum_speedup_claim":
            errors.append("B10-T1 D5 observable denominator table must not claim quantum speedup")
        if payload.get("method") != b10_t1_d5_table.get("method"):
            errors.append("B10-T1 D5 observable denominator table method mismatch")
        if payload.get("source_target_id") != b10_t1_d5_table.get("source_target_id"):
            errors.append("B10-T1 D5 observable denominator table source target mismatch")
        if payload.get("dependency_benchmark") != b10_t1_d5_table.get("dependency_benchmark"):
            errors.append("B10-T1 D5 observable denominator table dependency mismatch")
        if summary.get("instance_count") != b10_t1_d5_table.get("instance_count"):
            errors.append("B10-T1 D5 observable denominator table instance count mismatch")
        if summary.get("max_hilbert_dimension") != b10_t1_d5_table.get("max_hilbert_dimension"):
            errors.append("B10-T1 D5 observable denominator table max Hilbert dimension mismatch")
        if len(payload.get("validation_errors", [])) != b10_t1_d5_table.get("validation_error_count"):
            errors.append("B10-T1 D5 observable denominator table validation-error count mismatch")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T1 D5 observable denominator table must explicitly avoid BQP separation claims")
        if summary.get("max_relative_residual", 1.0) > 1e-6:
            errors.append("B10-T1 D5 observable denominator table residual exceeds audit threshold")
    b10_t1_d5_b3_table_status = {}
    if not b10_t1_d5_b3_table:
        warnings.append("B10 manifest has no B10-T1 D5 B3 molecular observable table")
    else:
        result_path = b10_t1_d5_b3_table.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B10-T1 D5 B3 molecular observable result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b10_t1_d5_b3_table_status = {
            "status": b10_t1_d5_b3_table.get("status"),
            "method": b10_t1_d5_b3_table.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "dependency_benchmark": payload.get("dependency_benchmark"),
            "instance_count": summary.get("instance_count"),
            "max_matrix_dimension": summary.get("max_matrix_dimension"),
            "max_relative_residual": summary.get("max_relative_residual"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "b3_d5_molecular_observable_denominator_proxy_not_reaction_solution":
            errors.append("B10-T1 D5 B3 molecular table must not claim reaction solution")
        if payload.get("method") != b10_t1_d5_b3_table.get("method"):
            errors.append("B10-T1 D5 B3 molecular table method mismatch")
        if payload.get("source_target_id") != b10_t1_d5_b3_table.get("source_target_id"):
            errors.append("B10-T1 D5 B3 molecular table source target mismatch")
        if payload.get("dependency_benchmark") != b10_t1_d5_b3_table.get("dependency_benchmark"):
            errors.append("B10-T1 D5 B3 molecular table dependency mismatch")
        if summary.get("instance_count") != b10_t1_d5_b3_table.get("instance_count"):
            errors.append("B10-T1 D5 B3 molecular table instance count mismatch")
        if summary.get("max_matrix_dimension") != b10_t1_d5_b3_table.get("max_matrix_dimension"):
            errors.append("B10-T1 D5 B3 molecular table max matrix dimension mismatch")
        if len(payload.get("validation_errors", [])) != b10_t1_d5_b3_table.get("validation_error_count"):
            errors.append("B10-T1 D5 B3 molecular table validation-error count mismatch")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T1 D5 B3 molecular table must explicitly avoid BQP separation claims")
        if summary.get("max_relative_residual", 1.0) > 1e-6:
            errors.append("B10-T1 D5 B3 molecular table residual exceeds audit threshold")
    b10_t1_d5_b3_reaction_table_status = {}
    if not b10_t1_d5_b3_reaction_table:
        warnings.append("B10 manifest has no B10-T1 D5 B3 reaction observable table")
    else:
        result_path = b10_t1_d5_b3_reaction_table.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B10-T1 D5 B3 reaction observable result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b10_t1_d5_b3_reaction_table_status = {
            "status": b10_t1_d5_b3_reaction_table.get("status"),
            "method": b10_t1_d5_b3_reaction_table.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "dependency_benchmark": payload.get("dependency_benchmark"),
            "instance_count": summary.get("instance_count"),
            "max_response_dimension": summary.get("max_response_dimension"),
            "max_relative_residual": summary.get("max_relative_residual"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "hamiltonian_derived_b3_reaction_observable_denominator_not_reaction_solution":
            errors.append("B10-T1 D5 B3 reaction table must not claim reaction solution")
        if payload.get("method") != b10_t1_d5_b3_reaction_table.get("method"):
            errors.append("B10-T1 D5 B3 reaction table method mismatch")
        if payload.get("source_target_id") != b10_t1_d5_b3_reaction_table.get("source_target_id"):
            errors.append("B10-T1 D5 B3 reaction table source target mismatch")
        if payload.get("dependency_benchmark") != b10_t1_d5_b3_reaction_table.get("dependency_benchmark"):
            errors.append("B10-T1 D5 B3 reaction table dependency mismatch")
        if summary.get("instance_count") != b10_t1_d5_b3_reaction_table.get("instance_count"):
            errors.append("B10-T1 D5 B3 reaction table instance count mismatch")
        if summary.get("max_response_dimension") != b10_t1_d5_b3_reaction_table.get("max_response_dimension"):
            errors.append("B10-T1 D5 B3 reaction table max response dimension mismatch")
        if len(payload.get("validation_errors", [])) != b10_t1_d5_b3_reaction_table.get("validation_error_count"):
            errors.append("B10-T1 D5 B3 reaction table validation-error count mismatch")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T1 D5 B3 reaction table must explicitly avoid BQP separation claims")
        if summary.get("max_relative_residual", 1.0) > 1e-8:
            errors.append("B10-T1 D5 B3 reaction table residual exceeds audit threshold")
    b10_t1_d5_b3_correlated_table_status = {}
    if not b10_t1_d5_b3_correlated_table:
        warnings.append("B10 manifest has no B10-T1 D5 B3 correlated reference table")
    else:
        result_path = b10_t1_d5_b3_correlated_table.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B10-T1 D5 B3 correlated reference result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b10_t1_d5_b3_correlated_table_status = {
            "status": b10_t1_d5_b3_correlated_table.get("status"),
            "method": b10_t1_d5_b3_correlated_table.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "dependency_benchmark": payload.get("dependency_benchmark"),
            "instance_count": summary.get("instance_count"),
            "method_count": len(summary.get("methods", [])),
            "max_abs_ccsd_derivative_shift_vs_rhf": summary.get("max_abs_ccsd_derivative_shift_vs_rhf"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "correlated_b3_reaction_references_instantiated_not_quantum_advantage_claim":
            errors.append("B10-T1 D5 B3 correlated reference table must not claim quantum advantage")
        if payload.get("method") != b10_t1_d5_b3_correlated_table.get("method"):
            errors.append("B10-T1 D5 B3 correlated reference table method mismatch")
        if payload.get("source_target_id") != b10_t1_d5_b3_correlated_table.get("source_target_id"):
            errors.append("B10-T1 D5 B3 correlated reference table source target mismatch")
        if payload.get("dependency_benchmark") != b10_t1_d5_b3_correlated_table.get("dependency_benchmark"):
            errors.append("B10-T1 D5 B3 correlated reference table dependency mismatch")
        if summary.get("instance_count") != b10_t1_d5_b3_correlated_table.get("instance_count"):
            errors.append("B10-T1 D5 B3 correlated reference table instance count mismatch")
        if len(summary.get("methods", [])) != b10_t1_d5_b3_correlated_table.get("method_count"):
            errors.append("B10-T1 D5 B3 correlated reference table method count mismatch")
        if len(payload.get("validation_errors", [])) != b10_t1_d5_b3_correlated_table.get("validation_error_count"):
            errors.append("B10-T1 D5 B3 correlated reference table validation-error count mismatch")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T1 D5 B3 correlated reference table must explicitly avoid BQP separation claims")
        if summary.get("max_abs_ccsd_derivative_shift_vs_rhf", 0.0) <= 0.0:
            errors.append("B10-T1 D5 B3 correlated reference table has no nonzero CCSD-vs-RHF derivative shift")
    b10_t1_d5_b3_fci_table_status = {}
    if not b10_t1_d5_b3_fci_table:
        warnings.append("B10 manifest has no B10-T1 D5 B3 FCI reference table")
    else:
        result_path = b10_t1_d5_b3_fci_table.get("result")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        if not result_exists:
            errors.append(f"B10-T1 D5 B3 FCI reference result path missing: {result_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b10_t1_d5_b3_fci_table_status = {
            "status": b10_t1_d5_b3_fci_table.get("status"),
            "method": b10_t1_d5_b3_fci_table.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "dependency_benchmark": payload.get("dependency_benchmark"),
            "instance_count": summary.get("instance_count"),
            "method_count": len(summary.get("methods", [])),
            "max_abs_fci_derivative_shift_vs_rhf": summary.get("max_abs_fci_derivative_shift_vs_rhf"),
            "max_abs_fci_derivative_shift_vs_ccsd": summary.get("max_abs_fci_derivative_shift_vs_ccsd"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "explicit_not_bqp_separation": payload.get("explicit_not_bqp_separation"),
            "result_exists": result_exists,
            "result": result_path,
        }
        if payload.get("status") != "fci_b3_reaction_references_instantiated_not_quantum_advantage_claim":
            errors.append("B10-T1 D5 B3 FCI reference table must not claim quantum advantage")
        if payload.get("method") != b10_t1_d5_b3_fci_table.get("method"):
            errors.append("B10-T1 D5 B3 FCI reference table method mismatch")
        if payload.get("source_target_id") != b10_t1_d5_b3_fci_table.get("source_target_id"):
            errors.append("B10-T1 D5 B3 FCI reference table source target mismatch")
        if payload.get("dependency_benchmark") != b10_t1_d5_b3_fci_table.get("dependency_benchmark"):
            errors.append("B10-T1 D5 B3 FCI reference table dependency mismatch")
        if summary.get("instance_count") != b10_t1_d5_b3_fci_table.get("instance_count"):
            errors.append("B10-T1 D5 B3 FCI reference table instance count mismatch")
        if len(summary.get("methods", [])) != b10_t1_d5_b3_fci_table.get("method_count"):
            errors.append("B10-T1 D5 B3 FCI reference table method count mismatch")
        if len(payload.get("validation_errors", [])) != b10_t1_d5_b3_fci_table.get("validation_error_count"):
            errors.append("B10-T1 D5 B3 FCI reference table validation-error count mismatch")
        if payload.get("explicit_not_bqp_separation") is not True:
            errors.append("B10-T1 D5 B3 FCI reference table must explicitly avoid BQP separation claims")
        if summary.get("max_abs_fci_derivative_shift_vs_rhf", 0.0) <= 0.0:
            errors.append("B10-T1 D5 B3 FCI reference table has no nonzero FCI-vs-RHF derivative shift")

    b10_t1_b3_b5_comparison_status = {}
    if not b10_t1_b3_b5_comparison:
        warnings.append("B10 manifest has no B10-T1 B3/B5 denominator boundary comparison")
    else:
        result_path = b10_t1_b3_b5_comparison.get("result")
        markdown_path = b10_t1_b3_b5_comparison.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T1 B3/B5 denominator comparison result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T1 B3/B5 denominator comparison markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b10_t1_b3_b5_comparison_status = {
            "status": b10_t1_b3_b5_comparison.get("status"),
            "method": b10_t1_b3_b5_comparison.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "dependency_benchmarks": payload.get("dependency_benchmarks"),
            "route_count": summary.get("route_count"),
            "negative_boundary_route_count": summary.get("negative_boundary_route_count"),
            "b3_selected_ci_larger_basis_denominator_beaten_count": summary.get(
                "b3_selected_ci_larger_basis_denominator_beaten_count"
            ),
            "b3_max_optimizer_loop_total_shots_lower_bound": summary.get(
                "b3_max_optimizer_loop_total_shots_lower_bound"
            ),
            "b5_non_oracle_rows_beating_oracle_boundary_field": summary.get(
                "b5_non_oracle_rows_beating_oracle_boundary_field"
            ),
            "b5_seeded_mps_rows_beating_non_oracle_embedding": summary.get(
                "b5_seeded_mps_rows_beating_non_oracle_embedding"
            ),
            "b5_variational_mps_rows_beating_seeded_mps_pressure_reference": summary.get(
                "b5_variational_mps_rows_beating_seeded_mps_pressure_reference"
            ),
            "b3_demoted": summary.get("b3_demoted"),
            "b5_positive_claim_ready": summary.get("b5_positive_claim_ready"),
            "bqp_separation_claimed": summary.get("bqp_separation_claimed"),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "b3_b5_denominator_boundary_comparison_not_bqp_separation":
            errors.append("B10-T1 B3/B5 denominator comparison status must avoid BQP-separation claims")
        if payload.get("method") != b10_t1_b3_b5_comparison.get("method"):
            errors.append("B10-T1 B3/B5 denominator comparison method mismatch")
        if payload.get("source_target_id") != b10_t1_b3_b5_comparison.get("source_target_id"):
            errors.append("B10-T1 B3/B5 denominator comparison source target mismatch")
        if summary.get("route_count") != b10_t1_b3_b5_comparison.get("route_count"):
            errors.append("B10-T1 B3/B5 denominator comparison route count mismatch")
        for field in [
            "b3_selected_ci_larger_basis_denominator_beaten_count",
            "b3_max_optimizer_loop_total_shots_lower_bound",
            "b5_non_oracle_rows_beating_oracle_boundary_field",
            "b5_seeded_mps_rows_beating_non_oracle_embedding",
            "b5_variational_mps_rows_beating_seeded_mps_pressure_reference",
        ]:
            if summary.get(field) != b10_t1_b3_b5_comparison.get(field):
                errors.append(f"B10-T1 B3/B5 denominator comparison {field} mismatch")
        if summary.get("b3_demoted") is not True:
            errors.append("B10-T1 B3/B5 denominator comparison must keep B3 demoted")
        if summary.get("b5_positive_claim_ready") is not False:
            errors.append("B10-T1 B3/B5 denominator comparison must not mark B5 positive-ready")
        if summary.get("bqp_separation_claimed") is not False:
            errors.append("B10-T1 B3/B5 denominator comparison must not claim BQP separation")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B10-T1 B3/B5 denominator comparison must not claim quantum advantage")
        if len(payload.get("validation_errors", [])) != b10_t1_b3_b5_comparison.get("validation_error_count"):
            errors.append("B10-T1 B3/B5 denominator comparison validation-error count mismatch")
        claim_boundary = payload.get("claim_boundary", {})
        if claim_boundary.get("bqp_separation_claimed") is not False:
            errors.append("B10-T1 B3/B5 denominator comparison payload claims BQP separation")
        if claim_boundary.get("quantum_advantage_claimed") is not False:
            errors.append("B10-T1 B3/B5 denominator comparison payload claims quantum advantage")

    b10_t1_missing_assumption_note_status = {}
    if not b10_t1_missing_assumption_note:
        warnings.append("B10 manifest has no B10-T1 missing-assumption theorem note")
    else:
        result_path = b10_t1_missing_assumption_note.get("result")
        markdown_path = b10_t1_missing_assumption_note.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T1 missing-assumption note result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T1 missing-assumption note markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b10_t1_missing_assumption_note_status = {
            "status": b10_t1_missing_assumption_note.get("status"),
            "method": b10_t1_missing_assumption_note.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "dependency_benchmarks": payload.get("dependency_benchmarks"),
            "theorem_skeleton_count": summary.get("theorem_skeleton_count"),
            "missing_assumption_count": summary.get("missing_assumption_count"),
            "proof_obligation_count": summary.get("proof_obligation_count"),
            "source_route_count": summary.get("source_route_count"),
            "source_b3_demoted": summary.get("source_b3_demoted"),
            "source_b5_positive_claim_ready": summary.get("source_b5_positive_claim_ready"),
            "dequantization_theorem_proved": summary.get("dequantization_theorem_proved"),
            "sampling_access_theorem_proved": summary.get("sampling_access_theorem_proved"),
            "bqp_separation_claimed": summary.get("bqp_separation_claimed"),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "missing_assumption_note_not_dequantization_theorem":
            errors.append("B10-T1 missing-assumption note must not claim to be a dequantization theorem")
        if payload.get("method") != b10_t1_missing_assumption_note.get("method"):
            errors.append("B10-T1 missing-assumption note method mismatch")
        if payload.get("source_target_id") != b10_t1_missing_assumption_note.get("source_target_id"):
            errors.append("B10-T1 missing-assumption note source target mismatch")
        for field in [
            "theorem_skeleton_count",
            "missing_assumption_count",
            "proof_obligation_count",
            "source_route_count",
        ]:
            if summary.get(field) != b10_t1_missing_assumption_note.get(field):
                errors.append(f"B10-T1 missing-assumption note {field} mismatch")
        if summary.get("missing_assumption_count", 0) < 3:
            errors.append("B10-T1 missing-assumption note must expose at least three missing assumptions")
        if summary.get("dequantization_theorem_proved") is not False:
            errors.append("B10-T1 missing-assumption note must not claim a dequantization theorem")
        if summary.get("sampling_access_theorem_proved") is not False:
            errors.append("B10-T1 missing-assumption note must not claim a sampling-access theorem")
        if summary.get("bqp_separation_claimed") is not False:
            errors.append("B10-T1 missing-assumption note must not claim BQP separation")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B10-T1 missing-assumption note must not claim quantum advantage")
        if len(payload.get("validation_errors", [])) != b10_t1_missing_assumption_note.get("validation_error_count"):
            errors.append("B10-T1 missing-assumption note validation-error count mismatch")
        claim_boundary = payload.get("claim_boundary", {})
        if claim_boundary.get("dequantization_theorem_proved") is not False:
            errors.append("B10-T1 missing-assumption note payload claims dequantization theorem")
        if claim_boundary.get("bqp_separation_claimed") is not False:
            errors.append("B10-T1 missing-assumption note payload claims BQP separation")

    b10_t1_asymptotic_access_contract_status = {}
    if not b10_t1_asymptotic_access_contract:
        warnings.append("B10 manifest has no B10-T1 asymptotic access contract")
    else:
        result_path = b10_t1_asymptotic_access_contract.get("result")
        markdown_path = b10_t1_asymptotic_access_contract.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T1 asymptotic access contract result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T1 asymptotic access contract markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b10_t1_asymptotic_access_contract_status = {
            "status": b10_t1_asymptotic_access_contract.get("status"),
            "method": b10_t1_asymptotic_access_contract.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "dependency_benchmarks": payload.get("dependency_benchmarks"),
            "family_contract_count": summary.get("family_contract_count"),
            "access_contract_count": summary.get("access_contract_count"),
            "bridge_condition_count": summary.get("bridge_condition_count"),
            "theorem_target_count": summary.get("theorem_target_count"),
            "sampling_access_bridge_proved": summary.get("sampling_access_bridge_proved"),
            "sampling_access_bridge_refuted_for_current_evidence": summary.get(
                "sampling_access_bridge_refuted_for_current_evidence"
            ),
            "general_dequantization_theorem_proved": summary.get("general_dequantization_theorem_proved"),
            "general_sampling_access_theorem_proved": summary.get("general_sampling_access_theorem_proved"),
            "bqp_separation_claimed": summary.get("bqp_separation_claimed"),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "b3_demoted": summary.get("b3_demoted"),
            "b5_positive_claim_ready": summary.get("b5_positive_claim_ready"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "access_contract_skeleton_sampling_bridge_refuted_for_current_evidence":
            errors.append("B10-T1 asymptotic access contract must remain a current-evidence bridge refutation")
        if payload.get("method") != b10_t1_asymptotic_access_contract.get("method"):
            errors.append("B10-T1 asymptotic access contract method mismatch")
        if payload.get("source_target_id") != b10_t1_asymptotic_access_contract.get("source_target_id"):
            errors.append("B10-T1 asymptotic access contract source target mismatch")
        for field in [
            "family_contract_count",
            "access_contract_count",
            "bridge_condition_count",
            "theorem_target_count",
        ]:
            if summary.get(field) != b10_t1_asymptotic_access_contract.get(field):
                errors.append(f"B10-T1 asymptotic access contract {field} mismatch")
        if summary.get("family_contract_count", 0) < 2:
            errors.append("B10-T1 asymptotic access contract must cover B3 and B5 families")
        if summary.get("access_contract_count", 0) < 8:
            errors.append("B10-T1 asymptotic access contract must cover explicit/oracle/sampling/quantum access for both families")
        if summary.get("sampling_access_bridge_proved") is not False:
            errors.append("B10-T1 asymptotic access contract must not claim a sampling-access bridge proof")
        if summary.get("sampling_access_bridge_refuted_for_current_evidence") is not True:
            errors.append("B10-T1 asymptotic access contract must refute the current sampling bridge")
        if summary.get("general_dequantization_theorem_proved") is not False:
            errors.append("B10-T1 asymptotic access contract must not claim a general dequantization theorem")
        if summary.get("general_sampling_access_theorem_proved") is not False:
            errors.append("B10-T1 asymptotic access contract must not claim a general sampling-access theorem")
        if summary.get("bqp_separation_claimed") is not False:
            errors.append("B10-T1 asymptotic access contract must not claim BQP separation")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B10-T1 asymptotic access contract must not claim quantum advantage")
        if summary.get("b3_demoted") is not True:
            errors.append("B10-T1 asymptotic access contract must keep B3 demoted")
        if summary.get("b5_positive_claim_ready") is not False:
            errors.append("B10-T1 asymptotic access contract must not mark B5 positive-ready")
        if len(payload.get("validation_errors", [])) != b10_t1_asymptotic_access_contract.get("validation_error_count"):
            errors.append("B10-T1 asymptotic access contract validation-error count mismatch")
        claim_boundary = payload.get("claim_boundary", {})
        if claim_boundary.get("general_dequantization_theorem_proved") is not False:
            errors.append("B10-T1 asymptotic access contract payload claims general dequantization theorem")
        if claim_boundary.get("bqp_separation_claimed") is not False:
            errors.append("B10-T1 asymptotic access contract payload claims BQP separation")

    b10_t1_b5_same_access_bridge_status = {}
    if not b10_t1_b5_same_access_bridge:
        warnings.append("B10 manifest has no B10-T1 B5 same-access sampling-or-DMRG bridge")
    else:
        result_path = b10_t1_b5_same_access_bridge.get("result")
        markdown_path = b10_t1_b5_same_access_bridge.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T1 B5 same-access bridge result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T1 B5 same-access bridge markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        b10_t1_b5_same_access_bridge_status = {
            "status": b10_t1_b5_same_access_bridge.get("status"),
            "method": b10_t1_b5_same_access_bridge.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "dependency_benchmarks": payload.get("dependency_benchmarks"),
            "denominator_ladder_count": summary.get("denominator_ladder_count"),
            "sampling_requirement_count": summary.get("sampling_requirement_count"),
            "blocking_sampling_requirement_count": summary.get("blocking_sampling_requirement_count"),
            "bridge_decision_count": summary.get("bridge_decision_count"),
            "b5_instance_count": summary.get("b5_instance_count"),
            "max_exact_d5_hilbert_dimension": summary.get("max_exact_d5_hilbert_dimension"),
            "seeded_mps_rows_beating_non_oracle_embedding": summary.get("seeded_mps_rows_beating_non_oracle_embedding"),
            "variational_mps_rows_beating_seeded_pressure": summary.get(
                "variational_mps_rows_beating_seeded_pressure"
            ),
            "sampling_oracle_constructed": summary.get("sampling_oracle_constructed"),
            "production_dmrg_available": summary.get("production_dmrg_available"),
            "same_access_positive_route_ready": summary.get("same_access_positive_route_ready"),
            "general_dequantization_theorem_proved": summary.get("general_dequantization_theorem_proved"),
            "sampling_access_theorem_proved": summary.get("sampling_access_theorem_proved"),
            "bqp_separation_claimed": summary.get("bqp_separation_claimed"),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != "b5_same_access_sampling_oracle_not_constructed_dmrg_required":
            errors.append("B10-T1 B5 same-access bridge status mismatch")
        if payload.get("method") != b10_t1_b5_same_access_bridge.get("method"):
            errors.append("B10-T1 B5 same-access bridge method mismatch")
        if payload.get("source_target_id") != b10_t1_b5_same_access_bridge.get("source_target_id"):
            errors.append("B10-T1 B5 same-access bridge source target mismatch")
        for field in [
            "denominator_ladder_count",
            "sampling_requirement_count",
            "blocking_sampling_requirement_count",
            "bridge_decision_count",
            "b5_instance_count",
            "max_exact_d5_hilbert_dimension",
            "seeded_mps_rows_beating_non_oracle_embedding",
            "variational_mps_rows_beating_seeded_pressure",
        ]:
            if summary.get(field) != b10_t1_b5_same_access_bridge.get(field):
                errors.append(f"B10-T1 B5 same-access bridge {field} mismatch")
        if summary.get("denominator_ladder_count", 0) < 4:
            errors.append("B10-T1 B5 same-access bridge must include at least four denominator ladder rows")
        if summary.get("blocking_sampling_requirement_count") != summary.get("sampling_requirement_count"):
            errors.append("B10-T1 B5 same-access bridge must keep every sampling requirement blocking")
        if summary.get("sampling_oracle_constructed") is not False:
            errors.append("B10-T1 B5 same-access bridge must not claim a sampling oracle")
        if summary.get("production_dmrg_available") is not False:
            errors.append("B10-T1 B5 same-access bridge must not claim production DMRG")
        if summary.get("same_access_positive_route_ready") is not False:
            errors.append("B10-T1 B5 same-access bridge must not claim a positive same-access route")
        if summary.get("general_dequantization_theorem_proved") is not False:
            errors.append("B10-T1 B5 same-access bridge must not claim a general dequantization theorem")
        if summary.get("sampling_access_theorem_proved") is not False:
            errors.append("B10-T1 B5 same-access bridge must not claim a sampling-access theorem")
        if summary.get("bqp_separation_claimed") is not False:
            errors.append("B10-T1 B5 same-access bridge must not claim BQP separation")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B10-T1 B5 same-access bridge must not claim quantum advantage")
        if len(payload.get("validation_errors", [])) != b10_t1_b5_same_access_bridge.get("validation_error_count"):
            errors.append("B10-T1 B5 same-access bridge validation-error count mismatch")
        claim_boundary = payload.get("claim_boundary", {})
        if claim_boundary.get("same_access_positive_route_ready") is not False:
            errors.append("B10-T1 B5 same-access bridge payload claims a positive route")
        if claim_boundary.get("bqp_separation_claimed") is not False:
            errors.append("B10-T1 B5 same-access bridge payload claims BQP separation")

    b10_t1_b5_response_sampler_stress_status = {}
    if not b10_t1_b5_response_sampler_stress:
        warnings.append("B10 manifest has no B10-T1 B5 response sampler cost stress")
    else:
        result_path = b10_t1_b5_response_sampler_stress.get("result")
        markdown_path = b10_t1_b5_response_sampler_stress.get("markdown_report")
        result_exists = bool(result_path and path_exists_from(benchmarks, result_path))
        markdown_exists = bool(markdown_path and path_exists_from(benchmarks, markdown_path))
        if not result_exists:
            errors.append(f"B10-T1 B5 response sampler stress result path missing: {result_path}")
        if not markdown_exists:
            errors.append(f"B10-T1 B5 response sampler stress markdown path missing: {markdown_path}")
        payload = json.loads(read((benchmarks / result_path).resolve())) if result_exists else {}
        summary = payload.get("summary", {})
        claims = payload.get("claim_boundary", {})
        b10_t1_b5_response_sampler_stress_status = {
            "status": b10_t1_b5_response_sampler_stress.get("status"),
            "method": b10_t1_b5_response_sampler_stress.get("method"),
            "source_target_id": payload.get("source_target_id"),
            "sampling_model": payload.get("sampling_model", {}).get("name"),
            "instance_count": summary.get("instance_count"),
            "confidence_z": summary.get("confidence_z"),
            "max_exact_d5_hilbert_dimension": summary.get("max_exact_d5_hilbert_dimension"),
            "max_exact_d5_matvec_equivalent_ops": summary.get("max_exact_d5_matvec_equivalent_ops"),
            "min_total_shots_to_match_seeded_mps_pressure": summary.get(
                "min_total_shots_to_match_seeded_mps_pressure"
            ),
            "median_total_shots_to_match_seeded_mps_pressure": summary.get(
                "median_total_shots_to_match_seeded_mps_pressure"
            ),
            "max_total_shots_to_match_seeded_mps_pressure": summary.get(
                "max_total_shots_to_match_seeded_mps_pressure"
            ),
            "max_optimistic_seeded_target_prep_2q_gate_floor": summary.get(
                "max_optimistic_seeded_target_prep_2q_gate_floor"
            ),
            "rows_where_sampler_shots_beat_explicit_d5_matvec_ops_for_seeded_target": summary.get(
                "rows_where_sampler_shots_beat_explicit_d5_matvec_ops_for_seeded_target"
            ),
            "sampling_oracle_constructed": summary.get("sampling_oracle_constructed"),
            "same_access_positive_route_ready": summary.get("same_access_positive_route_ready"),
            "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
            "bqp_separation_claimed": summary.get("bqp_separation_claimed"),
            "production_dmrg_available": claims.get("production_dmrg_available"),
            "validation_error_count": len(payload.get("validation_errors", [])),
            "result_exists": result_exists,
            "markdown_exists": markdown_exists,
            "result": result_path,
            "markdown_report": markdown_path,
        }
        if payload.get("status") != b10_t1_b5_response_sampler_stress.get("status"):
            errors.append("B10-T1 B5 response sampler stress status mismatch")
        if payload.get("method") != b10_t1_b5_response_sampler_stress.get("method"):
            errors.append("B10-T1 B5 response sampler stress method mismatch")
        if payload.get("source_target_id") != b10_t1_b5_response_sampler_stress.get("source_target_id"):
            errors.append("B10-T1 B5 response sampler stress source target mismatch")
        for field in [
            "instance_count",
            "confidence_z",
            "max_exact_d5_hilbert_dimension",
            "max_exact_d5_matvec_equivalent_ops",
            "min_total_shots_to_match_seeded_mps_pressure",
            "median_total_shots_to_match_seeded_mps_pressure",
            "max_total_shots_to_match_seeded_mps_pressure",
            "max_optimistic_seeded_target_prep_2q_gate_floor",
            "rows_where_sampler_shots_beat_explicit_d5_matvec_ops_for_seeded_target",
        ]:
            if summary.get(field) != b10_t1_b5_response_sampler_stress.get(field):
                errors.append(f"B10-T1 B5 response sampler stress {field} mismatch")
        if summary.get("instance_count") != 9:
            errors.append("B10-T1 B5 response sampler stress must cover nine B5 rows")
        if summary.get("rows_where_sampler_shots_beat_explicit_d5_matvec_ops_for_seeded_target") != 0:
            errors.append("B10-T1 B5 response sampler stress must not beat seeded target by shots")
        if summary.get("sampling_oracle_constructed") is not False:
            errors.append("B10-T1 B5 response sampler stress must not claim a sampling oracle")
        if summary.get("same_access_positive_route_ready") is not False:
            errors.append("B10-T1 B5 response sampler stress must not claim a same-access positive route")
        if summary.get("quantum_advantage_claimed") is not False:
            errors.append("B10-T1 B5 response sampler stress must not claim quantum advantage")
        if summary.get("bqp_separation_claimed") is not False:
            errors.append("B10-T1 B5 response sampler stress must not claim BQP separation")
        if claims.get("production_dmrg_available") is not False:
            errors.append("B10-T1 B5 response sampler stress must not claim production DMRG")
        if len(payload.get("validation_errors", [])) != b10_t1_b5_response_sampler_stress.get(
            "validation_error_count"
        ):
            errors.append("B10-T1 B5 response sampler stress validation-error count mismatch")

    for path in [roadmap_path, status_html_path]:
        if not path.exists():
            errors.append(f"missing status artifact: {path}")

    if "local semantic checks" not in read(roadmap_path):
        warnings.append("roadmap does not mention local semantic checks")
    if "semantic check" not in read(status_html_path):
        warnings.append("status HTML does not mention semantic check")

    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "catalog": {
            "path": str(catalog_path),
            "json_path": str(catalog_json_path),
            "problem_count": len(catalog),
            "ids_are_contiguous_1_to_100": catalog_ids == expected_ids,
            "metadata_matrix_count": len(catalog_metadata_rows),
            "metadata_matrix_ids_are_contiguous_1_to_100": catalog_metadata_ids == expected_ids,
            "metadata_complete": not incomplete_catalog_metadata,
            "json_record_count": catalog_json.get("record_count"),
            "json_status": catalog_json.get("status"),
            "json_freeze_lock": catalog_json.get("freeze_lock"),
            "user_freeze_directive_date": catalog_json.get("user_freeze_directive_date"),
            "user_freeze_directive_present": bool(catalog_json.get("user_freeze_directive")),
            "metadata_completion_scope": sorted(catalog_json.get("metadata_completion_scope", [])),
            "source_confidence_labels": sorted(catalog_json.get("source_confidence_labels", {}).keys()),
            "discipline_supergroup_count": len(catalog_json.get("discipline_supergroups", [])),
            "source_lineage_group_count": len(catalog_json.get("source_lineage_groups", {})),
            "non_revision_covenant_present": bool(catalog_json.get("non_revision_covenant")),
            "json_per_record_discipline_source_complete": not incomplete_json_records,
            "json_per_record_discipline_supergroups": sorted(observed_json_supergroups),
            "json_per_record_source_lineage_groups": sorted(observed_json_source_groups),
        },
        "top20": {
            "scoring_path": str(scoring_path),
            "evidence_path": str(evidence_path),
            "ids": scoring_top20_ids,
            "evidence_matches_scoring": evidence_top20_ids == scoring_top20_ids,
        },
        "attack_pack": {
            "path": str(attack_path),
            "ids": attack_ids,
            "matches_tier1_top10": attack_ids == expected_tier1,
        },
        "execution_board": execution_summary,
        "problem_dossiers": dossier_summary,
        "technical_resolution_program": technical_resolution_summary,
        "translation_pipeline": translation_summary,
        "b1": {
            "manifest": str(b1_manifest_path),
            "verification": b1_verification,
            "certificate_report": b1_certificate_report,
            "routing_diagnostic": b1_routing_diagnostic,
            "heavyhex_diagnostic": b1_heavyhex_diagnostic,
            "heavyhex_end_to_end": b1_heavyhex_e2e,
            "heavyhex_end_to_end_suite": b1_heavyhex_e2e_suite,
            "post_routing_bottleneck_profile": b1_post_routing_profile,
            "post_routing_swap_macro": b1_swap_macro,
            "virtual_swap_elimination": b1_virtual_swap,
            "post_virtual_swap_1q_resynthesis": b1_post_virtual_swap_1q,
            "native_t_resource_optimizer": b1_native_t_resource,
            "control_rz_commute_optimizer": b1_control_rz_commute,
            "u3_phase_factored_optimizer": b1_u3_phase_factored,
            "b7_gcm_h6_target_selector": b1_b7_gcm_h6_target_selector,
            "b7_gcm_h6_cone_feasibility_gate": b1_b7_gcm_h6_cone_feasibility,
            "b7_cone01_phase_removal_gate": b1_b7_cone01_phase_removal,
            "b7_cone01_euler_reabsorption_gate": b1_b7_cone01_euler_reabsorption,
            "b7_cone01_parameter_transfer_gate": b1_b7_cone01_parameter_transfer,
            "b7_cone01_theta_sharing_ledger_gate": b1_b7_cone01_theta_sharing,
            "b7_cone01_shared_theta_synthesis_object_gate": b1_b7_cone01_shared_theta_synthesis_object,
            "b7_cone01_shared_theta_replay_verifier_gate": b1_b7_cone01_shared_theta_replay_verifier,
            "b7_cone01_shared_theta_layout_routing_gate": b1_b7_cone01_shared_theta_layout_routing,
            "b7_cone01_shared_theta_factory_amortization_gate": b1_b7_cone01_shared_theta_factory_amortization,
            "b7_cone01_shared_theta_error_budget_gate": b1_b7_cone01_shared_theta_error_budget,
            "b7_cone01_theta_sharing_cost_model_gate": b1_b7_cone01_theta_sharing_cost_model,
            "synthetic_noise_proxy": b1_synthetic_noise,
        },
        "b2": {
            "manifest": str(b2_manifest_path),
            "baseline": b2_status,
            "target_volume": b2_target_status,
            "surface_code_estimate": b2_surface_status,
            "phenomenological_decoder": b2_decoder_status,
            "stim_surface_code_baseline": b2_stim_surface_status,
            "stim_surface_code_target_volume": b2_stim_target_status,
            "biased_schedule_proxy": b2_biased_schedule_status,
            "stim_biased_schedule_sweep": b2_stim_biased_schedule_status,
            "same_hardware_schedule_candidate": b2_same_hardware_status,
            "same_hardware_schedule_robustness": b2_same_hardware_robustness_status,
            "reduced_round_artifact_boundary": b2_reduced_round_boundary_status,
            "leakage_flagged_erasure_boundary": b2_leakage_flagged_erasure_status,
            "stim_heralded_erasure_stress": b2_stim_heralded_erasure_status,
            "heralded_erasure_false_positive_stress": b2_false_positive_erasure_status,
            "shot_conditioned_erasure_decoder_boundary": b2_shot_conditioned_erasure_status,
            "posterior_weighted_decoder_risk_ledger": b2_posterior_risk_ledger_status,
            "decoder_input_contract_feasibility_gate": b2_decoder_input_contract_status,
            "per_shot_decoder_trace_packet": b2_per_shot_trace_packet_status,
            "posterior_likelihood_decoder_injection_gate": b2_posterior_injection_gate_status,
            "dem_informed_detector_edge_semantics_gate": b2_dem_edge_semantics_gate_status,
            "hardware_like_leakage_model_gate": b2_hardware_like_leakage_gate_status,
        },
        "b3": {
            "manifest": str(b3_manifest_path),
            "resource_proxy": b3_status,
            "quantum_observable_fci_comparison": b3_quantum_observable_fci_status,
            "hamiltonian_pauli_mapper_comparison": b3_hamiltonian_pauli_mapper_status,
            "sampled_pauli_estimator_confidence": b3_sampled_pauli_confidence_status,
            "selected_ci_grouped_pauli_boundary": b3_selected_ci_grouped_pauli_status,
            "larger_basis_hamiltonian_mapper": b3_larger_basis_hamiltonian_mapper_status,
            "larger_basis_qwc_grouping": b3_larger_basis_qwc_grouping_status,
            "grouped_covariance_shot_floor": b3_grouped_covariance_shot_floor_status,
            "chemical_state_prep_derivative_boundary": b3_chemical_state_prep_derivative_status,
            "compiled_ucc_adapt_covariance_pilot": b3_compiled_ucc_adapt_covariance_status,
            "cross_molecule_ucc_adapt_pressure": b3_cross_molecule_ucc_adapt_pressure_status,
        },
        "b4": {
            "manifest": str(b4_manifest_path),
            "trap_protocol": b4_status,
            "circuit_refresh_task": b4_circuit_refresh_status,
            "openqasm3_randomized_measurement_packet": b4_openqasm3_packet_status,
            "public_qasm_packet_spoofer_gate": b4_public_qasm_spoofer_status,
            "late_bound_private_challenge_contract_gate": b4_late_bound_contract_status,
            "nonstabilizer_late_bound_transcript_pilot": b4_nonstabilizer_pilot_status,
            "nonstabilizer_support_spoofer_gate": b4_support_spoofer_status,
        },
        "b5": {
            "manifest": str(b5_manifest_path),
            "hubbard_embedding": b5_status,
            "same_access_production_contract_gate": b5_b10_production_contract_status,
            "canonical_environment_smoke_gate": b5_canonical_smoke_status,
            "canonical_dmrg_readiness_gate": b5_dmrg_readiness_status,
            "two_site_finite_dmrg_response_reference": b5_two_site_dmrg_status,
            "variational_mps_als_response_reference": b5_var_mps_status,
            "mps_truncation_response_reference": b5_mps_status,
            "non_oracle_response_embedding": b5_non_oracle_status,
            "boundary_field_response_embedding": b5_boundary_field_status,
        },
        "b6": {
            "manifest": str(b6_manifest_path),
            "descriptor_ranking": b6_status,
            "curated_materials_leakage_audit": b6_curated_status,
            "formula_descriptor_screen": b6_formula_status,
            "structural_electronic_proxy_screen": b6_structural_status,
        },
        "b7": {
            "manifest": str(b7_manifest_path),
            "fault_tolerance_codesign": b7_status,
            "dependency_schedule_bridge": b7_bridge_status,
            "workload_dag_factory_schedule": b7_workload_dag_status,
            "logical_t_factory_schedule": b7_logical_t_status,
            "logical_t_factory_schedule_post_1q": b7_logical_t_post_1q_status,
            "logical_t_factory_schedule_native": b7_logical_t_native_status,
            "logical_t_factory_schedule_control_rz": b7_logical_t_control_rz_status,
            "logical_t_factory_schedule_u3_phase_factored": b7_logical_t_u3_phase_factored_status,
            "min_stv_regime_classifier": b7_min_stv_classifier_status,
            "ft_synthesis_ledger": b7_ft_synthesis_ledger_status,
            "gcm_h6_ft_boundary": b7_gcm_h6_boundary_status,
            "precision_aware_rotation_ledger": b7_precision_rotation_status,
            "gcm_h6_numeric_rotation_structure": b7_gcm_h6_numeric_structure_status,
            "shared_synthesis_cache_boundary": b7_shared_synthesis_cache_status,
            "nonlocal_template_block_scan": b7_nonlocal_template_status,
            "template_priority_gate": b7_template_priority_status,
            "w8_21_small_block_synthesis": b7_w8_21_synthesis_status,
            "w8_21_broad_skeleton_search": b7_w8_21_broad_search_status,
            "w8_21_euler_local_search": b7_w8_21_euler_local_status,
            "w8_21_three_cnot_search": b7_w8_21_three_cnot_status,
            "w8_21_scoped_minimality_note": b7_w8_21_minimality_note_status,
            "w8_21_claim_boundary_fragment": b7_w8_21_claim_boundary_status,
        },
        "b8": {
            "manifest": str(b8_manifest_path),
            "output_invariant_verifier": b8_status,
            "adaptive_leakage_spoofer": b8_adaptive_status,
            "challenge_refresh_repair": b8_refresh_status,
            "circuit_refresh_task": b8_circuit_refresh_status,
            "openqasm3_randomized_measurement_packet": b8_openqasm3_packet_status,
            "public_qasm_packet_spoofer_gate": b8_public_qasm_spoofer_status,
            "late_bound_private_challenge_contract_gate": b8_late_bound_contract_status,
            "nonstabilizer_late_bound_transcript_pilot": b8_nonstabilizer_pilot_status,
            "nonstabilizer_support_spoofer_gate": b8_support_spoofer_status,
            "generative_spoofer_refresh": b8_generative_spoofer_status,
        },
        "b9": {
            "manifest": str(b9_manifest_path),
            "local_hamiltonian_gap_lab": b9_status,
            "failed_gap_amplification_lemma": b9_failed_gap_lemma_status,
            "symbolic_gap_skeleton": b9_symbolic_gap_skeleton_status,
            "named_family_width_locality_bound": b9_named_family_bound_status,
            "cluster_stabilizer_parametric_certificate": b9_parametric_certificate_status,
        },
        "b10": {
            "manifest": str(b10_manifest_path),
            "bqp_boundary_graph": b10_status,
            "formal_theorem_targets": b10_formal_target_status,
            "t2_minimum_refresh_spoofer_boundary": b10_t2_refresh_boundary_status,
            "t2_refresh_proof_obligation_gate": b10_t2_proof_gate_status,
            "t2_restricted_soundness_lemma": b10_t2_restricted_lemma_status,
            "t2_transcript_leakage_simulator": b10_t2_transcript_simulator_status,
            "t2_device_noise_transcript_bridge": b10_t2_device_noise_bridge_status,
            "t2_qiskit_aer_verifier_bridge": b10_t2_qiskit_aer_bridge_status,
            "t2_noisy_aer_verifier_bridge": b10_t2_noisy_aer_bridge_status,
            "t2_backend_calibrated_verifier_bridge": b10_t2_backend_calibrated_bridge_status,
            "t1_negative_boundary_proof": b10_t1_proof_status,
            "t1_source_backed_boundaries": b10_t1_source_backed_status,
            "t1_numerical_denominator_table": b10_t1_numerical_table_status,
            "t1_d5_observable_denominator_table": b10_t1_d5_table_status,
            "t1_d5_b3_molecular_observable_table": b10_t1_d5_b3_table_status,
            "t1_d5_b3_reaction_observable_table": b10_t1_d5_b3_reaction_table_status,
            "t1_d5_b3_correlated_reference_table": b10_t1_d5_b3_correlated_table_status,
            "t1_d5_b3_fci_reference_table": b10_t1_d5_b3_fci_table_status,
            "t1_b3_b5_denominator_boundary_comparison": b10_t1_b3_b5_comparison_status,
            "t1_missing_assumption_note": b10_t1_missing_assumption_note_status,
            "t1_asymptotic_access_contract": b10_t1_asymptotic_access_contract_status,
            "t1_b5_same_access_sampling_or_dmrg_bridge": b10_t1_b5_same_access_bridge_status,
            "t1_b5_response_sampler_cost_stress": b10_t1_b5_response_sampler_stress_status,
        },
        "status_artifacts": {
            "roadmap": str(roadmap_path),
            "status_html": str(status_html_path),
            "execution_board": str(execution_board_path),
            "top10_problem_dossiers_json": str(dossier_path),
            "top10_problem_dossiers_markdown": str(dossier_markdown_path),
            "technical_resolution_program_json": str(technical_resolution_path),
            "technical_resolution_program_markdown": str(technical_resolution_markdown_path),
            "translation_pipeline_json": str(translation_path),
            "translation_pipeline_markdown": str(translation_markdown_path),
            "b1_certificate_report": str(b1_certificate_report_path),
            "b1_routing_diagnostic": str(b1_routing_diagnostic_path),
            "b1_heavyhex_diagnostic": str(b1_heavyhex_diagnostic_path),
            "b1_heavyhex_end_to_end": str(b1_heavyhex_e2e_path),
            "b1_heavyhex_end_to_end_suite": str(b1_heavyhex_e2e_suite_path),
            "b1_post_routing_bottleneck_profile": str(b1_post_routing_profile_path),
            "b1_post_routing_swap_macro": str(b1_swap_macro_path),
            "b1_virtual_swap_elimination": str(b1_virtual_swap_path),
            "b1_virtual_swap_replay": str(b1_virtual_swap_replay_path),
            "b1_post_virtual_swap_1q_resynthesis": str(b1_post_virtual_swap_1q_path),
            "b1_native_t_resource_optimizer": str(b1_native_t_resource_path),
            "b1_control_rz_commute_optimizer": str(b1_control_rz_commute_path),
            "b1_u3_phase_factored_optimizer": str(b1_u3_phase_factored_path),
            "b1_b7_gcm_h6_target_selector": str(b1_b7_gcm_h6_target_selector_path),
            "b1_b7_gcm_h6_cone_feasibility_gate": str(b1_b7_gcm_h6_cone_feasibility_path),
            "b1_b7_cone01_phase_removal_gate": str(b1_b7_cone01_phase_removal_path),
            "b1_b7_cone01_euler_reabsorption_gate": str(b1_b7_cone01_euler_reabsorption_path),
            "b1_b7_cone01_parameter_transfer_gate": str(b1_b7_cone01_parameter_transfer_path),
            "b1_b7_cone01_theta_sharing_ledger_gate": str(b1_b7_cone01_theta_sharing_path),
            "b1_b7_cone01_shared_theta_synthesis_object_gate": str(
                b1_b7_cone01_shared_theta_synthesis_object_path
            ),
            "b1_b7_cone01_shared_theta_replay_verifier_gate": str(
                b1_b7_cone01_shared_theta_replay_verifier_path
            ),
            "b1_b7_cone01_shared_theta_layout_routing_gate": str(
                b1_b7_cone01_shared_theta_layout_routing_path
            ),
            "b1_b7_cone01_shared_theta_factory_amortization_gate": str(
                b1_b7_cone01_shared_theta_factory_amortization_path
            ),
            "b1_b7_cone01_shared_theta_error_budget_gate": str(
                b1_b7_cone01_shared_theta_error_budget_path
            ),
            "b1_b7_cone01_theta_sharing_cost_model_gate": str(
                b1_b7_cone01_theta_sharing_cost_model_path
            ),
            "b1_synthetic_noise_proxy": str(b1_synthetic_noise_path),
            "b2_phenomenological_decoder": str(research / "B2_phenomenological_repetition_decoder.md"),
            "b2_stim_surface_code_baseline": str(research / "B2_stim_surface_code_memory_baseline.md"),
            "b2_stim_surface_code_target_volume": str(research / "B2_stim_surface_code_target_volume.md"),
            "b2_biased_schedule_proxy": str(research / "B2_biased_schedule_proxy.md"),
            "b2_stim_biased_schedule_sweep": str(research / "B2_stim_biased_schedule_sweep.md"),
            "b2_same_hardware_schedule_candidate": str(research / "B2_same_hardware_schedule_candidate.md"),
            "b2_same_hardware_schedule_robustness": str(research / "B2_same_hardware_schedule_robustness.md"),
            "b2_reduced_round_artifact_boundary": str(research / "B2_reduced_round_artifact_boundary.md"),
            "b2_leakage_flagged_erasure_boundary": str(research / "B2_leakage_flagged_erasure_boundary.md"),
            "b2_stim_heralded_erasure_stress": str(research / "B2_stim_heralded_erasure_stress.md"),
            "b2_heralded_erasure_false_positive_stress": str(
                research / "B2_heralded_erasure_false_positive_stress.md"
            ),
            "b2_shot_conditioned_erasure_decoder_boundary": str(
                research / "B2_shot_conditioned_erasure_decoder_boundary.md"
            ),
            "b2_posterior_weighted_decoder_risk_ledger": str(
                research / "B2_posterior_weighted_decoder_risk_ledger.md"
            ),
            "b2_decoder_input_contract_feasibility_gate": str(
                research / "B2_decoder_input_contract_feasibility_gate.md"
            ),
            "b2_per_shot_decoder_trace_packet": str(
                research / "B2_per_shot_decoder_trace_packet.md"
            ),
            "b2_posterior_likelihood_decoder_injection_gate": str(
                research / "B2_posterior_likelihood_decoder_injection_gate.md"
            ),
            "b2_dem_informed_detector_edge_semantics_gate": str(
                research / "B2_dem_informed_detector_edge_semantics_gate.md"
            ),
            "b2_hardware_like_leakage_model_gate": str(
                research / "B2_hardware_like_leakage_model_gate.md"
            ),
            "b3_quantum_observable_fci_comparison": str(research / "B3_quantum_observable_fci_comparison.md"),
            "b3_quantum_observable_fci_qasm_directory": str(
                results / "b3_quantum_observable_fci_comparison" / "circuits"
            ),
            "b3_hamiltonian_pauli_mapper_comparison": str(
                research / "B3_hamiltonian_pauli_mapper_comparison.md"
            ),
            "b3_hamiltonian_pauli_mapper_qasm_directory": str(
                results / "b3_hamiltonian_pauli_mapper_comparison" / "circuits"
            ),
            "b3_sampled_pauli_estimator_confidence": str(
                research / "B3_sampled_pauli_estimator_confidence.md"
            ),
            "b3_selected_ci_grouped_pauli_boundary": str(
                research / "B3_selected_ci_grouped_pauli_boundary.md"
            ),
            "b3_larger_basis_hamiltonian_mapper": str(
                research / "B3_larger_basis_hamiltonian_mapper.md"
            ),
            "b3_larger_basis_qwc_grouping": str(
                research / "B3_larger_basis_qwc_grouping.md"
            ),
            "b3_grouped_covariance_shot_floor": str(
                research / "B3_grouped_covariance_shot_floor.md"
            ),
            "b3_chemical_state_prep_derivative_boundary": str(
                research / "B3_chemical_state_prep_derivative_boundary.md"
            ),
            "b3_compiled_ucc_adapt_covariance_pilot": str(
                research / "B3_compiled_ucc_adapt_covariance_pilot.md"
            ),
            "b3_cross_molecule_ucc_adapt_pressure": str(
                research / "B3_cross_molecule_ucc_adapt_pressure.md"
            ),
            "b5_boundary_field_embedding_baseline": str(
                research / "B5_boundary_field_embedding_baseline.md"
            ),
            "b5_non_oracle_response_embedding_baseline": str(
                research / "B5_non_oracle_response_embedding_baseline.md"
            ),
            "b5_mps_truncation_response_reference": str(
                research / "B5_mps_truncation_response_reference.md"
            ),
            "b5_two_site_dmrg_response_reference": str(
                research / "B5_two_site_dmrg_response_reference.md"
            ),
            "b5_variational_mps_als_response_reference": str(
                research / "B5_variational_mps_als_response_reference.md"
            ),
            "b5_canonical_dmrg_readiness_gate": str(
                research / "B5_canonical_dmrg_readiness_gate.md"
            ),
            "b5_b10_same_access_production_contract_gate": str(
                research / "B5_B10_same_access_production_contract_gate.md"
            ),
            "b5_canonical_environment_smoke_gate": str(
                research / "B5_canonical_environment_smoke_gate.md"
            ),
            "b6_curated_materials_leakage_audit": str(research / "B6_curated_materials_leakage_audit.md"),
            "b6_formula_descriptor_screen": str(research / "B6_formula_descriptor_screen.md"),
            "b6_structural_electronic_proxy_screen": str(
                research / "B6_structural_electronic_proxy_screen.md"
            ),
            "b10_formal_theorem_targets": str(research / "B10_formal_theorem_targets.md"),
            "b10_t2_minimum_refresh_spoofer_boundary": str(research / "B8_generative_spoofer_refresh.md"),
            "b10_t2_refresh_proof_obligation_gate": str(research / "B10_t2_refresh_proof_obligation_gate.md"),
            "b10_t2_restricted_soundness_lemma": str(research / "B10_t2_restricted_soundness_lemma.md"),
            "b10_t2_transcript_leakage_simulator": str(research / "B10_t2_transcript_leakage_simulator.md"),
            "b10_t2_device_noise_transcript_bridge": str(research / "B10_t2_device_noise_transcript_bridge.md"),
            "b10_t2_qiskit_aer_verifier_bridge": str(research / "B10_t2_qiskit_aer_verifier_bridge.md"),
            "b10_t2_noisy_aer_verifier_bridge": str(research / "B10_t2_noisy_aer_verifier_bridge.md"),
            "b10_t2_backend_calibrated_verifier_bridge": str(
                research / "B10_t2_backend_calibrated_verifier_bridge.md"
            ),
            "b10_t1_negative_boundary_proof": str(research / "B10_t1_negative_boundary_proof.md"),
            "b10_t1_source_backed_boundaries": str(research / "B10_t1_source_backed_boundaries.md"),
            "b10_t1_numerical_denominator_table": str(research / "B10_t1_numerical_denominator_table.md"),
            "b10_t1_d5_observable_denominator_table": str(research / "B10_t1_d5_observable_denominator_table.md"),
            "b10_t1_d5_b3_molecular_observable_table": str(research / "B10_t1_d5_b3_molecular_observable_table.md"),
            "b10_t1_d5_b3_reaction_observable_table": str(research / "B10_t1_d5_b3_reaction_observable_table.md"),
            "b10_t1_d5_b3_correlated_reference_table": str(research / "B10_t1_d5_b3_correlated_reference_table.md"),
            "b10_t1_d5_b3_fci_reference_table": str(research / "B10_t1_d5_b3_fci_reference_table.md"),
            "b10_t1_b3_b5_denominator_boundary_comparison": str(
                research / "B10_t1_b3_b5_denominator_boundary_comparison.md"
            ),
            "b10_t1_missing_assumption_note": str(research / "B10_t1_missing_assumption_note.md"),
            "b10_t1_asymptotic_access_contract": str(research / "B10_t1_asymptotic_access_contract.md"),
            "b10_t1_b5_same_access_sampling_or_dmrg_bridge": str(
                research / "B10_t1_b5_same_access_sampling_or_dmrg_bridge.md"
            ),
            "b10_t1_b5_response_sampler_cost_stress": str(
                research / "B10_t1_b5_response_sampler_cost_stress.md"
            ),
            "b9_failed_gap_amplification_lemma": str(research / "B9_failed_gap_amplification_lemma.md"),
            "b9_symbolic_gap_skeleton": str(research / "B9_symbolic_gap_skeleton.md"),
            "b9_symbolic_gap_lean_skeleton": str(
                research / "proof_skeletons" / "B9_failed_gap_amplification_skeleton.lean"
            ),
            "b9_named_family_width_locality_bounds": str(research / "B9_named_family_width_locality_bounds.md"),
            "b9_named_family_width_locality_bound_lean_skeleton": str(
                research / "proof_skeletons" / "B9_cluster_stabilizer_width_locality_bound.lean"
            ),
            "b9_cluster_stabilizer_parametric_certificate": str(
                research / "B9_cluster_stabilizer_parametric_certificate.md"
            ),
            "b7_dependency_schedule_bridge": str(research / "B7_b1_b2_dependency_schedule_bridge.md"),
            "b7_workload_dag_factory_schedule": str(research / "B7_workload_dag_factory_schedule.md"),
            "b7_logical_t_factory_schedule": str(research / "B7_logical_t_factory_schedule.md"),
            "b7_logical_t_factory_schedule_post_1q": str(research / "B7_logical_t_factory_schedule_post_1q.md"),
            "b7_logical_t_factory_schedule_native": str(research / "B7_logical_t_factory_schedule_native.md"),
            "b7_logical_t_factory_schedule_control_rz": str(research / "B7_logical_t_factory_schedule_control_rz.md"),
            "b7_logical_t_factory_schedule_u3_phase_factored": str(
                research / "B7_logical_t_factory_schedule_u3_phase_factored.md"
            ),
            "b7_min_stv_regime_classifier": str(research / "B7_min_stv_regime_classifier.md"),
            "b7_ft_synthesis_ledger": str(research / "B7_ft_synthesis_ledger.md"),
            "b7_gcm_h6_ft_boundary": str(research / "B7_gcm_h6_ft_boundary.md"),
            "b7_precision_aware_rotation_ledger": str(research / "B7_precision_aware_rotation_ledger.md"),
            "b7_gcm_h6_numeric_rotation_structure": str(research / "B7_gcm_h6_numeric_rotation_structure.md"),
            "b7_shared_synthesis_cache_boundary": str(research / "B7_shared_synthesis_cache_boundary.md"),
            "b7_nonlocal_template_block_scan": str(research / "B7_nonlocal_template_block_scan.md"),
            "b7_template_priority_gate": str(research / "B7_template_priority_gate.md"),
            "b7_w8_21_small_block_synthesis": str(research / "B7_w8_21_small_block_synthesis.md"),
            "b7_w8_21_broad_skeleton_search": str(research / "B7_w8_21_broad_skeleton_search.md"),
            "b7_w8_21_euler_local_search": str(research / "B7_w8_21_euler_local_search.md"),
            "b7_w8_21_three_cnot_search": str(research / "B7_w8_21_three_cnot_search.md"),
            "b7_w8_21_scoped_minimality_note": str(research / "B7_w8_21_scoped_minimality_note.md"),
            "b7_w8_21_claim_boundary_fragment": str(research / "B7_w8_21_claim_boundary_fragment.md"),
            "b4_b8_circuit_refresh_task": str(research / "B4_B8_circuit_refresh_task.md"),
            "b4_b8_openqasm3_randomized_measurement_packet": str(
                research / "B4_B8_openqasm3_randomized_measurement_packet.md"
            ),
            "b4_b8_openqasm3_packet_public_spoofer_gate": str(
                research / "B4_B8_openqasm3_packet_public_spoofer_gate.md"
            ),
            "b4_b8_late_bound_private_challenge_contract_gate": str(
                research / "B4_B8_late_bound_private_challenge_contract_gate.md"
            ),
            "b4_b8_nonstabilizer_late_bound_transcript_pilot": str(
                research / "B4_B8_nonstabilizer_late_bound_transcript_pilot.md"
            ),
            "b4_b8_nonstabilizer_support_spoofer_gate": str(
                research / "B4_B8_nonstabilizer_support_spoofer_gate.md"
            ),
            "b8_generative_spoofer_refresh": str(research / "B8_generative_spoofer_refresh.md"),
            "b8_adaptive_leakage_spoofer": str(research / "B8_adaptive_leakage_spoofer.md"),
            "b8_challenge_refresh_repair": str(research / "B8_challenge_refresh_repair.md"),
            "b1_ablation_report": str(research / "B1_ablation_report.json"),
        },
    }


def markdown_report(report: dict) -> str:
    lines = [
        "# Portfolio Status Report",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Overall audit: {'PASS' if report['passed'] else 'FAIL'}",
        "",
        "## Portfolio Inventory",
        "",
        f"- 100-problem catalog count: {report['catalog']['problem_count']}",
        f"- Catalog IDs contiguous 1..100: {report['catalog']['ids_are_contiguous_1_to_100']}",
        f"- Catalog metadata matrix count: {report['catalog']['metadata_matrix_count']}",
        f"- Catalog metadata complete: {report['catalog']['metadata_complete']}",
        f"- Catalog JSON status/freeze lock: {report['catalog']['json_status']} / {report['catalog']['json_freeze_lock']}",
        f"- Catalog discipline/source groups: {report['catalog']['discipline_supergroup_count']} / {report['catalog']['source_lineage_group_count']}",
        f"- Catalog non-revision covenant present: {report['catalog']['non_revision_covenant_present']}",
        f"- Top 20 evidence matches scoring: {report['top20']['evidence_matches_scoring']}",
        f"- Top 10 attack pack matches Tier 1: {report['attack_pack']['matches_tier1_top10']}",
        f"- Top 10 execution board directions: {report['execution_board']['direction_count']}",
        f"- Top 10 execution board matches attack pack: {report['execution_board']['problem_ids_match_attack_pack']}",
        f"- Top 10 problem dossiers: {report['problem_dossiers']['dossier_count']}",
        f"- Top 10 problem dossiers complete: {report['problem_dossiers']['all_required_fields_present']}",
        f"- Technical resolution directions: {report['technical_resolution_program']['direction_count']}",
        f"- Technical resolution criterion: {report['technical_resolution_program']['success_criterion']}",
        f"- Translation pipeline status: {report['translation_pipeline']['status']}",
        "",
        "## Top 10 Attack IDs",
        "",
        ", ".join(str(pid) for pid in report["attack_pack"]["ids"]),
        "",
        "## Top 10 Execution Board",
        "",
        f"- Exists: {report['execution_board']['exists']}",
        f"- B IDs are B1..B10: {report['execution_board']['b_ids_are_b1_to_b10']}",
        f"- Lanes: {report['execution_board']['lanes']}",
        "",
        "## Top 10 Problem Dossiers",
        "",
        f"- JSON exists: {report['problem_dossiers']['exists']}",
            f"- Markdown exists: {report['problem_dossiers']['markdown_exists']}",
            f"- B IDs are B1..B10: {report['problem_dossiers']['b_ids_are_b1_to_b10']}",
            f"- Problem IDs match attack pack: {report['problem_dossiers']['problem_ids_match_attack_pack']}",
            f"- All required fields present: {report['problem_dossiers']['all_required_fields_present']}",
            f"- Maturity scores: {report['problem_dossiers']['maturity_scores']}",
            "",
            "## Technical Resolution Program",
            "",
            f"- JSON exists: {report['technical_resolution_program']['exists']}",
            f"- Markdown exists: {report['technical_resolution_program']['markdown_exists']}",
            f"- B IDs are B1..B10: {report['technical_resolution_program']['b_ids_are_b1_to_b10']}",
            f"- All required fields present: {report['technical_resolution_program']['all_required_fields_present']}",
            f"- Current success criterion: {report['technical_resolution_program']['success_criterion']}",
            "",
            "## Translation Pipeline",
            "",
            f"- JSON exists: {report['translation_pipeline']['exists']}",
            f"- Markdown exists: {report['translation_pipeline']['markdown_exists']}",
            f"- Status: {report['translation_pipeline']['status']}",
            f"- Manuscripts/preprints: {report['translation_pipeline']['manuscript_count']}",
            f"- Patent disclosures: {report['translation_pipeline']['patent_disclosure_count']}",
            f"- Fundable projects: {report['translation_pipeline']['fundable_project_count']}",
            f"- Monetizable tools: {report['translation_pipeline']['tool_count']}",
            f"- Lead tool identified: {report['translation_pipeline']['has_lead_tool']}",
            f"- Declared targets met: {report['translation_pipeline']['targets_met']}",
            "",
            "## B1 Verification Status",
            "",
        "| Result | Audit | Replay | Semantic | Proof events | Exposure reduction |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key, row in report["b1"]["verification"].items():
        proof_events = row.get("proof_events", {})
        events = int(proof_events.get("single_qubit_events", 0)) + int(proof_events.get("rzz_events", 0))
        lines.append(
            "| "
            + key
            + f" | {row.get('audit')} | {row.get('replay')} | {row.get('semantic')} | {events} | {row.get('heavy_hex_like_exposure_reduction')} |"
        )
    b1_report = report["b1"]["certificate_report"]
    lines.extend(
        [
            "",
            "## B1 Certificate Evidence Report",
            "",
            f"- Exists: {b1_report.get('exists')}",
            f"- Status: {b1_report.get('status')}",
            f"- Proof-log result rows: {b1_report.get('prooflog_result_count')}",
            f"- Exact circuit count: {b1_report.get('exact_circuit_count')}",
            f"- Exact equivalence failures: {b1_report.get('exact_equivalence_failed')}",
            f"- Proof-log verification passed: {b1_report.get('proof_log_verification_passed')}",
            f"- Minimum circuit-count gate passed: {b1_report.get('minimum_circuit_count_passed')}",
            f"- Aggregate exposure-reduction gate passed: {b1_report.get('aggregate_hardware_exposure_reduction_passed')}",
            f"- Ablation table gate passed: {b1_report.get('ablation_table_passed')}",
            f"- Baseline comparison gate passed: {b1_report.get('baseline_comparison_passed')}",
            f"- Routing diagnostic gate passed: {b1_report.get('routing_diagnostic_passed')}",
            f"- Calibrated heavy-hex routing baseline passed: {b1_report.get('routing_aware_calibrated_heavy_hex_baseline_passed')}",
            f"- Heavy-hex topology diagnostic passed: {b1_report.get('heavyhex_topology_diagnostic_passed')}",
            f"- Heavy-hex end-to-end routed benefit passed: {b1_report.get('heavyhex_end_to_end_routed_benefit_passed')}",
            f"- Post-routing bottleneck profile passed: {b1_report.get('post_routing_bottleneck_profile_passed')}",
            f"- Post-routing SWAP macro compression passed: {b1_report.get('post_routing_swap_macro_compression_passed')}",
            f"- Virtual SWAP elimination passed: {b1_report.get('virtual_swap_elimination_passed')}",
            f"- Global equivalence scope gate passed: {b1_report.get('global_equivalence_scope_passed')}",
            f"- Unsupported claim count: {b1_report.get('unsupported_claim_count')}",
            "",
            "## B1 Routing Diagnostic",
            "",
            f"- Exists: {report['b1']['routing_diagnostic'].get('exists')}",
            f"- Status: {report['b1']['routing_diagnostic'].get('status')}",
            f"- Full exact-valid baseline: {report['b1']['routing_diagnostic'].get('full_exact_valid_baseline')}",
            f"- Full measurement-distribution-valid baseline: {report['b1']['routing_diagnostic'].get('full_measurement_distribution_valid_baseline')}",
            f"- Partial measurement-distribution levels: {report['b1']['routing_diagnostic'].get('partial_measurement_distribution_levels')}",
            f"- Common measurement-distribution failures: {report['b1']['routing_diagnostic'].get('common_measurement_distribution_failures')}",
            f"- Aer cross-check all passed: {report['b1']['routing_diagnostic'].get('aer_crosscheck_all_passed')}",
            f"- Aer cross-check total pairs: {report['b1']['routing_diagnostic'].get('aer_crosscheck_total_pairs')}",
            f"- Aer cross-check max TVD: {report['b1']['routing_diagnostic'].get('aer_crosscheck_max_tvd')}",
            f"- Best diagnostic exposure reduction: {report['b1']['routing_diagnostic'].get('best_diagnostic_exposure_reduction_pct')}",
            "",
            "## B1 Heavy-Hex Topology Diagnostic",
            "",
            f"- Exists: {report['b1']['heavyhex_diagnostic'].get('exists')}",
            f"- Status: {report['b1']['heavyhex_diagnostic'].get('status')}",
            f"- Distance: {report['b1']['heavyhex_diagnostic'].get('distance')}",
            f"- Physical qubits: {report['b1']['heavyhex_diagnostic'].get('physical_qubits')}",
            f"- Aer cross-check all passed: {report['b1']['heavyhex_diagnostic'].get('aer_crosscheck_all_passed')}",
            f"- Aer-valid levels: {report['b1']['heavyhex_diagnostic'].get('aer_crosscheck_valid_levels')}",
            f"- Best diagnostic exposure reduction: {report['b1']['heavyhex_diagnostic'].get('best_diagnostic_exposure_reduction_pct')}",
            "",
            "## B1 Heavy-Hex End-to-End Routed Benefit",
            "",
            f"- Exists: {report['b1']['heavyhex_end_to_end'].get('exists')}",
            f"- Status: {report['b1']['heavyhex_end_to_end'].get('status')}",
            f"- Aer cross-check pass/fail: {report['b1']['heavyhex_end_to_end'].get('aer_crosscheck_passed')} / {report['b1']['heavyhex_end_to_end'].get('aer_crosscheck_failed')}",
            f"- Operation-count reduction after routing: {report['b1']['heavyhex_end_to_end'].get('operation_count_reduction_pct')}",
            f"- Two-qubit reduction after routing: {report['b1']['heavyhex_end_to_end'].get('two_qubit_gate_count_reduction_pct')}",
            f"- Logical-depth reduction after routing: {report['b1']['heavyhex_end_to_end'].get('logical_depth_reduction_pct')}",
            f"- Exposure reduction after routing: {report['b1']['heavyhex_end_to_end'].get('hardware_weighted_exposure_reduction_pct')}",
            f"- Suite exists: {report['b1']['heavyhex_end_to_end_suite'].get('exists')}",
            f"- Suite levels tested: {report['b1']['heavyhex_end_to_end_suite'].get('levels_tested')}",
            f"- Suite all Aer cross-checks passed: {report['b1']['heavyhex_end_to_end_suite'].get('all_aer_crosschecks_passed')}",
            f"- Suite best exposure reduction: {report['b1']['heavyhex_end_to_end_suite'].get('best_exposure_reduction_pct')}",
            "",
            "## B1 Post-Routing Bottleneck Profile",
            "",
            f"- Exists: {report['b1']['post_routing_bottleneck_profile'].get('exists')}",
            f"- Status: {report['b1']['post_routing_bottleneck_profile'].get('status')}",
            f"- Levels tested: {report['b1']['post_routing_bottleneck_profile'].get('levels_tested')}",
            f"- All Aer cross-checks passed: {report['b1']['post_routing_bottleneck_profile'].get('all_aer_crosschecks_passed')}",
            f"- Level 0 exposure reduction: {report['b1']['post_routing_bottleneck_profile'].get('level0_exposure_reduction_pct')}",
            f"- Level 1 exposure reduction: {report['b1']['post_routing_bottleneck_profile'].get('level1_exposure_reduction_pct')}",
            f"- Benefit-erased circuits: {report['b1']['post_routing_bottleneck_profile'].get('erased_circuit_count')}",
            f"- Top level-1 2Q bottleneck: {report['b1']['post_routing_bottleneck_profile'].get('top_level1_two_qubit_bottleneck')}",
            "",
            "## B1 Post-Routing SWAP Macro Diagnostic",
            "",
            f"- Exists: {report['b1']['post_routing_swap_macro'].get('exists')}",
            f"- Status: {report['b1']['post_routing_swap_macro'].get('status')}",
            f"- SWAP macros: {report['b1']['post_routing_swap_macro'].get('swap_macros')}",
            f"- Removed CX gates: {report['b1']['post_routing_swap_macro'].get('removed_cx_gates')}",
            f"- 2Q macro reduction: {report['b1']['post_routing_swap_macro'].get('two_qubit_reduction_pct')}",
            f"- Exposure reduction under macro cost model: {report['b1']['post_routing_swap_macro'].get('exposure_reduction_pct')}",
            f"- Local Aer failures: {report['b1']['post_routing_swap_macro'].get('local_aer_failed')}",
            f"- End-to-end Aer failures: {report['b1']['post_routing_swap_macro'].get('end_to_end_aer_failed')}",
            f"- Top SWAP macro circuit: {report['b1']['post_routing_swap_macro'].get('top_swap_macro_circuit')}",
            "",
            "## B1 Virtual SWAP Elimination",
            "",
            f"- Exists: {report['b1']['virtual_swap_elimination'].get('exists')}",
            f"- Status: {report['b1']['virtual_swap_elimination'].get('status')}",
            f"- Rewritten circuits: {report['b1']['virtual_swap_elimination'].get('rewritten_circuits')}",
            f"- Skipped circuits: {report['b1']['virtual_swap_elimination'].get('skipped_circuits')}",
            f"- Virtual SWAPs removed: {report['b1']['virtual_swap_elimination'].get('virtual_swaps_removed')}",
            f"- Removed CX gates: {report['b1']['virtual_swap_elimination'].get('removed_cx_gates')}",
            f"- 2Q reduction: {report['b1']['virtual_swap_elimination'].get('two_qubit_reduction_pct')}",
            f"- Exposure reduction: {report['b1']['virtual_swap_elimination'].get('exposure_reduction_pct')}",
            f"- Local Aer failures: {report['b1']['virtual_swap_elimination'].get('local_aer_failed')}",
            f"- End-to-end Aer failures: {report['b1']['virtual_swap_elimination'].get('end_to_end_aer_failed')}",
            f"- Proof replay status: {report['b1']['virtual_swap_elimination'].get('proof_replay_status')}",
            f"- Proof replay events: {report['b1']['virtual_swap_elimination'].get('proof_replayed_events')} / {report['b1']['virtual_swap_elimination'].get('proof_replay_events')}",
            f"- Proof replay output mismatches: {report['b1']['virtual_swap_elimination'].get('proof_replay_output_mismatches')}",
            f"- Proof replay errors: {report['b1']['virtual_swap_elimination'].get('proof_replay_error_count')}",
            f"- Top virtual-SWAP circuit: {report['b1']['virtual_swap_elimination'].get('top_virtual_swap_circuit')}",
            "",
            "## B1 Post-Virtual-SWAP 1Q Resynthesis",
            "",
            f"- Exists: {report['b1']['post_virtual_swap_1q_resynthesis'].get('exists')}",
            f"- Status: {report['b1']['post_virtual_swap_1q_resynthesis'].get('status')}",
            f"- Rewritten circuits: {report['b1']['post_virtual_swap_1q_resynthesis'].get('rewritten_circuits')}",
            f"- Resynthesized 1Q runs: {report['b1']['post_virtual_swap_1q_resynthesis'].get('resynthesized_runs')}",
            f"- Removed 1Q gates: {report['b1']['post_virtual_swap_1q_resynthesis'].get('removed_single_qubit_gates')}",
            f"- Certificate events: {report['b1']['post_virtual_swap_1q_resynthesis'].get('certificate_entries')}",
            f"- Logical T-count proxy reduction: {report['b1']['post_virtual_swap_1q_resynthesis'].get('logical_t_count_reduction')}",
            f"- Logical T-depth proxy reduction: {report['b1']['post_virtual_swap_1q_resynthesis'].get('logical_t_depth_reduction')}",
            f"- Non-Clifford rotation reduction: {report['b1']['post_virtual_swap_1q_resynthesis'].get('non_clifford_rotation_count_reduction')}",
            f"- Aer failures: {report['b1']['post_virtual_swap_1q_resynthesis'].get('aer_failed')}",
            f"- Aer pairs: {report['b1']['post_virtual_swap_1q_resynthesis'].get('aer_pair_count')}",
            f"- Aer max TVD: {report['b1']['post_virtual_swap_1q_resynthesis'].get('aer_max_tvd')}",
            "",
            "## B1 Native T-Resource Optimizer",
            "",
            f"- Exists: {report['b1']['native_t_resource_optimizer'].get('exists')}",
            f"- Status: {report['b1']['native_t_resource_optimizer'].get('status')}",
            f"- Rewritten circuits: {report['b1']['native_t_resource_optimizer'].get('rewritten_circuits')}",
            f"- Circuits changed: {report['b1']['native_t_resource_optimizer'].get('circuits_changed')}",
            f"- Canonicalization events: {report['b1']['native_t_resource_optimizer'].get('canonicalization_events')}",
            f"- Identity events: {report['b1']['native_t_resource_optimizer'].get('identity_events')}",
            f"- Native RZ rewrite events: {report['b1']['native_t_resource_optimizer'].get('rz_rewrite_events')}",
            f"- Removed 1Q gates: {report['b1']['native_t_resource_optimizer'].get('removed_single_qubit_gates')}",
            f"- Certificate events: {report['b1']['native_t_resource_optimizer'].get('certificate_entries')}",
            f"- Logical T-count proxy reduction: {report['b1']['native_t_resource_optimizer'].get('logical_t_count_reduction')}",
            f"- Logical T-depth proxy reduction: {report['b1']['native_t_resource_optimizer'].get('logical_t_depth_reduction')}",
            f"- Non-Clifford rotation reduction: {report['b1']['native_t_resource_optimizer'].get('non_clifford_rotation_count_reduction')}",
            f"- Aer failures: {report['b1']['native_t_resource_optimizer'].get('aer_failed')}",
            f"- Aer pairs: {report['b1']['native_t_resource_optimizer'].get('aer_pair_count')}",
            f"- Aer max TVD: {report['b1']['native_t_resource_optimizer'].get('aer_max_tvd')}",
            "",
            "## B1 Control-RZ Commute Optimizer",
            "",
            f"- Exists: {report['b1']['control_rz_commute_optimizer'].get('exists')}",
            f"- Status: {report['b1']['control_rz_commute_optimizer'].get('status')}",
            f"- Rewritten circuits: {report['b1']['control_rz_commute_optimizer'].get('rewritten_circuits')}",
            f"- Circuits changed: {report['b1']['control_rz_commute_optimizer'].get('circuits_changed')}",
            f"- Absorbed RZ gates: {report['b1']['control_rz_commute_optimizer'].get('absorbed_rz_gates')}",
            f"- Certificate events: {report['b1']['control_rz_commute_optimizer'].get('certificate_entries')}",
            f"- Merged or moved groups: {report['b1']['control_rz_commute_optimizer'].get('merged_or_moved_groups')}",
            f"- Removed RZ gates: {report['b1']['control_rz_commute_optimizer'].get('removed_rz_gates')}",
            f"- CNOT-control commutations: {report['b1']['control_rz_commute_optimizer'].get('commuted_cx_count')}",
            f"- Logical T-count proxy reduction: {report['b1']['control_rz_commute_optimizer'].get('logical_t_count_reduction')}",
            f"- Logical T-depth proxy reduction: {report['b1']['control_rz_commute_optimizer'].get('logical_t_depth_reduction')}",
            f"- Non-Clifford rotation reduction: {report['b1']['control_rz_commute_optimizer'].get('non_clifford_rotation_count_reduction')}",
            f"- Aer failures: {report['b1']['control_rz_commute_optimizer'].get('aer_failed')}",
            f"- Aer pairs: {report['b1']['control_rz_commute_optimizer'].get('aer_pair_count')}",
            f"- Aer max TVD: {report['b1']['control_rz_commute_optimizer'].get('aer_max_tvd')}",
            "",
            "## B1 U3 Phase-Factored Optimizer",
            "",
            f"- Exists: {report['b1']['u3_phase_factored_optimizer'].get('exists')}",
            f"- Status: {report['b1']['u3_phase_factored_optimizer'].get('status')}",
            f"- Rewritten circuits: {report['b1']['u3_phase_factored_optimizer'].get('rewritten_circuits')}",
            f"- Circuits changed: {report['b1']['u3_phase_factored_optimizer'].get('circuits_changed')}",
            f"- U3 factorization events: {report['b1']['u3_phase_factored_optimizer'].get('u3_factorization_events')}",
            f"- RZ components emitted: {report['b1']['u3_phase_factored_optimizer'].get('rz_components_emitted')}",
            f"- RY components emitted: {report['b1']['u3_phase_factored_optimizer'].get('ry_components_emitted')}",
            f"- Zero components removed: {report['b1']['u3_phase_factored_optimizer'].get('zero_components_removed')}",
            f"- Factorization certificate events: {report['b1']['u3_phase_factored_optimizer'].get('factorization_certificate_entries')}",
            f"- RZ commute certificate events: {report['b1']['u3_phase_factored_optimizer'].get('rz_commute_certificate_entries')}",
            f"- Removed RZ gates: {report['b1']['u3_phase_factored_optimizer'].get('removed_rz_gates')}",
            f"- CNOT-control commutations: {report['b1']['u3_phase_factored_optimizer'].get('commuted_cx_count')}",
            f"- Logical T-count proxy reduction: {report['b1']['u3_phase_factored_optimizer'].get('logical_t_count_reduction')}",
            f"- Logical T-depth proxy reduction: {report['b1']['u3_phase_factored_optimizer'].get('logical_t_depth_reduction')}",
            f"- Non-Clifford rotation reduction: {report['b1']['u3_phase_factored_optimizer'].get('non_clifford_rotation_count_reduction')}",
            f"- Aer failures: {report['b1']['u3_phase_factored_optimizer'].get('aer_failed')}",
            f"- Aer pairs: {report['b1']['u3_phase_factored_optimizer'].get('aer_pair_count')}",
            f"- Aer max TVD: {report['b1']['u3_phase_factored_optimizer'].get('aer_max_tvd')}",
            "",
            "## B1/B7 gcm_h6 Target Selector",
            "",
            f"- Exists: {report['b1']['b7_gcm_h6_target_selector'].get('exists')}",
            f"- Status: {report['b1']['b7_gcm_h6_target_selector'].get('status')}",
            f"- Arbitrary rotations / target removals / proxy-T target: {report['b1']['b7_gcm_h6_target_selector'].get('arbitrary_rotation_count')} / {report['b1']['b7_gcm_h6_target_selector'].get('target_removed_arbitrary_occurrences_for_gcm_h6_1_20')} / {report['b1']['b7_gcm_h6_target_selector'].get('target_proxy_t_ledger_reduction_for_gcm_h6_1_20')}",
            f"- Raw/canonical unique numeric parameters: {report['b1']['b7_gcm_h6_target_selector'].get('raw_unique_numeric_parameter_count')} / {report['b1']['b7_gcm_h6_target_selector'].get('canonical_unique_numeric_parameter_count')}",
            f"- Top angle / cone occurrences: {report['b1']['b7_gcm_h6_target_selector'].get('top_canonical_angle_occurrences')} / {report['b1']['b7_gcm_h6_target_selector'].get('top_cone_occurrences')}",
            f"- Cone/angle/qubit classes meeting target: {report['b1']['b7_gcm_h6_target_selector'].get('cone_classes_meeting_target_if_one_removed_per_occurrence')} / {report['b1']['b7_gcm_h6_target_selector'].get('canonical_angle_classes_meeting_target_if_one_removed_per_occurrence')} / {report['b1']['b7_gcm_h6_target_selector'].get('qubit_classes_meeting_target_if_one_removed_per_occurrence')}",
            f"- Rewrite/resource/semantic claims: {report['b1']['b7_gcm_h6_target_selector'].get('rewrite_claimed')} / {report['b1']['b7_gcm_h6_target_selector'].get('resource_saving_claimed')} / {report['b1']['b7_gcm_h6_target_selector'].get('semantic_certificate_claimed')}",
            f"- Validation errors: {report['b1']['b7_gcm_h6_target_selector'].get('validation_error_count')}",
            "",
            "## B1/B7 gcm_h6 Cone Feasibility Gate",
            "",
            f"- Exists: {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('status')}",
            f"- Target cone classes / total occurrences: {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('target_cone_class_count')} / {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('target_cone_total_occurrences')}",
            f"- Strict direct sandwiches / pair-local windows / pair-local single-arb windows: {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('strict_direct_sandwich_total')} / {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('pair_local_window_total')} / {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('pair_local_single_arbitrary_window_total')}",
            f"- Cone classes meeting target by pair-local single windows: {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('cone_classes_meeting_target_by_pair_local_single_windows')}",
            f"- Leading feasible cone / windows / direct sandwiches: {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('leading_feasible_cone_id')} / {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('leading_feasible_pair_local_single_window_count')} / {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('leading_feasible_direct_sandwich_count')}",
            f"- Rewrite/resource/semantic claims: {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('rewrite_claimed')} / {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('resource_saving_claimed')} / {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('semantic_certificate_claimed')}",
            f"- Validation errors: {report['b1']['b7_gcm_h6_cone_feasibility_gate'].get('validation_error_count')}",
            "",
            "## B1/B7 cone_01 Phase-Removal Gate",
            "",
            f"- Exists: {report['b1']['b7_cone01_phase_removal_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_cone01_phase_removal_gate'].get('status')}",
            f"- Target cone / candidate windows / required windows: {report['b1']['b7_cone01_phase_removal_gate'].get('target_cone_id')} / {report['b1']['b7_cone01_phase_removal_gate'].get('candidate_window_count')} / {report['b1']['b7_cone01_phase_removal_gate'].get('required_exact_windows_for_b7_target')}",
            f"- Remove-only / fixed-phase / continuous-RZ exact passes: {report['b1']['b7_cone01_phase_removal_gate'].get('remove_only_exact_pass_count')} / {report['b1']['b7_cone01_phase_removal_gate'].get('fixed_phase_exact_pass_count')} / {report['b1']['b7_cone01_phase_removal_gate'].get('continuous_rz_exact_pass_count')}",
            f"- Best / median continuous-RZ residual: {report['b1']['b7_cone01_phase_removal_gate'].get('best_continuous_rz_residual_norm')} / {report['b1']['b7_cone01_phase_removal_gate'].get('median_continuous_rz_residual_norm')}",
            f"- Best fixed-phase residual: {report['b1']['b7_cone01_phase_removal_gate'].get('best_fixed_phase_residual_norm')}",
            f"- Restricted gate clears B7 target: {report['b1']['b7_cone01_phase_removal_gate'].get('restricted_gate_clears_b7_target')}",
            f"- Rewrite/resource/semantic/obstruction claims: {report['b1']['b7_cone01_phase_removal_gate'].get('rewrite_claimed')} / {report['b1']['b7_cone01_phase_removal_gate'].get('resource_saving_claimed')} / {report['b1']['b7_cone01_phase_removal_gate'].get('semantic_certificate_claimed')} / {report['b1']['b7_cone01_phase_removal_gate'].get('obstruction_theorem_claimed')}",
            f"- Validation errors: {report['b1']['b7_cone01_phase_removal_gate'].get('validation_error_count')}",
            "",
            "## B1/B7 cone_01 Euler-Reabsorption Gate",
            "",
            f"- Exists: {report['b1']['b7_cone01_euler_reabsorption_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_cone01_euler_reabsorption_gate'].get('status')}",
            f"- Target cone / candidate windows / required windows: {report['b1']['b7_cone01_euler_reabsorption_gate'].get('target_cone_id')} / {report['b1']['b7_cone01_euler_reabsorption_gate'].get('candidate_window_count')} / {report['b1']['b7_cone01_euler_reabsorption_gate'].get('required_exact_windows_for_b7_target')}",
            f"- Exact RY candidates / optimizer seeds: {report['b1']['b7_cone01_euler_reabsorption_gate'].get('exact_ry_candidate_angle_count')} / {report['b1']['b7_cone01_euler_reabsorption_gate'].get('optimizer_seed_count')}",
            f"- Fixed-RY plus RZ-reabsorption exact passes: {report['b1']['b7_cone01_euler_reabsorption_gate'].get('fixed_ry_with_rz_reabsorption_exact_pass_count')}",
            f"- Best / median residual: {report['b1']['b7_cone01_euler_reabsorption_gate'].get('best_residual_norm')} / {report['b1']['b7_cone01_euler_reabsorption_gate'].get('median_residual_norm')}",
            f"- Editable RZ parameter range: {report['b1']['b7_cone01_euler_reabsorption_gate'].get('editable_rz_parameter_count_min')} - {report['b1']['b7_cone01_euler_reabsorption_gate'].get('editable_rz_parameter_count_max')}",
            f"- Restricted gate clears B7 target: {report['b1']['b7_cone01_euler_reabsorption_gate'].get('restricted_gate_clears_b7_target')}",
            f"- Rewrite/resource/semantic/obstruction claims: {report['b1']['b7_cone01_euler_reabsorption_gate'].get('rewrite_claimed')} / {report['b1']['b7_cone01_euler_reabsorption_gate'].get('resource_saving_claimed')} / {report['b1']['b7_cone01_euler_reabsorption_gate'].get('semantic_certificate_claimed')} / {report['b1']['b7_cone01_euler_reabsorption_gate'].get('obstruction_theorem_claimed')}",
            f"- Validation errors: {report['b1']['b7_cone01_euler_reabsorption_gate'].get('validation_error_count')}",
            "",
            "## B1/B7 cone_01 Parameter-Transfer Gate",
            "",
            f"- Exists: {report['b1']['b7_cone01_parameter_transfer_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_cone01_parameter_transfer_gate'].get('status')}",
            f"- Target cone / candidate windows / required windows: {report['b1']['b7_cone01_parameter_transfer_gate'].get('target_cone_id')} / {report['b1']['b7_cone01_parameter_transfer_gate'].get('candidate_window_count')} / {report['b1']['b7_cone01_parameter_transfer_gate'].get('required_exact_windows_for_b7_target')}",
            f"- Nonzero/zero parameter-sensitivity windows: {report['b1']['b7_cone01_parameter_transfer_gate'].get('nonzero_parameter_sensitivity_count')} / {report['b1']['b7_cone01_parameter_transfer_gate'].get('parameter_sensitivity_zero_count')}",
            f"- Near pi/4-grid windows: {report['b1']['b7_cone01_parameter_transfer_gate'].get('near_pi_over_four_grid_count')}",
            f"- Distinct theta / largest group / repeated occurrences: {report['b1']['b7_cone01_parameter_transfer_gate'].get('distinct_canonical_theta_count')} / {report['b1']['b7_cone01_parameter_transfer_gate'].get('largest_repeated_theta_group')} / {report['b1']['b7_cone01_parameter_transfer_gate'].get('repeated_theta_occurrence_count')}",
            f"- Minimum parameter-carrier obligation: {report['b1']['b7_cone01_parameter_transfer_gate'].get('minimum_parameter_carrier_obligation_for_b7_target')}",
            f"- Deletion without parameter carrier clears B7 target: {report['b1']['b7_cone01_parameter_transfer_gate'].get('deletion_without_parameter_carrier_clears_b7_target')}",
            f"- Rewrite/resource/semantic/obstruction claims: {report['b1']['b7_cone01_parameter_transfer_gate'].get('rewrite_claimed')} / {report['b1']['b7_cone01_parameter_transfer_gate'].get('resource_saving_claimed')} / {report['b1']['b7_cone01_parameter_transfer_gate'].get('semantic_certificate_claimed')} / {report['b1']['b7_cone01_parameter_transfer_gate'].get('obstruction_theorem_claimed')}",
            f"- Validation errors: {report['b1']['b7_cone01_parameter_transfer_gate'].get('validation_error_count')}",
            "",
            "## B1/B7 cone_01 Theta-Sharing Ledger Gate",
            "",
            f"- Exists: {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('status')}",
            f"- Candidate windows / theta groups / duplicate theta occurrences: {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('candidate_window_count')} / {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('distinct_theta_group_count')} / {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('duplicate_theta_occurrence_count')}",
            f"- Optimistic cache proxy-T reuse / target proxy-T: {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('optimistic_cache_proxy_t_reuse')} / {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('target_proxy_t_ledger_reduction_for_gcm_h6_1_20')}",
            f"- Optimistic cache model clears target: {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('optimistic_cache_model_clears_target')}",
            f"- Occurrence-ledger removed occurrences / proxy-T reduction: {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('occurrence_ledger_removed_occurrences')} / {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('occurrence_ledger_proxy_t_reduction')}",
            f"- Occurrence-ledger clears target: {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('occurrence_ledger_clears_target')}",
            f"- Additional occurrence certificates required: {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('additional_occurrence_certificates_required')}",
            f"- Cache model accepted as FT ledger: {not report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('cache_model_not_accepted_as_ft_ledger')}",
            f"- Rewrite/resource/semantic/physical/B7-ledger claims: {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('rewrite_claimed')} / {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('resource_saving_claimed')} / {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('semantic_certificate_claimed')} / {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('physical_resource_reduction_claimed')} / {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('b7_ledger_improvement_claimed')}",
            f"- Validation errors: {report['b1']['b7_cone01_theta_sharing_ledger_gate'].get('validation_error_count')}",
            "",
            "## B1/B7 cone_01 Shared-Theta Synthesis Object Gate",
            "",
            f"- Exists: {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('status')}",
            f"- Candidate windows / shared objects / covered occurrences: {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('candidate_window_count')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('shared_synthesis_object_count')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('covered_occurrence_count')}",
            f"- Duplicate theta occurrences / optimistic cache signal: {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('duplicate_theta_occurrence_count')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('optimistic_cache_proxy_t_reuse')}",
            f"- Object existence / all windows covered: {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('shared_object_existence_gate_passed')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('all_candidate_windows_covered')}",
            f"- Replay/layout/B7-accepted object counts: {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('semantic_replay_verified_object_count')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('physical_layout_assigned_object_count')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('b7_ledger_accepted_object_count')}",
            f"- Occurrence-ledger removed occurrences / proxy-T reduction: {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('occurrence_ledger_removed_occurrences')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('occurrence_ledger_proxy_t_reduction')}",
            f"- Cost model accepted: {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('cost_model_accepted')}",
            f"- Rewrite/resource/semantic/physical/B7-ledger claims: {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('rewrite_claimed')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('resource_saving_claimed')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('semantic_certificate_claimed')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('physical_resource_reduction_claimed')} / {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('b7_ledger_improvement_claimed')}",
            f"- Validation errors: {report['b1']['b7_cone01_shared_theta_synthesis_object_gate'].get('validation_error_count')}",
            "",
            "## B1/B7 cone_01 Shared-Theta Replay Verifier Gate",
            "",
            f"- Exists: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('status')}",
            f"- Candidate windows / shared objects: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('candidate_window_count')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('shared_synthesis_object_count')}",
            f"- Replay-verified objects / replayed occurrences: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('replay_verified_object_count')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('replayed_occurrence_count')}",
            f"- Coverage matches parameter transfer: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('coverage_matches_parameter_transfer')}",
            f"- Duplicate/missing/theta-mismatch/object-mismatch counts: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('duplicate_line_count')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('missing_qasm_line_count')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('line_theta_mismatch_count')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('object_group_mismatch_count')}",
            f"- Shared-theta replay gate passed: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('shared_theta_replay_gate_passed')}",
            f"- Semantic rewrite verified / cost model accepted: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('semantic_rewrite_verified')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('cost_model_accepted')}",
            f"- Occurrence-ledger removed occurrences / proxy-T reduction: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('occurrence_ledger_removed_occurrences')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('occurrence_ledger_proxy_t_reduction')}",
            f"- Rewrite/resource/semantic/physical/B7-ledger claims: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('rewrite_claimed')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('resource_saving_claimed')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('semantic_certificate_claimed')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('physical_resource_reduction_claimed')} / {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('b7_ledger_improvement_claimed')}",
            f"- Validation errors: {report['b1']['b7_cone01_shared_theta_replay_verifier_gate'].get('validation_error_count')}",
            "",
            "## B1/B7 cone_01 Shared-Theta Layout/Routing Gate",
            "",
            f"- Exists: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('status')}",
            f"- Candidate windows / shared objects: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('candidate_window_count')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('shared_synthesis_object_count')}",
            f"- Layout-routed objects / occurrences: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('layout_routed_object_count')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('layout_routed_occurrence_count')}",
            f"- Logical anchors / route packets: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('logical_anchor_object_count')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('logical_route_packet_count')}",
            f"- Logical topology qubits / total hops / max hops: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('logical_line_topology_qubit_count')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('total_logical_hop_count')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('max_logical_hop_count')}",
            f"- Missing routes / layout gate passed: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('missing_route_count')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('layout_routing_gate_passed')}",
            f"- Physical layout / factory model / error budget present: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('physical_layout_claimed')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('factory_amortization_model_present')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('shared_error_budget_present')}",
            f"- Occurrence-ledger removed occurrences / proxy-T reduction: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('occurrence_ledger_removed_occurrences')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('occurrence_ledger_proxy_t_reduction')}",
            f"- Rewrite/resource/semantic/physical/B7-ledger claims: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('rewrite_claimed')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('resource_saving_claimed')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('semantic_certificate_claimed')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('physical_resource_reduction_claimed')} / {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('b7_ledger_improvement_claimed')}",
            f"- Validation errors: {report['b1']['b7_cone01_shared_theta_layout_routing_gate'].get('validation_error_count')}",
            "",
            "## B1/B7 cone_01 Shared-Theta Factory-Amortization Gate",
            "",
            f"- Exists: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('status')}",
            f"- Candidate windows / shared objects / routed occurrences: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('candidate_window_count')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('shared_synthesis_object_count')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('layout_routed_occurrence_count')}",
            f"- Baseline/shared factory compilation counts: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('baseline_factory_compilation_count')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('shared_object_factory_compilation_count')}",
            f"- Amortized saved compiles / gross proxy-T delta: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('amortized_saved_compilation_count')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('gross_proxy_t_pressure_delta')}",
            f"- Baseline/shared proxy-T pressure: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('baseline_proxy_t_pressure')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('shared_object_proxy_t_pressure')}",
            f"- Factory gate passed: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('factory_amortization_gate_passed')}",
            f"- Physical factory schedule / error budget / independent baseline / refreshed B7 ledger: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('physical_factory_schedule_present')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('shared_error_budget_present')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('independent_baseline_present')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('refreshed_b7_ledger_present')}",
            f"- Occurrence-ledger removed occurrences / proxy-T reduction: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('occurrence_ledger_removed_occurrences')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('occurrence_ledger_proxy_t_reduction')}",
            f"- Rewrite/resource/semantic/physical/B7-ledger claims: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('rewrite_claimed')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('resource_saving_claimed')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('semantic_certificate_claimed')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('physical_resource_reduction_claimed')} / {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('b7_ledger_improvement_claimed')}",
            f"- Validation errors: {report['b1']['b7_cone01_shared_theta_factory_amortization_gate'].get('validation_error_count')}",
            "",
            "## B1/B7 cone_01 Shared-Theta Error-Budget Gate",
            "",
            f"- Exists: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('status')}",
            f"- Candidate windows / shared objects / routed occurrences: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('candidate_window_count')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('shared_synthesis_object_count')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('layout_routed_occurrence_count')}",
            f"- Total / per-object / per-occurrence error budget: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('total_shared_theta_error_budget')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('per_object_error_budget')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('per_occurrence_error_budget')}",
            f"- Aggregate occurrence / object error budget: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('aggregate_per_occurrence_error_budget')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('aggregate_object_error_budget')}",
            f"- Correlation groups / max correlated occurrences: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('correlation_group_count')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('max_correlated_occurrence_count')}",
            f"- Shared-error gate / factory gate passed: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('shared_error_budget_gate_passed')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('factory_amortization_gate_passed')}",
            f"- Independent calibration / hardware noise / independent baseline / refreshed B7 ledger: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('independent_calibration_present')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('hardware_noise_model_present')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('independent_baseline_present')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('refreshed_b7_ledger_present')}",
            f"- Occurrence-ledger removed occurrences / proxy-T reduction: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('occurrence_ledger_removed_occurrences')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('occurrence_ledger_proxy_t_reduction')}",
            f"- Rewrite/resource/semantic/physical/B7-ledger claims: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('rewrite_claimed')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('resource_saving_claimed')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('semantic_certificate_claimed')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('physical_resource_reduction_claimed')} / {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('b7_ledger_improvement_claimed')}",
            f"- Validation errors: {report['b1']['b7_cone01_shared_theta_error_budget_gate'].get('validation_error_count')}",
            "",
            "## B1/B7 cone_01 Theta-Sharing Cost-Model Gate",
            "",
            f"- Exists: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('exists')}",
            f"- Status: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('status')}",
            f"- Candidate windows / theta groups / duplicate theta occurrences: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('candidate_window_count')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('distinct_theta_group_count')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('duplicate_theta_occurrence_count')}",
            f"- Optimistic cache signal / target proxy-T: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('optimistic_cache_proxy_t_reuse')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('target_proxy_t_ledger_reduction_for_gcm_h6_1_20')}",
            f"- Shared object gate / replay gate: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_object_existence_gate_passed')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_replay_gate_passed')}",
            f"- Replay-verified shared objects / replayed occurrences: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_replay_verified_object_count')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_replayed_occurrence_count')}",
            f"- Layout gate / routed objects / routed occurrences: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_layout_routing_gate_passed')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_layout_routed_object_count')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_layout_routed_occurrence_count')}",
            f"- Layout total / max logical hops: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_layout_total_logical_hop_count')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_layout_max_logical_hop_count')}",
            f"- Factory gate / baseline compiles / shared compiles: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_factory_amortization_gate_passed')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_factory_baseline_compilation_count')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_factory_shared_object_compilation_count')}",
            f"- Factory gross proxy-T delta: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_factory_gross_proxy_t_delta')}",
            f"- Error-budget gate / total budget / aggregate occurrence budget: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_error_budget_gate_passed')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_total_error_budget')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_aggregate_per_occurrence_error_budget')}",
            f"- Error-budget correlation groups / max correlated occurrences: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_correlation_group_count')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('shared_theta_max_correlated_occurrence_count')}",
            f"- Acceptance gates passed / failed / total: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('cost_model_acceptance_pass_count')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('cost_model_acceptance_fail_count')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('cost_model_acceptance_gate_count')}",
            f"- Cost model accepted: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('cost_model_accepted')}",
            f"- B7 ledger proxy-T reduction after cost model: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('b7_ledger_proxy_t_reduction_after_cost_model')}",
            f"- Additional occurrence certificates / cost-model gates required: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('additional_occurrence_certificates_required')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('additional_cost_model_gates_required')}",
            f"- Rewrite/resource/semantic/physical/B7-ledger claims: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('rewrite_claimed')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('resource_saving_claimed')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('semantic_certificate_claimed')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('physical_resource_reduction_claimed')} / {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('b7_ledger_improvement_claimed')}",
            f"- Validation errors: {report['b1']['b7_cone01_theta_sharing_cost_model_gate'].get('validation_error_count')}",
            "",
            "## B1 Synthetic Heavy-Hex Noise Proxy",
            "",
            f"- Exists: {report['b1']['synthetic_noise_proxy'].get('exists')}",
            f"- Status: {report['b1']['synthetic_noise_proxy'].get('status')}",
            f"- Profile: {report['b1']['synthetic_noise_proxy'].get('profile')}",
            f"- Best comparison: {report['b1']['synthetic_noise_proxy'].get('best_comparison_by_exposure_reduction')}",
            f"- Source routed vs virtual-SWAP exposure reduction: {report['b1']['synthetic_noise_proxy'].get('source_vs_virtual_swap_exposure_reduction_pct')}",
            f"- Source routed vs virtual-SWAP success proxy ratio: {report['b1']['synthetic_noise_proxy'].get('source_vs_virtual_swap_success_proxy_ratio')}",
            "",
            "## B2 Baseline Status",
            "",
            f"- Status: {report['b2']['baseline'].get('status')}",
            f"- Configurations: {report['b2']['baseline'].get('configurations')}",
            f"- Shots per configuration: {report['b2']['baseline'].get('shots_per_configuration')}",
            f"- Result exists: {report['b2']['baseline'].get('result_exists')}",
            f"- Target-volume combinations: {report['b2']['target_volume'].get('target_combinations')}",
            f"- Target-volume met/unmet: {report['b2']['target_volume'].get('met_count')} / {report['b2']['target_volume'].get('unmet_count')}",
            f"- Target-volume result exists: {report['b2']['target_volume'].get('result_exists')}",
            f"- Surface-code rough estimate status: {report['b2']['surface_code_estimate'].get('status')}",
            f"- Surface-code rough estimate met/unmet: {report['b2']['surface_code_estimate'].get('met_count')} / {report['b2']['surface_code_estimate'].get('unmet_count')}",
            f"- Surface-code rough estimate result exists: {report['b2']['surface_code_estimate'].get('result_exists')}",
            f"- Phenomenological decoder status: {report['b2']['phenomenological_decoder'].get('status')}",
            f"- Phenomenological decoder configurations: {report['b2']['phenomenological_decoder'].get('configurations')}",
            f"- Phenomenological decoder improved configurations: {report['b2']['phenomenological_decoder'].get('improved_configurations')}",
            f"- Phenomenological decoder best relative reduction: {report['b2']['phenomenological_decoder'].get('best_relative_reduction')}",
            f"- Phenomenological decoder result exists: {report['b2']['phenomenological_decoder'].get('result_exists')}",
            f"- Stim/PyMatching surface-code baseline status: {report['b2']['stim_surface_code_baseline'].get('status')}",
            f"- Stim/PyMatching surface-code configurations: {report['b2']['stim_surface_code_baseline'].get('configurations')}",
            f"- Stim/PyMatching surface-code total shots: {report['b2']['stim_surface_code_baseline'].get('total_shots')}",
            f"- Stim/PyMatching surface-code distances: {report['b2']['stim_surface_code_baseline'].get('distance_values')}",
            f"- Stim/PyMatching surface-code memory bases: {report['b2']['stim_surface_code_baseline'].get('memory_bases')}",
            f"- Stim/PyMatching surface-code nonincreasing trend checks: {report['b2']['stim_surface_code_baseline'].get('nonincreasing_trend_count')} / {report['b2']['stim_surface_code_baseline'].get('distance_trend_checks')}",
            f"- Stim/PyMatching surface-code max decoder runtime / shot: {report['b2']['stim_surface_code_baseline'].get('max_decoder_runtime_seconds_per_shot')}",
            f"- Stim/PyMatching surface-code result exists: {report['b2']['stim_surface_code_baseline'].get('result_exists')}",
            f"- Stim surface-code target-volume status: {report['b2']['stim_surface_code_target_volume'].get('status')}",
            f"- Stim surface-code target-volume criterion: {report['b2']['stim_surface_code_target_volume'].get('criterion')}",
            f"- Stim surface-code target-volume combinations: {report['b2']['stim_surface_code_target_volume'].get('target_combinations')}",
            f"- Stim surface-code target-volume met/unmet: {report['b2']['stim_surface_code_target_volume'].get('met_count')} / {report['b2']['stim_surface_code_target_volume'].get('unmet_count')}",
            f"- Stim surface-code target-volume result exists: {report['b2']['stim_surface_code_target_volume'].get('result_exists')}",
            f"- Biased schedule proxy status: {report['b2']['biased_schedule_proxy'].get('status')}",
            f"- Biased schedule proxy target combinations: {report['b2']['biased_schedule_proxy'].get('target_combinations')}",
            f"- Biased schedule proxy baseline/candidate met: {report['b2']['biased_schedule_proxy'].get('baseline_met_count')} / {report['b2']['biased_schedule_proxy'].get('candidate_met_count')}",
            f"- Biased schedule proxy candidate-only target hits: {report['b2']['biased_schedule_proxy'].get('candidate_only_meets_target_count')}",
            f"- Biased schedule proxy volume improvements: {report['b2']['biased_schedule_proxy'].get('improved_volume_count')}",
            f"- Biased schedule proxy result exists: {report['b2']['biased_schedule_proxy'].get('result_exists')}",
            f"- Stim biased schedule sweep status: {report['b2']['stim_biased_schedule_sweep'].get('status')}",
            f"- Stim biased schedule sweep configurations: {report['b2']['stim_biased_schedule_sweep'].get('configurations')}",
            f"- Stim biased schedule sweep total shots: {report['b2']['stim_biased_schedule_sweep'].get('total_shots')}",
            f"- Stim biased schedule sweep baseline/candidate met: {report['b2']['stim_biased_schedule_sweep'].get('baseline_met_count')} / {report['b2']['stim_biased_schedule_sweep'].get('candidate_met_count')}",
            f"- Stim biased schedule sweep candidate-only target hits: {report['b2']['stim_biased_schedule_sweep'].get('candidate_only_meets_target_count')}",
            f"- Stim biased schedule sweep volume improvements: {report['b2']['stim_biased_schedule_sweep'].get('improved_volume_count')}",
            f"- Stim biased schedule sweep max decoder runtime / shot: {report['b2']['stim_biased_schedule_sweep'].get('max_decoder_runtime_seconds_per_shot')}",
            f"- Stim biased schedule sweep result exists: {report['b2']['stim_biased_schedule_sweep'].get('result_exists')}",
            f"- Same-hardware schedule status: {report['b2']['same_hardware_schedule_candidate'].get('status')}",
            f"- Same-hardware schedule configurations / shots: {report['b2']['same_hardware_schedule_candidate'].get('configurations')} / {report['b2']['same_hardware_schedule_candidate'].get('total_shots')}",
            f"- Same-hardware schedule baseline/candidate met: {report['b2']['same_hardware_schedule_candidate'].get('baseline_met_count')} / {report['b2']['same_hardware_schedule_candidate'].get('candidate_met_count')}",
            f"- Same-hardware schedule candidate-only target hits: {report['b2']['same_hardware_schedule_candidate'].get('candidate_only_meets_target_count')}",
            f"- Same-hardware schedule volume improvements / max reduction: {report['b2']['same_hardware_schedule_candidate'].get('improved_volume_count')} / {report['b2']['same_hardware_schedule_candidate'].get('max_volume_reduction')}",
            f"- Same-hardware schedule new-code/threshold/device claims: {report['b2']['same_hardware_schedule_candidate'].get('new_code_claimed')} / {report['b2']['same_hardware_schedule_candidate'].get('threshold_claimed')} / {report['b2']['same_hardware_schedule_candidate'].get('calibrated_device_claimed')}",
            f"- Same-hardware schedule result exists: {report['b2']['same_hardware_schedule_candidate'].get('result_exists')}",
            f"- Same-hardware robustness status: {report['b2']['same_hardware_schedule_robustness'].get('status')}",
            f"- Same-hardware robustness configurations / shots: {report['b2']['same_hardware_schedule_robustness'].get('configurations')} / {report['b2']['same_hardware_schedule_robustness'].get('total_shots')}",
            f"- Same-hardware robustness profiles / comparisons: {report['b2']['same_hardware_schedule_robustness'].get('profile_count')} / {report['b2']['same_hardware_schedule_robustness'].get('target_comparisons')}",
            f"- Same-hardware robustness improved rows aggressive/non-aggressive: {report['b2']['same_hardware_schedule_robustness'].get('total_aggressive_improved_volume_rows')} / {report['b2']['same_hardware_schedule_robustness'].get('total_non_aggressive_improved_volume_rows')}",
            f"- Same-hardware robustness aggressive-only dependence: {report['b2']['same_hardware_schedule_robustness'].get('positive_signal_depends_on_aggressive_schedule')}",
            f"- Same-hardware robustness new-code/threshold/device claims: {report['b2']['same_hardware_schedule_robustness'].get('new_code_claimed')} / {report['b2']['same_hardware_schedule_robustness'].get('threshold_claimed')} / {report['b2']['same_hardware_schedule_robustness'].get('calibrated_device_claimed')}",
            f"- Same-hardware robustness result exists: {report['b2']['same_hardware_schedule_robustness'].get('result_exists')}",
            f"- Reduced-round artifact boundary status: {report['b2']['reduced_round_artifact_boundary'].get('status')}",
            f"- Reduced-round artifact boundary candidate/robust improved rows: {report['b2']['reduced_round_artifact_boundary'].get('candidate_improved_volume_count')} / {report['b2']['reduced_round_artifact_boundary'].get('robustness_improved_volume_count')}",
            f"- Reduced-round artifact boundary robust non-aggressive rows: {report['b2']['reduced_round_artifact_boundary'].get('robustness_non_aggressive_improved_volume_count')}",
            f"- Reduced-round artifact boundary aggressive/distance-3/one-round flags: {report['b2']['reduced_round_artifact_boundary'].get('all_robustness_improvements_aggressive')} / {report['b2']['reduced_round_artifact_boundary'].get('all_robustness_improvements_distance_3')} / {report['b2']['reduced_round_artifact_boundary'].get('all_robustness_improvements_one_round')}",
            f"- Reduced-round artifact boundary small-distance/aggressive dependency: {report['b2']['reduced_round_artifact_boundary'].get('small_distance_artifact_flag')} / {report['b2']['reduced_round_artifact_boundary'].get('aggressive_schedule_dependency_flag')}",
            f"- Reduced-round artifact boundary new-code/threshold/device claims: {report['b2']['reduced_round_artifact_boundary'].get('new_code_claimed')} / {report['b2']['reduced_round_artifact_boundary'].get('threshold_claimed')} / {report['b2']['reduced_round_artifact_boundary'].get('calibrated_device_claimed')}",
            f"- Reduced-round artifact boundary validation errors: {report['b2']['reduced_round_artifact_boundary'].get('validation_error_count')}",
            f"- Reduced-round artifact boundary result/markdown exists: {report['b2']['reduced_round_artifact_boundary'].get('result_exists')} / {report['b2']['reduced_round_artifact_boundary'].get('markdown_exists')}",
            f"- Leakage-flagged erasure boundary status: {report['b2']['leakage_flagged_erasure_boundary'].get('status')}",
            f"- Leakage-flagged erasure boundary configurations: {report['b2']['leakage_flagged_erasure_boundary'].get('configuration_count')}",
            f"- Leakage-flagged erasure boundary baseline/candidate met: {report['b2']['leakage_flagged_erasure_boundary'].get('baseline_met_count')} / {report['b2']['leakage_flagged_erasure_boundary'].get('candidate_met_count')}",
            f"- Leakage-flagged erasure boundary improved rows / d5-d7 rows: {report['b2']['leakage_flagged_erasure_boundary'].get('improved_volume_count')} / {report['b2']['leakage_flagged_erasure_boundary'].get('distance_5_7_improved_count')}",
            f"- Leakage-flagged erasure boundary high-efficiency d5-d7 rows: {report['b2']['leakage_flagged_erasure_boundary'].get('high_efficiency_distance_5_7_improved_count')}",
            f"- Leakage-flagged erasure boundary max/mean volume reduction: {report['b2']['leakage_flagged_erasure_boundary'].get('max_volume_reduction')} / {report['b2']['leakage_flagged_erasure_boundary'].get('mean_volume_reduction_on_improved')}",
            f"- Leakage-flagged erasure boundary non-aggressive/reduced-round flags: {report['b2']['leakage_flagged_erasure_boundary'].get('non_aggressive_mechanism')} / {report['b2']['leakage_flagged_erasure_boundary'].get('reduced_rounds_used')}",
            f"- Leakage-flagged erasure boundary new-code/threshold/device/circuit claims: {report['b2']['leakage_flagged_erasure_boundary'].get('new_code_claimed')} / {report['b2']['leakage_flagged_erasure_boundary'].get('threshold_claimed')} / {report['b2']['leakage_flagged_erasure_boundary'].get('calibrated_device_claimed')} / {report['b2']['leakage_flagged_erasure_boundary'].get('circuit_level_decoder_claimed')}",
            f"- Leakage-flagged erasure boundary validation errors: {report['b2']['leakage_flagged_erasure_boundary'].get('validation_error_count')}",
            f"- Leakage-flagged erasure boundary result/markdown exists: {report['b2']['leakage_flagged_erasure_boundary'].get('result_exists')} / {report['b2']['leakage_flagged_erasure_boundary'].get('markdown_exists')}",
            f"- Stim heralded-erasure stress status: {report['b2']['stim_heralded_erasure_stress'].get('status')}",
            f"- Stim heralded-erasure stress configurations / shots: {report['b2']['stim_heralded_erasure_stress'].get('configuration_count')} / {report['b2']['stim_heralded_erasure_stress'].get('total_shots')}",
            f"- Stim heralded-erasure stress baseline/candidate met: {report['b2']['stim_heralded_erasure_stress'].get('baseline_met_count')} / {report['b2']['stim_heralded_erasure_stress'].get('candidate_met_count')}",
            f"- Stim heralded-erasure stress candidate-only hits: {report['b2']['stim_heralded_erasure_stress'].get('candidate_only_meets_target_count')}",
            f"- Stim heralded-erasure stress improved rows / d5-d7 rows: {report['b2']['stim_heralded_erasure_stress'].get('improved_volume_count')} / {report['b2']['stim_heralded_erasure_stress'].get('distance_5_7_improved_count')}",
            f"- Stim heralded-erasure stress max/mean volume reduction: {report['b2']['stim_heralded_erasure_stress'].get('max_volume_reduction')} / {report['b2']['stim_heralded_erasure_stress'].get('mean_volume_reduction_on_improved')}",
            f"- Stim heralded-erasure stress reduced-round/d3 flags: {report['b2']['stim_heralded_erasure_stress'].get('reduced_rounds_used')} / {report['b2']['stim_heralded_erasure_stress'].get('distance_3_candidate_used')}",
            f"- Stim heralded-erasure stress new-code/threshold/device/full-decoder/shot-conditioned claims: {report['b2']['stim_heralded_erasure_stress'].get('new_code_claimed')} / {report['b2']['stim_heralded_erasure_stress'].get('threshold_claimed')} / {report['b2']['stim_heralded_erasure_stress'].get('calibrated_device_claimed')} / {report['b2']['stim_heralded_erasure_stress'].get('full_physical_leakage_decoder_claimed')} / {report['b2']['stim_heralded_erasure_stress'].get('shot_conditioned_erasure_decoder_claimed')}",
            f"- Stim heralded-erasure stress validation errors: {report['b2']['stim_heralded_erasure_stress'].get('validation_error_count')}",
            f"- Stim heralded-erasure stress result/markdown exists: {report['b2']['stim_heralded_erasure_stress'].get('result_exists')} / {report['b2']['stim_heralded_erasure_stress'].get('markdown_exists')}",
            f"- Heralded-erasure false-positive stress status: {report['b2']['heralded_erasure_false_positive_stress'].get('status')}",
            f"- Heralded-erasure false-positive stress configurations / shots: {report['b2']['heralded_erasure_false_positive_stress'].get('configuration_count')} / {report['b2']['heralded_erasure_false_positive_stress'].get('total_shots')}",
            f"- Heralded-erasure false-positive stress candidate met / improved rows: {report['b2']['heralded_erasure_false_positive_stress'].get('candidate_met_count')} / {report['b2']['heralded_erasure_false_positive_stress'].get('improved_volume_count')}",
            f"- Heralded-erasure false-positive stress positive-fp improved / d5-d7 rows: {report['b2']['heralded_erasure_false_positive_stress'].get('false_positive_positive_improved_volume_count')} / {report['b2']['heralded_erasure_false_positive_stress'].get('false_positive_positive_d5_d7_improved_count')}",
            f"- Heralded-erasure false-positive stress fp=0.001 / fp=0.003 improved rows: {report['b2']['heralded_erasure_false_positive_stress'].get('fp_0p001_improved_volume_count')} / {report['b2']['heralded_erasure_false_positive_stress'].get('fp_0p003_improved_volume_count')}",
            f"- Heralded-erasure false-positive stress max/mean volume reduction: {report['b2']['heralded_erasure_false_positive_stress'].get('max_volume_reduction')} / {report['b2']['heralded_erasure_false_positive_stress'].get('mean_volume_reduction_on_improved')}",
            f"- Heralded-erasure false-positive stress new-code/threshold/device/full-decoder/shot-conditioned claims: {report['b2']['heralded_erasure_false_positive_stress'].get('new_code_claimed')} / {report['b2']['heralded_erasure_false_positive_stress'].get('threshold_claimed')} / {report['b2']['heralded_erasure_false_positive_stress'].get('calibrated_device_claimed')} / {report['b2']['heralded_erasure_false_positive_stress'].get('full_physical_leakage_decoder_claimed')} / {report['b2']['heralded_erasure_false_positive_stress'].get('shot_conditioned_erasure_decoder_claimed')}",
            f"- Heralded-erasure false-positive stress validation errors: {report['b2']['heralded_erasure_false_positive_stress'].get('validation_error_count')}",
            f"- Heralded-erasure false-positive stress result/markdown exists: {report['b2']['heralded_erasure_false_positive_stress'].get('result_exists')} / {report['b2']['heralded_erasure_false_positive_stress'].get('markdown_exists')}",
            f"- Shot-conditioned erasure boundary status: {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('status')}",
            f"- Shot-conditioned erasure boundary source positive-fp d5/d7 rows: {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('source_positive_fp_d5_d7_improved_rows')}",
            f"- Shot-conditioned erasure boundary profiles / evaluated rows: {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('calibration_profile_count')} / {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('evaluated_profile_rows')}",
            f"- Shot-conditioned erasure boundary surviving profiles / max rows: {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('profiles_with_surviving_rows')} / {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('max_surviving_d5_d7_improved_rows_in_profile')}",
            f"- Shot-conditioned erasure boundary strict surviving / all-profile robust: {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('strict_high_purity_surviving_rows')} / {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('robust_all_profile_survival')}",
            f"- Shot-conditioned erasure boundary calibration model / production decoder / threshold / hardware: {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('shot_conditioned_calibration_model_performed')} / {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('production_decoder_claimed')} / {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('threshold_claimed')} / {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('hardware_result_claimed')}",
            f"- Shot-conditioned erasure boundary validation errors: {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('validation_error_count')}",
            f"- Shot-conditioned erasure boundary result/markdown exists: {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('result_exists')} / {report['b2']['shot_conditioned_erasure_decoder_boundary'].get('markdown_exists')}",
            f"- Posterior-risk ledger status: {report['b2']['posterior_weighted_decoder_risk_ledger'].get('status')}",
            f"- Posterior-risk ledger budgets / evaluated rows: {report['b2']['posterior_weighted_decoder_risk_ledger'].get('risk_budget_count')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('evaluated_budget_profile_rows')}",
            f"- Posterior-risk ledger raw / mild / nominal / conservative / strict survivors: {report['b2']['posterior_weighted_decoder_risk_ledger'].get('source_raw_surviving_d5_d7_rows')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('mild_adjusted_surviving_d5_d7_rows')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('nominal_adjusted_surviving_d5_d7_rows')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('conservative_adjusted_surviving_d5_d7_rows')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('strict_adjusted_surviving_d5_d7_rows')}",
            f"- Posterior-risk ledger strict high-purity / all-profile robust: {report['b2']['posterior_weighted_decoder_risk_ledger'].get('strict_high_purity_adjusted_survivors')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('robust_all_profile_adjusted_survival')}",
            f"- Posterior-risk ledger conservative / strict max adjusted reduction: {report['b2']['posterior_weighted_decoder_risk_ledger'].get('conservative_max_decoder_adjusted_reduction')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('strict_max_decoder_adjusted_reduction')}",
            f"- Posterior-risk ledger risk model / circuit decoder / production decoder / threshold / hardware: {report['b2']['posterior_weighted_decoder_risk_ledger'].get('posterior_weighted_decoder_risk_model_performed')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('circuit_level_decoder_claimed')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('production_decoder_claimed')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('threshold_claimed')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('hardware_result_claimed')}",
            f"- Posterior-risk ledger validation errors: {report['b2']['posterior_weighted_decoder_risk_ledger'].get('validation_error_count')}",
            f"- Posterior-risk ledger result/markdown exists: {report['b2']['posterior_weighted_decoder_risk_ledger'].get('result_exists')} / {report['b2']['posterior_weighted_decoder_risk_ledger'].get('markdown_exists')}",
            f"- Decoder input contract status: {report['b2']['decoder_input_contract_feasibility_gate'].get('status')}",
            f"- Decoder input contract available/missing inputs: {report['b2']['decoder_input_contract_feasibility_gate'].get('available_contract_input_count')} / {report['b2']['decoder_input_contract_feasibility_gate'].get('missing_contract_input_count')}",
            f"- Decoder input contract gates passed/failed/critical failed: {report['b2']['decoder_input_contract_feasibility_gate'].get('passed_gate_count')} / {report['b2']['decoder_input_contract_feasibility_gate'].get('failed_gate_count')} / {report['b2']['decoder_input_contract_feasibility_gate'].get('failed_critical_gate_count')}",
            f"- Decoder input contract raw/conservative/strict survivors: {report['b2']['decoder_input_contract_feasibility_gate'].get('source_raw_surviving_d5_d7_rows')} / {report['b2']['decoder_input_contract_feasibility_gate'].get('conservative_adjusted_surviving_d5_d7_rows')} / {report['b2']['decoder_input_contract_feasibility_gate'].get('strict_adjusted_surviving_d5_d7_rows')}",
            f"- Decoder input contract satisfied / demotion recommended: {report['b2']['decoder_input_contract_feasibility_gate'].get('decoder_contract_satisfied')} / {report['b2']['decoder_input_contract_feasibility_gate'].get('demotion_recommended_until_decoder_or_calibration')}",
            f"- Decoder input contract circuit decoder / production decoder / threshold / hardware: {report['b2']['decoder_input_contract_feasibility_gate'].get('circuit_level_decoder_claimed')} / {report['b2']['decoder_input_contract_feasibility_gate'].get('production_decoder_claimed')} / {report['b2']['decoder_input_contract_feasibility_gate'].get('threshold_claimed')} / {report['b2']['decoder_input_contract_feasibility_gate'].get('hardware_result_claimed')}",
            f"- Decoder input contract validation errors: {report['b2']['decoder_input_contract_feasibility_gate'].get('validation_error_count')}",
            f"- Decoder input contract result/markdown exists: {report['b2']['decoder_input_contract_feasibility_gate'].get('result_exists')} / {report['b2']['decoder_input_contract_feasibility_gate'].get('markdown_exists')}",
            f"- Per-shot trace packet status: {report['b2']['per_shot_decoder_trace_packet'].get('status')}",
            f"- Per-shot trace packet challenges / shots each / total traces: {report['b2']['per_shot_decoder_trace_packet'].get('challenge_count')} / {report['b2']['per_shot_decoder_trace_packet'].get('shots_per_challenge')} / {report['b2']['per_shot_decoder_trace_packet'].get('total_shot_traces')}",
            f"- Per-shot trace packet failures / max detectors / synthetic flags: {report['b2']['per_shot_decoder_trace_packet'].get('total_logical_failures')} / {report['b2']['per_shot_decoder_trace_packet'].get('max_detector_count')} / {report['b2']['per_shot_decoder_trace_packet'].get('total_synthetic_flag_events')}",
            f"- Per-shot trace packet detector bits / observables / synthetic flags persisted: {report['b2']['per_shot_decoder_trace_packet'].get('per_shot_detector_bitstrings_persisted')} / {report['b2']['per_shot_decoder_trace_packet'].get('stim_observable_bitstrings_persisted')} / {report['b2']['per_shot_decoder_trace_packet'].get('synthetic_detector_tick_flag_events_persisted')}",
            f"- Per-shot trace packet posterior injection / real calibrated flags: {report['b2']['per_shot_decoder_trace_packet'].get('posterior_likelihood_decoder_injection_performed')} / {report['b2']['per_shot_decoder_trace_packet'].get('real_hardware_or_calibrated_flag_events')}",
            f"- Per-shot trace packet circuit decoder / production decoder / threshold / hardware: {report['b2']['per_shot_decoder_trace_packet'].get('circuit_level_decoder_claimed')} / {report['b2']['per_shot_decoder_trace_packet'].get('production_decoder_claimed')} / {report['b2']['per_shot_decoder_trace_packet'].get('threshold_claimed')} / {report['b2']['per_shot_decoder_trace_packet'].get('hardware_result_claimed')}",
            f"- Per-shot trace packet validation errors: {report['b2']['per_shot_decoder_trace_packet'].get('validation_error_count')}",
            f"- Per-shot trace packet result/markdown exists: {report['b2']['per_shot_decoder_trace_packet'].get('result_exists')} / {report['b2']['per_shot_decoder_trace_packet'].get('markdown_exists')}",
            f"- Posterior injection gate status: {report['b2']['posterior_likelihood_decoder_injection_gate'].get('status')}",
            f"- Posterior injection gate challenges / profiles / shots: {report['b2']['posterior_likelihood_decoder_injection_gate'].get('source_challenge_count')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('injection_profile_count')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('total_profile_shots')}",
            f"- Posterior injection gate best profile / injected failures / delta: {report['b2']['posterior_likelihood_decoder_injection_gate'].get('best_profile')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('best_profile_injected_failures')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('best_profile_failure_delta')}",
            f"- Posterior injection gate fixed / introduced / changed predictions: {report['b2']['posterior_likelihood_decoder_injection_gate'].get('best_profile_fixed_failures')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('best_profile_introduced_failures')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('best_profile_changed_predictions')}",
            f"- Posterior injection gate injection / synthetic flags / calibrated data / hardware: {report['b2']['posterior_likelihood_decoder_injection_gate'].get('posterior_likelihood_injection_performed')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('synthetic_flag_likelihoods_consumed')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('calibrated_flag_data_used')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('real_hardware_trace_used')}",
            f"- Posterior injection gate improvement / non-regression / demotion: {report['b2']['posterior_likelihood_decoder_injection_gate'].get('improvement_gate_passed')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('all_challenge_nonregression_gate_passed')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('route_demotion_recommended')}",
            f"- Posterior injection gate circuit decoder / production decoder / threshold / hardware: {report['b2']['posterior_likelihood_decoder_injection_gate'].get('circuit_level_decoder_claimed')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('production_decoder_claimed')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('threshold_claimed')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('hardware_result_claimed')}",
            f"- Posterior injection gate validation errors: {report['b2']['posterior_likelihood_decoder_injection_gate'].get('validation_error_count')}",
            f"- Posterior injection gate result/markdown exists: {report['b2']['posterior_likelihood_decoder_injection_gate'].get('result_exists')} / {report['b2']['posterior_likelihood_decoder_injection_gate'].get('markdown_exists')}",
            f"- DEM edge semantics gate status: {report['b2']['dem_informed_detector_edge_semantics_gate'].get('status')}",
            f"- DEM edge semantics gate challenges / profiles / shots: {report['b2']['dem_informed_detector_edge_semantics_gate'].get('source_challenge_count')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('semantic_profile_count')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('total_profile_shots')}",
            f"- DEM edge semantics gate best profile / injected failures / delta: {report['b2']['dem_informed_detector_edge_semantics_gate'].get('best_profile')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('best_profile_injected_failures')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('best_profile_failure_delta')}",
            f"- DEM edge semantics gate fixed / introduced / changed predictions: {report['b2']['dem_informed_detector_edge_semantics_gate'].get('best_profile_fixed_failures')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('best_profile_introduced_failures')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('best_profile_changed_predictions')}",
            f"- DEM edge semantics gate aggressive injected / introduced failures: {report['b2']['dem_informed_detector_edge_semantics_gate'].get('aggressive_profile_injected_failures')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('aggressive_profile_introduced_failures')}",
            f"- DEM edge semantics gate DEM semantics / synthetic flags / calibrated data / hardware: {report['b2']['dem_informed_detector_edge_semantics_gate'].get('dem_edge_probability_semantics_performed')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('synthetic_flag_likelihoods_consumed')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('calibrated_flag_data_used')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('real_hardware_trace_used')}",
            f"- DEM edge semantics gate improvement / non-regression / demotion: {report['b2']['dem_informed_detector_edge_semantics_gate'].get('improvement_gate_passed')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('all_challenge_nonregression_gate_passed')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('route_demotion_recommended')}",
            f"- DEM edge semantics gate production decoder / threshold / hardware: {report['b2']['dem_informed_detector_edge_semantics_gate'].get('production_decoder_claimed')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('threshold_claimed')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('hardware_result_claimed')}",
            f"- DEM edge semantics gate validation errors: {report['b2']['dem_informed_detector_edge_semantics_gate'].get('validation_error_count')}",
            f"- DEM edge semantics gate result/markdown exists: {report['b2']['dem_informed_detector_edge_semantics_gate'].get('result_exists')} / {report['b2']['dem_informed_detector_edge_semantics_gate'].get('markdown_exists')}",
            f"- Hardware-like leakage gate status: {report['b2']['hardware_like_leakage_model_gate'].get('status')}",
            f"- Hardware-like leakage gate challenges / profiles / shots / holdout shots: {report['b2']['hardware_like_leakage_model_gate'].get('source_challenge_count')} / {report['b2']['hardware_like_leakage_model_gate'].get('observation_profile_count')} / {report['b2']['hardware_like_leakage_model_gate'].get('total_profile_shots')} / {report['b2']['hardware_like_leakage_model_gate'].get('holdout_profile_shots')}",
            f"- Hardware-like leakage gate best profile / injected failures / delta: {report['b2']['hardware_like_leakage_model_gate'].get('best_profile')} / {report['b2']['hardware_like_leakage_model_gate'].get('best_profile_injected_failures')} / {report['b2']['hardware_like_leakage_model_gate'].get('best_profile_failure_delta')}",
            f"- Hardware-like leakage gate holdout injected / delta / introduced: {report['b2']['hardware_like_leakage_model_gate'].get('best_profile_holdout_injected_failures')} / {report['b2']['hardware_like_leakage_model_gate'].get('best_profile_holdout_failure_delta')} / {report['b2']['hardware_like_leakage_model_gate'].get('best_profile_holdout_introduced_failures')}",
            f"- Hardware-like leakage gate model flags best / stress: {report['b2']['hardware_like_leakage_model_gate'].get('best_profile_model_flag_events')} / {report['b2']['hardware_like_leakage_model_gate'].get('stress_profile_model_flag_events')}",
            f"- Hardware-like leakage gate model / detector bits / synthetic fixture / calibrated data / hardware: {report['b2']['hardware_like_leakage_model_gate'].get('hardware_like_leakage_model_used')} / {report['b2']['hardware_like_leakage_model_gate'].get('detector_bitstrings_consumed')} / {report['b2']['hardware_like_leakage_model_gate'].get('synthetic_flag_fixture_consumed')} / {report['b2']['hardware_like_leakage_model_gate'].get('calibrated_flag_data_used')} / {report['b2']['hardware_like_leakage_model_gate'].get('real_hardware_trace_used')}",
            f"- Hardware-like leakage gate holdout improvement / non-regression / demotion: {report['b2']['hardware_like_leakage_model_gate'].get('holdout_improvement_gate_passed')} / {report['b2']['hardware_like_leakage_model_gate'].get('holdout_nonregression_gate_passed')} / {report['b2']['hardware_like_leakage_model_gate'].get('route_demotion_recommended')}",
            f"- Hardware-like leakage gate production decoder / threshold / hardware: {report['b2']['hardware_like_leakage_model_gate'].get('production_decoder_claimed')} / {report['b2']['hardware_like_leakage_model_gate'].get('threshold_claimed')} / {report['b2']['hardware_like_leakage_model_gate'].get('hardware_result_claimed')}",
            f"- Hardware-like leakage gate validation errors: {report['b2']['hardware_like_leakage_model_gate'].get('validation_error_count')}",
            f"- Hardware-like leakage gate result/markdown exists: {report['b2']['hardware_like_leakage_model_gate'].get('result_exists')} / {report['b2']['hardware_like_leakage_model_gate'].get('markdown_exists')}",
            "",
            "## B3 Resource Proxy Status",
            "",
            f"- Status: {report['b3']['resource_proxy'].get('status')}",
            f"- Molecules: {report['b3']['resource_proxy'].get('molecule_count')}",
            f"- Basis: {report['b3']['resource_proxy'].get('basis')}",
            f"- Proxy T-count reduction range: {report['b3']['resource_proxy'].get('proxy_t_count_reduction_range')}",
            f"- Result exists: {report['b3']['resource_proxy'].get('result_exists')}",
            f"- Quantum observable vs FCI status: {report['b3']['quantum_observable_fci_comparison'].get('status')}",
            f"- Quantum observable vs FCI instances/qasm: {report['b3']['quantum_observable_fci_comparison'].get('reaction_coordinate_instances')} / {report['b3']['quantum_observable_fci_comparison'].get('qasm_file_count')}",
            f"- Quantum observable vs FCI max qubits/controlled phases: {report['b3']['quantum_observable_fci_comparison'].get('max_total_qubits')} / {report['b3']['quantum_observable_fci_comparison'].get('max_controlled_phase_gates')}",
            f"- Quantum observable vs FCI beaten count: {report['b3']['quantum_observable_fci_comparison'].get('fci_denominator_beaten_count')}",
            f"- Quantum observable vs FCI advantage/reaction claims: {report['b3']['quantum_observable_fci_comparison'].get('quantum_advantage_claimed')} / {report['b3']['quantum_observable_fci_comparison'].get('reaction_dynamics_solution_claimed')}",
            f"- Quantum observable vs FCI validation errors: {report['b3']['quantum_observable_fci_comparison'].get('validation_error_count')}",
            f"- Quantum observable vs FCI result/markdown/qasm exists: {report['b3']['quantum_observable_fci_comparison'].get('result_exists')} / {report['b3']['quantum_observable_fci_comparison'].get('markdown_exists')} / {report['b3']['quantum_observable_fci_comparison'].get('qasm_directory_exists')}",
            f"- Hamiltonian Pauli mapper status: {report['b3']['hamiltonian_pauli_mapper_comparison'].get('status')}",
            f"- Hamiltonian Pauli mapper instances/qasm: {report['b3']['hamiltonian_pauli_mapper_comparison'].get('reaction_coordinate_instances')} / {report['b3']['hamiltonian_pauli_mapper_comparison'].get('qasm_file_count')}",
            f"- Hamiltonian Pauli mapper max qubits/Pauli terms: {report['b3']['hamiltonian_pauli_mapper_comparison'].get('max_total_qubits')} / {report['b3']['hamiltonian_pauli_mapper_comparison'].get('max_pauli_terms_after_cutoff')}",
            f"- Hamiltonian Pauli mapper max packet terms / shot floor: {report['b3']['hamiltonian_pauli_mapper_comparison'].get('max_measurement_packet_terms')} / {report['b3']['hamiltonian_pauli_mapper_comparison'].get('max_total_measurement_shot_floor')}",
            f"- Hamiltonian Pauli mapper state-prep/variance included: {report['b3']['hamiltonian_pauli_mapper_comparison'].get('state_preparation_cost_included')} / {report['b3']['hamiltonian_pauli_mapper_comparison'].get('observable_variance_estimate_included')}",
            f"- Hamiltonian Pauli mapper beaten count: {report['b3']['hamiltonian_pauli_mapper_comparison'].get('fci_denominator_beaten_count')}",
            f"- Hamiltonian Pauli mapper advantage/reaction claims: {report['b3']['hamiltonian_pauli_mapper_comparison'].get('quantum_advantage_claimed')} / {report['b3']['hamiltonian_pauli_mapper_comparison'].get('reaction_dynamics_solution_claimed')}",
            f"- Hamiltonian Pauli mapper validation errors: {report['b3']['hamiltonian_pauli_mapper_comparison'].get('validation_error_count')}",
            f"- Hamiltonian Pauli mapper result/markdown/qasm exists: {report['b3']['hamiltonian_pauli_mapper_comparison'].get('result_exists')} / {report['b3']['hamiltonian_pauli_mapper_comparison'].get('markdown_exists')} / {report['b3']['hamiltonian_pauli_mapper_comparison'].get('qasm_directory_exists')}",
            f"- Sampled Pauli confidence status: {report['b3']['sampled_pauli_estimator_confidence'].get('status')}",
            f"- Sampled Pauli confidence instances / z: {report['b3']['sampled_pauli_estimator_confidence'].get('reaction_coordinate_instances')} / {report['b3']['sampled_pauli_estimator_confidence'].get('confidence_z')}",
            f"- Sampled Pauli confidence max random terms / pilot shots: {report['b3']['sampled_pauli_estimator_confidence'].get('max_random_pauli_terms')} / {report['b3']['sampled_pauli_estimator_confidence'].get('max_pilot_total_shots')}",
            f"- Sampled Pauli confidence max Neyman shot floor: {report['b3']['sampled_pauli_estimator_confidence'].get('max_target_total_shot_floor_neyman')}",
            f"- Sampled Pauli confidence reduction range: {report['b3']['sampled_pauli_estimator_confidence'].get('min_shot_reduction_vs_upper_bound')} / {report['b3']['sampled_pauli_estimator_confidence'].get('max_shot_reduction_vs_upper_bound')}",
            f"- Sampled Pauli confidence all CIs contain exact HF energy: {report['b3']['sampled_pauli_estimator_confidence'].get('all_pilot_cis_contain_exact_energy')}",
            f"- Sampled Pauli confidence selected-CI included / FCI wins: {report['b3']['sampled_pauli_estimator_confidence'].get('selected_ci_or_larger_active_space_included')} / {report['b3']['sampled_pauli_estimator_confidence'].get('fci_denominator_beaten_count')}",
            f"- Sampled Pauli confidence advantage/reaction claims: {report['b3']['sampled_pauli_estimator_confidence'].get('quantum_advantage_claimed')} / {report['b3']['sampled_pauli_estimator_confidence'].get('reaction_dynamics_solution_claimed')}",
            f"- Sampled Pauli confidence validation errors: {report['b3']['sampled_pauli_estimator_confidence'].get('validation_error_count')}",
            f"- Sampled Pauli confidence result/markdown exists: {report['b3']['sampled_pauli_estimator_confidence'].get('result_exists')} / {report['b3']['sampled_pauli_estimator_confidence'].get('markdown_exists')}",
            f"- Selected-CI grouped Pauli status: {report['b3']['selected_ci_grouped_pauli_boundary'].get('status')}",
            f"- Selected-CI grouped Pauli rows / max orbitals / max spin qubits: {report['b3']['selected_ci_grouped_pauli_boundary'].get('selected_ci_larger_basis_rows')} / {report['b3']['selected_ci_grouped_pauli_boundary'].get('max_selected_ci_spatial_orbitals')} / {report['b3']['selected_ci_grouped_pauli_boundary'].get('max_selected_ci_spin_orbital_qubits')}",
            f"- Selected-CI grouped Pauli max determinant product / max QWC groups: {report['b3']['selected_ci_grouped_pauli_boundary'].get('max_selected_ci_determinant_product')} / {report['b3']['selected_ci_grouped_pauli_boundary'].get('max_qwc_group_count')}",
            f"- Selected-CI grouped Pauli packet reduction range: {report['b3']['selected_ci_grouped_pauli_boundary'].get('min_packet_reduction_vs_ungrouped')} / {report['b3']['selected_ci_grouped_pauli_boundary'].get('max_packet_reduction_vs_ungrouped')}",
            f"- Selected-CI grouped Pauli ansatz surcharge / denominator wins: {report['b3']['selected_ci_grouped_pauli_boundary'].get('max_ansatz_two_qubit_gate_executions_at_target')} / {report['b3']['selected_ci_grouped_pauli_boundary'].get('selected_ci_larger_basis_denominator_beaten_count')}",
            f"- Selected-CI grouped Pauli large-basis mapper / advantage claims: {report['b3']['selected_ci_grouped_pauli_boundary'].get('large_basis_quantum_mapper_included')} / {report['b3']['selected_ci_grouped_pauli_boundary'].get('quantum_advantage_claimed')}",
            f"- Selected-CI grouped Pauli validation errors: {report['b3']['selected_ci_grouped_pauli_boundary'].get('validation_error_count')}",
            f"- Selected-CI grouped Pauli result/markdown exists: {report['b3']['selected_ci_grouped_pauli_boundary'].get('result_exists')} / {report['b3']['selected_ci_grouped_pauli_boundary'].get('markdown_exists')}",
            f"- Larger-basis Hamiltonian mapper status: {report['b3']['larger_basis_hamiltonian_mapper'].get('status')}",
            f"- Larger-basis Hamiltonian mapper included / same denominator basis: {report['b3']['larger_basis_hamiltonian_mapper'].get('larger_basis_quantum_mapper_included')} / {report['b3']['larger_basis_hamiltonian_mapper'].get('same_basis_as_selected_ci_denominator')}",
            f"- Larger-basis Hamiltonian mapper max qubits / Pauli terms: {report['b3']['larger_basis_hamiltonian_mapper'].get('max_total_qubits')} / {report['b3']['larger_basis_hamiltonian_mapper'].get('max_pauli_terms_after_cutoff')}",
            f"- Larger-basis Hamiltonian mapper max buckets / Neyman shots: {report['b3']['larger_basis_hamiltonian_mapper'].get('max_conservative_same_basis_bucket_count')} / {report['b3']['larger_basis_hamiltonian_mapper'].get('max_neyman_target_total_shot_floor')}",
            f"- Larger-basis Hamiltonian mapper ansatz executions / denominator wins: {report['b3']['larger_basis_hamiltonian_mapper'].get('max_ansatz_two_qubit_gate_executions_at_neyman_target')} / {report['b3']['larger_basis_hamiltonian_mapper'].get('selected_ci_larger_basis_denominator_beaten_count')}",
            f"- Larger-basis Hamiltonian mapper advantage/reaction claims: {report['b3']['larger_basis_hamiltonian_mapper'].get('quantum_advantage_claimed')} / {report['b3']['larger_basis_hamiltonian_mapper'].get('reaction_dynamics_solution_claimed')}",
            f"- Larger-basis Hamiltonian mapper validation errors: {report['b3']['larger_basis_hamiltonian_mapper'].get('validation_error_count')}",
            f"- Larger-basis Hamiltonian mapper result/markdown exists: {report['b3']['larger_basis_hamiltonian_mapper'].get('result_exists')} / {report['b3']['larger_basis_hamiltonian_mapper'].get('markdown_exists')}",
            f"- Larger-basis QWC grouping status: {report['b3']['larger_basis_qwc_grouping'].get('status')}",
            f"- Larger-basis QWC grouping included / algorithm: {report['b3']['larger_basis_qwc_grouping'].get('qwc_grouping_included')} / {report['b3']['larger_basis_qwc_grouping'].get('qwc_grouping_algorithm')}",
            f"- Larger-basis QWC grouping max previous buckets / QWC groups: {report['b3']['larger_basis_qwc_grouping'].get('max_previous_conservative_same_basis_bucket_count')} / {report['b3']['larger_basis_qwc_grouping'].get('max_qwc_group_count')}",
            f"- Larger-basis QWC grouping reduction range: {report['b3']['larger_basis_qwc_grouping'].get('min_qwc_reduction_vs_previous_bucket_count')} / {report['b3']['larger_basis_qwc_grouping'].get('max_qwc_reduction_vs_previous_bucket_count')}",
            f"- Larger-basis QWC grouping shot-floor reduced / denominator wins: {report['b3']['larger_basis_qwc_grouping'].get('neyman_shot_floor_reduced_by_grouping')} / {report['b3']['larger_basis_qwc_grouping'].get('selected_ci_larger_basis_denominator_beaten_count')}",
            f"- Larger-basis QWC grouping advantage/reaction claims: {report['b3']['larger_basis_qwc_grouping'].get('quantum_advantage_claimed')} / {report['b3']['larger_basis_qwc_grouping'].get('reaction_dynamics_solution_claimed')}",
            f"- Larger-basis QWC grouping validation errors: {report['b3']['larger_basis_qwc_grouping'].get('validation_error_count')}",
            f"- Larger-basis QWC grouping result/markdown exists: {report['b3']['larger_basis_qwc_grouping'].get('result_exists')} / {report['b3']['larger_basis_qwc_grouping'].get('markdown_exists')}",
            f"- Grouped covariance shot-floor status: {report['b3']['grouped_covariance_shot_floor'].get('status')}",
            f"- Grouped covariance model: {report['b3']['grouped_covariance_shot_floor'].get('covariance_model')}",
            f"- Grouped covariance max previous/grouped shot floor: {report['b3']['grouped_covariance_shot_floor'].get('max_previous_independent_term_neyman_shot_floor')} / {report['b3']['grouped_covariance_shot_floor'].get('max_grouped_covariance_shot_floor')}",
            f"- Grouped covariance reduction range: {report['b3']['grouped_covariance_shot_floor'].get('min_grouped_covariance_reduction_vs_previous_independent_floor')} / {report['b3']['grouped_covariance_shot_floor'].get('max_grouped_covariance_reduction_vs_previous_independent_floor')}",
            f"- Grouped covariance max pairs / ansatz executions: {report['b3']['grouped_covariance_shot_floor'].get('max_nonzero_covariance_pair_count')} / {report['b3']['grouped_covariance_shot_floor'].get('max_ansatz_two_qubit_gate_executions_at_grouped_covariance_target')}",
            f"- Grouped covariance denominator wins / advantage claims: {report['b3']['grouped_covariance_shot_floor'].get('selected_ci_larger_basis_denominator_beaten_count')} / {report['b3']['grouped_covariance_shot_floor'].get('quantum_advantage_claimed')}",
            f"- Grouped covariance validation errors: {report['b3']['grouped_covariance_shot_floor'].get('validation_error_count')}",
            f"- Grouped covariance result/markdown exists: {report['b3']['grouped_covariance_shot_floor'].get('result_exists')} / {report['b3']['grouped_covariance_shot_floor'].get('markdown_exists')}",
            f"- Chemical prep derivative status: {report['b3']['chemical_state_prep_derivative_boundary'].get('status')}",
            f"- Chemical prep derivative propagation / sampled covariance: {report['b3']['chemical_state_prep_derivative_boundary'].get('derivative_error_propagation_included')} / {report['b3']['chemical_state_prep_derivative_boundary'].get('sampled_chemical_state_covariance_included')}",
            f"- Chemical prep max source/derivative shot floor: {report['b3']['chemical_state_prep_derivative_boundary'].get('max_source_grouped_covariance_shot_floor')} / {report['b3']['chemical_state_prep_derivative_boundary'].get('max_three_point_derivative_total_shot_floor')}",
            f"- Chemical prep derivative inflation range: {report['b3']['chemical_state_prep_derivative_boundary'].get('min_derivative_shot_floor_inflation_vs_center_energy_floor')} / {report['b3']['chemical_state_prep_derivative_boundary'].get('max_derivative_shot_floor_inflation_vs_center_energy_floor')}",
            f"- Chemical prep UCCSD/ADAPT/adiabatic 2Q prep max: {report['b3']['chemical_state_prep_derivative_boundary'].get('max_uccsd_two_qubit_gates_per_preparation')} / {report['b3']['chemical_state_prep_derivative_boundary'].get('max_adapt_two_qubit_gates_per_preparation')} / {report['b3']['chemical_state_prep_derivative_boundary'].get('max_adiabatic_two_qubit_gates_per_preparation')}",
            f"- Chemical prep denominator wins / advantage claims: {report['b3']['chemical_state_prep_derivative_boundary'].get('selected_ci_larger_basis_denominator_beaten_count')} / {report['b3']['chemical_state_prep_derivative_boundary'].get('quantum_advantage_claimed')}",
            f"- Chemical prep validation errors: {report['b3']['chemical_state_prep_derivative_boundary'].get('validation_error_count')}",
            f"- Chemical prep result/markdown exists: {report['b3']['chemical_state_prep_derivative_boundary'].get('result_exists')} / {report['b3']['chemical_state_prep_derivative_boundary'].get('markdown_exists')}",
            f"- Compiled UCC/ADAPT covariance pilot status: {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('status')}",
            f"- Compiled UCC/ADAPT pilot molecule / groups / basis cap: {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('pilot_molecule')} / {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('pilot_group_count')} / {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('pilot_max_basis_weight')}",
            f"- Compiled UCC/ADAPT sampled covariance / optimizer accounting: {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('pilot_sampled_covariance_included')} / {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('optimizer_loop_shot_accounting_included')}",
            f"- Compiled UCC/ADAPT pilot variance error mean/max: {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('pilot_mean_relative_variance_error')} / {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('pilot_max_relative_variance_error')}",
            f"- Compiled UCC/ADAPT HF/compiled center floors: {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('source_hf_center_grouped_covariance_shot_floor')} / {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('compiled_state_center_grouped_covariance_shot_floor')}",
            f"- Compiled UCC/ADAPT derivative floor / optimizer shots: {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('compiled_state_three_point_derivative_shot_floor')} / {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('optimizer_loop_total_shots')}",
            f"- Compiled UCC/ADAPT denominator wins / advantage claims: {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('selected_ci_larger_basis_denominator_beaten_count')} / {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('quantum_advantage_claimed')}",
            f"- Compiled UCC/ADAPT validation errors: {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('validation_error_count')}",
            f"- Compiled UCC/ADAPT result/markdown exists: {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('result_exists')} / {report['b3']['compiled_ucc_adapt_covariance_pilot'].get('markdown_exists')}",
            f"- Cross-molecule UCC/ADAPT pressure status: {report['b3']['cross_molecule_ucc_adapt_pressure'].get('status')}",
            f"- Cross-molecule pressure instances / sampled groups: {report['b3']['cross_molecule_ucc_adapt_pressure'].get('pressure_instances')} / {report['b3']['cross_molecule_ucc_adapt_pressure'].get('pilot_group_count_total')}",
            f"- Cross-molecule pressure variance error mean/max: {report['b3']['cross_molecule_ucc_adapt_pressure'].get('pilot_mean_relative_variance_error_across_molecules')} / {report['b3']['cross_molecule_ucc_adapt_pressure'].get('pilot_max_relative_variance_error_across_molecules')}",
            f"- Cross-molecule pressure optimizer shots / 2Q lower bound: {report['b3']['cross_molecule_ucc_adapt_pressure'].get('max_optimizer_loop_total_shots_lower_bound')} / {report['b3']['cross_molecule_ucc_adapt_pressure'].get('max_optimizer_loop_two_qubit_executions_lower_bound')}",
            f"- Cross-molecule pressure demotion recommendation: {report['b3']['cross_molecule_ucc_adapt_pressure'].get('demotion_recommended')} / {report['b3']['cross_molecule_ucc_adapt_pressure'].get('b3_status_recommendation')}",
            f"- Cross-molecule pressure validation errors: {report['b3']['cross_molecule_ucc_adapt_pressure'].get('validation_error_count')}",
            f"- Cross-molecule pressure result/markdown exists: {report['b3']['cross_molecule_ucc_adapt_pressure'].get('result_exists')} / {report['b3']['cross_molecule_ucc_adapt_pressure'].get('markdown_exists')}",
            "",
            "## B4 Trap Protocol Status",
            "",
            f"- Status: {report['b4']['trap_protocol'].get('status')}",
            f"- Model status: {report['b4']['trap_protocol'].get('model_status')}",
            f"- Configurations: {report['b4']['trap_protocol'].get('configuration_count')}",
            f"- Spoofing families tested: {report['b4']['trap_protocol'].get('spoofing_families_tested')}",
            f"- Spoofing families failing batch rule: {report['b4']['trap_protocol'].get('spoofing_families_failing_count')}",
            f"- Batch completeness range: {report['b4']['trap_protocol'].get('batch_completeness_range')}",
            f"- Result exists: {report['b4']['trap_protocol'].get('result_exists')}",
            f"- Circuit refresh status: {report['b4']['circuit_refresh_task'].get('status')}",
            f"- Circuit refresh configurations: {report['b4']['circuit_refresh_task'].get('configuration_count')}",
            f"- Circuit refresh honest completeness: {report['b4']['circuit_refresh_task'].get('minimum_honest_completeness')}",
            f"- Circuit refresh no-refresh high-leakage max soundness: {report['b4']['circuit_refresh_task'].get('none_high_leakage_max_soundness')}",
            f"- Circuit refresh best repaired high-leakage max soundness: {report['b4']['circuit_refresh_task'].get('best_repair_high_leakage_max_soundness')}",
            f"- Circuit refresh result/markdown exists: {report['b4']['circuit_refresh_task'].get('result_exists')} / {report['b4']['circuit_refresh_task'].get('markdown_exists')}",
            f"- OpenQASM 3 packet status: {report['b4']['openqasm3_randomized_measurement_packet'].get('status')}",
            f"- OpenQASM 3 packet circuits / max qubits: {report['b4']['openqasm3_randomized_measurement_packet'].get('circuit_file_count')} / {report['b4']['openqasm3_randomized_measurement_packet'].get('max_total_qubits')}",
            f"- OpenQASM 3 packet headers / Aer mismatches / honest completeness: {report['b4']['openqasm3_randomized_measurement_packet'].get('all_qasm3_headers_valid')} / {report['b4']['openqasm3_randomized_measurement_packet'].get('aer_semantic_mismatch_count')} / {report['b4']['openqasm3_randomized_measurement_packet'].get('minimum_aer_honest_completeness')}",
            f"- OpenQASM 3 packet hardware execution / advantage / BQP separation: {report['b4']['openqasm3_randomized_measurement_packet'].get('hardware_execution_performed')} / {report['b4']['openqasm3_randomized_measurement_packet'].get('quantum_advantage_claimed')} / {report['b4']['openqasm3_randomized_measurement_packet'].get('bqp_separation_claimed')}",
            f"- OpenQASM 3 packet result/markdown/directory exists: {report['b4']['openqasm3_randomized_measurement_packet'].get('result_exists')} / {report['b4']['openqasm3_randomized_measurement_packet'].get('markdown_exists')} / {report['b4']['openqasm3_randomized_measurement_packet'].get('qasm_directory_exists')}",
            f"- Public-QASM spoofer status: {report['b4']['public_qasm_packet_spoofer_gate'].get('status')}",
            f"- Public-QASM spoofer parsed circuits / prediction success: {report['b4']['public_qasm_packet_spoofer_gate'].get('parsed_circuit_count')} / {report['b4']['public_qasm_packet_spoofer_gate'].get('public_stabilizer_emulator_prediction_success_rate')}",
            f"- Public-QASM packet soundness rejected / late-bound private challenges required: {report['b4']['public_qasm_packet_spoofer_gate'].get('public_packet_contract_soundness_rejected')} / {report['b4']['public_qasm_packet_spoofer_gate'].get('late_bound_private_challenges_required')}",
            f"- Public-QASM spoofer hardware execution / advantage / BQP separation: {report['b4']['public_qasm_packet_spoofer_gate'].get('hardware_execution_performed')} / {report['b4']['public_qasm_packet_spoofer_gate'].get('quantum_advantage_claimed')} / {report['b4']['public_qasm_packet_spoofer_gate'].get('bqp_separation_claimed')}",
            f"- Public-QASM spoofer result/markdown exists: {report['b4']['public_qasm_packet_spoofer_gate'].get('result_exists')} / {report['b4']['public_qasm_packet_spoofer_gate'].get('markdown_exists')}",
            f"- Late-bound contract status: {report['b4']['late_bound_private_challenge_contract_gate'].get('status')}",
            f"- Late-bound public skeletons / hide private material: {report['b4']['late_bound_private_challenge_contract_gate'].get('public_skeleton_file_count')} / {report['b4']['late_bound_private_challenge_contract_gate'].get('public_skeletons_hide_private_material')}",
            f"- Late-bound deterministic data blocker / late-binding alone sufficient: {report['b4']['late_bound_private_challenge_contract_gate'].get('public_data_transcript_classically_predictable')} / {report['b4']['late_bound_private_challenge_contract_gate'].get('late_bound_private_challenge_alone_sufficient_for_soundness')}",
            f"- Late-bound gates passed/failed: {report['b4']['late_bound_private_challenge_contract_gate'].get('passed_gate_count')} / {report['b4']['late_bound_private_challenge_contract_gate'].get('failed_gate_count')}",
            f"- Late-bound contract result/markdown/skeleton-dir exists: {report['b4']['late_bound_private_challenge_contract_gate'].get('result_exists')} / {report['b4']['late_bound_private_challenge_contract_gate'].get('markdown_exists')} / {report['b4']['late_bound_private_challenge_contract_gate'].get('public_skeleton_directory_exists')}",
            f"- Non-stabilizer pilot status: {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('status')}",
            f"- Non-stabilizer pilot circuits / deterministic blocker removed: {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('circuit_count')} / {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('public_deterministic_transcript_blocker_removed')}",
            f"- Non-stabilizer pilot entropy / max output probability: {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('minimum_min_entropy_bits')} / {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('maximum_output_probability')}",
            f"- Non-stabilizer pilot gates passed/failed: {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('passed_gate_count')} / {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('failed_gate_count')}",
            f"- Non-stabilizer pilot hardware execution / advantage / BQP separation: {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('hardware_execution_performed')} / {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('quantum_advantage_claimed')} / {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('bqp_separation_claimed')}",
            f"- Non-stabilizer pilot result/markdown/directory exists: {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('result_exists')} / {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('markdown_exists')} / {report['b4']['nonstabilizer_late_bound_transcript_pilot'].get('nonstabilizer_pilot_directory_exists')}",
            f"- Support-spoofer gate status: {report['b4']['nonstabilizer_support_spoofer_gate'].get('status')}",
            f"- Support-spoofer circuits / spoofers / rows: {report['b4']['nonstabilizer_support_spoofer_gate'].get('circuit_count')} / {report['b4']['nonstabilizer_support_spoofer_gate'].get('spoofer_count')} / {report['b4']['nonstabilizer_support_spoofer_gate'].get('attack_row_count')}",
            f"- Support-spoofer exact success / support acceptance: {report['b4']['nonstabilizer_support_spoofer_gate'].get('max_exact_transcript_success_probability')} / {report['b4']['nonstabilizer_support_spoofer_gate'].get('max_support_acceptance_rate')}",
            f"- Support-spoofer support-only soundness rejected / exact blocker survives: {report['b4']['nonstabilizer_support_spoofer_gate'].get('support_only_verifier_soundness_rejected')} / {report['b4']['nonstabilizer_support_spoofer_gate'].get('deterministic_exact_transcript_blocker_survives')}",
            f"- Support-spoofer result/markdown exists: {report['b4']['nonstabilizer_support_spoofer_gate'].get('result_exists')} / {report['b4']['nonstabilizer_support_spoofer_gate'].get('markdown_exists')}",
            "",
            "## B5 Hubbard Embedding Status",
            "",
            f"- Status: {report['b5']['hubbard_embedding'].get('status')}",
            f"- Model status: {report['b5']['hubbard_embedding'].get('model_status')}",
            f"- Configurations: {report['b5']['hubbard_embedding'].get('configuration_count')}",
            f"- Exact Hilbert dimension range: {report['b5']['hubbard_embedding'].get('exact_hilbert_dimension_range')}",
            f"- Mean error/site by cluster size: {report['b5']['hubbard_embedding'].get('mean_error_per_site_by_cluster_size')}",
            f"- Result exists: {report['b5']['hubbard_embedding'].get('result_exists')}",
            f"- Boundary-field response status: {report['b5']['boundary_field_response_embedding'].get('status')}",
            f"- Boundary-field response instances: {report['b5']['boundary_field_response_embedding'].get('instance_count')}",
            f"- Boundary-field response mean/max relative error: {report['b5']['boundary_field_response_embedding'].get('mean_relative_response_error')} / {report['b5']['boundary_field_response_embedding'].get('max_relative_response_error')}",
            f"- Boundary-field exact/cluster max Hilbert dimension: {report['b5']['boundary_field_response_embedding'].get('max_exact_d5_hilbert_dimension')} / {report['b5']['boundary_field_response_embedding'].get('max_cluster_hilbert_dimension')}",
            f"- Boundary-field oracle tuned / quantum win claimed: {report['b5']['boundary_field_response_embedding'].get('oracle_tuned_boundary_field')} / {report['b5']['boundary_field_response_embedding'].get('quantum_response_win_claimed')}",
            f"- Boundary-field validation errors: {report['b5']['boundary_field_response_embedding'].get('validation_error_count')}",
            f"- Boundary-field result/markdown exists: {report['b5']['boundary_field_response_embedding'].get('result_exists')} / {report['b5']['boundary_field_response_embedding'].get('markdown_exists')}",
            f"- Non-oracle response status: {report['b5']['non_oracle_response_embedding'].get('status')}",
            f"- Non-oracle response instances: {report['b5']['non_oracle_response_embedding'].get('instance_count')}",
            f"- Non-oracle selected mean/max relative error: {report['b5']['non_oracle_response_embedding'].get('selected_mean_relative_response_error')} / {report['b5']['non_oracle_response_embedding'].get('selected_max_relative_response_error')}",
            f"- Non-oracle rows beating oracle boundary-field: {report['b5']['non_oracle_response_embedding'].get('non_oracle_rows_beating_oracle_boundary_field')}",
            f"- Non-oracle exact/cluster max Hilbert dimension: {report['b5']['non_oracle_response_embedding'].get('max_exact_d5_hilbert_dimension')} / {report['b5']['non_oracle_response_embedding'].get('max_selected_cluster_hilbert_dimension')}",
            f"- Non-oracle uses exact target / oracle tuned / quantum win claimed: {report['b5']['non_oracle_response_embedding'].get('uses_exact_target_for_selection')} / {report['b5']['non_oracle_response_embedding'].get('oracle_tuned_boundary_field')} / {report['b5']['non_oracle_response_embedding'].get('quantum_response_win_claimed')}",
            f"- Non-oracle validation errors: {report['b5']['non_oracle_response_embedding'].get('validation_error_count')}",
            f"- Non-oracle result/markdown exists: {report['b5']['non_oracle_response_embedding'].get('result_exists')} / {report['b5']['non_oracle_response_embedding'].get('markdown_exists')}",
            f"- MPS truncation response status: {report['b5']['mps_truncation_response_reference'].get('status')}",
            f"- MPS truncation instances / bond dimensions / selected bond dimension: {report['b5']['mps_truncation_response_reference'].get('instance_count')} / {report['b5']['mps_truncation_response_reference'].get('bond_dimensions_tested')} / {report['b5']['mps_truncation_response_reference'].get('selected_bond_dimension')}",
            f"- MPS truncation selected mean/max relative error: {report['b5']['mps_truncation_response_reference'].get('selected_mean_relative_response_error')} / {report['b5']['mps_truncation_response_reference'].get('selected_max_relative_response_error')}",
            f"- MPS truncation selected mean/max energy error per site: {report['b5']['mps_truncation_response_reference'].get('selected_mean_energy_error_per_site')} / {report['b5']['mps_truncation_response_reference'].get('selected_max_energy_error_per_site')}",
            f"- MPS truncation min overlap / fixed-sector norm: {report['b5']['mps_truncation_response_reference'].get('selected_min_overlap_with_exact_ground_state')} / {report['b5']['mps_truncation_response_reference'].get('selected_min_fixed_sector_norm_before_normalization')}",
            f"- MPS rows beating non-oracle embedding: {report['b5']['mps_truncation_response_reference'].get('mps_rows_beating_non_oracle_embedding')}",
            f"- MPS exact-state seeded / variational DMRG / quantum win claimed: {report['b5']['mps_truncation_response_reference'].get('exact_state_seeded')} / {report['b5']['mps_truncation_response_reference'].get('variational_dmrg')} / {report['b5']['mps_truncation_response_reference'].get('quantum_response_win_claimed')}",
            f"- MPS validation errors: {report['b5']['mps_truncation_response_reference'].get('validation_error_count')}",
            f"- MPS result/markdown exists: {report['b5']['mps_truncation_response_reference'].get('result_exists')} / {report['b5']['mps_truncation_response_reference'].get('markdown_exists')}",
            f"- Two-site finite-DMRG status: {report['b5']['two_site_finite_dmrg_response_reference'].get('status')}",
            f"- Two-site finite-DMRG instances / bond dimensions / restarts x sweeps: {report['b5']['two_site_finite_dmrg_response_reference'].get('instance_count')} / {report['b5']['two_site_finite_dmrg_response_reference'].get('bond_dimensions_tested')} / {report['b5']['two_site_finite_dmrg_response_reference'].get('restarts_per_instance_bond_dimension')} x {report['b5']['two_site_finite_dmrg_response_reference'].get('sweeps_per_restart')}",
            f"- Two-site finite-DMRG selected mean/max relative error: {report['b5']['two_site_finite_dmrg_response_reference'].get('selected_mean_relative_response_error')} / {report['b5']['two_site_finite_dmrg_response_reference'].get('selected_max_relative_response_error')}",
            f"- Two-site finite-DMRG rows beating ALS / seeded pressure: {report['b5']['two_site_finite_dmrg_response_reference'].get('two_site_dmrg_rows_beating_variational_mps_als_reference')} / {report['b5']['two_site_finite_dmrg_response_reference'].get('two_site_dmrg_rows_beating_seeded_mps_pressure_reference')}",
            f"- Two-site finite-DMRG production DMRG / quantum win claimed: {report['b5']['two_site_finite_dmrg_response_reference'].get('production_dmrg')} / {report['b5']['two_site_finite_dmrg_response_reference'].get('quantum_response_win_claimed')}",
            f"- Two-site finite-DMRG validation errors: {report['b5']['two_site_finite_dmrg_response_reference'].get('validation_error_count')}",
            f"- Two-site finite-DMRG result/markdown exists: {report['b5']['two_site_finite_dmrg_response_reference'].get('result_exists')} / {report['b5']['two_site_finite_dmrg_response_reference'].get('markdown_exists')}",
            f"- Canonical-environment smoke gate status: {report['b5']['canonical_environment_smoke_gate'].get('status')}",
            f"- Canonical-environment smoke gate instances / ledger rows / smoke-passed rows: {report['b5']['canonical_environment_smoke_gate'].get('instance_count')} / {report['b5']['canonical_environment_smoke_gate'].get('environment_ledger_rows')} / {report['b5']['canonical_environment_smoke_gate'].get('smoke_passed_row_count')}",
            f"- Canonical-environment smoke gate fixed-sector / variance / discarded-weight / monotonicity rows: {report['b5']['canonical_environment_smoke_gate'].get('fixed_sector_norm_passed_rows')} / {report['b5']['canonical_environment_smoke_gate'].get('energy_variance_passed_rows')} / {report['b5']['canonical_environment_smoke_gate'].get('discarded_weight_passed_rows')} / {report['b5']['canonical_environment_smoke_gate'].get('energy_monotonicity_passed_rows')}",
            f"- Canonical-environment smoke gate response-close / beats seeded / beats ALS: {report['b5']['canonical_environment_smoke_gate'].get('response_close_to_seeded_rows')} / {report['b5']['canonical_environment_smoke_gate'].get('rows_beating_seeded_mps_pressure_reference')} / {report['b5']['canonical_environment_smoke_gate'].get('rows_beating_variational_mps_als_reference')}",
            f"- Canonical-environment smoke gate mean/max response error: {report['b5']['canonical_environment_smoke_gate'].get('mean_relative_response_error')} / {report['b5']['canonical_environment_smoke_gate'].get('max_relative_response_error')}",
            f"- Canonical-environment smoke gate min norm / max discarded / max variance: {report['b5']['canonical_environment_smoke_gate'].get('min_fixed_sector_norm_before_normalization')} / {report['b5']['canonical_environment_smoke_gate'].get('max_relative_discarded_weight')} / {report['b5']['canonical_environment_smoke_gate'].get('max_energy_variance')}",
            f"- Canonical-environment smoke gate mature DMRG / production DMRG / quantum win: {report['b5']['canonical_environment_smoke_gate'].get('mature_canonical_dmrg_ready')} / {report['b5']['canonical_environment_smoke_gate'].get('production_dmrg_claimed')} / {report['b5']['canonical_environment_smoke_gate'].get('quantum_response_win_claimed')}",
            f"- Canonical-environment smoke gate validation errors: {report['b5']['canonical_environment_smoke_gate'].get('validation_error_count')}",
            f"- Canonical-environment smoke gate result/markdown exists: {report['b5']['canonical_environment_smoke_gate'].get('result_exists')} / {report['b5']['canonical_environment_smoke_gate'].get('markdown_exists')}",
            f"- Variational MPS/ALS status: {report['b5']['variational_mps_als_response_reference'].get('status')}",
            f"- Variational MPS/ALS instances / bond dimensions / selected bond dimensions: {report['b5']['variational_mps_als_response_reference'].get('instance_count')} / {report['b5']['variational_mps_als_response_reference'].get('bond_dimensions_tested')} / {report['b5']['variational_mps_als_response_reference'].get('selected_bond_dimensions')}",
            f"- Variational MPS/ALS restarts x sweeps: {report['b5']['variational_mps_als_response_reference'].get('restarts_per_instance_bond_dimension')} x {report['b5']['variational_mps_als_response_reference'].get('sweeps_per_restart')}",
            f"- Variational MPS/ALS selected mean/max relative error: {report['b5']['variational_mps_als_response_reference'].get('selected_mean_relative_response_error')} / {report['b5']['variational_mps_als_response_reference'].get('selected_max_relative_response_error')}",
            f"- Variational MPS/ALS selected mean/max energy error per site: {report['b5']['variational_mps_als_response_reference'].get('selected_mean_energy_error_per_site')} / {report['b5']['variational_mps_als_response_reference'].get('selected_max_energy_error_per_site')}",
            f"- Variational MPS/ALS min overlap / fixed-sector norm: {report['b5']['variational_mps_als_response_reference'].get('selected_min_overlap_with_exact_ground_state')} / {report['b5']['variational_mps_als_response_reference'].get('selected_min_fixed_sector_norm_before_normalization')}",
            f"- Variational MPS/ALS rows beating seeded MPS pressure: {report['b5']['variational_mps_als_response_reference'].get('variational_mps_rows_beating_seeded_mps_pressure_reference')}",
            f"- Variational MPS/ALS exact-state seeded / production DMRG / quantum win claimed: {report['b5']['variational_mps_als_response_reference'].get('exact_state_seeded')} / {report['b5']['variational_mps_als_response_reference'].get('production_dmrg')} / {report['b5']['variational_mps_als_response_reference'].get('quantum_response_win_claimed')}",
            f"- Variational MPS/ALS validation errors: {report['b5']['variational_mps_als_response_reference'].get('validation_error_count')}",
            f"- Variational MPS/ALS result/markdown exists: {report['b5']['variational_mps_als_response_reference'].get('result_exists')} / {report['b5']['variational_mps_als_response_reference'].get('markdown_exists')}",
            f"- Canonical DMRG readiness status: {report['b5']['canonical_dmrg_readiness_gate'].get('status')}",
            f"- Canonical DMRG readiness gates passed/failed: {report['b5']['canonical_dmrg_readiness_gate'].get('passed_gate_count')} / {report['b5']['canonical_dmrg_readiness_gate'].get('failed_gate_count')}",
            f"- Canonical DMRG readiness seeded reference strongest / prototype fixed-sector norms pass: {report['b5']['canonical_dmrg_readiness_gate'].get('exact_state_seeded_reference_is_strongest')} / {report['b5']['canonical_dmrg_readiness_gate'].get('prototype_fixed_sector_norms_pass')}",
            f"- Canonical DMRG readiness production DMRG / quantum win / same-access positive route: {report['b5']['canonical_dmrg_readiness_gate'].get('production_dmrg')} / {report['b5']['canonical_dmrg_readiness_gate'].get('quantum_response_win_claimed')} / {report['b5']['canonical_dmrg_readiness_gate'].get('same_access_positive_route_claimed')}",
            f"- Canonical DMRG readiness validation errors: {report['b5']['canonical_dmrg_readiness_gate'].get('validation_error_count')}",
            f"- Canonical DMRG readiness result/markdown exists: {report['b5']['canonical_dmrg_readiness_gate'].get('result_exists')} / {report['b5']['canonical_dmrg_readiness_gate'].get('markdown_exists')}",
            f"- B5/B10 same-access production contract status: {report['b5']['same_access_production_contract_gate'].get('status')}",
            f"- B5/B10 same-access production contract gates passed/failed: {report['b5']['same_access_production_contract_gate'].get('contract_pass_count')} / {report['b5']['same_access_production_contract_gate'].get('contract_fail_count')}",
            f"- B5/B10 same-access production contract smoke/readiness/sampling blockers: {report['b5']['same_access_production_contract_gate'].get('canonical_environment_smoke_passed_rows')} smoke-passed rows / {report['b5']['same_access_production_contract_gate'].get('readiness_passed_gate_count')} readiness gates / {report['b5']['same_access_production_contract_gate'].get('blocking_sampling_requirement_count')} blocking sampling requirements",
            f"- B5/B10 same-access production contract production DMRG / oracle / positive route: {report['b5']['same_access_production_contract_gate'].get('production_dmrg_available')} / {report['b5']['same_access_production_contract_gate'].get('sampling_oracle_constructed')} / {report['b5']['same_access_production_contract_gate'].get('same_access_positive_route_ready')}",
            f"- B5/B10 same-access production contract validation errors: {report['b5']['same_access_production_contract_gate'].get('validation_error_count')}",
            f"- B5/B10 same-access production contract result/markdown exists: {report['b5']['same_access_production_contract_gate'].get('result_exists')} / {report['b5']['same_access_production_contract_gate'].get('markdown_exists')}",
            "",
            "## B6 Superconductivity Descriptor Status",
            "",
            f"- Status: {report['b6']['descriptor_ranking'].get('status')}",
            f"- Model status: {report['b6']['descriptor_ranking'].get('model_status')}",
            f"- Candidates: {report['b6']['descriptor_ranking'].get('candidate_count')}",
            f"- Top-k: {report['b6']['descriptor_ranking'].get('top_k')}",
            f"- Known high-Tc precision@k: {report['b6']['descriptor_ranking'].get('known_high_tc_precision_at_k')}",
            f"- Known high-Tc recall@k: {report['b6']['descriptor_ranking'].get('known_high_tc_recall_at_k')}",
            f"- Top family counts: {report['b6']['descriptor_ranking'].get('top_family_counts')}",
            f"- Result exists: {report['b6']['descriptor_ranking'].get('result_exists')}",
            f"- Curated leakage audit status: {report['b6']['curated_materials_leakage_audit'].get('status')}",
            f"- Curated records / families / split year: {report['b6']['curated_materials_leakage_audit'].get('record_count')} / {report['b6']['curated_materials_leakage_audit'].get('family_count')} / {report['b6']['curated_materials_leakage_audit'].get('split_year')}",
            f"- Curated post-split records / positives: {report['b6']['curated_materials_leakage_audit'].get('post_split_record_count')} / {report['b6']['curated_materials_leakage_audit'].get('post_split_positive_count')}",
            f"- Curated all physics AP@k / random AP@k mean: {report['b6']['curated_materials_leakage_audit'].get('all_physics_average_precision_at_k')} / {report['b6']['curated_materials_leakage_audit'].get('all_random_average_precision_at_k_mean')}",
            f"- Curated post-split physics AP / family-prior AP / random AP mean: {report['b6']['curated_materials_leakage_audit'].get('post_split_physics_average_precision_at_k')} / {report['b6']['curated_materials_leakage_audit'].get('post_split_family_prior_average_precision_at_k')} / {report['b6']['curated_materials_leakage_audit'].get('post_split_random_average_precision_at_k_mean')}",
            f"- Curated family-holdout physics AP / random AP mean: {report['b6']['curated_materials_leakage_audit'].get('family_holdout_mean_physics_ap')} / {report['b6']['curated_materials_leakage_audit'].get('family_holdout_mean_random_ap')}",
            f"- Curated discovery/mechanism/database claims: {report['b6']['curated_materials_leakage_audit'].get('material_discovery_claimed')} / {report['b6']['curated_materials_leakage_audit'].get('mechanism_solved')} / {report['b6']['curated_materials_leakage_audit'].get('complete_materials_database')}",
            f"- Curated validation errors: {report['b6']['curated_materials_leakage_audit'].get('validation_error_count')}",
            f"- Curated result/markdown exists: {report['b6']['curated_materials_leakage_audit'].get('result_exists')} / {report['b6']['curated_materials_leakage_audit'].get('markdown_exists')}",
            f"- Formula descriptor screen status: {report['b6']['formula_descriptor_screen'].get('status')}",
            f"- Formula records / expanded negatives / families: {report['b6']['formula_descriptor_screen'].get('record_count')} / {report['b6']['formula_descriptor_screen'].get('expanded_negative_control_count')} / {report['b6']['formula_descriptor_screen'].get('family_count')}",
            f"- Formula AP@k / family-prior AP@k: {report['b6']['formula_descriptor_screen'].get('formula_average_precision_at_k')} / {report['b6']['formula_descriptor_screen'].get('family_prior_average_precision_at_k')}",
            f"- Formula post-split AP / family-prior post-split AP: {report['b6']['formula_descriptor_screen'].get('post_split_formula_average_precision_at_k')} / {report['b6']['formula_descriptor_screen'].get('post_split_family_prior_average_precision_at_k')}",
            f"- Formula discovery/mechanism/database/computed-observable claims: {report['b6']['formula_descriptor_screen'].get('material_discovery_claimed')} / {report['b6']['formula_descriptor_screen'].get('mechanism_solved')} / {report['b6']['formula_descriptor_screen'].get('complete_materials_database')} / {report['b6']['formula_descriptor_screen'].get('computed_quantum_observable_claimed')}",
            f"- Formula uses formula descriptors / B5-linked proxy: {report['b6']['formula_descriptor_screen'].get('uses_formula_derived_descriptors')} / {report['b6']['formula_descriptor_screen'].get('uses_b5_linked_proxy')}",
            f"- Formula validation errors: {report['b6']['formula_descriptor_screen'].get('validation_error_count')}",
            f"- Formula result/markdown exists: {report['b6']['formula_descriptor_screen'].get('result_exists')} / {report['b6']['formula_descriptor_screen'].get('markdown_exists')}",
            f"- Structural/electronic proxy status: {report['b6']['structural_electronic_proxy_screen'].get('status')}",
            f"- Structural/electronic records / expanded negatives / families: {report['b6']['structural_electronic_proxy_screen'].get('record_count')} / {report['b6']['structural_electronic_proxy_screen'].get('expanded_negative_control_count')} / {report['b6']['structural_electronic_proxy_screen'].get('family_count')}",
            f"- Structural/electronic AP@k / formula AP@k / family-prior AP@k: {report['b6']['structural_electronic_proxy_screen'].get('structural_average_precision_at_k')} / {report['b6']['structural_electronic_proxy_screen'].get('formula_average_precision_at_k')} / {report['b6']['structural_electronic_proxy_screen'].get('family_prior_average_precision_at_k')}",
            f"- Structural/electronic post-split AP / family-prior post-split AP: {report['b6']['structural_electronic_proxy_screen'].get('post_split_structural_average_precision_at_k')} / {report['b6']['structural_electronic_proxy_screen'].get('post_split_family_prior_average_precision_at_k')}",
            f"- Structural/electronic holdout AP / top-k negative controls: {report['b6']['structural_electronic_proxy_screen'].get('family_holdout_structural_mean_ap')} / {report['b6']['structural_electronic_proxy_screen'].get('top_k_negative_control_count')}",
            f"- Structural/electronic discovery/mechanism/database/DFT/crystal claims: {report['b6']['structural_electronic_proxy_screen'].get('material_discovery_claimed')} / {report['b6']['structural_electronic_proxy_screen'].get('mechanism_solved')} / {report['b6']['structural_electronic_proxy_screen'].get('complete_materials_database')} / {report['b6']['structural_electronic_proxy_screen'].get('real_dft_claimed')} / {report['b6']['structural_electronic_proxy_screen'].get('real_crystallographic_database_claimed')}",
            f"- Structural/electronic validation errors: {report['b6']['structural_electronic_proxy_screen'].get('validation_error_count')}",
            f"- Structural/electronic result/markdown exists: {report['b6']['structural_electronic_proxy_screen'].get('result_exists')} / {report['b6']['structural_electronic_proxy_screen'].get('markdown_exists')}",
            "",
            "## B7 Fault-Tolerance Co-Design Status",
            "",
            f"- Status: {report['b7']['fault_tolerance_codesign'].get('status')}",
            f"- Model status: {report['b7']['fault_tolerance_codesign'].get('model_status')}",
            f"- Workloads: {report['b7']['fault_tolerance_codesign'].get('workload_count')}",
            f"- Configurations: {report['b7']['fault_tolerance_codesign'].get('configuration_count')}",
            f"- Minimum space-time-volume reduction: {report['b7']['fault_tolerance_codesign'].get('min_space_time_volume_reduction')}",
            f"- Mean space-time-volume reduction: {report['b7']['fault_tolerance_codesign'].get('mean_space_time_volume_reduction')}",
            f"- Workloads meeting 25% reduction: {report['b7']['fault_tolerance_codesign'].get('workloads_meeting_25_percent_reduction')}",
            f"- Result exists: {report['b7']['fault_tolerance_codesign'].get('result_exists')}",
            f"- B1/B2 dependency bridge status: {report['b7']['dependency_schedule_bridge'].get('status')}",
            f"- B1/B2 dependency bridge comparisons: {report['b7']['dependency_schedule_bridge'].get('comparison_count')}",
            f"- B1/B2 dependency bridge min STV reduction: {report['b7']['dependency_schedule_bridge'].get('min_space_time_volume_reduction')}",
            f"- B1/B2 dependency bridge mean STV reduction: {report['b7']['dependency_schedule_bridge'].get('mean_space_time_volume_reduction')}",
            f"- B1/B2 dependency bridge selected B2 distance/target: d={report['b7']['dependency_schedule_bridge'].get('selected_b2_distance')} / {report['b7']['dependency_schedule_bridge'].get('selected_b2_target_logical_error')}",
            f"- B1/B2 dependency bridge result exists: {report['b7']['dependency_schedule_bridge'].get('result_exists')}",
            f"- Workload DAG factory schedule status: {report['b7']['workload_dag_factory_schedule'].get('status')}",
            f"- Workload DAG factory comparisons: {report['b7']['workload_dag_factory_schedule'].get('comparison_count')}",
            f"- Workload DAG factory variants: {report['b7']['workload_dag_factory_schedule'].get('factory_variants')}",
            f"- Workload DAG min STV reduction: {report['b7']['workload_dag_factory_schedule'].get('min_space_time_volume_reduction')}",
            f"- Workload DAG mean STV reduction: {report['b7']['workload_dag_factory_schedule'].get('mean_space_time_volume_reduction')}",
            f"- Workload DAG factory bottleneck comparisons: {report['b7']['workload_dag_factory_schedule'].get('factory_bottleneck_comparisons')}",
            f"- Workload DAG result exists: {report['b7']['workload_dag_factory_schedule'].get('result_exists')}",
            f"- Logical T factory schedule status: {report['b7']['logical_t_factory_schedule'].get('status')}",
            f"- Logical T factory comparisons: {report['b7']['logical_t_factory_schedule'].get('comparison_count')}",
            f"- Logical T factory bottleneck comparisons: {report['b7']['logical_t_factory_schedule'].get('factory_bottleneck_comparisons')}",
            f"- Logical T factory mean STV reduction: {report['b7']['logical_t_factory_schedule'].get('mean_space_time_volume_reduction')}",
            f"- Logical T-count mean reduction: {report['b7']['logical_t_factory_schedule'].get('mean_logical_t_count_reduction')}",
            f"- Logical T factory result exists: {report['b7']['logical_t_factory_schedule'].get('result_exists')}",
            f"- Post-1Q logical T factory status: {report['b7']['logical_t_factory_schedule_post_1q'].get('status')}",
            f"- Post-1Q logical T factory comparisons: {report['b7']['logical_t_factory_schedule_post_1q'].get('comparison_count')}",
            f"- Post-1Q logical T factory bottleneck comparisons: {report['b7']['logical_t_factory_schedule_post_1q'].get('factory_bottleneck_comparisons')}",
            f"- Post-1Q logical T factory min STV reduction: {report['b7']['logical_t_factory_schedule_post_1q'].get('min_space_time_volume_reduction')}",
            f"- Post-1Q logical T factory mean STV reduction: {report['b7']['logical_t_factory_schedule_post_1q'].get('mean_space_time_volume_reduction')}",
            f"- Post-1Q logical T-count mean reduction: {report['b7']['logical_t_factory_schedule_post_1q'].get('mean_logical_t_count_reduction')}",
            f"- Post-1Q logical T factory result exists: {report['b7']['logical_t_factory_schedule_post_1q'].get('result_exists')}",
            f"- Native logical T factory status: {report['b7']['logical_t_factory_schedule_native'].get('status')}",
            f"- Native logical T factory comparisons: {report['b7']['logical_t_factory_schedule_native'].get('comparison_count')}",
            f"- Native logical T factory bottleneck comparisons: {report['b7']['logical_t_factory_schedule_native'].get('factory_bottleneck_comparisons')}",
            f"- Native logical T factory min STV reduction: {report['b7']['logical_t_factory_schedule_native'].get('min_space_time_volume_reduction')}",
            f"- Native logical T factory mean STV reduction: {report['b7']['logical_t_factory_schedule_native'].get('mean_space_time_volume_reduction')}",
            f"- Native logical T-count mean reduction: {report['b7']['logical_t_factory_schedule_native'].get('mean_logical_t_count_reduction')}",
            f"- Native logical T factory result exists: {report['b7']['logical_t_factory_schedule_native'].get('result_exists')}",
            f"- Control-RZ logical T factory status: {report['b7']['logical_t_factory_schedule_control_rz'].get('status')}",
            f"- Control-RZ logical T factory comparisons: {report['b7']['logical_t_factory_schedule_control_rz'].get('comparison_count')}",
            f"- Control-RZ logical T factory bottleneck comparisons: {report['b7']['logical_t_factory_schedule_control_rz'].get('factory_bottleneck_comparisons')}",
            f"- Control-RZ logical T factory min STV reduction: {report['b7']['logical_t_factory_schedule_control_rz'].get('min_space_time_volume_reduction')}",
            f"- Control-RZ logical T factory mean STV reduction: {report['b7']['logical_t_factory_schedule_control_rz'].get('mean_space_time_volume_reduction')}",
            f"- Control-RZ logical T-count mean reduction: {report['b7']['logical_t_factory_schedule_control_rz'].get('mean_logical_t_count_reduction')}",
            f"- Control-RZ logical T factory result exists: {report['b7']['logical_t_factory_schedule_control_rz'].get('result_exists')}",
            f"- U3 phase-factored logical T factory status: {report['b7']['logical_t_factory_schedule_u3_phase_factored'].get('status')}",
            f"- U3 phase-factored logical T factory comparisons: {report['b7']['logical_t_factory_schedule_u3_phase_factored'].get('comparison_count')}",
            f"- U3 phase-factored logical T factory bottleneck comparisons: {report['b7']['logical_t_factory_schedule_u3_phase_factored'].get('factory_bottleneck_comparisons')}",
            f"- U3 phase-factored logical T factory min STV reduction: {report['b7']['logical_t_factory_schedule_u3_phase_factored'].get('min_space_time_volume_reduction')}",
            f"- U3 phase-factored logical T factory mean STV reduction: {report['b7']['logical_t_factory_schedule_u3_phase_factored'].get('mean_space_time_volume_reduction')}",
            f"- U3 phase-factored logical T-count mean reduction: {report['b7']['logical_t_factory_schedule_u3_phase_factored'].get('mean_logical_t_count_reduction')}",
            f"- U3 phase-factored logical T factory result exists: {report['b7']['logical_t_factory_schedule_u3_phase_factored'].get('result_exists')}",
            f"- Minimum-STV regime classifier status: {report['b7']['min_stv_regime_classifier'].get('status')}",
            f"- Minimum-STV regime classifier min workload: {report['b7']['min_stv_regime_classifier'].get('min_workload')}",
            f"- Minimum-STV regime classifier min STV reduction: {report['b7']['min_stv_regime_classifier'].get('min_space_time_volume_reduction')}",
            f"- Minimum-STV regime classifier factory-bottleneck rows: {report['b7']['min_stv_regime_classifier'].get('factory_bottleneck_after_count')}",
            f"- Minimum-STV regime classifier deep factory-locked rows: {report['b7']['min_stv_regime_classifier'].get('deep_factory_locked_count')}",
            f"- T proxy still needed for 1.20x / 1.25x STV: {report['b7']['min_stv_regime_classifier'].get('target_1_20_additional_t_count_proxy_to_remove')} / {report['b7']['min_stv_regime_classifier'].get('target_1_25_additional_t_count_proxy_to_remove')}",
            f"- Minimum-STV regime classifier result exists: {report['b7']['min_stv_regime_classifier'].get('result_exists')}",
            f"- FT synthesis ledger status: {report['b7']['ft_synthesis_ledger'].get('status')}",
            f"- FT synthesis ledger min workload: {report['b7']['ft_synthesis_ledger'].get('min_workload')}",
            f"- FT synthesis ledger min STV reduction: {report['b7']['ft_synthesis_ledger'].get('min_space_time_volume_reduction')}",
            f"- FT synthesis ledger mean STV reduction: {report['b7']['ft_synthesis_ledger'].get('mean_space_time_volume_reduction')}",
            f"- FT synthesis ledger after factory/data bottlenecks: {report['b7']['ft_synthesis_ledger'].get('factory_bottleneck_after_count')} / {report['b7']['ft_synthesis_ledger'].get('data_bottleneck_after_count')}",
            f"- FT synthesis ledger sat_n11 T ledger before/after: {report['b7']['ft_synthesis_ledger'].get('sat_n11_before_t_ledger')} / {report['b7']['ft_synthesis_ledger'].get('sat_n11_after_t_ledger')}",
            f"- FT synthesis ledger sat_n11 balanced/throughput STV: {report['b7']['ft_synthesis_ledger'].get('sat_n11_balanced_stv_reduction')} / {report['b7']['ft_synthesis_ledger'].get('sat_n11_throughput_stv_reduction')}",
            f"- FT synthesis ledger result exists: {report['b7']['ft_synthesis_ledger'].get('result_exists')}",
            f"- gcm_h6 FT boundary status: {report['b7']['gcm_h6_ft_boundary'].get('status')}",
            f"- gcm_h6 FT boundary current min workload/variant: {report['b7']['gcm_h6_ft_boundary'].get('current_min_workload')} / {report['b7']['gcm_h6_ft_boundary'].get('current_min_factory_variant')}",
            f"- gcm_h6 FT boundary current min STV: {report['b7']['gcm_h6_ft_boundary'].get('current_min_space_time_volume_reduction')}",
            f"- gcm_h6 arbitrary numeric rotations/cost: {report['b7']['gcm_h6_ft_boundary'].get('gcm_h6_after_arbitrary_numeric_rotation_count')} / {report['b7']['gcm_h6_ft_boundary'].get('gcm_h6_after_arbitrary_numeric_t_cost')}",
            f"- gcm_h6 T ledger still needed for 1.20x / 1.25x STV: {report['b7']['gcm_h6_ft_boundary'].get('gcm_h6_target_1_20_additional_t_ledger_to_remove')} / {report['b7']['gcm_h6_ft_boundary'].get('gcm_h6_target_1_25_additional_t_ledger_to_remove')}",
            f"- Cost sweep alone clears 1.20x all-variant min: {report['b7']['gcm_h6_ft_boundary'].get('portfolio_cost_sweep_reaches_1_20')}",
            f"- gcm_h6 FT boundary result exists: {report['b7']['gcm_h6_ft_boundary'].get('result_exists')}",
            f"- Precision-aware rotation ledger status: {report['b7']['precision_aware_rotation_ledger'].get('status')}",
            f"- Precision-aware rotation ledger arbitrary/unique numeric rotations: {report['b7']['precision_aware_rotation_ledger'].get('gcm_h6_after_arbitrary_numeric_rotation_count')} / {report['b7']['precision_aware_rotation_ledger'].get('gcm_h6_after_unique_numeric_parameters')}",
            f"- Precision-aware one-sided max arbitrary T cost for 1.20x / 1.25x: {report['b7']['precision_aware_rotation_ledger'].get('gcm_h6_one_sided_target_1_20_max_average_arbitrary_t_cost')} / {report['b7']['precision_aware_rotation_ledger'].get('gcm_h6_one_sided_target_1_25_max_average_arbitrary_t_cost')}",
            f"- Best tested precision budget arbitrary T cost / min STV: {report['b7']['precision_aware_rotation_ledger'].get('best_tested_precision_budget_arbitrary_t_cost')} / {report['b7']['precision_aware_rotation_ledger'].get('best_tested_precision_budget_min_stv_reduction')}",
            f"- Precision budgets clear 1.20x all-variant/gcm_h6 min: {report['b7']['precision_aware_rotation_ledger'].get('portfolio_precision_budgets_clear_1_20')} / {report['b7']['precision_aware_rotation_ledger'].get('gcm_h6_precision_budgets_clear_1_20')}",
            f"- Precision-aware rotation ledger result exists: {report['b7']['precision_aware_rotation_ledger'].get('result_exists')}",
            f"- gcm_h6 numeric-rotation structure status: {report['b7']['gcm_h6_numeric_rotation_structure'].get('status')}",
            f"- gcm_h6 numeric rotations before/after/removed: {report['b7']['gcm_h6_numeric_rotation_structure'].get('arbitrary_numeric_rotations_before')} / {report['b7']['gcm_h6_numeric_rotation_structure'].get('arbitrary_numeric_rotations_after')} / {report['b7']['gcm_h6_numeric_rotation_structure'].get('arbitrary_numeric_rotations_removed')}",
            f"- gcm_h6 numeric-structure T ledger before/after/removed: {report['b7']['gcm_h6_numeric_rotation_structure'].get('logical_t_ledger_before')} / {report['b7']['gcm_h6_numeric_rotation_structure'].get('logical_t_ledger_after')} / {report['b7']['gcm_h6_numeric_rotation_structure'].get('logical_t_ledger_removed')}",
            f"- gcm_h6 numeric-structure proof events / Aer failed: {report['b7']['gcm_h6_numeric_rotation_structure'].get('proof_events')} / {report['b7']['gcm_h6_numeric_rotation_structure'].get('aer_crosscheck_failed')}",
            f"- gcm_h6 numeric-structure min STV / clears 1.20x: {report['b7']['gcm_h6_numeric_rotation_structure'].get('portfolio_min_space_time_volume_reduction')} / {report['b7']['gcm_h6_numeric_rotation_structure'].get('portfolio_clears_1_20')}",
            f"- gcm_h6 numeric-rotation structure result exists: {report['b7']['gcm_h6_numeric_rotation_structure'].get('result_exists')}",
            f"- Shared synthesis/cache boundary status: {report['b7']['shared_synthesis_cache_boundary'].get('status')}",
            f"- Shared synthesis/cache occurrences / unique numeric instructions: {report['b7']['shared_synthesis_cache_boundary'].get('after_numeric_occurrences')} / {report['b7']['shared_synthesis_cache_boundary'].get('after_unique_numeric_instructions')}",
            f"- Shared synthesis/cache classical catalog reduction factor: {report['b7']['shared_synthesis_cache_boundary'].get('classical_catalog_reduction_factor')}",
            f"- Shared synthesis/cache physical T ledger before/after: {report['b7']['shared_synthesis_cache_boundary'].get('physical_occurrence_before_t_ledger')} / {report['b7']['shared_synthesis_cache_boundary'].get('physical_occurrence_after_t_ledger')}",
            f"- Shared synthesis/cache FT T-ledger reduction from cache: {report['b7']['shared_synthesis_cache_boundary'].get('ft_t_ledger_reduction_from_cache')}",
            f"- Shared synthesis/cache physical min STV / clears 1.20x: {report['b7']['shared_synthesis_cache_boundary'].get('physical_occurrence_min_stv_reduction')} / {report['b7']['shared_synthesis_cache_boundary'].get('physical_occurrence_clears_1_20')}",
            f"- Invalid after-only unique-template gcm_h6/all-variant clears 1.20x: {report['b7']['shared_synthesis_cache_boundary'].get('invalid_after_only_unique_gcm_h6_clears_1_20')} / {report['b7']['shared_synthesis_cache_boundary'].get('invalid_after_only_unique_all_variant_clears_1_20')}",
            f"- Shared synthesis/cache boundary result exists: {report['b7']['shared_synthesis_cache_boundary'].get('result_exists')}",
            f"- Nonlocal template block scan status: {report['b7']['nonlocal_template_block_scan'].get('status')}",
            f"- Nonlocal template candidate certificates / top templates: {report['b7']['nonlocal_template_block_scan'].get('candidate_certificate_count')} / {report['b7']['nonlocal_template_block_scan'].get('top_template_count')}",
            f"- Best nonlocal template id/width/occurrences: {report['b7']['nonlocal_template_block_scan'].get('best_template_id')} / {report['b7']['nonlocal_template_block_scan'].get('best_template_width')} / {report['b7']['nonlocal_template_block_scan'].get('best_template_nonoverlap_occurrences')}",
            f"- Best nonlocal template arbitrary coverage: {report['b7']['nonlocal_template_block_scan'].get('best_template_arbitrary_rotations_per_occurrence')} per occurrence, {report['b7']['nonlocal_template_block_scan'].get('best_template_physical_arbitrary_occurrences_covered')} physical occurrences covered",
            f"- Nonlocal template adjacent inverse/duplicate pairs: {report['b7']['nonlocal_template_block_scan'].get('adjacent_inverse_pair_count')} / {report['b7']['nonlocal_template_block_scan'].get('adjacent_duplicate_pair_count')}",
            f"- Nonlocal template removed arbitrary/T ledger: {report['b7']['nonlocal_template_block_scan'].get('arbitrary_numeric_rotations_removed')} / {report['b7']['nonlocal_template_block_scan'].get('logical_t_ledger_removed')}",
            f"- Nonlocal template min STV / gcm_h6 occurrence target for 1.20x: {report['b7']['nonlocal_template_block_scan'].get('portfolio_min_space_time_volume_reduction')} / {report['b7']['nonlocal_template_block_scan'].get('first_gcm_h6_1_20_removed_arbitrary_occurrences')}",
            f"- Nonlocal template all-variant 1.20x by gcm_h6-only removals: {report['b7']['nonlocal_template_block_scan'].get('all_variant_1_20_by_gcm_h6_only')}",
            f"- Nonlocal template block scan result exists: {report['b7']['nonlocal_template_block_scan'].get('result_exists')}",
            f"- Template priority gate status: {report['b7']['template_priority_gate'].get('status')}",
            f"- Template priority gate templates / target removed arbitrary / one-angle clear count: {report['b7']['template_priority_gate'].get('template_count')} / {report['b7']['template_priority_gate'].get('target_removed_arbitrary_occurrences_for_gcm_h6_1_20')} / {report['b7']['template_priority_gate'].get('single_template_one_angle_clear_count')}",
            f"- Template priority gate best template / required removals per occurrence / one-angle shortfall: {report['b7']['template_priority_gate'].get('best_template_id')} / {report['b7']['template_priority_gate'].get('best_template_required_arbitrary_removed_per_occurrence')} / {report['b7']['template_priority_gate'].get('best_template_one_angle_shortfall')}",
            f"- Template priority gate w8_21 prior optimizer runs / exact rewrite found: {report['b7']['template_priority_gate'].get('w8_21_prior_optimizer_runs')} / {report['b7']['template_priority_gate'].get('w8_21_prior_exact_rewrite_found')}",
            f"- Template priority gate all-variant 1.20x / physical claim / global lower bound: {report['b7']['template_priority_gate'].get('all_variant_1_20_by_gcm_h6_only')} / {report['b7']['template_priority_gate'].get('physical_resource_reduction_claimed')} / {report['b7']['template_priority_gate'].get('global_lower_bound_claimed')}",
            f"- Template priority gate validation errors / result/markdown exists: {report['b7']['template_priority_gate'].get('validation_error_count')} / {report['b7']['template_priority_gate'].get('result_exists')} / {report['b7']['template_priority_gate'].get('markdown_exists')}",
            f"- w8_21 small-block synthesis status: {report['b7']['w8_21_small_block_synthesis'].get('status')}",
            f"- w8_21 synthesis attempts / passing candidates: {report['b7']['w8_21_small_block_synthesis'].get('candidate_attempt_count')} / {report['b7']['w8_21_small_block_synthesis'].get('passing_candidate_count')}",
            f"- w8_21 best fixed parameter/label/residual: {report['b7']['w8_21_small_block_synthesis'].get('best_fixed_parameter')} / {report['b7']['w8_21_small_block_synthesis'].get('best_fixed_label')} / {report['b7']['w8_21_small_block_synthesis'].get('best_residual_norm')}",
            f"- w8_21 local rank / five-degree support: {report['b7']['w8_21_small_block_synthesis'].get('finite_difference_rank')} / {report['b7']['w8_21_small_block_synthesis'].get('rank_supports_five_independent_continuous_degrees')}",
            f"- w8_21 same-skeleton exact replacement found: {report['b7']['w8_21_small_block_synthesis'].get('same_skeleton_one_rotation_exact_replacement_found')}",
            f"- w8_21 small-block synthesis result/proof exists: {report['b7']['w8_21_small_block_synthesis'].get('result_exists')} / {report['b7']['w8_21_small_block_synthesis'].get('proof_exists')}",
            f"- w8_21 broad-skeleton search status: {report['b7']['w8_21_broad_skeleton_search'].get('status')}",
            f"- w8_21 broad-skeleton families total/scanned/selection: {report['b7']['w8_21_broad_skeleton_search'].get('total_family_count')} / {report['b7']['w8_21_broad_skeleton_search'].get('family_count')} / {report['b7']['w8_21_broad_skeleton_search'].get('family_selection')}",
            f"- w8_21 broad-skeleton optimizer runs / passing candidates: {report['b7']['w8_21_broad_skeleton_search'].get('attempted_optimizer_runs')} / {report['b7']['w8_21_broad_skeleton_search'].get('passing_candidate_count')}",
            f"- w8_21 broad-skeleton best family/residual: {report['b7']['w8_21_broad_skeleton_search'].get('best_family_label')} / {report['b7']['w8_21_broad_skeleton_search'].get('best_residual_norm')}",
            f"- w8_21 broad-skeleton exact found / global lower bound claimed: {report['b7']['w8_21_broad_skeleton_search'].get('bounded_four_rotation_two_cnot_search_found_exact_candidate')} / {report['b7']['w8_21_broad_skeleton_search'].get('global_two_qubit_lower_bound_claimed')}",
            f"- w8_21 broad-skeleton result/proof exists: {report['b7']['w8_21_broad_skeleton_search'].get('result_exists')} / {report['b7']['w8_21_broad_skeleton_search'].get('proof_exists')}",
            f"- w8_21 Euler-local search status: {report['b7']['w8_21_euler_local_search'].get('status')}",
            f"- w8_21 Euler-local families total/scanned/mode: {report['b7']['w8_21_euler_local_search'].get('total_family_count')} / {report['b7']['w8_21_euler_local_search'].get('family_count')} / {report['b7']['w8_21_euler_local_search'].get('family_mode')}",
            f"- w8_21 Euler-local optimizer runs / passing candidates: {report['b7']['w8_21_euler_local_search'].get('attempted_optimizer_runs')} / {report['b7']['w8_21_euler_local_search'].get('passing_candidate_count')}",
            f"- w8_21 Euler-local best family/residual: {report['b7']['w8_21_euler_local_search'].get('best_family_label')} / {report['b7']['w8_21_euler_local_search'].get('best_residual_norm')}",
            f"- w8_21 Euler-local exact found / global lower bound claimed: {report['b7']['w8_21_euler_local_search'].get('euler_local_four_rotation_search_found_exact_candidate')} / {report['b7']['w8_21_euler_local_search'].get('global_two_qubit_lower_bound_claimed')}",
            f"- w8_21 Euler-local result/proof exists: {report['b7']['w8_21_euler_local_search'].get('result_exists')} / {report['b7']['w8_21_euler_local_search'].get('proof_exists')}",
            f"- w8_21 three-CNOT search status: {report['b7']['w8_21_three_cnot_search'].get('status')}",
            f"- w8_21 three-CNOT families total/scanned/mode: {report['b7']['w8_21_three_cnot_search'].get('total_family_count')} / {report['b7']['w8_21_three_cnot_search'].get('family_count')} / {report['b7']['w8_21_three_cnot_search'].get('family_mode')}",
            f"- w8_21 three-CNOT optimizer runs / passing candidates: {report['b7']['w8_21_three_cnot_search'].get('attempted_optimizer_runs')} / {report['b7']['w8_21_three_cnot_search'].get('passing_candidate_count')}",
            f"- w8_21 three-CNOT best family/residual: {report['b7']['w8_21_three_cnot_search'].get('best_family_label')} / {report['b7']['w8_21_three_cnot_search'].get('best_residual_norm')}",
            f"- w8_21 three-CNOT exact found / global lower bound claimed: {report['b7']['w8_21_three_cnot_search'].get('three_cnot_four_rotation_search_found_exact_candidate')} / {report['b7']['w8_21_three_cnot_search'].get('global_two_qubit_lower_bound_claimed')}",
            f"- w8_21 three-CNOT result/proof exists: {report['b7']['w8_21_three_cnot_search'].get('result_exists')} / {report['b7']['w8_21_three_cnot_search'].get('proof_exists')}",
            f"- w8_21 scoped minimality note status: {report['b7']['w8_21_scoped_minimality_note'].get('status')}",
            f"- w8_21 scoped minimality optimizer runs / exact rewrite found: {report['b7']['w8_21_scoped_minimality_note'].get('total_optimizer_runs_across_searches')} / {report['b7']['w8_21_scoped_minimality_note'].get('exact_rewrite_found')}",
            f"- w8_21 scoped minimality arbitrary/T ledger removed: {report['b7']['w8_21_scoped_minimality_note'].get('w8_21_arbitrary_rotations_removed')} / {report['b7']['w8_21_scoped_minimality_note'].get('w8_21_proxy_t_ledger_removed')}",
            f"- w8_21 scoped minimality markdown exists: {report['b7']['w8_21_scoped_minimality_note'].get('markdown_exists')}",
            f"- w8_21 claim-boundary fragment status: {report['b7']['w8_21_claim_boundary_fragment'].get('status')}",
            f"- w8_21 claim-boundary optimizer runs / exact rewrite found: {report['b7']['w8_21_claim_boundary_fragment'].get('total_optimizer_runs_across_searches')} / {report['b7']['w8_21_claim_boundary_fragment'].get('exact_rewrite_found')}",
            f"- w8_21 claim-boundary arbitrary/T ledger removed: {report['b7']['w8_21_claim_boundary_fragment'].get('w8_21_arbitrary_rotations_removed')} / {report['b7']['w8_21_claim_boundary_fragment'].get('w8_21_proxy_t_ledger_removed')}",
            f"- w8_21 claim-boundary global minimality theorem claimed: {report['b7']['w8_21_claim_boundary_fragment'].get('global_minimality_theorem_claimed')}",
            f"- w8_21 claim-boundary markdown exists/has claim: {report['b7']['w8_21_claim_boundary_fragment'].get('markdown_exists')} / {report['b7']['w8_21_claim_boundary_fragment'].get('markdown_has_claim')}",
            "",
            "## B8 Output Invariant Verification Status",
            "",
            f"- Status: {report['b8']['output_invariant_verifier'].get('status')}",
            f"- Model status: {report['b8']['output_invariant_verifier'].get('model_status')}",
            f"- Tasks: {report['b8']['output_invariant_verifier'].get('task_count')}",
            f"- Configurations: {report['b8']['output_invariant_verifier'].get('configuration_count')}",
            f"- Samples per trial: {report['b8']['output_invariant_verifier'].get('sample_count')}",
            f"- Adversaries tested: {report['b8']['output_invariant_verifier'].get('adversaries_tested')}",
            f"- Adversaries failing invariant rule: {report['b8']['output_invariant_verifier'].get('adversaries_failing_count')}",
            f"- Minimum honest completeness: {report['b8']['output_invariant_verifier'].get('minimum_honest_completeness')}",
            f"- Maximum adversary soundness: {report['b8']['output_invariant_verifier'].get('maximum_adversary_soundness')}",
            f"- Result exists: {report['b8']['output_invariant_verifier'].get('result_exists')}",
            f"- Adaptive leakage status: {report['b8']['adaptive_leakage_spoofer'].get('status')}",
            f"- Adaptive leakage configurations: {report['b8']['adaptive_leakage_spoofer'].get('configuration_count')}",
            f"- Adaptive leakage fractions: {report['b8']['adaptive_leakage_spoofer'].get('leakage_fractions')}",
            f"- Adaptive leakage maximum soundness: {report['b8']['adaptive_leakage_spoofer'].get('maximum_adaptive_soundness')}",
            f"- Adaptive leakage dangerous threshold: {report['b8']['adaptive_leakage_spoofer'].get('dangerous_leakage_threshold')}",
            f"- Adaptive leakage result exists: {report['b8']['adaptive_leakage_spoofer'].get('result_exists')}",
            f"- Challenge-refresh repair status: {report['b8']['challenge_refresh_repair'].get('status')}",
            f"- Challenge-refresh repair configurations: {report['b8']['challenge_refresh_repair'].get('configuration_count')}",
            f"- Challenge-refresh repair modes: {report['b8']['challenge_refresh_repair'].get('refresh_modes')}",
            f"- High-leakage repair modes passing: {report['b8']['challenge_refresh_repair'].get('high_leakage_repair_modes_passing')}",
            f"- Challenge-refresh repair result exists: {report['b8']['challenge_refresh_repair'].get('result_exists')}",
            f"- Circuit refresh status: {report['b8']['circuit_refresh_task'].get('status')}",
            f"- Circuit refresh configurations: {report['b8']['circuit_refresh_task'].get('configuration_count')}",
            f"- Circuit refresh no-refresh high-leakage max soundness: {report['b8']['circuit_refresh_task'].get('none_high_leakage_max_soundness')}",
            f"- Circuit refresh best repaired high-leakage max soundness: {report['b8']['circuit_refresh_task'].get('best_repair_high_leakage_max_soundness')}",
            f"- Circuit refresh high-leakage repair modes passing: {report['b8']['circuit_refresh_task'].get('high_leakage_repair_modes_passing')}",
            f"- Circuit refresh result/markdown exists: {report['b8']['circuit_refresh_task'].get('result_exists')} / {report['b8']['circuit_refresh_task'].get('markdown_exists')}",
            f"- OpenQASM 3 packet status: {report['b8']['openqasm3_randomized_measurement_packet'].get('status')}",
            f"- OpenQASM 3 packet circuits / max qubits: {report['b8']['openqasm3_randomized_measurement_packet'].get('circuit_file_count')} / {report['b8']['openqasm3_randomized_measurement_packet'].get('max_total_qubits')}",
            f"- OpenQASM 3 packet headers / Aer mismatches / honest completeness: {report['b8']['openqasm3_randomized_measurement_packet'].get('all_qasm3_headers_valid')} / {report['b8']['openqasm3_randomized_measurement_packet'].get('aer_semantic_mismatch_count')} / {report['b8']['openqasm3_randomized_measurement_packet'].get('minimum_aer_honest_completeness')}",
            f"- OpenQASM 3 packet hardware execution / advantage / BQP separation: {report['b8']['openqasm3_randomized_measurement_packet'].get('hardware_execution_performed')} / {report['b8']['openqasm3_randomized_measurement_packet'].get('quantum_advantage_claimed')} / {report['b8']['openqasm3_randomized_measurement_packet'].get('bqp_separation_claimed')}",
            f"- OpenQASM 3 packet result/markdown/directory exists: {report['b8']['openqasm3_randomized_measurement_packet'].get('result_exists')} / {report['b8']['openqasm3_randomized_measurement_packet'].get('markdown_exists')} / {report['b8']['openqasm3_randomized_measurement_packet'].get('qasm_directory_exists')}",
            f"- Public-QASM spoofer status: {report['b8']['public_qasm_packet_spoofer_gate'].get('status')}",
            f"- Public-QASM spoofer parsed circuits / prediction success: {report['b8']['public_qasm_packet_spoofer_gate'].get('parsed_circuit_count')} / {report['b8']['public_qasm_packet_spoofer_gate'].get('public_stabilizer_emulator_prediction_success_rate')}",
            f"- Public-QASM packet soundness rejected / late-bound private challenges required: {report['b8']['public_qasm_packet_spoofer_gate'].get('public_packet_contract_soundness_rejected')} / {report['b8']['public_qasm_packet_spoofer_gate'].get('late_bound_private_challenges_required')}",
            f"- Public-QASM spoofer hardware execution / advantage / BQP separation: {report['b8']['public_qasm_packet_spoofer_gate'].get('hardware_execution_performed')} / {report['b8']['public_qasm_packet_spoofer_gate'].get('quantum_advantage_claimed')} / {report['b8']['public_qasm_packet_spoofer_gate'].get('bqp_separation_claimed')}",
            f"- Public-QASM spoofer result/markdown exists: {report['b8']['public_qasm_packet_spoofer_gate'].get('result_exists')} / {report['b8']['public_qasm_packet_spoofer_gate'].get('markdown_exists')}",
            f"- Late-bound contract status: {report['b8']['late_bound_private_challenge_contract_gate'].get('status')}",
            f"- Late-bound public skeletons / hide private material: {report['b8']['late_bound_private_challenge_contract_gate'].get('public_skeleton_file_count')} / {report['b8']['late_bound_private_challenge_contract_gate'].get('public_skeletons_hide_private_material')}",
            f"- Late-bound deterministic data blocker / late-binding alone sufficient: {report['b8']['late_bound_private_challenge_contract_gate'].get('public_data_transcript_classically_predictable')} / {report['b8']['late_bound_private_challenge_contract_gate'].get('late_bound_private_challenge_alone_sufficient_for_soundness')}",
            f"- Late-bound gates passed/failed: {report['b8']['late_bound_private_challenge_contract_gate'].get('passed_gate_count')} / {report['b8']['late_bound_private_challenge_contract_gate'].get('failed_gate_count')}",
            f"- Late-bound contract result/markdown/skeleton-dir exists: {report['b8']['late_bound_private_challenge_contract_gate'].get('result_exists')} / {report['b8']['late_bound_private_challenge_contract_gate'].get('markdown_exists')} / {report['b8']['late_bound_private_challenge_contract_gate'].get('public_skeleton_directory_exists')}",
            f"- Non-stabilizer pilot status: {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('status')}",
            f"- Non-stabilizer pilot circuits / deterministic blocker removed: {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('circuit_count')} / {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('public_deterministic_transcript_blocker_removed')}",
            f"- Non-stabilizer pilot entropy / max output probability: {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('minimum_min_entropy_bits')} / {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('maximum_output_probability')}",
            f"- Non-stabilizer pilot gates passed/failed: {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('passed_gate_count')} / {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('failed_gate_count')}",
            f"- Non-stabilizer pilot hardware execution / advantage / BQP separation: {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('hardware_execution_performed')} / {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('quantum_advantage_claimed')} / {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('bqp_separation_claimed')}",
            f"- Non-stabilizer pilot result/markdown/directory exists: {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('result_exists')} / {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('markdown_exists')} / {report['b8']['nonstabilizer_late_bound_transcript_pilot'].get('nonstabilizer_pilot_directory_exists')}",
            f"- Support-spoofer gate status: {report['b8']['nonstabilizer_support_spoofer_gate'].get('status')}",
            f"- Support-spoofer circuits / spoofers / rows: {report['b8']['nonstabilizer_support_spoofer_gate'].get('circuit_count')} / {report['b8']['nonstabilizer_support_spoofer_gate'].get('spoofer_count')} / {report['b8']['nonstabilizer_support_spoofer_gate'].get('attack_row_count')}",
            f"- Support-spoofer exact success / support acceptance: {report['b8']['nonstabilizer_support_spoofer_gate'].get('max_exact_transcript_success_probability')} / {report['b8']['nonstabilizer_support_spoofer_gate'].get('max_support_acceptance_rate')}",
            f"- Support-spoofer support-only soundness rejected / exact blocker survives: {report['b8']['nonstabilizer_support_spoofer_gate'].get('support_only_verifier_soundness_rejected')} / {report['b8']['nonstabilizer_support_spoofer_gate'].get('deterministic_exact_transcript_blocker_survives')}",
            f"- Support-spoofer result/markdown exists: {report['b8']['nonstabilizer_support_spoofer_gate'].get('result_exists')} / {report['b8']['nonstabilizer_support_spoofer_gate'].get('markdown_exists')}",
            f"- Generative spoofer status: {report['b8']['generative_spoofer_refresh'].get('status')}",
            f"- Generative spoofer configurations: {report['b8']['generative_spoofer_refresh'].get('configuration_count')}",
            f"- Generative spoofer maximum learned soundness: {report['b8']['generative_spoofer_refresh'].get('maximum_learned_soundness')}",
            f"- Generative spoofer safe high-leakage refresh modes: {report['b8']['generative_spoofer_refresh'].get('safe_high_leakage_refresh_modes')}",
            f"- Generative spoofer unsafe high-leakage refresh modes: {report['b8']['generative_spoofer_refresh'].get('unsafe_high_leakage_refresh_modes')}",
            f"- Generative spoofer result/markdown exists: {report['b8']['generative_spoofer_refresh'].get('result_exists')} / {report['b8']['generative_spoofer_refresh'].get('markdown_exists')}",
            "",
            "## B9 Local Hamiltonian Gap Lab Status",
            "",
            f"- Status: {report['b9']['local_hamiltonian_gap_lab'].get('status')}",
            f"- Model status: {report['b9']['local_hamiltonian_gap_lab'].get('model_status')}",
            f"- Configurations: {report['b9']['local_hamiltonian_gap_lab'].get('configuration_count')}",
            f"- Locality-preserving candidates: {report['b9']['local_hamiltonian_gap_lab'].get('locality_preserving_candidate_count')}",
            f"- Candidate passes: {report['b9']['local_hamiltonian_gap_lab'].get('candidate_pass_count')}",
            f"- Counterexample candidates: {report['b9']['local_hamiltonian_gap_lab'].get('counterexample_candidate_count')}",
            f"- Max local normalized-gap ratio: {report['b9']['local_hamiltonian_gap_lab'].get('max_local_candidate_normalized_gap_ratio')}",
            f"- Max dense-filter raw gap ratio: {report['b9']['local_hamiltonian_gap_lab'].get('max_dense_filter_gap_ratio')}",
            f"- Result exists: {report['b9']['local_hamiltonian_gap_lab'].get('result_exists')}",
            f"- Failed gap-amplification lemma status: {report['b9']['failed_gap_amplification_lemma'].get('status')}",
            f"- Failed gap-amplification theorem count: {report['b9']['failed_gap_amplification_lemma'].get('theorem_count')}",
            f"- Failed gap-amplification strict counterexamples: {report['b9']['failed_gap_amplification_lemma'].get('strict_counterexample_count')}",
            f"- Failed gap-amplification dense locality traps: {report['b9']['failed_gap_amplification_lemma'].get('dense_locality_trap_count')}",
            f"- Failed gap-amplification proof obligations: {report['b9']['failed_gap_amplification_lemma'].get('proof_obligation_count')}",
            f"- Failed gap-amplification explicitly not Quantum PCP proof: {report['b9']['failed_gap_amplification_lemma'].get('explicit_not_quantum_pcp_proof')}",
            f"- Failed gap-amplification global impossibility claimed: {report['b9']['failed_gap_amplification_lemma'].get('global_gap_amplification_impossibility_claimed')}",
            f"- Failed gap-amplification validation errors: {report['b9']['failed_gap_amplification_lemma'].get('validation_error_count')}",
            f"- Failed gap-amplification result/markdown exists: {report['b9']['failed_gap_amplification_lemma'].get('result_exists')} / {report['b9']['failed_gap_amplification_lemma'].get('markdown_exists')}",
            f"- Symbolic gap skeleton status: {report['b9']['symbolic_gap_skeleton'].get('status')}",
            f"- Symbolic gap skeleton target: {report['b9']['symbolic_gap_skeleton'].get('proof_assistant_target')}",
            f"- Symbolic gap skeleton definitions/theorems: {report['b9']['symbolic_gap_skeleton'].get('symbolic_definition_count')} / {report['b9']['symbolic_gap_skeleton'].get('theorem_skeleton_count')}",
            f"- Symbolic gap skeleton open obligations: {report['b9']['symbolic_gap_skeleton'].get('open_obligation_count')}",
            f"- Symbolic gap skeleton checked/formal theorem: {report['b9']['symbolic_gap_skeleton'].get('proof_assistant_checked')} / {report['b9']['symbolic_gap_skeleton'].get('formal_theorem_proved')}",
            f"- Symbolic gap skeleton explicitly not Quantum PCP proof: {report['b9']['symbolic_gap_skeleton'].get('explicit_not_quantum_pcp_proof')}",
            f"- Symbolic gap skeleton validation errors: {report['b9']['symbolic_gap_skeleton'].get('validation_error_count')}",
            f"- Symbolic gap skeleton result/markdown/lean exists: {report['b9']['symbolic_gap_skeleton'].get('result_exists')} / {report['b9']['symbolic_gap_skeleton'].get('markdown_exists')} / {report['b9']['symbolic_gap_skeleton'].get('lean_exists')}",
            f"- Named-family bound status: {report['b9']['named_family_width_locality_bound'].get('status')}",
            f"- Named-family bound family: {report['b9']['named_family_width_locality_bound'].get('named_family')}",
            f"- Named-family bound rows/scaling/locality: {report['b9']['named_family_width_locality_bound'].get('rows_matched')} / {report['b9']['named_family_width_locality_bound'].get('scaling_factor')} / {report['b9']['named_family_width_locality_bound'].get('max_locality')}",
            f"- Named-family bound uniform/locality/raw/norm-invariant/rejected: {report['b9']['named_family_width_locality_bound'].get('all_terms_scaled_uniformly')} / {report['b9']['named_family_width_locality_bound'].get('locality_bound_preserved')} / {report['b9']['named_family_width_locality_bound'].get('raw_gap_amplifies')} / {report['b9']['named_family_width_locality_bound'].get('normalized_gap_invariant_under_uniform_scaling')} / {report['b9']['named_family_width_locality_bound'].get('certificate_rejected')}",
            f"- Named-family bound checked/formal theorem: {report['b9']['named_family_width_locality_bound'].get('proof_assistant_checked')} / {report['b9']['named_family_width_locality_bound'].get('formal_theorem_proved')}",
            f"- Named-family bound proof-check status: {report['b9']['named_family_width_locality_bound'].get('proof_assistant_check_status')}",
            f"- Named-family bound explicitly not Quantum PCP proof: {report['b9']['named_family_width_locality_bound'].get('explicit_not_quantum_pcp_proof')}",
            f"- Named-family bound validation errors: {report['b9']['named_family_width_locality_bound'].get('validation_error_count')}",
            f"- Named-family bound result/markdown/lean exists: {report['b9']['named_family_width_locality_bound'].get('result_exists')} / {report['b9']['named_family_width_locality_bound'].get('markdown_exists')} / {report['b9']['named_family_width_locality_bound'].get('lean_exists')}",
            f"- Parametric certificate status: {report['b9']['cluster_stabilizer_parametric_certificate'].get('status')}",
            f"- Parametric certificate family: {report['b9']['cluster_stabilizer_parametric_certificate'].get('named_family')}",
            f"- Parametric certificate n-min/rows: {report['b9']['cluster_stabilizer_parametric_certificate'].get('parameterized_n_min')} / {report['b9']['cluster_stabilizer_parametric_certificate'].get('finite_rows_checked')}",
            f"- Parametric certificate support/locality/scale: {report['b9']['cluster_stabilizer_parametric_certificate'].get('support_size_set')} / {report['b9']['cluster_stabilizer_parametric_certificate'].get('max_locality')} / {report['b9']['cluster_stabilizer_parametric_certificate'].get('uniform_scale')}",
            f"- Parametric certificate normalized-gap invariant/rejected: {report['b9']['cluster_stabilizer_parametric_certificate'].get('normalized_gap_invariant_symbolically')} / {report['b9']['cluster_stabilizer_parametric_certificate'].get('certificate_rejected')}",
            f"- Parametric certificate local/formal theorem: {report['b9']['cluster_stabilizer_parametric_certificate'].get('local_verifier_checked')} / {report['b9']['cluster_stabilizer_parametric_certificate'].get('formal_theorem_proved')}",
            f"- Parametric certificate explicitly not Quantum PCP proof: {report['b9']['cluster_stabilizer_parametric_certificate'].get('explicit_not_quantum_pcp_proof')}",
            f"- Parametric certificate validation errors: {report['b9']['cluster_stabilizer_parametric_certificate'].get('validation_error_count')}",
            f"- Parametric certificate result/markdown exists: {report['b9']['cluster_stabilizer_parametric_certificate'].get('result_exists')} / {report['b9']['cluster_stabilizer_parametric_certificate'].get('markdown_exists')}",
            "",
            "## B10 BQP Boundary Graph Status",
            "",
            f"- Status: {report['b10']['bqp_boundary_graph'].get('status')}",
            f"- Model status: {report['b10']['bqp_boundary_graph'].get('model_status')}",
            f"- Nodes: {report['b10']['bqp_boundary_graph'].get('node_count')}",
            f"- Edges: {report['b10']['bqp_boundary_graph'].get('edge_count')}",
            f"- Connected components: {report['b10']['bqp_boundary_graph'].get('connected_component_count')}",
            f"- Advantage-preserving edges: {report['b10']['bqp_boundary_graph'].get('advantage_preserving_edge_count')}",
            f"- Fragile edges: {report['b10']['bqp_boundary_graph'].get('fragile_edge_count')}",
            f"- Restricted theorem targets: {report['b10']['bqp_boundary_graph'].get('restricted_theorem_target_count')}",
            f"- Top failure modes: {report['b10']['bqp_boundary_graph'].get('top_failure_modes')}",
            f"- Result exists: {report['b10']['bqp_boundary_graph'].get('result_exists')}",
            f"- Formal theorem target status: {report['b10']['formal_theorem_targets'].get('status')}",
            f"- Formal theorem target count: {report['b10']['formal_theorem_targets'].get('target_count')}",
            f"- Formal theorem target types: {report['b10']['formal_theorem_targets'].get('target_types')}",
            f"- Formal theorem target dependencies: {report['b10']['formal_theorem_targets'].get('dependency_ids')}",
            f"- Formal theorem target validation errors: {report['b10']['formal_theorem_targets'].get('validation_error_count')}",
            f"- Formal theorem target result exists: {report['b10']['formal_theorem_targets'].get('result_exists')}",
            f"- B10-T2 refresh-boundary status: {report['b10']['t2_minimum_refresh_spoofer_boundary'].get('status')}",
            f"- B10-T2 refresh-boundary maximum learned soundness: {report['b10']['t2_minimum_refresh_spoofer_boundary'].get('maximum_learned_soundness')}",
            f"- B10-T2 refresh-boundary safe modes: {report['b10']['t2_minimum_refresh_spoofer_boundary'].get('safe_high_leakage_refresh_modes')}",
            f"- B10-T2 refresh-boundary unsafe modes: {report['b10']['t2_minimum_refresh_spoofer_boundary'].get('unsafe_high_leakage_refresh_modes')}",
            f"- B10-T2 refresh-boundary explicitly not BQP separation: {report['b10']['t2_minimum_refresh_spoofer_boundary'].get('explicit_not_bqp_separation')}",
            f"- B10-T2 refresh-boundary result/markdown exists: {report['b10']['t2_minimum_refresh_spoofer_boundary'].get('result_exists')} / {report['b10']['t2_minimum_refresh_spoofer_boundary'].get('markdown_exists')}",
            f"- B10-T2 proof-gate status: {report['b10']['t2_refresh_proof_obligation_gate'].get('status')}",
            f"- B10-T2 proof-gate lemma status: {report['b10']['t2_refresh_proof_obligation_gate'].get('lemma_status')}",
            f"- B10-T2 proof-gate obligations: {report['b10']['t2_refresh_proof_obligation_gate'].get('proof_obligation_count')}",
            f"- B10-T2 proof-gate unsafe modes: {report['b10']['t2_refresh_proof_obligation_gate'].get('unsafe_high_leakage_refresh_modes')}",
            f"- B10-T2 proof-gate hardware verifier instantiated: {report['b10']['t2_refresh_proof_obligation_gate'].get('hardware_randomized_measurement_circuits_instantiated')}",
            f"- B10-T2 proof-gate validation errors: {report['b10']['t2_refresh_proof_obligation_gate'].get('validation_error_count')}",
            f"- B10-T2 proof-gate result/markdown exists: {report['b10']['t2_refresh_proof_obligation_gate'].get('result_exists')} / {report['b10']['t2_refresh_proof_obligation_gate'].get('markdown_exists')}",
            f"- B10-T2 restricted lemma status: {report['b10']['t2_restricted_soundness_lemma'].get('status')}",
            f"- B10-T2 restricted lemma theorem/corollary count: {report['b10']['t2_restricted_soundness_lemma'].get('theorem_count')} / {report['b10']['t2_restricted_soundness_lemma'].get('corollary_count')}",
            f"- B10-T2 restricted lemma single-unknown-mask bound: {report['b10']['t2_restricted_soundness_lemma'].get('single_unknown_mask_soundness_bound')}",
            f"- B10-T2 restricted lemma hardware verifier instantiated: {report['b10']['t2_restricted_soundness_lemma'].get('hardware_randomized_measurement_circuits_instantiated')}",
            f"- B10-T2 restricted lemma sampling hardness proved: {report['b10']['t2_restricted_soundness_lemma'].get('sampling_hardness_proved')}",
            f"- B10-T2 restricted lemma validation errors: {report['b10']['t2_restricted_soundness_lemma'].get('validation_error_count')}",
            f"- B10-T2 restricted lemma result/markdown exists: {report['b10']['t2_restricted_soundness_lemma'].get('result_exists')} / {report['b10']['t2_restricted_soundness_lemma'].get('markdown_exists')}",
            f"- B10-T2 transcript simulator status: {report['b10']['t2_transcript_leakage_simulator'].get('status')}",
            f"- B10-T2 transcript simulator configurations: {report['b10']['t2_transcript_leakage_simulator'].get('configuration_count')}",
            f"- B10-T2 transcript simulator honest completeness: {report['b10']['t2_transcript_leakage_simulator'].get('minimum_honest_completeness')}",
            f"- B10-T2 transcript simulator max refreshed high-leakage soundness: {report['b10']['t2_transcript_leakage_simulator'].get('max_soundness_refresh_independent_high_leakage')}",
            f"- B10-T2 transcript simulator min refreshed high-leakage unknown independent predicates: {report['b10']['t2_transcript_leakage_simulator'].get('min_unknown_independent_count_refresh_high_leakage')}",
            f"- B10-T2 transcript simulator unsafe modes: {report['b10']['t2_transcript_leakage_simulator'].get('unsafe_high_leakage_modes')}",
            f"- B10-T2 transcript simulator hardware verifier instantiated: {report['b10']['t2_transcript_leakage_simulator'].get('hardware_randomized_measurement_circuits_instantiated')}",
            f"- B10-T2 transcript simulator sampling hardness proved: {report['b10']['t2_transcript_leakage_simulator'].get('sampling_hardness_proved')}",
            f"- B10-T2 transcript simulator validation errors: {report['b10']['t2_transcript_leakage_simulator'].get('validation_error_count')}",
            f"- B10-T2 transcript simulator result/markdown exists: {report['b10']['t2_transcript_leakage_simulator'].get('result_exists')} / {report['b10']['t2_transcript_leakage_simulator'].get('markdown_exists')}",
            f"- B10-T2 device-noise bridge status: {report['b10']['t2_device_noise_transcript_bridge'].get('status')}",
            f"- B10-T2 device-noise bridge configurations/profiles: {report['b10']['t2_device_noise_transcript_bridge'].get('configuration_count')} / {report['b10']['t2_device_noise_transcript_bridge'].get('device_profile_count')}",
            f"- B10-T2 device-noise bridge safe refresh modes: {report['b10']['t2_device_noise_transcript_bridge'].get('bridge_safe_refresh_modes')}",
            f"- B10-T2 device-noise bridge max safe high-leakage soundness: {report['b10']['t2_device_noise_transcript_bridge'].get('max_soundness_bridge_safe_high_leakage')}",
            f"- B10-T2 device-noise bridge margin-sensitive modes: {report['b10']['t2_device_noise_transcript_bridge'].get('margin_sensitive_refresh_modes')}",
            f"- B10-T2 device-noise bridge unsafe profiles: {report['b10']['t2_device_noise_transcript_bridge'].get('unsafe_device_profiles')}",
            f"- B10-T2 device-noise bridge hardware verifier instantiated: {report['b10']['t2_device_noise_transcript_bridge'].get('hardware_randomized_measurement_circuits_instantiated')}",
            f"- B10-T2 device-noise bridge validation errors: {report['b10']['t2_device_noise_transcript_bridge'].get('validation_error_count')}",
            f"- B10-T2 device-noise bridge result/markdown exists: {report['b10']['t2_device_noise_transcript_bridge'].get('result_exists')} / {report['b10']['t2_device_noise_transcript_bridge'].get('markdown_exists')}",
            f"- B10-T2 Qiskit/Aer bridge status: {report['b10']['t2_qiskit_aer_verifier_bridge'].get('status')}",
            f"- B10-T2 Qiskit/Aer bridge circuits: {report['b10']['t2_qiskit_aer_verifier_bridge'].get('aer_circuit_count')}",
            f"- B10-T2 Qiskit/Aer bridge max qubits incl. ancilla: {report['b10']['t2_qiskit_aer_verifier_bridge'].get('max_circuit_qubits_with_ancilla')}",
            f"- B10-T2 Qiskit/Aer bridge semantic mismatches: {report['b10']['t2_qiskit_aer_verifier_bridge'].get('aer_semantic_mismatch_count')}",
            f"- B10-T2 Qiskit/Aer bridge honest completeness: {report['b10']['t2_qiskit_aer_verifier_bridge'].get('minimum_aer_honest_completeness')}",
            f"- B10-T2 Qiskit/Aer bridge source soundness: {report['b10']['t2_qiskit_aer_verifier_bridge'].get('source_device_noise_max_safe_high_leakage_soundness')}",
            f"- B10-T2 Qiskit/Aer bridge hardware circuits instantiated: {report['b10']['t2_qiskit_aer_verifier_bridge'].get('hardware_executable_randomized_measurement_circuits_instantiated')}",
            f"- B10-T2 Qiskit/Aer bridge hardware execution performed: {report['b10']['t2_qiskit_aer_verifier_bridge'].get('hardware_execution_performed')}",
            f"- B10-T2 Qiskit/Aer bridge validation errors: {report['b10']['t2_qiskit_aer_verifier_bridge'].get('validation_error_count')}",
            f"- B10-T2 Qiskit/Aer bridge result/markdown exists: {report['b10']['t2_qiskit_aer_verifier_bridge'].get('result_exists')} / {report['b10']['t2_qiskit_aer_verifier_bridge'].get('markdown_exists')}",
            f"- B10-T2 noisy Aer bridge status: {report['b10']['t2_noisy_aer_verifier_bridge'].get('status')}",
            f"- B10-T2 noisy Aer bridge circuits: {report['b10']['t2_noisy_aer_verifier_bridge'].get('noisy_aer_circuit_count')}",
            f"- B10-T2 noisy Aer bridge max qubits incl. ancilla: {report['b10']['t2_noisy_aer_verifier_bridge'].get('max_circuit_qubits_with_ancilla')}",
            f"- B10-T2 noisy Aer bridge safe honest/adversary acceptance: {report['b10']['t2_noisy_aer_verifier_bridge'].get('minimum_safe_noisy_honest_acceptance')} / {report['b10']['t2_noisy_aer_verifier_bridge'].get('maximum_safe_noisy_adversary_acceptance')}",
            f"- B10-T2 noisy Aer bridge honest predicate-bit error: {report['b10']['t2_noisy_aer_verifier_bridge'].get('maximum_safe_noisy_honest_predicate_bit_error_rate')}",
            f"- B10-T2 noisy Aer bridge safe unknown predicates: {report['b10']['t2_noisy_aer_verifier_bridge'].get('minimum_safe_noisy_unknown_independent_count')}",
            f"- B10-T2 noisy Aer bridge unsafe profiles: {report['b10']['t2_noisy_aer_verifier_bridge'].get('unsafe_noisy_device_profiles')}",
            f"- B10-T2 noisy Aer bridge hardware execution performed: {report['b10']['t2_noisy_aer_verifier_bridge'].get('hardware_execution_performed')}",
            f"- B10-T2 noisy Aer bridge validation errors: {report['b10']['t2_noisy_aer_verifier_bridge'].get('validation_error_count')}",
            f"- B10-T2 noisy Aer bridge result/markdown exists: {report['b10']['t2_noisy_aer_verifier_bridge'].get('result_exists')} / {report['b10']['t2_noisy_aer_verifier_bridge'].get('markdown_exists')}",
            f"- B10-T2 backend-calibrated bridge status: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('status')}",
            f"- B10-T2 backend-calibrated bridge circuits: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('backend_calibrated_aer_circuit_count')}",
            f"- B10-T2 backend-calibrated bridge max qubits incl. ancilla: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('max_circuit_qubits_with_ancilla')}",
            f"- B10-T2 backend-calibrated bridge safe honest/adversary acceptance: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('minimum_safe_calibrated_honest_acceptance')} / {report['b10']['t2_backend_calibrated_verifier_bridge'].get('maximum_safe_calibrated_adversary_acceptance')}",
            f"- B10-T2 backend-calibrated bridge honest predicate-bit error: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('maximum_safe_calibrated_honest_predicate_bit_error_rate')}",
            f"- B10-T2 backend-calibrated bridge safe unknown predicates: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('minimum_safe_calibrated_unknown_independent_count')}",
            f"- B10-T2 backend-calibrated bridge unsafe refresh modes: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('unsafe_calibrated_refresh_modes')}",
            f"- B10-T2 backend-calibrated bridge GenericBackendV2 used: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('qiskit_generic_backend_v2_used')}",
            f"- B10-T2 backend-calibrated bridge real backend properties used: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('real_backend_properties_used')}",
            f"- B10-T2 backend-calibrated bridge hardware execution performed: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('hardware_execution_performed')}",
            f"- B10-T2 backend-calibrated bridge validation errors: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('validation_error_count')}",
            f"- B10-T2 backend-calibrated bridge result/markdown exists: {report['b10']['t2_backend_calibrated_verifier_bridge'].get('result_exists')} / {report['b10']['t2_backend_calibrated_verifier_bridge'].get('markdown_exists')}",
            f"- B10-T1 proof status: {report['b10']['t1_negative_boundary_proof'].get('status')}",
            f"- B10-T1 proof result: {report['b10']['t1_negative_boundary_proof'].get('proof_result')}",
            f"- B10-T1 theorem count: {report['b10']['t1_negative_boundary_proof'].get('theorem_count')}",
            f"- B10-T1 open obligations: {report['b10']['t1_negative_boundary_proof'].get('open_obligation_count')}",
            f"- B10-T1 validation errors: {report['b10']['t1_negative_boundary_proof'].get('validation_error_count')}",
            f"- B10-T1 explicitly not BQP separation: {report['b10']['t1_negative_boundary_proof'].get('explicit_not_bqp_separation')}",
            f"- B10-T1 result exists: {report['b10']['t1_negative_boundary_proof'].get('result_exists')}",
            f"- B10-T1 source-backed status: {report['b10']['t1_source_backed_boundaries'].get('status')}",
            f"- B10-T1 source count: {report['b10']['t1_source_backed_boundaries'].get('source_count')}",
            f"- B10-T1 denominator baselines: {report['b10']['t1_source_backed_boundaries'].get('baseline_count')}",
            f"- B10-T1 boundary checks: {report['b10']['t1_source_backed_boundaries'].get('boundary_check_count')}",
            f"- B10-T1 source-backed validation errors: {report['b10']['t1_source_backed_boundaries'].get('validation_error_count')}",
            f"- B10-T1 source-backed explicitly not BQP separation: {report['b10']['t1_source_backed_boundaries'].get('explicit_not_bqp_separation')}",
            f"- B10-T1 source-backed result exists: {report['b10']['t1_source_backed_boundaries'].get('result_exists')}",
            f"- B10-T1 numerical-table status: {report['b10']['t1_numerical_denominator_table'].get('status')}",
            f"- B10-T1 numerical-table families: {report['b10']['t1_numerical_denominator_table'].get('family_count')}",
            f"- B10-T1 numerical-table instances: {report['b10']['t1_numerical_denominator_table'].get('instance_count')}",
            f"- B10-T1 numerical-table CG instances: {report['b10']['t1_numerical_denominator_table'].get('cg_instance_count')}",
            f"- B10-T1 numerical-table LSQR instances: {report['b10']['t1_numerical_denominator_table'].get('lsqr_instance_count')}",
            f"- B10-T1 numerical-table max residual: {report['b10']['t1_numerical_denominator_table'].get('max_relative_residual')}",
            f"- B10-T1 numerical-table validation errors: {report['b10']['t1_numerical_denominator_table'].get('validation_error_count')}",
            f"- B10-T1 numerical-table explicitly not BQP separation: {report['b10']['t1_numerical_denominator_table'].get('explicit_not_bqp_separation')}",
            f"- B10-T1 numerical-table result exists: {report['b10']['t1_numerical_denominator_table'].get('result_exists')}",
            f"- B10-T1 D5 table status: {report['b10']['t1_d5_observable_denominator_table'].get('status')}",
            f"- B10-T1 D5 table dependency: {report['b10']['t1_d5_observable_denominator_table'].get('dependency_benchmark')}",
            f"- B10-T1 D5 table instances: {report['b10']['t1_d5_observable_denominator_table'].get('instance_count')}",
            f"- B10-T1 D5 table max Hilbert dimension: {report['b10']['t1_d5_observable_denominator_table'].get('max_hilbert_dimension')}",
            f"- B10-T1 D5 table max residual: {report['b10']['t1_d5_observable_denominator_table'].get('max_relative_residual')}",
            f"- B10-T1 D5 table validation errors: {report['b10']['t1_d5_observable_denominator_table'].get('validation_error_count')}",
            f"- B10-T1 D5 table explicitly not BQP separation: {report['b10']['t1_d5_observable_denominator_table'].get('explicit_not_bqp_separation')}",
            f"- B10-T1 D5 table result exists: {report['b10']['t1_d5_observable_denominator_table'].get('result_exists')}",
            f"- B10-T1 D5-B3 table status: {report['b10']['t1_d5_b3_molecular_observable_table'].get('status')}",
            f"- B10-T1 D5-B3 table dependency: {report['b10']['t1_d5_b3_molecular_observable_table'].get('dependency_benchmark')}",
            f"- B10-T1 D5-B3 table instances: {report['b10']['t1_d5_b3_molecular_observable_table'].get('instance_count')}",
            f"- B10-T1 D5-B3 table max matrix dimension: {report['b10']['t1_d5_b3_molecular_observable_table'].get('max_matrix_dimension')}",
            f"- B10-T1 D5-B3 table max residual: {report['b10']['t1_d5_b3_molecular_observable_table'].get('max_relative_residual')}",
            f"- B10-T1 D5-B3 table validation errors: {report['b10']['t1_d5_b3_molecular_observable_table'].get('validation_error_count')}",
            f"- B10-T1 D5-B3 table explicitly not BQP separation: {report['b10']['t1_d5_b3_molecular_observable_table'].get('explicit_not_bqp_separation')}",
            f"- B10-T1 D5-B3 table result exists: {report['b10']['t1_d5_b3_molecular_observable_table'].get('result_exists')}",
            f"- B10-T1 D5-B3 reaction table status: {report['b10']['t1_d5_b3_reaction_observable_table'].get('status')}",
            f"- B10-T1 D5-B3 reaction table dependency: {report['b10']['t1_d5_b3_reaction_observable_table'].get('dependency_benchmark')}",
            f"- B10-T1 D5-B3 reaction table instances: {report['b10']['t1_d5_b3_reaction_observable_table'].get('instance_count')}",
            f"- B10-T1 D5-B3 reaction table max response dimension: {report['b10']['t1_d5_b3_reaction_observable_table'].get('max_response_dimension')}",
            f"- B10-T1 D5-B3 reaction table max residual: {report['b10']['t1_d5_b3_reaction_observable_table'].get('max_relative_residual')}",
            f"- B10-T1 D5-B3 reaction table validation errors: {report['b10']['t1_d5_b3_reaction_observable_table'].get('validation_error_count')}",
            f"- B10-T1 D5-B3 reaction table explicitly not BQP separation: {report['b10']['t1_d5_b3_reaction_observable_table'].get('explicit_not_bqp_separation')}",
            f"- B10-T1 D5-B3 reaction table result exists: {report['b10']['t1_d5_b3_reaction_observable_table'].get('result_exists')}",
            f"- B10-T1 D5-B3 correlated table status: {report['b10']['t1_d5_b3_correlated_reference_table'].get('status')}",
            f"- B10-T1 D5-B3 correlated table dependency: {report['b10']['t1_d5_b3_correlated_reference_table'].get('dependency_benchmark')}",
            f"- B10-T1 D5-B3 correlated table instances: {report['b10']['t1_d5_b3_correlated_reference_table'].get('instance_count')}",
            f"- B10-T1 D5-B3 correlated table methods: {report['b10']['t1_d5_b3_correlated_reference_table'].get('method_count')}",
            f"- B10-T1 D5-B3 correlated table max |CCSD-RHF derivative shift|: {report['b10']['t1_d5_b3_correlated_reference_table'].get('max_abs_ccsd_derivative_shift_vs_rhf')}",
            f"- B10-T1 D5-B3 correlated table validation errors: {report['b10']['t1_d5_b3_correlated_reference_table'].get('validation_error_count')}",
            f"- B10-T1 D5-B3 correlated table explicitly not BQP separation: {report['b10']['t1_d5_b3_correlated_reference_table'].get('explicit_not_bqp_separation')}",
            f"- B10-T1 D5-B3 correlated table result exists: {report['b10']['t1_d5_b3_correlated_reference_table'].get('result_exists')}",
            f"- B10-T1 D5-B3 FCI table status: {report['b10']['t1_d5_b3_fci_reference_table'].get('status')}",
            f"- B10-T1 D5-B3 FCI table dependency: {report['b10']['t1_d5_b3_fci_reference_table'].get('dependency_benchmark')}",
            f"- B10-T1 D5-B3 FCI table instances: {report['b10']['t1_d5_b3_fci_reference_table'].get('instance_count')}",
            f"- B10-T1 D5-B3 FCI table methods: {report['b10']['t1_d5_b3_fci_reference_table'].get('method_count')}",
            f"- B10-T1 D5-B3 FCI table max |FCI-RHF derivative shift|: {report['b10']['t1_d5_b3_fci_reference_table'].get('max_abs_fci_derivative_shift_vs_rhf')}",
            f"- B10-T1 D5-B3 FCI table max |FCI-CCSD derivative shift|: {report['b10']['t1_d5_b3_fci_reference_table'].get('max_abs_fci_derivative_shift_vs_ccsd')}",
            f"- B10-T1 D5-B3 FCI table validation errors: {report['b10']['t1_d5_b3_fci_reference_table'].get('validation_error_count')}",
            f"- B10-T1 D5-B3 FCI table explicitly not BQP separation: {report['b10']['t1_d5_b3_fci_reference_table'].get('explicit_not_bqp_separation')}",
            f"- B10-T1 D5-B3 FCI table result exists: {report['b10']['t1_d5_b3_fci_reference_table'].get('result_exists')}",
            f"- B10-T1 B3/B5 denominator comparison status: {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('status')}",
            f"- B10-T1 B3/B5 routes / negative-boundary routes: {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('route_count')} / {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('negative_boundary_route_count')}",
            f"- B10-T1 B3 denominator wins / max optimizer-loop shots: {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('b3_selected_ci_larger_basis_denominator_beaten_count')} / {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('b3_max_optimizer_loop_total_shots_lower_bound')}",
            f"- B10-T1 B5 non-oracle wins / seeded MPS wins / variational-over-seeded wins: {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('b5_non_oracle_rows_beating_oracle_boundary_field')} / {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('b5_seeded_mps_rows_beating_non_oracle_embedding')} / {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('b5_variational_mps_rows_beating_seeded_mps_pressure_reference')}",
            f"- B10-T1 B3 demoted / B5 positive-ready / BQP separation / quantum advantage: {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('b3_demoted')} / {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('b5_positive_claim_ready')} / {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('bqp_separation_claimed')} / {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('quantum_advantage_claimed')}",
            f"- B10-T1 B3/B5 comparison validation errors: {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('validation_error_count')}",
            f"- B10-T1 B3/B5 comparison result/markdown exists: {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('result_exists')} / {report['b10']['t1_b3_b5_denominator_boundary_comparison'].get('markdown_exists')}",
            f"- B10-T1 missing-assumption note status: {report['b10']['t1_missing_assumption_note'].get('status')}",
            f"- B10-T1 missing-assumption theorem skeletons / missing assumptions / proof obligations: {report['b10']['t1_missing_assumption_note'].get('theorem_skeleton_count')} / {report['b10']['t1_missing_assumption_note'].get('missing_assumption_count')} / {report['b10']['t1_missing_assumption_note'].get('proof_obligation_count')}",
            f"- B10-T1 missing-assumption dequantization theorem / sampling-access theorem / BQP separation / quantum advantage: {report['b10']['t1_missing_assumption_note'].get('dequantization_theorem_proved')} / {report['b10']['t1_missing_assumption_note'].get('sampling_access_theorem_proved')} / {report['b10']['t1_missing_assumption_note'].get('bqp_separation_claimed')} / {report['b10']['t1_missing_assumption_note'].get('quantum_advantage_claimed')}",
            f"- B10-T1 missing-assumption validation errors: {report['b10']['t1_missing_assumption_note'].get('validation_error_count')}",
            f"- B10-T1 missing-assumption result/markdown exists: {report['b10']['t1_missing_assumption_note'].get('result_exists')} / {report['b10']['t1_missing_assumption_note'].get('markdown_exists')}",
            f"- B10-T1 asymptotic access status: {report['b10']['t1_asymptotic_access_contract'].get('status')}",
            f"- B10-T1 asymptotic families / access rows / bridge conditions: {report['b10']['t1_asymptotic_access_contract'].get('family_contract_count')} / {report['b10']['t1_asymptotic_access_contract'].get('access_contract_count')} / {report['b10']['t1_asymptotic_access_contract'].get('bridge_condition_count')}",
            f"- B10-T1 sampling bridge proved / refuted for current evidence: {report['b10']['t1_asymptotic_access_contract'].get('sampling_access_bridge_proved')} / {report['b10']['t1_asymptotic_access_contract'].get('sampling_access_bridge_refuted_for_current_evidence')}",
            f"- B10-T1 general dequantization theorem / sampling-access theorem / BQP separation / quantum advantage: {report['b10']['t1_asymptotic_access_contract'].get('general_dequantization_theorem_proved')} / {report['b10']['t1_asymptotic_access_contract'].get('general_sampling_access_theorem_proved')} / {report['b10']['t1_asymptotic_access_contract'].get('bqp_separation_claimed')} / {report['b10']['t1_asymptotic_access_contract'].get('quantum_advantage_claimed')}",
            f"- B10-T1 asymptotic access validation errors: {report['b10']['t1_asymptotic_access_contract'].get('validation_error_count')}",
            f"- B10-T1 asymptotic access result/markdown exists: {report['b10']['t1_asymptotic_access_contract'].get('result_exists')} / {report['b10']['t1_asymptotic_access_contract'].get('markdown_exists')}",
            f"- B10-T1 B5 same-access bridge status: {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('status')}",
            f"- B10-T1 B5 denominator ladder / sampling requirements / blocking requirements: {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('denominator_ladder_count')} / {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('sampling_requirement_count')} / {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('blocking_sampling_requirement_count')}",
            f"- B10-T1 B5 seeded-MPS-over-non-oracle / variational-over-seeded rows: {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('seeded_mps_rows_beating_non_oracle_embedding')} / {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('variational_mps_rows_beating_seeded_pressure')}",
            f"- B10-T1 B5 sampling oracle / production DMRG / same-access positive route: {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('sampling_oracle_constructed')} / {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('production_dmrg_available')} / {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('same_access_positive_route_ready')}",
            f"- B10-T1 B5 dequantization theorem / sampling-access theorem / BQP separation / quantum advantage: {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('general_dequantization_theorem_proved')} / {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('sampling_access_theorem_proved')} / {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('bqp_separation_claimed')} / {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('quantum_advantage_claimed')}",
            f"- B10-T1 B5 same-access bridge validation errors: {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('validation_error_count')}",
            f"- B10-T1 B5 same-access bridge result/markdown exists: {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('result_exists')} / {report['b10']['t1_b5_same_access_sampling_or_dmrg_bridge'].get('markdown_exists')}",
            f"- B10-T1 B5 response sampler stress status: {report['b10']['t1_b5_response_sampler_cost_stress'].get('status')}",
            f"- B10-T1 B5 response sampler stress instances / confidence z: {report['b10']['t1_b5_response_sampler_cost_stress'].get('instance_count')} / {report['b10']['t1_b5_response_sampler_cost_stress'].get('confidence_z')}",
            f"- B10-T1 B5 response sampler stress min/median/max shots to match seeded MPS: {report['b10']['t1_b5_response_sampler_cost_stress'].get('min_total_shots_to_match_seeded_mps_pressure')} / {report['b10']['t1_b5_response_sampler_cost_stress'].get('median_total_shots_to_match_seeded_mps_pressure')} / {report['b10']['t1_b5_response_sampler_cost_stress'].get('max_total_shots_to_match_seeded_mps_pressure')}",
            f"- B10-T1 B5 response sampler stress max seeded-target prep 2Q floor: {report['b10']['t1_b5_response_sampler_cost_stress'].get('max_optimistic_seeded_target_prep_2q_gate_floor')}",
            f"- B10-T1 B5 response sampler stress rows beating D5 matvec ops for seeded target: {report['b10']['t1_b5_response_sampler_cost_stress'].get('rows_where_sampler_shots_beat_explicit_d5_matvec_ops_for_seeded_target')}",
            f"- B10-T1 B5 response sampler stress sampling oracle / same-access positive route / quantum advantage: {report['b10']['t1_b5_response_sampler_cost_stress'].get('sampling_oracle_constructed')} / {report['b10']['t1_b5_response_sampler_cost_stress'].get('same_access_positive_route_ready')} / {report['b10']['t1_b5_response_sampler_cost_stress'].get('quantum_advantage_claimed')}",
            f"- B10-T1 B5 response sampler stress validation errors: {report['b10']['t1_b5_response_sampler_cost_stress'].get('validation_error_count')}",
            f"- B10-T1 B5 response sampler stress result/markdown exists: {report['b10']['t1_b5_response_sampler_cost_stress'].get('result_exists')} / {report['b10']['t1_b5_response_sampler_cost_stress'].get('markdown_exists')}",
            "",
        ]
    )
    lines.extend(["## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = audit(args.root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
