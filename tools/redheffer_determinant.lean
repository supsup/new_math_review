import Mathlib

/-!
Vaughan's row operation for the Redheffer determinant, extended to a
completely multiplicative weight and any first column. Indices i,j in
Lean represent i+1,j+1 on the board.
-/

open scoped ArithmeticFunction.Moebius ArithmeticFunction.zeta

namespace Redheffer

def weightedBoard (n : ℕ) (weight : ℕ → ℤ) (column : Fin (n + 1) → ℤ) :
    Matrix (Fin (n + 1)) (Fin (n + 1)) ℤ :=
  fun i j => if j = 0 then column i else
    if i.val + 1 ∣ j.val + 1 then weight ((j.val + 1) / (i.val + 1)) else 0

def board (n : ℕ) : Matrix (Fin (n + 1)) (Fin (n + 1)) ℤ :=
  weightedBoard n (fun _ => 1) (fun _ => 1)

def mobiusWeights {n : ℕ} (i : Fin (n + 1)) : ℤ := μ (i.val + 1)

def mertens (n : ℕ) : ℤ := ∑ i : Fin (n + 1), mobiusWeights i

private theorem sum_over_divisors {n : ℕ} (j : Fin (n + 1)) :
    (∑ i : Fin (n + 1), if i.val + 1 ∣ j.val + 1 then mobiusWeights i else 0) =
      ∑ d ∈ (j.val + 1).divisors, μ d := by
  classical
  let positive : Fin (n + 1) ↪ ℕ :=
    ⟨fun i => i.val + 1, fun i k h => Fin.ext (Nat.succ.inj h)⟩
  have hmap : Finset.map positive (Finset.univ.filter fun i => i.val + 1 ∣ j.val + 1) =
      (j.val + 1).divisors := by
    ext d
    simp only [Finset.mem_map, Finset.mem_filter, Finset.mem_univ, true_and, Nat.mem_divisors]
    constructor
    · rintro ⟨i, hi, rfl⟩
      exact ⟨hi, by omega⟩
    · rintro ⟨hd, _⟩
      have hpos : 0 < d := Nat.pos_of_dvd_of_pos hd (by omega)
      have hle : d ≤ j.val + 1 := Nat.le_of_dvd (by omega) hd
      have hj := j.isLt
      refine ⟨⟨d - 1, by omega⟩, ?_, ?_⟩
      · change d - 1 + 1 ∣ j.val + 1
        simpa [Nat.sub_add_cancel hpos] using hd
      · change d - 1 + 1 = d
        omega
  rw [← hmap, Finset.sum_map, Finset.sum_filter]
  rfl

private theorem replacement_row {n : ℕ} (weight : ℕ → ℤ)
    (hmul : ∀ u v, weight (u * v) = weight u * weight v)
    (column : Fin (n + 1) → ℤ) (j : Fin (n + 1)) :
    (∑ i : Fin (n + 1), (mobiusWeights i * weight (i.val + 1)) *
        weightedBoard n weight column i j) =
      if j = 0 then ∑ i : Fin (n + 1), mobiusWeights i * weight (i.val + 1) * column i
      else 0 := by
  classical
  by_cases hj : j = 0
  · simp [weightedBoard, hj]
  · have hgt : j.val + 1 ≠ 1 := by
      intro h
      apply hj
      exact Fin.ext (by simpa using h)
    simp only [weightedBoard, hj, if_false]
    calc
      _ = ∑ i : Fin (n + 1),
          (if i.val + 1 ∣ j.val + 1 then mobiusWeights i else 0) *
            weight (j.val + 1) := by
        apply Finset.sum_congr rfl
        intro i _
        by_cases h : i.val + 1 ∣ j.val + 1
        · rw [if_pos h, if_pos h, mul_assoc, ← hmul, Nat.mul_div_cancel' h]
        · simp [h]
      _ = 0 := by
        rw [← Finset.sum_mul, sum_over_divisors, ← ArithmeticFunction.coe_mul_zeta_apply,
          ArithmeticFunction.moebius_mul_coe_zeta, ArithmeticFunction.one_apply_ne hgt, zero_mul]

/-- The first column pairs with the Möbius-weighted first row. -/
theorem det_weightedBoard (n : ℕ) (weight : ℕ → ℤ) (hone : weight 1 = 1)
    (hmul : ∀ u v, weight (u * v) = weight u * weight v)
    (column : Fin (n + 1) → ℤ) :
    (weightedBoard n weight column).det =
      ∑ i : Fin (n + 1), mobiusWeights i * weight (i.val + 1) * column i := by
  classical
  let matrix := weightedBoard n weight column
  let c := fun i : Fin (n + 1) => mobiusWeights i * weight (i.val + 1)
  let replaced := matrix.updateRow 0 (∑ i, c i • matrix i)
  have hdet : replaced.det = matrix.det := by
    rw [Matrix.det_updateRow_sum]
    simp [c, mobiusWeights, hone]
  have hrow (j : Fin (n + 1)) :
      replaced 0 j = if j = 0 then ∑ i, c i * column i else 0 := by
    simp only [replaced, Matrix.updateRow_self, Finset.sum_apply, Pi.smul_apply, smul_eq_mul]
    exact replacement_row weight hmul column j
  let minor := replaced.submatrix Fin.succ Fin.succ
  have hminor : minor.det = 1 := by
    have hupper : minor.IsUpperTriangular := by
      intro i j hij
      have hlt : j.succ.val + 1 < i.succ.val + 1 := by
        change j.val < i.val at hij
        simp only [Fin.val_succ]
        omega
      have hnd : ¬ i.succ.val + 1 ∣ j.succ.val + 1 := by
        intro hd
        exact (Nat.not_le_of_lt hlt) (Nat.le_of_dvd (by omega) hd)
      simp only [Fin.val_succ] at hnd
      simp [minor, replaced, matrix, weightedBoard, Fin.succ_ne_zero, hnd]
    rw [Matrix.det_of_isUpperTriangular hupper]
    simp [minor, replaced, matrix, weightedBoard, Fin.succ_ne_zero, Nat.div_self, hone]
  have hminor' : (replaced.submatrix Fin.succ Fin.succ).det = 1 := hminor
  change matrix.det = ∑ i, c i * column i
  rw [← hdet, Matrix.det_succ_row_zero, Fin.sum_univ_succ]
  simp [hrow, Fin.succ_ne_zero, Fin.succAbove_zero, hminor']

/-- The Redheffer matrix on indices 1 through n+1 has determinant M(n+1). -/
theorem det_board (n : ℕ) : (board n).det = mertens n := by
  simpa [board, mertens] using
    det_weightedBoard n (fun _ => 1) rfl (by simp) (fun _ => 1)

#print axioms det_weightedBoard
#print axioms det_board

end Redheffer
