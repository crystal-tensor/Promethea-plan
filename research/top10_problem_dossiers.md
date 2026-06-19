# Top 10 Problem Dossiers v0.1

Last updated: 2026-06-19

Purpose: turn the Top 10 attack directions into reviewable research dossiers.
Each dossier states what we are trying to solve, why the problem remains hard,
where the problem lineage comes from, what earlier approaches achieved, what
our proposed route is, what has already been completed in this workspace, and
what still has to happen before anyone can claim a serious solution.

Important limitation: these are research plans and artifact statuses, not solved
world problems. The progress score is an internal artifact-maturity estimate.

## Progress Scale

| Score band | Meaning |
|---:|---|
| 0-10 | Problem framed; no credible reproducible artifact yet. |
| 11-25 | Toy/proxy artifact exists and can be audited locally. |
| 26-45 | Reproducible baseline plus measurable delta exists, with limitations. |
| 46-70 | Strong baseline comparison and partial external-style validation. |
| 71-90 | Manuscript-grade evidence across broad benchmarks or formal targets. |
| 91-100 | Community-grade solution candidate; requires independent validation. |

## B1: Hardware-Aware Quantum Circuit Compression

**Problem ID:** 25

**What we are solving:** compile the same quantum algorithm into fewer
two-qubit gates, lower depth, lower error exposure, and a device-compatible
layout while preserving auditable semantic equivalence.

**Lineage and unresolved age:** the lineage runs through universal quantum gate
decomposition and quantum compilation, with representative milestones including
Barenco et al. on elementary gates and SABRE-style NISQ qubit mapping. As a
general compilation optimization problem it has been open for roughly 30 years;
as practical hardware-aware NISQ compilation it has been active for about a
decade.

**Why it remains hard:** routing, commutation, measurement/reset semantics,
native gate sets, device topology, and noise are coupled. A transformation that
reduces gate count can still increase real error if it uses bad couplers or
creates idle-time exposure. Exact equivalence checking also becomes expensive as
circuits grow.

**Earlier approaches and milestones:** peephole rewriting, phase-polynomial
optimization, ZX-calculus, SAT/SMT synthesis, tensor equivalence, Qiskit/tket
transpilers, and SABRE/LightSABRE mapping. The field moved from abstract gate
count reduction to topology-aware and noise-aware compilation.

**Our proposed route:** proof-logged local rewrites plus measurement-aware
virtual-SWAP elimination, followed by post-virtual-SWAP 1Q resynthesis to test
whether B1 can also touch non-Clifford/T-resource proxies. Every reduction must
emit replayable proof events and must be checked against exact or
measurement-distribution semantics where possible.

**Completed here:** 30/30 circuits rewritten; 481 virtual SWAPs and 1443 CX
gates removed; two-qubit count reduced by 37.18%; exposure reduced by 32.65%;
proof replay passed on 481/481 events; local and end-to-end Aer failures are 0.
A post-virtual-SWAP 1Q pass removed 60 additional gates, reduced the logical
T-count proxy 1.018x and T-depth proxy 1.015x, and passed 30/30 Aer
cross-checks. Later control-RZ and U3 phase-factored diagnostics exposed
additional T-resource proxy improvements. The B1/B7 `gcm_h6` target selector
now counts 270 arbitrary decimal rotations, and the cone-feasibility gate shows
3 target cone classes covering 111 occurrences. Strict direct
CNOT-rotation-CNOT sandwiches total only 4, but `cone_01` has 35 pair-local
single-arbitrary windows and is the only cone class meeting B7's 30-occurrence
target under that stricter local-window criterion. No rewrite, semantic
certificate, or resource saving is claimed yet. The restricted `cone_01`
phase-removal gate then tests all 35 windows under remove-only, fixed-Z, and
continuous-RZ same-envelope replacement; all three routes have 0 exact-pass
windows at tolerance 1e-8, with best continuous-RZ residual
0.36435162331705345. This closes the simple phase-absorption route without
proving a global obstruction theorem. The Euler-reabsorption gate then locks
the arbitrary RY to 9 exact/Clifford-like candidate angles while neighboring
target-qubit RZ phases reoptimize; it still finds 0 exact-pass windows, with
best/median residual 0.21253656711362606 / 0.3643516233170531.
The parameter-transfer obligation gate then checks all 35 `cone_01` windows:
every original `RY(theta)` has nonzero projective unitary sensitivity, 0
angles are near the pi/4 exact grid, and 4 distinct theta groups cover the
windows. This does not prove a KAK lower bound or produce a rewrite, but it
prevents no-carrier deletion from being counted as B7 savings.
The theta-sharing ledger gate then converts those 4 groups into accounting
pressure: 31 duplicate theta occurrences create an optimistic 620 proxy-T
cache-reuse signal, but the accepted occurrence ledger still counts 0 removed
occurrences and 0 proxy-T reduction. This is a guardrail, not a resource-saving
claim.
The physical cost-model gate then checks whether that cache signal can already
be promoted into countable B7 savings. A follow-up shared-theta synthesis object gate defines 4 machine-readable
object proposals covering all 35 windows, a replay-verifier gate now checks
4/4 objects and 35/35 occurrences against source QASM and parameter-transfer
groups with 0 mismatches, and a logical layout/routing scaffold assigns route
packets for all 35 occurrences. This upgrades the cost-model scaffold from 0/8
to 6/8 acceptance gates by passing CM-02 object existence, CM-03 replay,
CM-04 logical routing, CM-05 factory amortization, CM-06 shared-error budgeting,
and CM-07 independent accounting baseline. The factory scaffold
collapses 35 baseline synthesis requests to 4 shared-object requests and records
31 amortized saved compiles plus a gross 620 proxy-T pressure delta. The error-budget scaffold allocates a 1e-6 aggregate synthesis-error budget across 4 correlation groups. The independent-baseline scaffold confirms 0 double-counted occurrences and 0 double-counted proxy-T pressure. The cost
model remains unaccepted: the refreshed-B7-ledger gate now attempts CM-08
explicitly and rejects the current shared-theta model. There are still no
30 occurrence-removing certificates, no accepted physical device layout, no
physical factory schedule, no device-calibrated physical validation, and no
`gcm_h6` min-row improvement.
Accepted B7 reduction remains 0.
The local-equivalence invariant obligation gate then returns to the CM-01
structural route: using a magic-basis determinant-normalized trace fingerprint,
24 of 35 `cone_01` windows show nonzero local-equivalence invariant sensitivity
to `RY(theta)` and 24 mismatch the nearest pi/4-grid invariant. Eleven windows
remain invariant-flat. This blocks a local-only absorption interpretation for
24 windows, but it does not reach the 30-window B7 target and is not a KAK
theorem, rewrite certificate, semantic certificate, obstruction theorem, or
resource-saving claim.
The invariant-flat residual gate then turns those 11 flat windows into 3
normalized work packets, all sharing partner q[14]. Even if all 11 were solved,
they would remove at most 11 occurrences / 220 proxy-T units and would still
miss the B7 1.20x target by 19 occurrences / 380 proxy-T units.
The flat-pattern KAK packet then shows all 3 residual work packets share one
numerical nonlocal fingerprint and match nearest pi/4-grid nonlocal
fingerprints, but same-envelope grid replacement still has 0 exact passes with
residual norms 0.2125-0.3644. All 3 packets therefore remain local-dressing or
rewrite-certificate obligations, not resource-saving certificates.
The local-dressing search gate then numerically matches all 3 nearest-grid
representatives to the original flat patterns with arbitrary SU(2)xSU(2)
local dressing, max residual 4.710277376051325e-16. This confirms the
nonlocal-class packet is actionable, but the dressing contains off-pi/4-grid
local Euler parameters, so accepted occurrence removal and accepted proxy-T
reduction both remain 0.
The dressing absorption/exactification gate then projects those 3 numerical
dressings to the pi/4 grid and gets 0/3 exact passes, projected residuals
0.3000-0.8416, 3 distinct grid signatures, 26 off-grid local dressing
parameters, and 0 single-parameter snap exact passes. This closes the cheap
rounding/shared-signature route but does not prove that no other exact dressing
or replayable rewrite exists.
The local Clifford dressing gate then enumerates 24 one-qubit Clifford
representatives, 576 pair-local Clifford representatives, and 331,776
left/right pair-local Clifford dressing candidates per residual packet. It
finds 0/3 exact packets, with best residual norms still in the 0.2125-0.3644
range. This closes the plain local Clifford route but still leaves open
stronger non-Clifford exact local dressing, broader two-qubit rewrite
certificates, or a scoped obstruction theorem. The single-carrier local
dressing gate then checks 143,327,232 candidates and exactifies all 3 flat
packets with residuals 3.20e-16-4.68e-16, but each packet still carries one
arbitrary local carrier, so accepted occurrence removal and accepted proxy-T
reduction remain 0. The single-carrier ledger pressure gate then shows the
ledger sees this as replacement rather than removal: 3 unique carrier
signatures cover 11 flat occurrences, 11 carrier occurrences are inserted for
11 originals, net arbitrary-occurrence delta is 0, optimistic template reuse is
160 proxy-T but unaccepted, and even full carrier absorption would still leave
a 19-occurrence / 380 proxy-T B7 gap.

