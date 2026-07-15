import B9.ClusterStabilizer.WidthLocality

namespace B9

open ClusterStabilizer

def BasisState (n : Nat) := Fin n -> Bool

inductive Phase where
  | plus
  | minus
deriving DecidableEq, Repr

def Phase.mul : Phase -> Phase -> Phase
  | .plus, value => value
  | .minus, .plus => .minus
  | .minus, .minus => .plus

structure BasisAction (n : Nat) where
  phase : Phase
  state : BasisState n

def flipAt {n : Nat} (state : BasisState n) (site : Fin n) : BasisState n :=
  fun j => if j = site then !state j else state j

def Phase.ofBit : Bool -> Phase
  | false => .plus
  | true => .minus

def PauliFactor.act {n : Nat} (factor : PauliFactor n) (state : BasisState n) : BasisAction n :=
  match factor.axis with
  | .x => { phase := .plus, state := flipAt state factor.site }
  | .z => { phase := Phase.ofBit (state factor.site), state := state }

def PauliTerm.basisAction {n : Nat} : PauliTerm n -> BasisState n -> BasisAction n
  | { factors := [] }, state => { phase := .plus, state := state }
  | { factors := factor :: rest }, state =>
      let first := factor.act state
      let tail := (PauliTerm.mk rest).basisAction first.state
      { phase := first.phase.mul tail.phase, state := tail.state }

def BasisState.agreesOutside {n : Nat} (sites : List (Fin n))
    (before after : BasisState n) : Prop :=
  forall j, j ∉ sites -> before j = after j

def PauliTerm.siteSupport {n : Nat} (term : PauliTerm n) : List (Fin n) :=
  term.factors.map PauliFactor.site

theorem pauli_factor_act_agrees_outside
    {n : Nat} (factor : PauliFactor n) (state : BasisState n) :
    BasisState.agreesOutside [factor.site] state (factor.act state).state := by
  cases factor with
  | mk site axis =>
      cases axis with
      | x =>
          intro j hNotMem
          have hNe : j ≠ site := by simpa using hNotMem
          simp [BasisState.agreesOutside, PauliFactor.act, flipAt, hNe]
      | z =>
          intro j _hNotMem
          rfl

theorem pauli_term_basis_action_empty
    {n : Nat} (state : BasisState n) :
    (PauliTerm.mk []).basisAction state = { phase := .plus, state := state } := by
  simp [PauliTerm.basisAction]

theorem pauli_term_basis_action_cons
    {n : Nat} (factor : PauliFactor n) (rest : List (PauliFactor n))
    (state : BasisState n) :
    (PauliTerm.mk (factor :: rest)).basisAction state =
      let first := factor.act state
      let tail := (PauliTerm.mk rest).basisAction first.state
      { phase := first.phase.mul tail.phase, state := tail.state } := by
  simp [PauliTerm.basisAction]

theorem pauli_term_basis_action_agrees_outside
    {n : Nat} (term : PauliTerm n) (state : BasisState n) :
    BasisState.agreesOutside term.siteSupport state (term.basisAction state).state := by
  cases term with
  | mk factors =>
      induction factors generalizing state with
      | nil =>
          intro j _hNotMem
          simp [PauliTerm.siteSupport, PauliTerm.basisAction]
      | cons factor rest ih =>
          intro j hNotMem
          have hSite : j ≠ factor.site := by
            intro hEq
            apply hNotMem
            simp [PauliTerm.siteSupport, hEq]
          have hRest : j ∉ (rest.map PauliFactor.site) := by
            intro hMem
            apply hNotMem
            simp [PauliTerm.siteSupport, hMem]
          have hFirst : state j = (factor.act state).state j := by
            exact pauli_factor_act_agrees_outside factor state j (by simp [hSite])
          have hTail := ih (state := (factor.act state).state) j hRest
          simpa [PauliTerm.siteSupport, PauliTerm.basisAction] using hFirst.trans hTail

theorem pauli_term_basis_action_is_total
    {n : Nat} (term : PauliTerm n) :
    forall state : BasisState n, exists action : BasisAction n,
      term.basisAction state = action := by
  intro state
  exact ⟨term.basisAction state, rfl⟩

end B9
