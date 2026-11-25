import Mathlib

/-! A check for the trapping-disk card. From a Mathlib project at Lean 4.33.1,
run `lake env lean /path/to/tools/zeta_trapping_disk.lean`.

The Bernoulli polynomial bounds, numerical comparisons and convergence from
the derivative and center bounds are checked here. The Euler–Maclaurin
expansion and its application to zeta are explained on the card. -/

open Filter Function Set Topology

namespace MathBreak

noncomputable section

def trapCenter : ℂ := -3 / 10
def trapRadius : ℝ := 3 / 50

def trapDisk : Set ℂ := Metric.closedBall trapCenter trapRadius

def trapSlope : NNReal := ⟨43 / 50, by norm_num⟩
def centerDrift : ℝ := 47 / 6250

theorem bernoulli_two_bound {t : ℝ} (h0 : 0 ≤ t) (h1 : t ≤ 1) :
    |t^2 - t + 1/6| ≤ 1/6 := by
  refine abs_le.2 ⟨?_, ?_⟩
  · nlinarith [sq_nonneg (t - 1/2)]
  · nlinarith [mul_nonneg h0 (sub_nonneg.2 h1)]

theorem bernoulli_three_bound {t : ℝ} (h0 : 0 ≤ t) (h1 : t ≤ 1) :
    |t * (t - 1/2) * (t - 1)| < 1/20 := by
  let u := (t - 1/2)^2
  have hu : u ≤ 1/4 := by
    dsimp [u]
    nlinarith [mul_nonneg h0 (sub_nonneg.2 h1)]
  have gap : 0 ≤ (1/3 - u) * (u - 1/12)^2 :=
    mul_nonneg (sub_nonneg.2 (by linarith)) (sq_nonneg _)
  have ident : (t * (t - 1/2) * (t - 1))^2 + (1/3 - u) * (u - 1/12)^2 = 1/432 := by
    dsimp [u]
    ring
  have hs : |t * (t - 1/2) * (t - 1)|^2 < (1/20 : ℝ)^2 := by
    rw [sq_abs]
    nlinarith
  by_contra! h
  nlinarith [sq_nonneg (|t * (t - 1/2) * (t - 1)| - 1/20)]

theorem trap_numeric_estimates :
    (1/(1.24 : ℝ)^2 + 1/12 + 0.52/(12*0.64) + 0.36*0.76/(12*0.64^2)) <
      (trapSlope : ℝ) ∧
    3/520 + (7/4000 : ℝ) < centerDrift ∧
    centerDrift + (trapSlope : ℝ) * trapRadius < trapRadius := by
  have hSlope : (trapSlope : ℝ) = 43 / 50 := rfl
  norm_num [hSlope, centerDrift, trapRadius]

theorem trap_disk {f : ℂ → ℂ}
    (hdiff : ∀ z ∈ trapDisk, DifferentiableAt ℂ f z)
    (hderiv : ∀ z ∈ trapDisk, ‖fderiv ℂ f z‖ ≤ (trapSlope : ℝ))
    (hcenter : dist (f trapCenter) trapCenter ≤ centerDrift) :
    ∃ z ∈ trapDisk, IsFixedPt f z ∧
      (∀ w ∈ trapDisk, IsFixedPt f w → w = z) ∧
      ∀ w ∈ trapDisk, Tendsto (fun n : ℕ ↦ f^[n] w) atTop (𝓝 z) := by
  have center_mem : trapCenter ∈ trapDisk := by norm_num [trapDisk, trapRadius]
  have hlip : LipschitzOnWith trapSlope f trapDisk :=
    Convex.lipschitzOnWith_of_nnnorm_fderiv_le hdiff (fun z hz ↦ hderiv z hz)
      (convex_closedBall trapCenter trapRadius)
  have hmap : MapsTo f trapDisk trapDisk := by
    intro z hz
    show dist (f z) trapCenter ≤ trapRadius
    calc
      dist (f z) trapCenter ≤ dist (f z) (f trapCenter) + dist (f trapCenter) trapCenter :=
        dist_triangle _ _ _
      _ ≤ (trapSlope : ℝ) * dist z trapCenter + centerDrift :=
        add_le_add (hlip.dist_le_mul z hz trapCenter center_mem) hcenter
      _ ≤ (trapSlope : ℝ) * trapRadius + centerDrift := by
        gcongr
        exact hz
      _ ≤ trapRadius := by linarith [trap_numeric_estimates.2.2]
  have hcon : ContractingWith trapSlope (hmap.restrict f trapDisk trapDisk) := by
    refine ⟨?_, LipschitzWith.of_dist_le_mul fun x y ↦ hlip.dist_le_mul x.val x.property y.val y.property⟩
    change (43 / 50 : ℝ) < 1
    norm_num
  have complete : IsComplete trapDisk := Metric.isClosed_closedBall.isComplete
  obtain ⟨z, hz, hfix, -, -⟩ := hcon.exists_fixedPoint' complete hmap center_mem (edist_ne_top _ _)
  have unique (w : ℂ) (hw : w ∈ trapDisk) (hfixw : IsFixedPt f w) : w = z := by
    have heq := hcon.fixedPoint_unique' (x := ⟨w,hw⟩) (y := ⟨z,hz⟩)
      (Subtype.ext hfixw) (Subtype.ext hfix)
    exact congrArg Subtype.val heq
  refine ⟨z, hz, hfix, unique, fun w hw ↦ ?_⟩
  obtain ⟨v, hv, hvfix, hlim, -⟩ := hcon.exists_fixedPoint' complete hmap hw (edist_ne_top _ _)
  exact (unique v hv hvfix) ▸ hlim

#print axioms bernoulli_two_bound
#print axioms bernoulli_three_bound
#print axioms trap_numeric_estimates
#print axioms trap_disk

end

end MathBreak
