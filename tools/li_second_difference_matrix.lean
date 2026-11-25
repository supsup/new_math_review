import Mathlib

/-!
Second differences of a Li conjugate pair and the finite cosine matrix.
Replay in a Lean 4.33.1 Mathlib project:
    lake env lean /path/to/li_second_difference_matrix.lean
-/

open scoped BigOperators

namespace LiMatrix

noncomputable section

private theorem square_sum {ι : Type*} [Fintype ι] (f : ι → ℝ) :
    (∑ i, f i) ^ 2 = ∑ i, ∑ j, f i * f j := by
  rw [pow_two, Finset.sum_mul]
  simp_rw [Finset.mul_sum]

/-- Each unit-circle pair contributes a nonnegative weighted cosine matrix. -/
theorem cosine_quadratic (m : ℕ) (θ w : ℝ) (coeff : Fin m → ℝ) :
    (∑ i, ∑ j, coeff i * coeff j *
        (w * Real.cos ((i.val : ℝ)*θ - (j.val : ℝ)*θ))) =
      w * ((∑ i, coeff i * Real.cos ((i.val : ℝ)*θ)) ^ 2
        + (∑ i, coeff i * Real.sin ((i.val : ℝ)*θ)) ^ 2) := by
  let x := fun i : Fin m => coeff i * Real.cos ((i.val : ℝ)*θ)
  let y := fun i : Fin m => coeff i * Real.sin ((i.val : ℝ)*θ)
  change _ = w * ((∑ i, x i)^2 + (∑ i, y i)^2)
  rw [square_sum x, square_sum y]
  calc
    _ = ∑ i, ∑ j, w * (x i * x j + y i * y j) := by
      refine Finset.sum_congr rfl fun i _ => Finset.sum_congr rfl fun j _ => ?_
      simp only [x, y, Real.cos_sub]
      ring
    _ = _ := by simp only [mul_add, Finset.sum_add_distrib, Finset.mul_sum]

theorem cosine_quadratic_nonnegative (m : ℕ) (θ w : ℝ) (hw : 0 ≤ w) (coeff : Fin m → ℝ) :
    0 ≤ ∑ i, ∑ j, coeff i * coeff j *
      (w * Real.cos ((i.val : ℝ)*θ - (j.val : ℝ)*θ)) := by
  rw [cosine_quadratic]
  positivity

theorem pair_secondDifference (x θ : ℝ) :
    2*(1 - Real.cos (x+θ)) - 2*(2*(1 - Real.cos x)) + 2*(1 - Real.cos (x-θ)) =
      4*(1 - Real.cos θ)*Real.cos x := by
  rw [Real.cos_add, Real.cos_sub]
  ring

/-- The contribution sequence of the synthetic quartet with radii 1/2 and 2. -/
def offCoefficient (n : ℕ) : ℝ :=
  if n % 4 = 0 then 4 - 2 * ((1/2:ℝ)^n + 2^n)
  else if n % 4 = 2 then 4 + 2 * ((1/2:ℝ)^n + 2^n)
  else 4

/-- Extend the coefficient sequence evenly before taking the second difference. -/
def secondDifference (a : ℕ → ℝ) (k : ℕ) : ℝ :=
  a (k+1) - 2*a k + a (if k = 0 then 1 else k-1)

def entry (a : ℕ → ℝ) (i j : Fin 3) : ℝ := secondDifference a
  (max i.val j.val - min i.val j.val)

def witness : Fin 3 → ℝ := ![1, 0, 1]

theorem off_first_coefficients :
    offCoefficient 0 = 0 ∧ offCoefficient 1 = 4 ∧ offCoefficient 2 = 25/2 ∧ offCoefficient 3 = 4 := by
  norm_num [offCoefficient]

theorem synthetic_not_psd :
    (∑ i, ∑ j, witness i * witness j * entry offCoefficient i j) = -18 := by
  norm_num [Fin.sum_univ_succ, witness, entry, secondDifference, offCoefficient]

#print axioms pair_secondDifference
#print axioms cosine_quadratic_nonnegative
#print axioms synthetic_not_psd

end

end LiMatrix
