"""Replay a seven-tap circulant recovering from any six lost readings."""

from math import factorial

from flint import fmpz, nmod_poly


PRIME = 110_909
SIZE = PRIME - 1
OFFSETS = (0, 1583, 55273, 58490, 73564, 94050, 94848)
ADDRESSES = (110822, 11495, 36194, 13987, 29685, 58083, 72462)
AUXILIARY_PRIMES = (1_000_003, 1_000_033)


def main():
    assert fmpz(PRIME).is_prime()
    product = nmod_poly([1], PRIME)
    for x in ADDRESSES:
        product *= nmod_poly([1, x], PRIME)
    exponential = [pow(factorial(k), -1, PRIME) for k in range(8)]
    assert product == nmod_poly(exponential, PRIME)
    assert len(set(ADDRESSES)) == len(ADDRESSES)

    logarithms = {}
    value = 1
    for index in range(SIZE):
        logarithms[value] = index
        value = 2*value % PRIME
    assert value == 1 and len(logarithms) == SIZE
    indices = sorted(logarithms[x] for x in ADDRESSES)
    assert OFFSETS == tuple(i-indices[0] for i in indices)

    cycle = [-1] + [0]*(SIZE-1) + [1]
    mask = [int(i in OFFSETS) for i in range(OFFSETS[-1]+1)]
    roots = [pow(2,k,PRIME) for k in range(2,8)]
    common = nmod_poly(cycle, PRIME).gcd(nmod_poly(mask, PRIME))
    assert common.degree() == len(roots) and all(common(x) == 0 for x in roots)
    for p in AUXILIARY_PRIMES:
        assert fmpz(p).is_prime()
        assert nmod_poly(cycle, p).gcd(nmod_poly(mask, p)).degree() == 0

    print(f"{SIZE:,} inputs, seven wires per reading, exact rank {SIZE-len(roots):,} mod {PRIME:,}.")
    print(f"Roots {roots}. Ordinary invertibility checked at two auxiliary primes.")


if __name__ == "__main__":
    main()
