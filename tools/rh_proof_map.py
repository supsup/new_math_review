"""Write rh_proof_map.html: a map of the Lean proof of the Riemann Hypothesis, for a reader who is not a number theorist.

Run from the repository root:  python3 -I tools/rh_proof_map.py

Numbers come from crew_visuals/rh_proof_map_data.json (written by tools/rh_archive_index.py from the archive itself).
The cards below are written by hand, and each one says who read what. The page is static: it has no script, and this
builder refuses to write it if the numbers do not add up.
"""
import html
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
e = html.escape


def num(n):
    return f"{n:,}"


# ---- the last steps, top down. status: "read" (statement read), "wiring" (the proof term read, the statements it
# ---- names not yet), who: the seats that read it.
SPINE_CARDS = [
    {"key": "riemannHypothesis", "status": "read", "who": "Fixpoint",
     "lean": "theorem riemannHypothesis : RiemannHypothesis := rhOfAll",
     "where": "Main.lean, 12 lines in all",
     "plain": "The file that states the result. It says that the Riemann Hypothesis, exactly as the Lean library Mathlib defines it, "
              "is proved by a term called rhOfAll. The same file has four companion declarations: one more for zeta and three for Dirichlet L-functions."},
    {"key": "rh_of_every", "status": "read", "who": "Fixpoint and Lattice",
     "lean": "theorem Formalism.VW.rh_of_every (h : UpperTheory.EveryCharacter) : RiemannHypothesis",
     "where": "Formalism/GammaFactorNonvanishing/CritLine.lean, lines 11 to 32",
     "plain": "The last step, and the only short one. Suppose no L-function has a zero to the right of the line. A zero to the LEFT of the line "
              "would have a mirror image to the right of it (the functional equation), so there are none on the left either. "
              "Every zero in the strip is therefore on the line. Lattice's page 'Why only the center line remains' lets you drag this. "
              "This is the first step we ran through Lean ourselves: copied out byte for byte and compiled on its own with "
              "Lean 4.33.1 against the version of Mathlib the archive pins, it is accepted, and it rests only on Lean's three standard "
              "axioms. Two deliberately wrong versions are rejected. The script tools/rh_mirror_step.py rebuilds that check from your own "
              "copy of the archive. That check covers this step and nothing below it. Later the same day we compiled this step's own file "
              "together with every archive file it imports; the record of our Lean runs says what that covers."},
    {"key": "EveryCharacter", "status": "read", "who": "Fixpoint",
     "lean": "def UpperTheory.EveryCharacter : Prop := ∀ N χ s, 1/2 < s.re → (χ ≠ 1 ∨ s ≠ 1) → LFunction χ s ≠ 0",
     "where": "Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean, line 13",
     "plain": "The statement the last step needs: for every Dirichlet character, the L-function has no zero whose real part is above one half. "
              "One point is set aside: s = 1 for the trivial character, where zeta has its pole. Zeta is the simplest case."},
    {"key": "window", "status": "read", "who": "Lattice",
     "lean": "Gm x ≤ x^(1/2 + (eD + eL + 7)·ε)   on family windows",
     "where": "Formalism/SharpRestriction/RamificationFrobenius/TotientGaloisClasses/TopWin.lean line 26; Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/TopPlug.lean lines 11 to 18; Development/AutomorphicArithmetic/CharacterBoxes/Imprimitive.lean lines 5 to 28",
     "plain": "Lattice's reading: the right-half statement is deduced from a one-sided bound on a sum over 'windows'. "
              "If some L-function had a zero to the right of the line, the bound would fail once ε is chosen small against that zero's excess. "
              "In the Lean the bounded quantity is zeta's own term plus a weighted sum over the other characters, so the code handles a whole "
              "package of characters at once. A second file extends the result from primitive characters to all characters."},
    {"key": "everyCharacter", "status": "wiring", "who": "Fixpoint and Lattice",
     "lean": "everyCharacter := everyCharacter_of_row galoisLocalGlobalStrong_recParameter",
     "where": "Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean, lines 7 to 14",
     "plain": "How the bound is supplied. The code combines a statement called VWin with a package of three statements called "
              "OpenLiteratureStatements, and fills in all three right here: two by the same statement about Galois representations, "
              "one by a statement about local dictionaries. The next three cards say what VWin and those statements are."},
    {"key": "vwin", "status": "read", "who": "Lattice",
     "lean": "UpperTheory.Top.VWin",
     "where": "Development/AutomorphicArithmetic/CharacterBoxes/ExistsPageN.lean, lines 12 to 49",
     "plain": "Lattice's reading: for each primitive character one can find a window from Y to Y squared on which certain weighted sums "
              "of lengths of finite Galois-cohomology modules stay bounded. It is an arithmetic input, a control on denominators, "
              "and it is a different window from the analytic one, Y to Y^(3/2), in the card above."},
    {"key": "llc", "status": "read", "who": "Confluence",
     "lean": "localLanglandsExists : UpperTheory.Zero.LLC.RecTExists",
     "where": "Development/AutomorphicArithmetic/Foundations/LocalLanglands/IsRecTOfIsRec.lean, line 78 (scope: GoodCusp, line 20)",
     "plain": "A dictionary exists, in a restricted form. For every number field and every finite place, there is a map from the irreducible "
              "representations of GL_n over the local field to Weil-Deligne representations, obeying a list of laws. "
              "The strong laws are demanded only for a class the code calls Good. So this is not 'the local Langlands correspondence' in full, "
              "and we do not call it that."},
    {"key": "row", "status": "read", "who": "Confluence",
     "lean": "caraianiLocalGlobalDual, galoisRepOfPolarizedPairLit : UpperTheory.One.M.Row   (that is, GalStar.Row0b)",
     "where": "Foundations/UnitarySphericalFixing/SatakeParameters/RecT.lean line 6; GaloisRepresentations/TypeConditions/WeightsConjBis.lean line 69",
     "plain": "Galois representations exist for a family of automorphic forms. For every CM field E, every prime l, and every automorphic "
              "representation of GL_n over E of a certain kind (regular algebraic, polarized, cuspidal), there is a continuous l-adic Galois "
              "representation of E that matches it place by place away from l, with matching weights. "
              "Not yet read: exactly how strong the conditions away from l and above l are."},
    {"key": "galoisLocalGlobalStrong_recParameter", "status": "wiring", "who": "Fixpoint",
     "lean": "galoisLocalGlobalStrong_recParameter := galoisRepresentations_of_thetaLift UpperTheory.TP.K.tLiftK\n"
             "galoisRepresentations_of_thetaLift (up : TLiftK) := galoisLocalGlobalStrong_of_geometry_lift geoOne_holds up",
     "where": "Development/AutomorphicArithmetic/Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean, line 6; GaloisRepresentationsOfThetaLift.lean, line 6",
     "plain": "Where the code visibly meets the author's description below. The statement about Galois representations is obtained from two "
              "things: the existence of theta lifts (next card), and a statement the code calls geoOne_holds, which we have not read."},
    {"key": "galoisLocalGlobal_of_geometry_lift", "status": "wiring", "who": "Fixpoint",
     "lean": "galoisLocalGlobal_of_geometry_lift geo up := rest (coreAll_of (seedFinOdd_of_geoOne geo) (congFinOdd_of_ex wtLacEx_holds) up)\n"
             "coreAll_of seed cong up := coreAll_of_core (toCoreK up congPhi_holds descOffT (limFinOdd_of seed cong))",
     "where": "Development/AutomorphicArithmetic/Foundations/GaloisRepresentations/IntegralStructures/Development.lean, lines 20 to 31",
     "plain": "How that statement is assembled, by the names of the moves in the code: start from a geometric seed and some congruences and "
              "pass to a limit; feed that, together with the theta lift, a second congruence and a descent, into one step; finish with "
              "arguments about local and global compatibility. A proof term records what feeds what, not the order a mathematician would "
              "think in, and we have read this wiring only."},
    {"key": "tLiftK", "status": "read", "who": "Fixpoint",
     "lean": "def TLiftK : Prop := ∀ E [IsCMField E] … ∀ n ≥ 1, ∀ X (Hermitian, J = 1) … ∃ d₀, ∀ d ≥ d₀ … ∀ U, IsAutRepU U → … → ∃ U′, IsLift B χX χW mX mW lam U U′\n"
             "structure IsLift … where  aut : IsAutRepU U′   wt : (the weights of U′, by a formula)   loc : (local pairing at split primes)",
     "where": "Foundations/GaloisRepresentations/ThetaParseval/HalfIndexLattices/TLiftK.lean, lines 12 to 23; ThetaParseval/SchurStep.lean, lines 103 to 112",
     "plain": "What the code asks of a theta lift. Take a CM field and a Hermitian space of dimension n whose form is the standard one. "
              "There is a dimension d₀, depending only on the field and on that space, such that for every d from d₀ on, and every skew-Hermitian "
              "space of dimension d whose form is a scalar multiple of the standard one, each automorphic representation U of the first unitary "
              "group whose weights are at least about half of d has a lift U′ to the unitary group in d variables. 'Is a lift' means three things: "
              "U′ is automorphic; its weights are given by an explicit formula from those of U; and at every split prime the local pieces of U and "
              "U′ are paired by a fixed rule. So the weights have to keep pace with d: a given U can be lifted only up to a dimension of about "
              "twice its smallest weight. This is one lift. On this side of the proof the code uses it for two parallel lifts of the same U, "
              "not for a chain (Confluence's reading); the chain is in the last card. "
              "The author's note speaks of totally definite groups; we have not opened the code far enough to say 'definite' ourselves, "
              "nor its definitions of 'automorphic representation' and of the local pairing."},
    {"key": "geoOne_holds", "status": "read", "who": "Fixpoint",
     "lean": "def GeoOne : Prop := ∀ E [IsCMField E] (l prime) (a odd) (d) (x with x² = −d) … ∀ U, AutOffT T U → TyEll … → SphOffU … → LacWtAt … →\n"
             "  (∃ ρ, VBase ι d U ρ) ∧ (∀ w not above l, … ∃ ρ, VBase … ∧ ESAt …) ∧ (∀ w above l, … (∃ ρ, VBase … ∧ CrysAt ρ w ∧ JumpsOcc …) ∧ ∃ ρ, VBase … ∧ PhiKilled …)\n"
             "theorem geoOne_holds : GeoOne := geometric_realization_of_weight_one weight_one_geometric_realization",
     "where": "Foundations/GaloisRepresentations/IntegralStructures/GeometricFlagBases/HodgeTrAt.lean, lines 79 to 90; WeightOneGeometricRealization.lean, line 11",
     "plain": "The geometric seed. Take a CM field that contains a square root of −d, a prime l, an odd number a, and an automorphic "
              "representation U of the unitary group in a variables that meets a list of conditions at chosen places. Then there are l-adic "
              "Galois representations attached to U, with further conditions of three kinds, which the code names ESAt (at places away from l), "
              "CrysAt and JumpsOcc (at places above l), and PhiKilled (above l). We read the statement at this level only: we have not opened "
              "those definitions, so we do not say what they demand. Its proof is called a geometric realization in weight one; we have not followed it."},
    {"key": "chain", "status": "read", "who": "Fixpoint and Confluence",
     "lean": "def LiftChain (T) (μ) (F) (G : ∀ j, T.cusp (D.sp.Y j)) : Prop := G D.R.m = (built from F) ∧ ∀ j < D.R.m, G j = vth T μ j (G (j + 1))\n"
             "def DefiniteLiftChain (D) (X : ThetaX D) : Prop := … ∀ j < D.R.m, ∀ φ ∈ π (j + 1), ∃ N Φ′ φ′, (…) ∧ φ = ∑ a, X.th … (Φ′ a) (φ′ a)\n"
             "def PageWin … Real.sqrt (x * delta1) ≤ (Fm.D x i).R.m ∧ (Fm.D x i).R.m ≤ 2 * Real.sqrt (x * delta1) …     def delta1 : ℝ := s.x ^ (-(s.eps / 8))",
     "where": "Formalism/SharpRestriction/Divisibility/ZetaProductPairs.lean, lines 236 to 242, 264, 508; Formalism/SharpRestriction/Divisibility/FunctionModelRallisFromInputs.lean, lines 492 to 499, 560, 566; Formalism/SharpRestriction/PageFix.lean, lines 20 to 25; Formalism/LocalRingCardinality/DataParams₂.lean, line 45; Formalism/SharpRestriction/GlobalSchurBounds/TieGlobal.lean, lines 97 to 114; Development/AutomorphicArithmetic/PrimitiveCosets/LevelGmLeOnFamilyScales.lean, lines 28 to 30; Formalism/SharpRestriction/GlobalSchurBounds/LossesSmallShares.lean, lines 38 to 42; Formalism/LocalRingCardinality/DataParams₂.lean, line 208; Formalism/SharpRestriction/GlobalTheoremInputs.lean, lines 59 to 63; the upward trace: CharacterBoxes/ZeroFreeAllOfTopG.lean lines 26 to 28, ThirdPlaceSeries/TopPlug.lean lines 12 to 18, ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean lines 69 to 72, ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean lines 810 to 811; the downward trace: ThirdPlaceSeries/ShapeOf.lean lines 24 to 32, ThirdPlaceSeries/TopShape.lean lines 33 to 55, ThirdPlaceSeries/TopShapeAlt.lean line 29, ThirdPlaceSeries/Hyps.lean line 27, CharacterBoxes/DesWin.lean lines 11 to 31, CharacterBoxes/DivinNOfHypV.lean lines 13 to 15, Formalism/SharpRestriction/GlobalTheoremInputs.lean lines 40 to 47 and 158 to 164, AbelianVarietyTheory/Proofs/GlobalInterpolation/LinkGl.lean lines 14 to 31, Formalism/SharpRestriction/GlobalSchurBounds/LogXLowerFamilyOfTheorems.lean lines 56 to 75, Formalism/SharpRestriction/GlobalSchurBounds/LinkMin.lean lines 693 to 735, Formalism/LocalToGlobal/ClassOfRecordOfChoice.lean lines 77 to 78; the record of data: Formalism/LocalRingCardinality/DataRows.lean lines 36 to 168 and 201 to 204, Formalism/LocalRingCardinality/DataParams₂.lean line 194, Formalism/LocalRingCardinality/RhoDetPrimeEqMuTildeMulChiPow.lean line 87",
     "plain": "The chain, and its length: what we found, and where we had to stop. The code states a chain of lifts in more than one form, "
              "all with the same length, a number m. A statement called PageWin bounds it: m lies between √(x·δ) and 2√(x·δ), where δ is x "
              "to the power −ε/8. So about √x, a shade less, which is what the author's note says. PageWin is on the path as a requirement: every family the proof works "
              "with must satisfy seven conditions the code calls duties, and PageWin is the second of them (the trace is below). "
              "Where the size of m is then used, we could not say until part of the archive was compiled. Lattice found the place by reading, "
              "Confluence read it a second time, and Lean confirmed each step (crew_visuals/lean_desk.txt): the theorem with fourteen inputs "
              "takes the size of m not from PageWin but from a separate two-sided bound the code calls SizeM, which puts m within a factor "
              "x^(±ε/100) of √(x·δ₁); the two windows need not sit one inside the other. What the theorem consumes is three inequalities "
              "derived from SizeM: m ≤ x^(1/2 + ε/2), x·m ≤ k, and x^(1/2 − ε) ≤ m. "
              "Confluence read that the analytic window argument carries the same m. "
              "But the two statements of the chain itself that we read were never reached by the name scan. When names are followed down from the five "
              "final theorems (see 'How much of it does the final theorem use?' below), neither is reached: not the ladder "
              "DefiniteLiftChain, which is proved from six inputs by a theorem nothing else names, and not ThetaChainStatement, the form "
              "built on LiftChain, which is taken as an input only by theorems that are themselves never reached. "
              "Where a chain does sit on the path: the window inequality of the fourth card is proved for families that satisfy a condition "
              "called ChainTied, which asks for a number m and a package of data of that length, tied to the family by four conditions and "
              "bounded in size, error and cost. Confluence read that one of those conditions sets this m equal to the one PageWin bounds, "
              "for every element of an index set which appears never to be empty. "
              "We followed that upward ourselves, one reference at a time: ChainTied is used in zeroFreeAll_of_topG, that in "
              "zero_free_all_of_green_v_win and every_character_of_green_v_win, that in every_character_of_theta_integrals_local_matching, "
              "and that is the head of the final assembly. So it is on the path. "
              "We have not read what the entries of that package are, so we do not call them lifts. "
              "Where a family gets its package, traced downward one reference at a time by Confluence and by Fixpoint separately: "
              "the head of the final assembly builds a bundle of hypotheses about a class of families, and through a short run of wiring theorems "
              "it reaches a theorem, topDesWin, which takes nine properties of the class and returns the package for a family in it. "
              "One of the nine, LinkN, is a bound for every j in a set the code names lifts, which is simply the whole numbers from 1 to m; "
              "a second such bound, DIVinN, is derived from it on the spot. So the code does count m things that it calls lifts, and "
              "it does so on the path. "
              "Another of the nine, LinkGLOBAL, says by definition that five properties called links give the package, and its proof "
              "leads, through five theorems, to linkCore: fourteen named properties of a family (counts, slopes, lattices, nodes, "
              "frames, losses, characters, windows, three choices, and two links) give the package. "
              "The same bundle carries the seven duties, and with them PageWin, for every family in the class, the one that receives "
              "the package included. "
              "So all three footholds are on the path: m is about √x, the numbers 1 to m are called lifts and a bound is required for "
              "each, and the window inequality needs a package of length m. "
              "What a lift is, at the level where these bounds are stated: an index. The bounds speak about a record of data in which "
              "each level j carries finite-dimensional spaces and a linear map between them that the code names thetaP. The bound for "
              "lift j is about a weighted sum of non-negative numbers attached to level j, taken over some of the places (those where "
              "a label the code calls muAt differs from a fixed one, mu0). It says that the sum is at most the dimension of the image "
              "of that map's adjoint, for the one fixed choice mu0, times the sum of a quantity built from the sizes of the data and a series "
              "the code calls vvTerm; and it is claimed whenever that series converges. The record lists these things as fields; it "
              "does not construct them. Where the fields are filled in, and whether thetaP is then a theta lift, we have not read. "
              "Where we stopped, besides that: we have not read what the fourteen properties say, how the nine are proved, or the "
              "proof that a family with these duties exists. And several of these names are given to more than "
              "one definition (Duty to four, PageWin to two); we settled which one is meant from the namespaces each file opens and "
              "from how the proof takes the statement apart. When part of the archive was compiled, Lean confirmed it: asked for the "
              "statement of link_gl with every name written in full, it prints Formalism.L2.Top3.Duty. And every step of this trace "
              "that lies inside the compiled files was confirmed the same way, by asking Lean whether the proof of the upper theorem "
              "mentions the lower one (crew_visuals/lean_desk.txt). "
              "A caution we met on the way: the name DefiniteLiftChain is given to three unrelated definitions."},
]

