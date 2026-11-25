"""Check the minimum-support mod-17 shapes and the Fano three-move puzzle.

Pass the compiled tools/check_seven_row_spectrum.cpp executable as an argument.
"""

from argparse import ArgumentParser
from itertools import combinations, permutations
from pathlib import Path
from subprocess import check_output

from check_mod11_minimum import determinant


def column_permutations(dimension=7):
    size = 1 << dimension
    for permutation in permutations(range(dimension)):
        transform = bytearray(size)
        for mask in range(1, size):
            bit = mask & -mask
            transform[mask] = transform[mask ^ bit] | (1 << permutation[bit.bit_length() - 1])
        yield transform


def column_orbit(rows, transforms):
    return {tuple(sorted(transform[mask] for mask in rows)) for transform in transforms}


def from_masks(rows):
    return [[(mask >> j) & 1 for j in range(len(rows) - 1, -1, -1)] for mask in rows]


def to_masks(rows):
    return [sum(value << (len(row) - 1 - j) for j, value in enumerate(row)) for row in rows]


def check_classes(binary, transforms):
    output = check_output([str(binary.resolve()), '--mod17-boards'], text=True)
    boards = [tuple(map(int, line.split()[1:])) for line in output.splitlines() if line.startswith('mod17:')]
    assert len(boards) == 36
    classes = set()
    for rows in boards:
        decoded = from_masks(rows)
        assert sum(map(sum, decoded)) == 24 and abs(determinant(decoded)) == 17
        classes.add(min(column_orbit(rows, transforms)))

    counts = []
    transposes = []
    classes = sorted(classes)
    for number, rows in enumerate(classes, start=1):
        size = len(column_orbit(rows, transforms))
        counts.append(size)
        transpose = to_masks(zip(*from_masks(rows)))
        other = classes.index(min(column_orbit(transpose, transforms))) + 1
        transposes.append(other)
        print(number, ' '.join(f'{row:07b}' for row in rows), size, other)
    assert counts == [5040, 2520, 2520, 1260, 5040]
    assert transposes == [1, 3, 2, 4, 5]
    print(f'{sum(counts):,} row-unordered boards with fixed column labels.')
    return classes


def check_fano_puzzle(classes, transforms):
    original = [[int((j - i) % 7 in (0, 1, 3)) for j in range(7)] for i in range(7)]
    zeros = [(i, j) for i in range(7) for j in range(7) if not original[i][j]]
    winners = 0
    for moves in combinations(zeros, 3):
        edited = [row[:] for row in original]
        crossings = [[original[row][col] for _, col in moves] for row, _ in moves]
        for row, col in moves:
            edited[row][col] = 1
        pattern_wins = any(
            all(crossings[order[i]][order[j]] == int(i > j) for i in range(3) for j in range(3))
            for order in permutations(range(3))
        )
        edited_wins = abs(determinant(edited)) == 17
        assert pattern_wins == edited_wins
        if edited_wins:
            winners += 1
            assert min(column_orbit(to_masks(edited), transforms)) == classes[4]
    assert winners == 168
    print(f'{winners} winning triples, each in shape 5.')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path, help='compiled seven-row spectrum checker')
    arguments = parser.parse_args()
    transforms = list(column_permutations())
    check_fano_puzzle(check_classes(arguments.binary, transforms), transforms)
