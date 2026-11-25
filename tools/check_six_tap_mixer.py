"""Replay the six-tap quartic mixer over the field modulo 14717."""

from math import comb

from flint import fmpz, fmpz_poly, nmod_poly


PRIME = 14_717
SIZE = PRIME - 1
OFFSETS = (0, 1912, 4076, 5184, 12912, 13005)
ADDRESSES = (3944, 5822, 12349, 4816, 13339, 3882)
ROOTS = (16, 32, 64, 128, 256)
AUXILIARY_PRIME = 1_000_003


def verify_construction():
    # Differentiate exp(t + b*t^2 + c*t^3) to generate its coefficients.
    b, c = 13758, 6281
    series = [1]
    for k in range(1, 9):
        coefficient = series[k-1]
        if k >= 2:
            coefficient += 2*b*series[k-2]
        if k >= 3:
            coefficient += 3*c*series[k-3]
        series.append(coefficient * pow(k, -1, PRIME) % PRIME)
    assert series[7:] == [0, 0]

    product = nmod_poly([1], PRIME)
    for x in ADDRESSES:
        product *= nmod_poly([1, x], PRIME)
    assert product == nmod_poly(series[:7], PRIME)

    logarithms = {}
    value = 1
    for index in range(SIZE):
        logarithms[value] = index
        value = 2*value % PRIME
    assert value == 1 and len(logarithms) == SIZE
    indices = sorted(logarithms[x] for x in ADDRESSES)
    assert OFFSETS == tuple(i-indices[0] for i in indices)


def main():
    assert fmpz(PRIME).is_prime()
    assert fmpz(AUXILIARY_PRIME).is_prime()
    verify_construction()

    cycle = [-1] + [0]*(SIZE-1) + [1]
    mask = [int(i in OFFSETS) for i in range(OFFSETS[-1]+1)]
    finite_gcd = nmod_poly(cycle, PRIME).gcd(nmod_poly(mask, PRIME))
    assert finite_gcd.degree() == len(ROOTS)
    assert all(finite_gcd(root) == 0 for root in ROOTS)
    assert ROOTS == tuple(pow(2, j, PRIME) for j in range(4, 9))
    assert fmpz_poly(cycle).gcd(fmpz_poly(mask)).degree() == 0
    assert nmod_poly(cycle, AUXILIARY_PRIME).gcd(nmod_poly(mask, AUXILIARY_PRIME)).degree() == 0

    print(f"{SIZE:,} inputs, six wires per reading, and exact rank {SIZE-len(ROOTS):,} mod {PRIME:,}.")
    print(f"Ordinary invertibility verified. Distinct addresses cover all {comb(SIZE, 5):,} probe sets.")


if __name__ == "__main__":
    main()
