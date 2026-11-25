import Formalism.GammaFactorNonvanishing.RhOfRight
import Formalism.SharpRestriction.RamificationFrobenius.TotientGaloisClasses.TopWin
import Development.AutomorphicArithmetic.PrimitiveCosets.LevelGmLeOnFamilyScales
import Development.AutomorphicArithmetic.PrimitiveCosets.Imports

/-!
The tied-family stop along the archived proof: this file keeps the comparison
and analytic finish, and assumes the specific family needed for zeta.

Replay in the Lean archive project at 6193bb5 with Lean 4.33.1 and Mathlib
0df444a. The import closure contains 408 archive files.
    lake env lean /path/to/rh_mod_one_tied_windows.lean
-/

open Formalism.BasicNotions Formalism.MainNotions Formalism.HC

/--
To finish the archive's proof for zeta alone, it suffices to construct tied
families at scale 3/2 for the modulus-one character. For each sufficiently
small positive epsilon the hypothesis provides a family realizing the
character, with large windows and a tied comparison on those windows.
-/
theorem rh_of_mod_one_tied_windows
    (hFamilies : ChebyshevInequalityAtWindowScale
      (core := fun Fm : FamP _ => Fm.toFamCore) (Tied := fun Fm => ChainTied Fm)
      (3 / 2) (Level.cyc PChar.one)) : RiemannHypothesis := by
  have hScale : (1 : ℝ) < 3 / 2 := by norm_num
  have hOne : ZeroFreeOn (fun ψ => ψ = PChar.one) :=
    zeroFreeOn_of_tiedWin_cyc (Fam := FamP) (core := fun Fm => Fm.toFamCore)
      (Tied := fun Fm => ChainTied Fm) hScale
      (fun ψ _ => UpperTheory.Comparison₂.level_gm_le_on_family_scales (Level.cyc ψ))
      (fun ψ _ => UpperTheory.Comparison₂.formB _) fun ψ hψ => by
        subst ψ
        exact hFamilies
  apply Formalism.VW.rh_of_right
  intro s hs _
  have hz := hOne PChar.one rfl s hs
  change DirichletCharacter.LFunction (1 : DirichletCharacter ℂ 1) s ≠ 0 at hz
  rwa [DirichletCharacter.LFunction_modOne_eq] at hz

#print axioms rh_of_mod_one_tied_windows

private theorem modOneKept : (Level.cyc PChar.one).KEPT = {PChar.one} := by
  classical
  ext ψ
  rw [Level.cyc, Level.mem_ofSub]
  have hχ : PChar.one.χ = 1 := rfl
  rw [hχ, Subgroup.zpowers_one_eq_bot]
  simp only [Subgroup.mem_bot, Finset.mem_singleton]
  constructor
  · rintro ⟨_, rfl, h⟩
    rw [PChar.of_one] at h
    exact h.symm
  · rintro rfl
    exact ⟨1, rfl, PChar.of_one _⟩

private theorem modOneGm (x : ℝ) : (Level.cyc PChar.one).Gm x = Formalism.Gz x := by
  classical
  simp [Level.Gm, Level.Nt, modOneKept]


/-- The archived tied family supplies the exact analytic prime-window bound. -/
theorem mod_one_tied_windows_give_prime_bound
    (hFamilies : ChebyshevInequalityAtWindowScale
      (core := fun Fm : FamP _ => Fm.toFamCore) (Tied := fun Fm => ChainTied Fm)
      (3 / 2) (Level.cyc PChar.one)) :
    ∀ θ : ℝ, 1 / 2 < θ → θ < 1 → ∀ Y₀ : ℝ,
      ∃ Y : ℝ, Y₀ ≤ Y ∧ ∀ y ∈ Set.Icc Y (Y ^ (3 / 2 : ℝ)), Deduction.G y ≤ y ^ θ := by
  intro θ hθ _ Y₀
  obtain ⟨eD, eL, ε₁, hε₁, hFamilies⟩ := hFamilies
  obtain ⟨ε, hε0, hεlt, hMargin⟩ :=
    exists_small_eps (eD + eL + 7) (sub_pos.mpr hθ) hε₁
  obtain ⟨Fm, hE, hW, hT⟩ := hFamilies ε hε0 hεlt
  obtain ⟨x₁, hBound⟩ := UpperTheory.Comparison₂.level_gm_le_on_family_scales
    (Level.cyc PChar.one) eD eL ε hε0 Fm hE hT
  obtain ⟨Y, hY, hWindow⟩ := hW (max (max Y₀ x₁) 1)
  have hY₀ := (le_max_left Y₀ x₁).trans ((le_max_left _ (1 : ℝ)).trans hY)
  have hY₁ := (le_max_right Y₀ x₁).trans ((le_max_left _ (1 : ℝ)).trans hY)
  have hOne := (le_max_right (max Y₀ x₁) (1 : ℝ)).trans hY
  refine ⟨Y, hY₀, fun y hy => ?_⟩
  rw [← (UpperTheory.Comparison₂.Gz_eq y).2, ← (UpperTheory.Comparison₂.Gz_eq y).1,
    ← modOneGm]
  exact (hBound y (hY₁.trans hy.1) (hWindow y hy.1 hy.2)).trans
    (Real.rpow_le_rpow_of_exponent_le (hOne.trans hy.1) (by linarith))

#print axioms mod_one_tied_windows_give_prime_bound
