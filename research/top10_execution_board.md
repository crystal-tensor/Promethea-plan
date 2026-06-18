# Top 10 Execution Board v0.1

Last updated: 2026-06-18

Purpose: turn the Top 10 quantum attack directions from initialized v0
artifacts into a one-year execution portfolio with decision gates. This file
does not claim that any hard problem is solved. It defines what each direction
must prove next, when to merge directions, and when to demote weak paths.

Machine-readable source: `top10_execution_board.json`
Detailed problem dossiers: `top10_problem_dossiers.md`
Machine-readable dossier source: `top10_problem_dossiers.json`

## Portfolio State

Current state: **stage 1l evidence hardening; B10-T1 now has an optimistic B5 response-sampler cost stress showing no positive same-access route, while B2 has a false-positive erasure boundary and B5 keeps production DMRG open**.

The first research pass created:

- a 100-problem catalog,
- a Top 20 scoring and evidence map,
- a Top 10 attack pack,
- B1-B10 benchmark or prototype artifacts,
- a passing portfolio audit with no warnings.

The next pass should stop expanding the list and instead force each Top 10
direction through a 30-day validation gate.

## Lanes

| Lane | Directions | Role |
|---|---|---|
| Technical system spine | B1, B2, B7 | Highest chance of a coherent technical solution path: certified compression, QEC overhead, and FT co-design. |
| Coupled application | B3, B5, B6 | Chemistry/materials applications that need stronger classical baselines before claims become serious. |
| Verification protocol | B4, B8 | Should be merged into one verification track unless B4 gets a circuit-level hardness task quickly. |
| Theory and negative results | B9, B10 | Useful as theorem-target and negative-result engines, not short-term breakthrough claims. |

## Decision Rules

- Monthly keep rule: keep a direction only if the next 30-day artifact can
  falsify or improve a concrete claim.
- Merge rule: merge directions when their validation stack is shared, such as
  B4 plus B8 or B1 plus B7.
- Technical-gate rule: do not promote a direction into publication, patent,
  financing, or productization work until it has a reproduced baseline, a
  measurable delta, and an explicit limitation section.
- Replacement rule: replace a Top 10 direction with a Tier 2 candidate if two
  consecutive monthly gates fail without producing a useful negative result.

## Direction Gates

