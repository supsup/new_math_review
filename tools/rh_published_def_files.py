#!/usr/bin/env python3
"""rh_published_def_files.py ARCHIVE_SRC BUILD_SRC SCAN2.json PROVED.txt OUT.json: for every statement of the table, the file that DEFINES
GlobalTheory.Published.<statement>, and whether the files of its proof import that file. Reads only.
Known limit: the import reader stops at the first line that is neither an import nor the start of a comment, so a file
with a block comment of several lines above its imports would be read as importing nothing. A second reader of the
same files, written apart by Confluence, found no such file among the 36,939 it opened and gave the same five rows."""
import os, re, sys, json
src, built, scan, provedp, outp = sys.argv[1:6]
d = json.load(open(scan, encoding="utf-8")); rows = d["statements"]; want = {r["statement"] for r in rows}
proved = {l.split("#")[0].strip() for l in open(provedp, encoding="utf-8") if l.strip() and not l.startswith("#")}
DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|nonrec\s+)*(def|abbrev|structure|class|inductive)\s+((?:_root_\.)?[\w'.₀-₉]+)")
NS = re.compile(r"^namespace\s+(\S+)"); END = re.compile(r"^end\s+(\S+)")
where = {}
for dp, dn, fn in os.walk(src):
    for f in fn:
        if not f.endswith(".lean"): continue
        p = os.path.join(dp, f)
        try: tx = open(p, encoding="utf-8").read()
        except Exception: continue
        if "Published" not in tx: continue
        stack = []
        for line in tx.split("\n"):
            g = NS.match(line)
            if g: stack.append(g.group(1)); continue
            g = END.match(line)
            if g and stack and stack[-1] == g.group(1): stack.pop(); continue
            g = DECL.match(line)
            if g:
                nm = g.group(2); full = nm[7:] if nm.startswith("_root_.") else ".".join(stack + [nm])
                if full.startswith("GlobalTheory.Published.") and full[len("GlobalTheory.Published."):] in want:
                    where.setdefault(full[len("GlobalTheory.Published."):], []).append((os.path.relpath(p, src)[:-5].replace(os.sep, "."), g.group(1), line.strip()[:160]))
IMPORT = re.compile(r"^\s*(?:public\s+|private\s+|meta\s+)*import\s+(?:all\s+)?(\S+)")
def path(root, m): return os.path.join(root, *m.split(".")) + ".lean"
imps = {}
def imports(m):
    if m not in imps:
        out = []
        if os.path.exists(path(src, m)):
            for line in open(path(src, m), encoding="utf-8"):
                g = IMPORT.match(line)
                if g: out.append(g.group(1))
                elif line.strip() and not line.lstrip().startswith(("--", "/-", "module", "set_option")):
                    if not line.startswith("import") and "import" not in line[:20]: break
            imps[m] = out
        else: imps[m] = None
    return imps[m]
def closure(roots):
    seen, st = set(), list(roots)
    while st:
        m = st.pop()
        if m in seen: continue
        i = imports(m)
        if i is None: continue
        seen.add(m); st.extend(i)
    return seen
have = set()
for dp, dn, fn in os.walk(built):
    for f in fn:
        if f.endswith(".lean"): have.add(os.path.relpath(os.path.join(dp, f), built)[:-5].replace(os.sep, "."))
out = []
for r in rows:
    s = r["statement"]; w = where.get(s, [])
    mods = sorted({x[0] for x in w}); pc = closure(r["proof_modules"]) if r["proof_modules"] else set()
    inside = [m for m in mods if m in pc]
    dc = closure(mods) if mods else set()
    out.append({"statement": s, "def_modules": mods, "kinds": sorted({x[1] for x in w}), "def_in_proof_closure": bool(inside), "proof_files": len(pc),
                "with_def_files": len(pc | dc), "def_new_vs_build": len(dc - have), "checked": s in proved, "line": w[0][2] if w else None})
json.dump(out, open(outp, "w"), indent=0)
nod = [o for o in out if not o["def_modules"]]; outside = [o for o in out if o["def_modules"] and not o["def_in_proof_closure"]]
print("statements:", len(out), "; definition found:", len(out) - len(nod), "; not found:", [o["statement"] for o in nod])
print("definition NOT among the files the proof imports:", len(outside), "; of those already checked:", sum(o["checked"] for o in outside))
for o in sorted(outside, key=lambda o: o["statement"]):
    print("  %-34s checked=%-5s proof %6d  with def %6d  def needs %5d new files | %s" % (o["statement"], o["checked"], o["proof_files"], o["with_def_files"], o["def_new_vs_build"], (o["line"] or "")[:110]))
