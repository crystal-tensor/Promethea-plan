# B9 Cluster-Stabilizer Parametric Certificate

Status: `parametric_certificate_checked_by_local_verifier_not_formal_theorem`

This artifact is a local executable verifier for one narrow B9 statement. It checks the open-chain cluster-stabilizer toy family used by the local Hamiltonian lab and confirms that uniform reweighting by `27/20` preserves locality and normalized gap at the formula level for the declared family.

It is stronger than the previous informal skeleton because the formulas, finite source rows, and claim boundary are checked by a repo-local script. It is still not a Lean/mathlib theorem, not a Quantum PCP proof, and not a global no-go theorem.

## Checked Formula

- Family: `cluster_stabilizer_open_uniform_reweight`
- Domain: integer `n >= 4`
- Term count: `n`
- Interior terms: `n-2`
- Boundary terms: `2`
- Support sizes: `{2, 3}`
- Maximum locality: `3`
- Uniform scale: `27/20`
- Hamiltonian identity: `H'_n = (27/20) H_n`
- Normalized gap identity: `(s*g)/(s*w) = g/w`, for `s = 27/20` and `w > 0`

## Finite Source Rows Checked

| n | term count | supports | max locality | normalized gap invariant | checked |
|---:|---:|---|---:|---|---|
| 4 | 4 | [2, 3] | 3 | True | True |
| 5 | 5 | [2, 3] | 3 | True | True |
| 6 | 6 | [2, 3] | 3 | True | True |

## Claim Boundary

- Local verifier checked: `true`
- Proof assistant checked: `false`
- Formal theorem proved: `false`
- Quantum PCP proof claimed: `false`
- Global gap-amplification impossibility claimed: `false`
- NLTS theorem claimed: `false`

## Result

The certificate is intentionally rejected as a raw-gap-only certificate: positive uniform rescaling changes raw gap and width by the same factor, so the normalized gap is invariant. This makes it useful as a checked negative guardrail for B9, not as a solved frontier claim.

Validation error count: `0`
