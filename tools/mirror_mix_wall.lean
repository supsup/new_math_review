import Mathlib.NumberTheory.LSeries.DirichletContinuation
import Mathlib.NumberTheory.LSeries.Linearity
import Mathlib.Tactic

/-!
# A zero-free wall for the real mixtures of two L-functions modulo five

At real part 5/2, normalize the leading term to one. Comparing the
remaining coefficients by residue and using a telescoping bound from
n = 16 gives a total below 0.9942. As the real part grows, each term
only gets smaller.

Replay with Lean 4.33.1 in a Mathlib project:
    lake env lean /path/to/mirror_mix_wall.lean

The coefficient estimate follows Confluence's proof from local commit
cf70d7b of new_math_review. Lattice supplied the series comparison,
telescoping bound, character and Gauss sum calculations, and assembly.
-/

open scoped BigOperators

namespace MixWall

/-! ## The series estimate -/

/-- If the total size of the tail is smaller than the first term, cancellation is impossible. -/
theorem LSeries_ne_zero_of_tail_bound {f : ℕ → ℂ} {s : ℂ} (leading : f 1 = 1)
    {majorant : ℕ → ℝ} (hs : Summable majorant)
    (bound : ∀ n, ‖LSeries.term f s (n + 2)‖ ≤ majorant n)
    (small : (∑' n, majorant n) < 1) : LSeries f s ≠ 0 := by
  have hn := hs.of_nonneg_of_le (fun n => norm_nonneg (LSeries.term f s (n + 2))) bound
  have hf := (summable_nat_add_iff 2).mp (summable_norm_iff.mp hn)
  have split : LSeries f s = 1 + ∑' n, LSeries.term f s (n + 2) := by
    rw [LSeries, ← hf.sum_add_tsum_nat_add 2]
    norm_num [Finset.sum_range_succ, LSeries.term_def, leading]
  intro hz
  have ht : (∑' n, LSeries.term f s (n + 2)) = -1 := by
    rw [hz] at split
    linear_combination -split
  have hnorm := (norm_tsum_le_tsum_norm hn).trans_lt ((hn.tsum_le_tsum bound hs).trans_lt small)
  rw [ht] at hnorm
  norm_num at hnorm

noncomputable def residueLimit : ℝ := 250/71

/-- Residues ±1 have weight one, ±2 have weight at most residueLimit, and multiples of 5 vanish. -/
noncomputable def residueWeight (n : ℕ) : ℝ :=
  if n % 5 = 0 then 0 else if n % 5 = 1 ∨ n % 5 = 4 then 1 else residueLimit

private theorem weight_nonneg (n : ℕ) : 0 ≤ residueWeight n := by
  unfold residueWeight
  split_ifs <;> norm_num [residueLimit]

/-- A rational square root lower bound with two decimal places. -/
noncomputable def sqrtLower (n : ℕ) : ℝ := (Nat.sqrt (10000 * n) : ℝ)/100

private theorem sqrtLower_le (n : ℕ) : sqrtLower n ≤ Real.sqrt (n : ℝ) := by
  have h : ((Nat.sqrt (10000 * n) : ℕ) : ℝ)^2 ≤ 10000*(n : ℝ) := by
    rw [pow_two]
    exact_mod_cast (Nat.sqrt_le (10000 * n))
  have hs := Real.sq_sqrt (show 0 ≤ (n : ℝ) by positivity)
  have hsign := Real.sqrt_nonneg (n : ℝ)
  unfold sqrtLower
  nlinarith [sq_nonneg ((Nat.sqrt (10000 * n) : ℝ) - 100*Real.sqrt (n : ℝ))]

private theorem sqrtLower_mono {n m : ℕ} (h : n ≤ m) : sqrtLower n ≤ sqrtLower m := by
  unfold sqrtLower
  gcongr

noncomputable def termMajorant (n : ℕ) : ℝ := residueWeight n / ((n : ℝ)^2 * sqrtLower n)

private theorem termMajorant_nonneg (n : ℕ) : 0 ≤ termMajorant n := by
  exact div_nonneg (weight_nonneg n) (by unfold sqrtLower; positivity)

private theorem weights_of_block (k : ℕ) :
    (∑ j ∈ Finset.range 5, residueWeight (16 + 5*k + j)) = 2 + 2*residueLimit := by
  rw [show (5 : ℕ) = 4+1 by rfl]
  simp only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add]
  have hr (j : ℕ) : (16 + 5*k + j) % 5 = (1+j) % 5 := by omega
  norm_num [residueWeight, hr]
  ring

/-- Each block begins at x = 16 + 5k and has weight 2 + 2R. Compare 1/(4x²)
with 1/((2x−5)(2x+5)), the difference of successive reciprocals divided by ten. -/
private theorem block_majorant (k : ℕ) :
    (∑ j ∈ Finset.range 5, termMajorant (16 + 5*k + j)) ≤
      (2 + 2*residueLimit)/10 * (1/(27+(10:ℝ)*k) - 1/(37+(10:ℝ)*k)) := by
  let x : ℝ := 16+5*(k : ℝ)
  let d : ℝ := (2*x-5)*(2*x+5)
  have hx : 16 ≤ x := by dsimp [x]; linarith [show (0 : ℝ) ≤ k by positivity]
  have hd : 0 < d := by dsimp [d]; exact mul_pos (by linarith) (by linarith)
  have compare (j : ℕ) : termMajorant (16 + 5*k + j) ≤ residueWeight (16 + 5*k + j) / d := by
    have hv : x ≤ ((16 + 5*k + j : ℕ) : ℝ) := by
      push_cast
      dsimp [x]
      linarith [show (0 : ℝ) ≤ j by positivity]
    have hs : (4 : ℝ) ≤ sqrtLower (16 + 5*k + j) :=
      (show (4 : ℝ) ≤ sqrtLower 16 by norm_num [sqrtLower]).trans (sqrtLower_mono (by omega))
    have hb : 4*x^2 ≤ ((16 + 5*k + j : ℕ) : ℝ)^2 * sqrtLower (16 + 5*k + j) := by
      rw [mul_comm 4]
      gcongr
    exact div_le_div_of_nonneg_left (weight_nonneg _) hd ((by dsimp [d]; nlinarith : d ≤ 4*x^2).trans hb)
  calc
    _ ≤ ∑ j ∈ Finset.range 5, residueWeight (16 + 5*k + j) / d :=
      Finset.sum_le_sum (fun j _ => compare j)
    _ = (2 + 2*residueLimit)/d := by rw [← Finset.sum_div, weights_of_block]
    _ = _ := by
      dsimp [d, x]
      have hp : (27+(10:ℝ)*k) ≠ 0 := by positivity
      have hq : (37+(10:ℝ)*k) ≠ 0 := by positivity
      rw [show 2*(16+5*(k : ℝ))-5 = 27+10*(k : ℝ) by ring,
          show 2*(16+5*(k : ℝ))+5 = 37+10*(k : ℝ) by ring]
      field_simp
      ring

private theorem block_sums (k : ℕ) :
    (∑ n ∈ Finset.range (5 * k), termMajorant (n + 16)) ≤
      (2 + 2*residueLimit)/10 * (1/27 - 1/(27+(10:ℝ)*k)) := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [Nat.mul_succ, Finset.sum_range_add]
    have hn (j : ℕ) : 5*k + j + 16 = 16 + 5*k + j := by omega
    simp only [hn]
    push_cast
    calc
      _ ≤ _ + _ := add_le_add ih (block_majorant k)
      _ = _ := by ring_nf

private theorem tail_range (k : ℕ) :
    (∑ n ∈ Finset.range k, termMajorant (n + 16)) ≤ (2 + 2*residueLimit)/270 := by
  calc
    _ ≤ ∑ n ∈ Finset.range (5 * k), termMajorant (n + 16) :=
      Finset.sum_le_sum_of_subset_of_nonneg (Finset.range_mono (by omega)) (fun n _ _ => termMajorant_nonneg _)
    _ ≤ _ := (block_sums k).trans (by
      have h : 0 ≤ (1 : ℝ)/(27+10*(k : ℝ)) := by positivity
      have hM : 0 ≤ (2 + 2*residueLimit)/10 := by norm_num [residueLimit]
      calc
        _ ≤ (2 + 2*residueLimit)/10 * (1/27) := mul_le_mul_of_nonneg_left (sub_le_self _ h) hM
        _ = _ := by ring)

private theorem tail_sum : (∑' n, termMajorant (n + 16)) ≤ (2 + 2*residueLimit)/270 :=
  Real.tsum_le_of_sum_range_le (fun n => termMajorant_nonneg (n + 16)) tail_range

private theorem termMajorant_summable : Summable (fun n => termMajorant (n + 2)) := by
  apply (summable_nat_add_iff 14).mp
  simpa only [Nat.add_assoc] using
    (summable_of_sum_range_le (fun n => termMajorant_nonneg (n + 16)) tail_range)

private theorem termMajorant_sum_lt : (∑' n, termMajorant (n + 2)) < 9942 / 10000 := by
  rw [← termMajorant_summable.sum_add_tsum_nat_add 14]
  have hexact : (∑ n ∈ Finset.range 14, termMajorant (n + 2)) + (2 + 2*residueLimit)/270 < 9942 / 10000 := by
    norm_num [Finset.sum_range_succ, termMajorant, residueWeight, sqrtLower, residueLimit]
  have htail : (∑' n, termMajorant (n + 14 + 2)) ≤ (2 + 2*residueLimit)/270 := by
    simpa only [Nat.add_assoc] using tail_sum
  exact (add_le_add le_rfl htail).trans_lt hexact

/-- A sequence with these mod-five coefficient bounds has a zero-free right half-plane. -/
theorem modFive_LSeries_ne_zero {f : ℕ → ℂ} {s : ℂ}
    (hfirst : f 1 = 1) (hcoeff : ∀ n, ‖f n‖ ≤ residueWeight n)
    (hσ : (5 / 2 : ℝ) ≤ s.re) :
    LSeries f s ≠ 0 := by
  apply LSeries_ne_zero_of_tail_bound hfirst termMajorant_summable _ (termMajorant_sum_lt.trans (by norm_num))
  intro n
  have hre : ((5 / 2 : ℝ) : ℂ).re ≤ s.re := by simpa only [Complex.ofReal_re] using hσ
  apply (LSeries.norm_term_le_of_re_le_re f hre (n + 2)).trans
  rw [LSeries.norm_term_eq, if_neg (by omega), Complex.ofReal_re]
  have hn : (0 : ℝ) < (↑(n + 2) : ℝ) := by positivity
  have hpow : (↑(n + 2) : ℝ) ^ (5 / 2 : ℝ) =
      (↑(n + 2) : ℝ)^2 * Real.sqrt (↑(n + 2) : ℝ) := by
    rw [show (5 / 2 : ℝ) = 2+1/2 by norm_num, Real.rpow_add hn,
      Real.rpow_two, ← Real.sqrt_eq_rpow]
  rw [hpow]
  have hroot : 0 < sqrtLower (n + 2) :=
    (show (0 : ℝ) < sqrtLower 1 by norm_num [sqrtLower]).trans_le (sqrtLower_mono (by omega))
  calc
    _ ≤ residueWeight (n + 2) / ((↑(n + 2) : ℝ)^2 * Real.sqrt (↑(n + 2) : ℝ)) := by
      gcongr
      exact hcoeff (n + 2)
    _ ≤ termMajorant (n + 2) := by
      unfold termMajorant
      exact div_le_div_of_nonneg_left (weight_nonneg _) (by positivity)
        (mul_le_mul_of_nonneg_left (sqrtLower_le _) (sq_nonneg _))

/-! ## The normalized coefficients -/

open Complex

/-- `|u ± v ε|² = 1 ± 2 u v Re ε` when `‖ε‖ = 1` and `u² + v² = 1`. -/
theorem normSq_u_add_v_eps (eps : ℂ) (u v : ℝ) (heps : normSq eps = 1) (huv : u ^ 2 + v ^ 2 = 1) :
    normSq ((u : ℂ) + (v : ℂ) * eps) = 1 + 2 * u * v * eps.re := by
  rw [normSq_apply] at heps ⊢
  simp only [add_re, add_im, mul_re, mul_im, ofReal_re, ofReal_im, zero_mul, sub_zero, zero_add]
  nlinarith [heps, huv]

theorem normSq_u_sub_v_eps (eps : ℂ) (u v : ℝ) (heps : normSq eps = 1) (huv : u ^ 2 + v ^ 2 = 1) :
    normSq ((u : ℂ) - (v : ℂ) * eps) = 1 - 2 * u * v * eps.re := by
  rw [normSq_apply] at heps ⊢
  simp only [sub_re, sub_im, mul_re, mul_im, ofReal_re, ofReal_im, zero_mul, sub_zero, zero_sub]
  nlinarith [heps, huv]

/-- **The coefficient bound, for every real mixing angle.** -/
theorem mix_coeff_bound (eps : ℂ) (u v : ℝ) (heps : ‖eps‖ = 1) (h0 : 0 ≤ eps.re)
    (h1 : eps.re ≤ 57459 / 67541) (huv : u ^ 2 + v ^ 2 = 1) :
    ((u : ℂ) + (v : ℂ) * eps ≠ 0) ∧
      ‖((u : ℂ) - (v : ℂ) * eps) / ((u : ℂ) + (v : ℂ) * eps)‖ ≤ 250 / 71 := by
  have hn : normSq eps = 1 := by rw [normSq_eq_norm_sq, heps]; norm_num
  set c := eps.re with hc
  have hx0 : -1 ≤ 2 * u * v := by nlinarith [sq_nonneg (u + v)]
  have hx1 : 2 * u * v ≤ 1 := by nlinarith [sq_nonneg (u - v)]
  have hden : 0 < 1 + 2 * u * v * c := by nlinarith
  have hD : normSq ((u : ℂ) + (v : ℂ) * eps) = 1 + 2 * u * v * c := normSq_u_add_v_eps eps u v hn huv
  have hN : normSq ((u : ℂ) - (v : ℂ) * eps) = 1 - 2 * u * v * c := normSq_u_sub_v_eps eps u v hn huv
  have hne : (u : ℂ) + (v : ℂ) * eps ≠ 0 := by
    intro h; rw [h, map_zero] at hD; linarith
  refine ⟨hne, ?_⟩
  -- the squared norm of the quotient is (1 - x c)/(1 + x c) with x = 2uv
  have hsq : ‖((u : ℂ) - (v : ℂ) * eps) / ((u : ℂ) + (v : ℂ) * eps)‖ ^ 2
      = (1 - 2 * u * v * c) / (1 + 2 * u * v * c) := by
    rw [norm_div, div_pow, ← normSq_eq_norm_sq, ← normSq_eq_norm_sq, hN, hD]
  -- worst angle x = -1, then the rational endpoint: (1 - x c)(1 - c) ≤ (1 + c)(1 + x c), and
  -- (1 + c)/(1 - c) ≤ (250/71)² exactly when c ≤ 57459/67541
  have hbound : (1 - 2 * u * v * c) / (1 + 2 * u * v * c) ≤ (250 / 71) ^ 2 := by
    rw [div_le_iff₀ hden]
    nlinarith [mul_nonneg h0 (show (0 : ℝ) ≤ 2 * u * v + 1 by linarith)]
  have hq := norm_nonneg (((u : ℂ) - (v : ℂ) * eps) / ((u : ℂ) + (v : ℂ) * eps))
  nlinarith [hsq, hbound, hq]

/-- The root-number input in the form the bound needs: `c ≥ 0` and `c² = (5 + √5)/10` give
`c ≤ 57459/67541`, using only `√5 < 2.2361`. -/
theorem re_le_of_sq (c : ℝ) (hc0 : 0 ≤ c) (hc2 : c ^ 2 = (5 + Real.sqrt 5) / 10) :
    c ≤ 57459 / 67541 := by
  have hs : Real.sqrt 5 < 22361 / 10000 := by
    rw [Real.sqrt_lt' (by norm_num)]; norm_num
  nlinarith [Real.sqrt_nonneg 5]

/-! ## The character and its root number -/

/-- The mod-five odd character with value i at 2. -/
noncomputable def chiFive (n : ℕ) : ℂ :=
  match n % 5 with
  | 1 => 1
  | 2 => Complex.I
  | 3 => -Complex.I
  | 4 => -1
  | _ => 0

/-- Its root number, obtained by pairing conjugate terms of the Gauss sum. -/
noncomputable def epsilonFive : ℂ :=
  ⟨2/Real.sqrt 5 * Real.sin (2*Real.pi/5),
    2/Real.sqrt 5 * Real.sin (4*Real.pi/5)⟩

private theorem sin_two_pi_div_five_sq :
    Real.sin (2*Real.pi/5)^2 = (5 + Real.sqrt 5) / 8 := by
  rw [Real.sin_sq_eq_half_sub, show 2*(2*Real.pi/5) = Real.pi-Real.pi/5 by ring,
      Real.cos_pi_sub, Real.cos_pi_div_five]
  ring

private theorem sin_four_pi_div_five_sq :
    Real.sin (4*Real.pi/5)^2 = (5 - Real.sqrt 5) / 8 := by
  rw [show 4*Real.pi/5 = Real.pi-Real.pi/5 by ring, Real.sin_pi_sub]
  have hs := Real.sin_sq_add_cos_sq (Real.pi/5)
  rw [Real.cos_pi_div_five] at hs
  nlinarith [Real.sq_sqrt (show (0 : ℝ) ≤ 5 by norm_num)]

private theorem epsilonFive_norm : ‖epsilonFive‖ = 1 := by
  have h : ‖epsilonFive‖^2 = 1^2 := by
    rw [Complex.sq_norm, Complex.normSq_apply]
    change (2/Real.sqrt 5 * Real.sin (2*Real.pi/5)) *
        (2/Real.sqrt 5 * Real.sin (2*Real.pi/5)) +
      (2/Real.sqrt 5 * Real.sin (4*Real.pi/5)) *
        (2/Real.sqrt 5 * Real.sin (4*Real.pi/5)) = _
    simp only [← pow_two, mul_pow, div_pow, Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 5),
      sin_two_pi_div_five_sq, sin_four_pi_div_five_sq]
    ring
  exact (sq_eq_sq₀ (norm_nonneg _) zero_le_one).mp h

private theorem epsilonFive_re_bounds :
    0 ≤ epsilonFive.re ∧ epsilonFive.re ≤ 57459/67541 := by
  have hre : 0 ≤ epsilonFive.re := by
    change 0 ≤ 2/Real.sqrt 5 * Real.sin (2*Real.pi/5)
    exact mul_nonneg (by positivity) (Real.sin_nonneg_of_nonneg_of_le_pi
      (by positivity) (by linarith [Real.pi_pos]))
  apply And.intro hre
  apply re_le_of_sq _ hre
  change (2 / Real.sqrt 5 * Real.sin (2 * Real.pi / 5)) ^ 2 = _
  simp only [mul_pow, div_pow, Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 5),
    sin_two_pi_div_five_sq]
  ring

/-- The unnormalized mixture of the odd character and its conjugate. -/
noncomputable def mixCoeffs (eps : ℂ) (u v : ℝ) (n : ℕ) : ℂ :=
  (u : ℂ) * chiFive n + (v : ℂ) * eps * star (chiFive n)

private theorem mix_certified_by_ratio (eps : ℂ) (u v : ℝ) {s : ℂ}
    (hw : (u : ℂ)+(v : ℂ)*eps ≠ 0)
    (hratio : ‖((u : ℂ)-(v : ℂ)*eps)/((u : ℂ)+(v : ℂ)*eps)‖ ≤ residueLimit)
    (hs : (5 / 2 : ℝ) ≤ s.re) :
    LSeries (mixCoeffs eps u v) s ≠ 0 := by
  let d := (u : ℂ)+(v : ℂ)*eps
  let f n := mixCoeffs eps u v n / d
  have first : f 1 = 1 := by norm_num [f, d, mixCoeffs, chiFive, hw]
  have coeffs (n : ℕ) : ‖f n‖ ≤ residueWeight n := by
    have hmod := Nat.mod_lt n (by decide : 0 < 5)
    have hplus : ‖((u : ℂ)+(v : ℂ)*eps)/d‖ = 1 := by simp [d, hw]
    have h2 : (u : ℂ) * Complex.I + -((v : ℂ)*eps*Complex.I) =
        Complex.I * ((u : ℂ)-(v : ℂ)*eps) := by ring
    have h3 : -((u : ℂ) * Complex.I) + (v : ℂ)*eps*Complex.I =
        (-Complex.I) * ((u : ℂ)-(v : ℂ)*eps) := by ring
    interval_cases h : n % 5
    · simp [f, d, mixCoeffs, chiFive, residueWeight, h]
    · simpa [f, d, mixCoeffs, chiFive, residueWeight, h] using hplus.le
    · simpa [f, d, mixCoeffs, chiFive, residueWeight, h, h2, mul_div_assoc] using hratio
    · simpa [f, d, mixCoeffs, chiFive, residueWeight, h, h3, mul_div_assoc] using hratio
    · have hchar : chiFive n = -1 := by simp [chiFive, h]
      have hweight : residueWeight n = 1 := by simp [residueWeight, h]
      simp only [f, mixCoeffs, hchar, hweight, star_neg, star_one]
      rw [show (u : ℂ)*(-1)+(v : ℂ)*eps*(-1) = -d by dsimp [d]; ring, neg_div, norm_neg]
      exact hplus.le
  have nonzero := modFive_LSeries_ne_zero first coeffs hs
  have hf : f = d⁻¹ • mixCoeffs eps u v := by
    ext n
    simp [f, div_eq_mul_inv, mul_comm]
  rw [hf, LSeries_smul] at nonzero
  exact fun hz => nonzero (by rw [hz, mul_zero])


/-- The odd character modulo five, as a Mathlib Dirichlet character. -/
noncomputable def dirichletFive : DirichletCharacter ℂ 5 where
  toFun x := chiFive x.val
  map_one' := by norm_num [chiFive, show (1 : ZMod 5).val = 1 by decide]
  map_mul' := by
    intro a b
    rw [ZMod.val_mul]
    have ha := ZMod.val_lt a
    have hb := ZMod.val_lt b
    interval_cases h_a : a.val <;> interval_cases h_b : b.val <;>
      norm_num [chiFive, h_a, h_b, Complex.I_mul_I]
  map_nonunit' := by
    intro a ha
    let _ : Fact (Nat.Prime 5) := ⟨by decide⟩
    have hzero : a = 0 := by simpa [isUnit_iff_ne_zero] using ha
    norm_num [hzero, chiFive]

private theorem dirichletFive_nat (n : ℕ) : dirichletFive n = chiFive n := by
  change chiFive (n : ZMod 5).val = chiFive n
  rw [ZMod.val_natCast]
  simp [chiFive]

private theorem chiFive_bound (n : ℕ) : ‖chiFive n‖ ≤ 1 := by
  have h := Nat.mod_lt n (by decide : 0 < 5)
  interval_cases hr : n % 5 <;> norm_num [chiFive, hr]

private theorem mix_LFunction_eq (eps : ℂ) (u v : ℝ) {s : ℂ} (hs : 1 < s.re) :
    LSeries (mixCoeffs eps u v) s =
      (u : ℂ)*dirichletFive.LFunction s + (v : ℂ)*eps*(star dirichletFive).LFunction s := by
  let chiBar := fun n : ℕ => star (chiFive n)
  have hχ : LSeriesSummable chiFive s :=
    LSeriesSummable_of_bounded_of_one_lt_re (fun n _ => chiFive_bound n) hs
  have hχbar : LSeriesSummable chiBar s :=
    LSeriesSummable_of_bounded_of_one_lt_re
      (fun n _ ↦ by simpa [chiBar] using chiFive_bound n) hs
  have hf : mixCoeffs eps u v = (u : ℂ) • chiFive + ((v : ℂ)*eps) • chiBar := by
    ext n
    rfl
  simp only [hf, LSeries_add (hχ.smul u) (hχbar.smul ((v : ℂ)*eps)), LSeries_smul,
    DirichletCharacter.LFunction_eq_LSeries _ hs, MulChar.star_apply, dirichletFive_nat, chiBar]

private theorem stdAddFive (j : ℤ) :
    ZMod.stdAddChar (j : ZMod 5) =
      Complex.exp (((2*Real.pi*j/5 : ℝ) : ℂ) * Complex.I) := by
  rw [ZMod.stdAddChar_coe]
  congr 1
  push_cast
  ring

private theorem exp_real_mul_I (x : ℝ) :
    Complex.exp ((x : ℂ) * Complex.I) =
      (Real.cos x : ℂ) + (Real.sin x : ℂ) * Complex.I := by
  rw [Complex.exp_mul_I, ← Complex.ofReal_cos, ← Complex.ofReal_sin]

private theorem gauss_five :
    gaussSum dirichletFive ZMod.stdAddChar =
      2 * Complex.I * (Real.sin (2*Real.pi/5) : ℂ) -
        2 * (Real.sin (4*Real.pi/5) : ℂ) := by
  rw [gaussSum, show (Finset.univ : Finset (ZMod 5)) = {0, 1, 2, 3, 4} by decide]
  rw [Finset.sum_insert (by decide), Finset.sum_insert (by decide),
    Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton]
  have hv0 : dirichletFive 0 = 0 := by rfl
  have hv2 : dirichletFive 2 = Complex.I := by rfl
  have hv3 : dirichletFive 3 = -Complex.I := by rfl
  have hv4 : dirichletFive 4 = -1 := by rfl
  rw [hv0, zero_mul, zero_add, map_one, one_mul, hv2, hv3, hv4]
  have h1 : ZMod.stdAddChar (1 : ZMod 5) = Complex.exp (((2*Real.pi/5 : ℝ) : ℂ) * Complex.I) := by
    simpa using stdAddFive 1
  have h2 : ZMod.stdAddChar (2 : ZMod 5) = Complex.exp (((4*Real.pi/5 : ℝ) : ℂ) * Complex.I) := by
    rw [show (2 : ZMod 5) = ((2 : ℤ) : ZMod 5) by decide, stdAddFive]
    congr 2
    push_cast
    ring
  have h3 : ZMod.stdAddChar (3 : ZMod 5) = Complex.exp (((( -(4*Real.pi/5)) : ℝ) : ℂ) * Complex.I) := by
    rw [show (3 : ZMod 5) = ((-2 : ℤ) : ZMod 5) by decide, stdAddFive]
    congr 2
    push_cast
    ring
  have h4 : ZMod.stdAddChar (4 : ZMod 5) = Complex.exp (((( -(2*Real.pi/5)) : ℝ) : ℂ) * Complex.I) := by
    rw [show (4 : ZMod 5) = ((-1 : ℤ) : ZMod 5) by decide, stdAddFive]
    congr 2
    push_cast
    ring
  rw [h1, h2, h3, h4, exp_real_mul_I, exp_real_mul_I, exp_real_mul_I, exp_real_mul_I]
  simp only [Real.cos_neg, Real.sin_neg, Complex.ofReal_neg]
  ring_nf
  simp [Complex.I_sq, sub_eq_add_neg]

theorem rootNumber_dirichletFive : dirichletFive.rootNumber = epsilonFive := by
  have hodd : ¬dirichletFive.Even := by
    unfold DirichletCharacter.Even
    rw [show (-1:ZMod 5) = 4 by decide]
    change (-1:ℂ) ≠ 1
    norm_num
  have hroot : (5 : ℂ) ^ (1 / 2 : ℂ) = (Real.sqrt 5 : ℂ) := by
    rw [Real.sqrt_eq_rpow, Complex.ofReal_cpow (by norm_num)]
    norm_num
  rw [DirichletCharacter.rootNumber, if_neg hodd, pow_one, gauss_five]
  norm_num only [Nat.cast_ofNat, hroot]
  have hsplit (a b : ℂ) :
      (2 * Complex.I * a - 2*b) / Complex.I = 2*a + 2*b*Complex.I := by
    apply (div_eq_iff Complex.I_ne_zero).mpr
    rw [add_mul, mul_assoc (2*b), Complex.I_mul_I]
    ring
  rw [hsplit]
  have htwore : (2 : ℂ).re = 2 := by norm_num
  have htwoim : (2 : ℂ).im = 0 := by norm_num
  apply Complex.ext <;>
    simp only [epsilonFive, Complex.div_ofReal_re, Complex.div_ofReal_im, Complex.add_re,
      Complex.add_im, Complex.mul_re, Complex.mul_im, Complex.ofReal_re, Complex.ofReal_im,
      htwore, htwoim, Complex.I_re, Complex.I_im] <;>
    ring

/-- Every real-angle mix of the two mod-five L-functions is zero-free on Re s ≥ 5/2. -/
theorem modFive_mix_wall (tau : ℝ) {s : ℂ} (hs : (5 / 2 : ℝ) ≤ s.re) :
    (Real.cos tau : ℂ) * dirichletFive.LFunction s +
      (Real.sin tau : ℂ) * dirichletFive.rootNumber * (star dirichletFive).LFunction s ≠ 0 := by
  have hb := mix_coeff_bound epsilonFive (Real.cos tau) (Real.sin tau) epsilonFive_norm
    epsilonFive_re_bounds.1 epsilonFive_re_bounds.2 (Real.cos_sq_add_sin_sq tau)
  rw [rootNumber_dirichletFive, ← mix_LFunction_eq _ _ _ (by linarith)]
  exact mix_certified_by_ratio _ _ _ hb.1 hb.2 hs

#print axioms modFive_mix_wall

/-! ## Reflection for the completed mixture -/

private theorem dirichletFive_odd : dirichletFive.Odd := by
  unfold DirichletCharacter.Odd
  rw [show (-1 : ZMod 5) = 4 by decide]
  rfl

private theorem dirichletFive_star_odd : (star dirichletFive).Odd := by
  show (star dirichletFive) (-1) = -1
  rw [MulChar.star_apply, dirichletFive_odd]
  simp

private theorem primitive_of_odd_five {χ : DirichletCharacter ℂ 5} (hχ : χ.Odd) : χ.IsPrimitive := by
  rcases (Nat.dvd_prime (by decide : Nat.Prime 5)).mp χ.conductor_dvd_level with h | h
  · have hone := (χ.eq_one_iff_conductor_eq_one).mpr h
    unfold DirichletCharacter.Odd at hχ
    rw [hone, MulChar.one_apply (isUnit_one.neg)] at hχ
    norm_num at hχ
  · exact h

/-- The same real-angle mix with the common Gamma factor included. -/
noncomputable def completedMix (tau : ℝ) (s : ℂ) : ℂ :=
  (Real.cos tau : ℂ) * dirichletFive.completedLFunction s +
    (Real.sin tau : ℂ) * dirichletFive.rootNumber * (star dirichletFive).completedLFunction s

theorem completedMix_ne_zero_right (tau : ℝ) {s : ℂ} (hs : (5 / 2 : ℝ) ≤ s.re) :
    completedMix tau s ≠ 0 := by
  have hχ := DirichletCharacter.LFunction_eq_completed_div_gammaFactor dirichletFive s
    (.inr (by decide))
  have hbar := DirichletCharacter.LFunction_eq_completed_div_gammaFactor (star dirichletFive) s
    (.inr (by decide))
  rw [dirichletFive_odd.gammaFactor_def] at hχ
  rw [dirichletFive_star_odd.gammaFactor_def] at hbar
  have wall := modFive_mix_wall tau hs
  rw [hχ, hbar, ← mul_div_assoc, ← mul_div_assoc, ← add_div] at wall
  change completedMix tau s / _ ≠ 0 at wall
  exact fun hzero => wall (by rw [hzero, zero_div])

private theorem rootNumbers_mul :
    dirichletFive.rootNumber * (star dirichletFive).rootNumber = 1 := by
  let s : ℂ := 3
  have hn : dirichletFive.completedLFunction s ≠ 0 := by
    simpa [completedMix] using completedMix_ne_zero_right 0
      (s := s) (by norm_num [s] : (5 / 2 : ℝ) ≤ s.re)
  -- Applying the functional equation twice returns the same L-function.
  have hχ := DirichletCharacter.IsPrimitive.completedLFunction_one_sub
    (primitive_of_odd_five dirichletFive_odd) (1 - s)
  have hbar := DirichletCharacter.IsPrimitive.completedLFunction_one_sub
    (primitive_of_odd_five dirichletFive_star_odd) s
  rw [sub_sub_cancel, ← MulChar.star_eq_inv] at hχ
  rw [← MulChar.star_eq_inv, star_star] at hbar
  rw [hbar] at hχ
  have hpow : (5 : ℂ) ^ (1 - s - 1/2) * (5 : ℂ) ^ (s - 1/2) = 1 := by
    rw [← Complex.cpow_add _ _ (by norm_num), show 1 - s - 1/2 + (s - 1/2) = 0 by ring,
      Complex.cpow_zero]
  have hcancel : dirichletFive.completedLFunction s =
      (dirichletFive.rootNumber * (star dirichletFive).rootNumber) *
        dirichletFive.completedLFunction s := by
    calc
      _ = _ := hχ
      _ = ((5 : ℂ) ^ (1 - s - 1/2) * (5 : ℂ) ^ (s - 1/2)) *
            ((dirichletFive.rootNumber * (star dirichletFive).rootNumber) *
              dirichletFive.completedLFunction s) := by push_cast; ring
      _ = _ := by rw [hpow, one_mul]
  exact mul_right_cancel₀ hn (by simpa using hcancel.symm)

/-- Reflection swaps the two real weights in the completed mixture. -/
theorem completedMix_reflect (tau : ℝ) (s : ℂ) :
    completedMix tau (1 - s) =
      (5 : ℂ) ^ (s - 1/2) * completedMix (Real.pi / 2 - tau) s := by
  have hχ := DirichletCharacter.IsPrimitive.completedLFunction_one_sub
    (primitive_of_odd_five dirichletFive_odd) s
  have hbar := DirichletCharacter.IsPrimitive.completedLFunction_one_sub
    (primitive_of_odd_five dirichletFive_star_odd) s
  rw [← MulChar.star_eq_inv] at hχ
  rw [← MulChar.star_eq_inv, star_star] at hbar
  rw [completedMix, completedMix, hχ, hbar, Real.cos_pi_div_two_sub, Real.sin_pi_div_two_sub]
  calc
    _ = (5 : ℂ) ^ (s - 1/2) *
          ((Real.sin tau : ℂ) * (dirichletFive.rootNumber * (star dirichletFive).rootNumber) *
            dirichletFive.completedLFunction s +
          (Real.cos tau : ℂ) * dirichletFive.rootNumber * (star dirichletFive).completedLFunction s) := by
        push_cast
        ring
    _ = _ := by rw [rootNumbers_mul, mul_one]

/-- The completed mixture is zero-free on both sides of the resulting strip. -/
theorem completedMix_ne_zero_outside (tau : ℝ) {s : ℂ}
    (hs : s.re ≤ -(3 / 2 : ℝ) ∨ (5 / 2 : ℝ) ≤ s.re) :
    completedMix tau s ≠ 0 := by
  rcases hs with left | right
  · have hright : (5 / 2 : ℝ) ≤ (1 - s).re := by
      simp only [Complex.sub_re, Complex.one_re]
      linarith
    have hmirror := completedMix_reflect tau (1 - s)
    rw [sub_sub_cancel] at hmirror
    rw [hmirror]
    exact mul_ne_zero (by exact Complex.cpow_ne_zero_iff.mpr (Or.inl (by norm_num)))
      (completedMix_ne_zero_right _ hright)
  · exact completedMix_ne_zero_right tau right

#print axioms completedMix_ne_zero_outside

end MixWall
