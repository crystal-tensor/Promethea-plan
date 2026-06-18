# B6 Formula-Derived Descriptor Screen v0.1

- Status: formula_descriptor_screen_not_material_discovery_claim
- Method: b6_formula_descriptor_screen_v0
- Model status: formula_element_table_descriptors_with_b5_correlation_proxy_not_material_discovery
- Records: 38
- Curated records: 26
- Expanded negative controls: 12
- Families: 22
- High-Tc threshold: 30.0 K
- Formula AP@12: 0.09999999999999999
- Family-prior AP@12: 1.0
- Post-split formula AP: 0.5947278911564625
- Post-split family-prior AP: 0.9821428571428571
- Validation errors: []

## Top Formula-Descriptor Rows

| rank | material | formula | family | Tc K | source | score | B5 corr proxy | B5 screen proxy | parsed elements |
|---:|---|---|---|---:|---|---:|---:|---:|---|
| 1 | CuO_negative | CuO | binary_oxide_negative | 0.0 | negative_control | 1.7868 | 0.6300 | 0.8850 | {'Cu': 1.0, 'O': 1.0} |
| 2 | FeSe_2008 | FeSe | iron_chalcogenide | 8.0 | curated | 1.2740 | 0.5400 | 0.6800 | {'Fe': 1.0, 'Se': 1.0} |
| 3 | FeSe_ambient_low_tc_control | FeSe | iron_chalcogenide_low_tc_control | 8.0 | negative_control | 1.2740 | 0.5400 | 0.6800 | {'Fe': 1.0, 'Se': 1.0} |
| 4 | PrNiO2_parent_negative | PrNiO2 | nickelate_parent_negative | 0.0 | negative_control | 1.2739 | 0.5242 | 0.4997 | {'Ni': 1.0, 'O': 2.0, 'Pr': 1.0} |
| 5 | FeSe_pressure_2009 | FeSe | iron_chalcogenide | 37.0 | curated | 1.2303 | 0.5400 | 0.6800 | {'Fe': 1.0, 'Se': 1.0} |
| 6 | YBCO_1987 | YBa2Cu3O7-d | cuprate | 93.0 | curated | 1.1783 | 0.4470 | 0.4709 | {'Ba': 2.0, 'Cu': 3.0, 'O': 7.0, 'Y': 1.0} |
| 7 | LaNiO3_negative | LaNiO3 | nickelate_parent_negative | 0.0 | negative_control | 1.1609 | 0.4481 | 0.3964 | {'La': 1.0, 'Ni': 1.0, 'O': 3.0} |
| 8 | NdNiO3_negative | NdNiO3 | nickelate_parent_negative | 0.0 | negative_control | 1.1595 | 0.4481 | 0.3938 | {'Nd': 1.0, 'Ni': 1.0, 'O': 3.0} |
| 9 | BaKFe2As2_2008 | Ba1-xKxFe2As2 | iron_pnictide | 38.0 | curated | 1.0947 | 0.5014 | 0.5891 | {'As': 2.0, 'Ba': 1.0, 'Fe': 2.0} |
| 10 | BaFe2As2_parent_negative | BaFe2As2 | iron_pnictide_parent_negative | 0.0 | negative_control | 1.0947 | 0.5014 | 0.5891 | {'As': 2.0, 'Ba': 1.0, 'Fe': 2.0} |
| 11 | LaFeAsOF_2008 | LaFeAsO1-xFx | iron_pnictide | 26.0 | curated | 1.0860 | 0.4832 | 0.4617 | {'As': 1.0, 'Fe': 1.0, 'La': 1.0, 'O': 1.0} |
| 12 | SmFeAsOF_2008 | SmFeAsO1-xFx | iron_pnictide | 55.0 | curated | 1.0831 | 0.4832 | 0.4564 | {'As': 1.0, 'Fe': 1.0, 'O': 1.0, 'Sm': 1.0} |

## Claim Boundary

- material_discovery_claimed: False
- mechanism_solved: False
- complete_materials_database: False
- computed_quantum_observable_claimed: False
- uses_formula_derived_descriptors: True
- uses_b5_linked_proxy: True
- what_is_supported: A deterministic formula parser and embedded element table now produce structural/electronic descriptor proxies plus B5-linked correlation/screening proxies over the curated table and expanded negative controls.
- what_is_not_supported: The result is not a materials discovery, not a solved high-Tc mechanism, not a complete database, and not a computed DFT/DMRG/quantum observable.

## Next Gate

Replace these formula-derived proxies with computed structural/electronic descriptors
from crystallographic records, DFT summaries, or B5 tensor/DMRG observables. Expand
the post-2008 negative set so family priors and random baselines cannot saturate.
