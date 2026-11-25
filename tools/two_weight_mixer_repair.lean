import Mathlib

/-!
The sixteen-reading mixer at weights 1 and 2. Two spectra and a Vandermonde
argument show that any seven direct probes determine the inputs whenever the
mixed reading budget is 2 errors plus erasures at most seven.

Replay in a Lean 4.33.1 project with Mathlib at 0df444a.
    lake env lean /path/to/two_weight_mixer_repair.lean
-/

open scoped BigOperators Matrix

namespace TwoWeightMixer

local instance : Fact (Nat.Prime 17) := ⟨by decide⟩

abbrev Pos := ZMod 16
abbrev F := ZMod 17

def taps : Finset Pos := {1, 2, 3, 5, 8, 9, 14}

def mix (f : Pos → F) (j : Pos) : F :=
  f j + 2 * ∑ offset ∈ taps, f (j - offset)

private def address (j : Pos) : F := (3 : F) ^ j.val

private theorem address_ne_zero (j : Pos) : address j ≠ 0 :=
  pow_ne_zero _ (by decide)

private theorem address_injective : Function.Injective address := by
  have h : ∀ i j : Pos, i ≠ j → address i ≠ address j := by decide
  intro i j hij
  by_contra hne
  exact h i j hne hij

private theorem address_add (i j : Pos) : address (i + j) = address i * address j := by
  unfold address
  rw [ZMod.val_add, ← pow_eq_pow_mod _ (show (3 : F) ^ 16 = 1 by decide), pow_add]

private def spectrum (f : Pos → F) (k : ℕ) : F :=
  ∑ j : Pos, f j * (address j)^k

private def gain (k : ℕ) : F :=
  1 + 2 * ∑ offset ∈ taps, (address offset)^k

private theorem shift (f : Pos → F) (k : ℕ) (offset : Pos) :
    (∑ j : Pos, f (j - offset) * (address j)^k) = spectrum f k * (address offset)^k := by
  rw [← Equiv.sum_comp (Equiv.addRight offset) (fun j : Pos => f (j - offset) * (address j)^k)]
  change (∑ j : Pos, f (j + offset - offset) * (address (j + offset))^k) = _
  simp only [add_sub_cancel_right, address_add, mul_pow]
  rw [spectrum, Finset.sum_mul]
  simp only [mul_assoc]

private theorem spectrum_mix (f : Pos → F) (k : ℕ) :
    spectrum (mix f) k = gain k * spectrum f k := by
  unfold spectrum mix gain
  simp only [add_mul, mul_assoc, Finset.sum_add_distrib, ← Finset.mul_sum, Finset.sum_mul]
  rw [Finset.sum_comm]
  simp_rw [shift, ← Finset.mul_sum]
  unfold spectrum
  rw [← Finset.sum_mul]
  ring

private theorem mix_sub (f g : Pos → F) (j : Pos) :
    mix (f - g) j = mix f j - mix g j := by
  simp only [mix, Pi.sub_apply, Finset.sum_sub_distrib]
  ring

private theorem small_gains : ∀ k : Fin 7, gain (1 + k.val) = 0 := by decide

private theorem large_gains : ∀ k : Fin 9, gain (8 + k.val) ≠ 0 := by decide

private theorem sparse_vanish {m : ℕ} (slots : Fin m → Pos) (hi : Function.Injective slots)
    (f : Pos → F) (hSupp : ∀ j, j ∉ Set.range slots → f j = 0)
    (start : ℕ) (hMoment : ∀ k : Fin m, spectrum f (start + k.val) = 0) :
    f = 0 := by
  classical
  let v : Fin m → F := address ∘ slots
  let w : Fin m → F := fun i => f (slots i) * (v i)^start
  have hMapped : w ᵥ* Matrix.vandermonde v = 0 := by
    funext k
    simp only [Matrix.vecMul, dotProduct, Matrix.vandermonde_apply,
      Pi.zero_apply, w, mul_assoc, ← pow_add, v, Function.comp_apply]
    have restricted :
        (∑ i : Fin m, f (slots i) * (address (slots i))^(start + k.val)) =
        spectrum f (start + k.val) := by
      unfold spectrum
      rw [← Finset.sum_image (f := fun j : Pos => f j * (address j)^(start + k.val))
        (s := Finset.univ) (g := slots) hi.injOn]
      apply Finset.sum_subset (Finset.subset_univ _)
      intro j _ hn
      have hr : j ∉ Set.range slots := by simpa [Finset.mem_image, Set.mem_range] using hn
      simp [hSupp j hr]
    rw [restricted, hMoment k]
  have hw : w = 0 := Matrix.eq_zero_of_vecMul_eq_zero
    (Matrix.det_vandermonde_ne_zero_iff.mpr (address_injective.comp hi)) hMapped
  funext j
  by_cases hj : j ∈ Set.range slots
  · obtain ⟨i, rfl⟩ := hj
    have h : f (slots i) * (address (slots i))^start = 0 := congrFun hw i
    exact (mul_eq_zero.mp h).resolve_right (pow_ne_zero _ (address_ne_zero _))
  · exact hSupp j hj


