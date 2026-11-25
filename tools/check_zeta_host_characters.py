"""Check the host-field splitting formulas by enumerating finite Galois quotients."""

from math import gcd, lcm

Q, D = 11, 263
# Dyadic modulus, exponents of its character, odd modulus, exponents of
# its character, odd image order. Zero divisors are omitted from each map.
CHARACTERS = [
    (1, {0: 0}, 1, {0: 0}, 1),
    (1, {0: 0}, 5, {1: 0, 2: 1, 3: 1, 4: 0}, 2),
    (1, {0: 0}, 5, {1: 0, 2: 1, 4: 2, 3: 3}, 4),
    (1, {0: 0}, 7, {pow(3, j, 7): j % 3 for j in range(6)}, 3),
    (4, {1: 0, 3: 1}, 1, {0: 0}, 1),
    (8, {1: 0, 3: 1, 5: 1, 7: 0}, 1, {0: 0}, 1),
    (4, {1: 0, 3: 1}, 7, {pow(3, j, 7): j % 3 for j in range(6)}, 3),
]
PRIMES = (3, 5, 7, 13, 17, 19, 31, 41, 73, 97)


def valuation(n):
    return (n & -n).bit_length() - 1


def multiply(a, b, M, roots):
    # The dyadic coordinate is represented up to sign by the residue 1 mod 4.
    return (a[0] * b[0] % M, (a[1] + b[1]) % roots,
            (a[2] + b[2]) % 2, (a[3] + b[3]) % 2)


def image_element(a2, ao, qsign, dsign, M, character):
    dyadic, left, _, right, odd_order = character
    two_order = 1 if dyadic == 1 else 2
    roots = lcm(two_order, odd_order)
    # Choose the sign of the dyadic *coordinate* only. The original unit
    # is still used in the character entry, which can distinguish it.
    representative = a2 if a2 % 4 == 1 else (-a2) % M
    exponent = (left[a2 % dyadic] * (roots // two_order)
                + right[ao] * (roots // odd_order)) % roots
    return representative, exponent, qsign, dsign


def check():
    cases = 0
    q_squares = {a * a % Q for a in range(1, Q)}
    d_squares = {a * a % D for a in range(1, D)}
    for character in CHARACTERS:
        dyadic, left, odd, right, odd_order = character
        roots = lcm(1 if dyadic == 1 else 2, odd_order)
        relative = lcm(1 if left[-1 % dyadic] == 0 else 2, odd_order)
        for e in range(1, 9):
            M = 2 ** (e + 2)
            image = {image_element(a2, ao, x, y, M, character)
                     for a2 in range(1, M, 2) for ao in right
                     for x in (0, 1) for y in (0, 1)}
            assert len(image) == M * relative
            for prime in PRIMES:
                if gcd(prime, odd) != 1:
                    continue
                element = image_element(prime % M, prime % odd,
                                        int(prime % Q not in q_squares),
                                        int(prime % D not in d_squares), M, character)
                identity = (1, 0, 0, 0)
                power, order = element, 1
                while power != identity:
                    power = multiply(power, element, M, roots)
                    order += 1
                    assert order <= len(image)
                v = max(valuation(prime - 1), valuation(prime + 1))
                f_real = 2 ** max(0, e + 2 - v)
                f_character = roots // gcd(roots, element[1])
                expected = lcm(f_real, f_character, 1 + int(bool(element[2] or element[3])))
                assert order == expected, (character, e, prime, order, expected)
                if f_real >= max(2, 2 ** valuation(f_character)):
                    odd_part = f_character >> valuation(f_character)
                    assert len(image) // order == (2**v * relative) // odd_part
                cases += 1
    print(f"{cases} finite quotient orders and stabilized prime counts agree.")


if __name__ == "__main__":
    check()
