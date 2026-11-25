import Formalism.GammaFactorNonvanishing.RhOfRight
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.ShapeOf
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopShape
import Development.AutomorphicArithmetic.CharacterBoxes.SupplyChi
import Development.WeilBound.CoreStatements.StandardPublishedResults.StandardTheoremStatements.GreenRegularCharacters
import Development.AbelianVarietyTheory.Proofs.InertiaEigenvalues.SumRangeEqRoots

/-!
The two inputs to the modulus-one branch, replayed against archive 6193bb5.
The cohomology budget supplies hosts. Green's compiled theorem and
the family bundle then connect those hosts into families with tied windows.

From the compiled archive project with Lean 4.33.1:
    lake env lean --tstack=400000 /path/to/rh_mod_one_input_cuts.lean
-/

open Formalism.BasicNotions Formalism.MainNotions Formalism.HC GlobalTheory.EX UpperTheory.Top

namespace ZetaInputs

abbrev Bundle : Prop :=
  Nonempty (GlobalTheory.Fc.HypsAlt (fun 𝒞 => Closed 𝒞 fun Fm _ => LinkN Fm)
    GlobalTheory.Fc.DefiniteSideCondition)

abbrev Hosts : Prop := HostExW (3 / 2) (GChi PChar.one).req

abbrev Connected : Prop := FamilyClassConnected ((GChi PChar.one).cls (3 / 2))

abbrev TiedWindows : Prop :=
  ChebyshevInequalityAtWindowScale
    (core := fun Fm : FamP _ => Fm.toFamCore) (Tied := fun Fm => ChainTied Fm)
    (3 / 2) (Level.cyc PChar.one)

/-- The budget is needed only for the modulus-one character. -/
theorem hosts_of_budget (hBudget : VWinAt PChar.one 401) : Hosts :=
  supplyChi PChar.one hBudget

/-- The bundle yields the comparison for this character once its hosts are supplied. -/
theorem connected_of_bundle (hBundle : Bundle) (hHosts : Hosts) : Connected := by
  obtain ⟨bundle⟩ := hBundle
  have hGreen := GlobalTheory.GreenBridge.green_of_regular
    PositivityTheory.Stage1.PM.greenRegularCharacters
  have hTop : TopG := GlobalTheory.Fc.forall_goal_of_shape_of_hyps _ _ _ _
    (shape_closed_link_n_of_green hGreen) trivial trivial bundle
  exact hTop (3 / 2) (GChi PChar.one) (by norm_num) hHosts (hypV_of_cls PChar.one (3 / 2))

/-- The comparison's output already contains the whole tied-window input. -/
theorem tied_windows_of_connected (hConnected : Connected) : TiedWindows := by
  obtain ⟨eD, eL, ε₁, hε₁, hFamily⟩ := hConnected
  refine ⟨eD, eL, ε₁, hε₁, fun eps h0 h1 => ?_⟩
  obtain ⟨Fm, hClass, hTie⟩ := hFamily eps h0 h1
  exact ⟨Fm, eFamC_of_cls PChar.one (3 / 2) Fm hClass, hClass.1, hTie⟩

theorem tied_windows_of_two_inputs (hBudget : VWinAt PChar.one 401) (hBundle : Bundle) :
    TiedWindows :=
  tied_windows_of_connected (connected_of_bundle hBundle (hosts_of_budget hBudget))

theorem rh_of_tied_windows (hTied : TiedWindows) : RiemannHypothesis := by
  have hOne : ZeroFreeOn (fun ψ => ψ = PChar.one) :=
    zeroFreeOn_of_tiedWin_cyc (Fam := FamP) (core := fun Fm => Fm.toFamCore)
      (Tied := fun Fm => ChainTied Fm) (by norm_num : (1 : ℝ) < 3 / 2)
      (fun ψ _ => UpperTheory.Comparison₂.level_gm_le_on_family_scales (Level.cyc ψ))
      (fun ψ _ => UpperTheory.Comparison₂.formB _) fun ψ hψ => by
        subst ψ
        exact hTied
  apply Formalism.VW.rh_of_right
  intro s hs _
  have hz := hOne PChar.one rfl s hs
  change DirichletCharacter.LFunction (1 : DirichletCharacter ℂ 1) s ≠ 0 at hz
  rwa [DirichletCharacter.LFunction_modOne_eq] at hz

/-- A modulus-one budget and the archived bundle imply RH with Green proved internally. -/
theorem rh_of_two_mod_one_inputs (hBudget : VWinAt PChar.one 401) (hBundle : Bundle) :
    RiemannHypothesis :=
  rh_of_tied_windows (tied_windows_of_two_inputs hBudget hBundle)

#print axioms hosts_of_budget
#print axioms connected_of_bundle
#print axioms tied_windows_of_two_inputs
#print axioms rh_of_two_mod_one_inputs

end ZetaInputs
