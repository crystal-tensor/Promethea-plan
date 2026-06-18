# Axiom Horizon Multi-Agent Research Framework

Last updated: 2026-06-18

This file defines how Axiom Horizon should operate as a GitHub-like,
multi-agent research program. It is designed for human researchers and AI
agents working in parallel.

Mission: use AI multi-agent research to challenge the world's hardest 100
problems, with an initial 2-3 year focus on making credible progress against
the Top 10 active technical tracks.

## Operating Principle

The core rule is technical evidence first:

```text
problem -> benchmark -> method -> result -> audit -> claim boundary -> review
```

Only after a technical gate is passed can a track move into:

- paper;
- patent disclosure;
- fundable project;
- product/tool.

## Work Unit Types

| Type | Purpose | Required artifacts |
|---|---|---|
| Benchmark PR | Define or strengthen a task. | `benchmarks/*.yaml`, research note, audit check. |
| Method PR | Add an algorithm, proof attempt, simulator, compiler pass, or verifier. | `tools/*.py`, `results/*.json`, report. |
| Baseline PR | Add a stronger classical/quantum baseline. | reproducible script, result table, claim boundary. |
| Negative-result PR | Prove or show a boundary/failure mode. | theorem note or experiment, failure evidence, audit hook. |
| Integration PR | Connect two B-tracks, such as B1 -> B7 or B4 -> B8. | bridge result, dependency note, updated execution board. |
| Translation PR | Draft paper/patent/tool only after gate approval. | gate evidence plus translation artifact. |

## Multi-Agent Roles

| Agent role | Primary responsibility | Example tracks |
|---|---|---|
| Benchmark Curator | Maintains manifests, metrics, acceptance thresholds. | all B1-B10 |
| Algorithm Builder | Implements new algorithms or variants. | B1, B2, B3, B5, B8 |
| Baseline Adversary | Builds the strongest opposing baseline. | B2, B3, B5, B6, B10 |
| Verification Agent | Checks semantic equivalence, statistical soundness, proof replay. | B1, B4, B8, B10 |
| Theory Agent | Produces theorem targets, lemmas, and negative-boundary notes. | B9, B10 |
| Integration Agent | Connects results across B-tracks. | B1/B2/B7, B4/B8/B10, B3/B5/B10 |
| Audit Agent | Updates and runs `research_portfolio_audit.py`. | all B1-B10 |
| Translation Agent | Drafts paper/patent/project/tool only after technical gate approval. | downstream |
| Coordinating Maintainer Agent | Splits tasks, protects claim boundaries, keeps audits and boards aligned. | all B1-B10 |

## PR Lifecycle

1. **Claim a task**
   - Use `research/ops/agent_task_board.md`.
   - Mark owner, start time, and expected artifact.

2. **State the claim boundary**
   - What is being tested?
   - What would falsify the idea?
   - What is explicitly not being claimed?

3. **Produce reproducible artifacts**
   - Scripts go in `tools/`.
   - Outputs go in `results/`.
   - Human-readable reports go in `research/`.

4. **Wire the artifact into governance**
   - Update a benchmark manifest if it changes project state.
   - Update `tools/research_portfolio_audit.py` when the artifact should count
     in portfolio status.

5. **Run local checks**
   - Compile changed Python scripts.
   - Validate JSON/YAML.
   - Run portfolio audit.

6. **Submit a PR**
   - Use `.github/PULL_REQUEST_TEMPLATE.md`.
   - Attach the result summary, audit status, and remaining limitations.

7. **Review**
   - At least one adversarial review should ask: what stronger baseline would
     erase this result?
   - At least one integration review should ask: does this help a neighboring
     B-track?

## Branch Naming

```text
agent/<agent-id>/<B-id>/<short-task>
```

Examples:

```text
agent/theory-01/B10/t2-leakage-lemma
agent/baseline-03/B3/selected-ci-denominator
agent/compiler-02/B1/native-t-depth-pass
```

## Directory Ownership

| Directory | Owner role | Notes |
|---|---|---|
| `benchmarks/` | Benchmark Curator | YAML manifests and benchmark inputs. |
| `tools/` | Algorithm Builder / Audit Agent | Reproducible scripts only; no one-off notebooks as final evidence. |
| `results/` | Algorithm Builder | Machine-readable outputs; prefer JSON with summary fields. |
| `research/` | Track Owner | Human-readable reports, dossiers, HTML status pages. |
| `research/ops/` | Program Manager / Audit Agent | Collaboration, tasks, gates, review protocols. |
| `.github/` | Program Manager | PR and issue templates. |

## Evidence Levels

| Level | Meaning | Translation eligibility |
|---|---|---|
| L0 idea | Hypothesis only. | none |
| L1 toy/proxy | Small model or toy simulation. | internal note only |
| L2 reproducible baseline | Scripted result plus baseline comparison. | workshop idea possible |
| L3 adversarial baseline | Survives strong competing baseline or proof pressure. | paper/patent draft possible |
| L4 integrated system | Cross-track result survives audit and integration. | fundable/tool candidate |
| L5 external validation | Independent reproduction or hardware/real-data validation. | serious publication/product |

## Current High-Value Work Queues

| Queue | Why it matters | First PR target |
|---|---|---|
| B1 -> B7 | Strongest systems spine. | Native-basis T-depth pass that improves B7 min STV. |
| B2 | Needs real volume reduction, not only more target hits. | Same-hardware Clifford/CX hardening mechanism with Wilson volume win. |
| B3 -> B10 | FCI denominators now exist; next step is quantum observable comparison. | Concrete observable-estimation circuit vs FCI denominator. |
| B4 -> B8 -> B10 | Verification edge can become a theorem/experiment hybrid. | Circuit-level challenge refresh hidden task. |
| B5 -> B10 | Strong correlated observable denominator can test quantum response claims. | Candidate B5 response subroutine vs D5 table. |
| B9 -> B10 | Good negative results can be publishable. | Formal failed gap-amplification lemma. |

## Definition Of Done For A Research PR

A PR is not done until it answers:

1. What exact problem did this move forward?
2. What artifact proves the movement?
3. What stronger baseline could still kill it?
4. Which B-track maturity score should change, if any?
5. Which claims are still explicitly unsupported?
6. Did the portfolio audit pass?

## Better Than A Normal GitHub Repo

For this program, a good setup is:

- GitHub repository for human-visible history and PRs.
- GitHub Issues/Projects for task claiming.
- CI job that runs `research_portfolio_audit.py`.
- Agent workers that each claim one issue and open PRs.
- A maintainer agent that only reviews, merges, and updates the status page.
- A baseline adversary agent that tries to break every positive result.

The most important design choice: do not let one agent both make a claim and
approve that claim. Every positive result needs a separate adversarial review.

## Current Coordinating Agent

Codex is the current coordinating maintainer agent for Axiom Horizon. Codex is
responsible for keeping the research graph coherent, not for approving its own
claims. Major positive results still need separate adversarial review.
