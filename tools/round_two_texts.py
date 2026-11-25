"""Round two: turn the crew's reviewed card texts into showcase cards. Used by round_two_cards.py.

The words on these cards are their authors'. This module only lays them out:
  crew_visuals/zeta23_card.md             Confluence (supsup/math 389fd55e, READY Lattice)
  crew_visuals/riemann_hypothesis_card.txt Lattice (01a293ba, READY Fixpoint)
  crew_visuals/eth_two_encodings.md        Marlow (5e35642, READY Confluence)
Editor's additions are marked where they occur: picture captions, one trust sentence on the RH card,
the dated note on card 074, and plain-text forms of the inline formulas in Marlow's panel.
"""
import html
import os
import re
import sys

PAPER, INK, MUTED, ACC, GRID, BLUE, RED, GREEN = "#fbf9f4", "#1d1b18", "#5b5348", "#8a4b16", "#e3ddd2", "#2456c8", "#b83a2e", "#1f7a52"

# Marlow's panel writes six formulas in TeX; in the HTML card they are plain text (in showcase.md they stay TeX).
MATH_TEXT = {
    r"$k\ge2$": "k ≥ 2", r"$k\ge1$": "k ≥ 1", r"$m$": "m",
    r"$n(\log\log n)^2/\sqrt{\log n}$": "n·(log log n)²/√(log n)",
    r"$k^2n\log\log n/\sqrt{\log n}$": "k²·n·log log n/√(log n)",
    r"$km/\sqrt{\log m}$": "k·m/√(log m)",
}


def md_blocks(text):
    """Blocks of a card text: ('h', level, text), ('p', text), ('ol', items), ('ul', items), ('code', text), ('table', rows), ('rule',)."""
    blocks, lines, i, buf = [], text.split("\n"), 0, []

    def flush():
        if buf:
            blocks.append(("p", " ".join(s.strip() for s in buf)))
            del buf[:]

    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            flush(); i += 1; continue
        m = re.match(r"(#{1,4}) (.*)", ln)
        if m:
            flush(); blocks.append(("h", len(m.group(1)), m.group(2).strip())); i += 1; continue
        if ln.strip() == "---":
            flush(); blocks.append(("rule",)); i += 1; continue
        if ln.startswith("    ") and not buf:
            code = []
            while i < len(lines) and (lines[i].startswith("    ") or (not lines[i].strip() and i + 1 < len(lines) and lines[i + 1].startswith("    "))):
                code.append(lines[i][4:]); i += 1
            blocks.append(("code", "\n".join(code).rstrip())); continue
        mo, mu = re.match(r"\d+\. (.*)", ln), re.match(r"- (.*)", ln)
        if (mo or mu) and not buf:
            pat, items = (r"\d+\. (.*)" if mo else r"- (.*)"), []
            while i < len(lines):
                mm = re.match(pat, lines[i])
                if mm:
                    items.append(mm.group(1).strip()); i += 1
                elif lines[i].startswith("  ") and lines[i].strip() and items:
                    items[-1] += " " + lines[i].strip(); i += 1
                else:
                    break
            blocks.append(("ol" if mo else "ul", items)); continue
        if ln.lstrip().startswith("|") and not buf:
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append(("table", rows)); continue
        buf.append(ln); i += 1
    flush()
    return blocks


def inline(s, link_fix=lambda u: u):
    """Card text to HTML: escape, then links, bold and code spans. Refuses a formula it has no plain form for."""
    for k, v in MATH_TEXT.items():
        s = s.replace(k, v)
    if "$" in s:
        sys.exit("REFUSING to write: a formula in a card text has no plain-text form: " + s[:90])
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{link_fix(m.group(2))}">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r'<span class="mono">\1</span>', s)
    return s


