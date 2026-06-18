# One-Year Research Roadmap v0.1

Last updated: 2026-06-13

Mission: build a credible future-quantum-computing research plan over 100
hard problems and produce original algorithmic or methodological attacks on at
least 10 of them.

## Year-End Success Criteria

By the end of 12 months, the program should have:

1. A source-backed catalog of 100 hard problems with stable IDs, evidence,
   attackability notes, and revision history.
2. A ranked portfolio of at least 10 quantum or quantum-inspired attack
   directions.
3. For each of the 10 directions: a problem statement, literature map,
   baseline, proposed method, validation benchmark, and result status.
4. At least 3 implemented prototypes or benchmark suites.
5. At least 2 paper-quality technical manuscripts or preprint drafts.
6. A clear record of negative results, failed assumptions, and abandoned paths.

## Phase 1: Foundation and Triage, Weeks 1-4

**Goal:** turn the 100-problem catalog into a defensible research portfolio.

Deliverables:

- Problem catalog v0.2 with source links per problem.
- Scoring matrix v0.2 with evidence notes and uncertainty.
- Top 20 shortlist with minimum publishable result for each.
- Top 10 attack pack v0.2.
- Literature map template and benchmark template.

Decision gate:

- Keep a problem in the top 10 only if it has a concrete validation path and a
  plausible one-year output.

## Phase 2: Literature and Baseline Reproduction, Months 2-3

**Goal:** avoid fantasy research by reproducing the strongest known baselines.

Deliverables:

- Literature map for each top 10 problem.
- Baseline implementations or resource-estimation notebooks for at least 5
  problems.
- A "claim ledger" tracking what each proposed method must beat.
- First internal review: kill or replace weak directions.

Decision gate:

- Each surviving direction must have either a theorem target, benchmark,
  resource-estimate target, or protocol metric.

## Phase 3: Prototype Algorithms, Months 4-6

**Goal:** produce original methods and test them against baselines.

Deliverables:

- Prototype 1: hardware-aware quantum circuit compression.
- Prototype 2: quantum error-correction code/decoder search.
- Prototype 3: molecular reaction dynamics resource estimator.
- Protocol draft: verifiable quantum advantage or classical output
  verification.
- Technical notes for all 10 directions.

Decision gate:

- At least 3 directions must show a measurable improvement, new theorem path,
  or publishable negative result.

## Phase 4: Deepening and Manuscripts, Months 7-9

**Goal:** convert the strongest prototypes into paper-grade contributions.

Deliverables:

- Manuscript draft 1: circuit compression or QEC overhead reduction.
- Manuscript draft 2: verification protocol, molecular resource estimate, or
  correlated-matter hybrid solver.
- Public benchmark package v0.1.
- External expert review plan.

Decision gate:

- Any direction without defensible novelty or validation is replaced by a Tier
  2 candidate.

## Phase 5: Integration, Months 10-12

**Goal:** produce the final research plan and publishable outputs.

Deliverables:

- Final 100-problem catalog with sources and rankings.
- Final 10-problem attack portfolio.
- Prototype and benchmark release.
- Manuscript submissions or preprints.
- Next-three-year research roadmap.

## Operating Cadence

- Weekly: one problem deep dive, one literature update, one benchmark update.
- Biweekly: portfolio score review.
- Monthly: kill/keep/merge decision for each top 10 direction.
- Quarterly: external review of methods and claims.

## Immediate Next Sprint

Sprint length: 2 weeks.

Sprint goals:

1. Upgrade `problem_catalog_100.md` from source-family support to per-problem
   source support for the top 20.
2. Create benchmark definitions for problem IDs 25, 22, 49, and 16.
3. Draft literature maps for IDs 25 and 22.
4. Define exact success metrics for the first prototype.

Sprint status:

- Top 20 source/evidence map started in `top20_evidence_map.md`.
- Benchmark definitions for IDs 25, 22, 49, and 16 started in
  `benchmark_specs_v0.md`.
- B1 seed circuits, hardware profiles, and a first metrics runner started in
  `../benchmarks/` and `../tools/b1_qasm_metrics.py`.
- B1 now has a conservative local rewrite baseline plus exact small-circuit
  statevector equivalence checks in `../tools/`.
