"""Count archive source files reachable from selected Lean entry files.

Pass the extracted archive's src directory, at revision 6193bb5 to
reproduce the card. Counts follow module imports, including each entry
file. They are separate from declaration counts measured in compiled
proof terms.
"""

import argparse
from functools import lru_cache
import json
from pathlib import Path
import re


ARCHIVE_ROOTS = {
    "BuildAid", "CompanionTheory", "Development", "Formalism", "GroundTheory",
    "Lemmata", "Main", "PositivityTheory", "ReciprocityTheory", "Statements", "Supplements",
}
IMPORT = re.compile(r"(?:(?:public|private|meta|all)\s+)*import\s+(\S+)")
COMMENT = re.compile(r"/-|-/|--")
ENTRIES = {
    "compiled": ("CritLine", "TopPlug"),
    "green": ("SumRangeEqRoots",),
    "budget": ("VwinOfRow",),
    "budget_assembly": ("TopMainZj",),
    "bundle": ("SiegelEisensteinSecondTermHypotheses",),
    "galois": ("RowSrc",),
    "literature": ("EveryCharacterOfLiteratureOfVWin",),
    "final": ("MainTheorems",),
}
SUPPLIERS = ("green", "budget", "bundle", "galois")


def header_imports(path):
    """Read the import header, ignoring line comments and nested block comments."""
    depth = 0
    with path.open(encoding="utf-8") as source:
        for line in source:
            start = 0
            chunks = []
            for token in COMMENT.finditer(line):
                if depth == 0:
                    chunks.append(line[start:token.start()])
                    if token[0] == "--":
                        start = len(line)
                        break
                if token[0] == "/-":
                    depth += 1
                elif token[0] == "-/":
                    depth -= 1
                start = token.end()
            if depth == 0:
                chunks.append(line[start:])
            statement = "".join(chunks).strip()
            if not statement or statement in ("prelude", "module"):
                continue
            match = IMPORT.fullmatch(statement)
            if match is None:
                return
            name = match[1]
            if name.split(".", 1)[0] in ARCHIVE_ROOTS:
                yield name


def census(source):
    @lru_cache(maxsize=None)
    def imports(module):
        path = source.joinpath(*module.split(".")).with_suffix(".lean")
        if not path.is_file():
            raise FileNotFoundError(path)
        return tuple(header_imports(path))

    def closure(starts):
        pending = list(starts)
        files = set()
        while pending:
            current = pending.pop()
            if current not in files:
                files.add(current)
                pending.extend(imports(current))
        return files

    entry_names = {name for names in ENTRIES.values() for name in names}
    candidates = {name: [] for name in entry_names}
    for path in source.rglob("*.lean"):
        if path.stem in candidates:
            candidates[path.stem].append(path)
    modules = {}
    for name, paths in candidates.items():
        if len(paths) != 1:
            raise ValueError(f"Expected exactly one source file for {name}, found {paths}")
        modules[name] = ".".join(paths[0].relative_to(source).with_suffix("").parts)

    assembly_imports = set(imports(modules["TopMainZj"]))
    tempered, = (name for name in assembly_imports
                 if name.rsplit(".", 1)[-1] == "TemperedProductOfSquareIntegrable")
    closures = {key: closure(modules[name] for name in names) for key, names in ENTRIES.items()}
    closures["tempered"] = closure((tempered,))
    compiled = closures["compiled"]
    results = {}
    for key, files in closures.items():
        outside = files - compiled
        results[key] = dict(total=len(files), outside=len(outside))
        if key in SUPPLIERS:
            others = set().union(*(closures[other] for other in SUPPLIERS if other != key))
            results[key]["exclusive"] = len(outside - others)
    # Identify extra source files brought in by the largest direct import
    # of the budget assembly and by none of its other direct imports.
    results["tempered"]["exclusive_within_budget_assembly"] = len(
        closures["tempered"] - compiled - closure(assembly_imports - {tempered})
    )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="extracted/lean/src from the archive")
    args = parser.parse_args()
    print(json.dumps(census(args.source.resolve()), indent=2))
