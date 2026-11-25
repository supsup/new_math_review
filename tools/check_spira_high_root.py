"""Certify one 135° zero near the sharp real-part limit at large height.

The normalized ratio of the two Dirichlet L-functions equals the root
number at a zero of this mixture. We work with a logarithm of that ratio
from its Euler factors in Re(s) > 1. Rouché compares a linear function
with the finite prime sum plus a uniform bound for the omitted tail.

For the limiting real part of this second Davenport–Heilbronn function,
see Bombieri and Ghosh, Around the Davenport–Heilbronn function, §§5–6.
https://doi.org/10.1070/RM2011v066n02ABEH004740
"""

from math import isqrt

from flint import acb, arb, ctx

from check_davenport_heilbronn_disks import exact_kappa


PRIME_LIMIT = 100_000
REAL = "2.378755863122"
HEIGHT = "1174561.0989005927"
RADIUS = "1e-6"


def relevant_primes(limit):
    sieve = bytearray(b"\1")*(limit+1)
    sieve[:2] = b"\0\0"
    for p in range(2, isqrt(limit)+1):
        if sieve[p]:
            sieve[p*p::p] = b"\0"*(1+(limit-p*p)//p)
    return (p for p in range(2,limit+1) if sieve[p] and p % 5 in (2,3))


def check():
    ctx.dps = 60
    x, t, radius = map(arb, (REAL, HEIGHT, RADIUS))
    center = acb(x, t)
    sigma_min = x-radius
    assert sigma_min > arb("2.3787")
    imaginary = acb(0, 1)
    phase = 2*exact_kappa().atan()
    value = -imaginary*phase
    derivative = acb(0)
    second_bound = arb(0)
    for p in relevant_primes(PRIME_LIMIT):
        log_p = arb(p).log()
        sign = 1 if p % 5 == 2 else -1
        z = (-center*log_p).exp()
        value += 2*imaginary*sign*z.atan()
        derivative -= 2*imaginary*sign*log_p*z/(1+z*z)
        a = (-sigma_min*log_p).exp()
        second_bound += 2*log_p**2*a*(1+a*a)/(1-a*a)**2

    # Absolute convergence permits the sum of analytic logarithm branches.
    # The arctangent series bounds 2|atan z| by 2|z|/(1-|z|²).
    n = arb(PRIME_LIMIT)
    tail = 2*n**(1-sigma_min)/((sigma_min-1)*(1-n**(-2*sigma_min)))
    error = value.abs_upper() + radius**2*second_bound/2 + tail
    signal = radius*derivative.abs_lower()
    assert error < signal
    print(f"One simple root in radius {RADIUS} about {REAL} + {HEIGHT}i at 135°.")
    print(f"Upper error {error.str(10)} < lower linear term {signal.str(10)}.")


if __name__ == "__main__":
    check()
