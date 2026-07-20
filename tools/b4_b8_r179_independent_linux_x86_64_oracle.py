#!/usr/bin/env python3
"""Independently audit R179 Linux evidence without importing Qiskit."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import platform
import sys
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r179_independent_linux_x86_64_oracle_v0"
PROTOCOL_PATH = "results/B4_B8_R179_linux_x86_64_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R179_linux_x86_64_contract_v0.json"
SOURCE_PATH = "results/B4_B8_R179_linux_x86_64_replay_v0.json"
WORKER_DIR = "results/B4_B8_R179_linux_x86_64_replay"
RESULT_PATH = "results/B4_B8_R179_independent_linux_x86_64_oracle_v0.json"
REPORT_PATH = "research/B4_B8_R179_independent_linux_x86_64_oracle.md"
BUILD_MANIFEST_PATH = (
    "research/source_lineage/Qiskit_2_4_1_R179_linux_x86_64_build_manifest.json"
)


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_reference(root: Path) -> Any:
    path = root / "tools/b4_b8_r176_independent_fixed_accumulator_oracle.py"
    spec = importlib.util.spec_from_file_location("r179_stdlib_reference_oracle", path)
    if spec is None or spec.loader is None:
        raise ValueError("R179 could not load the standard-library reference oracle")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.METHOD = METHOD
    module.PROTOCOL_PATH = PROTOCOL_PATH
    module.CONTRACT_PATH = CONTRACT_PATH
    module.SOURCE_PATH = SOURCE_PATH
    module.WORKER_DIR = WORKER_DIR
    module.RESULT_PATH = RESULT_PATH
    module.REPORT_PATH = REPORT_PATH
    return module


def build_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    platform = result["platform_audit"]
    return "\n".join(
        [
            "# B4/B8/B10 R179 Independent Linux x86-64 Oracle",
            "",
            f"- Status: `{result['status']}`",
            f"- Matrix requirements: `{result['requirements_passed']}/12`",
            f"- Platform requirements: `{platform['requirements_passed']}/3`",
            f"- Payload hash: `{result['payload_hash']}`",
            "",
            "## Independent Check",
            "",
            f"The standard-library audit validates `{summary['worker_hashes_valid']}/39` worker hashes, `{summary['row_hashes_valid']}/2400` row hashes, and `{summary['case_hashes_valid']}/84` case hashes. It reproduces `{summary['standard_outcomes_reproduced']}/1728` standard outcomes and `{summary['small_gap_outcomes_reproduced']}/672` small-gap outcomes.",
            "",
            f"It imports neither Qiskit nor the R179 executor. All `{platform['linux_x86_64_worker_count']}/39` workers identify Linux x86-64, and the source result is bound to build manifest `{result['build_manifest_payload_hash']}`.",
            "",
            "## Claim Boundary",
            "",
            "This strengthens evidence integrity for one GitHub-hosted Ubuntu x86-64 replay. It does not make the patch upstream accepted or production ready, establish broad graph-scale behavior, provide hardware evidence, quantum advantage, BQP separation, solve B4/B8/B10, or add credit.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    args, remaining = parser.parse_known_args()
    if remaining:
        raise ValueError(f"R179 unexpected oracle arguments: {remaining}")
    root = args.root.resolve()
    if (root / RESULT_PATH).exists() or (root / REPORT_PATH).exists():
        raise ValueError("R179 independent oracle evidence already exists")
    module = load_reference(root)
    original_argv = sys.argv
    sys.argv = [
        str(Path(__file__).resolve()),
        "--root",
        str(root),
        "--preregistration-commit",
        args.preregistration_commit,
        "--preregistration-discussion",
        args.preregistration_discussion,
    ]
    try:
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            returncode = module.main()
    finally:
        sys.argv = original_argv
    result = json.loads((root / RESULT_PATH).read_text(encoding="utf-8"))
    build = json.loads((root / BUILD_MANIFEST_PATH).read_text(encoding="utf-8"))
    source = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    manifests = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((root / WORKER_DIR).glob("*.json"))
    ]
    linux_workers = sum(
        row.get("environment", {}).get("system") == "Linux"
        and row.get("environment", {}).get("machine") in {"x86_64", "amd64"}
        for row in manifests
    )
    platform_requirements = [
        {
            "requirement_id": "L1",
            "passed": platform.system() == "Linux"
            and platform.machine() in {"x86_64", "amd64"},
        },
        {"requirement_id": "L2", "passed": linux_workers == 39},
        {
            "requirement_id": "L3",
            "passed": source.get("build_manifest_payload_hash")
            == build.get("payload_hash")
            and source.get("platform_gate", {}).get("requirements_failed") == 0,
        },
    ]
    platform_passed = all(row["passed"] for row in platform_requirements)
    passed = returncode == 0 and platform_passed
    result.update(
        {
            "title": "B4/B8/B10 R179 independent Linux x86-64 oracle",
            "method": METHOD,
            "status": "independent_linux_x86_64_oracle_complete"
            if passed
            else "independent_linux_x86_64_oracle_failed",
            "classification": "standard_library_reproduction_of_linux_x86_64_matrix"
            if passed
            else "incomplete",
            "source_target_id": "T-B4-002dk/T-B8-003do/T-B10-009da-r179-oracle",
            "upstream_target_id": source["source_target_id"],
            "build_manifest_payload_hash": build["payload_hash"],
            "platform_audit": {
                "linux_x86_64_worker_count": linux_workers,
                "requirements": platform_requirements,
                "requirements_passed": sum(
                    row["passed"] for row in platform_requirements
                ),
                "requirements_failed": sum(
                    not row["passed"] for row in platform_requirements
                ),
            },
            "claim_boundary": {
                "what_is_supported": "a Qiskit-free standard-library reproduction of every frozen R179 Linux mapping expectation, exact oracle, hash, timing ratio, memory ratio, and platform binding",
                "what_is_not_supported": "an upstream-accepted or production Qiskit remedy, confirmed Qiskit bug, broad graph-scale behavior, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
            },
        }
    )
    result["summary"].pop("r176_executor_imported", None)
    result["summary"].update(
        {
            "r179_executor_imported": False,
            "linux_x86_64_worker_count": linux_workers,
            "platform_audit_passed": platform_passed,
        }
    )
    result.pop("payload_hash", None)
    result["payload_hash"] = canonical_hash(result)
    write_json(root / RESULT_PATH, result)
    (root / REPORT_PATH).write_text(build_report(result), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "requirements_passed": result["requirements_passed"],
                "requirements_failed": result["requirements_failed"],
                "platform_audit": result["platform_audit"],
                "payload_hash": result["payload_hash"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
