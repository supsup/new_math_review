#!/usr/bin/env python3
"""Check the extremal cycles and additive envelopes in the min-plus visual."""

from fractions import Fraction
from itertools import permutations, product
from random import Random


def min_plus(a, b):
    return [
        [min(a[i][j] + b[j][k] for j in range(len(b))) for k in range(len(b[0]))]
        for i in range(len(a))
    ]


def layered_graph(a, b, c):
    rows, mid, cols = len(a), len(b), len(b[0])
    target = rows + mid
    edges = [(i, rows + j, a[i][j]) for i, j in product(range(rows), range(mid))]
    edges += [(rows + j, target + k, b[j][k]) for j, k in product(range(mid), range(cols))]
    edges += [(target + k, i, -c[i][k]) for k, i in product(range(cols), range(rows))]
    return target + cols, edges


def feasible_potentials(n, edges):
    """Bellman–Ford with a zero-weight auxiliary source to every vertex."""
    values = [0] * n
    for _ in range(n):
        changed = False
        for source, dest, weight in edges:
            new = values[source] + weight
            if new < values[dest]:
                values[dest] = new
                changed = True
        if not changed:
            return values
    return None


def row_costs(d, c):
    return [
        [min(a - b for a, b in zip(product_row, candidate_row)) for candidate_row in c]
        for product_row in d
    ]


def minimum_cycle_mean(costs, sizes):
    means = []
    for size in sizes:
        for cycle in permutations(range(len(costs)), size):
            if cycle[0] != min(cycle):
                continue
            total = sum(costs[i][j] for i, j in zip(cycle, cycle[1:] + cycle[:1]))
            means.append(Fraction(total, size))
    return min(means)


def check_instance(a, b, c):
    d = min_plus(a, b)
    n, edges = layered_graph(a, b, c)
    original = feasible_potentials(n, edges)

    # The reduced graph arises by eliminating the column variables of the additive envelope.
    costs = row_costs(d, c)
    rows = feasible_potentials(len(d), [(i, j, w) for i, row in enumerate(costs)
                                       for j, w in enumerate(row)])
    mean = minimum_cycle_mean(costs, range(1, len(d) + 1))
    assert (original is None) == (rows is None) == (mean < 0), (d, c)
    if rows is None:
        return

    targets = [max(rows[i] + c[i][k] for i in range(len(rows))) for k in range(len(c[0]))]
    middle = [min(rows[i] + a[i][j] for i in range(len(rows))) for j in range(len(b))]
    lifted = rows + middle + targets
    assert all(lifted[v] - lifted[u] <= w for u, v, w in edges), (d, c)
    assert all(c[i][k] <= targets[k] - rows[i] <= d[i][k]
               for i, k in product(range(len(rows)), range(len(targets)))), (d, c)


def identity_costs(n):
    return [[0 if j == k else 32 for k in range(n)] for j in range(n)]


def check_two_by_two():
    b = identity_costs(2)
    count = 0
    for a, b0, c0, d0 in product(range(-2, 3), repeat=4):
        d = [[a, b0], [c0, d0]]
        assert min_plus(d, b) == d
        mixed = a + d0 - b0 - c0
        threshold = Fraction(abs(mixed), 2)
        assert -minimum_cycle_mean(row_costs(d, d), (1, 2)) == threshold
        for twice_slack in range(9):
            slack = Fraction(twice_slack, 2)
            c = [[value - slack for value in row] for row in d]
            n, edges = layered_graph(d, b, c)
            assert (feasible_potentials(n, edges) is not None) == (slack >= threshold)
            check_instance(d, b, c)
            count += 1
    return count


def check_nine_edges():
    d = [[0, 1, 2], [2, 0, 1], [1, 2, 0]]
    b = identity_costs(3)
    assert min_plus(d, b) == d
    worst_rectangle = max(abs(d[i][k] + d[j][l] - d[i][l] - d[j][k])
                          for i, j, k, l in product(range(3), repeat=4))
    assert worst_rectangle == 3
    assert minimum_cycle_mean(row_costs(d, d), (1, 2)) == Fraction(-3, 2)
    assert minimum_cycle_mean(row_costs(d, d), (1, 2, 3)) == -2
    for twice_slack in range(11):
        slack = Fraction(twice_slack, 2)
        c = [[value - slack for value in row] for row in d]
        n, edges = layered_graph(d, b, c)
        edge_weights = {(u, v): w for u, v, w in edges}
        cycle = [0, 3, 6, 1, 4, 7, 2, 5, 8, 0]
        assert sum(edge_weights[u, v] for u, v in zip(cycle, cycle[1:])) == 3 * (slack - 2)
        assert (feasible_potentials(n, edges) is not None) == (slack >= 2)
        check_instance(d, b, c)
    return 11


def check_more_examples():
    rng = Random(380)
    for _ in range(400):
        rows, middle, cols = (rng.randint(2, 4) for _ in range(3))
        a = [[rng.randint(-5, 5) for _ in range(middle)] for _ in range(rows)]
        b = [[rng.randint(-5, 5) for _ in range(cols)] for _ in range(middle)]
        d = min_plus(a, b)
        c = [[value - rng.randint(-1, 4) for value in row] for row in d]
        check_instance(a, b, c)
    return 400


def rectangle_gap(d):
    return max(max(d[i][k] - d[j][k] for k in range(len(d[0])))
               - min(d[i][k] - d[j][k] for k in range(len(d[0])))
               for i, j in product(range(len(d)), repeat=2))


def check_rectangle_bound():
    rng = Random(381)
    for _ in range(250):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        d = [[rng.randint(-7, 7) for _ in range(cols)] for _ in range(rows)]
        diameter = rectangle_gap(d)
        size = min(rows, cols)
        threshold = -minimum_cycle_mean(row_costs(d, d), range(1, rows + 1))
        assert Fraction(diameter, 2) <= threshold <= Fraction((size - 1) * diameter, size)

    for size in range(2, 13):
        d = [[(k - i) % size for k in range(size)] for i in range(size)]
        assert rectangle_gap(d) == size
        costs = row_costs(d, d)
        assert min(map(min, costs)) == 1 - size
        assert all(costs[i][(i + 1) % size] == 1 - size for i in range(size))
        # The zero envelope is feasible at slack size - 1, and that cycle is
        # negative below size - 1. Check both in the full tripartite graph.
        b = identity_costs(size)
        assert min_plus(d, b) == d
        for slack, feasible in [(Fraction(2 * size - 3, 2), False), (size - 1, True)]:
            c = [[value - slack for value in row] for row in d]
            n, edges = layered_graph(d, b, c)
            assert (feasible_potentials(n, edges) is not None) == feasible
    return 250 + 11


if __name__ == "__main__":
    total = check_two_by_two() + check_nine_edges() + check_more_examples()
    print(f"Verified {total:,} exact layered-graph and additive-envelope cases.")
    count = check_rectangle_bound()
    print(f"Verified the sharp rectangle bound on {count} further exact matrices.")
