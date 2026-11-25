"""Check the seven-row prime-11 result by resolving the degree-two equations.

The reduction uses the known maximum absolute determinant 9 in size six.
See crew_visuals/mod11_rank_card.txt for the argument and citation.
"""

from itertools import combinations, combinations_with_replacement, product


def determinant(rows):
    """Compute an integer determinant by fraction-free elimination."""
    matrix = [list(row) for row in rows]
    dimension = len(matrix)
    sign = 1
    previous = 1
    for col in range(dimension - 1):
        pivot = next((row for row in range(col, dimension) if matrix[row][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            sign = -sign
            matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        leading = matrix[col][col]
        for row in range(col + 1, dimension):
            for j in range(col + 1, dimension):
                numerator = leading * matrix[row][j] - matrix[row][col] * matrix[col][j]
                matrix[row][j], remainder = divmod(numerator, previous)
                assert remainder == 0
        previous = leading
    return sign * matrix[-1][-1]


def minimum_support(coefficients, components, inactive_vertices):
    used = sum(map(abs, coefficients))
    canceling_pairs = sum(
        min(plus - max(value, 0), minus - max(-value, 0))
        for value, (plus, minus) in zip(coefficients, components)
    )
    for pairs in range(canceling_pairs + 1):
        support = used + 2 * pairs
        if support + inactive_vertices >= 3:
            return max(support, 3)
    return None


def check_lower_bound(*, prime, cap, expected_counts, dimension=7):
    """Exclude nonsingular witnesses with at least two ones per row."""
    component_types = [(1, 0)] + [
        (plus, minus)
        for plus in range(1, dimension)
        for minus in range(1, plus + 1)
        if plus + minus <= dimension
    ]
    counts = []
    for heavy_rows in range(1, min(dimension, cap - 2 * dimension) + 1):
        budget = cap - 2 * (dimension - heavy_rows)
        max_row = budget - 3 * (heavy_rows - 1)
        checked = 0
        for components in combinations_with_replacement(component_types, heavy_rows):
            inactive = dimension - sum(plus + minus for plus, minus in components)
            # An odd component needs at least three vertices.
            if inactive < 0 or inactive in (1, 2):
                continue
            rows = []
            for coefficients in product(*(range(-minus, plus + 1) for plus, minus in components)):
                if not any(coefficients):
                    continue
                support = minimum_support(coefficients, components, inactive)
                if support is not None and support <= max_row:
                    rows.append((coefficients, support))

            # An invertible reduced system cannot contain identical rows.
            for chosen in combinations(rows, heavy_rows):
                if sum(support for _, support in chosen) > budget:
                    continue
                checked += 1
                det = determinant([coefficients for coefficients, _ in chosen])
                assert det == 0 or det % prime != 0, (components, chosen, det)
        counts.append(checked)
        print(f"{heavy_rows} heavy rows: {checked:,} smaller systems checked")

    assert counts == expected_counts
    print(f"No mod-{prime} rank drop with at most {cap} ones, after checking {sum(counts):,} systems.")


def check_witness():
    encoded = ["1100000", "1010000", "0001100", "0110010", "1001010", "0111001", "1000111"]
    rows = [tuple(map(int, row)) for row in encoded]
    weights = [1, -1, -1, -3, 3, 2, 5]
    assert sum(map(sum, rows)) == 20
    assert abs(determinant(rows)) == 11
    assert [sum(bit * weight for bit, weight in zip(row, weights)) for row in rows] == [0] * 6 + [11]
    print("The displayed witness has 20 ones and absolute determinant 11.")


if __name__ == "__main__":
    check_witness()
    check_lower_bound(prime=11, cap=19, expected_counts=[33, 818, 16_839, 159_742, 254_506])
