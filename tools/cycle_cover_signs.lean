import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Algebra.CharP.Basic

/-! The permanent and determinant agree over every ring of characteristic two. -/

namespace CycleCover

open Equiv

/-- The unsigned sum of cycle-cover terms. -/
noncomputable def permanent {R ι : Type*} [CommRing R] [Fintype ι] [DecidableEq ι]
    (matrix : Matrix ι ι R) : R :=
  ∑ permutation : Perm ι, ∏ i, matrix (permutation i) i

theorem det_eq_permanent {R ι : Type*} [CommRing R] [CharP R 2] [Fintype ι]
    [DecidableEq ι] (matrix : Matrix ι ι R) : matrix.det = permanent matrix := by
  have htwo : (2 : R) = 0 := CharP.cast_eq_zero R 2
  have hneg : -(1 : R) = 1 :=
    neg_eq_iff_add_eq_zero.mpr (by simpa [one_add_one_eq_two] using htwo)
  rw [Matrix.det_apply', permanent]
  apply Finset.sum_congr rfl
  intro permutation _
  rcases Int.units_eq_one_or (Perm.sign permutation) with h | h
  · simp [h]
  · simp [h, hneg]

#print axioms det_eq_permanent

end CycleCover
