# B9 Pauli Action Composition Gate

- Method: `b9_pauli_action_composition_gate_v0`
- Status: `pauli_action_composition_checked_not_linear_or_spectral_proof`
- Requirements passed/failed: `11` / `0`
- Fresh Lean/Lake commands returning zero: `3/3`
- Source SHA256: `28776e0088a0461045d953c1f66012029dd550bfbad147fb10916deb7b919418`
- Transcript SHA256: `299a727ca77041e61a57dc8ec0f1da9bde5006df0e54123b658ac59e59b05660`

## Supported Result

Lean checks that a Pauli basis action can be split into two factor lists, replayed sequentially, and recombined with the same phase and final basis state; the resulting action remains local outside the concatenated site support.

## Claim Boundary

This is still a computational-basis action model, not a complex linear operator, Hamiltonian sum, Hermiticity proof, spectral theorem, Quantum PCP/NLTS theorem, global impossibility result, BQP separation, or quantum-advantage claim.

- R1 [PASS]: Lean and Lake version probes return zero
- R2 [PASS]: All three B9 modules compile together
- R3 [PASS]: Basis actions have an explicit composition operation
- R4 [PASS]: Phase composition is associative
- R5 [PASS]: Action composition is associative
- R6 [PASS]: The phase-plus identity preserves an action result
- R7 [PASS]: A single Pauli factor is exposed as a composed action
- R8 [PASS]: Appending Pauli factors replays as left action then right action
- R9 [PASS]: Appending actions preserves locality outside concatenated support
- R10 [PASS]: Fresh transcript binds all source hashes
- R11 [PASS]: The checked module contains no matrix or complex-amplitude machinery
