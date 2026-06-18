# B1-B10 Translation Pipeline v0.1

Last updated: 2026-06-13

Purpose: park downstream translation options for after the B1-B10 technical
gates pass. The current goal is to solve the technical problems first. This
document should not be used as the active success criterion until the relevant
B-direction has passed its technical solution gate.

Status: **deferred_until_b1_b10_technical_gates_pass**.

Legal note: patent sections are invention-disclosure drafts for technical
planning. They are not legal advice and should be reviewed by qualified patent
counsel before any filing or public disclosure.

## Portfolio Thesis

The most coherent near-term venture is not a general quantum-computing moonshot.
It is a verification-first quantum software stack:

1. **B1** reduces circuit cost with replayable proof logs.
2. **B2** turns physical/logical error assumptions into target-volume baselines.
3. **B7** connects B1 and B2 into end-to-end fault-tolerant resource estimates.
4. **B4/B8** verify outputs and expose adaptive-spoofer failure boundaries.
5. **B3/B5/B6** supply application markets in chemistry and correlated
   materials once the platform has stronger baselines.
6. **B9/B10** create theoretical guardrails, negative results, and defensible
   claim boundaries.

## 12-Month Output Targets

| Stream | Target | Lead lanes | Current status |
|---|---:|---|---|
| Manuscripts/preprints | 3 main drafts + 1 theory note | B1/B2/B7, B4/B8/B10, B3/B5/B6, B9/B10 | First evidence exists; no completed manuscript yet. |
| Patent disclosures | 5 provisional-ready drafts | B1, B2, B4/B8, B7, B5/B6 | Technical claim sketches exist; counsel review still needed. |
| Fundable projects | 3 fundable venture/grant packages | Compiler assurance, QEC benchmarking, verification/security | Needs pitch deck, customer discovery, and milestone budget. |
| Monetizable tools | 4 productizable tools | Audit CLI, QEC bench, verifier lab, materials screener | Research scripts exist; product packaging not started. |

## Manuscript Pipeline

### M1: Certified Hardware-Aware Quantum Circuit Compression

**Lead:** B1 with B2/B7 support.

**Working title:** Certified virtual-SWAP elimination for topology-aware quantum
circuit compression.

**Core claim to prove:** measurement-aware virtual-SWAP elimination can reduce
post-routing two-qubit count and synthetic exposure while preserving replayable
semantic certificates.

**Evidence already present:** 30/30 circuits rewritten; 481 virtual SWAPs and
1443 CX gates removed; 37.18% two-qubit reduction; 32.65% synthetic exposure
reduction; proof replay passed 481/481.

**Manuscript gate:** reproduce against at least one calibrated/live-like
heavy-hex baseline and one broader benchmark family; include limitations around
layout finality, dynamic circuits, and synthetic-noise assumptions.

**Target artifact:** `paper_m1_certified_compression_outline.md`, then a
preprint draft.

### M2: Target-Volume QEC Baselines and Cross-Layer Resource Accounting

**Lead:** B2 and B7.

**Working title:** Wilson-bounded target-volume accounting for surface-code
baselines and compiler-aware fault-tolerant scheduling.

**Core claim to prove:** QEC comparisons should be reported as target-volume
tables with confidence bounds, and compiler reductions should count only after
they survive dependency scheduling.

**Evidence already present:** B2 Stim/PyMatching baseline with 30 configs and
90,000 shots; B2 Wilson target-volume table with 40 combinations; B2
same-hardware reduced-round candidate with 120 configs / 360,000 shots and 22
Wilson target-volume improved rows; B2 robustness stress with 240 configs /
1,200,000 shots showing 88 stressed improved rows, all aggressive d-4 and 0
non-aggressive d-2; B7 B1/B2 dependency-schedule bridge with conservative
1.195x-1.616x STV reduction.

**Manuscript gate:** a non-aggressive or physically motivated reduced-round
variant must survive larger distances/shots, leakage/correlated-noise fields,
and noise-mismatch stress; then B7 needs a real workload DAG with
factory-throughput variants.

**Target artifact:** `paper_m2_target_volume_codesign_outline.md`.

### M3: Leakage-Resilient Verification of Quantum Outputs

**Lead:** B4 and B8 with B10 guardrails.

**Working title:** Challenge-refresh hidden-invariant tests for classically
verifiable quantum outputs.

**Core claim to prove:** hidden invariants and trap tasks can reject low/mid
leakage spoofers, while adaptive leakage experiments expose the exact point
where challenge refresh becomes necessary.

**Evidence already present:** B4 toy trap protocol rejects four spoofing
families; B8 hidden-invariant verifier has honest completeness 1.0 and rejects
five adversaries; B8 adaptive leakage test identifies 0.75 leakage as dangerous.

**Manuscript gate:** circuit-level hidden task generator, challenge refresh,
projection rotation, and adaptive generative spoofers.

**Target artifact:** `paper_m3_verification_protocol_outline.md`.

### M4: Application/Materials Position Paper

**Lead:** B3, B5, B6.

**Working title:** Observable-first quantum simulation descriptors for
correlated chemistry and superconducting-material search.

