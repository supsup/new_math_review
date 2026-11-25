"""Measure the shape of the Lean archive of the announced proof of the Riemann Hypothesis. Read-only; nothing is built.

    python3 -I tools/rh_archive_index.py PATH/TO/extracted/lean/src crew_visuals/rh_proof_map_data.json

The archive is not part of this repository. We read the mirror 1337isnot1337/riemann-hypothesis-solved at revision
6193bb5; the numbers in crew_visuals/rh_proof_map_data.json are this script's output on that revision.

What it does, in one pass over every .lean file:
  - counts lines, and records the file's `import` lines and the names it declares
    (theorem, lemma, def, abbrev, structure, class, inductive, instance, axiom, opaque at the start of a line);
  - builds the import graph and, for a few named files on the way down from Main.lean, counts the files and lines
    that the file reaches through imports (its "import cone");
  - sums lines by folder, two and three levels deep;
  - reads the final assembly file and lists the stated types of the theorems that take the literature package.

What the numbers do NOT mean: a file being reachable by imports does not show that the final theorem logically needs
it, and a line count is not a measure of difficulty. A Lean name is a name; it is not the statement behind it. The
grouping of the named statements by area is ours and goes by the name alone.
"""
import collections
import json
import os
import re
import sys

DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private |protected |noncomputable |unsafe |partial )*"
                  r"(theorem|lemma|def|abbrev|structure|class|inductive|instance|axiom|opaque)\s+([^\s:({\[]+)")
ASSEMBLY = "Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.EveryCharacterOfLiteratureOfVWin"
SPINE = [
    ("riemannHypothesis", "Main"),
    ("rh_of_every", "Formalism.GammaFactorNonvanishing.CritLine"),
    ("everyCharacter", "Development.AutomorphicArithmetic.CharacterBoxes.MainConclusion"),
    ("every_character_of_literature_of_vWin", ASSEMBLY),
    ("vwin_of_row", "Development.AutomorphicArithmetic.AutomorphicVarieties.ModularityArgument.ThresholdArguments.DenseThresholdCases.VwinOfRow"),
    ("galoisLocalGlobalStrong_recParameter", "Development.AutomorphicArithmetic.Foundations.GaloisRepresentations.IntegralStructures.RowSrc"),
    ("tLiftK", "Development.AutomorphicArithmetic.Foundations.GaloisRepresentations.ThetaParseval.ThetaKernels.TLiftK"),
    ("recTExists", "Development.AutomorphicArithmetic.Foundations.LocalLanglands.LocalCentralUnits.RecTExists"),
    ("geoOne_holds", "Development.AutomorphicArithmetic.Foundations.GaloisRepresentations.IntegralStructures.GeometricFlagBases.WeightOneGeometricRealization"),
    ("galoisLocalGlobal_of_geometry_lift", "Development.AutomorphicArithmetic.Foundations.GaloisRepresentations.IntegralStructures.Development"),
]
# Grouping by area: OURS, by name only. First matching rule wins.
RULES = [
    ("Representations of real groups", r"DiscreteSeries|HolomorphicDiscrete|HarishChandra|CasselmanWallach|KFinite|DixmierMalliavin|WeylBranching|InducedSimple|SchurOrthogonality|FormalDegree|HoweDualityReal|RealMetaplectic"),
    ("Class field theory and classical number theory", r"ClassField|Artin|Chebotarev|Linnik|HilbertClass|Weber|RayC|RayClass|HasseNorm|Landherr|Chevalley|Brauer|HeckeL|HeckeTate|PartialZeta|DeligneRibet|SiegelKlingen|IdealInvariants|QuadraticClass"),
    ("Algebraic and Arakelov geometry", r"Kawamata|Nadel|Nef|Vol|L2Extension|Principalisation|ChowForm|HilbertSamuel|ArCalc|ArDegree|CycleHeights|GoodChernWeil|Serre|PointSeparation"),
    ("The Weil representation and theta lifts", r"WeilRep|WeilSiegel|WeilTheta|Theta|Metaplectic|StoneVonNeumann|Rallis|Kudla|GLHowe|Doubling|SiegelEisenstein|SiegelWeil|SiegelToroidal|HermitianHasse|HermitianLocal"),
    ("Representations of p-adic groups and local Langlands", r"Bernstein|Zelevinsky|Segment|DepthZero|MoyPrasad|Langlands|LocalConverse|GelfandKazhdan|Generic|Green|Unlinked|Standard|Tempered|IrreducibleAdmissible|UnitaryIrreducible|GeometricLemma|BorelCasselman|TotallyDisjoint|EssSquare|SquareIntegrable|GrothendieckRing|RadfordShuffle|Unramified"),
    ("Automorphic forms", r"Cusp|Automorphic|JacquetShalika|Flath|BaseChange|Clozel|GKGlobal|StrongApprox|SiegelSet|RegularAlgebraic|AlgebraicCharacter"),
    ("p-adic Hodge theory and Galois cohomology", r"BhattScholze|Fontaine|DeRham|Crystalline|Prismatic|GrothendieckMessing|BlochKato|PoitouTate"),
    ("Abelian varieties and complex multiplication", r"Abelian|SemiAbelian|Semistable|CMCurve|ComplexMultiplication|EllipticMain|DualAbelian|principalPolar|Toroidal|AbMul|GrothendieckDeformation|FormalAlgebraisation"),
]


