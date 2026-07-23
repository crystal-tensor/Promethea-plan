# B9 All-n Term-Family Locality Gate

- Method: `b9_term_family_locality_gate_v0`
- Status: `term_family_locality_checked_not_hamiltonian_spectral_proof`
- Requirements passed/failed: `10` / `0`
- Fresh Lean/Lake commands returning zero: `3/3`
- Index domain: `Fin n`
- Minimum n: `2`
- Source SHA256: `2ef4ffbfa6f94ae76ef55445a1e200fcd0b6368c2f72fe46304f5884fef9df51`
- Transcript SHA256: `83942fa83b93d122f2797da0822be0374c5f38187d2857d7f1104975de9a48aa`

## Supported Result

For every n >= 2, Lean checks a canonical Fin n-indexed family whose terms are explicitly boundary or interior constructors, every term has locality in {2,3}, every term has locality at most 3, and the family is total over its index domain.

## Claim Boundary

This does not define Pauli operators or prove a Hamiltonian term sum, its spectrum, a Quantum PCP theorem, an NLTS theorem, a global gap-amplification impossibility result, or a BQP separation.

- R1 [PASS]: Lean/Lake version probes return zero
- R2 [PASS]: The B9 module returns zero
- R3 [PASS]: ClusterTerm.at is an indexed construction
- R4 [PASS]: The left boundary branch is explicit
- R5 [PASS]: The right boundary branch is explicit
- R6 [PASS]: The interior branch carries both arithmetic bounds
- R7 [PASS]: ClusterTermFamily is total over Fin n
- R8 [PASS]: The canonical family is defined for every n >= 2
- R9 [PASS]: The canonical family has checked support and max-locality theorems
- R10 [PASS]: The family is total and the transcript is fresh
