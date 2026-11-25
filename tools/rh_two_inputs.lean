import Formalism.GammaFactorNonvanishing.CritLine
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopPlug
import Development.WeilBound.CoreStatements.StandardPublishedResults.StandardTheoremStatements.GreenRegularCharacters
import Development.AbelianVarietyTheory.Proofs.InertiaEigenvalues.SumRangeEqRoots

/-!
# Two inputs, not three

tools/rh_outline.lean writes the last stretch of the announced proof of the Riemann Hypothesis as six steps from THREE
inputs: Green, VWin, and a record of hypotheses. This file removes the first.

The archive (mirror 1337isnot1337/riemann-hypothesis-solved at 6193bb5) proves Green's classification of 1955 in its own
files, in the published form (`GlobalTheory.Published.GreenRegularCharacters`), and has a short bridge from that form to the
form the route uses (`GlobalTheory.GLq.Green`). Both are compiled below, so Green is no longer assumed here, and the
conditional statement is left with two inputs. Nothing here is new mathematics: each line calls the archive's own theorem.

What it shows:   VWin and the record of hypotheses together imply the Riemann Hypothesis.
What it does not show:   that those two hold. The archive proves them in files we have not built.

To run it: build your copy of the archive as far as the four files imported above. The third and fourth need 19 archive
files beyond the first two. Then, from the archive's project folder:
    lake env lean --tstack=400000 /path/to/rh_two_inputs.lean
-/

set_option pp.fullNames true

-- the archive's proof of the classification, in its published form, and the bridge
#check @PositivityTheory.Stage1.PM.greenRegularCharacters
#print axioms PositivityTheory.Stage1.PM.greenRegularCharacters
#check @GlobalTheory.GreenBridge.green_of_regular

namespace RHTwoInputs

/-- The first input of tools/rh_outline.lean, with nothing assumed. -/
theorem green_holds : GlobalTheory.GLq.Green :=
  GlobalTheory.GreenBridge.green_of_regular PositivityTheory.Stage1.PM.greenRegularCharacters

/-- If the two remaining inputs hold, the Riemann Hypothesis holds. -/
theorem riemannHypothesis_of_two_inputs (input2 : UpperTheory.Top.VWin)
    (input3 : Nonempty (GlobalTheory.Fc.HypsAlt
      (fun 𝒞 => Formalism.MainNotions.Closed 𝒞 fun Fm _ => Formalism.MainNotions.LinkN Fm)
      GlobalTheory.Fc.DefiniteSideCondition)) : RiemannHypothesis :=
  Formalism.VW.rh_of_every (UpperTheory.Top.every_character_of_green_v_win green_holds input2 input3)

#print axioms green_holds
#print axioms riemannHypothesis_of_two_inputs

end RHTwoInputs
