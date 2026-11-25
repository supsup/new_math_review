"""Check the four-syndrome decoder for the sixty-input rotating mixer."""

from itertools import combinations
from math import prod

from check_multiple_loss_circulants import EXAMPLES


P, CHECKS, OFFSETS, INITIAL_ROOT, RATIO, _ = EXAMPLES[1]
N = P - 1
NODES = [pow(RATIO, -i, P) for i in range(N)]
GAINS = [pow(INITIAL_ROOT, -i, P) for i in range(N)]
INVERSES = [0] + [pow(j, -1, P) for j in range(1, P)]
COLLISION_POSITIONS = (1, 4, 7, 13, 21)


def syndrome(changes):
    return [sum(amount * GAINS[i] * pow(NODES[i], j, P) for i, amount in changes) % P
            for j in range(CHECKS)]


def check_left_vectors():
    for input_index in range(N):
        rows = [(input_index - offset) % N for offset in OFFSETS]
        assert all(sum(GAINS[i]*pow(NODES[i], j, P) for i in rows) % P == 0
                   for j in range(CHECKS))


def check_decoding():
    for node in NODES:
        for weight in range(1, P):
            first, second, third, fourth = (weight * pow(node, j, P) % P for j in range(CHECKS))
            assert (first*third - second**2) % P == 0
            assert second*INVERSES[first] % P == node
            assert third == first*node**2 % P and fourth == first*node**3 % P

    verified = 0
    for x, y in combinations(NODES, 2):
        # Multiplying both errors by the same nonzero scalar multiplies
        # the checks by that scalar and leaves the locator unchanged.
        for weight in range(1, P):
            a, b, c, d = ((pow(x, j, P) + weight*pow(y, j, P)) % P for j in range(CHECKS))
            delta = (a*c - b**2) % P
            assert delta == weight * (x-y)**2 % P != 0
            total = (a*d - b*c) * INVERSES[delta] % P
            product = (b*d - c**2) * INVERSES[delta] % P
            assert total == (x+y) % P and product == x*y % P
            first_weight = (b - a*y)*INVERSES[(x-y) % P] % P
            assert first_weight == 1 and (a - first_weight) % P == weight
            verified += 1
    assert verified == 106200
    print(f"{verified:,} normalized two-error cases. Scaling covers all {verified*(P-1):,} cases.")


def check_collision():
    nodes = [NODES[i] for i in COLLISION_POSITIONS]
    weights = [INVERSES[prod(x-y for y in nodes if x != y) % P] for x in nodes]
    magnitudes = [weight*INVERSES[GAINS[i]] % P for i, weight in zip(COLLISION_POSITIONS, weights)]
    assert all(magnitudes)
    all_changes = list(zip(COLLISION_POSITIONS, magnitudes))
    actual = all_changes[:3]
    phantom = [(i, -m % P) for i, m in all_changes[3:]]
    assert syndrome(all_changes) == [0]*CHECKS
    assert syndrome(actual) == syndrome(phantom) != [0]*CHECKS
    print(f"Three changes {actual} give the same four checks as two changes {phantom}.")


if __name__ == "__main__":
    check_left_vectors()
    check_decoding()
    check_collision()
