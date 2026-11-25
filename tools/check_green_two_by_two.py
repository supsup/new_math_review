"""Replay the smallest nontrivial instance of the archive's Green premise."""

from fractions import Fraction
from itertools import combinations, product


VECTORS = ((1, 0), (0, 1), (1, 1))
IDENTITY = (1, 0, 0, 1)
SHEAR = (1, 1, 0, 1)


def action(matrix):
    a, b, c, d = matrix
    return tuple(VECTORS.index(((a*x + b*y) % 2, (c*x + d*y) % 2)) for x, y in VECTORS)


def characters(permutation):
    inversions = sum(permutation[i] > permutation[j] for i, j in combinations(range(3), 2))
    fixed_points = sum(i == image for i, image in enumerate(permutation))
    return 1, (-1)**inversions, fixed_points - 1


def check():
    matrices = [(a, b, c, d) for a, b, c, d in product(range(2), repeat=4) if (a*d-b*c) % 2]
    permutations = [action(matrix) for matrix in matrices]
    assert len(matrices) == len(set(permutations)) == 6

    table = {matrix: characters(permutation) for matrix, permutation in zip(matrices, permutations)}
    degrees = table[IDENTITY]
    assert degrees == (1, 1, 2) and sum(d*d for d in degrees) == len(matrices)
    for i, j in product(range(3), repeat=2):
        assert Fraction(sum(row[i]*row[j] for row in table.values()), len(matrices)) == (i == j)

    shear_ranks = [Fraction(a + b, 2) for a, b in zip(degrees, table[SHEAR])]
    assert shear_ranks == [1, 0, 1]
    labels = [(a, b) for a, b in product(range(2), repeat=2)
              if b and all((t*t + a*t + b) % 2 for t in range(2))]
    assert labels == [(1, 1)]  # T² + T + 1 is the only quadratic label.

    irreducible_class = [matrix for matrix in matrices
                         if ((matrix[0]+matrix[3]) % 2, 1) in labels]
    # Coordinates in the complex basis (1, ω) over Q, using ω² = −1 − ω.
    omega, omega_squared = (0, 1), (-1, -1)
    green_trace = tuple(-a-b for a, b in zip(omega, omega_squared))
    assert len(irreducible_class) == 2
    assert all((table[matrix][1], 0) == green_trace for matrix in irreducible_class)
    print("Six matrices with six different actions on the three nonzero vectors.")
    print("Degrees 1, 1, 2. Shear-fixed dimensions 1, 0, 1.")
    print("The sign character has label T² + T + 1 and value 1 at both irreducible-class matrices.")


if __name__ == "__main__":
    check()
