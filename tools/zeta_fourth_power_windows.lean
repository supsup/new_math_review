import PrimeBound

/-!
Fourth-power sampling for the prime-sum criterion, using the existing local
PrimeBound wrapper and the archive's definition of Deduction.G.

Replay from the repository root with the same 31 archive modules:
    python3 -B tools/replay_rh_prime_bound.py ARCHIVE_SRC MATHLIB_PROJECT --fourth-powers
-/

open Set
open scoped ArithmeticFunction.vonMangoldt

namespace ZetaFourthGrid

private theorem ramp_eq_finite_sum {x b : ℝ} (hx : 0 ≤ x) (hxb : x ≤ b) :
    (Deduction.ramp (fun _ => 1) x).re =
      ∑ n ∈ Finset.range (⌊b⌋₊ + 1), Λ n * max (x / n - 1) 0 := by
  unfold Deduction.ramp
  simp only [mul_one, ← Complex.ofReal_mul, ← Complex.ofReal_sum, Complex.ofReal_re]
  apply Finset.sum_subset (Finset.range_subset_range.mpr (by gcongr))
  intro n _ hn
  have hn' : ⌊x⌋₊ < n := by
    rw [Finset.mem_range] at hn
    omega
  have hxn := (Nat.floor_lt hx).mp hn'
  have hn0 : 0 < (n : ℝ) := hx.trans_lt hxn
  have h0 : x / n - 1 ≤ 0 := by
    rw [sub_nonpos, div_le_iff₀ hn0, one_mul]
    exact hxn.le
  simp [max_eq_right h0]

private theorem convexOn_affine {a b : ℝ} (c d : ℝ) :
    ConvexOn ℝ (Icc a b) (fun x => c * x + d) := by
  refine ⟨convex_Icc _ _, ?_⟩
  intro x hx y hy u v hu hv huv
  simp only [smul_eq_mul]
  have h : c * (u * x + v * y) + d = u * (c * x + d) + v * (c * y + d) := by
    linear_combination -d * huv
  exact h.le

/-- The nonnegative prime-power hinges make the log-corrected function convex. -/
theorem convex_corrected {a b : ℝ} (ha : 0 ≤ a) :
    ConvexOn ℝ (Icc a b) (fun x => Deduction.G x + x * Real.log x) := by
  let hinge := fun (n : ℕ) (x : ℝ) => Λ n * max (x / n - 1) 0
  have hH (n : ℕ) : ConvexOn ℝ (Icc a b) (hinge n) := by
    have hA : ConvexOn ℝ (Icc a b) (fun x => x / n - 1) := by
      convert convexOn_affine (a := a) (b := b) (1 / (n : ℝ)) (-1) using 1
      ext x
      ring
    have hM := hA.sup (convexOn_const (0 : ℝ) (convex_Icc a b))
    exact hM.smul (show 0 ≤ Λ n from ArithmeticFunction.vonMangoldt_nonneg)
  have hSum (S : Finset ℕ) : ConvexOn ℝ (Icc a b) (fun x => ∑ n ∈ S, hinge n x) := by
    classical
    induction S using Finset.induction_on with
    | empty => simpa using convexOn_const (0 : ℝ) (convex_Icc a b)
    | insert n S hn ih =>
      simpa [Finset.sum_insert hn, Pi.add_def] using (hH n).add ih
  apply ((hSum (Finset.range (⌊b⌋₊ + 1))).add
    (convexOn_affine (1 + Real.eulerMascheroniConstant) 0)).congr
  intro x hx
  simp [hinge, Deduction.G, ramp_eq_finite_sum (ha.trans hx.1) hx.2]
  ring