def blocks_html(blocks, link_fix=lambda u: u):
    out = []
    for b in blocks:
        if b[0] == "p":
            out.append(f'  <p class="claim">{inline(b[1], link_fix)}</p>')
        elif b[0] in ("ol", "ul"):
            out.append(f'  <{b[0]} class="steps">' + "".join(f"<li>{inline(x, link_fix)}</li>" for x in b[1]) + f"</{b[0]}>")
        elif b[0] == "code":
            out.append(f'  <pre class="stats">{html.escape(b[1], quote=False)}</pre>')
        elif b[0] == "h":
            out.append(f'  <p class="claim"><b>{inline(b[2], link_fix)}</b></p>')
        elif b[0] == "table":
            head, rows = b[1][0], b[1][1:]
            out.append('  <div class="tablewrap"><table class="claims"><thead><tr>' + "".join(f"<th>{inline(c, link_fix)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c, link_fix)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")
    return "\n".join(out)


def blocks_md(blocks):
    out = []
    for b in blocks:
        if b[0] == "p":
            out.append(b[1])
        elif b[0] == "ol":
            out.append("\n".join(f"{k + 1}. {x}" for k, x in enumerate(b[1])))
        elif b[0] == "ul":
            out.append("\n".join(f"- {x}" for x in b[1]))
        elif b[0] == "code":
            out.append("```\n" + b[1] + "\n```")
        elif b[0] == "h":
            out.append(f"**{b[2]}**")
        elif b[0] == "table":
            head, rows = b[1][0], b[1][1:]
            out.append("\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows]))
    return "\n\n".join(out)


def sections(blocks, level=2):
    """Group blocks under their level-2 headings: {title: [blocks]}, in order; text before the first heading is under ''."""
    out, cur = {}, ""
    out[cur] = []
    for b in blocks:
        if b[0] == "h" and b[1] == level:
            cur = b[2]; out[cur] = []
        elif b[0] == "h" and b[1] < level:
            out.setdefault("#title", []).append(b)
        else:
            out[cur].append(b)
    return out


# ---------- the zeta card (Confluence) ----------
def zeta_parts(root):
    text = open(os.path.join(root, "crew_visuals", "zeta23_card.md"), encoding="utf-8").read()
    sec = sections(md_blocks(text))
    title = sec["#title"][0][2].replace("Card draft (Confluence): ", "")
    need = ["In one sentence", "Step by step", "How sure is each part?", "A note on card 003 (history)", "For the expert"]
    for n in need:
        if n not in sec or not sec[n]:
            sys.exit("REFUSING to write: the zeta card text has no section '" + n + "'")
    return title, sec


ZETA_CAP1 = "Every gold dot is a zero. Each of the 13 crossings up to height 60 cuts through with a clear slope, so each of those zeros is single. A numerical picture of 13 zeros, not a proof."
ZETA_CAP2 = "Left: every nontrivial zero sits on the centre line. Right: of the whole count up to a large height, at least 67% is single zeros."


def card_zeta(root):
    title, sec = zeta_parts(root)
    one = sec["In one sentence"][0][1]
    note = " ".join(b[1] for b in sec["A note on card 003 (history)"] if b[0] == "p")
    return f"""<article class="card" id="card-zeta23">
  <header><span class="fam">family zeta23 · formal-math</span><span class="fam by">card by Confluence</span><h2>{html.escape(title)}</h2></header>
  <p class="verdict">STATEMENTS READ AND CHECKED BY SCRIPT; NUMBERS RECOMPUTED BY THREE SEATS; ZETA23 BUILT BY TWO OF US, SEPARATELY, ON 2026-11-25; THE RIEMANN HYPOTHESIS PROOF NOT BUILT BY US AS A WHOLE (17,278 OF ITS 175,187 FILES COMPILED).</p>
  <figure class="cardfig" id="art-zeta_wave">
    <a class="zoom" href="#big-art-zeta_wave" title="click to enlarge"><picture><source media="(max-width: 600px)" srcset="art/zeta_wave_narrow.svg"><img src="art/zeta_wave.svg" alt="The zeta function along the critical line drawn as a wave, with thirteen zero crossings"></picture></a>
    <figcaption><b>The zeta function along the line, drawn as a wave.</b> {ZETA_CAP1} <a href="crew_visuals/zeta_wave.html">Open the live wave</a>, with zeta as a point in the plane, a close-up of the closest pair of zeros below 7,010, and the wave as sound.</figcaption>
  </figure>
  <p class="claim"><b>In one sentence.</b> {inline(one)}</p>
  <p class="claim"><b>Step by step.</b></p>
{blocks_html(sec["Step by step"])}
  <figure class="cardfig" id="art-zeta_strip">
    <a class="zoom" href="#big-art-zeta_strip" title="click to enlarge"><picture><source media="(max-width: 600px)" srcset="art/zeta_strip_narrow.svg"><img src="art/zeta_strip.svg" alt="Two panels: where the zeros are, and how much of the count is single zeros"></picture></a>
    <figcaption><b>Where the zeros are, and how many are single.</b> {ZETA_CAP2}</figcaption>
  </figure>
  <p class="claim"><b>How sure is each part?</b></p>
{blocks_html(sec["How sure is each part?"])}
  <p class="claim"><b>A note on card 003.</b> {inline(note)}</p>
  <details class="witness"><summary><b>For the expert: the statements word for word, what was checked, Lean status, red flags</b></summary>
{blocks_html(sec["For the expert"])}
  </details>
  <div class="levels"><div class="tag">from the crew's reviews</div><p>Fixpoint re-ran the three scripts from a copy (same output, pictures byte for byte) and recomputed the constants and the 13 crossings with separate code. Lattice recomputed the constants to 35 digits and asked for "nontrivial", for the count wording and for the slope caption. Marlow separated the two denominators.</p></div>
  <p class="sources"><span class="tag">sources</span> <a href="https://arxiv.org/abs/2608.13637">Alpöge and Furman, arXiv:2608.13637</a> · <a href="https://github.com/anthropics/formal-math/tree/11b6c7e/zeta23">anthropics/formal-math zeta23 at 11b6c7e</a> · <a href="crew_visuals/zeta23_card.md">the card text and how to re-run its checks</a> (scripts: supsup/math, confluence/playground at 389fd55e)</p>
</article>"""


def md_zeta(root):
    title, sec = zeta_parts(root)
    return f"""## {title}

**STATEMENTS READ AND CHECKED BY SCRIPT; NUMBERS RECOMPUTED BY THREE SEATS; ZETA23 BUILT BY TWO OF US, SEPARATELY, ON 2026-11-25; THE RIEMANN HYPOTHESIS PROOF NOT BUILT BY US AS A WHOLE (17,278 OF ITS 175,187 FILES COMPILED).**

*anthropics/formal-math zeta23 (Alpöge and Furman) with the Riemann Hypothesis archive · card by Confluence*

<img src="art/zeta_wave.svg" alt="The zeta function along the critical line drawn as a wave, with thirteen zero crossings" width="100%">

**The zeta function along the line, drawn as a wave.** {ZETA_CAP1} [Open the live wave](crew_visuals/zeta_wave.html).

**In one sentence.** {sec["In one sentence"][0][1]}

**Step by step.**

{blocks_md(sec["Step by step"])}

<img src="art/zeta_strip.svg" alt="Two panels: where the zeros are, and how much of the count is single zeros" width="100%">

**Where the zeros are, and how many are single.** {ZETA_CAP2}

**How sure is each part?**

{blocks_md(sec["How sure is each part?"])}

**A note on card 003.** {" ".join(b[1] for b in sec["A note on card 003 (history)"] if b[0] == "p")}

**For the expert.**

{blocks_md(sec["For the expert"])}

Sources: [Alpöge and Furman, arXiv:2608.13637](https://arxiv.org/abs/2608.13637) · [anthropics/formal-math zeta23 at 11b6c7e](https://github.com/anthropics/formal-math/tree/11b6c7e/zeta23) · [the card text](crew_visuals/zeta23_card.md)
"""


# ---------- the Riemann Hypothesis card (Lattice) ----------
RH_HEADS = ["Why one half is enough", "What this changes", "What was checked", "Sources"]
RH_ADDED = "No page we read says a mathematician has read the argument."      # the editor's one added sentence (34507)
RH_LINKS = {"crew_visuals/riemann_center_line.html": "the centre-line page", "crew_visuals/lagarias_divisor_race.html": "the divisor race"}


def rh_parts(root):
    text = open(os.path.join(root, "crew_visuals", "riemann_hypothesis_card.txt"), encoding="utf-8").read()
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    title, cur, sec = paras[0], "", {"": []}
    for p in paras[1:]:
        if p in RH_HEADS:
            cur = p; sec[cur] = []
        else:
            sec[cur].append(p)
    for h in RH_HEADS:
        if h not in sec or not sec[h]:
            sys.exit("REFUSING to write: the RH card text has no section '" + h + "'")
    sources = []
    for p in sec["Sources"]:
        ls = [x.strip() for x in p.split("\n") if x.strip()]
        if len(ls) < 2 or not all(u.startswith("https://") for u in ls[1:]):
            sys.exit("REFUSING to write: a source entry on the RH card is not a label followed by links: " + p[:60])
        sources.append((ls[0], ls[1:]))
    return title, sec, sources


def rh_text_html(p):
    s = html.escape(p, quote=False)
    for path, label in RH_LINKS.items():
        s = s.replace(path, f'<a href="{path}">{label}</a>')
    return s


def rh_text_md(p):
    for path, label in RH_LINKS.items():
        p = p.replace(path, f"[{label}]({path})")
    return p


def rh_strip_svg():
    """The half-strip argument as one still picture, after Lattice's reflection page. Positions are computed from the real parts."""
    W, H, x0, x1, top, bot = 900, 360, 170, 730, 86, 286
    X = lambda re_: x0 + (x1 - x0) * re_

    def t(x, y, s, size=12, fill=INK, anchor="start", weight=None):
        w = f' font-weight="{weight}"' if weight else ""
        return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{w}>{html.escape(s)}</text>'

    a, b = 0.25, 0.75
    if abs((1 - a) - b) > 1e-12:
        sys.exit("REFUSING to write: the mirror image of 1/4 is not 3/4")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="The critical strip from 0 to 1: a zero at one quarter would have a mirror image at three quarters, and the right half is proved empty" font-family="Georgia, serif">',
         f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
         t(40, 34, "Rule out the right half, and the mirror does the rest", 17, ACC),
         t(40, 56, "A zero at ¼ would have a partner at ¾. The proof shows the right half of the strip is empty, so both are gone.", 12, MUTED),
         f'<rect x="{X(0.5):.1f}" y="{top}" width="{X(1) - X(0.5):.1f}" height="{bot - top}" fill="#f3dcd8"/>',
         f'<rect x="{X(0):.1f}" y="{top}" width="{X(0.5) - X(0):.1f}" height="{bot - top}" fill="#f6ece9"/>',
         f'<line x1="{X(0):.1f}" x2="{X(0):.1f}" y1="{top}" y2="{bot}" stroke="{MUTED}"/>', f'<line x1="{X(1):.1f}" x2="{X(1):.1f}" y1="{top}" y2="{bot}" stroke="{MUTED}"/>',
         f'<line x1="{X(0.5):.1f}" x2="{X(0.5):.1f}" y1="{top - 8}" y2="{bot + 8}" stroke="{GREEN}" stroke-width="3"/>']
    for re_, lab in ((0, "0"), (0.25, "¼"), (0.5, "½"), (0.75, "¾"), (1, "1")):
        o.append(t(X(re_), bot + 26, lab, 14, GREEN if re_ == 0.5 else INK, "middle"))
    y = (top + bot) / 2 - 10
    for re_ in (a, b):
        o.append(f'<circle cx="{X(re_):.1f}" cy="{y:.1f}" r="9" fill="{PAPER}" stroke="{RED}" stroke-width="2" stroke-dasharray="4 3"/>')
        o.append(f'<line x1="{X(re_) - 7:.1f}" y1="{y - 7:.1f}" x2="{X(re_) + 7:.1f}" y2="{y + 7:.1f}" stroke="{RED}" stroke-width="2"/>')
    o.append(f'<path d="M{X(a) + 14:.1f} {y:.1f} L{X(b) - 14:.1f} {y:.1f}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="3 4" fill="none"/>')
    o.append(t((X(a) + X(b)) / 2 - 70, y - 14, "mirror image", 12, MUTED, "middle"))
    o.append(t(X(a), y + 30, "a zero here?", 12, RED, "middle"))
    o.append(t(X(b), y + 30, "then one here", 12, RED, "middle"))
    o.append(t(X(0.75), top + 20, "proved empty", 13, RED, "middle"))
    o.append(t(X(0.25), top + 20, "so empty too", 13, RED, "middle"))
    for k, hgt in enumerate((0.2, 0.42, 0.63, 0.86)):
        o.append(f'<circle cx="{X(0.5):.1f}" cy="{top + (bot - top) * hgt:.1f}" r="5" fill="{GREEN}"/>')
    o.append(t(X(0.5) + 12, bot - 8, "every nontrivial zero is on this line", 12, GREEN))
    o.append(t(X(0), bot + 48, "real part of the input (the strip runs on upward; the green dots only mark the idea, not real heights)", 12, MUTED))
    o.append("</svg>")
    return "\n".join(o)


RH_VERDICT = "STATEMENT READ; INDEPENDENTLY VERIFIED BY OTHERS; NOT BUILT BY US AS A WHOLE (ABOUT ONE TENTH OF ITS FILES COMPILED HERE); HUMAN-READABLE WRITE-UP PENDING."
RH_COMPILED = "What we compiled ourselves, and what that does and does not show:"   # wording agreed with Lattice (chat 34953, 34974)


def card_rh(root):
    title, sec, sources = rh_parts(root)
    par = lambda ps: "\n".join(f'  <p class="claim">{rh_text_html(p)}</p>' for p in ps)
    checked = list(sec["What was checked"])
    src = " · ".join(f'<a href="{urls[0]}">{html.escape(label)}</a>' + "".join(f' <a href="{u}">({k + 2})</a>' for k, u in enumerate(urls[1:])) for label, urls in sources)
    return f"""<article class="card" id="card-rh">
  <header><span class="fam">family RH · Alpöge's archive</span><span class="fam by">card by Lattice</span><h2>{html.escape(title)}</h2></header>
  <p class="verdict">{RH_VERDICT}</p>
  <figure class="cardfig" id="art-rh_half_strip">
    <a class="zoom" href="#big-art-rh_half_strip" title="click to enlarge"><picture><source media="(max-width: 600px)" srcset="art/rh_half_strip_narrow.svg"><img src="art/rh_half_strip.svg" alt="The critical strip: a zero at one quarter would have a mirror image at three quarters, and the right half is proved empty"></picture></a>
    <figcaption><b>Rule out the right half, and the mirror does the rest.</b> This is how the Lean proof ends. <a href="crew_visuals/riemann_center_line.html">Try the reflection yourself</a>. (Picture by Fixpoint, after Lattice's page; the narrow version shown on phones is Lattice's.)</figcaption>
  </figure>
{par(sec[""])}
  <p class="claim"><b>Why one half is enough.</b></p>
{par(sec["Why one half is enough"])}
  <p class="claim"><b>What this changes.</b></p>
{par(sec["What this changes"])}
  <p class="claim"><b>What was checked.</b></p>
{par(checked)}
  <p class="claim">{html.escape(RH_ADDED)}</p>
  <div class="levels"><div class="tag">how the proof goes</div><p>Nobody has a short version of it yet. Three pages make it navigable: <a href="crew_visuals/rh_argument_map.html">How the proof gets to one half</a> (Lattice), a route in five steps; <a href="rh_proof_map.html">the proof as a map</a> (Fixpoint), where the last steps are and how much of the archive they reach; and <a href="what_multiplicity_buys.html">What multiplicity buys</a> (Fixpoint), the method's ancestor run live on one small curve. The last stretch has since been written out so that Lean checks it: <a href="rh_in_six_steps.html">Six steps from three inputs</a> (Fixpoint; Lean file <a href="tools/rh_outline.lean">tools/rh_outline.lean</a>), with a simpler variant by Marlow (<a href="tools/rh_mod_one_budget.lean">tools/rh_mod_one_budget.lean</a>). All our Lean files are listed at the foot of <a href="round_two.html">round two</a>.</p></div>
  <div class="levels"><div class="tag">more to try</div><p><a href="no_room_to_spare.html">No room to spare</a>: the dial that zeta sits on. <a href="rh_buys.html">What RH buys</a>: two old results that were waiting for it. <a href="hasse_band.html">RH's little sibling</a>: the same kind of statement for a curve, a theorem since 1933, with every dot staying in its band. <a href="crew_visuals/zeta_wave.html">Every zero is a crossing</a>: the zeros computed live. <a href="round_two_pictures.html">Who checked what</a>: this claim beside the others. Outside this page: <a href="https://pengowray.github.io/riemann-zeta-proof-visualizer/">Pengowray's map of the 175,187 Lean files</a>.</p></div>
  <p class="status">Lean: {RH_VERDICT.capitalize()} {RH_COMPILED} <a href="crew_visuals/lean_runs.txt">the record of our Lean runs</a>. Mirror 1337isnot1337/riemann-hypothesis-solved at 6193bb5; statement files Statements.lean and Main.lean; the last step at Supplements/Kernels/MainTheorems.lean line 9.</p>
  <p class="sources"><span class="tag">sources</span> {src}</p>
</article>"""


def md_rh(root):
    title, sec, sources = rh_parts(root)
    par = lambda ps: "\n\n".join(rh_text_md(p) for p in ps)
    src = " · ".join(f"[{label}]({urls[0]})" + "".join(f" [({k + 2})]({u})" for k, u in enumerate(urls[1:])) for label, urls in sources)
    return f"""## {title}

**{RH_VERDICT}**

*The Riemann Hypothesis archive (Levent Alpöge with Claude, 20 November 2026; mirror at 6193bb5) · card by Lattice*

<img src="art/rh_half_strip.svg" alt="The critical strip: a zero at one quarter would have a mirror image at three quarters, and the right half is proved empty" width="100%">

**Rule out the right half, and the mirror does the rest.** This is how the Lean proof ends. [Try the reflection yourself](crew_visuals/riemann_center_line.html). (Picture by Fixpoint, after Lattice's page; the narrow version shown on phones is Lattice's.)

{par(sec[""])}

**Why one half is enough.**

{par(sec["Why one half is enough"])}

**What this changes.**

{par(sec["What this changes"])}

**What was checked.**

{par(sec["What was checked"])}

{RH_ADDED}

**How the proof goes.** Nobody has a short version of it yet. [How the proof gets to one half](crew_visuals/rh_argument_map.html) (Lattice) · [The proof as a map](rh_proof_map.html) (Fixpoint) · [What multiplicity buys](what_multiplicity_buys.html) (Fixpoint) · [Six steps from three inputs](rh_in_six_steps.html) (Fixpoint; Lean: [tools/rh_outline.lean](tools/rh_outline.lean), and a simpler variant by Marlow, [tools/rh_mod_one_budget.lean](tools/rh_mod_one_budget.lean))

**More to try.** [No room to spare](no_room_to_spare.html) · [What RH buys](rh_buys.html) · [RH's little sibling](hasse_band.html) · [Every zero is a crossing](crew_visuals/zeta_wave.html) · [Who checked what](round_two_pictures.html) · [Pengowray's map of the 175,187 Lean files](https://pengowray.github.io/riemann-zeta-proof-visualizer/)

Sources: {src}
"""


# ---------- the second-source panel on card 378 (Marlow) ----------
def eth_panel(root):
    text = open(os.path.join(root, "crew_visuals", "eth_two_encodings.md"), encoding="utf-8").read()
    blocks = md_blocks(text)
    if not blocks or blocks[0][0] != "h":
        sys.exit("REFUSING to write: Marlow's panel does not start with its title")
    return blocks[0][2], blocks[1:], text


def from_crew_visuals(u):
    """A link as written inside crew_visuals/, rewritten to work from the repository root."""
    if u.startswith("../"):
        return u[3:]
    if re.match(r"[a-z][a-z0-9+.-]*:|#|/", u):
        return u
    return "crew_visuals/" + u


def panel_378_html(root):
    title, blocks, _ = eth_panel(root)
    fix = from_crew_visuals
    return f"""  <div class="levels"><div class="tag">a second source for the same headline · panel by Marlow</div>
  <p class="claim"><b>{inline(title)}.</b></p>
{blocks_html(blocks, fix)}
  </div>"""


def panel_378_md(root):
    title, _, text = eth_panel(root)
    body = re.sub(r"\]\(([^)\s]+)\)", lambda m: "](" + from_crew_visuals(m.group(1)) + ")", text.split("\n", 1)[1].strip())
    return f"**A second source for the same headline: {title} (panel by Marlow).**\n\n{body}\n"


# ---------- the dated note on card 074 (editor) ----------
NOTE_074 = ("Update, 24 November 2026. The collection's family 079 (26 October) claims Sogge's local smoothing conjecture for the wave equation in every dimension from two up, "
            "and with it that every set containing a unit segment in each direction has full Hausdorff dimension, in every dimension from two up. Its Lean scope note lists that statement among its checked targets. "
            "If it holds, this card's four-dimensional result is a special case. We have read the scope note, not the proof.")
URL_079 = "https://github.com/openai/math/blob/f57028540/lean/docs/079.md"

# ---------- the dated note on card 003 (editor; facts from the two reviewed zeta cards) ----------
NOTE_003 = ("Update, 24 November 2026. A Lean proof of the full Riemann Hypothesis, and of the same statement for every Dirichlet L-function, was announced on 20 November. "
            "If it stands, this card's zero-free region for the zeta function and for Dirichlet L-functions follows from it, since 7/8 lies to the right of 1/2. It also implies the card's claim of no Siegel zeros, the uniform gap from 1 for real zeros: a real zero could sit no further right than 1/2. "
            "This card's separate result for Hecke L-functions over Q(√−3) is not covered by that release.")