**Remaining path to a serious solution:** connect to calibrated/live-like
heavy-hex baselines; cover dynamic circuits and reset/measurement semantics;
turn `cone_01` into a broader replayable semantic rewrite certificate,
KAK/Clifford scaffold, or scoped obstruction report that explicitly carries,
shares, or eliminates theta while addressing at least 30 arbitrary rotation
occurrences / 600
proxy-T units, turn the single-carrier exact packets into replayable occurrence-removing
certificates that beat the T-B1-004v replacement ledger, or produce a method beyond direct pi/4 projection or shared grid
signatures for the carrier-bearing packets only as part of a larger
30-occurrence certificate set, or reverse the rejected CM-08 with accepted physical model
evidence after CM-02/CM-07; broaden benchmarks; package certificates for independent
reproduction.

**Current internal maturity:** 59/100.

## B2: Low-Overhead Quantum Error Correction

**Problem ID:** 22

**What we are solving:** reduce the number of physical qubits, measurement
rounds, and decoding resources needed to reach a target logical error rate on
realistic hardware.

**Lineage and unresolved age:** Shor's 1995 quantum error-correcting code,
Steane/CSS codes, Kitaev's topological ideas, and Dennis-Kitaev-Landahl-Preskill
topological quantum memory define the core lineage. Practical low-overhead
fault tolerance remains unresolved after roughly 30 years.

**Why it remains hard:** overhead is dominated by hardware noise, decoder
latency, leakage, correlated errors, measurement schedules, and layout. The best
code on paper may fail under circuit-level noise or hardware constraints.

**Earlier approaches and milestones:** Shor/Steane/CSS codes, surface codes,
color codes, subsystem codes, quantum LDPC codes, biased-noise codes, lattice
surgery, minimum-weight matching, belief propagation, and learned decoders.
Stim and PyMatching made large baseline studies much easier to reproduce.

**Our proposed route:** establish a Wilson-bounded target-volume baseline first,
then require each candidate code, schedule, decoder, or leakage-mitigation
mechanism to beat that baseline on the same metrics. Reduced-round signals are
now explicitly boundary-checked; the active new route is leakage-flagged erasure
information that may lower required distance without reducing syndrome rounds.

**Completed here:** Stim/PyMatching rotated surface-code baseline with 30
configurations, 90,000 shots, distances 3/5/7, X/Z memory bases; Wilson
target-volume table with 40 combinations, 22 met and 18 unmet; biased schedule
proxy raises candidate-met targets to 28 and closes 6 baseline-unmet Wilson
target gaps, but has 0 volume-improvement rows. A real circuit-level sweep with
90 configurations and 270,000 shots raises candidate-met targets to 26 and
closes 4 baseline-unmet Wilson target gaps; all four come from Clifford/CX
hardening, and volume improvement remains 0. A same-hardware reduced-round
candidate then runs 120 configurations / 360,000 shots and finds 22 Wilson
target-volume improved rows with max 3.0x reduction. A robustness stress run
with 240 configurations / 1,200,000 shots preserves 88 improved rows under
higher-shot reseed, 0.60/0.75 noise mismatch, and Clifford-only mechanism
profiles, but all 88 come from aggressive d-4 schedules and 0 come from
non-aggressive d-2 variants. The reduced-round artifact boundary confirms all
original and stress-preserved improved rows are aggressive, distance-3,
one-round candidates, so this lever is closed as a small-distance/aggressive-
schedule artifact boundary rather than a low-overhead QEC claim. T-B2-003 adds
a different non-aggressive leakage-flagged erasure analytic boundary with 42
proxy target-volume improved rows and 33 distance-5/7 rows. T-B2-004 now adds a
Stim HERALDED_ERASE / DEPOLARIZE1 circuit-derived stress: 108 configurations,
216,000 shots, 72 target comparisons, 59 candidate-met rows vs 53 baseline-met
rows, 7 candidate-only target hits, 10 improved target-volume rows, all 10 with
candidate distance 5 or 7, max reduction 4.598x, mean reduction 2.623x,
validation errors 0, no reduced rounds, no d=3 candidates, and no new-code,
threshold, calibrated-device, full physical leakage-decoder, or shot-conditioned
erasure-decoder claim. T-B2-005 adds a heralded-erasure false-positive overhead
stress: 270 configurations, 324,000 shots, 288 target comparisons, 13 improved
rows total, 5 positive-false-positive d=5/d=7 improved rows at fp=0.001/tick,
and 0 improved rows by fp=0.003/tick. It explicitly does not claim
shot-conditioned erasure decoding, calibrated leakage, a threshold, hardware
evidence, or a new code. T-B2-006 now adds a posterior-calibrated
shot-conditioned leakage boundary over the same 288 target comparisons: 4
calibration profiles, 1,152 evaluated profile rows, 3 profiles with surviving
rows, max 4 surviving d=5/d=7 rows in one profile, strict high-purity survival
0, and robust all-profile survival false. It performs calibration modeling but
still does not claim a production decoder, hardware-calibrated leakage model,
threshold, hardware result, or new code.
T-B2-007 adds a posterior-weighted decoder-risk ledger over those profile rows:
4 risk budgets, 4,608 budget/profile rows, 6 raw profile-survivor rows, and
mild/nominal/conservative/strict adjusted survivors of 6/5/3/3. Strict
high-purity adjusted survivors remain 0 and all-profile adjusted survival is
false. This is useful risk accounting, but it is not a circuit-level
shot-conditioned decoder, production decoder, threshold result, hardware result,
or new code. T-B2-008 adds a decoder-input contract feasibility gate: 10
required decoder inputs, 4 available, 6 missing; 9 feasibility gates, 4 passed,
5 failed critical gates; strict high-purity adjusted survivors remain 0; robust
all-profile adjusted survival remains false. T-B2-009a adds a per-shot decoder
trace packet: 3 strict challenge rows, 192 shots per challenge, 576
detector-bitstring traces, observable/prediction rows, and 482 synthetic
detector/tick flag events. T-B2-009b adds a posterior-likelihood injection
gate: 3 injection profiles / 1,728 profile-shots, best profile changes 0
predictions and fixes 0 failures, strong profile introduces 2 failures,
improvement gate is false, and route demotion remains recommended. T-B2-009c
adds a DEM-informed detector-to-edge semantics gate: 3 semantic profiles /
1,728 profile-shots, best conservative profile changes 0 predictions, fixes 0
failures, introduces 0 failures, and leaves 22 injected failures, while the
aggressive DEM profile introduces 1 failure. T-B2-009d adds a hardware-like
leakage observation model gate: 3 observation profiles / 1,728 profile-shots,
864 holdout profile-shots, best conservative hardware-like profile generates
415 model flag events, changes 0 predictions, fixes 0 failures, introduces 0
failures, and has holdout failure delta 0. No circuit-level production decoder,
threshold, hardware, calibrated-device, quantum-advantage, or new-code claim is
made.

