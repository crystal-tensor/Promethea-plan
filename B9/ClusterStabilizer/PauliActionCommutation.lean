import B9.ClusterStabilizer.PauliActionComposition

namespace B9

open ClusterStabilizer

theorem flipAt_commute
    {n : Nat} (state : BasisState n) (firstSite secondSite : Fin n)
    (hSite : firstSite ≠ secondSite) :
    flipAt (flipAt state firstSite) secondSite =
      flipAt (flipAt state secondSite) firstSite := by
  funext j
  by_cases hFirst : j = firstSite
  · subst j
    simp [flipAt, hSite, Ne.symm hSite]
  · by_cases hSecond : j = secondSite
    · subst j
      simp [flipAt, hSite, Ne.symm hSite]
    · simp [flipAt, hFirst, hSecond]

theorem phase_mul_comm (first second : Phase) :
    first.mul second = second.mul first := by
  cases first <;> cases second <;> rfl

theorem pauli_factor_act_disjoint_commute
    {n : Nat} (first second : PauliFactor n)
    (hSite : first.site ≠ second.site) (state : BasisState n) :
    (first.act state).compose (second.act (first.act state).state) =
      (second.act state).compose (first.act (second.act state).state) := by
  cases first with
  | mk firstSite firstAxis =>
      cases second with
      | mk secondSite secondAxis =>
          have hNe : firstSite ≠ secondSite := by simpa using hSite
          cases firstAxis <;> cases secondAxis
          · simp [PauliFactor.act, BasisAction.compose]
            rw [flipAt_commute state firstSite secondSite hNe]
          · cases hBit : state secondSite <;>
              simp [PauliFactor.act, BasisAction.compose, Phase.ofBit, Phase.mul,
                flipAt, hNe, Ne.symm hNe, hBit]
          · cases hBit : state firstSite <;>
              simp [PauliFactor.act, BasisAction.compose, Phase.ofBit, Phase.mul,
                flipAt, hNe, Ne.symm hNe, hBit]
          · simp [PauliFactor.act, BasisAction.compose, Phase.ofBit, phase_mul_comm]

theorem pauli_factor_act_disjoint_state_commute
    {n : Nat} (first second : PauliFactor n)
    (hSite : first.site ≠ second.site) (state : BasisState n) :
    (second.act (first.act state).state).state =
      (first.act (second.act state).state).state := by
  have hAction := pauli_factor_act_disjoint_commute first second hSite state
  simpa [BasisAction.compose] using congrArg BasisAction.state hAction

theorem pauli_factor_act_disjoint_phase_commute
    {n : Nat} (first second : PauliFactor n)
    (hSite : first.site ≠ second.site) (state : BasisState n) :
    ((first.act state).phase).mul (second.act (first.act state).state).phase =
      ((second.act state).phase).mul (first.act (second.act state).state).phase := by
  have hAction := pauli_factor_act_disjoint_commute first second hSite state
  simpa [BasisAction.compose] using congrArg BasisAction.phase hAction

end B9