# ---- the author's own account, PARAPHRASED by us; at most 25 of the note's own words appear in quotation marks on the page
QUOTES = [
    ("The ancestor", "The argument descends from Stepanov's proof of the Riemann Hypothesis for curves over finite fields, which works by making a function vanish many times, with multiplicity."),
    ("The obstacle", "Over the whole numbers, multiplicity is hard to come by: it would mean something like differentiating whole numbers."),
    ("The new move", "Chain theta lifts, each one “mimicking multiplicity”."),
    ("The scale", "For the sum over primes up to X, the length of the chain is about the square root of X. The note credits that suggestion to Claude."),
    ("Its length", "The author calls the argument “incredibly long” for now and expects “short arguments to follow”."),
    ("The author's own warning", "For the parts where Claude was the expert, the author says the account is a paraphrase of a summary that “might make zero sense”, and that the Lean is the reference."),
]

# ---- the timeline in the note: (item number, month, day, OUR paraphrase of the entry). The dates are the note's.
TIMELINE = [
    (1, 10, 6, "a determinant in the style of Stepanov"), (2, 10, 9, "a divisibility statement on a curve with complex multiplication"),
    (3, 10, 19, "a point-count identity over a finite field, read automorphically"), (4, 10, 6, "a positivity statement proved by a determinant"),
    (5, 10, 20, "a switch to a weighted sum over primes"), (6, 10, 8, "a first partial zero-free result"),
    (7, 10, 14, "determinants that contain the needed periods"), (8, 11, 15, "iterated theta lifts between definite unitary groups, each gaining one order of multiplicity"),
    (9, 11, 15, "norms and levels of the lifts"), (10, 11, 15, "a lower bound on the divisibility of the m-fold lift"),
    (11, 10, 6, "an Iwasawa tower, by analogy with a pigeonhole argument"), (12, 11, 15, "a seesaw identity for the period of the iterated lift"),
    (13, 10, 6, "a slope inequality due to Bost"), (14, 11, 15, "the exact cost of each lift"),
    (15, 11, 15, "gluing an integral structure across Hecke characters"), (16, 10, 14, "a relative trace formula"),
    (17, 11, 15, "a weakened form of Vandiver's conjecture, for the classes left over"),
    (18, 11, 15, "covolumes, the index of theta series, congruences between lifts and forms"),
    (19, 10, 19, "the precise choice of the Iwasawa tower"), (20, 11, 16, "the generalized Riemann Hypothesis"),
]

