import Mathlib

open Polynomial

namespace FourLossMixer

local instance : Fact (Nat.Prime 61) := ⟨by decide⟩

/-- The 60 sample addresses are nonzero powers of an element of order 60. -/
theorem addressOrder : orderOf (35 : ZMod 61) = 60 := by
  apply orderOf_eq_of_pow_and_pow_div_prime (by decide) (by decide)
  intro q hq hdiv
  have check : ∀ i : Fin 61, i.val.Prime → i.val ∣ 60 →
      ((35 : ZMod 61) ^ (60 / i.val)) ≠ 1 := by decide
  exact check ⟨q, Nat.lt_succ_of_le (Nat.le_of_dvd (by decide) hdiv)⟩ hq hdiv

def address (j : Fin 60) : ZMod 61 := 35 ^ j.val

theorem address_injective : Function.Injective address := by
  intro i j hij
  apply Fin.ext
  have hi : i.val ∈ Set.Iio (orderOf (35 : ZMod 61)) := by simp [addressOrder, i.isLt]
  have hj : j.val ∈ Set.Iio (orderOf (35 : ZMod 61)) := by simp [addressOrder, j.isLt]
  exact pow_injOn_Iio_orderOf hi hj hij

/-- The four geometric-progression roots used in the degree-three model. -/
theorem fourRootEvaluations : ∀ k : Fin 4,
    let r : ZMod 61 := 42 * 35 ^ k.val
    r ^ 60 = 1 ∧ 1 + r + r ^ 4 + r ^ 51 + r ^ 52 = 0 := by decide

/-- Four distinct probes determine exactly one cubic after normalization. -/
theorem fourProbes (probes : Fin 4 → Fin 60) (distinct : Function.Injective probes)
    (values : Fin 4 → ZMod 61) :
    ∃! f : (ZMod 61)[X], f.degree < 4 ∧
      ∀ j, f.eval (address (probes j)) = values j := by
  let s : Finset (Fin 4) := Finset.univ
  let v : Fin 4 → ZMod 61 := address ∘ probes
  have hv : Set.InjOn v s := (address_injective.comp distinct).injOn
  have characteristic (f : (ZMod 61)[X]) :
      (f.degree < 4 ∧ ∀ j, f.eval (v j) = values j) ↔ f = Lagrange.interpolate s v values := by
    simpa [s] using (Lagrange.eq_interpolate_iff (f := f) (r := values) hv)
  exact ⟨_, (characteristic _).2 rfl, fun f hf => (characteristic f).1 hf⟩

end FourLossMixer

#print axioms FourLossMixer.addressOrder
#print axioms FourLossMixer.fourRootEvaluations
#print axioms FourLossMixer.fourProbes
