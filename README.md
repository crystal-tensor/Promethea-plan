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

B4/B8 now has the first verifier-private predicate pressure gate on top of
that support-spoofer boundary. The gate adds four late-bound private predicate
bits to the same 36 pilot circuits and 4 spoofer families. In the no-leakage
analytic model, public support-only acceptance falls from 1.0 to 0.0625, a
16x guessing burden. The leakage boundary remains explicit: leaking one private
predicate bit raises acceptance to 0.125, and full predicate leakage returns
acceptance to 1.0. This is useful protocol pressure, not hardware execution,
not cryptographic or protocol soundness, not sampling hardness, not quantum
advantage, and not a BQP separation claim.

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
