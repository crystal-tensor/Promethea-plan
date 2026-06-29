# B1-B10 Solution Sprint 001

Last updated: 2026-06-17

Purpose: start the active technical push from B1 to B10. This sprint does not
claim that any of the ten problems is solved. It turns each direction into a
testable work package with a concrete hypothesis, algorithmic move, evidence
standard, and PR-ready task. Publication, patent, financing, and product work
remain downstream until the relevant technical gate is passed.

## Sprint Thesis

The fastest credible path is not ten isolated moonshots. It is four coupled
spines:

| Spine | Tracks | Sprint result we want |
|---|---|---|
| Systems spine | B1, B2, B7 | A compiler/QEC/FT ledger where local savings survive factories and schedules. |
| Verification spine | B4, B8, B10 | A circuit-level hidden task whose verification cost and leakage assumptions are explicit. |
| Application spine | B3, B5, B6, B10 | Observable-first chemistry/materials benchmarks with strong classical denominators. |
| Theory spine | B9, B10 | Negative lemmas and boundary notes that prevent overclaiming. |

## Sprint Rules

1. A work package must be falsifiable in one PR.
2. Every positive claim needs a named baseline and a limitation section.
3. Every result that changes project status needs machine-readable output,
   a human-readable report, and an audit hook.
4. The translation pipeline is unlocked only after a technical gate passes.
5. Failed approaches are kept if they produce a clean negative result.

## B1: Hardware-Aware Circuit Compression

**Technical target:** reduce routed two-qubit work, exposure, and
fault-tolerant T-resource proxies while preserving replayable semantic
certificates.

**Sprint hypothesis:** the current virtual-SWAP and 1Q resynthesis evidence can
be strengthened by adding a native-basis non-Clifford/T-depth pass that reduces
minimum B7 factory-dominated STV, not only mean STV.

**Algorithmic move:** build a proof-logged phase-gadget and Rz-commutation pass
that detects same-wire and post-virtual-SWAP non-Clifford rotation chains,
canonicalizes them under native-basis cost, and emits local certificate events.

**Next PR:** `T-B1-001`. Expected artifacts:

- `tools/b1_native_t_resource_optimizer.py`
- `results/B1_native_t_resource_optimizer_v0.json`
- `research/B1_native_t_resource_optimizer.md`
- optional update to B7 retest inputs

**Acceptance gate:** 30-circuit suite passes measurement-distribution or exact
checks; T-count or T-depth proxy improves on at least one factory-bottlenecked
workload; B7 retest reports whether min STV moves above 1.0x.

**Failure value:** if min STV remains 1.0x, record the bottleneck class and
split B7 claims into data-path and T-factory regimes.

**Sprint 001 update, 2026-06-15:** first native pass is now implemented as
`tools/b1_native_t_resource_optimizer.py`. It canonicalizes
`u3(0, phi, lambda)` into native Z-phase form, emits 1691 proof events across
30 circuits, changes 26 circuits, removes 4 identity 1Q gates, and passes a
30/30 Aer measurement-distribution cross-check with max TVD 0.0. It reduces the
incremental logical T-count proxy by 1.000990x after post-1Q resynthesis. B7
propagation improves mean STV from 1.034436848x to 1.034608523x, but minimum
STV remains 1.0x. This completes `T-B1-001` as a narrow positive diagnostic and
creates `T-B1-002`: target the factory-boundary workloads
`qasmbench_medium_exact/gcm_h6.qasm`, `qasmbench_medium_exact/sat_n11.qasm`,
and `qasmbench_small/hhl_n7.qasm`, where T-count reduction is still 1.0x.

**Sprint 001 update 2, 2026-06-15:** `T-B1-002` now has a positive diagnostic:
`tools/b1_control_rz_commute_optimizer.py` accumulates RZ gates and commutes
them only across CNOTs where the same qubit is the control. It removes 380 RZ
gates, records 1172 CNOT-control commutations, emits 1307 certificate events,
and passes 30/30 Aer measurement-distribution checks with max TVD 0.0. B1
logical T-count proxy improves by 1.119320x over the native pass. B7 propagation
breaks the previous min-STV boundary: min STV is now 1.121951x and mean STV is
1.183921x under the current proxy schedule. This is a serious B1/B7 systems
spine advance, but it remains a diagnostic because arbitrary U3 rotations and
full fault-tolerant synthesis/layout are still outside the pass. New `T-B1-003`
should target remaining arbitrary-rotation factory cost with a general
phase-polynomial or native-U3 synthesis ledger.

**Sprint 001 update 3, 2026-06-15:** `T-B1-003` is now implemented as
`tools/b1_u3_phase_factored_optimizer.py`. The pass factors remaining
`u3(theta, phi, lambda)` gates into the native QASM execution order
`rz(lambda); ry(theta); rz(phi)` up to global phase, then reuses the
control-RZ commute/merge rule. It factors 1641 U3 gates, emits 1641
factorization certificate events plus 3242 RZ-commute certificate events,
removes 313 additional RZ gates, records 540 CNOT-control commutations after
factoring, and passes 30/30 Aer measurement-distribution checks with max TVD
0.0. Incremental B1 logical T-count proxy improves by 1.036371x over the
control-RZ pass, and B7 propagation improves mean STV from 1.183921x to
1.234394x. Minimum STV remains 1.121951x, so the boundary has not moved again;
the next B1/B7 work should either attack the remaining `sat_n11` minimum-STV
regime or replace the proxy with a real FT synthesis/layout/factory ledger.

## B2: Low-Overhead Quantum Error Correction

**Technical target:** beat a surface-code baseline on Wilson-bounded target
volume under identical assumptions.

**Sprint hypothesis:** the previous Clifford/CX hardening signal is real, but
it must be converted from a target-hit improvement into a volume improvement by
using the same hardware footprint and a better schedule/noise mechanism.

**Algorithmic move:** create a schedule family that couples Clifford/CX
hardening with biased correlated noise fields, then selects rows by Wilson 95%
high logical-error bounds and total space-time volume.

**Next PR:** `T-B2-001`. Expected artifacts:

- `tools/b2_same_hardware_schedule_candidate.py`
- `results/B2_same_hardware_schedule_candidate_v0.json`
- `research/B2_same_hardware_schedule_candidate.md`

**Acceptance gate:** at least one Wilson-bounded target-volume reduction
against the surface-code baseline at the same distance, basis, shot budget, and
decoder.

**Failure value:** if target hits improve but volume does not, preserve the
result as evidence that schedule hardening helps reliability but not overhead.

**Sprint update 15:** `T-B2-001` is now implemented as
`tools/b2_same_hardware_schedule_candidate.py`. The tool keeps the same
rotated-surface-code family, distance grid, memory bases, physical-error grid,
shot budget, physical qubits per distance, and PyMatching decoder, then uses
reduced syndrome rounds as the schedule-level volume lever. The official run
tested 120 configurations and 360,000 shots. Against the same Wilson 95%
target-volume table, candidate-met targets increased from 22 to 30, candidate-
only target hits increased to 8, and 22 target rows showed lower space-time
volume. The max and mean reduction on improved rows are both 3.0x because the
best rows use the aggressive `d-4` round-reduced all-operations-hardened
schedule at distance 3. This is the first B2 Wilson target-volume positive
diagnostic, but it is not a new code, threshold, or calibrated-device claim.

**Sprint update 16:** `T-B2-001` now has a robustness boundary report:
`tools/b2_same_hardware_schedule_robustness.py` stress-tests the positive
schedule over four profiles: higher-shot reseed, mild 0.60 noise mismatch,
moderate 0.75 noise mismatch, and Clifford-only physical mechanism. The formal
run used 240 configurations and 1,200,000 shots. It preserves 88 Wilson target-
volume improved rows under stress, but all 88 come from the aggressive `d-4`
variant and 0 come from non-aggressive `d-2` variants. Therefore B2 has a real
schedule-level diagnostic, not a strengthened low-overhead QEC claim.

**Next PR:** `T-B2-002`. Find a non-aggressive or physically motivated
reduced-round schedule/code mechanism that survives larger-distance and
noise-mismatch Wilson target-volume stress, or convert the reduced-round signal
into a small-distance artifact/boundary note before allowing B2 to feed a
stronger B7 ledger.

**Sprint update 31:** `T-B2-002` is now merged as a reduced-round artifact
boundary note, not as a low-overhead QEC win. The new tool
`tools/b2_reduced_round_artifact_boundary.py` consumes
`results/B2_same_hardware_schedule_candidate_v0.json` and
`results/B2_same_hardware_schedule_robustness_v0.json`, then emits
`results/B2_reduced_round_artifact_boundary_v0.json` and
`research/B2_reduced_round_artifact_boundary.md`. It confirms that the 22
original volume-positive rows and the 88 stress-preserved rows are all
aggressive, distance-3, one-round candidates; robust non-aggressive improved
rows remain 0. The reduced-round lever is therefore closed as a
small-distance/aggressive-schedule artifact boundary until a genuinely
different mechanism appears. Next: `T-B2-003` should start a new B2 mechanism:
non-aggressive schedule, different code family, leakage-aware circuit model,
or larger-distance decoder improvement with distance-5/7 Wilson target-volume
reductions under noise mismatch.

**Sprint update 39:** `T-B2-003` is now merged as a leakage-flagged erasure
analytic boundary. `tools/b2_leakage_flagged_erasure_boundary.py` emits
`results/B2_leakage_flagged_erasure_boundary_v0.json` and
`research/B2_leakage_flagged_erasure_boundary.md`. It runs 480 analytic
configurations and finds 42 proxy target-volume improved rows, including 33
candidate distance-5/7 rows, with no reduced rounds and no distance-3
candidates. This is a new non-aggressive direction, but it remains a formula
proxy, not a circuit-level decoder, threshold, calibrated-device, or new-code
claim.

**Sprint update 40:** `T-B2-004` is now merged as a Stim heralded-erasure
stress boundary. `tools/b2_stim_heralded_erasure_stress.py` injects
`DEPOLARIZE1` or `HERALDED_ERASE` after each `TICK` of generated rotated
surface-code memory circuits, then decodes with PyMatching from the detector
error model. The default run covers 108 configurations and 216,000 shots, with
72 target comparisons, 59 candidate-met rows vs 53 baseline-met rows, 7
candidate-only target hits, and 10 improved target-volume rows. All 10 improved
rows are candidate distance 5 or 7; max reduction is 4.598x and mean reduction
is 2.623x after flag overhead. This is stronger than the analytic proxy, but it
is still not a shot-conditioned erasure decoder, calibrated leakage model,
threshold, hardware, or new-code claim.

**Sprint update 41:** `T-B2-005` is now merged as a heralded-erasure
false-positive overhead stress. The official run executes 270 configurations /
324k shots and 288 target comparisons. It preserves 5 d=5/d=7 improved rows at
positive false-positive rate fp=0.001/tick, but all improved rows disappear by
fp=0.003/tick. This is not a shot-conditioned erasure decoder or calibrated
leakage model; it is the current flag-noise survival boundary. Next:
`T-B2-006` should replace this detector-error-model stress with a real
shot-conditioned erasure decoder or calibrated leakage model.

**Sprint update 42:** `T-B2-006` is now merged as a posterior-calibrated
shot-conditioned leakage boundary, not a production decoder. The tool reads the
T-B2-005 false-positive target comparisons and evaluates 4 calibration profiles
over 1,152 profile rows. Three profiles preserve some d=5/d=7 rows, the best
profile preserves 4 rows, strict high-purity survival is 0, and robust
all-profile survival is false. Next: `T-B2-007` should integrate posterior flag
probabilities into a circuit-level decoder or use calibrated leakage/flag data;
otherwise demote the heralded-erasure route.

**Sprint update 43:** `T-B2-007` is now merged as a posterior-weighted
decoder-risk ledger, not a production decoder. The tool reads T-B2-006's 1,152
posterior-calibrated profile rows and evaluates 4 risk budgets over 4,608
budget/profile rows. The source has 6 raw d=5/d=7 profile-survivor rows;
mild/nominal/conservative/strict adjusted survivors are 6/5/3/3. Strict
high-purity adjusted survivors remain 0, and robust all-profile adjusted
survival is false. Next: `T-B2-008` must be a real circuit-level
shot-conditioned decoder or a calibrated leakage/flag dataset; otherwise this
route should stay a boundary track.

**Sprint update 45:** `T-B2-008` is now merged as a decoder-input contract
feasibility gate, not a circuit-level decoder. The new tool
`tools/b2_decoder_input_contract_feasibility_gate.py` maps the T-B2-006/T-B2-007
posterior and risk rows into 10 decoder contract inputs. Only 4 inputs are
available and 6 are missing; 9 feasibility gates are evaluated, 4 pass, and 5
critical gates fail. Strict high-purity adjusted survivors remain 0, robust
all-profile adjusted survival remains false, and the route is explicitly
demoted until a real decoder or calibrated leakage/flag dataset exists. Next:
`T-B2-009a` should first persist per-shot syndrome/flag traces; `T-B2-009b`
must then inject posterior flag likelihoods into a PyMatching/Stim circuit-level
decoder, or collect calibrated leakage/flag data.

**Sprint update 46:** `T-B2-009a` is now merged as a per-shot decoder trace
packet, not a posterior-likelihood decoder. The new tool
`tools/b2_per_shot_decoder_trace_packet.py` selects three strict challenge rows
from the posterior-risk ledger, replays Stim generated rotated surface-code
memory circuits, and persists 576 detector-bitstring traces with observable and
baseline PyMatching prediction rows. It also emits 482 synthetic detector/tick
flag events as an interface fixture. This closes part of the input gap found by
T-B2-008, but it does not claim real calibrated flag events, posterior
likelihood injection, a circuit-level shot-conditioned decoder, a threshold,
hardware evidence, or a new code. Next: `T-B2-009b` must consume these traces in
a posterior-likelihood PyMatching/Stim decoder or replace the synthetic flag
fixture with calibrated leakage/flag data.

**Sprint update 47:** `T-B2-009b` is now merged as a posterior-likelihood
injection interface gate, but it is a negative boundary, not a decoder win. The
new tool `tools/b2_posterior_likelihood_decoder_injection_gate.py` consumes the
T-B2-009a per-shot traces, reconstructs PyMatching edge weights per shot using
synthetic flag posteriors, and evaluates 3 injection profiles over 1,728
profile-shots. The best profile is `mild_flag_weight_shift`: it changes 0
predictions, fixes 0 failures, introduces 0 failures, and leaves 22 injected
failures. The strong profile introduces 2 failures. Therefore the improvement
gate is false, the route remains demoted, and the next useful gate is
`T-B2-009c`: calibrated detector-to-edge posterior semantics or real
leakage/flag data.

**Sprint update 48:** `T-B2-009c` is now merged as a DEM-informed
detector-to-edge semantics gate, and it is also a negative boundary. The new
tool `tools/b2_dem_informed_detector_edge_semantics_gate.py` consumes the
T-B2-009a per-shot traces and allocates synthetic flag posterior mass onto
incident PyMatching/Stim detector-error-model edges by base edge-probability
responsibility. It evaluates 3 semantic profiles over 1,728 profile-shots. The
best conservative profile changes 0 predictions, fixes 0 failures, introduces
0 failures, and leaves 22 injected failures; the aggressive DEM profile
introduces 1 failure. The improvement gate is still false, the route remains
demoted, and the next useful gate is `T-B2-009d`: calibrated leakage/flag
observations or a hardware-like leakage model.

**Sprint update 49:** `T-B2-009d` is now merged as a hardware-like leakage
observation model gate, and it is another negative boundary. The new tool
`tools/b2_hardware_like_leakage_model_gate.py` consumes the T-B2-009a detector
bitstrings without consuming the synthetic flag fixture, generates
deterministic hardware-like leakage observations from challenge-level
leakage/false-positive parameters, and maps those observations onto
Stim/PyMatching DEM edges. It evaluates 3 observation profiles over 1,728
profile-shots, including 864 holdout profile-shots. The best conservative
hardware-like profile generates 415 model flag events, changes 0 predictions,
fixes 0 failures, introduces 0 failures, and leaves 22 injected failures; its
holdout failure delta is also 0. The stress profile generates 727 model flag
events and still fixes 0 failures. The route remains demoted until
`T-B2-009e` supplies real calibrated leakage/flag observations or independent
hardware traces.

## B3: Molecular Reaction Dynamics

**Technical target:** produce a reaction-coordinate quantum observable estimate
that is compared against strong classical chemistry denominators.

**Sprint hypothesis:** the B10 FCI-strength reference rows can become the first
observable-level denominator for a quantum circuit comparison if B3 emits
Hamiltonians along one toy reaction coordinate.

**Algorithmic move:** generate a multi-point PySCF reaction path, map each
Hamiltonian to qubit operators, and compare Trotter/LCU/qubitization-style
observable estimation resources against RHF/MP2/CCSD/FCI denominator rows.

**Next PR:** `T-B3-001`. Expected artifacts:

- `tools/b3_reaction_path_observable_circuit.py`
- `results/B3_reaction_path_observable_circuit_v0.json`
- `research/B3_reaction_path_observable_circuit.md`

**Acceptance gate:** one reaction-coordinate observable has Hamiltonian rows,
classical denominator values, circuit/resource estimates, and propagated
observable error.

