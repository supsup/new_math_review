import Development.AutomorphicArithmetic.AutomorphicVarieties.OddResidueBounds.ThmBcOfPsiBound

open NumberField Formalism.GaloisCohomology UpperTheory.Top UpperTheory.V

namespace ZetaOddCutoff

/-- Stickelberger's individual estimates bound the total contribution of the odd
minus lengths below a cutoff, including primes that divide the conductor. -/
theorem small_minus_budget :
    ∃ C : ℝ, 0 ≤ C ∧
      ∀ (E Ω : Type) [Field E] [NumberField E] [IsCMField E] [Field Ω]
        [Algebra E Ω] [IsAlgClosure E Ω] (N : ℕ), 0 < N →
      Nonempty (E →ₐ[ℚ] CyclotomicField N ℚ) →
      ∀ (t L : ℕ), 2 ≤ t → 2 ≤ L →
      ∀ (ld : ∀ (p : ℕ) [Fact p.Prime], LData E Ω p),
        (∀ (p : ℕ) [Fact p.Prime], p ≠ 2 → ∀ j : ℕ, 1 ≤ j →
          minusLen (ld p) j ≠ ⊤) ∧
        ∀ S : Finset Nat.Primes, (∀ p ∈ S, (p : ℕ) ≠ 2 ∧ (p : ℕ) ≤ L) →
          (∑ j ∈ Finset.Ico 1 t, ∑ p ∈ S,
            Real.log (p : ℕ) *
              ((@minusLen E Ω _ _ _ _ _ _ p ⟨p.2⟩ (@ld p ⟨p.2⟩) j).toNat : ℝ))
          ≤ C * (Module.finrank ℚ E : ℝ)^2 * (t : ℝ)^2 * (L : ℝ)^2 *
              (Real.log ((t : ℝ) * L * N))^2 := by
  obtain ⟨C, hC, hStick⟩ := Odd.stickBound
  refine ⟨C, hC, ?_⟩
  intro E Ω _ _ _ _ _ _ N hN hEmb t L ht hL ld
  refine ⟨fun p _ hp j hj => (hStick E Ω N hN hEmb p (ld p) (Or.inl hp) j hj).1, ?_⟩
  intro S hS
  have hcard : S.card ≤ L := calc
    S.card = (S.image fun p : Nat.Primes => (p : ℕ)).card :=
      (Finset.card_image_of_injective _ Subtype.val_injective).symm
    _ ≤ (Finset.Icc 1 L).card := by
      apply Finset.card_le_card
      intro i hi
      obtain ⟨p, hp, rfl⟩ := Finset.mem_image.mp hi
      exact Finset.mem_Icc.mpr ⟨p.2.one_lt.le, (hS p hp).2⟩
    _ = L := by simp
  have hjcard : (Finset.Ico 1 t).card ≤ t := by simp
  have ht' : (1 : ℝ) ≤ t := by exact_mod_cast (show 1 ≤ t by omega)
  have hL' : (1 : ℝ) ≤ L := by exact_mod_cast (show 1 ≤ L by omega)
  have hN' : (1 : ℝ) ≤ N := by exact_mod_cast hN
  have hlog : 0 ≤ Real.log ((t : ℝ) * L * N) :=
    Real.log_nonneg (one_le_mul_of_one_le_of_one_le
      (one_le_mul_of_one_le_of_one_le ht' hL') hN')
  let M : ℝ :=
    C * L * (Module.finrank ℚ E : ℝ)^2 * t * (Real.log ((t : ℝ) * L * N))^2
  have hM : 0 ≤ M := by dsimp [M]; positivity
  calc
    _ ≤ ∑ _j ∈ Finset.Ico 1 t, ∑ _p ∈ S, M := by
      apply Finset.sum_le_sum
      intro j hj
      obtain ⟨hj₁, hj₂⟩ := Finset.mem_Ico.mp hj
      apply Finset.sum_le_sum
      intro p hp
      have hterm := (@hStick E Ω _ _ _ _ _ _ N hN hEmb p ⟨p.2⟩
        (@ld p ⟨p.2⟩) (Or.inl (hS p hp).1) j hj₁).2
      have hj₁' : (1 : ℝ) ≤ j := by exact_mod_cast hj₁
      have hp₁' : (1 : ℝ) ≤ (p : ℕ) := by exact_mod_cast p.2.one_lt.le
      have hj₂' : (j : ℝ) + 1 ≤ t := by exact_mod_cast (show j + 1 ≤ t by omega)
      have hp₂' : ((p : ℕ) : ℝ) ≤ L := by exact_mod_cast (hS p hp).2
      have hpos : 0 < (j : ℝ) * (p : ℕ) * N := by positivity
      have hnonneg : 0 ≤ Real.log ((j : ℝ) * (p : ℕ) * N) :=
        Real.log_nonneg (one_le_mul_of_one_le_of_one_le
          (one_le_mul_of_one_le_of_one_le hj₁' hp₁') hN')
      have hle : Real.log ((j : ℝ) * (p : ℕ) * N) ≤ Real.log ((t : ℝ) * L * N) :=
        Real.log_le_log hpos (by gcongr)
      calc
        _ ≤ C * (p : ℕ) * (Module.finrank ℚ E : ℝ)^2 * ((j : ℝ) + 1) *
          (Real.log ((j : ℝ) * (p : ℕ) * N))^2 := by simpa [mul_comm (Real.log _)] using hterm
        _ ≤ M := by dsimp [M]; gcongr
    _ = ((Finset.Ico 1 t).card : ℝ) * S.card * M := by
      simp [Finset.sum_const, nsmul_eq_mul, mul_assoc]
    _ ≤ (t : ℝ) * L * M := by gcongr
    _ = _ := by dsimp [M]; ring

/-- A bound on all odd plus terms and a bound on the large odd minus terms
suffice, together with the dyadic bound, to assemble the full budget. -/
theorem vvle_of_odd_cutoff :
    ∃ C : ℝ, 0 ≤ C ∧
      ∀ (E : Type) [Field E] [NumberField E] [IsCMField E] (N : ℕ), 0 < N →
      Nonempty (E →ₐ[ℚ] CyclotomicField N ℚ) →
      ∀ (t L : ℕ), 2 ≤ t → 2 ≤ L →
      ∀ (B₂ Bplus Blarge : ℝ),
        BoundedHeightTwoPlaceCondition E t B₂ →
        VVplusLe E t Bplus →
        (∀ (Ω : Type) [Field Ω] [Algebra E Ω] [IsAlgClosure E Ω]
          (ld : ∀ (p : ℕ) [Fact p.Prime], LData E Ω p)
          (S : Finset Nat.Primes), (∀ p ∈ S, L < (p : ℕ)) →
          (∑ p ∈ S, Real.log (p : ℕ) * ∑ j ∈ Finset.Ico 1 t,
            ((@minusLen E Ω _ _ _ _ _ _ p ⟨p.2⟩ (@ld p ⟨p.2⟩) j).toNat : ℝ)) ≤ Blarge) →
        VVle E t (B₂ * Real.log 2 +
          (C * (Module.finrank ℚ E : ℝ)^2 * (t : ℝ)^2 * (L : ℝ)^2 *
            (Real.log ((t : ℝ) * L * N))^2 + Blarge) + Bplus) := by
  obtain ⟨C, hC, hCutoff⟩ := small_minus_budget
  refine ⟨C, hC, ?_⟩
  intro E _ _ _ N hN hEmb t L ht hL B₂ Bplus Blarge h₂ hplus hlarge
  refine vvle_of_parts h₂ ?_ hplus
  intro Ω _ _ _ ld
  obtain ⟨hfinite, hsmall⟩ := hCutoff E Ω N hN hEmb t L ht hL ld
  refine ⟨fun p _ j hp hj _ => hfinite p hp j hj, ?_⟩
  intro S hS
  rw [← Finset.sum_filter_add_sum_filter_not S (fun p : Nat.Primes => (p : ℕ) ≤ L)]
  apply add_le_add
  · simp_rw [Finset.mul_sum]
    rw [Finset.sum_comm]
    exact hsmall _ (fun p hp =>
      ⟨hS p (Finset.mem_filter.mp hp).1, (Finset.mem_filter.mp hp).2⟩)
  · exact hlarge Ω ld _ (fun p hp => Nat.lt_of_not_ge (Finset.mem_filter.mp hp).2)

#print axioms small_minus_budget
#print axioms vvle_of_odd_cutoff

end ZetaOddCutoff