**Remaining path to a serious solution:** replace synthetic detector/tick flag
events and hardware-like observation models with real calibrated leakage/flag
observations or independent hardware traces; rerun posterior-likelihood
decoding and require holdout improvement plus all-challenge non-regression;
re-test d=5/d=7 rows under strict high-purity and all-profile robustness gates
before feeding B7.

**Current internal maturity:** 48/100.

## B3: Quantum Algorithms for Molecular Reaction Dynamics

**Problem ID:** 49

**What we are solving:** predict reaction-path observables and dynamics, not
just static small-molecule ground-state energies, with a quantum algorithm whose
resource estimate can be compared with strong classical chemistry baselines.

**Lineage and unresolved age:** Feynman proposed quantum simulation in 1982,
Lloyd formalized universal quantum simulators in 1996, and Aspuru-Guzik et al.
made molecular-energy estimation a quantum-chemistry milestone in 2005.
Practical reaction dynamics with convincing advantage remains unresolved after
about 20 years of algorithmic development.

**Why it remains hard:** electron correlation, active-space selection, nuclear
motion, nonadiabatic effects, real-time dynamics, and observable-level error
budgets all interact. Classical baselines such as DMRG, coupled cluster, and
selected CI are very strong on many instances.

**Earlier approaches and milestones:** phase estimation, Trotterization,
qubitization, VQE, adiabatic state preparation, active-space embedding, and
classical DMRG/FCI/CC baselines. Small molecular simulations exist, but
reaction-dynamics advantage remains unproven.

**Our proposed route:** observable-first reaction simulation. Choose an
experimentally relevant reaction-coordinate observable, then derive the
Hamiltonians, mappings, circuits, and resource estimates needed for that
observable rather than reconstructing the full wavefunction.

**Completed here:** PySCF-backed small-molecule resource proxy for H2, LiH, H2O,
and N2; preliminary observable-first proxy reductions of 6.11x-6.25x. B10-T1
now supplies Hamiltonian-derived B3 reaction-coordinate denominators plus
RHF/MP2/CCSD/FCI small-basis reference derivatives for the same four rows.
T-B3-001 adds four OpenQASM observable-estimation proxy circuits aligned to
those FCI derivative denominators, with max 21 qubits, max 441 controlled-phase
gates, explicit measurement-shot floors, and 0 FCI denominator wins claimed.
T-B3-003 replaces the phase-kickback proxy gap with Qiskit Nature
Jordan-Wigner Hamiltonian Pauli-term measurement packets: 4 QASM packets, max
20 qubits, max 2951 mapped Pauli terms, max conservative total shot floor
30,504,129,929, Hartree-Fock state-preparation costs and Pauli-estimator
variance costs included, and still 0 FCI denominator wins.
T-B3-004 adds sampled Pauli-estimator confidence intervals: 2048 pilot shots
per random Pauli term, z=2.576 intervals all cover exact HF Pauli energy, max
Neyman target shot floor 6,570,468, and 442x-34,544x reduction vs the previous
conservative upper-bound shot floors. That T-B3-004 artifact still had 0 FCI wins and no
selected-CI/larger-active-space denominator.
T-B3-005 adds that stronger denominator pressure test: the same four reaction
coordinates now have selected-CI finite differences in larger orbital bases
(H2/LiH in cc-pVDZ, H2O/N2 in 3-21G), all selected-CI points converge, max
spatial orbitals is 19, max spin-orbital qubits is 38, and max selected
determinant product is 400. The Pauli side now includes QWC grouping and a
two-layer ansatz state-preparation surcharge; packet reduction is 1.0x-4.17x,
but max ansatz two-qubit executions reach 289,100,592 and larger-basis
denominator wins remain 0.
T-B3-006 closes the larger-basis quantum-mapper gap: the same selected-CI
denominator bases are now mapped to Jordan-Wigner qubits, with max 38 qubits,
max 77,858 Pauli terms, max conservative same-basis bucket count 77,116, max
Neyman target shot floor 6,464,114,739, max ansatz two-qubit executions
956,688,981,372, and still 0 larger-basis denominator wins.
T-B3-007 adds actual larger-basis QWC grouping: bitmask first-fit covers reduce
measurement settings 3.09x-3.96x across all four larger-basis Pauli sets, with
LiH dropping from 77,116 conservative buckets to 19,644 QWC groups and max
group size 291. This is a real measurement-setting reduction, but grouped
covariance has not yet reduced the Neyman shot floor, so denominator wins
remain 0.
T-B3-008 propagates exact HF product-state covariance inside those larger-basis
QWC groups. The grouped shot floor falls 4.91x-5.58x versus the independent-term
floor, with the max row moving from 6,464,114,739 shots to 1,283,900,037 shots
and max ansatz two-qubit executions dropping to 190,017,205,476. This is real
measurement-economics progress, but it is still HF covariance rather than a
correlated chemical-state preparation result, and denominator wins remain 0.
T-B3-009 propagates that grouped-covariance energy floor through the three-point
finite-difference derivative. With delta=0.01, the derivative-level shot floor
inflates 10000x, reaching 12,839,000,370,000 shots on the largest row. It also
adds UCCSD, ADAPT-VQE-envelope, and adiabatic-envelope two-qubit preparation
costs; max UCCSD prep is 1,493,030 two-qubit gates and max UCCSD executions reach
18,497,517,970,970,500,000. Sampled correlated-state covariance is still not
available, and denominator wins remain 0.
T-B3-010 adds the first compiled UCC/ADAPT covariance pilot. It builds a
H2/cc-pVDZ one-parameter compiled UCC-double / ADAPT-seed state, samples 48
sampleable QWC groups at 512 shots per group, and obtains mean/max relative
variance error 0.0068/0.0827 against exact group covariance for the sampled
subset. The full exact-cover accounting gives a compiled-state center shot
floor of 66,955,026 versus the HF center floor of 63,465,167, a derivative shot
floor of 669,550,260,000, optimizer-loop total shots of 24,773,359,620,000, and
optimizer-loop two-qubit executions of 7,531,101,324,480,000. This closes the
"no compiled ansatz covariance at all" gap, but it is a one-parameter H2 pilot,
not converged VQE/ADAPT, not sampled covariance for every group or molecule,
and still has 0 denominator wins.
T-B3-011 extends the pressure test across H2, LiH, H2O, and N2 using bounded
high-coefficient sampled QWC subsets: 35 sampled groups total, 384 shots per
group, mean/max relative variance error 0.0833/0.5029. Even under the optimistic
lower-bound accounting that reuses HF grouped-covariance derivative floors, the
max optimizer-loop shot lower bound is 475,043,013,690,000 and the max
optimizer-loop two-qubit lower bound is 281,225,464,104,480,000. The result is
a demotion boundary: the current one-parameter UCC/ADAPT plus QWC route should
not remain a breakthrough candidate without a new state-preparation or
measurement mechanism.

**Remaining path to a serious solution:** keep B3 demoted unless a rescue-only
attempt produces real multi-parameter UCCSD/ADAPT covariance or a
stronger-than-QWC measurement strategy; compare against selected-CI, DMRG, and
tensor-network denominators; promote only if preparation, measurement,
optimizer-loop, and strong classical denominator costs are all beaten at fixed
derivative-level observable error.

