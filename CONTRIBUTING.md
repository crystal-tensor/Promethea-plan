# Contributing To Axiom Horizon

Axiom Horizon accepts contributions as research PRs. A contribution can be
from a human researcher, an AI agent, or a human-agent pair.

## What Counts As A Valid Contribution

A valid PR should move the 100-problem / Top 10 program forward. Most active
work should target at least one B-track:

- B1 circuit compression
- B2 quantum error correction
- B3 molecular reaction dynamics
- B4 verifiable quantum advantage
- B5 strongly correlated matter
- B6 superconductivity search
- B7 fault-tolerance co-design
- B8 classical verification of quantum outputs
- B9 Quantum PCP / Local Hamiltonian
- B10 BQP boundary map

The frozen 100-problem catalog is a read-only routing map by default. Do not
rerank, replace, or expand it unless the project founder explicitly reopens
that catalog work.

## Required PR Sections

Every PR should include:

1. Track ID: `B1` through `B10`.
2. Work unit type: benchmark, method, baseline, negative result, integration,
   audit, or translation.
3. Claim boundary: what is and is not being claimed.
4. Reproducible command.
5. Changed artifacts.
6. Audit result.
7. Remaining blockers.

## Artifact Rules

- Use `benchmarks/` for benchmark definitions and manifests.
- Use `tools/` for executable scripts.
- Use `results/` for machine-readable outputs.
- Use `research/` for human-readable interpretation.
- Use `research/ops/` for program-management docs.
- Do not put final evidence only in chat logs.
- Do not make publication, patent, financing, or product claims before a
  technical gate is passed.

## Local Checks

Run the checks that match your PR:

```bash
python3 -m py_compile tools/<changed_script>.py
python3 -m json.tool results/<changed_result>.json >/tmp/result.jsoncheck
python3 tools/portfolio_refresh_check.py
```

`tools/portfolio_refresh_check.py` also parses benchmark YAML, key portfolio
JSON files, and the current HTML status page. Use `--require-clean` in CI or
release gates when regenerated audit/status artifacts must already be committed.

For ad hoc YAML or HTML-only debugging, you can still run:

```bash
python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
import yaml

for path in Path("benchmarks").glob("*.yaml"):
    yaml.safe_load(path.read_text(encoding="utf-8"))

HTMLParser().feed(Path("research/current_stage_brief.html").read_text(encoding="utf-8"))
print("parse checks ok")
PY
```

## Review Standard

Reviewers should prioritize:

- hidden assumptions;
- missing baselines;
- reproducibility gaps;
- unsupported claims;
- integration impact on neighboring tracks;
- audit coverage.

Positive results should receive adversarial review. Negative results should
receive usefulness review: what future false claim does this prevent?

## Bounty Contributions

Some issues may be marked as bounty candidates when funding is available.
Bounty coordination contact:

```text
wave function61@gmail.com
```

Paid or unpaid, bounty PRs follow the same evidence rules: reproducible
artifact first, claim boundary always.

## Translation Rule

Translation artifacts are welcome only after a technical gate is passed.

Allowed after gate:

- paper outline or manuscript;
- patent disclosure draft;
- fundable project memo;
- product/tool specification.

Not allowed before gate:

- claiming a world problem is solved;
- claiming quantum advantage without a denominator;
- claiming hardware relevance without device-like assumptions;
- claiming fundability or patentability without technical novelty evidence.
