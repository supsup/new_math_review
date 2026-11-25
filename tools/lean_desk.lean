/-
tools/lean_desk.lean: three read-only commands for asking a compiled Lean project about itself.

  #whereis a b c     every constant whose name ends in one of these, with its kind and the module that declares it
  #uses X Y          does the declaration X (its statement or its proof term) mention Y, directly or through
                     X's own auxiliary pieces (the parts Lean splits off, and internal names)
  #usedby X P Q      the declarations X mentions in that sense, restricted to names that start with P or Q

Nothing here adds an axiom, evaluates code from the project, or writes a file.

To use: in a project that is already built, make a file that starts with
    import <a module of the project>
    import Lean
followed by everything in this file below its own import line, followed by your questions; then
    lake env lean YourFile.lean
The questions put to the archive of the announced proof of the Riemann Hypothesis on 25 November 2026, and
Lean's answers word for word, are in crew_visuals/lean_desk.txt.  Written by Fixpoint for Marginalia.
-/
import Lean
open Lean Elab Command

namespace Desk

/-- Is `n` one of the pieces Lean makes on its own for the declaration `root` (a match, a proof split off, an equation lemma)? -/
def auxOf (root n : Name) : Bool :=
  n != root && root.isPrefixOf n

/-- The constants mentioned by `root`, looking through its own auxiliary pieces and through internal names. -/
partial def directUses (env : Environment) (root : Name) : NameSet := Id.run do
  let mut seen : NameSet := {}
  let mut out : NameSet := {}
  let mut todo : Array Name := #[root]
  while !todo.isEmpty do
    let n := todo.back!
    todo := todo.pop
    if seen.contains n then continue
    seen := seen.insert n
    match env.find? n with
    | none => pure ()
    | some ci =>
      for u in ci.getUsedConstantsAsSet do
        if auxOf root u || u.isInternalDetail then
          todo := todo.push u
        else
          out := out.insert u
  return out

def moduleOf (env : Environment) (n : Name) : String :=
  match env.getModuleIdxFor? n with
  | some idx => toString env.header.moduleNames[idx.toNat]!
  | none => "(this file)"

elab "#whereis " ids:ident+ : command => do
  let env ← getEnv
  let wanted : Array Name := ids.map (·.getId)
  let hits := env.constants.fold (init := (#[] : Array Name)) fun acc n _ =>
    if !n.isInternalDetail && wanted.any (fun w => w.isSuffixOf n) then acc.push n else acc
  let hits := hits.qsort (fun a b => a.toString < b.toString)
  let mut msg := m!"{hits.size} constant(s)"
  for h in hits do
    let kind := match env.find? h with
      | some (.thmInfo _) => "theorem"
      | some (.defnInfo _) => "def"
      | some (.axiomInfo _) => "AXIOM"
      | some (.opaqueInfo _) => "opaque"
      | some (.inductInfo _) => "inductive"
      | some (.ctorInfo _) => "constructor"
      | some (.recInfo _) => "recursor"
      | some (.quotInfo _) => "quot"
      | none => "?"
    msg := msg ++ m!"\n  {kind} {h}  [{moduleOf env h}]"
  logInfo msg

elab "#uses " x:ident y:ident : command => do
  let env ← getEnv
  let (a, b) := (x.getId, y.getId)
  unless env.contains a do throwError "unknown constant {a}"
  unless env.contains b do throwError "unknown constant {b}"
  let used := directUses env a
  logInfo m!"{a} uses {b}: {used.contains b}"

elab "#usedby " x:ident pre:ident* : command => do
  let env ← getEnv
  let a := x.getId
  unless env.contains a do throwError "unknown constant {a}"
  let prefixes : Array Name := pre.map (·.getId)
  let used := (directUses env a).toArray.filter fun n => prefixes.isEmpty || prefixes.any (·.isPrefixOf n)
  let used := used.qsort (fun p q => p.toString < q.toString)
  let mut msg := m!"{a} mentions {used.size} constant(s)" ++ (if prefixes.isEmpty then m!"" else m!" under {prefixes}")
  for u in used do
    msg := msg ++ m!"\n  {u}  [{moduleOf env u}]"
  logInfo msg

end Desk
