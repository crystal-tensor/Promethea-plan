#!/usr/bin/env python3
"""Rank toy superconductivity candidates with quantum-simulation descriptors."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np


FAMILIES = {
    "cuprate_like": {
        "known_high_tc_family": True,
        "u_over_w": (1.4, 0.22),
        "spin_fluctuation": (0.88, 0.08),
        "phonon_lambda": (0.25, 0.08),
        "dimensionality": (2.0, 0.15),
        "disorder": (0.18, 0.08),
        "pressure_gpa": (0.0, 2.0),
        "carrier_optimality": (0.82, 0.12),
        "competing_order": (0.42, 0.14),
    },
    "iron_pnictide_like": {
        "known_high_tc_family": True,
        "u_over_w": (1.05, 0.18),
        "spin_fluctuation": (0.76, 0.09),
        "phonon_lambda": (0.30, 0.08),
        "dimensionality": (2.2, 0.18),
        "disorder": (0.22, 0.09),
        "pressure_gpa": (3.0, 3.0),
        "carrier_optimality": (0.74, 0.13),
        "competing_order": (0.36, 0.12),
    },
    "hydride_like": {
        "known_high_tc_family": True,
        "u_over_w": (0.35, 0.11),
        "spin_fluctuation": (0.20, 0.07),
        "phonon_lambda": (0.92, 0.12),
        "dimensionality": (3.0, 0.08),
        "disorder": (0.12, 0.06),
        "pressure_gpa": (165.0, 40.0),
        "carrier_optimality": (0.70, 0.13),
        "competing_order": (0.12, 0.08),
    },
    "nickelate_like": {
        "known_high_tc_family": False,
        "u_over_w": (1.25, 0.25),
        "spin_fluctuation": (0.72, 0.11),
        "phonon_lambda": (0.22, 0.07),
        "dimensionality": (2.0, 0.12),
        "disorder": (0.30, 0.13),
        "pressure_gpa": (1.0, 2.0),
        "carrier_optimality": (0.62, 0.18),
        "competing_order": (0.50, 0.16),
    },
    "flat_band_oxide_like": {
        "known_high_tc_family": False,
        "u_over_w": (1.75, 0.35),
        "spin_fluctuation": (0.66, 0.12),
        "phonon_lambda": (0.28, 0.10),
        "dimensionality": (2.1, 0.25),
        "disorder": (0.38, 0.16),
        "pressure_gpa": (0.0, 1.0),
        "carrier_optimality": (0.55, 0.18),
        "competing_order": (0.62, 0.17),
    },
    "organic_salt_like": {
        "known_high_tc_family": False,
        "u_over_w": (1.55, 0.25),
        "spin_fluctuation": (0.62, 0.11),
        "phonon_lambda": (0.32, 0.09),
        "dimensionality": (1.6, 0.20),
        "disorder": (0.28, 0.12),
        "pressure_gpa": (0.8, 1.0),
        "carrier_optimality": (0.58, 0.16),
        "competing_order": (0.55, 0.15),
    },
}


def clipped_normal(rng: np.random.Generator, mean: float, scale: float, lo: float, hi: float) -> float:
    return float(np.clip(rng.normal(mean, scale), lo, hi))


def sample_candidates(per_family: int, seed: int) -> list[dict]:
    rng = np.random.default_rng(seed)
    candidates = []
    for family, spec in FAMILIES.items():
        for idx in range(per_family):
            pressure_lo, pressure_hi = (0.0, 260.0) if family == "hydride_like" else (0.0, 25.0)
            row = {
                "candidate_id": f"{family}_{idx + 1:02d}",
                "family": family,
                "known_high_tc_family": spec["known_high_tc_family"],
                "u_over_w": clipped_normal(rng, *spec["u_over_w"], 0.05, 3.0),
                "spin_fluctuation": clipped_normal(rng, *spec["spin_fluctuation"], 0.0, 1.0),
                "phonon_lambda": clipped_normal(rng, *spec["phonon_lambda"], 0.0, 1.4),
                "dimensionality": clipped_normal(rng, *spec["dimensionality"], 1.0, 3.0),
                "disorder": clipped_normal(rng, *spec["disorder"], 0.0, 1.0),
                "pressure_gpa": clipped_normal(rng, *spec["pressure_gpa"], pressure_lo, pressure_hi),
                "carrier_optimality": clipped_normal(rng, *spec["carrier_optimality"], 0.0, 1.0),
                "competing_order": clipped_normal(rng, *spec["competing_order"], 0.0, 1.0),
            }
            candidates.append(row)
    return candidates


def score_candidate(row: dict, weights: dict[str, float]) -> dict:
    dimensionality_bonus = math.exp(-((row["dimensionality"] - 2.0) ** 2) / 0.55)
    spin_channel = row["spin_fluctuation"] * dimensionality_bonus * math.exp(-abs(row["u_over_w"] - 1.35) / 0.75)
    phonon_channel = row["phonon_lambda"] * math.exp(-row["u_over_w"] / 2.7)
    carrier_channel = row["carrier_optimality"] * math.exp(-abs(row["u_over_w"] - 1.2) / 1.2)
    pressure_penalty = max(row["pressure_gpa"] - 80.0, 0.0) / 220.0
    disorder_penalty = row["disorder"] ** 1.4
    competition_penalty = 0.55 * row["competing_order"] if row["competing_order"] > 0.45 else 0.25 * row["competing_order"]
    score = (
        weights["spin"] * spin_channel
        + weights["phonon"] * phonon_channel
        + weights["carrier"] * carrier_channel
        - weights["disorder"] * disorder_penalty
        - weights["competition"] * competition_penalty
        - weights["pressure"] * pressure_penalty
    )
    return {
        "spin_pairing_descriptor": spin_channel,
        "phonon_pairing_descriptor": phonon_channel,
        "carrier_descriptor": carrier_channel,
        "disorder_penalty": disorder_penalty,
        "competition_penalty": competition_penalty,
        "pressure_penalty": pressure_penalty,
        "descriptor_score": score,
    }


def ensemble_uncertainty(row: dict, seed: int, samples: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    scores = []
    base = {
        "spin": 0.48,
        "phonon": 0.25,
        "carrier": 0.20,
        "disorder": 0.18,
        "competition": 0.16,
        "pressure": 0.08,
    }
    for _ in range(samples):
        weights = {key: float(max(0.01, rng.normal(value, 0.08 * value))) for key, value in base.items()}
        scores.append(score_candidate(row, weights)["descriptor_score"])
    return float(np.mean(scores)), float(np.std(scores))


def run(per_family: int, top_k: int, seed: int, ensemble_samples: int) -> dict:
    weights = {
        "spin": 0.48,
        "phonon": 0.25,
        "carrier": 0.20,
        "disorder": 0.18,
        "competition": 0.16,
        "pressure": 0.08,
    }
    candidates = []
    for row in sample_candidates(per_family=per_family, seed=seed):
        scored = {**row, **score_candidate(row, weights)}
        mean_score, score_std = ensemble_uncertainty(scored, seed + len(candidates) + 1, ensemble_samples)
        scored["ensemble_mean_score"] = mean_score
        scored["ensemble_score_std"] = score_std
        scored["active_learning_priority"] = mean_score + 0.5 * score_std
        candidates.append(scored)

    ranked = sorted(candidates, key=lambda item: item["active_learning_priority"], reverse=True)
    for rank, row in enumerate(ranked, start=1):
        row["rank"] = rank

    top_rows = ranked[:top_k]
    top_family_counts = dict(Counter(row["family"] for row in top_rows))
    known_high_tc_count = sum(1 for row in top_rows if row["known_high_tc_family"])
    known_high_tc_recall_at_k = known_high_tc_count / max(1, sum(1 for row in candidates if row["known_high_tc_family"]))
    precision_at_k = known_high_tc_count / top_k

    return {
        "benchmark_id": "B6",
        "method": "toy_superconductivity_descriptor_ranker_v0",
        "model_status": "toy_descriptor_ranking_not_material_discovery_claim",
        "seed": seed,
        "candidate_count": len(candidates),
        "families": sorted(FAMILIES),
        "candidates_per_family": per_family,
        "top_k": top_k,
        "top_family_counts": top_family_counts,
        "known_high_tc_precision_at_k": precision_at_k,
        "known_high_tc_recall_at_k": known_high_tc_recall_at_k,
        "top_candidate_ids": [row["candidate_id"] for row in top_rows],
        "top_candidates": top_rows,
        "results": ranked,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-family", type=int, default=12)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--seed", type=int, default=370626)
    parser.add_argument("--ensemble-samples", type=int, default=64)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = run(
        per_family=args.per_family,
        top_k=args.top_k,
        seed=args.seed,
        ensemble_samples=args.ensemble_samples,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
