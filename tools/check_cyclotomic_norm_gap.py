"""Check the moment norms and ideal roots in crew_visuals/cyclotomic_norm_gap.html."""

import argparse
import json
import subprocess
from fractions import Fraction
from math import isqrt


def prime_factors(n):
    """Return the distinct prime factors of a positive integer."""
    factors = []
    for p in range(2, isqrt(n) + 1):
        if p * p > n:
            break
        if n % p == 0:
            factors.append(p)
            while n % p == 0:
                n //= p
    if n > 1:
        factors.append(n)
    return factors


def generator(p):
    return next(g for g in range(2, p)
                if all(pow(g, (p - 1) // q, p) != 1 for q in prime_factors(p - 1)))


def remainder(coefficients, modulus):
    """Reduce an integer coefficient vector by a monic polynomial."""
    coeffs = list(coefficients) + [0] * max(0, len(modulus) - 1 - len(coefficients))
    degree = len(modulus) - 1
    for i in range(len(coeffs) - 1, degree - 1, -1):
        lead = coeffs[i]
        for j in range(degree):
            coeffs[i - degree + j] -= lead * modulus[j]
    return coeffs[:degree]


def determinant(matrix):
    """Fraction-free elimination with pivoting over the integers."""
    matrix = [row[:] for row in matrix]
    sign = divider = 1
    for k in range(len(matrix) - 1):
        pivot_row = next((i for i in range(k, len(matrix)) if matrix[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            matrix[k], matrix[pivot_row] = matrix[pivot_row], matrix[k]
            sign = -sign
        pivot = matrix[k][k]
        for i in range(k + 1, len(matrix)):
            for j in range(k + 1, len(matrix)):
                numerator = matrix[i][j] * pivot - matrix[i][k] * matrix[k][j]
                matrix[i][j], leftover = divmod(numerator, divider)
                assert leftover == 0
            matrix[i][k] = 0
        divider = pivot
    return sign * matrix[-1][-1]


def norm(coefficients, modulus):
    degree = len(modulus) - 1
    columns = [remainder([0] * i + coefficients, modulus) for i in range(degree)]
    return determinant(list(map(list, zip(*columns))))


def moment(p, order, modulus):
    """Return the half-moment S/2 in the power basis and the chosen generator."""
    g = generator(p)
    buckets = [0] * order
    a = 1
    for k in range(p - 1):
        buckets[k % order] += a
        a = a * g % p
    assert a == 1
    reduced = remainder(buckets, modulus)
    assert all(c % 2 == 0 for c in reduced)
    return [c // 2 for c in reduced], g


def evaluate_mod(coefficients, root, p):
    result = 0
    for c in reversed(coefficients):
        result = (result * root + c) % p
    return result


def primitive_roots_of_order(order, p):
    g = generator(p)
    factors = prime_factors(order)
    return [pow(g, k * ((p - 1) // order), p) for k in range(1, order)
            if all(k % q != 0 for q in factors)]


def multiply(a, b, modulus):
    product = [0] * (len(a) + len(b) - 1)
    for i, coeff_a in enumerate(a):
        for j, coeff_b in enumerate(b):
            product[i + j] += coeff_a * coeff_b
    return remainder(product, modulus)


def power_substitution(coefficients, exponent, modulus):
    powers = [0] * 46
    for i, c in enumerate(coefficients):
        powers[i * exponent % 46] += c
    return remainder(powers, modulus)


def quadratic_certificate(half_moment, modulus):
    """Take the product of the 11 conjugates fixing the quadratic subfield."""
    product = [1]
    for k in range(1, 46, 2):
        if pow(k, 11, 23) == 1:
            conjugate = power_substitution(half_moment, k, modulus)
            product = multiply(product, conjugate, modulus)
    gauss_sum = [0] * 46
    for k in range(1, 23):
        gauss_sum[2 * k] = 1 if pow(k, 11, 23) == 1 else -1
    tau = remainder(gauss_sum, modulus)
    assert multiply(tau, tau, modulus) == [-23] + [0] * 21
    # For omega = (1 + tau) / 2, the numerator -59+28*omega is -45+14*tau.
    numerator = [14 * c for c in tau]
    numerator[0] -= 45
    assert product == [47**10 * c for c in numerator]


def square_candidates(n):
    return [4 * n - 23 * b * b for b in range(isqrt((4 * n) // 23) + 1)]


def check_exception():
    phi46 = [(-1)**i for i in range(23)]
    half_moment, g = moment(47, 46, phi46)
    fraction = Fraction(norm(half_moment, phi46), 47**22)
    assert g == 5 and fraction == Fraction(139, 47)
    pole = [r for r in primitive_roots_of_order(46, 47)
            if evaluate_mod(half_moment, r, 47) != 0]
    zero = [r for r in primitive_roots_of_order(46, 139)
            if evaluate_mod(half_moment, r, 139) == 0]
    assert pole == [19] and zero == [60]
    quadratic_certificate(half_moment, phi46)
    assert 45**2 + 23 * 14**2 == 47 * 139
    print("h=46, p=47: N(S/(2p)) = 139/47, pole at 19 and zero at 60.")
    print("Norm down to the quadratic subfield: (-45+14*sqrt(-23))/47.")
    for prime in (47, 139):
        candidates = square_candidates(prime)
        assert all(isqrt(v)**2 != v for v in candidates)
        print(f"Norm {prime} in Q(sqrt(-23)) would require a square among {candidates}.")
    assert square_candidates(47 * 139)[28] == 90**2


def check_order_twelve():
    phi12 = [1, 0, -1, 0, 1]
    samples = {13: Fraction(1, 13), 37: 1, 61: 1, 109: 1, 157: 13,
               181: 37, 229: 13, 277: 16}
    for p, expected in samples.items():
        half_moment, _ = moment(p, 12, phi12)
        moment_norm = Fraction(norm(half_moment, phi12), p**4)
        assert moment_norm == expected
        quotient = moment_norm * (p if p == 13 else 1)
        print(f"h=12, p={p}: N(S/(2p)) = {moment_norm}, quotient = {quotient}.")
    witnesses = {4: [1, 0, 0, 1], 9: [0, 1, 0, 1], 13: [0, 0, 1, 2],
                 25: [1, 0, 0, 2], 49: [0, 1, 0, 2], 121: [0, 2, 1, 2]}
    for value, coefficients in witnesses.items():
        assert norm(coefficients, phi12) == value
    print(f"Verified {len(witnesses)} explicit norms in Q(zeta_12).")


def certify_smaller_orders(gp):
    command = ("forstep(h=2,44,2,b=bnfinit(polcyclo(h),1); "
               "print([h,b.no,bnfcertify(b)]))\n")
    result = subprocess.run([gp, "-fq", "-s", "256M"], input=command,
                            capture_output=True, text=True, check=True)
    rows = [json.loads(row) for row in result.stdout.splitlines()]
    assert rows == [[h, 1, 1] for h in range(2, 45, 2)], result.stderr
    print("Certified class number one at all 22 smaller even orders.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gp", metavar="EXECUTABLE",
                        help="certify class number one for the smaller orders with PARI/GP")
    args = parser.parse_args()
    check_exception()
    check_order_twelve()
    if args.gp:
        certify_smaller_orders(args.gp)


if __name__ == "__main__":
    main()
