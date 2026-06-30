import Mathlib.Data.Real.Basic

namespace B9.ClusterStabilizer

structure SpectralSummary where
  gap : Real
  width : Real
  normalizedGap : Real
  locality : Nat

def RawGapAmplifies (before after : SpectralSummary) : Prop :=
  after.gap > before.gap

def NormalizedGapInvariant (before after : SpectralSummary) : Prop :=
  after.normalizedGap = before.normalizedGap

def LocalityPreserved (before after : SpectralSummary) : Prop :=
  after.locality = before.locality

theorem uniform_scale_raw_gap_is_not_certificate
    (before after : SpectralSummary)
    (hRaw : RawGapAmplifies before after)
    (hInvariant : NormalizedGapInvariant before after) :
    not (after.normalizedGap > before.normalizedGap) := by
  intro hImproves
  rw [hInvariant] at hImproves
  exact (lt_irrefl before.normalizedGap) hImproves

theorem cluster_stabilizer_open_uniform_reweight_obligation
    (n : Nat)
    (hN : 4 <= n)
    (before after : SpectralSummary)
    (hLocality : LocalityPreserved before after)
    (hRaw : RawGapAmplifies before after)
    (hInvariant : NormalizedGapInvariant before after) :
    after.locality = before.locality ∧
      not (after.normalizedGap > before.normalizedGap) := by
  constructor
  · exact hLocality
  · exact uniform_scale_raw_gap_is_not_certificate before after hRaw hInvariant

end B9.ClusterStabilizer
