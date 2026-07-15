import Lake
open Lake DSL

package axiom_horizon_b9 where
  -- This Lake project is a proof scaffold for B9 only. It intentionally does
  -- not claim a checked theorem until a real Lean 4/Lake toolchain succeeds.

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.12.0"

@[default_target]
lean_lib B9 where
  roots := #[
    `B9.ClusterStabilizer.WidthLocality,
    `B9.ClusterStabilizer.PauliBasisAction
  ]
