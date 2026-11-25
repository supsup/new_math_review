import Formalism.GammaFactorNonvanishing.CritLine
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopPlug
import Lean

/-!
Replay inside the compiled CritLine and TopPlug project at archive revision
6193bb5 with Lean 4.33.1: lake env lean /path/to/rh_hypothesis_bundle.lean

Inspect named projection constants and primitive structure projections in
declaration values. The base-level selector puts its proof of pin in a
generated auxiliary theorem, which is checked separately.
-/

open Lean Elab Command

def projectedFields (env : Environment) (owner : Name) (term : Expr) : Array Name := Id.run do
  let fields := getStructureFields env owner
  let names := term.getUsedConstants
  let mut used := #[]
  for i in [:fields.size] do
    let field := fields[i]!
    let byName := (getProjFnForField? env owner field).any names.contains
    let byIndex := (term.find? fun e =>
      match e with
      | .proj source j _ => source == owner && j == i
      | _ => false).isSome
    if byName || byIndex then
      used := used.push field
  return used

#eval show CommandElabM Unit from do
  let env ← getEnv
  let record := `GlobalTheory.Fc.HypsAlt
  let bundle := `GlobalTheory.Fc.BundleCondition
  let fields := getStructureFields env record
  let inner := getStructureFields env bundle
  let .thmInfo theoremInfo ← getConstInfo `GlobalTheory.Fc.goal_of_shape_of_hyps
    | throwError "Expected the theorem joining the fields to the route"
  let used := projectedFields env record theoremInfo.value
  unless fields.size == 46 && fields == used do
    throwError "Expected all 46 fields to be projected: {used}"
  unless inner == #[`R, `S, `P, `pin, `DH, `C, `B] do
    throwError "Unexpected per-index bundle fields: {inner}"
  IO.println s!"goal_of_shape_of_hyps projects all {used.size} fields: {used}"
  IO.println s!"BundleCondition has {inner.size} fields: {inner}"

  for (name, expected) in [
    (`GlobalTheory.Fc.familySelection, `R),
    (`GlobalTheory.Fc.spectralConditionOfRawSelection, `S),
    (`GlobalTheory.Fc.baseLevelChoiceOfRawSelection, `P),
    (`GlobalTheory.Fc.baseLevelChoiceOfRawSelection._proof_1, `pin),
    (`GlobalTheory.Fc.definiteHeightOfRawSelection, `DH),
    (`GlobalTheory.Fc.columnChoiceOfRawSelection, `C),
    (`GlobalTheory.Fc.selectionBundleOfRawSelection, `B)] do
    let some value := (← getConstInfo name).value? (allowOpaque := true)
      | throwError "No definition value at {name}"
    let actual := projectedFields env bundle value
    unless actual == #[expected] do
      throwError "{name} projected {actual}, expected {expected}"
    IO.println s!"{name} projects {expected}"

-- The scope of this build is the two compiled import closures at 6193bb5.
-- Check presence by full declaration name, including the outer call sites.
#eval show CommandElabM Unit from do
  let env ← getEnv
  for (name, expected) in [
    (`UpperTheory.Top.every_character_of_green_v_win, true),
    (`Formalism.VW.rh_of_every, true),
    (`GlobalTheory.GreenBridge.green_of_regular, false),
    (`UpperTheory.One.vwin_of_row, false),
    (`UpperTheory.Lit.nonempty_hyps_definite_side_of_closed_bound, false),
    (`UpperTheory.Lit.every_character_of_theta_integrals_local_matching, false),
    (`UpperTheory.LiteratureTheorems.every_character_of_literature_of_vWin, false),
    (`UpperTheory.FinalTheorems.everyCharacter_of_row, false),
    (`UpperTheory.Gal.Int.galoisLocalGlobalStrong_recParameter, false),
    (`allChi, false),
    (`rhOfAll, false)] do
    let found := (env.find? name).isSome
    unless found == expected do throwError "Unexpected availability of {name}: {found}"
    IO.println s!"{name}: loaded = {found}"