def main():
    src, out = sys.argv[1], sys.argv[2]
    mods = {}
    for root, _, files in os.walk(src):
        for f in files:
            if not f.endswith(".lean"):
                continue
            p = os.path.join(root, f)
            mod = os.path.relpath(p, src)[:-5].replace(os.sep, ".")
            lines, imports, kinds = 0, [], []
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    lines += 1
                    if line.startswith("import "):
                        imports.append(line[7:].strip())
                        continue
                    m = DECL.match(line)
                    if m:
                        kinds.append(m.group(1))
            mods[mod] = (lines, imports, kinds)

    def cone(rootmod):
        seen, stack = set(), [rootmod]
        while stack:
            m = stack.pop()
            if m in seen or m not in mods:
                continue
            seen.add(m)
            stack.extend(mods[m][1])
        return seen

    total_files, total_lines = len(mods), sum(v[0] for v in mods.values())
    kinds = collections.Counter(k for v in mods.values() for k in v[2])
    top = collections.Counter()
    lvl2 = collections.defaultdict(lambda: [0, 0])
    lvl3 = collections.defaultdict(lambda: [0, 0])
    for m, v in mods.items():
        p = m.split(".")
        top[p[0]] += v[0]
        key2 = ".".join(p[:2]) if len(p) >= 3 else p[0]
        lvl2[key2][0] += 1
        lvl2[key2][1] += v[0]
        if len(p) >= 4:
            key3 = ".".join(p[:3])
            lvl3[key3][0] += 1
            lvl3[key3][1] += v[0]
    two = sorted(([k, a, b] for k, (a, b) in lvl2.items()), key=lambda r: (-r[2], r[0]))
    three = {k: sorted(([c.split(".")[2], a, b] for c, (a, b) in lvl3.items() if c.startswith(k + ".")), key=lambda r: (-r[2], r[0]))
             for k, _, b in two if b > 500000}
    spine = []
    for name, mod in SPINE:
        c = cone(mod)
        parts = collections.Counter()
        for x in c:
            q = x.split(".")
            parts[".".join(q[:2]) if len(q) >= 3 else q[0]] += mods[x][0]
        spine.append({"name": name, "file": mod.replace(".", "/") + ".lean", "own_lines": mods[mod][0],
                      "cone_files": len(c), "cone_lines": sum(mods[x][0] for x in c),
                      "cone_top": [[k, v] for k, v in sorted(parts.items(), key=lambda r: (-r[1], r[0]))[:3]]})

    text = open(os.path.join(src, ASSEMBLY.replace(".", os.sep) + ".lean"), encoding="utf-8").read()
    typed = re.findall(r"(?m)^theorem (\S+) \(O : _root_\.UpperTheory\.LiteratureTheorems\.OpenLiteratureStatements\)\s*(?:\([^)]*\)\s*)*: ([^\n]+?) :=\n", text)
    published = sorted({t.strip().replace("GlobalTheory.Published.", "") for _, t in typed if t.strip().startswith("GlobalTheory.Published.")})
    other = sorted({t.strip() for _, t in typed if not t.strip().startswith("GlobalTheory.Published.") and t.strip() != "UpperTheory.EveryCharacter"})
    groups = collections.OrderedDict((g, []) for g, _ in RULES)
    groups["Not grouped"] = []
    for name in published:
        for g, rx in RULES:
            if re.search(rx, name):
                groups[g].append(name)
                break
        else:
            groups["Not grouped"].append(name)

    inside = collections.defaultdict(lambda: [0, 0])          # what the largest folder holds, two levels further down
    for m, v in mods.items():
        p = m.split(".")
        if p[:3] == ["Development", "AbelianVarietyTheory", "Proofs"] and len(p) >= 5:
            inside[p[3]][0] += 1
            inside[p[3]][1] += v[0]
    inside_largest = sorted(([k, a_, b_] for k, (a_, b_) in inside.items()), key=lambda r: (-r[2], r[0]))

    reach = cone("Main")
    data = {
        "revision": "6193bb5", "files": total_files, "lines": total_lines,
        "reachable_files": len(reach), "reachable_lines": sum(mods[m][0] for m in reach),
        "declarations": dict(sorted(kinds.items())),
        "top": sorted(top.items(), key=lambda r: (-r[1], r[0])),
        "two": two, "three": three, "inside_largest": inside_largest, "spine": spine,
        "assembly_theorems": len(typed), "published": published, "groups": groups, "other_statements": other,
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=0, sort_keys=False)
        fh.write("\n")
    print(f"files {total_files}, lines {total_lines}, reachable from Main {len(reach)}; declarations {sum(kinds.values())}")
    print(f"folders two levels deep: {len(two)}; assembly theorems {len(typed)}, published names {len(published)}, other statements {len(other)}")
    for g, v in groups.items():
        print(f"  {g}: {len(v)}")


if __name__ == "__main__":
    main()