- B1 has imported a first 10-circuit QASMBench small subset with exact
  equivalence-checked rewrite harness results.
- B1 has a first exact-equivalence-checked single-qubit block resynthesis
  prototype with non-trivial reductions on the QASMBench small subset.
- B1 single-qubit resynthesis now has a commuting-aware mode that safely
  improves the QASMBench small result under exact equivalence checks.
- B1 now has a first 2Q interaction-window resynthesis prototype
  (`cx-rz-cx -> rzz`) with exact equivalence and stronger hardware exposure
  reductions on QASMBench small.
- B1's current best QASMBench small pipeline is commuting-aware 1Q plus
  iterative RZZ resynthesis, reaching 9.26% heavy-hex-like exposure reduction
  under exact equivalence checks.
- B1's current best pipeline is now automated as a fixed-point runner so it can
  be reused on larger QASMBench/MQT subsets.
- B1 fixed-point runner has been validated on an exact-checkable QASMBench
  medium subset up to 15 qubits; small+medium aggregate now covers 16 circuits
  with zero equivalence failures.
- B1 interaction-simulation subset now reaches 19.13% heavy-hex-like exposure
  reduction with zero equivalence failures, close to the 20% target but still
  on only 2 targeted circuits.
- B1 hhl_n10 stress run exceeds 20% heavy-hex-like exposure reduction under
  structural local-rule certification, but global exact equivalence is skipped
  pending a scalable verifier.
- B1 fixed-point runner now emits local rewrite certificate summaries for 1Q
  resynthesis and RZZ windows; small exact and hhl_n10 stress reruns have
  machine-readable certificate counts in `../results/`.
- B1 now has JSONL per-rewrite proof logs plus an audit runner that checks
  summary counts, QASM input line references, and RZZ disjoint-commutation side
  conditions on both small exact and hhl_n10 stress reruns.
- B1 proof logs are now replayable: a replay checker reconstructs each pass
  output from proof events and verifies exact QASM output equality on both the
  small exact and hhl_n10 stress reruns.
- B1 proof logs now have local semantic checks: every recorded 1Q
  resynthesis and RZZ rewrite event passes matrix-level identity verification
  on both the small exact and hhl_n10 stress reruns.
- Portfolio audit added in `portfolio_status_report.md`: the 100-problem
  catalog has contiguous IDs 1-100, Top 20 evidence matches scoring, Top 10
  attack pack matches Tier 1, and B1 proof-log verification artifacts are
  present and passing.
- B2 low-overhead QEC is initialized with a reproducible repetition-code
  memory control baseline covering 40 distance/noise configurations; the
  portfolio audit now tracks the B2 baseline artifact.
- B2 now has a target-volume metric layer and a rough surface-code
  threshold-law estimate, explicitly marked as non-simulation planning
  evidence now that a real Stim/PyMatching baseline exists for direct
  circuit-level comparison.
- B2 now has a phenomenological repetition-code decoder fallback in
  `B2_phenomenological_repetition_decoder.md`: a small Viterbi/minimum-weight
  syndrome-history decoder runs over 12 distance/noise configurations. It
  improves 2 configurations over final-majority decoding, with the best
  configuration reducing logical error from 0.007 to 0.001. This is a decoder
  interface milestone, not a surface-code claim.
- B2 now has a Stim/PyMatching rotated surface-code memory baseline in
  `B2_stim_surface_code_memory_baseline.md`: 30 configurations, 90,000 total
  shots, distances 3/5/7, X/Z memory, physical error rates 0.001-0.01, and
  maximum decoder runtime of about 1.47e-5 seconds per shot. This is the first
  real surface-code baseline, not a searched-code improvement claim.
- B2 now has a Wilson-bounded target-volume table in
  `B2_stim_surface_code_target_volume.md`: 40 basis/error/target combinations,
  22 met and 18 unmet under the Wilson 95% upper-bound criterion. The strict
  1e-3 target is not certified by the current 3,000-shot sweep, even where
  observed failures are zero.
- B3 molecular reaction dynamics is initialized with a PySCF-backed small
  molecule resource proxy over H2, LiH, H2O, and N2; the portfolio audit now
  tracks the B3 resource artifact.
