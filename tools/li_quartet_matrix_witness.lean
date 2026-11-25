import Mathlib

/-!
The three-by-three second-difference test for one quartet. Write
`w + 1 / w = a + b*i`; for a nonreal off-circle `w`, `b ≠ 0`.
These real formulas are the three diagonals of its Toeplitz matrix.

Replay in a Lean 4.33.1 Mathlib project.
    lake env lean /path/to/li_quartet_matrix_witness.lean
-/

namespace LiQuartet

def d₀ (a : ℝ) : ℝ := 4 * (2 - a)
def d₁ (a b : ℝ) : ℝ := 2 * (2 - a) * a + 2 * b^2
def d₂ (a b : ℝ) : ℝ := 2 * (2 - a) * (a^2 - b^2 - 2) + 4 * a * b^2

def quadratic (a b x y z : ℝ) : ℝ :=
  d₀ a * (x^2 + y^2 + z^2) + 2 * d₁ a b * (x*y + y*z) + 2 * d₂ a b * x*z

theorem middle_weight_identity (a b x : ℝ) :
    quadratic a b 1 (-x) 1 =
      4 * (2 - a) * (x - a)^2 - 8 * b^2 * (x - a) - 4 * (2 - a) * b^2 := by
  unfold quadratic d₀ d₁ d₂
  ring

/-- A single nonreal off-circle quartet gives a negative form by size three. -/
theorem negative_witness (a b : ℝ) (hb : b ≠ 0) :
    ∃ x y z : ℝ, quadratic a b x y z < 0 := by
  have hb2 : 0 < b^2 := sq_pos_of_ne_zero hb
  rcases lt_trichotomy a 2 with h | h | h
  · refine ⟨1, -a, 1, ?_⟩
    rw [middle_weight_identity]
    have hη : 0 < 2 - a := sub_pos.mpr h
    simpa only [sub_self, zero_pow (by decide : 2 ≠ 0), mul_zero, sub_zero, zero_sub]
      using (neg_neg_of_pos (mul_pos (mul_pos (by norm_num : (0 : ℝ) < 4) hη) hb2))
  · refine ⟨1, -1, 0, ?_⟩
    rw [h]
    norm_num [quadratic, d₀, d₁]
    nlinarith
  · refine ⟨1, 0, 0, ?_⟩
    norm_num [quadratic, d₀]
    linarith

noncomputable def quartetTerm (w : ℂ) (n : ℕ) : ℝ := 4 - 2 * (w^n + (w⁻¹)^n).re

noncomputable def secondDifference (w : ℂ) (k : ℕ) : ℝ :=
  quartetTerm w (k+1) - 2 * quartetTerm w k + quartetTerm w (if k = 0 then 1 else k-1)

private theorem diagonals (w : ℂ) (hw : w ≠ 0) :
    let r := w + w⁻¹
    secondDifference w 0 = d₀ r.re ∧
    secondDifference w 1 = d₁ r.re r.im ∧ secondDifference w 2 = d₂ r.re r.im := by
  let r := w + w⁻¹
  have h₂ : w^2 + (w⁻¹)^2 = r^2 - 2 := by
    dsimp [r]
    field_simp
    ring
  have h₃ : w^3 + (w⁻¹)^3 = r^3 - 3*r := by
    dsimp [r]
    field_simp
    ring
  have q₀ : quartetTerm w 0 = 0 := by norm_num [quartetTerm]
  have q₁ : quartetTerm w 1 = 4 - 2*r.re := by simp [quartetTerm, r]
  have q₂ : quartetTerm w 2 = 4 - 2*(r.re^2 - r.im^2 - 2) := by
    unfold quartetTerm
    rw [h₂, pow_two]
    simp [Complex.sub_re, Complex.mul_re]
    ring
  have q₃ : quartetTerm w 3 = 4 - 2*(r.re^3 - 3*r.re*r.im^2 - 3*r.re) := by
    unfold quartetTerm
    rw [h₃]
    simp [pow_succ, Complex.sub_re, Complex.mul_re, Complex.mul_im]
    ring
  constructor
  · change quartetTerm w 1 - 2 * quartetTerm w 0 + quartetTerm w 1 = d₀ r.re
    rw [q₀, q₁, d₀]
    ring
  constructor
  · change quartetTerm w 2 - 2 * quartetTerm w 1 + quartetTerm w 0 = d₁ r.re r.im
    rw [q₀, q₁, q₂, d₁]
    ring
  · change quartetTerm w 3 - 2 * quartetTerm w 2 + quartetTerm w 1 = d₂ r.re r.im
    rw [q₁, q₂, q₃, d₂]
    ring

/-- The exact second-difference matrix of a nonreal off-circle quartet fails at size three. -/
theorem actual_quartet_witness {w : ℂ} (hi : w.im ≠ 0) (hn : ‖w‖ ≠ 1) :
    ∃ x y z : ℝ, secondDifference w 0 * (x^2 + y^2 + z^2) +
      2 * secondDifference w 1 * (x*y + y*z) + 2 * secondDifference w 2 * x*z < 0 := by
  have hw : w ≠ 0 := by
    intro h
    exact hi (by simp [h])
  let r := w + w⁻¹
  have hr : r.im ≠ 0 := by
    intro h
    change (w + w⁻¹).im = 0 at h
    rw [Complex.add_im, Complex.inv_im] at h
    have hs : Complex.normSq w ≠ 0 := fun hz => hw (Complex.normSq_eq_zero.mp hz)
    field_simp at h
    have hp : w.im * (Complex.normSq w - 1) = 0 := by linarith
    have hsq : ‖w‖^2 = 1 := by
      rw [← Complex.normSq_eq_norm_sq]
      exact sub_eq_zero.mp ((mul_eq_zero.mp hp).resolve_left hi)
    have hfactor : (‖w‖ - 1) * (‖w‖ + 1) = 0 := by nlinarith
    exact hn (sub_eq_zero.mp ((mul_eq_zero.mp hfactor).resolve_right (by positivity)))
  obtain ⟨hd₀, hd₁, hd₂⟩ := diagonals w hw
  obtain ⟨x, y, z, h⟩ := negative_witness r.re r.im hr
  exact ⟨x, y, z, by simpa only [hd₀, hd₁, hd₂, quadratic] using h⟩

end LiQuartet

#print axioms LiQuartet.negative_witness
#print axioms LiQuartet.actual_quartet_witness
