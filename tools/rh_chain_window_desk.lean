/-
Replay this file inside the compiled archive project at 6193bb5 with Lean 4.33.1.
Use lake env lean /path/to/rh_chain_window_desk.lean after building the two imports.
The checks read declaration types and direct proof-term references.
The companion page explains which projected bounds the source formulas use.
-/
import Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopPlug
import Formalism.GammaFactorNonvanishing.CritLine
import Lean

open Lean Elab Command

set_option pp.fullNames true in
#check @Formalism.MainNotions.FamP.sizes

set_option pp.fullNames true in
#check @Formalism.MainNotions.Lnk.size_window_at_five

#check Formalism.LFunctionChainParameters.ThickSetMeanBounds.proposition_size_bound

run_cmd do
  let env ← getEnv
  let checks := [
    (`Formalism.MainNotions.linkGLOBAL7_items, `Formalism.MainNotions.Lnk.size_windows_of_thick_density),
    (`Formalism.MainNotions.Lnk.size_windows_of_thick_density, `Formalism.MainNotions.FamP.sizes),
    (`Formalism.MainNotions.Lnk.size_windows_of_thick_density, `Formalism.MainNotions.Lnk.size_window_at_five),
    (`Formalism.MainNotions.Lnk.size_window_at_five, `Formalism.MainNotions.Lnk.winA),
    (`Formalism.MainNotions.Lnk.size_window_at_five, `Formalism.MainNotions.Lnk.winB),
    (`Formalism.MainNotions.Lnk.size_window_at_five, `Formalism.MainNotions.Lnk.winL),
    (`Formalism.MainNotions.Lnk.linkCore, `Formalism.LFunctionChainParameters.LErr.ErrWindows0),
    (`Formalism.MainNotions.Lnk.linkCore, `Formalism.LFunctionChainParameters.LChain.RestSize),
    (`UpperTheory.Comparison₂.level_gm_le_on_family_scales, `UpperTheory.Comparison₂.tiedCore_of_chainTied),
    (`UpperTheory.Comparison₂.level_gm_le_on_family_scales, `UpperTheory.Comparison₂.windowInequality_of_artinInputs),
    (`UpperTheory.Comparison₂.windowInequality_of_artinInputs, `UpperTheory.Comparison₂.core_gm),
    (`UpperTheory.Comparison₂.core_gm, `Deduction.ch_core),
    (`Deduction.ch_core, `Formalism.LFunctionChainParameters.ThickSetMeanBounds.proposition_size_bound)
  ]
  for (first, second) in checks do
    let some (.thmInfo theoremInfo) := env.find? first | throwError "Missing theorem {first}"
    unless env.contains second do throwError "Missing {second}"
    unless theoremInfo.value.getUsedConstants.contains second do
      throwError "No direct proof-term edge {first} to {second}"
    logInfo m!"{first} → {second}"

#print axioms Formalism.MainNotions.Lnk.size_window_at_five
#print axioms Formalism.LFunctionChainParameters.ThickSetMeanBounds.proposition_size_bound