**Current internal maturity:** 30/100.

## B4: Verifiable Quantum Advantage Protocols

**Problem ID:** 16

**What we are solving:** design a task that a quantum device can perform, a
classical adversary cannot cheaply spoof, and a verifier can check under
realistic noise without reproducing the full quantum distribution.

**Lineage and unresolved age:** the problem line draws from interactive proofs,
blind quantum computation, sampling advantage, and classical verification.
Representative milestones include universal blind quantum computation and
Mahadev's classical verification protocol. Practical verifiable advantage
remains unresolved after roughly 15-20 years.

**Why it remains hard:** if a task is easy to verify, it may also be easy to
fake. If it is classically hard to simulate, verifying its output can be almost
as hard as solving it. Noise, postselection, and adaptive spoofers narrow the
soundness margin.

**Earlier approaches and milestones:** trap-based verification, blind quantum
computation, cross-entropy benchmarking, random circuit sampling, cryptographic
verification, self-testing, and interactive-proof protocols.

**Our proposed route:** hidden-trap and hidden-invariant hybrid tasks. The
verifier embeds checkable structure inside the task distribution, derives
projection checks from explicit circuits, and then tests adaptive spoofers to
find leakage boundaries.

**Completed here:** toy hidden-trap statistical protocol; four spoofing
families rejected; B8 leakage stress test shows 75% leakage is a dangerous
boundary for trap-aware spoofing; shared B4/B8 CNOT hidden-projection refresh
proxy runs 3 circuit-derived tasks / 192 configs with honest completeness 1.0,
no-refresh high-leakage max soundness 0.675, and repaired high-leakage max
soundness 0.0. T-B4-002a exports a hardware-executable OpenQASM 3 randomized
measurement packet for the same hidden-projection verifier spine: 36 circuit
files, 3 tasks, 3 refresh modes, 4 packet circuits per task-mode, max 30 qubits
including verifier ancillas, and 0 Qiskit/Aer semantic mismatches. It is not
hardware execution, sampling hardness, quantum advantage, or BQP separation.
T-B8-003a then adds a public-QASM packet spoofer boundary: a deterministic
parser/emulator predicts all 36 public packet transcripts, so public-packet
protocol soundness is rejected and private late-binding is required.
T-B8-003b adds the late-bound private challenge contract: all 36 public
skeletons remove verifier-private masks and flips, but the public data
transcripts remain deterministic and classically predictable, so late-bound
parity challenges alone are insufficient. T-B8-003c adds a non-stabilizer
late-bound transcript pilot: all 36 public skeletons receive H plus T/RZ(pi/4)
challenge-basis layers, the deterministic transcript blocker is removed for
36/36 pilot circuits, minimum min-entropy is 4 bits, and maximum output
probability is 0.0625; it remains an exact small-probability pilot, not
hardware execution, cryptographic soundness, sampling hardness, quantum
advantage, or BQP separation. T-B8-003d adds a support-aware spoofer gate: four
public-support spoofer families attack all 36 non-stabilizer pilot circuits;
exact transcript success remains capped at 0.0625, but support-only verifier
acceptance is 1.0, so support-membership soundness is rejected.
T-B8-003e adds a verifier-private predicate pressure gate: four late-bound
private predicate bits reduce support-aware spoofer acceptance from public
support-only 1.0 to hidden-private-predicate acceptance 0.0625, while one-bit
leakage raises acceptance to 0.125 and full predicate leakage restores 1.0.
This is an analytic verifier-burden gate, not hardware execution or protocol
soundness.

**Remaining path to a serious solution:** replace the analytic private
predicate pressure gate with a formal private challenge protocol, real backend
properties, or hardware randomized-measurement execution; attack the resulting
non-public transcript; then prove completeness and soundness under explicit
assumptions.

**Current internal maturity:** 27/100.

## B5: Strongly Correlated Matter via Hybrid Quantum-Tensor Solvers

**Problem ID:** 38

**What we are solving:** make reliable predictions for strongly correlated
models such as Hubbard/t-J systems in regimes where classical methods disagree,
especially two-dimensional, doped, finite-temperature, or dynamical settings.

**Lineage and unresolved age:** Hubbard introduced the electron-correlation
model in 1963. General strongly correlated electron problems, especially doped
two-dimensional regimes, have remained unresolved for roughly 60 years.

**Why it remains hard:** the sign problem, entanglement growth, finite-size
extrapolation, competing phases, and dynamical correlations make broad
classical simulation unreliable. Different classical approximations can
disagree in the scientifically interesting regimes.

**Earlier approaches and milestones:** exact diagonalization, quantum Monte
Carlo, DMRG/tensor networks, DMFT, cluster embedding, variational Monte Carlo,
and cold-atom or quantum simulation platforms.

**Our proposed route:** use quantum processors as entanglement or impurity
kernels inside a classical embedding/tensor workflow, not as monolithic
many-body simulators.

**Completed here:** exact small Hubbard reference and cluster-product proxy;
cluster-4 mean error per site improves 4.63x over cluster-2 in the current
small benchmark. T-B5-001 adds an oracle-tuned classical boundary-field
response embedding denominator on the same 9 B10 D5 Hubbard density-response
rows. T-B5-002 closes the oracle-selection loophole with a non-oracle response
embedding denominator: predeclared zero-field/finitesize-extrapolation policy,
selected mean/max relative response error 0.05098/0.12308, 4 rows beating the
oracle-tuned denominator after-the-fact, max exact D5 Hilbert dimension 4900
versus max selected cluster dimension 36, validation errors 0, and no quantum
response or accuracy-per-resource win claimed. T-B5-003a adds an
exact-state-seeded MPS/Schmidt truncation pressure reference on the same 9
rows: bond dimensions 2/4/8/16, selected bond dimension 16, selected mean/max
relative response error 0.000442/0.001695, selected mean/max energy error per
site 0.000244/0.001156, min exact-state overlap 0.999101, 6 rows beating the
non-oracle embedding denominator, and explicit non-claim of variational DMRG,
deployable tensor solving, quantum response, or accuracy-per-resource win.
T-B5-003b adds a non-exact-state-seeded variational MPS/ALS prototype: bond
dimensions 2/4, 3 restarts x 8 sweeps, selected mean/max relative response
error 0.01806/0.03907, selected mean/max energy error per site
0.00303/0.00853, min exact-state overlap 0.9626, 0 rows beating the seeded
MPS pressure reference, and explicit non-claim of production DMRG or quantum
advantage. T-B5-004 adds a two-site finite-DMRG-style pressure prototype on the
same 9 rows: bond dimension 4, 2 restarts x 4 sweeps, selected mean/max
relative response error 0.08196/0.27710, selected mean/max energy error per
site 0.01619/0.02836, min exact-state overlap 0.93945, 4 rows beating one-site
ALS, 0 rows beating the exact-state-seeded MPS pressure reference, and explicit
non-claim of canonical-environment production DMRG, quantum response, or
accuracy-per-resource win. T-B5-005 adds a canonical DMRG readiness gate over
the current tensor portfolio: 8 readiness gates evaluated, 0 passed and 8
failed; seeded MPS pressure remains the strongest response reference; two-site
and one-site ALS prototypes each have 0 rows beating seeded pressure; prototype
fixed-sector norms fail the 0.01 threshold; and production DMRG, quantum
response win, accuracy-per-resource win, and same-access positive route all
remain false. T-B5-006a adds a canonical-environment smoke gate over the same
two-site prototype outputs: 9 environment ledgers are present, but 0 rows pass
the full smoke gate, 3 rows pass the fixed-sector norm / energy variance /
discarded-weight / monotonicity checks, 0 rows are close to seeded MPS pressure,
0 rows beat seeded MPS pressure, and mature canonical DMRG, production DMRG,
quantum response win, accuracy-per-resource win, and same-access positive route
all remain false.
T-B5-006b adds a B5/B10 same-access production contract gate: it consumes the
canonical DMRG readiness gate, canonical-environment smoke gate, and B10-T1 B5
same-access bridge. The current portfolio passes only 2/10 contract gates,
fails 8/10, has 0 smoke-passed rows, 0 readiness gates, 5 blocking sampling
requirements, no production DMRG, no sampling oracle, no same-access positive
route, and no BQP or quantum-advantage claim.

