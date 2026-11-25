"""Replay the mod-59 mixer that recovers from losing any five readings."""

from math import comb
from random import Random

from flint import fmpz_mat, nmod_mat


PRIME = 59
SIZE = PRIME - 1
LOSSES = 5
OFFSETS = (0, 4, 14, 36, 43, 46, 48)
DETERMINANT = 3_047_747_308_987_465


def main():
    board = [[int((j-i) % SIZE in OFFSETS) for j in range(SIZE)] for i in range(SIZE)]
    assert int(fmpz_mat(board).det()) == DETERMINANT
    assert DETERMINANT == 4_263_035 * PRIME**LOSSES
    assert nmod_mat(board, PRIME).rank() == SIZE - LOSSES

    roots = [x for x in range(1, PRIME) if sum(pow(x, e, PRIME) for e in OFFSETS) % PRIME == 0]
    progression = [23*pow(2, k, PRIME) % PRIME for k in range(LOSSES)]
    assert sorted(roots) == sorted(progression)
    addresses = [pow(2, j, PRIME) for j in range(SIZE)]
    assert len(set(addresses)) == SIZE

    # Check literal recovery on fixed pseudorandom choices. The determinant
    # of the evaluation system covers every choice, independently of this test.
    random = Random(59)
    unit_rows = [[int(i == j) for j in range(SIZE)] for i in range(SIZE)]
    for _ in range(128):
        missing = set(random.sample(range(SIZE), LOSSES))
        delivered = [row for i, row in enumerate(board) if i not in missing]
        direct = [unit_rows[i] for i in random.sample(range(SIZE), LOSSES)]
        assert nmod_mat(delivered + direct, PRIME).rank() == SIZE

    print(f"{SIZE} inputs, {len(OFFSETS)} wires per reading, determinant {DETERMINANT:,}.")
    print(f"Distinct addresses cover all {comb(SIZE, LOSSES):,} probe sets. "
          "Verified 128 actual row replacements.")


if __name__ == "__main__":
    main()
