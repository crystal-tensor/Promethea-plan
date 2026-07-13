# B4/B8 R147 Target-Descriptor Adaptation Holdout Protocol

- Frozen adaptation groups / hidden rows: `12` / `96`
- Three-arm executions / total shots: `288` / `589824`
- Arms: descriptor-adapted foreign route, target-specific R143, automatic
- Adapted-target mean / bootstrap floors: `-0.005` / `-0.01`
- Groups above -0.02 versus target: at least `11 / 12`
- Severe rows below -0.05: at most `0`
- Each-target mean floor: `-0.01`
- Lagos dense-XY mean floor / severe-row cap: `-0.02` / `0`
- Challenge executed: `false`

The selector is frozen before the challenge. It uses only public target readout
and CX calibration descriptors to choose between the two foreign R143 routes.
R146 hidden rows, R146 deltas, and the target-specific R143 route identity are
forbidden selector inputs. The target-specific route is used only as a blind
denominator after preregistration.

This protocol does not represent temporal calibration drift, another machine,
real hardware, mitigation, soundness, quantum advantage, BQP separation, a
solved frontier, or new credit.