**Remaining path to a serious solution:** run T-B5-006 by implementing mature
canonical-environment DMRG/MPS for the same response rows, with stored
left/right environments, orthonormal residuals, sweep convergence, no
exact-state seeding, and full cost accounting; or compare a fully costed
quantum impurity/response kernel against exact D5, non-oracle embedding, seeded
MPS pressure, one-site ALS, two-site finite-DMRG-style, readiness-gate, and
smoke-gate denominators while satisfying the same-access production contract.

**Current internal maturity:** 27/100.

## B6: High-Temperature Superconductivity Search

**Problem ID:** 37

**What we are solving:** build a mechanism-aware candidate-ranking pipeline for
unconventional superconductors, using descriptors that are not just historical
family labels or data leakage.

**Lineage and unresolved age:** Bednorz and Muller discovered high-temperature
superconductivity in Ba-La-Cu-O in 1986. Predictive mechanism and candidate
search for high-Tc materials remain unresolved after roughly 40 years.

**Why it remains hard:** the material space is huge, data are biased toward
known families, experimental labels are sparse, descriptor leakage is common,
and strong-correlation mechanisms are difficult to compute.

**Earlier approaches and milestones:** Hubbard/t-J/RVB theories,
spin-fluctuation models, DFT and DFT+DMFT, Eliashberg-style calculations,
materials informatics, and crystal graph neural networks. Major empirical
milestones include cuprates, iron pnictides, nickelates, and hydrides.

**Our proposed route:** mechanism-aware descriptor ranking coupled to B5. The
pipeline must separate family-prior leakage from physics signal and prioritize
experimentally testable candidates.

**Completed here:** toy descriptor-ranking harness with 72 candidates and
precision@12 of 0.833333 on synthetic known-high-Tc labels. T-B6-001 adds a
curated retrospective leakage audit with 26 materials records across 12
families, a post-2008 time split, high-Tc threshold 30 K, all-physics AP@10
0.89 versus random AP@10 mean 0.5346, post-split physics AP 0.9094 versus
family-prior AP 0.9379 and random AP mean 0.9030, family-holdout physics AP
0.9722 versus random AP 0.8529. T-B6-002 adds a formula-derived descriptor
screen with 38 records across 22 families, 12 expanded negative controls,
embedded element-table descriptors, B5-linked correlation/screening proxies,
formula AP@12 0.10, family-prior AP@12 1.0, post-split formula AP 0.5947,
post-split family-prior AP 0.9821, validation errors 0, and explicit non-claim
of material discovery, solved mechanism, complete database coverage, or
computed quantum observable.
T-B6-003 now adds a structural/electronic proxy boundary with the same 38
records / 22 families / 12 expanded negative controls. Structural AP@12 improves
to 0.611 versus formula AP@12 0.10, but family-prior AP@12 remains 1.0;
post-split structural AP is 0.690 versus family-prior 0.982; family-holdout
structural mean AP is 0.896; and the top 12 still include 3 negative controls.
This is a useful leakage boundary, not a material discovery, mechanism solution,
complete database, real DFT calculation, crystallographic database pull, or
computed quantum observable.

**Remaining path to a serious solution:** replace curated/imputed structural
proxies with crystallographic descriptors; attach DFT or B5-computed electronic
observables; expand post-2008 negative controls and parent compounds; beat
family-prior and random baselines without promoting negative controls; produce a
short candidate list only after the technical gate passes.

**Current internal maturity:** 21/100.

## B7: Architecture-Level Fault-Tolerance Co-Design

**Problem ID:** 21

**What we are solving:** optimize algorithms, compilation, error correction,
magic-state factories, layout, and scheduling together so that complete
fault-tolerant computations use less space-time volume.

**Lineage and unresolved age:** the lineage includes Shor's error correction,
threshold theorems, surface-code architectures, lattice surgery, and resource
estimation. Large-scale practical co-designed fault tolerance remains unresolved
after roughly 30 years.

**Why it remains hard:** local savings can disappear at system level. Circuit
depth, logical error targets, factory throughput, feed-forward, routing, and
layout constraints interact nonlinearly.

**Earlier approaches and milestones:** surface-code resource estimation,
lattice-surgery scheduling, magic-state factory design, modular architectures,
and compiler-resource co-design.

**Our proposed route:** bridge B1 and B2 into a workload-level dependency
schedule, then add explicit workload-DAG, factory-throughput, logical
T-resource, FT synthesis, and occurrence-level rewrite-certification pressure
tests. A claimed B1 circuit saving should count only if it improves the B7
space-time-volume ledger after B2 target-volume, synthesis, and factory
assumptions are applied.

**Completed here:** scalar planning model, B1/B2 dependency-schedule bridge,
workload-DAG factory-throughput schedule, logical T-factory boundary tests, FT
synthesis ledger, `gcm_h6` min-row boundary, repeated-template/cache boundary,
nonlocal template scan, `w8_21` claim-boundary closure, template-priority gate,
B1-side target selector, and B1-side cone-feasibility gate. The workload-DAG schedule has mean STV reduction 1.475x. The FT synthesis
ledger exposes `gcm_h6` as the current min row at 1.086008x. The `w8_21` route
was tested across same-skeleton, exhaustive two-CNOT Rz/Ry, target-informed
Euler-local, and bounded three-CNOT families for 43480 optimizer runs, finding
0 exact four-arbitrary-angle replacements and 0 ledger removal. The new
template-priority gate evaluates 12 retained templates: 0 one-angle
single-template routes clear the one-sided `gcm_h6` 1.20x target, and best
`w8_21` needs at least 2 arbitrary removals per occurrence. The B1-side
cone-feasibility gate shows strict direct CNOT-rotation-CNOT sandwiches total
only 4, while `cone_01` has 35 pair-local single-arbitrary windows and is the
only target cone meeting the 30-occurrence threshold under that stricter filter.
The restricted phase-removal gate then tests all 35 `cone_01` windows and finds
0 exact-pass windows for remove-only, fixed-Z, and continuous-RZ same-envelope
replacement. The Euler-reabsorption gate also finds 0 exact-pass windows after
locking RY to exact candidates and reoptimizing neighboring RZ phases. This is
still not an occurrence-removing certificate, resource-saving claim, or global
obstruction theorem.
The parameter-transfer gate adds the sharper accounting constraint: all 35
candidate windows are sensitive to their `RY(theta)` values, none are pi/4-grid
exact, and no-carrier deletion cannot clear the 30-window B7 target.
The theta-sharing ledger gate adds the next guardrail: the 4 theta groups imply
31 duplicate theta occurrences and 620 optimistic cache-reuse proxy-T units, but
the occurrence-based FT ledger still accepts 0 occurrence removal and 0 proxy-T
reduction.
The physical cost-model gate first rejected theta-sharing accounting at 0/8
gates. A follow-up shared-theta synthesis object gate defines 4 object proposals
covering all 35 `cone_01` windows, a replay-verifier gate checks 4/4 objects
and 35/35 occurrences with 0 mismatches, and a logical layout/routing scaffold
assigns anchor/route packets for all occurrences. A factory-amortization
scaffold then accounts for 35 baseline synthesis requests collapsing to 4
shared-object requests. The updated cost-model scaffold now passes CM-02,
CM-03, CM-04, CM-05, CM-06, and CM-07 and is 6/8 passed, 2/8 failed. The
refreshed-B7-ledger gate now attempts CM-08 and rejects the current model. It is still not accepted,
and B7 ledger reduction remains 0.
The local-equivalence invariant obligation gate now blocks local-only
absorption for 24 of the 35 `cone_01` windows using a magic-basis
determinant-normalized trace fingerprint, but 11 windows remain invariant-flat
and the 30-window B7 threshold remains uncleared.
The invariant-flat residual gate now isolates those 11 windows into 3 normalized
work packets and proves that this subset alone can cover only 11/30 required
occurrence removals, leaving 19 occurrences / 380 proxy-T missing.
The flat-pattern KAK packet then shows those 3 packets share one nonlocal
fingerprint and all 3 nearest-grid candidates match that fingerprint, but there
are 0 same-envelope exact passes and 3 local-dressing/rewrite obligations.
B7 accepted ledger reduction remains 0.
The local-dressing search gate then numerically solves those 3 dressing
obligations at max residual 4.710277376051325e-16, but the off-grid local Euler
parameters are not accepted resource savings. Accepted occurrence removal and
accepted proxy-T reduction remain 0.
The dressing absorption/exactification gate then rejects direct rounding:
pi/4 projection gives 0/3 exact passes with projected residuals 0.3000-0.8416,
the three packets have 3 distinct grid signatures, and 26 local dressing
parameters remain off-grid. Accepted occurrence and proxy-T reduction remain 0.
The local Clifford dressing gate then performs a finite local-Clifford closure
check over 24 one-qubit Clifford representatives, 576 pair-local Clifford
representatives, and 331,776 left/right dressing candidates per residual
packet. It finds 0/3 exact packets, so plain local Clifford dressing is not the
missing B7 certificate route. The single-carrier local dressing gate then
exactifies all 3 flat packets after 143,327,232 checked candidates, but leaves
one arbitrary local carrier per packet. Accepted occurrence and proxy-T
reduction remain 0. The single-carrier ledger pressure gate then shows
that the current ledger treats this as replacement rather than removal: 11
inserted carrier occurrences replace 11 original flat occurrences, accepted
reduction remains 0, optimistic template reuse is unaccepted, and even absorbing
all carriers would still leave a 19-occurrence / 380 proxy-T target gap.

