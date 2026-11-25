#!/usr/bin/env python3
"""lattex_census.py REPO OUT.json: every non-ASCII character in the repository's tracked .html, .md, .txt, .js, .py and
.lean files (script and style blocks included, since pages build formulas in JavaScript), with how many files use
it and how often. The three LatteX probe tools are left out: their own tables list every character and would count
as use. Text that LatteX itself wrote into a typeset page (the labels of its pictures) is counted like any other."""
import sys, subprocess, json, unicodedata, collections, re
repo, outp = sys.argv[1:3]
SELF = ("tools/lattex_census.py", "tools/lattex_probe_chars.py", "tools/lattex_missing_glyphs.py")
files = [f for f in subprocess.run(["git", "-C", repo, "ls-files"], capture_output=True, text=True).stdout.split("\n")
         if f.endswith((".html", ".md", ".txt", ".js", ".py", ".lean")) and f not in SELF]
count = collections.Counter(); infiles = collections.defaultdict(set)
for f in files:
    try: s = open(repo + "/" + f, encoding="utf-8").read()
    except Exception: continue
    for m in re.finditer(r"&(#x?[0-9a-fA-F]+|[a-zA-Z]+);", s):       # HTML entities count as the character they stand for
        import html as H
        ch = H.unescape(m.group(0))
        if len(ch) == 1 and ord(ch) > 127: count[ch] += 1; infiles[ch].add(f)
    for ch in s:
        if ord(ch) > 127: count[ch] += 1; infiles[ch].add(f)
rows = []
for ch, n in count.most_common():
    try: name = unicodedata.name(ch)
    except ValueError: name = "?"
    rows.append({"ch": ch, "cp": "U+%04X" % ord(ch), "name": name, "cat": unicodedata.category(ch), "n": n, "files": len(infiles[ch]), "eg": sorted(infiles[ch])[:3]})
json.dump({"files_read": len(files), "rows": rows}, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("files read:", len(files), "; distinct non-ASCII characters:", len(rows))
bycat = collections.Counter(r["cat"] for r in rows); print(dict(bycat))
