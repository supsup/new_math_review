#!/usr/bin/env python3
"""rh_published_scan2.py ARCHIVE_SRC OUT.json

A second, more careful reading of the archive's table of published results (EveryCharacterOfLiteratureOfVWin.lean).
For each line of the table whose type is a GlobalTheory.Published statement it records:
  table_files   the number of archive files imported by the file(s) declaring the theorem(s) the line names (what the first
                scan, tools/rh_published_scan.py, measured: what must be compiled to check the table's line as written);
  proof_files   the same after following one-line aliases: if a named theorem is declared as 'theorem a : T := b', with b a
                single name, the count is taken at b's file instead, and so on (at most 6 steps);
  package       True if the line, or a line of the table it calls, uses the table's argument O, the package of statements
                the archive assumes from the literature, for anything but passing it on (so the line is not a proof from
                archive theorems alone);
  same_as       another statement of which this one is by definition a copy (def A : Prop := B), if any.
Reads only; runs no Lean. Names are located by reading every file for them, then a simple reading of 'namespace' and 'end' lines; a name that cannot
be placed uniquely is left where the table put it and listed under 'unfollowed'.
Known limits: a one-line body counts as a repeat when it is a single dotted name, so a local hypothesis or a projection
would be misread as a theorem name, and binders on the repeating theorem are not checked; a repeat whose target is
written without its namespace is followed only if exactly one file declares a name ending that way. The table has 195
theorems; the pattern here matches the 194 that take the package alone and leaves out the file's final theorem."""
import json, os, re, subprocess, sys, tempfile
src, outp = sys.argv[1], sys.argv[2]
WR = "Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean"
text = open(os.path.join(src, WR), encoding="utf-8").read()
# every theorem of the table that takes the package O
chunks = re.split(r"^(?=theorem )", text, flags=re.M)[1:]
table = {}                                                    # name -> (type, body)
for ch in chunks:
    m = re.match(r"theorem (\S+) \(O : [^)]*\) :(.*?):=\n?(.*)", ch, flags=re.S)
    if not m: continue
    table[m.group(1)] = (" ".join(m.group(2).split()), m.group(3).strip())
short = lambda n: n.replace("_root_.", "")
tnames = set(table)
ident = re.compile(r"(?:_root_\.)?([A-Za-z_][\w']*(?:\.[A-Za-z_₀-₉][\w'₀-₉]*)+)")
call = re.compile(r"\(?(?:_root_\.)?([A-Za-z_][\w'.₀-₉]*) O\)?")
def uses_package(name, seen=()):
    """True if the body uses O other than by handing it to another table theorem that does not use it"""
    if name in seen: return True
    typ, body = table[name]
    deps = [short(m) for m in call.findall(body)]
    rest = call.sub(" ", body)
    if re.search(r"\bO\b", rest): return True
    for d in deps:
        if d not in table: return True
        if uses_package(d, seen + (name,)): return True
    return False
pub = {}                                                      # statement -> table theorem (the first for it)
for n, (typ, body) in table.items():
    m = re.fullmatch(r"(?:_root_\.)?GlobalTheory\.Published\.(\w+)", typ)
    if m: pub.setdefault(m.group(1), n)
SKIP = ("And.", "Or.", "Iff.", "Exists.", "Nat.", "Classical.")
def consts_of(name, depth=0):
    """archive theorems a table line names, following calls to other table lines"""
    typ, body = table[name]; out = set()
    for c in ident.findall(body):
        if c.startswith(SKIP): continue
        if c in table and depth < 8: out |= consts_of(c, depth + 1)
        elif c.startswith("UpperTheory.LiteratureTheorems.") or c.startswith("GlobalTheory.Published."):
            if c in table: continue
            if c.startswith("GlobalTheory.Published."): out.add(c)      # a theorem that lives in that namespace
        else: out.add(c)
    return out
