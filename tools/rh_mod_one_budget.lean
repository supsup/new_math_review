import Formalism.GammaFactorNonvanishing.RhOfRight
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.ShapeOf
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopShape
import Development.AutomorphicArithmetic.CharacterBoxes.SupplyChi

/-!
A conditional route to the Riemann Hypothesis using the archive's modulus-one
character. `VWin` supplies a weighted-length bound for every primitive
character. This proof assumes just `VWinAt PChar.one 401`, alongside the
archived Green statement and the same family bundle as the general route.

Replay in the compiled archive project at revision 6193bb5 with Lean 4.33.1.
    lake env lean /path/to/rh_mod_one_budget.lean
-/

open Formalism.BasicNotions Formalism.MainNotions Formalism.HC GlobalTheory.EX
open UpperTheory.Top

private theorem zero_free_mod_one_of_topG (hTop : TopG)
    (hHost : HostExW (3 / 2) (GChi PChar.one).req) : PChar.one.ZeroFreeAbove (1 / 2) := by
  have hScale : (1 : ℝ) < 3 / 2 := by norm_num
  -- The zero-free comparison can be run on a single-character class.
  have hOne : ZeroFreeOn (fun ψ => ψ = PChar.one) :=
    zeroFreeOn_of_tiedWin_cyc (Fam := FamP) (core := fun Fm => Fm.toFamCore)
      (Tied := fun Fm => ChainTied Fm) hScale
      (fun ψ _ => UpperTheory.Comparison₂.level_gm_le_on_family_scales _)
      (fun ψ _ => UpperTheory.Comparison₂.formB _) fun ψ hψ => by
        subst ψ
        obtain ⟨eD, eL, ε₁, hFirst, hFamily⟩ :=
          hTop (3 / 2) (GChi PChar.one) hScale hHost (hypV_of_cls PChar.one (3 / 2))
        refine ⟨eD, eL, ε₁, hFirst, fun eps a b => ?_⟩
        obtain ⟨Fm, hClass, hTied⟩ := hFamily eps a b
        exact ⟨Fm, eFamC_of_cls PChar.one (3 / 2) Fm hClass, hClass.1, hTied⟩
  exact hOne PChar.one rfl

theorem rh_with_mod_one_budget (hGreen : GlobalTheory.GLq.Green)
    (hBudget : VWinAt PChar.one 401)
    (hBundle : Nonempty (GlobalTheory.Fc.HypsAlt (fun 𝒞 => Closed 𝒞 fun Fm _ => LinkN Fm)
          GlobalTheory.Fc.DefiniteSideCondition)) : RiemannHypothesis := by
  -- Green and the bundle give the connected family comparison.
  rcases hBundle with ⟨bundle⟩
  have hTop : TopG := GlobalTheory.Fc.forall_goal_of_shape_of_hyps _ _ _ _
    (shape_closed_link_n_of_green hGreen) trivial trivial bundle
  -- The budget supplies a host for the one character the zeta function uses.
  have hHost := supplyChi PChar.one hBudget
  have hFree := zero_free_mod_one_of_topG hTop hHost
  -- Its L-function is the zeta function. The symmetry step finishes RH.
  apply Formalism.VW.rh_of_right
  intro s hs _
  have hz := hFree s hs
  change DirichletCharacter.LFunction (1 : DirichletCharacter ℂ 1) s ≠ 0 at hz
  rwa [DirichletCharacter.LFunction_modOne_eq] at hz

#print axioms rh_with_mod_one_budget
