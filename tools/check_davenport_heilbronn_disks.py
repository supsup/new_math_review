"""Certify one zero in each of eight small disks using FLINT ball arithmetic.

Install python-flint (tested with 0.6.0), then run this file. The optional
--plot-data flag emits rounded bounds for the interactive companion.
"""

import argparse
import json
from math import inf, nextafter

from flint import acb, acb_series, arb, ctx


RIGHT_CENTERS = [
    ("0.808517182", "85.699348485", "1e-8"),
    ("0.650830", "114.163343", "1e-6"),
    ("0.574356", "166.479306", "1e-6"),
    ("0.724258", "176.702461", "1e-6"),
]
RADIUS_SCALES = ("0.01", "0.05", "0.2", "0.5", "1", "2", "10", "50", "200")


def combination(s, kappa):
    """Evaluate the unscaled Hurwitz combination on a ball or a Taylor series."""
    z1, z2, z3, z4 = [s.zeta(arb(f"{n}/5")) for n in range(1, 5)]
    return z1 + kappa * (z2 - z3) - z4


def exact_kappa():
    root5 = arb(5).sqrt()
    return ((10 - 2 * root5).sqrt() - 2) / (root5 - 1)


def bounds(center, radius, point_jet, kappa):
    """Return the two error terms and the linear term on the circle."""
    # The square encloses the disk, so the resulting derivative interval
    # bounds every derivative along every segment from the center to the rim.
    width = radius.upper()
    square = acb(arb(0, width), arb(0, width))
    derivatives = combination(acb_series([center + square, 1], prec=2), kappa)[1]
    offset = point_jet[0].abs_upper()
    variation = (derivatives - point_jet[1]).abs_upper()
    signal = point_jet[1].abs_lower()
    return offset, radius * variation, radius * signal


def data_for_point(center, scale, kappa):
    center_jet = combination(acb_series([center, 1], prec=2), kappa)
    results = []
    for multiplier in RADIUS_SCALES:
        radius = scale * arb(multiplier)
        offset, change, signal = bounds(center, radius, center_jet, kappa)
        passed = offset + change < signal
        if multiplier == "1":
            assert passed, (center, radius, offset, change, signal)
        # Preserve the direction of each bound after conversion to a JS number.
        results.append([
            nextafter(float(offset.upper()), inf),
            nextafter(float(change.upper()), inf),
            nextafter(float(signal.lower()), -inf),
            passed,
        ])
    return results


def check():
    ctx.dps = 70
    kappa = exact_kappa()
    result = []
    for real, imag, radius in RIGHT_CENTERS:
        x, y, scale = map(arb, (real, imag, radius))
        for cx in (x, 1 - x):
            # Distance from the center line exceeds the disk radius.
            assert abs(cx - arb("1/2")) > scale
        right = data_for_point(acb(x, y), scale, kappa)
        left = data_for_point(acb(1 - x, y), scale, kappa)
        result.append({"right": right, "left": left})

    control = acb(arb("0.8"), arb("85.7"))
    control_jet = combination(acb_series([control, 1], prec=2), kappa)
    offset, error, signal = bounds(control, arb("1e-8"), control_jet, kappa)
    assert offset + error > signal
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot-data", action="store_true", help="print JSON for the visual")
    data = check()
    if parser.parse_args().plot_data:
        print(json.dumps(data, separators=(",", ":")))
    else:
        for (real, imag, radius), pair in zip(RIGHT_CENTERS, data):
            ratios = []
            for side in ("right", "left"):
                offset, variation, signal, verified = pair[side][RADIUS_SCALES.index("1")]
                assert verified
                ratios.append((offset + variation) / signal)
            print(f"{real} + {imag}i and mirror, radius {radius}: "
                  f"ratios {ratios[0]:.8f} and {ratios[1]:.8f}")
        print("Eight unique zeros counting multiplicity. Shifted-center control rejected.")
