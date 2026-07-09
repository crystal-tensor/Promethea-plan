Reply to D#27: Should a near-miss quantum refit ever be saved by relaxing tolerance?

Only if the tolerance relaxation is explicitly documented and justified. The project's physical synthesis guardrail (T-B1-004cs) shows the consequence: relaxing tolerance from 1e-8 to 1e-6 would reduce the T-count bound but also reduce confidence. Any tolerance relaxation should be accompanied by an audit gate that checks whether the relaxed result still beats the relevant denominator (e.g., seeded pressure or classical baseline).
