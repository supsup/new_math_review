"""Certify every center-line contact of the mod-5 real mixtures at heights 76–96.

Requires python-flint. The proof uses the Wronskian, so the common gamma
factor and the exponential factor in the two L-functions both cancel.
"""

from fractions import Fraction

from flint import acb, acb_series, arb, ctx


HEIGHTS = (
    "77.018839481133411160", "77.450969916572478909",
    "80.977613764173611431", "83.906566888804885584",
    "85.222670197057382194", "85.899025334951197533",
    "88.546597400030600378", "91.191884267233378128",
)
LOCAL_RADIUS = Fraction(1, 10**6)
TIGHT_RADIUS = Fraction(1, 10**12)
I = acb(0, 1)


def line(height):
    return acb(arb("1/2"), height)


def hurwitz_parts(s):
    a, b, c, d = [s.zeta(arb(f"{k}/5")) for k in range(1, 5)]
    return a - d, b - c


def root_number():
    """Root number of the primitive odd character with chi(2) = i."""
    return 2 / arb(5).sqrt() * acb((2 * arb.pi() / 5).sin(), (4 * arb.pi() / 5).sin())


def point_jets(s, order):
    return hurwitz_parts(acb_series([s, 1], prec=order))


def wronskian(p, q):
    return p[0] * q[1] - p[1] * q[0]


def wronskian_derivative(p, q):
    return 2 * (p[0] * q[2] - p[2] * q[0])


def local_certificate(center, radius):
    p, q = point_jets(center, 3)
    width = radius.upper()
    box = center + acb(arb(0, width), arb(0, width))
    box_p, box_q = point_jets(box, 3)
    assert (box_p[0] - I * box_q[0]).abs_lower() > 0
    box_derivative = wronskian_derivative(box_p, box_q)
    derivative = wronskian_derivative(p, q)
    error = wronskian(p, q).abs_upper() + radius * (box_derivative - derivative).abs_upper()
    return error / (radius * derivative.abs_lower())


def exclude_between(lower, upper, depth=0):
    center = arb(str((lower + upper) / 2))
    radius = arb(str((upper - lower) / 2))
    p, q = point_jets(line(arb(center, radius)), 3)
    if wronskian(p, q).abs_lower() > 0:
        return 1
    center_value = wronskian(*point_jets(line(center), 2))
    if center_value.abs_lower() > radius * wronskian_derivative(p, q).abs_upper():
        return 1
    if depth == 38:
        raise ValueError(f"Could not exclude a stationary root on [{lower}, {upper}]")
    middle = (lower + upper) / 2
    return exclude_between(lower, middle, depth + 1) + exclude_between(middle, upper, depth + 1)


def angle_and_curvature(t):
    radius = arb(str(TIGHT_RADIUS))
    p, q = point_jets(line(arb(t, radius)), 3)
    direct, conjugate = p[0] + I * q[0], p[0] - I * q[0]
    assert direct.abs_lower() > 0 and conjugate.abs_lower() > 0
    eps = root_number()
    ratio = direct / (eps * conjugate)
    assert ratio.imag.contains(0)
    angle = (-ratio.real).atan() * 180 / arb.pi()
    if angle < 0:
        angle += 180
    assert 0 < angle < 180, angle
    # At W = 0 the derivative of the denominator in theta' drops out.
    curvature = (2 * I * wronskian_derivative(p, q)
                 / (eps * conjugate**2 * (1 + ratio**2))).real
    assert not curvature.contains(0)
    return angle, curvature


def check_contacts_in_band(heights, low_height, high_height):
    angles = []
    for digits in heights:
        t = arb(digits)
        for radius in (LOCAL_RADIUS, TIGHT_RADIUS):
            ratio = local_certificate(line(t), arb(str(radius)))
            assert ratio < 1, (digits, radius, ratio)
        angle, curvature = angle_and_curvature(t)
        angles.append((angle, curvature))
        print(f"t = {digits} ± 1e-12, angle {angle.str(14)}°, "
              f"{'return' if curvature > 0 else 'leave'}", flush=True)

    exact_centers = list(map(Fraction, heights))
    starts = [Fraction(low_height)] + [t + LOCAL_RADIUS for t in exact_centers]
    ends = [t - LOCAL_RADIUS for t in exact_centers] + [Fraction(high_height)]
    assert all(a < b for a, b in zip(starts, ends))
    panels = sum(exclude_between(lo, hi) for lo, hi in zip(starts, ends))
    return angles, panels


def check():
    ctx.dps = 65
    angles, panels = check_contacts_in_band(HEIGHTS, 76, 96)
    assert all((curvature > 0) == (i % 2 == 0) for i, (_, curvature) in enumerate(angles))
    assert local_certificate(line(arb("85.8")), arb(str(TIGHT_RADIUS))) > 1
    print(f"All nine intervening intervals excluded in {panels} panels. "
          "Shifted-center control rejected.")


if __name__ == "__main__":
    check()