**Remaining path to a serious solution:** produce a symbolic KAK/Clifford-
scaffold proof, scoped obstruction, or certified broader `cone_01`
occurrence-removing rewrite for `gcm_h6` with explicit theta-carrier
accounting, turn the single-carrier exact packets into occurrence-removing certificates
or otherwise absorb/share/remove the carrier in the 3 invariant-flat residual KAK
packets only as part of a
larger 30-occurrence certificate set that turns ledger replacement into accepted removal, or reverse the rejected CM-08 with accepted physical model evidence after CM-02/CM-07; strengthen B1 non-Clifford/T-depth
optimization until a certified occurrence-removing rewrite improves minimum
factory STV;
separate claims by data-path versus T-factory dominated regimes; include
physical layout, routing, and feed-forward constraints; run a full algorithm
resource ledger.

**Current internal maturity:** 56/100.

## B8: Classical Verification of Quantum Outputs

**Problem ID:** 30

**What we are solving:** verify task-relevant properties of quantum outputs
without reconstructing the whole output distribution and without letting a
classical spoofer learn the hidden tests.

**Lineage and unresolved age:** the lineage includes interactive proofs,
property testing, blind computation, randomized measurements, and
Mahadev-style verification. Practical low-overhead verification remains
unresolved after roughly 15 years.

**Why it remains hard:** the verifier sees only samples; full distributions are
exponentially large; hidden invariants leak if reused; adaptive spoofers can
learn the verifier's structure.

**Earlier approaches and milestones:** trap/invariant tests, randomized
measurements, classical shadows, cryptographic verification, cross-device
consistency, cross-entropy benchmarking, and property testing.

**Our proposed route:** hidden-invariant tests plus adaptive leakage stress. We
try to break the verifier first, then add challenge refresh, projection
rotation, and B4 circuit-derived hidden projection tasks to repair soundness.

**Completed here:** toy hidden-invariant verifier with honest completeness 1.0
and five adversaries rejected; 48-configuration adaptive leakage test showing
0-0.5 leakage rejected and 0.75 leakage dangerous; toy refresh/rotation repair
passes the <=5% high-leakage soundness gate; shared B4/B8 circuit-refresh proxy
reduces high-leakage adaptive soundness from 0.675 without refresh to 0.0 under
repaired modes; trained/generative spoofer stress runs 144 configs, reaches
learned soundness 1.0 without refresh, and keeps projection_rotation,
challenge_refresh, and refresh_plus_rotation <=5% in this proxy. B10-T2 now
has a proof-obligation gate that rejects no-refresh high-leakage claims and
spells out seven conditions needed before any restricted soundness lemma can be
attempted. The first restricted refresh-independence lemma is now proved under
a bounded-leakage transcript model: if at least one refreshed predicate remains
unknown and independent, the current proxy parameters give a 8.94e-44
single-unknown-mask soundness bound. The transcript leakage simulator now runs
192 configurations and shows refreshed high-leakage modes retain at least 6
unknown independent predicates with max empirical soundness 0.025, while
no-refresh high leakage remains unsafe.
T-B4-002a now adds a B4/B8 OpenQASM 3 randomized-measurement packet with 36
hardware-executable verifier circuits, all using `OPENQASM 3.0`, max 30 qubits
including verifier ancillas, and 0 Qiskit/Aer semantic mismatches. It is a
packet and semantic check, not hardware execution or sampling hardness.
T-B8-003a then adds a public-QASM packet spoofer boundary: a deterministic
parser/emulator predicts all 36 public packet transcripts, public-packet
spoofer acceptance is 1.0, and public-packet protocol soundness is rejected.
T-B8-003b adds a late-bound private challenge contract: public skeletons hide
private masks/flips for all 36 circuits, but deterministic public data
transcripts remain classically predictable; 4/8 gates pass and 4/8 fail.
T-B8-003c adds the non-stabilizer late-bound transcript pilot: 36/36 public
skeletons now include H plus T/RZ(pi/4) challenge-basis layers, the old
deterministic public-data transcript blocker is removed, minimum min-entropy is
4 bits, and maximum output probability is 0.0625; it is still exact
small-probability evidence only, not hardware execution, cryptographic/protocol
soundness, sampling hardness, quantum advantage, or BQP separation.
T-B8-003d adds the support-aware spoofer gate: four public-support spoofer
families attack all 36 non-stabilizer pilot circuits; exact transcript success
remains 0.0625, but support-only verifier acceptance is 1.0, rejecting
support-membership soundness while preserving the exact-transcript blocker.
T-B8-003e adds the verifier-private predicate pressure gate: hidden private
predicate acceptance is 0.0625 instead of public support-only acceptance 1.0;
one-bit leakage raises acceptance to 0.125, and full predicate leakage restores
acceptance to 1.0.
The device-noise transcript bridge now adds 480 configurations across five
noise profiles: bounded bridge profiles preserve honest completeness 1.0, and
challenge_refresh / refresh_plus_rotation stay at max high-leakage soundness
0.0208 with at least 7 unknown independent predicates. Projection rotation is
now margin-sensitive under low-noise calibration, and calibration side-channel
leakage is rejected.
The Qiskit/Aer verifier bridge now instantiates 216 ideal randomized
parity-verifier circuits with ancilla challenge flips, 0 semantic mismatches,
honest completeness 1.0, and up to 30 qubits including verifier ancillas.
The noisy Aer verifier bridge now executes 9600 randomized parity-verifier
circuits for the 12-qubit task with honest and four adversary input families;
bridge-safe modes keep noisy honest acceptance at 1.0 and noisy adversary
acceptance at 0.0 while preserving at least 7 unknown independent predicates.
The backend-calibrated-style verifier bridge now derives per-qubit readout
errors and per-gate depolarizing errors from Qiskit GenericBackendV2 target
InstructionProperties, then executes 5760 randomized parity-verifier circuits
across three calibration snapshots. Bridge-safe modes keep calibrated honest
acceptance at 1.0, calibrated adversary acceptance at 0.25, max honest
predicate-bit error at 0.0703125, and at least 7 unknown independent
predicates; no-refresh remains unsafe.

