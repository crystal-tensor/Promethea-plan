# AI Agent Collaboration Protocol

Last updated: 2026-06-15

This protocol lets multiple AI agents work on the project without stepping on
each other or inflating claims.

## Agent Packet

Each agent should start by writing or updating a packet:

```text
Agent ID:
Track:
Task:
Branch/work packet:
Claim boundary:
Expected files:
Validation commands:
Blockers:
```

## Agent Types

| Agent type | Must do | Must not do |
|---|---|---|
| Builder | Create scripts, results, and notes. | Approve its own claim. |
| Baseline Adversary | Try to beat or erase a result. | Weaken baselines to make a result look good. |
| Theorist | Formalize assumptions and lemmas. | Claim broad separations from restricted notes. |
| Integrator | Connect B-tracks and update manifests. | Merge without audit coverage. |
| Auditor | Run checks and update reports. | Rewrite scientific claims to sound stronger. |
| Translator | Draft paper/patent/tool after gate. | Start translation before gate approval. |

## Work Isolation

Agents should avoid editing the same file unless one of them owns integration.
Suggested ownership:

- Track agents own `research/B*_*.md`, `benchmarks/B*.yaml`, and `tools/b*_*.py`.
- Audit agent owns `tools/research_portfolio_audit.py`.
- Program manager owns `research/current_stage_brief.html` and `research/ops/`.

## Required Claim Boundary

Every result must state:

- what is now supported;
- what is still not supported;
- what stronger baseline or proof obligation comes next.

Example:

```text
Now supported: B3 D5 rows have FCI small-basis denominators.
Still not supported: no quantum implementation, no full reaction dynamics,
no basis-complete chemistry claim, no BQP separation.
Next proof pressure: compare a concrete quantum observable-estimation circuit
against this denominator.
```

## Collision Handling

If two agents want the same task:

1. The first agent to mark the task as claimed owns the builder role.
2. The second agent should become baseline adversary or reviewer.
3. If both produced artifacts, an integrator creates a comparison PR.

## Merge Rule

No PR should be merged into the main research line unless:

- it has a reproducible command;
- result files exist;
- claim boundaries are explicit;
- audit passes or the failure is intentionally documented;
- one reviewer other than the builder has checked the claim.
