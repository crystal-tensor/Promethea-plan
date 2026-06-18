#!/usr/bin/env python3
"""Export the frozen 100-problem catalog metadata to JSON.

The canonical human-readable source remains research/problem_catalog_100.md.
This script parses its Frozen Metadata Matrix and emits a machine-readable
snapshot so apps and agents can display the catalog without reopening it.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
from pathlib import Path


TABLE_COLUMNS = [
    "id",
    "problem",
    "discipline_cluster",
    "source_lineage",
    "unresolved_age",
    "core_difficulty",
    "prior_approaches_and_milestones",
    "frozen_project_positioning",
]

FINAL_LOCK_MARKER = "### Per-record final routing lock"
PROBLEM_ENTRY_RE = re.compile(r"^(\d+)\.\s+\*\*(.+?)\*\*\s+-\s+(.*)$")


def discipline_supergroup(problem_id: int) -> str:
    if 1 <= problem_id <= 20:
        return "Mathematics and complexity foundations"
    if 21 <= problem_id <= 30:
        return "Quantum computing core"
    if 31 <= problem_id <= 40:
        return "Physics and cosmology"
    if 41 <= problem_id <= 50:
        return "Chemistry, materials, and energy"
    if 51 <= problem_id <= 60:
        return "Life science and medicine"
    if 61 <= problem_id <= 70:
        return "AI, cognition, and automated science"
    if 71 <= problem_id <= 80:
        return "Earth, climate, and ecology"
    if 81 <= problem_id <= 90:
        return "Cryptography, security, and social systems"
    if 91 <= problem_id <= 100:
        return "Engineering, space, and long-term civilization"
    raise ValueError(f"Unexpected frozen catalog id: {problem_id}")


def split_markdown_row(line: str) -> list[str]:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return [re.sub(r"\s+", " ", cell) for cell in cells]


def parse_problem_summaries(text: str) -> dict[int, dict[str, str]]:
    """Extract the frozen plain-language statement and quantum angle."""
    before_matrix = text.split("## Frozen Metadata Matrix", 1)[0]
    entries: dict[int, dict[str, str]] = {}
    current_id: int | None = None
    current_title = ""
    current_chunks: list[str] = []

    def flush() -> None:
        nonlocal current_id, current_title, current_chunks
        if current_id is None:
            return
        body = re.sub(r"\s+", " ", " ".join(current_chunks)).strip()
        statement = body
        quantum_relevance = ""
        if "Quantum angle:" in body:
            statement, quantum_relevance = body.split("Quantum angle:", 1)
            statement = statement.strip()
            quantum_relevance = quantum_relevance.strip()
        entries[current_id] = {
            "title": current_title,
            "problem_statement": statement.rstrip("."),
            "quantum_relevance": quantum_relevance.rstrip("."),
        }

    for raw_line in before_matrix.splitlines():
        line = raw_line.strip()
        match = PROBLEM_ENTRY_RE.match(line)
        if match:
            flush()
            current_id = int(match.group(1))
            current_title = match.group(2).strip()
            current_chunks = [match.group(3).strip()]
            continue
        if current_id is not None and line and not line.startswith("#"):
            current_chunks.append(line)
    flush()
    return entries


def source_confidence(source_lineage_group: str) -> tuple[str, str]:
    if source_lineage_group == "Clay or other major mathematical challenge":
        return "A", "Official formal challenge list or prize-problem lineage."
    if source_lineage_group == "Institutional roadmap or standards lineage":
        return "A", "Anchored in institutional roadmaps, standards, reports, or global-goal programs."
    if source_lineage_group == "Named proposer, discovery, or named technical lineage":
        return "B", "Anchored in a named scientific discovery, canonical algorithm, or peer-reviewed technical lineage."
    if source_lineage_group == "Research tradition":
        return "B", "Defined by a mature multi-decade research community rather than a single official problem statement."
    return "C", "Catalog synthesis field retained for orientation only."


def completion_aliases(record: dict[str, object], summaries: dict[int, dict[str, str]]) -> dict[str, object]:
    problem_id = int(record["id"])
    source_group = str(record["source_lineage_group"])
    confidence, confidence_reason = source_confidence(source_group)
    summary = summaries.get(problem_id, {})
    problem_statement = summary.get("problem_statement") or str(record["core_difficulty"])
    quantum_relevance = summary.get("quantum_relevance") or "Quantum relevance is recorded in the frozen catalog narrative."
    prior_and_milestones = str(record["prior_approaches_and_milestones"])
    return {
        "title": str(record["problem"]),
        "problem_statement": problem_statement,
        "quantum_relevance": quantum_relevance,
        "origin": str(record["source_lineage"]),
        "who_proposed_or_source": str(record["source_lineage"]),
        "first_formulated_or_crystallized": str(record["source_lineage"]),
        "unresolved_age_years_as_of_2026": str(record["unresolved_age"]),
        "difficulty_core": str(record["core_difficulty"]),
        "prior_approaches": prior_and_milestones,
        "major_milestones": prior_and_milestones,
        "project_positioning": str(record["frozen_project_positioning"]),
        "source_confidence": confidence,
        "source_confidence_reason": confidence_reason,
        "catalog_work_status": "final_frozen_do_not_reopen",
    }


def parse_catalog(markdown_path: Path) -> list[dict[str, object]]:
    text = markdown_path.read_text(encoding="utf-8")
    marker = "## Frozen Metadata Matrix"
    if marker not in text:
        raise ValueError(f"{markdown_path} does not contain {marker!r}")

    summaries = parse_problem_summaries(text)
    rows: list[dict[str, object]] = []
    in_table = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            if in_table and rows:
                break
            continue
        cells = split_markdown_row(line)
        if cells[:3] == ["ID", "Problem", "Discipline cluster"]:
            in_table = True
            continue
        if not in_table or set(cells[0]) <= {"-", ":"}:
            continue
        if len(cells) != len(TABLE_COLUMNS):
            raise ValueError(f"Unexpected table width {len(cells)} in row: {line}")
        record = dict(zip(TABLE_COLUMNS, cells))
        record["id"] = int(record["id"])
        record["discipline_supergroup"] = discipline_supergroup(int(record["id"]))
        record["source_lineage_group"] = classify_source_lineage(str(record["source_lineage"]))
        record["is_top10"] = record["id"] in {25, 22, 49, 16, 38, 37, 21, 30, 17, 11}
        record.update(completion_aliases(record, summaries))
        rows.append(record)

    if len(rows) != 100:
        raise ValueError(f"Expected 100 metadata rows, found {len(rows)}")
    ids = [int(row["id"]) for row in rows]
    if ids != list(range(1, 101)):
        raise ValueError(f"Catalog ids are not the frozen 1..100 sequence: {ids}")
    return rows


def build_export(rows: list[dict[str, object]]) -> dict[str, object]:
    source_lineage_groups = Counter(str(row["source_lineage_group"]) for row in rows)
    return {
        "catalog_id": "future_quantum_hardest_100_frozen_v1",
        "version": "1.0",
        "last_updated": "2026-06-18",
        "status": "frozen",
        "freeze_lock": True,
        "user_freeze_directive_date": "2026-06-18",
        "user_freeze_directive": (
            "Complete the discipline groups, source lineage, and related "
            "metadata for the 100 records, then stop working on the 100-problem "
            "catalog itself. Do not continue expanding, reranking, remapping, "
            "or polishing this catalog unless the user explicitly reopens it."
        ),
        "closure_rule": (
            "Do not expand, rerank, substitute, or keep researching the "
            "100-problem universe itself. Future work must focus on B1-B10 "
            "technical resolution artifacts unless the user explicitly reopens "
            "the catalog."
        ),
        "metadata_completion_scope": [
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
        ],
        "source_confidence_labels": {
            "A": "Official problem list, standard, consensus report, or decadal survey.",
            "B": "Peer-reviewed survey or major institutional technical report.",
            "C": "Reputable secondary synthesis used only for orientation.",
            "D": "Speculative source; should not justify catalog inclusion without stronger support.",
        },
        "top10_problem_ids": [25, 22, 49, 16, 38, 37, 21, 30, 17, 11],
        "top10_mapping": {
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
        },
        "discipline_supergroups": [
            {
                "name": "Mathematics and complexity foundations",
                "id_range": "1-20",
                "role": "Proof barriers, lower bounds, and formal-computation reference problems.",
            },
            {
                "name": "Quantum computing core",
                "id_range": "21-30",
                "role": "Directly actionable quantum software, verification, architecture, and QEC targets.",
            },
            {
                "name": "Physics and cosmology",
                "id_range": "31-40",
                "role": "Fundamental theory and many-body simulation frontiers.",
            },
            {
                "name": "Chemistry, materials, and energy",
                "id_range": "41-50",
                "role": "Molecular, materials, catalyst, and energy problems where simulation may matter.",
            },
            {
                "name": "Life science and medicine",
                "id_range": "51-60",
                "role": "Biological, medical, and public-health systems with high uncertainty.",
            },
            {
                "name": "AI, cognition, and automated science",
                "id_range": "61-70",
                "role": "Agent reliability, formal verification, knowledge governance, and discovery systems.",
            },
            {
                "name": "Earth, climate, and ecology",
                "id_range": "71-80",
                "role": "Planetary-scale simulation, forecasting, and resilience problems.",
            },
            {
                "name": "Cryptography, security, and social systems",
                "id_range": "81-90",
                "role": "Quantum-era security, privacy, governance, and systemic-risk problems.",
            },
            {
                "name": "Engineering, space, and long-term civilization",
                "id_range": "91-100",
                "role": "Infrastructure, education, instrumentation, space, and civilizational-risk targets.",
            },
        ],
        "source_lineage_groups": dict(sorted(source_lineage_groups.items())),
        "non_revision_covenant": (
            "Agents and contributors may cite, display, route, or translate the "
            "100 records, but should not add, remove, rerank, rename IDs, alter "
            "the Top 10 mapping, or repeatedly refine frozen metadata."
        ),
        "record_count": len(rows),
        "completion_audit": {
            "record_count": len(rows),
            "discipline_supergroup_count": 9,
            "source_lineage_group_count": 4,
            "records_with_problem_statement": sum(1 for row in rows if row.get("problem_statement")),
            "records_with_quantum_relevance": sum(1 for row in rows if row.get("quantum_relevance")),
            "records_with_source_confidence": sum(1 for row in rows if row.get("source_confidence")),
            "final_action": "catalog metadata complete; stop further 100-problem catalog work",
        },
        "records": rows,
    }


def classify_source_lineage(source_lineage: str) -> str:
    text = source_lineage.lower()
    institutional_markers = [
        "who",
        "un ",
        "sdg",
        "ipcc",
        "nist",
        "nasa",
        "esa",
        "nae",
        "p5",
        "roadmap",
        "program",
        "standards",
        "report",
    ]
    if "clay" in text:
        return "Clay or other major mathematical challenge"
    if any(marker in text for marker in institutional_markers):
        return "Institutional roadmap or standards lineage"
    if "lineage" in text or "tradition" in text or "research" in text:
        return "Research tradition"
    return "Named proposer, discovery, or named technical lineage"


def final_lock_table(rows: list[dict[str, object]]) -> str:
    lines = [
        FINAL_LOCK_MARKER,
        "",
        "This table is the final per-record routing lock. It is added only to",
        "make the frozen catalog easier for agents and contributors to route;",
        "it does not reopen ranking, naming, or membership of the 100 problems.",
        "",
        "| ID | Discipline supergroup | Source-lineage group |",
        "|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {id} | {discipline_supergroup} | {source_lineage_group} |".format(**row)
        )
    return "\n".join(lines) + "\n"


def update_markdown_final_lock(markdown_path: Path, rows: list[dict[str, object]]) -> None:
    text = markdown_path.read_text(encoding="utf-8")
    table = final_lock_table(rows)
    next_heading = "\n### Top 10 lock"
    if FINAL_LOCK_MARKER in text:
        pattern = re.compile(
            rf"{re.escape(FINAL_LOCK_MARKER)}\n.*?(?=\n### Top 10 lock)",
            re.DOTALL,
        )
        text, count = pattern.subn(table.rstrip(), text, count=1)
        if count != 1:
            raise ValueError("Could not replace existing final routing lock table")
    elif next_heading in text:
        text = text.replace(next_heading, "\n" + table + next_heading, 1)
    else:
        text = text.rstrip() + "\n\n" + table
    markdown_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown", type=Path, default=Path("research/problem_catalog_100.md"))
    parser.add_argument("--json-output", type=Path, default=Path("research/problem_catalog_100.json"))
    args = parser.parse_args()

    rows = parse_catalog(args.markdown)
    payload = build_export(rows)
    update_markdown_final_lock(args.markdown, rows)
    args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"exported {len(rows)} frozen problem records to {args.json_output}")


if __name__ == "__main__":
    main()
