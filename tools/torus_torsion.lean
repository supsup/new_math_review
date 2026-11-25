import Mathlib

/-!
The n-torsion of the real torus (ℝ/ℤ)^(2g) has n^(2g) points.
The display pairs the coordinates as g squares. The archive's general
abelian-scheme theorem is a separate result over algebraically closed fields.
-/

namespace TorusTorsion

local instance : Fact (0 < (1 : ℝ)) := ⟨by norm_num⟩

abbrev Circle := AddCircle (1 : ℝ)

noncomputable def circlePoint (n : ℕ) (j : Fin n) : Circle :=
  ((j.val : ℝ) / n : ℝ)

private theorem circlePoint_killed {n : ℕ} (hn : 0 < n) (j : Fin n) :
    n • circlePoint n j = 0 := by
  apply (AddCircle.nsmul_eq_zero_iff hn).2
  refine ⟨j.val, j.isLt, ?_⟩
  simp [circlePoint]

noncomputable def circleGrid {n : ℕ} (hn : 0 < n) :
    Fin n ≃ {t : Circle // n • t = 0} :=
  Equiv.ofBijective (fun j => ⟨circlePoint n j, circlePoint_killed hn j⟩) (by
    have hnReal : 0 < (n : ℝ) := by exact_mod_cast hn
    have mem (j : Fin n) : (j.val : ℝ) / n ∈ Set.Ico (0 : ℝ) (0 + 1) := by
      refine ⟨div_nonneg (by positivity) hnReal.le, ?_⟩
      rw [zero_add, div_lt_one hnReal]
      exact_mod_cast j.isLt
    constructor
    · intro j k h
      have hcircle : circlePoint n j = circlePoint n k := congrArg Subtype.val h
      have hreal := (AddCircle.coe_eq_coe_iff_of_mem_Ico (mem j) (mem k)).1 hcircle
      have hn' : (n : ℝ) ≠ 0 := hnReal.ne'
      have hjk : (j.val : ℝ) = k.val := by
        calc
          (j.val : ℝ) = ((j.val : ℝ) / n) * n := (div_mul_cancel₀ _ hn').symm
          _ = ((k.val : ℝ) / n) * n := by rw [hreal]
          _ = k.val := div_mul_cancel₀ _ hn'
      exact Fin.ext (by exact_mod_cast hjk)
    · intro ⟨t, ht⟩
      obtain ⟨j, hj, he⟩ := (AddCircle.nsmul_eq_zero_iff hn).1 ht
      exact ⟨⟨j, hj⟩, Subtype.ext (by simpa [circlePoint] using he)⟩)

theorem card_torus_torsion (g n : ℕ) (hn : 0 < n) :
    Nat.card {t : Fin (2 * g) → Circle // n • t = 0} = n ^ (2 * g) := by
  let separated : {t : Fin (2 * g) → Circle // n • t = 0} ≃
      (Fin (2 * g) → {u : Circle // n • u = 0}) :=
    { toFun := fun t i => ⟨t.val i, congrFun t.property i⟩
      invFun := fun t => ⟨fun i => (t i).val, funext fun i => (t i).property⟩
      left_inv := fun _ => rfl
      right_inv := fun _ => rfl }
  let grid := separated.trans (Equiv.piCongrRight fun _ => (circleGrid hn).symm)
  rw [Nat.card_congr grid, Nat.card_eq_fintype_card, Fintype.card_fun, Fintype.card_fin,
    Fintype.card_fin]

#print axioms card_torus_torsion

end TorusTorsion
