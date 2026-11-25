import Development.AutomorphicArithmetic.ThetaCorrespondence.Linnik

/-!
Linnik's theorem, as the archive of the announced proof of the Riemann Hypothesis states and proves it
(mirror 1337isnot1337/riemann-hypothesis-solved at 6193bb5).

The statement: there are positive numbers C and L such that, whenever a and q are whole numbers with no common factor,
the first prime that leaves the same remainder as a on division by q is at most C * q^L. No hypothesis is assumed.

This file proves nothing new. It imports the archive's own file and asks Lean to print the statement and the axioms its
proof depends on. That file needs 517 of the archive's 175,187 files. To run this, build your copy of the archive as far
as the module imported above, then, from the archive's project folder:
    lake env lean /path/to/rh_linnik.lean
-/

set_option pp.fullNames true
#check @UpperTheory.Lit.linnik
#print GlobalTheory.Published.Linnik
#print GlobalTheory.Published.leastPrimeMod
#print GlobalTheory.Published.primesInProgression
-- the statement is not empty: the archive proves it equivalent to "there is such a prime, and it is that small"
#check @GlobalTheory.Published.linnik_iff_exists_prime
#print axioms UpperTheory.Lit.linnik
