# B7 w8_21 Scoped Minimality Note v0.1

Last updated: 2026-06-16

Status: **scoped_minimality_note_not_global_lower_bound**

## Question

The B7 `gcm_h6` fault-tolerant ledger is blocked by repeated arbitrary
numeric rotations.  The nonlocal template scan found that template `w8_21`
covers 20 non-overlapping occurrences and 100 physical arbitrary-rotation
occurrences.  If each occurrence could be replaced by an exactly equivalent
block with four arbitrary rotations instead of five, the ledger would remove
20 arbitrary rotations, or 400 proxy T units under the current accounting.

This note asks a deliberately scoped question:

Can the repeated `w8_21` block be certified as an exact four-arbitrary-angle
replacement inside the tested two-qubit circuit families?

## Evidence Summary

| Search | Family exhausted | Optimizer runs | Passing exact candidates | Best residual | Claim boundary |
|---|---:|---:|---:|---:|---|
| Same-skeleton one fixed angle | 55 fixed-angle attempts | 880 | 0 | 0.03936333737388844 | Same two-CNOT skeleton only; local finite-difference rank is 5. |
| Two-CNOT broad skeleton | 15360/15360 families | 30720 | 0 | 0.24437773599006635 | Length-6 two-CNOT/four-Rz/Ry skeletons only. |
| Two-CNOT Euler-local target-informed | 500/500 families | 3000 | 0 | 0.24437773599006604 | Target-informed local Euler layers with source pi scaffold. |
| Three-CNOT target-informed | 1480/1480 families | 8880 | 0 | 1.0352761804100845 | Target-informed local Euler layers with one extra CNOT and source pi scaffold. |

Total checked optimizer runs across the four searches: **43480**.

## Interpretation

The tested evidence does not support a B7 resource reduction from `w8_21`.
Within the searched families, no exact replacement was found that reduces the
arbitrary-angle count from five to four per occurrence.

This is a useful negative result because it prevents the project from counting
400 proxy T units of savings without an emitted and verified rewrite.  It also
separates three ideas that can otherwise be conflated:

- Repeated templates exist in `gcm_h6`.
- Repeated templates can reduce classical synthesis catalog size.
- Repeated templates do not automatically reduce physical occurrence-based
  fault-tolerant rotation injections.

## What This Does Not Prove

This note is not a global KAK minimality theorem.  It does not rule out:

- arbitrary Clifford scaffolds beyond the tested pi scaffolds;
- all possible three-CNOT or higher-CNOT decompositions;
- ancilla-assisted or measurement-assisted rewrites;
- approximate rewrites with explicit synthesis-error budgets;
- symbolic identities outside the searched Rz/Ry Euler parameterizations.

## Claim Boundary for B7

Until an exact rewrite is emitted and verified against all 20 non-overlapping
`w8_21` occurrences, the B7 FT ledger must keep:

- `w8_21` arbitrary rotations removed: **0**;
- `w8_21` proxy T ledger removed: **0**;
- `gcm_h6` occurrence-based arbitrary rotation count after B1 passes: **270**;
- `gcm_h6` FT ledger after B1 passes: **6224**;
- portfolio min STV under the FT synthesis ledger: **1.086007702182285**.

## Publication Use

This can become a negative-result subsection in a systems paper:

**"Repeated synthesis templates are not physical savings unless an exact
occurrence-removing rewrite is certified."**

The publishable contribution is not that `w8_21` is globally minimal.  The
contribution is an auditable claim-separation method:

1. find repeated nonlocal templates;
2. quantify the hypothetical ledger savings;
3. test exact replacement families;
4. block resource claims when no rewrite certificate exists.

## Source Artifacts

- `research/B7_nonlocal_template_block_scan.md`
- `research/B7_w8_21_small_block_synthesis.md`
- `research/B7_w8_21_broad_skeleton_search.md`
- `research/B7_w8_21_euler_local_search.md`
- `research/B7_w8_21_three_cnot_search.md`
- `results/b7_w8_21_small_block_synthesis/proofs.jsonl`
- `results/b7_w8_21_broad_skeleton_search/proofs.jsonl`
- `results/b7_w8_21_euler_local_search/proofs.jsonl`
- `results/b7_w8_21_three_cnot_search/proofs.jsonl`

