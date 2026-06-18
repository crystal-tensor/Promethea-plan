# Agent Task Board

Last updated: 2026-06-18

Use this as a lightweight GitHub Projects board until the repo is published.

Status values:

- `open`
- `claimed`
- `in_review`
- `merged`
- `blocked`

## Priority Queue

| Task ID | Track | Status | Owner | Role | Target artifact |
|---|---|---|---|---|---|
| T-B1-001 | B1 | merged | codex | Builder | Native-basis non-Clifford/T-depth optimizer with B7 min-STV retest input. |
| T-B1-002 | B1/B7 | merged | codex | Builder | Targeted non-Clifford optimizer for factory-boundary workloads where native retest still has 1.0x STV. |
| T-B1-003 | B1/B7 | merged | codex | Builder | U3 phase-factored native Euler optimizer for remaining arbitrary-rotation factory cost after control-RZ pass. |
| T-B1-004 | B1/B7 | open | unassigned | Builder | Remove another 344 logical T proxy from `sat_n11` to reach 1.20x min STV, or prove the current local phase passes cannot do it. |
| T-B2-001 | B2 | merged | codex | Builder | Same-hardware reduced-round schedule candidate plus robustness boundary: 120 configs / 360k shots found 22 volume-improved rows, max reduction 3.0x; 240-config / 1.2M-shot stress preserved 88 aggressive rows but 0 non-aggressive improved rows, so the claim remains aggressive-only diagnostic. |
| T-B2-002 | B2 | merged | codex | Builder | Reduced-round artifact boundary: current same-hardware signal closes as small-distance/aggressive-schedule artifact; original 22 improved rows and stress-preserved 88 improved rows are all aggressive, distance-3, one-round candidates, with 0 non-aggressive improved rows; not a new-code, threshold, or calibrated-device claim. |
| T-B2-003 | B2 | merged | codex | Builder | Leakage-flagged erasure analytic boundary: 480 configurations, 335 candidate-met rows vs 264 baseline-met rows, 42 proxy target-volume improved rows, 33 distance-5/7 improved rows, 19 high-efficiency distance-5/7 rows, max reduction 23.904x, mean reduction 4.837x, validation errors 0; no reduced rounds, no d=3 candidates, and no new-code, threshold, device, or circuit-level decoder claim. |
| T-B2-004 | B2 | merged | codex | Builder/Baseline Adversary | Stim HERALDED_ERASE / DEPOLARIZE1 circuit-derived leakage stress: 108 configs / 216k shots, 72 target comparisons, 59 candidate-met rows vs 53 baseline-met rows, 7 candidate-only target hits, 10 improved volume rows, all 10 at candidate distance 5 or 7, max reduction 4.598x, mean reduction 2.623x, validation errors 0; not a shot-conditioned erasure decoder, calibrated leakage model, threshold, hardware, or new-code claim. |
| T-B2-005 | B2 | open | unassigned | Builder/Baseline Adversary | Replace the Stim detector-error-model stress with a shot-conditioned erasure decoder or calibrated leakage model; preserve d=5/d=7 target-volume rows under noise mismatch and realistic flag false-positive overhead, or demote the leakage-erasure route. |
| T-B3-001 | B3/B10 | merged | codex | Builder | Reaction-coordinate quantum observable-estimation circuit proxy vs FCI denominator: 4 OpenQASM proxy circuits aligned to B10-T1 FCI derivative rows, max 21 qubits and 441 controlled-phase gates; FCI denominator beaten count remains 0, not quantum advantage or reaction-dynamics solution. |
| T-B3-002 | B3 | open | unassigned | Baseline Adversary | Selected-CI or larger-active-space denominator beyond STO-3G rows. |
| T-B3-003 | B3/B10 | merged | codex | Builder | Hamiltonian Pauli-term mapper comparison: Qiskit Nature Jordan-Wigner circuits for 4 B3 reaction-coordinate rows, 4 QASM measurement packets, max 20 qubits, max 2951 mapped Pauli terms, max conservative shot floor 30,504,129,929, state-preparation and variance costs included; FCI denominator wins remain 0. |
| T-B3-004 | B3/B10 | merged | codex | Builder/Baseline Adversary | Sampled Pauli-estimator confidence intervals: 4 Hamiltonian-mapped B3 rows, 2048 pilot shots per random Pauli term, 99% z=2.576 intervals all cover exact HF Pauli energy, max Neyman target shot floor 6,570,468 vs previous upper-bound floor 30,504,129,929, reduction range 442x-34,544x; still 0 FCI wins and not selected-CI/larger-active-space evidence. |
| T-B3-005 | B3/B10 | merged | codex | Builder/Baseline Adversary | Selected-CI larger-basis denominator and grouped Pauli boundary: 4 same reaction coordinates, H2/LiH in cc-pVDZ and H2O/N2 in 3-21G selected-CI finite differences, all selected-CI points converged, max 19 spatial orbitals / 38 spin-orbital qubits, max selected determinant product 400, QWC packet reduction 1.0x-4.17x, max ansatz two-qubit executions 289,100,592, 0 larger-basis denominator wins; not a large-basis quantum mapper or advantage claim. |
| T-B3-006 | B3/B10 | merged | codex | Builder/Baseline Adversary | Larger-basis Hamiltonian mapper boundary: the same selected-CI denominator bases are now Jordan-Wigner mapped, covering 4 rows with max 38 qubits, max 77,858 Pauli terms, max conservative same-basis bucket count 77,116, max Neyman target shot floor 6,464,114,739, max ansatz two-qubit executions 956,688,981,372, and 0 selected-CI larger-basis denominator wins; not optimal grouping, chemical state prep, or advantage. |
| T-B3-007 | B3/B10 | merged | codex | Builder/Baseline Adversary | Larger-basis QWC grouping boundary: actual bitmask first-fit QWC covers for the 4 larger-basis B3 Hamiltonians reduce measurement settings 3.09x-3.96x, with max previous bucket count 77,116 -> max QWC groups 19,644 and max group size 291; shot floor is not reduced without covariance propagation, and selected-CI larger-basis denominator wins remain 0. |
| T-B3-008 | B3/B10 | merged | codex | Builder/Baseline Adversary | Grouped-observable covariance shot-floor boundary: exact HF product-state covariance inside the larger-basis QWC groups reduces independent-term shot floors 4.91x-5.58x, with max floor 6,464,114,739 -> 1,283,900,037, max nonzero covariance pairs 73,474, and max ansatz two-qubit executions 190,017,205,476; selected-CI larger-basis denominator wins remain 0. |
| T-B3-009 | B3/B10 | merged | codex | Builder/Baseline Adversary | Chemical state-preparation derivative boundary: grouped-covariance energy floors are propagated through three-point finite-difference derivative error, inflating shot floors 10000x with max 1,283,900,037 -> 12,839,000,370,000; UCCSD/ADAPT/adiabatic 2Q prep envelopes are now charged, max UCCSD prep 1,493,030 2Q gates and max UCCSD executions 18,497,517,970,970,500,000; sampled correlated-state covariance remains unsupported and denominator wins remain 0. |
| T-B3-010 | B3/B10 | merged | codex | Builder/Baseline Adversary | Compiled UCC/ADAPT covariance pilot: H2/cc-pVDZ one-parameter UCC-double/ADAPT-seed state has sampled covariance on 48 sampleable QWC groups, 512 shots/group, mean/max relative variance error 0.0068/0.0827; exact compiled-state center floor is 66,955,026 vs HF 63,465,167, derivative floor is 669,550,260,000, optimizer-loop total shots 24,773,359,620,000, and optimizer-loop 2Q executions 7,531,101,324,480,000; no denominator win. |
| T-B3-011 | B3/B10 | merged | codex | Builder/Baseline Adversary | Cross-molecule UCC/ADAPT pressure and demotion boundary: H2/LiH/H2O/N2 bounded high-coefficient sampled covariance pressure uses 35 sampled groups total, 384 shots/group, mean/max relative variance error 0.0833/0.5029; optimistic optimizer-loop lower-bound shots reach 475,043,013,690,000 and lower-bound 2Q executions reach 281,225,464,104,480,000, so B3 is demoted to a negative-boundary track until a multi-parameter state prep or new measurement strategy changes the denominator comparison. |
| T-B3-012 | B3/B10 | open | unassigned | Builder/Baseline Adversary | Rescue-only B3 attempt: produce a real multi-parameter UCCSD/ADAPT covariance result or stronger-than-QWC measurement strategy that beats selected-CI/DMRG/tensor denominators after optimizer-loop accounting; otherwise keep B3 demoted and move effort to B5/B10 or B4/B8. |
| T-B4-001 | B4/B8 | merged | codex | Builder | Circuit-level CNOT hidden-projection task with challenge refresh/projection rotation: 192 configs, honest completeness 1.0, no-refresh high-leakage max soundness 0.675, repaired high-leakage max soundness 0.0; proxy only, not a quantum advantage claim. |
| T-B4-002 | B4/B8 | open | unassigned | Builder/Adversary | Upgrade the CNOT hidden-projection proxy to hardware-executable randomized measurement circuits or attack it with trained/generative spoofers. |
| T-B5-001 | B5/B10 | merged | codex | Builder/Baseline Adversary | Boundary-field response embedding baseline: same 9 B10 D5 Hubbard density-response rows, 7-field oracle-tuned edge-field grid, mean/max relative response error 0.0541/0.1216, exact D5 max Hilbert dimension 4900 versus max embedded cluster dimension 36; denominator only, no quantum response or accuracy-per-resource win claimed. |
| T-B5-002 | B5/B10 | merged | codex | Builder/Baseline Adversary | Non-oracle response embedding denominator: same 9 B10 D5 Hubbard rows, predeclared selection rule using zero-field cluster embedding for 4-site rows and inverse-size two/four-site cluster extrapolation for larger rows, selected mean/max relative response error 0.05098/0.12308, 4 meaningful rows beating the prior oracle-tuned boundary-field denominator after-the-fact; exact D5 targets used only for evaluation, no quantum response or accuracy-per-resource win claimed. |
| T-B5-003a | B5/B10 | merged | codex | Builder/Baseline Adversary | Exact-state-seeded MPS/Schmidt truncation pressure reference: same 9 B10 D5 Hubbard rows, bond dimensions 2/4/8/16, selected bond dimension 16, mean/max response error 0.000442/0.001695, min exact-ground-state overlap 0.999101, 6 rows beating the small-cluster non-oracle embedding denominator; explicitly not variational DMRG, not deployable tensor solver, and not quantum/accuracy-per-resource win. |
| T-B5-003b | B5/B10 | merged | codex | Builder/Baseline Adversary | Non-exact-state-seeded variational MPS/ALS pressure prototype: same 9 B10 D5 Hubbard rows, bond dimensions 2/4, 3 restarts x 8 sweeps, selected mean/max response error 0.01806/0.03907, min overlap 0.9626, 0 rows beating exact-state-seeded MPS pressure reference; explicitly not production DMRG and not quantum/accuracy-per-resource win. |
| T-B5-003 | B5/B10 | open | unassigned | Builder/Baseline Adversary | Replace the MPS/ALS prototype with mature canonical-environment variational DMRG/MPS, or compare a candidate quantum impurity/response kernel after state-preparation, measurement, optimizer-loop, and classical denominator costs. |
| T-B6-001 | B6 | merged | codex | Baseline Adversary | Curated retrospective materials table with family/time leakage audit: 26 records / 12 families, post-2008 split, high-Tc threshold 30 K, all-physics AP@10 0.89 vs random AP@10 mean 0.5346, post-split physics AP 0.9094 vs family-prior AP 0.9379 and random AP mean 0.9030, validation errors 0; explicitly not a material-discovery or solved-mechanism claim. |
| T-B6-002 | B6/B5 | merged | codex | Builder/Baseline Adversary | Formula-derived descriptor screen: 38 records / 22 families with 12 expanded negative controls, embedded element-table descriptors, and B5-linked correlation/screening proxies. Formula AP@12 is only 0.10 while family-prior AP@12 is 1.0; post-split formula AP is 0.5947 vs family-prior 0.9821. Validation errors 0; explicitly not a material-discovery, solved-mechanism, complete-database, or computed-observable claim. |
| T-B6-003 | B6/B5 | open | unassigned | Builder/Baseline Adversary | Replace formula-derived proxies with crystallographic/DFT/B5-computed structural and electronic observables, then expand the post-2008 negative set so family priors and random baselines cannot saturate the audit. |
| T-B7-001 | B1/B7 | merged | codex | Integrator | B7 min-STV regime classifier after U3 phase-factored B1 pass. |
| T-B7-002 | B7 | merged | codex | Integrator | Replace fixed rotation T-cost proxy with an FT synthesis ledger for the `sat_n11` min-STV regime. |
| T-B7-003 | B1/B7 | merged | codex | Builder | Quantify the new FT-ledger min-STV boundary: `gcm_h6` at 1.086008x under throughput-heavy factories. |
| T-B7-004 | B7 | merged | codex | Builder | Build a precision-aware arbitrary-rotation ledger for `gcm_h6`; explicit synthesis-error budgets do not clear 1.20x and imply arbitrary T cost above fixed 20. |
| T-B7-005 | B1/B7 | merged | codex | Builder | Conservative same-axis local merge/cancel pass for `gcm_h6`; Aer 1/1 passed, but arbitrary rotations remain 270 -> 270 and T ledger remains 6224 -> 6224. |
| T-B7-006 | B1/B7 | merged | codex | Builder | Shared-synthesis/cache boundary for `gcm_h6`: 270 occurrences compress to 26 classical templates, but FT T ledger remains occurrence-based at 6760 -> 6224 with 0 cache reduction. |
| T-B7-007 | B1/B7 | merged | codex | Builder | Nonlocal repeated-block scan for `gcm_h6`: 2633 template certificates, best 8-op template covers 100 arbitrary occurrences, but no adjacent inverse/duplicate block and 0 T-ledger removal. |
| T-B7-008 | B1/B7 | merged | codex | Builder | Same-skeleton exact small-block synthesis for `w8_21`: 55 fixed-angle attempts, 16 seeds each, 0 passing candidates; best `a=pi/2` residual 3.936e-02 and local rank 5. |
| T-B7-009 | B1/B7 | merged | codex | Builder | Broaden beyond the same two-CNOT skeleton for `w8_21`: same-skeleton, 15360/15360 two-CNOT/four-Rz/Ry, 500/500 two-CNOT Euler-local, and 1480/1480 three-CNOT target-informed searches all found 0 exact four-arbitrary candidates; scoped minimality note and claim-boundary paper fragment are emitted, so no `w8_21` resource reduction may be counted without a future occurrence-removing certificate. |
| T-B7-010 | B1/B7 | open | unassigned | Theorist/Builder | Either produce a symbolic KAK/Clifford-scaffold proof for `w8_21`, or find a different occurrence-removing rewrite for `gcm_h6`; do not expand local `w8_21` numerical searches without a new symbolic scaffold. |
| T-B8-001 | B8 | merged | codex | Verification Agent | Adaptive spoofer suite for the B4/B8 circuit-level refresh task: 4 spoofer families across leakage fractions and refresh modes; high-leakage no-refresh risk reproduced, refresh/rotation repairs pass <=5% soundness in the proxy model. |
| T-B8-002 | B8/B10 | merged | codex | Verification Agent/Theorist | Trained/generative spoofer refresh stress: 144 configs, max learned soundness 1.0; no-refresh high leakage unsafe, projection_rotation/challenge_refresh/refresh_plus_rotation safe in this proxy. Boundary only, not a soundness proof. |
| T-B9-001 | B9/B10 | merged | codex | Theorist | Failed gap-amplification negative lemma: finite-instance B9 v0 screen now records one reusable negative lemma, 4 strict width-trap counterexamples, 9 dense locality traps, 5 proof obligations, and explicit non-claim of Quantum PCP proof or global gap-amplification impossibility. |
| T-B9-002 | B9/B10 | merged | codex | Theorist/Builder | Symbolic/proof-assistant skeleton: Lean-style file with 5 symbolic definitions, 3 theorem skeletons, 5 carried proof obligations, inherited 4 strict counterexamples and 9 dense locality traps; explicitly not proof-assistant checked, not a formal theorem, not Quantum PCP proof, and not global impossibility. |
| T-B9-003 | B9/B10 | merged | codex | Theorist/Builder | Named-family width/locality bound skeleton: `cluster_stabilizer_open_uniform_reweight` rows n=4,5,6 show all terms uniformly scaled by 1.35, max locality preserved at 3, raw gap amplifies, normalized gap is invariant, and the certificate is rejected; proof-check attempted but current `lean` command is not a usable Lean/mathlib checker. |
| T-B9-004 | B9/B10 | open | unassigned | Theorist/Builder | Create a real Lean/mathlib project or other proof-checkable environment for the open-boundary cluster-stabilizer family, then formalize support-size, uniform-scaling, spectral-width, and normalized-gap invariance lemmas for all n >= 4. |
| T-B10-001 | B10 | merged | codex | Theorist | B3/B5 denominator boundary comparison for B10-T1: 4 route cards; B3 one-parameter UCC/ADAPT + QWC stays negative-boundary with 0 selected-CI larger-basis denominator wins and max optimizer-loop shots lower bound 475,043,013,690,000; B5 has non-oracle and seeded-MPS classical pressure but variational MPS/ALS has 0 rows beating seeded pressure. No BQP separation or quantum advantage claim. |
| T-B10-002 | B10/B8 | merged | codex | Theorist | B10-T2 refresh proof-obligation gate: rejects no-refresh high-leakage soundness claims in the current proxy, records projection/challenge refresh as admissible next-proof conditions, and explicitly shows the proxy cannot support a general soundness lemma yet. |
| T-B10-003 | B10/B8 | merged | codex | Theorist | Restricted B10-T2 refresh-independence soundness lemma: under a declared bounded-leakage model with at least one refreshed predicate unknown and independent, Hoeffding gives single-unknown-mask soundness <= 8.94e-44 for current proxy parameters; explicitly not hardware verifier, sampling hardness, cryptographic soundness, or BQP separation. |
| T-B10-004 | B10/B8 | merged | codex | Theorist/Verification Agent | Transcript leakage simulator: 192 configs, honest completeness 1.0, no-refresh unsafe, refreshed high leakage modes retain >=6 unknown independent predicates, max refreshed high-leakage soundness 0.025; not hardware verifier/sampling hardness/BQP separation. |
| T-B10-005 | B10/B8 | merged | codex | Theorist/Verification Agent | Device-noise transcript bridge: 480 configs, 5 noise profiles, bounded bridge profiles preserve honest completeness 1.0; challenge_refresh/refresh_plus_rotation high-leakage max soundness 0.0208 with >=7 unknown independent predicates; projection_rotation is margin-sensitive; calibration_side_channel rejected; not hardware execution/sampling hardness/BQP separation. |
| T-B10-006 | B10/B8 | merged | codex | Theorist/Verification Agent | Qiskit/Aer circuit-level verifier bridge: 216 randomized parity-verifier circuits, max 30 qubits including ancillas, 0 Aer semantic mismatches, honest completeness 1.0; inherits device-noise bridge soundness 0.0208 for challenge_refresh/refresh_plus_rotation; not hardware execution/sampling hardness/BQP separation. |
| T-B10-007 | B10/B8 | merged | codex | Verification Agent/Builder | Noisy Aer circuit-level verifier bridge: 9600 randomized parity-verifier circuits from the 12-qubit task, honest plus 4 circuit-level adversary input families, 5 noise profiles, safe refresh modes challenge_refresh/refresh_plus_rotation; bridge-safe noisy honest acceptance 1.0, adversary acceptance 0.0, max honest predicate-bit error 0.1125; calibration_side_channel rejected; not calibrated backend/hardware execution/sampling hardness/BQP separation. |
| T-B10-008 | B10/B8 | merged | codex | Verification Agent/Builder | Backend-calibrated-style verifier bridge: 5760 randomized parity-verifier circuits using Qiskit GenericBackendV2 target InstructionProperties for per-qubit/per-edge Aer noise; safe calibrated honest acceptance 1.0, adversary acceptance 0.25, max honest predicate-bit error 0.0703125; no-refresh remains unsafe; not real backend properties, hardware execution, sampling hardness, or BQP separation. |
| T-B10-009 | B10/B8 | open | unassigned | Verification Agent/Builder | Replace GenericBackendV2 calibration snapshots with real backend properties or run hardware randomized-measurement verifier execution for B10-T2. |
| T-B10-010 | B10/B3/B5 | merged | codex | Theorist/Baseline Adversary | Missing-assumption theorem note: 2 theorem skeletons, 5 missing assumptions, and 5 proof obligations derived from the B3/B5 denominator comparison. It supports a finite negative-boundary claim policy, but explicitly does not prove a dequantization theorem, sampling-access theorem, BQP separation, or quantum advantage. |
| T-B10-011 | B10/B3/B5 | merged | codex | Theorist/Baseline Adversary | Asymptotic access-contract note: 2 family contracts, 8 explicit/oracle/sampling/quantum access rows, and 5 bridge conditions. The current portfolio refutes the sampling-access bridge for present B3/B5 evidence, while explicitly not proving a general dequantization theorem, sampling-access theorem, BQP separation, or quantum advantage. |
| T-B10-012 | B10/B5 | open | unassigned | Theorist/Baseline Adversary | Pick the B5 Hubbard response family from T-B10-011 and either build a comparable sampling/query oracle with variance and preparation costs, or formalize why production DMRG/MPS remains the stronger same-access denominator. |
| T-AUDIT-001 | all | open | unassigned | Audit Agent | CI-style audit script and status-page refresh command. |

## Task Template

```text
Task ID:
Track:
Owner:
Role:
Status:
Goal:
Files expected:
Commands expected:
Claim boundary:
Reviewers needed:
```

## Current Suggested Agent Swarm

| Agent | First assignment |
|---|---|
| compiler-agent | T-B1-004 |
| ft-ledger-agent | T-B7-010 |
| qec-agent | T-B2-005 |
| chemistry-agent | T-B3-012 only if a rescue mechanism is proposed; otherwise support B5/B10 |
| chemistry-baseline-agent | T-B3-002 |
| verification-agent | T-B4-002 |
| correlated-matter-agent | T-B5-003 |
| materials-agent | T-B6-003 |
| theory-agent | T-B9-004, T-B10-009, T-B10-012 |
| audit-agent | T-AUDIT-001 |

## Sprint 001 Work Packages

Detailed hypotheses, expected files, acceptance gates, and failure-value rules
are in `../b1_b10_solution_sprint_001.md`.

## Claiming A Task

Change `Status` to `claimed`, fill `Owner`, and create a work packet or branch:

```text
agent/<agent-id>/<task-id>/<short-name>
```

The owner must update this board when the PR enters review or is blocked.
