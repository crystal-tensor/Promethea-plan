import B9.ClusterStabilizer.PauliActionCommutation

namespace B9

open ClusterStabilizer

def PauliFactor.disjointTerm {n : Nat} (factor : PauliFactor n)
    (term : PauliTerm n) : Prop :=
  forall site, site ∈ term.siteSupport -> factor.site ≠ site

theorem pauli_factor_term_disjoint_commute
    {n : Nat} (factor : PauliFactor n) (term : PauliTerm n)
    (hDisjoint : factor.disjointTerm term) (state : BasisState n) :
    (factor.act state).compose
        (term.basisAction (factor.act state).state) =
      (term.basisAction state).compose
        (factor.act (term.basisAction state).state) := by
  cases term with
  | mk factors =>
      induction factors generalizing state with
      | nil =>
          cases hPhase : (factor.act state).phase <;>
            simp [PauliFactor.disjointTerm, PauliTerm.siteSupport,
              PauliTerm.basisAction, BasisAction.compose, Phase.mul, hPhase]
      | cons head tail ih =>
          have hHead : factor.site ≠ head.site := by
            apply hDisjoint head.site
            simp [PauliFactor.disjointTerm, PauliTerm.siteSupport]
          have hTail : factor.disjointTerm (PauliTerm.mk tail) := by
            intro site hSite
            apply hDisjoint site
            simpa [PauliTerm.siteSupport] using
              (List.mem_cons_of_mem head.site hSite)
          have hSwap := pauli_factor_act_disjoint_commute factor head hHead state
          have hTailSwap := ih (state := (head.act state).state) hTail
          have hStateSwap := congrArg BasisAction.state hSwap
          have hTailInput := congrArg
            (fun state : BasisState n => (PauliTerm.mk tail).basisAction state)
            (by simpa [BasisAction.compose] using hStateSwap)
          have hTailAction :
              (PauliTerm.mk tail).basisAction
                  (head.act (factor.act state).state).state =
                (PauliTerm.mk tail).basisAction
                  (factor.act (head.act state).state).state := by
            simpa only using hTailInput
          calc
            (factor.act state).compose
                ((PauliTerm.mk (head :: tail)).basisAction
                  (factor.act state).state) =
                (factor.act state).compose
                  ((head.act (factor.act state).state).compose
                    ((PauliTerm.mk tail).basisAction
                      (head.act (factor.act state).state).state)) := by
              rw [pauli_term_basis_action_cons_compose]
            _ = ((factor.act state).compose
                  (head.act (factor.act state).state)).compose
                    ((PauliTerm.mk tail).basisAction
                      (head.act (factor.act state).state).state) := by
              rw [← basis_action_compose_assoc]
            _ = ((head.act state).compose
                  (factor.act (head.act state).state)).compose
                    ((PauliTerm.mk tail).basisAction
                      (head.act (factor.act state).state).state) := by
              rw [hSwap]
            _ = ((head.act state).compose
                  (factor.act (head.act state).state)).compose
                    ((PauliTerm.mk tail).basisAction
                      (factor.act (head.act state).state).state) := by
              rw [hTailAction]
            _ = (head.act state).compose
                  ((factor.act (head.act state).state).compose
                    ((PauliTerm.mk tail).basisAction
                      (factor.act (head.act state).state).state)) := by
              rw [basis_action_compose_assoc]
            _ = (head.act state).compose
                  (((PauliTerm.mk tail).basisAction
                      (head.act state).state).compose
                    (factor.act
                      ((PauliTerm.mk tail).basisAction
                        (head.act state).state).state)) := by
              rw [hTailSwap]
            _ = ((head.act state).compose
                  ((PauliTerm.mk tail).basisAction (head.act state).state)).compose
                    (factor.act
                      ((PauliTerm.mk tail).basisAction
                        (head.act state).state).state) := by
              rw [← basis_action_compose_assoc]
            _ = ((PauliTerm.mk (head :: tail)).basisAction state).compose
                  (factor.act
                    ((PauliTerm.mk (head :: tail)).basisAction state).state) := by
              simp [pauli_term_basis_action_cons_compose, BasisAction.compose]

