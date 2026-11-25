"""Check the larger-dimensional cases behind global sparse rank-drop minima."""

from check_mod11_minimum import check_lower_bound, determinant


if __name__ == '__main__':
    witness = ['00000011', '00000101', '00001110', '00011001', '00110110', '01101000', '10101000', '11010000']
    rows = [list(map(int, row)) for row in witness]
    weights = [-7, -7, 5, -3, 2, -1, -1, 1]
    assert sum(map(sum, rows)) == 23
    assert determinant(rows) == 17
    assert [sum(bit * weight for bit, weight in zip(row, weights)) for row in rows] == [0]*7 + [-17]
    print('The eight-row board uses 23 ones and has determinant 17.')

    paired = ['00000011', '00001100', '00010101', '00100110', '01010010', '01101001', '10101000', '11000100']
    rows = [list(map(int, row)) for row in paired]
    assert sum(map(sum, rows)) == 23 and determinant(rows) == 17
    rows[6][2], rows[6][3] = 0, 1
    assert sum(map(sum, rows)) == 23 and determinant(rows) == 19
    print('Moving the paired board’s 1 from row 7 column C to D changes determinant 17 to 19.')

    cases = [
        (11, 19, 8, [51, 1_475, 7_956]),
        (11, 19, 9, [51]),
        (13, 20, 8, [53, 2_011, 31_721, 178_332]),
        (13, 20, 9, [65, 1_068]),
        (13, 20, 10, []),
        (17, 22, 9, [73, 3_479, 85_030, 468_742]),
        (17, 22, 10, [91, 2_024]),
        (17, 22, 11, []),
        (19, 22, 9, [73, 3_479, 85_030, 468_742]),
        (19, 22, 10, [91, 2_024]),
        (19, 22, 11, []),
    ]
    for prime, cap, dimension, counts in cases:
        print(f'Size {dimension}, prime {prime}, support cap {cap}.')
        check_lower_bound(prime=prime, cap=cap, dimension=dimension, expected_counts=counts)
