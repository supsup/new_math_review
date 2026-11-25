import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.Tactic

/-!
A finite part of Li's criterion. A point on the critical line maps to
the unit circle under w = (ρ - 1) / ρ, so its conjugate pair contributes
a nonnegative term for every power. A synthetic off-line quartet can
give a negative contribution already at power four.

Replay in a Lean 4.33.1 Mathlib project:
    lake env lean /path/to/li_pair_positivity.lean
-/

open Complex

namespace LiPairs

noncomputable section

def liMap (ρ : ℂ) : ℂ := (ρ - 1) / ρ

theorem liMap_conj (ρ : ℂ) :
    liMap ((starRingEnd ℂ) ρ) = (starRingEnd ℂ) (liMap ρ) := by
  simp [liMap, map_div₀]

theorem liMap_reflect (ρ : ℂ) : liMap (1 - ρ) = (liMap ρ)⁻¹ := by
  unfold liMap
  rw [inv_div, show 1 - ρ - 1 = -ρ by ring]
  calc
    -ρ / (1 - ρ) = -ρ / -(ρ - 1) := by congr 1; ring
    _ = _ := by rw [div_neg, neg_div, neg_neg]

theorem liMap_norm_on_line {ρ : ℂ} (hline : ρ.re = 1 / 2) : ‖liMap ρ‖ = 1 := by
  have hρ : ρ ≠ 0 := by
    intro hz
    rw [hz] at hline
    norm_num at hline
  have hsub : ρ - 1 = -(starRingEnd ℂ) ρ := by
    apply Complex.ext
    · simp only [sub_re, one_re, neg_re, conj_re, hline]
      norm_num
    · simp
  rw [liMap, hsub, norm_div, norm_neg, norm_conj, div_self (norm_ne_zero_iff.mpr hρ)]

def pairContribution (ρ : ℂ) (n : ℕ) : ℝ :=
  ((1 - (liMap ρ) ^ n) + (1 - (liMap ((starRingEnd ℂ) ρ)) ^ n)).re

theorem pairContribution_eq (ρ : ℂ) (n : ℕ) :
    pairContribution ρ n = 2 * (1 - ((liMap ρ) ^ n).re) := by
  rw [pairContribution, liMap_conj, ← map_pow]
  simp only [add_re, sub_re, one_re, conj_re]
  ring

theorem pairContribution_nonneg {ρ : ℂ} (hline : ρ.re = 1 / 2) (n : ℕ) :
    0 ≤ pairContribution ρ n := by
  have hnorm : ‖(liMap ρ) ^ n‖ = 1 := by
    rw [norm_pow, liMap_norm_on_line hline, one_pow]
  have hre : ((liMap ρ) ^ n).re ≤ 1 := hnorm ▸ re_le_norm ((liMap ρ) ^ n)
  rw [pairContribution_eq]
  linarith

/-- Applying RH to a nontrivial zero makes its conjugate pair nonnegative. -/
theorem zetaPairContribution_nonneg (rh : RiemannHypothesis) {ρ : ℂ}
    (hz : riemannZeta ρ = 0) (hn : ¬∃ n : ℕ, ρ = -2 * (n + 1)) (h1 : ρ ≠ 1) (n : ℕ) :
    0 ≤ pairContribution ρ n :=
  pairContribution_nonneg (rh ρ hz hn h1) n

theorem pairContribution_one {ρ : ℂ} (hline : ρ.re = 1 / 2) :
    pairContribution ρ 1 = 1 / (1/4 + ρ.im ^ 2) := by
  have hρ : ρ ≠ 0 := by intro hz; rw [hz] at hline; norm_num at hline
  have hmap : liMap ρ = 1 - ρ⁻¹ := by rw [liMap, sub_div, div_self hρ, one_div]
  rw [pairContribution_eq, pow_one, hmap, sub_re, one_re, Complex.inv_re]
  unfold Complex.normSq
  simp [hline, pow_two]
  ring

def unitExample : ℂ := ⟨1/2, 1/2⟩
def offExample : ℂ := ⟨4/5, 2/5⟩

theorem unitExample_map : liMap unitExample = I := by
  have hρ : unitExample ≠ 0 := by intro h; have := congrArg Complex.re h; norm_num [unitExample] at this
  rw [liMap, div_eq_iff hρ]
  apply Complex.ext <;> norm_num [unitExample, sub_re, sub_im, mul_re, mul_im]

theorem offExample_map : liMap offExample = (1/2)*I := by
  have hρ : offExample ≠ 0 := by intro h; have := congrArg Complex.re h; norm_num [offExample] at this
  rw [liMap, div_eq_iff hρ]
  apply Complex.ext <;> norm_num [offExample, sub_re, sub_im, mul_re, mul_im]

theorem offExample_reflect_map : liMap (1 - offExample) = -2*I := by
  have hρ : 1 - offExample ≠ 0 := by
    intro h
    have := congrArg Complex.re h
    norm_num [offExample, sub_re] at this
  rw [liMap, div_eq_iff hρ]
  apply Complex.ext <;> norm_num [offExample, sub_re, sub_im, mul_re, mul_im]

theorem offExample_fourth :
    pairContribution offExample 4 + pairContribution (1 - offExample) 4 = -225/8 := by
  rw [pairContribution_eq, pairContribution_eq, offExample_map, offExample_reflect_map,
    mul_pow, mul_pow, Complex.I_pow_four, mul_one, mul_one]
  norm_num

#print axioms zetaPairContribution_nonneg
#print axioms pairContribution_one
#print axioms offExample_fourth

end

end LiPairs
