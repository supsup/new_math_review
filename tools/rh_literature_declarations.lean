import Formalism.GammaFactorNonvanishing.CritLine
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopPlug
import Development.WeilBound.CoreStatements.StandardPublishedResults.StandardTheoremStatements.GreenRegularCharacters
import Development.AbelianVarietyTheory.Proofs.InertiaEigenvalues.SumRangeEqRoots
import Lean

/-!
Compare declaration reach with and without traversing the bodies of compiled
published proofs. This uses the same conditional implication as rh_two_inputs.lean
and the imported archive at 6193bb5. Run against the four built imports above:

    LEAN_PATH=<build paths> lean --tstack=400000 tools/rh_literature_declarations.lean

A qualifying theorem's type still contributes dependencies in the shortened
trace. The trace counts archive constants and their defining modules. It traverses
types and bodies of both theorems and definitions and retains constructor and
recursor ownership. Its theorem selector uses literal constant types from
GlobalTheory.Published and the three standard Lean axioms.
-/

namespace LiteratureReach

private theorem green : GlobalTheory.GLq.Green :=
  GlobalTheory.GreenBridge.green_of_regular PositivityTheory.Stage1.PM.greenRegularCharacters

private theorem conditional (budget : UpperTheory.Top.VWin)
    (family : Nonempty (GlobalTheory.Fc.HypsAlt
      (fun 𝒞 => Formalism.MainNotions.Closed 𝒞 fun Fm _ => Formalism.MainNotions.LinkN Fm)
      GlobalTheory.Fc.DefiniteSideCondition)) : RiemannHypothesis :=
  Formalism.VW.rh_of_every (UpperTheory.Top.every_character_of_green_v_win green budget family)

open Lean Elab Command

private def archiveRoots : Array Name :=
  #[`BuildAid, `CompanionTheory, `Development, `Formalism, `GroundTheory, `Lemmata,
    `Main, `PositivityTheory, `ReciprocityTheory, `Statements, `Supplements]

private def archiveModule (env : Environment) (name : Name) : Option ModuleIdx := do
  let index ← env.getModuleIdxFor? name
  let root := env.allImportedModuleNames[index]!.getRoot
  if archiveRoots.contains root then some index else none

private def literatureAnchors (env : Environment) : CommandElabM NameHashSet := do
  let mut anchors : NameHashSet := {}
  for (name, info) in env.constants.toList do
    if let .thmInfo info := info then
      if let .const statement _ := info.type then
        if statement.getPrefix == `GlobalTheory.Published && (archiveModule env name).isSome then
          let axioms ← Lean.collectAxioms name
          if axioms.all (fun ax => ax == `propext || ax == `Classical.choice || ax == `Quot.sound) then
            anchors := anchors.insert name
  return anchors

private structure Reach where
  declarations : Nat := 0
  modules : Std.HashSet ModuleIdx := {}
  anchors : NameHashSet := {}

private def traverse (env : Environment) (start : Name) (anchors : NameHashSet)
    (stopAtAnchors : Bool) : IO Reach := do
  let mut seen := ({} : NameHashSet).insert start
  let mut pending := #[start]
  let mut reach : Reach := {}
  while let some name := pending.back? do
    pending := pending.pop
    if let some index := archiveModule env name then
      reach := { reach with
        declarations := reach.declarations + 1
        modules := reach.modules.insert index }
    else unless name == ``green || name == ``conditional do
      continue
    let some info := env.find? name | throw (IO.userError s!"Missing constant {name}")
    let anchor := anchors.contains name
    if anchor then
      reach := { reach with anchors := reach.anchors.insert name }
    let body := if stopAtAnchors && anchor then #[] else
      (info.value? (allowOpaque := true)).map Expr.getUsedConstants |>.getD #[]
    let structural := match info with
      | .inductInfo val => val.ctors.toArray
      | .ctorInfo val => #[val.induct]
      | .recInfo val => val.all.toArray
      | _ => #[]
    for dep in info.type.getUsedConstants ++ body ++ structural do
      unless seen.contains dep do
        seen := seen.insert dep
        pending := pending.push dep
  return reach

#eval show CommandElabM Unit from do
  let env ← getEnv
  let anchors ← literatureAnchors env
  IO.println s!"Eligible compiled literature theorems: {anchors.size}"
  for (label, target) in [("Conditional RH", ``conditional), ("Green bridge", ``green)] do
    let full ← traverse env target anchors false
    let stop ← traverse env target anchors true
    let stops := stop.anchors.toList.toArray.qsort (fun x y => x.toString < y.toString)
    IO.println s!"{label}, declarations: {full.declarations} → {stop.declarations}"
    IO.println s!"{label}, modules: {full.modules.size} → {stop.modules.size}"
    IO.println s!"{label}, proof bodies skipped: {stops}"

end LiteratureReach
