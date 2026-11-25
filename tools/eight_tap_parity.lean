import Mathlib

/-!
Eight positive taps with weights three on the diagonal and one elsewhere.
The same array is invertible over the rationals and gives one parity
over ZMod 2. Seven direct bits and that parity determine the input.

Replay in a Lean 4.33.1 Mathlib project:
    lake env lean /path/to/eight_tap_parity.lean
-/

open scoped BigOperators

namespace EightTapParity

def mix {R : Type*} [Semiring R] (x : Fin 8 → R) (i : Fin 8) : R :=
  2 * x i + ∑ j, x j

theorem sum_rational_readings (x : Fin 8 → ℚ) :
    (∑ i, mix x i) = 10 * ∑ j, x j := by
  simp only [mix, Finset.sum_add_distrib, ← Finset.mul_sum, Finset.sum_const, Finset.card_univ,
    Fintype.card_fin, nsmul_eq_mul]
  ring

theorem rational_recovery (x : Fin 8 → ℚ) (i : Fin 8) :
    (mix x i - (∑ j, mix x j) / 10) / 2 = x i := by
  rw [sum_rational_readings, mix]
  ring

theorem parity_reading (x : Fin 8 → ZMod 2) (i : Fin 8) :
    mix x i = ∑ j, x j := by
  rw [mix, show (2 : ZMod 2) = 0 by decide, zero_mul, zero_add]

theorem remaining_bit (x : Fin 8 → ZMod 2) (i : Fin 8) :
    x i = mix x i - ∑ j ∈ Finset.univ.erase i, x j := by
  have hsum : (∑ j ∈ Finset.univ.erase i, x j) + x i = ∑ j, x j :=
    Finset.sum_erase_add Finset.univ x (Finset.mem_univ i)
  rw [parity_reading, ← hsum]
  abel

/-- Any seven direct bits and one mixed reading determine all eight. -/
theorem recovery_from_seven (x y : Fin 8 → ZMod 2) (missing : Fin 8)
    (known : ∀ i, i ≠ missing → x i = y i)
    (reading : mix x missing = mix y missing) : x = y := by
  ext i
  by_cases hi : i = missing
  · subst i
    have hsum : (∑ j ∈ Finset.univ.erase missing, x j) =
        ∑ j ∈ Finset.univ.erase missing, y j := by
      apply Finset.sum_congr rfl
      exact fun j hj => known j (Finset.mem_erase.mp hj).1
    rw [remaining_bit x missing, remaining_bit y missing, reading, hsum]
  · exact known i hi

#print axioms rational_recovery
#print axioms recovery_from_seven

end EightTapParity
