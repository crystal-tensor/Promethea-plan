# Prometheus-plan

**An AI Multi-Agent Research Program for Quantum Computing's Hardest Frontiers**

Broader open-source mission: challenge the world's hardest 100 problems through
AI multi-agent research, with a 2-3 year concentrated push on the Top 10
technical frontier tracks.

[Repository target](https://github.com/crystal-tensor/Prometheus-plan)

---

## Mission

Prometheus-plan is an open-source, AI multi-agent research program built to
challenge the world's hardest long-horizon scientific and technical problems.

The project starts from a living, open map of **100 hard problems**. Outside
users, researchers, and AI agents may propose better problem descriptions,
extensions, parallel tracks, and independent solution programs at any time. The
core Prometheus-plan maintainer effort currently concentrates on the **Top 10
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

Prometheus-plan is not a normal notes repository. It is a research operating
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

The latest B1/B7 evidence adds a source-bound local KAK invariant packet for
the repeated `w8_21` block. An analytic, global-phase-projected derivative
witness records local rank 5 and a largest 5-by-5 minor determinant of
`0.023711677101274878`; the magic-basis invariant eigenphases are numerically
`[-pi/3, -pi/3, pi/3, pi/3]`. This makes the next symbolic route concrete, but
it is not a symbolic KAK theorem, a global two-CNOT lower bound, an
occurrence-removing rewrite, a resource reduction, or B7 credit.

The newest B1/B7 artifact upgrades that pointwise observation into a family-level
controlled-unitary invariant closure for the fixed `w8_21` two-CNOT skeleton.
In the control-target basis, the relative block has the explicit form
`W = U0^dagger U1` with `tau = trace(W)/2 = -cos(b)cos(c)`, independent of the
`d` and `e` dressing angles. The magic-basis matrix satisfies the candidate
quadratic identity `m^2 - 2*tau*m + I = 0` and characteristic polynomial
`(lambda^2 - 2*tau*lambda + 1)^2`. The source point has `tau=0.5000000000000002`;
65 deterministic family points pass with maximum closed-form residual
`8.875e-16` and characteristic-coefficient residual `6.673e-15`. This is a
family-level invariant and a route to local-dressing synthesis, not yet an
occurrence-removing rewrite, fewer arbitrary rotations, a global lower bound,
or B7 credit.

The follow-up B1/B7 artifact now gives an explicit constructive normal form for
the same fixed `w8_21` skeleton:
`U = (I tensor Ry(e) Rz(d)) CX (I tensor Ry(-c) Rz(b+pi)) CX (I tensor Rz(a))`.
The source residual is `4.074e-16`; 65 deterministic family points pass with
maximum constructive residual `5.895e-16` and controlled-relative residual
`8.243e-16`. The factorization preserves 2 CNOTs and all 5 arbitrary
parameters. It is a reusable synthesis scaffold, but it does not remove an
occurrence, lower arbitrary-rotation count, reduce proxy-T cost, or add B7
credit.

The next B1/B7 gate replays the constructive normal form in the real `gcm_h6`
source context. The upstream scan records 20 raw `w8_21` occurrences and
selects 16 non-overlapping spans; all 16 context replays pass with maximum
residual `1.63e-16`. Seven occurrences are followed by a target-local `Rz`,
but the normal form ends in `Ry(e)`, so the direct `Rz` merge count remains 0.
The exact rewrite still preserves 2 CNOTs and 5 arbitrary parameters; accepted
occurrence removal, proxy-T reduction, and B7 credit remain 0. This is a
real-circuit context boundary, not a full-circuit rewrite or a B7 solution.

The newest B1/B7 step turns the fixed-skeleton invariant into a machine-checked
symbolic certificate. SymPy proves the control-target block form, the closed
relative block, `tau=-cos(b)cos(c)`, unitarity, independence from `d/e`, and the
exact quadratic identity `W^2-2*tau*W+I=0`; all 6 exact checks pass. The
priority, provenance, replay-validation, and acceptance gates each pass 9/9,
and the accepted certificate is then retested against the resource ledger. The
result is precise but not a compression win: CNOTs remain `2 -> 2`, arbitrary
parameters remain `5 -> 5`, occurrence removal is 0, proxy-T reduction is 0,
and B7 credit remains 0.

The next B1/B7 experiment tests the larger-neighborhood transfer route rather
than only observing the boundary. Seven selected `w8_21` occurrences are
immediately followed by the same-target arbitrary `Rz(0.28861107553559073)`.
Refitting each complete context into the same two-CNOT, five-parameter normal
form with 12 deterministic seeds finds 0/7 exact fits; the best residual is
`0.2301426459717444` at a `1e-10` acceptance threshold. The external rotation
therefore cannot be removed by this bounded same-skeleton route. Occurrence
removal, proxy-T reduction, and B7 credit remain 0; the next route is a
commutation-aware scaffold that explicitly carries and prices the external
rotation.

The carrier-pricing control keeps that external `Rz` explicit. All 7 real
contexts replay exactly with a sixth local parameter, and the identity
`Rz_target(theta) CX = CX (CX Rz_target(theta) CX)` passes for all 7 rows. The
explicit carrier preserves 2 CNOTs and 6 arbitrary parameters, so it produces
zero savings; commuting the carrier through a CX boundary in the declared
construction costs 4 CNOTs and still 6 arbitrary parameters. This is a
carrier-aware semantic control, not a global necessity theorem or B7 credit.

The latest B1/B7 control searches a different route: it relocates the five
arbitrary angles across the local Euler slots while retaining two CX gates and
the exact `mid:q1:rz1=pi` scaffold. The exact source placement is excluded;
243 relocated families are tested against the seven source-bound external-Rz
contexts with 3,402 deterministic optimizer runs. No exact five-angle context
replay is found; the best residual is `0.03046391998887225`. This closes only
the declared relocated-Euler family. It does not prove that six parameters are
globally necessary, and occurrence removal, proxy-T reduction, and B7 credit
remain 0. The next high-value route is symbolic invariant analysis or a
genuinely different Clifford scaffold.

The next B1/B7 artifact converts that numerical boundary into a scoped exact
phase-ratio obstruction. For the same relative-block parameter branch, the
post-context left dressing is `Rz(theta) Ry(e) Rz(d)`, while the retained
five-parameter form offers only `Ry(ep) Rz(dp)`. With generic source `e`, the
off-diagonal and diagonal phase ratios force `exp(2*i*theta)=1`, or
`theta=0 mod pi` for real angles. The seven source-bound contexts all have
generic dressing and sit at distance `0.5692420427088251` from that condition;
same-branch absorption is therefore allowed in `0/7` rows. This is an exact
same-branch obstruction, not a global six-parameter lower bound, alternate
Clifford-frame theorem, full-circuit rewrite, or B7 credit.

The follow-up B1/B7 branch-closure artifact enumerates the four representative
discrete relative-block branches generated by `c'=s*c+k*pi`. They induce the
local factors `I`, `Ry(pi)`, `Rz(-pi)`, and `iX`; all 12 exact branch checks
pass, including equality of the closed relative block. Every one of the 28
source-bound context/branch pairs retains the phase-ratio product
`exp(2*i*theta)`, so the absorbing-pair count is `0/28`. This closes the finite
discrete branch set only. Continuous alternate Clifford scaffolds, global KAK
minimality, full-circuit rewrites, and B7 credit remain open.

The newest B1/B7 experiment tests a continuous escape around that boundary: one
fixed control-side `+/- pi/2` Clifford frame is inserted at every local layer
and Euler axis, with both signs and all four CX direction sequences. The search
keeps two CX gates and five arbitrary target angles, covering 72 families across
each of seven real source-bound contexts and 1,008 deterministic optimizer runs.
Exact replays are `0/7`; the best residual is `0.7886609149859014`. This closes
only the declared bounded control-side frame family, not a global KAK lower
bound, exhaustive Clifford-word search, or full-circuit rewrite. Occurrence
removal, proxy-T reduction, and B7 credit remain 0. The next route is a longer
fixed Clifford word or a genuinely different nonlocal skeleton with exact
arbitrary-input replay and resource pricing.

The next B1/B7 experiment lengthens that local word without changing its
nonlocal or arbitrary-parameter budget. It inserts two fixed control-side
`+/- pi/2` frames in two distinct local layers, exhausts all layer pairs,
axes, signs, and CX direction sequences, and tests 432 families per context.
Across seven source-bound contexts, 6,048 deterministic optimizer runs produce
zero exact five-angle replays; the best residual is `0.2301426459717444`.
The best word is a pair of opposite `Rz` frames, so it degenerates to the
already-known same-skeleton boundary rather than creating a new absorption
mechanism. This closes only the declared two-frame family, not a global KAK
lower bound, an exhaustive Clifford-word search, or a full-circuit rewrite.
Occurrence removal, proxy-T reduction, and B7 credit remain 0.

The next B1/B7 experiment changes the nonlocal word itself: three CX gates are
allowed while five arbitrary angles are placed on target-side Euler slots, with
the source `Rz(pi)` scaffold fixed. The bounded family retains at least four of
the five source target-side slots and exhausts all eight CX direction sequences,
giving 248 families per context. Across seven source-bound contexts, 3,472
deterministic optimizer runs produce exact replays `0/7`; the best residual is
`1.5310915690771965`. The experiment therefore does not show that one extra CX
can replace the sixth arbitrary angle in this family. It spends one additional
CX for a potential one-angle saving, but no rewrite, occurrence removal,
proxy-T reduction, or B7 credit is accepted. This closes only the declared
target-side family, not a global three-CX lower bound or a solved B1/B7 frontier.

The follow-up B1/B7 mixed-support search moves one arbitrary angle across the
local support boundary: four source target-side angles are retained, while
the fifth is placed on each of 18 other local Euler slots. Three CX gates and
all eight CX direction sequences are retained, giving 720 families per
context. Across seven source-bound contexts, 10,080 deterministic optimizer
runs produce exact replays `0/7`; the best residual is `1.033550478227691`.
The best family consistently returns to `pre:q0:rz0` plus four target-side
slots, but still fails exact replay. No rewrite, occurrence removal,
proxy-T reduction, or B7 credit is accepted; this closes only the declared
mixed-support family, not a global three-CX lower bound.

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
The latest B5/B10 production implementation triage gate now splits that failed
contract into six PR-sized work packets: two immediate guardrail packets
(`W4` row-contract preservation and `W6` claim-safety/audit wiring) and four
blocked implementation/theory packets (`W1` production DMRG/MPS denominator,
`W2` seeded-pressure replacement audit, `W3` same-access response-oracle cost
ledger, and `W5` B10-T1 theorem-boundary integration). It satisfies 6/6
triage readiness conditions while keeping production DMRG, sampling oracle,
same-access positive route, catalog change, quantum advantage, and BQP
separation all false.
The W4 row-contract harness is now executed as a machine-checkable guardrail:
it preserves the same 9 D5 Hubbard response rows across 10 B5/B10 source
artifacts, records row-contract hash
`7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc`,
passes 10/10 source checks and 6/6 conditions, and leaves `W1`/`W2`/`W3` as
the only positive-route implementation packets. It is not a new denominator,
not production DMRG, not a response oracle, and not a quantum advantage claim.
The W2 seeded-pressure replacement audit is now also executed. It replays three
candidate replacement families under the locked row contract and finds
0 deployable replacements for the exact-state-seeded MPS pressure reference.
The seeded mean relative response error is `0.0004416259745141553`; the best
replacement-by-mean is `variational_mps_als` at `0.01805548365563228`, with
0 rows beating seeded pressure. The largest row-level win count across all
candidate families is only 2/9, so the seeded-pressure blocker remains explicit
and W2 is closed as a current positive-route packet.
The W3 same-access response-oracle cost ledger is now executed as well. It
checks 8 oracle requirements under the same row contract: 3 pass and 5 fail
(`O3` state preparation, `O4` mixing/query cost, `O5` readout/noise cost,
`O6` optimizer-loop cost, and `O7` denominator win). The measurement-confidence
ledger exists, but no response oracle is constructed, 0 rows beat explicit D5
matvec pressure for the seeded target, and the remaining positive-route packet
is now `W1` production DMRG/MPS.
The W1 production DMRG/MPS acceptance gate is now executed. It checks 10
production-denominator requirements under the locked row contract: 3 pass and
7 fail (`D3` non-exact-state-seeded production denominator, `D4` stored
canonical environments and orthonormal residuals, `D5` full-row convergence
ledgers, `D6` seeded-pressure replacement, `D7` same-access cost ledger, `D8`
B10 positive-route readiness, and `D9` prototype-over-seeded pressure). The
gate preserves all 9 rows and 9 environment-ledger rows, but confirms that W1
is still blocked on the denominator engine itself.
The first W1 denominator-engine ledger is now also executed. It checks 8
denominator-engine requirements under the same row-contract hash: 4 pass and
4 fail (`E4` production canonical environments/residuals, `E5` all-row
convergence, `E6` seeded-pressure replacement, and `E7` same-access production
cost ledger). The ledger preserves all 9 rows and 216 sweep-ledger rows, but
has 0 convergence-passed rows and 0 rows beating seeded pressure. The selected
candidate family remains `variational_mps_als`, with mean candidate relative
response error `0.01805548365563228` versus seeded pressure
`0.0004416259745141553`. This is useful negative evidence and a runnable
denominator-engine shell, not production DMRG, not a deployable tensor solver,
not a same-access positive route, and not a quantum advantage claim.
The W1 canonical residual blocker gate now decomposes the next production
solver obligations. It checks 8 requirements: 4 pass and 4 fail (`C3` stored
canonical environments, `C4` orthonormal residual ledgers, `C5` all-row
convergence evidence, and `C7` same-access production cost ledger). The gate
records 0 environment rows, 0 residual rows, 0 convergence-passed rows, and 4
PR packets: `W1-E4-env-residuals`, `W1-E5-convergence`,
`W1-E6-seeded-pressure`, and `W1-E7-cost-ledger`. This is a useful handoff
contract for future agents, not production DMRG and not a positive route.
The W1 implementation contract gate now makes that handoff stricter. It
declares the row-level artifact schema for any future production DMRG/MPS PR:
17 required row keys, the locked 9-row contract hash, and four implementation
packets covering environments/residuals, convergence, seeded-pressure
comparison, and same-access production costs. The contract checks 10
requirements: 5 pass and 5 fail (`K5`-`K9`). There are still 0 environment
rows, 0 orthonormal-residual rows, 0 discarded-weight rows, 0 convergence
rows, 0 rows beating seeded pressure, and no complete same-access cost ledger.
This is still not production DMRG, not a same-access positive route, not a
BQP separation, and not a quantum advantage claim.
The W1 prototype environment scout now maps reusable smoke-gate evidence
without promoting it into a production claim. It checks 8 requirements: 5 pass
and 3 fail (`P5`-`P7`). The older two-site smoke gate contributes 9 prototype
environment-ledger rows, 9 prototype trace hashes, and 9 discarded-weight
metrics under the locked B5/B10 row contract. However, accepted canonical
left/right environment hashes, orthonormal residual rows, production
discarded-weight rows, and production contract rows all remain 0. The next W1
solver must turn those prototype traces into accepted 17-key production row
artifacts before any K5/K6 progress, production DMRG claim, or positive
B10-T1 route can be counted.
`T-B5-006l` / `T-B10-014j` now adds a W1 production-row intake template
gate. It consumes the implementation contract and prototype scout, then emits
9 locked row templates under the same row-contract hash. The gate checks 8
requirements: 5 pass and 3 fail (`I5`-`I7`). It carries all 9 prototype trace
hashes as provenance, keeps the 17-key row schema, pre-fills 9 stable keys per
row, and exposes 8 production-required keys that still must be submitted:
canonical center site, left/right environment hashes, orthonormal residual
norm, discarded weight, wall-clock time, peak memory, and sweep/matvec count.
Submitted production rows and accepted production rows remain 0, so this is a
PR intake template, not production DMRG, not a deployable denominator, not a
same-access positive route, not quantum advantage, and not BQP separation.
`T-B5-006m` / `T-B10-014k` now turns that intake surface into an agent-ready
blocker queue. It consumes the 9 templates and the W1 implementation contract,
checks 9 queue requirements, passes 6, and fails only `Q6`-`Q8` because no
production row has been submitted or accepted yet. The gate partitions all 72
missing production fields into three PR-sized packets: `W1-E4-env-residuals`
with 36 missing fields, `W1-E5-convergence` with 9 missing fields, and
`W1-E7-cost-ledger` with 27 missing fields. The queue is useful because it
tells solver, baseline, and cost-ledger agents exactly which row artifacts to
submit first while preserving the locked row-contract hash. It is still not
production DMRG, not a seeded-pressure win, not a same-access positive route,
not quantum advantage, and not BQP separation.
The latest B10-T1 stress test still finds no positive same-access route because
0 rows beat explicit D5 matvec-equivalent costs by shots. This is progress, but
it is not a production DMRG result, not a deployable tensor solver, not a
sampling oracle, and not a quantum advantage claim.

B3/B10 now has a same-access negative boundary note for the chemistry route.
It consumes the failed measurement-rescue gate and records 9/9 satisfied
negative-boundary conditions. The source rescue gate still passes 5/10 and
fails M5-M9: full cross-molecule compiled-state covariance, multi-parameter or
converged chemistry ansatz evidence, selected-CI/FCI denominator wins,
optimizer-loop shots below the positive-route stress ceiling, and B10 access
contract acceptance. Current B3 evidence still has 0 denominator wins, max
optimizer-loop shots lower bound 475,043,013,690,000, max optimizer-loop
two-qubit executions lower bound 281,225,464,104,480,000, and B3 remains
demoted. This is not a reaction dynamics solution, not quantum advantage, and
not a BQP separation.

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

B4/B8 now has the first verifier-private predicate pressure gate on top of
that support-spoofer boundary. The gate adds four late-bound private predicate
bits to the same 36 pilot circuits and 4 spoofer families. In the no-leakage
analytic model, public support-only acceptance falls from 1.0 to 0.0625, a
16x guessing burden. The leakage boundary remains explicit: leaking one private
predicate bit raises acceptance to 0.125, and full predicate leakage returns
acceptance to 1.0. This is useful protocol pressure, not hardware execution,
not cryptographic or protocol soundness, not sampling hardness, not quantum
advantage, and not a BQP separation claim.

B6 has moved from a synthetic descriptor toy to curated leakage audits,
structural/electronic proxy boundaries, and a crystallographic reproducibility
gate. The latest gate audits an existing crystallographic descriptor result
with 56 records, 28 families, and 18 negative controls. It passes 6/11 checks
and fails R6-R10: the current runtime lacks `pymatgen`, source validation
errors remain 2, post-split crystallographic AP is 0.2476 versus family-prior
AP 0.4901, and there are still no DFT or B5-computed observables. This is not a
material-discovery, solved-mechanism, DFT-observable, B5-observable, or
solution claim.

`T-B6-005` converts those failed crystallographic-readiness checks into a
reproducible evidence contract. The contract checks 8 requirements: 3 pass and
5 fail. Failed gates `K4`-`K8` map directly to five PR packets: reproducible
crystallographic backend, source-validation cleanup, post-split family-prior
denominator defeat, DFT observable channel, and B5-computed observable channel.
This is still not a material-discovery, mechanism, complete-database, DFT,
B5-observable, or solution claim.

`T-B6-005b` adds a crystallographic packet scout over that contract. The scout
checks 8 requirements: 3 pass and 5 fail (`S4`-`S8`). It maps 5 packets while
preserving the 56-record / 28-family / 18-negative-control scope, 27
post-split records, crystallographic AP 0.247619 versus family-prior AP
0.490136, 2 source-validation errors, no pinned backend, 0 DFT observable rows,
and 0 B5-computed observable rows. The result is a sharper intake map for
materials and B5 agents, not a material-discovery, mechanism, DFT-observable,
B5-observable, reproducible-descriptor, or solution claim.

`T-B6-005c` adds a validation-rescue scout over the same 56-record table. A
predeclared `physics_risk_adjusted_v0` score keeps 2 negative controls in
top-k and reaches post-split AP 1.0 versus family-prior AP 0.490136, so the
source-validation symptoms have a plausible engineering route. The gate still
fails `V6`-`V8` because there is no pinned crystallographic backend, no DFT
observable channel, and no B5-computed observable channel. The source screen is
not rewritten, and no material-discovery, mechanism, DFT/B5-observable, or
solution claim is made.

`T-B6-005d` adds a backend replay scout for that rescue. The repo-local replay
recomputes `physics_risk_adjusted_v0` from the existing table, pins the source
table, formula, and replay hashes, and reproduces post-split AP 1.0 with 2
negative controls in top-k. The gate now passes 6/8 and fails only `R7`-`R8`:
DFT observable rows and B5-computed observable rows remain 0. This is a
deterministic replay artifact, not an external crystallographic backend, source
rewrite, material-discovery, mechanism, DFT/B5-observable, or solution claim.

`T-B6-005e` adds an observable contract gate over the backend replay. It
declares 5 observable packets, an 11-key DFT row schema, an 11-key B5 row
schema, and hash-preservation requirements for the source table, replay formula,
and replay table. The gate passes 4/6 and fails `O5`-`O6` because DFT rows and
B5 rows are still 0. This is a contract for future observable PRs, not
observable evidence or a candidate-ranking promotion.

B2 has moved past the earlier reduced-round artifact into a leakage-flagged
erasure analytic boundary: 480 configurations, 42 proxy target-volume improved
rows, 33 distance-5/7 improved rows, no reduced rounds, and no new-code,
threshold, device, or circuit-level decoder claim.

B2 now also has a Stim HERALDED_ERASE / DEPOLARIZE1 stress boundary, a
false-positive overhead stress, a posterior-calibrated shot-conditioned leakage
boundary, a posterior-weighted decoder-risk ledger, a decoder-input contract
feasibility gate, a per-shot decoder trace packet, a posterior-likelihood
injection gate, a DEM-informed detector-to-edge semantics gate, and a
hardware-like leakage observation model gate, a calibration-transfer guardrail,
a calibrated-evidence contract gate, and now a calibrated trace scout. The
latest B2 scout consumes the contract, guardrail, per-shot trace packet, and
hardware-like leakage profiles. It checks 8 scout requirements: 5 pass and 3
fail (`S5`, `S6`, `S7`). The scout preserves 576 synthetic traces, 3 challenge
trace hashes, 482 synthetic flag events, 9 hardware-like profile results, and
864 holdout profile-shots, but still has 0 calibrated flag observation rows, 0
real hardware trace rows, and 0 strict holdout improvement rows. The best
conservative hardware-like profile remains 16 holdout baseline failures, 16
holdout injected failures, and holdout failure delta 0. Calibration transfer,
production decoder readiness, threshold support, calibrated trace readiness,
hardware support, quantum advantage, and new-code support all remain false.
This is a sharper handoff artifact, not a circuit-level decoder, production
decoder, threshold, hardware result, quantum-advantage result, or new-code
claim.

B9 now has a local parametric certificate checker plus a proof-environment
contract gate, proof-project scaffold, and CI handoff for the
`cluster_stabilizer_open_uniform_reweight` family. The local checker verifies
the n >= 4 formula-level term count, support set {2,3}, max locality 3, exact
uniform scale 27/20, finite rows n=4,5,6, and normalized-gap invariance with a
repo-local exact-rational verifier. T-B9-004m repairs the Lean source interface,
builds the pinned Lean 4.12.0/Mathlib environment, and records a source-backed
transcript for `lean --version`, `lake --version`, and
`lake env lean B9/ClusterStabilizer/WidthLocality.lean`, all with returncode 0.
The acquisition gate now passes 7/7 requirements and the priority transcript
packet passes 9/9 requirements.

This is a checked indexed theorem interface, not a formal all-n Hamiltonian
theorem: the open-boundary construction, support-size proof over all n, and
unconditional spectral-scaling lemmas still need to be formalized. It is not a
Quantum PCP proof, not an NLTS theorem, and not a global gap-amplification
no-go theorem.

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
independent-baseline scaffold then separates cache labels from accepted
occurrence-ledger savings and confirms zero double-counted occurrences and zero
double-counted proxy-T pressure. The cost-model scaffold has moved from 0/8 to
6/8 acceptance gates by passing CM-02 object existence, CM-03 replay, CM-04
logical layout/routing, CM-05 factory amortization, CM-06 shared-error
budgeting, and CM-07 independent accounting baseline. The model is still not
accepted: the refreshed-B7-ledger gate has now been attempted and explicitly
rejects theta sharing under the current evidence because there are no 30
occurrence-removing certificates, no accepted physical device layout, no physical
factory schedule, no device-calibrated physical validation, no accepted proxy-T
reduction, and no `gcm_h6` min-row improvement. The counted B7 ledger reduction
remains 0.

B1/B7 has now returned from the rejected CM-08 cost-model route to a CM-01
structural obligation gate for `cone_01`. A local-equivalence invariant
diagnostic uses a magic-basis, determinant-normalized trace fingerprint over
all 35 candidate windows. The result is useful but still incomplete: 24 windows
show nonzero local-equivalence invariant sensitivity to `RY(theta)`, and those
same 24 mismatch the nearest pi/4-grid invariant; 11 windows remain
invariant-flat under this diagnostic. This blocks a local-only absorption
interpretation for 24 windows, but it does not clear the B7 requirement of 30
certified windows. There is still no KAK theorem, no occurrence-removing
rewrite certificate, no semantic certificate, no accepted physical cost model,
and no B7 resource-saving claim.

B1/B7 has now pushed that `cone_01` carrier route through blocker-stack,
motif, CNOT-parity, interleaving-commutation, and semantic-replay-packet gates.
The cheap routes are rejected: the current blocked source-aligned candidates
have 11 repeated same-edge blocker pairs, 0 clean adjacent CNOT cancellations,
18 interleaving single-qubit operations, 4 target-side phase obstructions, and
7 non-diagonal interleaving obstructions. The latest packet gate is constructive
but still not a solution: it turns the 3 blocked carrier CNOT stacks into exact
bounded two-qubit replay targets with 4x4 matrix fingerprints, covering 32
window gates total, 14 CNOTs, 18 single-qubit gates, and 3 distinct semantic
fingerprints. No shorter replay, occurrence removal, proxy-T reduction, B7
ledger improvement, or solved-problem claim is made.

B1/B7 now also has a restricted packet-synthesis search over those exact
targets. It searches fixed-direction 0/1/2/3-CNOT scaffolds with arbitrary local
U3 layers and finds numerical exact reduced-CNOT candidates for all 3 packets:
candidate line 1378 reaches 1 CNOT from source 4, and candidate lines 1381 and
268 reach 2 CNOTs from source 5. The candidate CNOT reduction is 9 if a later
gate accepts the replacements. The current gate does not accept them yet:
full-circuit replay, symbolic/exact decomposition boundaries, local-layer
resource accounting, occurrence removal, proxy-T reduction, and B7 ledger
improvement all remain open.

The follow-up replay/resource gate now rejects that route as a B7 ledger
improvement under the current accounting rules. The 3 bounded packet targets
remain numerically replay-consistent, but the reduced-CNOT scaffolds replace 1
source off-pi/4 parameter with 40 replacement off-pi/4 local-U3 parameters,
adding 780 proxy-T pressure. Accepted full-circuit replay certificates,
occurrence removal, proxy-T reduction, and B7 ledger improvement remain 0.

The next local-U3 exactification gate now closes the cheapest repair attempt.
It snaps all 40 replacement off-pi/4 local-U3 parameters to the pi/4 grid and
replays the same three packet targets. The snapped packets have 0/3 exact
passes with residuals from 0.4757435265 to 0.7803612881, so cheap grid snapping
breaks the bounded replay instead of producing an accepted exact decomposition.
Accepted local-U3 exactification, absorption certificates, full-circuit replay,
occurrence removal, proxy-T reduction, and B7 ledger improvement remain 0.

The sparse local-U3 repair gate then tests the next-cheapest route: keep the
pi/4-snapped scaffold, but free only one or two local-U3 parameters. It searches
420 sparse repair candidates. One bounded packet, line 1378, is repaired by
changing one snapped grid choice; the other two packets remain unrepaired even
with two free parameters. This is partial packet evidence only. It is not a
full-circuit rewrite, not a symbolic decomposition, and not a B7 ledger saving.
Accepted occurrence removal, proxy-T reduction, and B7 improvement remain 0.

The three-parameter local-U3 repair continuation now exhaustively searches the
two unresolved packets from that gate. It checks 1,632 exactly-three-parameter
repairs and exactifies line 268, while line 1381 remains unrepaired with best
residual 0.049865177666770955. The portfolio now has 2/3 bounded packet
repairs, with candidate CNOT reduction 6 if those packets were later accepted.
They are not accepted yet: symbolic decomposition, full-circuit replay,
occurrence removal, proxy-T reduction, and B7 ledger improvement remain 0.

The four-parameter line-1381 pressure gate then exhaustively searches 3,060
exactly-four-parameter repairs for the last unresolved packet. It improves the
best residual from 0.049865177666770955 to 0.02997767950993884, but still finds
0 exact repairs. The reduced-CNOT packet route therefore remains at 2/3 bounded
packet repairs, and accepted occurrence removal, proxy-T reduction, and B7
ledger improvement remain 0. The next route must broaden the scaffold,
formalize a scoped obstruction for line 1381, or move to a different
ledger-reducing construction.

The five-parameter line-1381 exact-repair gate then searches the same
two-CNOT pi/4-snapped scaffold with exactly five freed local-U3 parameters and
finds a first exact packet repair after 5,795 of 8,568 deterministic
combinations. The best residual is 6.513934436930801e-13, so all three reduced
CNOT packets now have bounded packet-level repairs. This is real progress, but
it is still not an accepted B7 saving: the line-1381 repair carries five
off-grid local-U3 parameters, no symbolic full-circuit replay certificate has
been emitted, and accepted occurrence removal, proxy-T reduction, and B7 ledger
improvement remain 0.

The repaired-packet resource-boundary gate now consumes the three bounded
packet repairs together. It preserves the 3/3 packet-repair status and the
candidate 9-CNOT reduction signal, while reducing replacement off-grid local-U3
parameters from 40 to 5 and incremental proxy-T pressure from 780 to 80. That
is a meaningful narrowing of the resource blocker, but not a ledger win:
accepted full-circuit replay certificates, occurrence removal, proxy-T
reduction, and B7 improvement all remain 0. The next route must exact-decompose
or absorb the five remaining line-1381 off-grid local-U3 parameters and emit
symbolic full-circuit replay certificates before any B7 saving can be counted.

The line-1381 exact-decomposition pressure gate now tests those five remaining
off-grid local-U3 parameters against the simple acceptance contracts: pi/4
grid, low-denominator power-of-two pi grid, rational-pi grid up to denominator
512, and source-angle absorption. All five parameters remain unaccepted:
pi/4, dyadic-pi, rational-pi, source-absorption, symbolic decomposition,
full-circuit replay, occurrence removal, proxy-T reduction, and B7 ledger
improvement all stay at 0. This closes the cheap exact-decomposition route but
does not prove a global obstruction; the next route must use broader symbolic
synthesis, context-aware absorption, or full-circuit replay with honest
resource pricing.

The follow-up line-1381 context-absorption gate checks whether those same five
parameters can be absorbed by exact inventory matches or one-step same-support
context cancellation in the native optimized `gcm_h6` QASM. It reviews 2,049
rotation arguments overall and 44 same-support context rotation arguments
inside the configured +/-64-line neighborhood. The result is still negative:
0/5 parameters have exact or absolute-angle inventory matches, 0/5 have
same-support context matches, 0/5 exactly cancel back to the pi/4 grid, and B7
accepted occurrence/proxy-T reduction remains 0. This closes only a cheap
single-step context route; multi-rotation symbolic absorption and full-circuit
replay remain open.

The next line-1381 multi-rotation context gate broadens that pressure test to
signed sums of two or three same-support context rotations. Across the same 44
context rotation arguments, it evaluates 3,784 width-2 signed combinations and
105,952 width-3 signed combinations per parameter, or 548,680 total signed
combination tests across the five remaining parameters. The result remains
negative: 0/5 parameters have exact width-2 or width-3 absorption back to the
pi/4 grid, the best width-3 grid error is 1.5819911093339911e-3, and accepted
full-circuit replay, occurrence removal, proxy-T reduction, and B7 ledger
improvement remain 0. This closes a bounded two-/three-rotation context route;
four-or-more-rotation symbolic absorption, commutation-aware replay, and
different occurrence-removing scaffolds remain open.

The follow-on four-rotation context gate tests the next bounded rung before
leaving the local context path. For each of the same five line-1381 parameters,
it evaluates 2,172,016 signed width-4 combinations from the same 44 context
rotation arguments, or 10,860,080 total signed combination tests. The result is
again negative: 0/5 parameters have exact width-4 absorption back to the pi/4
grid, the best width-4 grid error remains 1.5819911093339911e-3, and accepted
full-circuit replay, occurrence removal, proxy-T reduction, and B7 ledger
improvement remain 0. This closes an exactly-four-rotation context route; a
future route must justify five-or-more symbolic absorption, commutation-aware
full-circuit replay, or a different occurrence-removing scaffold.

The next commutation-corridor gate moves from bounded angle arithmetic toward
replay pressure. It reviews the 10 best two-/three-/four-rotation context
candidates from T-B1-004ap/aq, covering 32 context references on 8 unique lines.
The cheap corridor model accepts 0 candidates: 7 references sit inside the
target packet, 13 references are not standalone RZ-like rotations, 21 references
have support-touching CNOT or non-diagonal single-qubit blockers, and 0 external
standalone-Z references have a clear path into line 1381. Accepted full-circuit
replay, occurrence removal, proxy-T reduction, and B7 ledger improvement remain
0. This does not prove a global obstruction, but it closes the cheap
commutation-corridor interpretation of the current bounded context hints.

The follow-on full-circuit replay obligation gate turns that boundary into a
reviewable checklist. T-B1-004as confirms that all 3 reduced-CNOT packets still
have bounded exact repairs, but 0/3 have symbolic exactness certificates,
full-circuit replay events, replacement QASM patches, occurrence-class lifts, or
B7 ledger acceptance. Two packets are resource-clean at bounded-packet level;
line 1381 still has one unpriced off-grid local-U3 burden after the failed exact
decomposition, bounded context, and cheap corridor routes. Accepted full-circuit
replay, occurrence removal, proxy-T reduction, and B7 ledger improvement remain
0. The next useful PR must create actual replay certificates or a different
occurrence-removing route, not another local diagnostic that cannot enter the
B7 ledger.

T-B1-004at now converts the replacement-QASM obligation into concrete bounded
OpenQASM 3 patch snippets. All 3 repaired reduced-CNOT packets have bounded
QASM3 snippets and all 3 pass the bounded exactness check, preserving the
candidate 9-CNOT reduction if a future full-circuit patch is accepted. The gate
still rejects B7 credit: the line-1378 and line-1381 source windows overlap on
lines 1369-1377, so the snippets are not a composable full-circuit patch set.
Accepted full-circuit patches, replay certificates, occurrence removal,
proxy-T reduction, and B7 ledger improvement remain 0. The next useful PR must
merge or resynthesize the overlapping patch region and then replay it against
the source circuit.

T-B1-004au now prevents double-counting that overlap. It enumerates
non-overlapping bounded patch subsets and selects line 268 plus the larger
line-1381 window, dropping line 1378 because it is contained in the line-1381
source window. The candidate CNOT signal is therefore 6 for the current
composable bounded subset, not the naive 9. No full-circuit QASM rewrite is
emitted yet because the source benchmark is still a legacy OpenQASM 2.0 fixture
while the bounded replacement snippets are OpenQASM 3 snippets. The project
route is OpenQASM 3-facing; no replay certificate, occurrence removal, proxy-T
reduction, or B7 improvement is accepted.

T-B1-004av now bridges that subset into a concrete legacy-dialect replay
candidate at
`results/B1_B7_cone01_qasm2_candidate_rewrite_gate/gcm_h6_line268_line1381_candidate.qasm`.
The candidate rewrites the line-268 and line-1381 windows and down-converts the
bounded OpenQASM 3 `U` snippets only to match the current legacy fixture parser,
lowering structural CNOT count from 795 to 789. This is the first
replay-consumable artifact for the branch and a stepping stone toward an
OpenQASM 3 exporter, but it is still not a full-circuit replay certificate, not
a recovered line-1378 merge, not a priced local-U3 resource result, and not a B7
ledger saving. Accepted full-circuit patch, replay, occurrence removal, proxy-T
reduction, and B7 improvement remain 0.

T-B1-004aw then runs the first full-statevector replay probe on that
legacy-dialect candidate. After removing final measurements, the source and candidate
19-qubit circuits have statevector dimension 524,288, state fidelity
0.9999999999999551, max global-phase-aligned amplitude delta
1.3908205762322243e-13, max probability delta 5.551115123125783e-16, and
measured q[4] marginal delta 5.551115123125783e-16. The probe passes for the
benchmark default input state, but it is still not a symbolic unitary proof for
arbitrary inputs and still does not accept B7 occurrence, proxy-T, or ledger
credit.

T-B1-004ax adds sampled-input replay pressure. It runs the same source and
candidate circuits on 8 deterministic input states: 6 computational-basis
preparations and 2 seeded product states. All 8 pass; min state fidelity is
0.9999999999999547, max global-phase-aligned amplitude delta is
1.392888964263601e-13, and max probability delta is
1.8214596497756474e-15. This is stronger than default-input replay, but it is
still sampled evidence, not symbolic arbitrary-input equivalence, and it still
does not accept B7 occurrence, proxy-T, or ledger credit.

T-B1-004ay adds phase-consistency and superposition replay pressure. It checks
the same source/candidate pair on 4 phase-anchor inputs and 4 superposition
inputs after final measurements are removed. All 8 pass; overlap phase spread
is 1.3722356584366935e-13 radians, min overlap magnitude is
0.9999999999999772, min state fidelity is 0.9999999999999547, and max
probability delta is 1.074140776324839e-14. This reduces the risk that
independent per-input global-phase alignment hides an input-dependent phase
mismatch, but it is still sampled evidence, not symbolic arbitrary-input
equivalence, and accepted B7 occurrence, proxy-T, and ledger credit remain 0.

T-B1-004az fixes one global phase from the zero-input replay and reuses that
same phase across a sampled subspace: 6 computational-basis anchors and 15
coherent pair superpositions. All 21 cases pass; max global-anchor phase delta
is 3.142993331217661e-14 radians, min overlap magnitude is
0.9999999999999772, min state fidelity is 0.9999999999999547, and max
probability delta is 1.074140776324839e-14. This is stronger than
independently aligned sampled replay, but it is still a sampled subspace
check, not symbolic unitary equivalence, and accepted B7 occurrence, proxy-T,
and ledger credit remain 0.

T-B1-004ba turns the six basis anchors from T-B1-004az into a finite
linear-span replay certificate. It builds the source/candidate error operator
restricted to the six-dimensional input span under the same zero-input global
phase anchor. The restricted error spectral norm is
2.7889440543898627e-13, max basis L2 error is 2.534056605707275e-13, and 15
coherent pair witnesses remain passed. This certifies only 6 of 524,288 input
dimensions, so it is not a full Hilbert-space unitary proof; accepted B7
occurrence, proxy-T, and ledger credit remain 0.

T-B1-004bb turns the selected non-overlap line-268 plus line-1381 patch subset
into a tolerance-bounded full-circuit semantic patch certificate for the
legacy-dialect candidate. The two selected windows are non-overlapping, both
local-unitary replacement certificates pass, the emitted legacy-dialect candidate
exists, and the candidate keeps the 795 -> 789 CNOT delta. The certificate accepts 1
full-circuit replay/QASM patch artifact, but B7 resource credit remains 0
because line 1378 is still dropped and line 1381 still has 5 unpriced off-grid
local-U3 parameters.

T-B1-004bc prices that remaining line-1381 local-U3 boundary. The five off-grid
local-U3 parameters correspond to 100 proxy-T pressure units under the project
ledger, while the selected CNOT delta remains 6 and the dropped line-1378 delta
remains 3. This is a quantified blocker, not a win: local-U3 pricing is still
not accepted, line 1378 is not recovered, and B7 occurrence, proxy-T, and
ledger credit remain 0.

T-B1-004bd now closes the naive overlap-additivity interpretation of that
dropped line-1378 delta. The line-1378 source window [1369, 1377] is contained
inside the line-1381 source window [1369, 1379] on the same [4, 8] support, so
the union region has only 5 source CNOTs. Adding the line-1381 3-CNOT delta and
the line-1378 3-CNOT delta would require -1 replacement CNOTs. The full dropped
line-1378 delta is therefore not additively recoverable; a future route must
synthesize a new union-region replacement with replay and honest local-U3
pricing, or find a different occurrence-removing certificate.

T-B1-004be tests that honest union-region route with a scoped low-CNOT search.
For the line-1378/1381 union target [1369, 1379], it searches 0-CNOT and
1-CNOT local-U3 scaffolds, including both 1-CNOT orientations. No exact
low-CNOT scaffold is found: the best 1-CNOT residual is
0.2548908758679516 with max entry error 0.12724247975106365. The existing
2-CNOT line-1381 replacement remains the current exact candidate in this
branch, and no extra delta, occurrence removal, proxy-T reduction, or B7 ledger
credit is accepted. This is not a global CNOT lower-bound theorem.

T-B1-004bf now checks that 2-CNOT boundary directly with an all-orientation
sequence census. For the same line-1378/1381 union target [1369, 1379], all
four length-2 CNOT direction sequences pass the numerical exact threshold. The
best exact sequence is `01-10`, with residual 5.812946138498332e-13, max entry
error 3.4095575404049453e-13, and 13 off-pi/4 local-U3 parameters among 18
total parameters. This confirms the current 2-CNOT union-region candidate is
not a fragile single-orientation artifact, but it remains candidate-only: no
full-circuit replay certificate, QASM patch, local-U3 pricing acceptance,
occurrence removal, proxy-T reduction, or B7 ledger credit is accepted.

T-B1-004bg then prevents that robustness result from being over-counted. It
compares the T-B1-004bf exact 2-CNOT candidates against the current line-1381
pricing boundary. The current line-1381 branch carries 5 off-pi/4 local-U3
parameters, or 100 proxy-T pressure units, while the best-priced 2-CNOT census
candidate still carries 13 off-pi/4 parameters, or 260 proxy-T pressure units.
The census route is therefore pricing-dominated by the current patch boundary:
selected replacement changes, accepted occurrence removal, proxy-T reduction,
and B7 ledger credit all remain 0.

T-B1-004bm checks the cheap grid-pricing escape hatch for the T-B1-004bf
union-region census candidates. It snaps all local-U3 parameters in each of the
four exact 2-CNOT union candidates back to the pi/4 grid and replays the union
target. Exact pass / fail is 0/4. The best grid-snap residual is
0.36435162331693166 on sequence `10-10`, and the worst is 1.021457442072864 on
sequence `10-01`. This rejects a free grid-priced adoption of the union census
route; occurrence removal, proxy-T reduction, local-U3 pricing acceptance, and
B7 ledger credit remain 0.

T-B1-004bn tests the next-cheapest union-census pricing escape hatch. For each
of the four exact 2-CNOT union-region candidates, it snaps all local-U3
parameters to the pi/4 grid, frees exactly one parameter, and re-optimizes that
single degree of freedom. All 72 one-free-parameter trials fail exact replay.
The best residual is 0.25709607640616583 on sequence `10-10` at parameter index
7; the worst best-sequence residual is 0.6857140007440164 on sequence `10-01`.
This blocks a 20-proxy-T one-free-parameter adoption of the union route;
occurrence removal, proxy-T reduction, local-U3 pricing acceptance, and B7
ledger credit remain 0.

T-B1-004bo now tests the next pricing rung for the same union-census branch.
It snaps all local-U3 parameters in the four exact 2-CNOT union candidates to
the pi/4 grid, then frees every possible pair of parameters and re-optimizes
that pair. All 612 two-free-parameter trials fail exact replay. The best
residual is 0.1831095797026285 on sequence `10-10` at pair `[5, 7]`; the worst
best-sequence residual is 0.46644639853601 on sequence `10-01`. This blocks a
40-proxy-T two-free-parameter adoption of the union route. The remaining useful
routes are now a different scaffold, symbolic/context absorption, honest
larger local-U3 pricing with full-circuit replay, or a different
occurrence-removing branch; occurrence removal, proxy-T reduction, local-U3
pricing acceptance, and B7 ledger credit remain 0.

T-B1-004bp adds a targeted three-free expansion pressure test instead of
restarting a broad cheap-cleanup sweep. For each of the four exact 2-CNOT
union-region candidates, it takes the best failed T-B1-004bo two-parameter pair,
adds one more free local-U3 parameter, and re-optimizes the resulting targeted
triple. All 64 targeted three-free trials fail exact replay. The best residual
is 0.04582709543239648 on sequence `10-10` at triple `[5, 7, 4]`; the worst
best-sequence residual is 0.3812803680403496 on sequence `10-01`. This does
not prove an exhaustive three-free lower bound, but it blocks the most natural
60-proxy-T extension of the failed two-free route. Occurrence removal,
proxy-T reduction, local-U3 pricing acceptance, and B7 ledger credit remain 0.

T-B1-004bh sharpens the remaining line-1381 blocker. It snaps each one of the
five current off-pi/4 local-U3 parameters back to the pi/4 grid, then
re-optimizes the other four parameters on the same two-CNOT scaffold. All 5/5
leave-one-out trials fail the exact replay threshold: the best residual is
0.09892087709180968, which is about 9.89e6 times the 1e-8 exact tolerance. This
does not prove global five-parameter minimality, but it blocks a cheap
single-parameter removal claim. Occurrence removal, proxy-T reduction, local-U3
acceptance, and B7 ledger credit remain 0.

T-B1-004bi makes that pressure test stricter. It snaps every pair among the
same five off-pi/4 line-1381 local-U3 parameters back to the pi/4 grid, then
re-optimizes the remaining three parameters on the same two-CNOT scaffold. All
10/10 leave-two-out trials fail the exact replay threshold. The best residual
is 0.13583443746892182 for fixed pair [9, 16], and the worst residual is
0.41204448255804876 for fixed pair [16, 17]. This blocks a cheap two-parameter
free-removal claim, but it still does not prove global five-parameter
minimality. Occurrence removal, proxy-T reduction, local-U3 acceptance, and B7
ledger credit remain 0.

T-B1-004bj makes the pressure test stricter again. It snaps every triple among
the same five off-pi/4 line-1381 local-U3 parameters back to the pi/4 grid,
then re-optimizes the remaining two parameters on the same two-CNOT scaffold.
All 10/10 leave-three-out trials fail the exact replay threshold. The best
residual is 0.29673862906454757 for fixed triple [4, 9, 16], and the worst
residual is 0.7449029676343185 for fixed triple [4, 16, 17]. This blocks a
cheap three-parameter free-removal claim, but it still does not prove global
five-parameter minimality. Occurrence removal, proxy-T reduction, local-U3
acceptance, and B7 ledger credit remain 0.

T-B1-004bk pushes the same boundary to leave-four-out pressure. It snaps every
quadruple among the same five off-pi/4 line-1381 local-U3 parameters back to
the pi/4 grid, then re-optimizes the remaining one parameter on the same
two-CNOT scaffold. All 5/5 leave-four-out trials fail the exact replay
threshold. The best residual is 0.45761708677312707 for fixed quadruple
[3, 4, 9, 16], and the worst residual is 0.8369082341779268 for fixed
quadruple [4, 9, 16, 17]. This blocks a cheap four-parameter free-removal
claim, but it still does not prove global five-parameter minimality.
Occurrence removal, proxy-T reduction, local-U3 acceptance, and B7 ledger
credit remain 0.

T-B1-004bl closes the endpoint version of the same cheap-removal story. It
snaps all five current off-pi/4 line-1381 local-U3 parameters back to the
pi/4 grid with no parameter left to re-optimize. The all-grid endpoint fails
the exact replay threshold: exact pass / fail is 0/1, residual is
0.8415210419190079, about 8.42e7 times the 1e-8 exact tolerance. This blocks
an all-grid snap interpretation, but it still does not prove global
five-parameter minimality. Occurrence removal, proxy-T reduction, local-U3
acceptance, and B7 ledger credit remain 0.

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

Prometheus-plan is designed for many agents working in parallel:

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

T-B1-004bq changes scaffold instead of continuing cheap parameter-cleanup tests.
It allows 3 CNOTs for the same line-1378/1381 union target and searches all 8
CNOT direction sequences with arbitrary local-U3 layers. All 8 sequences reach
local exact replay, but the best exact priced candidate still has 18 off-pi/4
local-U3 parameters, or 360 proxy-T pressure units, on sequence `10-10-01`.
That is worse than both the current line-1381 5-parameter / 100-proxy-T
boundary and the best 2-CNOT census 13-parameter / 260-proxy-T candidate; the
3-CNOT scaffold also fails to structurally dominate the current 2-CNOT
line-1381 replacement. Occurrence removal, proxy-T reduction, local-U3 pricing
acceptance, and B7 ledger credit remain 0.

T-B1-004br consumes that best exact 3-CNOT priced candidate and asks whether the
18 off-pi/4 local-U3 parameters can be cheaply absorbed by the native optimized
gcm_h6 rotation inventory or by one same-support context rotation in the
line-1378/1381 union window. The answer is negative under this gate: 0/18
parameters have exact inventory matches, 0/18 have absolute-angle inventory
matches, 0/18 have same-support context matches, and 0/18 exactly cancel back
to the pi/4 grid with one context rotation. The best one-step grid-cancellation
error is 0.000655799901145393, still outside the exact tolerance. The 3-CNOT
route therefore remains pricing-dominated; B7 ledger credit remains 0.

T-B1-004bs then broadens the same 3-CNOT absorption test from one context
rotation to signed sums of two or three same-support context rotations. For the
same sequence `10-10-01`, it checks all 18 off-pi/4 parameters against 44
context rotations, with 3,784 width-2 combinations and 105,952 width-3
combinations per parameter. Across 1,975,248 signed-combination tests, exact
width-2 absorption is 0/18, exact width-3 absorption is 0/18, and the best
width-2/width-3 grid error remains 0.000655799901145393. This closes the
bounded two-/three-rotation context escape hatch for the direct 3-CNOT branch;
accepted occurrence removal, proxy-T reduction, and B7 ledger credit remain 0.

T-B1-004bt takes the next bounded step for the same direct 3-CNOT branch by
testing exactly four same-support context rotations. The gate keeps sequence
`10-10-01`, 18 off-pi/4 parameters, and 44 context rotations, then evaluates
2,172,016 width-4 signed combinations per parameter. Across 39,096,288 total
signed-combination tests, exact width-4 absorption is 0/18. The best width-4
grid error remains 0.000655799901145393 and the worst best-parameter error is
0.027779719778975753. This closes the bounded exactly-four-rotation context
escape hatch for the direct 3-CNOT branch; accepted occurrence removal,
proxy-T reduction, and B7 ledger credit remain 0.

T-B1-004bu responds to the dialect boundary directly. It consumes the
legacy-dialect line-268 plus line-1381 candidate and exports an OpenQASM 3.0
artifact at
`results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`.
The export has a valid `OPENQASM 3.0` header, uses `stdgates.inc`, converts
487 legacy `u3` gates to `U`, converts the final measurement to modern
assignment syntax, and preserves operation counts: 789 `cx`, 601 `rz`, 487
`U`, and 1 measurement. This accepts one OpenQASM 3 export artifact, but it is
not a new replay proof, not a local-U3 pricing certificate, not occurrence
removal, and not B7 ledger credit. The next useful gate must parse or replay
the OpenQASM 3 artifact through a modern toolchain and then connect it to
symbolic equivalence or honest resource pricing.

T-B1-004bv then turns that next gate into an explicit dependency boundary. It
strictly parses the OpenQASM 3 artifact with the project's local parser and
confirms 19 qubits, 1 bit, 1,884 statements, 1,878 operation rows, and the same
operation counts as the export gate: 789 `cx`, 601 `rz`, 487 `U`, and 1
measurement. Local parser errors are 0, so one local OpenQASM 3 parse artifact
is accepted. The installed Qiskit core is present, but `qiskit_qasm3_import` is
not installed, so Qiskit's OpenQASM 3 loader is attempted and rejected with a
`MissingOptionalLibraryError`. Qiskit loader parse artifacts, replay proof,
local-U3 pricing, occurrence removal, proxy-T reduction, and B7 ledger credit
all remain 0.

T-B1-004bw adds a structural roundtrip gate before any new replay or resource
claim. It normalizes the legacy OpenQASM 2 candidate and the OpenQASM 3 artifact
into canonical instruction streams and compares them exactly. Both streams have
1,878 instructions, zero mismatches, identical SHA256 stream hashes, and the
same operation counts: 789 `cx`, 601 `rz`, 487 `U`, and 1 measurement. This
accepts one structural roundtrip artifact, but Qiskit-loader artifacts, replay
proof, local-U3 pricing, occurrence removal, proxy-T reduction, and B7 ledger
credit remain 0.

T-B1-004bx moves that OpenQASM 3 artifact from structural portability into a
project-local semantic replay check. The gate parses the OpenQASM 3 file with
the project's strict subset parser, constructs a `QuantumCircuit` directly, and
compares the resulting 19-qubit default-input statevector against the optimized
source circuit after final measurement removal. The replay passes with fidelity
0.9999999999999551, infidelity 4.4853010194856324e-14, max aligned amplitude
delta 1.3908205762322243e-13, max probability delta 5.551115123125783e-16, and
measured q[4] marginal delta 5.551115123125783e-16. This accepts one
project-local OpenQASM 3 replay artifact, but it is still not a Qiskit loader
parse, symbolic equivalence, arbitrary-input equivalence, local-U3 pricing,
occurrence removal, proxy-T reduction, or B7 ledger credit.

T-B1-004by broadens the same OpenQASM 3 replay branch from the default input to
8 deterministic sampled inputs. The project-local parser replays 6
computational-basis preparations and 2 seeded product states against the
optimized source after final measurement removal. All 8 cases pass with min
state fidelity 0.9999999999999547, max infidelity 4.529709940470639e-14, max
aligned amplitude delta 1.392888964263601e-13, and max probability delta
1.8214596497756474e-15. This accepts one project-local OpenQASM 3 multi-input
replay artifact, but Qiskit-loader replay, symbolic/arbitrary-input
equivalence, local-U3 pricing, occurrence removal, proxy-T reduction, and B7
ledger credit remain 0.

T-B1-004bz adds phase-consistent replay pressure to that OpenQASM 3 branch. The
project-local parser replays the candidate over 4 phase-anchor inputs and 4
superposition inputs, then checks overlap-phase spread rather than relying only
on per-input global-phase alignment. All 8 cases pass with overlap phase spread
1.3722356584366935e-13 radians, min overlap magnitude
0.9999999999999772, min state fidelity 0.9999999999999547, max aligned
amplitude delta 1.392888964263601e-13, and max probability delta
1.074140776324839e-14. This accepts one project-local OpenQASM 3
phase-consistent replay artifact, but Qiskit-loader replay,
symbolic/arbitrary-input equivalence, local-U3 pricing, occurrence removal,
proxy-T reduction, and B7 ledger credit remain 0.

T-B1-004ca fixes the zero-input global phase anchor for the OpenQASM 3 branch
and reuses that same anchor across 6 basis-subspace anchors and 15 coherent
pair superpositions. All 21 cases pass with max global-anchor phase delta
3.142993331217661e-14 radians, min overlap magnitude 0.9999999999999772, min
state fidelity 0.9999999999999547, max aligned amplitude delta
1.3928889642636009e-13, and max probability delta 1.074140776324839e-14. This
accepts one project-local OpenQASM 3 global-phase subspace replay artifact, but
Qiskit-loader replay, symbolic/arbitrary-input equivalence, local-U3 pricing,
occurrence removal, proxy-T reduction, and B7 ledger credit remain 0.

T-B1-004cb turns the OpenQASM 3 global-phase subspace replay evidence into a
finite linear-span certificate. It consumes T-B1-004ca, rebuilds the
OpenQASM 3 candidate through the project-local parser, fixes the same zero-input
global phase anchor, and computes the restricted error operator over the
six-dimensional span generated by the basis anchors. The certificate passes with
linear-span spectral norm 2.7889440543898627e-13, Frobenius norm
6.134324404657074e-13, max basis L2 error 2.534056605707275e-13,
max basis amplitude delta 1.3928889642636009e-13, max basis probability delta
7.771561172376096e-16, max source/candidate Gram delta
1.9984014443252818e-15, and max cross-Gram delta 4.403624367368429e-14.
This accepts one project-local OpenQASM 3 finite-span certificate, but it still
covers only 6 of 524,288 input dimensions and remains separate from
Qiskit-loader replay, full-space symbolic/local-unitary equivalence,
local-U3 pricing, occurrence removal, proxy-T reduction, and B7 ledger credit.

T-B1-004cc lifts the selected line-268 plus line-1381 composable patch
certificate onto the OpenQASM 3 artifact. It consumes the QASM2 composable patch
certificate, the OpenQASM 3 structural roundtrip gate, and the OpenQASM 3
finite-span replay certificate. The canonical QASM2/OpenQASM 3 instruction
stream still matches at 1,878 instructions with zero mismatches and SHA-256
`7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343`; the
selected patch lines remain `[268, 1381]`, the dropped overlap line remains
`[1378]`, max selected patch residual is `6.513210005207597e-13`, max selected
entry error is `4.525273102184799e-13`, and the OpenQASM 3 finite-span spectral
error remains `2.7889440543898627e-13`. This accepts one project-local
OpenQASM 3 composable patch-lift artifact, but it is still not a Qiskit-loader
parse, full-space symbolic/unitary proof, local-U3 pricing certificate,
occurrence removal, proxy-T reduction, or B7 ledger credit.

T-B1-004cd adds a provenance seal for the OpenQASM 3 patch-lift chain. It
hash-seals the QASM2 candidate, OpenQASM 3 candidate, QASM2 composable patch
certificate, OpenQASM 3 structural roundtrip certificate, OpenQASM 3 finite-span
certificate, and OpenQASM 3 patch-lift certificate. Both QASM files have 1,884
raw lines and normalize to the same 1,878-instruction stream with SHA-256
`7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343`; the
provenance seal digest is
`159c9b1d99a607d463fe712a190b35460603712561a4ea8eb4033bf4de495902`. This
accepts one project-local OpenQASM 3 provenance-seal artifact, but it still does
not claim Qiskit-loader parsing, symbolic equivalence, local-U3 pricing,
occurrence removal, proxy-T reduction, or B7 ledger credit.

T-B1-004ce adds a source-map gate for the OpenQASM 3 patch-lift chain. It builds
a one-to-one instruction map between the QASM2 candidate and the OpenQASM 3
candidate over all 1,878 normalized instructions, records the map digest
`92a499ea6d549426095fbb0fc878f7033027991621a6d5ea1c03cd25d82e9e1e`, and
confirms raw-line drift count 0. The selected patch lines remain line 268 and
line 1381, mapped to instruction indices 263 and 1375; the dropped overlap line
1378 maps to instruction index 1372. This accepts one project-local OpenQASM 3
source-map artifact, but it still does not claim Qiskit-loader parsing,
symbolic equivalence, local-U3 pricing, occurrence removal, proxy-T reduction,
or B7 ledger credit.

T-B1-004cf compresses that source-map evidence into a reviewable OpenQASM 3
patch witness packet. The packet has 3 rows for candidate lines 268, 1378, and
1381; 2 rows are selected non-overlap witnesses, 1 row is the dropped-overlap
witness, and the instruction indices are 263, 1372, and 1375. The witness packet
hash is `e0d2e63f3f2c16be685baef3360ff68d5765db549c5e17e655a6e74c6fb82dc8`;
max witness residual is `9.049428032408627e-13`, max entry error is
`6.398911863522162e-13`, selected CNOT delta remains 6, and the lost overlap
delta remains 3. This accepts one project-local review packet only; Qiskit-loader
parsing, symbolic equivalence, local-U3 pricing, occurrence removal, proxy-T
reduction, and B7 ledger credit remain 0.

T-B1-004cg removes the previous OpenQASM 3 loader dependency blocker. After
adding `qiskit-qasm3-import>=0.6`, Qiskit's OpenQASM 3 loader parses the
exported candidate with 19 qubits, 1 classical bit, depth 1483, and operation
counts `cx=789`, `rz=601`, `u=487`, `measure=1`. Default-input replay against
the optimized source passes with fidelity `0.9999999999999551`, max aligned
amplitude delta `1.3908205762322243e-13`, max probability delta
`5.551115123125783e-16`, and measured q[4] marginal delta
`5.551115123125783e-16`. This accepts one Qiskit-loader parse artifact and one
Qiskit-loader replay artifact, but it still does not claim arbitrary-input or
symbolic equivalence, local-U3 pricing, occurrence removal, proxy-T reduction,
or B7 ledger credit.

T-B1-004ch broadens that loader-backed evidence from the default input to the
same deterministic 8-input suite used by the project-local multi-input replay
gate. The Qiskit-loaded OpenQASM 3 candidate passes all 8 cases: 6
computational-basis inputs and 2 seeded product states. Minimum state fidelity
is `0.9999999999999547`, max infidelity is `4.529709940470639e-14`, max
global-phase-aligned amplitude delta is `1.392888964263601e-13`, and max
probability delta is `1.8214596497756474e-15`. This accepts one
Qiskit-loader multi-input replay artifact, but it remains sampled numerical
evidence, not arbitrary-input symbolic equivalence, local-U3 pricing,
occurrence removal, proxy-T reduction, or B7 ledger credit.

T-B1-004ci adds Qiskit-loader phase-consistent replay pressure. The
Qiskit-loaded OpenQASM 3 candidate passes 4 phase-anchor inputs and 4
superposition inputs with overlap phase spread `1.3722356584366935e-13`
radians, min overlap magnitude `0.9999999999999772`, min fidelity
`0.9999999999999547`, max aligned amplitude delta
`1.392888964263601e-13`, max probability delta
`1.074140776324839e-14`, and 0 failed cases. This accepts one Qiskit-loader
phase-consistent replay artifact, but it remains sampled evidence, not
symbolic or arbitrary-input equivalence, local-U3 pricing, occurrence removal,
proxy-T reduction, or B7 ledger credit.

T-B1-004cj adds Qiskit-loader global-phase anchored subspace replay pressure.
The Qiskit-loaded OpenQASM 3 candidate fixes the zero-input global phase anchor
and reuses it across 6 basis anchors plus 15 coherent pair superpositions. All
21 cases pass with max global-anchor phase delta `3.142993331217661e-14`
radians, min overlap magnitude `0.9999999999999772`, min fidelity
`0.9999999999999547`, max aligned amplitude delta
`1.3928889642636009e-13`, max probability delta
`1.074140776324839e-14`, and 0 failed cases. This accepts one Qiskit-loader
global-phase subspace replay artifact, but it remains sampled subspace
evidence, not symbolic or arbitrary-input equivalence, local-U3 pricing,
occurrence removal, proxy-T reduction, or B7 ledger credit.

T-B1-004ck upgrades that loader branch to a finite linear-span replay
certificate. It consumes the Qiskit-loader global-phase subspace gate and the
project-local OpenQASM 3 linear-span certificate, fixes the same zero-input
global phase anchor, and computes the source/candidate error operator over the
6-dimensional basis-anchor span. The loader-backed certificate passes with
spectral norm `2.7889440543898627e-13`, Frobenius error
`6.134324404657074e-13`, max basis L2 error `2.534056605707275e-13`, max basis
amplitude delta `1.3928889642636009e-13`, max basis probability delta
`7.771561172376096e-16`, max source/candidate Gram delta
`1.9984014443252818e-15`, and max cross-Gram delta
`4.403624367368429e-14`. This accepts one Qiskit-loader finite-span certificate
artifact for 6 of 524,288 input dimensions, but it is still not full-space
symbolic equivalence, arbitrary-input equivalence, local-U3 pricing, occurrence
removal, proxy-T reduction, or B7 ledger credit.

T-B1-004cl lifts the composable patch evidence onto the Qiskit-loader path. It
consumes the project-local OpenQASM 3 composable patch-lift gate, the
Qiskit-loader global-phase gate, and the Qiskit-loader finite-span certificate
for the same exported candidate. The selected patch lines remain 268 and 1381,
the dropped overlap line remains 1378, the normalized instruction stream still
has 0 mismatches across 1,878 instructions, and the loader-backed finite-span
certificate keeps spectral norm `2.7889440543898627e-13`, max basis L2 error
`2.534056605707275e-13`, max probability delta `7.771561172376096e-16`, and
max cross-Gram delta `4.403624367368429e-14`. This accepts one
Qiskit-loader-backed composable patch-lift support artifact, but it is still
not full-space symbolic equivalence, arbitrary-input equivalence, local-U3
pricing, occurrence removal, proxy-T reduction, or B7 ledger credit.

T-B1-004cm seals the Qiskit-loader evidence chain for drift detection. It
hashes the exported OpenQASM 3 candidate plus the Qiskit-loader replay,
multi-input, phase-consistent, global-phase, finite-span, and composable
patch-lift support artifacts into seal
`d06c1fdae3ad7cad1971cdcdcea1f890d3931924a7e70affc25fdf89737e09a8`. The seal
keeps Qiskit 2.4.1, `qiskit-qasm3-import` 0.6.0, `openqasm3` 1.0.1, 19 qubits,
depth 1483, operation counts `cx=789`, `rz=601`, `u=487`, `measure=1`, 8
multi-input cases, 8 phase-consistent cases, 21 global-phase cases, 0 failed
cases, and the same selected lines [268, 1381] with dropped overlap line
[1378]. This is a reproducibility gate, not a new equivalence theorem:
full-space symbolic equivalence, local-U3 pricing, occurrence removal, proxy-T
reduction, and B7 ledger credit remain 0.

T-B1-004cn reproduces that Qiskit-loader evidence seal. It independently
recomputes all 7 source artifact hashes, reruns the T-B1-004cm seal generator,
and requires the expected, independent, and reproduced seals to match
`d06c1fdae3ad7cad1971cdcdcea1f890d3931924a7e70affc25fdf89737e09a8`. The JSON
report remains byte-stable with hash
`f7a5f57ced33e3d8c3f8be12fbcd0dba26a5b42206dac8bb0e1ed1723a735ad2`, the
Markdown report remains byte-stable with hash
`7a648d78758b0f6499d7a743993714fef3d47932b9b02ec5de317228c7828dc7`, and the
source-hash mismatch count is 0. This accepts one evidence-seal reproduction
artifact, but it is still a reproducibility gate only: full-space symbolic
equivalence, local-U3 pricing, occurrence removal, proxy-T reduction, and B7
ledger credit remain 0.

T-B1-004co adds seeded product-state semantic pressure to the Qiskit-loader
OpenQASM 3 path. It consumes the phase-consistent replay gate and the reproduced
evidence seal, loads the same OpenQASM 3.0 candidate through Qiskit's qasm3
loader, removes final measurements, and replays 16 deterministic product-state
inputs generated from seeds
`[17, 29, 41, 53, 67, 79, 83, 97, 101, 113, 127, 131, 149, 163, 181, 191]`
with an `rx/ry/rz` preparation sequence. All 16 cases pass with min fidelity
`0.9999999999999389`, max infidelity `6.106226635438361e-14`, max aligned
amplitude delta `1.3496991625769186e-14`, max L2 aligned amplitude delta
`2.8917153762798005e-13`, max probability delta `8.020927672047762e-16`, and
0 failed cases. This accepts one seeded product-state replay artifact, but it
does not establish arbitrary-input or symbolic equivalence, local-U3 pricing,
occurrence removal, proxy-T reduction, or B7 ledger credit.

T-B1-004cp adds the resource-boundary decision gate that the seeded replay
branch needed. It consumes the seeded product-state replay result, the line-1381
local-U3 pricing gate, the theta-sharing cost-model gate, and the refreshed B7
ledger gate. The gate accepts the seeded replay evidence as semantic pressure,
but records all five current resource blockers as still failed: line 1381 keeps
5 off-grid local-U3 parameters and 100 unpriced proxy-T pressure, line 1378's
overlap delta is still unrecovered, accepted occurrence removal is still 0
against the 30-occurrence target, the theta cost model remains rejected at 6/8
acceptance checks, and the refreshed B7 ledger still rejects theta sharing with
600 proxy-T of missing reduction. This accepts one resource-boundary artifact
and prevents replay evidence from being counted as B7 resource credit; accepted
occurrence removal, accepted proxy-T reduction, resource saving, and B7 ledger
improvement remain 0.

T-B1-004cq returns to the line-1381 resource wall and tests whether the five
remaining off-grid local-U3 parameters can be absorbed by signed sums of exactly
five nearby same-support context rotations. A meet-in-the-middle split covers
34,752,256 virtual width-5 signed combinations per parameter, or 173,761,280
virtual tests across all five parameters, using the same 44 context rotation
arguments in the 1305-1443 line window. The result is still negative: 0/5
parameters have exact width-5 absorption back to the pi/4 grid, with best grid
error range `0.001581991109333103` to `0.026659551749407484`. This closes the
bounded width-5 local context route, but it is not a global obstruction theorem.
No full-circuit replay certificate, occurrence removal, proxy-T reduction,
resource saving, or B7 ledger improvement is accepted.

`T-B1-004cr` / `T-B7-010` adds a cone_01 route-triage decision gate over the
current shortcut stack. It consumes the seeded replay resource-boundary,
width-5 context absorption, commutation-corridor, shared-theta
cost-model/refreshed-ledger, and all-grid line-1381 removal artifacts. The gate
triages 5 shortcut routes and accepts 0 for B7 credit: seeded replay keeps 5
failed resource blockers, width-5 context absorption has 0/5 exact hits, cheap
commutation corridor has 0 accepted candidates, shared-theta cache saving
remains rejected by the cost model and refreshed B7 ledger, and all-grid
parameter removal has 0 exact passes. The next route must be a
commutation-aware full-circuit replay certificate, honest line-1381 local-U3
pricing under a physical synthesis model, line-1378 recovery without overlap
double-counting, or a different occurrence-removing scaffold. No occurrence
removal, proxy-T reduction, resource saving, or B7 ledger improvement is
accepted.

`T-B1-004cs` / `T-B7-011` follows the route-triage decision by testing the
honest line-1381 local-U3 pricing route under a conservative physical synthesis
guardrail. The current selected line-268 plus line-1381 patch keeps 5 off-grid
line-1381 local-U3 parameters. With an aggregate synthesis-error budget of
`1e-8`, the per-parameter budget is `2e-9`, the single-parameter T-count bound
is 97, and the five-parameter physical synthesis T-count bound is 485. The
selected 6-CNOT structural delta only supplies 120 proxy-credit units under the
project ledger, leaving a positive cost-minus-credit gap of 365. Physical
synthesis pricing is therefore not accepted, line 1378 is still unrecovered,
and accepted occurrence removal, proxy-T reduction, resource saving, and B7
ledger improvement remain 0.

`T-B1-004ct` seals the current OpenQASM 3/Qiskit-loader claim boundary. It
aggregates the byte-stable evidence-seal reproduction, the 6-dimensional
linear-span replay certificate, the composable patch lift, and the seeded
resource-boundary gate into one citable evidence packet. All 8 seal
requirements pass: selected lines remain `[268, 1381]`, dropped overlap line
`[1378]` remains unrecovered, the Qiskit-loader certified input-subspace
fraction is `1.1444091796875e-05`, 16 seeded product-state cases pass with min
fidelity `0.9999999999999389`, and all 5 resource blockers remain open. This is
useful because it prevents replay evidence from drifting into a resource claim:
accepted occurrence removal, proxy-T reduction, resource saving, and B7 ledger
improvement remain 0.

`T-B1-004ee` / `T-B7-013n` consumes the R28 certificate-triad contract and
treats the emitted template as a placeholder submission. The preflight passes
8/8 requirements by rejecting that placeholder: C1 source-lineage, C8
zero-credit claim boundary, and C9 hash surface pass, but C2-C7 fail because
the strict replay rows, same-unitary replay certificate, 31-row same-access
denominator table, leakage-free optimizer trace, machine replay, and offline
bundle evidence are still missing. Preflight hash
`6129db1af66089749a8e3317bd0d3376d90a42991c16dac290f875fc81839c80`; 12
placeholder fields are rejected; O3 remains open; reroute, B7 credit, STV
credit, and resource-saving claims remain 0/false.

`T-B1-004ef` / `T-B7-013o` is the current B1/B7 O3-F4 gate. It narrows the
first missing evidence bundle, C2 strict replay, into an 8-row source-bound
submission template derived from the R24 challenge packet. The gate passes 8/8
requirements by emitting the row template and rejecting it as a placeholder:
8/8 challenge rows are present, every row has the required field surface, but
72 placeholder cells and 0 numeric replay errors mean C2 is not accepted.
Template hash `5169bcb486c808157c30d89fd9e02d91bae2918748fa338f44d2b7aab5cd65ab`;
row-table hash `fe1c57867f1e2e23a392e8a87045918b349c3df97bf2e5df3eb471459e7351e9`;
preflight hash `f4b743162793460c4cd93c600cd9a7db07456edede109ec66c99c2138c67dadf`.
O3 remains open; C2 acceptance, reroute, B7 credit, STV credit, and
resource-saving claims remain 0/false.

`T-B1-004eg` / `T-B7-013p` now hardens that C2 surface against a numeric-only
overclaim. It builds a sentinel fixture with all 8 replay errors numerically
below the `1e-08` tolerance; the largest error is `8e-10`, so the numeric
surface passes. The fixture is still rejected because 32 witness, circuit, and
stdout hash cells are invalid placeholders and no real replay command
provenance is supplied. Fixture hash
`78a33f7e7bcbad0f3f5dce8d172d997eb7cde9a43a2b979abd9d852971544e07`;
preflight hash `978f9ffe9d72a438c4701c659381eb4e818758448bb13f3b097e7d4b17625256`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004eh` / `T-B7-013q` now hardens C2 again against hash-shape theater. It
constructs a fixture where the numeric surface still passes, every witness,
circuit, and stdout hash has valid sha256 shape, and the replay command has an
executable command shape. The fixture is rejected anyway because all 8 declared
provenance binding hashes fail to recompute from the row payload. Fixture hash
`7bb2708cedae88328e309bb5a7431f5d916cbbb9f284d532f1a4f532d2e73bc2`;
preflight hash `933d2689f1fb65a27db900da5b078594d18d438a0441012fbd3a09d8a80ffa0c`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004ei` / `T-B7-013r` turns the R32 blocker into a submission contract.
The new C2 provenance-binding contract defines 11 binding fields and 9 required
execution artifact surfaces, emits an 8-row template, and rejects the current
state because no source-backed submission or execution artifact exists yet.
Contract hash `d4ff1b028d42ca0c995bfee52b0c4fdc5e3dc8cc877b358b1752bef17e4c92aa`;
template hash `6ed9e03c13ad5287efe6c804a458f0b3f9156c2533b540972cb48eeb85c19330`;
preflight hash `4505af5067f39902a13670f9b0162aaac542b78b7723ebf55e6d61149218c52d`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004ej` / `T-B7-013s` now turns that C2 contract into a runnable
preflight verifier. It consumes the R33 contract/template, recomputes the
template hash, then rejects the current placeholder template before any row can
count. The rejection is explicit: 0/8 rows pass, 88 binding fields remain
placeholders, 72 execution artifact cells remain placeholders, 72 hash cells are
invalid, 8 provenance binding hashes fail to recompute from row payloads, and 8
replay errors are nonnumeric. Preflight hash
`bb3cccb45db7d5de25fb2747529d7860aa8b58a093bdfd7ad8bbd756301b67ac`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004ek` / `T-B7-013t` now hardens that verifier against metadata-only
evidence. It constructs a fixture whose C2 rows pass the surface requirements:
valid hash shape, recomputed provenance bindings, numeric replay errors below
`1e-08`, and the zero-credit claim boundary. The fixture is still rejected
because the four materialized execution-file classes per row are absent:
replay stdout, source circuit, candidate circuit, and same-unitary witness.
Surface rows pass/fail `8/0`; materialized rows pass/fail `0/8`; missing
materialized files `32`. Fixture hash
`df2c6cc13381c1762bd200a2f77ec0302c32bd6cbbc270b840c05c2778cf2c3a`;
preflight hash `ab1ec9d5377dd719ccdf31a3c83983167c354db771043ca2aa2aa84de2154122`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004el` / `T-B7-013u` turns the materialization blocker into a partial
smoke row. It creates four hash-matched files for `O3-F4-C01`: replay stdout,
source circuit, candidate circuit, and witness. The row is intentionally marked
as materialization-only, not a same-unitary certificate and not source-backed C2
evidence. The fixture keeps all 8 metadata surfaces clean, but only 1/8 rows is
materialized, so the bundle is rejected. Surface rows pass/fail `8/0`;
materialized rows pass/fail `1/7`; missing materialized files drop from `32` to
`28`. Fixture hash
`6565d611d2b0ca01af2de0c73054b765278f450e60f6ad35107fef0ddacb0144`;
preflight hash `7a5d901ba75e0bc9f1d7d06d8530a4a08ea3a93f70afb8711c8143a925437042`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004em` / `T-B7-013v` closes the pure C2 file-existence blocker without
promoting smoke evidence into proof. It materializes all 8 O3-F4 C2 rows with
32 hash-matched files across replay stdout, source circuit, candidate circuit,
and witness slots. Surface rows pass/fail `8/0`; materialized rows pass/fail
`8/0`; missing materialized files drop to `0`; hash mismatches stay `0`.
Fixture hash `17b1a4e3e197ac838d636bcb52ca81a9001651758e1c306b97039b578eff32a6`;
fixture file sha256
`068391b6c4c0087a877c2a863c8d7f7a3b06291af9b5da53982266a4f18b374a`;
preflight hash `4a469eadb38d952eb6168c55aee670c4122301478c44490badb831f1c86f5734`.
The rejection is now sharper: all 8 rows are still smoke-only, 0 rows are
source-backed, no same-unitary certificate is accepted, and C2/O3/reroute/B7
credit/STV/resource-saving claims remain 0/false. The next useful PR must
replace smoke files with source-backed replay outputs and same-unitary witness
files before C3-C7 can count.

`T-B1-004en` / `T-B7-013w` now turns that next step into a hard discriminator.
It emits the O3-F4 C2 source-backed replacement contract and reruns the current
R37 all-row fixture against stricter source-backed evidence rules. The result is
intentionally negative but useful: all 8 rows remain materialized, all 8 are
rejected as smoke-only, 0 rows pass the source-backed discriminator, source-backed
flag failures are `8`, source-provenance failures are `8`, witness-schema
failures are `8`, and provenance-binding mismatches remain `0`. Replacement
contract hash `906da61aa3c205ebefe1caf001e3e2b86aeb74abcf89d1bbc6441f8c1137186f`;
discriminator hash `e23f694cdb37f985e30b15ead907bbf4772db2260398c773c7e5e3777d00c852`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false. The next useful PR is now narrower: submit at least one
row that satisfies the source-backed replacement contract before scaling to all
8 rows and then moving to C3-C7.

`T-B1-004eo` / `T-B7-013x` now makes the first source-provenance move for a
single row without treating it as source-backed proof. It adds hash-verifiable
source dataset, source trace, and replay-environment files for `O3-F4-C01`.
Materialized rows still pass `8`; source-provenance rows pass `1`; source-
provenance failures drop from `8` to `7`; source-backed rows remain `0`;
source-backed flag failures remain `8`; witness-schema failures remain `8`.
Single-row source-provenance fixture hash
`4b448b8e5e8879bb8e04bc7928a3091188a51b754a15fb624c042320ad81d357`;
evaluation hash `6f7d781074ac6f195f8a7c69995f9f5996b6f5ec627e573522e5073aabf04c29`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false. The next useful PR should add real source-backed replay
flags and a same-unitary witness schema/verifier for the enriched row, then
repeat source-provenance packets for the remaining 7 rows.

`T-B1-004ep` / `T-B7-013y` now adds the first witness-schema scaffold for
`O3-F4-C01` without converting it into a same-unitary certificate. It creates a
hash-verifiable witness schema file and dry-run verifier file, preserving the
R39 source-provenance packet. Source-provenance rows pass `1`; witness-schema
rows pass `1`; witness-schema failures drop from `8` to `7`; source-backed rows
remain `0`; source-backed flag failures remain `8`. Single-row witness-scaffold
fixture hash `b9c02595fface2f8c1f51b4f627ad893bfb9c88a5fac92c9966e6f31ecb38fea`;
evaluation hash `1d6e5ce62e04b2c1bfd5532b5acff3684a075f3faec4303cee89be6a5a10518b`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false. The next useful PR must turn the dry-run scaffold into a
real same-unitary verifier and replace the smoke flags with source-backed replay
flags for `O3-F4-C01`.

`T-B1-004eq` / `T-B7-013z` now makes the witness scaffold executable as a
preflight, while still rejecting it as non-evidence for C2. It adds a
hash-verifiable witness-preflight transcript and command manifest for
`O3-F4-C01`. Source-provenance rows pass `1`; witness-schema rows pass `1`;
witness-preflight rows pass `1`; witness-preflight failures drop from `8` to
`7`; source-backed rows remain `0`; source-backed flag failures remain `8`.
Single-row witness-preflight fixture hash
`93cdfd2c153f052d28c1949e35a44e86a835d4c2ddab9d3859e42e079ff7437a`;
evaluation hash `507326bb8120b51b1d4c1ea8a7d8d598178b76f2faddab1c9ce52b1904e008d8`.
C2 remains unaccepted because R41 does not compute a unitary distance, does not
turn the preflight into a same-unitary certificate, and does not mark the row
source-backed. O3, reroute, B7 credit, STV credit, and resource-saving claims
remain 0/false.

`T-B1-004er` / `T-B7-014a` now replaces the R41 preflight-only step with one
actual unitary-distance computation for `O3-F4-C01`. The R42 gate parses the
OpenQASM 3.0 single-qubit `rz(0.125)` source/candidate pair, computes the
one-qubit RZ operator-norm distance, and records `0.0` under a hash-bound
witness and transcript. Source-provenance rows pass `1`; witness-schema rows
pass `1`; witness-preflight rows pass `1`; unitary-distance rows pass `1`;
unitary-distance failures remain `7`; source-backed rows remain `0`;
source-backed flag failures remain `8`. Single-row unitary-distance fixture
hash `6588f37a519d94058f8b0cffc9698a8aeeb574cb0dea325e79ce8823e5ae58de`;
evaluation hash `0fefc6f3c95580ac37aea5e54ff2982058fc5f5676b25f9e8c57098da9468c98`.
C2 remains unaccepted because R42 is still one smoke row, does not mark the row
source-backed, and does not turn the numeric distance into a same-unitary
certificate. O3, reroute, B7 credit, STV credit, and resource-saving claims
remain 0/false. The next useful PR should replace smoke flags with real
source-backed replay flags only after independent source lineage and replay
evidence exist, then replicate provenance, witness, preflight, and unitary
distance packets for the remaining 7 rows.

`T-B1-004es` / `T-B7-014b` now extends that unitary-distance computation from
one smoke row to all 8 O3-F4 C2 smoke rows. R43 parses every OpenQASM 3.0
single-qubit RZ source/candidate pair, computes the one-qubit RZ operator-norm
distance, and records max computed distance `0.0` across the 8-row bundle.
Materialized rows pass `8`; source-provenance rows still pass only `1`;
witness-schema rows still pass only `1`; witness-preflight rows still pass only
`1`; unitary-distance rows now pass `8`; unitary-distance failures drop to `0`;
source-backed rows remain `0`; source-backed flag failures remain `8`.
All-row unitary-distance fixture hash
`544e83b2ed5c72b6590595bd0925497bf4438a850dcbc841fba100d8763088d5`;
evaluation hash `969f78433eb87bbf1bc00d43279bb56035604ff01f27f3f3510a68fa957b6ed5`.
C2 remains unaccepted because R43 is still a smoke-distance coverage gate, not
source-backed replay, not a same-unitary certificate, and not an O3 closure.
O3, reroute, B7 credit, STV credit, and resource-saving claims remain 0/false.
The next useful PR is no longer "compute the remaining smoke distances"; it is
to replace smoke rows with real source-backed replay evidence and add
provenance, witness schema, and preflight packets for `O3-F4-C02` through
`O3-F4-C08`.

`T-B1-004et` / `T-B7-014c` now binds source-provenance packets for the 7 C2
rows that lacked provenance after R43. It adds hash-verifiable source dataset,
source trace, and replay-environment files for `O3-F4-C02` through
`O3-F4-C08` while keeping `O3-F4-C01` on its R39 provenance packet.
Materialized rows pass `8`; source-provenance rows now pass `8`; source-
provenance failures drop to `0`; unitary-distance rows remain `8`;
witness-schema rows still pass only `1`; witness-preflight rows still pass only
`1`; source-backed rows remain `0`; source-backed flag failures remain `8`.
Remaining source-provenance fixture hash
`23009a587461b2eb2ecae0e22e178aaa2935505efdc1010d6d76a2018a2bb98e`;
evaluation hash `5bca1cbfcfe354876962402673c4c8eb125fd4de472a7cedd71dfa9a09c386f9`.
C2 remains unaccepted because R44 is provenance binding, not witness-schema
completion, not executable preflight completion, not source-backed replay, and
not a same-unitary certificate. O3, reroute, B7 credit, STV credit, and
resource-saving claims remain 0/false. The next useful PR should add witness
schemas and executable preflight packets for `O3-F4-C02` through `O3-F4-C08`,
then rerun the source-backed discriminator before C3-C7.

`T-B1-004eu` / `T-B7-014d` now binds witness-schema packets for the 7 C2
rows that lacked schema coverage after R44. It adds hash-verifiable witness
schema and dry-run verifier files for `O3-F4-C02` through `O3-F4-C08`, while
leaving executable preflight and source-backed acceptance blocked.
Materialized rows pass `8`; source-provenance rows pass `8`; witness-schema
rows now pass `8`; witness-schema failures drop to `0`; unitary-distance rows
remain `8`; witness-preflight rows still pass only `1`; witness-preflight
failures remain `7`; source-backed rows remain `0`; source-backed flag failures
remain `8`. Remaining witness-schema fixture hash
`fec121320fee7ca6bb805eae33da552ff311401bd1cac69198f6b06250388582`;
evaluation hash `4d84a1bf7b06fb3317c79016c8e9b7c6063a7e1bf70a7169e1304ea129c0ad18`.
C2 remains unaccepted because R45 is schema binding, not executable preflight
completion, not source-backed replay, and not a same-unitary certificate. O3,
reroute, B7 credit, STV credit, and resource-saving claims remain 0/false. The
next useful PR should add executable witness-preflight transcripts for
`O3-F4-C02` through `O3-F4-C08`, then rerun the source-backed discriminator
before C3-C7.

`T-B1-004ev` / `T-B7-014e` now binds executable witness-preflight transcripts
and command manifests for the 7 C2 rows that lacked preflight coverage after
R45. Materialized rows pass `8`; source-provenance rows pass `8`; witness-
schema rows pass `8`; witness-preflight rows now pass `8`; unitary-distance
rows remain `8`; source-backed rows remain `0`; source-backed flag failures
remain `8`. Remaining witness-preflight fixture hash
`7665b3e23fe6663f2c4335a11b53ef0c9b5bb0bad9716cf0eb200f09274d5cbe`;
evaluation hash `f2ab073dad9f63d0d592a3901b38b19d3741225ac25ea5f9b915c7a109cd478b`.
C2 remains unaccepted because R46 is executable preflight coverage, not
source-backed replay, not a same-unitary certificate, and not an O3 closure.
O3, reroute, B7 credit, STV credit, and resource-saving claims remain 0/false.
The next useful PR should rerun the source-backed discriminator against the
all-row provenance/schema/preflight/distance bundle and keep it failing until
real source-backed replay evidence exists.

`T-B1-004ew` / `T-B7-014f` reruns the source-backed discriminator after R46
against the full all-row provenance/schema/preflight/distance fixture. The
important change is narrower failure: materialized rows pass `8`, prerequisite-
clean rows pass `8`, source-provenance failures are now `0`, witness-schema
failures are `0`, binding mismatches are `0`, and flags-only rejection rows are
`8`. Source-backed rows remain `0`; source-backed flag failures remain `8`;
smoke-only rows remain `8`. Discriminator hash
`b4db0ab566bad93fa2baba3d700e7a512a19a2d115bc7c8d35e1aa048faf4e98`;
replacement contract hash
`906da61aa3c205ebefe1caf001e3e2b86aeb74abcf89d1bbc6441f8c1137186f`.
This proves the blocker has moved from missing evidence scaffolding to the
final source-backed replay and same-unitary acceptance flags. C2 remains
unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving claims
remain 0/false. The next useful PR must replace smoke-only flags with external
source-backed replay evidence and verifier-backed same-unitary certificates
for all 8 rows before C3-C7.

`T-B1-004ex` / `T-B7-014g` turns that next step into the first concrete
source-backed row intake contract for `O3-F4-C01`. It emits a 30-key row
submission contract, a 14-key production-required surface, 9 evidence-file
classes, and a hash-bound submission template. Contract hash
`17cc41b93dc2ecefde937859f55f5ab4ad80d264c60940d4a39d0202eedd598d`;
template hash `7f08f0e608964a9c95874e7e487ae7521727ca7b0e03e8aa81916af4a8b2a052`;
evaluation hash `d647614066ffd8870051a08229e92ccffe96fd5ffb2b48f624626a8293cf89c2`.
No source-backed row is submitted or accepted yet; accepted source-backed rows
remain `0`; production-missing keys remain `14`; source-backed flags do not
pass. C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-
saving claims remain 0/false. The next useful PR should submit the
`O3-F4-C01` row artifact against this template, then rerun R47 and require
exactly one row to pass without weakening the discriminator.

`T-B1-004ey` / `T-B7-014h` makes the R48 row template executable by emitting
a preflight verifier for `O3-F4-C01`. The verifier checks the 30-key contract,
14 production-required keys, 8 file/hash pairs, 3 source-backed boolean states,
the witness schema, and zero-credit claim-boundary tokens. It rejects the
current placeholder template, as intended: accepted source-backed rows remain
`0`; empty production keys are `12`; file-hash failures are `8`; source-backed
boolean failures are `3`; schema and claim-boundary tokens pass. Verifier hash
`004f8693b7ddd3d2124bb7acdc6f49a9ab0c6e5733287a8a10d076d8b2ce43af`;
evaluation hash `c59108f40ddd483229a01c503d7e8311d228b054fdafb5486ac7c559f4614c10`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false. The next useful PR should submit `O3-F4-C01` with all
production keys and hash-matched files, rerun R49 until exactly one row passes,
then rerun R47 without weakening the source-backed discriminator.

`T-B1-004ez` / `T-B7-014i` closes the next mechanical blocker without
overclaiming the result: it binds the existing `O3-F4-C01` dataset, source
trace, replay environment, OpenQASM 3.0 source/candidate circuits, stdout,
unitary-distance witness, and an explicit verifier-signature blocker note into
a hash-matched pre-submission row. R49's file-hash failures drop from `8` to
`0`, while accepted source-backed rows remain `0`; empty production keys drop
to `2`; the three semantic blockers remain `source_backed_replay=false`,
`same_unitary_certificate=false`, and `smoke_only_not_c2_acceptance=true`.
Presubmission row hash
`3f7be50125146f8d4c68fd83f3d7526a25960e89b9584416e8fa6b5f2068059f`;
evaluation hash `da44c636972d9d407d1ed066e207813c405358c75cb97e8dcdf5f1db8ed7a50f`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false. The next useful PR must replace the smoke witness,
dry-run verifier, and signature blocker with source-backed replay evidence and
a real same-unitary verifier, then rerun R49 and R47.

`T-B1-004fa` / `T-B7-014j` fixes a preflight-gate semantics issue before the
next row can honestly pass. R49/R50 treated any production-required `False`
value as empty, but the required passing state for `smoke_only_not_c2_acceptance`
is exactly `false`. R51 emits a boolean-aware verifier: boolean production keys
are complete when present as booleans, and their accepted values are checked
only by `required_boolean_state`. Legacy semantics would mark a semantically
correct `smoke_only_not_c2_acceptance=false` row as having `1` empty key; the
boolean-aware verifier reduces that simulated empty-key count to `0`. On the
actual R50 row, empty production keys are now `0` and file-hash failures are
`0`, while the row is still rejected on the three real semantic flags:
`source_backed_replay`, `same_unitary_certificate`, and
`smoke_only_not_c2_acceptance`. Boolean-aware verifier hash
`0518bf37d62e8dc3a98801dcc7edac71d3ae548b907718a120c1cd55ec5b8f2f`;
evaluation hash `0e5f9400f588f2fa6b7baaeb7f40ddc31cfeb841c2583e21cc1757084b838bde`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004fb` / `T-B7-014k` converts the three remaining R51 semantic blockers
into a hash-bound evidence-triplet route for `O3-F4-C01`. R52 defines three
replacement slots: `E1-source-backed-replay-witness` for `source_backed_replay`,
`E2-real-same-unitary-verifier-transcript` for `same_unitary_certificate`, and
`E3-verifier-signature-artifact` for `smoke_only_not_c2_acceptance=false`.
The gate passes 8/8 requirements while rejecting direct promotion of the current
smoke witness, R40 dry-run verifier, and R50 signature blocker note. Current
evidence slots satisfied remain `0/3`; current blocker files present are `3`;
accepted source-backed rows remain `0`. Route hash
`77f3a833e73eb7556e484001da3e0b7abe63bca1c58455cf4d84424d51d823a7`;
route packet hash `f447c154a88e83744de319ce50802c3997efe00dc2931dd5becd395e0deaf8e2`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004fc` / `T-B7-014l` satisfies the first R52 evidence slot for
`O3-F4-C01`: `E1-source-backed-replay-witness`. R53 binds the R39 source
dataset, source trace, replay environment, OpenQASM 3.0 source/candidate files,
replay command, and replay stdout hash into a new E1 witness. The replay parses
the source and candidate `rz(0.125)` circuits and computes unitary distance
`0.0` under strict tolerance `1e-08`. E1 is now true, while E2 and E3 remain
false; accepted source-backed rows remain `0`. E1 witness hash
`541b1f8aebfd944e1d407f98d4954a98756963680cdcf252ceb992ecb8ccc22d`;
E1 replacement row hash
`f78eacf2d988b75147a110c644d65c7e885008bf9c618929ad60c772c30ffdd3`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004fd` / `T-B7-014m` satisfies the second R52 evidence slot for
`O3-F4-C01`: `E2-real-same-unitary-verifier-transcript`. R54 executes a
single-qubit RZ same-unitary verifier against the R53 E1 witness, records
command, version, input hashes, stdout hash, and transcript hash, and rejects
the old R40 dry-run verifier scope. The verifier recomputes unitary distance
`0.0` under strict tolerance `1e-08`. E1 and E2 are now true, while E3 remains
false; accepted source-backed rows remain `0`. E2 transcript hash
`6ff70effc8c22d07360a8dad3e252798ed705d6057b9953d9af1b39e0042da14`;
E2 replacement row hash
`f08207287159f6518294ddb8e8ab02a68048cc10a0c6b62849a2bee559106b44`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004fe` / `T-B7-014n` satisfies the third R52 evidence slot for
`O3-F4-C01`: `E3-verifier-signature-artifact`. R55 replaces the R50 signature
blocker note with a deterministic evidence signature bound to the R53 E1 witness,
the R54 E2 transcript, and the R54 E2 replacement row. E1, E2, and E3 are now
true; evidence slots satisfied are `3/3`; `smoke_only_not_c2_acceptance` is now
false in the E3 replacement row; accepted source-backed rows remain `0` because
R51 and R47 have not been rerun. E3 signature hash
`071454fcb51b9379f8fd084bde287509b53b3f574358690d82ef9e25084c15d0`;
E3 artifact hash
`fd08ea43b47f64855901e80e09166ce2592994a0628e352322d753c2052620b4`;
E3 replacement row hash
`aadfa0c9d89cbe4e8adbd76ca889e641914bdc2c8bbf67348093f027ff319573`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004ff` / `T-B7-014o` reruns the R51 boolean-aware preflight verifier on
the R55 E1/E2/E3 replacement row. R56 passes 8/8 requirements with missing keys
`0`, empty production keys `0`, malformed sha fields `0`, file-hash failures
`0`, flag failures `0`, schema passed true, and boundary tokens present true.
The R51 preflight accepts one row, but R47 has not been rerun and accepted
source-backed rows after the discriminator remain `0`. R51 verifier hash
`0518bf37d62e8dc3a98801dcc7edac71d3ae548b907718a120c1cd55ec5b8f2f`;
R56 evaluation hash
`50554cd4d0b936ee58d47e9c9084ced573aa328fb953f9fbe88bb6a7e5d0eb8d`;
R56 E3 row hash
`aadfa0c9d89cbe4e8adbd76ca889e641914bdc2c8bbf67348093f027ff319573`.
C2 remains unaccepted; O3, reroute, B7 credit, STV credit, and resource-saving
claims remain 0/false.

`T-B1-004fg` / `T-B7-014p` reruns the R47/R38 source-backed discriminator on
exactly the R56/R55 preflight-passing `O3-F4-C01` row. R57 passes 8/8
requirements and accepts exactly one source-backed row at the R47 discriminator
layer: row count `1`, materialized rows passed `1`, source-backed rows passed
`1`, source-backed flag failures `0`, source provenance failures `0`, witness
schema failures `0`, binding mismatch count `0`. R57 fixture hash
`d8c11f1daaedf3c6d434f4ebce92687a1795e008b15f76da1fc6139b79ba9936`;
R57 evaluation hash
`33b3749a7991a17ccf8b29697e08f204c145a485e5283c0ffa5d09c926ca4cff`;
R57 discriminator row hash
`c4bab44fe8e9c3499352fc9ed939f291810380a88ff744243f90760d331c711c`.
This is not full C2 closure: all-8 acceptance remains false, O3 remains open,
reroute remains false, and B7/STV/resource/ledger credit remain 0/false.

`T-B1-004fh` / `T-B7-014q` scales that same R47/R38 path from one row to all
8 O3-F4 C2 rows. R58 generates source-backed replay evidence packets,
same-unitary witnesses, verifier transcripts, signature artifacts, and
hash-bound discriminator rows for `O3-F4-C01` through `O3-F4-C08`, then reruns
the unchanged source-backed discriminator. It passes 8/8 requirements: row
count `8`, source-backed rows passed `8`, source-backed flag failures `0`,
source provenance failures `0`, witness schema failures `0`, binding mismatch
count `0`, and R47 all-8 acceptance true. R58 fixture hash
`d0d637b0c262f29dc0665ee0c33fe4a115cb774effe946cce6d65353376431b4`;
R58 evaluation hash
`fe7faded3f89bebd0a55d83ad273cf2925fcfcb6b314d47dac06f9fc4403f77d`;
discriminator hash
`9545943101fea7807122aa36c6c048dc742fce6af761c5229cd69b899b4cc99a`.
This is still not O3 closure and not B7 credit: C3 same-unitary replay
certificate, C4/C5 denominator comparison, C6 leakage-free trace, C7
machine-check replay, and B7 ledger retest remain open; reroute remains false
and B7/STV/resource/ledger credit remain 0/false.

`T-B1-004fi` / `T-B7-014r` now attacks the next C3 gate directly. R59
replays the all-8 R58 rows as single-qubit OpenQASM 3.0 `rz(theta)`
certificates and adds one perturbed negative control per row. It passes 8/8
requirements: row count `8`, positive replay certificates passed `8`,
negative controls rejected `8`, max positive replay distance `0.0`, minimum
negative-control distance `0.015624841054765663`, and restricted C3
same-unitary replay certificate complete true. R59 also records an important
audit observation: all 8 R58 evidence-packet semantic hashes still match, but
the R58 evidence-packet file SHA fields are stale after final row binding, so
R59 rebinds the actual file hashes instead of hiding the mismatch. R59 bundle
hash `fa7ab308e09644f3d58228a92ea580fb40f6ea88b8408cc75ddc21df79b84cbb`.
This is still not O3 closure and not B7 credit: C4/C5 denominator comparison,
C6 leakage-free trace, C7 machine-check replay, and B7 ledger retest remain
open; reroute remains false and B7/STV/resource/ledger credit remain 0/false.

`T-B1-004fj` / `T-B7-014s` now turns the next C4/C5 same-access denominator
step into a concrete submission contract instead of leaving it as a prose
blocker. R60 emits 8 row-level denominator templates, one per R59 certificate,
with 24 required acceptance fields per row. Each template is hash-bound to the
R59 source circuit, candidate circuit, and replay certificate, pins a
same-access model hash, forbids hidden optimizer traces, hardware calibration
data, unbound external oracles, and post-hoc angle edits, and requires a
verifier transcript plus leakage audit statement before any row can count.
R60 passes 8/8 contract requirements and contract hash
`2f1eea9d7fcc32e8cfeff6069d5fd351013b428586abff90c115c20b40812c2b`.
This is deliberately still not a denominator win: submitted denominator rows
`0`, accepted denominator rows `0`, C4/C5 comparison complete false, O3 open,
`reroute_allowed=false`, and B7/STV/resource/ledger credit remain 0/false.
The next useful PR must fill the R60 row templates with source-backed
same-access denominator evidence before C6, C7, or any B7 ledger retest.

`T-B1-004fk` / `T-B7-014t` now adversarially reviews that R60 contract. R61
constructs 8 metadata-only denominator-theater rows that satisfy every R60
required field, so a naive field-presence checker would accept `8/8`. The
hardened R61 checker rejects `8/8` because the rows have no existing
implementation path, no existing verifier transcript, unbound transcript SHA,
no replayed command, no structured leakage audit, self-asserted denominator
distance, and an overclaiming boundary. R61 emits 10 hardening rules under
schema `r61_c4_c5_same_access_denominator_row_hardened_v1`; bundle hash
`c86e614516aa87397edbc783a5db6895fd7574e1fc980a327941e954ecd50165`.
This is still not a denominator win: accepted denominator rows `0`, C4/C5
comparison complete false, O3 open, `reroute_allowed=false`, and
B7/STV/resource/ledger credit remain 0/false. The next useful PR should
implement the R61 hardened acceptance verifier, then submit real denominator
rows with existing implementation and transcript artifacts.

`T-B1-004fl` / `T-B7-014u` now turns the R61 hardening rules into an
executable acceptance verifier. R62 replays all 8 R61 metadata-only
denominator-theater rows against 10 hardened checks per row: required fields,
schema match, source/candidate/certificate hash binding, implementation path,
replayed command, transcript hash, transcript-bound distance, structured
same-access/leakage audit, transcript-derived pressure flags, and claim
boundary. The verifier emits 8 per-row transcripts, rejects `8/8` theater
rows, accepts `0/8`, has minimum failed checks per rejected row `7`, and
maximum passed checks per rejected row `3`. R62 bundle hash
`0900006a8639e0aa00e1d80c5cf3c5901520be262c0c930af2a4d5820245b6fd`.
This is still not a denominator win: accepted denominator rows `0`, C4/C5
comparison complete false, O3 open, `reroute_allowed=false`, and
B7/STV/resource/ledger credit remain 0/false. The next useful PR must submit
real source-backed C4/C5 denominator rows with existing implementation and
verifier transcript artifacts under the R62 verifier.

`T-B1-004fm` / `T-B7-014v` now submits those source-backed C4/C5 rows. R63
uses a reviewed same-access OpenQASM 3.0 single-`rz(theta)` denominator
verifier, replays 8 row commands, writes 8 denominator transcripts, writes 8
R62-compatible acceptance transcripts, and accepts `8/8` submitted denominator
rows. The max denominator distance is `0.0`; C4/C5 same-access denominator
comparison complete is true. R63 bundle hash
`7089f6070e7d5a75c57a765e3406f8199b1539b92ff23777159a8344e99c356f`.
This is still not O3 closure and not B7 credit: C6 leakage-free optimizer
trace and C7 machine-check replay remain open, `reroute_allowed=false`, and
B7/STV/resource/ledger credit remain 0/false. The next useful PR should run C6
leakage-free optimizer trace over the accepted R63 rows before any C7 or B7
ledger retest.

`T-B1-004fn` / `T-B7-014w` now completes that C6 leakage trace. R64 emits 8
hash-bound optimizer-trace audit files, one for each accepted R63 denominator
row, and checks command arguments, implementation hash, row hash, denominator
transcript hash, stdout hash, acceptance transcript, allowed-input scope,
row-specific pressure artifacts, and forbidden-input review. All 8 traces pass:
used inputs are limited to the template inputs plus row-specific pressure
artifacts, forbidden inputs used remain `0`, transcript/stdout hashes match,
and command arguments match the accepted rows. R64 bundle hash
`3fada7236ff61d0f015437d7b9562e1687c488a08db769369eca417a0fa5d61a`.
This is still not O3 closure and not B7 credit: C7 machine-check replay remains
open, `reroute_allowed=false`, and B7/STV/resource/ledger credit remain
0/false. The next useful PR should produce the C7 machine-check replay bundle
before any B7 ledger retest.

`T-B1-004fo` / `T-B7-014x` now completes that C7 replay for the current row
set. R65 reruns the same-access denominator verifier for all 8 accepted
R63/R64 rows, writes 8 replay transcripts, 8 replay stdout captures, and 8
machine-check replay verdicts, then compares stable semantic replay digests
against the original R63 transcripts. All 8 verdicts pass: replay commands exit
zero, semantic digests match, file hashes bind the R63 rows/R64 traces/original
transcripts/implementation, denominator distances remain `0.0`, negative
controls are rejected, and forbidden inputs remain unused. R65 bundle hash
`76544060858cd8f926c5823f2d2e30132935a1f855595316bafa1e19e29b2a39`.
This is still not O3 closure and not B7 credit: `reroute_allowed=false`, and
B7/STV/resource/ledger credit remain 0/false. The next useful PR should run a
zero-credit B7 ledger retest boundary before any promotion claim.

`T-B1-004fp` / `T-B7-014y` now runs that B7 zero-credit retest boundary. R66
binds the R65 machine-checked row set against the B7 resource boundary, the R4
ledger-replay block gate, and the current B7 FT synthesis ledger. The retest
packet covers 8 rows: all 8 are machine checked, 0 rows are ledger-credit
admissible, accepted exit routes remain `0`, occurrence removal remains `0`,
proxy-T reduction remains `0`, logical-T count/depth deltas remain `0`, and STV
delta remains `0`. R66 retest packet hash
`29d1cb2e95aafd29418e8082e0d8ab92edb1fe4ffa3a61af749204ad3294de59`.
This is a completed boundary, not a promotion: O3 closure, reroute permission,
B7 dependency/resource/FT/STV credit, resource saving, and ledger improvement
remain 0/false. The next useful PR must supply an accepted exit route or
full-circuit rewrite artifact with a nonzero occurrence/proxy-T delta before any
nonzero B7 ledger retest.

`T-B1-004fq` / `T-B7-014z` now turns that next step into a hash-bound accepted
exit-route submission contract. R67 emits three admissible route classes:
`R1-line1381-resolution`, `R2-line1378-overlap-recovery`, and
`R3-thirty-certificate-batch`. The contract requires 29 submission fields,
including source and candidate OpenQASM 3.0 paths and hashes, machine-check
replay command and stdout, semantic or symbolic equivalence evidence,
no-double-counting ledger evidence, line1381/line1378 evidence, occurrence and
proxy-T ledgers, nonzero deltas, and an explicit claim boundary. The placeholder
template is rejected with 23 placeholder fields, so accepted exit routes remain
`0`, accepted occurrence removal remains `0`, accepted proxy-T reduction remains
`0`, `b7_nonzero_retest_allowed=false`, and B7 credit remains `0`. R67 contract
hash `99e50d8c04bbb0b7435f4867d965b20376fd5c0685319a0b87a0ba9dad61f0a0`.
This is a contract gate, not an accepted route. The next useful PR must fill the
R67 template with source-backed replay, no-double-counting, line1381/line1378,
occurrence-delta, and proxy-T-delta evidence before any nonzero B7 ledger retest.

`T-B1-004fr` / `T-B7-015a` now pre-fills that contract against the evidence
already in the repository. R68 maps the R67 field set onto R1/R2/R5/R59/R66
artifacts and emits an R1 line1381 prefill draft, a three-route coverage matrix,
and a blocker queue. The R1 draft fills 24 of 29 required fields, but 5 fields
remain placeholders: source OpenQASM 3.0 path/hash, machine-check replay
command, replay stdout path, and replay stdout hash. Positive deltas also remain
absent: accepted exit routes `0`, occurrence removal `0`, proxy-T reduction
`0`, `b7_nonzero_retest_allowed=false`, and B7 credit `0`. R68 blocker queue
hash `510049cc66fa29b1cbce6610e9f61dcdedf20d020682a0b5a3a8b9d8eff02716`.
This is a prefill and blocker gate, not an accepted route. The next useful PR
must fill the missing source OpenQASM 3.0 and machine-check replay fields, then
submit a positive occurrence/proxy-T delta ledger before any nonzero B7 ledger
retest.

`T-B1-004fs` / `T-B7-015b` now resolves the source OpenQASM 3.0 part of that
prefill. R69 exports the original `gcm_h6` source circuit from OpenQASM 2.0 to
OpenQASM 3.0, verifies that the normalized instruction stream is preserved
(`1638` normalized instructions, stream hash
`75ad2565015b8abf1cc2024749a07f7bd15ddbeba568a08a445659d01c454b5a`), and
refreshes the R1 line1381 prefill. The draft moves from 24/29 fields to 26/29
fields. The remaining placeholder fields are now only the machine-check replay
triple: `machine_check_replay_command`, `machine_check_replay_stdout_path`, and
`machine_check_replay_stdout_sha256`. Positive deltas still remain absent:
accepted exit routes `0`, occurrence removal `0`, proxy-T reduction `0`,
`b7_nonzero_retest_allowed=false`, and B7 credit `0`. R69 blocker queue hash
`28b3f8e5d43a20e9315db4d576f6043547980e05421c14b5112e16f9f9d77292`.
This is still not an accepted route. The next useful PR must add a
machine-check replay command/stdout/hash, then submit positive occurrence and
proxy-T delta evidence before any nonzero B7 ledger retest.

B4/B8 now has a formal verifier-private challenge protocol model:
`T-B4-002b` / `T-B8-003f` turns the previous private-predicate pressure gate
into a commit-challenge-response-verify protocol over 36 shared challenge rows.
The analytic protocol passes 8/8 gates with hidden-private acceptance 0.0625,
public support-only acceptance 0.5, one-bit leakage acceptance 0.125, and full
private-material leakage acceptance 1.0. This is still not hardware execution,
cryptographic soundness, protocol soundness, sampling hardness, quantum
advantage, or a BQP separation.

`T-B4-002c` / `T-B8-003g` now pushes that protocol into a conservative
noise-modeled transcript bridge. It evaluates 720 transcript/noise/leakage
cases from 36 protocol rows, 4 noise profiles, and 5 leakage profiles.
Under the backend-like predicate-bit error profile, no-refresh honest
acceptance is 0.747047070414 and fails the 0.8 honest threshold, while
challenge refresh reaches 0.805169120213 and refresh plus rotation reaches
0.866618491942. No-leak adversary acceptance remains 0.0625, three-private-bit
leakage rises to 0.5, and full private-material leakage restores acceptance to
1.0. This is a transcript-noise pressure gate only; it still does not use real
backend properties, execute hardware, prove protocol soundness, prove sampling
hardness, claim quantum advantage, or separate BQP.

`T-B4-002d` / `T-B8-003h` adds a deterministic parametric learned/generative
spoofer-pressure diagnostic on top of that noise bridge. It covers 4 spoofer
families across 2,880 pressure rows. The result is intentionally negative:
the artifact is valid with 0 validation errors, but only 6/8 pressure gates
pass. Max no-leak spoofer acceptance reaches 0.1196875 and max backend-like
refreshed no-leak spoofer acceptance reaches 0.109140625, both above the 0.10
diagnostic pressure threshold. Three-private-bit leakage reaches 0.6575 and
full private-material leakage reaches 1.0. This is not actual ML training, real
backend evidence, hardware execution, protocol soundness, sampling hardness,
quantum advantage, or BQP separation.

`T-B4-002e` / `T-B8-003i` replaces that parametric-only warning with an actual
deterministic train/holdout fitted-spoofer diagnostic over the synthetic
transcript bridge. It trains on 560 transcript rows, holds out 160 rows by
protocol index, and evaluates 4 fitted model families across 640 model-row
checks. The private-safe no-leak calibrator stays at 0.0625, including
backend-like refreshed no-leak rows, while leakage-blind mixture fitting reaches
0.35 on no-leak holdout rows and full private-material leakage remains 1.0.
This means the immediate synthetic-transcript break is leakage contamination,
not private-safe no-leak fitting. It is still not real backend evidence,
hardware execution, protocol soundness, sampling hardness, quantum advantage,
or BQP separation.

`T-B4-002f` / `T-B8-003j` adds a real-backend transcript readiness guardrail.
It consumes the fitted-spoofer holdout result plus the B10-T2
GenericBackendV2-style calibrated Aer verifier bridge. The guardrail checks 10
requirements: 5 pass and 5 fail. The missing gates are real backend properties
(`R5`), hardware execution (`R6`), leakage-separated real-transcript fitting
(`R7`), leakage-blind no-leak acceptance below 0.10 (`R8`), and full
private-material leakage bounded below 0.25 (`R9`). The current evidence still
has 0 real backend transcript rows, private-safe no-leak fitted acceptance
0.0625, leakage-blind no-leak fitted acceptance 0.35, and full-private-material
leak fitted acceptance 1.0. This is not real-backend transcript readiness,
protocol soundness, cryptographic soundness, sampling hardness, quantum
advantage, or BQP separation.

`T-B4-002g` / `T-B8-003k` converts the failed readiness guardrail into a
real-backend transcript evidence contract. The contract checks 10 requirements:
5 pass and 5 fail. It preserves the same failed source gates (`R5`-`R9`) and
emits five PR packets: real backend properties, hardware execution,
leakage-separated real fitting, leakage-blind no-leak margin, and full-leakage
containment. The current state still has 0 real backend transcript rows,
leakage-blind no-leak fitted acceptance 0.35, full-private-material leakage
acceptance 1.0, and no protocol-soundness, hardware, advantage, or BQP claim.

`T-B4-002h` / `T-B8-003l` now adds a real-backend packet scout. The scout
consumes the contract, readiness guardrail, and fitted-spoofer holdout
evidence. It checks 9 scout requirements: 4 pass and 5 fail (`S5`-`S9`). It
maps all 5 real-backend PR packets, preserves 5760 backend-calibrated Aer
circuits, 640 fitted evaluation rows, and 160 holdout rows, but still records
0 real backend transcript rows, no real backend properties, no hardware
execution, and no leakage-separated real training. This is a sharper evidence
intake surface, not real-backend readiness, protocol soundness, sampling
hardness, quantum advantage, or BQP separation.

`T-B4-002i` / `T-B8-003m` now quantifies the real-backend soundness margin that
the next transcript PR must beat. It consumes the packet scout and checks 8
margin requirements: 5 pass and 3 fail (`M4`-`M6`). On the current 160-row
synthetic holdout, the private-safe no-leak fitted channel is 10/160 and passes
the <=16/160 no-leak budget. The leakage-blind no-leak channel is 56/160, so a
future real-row claim must remove at least 40 accepted cases or redesign the
split. Full private-material leakage is 160/160, so it must be explicitly
excluded or reduced to <=40/160. Real backend transcript rows remain 0, so this
is a margin ledger for the next PR, not protocol soundness, hardware evidence,
quantum advantage, or BQP separation.

`T-B1-004ft` / `T-B7-015c` now closes the R69 machine-check replay placeholder
gap for the R1 line1381 route prefill. It runs a deterministic replay command
that binds the source OpenQASM 3 artifact, candidate OpenQASM 3 artifact, R59
same-unitary certificate chain, R65 machine-check replay bundle, and R66
zero-credit ledger boundary. The R1 prefill moves from 26/29 fields to 29/29
fields, with replay stdout hash
`10de947944fa9e737a1d072bde67669df766159fd0444a8c723f7b2a9905fdd1`.
The structural CNOT delta remains 795 -> 789, but this is still not an accepted
exit route: accepted route count, occurrence removal, proxy-T reduction, and B7
credit all remain 0. The next required PR is a positive occurrence/proxy-T
delta ledger that can survive the R67 accepted-exit-route contract.

`T-B1-004fu` / `T-B7-015d` now turns that positive-delta requirement into an
executable verifier. R71 emits a 23-field positive-delta ledger contract, a
fillable template, a structural-only rejected fixture, and four PR packets for
line1381 occurrence delta, proxy-T derivation, line1378 no-double-counting, and
downstream B7 retest. The verifier passes its own 7/7 requirements and rejects
the structural-only fixture because `occurrence_removal_positive` and
`proxy_t_reduction_positive` fail. This means the 795 -> 789 CNOT signal is
preserved as useful evidence, but it is still not allowed to become accepted
route credit, proxy-T credit, or B7 credit without a source-backed positive
delta ledger.

`T-B1-004fv` / `T-B7-015e` now hardens that boundary with a source-backed
delta preflight. R72 fills a metadata-positive candidate row, then compares the
base R71 shape verifier against a stricter source-backed verifier. The base R71
verifier accepts the row, but the hardened verifier rejects it on 8 gates
because the R1 and R2 packets still fail P6/P7/P8 and the positive occurrence
and proxy-T fields are metadata-only. Requirements pass 7/7, accepted exit
routes remain 0, occurrence removal remains 0, proxy-T reduction remains 0, B7
credit remains 0, and the next work is to replace the metadata-positive row
with real R1/R2 source-backed artifacts.

`T-B1-004fw` / `T-B7-015f` now converts that replacement step into a source
closure intake contract. R73 maps the R72 D1-D3 blockers into 3 required
closure packets and 33 source-backed fields: R1 line1381 occurrence replay, R1
proxy-T pricing replay, and R2 line1378 no-double-counting or recovery replay.
The metadata-only fixture is rejected on 5 gates, including missing required
source artifacts, missing hash-bound artifacts, non-source-backed occurrence
derivation, non-source-backed proxy-T derivation, and non-source-backed
line1378 no-double-counting. Requirements pass 8/8, accepted exit routes remain
0, occurrence removal remains 0, proxy-T reduction remains 0, and B7 credit
remains 0.

`T-B1-004fx` / `T-B7-015g` now fills the first R73 source packet without
promoting it into credit. R74 turns the R73-D1 line1381 occurrence packet into a
hash-bound source-backed prefill: source OpenQASM3 line 1381 is
`cx q[3],q[15];`, the same candidate line is not a CNOT, source/candidate CNOT
counts remain `795 -> 789`, and the replay artifact, stdout, and verdict are
all materialized. The R73 intake now recognizes D1 as source-backed, but still
rejects the submission on 4 gates because D2 proxy-T pricing and D3 line1378
no-double-counting remain open. Requirements pass 8/8; accepted exit routes,
occurrence removal, proxy-T reduction, and B7 credit remain 0.

`T-B1-004fy` / `T-B7-015h` now fills the second R73 source packet without
promoting it into credit. R75 binds the locked R1
`line1381_unpriced_proxy_t_pressure_before = 100` value, emits a hash-bound
proxy-T pricing model, derivation artifact, replay stdout, and verdict, and
prefills D2 with a conservative replayable `100 -> 99` proxy-T pricing delta.
The R73 intake now recognizes D1 and D2 as source-backed, but still rejects the
submission on 3 gates because D3 line1378 no-double-counting remains open.
Requirements pass 8/8; accepted exit routes, occurrence removal, accepted
proxy-T reduction, and B7 credit remain 0.

`T-B1-004fz` / `T-B7-015i` now fills the third R73 source packet without
promoting it into credit. R76 binds the locked R2 overlap-additivity facts:
`line1378_window=[1369,1377]`, `line1381_window=[1369,1379]`, and
`line1378_window_contained_in_line1381=true`. It materializes a hash-bound
source artifact, no-double-counting ledger, replay stdout, and verdict, then
marks line1378 as `excluded_from_line1381_count` rather than double-counting the
contained window. The R73 source-closure intake shape now passes with D1/D2/D3
source-backed, but accepted exit routes, occurrence removal, accepted proxy-T
reduction, and B7 credit remain 0. The next gate is a hardened R72/R73 rerun,
not a resource or B7 promotion.

`T-B1-004ga` / `T-B7-015j` now completes that hardened R72/R73 rerun after
R76. R77 consumes the R72 preflight baseline plus the R76 D1/D2/D3
source-closure submission and proves the source-closure axis is no longer the
active blocker: R73 intake is accepted, D1/D2/D3 are prefilled, and all
hash-bound packet artifacts match. The promotion still fails exactly where it
should: accepted exit route, accepted occurrence removal, and accepted proxy-T
reduction remain 0, so `b7_nonzero_retest_allowed=false`, B7 credit remains 0,
and O3/reroute/resource claims remain blocked. Requirements pass 8/8; the next
useful artifact is a real accepted positive-route packet, not another
source-closure packet.

`T-B1-004gb` / `T-B7-015k` now turns that next artifact into a concrete
contract. R78 emits the positive-route packet contract, template, current-empty
preflight verdict, stdout, and blocker queue. The contract targets exactly the
three post-R77 promotion gates: `accepted_exit_route_positive`,
`accepted_occurrence_positive`, and `accepted_proxy_t_positive`, while preserving
the R76 no-double-counting ledger. The current template is intentionally
rejected on 5 gates with 15 missing production fields; accepted exit routes,
occurrence removal, accepted proxy-T reduction, B7 nonzero retest permission,
and B7 credit remain 0/false. Requirements pass 8/8; the next useful PR must
fill R78-A/B/C/D with replay, certificate, occurrence, proxy-T, and
no-double-counting preservation evidence.

`T-B1-004gc` / `T-B7-015l` now fills the R78-A route/replay/certificate surface
without overclaiming acceptance. R79 consumes the R70 machine-check replay
prefill and maps its candidate OpenQASM3 artifact, replay stdout, and
same-unitary/symbolic certificate into a partial R78 packet while preserving the
R76 no-double-counting verdict. Missing R78 production fields drop from 15 to
4: only occurrence acceptance ledger path/hash and proxy-T acceptance ledger
path/hash remain missing. The partial packet is still rejected on 5 gates,
including all three positive-promotion gates, so accepted exit routes,
occurrence removal, accepted proxy-T reduction, and B7 credit remain 0.

`T-B1-004gd` / `T-B7-015m` now removes the remaining field-completeness blocker
without promoting the route. R80 materializes hash-bound occurrence and proxy-T
acceptance ledgers, inserts them into a new R78 packet, and reruns the
preflight. Missing production fields drop from 4 to 0 and all hash-bound
artifacts match, but the packet remains rejected exactly on
`accepted_exit_route_positive`, `accepted_occurrence_positive`, and
`accepted_proxy_t_positive`. Accepted exit routes, occurrence removal, accepted
proxy-T reduction, and B7 credit remain 0; the next work must produce a real
positive occurrence/proxy-T ledger rather than another surface-completion patch.

`T-B1-004ge` / `T-B7-015n` now promotes that completed packet into one accepted
B1 route without granting B7 credit. R81 replaces the R80 zero ledgers with
source-backed positive ledgers: R74 proves line 1381 is a source `cx` while the
candidate same line is not a CNOT, R75 binds the replayed proxy-T delta
`100 -> 99`, and R76 preserves the no-double-counting decision that excludes
line 1378 from a second count. The R78 packet preflight now passes all gates:
accepted exit routes `1`, accepted occurrence removal `1`, accepted proxy-T
reduction `1`. O3 closure, reroute permission, resource saving, and B7 credit
remain blocked until a downstream B7 resource/FT ledger retest accepts the
R81 packet.

`T-B1-004gf` / `T-B7-015o` now completes that downstream B7 retest without
promoting the result into a B7 win. R82 consumes the R81 accepted B1 route as a
candidate B7 input, maps its one-unit proxy-T reduction into a candidate
logical-T delta, and compares it against the current `gcm_h6` FT boundary. The
current B7 ledger still needs 592 additional T-ledger units removed to reach the
1.20x STV target and 824 units for the 1.25x target; after R81 those gaps are
591 and 823. The R82 gate passes 8/8 requirements, marks the downstream retest
complete, and keeps accepted B7 dependency/resource/FT/STV credit at `0`.
Ledger hash `20c28c61dfa70b040207feb0ff4d503232fbc6ea186701b4622c7278401da4b9`;
verdict hash `c49d3f1ac0efaab7cf46af674014ad0231b19878e44f65c9aa6d8fd164bc4460`;
blocker queue hash `1ed204037a6e2b2184b45a74f87d87a35f2e48fda9c81ec89e3abfaa9106534c`.
This closes the vague "run B7 retest" blocker and replaces it with a quantified
gap: the next useful PR must remove at least 591 additional T-ledger units or
provide an equivalent full B7 reprice before any nonzero B7 credit can be
claimed.

`T-B1-004gg` / `T-B7-015p` now turns that quantified gap into a fillable
contract for future PRs. R83 consumes the R82 zero-credit B7 retest, freezes the
1.20x STV acceptance threshold at a minimum `591` additional T-ledger units, and
emits a 33-field production contract with 10 acceptance gates. The placeholder
template is rejected, as intended, with 8 failed gates and accepted B7 credit
still `0`. R83 also emits three PR-sized work packets: remove or reprice 30
arbitrary rotations at cost 20 each, submit a 591-unit source-backed proxy-T
row batch, or provide an equivalent full B7 reprice. Contract hash
`3c306524d0fa44b789b6723608d8f919c1847dcce622ca90104b1d9af51f7c43`;
template-preflight hash `baf9b75a5a642101b01525962bc2257f63949311e77e268ce1e6ac15a9ff6acb`;
work-packet hash `ef857b3f327fc6d8fa0a4dbc9a7ee97af3378b219341f5a038412fd80d06785a`;
blocker queue hash `6bb240d44071e90a9d10ebdc7065fa571b1861fe9e860d6ab9ce8fa769bf3ab0`.
This is still not O3 closure, reroute permission, resource saving, or B7
credit. It is the mergeable surface for the next agents to attack.

`T-B1-004gh` / `T-B7-015q` now triages those three R83 work packets into a
single next-PR route. R84 ranks all three packets, preserves the 33-field R83
contract, and selects `R83-G1-30-arbitrary-rotation-batch` as the next target:
30 source-backed arbitrary-rotation removals or reprices would supply `600`
candidate T-ledger units against the `591` unit 1.20x gap, leaving `9` units of
margin before downstream B7 replay. The priority packet keeps
`accepted_b7_credit_delta=0`, `o3_closed=false`, `reroute_allowed=false`, and
`resource_saving_claimed=false`. Triage hash
`ff01f24e5d4f73dd17ba0352d204db9c91380bab274098702ea0fe85d14309d0`;
priority-packet hash `a2e76353b571b7b99acee9af9598f1fa54fb493c07204625e3d643081549ce62`;
blocker queue hash `c4f914bf6e0bc686be94032af2fe83203742a760f9a0c6244d81932541cb4c41`.
This is still not a filled R83 submission. It simply tells the next builder
agent exactly which evidence packet should be filled first.

`T-B1-004gi` / `T-B7-015r` now materializes that selected G1 route into a
source-backed row intake. R85 uses the same B7 rotation-family classifier that
reports `270` arbitrary numeric rotations for `gcm_h6`, extracts the first `30`
arbitrary components in QASM order, and binds each row to a source line,
component id, angle expression, qubit, and line hash. The candidate mapping is
`30 * 20 = 600` T-ledger units, which would reach the R84 selected target if a
future filled R83 submission accepts every row. The no-double-counting screen
passes for unique source components, but the preflight intentionally rejects
credit on four missing gates: replay stdout, STV reprice ledger, filled R83
submission, and downstream B7 replay. Source-rows hash
`0a56014b1b0d8efb3bb866a63c2e0a182255ca306addd2ffd1b75e616fc8d2db`;
candidate-mapping hash `cddd98736eb312fba1fb063342f9cf38aa21283e0aa5163d7002ef477cc9a47c`;
preflight hash `3f7cf84f8243e83442e06dcaad662b6bdbcda129158e6560b415e953f3dbb846`.
B7 credit remains `0`.

`T-B1-004ho` / `T-B7-016x` now adds the R117 independent NumPy replay gate.
R117 re-parses the R116 source and candidate OpenQASM with a separate NumPy
statevector engine, without calling Qiskit for compilation or simulation. It
checks 30 finite inputs: zero, 13 computational-basis states, 8 full random
states, and 8 random product states. All `30/30` pass with maximum fidelity
deficit `1.33e-15`; the terminal measurement map remains identical; CX remains
`762 -> 528` (`30.7087%`). This is cross-implementation finite-probe evidence,
not an arbitrary-input unitary proof; hardware layout, T-resource, and B7
credit remain outside the claim boundary. Requirements pass `10/10`; B7 credit
remains `0`.

`T-B1-004hp` / `T-B7-016y` now adds the R118 randomized channel fingerprint
gate. An independent NumPy engine replays the R116 source/candidate pair over
160 cross-type inputs: 32 computational-basis, 64 Haar-like, 32 product,
16 endpoint-entangled, and 16 biased states. All `160/160` candidate probes
pass with maximum fidelity deficit `2.44e-15`; a deliberately inserted `X`
negative control fails `16/16`, showing that the harness detects a semantic
perturbation. CX remains `762 -> 528`, but this is still finite numerical
evidence, not an exact arbitrary-input unitary proof, hardware result,
T-resource reduction, or B7 credit.

`T-B4-002s` / `T-B8-003w` / `T-B10-009k` now adds the R118 randomized
measurement-data boundary. R118 replaces toy parity samples with three
six-qubit state-preparation circuits, randomized X/Y/Z measurement bases, 60
trials per adversary, 1,024 shots per trial, and 8 hidden target observables.
Honest completeness reaches the diagnostic floor `0.80`, but maximum adversary
soundness is `1.0`: marginal matching and a public all-plus basis strategy can
still pass some hidden-observable rows. This is an accepted negative boundary,
not a protocol-soundness result; hardware execution, calibrated backend
evidence, quantum advantage, BQP, and B10-T2 credit remain false. Requirements
pass `10/10`.

`T-B4-002t` / `T-B8-003x` / `T-B10-009l` now adds the R119 private signed
observable bundle. After collecting the randomized measurement data, the
verifier selects a hidden bundle containing one negative correlation, one
cross-half positive correlation, and one random positive correlation. On two
ideal six-qubit entangled tasks, honest completeness is `0.85`, maximum
adversary soundness is `0.0333`, and all `8/8` task/adversary rows are at or
below the `0.05` target. This is scoped simulator evidence, not general
protocol soundness; calibrated noise, hardware execution, quantum advantage,
BQP separation, and B10 credit remain unclaimed. Requirements pass `10/10`.

`T-B4-002u` / `T-B8-003y` / `T-B10-009m` now adds the R120 explicit Aer noise
replay. The R119 bundle is replayed at a fixed 1,024-shot budget under
ideal/light/moderate/stress profiles. Minimum honest completeness is
`0.75/0.45/0.60/0.55`; no profile reaches the `0.80` floor. The ideal baseline
itself misses the floor, so shot budget is a blocker before calibrated backend
evidence can be interpreted. This is synthetic simulator evidence only; no
hardware, protocol soundness, quantum advantage, BQP, or B10 credit is claimed.
Requirements pass `10/10`.

`T-B4-002v` / `T-B8-003z` / `T-B10-009n` now adds the R121 shot-budget
sweep. The R120 private bundle is replayed at `512/1024/2048/4096/8192`
shots under ideal and light Aer profiles, with `12` trials per task/budget.
Minimum honest completeness by budget is ideal
`0.5/0.6666666666666666/0.5/0.8333333333333334/0.9166666666666666` and light
`0.25/0.5833333333333334/0.75/1.0/0.8333333333333334`. Both profiles first
cross the `0.80` floor at `4096` shots in this seeded run; intermediate values
fluctuate, so this supports shot-budget sensitivity, not a monotonic noise law.
Matched-seed repeats and calibrated backend evidence remain open. Requirements
pass `10/10`; hardware, protocol soundness, quantum advantage, BQP, and B10
credit remain unclaimed.

`T-B4-002w` / `T-B8-003aa` / `T-B10-009o` now adds the R122 matched-seed
prefix replay. Each of `30` trials per profile/task generates one ordered
`8192`-shot stream and evaluates `512/1024/2048/4096/8192` prefixes with the
same measurement schedule and hidden observable bundle. The weakest-task point
estimates are ideal `0.4333/0.5333/0.6667/0.8667/0.9667` and light
`0.4333/0.6667/0.5667/0.8000/0.8667`; both first cross `0.80` at `4096` shots.
The 95% Wilson lower bounds are ideal
`0.2738/0.3614/0.4878/0.7032/0.8333` and light
`0.2738/0.4878/0.3920/0.6269/0.7032`, so only ideal at `8192` is
confidence-qualified and light never qualifies in this run. The paired ledger
contains `49` fail-to-pass and `20` pass-to-fail adjacent transitions. This is
stronger shot-budget evidence, not a monotonic law or soundness result.
Requirements pass `10/10`; hardware, calibrated backend, advantage, BQP, and
B10 credit remain unclaimed.

`T-B4-002x` / `T-B8-003ab` / `T-B10-009p` now adds the R123 independent-seed
block replay. Five distinct root-seed blocks run `12` paired trials per
profile/task at the critical `4096/8192` prefixes, producing `240` trial rows.
At `8192`, all five blocks clear the point-estimate floor in both profiles and
the pooled 95% Wilson lower bounds are ideal `0.8193` and light `0.8630`.
The stricter minimum leave-one-block-out lower bounds are ideal `0.7783` and
light `0.8316`, so only the light profile remains confidence-qualified after
every single-block deletion. The ledger records `18` fail-to-pass and `3`
pass-to-fail transitions. This isolates a block-robustness gap; it does not
establish a universal shot threshold, iid law, hardware evidence, protocol
soundness, advantage, BQP separation, or B10 credit. Requirements pass `10/10`.

`T-B4-002y` / `T-B8-003ac` / `T-B10-009q` now adds the R124 publicly
preregistered holdout replay. Discussion #124 publishes contract SHA-256
`18da0e4fe50a98f2830782c04563102371a608e87a0e5859c9b5a65839693604`
before execution, fixing five disjoint root seeds, `16` trials per
block/profile/task, the `4096/8192` paired budgets, and five acceptance
conditions. At `8192`, ideal/light pooled Wilson lower bounds are
`0.9134/0.8784`, minimum leave-one-block-out lower bounds are
`0.8930/0.8500`, and all `5/5` blocks clear the point floor. The paired ledger
records `26` fail-to-pass and `0` pass-to-fail transitions. Both profiles pass
A1-A5, so the global preregistered synthetic holdout verdict is `ACCEPT`.
This unlocks calibrated-backend-property or independent-backend-transcript
replay only; it does not establish a universal threshold, hardware result,
protocol soundness, advantage, BQP separation, or B10 credit. Requirements
pass `12/12`.

`T-B4-002z` / `T-B8-003ad` / `T-B10-009r` now adds the R125 historical QPU
snapshot replay. Discussion #126 preregisters contract SHA-256
`547bef430ce85ea9052d791edd939e554b4a72f67dcabbb61169c7e02a675716`,
three Qiskit IBM Runtime `0.46.1` fake-backend snapshot hashes, five disjoint
seed blocks, `16` trials per block/snapshot/task, and the unchanged A1-A5
rules. R125 transpiles `4374` randomized-measurement basis circuits to the
FakeOslo, FakeJakartaV2, and FakeLagosV2 targets and emits `480` paired trial
rows. At `8192` shots, weakest point/Wilson/leave-one-block-out values are
Oslo `0.8625/0.7703/0.7179`, Jakarta `0.8000/0.6995/0.6487`, and Lagos
`0/0/0`. No snapshot passes all five conditions; the global verdict is
`REJECT`, with `38` fail-to-pass and `6` pass-to-fail transitions. Extra shots
therefore do not repair this historical topology/readout boundary. These are
frozen historical system properties for local Aer testing, not current
calibration, provider access, hardware execution, soundness, advantage, BQP
separation, or B10 credit. Requirements pass `13/13`.

`T-B4-002aa` / `T-B8-003ae` / `T-B10-009s` now adds the R126 calibration
attribution ledger. It consumes all `480` fixed R125 rows without rerunning or
tuning the failed holdout, parses six representative OpenQASM 3 circuits, and
emits six snapshot/task attribution rows, `60` hidden-bundle strata, `30`
seed-block strata, seven descriptive correlations, and four mitigation
packets. FakeOslo/FakeJakartaV2 graph tasks pass `80/80`, while their routed
11-CX GHZ tasks pass `69/80` and `64/80`. FakeLagosV2 has readout-any-error
proxy `0.6702`; its GHZ/graph tasks pass only `1/80` and `0/80`. Combined
exposure versus candidate pass rate has descriptive Spearman rho `-0.8407`
over only six rows, so R126 does not promote a causal claim. No mitigation is
tested and the R125 holdout is not reused for acceptance. The next gate is a
public preregistration for physical-qubit selection, routing/readout ablation,
and disjoint readout mitigation; hardware, soundness, advantage, BQP, and B10
credit remain unclaimed. Requirements pass `10/10`.

`T-B4-002ab` / `T-B8-003af` / `T-B10-009t` now adds the R127
calibration-aware layout design gate. It enumerates all `30240` injective
six-logical-to-seven-physical mappings using frozen snapshot measurement/CX
properties and each task's interaction graph, retains `60` top candidates,
and transpiles one selected all-Z representative for every snapshot/task pair.
Only `3/6` graph layouts reduce compiled exposure. All three GHZ candidates
worsen because compiled CX count rises from `11` to `14`; mean compiled
exposure delta is `-0.00503`, so the layout design gate fails. The result shows
that the static calibration objective is not transpiler-invariant and the next
selector must rank actual compiled candidates. No acceptance holdout or
readout mitigation is executed, R125 is not reused for acceptance, and current
calibration, hardware, soundness, advantage, BQP, and B10 credit remain
unclaimed. Requirements pass `10/10`.

`T-B4-002ac` / `T-B8-003ag` / `T-B10-009u` now adds the R128
transpiler-in-the-loop layout ranking gate. It reranks all `60` retained R127
candidates over five fixed transpiler seeds, producing `300` candidate and
`30` same-condition automatic-layout compilations. The compiled objective
replaces three static rank-one layouts; `5/6` groups improve mean exposure and
`6/6` improve worst exposure. However, only the Lagos graph task beats the
automatic layout in at least four of five seeds, while Jakarta GHZ remains
worse on mean exposure and carries `14` CX versus the automatic layout's `11`.
The strict routing-survival gate therefore fails and no new holdout is opened.
R125 acceptance rows are not read, and no mitigation, current calibration,
hardware, soundness, advantage, BQP, or B10 credit is claimed. Requirements
pass `10/10`.

`T-B4-002ad` / `T-B8-003ah` / `T-B10-009v` now adds the R129
seed-robust layout ranking gate. The selector is trained on eight fixed
transpiler seeds using the lower `20%` paired exposure gain before win count
and mean gain, then evaluated on ten disjoint seeds that are not compiled until
after selection. Across `708` compilations, the robust objective changes one
of six R128 selectors. Four groups retain positive unseen mean gain, but only
Lagos graph has positive unseen lower-tail gain and wins at least `8/10` seeds;
it wins `10/10`. Jakarta GHZ improves over the R128 selector but remains
negative on mean gain and wins only `3/10`. The robust unseen-seed gate fails,
showing that the retained static Top-10 candidate set needs route-signature
expansion rather than another weight adjustment. No R125 acceptance rows,
verifier holdout, mitigation, current calibration, hardware, soundness,
advantage, BQP, or B10 credit is used or claimed. Requirements pass `10/10`.

`T-B4-002ae` / `T-B8-003ai` / `T-B10-009w` now adds the R130
route-signature candidate expansion gate. It enumerates all `30240` injective
mappings, identifies `6720` route signatures, and retains `312` candidates
covering `282` signatures. Every GHZ snapshot covers all `42/42` available
signatures, while each graph snapshot retains `52` distinct signatures. The
expanded pool is trained and evaluated with new disjoint seed blocks across
`2724` compilations. Two selectors change. Lagos GHZ moves to static rank
`241`, improves unseen mean gain to `+0.0116`, and wins `5/10`, but its lower
tail remains slightly negative at `-0.00015`. Only Lagos graph remains robust
at `10/10`; the global route-expansion gate fails. This rejects the simple
claim that Top-10 width alone caused R129 and moves the next gate to exact
compiled-route-family analysis. No verifier holdout, mitigation, current
calibration, hardware, soundness, advantage, BQP, or B10 credit is used or
claimed. Requirements pass `10/10`.

`T-B4-002af` / `T-B8-003aj` / `T-B10-009x` now adds the R131 exact
compiled route-family attribution boundary. It recompiles selected and
automatic layouts on the `60` already-used R130 compiler-diagnostic rows,
byte-matches selected QASM `60/60`, and replays exposure deltas `60/60`.
Stable directed CX-edge-multiset and exposure equivalence identifies `9`
selected and `33` automatic route-exposure classes. Automatic layout switches classes in
all `6/6` groups. Selected layout remains in one family in `4/6` groups, and
their outcome instability is attributable to automatic-family switching;
Jakarta GHZ and graph also switch selected families and need a separate route
determinism constraint. Cross-process replay also shows that exact ordered
default routes can drift despite fixed transpiler, Python-hash, and native-thread
settings, while the route-exposure class ledger remains identical. R131 therefore
freezes default QASM as observed samples and explicitly does not claim exact
ordered-route reproducibility. It opens no new seed block and performs no selection
or acceptance. It is post-hoc compiler attribution, not a causal hardware,
soundness, advantage, BQP, or B10 claim. Requirements pass `10/10`.

`T-B4-002ag` / `T-B8-003ak` / `T-B10-009y` now adds the R132
topology-constrained route-policy boundary. Four policies are compared over `240`
fresh training compilations; the global training-only selector chooses
`selected_o3_lookahead`. A disjoint block then performs `180` validation
compilations against the original selected-layout route and Qiskit's automatic
layout. The constrained route occupies one route-exposure class and one exact
QASM hash in all `6/6` groups, and all `60/60` frozen validation circuits replay
byte-for-byte in a fresh process. Mean and lower-tail exposure do not regress
against the original selected-layout reference in `6/6` groups. This resolves
the R131 reproducibility defect, but not the baseline-quality problem: only
`3/6` groups avoid every loss against automatic layout, and aggregate outcomes
are `27` wins, `19` ties, and `14` losses. The compiler stability gate passes;
verifier acceptance, mitigation, current calibration, hardware, soundness,
advantage, BQP, and new B10 credit remain excluded. Requirements pass `10/10`.

`T-B4-002ah` / `T-B8-003al` / `T-B10-009z` now adds the R133 unseen
circuit-family holdout boundary. Four source families absent from R119-R132
(star echo, star phase, ring phase, and brickwork) are compiled on three
historical fake backends over ten fresh seeds. The upstream R130 mappings and
R132 `selected_o3_lookahead` policy are frozen before the `360` holdout
compilations. All `12/12` backend/circuit groups retain one route-exposure
class and one exact QASM hash; `120/120` constrained circuits replay
byte-for-byte in a fresh process. Determinism therefore generalizes, but cost
quality does not: only `4/12` groups avoid every automatic-layout loss, with
`21` wins, `24` ties, and `75` losses. The attribution ledger assigns `46`
losses to an inherited fixed-mapping gap not recovered by lookahead, `20` to
combined mapping and policy regression, and `9` to lookahead-only regression.
The automatic-baseline no-loss gate fails. No holdout selection, verifier
acceptance, hardware, soundness, advantage, BQP, or new B10 credit is claimed.
Requirements pass `10/10`.

`T-B4-002ai` / `T-B8-003am` / `T-B10-009aa` now adds the R134
family-agnostic deterministic mapping boundary. Four graph-embedding rules each
enumerate all `5,040` six-to-seven-qubit injections using only circuit
interaction weights, historical coupling distance, path-error pressure, and
readout error. R133 circuits plus `240` fresh design compilations select
`weighted_distance`; validation is then isolated on four new QFT, K3,3-QAOA,
tree-phase, and RXX-cycle families over `360` compilations. All `12/12` groups
remain route- and exact-QASM-invariant, and `120/120` frozen circuits replay in
a fresh process. The generic mapper improves the unseen-family comparison from
R133's `75` losses and `4/12` no-loss groups to `54` losses and `6/12` no-loss
groups, with `28` wins and `38` ties. It still fails the automatic-baseline
no-loss gate: QFT loses `10/10` on every backend, and Jakarta/Lagos RXX or K3,3
rows retain losses. No verifier acceptance, hardware, soundness, advantage,
BQP, or new B10 credit is claimed. Requirements pass `10/10`.

`T-B4-002ak` / `T-B8-003ao` / `T-B10-009ac` now adds the R136
route-realization lower-tail margin boundary and records the first dense-family
automatic-layout no-loss pass in this line. R135's seven residual loss margins
range from `2.77e-5` to `5.64e-3`. Without reading those loss rows, R136 takes
the top eight R135 mapping/policy candidates per group and recompiles each under
`16` fresh route-realization seeds. The resulting `1,536` realizations are
ranked before a disjoint ten-seed automatic baseline is opened. Across `1,656`
total compilations, eight of twelve groups improve over the R135 selected
exposure, all `12/12` groups are loss-free, outcomes are `116` wins, `4` ties,
and `0` losses, and selected QASM replays `12/12` byte-for-byte in a fresh
process. The compiler-level no-loss gate passes. This is not yet verifier
acceptance: no private-challenge execution, transcript soundness test, current
calibration, hardware, quantum advantage, BQP separation, or new B10 credit is
claimed. Requirements pass `10/10`.

`T-B4-002al` / `T-B8-003ap` / `T-B10-009ad` now adds the R137
artifact-bound private-challenge integrity boundary. R137 commits to the exact
12 R136 OpenQASM 3 artifacts, their parsed semantic fingerprints, the R136
result hash, the protocol nonce, and the full compiler-cost ledger before 48
late-bound probes are generated. Every artifact receives one byte-range, source
window, operation-count, and structural challenge. The positive transcript is
accepted with 48/48 responses, all five phase artifacts replay byte-for-byte in
a fresh process, and 10/10 artifact-substitution, response-swap, nonce-replay,
secret-substitution, challenge-deletion, cost-underreporting, response-forgery,
precommit-leakage, artifact-omission, and duplicate-response attacks are
rejected. The ledger charges all 1,536 route-realization compilations, 120
automatic validation compilations, and 128 selection attempts per frozen
artifact. This accepts local artifact integrity only. It is not externally
timestamped preregistration, independent secret custody, statistical
performance acceptance, hardware execution, protocol or cryptographic
soundness, quantum advantage, BQP separation, or new B10 credit. Requirements
pass `10/10`.

`T-B4-002am` / `T-B8-003aq` / `T-B10-009ae` preregisters the R138
post-commit statistical challenge before any challenge secret or trial row
exists. The fixed contract binds the public R137 commit and commitment hash,
all 12 selected-QASM hashes, 96 paired trials, 4,096 shots per circuit, matching
historical FakeBackend noise, squared Hellinger fidelity to the exact logical
distribution, and eight immutable acceptance conditions. The primary paired
mean noninferiority floor is `-0.005`; the bootstrap 95% lower floor is
`-0.0125`; at least 10/12 groups must remain above `-0.025`; and at most two
rows may fall below `-0.05`. Execution is intentionally unopened at this
commit. Thresholds may not change after publication, and a rejection must be
reported rather than repaired after seeing the holdout. The contract was then
published in commit `17012a4a5706eca8ec3c650c3e2a72bbfa82c80c` and Discussion
`#140` before challenge generation. The executed holdout accepts all `8/8`
conditions: 96 paired rows over 786,432 simulated shots produce mean selected
and automatic Hellinger fidelities `0.85347188` and `0.84992130`, for paired
delta `+0.00355058`; the 10,000-resample 95% interval is
`[+0.00137647,+0.00577807]`. Outcomes are `64/0/32`, all `12/12` group means
remain above `-0.025`, and no row falls below `-0.05`. The Lagos complete-Ising
group still has a negative mean delta of `-0.01399989`, so this is a scoped
synthetic-noise noninferiority acceptance, not uniform superiority. Four phase
artifacts replay `4/4`; requirements pass `10/10`. No current calibration,
hardware, mitigation, independent custody, soundness, quantum advantage, BQP,
or new credit is claimed.

`T-B4-002an` / `T-B8-003ar` / `T-B10-009af` now adds the R139
Lagos complete-Ising channel attribution boundary. It reuses the eight revealed
R138 circuit/seed pairs and executes 32 paired channel rows under full,
gate-only, readout-only, and noiseless models. The full-noise mean delta exactly
replays `-0.01399989`; gate-only shrinks to `-0.00033016`, readout-only expands
to `-0.02365719`, and noiseless sampling is `+0.00008690`. All compiled circuits
retain exact semantic fidelity of at least `0.9999999999999984`. An analytic
output-aware readout channel using each logical bit's actual physical
measurement assignment produces mean delta `-0.02286062`, agrees with sampled
readout ranking signs `8/8`, and reaches correlation `0.98493343`. The old
combined-error proxy prefers the selected route while exact output-aware
readout prefers automatic routing in `6/8` rows. This supports a synthetic
output-aware readout-assignment attribution, not hardware causality or a
mapping repair. Phase replay passes `2/2`; requirements pass `10/10`; hardware,
mitigation, soundness, advantage, BQP, and new credit remain excluded.

`T-B4-002ao` / `T-B8-003as` / `T-B10-009ag` now freezes the R140
parameter-free output-aware mapping design before noisy validation. R140
recompiles and hash-checks all `1,536/1,536` R136 route realizations, then ranks
each candidate by `(1 - cx_any_error_proxy) *
exact_output_aware_readout_fidelity`. It fits no weight and reads zero R138 or
R139 validation rows. Four of twelve selections change; Lagos complete-Ising
moves from `[5,3,6,4,1,0]` to `[1,3,2,0,5,4]`, improves exact readout fidelity
by `0.00408986`, lowers CX-any-error pressure from `0.51115694` to
`0.42900958`, and raises the design score by `0.07231395`. All twelve selected
QASM files replay across a second process and retain exact semantic fidelity at
least `0.9999999999999976`. The unopened holdout contract hash is
`d11f07b5d5a25c81a3f89a1b03297deb1a80486ce3613d1c17d3071e651a7cb5`;
it fixes 96 fresh three-arm trials and ten immutable acceptance conditions.
This is a frozen design and preregistration, not a validated repair.

The R140 holdout at `T-B4-002ap` / `T-B8-003at` / `T-B10-009ah`
then executes 96 fresh three-arm rows and 1,179,648 synthetic shots after public
commit `9b39d062...` and Discussion #143. The verdict is `REJECT`: 9/10 fixed
conditions pass, but A4 fails. Lagos complete-Ising changes from negative to
positive against automatic compilation (`+0.00340156`) and wins `4/8`, while
the new route improves on the old frozen route by only `+0.00103058`, below the
preregistered `+0.01` materiality floor. Portfolio new-minus-automatic is
`+0.00582195` with bootstrap lower `+0.00405345`; new-minus-old is
`+0.00024811`; all 12/12 groups avoid a `-0.01` mean regression and severe row
regressions are 0. The sign repair is real under this synthetic model, but its
increment over the previous route is too small to count as a validated repair.
Requirements pass 10/10 and phase replay passes 4/4; all downstream credit
remains zero.

`T-B4-002aq` / `T-B8-003au` / `T-B10-009ai` now freezes the R141
fixed-width hashed-output-sketch design before noisy validation. The selector
uses 256 histogram buckets, 4,096 pilot samples, and eight shared readout
replicas per sample; it receives no full output-distribution table. Across 16
independent pilot blocks per backend/task group, it matches the R140 exact
selection in 171/192 cases and in 16/16 Lagos complete-Ising cases. Mean exact
R140 score regret is `0.00006503`, maximum regret is `0.00207426`, and all 12
selected OpenQASM 3 artifacts replay exactly. The immutable four-arm holdout
contract hash is
`388fb1aa35ae98d2c5f624e34541832e8590481046b42af105e57be63d6a770f`;
it fixes 96 hidden-pilot rows, 384 noisy executions, 1,572,864 shots, and ten
acceptance conditions before a challenge secret exists. The scoring interface
is fixed-width, but the current pilot samples are statevector-backed, so this
is not yet an end-to-end scalability result, holdout acceptance, hardware
evidence, advantage, BQP evidence, or new credit.

The R141 holdout at `T-B4-002ar` / `T-B8-003av` / `T-B10-009aj`
then opens the hidden challenge after public commit `d6de013...` and Discussion
#145. Across 96 four-arm rows, 384 synthetic executions, and 1,572,864 shots,
the sketch matches R140 exact selection `87/96` times and Lagos complete-Ising
`8/8`; mean/max exact-score regret are `0.00004099` / `0.00197748`. Portfolio
sketch-minus-automatic is `+0.00386523` with bootstrap lower `+0.00213694`, and
sketch-minus-R140-exact is `-0.00044153`, so the fixed-width approximation and
portfolio noninferiority gates pass. The global verdict is nevertheless
`REJECT`: A7 alone fails because Lagos sketch-minus-automatic is
`-0.00355006` with only `3/8` wins. This fresh-seed reversal shows that the
R140 local repair is not challenge-seed robust. Requirements pass `10/10`,
phase replay passes `4/4`, and downstream credit remains zero.

`T-B4-002as` / `T-B8-003aw` / `T-B10-009ak` now freezes the R142
seed-robust lower-confidence-bound mapping design. R142 uses the R141 sketch to
retain eight unique QASM candidates per group, then spends a disclosed design
denominator of 1,728 synthetic executions and 3,538,944 shots across sixteen
disjoint seeds. It selects by `mean_delta - 1.96 * standard_error` without
reading any R141 holdout row. Eight of twelve groups achieve a positive LCB and
ten selections change from R140. Lagos returns to mapping `[5,3,6,4,1,0]`,
with design mean `+0.01062521`, LCB `+0.00523438`, and `12/16` wins. All twelve
selected OpenQASM 3 files replay exactly. The unopened holdout contract hash is
`60d62422c35b4f9b2f3339faefc7512c81c3f8049a1ce7291dacb2c6853ba4b6`;
it fixes 96 fresh three-arm rows, 288 executions, 1,179,648 shots, and A1-A10.
This is a frozen robustness design, not hidden-seed acceptance, an efficient
production mapper, hardware evidence, advantage, BQP evidence, or new credit.

The R142 holdout at `T-B4-002at` / `T-B8-003ax` / `T-B10-009al`
then executes 96 hidden three-arm rows and 1,179,648 shots after public commit
`b550327...` and Discussion #147. The preregistered verdict is `ACCEPT`: all
A1-A10 pass. Lagos R142-minus-automatic is `+0.02063963` with `7/8` wins, and
R142-minus-R140 is `+0.01290316`, above the fixed `+0.005` materiality floor.
Portfolio R142-minus-automatic is `+0.00908706` with bootstrap lower
`+0.00669395`; R142-minus-R140 is `+0.00260598` with bootstrap lower
`+0.00158898`; all 12/12 groups stay above `-0.01` versus R140 and severe
regressions are zero. Requirements pass `10/10` and phase replay passes `4/4`.
This validates synthetic challenge-seed transfer for the LCB portfolio, not an
efficient production mapper, current-calibration result, hardware result,
soundness result, advantage, BQP separation, solved frontier, or new credit.

`T-B4-002au` / `T-B8-003ay` / `T-B10-009am` now freezes the R143
successive-halving LCB design. The fixed `8 -> 4 -> 2 -> 1` schedule evaluates
four additional seeds per round and charges 816 executions, reducing R142's
1,728-execution design denominator by `52.7778%`. It reproduces 10/12 R142
choices; mean/max full-budget LCB regret are `0.00010310` / `0.00098866`, and
the accepted Lagos route remains unchanged with full-budget LCB `+0.00523438`.
All twelve selected OpenQASM 3 files replay exactly, and zero R142 holdout rows
enter selection. The unopened contract hash is
`f26cb5cd47223dc9ef46e6164e3581d99eb50730ddb6af15f43822c21c9c62f3`;
it fixes 96 hidden three-arm rows and ten acceptance conditions. This is a
counterfactual charged-execution reduction, not yet fresh hidden acceptance,
live wall-clock savings, cross-calibration transfer, hardware evidence,
advantage, BQP evidence, or new credit.

The R143 holdout at `T-B4-002av` / `T-B8-003az` / `T-B10-009an`
then passes all preregistered A1-A10 gates. Lagos R143-minus-automatic is
`+0.00833417` with `5/8` wins and R143-minus-R142 is exactly `0`. Portfolio
R143-minus-automatic is `+0.00836707` with bootstrap lower `+0.00591163`;
R143-minus-R142 is `-0.00020420` with bootstrap lower `-0.00050431`. All 12/12
groups stay above `-0.01` versus R142, severe regressions are zero, requirements
pass `10/10`, and phase replay passes `4/4`. The 52.7778% charged-execution
reduction therefore preserves synthetic hidden-seed performance. Live
wall-clock savings, cross-calibration transfer, hardware, advantage, BQP, and
new credit remain unclaimed.

`T-B4-002aw` / `T-B8-003ba` / `T-B10-009ao` now freezes the R144
matched live-runtime protocol before measurement. It compares the accepted
R142 full strategy (`1,728` executions) with R143 successive halving (`816`)
at `2,048` shots using identical circuits, seeds, snapshots, and a
post-preregistration secret that chooses strategy order. Shared source loading,
circuit preparation, semantic checks, and warmup are reported separately; the
`perf_counter_ns` interval covers fresh simulator creation, automatic
compilation, circuit execution, online LCB updates, and elimination. Acceptance
requires at least `30%` measured execution-loop savings, exact selection
reproduction, and fair per-execution timing. Contract hash
`4eacb0b36f7cebc52dcd8892430905975374e0038c8cf61cb4b9ead8d5a6beb5`.
No timing measurement, cross-calibration, hardware, billing, advantage, BQP,
or new-credit claim has yet opened.

The R144 matched live-runtime benchmark at `T-B4-002ax` /
`T-B8-003bb` / `T-B10-009ap` then passes A1-A10. The secret selects
full-first order. The full execution loop takes `61.331846` seconds for 1,728
executions; successive halving takes `28.694975` seconds for 816 executions,
a measured reduction of `53.2136%`. The halving/full per-execution runtime
ratio is `0.990771`, and both strategies reproduce their frozen selections
`12/12`, so the saving tracks execution elimination rather than faster
individual executions. Shared setup and warmup are reported separately as
`5.875736` and `0.272216` seconds. Requirements pass `10/10`; the measurement
hash replays without remeasurement. This supports one local matched
execution-loop timing result, not repeated-order confidence, cross-machine or
cross-calibration transfer, hardware or cloud billing savings, advantage, BQP,
or new credit.

`T-B4-002ay` / `T-B8-003bc` / `T-B10-009aq` now freezes the R145
counterbalanced repeated-order runtime protocol before measurement. A fresh
post-preregistration secret selects `ABBA` or `BAAB`, where A is the 1,728-run
full strategy and B is the 816-run successive-halving strategy. Each strategy
therefore runs twice at `2,048` shots with the same circuits, 16 seeds, backend
snapshots, timer boundary, shared setup, and warmup disclosure used by R144.
Acceptance requires `24/24` selection replay per strategy, at least `30%`
pooled runtime reduction, at least `20%` reduction in both adjacent A/B pairs,
no more than `15` percentage points between pair reductions, and a pooled
per-execution ratio in `[0.5, 2.0]`. Contract hash
`ab414301268580529042bc3e5e5e5f13a29a58b9cf78d08b191f34a856c48690`.
No R145 timing, cross-machine or calibration transfer, hardware or billing
savings, advantage, BQP, solved-frontier, or new-credit claim has opened.

The R145 counterbalanced benchmark at `T-B4-002az` / `T-B8-003bd` /
`T-B10-009ar` then passes A1-A10 under the secret-selected `BAAB` schedule.
The two full repeats take `66.608633` and `66.715556` seconds; the two halving
repeats take `32.587036` and `32.525027` seconds. Pooled execution-loop savings
are `51.1626%`, while the two adjacent-pair savings are `51.0769%` and
`51.2482%`; their spread is only `0.1714` percentage points. The pooled
halving/full per-execution ratio is `1.034204`, and both strategies replay all
`24/24` frozen selections. Requirements pass `10/10`, and measurement hash
`0a52d7476ab252ee7086295e709904abbfedb1e650513c76b6b6ac3c2333b218`
replays without remeasurement. This accepts one same-machine repeated-order
runtime result, not cross-machine or cross-calibration transfer, hardware or
cloud billing savings, advantage, BQP, solved-frontier status, or new credit.

`T-B4-002ba` / `T-B8-003be` / `T-B10-009as` now freezes the R146
cross-backend calibration-snapshot transfer protocol before challenge. It
tests all six directed pairs among FakeJakartaV2, FakeLagosV2, and FakeOslo on
all four dense validation tasks. Each source R143 winner carries its mapping,
route policy, and realization seed unchanged but is recompiled on the target
snapshot; the target-specific R143 winner and a hidden-seed automatic layout
form the denominators. Eight hidden trials per transfer group fix `192`
three-arm rows, `576` executions, and `1,179,648` shots. Acceptance requires
portfolio noninferiority versus both automatic and target-specific routes, at
least `20/24` groups above `-0.02` versus target-specific, zero row regressions
below `-0.05`, and every target snapshot mean above `-0.01`. Contract hash
`5e29e68eefcb6809a4df6cc86916b76f299267f36eeabc4d44fd22754cfaceb3`.
No R146 challenge, temporal same-device calibration transfer, cross-machine
transfer, hardware, advantage, BQP, solved-frontier, or new-credit claim has
opened.

The R146 holdout at `T-B4-002bb` / `T-B8-003bf` / `T-B10-009at` is
then preregistered REJECT with A5-A8 failed. All `48/48` compiled source and
target routes preserve semantics, and transfer versus automatic remains close
to noninferior with portfolio mean `-0.00293528` and bootstrap lower
`-0.00539244`. Transfer versus the target-specific R143 route is materially
worse: portfolio mean `-0.01145921`, bootstrap lower `-0.01410930`, only
`19/24` groups above `-0.02`, and `9` rows below `-0.05`. FakeLagosV2 is the
weakest target at mean `-0.01799629`. The dominant failure is
FakeJakartaV2-to-FakeLagosV2 dense XY: all `8/8` rows are severe and the group
mean is `-0.07489771`; FakeOslo-to-FakeLagosV2 complete Ising contributes the
remaining severe row. Requirements and phase replay pass `10/10` and `4/4`.
This rejects unconditioned cross-backend snapshot transfer and motivates a
target-calibration adaptation gate; temporal same-device transfer,
cross-machine transfer, hardware, advantage, BQP, solved-frontier status, and
new credit remain unclaimed.

`T-B4-002bc` / `T-B8-003bg` / `T-B10-009au` now freezes the R147
target-descriptor adaptation design and holdout protocol before challenge. For
each of three target snapshots and four dense tasks, the selector recompiles
only the two foreign R143 route identities and chooses the lower public target
readout/CX combined-error proxy with deterministic tie breaks. The
target-specific R143 route is excluded from all 12 selector pools and is
reserved only as a blind denominator; R146 hidden rows and deltas are never
read for selection or tuning. All `24/24` foreign candidate routes preserve
semantics. The selector chooses FakeOslo for all four FakeLagosV2 tasks,
including the R146 dense-XY failure locus, using calibration descriptors alone.
The preregistered holdout fixes `96` three-arm rows, `288` executions, and
`589,824` shots. Acceptance requires portfolio noninferiority, at least `11/12`
groups above `-0.02` versus target-specific, zero regressions below `-0.05`,
every target mean above `-0.01`, and a dedicated Lagos dense-XY mean/severe-row
guard of `-0.02` / `0`. Contract hash
`7dc1d668848ef18524979ff161f46031a8658ba15e91870cea0b6f2743e77394`.
No R147 holdout result, temporal transfer, cross-machine transfer, hardware,
advantage, BQP, solved-frontier status, or new credit is claimed.

The R147 holdout at `T-B4-002bd` / `T-B8-003bh` / `T-B10-009av` is
then preregistered REJECT with A5-A8 failed. Requirements and phase replay pass
`10/10` and `4/4`, and all `24/24` adapted and target-specific compiled routes
preserve semantics. Adapted versus automatic remains noninferior with portfolio
mean `-0.00133967` and bootstrap lower `-0.00375896`, but adapted versus the
target-specific R143 route has mean `-0.00945567` and bootstrap lower
`-0.01233164`. Only `9/12` groups remain above `-0.02`, two rows fall below
`-0.05`, and the weakest target mean is FakeLagosV2 at `-0.01482360`.
The descriptor rule does repair the former dominant Lagos dense-XY failure:
its group mean moves from R146's `-0.07489771` to `-0.01496745`, with severe
rows falling from eight to zero. The bottleneck moves to Lagos complete Ising,
whose mean is `-0.04314811` with two severe rows; Jakarta complete Ising and
dense XY also miss the group floor. This rejects calibration-proxy-only
adaptation while isolating task-conditioned channel risk as the next gate.
Temporal transfer, cross-machine transfer, hardware, advantage, BQP,
solved-frontier status, and new credit remain unclaimed.

`T-B4-002be` / `T-B8-003bi` / `T-B10-009aw` now freezes the R148
task-conditioned channel-risk design and hidden holdout before challenge. The
rule has zero fitted weights and reads zero R147 hidden rows. For the six task
groups whose ideal output is nonuniform, it prioritizes exact output-aware
readout fidelity and uses CX survival as a tie break; for the six uniform-output
groups, whose distribution is invariant under symmetric readout flips, it
prioritizes CX survival. Target-specific R143 routes remain excluded from all
selector pools. All `24/24` foreign candidates preserve semantics, and the rule
changes four R147 selections: Jakarta complete Ising, Jakarta dense XY, Lagos
complete Ising, and Oslo scrambled QFT. The preregistered challenge fixes `96`
three-arm rows, `288` executions, and `589,824` shots. Acceptance retains the
R147 portfolio, group, severe-row, and each-target floors and additionally
requires simultaneous repair of Jakarta complete Ising, Jakarta dense XY, and
Lagos complete Ising. Contract hash
`fa2c21ca88e6f08ec65c689c44d065e00ca00a5182846ec74ca70177b7103132`.
No R148 holdout, scalable exact-output method, temporal transfer, cross-machine
transfer, hardware, advantage, BQP, solved-frontier status, or new credit is
claimed.

The R148 holdout at `T-B4-002bf` / `T-B8-003bj` / `T-B10-009ax` is
then preregistered REJECT with A8 alone failed; A1-A7 and A9-A10 pass.
Requirements and phase replay pass `10/10` and `4/4`, and all `24/24`
conditioned and target-specific routes preserve semantics. Portfolio
conditioned-automatic mean and bootstrap lower are positive at `+0.00216544`
and `+0.00055207`. Conditioned-target mean `-0.00486511` clears the fixed
`-0.005` floor and its bootstrap lower is `-0.00690479`; `11/12` groups clear
`-0.02`, severe rows are zero, and every target mean clears `-0.01`. The rule
repairs Jakarta complete Ising to `-0.00406249` and Lagos complete Ising to
`-0.00610122`, both without severe rows. The sole residual is Jakarta dense XY
at `-0.02798808`, below the dedicated `-0.02` simultaneous-repair floor, so A8
and the global verdict remain false. This isolates a candidate-support limit:
both available foreign routes are inadequate for that group, so the next gate
must generate a new target-aware route without copying the target-specific R143
identity rather than tune channel weights. Scalable exact-output evaluation,
temporal transfer, cross-machine transfer, hardware, advantage, BQP,
solved-frontier status, and new credit remain unclaimed.

`T-B4-002bg` / `T-B8-003bk` / `T-B10-009ay` now freezes the R149
Jakarta dense-XY candidate-generation design before any new holdout is opened.
The generator enumerates all `5,040` six-logical-to-seven-physical mappings,
excludes the target-specific R143 identity and both foreign R148 identities,
and statically ranks the remaining `5,037` mappings from public calibration,
output-sensitive readout risk, and circuit interaction structure. Three ranking
views produce a 12-mapping shortlist; two routing policies and two realization
seeds produce `48` compiled candidates. Fixed public design seeds successively
halve them `48 -> 12 -> 3 -> 1`. The selected mapping `[5, 6, 1, 0, 3, 2]`
copies no frozen identity and reads zero R148 hidden rows. Post-selection
diagnostics, excluded from selection, place it `-0.00115322` below the R143
target-specific route and `+0.02465309` above the old R148 foreign route.
The immutable challenge at `T-B4-002bh` / `T-B8-003bl` / `T-B10-009az`
will run `96` rows, `296` circuit executions, and `606,208` shots across all
12 portfolio groups. It requires all `12/12` groups to clear `-0.02`, zero
severe rows, every target to clear `-0.01`, and the replacement to improve at
least `+0.01` over the R148 route. Contract hash
`4efbda7920ec5b7cc9486145076f4550d109f6db32c730904e9fc406c4a80552`.
No R149 holdout, general route-generation advantage, temporal or cross-machine
transfer, hardware result, quantum advantage, BQP separation, solved-frontier
status, or new credit is claimed.

`T-B4-002bv` / `T-B8-003bz` / `T-B10-009bn` now preregisters R157 as
a direct `VF2PostLayout` tie-isolation experiment. The input is the exact
77-operation, depth-39 OpenQASM 3 circuit observed after R156 callback 16,
hash `ce216610...`; this removes the first sixteen full-pipeline passes from
the new execution surface. Independent recalculation shows that the two R156
endpoint mappings have exactly the same average-error score,
`0.45894321220828727`. Five frozen profiles require 98 post-registration
operating-system processes and 160 direct pass replays: native target,
ascending canonical target, descending canonical target, fresh target repeated
inside one process, and one target shared inside one process. The exact Qiskit
2.4.1 Rust source commit/path/hash and `seed=-1`, `strict_direction=false`,
30,000,000 call limit, and 250,000 trial limit are bound. Mapping collapse,
continued variation, new mappings, and no-solution rows are all admissible and
must be retained. Requirements pass `10/10`; contract `f45f7e7f...`;
execution remains unopened. This protocol does not claim a lower-level
mechanism, confirmed Qiskit bug, general compiler determinism theorem,
hardware or simulation performance, transfer, route advantage, quantum
advantage, BQP separation, solved-frontier status, or new credit.

`T-B4-002bw` / `T-B8-003ca` / `T-B10-009bo` completes the retained R157
matrix with 98 post-registration operating-system processes and 160 direct
`VF2PostLayout` replays. Both known exactly tied mappings remain present in
every one of the five profiles. Their aggregate counts are `103/57`; native
independent-process counts are `24/8`, ascending `20/12`, descending `19/13`,
fresh-target same-process `19/13`, and shared-target same-process `21/11`.
All five profiles vary internally; there are no new mappings and no no-solution
rows. This rejects the simple explanations that process startup, canonical
Target insertion order, fresh Target construction, or reuse of one shared
Target is sufficient by itself to select one mapping deterministically. It
does not identify the lower-level source. Five post-registration implementation
smoke calls are disclosed outside the matrix, so R157 is not described as a
blinded confirmation. Conditions and requirements pass `10/10`; zero
simulations and zero shots were used. No compiler-mechanism, confirmed-bug,
hardware, transfer, route-advantage, quantum-advantage, BQP, solved-frontier,
or new-credit claim is made.

`T-B4-002bx` / `T-B8-003cb` / `T-B10-009bp` now preregisters R158 as a
source-bound accelerator-call boundary experiment. Qiskit release commit
`0fd015a2...`, five Python/Rust source-file hashes, and the installed 2.4.1
accelerator binary hash `a299d48f...` are frozen. Four one-process profiles
retain 64 calls each: the Python pass with fresh DAG/config/internal ErrorMap;
the Rust accelerator with fresh DAG/config/internal ErrorMap; the accelerator
with shared DAG/config and internal ErrorMap; and the accelerator with one
shared DAG, Target, config, and externally constructed ErrorMap. The matrix
therefore fixes 4 processes and 256 direct calls. If the final profile still
varies, the observation boundary moves inside per-call Rust VF2 graph/state/
scoring construction, but no particular hash, iterator, floating-point, or
retention mechanism is proved. Requirements pass `10/10`; contract
`c8ac00cb...`; execution remains unopened. No lower-level mechanism,
confirmed Qiskit bug, hardware, transfer, route-advantage, quantum-advantage,
BQP, solved-frontier, or new-credit claim is made.

`T-B4-002by` / `T-B8-003cc` / `T-B10-009bq` completes R158 with four
post-registration operating-system processes and 256 retained calls. The
Python-pass fresh-object profile produces the two tied mappings at `46/18`;
the direct accelerator with fresh DAG/config and internal ErrorMap produces
`36/28`; and sharing the DAG/config while retaining internal ErrorMap
construction produces `34/30`. The final profile reuses one DAG, Target,
configuration, and externally constructed deterministic ErrorMap and collapses
to mapping A at `64/0`. Aggregate mapping counts are `180/76`, with no new
mapping and no no-solution row. This localizes the observed variation boundary
to internal ErrorMap construction under the frozen source and binary, while
not identifying a hash, iterator, floating-point accumulation, or retention
mechanism. Conditions and requirements pass `10/10`; zero simulations and zero
shots were used. No confirmed Qiskit-bug, general compiler-determinism,
hardware, transfer, route-advantage, quantum-advantage, BQP, solved-frontier,
or new-credit claim is made.

`T-B4-002bz` / `T-B8-003cd` / `T-B10-009br` preregisters R159 as a
source-instrumented ErrorMap accumulation trace. An exact patch against Qiskit
release commit `0fd015a2...` retains each qargs operation order, operation-error
bits, every accumulated `f64` bit pattern, average-error bits, and the returned
tied mapping. The patched source hash is `ab0f5319...`; the release accelerator
hash is `b24cf719...`. Three operating-system processes freeze 128 native
HashSet-order calls, 64 ascending-order calls, and 64 descending-order calls.
The support rule requires native mapping variation, both sorted profiles to
collapse, multiple native average-error bit maps, a functional operation-order
to error-bits relation, and a functional error-bits to mapping relation. Three
pre-registration API-smoke calls used only an unrelated three-qubit
GenericBackendV2 toy; the frozen R157 input was not loaded. Requirements pass
`10/10`; execution remains unopened. No causal mechanism, confirmed Qiskit
bug, general compiler theorem, hardware relevance, route advantage, quantum
advantage, BQP separation, solved-frontier status, or new credit is claimed.

`T-B4-002ca` / `T-B8-003ce` / `T-B10-009bs` executes the frozen R159
source trace after commit `b33e8843...` and Discussion #180. The native
HashSet-order profile produces the two exactly tied mappings at `71/57`, with
`128` operation-order hashes and `16` average-error-bit hashes. Every native
order hash maps to one error-bit map, and every error-bit map maps to one
layout class. Ascending and descending accumulation each collapse to mapping A
at `64/0`; their fixed error-bit maps differ from each other. Aggregate counts
are `199/57`, all A1-A10 and P1-P10 pass, and no simulation or shots occur. A
preflight import first rejected the globally installed accelerator hash
`a299d48f...` before the frozen input was loaded; the accepted run imported the
preregistered instrumented binary `b24cf719...` through its source path. The
classification is `operation_order_f64_path_supported` for this instrumented
build and tied input. It is not elevated to a confirmed Qiskit bug,
cross-platform theorem, hardware, route-advantage, quantum-advantage, BQP,
solved-frontier, or new-credit claim.

`T-B4-002cb` / `T-B8-003cf` / `T-B10-009bt` preregisters R160 as a
deterministic external ErrorMap remediation and exact-oracle guardrail. Four
construction modes--ascending `f64`, descending `f64`, `math.fsum`, and exact
binary-fraction accumulation--cover one tied baseline plus 32 declared ULP
perturbations. Four processes per mode and two replays per case freeze 16
processes and 1,056 direct VF2 calls. Every mode/case is independently scored
over all `7! = 5,040` mappings with exact rational arithmetic; a non-tied case
counts only when all four modes share one unique optimum with a gap of at least
`1e-16`. The protocol also separates R157's concrete-operation-only Python
score from the Rust ErrorMap denominator retained by R159. A four-call
pre-registration smoke used only an unrelated three-qubit toy. Requirements
pass `10/10`; frozen-input execution remains unopened. No source patch,
accepted upstream fix, confirmed Qiskit bug, cross-platform theorem, hardware,
route-advantage, quantum-advantage, BQP, solved-frontier, or new-credit claim is
made.

`T-B4-002cc` / `T-B8-003cg` / `T-B10-009bu` executes all 16 processes,
33 cases, and 1,056 direct calls. All four methods stabilize the untouched tie
to `[6,5,4,3,0,1,2]`; 12 cases clear the `1e-16` protected-margin gate and all
12 select the shared exact optimum. The executor initially reported
`deterministic_external_map_remediation_supported`, but its own summary showed
that not every replay belonged to the exact-oracle minimum set. The independent
`T-B4-002cd` / `T-B8-003ch` / `T-B10-009bv` adjudication therefore
overrules that label under the public support rule. Exactly `224/1,056` calls
across seven 1-8 ULP near-tie cases return mapping A while the exact rational
oracle prefers mapping B; exact-oracle passes are `832/1,056`. The audited
classification is `tie_stabilized_but_non_tied_guardrail_failed`. Raw execution
integrity remains valid, but complete remediation is rejected. No source patch,
confirmed Qiskit bug, cross-platform theorem, hardware, route-advantage,
quantum-advantage, BQP, solved-frontier, or new-credit claim is made.

`T-B4-002ce` / `T-B8-003ci` / `T-B10-009bw` then executes R161 as a
source-faithful score audit over the immutable R160 workers. It applies the
same `neg_log_fidelity` transform used by the Qiskit VF2 source, scores all
`5,040` enumerated mappings with an exact rational shadow oracle, and rebuilds
the source-order binary64 fold. The transformed exact oracle still rejects the
same `224/1,056` rows, but every one of those rows is a minimum under the
reconstructed binary64 path. A further `32` rows on `edge_1_2_m008ulp` sit one
`2.7755575615628914e-17` score unit above that reconstruction. The resulting
classification is `source_f64_consistent_but_exact_rational_gap_remains`:
this is a numerical diagnostic boundary, not a compiler-bug claim or a fix.
Requirements pass `10/10`; no source patch, hardware, quantum advantage, BQP,
solved-frontier, or new-credit claim is made.

`T-B4-002cf` / `T-B8-003cj` / `T-B10-009bx` then executes R162 as a
source-instrumented score-combination trace over the frozen R157 input. Three
processes retain 256 calls, `44,800` combine/compare/candidate events, and
`6,912` strict `Decreasing` comparisons. The returned source binary64 total
differs from `math.fsum` on `141/256` calls; the remaining `115/256` agree with
`math.fsum` but differ from the exact rational sum of retained binary64 leaves.
Mapping classes are A/B `207/49`, with no-solution and other mappings at zero.
This localizes a candidate-total arithmetic boundary and does not establish a
confirmed Qiskit bug, numerical remedy, cross-platform theorem, hardware
result, route advantage, quantum advantage, BQP separation, solved B4/B8/B10,
or new credit. Requirements pass `10/10`.

`T-B4-002cg` / `T-B8-003ck` / `T-B10-009by` executes R163 as a comparison-policy
shadow over the hash-bound R162 traces. It replays 3 profiles and 256 calls
under source binary64, compensated `math.fsum`, exact retained-binary64 leaves,
and a declared 1-ULP tie-aware rule. Of `6,912` source comparisons, `1,180`
are uniquely reconstructable and `5,732` are explicitly skipped because their
operands are not yet recoverable without ambiguity. All four policies agree
with the source on every reconstructable event; `24` tie-aware ties appear but
no source decision changes. The result is a comparison-level negative boundary:
it does not establish a production remedy, changed mapping, confirmed Qiskit
bug, hardware result, quantum advantage, BQP separation, solved B4/B8/B10, or
new credit. Requirements pass `10/10`; complete operand provenance is the next
gate.

`T-B4-002ch` / `T-B8-003cl` / `T-B10-009bz` executes R164 with a source-combine
binding. Each comparison operand is bound by its source expression and the
hash-bound `combine.result_bits`, then checked against a unique retained
binary64 leaf vector. All `6,912/6,912` source comparisons are reconstructable
across 3 profiles and 256 replays. Compensated `math.fsum`, exact retained-leaf,
and 1-ULP tie-aware policies each disagree with the source on `49` comparison
events; the tie-aware policy records `256` ties. This exposes a policy-sensitive
comparison boundary, but remains a shadow-only diagnostic: it does not establish
a source patch, production remedy, changed mapping, confirmed Qiskit bug,
hardware result, quantum advantage, BQP separation, solved B4/B8/B10, or new
credit. Requirements pass `10/10`; the next gate is a full candidate-selection
replay under a predeclared acceptance rule.

`T-B4-002ci` / `T-B8-003cm` / `T-B10-009ca` executes R165 as a complete-candidate
selection replay. The hash-bound Qiskit 2.4.1 accelerator records every complete
VF2 candidate yielded by the frozen iterator, including its mapping, score,
retained leaves, and enumeration index. Across 3 profiles and 256 calls, `298`
yielded candidates are observed and source-return validation matches `256/256`.
Compensated, exact-leaf, and 1-ULP policies each select a different observed
candidate mapping in `42` replays. This is a candidate-level replay boundary,
not an alternate search-path or production-compiler claim: it does not establish
a confirmed Qiskit bug, numerical remedy, hardware result, quantum advantage,
BQP separation, solved B4/B8/B10, or new credit. Requirements pass `10/10`; the
next gate is an independent reproduction and adversarial baseline.

`T-B4-002cj` / `T-B8-003cn` / `T-B10-009ca-r166` preregisters R166 before
execution. An independent standard-library verifier will read only the
committed R165 profile manifests and replay rows; it will not import the R165
executor or call Qiskit. It will recompute all four selection policies, verify
the 3-profile/256-replay and 298-candidate aggregates, and run tamper,
rehashed-false-selection, candidate-removal, and candidate-order baselines.
This is an evidence-integrity gate for the candidate-level result, not a
production mapping, alternate search path, confirmed bug, hardware, quantum
advantage, BQP, solved-frontier, or new-credit claim.

The first dry execution stopped before producing a result because the verifier
read `profile_count` from the wrong protocol level. The implementation was
corrected, its executor and contract hashes were rebound, and the correction
was recorded before the R166 rerun; no scientific result was inferred from the
failed dry execution.

R166 then completed with an independent standard-library verifier. It checked
`256/256` row payload hashes, recomputed `298` complete candidates and
`256/256` source-return matches, and reproduced the R165 policy-change counts
exactly: `source_f64=0`, `compensated_fsum=42`, `exact_binary64_leaf=42`, and
`tie_aware_1ulp=42`. Unhashed row tampering was rejected, a rehashed false
selection was rejected by recomputation, and removing the source-selected
candidate was detected. This strengthens evidence integrity only; it does not
establish a production mapping change, alternate search path, confirmed bug,
hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or
new credit. Requirements pass `10/10`.

`T-B4-002ck` / `T-B8-003co` / `T-B10-009ca-r167` preregistered and then executed
the next candidate-level test on a new input. R167 uses a hash-bound
six-active-qubit path-with-chord OpenQASM 3 interaction graph rather than the
R157 input, with three operation-order profiles and `192` fixed calls. The
source-instrumented Qiskit path completed all calls, but the input produced
`0/192` candidate events, `0/192` yielded complete candidates, and `0/192`
returned candidates. Every arithmetic-policy mapping-difference count is zero,
and simulation and shots remain zero.

R167 had three implementation-only corrections. Two pre-execution dry checks
stopped before any worker artifact existed: the executor first read the
top-level protocol as if it were nested under a `protocol` key, then its
accelerator probe assumed a Rust module exposed `__file__`. After the workers
completed, aggregation exposed a third schema mismatch: source-return
validation was nested under `replay`, while the aggregator read a top-level
field. The third correction was committed in `f30c077` before the result file
was written. The executor and contract hashes were rebound after each fix.

The raw complete-candidate protocol remains honestly incomplete at `6/10`:
there is no candidate set on which source-return or arithmetic-policy
correctness can be estimated. A separate `10/10` candidate-free adjudication
records this as a reproducible feasibility boundary, not as evidence of a
wrong winner, a confirmed Qiskit bug, cross-input generality, hardware
relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.
The next gate is an input/target compatibility design that can exercise the
candidate path, or an explicitly preregistered no-candidate branch.

`T-B4-002cl` / `T-B8-003cp` / `T-B10-009cb-r168` resolves that next gate for
the R167 input-target pair at the structural-diagnostic level. R168 exhaustively
enumerates all injective assignments of the six active logical vertices into
the seven `FakeNairobiV2` target vertices under the same undirected
`strict_direction=false` boundary. The R167 interaction graph has six unique
edges and cycle rank `1`; the target graph has six unique edges and cycle rank
`0`; complete edge-preserving embeddings are `0`. Removing only the chord still
gives `0` embeddings because the six-vertex path exceeds the target diameter.
A target-derived six-vertex tree template gives `8` embeddings.

R168 therefore explains the R167 candidate-free boundary for this specific
input-target pair without upgrading it into a Qiskit bug, numerical remedy,
production mapping change, hardware result, quantum advantage, BQP separation,
solved B4/B8/B10, or new credit. The next experiment must freeze a new
target-compatible OpenQASM 3 input with a nonzero embedding count, then rerun
the candidate-level arithmetic-policy replay.

`T-B4-002cm` / `T-B8-003cq` / `T-B10-009cc-r169` now freezes that follow-up
experiment before execution. R169 uses a six-active-qubit target-compatible
tree with interaction edges `(1,2),(2,3),(2,4),(4,5),(5,6)`, the graph family
for which R168 found `8` injective embeddings in the `FakeNairobiV2` target.
The protocol keeps the same three operation-order profiles, `192` total calls,
source-instrumented Qiskit path, and four arithmetic policies. Candidate
counts, source-return matches, policy changes, and simulation counts remain
open until the preregistered replay runs. R169 is a candidate-feasibility
control, not a production mapping change, confirmed bug, hardware result,
quantum advantage, BQP separation, solved B4/B8/B10, or new credit.

R169 then completes with requirements `10/10`. All `192/192` candidate-traced
calls produce candidates, yielding `576` complete candidates (`3` per call),
and source-return validation matches `192/192`. The four arithmetic policies
change `0` mappings on this input, while simulation and shots remain `0/0`.
This clears candidate observability for one target-compatible input and leaves
the policy-stability question open: a second compatible graph with closer
candidate scores is required before treating the zero-difference result as a
general property. No numerical remedy, production mapping change, confirmed
Qiskit bug, hardware result, quantum advantage, BQP separation, solved B4/B8/B10,
or new credit is claimed.

`T-B4-002cn` / `T-B8-003cr` / `T-B10-009cd-r170` now freezes the next
near-tie control before execution. R170 uses a five-active-qubit
target-compatible tree with edges `(0,1),(1,2),(2,4),(3,4)`. A one-call
ascending-order design preflight observes `3` candidates and a best-two
source-score gap of exactly `1.0 ULP`; the preflight performs no mapping
selection or simulation. The full replay keeps three operation-order profiles,
`192` calls, and the four arithmetic policies. It is designed to test whether
the zero policy-difference result from R169 survives deliberate near-tie
pressure, not to claim a numerical remedy, production mapping change, confirmed
Qiskit bug, hardware result, quantum advantage, BQP separation, solved B4/B8/B10,
or new credit.

R170 then completes with requirements `10/10`. All `192/192` calls produce
exactly `3` candidates, yielding `576` candidates; source-return validation
matches `192/192`. The source binary64 policy changes `0` mappings, while
compensated `math.fsum`, exact retained-binary64 leaves, and tie-aware 1-ULP
selection each change `192` mappings. The same split appears under all three
operation-order profiles, with simulation and shots remaining `0/0`. This is
strong evidence that a one-ULP candidate gap can expose a policy-dependent
selection boundary in this frozen input, but it is not yet an independent score
oracle, a cross-input theorem, a numerical remedy, a production mapping change,
a confirmed Qiskit bug, a hardware result, quantum advantage, BQP separation,
solved B4/B8/B10, or new credit. The next gate is a second near-tie graph and
an independent score oracle.

`T-B4-002co` / `T-B8-003cs` / `T-B10-009ce-r171` now freezes an independent
standard-library oracle for the R170 result. R171 reads only the committed
worker manifests, verifies row payload hashes, reconstructs binary64 source
scores, compensated sums, exact rational leaf sums, and the 1-ULP tie rule, then
checks the `192/192` source-return matches and exact policy split. It performs
no Qiskit import, new circuit call, simulation, route change, or hidden seed.
This is an evidence-integrity and arithmetic-recomputation gate, not a new
numerical remedy, production mapping change, confirmed bug, hardware result,
quantum advantage, BQP separation, solved B4/B8/B10, or new credit.

R171 completes with requirements `10/10`. A standard-library-only oracle
verifies `192/192` replay-row hashes, reconstructs `576` candidate records,
reproduces `192/192` source-return matches, and exactly matches the R170 policy
split: source `0`, compensated `192`, exact leaf `192`, tie-aware `192`. It
performs zero Qiskit calls, simulations, shots, route changes, or hidden seeds.
This strengthens evidence integrity and arithmetic recomputation for the frozen
input, but does not establish a new Qiskit execution, cross-input theorem,
production mapping change, numerical remedy, confirmed bug, hardware result,
quantum advantage, BQP separation, solved B4/B8/B10, or new credit. The next
gate is a second near-tie graph with an independent oracle.

The R149 holdout at `T-B4-002bh` / `T-B8-003bl` / `T-B10-009az` is
then preregistered ACCEPT with A1-A10, requirements, and phase replay all
passing `10/10`, `10/10`, and `4/4`. All `24/24` repaired and target-specific
routes preserve semantics. The repaired portfolio beats the automatic arm by
mean `+0.00360133` with bootstrap lower `+0.00142312`; against the
target-specific denominator it has mean `-0.00391072` and bootstrap lower
`-0.00542965`. All `12/12` groups clear `-0.02`, no row falls below `-0.05`,
and every target mean clears `-0.01`. The generated Jakarta dense-XY route has
mean `-0.00565709` versus the target-specific route and `+0.02424579` versus
the frozen R148 foreign route, with zero severe rows. This closes the sole R148
portfolio gap under the preregistered finite simulated-noise contract, but it
does not establish general candidate-generation advantage, temporal or
cross-machine transfer, hardware performance, quantum advantage, BQP
separation, solved B4/B8/B10, or new credit.

`T-B4-002bi` / `T-B8-003bm` / `T-B10-009ba` now freezes the R150
unseen-backend candidate-generation design before challenge. The unchanged
R149 recipe is applied independently to FakeCasablancaV2, FakeNairobiV2, and
FakePerth, three seven-qubit backend classes absent from the R125-R149
portfolio. It enumerates `15,120` mappings, shortlists `36`, compiles `144`
generated candidates, and checks `240` strong denominator candidates from 80
independent optimization-level-3 transpiler seeds per backend. All `384/384`
circuits preserve semantics. Public post-selection diagnostic deltas against
the strong denominators are `-0.02514781`, `+0.00966658`, and `+0.00345661`
for Casablanca, Nairobi, and Perth. These diagnostics do not alter selection.
The unopened contract fixes `24` hidden rows, `72` executions, and `147,456`
shots. It requires all `3/3` backend means to clear `-0.02`, zero severe rows,
and portfolio generated-denominator mean/bootstrap floors of `-0.005` and
`-0.015`. Contract hash
`b71c0e9e171fc9b3a221303e3b328595b18c2f186e4c2a3e52f5b088ead5332b`.
No hidden result, temporal or real-device transfer, hardware performance,
general route-generation advantage, quantum advantage, BQP separation,
solved-frontier status, or new credit is claimed.

The R150 holdout at `T-B4-002bj` / `T-B8-003bn` / `T-B10-009bb` is
preregistered REJECT with A6 and A8 failed; A1-A5, A7, A9, and A10 pass.
Requirements and phase replay pass `10/10` and `4/4`, and all `6/6` frozen
generated/denominator routes preserve semantics. The generated portfolio beats
fresh hidden-seed automatic compilation by mean `+0.01858639` with bootstrap
lower `+0.01034859`. Against the strong 80-seed denominators, portfolio mean
`-0.00240671` and bootstrap lower `-0.00965945` pass their fixed floors, and no
row falls below `-0.05`. Nairobi and Perth win `8/8` rows with group means
`+0.01164795` and `+0.00683421`. Casablanca loses `0/8` rows with mean
`-0.02570231` and minimum `-0.03723049`, so only `2/3` backend groups clear
the required `-0.02` floor. The unchanged R149 recipe therefore fails the
strict three-backend generalization claim and opens a Casablanca-specific
topology/calibration attribution gate. This is not temporal or real-device
transfer, hardware performance, general route-generation advantage, quantum
advantage, BQP separation, solved B4/B8/B10, or new credit.

`T-B4-002bk` / `T-B8-003bo` / `T-B10-009bc` now attributes the R150
Casablanca failure without selecting a repair. Across 32 fresh attribution
seeds, two frozen routes, and full/gate-only/readout-only noise on all three
backends, R151 executes `576` circuits and `4,718,592` shots. Casablanca's
full-model generated-denominator delta `-0.02653462` reproduces the R150
holdout sign and magnitude. Gate-only remains `-0.02895127`, while readout-only
is effectively neutral at `+0.00008194`. The generated route has identical
readout exposure, but `10` additional CX operations, CX exposure-proxy delta
`+0.05333778`, combined exposure delta `+0.04757183`, and depth `143` versus
`125`. Its heaviest edge `(5,3)` occurs 17 times versus 12 in the denominator.
However, Nairobi also has eight additional CX operations and worse exposure
while retaining a positive gate-only delta, so raw CX count alone is not a
causal certificate. Casablanca's candidate pool contains 31 unique edge
signatures and the selected route ranks fourth of 48 by combined exposure;
the strong denominator signature is absent from that pool. Requirements pass
`10/10`. The next gate must freeze an edge-pattern-aware, diversity-expanding
candidate rule before any new hidden rows. R151 is diagnostic, not causal
proof, a repair, hardware evidence, general route-generation advantage,
quantum advantage, BQP separation, solved-frontier status, or new credit.

`T-B4-002bl` / `T-B8-003bp` / `T-B10-009bd` now freezes the R152
Casablanca edge-signature expansion before challenge. R151 found that all 31
edge signatures in the original 48-candidate pool missed the strong
denominator signature. R152 therefore starts from the independent 80-seed
automatic-route library, excludes every original candidate signature, excludes
the strong denominator QASM and exact signature, and admits 16 novel signature
representatives. Public `16 -> 4 -> 1 -> 1` successive halving charges 88
executions; 32 post-selection diagnostics cannot alter the winner. The selected
seed `150128` has 59 CX operations, a combined exposure proxy of `0.55257253`,
and copies none of the excluded signatures. Its public mean is `+0.02321779`
versus the R150 generated route and `-0.00353929` versus the strong denominator.
The unopened R152 contract keeps Nairobi and Perth on their R150 routes and
replaces only Casablanca. It fixes 24 hidden rows, 72 executions, and 147,456
shots; requires all 3/3 group means and Casablanca itself to clear `-0.02`;
allows zero severe rows; and retains portfolio mean/bootstrap floors of
`-0.005`/`-0.015` versus the denominator. Contract hash
`f81dbba0ce3e4a4c601dde43c34fbf89efb0deaa49b8b57d772167f373889ce1`.
R150 hidden trial values used for candidate scoring remain zero. No hidden
result, causal proof, temporal or real-device transfer, hardware performance,
general route-generation advantage, quantum advantage, BQP separation,
solved-frontier status, or new credit is claimed.

The R152 holdout at `T-B4-002bm` / `T-B8-003bq` / `T-B10-009be` is
preregistered ACCEPT with A1-A10 and P1-P10 passing. A second full replay
matches all `4/4` phase artifacts. Portfolio repaired-automatic mean/bootstrap
lower are `+0.02626896` / `+0.01927970`; repaired-denominator mean/bootstrap
lower are `+0.00488735` / `+0.00183043`. All `3/3` backend groups clear
`-0.02`, no row falls below `-0.05`, and all `6/6` route semantic checks pass.
The novel Casablanca signature moves the group mean from R150's
`-0.02570231` to `-0.00336195`, with minimum row `-0.00936479` and `2/8`
strict wins against the strong denominator. Preserved Nairobi and Perth
controls remain positive at `+0.00927928` and `+0.00874473`. Payload hash
`8d2c1a56383012a3c4b5dd8ca0c0840b0504aab7879ebea354c3e2e63cf928f1`.
This accepts one finite simulated-noise edge-signature repair and rejects the
R150 Casablanca failure under new hidden seeds. It is not causal proof,
temporal or real-device transfer, hardware performance, general
route-generation advantage, quantum advantage, BQP separation,
solved-frontier status, or new credit.

`T-B4-002aj` / `T-B8-003an` / `T-B10-009ab` now adds the R135
dense-interaction deterministic fallback boundary. For each new inverse-QFT,
scrambled-QFT, complete-Ising, and dense-XY input, five temporal graph rules
contribute top mappings while `80` disjoint seeded automatic-layout runs add
candidate initial mappings. The `538` unique group-level mappings are recompiled
under default and lookahead policies; `1,076` portfolio candidates are ranked by
historical compiled exposure before the validation baselines are opened. Across
`2,156` total compilations, the isolated validation block records `100` wins,
`13` ties, and `7` losses, reducing R134's `54` losses. Seven of twelve groups
are loss-free, selected QASM replays `12/12` across a fresh process, and ten
groups choose fixed-map default routing while two choose lookahead. The strict
automatic-baseline no-loss gate still fails: inverse-QFT retains one loss each
on Lagos and Oslo, complete Ising retains two on Jakarta and Oslo, and Lagos
dense XY retains one. No verifier acceptance, hardware, soundness, advantage,
BQP, or new B10 credit is claimed. Requirements pass `10/10`.

`T-B1-004gj` / `T-B7-015s` now closes the first R85 blocker without
promoting the candidate. R86 emits source-binding replay stdout for all `30`
selected G1 rows and verifies that every row still binds to the original
`gcm_h6` QASM source line hash and source-component id. Replay events `30/30`
are covered, line hashes verified `30/30`, and the candidate mapping remains
`600` T-ledger units with accepted T-ledger reduction `0`. The replay-aware
preflight now sets `replay_stdout_present=true`, but still rejects credit on the
three remaining gates: STV reprice ledger, filled R83 submission, and downstream
B7 replay. Transcript hash
`cbdee2263c4dac2e649d0677652cfef8b91eb88460ade8211546936869ce034d`;
stdout hash `4efe9839cafe6502f297afc0ab0a1d06f343e3da26c38eb5223dd0077a5f1004`;
preflight hash `71d6cf3d82d7d6dbc70de94a0a7dad9a1477f537254635a53dba6efc6a90f1e5`;
blocker queue hash `6a934fc9ec42e86b752426d5a7460c876eb7562224f12385c148c78355cc65a2`.
B7 credit remains `0`; this is replay-stdout binding only, not STV repricing,
same-unitary proof, or O3 closure.

`T-B1-004gk` / `T-B7-015t` now closes the next blocker by producing a
candidate STV/T-ledger reprice ledger for the R86 replay-bound G1 rows. R87
keeps all `30` selected rows replay-bound and prices the candidate bundle from
the R83 current-after-T ledger `6224` down to `5624`, a `600` unit candidate
reduction and `8` units below the `5632` 1.20x target ceiling. The
STV-aware preflight now sets `stv_reprice_ledger_present=true`, but still
rejects credit on the two remaining gates: filled R83 production submission and
downstream B7 replay. STV ledger hash
`6eeadbd0b333454e957b3f79dd8f06066950d8e997ea2a25ac70b887eebe369a`;
stdout hash `ba0335d3b4342375358e26d560977c8a562b33d2fbf4fd8f452b596d612aab7a`;
preflight hash `5bb78c88b7265a6af247b771d4ae0cc73938b4a9b7e39880b1ea8c8106fa064f`;
blocker queue hash `0b65c44240c6f14b6f9e754c6dc734c2972a69f596f6dd49b1842edf9d169562`.
B7 credit remains `0`; this is a candidate STV ledger, not a filled R83 packet,
downstream replay, or O3 closure.

`T-B1-004gl` / `T-B7-015u` now closes the filled-submission blocker by
materializing the G1 route as a complete R83 production packet. R88 fills all
`33/33` required fields, binds `10` evidence artifacts by SHA-256, and passes
all `10/10` R83 acceptance-shape gates. The candidate ledger still claims
`600` T-ledger units and `5624` after-T ledger with `8` units of margin below
the `5632` 1.20x target ceiling, but downstream B7 replay is still missing.
Evidence-bundle hash
`96e14ca9e5b97799ea503e4f3e8a7a32070ca42757ed1eb3b470f22beac2052e`;
filled-submission hash
`6ac1427a6c04a6ced8d9d1cb22461c7721fd755c5b1d4d01dc139bc4647d04e7`;
preflight hash `ca6d79111ba0d8dc950c2385c18f2902fa756d2a48970e627fbbdbe7160401fd`;
blocker queue hash `09e25308180ee3e41e2ce6f14ed737139b77f3c3a749a718f6617bdf731e44bc`.
B7 credit remains `0`; this is a filled R83 submission, not downstream replay,
resource-saving permission, reroute permission, or O3 closure.

`T-B1-004gm` / `T-B7-015v` now closes the downstream replay gate for the filled
R83 G1 submission. R89 replays the candidate against the current B7 proxy
FT/STV boundary and accepts exactly one narrow proxy credit: the `1.20x` target
is reached because the candidate path prices `6224 -> 5624`, leaving `8` units
of margin below the `5632` ceiling. The `1.25x` target remains false with
margin `-224`, and no physical-layout, O3, reroute, or resource-saving claim is
made. Replay-ledger hash
`4fa9daa77d27717e74965889eea20a0df05be43c9fdf68a5050348593f15b1f2`;
verdict hash `f9d7409a9f83f37e3f220b39fd22621f15a87e7f5ab319cdedc8fbfa782ba7f6`;
blocker queue hash `0aed27e6658d039295e9b76587c60e501d2cda2bddd81e531f5cd4d48f2d71b1`.
Accepted B7 credit is now `1` only in scope
`proxy_ft_stv_1_20_only`; this is not a claim that B7 is solved.

`T-B1-004gn` / `T-B7-015w` now adds the R90 independent review gate for that
R89 proxy credit. R90 recomputes the B7 replay arithmetic from the filled
R88/R83 submission and the current B7 boundary, reproduces the `6224 -> 5624`
candidate path, and finds no double-count violation in the accepted one-unit
proxy FT/STV credit. The review preserves exactly the R89 narrow credit:
`accepted_b7_credit_delta_after_review=1`, `new_credit_delta=0`, and
`revoked_credit_delta=0`. The `1.20x` margin remains `8`; the `1.25x` target
remains blocked with margin `-224`; O3 closure, reroute permission,
physical-layout evidence, and resource-saving claims all remain false.
Review-ledger hash
`ee61a303c275756871e1a9a9535803d8db911486e5f06aec47e049ed20b792a6`;
verdict hash `e62e53533dd9704ffef72501a161858b00b754cceb5b37a8cc619ef6aea63370`;
blocker queue hash `a3a74ced55860ffa04c7e36e15a8f0b7bde852132d77614cb99f17531758e36b`.
This is still a review/kill-test gate, not a B7 solution.

`T-B1-004go` / `T-B7-015x` now turns the R89/R90 proxy-credit review into an
external reproduction contract. R91 emits a fillable third-party submission
template with `28` required fields and `14` production-required fields, accepts
five review modes, and rejects the current empty submission on `6` preflight
gates with `12` missing production fields. Accepted external reproductions are
still `0`, accepted external falsifications are still `0`, and `new_credit_delta`
remains `0`. The inherited R90 margins remain `8` at `1.20x` and `-224` at
`1.25x`; O3 closure, physical-layout evidence, and resource-saving claims all
remain false. Contract hash
`ae6d508fdd10aa0e48e64800f08b48afe4b6c29d246b00a5640643ec972f2a76`;
template hash `2af8c0f624b493b159c4198fe4692aa5d2f52f92d6ba8cd15578e48c82ceeada`;
preflight hash `7fe0e695aaaf84115d98e8e8dc48ff94eb3e13a3a052bdba645f25aa19063ec6`;
blocker queue hash `1cc6567b04d3be2d0aad4e11749972e922607c98836f7eeabc3dec0d7258d7fb`.
This is a collaboration gate: it makes the one-unit proxy credit easier to
reproduce or kill, but it does not add evidence by itself.

`T-B1-004gp` / `T-B7-015y` now adds the R92 validator fixture for the R91
contract. R92 emits validator rules, a local environment manifest, a command
transcript, a double-count test, a filled fixture submission, and a fixture
preflight verdict. The fixture passes all `9/9` validator gates, including
schema, hash binding, arithmetic, double-count decision, and claim-boundary
safety, but it is explicitly marked as a local fixture and is not counted as
external reproduction or falsification. Accepted external reproductions remain
`0`, accepted external falsifications remain `0`, and `new_credit_delta`
remains `0`. Validator-rules hash
`49c4f245da0f16476a047c3c17935537adf62b256406ccd543f0bb4f0b4c65ec`;
fixture-submission hash
`8bd40bbfe6ae61cc4a02e1f1bbbd3d740289d7179a045243f782e73efcab86d0`;
fixture-preflight hash
`f1ccecdaba721a64ecda50eeb6a30499f4e1b17bd37009e3e3ebb5cac4ae3114`;
blocker queue hash `3fa0c8e96a5d086b0ec5c203ba7081f561e3f638860096bd8d2a3c5b35100e10`.
The next real gate is a non-fixture external submission.

`T-B1-004gq` / `T-B7-015z` now adds the R93 non-fixture external intake gate.
R93 converts the R92 validator into a stricter external packet path: it bans
the local fixture agent id `r92-local-validator-fixture`, emits a `33`-field
intake contract with `19` production-required fields, and rejects the current
empty packet on `7` preflight gates with `16` missing production fields.
Accepted external reproductions remain `0`, accepted external falsifications
remain `0`, and `new_credit_delta` remains `0`. Intake-contract hash
`0e1108d271259b7d602939e72b463695e7b0e7dd6a3685a3f7ee418dbb82e882`;
packet-template hash
`1bd5e493063e3af62daa04867be334cab8dcd751cab9c707258735664003f405`;
preflight hash `6ec529295cde9e66d34ba062b0203bb1fe01dc56e0f4c6d777c6d59dcbc2bfc3`;
blocker queue hash `ef1ee51bf9e5a542b5f34bdacabd236471c7700c4376c2ead7a61c6d9ee818e5`.
The next real gate is a filled non-fixture packet plus maintainer verdict.

`T-B1-004gr` / `T-B7-016a` now adds the R94 maintainer verdict and counter
contract gate. R94 takes the R93 non-fixture intake blocker and defines the
allowed maintainer verdict modes, evidence-sufficiency labels, counter targets,
credit decisions, and counter-transition rules before an external reproduction
or falsification counter can move. It emits a `24`-field verdict contract with
`15` production-required fields and a fillable verdict template. The current
empty maintainer verdict is rejected on `11` preflight gates with `11` missing
production fields. Maintainer verdict accepted remains `false`, counter delta
remains `0`, accepted external reproductions remain `0`, accepted external
falsifications remain `0`, and `new_credit_delta` remains `0`. Verdict-contract
hash `8b9628a69d93855f005cfe0ea554f7ee4e7d7f4e57c109568a77082097814040`;
verdict-template hash
`1abfe2eee37de29a06935f53c371892d1eb43f21c9d769d76851974084d97ff4`;
preflight hash `d857144c4623eb10eba2d69129349acd80ee71b5e25e4e923a572ee305992538`;
blocker queue hash `0f4774f61f1f607f934514f2d51bc09fd1ac2a3bf58bf031fb453b0d93027cad`.
The next real gate is a filled R93 packet plus a source-backed maintainer
review transcript.

`T-B1-004gs` / `T-B7-016b` now adds the R95 maintainer review transcript
intake gate. R95 turns the R94 verdict blocker into a source-backed transcript
contract: a real review transcript must bind the filled R93 packet hash,
command transcript, environment manifest, recomputed target rows, double-count
test, review notes, evidence-sufficiency label, counter target, proposed credit
decision, and claim boundary before any R94 verdict can count. It emits a `30`
field transcript contract with `18` production-required fields and `6`
evidence-file classes. The current empty transcript is rejected on `13`
preflight gates with `16` missing production fields. Review transcript accepted
remains `false`, maintainer verdict accepted remains `false`, counter delta
remains `0`, accepted external reproductions remain `0`, accepted external
falsifications remain `0`, and `new_credit_delta` remains `0`.
Transcript-contract hash
`a5b59461a201d0488075fb9436a7d8a85a5b9207591b3e0a6b0c1f3144b269e2`;
transcript-template hash
`26eaa32db7cf0557403e96de1e2e553d291149c9d44c2c0a829f9815d49caad1`;
preflight hash `881708dee9955519b1819027b0e49fb2c60cebd750a14255e81b3895b9de9383`;
blocker queue hash `e9929538c9e3557b0cccab0e2399ad42b87fda3f9ab8fd9b8516109138335767`.
The next real gate is a filled R95 transcript that can feed an R94 maintainer
verdict.

`T-B1-004gt` / `T-B7-016c` now adds the R96 review transcript validator gate.
R96 converts the R95 transcript contract into runnable validator rules for a
future source-backed maintainer review transcript. The validator inherits the
R95 `30` required fields, `18` production-required fields, `6` evidence-file
classes, and emits `18` validator gates. Running those rules on the current
empty R95 transcript rejects it on `13` gates with `16` missing production
fields. Review transcript accepted remains `false`, maintainer verdict accepted
remains `false`, counter delta remains `0`, accepted external reproductions
remain `0`, accepted external falsifications remain `0`, and
`new_credit_delta` remains `0`. Validator-rules hash
`9a0c3c7be2a9dc65a1ffc24d440c03f88a250999e666fbcc886109275cfc15e0`;
empty-validation hash
`ad2afc99328134a788d1b74bf36e55a87be2e261853199bc162fb85fe16b19f7`;
blocker queue hash `fe11597c8f0457188373df4c2c5d1e73911abaf5d01262c63494e359f33b5ddf`.
The next real gate is a filled R95 transcript that passes the R96 validator
before any R94 maintainer verdict can count.

`T-B1-004gu` / `T-B7-016d` now adds the R97 evidence-file materiality gate.
R97 hardens the R96 validator by requiring declared review evidence files to
exist and match their SHA-256 claims. It emits `10` materiality gates over `6`
evidence-file pairs, then generates a filled-looking spoof transcript with fake
hashes and missing files. The spoof is rejected on `5` materiality gates:
missing evidence paths, nonmatching evidence hashes, fake reviewed-packet hash,
fake reviewer-signature hash, and final materiality acceptance. Review
transcript accepted remains `false`, maintainer verdict accepted remains
`false`, counter delta remains `0`, accepted external reproductions remain `0`,
accepted external falsifications remain `0`, and `new_credit_delta` remains
`0`. Materiality-rules hash
`5a1392fe33f5069afae4d6422519842726059461307100a628eb051aff2809e5`;
spoof-transcript hash
`d4bd97bed0ee7a3c57a927aa27707e8838ba40da79ab7921e4ba78a433d8bebd`;
materiality-validation hash
`d77d17cd95c8130f8ff19a05cfb06a308437daa183f9b211c96481900cd987ba`;
blocker queue hash `86dd811d617c733bbba06642d6edd866645a8e2de2eab990df37e557c4008ff9`.
The next real gate is a filled transcript with real in-repository evidence
files whose bytes match every declared hash.

`T-B1-004gv` / `T-B7-016e` now adds the R98 placeholder evidence semantic gate.
R98 shows that file existence and SHA-256 materiality are necessary but still
not sufficient. It creates `6` real placeholder evidence files, builds a
filled-looking review transcript whose declared hashes match those files, and
then rejects it on `7` semantic gates because the files contain placeholder
content instead of a substantive replay command, recorded environment identity,
nonempty recomputed rows, explicit double-count decision, and review rationale.
Review transcript accepted remains `false`, maintainer verdict accepted remains
`false`, counter delta remains `0`, accepted external reproductions remain `0`,
accepted external falsifications remain `0`, and `new_credit_delta` remains
`0`. Bundle-manifest hash
`03a555b70877a9add69d3057b6c8561990d611e167b4aed946c1cb5fb11d0146`;
placeholder-transcript hash
`bb13801253d24e26624eecd96ddfa1bb7badaf0901aae770ee3ae134ff008e18`;
semantic-validation hash
`2fd9959eb5b9741ba0c32714bd8d5d4e5d7089bf7ec9a9d1558edd56d7a4c6d1`;
blocker queue hash `68f0f0e8f86e34ee3e4e36ddb35afad48488e4dcff6a06c250f33feb491125aa`.
The next real gate is a non-placeholder evidence bundle with an actual replay
command, recorded environment, recomputed rows, double-count decision, and
review rationale.

`T-B1-004gw` / `T-B7-016f` now adds the R99 substantive evidence intake gate.
R99 turns the R98 negative control into a positive semantic-intake packet. It
emits `6` non-placeholder evidence files, binds their bytes into a review
transcript, verifies replay command, environment identity, nonempty recomputed
rows, explicit double-count decision, review rationale, non-placeholder packet
and signature hashes, zero direct credit, and safe claim boundary, then marks
the transcript ready for a later R94 maintainer verdict. Semantic validation
accepted is `true`; review transcript accepted is `true`; ready for maintainer
verdict is `true`; maintainer verdict accepted remains `false`; counter delta
remains `0`; accepted external reproductions remain `0`; accepted external
falsifications remain `0`; and `new_credit_delta` remains `0`.
Bundle-manifest hash
`a4f4bc83d555bda4cc80fdc59716e103396bb245a024d1426c7ea30a341565bd`;
review-transcript hash
`299da9741c918757081e42db960cda56f186ae01f5fcd2cd2a60748046c89ae2`;
semantic-validation hash
`bc476af1df2712aa78fc543b548cdf2f61d72edb2feb27c1f401a31b89e4352c`;
verdict queue hash `6bb1b3de4e396dabd9802f8cc910a234906422f005235e2a5fb6b0f1991fadc5`.
The next real gate is an R94 maintainer verdict that references the accepted R99
transcript and semantic-validation hashes, ideally rerun from a clean checkout
and reviewed by an independent reproduction/falsification agent.

`T-B1-004gx` / `T-B7-016g` now adds the R100 maintainer verdict no-counter
gate. R100 consumes the accepted R99 semantic-intake packet and emits an
R94-shaped maintainer verdict. The verdict is accepted as a no-counter decision:
it preserves the already reviewed one-unit proxy FT/STV credit, but it does not
increment external reproduction or falsification counters, does not grant new
B7 credit, and does not close O3, resource-saving, or physical-layout claims.
R100 passes `7/7` requirements and `13/13` verdict-validation gates. Maintainer
verdict accepted is `true`; counter delta remains `0`; accepted external
reproductions remain `0`; accepted external falsifications remain `0`; and
`new_credit_delta` remains `0`. Verdict hash
`20bd06ba2b0888eb6ead5b504c7e57ab010cbecac956597966c7e8e92135c779`;
verdict-validation hash
`76d0b46592318027706bfd18f4d977adc40e063d1cc37a1f200a7c5719507ff9`;
blocker queue hash `81456ba48b081cf12135caa94e9789e782dfacfe796f675ed76d218051c44151`.
The next real gate is an independent clean-clone rerun and an explicit external
reproduction or falsification decision that can move exactly one external
counter without touching B7/O3/resource/layout claims.

`T-B1-004gy` / `T-B7-016h` now adds the R101 clean-clone rerun gate. R101
checks out the current project into a clean local clone, reruns the R100
maintainer no-counter verdict script, and compares stable verdict, validation,
and blocker hashes. The clean-clone rerun reproduces those stable hashes and
keeps the no-counter boundary intact. Requirements pass `5/5`; clean-clone
comparison gates pass `8/8`; maintainer verdict accepted remains `true`;
counter delta remains `0`; accepted external reproductions remain `0`;
accepted external falsifications remain `0`; and `new_credit_delta` remains
`0`. Manifest hash
`dd4efc1db388f83e83e9e4353c46400e4817f29dd1c340a01ceb2df07a718540`;
comparison hash
`21eb86eb046bb392f47d183f7b9a7690e8e127d01b1ff545d206a8629f553900`;
blocker queue hash `459d9c4cfdafa7be6d41bbb7196b4d59e91b38d09d5d8e4a5140814c7732b9da`.
R101 is still not a third-party external reproduction. The next real gate needs
an independent reviewer identity and an explicit counter-transition decision.

`T-B1-004gz` / `T-B7-016i` now adds the R102 external reviewer identity
contract gate. R102 turns the R101 blocker into a concrete identity and
counter-decision contract, emits a fillable external counter-decision template,
and tests it with a local surrogate reviewer negative control. The surrogate is
rejected because it is not independent and does not attach independent replay
artifacts. Requirements pass `5/5`; preflight gates pass `5` and fail `3`;
external reviewer identity accepted is `false`; counter transition accepted is
`false`; counter delta remains `0`; accepted external reproductions remain `0`;
accepted external falsifications remain `0`; and `new_credit_delta` remains
`0`. Identity-contract hash
`4a69fde0559dc679fb54ae666aae172f8824500710dbcb0ec27930978c78cd2c`;
decision-template hash
`14a6524224be397c1149ab28a913d7c6e130f3142bc46d9104b1fef213ee2bb3`;
preflight hash `005c4c0c3a9890aa7947ef7f9db04ea13c8057e4e56ea2e3dc21fc674bdc13b5`;
blocker queue hash `548a368637e12a9d9e2fef78c6eea955688144f082b8cb104da301ad89ff4df1`.
The next real gate is a real independent reviewer packet with environment,
clean-checkout transcript, and exactly one audited external counter transition.

`T-B1-004ha` / `T-B7-016j` now adds the R103 external counter transition audit
gate. R103 fills the R102 decision template with a packet that requests `+1`
accepted external reproduction, but rejects it because the packet reuses
repo-local R101 clean-rerun artifacts and has no external-origin attestation.
Requirements pass `5/5`; audit gates pass `7` and fail `3`; claimed counter
delta is `1`; claimed external packet rejected is `true`; counter transition
accepted is `false`; counter delta remains `0`; accepted external reproductions
remain `0`; accepted external falsifications remain `0`; and
`new_credit_delta` remains `0`. Claimed-decision hash
`cff5f2c1ced3854bb0eccb4fb32ad72824f73b94420af5ab13e549761ad4e9b7`; audit
hash `2de6e6a2b8234af2e82c3e4af09296c5492054c7e0fbe6703bc1e7697bd2dc51`;
blocker queue hash `876d3e77f00c0676c3d57eeeedef6896df05c1ac244b146d3ef5d6ed7bc027ba`.
The next real gate must supply external-origin attestation, nonlocal replay
artifacts, and an audit that accepts exactly one reproduction or falsification
counter transition without moving B7/O3/resource/layout claims.

`T-B1-004hb` / `T-B7-016k` now adds the R104 external-origin attestation
contract gate. R104 turns the R103 origin blocker into a concrete 20-field
attestation contract and fillable template, then rejects a local placeholder
attestation that reuses R101/R103 local artifacts. Requirements pass `5/5`;
preflight gates pass `5` and fail `7`; local placeholder rejected is `true`;
origin attestation accepted is `false`; counter transition accepted is `false`;
counter delta remains `0`; accepted external reproductions remain `0`;
accepted external falsifications remain `0`; and `new_credit_delta` remains
`0`. Origin-contract hash
`9150bfda0b040365f0fb3bce12ee91f4e968f01f742a483d6b7ddb6a80b9b485`;
attestation-template hash
`3159b7162402eb1cfb2b6b482c87d7dfde3e95756fe5312cb002e891abf6d6d0`;
preflight hash `76183801f092c26e9c2e9d88ea4821f2429007959d6604ba13e1367e165ddd2c`;
blocker queue hash `53a9922bdb7218bfb52cabb7005b7328cc8cad0a81707835baf299b377c26a25`.
The next real gate must fill the R104 template with signed external-origin
attestation, a nonlocal clean-checkout bundle, and a single-counter transition
audit.

`T-B1-004hc` / `T-B7-016l` now adds the R105 external-origin attestation
verifier gate. R105 converts the R104 20-field attestation contract into 16
executable verifier gates, rejects the empty R104 template, and rejects the
local placeholder packet on nonlocal-origin checks. Requirements pass `5/5`;
empty-template origin accepted is `false` with `14` failed gates; local
placeholder origin accepted is `false` with `8` failed gates; counter transition
accepted is `false`; counter delta remains `0`; accepted external reproductions
remain `0`; accepted external falsifications remain `0`; and
`new_credit_delta` remains `0`. Verifier-rules hash
`5a94f79d40e3afcc8d5459843c07cc8dffa7241b3ae34b9ebf687cca41c9e89e`;
template-validation hash
`37fd78884fa792dc9c4dae511b66e999fd12efd35a73744852744fec5d3559a7`;
placeholder-validation hash
`dc6ff64dba76c7e11a3bd26e7260539c04d7ec7ca16b272e5b11518faee95b01`;
blocker queue hash `9aa6e3af7f3c7ae95ee56c100bb6052cfd98a10218517035e04ab2f34f8cd7d3`.
The next real gate is a production R104 packet that passes the R105 verifier
before a separate single-counter audit is allowed to move any counter.

`T-B1-004hd` / `T-B7-016m` now adds the R106 remote-origin materiality gate.
R106 builds a remote-looking R104 packet that passes the R105 surface verifier
on all `16/16` gates, then rejects it because reviewer-key registry, detached
signature verification, third-party CI run, remote artifact-fetch transcript,
and independent reviewer contact evidence are absent. Requirements pass `5/5`;
R105 surface origin accepted is `true`; remote-looking spoof rejected is
`true`; material origin accepted is `false`; materiality gates pass `1` and
fail `7`; counter transition accepted is `false`; counter delta remains `0`;
accepted external reproductions remain `0`; accepted external falsifications
remain `0`; and `new_credit_delta` remains `0`. Remote-looking packet hash
`76a6aed9a8564b2362bbd8edccc9181def1f59046ce74c432e6300017c6d6532`;
surface-validation hash
`8e7f72ea50b23ef6b79b9267f2673795aef2e83d5580c435533295223a653621`;
materiality-audit hash
`f9b520d2fbc43860bcc74f6a23a76b85cacdc4fbbc171e17a048af31b41dc20a`;
blocker queue hash `409e093e4343a901debbc1701065919e6bdeb4971b50419e68316b459dd2e265`.
The next real gate must attach reviewer-key registration, detached signature
verification, public third-party CI evidence, and remote artifact-fetch
transcripts before a counter audit can move.

`T-B1-004he` / `T-B7-016n` now adds the R107 material evidence packet contract
gate. R107 converts the R106 materiality blockers into a fillable external
evidence packet contract with `30` required fields and `22` acceptance gates.
It rejects the empty template with `5` gates passing and `18` gates failing,
and rejects a self-declared packet that reuses the R106 negative-control
artifact with `18` gates passing and `5` gates failing. Requirements pass
`6/6`; counter transition accepted is `false`; counter delta remains `0`;
accepted external reproductions remain `0`; accepted external falsifications
remain `0`; and `new_credit_delta` remains `0`. Contract hash
`922ff2fd88cc03fba5a073d5273d9d89f4d2a60790843cc3a87759acf139acfb`;
template hash `6112970d00936f01422ac75a3b7be44f1274b29661e7990fee2f2896cc8629ba`;
empty-template preflight hash
`66e69a29eaa3a2e080e5b86a10ad29cfec8fc600e9cfe99b630eb4e3c9a63584`;
self-declared preflight hash
`6683c248ee5c3cbaa34a111c10db0216eb3d53549ebb68478d4cd1899556fba4`;
blocker queue hash `b9fbd3e09273a83ccea2ce23f323b6bd56a425946805a7cd871069de4fb56734`.
The next real gate must submit a filled material evidence packet with public
reviewer-key registry, detached signature verification transcript, public
third-party CI log, remote artifact-fetch transcript, fetched artifact
manifest, environment manifest, and reviewer-contact verification before a
separate single-counter audit can move.

`T-B1-004hf` / `T-B7-016o` now adds the R108 material evidence preflight
verifier gate. R108 turns the R107 contract into hardened verifier rules with
`24` gates, materializes a field-complete near-pass packet with `10` evidence
files and matching hashes, then rejects it because the evidence is explicitly
local synthetic rather than public third-party material. Requirements pass
`6/6`; near-pass packet accepted is `false`; near-pass gates pass `23` and
fail `2`; failed gates are `local_synthetic_marker_absent` and
`material_evidence_packet_accepted`; counter transition accepted is `false`;
counter delta remains `0`; accepted external reproductions remain `0`;
accepted external falsifications remain `0`; and `new_credit_delta` remains
`0`. Verifier-rules hash
`4edf2f0114ed4854db58e1a20ce5276f1be7090503600a3f4c3a89a9d8aa692e`;
near-pass packet hash
`14466067f86a077da82a0d31b9ddb41739ee523b797f42fc1550b62dc4f04f9a`;
preflight-verdict hash
`e310d3948c9ead61a44383ec5e80da78cbe493c09964169cf2ad3703dee989a1`;
evidence-manifest hash
`017ee34db31ca2c5dd8f1505a42f40cbdcb99b46f1d100abb3d04b3f8d8f43a2`;
blocker queue hash `7ff0fa3784990b1d005f05d4e5a1349cd127913b7b24bebfbbb2888fb9754033`.
The next real gate must replace the local-synthetic support files with public
third-party artifacts and rerun the R108 verifier before any separate
single-counter audit.

`T-B1-004hg` / `T-B7-016p` now adds the R109 public artifact dereference
contract gate. R109 hardens the R108 blocker into a challenge-nonce contract
for live public artifact dereferencing: public URLs alone do not count, and
cached local transcripts do not count. The gate emits a 16-field public
dereference contract plus packet template, rejects a URL-only packet, rejects a
cached-transcript packet, and keeps every reproduction/falsification counter at
zero until live HTTP transcripts are attached to the reviewer key, CI run, and
artifact URLs and bound to the R109 challenge nonce. Requirements pass `6/6`;
URL-only packet accepted is `false`; cached-transcript packet accepted is
`false`; counter transition accepted is `false`; counter delta remains `0`;
accepted external reproductions remain `0`; accepted external falsifications
remain `0`; and `new_credit_delta` remains `0`. Contract hash
`85fada945943cce2e57ac18e82670cc44d8cc5c8ac038fe998e9cf82deb6700e`;
template hash `c5ea8379e8a697435e89bee499822f7c6fe759c9237fbae7a4dfb27067ae43cf`;
URL-only preflight hash
`a2638f4a8c1fffa7432651a584102df8f045f5a58c9854382e98ecf62a45e59c`;
cached-transcript preflight hash
`e2152d8d4ab82fe056c129c66d1e4078b7b20ee4972d7e861e9e0dd8f72741c8`;
blocker queue hash `bf746fd1618e4305cf311640f476e265b98b56ef56a5abc4b8d487b7ca9cd168`.
The next real gate must attach live public HTTP transcripts for the reviewer
key, CI run, and artifact URL, bind those transcripts to the R109 challenge
nonce and requested URLs, rerun R109/R108, then run a separate single-counter
audit.

`T-B1-004hh` / `T-B7-016q` now adds the R110 live public dereference probe
gate. R110 takes the R109 URL-only negative-control URLs and attempts
unauthenticated public `curl` fetches for the reviewer key, CI run, and artifact
URL. All three fetches produce requested-url-bound public transcripts, but only
two complete with `404 Not Found`; no response is HTTP `2xx`, and none contains
the R109 challenge nonce. Requirements pass `6/6`; public fetch attempts are
`3`; completed fetches are `2`; HTTP `2xx` fetches are `0`; nonce-bound transcripts
are `0`; dereference packet accepted is `false`; counter transition accepted is
`false`; counter delta remains `0`; accepted external reproductions remain
`0`; accepted external falsifications remain `0`; and `new_credit_delta`
remains `0`. Verdict hash
`73eb0190dbde80d22294d2699507b75010812047f681ffad8dd128fe99cd6b6a`;
blocker queue hash `f888da6ab51011883e7ec74daf9f6963e54613cb5dd132266b835c718af21cd9`.
The next real gate must replace those public-looking placeholder URLs with
real public HTTP `2xx` reviewer-key, CI-run, and artifact transcripts that bind
the R109 challenge nonce before R109/R108 or any single-counter audit can pass.

`T-B1-004hi` / `T-B7-016r` now adds the R111 independent-origin materiality
gate. R111 fetches three immutable raw URLs that all return HTTP `2xx`, bind the
R109 challenge nonce, and bind their requested URLs. It still rejects the packet
because all three origins are the same project repository and the bodies remain
self-attested or synthetic. Requirements pass `8/8`; materiality accepted is
`false`; counter transition accepted is `false`; counter delta remains `0`;
accepted external reproductions remain `0`; accepted external falsifications
remain `0`; and `new_credit_delta` remains `0`. Verdict hash
`d770967e949d18682a3f5aba20a09dba5ed43c6b204847cf1388d2a463cb2461`;
blocker queue hash `9b6b707ea3d984b62bcf8a41d7fc5c9aee22d91fd72d5da42c2d28a0e514e81b`.
The next gate requires an independent reviewer key, third-party CI transcript,
and externally attested artifact transcript outside the project repository.

`T-B1-004hj` / `T-B7-016s` now adds the R112 exact replay qubit guard. The
13-qubit `gcm_h6.qasm` workload is deliberately rejected by the explicit
`max-qubits=12` guard, then passes exact statevector equivalence at
`max-qubits=13`. The fixed-point local rewrite removes `1,297` one-qubit
operations, reduces logical depth by `40.0899%`, and reduces hardware exposure
by `9.9003%`; the two-qubit gate delta is `0`, so no T-resource, layout, or B7
credit is claimed. Requirements pass `8/8`; counter delta remains `0`; and
`new_credit_delta` remains `0`. The next technical gate is a composable
full-circuit semantic certificate with a nonzero two-qubit or proxy-T delta
under the same denominator.

`T-B1-004hk` / `T-B7-016t` now adds an adversarial two-qubit reduction gate.
Qiskit level 3 produces a visually attractive candidate on `gcm_h6.qasm` with
CX count `762 -> 528`, a `30.7087%` reduction. The exact statevector checker
rejects it: equivalence is `0/1` and the first failed fidelity is `0.5`.
Candidate acceptance is `false`; counter delta and `new_credit_delta` remain
`0`; no B7 credit is granted. Requirements pass `8/8`. The result sharpens the
next target: find a composable candidate that passes exact equivalence while
retaining a nonzero two-qubit or proxy-T delta under the same denominator.

`T-B1-004hl` / `T-B7-016u` now adds the R114 optimization-level sweep. On the
same 13-qubit workload, levels 0 and 1 preserve exact equivalence with CX
count `762`; levels 2 and 3 reduce CX to `528` but both fail exact equivalence
with fidelity `0.5`. No nonzero-2Q level is accepted; counter delta and
`new_credit_delta` remain `0`; no B7 credit is granted. Requirements pass
`8/8`. The next target remains a composable semantic rewrite that passes exact
equivalence and retains a real two-qubit or proxy-T delta.

`T-B1-004hm` / `T-B7-016v` now adds the R115 measurement-semantics 2Q gate. The
same level-2 candidate reduces CX `762 -> 528`; it fails full-state equivalence
with fidelity `0.5`, but preserves the fixed-initial-state final measurement
distribution with L1 delta `3.89e-15` and max probability delta `1.94e-15`.
This is accepted only as a narrow B1 measurement-scope result. It does not
support arbitrary-input/full-state equivalence, mid-circuit measurement
semantics, hardware layout, T-resource, or B7 credit; B7 credit remains `0`.
Requirements pass `8/8`.

`T-B1-004hn` / `T-B7-016w` now adds the R116 measurement-detached exact 2Q
gate. R116 removes the terminal measurement before Qiskit optimization, compiles
the 13-qubit quantum core, and restores the original classical measurement map.
The candidate keeps the R115 CX count `762 -> 528` (`30.7087%`), passes the
default statevector replay with fidelity `1.0`, passes `22/22` finite input
probes with maximum fidelity deficit `9.99e-15`, and passes final measurement
distribution replay with L1 delta `3.83e-15`. This is a materially stronger
B1 candidate, but it is still finite-probe evidence rather than an arbitrary-input
unitary proof; mid-circuit measurement semantics, hardware layout, T-resource,
and B7 credit remain outside the claim boundary. Requirements pass `10/10`;
B7 credit remains `0`.

`T-B4-002bn` / `T-B8-003br` / `T-B10-009bf` now preregisters R153 as an
independent hidden-seed replication of the accepted R152 routes. No route is
selected, fitted, or changed: Casablanca replays the R152 novel-signature
route, while Nairobi and Perth preserve their accepted controls. The unopened
challenge expands each backend from 8 to 32 hidden trials in four independent
8-row blocks, for 96 rows, 288 executions, and 589,824 shots. Acceptance keeps
the R152 group floors, adds a 10/12 block-stability floor at -0.03, and caps
within-backend block spread at 0.08. Contract `99aae340...`; this is a frozen
replication test, not a hidden result, causal proof, temporal or real-device
transfer, hardware performance, general route-generation advantage, quantum
advantage, BQP separation, solved-frontier status, or new credit.

The R153 holdout at `T-B4-002bo` / `T-B8-003bs` / `T-B10-009bg` is
preregistered ACCEPT with A1-A10 and P1-P10 passing. The accepted R152 routes
were replayed unchanged across 96 hidden rows, 12 independent blocks, 288
same-seed three-arm executions, and 589,824 shots. Portfolio repaired-automatic
mean/bootstrap lower are `+0.02595381` / `+0.02209900`; repaired-denominator
mean/bootstrap lower are `+0.00327876` / `+0.00170832`. All `3/3` backend means
clear `-0.02`, all `12/12` block means clear `-0.03`, the maximum
within-backend block-mean spread is `0.00609251`, and no row falls below
`-0.05`. Casablanca remains slightly below the strong denominator on average
at `-0.00337217`, while Nairobi and Perth remain positive at `+0.00860058` and
`+0.00460786`. A stable full replay matches all `96/96` rows and `4/4` phase
artifacts. An earlier generation-to-first-replay comparison matched only `2/4`
phase artifacts because the fresh-automatic mean moved by about `2.2e-6`; no
acceptance condition changed. Payload hash `3f48a8ac...`. This supports one
independent hidden-seed replication of the finite R152 simulated-noise result,
with an open execution-reproducibility caveat that requires per-row automatic
circuit hashes and serial Aer execution in the next gate. It is not causal
proof, temporal or real-device transfer, hardware performance, general
route-generation advantage, quantum advantage, BQP separation, solved-frontier
status, or new credit.

`T-B4-002bp` / `T-B8-003bt` / `T-B10-009bh` now preregisters R154 as a
fail-closed deterministic replay of the R153 execution surface. It creates no
new hidden statistical evidence and changes no route. Instead, two separate
operating-system processes must replay the same 96 public R153 seed rows under
serial Aer controls, for 576 total circuit executions and 1,179,648 shots.
Every fresh automatic circuit receives a normalized OpenQASM 3 hash; every arm
count vector, scientific row, backend target, and fixed route receives an
independent canonical hash. Acceptance requires `96/96` automatic QASM,
`288/288` arm-count, `96/96` row, `3/3` backend-target, and `6/6` fixed-route
hash matches with zero mismatches. Python, Qiskit, Aer, runtime, deterministic
environment variables, and one-thread/experiment/shot Aer settings are frozen.
Protocol requirements pass `10/10`; contract `1ef1f7be...`; execution remains
unopened. This does not yet close the R153 replay caveat and does not support
new statistical evidence, hardware performance, temporal or real-device
transfer, general route-generation advantage, quantum advantage, BQP
separation, solved-frontier status, or new credit.

The R154 execution at `T-B4-002bq` / `T-B8-003bu` / `T-B10-009bi` is
ACCEPTED under the newly frozen serial controls. Two independent operating-
system processes replayed all 96 public R153 rows, producing exact matches for
`96/96` automatic OpenQASM 3 hashes, `288/288` arm-count hashes, `96/96`
scientific-row hashes, `3/3` backend-target hashes, `6/6` fixed-route hashes,
and all `10/10` R153 acceptance decisions. The reference pass also matched
`96/96` stored R153 scientific rows, and the cross-process comparison recorded
zero total mismatches. Requirements and acceptance conditions pass `10/10`;
payload hash `dacd880f...`. This closes the serial replacement-replay caveat
for this finite execution surface. It does not explain or prove deterministic
the original R153 default-parallel path, whose transient drift remains open,
and it adds no new hidden statistical evidence. It is not hardware evidence,
temporal or real-device transfer, general route-generation advantage, quantum
advantage, BQP separation, solved-frontier status, or new credit.

`T-B4-002br` / `T-B8-003bv` / `T-B10-009bj` now preregisters R155 as a
`2 x 2` execution-mode attribution matrix for the unresolved R153 transient.
It crosses one-thread versus four-thread process environments with explicit
serial Aer options versus the R153 code-equivalent default-Aer path. Each of
the four cells must run twice in separate operating-system processes, replaying
the same 96 public R153 rows without new seeds, route changes, or selection.
The unopened gate fixes 8 processes, 768 row executions, 2,304 circuit
executions, and 4,718,592 shots. Every process must hash every automatic
OpenQASM 3 circuit, all three count vectors, and every scientific row, then
enter four within-cell, seven serial-reference, and eight stored-R153
comparisons. Diagnostic completion does not require zero mismatches: any drift
must be recorded and classified rather than discarded. Requirements pass
`10/10`; contract `76f7939c...`; execution remains unopened. No causal
attribution, new hidden evidence, temporal or real-device transfer, hardware
performance, general route-generation advantage, quantum advantage, BQP
separation, solved-frontier status, or new credit is claimed.

The R155 matrix at `T-B4-002bs` / `T-B8-003bw` / `T-B10-009bk` is
diagnostically complete with A1-A10 and P1-P10 passing. All 8 independent
processes completed 768 rows, 2,304 circuit executions, and 4,718,592 shots.
Three of four cells were internally unstable: the matrix records 9
within-cell component mismatches, 15 serial-reference mismatches, and 3 stored-
R153 core-row mismatches. Every mismatch is the same `FakeNairobiV2` trial 21
automatic arm. The repaired and denominator routes and counts remain stable,
while automatic compilation alternates between exactly two OpenQASM 3 hashes.
Those variants shift automatic fidelity by `0.000210775927`; one affected row
among 96 implies a portfolio-mean shift of `2.195582577e-6`, reproducing the
scale of the documented R153 transient. The first observed divergence is thus
automatic transpilation, which excludes an Aer-sampling-only explanation for
these mismatches. It does not identify which lower-level compiler mechanism is
causal: three unstable cells block the preregistered single-factor attribution.
Payload `4b4556c8...`; next pressure must capture both QASM variants and run an
expanded repeated-transpile block for the one affected row. No new hidden
evidence, temporal or real-device transfer, hardware performance, general
route-generation advantage, quantum advantage, BQP separation, solved-
frontier status, or new credit is claimed.

`T-B4-002bt` / `T-B8-003bx` / `T-B10-009bl` now preregisters R156 as a
pass-level capture of the sole R155 mismatch row: `FakeNairobiV2` trial 21.
Thirty-two independent operating-system processes must each compile that
public row once under Qiskit 2.4.1, optimization level 3, transpiler seed
`105203961`, and the same one-thread environment. Every process must retain its
complete pass callback trace, bounded property-set summaries, final OpenQASM 3
artifact, process identity, and runtime; no simulation or sampling is run.
Diagnostic completion does not require the two R155 variants to reappear: one,
two, or more final hashes must be retained without exclusion. If multiple
variants occur, the gate must emit the first aligned circuit and property-set
divergence plus a structured final-circuit diff. Requirements pass `10/10`;
contract `04911bf4...`; execution remains unopened. A first divergent pass is
an observed localization boundary, not a compiler mechanism or Qiskit-bug
claim. No hidden evidence, hardware performance, temporal or real-device
transfer, general route-generation advantage, quantum advantage, BQP
separation, solved-frontier status, or new credit is claimed.

The R156 execution at `T-B4-002bu` / `T-B8-003by` / `T-B10-009bm` is
diagnostically complete with A1-A10 and P1-P10 passing. All 32 independent
operating-system processes completed one seeded compilation and retained 50
callback rows each, for 1,600 total pass records and zero simulations or
shots. Both R155 OpenQASM 3 variants reappeared without unknown variants: the
305-operation class occurred in 20 processes and the 307-operation class in
12. Every pass sequence is identical. The bounded property sets first diverge
after callback 17 `VF2PostLayout`, where only `post_layout` differs: logical
qubits 4 and 6 exchange the physical endpoints 0 and 2. Callback 18
`ApplyLayout` is the first point where the circuit hashes differ. Both final
circuits have depth 133 and 63 CX gates; their RZ counts are 132 and 134. This
is a reproducible pass-level localization boundary, not proof that
`VF2PostLayout` is the lower-level source of nondeterminism or that Qiskit has
a confirmed bug. Payload `3cf4927f...`; no hidden evidence, simulation or
hardware performance, temporal or real-device transfer, general route-
generation advantage, quantum advantage, BQP separation, solved-frontier
status, or new credit is claimed.

`T-B1-004hq` / `T-B7-016z` now adds the R119 dual-engine compositional replay
gate. The R116 source/candidate pair is sent through Qiskit Statevector and the
independent NumPy engine on 24 structured inputs; all `24/24` source/candidate
rows and both-engine cross-checks pass. Each circuit is split at one-third,
one-half, and two-thirds of its gate stream, producing `48/48` prefix/suffix
composition passes that reconstruct the unsplit output. An inserted `X`
negative control fails `8/8`. CX remains `762 -> 528`, while formal
arbitrary-input equivalence, hardware layout, T-resource reduction, and B7
credit remain outside the claim boundary. Requirements pass `10/10`.
