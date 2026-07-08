# B1/B7 Cone01 R27 O3-F4 Tolerance-Ablation Gate

- Target: `T-B1-004ec/T-B7-013l`
- Upstream target: `T-B1-004eb/T-B7-013k`
- Method: `b1_b7_cone01_r27_o3_f4_tolerance_ablation_gate_v0`
- Status: `cone01_r27_o3_f4_tolerance_ablation_blocks_tolerance_waiver`
- Ablation hash: `fd9d2333a13057ab367029cd4e1cac7423ffb4a6ed816e5b498fd8e9dba9f7be`
- Source R26 sentinel hash: `bb93711b3b2dc2a8b73ded6536e56ad14357eeb544029bd65a7c6b18a751add3`
- Source near-miss fixture hash: `a239097cd2ca844d616829a141a6490e74285f8af16fee506c70088125d43873`

## Result

R27 passes 9/9 requirements. It blocks tolerance relaxation as a shortcut: F4-A2 can pass at relaxed tolerances, but F4-A5/F4-A6/F4-A7 keep the fixture rejected.

## Tolerance Sweep

| tolerance | F4-A2 replay | failed gates | accepted |
| --- | --- | --- | --- |
| `1e-08` | `False` | `['F4-A2', 'F4-A5', 'F4-A6', 'F4-A7']` | `False` |
| `1.8e-08` | `False` | `['F4-A2', 'F4-A5', 'F4-A6', 'F4-A7']` | `False` |
| `2e-08` | `True` | `['F4-A5', 'F4-A6', 'F4-A7']` | `False` |
| `1e-07` | `True` | `['F4-A5', 'F4-A6', 'F4-A7']` | `False` |

## Requirement Results

- `S1` PASS: R24 harness and R26 near-miss sentinel are validation-clean sources
- `S2` PASS: Tolerance sweep includes strict and relaxed replay thresholds
- `S3` PASS: Strict R26 tolerance still rejects same-unitary replay
- `S4` PASS: At least one relaxed tolerance flips only F4-A2 to pass
- `S5` PASS: Certificate, denominator, and leakage gates remain failed for every tolerance
- `S6` PASS: No sweep row accepts the near-miss fixture
- `S7` PASS: Tolerance waiver remains disallowed without certificate, denominator, and leakage fixes
- `S8` PASS: R27 preserves zero O3, reroute, and B7 credit claims
- `S9` PASS: Ablation packet is hash-bound to R24, R26, and the near-miss fixture

## Claim Boundary

- Supported: R27 shows that relaxing same-unitary replay tolerance can make F4-A2 pass, but cannot accept the R26 near-miss fixture because certificate, denominator, and leakage gates remain failed.
- Not supported: R27 does not submit or accept a valid O3-F4 refit artifact, does not close O3, and does not permit R5 reroute. No B7 credit or resource saving is supported.
- Next gate: Submit a valid O3-F4 artifact that passes all F4-A1..F4-A9 under the strict tolerance with complete certificate, same-access denominator comparison, and leakage-free trace; or return to O3-F3/O3-F5.

- validation_error_count: `0`
