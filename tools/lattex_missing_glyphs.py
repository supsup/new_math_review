#!/usr/bin/env python3
"""lattex_missing_glyphs.py CENSUS.json LATTEX.jar OUT.json: which characters does LatteX draw as its missing-glyph box? Each character is
set alone, raw; its outline is compared with the outline LatteX draws for two unassigned code points (U+0378, U+0379),
which no font can have and which must agree with each other for the test to mean anything."""
import json, subprocess, sys, re
census, jar, outp = sys.argv[1:4]
rows = json.load(open(census, encoding='utf-8'))['rows']
chars = [r['ch'] for r in rows if ord(r['ch']) not in (0x304, 0x2009, 0xA0)]
probes = [chr(0x378), chr(0x379)] + chars
proc = subprocess.run(['java', '-jar', jar, '--batch'], input='\n'.join(probes) + '\n', capture_output=True, text=True)
recs = proc.stdout.split('\0')
if recs and recs[-1].strip() == '': recs.pop()
assert len(recs) == len(probes), (len(recs), len(probes), proc.stderr[:200])
def outline(svg): return tuple(re.findall(r'<path d="([^"]*)"', svg))
nd = outline(recs[0])
if not nd or nd != outline(recs[1]): sys.exit('no stable missing-glyph outline: %r vs %r' % (recs[0][:200], recs[1][:200]))
print('missing-glyph outline begins:', nd[0][:64])
tofu, err, ok = [], [], []
for ch, rec in zip(chars, recs[2:]):
    if '<svg' not in rec: err.append((ch, rec.strip()[:120]))
    elif outline(rec) == nd: tofu.append(ch)
    else: ok.append(ch)
info = {r['ch']: r for r in rows}
json.dump({'tofu': tofu, 'errors': err, 'ok': len(ok)}, open(outp, 'w', encoding='utf-8'), ensure_ascii=False)
print('characters set alone:', len(chars), '; drawn:', len(ok), '; refused with an error:', len(err), '; DRAWN AS THE MISSING-GLYPH BOX:', len(tofu))
for ch in tofu: print('  TOFU', info[ch]['cp'], ch, info[ch]['name'], '| used', info[ch]['n'], 'times in', info[ch]['files'], 'files, e.g.', info[ch]['eg'][0])
for ch, why in err: print('  ERROR', info[ch]['cp'], ch, info[ch]['name'], '|', why)
