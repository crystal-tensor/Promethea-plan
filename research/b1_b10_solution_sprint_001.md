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
