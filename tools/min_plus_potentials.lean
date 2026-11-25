import Mathlib.Data.Real.Basic
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Tactic.Linarith

/-! Two finite elimination steps used by the min-plus potential visual. -/

namespace MinPlusPotential

open Finset

variable {I J K : Type} [Fintype I] [Nonempty I]

private theorem allRowsNonempty : (univ : Finset I).Nonempty := by
  obtain ⟨i⟩ := ‹Nonempty I›
  exact ⟨i, mem_univ i⟩

/-- Eliminating each middle potential gives a lower bound from the closing
edge and one upper bound from each two-edge path. -/
theorem sharedPotential_iff_additiveEnvelope (A : I → J → ℝ) (B : J → K → ℝ)
    (C : I → K → ℝ) :
    (∃ (u : I → ℝ) (m : J → ℝ) (v : K → ℝ),
      (∀ i j, m j - u i ≤ A i j) ∧
      (∀ j k, v k - m j ≤ B j k) ∧
      (∀ i k, C i k ≤ v k - u i)) ↔
    (∃ (u : I → ℝ) (v : K → ℝ),
      (∀ i k, C i k ≤ v k - u i) ∧
      (∀ i j k, v k - u i ≤ A i j + B j k)) := by
  constructor
  · rintro ⟨u, m, v, hu, hv, hc⟩
    refine ⟨u, v, hc, fun i j k => ?_⟩
    linarith [hu i j, hv j k]
  · rintro ⟨u, v, hc, hd⟩
    let m (j : J) := univ.inf' allRowsNonempty (fun i => u i + A i j)
    refine ⟨u, m, v, ?_, ?_, hc⟩
    · intro i j
      have h : m j ≤ u i + A i j := inf'_le _ (mem_univ i)
      linarith
    · intro j k
      have h : v k - B j k ≤ m j := by
        apply le_inf'
        intro i _
        linarith [hd i j k]
      linarith

/-- A column potential fits all its intervals exactly when every lower
endpoint is at most every upper endpoint. This eliminates the columns. -/
theorem additiveEnvelope_iff_rowPotential (C D : I → K → ℝ) :
    (∃ (u : I → ℝ) (v : K → ℝ),
      ∀ i k, C i k ≤ v k - u i ∧ v k - u i ≤ D i k) ↔
    (∃ u : I → ℝ, ∀ i r k, u r - u i ≤ D i k - C r k) := by
  constructor
  · rintro ⟨u, v, h⟩
    refine ⟨u, fun i r k => ?_⟩
    linarith [(h i k).2, (h r k).1]
  · rintro ⟨u, h⟩
    let v (k : K) := univ.sup' allRowsNonempty (fun r => C r k + u r)
    refine ⟨u, v, fun i k => ⟨?_, ?_⟩⟩
    · have hh : C i k + u i ≤ v k := le_sup' (fun r => C r k + u r) (mem_univ i)
      linarith
    · have hh : v k ≤ D i k + u i := by
        apply sup'_le
        intro r _
        linarith [h i r k]
      linarith

#print axioms sharedPotential_iff_additiveEnvelope
#print axioms additiveEnvelope_iff_rowPotential

end MinPlusPotential
