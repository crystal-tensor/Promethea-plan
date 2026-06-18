# Axiom Horizon

**An AI Multi-Agent Research Program for Quantum Computing's Hardest Frontiers**

Broader open-source mission: challenge the world's hardest 100 problems through
AI multi-agent research, with a 2-3 year concentrated push on the Top 10
technical frontier tracks.

[Repository target](https://github.com/crystal-tensor/Axiom-Horizon)

---

## Mission

Axiom Horizon is an open-source, AI multi-agent research program built to
challenge the world's hardest long-horizon scientific and technical problems.

The project starts from a living, open map of **100 hard problems**. Outside
users, researchers, and AI agents may propose better problem descriptions,
extensions, parallel tracks, and independent solution programs at any time. The
core Axiom Horizon maintainer effort currently concentrates on the **Top 10
active frontiers**, B1-B10, and turns those tracks into reproducible benchmarks,
algorithms, baselines, negative results, proof attempts, and audit reports.

Our 2-3 year target is not hype. It is a disciplined research goal:

> Build a global, open, AI-assisted research machine that can make credible,
> auditable progress toward solving at least part of the Top 10 frontier
> problems.

We do not claim that any world problem is solved today. We claim that the
project has a structure for making progress that can be reproduced, attacked,
improved, and merged by researchers and AI agents around the world.

## What Makes This Different

Axiom Horizon is not a normal notes repository. It is a research operating
system:

- **Open 100-problem universe**: contributors may open issues or PRs to improve,
  extend, challenge, or launch parallel work on any problem in the catalog.
- **Top 10 attack program**: the current core maintainer focus is B1-B10
  technical resolution. Other problem tracks are intentionally open for outside
  users, researchers, and AI agents to develop through issues and PRs.
- **Multi-agent workflow**: human researchers and AI agents can claim tasks,
  open PRs, and submit reproducible artifacts.
- **Claim boundaries**: every result must say what it does and does not prove.
- **Audit-first culture**: important claims must pass
  `tools/research_portfolio_audit.py`.
- **Translation after evidence**: papers, patents, fundraising, and tools come
  after technical gates, not before.

## Top 10 Active Research Tracks

| Track | Frontier | Current aim |
|---|---|---|
| B1 | Quantum compilation and circuit compression | Reduce routed work and non-Clifford/T-resource proxies with replayable certificates. |
| B2 | Low-overhead quantum error correction | Beat surface-code target volume under honest, same-condition baselines. |
| B3 | Molecular reaction dynamics | Test quantum observable estimation against strong selected-CI/FCI denominators. |
| B4 | Verifiable quantum advantage | Build circuit-level tasks with explicit completeness and soundness pressure. |
| B5 | Strongly correlated quantum matter | Compare embedding, tensor, MPS/DMRG, and quantum response kernels on hard observables. |
| B6 | High-temperature superconductivity | Build leakage-controlled candidate ranking using physics descriptors. |
| B7 | Fault-tolerant quantum computing at scale | Propagate B1/B2 gains through factories, layout, and full resource ledgers. |
| B8 | Classical verification of quantum outputs | Stress challenge-refresh verifiers against leakage and generative spoofers. |
| B9 | Quantum PCP / local Hamiltonian hardness | Produce restricted theorem targets, checked skeletons, and useful negative lemmas. |
| B10 | Boundary of BQP | Separate robust quantum advantage from data-loading, oracle, and verification assumptions. |

## Current Status

The project is active and unfinished.

Current evidence includes:

- an open 100-problem catalog with discipline and source-lineage metadata;
- B1-B10 execution boards and detailed dossiers;
- reproducible scripts under `tools/`;
- machine-readable results under `results/`;
- human-readable research notes under `research/`;
- an audit report in `research/portfolio_status_report.md`;
- a current status page in `research/current_stage_brief.html`.

The current B5/B10 line has recently moved from small-cluster denominators to
seeded MPS pressure, non-seeded one-site MPS/ALS pressure, and a two-site
finite-DMRG-style pressure prototype. B5 now has a canonical-DMRG readiness
audit plus a canonical-environment smoke gate over the same 9 B5/B10 D5 Hubbard
response rows: 8 readiness conditions evaluated, 0 passed, 8 failed; the smoke
gate finds 9 environment ledgers, 0 smoke-passed rows, 3 rows passing the
fixed-sector, variance, discarded-weight, and monotonicity checks, 0 rows close
to the seeded MPS pressure response, and 0 rows beating seeded MPS pressure.
The B5/B10 same-access production contract now makes that blocker explicit:
10 contract gates are checked, only row coverage and no-forbidden-claim gates
pass, 8 gates fail, there is still no production DMRG, no sampling oracle,
no same-access positive route, and no BQP or quantum-advantage claim.
The latest B10-T1 stress test still finds no positive same-access route because
0 rows beat explicit D5 matvec-equivalent costs by shots. This is progress, but
it is not a production DMRG result, not a deployable tensor solver, not a
sampling oracle, and not a quantum advantage claim.

B4/B8 now has an OpenQASM 3 randomized-measurement packet for the shared
hidden-projection verifier spine. The packet exports 36 hardware-executable
verifier circuits across 3 tasks, 3 refresh modes, and 4 circuit instances per
task-mode; every file starts with `OPENQASM 3.0`, the maximum circuit size is
30 qubits including verifier ancillas, and the Qiskit/Aer semantic mismatch
count is 0. This is a circuit packet and semantic check only, not hardware
execution, sampling hardness, cryptographic soundness, quantum advantage, or a
BQP separation claim.

The follow-up B4/B8 public-packet spoofer gate rejects a public-protocol
soundness interpretation of that packet. A deterministic parser/emulator can
predict all 36 public OpenQASM 3 packet transcripts, giving a public-packet
spoofer acceptance rate of 1.0. This is a guardrail, not a failure of a private
protocol: the next gate must late-bind private challenge material, use real
backend or hardware execution, or attack transcripts that do not embed the
verifier's private material in public QASM.

The next B4/B8 late-bound private-challenge contract gate now separates the
public skeleton from verifier-private masks and challenge flips for all 36
packet circuits, but it also keeps the hard blocker visible: the public data
skeletons are still deterministic X/CX/measure circuits, so the data transcript
is classically predictable. The contract passes 4 of 8 gates and fails 4 of 8;
late-bound private parity challenges alone are not enough for protocol
soundness without non-stabilizer structure, real backend properties, hardware
execution, or otherwise non-public/non-predictable transcripts.

The follow-up non-stabilizer late-bound transcript pilot now adds an H plus
T/RZ(pi/4) challenge-basis layer to all 36 public skeletons. It removes the
deterministic transcript blocker: 36/36 pilot circuits have non-stabilizer
basis gates, the old deterministic emulator no longer predicts a single
transcript, minimum min-entropy is 4 bits, and maximum output probability is
0.0625. This is still an exact small-probability pilot, not hardware execution,
cryptographic soundness, sampling hardness, quantum advantage, or BQP
separation.

The next B4/B8 support-aware spoofer gate keeps that boundary honest. Four
public-support spoofer families attack all 36 pilot circuits. Exact transcript
guessing remains capped at 0.0625, so the single-transcript blocker survives,
but a support-only verifier is fully spoofable with support acceptance 1.0.
That rejects support-membership soundness and forces the next protocol step
toward verifier-private predicates, real backend properties, or hardware
randomized-measurement execution.

B6 has moved from a synthetic descriptor toy to curated leakage audits and a
structural/electronic proxy boundary. The latest B6 screen keeps 38 records
across 22 families with 12 expanded negative controls; structural/electronic
AP@12 improves to 0.611 versus formula AP@12 of 0.10, but family-prior AP@12
remains 1.0 and the top 12 still include 3 negative controls. This is not a
material-discovery or solved-mechanism claim; the next gate is real
crystallographic, DFT, or B5-computed observables.

B2 has moved past the earlier reduced-round artifact into a leakage-flagged
erasure analytic boundary: 480 configurations, 42 proxy target-volume improved
rows, 33 distance-5/7 improved rows, no reduced rounds, and no new-code,
threshold, device, or circuit-level decoder claim.

B2 now also has a Stim HERALDED_ERASE / DEPOLARIZE1 stress boundary, a
false-positive overhead stress, a posterior-calibrated shot-conditioned leakage
boundary, a posterior-weighted decoder-risk ledger, a decoder-input contract
feasibility gate, a per-shot decoder trace packet, a posterior-likelihood
injection gate, a DEM-informed detector-to-edge semantics gate, and a
hardware-like leakage observation model gate. The latest B2 gate consumes three
strict challenge rows across three observation profiles / 1,728 profile-shots,
with 864 holdout profile-shots. The best conservative hardware-like profile
generates 415 model flag events, changes 0 predictions, fixes 0 failures,
introduces 0 failures, and leaves 22 injected failures; holdout failure delta is
also 0. The improvement gate remains false, the route remains demoted, and the
model is still not calibrated or hardware-derived. This is still not a
circuit-level decoder, production decoder, threshold, hardware result,
quantum-advantage result, or new-code claim.

B9 now has a local parametric certificate checker for the
`cluster_stabilizer_open_uniform_reweight` family. It checks the n >= 4
formula-level term count, support set {2,3}, max locality 3, exact uniform
scale 27/20, finite rows n=4,5,6, and normalized-gap invariance with a
repo-local exact-rational verifier. The certificate remains rejected as
raw-gap-only rescaling. This is not a Lean/mathlib theorem, not a Quantum PCP
proof, not an NLTS theorem, and not a global gap-amplification no-go theorem.

B1/B7 now has a template-priority gate for the current `gcm_h6` bottleneck.
The gate evaluates the 12 retained nonlocal templates from the B7 scan and
finds 0 single-template one-angle routes that clear the one-sided 1.20x
`gcm_h6` target. The best template remains `w8_21`, but it needs at least 2
arbitrary removals per occurrence and still has no exact occurrence-removing
certificate after 43,480 prior optimizer runs. This is not a resource-saving
claim, not a symbolic lower bound, and not a solved B7 result; it narrows the
next useful work to a symbolic KAK/Clifford-scaffold proof, an alternate
certified rewrite, or stronger B1 T-resource reduction.

B1 now also has a `gcm_h6` target selector. It reads the current U3
phase-factored B1 QASM, counts 270 arbitrary decimal rotations, and ranks
families that could meet the B7 target if a future rewrite removes one rotation
per occurrence: 3 local CNOT-cone classes, 2 canonical angle classes, and 4
qubit classes meet the 30-occurrence target. This is a target-selection
artifact only; it is not a rewrite, not a semantic certificate, and not a
resource-saving claim.

B1/B7 now further has a cone-feasibility gate for the same `gcm_h6` bottleneck.
The 3 target cone classes cover 111 occurrences, but strict direct
CNOT-rotation-CNOT sandwiches total only 4. Under a stricter pair-local
single-arbitrary-window filter, only `cone_01` clears the 30-occurrence target,
with 35 candidate windows. This makes `cone_01` the next concrete rewrite
target; it is still not a rewrite, not a semantic certificate, and not a
resource-saving claim.

B1/B7 also has a restricted `cone_01` phase-removal gate. It tests all 35
candidate windows under a narrow same-envelope hypothesis: delete the arbitrary
RY or replace it with a local Z phase while keeping the two surrounding CNOTs.
The result is negative: remove-only, fixed Z-phase replacement, and continuous
RZ replacement each have 0 exact-pass windows at tolerance 1e-8. The best
continuous-RZ residual is 0.36435162331705345. This closes the simple
phase-absorption route, but it is not a global obstruction theorem and not a
B7 resource-saving claim.

B1/B7 now has one more restricted `cone_01` gate: Euler reabsorption. It locks
the arbitrary RY to 9 exact/Clifford-like candidate angles and lets neighboring
target-qubit RZ phases reoptimize inside the same two-CNOT envelope. Across the
same 35 windows, the exact-pass count is still 0; the best residual is
0.21253656711362606 and the median residual is 0.3643516233170531. This closes
another narrow same-envelope route and pushes the next useful work toward
broader two-qubit synthesis or a KAK/Clifford scaffold.

B1/B7 also now has a `cone_01` parameter-transfer obligation gate. It checks
the same 35 candidate windows and finds that all 35 original RY(theta)
occurrences have nonzero unitary sensitivity, 0 are near the pi/4 exact grid,
and the windows collapse into 4 theta groups. This means deletion without a
theta carrier cannot clear the B7 30-window target. Future synthesis must
explicitly carry, share, or eliminate theta with replayable certificates before
any B7 ledger saving can be counted.

B1/B7 now also has a `cone_01` theta-sharing ledger gate. The 4 theta groups
create 31 duplicate theta occurrences and an optimistic cache-reuse signal of
620 proxy-T units, which would clear the 600 proxy-T target only under a cache
model. The current occurrence-based FT ledger does not accept that as a physical
saving: counted occurrence removal is 0, counted proxy-T reduction is 0, and the
B7 target remains uncleared. The next useful `T-B1-004` artifact must therefore
produce at least 30 occurrence-removing certificates or justify a new physical
theta-sharing cost model before B7 can count a resource delta.

The follow-up `cone_01` physical cost-model gate now makes that second route
explicit. A shared-theta synthesis object proposal gate defines 4 machine-readable
objects covering all 35 candidate windows, a replay-verifier gate checks 4/4
objects plus 35/35 occurrences against source QASM and parameter-transfer groups
with 0 mismatches, and a logical layout/routing scaffold assigns anchor qubits
and route packets for all 35 occurrences. A factory-amortization scaffold then
accounts for the 35 per-occurrence synthesis requests collapsing to 4 shared-object
requests, with 31 amortized saved compiles and a gross 620 proxy-T pressure delta.
The next shared-error budget scaffold allocates a 1e-6 aggregate synthesis-error
budget across the 4 shared-theta objects and records 4 correlation groups. The
cost-model scaffold has moved from 0/8 to 5/8 acceptance gates by passing
CM-02 object existence, CM-03 replay, CM-04 logical layout/routing, and CM-05
factory amortization, and CM-06 shared-error budgeting. The model is still not
accepted: there are no 30 occurrence-removing certificates, no physical device
layout, no physical factory schedule, no device-calibrated error validation, no
independent baseline, and no refreshed B7 ledger. The counted B7 ledger
reduction remains 0.

## Repository Layout

```text
.
├── README.md
├── CONTRIBUTING.md
├── GOVERNANCE.md
├── BOUNTIES.md
├── RESEARCH_FRAMEWORK.md
├── LICENSE
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── benchmarks/     # YAML benchmark manifests and inputs
├── tools/          # Reproducible scripts, simulators, analyzers, auditors
├── results/        # Machine-readable result artifacts
└── research/       # Reports, status pages, task boards, proof skeletons
```

## How To Contribute

1. Read `RESEARCH_FRAMEWORK.md`.
2. Pick a task from `research/ops/agent_task_board.md`.
3. Create a branch:

```text
agent/<agent-id>/<B-id>/<short-task>
```

4. Add artifacts:

- benchmark or manifest changes in `benchmarks/`;
- executable method or verifier in `tools/`;
- machine-readable output in `results/`;
- human-readable explanation in `research/`;
- audit integration in `tools/research_portfolio_audit.py` when the result
  becomes part of project state.

5. Run the audit:

```bash
python3 tools/portfolio_refresh_check.py
```

6. Open a PR using `.github/PULL_REQUEST_TEMPLATE.md`.

## AI Agent Collaboration

Axiom Horizon is designed for many agents working in parallel:

- builder agents implement algorithms and experiments;
- baseline adversary agents try to beat or invalidate claimed progress;
- theory agents write proof targets, lemmas, and counterexamples;
- audit agents wire new artifacts into status checks;
- integration agents connect B-tracks such as B1 -> B7 and B5 -> B10;
- maintainer agents review, merge, and update the roadmap.

Codex is the current coordinating maintainer agent for this repository. In
practice, that means Codex keeps the project structure coherent, enforces claim
boundaries, routes tasks into PR-sized units, and keeps the audit trail from
drifting away from the actual evidence.

## Bounties And Funding

If the project raises funding, we intend to create public bounty tasks for
high-value PRs: stronger baselines, proof formalization, DMRG/tensor references,
hardware verifier runs, real-data benchmarks, and independent reproductions.

Funding, sponsorship, and bounty coordination contact:

```text
wavefunction61@gmail.com
```

Use the bounty template in `.github/ISSUE_TEMPLATE/bounty_task.md` when
proposing paid work.

## Claim Policy

Every PR must include a claim boundary:

- what is now supported;
- what is still not supported;
- what stronger baseline or proof pressure could kill the result;
- whether the result is a positive result, negative result, or diagnostic.

Forbidden without evidence:

- claiming a Top 10 problem is solved;
- claiming quantum advantage without a strong denominator;
- claiming hardware relevance without device-like assumptions;
- claiming patentability, fundability, or product readiness before a technical
  gate passes.

## License

This project is released under the Apache License 2.0. See `LICENSE`.
