import B9.ClusterStabilizer.PauliBasisAction

namespace B9

open ClusterStabilizer

def BasisAction.compose {n : Nat} (first second : BasisAction n) : BasisAction n :=
  { phase := first.phase.mul second.phase, state := second.state }

def BasisAction.identity {n : Nat} (state : BasisState n) : BasisAction n :=
  { phase := .plus, state := state }

theorem phase_mul_assoc (a b c : Phase) :
    (a.mul b).mul c = a.mul (b.mul c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem basis_action_compose_assoc
    {n : Nat} (first second third : BasisAction n) :
    (first.compose second).compose third = first.compose (second.compose third) := by
  cases first with
  | mk firstPhase firstState =>
      cases second with
      | mk secondPhase secondState =>
          cases third with
          | mk thirdPhase thirdState =>
              cases firstPhase <;> cases secondPhase <;> cases thirdPhase <;> rfl

theorem basis_action_compose_identity_right
    {n : Nat} (action : BasisAction n) :
    action.compose (BasisAction.identity action.state) = action := by
  cases action with
  | mk phase state =>
      cases phase <;> rfl

theorem pauli_term_basis_action_cons_compose
    {n : Nat} (factor : PauliFactor n) (rest : List (PauliFactor n))
    (state : BasisState n) :
    (PauliTerm.mk (factor :: rest)).basisAction state =
      (factor.act state).compose ((PauliTerm.mk rest).basisAction (factor.act state).state) := by
  simp [PauliTerm.basisAction, BasisAction.compose]

theorem pauli_term_basis_action_append
    {n : Nat} (left right : PauliTerm n) (state : BasisState n) :
    (PauliTerm.mk (left.factors ++ right.factors)).basisAction state =
      (left.basisAction state).compose
        (right.basisAction (left.basisAction state).state) := by
  cases left with
  | mk leftFactors =>
      induction leftFactors generalizing state with
      | nil =>
          simp [PauliTerm.basisAction, BasisAction.compose, Phase.mul]
      | cons factor rest ih =>
          simp only [List.cons_append, pauli_term_basis_action_cons_compose]
          rw [ih]
          simpa [BasisAction.compose] using
            (basis_action_compose_assoc (factor.act state)
              ((PauliTerm.mk rest).basisAction (factor.act state).state)
              (right.basisAction ((PauliTerm.mk rest).basisAction (factor.act state).state).state)).symm

theorem pauli_term_basis_action_append_locality
    {n : Nat} (left right : PauliTerm n) (state : BasisState n) :
    BasisState.agreesOutside (left.siteSupport ++ right.siteSupport) state
      ((PauliTerm.mk (left.factors ++ right.factors)).basisAction state).state := by
  rw [pauli_term_basis_action_append]
  intro j hNotMem
  have hLeft : j ∉ left.siteSupport := by
    intro hMem
    apply hNotMem
    simp [hMem]
  have hRight : j ∉ right.siteSupport := by
    intro hMem
    apply hNotMem
    simp [hMem]
  have hFirst := pauli_term_basis_action_agrees_outside left state j hLeft
  have hSecond := pauli_term_basis_action_agrees_outside right
    (left.basisAction state).state j hRight
  exact hFirst.trans hSecond

end B9