**Core claim to prove:** quantum simulation should focus on observables that
feed downstream materials ranking, not full wavefunction reconstruction.

**Evidence already present:** B3 PySCF small-molecule resource proxy; B5 exact
Hubbard cluster proxy; B6 toy descriptor ranker.

**Manuscript gate:** reaction-coordinate toy path, stronger tensor/boundary
baseline, and real or curated materials table with leakage controls.

**Target artifact:** `paper_m4_observable_descriptors_outline.md`.

### M5: Theory Note

**Lead:** B9 and B10.

**Working title:** Negative-result scaffolds for quantum PCP gap amplification
and BQP advantage-boundary claims.

**Core claim to prove:** some tempting gap-amplification or advantage-preserving
routes fail under formal locality, normalization, input-model, or verifier
assumptions.

**Evidence already present:** B9 small gap lab with four counterexample
candidates; B10 graph with 12 nodes, 14 edges, and 11 restricted theorem
targets.

**Manuscript gate:** one formal negative lemma or two restricted theorem target
definitions.

**Target artifact:** `paper_m5_theory_guardrails_note.md`.

## Patent Disclosure Pipeline

### IP1: Measurement-Aware Virtual-SWAP Elimination With Proof Replay

**Linked lanes:** B1, B7.

**Potential invention:** a compiler pass that detects routed SWAP macros whose
logical effect can be represented as a tracked wire/measurement map, removes the
physical SWAP gates, and emits proof events that can be replayed against local
and end-to-end measurement semantics.

**Why it might be protectable:** the current implementation combines SWAP-macro
recognition, virtual wire mapping, measurement-awareness, and replayable proof
logs in one auditable workflow.

**Current evidence:** 481 virtual SWAPs removed, 1443 CX gates removed, 481/481
proof events replayed successfully.

**Pre-filing tasks:** prior-art search on virtual qubit remapping, Pauli-frame
tracking, routing-pass optimizers, and compiler certificate systems; document
novel implementation details and failure cases.

### IP2: Wilson-Bounded Target-Volume Selection for QEC Code/Schedule Choice

**Linked lanes:** B2, B7.

**Potential invention:** a method for selecting QEC codes, schedules, or decoder
settings by comparing target logical error rates under confidence-bounded
space-time volume rather than point-estimate logical error.

**Why it might be protectable:** it packages confidence-bound estimation,
decoder runtime, physical footprint, and schedule selection into one
decision-making layer.

**Current evidence:** 40 Stim surface-code target-volume combinations with
Wilson 95% high criterion; 22 met and 18 unmet; same-hardware reduced-round
candidate finds 22 improved target-volume rows, but robustness stress shows the
positive signal is currently aggressive-only.

**Pre-filing tasks:** prior-art search on surface-code resource estimators,
reduced-round syndrome extraction, schedule-level QEC overhead selection,
decoder benchmarking, and statistical confidence intervals in QEC selection.

### IP3: Challenge-Refresh Hidden-Invariant Verification

**Linked lanes:** B4, B8, B10.

**Potential invention:** a quantum-output verification protocol that rotates
hidden invariants or projections after detecting leakage-risk thresholds, so
adaptive spoofers cannot reuse inferred challenges.

**Why it might be protectable:** the leakage stress test is used as an active
control signal for challenge refresh rather than only a post-hoc metric.

**Current evidence:** low/mid leakage spoofers rejected; 0.75 leakage identified
as dangerous with trap-aware spoofer soundness of 0.792.

**Pre-filing tasks:** build circuit-level task generator; document refresh
policy; compare against trap-based verification, UBQC, Mahadev-style
verification, XEB, shadows, and property testing.

### IP4: Dependency-Scheduled Fault-Tolerance Co-Design Engine

**Linked lanes:** B1, B2, B7.

**Potential invention:** a resource estimator that schedules algorithm blocks,
compiler reductions, target-volume QEC rows, and factory throughput together,
then reports the surviving system-level resource delta.

**Why it might be protectable:** it turns local compiler/QEC improvements into a
dependency-aware resource ledger with explicit kill conditions for erased
savings.

**Current evidence:** B7 B1/B2 bridge with 6 comparisons and conservative STV
reduction of 1.195x-1.616x. The FT synthesis ledger exposes `gcm_h6` as the
current min row, and the `w8_21` claim-boundary closure shows 43480 optimizer
runs, 0 exact replacements, and 0 ledger removal, so repeated templates cannot
be counted as physical savings without occurrence-removing certificates.

**Pre-filing tasks:** add real workload DAGs, magic-state factory variants,
occurrence-removing rewrite certificates, and physical-layout assumptions.

### IP5: Leakage-Audited Mechanism-Aware Materials Descriptor Ranking

**Linked lanes:** B5, B6, B3.

**Potential invention:** a candidate-ranking system that combines
strong-correlation observables, materials descriptors, and explicit
family-prior leakage audits before recommending superconducting candidates.

**Why it might be protectable:** the key is not generic materials ML, but a
leakage-audited pipeline driven by quantum-simulation-derived descriptors.

**Current evidence:** B6 toy ranking harness; B5 exact/cluster proxy; B3
observable-first resource proxy.

