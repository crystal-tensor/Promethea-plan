# B9 Failed Gap-Amplification Negative Lemma v0.1

Last updated: 2026-06-17

Status: **finite_instance_negative_gap_amplification_lemma_not_quantum_pcp_proof**

## Finite-Instance Lemma

**Name:** `raw_gap_amplification_is_not_a_local_normalized_gap_amplification_certificate`

In the B9 v0 exact small-instance screen, a transformation is not accepted as a gap-amplification proof step merely because the raw spectral gap increases. It must also preserve locality, maintain the tracked ground-space overlap, and improve the normalized gap. The tested locality-preserving reweighting family has zero accepted rows; several rows increase raw gap while failing normalized-gap improvement.

This is a finite exact-diagonalization negative lemma for the current B9 v0 screen. It is useful because it prevents a common overclaim: raw spectral-gap growth alone is not a local-Hamiltonian gap-amplification certificate.

## Summary

- Source method: small_local_hamiltonian_gap_lab_v0
- Configurations: 18
- Locality-preserving candidates: 9
- Local candidate passes: 0
- Strict counterexamples: 4
- Tolerance counterexamples: 5
- Dense locality traps: 9
- Max local normalized-gap ratio: 1.000000000000002
- Max dense-filter raw gap ratio: 2.4142428682853314
- Explicitly not Quantum PCP proof: True
- Global impossibility claimed: False
- Proof assistant formalized: False
- Validation errors: 0

## Strict Counterexamples

| case | locality | gap ratio | normalized-gap ratio | overlap | accepted |
|---|---:|---:|---:|---:|---:|
| xxz_chain:4q:local_interaction_reweight_v0 | 2 | 1.252100 | 0.936769 | 0.993182 | False |
| xxz_chain:6q:local_interaction_reweight_v0 | 2 | 1.138104 | 0.853822 | 0.988374 | False |
| cluster_stabilizer_open:4q:local_interaction_reweight_v0 | 3 | 1.350000 | 1.000000 | 1.000000 | False |
| cluster_stabilizer_open:5q:local_interaction_reweight_v0 | 3 | 1.350000 | 1.000000 | 1.000000 | False |

## Dense Locality Traps

| case | locality | gap ratio | normalized-gap ratio | overlap |
|---|---:|---:|---:|---:|
| transverse_ising_frustrated:4q:shifted_square_spectral_filter_v0 | 4 | 1.129560 | 0.203507 | 1.000000 |
| transverse_ising_frustrated:5q:shifted_square_spectral_filter_v0 | 5 | 1.092379 | 0.164256 | 1.000000 |
| transverse_ising_frustrated:6q:shifted_square_spectral_filter_v0 | 6 | 1.056659 | 0.130842 | 1.000000 |
| xxz_chain:4q:shifted_square_spectral_filter_v0 | 4 | 2.414243 | 0.352988 | 1.000000 |
| xxz_chain:5q:shifted_square_spectral_filter_v0 | 5 | 1.630660 | 0.189090 | 1.000000 |
| xxz_chain:6q:shifted_square_spectral_filter_v0 | 6 | 2.271121 | 0.219607 | 1.000000 |
| cluster_stabilizer_open:4q:shifted_square_spectral_filter_v0 | 4 | 1.910000 | 0.339858 | 1.000000 |
| cluster_stabilizer_open:5q:shifted_square_spectral_filter_v0 | 5 | 1.910000 | 0.272080 | 1.000000 |
| cluster_stabilizer_open:6q:shifted_square_spectral_filter_v0 | 6 | 1.910000 | 0.226841 | 1.000000 |

## Proof Obligations

- Replace finite exact-diagonalization evidence with a symbolic statement over a named Hamiltonian family.
- Track spectral-width growth analytically, not only raw spectral gap.
- Prove locality preservation term-by-term after any transformation.
- Bound ground-space perturbation or specify the acceptable promise gap model.
- Separate dense spectral filters from local Hamiltonian transformations before invoking PCP-style intuition.

## Claim Boundary

- Supported: a reusable finite-instance failed-proof record for naive gap amplification in the B9 v0 screen.
- Not supported: a Quantum PCP proof, an NLTS theorem, a local-Hamiltonian hardness theorem, or a global impossibility theorem for gap amplification.

## Limits

- Finite-instance negative lemma only; it covers the v0 model/transform screen and not all gap-amplification strategies.
- The local reweighting family is a toy probe, not a complete family of locality-preserving transformations.
- Dense shifted-square filters are recorded as locality traps, not as valid local-Hamiltonian proof steps.
- No Quantum PCP theorem, NLTS theorem, or global no-go theorem is claimed.
