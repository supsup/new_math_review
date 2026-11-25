"""Certify the off-line crossing at height 200 using python-flint."""

import argparse
from fractions import Fraction
import json

from flint import acb_series, arb, ctx

from check_davenport_heilbronn_window import segment
from check_mirror_mix_band import check_outer_half_planes, imaginary_product
from check_mirror_mix_contacts import root_number
from check_mirror_mix_loops import factors


HEIGHT = 200
SIGMA_LOW, SIGMA_HIGH = map(Fraction, ("1.2270615302723483", "1.2270615302723484"))


def strip(left, right):
    return segment((left, HEIGHT), (right, HEIGHT))


def derivative(left, right, epsilon):
    first, second = factors(acb_series([strip(left, right), 1], prec=2), epsilon)
    return (first[1]*second[0].conjugate() + first[0]*second[1].conjugate()).imag


def sign_panels(left, right, sign, epsilon, depth=0):
    if sign * imaginary_product(strip(left, right), epsilon) > 0:
        return 1
    if depth == 24:
        raise ValueError(f"Couldn't certify the sign between {left} and {right}")
    middle = (left + right) / 2
    return (sign_panels(left, middle, sign, epsilon, depth+1)
            + sign_panels(middle, right, sign, epsilon, depth+1))


def enclose_crossing(epsilon):
    half, near, left, right = map(Fraction, ("0.5", "0.501", "1.226", "1.228"))
    assert derivative(half, near, epsilon) > 0
    up = sign_panels(near, left, 1, epsilon)
    down = sign_panels(right, Fraction(4), -1, epsilon)
    assert derivative(left, right, epsilon) < 0
    assert left < SIGMA_LOW < SIGMA_HIGH < right
    assert imaginary_product(strip(SIGMA_LOW, SIGMA_LOW), epsilon) > 0
    assert imaginary_product(strip(SIGMA_HIGH, SIGMA_HIGH), epsilon) < 0

    first, second = factors(acb_series([strip(SIGMA_LOW, SIGMA_HIGH), 1], prec=2), epsilon)
    assert second[0].abs_lower() > 0
    ratio = first / second
    assert ratio[0].imag.contains(0) and ratio[0].real > 0
    angle = 180 - ratio[0].real.atan() * 180 / arb.pi()
    assert arb("122.2446141504885") < angle < arb("122.2446141504887")
    assert ratio[1].imag < 0
    velocity = -(1 + ratio[0].real**2) / ratio[1]
    assert velocity.imag < 0
    return ratio[0].real, angle, velocity.imag, up, down


def plot_data(epsilon):
    # The sampled graph is for display. The signs and monotonicity proof above
    # handle the intervals between samples.
    out = []
    for step in range(101):
        x = Fraction(1) + Fraction(step, 200)
        first, second = factors(strip(x, x), epsilon)
        ratio = first / second
        out.append([round(float(ratio.real.mid()), 9), round(float(ratio.imag.mid()), 9)])
    return out


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--plot-data", action="store_true")
    args = cli.parse_args()
    ctx.dps = 65
    epsilon = root_number()
    if args.plot_data:
        print(json.dumps(plot_data(epsilon), separators=(",", ":")))
    else:
        check_outer_half_planes(epsilon)
        ratio, angle, velocity, up, down = enclose_crossing(epsilon)
        print(f"Exactly one crossing at height {HEIGHT} to the right of the center line.")
        print(f"Real part between {arb(str(SIGMA_LOW)).mid()} and {arb(str(SIGMA_HIGH)).mid()}.")
        print(f"Ratio {ratio.str(16)}, angle {angle.str(17)} degrees.")
        print(f"Vertical velocity {velocity.str(10)} per radian. The root moves down as the angle increases.")
        print(f"Bounded both sides with {up} positive and {down} negative interval panels.")
