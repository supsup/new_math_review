"""Certify the first height a mod-five mixture reaches each real-part marker.

The angle can vary freely. Requires python-flint. Uses the phase of the
Dirichlet L-ratio and the crossing and curvature bounds from the finite
maximum certificate.
"""

from fractions import Fraction

from flint import arb, ctx

from check_mirror_mix_finite_peak import LOW, beta_bounds, cover, phase_jet
from check_mirror_mix_sharp_walls import phase_envelope, relevant_primes


MARKERS = (
    ("2.35", "425.93972523060", "425.93972523061"),
    ("2.36", "1649.72831853407", "1649.72831853408"),
    ("2.37", "1649.79982831787", "1649.79982831789"),
    ("2.375", "1649.88070285497", "1649.88070285498"),
    ("2.376", "43102.72512598181", "43102.72512598182"),
    ("2.377", "148833.61813565868", "148833.61813565870"),
    ("2.378", "808291.96971721064", "808291.96971721065"),
)


PRIME_LIMIT = 100_000


def round_out(value, rounding):
    """Return a rational grid bound beyond the entire ball."""
    scale = 10**10
    endpoint = (scale*value).lower() if rounding == "down" else (scale*value).upper()
    integer = endpoint.floor() if rounding == "down" else endpoint.ceil()
    return Fraction(int(integer.unique_fmpz()), scale)


def screen_one_prime(windows, period, offset, radius):
    """Intersect with all cosine windows that could supply the required turn."""
    result = []
    for start, end in windows:
        lo, hi = (arb(str(start)) - offset - radius)/period, (arb(str(end)) - offset + radius)/period
        first = int(lo.lower().ceil().unique_fmpz())
        last = int(hi.upper().floor().unique_fmpz())
        for k in range(first, last + 1):
            center = k*period + offset
            begin = max(start, round_out(center - radius, "down"))
            finish = min(end, round_out(center + radius, "up"))
            # Keep the endpoints of each cosine window.
            if begin <= finish:
                result.append((begin, finish))
    return result


def certify_earlier(sigma, end, target, curvature, primes):
    """Screen the early heights before checking the ones that remain."""
    _, maximum = phase_envelope(sigma, primes, PRIME_LIMIT)
    budget = (maximum - target).upper()
    assert 0 < budget
    windows = [(Fraction(0), end)]
    terms = []
    for p in primes:
        if p > 503:
            break
        radius = arb(p)**(-sigma)
        cap = 2*radius.atan()
        speed = arb(p).log()
        coefficient = 2*radius/(1 - radius**2)
        sign = 1 if p % 5 == 2 else -1
        terms.append((cap, sign*coefficient, speed))
        if cap > budget:
            # If the sum of turns reaches the target, each prime's unused
            # turn is at most the total unused turn. This forces its signed
            # cosine above the threshold below.
            period = 2*arb.pi()/speed
            offset = arb(0) if sign > 0 else period/2
            half_width = ((cap - budget).tan()/coefficient).acos()/speed
            windows = screen_one_prime(windows, period, offset, half_width)

    panels, excluded = 0, 0
    for lo, hi in windows:
        midpoint = arb(str((lo + hi)/2))
        radius = arb(str((hi - lo)/2))
        height = arb(midpoint, radius.upper())
        loss = arb(0)
        for cap, coefficient, speed in terms:
            loss += cap - (coefficient*(height*speed).cos()).atan()
            if loss > budget:
                excluded += 1
                break
        else:
            if lo == hi:
                assert phase_jet(sigma, midpoint, 1)[0].imag < target
            else:
                panels += cover(sigma, lo, hi, curvature, target)
    return len(windows), excluded, panels


def bracket(sigma_text, lo_text, hi_text, target, curvature, primes):
    sigma, lo, hi = map(arb, (sigma_text, lo_text, hi_text))
    assert Fraction(sigma_text) >= LOW
    assert phase_jet(sigma, lo, 1)[0].imag < target
    assert phase_jet(sigma, hi, 1)[0].imag > target

    midpoint, radius = (lo + hi)/2, (hi - lo)/2
    slope = phase_jet(sigma, midpoint, 2)[1].real
    assert slope > radius*curvature
    # At this crossing the height derivative is positive. The negative
    # real derivative implies that the zero moves to the right.
    box = arb(midpoint, radius.upper())
    ratio = phase_jet(sigma, box, 1)[0].real.exp()
    angle = 180 - ratio.atan()*180/arb.pi()

    # If the phase is below target on this vertical line, it cannot
    # meet target farther right. Every real-direction crossing falls,
    # and the global phase envelope also excludes the other direction.
    windows, excluded, panels = certify_earlier(sigma, Fraction(lo_text), target, curvature, primes)
    print(f"First Re s = {sigma_text} at {lo_text} < t < {hi_text}, "
          f"angle {angle.str(12)}°.", flush=True)
    print(f"  {windows} prime windows before the crossing; {excluded} fail the partial sum, "
          f"with {panels} interval panels in the rest.", flush=True)


def check_shared_crossing(first, second, target, curvature):
    """Keep the two higher markers on the same rising branch."""
    lower, upper = arb(first[0]), arb(second[0])
    start, end = arb(first[1]), arb(second[2])
    midpoint = phase_jet((lower + upper)/2, (start + end)/2, 2)
    radius = ((upper - lower) + (end - start))/2
    # |d²/ds² log(Lχ/Lχ̄)| bounds changes in the height derivative
    # along any complex segment, so one slope test covers the box.
    assert midpoint[1].real > radius*curvature
    assert phase_jet(lower, end, 1)[0].imag > target
    assert phase_jet(upper, start, 1)[0].imag < target
    print(f"The first {first[0]} and {second[0]} crossings lie on one rising zero trajectory.")


def check():
    ctx.dps = 60
    pi = arb.pi()
    target = ((4*pi/5).sin()/(2*pi/5).sin()).atan()
    curvature, falling = beta_bounds(target)
    assert falling < 0
    primes = relevant_primes(PRIME_LIMIT)
    for marker in MARKERS:
        bracket(*marker, target, curvature, primes)
    check_shared_crossing(MARKERS[1], MARKERS[2], target, curvature)
    check_shared_crossing(MARKERS[2], MARKERS[3], target, curvature)


if __name__ == "__main__":
    check()
