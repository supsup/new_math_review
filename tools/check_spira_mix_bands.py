"""Certify the three higher Davenport–Heilbronn loops, including their Spira zeros.

Requires python-flint. Reuses the all-angle edge exclusions and fold checker.
"""

from fractions import Fraction

from flint import acb, arb, ctx

from check_davenport_heilbronn_disks import RIGHT_CENTERS
from check_mirror_mix_band import check_horizontal, check_outer_half_planes, check_start
from check_mirror_mix_contacts import check_contacts_in_band, root_number
from check_mirror_mix_loops import certify_simple_root, factors


# Band endpoints and contact heights in increasing height order (return, leave).
BANDS = (
    (113, 115, ("114.0338515711900894310342", "114.3382647454014236959818")),
    (166, 167, ("166.2619941907352538055078", "166.5047133326857057284789")),
    (176, 177, ("176.5189286017706911956296", "176.9666449706007124099822")),
)


def check_band(low, high, contact_heights, spira_center, epsilon):
    print(f"Heights {low}–{high}", flush=True)
    for height in (low, high):
        check_horizontal(Fraction(height), epsilon)
    check_start(epsilon, low, high, 1)
    angles, panels = check_contacts_in_band(contact_heights, low, high)
    (return_angle, return_curve), (leave_angle, leave_curve) = angles
    assert return_curve > 0 and leave_curve < 0
    assert 0 < leave_angle < 45 < return_angle < 90
    print(f"Two folds only ({panels} intervening panels), "
          f"at {leave_angle.str(14)}° and {return_angle.str(14)}°.")

    def davenport_heilbronn(s):
        first, second = factors(s, epsilon)
        return first + second

    x, t, radius = spira_center
    real, imag, width = map(arb, (x, t, radius))
    assert real - width > arb("1/2")
    assert low < imag - width and imag + width < high
    certify_simple_root(davenport_heilbronn, acb(real, imag), Fraction(radius))
    # Reflection puts a single partner in the other half of the band.
    print(f"Spira's pair is on this loop at 45° (right disk {x}+{t}i, radius {radius}).", flush=True)


if __name__ == "__main__":
    ctx.dps = 52
    epsilon = root_number()
    check_outer_half_planes(epsilon)
    assert len(BANDS) == len(RIGHT_CENTERS) - 1
    for band, center in zip(BANDS, RIGHT_CENTERS[1:]):
        check_band(*band, center, epsilon)
