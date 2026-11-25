"""Certify the height boundaries and starting count for the four-loop sweep.

Requires python-flint. The companion loop replay checks the eight folds.
"""

from fractions import Fraction

from flint import acb_series, arb, ctx

from check_davenport_heilbronn_window import segment, winding
from check_mirror_mix_contacts import I, hurwitz_parts, line, point_jets, root_number, wronskian
from check_mirror_mix_loops import factors


def imaginary_product(s, epsilon):
    a, b = factors(s, epsilon)
    return (a * b.conjugate()).imag


def horizontal_panels(left, right, t, epsilon, depth=0):
    strip = segment((left, t), (right, t))
    if imaginary_product(strip, epsilon) < 0:
        return 1
    if depth == 22:
        raise ValueError(f"Could not exclude a crossing at height {t} over [{left}, {right}]")
    middle = (left + right) / 2
    return (horizontal_panels(left, middle, t, epsilon, depth + 1)
            + horizontal_panels(middle, right, t, epsilon, depth + 1))


def check_horizontal(t, epsilon):
    left, right = Fraction(1, 2), Fraction(501, 1000)
    strip = segment((left, t), (right, t))
    a, b = factors(acb_series([strip, 1], prec=2), epsilon)
    derivative = (a[1]*b[0].conjugate() + a[0]*b[1].conjugate()).imag
    # The value at 1/2 is exactly zero by the functional equation.
    assert derivative < 0
    panels = horizontal_panels(right, Fraction(4), t, epsilon)
    p, q = point_jets(line(arb(str(t))), 2)
    assert wronskian(p, q).abs_lower() > 0
    print(f"Height {t}: only the center-line point can be a zero, "
          f"and it can only be simple ({panels} horizontal panels).", flush=True)


def check_start(epsilon, low_height, high_height, expected):
    def pure(s):
        p, q = hurwitz_parts(s)
        return p + I*q

    # The Euler product for a single character and reflection exclude
    # zeros outside the real limits of this rectangle at this angle.
    left, right = Fraction(-1, 2), Fraction(3, 2)
    low, high = Fraction(low_height), Fraction(high_height)
    corners = [(left, low), (right, low), (right, high), (left, high)]
    count, panels = winding(pure, corners)
    assert count.contains(expected) and abs(count - expected) < arb("1/2")

    log_five, log_pi = arb(5).log(), arb.pi().log()
    inverse_phase = 1 / epsilon.sqrt()
    signs = []
    for step in range(20*(high_height - low_height) + 1):
        t = low + Fraction(step, 20)
        s = line(arb(str(t)))
        k = (s + 1) / 2
        completion = (k*(log_five - log_pi) - s*log_five).exp() * k.gamma() * inverse_phase
        real_function = pure(s) * completion
        assert real_function.imag.contains(0)
        assert not real_function.real.contains(0)
        signs.append(real_function.real > 0)
    brackets = sum(a != b for a, b in zip(signs, signs[1:]))
    assert brackets == expected
    print(f"At angle zero: {expected} zeros in all ({panels} winding panels) "
          f"and {brackets} distinct intervals with a sign change.")


def check_outer_half_planes(epsilon):
    # For Re(s) >= 4 both L-series differ from 1 by at most
    # sum(n^-4, n >= 2) <= 2^-4 + integral(2, infinity, x^-4) = 5/48.
    tail = Fraction(5, 48)
    assert 2*tail + tail**2 < Fraction(1, 4) and epsilon.imag > arb("1/2")
    print("All real mixtures are zero-free for Re(s) >= 4, and by reflection for Re(s) <= -3.")


if __name__ == "__main__":
    ctx.dps = 43
    epsilon = root_number()
    check_outer_half_planes(epsilon)
    for height in (Fraction(76), Fraction(96)):
        check_horizontal(height, epsilon)
    check_start(epsilon, 76, 96, 14)
