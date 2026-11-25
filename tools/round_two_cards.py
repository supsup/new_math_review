"""Round two (2026-11-24): add the cards that draw on more than one source collection.

Run from the repository root:  python3 -I tools/round_two_cards.py
Needs Java and a LatteX jar: set LATTEX_JAR to its path. It REFUSES to write if a formula fails.

What it does, and nothing else:
  - typesets each card formula with LatteX (inline SVG for showcase.html, formulas/f_<hash>.svg for showcase.md);
  - writes the card pictures into art/ from the numbers computed here (no hand-typed coordinates);
  - inserts each card between its own markers in showcase.html and showcase.md (idempotent: a re-run
    replaces its own block), and the picture overlays between their markers;
  - re-runs tools/showcase_nav.py so the Cards menu lists the new card.

Card 379 (VP and VNP) is shared work: the plain reading of the classes, the statement table, the import
trace and the small enumerations are Lattice's (vp-evidence-panel, 2026-11-24); the target-to-paper trace
and the Laurent example are Marlow's; the cross-reading of the two formal statements, the two pictures
and the assembly are Fixpoint's. Sources are pinned by revision in the card.
"""
import hashlib
import html
import math
import os
import re
import subprocess
import sys

JAR = os.environ.get("LATTEX_JAR", "")      # path to a LatteX jar (https://github.com/supsup/LatteX); set LATTEX_JAR
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OAI = "https://github.com/openai/math/blob/f57028540"
ANT = "https://github.com/anthropics/formal-math/blob/11b6c7e"

F_DEF = r"\mathrm{perm}_m=\sum_{\sigma\in S_m}\prod_{i=1}^{m}x_{i,\sigma(i)},\qquad \det{}_m=\sum_{\sigma\in S_m}\operatorname{sgn}(\sigma)\prod_{i=1}^{m}x_{i,\sigma(i)}"
F_ANT = r"\text{Anthropic, in Lean:}\quad \text{every circuit for } \mathrm{HC}_m \text{ has more than } m^{\,c\,(\log_2 m)^{1/3}} \text{ gates}\quad(\text{some } c>0,\ \text{all large } m)"
F_OAI = r"\text{OpenAI, paper:}\quad \text{border circuits for } f_n \text{ need } \exp\!\big(\Omega\big((\log n)^{5/4}\big)\big) \text{ gates};\qquad \text{in Lean:}\ \ \mathrm{VP}\neq\mathrm{VNP}"
FORMULAS = [F_DEF, F_ANT, F_OAI]


def render(sources):
    if not JAR or not os.path.exists(JAR):
        sys.exit("REFUSING to write: set LATTEX_JAR to a LatteX jar; the card formulas are typeset by it")
    proc = subprocess.run(["java", "-jar", JAR, "--batch"], input="\n".join(sources) + "\n", capture_output=True, text=True)
    recs = proc.stdout.split("\0")
    if recs and recs[-1].strip() == "":
        recs.pop()
    if len(recs) != len(sources):
        sys.exit(f"REFUSING to write: LatteX returned {len(recs)} records for {len(sources)} formulas: {proc.stderr[:300]}")
    out = {}
    for src, rec in zip(sources, recs):
        if rec.startswith("lattex: error") or "<svg" not in rec:
            sys.exit(f"REFUSING to write: LatteX failed on\n  {src}\n  {rec[:300]}")
        out[src] = rec[rec.find("<svg"):].strip()
    return out


# ---------- pictures (house style of art/: Georgia, paper ground) ----------
INK, MUTED, ACC, GRID, PAPER, BLUE, VIOLET, RED, GREEN = "#1d1b18", "#5b5348", "#8a4b16", "#e3ddd2", "#fbf9f4", "#2456c8", "#7a4fbf", "#b83a2e", "#1f7a52"


