import Formalism.GammaFactorNonvanishing.CritLine
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopPlug

/-!
# The top of the route to the Riemann Hypothesis, as six short steps

This file is an OUTLINE, checked by Lean. It is not a new proof and not a shorter proof.

It takes the last stretch of the announced proof of the Riemann Hypothesis (the archive mirrored at
1337isnot1337/riemann-hypothesis-solved, revision 6193bb5) and writes it as six named steps of one line
each, so that a reader can see the shape of the argument and Lean can confirm that the steps fit together.
Every step is a theorem of the archive, used here under its own name. Nothing is assumed except the
THREE INPUTS below, and Lean's three standard axioms.

What it shows:   Input 1, Input 2 and Input 3 together imply the Riemann Hypothesis.
What it does not show:   that the three inputs hold. The archive proves them in other files, which we
have not built (crew_visuals/lean_runs.txt, section 3 and section 4).

To run it: you need your own copy of the archive, built as far as the two files imported above
(crew_visuals/lean_runs.txt says how; that build took about three hours here). Then, from the archive's
project folder:   lake env lean --tstack=400000 /path/to/rh_outline.lean
It prints the axioms the last theorem depends on, and takes a few seconds.

Written by Fixpoint for Marginalia, 25 November 2026, after a question from a reader:
could the proof be made simpler in Lean, from what we learned?

A genuinely simpler variant is beside this file: tools/rh_mod_one_budget.lean, by Marlow, reaches the
same conclusion with Input 2 asked for one character only, the one whose L-function is the zeta function.
This file keeps to the archive's own route.
-/

namespace RHOutline

/-! ## The three inputs (assumed here; proved by the archive elsewhere) -/

/-- Input 1, the archive's `Green`: a classification of certain characters of the groups of invertible
matrices over a finite field (J. A. Green, 1955). A small worked case: crew_visuals/green_six_matrices.html. -/
abbrev Input1 : Prop := GlobalTheory.GLq.Green

/-- Input 2, the archive's `VWin`: for each primitive Dirichlet character, on a range of scales, one budget
that bounds weighted lengths of certain Galois-cohomology groups. A toy: crew_visuals/vwin_weighted_lengths.html. -/
abbrev Input2 : Prop := UpperTheory.Top.VWin

/-- The class of families the third input speaks about: those closed under the archive's condition `LinkN`. -/
abbrev LinkedClass : Formalism.MainNotions.FamClass → Prop :=
  fun 𝒞 => Formalism.MainNotions.Closed 𝒞 fun Fm _ => Formalism.MainNotions.LinkN Fm

/-- Input 3, a record of 46 hypotheses about that class of families (the archive's `HypsAlt`).
Opened into its pieces: crew_visuals/rh_hypothesis_bundle.html. -/
abbrev Input3 : Prop :=
  Nonempty (GlobalTheory.Fc.HypsAlt LinkedClass GlobalTheory.Fc.DefiniteSideCondition)

/-! ## The statements in between, under plain names -/

/-- No Dirichlet L-function has a zero with real part greater than one half
(apart from the pole case the statement excludes). The archive's `EveryCharacter`. -/
abbrev NoZerosRightOfTheLine : Prop := UpperTheory.EveryCharacter

/-- The same for primitive characters only. The archive's `ZeroFreeAll`. -/
abbrev NoZerosForPrimitiveCharacters : Prop := Formalism.HC.ZeroFreeAll

/-- The archive's `TopG`, its main statement about classes of families. The proof map describes it. -/
abbrev MainComparison : Prop := UpperTheory.Top.TopG

/-- For one primitive character, the bound the main comparison needs, at the parameter 3/2. -/
abbrev BoundFor (ψ : Formalism.HC.PChar) : Prop := GlobalTheory.EX.HostExW (3 / 2) (UpperTheory.Top.GChi ψ).req

/-- The archive's `TopShapeAlt`: "if the hypotheses of Input 3 hold for the linked class, the main comparison holds". -/
abbrev Shape : Prop := GlobalTheory.Fc.TopShapeAlt True True LinkedClass MainComparison

/-! ## The six steps -/

/-- Step 1, the mirror. In the critical strip, the functional equation pairs zeros across the line of real
part one half. If there are no zeros to the right, reflection clears the left side too, and every zero in
the strip is on the line. (This is the step that is NOT enough on its own: how_a_zero_leaves_the_line.html.) -/
theorem step1_mirror : NoZerosRightOfTheLine → RiemannHypothesis :=
  Formalism.VW.rh_of_every

/-- Step 2. From primitive characters to all characters. -/
theorem step2_all_characters : NoZerosForPrimitiveCharacters → NoZerosRightOfTheLine :=
  UpperTheory.Top.imprimitive

/-- Step 3, the assembly. The main comparison, with the bound for each primitive character, leaves no zeros. -/
theorem step3_assembly : MainComparison → (∀ ψ, BoundFor ψ) → NoZerosForPrimitiveCharacters :=
  fun comparison bounds => UpperTheory.Top.zeroFreeAll_of_topG (la := 3 / 2) (by norm_num) comparison bounds

/-- Step 4. Input 2 supplies the bound, one character at a time. -/
theorem step4_bounds : Input2 → ∀ ψ, BoundFor ψ :=
  fun input2 ψ => UpperTheory.Top.supplyChi ψ (input2 ψ)

/-- Step 5. Input 1 gives the shape of the argument. -/
theorem step5_shape : Input1 → Shape :=
  UpperTheory.Top.shape_closed_link_n_of_green

/-- Step 6. Input 3 fills the shape in, and the main comparison follows. -/
theorem step6_comparison : Shape → Input3 → MainComparison :=
  fun shape input3 => input3.elim fun hyps =>
    GlobalTheory.Fc.forall_goal_of_shape_of_hyps _ _ _ _ shape trivial trivial hyps

/-! ## All six together -/

/-- If the three inputs hold, the Riemann Hypothesis holds. -/
theorem riemannHypothesis_of_three_inputs (input1 : Input1) (input2 : Input2) (input3 : Input3) :
    RiemannHypothesis :=
  step1_mirror
    (step2_all_characters
      (step3_assembly
        (step6_comparison (step5_shape input1) input3)
        (step4_bounds input2)))

#print axioms riemannHypothesis_of_three_inputs

end RHOutline