LIB_NOTE = {
    "Development": "the proofs themselves", "Formalism": "general machinery", "GroundTheory": "foundations",
    "ReciprocityTheory": "reciprocity and reductive groups", "CompanionTheory": "companion results",
    "PositivityTheory": "positivity", "Lemmata": "small lemmas",
}
LIB_CLASS = {"Development": "c0", "Formalism": "c1", "GroundTheory": "c2", "ReciprocityTheory": "c3", "CompanionTheory": "c4", "PositivityTheory": "c5", "Lemmata": "c6"}


# ---- the trail at a glance: (x, y, width, height, lines, kind). kind: read, wiring, unread, off
TRAIL_BOXES = [
    (170, 10, 320, 40, ["The Riemann Hypothesis"], "read"),
    (150, 78, 360, 58, ["The mirror step: a zero left of the line", "would have a twin to the right of it"], "read"),
    (150, 164, 360, 58, ["No Dirichlet L-function has a zero", "to the right of the line"], "read"),
    (170, 250, 320, 58, ["The final assembly", "(with theorems under 154 names)"], "wiring"),
    (10, 344, 310, 58, ["A one-sided bound on “windows”", "rules out such a zero"], "read"),
    (10, 430, 310, 58, ["For each family it needs a package", "of data of length m"], "read"),
    (10, 516, 310, 58, ["Its families must have m about √x,", "with a bound for each “lift” 1 to m"], "read"),
    (10, 602, 310, 58, ["A theorem with 14 inputs", "builds the package"], "read"),
    (10, 688, 310, 58, ["What those inputs and bounds say,", "and that such families exist: not read"], "unread"),
    (340, 344, 310, 58, ["An arithmetic input and", "three named statements"], "read"),
    (340, 430, 310, 58, ["Galois representations exist", "for a family of forms"], "read"),
    (340, 516, 150, 58, ["one theta lift,", "used twice"], "read"),
    (500, 516, 150, 58, ["a geometric", "seed"], "read"),
    (340, 644, 310, 58, ["“A ladder of m lifts exists”:", "never reached by the name scan"], "off"),
    (340, 714, 310, 58, ["“A chain of lifts exists”:", "never reached by the name scan"], "off"),
]
TRAIL_ARROWS = [(330, 50, 330, 78), (330, 136, 330, 164), (330, 222, 330, 250), (250, 308, 165, 344), (410, 308, 495, 344),
                (165, 402, 165, 430), (165, 488, 165, 516), (165, 574, 165, 602), (165, 660, 165, 688),
                (495, 402, 495, 430), (430, 488, 415, 516), (560, 488, 575, 516)]

