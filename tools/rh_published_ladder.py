#!/usr/bin/env python3
"""rh_published_ladder.py SCAN2.json PROVED.txt OUT.html

Writes the page 'How far is each published result?': one bar for each statement in the archive's table of published results,
as tall as the number of archive files that the file holding its proof brings with it, marked if Lean has checked it
in our build, and marked differently if its line uses the package of statements the archive assumes.
SCAN2.json is the output of tools/rh_published_scan2.py. PROVED.txt lists, one per
line, the statements Lean has accepted here (the replies are in crew_visuals/lean_desk.txt); a statement that is not in the table
must say so on its line ('Name  # outside the table'); one checked by the theorem its line leads to, not through
the line itself, says 'Name  # direct'; and one checked by its line with a repeated theorem replaced inside it says
'Name  # replaced'. Its first comment line is the sentence about our builds, and its
second, if there is one, a remark about the names; both are typed by hand from crew_visuals/lean_runs.txt and are not checked here.
Refuses to write if a proved name is unknown, is listed twice, or is one whose line uses the package, or if a statement other
than the placeholder has no proof placed."""
import html, json, sys
scan, provedp, outp = sys.argv[1:4]
d = json.load(open(scan, encoding="utf-8"))
notes, proved, outside, direct, replaced = [], [], [], [], []
for l in open(provedp, encoding="utf-8"):
    l = l.strip()
    if not l: continue
    if l.startswith("#"): notes.append(l.lstrip("# ").strip()); continue
    name, _, mark = l.partition("#")
    name = name.strip()
    if mark.strip() == "outside the table": outside.append(name)
    elif mark.strip() == "direct": direct.append(name)
    elif mark.strip() == "replaced": replaced.append(name)
    elif mark.strip(): sys.exit("REFUSING: unknown mark on a line of PROVED: " + l)
    proved.append(name)
if len(set(proved)) != len(proved): sys.exit("REFUSING: a name is listed twice in PROVED")
package = {r["statement"] for r in d["statements"] if r["package"]}
rows = [r for r in d["statements"] if r["proof_modules"]]
left_out = sorted(r["statement"] for r in d["statements"] if not r["proof_modules"])
bad = [r["statement"] for r in rows if r["unfollowed"] and not r["package"]]
if bad: sys.exit("REFUSING: a line names a theorem the scan could not place: " + ", ".join(bad))
names = {r["statement"] for r in rows}
for p in proved:
    if p in outside and p in {r["statement"] for r in d["statements"]}: sys.exit("REFUSING: marked outside the table but the table has it: " + p)
    if p not in outside and p not in names: sys.exit("REFUSING: a proved name is not a statement of the table: " + p)
    if p in package: sys.exit("REFUSING: listed as proved, but its line uses the package: " + p)