**Remaining path to a serious solution:** replace the analytic private
predicate model with a formal verifier-private protocol, real backend
properties, or hardware randomized-measurement execution; then attack that
non-public transcript with stronger learned/generative spoofers and explicit
leakage models.

**Current internal maturity:** 39/100.

## B9: Quantum PCP and Local Hamiltonian Hardness

**Problem ID:** 17

**What we are solving:** understand whether the quantum PCP conjecture or
restricted variants hold, or identify formal barriers to gap amplification in
local Hamiltonian problems.

**Lineage and unresolved age:** the problem descends from the classical PCP
theorem, Kitaev's local Hamiltonian QMA-completeness, and the 2000s formulation
of the Quantum PCP conjecture. The core problem has remained unresolved for
roughly 15-25 years.

**Why it remains hard:** entanglement breaks many classical PCP intuitions.
Gap amplification, locality, noncommuting constraints, NLTS, and quantum
locally testable codes are tightly coupled.

**Earlier approaches and milestones:** local Hamiltonian QMA-completeness,
detectability lemma, product tests, gap amplification attempts, NLTS, locally
testable quantum codes, and commuting-Hamiltonian special cases.

**Our proposed route:** do not try to solve the full conjecture first. Build an
exact small-instance laboratory and counterexample database, then formalize
restricted negative lemmas or limited positive theorems.

**Completed here:** exact small-instance gap lab with 18 configurations; nine
locality-preserving candidates; zero candidate passes; four counterexample
candidates. The first finite-instance failed gap-amplification negative lemma
is now extracted from that lab: raw spectral-gap growth is rejected as a local
Hamiltonian amplification certificate unless locality, ground-space overlap,
and normalized-gap improvement are checked together. The lemma records 4 strict
width-trap counterexamples, 9 dense locality traps, and 5 proof obligations,
while explicitly not claiming a Quantum PCP proof or global gap-amplification
impossibility.
T-B9-002 adds a Lean-style symbolic skeleton with 5 definitions, 3 theorem
skeletons, and the same 5 open obligations, but it is not proof-assistant
checked and not a formal theorem.
T-B9-003 instantiates the obstruction on
`cluster_stabilizer_open_uniform_reweight`: for n=4,5,6 all terms have support
2 or 3 and are uniformly scaled by 1.35, max locality remains 3, raw gap
amplifies, normalized gap is invariant, and the certificate is rejected as
global energy rescaling. The available `lean` command failed and this is not a
checked theorem.
T-B9-004a adds a repo-local parametric certificate checker for the same family:
it checks the n >= 4 formula-level term counts, support set {2,3}, max locality
3, exact uniform scale 27/20, finite rows n=4,5,6, and normalized-gap
invariance by exact rational algebra.
T-B9-004b adds a proof-environment readiness gate: only 4/9 gates pass; Lean
exits with failure, Lake is absent, no Lake/mathlib project files exist, the
named-family theorem remains a placeholder `True` obligation, and no
proof-assistant checked theorem exists. The certificate is still rejected as
raw-gap-only rescaling, and it is still not a proof-assistant theorem.

**Remaining path to a serious solution:** pin a real Lean 4/Lake/mathlib or
equivalent proof-checkable project; replace the placeholder `True` theorem with
an indexed Hamiltonian-family theorem; formalize the open-boundary
cluster-stabilizer family for all n >= 4; prove support-size,
uniform-scaling, spectral-width, and normalized-gap invariance lemmas; then
decide whether the checked statement informs the full conjecture.

**Current internal maturity:** 15/100.

## B10: Mapping the Boundary of BQP

**Problem ID:** 11

**What we are solving:** separate robust quantum advantage claims from claims
that depend on unrealistic data loading, oracle construction, precision,
verification gaps, or noise assumptions.

**Lineage and unresolved age:** Bernstein and Vazirani's quantum complexity
theory, Shor's algorithm, hidden-subgroup work, Hamiltonian simulation, quantum
walks, and sampling advantage proposals collectively define this boundary.
The true boundary between BQP and classical computation remains unresolved
after roughly 30 years.

**Why it remains hard:** unconditional complexity separations are extremely
hard. Oracle separations do not automatically imply real-world advantage, and
average-case hardness, input models, precision, and verification assumptions
can erase apparent speedups.

**Earlier approaches and milestones:** oracle separations, hidden subgroup
algorithms, quantum walks, Hamiltonian simulation, boson sampling, random
circuit sampling, dequantization, and fine-grained complexity.

**Our proposed route:** build a reduction and failure-mode graph. Every
advantage claim is decomposed into promise, input model, output certificate,
classical baseline, noise tolerance, and verifier burden.