private theorem sparse_vanish_on (locations : Finset Pos) (f : Pos → F)
    (hSupp : ∀ j, j ∉ locations → f j = 0)
    (start : ℕ) (hMoment : ∀ k : Fin locations.card, spectrum f (start + k.val) = 0) :
    f = 0 := by
  let slots : Fin locations.card → Pos := fun i => (locations.equivFin.symm i).val
  have hi : Function.Injective slots :=
    Subtype.val_injective.comp locations.equivFin.symm.injective
  refine sparse_vanish slots hi f ?_ start hMoment
  intro j hj
  refine hSupp j (fun h => hj ⟨locations.equivFin ⟨j, h⟩, ?_⟩)
  simp [slots]

/-- Seven erased mixed readings and seven direct probes determine all sixteen inputs. -/
theorem repairSeven (x y : Pos → F) (lost unknown : Finset Pos)
    (lostBound : lost.card ≤ 7) (unknownBound : unknown.card ≤ 9)
    (sameMix : ∀ j, j ∉ lost → mix x j = mix y j)
    (sameInput : ∀ j, j ∉ unknown → x j = y j) : x = y := by
  have hm : mix (x - y) = 0 := by
    refine sparse_vanish_on lost _ ?_ 1 ?_
    · intro j hj
      rw [mix_sub, sameMix j hj, sub_self]
    · intro k
      have hGain : gain (1 + k.val) = 0 := small_gains (Fin.castLE lostBound k)
      rw [spectrum_mix, hGain, zero_mul]
  have hz : x - y = 0 := by
    refine sparse_vanish_on unknown _ ?_ 8 ?_
    · intro j hj
      simp [sameInput j hj]
    · intro k
      have h := spectrum_mix (x - y) (8 + k.val)
      rw [hm] at h
      have zeroSpectrum : spectrum 0 (8 + k.val) = 0 := by simp [spectrum]
      rw [zeroSpectrum] at h
      exact (mul_eq_zero.mp h.symm).resolve_left (large_gains (Fin.castLE unknownBound k))
  exact sub_eq_zero.mp hz

/-- Each missing mixed reading spends one unit and each wrong reading spends two. -/
theorem repairDamaged (report x y : Pos → F)
    (erased badX badY unknown : Finset Pos) (errors : ℕ)
    (badXBound : badX.card ≤ errors) (badYBound : badY.card ≤ errors)
    (budget : 2 * errors + erased.card ≤ 7) (unknownBound : unknown.card ≤ 9)
    (fitX : ∀ j, j ∉ erased → j ∉ badX → mix x j = report j)
    (fitY : ∀ j, j ∉ erased → j ∉ badY → mix y j = report j)
    (sameInput : ∀ j, j ∉ unknown → x j = y j) : x = y := by
  refine repairSeven x y (erased ∪ (badX ∪ badY)) unknown ?_ unknownBound ?_ sameInput
  · have h₁ := Finset.card_union_le erased (badX ∪ badY)
    have h₂ := Finset.card_union_le badX badY
    omega
  · intro j hj
    simp only [Finset.mem_union, not_or] at hj
    exact (fitX j hj.1 hj.2.1).trans (fitY j hj.1 hj.2.2).symm

end TwoWeightMixer

#print axioms TwoWeightMixer.repairSeven
#print axioms TwoWeightMixer.repairDamaged