**Failure value:** if the quantum resource estimate loses to denominators, the
negative result feeds B10 boundary notes.

## B4: Verifiable Quantum Advantage

**Technical target:** instantiate a circuit-level task that is checkable by the
verifier but hard to spoof cheaply.

**Sprint hypothesis:** B4 should merge its toy trap model with B8's
refresh/rotation repair so the verifier can test adaptive spoofers on circuit
outputs rather than abstract samples.

**Algorithmic move:** generate hidden-trap circuits with embedded invariant
checks, then rotate challenges between batches and measure completeness and
soundness under adaptive spoofers.

**Next PR:** `T-B4-001`. Expected artifacts:

- `tools/b4_b8_hidden_task_generator.py`
- `results/B4_B8_hidden_task_refresh_v0.json`
- `research/B4_B8_hidden_task_refresh.md`

**Acceptance gate:** honest completeness stays high while adaptive spoofer
soundness remains below the configured threshold under at least two refresh
modes.

**Failure value:** if spoofers win, the leakage pattern becomes a B10 verifier
burden condition.

**Sprint update 18:** `T-B4-001` is now merged with `T-B8-001` as a shared
B4/B8 circuit-level proxy task. The new tool
`tools/b4_b8_circuit_refresh_task.py` builds random CNOT hidden-projection
sampling tasks, derives verifier masks from explicit circuits, and attacks the
tasks with four adaptive spoofer families across leakage fractions and refresh
modes. The official run emits `results/B4_B8_circuit_refresh_task_v0.json` and
`research/B4_B8_circuit_refresh_task.md`: 3 tasks, 192 configurations, minimum
honest completeness 1.0, no-refresh high-leakage max soundness 0.675, and best
repaired high-leakage max soundness 0.0. This is not a quantum advantage claim;
it is the first circuit-level B4/B8 verification proxy with a clear leakage
failure and refresh/rotation repair boundary.

**Sprint update 54:** `T-B4-002a` is now merged as an OpenQASM 3
randomized-measurement packet for the B4/B8 hidden-projection verifier spine.
The new tool `tools/b4_b8_openqasm3_randomized_measurement_packet.py` exports
36 `OPENQASM 3.0` verifier circuits across 3 tasks, 3 refresh modes, and 4
packet circuits per task-mode. The largest circuit uses 30 qubits including
verifier ancillas, and the Qiskit/Aer semantic mismatch count is 0. This is a
circuit packet and semantic check only: it is not hardware execution, sampling
hardness, cryptographic soundness, quantum advantage, or BQP separation. Next:
run the packet against real backend properties, hardware randomized-measurement
execution, or stronger trained/generative spoofers.

**Sprint update 55:** `T-B8-003a` is now merged back into B4 as a public-QASM
packet spoofer boundary. The new tool
`tools/b4_b8_openqasm3_packet_public_spoofer_gate.py` parses the 36 exported
OpenQASM 3 packet circuits and deterministically emulates the generated
X/CX/measure subset from public text. The public emulator predicts all 36
packet transcripts, so a public-packet protocol-soundness interpretation is
rejected. This is not an attack on a private protocol, not hardware execution,
not sampling hardness, and not quantum advantage. Next: late-bind private
challenge material or move to real backend/hardware transcripts before making
any verifier-soundness claim.

**Sprint update 56:** `T-B8-003b` is now merged back into B4 as a late-bound
private challenge contract gate. The new tool
`tools/b4_b8_late_bound_private_challenge_contract_gate.py` emits 36 public
skeleton QASM files with verifier-private masks and challenge flips removed.
That separation gate passes, but the skeletons are still deterministic
X/CX/measure circuits, so the public data transcripts remain classically
predictable. The contract passes 4 of 8 gates and fails 4 of 8. Late-bound
parity challenges alone are therefore not protocol soundness; the next gate
needs non-stabilizer structure, real backend properties, hardware execution, or
otherwise non-public/non-predictable transcripts.

**Sprint update 57:** `T-B8-003c` is now merged back into B4 as a
non-stabilizer late-bound transcript pilot. The new tool
`tools/b4_b8_nonstabilizer_late_bound_transcript_pilot.py` emits 36 pilot
`OPENQASM 3.0` circuits under
`results/B4_B8_nonstabilizer_late_bound_transcript_pilot/circuits/` and records
`results/B4_B8_nonstabilizer_late_bound_transcript_pilot_v0.json` plus
`research/B4_B8_nonstabilizer_late_bound_transcript_pilot.md`. Each pilot adds
H plus T/RZ(pi/4) challenge-basis layers to the public skeleton. The old
deterministic transcript blocker is removed for 36/36 circuits, minimum
min-entropy is 4 bits, and maximum output probability is 0.0625. This is an
exact small-probability pilot only: not hardware execution, not cryptographic
or protocol soundness, not sampling hardness, not quantum advantage, and not
BQP separation.

**Sprint update 58:** `T-B8-003d` is now merged back into B4 as a support-aware
spoofer gate. The new tool `tools/b4_b8_nonstabilizer_support_spoofer_gate.py`
reads the non-stabilizer pilot and evaluates four public-support spoofer
families across all 36 circuits. Exact transcript success remains capped at
0.0625, so the single-transcript blocker survives. But support-only verifier
acceptance is 1.0, so public support membership is rejected as protocol
soundness. The next B4 gate must add verifier-private acceptance predicates,
real backend properties, or hardware randomized-measurement execution.

**Sprint update 59:** `T-B8-003e` is now merged back into B4 as a
verifier-private predicate pressure gate. The new tool
`tools/b4_b8_verifier_private_predicate_gate.py` consumes the support-aware
spoofer boundary and adds four late-bound private predicate bits to all 36 pilot
circuits and four spoofer families. Public support-only acceptance was 1.0; the
hidden-private-predicate analytic acceptance is now 0.0625, a 16x guessing
burden. The leakage boundary is explicit: one private bit leaked raises
acceptance to 0.125, and full predicate leakage returns acceptance to 1.0. This
is useful protocol pressure, but it is not hardware execution, cryptographic
soundness, protocol soundness, sampling hardness, quantum advantage, or BQP
separation.

## B5: Strongly Correlated Matter

**Technical target:** show an accuracy-per-resource improvement on a meaningful
strongly correlated observable.

**Sprint hypothesis:** the exact Hubbard denominator can be made more serious
by adding a boundary-field or tensor-network embedding baseline before testing
any quantum response subroutine.

**Algorithmic move:** add a boundary-field embedding baseline for 2D or doped
Hubbard patches and compare recovered cluster-product error fraction against
the current exact small-system denominator.

**Next PR:** `T-B5-001`. Expected artifacts:

- `tools/b5_boundary_embedding_baseline.py`
- `results/B5_boundary_embedding_baseline_v0.json`
- `research/B5_boundary_embedding_baseline.md`

**Acceptance gate:** report exact denominator, embedding baseline, error per
site, observable choice, and where a quantum impurity/kernel would enter.

**Failure value:** if the classical embedding baseline is already strong, use
it as a denominator for B10 rather than overclaiming quantum advantage.

**Sprint update 19:** `T-B5-004` is now merged as a two-site
finite-DMRG-style pressure prototype on the same 9 B5/B10 D5 Hubbard
density-response rows. The official run tests bond dimension 4 with 2 restarts
x 4 sweeps, selected mean/max relative response error 0.08196/0.27710, selected
mean/max energy error per site 0.01619/0.02836, min exact-state overlap
0.93945, 4 rows beating the one-site MPS/ALS prototype, and 0 rows beating the
exact-state-seeded MPS pressure reference. This is not canonical-environment
production DMRG, not a deployable tensor solver, and not a quantum advantage
claim; it is a denominator-pressure artifact for the next B10-T1 gate.

**Sprint update 44:** `T-B5-005` is now merged as a canonical DMRG readiness
gate, not as production DMRG. `tools/b5_canonical_dmrg_readiness_gate.py`
cross-checks the seeded MPS pressure, one-site MPS/ALS, two-site
finite-DMRG-style, and non-oracle embedding references on the same 9 B5/B10 D5
Hubbard response rows. It evaluates 8 readiness gates, passes 0, fails 8,
keeps seeded MPS pressure as the strongest reference, records 0 non-seeded
tensor rows beating seeded pressure, and keeps production DMRG, same-access
positive route, quantum response win, and accuracy-per-resource win all false.
Next: `T-B5-006` must implement actual canonical-environment DMRG/MPS with
stored environments, orthonormal residuals, sweep convergence, no exact-state
seeding, and full cost accounting, or provide a fully costed quantum response
kernel that beats the denominator ladder.

**Sprint update 50:** `T-B5-006a` is now merged as a
canonical-environment smoke gate over the existing two-site prototype outputs,
not as production DMRG. `tools/b5_canonical_environment_smoke_gate.py` checks
the same 9 B5/B10 D5 Hubbard response rows for environment ledger presence,
fixed-sector norm, energy variance, discarded-weight pressure, monotonicity,
and response closeness to the seeded MPS pressure reference. The official run
finds 9 environment ledgers, 0 smoke-passed rows, 3 rows passing the
fixed-sector norm / energy variance / discarded-weight / monotonicity checks,
0 rows close to seeded MPS pressure, and 0 rows beating seeded MPS pressure.
The path remains blocked until `T-B5-006` produces mature canonical-environment
DMRG/MPS with stored environments, orthonormal residuals, convergence, no
exact-state seeding, and full cost accounting, or a fully costed quantum
response kernel beats the denominator ladder.

**Sprint update 53:** `T-B5-006b` is now merged as a B5/B10 same-access
production contract gate. `tools/b5_b10_same_access_production_contract_gate.py`
consumes the canonical DMRG readiness gate, the canonical-environment smoke
gate, and the B10-T1 B5 same-access bridge. The current portfolio passes only
2/10 contract gates: row coverage and no-forbidden-claim discipline. It still
has 0 smoke-passed rows, 0 readiness gates, 5 blocking sampling requirements,
no production DMRG, no sampling oracle, and no same-access positive route. This
does not solve B5 or B10; it turns `T-B5-006` and `T-B10-014` into explicit
acceptance-contract tasks.

## B6: High-Temperature Superconductivity Search

**Technical target:** rank candidate materials using mechanism-aware
descriptors while controlling family-prior leakage.

**Sprint hypothesis:** the curated table, formula-derived proxy screen, and
structural/electronic proxy boundary are useful leakage controls; the next useful
artifact must use real crystallographic, DFT, or B5-computed observables.

**Algorithmic move:** replace formula-derived proxies with computed
structural/electronic descriptors, keep family/time leakage controls, and
charge any B5 observable coupling as a separate evidence channel.

**Current evidence:** `T-B6-003` is now merged as a structural/electronic proxy
boundary. It keeps 38 records / 22 families with 12 expanded negative controls,
improves AP@12 from formula 0.10 to structural 0.611, but still loses to
family-prior AP@12 1.0. Post-split structural AP is 0.690 vs family-prior 0.982,
family-holdout structural mean AP is 0.896, and the top 12 contain 3 negative
controls. It is not a discovery/mechanism/database/DFT/crystallographic-data or
computed-observable claim.

**Next PR:** `T-B6-004`. Expected artifacts:

- `benchmarks/B6_high_temperature_superconductivity.yaml`
- `tools/b6_crystallographic_or_dft_descriptor_audit.py`
- `results/B6_crystallographic_or_dft_descriptor_audit_v0.json`
- `research/B6_crystallographic_or_dft_descriptor_audit.md`

**Acceptance gate:** computed descriptors are reported separately from
family-prior and formula-proxy baselines under random, time-forward, and
family-held-out splits; B5-derived observables must disclose whether they are
real computed observables or only proxies.

**Failure value:** if performance collapses under family-held-out evaluation,
the project avoids false discovery claims and moves toward data-quality work.

## B7: Fault-Tolerance Co-Design

**Technical target:** create an end-to-end resource ledger where compiler and
QEC improvements survive workload DAGs, factories, layout, and feed-forward.

**Sprint hypothesis:** B7 should use B1 as the active lever, but only count
savings that survive factory bottlenecks and minimum-STV tests.

**Algorithmic move:** retest B7 with the new B1 native T-resource pass and
separate data-path-dominated, factory-dominated, and feed-forward-dominated
workloads.

**Next PR:** `T-B7-001`. Expected artifacts:

- `tools/b7_min_stv_regime_classifier.py`
- `results/B7_min_stv_regime_classifier_v0.json`
- `research/B7_min_stv_regime_classifier.md`

**Acceptance gate:** every workload row reports dominant bottleneck, pre/post
STV, min/mean reductions, and whether the improvement is data-path or
T-factory driven.

**Failure value:** if B1 cannot move factory-dominated min STV, B7 becomes a
claim-separation paper rather than a universal reduction claim.

**Sprint update 4:** `T-B7-001` is now merged. The classifier consumes
`logical_t_factory_schedule_u3_phase_factored_v0` and identifies the remaining
minimum-STV row as `qasmbench_medium_exact/sat_n11.qasm` under
`throughput_heavy_factories`: STV reduction 1.121951x, logical T reduction
1.122137x, after-T proxy 5240, and 18/18 schedule rows still factory-path
bottlenecked. U3 phase factoring improves portfolio mean STV, but not this
minimum row.

**Next PR:** `T-B1-004` should remove another 344 logical T proxy from
`sat_n11` to reach 1.20x min STV, or produce a negative boundary for the current
local phase-pass family. `T-B7-002` should replace the fixed rotation T-cost
proxy with an FT synthesis ledger; the 1.25x min-STV target currently requires
544 additional T proxy removal if the same factory footprint is held fixed.

**Sprint update 5:** `T-B7-002` is now merged. The new FT synthesis ledger
classifies exact rotations instead of charging every non-Clifford rotation a
fixed 20-T proxy. Under this ledger, `sat_n11` is re-costed from 294 to 262 T
ledger units and reaches 1.611481x STV reduction under balanced and
throughput-heavy factory variants, moving those rows from factory-path to
data-path bottlenecks. The new minimum row is
`qasmbench_medium_exact/gcm_h6.qasm` under `throughput_heavy_factories` at
1.086008x STV reduction, with portfolio mean STV at 1.253640x.

**Next PR:** `T-B7-003` should attack the new `gcm_h6` FT-ledger boundary or
show that its remaining arbitrary numeric rotations require a stronger
synthesis, routing, or layout assumption before B7 can claim a robust min-STV
win.

**Sprint update 6:** `T-B7-003` is now merged as a quantified boundary result.
The current FT-ledger minimum row is `qasmbench_medium_exact/gcm_h6.qasm` under
`throughput_heavy_factories`, with STV reduction 1.086008x and 270 after-side
arbitrary numeric rotations contributing 5400 / 6224 T ledger units. To push
that current row to 1.20x requires 592 additional T-ledger reduction, equivalent
to about 30 arbitrary rotations at cost 20; 1.25x requires 824 T-ledger
reduction, about 42 such rotations. A portfolio-wide arbitrary-rotation cost
sweep from 20 down to 0 does **not** clear the all-variant 1.20x min-STV
threshold, because other factory/layout variants become the bottleneck.

**Next PR:** `T-B7-004` should add a precision-aware arbitrary-rotation
synthesis/layout ledger for `gcm_h6`, or turn this into a formal negative
boundary for local phase passes under the current factory variants.

**Sprint update 7:** `T-B7-004` is now merged as a precision-aware negative
boundary. The new ledger attaches an explicit uniform synthesis-error budget to
the 270 after-side arbitrary numeric rotations in `gcm_h6`. Under a
Ross-Selinger-style proxy, the most lenient tested total synthesis-error budget
0.1 implies average arbitrary-rotation T cost 35, not below the fixed 20-cost
assumption, and the best tested precision-budget row reaches only 1.079316x
portfolio min STV. The one-sided after-row target would require average
arbitrary-rotation cost <=17 for 1.20x and <=16 for 1.25x, which would require
an impossible >1 total error budget under this proxy. The QASM reuse probe,
however, finds 270 numeric rotation occurrences but only 26 unique numeric
parameters/instructions.

**Next PR:** `T-B7-005` should attack `gcm_h6` structurally: merge or cancel
repeated numeric rotations, test a shared-synthesis/cache proxy for repeated
angles, or prove that the remaining repeated numeric rotations cannot be
reduced by local phase passes.

**Sprint update 8:** `T-B7-005` is now merged as a conservative structural
negative boundary. The pass applies only same-axis numeric rotation
merge/cancel across operations on disjoint qubits, emits 172 certificate
events, and passes a 1/1 Aer measurement-distribution cross-check with TVD
0.0 on `gcm_h6`. It does not remove any arbitrary numeric rotations:
270 -> 270, and the FT T ledger remains 6224 -> 6224. The portfolio min row
therefore stays `gcm_h6` / throughput-heavy factories at 1.086008x STV.

**Next PR:** `T-B7-006` must be nonlocal: either a phase-polynomial or
template-aware compression pass for the `gcm_h6` repeated-angle blocks, or a
proof-quality memo showing that shared synthesis/cache of repeated angles only
saves classical compile effort and cannot reduce the fault-tolerant T ledger.

