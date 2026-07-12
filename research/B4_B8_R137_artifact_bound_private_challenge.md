# B4/B8 R137 Artifact-Bound Private Challenge

## Result

- Frozen R136 QASM artifacts: `12`
- Late-bound challenges / responses: `48` / `48`
- Probe types: `4`
- Positive transcript accepted: `True`
- Adversarial mutations rejected: `10` / `10`
- Route-realization search cost disclosed: `1536`
- Total compiler calls disclosed: `1656`
- Selection attempts per artifact: `128`
- Phase artifacts replayed across processes: `5` / `5`
- New credit delta: `0`

R137 binds the exact 12 R136 QASM files, their parsed semantic fingerprints,
the R136 result hash, the 1,536-compilation selection ledger, a secret
commitment, and a protocol nonce before generating 48 private probes. The
secret is revealed only after responses exist inside the local execution, so
the verifier can regenerate every challenge and independently recompute every
response.

## Adversarial Pressure

- `post_commit_artifact_hash_substitution`: REJECTED; errors `artifact_hash_mismatch:FakeJakartaV2::dense_validation_complete_ising_n6, commitment_hash_mismatch`.
- `cross_challenge_response_swap`: REJECTED; errors `response_mismatch:8ef64fdff7ffa496beb2f862f93ebf11a9a7c2f2f3d5356f3ce1b292538c1b90, response_mismatch:921a1b34e4963d3417e2b2284f64239e4052205bbc898247d13aa046a3329011`.
- `stale_nonce_replay`: REJECTED; errors `challenge_regeneration_mismatch`.
- `challenge_secret_substitution`: REJECTED; errors `challenge_regeneration_mismatch, challenge_secret_commitment_mismatch`.
- `challenge_deletion`: REJECTED; errors `challenge_count_mismatch, challenge_coverage_mismatch, challenge_regeneration_mismatch, response_count_or_uniqueness_mismatch`.
- `selection_cost_underreporting`: REJECTED; errors `commitment_hash_mismatch, selection_cost_underreported_or_inconsistent, total_compilation_cost_mismatch`.
- `forged_probe_response`: REJECTED; errors `response_mismatch:fbec04589203123fd05eeb90a9c99c51b334ca5d527ce475bb3ff015aa931870`.
- `private_material_injected_before_commit`: REJECTED; errors `commitment_hash_mismatch, precommit_contains_private_material:challenge_secret_hex`.
- `artifact_omission`: REJECTED; errors `artifact_count_mismatch, challenge_regeneration_mismatch, commitment_hash_mismatch, missing_response_or_artifact:1d813d7caef320844921a7404361b0821855c2ad2b082859f6426a251a05140b, missing_response_or_artifact:5d0e28a5a3e8ad025c93d76e834dc31554e1ebc3a6bf42f7de64a0267c6190fc, missing_response_or_artifact:c0230c2cf3ea01c1b3707926605cbe841c31c33fa828a38d6bb54213d54d9b31, missing_response_or_artifact:c1eaaa6c9e0120f59d21b3e43675e2ae5019e142d1da750419051cd2cdec1c88`.
- `duplicate_response_replay`: REJECTED; errors `missing_response_or_artifact:c1eaaa6c9e0120f59d21b3e43675e2ae5019e142d1da750419051cd2cdec1c88, response_count_or_uniqueness_mismatch`.

## Requirements

- `P1` PASS: R136 no-loss source and payload are hash-bound
- `P2` PASS: all 12 exact QASM artifacts and semantic fingerprints match
- `P3` PASS: secret commitment and protocol nonce precede challenge generation
- `P4` PASS: 48 late-bound challenges cover four probe types on every artifact
- `P5` PASS: all challenge responses independently recompute
- `P6` PASS: full 1,536-selection and 1,656-total cost ledger is bound
- `P7` PASS: all ten adversarial transcript mutations are rejected
- `P8` PASS: all five phase artifacts replay identically in a fresh process
- `P9` PASS: acceptance is restricted to local artifact integrity
- `P10` PASS: hardware, soundness, advantage, BQP, and new credit remain excluded

## Claim Boundary

Supported: local artifact-integrity verifier acceptance for a commit-challenge-
response-reveal transcript that binds all 12 R136 QASM artifacts and charges the
full compiler-selection ledger. Not supported: externally timestamped
preregistration, independent secret custody, statistical performance
acceptance, device calibration, hardware execution, protocol or cryptographic
soundness, sampling hardness, quantum advantage, BQP separation, or new B10
credit.
