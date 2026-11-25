"""Replay for crew_visuals/hecke_l_at_one.html (Confluence).

1. Run the page's own arithmetic (the JavaScript between MATH-BEGIN and MATH-END) in node: every character mod q for
   3 <= q <= 80, L(1, chi) for each primitive non-principal one, and L(1 + it, chi) at t = 1, 7.5, 20 and 45.
2. Separately in Python, written apart from the page: the characters from a generator search of their own, compared
   value by value; L(1, chi) = -(1/q) sum chi(a) psi(a/q) with the digamma function psi (recurrence and asymptotic
   series), a different formula from the page's; and L(1 + it, chi) by a separately written Euler-Maclaurin sum for the
   Hurwitz zeta function with other parameters (200 terms, six corrections).
3. Dirichlet's class number formula for every q <= 200 with -q a fundamental discriminant, h counted from reduced forms.
4. The two claims the page draws: no primitive L(1, chi) with q <= 80 is within 0.1 of 0, and |zeta(1 + it)| stays above
   0.3 for 0.5 <= t <= 60 on a fine grid. These are finite observations, not the theorem.
Standard library and node. Usage:  python3 tools/check_hecke_l_at_one.py
"""

import cmath
import json
import math
import re
import subprocess
import tempfile
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TS = [1.0, 7.5, 20.0, 45.0]


def digamma(x):
    r = 0.0
    while x < 10:
        r -= 1 / x
        x += 1
    x2 = 1 / (x * x)
    return r + math.log(x) - 1 / (2 * x) - x2 * (1 / 12 - x2 * (1 / 120 - x2 * (1 / 252 - x2 * (1 / 240 - x2 / 132))))


BERN = [1 / 6, -1 / 30, 1 / 42, -1 / 30, 5 / 66, -691 / 2730]


def hurwitz(s, x):
    N = 200
    total = sum((n + x) ** (-s) for n in range(N))
    y = N + x
    total += y ** (1 - s) / (s - 1) + y ** (-s) / 2
    poch, fact = s, 2.0
    for k, b in enumerate(BERN, start=1):
        total += b / fact * poch * y ** (-s - 2 * k + 1)
        poch *= (s + 2 * k - 1) * (s + 2 * k)
        fact *= (2 * k + 1) * (2 * k + 2)
    return total


def unit_group_chars(q):
    """All characters mod q as dicts a -> complex, from a brute-force generating set of (Z/q)^x."""
    units = [a for a in range(1, q) if gcd(a, q) == 1]
    # build the group as a product of cyclic factors by a greedy search for an element of maximal order
    def order(a):
        x, k = a, 1
        while x != 1:
            x, k = x * a % q, k + 1
        return k
    chars = [{1: 1 + 0j}]
    covered = {1}
    gens = []
    while len(covered) < len(units):
        g = max((a for a in units if a not in covered), key=order)
        # smallest power of g that lands in the subgroup generated so far
        m, x = 1, g
        while x not in covered:
            x, m = x * g % q, m + 1
        gens.append((g, m, x))
        new = set()
        for c in covered:
            y = c
            for _ in range(m):
                new.add(y)
                y = y * g % q
        covered = new
        newchars = []
        for ch in chars:
            # chi(g)^m must equal chi(x); choose the m-th roots
            base = ch[x]
            r0 = cmath.exp(cmath.log(base) / m) if base != 1 else 1 + 0j
            for j in range(m):
                z = r0 * cmath.exp(2j * math.pi * j / m)
                nc = {}
                for c, v in ch.items():
                    y, w = c, v
                    for _ in range(m):
                        nc[y] = w
                        y, w = y * g % q, w * z
                newchars.append(nc)
        chars = newchars
    return chars


def primitive(ch, q):
    for p in {p for p in range(2, q + 1) if q % p == 0 and all(p % r for r in range(2, int(p ** .5) + 1))}:
        d = q // p
        if all(abs(v - 1) < 1e-9 for a, v in ch.items() if a % d == 1 % d):
            return False
    return True


def class_number(d):
    h, a = 0, 1
    while 3 * a * a <= d:
        for b in range(-a + 1, a + 1):
            if (b * b + d) % (4 * a):
                continue
            c = (b * b + d) // (4 * a)
            if c < a or (b < 0 and a == c) or gcd(gcd(a, abs(b)), c) != 1:
                continue
            h += 1
        a += 1
    return h


