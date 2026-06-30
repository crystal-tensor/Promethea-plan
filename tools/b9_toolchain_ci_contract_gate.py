#!/usr/bin/env python3
"""T-B9-004e: audit the CI handoff for the B9 Lean/Lake proof scaffold."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_TEMPLATE = ROOT / "research" / "ci" / "b9-lean-proof-scaffold.yml"
ACTIVE_WORKFLOW = ROOT / ".github" / "workflows" / "b9-lean-proof-scaffold.yml"
LEAN_TOOLCHAIN = ROOT / "lean-toolchain"
LAKEFILE = ROOT / "lakefile.lean"
PROJECT_MODULE = ROOT / "B9" / "ClusterStabilizer" / "WidthLocality.lean"

METHOD = "b9_toolchain_ci_contract_gate_v0"
STATUS = "toolchain_ci_contract_open_pending_remote_run"
MODEL_STATUS = "github_actions_lean_lake_handoff_without_checked_run_artifact"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def requirement(req_id: str, label: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {
        "id": req_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def has(pattern: str, source: str) -> bool:
    return re.search(pattern, source, re.MULTILINE) is not None


def build_payload() -> dict[str, Any]:
    workflow = read_text(WORKFLOW_TEMPLATE)
    toolchain = read_text(LEAN_TOOLCHAIN).strip()
    lakefile = read_text(LAKEFILE)
    module = read_text(PROJECT_MODULE)
    requirements = [
        requirement(
            "C1",
            "B9 Lean workflow template exists",
            WORKFLOW_TEMPLATE.exists(),
            rel(WORKFLOW_TEMPLATE),
        ),
        requirement(
            "C2",
            "workflow is scoped to B9 proof files",
            '"B9/**"' in workflow
            and '"research/proof_skeletons/B9_*.lean"' in workflow
            and '"benchmarks/B9_quantum_pcp_local_hamiltonian.yaml"' in workflow,
            "paths include B9, proof_skeletons, tools, results, and benchmark",
        ),
        requirement(
            "C3",
            "workflow installs pinned toolchain from lean-toolchain",
            "cat lean-toolchain" in workflow
            and "elan-init.sh" in workflow
            and toolchain == "leanprover/lean4:v4.12.0",
            f"toolchain={toolchain}",
        ),
        requirement(
            "C4",
            "workflow exposes both Lean and Lake version probes",
            "lean --version" in workflow and "lake --version" in workflow,
            "lean --version / lake --version",
        ),
        requirement(
            "C5",
            "workflow runs Lake dependency resolution",
            "lake update" in workflow and "mathlib4" in lakefile,
            "lake update with mathlib4 dependency",
        ),
        requirement(
            "C6",
            "workflow checks the B9 Lean module",
            "lake env lean B9/ClusterStabilizer/WidthLocality.lean" in workflow
            and "cluster_stabilizer_open_uniform_reweight_obligation" in module,
            rel(PROJECT_MODULE),
        ),
        requirement(
            "C7",
            "workflow refreshes B9 proof-environment gates",
            "tools/b9_proof_environment_readiness_gate.py" in workflow
            and "tools/b9_proof_environment_contract_gate.py" in workflow
            and "tools/b9_proof_project_scaffold_gate.py" in workflow,
            "readiness, contract, and scaffold refresh commands",
        ),
        requirement(
            "C8",
            "active remote CI run artifact is present",
            False,
            "the OAuth token cannot activate .github/workflows here; no remote CI run artifact or checked theorem output is recorded in this repository",
        ),
    ]
    failed = [row for row in requirements if not row["passed"]]
    return {
        "benchmark_id": "B9",
        "title": "B9 Lean/Lake CI contract gate",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "workflow_template": rel(WORKFLOW_TEMPLATE),
        "active_workflow": rel(ACTIVE_WORKFLOW),
        "active_workflow_present": ACTIVE_WORKFLOW.exists(),
        "lean_toolchain": rel(LEAN_TOOLCHAIN),
        "lakefile": rel(LAKEFILE),
        "lean_project_module": rel(PROJECT_MODULE),
        "ci_contract_requirement_count": len(requirements),
        "passed_ci_contract_requirement_count": len(requirements) - len(failed),
        "failed_ci_contract_requirement_count": len(failed),
        "failed_ci_contract_requirement_ids": [row["id"] for row in failed],
        "requirements": requirements,
        "claim_boundary": {
            "ci_template_created": True,
            "active_workflow_present": ACTIVE_WORKFLOW.exists(),
            "remote_ci_run_artifact_present": False,
            "actual_lean4_available_locally": False,
            "lake_available_locally": False,
            "proof_environment_ready": False,
            "proof_assistant_checked": False,
            "formal_theorem_proved": False,
            "explicit_not_quantum_pcp_proof": True,
            "global_gap_amplification_impossibility_claimed": False,
            "nlts_theorem_claimed": False,
        },
        "validation_errors": [],
        "validation_error_count": 0,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# B9 Lean/Lake CI Contract Gate",
        "",
        f"Status: **{payload['status']}**",
        "",
        "T-B9-004e adds a GitHub Actions handoff for the B9 Lean/Lake scaffold. "
        "It defines how an external runner should install the pinned Lean "
        "toolchain, expose Lake, run `lake update`, check the B9 Lean module, "
        "and refresh the B9 proof-environment gates. This is a CI contract, not "
        "a recorded proof-assistant success.",
        "",
        "## Metrics",
        "",
        f"- Workflow template: `{payload['workflow_template']}`",
        f"- Active workflow present locally: `{payload['active_workflow_present']}`",
        (
            f"- CI contract requirements passed / failed: "
            f"{payload['passed_ci_contract_requirement_count']} / "
            f"{payload['failed_ci_contract_requirement_count']}"
        ),
        f"- Failed CI contract requirement IDs: `{payload['failed_ci_contract_requirement_ids']}`",
        "",
        "## Requirements",
        "",
        "| ID | Pass | Requirement | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["requirements"]:
        passed = "yes" if row["passed"] else "no"
        lines.append(f"| {row['id']} | {passed} | {row['label']} | {row['evidence']} |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- The CI handoff template exists and is scoped to B9 proof files.",
            "- The template must be copied into `.github/workflows/` by a token with workflow scope before it can run on GitHub.",
            "- No remote CI run artifact is recorded yet.",
            "- No proof-assistant checked theorem is claimed.",
            "- No Quantum PCP, NLTS, or global gap-amplification theorem is claimed.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "results" / "B9_toolchain_ci_contract_gate_v0.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=ROOT / "research" / "B9_toolchain_ci_contract_gate.md",
    )
    args = parser.parse_args()
    payload = build_payload()
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload, args.markdown_output)


if __name__ == "__main__":
    main()