**Sprint update 9:** `T-B7-006` is now merged as a shared-synthesis/cache
boundary result. The repeated numeric rotations in `gcm_h6` compress from
270 occurrences to 26 unique numeric instruction templates, a 10.384615x
classical catalog reduction. Under the physical occurrence-injection model,
however, every executed arbitrary rotation still consumes an FT rotation
injection, so cache reuse removes 0 T-ledger units and the physical ledger
remains 6760 -> 6224 with portfolio min STV 1.086008x. An intentionally
invalid after-only unique-template accounting would make `gcm_h6` look like it
clears 1.20x, but it still fails the all-variant portfolio gate and is not a
valid physical resource model.

**Next PR:** `T-B7-007` should stop treating repeated-angle cache as a physical
resource reduction and instead attempt a nonlocal repeated-block rewrite:
phase-polynomial, template-aware cancellation, shared magic-state gadget with a
valid execution model, or a sharper no-go certificate for the `gcm_h6` block
family.

**Sprint update 10:** `T-B7-007` is now merged as a nonlocal repeated-block
scan. The scanner emits 2633 role-normalized template certificates over window
widths 8-64. The best exact repeated template, `w8_21`, has width 8, appears
20 non-overlapping times, contains 5 arbitrary rotations per occurrence, and
covers 100 physical arbitrary-rotation occurrences across 14 qubit bindings.
However, the scan finds 0 adjacent inverse block pairs and 0 adjacent duplicate
same-binding block pairs, so it emits no semantics-preserving QASM rewrite:
arbitrary rotations remain 270 -> 270 and T ledger remains 6224 -> 6224. The
target sweep says `gcm_h6` alone reaches 1.20x after removing 30 arbitrary
occurrences / 600 T ledger units, but all-variant 1.20x is still not reached by
changing `gcm_h6` alone because the old `sat_n11` row becomes the minimum at
1.121827x.

**Next PR:** `T-B7-008` should synthesize the best template `w8_21` as an
actual small unitary block. The acceptance gate is strict: either replace each
executed block with fewer than 5 arbitrary rotations and prove equivalence, or
produce a basis-specific minimality/no-go certificate for that template family.

**Sprint update 11:** `T-B7-008` is now merged as a same-skeleton exact
small-block synthesis probe for `w8_21`. The probe tested 55 one-fixed-angle
exact/Clifford candidates, with 16 numerical seeds per candidate, while
re-optimizing the other four angles inside the same two-CNOT skeleton. No
candidate preserved the target 2-qubit unitary within the strict 1e-8
tolerance. The best near miss fixes `a = pi/2`, has residual norm
3.936333737388844e-02 and max entry error 1.8235495914643154e-02. The
finite-difference Jacobian has numerical rank 5, supporting that this
same-skeleton family carries five independent continuous degrees. This closes
the direct one-arbitrary-rotation exact-angle replacement path, but it is not a
global two-qubit lower bound.

**Next PR:** `T-B7-009` should broaden beyond the same two-CNOT skeleton:
KAK/COSINE-style synthesis, alternate CNOT placements, or a sharper
template-family minimality note. A positive result must emit a QASM rewrite for
the 20 non-overlapping `w8_21` occurrences and then rerun proof/Aer/resource
checks.

**Sprint update 12:** `T-B7-009` has now completed a bounded broad-skeleton
exhaustive scan. The new tool scans all length-6 circuits with two CNOTs placed
anywhere, either CNOT direction, and four arbitrary Rz/Ry rotations on either
qubit: 15360 skeleton families, two seeds per family, for 30720 optimizer runs.
It found 0 exact four-arbitrary-rotation candidates; the best candidate
`ry_q1-cx01-rz_q1-cx01-rz_q1-ry_q1` has residual norm 0.24437773599006635 and
max entry error 0.12522813855335146, far above the 1e-8 exact gate. This is a
bounded negative result for this Rz/Ry + two-CNOT + four-rotation family, not a
global lower bound.

**Follow-up completed below:** `T-B7-009` continued with a target-informed
Euler-local family, then with a bounded three-CNOT/four-arbitrary family, and
then with a scoped minimality note that states which searched families were
exhausted.

**Sprint update 13:** `T-B7-009` now has a second, more target-aware negative
boundary. The new tool `tools/b7_w8_21_euler_local_search.py` tests a bounded
Euler-local two-CNOT family with pre/mid/post local `Rz-Ry-Rz` layers on both
qubits. The official run uses target-informed enumeration: it preserves the
source `w8_21` fixed `pi` scaffold, keeps at least 3 of the 5 source arbitrary
angle slots free, allows one remaining free slot to move into nearby Euler-local
structure, and optimizes 500/500 families with 6 seeds each for 3000 optimizer
runs. It found 0 exact four-arbitrary-angle candidates at 1e-8 tolerance. The
best family is
`cx01-cx01|fixed[mid:q1:rz1=pi]|free[pre:q1:ry,mid:q1:rz0,post:q1:rz0,post:q1:ry]`
with residual norm 0.24437773599006604 and max entry error
0.1252281345437596. This strengthens the broad-skeleton negative result by
allowing Euler-local structure around the CNOTs, but it still does not prove a
global KAK lower bound or exclude all Clifford scaffolds, three-CNOT circuits,
ancillas, or measurements.

**Follow-up completed below:** the bounded three-CNOT/four-arbitrary-angle
search has been run, and the scoped minimality note now records why no B7
resource claim can count a `w8_21` rewrite from the tested families.

**Sprint update 14:** the bounded three-CNOT branch of `T-B7-009` is now also
complete. `tools/b7_w8_21_three_cnot_search.py` tests target-informed
pre/mid1/mid2/post local `Rz-Ry-Rz` Euler layers with three CNOTs, four free
arbitrary angles, and the original source `pi` scaffold fixed. The official
run exhausts 1480/1480 families with 6 seeds each, for 8880 optimizer runs.
It found 0 exact candidates at 1e-8 tolerance. The best family is
`cx01-cx10-cx10|fixed[mid1:q1:rz1=pi]|free[mid1:q1:rz0,mid1:q1:ry,post:q0:rz0,post:q1:rz0]`,
with residual norm 1.0352761804100845 and max entry error
0.4895711241454502. Within the tested target-informed family, adding one extra
CNOT does not rescue the attempted 5-to-4 arbitrary-angle compression.

**Next PR:** stop expanding `w8_21` numerical searches unless a new symbolic
KAK/Clifford-scaffold argument is specified. Convert T-B7-008/T-B7-009 into a
scoped minimality note and claim-boundary paper fragment: same-skeleton
one-fixed-angle search, two-CNOT/four-Rz-Ry broad skeleton, two-CNOT
target-informed Euler-local search, and three-CNOT target-informed
Euler-local search all failed to produce a verified four-arbitrary-angle
replacement, so B7 cannot count any `w8_21` resource reduction from these
families.

**Sprint update 17:** `T-B7-009` is now merged as a claim-boundary closure.
The new fragment `research/B7_w8_21_claim_boundary_fragment.md` converts the
four negative search families into a paper-ready boundary statement: repeated
synthesis templates are not physical resource savings unless they come with an
occurrence-removing certificate. Across 43480 optimizer runs, the tested
families found 0 exact four-arbitrary-angle replacements, so `w8_21` removes
0 arbitrary rotations and 0 proxy-T ledger units in B7. This closes the local
numeric `w8_21` expansion path. The next useful work is symbolic
KAK/Clifford-scaffold proof, a certified alternate rewrite for `gcm_h6`, or a
return to `T-B1-004`.

**Sprint update 18:** `T-B7-010a` is now merged as a template-priority gate.
The new artifact `research/B7_template_priority_gate.md` evaluates the 12
retained nonlocal templates against the one-sided `gcm_h6` 1.20x target of 30
removed arbitrary occurrences / 600 proxy-T ledger units. No single template
clears the gate by removing only one arbitrary rotation per occurrence. The
best template remains `w8_21`, but it has only 20 nonoverlap occurrences, so it
needs at least 2 arbitrary removals per occurrence and still has no exact
occurrence-removing certificate after the prior 43480 optimizer runs. This does
not solve B7 and does not claim a physical resource reduction; it tightens
`T-B7-010` so future work must be symbolic, certificate-producing, or return to
B1 T-resource improvement.

**Sprint update 18b:** `T-B1-004a` is now merged as the B1-side target
selector for that same `gcm_h6` bottleneck. The new artifact
`research/B1_B7_gcm_h6_target_selector.md` reads the current B1 U3
phase-factored `gcm_h6` QASM and ranks the arbitrary-rotation families that can
meet the B7 one-sided target if a future semantic rewrite removes one rotation
per occurrence. Current counts are 270 arbitrary decimal rotations, 30 required
removed occurrences, 600 proxy-T ledger units, 3 local CNOT-cone classes meeting
the target, 2 canonical angle classes meeting the target, and 4 qubit classes
meeting the target. This is not a rewrite and not a resource-saving claim; it
turns `T-B1-004` into a sharper instruction: pick one ranked family, prove a
replayable semantic rewrite, then re-run the B7 FT ledger.

**Sprint update 18c:** `T-B1-004b` is now merged as a cone-feasibility gate.
The new artifact `research/B1_B7_gcm_h6_cone_feasibility_gate.md` evaluates the
3 target cone classes from `T-B1-004a`. Together they cover 111 occurrences,
but strict direct CNOT-rotation-CNOT sandwiches total only 4, so there is still
no direct local rewrite claim. The useful result is narrower: `cone_01` has 35
pair-local single-arbitrary windows and is the only cone class that meets the
30-occurrence B7 target under this stricter criterion. This makes the next
`T-B1-004` attempt concrete: synthesize or prove a local two-qubit semantic
rewrite for at least 30 `cone_01` windows, emit replayable certificates, and
only then re-run the B7 FT ledger.

**Sprint update 18d:** `T-B1-004c` is now merged as a restricted
phase-removal gate. The new artifact
`research/B1_B7_cone01_phase_removal_gate.md` tests all 35 `cone_01`
pair-local single-arbitrary windows under a narrow same-envelope hypothesis:
delete the arbitrary `RY`, replace it with a fixed Z phase, or replace it with
an optimized continuous `RZ` while keeping the same two surrounding CNOTs. All
three routes have 0 exact-pass windows at tolerance 1e-8; the best
continuous-RZ residual is 0.36435162331705345. This closes the simple
phase-absorption route, but it is not a global obstruction theorem. `T-B1-004`
now needs broader two-qubit synthesis, KAK/Clifford scaffolding, or another
certificate-bearing transformation.

**Sprint update 18e:** `T-B1-004d` is now merged as a restricted Euler
reabsorption gate. The new artifact
`research/B1_B7_cone01_euler_reabsorption_gate.md` keeps the same two-CNOT
envelope, locks the arbitrary `RY` to 9 exact/Clifford-like candidate angles,
and lets neighboring target-qubit `RZ` phases reoptimize. Across the same 35
`cone_01` windows, the exact-pass count remains 0. The best residual improves
to 0.21253656711362606 and the median residual is 0.3643516233170531, but this
still cannot clear the B7 target. This closes another narrow route and makes
the next useful `T-B1-004` work a genuine two-qubit synthesis/KAK/Clifford
scaffold problem rather than a local Euler absorption trick.

**Sprint update 18f:** `T-B1-004e` is now merged as a parameter-transfer
obligation gate for `cone_01`. The new artifact
`research/B1_B7_cone01_parameter_transfer_gate.md` checks all 35 candidate
windows and finds nonzero projective unitary sensitivity for every original
`RY(theta)` occurrence. None of the 35 angles is near the pi/4 exact grid, and
the windows collapse into 4 distinct theta groups with the largest group
covering 16 occurrences. This does not prove a KAK lower bound and does not
produce a rewrite, but it makes the next `T-B1-004` attempt sharper: any
broader two-qubit synthesis or Clifford/KAK scaffold must explicitly carry,
share, or eliminate theta with certificates before B7 can count a 30-occurrence
or 600 proxy-T ledger reduction.

**Sprint update 18g:** `T-B1-004f` is now merged as a theta-sharing ledger
gate for `cone_01`. The new artifact
`research/B1_B7_cone01_theta_sharing_ledger_gate.md` consumes the
parameter-transfer gate and the B7 template-priority target. The 4 theta groups
create 31 duplicate theta occurrences and an optimistic cache-reuse signal of
620 proxy-T units, which would clear the 600 proxy-T target only under a cache
model. Under the current occurrence-based FT ledger, however, counted
occurrence removal remains 0, counted proxy-T reduction remains 0, and the
ledger target remains uncleared. The next `T-B1-004` attempt must either produce
30 occurrence-removing certificates or justify a new physical theta-sharing cost
model before B7 can count a resource delta.

**Sprint update 18h:** `T-B1-004g` is now merged as a physical cost-model
feasibility gate for `cone_01` theta sharing. The new artifact
`research/B1_B7_cone01_theta_sharing_cost_model_gate.md` keeps the optimistic
620 proxy-T cache signal visible, but checks the eight requirements that would
make theta sharing physically countable. This initial gate passed 0/8 gates:
there was no shared synthesis object, replay verifier, layout/routing model,
factory-amortization ledger, shared-error budget, independent baseline, or
refreshed B7 ledger. The follow-up `T-B1-004h` now supplies the shared object
proposal, `T-B1-004i` adds a line-level replay verifier, and `T-B1-004j` adds a
logical layout/routing scaffold. `T-B1-004k` adds a factory-amortization
scaffold, `T-B1-004l` adds a shared-error budget scaffold, and `T-B1-004m`
adds an independent accounting baseline. `T-B1-004n` now makes the CM-08
refreshed-B7-ledger attempt explicit and rejects the current shared-theta model,
so the scaffold remains 6/8 gates passed. The cost model is still not accepted
and B7 ledger reduction remains 0.

**Sprint update 18i:** `T-B1-004h` is now merged as a shared-theta synthesis object
proposal gate. The new artifact `research/B1_B7_cone01_shared_theta_synthesis_object_gate.md`
defines 4 machine-readable shared objects covering all 35 `cone_01` candidate
windows. This upgrades the cost-model scaffold to 1/8 passed gates by satisfying
CM-02 object existence. The follow-up `T-B1-004i` is now merged as a replay
verifier scaffold: 4/4 shared objects and 35/35 occurrences replay cleanly
against source QASM and parameter-transfer theta groups with 0 mismatches. The
follow-up `T-B1-004j` is now merged as a logical layout/routing scaffold: all 4
objects and all 35 occurrences receive anchor/route packets, with total/max
logical hops 139/11. `T-B1-004k` adds a factory-amortization scaffold that
collapses 35 baseline synthesis requests to 4 shared-object requests. The
follow-up `T-B1-004l` adds a shared-error budget scaffold across the 4 shared
objects. `T-B1-004m` now adds an independent accounting baseline that confirms
zero double-counted occurrences and zero double-counted proxy-T pressure. The
follow-up `T-B1-004n` now attempts CM-08 and rejects the model at the B7 ledger:
accepted proxy-T reduction remains 0 and the `gcm_h6` min row is unchanged. The
updated cost model is 6/8 passed, 2/8 failed; it still has no occurrence-removing
certificates, accepted physical device layout, physical factory schedule, or
device-calibrated physical validation. The cost model remains unaccepted and B7
ledger reduction remains 0.

**Sprint update 18j:** `T-B1-004j` is now merged as a shared-theta logical
layout/routing scaffold. The new artifact
`research/B1_B7_cone01_shared_theta_layout_routing_gate.md` assigns logical
anchor qubits to all 4 replay-verified shared-theta objects and emits 35
occurrence route packets. This satisfies CM-04 as logical route scaffolding only:
it is not a physical device layout, not a factory-amortization model, not a
semantic rewrite certificate, and not a B7 resource claim. The cost-model gate is
now 3/8 passed and 5/8 failed, with counted B7 ledger reduction still 0.

**Sprint update 18k:** `T-B1-004k` is now merged as a shared-theta
factory-amortization scaffold. The new artifact
`research/B1_B7_cone01_shared_theta_factory_amortization_gate.md` consumes the
shared-object, replay, and logical-routing evidence and accounts for 35 baseline
per-occurrence synthesis requests collapsing to 4 shared-object synthesis
requests. It records 31 amortized saved compiles, baseline/shared proxy-T
pressure 700/80, and a gross 620 proxy-T pressure delta. This satisfies CM-05 as
a scaffold only. It is not a physical factory schedule, not a shared-error
budget, not an independent baseline, not a refreshed B7 ledger, and not a
resource claim. The cost-model gate is now 4/8 passed and 4/8 failed, with
counted B7 ledger reduction still 0.

**Sprint update 18l:** `T-B1-004l` is now merged as a shared-theta
error-budget scaffold. The new artifact
`research/B1_B7_cone01_shared_theta_error_budget_gate.md` consumes the
factory-amortized shared-theta objects and allocates a scaffold-level
1e-6 aggregate synthesis-error budget: 2.5e-7 per shared object, 1e-8 per
occurrence, 4 correlation groups, and max correlated occurrence count 16.
This satisfies CM-06 as bookkeeping only. It is not device-calibrated, not
independently validated, not an independent physical baseline, not a refreshed
B7 ledger, and not a resource claim. The cost-model gate is now 5/8 passed and
3/8 failed, with counted B7 ledger reduction still 0.

