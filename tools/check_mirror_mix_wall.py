"""Prove the uniform 5/2 wall with rational arithmetic and a short sum."""

from fractions import Fraction
from math import isqrt


SCALE = 100
KAPPA_LOWER = Fraction(71, 250)
ODD_WEIGHT_UPPER = 1 / KAPPA_LOWER


def sqrt_lower(n):
    return Fraction(isqrt(SCALE*SCALE*n), SCALE)


def tail_bound(side):
    """Upper bounds for the two residue classes through side² and the rest."""
    units = larger = Fraction()
    last = side*side
    for n in range(2, last+1):
        weight = Fraction(1, n*n) / sqrt_lower(n)
        if n % 5 in (1, 4):
            units += weight
        elif n % 5 in (2, 3):
            larger += weight * ODD_WEIGHT_UPPER
    remainder = Fraction(2, 3*last*side) * ODD_WEIGHT_UPPER
    return units, larger, remainder


def check():
    # cos²(phi) = (5 + sqrt(5))/10 and kappa² = (1 - cos(phi))/(1 + cos(phi)).
    root5_upper = Fraction(22361, 10000)
    assert root5_upper**2 > 5
    cosine_squared_upper = (5 + root5_upper) / 10
    cosine_threshold = (1 - KAPPA_LOWER**2) / (1 + KAPPA_LOWER**2)
    assert 0 < cosine_threshold and cosine_squared_upper < cosine_threshold**2

    parts = tail_bound(4)
    bound = sum(parts)
    assert bound < Fraction(9984, 10000) < 1
    assert sum(tail_bound(3)) > 1  # The shorter estimate cannot prove the wall.
    print("Uniform normalized coefficient bound on residues ±2: less than 250/71.")
    print("Through n=16, these are the upper bounds for ±1, ±2, and the rest:")
    print(", ".join(f"{float(term):.10f}" for term in parts))
    print(f"Total {float(bound):.10f} < 0.9984 < 1 at real part 5/2.")


if __name__ == "__main__":
    check()
