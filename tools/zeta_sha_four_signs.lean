import Development.AutomorphicArithmetic.AutomorphicVarieties.LengthEqAddEigen

/-!
The archive splits its odd coefficient-prime lengths by complex conjugation.
Two commuting involutions split the same length into four pieces.
This file checks the eigenspace length identity for the archive's actual
Sha module. The companion note proves the field descent on paper.
-/

open NumberField Formalism.GaloisCohomology ReciprocityTheory.Gal UpperTheory.V

namespace ZetaSha

private theorem length_eq_four_eigen {R M : Type} [CommRing R] [AddCommGroup M] [Module R M]
    (h2 : IsUnit (2 : R)) (N : Submodule R M) (f g : Module.End R M)
    (hNf : ∀ x ∈ N, f x ∈ N) (hNg : ∀ x ∈ N, g x ∈ N)
    (hf : ∀ x, f (f x) = x) (hg : ∀ x, g (g x) = x)
    (hComm : ∀ x, f (g x) = g (f x)) :
    Module.length R N =
      (Module.length R ↥(N ⊓ f.eigenspace 1 ⊓ g.eigenspace 1) +
        Module.length R ↥(N ⊓ f.eigenspace 1 ⊓ g.eigenspace (-1))) +
      (Module.length R ↥(N ⊓ f.eigenspace (-1) ⊓ g.eigenspace 1) +
        Module.length R ↥(N ⊓ f.eigenspace (-1) ⊓ g.eigenspace (-1))) := by
  have hStable (s : R) (x : M) (hx : x ∈ N ⊓ f.eigenspace s) :
      g x ∈ N ⊓ f.eigenspace s := by
    refine ⟨hNg x hx.1, Module.End.mem_eigenspace_iff.mpr ?_⟩
    rw [hComm, Module.End.mem_eigenspace_iff.mp hx.2, map_smul]
  rw [length_eq_add_eigen h2 N f hNf hf 1 (one_mul 1)]
  rw [length_eq_add_eigen h2 (N ⊓ f.eigenspace 1) g (hStable 1) hg 1 (one_mul 1)]
  rw [length_eq_add_eigen h2 (N ⊓ f.eigenspace (-1)) g (hStable (-1)) hg 1 (one_mul 1)]

private theorem two_is_unit (l : ℕ) [Fact l.Prime] (hl : l ≠ 2) : IsUnit (2 : ℤ_[l]) := by
  by_contra hn
  have hmem : (2 : ℤ_[l]) ∈ IsLocalRing.maximalIdeal ℤ_[l] :=
    (IsLocalRing.mem_maximalIdeal _).mpr hn
  rw [← PadicInt.ker_toZMod, RingHom.mem_ker, map_ofNat] at hmem
  have hzero : ((2 : ℕ) : ZMod l) = 0 := by simpa using hmem
  rw [ZMod.natCast_eq_zero_iff] at hzero
  exact hl ((Nat.prime_dvd_prime_iff_eq Fact.out Nat.prime_two).mp hzero)

section Host

variable {E Ω : Type} [Field E] [NumberField E] [Field Ω] [Algebra E Ω] [IsAlgClosure E Ω]
  {l : ℕ} [Fact l.Prime]

noncomputable abbrev shaSign (D : LData E Ω l) (j : ℤ) (σ τ : E ≃+* E) (s t : ℤ_[l]) : ℕ∞ :=
  Module.length ℤ_[l] ↥(Sha D j ⊓ (galoisActionOnCohomology D j σ).eigenspace s ⊓
    (galoisActionOnCohomology D j τ).eigenspace t)

/-- At any odd coefficient prime, two commuting field involutions split the archive's length. -/
theorem shaLen_eq_four_signs (hl : l ≠ 2) (D : LData E Ω l) (j : ℤ)
    (σ τ : E ≃+* E) (hσ : σ * σ = 1) (hτ : τ * τ = 1) (hComm : σ * τ = τ * σ) :
    shaLen D j = (shaSign D j σ τ 1 1 + shaSign D j σ τ 1 (-1)) +
      (shaSign D j σ τ (-1) 1 + shaSign D j σ τ (-1) (-1)) := by
  apply length_eq_four_eigen (two_is_unit l hl) (Sha D j)
    (galoisActionOnCohomology D j σ) (galoisActionOnCohomology D j τ)
    (fun _ hx => galois_action_preserves_sha D j σ hx)
    (fun _ hx => galois_action_preserves_sha D j τ hx)
  · intro x
    rw [← Module.End.mul_apply, ← galois_action_cohomology_mul, hσ,
      galois_action_cohomology_one, Module.End.one_apply]
  · intro x
    rw [← Module.End.mul_apply, ← galois_action_cohomology_mul, hτ,
      galois_action_cohomology_one, Module.End.one_apply]
  · intro x
    rw [← Module.End.mul_apply, ← galois_action_cohomology_mul, hComm,
      galois_action_cohomology_mul, Module.End.mul_apply]

end Host

#print axioms shaLen_eq_four_signs

end ZetaSha
