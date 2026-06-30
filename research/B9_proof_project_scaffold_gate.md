# B9 Lean/Lake Proof Project Scaffold Gate

Status: **proof_project_scaffold_open_not_checked**

T-B9-004d creates a repository-local Lean/Lake scaffold and replaces the named-family placeholder theorem with an indexed theorem interface. This is still not a formal B9 theorem, Quantum PCP proof, NLTS proof, or global gap-amplification impossibility theorem.

## Metrics

- Named family: `cluster_stabilizer_open_uniform_reweight`
- Readiness failed gates: `['PE-03', 'PE-04', 'PE-09']`
- Contract failed requirements: `['K4', 'K5', 'K8']`
- Scaffold requirements passed / failed: 6 / 2
- Failed scaffold requirement IDs: `['S7', 'S8']`
- Lean toolchain: `lean-toolchain`
- Lakefile: `lakefile.lean`
- Lean project module: `B9/ClusterStabilizer/WidthLocality.lean`

## Requirements

| ID | Pass | Requirement | Evidence |
| --- | --- | --- | --- |
| S1 | yes | source readiness gate is refreshed after scaffold creation | failed_gate_ids=['PE-03', 'PE-04', 'PE-09'] |
| S2 | yes | source contract gate is refreshed after scaffold creation | failed_contract_requirement_ids=['K4', 'K5', 'K8'] |
| S3 | yes | Lean toolchain file is pinned | lean-toolchain |
| S4 | yes | Lake project file declares mathlib dependency | lakefile.lean |
| S5 | yes | skeleton theorem interface is indexed and non-placeholder | research/proof_skeletons/B9_cluster_stabilizer_width_locality_bound.lean |
| S6 | yes | Lake module mirrors the theorem interface | B9/ClusterStabilizer/WidthLocality.lean |
| S7 | no | actual Lean 4 executable is available | lean4_signature_detected=False |
| S8 | no | the theorem is proof-assistant checked | proof_assistant_checked=False; formal_theorem_proved=False |

## Claim Boundary

- The Lean/Lake project scaffold exists.
- The named-family obligation is no longer a `True` placeholder.
- The theorem is not proof-assistant checked.
- The local executable named `lean` is not yet accepted as Lean 4 unless the version signature proves it.
- Lake is still missing in the current environment.
- No Quantum PCP, NLTS, or global gap-amplification theorem is claimed.