private theorem convex_quadratic_log {a b : ℝ} (ha : 0 < a) :
    ConvexOn ℝ (Icc a b) (fun x => x ^ 2 / (2 * a) - x * Real.log x) := by
  refine convexOn_of_hasDerivWithinAt2_nonneg (f' := fun x => x / a - Real.log x - 1)
    (f'' := fun x => 1 / a - 1 / x) (convex_Icc _ _) ?_ ?_ ?_ ?_
  · intro x hx
    have hx0 := ha.trans_le hx.1
    exact (((continuousAt_id.pow 2).div_const _).sub
      (continuousAt_id.mul (Real.continuousAt_log hx0.ne'))).continuousWithinAt
  · intro x hx
    have hx0 := ha.trans_le (interior_subset hx : x ∈ Icc a b).1
    have hq := ((hasDerivAt_id x).pow 2).div_const (2 * a)
    have hf := (hasDerivAt_id x).mul (Real.hasDerivAt_log hx0.ne')
    have hqd : ((2 : ℕ) : ℝ) * id x ^ (2 - 1 : ℕ) * 1 / (2 * a) = x / a := by
      norm_num
      field_simp [ha.ne']
    have hfd : 1 * Real.log x + id x * x⁻¹ = Real.log x + 1 := by simp [hx0.ne']
    rw [hqd] at hq
    rw [hfd] at hf
    rw [show x / a - Real.log x - 1 = x / a - (Real.log x + 1) by ring]
    exact (hq.sub hf).hasDerivWithinAt
  · intro x hx
    have hx0 := ha.trans_le (interior_subset hx : x ∈ Icc a b).1
    simpa [one_div] using (((hasDerivAt_id x).div_const a).sub
      (Real.hasDerivAt_log hx0.ne')).sub_const 1 |>.hasDerivWithinAt
  · intro x hx
    exact sub_nonneg.mpr (one_div_le_one_div_of_le ha (interior_subset hx : x ∈ Icc a b).1)

/-- The concavity of the log correction costs at most one quadratic mesh error. -/
theorem interval_bound {a b x eta : ℝ} (ha : 0 < a) (hab : a < b)
    (hx : x ∈ Icc a b) (heta0 : 0 ≤ eta) (heta1 : eta ≤ 1)
    (hGa : Deduction.G a ≤ a ^ eta) (hGb : Deduction.G b ≤ b ^ eta) :
    Deduction.G x ≤ x ^ eta + (b - a) ^ 2 / (8 * a) := by
  let t := (x - a) / (b - a)
  have hgap : 0 < b - a := sub_pos.mpr hab
  have ht0 : 0 ≤ t := div_nonneg (sub_nonneg.mpr hx.1) hgap.le
  have ht1 : t ≤ 1 := (div_le_iff₀ hgap).mpr (by linarith [hx.2])
  have ht : (1 - t) * a + t * b = x := by
    dsimp [t]
    field_simp [hgap.ne']
    ring
  have hsum : ConvexOn ℝ (Icc a b) (fun y => Deduction.G y + y ^ 2 / (2 * a)) := by
    apply ((convex_corrected ha.le).add (convex_quadratic_log ha)).congr
    intro y hy
    simp
  have hquad := hsum.2 (left_mem_Icc.mpr hab.le) (right_mem_Icc.mpr hab.le)
    (sub_nonneg.mpr ht1) ht0 (by ring : 1 - t + t = 1)
  simp only [smul_eq_mul] at hquad
  rw [ht] at hquad
  have hConcave := (Real.concaveOn_rpow heta0 heta1).2
    (show a ∈ Ici (0 : ℝ) from ha.le) (show b ∈ Ici (0 : ℝ) from ha.le.trans hab.le)
    (sub_nonneg.mpr ht1) ht0 (by ring : 1 - t + t = 1)
  simp only [smul_eq_mul] at hConcave
  rw [ht] at hConcave
  have hEnds : (1 - t) * Deduction.G a + t * Deduction.G b ≤ x ^ eta :=
    (add_le_add (mul_le_mul_of_nonneg_left hGa (sub_nonneg.mpr ht1))
      (mul_le_mul_of_nonneg_left hGb ht0)).trans hConcave
  have hError :
      (1 - t) * (a ^ 2 / (2 * a)) + t * (b ^ 2 / (2 * a)) - x ^ 2 / (2 * a) =
        (b - a) ^ 2 / (2 * a) * (t * (1 - t)) := by
    rw [← ht]
    ring
  have hQuarter : t * (1 - t) ≤ 1 / 4 := by nlinarith [sq_nonneg (t - 1 / 2)]
  have hErrorBound := mul_le_mul_of_nonneg_left hQuarter
    (div_nonneg (sq_nonneg (b-a)) (by positivity : 0 ≤ 2 * a))
  calc
    Deduction.G x ≤ x ^ eta + (b - a) ^ 2 / (2 * a) * (1 / 4) := by linarith
    _ = _ := by ring

private theorem fourth_gap_bound {m x : ℝ} (hm : 1 ≤ m) (hx : m ^ 4 ≤ x) :
    ((m + 1) ^ 4 - m ^ 4) ^ 2 / (8 * m ^ 4) ≤ 29 * √x := by
  have hm0 : 0 < m := zero_lt_one.trans_le hm
  have hgap : 0 ≤ (m + 1) ^ 4 - m ^ 4 := by
    exact sub_nonneg.mpr (pow_le_pow_left₀ hm0.le (by linarith) 4)
  have h1 : m ≤ m ^ 2 := le_self_pow₀ hm (by decide)
  have h2 : m ^ 2 ≤ m ^ 3 := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hm) (sq_nonneg m)]
  have hgapmax : (m + 1) ^ 4 - m ^ 4 ≤ 15 * m ^ 3 := by
    nlinarith
  have hsq := pow_le_pow_left₀ hgap hgapmax 2
  have hlocal : ((m + 1) ^ 4 - m ^ 4) ^ 2 / (8 * m ^ 4) ≤ 29 * m ^ 2 := by
    apply (div_le_iff₀ (by positivity)).mpr
    nlinarith [pow_nonneg hm0.le 6]
  have hroot := Real.sqrt_le_sqrt hx
  rw [show m ^ 4 = (m ^ 2) ^ 2 by ring, Real.sqrt_sq (sq_nonneg m)] at hroot
  exact hlocal.trans (mul_le_mul_of_nonneg_left hroot (by norm_num))

/-- One cofinal fourth-power sample window for each exponent and cutoff. -/
def SampleBound : Prop :=
  ∀ eta : ℝ, 1 / 2 < eta → eta < 1 → ∀ N₀ : ℕ,
    ∃ N : ℕ, N₀ ≤ N ∧
      ∀ m : ℕ, N ≤ m → m ≤ ⌊(N : ℝ) ^ (3 / 2 : ℝ)⌋₊ + 1 →
        Deduction.G ((m : ℝ) ^ 4) ≤ ((m : ℝ) ^ 4) ^ eta

private theorem bounds_between_fourth_powers {N : ℕ} (hN : 1 ≤ N) {eta : ℝ}
    (heta0 : 0 ≤ eta) (heta1 : eta ≤ 1)
    (hSample : ∀ m : ℕ, N ≤ m → m ≤ ⌊(N : ℝ) ^ (3 / 2 : ℝ)⌋₊ + 1 →
      Deduction.G ((m : ℝ) ^ 4) ≤ ((m : ℝ) ^ 4) ^ eta)
    {x : ℝ} (hx : x ∈ Icc ((N : ℝ) ^ 4) (((N : ℝ) ^ 4) ^ (3 / 2 : ℝ))) :
    Deduction.G x ≤ x ^ eta + 29 * √x := by
  have hx0 : 0 ≤ x := (by positivity : 0 ≤ (N : ℝ) ^ 4).trans hx.1
  let u := √(√x)
  have hu0 : 0 ≤ u := Real.sqrt_nonneg _
  have hu4 : u ^ 4 = x := by
    dsimp [u]
    rw [show (4 : ℕ) = 2 * 2 by decide, pow_mul, Real.sq_sqrt (Real.sqrt_nonneg x),
      Real.sq_sqrt hx0]
  let m := ⌊u⌋₊
  have hm0 : 0 ≤ (m : ℝ) := Nat.cast_nonneg _
  have hmN : N ≤ m := Nat.le_floor ((pow_le_pow_iff_left₀ (Nat.cast_nonneg _) hu0
    (by decide : (4 : ℕ) ≠ 0)).mp (hu4 ▸ hx.1))
  have hm : 1 ≤ (m : ℝ) := by exact_mod_cast hN.trans hmN
  have hupper : u ≤ (N : ℝ) ^ (3 / 2 : ℝ) := by
    have hpow : ((N : ℝ) ^ (3 / 2 : ℝ)) ^ 4 = ((N : ℝ) ^ 4) ^ (3 / 2 : ℝ) := by
      rw [← Real.rpow_mul_natCast (Nat.cast_nonneg _),
        ← Real.rpow_natCast_mul (Nat.cast_nonneg _)]
      congr 1
      norm_num
    apply (pow_le_pow_iff_left₀ (n := 4) hu0 (Real.rpow_nonneg (Nat.cast_nonneg _) _) (by decide)).mp
    rw [hu4, hpow]
    exact hx.2
  have hmb := Nat.floor_le_floor hupper
  have hEnds : x ∈ Icc ((m : ℝ) ^ 4) (((m : ℝ) + 1) ^ 4) := by
    rw [← hu4]
    exact ⟨pow_le_pow_left₀ hm0 (Nat.floor_le hu0) 4,
      pow_le_pow_left₀ hu0 (Nat.lt_floor_add_one u).le 4⟩
  have hb := hSample (m + 1) (hmN.trans (Nat.le_succ _)) (Nat.add_le_add_right hmb 1)
  push_cast at hb
  have hInterval := interval_bound (by positivity : 0 < (m : ℝ) ^ 4)
    (pow_lt_pow_left₀ (by linarith : (m : ℝ) < (m : ℝ) + 1) hm0 (by decide))
    hEnds heta0 heta1 (hSample m hmN (hmb.trans (Nat.le_succ _))) hb
  exact hInterval.trans (add_le_add_right (fourth_gap_bound hm hEnds.1) (x ^ eta))

private theorem eventually_absorb_error {eta theta : ℝ} (heta : eta < theta)
    (hhalf : 1 / 2 < theta) :
    ∃ R : ℝ, ∀ x : ℝ, R ≤ x → 0 < x → x ^ eta + 29 * √x ≤ x ^ theta := by
  obtain ⟨R₁, h₁⟩ := Filter.eventually_atTop.mp
    ((tendsto_rpow_atTop (sub_pos.mpr heta)).eventually_ge_atTop 2)
  obtain ⟨R₂, h₂⟩ := Filter.eventually_atTop.mp
    ((tendsto_rpow_atTop (sub_pos.mpr hhalf)).eventually_ge_atTop 58)
  refine ⟨max R₁ R₂, fun x hx hx0 => ?_⟩
  have hη := mul_le_mul_of_nonneg_left (h₁ x ((le_max_left _ _).trans hx))
    (Real.rpow_nonneg hx0.le eta)
  have hroot := mul_le_mul_of_nonneg_left (h₂ x ((le_max_right _ _).trans hx))
    (Real.rpow_nonneg hx0.le (1 / 2))
  rw [← Real.rpow_add hx0, show eta + (theta - eta) = theta by ring] at hη
  rw [← Real.rpow_add hx0, show 1 / 2 + (theta - 1 / 2) = theta by ring,
    ← Real.sqrt_eq_rpow] at hroot
  linarith

/-- Fourth-power samples suffice for the archive's continuous prime-window input. -/
theorem prime_windows_of_samples (h : SampleBound) :
    ∀ theta : ℝ, 1 / 2 < theta → theta < 1 → ∀ Y₀ : ℝ,
      ∃ Y : ℝ, Y₀ ≤ Y ∧ ∀ x ∈ Icc Y (Y ^ (3 / 2 : ℝ)), Deduction.G x ≤ x ^ theta := by
  intro theta hhalf htheta Y₀
  let eta := (1 / 2 + theta) / 2
  have heta : 1 / 2 < eta := by dsimp [eta]; linarith
  have heθ : eta < theta := by dsimp [eta]; linarith
  obtain ⟨R, hR⟩ := eventually_absorb_error heθ hhalf
  let N₀ := max 1 ⌈max R Y₀⌉₊
  obtain ⟨N, hN₀, hS⟩ := h eta heta (heθ.trans htheta) N₀
  have hN : 1 ≤ N := (le_max_left _ _).trans hN₀
  have hN1 : 1 ≤ (N : ℝ) := by exact_mod_cast hN
  have hBack : max R Y₀ ≤ (N : ℝ) ^ 4 := by
    refine (Nat.le_ceil _).trans ((Nat.cast_le.mpr ((le_max_right _ _).trans hN₀)).trans ?_)
    exact le_self_pow₀ hN1 (by decide)
  refine ⟨(N : ℝ) ^ 4, (le_max_right _ _).trans hBack, fun x hx => ?_⟩
  have hx0 : 0 < x := (by positivity : 0 < (N : ℝ) ^ 4).trans_le hx.1
  exact (bounds_between_fourth_powers hN (by linarith) (heθ.trans htheta).le hS hx).trans
    (hR x ((le_max_left _ _).trans (hBack.trans hx.1)) hx0)

/-- The existing analytic finish applies to the sampled bounds. -/
theorem rh_of_fourth_power_samples (h : SampleBound) : RiemannHypothesis :=
  rh_of_zeta_prime_bound (prime_windows_of_samples h)

#print axioms convex_corrected
#print axioms interval_bound
#print axioms prime_windows_of_samples
#print axioms rh_of_fourth_power_samples

end ZetaFourthGrid