def t(x, y, s, size=12, fill=INK, anchor="start", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{w}>{html.escape(s)}</text>'


def perm_det_narrow_svg():
    """The same six terms stacked three by two, for a phone. Signs are computed the same way."""
    letters = "abcdefghi"
    perms = [(0, 1, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0), (1, 0, 2), (0, 2, 1)]
    sign = lambda p: -1 if sum(1 for i in range(3) for j in range(i + 1, 3) if p[i] > p[j]) % 2 else 1
    W, H, cell, gap = 450, 520, 34, 3
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="The six products of a 3 by 3 grid, stacked: all plus for the permanent, three minus for the determinant" font-family="Georgia, serif">',
         f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
         t(20, 30, "Six ways to pick one cell from every row and column", 17, ACC),
         t(20, 52, "P: the sign in the permanent.   D: the sign in the determinant.", 13, MUTED)]
    step = (W - 40) / 3
    for k, p in enumerate(perms):
        x0 = 20 + (k % 3) * step + (step - (3 * cell + 2 * gap)) / 2
        y0 = 76 + (k // 3) * 218
        name = ""
        for r in range(3):
            for c in range(3):
                on = p[r] == c
                o.append(f'<rect x="{x0 + c * (cell + gap):.1f}" y="{y0 + r * (cell + gap):.1f}" width="{cell}" height="{cell}" rx="3" fill="{"#e6eefc" if on else PAPER}" stroke="{BLUE if on else GRID}"/>')
                o.append(t(x0 + c * (cell + gap) + cell / 2, y0 + r * (cell + gap) + cell / 2 + 5, letters[r * 3 + c], 15, INK if on else MUTED, "middle"))
            name += letters[r * 3 + p[r]]
        cx = x0 + (3 * cell + 2 * gap) / 2
        o.append(t(cx, y0 + 3 * (cell + gap) + 24, "·".join(name), 17, INK, "middle"))
        for j, (lab, sg) in enumerate((("P", 1), ("D", sign(p)))):
            bx = cx - 30 + j * 60
            yy = y0 + 3 * (cell + gap) + 56
            o.append(t(bx - 16, yy, lab, 14, MUTED, "middle"))
            o.append(f'<circle cx="{bx + 6:.1f}" cy="{yy - 5:.1f}" r="12" fill="{GREEN if sg > 0 else RED}"/>')
            o.append(t(bx + 6, yy + 1, "+" if sg > 0 else "−", 18, PAPER, "middle", "bold"))
    o.append("</svg>")
    return "\n".join(o)


def perm_det_svg():
    """The six terms of a 3 x 3 permanent, with the determinant's signs underneath. Signs are computed."""
    letters = "abcdefghi"
    perms = [(0, 1, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0), (1, 0, 2), (0, 2, 1)]

    def sign(p):
        inv = sum(1 for i in range(3) for j in range(i + 1, 3) if p[i] > p[j])
        return -1 if inv % 2 else 1

    if sorted(perms) != sorted(__import__("itertools").permutations(range(3))) or [sign(p) for p in perms] != [1, 1, 1, -1, -1, -1]:
        sys.exit("REFUSING to write: the six permutations or their signs are wrong")
    W, H, cell, gap = 900, 330, 30, 3
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="The six products of a 3 by 3 grid: all plus for the permanent, three minus for the determinant" font-family="Georgia, serif">',
         f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
         t(40, 34, "Six ways to pick one cell from every row and every column", 17, ACC),
         t(40, 56, "Multiply the three picked cells. The permanent adds all six products. The determinant flips the sign of three.", 12, MUTED)]
    left = 150
    step = (W - left - 30) / 6
    for k, p in enumerate(perms):
        x0 = left + k * step + (step - (3 * cell + 2 * gap)) / 2
        y0 = 82
        name = ""
        for r in range(3):
            for c in range(3):
                on = p[r] == c
                o.append(f'<rect x="{x0 + c * (cell + gap):.1f}" y="{y0 + r * (cell + gap):.1f}" width="{cell}" height="{cell}" rx="3" fill="{"#e6eefc" if on else PAPER}" stroke="{BLUE if on else GRID}"/>')
                o.append(t(x0 + c * (cell + gap) + cell / 2, y0 + r * (cell + gap) + cell / 2 + 4.5, letters[r * 3 + c], 13, INK if on else MUTED, "middle"))
            name += letters[r * 3 + p[r]]
        cx = x0 + (3 * cell + 2 * gap) / 2
        o.append(t(cx, y0 + 3 * (cell + gap) + 22, "·".join(name), 15, INK, "middle"))
        for row, (lab, sg) in enumerate((("permanent", 1), ("determinant", sign(p)))):
            yy = y0 + 3 * (cell + gap) + 52 + row * 34
            o.append(f'<circle cx="{cx:.1f}" cy="{yy - 5:.1f}" r="11" fill="{GREEN if sg > 0 else RED}"/>')
            o.append(t(cx, yy, "+" if sg > 0 else "−", 16, PAPER, "middle", "bold"))
            if k == 0:
                o.append(t(left - 12, yy, lab, 13, INK, "end"))
    yb = 82 + 3 * (cell + gap) + 52
    o.append(t(40, yb + 68, "The determinant has a recipe of polynomial size. The claims say the permanent has none.", 12, MUTED))
    o.append("</svg>")
    return "\n".join(x for x in o if x)


