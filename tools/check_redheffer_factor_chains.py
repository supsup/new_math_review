"""Check the length-refined ordered factorizations against Redheffer determinants."""

from math import log2

from check_farey_harmonics import determinant


def counts_by_length(limit):
    counts = [[0] * (int(log2(limit)) + 1) for _ in range(limit + 1)]
    counts[1][0] = 1
    for n in range(2, limit + 1):
        for factor in range(2, n + 1):
            if n % factor == 0:
                for length, count in enumerate(counts[n // factor][:-1], 1):
                    counts[n][length] += count
    return counts


def compare(limit, character, harmonics):
    counts = counts_by_length(limit)
    cases = 0
    for size in range(2, limit + 1):
        for harmonic in harmonics:
            first = [sum(d * character(d) for d in range(1, size // q + 1)
                         if harmonic % d == 0) for q in range(1, size + 1)]
            for weight in (-2, -1, 0, 1, 2):
                expected = sum(character(q) * first[q - 1] *
                               sum(count * weight**r for r, count in enumerate(counts[q]))
                               for q in range(1, size + 1))
                rows = [[first[i - 1]] + [
                    1 if j == i else -weight * character(j // i) if j % i == 0 else 0
                    for j in range(2, size + 1)
                ] for i in range(1, size + 1)]
                assert determinant(rows) == expected, (size, harmonic, weight)
                cases += 1
    return cases


if __name__ == "__main__":
    plain = lambda _: 1
    quadratic = lambda q: (0, 1, -1, -1, 1)[q % 5]
    counts = counts_by_length(60)
    assert counts[12] == [0, 1, 4, 3, 0, 0]
    assert sum(sum(c) for c in counts[1:13]) == 28
    assert sum(sum(x * (-1)**r for r, x in enumerate(c)) for c in counts[1:13]) == -2
    cases = compare(60, plain, (1,))
    cases += compare(42, plain, (2, 6, 13, 24))
    cases += compare(42, quadratic, (1, 2, 6, 13, 24))
    print(f"{cases:,} exact length-refined sums and determinants agree.")
