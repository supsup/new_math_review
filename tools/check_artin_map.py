"""Replay for crew_visuals/artin_map_roots_of_unity.html (Confluence).

1. Run the page's own arithmetic (the JavaScript between MATH-BEGIN and MATH-END) in node, for every 3 <= n <= 60
   and every prime p < 300, and read back the degrees of the irreducible factors of Phi_n mod p (or of Phi_m, with
   n = p^k m, when p divides n), and whether Phi_n == Phi_m^e mod p.
2. Independently, in Python: Phi_n by exact integer division; the NUMBER of irreducible factors of Phi_m mod p by
   Berlekamp's method (the dimension of the kernel of Q - I, Q the matrix of the p-th power map modulo Phi_m, by
   Gaussian elimination mod p); and Phi_n == Phi_m^e mod p by direct multiplication.
3. The theorem the page illustrates: for p not dividing m, every factor has degree ord_m(p) and there are
   phi(m)/ord_m(p) of them. Both computations must agree with it and with each other.
4. Recount the primes the page's self-check quotes: 78,498 below 10^6, and 39,175 and 39,322 in the classes 1 and 3 mod 4.
Standard library and node. Usage:  python3 tools/check_artin_map.py
"""

import json
import re
import subprocess
import tempfile
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def primes_upto(N):
    sv = bytearray([1]) * (N + 1)
    sv[0:2] = b'\x00\x00'
    for i in range(2, int(N ** .5) + 1):
        if sv[i]:
            sv[i * i::i] = bytearray(len(range(i * i, N + 1, i)))
    return [i for i in range(N + 1) if sv[i]]


def phi(n):
    return sum(1 for a in range(1, n + 1) if gcd(a, n) == 1)


def order(a, n):
    x, k = a % n, 1
    while x != 1:
        x, k = x * a % n, k + 1
    return k


CYC = {}


def cyclotomic(n):
    if n not in CYC:
        num = [-1] + [0] * (n - 1) + [1]
        for d in range(1, n):
            if n % d == 0:
                b = cyclotomic(d)
                q = [0] * (len(num) - len(b) + 1)
                r = num[:]
                for i in range(len(r) - 1, len(b) - 2, -1):
                    c = r[i]
                    q[i - len(b) + 1] = c
                    for j, bj in enumerate(b):
                        r[i - len(b) + 1 + j] -= c * bj
                assert not any(r)
                num = q
        CYC[n] = num
    return CYC[n]


def polymulmod(a, b, p):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i + j] = (r[i + j] + x * y) % p
    return r


def polyrem(a, f, p):
    a = [x % p for x in a]
    D = len(f) - 1
    for i in range(len(a) - 1, D - 1, -1):
        c = a[i]
        if c:
            for j in range(D + 1):
                a[i - D + j] = (a[i - D + j] - c * f[j]) % p
    return (a[:D] + [0] * D)[:D]


def berlekamp_count(f, p):
    """Number of irreducible factors of the squarefree monic f mod p: dim ker(Q - I)."""
    D = len(f) - 1
    f = [x % p for x in f]
    X = polyrem([0] * p + [1], f, p) if p < 4 * D else None
    if X is None:
        X, base, e = [1] + [0] * (D - 1), polyrem([0, 1], f, p), p
        while e:
            if e & 1:
                X = polyrem(polymulmod(X, base, p), f, p)
            base = polyrem(polymulmod(base, base, p), f, p)
            e >>= 1
    rows, cur = [], [1] + [0] * (D - 1)
    for i in range(D):
        rows.append([(cur[j] - (1 if j == i else 0)) % p for j in range(D)])
        cur = polyrem(polymulmod(cur, X, p), f, p)
    rank, M = 0, [r[:] for r in rows]
    for col in range(D):
        piv = next((r for r in range(rank, D) if M[r][col]), None)
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        inv = pow(M[rank][col], p - 2, p)
        M[rank] = [x * inv % p for x in M[rank]]
        for r in range(D):
            if r != rank and M[r][col]:
                c = M[r][col]
                M[r] = [(x - c * y) % p for x, y in zip(M[r], M[rank])]
        rank += 1
    return D - rank


def main():
    page = (ROOT / 'crew_visuals' / 'artin_map_roots_of_unity.html').read_text()
    js = re.search(r'// MATH-BEGIN\n(.*?)// MATH-END', page, re.S).group(1)
    small = [q for q in primes_upto(300)]
    harness = js + '\nconst out = [];\nfor (let n = 3; n <= 60; n++) for (const p of ' + json.dumps(small) + \
        ') { const s = splitting(n, p); out.push([n, p, s.k, s.m, s.e, s.degs, s.congruent]); }\nconsole.log(JSON.stringify(out));\n'
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / 'h.js'
        f.write_text(harness)
        rows = json.loads(subprocess.run(['node', str(f)], check=True, capture_output=True, text=True).stdout)
    unram = ram = 0
    for n, p, k, m, e, degs, congruent in rows:
        kk, mm = 0, n
        while mm % p == 0:
            mm //= p
            kk += 1
        assert (k, m) == (kk, mm), (n, p)
        fdeg = 1 if m == 1 else order(p % m, m)
        want = [fdeg] * (phi(m) // fdeg)
        assert degs == want, (n, p, degs, want)
        assert berlekamp_count(cyclotomic(m), p) == len(want), (n, p)
        if k:
            ram += 1
            ee = phi(p ** k)
            assert e == ee and congruent
            lhs = [x % p for x in cyclotomic(n)]
            rhs = [1]
            for _ in range(ee):
                rhs = polymulmod(rhs, [x % p for x in cyclotomic(m)], p)
            assert lhs == rhs, (n, p)
        else:
            unram += 1
    P = primes_upto(10 ** 6)
    c1 = sum(1 for q in P if q % 4 == 1)
    c3 = sum(1 for q in P if q % 4 == 3)
    assert (len(P), c1, c3) == (78498, 39175, 39322)
    print(f"The page's own arithmetic, run in node, factors Phi_n mod p for {len(rows):,} pairs (3 <= n <= 60, p < 300): "
          f"{unram:,} unramified and {ram} ramified.")
    print("Every unramified factorization has phi(n)/ord_n(p) factors of degree ord_n(p), and Berlekamp's independent "
          "count agrees; every ramified one satisfies Phi_n == Phi_m^phi(p^k) mod p, checked again in Python.")
    print(f"Primes below 10^6: {len(P):,}; {c1:,} are 1 mod 4 and {c3:,} are 3 mod 4.")


if __name__ == '__main__':
    main()
