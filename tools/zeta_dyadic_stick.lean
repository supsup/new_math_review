import Development.AutomorphicArithmetic.AutomorphicVarieties.OddResidueBounds.ThmBcOfPsiBound

/-!
Specialize the archive's StickBound to coefficient prime 2 in a CM field
with a primitive fourth root of unity. The paper descent and application
to the modulus-one host are in crew_visuals/zeta_dyadic_class_numbers.txt.

Use the archive at 6193bb5, Lean 4.33.1 and Mathlib 0df444a. Build the
archive module OddResidueBounds.ThmBcOfPsiBound before running this file.
    lake env lean --tstack=400000 /path/to/zeta_dyadic_stick.lean
-/

open NumberField Formalism.ConjugateSelfDual ReciprocityTheory.Gal
  Formalism.GaloisCohomology UpperTheory.V

namespace ZetaDyadic

local instance : Fact (2 : ℕ).Prime := ⟨Nat.prime_two⟩

private theorem procyc_of_fourth_root (E Ω : Type) [Field E] [NumberField E]
    [Field Ω] [Algebra E Ω] [IsAlgClosure E Ω] {ζ : E} (hζ : IsPrimitiveRoot ζ 4) :
    Kum.Procyc E Ω 2 := by
  right
  intro σ
  have : IsAlgClosed Ω := IsAlgClosure.isAlgClosed E
  have : CharZero Ω := charZero_of_injective_algebraMap (algebraMap E Ω).injective
  have : NeZero (2 : Ω) := ⟨by norm_num⟩
  let t := algebraMap E Ω ζ
  have ht : IsPrimitiveRoot t (2 ^ 2) := hζ.map_of_injective (algebraMap E Ω).injective
  let a : ZMod (2 ^ 2) := (Kum.cycR E Ω 2 2 σ : (ZMod (2 ^ 2))ˣ)
  have h₁ : σ t = t ^ a.val :=
    cyclotomicCharacter.spec (L := Ω) 2 (MulSemiringAction.toRingAut (G E Ω) Ω σ) t ht.pow_eq_one
  have h₂ : σ t = t := σ.commutes ζ
  apply Units.ext
  apply ZMod.val_injective
  apply ht.pow_inj (ZMod.val_lt a) (ZMod.val_lt 1)
  rw [← h₁, h₂]
  change t = t ^ (1 : ℕ)
  rw [pow_one]

/-- The archived polynomial estimate for the minus length at coefficient prime 2. -/
theorem stickBound_at_two_with_fourth_root :
    ∃ C : ℝ, 0 ≤ C ∧
      ∀ (E Ω : Type) [Field E] [NumberField E] [IsCMField E] [Field Ω] [Algebra E Ω]
        [IsAlgClosure E Ω] (N : ℕ), 0 < N →
        Nonempty (E →ₐ[ℚ] CyclotomicField N ℚ) →
        (∃ ζ : E, IsPrimitiveRoot ζ 4) → ∀ (D : LData E Ω 2) (j : ℕ), 1 ≤ j →
          minusLen D j ≠ ⊤ ∧ ((minusLen D j).toNat : ℝ) * Real.log 2 ≤
            C * 2 * (Module.finrank ℚ E : ℝ) ^ 2 * (j + 1) *
              Real.log ((j : ℝ) * 2 * N) ^ 2 := by
  obtain ⟨C, hC, h⟩ := Odd.stickBound
  refine ⟨C, hC, ?_⟩
  intro E Ω _ _ _ _ _ _ N hN hE ⟨ζ, hζ⟩ D j hj
  exact h E Ω N hN hE 2 D (procyc_of_fourth_root E Ω hζ) j hj

#print axioms UpperTheory.V.Odd.stickBound
#print axioms stickBound_at_two_with_fourth_root

end ZetaDyadic