theorem pauli_term_basis_action_disjoint_commute
    {n : Nat} (left right : PauliTerm n)
    (hDisjoint : forall leftSite, leftSite ∈ left.siteSupport ->
      forall rightSite, rightSite ∈ right.siteSupport -> leftSite ≠ rightSite)
    (state : BasisState n) :
    (PauliTerm.mk (left.factors ++ right.factors)).basisAction state =
      (PauliTerm.mk (right.factors ++ left.factors)).basisAction state := by
  cases left with
  | mk leftFactors =>
      cases right with
      | mk rightFactors =>
          induction leftFactors generalizing state with
          | nil =>
              simp [PauliTerm.basisAction]
          | cons head leftTail ih =>
              have hHead : head.disjointTerm (PauliTerm.mk rightFactors) := by
                intro site hSite
                apply hDisjoint head.site
                · simp [PauliTerm.siteSupport]
                · exact hSite
              have hTail : forall leftSite, leftSite ∈
                  (PauliTerm.mk leftTail).siteSupport ->
                  forall rightSite, rightSite ∈
                    (PauliTerm.mk rightFactors).siteSupport -> leftSite ≠ rightSite := by
                intro leftSite hLeftSite rightSite hRightSite
                apply hDisjoint leftSite
                · simpa [PauliTerm.siteSupport] using
                    (List.mem_cons_of_mem head.site hLeftSite)
                · exact hRightSite
              have hFactor := pauli_factor_term_disjoint_commute
                head (PauliTerm.mk rightFactors) hHead state
              have hFactorTailInput := congrArg
                (fun action : BasisAction n =>
                  (PauliTerm.mk leftTail).basisAction action.state)
                hFactor
              have hFactorTailAction :
                  (PauliTerm.mk leftTail).basisAction
                      ((PauliTerm.mk rightFactors).basisAction
                        (head.act state).state).state =
                    (PauliTerm.mk leftTail).basisAction
                      (head.act
                        ((PauliTerm.mk rightFactors).basisAction state).state).state := by
                simpa [BasisAction.compose] using hFactorTailInput
              have hInnerAction :
                  ((PauliTerm.mk leftTail).basisAction (head.act state).state).compose
                      ((PauliTerm.mk rightFactors).basisAction
                        ((PauliTerm.mk leftTail).basisAction (head.act state).state).state) =
                    ((PauliTerm.mk rightFactors).basisAction (head.act state).state).compose
                      ((PauliTerm.mk leftTail).basisAction
                        ((PauliTerm.mk rightFactors).basisAction
                          (head.act state).state).state) := by
                calc
                  _ = (PauliTerm.mk (leftTail ++ rightFactors)).basisAction
                        (head.act state).state := by
                    rw [pauli_term_basis_action_append]
                  _ = (PauliTerm.mk (rightFactors ++ leftTail)).basisAction
                        (head.act state).state := ih (head.act state).state hTail
                  _ = _ := by
                    rw [pauli_term_basis_action_append]
              calc
                (PauliTerm.mk ((head :: leftTail) ++ rightFactors)).basisAction state =
                    ((PauliTerm.mk (head :: leftTail)).basisAction state).compose
                      ((PauliTerm.mk rightFactors).basisAction
                        ((PauliTerm.mk (head :: leftTail)).basisAction state).state) := by
                  rw [pauli_term_basis_action_append]
                _ = ((head.act state).compose
                      ((PauliTerm.mk leftTail).basisAction (head.act state).state)).compose
                    ((PauliTerm.mk rightFactors).basisAction
                      ((head.act state).compose
                        ((PauliTerm.mk leftTail).basisAction (head.act state).state)).state) := by
                  rw [pauli_term_basis_action_cons_compose]
                _ = (head.act state).compose
                    (((PauliTerm.mk leftTail).basisAction (head.act state).state).compose
                      ((PauliTerm.mk rightFactors).basisAction
                        ((PauliTerm.mk leftTail).basisAction (head.act state).state).state)) := by
                  rw [basis_action_compose_assoc]
                  simp only [BasisAction.compose]
                _ = (head.act state).compose
                    (((PauliTerm.mk rightFactors).basisAction (head.act state).state).compose
                      ((PauliTerm.mk leftTail).basisAction
                        ((PauliTerm.mk rightFactors).basisAction
                          (head.act state).state).state)) := by
                  rw [hInnerAction]
                _ = ((head.act state).compose
                      ((PauliTerm.mk rightFactors).basisAction (head.act state).state)).compose
                    ((PauliTerm.mk leftTail).basisAction
                      ((PauliTerm.mk rightFactors).basisAction
                        (head.act state).state).state) := by
                  rw [← basis_action_compose_assoc]
                _ = ((PauliTerm.mk rightFactors).basisAction state).compose
                    ((head.act ((PauliTerm.mk rightFactors).basisAction state).state).compose
                      ((PauliTerm.mk leftTail).basisAction
                        ((PauliTerm.mk rightFactors).basisAction
                          (head.act state).state).state)) := by
                  rw [← basis_action_compose_assoc]
                  rw [hFactor]
                _ = ((PauliTerm.mk rightFactors).basisAction state).compose
                    ((head.act ((PauliTerm.mk rightFactors).basisAction state).state).compose
                      ((PauliTerm.mk leftTail).basisAction
                        ((head.act ((PauliTerm.mk rightFactors).basisAction state).state).state))) := by
                  rw [hFactorTailAction]
                _ = ((PauliTerm.mk rightFactors).basisAction state).compose
                    ((PauliTerm.mk (head :: leftTail)).basisAction
                      ((PauliTerm.mk rightFactors).basisAction state).state) := by
                  simp [pauli_term_basis_action_cons_compose, BasisAction.compose]
                _ = (PauliTerm.mk (rightFactors ++ (head :: leftTail))).basisAction state := by
                  rw [pauli_term_basis_action_append]

end B9
