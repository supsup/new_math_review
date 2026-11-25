"""Replay for crew_visuals/class_numbers_band.html (Confluence).

1. Compile tools/class_number_sweep.c with the system C compiler in a temporary directory, run it to 4,000,000,
   and compare its JSON (minified) with the JSON embedded in the page, byte for byte.
2. Independently check class numbers at a random sample of fundamental discriminants, and at the last record
   holders, with Dirichlet's sum h(-d) = (sum of chi(a) over 0 < a < d/2) / (2 - chi(2)) for d > 4, chi the
   Kronecker symbol (-d / .) computed by quadratic reciprocity. This shares nothing with the form count.
3. Check that the discriminants with h = 1 are exactly Heegner's nine and that the records are monotone.
Standard library only, plus a C compiler. Usage:  python3 tools/check_class_numbers_band.py
"""

import json
import math
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def jacobi(a, n):
    a %= n
    r = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                r = -r
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            r = -r
        a %= n
    return r if n == 1 else 0


def kron(D, a):
    r = 1
    while a % 2 == 0:
        a //= 2
        if D % 2 == 0:
            return 0
        r *= 1 if D % 8 in (1, 7) else -1
    return r * jacobi(D, a) if a > 1 else r


def h_dirichlet(d):
    s = sum(kron(-d, a) for a in range(1, (d - 1) // 2 + 1))
    return s // (2 - kron(-d, 2))


def squarefree(m):
    p = 2
    while p * p <= m:
        if m % (p * p) == 0:
            return False
        p += 1
    return True


def fundamental(d):
    if d % 4 == 3:
        return squarefree(d)
    if d % 4 == 0:
        m = d // 4
        return m % 4 in (1, 2) and squarefree(m)
    return False


def class_number(d):
    h, a = 0, 1
    while 3 * a * a <= d:
        for b in range(-a + 1, a + 1):
            if (b * b + d) % (4 * a):
                continue
            c = (b * b + d) // (4 * a)
            if c < a or (b < 0 and a == c) or math.gcd(math.gcd(a, b), c) != 1:
                continue
            h += 1
        a += 1
    return h


def main():
    page = (ROOT / 'crew_visuals' / 'class_numbers_band.html').read_text()
    embedded = re.search(r'<script id="band" type="application/json">(.*?)</script>', page, re.S).group(1)
    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / 'sweep'
        subprocess.run(['cc', '-O2', '-o', str(exe), str(ROOT / 'tools' / 'class_number_sweep.c'), '-lm'], check=True)
        out = subprocess.run([str(exe), '4000000'], check=True, capture_output=True, text=True).stdout
    fresh = json.dumps(json.loads(out), separators=(',', ':'))
    assert fresh == embedded, 'the embedded data differ from a fresh run of the sweep'
    band = json.loads(embedded)
    random.seed(25)
    sample = sorted({d for d in random.sample(range(5, 200000), 4000) if fundamental(d)})[:400]
    sample += [r[1] for r in band['records'][-3:]]
    bad = [d for d in sample if class_number(d) != h_dirichlet(d)]
    assert not bad, bad[:5]
    recorded = {r[1]: r[2] for r in band['records']}
    assert all(class_number(d) == h for d, h in recorded.items() if d < 300000)
    assert band['class_number_one'] == [3, 4, 7, 8, 11, 19, 43, 67, 163]
    L = lambda d, h: 2 * math.pi * h / ((6 if d == 3 else 4 if d == 4 else 2) * math.sqrt(d))
    mx, mn = -1.0, 1e9
    for t, d, h in band['records']:
        v = L(d, h)
        if t == 'max':
            assert v > mx
            mx = v
        else:
            assert v < mn
            mn = v
    print(f"The sweep reproduces the page's data byte for byte: {band['fundamental']:,} fields, {len(band['records'])} records, {len(band['bins'])} bins.")
    print(f"Dirichlet's sum agrees with the form count at {len(sample)} fields, including the last three record holders.")
    print(f"Records monotone; largest L(1, chi) = {mx:.6f}, smallest = {mn:.6f}; h = 1 exactly at Heegner's nine.")


if __name__ == '__main__':
    main()
