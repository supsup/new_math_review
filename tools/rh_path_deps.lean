/-
rh_path_deps.lean: ask Lean, instead of reading, whether the left branch of the trail picture in rh_proof_map.html
holds. Written by Confluence on 2026-11-25; to be run UNCHANGED by Fixpoint in the archive's own project (mirror
1337isnot1337/riemann-hypothesis-solved at 6193bb5, Lean 4.33.1, Mathlib 0df444a360ea), from the folder that holds
the archive's lakefile:   lake env lean --tstack=400000 rh_path_deps.lean
It imports only modules already built in the closure of Formalism.GammaFactorNonvanishing.CritLine, and contains
none of the archive's text: only declaration names. The DepCheck core between the two marker lines is byte for
byte the core of rh_path_deps_toy.lean, whose control must print TOY CONTROL PASSED first (plain `lean`, no project).
Every line it prints is a measurement; the last line says how many answers differed from the hand trace.
-/
import Formalism.GammaFactorNonvanishing.CritLine
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.ShapeOf
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopShape
import Development.AutomorphicArithmetic.CharacterBoxes.DesWin
import Development.AutomorphicArithmetic.CharacterBoxes.ZeroFreeAllOfTopG
import Development.AbelianVarietyTheory.Proofs.GlobalInterpolation.LinkGl
import Formalism.SharpRestriction.GlobalTheoremInputs
import Formalism.SharpRestriction.GlobalSchurBounds.LogXLowerFamilyOfTheorems
import Formalism.SharpRestriction.GlobalSchurBounds.LinkMin
import Formalism.SharpRestriction.GlobalSchurBounds.LossesSmallShares
import Formalism.LocalToGlobal.ClassOfRecordOfChoice
import Formalism.LocalRingCardinality.DataRows
import Formalism.SharpRestriction.PageFix

-- ===== DepCheck core (Confluence, 2026-11-25). The same bytes run in the toy control and in the archive run. =====
-- What it asks Lean: which declarations does a declaration's statement or proof term mention, transitively?
-- "Mentions" = the constants in its type and its value (definitions, theorems, opaque constants), plus the
-- constructors of an inductive type, the type of a constructor, and the types of a recursor. Only constants
-- from the project's own modules are followed (Mathlib and Lean core are not expanded: they cannot mention
-- the project). Names are resolved by SUFFIX against every constant, and every match is reported, so a name
-- defined more than once shows up instead of being silently chosen.
open Lean Elab Command

namespace DepCheck

def valueOf : ConstantInfo → Option Expr
  | .defnInfo v => some v.value
  | .thmInfo v => some v.value
  | .opaqueInfo v => some v.value
  | _ => none

def directDeps (ci : ConstantInfo) : NameSet := Id.run do
  let mut s : NameSet := {}
  for n in ci.type.getUsedConstants do s := s.insert n
  if let some v := valueOf ci then
    for n in v.getUsedConstants do s := s.insert n
  match ci with
  | .inductInfo v => for c in v.ctors do s := s.insert c
  | .ctorInfo v => s := s.insert v.induct
  | .recInfo v => for c in v.all do s := s.insert c
  | _ => pure ()
  return s

/-- the module a constant comes from; `none` for constants declared in the file being run -/
def moduleOf (n : Name) : CommandElabM (Option Name) := do
  let env ← getEnv
  match env.getModuleIdxFor? n with
  | some i => return some (env.allImportedModuleNames[i]!)
  | none => return none

/-- project constants: declared in this file, or in a module whose first component is a project root -/
def isProject (roots : List Name) (n : Name) : CommandElabM Bool := do
  match ← moduleOf n with
  | none => return true
  | some m => return roots.contains m.getRoot

def kindOf : ConstantInfo → String
  | .thmInfo _ => "theorem" | .defnInfo _ => "def" | .opaqueInfo _ => "opaque" | .axiomInfo _ => "AXIOM"
  | .inductInfo _ => "inductive" | .ctorInfo _ => "constructor" | .recInfo _ => "recursor" | .quotInfo _ => "quot"

/-- every project constant whose name ends with the given components (private names included) -/
def resolve (roots : List Name) (suffix : Name) : CommandElabM (Array Name) := do
  let env ← getEnv
  let cands := env.constants.fold (fun acc n _ => if suffix.isSuffixOf n then acc.push n else acc) #[]
  let mut out := #[]
  for n in cands do
    if ← isProject roots n then out := out.push n
  return out.qsort (fun a b => a.toString < b.toString)

/-- all project constants reachable from `starts` through types and values -/
def closure (roots : List Name) (starts : Array Name) : CommandElabM NameSet := do
  let env ← getEnv
  let mut seen : NameSet := {}
  let mut stack := starts
  while !stack.isEmpty do
    let n := stack.back!
    stack := stack.pop
    if seen.contains n then continue
    let some ci := env.find? n | continue
    unless ← isProject roots n do continue
    seen := seen.insert n
    for m in (directDeps ci).toList do
      unless seen.contains m do stack := stack.push m
  return seen

