# B9 Named-Family Width/Locality Bound Skeleton v0.1

Last updated: 2026-06-17

Status: **named_family_width_locality_bound_skeleton_not_checked_theorem**

## Summary

- Named family: `cluster_stabilizer_open_uniform_reweight`
- Source method: small_local_hamiltonian_gap_lab_v0
- Rows matched: 3 for qubits [4, 5, 6]
- Scaling factor: 1.35
- Max locality: 3
- Locality bound preserved: True
- Raw gap amplifies: True
- Normalized gap invariant: True
- Certificate rejected: True
- Proof assistant checked: False
- Proof assistant status: failed
- Formal theorem proved: False
- Explicitly not Quantum PCP proof: True
- Global impossibility claimed: False
- Validation errors: 0

## Analytic Bound Statement

- For the open-boundary cluster stabilizer family, every generated term has support size 2 or 3.
- The B9 local_interaction_reweight_v0 transformation multiplies every support>=2 term by 1.35.
- Therefore H'_n = 1.35 * H_n for the generated family rows.
- Positive uniform scaling preserves eigenvectors and scales both spectral gap and spectral width by 1.35.
- The normalized gap gap(H)/width(H) is invariant, while max locality remains 3.

## Finite Row Checks

- n=4: term_count=4, supports=[2, 3], unique_scales=[1.35], max_support=3
- n=5: term_count=5, supports=[2, 3], unique_scales=[1.35], max_support=3
- n=6: term_count=6, supports=[2, 3], unique_scales=[1.35], max_support=3

## Rejection Reason

Raw spectral gap growth is exactly global positive energy rescaling; spectral width scales by the same factor, so normalized gap does not improve.

## Claim Boundary

- Supported: a named-family analytic skeleton explaining why the B9 v0 cluster-stabilizer local reweight rows are only uniform energy rescaling.
- Supported: finite rows n=4,5,6 match the symbolic locality/width story.
- Not supported: proof-assistant checked theorem, Quantum PCP proof, NLTS theorem, or global gap-amplification no-go theorem.

## Remaining Steps

- Formalize the parameterized open-boundary cluster stabilizer Hamiltonian in an actual Lean/mathlib project.
- Prove the support-size and uniform-scaling lemmas over all n >= 4.
- Prove spectral gap, spectral width, and normalized-gap scaling for positive scalar multiplication of self-adjoint matrices.
- Connect the finite JSON rows to generated certificates rather than manual inspection.
- Generalize from this rejected uniform-scaling family to nontrivial locality-preserving transformations or prove a narrower no-go theorem.

## Proof-Check Environment Note

```text
/Users/avalok/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
Traceback (most recent call last):
  File "/Users/avalok/Library/Python/3.9/bin/lean", line 3, in <module>
    from lean.main import main
  File "/Users/avalok/Library/Python/3.9/lib/python/site-packages/lean/main.py", line 87, in <module>
    from lean.commands import lean
  File "/Users/avalok/Library/Python/3.9/lib/python/site-packages/lean/commands/__init__.py", line 14, in <module>
    from lean.commands.lean import lean
  File "/Users/avalok/Library/Python/3.9/lib/python/site-packages/lean/commands/lean.py", line 17, in <module>
    from lean.click import verbose_option
  File "/Users/avalok/Library/Python/3.9/lib/python/site-packages/lean/click.py", line 21, in <module>
    from lean.container import container
  File "/Users/avalok/Library/Python/3.9/lib/python/site-packages/lean/container.py", line 17, in <module>
    from lean.components.api.api_client import APIClient
  File "/Users/avalok/Library/Python/3.9/lib/python/site-packages/lean/components/api/api_client.py", line 16, in <module>
    from lean.components.api.auth0_client import Auth0Client
  File "/Users/avalok/Library/Python/3.9/lib/python/site-packages/lean/components/api/auth0_client.py", line 15, in <module>
    from lean.components.util.logger import Logger
  File "/Users/avalok/Library/Python/3.9/lib/python/site-packages/lean/components/util/logger.py", line 18, in <module>
    from lean.models.logger import Option
  File "/Users/avalok/Library/Python/3.9/lib/python/site-packages/lean/models/__init__.py", line 49, in <module>
    raise FileNotFoundError(
FileNotFoundError: Modules json not found in the given path /Users/avalok/Library/Python/3.9/lib/python/site-packages/lean/modules-1.14.json: HTTPSConnectionPool(host='cdn.
```
