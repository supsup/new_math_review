"""Print the numerical trajectories embedded in the four-pair portrait.

Requires python-flint. The exact band and loop replays certify the curves'
existence. This tool samples their coordinates for the drawing.
"""

import json

from flint import acb, acb_series, arb, ctx

from check_davenport_heilbronn_disks import RIGHT_CENTERS
from check_mirror_mix_contacts import HEIGHTS, angle_and_curvature, root_number
from check_mirror_mix_loops import factors
from check_spira_mix_bands import BANDS


def continue_zero(start, tau, epsilon):
    radians = arb(tau) * arb.pi() / 180
    sine, cosine = radians.sin(), radians.cos()
    point = start
    for _ in range(24):
        a, b = factors(acb_series([point, 1], prec=2), epsilon)
        jet = a*cosine + b*sine
        if jet[0].abs_upper() < arb("1e-34"):
            assert point.real > arb("1/2")
            return point
        point = (point - jet[0]/jet[1]).mid()
    raise ValueError(f"Continuation failed at angle {tau}")


def contact(height):
    angle, _ = angle_and_curvature(arb(height))
    return float(angle.mid()), 0.5, float(height)


def sample_side(start, endpoint, epsilon):
    target, _, height = endpoint
    point = start
    result = []
    # Quadratic angle spacing approaches the square-root turn smoothly.
    divisions = 48
    for j in range(1, divisions):
        tau = target + (45 - target)*((divisions - j)/divisions)**2
        point = continue_zero(point, tau, epsilon)
        result.append((tau, float(point.real), float(point.imag)))
    result.append((target, 0.5, height))
    return result


def sample_loop(heights, spira_center, epsilon):
    return_height, leave_height = heights
    start, finish = contact(leave_height), contact(return_height)
    x, t, radius = map(arb, spira_center)
    center = acb(x, t)
    middle = continue_zero(center, 45, epsilon)
    assert (middle - center).abs_upper() < radius
    middle_point = (45, float(middle.real), float(middle.imag))
    points = sample_side(middle, start, epsilon)[::-1] + [middle_point] + sample_side(middle, finish, epsilon)
    assert all(a[0] < b[0] for a, b in zip(points, points[1:]))
    return [[round(value, 9) for value in point] for point in points]


if __name__ == "__main__":
    ctx.dps = 56
    epsilon = root_number()
    contact_pairs = (HEIGHTS[4:6], *(heights for _, _, heights in BANDS))
    for heights, center in zip(contact_pairs, RIGHT_CENTERS):
        print(json.dumps(sample_loop(heights, center, epsilon), separators=(",", ":")))
