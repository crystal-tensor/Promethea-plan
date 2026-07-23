# B9 Spectral-Width Formalization Gate

- Method: `b9_spectral_width_formalization_gate_v0`
- Status: `spectral_width_formalization_checked_not_quantum_pcp_proof`
- Requirements passed/failed: `10` / `0`
- Fresh Lean/Lake commands returning zero: `3/3`
- Source SHA256: `662897b37c77726bcac0810f071449b3683a7b2aa4968221f9ff1057d88ff85c`
- Transcript SHA256: `fcea4574a65c527dae71b1974ee8f3999a5e1a08369590d5a9b791a40649db5a`

## Supported Result

Lean checks spectral-width ratio cancellation for a nonzero uniform real scale and checks a concrete UniformScaleFactor wrapper.

## Claim Boundary

This does not prove the all-n Hamiltonian construction, locality, a Quantum PCP theorem, an NLTS theorem, a global gap-amplification impossibility theorem, or a BQP separation.

- R1 [PASS]: Lean/Lake probes return zero
- R2 [PASS]: The B9 module returns zero
- R3 [PASS]: The spectral-width cancellation theorem exists
- R4 [PASS]: The theorem requires a nonzero scale
- R5 [PASS]: The theorem delegates to normalized-gap cancellation
- R6 [PASS]: The new interface has no injected hRatio
- R7 [PASS]: The generic uniform-scale spectral-width interface exists
- R8 [PASS]: The concrete 27/20 wrapper exists
- R9 [PASS]: Transcript has three records, no warnings, and binds source hash
- R10 [PASS]: Formal-complexity claims remain explicitly out of scope
