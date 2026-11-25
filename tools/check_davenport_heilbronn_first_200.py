"""Certify every Davenport–Heilbronn zero of height 0 through 200."""

from fractions import Fraction
from math import ceil

from flint import acb, arb, ctx

from check_davenport_heilbronn_disks import RIGHT_CENTERS, combination, exact_kappa
from check_davenport_heilbronn_window import increments
from check_mirror_mix_band import check_outer_half_planes
from check_mirror_mix_contacts import root_number
from check_mirror_mix_loops import certify_simple_root
from check_spira_gaps import line_brackets


def count_by_reflection(completed, low, high):
    half, right = Fraction(1, 2), Fraction(4)
    # Reflection conjugates the values and reverses the orientation of this
    # part of the contour. Both signs change, so the argument change doubles.
    heights = [low] + [Fraction(t) for t in range(ceil(low), ceil(high)) if t > low] + [high]
    path = [(half, low)] + [(right, t) for t in heights] + [(half, high)]
    parts = [angle for a, b in zip(path, path[1:]) for angle in increments(completed, a, b)]
    winding = sum(parts, arb(0)) / arb.pi()
    count = round(float(winding.mid()))
    assert winding.contains(count) and abs(winding - count) < arb("1/2")
    return count, len(parts)


def check_starting_height(kappa):
    assert 0 < kappa < arb("1/3")
    # The coefficient partial sums are 1, 1+kappa, 1, 0, 0, periodically.
    # For x in [1/2,4], the real part of L(s)/s at height t is bounded below by
    # integral_0^log(2) exp(-4u) du minus
    # (1+kappa) * t^2/2 * integral_0^infinity exp(-u/2) * u^2 du.
    assert Fraction(15, 64) > Fraction(4, 3)*Fraction(1, 2)*Fraction(1, 10)**2*16
    print("The starting band 0–0.1 is clear by the partial-sum estimate.", flush=True)


def check():
    ctx.dps = 46
    kappa = exact_kappa()
    check_outer_half_planes(root_number())
    check_starting_height(kappa)
    log_scale = (arb(5).log() + arb.pi().log()) / 2

    def unscaled(s):
        return combination(s, kappa)

    def completed(s):
        return unscaled(s) * (-s*log_scale).exp() * ((s + 1)/2).gamma()

    for x, t, radius in RIGHT_CENTERS:
        cx, height, r = map(arb, (x, t, radius))
        assert cx - r > arb("1/2") and cx + r < 4
        assert height - r > 76 and height + r < 177
        certify_simple_root(unscaled, acb(cx, height), Fraction(radius))
    intervals = [(arb(t) - arb(r), arb(t) + arb(r)) for _, t, r in RIGHT_CENTERS]
    assert all(a[1] < b[0] for a, b in zip(intervals, intervals[1:]))

    bands = ((Fraction(1, 10), Fraction(76), 38, 0),
             (Fraction(76), Fraction(177), 66, 8),
             (Fraction(177), Fraction(200), 18, 0))
    for low, high, on_line, off_line in bands:
        count, panels = count_by_reflection(completed, low, high)
        brackets = line_brackets(completed, low, high, Fraction(1, 40))
        assert count == on_line + off_line and brackets == on_line
        print(f"Heights {float(low):g}–{float(high):g}: {count} zeros, {brackets} on the line, "
              f"{off_line} off it ({panels:,} right-hand contour panels).", flush=True)
    print("Heights 0–200: exactly 130 zeros, 122 on the line and four reflected pairs.")

    center = acb(arb("1/2"), 1)
    assert count_by_reflection(lambda s: (s-center)**2 - arb("1/4"),
                               Fraction(0), Fraction(2))[0] == 2


if __name__ == "__main__":
    check()
