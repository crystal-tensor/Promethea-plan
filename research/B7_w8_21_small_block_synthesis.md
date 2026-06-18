# B7 w8_21 Exact Small-Block Synthesis v0.1

Last updated: 2026-06-15

Status: **w8_21_small_block_synthesis_negative_boundary_not_physical_layout**

## Summary

- Source template report: `results/B7_nonlocal_template_block_scan_v0.json`
- Template: `w8_21` / width 8
- Non-overlap occurrences in gcm_h6: 20
- Baseline arbitrary rotations per occurrence: 5
- Candidate family: same two-CNOT w8_21 skeleton with one arbitrary rotation fixed to an exact/Clifford angle and the other four angles re-optimized
- Candidate attempts: 55 with 16 seeds each
- Passing candidates at tolerance 1e-08: 0
- Best residual norm: 3.936334e-02
- Best max entry error: 1.823550e-02
- Best fixed parameter/angle: `a` = `pi/2`
- Local finite-difference rank: 5 over ['a', 'b', 'c', 'd', 'e']
- Interpretation: No same-skeleton replacement was found that fixes one of the five arbitrary angles to an exact/Clifford value while preserving the 2-qubit unitary within tolerance.  The finite-difference Jacobian has rank 5 at w8_21, supporting that this template carries five independent continuous degrees inside this skeleton.  This is not a global lower bound over all possible two-qubit circuits, but it closes the most direct T-B7-008 compression path.

## Target Operations

- `rz(a) target`
- `cx control,target`
- `rz(b) target`
- `ry(c) target`
- `rz(pi) target`
- `cx control,target`
- `rz(d) target`
- `ry(e) target`

## Local Rank Check

- Singular values: `[1.3656979119081312, 1.133411232242735, 1.0000000000342875, 0.845800791326925, 0.3672454403477957]`
- Rank threshold: 1e-07
- Rank supports five independent continuous degrees: True

## Top Candidate Attempts

| fixed parameter | exact value | residual | max entry error | candidate T cost | T saving if exact |
|---|---|---:|---:|---:|---:|
| `a` | `pi/2` | 3.936334e-02 | 1.823550e-02 | 80 | 20 |
| `a` | `-pi/2` | 3.936334e-02 | 1.823550e-02 | 80 | 20 |
| `d` | `-pi/4` | 9.086969e-02 | 4.211708e-02 | 81 | 19 |
| `d` | `pi/4` | 9.086969e-02 | 4.211708e-02 | 81 | 19 |
| `d` | `3*pi/4` | 9.086969e-02 | 4.211708e-02 | 81 | 19 |
| `d` | `-3*pi/4` | 9.086969e-02 | 4.211708e-02 | 81 | 19 |
| `d` | `-pi/8` | 1.051023e-01 | 4.939121e-02 | 84 | 16 |
| `d` | `pi/8` | 1.051023e-01 | 4.939121e-02 | 84 | 16 |
| `c` | `pi/8` | 1.326618e-01 | 6.143100e-02 | 84 | 16 |
| `c` | `-pi/8` | 1.326618e-01 | 6.143100e-02 | 84 | 16 |
| `b` | `3*pi/4` | 1.620818e-01 | 7.468998e-02 | 81 | 19 |
| `b` | `-pi/4` | 1.620818e-01 | 7.468998e-02 | 81 | 19 |
| `c` | `pi/4` | 2.598298e-01 | 1.230564e-01 | 81 | 19 |
| `c` | `-pi/4` | 2.598298e-01 | 1.230564e-01 | 81 | 19 |
| `c` | `-3*pi/4` | 2.598298e-01 | 1.230564e-01 | 81 | 19 |
| `c` | `3*pi/4` | 2.598298e-01 | 1.230564e-01 | 81 | 19 |

## Claim Boundary

- same_skeleton_one_rotation_exact_replacement_found: `False`
- same_skeleton_best_residual_below_tolerance: `False`
- five_parameter_family_local_rank: `5`
- rank_supports_five_independent_continuous_degrees: `True`
- would_reduce_arbitrary_occurrences_if_passing: `0`
- would_reduce_t_ledger_if_passing_best: `0`

## Next Actions

- If negative, broaden synthesis beyond the same two-CNOT skeleton: KAK/COSINE-style two-qubit synthesis or numerical search over different CNOT placements.
- If a broader candidate beats 5 arbitrary rotations, emit a QASM rewrite for all 20 w8_21 occurrences and run Aer/proof checks.
- If broader synthesis also fails, write a template-family minimality note as a B7 negative-result lemma.

## Limits

- This is a scoped same-skeleton numerical synthesis probe, not a proof over all two-qubit circuits.
- Exact/Clifford fixed-angle replacements are tested numerically with global phase alignment.
- No full gcm_h6 QASM rewrite is emitted unless a candidate passes the exact tolerance.
- The FT ledger remains a proxy until physical layout and synthesis assumptions are made explicit.
