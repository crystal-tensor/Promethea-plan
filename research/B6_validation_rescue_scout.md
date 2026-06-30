# B6 Validation Rescue Scout

Status: **validation_rescue_candidate_found_not_material_discovery_claim**

## Summary

- Method: `b6_validation_rescue_scout_v0`
- Selected variant: `physics_risk_adjusted_v0`
- Requirements passed / failed: 5 / 3
- Failed requirement IDs: V6, V7, V8
- Source validation errors observed: 2
- Selected negative controls in top-k: 2
- Selected post-split AP: 1.0
- Family-prior AP: 0.4901360544217687
- DFT rows / B5 rows: 0 / 0

## Variant Results

- crystallographic_baseline_v0: post-split AP=0.24761904761904763, negatives_in_top_k=3, candidate=False
- physics_descriptor_v0: post-split AP=0.9093537414965986, negatives_in_top_k=2, candidate=True
- combined_descriptor_v0: post-split AP=0.5791177076891362, negatives_in_top_k=2, candidate=True
- physics_risk_adjusted_v0: post-split AP=1.0, negatives_in_top_k=2, candidate=True
- combined_risk_adjusted_v0: post-split AP=0.5791177076891362, negatives_in_top_k=2, candidate=True
- family_prior_denominator_v0: post-split AP=0.4901360544217687, negatives_in_top_k=3, candidate=False

## Requirement Results

- V1 [PASS]: source descriptor screen is available
- V2 [PASS]: packet scout is available and still demotes B6
- V3 [PASS]: predeclared rescue variants were evaluated
- V4 [PASS]: selected rescue keeps negative controls in top-k
- V5 [PASS]: selected rescue beats post-split family-prior AP
- V6 [FAIL]: reproducible crystallographic backend is pinned
- V7 [FAIL]: DFT observable channel exists
- V8 [FAIL]: B5-computed observable channel exists

## Claim Boundary

- Supported: A predeclared physics-risk rescue candidate clears the two source-validation symptoms on the existing table.
- Not supported: The source screen is not rewritten, no backend is pinned, no DFT/B5 observables exist, and no material-discovery or mechanism claim is made.
- Next gate: Turn the selected rescue into a pinned backend run, then attach DFT and B5 observable rows before any candidate-ranking promotion.
