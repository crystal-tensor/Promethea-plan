# B1/B7 Cone01 R109 Public Artifact Dereference Contract Gate

- Target: `T-B1-004hg/T-B7-016p`
- Upstream target: `T-B1-004hf/T-B7-016o`
- Method: `b1_b7_cone01_r109_public_artifact_dereference_contract_gate_v0`
- Status: `cone01_r109_public_dereference_contract_ready_url_only_rejected`
- Model status: `r108_preflight_requires_public_artifact_dereference_challenge`

## Result

R109 adds the public dereference layer after R108. It rejects URL-only
evidence and cached transcript evidence, requiring live public HTTP
transcripts bound to the challenge nonce before any R108 rerun or
single-counter audit can proceed.

## Key Counters

- Required fields: `16`
- Acceptance gates: `13`
- URL-only packet accepted: `False`
- URL-only gates passed / failed: `8` / `7`
- Cached transcript packet accepted: `False`
- Cached transcript gates passed / failed: `12` / `3`
- Counter transition accepted: `False`
- Counter delta: `0`
- Accepted external reproductions: `0`
- Accepted external falsifications: `0`
- New credit delta: `0`

## Requirements

- `A1` PASS: R109 binds the R108 result and verifier rules
- `A2` PASS: R109 emits a challenge-nonce public dereference contract and template
- `A3` PASS: R109 rejects URL-only public artifact claims
- `A4` PASS: R109 rejects cached transcripts that are not live public fetches
- `A5` PASS: R109 keeps counters and new credit at zero
- `A6` PASS: R109 emits blockers for live transcript, nonce binding, and separate counter audit

## Artifacts

- Result JSON: `results/B1_B7_cone01_R109_public_artifact_dereference_contract_gate_v0.json`
- Contract: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R109-G1-public-artifact-dereference-contract/public-artifact-dereference-contract.json`
- Template: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R109-G1-public-artifact-dereference-contract/public-artifact-dereference-packet.template.json`
- URL-only packet: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R109-G1-public-artifact-dereference-contract/url-only-public-artifact-negative-control.json`
- URL-only verdict: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R109-G1-public-artifact-dereference-contract/url-only-public-artifact-preflight.verdict.json`
- Cached transcript packet: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R109-G1-public-artifact-dereference-contract/cached-transcript-negative-control.json`
- Cached transcript verdict: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R109-G1-public-artifact-dereference-contract/cached-transcript-preflight.verdict.json`
- Blocker queue: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R109-G1-post-public-dereference-contract-blocker-queue.json`

## Claim Boundary

R109 is a dereference-contract and negative-control gate. It does not
accept an external reproduction, does not move a counter, and does not
grant B7/O3/resource/layout credit.
