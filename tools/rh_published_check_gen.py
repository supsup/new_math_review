#!/usr/bin/env python3
"""rh_published_check_gen.py ARCHIVE_SRC BUILT_SRC SCAN.json OUT.lean

SCAN.json is the output of tools/rh_published_scan.py.

Writes a Lean file that restates, for each 'published' statement whose proof files are all in the build copy, the archive's own
wrapper (the line in EveryCharacterOfLiteratureOfVWin.lean that proves the statement from an archive theorem) as a local theorem,
and prints its axioms. A wrapper that leans on another wrapper is restated after it. Statements whose files are not built are
skipped and counted. Reads only."""
import json, os, re, sys
src, built, tj, outp = sys.argv[1:5]
WR = "Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean"
text = open(os.path.join(src, WR), encoding="utf-8").read()
wr = re.findall(r"^theorem (\S+) \(O : [^)]*\) : (?:_root_\.)?(GlobalTheory\.Published\.\w+) :=\n((?:[ \t]+.*\n?)+)", text, flags=re.M)
by_wrapper = {n: s for n, s, b in wr}
first = {}
for n, s, b in wr: first.setdefault(s, (n, b.strip()))
d = json.load(open(tj)); rows = {r["statement"]: r for r in d["statements"]}
IMPORT = re.compile(r"^\s*(?:public\s+|private\s+|meta\s+)*import\s+(?:all\s+)?(\S+)")
def path(root, m): return os.path.join(root, *m.split(".")) + ".lean"
cache = {}
def all_built(mod):
    if mod in cache: return cache[mod]
    seen, st, ok = set(), [mod], True
    while st:
        m = st.pop()
        if m in seen: continue
        seen.add(m)
        if not os.path.exists(path(src, m)): continue                 # outside the archive
        if not os.path.exists(path(built, m)): ok = False; break
        for line in open(path(src, m), encoding="utf-8"):
            g = IMPORT.match(line)
            if g: st.append(g.group(1))
            elif line.strip() and not line.lstrip().startswith(("--", "/-", "module", "set_option", "public", "private", "meta")): break
    cache[mod] = ok; return ok
ref = re.compile(r"\(?(?:_root_\.)?(UpperTheory\.LiteratureTheorems\.\w+_of_literature) O\)?")
done, order, skipped, imports = {}, [], [], set()
def emit(stmt, depth=0):
    if stmt in done: return done[stmt]
    short = stmt.replace("GlobalTheory.Published.", "")
    r = rows.get(short)
    if r is None or r["unplaced"] or not r["modules"] or depth > 8: done[stmt] = None; return None
    if not all(all_built(m) for m in r["modules"]): done[stmt] = None; return None
    name, body = first[stmt]
    ok = True
    def sub(m):
        nonlocal ok
        dep = by_wrapper.get(m.group(1))
        nm = emit(dep, depth + 1) if dep else None
        if nm is None: ok = False; return m.group(0)
        return nm
    body2 = ref.sub(sub, body)
    if not ok or re.search(r"\bO\b", body2): done[stmt] = None; return None
    nm = "pub_" + short
    done[stmt] = nm; imports.update(r["modules"]); order.append((nm, stmt, " ".join(body2.split())))
    return nm
for stmt in sorted(first):
    if emit(stmt) is None: skipped.append(stmt.replace("GlobalTheory.Published.", ""))
with open(outp, "w", encoding="utf-8") as f:
    for m in sorted(imports): f.write("import " + m + "\n")
    f.write("\nset_option linter.all false\nset_option maxHeartbeats 400000\n\n")
    for nm, stmt, body in order:
        f.write(f"theorem {nm} : {stmt} :=\n  {body}\n#print axioms {nm}\n\n")
print("restated:", len(order), "; skipped (files not built, or the wrapper uses the literature package):", len(skipped), "; imports:", len(imports))
print("restated names:", " ".join(n[4:] for n, _, _ in order))
