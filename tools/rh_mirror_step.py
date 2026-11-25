"""Check the mirror step of the announced Lean proof of the Riemann Hypothesis on its own.

The step: if no Dirichlet L-function has a zero to the right of the line (the archive's statement EveryCharacter),
then for every primitive Dirichlet character every zero in the strip is on the line (critLine), and the Riemann Hypothesis
holds (rh_of_every, which by Lean's own record rests on rh_of_right and not on critLine: the two are siblings).
In the archive it lives in three places; the file that states it imports 14,301 other archive files, but the step
itself needs only Mathlib and one definition. This script copies the three pieces, byte for byte, out of YOUR OWN
checkout of the archive into a small Lake project, so that Lean can check the step in about a minute.
It contains two short statement lines from the archive, used to make the two mutants, and nothing else of the archive's text.

Usage:  python3 -I tools/rh_mirror_step.py ARCHIVE_SRC OUT_DIR
        ARCHIVE_SRC is the folder that holds Main.lean (mirror 1337isnot1337/riemann-hypothesis-solved at 6193bb5, lean/src).
Then:   cd OUT_DIR && lake update && lake build
Expect: 'Build completed successfully', and for each of the three theorems
        "depends on axioms: [propext, Classical.choice, Quot.sound]"   (Lean's three standard axioms; no sorryAx)
Controls that must FAIL:  lake env lean Mutant1.lean   and   lake env lean Mutant2.lean
        Mutant1 weakens the hypothesis (zeros excluded only to the right of 1); Mutant2 claims real part one third.

Checked by Fixpoint on 2026-11-25 with Lean 4.33.1 and Mathlib 0df444a360ea (the archive's own pins): accepted, three
standard axioms; both mutants rejected. This checks the STEP, not the proof of EveryCharacter, which is the rest of the archive.
"""
import hashlib
import os
import sys

SOURCES = [
    ("Formalism/GammaFactorNonvanishing/RhOfRight.lean", "7e2c0b519ee420192cad8fb281c2d2bfebae2ba553342fd579c81c2aa0bd3dc5"),
    ("Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean", "31f6e49936226cfc3d71b15685347bd2874db0aef384e5cf4fea7d09ba68dc71"),
    ("Formalism/GammaFactorNonvanishing/CritLine.lean", "5b1552ac13442150f6900f37b9b44eff1491fad1bebe2ec07a959eecb9bcfe02"),
]
TOOLCHAIN = "leanprover/lean4:v4.33.1\n"
LAKEFILE = '''name = "mirrorstep"
defaultTargets = ["MirrorStep"]
moreLeanArgs = ["--tstack=400000"]

[leanOptions]
autoImplicit = false
relaxedAutoImplicit = false
maxSynthPendingDepth = 3
pp.unicode.fun = true
maxHeartbeats = 4000000

[[require]]
name = "mathlib"
git = "https://github.com/leanprover-community/mathlib4"
rev = "0df444a360eaa60ab8c11dca51a86af692955474"

[[lean_lib]]
name = "MirrorStep"
'''


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = sys.argv[1], sys.argv[2]
    texts = []
    for rel, want in SOURCES:
        raw = open(os.path.join(src, rel), "rb").read()
        got = hashlib.sha256(raw).hexdigest()
        if got != want:
            sys.exit(f"REFUSED: {rel} has sha256 {got}, not the {want} this script was checked against")
        texts.append(raw.decode("utf-8").split("\n"))
    rr, ec, cl = texts
    h = [w[:16] for _, w in SOURCES]
    assert rr[0] == "import Mathlib" and ec[12].startswith("def UpperTheory.EveryCharacter : Prop :=")
    assert cl[3] == "open Complex DirichletCharacter" and cl[28].startswith("theorem Formalism.VW.rh_of_every")
    o = ["/-",
         "The mirror step of the announced Lean proof of the Riemann Hypothesis, checked on its own.",
         "Everything between the markers is copied byte for byte from the archive (mirror 1337isnot1337/riemann-hypothesis-solved at 6193bb5):",
         f"  Formalism/GammaFactorNonvanishing/RhOfRight.lean, whole file (sha256 {h[0]})",
         f"  Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean, lines 13 to 14, the definition only (file sha256 {h[1]})",
         f"  Formalism/GammaFactorNonvanishing/CritLine.lean, lines 4 to 32 (file sha256 {h[2]})",
         "CritLine.lean imports EveryCharacter.lean for that one definition; the definition is stated in Mathlib's terms alone, so it is copied here",
         "and the 14,301 archive files that the import would otherwise bring in are not needed. Nothing else is changed.",
         "-/",
         "-- BEGIN RhOfRight.lean"]
    o += rr[:-1] if rr[-1] == "" else rr
    o += ["-- END RhOfRight.lean", "", "-- BEGIN EveryCharacter.lean lines 13-14"] + ec[12:14]
    o += ["-- END EveryCharacter.lean lines 13-14", "", "-- BEGIN CritLine.lean lines 4-32"] + cl[3:32]
    o += ["-- END CritLine.lean lines 4-32", "",
          "#print axioms Formalism.VW.rh_of_right", "#print axioms Formalism.VW.critLine", "#print axioms Formalism.VW.rh_of_every",
          "#check @Formalism.VW.rh_of_every", "#check @Formalism.VW.critLine", ""]
    text = "\n".join(o)
    a = "∀ (N : ℕ) [NeZero N] (χ : DirichletCharacter ℂ N) (s : ℂ), 1 / 2 < s.re → (χ ≠ 1 ∨ s ≠ 1) → DirichletCharacter.LFunction χ s ≠ 0"
    b = "(h0 : 0 < s.re) (h1 : s.re < 1) (hz : LFunction χ s = 0) : s.re = 1 / 2 := by"
    assert text.count(a) == 1 and text.count(b) == 1
    os.makedirs(out, exist_ok=True)
    files = {"MirrorStep.lean": text, "lean-toolchain": TOOLCHAIN, "lakefile.toml": LAKEFILE,
             "Mutant1.lean": text.replace(a, a.replace("1 / 2 < s.re", "1 < s.re")),
             "Mutant2.lean": text.replace(b, b.replace("s.re = 1 / 2", "s.re = 1 / 3"))}
    for name, body in files.items():
        with open(os.path.join(out, name), "w", encoding="utf-8") as fh:
            fh.write(body)
    print(f"wrote {', '.join(files)} to {out}")
    print("next: cd there, then 'lake update' (fetches the pinned Mathlib with its prebuilt cache, about 7.5 GB) and 'lake build'")


if __name__ == "__main__":
    main()
