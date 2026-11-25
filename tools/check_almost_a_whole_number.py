#!/usr/bin/env python3
"""check_almost_a_whole_number.py [LIMIT [OUT.json]]

The separate program behind almost_a_whole_number.html. For every field discriminant D from -3 down to -LIMIT (250 by
default) it lists the reduced forms, computes j of each and the polynomial whose roots they are, and reports how far the
coefficients are from whole numbers; and for n = 1..250 it computes e^(pi sqrt n) and its distance from a whole number.
Standard library only. To compare the page with it: run the page's MATH block (between MATH-BEGIN and MATH-END) and
compare with OUT.json; the page also carries a sample of these numbers and checks itself against them on load."""
# Independent numbers for the page 'Almost a whole number'. Written apart from the page's JavaScript and by a different route:
# the page computes j from the two Eisenstein series in q = e^(2 pi i tau); this program computes it from the three theta
# constants in the nome e^(pi i tau), in Python's decimal arithmetic, and pi from Machin's formula in whole numbers.
import json, sys
from decimal import Decimal as Dc, getcontext
from math import gcd, isqrt
P = 300; getcontext().prec = P
def machin_pi(digits):
    S = 10 ** (digits + 10)
    def atan_inv(x):
        t = S // x; s = t; n = 1; x2 = x * x
        while t:
            t //= x2; n += 2
            s += -(t // n) if (n // 2) % 2 else t // n
        return s
    return 4 * (4 * atan_inv(5) - atan_inv(239)) // 10 ** 10
PI_DIGITS = 290
PI = Dc(machin_pi(PI_DIGITS)) / Dc(10) ** PI_DIGITS
def cos_sin(y):
    y = y % (2 * PI)
    c = s = Dc(0); t = Dc(1); n = 0
    while abs(t) > Dc(10) ** (-(P + 5)) or n < 4:
        if n % 4 == 0: c += t
        elif n % 4 == 1: s += t
        elif n % 4 == 2: c -= t
        else: s -= t
        n += 1; t = t * y / n
    return c, s
def cexp(x, y):                     # e^(x + i y)
    m = x.exp(); c, s = cos_sin(y); return (m * c, m * s)
def cmul(a, b): return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])
def cadd(a, b): return (a[0] + b[0], a[1] + b[1])
def cdiv(a, b):
    d = b[0] * b[0] + b[1] * b[1]; return ((a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d)
def cpow(a, n):
    r = (Dc(1), Dc(0))
    for _ in range(n): r = cmul(r, a)
    return r
def j_theta(tre, tim):              # tau = tre + i tim, tim > 0
    def term(e):                    # e^(pi i tau e) for a rational exponent e given as Decimal
        return cexp(-PI * tim * e, PI * tre * e)
    t2 = (Dc(0), Dc(0)); t3 = (Dc(1), Dc(0)); t4 = (Dc(1), Dc(0)); n = 0
    while True:
        a = term((Dc(2 * n + 1) / 2) ** 2); t2 = cadd(t2, (2 * a[0], 2 * a[1]))
        if n >= 1:
            b = term(Dc(n * n)); t3 = cadd(t3, (2 * b[0], 2 * b[1])); sg = -1 if n % 2 else 1; t4 = cadd(t4, (2 * sg * b[0], 2 * sg * b[1]))
        if abs(a[0]) + abs(a[1]) < Dc(10) ** (-(P + 5)) and n > 2: break
        n += 1
    s = cadd(cadd(cpow(t2, 8), cpow(t3, 8)), cpow(t4, 8)); num = cpow(s, 3); num = (32 * num[0], 32 * num[1])
    den = cpow(cmul(cmul(t2, t3), t4), 8)
    return cdiv(num, den)
def squarefree(n):
    i = 2
    while i * i <= n:
        if n % (i * i) == 0: return False
        i += 1
    return True
def fundamental(D):                 # D < 0
    if D % 4 == 1: return squarefree(-D)
    if D % 4 == 0: m = D // 4; return m % 4 in (2, 3) and squarefree(-m)
    return False
def forms(D):
    out = []; a = 1
    while 3 * a * a <= -D:
        for b in range(-a + 1, a + 1):
            if (b * b - D) % (4 * a): continue
            c = (b * b - D) // (4 * a)
            if c < a or (c == a and b < 0): continue
            if gcd(gcd(a, abs(b)), c) != 1: continue
            out.append((a, b, c))
        a += 1
    return out
def poly(D):
    fs = forms(D); coef = [(Dc(1), Dc(0))]           # highest power first
    sq = Dc(-D).sqrt()
    for a, b, c in fs:
        jv = j_theta(Dc(-b) / (2 * a), sq / (2 * a))
        new = [(Dc(0), Dc(0))] * (len(coef) + 1)
        for i, cf in enumerate(coef):
            new[i] = cadd(new[i], cf); m = cmul(cf, jv); new[i + 1] = cadd(new[i + 1], (-m[0], -m[1]))
        coef = new
    ints = [int(c[0].to_integral_value()) for c in coef]
    err = max(max(abs(c[0] - i), abs(c[1])) for c, i in zip(coef, ints))
    return fs, ints, err
LIM = int(sys.argv[1]) if len(sys.argv) > 1 else 250
out = {"pi": str(PI)[:2 + 250], "fields": {}, "near": {}}
worst = Dc(0)
for D in range(-3, -LIM - 1, -1):
    if not fundamental(D): continue
    fs, ints, err = poly(D); worst = max(worst, err)
    out["fields"][str(D)] = {"h": len(fs), "forms": fs, "poly": [str(i) for i in ints]}
for n in range(1, 251):
    v = (PI * Dc(n).sqrt()).exp(); fr = v - v.to_integral_value()
    out["near"][str(n)] = {"floor": str(int(v // 1)), "dist": format(abs(fr), ".6E")}
json.dump(out, open(sys.argv[2] if len(sys.argv) > 2 else "expect_j.json", "w"), indent=0)
print("fundamental discriminants down to", -LIM, ":", len(out["fields"]), "; largest distance of a coefficient from a whole number:", format(worst, ".3E"))
for D in (-3, -4, -7, -8, -11, -19, -43, -67, -163, -15, -20, -23): print(D, out["fields"][str(D)]["h"], out["fields"][str(D)]["poly"])
print("class number one:", [D for D, f in out["fields"].items() if f["h"] == 1])
top = sorted(out["near"].items(), key=lambda kv: float(kv[1]["dist"]))[:14]
print("closest to whole numbers:", [(k, v["dist"]) for k, v in top])
