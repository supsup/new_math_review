import Mathlib

/-!
Two algebraic identities for the finite quartet filter. An included
unit-circle pair is killed by its quadratic. The final factor makes the
centered value purely imaginary, giving a negative quartet form.
-/

namespace LiQuartetFilter

open Complex

theorem pair_factor_zero (v : ℂ) (k : ℝ) (hv : v ≠ 0)
    (h : v + v⁻¹ = (k : ℂ) / 2) :
    2 * v^2 - (k : ℂ) * v + 2 = 0 := by
  calc
    2 * v^2 - (k : ℂ) * v + 2 = 2 * v * v + 2 * (v * v⁻¹) - (k : ℂ) * v := by
      rw [mul_inv_cancel₀ hv]
      ring
    _ = 2 * v * (v + v⁻¹ - (k : ℂ) / 2) := by ring
    _ = 0 := by rw [h, sub_self, mul_zero]

def centered (a b : ℝ) : ℂ :=
  ((a : ℂ) + (b : ℂ) * I) * (-(3 : ℂ) * (b : ℂ) - (3 : ℂ) * (a : ℂ) * I)

theorem centered_eq (a b : ℝ) :
    centered a b = -(3 : ℂ) * ((a : ℂ)^2 + (b : ℂ)^2) * I := by
  apply Complex.ext <;> simp [centered, pow_two, Complex.mul_re, Complex.mul_im] <;> ring

theorem quartet_value (a b : ℝ) :
    4 * (((2 : ℂ) + (3 / 2 : ℂ) * I) * (centered a b)^2).re =
      -72 * (a^2 + b^2)^2 := by
  rw [centered_eq]
  simp [pow_two, Complex.mul_re, Complex.mul_im]
  ring

theorem quartet_negative (a b : ℝ) (h : a ≠ 0 ∨ b ≠ 0) :
    4 * (((2 : ℂ) + (3 / 2 : ℂ) * I) * (centered a b)^2).re < 0 := by
  rw [quartet_value]
  have hab : 0 < a^2 + b^2 := by
    rcases h with h | h
    · exact add_pos_of_pos_of_nonneg (sq_pos_of_ne_zero h) (sq_nonneg b)
    · exact add_pos_of_nonneg_of_pos (sq_nonneg a) (sq_pos_of_ne_zero h)
  exact mul_neg_of_neg_of_pos (by norm_num) (pow_pos hab _)

#print axioms pair_factor_zero
#print axioms quartet_negative

end LiQuartetFilter
