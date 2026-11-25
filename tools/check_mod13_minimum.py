"""Check the smallest mod-13 example in size seven using signed components."""

from check_mod11_minimum import check_lower_bound, determinant


def check_witness():
    encoded = ["0011000", "0000101", "0000011", "0101001", "0110110", "1001110", "1110001"]
    rows = [tuple(map(int, row)) for row in encoded]
    weights = [-7, -1, -3, 3, 2, 2, -2]
    assert sum(map(sum, rows)) == 21
    assert abs(determinant(rows)) == 13
    assert [sum(bit * weight for bit, weight in zip(row, weights)) for row in rows] == [0] * 6 + [-13]
    print("The displayed witness has 21 ones and absolute determinant 13.")


if __name__ == '__main__':
    check_witness()
    check_lower_bound(prime=13, cap=20, expected_counts=[33, 824, 19_495, 360_692, 1_685_516, 1_623_160])
