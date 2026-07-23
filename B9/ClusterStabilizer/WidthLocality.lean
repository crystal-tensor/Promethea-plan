import Mathlib.Data.Real.Basic

namespace B9

structure SpectralSummary where
  gap : Real
  width : Real
  normalizedGap : Real
  locality : Nat

section ClusterStabilizer
namespace ClusterStabilizer

def RawGapAmplifies (before after : SpectralSummary) : Prop :=
  after.gap > before.gap

def NormalizedGapInvariant (before after : SpectralSummary) : Prop :=
  after.normalizedGap = before.normalizedGap

def LocalityPreserved (before after : SpectralSummary) : Prop :=
  after.locality = before.locality

theorem uniform_scale_raw_gap_is_not_certificate
    (before after : SpectralSummary)
    (_hRaw : RawGapAmplifies before after)
    (hInvariant : NormalizedGapInvariant before after) :
    ¬ (after.normalizedGap > before.normalizedGap) := by
  intro hImp
  rw [hInvariant] at hImp
  exact (lt_irrefl before.normalizedGap) hImp

theorem cluster_stabilizer_open_uniform_reweight_obligation
    (n : Nat)
    (_hN : 4 <= n)
    (before after : SpectralSummary)
    (hLocality : LocalityPreserved before after)
    (hRaw : RawGapAmplifies before after)
    (hInvariant : NormalizedGapInvariant before after) :
    after.locality = before.locality ∧
      ¬ (after.normalizedGap > before.normalizedGap) := by
  constructor
  . exact hLocality
  . exact uniform_scale_raw_gap_is_not_certificate before after hRaw hInvariant

end ClusterStabilizer

end ClusterStabilizer

open ClusterStabilizer

section SupportSize

def HasSupportSize (summary : SpectralSummary) : Prop :=
  summary.locality = 2 ∨ summary.locality = 3

theorem locality_in_support_set (summary : SpectralSummary) (hLoc : HasSupportSize summary) :
    summary.locality = 2 ∨ summary.locality = 3 := hLoc

def MaxLocalityPreserved (before after : SpectralSummary) : Prop :=
  after.locality <= before.locality

theorem uniform_scale_preserves_max_locality
    (before after : SpectralSummary)
    (hLoc : LocalityPreserved before after) :
    MaxLocalityPreserved before after := by
  unfold MaxLocalityPreserved
  rw [hLoc]

end SupportSize

section UniformScaling

noncomputable def UniformScaleFactor : Real := 27/20

def IsUniformlyScaled (before after : SpectralSummary) : Prop :=
  after.gap = UniformScaleFactor * before.gap ∧
  after.width = UniformScaleFactor * before.width

theorem normalized_gap_scale_cancel
    (gap width scale : Real)
    (hScale : scale ≠ 0) :
    (scale * gap) / (scale * width) = gap / width := by
  by_cases hWidth : width = 0
  · simp [hWidth]
  · rw [div_eq_mul_inv, div_eq_mul_inv, mul_inv_rev]
    calc
      scale * gap * (width⁻¹ * scale⁻¹) =
          (scale * scale⁻¹) * (gap * width⁻¹) := by ac_rfl
      _ = gap * width⁻¹ := by rw [mul_inv_cancel₀ hScale, one_mul]

theorem uniform_scale_preserves_normalized_gap_from_nonzero_scale
    (gap width scale : Real)
    (before after : SpectralSummary)
    (hScale : scale ≠ 0)
    (hBefore : before.normalizedGap = gap / width)
    (hAfter : after.normalizedGap = (scale * gap) / (scale * width)) :
    ClusterStabilizer.NormalizedGapInvariant before after := by
  unfold ClusterStabilizer.NormalizedGapInvariant
  rw [hAfter, hBefore, normalized_gap_scale_cancel gap width scale hScale]

theorem uniform_scale_factor_ne_zero : UniformScaleFactor ≠ 0 := by
  norm_num [UniformScaleFactor]

theorem uniform_scale_preserves_normalized_gap
    (gap width scale : Real)
    (before after : SpectralSummary)
    (hBefore : before.normalizedGap = gap / width)
    (hAfter : after.normalizedGap = (scale * gap) / (scale * width))
    (hRatio : (scale * gap) / (scale * width) = gap / width) :
    ClusterStabilizer.NormalizedGapInvariant before after := by
  unfold ClusterStabilizer.NormalizedGapInvariant
  rw [hAfter, hBefore, hRatio]

end UniformScaling

section SpectralWidth

def SpectralWidthPreserved (before after : SpectralSummary) : Prop :=
  after.width / after.gap = before.width / before.gap

theorem spectral_width_ratio_scale_cancel
    (width gap scale : Real)
    (hScale : scale ≠ 0) :
    (scale * width) / (scale * gap) = width / gap := by
  exact normalized_gap_scale_cancel width gap scale hScale

theorem uniform_scale_preserves_spectral_width_ratio_from_nonzero_scale
    (before after : SpectralSummary)
    (scale : Real)
    (hScale : scale ≠ 0)
    (hGap : after.gap = scale * before.gap)
    (hWidth : after.width = scale * before.width) :
    SpectralWidthPreserved before after := by
  unfold SpectralWidthPreserved
  rw [hWidth, hGap]
  exact spectral_width_ratio_scale_cancel before.width before.gap scale hScale

theorem uniform_scale_preserves_spectral_width_ratio_concrete
    (before after : SpectralSummary)
    (hScale : IsUniformlyScaled before after) :
    SpectralWidthPreserved before after := by
  rcases hScale with ⟨hGap, hWidth⟩
  exact uniform_scale_preserves_spectral_width_ratio_from_nonzero_scale
    before after UniformScaleFactor uniform_scale_factor_ne_zero hGap hWidth

theorem uniform_scale_preserves_spectral_width_ratio
    (before after : SpectralSummary)
    (hScale : IsUniformlyScaled before after)
    (hRatio : (UniformScaleFactor * before.width) / (UniformScaleFactor * before.gap) = before.width / before.gap) :
    SpectralWidthPreserved before after := by
  rcases hScale with ⟨hGap, hWidth⟩
  unfold SpectralWidthPreserved
  rw [hGap, hWidth]
  exact hRatio

end SpectralWidth

end B9
