"""Exact congruences and the smallest modulus for two-loss binary circulants.

Requires python-flint. Matrices in a field are tested with polynomial GCDs.
Their ordinary determinants use the existing integer Bareiss replay.
"""

from itertools import combinations

from flint import fmpz_poly, nmod_poly

from check_mod11_minimum import determinant


# Prime, board size, wiring offsets, modular roots, and ordinary determinant.
BOARDS = (
    (17, 16, (0, 1, 2, 3, 9), (2, 14), -1445),
    (19, 18, (0, 1, 5, 7), (13, 16), -20216),
    (23, 22, (0, 1, 4), (18, 19), 1587),
)


def cyclic_polynomial(size):
    return [-1] + [0] * (size - 1) + [1]


def wiring_polynomial(size, support):
    return [int(j in support) for j in range(size)]


def all_probe_pairs(modular_gcd, size, prime):
    """Compare probe 0 to each other probe. Shifts cover all remaining pairs."""
    if modular_gcd.degree() != 2:
        return False
    a, b = int(modular_gcd[1]), int(modular_gcd[0])
    previous, current = (1, 0), (0, 1)
    for _ in range(1, size):
        if current[1] == 0:
            return False
        previous, current = current, tuple((-a*v - b*u) % prime for u, v in zip(previous, current))
    return True


def first_wiring(prime, size):
    """A cyclic shift lets any nonempty row start at offset zero."""
    cycle = cyclic_polynomial(size)
    modular_cycle = nmod_poly(cycle, prime)
    integer_cycle = fmpz_poly(cycle)
    # Skip the zero and all-ones rows (singular), and singleton rows (permutations).
    for weight in range(2, size):
        for tail in combinations(range(1, size), weight - 1):
            support = (0,) + tail
            coefficients = wiring_polynomial(size, support)
            modular_gcd = nmod_poly(coefficients, prime).gcd(modular_cycle)
            if (all_probe_pairs(modular_gcd, size, prime)
                    and fmpz_poly(coefficients).gcd(integer_cycle).degree() == 0):
                return support
    return None


def verify_example(prime, size, support, roots, expected_det):
    coefficients = wiring_polynomial(size, support)
    board = [[coefficients[(j - i) % size] for j in range(size)] for i in range(size)]
    assert determinant(board) == expected_det != 0 and expected_det % prime**2 == 0
    cycle = nmod_poly(cyclic_polynomial(size), prime)
    modular_gcd = nmod_poly(coefficients, prime).gcd(cycle)
    alpha, beta = roots
    assert modular_gcd == nmod_poly([alpha * beta, -alpha - beta, 1], prime)
    assert all_probe_pairs(modular_gcd, size, prime)

    # Independent check of both kernels by evaluation at the two roots.
    rows = [[pow(root, j, prime) for j in range(size)] for root in roots]
    for matrix, vectors in ((board, rows), (zip(*board), [row[:1] + row[:0:-1] for row in rows])):
        assert all(sum(a*b for a, b in zip(row, vector)) % prime == 0
                   for row in matrix for vector in vectors)
        a, b = vectors
        assert all((a[i]*b[j] - a[j]*b[i]) % prime != 0 for i, j in combinations(range(size), 2))
    print(f"mod {prime}, size {size}: det {expected_det}, roots {roots}, {len(support)} marks per row.")


if __name__ == "__main__":
    for example in BOARDS:
        verify_example(*example)
    for p in (2, 3, 5, 7, 11, 13, 17):
        survivors = [(n, support) for n in range(3, p + 2) if (support := first_wiring(p, n))]
        assert survivors == ([(16, BOARDS[0][2])] if p == 17 else []), (p, survivors)
        print(f"mod {p}, sizes 3–{p + 1}: {survivors or 'no solution'}")
    repeated = nmod_poly([1, 1, 1], 7)
    assert repeated.gcd(nmod_poly(cyclic_polynomial(6), 7)) == repeated
    assert not all_probe_pairs(repeated, 6, 7)
    print("Controls pass: two kernel dimensions alone can leave repeated probe directions.")
