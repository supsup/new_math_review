import Development.AutomorphicSpectrum.Proofs.GlobalProofs.HilbertClassFieldJ
import Development.AbelianVarietyTheory.Proofs.CubicalLineBundles.ExistsFieldCmCurvesUnitDiscriminant
import Development.AbelianVarietyTheory.Proofs.DivisorProofs.IsIntegralJOfNonrealMultiplierStatement

/-!
The theorem behind "e^(pi sqrt 163) is almost a whole number", as the archive of the announced proof of the Riemann
Hypothesis states and proves it (mirror 1337isnot1337/riemann-hypothesis-solved at 6193bb5), and one short consequence
of our own.

The archive's statement HilbertClassFieldJ: for a number field K of degree two with no real embedding, placed in the
complex numbers, and the grid L₀ made by its whole numbers, adjoining j of that grid to K gives the Hilbert class field
of K; the degree of that extension is the class number; two ideals have the same j exactly when they are in the same
class; and the conjugates of j over K are exactly the j of the ideal classes.

The archive also proves, outside its table of published results, that j of such a grid is an algebraic integer, in two
forms printed below.

This file proves nothing deep. It prints those statements and their axioms, and then puts two of them together: if the
class number is one, j of the grid is the image of one of K's own whole numbers. It does not prove that j is then an
ordinary whole number; that takes one more step (j is real), which is not done here.

Page: almost_a_whole_number.html.
-/

open NumberField GlobalTheory GlobalTheory.Published
open scoped nonZeroDivisors IntermediateField

set_option linter.all false

#check @GlobalTheory.CompanionTheory.Hypotheses₂.hilbertClassFieldJ
#print GlobalTheory.Published.HilbertClassFieldJ
#print GlobalTheory.Published.IsHilbertClassField
#print GlobalTheory.Published.IsUnramifiedAbelian
#print GlobalTheory.Published.IsIdealLattice
#print GlobalTheory.Published.idealInvariants
#check @GlobalTheory.T.isIntegral_j_of_nonreal_multiplier
#check @GlobalTheory.CMCurves.isIntegral_latticeJ
#check @GlobalTheory.Published.latticeCurve_j_eq

/-- j of the grid made by the whole numbers of K has no denominator. -/
theorem j_integral_of_ideal_lattice (K : Type) [Field K] [NumberField K] [Algebra K ℂ]
    (hK : Module.finrank ℚ K = 2) (L₀ : PeriodPair) (hL : IsIdealLattice (K := K) 1 L₀) :
    IsIntegral ℤ (latticeCurve L₀).j := by
  rw [latticeCurve_j_eq]
  refine GlobalTheory.CMCurves.isIntegral_latticeJ hK (algebraMap K ℂ) L₀ ?_
  intro a z hz
  have hz' : z ∈ (L₀.lattice : Set ℂ) := hz
  show algebraMap K ℂ (a : K) * z ∈ (L₀.lattice : Set ℂ)
  rw [hL] at hz' ⊢
  obtain ⟨x, hx, rfl⟩ := hz'
  refine ⟨(a : K) * x, ?_, by simp⟩
  have := (((1 : (FractionalIdeal (𝓞 K)⁰ K)ˣ).1 : FractionalIdeal (𝓞 K)⁰ K) : Submodule (𝓞 K) K).smul_mem a hx
  simpa [Algebra.smul_def] using this

/-- If the class number is one, j of that grid is one of K's own whole numbers. -/
theorem j_whole_of_class_number_one (K : Type) [Field K] [NumberField K] [IsTotallyComplex K] [Algebra K ℂ]
    (hK : Module.finrank ℚ K = 2) (h1 : classNumber K = 1)
    (L₀ : PeriodPair) (hL : IsIdealLattice (K := K) 1 L₀) :
    ∃ x : 𝓞 K, algebraMap K ℂ (x : K) = (latticeCurve L₀).j := by
  obtain ⟨-, hdeg, -⟩ := GlobalTheory.CompanionTheory.Hypotheses₂.hilbertClassFieldJ K hK L₀ hL
  rw [h1] at hdeg
  have hbot : K⟮(latticeCurve L₀).j⟯ = ⊥ := IntermediateField.finrank_eq_one_iff.mp hdeg
  have hmem : (latticeCurve L₀).j ∈ (⊥ : IntermediateField K ℂ) := IntermediateField.adjoin_simple_eq_bot_iff.mp hbot
  obtain ⟨y, hy⟩ := IntermediateField.mem_bot.mp hmem
  have hint := j_integral_of_ideal_lattice K hK L₀ hL
  rw [← hy] at hint
  have hy' : IsIntegral ℤ y := (isIntegral_algebraMap_iff (algebraMap K ℂ).injective).mp hint
  exact ⟨⟨y, hy'⟩, hy⟩

#print axioms GlobalTheory.CompanionTheory.Hypotheses₂.hilbertClassFieldJ
#print axioms GlobalTheory.T.isIntegral_j_of_nonreal_multiplier
#print axioms GlobalTheory.CMCurves.isIntegral_latticeJ
#print axioms j_integral_of_ideal_lattice
#print axioms j_whole_of_class_number_one