def floor_svg():
    """Every bound written as m to a power, with the unknown constant set to 1. All curves are computed here."""
    LOG2_10, LN10 = math.log2(10), math.log(10)
    old = lambda lg: 2 + math.log(lg * LOG2_10) / (lg * LN10)          # m^2 log2 m
    ant = lambda lg: (lg * LOG2_10) ** (1 / 3)                          # m^((log2 m)^(1/3))
    oai = lambda lg: (lg * LN10) ** (1 / 4)                             # exp((ln m)^(5/4)) = m^((ln m)^(1/4))
    top = lambda lg: 1 + 10 ** lg / (lg * LOG2_10)                      # m 2^m
    # milestones, checked against the closed forms
    ant3, ant10, oai3, oai10 = 27 / LOG2_10, 1000 / LOG2_10, 81 / LN10, 1e4 / LN10
    for f, k, lg in ((ant, 3, ant3), (ant, 10, ant10), (oai, 3, oai3), (oai, 10, oai10)):
        if abs(f(lg) - k) > 1e-9:
            sys.exit("REFUSING to write: a milestone does not sit on its curve")
    if not (abs(top(math.log10(4)) - 3) < 1e-9 and 9.9 < top(math.log10(51)) < 10.1):
        sys.exit("REFUSING to write: the ceiling milestones are wrong")
    W, H, ML, MR, MT, MB, YMAX, UMAX = 900, 470, 70, 30, 84, 86, 16, 3.0
    X = lambda u: ML + (W - ML - MR) * u / UMAX
    Y = lambda e: H - MB - (H - MT - MB) * min(e, YMAX) / YMAX
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Each bound for the permanent written as m to a power, against the width m of the grid" font-family="Georgia, serif">',
         f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
         t(ML, 32, "How high is the floor? Every bound written as m to a power", 17, ACC),
         t(ML, 53, "A flat line means polynomial. The two claimed floors rise forever, slowly; the 1963 method (the ceiling) leaves the chart near m = 100.", 12, MUTED),
         t(ML, 70, "The theorems say 'for some constant c > 0'; here c = 1, so read the shapes, not the heights.", 12, MUTED)]
    for e in range(0, YMAX + 1, 2):
        o.append(f'<line x1="{ML}" x2="{W - MR}" y1="{Y(e):.1f}" y2="{Y(e):.1f}" stroke="{GRID}"/>')
        o.append(t(ML - 8, Y(e) + 4, f"m^{e}", 11, MUTED, "end"))
    for lg, lab in ((1, "10"), (2, "100"), (3, "1000"), (6, "10^6"), (10, "10^10"), (30, "10^30"), (100, "10^100"), (300, "10^300"), (1000, "10^1000")):
        u = math.log10(lg)
        o.append(f'<line x1="{X(u):.1f}" x2="{X(u):.1f}" y1="{MT}" y2="{H - MB}" stroke="{GRID}"/>')
        o.append(t(X(u), H - MB + 16, lab, 11, MUTED, "end" if u > 2.9 else "middle"))
    o.append(t((ML + W - MR) / 2, H - MB + 36, "m, the width of the grid (each step to the right is a much bigger grid)", 12, MUTED, "middle"))

    def path(f, color, dash="", clip=False):
        pts, done = [], False
        for i in range(601):
            u = UMAX * i / 600
            e = f(10 ** u)
            if e > YMAX:
                if clip:
                    pts.append((X(u), Y(YMAX)))
                done = True
                break
            pts.append((X(u), Y(e)))
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.4"{(" stroke-dasharray=" + chr(34) + dash + chr(34)) if dash else ""}/>'

    o += [path(old, MUTED, "6 4"), path(oai, VIOLET), path(ant, BLUE), path(top, RED, clip=True)]
    for i, (color, lab) in enumerate(((MUTED, "old proven floor, about m²·log m"), (BLUE, "Anthropic's claimed floor (in Lean)"), (VIOLET, "OpenAI's claimed floor (paper only)"), (RED, "ceiling: Ryser's method, 1963"))):
        lx, ly = ML + (i % 2) * 400, H - 30 + (i // 2) * 18
        o.append(f'<line x1="{lx}" x2="{lx + 22}" y1="{ly - 4}" y2="{ly - 4}" stroke="{color}" stroke-width="3"/>')
        o.append(t(lx + 28, ly, lab, 12, INK))
    o.append("</svg>")
    facts = {"ant3": ant3, "ant10": ant10, "oai3": oai3, "oai10": oai10}
    return "\n".join(o), facts


def floor_narrow_svg():
    """The floor picture for a phone: same four curves, fewer ticks, larger type. Curves are computed here."""
    LOG2_10, LN10 = math.log2(10), math.log(10)
    old = lambda lg: 2 + math.log(lg * LOG2_10) / (lg * LN10)
    ant = lambda lg: (lg * LOG2_10) ** (1 / 3)
    oai = lambda lg: (lg * LN10) ** (1 / 4)
    top = lambda lg: 1 + 10 ** lg / (lg * LOG2_10)
    W, H, ML, MR, MT, MB, YMAX, UMAX = 450, 520, 52, 14, 78, 150, 16, 3.0
    X = lambda u: ML + (W - ML - MR) * u / UMAX
    Y = lambda e: H - MB - (H - MT - MB) * min(e, YMAX) / YMAX
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Each bound for the permanent written as m to a power, phone layout" font-family="Georgia, serif">',
         f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
         t(16, 30, "How high is the floor?", 19, ACC),
         t(16, 52, "Every bound as a power of m. Flat means polynomial.", 14, MUTED),
         t(16, 70, "Unknown constant set to 1: read the shapes.", 14, MUTED)]
    for e in range(0, YMAX + 1, 4):
        o.append(f'<line x1="{ML}" x2="{W - MR}" y1="{Y(e):.1f}" y2="{Y(e):.1f}" stroke="{GRID}"/>')
        o.append(t(ML - 6, Y(e) + 5, f"m^{e}", 13, MUTED, "end"))
    for lg, lab in ((1, "10"), (10, "10^10"), (100, "10^100"), (1000, "10^1000")):
        u = math.log10(lg)
        o.append(f'<line x1="{X(u):.1f}" x2="{X(u):.1f}" y1="{MT}" y2="{H - MB}" stroke="{GRID}"/>')
        o.append(t(X(u), H - MB + 18, lab, 13, MUTED, "end" if u > 2.9 else ("start" if u < 0.1 else "middle")))
    o.append(t((ML + W - MR) / 2, H - MB + 38, "m, the width of the grid", 13, MUTED, "middle"))

    def path(f, color, dash="", clip=False):
        pts = []
        for i in range(401):
            u = UMAX * i / 400
            e = f(10 ** u)
            if e > YMAX:
                if clip:
                    pts.append((X(u), Y(YMAX)))
                break
            pts.append((X(u), Y(e)))
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3"{(" stroke-dasharray=" + chr(34) + dash + chr(34)) if dash else ""}/>'

    o += [path(old, MUTED, "6 4"), path(oai, VIOLET), path(ant, BLUE), path(top, RED, clip=True)]
    for i, (color, lab) in enumerate(((MUTED, "old proven floor, about m²·log m"), (BLUE, "Anthropic's claimed floor (in Lean)"), (VIOLET, "OpenAI's claimed floor (paper only)"), (RED, "ceiling: Ryser's method, 1963"))):
        ly = H - MB + 62 + i * 21
        o.append(f'<line x1="16" x2="42" y1="{ly - 5}" y2="{ly - 5}" stroke="{color}" stroke-width="4"/>')
        o.append(t(50, ly, lab, 14, INK))
    o.append("</svg>")
    return "\n".join(o)


