import Development.AbelianVarietyTheory.Proofs.IwasawaDecomposition.GlobalArtinReciprocityHolds

/-!
Artin reciprocity for every number field, as the archive of the announced proof of the Riemann Hypothesis states and
proves it (mirror 1337isnot1337/riemann-hypothesis-solved at 6193bb5).

The statement: for a number field E with an algebraic closure, there is a homomorphism from the ideles of E to the
absolute Galois group made commutative (its topological abelianisation) which is continuous, open and onto; whose kernel
is the closure of the principal ideles times the connected part at the infinite places; and which at every finite place
sends the local units onto the image of inertia, each uniformiser to the inverse of a Frobenius element, and the local
multiplicative group densely onto the image of the decomposition group. It says such a map exists, not that it is the only one.

This file proves nothing new. It imports the archive's own file, asks Lean to print the statement, the structure it is
made of and three of the definitions that structure names (the others, for ideles, places above a prime, inertia, Frobenius
and the decomposition group, are in the archive's files and are not printed here), restates the first clause in Mathlib's
own words, and prints the axioms the proof depends on. The imported
file needs 306 of the archive's 175,187 files. To run this, build your copy of the archive as far as the module imported
above, then, from the archive's project folder:
    lake env lean /path/to/rh_artin.lean
-/

open GlobalTheory.HeckeGal

set_option pp.fullNames true
#check @GlobalTheory.globalArtinReciprocity_holds
#print GlobalTheory.Published.GlobalArtinReciprocity
#print GlobalTheory.HeckeGal.IsGlobalArtin
#print GlobalTheory.HeckeGal.Gab
#print GlobalTheory.HeckeGal.toAb
#print GlobalTheory.HeckeGal.infConn

/-- The first clause, unpacked: the map is onto, continuous and open. -/
theorem artin_map_onto_continuous_open (E Ω : Type) [Field E] [NumberField E] [Field Ω] [Algebra E Ω] [IsAlgClosure E Ω] :
    ∃ art : _ →* Gab E Ω, IsGlobalArtin art ∧ Function.Surjective art ∧ Continuous art ∧ IsOpenMap art := by
  obtain ⟨art, h⟩ := GlobalTheory.globalArtinReciprocity_holds E Ω
  exact ⟨art, h, h.quot.surjective, h.quot.continuous, h.quot.isOpenMap⟩

#print axioms GlobalTheory.globalArtinReciprocity_holds
#print axioms artin_map_onto_continuous_open
