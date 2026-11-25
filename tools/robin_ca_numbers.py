"""Colossally abundant numbers far out, for crew_visuals/robin_and_nicolas.html (Confluence).

For a prime x take eps = log(1 + 1/x)/log x, the critical value at which x enters with exponent 1, and build the
colossally abundant number n = prod p^a_p with a_p = floor(log((p^(1+eps) - 1)/(p^eps - 1))/log p) - 1
(Alaoglu and Erdos). Work in logarithms: log n = sum a_p log p and log(sigma(n)/n) = sum log((1 - p^-(a_p+1))/(1 - 1/p)).
Print, as JSON, [x, log n, sigma(n)/(n log log n), D, T1, T2, c'] for about 110 primes x up to 10^7, where
D = (e^gamma log log n - sigma(n)/n) sqrt(log n) and, with N the primorial of x, theta = log N,
Delta = log n - theta and Pi = prod (1 - p^-(a_p+1)), the exact split D = T1 + T2 - c' has
T1 = sqrt(log n) e^gamma log(1 + Delta/theta), T2 = sqrt(log n) (N/phi(N)) (1 - Pi) and c' = c(N) sqrt(log n/theta),
c(N) = (N/phi(N) - e^gamma log theta) sqrt(theta) being Nicolas's quantity. Also check the construction: the critical values give exactly the first 24 colossally abundant
numbers of OEIS A004490. Needs numpy.  Usage:  python3 tools/robin_ca_numbers.py
"""

import json
import math

import numpy as np

EG = math.exp(0.5772156649015329)
OEIS_A004490 = [2, 6, 12, 60, 120, 360, 2520, 5040, 55440, 720720, 1441440, 4324320, 21621600, 367567200, 6983776800,
                160626866400, 321253732800, 9316358251200, 288807105787200, 2021649740510400, 6064949221531200,
                224403121196654400, 9200527969062830400, 395622702669701707200]


def exponents(eps, lp):
    return np.maximum(np.floor(np.log(np.expm1((1 + eps) * lp) / np.expm1(eps * lp)) / lp + 1e-9) - 1, 0)


def small_check():
    P = np.array([p for p in range(2, 200) if all(p % q for q in range(2, int(p ** .5) + 1))], float)
    lp = np.log(P)
    crit = sorted({e for p in P[:25] for a in range(1, 14)
                   for e in [math.log((p ** (a + 1) - 1) / (p ** (a + 1) - p)) / math.log(p)] if e > 1e-3}, reverse=True)
    seen = []
    for e in crit:
        a = exponents(e * (1 - 1e-12), lp)
        n = 1
        for i in range(len(P)):
            n *= int(P[i]) ** int(a[i])
        if n > 4e20:
            break
        if n > 1 and n not in seen:
            seen.append(n)
    assert sorted(seen) == OEIS_A004490, sorted(seen)


def far_out(N=10_000_000):
    sv = np.ones(N + 1, bool)
    sv[:2] = False
    for i in range(2, int(N ** .5) + 1):
        if sv[i]:
            sv[i * i::i] = False
    P = np.nonzero(sv)[0].astype(np.float64)
    lp = np.log(P)
    out = []
    for i in np.unique(np.round(np.geomspace(10, len(P) - 1, 110)).astype(int)):
        x = P[i]
        l = lp[:i + 1]
        a = exponents(math.log1p(1 / x) / math.log(x) * (1 - 1e-12), l)
        theta = math.fsum(l)
        delta = math.fsum((a - 1) * l)
        logn = theta + delta
        nphi = math.exp(math.fsum(-np.log1p(-1 / P[:i + 1])))
        logpi = math.fsum(np.log1p(-np.exp(-(a + 1) * l)))
        s = nphi * math.exp(logpi)
        D = (EG * math.log(logn) - s) * math.sqrt(logn)
        T1 = math.sqrt(logn) * EG * math.log1p(delta / theta)
        T2 = math.sqrt(logn) * nphi * -math.expm1(logpi)
        cp = (nphi - EG * math.log(theta)) * math.sqrt(theta) * math.sqrt(logn / theta)
        assert abs(T1 + T2 - cp - D) < 1e-9, (x, T1 + T2 - cp - D)
        out.append([int(x), logn, s / math.log(logn), D, T1, T2, cp])
    return out


if __name__ == '__main__':
    small_check()
    print(json.dumps(far_out(), separators=(',', ':')))
