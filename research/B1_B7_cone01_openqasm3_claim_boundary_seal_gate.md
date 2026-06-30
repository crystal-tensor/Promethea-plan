# B1/B7 cone_01 OpenQASM 3 Claim-Boundary Seal Gate

- Method: `b1_b7_cone01_openqasm3_claim_boundary_seal_gate_v0`
- Status: `cone01_openqasm3_claim_boundary_sealed_without_b7_credit`
- Model status: `qiskit_loader_replay_chain_citable_but_resource_boundary_blocks_b7_credit`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- Supported claim: The current OpenQASM 3/Qiskit-loader evidence chain is coherent enough to cite as finite-span replay and seeded-product semantic pressure for the selected cone_01 patch lines.

## Source Gates

- Evidence-seal reproduction: `results/B1_B7_cone01_openqasm3_qiskit_loader_evidence_seal_reproduction_gate_v0.json`
- Linear-span certificate: `results/B1_B7_cone01_openqasm3_qiskit_loader_linear_span_replay_certificate_gate_v0.json`
- Composable patch lift: `results/B1_B7_cone01_openqasm3_qiskit_loader_composable_patch_lift_gate_v0.json`
- Seeded resource boundary: `results/B1_B7_cone01_openqasm3_qiskit_loader_seeded_resource_boundary_gate_v0.json`

## Seal Requirements

- `S1` Qiskit-loader evidence seal is byte-stably reproduced: `True`. seal=d06c1fdae3ad7cad1971cdcdcea1f890d3931924a7e70affc25fdf89737e09a8
- `S2` Qiskit loader has a certified finite linear span: `True`. dimension=6, spectral_error=2.7889440543898627e-13
- `S3` Composable patch lift is supported through the Qiskit loader: `True`. selected_lines=[268, 1381], certified_fraction=1.1444091796875e-05
- `S4` Seeded product replay survives the loader path: `True`. cases=16, min_fidelity=0.9999999999999389
- `S5` Line 1381 resource burden is still explicit: `True`. off_grid=5, proxy_t=100
- `S6` Dropped overlap line 1378 remains unrecovered: `True`. line1378_delta_recovered=False
- `S7` B7 ledger credit remains zero: `True`. occurrence=0, proxy_t=0
- `S8` All resource blockers are still open: `True`. failed_blockers=5/5

## Decision

- Selected line numbers: `[268, 1381]`
- Dropped overlap line numbers: `[1378]`
- Qiskit-loader linear-span dimension / spectral error: `6` / `2.7889440543898627e-13`
- Certified input-subspace fraction: `1.1444091796875e-05`
- Seeded product cases / min fidelity: `16` / `0.9999999999999389`
- Line-1381 off-grid local-U3 parameters / proxy-T pressure: `5` / `100`
- Line-1378 delta recovered: `False`
- Resource blockers still failed: `5` / `5`
- Accepted occurrence / proxy-T reduction: `0` / `0`
- Accepted claim-boundary seal: `1`

## Claim Boundary

- No B7 resource reduction is accepted.
- No full-Hilbert-space symbolic equivalence theorem is claimed.
- No line-1381 local-U3 pricing certificate is accepted.
- No recovery of the dropped line-1378 overlap delta is recorded.
- No occurrence-removing certificate meeting the 30-window target exists.

## Next Gate

Either price/remove the five line-1381 off-grid local-U3 parameters, recover line 1378 without overlap double-counting, or produce at least 30 occurrence-removing certificates accepted by the refreshed B7 ledger.

## Validation

- Claim boundary sealed: `True`
- Validation errors: `0`
