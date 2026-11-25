#!/usr/bin/env python3
"""rh_published_replay_gen.py ARCHIVE_SRC SCAN2.json OUT.lean TIER.txt NAME... [+MODULE...]

SCAN2.json is the output of tools/rh_published_scan2.py. For each named statement this writes, into OUT.lean, the line of the
archive's table of published results (EveryCharacterOfLiteratureOfVWin.lean) that proves it, changed in two ways only:
  1. a call to another line of the table, '(x_of_literature O)', is replaced by that line's own right-hand side;
  2. a named theorem that is a one-line repeat of another ('theorem a : T := b') is replaced by the theorem at the end of
     the chain of repeats (at most 6 steps), so that the file holding the proof is imported and not a file that only
     repeats it.
A line with no repeats comes out as the table wrote it and is named pub_<statement>; a line where a name was replaced is
named direct_<statement>. Each is followed by '#print axioms'. TIER.txt receives the modules to build first. For each
statement the tool also prints one line 'KIND <statement> <kind>': 'written' (the table's line as it stands), 'direct' (the
line was one name, now the theorem at the end of its chain) or 'replaced' (a longer line with a name replaced inside it).
Refuses a statement whose line still mentions the package O after step 1 (it uses a statement the archive assumes).
An argument written +MODULE adds that module to the imports and to TIER.txt. It is needed for the few statements whose
name the archive defines in a file that the proof's own files do not import (tools/rh_published_def_files.py lists them).
This tool decides nothing: whether a rewritten line proves the statement is for Lean to say when OUT.lean is compiled.
Names are placed by reading the files the scan listed for these statements and what they import, with a simple reading of
'namespace' and 'end' lines; a name it cannot place in exactly one file is left as the table wrote it. Reads only."""
import json, os, re, sys
src, sj, outp, tierp = sys.argv[1:5]
want = [a for a in sys.argv[5:] if not a.startswith("+")]; extra = [a[1:] for a in sys.argv[5:] if a.startswith("+")]
d = json.load(open(sj, encoding="utf-8")); rows = {r["statement"]: r for r in d["statements"]}
WR = "Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean"
text = open(os.path.join(src, WR), encoding="utf-8").read()
table = {}                                                    # table theorem -> (type, right-hand side)
for ch in re.split(r"^(?=theorem )", text, flags=re.M)[1:]:
    m = re.match(r"theorem (\S+) \(O : [^)]*\) :(.*?):=([^\n]*)\n?", ch, flags=re.S)
    if not m: continue
    body = [m.group(3).strip()] if m.group(3).strip() else []
    for line in ch[m.end():].split("\n"):
        if line[:1] in (" ", "\t") and line.strip(): body.append(line.strip())
        elif line.strip() == "": continue
        else: break
    table[m.group(1)] = (" ".join(m.group(2).split()), " ".join(body))
pub = {}
for n, (typ, body) in table.items():
    m = re.fullmatch(r"(?:_root_\.)?GlobalTheory\.Published\.(\w+)", typ)
    if m: pub.setdefault(m.group(1), n)
call = re.compile(r"(?:_root_\.)?([A-Za-z_][\w'.₀-₉]*) O\b")
def expand(n, depth=0):
    if depth > 8: sys.exit("REFUSING: the table's lines call each other more than 8 deep at " + n)
    def sub(m):
        x = m.group(1)
        if x not in table: return m.group(0)
        return "(" + expand(x, depth + 1) + ")"
    return call.sub(sub, table[n][1])
# ---- the files to read for names: everything the scan's modules for these statements import
IMPORT = re.compile(r"^\s*(?:public\s+|private\s+|meta\s+)*import\s+(?:all\s+)?(\S+)")
def fpath(m): return os.path.join(src, *m.split(".")) + ".lean"
imps = {}
def imports(m):
    if m not in imps:
        out = []
        for line in open(fpath(m), encoding="utf-8"):
            g = IMPORT.match(line)
            if g: out.append(g.group(1))
            elif line.strip() and not line.lstrip().startswith(("--", "/-", "module", "set_option", "public", "private", "meta")): break
        imps[m] = out
    return imps[m]
def closure(mods):
    seen, st = set(), list(mods)
    while st:
        m = st.pop()
        if m in seen or not os.path.exists(fpath(m)): continue
        seen.add(m); st.extend(imports(m))
    return seen
