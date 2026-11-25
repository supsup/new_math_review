"""Enclose the sharp right walls for the integer angles of the mod-five dial."""

import argparse
from fractions import Fraction
import json
import math

from flint import arb, ctx

from check_mirror_mix_contacts import root_number
from check_mirror_mix_sharp_walls import LIMIT, check_edges, quadratic_log_ratio, relevant_primes


ANGLE_REPRESENTATIVES = (*range(1, 46), *range(91, 136))
ESTIMATE_LIMIT = 1_500
REPLAY_LIMIT = 10_000
DECIMAL_SCALE = 100_000_000
HALF_BRACKET = 30


def approximate_parameters(sigma, primes):
    log_ratio = float(quadratic_log_ratio(arb(str(sigma))).mid())
    terms = []
    for p in primes:
        r = p**(-sigma)
        terms.append((2*r/(1-r*r), 2*r/(1+r*r), 2*math.atanh(r)))
    return log_ratio, terms


def approximate_point(parameters, normal):
    c, s = math.cos(normal), math.sin(normal)
    baseline, terms = parameters
    x, y = c*baseline, s*baseline
    for horizontal, vertical, baseline_prime in terms:
        x += math.asinh(horizontal*c) - c*baseline_prime
        y += math.asin(vertical*s) - s*baseline_prime
    return x, y


def point_on_target_ray(parameters, x, y):
    left, right = 0, math.pi/2
    for _ in range(33):
        normal = (left + right) / 2
        vx, vy = approximate_point(parameters, normal)
        if vy*x > vx*y:
            right = normal
        else:
            left = normal
    normal = (left + right) / 2
    return normal, approximate_point(parameters, normal)[1]


def estimate_wall(x, y, primes):
    low, high = 1.001, 2.5
    for _ in range(35):
        middle = (low + high) / 2
        _, reach = point_on_target_ray(approximate_parameters(middle, primes), x, y)
        if reach > y:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def enclosed_point(sigma, normal, primes):
    c, s = normal.cos(), normal.sin()
    baseline = quadratic_log_ratio(sigma)
    x, y = c*baseline, s*baseline
    for p in primes:
        r = arb(p)**(-sigma)
        baseline_prime = 2*r.atanh()
        x += (2*r*c/(1-r*r)).asinh() - c*baseline_prime
        y += (2*r*s/(1+r*r)).asin() - s*baseline_prime

    # For r <= 1/8, each coordinate differs from its baseline coordinate
    # by at most 8 r^3. Sum over all omitted integers to enclose the tail.
    tail = 8*arb(REPLAY_LIMIT)**(1-3*sigma)/(3*sigma-1)
    known_radius = tail.upper()
    return x + arb(0, known_radius), y + arb(0, known_radius)


def check_tail_constants():
    multiplier = Fraction(128, 63)  # 2 / (1 - r^2) for r <= 1/8
    # |asinh u - u| <= |u|^3/6. For |u| <= 1/4, |asin u - u| <= |u|^3/3.
    # The difference of the arguments from 2r is at most multiplier*r^3.
    assert multiplier + multiplier**3 / 6 < 7
    assert 2 + Fraction(8, 3) < 7
    assert 2 / (3*(1-Fraction(1, 64))) < 1
    assert REPLAY_LIMIT >= 8


def certify(angle, x, y, estimates, replay):
    x_float, y_float = float(x.mid()), float(y.mid())
    center = estimate_wall(x_float, y_float, estimates)
    tick = round(center*DECIMAL_SCALE)
    low = Fraction(tick-HALF_BRACKET, DECIMAL_SCALE)
    high = Fraction(tick+HALF_BRACKET, DECIMAL_SCALE)
    assert low > 1
    low_normal, _ = point_on_target_ray(approximate_parameters(float(low), estimates), x_float, y_float)
    low_x, low_y = enclosed_point(arb(str(low)), arb(str(low_normal)), replay)
    # Convexity and reflection across either axis give the entire rectangle.
    assert low_x > x and low_y > y, (angle, low_x-x, low_y-y)

    high_normal, _ = point_on_target_ray(approximate_parameters(float(high), estimates), x_float, y_float)
    direction = arb(str(high_normal))
    high_x, high_y = enclosed_point(arb(str(high)), direction, replay)
    # This single supporting line puts the target outside the larger-σ set.
    separation = direction.cos()*(x-high_x) + direction.sin()*(y-high_y)
    assert separation > 0, (angle, separation)
    return float(low), float(high)


def chart_outline(sigma, primes):
    parameters = approximate_parameters(sigma, primes)
    return [
        [round(c, 7) for c in approximate_point(parameters, j*math.pi/40)]
        for j in range(21)
    ]


def check(make_plot):
    ctx.dps = 55
    check_tail_constants()
    epsilon = root_number()
    theta = (epsilon.imag/epsilon.real).atan()
    estimates = relevant_primes(ESTIMATE_LIMIT)
    replay = relevant_primes(REPLAY_LIMIT)
    axes = {row["angle"]: (float(row["lower"]), float(row["upper"]))
            for row in check_edges(relevant_primes(LIMIT))}

    rows = []
    for angle in ANGLE_REPRESENTATIVES:
        y = arb.pi()-theta if angle < 90 else theta
        if angle in axes:
            x = arb(0)
            low, high = axes[angle]
        else:
            x = abs(abs((arb.pi()*angle/180).tan()).log())
            low, high = certify(angle, x, y, estimates, replay)
        midpoint = (low+high)/2
        row = {
            "angle": angle, "wall": round(midpoint, 8), "interval": [low, high],
            "target": [round(float(x.mid()), 7), round(float(y.mid()), 7)],
        }
        if make_plot:
            row["outline"] = chart_outline(midpoint, estimates)
        rows.append(row)
    assert len(rows) == 90
    return rows


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--plot-data", action="store_true")
    args = cli.parse_args()
    rows = check(args.plot_data)
    if args.plot_data:
        print(json.dumps(rows, separators=(",", ":")))
    else:
        print("Enclosed 90 representatives, all 178 integer-angle settings with both weights present.")
        for row in rows:
            if row["angle"] in (30, 45, 120, 135):
                print(f"{row['angle']}°: {row['interval'][0]} < wall < {row['interval'][1]}")
