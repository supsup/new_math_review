"""Certify the three gaps between the bands containing Spira's four pairs.

Requires python-flint (replayed with 0.6.0). The gap calculation proves that
no angle from 0 to 90 degrees produces an off-line zero in any gap. The
separate --fixed-angle check counts the entire 76–177 band at 45 degrees.
"""

import argparse
from fractions import Fraction

from flint import acb, acb_series, arb, ctx

from check_davenport_heilbronn_disks import RIGHT_CENTERS, bounds, combination, exact_kappa
from check_davenport_heilbronn_window import winding
from check_mirror_mix_band import check_horizontal
from check_mirror_mix_contacts import (
    I,
    LOCAL_RADIUS,
    TIGHT_RADIUS,
    angle_and_curvature,
    exclude_between,
    hurwitz_parts,
    line,
    local_certificate,
    point_jets,
    root_number,
    wronskian,
)


# The latter two columns are the expected numbers of contacts and pure-angle zeros.
GAPS = ((96, 113, 6, 12), (115, 166, 16, 38), (167, 176, 4, 7))
STEP = Fraction(1, 20)


def angle_derivative_is_positive(height, epsilon):
    p, q = point_jets(line(arb(str(height))), 2)
    direct = p[0] + I*q[0]
    conjugate = epsilon * (p[0] - I*q[0])
    # Differentiate -atan(direct/conjugate), then combine denominators.
    value = 2*epsilon * wronskian(p, q) / (direct**2 + conjugate**2)
    assert value.imag.contains(0) and not value.real.contains(0), height
    return value.real > 0


def certify_contacts(lower, upper, epsilon):
    previous = lower
    sign = angle_derivative_is_positive(previous, epsilon)
    centers = []
    for j in range(1, int((upper - lower) / STEP) + 1):
        endpoint = lower + j*STEP
        next_sign = angle_derivative_is_positive(endpoint, epsilon)
        if sign != next_sign:
            left, right = previous, endpoint
            for _ in range(49):
                middle = (left + right) / 2
                if angle_derivative_is_positive(middle, epsilon) == sign:
                    left = middle
                else:
                    right = middle
            center = (left + right) / 2
            height = arb(str(center))
            for radius in (LOCAL_RADIUS, TIGHT_RADIUS):
                assert local_certificate(line(height), arb(str(radius))) < 1, center
            angle, curvature = angle_and_curvature(height)
            assert angle > 90, (center, angle)
            print(f"  t={height.str(15)}, angle={angle.str(14)}, "
                  f"{'return' if curvature > 0 else 'leave'}", flush=True)
            centers.append(center)
        previous, sign = endpoint, next_sign
    starts = [lower] + [t + LOCAL_RADIUS for t in centers]
    stops = [t - LOCAL_RADIUS for t in centers] + [upper]
    assert all(a < b for a, b in zip(starts, stops))
    exclusion_panels = sum(exclude_between(a, b) for a, b in zip(starts, stops))
    return len(centers), exclusion_panels


def rectangle(left, right, lower, upper):
    return [(left, lower), (right, lower), (right, upper), (left, upper)]


def count_winding(function, corners):
    count, panels = winding(function, corners)
    integer = round(float(count.mid()))
    assert count.contains(integer) and abs(count - integer) < arb("1/2"), count
    return integer, panels


def line_brackets(function, lower, upper, step):
    signs = []
    for j in range(int((upper - lower) / step) + 1):
        value = function(line(arb(str(lower + j*step))))
        assert value.imag.contains(0) and not value.real.contains(0)
        signs.append(value.real > 0)
    return sum(a != b for a, b in zip(signs, signs[1:]))


def check_gaps():
    ctx.dps = 62
    epsilon = root_number()
    log_five, log_pi = arb(5).log(), arb.pi().log()
    assert epsilon.imag > arb("1/2")  # the uniform far-half-plane estimate from the band replay

    def pure(s):
        p, q = hurwitz_parts(s)
        return p + I*q

    def completed(s):
        k = (s + 1) / 2
        completion = (k*(log_five - log_pi) - s*log_five).exp() * k.gamma()
        return pure(s) * completion / epsilon.sqrt()

    for lo, hi, expected_contacts, expected_zeros in GAPS:
        lower, upper = Fraction(lo), Fraction(hi)
        print(f"Gap {lower}–{upper}:", flush=True)
        for height in (lower, upper):
            check_horizontal(height, epsilon)
        contacts, gap_panels = certify_contacts(lower, upper, epsilon)
        assert contacts == expected_contacts
        sides = rectangle(Fraction(-1, 2), Fraction(3, 2), lower, upper)
        zeros, winding_panels = count_winding(pure, sides)
        assert zeros == expected_zeros == line_brackets(completed, lower, upper, STEP)
        print(f"{contacts} contacts, all above 90 degrees ({gap_panels} exclusion panels); "
              f"{zeros} initial zeros, all on the line ({winding_panels} winding panels).", flush=True)


def check_fixed_angle():
    ctx.dps = 48
    start, end = Fraction(76), Fraction(177)
    kappa = exact_kappa()
    log_five, log_pi = arb(5).log(), arb.pi().log()

    def mixture(s):
        return combination(s, kappa)

    def completed(s):
        return mixture(s) * (-s*(log_five + log_pi)/2).exp() * ((s + 1)/2).gamma()

    corners = rectangle(Fraction(-3), Fraction(4), start, end)
    zero_count, panels = count_winding(mixture, corners)
    brackets = line_brackets(completed, start, end, Fraction(1, 40))

    for x, t, radius in RIGHT_CENTERS:
        center = acb(arb(x), arb(t))
        width = arb(radius)
        assert arb("1/2") < arb(x) - width and arb(x) + width < arb(4)
        assert arb(t) - width > arb(start.numerator) and arb(t) + width < arb(end.numerator)
        jet = mixture(acb_series([center, 1], prec=2))
        offset, variation, signal = bounds(center, width, jet, kappa)
        assert offset + variation < signal
    intervals = [(arb(t) - arb(radius), arb(t) + arb(radius)) for _, t, radius in RIGHT_CENTERS]
    assert all(a[1] < b[0] for a, b in zip(intervals, intervals[1:]))

    # Reflection across Re(s)=1/2 supplies a separate left disk for every right disk.
    assert zero_count == brackets + 2*len(RIGHT_CENTERS)
    print(f"Angle 45, entire 76–177 band: {zero_count} zeros ({panels} winding panels), "
          f"{brackets} line brackets, and exactly {len(RIGHT_CENTERS)} reflected off-line pairs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixed-angle", action="store_true", help="also count the entire band at 45 degrees")
    args = parser.parse_args()
    check_gaps()
    if args.fixed_angle:
        check_fixed_angle()
