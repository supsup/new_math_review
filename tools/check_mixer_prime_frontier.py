"""Replay the signed-path recovery constructions, including both growth steps."""

import argparse
from functools import cache
from math import isqrt

from check_mod11_minimum import determinant


LAST_ROWS = {
    19: (1, -1, 0, 0, 1),
    23: (-1, 0, 0, -1, 1),
    29: (-1, 1, 0, 0, 0, -1),
    31: (-1, 0, 0, 0, 2),
    37: (1, 0, 1, 0, 0, -1),
    41: (1, 0, 0, -1, 0, -1),
    47: (-1, 0, 0, 0, 1, -1),
}

COMPACT_TAILS = {
    19: [(-1, 0, 0, -1, -1), (0, 0, 1, -1, 1)],
    23: [(-1, 0, 0, 0, 2), (0, 0, 1, -1, -1)],
}


def signed_path(last):
    size = len(last)
    return [
        [2 * int(i == j) + int(i + 1 == j) for j in range(size)]
        for i in range(size - 1)
    ] + [list(last)]


def binary_digits(value):
    return tuple(map(int, reversed(bin(value)[2:])))


def separated_digits(value):
    digits = []
    while value:
        digit = 0 if value % 2 == 0 else 2 - value % 4
        digits.append(digit)
        value = (value - digit) // 2
    return tuple(digits)


def excess(digits):
    return len(digits) + sum(d != 0 for d in digits) - 3


@cache
def fewest_path_digits(value):
    if value == 1:
        return (1,)
    choices = (0,) if value % 2 == 0 else (1, -1)
    return min(((d,) + fewest_path_digits((value - d) // 2) for d in choices), key=excess)


def as_board(rows, size):
    return [[int(j in row) for j in range(size)] for row in rows]


def star_board(matrix, prime, split=False):
    left = null_vector(list(zip(*matrix)), prime)
    assert all(left)
    edge_rows = []
    last_rows = [[] for _ in matrix]
    size = 0
    for column in zip(*matrix):
        center = size
        size += 1
        for owner, weight in enumerate(column):
            if weight < 0:
                assert weight == -1
                last_rows[owner].append(center)
        for term in range(max(column)):
            owners = [i for i, weight in enumerate(column) if weight > term]
            # A leaf shared by these readings would get the negative of this
            # sum in the reading relation. Use separate leaves if it vanishes.
            canceled = sum(left[i] for i in owners) % prime == 0
            extra_split = split and not canceled and len(owners) == 2
            groups = [[i] for i in owners] if canceled or extra_split else [owners]
            if extra_split:
                split = False
            for group in groups:
                edge_rows.append([center, size])
                for owner in group:
                    last_rows[owner].append(size)
                size += 1
    assert not split, "There is no leaf shared by two readings"
    return as_board(edge_rows + last_rows, size)


def extend_by_two(board):
    size = len(board)
    row = board[0]
    column = row.index(1)
    result = [list(line) + [0, 0] for line in board]
    result[0][column] = 0
    result[0][-1] = 1
    result.extend(as_board([[column, size], [size, size + 1]], size + 2))
    return result


def null_vector(board, prime):
    """Return a generator when the matrix has a one-dimensional kernel."""
    a = [list(row) for row in board]
    size = len(a)
    pivots = []
    for col in range(size):
        rank = len(pivots)
        pivot = next((i for i in range(rank, size) if a[i][col] % prime), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inv = pow(a[rank][col], -1, prime)
        a[rank] = [(x * inv) % prime for x in a[rank]]
        for i in range(rank + 1, size):
            mult = a[i][col]
            a[i] = [(x - mult * y) % prime for x, y in zip(a[i], a[rank])]
        pivots.append(col)
    assert len(pivots) == size - 1
    free = next(j for j in range(size) if j not in pivots)
    result = [0] * size
    result[free] = 1
    for row, col in reversed(list(zip(a, pivots))):
        result[col] = -sum(x * y for x, y in zip(row, result)) % prime
    return result


def verify(board, prime, excess):
    size = len(board)
    assert sum(map(sum, board)) == 2 * size + excess
    assert abs(determinant(board)) == prime
    for matrix in (board, list(zip(*board))):
        weights = null_vector(matrix, prime)
        assert all(weights)
        assert all(sum(a * b for a, b in zip(row, weights)) % prime == 0 for row in matrix)
    return size


def check():
    for prime, last in LAST_ROWS.items():
        matrix = signed_path(last)
        assert abs(sum(coefficient * (-2)**j for j, coefficient in enumerate(last))) == prime
        assert abs(determinant(matrix)) == prime
        if prime in COMPACT_TAILS:
            matrix = matrix[:3] + [list(row) for row in COMPACT_TAILS[prime]]
            assert abs(determinant(matrix)) == prime
        sizes = []
        for split in (False, True):
            board = star_board(matrix, prime, split)
            for _ in range(3):
                sizes.append(verify(board, prime, len(last)))
                board = extend_by_two(board)
        print(f"mod {prime}: excess {len(last)}, verified sizes {sorted(sizes)}")


def check_family():
    checked = 0
    for prime in range(3, 998, 2):
        if any(prime % d == 0 for d in range(3, isqrt(prime) + 1, 2)):
            continue
        representations = (binary_digits(prime), separated_digits(prime), fewest_path_digits(prime))
        assert excess(representations[2]) <= min(map(excess, representations[:2]))
        for digits in representations:
            partial = 0
            for j, digit in enumerate(digits):
                partial += digit * 2**j
                if j < len(digits) - 1:
                    assert 0 < abs(partial) < prime
            assert partial == prime
            last = [(-1)**j * digit for j, digit in enumerate(digits)]
            matrix = signed_path(last)
            base = star_board(matrix, prime)
            verify(base, prime, excess(digits))
            if len(last) > 2:
                verify(star_board(matrix, prime, split=True), prime, excess(digits))
            checked += 1
    print(f"Verified {checked} signed or binary constructions from odd primes through 997.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", action="store_true", help="also test the digit constructions through 997")
    args = parser.parse_args()
    check()
    if args.family:
        check_family()
