"""Certify the whole window from the Davenport–Heilbronn phase portrait.

Requires python-flint. Run after check_davenport_heilbronn_disks.py, which
separately certifies the two off-line zeros in this window.
"""

from fractions import Fraction

from flint import acb, arb, ctx

from check_davenport_heilbronn_disks import combination, exact_kappa


CORNERS = [
    (Fraction(-1, 2), Fraction(76)),
    (Fraction(3, 2), Fraction(76)),
    (Fraction(3, 2), Fraction(96)),
    (Fraction(-1, 2), Fraction(96)),
]
ZETA_HEIGHTS = (
    "77.144840", "79.337375", "82.910381", "84.735493", "87.425275",
    "88.809111", "92.491899", "94.651344", "95.870634",
)
DH_HEIGHTS = (
    "77.226418", "78.717410", "80.327947", "81.925402", "83.108841",
    "87.647476", "89.439189", "90.724505", "92.182744", "93.780944",
    "95.348661",
)


def point(coords):
    return acb(*(arb(str(coord)) for coord in coords))


def segment(start, end):
    return acb(*(arb(str((a + b) / 2), arb(str(abs(a - b) / 2)))
                 for a, b in zip(start, end)))


def increments(function, start, end, depth=0):
    # The rectangular image enclosure is convex. When it excludes the
    # origin, the entire image curve turns by its principal endpoint angle.
    if function(segment(start, end)).abs_lower() > 0:
        yield (function(point(end)) / function(point(start))).arg()
        return
    if depth == 20:
        raise ValueError(f"Could not exclude a boundary zero on {start} to {end}")
    middle = tuple((a + b) / 2 for a, b in zip(start, end))
    yield from increments(function, start, middle, depth + 1)
    yield from increments(function, middle, end, depth + 1)


def winding(function, corners=CORNERS):
    angles = [angle for a, b in zip(corners, corners[1:] + corners[:1])
              for angle in increments(function, a, b)]
    return sum(angles, arb(0)) / (2 * arb.pi()), len(angles)


def brackets(completed, heights):
    radius = arb("1e-5")
    centers = list(map(arb, heights))
    assert all(a + radius < b - radius for a, b in zip(centers, centers[1:]))
    assert arb(76) < centers[0] - radius and centers[-1] + radius < arb(96)
    for t in centers:
        before = completed(acb(arb("1/2"), t - radius)).real
        after = completed(acb(arb("1/2"), t + radius)).real
        assert before * after < 0, (t, before, after)


def check():
    ctx.dps = 45
    kappa = exact_kappa()
    pi_log = arb.pi().log()
    five_log = arb(5).log()

    def dh(s):
        return combination(s, kappa)

    def completed_zeta(s):
        return s * (s - 1) / 2 * (-s * pi_log / 2).exp() * (s / 2).gamma() * s.zeta()

    def completed_dh(s):
        return (-s * (five_log + pi_log) / 2).exp() * ((s + 1) / 2).gamma() * dh(s)

    check_cases = (
        ("Zeta", acb.zeta, completed_zeta, 9, ZETA_HEIGHTS),
        ("Davenport–Heilbronn", dh, completed_dh, 13, DH_HEIGHTS),
    )
    for name, function, completed, expected, heights in check_cases:
        count, panels = winding(function)
        assert count.contains(expected) and abs(count - expected) < arb("1/2"), count
        brackets(completed, heights)
        print(f"{name}: winding {count}, {panels} certified panels, "
              f"{len(heights)} disjoint line brackets.")

    count, _ = winding(lambda s: s - acb(arb("1/2"), 86))
    assert count.contains(1) and abs(count - 1) < arb("1/2"), count
    try:
        winding(lambda s: s - acb(arb("3/2"), 86))
    except ValueError:
        print("Controls passed: one interior root, a boundary root refused.")
    else:
        raise AssertionError("The boundary-root control was accepted")


if __name__ == "__main__":
    check()