# ---- locating declarations by grep, then reading the files that mention the names
IMPORT = re.compile(r"^\s*(?:public\s+|private\s+|meta\s+)*import\s+(?:all\s+)?(\S+)")
DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|nonrec\s+)*(theorem|lemma|def|abbrev)\s+((?:_root_\.)?[\w'.₀-₉]+)")
NS = re.compile(r"^namespace\s+(\S+)"); END = re.compile(r"^end\s+(\S+)")
index = {}                                                    # full name -> list of (module, body text)
indexed_last = set()
def modname(p): return os.path.relpath(p, src)[:-5].replace(os.sep, ".")
def index_names(lasts):
    lasts = set(lasts) - indexed_last
    if not lasts: return
    indexed_last.update(lasts)
    hits = []
    for dp, dn, fn in os.walk(src):
        for f in fn:
            if not f.endswith(".lean"): continue
            p = os.path.join(dp, f)
            try: tx = open(p, encoding="utf-8").read()
            except Exception: continue
            for nm in lasts:
                if nm in tx: hits.append(p); break
    r = type("R", (), {"stdout": "\n".join(hits)})()
    print("  walk done:", len(lasts), "names;", len(hits), "files mention one", flush=True)
    for p in r.stdout.split("\n"):
        if not p: continue
        lines = open(p, encoding="utf-8").read().split("\n"); stack = []; mod = modname(p)
        i = 0
        while i < len(lines):
            line = lines[i]
            g = NS.match(line)
            if g: stack.append(g.group(1)); i += 1; continue
            g = END.match(line)
            if g and stack and stack[-1] == g.group(1): stack.pop(); i += 1; continue
            g = DECL.match(line)
            if g and g.group(2).rsplit(".", 1)[-1] in lasts:
                nm = g.group(2); full = nm[7:] if nm.startswith("_root_.") else ".".join(stack + [nm])
                j = i + 1
                while j < len(lines) and (lines[j][:1] in (" ", "\t") or lines[j] == "" and j + 1 < len(lines) and lines[j + 1][:1] in (" ", "\t")): j += 1
                decl = "\n".join(lines[i:j])
                body = decl.split(":=", 1)[1].strip() if ":=" in decl else ""
                index.setdefault(full, []).append((mod, body, g.group(1)))
                i = j; continue
            i += 1
def place(c):
    """(module, body, kind) of the declaration named c, if exactly one module declares a name that is c or ends with .c"""
    hits = [(full, v) for full, vs in index.items() if full == c or full.endswith("." + c) for v in vs]
    exact = [(f, v) for f, v in hits if f == c]
    use = exact or hits
    mods = {v[0] for _, v in use}
    return use[0][1] if len(mods) == 1 else None
single = re.compile(r"(?:_root_\.)?([A-Za-z_][\w'.₀-₉]*)$")
rows_c = {s: sorted(consts_of(n)) for s, n in pub.items()}
frontier = {c.rsplit(".", 1)[-1] for cs in rows_c.values() for c in cs}
final = {}                                                    # const -> (table module or None, final module or None, hops)
for _ in range(7):
    index_names(frontier); frontier = set()
    for cs in rows_c.values():
        for c in cs:
            cur, hops, first = c, 0, None
            while True:
                pl = place(cur)
                if pl is None: break
                if first is None: first = pl[0]
                m = single.fullmatch(pl[1]) if pl[2] in ("theorem", "lemma") else None
                if not m or hops >= 6: break
                nxt = m.group(1)
                if nxt.rsplit(".", 1)[-1] not in indexed_last: frontier.add(nxt.rsplit(".", 1)[-1]); break
                if place(nxt) is None: break
                cur, hops = nxt, hops + 1
            pl = place(cur)
            final[c] = (first, pl[0] if pl else None, hops)
    if not frontier: break
imps = {}
def imports(m):
    if m in imps: return imps[m]
    out = []; p = os.path.join(src, *m.split(".")) + ".lean"
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            g = IMPORT.match(line)
            if g: out.append(g.group(1))
            elif line.strip() and not line.lstrip().startswith(("--", "/-", "module", "set_option", "public", "private", "meta")): break
    imps[m] = out; return out
def closure(mods):
    seen, st = set(), list(mods)
    while st:
        m = st.pop()
        if m in seen or not os.path.exists(os.path.join(src, *m.split(".")) + ".lean"): continue
        seen.add(m); st.extend(imports(m))
    return seen
# statements that are by definition another statement
index_names(set(pub))
same = {}
for s in pub:
    pl = [v for v in index.get("GlobalTheory.Published." + s, []) if v[2] in ("def", "abbrev")]
    if len(pl) == 1:
        m = single.fullmatch(pl[0][1])
        if m and m.group(1).rsplit(".", 1)[-1] in pub and m.group(1).rsplit(".", 1)[-1] != s: same[s] = m.group(1).rsplit(".", 1)[-1]
        elif pl[0][1] == "True": same[s] = "True"
rows = []
for s, n in sorted(pub.items()):
    cs = rows_c[s]
    tmods = sorted({final[c][0] for c in cs if final[c][0]}); pmods = sorted({final[c][1] for c in cs if final[c][1]})
    unf = sorted(c for c in cs if final[c][0] is None)
    rows.append({"statement": s, "line": n, "names": cs, "table_modules": tmods, "proof_modules": pmods, "unfollowed": unf,
                 "table_files": len(closure(tmods)), "proof_files": len(closure(pmods)), "hops": max([final[c][2] for c in cs] or [0]),
                 "package": uses_package(n), "same_as": same.get(s)})
others = sorted(n for n, (typ, _) in table.items() if not re.fullmatch(r"(?:_root_\.)?GlobalTheory\.Published\.\w+", typ))
json.dump({"revision": "6193bb5", "table_theorems": len(table), "published_lines": sum(1 for n, (t, _) in table.items() if re.fullmatch(r"(?:_root_\.)?GlobalTheory\.Published\.\w+", t)),
           "statements": rows, "other_lines": others}, open(outp, "w"), indent=1, ensure_ascii=False)
print("table theorems with the package argument:", len(table), "; statements of type GlobalTheory.Published.*:", len(rows), "; other lines:", len(others))
print("lines that use the package:", sum(r["package"] for r in rows), "; with a name not placed:", sum(1 for r in rows if r["unfollowed"]), "; no names at all:", sum(1 for r in rows if not r["names"]))
print("aliases followed in", sum(1 for r in rows if r["hops"]), "rows; rows where proof_files < table_files:", sum(1 for r in rows if r["proof_files"] < r["table_files"]))
for s in ("RadfordShufflePolynomial", "StoneVonNeumann", "SchurOrthogonalitySquareIntegrable", "QuadraticClassFieldTheory", "Linnik", "GreenRegularCharacters", "GlobalArtinReciprocity", "BrauerDegreeZero", "ChevalleyUnits", "HeckeLAdicCharacterAbove", "UnusedSlot72", "DiscreteSeriesExists"):
    r = next(x for x in rows if x["statement"] == s); print(f'  {s:36s} table {r["table_files"]:7d}  proof {r["proof_files"]:7d}  hops {r["hops"]}  package {r["package"]}  same_as {r["same_as"]}  unfollowed {r["unfollowed"][:2]}')
