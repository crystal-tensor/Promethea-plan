# Governance

## Project Name

Axiom Horizon / 公理视界计划

## Mission Owner

The project founder sets the long-range mission: use AI multi-agent research to
challenge the world's hardest 100 problems and focus the first technical push
on the Top 10 active tracks.

## Coordinating Maintainer Agent

Codex is the current coordinating maintainer agent.

Responsibilities:

- keep the repository structure coherent;
- split work into PR-sized research tasks;
- maintain the B1-B10 execution board;
- enforce claim boundaries;
- require reproducible artifacts;
- keep `tools/research_portfolio_audit.py` aligned with project state;
- route positive claims to baseline-adversary review;
- keep translation work downstream of technical gates.

## Human And Agent Contributors

Contributors may be humans, AI agents, or human-agent teams.

All contributors must:

- work through branches and PRs;
- state the B-track and task ID;
- include reproducible commands;
- document what is still not solved;
- avoid unsupported breakthrough, fundraising, or product claims.

## Review Model

Every important PR should receive at least two review modes:

- **builder/integration review**: does it improve the intended B-track?
- **baseline-adversary review**: what stronger denominator, proof pressure, or
  counterexample could erase the result?

Positive results need adversarial review. Negative results need usefulness
review: what future false claim does this prevent?

## Merge Standard

A PR can be merged when:

- artifacts are present in the expected directories;
- the claim boundary is explicit;
- relevant commands reproduce or clearly document failure;
- JSON/YAML/HTML parse checks pass where relevant;
- `research_portfolio_audit.py` passes when project status changes;
- remaining blockers are documented.

## Top 100 Catalog Rule

The 100-problem catalog is frozen. Contributors should not add, remove, rerank,
or remap the catalog by default. Work should focus on B1-B10 technical
artifacts unless the founder explicitly reopens the catalog.

