# B9 Term-Level Disjoint Pauli Action Commutation Gate

- Method: `b9_pauli_action_term_disjoint_commutation_gate_v0`
- Status: `pauli_action_term_disjoint_commutation_checked_not_linear_or_spectral_proof`
- Requirements passed/failed: `12` / `0`
- Fresh Lean/Lake commands returning zero: `3/3`
- Source SHA256: `131c96bf6f204bd861f52cacd1574cab8a6f0c0920e06905e0592aaee00bf1f6`
- Transcript SHA256: `3377ac96cee163a86c1a8c20f9427746723c1ce8130305426024a59bab00c567`

## Supported Result

Lean checks that two Pauli terms with disjoint site supports commute under the restricted computational-basis replay, including final basis state and accumulated phase.

## Claim Boundary

This is still a finite computational-basis action model, not a complex linear operator, Hamiltonian sum, Hermiticity proof, spectral theorem, Quantum PCP/NLTS theorem, global impossibility result, BQP separation, or quantum-advantage claim.

- R1 [PASS]: Lean and Lake version probes return zero
- R2 [PASS]: All five B9 modules compile together
- R3 [PASS]: The source defines a factor-to-term disjointness predicate
- R4 [PASS]: A factor commutes with an entire disjoint term
- R5 [PASS]: The theorem reuses the prior factor-level commutation proof
- R6 [PASS]: The theorem reuses compositional replay associativity
- R7 [PASS]: The source proves whole-term disjoint replay commutation
- R8 [PASS]: The term theorem quantifies over both site supports
- R9 [PASS]: The checked module contains no matrix or complex-amplitude machinery
- R10 [PASS]: Fresh transcript binds every source and project hash
- R11 [PASS]: The proof is finite replay semantics rather than a spectral theorem
- R12 [PASS]: The source does not claim BQP or Quantum PCP resolution
