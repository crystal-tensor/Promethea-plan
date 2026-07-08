#!/usr/bin/env python3
"""Same-access RZ denominator verifier for B1/B7 O3-F4 C4/C5 rows."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_o3_f4_same_access_rz_denominator_verifier_v0"
RZ_PATTERN = re.compile(r"rz\(([^)]+)\)")


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_single_rz_theta(path: Path) -> float:
    matches = RZ_PATTERN.findall(path.read_text(encoding="utf-8"))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one rz(theta) in {path}, found {len(matches)}")
    return float(matches[0])


def rz_operator_norm_distance(theta_a: float, theta_b: float) -> float:
    return float(2.0 * abs(math.sin((theta_a - theta_b) / 2.0)))


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    source = args.root / args.source
    candidate = args.root / args.candidate
    certificate = args.root / args.r59_certificate
    negative_control = args.root / args.negative_control
    cert = load_json(certificate)
    neg = load_json(negative_control)
    source_theta = parse_single_rz_theta(source)
    candidate_theta = parse_single_rz_theta(candidate)
    denominator_distance = rz_operator_norm_distance(source_theta, candidate_theta)
    strict_tolerance = float(cert["strict_tolerance"])
    negative_control_distance = float(neg["negative_control_distance"])
    payload = {
        "artifact": "R63 same-access RZ denominator verifier transcript",
        "method": METHOD,
        "challenge_id": args.challenge_id,
        "source_circuit_file": args.source,
        "source_circuit_sha256": file_hash(source),
        "candidate_circuit_file": args.candidate,
        "candidate_circuit_sha256": file_hash(candidate),
        "r59_certificate_file": args.r59_certificate,
        "r59_certificate_sha256": file_hash(certificate),
        "r59_certificate_hash": cert["certificate_hash"],
        "negative_control_file": args.negative_control,
        "negative_control_sha256": file_hash(negative_control),
        "access_model_hash": args.access_model_hash,
        "unitary_distance_metric": "single_qubit_rz_operator_norm",
        "source_theta": source_theta,
        "candidate_theta": candidate_theta,
        "denominator_distance": denominator_distance,
        "r59_positive_replay_distance": float(cert["positive_replay_distance"]),
        "strict_tolerance": strict_tolerance,
        "positive_distance_met_or_equal": denominator_distance
        <= float(cert["positive_replay_distance"]) + strict_tolerance,
        "negative_control_distance": negative_control_distance,
        "negative_control_rejected": negative_control_distance > strict_tolerance,
        "pressure_flags_transcript_bound": True,
        "same_access_inputs_used": [
            args.source,
            args.candidate,
            args.r59_certificate,
            args.negative_control,
        ],
        "forbidden_inputs_used": [],
        "claim_boundary": (
            "Transcript-bound row evidence only. This verifier checks the RZ distance "
            "for one C4/C5 row and grants no architecture or resource promotion."
        ),
        "runtime_seconds": None,
    }
    payload["runtime_seconds"] = round(time.time() - started, 6)
    payload["transcript_hash"] = stable_hash(payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--challenge-id", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--r59-certificate", required=True)
    parser.add_argument("--negative-control", required=True)
    parser.add_argument("--access-model-hash", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    output = args.root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps({"challenge_id": payload["challenge_id"], "denominator_distance": payload["denominator_distance"], "transcript_hash": payload["transcript_hash"]}, sort_keys=True))


if __name__ == "__main__":
    main()
