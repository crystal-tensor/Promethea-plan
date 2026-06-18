# B7 w8_21 Claim-Boundary Paper Fragment v0.1

Last updated: 2026-06-17

Status: **claim_boundary_fragment_not_minimality_theorem**

## Candidate Subsection Title

Repeated synthesis templates are not physical resource savings without
occurrence-removing certificates.

## Context

The B7 fault-tolerant resource ledger for `gcm_h6` is dominated by
occurrence-based arbitrary rotations after the B1 passes.  A nonlocal repeated
template scan identified `w8_21`, an 8-operation two-qubit block that appears in
20 non-overlapping occurrences and covers 100 physical arbitrary-rotation
occurrences.  If each occurrence could be replaced by an exactly equivalent
block with four arbitrary rotations instead of five, the current ledger would
remove 20 arbitrary rotations, or 400 proxy T units.

The tempting claim is therefore:

> repeated nonlocal templates imply reusable synthesis savings in the
> fault-tolerant ledger.

The experiments below reject that claim for the tested `w8_21` families.

## Evidence

| Search family | Scope | Optimizer runs | Exact candidates | Best residual | Ledger removal |
|---|---:|---:|---:|---:|---:|
| Same-skeleton one fixed angle | 55 fixed-angle attempts | 880 | 0 | 0.03936333737388844 | 0 |
| Two-CNOT broad Rz/Ry skeleton | 15360/15360 families | 30720 | 0 | 0.24437773599006635 | 0 |
| Two-CNOT Euler-local target-informed | 500/500 families | 3000 | 0 | 0.24437773599006604 | 0 |
| Three-CNOT target-informed | 1480/1480 families | 8880 | 0 | 1.0352761804100845 | 0 |

The four searches execute **43480** optimizer runs and find **0** exact
four-arbitrary-angle replacements.  The B7 ledger therefore keeps:

- `w8_21` arbitrary rotations removed: **0**;
- `w8_21` proxy T ledger removed: **0**;
- `gcm_h6` arbitrary rotation occurrences after B1 passes: **270**;
- `gcm_h6` FT ledger after B1 passes: **6224**;
- portfolio min STV under the FT synthesis ledger: **1.086007702182285**.

## Claim-Separation Statement

This result separates three distinct claims:

1. `gcm_h6` contains repeated nonlocal circuit templates.
2. Repeated templates can reduce the classical catalog of synthesis subproblems.
3. Repeated templates reduce physical fault-tolerant resource counts.

The evidence supports claims 1 and 2 for the scanned templates, but it does not
support claim 3 for `w8_21`.  In the current ledger, repeated-template discovery
is not a physical resource reduction unless an exact occurrence-removing rewrite
is emitted and verified.

## Formal Claim Boundary

The strongest supported statement is:

> In the tested same-skeleton, exhaustive two-CNOT Rz/Ry, target-informed
> two-CNOT Euler-local, and bounded target-informed three-CNOT families, no
> exact four-arbitrary-angle replacement for `w8_21` was found at 1e-8
> tolerance.  Therefore the B7 occurrence-based FT ledger must count zero
> resource reduction from `w8_21` until a certified rewrite is produced.

The statement is deliberately not:

> `w8_21` is globally minimal, or no exact four-arbitrary-angle representation
> exists in any two-qubit circuit model.

## What Would Upgrade This Result

This boundary can be strengthened by any of the following:

- a symbolic KAK or algebraic minimality proof for the exact `w8_21` block;
- an exhaustive Clifford-scaffold enumeration with certified exact arithmetic;
- a verified exact rewrite that removes at least one arbitrary rotation per
  occurrence and passes the 20-occurrence B7 proof/Aer/resource checks;
- a lower-bound proof that includes ancilla-free higher-CNOT decompositions;
- an approximate rewrite whose synthesis-error budget and logical-failure
  contribution are explicitly propagated into the B7 STV ledger.

## Reproducibility Pointers

- `research/B7_nonlocal_template_block_scan.md`
- `research/B7_w8_21_small_block_synthesis.md`
- `research/B7_w8_21_broad_skeleton_search.md`
- `research/B7_w8_21_euler_local_search.md`
- `research/B7_w8_21_three_cnot_search.md`
- `research/B7_w8_21_scoped_minimality_note.md`
- `results/B7_w8_21_small_block_synthesis_v0.json`
- `results/B7_w8_21_broad_skeleton_search_v0.json`
- `results/B7_w8_21_euler_local_search_v0.json`
- `results/B7_w8_21_three_cnot_search_v0.json`

## Recommended Use In The Portfolio

Use this as the closing artifact for `T-B7-009`.  It is a useful negative result
for B1/B7 co-design because it prevents an unsupported 400-proxy-T resource
claim and gives the next agents a precise rule: do not count repeated-template
savings unless the rewrite certificate removes physical occurrences.