- B4 verifiable quantum advantage is initialized with a toy hidden-trap
  statistical protocol over 36 configurations; four simple spoofing families
  fail the current batch rule, but this is explicitly not a quantum advantage
  claim until real trap circuits and adversary implementations are added.
- B5 strongly correlated matter is initialized with a small exact
  diagonalization Hubbard benchmark over 15 configurations; 4-site cluster
  product proxies reduce mean energy error per site from 0.095526 to 0.020620
  versus 2-site proxies, defining a first embedding-error target.
- B6 high-temperature superconductivity search is initialized with a toy
  descriptor-ranking harness over 72 candidates; Top-12 precision against
  known high-Tc family labels is 0.833333, with cuprate-like, pnictide-like,
  and exploratory nickelate-like candidates surfaced.
- B7 architecture-level fault-tolerance co-design is initialized with a
  planning-level resource model across 3 workloads and 2 configurations; the
  co-designed layout gives a minimum 6.774x space-time-volume reduction under
  explicit scalar assumptions that must be replaced by real scheduling.
- B7 now has a B1/B2 dependency-schedule bridge in
  `B7_b1_b2_dependency_schedule_bridge.md`: it maps B1 virtual-SWAP
  before/after depth metrics onto a B2 Wilson-bounded surface-code target row.
  Across the aggregate and five high-impact circuits, the bridge gives a more
  conservative 1.195x-1.616x planning-level space-time-volume reduction. This
  is not a physical layout or lattice-surgery claim.
- B8 classical verification of quantum outputs is initialized with a toy
  hidden-invariant property tester across 3 tasks and 5 spoofing families;
  honest completeness is 1.0 and all 5 toy adversaries fail the current
  invariant rule, pending stronger adaptive spoofers.
- B8 now has an adaptive leakage spoofer stress test in
  `B8_adaptive_leakage_spoofer.md`: low and mid leakage fractions
  0.0/0.25/0.5 are rejected in the current synthetic setting, but 0.75 leakage
  lets the trap-aware leakage spoofer reach 0.792 soundness. This is a useful
  failure boundary that motivates challenge refresh and projection rotation.
- B9 Quantum PCP / Local Hamiltonian hardness is initialized with an exact
  small-instance gap lab over 18 configurations; no locality-preserving
  transformation passes the normalized-gap screen, while 4 counterexample
  candidates expose naive gap-amplification traps.
- B10 BQP-boundary mapping is initialized with a taxonomy/reduction graph over
  12 problem-family nodes and 14 edges; it identifies 8 advantage-preserving
  edges, 6 fragile edges, and 11 restricted theorem or negative-boundary
  targets, with data loading as the leading failure mode.
- The Top 10 execution board is now initialized in
  `top10_execution_board.md` and `top10_execution_board.json`, splitting the
  portfolio into primary manuscript, coupled application, verification
  protocol, and theory/negative-result lanes with explicit 30-day gates and
  kill/merge rules.
- B1 now has a generated certificate evidence report in
  `B1_certificate_report.md` and `B1_certificate_report.json`. It supports the
  current local-proof-log claim, records a 30-circuit exact aggregate with zero
  equivalence failures, and explicitly keeps the aggregate 20% exposure
  reduction, external-benchmark, and scalable global-equivalence gates open.
- B1 exact-checkable coverage was extended with
  `B1_exact_extension_manifest.yaml`, `../benchmarks/b1_exact_extension/`,
  `../tools/b1_generate_exact_extension.py`, and
  `../tools/b1_aggregate_exact_summaries.py`; the new 12-circuit generated
  suite passes exact equivalence plus audit/replay/semantic checks and lifts
  the exact aggregate to 30 circuits.
- B1 now has a 30-circuit ablation report in `B1_ablation_report.md` and
  `B1_ablation_report.json`: 1Q resynthesis explains most operation/depth
  reduction, while adjacent RZZ explains almost all two-qubit-gate reduction
  and most hardware-exposure reduction.
- B1 now has a first independent Qiskit baseline comparison in
  `B1_baseline_comparison.md` and `B1_baseline_comparison.json`. Qiskit
  levels 0 and 1 pass exact equivalence; level 3 is diagnostic only because it
  fails on 7 of 30 circuits. B1 beats the best exact-valid Qiskit row on the
  current metrics, but a routing-aware calibrated heavy-hex baseline remains
  open.
