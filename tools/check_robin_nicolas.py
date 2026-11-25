"""Replay for crew_visuals/robin_and_nicolas.html (Confluence).

1. Compile tools/robin_nicolas.c in a temporary directory and run it (10^7, 10^8); run tools/robin_ca_numbers.py
   (which itself checks its construction against OEIS A004490); assemble their JSON exactly as the page does and
   compare it with the JSON embedded in the page, byte for byte.
2. Independently of the divisor sieve: sigma(n) from a smallest-prime-factor sieve for every n <= 200,000. The
   numbers n >= 3 with sigma(n) >= e^gamma n log log n must be the embedded list, and [2] + that list must be OEIS
   A067698 as fetched. Report the closest any n comes to the line, to show there is no near-tie.
3. Independently of the C sums: every primorial up to the 120,569th with exactly rounded running sums (Shewchuk's
   partials, as in math.fsum). p_66 = 317, p_120568 = 1,591,873 and p_120569 = 1,591,883; c(N_1) and c(N_66) agree
   with Nicolas's printed 2.2085892614 and 4.0628356921; c(N_66) is the largest; c(N_120568) > e^gamma (2 + beta)
   > c(N_120569), with beta = 2 + gamma - log pi - 2 log 2 = 0.0461914179 as printed; and the C values agree to 1e-8.
4. For the colossally abundant rows with x <= 1000, rebuild n as an exact integer and recompute sigma(n)/n with
   exact fractions; the page's ratio and D must agree to 1e-9.
Standard library, a C compiler, and numpy (for the CA tool). Usage:  python3 tools/check_robin_nicolas.py
"""

import json
import math
import re
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAMMA = 0.5772156649015329
EG = math.exp(GAMMA)
OEIS_A067698 = [2, 3, 4, 5, 6, 8, 9, 10, 12, 16, 18, 20, 24, 30, 36, 48, 60, 72, 84, 120, 180, 240, 360, 720, 840,
                2520, 5040]


class RunningSum:
    """Exactly rounded running sum (Shewchuk's partials)."""

    def __init__(self):
        self.partials = []

    def add(self, x):
        out = []
        for y in self.partials:
            if abs(x) < abs(y):
                x, y = y, x
            hi = x + y
            lo = y - (hi - x)
            if lo:
                out.append(lo)
            x = hi
        out.append(x)
        self.partials = out

    def value(self):
        return math.fsum(self.partials)


def spf_sieve(N):
    spf = list(range(N + 1))
    for i in range(2, int(N ** .5) + 1):
        if spf[i] == i:
            for j in range(i * i, N + 1, i):
                if spf[j] == j:
                    spf[j] = i
    return spf


def sigma_from_spf(n, spf):
    s = 1
    while n > 1:
        p, pk, t = spf[n], 1, 1
        while n % p == 0:
            n //= p
            pk *= p
            t += pk
        s *= t
    return s


def primes_upto(N):
    sv = bytearray([1]) * (N + 1)
    sv[0:2] = b'\x00\x00'
    for i in range(2, int(N ** .5) + 1):
        if sv[i]:
            sv[i * i::i] = bytearray(len(range(i * i, N + 1, i)))
    return [i for i in range(N + 1) if sv[i]]


