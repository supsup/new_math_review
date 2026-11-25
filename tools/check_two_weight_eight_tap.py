"""Verify the shortest eight-tap board with positive weights 1 and 2.

The class requires ordinary invertibility, modular corank seven over a
prime, and recovery from any seven direct probes. See two_weight_mixer.html.
"""

from collections import Counter
from itertools import combinations
from math import isqrt

from flint import fmpz_poly, nmod_mat, nmod_poly


def circle_coefficients(n):
    return [-1] + [0] * (n - 1) + [1]


def possible_fields(n):
    fields = {}
    for doubles in range(9):
        weight = 8 + doubles
        square_norm = 8 + 3 * doubles
        bound = (n * square_norm - weight**2)**(n - 1)
        scale = (n - 1)**(n - 1)
        p = max(8, n - 6)
        while p**12 * scale <= bound:
            prime = all(p % k != 0 for k in range(2, isqrt(p) + 1))
            exponent = 2 * (7 - int(weight % p == 0))
            if prime and p**exponent * scale <= bound:
                fields.setdefault(doubles, []).append(p)
            p += 1
    return fields


def kernel_basis(n, generator):
    return [[int(generator[j - i]) if j >= i else 0 for j in range(n)] for i in range(7)]


def probe_minor(basis, positions, p):
    return nmod_mat([[row[j] for j in positions] for row in basis], p).det()


def reject_smaller(n):
    fields = possible_fields(n)
    circle = fmpz_poly(circle_coefficients(n))
    modular = Counter()
    ordinary = Counter()
    for doubles, primes in fields.items():
        circles = {p: nmod_poly(circle_coefficients(n), p) for p in primes}
        for rest in combinations(range(1, n), 7):
            # Rotating one tap to the origin preserves both rank tests and
            # the recovery property, so it suffices to put a tap at zero.
            taps = (0, *rest)
            for doubled in combinations(taps, doubles):
                coefficients = [0] * n
                for k in taps:
                    coefficients[k] = 1
                for k in doubled:
                    coefficients[k] = 2
                for p, circle_mod in circles.items():
                    gcd = nmod_poly(coefficients, p).gcd(circle_mod)
                    if gcd.degree() != 7:
                        continue
                    modular[p] += 1
                    if fmpz_poly(coefficients).gcd(circle).degree() != 0:
                        continue
                    ordinary[p] += 1
                    basis = kernel_basis(n, circle_mod // gcd)
                    failing = next(((0, *rest) for rest in combinations(range(1, n), 6)
                                    if probe_minor(basis, (0, *rest), p) == 0), None)
                    assert failing is not None, (n, p, coefficients)
    assert modular == {14: {11: 20}, 15: {11: 64}}.get(n, {}), (n, modular)
    assert ordinary == {15: {11: 64}}.get(n, {}), (n, ordinary)
    print(f'{n}: {sum(modular.values())} modular rank hits, {sum(ordinary.values())} also '
          'rationally invertible, none pass every probe set.')


def verify_board():
    n, p, root = 16, 17, 3
    coefficients = [0] * n
    coefficients[0] = 1
    for offset in (1, 2, 3, 5, 8, 9, 14):
        coefficients[offset] = 2
    assert coefficients[0] == 1 and all(c % 2 == 0 for c in coefficients[1:])
    addresses = [pow(root, k, p) for k in range(n)]
    assert len(set(addresses)) == n and pow(root, n, p) == 1
    polynomial = nmod_poly(coefficients, p)
    assert [k for k, address in enumerate(addresses) if polynomial(address) == 0] == list(range(1, 8))
    circle = nmod_poly(circle_coefficients(n), p)
    gcd = polynomial.gcd(circle)
    assert gcd.degree() == 7
    basis = kernel_basis(n, circle // gcd)
    checks = 0
    for positions in combinations(range(n), 7):
        assert probe_minor(basis, positions, p) != 0, positions
        checks += 1
    print(f'16: rank 9 modulo 17, invertible modulo 2, all {checks:,} seven-probe minors nonzero.')


if __name__ == '__main__':
    for n in range(9, 16):
        reject_smaller(n)
    verify_board()