for s in want:
    if s not in rows or s not in pub: sys.exit("REFUSING: no line in the table for " + s)
files = closure({m for s in want for m in rows[s]["table_modules"] + rows[s]["proof_modules"]})
texts = {}
DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|nonrec\s+)*(theorem|lemma|def|abbrev)\s+((?:_root_\.)?[\w'.₀-₉]+)")
NS = re.compile(r"^namespace\s+(\S+)"); END = re.compile(r"^end\s+(\S+)")
index, indexed = {}, set()                                    # full name -> [(module, right-hand side, kind)]
def index_names(lasts):
    lasts = set(lasts) - indexed
    if not lasts: return
    indexed.update(lasts)
    for mod in sorted(files):
        if mod not in texts: texts[mod] = open(fpath(mod), encoding="utf-8").read()
        tx = texts[mod]
        if not any(nm in tx for nm in lasts): continue
        lines = tx.split("\n"); stack = []; i = 0
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
                index.setdefault(full, []).append((mod, decl.split(":=", 1)[1].strip() if ":=" in decl else "", g.group(1)))
                i = j; continue
            i += 1
def place(c):
    """(full name, module, right-hand side, kind) if exactly one file read declares a name that is c or ends with .c"""
    hits = [(full, v) for full, vs in index.items() if full == c or full.endswith("." + c) for v in vs]
    use = [h for h in hits if h[0] == c] or hits
    return (use[0][0],) + use[0][1] if len({v[0] for _, v in use}) == 1 and len({f for f, _ in use}) == 1 else None
ident = re.compile(r"(?:_root_\.)?([A-Za-z_][\w']*(?:\.[A-Za-z_₀-₉][\w'₀-₉]*)+)")
single = re.compile(r"(?:_root_\.)?([A-Za-z_][\w'.₀-₉]*)$")
def last(c): return c.rsplit(".", 1)[-1]
def chain(c):
    """follow one-line repeats from c; returns the list of placements, first to last"""
    out, cur = [], c
    while len(out) <= 6:
        index_names({last(cur)}); pl = place(cur)
        if pl is None: break
        out.append(pl)
        m = single.fullmatch(pl[2]) if pl[3] in ("theorem", "lemma") else None
        if not m: break
        index_names({last(m.group(1))})
        if place(m.group(1)) is None: break
        cur = m.group(1)
    return out
items, mods, report = [], set(extra), []
for m in extra:
    if not os.path.exists(fpath(m)): sys.exit("REFUSING: no such archive module: " + m)
for s in want:
    body = expand(pub[s])
    if re.search(r"\bO\b", body): sys.exit("REFUSING: the line for %s uses the package O" % s)
    consts = sorted(set(ident.findall(body)), key=len, reverse=True)
    index_names({last(c) for c in consts})
    changed = []
    for c in consts:
        ch = chain(c)
        if not ch: continue
        full, mod = ch[-1][0], ch[-1][1]
        mods.add(mod)
        if len(ch) > 1:
            body, k = re.subn(r"(?<![\w.'])(?:_root_\.)?" + re.escape(c) + r"(?![\w.'])", lambda _m: full, body)
            if k: changed.append((c, full, len(ch) - 1))
    items.append((("direct_" if changed else "pub_") + s, s, body))
    report.append((s, changed, "written" if not changed else "direct" if single.fullmatch(body) else "replaced"))
with open(outp, "w", encoding="utf-8") as f:
    for m in sorted(mods): f.write("import " + m + "\n")
    f.write("\nset_option linter.all false\nset_option maxHeartbeats 400000\n\n")
    for nm, s, body in items: f.write(f"theorem {nm} : GlobalTheory.Published.{s} :=\n  {body}\n#print axioms {nm}\n\n")
open(tierp, "w", encoding="utf-8").write("\n".join(sorted(mods)) + "\n")
print("statements:", len(items), "; as the table wrote them:", sum(1 for _, c, _k in report if not c), "; with a name replaced:", sum(1 for _, c, _k in report if c), "; modules to build:", len(mods), "; archive files those import:", len(closure(mods)))
for s, changed, kind in report:
    print("  ", s, "(as written)" if not changed else "")
    for c, full, hops in changed: print("       ", c, "->", full, "(%d)" % hops)
for s, changed, kind in report: print("KIND", s, kind)
