# B9 Pauli Basis Action Gate

- Method: `b9_pauli_basis_action_gate_v0`
- Status: `pauli_basis_action_checked_not_matrix_or_spectral_proof`
- Requirements passed/failed: `10` / `0`
- Fresh Lean/Lake commands returning zero: `3/3`
- Basis domain: `Fin n -> Bool`
- Phase alphabet: `['plus', 'minus']`
- Source SHA256: `2109f0e916408e00c9d3d7916d8f2638cebaef4a31ae77b8d36b5afa4c23c1c0`
- Transcript SHA256: `a05099ef02806991d9092a7a705dda9cadae6ddb845437368cc475afae182c9a`

## Supported Result

Lean checks a total recursive action of Pauli-labelled terms on computational-basis bitstrings: X flips its site, Z preserves the bitstring while recording a sign phase, and the final state agrees with the input outside the finite factor site support.

## Claim Boundary

This is a computational-basis action model, not a complex matrix, linear operator, Hamiltonian sum, Hermiticity proof, spectral theorem, Quantum PCP/NLTS theorem, global impossibility result, or BQP separation.

- R1 [PASS]: Lean and Lake version probes return zero
- R2 [PASS]: WidthLocality and PauliBasisAction compile together
- R3 [PASS]: BasisState is a Fin n computational basis
- R4 [PASS]: Phase has plus/minus and bit interpretation
- R5 [PASS]: X flips one site
- R6 [PASS]: Z records a basis-bit phase and preserves the state
- R7 [PASS]: Pauli terms have recursive basis action
- R8 [PASS]: Single-factor action is local
- R9 [PASS]: Term action preserves basis bits outside its site support
- R10 [PASS]: Action is total and transcript is fresh