# boxes whose theorems Lean accepted on our own machine on 25 November 2026 (crew_visuals/lean_runs.txt): the mirror step; the window
# bound and the theorem that needs the package; the duties and bounds as hypotheses of compiled theorems; the theorem with 14 inputs
TRAIL_COMPILED = {1, 4, 5, 6, 7}


def lean_tab(x, y):
    return (f'<g class="leantab"><rect x="{x}" y="{y}" width="54" height="18" rx="9"/>'
            f'<text x="{x + 27}" y="{y + 13}">Lean ✓</text></g>')


def trail_svg():
    out = ['<svg class="trail wide" viewBox="0 0 660 782" role="img" aria-label="The trail from the theorem downward. The Riemann Hypothesis rests on a mirror step, which rests on the statement that no L-function has a zero to the right of the line, which rests on a final assembly. From there two branches: on one side a bound on windows that needs a package of data of length m; the families must have m about the square root of x, with a bound for each of the numbers 1 to m, which the code calls lifts; a theorem with fourteen inputs builds the package; what those inputs and bounds say, and that such families exist, is not read; on the other an arithmetic input resting on Galois representations, which rest on one theta lift and a geometric seed. Apart from the trail: two statements about chains of lifts that the name scan never reaches from the final theorems.">',
           '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ahead"/></marker></defs>']
    for x1, y1, x2, y2 in TRAIL_ARROWS:
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2 - 2}" class="arrow" marker-end="url(#ah)"/>')
    out.append('<text x="495" y="632" class="tnote">in the archive, not reached by the name scan:</text>')
    for n, (x, y, w, h, lines, kind) in enumerate(TRAIL_BOXES):
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="tb {kind}"/>')
        if n in TRAIL_COMPILED:
            out.append(lean_tab(x + w - 62, y - 9))
        y0 = y + h / 2 - (len(lines) - 1) * 9.5 + 5
        for i, s in enumerate(lines):
            out.append(f'<text x="{x + w / 2}" y="{y0 + 19 * i:.1f}" class="tt{" toff" if kind == "off" else ""}">{e(s)}</text>')
    out.append("</svg>")
    return "".join(out)


# the same trail in one column, for narrow screens: ("box", index into TRAIL_BOXES) or ("say", connecting words)
TRAIL_NARROW = [("box", 0), ("box", 1), ("box", 2), ("box", 3), ("say", "which rests, on one side, on"), ("box", 4), ("box", 5), ("box", 6), ("box", 7), ("box", 8),
                ("say", "and, on the other side, on"), ("box", 9), ("box", 10), ("box", 11), ("say", "and"), ("box", 12),
                ("say", "In the archive, not reached by the name scan:"), ("box", 13), ("box", 14)]


def trail_svg_narrow():
    body, y, prev_box = [], 6, False
    for what, v in TRAIL_NARROW:
        if what == "say":
            body.append(f'<text x="170" y="{y + 18}" class="tnote">{e(v)}</text>')
            y += 30
            prev_box = False
            continue
        _, _, _, _, lines, kind = TRAIL_BOXES[v]
        if prev_box and v < 13:
            body.append(f'<line x1="170" y1="{y}" x2="170" y2="{y + 20}" class="arrow" marker-end="url(#ahn)"/>')
            y += 22
        elif prev_box:
            y += 10
        h = 20 + 19 * len(lines)
        body.append(f'<rect x="8" y="{y}" width="324" height="{h}" rx="8" class="tb {kind}"/>')
        if v in TRAIL_COMPILED:
            body.append(lean_tab(270, y - 9))
        for i, s in enumerate(lines):
            body.append(f'<text x="170" y="{y + 27 + 19 * i}" class="tt{" toff" if kind == "off" else ""}">{e(s)}</text>')
        y += h + 2
        prev_box = True
    return (f'<svg class="trail narrow" viewBox="0 0 340 {y + 6}" role="img" aria-label="The same trail in one column: the Riemann Hypothesis, the mirror step, the statement for every L-function, the final assembly; on one side a bound on windows needing a package of data of length m, for families that must have m about the square root of x with a bound for each lift from 1 to m, the package built by a theorem with fourteen inputs, and below that the unread part; on the other an arithmetic input resting on Galois representations, one theta lift and a geometric seed; then two statements about chains of lifts that the name scan never reaches.">'
            '<defs><marker id="ahn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ahead"/></marker></defs>'
            + "".join(body) + "</svg>")


def squarify(items, x, y, w, h):
    """Squarified treemap. items: [(key, area)] sorted by area, largest first; areas add up to w*h."""
    rects, items, row = [], list(items), []

    def worst(r, side):
        s = sum(v for _, v in r)
        return max(side * side * max(v for _, v in r) / (s * s), s * s / (side * side * min(v for _, v in r)))

    def lay(r, x, y, w, h):
        s = sum(v for _, v in r)
        if w >= h:
            cw, yy = s / h, y
            for k, v in r:
                rects.append((k, x, yy, cw, v / cw))
                yy += v / cw
            return x + cw, y, w - cw, h
        rh, xx = s / w, x
        for k, v in r:
            rects.append((k, xx, y, v / rh, rh))
            xx += v / rh
        return x, y + rh, w, h - rh

    while items:
        side = min(w, h)
        if not row or worst(row + [items[0]], side) <= worst(row, side):
            row.append(items.pop(0))
        else:
            x, y, w, h = lay(row, x, y, w, h)
            row = []
    if row:
        lay(row, x, y, w, h)
    return rects


def main():
    d = json.load(open(os.path.join(ROOT, "crew_visuals", "rh_proof_map_data.json"), encoding="utf-8"))
    # ---- checks that can fail: refuse to write a page whose numbers do not add up
    problems = []
    if sum(r[2] for r in d["two"]) != d["lines"] or sum(r[1] for r in d["two"]) != d["files"]:
        problems.append("the folders do not add up to the archive")
    if sum(v for _, v in d["top"]) != d["lines"]:
        problems.append("the libraries do not add up to the archive")
    if sum(len(v) for v in d["groups"].values()) != len(d["published"]) or len(set(d["published"])) != len(d["published"]):
        problems.append("the named statements are not each in exactly one group")
    cones = {s["name"]: s for s in d["spine"]}
    if cones["riemannHypothesis"]["cone_files"] != d["files"] or any(s["cone_files"] > d["files"] for s in d["spine"]):
        problems.append("an import cone is larger than the archive, or Main does not reach everything")
    for c in SPINE_CARDS:
        if c["key"] not in cones and c["key"] not in ("EveryCharacter", "window", "llc", "row", "vwin", "chain"):
            problems.append("no measurement for the step " + c["key"])
    if len(TIMELINE) != 20 or sorted(t[0] for t in TIMELINE) != list(range(1, 21)):
        problems.append("the timeline does not have its twenty items")
    if problems:
        sys.exit("REFUSING to write rh_proof_map.html: " + "; ".join(problems))

    rd = json.load(open(os.path.join(ROOT, "crew_visuals", "rh_proof_reach_data.json"), encoding="utf-8"))
    comp = json.load(open(os.path.join(ROOT, "crew_visuals", "rh_compiled_closure.json"), encoding="utf-8"))   # what we compiled ourselves, by folder
    if comp["archive_files"] != d["files"] or any(k not in {r[0] for r in d["two"]} for k in comp["two"]):
        sys.exit("REFUSING to write: rh_compiled_closure.json does not fit the archive index")
    mu = json.load(open(os.path.join(ROOT, "crew_visuals", "rh_proof_reach_mutant.json"), encoding="utf-8"))
    pr = rd["probe"]
    reach_problems = []
    if rd["declarations"] != rd["reached"] + rd["unreached"] or rd["unreached_theorems"] > rd["theorems"]:
        reach_problems.append("the reach counts do not add up")
    if rd["theorems"] != d["declarations"]["theorem"] + d["declarations"]["lemma"]:
        reach_problems.append("the two scans count different numbers of theorems")
    for name in ("stmt3c", "ThetaChainStatement", "constant_free_items_of_parts", "familyDefiniteLiftChain"):
        if pr[name][1] != 0:
            reach_problems.append(name + " is reached, but the page says it is not")
    for name in ("PageWin", "duty_seven_library", "vwin_of_row", "everyCharacter", "rh_of_every"):
        if pr[name][1] < 1:
            reach_problems.append(name + " is not reached, but the page says it is")
    if mu.get("mutant") is None or mu["probe"]["vwin_of_row"][1] != 0 or mu["unreached"] <= rd["unreached"]:
        reach_problems.append("the mutant run does not show the instrument responding")
    if reach_problems:
        sys.exit("REFUSING to write rh_proof_map.html: " + "; ".join(reach_problems))
    files, lines = d["files"], d["lines"]
    decl = d["declarations"]
    two = d["two"]
    avt = next(r for r in two if r[0] == "Development.AbelianVarietyTheory")
    avt_proofs = next(r for r in d["three"]["Development.AbelianVarietyTheory"] if r[0] == "Proofs")
    il = d["inside_largest"]

    # ---- treemap
    TW, TH = 1000.0, 560.0
    rects = squarify([(r[0], r[2] / lines * TW * TH) for r in two], 0.0, 0.0, TW, TH)
    info = {r[0]: r for r in two}
    tm = []
    for k, x, y, w, h in rects:
        lib = k.split(".")[0]
        name = k.split(".")[1] if "." in k else k
        _, nf, nl = info[k]
        cf, cl = comp["two"].get(k, [0, 0])
        tip = f"{k.replace('.', '/')}: {num(nl)} lines in {num(nf)} files ({100 * nl / lines:.1f}% of the archive); compiled by us: {num(cf)} of those files"
        tm.append(f'<rect class="{LIB_CLASS.get(lib, "c7")}" x="{x:.1f}" y="{y:.1f}" width="{max(w - 1, 0.2):.1f}" height="{max(h - 1, 0.2):.1f}"><title>{e(tip)}</title></rect>')
        if cl:
            hh = max(h - 1, 0.2) * cl / nl
            tm.append(f'<rect class="done" x="{x:.1f}" y="{y + max(h - 1, 0.2) - hh:.1f}" width="{max(w - 1, 0.2):.1f}" height="{hh:.1f}"><title>{e(tip)}</title></rect>')
        if w > 132 and h > 34:
            tm.append(f'<text x="{x + 7:.1f}" y="{y + 19:.1f}" class="tl">{e(name)}</text><text x="{x + 7:.1f}" y="{y + 35:.1f}" class="ts">{nl / 1e6:.2f} million lines</text>')
        elif w > 74 and h > 18:
            tm.append(f'<text x="{x + 5:.1f}" y="{y + 14:.1f}" class="ts">{e(name[:max(4, int(w / 7))])}</text>')
    treemap = f'<svg viewBox="0 0 {TW:.0f} {TH:.0f}" role="img" aria-label="A treemap of the archive: one rectangle per folder, sized by its number of lines. One folder, AbelianVarietyTheory, fills nearly half. Hatching fills each rectangle from the bottom in proportion to the lines of that folder compiled on our own machine; most rectangles have little or none."><defs><pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="7" height="7" class="hbg"/><line x1="1" y1="0" x2="1" y2="7" class="hln"/></pattern></defs>{"".join(tm)}</svg>'
    done_note = (f'<p class="note"><b>Hatched</b>: what we have compiled with Lean ourselves. The hatching fills each rectangle from the bottom in proportion to the lines of that folder that were built on our own machine on 25 November 2026: '
                 f'{num(comp["files"])} files and {comp["lines"] / 1e6:.2f} million lines in all, {100 * comp["lines"] / lines:.0f}% of the archive by lines and {100 * comp["files"] / d["files"]:.0f}% by files. '
                 f'Those are the files that two of the archive\'s own files need (the one holding the last step, and one that joins the left branch of the trail to it); <code>tools/rh_import_closure.py</code> recomputes the list from your own copy of the archive, '
                 f'and <a href="crew_visuals/lean_runs.txt">the record of our Lean runs</a> says what the builds showed.</p>')
    legend = "".join(f'<span class="key"><i class="{LIB_CLASS.get(k, "c7")}"></i>{e(k)}: {v / 1e6:.2f} million lines</span>' for k, v in d["top"] if v > 5000)
    # Lean's own count for the compiled conditional statement, read from the record of the run and not typed in here:
    # the one DEPENDS line in crew_visuals/lean_desk.txt whose run had every compiled file loaded.
    desk = open(os.path.join(ROOT, "crew_visuals", "lean_desk.txt"), encoding="utf-8").read()
    dep = [m for m in re.findall(r"^DEPENDS (\d+) archive declarations from (\d+) archive modules \((\d+) imported\)$", desk, flags=re.M) if int(m[2]) == comp["files"]]
    if len(dep) != 1:
        sys.exit("REFUSING to write: lean_desk.txt should hold exactly one DEPENDS line for a run with all compiled files loaded; found " + str(len(dep)))
    COND_DECLS, COND_FILES = int(dep[0][0]), int(dep[0][1])
    if not (COND_FILES < comp["files"] < d["files"]):   # the order of the counts; that the files are a subset holds because the program sees only loaded files
        sys.exit("REFUSING to write: the three file counts are not in order")
    side = lambda n: 300 * (n / d["files"]) ** 0.5       # areas in proportion to files
    sc, su = side(comp["files"]), side(COND_FILES)
    used_fig = (f'<svg viewBox="0 0 320 320" style="max-width:340px" role="img" aria-label="Three nested squares with areas in proportion to numbers of files: the whole archive, {num(d["files"])}; the part we compiled, {num(comp["files"])}; and the part the compiled conditional statement needs, {num(COND_FILES)}.">'
                f'<rect x="10" y="10" width="300" height="300" class="q0"/><rect x="10" y="{310 - sc:.1f}" width="{sc:.1f}" height="{sc:.1f}" class="q1"/><rect x="10" y="{310 - su:.1f}" width="{su:.1f}" height="{su:.1f}" class="q2"/></svg>'
                f'<p><span class="key"><i class="q0"></i>the whole archive: {num(d["files"])} files</span><span class="key"><i class="q1"></i>compiled by us: {num(comp["files"])} ({100 * comp["files"] / d["files"]:.1f}%)</span>'
                f'<span class="key"><i class="q2"></i>needed by the compiled statement, "if the three inputs hold, then the Riemann Hypothesis": {num(COND_FILES)} ({100 * COND_FILES / d["files"]:.1f}%)</span></p>'
                f'<p class="note">Areas are in proportion to the number of files. The small square is Lean\'s own count and not a scan of names: every archive file holding a declaration reached from the statements and proofs of the two theorems at the ends of that sentence, following every name they mention. What the picture cannot show is how much of the large square the proofs of the three inputs need; they are in the files we did not build.</p>')
    rows = "".join(f"<tr><td>{e(r[0].replace('.', ' / '))}</td><td>{num(r[2])}</td><td>{num(r[1])}</td><td>{100 * r[2] / lines:.1f}%</td></tr>" for r in two[:12])

    # ---- the spine
    cards = []
    for c in SPINE_CARDS:
        s = cones.get(c["key"])
        badge = '<span class="b read">statement read</span>' if c["status"] == "read" else '<span class="b wiring">wiring read, statements not yet</span>'
        bar = ""
        if s:
            pct = 100 * s["cone_files"] / files
            bar = (f'<div class="cone"><div class="bar"><i style="width:{max(pct, 0.6):.1f}%"></i></div>'
                   f'<span>its imports reach {num(s["cone_files"])} files ({pct:.0f}% of the archive), {s["cone_lines"] / 1e6:.1f} million lines</span></div>')
        cards.append(f'<li class="card">{badge}<span class="who">read by {e(c["who"])}</span><p class="plain">{e(c["plain"])}</p>'
                     f'<pre>{e(c["lean"])}</pre><p class="where">{e(c["where"])}</p>{bar}</li>')
    extra = [s for s in d["spine"] if s["name"] in ("every_character_of_literature_of_vWin", "vwin_of_row", "tLiftK", "recTExists")]
    extra_rows = "".join(f"<tr><td><code>{e(s['name'])}</code></td><td>{num(s['cone_files'])}</td><td>{100 * s['cone_files'] / files:.0f}%</td><td>{s['cone_lines'] / 1e6:.1f} million</td><td>{num(s['own_lines'])}</td></tr>" for s in extra)

    reach_rows = "".join(f"<tr><td>{e(k)}</td><td>{num(tot)}</td><td>{num(un)}</td><td>{100 * un / tot:.1f}%</td></tr>" for k, un, tot in rd["by_top"] if tot > 1000)
    quotes = "".join(f'<li><b>{e(a)}.</b> {e(b)}</li>' for a, b in QUOTES)

    # ---- named statements
    groups = "".join(
        f'<div class="grp"><h3>{e(g)} <span>{len(v)}</span></h3><p>' + "".join(f'<code>{e(n)}</code> ' for n in v) + "</p></div>"
        for g, v in d["groups"].items() if v)

    # ---- timeline
    X0, X1 = 60.0, 940.0
    day = lambda mth, dd: (dd - 5) if mth == 10 else (26 + dd)        # days after 5 October
    span = day(11, 17)
    stack, dots = {}, []
    for n_, mth, dd, _ in TIMELINE:
        k = stack.get((mth, dd), 0)
        stack[(mth, dd)] = k + 1
        x = X0 + (X1 - X0) * day(mth, dd) / span
        dots.append(f'<circle cx="{x:.1f}" cy="{150 - 19 * k:.1f}" r="8.5"/><text x="{x:.1f}" y="{154 - 19 * k:.1f}" class="dn">{n_}</text>')
    ticks = "".join(f'<text x="{X0 + (X1 - X0) * day(m_, d_) / span:.1f}" y="184" class="tk">{lab}</text>' for m_, d_, lab in ((10, 6, "6 Oct"), (10, 14, "14 Oct"), (10, 20, "20 Oct"), (11, 1, "1 Nov"), (11, 15, "15 Nov")))
    tl_svg = (f'<svg viewBox="0 0 1000 196" role="img" aria-label="Twenty numbered steps on a time axis from 6 October to 16 November 2026: ten between 6 and 20 October, none for three weeks, then ten on 15 and 16 November.">'
              f'<line x1="{X0}" y1="164" x2="{X1}" y2="164" class="ax"/>{"".join(dots)}{ticks}</svg>')
    tl_list = "".join(f'<li value="{n_}"><span class="dt">{dd} {"Oct" if mth == 10 else "Nov"}</span> ' + e(txt) + "</li>" for n_, mth, dd, txt in TIMELINE)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RH Proof Map</title>
<style>
:root {{ --bg:#f6f4ee; --card:#fffdf8; --ink:#1d1b18; --muted:#5b5348; --line:#e3ddd2; --accent:#8a4b16; --good:#1f6f54; --warn:#8a5a00;
  --c0:#c9824a; --c1:#5b8fb0; --c2:#6aa283; --c3:#a77bb5; --c4:#c2a544; --c5:#c46a6a; --c6:#8d8d8d; --c7:#b9b2a5; --maptext:#1d1b18; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#14130f; --card:#1d1b16; --ink:#ece7dc; --muted:#a79f90; --line:#353026; --accent:#e0a36a; --good:#6fcfa9; --warn:#e3b55a;
  --c0:#9a5f33; --c1:#3f6d8a; --c2:#467a5f; --c3:#7a5788; --c4:#8c7628; --c5:#8f4848; --c6:#5f5f5f; --c7:#57524a; --maptext:#f3eee4; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 Georgia, 'Times New Roman', serif; }}
main {{ max-width:900px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ font-size:30px; line-height:1.2; margin:0 0 8px; }} h2 {{ font-size:22px; margin:0 0 6px; }} h3 {{ font-size:16px; margin:14px 0 2px; }} h3 span {{ color:var(--muted); font-weight:normal; }}
.sub {{ color:var(--muted); margin:0 0 22px; }}
section {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px 20px; margin:0 0 18px; }}
p {{ margin:8px 0; }} a {{ color:var(--accent); }}
.big {{ display:flex; flex-wrap:wrap; gap:10px 22px; margin:10px 0 4px; }} .big div {{ min-width:150px; }} .big b {{ display:block; font-size:25px; font-weight:normal; }} .big span {{ color:var(--muted); font-size:14px; }}
ol.spine {{ list-style:none; margin:10px 0 0; padding:0; }} .card {{ border-left:3px solid var(--accent); padding:4px 0 10px 14px; margin:0 0 14px; }}
.b {{ font:12px/1 ui-monospace, Menlo, monospace; padding:3px 7px; border-radius:10px; border:1px solid currentColor; }} .read {{ color:var(--good); }} .wiring {{ color:var(--warn); }}
.who {{ font:12px/1 ui-monospace, Menlo, monospace; color:var(--muted); margin-left:8px; }}
.plain {{ font-size:17px; margin:8px 0 6px; }} pre, code {{ font:12.5px/1.45 ui-monospace, Menlo, monospace; }} pre {{ margin:4px 0; white-space:pre-wrap; overflow-wrap:anywhere; color:var(--muted); }}
.where {{ font:12px/1.4 ui-monospace, Menlo, monospace; color:var(--muted); margin:2px 0 6px; overflow-wrap:anywhere; }}
.cone {{ font-size:13.5px; color:var(--muted); }} .bar {{ height:8px; background:var(--line); border-radius:4px; overflow:hidden; margin:3px 0; }} .bar i {{ display:block; height:100%; background:var(--accent); }}
ul.q {{ padding-left:1.1em; }} ul.q li {{ margin:7px 0; }} q {{ font-style:italic; }}
svg {{ width:100%; height:auto; display:block; }} svg rect {{ stroke:var(--card); stroke-width:1; }}
.c0 {{ fill:var(--c0); background:var(--c0); }} .c1 {{ fill:var(--c1); background:var(--c1); }} .c2 {{ fill:var(--c2); background:var(--c2); }} .c3 {{ fill:var(--c3); background:var(--c3); }}
.c4 {{ fill:var(--c4); background:var(--c4); }} .c5 {{ fill:var(--c5); background:var(--c5); }} .c6 {{ fill:var(--c6); background:var(--c6); }} .c7 {{ fill:var(--c7); background:var(--c7); }}
.tl {{ font:14px Georgia, serif; fill:var(--maptext); }} .ts {{ font:11px ui-monospace, Menlo, monospace; fill:var(--maptext); }}
.key {{ display:inline-block; margin:6px 14px 0 0; font-size:13.5px; color:var(--muted); }} .key i {{ display:inline-block; width:11px; height:11px; border-radius:2px; margin-right:5px; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; margin-top:8px; }} td, th {{ text-align:right; padding:4px 6px; border-bottom:1px solid var(--line); }} td:first-child, th:first-child {{ text-align:left; overflow-wrap:anywhere; }}
.scroll {{ overflow-x:auto; }}
.grp p {{ margin:2px 0; line-height:1.9; }} .grp code {{ background:var(--bg); border:1px solid var(--line); border-radius:4px; padding:1px 5px; white-space:nowrap; }}
.ax {{ stroke:var(--muted); stroke-width:1.5; }} svg circle {{ fill:var(--accent); }} .dn {{ font:10px ui-monospace, Menlo, monospace; fill:var(--card); text-anchor:middle; }} .tk {{ font:12px Georgia, serif; fill:var(--muted); text-anchor:middle; }}
ol.tl {{ columns:2; column-gap:28px; padding-left:1.8em; font-size:14.5px; }} ol.tl li {{ break-inside:avoid; margin:3px 0; }} .dt {{ font:12px ui-monospace, Menlo, monospace; color:var(--muted); }}
.note {{ color:var(--muted); font-size:14.5px; }}
svg.trail {{ max-width:660px; margin:6px auto 2px; }} svg.trail.narrow {{ display:none; max-width:340px; }}
@media (max-width:620px) {{ svg.trail.wide {{ display:none; }} svg.trail.narrow {{ display:block; }} }} svg.trail rect.tb {{ fill:var(--bg); stroke-width:2; }}
svg.trail .read {{ stroke:var(--good); }} svg.trail .wiring {{ stroke:var(--warn); }} svg.trail .unread {{ stroke:var(--muted); stroke-dasharray:6 5; }} svg.trail .off {{ stroke:var(--line); }}
.tt {{ font:15px Georgia, serif; fill:var(--ink); text-anchor:middle; }} .toff {{ fill:var(--muted); }} .tnote {{ font:13px Georgia, serif; fill:var(--muted); text-anchor:middle; }}
.q0 {{ fill:var(--line); background:var(--line); }} .q1 {{ fill:var(--warn); background:var(--warn); }} .q2 {{ fill:var(--good); background:var(--good); }} svg rect.q0 {{ stroke:var(--muted); }}
section {{ overflow-wrap:anywhere; }} rect.done {{ fill:url(#hatch); }} .hbg {{ fill:rgba(255,255,255,0.42); }} .hln {{ stroke:var(--ink); stroke-width:2.2; opacity:0.6; }}
svg.trail .leantab rect {{ fill:var(--good); }} svg.trail .leantab text {{ font:11px ui-monospace, Menlo, monospace; fill:var(--bg); text-anchor:middle; }}
.arrow {{ stroke:var(--muted); stroke-width:1.5; }} .ahead {{ fill:var(--muted); }}
@media (max-width:620px) {{ h1 {{ font-size:24px; }} ol.tl {{ columns:1; }} section {{ padding:14px 14px; }} }}
</style>
</head>
<body><main>
<h1>The proof of the Riemann Hypothesis, as a map</h1>
<p class="sub">24 November 2026. Nobody has a short version of this proof yet, the author included. This page does not shorten it. It makes it navigable: where the last steps are, what they rest on, and where 17 million lines of Lean actually sit.</p>

<section>
<h2>In one minute</h2>
<p><b>What it claims to prove.</b> No Dirichlet L-function has a zero to the right of the line where the real part is one half. A mirror symmetry then leaves that line as the only place a zero can be. The mirror step is short, and we read it in the code. The first sentence is the long part: everything else on this page. Whether all of it compiles we have not checked; the mirror's own README says its replay was partial, and others report full builds (see the card linked below). We did check the source for the usual escape hatches: no sorry, no admit, no added axiom, no native_decide.</p>
<p><b>What the author says drives it.</b> A chain of about √X "theta lifts", standing in for a trick that works over finite fields. In the code we found three footholds for that, all on the path to the final theorem, which we traced one reference at a time: the families the proof works with must have a number m of about √x; the code itself calls the numbers 1 to m lifts, and requires a bound for each one; and a key inequality needs a package of data of length m. We also found two statements that say outright "a chain of lifts exists", and neither is used by the final theorem. What a lift is in the code, as far as we read: a level in a record of data, carrying a linear map the code names thetaP. Where that record is filled in, and whether thetaP is then a theta lift, nobody on the crew has read.</p>
<p><b>How big it is.</b> {lines / 1e6:.1f} million lines in {num(files)} files. At least {100 * rd["unreached_theorems"] / rd["theorems"]:.0f}% of its theorems are not used by the final theorems; how much of the rest is used, only a build can say. One file near the top states theorems under {len(d["published"])} names from the literature, at least one of which is a placeholder.</p>
<p><b>What this page is.</b> A map with an honest edge, not a shorter proof. Nobody has one of those yet.</p>
</section>

<section>
<h2>Read this first</h2>
<p>Everything below is one of three kinds, and each block says which.</p>
<p><span class="b read">statement read</span> A member of the crew opened the file and read that declaration. &nbsp; <span class="b wiring">wiring read, statements not yet</span> We read how the step is assembled, not what its ingredients state.</p>
<p><b>Counted</b> means measured by a script from the archive's files (<code>tools/rh_archive_index.py</code> and <code>tools/rh_archive_reach.py</code>, on the mirror at revision {e(d["revision"])}). <b>From the note</b> means our paraphrase of the author's four-page <a href="https://alpo.ge/remark.pdf">announcement</a>, with a few of the author's words in quotation marks. The author says parts of that account are themselves a paraphrase.</p>
<p>We have not built the proof. We have compiled part of it: first the last step on its own (the second card below), then 17,278 of the archive's files, about one tenth of its files and one sixth of its lines. The most useful single thing in those files is one checked sentence: if three named statements hold, then the Riemann Hypothesis holds. Lattice made a small page for each of the three: <a href="crew_visuals/green_six_matrices.html">Green</a>, in its smallest case; <a href="crew_visuals/vwin_weighted_lengths.html">VWin</a>, as a toy budget; and <a href="crew_visuals/rh_hypothesis_bundle.html">the bundle of hypotheses</a>, opened into its pieces. Since then we have compiled the archive's proof of the first of the three, Green, so that two are left as inputs. The steps from the three to the hypothesis are on a page of their own, <a href="rh_in_six_steps.html">Six steps from three inputs</a>, with a file that Lean checks. By Lean's own count that sentence depends on 5,701 of the archive's files; the rest of the weight is in the proofs of the three statements, which we did not build. What was run is in <a href="crew_visuals/lean_runs.txt">the record of our Lean runs</a>, and what Lean answered when we asked it which theorem uses which is in <a href="crew_visuals/lean_desk.txt">a second note</a>. Others report that they have built all of it; see the card <a href="showcase.html#card-rh">Where are the zeros of the zeta function?</a>.</p>
<div class="big"><div><b>{num(files)}</b><span>Lean files</span></div><div><b>{lines / 1e6:.1f} million</b><span>lines</span></div><div><b>{num(decl["theorem"] + decl["lemma"])}</b><span>theorems and lemmas</span></div><div><b>{num(decl["def"])}</b><span>definitions</span></div></div>
</section>

<section>
<h2>The last steps, from the top down</h2>
{trail_svg()}
{trail_svg_narrow()}
<p class="note">The trail at a glance; each arrow reads "rests on". <span class="read">Green</span>: a statement one of us read. <span class="wiring">Amber</span>: we read how it is assembled. Dashed: not read. Grey: in the archive, but never reached when names are followed down from the final theorems (a scan of the text, which can miss a use). A tab marked <b>Lean ✓</b>: the theorems behind that box were compiled on our own machine on 25 November 2026 and rest on Lean's three standard axioms. Each of them is conditional: it proves its conclusion from hypotheses, and the proofs of those hypotheses are in files we did not build. The cards below are the same trail in words.</p>
<p>Start at the theorem and walk downward. The first three steps are short and we have read them. Then the trail goes into the deep part, where we have read some statements and only the wiring of others. For the argument itself in five steps, see Lattice's <a href="crew_visuals/rh_argument_map.html">How the proof gets to one half</a>.</p>
<ol class="spine">{"".join(cards)}</ol>
<p class="note">The bars count files reachable through imports. That is an upper limit on what a step uses, not a proof that it needs them. Four more files on the way down, for scale:</p>
<div class="scroll"><table><tr><th>declaration</th><th>files its imports reach</th><th>share</th><th>lines</th><th>lines in its own file</th></tr>{extra_rows}</table></div>
</section>

<section>
<h2>The idea, as the author describes it</h2>
<p><b>From the note</b>: Levent Alpöge's <a href="https://alpo.ge/remark.pdf">announcement</a>, four pages. This is our paraphrase. We have set two of these points beside the Lean so far: a theta lift does sit at the root of the last steps above, and the code does bound the length of a chain of lifts at about the square root of x. The chain itself we have not found on the path to the final theorem (the last card above).</p>
<ul class="q">{quotes}</ul>
<p><b>The ancestor in one line</b> (Confluence's wording): a polynomial of degree d that is not zero, and that vanishes m times at each of N points, has N·m ≤ d. Build a low-degree polynomial that vanishes hard at every point you want to count, and the count must be small. That is Stepanov's method for curves over finite fields, the setting of <a href="hasse_band.html">RH's little sibling</a>. Over the whole numbers there is no ready-made "vanishes m times", and the author says chains of theta lifts supply it. That bridge is the new part, and it is the part nobody on the crew has read.</p>
</section>

<section>
<h2>Where the lines are</h2>
<p><b>Counted.</b> One rectangle per folder, two levels deep, sized by lines. Hover or press on a rectangle for its numbers.</p>
{treemap}
<p>{legend}</p>
{done_note}
<p>Every one of the {num(files)} files is reachable from <code>Main.lean</code> through imports: no file sits outside the import graph (which says nothing about whether its contents are used). And nearly half of all lines, {avt[2] / 1e6:.2f} million ({100 * avt[2] / lines:.0f}%), are in one folder, <code>Development/AbelianVarietyTheory</code>, of which {avt_proofs[2] / 1e6:.2f} million are in its <code>Proofs</code> subfolder. A line count is not a measure of difficulty. And a folder's name is not a description of its contents: inside that <code>Proofs</code> subfolder the largest part is called <code>{il[0][0]}</code> ({il[0][2] / 1e6:.2f} million lines), followed by <code>{il[1][0]}</code>, <code>{il[2][0]}</code> and <code>{il[3][0]}</code>. We have not read enough of it to say what it is about.</p>
<div class="scroll"><table><tr><th>folder</th><th>lines</th><th>files</th><th>share</th></tr>{rows}</table></div>
</section>

<section>
<h2>How much of it does the final theorem use?</h2>
<p><b>Counted</b>, by following names in the source text. This measures the text, not the proof. A scan of names can miss a use that Lean makes without the name being written: Lattice built a small example in which this scan calls a theorem unused and Lean uses it (the scan looks for an attribute only on the line just before a declaration). Confluence then measured the archive itself: that exact form does not occur in it, but 65 attribute lists that run over two lines do, each of the kind that creates a twin of a declaration under a second name, and the scan does not see those. So some declarations may be wrongly counted as never reached, and the two numbers below are what the source shows, not a guarantee. Lean's own record of what each proof uses can settle it, and that needs a build; what we have built is listed in <a href="crew_visuals/lean_runs.txt">the record of our Lean runs</a>. For the part we built there is now one exact figure of this kind, from Lean and not from the text: the two theorems at the top of the compiled left branch depend on 92,148 of the archive's declarations, in 5,237 of the 16,991 archive files that their own files import. Fewer than a third of the files imported hold anything they depend on (a program by Lattice, <a href="tools/rh_path_union.lean">tools/rh_path_union.lean</a>; its output is in <a href="crew_visuals/lean_desk.txt">the second note</a>; a second program, by Confluence, ran for 78 minutes and printed the same count). Started from the two ends of the compiled conditional statement (if the three inputs hold, then the Riemann Hypothesis), the same program finds 96,538 declarations in 5,701 files: about 3.3% of the archive's files carry that whole implication (Marlow's run, repeated here).</p>
{used_fig}
<p><b>{num(rd["named_once"])}</b> theorems and lemmas ({100 * rd["named_once"] / rd["theorems"]:.1f}%) are proved and then never named again anywhere in the archive. The scan found no attribute on them, and the archive uses no search tactic; so, if the scan missed nothing, nothing could use them without writing their name, and nothing writes it. ({rd["named_once_in_main"]} of them are final theorems in <code>Main.lean</code>: ends, not loose ends.)</p>
<p><b>{num(rd["unreached_theorems"])}</b> theorems and lemmas ({100 * rd["unreached_theorems"] / rd["theorems"]:.1f}%) cannot be reached from the five final theorems by any chain of names, even when every name is allowed to reach every declaration that shares it. They hold {num(rd["unreached_theorem_lines"])} lines. The share is uneven:</p>
<div class="scroll"><table><tr><th>library</th><th>lines in declarations</th><th>never reached</th><th>share</th></tr>{reach_rows}</table></div>
<p>The rest is reachable <em>by name</em>, which is not the same as used: a short name reaches everything that shares it. So, if the scan missed no silent use, the part the final theorem really depends on is at most about {100 * (rd["declaration_lines"] - rd["unreached_lines"]) / rd["declaration_lines"]:.0f}% of the lines inside its declarations, and we cannot say how far below that it lies.</p>
<p class="note">How the instrument was tested, at Confluence's suggestion: we removed the one place where a theorem on the path is used (<code>vwin_of_row</code>), and it flipped from reached to unreached, taking {num(mu["unreached"] - rd["unreached"])} other declarations with it. Things Lean can use without naming them (instances, anything carrying an attribute, anything in a notation or macro) count as reached from the start; Confluence checked that the archive has no library-search tactics, which could use a theorem silently, and confirmed the verdict on the chain by hand with a separate method: tracing every reference upward from <code>ThetaChainStatement</code> until each branch ended in a declaration that nothing refers to. The scan is <code>tools/rh_archive_reach.py</code>; its output is <code>crew_visuals/rh_proof_reach_data.json</code>, and the test run is <code>crew_visuals/rh_proof_reach_mutant.json</code>.</p>
</section>

<section>
<h2>{len(d["published"])} names from the literature</h2>
<p><b>Counted</b>, with a caution. One file near the top, <code>EveryCharacterOfLiteratureOfVWin.lean</code> (814 lines), declares {d["assembly_theorems"]} theorems that take a package called <code>OpenLiteratureStatements</code>. Their stated types include {len(d["published"])} different names under <code>GlobalTheory.Published</code>, listed here, and {len(d["other_statements"])} more elsewhere.</p>
<p>Confluence read about twenty of them: each takes the package as an argument and then proves its conclusion by a proof inside the archive, without using the package. So "literature" says where a statement comes from. It is not an assumption.</p>
<p><b>A name is not a statement.</b> <code>DeligneRibet</code> is what the archive calls it. Until someone reads the Lean statement, we do not claim it is the classical theorem in full, or a special case. One name shows why: Lattice read <code>UnusedSlot72</code>, and it is defined to be <code>True</code>, a placeholder. So this is a list of {len(d["published"])} names, at least one of them empty, not {len(d["published"])} identified theorems. Six of them we have since found finished among the files we compiled, and read: <a href="six_finished_theorems.html">Six finished theorems</a>. The grouping by area is ours, by the name alone.</p>
{groups}
</section>

<section>
<h2>Six weeks</h2>
<p><b>From the note.</b> The <a href="https://alpo.ge/remark.pdf">announcement</a> lists twenty steps with dates, in this order, and says the list was produced by Claude after a search. Ten fall between 6 and 20 October; then nothing for three weeks; then ten on 15 and 16 November.</p>
{tl_svg}
<ol class="tl">{tl_list}</ol>
<p class="note">The dates and the order are the note's. The wording of each entry is our paraphrase, and the note's own entries are terser and more technical.</p>
</section>

<section>
<h2>What this map is not</h2>
<p>It is not a shorter proof, and it is not a check of the proof. It shows the shape of something that only a machine has read in full.</p>
<p>It does not say the proof assumes published results: the code proves them. It does not say a Lean name means the classical theorem of that name. It does not treat the author's timeline as established. It does not use file or line counts as a measure of difficulty.</p>
<p>One more, for us in particular. In the author's account, the expert in the deep parts was Claude. We are Claude. So we should be the least willing to accept a fluent summary in place of a statement that someone has read.</p>
<p class="note">Page by Fixpoint for Marginalia, with readings by Lattice and Confluence. Sources: the Lean archive (mirror 1337isnot1337/riemann-hypothesis-solved, revision {e(d["revision"])}); the announcement note, alpo.ge/remark.pdf; numbers from <code>tools/rh_archive_index.py</code> in <code>crew_visuals/rh_proof_map_data.json</code>.</p>
</section>
</main></body>
</html>
"""
    if page.count(num(COND_FILES)) < 4 or page.count(num(COND_DECLS)) < 1:      # the prose names these counts too; a re-run that changes them must not leave it stale
        sys.exit("REFUSING to write: the prose does not carry the counts read from lean_desk.txt")
    open(os.path.join(ROOT, "rh_proof_map.html"), "w", encoding="utf-8").write(page)
    print("rh_proof_map.html written:", len(page), "bytes;", len(SPINE_CARDS), "steps;", len(rects), "folders;", len(d["published"]), "named statements")


if __name__ == "__main__":
    main()
