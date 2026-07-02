#!/usr/bin/env python3
"""Build the B3/B10 F1 row acceptance packet submission from assembled row evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ACCEPTANCE_PACKET_ID = "B3-R1-full-covariance-row-acceptance-packet"
PROVENANCE_MANIFEST_ID = "B3-R1-full-covariance-provenance-manifest"
DENOMINATOR_REPLAY_MANIFEST_ID = "B3-R1-full-covariance-denominator-replay-manifest"
ROW_REPLAY_VALIDATION_MANIFEST_ID = "B3-R1-full-covariance-row-replay-validation-manifest"
DOWNSTREAM_PACKET_ID = "B3-R1-full-compiled-covariance"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def build_packet(args: argparse.Namespace) -> dict[str, Any]:
    row_replay = load_json(args.row_replay_validation_manifest_gate)
    priority = load_json(args.priority_packet_gate)
    assembled = load_json(args.assembled_rows_gate)
    row_summary = row_replay["summary"]
    priority_summary = priority["summary"]
    assembled_summary = assembled["summary"]
    row_bundle = assembled["row_bundle"]

    row_scope = {
        "h2_candidate_row_hash": assembled_summary["h2_candidate_row_hash"],
        "assembled_row_hashes": assembled_summary["assembled_row_hashes"],
        "candidate_row_count": assembled_summary["f1_candidate_row_count"],
        "required_f1_row_count": assembled_summary["required_f1_row_count"],
        "row_bundle_hash": assembled_summary["row_bundle_hash"],
    }
    row_table = {
        "candidate_row_ids": row_bundle["candidate_row_ids"],
        "candidate_row_hashes": row_bundle["candidate_row_hashes"],
        "assembled_row_ids": row_bundle["assembled_row_ids"],
        "assembled_row_hashes": row_bundle["assembled_row_hashes"],
        "source_shard_count": assembled_summary["source_shard_count"],
        "total_assembled_group_count": assembled_summary["total_assembled_group_count"],
        "total_nonzero_covariance_pair_count": assembled_summary["total_nonzero_covariance_pair_count"],
        "total_variance_sum": assembled_summary["total_variance_sum"],
    }
    compiled_state_replays = [
        row["compiled_state_replay_hashes"] for row in row_bundle["rows"]
    ]
    qwc_covariance_replays = [
        {
            "row_id": row["row_id"],
            "row_replay_hash": row["row_replay_hash"],
            "qwc_group_manifest_hashes": row["qwc_group_manifest_hashes"],
            "measurement_basis_manifest_hashes": row["measurement_basis_manifest_hashes"],
            "shard_hashes": row["shard_hashes"],
        }
        for row in row_bundle["rows"]
    ]
    denominator_decision = {
        "selected_ci_larger_basis_denominator_beaten_count": row_summary[
            "selected_ci_larger_basis_denominator_beaten_count"
        ],
        "denominator_win_count": 0,
        "same_access_denominator_win": False,
        "reason": "F1 candidate rows are assembled, but no same-access denominator win is established.",
    }
    optimizer_ledger = {
        "max_optimizer_loop_total_shots_lower_bound": row_summary[
            "max_optimizer_loop_total_shots_lower_bound"
        ],
        "accepted_priority_reopen_rows": row_summary["accepted_priority_reopen_rows"],
        "source_row_bundle_hash": assembled_summary["row_bundle_hash"],
    }
    b3_boundary = {
        "b3_reopen_ready": False,
        "multi_parameter_converged_chemistry": False,
        "reaction_dynamics_solution_claimed": False,
        "accepted_full_covariance_row_count": 0,
    }
    b10_boundary = {
        "b10_t1_credit_allowed": False,
        "positive_same_access_route_claimed": False,
        "bqp_separation_claimed": False,
        "denominator_win_count": 0,
    }
    claim_boundary = {
        "b3_reopen_ready": False,
        "reaction_dynamics_solution_claimed": False,
        "positive_same_access_route_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "what_is_supported": "A source-linked acceptance packet submission exists for the four-row F1 candidate bundle.",
        "what_is_not_supported": "The packet does not establish a same-access denominator win, accepted full-covariance row credit, B3 reopen, B10-T1 credit, quantum advantage, or BQP separation.",
    }
    packet = {
        "acceptance_packet_id": ACCEPTANCE_PACKET_ID,
        "provenance_manifest_id": PROVENANCE_MANIFEST_ID,
        "denominator_replay_manifest_id": DENOMINATOR_REPLAY_MANIFEST_ID,
        "row_replay_validation_manifest_id": ROW_REPLAY_VALIDATION_MANIFEST_ID,
        "downstream_packet_id": DOWNSTREAM_PACKET_ID,
        "priority_packet_hash": priority_summary["packet_hash"],
        "provenance_manifest_hash": row_summary["provenance_manifest_hash"],
        "denominator_manifest_hash": row_summary["denominator_manifest_hash"],
        "row_replay_validation_manifest_hash": row_summary["manifest_hash"],
        "row_scope_hash": stable_hash(row_scope),
        "full_covariance_row_table_hash": stable_hash(row_table),
        "compiled_state_replay_hash": stable_hash(compiled_state_replays),
        "pauli_grouping_covariance_replay_hash": stable_hash(qwc_covariance_replays),
        "derivative_estimator_replay_hash": stable_hash(
            {
                "status": "not_yet_replayed_for_acceptance",
                "source_row_bundle_hash": assembled_summary["row_bundle_hash"],
            }
        ),
        "selected_ci_fci_denominator_replay_hash": stable_hash(denominator_decision),
        "optimizer_loop_cost_ledger_hash": stable_hash(optimizer_ledger),
        "same_access_decision_hash": stable_hash(denominator_decision),
        "b10_access_boundary_hash": stable_hash(b10_boundary),
        "row_acceptance_ledger_hash": stable_hash(
            {
                "accepted_full_covariance_row_count": 0,
                "denominator_win_count": 0,
                "row_bundle_hash": assembled_summary["row_bundle_hash"],
                "accepted_f1_artifact": False,
            }
        ),
        "negative_boundary_nonpromotion_hash": stable_hash(claim_boundary),
        "accepted_full_covariance_row_count": 0,
        "denominator_win_count": 0,
        "optimizer_loop_total_shots_lower_bound": row_summary[
            "max_optimizer_loop_total_shots_lower_bound"
        ],
        "b3_reopen_boundary": b3_boundary,
        "b10_access_boundary": b10_boundary,
        "claim_boundary": claim_boundary,
        "source_evidence_files_present": True,
        "source_evidence_files": {
            "assembled_rows_gate": str(args.assembled_rows_gate),
            "row_replay_validation_manifest_gate": str(args.row_replay_validation_manifest_gate),
            "priority_packet_gate": str(args.priority_packet_gate),
        },
        "row_scope": row_scope,
        "full_covariance_row_table": row_table,
        "denominator_decision": denominator_decision,
        "optimizer_loop_cost_ledger": optimizer_ledger,
    }
    packet["acceptance_submission_hash"] = stable_hash(packet)
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--assembled-rows-gate",
        type=Path,
        default=Path("results/B3_B10_F1_assembled_rows_gate_v0.json"),
    )
    parser.add_argument(
        "--row-replay-validation-manifest-gate",
        type=Path,
        default=Path("results/B3_B10_full_covariance_row_replay_validation_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B3_B10_reopen_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/B3_B10_full_covariance_row_acceptance_packet_submissions/"
            "B3-R1-full-covariance-row-acceptance-packet.json"
        ),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    packet = build_packet(args)
    write_json(args.output, packet, args.pretty)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "acceptance_submission_hash": packet["acceptance_submission_hash"],
                "accepted_full_covariance_row_count": packet["accepted_full_covariance_row_count"],
                "denominator_win_count": packet["denominator_win_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