**Pre-filing tasks:** add real retrospective data, time/family splits, and
descriptor provenance.

## Fundable Project Packages

### F1: Quantum Compiler Assurance Platform

**Product thesis:** organizations experimenting with quantum workloads need to
know whether a compiler reduced real cost or merely moved risk into routing,
measurement mapping, or verification gaps.

**Core assets:** B1 proof logs, B1 virtual-SWAP elimination, B7 resource bridge,
B10 claim-boundary taxonomy.

**Funding route:** SBIR/STTR or seed round for a developer-tooling company.

**First customer profile:** quantum software teams, hardware labs, and research
groups running compiler benchmarks.

**Milestone budget target:** build CLI, dashboard, benchmark pack, certificate
export, and three customer pilots.

### F2: QEC Target-Volume Benchmarking Service

**Product thesis:** quantum hardware and architecture teams need comparable
QEC overhead accounting with confidence bounds and decoder runtime included.

**Core assets:** B2 Stim/PyMatching baseline, B2 target-volume table, B2
same-hardware schedule candidate and aggressive-only robustness boundary, B7
resource bridge.

**Funding route:** DOE/NSF grant plus enterprise pilots.

**First customer profile:** hardware companies, national labs, and academic
architecture groups.

**Milestone budget target:** expand code families, run larger sweeps, and
publish reproducible target-volume leaderboards.

### F3: Quantum Verification and Spoofing Lab

**Product thesis:** as quantum advantage claims proliferate, customers need a
red-team testbed for classical spoofing, leakage, challenge refresh, and output
verification.

**Core assets:** B4 trap protocol, B8 adaptive leakage stress, B10 claim
boundary graph.

**Funding route:** security-oriented seed project, government grants, or
enterprise verification pilots.

**First customer profile:** quantum cloud providers, benchmark authors,
defense/lab evaluation teams, and auditors of quantum-advantage claims.

**Milestone budget target:** implement circuit-level task generator, spoofer
library, protocol dashboard, and report templates.

### F4: Quantum-Risk and PQC Migration Adjacent Tool

**Product thesis:** near-term revenue can come from helping companies inventory
quantum risk and post-quantum cryptography migration while the deeper quantum
R&D stack matures.

**Core assets:** B10 boundary map and verification discipline; this is adjacent
to the research portfolio rather than a direct B1-B9 output.

**Funding route:** service revenue or lightweight SaaS before larger quantum
tooling revenue.

**First customer profile:** security teams needing PQC migration inventories
after standardized post-quantum cryptography guidance.

**Milestone budget target:** build assessment templates, crypto-inventory
connectors, and executive risk reports.

## Monetizable Tool Roadmap

| Tool | Linked lanes | MVP | Paying user | 90-day deliverable |
|---|---|---|---|---|
| Q-Cert Compiler Audit CLI | B1/B7/B10 | Run benchmark circuits, emit reductions, proof logs, and limitation report. | Quantum software teams and labs. | Package existing B1 scripts behind one CLI with HTML/JSON report export. |
| QEC Target-Volume Bench | B2/B7 | Run Stim/PyMatching sweeps, produce Wilson-bounded target-volume tables, and stress same-hardware schedule candidates. | Hardware and architecture teams. | Hosted or local benchmark runner with reproducible configs plus aggressive-only boundary warnings. |
| Quantum Verification Red-Team Lab | B4/B8/B10 | Generate hidden tasks, run spoofers, show completeness/soundness/leakage curves. | Benchmark designers and quantum cloud evaluators. | Merge B4/B8 into a shared task interface. |
| Materials Descriptor Screener | B3/B5/B6 | Rank candidate materials with leakage-audited descriptors and provenance. | Materials R&D teams. | Replace synthetic B6 data with curated retrospective dataset. |

### T1 MVP Status

The first monetizable tool now has a runnable MVP wrapper:

- CLI: `../tools/qcert_audit_cli.py`
- Markdown report: `QCERT_MVP_REPORT.md`
- JSON report: `../results/qcert_audit_mvp_report.json`

This wrapper currently packages existing B1/B7 evidence into a customer-readable
audit report. It is not yet an end-to-end customer-circuit runner.

## Next 30 Days

1. Promote **B1 Q-Cert** as the lead product and paper path.
2. Write M1 manuscript outline and IP1 invention disclosure in more formal
   claim language.
3. Package a single CLI command that runs B1 virtual-SWAP elimination and emits
   a customer-readable report.
4. Expand B2 target-volume sweeps, add non-aggressive reduced-round stress cases, and design QEC Benchmark MVP screens.
5. Merge B4/B8 task interfaces and define a verification red-team demo.
6. Draft one-page project briefs for F1, F2, and F3.

## External Reference Anchors

- USPTO provisional patent application overview:
  https://www.uspto.gov/patents/basics/apply/provisional-application
- NSF America's Seed Fund SBIR/STTR:
  https://seedfund.nsf.gov/
- DOE SBIR/STTR:
  https://science.osti.gov/sbir
- NIST post-quantum cryptography project:
  https://csrc.nist.gov/projects/post-quantum-cryptography
