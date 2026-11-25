import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic

/-!
A two-character mixture modulo five has weights u and v. The two characters
take values (I, -I, 1) and (-I, I, 1) at the arguments (2, 3, 6). Normalize
each coefficient by the leading coefficient u + v before multiplying.
-/

open Complex

theorem coefficient_six_defect (u v : ℂ) (hsum : u + v ≠ 0) :
    1 - ((I * (u - v)) / (u + v)) * ((-I * (u - v)) / (u + v)) =
      4 * u * v / (u + v)^2 := by
  have hproduct : (I : ℂ) * -I = 1 := by rw [mul_neg, I_mul_I, neg_neg]
  calc
    _ = 1 - ((u - v) / (u + v))^2 := by
      rw [mul_div_assoc, mul_div_assoc, mul_mul_mul_comm I _ (-I), hproduct, one_mul, pow_two]
    _ = _ := by
      field_simp
      ring

theorem coefficient_six_matches_iff (u v : ℂ) (hsum : u + v ≠ 0) :
    1 = ((I * (u - v)) / (u + v)) * ((-I * (u - v)) / (u + v)) ↔
      u = 0 ∨ v = 0 := by
  rw [← sub_eq_zero, coefficient_six_defect u v hsum]
  simp [div_eq_zero_iff, hsum, mul_eq_zero]

#print axioms coefficient_six_defect
#print axioms coefficient_six_matches_iff