def main():
    page = (ROOT / 'crew_visuals' / 'robin_and_nicolas.html').read_text()
    embedded = re.search(r'<script id="rn" type="application/json">(.*?)</script>', page, re.S).group(1)
    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / 'rn'
        subprocess.run(['cc', '-O2', '-o', str(exe), str(ROOT / 'tools' / 'robin_nicolas.c'), '-lm'], check=True)
        rn = json.loads(subprocess.run([str(exe), '10000000', '100000000'], check=True, capture_output=True, text=True).stdout)
    ca = json.loads(subprocess.run([sys.executable, '-B', str(ROOT / 'tools' / 'robin_ca_numbers.py')], check=True,
                                   capture_output=True, text=True).stdout)
    data = dict(rn)
    data['ca'] = ca
    assert json.dumps(data, separators=(',', ':')) == embedded, 'the embedded data differ from a fresh run of the tools'

    N = 200000
    spf = spf_sieve(N)
    exc, closest = [], (1.0, 0)
    for n in range(3, N + 1):
        r = sigma_from_spf(n, spf) / (n * math.log(math.log(n)))
        if r >= EG:
            exc.append(n)
        closest = min(closest, (abs(r - EG), n))
    assert exc == data['exceptions'], exc
    assert [2] + exc == OEIS_A067698
    assert data['robin_max_after_5040'][:2] == [10080, sigma_from_spf(10080, spf)]
    assert data['lagarias_max'][:2] == [12, 28]

    P = primes_upto(1591883)
    assert (len(P), P[65], P[120567]) == (120569, 317, 1591873)
    S, T, c = RunningSum(), RunningSum(), []
    for p in P:
        S.add(-math.log1p(-1 / p))
        T.add(math.log(p))
        th = T.value()
        c.append((math.exp(S.value()) - EG * math.log(th)) * math.sqrt(th))
    beta = 2 + GAMMA - math.log(math.pi) - 2 * math.log(2)
    limsup = EG * (2 + beta)
    assert abs(beta - 0.0461914179) < 1e-10 and abs(limsup - 3.6444150964) < 1e-9
    assert abs(c[0] - 2.2085892614) < 1e-9 and abs(c[65] - 4.0628356921) < 1e-9
    assert max(range(len(c)), key=c.__getitem__) == 65
    assert c[120567] > limsup > c[120568]
    assert abs(c[120567] - data['c120568']) < 1e-8 and abs(c[120568] - data['tail_max_from_120569'][1]) < 1e-8
    assert abs(c[65] - data['c66']) < 1e-8 and data['tail_max_from_120569'][0] == 120569
    for k, p, ratio, ck, theta in data['primorials']:
        if k <= len(c):
            assert P[k - 1] == p and abs(c[k - 1] - ck) < 1e-8, k

    sys.path.insert(0, str(ROOT / 'tools'))
    import numpy as np
    import robin_ca_numbers as R
    checked = 0
    for x, logn, ratio, D, *_ in data['ca']:
        if x > 1000:
            continue
        ps = [q for q in P if q <= x]
        a = R.exponents(math.log1p(1 / x) / math.log(x) * (1 - 1e-12), np.log(np.array(ps, float)))
        n = 1
        for q, k in zip(ps, a):
            n *= q ** int(k)
        sig = 1
        for q, k in zip(ps, a):
            sig *= (q ** (int(k) + 1) - 1) // (q - 1)
        s_over_n = Fraction(sig, n)
        ln = math.log(n)
        assert abs(ln - logn) < 1e-9 * logn
        assert abs(float(s_over_n) / math.log(ln) - ratio) < 1e-9
        assert abs((EG * math.log(ln) - float(s_over_n)) * math.sqrt(ln) - D) < 1e-9
        checked += 1
    print(f"The tools reproduce the page's data byte for byte: {len(data['exceptions'])} exceptions to Robin up to 10^7, "
          f"{data['primorial_count']:,} primorials, {len(data['ca'])} colossally abundant rows.")
    print(f"An independent sigma up to {N:,} finds the same exceptions, and [2] + them is OEIS A067698; the closest any "
          f"n comes to e^gamma is {closest[0]:.2e}, at {closest[1]}.")
    print(f"Exact running sums over the first 120,569 primorials: c(N_1) = {c[0]:.10f} and c(N_66) = {c[65]:.10f} as "
          f"Nicolas prints, c(N_66) the largest, and c(N_120568) = {c[120567]:.10f} > {limsup:.10f} > "
          f"c(N_120569) = {c[120568]:.10f}.")
    print(f"Exact sigma(n)/n confirms {checked} colossally abundant rows with x <= 1000.")


if __name__ == '__main__':
    main()
