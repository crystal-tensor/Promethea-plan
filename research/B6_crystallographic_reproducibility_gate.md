# B6 Crystallographic Reproducibility Gate

- Benchmark: `B6`
- Method: `b6_crystallographic_reproducibility_gate_v0`
- Status: `crystallographic_reproducibility_gate_failed_not_material_discovery_claim`
- Source result: `results/B6_crystallographic_descriptor_screen_v0.json`
- Source method/status: `b6_crystallographic_descriptor_screen_v0` / `crystallographic_descriptor_screen_not_material_discovery_claim`
- Gates passed/failed: 6 / 5

## Result

T-B6-004 has useful crystallographic descriptor evidence, but it is not a materials-discovery, solved-mechanism, complete-database, DFT-observable, or B5-computed-observable result. In the current runtime, the crystallographic backend is not reproducible because `pymatgen` is unavailable.

## Metrics

- Records / families: 56 / 28
- Negative controls / top-k negatives: 18 / 0
- Post-split records / positives: 27 / 7
- AP all crystallographic: 0.7125
- AP post-split crystallographic / family prior / physics / combined: 0.2476190476190476 / 0.4901360544217687 / 0.9093537414965985 / 0.5791177076891362
- Source validation error count: 2

## Gate Requirements

| ID | Pass | Requirement | Evidence |
| --- | --- | --- | --- |
| R1 | yes | source T-B6-004 result exists | path=results/B6_crystallographic_descriptor_screen_v0.json; method='b6_crystallographic_descriptor_screen_v0' |
| R2 | yes | expanded table has at least 50 records | record_count=56 |
| R3 | yes | post-2008 split has at least 24 records | post_split_record_count=27 |
| R4 | yes | expanded negative controls are present | negative_control_count=18 |
| R5 | yes | source boundary claims crystallographic descriptor data | real_crystallographic_data=True |
| R6 | no | current runtime can reproduce pymatgen-dependent descriptors | pymatgen_available=False; python=3.12.6 |
| R7 | no | source validation errors are empty | validation_errors=['no negative controls in top-k', 'family prior dominates: 0.4901 vs 0.2476'] |
| R8 | no | post-split crystallographic AP beats family prior | post_split_crystallo_ap=0.2476190476190476; post_split_family_prior_ap=0.4901360544217687 |
| R9 | no | DFT observables are available | dft_observables=False |
| R10 | no | B5-computed observables are available | b5_computed_observables=False |
| R11 | yes | no discovery, mechanism, or complete-database claim | material_discovery=False; mechanism_solved=False; complete_database=False |

## Claim Boundary

- No material discovery is claimed.
- No high-temperature superconductivity mechanism is claimed solved.
- No complete materials database is claimed.
- No DFT or B5-computed observable is claimed.
- Next required artifact: a pinned crystallographic/DFT/B5 observable pipeline that beats family-prior baselines on post-split holdouts.
