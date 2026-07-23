# B9 Pauli-Term Family Gate

- Method: `b9_pauli_term_family_gate_v0`
- Status: `pauli_term_family_checked_not_hamiltonian_spectral_proof`
- Requirements passed/failed: `10` / `0`
- Fresh Lean/Lake commands returning zero: `3/3`
- Index domain: `Fin n`
- Factor alphabet: `['X', 'Z']`
- Source SHA256: `0b93b31c11fd62dd44f30fe5de3aa9a27b40ee16befb0c6c1617d62e8ce26e9c`
- Transcript SHA256: `15a0aecf748975bc00a3b09a603985c2e5834e74bb7cb90d26f63055c7e233ca`

## Supported Result

Lean checks an all-n Fin n-indexed family of Pauli-labelled term descriptors: interior terms carry explicit Z-X-Z factors, boundaries carry two factors, factor-list locality matches the source ClusterTerm locality, and the family is total with support at most 3.

## Claim Boundary

The descriptors are not yet matrices or an operator algebra. This does not define a Hamiltonian sum, prove Hermiticity or spectrum, prove Quantum PCP or NLTS, prove a global impossibility result, or establish BQP separation.

- R1 [PASS]: Lean/Lake version probes return zero
- R2 [PASS]: The B9 module returns zero
- R3 [PASS]: PauliAxis exposes X and Z labels
- R4 [PASS]: PauliFactor carries a Fin n site
- R5 [PASS]: PauliTerm carries an explicit factor list
- R6 [PASS]: ClusterTerm maps to explicit Z-X-Z or boundary factors
- R7 [PASS]: The operator term locality equals source term locality
- R8 [PASS]: HamiltonianTermFamily is Fin n-indexed
- R9 [PASS]: The canonical operator family has support and max-locality theorems
- R10 [PASS]: The operator family is total and the transcript is fresh