**Sprint update 18m:** `T-B1-004m` is now merged as a shared-theta independent
accounting-baseline scaffold. The new artifact
`research/B1_B7_cone01_shared_theta_independent_baseline_gate.md` consumes the
error-budgeted and factory-amortized shared-theta objects, compares 35 baseline
per-occurrence synthesis requests against 4 shared-object requests, preserves
the 620 gross proxy-T cache/amortization signal, and confirms 0 double-counted
occurrences plus 0 double-counted proxy-T pressure. This satisfies CM-07 as
accounting evidence only. It is not an independent physical device baseline,
not device-calibrated validation, not a refreshed B7 ledger, and not a resource
claim. The cost-model gate is now 6/8 passed and 2/8 failed, with counted B7
ledger reduction still 0.

**Sprint update 18n:** `T-B1-004n` is now merged as a shared-theta
refreshed-B7-ledger rejection gate. The new artifact
`research/B1_B7_cone01_shared_theta_refreshed_b7_ledger_gate.md` consumes the
current 6/8 cost-model scaffold and the B7 `gcm_h6` FT boundary, then attempts
CM-08 explicitly. It rejects theta sharing as a counted B7 saving because the
cost model is unaccepted, occurrence-ledger proxy-T reduction remains 0, B7
accepted proxy-T reduction after refresh remains 0, and the `gcm_h6` min row is
unchanged. This is useful negative progress: the next route must either produce
30 occurrence-removing certificates or supply a genuinely accepted physical
model before the B7 ledger can count any resource delta.

**Sprint update 18o:** `T-B1-004o` is now merged as a local-equivalence
invariant obligation gate for `cone_01`. The new artifact
`research/B1_B7_cone01_local_invariant_obligation_gate.md` computes a
magic-basis determinant-normalized trace fingerprint for all 35 candidate
windows. It finds 24 windows with nonzero local-equivalence invariant
sensitivity to `RY(theta)` and 24 nearest pi/4-grid invariant mismatches,
leaving 11 invariant-flat windows. This blocks a local-only absorption
interpretation for 24 windows, but it still does not reach the 30-window B7
target and does not produce a KAK theorem, rewrite certificate, semantic
certificate, obstruction theorem, resource saving, or ledger reduction. The
next route must either certify at least 30 occurrence removals, resolve the 11
invariant-flat windows with a stronger invariant/synthesis scaffold, or produce
a genuinely accepted physical cost model.

**Sprint update 18p:** `T-B1-004p` is now merged as the invariant-flat residual
gate for `cone_01`. The new artifact
`research/B1_B7_cone01_invariant_flat_residual_gate.md` consumes the 11
invariant-flat windows from `T-B1-004o`, groups them into 3 normalized pattern
families, and shows that all of them share partner q[14]. The largest flat
theta group has 8 occurrences, but the important ledger result is negative:
even if all 11 flat windows were solved, they would remove at most 11
occurrences / 220 proxy-T units and would still miss the B7 1.20x target by 19
occurrences / 380 proxy-T units. This keeps the flat-window route as a concrete
work packet while preventing it from being counted as a rewrite, KAK theorem,
semantic certificate, resource saving, or B7 ledger improvement.

**Sprint update 18q:** `T-B1-004q` is now merged as the flat-pattern KAK packet
for the same residual route. The new artifact
`research/B1_B7_cone01_flat_pattern_kak_packet.md` converts the 3 residual
pattern groups into compact nonlocal-invariant packets. All 3 pattern groups
share one numerical nonlocal fingerprint and all 3 match their nearest
pi/4-grid nonlocal fingerprint, but same-envelope grid replacement still has
0 exact passes with residuals between 0.21253656711362615 and
0.3643516233170534. The result is useful because it narrows the next proof or
synthesis task to local dressing / rewrite certificates for three normalized
patterns. It is still not a KAK theorem, not a semantic certificate, not a
rewrite, not a resource saving, and not enough for B7 because the packets cover
only 11 of the 30 required occurrences.

**Sprint update 18r:** `T-B1-004r` is now merged as the local-dressing search
gate for those three flat-pattern packets. The new artifact
`research/B1_B7_cone01_local_dressing_search_gate.md` shows that all 3
nearest-grid representatives can be matched back to their original patterns by
arbitrary SU(2)xSU(2) local dressing, with max residual
4.710277376051325e-16. This confirms the q-step nonlocal-class signal is
operationally meaningful. It also preserves the main blocker: the best
dressings contain off-pi/4-grid local Euler parameters, accepted occurrence
removal remains 0, and accepted proxy-T reduction remains 0. The next route must
absorb, share, exactify, or replay-certify those dressing parameters before B7
can count anything.

**Sprint update 18s:** `T-B1-004s` is now merged as the dressing
absorption/exactification negative gate. The new artifact
`research/B1_B7_cone01_dressing_absorption_gate.md` projects the three
T-B1-004r numerical dressings onto the pi/4 grid and gets 0/3 exact passes,
projected residuals from 0.3000426259967881 to 0.8415525963596902, three
distinct grid signatures, 26 off-grid local dressing parameters, and 0
single-parameter snap exact passes. This closes the cheap route where the
continuous local dressing is simply rounded or shared as one exact object. The
remaining route must be a stronger exact local-dressing theorem, a replayable
rewrite certificate, a broader 30-occurrence certificate set, or an accepted
physical cost-model path.

**Sprint update 18t:** `T-B1-004t` is now merged as the local Clifford
dressing finite-search gate. The new artifact
`research/B1_B7_cone01_local_clifford_dressing_gate.md` generates 24
one-qubit Clifford representatives and 576 pair-local Clifford representatives,
then checks all 331,776 left/right pair-local Clifford dressings for each of
the three flat packets. The exact packet count is 0/3 and the best residual
range is 0.2125365671136259 to 0.3643516233170526, so accepted occurrence
removal and accepted proxy-T reduction remain 0. This closes the plain local
Clifford dressing route only; the remaining route must be non-Clifford exact
dressing, a broader two-qubit rewrite certificate, a larger 30-occurrence
certificate set, or an accepted physical cost model.

**Sprint update 18u:** `T-B1-004u` is now merged as the single-carrier local
dressing gate. The new artifact
`research/B1_B7_cone01_single_carrier_dressing_gate.md` checks 143,327,232
finite candidates across one theta/delta-derived carrier rotation, X/Y/Z
axes, partner/target roles, left/right side placement, and pair-local Clifford
wrappers. All three flat packets exactify with residuals from
3.2009291313835888e-16 to 4.677452743560217e-16. This is the first positive
structure packet after the local-Clifford failure, but it still leaves one
arbitrary local carrier rotation per packet, so accepted occurrence removal and
accepted proxy-T reduction remain 0. The next route must convert this
single-carrier structure into replayable occurrence-removing certificates,
extend beyond the 11 flat-window subset by at least 19 more occurrences, or
produce an accepted physical cost-model path.

**Sprint update 18v:** `T-B1-004v` is now merged as the single-carrier ledger
pressure gate. The new artifact
`research/B1_B7_cone01_single_carrier_ledger_gate.md` consumes the exact
packets from T-B1-004u and applies the current B7 occurrence-ledger rule. The
three carrier signatures cover 11 occurrences, but the per-occurrence model
inserts 11 carrier occurrences for 11 original arbitrary occurrences, giving
net arbitrary occurrence delta 0 and accepted proxy-T reduction 0. An
optimistic carrier-template view has only 3 carrier templates and 8 duplicate
carrier occurrences, but that is not accepted as a B7 resource reduction. Even
if all carriers are later absorbed, the route removes at most 11 occurrences
and still misses the 30-occurrence target by 19.

**Sprint update 18w:** `T-B1-004w` is now merged as the single-carrier
shareability gate. The new artifact
`research/B1_B7_cone01_single_carrier_shareability_gate.md` consumes
T-B1-004v and asks whether the exact carrier packets can coalesce into shared
carrier objects. The result is negative: the 11 covered occurrences still split
into 3 distinct carrier signatures, cross-pattern shareable signature count is
0, the largest signature covers only 8 occurrences, and optimistic reuse is
only 160 proxy-T, below the 600 proxy-T B7 target. Even accepting all shared
objects would still remove at most 11 occurrences and miss the B7 target by 19;
accepted occurrence removal and accepted proxy-T reduction remain 0.

**Sprint update 18x:** `T-B1-004x` is now merged as the carrier absorption
inventory gate. The new artifact
`research/B1_B7_cone01_carrier_absorption_inventory_gate.md` consumes
T-B1-004v/w and compares the three carrier signatures against the native
optimized `gcm_h6` rotation inventory. The inventory contains 2049 rotation
arguments. Two of three carrier patterns have angle inventory matches and
same-target matches, but `flat_pattern_02` has no inventory-angle match and
zero patterns have line-local absorption candidates. This means inventory
matches alone cannot turn the carrier route into a resource claim; accepted
absorption certificates, occurrence removal, proxy-T reduction, and B7 ledger
improvement all remain 0.

## B8: Classical Verification of Quantum Outputs

**Technical target:** keep verifier soundness low under adaptive leakage by
using challenge refresh and projection rotation.

**Sprint hypothesis:** the toy repair result should survive when embedded in
B4 circuit-level hidden tasks.

**Algorithmic move:** extend the adaptive leakage spoofer to observe partial
history, infer candidate invariants, and attack refreshed B4/B8 circuit tasks.

**Next PR:** `T-B8-001`. Expected artifacts:

- `tools/b8_circuit_adaptive_spoofer.py`
- `results/B8_circuit_adaptive_spoofer_v0.json`
- `research/B8_circuit_adaptive_spoofer.md`

**Acceptance gate:** soundness curves are reported across leakage fractions,
refresh intervals, projection rotations, and spoofer families.

**Failure value:** if high leakage still wins, formalize a minimum-refresh or
rotation-rate burden for B10-T2 instead of claiming a robust verifier.

**Sprint update 19:** `T-B8-001` is now merged together with `T-B4-001` through
the shared B4/B8 circuit refresh task. The adaptive suite covers
metadata-only, known-projection replay, surrogate projection learner, and
trap-aware leakage spoofers. It reproduces the 0.75 leakage failure when
refresh is absent, then shows projection rotation, challenge refresh, and
refresh-plus-rotation all pass the <=5% high-leakage soundness gate in this
CNOT hidden-projection proxy. Next: replace heuristic projection-enforcement
spoofers with trained/generative attackers and connect the minimum-refresh
condition to B10-T2.

**Sprint update 20:** `T-B8-002` is now merged as a trained/generative
spoofer boundary, not as a soundness proof. The new tool
`tools/b8_generative_spoofer_refresh.py` trains correlation-style projection
generators against the B4/B8 circuit-refresh proxy. The official run emits
`results/B8_generative_spoofer_refresh_v0.json` and
`research/B8_generative_spoofer_refresh.md`: 144 configurations, minimum honest
completeness 1.0, maximum learned soundness 1.0, no-refresh high leakage marked
unsafe, and `projection_rotation`, `challenge_refresh`, and
`refresh_plus_rotation` marked safe under this proxy. This gives B10-T2 a
concrete minimum-refresh proof obligation: no sampling-advantage verification
claim should pass through the B4/B8 layer unless projection rotation or a
stronger refresh condition is explicit.

**Sprint update 21:** `T-B10-002` is now merged as a proof-obligation gate, not
as a soundness lemma. The new tool
`tools/b10_t2_refresh_proof_obligation_gate.py` consumes the B8 trained-spoofer
stress result and the B10 formal target card, then emits
`results/B10_t2_refresh_proof_obligation_gate_v0.json` and
`research/B10_t2_refresh_proof_obligation_gate.md`. The gate rejects
no-refresh high-leakage verification claims in the current proxy because
learned soundness reaches 1.0 at lambda=0.75. It records
`projection_rotation`, `challenge_refresh`, and `refresh_plus_rotation` as
admissible next-proof conditions under the 5% proxy gate, but explicitly marks
the lemma status as `not_proved_proxy_insufficient_for_general_soundness`.
Seven open proof obligations remain: formal protocol timing, leakage-channel
definition, adversary class, soundness bound, hardware randomized-measurement
instantiation, separation from sampling-hardness assumptions, and verifier
overhead accounting.

**Sprint update 22:** `T-B10-003` is now merged on the restricted-lemma path,
not the hardware-verifier path. The new tool
`tools/b10_t2_restricted_soundness_lemma.py` emits
`results/B10_t2_restricted_soundness_lemma_v0.json` and
`research/B10_t2_restricted_soundness_lemma.md`. The lemma states that, in a
bounded-leakage transcript model where challenge refresh or projection rotation
leaves at least one verifier predicate unknown and independent of the
adversary, Hoeffding gives adversarial pass probability at most
`exp(-N(mu-tau)^2/2)` for that predicate. With the current proxy parameters
`N=4096`, `mu=0.30`, and `tau=0.08`, the single-unknown-mask bound is
`8.94e-44`, well below the 5% soundness gate. This is explicitly not a
hardware randomized-measurement verifier, cryptographic soundness theorem,
sampling-hardness proof, or BQP/classical separation; it only discharges the
restricted refresh-independence proof obligation.

**Sprint update 23:** `T-B10-004` is now merged on the transcript-simulator
path, not the hardware-verifier path. The new tool
`tools/b10_t2_transcript_leakage_simulator.py` emits
`results/B10_t2_transcript_leakage_simulator_v0.json` and
`research/B10_t2_transcript_leakage_simulator.md`. It runs 192 configurations
over four refresh modes, four leakage fractions, three CNOT hidden-projection
tasks, and four adversary families. Honest completeness is 1.0. No-refresh
high leakage remains unsafe. In refresh-independent high-leakage modes,
`projection_rotation`, `challenge_refresh`, and `refresh_plus_rotation` retain
at least 6 unknown independent predicates, and the maximum empirical soundness
is 0.025. This supports the restricted lemma's transcript assumptions in this
proxy, but it is still not a hardware randomized-measurement verifier,
sampling-hardness proof, cryptographic soundness theorem, or BQP/classical
separation. Next: `T-B10-005` should instantiate hardware-executable
randomized-measurement circuits or a device-noise transcript bridge and attack
that channel with unrestricted learned/generative adversaries.

**Sprint update 24:** `T-B10-005` is now merged as a device-noise transcript
bridge, not as hardware execution. The new tool
`tools/b10_t2_device_noise_transcript_bridge.py` emits
`results/B10_t2_device_noise_transcript_bridge_v0.json` and
`research/B10_t2_device_noise_transcript_bridge.md`. It runs 480 configurations
across five transcript-level noise profiles. Bounded bridge profiles preserve
honest completeness 1.0, and `challenge_refresh` / `refresh_plus_rotation`
keep high-leakage empirical soundness at most 0.0208 with at least 7 unknown
independent predicates. `projection_rotation` is now marked margin-sensitive:
under `low_noise_bridge` it reaches 0.0625 against the oracle-cover spoofer,
so it should not be counted as device-noise bridge-safe without extra margin.
The `calibration_side_channel` profile is rejected. Next: `T-B10-006` should
instantiate hardware-executable randomized-measurement circuits or a Qiskit/Aer
circuit-level verifier bridge.

**Sprint update 25:** `T-B10-006` is now merged as an ideal Qiskit/Aer
circuit-level verifier bridge, not as hardware execution. The new tool
`tools/b10_t2_qiskit_aer_verifier_bridge.py` emits
`results/B10_t2_qiskit_aer_verifier_bridge_v0.json` and
`research/B10_t2_qiskit_aer_verifier_bridge.md`. It instantiates randomized
parity-verifier circuits with ancilla challenge flips for the three B10-T2
CNOT hidden-projection tasks and runs 216 Aer circuits across
`projection_rotation`, `challenge_refresh`, and `refresh_plus_rotation`. The
ideal Aer semantic mismatch count is 0, minimum honest completeness is 1.0,
and the largest circuit uses 30 qubits including verifier ancillas. The
adversary/noise soundness is inherited from the device-noise transcript bridge:
`challenge_refresh` / `refresh_plus_rotation` remain at 0.0208 high-leakage
max soundness, while `projection_rotation` remains margin-sensitive. Next:
`T-B10-007` should add noisy Aer/backend-calibrated circuit execution or
circuit-level adversary generation.

**Sprint update 26:** `T-B10-007` is now merged as a noisy Qiskit/Aer
circuit-level verifier bridge, still not as calibrated backend or hardware
execution. The new tool `tools/b10_t2_noisy_aer_verifier_bridge.py` emits
`results/B10_t2_noisy_aer_verifier_bridge_v0.json` and
`research/B10_t2_noisy_aer_verifier_bridge.md`. It executes 9600 noisy Aer
randomized parity-verifier circuits for the 12-qubit B10-T2 task, using
honest inputs plus four circuit-level adversary input families constructed by
choosing adversarial output bit strings and inverting the CNOT task map. Under
the bridge-safe `challenge_refresh` / `refresh_plus_rotation` modes, bounded
noise profiles keep noisy honest acceptance at 1.0 and noisy adversary
acceptance at 0.0, with max honest predicate-bit error 0.1125 and at least 7
unknown independent predicates. The `calibration_side_channel` profile remains
rejected. Next: `T-B10-008` should add backend-calibrated noise parameters or
real hardware randomized-measurement verifier execution.