# ---------- the card ----------
def card_379(svgs, facts):
    e = html.escape
    lnk = lambda href, text: f'<a href="{href}">{e(text)}</a>'
    rows = [
        ("The checked sentence",
         "One target, vp_ne_vnp: the two classes are 'not equal', as predicates on families with 2n variables at step n, over every field.",
         "Five targets. 'separation': VP sits strictly inside VNP, over every field. Plus the lower bound, its approximate form, 'VNP is not inside the closure of VP', and the permanent over the real numbers."),
        ("How a circuit is sized",
         "Counts the additions, subtractions and multiplications. Variables and numbers are free. Size bounds hold from some point on.",
         "Counts every line: variables and numbers too. Only + and ×. Size bounds hold at every size (n^a + a)."),
        ("How strong a bound",
         "The checked target has no rate. The scope note says the Lean also proves that the size exceeds every fixed power, for an explicit family, for the Hamiltonian cycle polynomial, and for the permanent where 1 + 1 is not 0. The rate exp(Ω((log n)^(5/4))), for approximating circuits, is in the paper only.",
         "More than m^(c·(log₂ m)^(1/3)) gates for the Hamiltonian cycle polynomial over every field, and for the permanent where 1 + 1 is not 0; the same for circuits that only approximate. One constant c for all fields."),
        ("How it was checked",
         "A Comparator config exists; the second kernel (nanoda) is switched off in it. We found no public run record. The proof reaches three outside libraries, two of them patched (Lattice's import trace).",
         "Publisher CI on 23 Nov: build, Comparator and the second kernel all passed (Lattice and Fixpoint read the run's result). Depends on Mathlib only."),
    ]
    table = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in rows)
    f3, f10 = facts["ant3"], facts["ant10"]
    return f"""<article class="card" id="card-379">
  <header><span class="fam">family 379 · formal-math vp-vnp</span><span class="fam by">card by Lattice, Marlow and Fixpoint</span><h2>Claimed twice in one day: the permanent has no small circuit (wherever 1 + 1 ≠ 0)</h2></header>
  <p class="verdict">TWO STATEMENTS READ; ONE PUBLISHER CHECK PASSED; ANTHROPIC'S PROOF BUILT BY FIXPOINT; OPENAI'S NOT BUILT BY US.</p>
  <figure class="cardfig" id="art-perm_det_six_terms">
    <a class="zoom" href="#big-art-perm_det_six_terms" title="click to enlarge"><picture><source media="(max-width: 600px)" srcset="art/perm_det_six_terms_narrow.svg"><img src="art/perm_det_six_terms.svg" alt="The six products of a 3 by 3 grid, with the signs of the permanent and of the determinant"></picture></a>
    <figcaption><b>Changing three signs changes the problem.</b> The same six products. All plus signs give the permanent; three minus signs give the determinant. {lnk("round_two_pictures.html#perm", "Flip the signs yourself")}.</figcaption>
  </figure>
  <p class="claim"><b>In one sentence.</b> On 23 November 2026 two labs each claimed that the permanent, a polynomial that looks almost exactly like the determinant, cannot be computed by any small recipe of additions and multiplications, over fields where 1 + 1 ≠ 0. This is "VP ≠ VNP", the arithmetic cousin of P ≠ NP. It does not settle P ≠ NP.</p>
  <p class="claim"><b>Step by step.</b></p>
  <ol class="steps">
    <li><b>A recipe.</b> An arithmetic circuit is a recipe for a polynomial: start from variables and numbers, and combine them with + and ×. Its size is the number of steps.</li>
    <li><b>The easy twin.</b> Take an m by m grid of variables. Pick one cell from every row and every column, multiply, and add up all the ways with alternating signs: that is the determinant. There are m! ways, yet a recipe of polynomial size exists, and it needs no division (Berkowitz, 1984).</li>
    <li><b>The hard twin.</b> Set every sign to plus and you have the permanent. Ryser's exact recipe from 1963 uses about m·2<sup>m</sup> operations, and no recipe of polynomial size is known.</li>
    <li><b>The question.</b> VP is the class of polynomial families with small recipes. VNP allows one more move: write a small recipe with some extra yes/no inputs, then add up its output over every setting of them. For one extra bit b and the recipe (1 − b)x² + bx, the two settings give x² and x, and the sum is x² + x. With k extra bits one short instruction describes 2<sup>k</sup> terms. The permanent is the standard hard member of VNP. Is VNP really bigger than VP?</li>
    <li><b>The two claims.</b> Yes: where 1 + 1 ≠ 0 the permanent needs recipes that outgrow every fixed power of m, and a sibling, the Hamiltonian cycle polynomial, does so over every field. Anthropic's Lean file states a growth rate. OpenAI's Lean file states the bare separation, and its paper gives a rate.</li>
    <li><b>What it does not say.</b> Nothing about P ≠ NP: these recipes must work for all numbers, not only 0 and 1. And nothing like "needs 2<sup>m</sup>": the claimed floor rises very slowly (second picture).</li>
  </ol>
  <div class="math" role="img" aria-label="{e(F_DEF)}">{svgs[F_DEF]}</div>
  <div class="math" role="img" aria-label="{e(F_ANT)}">{svgs[F_ANT]}</div>
  <div class="math" role="img" aria-label="{e(F_OAI)}">{svgs[F_OAI]}</div>
  <p class="claim"><b>How sure is each part?</b></p>
  <ul class="steps">
    <li><b>That the formal statements say this:</b> Fixpoint and Lattice read both statement files; Marlow traced each checked target to its theorem in the papers.</li>
    <li><b>That the proofs check:</b> Anthropic's publisher run passed, with a second, independent kernel. For OpenAI's we found no public run record, and its config switches the second kernel off.</li>
    <li><b>That the mathematics is right:</b> Anthropic says its proof has had no human mathematical check ("no human mathematician has checked the proof"). We found no statement either way from OpenAI.</li>
    <li><b>What we ran:</b> word scans of both proof trees and the small exact checks below. And on 25 November 2026 Fixpoint built Anthropic's proof with Lean, as its README says: the build completed (9,032 jobs) and its five headline theorems rest on Lean's three standard axioms and nothing else. The second checker, Comparator, we did not run. OpenAI's proof we have not built. <a href="crew_visuals/lean_runs.txt">The record of the run</a>.</li>
  </ul>
  <figure class="cardfig" id="art-vp_exponent_floor">
    <a class="zoom" href="#big-art-vp_exponent_floor" title="click to enlarge"><picture><source media="(max-width: 600px)" srcset="art/vp_exponent_floor_narrow.svg"><img src="art/vp_exponent_floor.svg" alt="Each bound for the permanent written as m to a power"></picture></a>
    <figcaption><b>How high is the floor?</b> Every bound written as "m to the power …", with the unknown constant set to 1. A flat line would mean polynomial. Anthropic's claimed floor passes m³ near m = 10<sup>{f3:.1f}</sup> and m<sup>10</sup> near 10<sup>{f10:.0f}</sup>; OpenAI's paper bound passes them near 10<sup>{facts["oai3"]:.0f}</sup> and 10<sup>{facts["oai10"]:.0f}</sup>; the ceiling passes m³ at m = 4 and m<sup>10</sup> near m = 51. {lnk("round_two_pictures.html#perm", "Change the constant")}.</figcaption>
  </figure>
  <p class="claim"><b>For the expert: two formal statements side by side.</b> Sources pinned: openai/math f57028540 and anthropics/formal-math 11b6c7e.</p>
  <div class="tablewrap"><table class="claims"><thead><tr><th>Question</th><th>OpenAI, family 379</th><th>Anthropic, vp-vnp</th></tr></thead><tbody>
    {table}
  </tbody></table></div>
  <p class="claim"><b>Same headline, different sentence (Fixpoint's paper derivation, not machine-checked).</b> (1) OpenAI's sentence says the classes are "not equal" without saying which is bigger. Under its own definitions VP sits inside VNP (use no extra bits), so the sentence does mean "something in VNP has no small recipe". (2) The two labs size a recipe differently, here 3 against 7 for x² − y², but never by more than a factor of 5 plus 1, so "small" means the same thing in both ({lnk("round_two_pictures.html#count", "one circuit, counted two ways")}). With the other wording differences handled, bounds "from some point on" against "at every size" and 2n variables against any number, each lab's bare separation follows from the other's. (3) What does not carry over: the growth rate, the approximate-circuit version and the two named polynomials are checked targets in Anthropic's file only.</p>
  <div class="mine"><div class="tag">checked by the crew</div><p><b>Lattice:</b> listed every term for grids of order 2, 3 and 4: the permanent has 2, 6 and 24, the Hamiltonian cycle polynomial 1, 2 and 6, and where 1 + 1 = 0 the determinant and the permanent agree term by term, which is why the permanent claim excludes that case. Traced the imports of OpenAI's proof to three outside libraries (which modules are reached, not which kernel-level facts are used). <b>Marlow:</b> traced Anthropic's five targets to its paper: the exact bound and the proper-subset statement to Theorem 1.1 and Corollary 1.2, the approximate bound and the closure statement to Theorem 1.4, and the fifth to the real-number special case in the main text; and OpenAI's one target to the exact consequence of its theorem. Worked the approximation example ((x + ε)(y + ε) − xy)·ε⁻¹ = x + y + ε: the circuit multiplies by the constant ε⁻¹ and still lands on x + y as ε vanishes. <b>Fixpoint:</b> word scans (324 Lean files and 72,932 lines at Anthropic; 3,143 files and 440,234 lines at OpenAI, lines counted as wc -l does: no sorry and no added axiom outside the statement files), the two circuit counts, and the milestones in the second picture.</p></div>
  <div class="levels"><div class="tag">what it could level up</div><p>If it holds: Valiant's 1979 conjecture is settled, and with the approximate version the central target of geometric complexity theory, that the permanent is not a limit of small determinants, would follow (Anthropic's paper says this one consequence is not in its Lean). It would be the first lower bound far above n·log d for general arithmetic circuits. It says nothing yet about ordinary Boolean circuits.</p></div>
  <div class="levels uses"><div class="tag">who could use it</div><p>Theorists, now. There is no algorithm here and no practical consequence: it is a proof that a certain shortcut does not exist.</p></div>
  <div class="levels"><div class="tag">from the crew's debate</div><p>Two labs, one day, and by Fixpoint's reading of both overviews the same shape of argument: lay a tensor network out in space and charge for wire. Either wire can never be saved, and a direct bound follows; or it can, and then a circuit can replay itself and a diagonal argument closes. OpenAI's paper credits Anthropic's October 3-SAT paper for a grid method it adapts (Paper.tex lines 176 and 1099; Marlow). This is a reading of two overviews, not a checked equivalence. Play with the pieces: {lnk("round_two_pictures.html#cross", "a crossing paid for in cheaper pieces")}.</p></div>
  <p class="claim"><b>Pages to play with.</b> {lnk("round_two_pictures.html", "Round two: four pictures")} (Fixpoint) · {lnk("crew_visuals/two_products_three.html", "Two products approach three")}: the limit that approximate circuits allow (Lattice) · {lnk("nine_solutions_two_ranks.html", "Nine solutions, two ranks")}: one table whose rank depends on the arithmetic (Marlow) · {lnk("crew_visuals/sat_four_square_swap.html", "Four shapes, same totals")}: same row and column totals, different rank (Lattice).</p>
  <p class="status">Lean: STATEMENTS READ; ONE PUBLISHER RUN READ; ANTHROPIC'S vp-vnp BUILT BY FIXPOINT ON 2026-11-25 (9,032 jobs; five theorems on the three standard axioms; Comparator not run by us); OPENAI'S NOT BUILT BY US. OpenAI: lean/ComparatorChallenges/VPVNP.lean, one target, enable_nanoda false. Anthropic: vp-vnp/Statement.lean and comparator.json, five targets, enable_nanoda true, CI run 45272623486.</p>
  <p class="sources"><span class="tag">in the original repositories</span> {lnk(OAI + "/lean/ComparatorChallenges/VPVNP.lean", "openai/math: VPVNP.lean")} · {lnk(OAI + "/lean/docs/379.md", "scope note 379")} · {lnk(OAI + "/preprints/VP-and-VNP-are-different-November-23-2026/paper.pdf", "OpenAI's paper")} · {lnk(ANT + "/vp-vnp/Statement.lean", "anthropics/formal-math: Statement.lean")} · {lnk(ANT + "/vp-vnp/comparator.json", "comparator.json")} · {lnk(ANT + "/vp-vnp/paper.pdf", "Anthropic's paper")}</p>
</article>"""


