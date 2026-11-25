#!/usr/bin/env python3
"""rh_import_closure.py: which files of the archive does a given Lean file need?

Reads YOUR OWN checkout of the archive of the announced proof of the Riemann Hypothesis and follows the
'import' lines at the top of each file, starting from the modules you name, until nothing new turns up.
It prints how many archive files and lines that is, and writes the count for each folder (two levels
deep, the same folders as the picture on rh_proof_map.html) to a JSON file. It reads the archive and
changes nothing in it. It does not run Lean.

Usage:  python3 -I tools/rh_import_closure.py ARCHIVE_SRC OUT.json MODULE [MODULE ...]
        ARCHIVE_SRC is the folder that holds Main.lean (mirror 1337isnot1337/riemann-hypothesis-solved at 6193bb5, lean/src).

The two builds recorded in crew_visuals/lean_runs.txt were of
    Formalism.GammaFactorNonvanishing.CritLine
    Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopPlug
and crew_visuals/rh_compiled_closure.json is this script's output for those two names together.
Checks on itself: Main must need every file of the archive (175,187), and CritLine alone exactly 14,301.
"""
import json
import os
import re
import sys

IMPORT = re.compile(r"^\s*(?:public\s+|private\s+|meta\s+)*import\s+(?:all\s+)?(\S+)")


def path_of(src, mod):
    return os.path.join(src, *mod.split(".")) + ".lean"


def imports(src, mod, cache):
    if mod in cache:
        return cache[mod]
    out, in_comment = [], False
    with open(path_of(src, mod), encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if in_comment:
                in_comment = "-/" not in s
                continue
            if s.startswith("/-"):
                in_comment = "-/" not in s
                continue
            if not s or s.startswith("--") or s == "module" or s == "prelude":
                continue
            m = IMPORT.match(line)
            if not m:
                break                                   # imports come first; the first other line ends them
            if os.path.isfile(path_of(src, m.group(1))):
                out.append(m.group(1))                  # an import of Mathlib or Lean itself is not an archive file
    cache[mod] = out
    return out


def closure(src, roots, cache):
    seen, stack = set(), list(roots)
    while stack:
        m = stack.pop()
        if m in seen:
            continue
        seen.add(m)
        stack.extend(imports(src, m, cache))
    return seen


def count_lines(src, mod):
    with open(path_of(src, mod), "rb") as f:
        return f.read().count(b"\n")


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    src, out, roots = sys.argv[1], sys.argv[2], sys.argv[3:]
    for r in roots + ["Main", "Formalism.GammaFactorNonvanishing.CritLine"]:
        if not os.path.isfile(path_of(src, r)):
            sys.exit(f"REFUSING: no file for module {r} under {src}")
    cache = {}
    total = sum(1 for _, _, fs in os.walk(src) for f in fs if f.endswith(".lean"))
    whole = closure(src, ["Main"], cache)
    if len(whole) != total:
        sys.exit(f"REFUSING: Main reaches {len(whole)} files but the folder holds {total}; this script's reading of imports is off")
    crit = closure(src, ["Formalism.GammaFactorNonvanishing.CritLine"], cache)
    if total == 175187 and len(crit) != 14301:
        sys.exit(f"REFUSING: CritLine needs {len(crit)} files here, expected 14,301")
    got = closure(src, roots, cache)
    two, lines = {}, 0
    for m in sorted(got):
        p = m.split(".")
        key = ".".join(p[:2]) if len(p) >= 3 else p[0]
        n = count_lines(src, m)
        lines += n
        a = two.setdefault(key, [0, 0])
        a[0] += 1
        a[1] += n
    data = {"roots": roots, "files": len(got), "lines": lines, "archive_files": total, "two": dict(sorted(two.items()))}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"archive: {total} files; Main reaches all of them; CritLine alone needs {len(crit)}")
    print(f"the modules named need {len(got)} files, {lines} lines, in {len(two)} folders; written to {out}")


if __name__ == "__main__":
    main()
