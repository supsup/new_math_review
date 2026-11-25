"""Check two binary rotating mixers that tolerate three or four lost reports."""

from itertools import combinations
from math import comb, prod

from flint import nmod_mat, nmod_poly

from check_mod11_minimum import determinant
from check_two_loss_circulants import cyclic_polynomial, wiring_polynomial


# Prime, losses, offsets, initial root and common ratio, ordinary determinant.
EXAMPLES = (
    (29, 3, (0, 1, 2, 4, 6), 2, 3, 365835),
    (61, 4, (0, 1, 4, 51, 52), 42, 35, 196264796175),
)


def verify(prime, losses, offsets, alpha, ratio, expected_det):
    n = prime - 1
    coefficients = wiring_polynomial(n, offsets)
    board = [[coefficients[(j - i) % n] for j in range(n)] for i in range(n)]
    assert determinant(board) == expected_det != 0 and expected_det % prime**losses == 0

    roots = [alpha * pow(ratio, j, prime) % prime for j in range(losses)]
    root_poly = prod((nmod_poly([-root, 1], prime) for root in roots), start=nmod_poly([1], prime))
    modulus = nmod_poly(cyclic_polynomial(n), prime)
    assert modulus.gcd(nmod_poly(coefficients, prime)) == root_poly
    assert pow(ratio, n, prime) == 1
    addresses = [pow(ratio, i, prime) for i in range(n)]
    assert len(set(addresses)) == n

    # The determinant of the polynomial evaluation system is a product
    # of address differences (Vandermonde). We check every choice.
    choices = 0
    for nodes in combinations(addresses, losses):
        value = prod(b-a for a, b in combinations(nodes, 2))
        assert value % prime
        choices += 1
    assert choices == comb(n, losses)

    # A literal matrix check replaces selected rows by direct observations.
    # Adjacent and spaced-out indices exercise the two roles independently.
    groups = [
        set(range(losses)),
        set(range(n - losses, n)),
        {i * (n // losses) for i in range(losses)},
        {(n - 1 - i * (n // losses)) % n for i in range(losses)},
    ]
    for muted in groups:
        survivors = [row for i, row in enumerate(board) if i not in muted]
        for probes in groups:
            unit_rows = [[int(i == j) for j in range(n)] for i in sorted(probes)]
            assert nmod_mat(survivors + unit_rows, prime).rank() == n
    print(f"mod {prime}: {n} inputs, {losses} erasures, roots {roots}, det {expected_det}, "
          f"{choices:,} independent probe sets.")


def exclude_four_offsets_mod_29():
    prime, n = 29, 28
    powers = [[pow(root, exponent, prime) for exponent in range(n)] for root in range(1, prime)]
    checked = three_roots = 0
    for offsets in combinations(range(1, n), 3):
        checked += 1
        roots = [root for root, values in enumerate(powers, 1)
                 if (1 + sum(values[j] for j in offsets)) % prime == 0]
        if len(roots) != 3:
            continue
        three_roots += 1
        alpha, beta, gamma = roots
        beta_ratio = beta * pow(alpha, -1, prime) % prime
        gamma_ratio = gamma * pow(alpha, -1, prime) % prime
        # Subtract the first row (1, 1, 1) from the other two rows in
        # the evaluation matrix after scaling out alpha to each power.
        probes = [(pow(beta_ratio, j, prime) - 1, pow(gamma_ratio, j, prime) - 1)
                  for j in range(1, n)]
        assert any((a*d - b*c) % prime == 0 for (a, b), (c, d) in combinations(probes, 2))
    assert checked == 2925 and three_roots == 348
    print("mod 29: all 2,925 normalized four-offset patterns excluded; 348 had three roots.")


if __name__ == "__main__":
    for example in EXAMPLES:
        verify(*example)
    exclude_four_offsets_mod_29()