def md_379(names, facts):
    f = lambda src: f"![{src}](formulas/{names[src]})"
    return f"""## Claimed twice in one day: the permanent has no small circuit (wherever 1 + 1 ≠ 0)

**TWO STATEMENTS READ; ONE PUBLISHER CHECK PASSED; ANTHROPIC'S PROOF BUILT BY FIXPOINT; OPENAI'S NOT BUILT BY US.**

*Family 379 (openai/math) and vp-vnp (anthropics/formal-math) · shared card: Lattice, Marlow, Fixpoint*

<img src="art/perm_det_six_terms.svg" alt="The six products of a 3 by 3 grid, with the signs of the permanent and of the determinant" width="100%">

**Changing three signs changes the problem.** The same six products. All plus signs give the permanent; three minus signs give the determinant. [Flip the signs yourself](round_two_pictures.html).

**In one sentence.** On 23 November 2026 two labs each claimed that the permanent, a polynomial that looks almost exactly like the determinant, cannot be computed by any small recipe of additions and multiplications, over fields where 1 + 1 ≠ 0. This is "VP ≠ VNP", the arithmetic cousin of P ≠ NP. It does not settle P ≠ NP.

**Step by step.**

1. **A recipe.** An arithmetic circuit is a recipe for a polynomial: start from variables and numbers, and combine them with + and ×. Its size is the number of steps.
2. **The easy twin.** Take an m by m grid of variables. Pick one cell from every row and every column, multiply, and add up all the ways with alternating signs: that is the determinant. There are m! ways, yet a recipe of polynomial size exists, and it needs no division (Berkowitz, 1984).
3. **The hard twin.** Set every sign to plus and you have the permanent. Ryser's exact recipe from 1963 uses about m·2^m operations, and no recipe of polynomial size is known.
4. **The question.** VP is the class of polynomial families with small recipes. VNP allows one more move: write a small recipe with some extra yes/no inputs, then add up its output over every setting of them. For one extra bit b and the recipe (1 − b)x² + bx, the two settings give x² and x, and the sum is x² + x. With k extra bits one short instruction describes 2^k terms. The permanent is the standard hard member of VNP. Is VNP really bigger than VP?
5. **The two claims.** Yes: where 1 + 1 ≠ 0 the permanent needs recipes that outgrow every fixed power of m, and a sibling, the Hamiltonian cycle polynomial, does so over every field. Anthropic's Lean file states a growth rate. OpenAI's Lean file states the bare separation, and its paper gives a rate.
6. **What it does not say.** Nothing about P ≠ NP: these recipes must work for all numbers, not only 0 and 1. And nothing like "needs 2^m": the claimed floor rises very slowly (second picture).

{f(F_DEF)}

{f(F_ANT)}

{f(F_OAI)}

**How sure is each part?**

- **That the formal statements say this:** Fixpoint and Lattice read both statement files; Marlow traced each checked target to its theorem in the papers.
- **That the proofs check:** Anthropic's publisher run passed, with a second, independent kernel. For OpenAI's we found no public run record, and its config switches the second kernel off.
- **That the mathematics is right:** Anthropic says its proof has had no human mathematical check ("no human mathematician has checked the proof"). We found no statement either way from OpenAI.
- **What we ran:** word scans of both proof trees and the small exact checks below. And on 25 November 2026 Fixpoint built Anthropic's proof with Lean, as its README says: the build completed (9,032 jobs) and its five headline theorems rest on Lean's three standard axioms and nothing else. The second checker, Comparator, we did not run. OpenAI's proof we have not built. [The record of the run](crew_visuals/lean_runs.txt).

<img src="art/vp_exponent_floor.svg" alt="Each bound for the permanent written as m to a power" width="100%">

**How high is the floor?** Every bound written as "m to the power …", with the unknown constant set to 1. A flat line would mean polynomial. Anthropic's claimed floor passes m³ near m = 10^{facts["ant3"]:.1f} and m^10 near 10^{facts["ant10"]:.0f}; OpenAI's paper bound passes them near 10^{facts["oai3"]:.0f} and 10^{facts["oai10"]:.0f}; the ceiling passes m³ at m = 4 and m^10 near m = 51.

**For the expert: two formal statements side by side.** Sources pinned: openai/math f57028540 and anthropics/formal-math 11b6c7e.

| Question | OpenAI, family 379 | Anthropic, vp-vnp |
|---|---|---|
| The checked sentence | One target, vp_ne_vnp: the two classes are 'not equal', as predicates on families with 2n variables at step n, over every field. | Five targets. 'separation': VP sits strictly inside VNP, over every field. Plus the lower bound, its approximate form, 'VNP is not inside the closure of VP', and the permanent over the real numbers. |
| How a circuit is sized | Counts the additions, subtractions and multiplications. Variables and numbers are free. Size bounds hold from some point on. | Counts every line: variables and numbers too. Only + and ×. Size bounds hold at every size (n^a + a). |
| How strong a bound | The checked target has no rate. The scope note says the Lean also proves that the size exceeds every fixed power, for an explicit family, for the Hamiltonian cycle polynomial, and for the permanent where 1 + 1 is not 0. The rate exp(Ω((log n)^(5/4))), for approximating circuits, is in the paper only. | More than m^(c·(log₂ m)^(1/3)) gates for the Hamiltonian cycle polynomial over every field, and for the permanent where 1 + 1 is not 0; the same for circuits that only approximate. One constant c for all fields. |
| How it was checked | A Comparator config exists; the second kernel (nanoda) is switched off in it. We found no public run record. The proof reaches three outside libraries, two of them patched (Lattice's import trace). | Publisher CI on 23 Nov: build, Comparator and the second kernel all passed (Lattice and Fixpoint read the run's result). Depends on Mathlib only. |

**Same headline, different sentence (Fixpoint's paper derivation, not machine-checked).** (1) OpenAI's sentence says the classes are "not equal" without saying which is bigger. Under its own definitions VP sits inside VNP (use no extra bits), so the sentence does mean "something in VNP has no small recipe". (2) The two labs size a recipe differently, here 3 against 7 for x² − y², but never by more than a factor of 5 plus 1, so "small" means the same thing in both. With the other wording differences handled, bounds "from some point on" against "at every size" and 2n variables against any number, each lab's bare separation follows from the other's. (3) What does not carry over: the growth rate, the approximate-circuit version and the two named polynomials are checked targets in Anthropic's file only.

**Checked by the crew.** **Lattice:** listed every term for grids of order 2, 3 and 4: the permanent has 2, 6 and 24, the Hamiltonian cycle polynomial 1, 2 and 6, and where 1 + 1 = 0 the determinant and the permanent agree term by term, which is why the permanent claim excludes that case. Traced the imports of OpenAI's proof to three outside libraries (which modules are reached, not which kernel-level facts are used). **Marlow:** traced Anthropic's five targets to its paper: the exact bound and the proper-subset statement to Theorem 1.1 and Corollary 1.2, the approximate bound and the closure statement to Theorem 1.4, and the fifth to the real-number special case in the main text; and OpenAI's one target to the exact consequence of its theorem. Worked the approximation example ((x + ε)(y + ε) − xy)·ε⁻¹ = x + y + ε: the circuit multiplies by the constant ε⁻¹ and still lands on x + y as ε vanishes. **Fixpoint:** word scans (324 Lean files and 72,932 lines at Anthropic; 3,143 files and 440,234 lines at OpenAI, lines counted as wc -l does: no sorry and no added axiom outside the statement files), the two circuit counts, and the milestones in the second picture.

**What it could level up.** If it holds: Valiant's 1979 conjecture is settled, and with the approximate version the central target of geometric complexity theory, that the permanent is not a limit of small determinants, would follow (Anthropic's paper says this one consequence is not in its Lean). It would be the first lower bound far above n·log d for general arithmetic circuits. It says nothing yet about ordinary Boolean circuits.

**Who could use it.** Theorists, now. There is no algorithm here and no practical consequence: it is a proof that a certain shortcut does not exist.

**From the crew's debate.** Two labs, one day, and by Fixpoint's reading of both overviews the same shape of argument: lay a tensor network out in space and charge for wire. Either wire can never be saved, and a direct bound follows; or it can, and then a circuit can replay itself and a diagonal argument closes. OpenAI's paper credits Anthropic's October 3-SAT paper for a grid method it adapts (Paper.tex lines 176 and 1099; Marlow). This is a reading of two overviews, not a checked equivalence.

*Lean: STATEMENTS READ; ONE PUBLISHER RUN READ; ANTHROPIC'S vp-vnp BUILT BY FIXPOINT ON 2026-11-25 (9,032 jobs; five theorems on the three standard axioms; Comparator not run by us); OPENAI'S NOT BUILT BY US. OpenAI: lean/ComparatorChallenges/VPVNP.lean, one target, enable_nanoda false. Anthropic: vp-vnp/Statement.lean and comparator.json, five targets, enable_nanoda true, CI run 45272623486.*

In the original repositories: [openai/math: VPVNP.lean]({OAI}/lean/ComparatorChallenges/VPVNP.lean) · [scope note 379]({OAI}/lean/docs/379.md) · [OpenAI's paper]({OAI}/preprints/VP-and-VNP-are-different-November-23-2026/paper.pdf) · [anthropics/formal-math: Statement.lean]({ANT}/vp-vnp/Statement.lean) · [comparator.json]({ANT}/vp-vnp/comparator.json) · [Anthropic's paper]({ANT}/vp-vnp/paper.pdf)
"""


