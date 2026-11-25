"""Certify all departures and returns of the mod-five mixtures through height 201.

Requires python-flint. The real-axis argument in crew_visuals/spira_real_axis.txt
is the analytic lower-boundary certificate. It also gives a quarter-plane for
the two endpoint phases in the pure character's reflected contour at height 0.
"""

import argparse
from contextlib import nullcontext, redirect_stdout
from fractions import Fraction
import json
import sys

from flint import acb, arb, ctx

from check_davenport_heilbronn_first_200 import count_by_reflection
from check_davenport_heilbronn_window import increments
from check_mirror_mix_band import check_horizontal, check_outer_half_planes
from check_mirror_mix_contacts import I, check_contacts_in_band, hurwitz_parts, root_number
from check_spira_gaps import angle_derivative_is_positive, line_brackets


BANDS = ((0, 76, 37, 18), (76, 177, 74, 40), (177, 201, 20, 8))
STEP = Fraction(1, 20)


def locate_candidates(low, high, epsilon):
    """Suggest centers by sign, then let the interval proof exclude every gap."""
    previous = Fraction(low)
    sign = angle_derivative_is_positive(previous, epsilon)
    for tick in range(1, int((high-low)/STEP)+1):
        current = low + tick*STEP
        new_sign = angle_derivative_is_positive(current, epsilon)
        if sign != new_sign:
            left, right = previous, current
            for _ in range(49):
                midpoint = (left + right) / 2
                if angle_derivative_is_positive(midpoint, epsilon) == sign:
                    left = midpoint
                else:
                    right = midpoint
            yield str((left + right) / 2)
        previous, sign = current, new_sign


def count_from_real_axis(completed, high):
    half, right = Fraction(1, 2), Fraction(4)
    # P and Q are both positive on the bottom edge. After removing the
    # constant phase all completed values there lie in the first quadrant.
    # The net bottom turn therefore equals the principal endpoint turn,
    # without evaluating an interval over the individually singular zetas.
    bottom = (completed(acb(4)) / completed(acb(arb("1/2")))).arg()
    assert abs(bottom) < arb.pi()/2
    path = [(right, Fraction(t)) for t in range(high+1)] + [(half, Fraction(high))]
    parts = [bottom]
    parts.extend(angle for a, b in zip(path, path[1:]) for angle in increments(completed, a, b))
    winding = sum(parts, arb(0)) / arb.pi()
    count = round(float(winding.mid()))
    assert winding.contains(count) and abs(winding-count) < arb("1/2")
    return count, len(parts)


def pure_count(low, high, epsilon):
    phase = epsilon.sqrt()
    log_scale = (arb(5).log() + arb.pi().log()) / 2

    def completed(s):
        p, q = hurwitz_parts(s)
        return (p + I*q) * (-s*log_scale).exp() * ((s+1)/2).gamma() / phase

    if low == 0:
        count, panels = count_from_real_axis(completed, high)
    else:
        count, panels = count_by_reflection(completed, Fraction(low), Fraction(high))
    brackets = line_brackets(completed, Fraction(low), Fraction(high), Fraction(1, 40))
    assert brackets == count
    return count, panels


def order_events(events):
    result = sorted(events, key=lambda event: float(event[0].mid()))
    assert all(a[0] < b[0] for a, b in zip(result, result[1:]))
    return result


def count_at(events, angle):
    count = 0
    for event, change in events:
        assert event < angle or event > angle, (event, angle)
        if event < angle:
            count += change
    return count


def summarize(events):
    maximum = count = 0
    peaks = []
    for index, (angle, direction) in enumerate(events):
        count += direction
        assert count >= 0
        if count > maximum:
            maximum, peaks = count, []
        if count == maximum and count > 0:
            peaks.append((angle, events[index+1][0]))
    assert count == 0
    return maximum, peaks


def check():
    ctx.dps = 60
    epsilon = root_number()
    check_outer_half_planes(epsilon)
    for height in (76, 177, 201):
        check_horizontal(height, epsilon)

    bands = []
    for low, high, expected_zeros, expected_contacts in BANDS:
        pure, winding_panels = pure_count(low, high, epsilon)
        assert pure == expected_zeros
        candidates = list(locate_candidates(low, high, epsilon))
        angles, exclusion_panels = check_contacts_in_band(candidates, low, high)
        assert len(angles) == expected_contacts
        events = order_events([(angle, -1 if curve > 0 else 1) for angle, curve in angles])
        band_maximum, _ = summarize(events)
        print(f"Heights {low}–{high}: {pure} pure-character zeros on the line "
              f"({winding_panels} winding panels), {len(events)} contacts "
              f"({exclusion_panels} exclusion panels) and up to {band_maximum} pairs.", flush=True)
        bands.append(events)

    total = order_events([event for events in bands for event in events])
    maximum, peaks = summarize(total)
    assert maximum == 27 and len(peaks) == 2
    assert [count_at(events, 45) for events in bands] == [0, 4, 0]
    assert [count_at(events, 135) for events in bands] == [8, 15, 4]
    rounded = [[(round(float(angle.mid()), 9), jump) for angle, jump in events] for events in bands]
    # The page uses tenths of a degree. Compare every selectable count with
    # the corresponding exact interval result before publishing sample data.
    for tick in range(1801):
        cut = arb(tick) / 10
        for events, display in zip(bands, rounded):
            assert count_at(events, cut) == sum(jump for angle, jump in display if angle < tick/10)
    for left, right in peaks:
        print(f"{maximum} pairs from just after {left.str(11)}° to just before {right.str(11)}°.")
    return {"events": rounded, "peaks": [[float(left.mid()), float(right.mid())] for left, right in peaks]}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--plot-data", action="store_true")
    args = cli.parse_args()
    with redirect_stdout(sys.stderr) if args.plot_data else nullcontext():
        data = check()
    if args.plot_data:
        print(json.dumps(data, separators=(",", ":")))
