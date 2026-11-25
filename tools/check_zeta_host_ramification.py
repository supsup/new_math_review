"""Exact local-factor replay for the ramified-prime host field card.

Requires python-flint. The cyclotomic factor degrees come from finite-field
factorization, independently of the order/valuation formulas on the page.
"""

from math import lcm

from flint import fmpz_poly, nmod_poly


PAIRS = [(11, 263), (19, 1367), (43, 1031)]
X = fmpz_poly([0, 1])


def residue_degree(polynomial, p):
    """For a squarefree reduction, return the common residue degree."""
    _, factors = nmod_poly(polynomial.coeffs(), p).factor()
    assert factors and all(multiplicity == 1 for _, multiplicity in factors)
    degrees = {factor.degree() for factor, _ in factors}
    assert len(degrees) == 1
    return degrees.pop()


def eisens_at(polynomial, p):
    coeffs = polynomial.coeffs()
    return (coeffs[-1] % p != 0 and coeffs[0] % (p * p) != 0
            and all(coefficient % p == 0 for coefficient in coeffs[:-1]))


def quadratic(prime):
    # Minimal polynomial of (1 + sqrt(-prime)) / 2.
    return X**2 - X + (prime + 1) // 4


def check():
    cases = 0
    real = X  # the tower starts with Q and 2 cos(2*pi/4) = 0
    for e in range(9):
        assert real.degree() == 2**e
        if e:
            assert eisens_at(real, 2)
        for q, d in PAIRS:
            assert q % 8 == 3 and d % 16 == 7 and (d + 1) % q == 0
            assert eisens_at(X**2 + q, q)
            assert eisens_at(X**2 + d, d)
            rows = [
                # At 2 the real tower is totally ramified and the two
                # quadratic factors are unramified. At either odd conductor
                # prime, the real tower and the other quadratic are unramified.
                (2**e, lcm(residue_degree(quadratic(q), 2),
                            residue_degree(quadratic(d), 2))),
                (2, lcm(residue_degree(real, q), residue_degree(quadratic(d), q))),
                (2, lcm(residue_degree(real, d), residue_degree(quadratic(q), d))),
            ]
            degree = 2**(e + 2)
            triples = [(r, f, degree // (r * f)) for r, f in rows]
            assert all(r * f * g == degree for r, f, g in triples)
            at_d = 2**max(1, e - 1)
            expected = [(2**e, 2, 2), (2, 2**e, 2), (2, at_d, degree // (2 * at_d))]
            assert triples == expected, (e, q, d, triples)
            cases += len(rows)
        real = real(X**2 - 2)
    print(f"{cases} exact triples agree across three families and tower steps e=0…8.")


if __name__ == "__main__":
    check()
