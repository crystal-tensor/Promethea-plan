# B9 Disjoint Pauli Action Commutation Gate

- Method: `b9_pauli_action_disjoint_commutation_gate_v0`
- Status: `pauli_action_disjoint_commutation_checked_not_linear_or_spectral_proof`
- Requirements passed/failed: `11` / `0`
- Fresh Lean/Lake commands returning zero: `3/3`
- Source SHA256: `2d669fd4689944ef7c8cf4f88887c946d0f326c8b026883c956816ffc7ea8469`
- Transcript SHA256: `da02a3d3005e28b0c5834899449475938d830e6a73bb8b06ebfa8c2cb6ee0c65`

## Supported Result

Lean checks that two Pauli factors on distinct Fin n sites commute under the restricted computational-basis replay, with matching final basis state and phase projections.

## Claim Boundary

This is still a factor-level computational-basis action model, not a complex linear operator, Hamiltonian sum, Hermiticity proof, spectral theorem, Quantum PCP/NLTS theorem, global impossibility result, BQP separation, or quantum-advantage claim.

- R1 [PASS]: Lean and Lake version probes return zero
- R2 [PASS]: All four B9 modules compile together
- R3 [PASS]: The helper proves double flips commute at distinct sites
- R4 [PASS]: The phase alphabet has a checked commutative multiplication lemma
- R5 [PASS]: Disjoint Pauli factor actions commute as composed actions
- R6 [PASS]: The state projection of disjoint replay is order independent
- R7 [PASS]: The phase projection of disjoint replay is order independent
- R8 [PASS]: The proof imports the prior compositional replay contract
- R9 [PASS]: The checked module contains no matrix or complex-amplitude machinery
- R10 [PASS]: Fresh transcript binds all source and project hashes
- R11 [PASS]: The source keeps the restricted proof boundary explicit