if left_out != ["UnusedSlot72"]: sys.exit("REFUSING: the statements left out of the picture are not just the placeholder: " + ", ".join(left_out))
rows.sort(key=lambda r: (r["proof_files"], r["statement"]))
data = [[r["statement"], r["proof_files"], r["table_files"], 2 if r["statement"] in package else 1 if r["statement"] in proved else 0] for r in rows]
n_proved = sum(1 for x in data if x[3] == 1); n_pack = sum(1 for x in data if x[3] == 2)
n_alias = sum(1 for r in rows if r["proof_files"] < r["table_files"]); n_big = sum(1 for r in rows if r["table_files"] - r["proof_files"] > 100)
total = len(d["statements"])
page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>How far is each published result</title>
<style>
:root { --bg:#f6f4ee; --card:#fffdf8; --ink:#1d1b18; --muted:#5b5348; --line:#e3ddd2; --accent:#8a4b16; --good:#1f6f54; --soft:#cfc6b6; --warn:#b3261e; }
@media (prefers-color-scheme: dark) { :root { --bg:#14130f; --card:#1d1b16; --ink:#ece7dc; --muted:#a79f90; --line:#353026; --accent:#e0a36a; --good:#6fcfa9; --soft:#4a4437; --warn:#f2847c; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 Georgia, 'Times New Roman', serif; }
main { max-width:880px; margin:0 auto; padding:22px 16px 60px; overflow-wrap:anywhere; }
h1 { font-size:30px; line-height:1.2; margin:0 0 8px; } h2 { font-size:21px; margin:28px 0 6px; }
p { margin:8px 0; } a { color:var(--accent); } .sub { color:var(--muted); margin:0 0 18px; }
.box { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:12px 16px; margin:10px 0; }
.note { color:var(--muted); font-size:14.5px; } code { font:13px/1.4 ui-monospace, Menlo, monospace; }
canvas { display:block; width:100%; height:auto; border-radius:8px; touch-action:manipulation; }
.row { display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center; margin:8px 0; }
input[type=range] { flex:1 1 240px; min-width:160px; accent-color:var(--accent); }
.read { font-size:17px; margin:8px 0; } .read b { font-weight:normal; color:var(--accent); }
.key span { display:inline-block; margin:4px 16px 0 0; font-size:14px; color:var(--muted); } .key i { display:inline-block; width:12px; height:12px; margin-right:6px; vertical-align:-1px; border-radius:2px; }
details { margin-top:8px; } summary { cursor:pointer; color:var(--accent); }
ul.names { columns:3; column-gap:22px; padding-left:1.1em; margin:6px 0; font:12.5px/1.5 ui-monospace, Menlo, monospace; } ul.names li { break-inside:avoid; }
@media (max-width:700px) { ul.names { columns:2; } } @media (max-width:440px) { ul.names { columns:1; } }
</style>
</head>
<body>
<main>
<p class="note"><a href="round_two.html">Back to round two</a> · <a href="six_finished_theorems.html">Six finished theorems</a> · <a href="rh_in_six_steps.html">Six steps from three inputs</a></p>
<h1>How far is each published result?</h1>
<p class="sub">One file of the archive lists __TOTAL__ named statements from the literature and gives a line of Lean for each. This is how much of the archive each line leads to, and which statements Lean has checked here.</p>

<p>The announced proof of the Riemann Hypothesis leans on many theorems from the literature. One file of the archive is a table of them: __TOTAL__ named statements, each followed by a line of Lean. Nearly every line proves its statement by pointing at a theorem elsewhere in the archive; two lines lean on statements the archive assumes, and one statement is an empty slot, as said further down. (The same file holds __OTHER__ lines of other kinds and its own final theorem, which are not drawn here.) For each statement we traced the files its line names, followed one-line repeats to the file that holds the proof, and counted how many of the archive's files that file brings with it.</p>
<p>Each bar below is one named statement. Green bars are statements Lean has checked in our own build, with nothing assumed: __NPROVED__ of them so far.</p>

<div class="box">
<canvas id="chart" width="840" height="430" role="img" aria-label="One bar for each statement, sorted by the number of archive files that the file holding its proof brings with it, on a scale where each step up is ten times more. Green bars are checked in our build; red bars have a line that uses an assumed statement. The same numbers are in the list under the picture."></canvas>
<p class="key"><span><i style="background:var(--good)"></i>checked in our build</span><span><i style="background:var(--soft)"></i>not yet checked here</span><span><i style="background:var(--warn)"></i>its line uses an assumed statement</span><span><i style="border:2px solid var(--accent)"></i>the one you chose</span></p>
<p class="read" id="pick" aria-live="polite"></p>
<details><summary>All __DRAWN__ statements, with their numbers</summary>
<p class="note">After each name: the files its proof brings; in brackets, the count by the table's line where that is different; then "checked" if Lean has checked it here, or "assumed" if its line uses an assumed statement.</p>
<ul class="names">__ALLLIST__</ul>
</details>
</div>

<p><b>The __NPACK__ red bars.</b> Every line of the table is handed a small package of statements that the archive assumes and does not prove (three entries, two of them the same statement). Of the __TOTAL__ lines, __FREE__ never touch it. The other __NPACK__ do, so for those the table's line is not a proof from the archive alone.</p>
<p><b>One statement is not drawn.</b> <code>UnusedSlot72</code> is defined to be the statement "True", an empty slot. That leaves __DRAWN__ bars.</p>

<h2>What a number here means</h2>
<p>It is the number of archive files that the file or files holding the proof import, directly or through other files, themselves included: what a build has to compile before Lean can check that proof. It is a ceiling. A proof may use far less than its files import.</p>
<p>Finding the right file takes one step of care. For __NALIAS__ of the __DRAWN__ statements the table points at a theorem that only repeats, in one line, a result proved in another file, and the scan follows such one-line repeats to the proof's own file. Often the difference is a file or two. For __NBIG__ statements it is more than a hundred files, because the repeating line sits in a bundle that imports a great deal else. The Stone–von Neumann theorem is reached in the table through a bundle that brings 1,290 files, and is proved in a file that brings 3. Radford's theorem is reached through 967, and its proof is one file of 692 lines that needs nothing but Lean's mathematical library. Click a bar, or open the list under the picture, to see both numbers.</p>
<p>Most of our own checks went through the table's lines as they are written, so those builds compiled the bundles too. The last eight did not. The count above showed eight statements whose proofs needed only 115 files more than we had, where the table's lines would have gone through a bundle that brings 16,171; we built the 115 and Lean accepted each statement, proved by its own theorem.</p>

<p>For four statements the count falls short in one more way. The archive defines the name itself in a file that the proof's files do not import. Lean can check the proof with the files counted here, but to state the result under its published name it needs that file as well. That is 47 further files for each of <code>BaseChangeDefiniteUnitaryGroup</code> and <code>BaseChangeIsobaricTransfer</code>, 3,244 for <code>DoublingMethodLocalZetaIntegrals</code>, and one for <code>principalPolarisationOneSection</code>, which was checked through the table's own line. We met this when a check of the third was refused with "unknown identifier". <a href="tools/rh_published_def_files.py">tools/rh_published_def_files.py</a> looks for it in every row; the bars show the proof's files, as for every other statement.</p>

<h2>How many are within reach</h2>
<div class="box">
<div class="row"><label for="budget">Compile, for any one proof, at most this many files:</label><input id="budget" type="range" min="0" max="__STOPMAX__" step="1" value="6" aria-label="the most files compiled for one proof, in fixed steps from 10 to the whole archive"></div>
<p class="read" id="buy" aria-live="polite"></p>
<p class="note">Counted one proof at a time. Proofs share files, so many together cost far less than the sum. Our own builds, which went by the table's lines, show it: __BUILDNOTE__</p>
</div>

<h2>The statements checked here</h2>
<p>__PROVEDNOTE__</p>
<ul class="names">__PROVEDLIST__</ul>

<h2>What this is, and what it is not</h2>
<p>It is a measurement of the archive's shape, and a record of what Lean accepted on one machine. For each green bar Lean compiled a proof of the statement here and reported only its three standard axioms: the table's own line for __NLINE__ of them, the theorem that line leads to for __NDIRECT__, and for the other __NREPL__ the table's line with each repeated theorem replaced by the one it repeats.</p>
<p>It is not a list of famous theorems verified. A name is what the archive calls a statement; what the statement says has to be read. The ones that have been read against the classical theorems are on <a href="six_finished_theorems.html">Six finished theorems</a>, each with a note of who read it; the rest are names to us. Nor does any of this bear on whether the main proof is right: these are its ingredients, and old ones.</p>

<h2>Sources, and what was run</h2>
<p class="note">The table is the archive's file <code>EveryCharacterOfLiteratureOfVWin.lean</code> (mirror 1337isnot1337/riemann-hypothesis-solved at revision 6193bb5). <a href="tools/rh_published_scan2.py">tools/rh_published_scan2.py</a> reads it from your own copy, finds the file that declares each theorem a line names, follows one-line repeats to the proof's own file, follows import lines, and marks the lines that use the package; an earlier and simpler scan, <a href="tools/rh_published_scan.py">tools/rh_published_scan.py</a>, chose what we built. The checks: <a href="tools/rh_published_check_gen.py">tools/rh_published_check_gen.py</a> restates the archive's line for each statement as a theorem, without the package, and Lean prints its axioms; for the statements checked in the last round, <a href="tools/rh_published_replay_gen.py">tools/rh_published_replay_gen.py</a> writes the table's line again with each one-line repeat replaced by the theorem it repeats, so that the file holding the proof is the one compiled; for the eight before those, <a href="tools/rh_published_direct_gen.py">tools/rh_published_direct_gen.py</a> writes the proof by the theorem the line leads to; the replies are in <a href="crew_visuals/lean_desk.txt">the desk record</a>, and <a href="crew_visuals/lean_runs.txt">the record of our Lean runs</a> tells how the builds went. This page is written by <a href="tools/rh_published_ladder.py">tools/rh_published_ladder.py</a> from <a href="crew_visuals/rh_published_scan2.json">the scan</a> and <a href="crew_visuals/rh_published_proved.txt">the list of statements checked</a>. Page by Fixpoint for Marginalia.</p>
</main>
<script>
// DATA-BEGIN  [name, files the proof's own file brings, files the table's line brings, 0 not checked here | 1 checked here | 2 its line uses the package]
const DATA = __DATA__;
const STOPS = __STOPS__;
// DATA-END
(function () {
  const $ = id => document.getElementById(id), css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const fmt = n => n.toLocaleString('en-US');
  let sel = -1, geom = null;
  function draw() {
    const c = $('chart'), w = c.clientWidth || 840, narrow = w < 520, h = Math.round(w * (narrow ? 0.8 : 0.5)), dpr = window.devicePixelRatio || 1;
    c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); c.style.height = h + 'px';
    const g = c.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
    const L = 64, R = 8, T = 10, B = 22, bw = (w - L - R) / DATA.length, top = Math.log10(200000);
    const Y = v => T + (h - T - B) * (1 - Math.log10(Math.max(v, 1)) / top);
    geom = { L, bw };
    const col = [css('--soft'), css('--good'), css('--warn')];
    g.font = '11px ui-monospace, Menlo, monospace'; g.fillStyle = css('--muted'); g.strokeStyle = css('--line'); g.lineWidth = 1; g.textAlign = 'right';
    [1, 10, 100, 1000, 10000, 100000].forEach(v => { const y = Y(v); g.beginPath(); g.moveTo(L, y); g.lineTo(w - R, y); g.stroke(); g.fillText(fmt(v), L - 6, y + 4); });
    DATA.forEach((r, k) => { const x = L + k * bw, y = Y(r[1]); g.fillStyle = col[r[3]]; g.fillRect(x + 0.4, y, Math.max(bw - 0.8, 1), Math.max(h - B - y, 2)); if (k === sel) { g.strokeStyle = css('--accent'); g.lineWidth = 2; g.strokeRect(x - 0.5, y - 2, bw + 1, h - B - y + 4); } });
    g.fillStyle = css('--muted'); g.textAlign = 'center'; g.fillText('statements, fewest files first', L + (w - L - R) / 2, h - 6);
    const r = sel >= 0 ? DATA[sel] : null;
    $('pick').innerHTML = !r ? 'Click or tap a bar to see which statement it is.' : r[3] === 2 ? '<b>' + r[0] + '</b>: its line uses a statement the archive assumes, so it is not a proof from the archive alone. The archive theorems it also names bring ' + fmt(r[1]) + ' files.'
      : '<b>' + r[0] + '</b>: ' + (r[1] === 1 ? 'its proof is a single file that needs nothing else from the archive' : 'its proof brings ' + fmt(r[1]) + ' of the archive\\'s files') + (r[2] > r[1] ? ' (' + fmt(r[2]) + ' by the table\\'s line)' : '') + '. ' + (r[3] === 1 ? 'Lean has checked it here.' : 'Not yet checked here.');
  }
  function buy() {
    const cap = STOPS[Number($('budget').value)];
    let reach = 0, done = 0; DATA.forEach(r => { if (r[3] !== 2 && r[1] <= cap) reach++; if (r[3] === 1) done++; });
    $('buy').innerHTML = 'With at most <b>' + fmt(cap) + '</b> files for any one proof, <b>' + reach + '</b> of the ' + DATA.length + ' statements drawn are within reach (the red ones are never counted). Lean has checked ' + done + ' of the ' + DATA.length + ' here.';
  }
  $('budget').addEventListener('input', buy);
  $('chart').addEventListener('click', e => { const b = e.target.getBoundingClientRect(), k = Math.floor((e.clientX - b.left - geom.L) / geom.bw); if (k >= 0 && k < DATA.length) { sel = k; draw(); } });
  let pending = 0; window.addEventListener('resize', () => { cancelAnimationFrame(pending); pending = requestAnimationFrame(draw); });
  if (window.matchMedia) window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', draw);
  sel = DATA.findIndex(r => r[0] === 'Linnik'); draw(); buy();
})();
</script>
</body>
</html>
"""
stops = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 175187]
provedlist = "".join(f"<li>{html.escape(n)}</li>" for n in sorted(proved))
alllist = "".join(f"<li>{html.escape(x[0])} {x[1]:,}" + (f" ({x[2]:,})" if x[2] != x[1] else "") + (" checked" if x[3] == 1 else " assumed" if x[3] == 2 else "") + "</li>" for x in sorted(data))
provednote = (f"{len(proved)} statements. {n_proved - len(direct) - len(replaced)} are in the archive's table and were checked through its own line for them"
              + (f"; {len(direct)} more are in the table and were checked by the theorem that line leads to, without the bundle file in between" if direct else "")
              + (f"; {len(replaced)} more were checked by the table's line with each repeated theorem replaced by the one it repeats" if replaced else "")
              + (f"; {len(outside)} more ({', '.join(html.escape(e) for e in outside)}) is proved in the archive but is not in that table, and was found by an earlier sweep of what we had compiled." if outside else ".")
              + (" " + html.escape(notes[1]) if len(notes) > 1 else ""))
if not notes: sys.exit("REFUSING: PROVED has no first comment line with the sentence about our builds")
page = (page.replace("__DATA__", json.dumps(data, separators=(",", ":"))).replace("__STOPS__", json.dumps(stops)).replace("__STOPMAX__", str(len(stops) - 1))
            .replace("__PROVEDLIST__", provedlist).replace("__PROVEDNOTE__", provednote).replace("__BUILDNOTE__", html.escape(notes[0]))
            .replace("__TOTAL__", str(total)).replace("__OTHER__", str(len(d["other_lines"]))).replace("__NALIAS__", str(n_alias)).replace("__NBIG__", str(n_big)).replace("__ALLLIST__", alllist)
            .replace("__NLINE__", str(n_proved - len(direct) - len(replaced))).replace("__NDIRECT__", str(len(direct))).replace("__NREPL__", str(len(replaced))).replace("__NPROVED__", str(n_proved))
            .replace("__NPACK__", str(n_pack)).replace("__FREE__", str(total - n_pack)).replace("__DRAWN__", str(len(data))))
left = __import__("re").findall(r"__[A-Z]+__", page)
if left: sys.exit("REFUSING: unfilled places in the page: " + ", ".join(left))
open(outp, "w", encoding="utf-8").write(page)
print(f"written: {len(data)} statements drawn of {total}; {n_proved} checked in the table, {len(outside)} outside it; {n_pack} use the package")
