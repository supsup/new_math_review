import Lean

/- rh_path_deps_toy.lean: the control for rh_path_deps.lean. Run with plain `lean rh_path_deps_toy.lean` (Lean 4.33.1, no project); it must print TOY CONTROL PASSED. -/
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

-- ===== Toy control: every check below must come out as expected, or the collector is wrong =====
def ToyA : Nat := 1
theorem toy_b : ToyA = 1 := rfl
theorem toy_c : ToyA = 1 := toy_b                 -- toy_b appears only in the PROOF
theorem toy_h : ToyA = 1 := toy_c                 -- reaches toy_b only THROUGH toy_c
theorem toy_d : True := trivial                   -- unrelated
def ToyDuty (n : Nat) : Prop := n = 1 ∧ ToyA = n
theorem toy_e (h : ToyDuty 1) : ToyA = 1 := h.2    -- ToyDuty in the STATEMENT
theorem toy_f : True := by                        -- toy_b hidden inside a tactic proof
  have _x : ToyA = 1 := toy_b
  trivial
theorem toy_s : (1 : Nat) = 2 := sorry            -- a placeholder, for the axiom report
def TP (n : Nat) : Prop := n = n
def TQ (n : Nat) : Prop := n + 0 = n
def TDuty (n : Nat) : Prop := TQ n ∧ TP n ∧ TQ n        -- TP sits in the middle, like PageWin inside Duty
theorem uses_tp (h : TDuty 3) : TP 3 := h.2.1                                  -- takes TP out
theorem skips_tp (h : TDuty 3) : TQ 3 := h.2.2                                 -- steps over TP
theorem rc_tp (h : TDuty 3) : TP 3 := by obtain ⟨_, hp, _⟩ := h; exact hp      -- takes TP out by a pattern
theorem rc_skip (h : TDuty 3) : TQ 3 := by obtain ⟨hq, _, _⟩ := h; exact hq    -- destructures, never uses TP
namespace Other
def ToyA : Nat := 2                               -- a second ToyA: resolution must report both
end Other

#eval show CommandElabM Unit from do
  let r : List Name := []                         -- toy: only this file's constants count as project
  let mut bad := 0
  bad := bad + (← DepCheck.checkFrom r `toy_c [(`toy_b, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `toy_h [(`toy_b, true, some false), (`toy_c, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `toy_f [(`toy_b, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `toy_e [(`ToyDuty, true, some true)])
  bad := bad + (← DepCheck.checkFrom r `toy_d [(`toy_b, false, some false)])
  bad := bad + (← DepCheck.checkFrom r `toy_b [(`toy_c, false, some false)])
  let both ← DepCheck.resolve r `ToyA
  DepCheck.say s!"RESOLVE ToyA = {← DepCheck.showNames both}"
  unless both.size == 2 do bad := bad + 1
  DepCheck.axiomsOf r `toy_c
  DepCheck.axiomsOf r `toy_s
  let axS ← collectAxioms `toy_s
  let axC ← collectAxioms `toy_c
  unless axS.contains `sorryAx && !axC.contains `sorryAx do bad := bad + 1
  for (n, want) in [(`uses_tp, true), (`skips_tp, false), (`rc_tp, true), (`rc_skip, false)] do
    let some ci := (← getEnv).find? n | bad := bad + 1
    let got := match DepCheck.valueOf ci with | some v => DepCheck.extracts #[`TP] v | none => false
    let mentions := (DepCheck.directDeps ci).contains `TP
    DepCheck.say s!"EXTRACTS TP {n}: {got} (expected {want}); mentions TP: {mentions}"
    unless got == want && mentions do bad := bad + 1
  DepCheck.say (if bad == 0 then "TOY CONTROL PASSED" else s!"TOY CONTROL FAILED: {bad} unexpected")
