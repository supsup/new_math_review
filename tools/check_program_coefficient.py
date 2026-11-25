"""Cross-check a small program’s coefficients and its two-state arithmetic circuit."""

from itertools import product


def circuit(width):
    # For each next variable pair, keep polynomials for even and odd parity.
    even, odd = {(): 1}, {(): 0}
    for _ in range(width):
        next_even, next_odd = {}, {}
        for prefix in even:
            next_even[prefix + (0,)] = even[prefix]
            next_odd[prefix + (0,)] = odd[prefix]
            next_even[prefix + (1,)] = next_odd[prefix + (1,)] = even[prefix] + odd[prefix]
        even, odd = next_even, next_odd
    return even


def direct(word):
    """Count the even-cardinality subsets of positions whose bit is one."""
    return sum(sum(trace) % 2 == 0 and all(choice <= bit for choice, bit in zip(trace, word))
               for trace in product((0, 1), repeat=len(word)))


def check():
    cases = 0
    for width in range(1, 9):
        coefficients = circuit(width)
        total = 0
        for target in product((0, 1), repeat=width):
            selected = sum(value * int(word == target) for word, value in coefficients.items())
            assert selected == direct(target)
            total += selected
            cases += 1
        assert total == (3**width + 1) // 2
    assert circuit(4)[(1, 0, 1, 1)] == 4
    print(f"{cases} exact word selectors and eight full coefficient sums agree.")


if __name__ == "__main__":
    check()
