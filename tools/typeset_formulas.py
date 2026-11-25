#!/usr/bin/env python3
"""typeset_formulas.py [--check] PAGE.html [PAGE.html ...]

Typesets the formulas of a page with LatteX (https://github.com/supsup/LatteX), the way the cards are typeset.

A formula is an element that carries its own LaTeX source:

    <span class="tex" data-tex="e^{\\pi\\sqrt{163}}">e^(pi sqrt 163)</span>        set small, on the line of prose
    <div class="tex" data-tex="\\prod_{i<j}\\frac{a_i-a_j}{j-i}">...</div>          set full size, as a display

Whatever is inside the element is replaced by the picture LatteX draws for data-tex, sized in em so that it follows
the text, and coloured with the text's own colour, so it follows a dark page. The picture states its own display and
size, so a page rule that makes every svg a full-width block (as two of the pages have) does not catch it. An optional data-say gives the words a
screen reader should say; without it LatteX's own reading is used. Running the tool again changes nothing: the
picture is always made again from data-tex.

Needs Java and a LatteX jar: set LATTEX_JAR to its path. It REFUSES to write a page if LatteX reports an error for
any formula on it, or draws its missing-glyph box (a boxed question mark, which LatteX draws without any error for
a character none of its fonts has). With --check nothing is written; the exit code says whether every page is
already exactly what the tool would write."""
import html, os, re, subprocess, sys

JAR = os.environ.get("LATTEX_JAR", "")
EM = 40.0                                           # LatteX draws one em of text as 40 units
BOX = "M595 -169 L10 -169 L10 785 L595 785"         # how the outline of LatteX's missing-glyph box begins
PAT = re.compile(r'<(span|div) class="tex"((?: data-(?!tex=)[a-z]+="[^"]*")*) data-tex="([^"]*)">(.*?)</\1>', re.S)


def lattex(sources, inline):
    if not sources:
        return {}
    if not JAR or not os.path.exists(JAR):
        sys.exit("REFUSING: set LATTEX_JAR to a LatteX jar; the formulas are typeset by it")
    cmd = ["java", "-jar", JAR, "--batch"] + (["--inline"] if inline else [])
    proc = subprocess.run(cmd, input="\n".join(sources) + "\n", capture_output=True, text=True)
    recs = proc.stdout.split("\0")
    if recs and recs[-1].strip() == "":
        recs.pop()
    if len(recs) != len(sources):
        sys.exit(f"REFUSING: LatteX returned {len(recs)} records for {len(sources)} formulas: {proc.stderr[:300]}")
    out = {}
    for src, rec in zip(sources, recs):
        if "<svg" not in rec:
            sys.exit(f"REFUSING: LatteX could not set\n  {src}\n  {rec.strip()[:300]}")
        if BOX in rec:
            sys.exit(f"REFUSING: LatteX drew its missing-glyph box (a character it has no glyph for) in\n  {src}")
        out[src] = rec[rec.find("<svg"):].strip()
    return out


def fit(svg, display, say):
    m = re.match(r'<svg xmlns="http://www.w3.org/2000/svg" viewBox="(-?[\d.]+) (-?[\d.]+) ([\d.]+) ([\d.]+)" width="[\d.]+" height="[\d.]+" role="img" aria-label="([^"]*)">', svg)
    if not m:
        sys.exit("REFUSING: LatteX's output does not begin the way this tool expects: " + svg[:160])
    x, y, w, h = (float(m.group(i)) for i in range(1, 5))
    label = html.escape(say, quote=True) if say else m.group(5)
    if display:
        style = f"display:block;margin:0 auto;width:{w / EM:.3f}em;max-width:100%;height:auto"
    else:
        style = f"display:inline-block;width:{w / EM:.3f}em;height:{h / EM:.3f}em;vertical-align:{-(y + h) / EM:.3f}em"
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{m.group(1)} {m.group(2)} {m.group(3)} {m.group(4)}" style="{style}" role="img" aria-label="{label}">'
    body = re.sub(r">\s+<", "><", svg[m.end():].strip())
    return head + body


def typeset(text, name):
    found = list(PAT.finditer(text))
    need = {True: [], False: []}
    for m in found:
        src = html.unescape(m.group(3))
        if "\n" in src:
            sys.exit(f"REFUSING: {name}: a formula's source runs over a line break: {src[:80]!r}")
        if src not in need[m.group(1) == "div"]:
            need[m.group(1) == "div"].append(src)
    drawn = {True: lattex(need[True], inline=False), False: lattex(need[False], inline=True)}

    def put(m):
        display = m.group(1) == "div"
        say = re.search(r' data-say="([^"]*)"', m.group(2))
        pic = fit(drawn[display][html.unescape(m.group(3))], display, html.unescape(say.group(1)) if say else "")
        return f'<{m.group(1)} class="tex"{m.group(2)} data-tex="{m.group(3)}">{pic}</{m.group(1)}>'
    return PAT.sub(put, text), len(found), len(need[True]) + len(need[False])


def main():
    args = sys.argv[1:]
    check = "--check" in args
    pages = [a for a in args if a != "--check"]
    if not pages:
        sys.exit(__doc__)
    stale = 0
    for page in pages:
        old = open(page, encoding="utf-8").read()
        new, n, distinct = typeset(old, page)
        left = len(re.findall(r'class="tex"', new)) - n
        if left:
            sys.exit(f'REFUSING: {page}: {left} element(s) with class="tex" are not in the form this tool reads (class first, data-tex last)')
        if check:
            stale += new != old
            print(f"{page}: {n} formulas, {distinct} distinct; {'up to date' if new == old else 'WOULD CHANGE'}")
        else:
            if new != old:
                open(page, "w", encoding="utf-8").write(new)
            print(f"{page}: {n} formulas typeset, {distinct} distinct; {'written' if new != old else 'unchanged'}")
    sys.exit(1 if stale else 0)


if __name__ == "__main__":
    main()
