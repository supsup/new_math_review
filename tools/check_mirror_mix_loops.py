"""Certify four reflected loops, with a zero-free boundary for each whole arc.

Requires python-flint. The contact verification and certified contour count
are shared with the two related replays.
"""

from fractions import Fraction

from flint import acb, acb_series, arb, ctx

from check_davenport_heilbronn_window import increments, segment, winding
from check_mirror_mix_contacts import (
    HEIGHTS,
    I,
    angle_and_curvature,
    check as check_contacts,
    hurwitz_parts,
    line,
    root_number,
)


# real limits, height limits, tan(angle) limits, middle tan(angle), and
# the height of a persistent line zero at that middle value, if present.
BOXES = (
    ("0", "1", "76.96", "77.50", "-1.278", "-0.422", "-1", None),
    ("-1.25", "2.25", "80.90", "83.98", "-6.030", "-0.337", "-1", "82.736896632364803137"),
    ("0", "1", "85.10", "86.00", "0.435", "12", "1", None),
    ("-1.25", "2.25", "88.47", "91.26", "-2.810", "-0.224", "-1", "90.524803797716229614"),
)


def factors(s, epsilon):
    p, q = hurwitz_parts(s)
    return p + I * q, epsilon * (p - I * q)


def excludes_ratio(first, second, lower, upper):
    if not second.abs_lower() > 0:
        return False
    ratio = -first / second
    return not ratio.imag.contains(0) or ratio.real < lower or ratio.real > upper


def boundary_panels(start, end, lower, upper, epsilon, depth=0):
    first, second = factors(segment(start, end), epsilon)
    if (excludes_ratio(first, second, lower, upper)
            or excludes_ratio(second, first, 1 / upper, 1 / lower)):
        return 1
    if depth == 22:
        raise ValueError(f"Boundary certificate failed between {start} and {end}")
    middle = tuple((a + b) / 2 for a, b in zip(start, end))
    return (boundary_panels(start, middle, lower, upper, epsilon, depth + 1)
            + boundary_panels(middle, end, lower, upper, epsilon, depth + 1))


def certify_simple_root(function, center, radius):
    width = arb(str(radius))
    point = function(acb_series([center, 1], prec=2))
    square = center + acb(arb(0, width.upper()), arb(0, width.upper()))
    derivative = function(acb_series([square, 1], prec=2))[1]
    difference = (derivative - point[1]).abs_upper()
    assert point[0].abs_upper() + width * difference < width * point[1].abs_lower()


def line_panels(function, low_height, high_height, root):
    half = Fraction(1, 2)
    if root is None:
        intervals = [(low_height, high_height)]
    else:
        height = Fraction(root)
        radius = Fraction(1, 10**4)
        assert low_height < height - radius and height + radius < high_height
        certify_simple_root(function, line(arb(str(height))), radius)
        intervals = [(low_height, height - radius), (height + radius, high_height)]
    return sum(1 for a, b in intervals for _ in increments(function, (half, a), (half, b)))


def the_two_contacts(index, lower, upper, low_height, high_height):
    centers = list(map(Fraction, HEIGHTS))
    in_box = [j for j, t in enumerate(centers) if low_height < t < high_height]
    assert in_box == [index * 2, index * 2 + 1]
    angles = []
    for j in in_box:
        angle, curvature = angle_and_curvature(arb(HEIGHTS[j]))
        assert (curvature > 0) == (j % 2 == 0)
        mix = (angle * arb.pi() / 180).tan()
        assert lower < mix < upper
        angles.append(mix)
    return angles[1], angles[0]  # leave, then return, with increasing angle


def check_loop(index, spec, epsilon):
    x0, x1, y0, y1, lower, upper, middle = map(Fraction, spec[:7])
    root = spec[7]
    assert x0 + x1 == 1 and (0 < lower < upper or lower < upper < 0)
    low, high, sample = (arb(str(r)) for r in (lower, upper, middle))
    leave, end = the_two_contacts(index, low, high, y0, y1)
    assert leave < sample < end
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    def function(s):
        first, second = factors(s, epsilon)
        return first + sample * second

    contour = sum(boundary_panels(a, b, low, high, epsilon)
                  for a, b in zip(corners, corners[1:] + corners[:1]))
    winding_number, _ = winding(function, corners)
    number = 2 + int(root is not None)
    assert winding_number.contains(number) and abs(winding_number - number) < arb("1/2")
    panels = line_panels(function, y0, y1, root)
    print(f"Heights {float(y0):.2f}–{float(y1):.2f}: {contour:,} uniform boundary panels, "
          f"{number} zeros, {number - 2} persistent line zeros, "
          f"{panels:,} line exclusion panels at the sample.", flush=True)


if __name__ == "__main__":
    check_contacts()
    ctx.dps = 43
    epsilon = root_number()
    for i, box in enumerate(BOXES):
        check_loop(i, box, epsilon)
    assert not excludes_ratio(acb(-1), acb(1), arb("1/2"), arb(2))
    print("All four boxes certify a unique reflected pair from leave to return.")
