"""Check the corrected zeta ramp on five finite power windows.

Requires python-flint. Pass --plot-data to print the visual's samples.
"""

import argparse
import json
from math import isqrt

from flint import arb, ctx


STARTS = (64, 256, 1024, 4096, 16384)
STEPS = 192
THETA = "0.5"


def prime_powers(limit):
    """Return log-weighted prime powers in increasing order."""
    prime = bytearray(b"\x01")*(limit+1)
    for n in range(2, isqrt(limit)+1):
        if prime[n]:
            prime[n*n::n] = b"\x00"*((limit-n*n)//n+1)
    values = []
    for p in range(2, limit+1):
        if prime[p]:
            weight = arb(p).log()
            n = p
            while n <= limit:
                values.append((n, weight))
                n *= p
    return iter(sorted(values))


def points(start):
    end = start*isqrt(start)
    logarithmic_grid = (round(start*(end/start)**(i/STEPS)) for i in range(STEPS+1))
    return sorted({start, end, *logarithmic_grid})


def sample(windows):
    heights = sorted({y for window in windows for y in window})
    weights = prime_powers(heights[-1])
    power, weight = next(weights, (heights[-1]+1, arb(0)))
    psi, weighted = arb(0), arb(0)
    correction = 1 + arb.const_euler()
    values = {}
    for y in heights:
        while power <= y:
            psi += weight
            weighted += weight/power
            power, weight = next(weights, (heights[-1]+1, arb(0)))
        x = arb(y)
        ramp = y*weighted - psi
        values[y] = (psi - y, ramp - y*x.log() + y*correction)
    return values


def certify(window, values, theta):
    """Convexity of the ramp and a curvature bound fill every sample gap."""
    excess = {y: values[y][1] - arb(y)**theta for y in window}
    smallest_slack = None
    for a, b in zip(window, window[1:]):
        # For K(y) = -y log y + (1+gamma)y - y^theta, K'' >= -1/a.
        # The ramp lies below its chord. The smooth part can exceed its
        # chord by at most (b-a)^2/(8a). Use the larger endpoint excess.
        cap = max(excess[a].upper(), excess[b].upper()) + arb((b-a)**2)/(8*a)
        assert cap < 0, (a, b, cap)
        slack = -cap.upper()
        smallest_slack = slack if smallest_slack is None else min(slack, smallest_slack)
    return smallest_slack


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot-data", action="store_true")
    args = parser.parse_args()
    ctx.dps = 55
    windows = [points(start) for start in STARTS]
    values = sample(windows)
    theta = arb(THETA)
    data = []
    for window in windows:
        slack = certify(window, values, theta)
        if args.plot_data:
            data.append({
                "start": window[0], "end": window[-1],
                "samples": [[y, *[round(float(v.mid()), 8) for v in values[y]]] for y in window]
            })
        else:
            print(f"[{window[0]:,}, {window[-1]:,}]: {len(window)-1} intervals. "
                  f"G(y) < y^{THETA}, with margin at least {slack.str(12)}.")
    if args.plot_data:
        print(json.dumps(data, separators=(",", ":")))


if __name__ == "__main__":
    main()
