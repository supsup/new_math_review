import Formalism.GammaFactorNonvanishing.CritLine
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopPlug
import Development.AutomorphicArithmetic.ThetaCorrespondence.Linnik
import Lean

/-!
Which statements in the archive's namespace `GlobalTheory.Published` have a finished proof among the files loaded here?

The archive (the announced proof of the Riemann Hypothesis, mirror 1337isnot1337/riemann-hypothesis-solved at 6193bb5)
keeps the published results it relies on as definitions of type `Prop` in that namespace, and proves them in its own
files. This asks Lean, for the files imported below, which of those statements have a theorem of exactly that type, and
what axioms each such theorem depends on. It is a lower bound: a proof whose stated type is the definition written out,
and not its name, is not counted.

To run it you need your own copy of the archive built as far as the three files imported below (the third needs two files
beyond the first two; crew_visuals/lean_runs.txt says how). Then, from the archive's project folder:
    lake env lean --tstack=400000 /path/to/rh_published_sweep.lean
It reads the compiled files and prints; it writes nothing.
-/
open Lean Elab Command

#eval show CommandElabM Unit from do
  let env ← getEnv
  let pubNs := `GlobalTheory.Published
  -- the statements: Prop-valued definitions directly in the namespace
  let mut stmts : Array Name := #[]
  for (n, ci) in env.constants.toList do
    if n.getPrefix == pubNs && ci.type.isProp then
      match ci with
      | .defnInfo _ => stmts := stmts.push n
      | _ => pure ()
  let stmtSet : NameSet := stmts.foldl (fun s n => s.insert n) {}
  IO.println s!"STATEMENTS loaded in GlobalTheory.Published (Prop-valued definitions): {stmts.size}"
  -- the proofs: theorems whose type is literally one of those names
  let mut found : Array (Name × Name) := #[]
  for (n, ci) in env.constants.toList do
    match ci with
    | .thmInfo _ =>
      match ci.type with
      | .const t _ => if stmtSet.contains t then found := found.push (t, n)
      | _ => pure ()
    | _ => pure ()
  let sorted := found.qsort fun a b => a.1.toString < b.1.toString || (a.1 == b.1 && a.2.toString < b.2.toString)
  let mut proved : NameSet := {}
  for (t, n) in sorted do
    let axs ← Lean.collectAxioms n
    let m := match env.getModuleIdxFor? n with | some i => env.allImportedModuleNames[i]!.toString | none => "(this file)"
    proved := proved.insert t
    IO.println s!"PROOF {t.replacePrefix pubNs .anonymous} := {n}  [{m}]  axioms {axs.qsort (fun a b => a.toString < b.toString)}"
  IO.println s!"PROVED statements: {proved.size} of {stmts.size} loaded; theorems of that exact type: {sorted.size}"
  let missing := (stmts.filter fun n => !proved.contains n).qsort fun a b => a.toString < b.toString
  IO.println s!"LOADED BUT NO PROOF LOADED ({missing.size}): {missing.map fun n => n.replacePrefix pubNs .anonymous}"
