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
extensions, parallel tracks, and independent solution programs. The core Axiom
Horizon effort currently concentrates on the **Top 10 active frontiers**,
B1-B10, and turns those tracks into reproducible benchmarks, algorithms,
baselines, negative results, proof attempts, and audit reports.

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

- **Open 100-problem universe**: contributors may open issues or PRs to
  improve, extend, or launch parallel work on any problem.
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
seeded and non-seeded MPS pressure references. This is progress, but it is not
a completed DMRG result and not a quantum advantage claim.

B6 has moved from a synthetic descriptor toy to a curated retrospective
materials leakage audit: 26 records across 12 families, explicit post-2008
time split, family-prior comparison, and no material-discovery or solved
mechanism claim.

B2 has moved past the closed reduced-round artifact into a leakage-flagged
erasure analytic boundary: 480 configurations, 42 proxy target-volume improved
rows, 33 distance-5/7 improved rows, no reduced rounds, and no new-code,
threshold, device, or circuit-level decoder claim.

B2 now also has a Stim HERALDED_ERASE / DEPOLARIZE1 stress boundary: 108
configurations, 216k shots, 10 target-volume improved rows, all at candidate
distance 5 or 7, and no shot-conditioned erasure-decoder, threshold, hardware,
or new-code claim.

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
python3 tools/research_portfolio_audit.py \
  --json-output research/portfolio_status_report.json \
  --markdown-output research/portfolio_status_report.md \
  --pretty
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
