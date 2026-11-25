"""Check the Farey harmonic determinant with exact integer arithmetic.

Each packet of primitive roots is reduced modulo its cyclotomic polynomial
rather than evaluated with floating point. Bareiss elimination computes a
separate determinant. The character choices match farey_harmonics.html.
"""

from math import gcd

MAX_ORDER = 42
MAX_HARMONIC = 24


def trim(coefficients):
    while coefficients and coefficients[-1] == 0:
        coefficients.pop()
    return coefficients


def divide_monic(dividend, divisor):
    """Divide integer coefficient lists, stored lowest degree first."""
    remainder = trim(dividend[:])
    quotient = [0] * max(0, len(remainder) - len(divisor) + 1)
    while len(remainder) >= len(divisor):
        shift = len(remainder) - len(divisor)
        factor = remainder[-1]
        quotient[shift] = factor
        for i, coefficient in enumerate(divisor):
            remainder[shift + i] -= coefficient * factor
        trim(remainder)
    return trim(quotient), remainder


def primitive_packets():
    cyclotomic = {}
    packets = {}
    for q in range(1, MAX_ORDER + 1):
        polynomial = [-1] + [0] * (q - 1) + [1]
        for d in range(1, q):
            if q % d == 0:
                polynomial, remainder = divide_monic(polynomial, cyclotomic[d])
                assert not remainder
        cyclotomic[q] = polynomial
        units = [a for a in range(1, q + 1) if gcd(a, q) == 1]
        for k in range(1, MAX_HARMONIC + 1):
            counts = [0] * q
            for a in units:
                counts[(k * a) % q] += 1
            _, remainder = divide_monic(counts, polynomial)
            assert len(remainder) <= 1, (q, k, remainder)
            packets[q, k] = remainder[0] if remainder else 0
    return packets


def determinant(rows):
    """Fraction-free elimination with exact division and row pivoting."""
    matrix = [row[:] for row in rows]
    sign, previous = 1, 1
    for i in range(len(rows) - 1):
        pivot_row = next((j for j in range(i, len(rows)) if matrix[j][i]), None)
        if pivot_row is None:
            return 0
        if pivot_row != i:
            sign = -sign
            matrix[i], matrix[pivot_row] = matrix[pivot_row], matrix[i]
        pivot = matrix[i][i]
        for j in range(i + 1, len(rows)):
            for k in range(i + 1, len(rows)):
                value = matrix[j][k] * pivot - matrix[j][i] * matrix[i][k]
                matrix[j][k], remainder = divmod(value, previous)
                assert remainder == 0
            matrix[j][i] = 0
        previous = pivot
    return sign * matrix[-1][-1]


def binary_board(rows, conductor, character):
    """Use one triangular block to encode the entire integer first column."""
    n = len(rows)
    signs = []
    for i in range(1, n + 1):
        part = i
        while gcd(part, conductor) != 1:
            part //= gcd(part, conductor)
        signs.append(character(part))
    first = [sign * row[0] for sign, row in zip(signs, rows)]
    width = max(abs(value) for value in first).bit_length()

    # In the solution h of T h = e_0, the diagonal is 1 and each
    # new row sets its value to the negative sum of earlier values.
    earlier = [[], [0]]
    index = {1: 0, -1: 1}
    if width > 1:
        positives = [0, len(earlier)]
        earlier.append([1])
        for bit in range(1, width):
            power = 1 << bit
            index[-power] = len(earlier)
            earlier.append(positives[:])
            index[power] = len(earlier)
            earlier.append([index[-power]])
            positives.append(index[power])

    m = len(earlier)
    result = []
    for i, value in enumerate(first):
        row = [0] + [signs[i] * rows[i][j] * signs[j] for j in range(1, n)] + [0] * m
        for bit in range(width):
            digit = 1 << bit
            if abs(value) & digit:
                helper = -digit if value > 0 else digit
                row[n + index[helper]] = 1
        result.append(row)
    for i, depends_on in enumerate(earlier):
        row = [0] * (n + m)
        row[n + i] = 1
        row[0] = int(i == 0)
        for j in depends_on:
            row[n + j] = 1
        result.append(row)
    return result


def mobius_prefix(character):
    mobius = [0, 1]
    for n in range(2, MAX_ORDER + 1):
        mobius.append(-sum(mobius[d] for d in range(1, n) if n % d == 0))
    mertens = [0]
    for n, mu in enumerate(mobius[1:], 1):
        mertens.append(mertens[-1] + mu * character(n))
    return mertens


def check():
    packets = primitive_packets()
    cases = 0
    for conductor, character in ((1, lambda _: 1), (5, lambda q: (0, 1, -1, -1, 1)[q % 5])):
        prefix = mobius_prefix(character)
        for n in range(2, MAX_ORDER + 1):
            for k in range(1, MAX_HARMONIC + 1):
                divisors = [d for d in range(1, min(n, k) + 1) if k % d == 0]
                circle = sum(character(q) * packets[q, k] for q in range(1, n + 1))
                from_mertens = sum(d * character(d) * prefix[n // d] for d in divisors)
                assert circle == from_mertens, (n, k, circle, from_mertens)
                rows = [
                    [sum(d * character(d) for d in divisors if d * i <= n)] +
                    [character(j // i) if j % i == 0 else 0 for j in range(2, n + 1)]
                    for i in range(1, n + 1)
                ]
                assert determinant(rows) == circle, (n, k, circle)
                binary = binary_board(rows, conductor, character)
                assert all(entry in (0, 1) for row in binary for entry in row)
                assert determinant(binary) == circle, (conductor, n, k, circle)
                cases += 1
    print(f"{cases:,} exact circle sums, Möbius combinations, and both determinants agree.")


if __name__ == "__main__":
    check()
