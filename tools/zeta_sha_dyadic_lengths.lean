import Development.AutomorphicArithmetic.AutomorphicVarieties.PartsConj

/-!
A length inequality for an involution without dividing by 2.
The arithmetic descent for the modulus-one host is in the companion note.
-/

open NumberField Formalism.GaloisCohomology ReciprocityTheory.Gal UpperTheory.V

namespace ZetaDyadic

private theorem length_le_add_eigenspaces {R M : Type} [CommRing R]
    [AddCommGroup M] [Module R M] (N : Submodule R M) (f : Module.End R M)
    (hN : ∀ x ∈ N, f x ∈ N) (hf : ∀ x, f (f x) = x) :
    Module.length R N ≤ Module.length R ↥(N ⊓ f.eigenspace 1) +
      Module.length R ↥(N ⊓ f.eigenspace (-1)) := by
  let plus : ↥(N ⊓ f.eigenspace 1) →ₗ[R] N := Submodule.inclusion inf_le_left
  let diff : N →ₗ[R] M := N.subtype - f ∘ₗ N.subtype
  let minus : N →ₗ[R] ↥(N ⊓ f.eigenspace (-1)) :=
    diff.codRestrict _ (fun x => by
      change (x : M) - f x ∈ N ⊓ f.eigenspace (-1)
      refine ⟨N.sub_mem x.2 (hN x x.2), Module.End.mem_eigenspace_iff.mpr ?_⟩
      rw [map_sub, hf, neg_one_smul, neg_sub])
  have hPlus : Function.Injective plus := Submodule.inclusion_injective _
  have hExact : Function.Exact plus minus.rangeRestrict := by
    intro x
    constructor
    · intro hx
      have hMinus : minus x = 0 := congrArg Subtype.val hx
      have hd : (x : M) - f x = 0 :=
        congrArg (fun y : ↥(N ⊓ f.eigenspace (-1)) => (y : M)) hMinus
      have hx1 : (x : M) ∈ f.eigenspace 1 := Module.End.mem_eigenspace_iff.mpr
        (by rw [one_smul]; exact (sub_eq_zero.mp hd).symm)
      exact ⟨⟨x, x.2, hx1⟩, rfl⟩
    · rintro ⟨x, rfl⟩
      apply Subtype.ext
      apply Subtype.ext
      change (x : M) - f x = 0
      rw [Module.End.mem_eigenspace_iff.mp x.2.2, one_smul, sub_self]
  rw [Module.length_eq_add_of_exact plus minus.rangeRestrict hPlus
    (LinearMap.surjective_rangeRestrict _) hExact]
  exact add_le_add_right (Module.length_le_of_injective
    (LinearMap.range minus).subtype (Submodule.subtype_injective _)) _

section Host

variable {E Ω : Type} [Field E] [NumberField E] [Field Ω] [Algebra E Ω] [IsAlgClosure E Ω]
  {l : ℕ} [Fact l.Prime]

/-- An involution bounds the archive's length by its two sign lengths at every coefficient prime. -/
theorem shaLen_le_add_signs (D : LData E Ω l) (j : ℤ)
    (σ : E ≃+* E) (hσ : σ * σ = 1) :
    shaLen D j ≤
      Module.length ℤ_[l] ↥(Sha D j ⊓ (galoisActionOnCohomology D j σ).eigenspace 1) +
      Module.length ℤ_[l] ↥(Sha D j ⊓ (galoisActionOnCohomology D j σ).eigenspace (-1)) := by
  apply length_le_add_eigenspaces _ _ (fun _ hx => galois_action_preserves_sha D j σ hx)
  intro x
  rw [← Module.End.mul_apply, ← galois_action_cohomology_mul, hσ,
    galois_action_cohomology_one, Module.End.one_apply]

end Host

#print axioms shaLen_le_add_signs

end ZetaDyadic