def say (s : String) : CommandElabM Unit := IO.println s

def showNames (ns : Array Name) : CommandElabM String := do
  let env ← getEnv
  let mut parts := #[]
  for n in ns do
    let k := match env.find? n with | some ci => kindOf ci | none => "?"
    let m := match ← moduleOf n with | some m => toString m | none => "(this file)"
    parts := parts.push s!"{n} [{k}, {m}]"
  return if parts.isEmpty then "NONE FOUND" else ", ".intercalate parts.toList

/-- From each declaration named `upper` (every match), compute once: its closure, and what it mentions itself or
through its own auxiliary parts (upper.proof_1, upper.match_1, ...). Then answer each target, and count surprises.
A target is (name, expected transitive answer, expected direct answer or none). -/
def checkFrom (roots : List Name) (upper : Name) (targets : List (Name × Bool × Option Bool)) : CommandElabM Nat := do
  let env ← getEnv
  let us ← resolve roots upper
  say s!"FROM {upper} = {← showNames us}"
  if us.isEmpty then
    say s!"  CANNOT CHECK: {upper} is not among the project constants loaded here"
    return targets.length
  let mut found : Array (NameSet × NameSet) := #[]
  for u in us do
    let cl ← closure roots #[u]
    let mut dw : NameSet := {}
    for a in cl.toList do
      if a == u || u.isPrefixOf a then
        if let some ci := env.find? a then
          for d in (directDeps ci).toList do dw := dw.insert d
    say s!"  closure of {u}: {cl.toList.length} project constants"
    found := found.push (cl, dw)
  let mut bad := 0
  for (lower, expT, expD) in targets do
    let ls ← resolve roots lower
    if ls.isEmpty then
      say s!"  -> {lower}: not among the loaded project constants{if expT then "; UNEXPECTED" else " (expected no; trivially absent)"}"
      if expT then bad := bad + 1
      continue
    let mut trans := false
    let mut direct := false
    for (cl, dw) in found do
      for l in ls do
        if cl.contains l && !us.contains l then trans := true
        if dw.contains l && !us.contains l then direct := true
    let okT := trans == expT
    let okD := match expD with | some e => direct == e | none => true
    let verdict := if okT && okD then "as expected" else "UNEXPECTED"
    unless okT && okD do bad := bad + 1
    say s!"  -> {lower} = {← showNames ls}: transitive {if trans then "YES" else "no"}, direct {if direct then "YES" else "no"}; {verdict}"
  return bad

def axiomsOf (roots : List Name) (short : Name) : CommandElabM Unit := do
  for n in ← resolve roots short do
    let ax ← collectAxioms n
    say s!"AXIOMS {n}: {ax.toList}"

/-- Does a term TAKE OUT a conjunct whose type is headed by one of `targets`? `And.left` with that type on the left
counts; so does `And.casesOn` / `And.rec` with that type on the left when the body uses the left binder. Stepping over
it (`And.right`, or a binder the body never uses) does not count, although the term still MENTIONS the type, because a
projection names the types it steps over. Other forms (compiled `match` auxiliaries, raw projections) are not detected,
so a "no" here is not proof that the conjunct is unused. -/
def extracts (targets : Array Name) (e : Expr) : Bool :=
  let isT (t : Expr) : Bool := match t.getAppFn.constName? with | some c => targets.contains c | none => false
  let usedLeft (minor : Expr) : Bool := match minor with
    | .lam _ _ (.lam _ _ body _) _ => body.hasLooseBVar 1
    | _ => true
  (e.find? fun x =>
     (x.isAppOf ``And.left && x.getAppNumArgs ≥ 3 && isT (x.getArg! 0)) ||
     (x.isAppOf ``And.casesOn && x.getAppNumArgs ≥ 5 && isT (x.getArg! 0) && usedLeft (x.getArg! 4)) ||
     (x.isAppOf ``And.rec && x.getAppNumArgs ≥ 5 && isT (x.getArg! 0) && usedLeft (x.getArg! 3))).isSome

end DepCheck
-- ===== end of DepCheck core =====

