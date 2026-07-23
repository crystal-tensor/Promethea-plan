# B9 Scale-Cancellation Formalization Gate

- Method: `b9_scale_cancellation_formalization_gate_v0`
- Status: `scale_cancellation_formalization_checked_not_quantum_pcp_proof`
- Requirements passed/failed: `10` / `0`
- Fresh Lean/Lake commands returning zero: `3/3`
- Source SHA256: `553a66f87f721051aaf224e82ead9a279289e1b0a8d2a37227bfd3aecd90642b`
- Transcript SHA256: `fc2ca026c6da126c73d91ba4180106b2b3abf5af5d104e6ecdca9996501ea3f6`

## Supported Result

For real gap, width, and nonzero scale parameters, Lean checks cancellation of uniform scaling in the normalized-gap ratio, and checks that the project scale 27/20 is nonzero.

## Claim Boundary

This does not formalize the all-n Hamiltonian construction, locality over the construction, a Quantum PCP theorem, an NLTS theorem, a global gap-amplification impossibility theorem, or B10 complexity separation.

- R1 [PASS]: Lean/Lake version probes return zero
- R2 [PASS]: The B9 module returns zero under lake env lean
- R3 [PASS]: The source declares normalized_gap_scale_cancel
- R4 [PASS]: The cancellation theorem requires a nonzero scale
- R5 [PASS]: The cancellation proof does not inject hRatio
- R6 [PASS]: The new normalized-gap theorem consumes the cancellation lemma
- R7 [PASS]: The concrete 27/20 scale is checked as nonzero
- R8 [PASS]: Fresh transcript has three command records and no warnings
- R9 [PASS]: The transcript binds the current source hash
- R10 [PASS]: Forbidden B9/B10 claims remain false
