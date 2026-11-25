"""Check the 26-one witness and the remaining dimensions for the mixed rank drop."""

from itertools import combinations, combinations_with_replacement, product

from check_mod11_minimum import determinant, minimum_support


def count_reduced_systems(dimension, cap, heavy_count):
    """Exclude determinants divisible by 30 via weight-two graph components."""
    component_types = [(1, 0)] + [
        (plus, minus)
        for plus in range(1, dimension)
        for minus in range(1, plus + 1)
        if plus + minus <= dimension
    ]
    budget = cap - 2 * (dimension - heavy_count)
    max_row = budget - 3 * (heavy_count - 1)
    average, extra = divmod(budget, heavy_count)
    max_product = average ** (heavy_count - extra) * (average + 1) ** extra
    visits = 0

    for components in combinations_with_replacement(component_types, heavy_count):
        inactive = dimension - sum(plus + minus for plus, minus in components)
        if inactive < 0 or inactive in (1, 2):
            continue
        # Each odd cycle contributes a factor of 2 and no odd factor.
        divisor = 15 if inactive else 30
        if max_product < divisor:
            continue

        row_costs = {}
        ranges = [range(-minus, plus + 1) for plus, minus in components]
        for row in product(*ranges):
            if not any(row):
                continue
            support = minimum_support(row, components, inactive)
            if support is not None and support <= max_row:
                # Either sign of the same row gives the same absolute determinant.
                canonical = min(row, tuple(-value for value in row))
                row_costs[canonical] = min(support, row_costs.get(canonical, support))

        for chosen in combinations(row_costs.items(), heavy_count):
            if sum(cost for _, cost in chosen) <= budget:
                visits += 1
                value = determinant([row for row, _ in chosen])
                assert value == 0 or value % divisor != 0, (dimension, components, chosen, value)

    return visits


def check_witness():
    encoded = [
        '00000011', '00001100', '00110001', '01010100',
        '01101010', '10011010', '10100110', '11001001',
    ]
    rows = [list(map(int, row)) for row in encoded]
    weights = [9, 1, 11, 3, 4, -4, -16, -14]
    assert sum(map(sum, rows)) == 26
    assert determinant(rows) == -30
    assert [sum(bit * weight for bit, weight in zip(row, weights)) for row in rows] == [-30] + [0] * 7
    assert determinant([row[:1] + row[2:] for row in rows[1:]]) == -1
    print('Verified support 26, determinant −30, the weighted sums, and a unimodular minor.')


if __name__ == '__main__':
    check_witness()
    expected = {
        10: [0, 756, 151_590, 2_686_635, 14_659_718],
        11: [0, 0, 17_119],
        12: [0],
    }
    for dimension, counts in expected.items():
        for heavy_count, wanted in enumerate(counts, start=1):
            actual = count_reduced_systems(dimension, cap=25, heavy_count=heavy_count)
            assert actual == wanted, (dimension, heavy_count, actual, wanted)
            print(f'{dimension} rows, {heavy_count} heavy rows: {actual:,} reduced systems checked.', flush=True)
