# Future Quantum Computing Research Plan

This workspace is the working base for a one-year research program aimed at
the hardest long-horizon scientific and technological problems where quantum
computing, quantum-inspired algorithms, or new computational methods may create
breakthrough leverage.

## Current Artifacts

- `../benchmarks/`: draft YAML manifests for the first executable benchmark
  families.
- `problem_catalog_100.md` and `problem_catalog_100.json`: frozen v1.0
  catalog of exactly 100 candidate problems across mathematics, computation,
  quantum computing, physics, materials, biology, climate, AI, security, and
  civilization-scale engineering. The catalog is read-only for future work:
  use it for routing, citation, display, translation, and audit checks, not for
  expansion, reranking, Top 10 remapping, or recurring metadata polishing.
- `scoring_matrix.md`: scoring rubric and first-pass priority ranking.
- `attack_pack_10.md`: first 10 candidate attack directions with research
  hypotheses, method sketches, and validation targets.
- `source_registry.md`: authoritative source families and links used to seed
  the catalog.
- `top20_evidence_map.md`: source-backed evidence map for the first Top 20
  ranked problems.
- `benchmark_specs_v0.md`: first benchmark definitions for the first four
  quantum attack directions.
- `top10_execution_board.md` and `top10_execution_board.json`: portfolio
  execution board with lanes, 30-day gates, kill/merge rules, and manuscript
  bets for B1-B10.
- `B1_certificate_report.md` and `B1_certificate_report.json`: generated
  evidence package for the leading B1 manuscript track, including supported
  claims, unsupported claims, proof-log status, and next technical gates.
- `B1_ablation_report.md` and `B1_ablation_report.json`: generated 30-circuit
  ablation report separating 1Q resynthesis, adjacent RZZ, and final fixed-point
  contributions.
- `B1_baseline_comparison.md` and `B1_baseline_comparison.json`: independent
  Qiskit all-to-all `u3/cx` baseline comparison for the B1 30-circuit exact
  suite.
- `B1_routing_baseline_diagnostic.md` and
  `B1_routing_baseline_diagnostic.json`: Qiskit line-routing diagnostic for
  the B1 30-circuit suite. It is explicitly diagnostic-only and does not close
  the calibrated heavy-hex routing-baseline gate. The current diagnostic also
  includes Qiskit Aer shot-based cross-checks for 90 routed pairs.
- `B1_heavyhex_routing_diagnostic.md` and
  `B1_heavyhex_routing_diagnostic.json`: first Qiskit heavy-hex distance-3
  topology diagnostic for B1. It routes the 30-circuit suite to a 19-qubit
  heavy-hex coupling map and keeps calibrated-noise claims open.
- `B1_heavyhex_end_to_end_report.md` and
  `B1_heavyhex_end_to_end_report.json`: source-routed versus B1-routed
  heavy-hex comparison showing which B1 compression benefits survive topology
  routing.
- `B1_heavyhex_end_to_end_suite.md` and
  `B1_heavyhex_end_to_end_suite.json`: level-0/level-1 suite summary showing
  that Qiskit level 1 nearly erases the current B1 routed benefit.
- `../benchmarks/B1_exact_extension_manifest.yaml` and
  `../benchmarks/b1_exact_extension/`: deterministic generated B1 extension
  suite that lifts exact-checkable coverage to 30 circuits.
- `B1_prototype_notes.md`: current executable prototype notes for Problem 25
  circuit-compression metrics.
- `B2_prototype_notes.md` through `B10_prototype_notes.md`: executable v0
  notes for QEC overhead, molecular resource estimation, verifiable advantage,
  strongly correlated matter, and high-temperature superconductivity ranking
  fault-tolerance co-design, output-verification, and local-Hamiltonian gap
  and BQP-boundary baselines.

## Selection Principles

Each problem is scored from 1 to 5 on:

- `Q`: Quantum leverage. Can quantum computation, quantum simulation,
  quantum information, or quantum-inspired math plausibly change the frontier?
- `Y`: One-year output. Can a serious team produce publishable theory,
  prototype algorithms, benchmarks, or negative results within 12 months?
- `I`: 50-year impact. Would progress reshape science, security, energy,
  health, or civilization-scale capability?
- `V`: Verification path. Is there a concrete benchmark, theorem target,
  simulation target, experiment, or falsifiable milestone?
- `O`: Original algorithm space. Is there room for a genuinely new method,
  not only incremental application engineering?

Total score is `Q + Y + I + V + O`, with a maximum of 25.

## Working Rule

The catalog is not a claim that these are objectively the only hardest 100
problems in the world. It is a disciplined candidate set for choosing research
targets. Each version should improve source support, formulation precision,
and attackability.

After each new prototype or benchmark update, rerun:

`python3 tools/research_portfolio_audit.py --json-output research/portfolio_status_report.json --markdown-output research/portfolio_status_report.md --pretty`

The audit now checks both artifact integrity and whether the Top 10 execution
board still matches the attack pack.
