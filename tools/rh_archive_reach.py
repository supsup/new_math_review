"""How much of the Lean archive of the announced proof of the Riemann Hypothesis do the final theorems use?
Two rigorous LOWER bounds on what they do not use, from names alone. Read-only; nothing is built.

    python3 -I tools/rh_archive_reach.py PATH/TO/extracted/lean/src crew_visuals/rh_proof_reach_data.json

The archive is not part of this repository (mirror 1337isnot1337/riemann-hypothesis-solved, revision 6193bb5).

FIRST BOUND, one level deep. A plain theorem or lemma (no attribute) whose last name component occurs exactly once
in the whole archive, at its own declaration, cannot be used by anything.

SECOND BOUND, following references.

Every use of a declaration writes the last component of its name somewhere (plainly, qualified, or through dot
notation). So: start from the five theorems of Main.lean; whenever a declaration is reached, every identifier
component in its text may be a reference, and EVERY declaration whose name ends in that component is treated as
reached. This over-reaches on purpose (a local variable called h reaches every declaration named h), so what it
reaches is an UPPER bound on what the final theorems use, and what it never reaches is certainly unused by them.

Things that can be used without being named are treated as reached from the start: instances, declarations carrying
an attribute, anything named on an `attribute [...]` line, and every name written in a notation, macro, syntax,
infix, export, alias or open line or before the first declaration of a file (import lines apart: they name files). When such a line follows a
declaration, everything from it to the next declaration is counted too, since a macro can run over several lines.
An instance without a name is not indexed as a declaration; its whole text is counted as reached in the same way.

A declaration's text is taken from its line to the next declaration line in the same file (column 0 only).
What neither bound says: that a declaration which IS reached is used by the proof. Reaching goes by name, and a short
name reaches every declaration that shares it.
"""
import array
import collections
import json
import os
import re
import sys
import time

SRC, OUT = sys.argv[1], sys.argv[2]
# A test of the instrument itself: a third argument FILE:LINE:NAME removes one occurrence of NAME from that line before
# anything is read, as if that one use had been deleted. A theorem used only there must then come out unreached.
MUTANT = sys.argv[3].rsplit(":", 2) if len(sys.argv) > 3 else None
TOKEN = re.compile(r"[^\W\d][\w'₀-₉!?]*")
DECL = re.compile(r"^((?:@\[[^\]]*\]\s*)?)((?:private |protected |noncomputable |unsafe |partial |scoped |local )*)(theorem|lemma|def|abbrev|structure|class|inductive|instance|axiom|opaque)\s+([^\s:({\[]+)")
GLOBAL = re.compile(r"^\s*(?:@\[|(?:private |protected |noncomputable |scoped |local )*instance\b|attribute\b|notation\b|macro\b|macro_rules\b|syntax\b|infix[lr]?\b|prefix\b|postfix\b|export\b|alias\b|open\b|scoped\b|local\b|deriving\b|elab\b|initialize\b|unif_hint\b|set_option\b)")

t0 = time.time()
tid = {}                       # token -> id


def ids(tokens):
    out = set()
    for tk in tokens:
        i = tid.get(tk)
        if i is None:
            i = tid[tk] = len(tid)
        out.add(i)
    return out


