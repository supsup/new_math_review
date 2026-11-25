import Development.AbelianVarietyTheory.Proofs.FoundationProofs.BranchesAlongOfIrreducible

/-!
The branching rule from the invertible N by N complex matrices to the (N - 1) by (N - 1) ones, as the archive of the
announced proof of the Riemann Hypothesis states and proves it (mirror 1337isnot1337/riemann-hypothesis-solved at
6193bb5).

The statement WeylBranching: for every n from 1 up, with N = n + 1, and every row lam of N whole numbers that never
goes up, the archive's module for lam, acted on only by the n by n matrices in the top left corner, is the direct sum
of the modules for the rows mu that interlace lam (lam i >= mu i >= lam (i + 1)); the maps from the module of mu into
it that respect the action form a space of dimension one when mu interlaces lam and zero when it does not; and the same
when only the unitary n by n matrices act.

This file proves nothing. It asks Lean to print the statement, the definitions it rests on, and two lemmas from the
same proof file that the statement does not contain: the archive's modules are irreducible, for the whole group and for
the unitary group. Then it prints the axioms each of the three depends on.

Page: one_row_at_a_time.html.
-/

set_option linter.all false

#check @GlobalTheory.Published.weylBranching_holds
#print GlobalTheory.Published.WeylBranching
#print GlobalTheory.Branching.BranchesAlong
#print Formalism.MainNotions.PrimeDegreeVariant.Interlace
#print GlobalTheory.Branching.mult
#check @GlobalTheory.Branching.isIrreducible_smallRep_id
#check @GlobalTheory.Branching.isIrreducible_smallRep_unitary

#print axioms GlobalTheory.Published.weylBranching_holds
#print axioms GlobalTheory.Branching.isIrreducible_smallRep_id
#print axioms GlobalTheory.Branching.isIrreducible_smallRep_unitary
