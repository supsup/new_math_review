#!/usr/bin/env python3
"""typeset_review_pairs.py REPO OLD NEW CLASS FILE...: a reader's tool. for each file, show what a typesetting commit changed. Every element of the
given class in NEW is cut out; what is left must be found, piece by piece and in order, in OLD; the text of OLD that
sat where each element now sits is printed beside the element's LaTeX. Anything else that changed is printed as a diff."""
import sys, subprocess, re, html, difflib
repo, old, new, cls = sys.argv[1:5]; files = sys.argv[5:]
def show(rev, f):
    r = subprocess.run(['git', '-C', repo, 'show', f'{rev}:{f}'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None
SPAN = re.compile(r'<(span|div) class="%s"[^>]*?data-tex="([^"]*)"[^>]*>.*?</\1>' % re.escape(cls), re.S)
total = 0
for f in files:
    a, b = show(old, f), show(new, f)
    if b is None: print('==', f, 'MISSING in new'); continue
    spans = list(SPAN.finditer(b))
    if a is None: print('==', f, 'NEW FILE;', len(spans), 'formulas'); total += len(spans); continue
    PH = '\x00'
    b2 = SPAN.sub(PH, b)
    segs = b2.split(PH)
    pos = 0; olds = []; ok = True
    for i, seg in enumerate(segs):
        j = a.find(seg, pos) if seg else pos
        if j < 0: ok = False; break
        if i > 0: olds.append(a[pos:j])
        elif j != 0: ok = False; break
        pos = j + len(seg)
    if ok and pos != len(a): ok = False
    print('==', f, len(spans), 'formulas;', 'ONLY formulas changed' if ok else 'OTHER CHANGES TOO')
    total += len(spans)
    if ok:
        for o, m in zip(olds, spans):
            t = html.unescape(re.sub(r'<[^>]+>', lambda x: {'<sup>': '^(', '</sup>': ')', '<sub>': '_(', '</sub>': ')'}.get(x.group(0), ''), o))
            print('   ', repr(t)[:70].ljust(72), '=>', html.unescape(m.group(2))[:110])
    else:
        for l in difflib.unified_diff(a.split('\n'), b2.split('\n'), lineterm='', n=0):
            if l.startswith(('+', '-')) and not l.startswith(('+++', '---')): print('   ', l[:230].replace(PH, ' [FORMULA] '))
print('total formulas:', total)
