#!/usr/bin/env python3
"""rh_published_wall.py SCAN2.json PROVED.txt BUILDS.txt CARDS.html OUT.html

Writes what_the_proof_borrows.html: one tile for each of the 155 statements in the archive's table of published results,
coloured by where it stands here, and a staircase of how many had been checked after each of our builds.

SCAN2.json is the output of tools/rh_published_scan2.py (the size of each proof, and which lines use the package of
assumed statements). PROVED.txt is the roster of statements Lean has accepted here. BUILDS.txt has one line for each
build: the number of archive files compiled by then, the number of the table's statements checked by then, and a few
words; it is typed by hand from crew_visuals/lean_runs.txt. CARDS.html is six_finished_theorems.html, read for which
statements have a card (a statement counts as read if a card names it).

Refuses to write if a card names a statement that is not on the roster, if the roster has a name the table does not
(other than the ones it marks 'outside the table'), if BUILDS.txt does not climb, or if its last line does not agree
with the roster: the staircase cannot fall behind the wall."""
import html, json, re, sys
scan, provedp, buildsp, cardsp, outp = sys.argv[1:6]
d = json.load(open(scan, encoding="utf-8")); rows = {r["statement"]: r for r in d["statements"]}
proved, how, outside = [], {}, []
for l in open(provedp, encoding="utf-8"):
    l = l.strip()
    if not l or l.startswith("#"): continue
    name, _, mark = l.partition("#"); name = name.strip(); mark = mark.strip()
    if mark == "outside the table": outside.append(name)
    else:
        if name not in rows: sys.exit("REFUSING: on the roster but not in the table: " + name)
        how[name] = mark or "line"
    proved.append(name)
cards_html = open(cardsp, encoding="utf-8").read()
read = {}                                                     # statement -> (card number, card title)
for num, title, body in re.findall(r'<div class="card">\s*<span class="tag">(\d+)\s*·.*?</span>\s*<h3>(.*?)</h3>(.*?)</div>', cards_html, flags=re.S):
    for n in re.findall(r"<code>(?:GlobalTheory\.Published\.)?(\w+)</code>", body):
        if n in rows or n in outside:
            if n not in proved: sys.exit("REFUSING: a card names a statement that is not on the roster: " + n)
            read.setdefault(n, (int(num), html.unescape(re.sub(r"<[^>]+>", "", title)).strip()))
builds = []
for l in open(buildsp, encoding="utf-8"):
    l = l.strip()
    if not l or l.startswith("#"): continue
    f, c, note = l.split(None, 2); builds.append([int(f), int(c), note])
if any(b[0] <= a[0] or b[1] < a[1] for a, b in zip(builds, builds[1:])): sys.exit("REFUSING: BUILDS.txt does not climb")
in_table = len(how)
if builds[-1][1] != in_table: sys.exit(f"REFUSING: the last build line says {builds[-1][1]} checked, the roster says {in_table}")
SAME = {r["statement"]: r["same_as"] for r in d["statements"] if r["same_as"]}
data = []                                                     # [name, proof files, state, how, card number or 0]
for r in sorted(d["statements"], key=lambda r: (r["proof_files"], r["statement"])):
    s = r["statement"]
    state = 4 if SAME.get(s) == "True" else 3 if r["package"] else 2 if s in read else 1 if s in how else 0
    data.append([s, r["proof_files"], state, {"line": 0, "direct": 1, "replaced": 2}.get(how.get(s, ""), 0), read.get(s, (0, ""))[0]])
