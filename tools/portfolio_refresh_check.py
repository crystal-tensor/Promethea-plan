#!/usr/bin/env python3
"""Refresh and validate the Axiom Horizon portfolio status artifacts."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import py_compile
import re
import subprocess
import sys
from typing import Any

import yaml


DEFAULT_JSON_REPORT = Path("research/portfolio_status_report.json")
DEFAULT_MARKDOWN_REPORT = Path("research/portfolio_status_report.md")
README_PATH = Path("README.md")
STATUS_HTML_PATH = Path("research/current_stage_brief.html")

HAN_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, check=True)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compile_tools() -> None:
    for path in sorted(Path("tools").glob("*.py")):
        py_compile.compile(str(path), doraise=True)
    print("compiled tools/*.py")


def parse_structured_files(json_report: Path) -> None:
    for path in sorted(Path("benchmarks").glob("*.yaml")):
        yaml.safe_load(path.read_text(encoding="utf-8"))
    print("parsed benchmarks/*.yaml")

    json_paths = [
        json_report,
        Path("research/technical_resolution_program.json"),
        Path("research/top10_execution_board.json"),
        Path("research/top10_problem_dossiers.json"),
        Path("research/problem_catalog_100.json"),
    ]
    for path in json_paths:
        load_json(path)
    print("parsed portfolio JSON files")

    HTMLParser().feed(STATUS_HTML_PATH.read_text(encoding="utf-8"))
    print(f"parsed {STATUS_HTML_PATH}")


def assert_readme_ascii_policy() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    match = HAN_RE.search(readme)
    if match:
        line_no = readme.count("\n", 0, match.start()) + 1
        raise SystemExit(f"README.md contains Han character at line {line_no}")
    print("README.md Han-character check passed")


def assert_portfolio_passed(json_report: Path, allow_warnings: bool) -> None:
    report = load_json(json_report)
    errors = report.get("errors", [])
    warnings = report.get("warnings", [])
    if report.get("passed") is not True:
        raise SystemExit(f"portfolio audit did not pass; errors={errors!r}")
    if errors:
        raise SystemExit(f"portfolio audit errors present: {errors!r}")
    if warnings and not allow_warnings:
        raise SystemExit(f"portfolio audit warnings present: {warnings!r}")
    print(f"portfolio audit passed with {len(errors)} errors and {len(warnings)} warnings")


def assert_clean_worktree() -> None:
    status = subprocess.check_output(["git", "status", "--porcelain"], text=True)
    if status.strip():
        raise SystemExit(
            "worktree is not clean after refresh; commit generated artifacts:\n" + status
        )
    print("worktree clean after refresh")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh portfolio audit outputs and run local/CI quality checks."
    )
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_REPORT)
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Fail if git status is dirty after generated outputs are refreshed.",
    )
    parser.add_argument(
        "--allow-warnings",
        action="store_true",
        help="Allow portfolio audit warnings. Errors still fail.",
    )
    args = parser.parse_args()

    compile_tools()
    run(
        [
            sys.executable,
            "tools/research_portfolio_audit.py",
            "--json-output",
            str(args.json_output),
            "--markdown-output",
            str(args.markdown_output),
            "--pretty",
        ]
    )
    parse_structured_files(args.json_output)
    assert_readme_ascii_policy()
    assert_portfolio_passed(args.json_output, allow_warnings=args.allow_warnings)
    if args.require_clean:
        assert_clean_worktree()
    print("portfolio refresh/check complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
