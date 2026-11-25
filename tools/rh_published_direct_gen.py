#!/usr/bin/env python3
"""rh_published_direct_gen.py ARCHIVE_SRC SCAN2.json OUT.lean TIER.txt NAME...

SCAN2.json is the output of tools/rh_published_scan2.py. TIER.txt receives the modules to build before running OUT.lean.

For each named statement whose line in the archive's table is a single theorem name, follow one-line repeats
('theorem a : T := b') to the theorem at the end of the chain and write a Lean file that states the published statement and
proves it by that theorem directly, importing only the file that holds it. Also writes the list of modules to build.
Refuses a statement whose line is anything but a single name, or whose chain it cannot follow by reading the files the scan placed."""
import json, os, re, sys
src, sj, outp, tierp = sys.argv[1:5]; want = sys.argv[5:]
d = json.load(open(sj, encoding="utf-8")); rows = {r["statement"]: r for r in d["statements"]}
WR = "Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean"
text = open(os.path.join(src, WR), encoding="utf-8").read()
DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|nonrec\s+)*(theorem|lemma)\s+((?:_root_\.)?[\w'.₀-₉]+)")
NS = re.compile(r"^namespace\s+(\S+)"); END = re.compile(r"^end\s+(\S+)")
single = re.compile(r"(?:_root_\.)?([A-Za-z_][\w'.₀-₉]*)$")
def decls(mod):
    """full name -> body, for the theorems of one module"""
    out, stack = {}, []
    lines = open(os.path.join(src, *mod.split(".")) + ".lean", encoding="utf-8").read().split("\n"); i = 0
    while i < len(lines):
        line = lines[i]
        g = NS.match(line)
        if g: stack.append(g.group(1)); i += 1; continue
        g = END.match(line)
        if g and stack and stack[-1] == g.group(1): stack.pop(); i += 1; continue
        g = DECL.match(line)
        if g:
            nm = g.group(2); full = nm[7:] if nm.startswith("_root_.") else ".".join(stack + [nm])
            j = i + 1
            while j < len(lines) and (lines[j][:1] in (" ", "\t") or lines[j] == "" and j + 1 < len(lines) and lines[j + 1][:1] in (" ", "\t")): j += 1
            dtx = "\n".join(lines[i:j]); out[full] = dtx.split(":=", 1)[1].strip() if ":=" in dtx else ""
            i = j; continue
        i += 1
    return out
def find(name, mods):
    hits = []
    for m in mods:
        for full in decls(m):
            if full == name or full.endswith("." + name): hits.append((full, m))
    exact = [h for h in hits if h[0] == name]
    hits = exact or hits
    return hits[0] if len({h[1] for h in hits}) == 1 else None
items, imports = [], set()
for s in want:
    r = rows[s]
    m = re.search(r"^theorem \S+ \(O : [^)]*\) : (?:_root_\.)?GlobalTheory\.Published\.%s :=\n((?:[ \t]+.*\n?)+)" % re.escape(s), text, flags=re.M)
    if not m: sys.exit("REFUSING: no line for " + s)
    b = single.fullmatch(m.group(1).strip())
    if not b: sys.exit("REFUSING: the line for %s is not a single name: %s" % (s, m.group(1).strip()[:80]))
    cur, mods = b.group(1), r["table_modules"]
    for _ in range(7):
        h = find(cur, mods)
        if h is None: h = find(cur, r["proof_modules"])
        if h is None: sys.exit("REFUSING: cannot place %s for %s" % (cur, s))
        full, mod = h; body = decls(mod)[full]
        nxt = single.fullmatch(body)
        if not nxt or find(nxt.group(1), r["proof_modules"]) is None and find(nxt.group(1), r["table_modules"]) is None: break
        cur = nxt.group(1)
    else: sys.exit("REFUSING: the chain of repeats for %s is longer than this tool follows" % s)
    if mod not in r["proof_modules"]: sys.exit("REFUSING: the chain for %s ends in %s, not in the file the scan found" % (s, mod))
    items.append((s, full)); imports.add(mod)
with open(outp, "w", encoding="utf-8") as f:
    for m in sorted(imports): f.write("import " + m + "\n")
    f.write("\nset_option linter.all false\n\n")
    for s, full in items: f.write(f"theorem direct_{s} : GlobalTheory.Published.{s} :=\n  {full}\n#print axioms direct_{s}\n\n")
open(tierp, "w", encoding="utf-8").write("\n".join(sorted(imports)) + "\n")
print("restated directly:", len(items), "; modules to build:", len(imports))
for s, full in items: print("  ", s, ":=", full)
