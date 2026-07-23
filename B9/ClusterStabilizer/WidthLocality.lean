import Mathlib.Data.Real.Basic
import Mathlib.Tactic

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

inductive ClusterTerm (n : Nat) where
  | interior (i : Nat) (left : 1 ≤ i) (right : i + 1 < n)
  | leftBoundary (size : 2 ≤ n)
  | rightBoundary (size : 2 ≤ n)

def ClusterTerm.locality {n : Nat} : ClusterTerm n → Nat
  | .interior _ _ _ => 3
  | .leftBoundary _ => 2
  | .rightBoundary _ => 2

def ClusterTerm.uniformReweight {n : Nat} (term : ClusterTerm n) (_scale : Real) : ClusterTerm n :=
  term

theorem cluster_term_locality_in_support_set
    {n : Nat} (term : ClusterTerm n) :
    term.locality = 2 ∨ term.locality = 3 := by
  cases term <;> simp [ClusterTerm.locality]

theorem cluster_term_max_locality
    {n : Nat} (term : ClusterTerm n) :
    term.locality ≤ 3 := by
  cases term <;> simp [ClusterTerm.locality]

theorem cluster_term_summary_has_support_size
    {n : Nat} (term : ClusterTerm n)
    (gap width normalizedGap : Real) :
    HasSupportSize {
      gap := gap
      width := width
      normalizedGap := normalizedGap
      locality := term.locality
    } := by
  unfold HasSupportSize
  exact cluster_term_locality_in_support_set term

theorem uniform_reweight_preserves_cluster_term_locality
    {n : Nat} (term : ClusterTerm n) (scale : Real) :
    (term.uniformReweight scale).locality = term.locality := by
  rfl

def ClusterTerm.at {n : Nat} (hN : 2 ≤ n) (i : Fin n) : ClusterTerm n :=
  if hLeft : i.val = 0 then
    .leftBoundary hN
  else if hRight : i.val + 1 = n then
    .rightBoundary hN
  else
    .interior i.val (by omega) (by omega)

def ClusterTermFamily (n : Nat) := Fin n → ClusterTerm n

def canonicalClusterTermFamily {n : Nat} (hN : 2 ≤ n) : ClusterTermFamily n :=
  fun i => ClusterTerm.at hN i

theorem cluster_term_at_locality_in_support_set
    {n : Nat} (hN : 2 ≤ n) (i : Fin n) :
    (ClusterTerm.at hN i).locality = 2 ∨ (ClusterTerm.at hN i).locality = 3 := by
  unfold ClusterTerm.at
  split
  · simp [ClusterTerm.locality]
  · split
    · simp [ClusterTerm.locality]
    · simp [ClusterTerm.locality]

theorem cluster_term_at_max_locality
    {n : Nat} (hN : 2 ≤ n) (i : Fin n) :
    (ClusterTerm.at hN i).locality ≤ 3 := by
  unfold ClusterTerm.at
  split
  · simp [ClusterTerm.locality]
  · split
    · simp [ClusterTerm.locality]
    · simp [ClusterTerm.locality]

theorem canonical_cluster_term_family_locality_in_support_set
    {n : Nat} (hN : 2 ≤ n) (i : Fin n) :
    (canonicalClusterTermFamily hN i).locality = 2 ∨
      (canonicalClusterTermFamily hN i).locality = 3 := by
  exact cluster_term_at_locality_in_support_set hN i

theorem canonical_cluster_term_family_max_locality
    {n : Nat} (hN : 2 ≤ n) (i : Fin n) :
    (canonicalClusterTermFamily hN i).locality ≤ 3 := by
  exact cluster_term_at_max_locality hN i

theorem canonical_cluster_term_family_is_total
    {n : Nat} (hN : 2 ≤ n) :
    ∀ i : Fin n, ∃ term : ClusterTerm n,
      canonicalClusterTermFamily hN i = term := by
  intro i
  exact ⟨canonicalClusterTermFamily hN i, rfl⟩

inductive PauliAxis where
  | x
  | z
deriving DecidableEq, Repr

structure PauliFactor (n : Nat) where
  site : Fin n
  axis : PauliAxis

structure PauliTerm (n : Nat) where
  factors : List (PauliFactor n)

def PauliTerm.locality {n : Nat} (term : PauliTerm n) : Nat :=
  term.factors.length

def ClusterTerm.toPauliTerm {n : Nat} : ClusterTerm n → PauliTerm n
  | .interior i left right =>
      { factors := [
          { site := ⟨i - 1, by omega⟩, axis := .z },
          { site := ⟨i, by omega⟩, axis := .x },
          { site := ⟨i + 1, by omega⟩, axis := .z }
        ] }
  | .leftBoundary size =>
      { factors := [
          { site := ⟨0, by omega⟩, axis := .x },
          { site := ⟨1, by omega⟩, axis := .z }
        ] }
  | .rightBoundary size =>
      { factors := [
          { site := ⟨n - 2, by omega⟩, axis := .z },
          { site := ⟨n - 1, by omega⟩, axis := .x }
        ] }

theorem cluster_term_to_pauli_term_locality
    {n : Nat} (term : ClusterTerm n) :
    term.toPauliTerm.locality = term.locality := by
  cases term <;> simp [ClusterTerm.toPauliTerm, PauliTerm.locality, ClusterTerm.locality]

def HamiltonianTermFamily (n : Nat) := Fin n → PauliTerm n

def canonicalHamiltonianTermFamily {n : Nat} (hN : 2 ≤ n) : HamiltonianTermFamily n :=
  fun i => (ClusterTerm.at hN i).toPauliTerm

theorem canonical_hamiltonian_term_family_locality
    {n : Nat} (hN : 2 ≤ n) (i : Fin n) :
    (canonicalHamiltonianTermFamily hN i).locality =
      (canonicalClusterTermFamily hN i).locality := by
  exact cluster_term_to_pauli_term_locality (ClusterTerm.at hN i)

theorem canonical_hamiltonian_term_family_locality_in_support_set
    {n : Nat} (hN : 2 ≤ n) (i : Fin n) :
    (canonicalHamiltonianTermFamily hN i).locality = 2 ∨
      (canonicalHamiltonianTermFamily hN i).locality = 3 := by
  rw [canonical_hamiltonian_term_family_locality hN i]
  exact canonical_cluster_term_family_locality_in_support_set hN i

theorem canonical_hamiltonian_term_family_max_locality
    {n : Nat} (hN : 2 ≤ n) (i : Fin n) :
    (canonicalHamiltonianTermFamily hN i).locality ≤ 3 := by
  rw [canonical_hamiltonian_term_family_locality hN i]
  exact canonical_cluster_term_family_max_locality hN i

theorem canonical_hamiltonian_term_family_is_total
    {n : Nat} (hN : 2 ≤ n) :
    ∀ i : Fin n, ∃ term : PauliTerm n,
      canonicalHamiltonianTermFamily hN i = term := by
  intro i
  exact ⟨canonicalHamiltonianTermFamily hN i, rfl⟩

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
