#!/usr/bin/env python3
"""Create a hash manifest for the downloadable R179 evidence bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RESULT_PATH = "results/B4_B8_R179_linux_x86_64_replay_v0.json"
ORACLE_PATH = "results/B4_B8_R179_independent_linux_x86_64_oracle_v0.json"
WORKER_DIR = "results/B4_B8_R179_linux_x86_64_replay"
BUILD_MANIFEST_PATH = (
    "research/source_lineage/Qiskit_2_4_1_R179_linux_x86_64_build_manifest.json"
)
BINARY_PATH = (
    "research/source_lineage/"
    "Qiskit_2_4_1_R179_fixed_superaccumulator_pyext.x86_64-linux-gnu.so"
)
LOG_DIR = "research/source_lineage/R179_linux_x86_64_build_logs"
BUNDLE_PATH = "results/B4_B8_R179_linux_x86_64_bundle_manifest_v0.json"


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_hash(payload: dict[str, Any]) -> str:
    body = dict(payload)
    observed = body.pop("payload_hash", None)
    if not observed or observed != canonical_hash(body):
        raise ValueError("R179 bundle source payload mismatch")
    return str(observed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    root = args.root.resolve()
    if (root / BUNDLE_PATH).exists():
        raise ValueError("R179 bundle manifest already exists")
    result = json.loads((root / RESULT_PATH).read_text(encoding="utf-8"))
    oracle = json.loads((root / ORACLE_PATH).read_text(encoding="utf-8"))
    build = json.loads((root / BUILD_MANIFEST_PATH).read_text(encoding="utf-8"))
    for payload in (result, oracle, build):
        payload_hash(payload)
    required = [
        Path(BINARY_PATH),
        Path(BUILD_MANIFEST_PATH),
        Path(RESULT_PATH),
        Path(ORACLE_PATH),
        Path("research/B4_B8_R179_linux_x86_64_replay.md"),
        Path("research/B4_B8_R179_independent_linux_x86_64_oracle.md"),
    ]
    required.extend(
        path.relative_to(root) for path in sorted((root / WORKER_DIR).glob("*.json"))
    )
    required.extend(
        path.relative_to(root) for path in sorted((root / LOG_DIR).glob("*.txt"))
    )
    artifacts = []
    for relative in required:
        path = root / relative
        if not path.is_file():
            raise ValueError(f"R179 bundle artifact missing: {relative}")
        artifacts.append(
            {
                "path": str(relative),
                "sha256": file_sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    manifest = {
        "title": "B4/B8/B10 R179 Linux x86-64 downloadable evidence bundle",
        "version": 0,
        "method": "b4_b8_r179_linux_x86_64_bundle_v0",
        "status": "linux_x86_64_bundle_complete",
        "github_actions_run_url": build.get("github_actions", {}).get("run_url", ""),
        "source_result_payload_hash": result["payload_hash"],
        "source_oracle_payload_hash": oracle["payload_hash"],
        "source_build_payload_hash": build["payload_hash"],
        "artifact_count": len(artifacts),
        "worker_artifact_count": len(list((root / WORKER_DIR).glob("*.json"))),
        "artifacts": artifacts,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
        "hardware_result_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "new_credit_delta": 0,
    }
    if (
        manifest["worker_artifact_count"] != 39
        or not manifest["github_actions_run_url"]
    ):
        raise ValueError("R179 bundle worker or GitHub-run boundary mismatch")
    manifest["payload_hash"] = canonical_hash(manifest)
    path = root / BUNDLE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "artifact_count": manifest["artifact_count"],
                "payload_hash": manifest["payload_hash"],
                "run_url": manifest["github_actions_run_url"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
