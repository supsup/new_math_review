"""Build a binary matrix with prescribed positive determinant magnitude."""

from argparse import ArgumentParser

from check_mod11_minimum import determinant


GADGET = ('0000110', '0011000', '0001101', '0110001', '1100100', '1000011', '0101010')


def base_twelve_digits(value):
    if value < 1:
        raise ValueError('The determinant target must be positive.')
    digits = []
    while value:
        value, digit = divmod(value, 12)
        digits.append(digit)
    return digits[::-1]


def build(value):
    """Return rows as lists of column indices with a one, in creation order."""
    digits = base_twelve_digits(value)
    rows = []
    variables = 1

    def new_variable():
        nonlocal variables
        index = variables
        variables += 1
        return index

    def sum_to_zero(*terms):
        index = new_variable()
        rows.append((index, *terms))
        return index

    # Column zero is x. Build signed multiples of x once for all digits.
    positive = {1: 0}
    negative = {1: sum_to_zero(0)}
    duplicate = sum_to_zero(0)
    for digit in range(2, 12):
        prior = negative[digit - 1] if digit > 2 else duplicate
        positive[digit] = sum_to_zero(prior, negative[1])
        negative[digit] = sum_to_zero(positive[digit])

    current = positive[digits[0]]
    for digit in digits[1:]:
        columns = [new_variable() for _ in range(6)] + [current]
        following = new_variable()
        for pattern in GADGET[:-1]:
            rows.append(tuple(col for bit, col in zip(pattern, columns) if bit == '1'))
        last = tuple(col for bit, col in zip(GADGET[-1], columns) if bit == '1')
        add_digit = (negative[digit],) if digit else ()
        rows.append((*last, following, *add_digit))
        current = following

    rows.append((current,))
    assert len(rows) == variables
    assert all(len(set(row)) == len(row) for row in rows)
    assert sum(map(len, rows)) == 55 + 20*(len(digits)-1) + sum(digit > 0 for digit in digits[1:])
    return rows


def dense(rows):
    return [[int(i in row) for i in range(len(rows))] for row in rows]


def check():
    gadget = [list(map(int, row)) for row in GADGET]
    assert abs(determinant(gadget)) == 12
    assert abs(determinant([row[:-1] for row in gadget[:-1]])) == 1
    for value in [*range(1, 65), 255, 399, 1728, 10**9+7, 2**64+13]:
        rows = build(value)
        assert abs(determinant(dense(rows))) == value
    print('69 exact determinants passed, including a 65-bit target.')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('target', type=int, nargs='?', help='print a binary matrix for this target; omit for the replay')
    args = parser.parse_args()
    if args.target is None:
        check()
    else:
        for row in dense(build(args.target)):
            print(''.join(map(str, row)))