- B1 now has a Qiskit line-routing diagnostic in
  `B1_routing_baseline_diagnostic.md` and
  `B1_routing_baseline_diagnostic.json`. No line-routing level passes the
  bare statevector checker on all 30 circuits, but the sequential
  measurement-distribution checker now models mid-circuit measurement by
  branching/collapse and passes 30 of 30 circuits at levels 0, 1, and 3. This
  remains diagnostic-only, not a calibrated heavy-hex baseline.
- B1 line-routing measurement equivalence now has an independent Qiskit Aer
  shot-based cross-check: levels 0, 1, and 3 each pass 30/30 routed pairs with
  32,768 shots per pair. The maximum observed TVD is 0.04984 under the current
  dynamic threshold model, strengthening the diagnostic without promoting it
  to a calibrated heavy-hex claim.
- B1 now has a first Qiskit heavy-hex distance-3 topology diagnostic in
  `B1_heavyhex_routing_diagnostic.md` and
  `B1_heavyhex_routing_diagnostic.json`. Level 0 routes the 30-circuit suite
  onto a 19-qubit heavy-hex coupling map and passes 30/30 Aer cross-checks, but
  routing overhead worsens hardware-weighted exposure by 164.71%; this is a
  topology diagnostic, not a calibrated noise baseline.
- B1 now has a source-routed versus B1-routed heavy-hex end-to-end comparison
  in `B1_heavyhex_end_to_end_report.md` and
  `B1_heavyhex_end_to_end_report.json`. After Qiskit level-0 heavy-hex routing,
  B1 retains 16.95% operation-count reduction, 19.44% logical-depth reduction,
  20.55% idle-layer proxy reduction, and 2.93% exposure reduction, with 30/30
  Aer output cross-checks. Post-routing two-qubit count is unchanged, defining
  the next algorithmic bottleneck.
- The new `B1_heavyhex_end_to_end_suite.md` shows that Qiskit level 1 nearly
  erases the current B1 routed benefit: operation reduction falls to 0.03%,
  depth and exposure reductions fall to 0.00%, and post-routing 2Q reduction
  remains 0.00%. This strengthens the case for a routing-aware 2-4 qubit pass.
- B1 now has a per-circuit post-routing bottleneck profile in
  `B1_post_routing_bottleneck_profile.md` and
  `B1_post_routing_bottleneck_profile.json`: 16 circuits lose their level-0
  routed benefit under level 1, and the largest level-1 2Q bottlenecks are
  `gcm_h6`, `basis_trotter_n4`, `sat_n11`, and `hhl_n7`.
- B1 now has a first post-routing SWAP macro compression diagnostic in
  `B1_post_routing_swap_macro_report.md`: on the 30-circuit heavy-hex level-1
  routed suite it identifies 481 `cx-cx-cx` SWAP macros, removes 1,443 CX
  gates into 481 `swap` macros, reduces the macro-level 2Q count by 24.79%,
  and passes both local and end-to-end Aer cross-checks 30/30. This is
  explicitly not a native-basis hardware claim; it is the next algorithmic
  target for a native-basis-aware 2-4 qubit routing optimizer.
- B1 now has a measurement-aware virtual-SWAP elimination diagnostic in
  `B1_virtual_swap_elimination_report.md`: it removes 481 routed SWAPs from
  all 30 level-1 routed circuits by tracking a virtual wire permutation,
  reducing native CX/two-qubit count by 37.18% and passing local plus
  end-to-end Aer cross-checks 30/30. Its proof-log replay consumes all
  481 wire-permutation events with 0 output mismatches and 0 replay errors.
  Measurement operands are remapped when no classical control or reset is
  present; dynamic-circuit semantics remain the next B1 compiler milestone.
- B1 now has a documented synthetic heavy-hex noise proxy in
  `B1_synthetic_noise_proxy_report.md`: under the fixed
  `heavy_hex_like_sparse` profile, source level-1 routed vs virtual-SWAP shows
  32.65% exposure reduction and a 12748.39x relative success-proxy ratio. This
  is explicitly not a live backend calibration; it defines the next
  native-basis routing target.

First prototype recommendation:

Start with **Problem 25: hardware-aware quantum circuit compression** because
it has the best one-year validation path, clear metrics, and direct usefulness
to almost every other quantum direction.
