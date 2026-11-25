"""Certify the unique rightmost mod-five mixture zero through height 201.

Run with Python and python-flint. Marlow's calculation found a candidate
near height 99.89418. This replay tightens the box, using FLINT's native
Dirichlet L-series in place of the Hurwitz zeta combination.
"""
from fractions import Fraction
import math

from flint import acb, acb_series, arb, ctx, dirichlet_char

from check_mirror_mix_sharp_walls import relevant_primes


LIMIT = 100_000
LOW = Fraction("2.346000334548824")
HIGH = Fraction("2.346000334548825")
HEIGHT = Fraction("99.894179751668812")
WINDOW = Fraction("0.0000001")
HEIGHT_LOW = Fraction("99.8941797516688")
HEIGHT_HIGH = Fraction("99.8941797516689")
CHI = dirichlet_char(5, 2)
CHIBAR = dirichlet_char(5, 3)


def phase_jet(real, height, order):
    s = acb_series([acb(real, height), 1], prec=order)
    return (s.dirichlet_l(CHI) / s.dirichlet_l(CHIBAR)).log()


def beta_bounds(target):
    """Bound derivatives of the prime logarithms for real parts at least LOW."""
    sigma = arb(str(LOW))
    n = arb(LIMIT)
    logn = n.log()
    d = sigma-1
    tail = n**(1-sigma)
    first_tail = tail*(logn/d+1/d**2)
    second_tail = tail*(logn**2/d+2*logn/d**2+2/d**3)
    ratio = n**(-2*sigma)
    # Dominate the omitted primes by integrals over all integers.
    turn = 2*tail/d
    first = 2*first_tail/(1-ratio)
    second = 2*second_tail*(1+ratio)/(1-ratio)**2
    major = {}
    for p in relevant_primes(LIMIT):
        logp = arb(p).log()
        r = arb(p)**(-sigma)
        phase = 2*r.atan()
        turn += phase
        if p in (2,3):
            major[p] = phase
        else:
            first += 2*logp*r/(1-r*r)
        second += 2*logp**2*r*(1+r*r)/(1-r*r)**2

    # Each prime can turn the ratio at most 2 atan(p^-sigma).
    # A hit of target forces the two biggest turns to be positive.
    assert turn < arb.pi()-target
    minimum = {p: target-(turn-major[p]) for p in major}
    assert all(0 < minimum[p] < major[p] < arb.pi()/4 for p in major)
    # For an individual turn alpha, its sigma derivative is
    # -log(p) sin(alpha) cos(alpha) (1+r²)/(1-r²).
    # The lower bounds on alpha increase with sigma. The tail bounds decrease.
    fall = sum(arb(p).log()*a.sin()*a.cos() for p, a in minimum.items())
    assert fall > first
    return second, first-fall


def exclude_height(sigma, lo, hi, second, target, depth=0):
    midpoint = arb(str((lo+hi)/2))
    radius = arb(str((hi-lo)/2))
    h = phase_jet(sigma, midpoint, 2)
    if h[0].imag + radius*abs(h[1].real) + radius**2*second/2 < target:
        return 1
    if depth >= 42:
        raise ValueError((str(lo), str(hi), h[0].imag-target))
    middle = (lo+hi)/2
    return (exclude_height(sigma, lo, middle, second, target, depth+1)
            + exclude_height(sigma, middle, hi, second, target, depth+1))


def cover(sigma, begin, end, second, target):
    integers = map(Fraction, range(math.floor(begin)+1, math.ceil(end)))
    boundaries = [begin, *integers, end]
    return sum(exclude_height(sigma, a, b, second, target)
               for a, b in zip(boundaries, boundaries[1:]))


def check():
    ctx.dps = 80
    pi = arb.pi()
    target = ((4*pi/5).sin()/(2*pi/5).sin()).atan()
    second, falling = beta_bounds(target)
    low, high = arb(str(LOW)), arb(str(HIGH))
    # No crossing at or above HIGH can occur if all heights start below the
    # target, since every crossing must be downwards in the real direction.
    no_cross = cover(high, Fraction(0), Fraction(201), second, target)
    at_height = arb(str(HEIGHT))
    assert phase_jet(low, at_height, 1)[0].imag > target
    # The only other target phase is θ−π, ruled out by beta_bounds.
    # A root exists between LOW and HIGH at the witness height. Outside
    # this window, there is no crossing above LOW by the same argument.
    outside = (cover(low, Fraction(0), HEIGHT-WINDOW, second, target)
               + cover(low, HEIGHT+WINDOW, Fraction(201), second, target))
    middle, radius = (low+high)/2, (high-low)/2
    sigma_box = arb(middle, radius.upper())
    window = arb(at_height, arb(str(WINDOW)).upper())
    near = phase_jet(sigma_box, window, 3)
    # The rightmost root is attained by compactness. It lies inside this
    # height window, and the nonzero real derivative lets us solve locally
    # for its real part as a function of height. At its maximum the phase
    # is stationary in height. Strict concavity makes that height unique
    # at the attained real part.
    assert -2*near[2].imag < 0
    for sign, height in ((1, HEIGHT_LOW), (-1, HEIGHT_HIGH)):
        slope = phase_jet(middle, arb(str(height)), 2)[1].real
        assert sign*slope > radius*second
    lo, hi = arb(str(HEIGHT_LOW)), arb(str(HEIGHT_HIGH))
    height_box = arb((lo+hi)/2, ((hi-lo)/2).upper())
    value = phase_jet(sigma_box, height_box, 1)[0]
    angle = 180 - value.real.exp().atan()*180/pi
    assert arb("134.566109704") < angle < arb("134.566109706")
    print(f"{no_cross} upper-line panels; {outside} outer height panels at the lower line.")
    print(f"Crossing real derivative < {falling.str(12)}, "
          f"local height curvature {(-2*near[2].imag).str(12)}.")
    print("2.346000334548824 < maximal real part < 2.346000334548825")
    print("99.8941797516688 < unique maximal height < 99.8941797516689")
    print(f"mixing angle {angle.str(15)} degrees")


if __name__ == "__main__":
    check()