#eval show CommandElabM Unit from do
  let r : List Name := [`BuildAid, `CompanionTheory, `Development, `Formalism, `GroundTheory, `Lemmata, `Main,
    `PositivityTheory, `ReciprocityTheory, `Statements, `Supplements]
  let env ← getEnv
  let mods := env.allImportedModuleNames.filter (fun m => r.contains m.getRoot)
  DepCheck.say s!"LOADED: {mods.size} archive modules imported (of {env.allImportedModuleNames.size} modules in all)"
  let mut bad := 0
  -- the hand-traced hops, top to bottom (34758, 34760); YES means "the upper one's statement or proof mentions it"
  bad := bad + (← DepCheck.checkFrom r `GlobalTheory.Fc.forall_goal_of_shape_of_hyps
    [(`GlobalTheory.Fc.goal_of_shape_of_hyps, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `UpperTheory.Top.shape_closed_link_n_of_green
    [(`GlobalTheory.Top.link_gl, true, some true), (`UpperTheory.Top.topDesWin, true, some true),
     (`linkCore, true, none), (`ChainTied, true, none), (`LinkN, true, none), (`SizeData₂.lifts, true, none),
     (`Duty, true, none), (`PageWin, true, none),
     (`PDVS.DefiniteLiftChain, false, none), (`stmt3c, false, none), (`familyDefiniteLiftChain, false, none),
     (`ThetaChainStatement, false, none)])
  bad := bad + (← DepCheck.checkFrom r `UpperTheory.Top.topDesWin
    [(`LinkGLOBAL, true, some true), (`LinkN, true, some true), (`DIVinN, true, none), (`ChainTied, true, none)])
  bad := bad + (← DepCheck.checkFrom r `GlobalTheory.Top.link_gl
    [(`FamGLmin.link8, true, some true), (`Duty, true, some true), (`linkCore, true, none)])
  bad := bad + (← DepCheck.checkFrom r `FamGLmin.link8 [(`FamGLmin.link7, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `FamGLmin.link7 [(`linkGLOBAL7_min, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `linkGLOBAL7_min [(`linkGLOBAL7_items, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `linkGLOBAL7_items [(`linkCore, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `linkCore
    [(`ChainTied, true, none), (`GlobalTheory.Top.link_gl, false, some false), (`UpperTheory.Top.topDesWin, false, some false)])
  bad := bad + (← DepCheck.checkFrom r `LinkGLOBAL [(`ChainTied, true, some true), (`linkCore, false, some false)])
  bad := bad + (← DepCheck.checkFrom r `LinkN [(`SizeData₂.lifts, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `UpperTheory.Top.zeroFreeAll_of_topG
    [(`ChainTied, true, some true), (`level_gm_le_on_family_scales, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `ChainTied [(`linkCore, false, some false), (`LinkGLOBAL, false, some false)])
  -- which Duty and which PageWin: the ones in link_gl's STATEMENT, and the ones anywhere below the shape theorem
  for u in ← DepCheck.resolve r `GlobalTheory.Top.link_gl do
    let ci ← getConstInfo u
    let ts := ci.type.getUsedConstants.filter (fun n => (`Duty).isSuffixOf n || (`PageWin).isSuffixOf n)
    DepCheck.say s!"DUTY in the statement of {u}: {← DepCheck.showNames ts}"
  DepCheck.say s!"ALL Duty loaded: {← DepCheck.showNames (← DepCheck.resolve r `Duty)}"
  DepCheck.say s!"ALL PageWin loaded: {← DepCheck.showNames (← DepCheck.resolve r `PageWin)}"
  let roots ← DepCheck.resolve r `UpperTheory.Top.shape_closed_link_n_of_green
  let zf ← DepCheck.resolve r `UpperTheory.Top.zeroFreeAll_of_topG
  let cl ← DepCheck.closure r (roots ++ zf)
  let used := cl.toList.toArray
  let dutyIn := used.filter (fun n => (`Duty).isSuffixOf n || (`PageWin).isSuffixOf n)
  DepCheck.say s!"Duty/PageWin BELOW the path theorems: {← DepCheck.showNames (dutyIn.qsort (fun a b => a.toString < b.toString))}"
  -- MENTIONS PageWin: a projection names every conjunct type it steps over, so this is NOT use (34830)
  -- EXTRACTS PageWin: And.left with PageWin on the left, or And.casesOn/And.rec whose PageWin binder the body uses
  let pw ← DepCheck.resolve r `PageWin
  let mut touch := #[]
  let mut take := #[]
  for n in used do
    if let some ci := env.find? n then
      if (DepCheck.directDeps ci).toList.any (fun d => pw.contains d) then touch := touch.push n
      if let some v := DepCheck.valueOf ci then
        if DepCheck.extracts pw v then take := take.push n
  DepCheck.say s!"MENTION PageWin, below the path ({touch.size}; NOT the same as use): {← DepCheck.showNames ((touch.qsort (fun a b => a.toString < b.toString)).extract 0 40)}"
  DepCheck.say s!"EXTRACT the PageWin conjunct, below the path ({take.size}; a lower bound, see extracts): {← DepCheck.showNames ((take.qsort (fun a b => a.toString < b.toString)).extract 0 40)}"
  -- how much of what is imported does the path depend on
  let mut pmods : NameSet := {}
  for n in used do
    if let some m ← DepCheck.moduleOf n then pmods := pmods.insert m
  DepCheck.say s!"DEPENDS: below shape_closed_link_n_of_green and zeroFreeAll_of_topG: {used.size} archive constants from {pmods.toList.length} archive modules, of the {mods.size} archive modules imported here"
  for s in [`UpperTheory.Top.shape_closed_link_n_of_green, `UpperTheory.Top.zeroFreeAll_of_topG, `UpperTheory.Top.topDesWin,
            `GlobalTheory.Top.link_gl, `FamGLmin.link8, `linkCore] do
    DepCheck.axiomsOf r s
  DepCheck.say (if bad == 0 then "PATH: every answer matches the hand trace" else s!"PATH: {bad} answer(s) DIFFER from the hand trace")
