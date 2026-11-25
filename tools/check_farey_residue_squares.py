"""Exact reduced-residue and character checks for the Farey sums card."""

import argparse
import json
from fractions import Fraction
from math import gcd
from pathlib import Path

from check_farey_harmonics import MAX_HARMONIC, MAX_ORDER, primitive_packets


LIMIT = 240
# Each pair of rows gives the real and imaginary parts of a character.
ZERO = (0, 0, 0, 0)
PRINCIPAL = ((1, 1, 1, 1), ZERO)
CHARACTERS = {
    5: (PRINCIPAL, ((1, -1, -1, 1), ZERO),
        ((1, 0, 0, -1), (0, 1, -1, 0)), ((1, 0, 0, -1), (0, -1, 1, 0))),
    8: (PRINCIPAL, ((1, -1, 1, -1), ZERO),
        ((1, -1, -1, 1), ZERO), ((1, 1, -1, -1), ZERO)),
}


def mobius(n):
    sign = 1
    p = 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            if n % p == 0:
                return 0
            sign = -sign
        p += 1
    return -sign if n > 1 else sign


def check():
    phi = [0] + [sum(gcd(a, q) == 1 for a in range(1, q + 1)) for q in range(1, LIMIT + 1)]
    cyclotomic = primitive_packets()
    result = {}
    for modulus, characters in CHARACTERS.items():
        residues = [r for r in range(1, modulus) if gcd(r, modulus) == 1]
        by_residue = {r: i for i, r in enumerate(residues)}
        for k in range(1, MAX_HARMONIC + 1):
            buckets = [0] * len(residues)
            for n in range(1, LIMIT + 1):
                quotient = n // gcd(n, k)
                packet = mobius(quotient) * (phi[n] // phi[quotient])
                if n <= MAX_ORDER:
                    assert packet == cyclotomic[n, k]
                if n % modulus in by_residue:
                    buckets[by_residue[n % modulus]] += packet
                if n == 1:
                    continue
                projections = [[sum(w * a for w, a in zip(weights, buckets)) for weights in chi]
                               for chi in characters]
                principal = sum(buckets) ** 2
                full = len(residues) * sum(v * v for v in buckets)
                differences = sum((a - b) ** 2 for i, a in enumerate(buckets) for b in buckets[i + 1:])
                centered = [v - Fraction(sum(buckets), len(residues)) for v in buckets]
                assert full == sum(a * a + b * b for a, b in projections)
                assert full == principal + differences
                assert differences == len(residues) * sum(v * v for v in centered)
                assert differences == sum(a * a + b * b for a, b in projections[1:])
                if modulus == 8:
                    a, b, c, d = buckets
                    primitive = sum(x * x + y * y for x, y in projections[2:])
                    assert primitive == 2 * ((a - c) ** 2 + (b - d) ** 2)
                result[f"{modulus},{n},{k}"] = [buckets[:], projections, principal, differences]
    assert result["5,2,1"] == [[1, -1, 0, 0], [[0, 0], [2, 0], [1, -1], [1, 1]], 0, 8]
    assert result["5,179,2"][2:] == [225, 11]
    assert result["8,83,3"][2:] == [625, 19]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="write expected display values")
    args = parser.parse_args()
    cases = check()
    if args.json:
        args.json.write_text(json.dumps(cases), encoding="utf-8")
    print(f"{len(cases):,} exact residue, character, and centering comparisons agree.")
