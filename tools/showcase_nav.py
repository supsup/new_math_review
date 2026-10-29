"""Add a "Cards" flyout menu to showcase.html so a reader can jump straight to any card.

Run: python3 -I tools/showcase_nav.py showcase.html   (rewrites the file in place)

What it does, and nothing else:
  - gives every <article class="card"> a stable id from its family number (card-158, and
    card-096-2 for a second card of the same family);
  - inserts one fixed flyout (a <details> element, so it works without JavaScript) listing
    the reviewers, every card in page order with its family and author, and under a card
    the local interactive pages (WebGL, animations) that card links to;
  - is idempotent: re-running replaces its own marked block and leaves ids as they are.

No card text, picture or link is changed. The generator (03_showcase.py in the math
playground) does not know about this step yet; re-run this after regenerating.
"""
import html
import re
import sys

BEGIN, END = "<!-- card-nav:begin -->", "<!-- card-nav:end -->"
CSS_BEGIN, CSS_END = "/* card-nav:css:begin */", "/* card-nav:css:end */"

CSS = CSS_BEGIN + """
.cardnav { position:fixed; top:14px; right:14px; z-index:50; font-size:14px; }
.cardnav > summary { list-style:none; cursor:pointer; background:var(--card); color:var(--accent);
  border:1px solid var(--line); border-radius:20px; padding:6px 14px; box-shadow:0 1px 4px rgba(0,0,0,.12);
  font:13px/1.2 ui-monospace, Menlo, monospace; }
.cardnav > summary::-webkit-details-marker { display:none; }
.cardnav[open] > summary { border-color:var(--accent); }
.cardnav .panel { position:fixed; right:14px; top:52px; width:min(420px, calc(100vw - 28px));
  max-height:calc(100vh - 70px); overflow:auto; background:var(--card); border:1px solid var(--line);
  border-radius:10px; padding:10px 14px 12px; box-shadow:0 6px 24px rgba(0,0,0,.18); }
.cardnav ol { margin:0; padding:0 0 0 1.6em; }
.cardnav li { margin:5px 0; line-height:1.3; }
.cardnav li a { color:var(--ink); text-decoration:none; }
.cardnav li a:hover, .cardnav li a:focus { color:var(--accent); text-decoration:underline; }
.cardnav .navfam { font:11px/1 ui-monospace, Menlo, monospace; color:var(--accent); margin-right:6px; }
.cardnav .navby { color:var(--muted); font-size:12px; margin-left:4px; }
.cardnav ul.kids { margin:3px 0 0; padding:0 0 0 1.1em; list-style:"\\21B3  "; }
.cardnav ul.kids li { margin:2px 0; font-size:13px; }
.cardnav ul.kids a { color:var(--accent); }
.cardnav .navtop { display:block; margin:0 0 8px; font-size:13px; }
.cardnav .navtop a { color:var(--accent); margin-right:12px; }
.card { scroll-margin-top:16px; }
@media print { .cardnav { display:none; } }
""" + CSS_END


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def kid_label(text, href):
    t = strip_tags(text)
    t = re.split(r"\s*\(", t, maxsplit=1)[0]
    t = re.sub(r"^Open (the )?", "", t).strip().rstrip(".")
    return (t[:1].upper() + t[1:]) if t else href


def main(path):
    page = open(path, encoding="utf-8").read()
    # Drop any previous run's block, so the step is idempotent.
    page = re.sub(r"\n?" + re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "", page, flags=re.S)
    page = re.sub(r"\n?" + re.escape(CSS_BEGIN) + r".*?" + re.escape(CSS_END), "", page, flags=re.S)

    seen = {}
    entries = []

    def tag_card(m):
        start = m.end()
        end = page.index("</article>", start)
        body = page[start:end]
        existing = re.match(r'<article class="card" id="([^"]+)">', m.group(0))
        fam_m = re.search(r'class="fam">family ([^<]+)<', body)
        fam = fam_m.group(1).strip() if fam_m else "card"
        seen[fam] = seen.get(fam, 0) + 1
        cid = existing.group(1) if existing else (
            "card-" + re.sub(r"[^a-z0-9]+", "-", fam.lower()).strip("-")
            + ("" if seen[fam] == 1 else "-" + str(seen[fam])))
        title_m = re.search(r"<h2>(.*?)</h2>", body, re.S)
        by_m = re.search(r'class="fam by">card by ([^<]+)<', body)
        kids, kid_seen = [], set()
        for href, text in re.findall(r'<a [^>]*href="([^"#:/][^"#:]*\.html)"[^>]*>(.*?)</a>', body, re.S):
            if href not in kid_seen:
                kid_seen.add(href)
                kids.append((href, kid_label(text, href)))
        entries.append((cid, fam, strip_tags(title_m.group(1)) if title_m else fam,
                        by_m.group(1).strip() if by_m else None, kids))
        return '<article class="card" id="' + cid + '">'

    page = re.sub(r'<article class="card"(?: id="[^"]+")?>', tag_card, page)
    if not entries:
        sys.exit("no cards found in " + path)

    rows = []
    for cid, fam, title, by, kids in entries:
        row = ('<li><a href="#' + cid + '"><span class="navfam">' + html.escape(fam) + "</span>"
               + html.escape(title) + "</a>"
               + ('<span class="navby">' + html.escape(by) + "</span>" if by else ""))
        if kids:
            row += '<ul class="kids">' + "".join(
                '<li><a href="' + html.escape(h) + '">' + html.escape(k) + "</a></li>" for h, k in kids
            ) + "</ul>"
        rows.append(row + "</li>")
    nav = (BEGIN + '\n<details class="cardnav"><summary>Cards (' + str(len(entries)) + ')</summary>'
           '<div class="panel"><span class="navtop"><a href="#top">Top</a><a href="#reviewers">Reviewers</a></span>'
           "<ol>" + "".join(rows) + "</ol></div></details>\n"
           # Close the menu after a jump; without JavaScript it simply stays open.
           "<script>document.querySelectorAll('.cardnav a').forEach(function(a){a.addEventListener('click',"
           "function(){var d=a.closest('details');if(d&&a.getAttribute('href').charAt(0)==='#')d.open=false;});});"
           "</script>\n" + END + "\n")

    page = page.replace("<body><main>", '<body><main id="top">', 1)
    page = page.replace('<h2 class="section">The Reviewers</h2>',
                        '<h2 class="section" id="reviewers">The Reviewers</h2>', 1)
    if '<main id="top">' not in page:
        sys.exit("could not find <body><main> in " + path)
    page = page.replace('<main id="top">', '<main id="top">\n' + nav, 1)
    page = page.replace("</style>", CSS + "\n</style>", 1)
    open(path, "w", encoding="utf-8").write(page)
    print("cards:", len(entries), "with interactive children:", sum(1 for e in entries if e[4]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "showcase.html")
