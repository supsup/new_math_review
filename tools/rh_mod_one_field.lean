import Development.AutomorphicArithmetic.CharacterBoxes.ExistsPageN

/-!
The cyclotomic field test in the archive's modulus-one budget.
The character condition and its divisibility condition simplify by the
unique residue modulo one. The power-of-two and Jacobi tests remain
explicit in this equivalent proposition.

Replay in the compiled archive at 6193bb5 with Lean 4.33.1:
    lake env lean /path/to/rh_mod_one_field.lean
-/
open Formalism.HC UpperTheory.Top

private theorem one_val (a : ℕ) : PChar.one.val a = 1 := by
  change (1 : DirichletCharacter ℂ 1) (a : ZMod 1) = 1
  rw [Subsingleton.elim (a : ZMod 1) 1, map_one]

theorem isChiField_mod_one_iff (e q d : ℕ) (E : Type) [Field E] [NumberField E] :
    IsChiField PChar.one e q d E ↔
      ∃ (N : ℕ) (_ : NeZero N) (j : E →ₐ[ℚ] CyclotomicField N ℚ)
        (ζ : CyclotomicField N ℚ),
        2 ^ (e + 2) ∣ N ∧ q ∣ N ∧ d ∣ N ∧ IsPrimitiveRoot ζ N ∧
        ∀ (τ : CyclotomicField N ℚ ≃ₐ[ℚ] CyclotomicField N ℚ) (a : ℕ),
          τ ζ = ζ ^ a →
            ((∀ x : E, τ (j x) = j x) ↔
              (a ≡ 1 [MOD 2 ^ (e + 2)] ∨ a + 1 ≡ 0 [MOD 2 ^ (e + 2)]) ∧
              jacobiSym (a : ℤ) q = 1 ∧ jacobiSym (a : ℤ) d = 1) := by
  have h : PChar.one.N = 1 := rfl
  simp [IsChiField, h, one_val]

#print axioms isChiField_mod_one_iff
