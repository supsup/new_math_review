"""Replay the signed Farey discrepancy and its squared integral exactly."""

from fractions import Fraction
from math import gcd


def farey(order):
    points = [Fraction(0, 1)]
    points.extend(Fraction(a, b) for b in range(1, order + 1)
                  for a in range(1, b + 1) if gcd(a, b) == 1)
    return sorted(points)


def geometry(points, chi):
    """Integrate each linear piece of the discrepancy between jumps."""
    total = sum(chi(point.denominator) for point in points[1:])
    cumulative = 0
    integral = Fraction()
    for i, (u, v) in enumerate(zip(points, points[1:])):
        if i:
            cumulative += chi(u.denominator)
        left = cumulative - total * u + Fraction(1, 2)
        right = cumulative - total * v + Fraction(1, 2)
        integral += (v - u) * (left * left + left * right + right * right) / 3
    return total, integral


def mobius_to(limit):
    """Integer divisor recurrence, with mu(1)=1."""
    mu = [0, 1]
    for n in range(2, limit + 1):
        mu.append(-sum(mu[d] for d in range(1, n) if n % d == 0))
    return mu


def check():
    limit = 70
    mu = mobius_to(limit)
    cases, jumps = 0, 0
    for label, chi in (
        ("ordinary", lambda _: 1),
        ("mod 5", lambda n: (0, 1, -1, -1, 1)[n % 5]),
    ):
        prefix = [0]
        for n in range(1, limit + 1):
            prefix.append(prefix[-1] + chi(n) * mu[n])
        for n in range(2, limit + 1):
            points = farey(n)
            total, integral = geometry(points, chi)
            coefficients = [0] + [chi(j) * prefix[n // j] for j in range(1, n + 1)]
            assert sum(coefficients) == 1
            assert sum(j * coefficients[j] for j in range(1, n + 1)) == total
            cumulative = 0
            for point in points[1:]:
                a, b = point.numerator, point.denominator
                cumulative += chi(b)
                from_floors = sum(coefficients[j] * (j * a // b) for j in range(1, n + 1))
                assert cumulative == from_floors, (n, point)
                jumps += 1
            kernel = sum(
                Fraction(coefficients[j] * coefficients[k] * gcd(j, k)**2, 12 * j * k)
                for j in range(1, n + 1) for k in range(1, n + 1)
            )
            assert kernel == integral and kernel >= 0, (n, kernel, integral)
            if label == "ordinary":
                ranks = sum((point - Fraction(i, total))**2
                            for i, point in enumerate(points[1:], 1))
                assert integral == Fraction(1, 12) + total * ranks, n
            if label == "mod 5" and n == 5:
                assert total == 0 and kernel == Fraction(7, 12)
            cases += 1
    print(f"{cases} exact integrals and {jumps:,} cumulative counts agree.")


if __name__ == "__main__":
    check()
