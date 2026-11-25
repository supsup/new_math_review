import Formalism.GammaFactorNonvanishing.CritLine
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopShape
import Development.AutomorphicArithmetic.CharacterBoxes.ZeroFreeAllOfTopG
import Lean

open Lean Elab Command

namespace ExactDependencyUnion

structure Result where
  declarations : NameHashSet := {}
  modules : Std.HashSet ModuleIdx := {}
  mentions : Array Name := #[]
  extracts : Array Name := #[]

def takesExplicitConjunct (wanted : Name) (term : Expr) : Bool :=
  let isWanted (e : Expr) := e.getAppFn.constName? == some wanted
  let usesFirst : Expr → Bool
    | .lam _ _ (.lam _ _ body _) _ => body.hasLooseBVar 1
    | _ => false
  (term.find? fun e =>
    (e.isAppOf ``And.left && e.getAppNumArgs ≥ 3 && isWanted (e.getArg! 0)) ||
    (e.isAppOf ``And.casesOn && e.getAppNumArgs ≥ 5 && isWanted (e.getArg! 0) && usesFirst (e.getArg! 4)) ||
    (e.isAppOf ``And.rec && e.getAppNumArgs ≥ 5 && isWanted (e.getArg! 0) && usesFirst (e.getArg! 3))).isSome

def collect (env : Environment) (archiveRoots starts : Array Name)
    (wanted : Name) (includeLocals : Bool := false) : IO Result := do
  let mut result : Result := {}
  let mut scheduled : NameHashSet := {}
  let mut stack : Array Name := #[]
  for n in starts do
    if (env.find? n).isNone then
      throw <| IO.userError s!"Start {n} is absent"
    unless scheduled.contains n do
      stack := stack.push n
      scheduled := scheduled.insert n
  while let some n := stack.back? do
    stack := stack.pop
    let moduleId := env.getModuleIdxFor? n
    if let some idx := moduleId then
      let root := env.allImportedModuleNames[idx]!.getRoot
      unless archiveRoots.contains root do continue
      result := {result with modules := result.modules.insert idx}
    else
      unless includeLocals do continue
    let some info := env.find? n | continue
    result := {result with declarations := result.declarations.insert n}
    let typeNames := info.type.getUsedConstants
    let value := info.value? (allowOpaque := true)
    let valueNames := value.map Expr.getUsedConstants |>.getD #[]
    if typeNames.contains wanted || valueNames.contains wanted then
      result := {result with mentions := result.mentions.push n}
    if valueNames.contains wanted then
      if let some v := value then
        if takesExplicitConjunct wanted v then
          result := {result with extracts := result.extracts.push n}
    let structuralNames := match info with
      | .inductInfo val => val.ctors.toArray
      | .ctorInfo val => #[val.induct]
      | .recInfo val => val.all.toArray
      | _ => #[]
    for dep in typeNames ++ valueNames ++ structuralNames do
      unless scheduled.contains dep do
        scheduled := scheduled.insert dep
        stack := stack.push dep
  return result

end ExactDependencyUnion

#eval show CommandElabM Unit from do
  let env ← getEnv
  let roots := #[`BuildAid, `CompanionTheory, `Development, `Formalism, `GroundTheory, `Lemmata, `Main,
    `PositivityTheory, `ReciprocityTheory, `Statements, `Supplements]
  let wanted := `Formalism.MainNotions.PageWin
  let loaded := (env.allImportedModuleNames.filter fun n => roots.contains n.getRoot).size
  let stderr ← IO.getStderr
  stderr.putStrLn s!"Starting union traversal. {loaded} archive modules loaded."
  stderr.flush
  let result ← ExactDependencyUnion.collect env roots
    #[`UpperTheory.Top.shape_closed_link_n_of_green, `UpperTheory.Top.zeroFreeAll_of_topG] wanted
  IO.println s!"DEPENDS {result.declarations.size} archive declarations from {result.modules.size} archive modules ({loaded} imported)"
  IO.println s!"MENTION {wanted}: {result.mentions.size} constants in the union"
  IO.println s!"EXTRACT via explicit And recursor/projection, lower bound ({result.extracts.size}): {result.extracts}"
  for n in [`Formalism.MainNotions.Lnk.linkCore, `Formalism.MainNotions.Lnk.size_windows_of_thick_density,
    `Formalism.MainNotions.PageWin, `GlobalTheory.EX.DC.PageWin, `Formalism.L2.Top3.Duty] do
    IO.println s!"CLOSURE {n}: {result.declarations.contains n}"
