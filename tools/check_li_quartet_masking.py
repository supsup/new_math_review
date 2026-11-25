"""Bracket when a synthetic off-line quartet spoils a finite Li matrix.

The quartet is built from the exact decimal center of a certified mod-five
zero disk. This certificate uses that center as a mathematical input.
Install python-flint and run this file to replay the interval tests.
"""

import argparse
from functools import lru_cache
import json

from flint import acb, arb, arb_mat, ctx

from check_li_matrix import SIZE, li_coefficients


def first_rows():
    coefficients = li_coefficients(SIZE)
    zeta = [2 * coefficients[1]] + [
        coefficients[k + 1] - 2 * coefficients[k] + coefficients[k - 1]
        for k in range(1, SIZE)
    ]
    rho = acb("2.378755863122", "1174561.0989005927")
    w = 1 - 1 / rho
    # z = w + 1/w - 2. The quartet's second difference at k is
    # 2 Re((2-w-1/w)(w^k+w^-k)).
    z = 1 / (rho * (rho - 1))
    quartet = [-2 * (z * (w**k + w**(-k))).real for k in range(SIZE)]
    return zeta, quartet


def brackets():
    ctx.dps = 500
    zeta, quartet = first_rows()

    @lru_cache(maxsize=None)
    def det(size, weight):
        row = [a + weight * b for a, b in zip(zeta, quartet)]
        return arb_mat([[row[abs(i-j)] for j in range(size)] for i in range(size)]).det()

    def passes(size, weight):
        for order in range(1, size + 1):
            value = det(order, weight)
            if value < 0:
                return False
            assert value > 0, (order, weight, value)
        return True

    assert passes(SIZE, 0)
    assert passes(SIZE, 1)
    # The unamplified model quartet passes sizes 1 and 2 on its own.
    assert quartet[0] > abs(quartet[1])
    result = []
    for size in range(3, SIZE + 1):
        low, high = 0, 50
        assert not passes(size, 10**high)
        while high - low > 1:
            middle = (low + high) // 2
            if passes(size, 10**middle):
                low = middle
            else:
                high = middle
        exponent = low
        scale = 10**(exponent - 3)
        low, high = 1000, 10000
        while high - low > 1:
            middle = (low + high) // 2
            if passes(size, middle * scale):
                low = middle
            else:
                high = middle
        assert passes(size, low * scale)
        assert not passes(size, high * scale)
        result.append([size, low, high, exponent])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot-data", action="store_true")
    args = parser.parse_args()
    rows = brackets()
    if args.plot_data:
        print(json.dumps(rows, separators=(",", ":")))
    else:
        print("Sizes 1 and 2 stay positive at every nonnegative weight.")
        print("One copy stays positive through size", SIZE)
        for size, lo, hi, exponent in rows:
            print(f"Size {size:2}: ({lo / 1000:.3f}, {hi / 1000:.3f}) times 10^{exponent}")


if __name__ == "__main__":
    main()