**Sprint update 27:** `T-B10-008` is now merged as a backend-calibrated-style
Aer verifier bridge, still not as real backend properties or hardware
execution. The new tool `tools/b10_t2_backend_calibrated_verifier_bridge.py`
emits `results/B10_t2_backend_calibrated_verifier_bridge_v0.json` and
`research/B10_t2_backend_calibrated_verifier_bridge.md`. It derives
per-qubit readout errors and per-gate depolarizing errors from Qiskit
`GenericBackendV2` target `InstructionProperties`, then executes 5760
randomized parity-verifier circuits across three calibration snapshots. Under
the bridge-safe `challenge_refresh` / `refresh_plus_rotation` modes, calibrated
honest acceptance remains 1.0, calibrated adversary acceptance is 0.25, max
honest predicate-bit error is 0.0703125, and at least 7 unknown independent
predicates remain. The no-refresh mode remains unsafe. Next: `T-B10-009`
should replace GenericBackendV2 snapshots with real backend properties or run
hardware randomized-measurement verifier execution.

**Sprint update 54:** `T-B4-002a` is now merged into B8 as the OpenQASM 3
randomized-measurement packet for the shared B4/B8 verifier spine. The packet
adds `results/B4_B8_openqasm3_randomized_measurement_packet_v0.json`,
`research/B4_B8_openqasm3_randomized_measurement_packet.md`, and 36 exported
`.qasm` circuits under
`results/B4_B8_openqasm3_randomized_measurement_packet/circuits/`. Every
circuit starts with `OPENQASM 3.0`, the maximum size is 30 qubits including
verifier ancillas, and the Aer semantic mismatch count is 0. It is not a
hardware run, cryptographic soundness proof, sampling-hardness proof, quantum
advantage claim, or BQP separation claim. The next B8 gate is to run this
packet with real backend properties or hardware randomized-measurement
execution, and to attack the same packet with stronger spoofers.

**Sprint update 55:** `T-B8-003a` is now merged as the public-QASM packet
spoofer gate. The new result
`results/B4_B8_openqasm3_packet_public_spoofer_gate_v0.json` and report
`research/B4_B8_openqasm3_packet_public_spoofer_gate.md` show that a public
parser/emulator predicts all 36 OpenQASM 3 packet transcripts, with
public-packet spoofer acceptance 1.0. The gate rejects public-packet protocol
soundness and requires late-bound private challenge material, real backend
properties, hardware randomized-measurement execution, or non-public
transcripts before the verifier line can advance.

**Sprint update 56:** `T-B8-003b` is now merged as the late-bound private
challenge contract gate. The result
`results/B4_B8_late_bound_private_challenge_contract_gate_v0.json` and report
`research/B4_B8_late_bound_private_challenge_contract_gate.md` generate 36
public skeleton QASM files under
`results/B4_B8_late_bound_private_challenge_contract/public_skeletons/`.
Those skeletons remove verifier-private masks/flips, but the public data
transcripts are still deterministic and classically predictable. The gate
therefore keeps late-bound private challenge alone marked insufficient for
soundness, with 4 contract gates passed and 4 failed.

**Sprint update 57:** `T-B8-003c` is now merged as the non-stabilizer
late-bound transcript pilot. The result
`results/B4_B8_nonstabilizer_late_bound_transcript_pilot_v0.json`, report
`research/B4_B8_nonstabilizer_late_bound_transcript_pilot.md`, and 36 pilot
QASM files under
`results/B4_B8_nonstabilizer_late_bound_transcript_pilot/circuits/` add H plus
T/RZ(pi/4) challenge-basis layers to the public skeletons. The deterministic
public-data transcript blocker is removed for all 36 pilots, with minimum
min-entropy 4 bits and maximum output probability 0.0625. This advances the
transcript line, but it is still exact small-probability evidence only, not
hardware execution, cryptographic/protocol soundness, sampling hardness,
quantum advantage, or BQP separation.

**Sprint update 58:** `T-B8-003d` is now merged as the support-aware spoofer
gate. The result `results/B4_B8_nonstabilizer_support_spoofer_gate_v0.json` and
report `research/B4_B8_nonstabilizer_support_spoofer_gate.md` show a sharp
boundary: exact transcript success remains 0.0625, but a verifier that only
checks the public support template has support acceptance 1.0 under four
support-aware spoofer families. This keeps the exact-transcript blocker while
rejecting support-membership soundness. The next B8 gate must add a
verifier-private predicate, real backend properties, or hardware execution.

**Sprint update 59:** `T-B8-003e` is now merged as the verifier-private
predicate pressure gate. The result
`results/B4_B8_verifier_private_predicate_gate_v0.json` and report
`research/B4_B8_verifier_private_predicate_gate.md` add four private predicate
bits to the same 36 circuits and four support-aware spoofer families. The
public support-only verifier had acceptance 1.0; the hidden-private-predicate
model lowers acceptance to 0.0625, while one-bit leakage raises it to 0.125 and
full predicate leakage restores 1.0. The next B8 gate must replace this
analytic pressure model with a formal private challenge protocol, real backend
properties, or hardware randomized-measurement execution and then rerun
learned/generative spoofers.

## B9: Quantum PCP / Local Hamiltonian Hardness

**Technical target:** extract a restricted theorem or negative lemma from the
gap-amplification lab.

**Sprint hypothesis:** a failed small-instance amplification pattern can become
a useful negative lemma if the locality, normalization, and gap measurements
are stated precisely.

**Algorithmic move:** choose one counterexample family, write the attempted
amplification rule, identify the violated condition, and package it as a proof
obligation.

**Next PR:** `T-B9-001`. Expected artifacts:

- `research/B9_failed_gap_amplification_lemma.md`
- `results/B9_failed_gap_amplification_lemma_v0.json`
- optional proof-check notes

**Acceptance gate:** the lemma names assumptions, shows the counterexample
family, and states exactly what broader Quantum PCP claim it does not resolve.

**Failure value:** even a failed proof becomes a reusable barrier record.

**Sprint update 28:** `T-B9-001` is now merged as a finite-instance negative
lemma extracted from the B9 exact gap lab. The new tool
`tools/b9_failed_gap_amplification_lemma.py` consumes
`results/B9_local_hamiltonian_gap_lab_v0.json` and emits
`results/B9_failed_gap_amplification_lemma_v0.json` plus
`research/B9_failed_gap_amplification_lemma.md`. The lemma states that raw
spectral-gap growth is not an acceptable local-Hamiltonian gap-amplification
certificate unless locality, ground-space overlap, and normalized-gap
improvement are checked together. The current v0 screen has 0 accepted local
candidate rows, 4 strict width-trap counterexamples, 9 dense locality traps,
and 5 proof obligations. It explicitly does not claim a Quantum PCP proof,
NLTS theorem, local-Hamiltonian hardness theorem, or global gap-amplification
impossibility. Next: `T-B9-002` should turn this finite-instance failed-proof
record into a symbolic family statement or proof-assistant skeleton.

**Sprint update 29:** `T-B9-002` is now merged as a symbolic/proof-assistant
skeleton, still not as a checked formal theorem. The new tool
`tools/b9_symbolic_gap_skeleton.py` consumes
`results/B9_failed_gap_amplification_lemma_v0.json` and emits
`results/B9_symbolic_gap_skeleton_v0.json`,
`research/B9_symbolic_gap_skeleton.md`, and
`research/proof_skeletons/B9_failed_gap_amplification_skeleton.lean`. The
Lean-style skeleton defines `LocalHamiltonianFamily`, `LocalTransform`,
`RawGapAmplifies`, `NormalizedGapAmplifies`, and `AcceptableLocalGapStep`,
then records three theorem skeletons separating raw-gap growth, normalized-gap
failure, and locality failure. It carries forward five open obligations from
the finite-instance lemma, inherits four strict counterexamples and nine dense
locality traps, and explicitly remains unchecked by Lean/mathlib. Next:
`T-B9-003` should instantiate the skeleton on a named Hamiltonian family with
analytic width/locality bounds, then run an actual proof-check pass.

**Sprint update 30:** `T-B9-003` is now merged as a named-family
width/locality bound skeleton, still not as a checked theorem. The new tool
`tools/b9_named_family_width_locality_bounds.py` consumes
`results/B9_local_hamiltonian_gap_lab_v0.json` and emits
`results/B9_named_family_width_locality_bounds_v0.json`,
`research/B9_named_family_width_locality_bounds.md`, and
`research/proof_skeletons/B9_cluster_stabilizer_width_locality_bound.lean`.
The named family is `cluster_stabilizer_open_uniform_reweight`: for n=4,5,6
all generated open-boundary cluster-stabilizer terms have support 2 or 3, so
`local_interaction_reweight_v0` multiplies every term uniformly by 1.35. The
raw spectral gap therefore grows, max locality stays 3, and spectral width
scales by the same factor, leaving normalized gap invariant. The resulting
certificate is rejected as global energy rescaling, not a Quantum PCP proof or
global no-go theorem. A proof-check was attempted, but the current `lean`
command on PATH is not a usable Lean/mathlib theorem prover in this workspace.
Next: `T-B9-004` should create a real proof-checkable environment and
formalize the support-size, uniform-scaling, spectral-width, and
normalized-gap lemmas for all n >= 4.

**Sprint update 49:** `T-B9-004a` is now merged as a local parametric
certificate checker, still not as a proof-assistant theorem. The new tool
`tools/b9_cluster_stabilizer_parametric_certificate.py` consumes
`results/B9_named_family_width_locality_bounds_v0.json` and emits
`results/B9_cluster_stabilizer_parametric_certificate_v0.json` plus
`research/B9_cluster_stabilizer_parametric_certificate.md`. It checks the
open-chain cluster-stabilizer family with exact rational scale `27/20`,
formula-level term counts for all integer n >= 4, support set {2,3}, max
locality 3, and the symbolic identity `(s*g)/(s*w) = g/w` for positive width.
The certificate remains rejected as raw-gap-only global rescaling. This closes
a local verifier gap, but it is not a Lean/mathlib proof, Quantum PCP proof,
NLTS theorem, or global gap-amplification impossibility. Next: keep
`T-B9-004` open for an independently proof-checkable formalization.

**Sprint update 60:** `T-B9-004b` is now merged as a proof-environment
readiness blocker for the same named family. The new tool
`tools/b9_proof_environment_readiness_gate.py` consumes
`results/B9_cluster_stabilizer_parametric_certificate_v0.json` and emits
`results/B9_proof_environment_readiness_gate_v0.json` plus
`research/B9_proof_environment_readiness_gate.md`. It converts the formal
proof gap into nine explicit readiness gates: the local certificate exists and
the exact-rational verifier passes, but only 4/9 gates pass overall. The
current `lean` command exits with failure, `lake` is absent, no Lake/mathlib
project files are present, the named-family theorem is still a placeholder
`True` obligation, and no proof-assistant checked theorem exists. This keeps
`T-B9-004` open with a sharper target: pin Lean 4/Lake/mathlib, make the
skeleton check in that project, replace the placeholder theorem, and formalize
support-size, uniform-scaling, spectral-width, and normalized-gap invariance
for all integer n >= 4.

## B10: Boundary of BQP

**Technical target:** separate robust quantum advantage claims from hidden
input, oracle, loading, verification, precision, or output-cost assumptions.

**Sprint hypothesis:** B10's most valuable near-term contribution is not a
BQP/classical separation. It is an explicit boundary theorem or denominator
comparison for one advantage claim linked to B3/B5/B8.

**Algorithmic move:** use the completed B3/B5 denominator boundary comparison
as a theorem-note scaffold, and in parallel move B10-T2 from GenericBackendV2
calibration-style simulator evidence into real-backend properties or hardware
randomized-measurement verification.

**Current evidence:** `T-B10-001` is merged: 4 B3/B5 route cards, B3
selected-CI larger-basis denominator wins 0, B3 max optimizer-loop shots lower
bound 475,043,013,690,000, B5 non-oracle-over-oracle rows 4,
seeded-MPS-over-non-oracle rows 6, variational MPS/ALS-over-seeded rows 0, and
no BQP separation or quantum advantage claim.
`T-B10-010` is also merged: 2 theorem skeletons, 5 missing assumptions, and 5
proof obligations; it is not a dequantization theorem, sampling-access theorem,
BQP separation, or quantum advantage claim.
`T-B10-011` is now merged: 2 B3/B5 family contracts, 8
explicit/oracle/sampling/quantum access rows, 5 bridge conditions, and a
current-evidence refutation of the sampling-access bridge. It is not a general
dequantization theorem, sampling-access theorem, BQP separation, or quantum
advantage claim.
`T-B10-012` is now merged: 4 B5 denominator ladder rows, 5 sampling
requirements that all block the current bridge, 6 seeded-MPS-over-non-oracle
rows, 0 variational-over-seeded rows, no sampling oracle, no production DMRG,
and no same-access positive route.
`T-B5-004` now feeds `T-B10-013`: the two-site finite-DMRG-style prototype
beats one-site ALS on 4 rows but still beats seeded MPS pressure on 0 rows, so
the same-access bridge remains blocked until production DMRG/MPS or a fully
costed response sampler exists.
`T-B10-013` is now merged as the fully costed response-sampler stress path: an
optimistic bounded-density finite-difference sampler on the same 9 B5/B10
Hubbard response rows needs min/median/max 3.861e9 / 7.645e12 / 2.849e29 shots
to match the exact-state-seeded MPS pressure target, with 0 rows beating
explicit D5 matvec-equivalent costs by shots. It creates no sampling oracle, no
same-access positive route, no quantum advantage claim, and no BQP separation
claim.
`T-B5-005` now feeds `T-B10-014`: the canonical DMRG readiness gate passes 0/8
production-readiness conditions, keeps seeded MPS pressure strongest, records 0
non-seeded rows beating seeded pressure, and preserves the no-production-DMRG,
no-same-access-positive-route, no-quantum-advantage boundary.

**Next PR:** `T-B10-014` or `T-B10-009`. Expected artifacts:

- `research/B10_t1_b5_production_dmrg_response_reference.md` or `research/B10_t1_b5_real_response_oracle_stress.md`
- `results/B10_t1_b5_production_dmrg_response_reference_v0.json` or `results/B10_t1_b5_real_response_oracle_stress_v0.json`
- `research/B4_B8_hardware_randomized_verifier.md` or `research/B10_t2_real_backend_verifier_bridge.md`
- `results/B4_B8_hardware_randomized_verifier_v0.json` or `results/B10_t2_real_backend_verifier_bridge_v0.json`
- optional update to `research/B10_formal_theorem_targets.md`

**Acceptance gate:** a theorem target, proof attempt, counterexample, or
denominator comparison states the input model, output model, verifier burden,
and classical baseline.

**Failure value:** if the target cannot be proven, the failed proof should
still identify which assumption is too strong or too weak.

**Sprint update 18y:** `T-B1-004y` is now merged as a carrier
neighborhood/commutation pressure gate. The new artifact
`research/B1_B7_cone01_carrier_neighborhood_commutation_gate.md` consumes the
carrier absorption inventory boundary from `T-B1-004x` and asks whether
same-target carrier inventory matches are close enough to become credible
absorption search hints. The answer is still negative for accepted B7 progress:
2/3 patterns have same-target inventory matches, but 0/3 have radius-4
candidates, only `flat_pattern_01` has a radius-16/blocker-free candidate,
`flat_pattern_02` has no same-target match, and `flat_pattern_03` is 99 lines
away from its nearest same-target match. Accepted neighborhood absorption
certificates, occurrence removal, proxy-T reduction, commutation claims, and B7
ledger improvement all remain 0. The next `T-B1-004` route must now beat both
the inventory-only boundary and the neighborhood-only boundary with line-local,
commutation-certified, semantic-replay, or broader occurrence-removing evidence.

**Sprint update 18z:** `T-B1-004z` is now merged as a carrier
source-alignment pressure gate. The new artifact
`research/B1_B7_cone01_carrier_source_alignment_gate.md` consumes the
neighborhood boundary from `T-B1-004y` and asks whether nearby carrier candidates
also align with their nearest source lines. The answer remains negative for
accepted B7 progress: 5 radius-16 candidates were reviewed, 1 is blocker-free,
3 are source-qubit-aligned, and 0 are both blocker-free and source-qubit-aligned.
The only blocker-free candidate is line 337 on q[10] near source line 345 on
q[14], so accepted source-alignment certificates, occurrence removal, proxy-T
reduction, commutation claims, and B7 ledger improvement all remain 0. The next
`T-B1-004` route must now beat the inventory-only, neighborhood-only, and
source-alignment-only boundaries with replayable occurrence-removing evidence or
an accepted physical cost model.

**Sprint update 18aa:** `T-B1-004aa` is now merged as a carrier
blocker-stack pressure gate. The new artifact
`research/B1_B7_cone01_carrier_blocker_stack_gate.md` consumes the
source-alignment boundary from `T-B1-004z` and inspects the 3 source-qubit-aligned
radius-16 candidates. All 3 are blocked. Together they have 15 target-touching
CNOT blockers; 14 touch the candidate qubit directly and 1 touches another
target qubit. Accepted simple commutation-clearance certificates, occurrence
removal, proxy-T reduction, and B7 ledger improvement all remain 0. The next
`T-B1-004` route must therefore use a real CNOT-stack rewrite/semantic replay,
not only proximity, source alignment, or a single-qubit commute-through story.

