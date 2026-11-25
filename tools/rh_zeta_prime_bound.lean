import Formalism.GammaFactorNonvanishing.RhOfRight
import Development.AutomorphicArithmetic.DedekindLFunctions.LandauTheorems.ZeroFreeOfRpowWindow

/-!
The analytic finish for zeta alone, assuming a bound on a smoothed prime sum.
The only archive imports are RhOfRight and ZeroFreeOfRpowWindow.

Replay in the Lean archive project at 6193bb5 with Lean 4.33.1 and Mathlib
0df444a. The import closure contains 31 archive files.
    lake env lean /path/to/rh_zeta_prime_bound.lean
-/

private noncomputable def zetaFamily : Deduction.CharFamily where
  ι := Unit
  fin := inferInstance
  N := fun _ => 1
  nz := fun _ => inferInstance
  χ := fun _ => 1
  a := fun _ => 1
  a_pos := fun _ => zero_lt_one
  adm := fun _ => Or.inl rfl

private theorem zetaFamily_Gm (y : ℝ) : Deduction.Gm zetaFamily y = Deduction.G y := by
  have hχ (n : ℕ) : (1 : DirichletCharacter ℂ 1) (n : ZMod 1) = 1 := by
    rw [Subsingleton.elim (n : ZMod 1) 1, map_one]
  classical
  unfold Deduction.Gm
  change (∑ _i : Unit, (1 : ℝ) * (Deduction.Gchi (1 : DirichletCharacter ℂ 1) y).re) =
    Deduction.G y
  rw [Fintype.sum_unique, one_mul]
  unfold Deduction.Gchi
  rw [if_pos rfl]
  simp only [hχ, Complex.sub_re, Complex.add_re, Complex.ofReal_re, Deduction.G]

/-- Upper bounds for one smoothed prime sum on arbitrarily large power windows suffice. -/
theorem rh_of_zeta_prime_bound
    (h : ∀ θ : ℝ, 1 / 2 < θ → θ < 1 → ∀ Y₀ : ℝ,
      ∃ Y : ℝ, Y₀ ≤ Y ∧ ∀ y ∈ Set.Icc Y (Y ^ (3 / 2 : ℝ)), Deduction.G y ≤ y ^ θ) :
    RiemannHypothesis := by
  apply Formalism.VW.rh_of_right
  intro s hs _
  let θ : ℝ := (1 / 2 + min s.re 1) / 2
  have hm : (1 / 2 : ℝ) < min s.re 1 := lt_min hs (by norm_num)
  have hθ : 1 / 2 < θ := by dsimp [θ]; linarith
  have hθ1 : θ < 1 := by dsimp [θ]; linarith [min_le_right s.re 1]
  have hθs : θ < s.re := by dsimp [θ]; linarith [min_le_left s.re 1]
  have hδ : (0 : ℝ) < 1 / 2 := by norm_num
  have hfree := Deduction.zeroFree_of_rpow_window zetaFamily
    (by linarith : 0 < θ) hθ1 hδ (C := 1) fun Y₀ => by
      obtain ⟨Y, hY, hbound⟩ := h θ hθ hθ1 Y₀
      refine ⟨Y, hY, fun y hy => ?_⟩
      rw [zetaFamily_Gm, one_mul]
      apply hbound y
      convert hy using 1
      norm_num
  have hz := hfree () s hθs
  change DirichletCharacter.LFunction (1 : DirichletCharacter ℂ 1) s ≠ 0 at hz
  rwa [DirichletCharacter.LFunction_modOne_eq] at hz

#print axioms rh_of_zeta_prime_bound