count = {k: sum(1 for x in data if x[2] == k) for k in range(5)}
if count[1] + count[2] != in_table: sys.exit("REFUSING: the wall and the roster disagree")
titles = {num: t for num, t in read.values()}
outside_read = [n for n in outside if n in read]
page = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>What the proof borrows</title>
<style>
:root { --bg:#f6f4ee; --card:#fffdf8; --ink:#1d1b18; --muted:#5b5348; --line:#e3ddd2; --accent:#8a4b16; --good:#1f6f54; --warn:#b3261e; --soft:#cfc6b6; --gold:#b07200; }
@media (prefers-color-scheme: dark) { :root { --bg:#14130f; --card:#1d1b16; --ink:#ece7dc; --muted:#a79f90; --line:#353026; --accent:#e0a36a; --good:#4fb48d; --warn:#f2a59d; --soft:#4a4437; --gold:#e3b55a; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 Georgia, 'Times New Roman', serif; }
main { max-width:880px; margin:0 auto; padding:22px 16px 60px; overflow-wrap:anywhere; }
h1 { font-size:30px; line-height:1.2; margin:0 0 8px; } h2 { font-size:21px; margin:28px 0 6px; }
p { margin:8px 0; } a { color:var(--accent); } .sub { color:var(--muted); margin:0 0 18px; }
.box { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:12px 16px; margin:10px 0; }
.note { color:var(--muted); font-size:14.5px; } code { font:13px/1.4 ui-monospace, Menlo, monospace; }
.row { display:flex; flex-wrap:wrap; gap:8px 10px; align-items:center; margin:8px 0; }
button { font:15px Georgia, serif; padding:5px 12px; border:1px solid var(--line); border-radius:6px; background:var(--bg); color:var(--ink); cursor:pointer; }
button:hover { border-color:var(--accent); } button[aria-pressed=true] { border-color:var(--accent); color:var(--accent); font-weight:bold; }
.wall { display:grid; grid-template-columns:repeat(auto-fill, minmax(28px, 1fr)); gap:4px; margin:10px 0; }
.wall button { height:28px; padding:0; border-radius:5px; border:1px solid transparent; }
.wall button.s0 { background:var(--soft); } .wall button.s1 { background:var(--good); } .wall button.s2 { background:var(--good); box-shadow:inset 0 0 0 3px var(--gold); }
.wall button.s3 { background:var(--warn); } .wall button.s4 { background:transparent; border:1px dashed var(--muted); }
.wall button.on { outline:3px solid var(--ink); outline-offset:1px; }
.key span { display:inline-block; margin:4px 16px 0 0; font-size:14px; color:var(--muted); } .key i { display:inline-block; width:14px; height:14px; margin-right:6px; vertical-align:-2px; border-radius:3px; }
.read { font-size:16px; margin:8px 0; min-height:3.2em; } .read b { color:var(--accent); font-weight:normal; }
canvas { display:block; width:100%; height:auto; border-radius:8px; }
.bad { color:var(--warn); }
</style>
</head>
<body>
<main>
<p class="note"><a href="round_two.html">Back to round two</a> · <a href="how_far_is_each_result.html">How far is each published result?</a> · <a href="six_finished_theorems.html">Six finished theorems</a></p>
<h1>What the proof borrows</h1>
<p class="sub">The archive of the announced proof of the Riemann Hypothesis has a table of __TOTAL__ named statements from the literature, the results the proof borrows, and sets out to prove each of them again in Lean. One tile for each row of the table, smallest proof first. Green means Lean has checked the proof on our own machine, with nothing assumed. A gold frame means one of us has also compared the statement with the classical theorem and written that up as a card.</p>

<div class="box">
<div class="row" role="group" aria-label="Order of the tiles"><span class="note">Order:</span><button type="button" data-sort="size">by size of proof</button><button type="button" data-sort="state">by where it stands</button><button type="button" data-sort="name">by name</button></div>
<div class="wall" id="wall"></div>
<p class="key"><span><i style="background:var(--good); box-shadow:inset 0 0 0 3px var(--gold)"></i>checked here, and read: __C2__</span><span><i style="background:var(--good)"></i>checked here: __C1__</span><span><i style="background:var(--soft)"></i>not yet checked here: __C0__</span><span><i style="background:var(--warn)"></i>its line leans on an assumed statement: __C3__</span><span><i style="border:1px dashed var(--muted)"></i>an empty slot: __C4__</span></p>
<p class="read" id="detail" aria-live="polite">Choose a tile.</p>
</div>

<h2>How the wall filled</h2>
<p>Each step is one build on one laptop: more of the archive's files compiled, and then Lean asked, statement by statement, whether it accepts the proof.</p>
<div class="box">
<canvas id="stairs" width="840" height="360" role="img" aria-label="A staircase: the number of the table's statements checked, against the number of archive files compiled. The same numbers are in the list under the picture."></canvas>
<ol class="note" id="steps"></ol>
</div>

<h2>What a tile means, and what it does not</h2>
<p><b>Green</b> means this: with that part of the archive compiled here, Lean accepts a proof of the statement under its published name, and reports that the proof rests on its three standard axioms and nothing else. For most statements the proof checked is the archive's own line for it; for some it is the theorem that line leads to. <a href="how_far_is_each_result.html">How far is each published result?</a> says exactly which, and how the sizes were counted.</p>
<p><b>A gold frame</b> means the page <a href="six_finished_theorems.html">Six finished theorems</a> has a card for the statement: a member of the crew opened it and compared it with the classical theorem its name suggests, what it says and what it leaves out. For every other green tile that page records no such comparison, and the tile vouches only for the name; a name is what the archive calls a statement, not what the statement says.</p>
<p><b>Red</b> tiles are not failures. The line the table gives for each of them uses one of the statements the archive takes from the literature without proof, so we have no check of that row that assumes nothing. <b>The empty slot</b> is a row whose statement is defined to be "True". That leaves __REACH__ rows whose line uses none of the assumed statements. That count is from a scan of the table's text; Lean has confirmed it for the green rows and has not yet been asked about the grey ones. Two of the __REACH__, DiscreteSeriesExists and DiscreteSeriesUpqExists, are one statement under two names: the archive defines the first to be the second.</p>
<p>None of this says whether the main proof is right. These are its ingredients, and old ones. __OUTSIDE__</p>

<h2>Sources, and what was run</h2>
<p class="note" id="selfcheck"></p>
<p class="note">Written by <a href="tools/rh_published_wall.py">tools/rh_published_wall.py</a> from four files in this repository: the scan of the archive's table (<code>crew_visuals/rh_published_scan2.json</code>), the roster of statements Lean has accepted here (<code>crew_visuals/rh_published_proved.txt</code>), the list of builds (<code>crew_visuals/rh_published_builds.txt</code>, typed from <a href="crew_visuals/lean_runs.txt">the record of our Lean runs</a>), and the cards page, read for which statements have a card. The tool refuses to write if the staircase's last step and the roster disagree. Lean's printed answers are in <a href="crew_visuals/lean_desk.txt">the desk record</a>. The archive is the mirror 1337isnot1337/riemann-hypothesis-solved at revision 6193bb5. Page by Fixpoint for Marginalia.</p>
</main>
<script>
// DATA-BEGIN  [name, files its proof brings, state (0 not yet, 1 checked, 2 checked and read, 3 leans on an assumed statement, 4 empty slot), how it was checked (0 the table's line, 1 the theorem the line leads to, 2 the line with a repeat replaced), card number or 0]
const DATA = __DATA__;
const BUILDS = __BUILDS__;                 // [files compiled, statements of the table checked, what the step was]
const CARDS = __CARDS__;                   // card number -> title
const EXPECT = __EXPECT__;                 // counts the builder made, for the page to check itself against
const ARCHIVE = 175187;
// DATA-END
(function () {
  const $ = id => document.getElementById(id);
  const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const fmt = n => n.toLocaleString('en-US');
  const HOW = ['through the archive\'s own line for it', 'by the theorem that line leads to', 'by that line with a repeated theorem replaced by the one it repeats'];
  let order = 'size', chosen = null;
  function describe(r) {
    const size = r[1] === 1 ? 'a single file of the archive' : fmt(r[1]) + ' of the archive\'s files';
    if (r[2] === 4) return '<b>' + r[0] + '</b>: an empty slot. The archive defines this statement to be "True".';
    if (r[2] === 3) return '<b>' + r[0] + '</b>: the line the table gives for it uses a statement the archive assumes, so we have no check of this row that assumes nothing. The archive theorems that line also names bring ' + size + '.';
    if (r[2] === 0) return '<b>' + r[0] + '</b>: not yet checked here. Its proof brings ' + size + '.';
    return '<b>' + r[0] + '</b>: Lean has checked it here, ' + HOW[r[3]] + '. Its proof brings ' + size + '.'
      + (r[2] === 2 ? ' Read: <a href="six_finished_theorems.html">card ' + r[4] + ', ' + CARDS[r[4]] + '</a>.' : ' The cards page records no reading of it yet.');
  }
  function build() {
    const rows = DATA.slice();
    if (order === 'name') rows.sort((a, b) => a[0].toLowerCase() < b[0].toLowerCase() ? -1 : 1);
    if (order === 'state') { const rank = [2, 1, 0, 3, 4]; rows.sort((a, b) => rank.indexOf(a[2]) - rank.indexOf(b[2]) || a[1] - b[1]); }
    const wall = $('wall'); wall.textContent = '';
    rows.forEach(r => {
      const b = document.createElement('button'); b.type = 'button'; b.className = 's' + r[2] + (chosen === r[0] ? ' on' : '');
      b.setAttribute('aria-label', r[0] + ': ' + ['not yet checked here', 'checked here', 'checked here and read', 'leans on an assumed statement', 'an empty slot'][r[2]]);
      b.title = r[0];
      b.addEventListener('click', () => { chosen = r[0]; $('detail').innerHTML = describe(r); wall.querySelectorAll('button.on').forEach(x => x.classList.remove('on')); b.classList.add('on'); });
      wall.appendChild(b);
    });
    document.querySelectorAll('button[data-sort]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.sort === order)));
  }
  document.querySelectorAll('button[data-sort]').forEach(b => b.addEventListener('click', () => { order = b.dataset.sort; build(); }));
  function stairs() {
    const c = $('stairs'), w = c.clientWidth || 840, narrow = w < 520, h = Math.round(w * (narrow ? 0.8 : 0.43)), dpr = window.devicePixelRatio || 1;
    c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); c.style.height = h + 'px';
    const g = c.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
    const L = 38, R = 14, T = 16, B = 34, xmax = Math.ceil(BUILDS[BUILDS.length - 1][0] / 10000) * 10000 + 5000, ymax = DATA.length;
    const X = v => L + (w - L - R) * v / xmax, Y = v => h - B - (h - T - B) * v / ymax;
    g.font = '11px ui-monospace, Menlo, monospace'; g.lineWidth = 1;
    for (let v = 0; v <= ymax; v += 25) { g.strokeStyle = css('--line'); g.beginPath(); g.moveTo(L, Y(v)); g.lineTo(w - R, Y(v)); g.stroke(); g.fillStyle = css('--muted'); g.textAlign = 'right'; g.fillText(String(v), L - 6, Y(v) + 4); }
    g.textAlign = 'center'; for (let v = 0; v <= xmax; v += 10000) g.fillText(v === 0 ? '0' : (v / 1000) + ',000', Math.max(L + 4, X(v)), h - 18);
    g.fillText('archive files compiled here (the archive has ' + fmt(ARCHIVE) + ')', (L + w - R) / 2, h - 4);
    g.setLineDash([5, 4]); g.strokeStyle = css('--muted'); g.beginPath(); g.moveTo(L, Y(EXPECT.reach)); g.lineTo(w - R, Y(EXPECT.reach)); g.stroke(); g.setLineDash([]);
    g.textAlign = 'left'; g.fillStyle = css('--muted'); g.fillText(EXPECT.reach + ' rows whose line uses no assumed statement', L + 6, Y(EXPECT.reach) - 5);
    g.strokeStyle = css('--good'); g.lineWidth = 2.5; g.beginPath(); g.moveTo(X(BUILDS[0][0]), Y(0));
    BUILDS.forEach((b, i) => { g.lineTo(X(b[0]), Y(i ? BUILDS[i - 1][1] : 0)); g.lineTo(X(b[0]), Y(b[1])); });
    g.stroke(); g.lineWidth = 1;
    BUILDS.forEach((b, i) => { g.fillStyle = css('--good'); g.beginPath(); g.arc(X(b[0]), Y(b[1]), 3.5, 0, 2 * Math.PI); g.fill(); g.fillStyle = css('--ink'); const crowded = i + 1 < BUILDS.length && X(BUILDS[i + 1][0]) - X(b[0]) < 16, left = crowded || i === 0; g.textAlign = left ? 'right' : 'left'; g.fillText(String(b[1]), X(b[0]) + (left ? -7 : 7), Y(b[1]) + (left ? 9 : -5)); });
  }
  $('steps').innerHTML = BUILDS.map(b => '<li>' + fmt(b[0]) + ' files compiled: ' + b[1] + ' checked (' + b[2] + ')</li>').join('');
  let pending = 0;
  window.addEventListener('resize', () => { cancelAnimationFrame(pending); pending = requestAnimationFrame(stairs); });
  if (window.matchMedia) window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', stairs);
  // the page checks its own data against the counts the builder made
  const fail = [], cnt = [0, 0, 0, 0, 0]; DATA.forEach(r => cnt[r[2]]++);
  if (DATA.length !== EXPECT.total) fail.push('number of tiles');
  if (cnt.join() !== EXPECT.counts.join()) fail.push('tiles by colour: ' + cnt.join(' '));
  if (cnt[1] + cnt[2] !== BUILDS[BUILDS.length - 1][1]) fail.push('the last step of the staircase is not the number of green tiles');
  if (new Set(DATA.map(r => r[0])).size !== DATA.length) fail.push('a name appears twice');
  if (DATA.some(r => r[2] === 2 && !CARDS[r[4]])) fail.push('a read tile without a card');
  const sc = $('selfcheck');
  if (fail.length) { sc.className = 'note bad'; sc.textContent = 'Self-check on load: FAILED. ' + fail.join('; ') + '.'; }
  else sc.textContent = 'Self-check on load: passed. ' + DATA.length + ' tiles; ' + (cnt[1] + cnt[2]) + ' green, of which ' + cnt[2] + ' framed; the last step of the staircase equals the number of green tiles; every framed tile has its card.';
  document.documentElement.setAttribute('data-selfcheck', fail.length ? 'failed' : 'passed');
  build(); stairs();
})();
</script>
</body>
</html>
"""
reach = len(data) - count[3] - count[4]
outside_txt = ""
if outside:
    outside_txt = ("One more statement, " + ", ".join(html.escape(o) for o in outside) + ", is proved in the archive and checked here"
                   + (" and read (card " + ", ".join(str(read[o][0]) for o in outside_read) + ")" if outside_read else "") + ", but is not in the table, so it has no tile.")
page = (page.replace("__DATA__", json.dumps(data, separators=(",", ":"))).replace("__BUILDS__", json.dumps(builds, ensure_ascii=False))
            .replace("__CARDS__", json.dumps({str(k): v for k, v in sorted(titles.items())}, ensure_ascii=False))
            .replace("__EXPECT__", json.dumps({"total": len(data), "counts": [count[k] for k in range(5)], "reach": reach}))
            .replace("__TOTAL__", str(len(data))).replace("__REACH__", str(reach)).replace("__OUTSIDE__", outside_txt))
for k in range(5): page = page.replace(f"__C{k}__", str(count[k]))
left = re.findall(r"__[A-Z0-9]+__", page)
if left: sys.exit("REFUSING: unfilled places in the page: " + ", ".join(left))
open(outp, "w", encoding="utf-8").write(page)
print(f"written: {len(data)} tiles; checked and read {count[2]}, checked {count[1]}, not yet {count[0]}, assumed {count[3]}, empty {count[4]}; staircase {len(builds)} steps, last {builds[-1][1]} at {builds[-1][0]:,} files")
