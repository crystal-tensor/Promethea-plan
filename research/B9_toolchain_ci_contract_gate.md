# B9 Lean/Lake CI Contract Gate

Status: **toolchain_ci_contract_open_pending_remote_run**

T-B9-004e adds a GitHub Actions handoff for the B9 Lean/Lake scaffold. It defines how an external runner should install the pinned Lean toolchain, expose Lake, run `lake update`, check the B9 Lean module, and refresh the B9 proof-environment gates. This is a CI contract, not a recorded proof-assistant success.

## Metrics

- Workflow template: `research/ci/b9-lean-proof-scaffold.yml`
- Active workflow present locally: `False`
- CI contract requirements passed / failed: 7 / 1
- Failed CI contract requirement IDs: `['C8']`

## Requirements

| ID | Pass | Requirement | Evidence |
| --- | --- | --- | --- |
| C1 | yes | B9 Lean workflow template exists | research/ci/b9-lean-proof-scaffold.yml |
| C2 | yes | workflow is scoped to B9 proof files | paths include B9, proof_skeletons, tools, results, and benchmark |
| C3 | yes | workflow installs pinned toolchain from lean-toolchain | toolchain=leanprover/lean4:v4.12.0 |
| C4 | yes | workflow exposes both Lean and Lake version probes | lean --version / lake --version |
| C5 | yes | workflow runs Lake dependency resolution | lake update with mathlib4 dependency |
| C6 | yes | workflow checks the B9 Lean module | B9/ClusterStabilizer/WidthLocality.lean |
| C7 | yes | workflow refreshes B9 proof-environment gates | readiness, contract, and scaffold refresh commands |
| C8 | no | active remote CI run artifact is present | the OAuth token cannot activate .github/workflows here; no remote CI run artifact or checked theorem output is recorded in this repository |

## Claim Boundary

- The CI handoff template exists and is scoped to B9 proof files.
- The template must be copied into `.github/workflows/` by a token with workflow scope before it can run on GitHub.
- No remote CI run artifact is recorded yet.
- No proof-assistant checked theorem is claimed.
- No Quantum PCP, NLTS, or global gap-amplification theorem is claimed.
