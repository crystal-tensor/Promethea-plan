#!/usr/bin/env python3
"""Build the preregistered R181 Qiskit accelerator on Linux x86-64."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import sysconfig
import time
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r181_active_limb_linux_x86_64_build_v0"
SOURCE_COMMIT = "0fd015a22b84c9082173597a5d2304dc0aaec08c"
SOURCE_URL = "https://github.com/Qiskit/qiskit.git"
PROTOCOL_PATH = "results/B4_B8_R181_active_limb_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R181_active_limb_contract_v0.json"
PATCH_PATH = (
    "research/source_lineage/Qiskit_2_4_1_R180_active_limb_superaccumulator.patch"
)
BINARY_PATH = (
    "research/source_lineage/Qiskit_2_4_1_R181_active_limb_pyext.x86_64-linux-gnu.so"
)
MANIFEST_PATH = "research/source_lineage/Qiskit_2_4_1_R181_active_limb_linux_x86_64_build_manifest.json"
LOG_DIR = "research/source_lineage/R181_active_limb_linux_x86_64_build_logs"
EXPECTED_SOURCE_HASHES = {
    "crates/pyext/Cargo.toml": (
        "996c72ed40ce2a1cd379df98b3e7f99c4eb5c937bb743a29383141bc0c8a5db5"
    ),
    "crates/transpiler/Cargo.toml": (
        "0e04369fa263fc8f12495bb091c16858c077b216bf3dad7324a59a95b7a7fa26"
    ),
    "crates/transpiler/src/passes/vf2/vf2_layout.rs": (
        "d883ed30f5693a080272146245004981508004f2f9e86dba1b433c00a3eb8725"
    ),
}


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def validate_payload(payload: dict[str, Any], label: str) -> str:
    body = dict(payload)
    observed = body.pop("payload_hash", None)
    if not observed or observed != canonical_hash(body):
        raise ValueError(f"R181 {label} payload hash mismatch")
    return str(observed)


def validate_preregistration(
    args: argparse.Namespace, contract: dict[str, Any]
) -> None:
    created = int(
        datetime.fromisoformat(
            args.preregistration_created_at.replace("Z", "+00:00")
        ).timestamp()
    )
    if int(time.time()) <= created:
        raise ValueError("R181 build must start after public preregistration")
    if not args.preregistration_discussion.startswith(
        "https://github.com/crystal-tensor/Prometheus-plan/discussions/"
    ):
        raise ValueError("R181 preregistration discussion boundary mismatch")
    if contract.get("execution_started") is not False:
        raise ValueError("R181 contract must remain an unopened record")
    current_commit = command_output(["git", "rev-parse", "HEAD"])
    if args.preregistration_commit != current_commit:
        raise ValueError("R181 runner commit does not match the preregistration commit")
    if (
        os.environ.get("GITHUB_ACTIONS") == "true"
        and os.environ.get("GITHUB_SHA") != current_commit
    ):
        raise ValueError("R181 GitHub Actions checkout does not match HEAD")


def run_step(
    source: Path,
    log_dir: Path,
    step_id: str,
    command: list[str],
    *,
    environment: dict[str, str] | None = None,
) -> dict[str, Any]:
    started = time.time()
    completed = subprocess.run(
        command,
        cwd=source,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    stdout_path = log_dir / f"{step_id}.stdout.txt"
    stderr_path = log_dir / f"{step_id}.stderr.txt"
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    record = {
        "step_id": step_id,
        "command": command,
        "returncode": completed.returncode,
        "elapsed_seconds": time.time() - started,
        "stdout_path": f"{LOG_DIR}/{stdout_path.name}",
        "stdout_sha256": file_sha256(stdout_path),
        "stderr_path": f"{LOG_DIR}/{stderr_path.name}",
        "stderr_sha256": file_sha256(stderr_path),
    }
    if completed.returncode != 0:
        raise RuntimeError(
            f"R181 build step failed: {step_id}\n{completed.stdout}\n{completed.stderr}"
        )
    return record


def command_output(command: list[str]) -> str:
    return subprocess.check_output(command, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    parser.add_argument("--preregistration-created-at", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    validate_payload(protocol, "protocol")
    validate_payload(contract, "contract")
    validate_preregistration(args, contract)
    if protocol.get("method") != "b4_b8_r181_active_limb_protocol_v0":
        raise ValueError("R181 protocol identity mismatch")
    if contract.get("contract_id") != "B4-B8-R181-active-limb-contract-v0":
        raise ValueError("R181 contract identity mismatch")
    if contract.get("protocol_payload_hash") != protocol.get("payload_hash"):
        raise ValueError("R181 protocol binding mismatch")
    for section in ("source_bindings", "tool_bindings"):
        for binding in contract.get(section, {}).values():
            path = root / binding["path"]
            if not path.exists() or file_sha256(path) != binding["sha256"]:
                raise ValueError(f"R181 binding mismatch: {binding['path']}")
    for relative in contract.get("result_paths_must_be_absent", []):
        if (root / relative).exists():
            raise ValueError(
                f"R181 evidence existed before Linux execution: {relative}"
            )
    for relative in contract.get("build_output_paths_created_before_replay", []):
        if (root / relative).exists():
            raise ValueError(f"R181 build output existed before build: {relative}")
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "amd64"}:
        raise ValueError(
            f"R181 requires Linux x86-64, observed {platform.system()} {platform.machine()}"
        )

    source = Path("/tmp/prometheus-r181-qiskit-source")
    if source.exists():
        shutil.rmtree(source)
    source.mkdir(parents=True)
    log_dir = root / LOG_DIR
    log_dir.mkdir(parents=True)
    environment = dict(os.environ)
    environment.update(
        {
            "CARGO_TERM_COLOR": "never",
            "PYO3_PYTHON": sys.executable,
            "RUST_BACKTRACE": "1",
        }
    )
    steps = []
    steps.append(
        run_step(
            source,
            log_dir,
            "01_git_init",
            ["git", "init", "--quiet"],
            environment=environment,
        )
    )
    steps.append(
        run_step(
            source,
            log_dir,
            "02_git_remote",
            ["git", "remote", "add", "origin", SOURCE_URL],
            environment=environment,
        )
    )
    steps.append(
        run_step(
            source,
            log_dir,
            "03_git_fetch",
            ["git", "fetch", "--depth", "1", "origin", SOURCE_COMMIT],
            environment=environment,
        )
    )
    steps.append(
        run_step(
            source,
            log_dir,
            "04_git_checkout",
            ["git", "checkout", "--detach", "FETCH_HEAD"],
            environment=environment,
        )
    )
    steps.append(
        run_step(
            source,
            log_dir,
            "05_patch_check",
            ["git", "apply", "--check", str(root / PATCH_PATH)],
            environment=environment,
        )
    )
    steps.append(
        run_step(
            source,
            log_dir,
            "06_patch_apply",
            ["git", "apply", str(root / PATCH_PATH)],
            environment=environment,
        )
    )
    observed_source_hashes = {
        path: file_sha256(source / path) for path in EXPECTED_SOURCE_HASHES
    }
    if observed_source_hashes != EXPECTED_SOURCE_HASHES:
        raise ValueError("R181 patched source hashes do not match the frozen patch")
    pyext_metadata = tomllib.loads(
        (source / "crates/pyext/Cargo.toml").read_text(encoding="utf-8")
    )
    library_metadata = pyext_metadata.get("lib", {})
    library_name = library_metadata.get("name")
    crate_types = library_metadata.get("crate-type", [])
    if library_name != "qiskit_pyext" or "cdylib" not in crate_types:
        raise ValueError(
            "R181 Qiskit pyext metadata does not declare qiskit_pyext cdylib"
        )
    for step_id, command in [
        ("07_cargo_fmt", ["cargo", "fmt", "--all", "--", "--check"]),
        ("08_cargo_check", ["cargo", "check", "-p", "qiskit-transpiler", "--lib"]),
        (
            "09_cargo_test",
            [
                "cargo",
                "test",
                "-p",
                "qiskit-transpiler",
                "--lib",
                "r180_active_fixed_exact_score_tests",
            ],
        ),
        ("10_git_diff_check", ["git", "diff", "--check"]),
        (
            "11_cargo_release",
            [
                "cargo",
                "rustc",
                "--lib",
                "--manifest-path",
                "crates/pyext/Cargo.toml",
                "--release",
                "--features",
                "cache_pygates,pyo3/extension-module",
                "--crate-type",
                "cdylib",
            ],
        ),
    ]:
        steps.append(
            run_step(
                source,
                log_dir,
                step_id,
                command,
                environment=environment,
            )
        )

    candidate = source / "target/release" / f"lib{library_name}.so"
    if not candidate.is_file():
        raise ValueError(
            f"R181 source-declared release artifact is missing: {candidate}"
        )
    binary = root / BINARY_PATH
    binary.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate, binary)
    file_description = command_output(["file", str(binary)])
    if "x86-64" not in file_description or "shared object" not in file_description:
        raise ValueError(f"R181 built unexpected binary: {file_description}")

    qiskit_spec = importlib.util.find_spec("qiskit")
    if qiskit_spec is None or not qiskit_spec.submodule_search_locations:
        raise ValueError("R181 cannot locate the pinned installed Qiskit package")
    installed_qiskit = Path(
        next(iter(qiskit_spec.submodule_search_locations))
    ).resolve()
    smoke_overlay = Path("/tmp/prometheus-r181-import-smoke")
    if smoke_overlay.exists():
        shutil.rmtree(smoke_overlay)
    smoke_package = smoke_overlay / "qiskit"
    shutil.copytree(installed_qiskit, smoke_package)
    for installed_accelerator in smoke_package.glob("_accelerate*.so"):
        installed_accelerator.unlink()
    smoke_binary = smoke_package / "_accelerate.abi3.so"
    shutil.copy2(binary, smoke_binary)
    smoke_environment = dict(environment)
    smoke_environment["PYTHONPATH"] = os.pathsep.join(
        [str(smoke_overlay), environment.get("PYTHONPATH", "")]
    )
    smoke_code = "\n".join(
        [
            "import hashlib, json",
            "from pathlib import Path",
            "import qiskit._accelerate as accelerator",
            "from qiskit._accelerate.vf2_layout import VF2PassConfiguration",
            "path = Path(accelerator.__file__).resolve()",
            "entry = getattr(accelerator.vf2_layout, 'vf2_layout_pass_average_active_fixed_exact_score', None)",
            "print(json.dumps({'accelerator_path': str(path), 'accelerator_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'configuration_type': VF2PassConfiguration.__name__, 'active_limb_entry_point': callable(entry)}, sort_keys=True))",
        ]
    )
    steps.append(
        run_step(
            smoke_overlay,
            log_dir,
            "12_python_import_smoke",
            [sys.executable, "-c", smoke_code],
            environment=smoke_environment,
        )
    )
    import_smoke = json.loads(
        (log_dir / "12_python_import_smoke.stdout.txt").read_text(encoding="utf-8")
    )
    if (
        import_smoke.get("accelerator_sha256") != file_sha256(binary)
        or import_smoke.get("configuration_type") != "VF2PassConfiguration"
        or import_smoke.get("active_limb_entry_point") is not True
    ):
        raise ValueError("R181 Python import smoke did not bind the built accelerator")

    run_url = ""
    if os.environ.get("GITHUB_RUN_ID"):
        run_url = (
            f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
            f"{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/"
            f"{os.environ['GITHUB_RUN_ID']}"
        )
    manifest = {
        "title": "Qiskit 2.4.1 R181 active-limb Linux x86-64 build manifest",
        "version": 0,
        "method": METHOD,
        "status": "linux_x86_64_pyext_built_and_imported_after_preregistration",
        "preregistration": {
            "commit": args.preregistration_commit,
            "discussion": args.preregistration_discussion,
            "created_at": args.preregistration_created_at,
        },
        "official_source": {
            "repository": SOURCE_URL,
            "release": "2.4.1",
            "commit": SOURCE_COMMIT,
        },
        "patch": {"path": PATCH_PATH, "sha256": file_sha256(root / PATCH_PATH)},
        "patched_source_hashes": observed_source_hashes,
        "source_declared_library": {
            "metadata_path": "crates/pyext/Cargo.toml",
            "name": library_name,
            "crate_types": crate_types,
            "release_artifact": str(candidate.relative_to(source)),
        },
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "python_extension_suffix": sysconfig.get_config_var("EXT_SUFFIX"),
            "rustc": command_output(["rustc", "--version"]),
            "cargo": command_output(["cargo", "--version"]),
            "uname": command_output(["uname", "-a"]),
        },
        "github_actions": {
            "run_url": run_url,
            "run_id": os.environ.get("GITHUB_RUN_ID", ""),
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
            "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
            "job": os.environ.get("GITHUB_JOB", ""),
            "sha": os.environ.get("GITHUB_SHA", ""),
            "ref": os.environ.get("GITHUB_REF", ""),
        },
        "build_steps": steps,
        "python_import_smoke": import_smoke,
        "accelerator": {
            "path": BINARY_PATH,
            "sha256": file_sha256(binary),
            "size_bytes": binary.stat().st_size,
            "file_description": file_description,
        },
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
        "hardware_result_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "new_credit_delta": 0,
    }
    manifest["payload_hash"] = canonical_hash(manifest)
    write_json(root / MANIFEST_PATH, manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "accelerator_sha256": manifest["accelerator"]["sha256"],
                "payload_hash": manifest["payload_hash"],
                "run_url": run_url,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