| ID | Problem | Current maturity | 30-day gate | Kill or merge condition |
|---|---|---|---|---|
| B1 | Hardware-aware quantum circuit compression | Virtual-SWAP plus weak T-resource diagnostic | Strengthen local proof logs plus weak T-resource diagnostic into a native-basis non-Clifford/T-depth optimizer that improves the minimum B7 factory-dominated workload, not only the mean. | Demote if reductions disappear on broader benchmarks or certificate generation cannot scale beyond local rewrite evidence. |
| B2 | Low-overhead QEC | Stim baseline plus closed reduced-round artifact boundary; T-B2-004 Stim HERALDED_ERASE / DEPOLARIZE1 stress found 10 d=5/d=7 improved rows, and T-B2-005 false-positive stress runs 270 configs / 324k shots with 5 positive-false-positive d=5/d=7 improved rows at fp=0.001/tick but 0 improved rows by fp=0.003/tick. | Replace the false-positive Stim stress with a shot-conditioned erasure decoder or calibrated leakage model that preserves d=5/d=7 target-volume rows under noise mismatch and realistic flag false-positive overhead. | Demote the leakage-erasure route if the d=5/d=7 target-volume rows disappear under shot-conditioned erasure decoding, calibrated leakage stress, or realistic flag false-positive overhead above the observed fp=0.001/tick survival boundary. |
| B3 | Molecular reaction dynamics | T-B3-011 cross-molecule UCC/ADAPT pressure/demotion boundary: H2/LiH/H2O/N2 bounded high-coefficient sampled covariance pressure has 35 sampled groups total, 384 shots/group, mean/max variance error 0.0833/0.5029, max optimizer-loop shots lower bound 475,043,013,690,000, max optimizer-loop 2Q lower bound 281,225,464,104,480,000, and denominator wins remain 0. | Keep B3 as a negative-boundary track unless a rescue-only T-B3-012 produces real multi-parameter UCCSD/ADAPT covariance or stronger-than-QWC measurement that beats selected-CI/DMRG/tensor denominators after optimizer-loop accounting. | Demote current one-parameter UCC/ADAPT + QWC route; do not spend more B3 effort without a concrete rescue mechanism. |
| B4 | Verifiable quantum advantage | Toy hidden-trap protocol plus shared B4/B8 CNOT hidden-projection refresh proxy: 192 configs, honest completeness 1.0, no-refresh high-leakage soundness 0.675, repaired high-leakage soundness 0.0 | Upgrade the CNOT/projection proxy to hardware-executable randomized measurement circuits or attack it with trained/generative spoofers. | Merge into B8 if circuit-level hardness remains absent beyond property-testing proxies. |
| B5 | Strongly correlated matter | Small exact Hubbard reference plus cluster proxy; T-B5-001 B10-linked oracle-tuned denominator; T-B5-002 non-oracle response embedding denominator with mean/max error 0.05098/0.12308; T-B5-003a exact-state-seeded MPS/Schmidt pressure reference with mean/max error 0.000442/0.001695; T-B5-003b non-exact-state-seeded variational MPS/ALS prototype with bond dimensions 2/4, 3 restarts x 8 sweeps, mean/max error 0.01806/0.03907, min overlap 0.9626, and 0 rows beating the seeded MPS reference; T-B5-004 two-site finite-DMRG-style pressure prototype with bond dimension 4, 2 restarts x 4 sweeps, mean/max error 0.08196/0.27710, min overlap 0.93945, 4 rows beating one-site ALS, and 0 rows beating seeded MPS. | Replace both prototypes with mature canonical-environment variational DMRG/MPS, or compare a candidate quantum impurity/response kernel after full state-preparation, measurement, optimizer-loop, and classical denominator costs. | Demote if the benchmark remains 1D-only with prototype tensor references and no deployable DMRG/MPS baseline or quantum response-kernel costed comparison. |
| B6 | High-temperature superconductivity search | T-B6-002 formula-derived descriptor screen: 38 records / 22 families, 12 expanded negative controls, B5-linked correlation/screening proxies, formula AP@12 0.10 vs family-prior AP@12 1.0, post-split formula AP 0.5947 vs family-prior 0.9821; 0 validation errors; no discovery, mechanism, database, or computed-observable claim. | Replace formula proxies with crystallographic/DFT/B5-computed observables and expand post-2008 negatives so family priors cannot dominate. | Demote if computed descriptors do not beat family-prior and random baselines after expanded negative controls and family/time splits. |
| B7 | Fault-tolerance co-design | B1/B2 bridge plus FT synthesis ledger; `w8_21` claim-boundary closure with 43480 optimizer runs, 0 exact replacements, and 0 ledger removal | Improve the B7 minimum row through B1 T-resource work, or produce a symbolic KAK/Clifford-scaffold proof / alternate occurrence-removing rewrite for `gcm_h6`. | Demote if B1/B2-linked reductions collapse once physical layout, factory throughput, feed-forward, and occurrence-level synthesis certificates are explicit. |
| B8 | Classical verification of quantum outputs | Hidden-invariant test, adaptive leakage boundary, B4/B8 circuit-refresh proxy, trained/generative spoofer stress, B10-T2 proof gate, restricted lemma, transcript/device-noise bridge, ideal Qiskit/Aer verifier bridge, noisy Aer bridge, and backend-calibrated-style GenericBackendV2 bridge: 5760 target-property-derived noisy circuits, safe calibrated honest acceptance 1.0, adversary acceptance 0.25, inherited transcript safe soundness 0.0208 | Replace GenericBackendV2 snapshots with real backend properties or hardware randomized-measurement verifier execution. | Demote if hidden invariants remain too easy to infer once challenge refresh and adaptive generative spoofers are added. |
| B9 | Quantum PCP / Local Hamiltonian hardness | Exact small-instance gap lab plus finite-instance failed gap-amplification negative lemma, Lean-style symbolic skeleton, and named-family cluster-stabilizer width/locality skeleton: n=4,5,6 all terms scale by 1.35, max locality stays 3, raw gap amplifies, normalized gap is invariant, and the certificate is rejected | Create a real Lean/mathlib or equivalent proof-checkable project and formalize support-size, uniform-scaling, spectral-width, and normalized-gap invariance lemmas for all n >= 4. | Keep only as a negative-result track unless a restricted theorem target becomes precise. |
| B10 | Boundary of BQP | T-B10-012 B5 same-access sampling-or-DMRG bridge: 4 denominator ladder rows, 5 sampling requirements all blocking, 6 seeded-MPS-over-non-oracle rows, 0 variational-over-seeded rows, no sampling oracle, no production DMRG, no same-access positive route, and no dequantization/sampling theorem, BQP separation, or quantum advantage claim. T-B5-004 adds a two-site finite-DMRG-style pressure prototype that beats one-site ALS on 4 rows but still beats seeded MPS on 0 rows. T-B10-013 adds an optimistic bounded-density response-sampler cost stress on the same 9 B5/B10 rows: min/median/max shots to match exact-state-seeded MPS pressure are 3.861e9 / 7.645e12 / 2.849e29, 0 rows beat explicit D5 matvec ops by shots, and no sampling oracle, same-access positive route, quantum advantage, or BQP separation is claimed. B10-T2 still has the trained-spoofer/proof-gate/transcript/device-noise/Qiskit-Aer/backend-calibrated-style bridge stack. | T-B10-014 must replace the sampler-cost negative boundary with canonical-environment production DMRG/MPS for the same B5 response rows, or supply a real same-access response oracle with preparation, mixing, variance, and confidence costs; separately, replace the GenericBackendV2 bridge with real backend properties or hardware verifier execution. | Keep B10-T1 negative unless a same-access sampler or production DMRG/quantum response comparison beats the full denominator ladder without hidden access advantages. |