**Sprint update 18ab:** `T-B1-004ab` is now merged as a carrier
blocker-motif pressure gate. The new artifact
`research/B1_B7_cone01_carrier_blocker_motif_gate.md` consumes `T-B1-004aa`
and asks whether the 3 blocked source-aligned candidates share a reusable
CNOT-stack template motif. They do not: the 3 candidates form 3 distinct exact
stack motifs and 2 edge-family motifs; the largest exact motif group has 1
candidate, the largest edge-family group has 2 candidates, and no cross-pattern
motif exists. Accepted template motifs, occurrence removal, proxy-T reduction,
and B7 ledger improvement all remain 0. The next `T-B1-004` route must either
perform a real semantic CNOT-stack rewrite or leave the carrier route as a
negative boundary.

**Sprint update 18ac:** `T-B1-004ac` is now merged as a carrier blocker
CNOT-parity pressure gate. The new artifact
`research/B1_B7_cone01_carrier_blocker_parity_gate.md` consumes the
blocker-stack and blocker-motif gates and asks whether the 3 blocked
source-aligned candidates can be cleared by cheap CNOT parity or adjacent
duplicate-CNOT cancellation. They cannot: 1 candidate has CNOT-only parity
identity only if interleaved gates are ignored, 2 candidates have odd CNOT
parity, repeated same-edge blocker pairs total 11, clean adjacent cancel pairs
are 0, and target-qubit single-qubit interleavings total 18. Accepted parity
clearance, occurrence removal, proxy-T reduction, and B7 ledger improvement
all remain 0. The next `T-B1-004` route must now perform real semantic
CNOT-stack synthesis/replay rather than parity-level clearance.

**Sprint update 18ad:** `T-B1-004ad` is now merged as a carrier interleaving
commutation pressure gate. The new artifact
`research/B1_B7_cone01_carrier_interleaving_commutation_gate.md` consumes the
CNOT-parity gate and classifies the one-qubit gates between repeated blocker
CNOTs. Across 3 candidates it finds 18 interleaving operations on 13 unique
lines: 7 are cheap control-side phase commutations, but 4 are target-side phase
obstructions and 7 are non-diagonal obstructions. All 3 candidates contain
non-diagonal interleavings, so accepted interleaving-commutation clearance,
occurrence removal, proxy-T reduction, and B7 ledger improvement remain 0. The
next `T-B1-004` route must stop relying on cheap CNOT/local-gate clearance and
move into real CNOT-stack semantic synthesis/replay.

**Sprint update 18ae:** `T-B1-004ae` is now merged as a semantic replay packet
construction gate. The new artifact
`research/B1_B7_cone01_semantic_replay_packet_gate.md` consumes the
interleaving-commutation gate and turns the 3 blocked source-aligned carrier
CNOT stacks into exact bounded replay targets. All 3 packets are two-qubit
targets with exact 4x4 matrix fingerprints, covering 32 window gates total: 14
CNOTs and 18 single-qubit gates. The 3 packets have 3 distinct semantic
fingerprints. This is progress because the next synthesis/search step now has
precise local unitary targets. It is not a solution: semantic replay
certificates, shorter rewrites, accepted occurrence removal, proxy-T reduction,
and B7 ledger improvement remain 0.

**Sprint update 18af:** `T-B1-004af` is now merged as a packet synthesis search
gate. The new artifact
`research/B1_B7_cone01_packet_synthesis_search_gate.md` consumes the 3 exact
semantic replay packets and searches fixed-direction 0/1/2/3-CNOT scaffolds
with arbitrary local U3 layers. It finds numerical exact reduced-CNOT
candidates for all 3 packets: candidate line 1378 reaches 1 CNOT from source 4,
and candidate lines 1381 and 268 reach 2 CNOTs from source 5. If these were
later accepted, the candidate CNOT reduction would be 9. They are not accepted
yet: the local U3 layers need resource accounting, the candidates need
full-circuit replay certificates, and B7 occurrence/proxy-T reduction remains
0.

**Sprint update 18ag:** `T-B1-004ag` is now merged as a packet replay/resource
accounting gate. The new artifact
`research/B1_B7_cone01_packet_replay_resource_gate.md` consumes the T-B1-004ae
semantic packets and T-B1-004af reduced-CNOT candidates. The 3 bounded packet
targets remain numerically replay-consistent and preserve the candidate
9-CNOT reduction signal, but the replacements introduce 40 off-pi/4 local-U3
parameters versus 1 source off-pi/4 parameter, adding 780 proxy-T pressure
under the current accounting rule. The route is therefore rejected as a B7
ledger improvement: accepted full-circuit replay certificates, occurrence
removal, proxy-T reduction, and B7 improvement remain 0.

**Sprint update 18ah:** `T-B1-004ah` is now merged as a local-U3
exactification gate. The new artifact
`research/B1_B7_cone01_local_u3_exactification_gate.md` consumes the
T-B1-004af/T-B1-004ag reduced-CNOT packet candidates and tests direct pi/4-grid
snapping of their local-U3 layers. All 40 replacement off-grid parameters can
be projected onto the grid, but replay breaks: exact snapped packet passes are
0/3 and the snapped residual range is 0.4757435265-0.7803612881. Accepted
local-U3 exactification, absorption certificates, full-circuit replay,
occurrence removal, proxy-T reduction, and B7 improvement remain 0. The next
route must use stronger symbolic/local synthesis, context absorption with
replay certificates, or a different occurrence-removing scaffold.

**Sprint update 18ai:** `T-B1-004ai` is now merged as a sparse local-U3 repair
gate. The new artifact
`research/B1_B7_cone01_sparse_local_u3_repair_gate.md` consumes T-B1-004ah,
keeps the pi/4-snapped scaffold, and searches 420 sparse repair candidates
where only one or two local-U3 parameters are freed. One bounded packet, line
1378, admits an exact one-parameter grid-choice repair with residual
9.049428032408627e-13. The other two packets, line 1381 and line 268, remain
unrepaired even with two free parameters. This is partial bounded-packet
evidence only: accepted full-circuit rewrite, occurrence removal, proxy-T
reduction, and B7 improvement remain 0. The next route must broaden the repair
scaffold for the two unresolved packets, convert the line-1378 repair into a
symbolic full-circuit replay certificate, or abandon this reduced-CNOT scaffold.

**Sprint update 18aj:** `T-B1-004aj` is now merged as a three-parameter
local-U3 repair continuation. The new artifact
`research/B1_B7_cone01_three_parameter_local_u3_repair_gate.md` consumes
T-B1-004ai and exhaustively searches exactly-three-parameter repairs for the
two unresolved packets. It checks 1,632 candidates, exactifies line 268 with
residual 6.398929014192638e-13, and leaves line 1381 unresolved with best
residual 0.049865177666770955. The route now has 2/3 bounded packet repairs
and a partial candidate CNOT reduction of 6 if later accepted, but accepted
full-circuit rewrite, occurrence removal, proxy-T reduction, and B7 improvement
remain 0.

**Sprint update 18ak:** `T-B1-004ak` is now merged as a four-parameter
line-1381 repair pressure gate. The new artifact
`research/B1_B7_cone01_four_parameter_line1381_repair_pressure_gate.md`
consumes T-B1-004aj and exhaustively searches 3,060 exactly-four-parameter
repairs for the remaining unresolved reduced-CNOT packet. The best residual
improves from 0.049865177666770955 to 0.02997767950993884, but the gate finds
0 exact repairs. The route remains at 2/3 bounded packet repairs, and accepted
full-circuit rewrite, occurrence removal, proxy-T reduction, and B7 improvement
remain 0. Next work must broaden or change the scaffold, formalize a scoped
obstruction for line 1381, or abandon this reduced-CNOT route.

**Sprint update 18al:** `T-B1-004al` is now merged as a five-parameter
line-1381 exact repair gate. The new artifact
`research/B1_B7_cone01_five_parameter_line1381_exact_repair_gate.md` consumes
T-B1-004ak and finds a first exact packet repair after 5,795 of 8,568
deterministic five-parameter combinations, with residual
6.513934436930801e-13. The reduced-CNOT packet set is now 3/3 repaired at
bounded packet level, with candidate CNOT reduction 9 only if later accepted.
Accepted full-circuit rewrite, symbolic decomposition, occurrence removal,
proxy-T reduction, and B7 improvement all remain 0 because the repairs still
need symbolic full-circuit replay and off-grid local-U3 resource accounting.

Sprint update 18am: T-B1-004am now consumes the line-1378, line-268, and
line-1381 repairs together as a repaired-packet resource-boundary gate. The
route keeps 3/3 bounded packet repairs and the candidate 9-CNOT reduction
signal, but it lowers replacement off-grid local-U3 parameters from 40 to 5
and incremental proxy-T pressure from 780 to 80. This is a narrower blocker,
not a B7 ledger win: accepted full-circuit replay certificates, occurrence
removal, proxy-T reduction, and B7 improvement remain 0. The next sprint gate
must exact-decompose or absorb the five line-1381 off-grid local-U3 parameters
and emit symbolic full-circuit replay certificates before any saving can be
counted.

Sprint update 18an: T-B1-004an now consumes T-B1-004am and turns that next
question into an explicit exact-decomposition pressure gate. The five remaining
line-1381 off-grid local-U3 parameters are tested against pi/4-grid,
low-denominator dyadic-pi, rational-pi denominator <=512, and source-absorption
contracts. All five remain unaccepted: accepted exact decomposition, symbolic
decomposition, full-circuit replay certificate count, occurrence removal,
proxy-T reduction, and B7 improvement are all 0. The cheap
exact-decomposition route is now closed; the next sprint gate must move to
broader symbolic synthesis, context-aware absorption, or full-circuit replay
with honest resource pricing.

Sprint update 18ao: T-B1-004ao now consumes T-B1-004an and checks whether the
same five line-1381 parameters can be absorbed by the native optimized
`gcm_h6` context. The gate reviews 2,049 rotation arguments overall and 44
same-support context rotation arguments in the +/-64-line neighborhood around
the source packet. The result is still negative: 0/5 parameters have exact or
absolute-angle inventory matches, 0/5 have same-support context matches, 0/5
exactly cancel back to the pi/4 grid with one context rotation, and accepted
full-circuit replay, occurrence removal, proxy-T reduction, and B7 improvement
remain 0. The next sprint gate must move to multi-rotation/context-symbolic
absorption, full-circuit replay, or another occurrence-removing scaffold.

Sprint update 18ap: T-B1-004ap now consumes T-B1-004ao and widens the context
absorption pressure to signed sums of two or three same-support context
rotations. The gate reviews the same 44 local context rotation arguments and
evaluates 3,784 width-2 plus 105,952 width-3 signed combinations per parameter,
548,680 signed combination tests in total across the five remaining line-1381
parameters. The result remains negative: 0/5 parameters have exact width-2 or
width-3 absorption back to the pi/4 grid, the best width-3 grid error is
0.0015819911093339911, and accepted full-circuit replay, occurrence removal,
proxy-T reduction, and B7 improvement remain 0. The next sprint gate must move
to four-or-more-rotation symbolic absorption, commutation-aware full-circuit
replay, or another occurrence-removing scaffold.

Sprint update 18aq: T-B1-004aq now consumes T-B1-004ap and tests the next
bounded context rung: signed sums of exactly four same-support context
rotations. The gate reviews the same 44 local context rotation arguments and
evaluates 2,172,016 width-4 signed combinations per parameter, 10,860,080
signed combination tests in total across the five remaining line-1381
parameters. The result remains negative: 0/5 parameters have exact width-4
absorption back to the pi/4 grid, the best width-4 grid error remains
0.0015819911093339911, and accepted full-circuit replay, occurrence removal,
proxy-T reduction, and B7 improvement remain 0. The next sprint gate should
favor commutation-aware full-circuit replay or another occurrence-removing
scaffold unless a five-or-more-rotation symbolic search has a stronger
structural reason than local bounded enumeration.

## Sprint Promotion Matrix

| Track | Can become paper after this sprint? | Can become patent after this sprint? | Can become fundable/tool after this sprint? |
|---|---|---|---|
| B1 | Only if B7 min-STV improves or claim is cleanly split. | Possible invention disclosure if certificate pass is novel after prior-art search. | QCert CLI packaging can begin only as research tooling. |
| B2 | Only after at least one same-hardware volume reduction. | Possible if schedule selection method is novel and reproducible. | QEC benchmark tool can be packaged as baseline explorer. |
| B3 | Not until reaction-coordinate circuit vs denominator exists. | Unlikely before stronger chemistry baseline. | Chemistry resource explorer after denominator comparison. |
| B4/B8 | Only after circuit-level hidden task with adaptive spoofers. | Possible challenge-refresh protocol disclosure after novelty review. | Verification lab prototype after circuit-level generator. |
| B5/B6 | Not until real baselines/data exist. | Possible later for leakage-audited descriptor pipeline. | Materials screener only after leakage audit. |
| B7 | Only after regime-classified FT ledger. | Possible resource-ledger disclosure after layout assumptions. | Resource estimator prototype after workload schema stabilizes. |
| B9/B10 | Theory note possible if negative lemma/proof target is precise. | Usually not the lead route. | Boundary checker can become a claim-audit tool. |

## Immediate Assignment Order

1. `compiler-agent`: B1 native T-resource optimizer.
2. `ft-agent`: B7 min-STV regime classifier waiting on B1 output.
3. `qec-agent`: B2 circuit-level posterior decoder or calibrated leakage/flag dataset.
4. `verification-agent`: B4/B8 hidden task generator and adaptive spoofer.
5. `chemistry-agent`: B3 reaction observable circuit vs FCI denominator.
6. `theory-agent`: B10-T2 real-backend/hardware verifier bridge plus B9 negative lemma.
7. `materials-agent`: B6 computed descriptor audit with expanded negatives.

This sprint is complete only when at least one PR-quality artifact exists for
each spine and the portfolio audit still passes.

Sprint update 18ar: B1/B7 now has a line-1381 commutation-corridor pressure gate. T-B1-004ar consumes the best bounded context hints from T-B1-004ap/aq and reviews 10 best candidates, 32 context references, and 8 unique context lines. The cheap corridor model accepts 0 candidates: 7 references are inside the target packet, 13 are not standalone RZ-like rotations, 21 are blocked by support-touching CNOT or non-diagonal single-qubit structure, and 0 external standalone-Z references have a clear path into line 1381. This is not a full-circuit replay proof, but it closes the cheap corridor interpretation of the current bounded context hints.

Sprint update 18as: B1/B7 now has a full-circuit replay obligation gate. T-B1-004as consumes T-B1-004am/an/ao/ap/aq/ar and records the evidence still missing before the 3 bounded reduced-CNOT repairs can become B7 ledger savings. The gate keeps 3/3 bounded exact repairs, but symbolic exactness certificates, full-circuit replay events, replacement QASM patches, occurrence-class lifts, and B7 ledger acceptances are all 0. Two packets are resource-clean at bounded-packet level; line 1381 remains unpriced. Accepted replay, occurrence removal, proxy-T reduction, and B7 improvement remain 0.

Sprint update 18at: B1/B7 now has bounded OpenQASM 3 replacement snippets for the repaired reduced-CNOT packets. T-B1-004at emits 3/3 bounded QASM3 snippets and all 3 pass bounded exactness, keeping the candidate 9-CNOT reduction signal alive only as a future-if-accepted number. The source windows for line 1378 and line 1381 overlap on lines 1369-1377, so the snippets are not a composable full-circuit patch set. Accepted full-circuit patch count, replay certificates, occurrence removal, proxy-T reduction, and B7 improvement remain 0; the next step is merged-region resynthesis plus source-circuit replay.

Sprint update 18au: B1/B7 now has a non-overlap patch subset gate. T-B1-004au selects line 268 and line 1381 as the best non-overlapping bounded patch subset, drops line 1378 as contained inside the line-1381 window, and corrects the current composable bounded CNOT delta from 9 to 6. No full-circuit QASM rewrite, replay certificate, occurrence removal, proxy-T reduction, or B7 improvement is accepted; the next step is dialect-bridged full-circuit replay or a merged-region synthesis that recovers the dropped line-1378 delta.

Sprint update 18av: B1/B7 now has a QASM2 candidate rewrite gate. T-B1-004av
consumes the line-268 plus line-1381 non-overlap subset, converts the bounded
OpenQASM 3 `U` snippets into OpenQASM 2.0 `u3` syntax, and inserts them into
the `gcm_h6` source circuit as
`results/B1_B7_cone01_qasm2_candidate_rewrite_gate/gcm_h6_line268_line1381_candidate.qasm`.
The source CNOT count is 795 and the candidate CNOT count is 789, preserving
the current 6-CNOT structural delta. This is a replay-consumable candidate
artifact only: full-circuit replay, line-1378 merged-region recovery, local-U3
resource pricing, occurrence removal, proxy-T reduction, and B7 improvement all
remain unaccepted.

