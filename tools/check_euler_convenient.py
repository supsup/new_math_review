"""Replay for crew_visuals/euler_convenient_numbers.html (Confluence).

Two independent ways to find Euler's convenient (idoneal) numbers n:
  1. Grube's criterion (Kani 2011, Proposition 17(a)): n is convenient iff there is no primitive reduced form
     a x^2 + 2b xy + c y^2 with ac - b^2 = n and 0 < 2b < a < c (such a form and its mirror are distinct, mutually
     inverse classes, so the class group would have an element of order > 2).
  2. Genus count: count the classes h(-4n) (primitive reduced forms) and compare with the number of genera
     2^(mu - 1) (Cox, Primes of the form x^2 + ny^2, Proposition 3.11). n is convenient iff h(-4n) = 2^(mu - 1).
The two share no code. Then Euler's example 18,518,809 = 197^2 + 1848 * 100^2, and the 'fooling' numbers for
non-convenient n. Standard library only. Usage:  python3 tools/check_euler_convenient.py [grube_limit] [genus_limit]
(defaults 1,000,000 and 20,000; tools/idoneal_search.c runs criterion 1 to 5,000,000 in a fraction of a second).
"""

import sys
from math import gcd, isqrt

EULER65 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 18, 21, 22, 24, 25, 28, 30, 33, 37, 40, 42, 45, 48, 57, 58,
           60, 70, 72, 78, 85, 88, 93, 102, 105, 112, 120, 130, 133, 165, 168, 177, 190, 210, 232, 240, 253, 273, 280,
           312, 330, 345, 357, 385, 408, 462, 520, 760, 840, 1320, 1365, 1848]


def convenient_grube(n):
    a = 3
    while 3 * a * a <= 4 * n:
        for b in range(1, (a - 1) // 2 + 1):
            m = n + b * b
            if m % a == 0:
                c = m // a
                if c > a and gcd(gcd(a, 2 * b), c) == 1:
                    return False
        a += 1
    return True


def class_number(n):
    """Primitive reduced forms (a, B, c), B even, B^2 - 4ac = -4n, |B| <= a <= c, B >= 0 if |B| = a or a = c."""
    h, a = 0, 1
    while 3 * a * a <= 4 * n:
        for B in range(-a + (a % 2), a + 1, 2):
            num = B * B + 4 * n
            if num % (4 * a):
                continue
            c = num // (4 * a)
            if c < a or (B < 0 and (-B == a or a == c)) or gcd(gcd(a, B), c) != 1:
                continue
            h += 1
        a += 1
    return h


def genera(n):
    m, r = n, 0
    while m % 2 == 0:
        m //= 2
    p = 3
    while p * p <= m:
        if m % p == 0:
            r += 1
            while m % p == 0:
                m //= p
        p += 2
    if m > 1:
        r += 1
    mu = r if n % 4 == 3 else r + 1 if n % 4 in (1, 2) else r + 1 if n % 8 == 4 else r + 2
    return 2 ** (mu - 1)


def reps(n, m):
    out, y = [], 0
    while n * y * y <= m:
        r = m - n * y * y
        x = isqrt(r)
        if x * x == r:
            out.append((x, y))
        y += 1
    return out


def is_prime(m):
    if m < 2:
        return False
    if m % 2 == 0:
        return m == 2
    d = 3
    while d * d <= m:
        if m % d == 0:
            return False
        d += 2
    return True


def fooling(n, limit):
    for m in range(9, limit + 1, 2):
        if gcd(m, n) == 1 and not is_prime(m):
            r = reps(n, m)
            if len(r) == 1 and gcd(*r[0]) == 1:
                return m
    return None


def main():
    lim1 = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    lim2 = int(sys.argv[2]) if len(sys.argv) > 2 else 20_000
    by_grube = [n for n in range(1, lim1 + 1) if convenient_grube(n)]
    assert by_grube == EULER65, by_grube[:80]
    by_genus, multiple = [], True
    for n in range(1, lim2 + 1):
        h, g = class_number(n), genera(n)
        multiple &= (h % g == 0)
        if h == g:
            by_genus.append(n)
    assert multiple, 'h(-4n) not a multiple of the genus count'
    assert by_genus == [n for n in EULER65 if n <= lim2], by_genus
    assert reps(1848, 18518809) == [(197, 100)] and is_prime(18518809)
    assert fooling(11, 1000) == 15
    for n in EULER65[:30]:                       # convenient n: no fooling m below 20,000
        assert fooling(n, 20000) is None, n
    print(f"Grube's criterion up to {lim1:,}: exactly Euler's 65, the largest 1848.")
    print(f"Class number against genus count up to {lim2:,}: the same list, and h(-4n) is always a multiple of the genus count.")
    print("Euler's 18,518,809 = 197^2 + 1848 * 100^2 has one representation and is prime; for n = 11 the test is fooled by 15 = 2^2 + 11 * 1^2;")
    print("and for the first 30 convenient n, no odd composite below 20,000 fools the test.")


if __name__ == '__main__':
    main()