**Completed here:** taxonomy/reduction graph with 12 nodes, 14 edges, two
connected components, eight advantage-preserving edges, six fragile edges, and
11 restricted theorem targets. Added two formal theorem target cards:
`B10-T1` for the HHL/data-loading negative boundary and `B10-T2` for
sampling-advantage verification under B4/B8 leakage and challenge-refresh
assumptions. Both cards specify input, promise, output, verifier,
cost-accounting, dependencies, and proof obligations, with 0 validation errors.
B10-T1 now has a restricted explicit-I/O accounting lemma and corollary: hidden
loading, block-encoding, state-preparation, readout, or full-vector output costs
rule out end-to-end polylog HHL-style speedup claims in that explicit-I/O model.
B10-T1 also now has a source-backed boundary note with 6 literature anchors, 5
denominator baselines, and 4 claim-boundary checks.
B10-T1 also has a runnable 16-instance CG/LSQR numerical denominator table for
D1/D2 explicit sparse linear-system regimes.
B10-T1 also now has a 9-instance D5 B5 Hubbard density-response observable
denominator table, connecting the boundary work to a concrete strongly
correlated matter observable.
B10-T1/B5 now also has an oracle-tuned boundary-field response embedding
denominator on those same 9 rows: 7 edge-field candidates, mean/max relative
response error 0.0541/0.1216, max exact D5 Hilbert dimension 4900 versus max
embedded cluster dimension 36, validation errors 0, and no quantum response or
accuracy-per-resource win claimed.
B10-T1 also now has a 4-row Hamiltonian-derived D5 B3 reaction-coordinate
observable denominator table tied to PySCF finite-difference Hamiltonian
sources.
B10-T1 also now has a 4-row RHF/MP2/CCSD correlated B3 reference table for the
same reaction-coordinate rows.
B10-T1 also now has a 4-row FCI-strength B3 reference table for those same
small-basis reaction-coordinate rows.
B3 has now connected those B10-T1 references to proxy observable circuits,
Hamiltonian Pauli-term mapper measurement packets, and sampled Pauli-estimator
confidence intervals; the latest B3 sampling artifact reduces the prior
conservative shot floor by 442x-34,544x under an HF-bitstring measurement
model, but still claims 0 FCI wins.
B3 now also has T-B3-005 selected-CI larger-basis grouped Pauli boundary in the
B10-T1 denominator chain: it strengthens the B3/B10 negative boundary with
larger-basis selected-CI finite differences and grouped-measurement/state-prep
costs, but still gives 0 larger-basis denominator wins.
B3 now also has T-B3-006 larger-basis Hamiltonian mapper boundary: the selected-CI
denominator bases are mapped to qubits, but conservative measurement buckets
and generic state-prep surcharge still give 0 larger-basis denominator wins.
B3 now also has T-B3-007 larger-basis QWC grouping boundary: measurement-setting
counts fall 3.09x-3.96x, but covariance and state-prep costs still prevent an
advantage claim.
B3 now also has T-B3-008 grouped covariance shot-floor boundary: HF grouped
covariance lowers independent-term shot floors 4.91x-5.58x, but correlated
state-prep covariance and derivative-level error propagation still prevent an
advantage claim.
B3 now also has T-B3-009 chemical state-prep derivative boundary: derivative
propagation and UCCSD/ADAPT/adiabatic prep envelopes are explicit, but they
inflate the resource ledger and still give 0 denominator wins.
B3 now also has T-B3-010 compiled UCC/ADAPT covariance pilot: H2/cc-pVDZ
one-parameter UCC-double / ADAPT-seed sampling runs on 48 sampleable QWC groups
with mean/max variance error 0.0068/0.0827, but exact derivative and optimizer
loop accounting still give 0 denominator wins and make B3 a pressure-tested
negative boundary rather than an advantage claim.
B3 now also has T-B3-011 cross-molecule UCC/ADAPT pressure and demotion
boundary: H2/LiH/H2O/N2 bounded sampled covariance pressure gives max
optimizer-loop shots lower bound 475,043,013,690,000 and still 0 denominator
wins, so B3 should be treated as negative-boundary evidence in B10-T1 unless a
rescue mechanism appears.
B10-T2 now has a trained-spoofer minimum-refresh boundary from B8: no-refresh
high leakage is unsafe, while projection rotation or stronger refresh is safe
in the current proxy. B10-T2 also now has a proof-obligation gate:
no-refresh/high-leakage soundness claims are rejected in the current proxy;
projection rotation and challenge refresh are only admissible next-proof
conditions; and the current proxy is explicitly insufficient for a general
soundness lemma. A restricted refresh-independence lemma is now proved under a
declared bounded-leakage transcript model; for current proxy parameters the
single-unknown-mask Hoeffding bound is 8.94e-44. B10-T2 also now has a
transcript leakage simulator: 192 configurations, honest completeness 1.0,
no-refresh high leakage unsafe, refreshed high-leakage modes retaining at
least 6 unknown independent predicates, and max refreshed high-leakage
empirical soundness 0.025. This is still transcript-level evidence, not a
hardware verifier or sampling-hardness proof.
B10-T2 also now has a device-noise transcript bridge: bounded noise keeps
challenge_refresh and refresh_plus_rotation below the 5% high-leakage gate
with max empirical soundness 0.0208, while projection_rotation is marked
margin-sensitive and calibration side-channel leakage is rejected.
B10-T2 now also has an ideal Qiskit/Aer circuit-level verifier bridge:
216 randomized parity-verifier circuits, 0 semantic mismatches, and max 30
qubits including verifier ancillas.
B10-T2 now also has a noisy Aer circuit-level verifier bridge: 9600 noisy
randomized parity-verifier circuits, circuit-level adversary inputs generated
by CNOT preimage inversion, bridge-safe noisy honest acceptance 1.0, bridge-safe
noisy adversary acceptance 0.0, max honest predicate-bit error 0.1125, and
calibration-side-channel rejection.
B10-T2 now also has a backend-calibrated-style GenericBackendV2 verifier
bridge: 5760 target-property-derived noisy randomized parity-verifier circuits,
three calibration snapshots, bridge-safe calibrated honest acceptance 1.0,
bridge-safe calibrated adversary acceptance 0.25, max honest predicate-bit
error 0.0703125, no-refresh rejection, and explicit non-claim of real backend
properties or hardware execution.
T-B10-001 now adds a B3/B5 denominator boundary comparison with 4 route cards:
B3 remains demoted with 0 selected-CI larger-basis denominator wins and max
optimizer-loop shots lower bound 475,043,013,690,000; B5 has classical
denominator pressure with 4 non-oracle-over-oracle rows and 6 seeded-MPS rows
beating non-oracle embedding, but 0 variational MPS/ALS rows beat seeded MPS
pressure. The comparison makes no BQP separation or quantum advantage claim.
T-B10-010 now adds a missing-assumption theorem note with 2 theorem skeletons,
5 missing assumptions, and 5 proof obligations; it supports a finite
negative-boundary claim policy but explicitly does not prove a dequantization
theorem, sampling-access theorem, BQP separation, or quantum advantage.
T-B10-011 now adds an asymptotic access-contract note with 2 family contracts
for B3 reaction derivatives and B5 Hubbard response, 8
explicit/oracle/sampling/quantum access-contract rows, 5 bridge conditions,
and 2 theorem targets. It refutes the sampling-access bridge for the current
portfolio evidence because no comparable sampling/query oracle or positive
quantum response kernel is instantiated; it explicitly does not prove a
general dequantization theorem, sampling-access theorem, BQP separation, or
quantum advantage.
T-B10-012 now adds the B5 same-access sampling-or-DMRG bridge: 4 denominator
ladder rows, 5 sampling requirements all blocking, 6
seeded-MPS-over-non-oracle rows, 0 variational-over-seeded rows, no sampling
oracle, no production DMRG, no same-access positive route, and explicit
non-claim of dequantization, sampling theorem, BQP separation, or quantum
advantage.
T-B5-004 now feeds T-B10-013 with a two-site finite-DMRG-style B5 response
pressure prototype. It beats the one-site ALS prototype on 4 rows but still
beats the exact-state-seeded MPS pressure reference on 0 rows, so it strengthens
the same-access blocker instead of creating a positive BQP boundary route.
T-B10-013 now adds an optimistic bounded-density finite-difference response
sampler cost stress on the same 9 B5/B10 Hubbard response rows. To match the
exact-state-seeded MPS pressure target, min/median/max total shots are
3.861e9 / 7.645e12 / 2.849e29; 0 rows beat explicit D5 matvec-equivalent
costs by shots, and the result constructs no sampling oracle, no same-access
positive route, no quantum advantage claim, and no BQP separation claim.
T-B5-005 now adds a canonical DMRG readiness gate into the B10-T1/B5
access-model chain: 0/8 readiness gates pass, seeded MPS pressure remains
strongest, non-seeded tensor references beat seeded pressure on 0 rows, and no
production-DMRG, same-access positive-route, quantum-advantage, or
BQP-separation claim is made.
T-B5-006b now turns the B5/B10 same-access blocker into a production contract:
only 2/10 gates pass, 8/10 fail, and the current state has 0 smoke-passed rows,
0 readiness gates, 5 blocking sampling requirements, no production DMRG, no
sampling oracle, and no same-access positive route.

**Remaining path to a serious solution:** treat B3 as demoted unless a
multi-parameter UCCSD/ADAPT or stronger measurement rescue succeeds; run
T-B10-014 with T-B5-006 by replacing the readiness/cost negative boundary with
canonical-environment production DMRG/MPS for the same B5 Hubbard response rows,
or by supplying a real same-access response oracle with preparation, mixing,
variance, confidence, optimizer-loop, and classical denominator costs strong
enough to survive the full denominator ladder; turn the B10-T2
bridge into real backend-property verifier execution or hardware randomized
measurements; connect B4/B8 verification burdens back into the boundary map.

**Current internal maturity:** 50/100.

## Cross-Portfolio Process

1. Freeze the dossiers monthly and record what changed.
2. Require each lane to produce one falsifiable artifact every 30 days.
3. Promote only directions with measurable deltas and explicit limitations.
4. Merge B4/B8 and B1/B7 when validation stacks overlap.
5. Demote any direction after two failed monthly gates unless it produces a
   useful negative result.