Sprint update 18aw: B1/B7 now has a full-statevector replay probe for the
T-B1-004av QASM2 candidate. T-B1-004aw removes final measurements from the
source and candidate `gcm_h6` circuits, then compares the 19-qubit
benchmark-default-input statevectors. Statevector dimension is 524,288; fidelity
is 0.9999999999999551; infidelity is 4.4853010194856324e-14; max
global-phase-aligned amplitude delta is 1.3908205762322243e-13; max probability
delta is 5.551115123125783e-16; measured q[4] marginal delta is
5.551115123125783e-16. This upgrades the branch from a structural candidate to
a whole-circuit numerical replay-pressure artifact, but it is still not
symbolic arbitrary-input equivalence, not accepted local-U3 pricing, not
occurrence removal, not proxy-T reduction, and not B7 improvement. The next
sprint gate should either turn this into symbolic or multi-input replay
evidence with resource pricing, or synthesize a merged line-1378/line-1381
region that recovers the dropped 3-CNOT delta.

Sprint update 18ax: B1/B7 now has sampled-input statevector replay pressure.
T-B1-004ax consumes T-B1-004aw and tests the same source/candidate circuits
across 8 deterministic inputs: 6 computational-basis preparations and 2 seeded
product states. All 8 pass, with min state fidelity 0.9999999999999547, max
infidelity 4.529709940470639e-14, max global-phase-aligned amplitude delta
1.392888964263601e-13, and max probability delta 1.8214596497756474e-15. This
is stronger than default-input replay but still sampled evidence, not symbolic
arbitrary-input equivalence, and accepted occurrence removal, proxy-T
reduction, local-U3 pricing, and B7 improvement remain 0.

Sprint update 18ay: B1/B7 now has phase-consistent and superposition replay
pressure. T-B1-004ay consumes T-B1-004ax and tests 4 phase-anchor inputs plus 4
superposition inputs after final measurements are removed. All 8 pass, with
overlap phase spread 1.3722356584366935e-13 radians, min overlap magnitude
0.9999999999999772, min state fidelity 0.9999999999999547, max infidelity
4.529709940470639e-14, and max probability delta 1.074140776324839e-14. This
reduces the independent-global-phase alignment risk, but it is still sampled
evidence, not symbolic arbitrary-input equivalence, and accepted occurrence
removal, proxy-T reduction, local-U3 pricing, and B7 improvement remain 0.

Sprint update 18az: B1/B7 now has global-phase anchored subspace replay
pressure. T-B1-004az consumes T-B1-004ay, fixes one global phase from the zero
input, and reuses that phase across 6 computational-basis anchors and 15
coherent pair superpositions. All 21 pass, with max global-anchor phase delta
3.142993331217661e-14 radians, min overlap magnitude 0.9999999999999772, min
state fidelity 0.9999999999999547, max infidelity 4.529709940470639e-14, and
max probability delta 1.074140776324839e-14. This is stronger sampled subspace
evidence, but still not symbolic arbitrary-input equivalence; accepted
occurrence removal, proxy-T reduction, local-U3 pricing, and B7 improvement
remain 0.

Sprint update 18ba: B1/B7 now has a finite linear-span replay certificate for
the T-B1-004az basis anchors. T-B1-004ba computes the restricted
source/candidate error operator over the six-dimensional input span under the
same zero-input global phase anchor. The spectral norm is
2.7889440543898627e-13, max basis L2 error is 2.534056605707275e-13, max basis
probability delta is 7.771561172376096e-16, and all 15 coherent pair witnesses
remain passed. This certifies only 6/524,288 input dimensions; full-space
symbolic equivalence, occurrence removal, proxy-T reduction, local-U3 pricing,
and B7 improvement remain 0.

Sprint update 18bb: B1/B7 now has a composable patch certificate for the
selected line-268 plus line-1381 QASM2 candidate. T-B1-004bb checks that the
selected windows are non-overlapping, both local-unitary replacement
certificates pass, the QASM2 candidate exists, and the structural CNOT count is
795 -> 789. Max selected patch residual norm is 6.513210005207597e-13 and max
entry error is 4.525273102184799e-13. One tolerance-bounded full-circuit
semantic replay/QASM patch artifact is accepted, but B7 occurrence removal,
proxy-T reduction, local-U3 pricing, line-1378 recovery, and ledger improvement
remain 0.

Sprint update 18bc: B1/B7 now has a line-1381 local-U3 pricing boundary gate.
T-B1-004bc consumes the T-B1-004bb composable patch certificate and prices the
remaining blocker: line 1381 retains 5 off-grid local-U3 parameters, equal to
100 unaccepted proxy-T pressure units under the current ledger. The accepted
semantic replay/QASM patch artifact remains 1, selected CNOT delta remains 6,
and the dropped line-1378 delta remains 3. This is not a resource win:
local-U3 pricing, occurrence removal, proxy-T reduction, and B7 ledger
improvement remain 0. The next sprint gate must eliminate, absorb, or
symbolically decompose the five line-1381 parameters, recover the line-1378
merged-region delta, or find a different occurrence-removing route.

Sprint update 18bd: B1/B7 now has an overlap-additivity bound for the dropped
line-1378 delta. T-B1-004bd consumes the non-overlap subset and T-B1-004bc
pricing gate, then checks the line-1378/line-1381 merged-region arithmetic.
Line 1378's source window [1369, 1377] is contained inside line 1381's source
window [1369, 1379] on the same [4, 8] support, so the union region has only 5
source CNOTs. Adding line 1381's 3-CNOT delta and line 1378's 3-CNOT delta
would require -1 replacement CNOTs. The max possible extra delta versus the
current line-1381 replacement under nonnegative CNOT accounting is 2, so the
full dropped line-1378 delta is not additively recoverable. Accepted
merged-region rewrite, occurrence removal, proxy-T reduction, and B7
improvement remain 0. The next sprint gate must synthesize a new union-region
replacement with replay and honest local-U3 pricing, or switch to a different
occurrence-removing route.

Sprint update 18be: B1/B7 now has a scoped union-region low-CNOT search gate.
T-B1-004be consumes the semantic packet, packet-synthesis search, and
T-B1-004bd overlap-additivity bound, then searches the actual line-1378/1381
union target [1369, 1379] with 0-CNOT and 1-CNOT local-U3 scaffolds. Both
1-CNOT orientations are tested. Exact low-CNOT passes are 0/3; the best
low-CNOT residual is 0.2548908758679516 and the best max entry error is
0.12724247975106365. The existing 2-CNOT line-1381 replacement remains the
current exact candidate in this branch. This closes the scoped 0/1-CNOT
shortcut but is not a global lower-bound theorem: accepted union rewrite,
full-circuit replay, occurrence removal, proxy-T reduction, and B7 improvement
remain 0.

Sprint update 18bf: B1/B7 now has a 2-CNOT orientation census for that same
union target. T-B1-004bf searches all four length-2 CNOT direction sequences
for the line-1378/1381 union window [1369, 1379]. All 4/4 sequences pass exact
numerical replay; the best exact sequence is 01-10 with residual
5.812946138498332e-13, max entry error 3.4095575404049453e-13, and 13 off-pi/4
local-U3 parameters among 18 total parameters. This makes the 2-CNOT candidate
robust rather than fragile, but it remains candidate-only: accepted
full-circuit replay, QASM patch, local-U3 pricing, occurrence removal,
proxy-T reduction, and B7 improvement remain 0.

Sprint update 18bg: B1/B7 now has a pricing-dominance gate for the 2-CNOT
census candidates. T-B1-004bg compares the exact T-B1-004bf candidates with
the current line-1381 pricing boundary. The current branch has 5 off-pi/4
local-U3 parameters, priced as 100 proxy-T pressure units; the best-priced
exact census candidate has 13 off-pi/4 parameters, priced as 260 proxy-T
pressure units. The census candidate is therefore not adopted as a better B7
route. Selected replacement change, occurrence removal, proxy-T reduction, and
B7 improvement remain 0.

Sprint update 18bh: B1/B7 now has a line-1381 leave-one-out parameter gate.
T-B1-004bh keeps the current five-parameter exact line-1381 repair, snaps each
one of the five off-pi/4 local-U3 parameters back to the pi/4 grid, and
re-optimizes the other four parameters on the same two-CNOT scaffold. Exact
passes are 0/5. The best leave-one-out residual is 0.09892087709180968 at
parameter index 3, about 9.89e6 times the 1e-8 exact tolerance; the worst is
0.288314847983953 at parameter index 4. This blocks a cheap single-parameter
free-removal claim, but it is not a global minimality theorem and does not
eliminate, absorb, symbolically decompose, or price the five line-1381
parameters. Occurrence removal, proxy-T reduction, and B7 improvement remain 0.

Sprint update 18bi: B1/B7 now has a line-1381 leave-two-out parameter gate.
T-B1-004bi keeps the same five-parameter exact line-1381 repair, snaps every
pair of the five off-pi/4 local-U3 parameters back to the pi/4 grid, and
re-optimizes the remaining three parameters on the same two-CNOT scaffold.
Exact passes are 0/10. The best leave-two-out residual is
0.13583443746892182 for fixed pair [9, 16], about 1.36e7 times the 1e-8 exact
tolerance; the worst is 0.41204448255804876 for fixed pair [16, 17]. This
blocks a cheap two-parameter free-removal claim, but it is still not a global
five-parameter minimality theorem. Occurrence removal, proxy-T reduction,
local-U3 acceptance, and B7 improvement remain 0.

Sprint update 18bj: B1/B7 now has a line-1381 leave-three-out parameter gate.
T-B1-004bj keeps the same five-parameter exact line-1381 repair, snaps every
triple of the five off-pi/4 local-U3 parameters back to the pi/4 grid, and
re-optimizes the remaining two parameters on the same two-CNOT scaffold. Exact
passes are 0/10. The best leave-three-out residual is 0.29673862906454757 for
fixed triple [4, 9, 16], about 2.97e7 times the 1e-8 exact tolerance; the
worst is 0.7449029676343185 for fixed triple [4, 16, 17]. This blocks a cheap
three-parameter free-removal claim, but it is still not a global
five-parameter minimality theorem. Occurrence removal, proxy-T reduction,
local-U3 acceptance, and B7 improvement remain 0.

Sprint update 18bk: B1/B7 now has a line-1381 leave-four-out parameter gate.
T-B1-004bk keeps the same five-parameter exact line-1381 repair, snaps every
quadruple of the five off-pi/4 local-U3 parameters back to the pi/4 grid, and
re-optimizes the remaining one parameter on the same two-CNOT scaffold. Exact
passes are 0/5. The best leave-four-out residual is 0.45761708677312707 for
fixed quadruple [3, 4, 9, 16], about 4.58e7 times the 1e-8 exact tolerance;
the worst is 0.8369082341779268 for fixed quadruple [4, 9, 16, 17]. This
blocks a cheap four-parameter free-removal claim, but it is still not a global
five-parameter minimality theorem. Occurrence removal, proxy-T reduction,
local-U3 acceptance, and B7 improvement remain 0.

Sprint update 18bl: B1/B7 now has a line-1381 leave-five-out endpoint gate.
T-B1-004bl keeps the same five-parameter exact line-1381 repair, snaps all
five off-pi/4 local-U3 parameters back to the pi/4 grid, and leaves no
parameter free for re-optimization on the same two-CNOT scaffold. Exact pass /
fail is 0/1. The all-grid residual is 0.8415210419190079, about 8.42e7 times
the 1e-8 exact tolerance. This blocks a cheap all-grid snap interpretation,
but it is still not a global five-parameter minimality theorem. Occurrence
removal, proxy-T reduction, local-U3 acceptance, and B7 improvement remain 0.

Sprint update 18bm: B1/B7 now has a union-region grid-snap pricing gate.
T-B1-004bm consumes the four exact 2-CNOT union-region census candidates from
T-B1-004bf and snaps every local-U3 parameter in each candidate back to the
pi/4 grid. Exact pass / fail is 0/4. The best grid-snap residual is
0.36435162331693166 on sequence `10-10`, about 3.64e7 times the 1e-8 exact
tolerance; the worst residual is 1.021457442072864 on sequence `10-01`. This
blocks a cheap grid-priced adoption of the union-census route and keeps
occurrence removal, proxy-T reduction, local-U3 pricing acceptance, and B7
improvement at 0.

Sprint update 18bn: B1/B7 now has a union-region one-free-parameter pricing
gate. T-B1-004bn consumes the same four exact 2-CNOT union-region census
candidates from T-B1-004bf, snaps all local-U3 parameters to the pi/4 grid, and
then frees exactly one parameter at a time. All 72 one-free-parameter trials
fail exact replay. The best residual is 0.25709607640616583 on sequence
`10-10` at parameter index 7, about 2.57e7 times the 1e-8 exact tolerance; the
worst best-sequence residual is 0.6857140007440164 on sequence `10-01`. This
blocks a 20-proxy-T one-free-parameter adoption of the union route and keeps
occurrence removal, proxy-T reduction, local-U3 pricing acceptance, and B7
improvement at 0.

Sprint update 18bo: B1/B7 now has a union-region two-free-parameter pricing
gate. T-B1-004bo consumes the same four exact 2-CNOT union-region census
candidates from T-B1-004bf, snaps all local-U3 parameters to the pi/4 grid, and
then frees every possible pair of parameters. All 612 two-free-parameter trials
fail exact replay. The best residual is 0.1831095797026285 on sequence `10-10`
at pair `[5, 7]`, about 1.83e7 times the 1e-8 exact tolerance; the worst
best-sequence residual is 0.46644639853601 on sequence `10-01`. This blocks a
40-proxy-T two-free-parameter adoption of the union route. The next useful work
must change scaffold, produce symbolic/context absorption, accept honest larger
local-U3 pricing with full-circuit replay, or find a different
occurrence-removing branch.

Sprint update 18bp: B1/B7 now has a targeted three-free expansion pricing gate.
T-B1-004bp takes each sequence's best failed T-B1-004bo two-parameter pair,
adds one more free local-U3 parameter, and re-optimizes that targeted triple.
All 64 targeted three-free trials fail exact replay. The best residual is
0.04582709543239648 on sequence `10-10` at triple `[5, 7, 4]`, about 4.58e6
times the 1e-8 exact tolerance; the worst best-sequence residual is
0.3812803680403496 on sequence `10-01`. This is not an exhaustive three-free
lower bound, but it blocks the most direct 60-proxy-T extension of the failed
two-free route. Occurrence removal, proxy-T reduction, local-U3 pricing
acceptance, and B7 ledger improvement remain 0.

Sprint update 18bq: B1/B7 now has a union-region 3-CNOT pricing screen. Instead
of freeing more cheap local parameters, T-B1-004bq changes scaffold and allows
3 CNOTs across all 8 direction sequences for the same line-1378/1381 union
target. All 8 sequences are locally exact, with best residual
5.810128819011275e-13 on sequence `10-01-10`; however the best exact priced
candidate is sequence `10-10-01` with 18 off-pi/4 local-U3 parameters, or 360
proxy-T pressure units. This is worse than the current line-1381 5-parameter /
100-proxy-T boundary and does not structurally dominate the 2-CNOT line-1381
replacement. The next useful work must change scaffold in a way that actually
reduces priced local-U3 burden, prove symbolic/context absorption, or find a
different occurrence-removing route.

Sprint update 18br: B1/B7 now has a context-absorption gate for that best exact
3-CNOT priced candidate. T-B1-004br consumes sequence `10-10-01` and tests its
18 off-pi/4 local-U3 parameters against the native optimized gcm_h6 rotation
inventory plus the same-support context around the union window. The gate finds
0 exact inventory matches, 0 absolute-angle inventory matches, 0 same-support
context matches, and 0 exact one-step cancellations back to the pi/4 grid. The
best one-step grid-cancellation error is 0.000655799901145393, which is close
but not exact. The 3-CNOT route remains pricing-dominated, and occurrence
removal, proxy-T reduction, local-U3 pricing acceptance, and B7 ledger
improvement remain 0.

Sprint update 18bs: B1/B7 now has a bounded multi-rotation context gate for the
same best exact 3-CNOT priced candidate. T-B1-004bs keeps sequence `10-10-01`,
the 18 off-pi/4 local-U3 parameters, and the 44 same-support context rotation
arguments, then tests signed sums of two or three context rotations. It checks
3,784 width-2 combinations and 105,952 width-3 combinations per parameter, for
1,975,248 signed-combination tests overall. Exact width-2 absorption is 0/18,
exact width-3 absorption is 0/18, and the best width-2/width-3 grid error
remains 0.000655799901145393. This closes the bounded two-/three-rotation
context escape hatch for the direct 3-CNOT route; occurrence removal, proxy-T
reduction, local-U3 pricing acceptance, and B7 ledger improvement remain 0.

Sprint update 18bt: B1/B7 now has an exactly-four-rotation context gate for the
same direct 3-CNOT route. T-B1-004bt keeps sequence `10-10-01`, the same 18
off-pi/4 local-U3 parameters, and the same 44 same-support context rotation
arguments, then tests signed sums of exactly four context rotations. It checks
2,172,016 width-4 combinations per parameter, for 39,096,288 signed-combination
tests overall. Exact width-4 absorption is 0/18; the best width-4 grid error
remains 0.000655799901145393 and the worst best-parameter error is
0.027779719778975753. This closes the bounded exactly-four-rotation context
escape hatch for the direct 3-CNOT route; occurrence removal, proxy-T
reduction, local-U3 pricing acceptance, and B7 ledger improvement remain 0.

