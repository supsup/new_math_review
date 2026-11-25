"""Check quartic-character circle sums and their integer block determinants."""

from check_farey_harmonics import (
    MAX_HARMONIC,
    MAX_ORDER,
    binary_board,
    determinant,
    primitive_packets,
)


def character(n):
    return ((0, 0), (1, 0), (0, 1), (0, -1), (-1, 0))[n % 5]


def weighted_sum(terms):
    a = b = 0
    for scale, (r, i) in terms:
        a += scale * r
        b += scale * i
    return a, b


def mobius(limit):
    values = [0, 1]
    for n in range(2, limit + 1):
        values.append(-sum(values[d] for d in range(1, n) if n % d == 0))
    return values


def block_board(n, divisors, normalize=False):
    rows = []
    for i in range(1, n + 1):
        first = weighted_sum((d, character(d)) for d in divisors if i * d <= n)
        tail = [character(j // i) if j % i == 0 else (0, 0) for j in range(2, n + 1)]
        if normalize:
            prime_to_five = i
            while prime_to_five % 5 == 0:
                prime_to_five //= 5
            u, v = character(prime_to_five)
            a, b = first
            first = (a * u - b * v, a * v + b * u)
            tail = [(int(bool(a or b)), 0) for a, b in tail]
        row_pair = [[], []]
        for a, b in [first, *tail]:
            row_pair[0].extend([a, -b])
            row_pair[1].extend([b, a])
        rows.extend(row_pair)
    return rows


def make_binary(rows):
    """Encode the two remaining integer columns with independent helper blocks."""
    def one(_):
        return 1

    once = binary_board(rows, 1, one)
    once[0], once[1] = once[1], once[0]
    for row in once:
        row[0], row[1] = row[1], row[0]
    return binary_board(once, 1, one)


def check():
    packets = primitive_packets()
    mu = mobius(MAX_ORDER)
    sums = boards = 0
    for n in range(2, MAX_ORDER + 1):
        for k in range(1, MAX_HARMONIC + 1):
            divisors = [d for d in range(1, min(n, k) + 1) if k % d == 0]
            exact = weighted_sum((packets[q, k], character(q)) for q in range(1, n + 1))
            from_mobius = weighted_sum((d * mu[q], character(d * q))
                                       for d in divisors for q in range(1, n // d + 1))
            assert exact == from_mobius, (n, k, exact, from_mobius)
            if (n, k) == (7, 1):
                assert exact == (2, -1)
            sums += 1
            if n <= 12 or n in (18, 24, 36, 42) and k in (1, 2, 5, 6, 13, 24):
                a, b = exact
                norm = a * a + b * b
                assert determinant(block_board(n, divisors)) == norm, (n, k)
                normalized = block_board(n, divisors, normalize=True)
                largest = max(abs(value) for row in normalized for value in row[:2])
                width = largest.bit_length()
                helpers = 2 if width == 1 else 2 * width + 1
                binary = make_binary(normalized)
                assert len(binary) == 2 * n + 2 * helpers
                assert all(value in (0, 1) for row in binary for value in row)
                assert determinant(binary) == norm, (n, k, "binary")
                boards += 1
    print(f"{sums:,} exact quartic-character sums and {boards:,} integer/binary determinant pairs agree.")


if __name__ == "__main__":
    check()