def fundamental_neg(q):
    sqf = lambda m: all(m % (p * p) for p in range(2, int(m ** .5) + 1))
    if q % 4 == 3:
        return sqf(q)
    if q % 4 == 0:
        m = q // 4
        return m % 4 in (1, 2) and sqf(m)
    return False


def main():
    page = (ROOT / 'crew_visuals' / 'hecke_l_at_one.html').read_text()
    js = re.search(r'// MATH-BEGIN\n(.*?)// MATH-END', page, re.S).group(1)
    harness = js + """
const out = [];
for (let q = 3; q <= 80; q++) {
  const { chars } = characters(q);
  for (const v of chars) {
    const principal = v.every((z, a) => gcd(a, q) !== 1 || Math.abs(z[0] - 1) < 1e-9);
    if (principal || !isPrimitive(v, q)) continue;
    const at = [Lvalue(v, q, C(1))].concat(""" + json.dumps(TS) + """.map(t => Lvalue(v, q, C(1, t))));
    out.push([q, v, at.map(z => [z.re, z.im])]);
  }
}
const zl = []; for (let i = 0; i <= 2000; i++) { const t = 0.5 + 59.5 * i / 2000; zl.push(cabs(hurwitz(C(1, t), 1, false))); }
console.log(JSON.stringify({ out, zl }));
"""
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / 'h.js'
        f.write_text(harness)
        res = json.loads(subprocess.run(['node', str(f)], check=True, capture_output=True, text=True).stdout)
    rows, worst, closest = res['out'], 0.0, 9.0
    byq = {}
    for q, v, at in rows:
        byq.setdefault(q, []).append((v, at))
    for q in range(3, 81):
        mine = [ch for ch in unit_group_chars(q) if not all(abs(z - 1) < 1e-9 for z in ch.values()) and primitive(ch, q)]
        theirs = byq.get(q, [])
        assert len(mine) == len(theirs), (q, len(mine), len(theirs))
        for v, at in theirs:
            ch = {a: complex(*v[a]) for a in range(1, q) if gcd(a, q) == 1}
            assert any(all(abs(ch[a] - m[a]) < 1e-9 for a in ch) for m in mine), ('character not found', q)
            L1 = -sum(ch[a] * digamma(a / q) for a in ch) / q
            assert abs(L1 - complex(*at[0])) < 1e-9, (q, L1, at[0])
            closest = min(closest, abs(L1))
            for t, z in zip(TS, at[1:]):
                s = complex(1, t)
                Lt = q ** (-s) * sum(ch[a] * hurwitz(s, a / q) for a in ch)
                worst = max(worst, abs(Lt - complex(*z)))
    assert worst < 1e-8, worst
    assert closest > 0.1, closest
    nq = 0
    for q in range(3, 201):
        if fundamental_neg(q):
            ch = next(c for c in unit_group_chars(q) if all(abs(z.imag) < 1e-9 for z in c.values()) and c[q - 1].real < 0 and primitive(c, q))
            L1 = -sum(ch[a] * digamma(a / q) for a in ch) / q
            w = 6 if q == 3 else 4 if q == 4 else 2
            assert abs(L1.real - 2 * math.pi * class_number(q) / (w * math.sqrt(q))) < 1e-9, q
            nq += 1
    zmin = min(res['zl'])
    assert zmin > 0.3, zmin
    print(f"The page's own arithmetic, run in node, gives {len(rows):,} primitive characters for 3 <= q <= 80; a separate "
          f"Python construction finds the same ones, value for value.")
    print(f"L(1, chi) agrees with the digamma formula to 1e-9 for all of them (the closest to 0 is {closest:.4f}), and "
          f"L(1 + it, chi) at t = 1, 7.5, 20, 45 agrees with a separate Euler-Maclaurin sum to {worst:.1e}.")
    print(f"Dirichlet's class number formula holds at all {nq} q <= 200 with -q fundamental; |zeta(1 + it)| stays above "
          f"{zmin:.4f} for 0.5 <= t <= 60 on 2,001 points.")


if __name__ == '__main__':
    main()