Sprint update 18bu: B1/B7 now has an OpenQASM 3 candidate export gate for the
line-268 plus line-1381 branch. T-B1-004bu consumes the legacy-dialect replay
candidate and emits
`results/B1_B7_cone01_openqasm3_candidate_export_gate/gcm_h6_line268_line1381_candidate_openqasm3.qasm`.
The artifact starts with `OPENQASM 3.0`, uses `stdgates.inc`, declares
`qubit[19] q` and `bit[1] c`, converts 487 `u3` gates to `U`, converts the
final measurement into assignment syntax, and preserves operation counts: 789
`cx`, 601 `rz`, 487 `U`, and 1 measurement. This accepts one QASM3 export
artifact, but replay proof, local-U3 pricing, occurrence removal, proxy-T
reduction, and B7 ledger improvement remain 0.

Sprint update 18bv: B1/B7 now has an OpenQASM 3 parser-readiness gate. The
T-B1-004bv local strict parser accepts the T-B1-004bu artifact with 0 errors,
19 qubits, 1 bit, 1,884 statements, 1,878 operation rows, and preserved counts
of 789 `cx`, 601 `rz`, 487 `U`, and 1 measurement. Qiskit core is installed,
but the OpenQASM 3 loader cannot run because `qiskit_qasm3_import` is missing,
so accepted Qiskit-loader parse artifacts remain 0. This is honest progress on
toolchain readiness, not replay proof or B7 resource credit.

Sprint update 18bw: B1/B7 now has an OpenQASM 3 structural roundtrip gate. The
gate normalizes the legacy OpenQASM 2 candidate and the OpenQASM 3 artifact into
canonical instruction streams, then compares them exactly. Both streams have
1,878 instructions, 0 mismatches, 0 length delta, identical SHA256 stream hash
`7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343`, and
operation counts of 789 `cx`, 601 `rz`, 487 `U`, and 1 measurement. This accepts
one structural roundtrip artifact only; Qiskit-loader readiness, semantic
replay, local-U3 pricing, occurrence removal, proxy-T reduction, and B7 ledger
improvement remain 0.

Sprint update 18bx: B1/B7 now has a project-local OpenQASM 3 semantic replay
gate. T-B1-004bx consumes the structural roundtrip artifact, parses the
OpenQASM 3 file with the project's strict subset parser, constructs a
`QuantumCircuit` directly, removes final measurements, and compares the
default-input 19-qubit statevector against the optimized source circuit. The
replay passes with fidelity 0.9999999999999551, infidelity
4.4853010194856324e-14, max aligned amplitude delta 1.3908205762322243e-13,
max probability delta 5.551115123125783e-16, and measured q[4] marginal delta
5.551115123125783e-16. This accepts one project-local OpenQASM 3 replay
artifact only; Qiskit-loader parse, symbolic/arbitrary-input equivalence,
local-U3 pricing, occurrence removal, proxy-T reduction, and B7 ledger
improvement remain 0.

Sprint update 18by: B1/B7 now has a project-local OpenQASM 3 multi-input replay
gate. T-B1-004by consumes the local semantic replay artifact and checks 8
deterministic sampled inputs through the parsed OpenQASM 3 candidate and the
optimized source after final measurement removal. The suite covers 6
computational-basis preparations and 2 seeded product states; all 8 cases pass.
Min state fidelity is 0.9999999999999547, max infidelity is
4.529709940470639e-14, max aligned amplitude delta is
1.392888964263601e-13, and max probability delta is 1.8214596497756474e-15.
This accepts one project-local OpenQASM 3 multi-input replay artifact only;
Qiskit-loader replay, symbolic/arbitrary-input equivalence, local-U3 pricing,
occurrence removal, proxy-T reduction, and B7 ledger improvement remain 0.

Sprint update 18bz: B1/B7 now has a project-local OpenQASM 3 phase-consistent
replay gate. T-B1-004bz consumes the OpenQASM 3 multi-input replay artifact and
checks 4 phase-anchor inputs plus 4 superposition inputs through the parsed
OpenQASM 3 candidate and the optimized source after final measurement removal.
All 8 cases pass. The overlap phase spread is 1.3722356584366935e-13 radians,
min overlap magnitude is 0.9999999999999772, min state fidelity is
0.9999999999999547, max infidelity is 4.529709940470639e-14, max aligned
amplitude delta is 1.392888964263601e-13, and max probability delta is
1.074140776324839e-14. This accepts one project-local OpenQASM 3
phase-consistent replay artifact only; Qiskit-loader replay,
symbolic/arbitrary-input equivalence, local-U3 pricing, occurrence removal,
proxy-T reduction, and B7 ledger improvement remain 0.

Sprint update 18ca: B1/B7 now has a project-local OpenQASM 3 global-phase
subspace replay gate. T-B1-004ca consumes the OpenQASM 3 phase-consistent replay
artifact, fixes the zero-input global phase anchor, and reuses that same anchor
across 6 basis-subspace anchors and 15 coherent pair superpositions. All 21
cases pass. The max global-anchor phase delta is 3.142993331217661e-14 radians,
min overlap magnitude is 0.9999999999999772, min state fidelity is
0.9999999999999547, max infidelity is 4.529709940470639e-14, max aligned
amplitude delta is 1.3928889642636009e-13, and max probability delta is
1.074140776324839e-14. This accepts one project-local OpenQASM 3 global-phase
subspace replay artifact only; Qiskit-loader replay, symbolic/arbitrary-input
equivalence, local-U3 pricing, occurrence removal, proxy-T reduction, and B7
ledger improvement remain 0.

Sprint update 18cd: B1/B7 now has an OpenQASM 3 provenance seal gate.
T-B1-004cd consumes the T-B1-004cc patch-lift artifact and seals the underlying
QASM2 candidate, OpenQASM 3 candidate, source patch certificate, structural
roundtrip certificate, finite-span certificate, and patch-lift certificate with
file-level SHA-256 hashes. Both QASM files have 1,884 raw lines and normalize to
the same 1,878-instruction stream with hash
`7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343`; the
combined provenance seal hash is
`159c9b1d99a607d463fe712a190b35460603712561a4ea8eb4033bf4de495902`. This
accepts one project-local provenance-seal artifact only; Qiskit-loader replay,
full-space symbolic/local-unitary equivalence, local-U3 pricing, occurrence
removal, proxy-T reduction, and B7 ledger improvement remain 0.

Sprint update 18cb: B1/B7 now has a project-local OpenQASM 3 finite linear-span
replay certificate. T-B1-004cb consumes T-B1-004ca, rebuilds the candidate
through the project-local OpenQASM 3 parser, and computes the restricted error
operator on the six-dimensional basis-anchor span under the same zero-input
global phase. The certificate passes with spectral norm 2.7889440543898627e-13,
Frobenius norm 6.134324404657074e-13, max basis L2 error
2.534056605707275e-13, max basis amplitude delta 1.3928889642636009e-13,
max basis probability delta 7.771561172376096e-16, max source/candidate Gram
delta 1.9984014443252818e-15, and max cross-Gram delta
4.403624367368429e-14. This accepts one project-local OpenQASM 3 finite-span
certificate only; it covers 6/524,288 input dimensions and does not claim
Qiskit-loader replay, full-space symbolic/local-unitary equivalence,
local-U3 pricing, occurrence removal, proxy-T reduction, or B7 ledger
improvement.

Sprint update 18cc: B1/B7 now has an OpenQASM 3 composable patch-lift gate.
T-B1-004cc consumes the QASM2 composable patch certificate, the OpenQASM 3
structural roundtrip, and the OpenQASM 3 finite-span certificate. The legacy
candidate and OpenQASM 3 artifact still share the same 1,878-instruction stream
with zero mismatches and stream hash
`7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343`; the
selected patch lines remain `[268, 1381]`, dropped overlap line `[1378]`, max
selected patch residual `6.513210005207597e-13`, max selected entry error
`4.525273102184799e-13`, and OpenQASM 3 finite-span spectral error
`2.7889440543898627e-13`. This accepts one project-local OpenQASM 3 composable
patch-lift artifact only; Qiskit-loader replay, full-space symbolic/local-unitary
equivalence, local-U3 pricing, occurrence removal, proxy-T reduction, and B7
ledger improvement remain 0.

Sprint update 18ce: B1/B7 now has an OpenQASM 3 source-map gate. T-B1-004ce
consumes the provenance-sealed QASM2/OpenQASM 3 patch-lift chain and builds a
one-to-one instruction source map across all 1,878 normalized instructions. The
raw-line drift count is 0, the source-map hash is
`92a499ea6d549426095fbb0fc878f7033027991621a6d5ea1c03cd25d82e9e1e`, selected
line 268 maps to instruction index 263, selected line 1381 maps to instruction
index 1375, and dropped overlap line 1378 maps to instruction index 1372. This
accepts one project-local source-map artifact only; Qiskit-loader replay,
full-space symbolic/local-unitary equivalence, local-U3 pricing, occurrence
removal, proxy-T reduction, and B7 ledger improvement remain 0.

Sprint update 18cf: B1/B7 now has a compact OpenQASM 3 patch witness packet.
T-B1-004cf consumes the OpenQASM 3 source map, composable patch certificate,
patch-lift result, non-overlap subset, and bounded replacement patch evidence.
It emits three witness rows for candidate lines 268, 1378, and 1381, with line
1378 explicitly marked as the dropped-overlap witness. The witness instruction
indices are 263, 1372, and 1375; selected witness count is 2, dropped-overlap
witness count is 1, selected CNOT delta remains 6, lost overlap delta remains 3,
and the witness packet hash is
`e0d2e63f3f2c16be685baef3360ff68d5765db549c5e17e655a6e74c6fb82dc8`. This
accepts one project-local review packet only; Qiskit-loader replay, full-space
symbolic/local-unitary equivalence, local-U3 pricing, occurrence removal,
proxy-T reduction, and B7 ledger improvement remain 0.

Sprint update 18cg: B1/B7 now has a Qiskit-loader OpenQASM 3 replay gate.
T-B1-004cg consumes the parser-readiness, project-local semantic replay, and
patch witness packet gates, then loads the exported OpenQASM 3 candidate through
Qiskit's `qasm3` loader after adding `qiskit-qasm3-import>=0.6`. The loader
parses 19 qubits, 1 classical bit, depth 1483, and operation counts `cx=789`,
`rz=601`, `u=487`, `measure=1`. Default-input replay against the optimized
source passes with fidelity `0.9999999999999551`, max aligned amplitude delta
`1.3908205762322243e-13`, max probability delta `5.551115123125783e-16`, and
measured q[4] marginal delta `5.551115123125783e-16`. This accepts one
Qiskit-loader parse artifact and one Qiskit-loader replay artifact only;
arbitrary-input/symbolic equivalence, local-U3 pricing, occurrence removal,
proxy-T reduction, and B7 ledger improvement remain 0.

Sprint update 18ch: B1/B7 now has Qiskit-loader multi-input replay pressure.
T-B1-004ch consumes the default-input Qiskit-loader gate and the project-local
OpenQASM 3 multi-input replay gate, then replays the Qiskit-loaded OpenQASM 3
candidate on the same deterministic 8-input suite. All 8 cases pass: 6
computational-basis inputs and 2 seeded product states. Min state fidelity is
`0.9999999999999547`, max infidelity is `4.529709940470639e-14`, max aligned
amplitude delta is `1.392888964263601e-13`, max probability delta is
`1.8214596497756474e-15`, and failed cases are 0. This accepts one
Qiskit-loader multi-input replay artifact only; arbitrary-input/symbolic
equivalence, local-U3 pricing, occurrence removal, proxy-T reduction, and B7
ledger improvement remain 0.

Sprint update 18ci: B1/B7 now has Qiskit-loader phase-consistent replay
pressure. T-B1-004ci consumes the Qiskit-loader multi-input replay gate and the
project-local OpenQASM 3 phase-consistent replay gate, then replays the
Qiskit-loaded OpenQASM 3 candidate on 4 phase-anchor inputs plus 4
superposition inputs. All 8 cases pass with overlap phase spread
`1.3722356584366935e-13` radians, min overlap magnitude
`0.9999999999999772`, min fidelity `0.9999999999999547`, max infidelity
`4.529709940470639e-14`, max aligned amplitude delta
`1.392888964263601e-13`, max probability delta `1.074140776324839e-14`, and
failed cases 0. This accepts one Qiskit-loader phase-consistent replay artifact
only; arbitrary-input/symbolic equivalence, local-U3 pricing, occurrence
removal, proxy-T reduction, and B7 ledger improvement remain 0.

Sprint update 18cj: B1/B7 now has Qiskit-loader global-phase anchored subspace
replay pressure. T-B1-004cj consumes the Qiskit-loader phase-consistent replay
gate and the project-local OpenQASM 3 global-phase subspace replay gate, then
fixes the zero-input global phase anchor for the Qiskit-loaded candidate. All
21 cases pass across 6 basis anchors and 15 coherent pair superpositions: max
global-anchor phase delta is `3.142993331217661e-14` radians, min overlap
magnitude is `0.9999999999999772`, min fidelity is `0.9999999999999547`, max
infidelity is `4.529709940470639e-14`, max aligned amplitude delta is
`1.3928889642636009e-13`, max probability delta is
`1.074140776324839e-14`, and failed cases are 0. This accepts one
Qiskit-loader global-phase subspace replay artifact only; arbitrary-input or
symbolic equivalence, local-U3 pricing, occurrence removal, proxy-T reduction,
and B7 ledger improvement remain 0.

Sprint update 18ck: B1/B7 now has a Qiskit-loader finite linear-span replay
certificate. T-B1-004ck consumes the Qiskit-loader global-phase subspace replay
gate and the project-local OpenQASM 3 linear-span certificate, keeps the same
zero-input global phase anchor, and computes the replay error operator over the
6-dimensional basis-anchor span. The loader-backed certificate passes with
spectral norm `2.7889440543898627e-13`, Frobenius error
`6.134324404657074e-13`, max basis L2 error `2.534056605707275e-13`, max basis
amplitude delta `1.3928889642636009e-13`, max basis probability delta
`7.771561172376096e-16`, max source/candidate Gram delta
`1.9984014443252818e-15`, max cross-Gram delta
`4.403624367368429e-14`, and validation errors 0. This accepts one
Qiskit-loader finite-span certificate for 6/524,288 input dimensions only;
arbitrary-input or symbolic equivalence, local-U3 pricing, occurrence removal,
proxy-T reduction, and B7 ledger improvement remain 0.

Sprint update 18cl: B1/B7 now has Qiskit-loader support for the OpenQASM 3
composable patch lift. T-B1-004cl consumes the project-local OpenQASM 3
composable patch-lift gate, the Qiskit-loader global-phase subspace replay gate,
and the Qiskit-loader finite linear-span certificate for the same exported
candidate. The supported patch set remains selected lines [268, 1381] with
dropped overlap line [1378], stream mismatches 0 over 1,878 normalized
instructions, Qiskit-loader finite-span spectral norm
`2.7889440543898627e-13`, max basis L2 error `2.534056605707275e-13`, max
probability delta `7.771561172376096e-16`, max cross-Gram delta
`4.403624367368429e-14`, and validation errors 0. This accepts one
Qiskit-loader composable patch-lift support artifact only; arbitrary-input or
symbolic equivalence, local-U3 pricing, occurrence removal, proxy-T reduction,
and B7 ledger improvement remain 0.

Sprint update 18cm: B1/B7 now has a Qiskit-loader evidence-seal gate.
T-B1-004cm consumes the exported OpenQASM 3 candidate plus the Qiskit-loader
default replay, multi-input replay, phase-consistent replay, global-phase
subspace replay, finite linear-span certificate, and composable patch-lift
support artifacts. It records 7 source artifact hashes and emits evidence seal
`d06c1fdae3ad7cad1971cdcdcea1f890d3931924a7e70affc25fdf89737e09a8`. The seal
keeps Qiskit 2.4.1, qiskit-qasm3-import 0.6.0, openqasm3 1.0.1, depth 1483,
operation counts cx=789/rz=601/u=487/measure=1, 8 multi-input cases, 8
phase-consistent cases, 21 global-phase cases, 0 failed replay cases, selected
lines [268, 1381], dropped overlap line [1378], and B7 credit 0. This is a
drift-detection and reproducibility gate only; arbitrary-input or symbolic
equivalence, local-U3 pricing, occurrence removal, proxy-T reduction, and B7
ledger improvement remain 0.

Sprint update 18cn: B1/B7 now has a Qiskit-loader evidence-seal reproduction
gate. T-B1-004cn independently recomputes all 7 source artifact hashes, reruns
the T-B1-004cm seal generator, and requires the expected, independent, and
reproduced seals to match
`d06c1fdae3ad7cad1971cdcdcea1f890d3931924a7e70affc25fdf89737e09a8`. The
reproduction passes with 7/7 source-hash matches, 0 mismatch paths, byte-stable
JSON hash `f7a5f57ced33e3d8c3f8be12fbcd0dba26a5b42206dac8bb0e1ed1723a735ad2`,
byte-stable Markdown hash
`7a648d78758b0f6499d7a743993714fef3d47932b9b02ec5de317228c7828dc7`, 0 failed
replay cases, selected lines [268, 1381], dropped overlap line [1378], and B7
credit 0. This accepts one evidence-seal reproduction artifact only; arbitrary
input or symbolic equivalence, local-U3 pricing, occurrence removal, proxy-T
reduction, and B7 ledger improvement remain 0.
