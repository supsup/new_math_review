import Mathlib

open scoped BigOperators

/-!
The accounting in the archive's VVle hypothesis. Here lengths are natural
numbers, as required by the separate finiteness clause of VVle. These lemmas
start from such lengths and the budget inequality.
-/

theorem weighted_lengths_are_log_product (S : Finset ℕ) (length : ℕ → ℕ)
    (hpos : ∀ p ∈ S, 0 < p) :
    (∑ p ∈ S, Real.log (p : ℝ) * length p) =
      Real.log (∏ p ∈ S, (p : ℝ) ^ length p) := by
  classical
  induction S using Finset.induction_on with
  | empty => simp
  | @insert p S hpS ih =>
    have hp : (0 : ℝ) < p := by
      exact_mod_cast hpos p (Finset.mem_insert_self p S)
    have hS : ∀ q ∈ S, 0 < q := fun q hq => hpos q (Finset.mem_insert_of_mem hq)
    have hprod : 0 < ∏ q ∈ S, (q : ℝ) ^ length q :=
      Finset.prod_pos fun q hq => pow_pos (by exact_mod_cast hS q hq) _
    rw [Finset.sum_insert hpS, Finset.prod_insert hpS, ih hS,
      Real.log_mul (pow_pos hp _).ne' hprod.ne', Real.log_pow, mul_comm (↑(length p) : ℝ)]

theorem budget_excludes_large_prime (length : ℕ → ℕ) (B : ℝ)
    (budget : ∀ S : Finset ℕ, ∑ p ∈ S, Real.log (p : ℝ) * length p ≤ B)
    {p : ℕ} (hp : 2 ≤ p) (hlarge : Real.exp B < (p : ℝ)) : length p = 0 := by
  by_contra h
  have hone : (1 : ℝ) ≤ length p := by exact_mod_cast Nat.one_le_iff_ne_zero.mpr h
  have hp' : (1 : ℝ) ≤ p := by exact_mod_cast (show 1 ≤ p by omega)
  have logp := Real.log_nonneg hp'
  have hspend := budget {p}
  rw [Finset.sum_singleton] at hspend
  have hcost : Real.log (p : ℝ) ≤ Real.log (p : ℝ) * length p := by
    simpa using mul_le_mul_of_nonneg_left hone logp
  have hp_pos : (0 : ℝ) < p := lt_of_lt_of_le zero_lt_one hp'
  have := (Real.log_le_iff_le_exp hp_pos).mp (hcost.trans hspend)
  exact (not_le_of_gt hlarge) this

#print axioms weighted_lengths_are_log_product
#print axioms budget_excludes_large_prime
