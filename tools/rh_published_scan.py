#!/usr/bin/env python3
"""rh_published_scan.py ARCHIVE_SRC BUILT_SRC OUT.json

Which of the archive's 'published' statements could be checked cheaply?  Reads the archive's own table of proofs
(the wrappers in EveryCharacterOfLiteratureOfVWin.lean, each of which names the archive theorem that proves one statement),
finds the file that declares each named theorem, and counts how many archive files that file imports, directly or through
other files, and how many of those are not yet in BUILT_SRC (a build copy).  Reads only; runs no Lean.
The declaration index is by a simple reading of 'namespace', 'end' and declaration lines, so a name it cannot place is reported as such."""
import json, os, re, sys
src, built, outp = sys.argv[1], sys.argv[2], sys.argv[3]
WR = "Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean"
text = open(os.path.join(src, WR), encoding="utf-8").read()
wr = re.findall(r"^theorem (\S+) \(O : [^)]*\) : (?:_root_\.)?(GlobalTheory\.Published\.\w+) :=\n((?:[ \t]+.*\n?)+)", text, flags=re.M)
ident = re.compile(r"(?:_root_\.)?([A-Za-z_][\w']*(?:\.[A-Za-z_₀-₉][\w'₀-₉]*)+)")
wrappers = {}                                  # statement -> (wrapper name, set of constants named in the body)
by_wrapper = {}
for name, stmt, body in wr:
    consts = set(m for m in ident.findall(body) if not m.startswith(("And.", "Or.", "Iff.", "Exists.", "Nat.", "Classical.")))
    wrappers.setdefault(stmt, (name, consts)); by_wrapper[name] = stmt
IMPORT = re.compile(r"^\s*(?:public\s+|private\s+|meta\s+)*import\s+(?:all\s+)?(\S+)")
DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|nonrec\s+)*(?:theorem|lemma|def|abbrev|instance|structure|inductive)\s+((?:_root_\.)?[\w'.₀-₉]+)")
NS = re.compile(r"^namespace\s+(\S+)"); END = re.compile(r"^end\s+(\S+)")
wanted_last = set()
for stmt, (_, consts) in wrappers.items():
    for c in consts: wanted_last.add(c.rsplit(".", 1)[-1])
imports, decl_at = {}, {}                       # module -> [imports];  full name -> module
nfiles = 0
for dp, dn, fn in os.walk(src):
    for f in fn:
        if not f.endswith(".lean"): continue
        p = os.path.join(dp, f); mod = os.path.relpath(p, src)[:-5].replace(os.sep, ".")
        nfiles += 1
        try: lines = open(p, encoding="utf-8").read().split("\n")
        except Exception: continue
        imps, stack = [], []
        for line in lines:
            if line.startswith("import") or line.lstrip().startswith(("public import", "private import", "meta import")):
                g = IMPORT.match(line)
                if g: imps.append(g.group(1))
                continue
            c0 = line[:1]
            if c0 == "n":
                g = NS.match(line)
                if g: stack.append(g.group(1)); continue
            elif c0 == "e":
                g = END.match(line)
                if g and stack and stack[-1] == g.group(1): stack.pop(); continue
            g = DECL.match(line)
            if g:
                nm = g.group(1)
                if nm.rsplit(".", 1)[-1] in wanted_last:
                    full = nm[7:] if nm.startswith("_root_.") else ".".join(stack + [nm])
                    decl_at.setdefault(full, mod)
        imports[mod] = imps
def closure(mods):
    seen, st = set(), list(mods)
    while st:
        m = st.pop()
        if m in seen or m not in imports: continue
        seen.add(m); st.extend(imports[m])
    return seen
have = set()
for dp, dn, fn in os.walk(built):
    for f in fn:
        if f.endswith(".lean"): have.add(os.path.relpath(os.path.join(dp, f), built)[:-5].replace(os.sep, "."))
rows = []
def resolve(stmt, depth=0):
    """modules holding the theorems the wrapper for stmt names; wrappers of other statements are followed"""
    name, consts = wrappers[stmt]; mods, unknown = set(), []
    for c in consts:
        if c in by_wrapper and depth < 6:
            m2, u2 = resolve(by_wrapper[c], depth + 1); mods |= m2; unknown += u2
        elif c in decl_at: mods.add(decl_at[c])
        elif c.startswith("UpperTheory.LiteratureTheorems.") or c.startswith("GlobalTheory.Published."): continue
        else: unknown.append(c)
    return mods, unknown
for stmt in sorted(wrappers):
    mods, unknown = resolve(stmt)
    cl = closure(mods)
    rows.append({"statement": stmt.replace("GlobalTheory.Published.", ""), "wrapper": wrappers[stmt][0], "proof_names": sorted(wrappers[stmt][1]), "modules": sorted(mods), "unplaced": sorted(set(unknown)),
                 "files": len(cl), "new": len(cl - have)})
rows.sort(key=lambda r: (bool(r["unplaced"]) or not r["modules"], r["new"], r["files"]))
json.dump({"archive_files": nfiles, "built_files": len(have), "statements": rows}, open(outp, "w"), indent=1)
print("archive files:", nfiles, "; built copy:", len(have), "; statements with a wrapper:", len(rows), "; fully placed:", sum(1 for r in rows if r["modules"] and not r["unplaced"]))
for r in rows[:60]:
    print(f'{r["new"]:7d} new of {r["files"]:7d}  {r["statement"]:38s} {"UNPLACED " + ",".join(r["unplaced"])[:60] if r["unplaced"] or not r["modules"] else ""}')