## Manuscript Bets

1. **Technical lead: certified hardware-aware circuit compression.**
   B1 is currently the strongest candidate because it has replayable proof logs,
   local semantic checks, exact small-circuit validation, and a measurable
   hardware-exposure improvement.
2. **Systems extension: cross-layer FT resource reduction.** B7 now has a first B1/B2 dependency-schedule bridge, but it
   becomes credible only if that bridge survives real workload DAGs,
   factory-throughput scheduling, and physical layout assumptions.
3. **Verification technical track: B4 plus B8.** B8 now has an adaptive
   leakage boundary: low/mid leakage is rejected, but 75% leakage becomes
   dangerous. This should feed directly into B4 trap refresh and hidden
   challenge design.
4. **Theory note: B9 plus B10.** The near-term output is likely a restricted
   theorem target package or negative-result database, not a grand complexity
   separation. B10 now has two formal targets and one restricted B10-T1
   accounting lemma plus numerical, correlated, and FCI denominator tables; the next
   step is accuracy-per-resource proof pressure.

## Next 30 Days

| Week | Focus |
|---:|---|
| 1 | Freeze B1 proof-log report outline; B2 reduced-round is closed and T-B2-005 has a false-positive stress boundary, so convert it into a shot-conditioned erasure decoder or calibrated leakage model; pair B4 and B8 into one verification lane. |
| 2 | Run B1 on a broader benchmark family or document the scalable-verifier block; upgrade the B7 dependency bridge to a real workload DAG; source-back B10-T1 or start B10-T2 proof pressure. |
| 3 | Keep B3 demoted unless a rescue mechanism appears; advance B5 from prototype MPS/ALS and two-site finite-DMRG-style pressure tests to mature variational DMRG/MPS evidence or quantum response-kernel cost accounting; advance B6 from formula-derived proxy boundary to crystallographic/DFT/B5-computed descriptors plus expanded post-2008 negatives. |
| 4 | Run monthly keep/merge/kill review; select 2-3 directions for deeper technical validation; replace weak directions only if a Tier 2 candidate has a clearer validation path. |

## Immediate Recommendation

Lead with **B1**, not because the other nine are unimportant, but because B1
already has the strongest chain from method to measurement to verification.
Use B7 and B2 to turn it into a system-level claim, while B4/B8 and B9/B10
continue as protocol and theory tracks.
