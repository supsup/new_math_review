"""Locate the rightmost zero of the mod-five dial at heights 0 through 201.

The single required phase near the right edge reduces the upper bound to
one vertical line. Lattice independently found the tight isolating ranges
and checked uniqueness with a direct Dirichlet-L implementation.
"""

import argparse
from fractions import Fraction
import json

from flint import acb, acb_series, arb, ctx

from check_davenport_heilbronn_disks import exact_kappa
from check_mirror_mix_contacts import I, hurwitz_parts
from check_mirror_mix_sharp_walls import phase_envelope, relevant_primes


SIGMA_LOW, SIGMA_HIGH = "2.346000334548824", "2.346000334548825"
HEIGHT_LOW, HEIGHT_HIGH = "99.8941797516688", "99.8941797516689"
WITNESS_HEIGHT = "99.89417975166885"
PLOT_SIGMA = "2.34600034"
LIMIT = 100_000


def phase_jet(real, height, order=2):
    p, q = hurwitz_parts(acb_series([acb(real, height), 1], prec=order))
    return ((p + I*q)/(p - I*q)).log()


def derivative_bounds(sigma, target):
    primes = relevant_primes(LIMIT)
    _, maximum = phase_envelope(sigma, primes, LIMIT)
    assert maximum < arb.pi()-target

    # At a cancellation phase, the first two terms must already be
    # positive. Their negative derivatives dominate the other primes.
    main = arb(0)
    for p in (2, 3):
        cap = 2*(arb(p)**(-sigma)).atan()
        minimum = target - maximum + cap
        assert 0 < minimum < cap < arb.pi()/4
        main += arb(p).log()*minimum.sin()*minimum.cos()

    n, d = arb(LIMIT), sigma - 1
    log_n, r2 = n.log(), n**(-2*sigma)
    common = 2*n**(1-sigma)
    # Integrals of log(x)^k/x^sigma over x ≥ LIMIT bound the omitted primes.
    first = common*(log_n/d + 1/d**2)/(1-r2)
    second = common*(log_n**2/d + 2*log_n/d**2 + 2/d**3)*(1+r2)/(1-r2)**2
    for p in primes:
        r, log_p = arb(p)**(-sigma), arb(p).log()
        if p > 3:
            first += 2*log_p*r/(1-r*r)
        second += 2*log_p**2*r*(1+r*r)/(1-r*r)**2
    assert first < main
    return second, first-main


def cover(sigma, a, b, curvature, target, depth=0):
    mid = (a+b)/2
    jet = phase_jet(sigma, arb(str(mid)))
    r = arb(str((b-a)/2))
    # The analytic log's height derivative is the real part of its complex derivative.
    upper = jet[0].imag + r*jet[1].real.abs_upper() + r*r*curvature/2
    if upper < target:
        return 1
    assert depth < 30, (a, b, upper-target)
    return (cover(sigma, a, mid, curvature, target, depth+1)
            + cover(sigma, mid, b, curvature, target, depth+1))


def ball_between(a, b):
    return arb((a+b)/2, ((b-a)/2).upper())


def certify():
    target = 2*exact_kappa().atan()
    low, high = arb(SIGMA_LOW), arb(SIGMA_HIGH)
    curvature, falling = derivative_bounds(low, target)
    upper_panels = sum(cover(high, Fraction(t), Fraction(t+1), curvature, target) for t in range(201))
    assert phase_jet(low, arb(WITNESS_HEIGHT))[0].imag > target

    # A phase crossing at any fixed height falls as sigma increases. So
    # excluding it on a vertical line excludes it farther right as well.
    near = Fraction(WITNESS_HEIGHT)
    width = Fraction(1, 10**7)
    outer = cover(low, Fraction(0), near-width, curvature, target)
    outer += cover(low, near+width, Fraction(201), curvature, target)
    sigma = ball_between(low, high)
    local_height = arb(WITNESS_HEIGHT, arb(str(width)).upper())
    assert -2*phase_jet(sigma, local_height, order=3)[2].imag < 0

    # Strict concavity leaves one maximizing height in the remaining slab.
    # At that height the height derivative is zero. Its sign at the two
    # endpoints below is stable as sigma runs across the sharp bracket.
    mid, r = (low+high)/2, (high-low)/2
    t_low, t_high = arb(HEIGHT_LOW), arb(HEIGHT_HIGH)
    assert phase_jet(mid, t_low)[1].real > r*curvature
    assert -phase_jet(mid, t_high)[1].real > r*curvature
    angle = 180-phase_jet(sigma, ball_between(t_low,t_high))[0].real.exp().atan()*180/arb.pi()
    assert arb("134.566109704") < angle < arb("134.566109706")
    print(f"{upper_panels} upper-line panels, {outer} outer height panels.")
    print(f"Phase crossing slopes < {falling.str(9)}. Height curvature bound {curvature.str(9)}.")
    print(f"{SIGMA_LOW} < maximal real part < {SIGMA_HIGH}.")
    print(f"{HEIGHT_LOW} < unique maximizing height < {HEIGHT_HIGH}, at angle {angle.str(15)} degrees.")


def plot_data():
    target = 2*exact_kappa().atan()
    sigma, witness = arb(PLOT_SIGMA), arb(WITNESS_HEIGHT)

    def deficit(t):
        return float((phase_jet(sigma, t)[0].imag-target).mid())

    heights = [Fraction(t, 2) for t in range(403)] + [Fraction(WITNESS_HEIGHT)]
    full = [[float(t), deficit(arb(str(t)))] for t in sorted(heights)]
    zoom = [[i, 1e9*deficit(witness+arb(i)/10**6)] for i in range(-400, 401, 8)]
    assert all(value < 0 for _, value in full+zoom)
    return {"witness": float(witness.mid()), "full": full, "zoom": zoom}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot-data", action="store_true")
    args = parser.parse_args()
    ctx.dps = 65
    if args.plot_data:
        print(json.dumps(plot_data(), separators=(",", ":")))
    else:
        certify()
