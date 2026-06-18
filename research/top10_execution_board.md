# Top 10 Execution Board v0.1

Last updated: 2026-06-17

Purpose: turn the Top 10 quantum attack directions from initialized v0
artifacts into a one-year execution portfolio with decision gates. This file
does not claim that any hard problem is solved. It defines what each direction
must prove next, when to merge directions, and when to demote weak paths.

Machine-readable source: `top10_execution_board.json`
Detailed problem dossiers: `top10_problem_dossiers.md`
Machine-readable dossier source: `top10_problem_dossiers.json`

## Portfolio State

Current state: **stage 1g evidence hardening; B10-T2 backend-calibrated-style GenericBackendV2 verifier bridge is complete, and the next verification bridge is real backend properties or hardware randomized-measurement execution**.

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
| B2 | Low-overhead QEC | Stim baseline plus same-hardware reduced-round candidate and artifact boundary: 120 configs / 360k shots found 22 volume-improved rows; 240 configs / 1.2M-shot robustness preserved 88 improved rows; all original and stress-preserved improved rows are aggressive, distance-3, one-round candidates with 0 non-aggressive rows | Start a genuinely different B2 mechanism that can produce distance-5/7 Wilson target-volume reductions under noise mismatch without relying on aggressive one-round d=3 schedules. | Demote any candidate that only reproduces the closed distance-3 aggressive reduced-round artifact. |
| B3 | Molecular reaction dynamics | T-B3-011 cross-molecule UCC/ADAPT pressure/demotion boundary: H2/LiH/H2O/N2 bounded high-coefficient sampled covariance pressure has 35 sampled groups total, 384 shots/group, mean/max variance error 0.0833/0.5029, max optimizer-loop shots lower bound 475,043,013,690,000, max optimizer-loop 2Q lower bound 281,225,464,104,480,000, and denominator wins remain 0. | Keep B3 as a negative-boundary track unless a rescue-only T-B3-012 produces real multi-parameter UCCSD/ADAPT covariance or stronger-than-QWC measurement that beats selected-CI/DMRG/tensor denominators after optimizer-loop accounting. | Demote current one-parameter UCC/ADAPT + QWC route; do not spend more B3 effort without a concrete rescue mechanism. |
| B4 | Verifiable quantum advantage | Toy hidden-trap protocol plus shared B4/B8 CNOT hidden-projection refresh proxy: 192 configs, honest completeness 1.0, no-refresh high-leakage soundness 0.675, repaired high-leakage soundness 0.0 | Upgrade the CNOT/projection proxy to hardware-executable randomized measurement circuits or attack it with trained/generative spoofers. | Merge into B8 if circuit-level hardness remains absent beyond property-testing proxies. |
| B5 | Strongly correlated matter | Small exact Hubbard reference plus cluster proxy; T-B5-001 B10-linked oracle-tuned denominator; T-B5-002 non-oracle response embedding denominator with mean/max error 0.05098/0.12308; T-B5-003a exact-state-seeded MPS/Schmidt pressure reference with mean/max error 0.000442/0.001695; T-B5-003b non-exact-state-seeded variational MPS/ALS prototype with bond dimensions 2/4, 3 restarts x 8 sweeps, mean/max error 0.01806/0.03907, min overlap 0.9626, and 0 rows beating the seeded MPS reference. | Replace the MPS/ALS prototype with mature canonical-environment variational DMRG/MPS, or compare a candidate quantum impurity/response kernel after full state-preparation, measurement, optimizer-loop, and classical denominator costs. | Demote if the benchmark remains 1D-only with prototype tensor references and no deployable DMRG/MPS baseline or quantum response-kernel costed comparison. |
| B6 | High-temperature superconductivity search | Toy descriptor ranking | Connect descriptors to a real materials table or curated retrospective dataset and separate family-prior leakage from physics signal. | Demote if rankings are driven by hand-authored family priors. |
| B7 | Fault-tolerance co-design | B1/B2 bridge plus FT synthesis ledger; `w8_21` claim-boundary closure with 43480 optimizer runs, 0 exact replacements, and 0 ledger removal | Improve the B7 minimum row through B1 T-resource work, or produce a symbolic KAK/Clifford-scaffold proof / alternate occurrence-removing rewrite for `gcm_h6`. | Demote if B1/B2-linked reductions collapse once physical layout, factory throughput, feed-forward, and occurrence-level synthesis certificates are explicit. |
| B8 | Classical verification of quantum outputs | Hidden-invariant test, adaptive leakage boundary, B4/B8 circuit-refresh proxy, trained/generative spoofer stress, B10-T2 proof gate, restricted lemma, transcript/device-noise bridge, ideal Qiskit/Aer verifier bridge, noisy Aer bridge, and backend-calibrated-style GenericBackendV2 bridge: 5760 target-property-derived noisy circuits, safe calibrated honest acceptance 1.0, adversary acceptance 0.25, inherited transcript safe soundness 0.0208 | Replace GenericBackendV2 snapshots with real backend properties or hardware randomized-measurement verifier execution. | Demote if hidden invariants remain too easy to infer once challenge refresh and adaptive generative spoofers are added. |
| B9 | Quantum PCP / Local Hamiltonian hardness | Exact small-instance gap lab plus finite-instance failed gap-amplification negative lemma, Lean-style symbolic skeleton, and named-family cluster-stabilizer width/locality skeleton: n=4,5,6 all terms scale by 1.35, max locality stays 3, raw gap amplifies, normalized gap is invariant, and the certificate is rejected | Create a real Lean/mathlib or equivalent proof-checkable project and formalize support-size, uniform-scaling, spectral-width, and normalized-gap invariance lemmas for all n >= 4. | Keep only as a negative-result track unless a restricted theorem target becomes precise. |
| B10 | Boundary of BQP | Reduction graph plus 2 formal targets; B10-T1 explicit-I/O boundary stack now includes B3 through T-B3-011 cross-molecule pressure/demotion boundary and B5 through the 9-instance D5 Hubbard table, oracle-tuned and non-oracle response embedding denominators, exact-state-seeded MPS/Schmidt pressure reference, and non-exact-state-seeded variational MPS/ALS prototype; B10-T2 now has a trained-spoofer boundary, proof gate, restricted lemma, transcript/device-noise bridge, ideal Qiskit/Aer verifier bridge, noisy Aer verifier bridge, and backend-calibrated-style GenericBackendV2 verifier bridge | Replace the B5 MPS/ALS prototype with real variational DMRG/MPS evidence, compare a real B5 quantum response subroutine against D5, turn B3's demotion into a denominator/dequantization note, or replace the B10-T2 GenericBackendV2 bridge with real backend properties/hardware verifier execution. | Demote if formal targets do not produce source-backed theorem notes, negative lemmas, or useful failed-proof records. |

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
| 1 | Freeze B1 proof-log report outline; B2 reduced-round is now closed as an aggressive small-distance artifact boundary, so start a different B2 mechanism; pair B4 and B8 into one verification lane. |
| 2 | Run B1 on a broader benchmark family or document the scalable-verifier block; upgrade the B7 dependency bridge to a real workload DAG; source-back B10-T1 or start B10-T2 proof pressure. |
| 3 | Keep B3 demoted unless a rescue mechanism appears; advance B5 from MPS/ALS prototype to mature variational DMRG/MPS evidence or quantum response-kernel cost accounting; connect B6 to a real or curated materials table. |
| 4 | Run monthly keep/merge/kill review; select 2-3 directions for deeper technical validation; replace weak directions only if a Tier 2 candidate has a clearer validation path. |

## Immediate Recommendation

Lead with **B1**, not because the other nine are unimportant, but because B1
already has the strongest chain from method to measurement to verification.
Use B7 and B2 to turn it into a system-level claim, while B4/B8 and B9/B10
continue as protocol and theory tracks.
