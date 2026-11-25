"""Check the host-field card with exact polynomial factors (requires python-flint)."""

from math import gcd, isqrt, lcm
from flint import fmpz_poly, nmod_poly

PAIRS = [(11, 263), (19, 1367), (43, 1031)]
PRIMES = [p for p in range(3, 331, 2) if all(p % d for d in range(3, isqrt(p)+1, 2))]
X = fmpz_poly([0, 1])


def join_sqrt_minus(poly, q):
    """F(X + Y) F(X - Y) evaluated at Y^2 = -q."""
    even, odd = fmpz_poly(), fmpz_poly()
    for coefficient in reversed(poly.coeffs()):
        even, odd = X * even - q * odd + coefficient, even + X * odd
    return even**2 + q * odd**2


def valuation(n):
    return (n & -n).bit_length() - 1


def conductor_exponents(e):
    """Find minimal 2-power conductor for each character by its kernel."""
    order = 2**e
    modulus = 4 * order
    units_up_to_sign = [pow(5, i, modulus) for i in range(order)]
    # On the sign quotient, each residue class has a representative 1 mod 4.
    # Factoring through reduction modulo 2^k means the character kills this kernel.
    kernel_generator = {}
    for k in range(2, e+3):
        kernel = [i for i, unit in enumerate(units_up_to_sign) if (unit - 1) % 2**k == 0]
        kernel_generator[k] = gcd(order, *kernel)
    return sum(next(k for k, g in kernel_generator.items() if (character * g) % order == 0)
               for character in range(1, order))


def main():
    for e in range(9):
        assert conductor_exponents(e) == (e+1)*2**e - 1
    tests = 0
    repeats = 0
    real = X
    for e in range(7):
        degree = 2**(e+2)
        for q, d in PAIRS:
            for weight in [1, 2, 3]:
                poly = join_sqrt_minus(join_sqrt_minus(real, weight**2 * q), d)
                assert poly.degree() == degree
                for p in PRIMES:
                    if p in (q, d):
                        continue
                    f = 2**max(0, e+2-max(valuation(p-1), valuation(p+1)))
                    f = lcm(f, 1 if pow(p, (q-1)//2, q) == 1 else 2,
                            1 if pow(p, (d-1)//2, d) == 1 else 2)
                    factors = nmod_poly(poly.coeffs(), p).factor()[1]
                    # Dedekind gives field factors when the polynomial is squarefree at p.
                    if any(multiplicity > 1 for _, multiplicity in factors):
                        repeats += 1
                        continue
                    assert [factor.degree() for factor, _ in factors] == [f] * (degree // f)
                    tests += 1
        real = real(X**2 - 2)
    print(f"{tests} squarefree polynomial reductions agreed. Skipped {repeats} repeated reductions.")


if __name__ == "__main__":
    main()
