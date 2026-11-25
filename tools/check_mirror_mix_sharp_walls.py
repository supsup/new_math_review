"""Enclose the two sharp right walls of the mod-five dial using python-flint."""

import argparse
import json
from math import isqrt

from flint import arb, ctx

from check_mirror_mix_contacts import root_number


LIMIT = 100_000
EDGES = (
    (45, "1.120362498183", "1.120362498184"),
    (135, "2.38228610898", "2.38228610900"),
)
PLOT_RANGES = (("1.080", "1.180"), ("2.200", "2.550"))


def relevant_primes(limit):
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for p in range(2, isqrt(limit) + 1):
        if sieve[p]:
            sieve[p*p:limit+1:p] = b"\x00"*((limit-p*p)//p+1)
    return [p for p in range(2, limit+1) if sieve[p] and p % 5 in (2, 3)]


def quadratic_log_ratio(sigma):
    """Twice the sum of artanh(p^-sigma) over primes 2 and 3 modulo 5."""
    first, second, third, fourth = [sigma.zeta(arb(f"{r}/5")) for r in (1, 2, 3, 4)]
    five = arb(5)**(-sigma)
    quadratic = five*(first - second - third + fourth)
    assert quadratic > 0
    return ((1-five)*sigma.zeta()/quadratic).log()


def phase_envelope(sigma, primes, limit):
    # Replace the slowly converging prime sum with the log of a quotient
    # of Dirichlet L-functions, then subtract the cubic corrections.
    upper = quadratic_log_ratio(sigma)
    for prime in primes:
        ratio = arb(prime)**(-sigma)
        upper -= 2*(ratio.atanh() - ratio.atan())

    # 2(artanh r - atan r) = 4(r³/3 + r⁷/7 + …).
    # Use every integer after the sieve cutoff to dominate the prime tail.
    tail = (4*arb(limit)**(1-3*sigma)
            / (3*(3*sigma-1)*(1-arb(limit+1)**(-4*sigma))))
    return upper-tail, upper


def check_edges(primes):
    epsilon = root_number()
    theta = (epsilon.imag / epsilon.real).atan()
    for (angle, low, high), target in zip(EDGES, (arb.pi()-theta, theta)):
        at_low = phase_envelope(arb(low), primes, LIMIT)[0]
        at_high = phase_envelope(arb(high), primes, LIMIT)[1]
        assert at_low > target > at_high, (angle, at_low-target, target-at_high)
        yield {
            "angle": angle, "lower": low, "upper": high,
            "target": float((target*180/arb.pi()).mid()),
        }


def plot_data(edges):
    limit = 10_000
    primes = relevant_primes(limit)
    degrees = 180/arb.pi()
    for row, (low, high) in zip(edges, PLOT_RANGES):
        begin, end = arb(low), arb(high)
        values = []
        for i in range(101):
            sigma = begin + (end-begin)*i/100
            a, b = phase_envelope(sigma, primes, limit)
            assert b-a < arb("1e-8")
            values.append(round(float(((a+b)*degrees/2).mid()), 7))
        row["range"] = [float(low), float(high)]
        row["samples"] = values
    return edges


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--plot-data", action="store_true")
    args = cli.parse_args()
    ctx.dps = 60
    primes = relevant_primes(LIMIT)
    edges = list(check_edges(primes))
    if args.plot_data:
        print(json.dumps(plot_data(edges), separators=(",", ":")))
    else:
        for row in edges:
            print(f"{row['angle']}°: {row['lower']} < wall < {row['upper']}; "
                  f"target phase magnitude {row['target']:.10f}°")
