"""Check integer and mod-two cycle-cover identities on small directed graphs."""

from itertools import permutations
from random import Random

from check_farey_harmonics import determinant


def matching_masks(n):
    """Return edge masks and permutation signs, counted via inversions."""
    for targets in permutations(range(n)):
        mask = sum(1 << (i * n + j) for i, j in enumerate(targets))
        inversions = sum(a > b for i, a in enumerate(targets) for b in targets[i + 1:])
        yield mask, (-1) ** inversions


def directed_cycle_masks(n, length):
    """Pick cyclic order with its smallest vertex first."""
    for vertices in permutations(range(n), length):
        if vertices[0] != min(vertices):
            continue
        yield sum(1 << (a * n + b) for a, b in zip(vertices, vertices[1:] + vertices[:1]))


def permanent_subset_dp(rows):
    """Add one row at a time over the sets of occupied target columns."""
    n = len(rows)
    dp = [1] + [0] * ((1 << n) - 1)
    for used in range((1 << n) - 1):
        next_row = rows[bin(used).count("1")]
        for j, allowed in enumerate(next_row):
            bit = 1 << j
            if allowed and not used & bit:
                dp[used | bit] += dp[used]
    return dp[-1]


def from_principal_minors(rows):
    """Keep vertex 0 in the permanent factor and sum over the other subsets."""
    n = len(rows)
    total = 0
    for subset in range(0, 1 << n, 2):
        left = [i for i in range(n) if subset & (1 << i)]
        right = [i for i in range(n) if not subset & (1 << i)]
        signed = determinant([[-rows[i][j] for j in left] for i in left]) if left else 1
        total += signed * permanent_subset_dp([[rows[i][j] for j in right] for i in right])
    return total


def check_orders():
    rng = Random(4351)
    cases = loop_cases = 0
    for n in range(2, 6):
        candidates = range(1 << (n * n)) if n < 5 else [
            rng.randrange(1 << (n * n)) for _ in range(256)
        ]
        matches = tuple(matching_masks(n))
        even = tuple(mask for length in range(2, n + 1, 2) for mask in directed_cycle_masks(n, length))
        loops = sum(1 << (i * n + i) for i in range(n))
        long_cycles = set(directed_cycle_masks(n, n))
        for graph in candidates:
            rows = [[(graph >> (i * n + j)) & 1 for j in range(n)] for i in range(n)]
            det = determinant(rows)
            perm = permanent_subset_dp(rows)
            available = [(mask, sign) for mask, sign in matches if graph & mask == mask]
            assert len(available) == perm and sum(sign for _, sign in available) == det
            assert perm - det == 2 * sum(sign < 0 for _, sign in available)
            assert det % 2 == perm % 2
            hamiltonian = sum(mask in long_cycles for mask, _ in available)
            assert hamiltonian == sum(graph & mask == mask for mask in long_cycles)
            assert hamiltonian == from_principal_minors(rows), (n, graph)
            if graph & loops == loops:
                has_even_cycle = any(graph & mask == mask for mask in even)
                assert (perm == det) == (not has_even_cycle), (n, graph)
                loop_cases += 1
            cases += 1
    print(f"{cases:,} graph and principal-minor counts agree, including the even-cycle rule "
          f"on {loop_cases:,} boards with all loops.")


if __name__ == "__main__":
    check_orders()
