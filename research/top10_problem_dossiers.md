# Top 10 Problem Dossiers v0.1

Last updated: 2026-06-17

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
cross-checks. The B7 propagation retest gives mean STV 1.034x, while minimum
STV remains 1.0x.

**Remaining path to a serious solution:** connect to calibrated/live-like
heavy-hex baselines; cover dynamic circuits and reset/measurement semantics;
add native-basis-aware non-Clifford/T-depth optimization that improves minimum
B7 factory STV; broaden benchmarks; package certificates for independent
reproduction.

**Current internal maturity:** 37/100.

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
evidence, or a new code.

**Remaining path to a serious solution:** implement a real shot-conditioned
erasure decoder or calibrated leakage model; stress the surviving d=5/d=7 rows
under calibrated flag false-positive rates beyond the observed fp=0.001/tick
survival boundary; measure decoder/runtime overhead at larger distances and
more shots; connect only shot-conditioned or calibrated non-artifact B2 rows
into the B7 resource ledger.

**Current internal maturity:** 41/100.

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
soundness 0.0.

**Remaining path to a serious solution:** upgrade the CNOT/projection proxy to
hardware-executable randomized measurement hidden tasks; test trained
adaptive/generative classical spoofers; prove completeness and soundness under
explicit assumptions; run simulator and small-device trials.

**Current internal maturity:** 20/100.

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
accuracy-per-resource win.

**Remaining path to a serious solution:** replace the MPS/ALS and two-site
finite-DMRG-style prototypes with a mature canonical-environment variational
DMRG/MPS reference; expand to
two-dimensional/doped grids; select observables where classical methods
disagree; generate quantum impurity or response-kernel circuits; prove an
accuracy-per-resource advantage after state-preparation, measurement,
optimizer-loop, and classical-denominator costs are charged.

**Current internal maturity:** 24/100.

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

**Remaining path to a serious solution:** replace qualitative descriptor values
and formula-derived proxies with crystallographic, DFT, or B5-computed
structural/electronic descriptors; expand post-split negative controls; add
structure and correlation descriptors; use B5 observables where available;
produce a short candidate list only after the technical gate passes.

**Current internal maturity:** 19/100.

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
nonlocal template scan, and `w8_21` claim-boundary closure. The workload-DAG
schedule has mean STV reduction 1.475x. The FT synthesis ledger exposes
`gcm_h6` as the current min row at 1.086008x. The `w8_21` route was tested
across same-skeleton, exhaustive two-CNOT Rz/Ry, target-informed Euler-local,
and bounded three-CNOT families for 43480 optimizer runs, finding 0 exact
four-arbitrary-angle replacements and 0 ledger removal.

**Remaining path to a serious solution:** produce a symbolic KAK/Clifford-
scaffold proof or alternate occurrence-removing rewrite for `gcm_h6`; strengthen
B1 non-Clifford/T-depth optimization until minimum factory STV improves;
separate claims by data-path versus T-factory dominated regimes; include
physical layout, routing, and feed-forward constraints; run a full algorithm
resource ledger.

**Current internal maturity:** 33/100.

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

**Remaining path to a serious solution:** replace GenericBackendV2 snapshots
with real backend properties; instantiate hardware randomized-measurement
verifier execution; attack noisy/backend-calibrated circuits with stronger
learned/generative adversaries; output soundness curves under realistic leakage
models.

**Current internal maturity:** 32/100.

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

**Remaining path to a serious solution:** create a real Lean/mathlib or
equivalent proof-checkable project; formalize the open-boundary
cluster-stabilizer family for all n >= 4; prove support-size, uniform-scaling,
spectral-width, and normalized-gap invariance lemmas; then decide whether the
checked statement informs the full conjecture.

**Current internal maturity:** 12/100.

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

**Remaining path to a serious solution:** treat B3 as demoted unless a
multi-parameter UCCSD/ADAPT or stronger measurement rescue succeeds; run
T-B10-014 by replacing the sampler-cost negative boundary with
canonical-environment production DMRG/MPS for the same B5 Hubbard response rows,
or by supplying a real same-access response oracle with preparation, mixing,
variance, and confidence costs strong enough to survive the T-B10-012/T-B10-013
denominator ladder; turn the B10-T2
bridge into real backend-property verifier execution or hardware randomized
measurements; connect B4/B8 verification burdens back into the boundary map.

**Current internal maturity:** 49/100.

## Cross-Portfolio Process

1. Freeze the dossiers monthly and record what changed.
2. Require each lane to produce one falsifiable artifact every 30 days.
3. Promote only directions with measurable deltas and explicit limitations.
4. Merge B4/B8 and B1/B7 when validation stacks overlap.
5. Demote any direction after two failed monthly gates unless it produces a
   useful negative result.