kinds, lasts, mods, nlines, toks, rootflag, plain = [], [], [], [], [], [], []
root_tokens = set()
main_decls = []
occurrences = collections.Counter()      # how often each name component occurs in the whole archive
for root, _, files in os.walk(SRC):
    for f in files:
        if not f.endswith(".lean"):
            continue
        p = os.path.join(root, f)
        mod = os.path.relpath(p, SRC)[:-5].replace(os.sep, ".")
        with open(p, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().split("\n")
        if MUTANT and os.path.relpath(p, SRC) == MUTANT[0]:
            k = int(MUTANT[1]) - 1
            cut = re.sub(r"(?<![\w'])" + re.escape(MUTANT[2]) + r"(?![\w'])", "", lines[k], count=1)
            if cut == lines[k]:
                sys.exit("the mutant's name does not occur on that line")
            lines[k] = cut
        starts = []
        for i, line in enumerate(lines):
            for tk in TOKEN.findall(line):
                occurrences[tk] += 1
            if GLOBAL.match(line):
                root_tokens |= ids(TOKEN.findall(line))
            m = DECL.match(line)
            if m:
                attr = bool(m.group(1)) or (i > 0 and lines[i - 1].lstrip().startswith("@["))
                comp = TOKEN.findall(m.group(4))
                starts.append((i, m.group(3), comp[-1] if comp else m.group(4), attr))
        first = starts[0][0] if starts else len(lines)
        if first:                                   # the file's header, WITHOUT its import lines: an import names a file, not a declaration
            root_tokens |= ids(TOKEN.findall("\n".join(l for l in lines[:first] if not l.startswith("import "))))
        for k, (i, kind, last, attr) in enumerate(starts):
            end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
            for j in range(i + 1, end):         # a notation, macro or attribute after a declaration may run over several lines:
                if GLOBAL.match(lines[j]):       # everything from its first line to the next declaration counts as reached
                    root_tokens |= ids(TOKEN.findall("\n".join(lines[j:end])))
                    break
            d = len(kinds)
            kinds.append(kind)
            plain.append(not attr)
            lasts.append(ids([last]).pop())
            mods.append(mod)
            nlines.append(end - i)
            toks.append(array.array("I", sorted(ids(TOKEN.findall("\n".join(lines[i:end]))))))
            rootflag.append(attr or kind == "instance")
            if mod == "Main":
                main_decls.append(d)
print("parsed: declarations", len(kinds), "distinct tokens", len(tid), "seconds %.0f" % (time.time() - t0), flush=True)

by_last = collections.defaultdict(list)
for d, l in enumerate(lasts):
    by_last[l].append(d)

reached = bytearray(len(kinds))
seen_tok = bytearray(len(tid))
stack = []


def reach_decl(d):
    if not reached[d]:
        reached[d] = 1
        stack.append(d)


def see_token(t):
    if not seen_tok[t]:
        seen_tok[t] = 1
        for d in by_last.get(t, ()):
            reach_decl(d)


for d in main_decls:
    reach_decl(d)
for d, r in enumerate(rootflag):
    if r:
        reach_decl(d)
for t in root_tokens:
    see_token(t)
while stack:
    d = stack.pop()
    for t in toks[d]:
        see_token(t)

is_thm = [k in ("theorem", "lemma") for k in kinds]
n_thm = sum(is_thm)
un_thm = sum(1 for d in range(len(kinds)) if is_thm[d] and not reached[d])
un_all = sum(1 for d in range(len(kinds)) if not reached[d])
ln_thm = sum(nlines[d] for d in range(len(kinds)) if is_thm[d])
ln_un_thm = sum(nlines[d] for d in range(len(kinds)) if is_thm[d] and not reached[d])
ln_all = sum(nlines)
ln_un = sum(nlines[d] for d in range(len(kinds)) if not reached[d])
top_un, top_tot = collections.Counter(), collections.Counter()
two_un, two_tot = collections.Counter(), collections.Counter()
for d in range(len(kinds)):
    p = mods[d].split(".")
    k2 = ".".join(p[:2]) if len(p) >= 3 else p[0]
    top_tot[p[0]] += nlines[d]
    two_tot[k2] += nlines[d]
    if not reached[d]:
        top_un[p[0]] += nlines[d]
        two_un[k2] += nlines[d]
inv = {v: k for k, v in tid.items()}
once = [d for d in range(len(kinds)) if is_thm[d] and plain[d] and occurrences[inv[lasts[d]]] == 1]
probe = {}
for name in ("stmt3c", "DefiniteChainFromRallis", "familyDefiniteLiftChain", "DefiniteLiftChain", "duty_seven_library", "PageWin", "LiftChain", "ThetaChainStatement",
             "ThetaLiftChainTyped", "ConstantFreeStatements", "ConstantFreeFamily", "constant_free_items_of_parts", "InChain", "ChainTied", "TiePts", "TwoUpOK", "twoUpOK_of_steps",
             "tLiftK", "TLiftK", "IsLift", "geoOne_holds", "GeoOne", "toCoreK", "coreAll_of", "galoisLocalGlobal_of_geometry_lift", "recTExists", "vwin_of_row", "VWin",
             "rh_of_every", "everyCharacter", "EveryCharacter", "plugAll", "plugWin", "imprimitive", "zeroFreeAll_of_topG", "level_gm_le_on_family_scales",
             "every_character_of_literature_of_vWin", "deligne_ribet_of_literature", "UnusedSlot72", "TopCovolSlim2", "topCovolSlim2_use_alt_alt"):
    t = tid.get(name)
    ds = by_last.get(t, []) if t is not None else []
    probe[name] = [len(ds), sum(1 for d in ds if reached[d])]
out = {"revision": "6193bb5", "tokens": sum(occurrences.values()), "distinct_tokens": len(occurrences),
       "plain_theorems": sum(1 for d in range(len(kinds)) if is_thm[d] and plain[d]),
       "named_once": len(once), "named_once_lines": sum(nlines[d] for d in once),
       "named_once_in_main": sum(1 for d in once if mods[d] == "Main"),
       "declarations": len(kinds), "reached": int(sum(reached)), "unreached": un_all,
       "theorems": n_thm, "unreached_theorems": un_thm, "theorem_lines": ln_thm, "unreached_theorem_lines": ln_un_thm,
       "declaration_lines": ln_all, "unreached_lines": ln_un, "root_declarations": int(sum(rootflag)), "root_tokens": len(root_tokens),
       "by_top": [[k, top_un[k], top_tot[k]] for k, _ in top_tot.most_common()],
       "by_two": [[k, two_un[k], two_tot[k]] for k, _ in two_un.most_common(12)], "probe": probe}
if MUTANT:
    out["mutant"] = ":".join(MUTANT)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=0)
    fh.write("\n")
print("first bound: %d of %d theorems and lemmas are named exactly once (%.1f%%), %d lines" % (len(once), n_thm, 100 * len(once) / n_thm, out["named_once_lines"]))
print("declarations %d ; reached %d ; never reached %d (%.1f%%)" % (len(kinds), sum(reached), un_all, 100 * un_all / len(kinds)))
print("theorems and lemmas %d ; never reached %d (%.1f%%) ; lines %d of %d (%.1f%%)" % (n_thm, un_thm, 100 * un_thm / n_thm, ln_un_thm, ln_thm, 100 * ln_un_thm / ln_thm))
print("lines inside declarations %d ; in never-reached ones %d (%.1f%%)" % (ln_all, ln_un, 100 * ln_un / ln_all))
print("roots: %d declarations with an attribute or instances, %d global tokens" % (sum(rootflag), len(root_tokens)))
for k, a, b in out["by_top"]:
    print("  %-20s %9d of %9d lines never reached (%.1f%%)" % (k, a, b, 100 * a / b if b else 0))
print("probe [declared, reached]:", probe)
print("seconds %.0f" % (time.time() - t0))