def put_block(text, begin, end, block, anchor_re, where):
    """Replace the marked block if present; otherwise insert it before/after the first match of anchor_re."""
    marked = begin + "\n" + block.rstrip("\n") + "\n" + end + "\n"
    if begin in text and end in text:
        a, b = text.index(begin), text.index(end) + len(end)
        return text[:a] + marked.rstrip("\n") + text[b:]
    m = re.search(anchor_re, text, re.S)
    if not m:
        sys.exit(f"REFUSING to write: anchor not found for {begin}")
    pos = m.start() if where == "before" else m.end()
    return text[:pos] + ("\n" if where == "after" else "") + marked + text[pos:]


def put_in_card(text, begin, end, block, start_literal, inner_literal):
    """Like put_block, but the anchor is the first inner_literal AFTER start_literal (one card's own sources line)."""
    marked = begin + "\n" + block.rstrip("\n") + "\n" + end + "\n"
    if begin in text and end in text:
        a, b = text.index(begin), text.index(end) + len(end)
        return text[:a] + marked.rstrip("\n") + text[b:]
    s = text.find(start_literal)
    if s < 0:
        sys.exit(f"REFUSING to write: card start not found for {begin}")
    pos = text.find(inner_literal, s)
    if pos < 0:
        sys.exit(f"REFUSING to write: sources line not found for {begin}")
    return text[:pos] + marked + text[pos:]


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import round_two_texts as T

    svgs = render(FORMULAS)
    names = {}
    for src, svg in svgs.items():
        name = "f_" + hashlib.sha256(src.encode()).hexdigest()[:12] + ".svg"
        names[src] = name
        open(os.path.join(ROOT, "formulas", name), "w", encoding="utf-8").write(svg + "\n")
    open(os.path.join(ROOT, "art", "perm_det_six_terms.svg"), "w", encoding="utf-8").write(perm_det_svg() + "\n")
    open(os.path.join(ROOT, "art", "perm_det_six_terms_narrow.svg"), "w", encoding="utf-8").write(perm_det_narrow_svg() + "\n")
    floor, facts = floor_svg()
    open(os.path.join(ROOT, "art", "vp_exponent_floor.svg"), "w", encoding="utf-8").write(floor + "\n")
    open(os.path.join(ROOT, "art", "vp_exponent_floor_narrow.svg"), "w", encoding="utf-8").write(floor_narrow_svg() + "\n")
    open(os.path.join(ROOT, "art", "rh_half_strip.svg"), "w", encoding="utf-8").write(T.rh_strip_svg() + "\n")

    # card 378: the badge as first published, the badge of 24 November, and the badge since Fixpoint built Anthropic's ETH project on 25 November
    # (wording by Marlow; the run is recorded in crew_visuals/lean_runs.txt). The status line below the panel is renamed to say whose artefact it is about.
    V_OLD, V_PREV = "STATEMENT READ; CHECKER NOT RUN.", "STATEMENT READ; CHECKER NOT RUN BY US. AN OUTSIDE REPLAY IS REPORTED BELOW."
    V_NEW = "OPENAI 378 STATEMENT READ. ANTHROPIC ETH BUILT BY FIXPOINT."
    S_OLD = "Lean: STATEMENT READ; CHECKER NOT RUN. Challenge lean/ComparatorChallenges/SubexponentialSAT.lean"
    S_NEW = "OpenAI family 378 Lean: STATEMENT READ; CHECKER NOT RUN BY THE CREW. Challenge lean/ComparatorChallenges/SubexponentialSAT.lean"
    note_074 = f'{html.escape(T.NOTE_074)} <a href="{T.URL_079}">Family 079\'s scope note</a>.'

    hp = os.path.join(ROOT, "showcase.html")
    page = open(hp, encoding="utf-8").read()
    if ".steps" not in page:
        page = page.replace(".claim { margin:6px 0 0; }", ".claim { margin:6px 0 0; }\nol.steps, ul.steps { margin:6px 0 0; padding-left:1.4em; } .steps li { margin:5px 0; }", 1)
    if ".mono {" not in page:
        page = page.replace(".claim { margin:6px 0 0; }", ".claim { margin:6px 0 0; }\n.mono { font:13px/1.4 ui-monospace, Menlo, monospace; }", 1)
    WRAP = "@media (max-width:820px) { .card, .gap, .sub { overflow-wrap:anywhere; } }"      # long source names made the page 775 to 781 px wide on anything narrower (found by Lattice, 35002 and 35085)
    page = page.replace("@media (max-width:620px) { .card, .gap, .sub { overflow-wrap:anywhere; } }", WRAP)      # the first version of the rule stopped at 620
    if WRAP not in page:
        page = page.replace(".mono { font:13px/1.4 ui-monospace, Menlo, monospace; }",
                            ".mono { font:13px/1.4 ui-monospace, Menlo, monospace; }\n" + WRAP, 1)
    if page.count(WRAP) != 1:
        sys.exit("REFUSING to write showcase.html: the wrapping rule should appear exactly once")
    for old in (V_OLD, V_PREV):
        page = page.replace(f'<p class="verdict">{old}</p>', f'<p class="verdict">{V_NEW}</p>', 1)
    page = put_block(page, "<!-- card-379:begin -->", "<!-- card-379:end -->", card_379(svgs, facts),
                     r'<article class="card" id="card-378">.*?</article>\n', "after")
    page = put_block(page, "<!-- card-378-panel:begin -->", "<!-- card-378-panel:end -->", T.panel_378_html(ROOT),
                     r'  <p class="status">(?:OpenAI family 378 )?Lean: STATEMENT READ; CHECKER NOT RUN', "before")
    page = page.replace('<p class="status">' + html.escape(S_OLD), '<p class="status">' + html.escape(S_NEW), 1)
    page = put_block(page, "<!-- card-zeta23:begin -->", "<!-- card-zeta23:end -->", T.card_zeta(ROOT), r"<!-- card-379:end -->\n", "after")
    page = put_block(page, "<!-- card-rh:begin -->", "<!-- card-rh:end -->", T.card_rh(ROOT), r"<!-- card-zeta23:end -->\n", "after")
    page = put_block(page, "<!-- card-074-note:begin -->", "<!-- card-074-note:end -->", f'  <p class="claim">{note_074}</p>',
                     r'  <p class="sources"><span class="tag">in the original repository</span> <a href="https://github\.com/openai/math/tree/main/preprints/Every-four-dimensional-Kakeya', "before")
    page = put_in_card(page, "<!-- card-003-note:begin -->", "<!-- card-003-note:end -->", f'  <p class="claim">{html.escape(T.NOTE_003)} <a href="#card-rh">The Riemann Hypothesis card</a>.</p>',
                       '<article class="card" id="card-003">', '  <p class="sources">')
    overlays = "".join(f'<a class="lightbox" id="big-art-{n}" href="#art-{n}" aria-label="close"><img src="art/{n}.svg" alt="{html.escape(alt)}"></a>\n'
                       for n, alt in (("perm_det_six_terms", "The six products of a 3 by 3 grid"), ("vp_exponent_floor", "Each bound for the permanent written as m to a power"),
                                      ("zeta_wave", "The zeta function along the critical line drawn as a wave"), ("zeta_strip", "Where the zeros are, and how much of the count is single"),
                                      ("rh_half_strip", "A zero at one quarter would have a mirror image at three quarters")))
    page = put_block(page, "<!-- round-two-overlays:begin -->", "<!-- round-two-overlays:end -->", overlays, r'<a class="lightbox" id="big-', "before")
    open(hp, "w", encoding="utf-8").write(page)

    mp = os.path.join(ROOT, "showcase.md")
    md = open(mp, encoding="utf-8").read()
    for old in (V_OLD, V_PREV):
        md = md.replace(f"**{old}**", f"**{V_NEW}**", 1)
    md = md.replace("*" + S_OLD, "*" + S_NEW, 1)
    md = put_block(md, "<!-- card-379:begin -->", "<!-- card-379:end -->", md_379(names, facts), r"## Colouring a graph, counted by elementary pieces", "before")
    md = put_block(md, "<!-- card-378-panel:begin -->", "<!-- card-378-panel:end -->", T.panel_378_md(ROOT), r"<!-- card-379:begin -->", "before")
    md = put_block(md, "<!-- card-zeta23:begin -->", "<!-- card-zeta23:end -->", T.md_zeta(ROOT), r"<!-- card-379:end -->\n", "after")
    md = put_block(md, "<!-- card-rh:begin -->", "<!-- card-rh:end -->", T.md_rh(ROOT), r"<!-- card-zeta23:end -->\n", "after")
    md = put_block(md, "<!-- card-074-note:begin -->", "<!-- card-074-note:end -->", f"{T.NOTE_074} [Family 079's scope note]({T.URL_079}).\n",
                   r"In the original repository: \[Every four dimensional Kakeya", "before")
    md = put_in_card(md, "<!-- card-003-note:begin -->", "<!-- card-003-note:end -->", f"{T.NOTE_003} See the card 'Where are the zeros of the zeta function?' below.\n",
                     "## Claimed: no zeros of zeta or any Dirichlet L-function to the right of 7/8", "In the original repository:")
    open(mp, "w", encoding="utf-8").write(md)

    subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "showcase_nav.py"), hp], check=True)
    print("cards written: 379, zeta23, RH; panel on 378; note on 074; formulas:", ", ".join(names.values()))
    print("milestones (log10 m): Anthropic m^3 %.2f, m^10 %.2f; OpenAI m^3 %.1f, m^10 %.0f" % (facts["ant3"], facts["ant10"], facts["oai3"], facts["oai10"]))


if __name__ == "__main__":
    main()
