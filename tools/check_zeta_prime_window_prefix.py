"""Certify the first square-root crossing and the finite prefix up to 10**6.

Between integers, F(x) = G(x) - sqrt(x) has -1/n <= F''(x) < 0 on
[n, n+1]. The upper bound from its endpoint chord plus
(x-n)(n+1-x)/(2*n) covers the entire interval.
"""

from array import array
from math import isqrt

from flint import arb, ctx


def prime_powers(through):
    sieve = bytearray(b'\x01') * (through + 1)
    sieve[:2] = b'\x00\x00'
    for prime in range(2, isqrt(through) + 1):
        if sieve[prime]:
            first = prime * prime
            sieve[first::prime] = b'\x00' * ((through - first) // prime + 1)
    bases = array('I', [0]) * (through + 1)
    for prime in range(2, through + 1):
        if not sieve[prime]:
            continue
        power = prime
        while power <= through:
            bases[power] = prime
            power *= prime
    return bases


def main():
    ctx.prec = 128
    through = 1_000_000
    bases = prime_powers(through)
    gamma = arb.const_euler()

    def difference(x, reciprocal_weight, total_weight):
        return x * (1 + gamma + reciprocal_weight - x.log()) - total_weight - x.sqrt()

    lower, upper = arb(3346873827339) / 10**12, arb(3346873827340) / 10**12
    log2, log3 = arb(2).log(), arb(3).log()
    reciprocal_weight = log2 / 2 + log3 / 3
    total_weight = log2 + log3
    assert reciprocal_weight + gamma - log3 - 1 / (2 * arb(3).sqrt()) < 0
    assert difference(lower, reciprocal_weight, total_weight) > 0
    assert difference(upper, reciprocal_weight, total_weight) < 0

    reciprocal_weight = arb(0)
    total_weight = arb(0)
    previous = None
    for n in range(1, through + 1):
        x = arb(n)
        if bases[n]:
            log_prime = arb(bases[n]).log()
            reciprocal_weight += log_prime / x
            total_weight += log_prime
        gap = difference(x, reciprocal_weight, total_weight)
        if n <= 3:
            assert gap > 0, n
        elif n >= 5:
            penalty = arb(1) / (8 * (n - 1))
            assert previous + penalty < 0 and gap + penalty < 0, n
        previous = gap

    print('Unique crossing in [1, 1000000]: 3.346873827339 < x < 3.346873827340.')
    print('Certified G(x) < sqrt(x) on every real x in [4, 1000000].')


if __name__ == '__main__':
    main()
