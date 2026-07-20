#!/usr/bin/env python3
"""Replay the full R176 matrix on preregistered Linux x86-64 evidence."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import b4_b8_r176_fixed_superaccumulator_replay as base


METHOD = "b4_b8_r179_linux_x86_64_replay_v0"
PROTOCOL_PATH = "results/B4_B8_R179_linux_x86_64_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R179_linux_x86_64_contract_v0.json"
BINARY_PATH = (
    "research/source_lineage/"
    "Qiskit_2_4_1_R179_fixed_superaccumulator_pyext.x86_64-linux-gnu.so"
)
BUILD_MANIFEST_PATH = (
    "research/source_lineage/Qiskit_2_4_1_R179_linux_x86_64_build_manifest.json"
)
RESULT_PATH = "results/B4_B8_R179_linux_x86_64_replay_v0.json"
REPORT_PATH = "research/B4_B8_R179_linux_x86_64_replay.md"
OUT_DIR = "results/B4_B8_R179_linux_x86_64_replay"
ORACLE_PATH = "results/B4_B8_R179_independent_linux_x86_64_oracle_v0.json"


def configure_base() -> None:
    base.METHOD = METHOD
    base.PROTOCOL_PATH = PROTOCOL_PATH
    base.CONTRACT_PATH = CONTRACT_PATH
    base.BINARY_PATH = BINARY_PATH
    base.RESULT_PATH = RESULT_PATH
    base.REPORT_PATH = REPORT_PATH
    base.OUT_DIR = OUT_DIR
    original_environment = base.actual_environment

    def linux_environment() -> dict[str, Any]:
        value = original_environment()
        value.update(
            {
                "system": platform.system(),
                "machine": platform.machine(),
                "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
                "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
            }
        )
        return value

    base.actual_environment = linux_environment


def validate_contract(
    root: Path,
    protocol: dict[str, Any],
    contract: dict[str, Any],
    *,
    pre_replay: bool,
) -> None:
    protocol_hash = base.validate_hash_field(protocol, "payload_hash", "protocol")
    base.validate_hash_field(contract, "payload_hash", "contract")
    if protocol.get("method") != "b4_b8_r179_linux_x86_64_protocol_v0":
        raise ValueError("R179 protocol identity mismatch")
    if contract.get("contract_id") != "B4-B8-R179-linux-x86-64-contract-v0":
        raise ValueError("R179 contract identity mismatch")
    if contract.get("execution_started") is not False:
        raise ValueError("R179 contract is not an unopened record")
    if contract.get("protocol_payload_hash") != protocol_hash:
        raise ValueError("R179 protocol binding mismatch")
    for section in ("source_bindings", "tool_bindings"):
        for binding in contract.get(section, {}).values():
            path = root / binding["path"]
            if not path.exists() or base.file_sha256(path) != binding["sha256"]:
                raise ValueError(f"R179 binding mismatch: {binding['path']}")
    if pre_replay:
        for relative in (OUT_DIR, RESULT_PATH, REPORT_PATH, ORACLE_PATH):
            if (root / relative).exists():
                raise ValueError(f"R179 replay evidence already exists: {relative}")


def launch_worker(
    root: Path,
    overlay: Path,
    args: list[str],
    preregistration: dict[str, str],
) -> None:
    environment = dict(os.environ)
    environment.update(
        json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))[
            "process_environment"
        ]
    )
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(overlay), str(root / "tools"), environment.get("PYTHONPATH", "")]
    )
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--root",
        str(root),
        *args,
        "--preregistration-commit",
        preregistration["commit"],
        "--preregistration-discussion",
        preregistration["discussion"],
        "--preregistration-created-at",
        preregistration["created_at"],
    ]
    completed = subprocess.run(
        command,
        cwd=root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"R179 worker failed: {' '.join(args)}\n"
            f"{completed.stdout}\n{completed.stderr}"
        )


def build_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    platform_gate = result["platform_gate"]
    return "\n".join(
        [
            "# B4/B8/B10 R179 Linux x86-64 Replay",
            "",
            f"- Status: `{result['status']}`",
            f"- Frozen matrix requirements: `{result['requirements_passed']}/16`",
            f"- Platform requirements: `{platform_gate['requirements_passed']}/2`",
            f"- Payload hash: `{result['payload_hash']}`",
            "",
            "## Research Question",
            "",
            "Does the R176 exact-selection and performance result survive an independently built Ubuntu x86-64 accelerator?",
            "",
            "## Result",
            "",
            f"The Linux matrix executes `{summary['qiskit_calls_performed']}` direct Qiskit calls, including `{summary['recorded_call_count']}` recorded calls and `{summary['warmup_call_count']}` warmups across `{summary['worker_count']}` isolated processes. Source, BigUint, and fixed policies match `{summary['source_expected_match_count']}/800`, `{summary['biguint_expected_match_count']}/800`, and `{summary['fixed_expected_match_count']}/800`; BigUint and fixed agree on `{summary['biguint_fixed_mapping_agreement_count']}/800` mappings.",
            "",
            "## Performance",
            "",
            f"Aggregate BigUint/source is `{summary['aggregate_biguint_to_source_median_time_ratio']:.6f}`; fixed/source is `{summary['aggregate_fixed_to_source_median_time_ratio']:.6f}`; fixed/BigUint is `{summary['aggregate_fixed_to_biguint_median_time_ratio']:.6f}`. The worst fixed/source cell is `{summary['maximum_cell_fixed_to_source_median_time_ratio']:.6f}` and the worst fixed/source process-RSS ratio is `{summary['maximum_worker_fixed_to_source_peak_rss_ratio']:.6f}`.",
            "",
            "## Platform Evidence",
            "",
            f"All `{platform_gate['linux_x86_64_worker_count']}/39` worker manifests report Linux x86-64. The accelerator SHA-256 is `{result['accelerator_sha256']}` and the build-manifest payload hash is `{result['build_manifest_payload_hash']}`.",
            "",
            "## Claim Boundary",
            "",
            "This supports one independently built Ubuntu x86-64 replay of the frozen R176 matrix. It is not an upstream-accepted or production Qiskit patch, a confirmed Qiskit bug, broad graph-scale evidence, hardware evidence, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.",
            "",
        ]
    )


def aggregate(
    root: Path,
    protocol: dict[str, Any],
    contract: dict[str, Any],
    preregistration: dict[str, str],
) -> dict[str, Any]:
    result = base.aggregate(root, protocol, contract, preregistration)
    build = json.loads((root / BUILD_MANIFEST_PATH).read_text(encoding="utf-8"))
    base.validate_hash_field(build, "payload_hash", "build manifest")
    manifests = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((root / OUT_DIR).glob("*.json"))
    ]
    linux_workers = sum(
        row.get("environment", {}).get("system") == "Linux"
        and row.get("environment", {}).get("machine") in {"x86_64", "amd64"}
        for row in manifests
    )
    build_binding_passed = (
        build.get("status")
        == "linux_x86_64_pyext_built_and_imported_after_preregistration"
        and build.get("accelerator", {}).get("sha256")
        == base.file_sha256(root / BINARY_PATH)
        and build.get("preregistration") == preregistration
        and bool(build.get("github_actions", {}).get("run_url"))
    )
    platform_requirements = [
        {"requirement_id": "L1", "passed": linux_workers == 39},
        {"requirement_id": "L2", "passed": build_binding_passed},
    ]
    platform_passed = all(row["passed"] for row in platform_requirements)
    frozen_passed = result.get("requirements_failed") == 0
    passed = frozen_passed and platform_passed
    result.update(
        {
            "title": "B4/B8/B10 R179 Linux x86-64 replay",
            "method": METHOD,
            "status": "linux_x86_64_fixed_superaccumulator_supported_on_frozen_matrix"
            if passed
            else "linux_x86_64_fixed_superaccumulator_rejected_on_frozen_matrix",
            "classification": "independently_built_linux_x86_64_compiled_comparator_replay"
            if passed
            else "linux_x86_64_compiled_comparator_replay_failed",
            "source_target_id": "T-B4-002dj/T-B8-003dn/T-B10-009cz-r179-result",
            "upstream_target_id": protocol["source_target_id"],
            "build_manifest_path": BUILD_MANIFEST_PATH,
            "build_manifest_payload_hash": build["payload_hash"],
            "platform_gate": {
                "target": "ubuntu_x86_64",
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
                "what_is_supported": "one independently built Ubuntu x86-64 accelerator reproduces the frozen R176 exact-selection matrix and its declared local performance gates",
                "what_is_not_supported": "an upstream-accepted or production Qiskit remedy, confirmed Qiskit bug, broad graph-scale performance, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
            },
        }
    )
    result["summary"].update(
        {
            "cross_platform_replay_supported": passed,
            "linux_x86_64_worker_count": linux_workers,
            "github_actions_run_url": build.get("github_actions", {}).get(
                "run_url", ""
            ),
        }
    )
    result.pop("payload_hash", None)
    result["payload_hash"] = base.canonical_hash(result)
    base.write_json(root / RESULT_PATH, result)
    (root / REPORT_PATH).write_text(build_report(result), encoding="utf-8")
    return result


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "classification": result["classification"],
        "summary": result["summary"],
        "requirements_passed": result["requirements_passed"],
        "requirements_failed": result["requirements_failed"],
        "platform_gate": result["platform_gate"],
        "payload_hash": result["payload_hash"],
    }


def main() -> int:
    configure_base()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--worker-kind", choices=["standard", "small-gap"])
    parser.add_argument("--worker-dataset")
    parser.add_argument("--worker-profile")
    parser.add_argument("--worker-mode")
    parser.add_argument("--worker-policy", choices=sorted(base.POLICY_FUNCTIONS))
    parser.add_argument("--aggregate-existing", action="store_true")
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    parser.add_argument("--preregistration-created-at", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    preregistration = {
        "commit": args.preregistration_commit,
        "discussion": args.preregistration_discussion,
        "created_at": args.preregistration_created_at,
    }
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "amd64"}:
        raise ValueError("R179 replay requires Linux x86-64")
    if not (root / BUILD_MANIFEST_PATH).exists() or not (root / BINARY_PATH).exists():
        raise ValueError(
            "R179 replay requires the Linux build manifest and accelerator"
        )
    if args.worker_kind:
        validate_contract(root, protocol, contract, pre_replay=False)
        if args.worker_kind == "standard":
            base.execute_standard_worker(
                root,
                protocol,
                contract,
                str(args.worker_dataset),
                str(args.worker_profile),
                str(args.worker_policy),
                preregistration,
            )
        else:
            base.execute_small_gap_worker(
                root,
                protocol,
                contract,
                str(args.worker_mode),
                str(args.worker_policy),
                preregistration,
            )
        return 0
    if args.aggregate_existing:
        validate_contract(root, protocol, contract, pre_replay=False)
        result = aggregate(root, protocol, contract, preregistration)
        print(json.dumps(compact_result(result), indent=2, sort_keys=True))
        return 0 if result["status"].endswith("supported_on_frozen_matrix") else 1
    validate_contract(root, protocol, contract, pre_replay=True)
    overlay = base.prepare_overlay(root)
    (root / OUT_DIR).mkdir(parents=True)
    jobs = []
    for dataset in protocol["datasets"]:
        for profile in protocol["standard_profiles"]:
            for policy in protocol["policies"]:
                jobs.append(
                    [
                        "--worker-kind",
                        "standard",
                        "--worker-dataset",
                        dataset["dataset_id"],
                        "--worker-profile",
                        profile,
                        "--worker-policy",
                        policy,
                    ]
                )
    for mode in protocol["small_gap_modes"]:
        for policy in protocol["policies"]:
            jobs.append(
                [
                    "--worker-kind",
                    "small-gap",
                    "--worker-mode",
                    mode,
                    "--worker-policy",
                    policy,
                ]
            )
    for job in jobs:
        launch_worker(root, overlay, job, preregistration)
    result = aggregate(root, protocol, contract, preregistration)
    print(json.dumps(compact_result(result), indent=2, sort_keys=True))
    return 0 if result["status"].endswith("supported_on_frozen_matrix") else 1


if __name__ == "__main__":
    raise SystemExit(main())
