"""Replay two shifted eight-tap mixers for seven lost readings."""

from dataclasses import dataclass
from math import prod

from flint import fmpz, nmod_poly


@dataclass(frozen=True)
class Mixer:
    prime: int
    factors: tuple[int, ...]
    base: int
    quadratic: int
    cubic: int
    first_moment: int
    addresses: tuple[int, ...]
    offsets: tuple[int, ...]
    auxiliary_prime: int
    auxiliary_root: int


MIXERS = (
    Mixer(
        prime=12_871_291, factors=(2, 3, 5, 429_043), base=10,
        quadratic=-3_413_365, cubic=0, first_moment=3,
        addresses=(6251446, 7032005, 7394094, 9503192, 10513549, 11507449, 12319869, 12706143),
        offsets=(0, 120092, 567832, 2537342, 2624638, 3857764, 5427245, 6166315),
        auxiliary_prime=64_356_451, auxiliary_root=32,
    ),
    Mixer(
        prime=1_630_987, factors=(2, 3, 7, 38_833), base=2,
        quadratic=1_049_519, cubic=462_134, first_moment=4,
        addresses=(235911, 400580, 529184, 586582, 974843, 982688, 1261976, 1552185),
        offsets=(0, 109707, 401729, 466398, 694256, 807724, 875762, 935276),
        auxiliary_prime=8_154_931, auxiliary_root=16_807,
    ),
)


def check_shifted_exponential(mixer):
    p = mixer.prime
    # Pad the two negative degrees with zero for the derivative recurrence.
    coefficients = [0, 0, 1]
    for degree in range(1, mixer.first_moment+7):
        term = coefficients[-1] + 2*mixer.quadratic*coefficients[-2] + 3*mixer.cubic*coefficients[-3]
        coefficients.append(term * pow(degree, -1, p) % p)
    coefficients = coefficients[2:]
    assert not any(coefficients[9:])
    assert len(mixer.addresses) == len(set(mixer.addresses)) == 8 and all(mixer.addresses)
    product = nmod_poly([1], p)
    for address in mixer.addresses:
        product *= nmod_poly([1, address], p)
    assert product == nmod_poly(coefficients[:9], p)


def check_modular_rank(mixer):
    p, base = mixer.prime, mixer.base
    size = p - 1
    assert pow(base, size, p) == 1
    assert all(pow(base, size//factor, p) != 1 for factor in mixer.factors)

    powers = [1]*len(mixer.addresses)
    addresses = set(mixer.addresses)
    base_power = 1
    logarithms = []
    zero_moments = []
    for exponent in range(size):
        if base_power in addresses:
            logarithms.append(exponent)
        if sum(powers) % p == 0:
            zero_moments.append(exponent)
        base_power = base_power * base % p
        powers = [power * address % p for power, address in zip(powers, mixer.addresses)]

    assert mixer.offsets == tuple(index-logarithms[0] for index in logarithms)
    assert zero_moments == list(range(mixer.first_moment, mixer.first_moment+7))
    return [pow(base, exponent, p) for exponent in zero_moments]


def check_ordinary_invertibility(mixer):
    q, rho = mixer.auxiliary_prime, mixer.auxiliary_root
    size = mixer.prime - 1
    assert fmpz(q).is_prime() and (q-1) % size == 0
    assert pow(rho, size, q) == 1
    assert all(pow(rho, size//factor, q) != 1 for factor in mixer.factors)

    divisors = [1]
    for factor in mixer.factors:
        divisors += [order * factor for order in divisors]
    for order in divisors:
        root = pow(rho, size//order, q)
        assert sum(pow(root, offset, q) for offset in mixer.offsets) % q != 0
    return len(divisors)


if __name__ == "__main__":
    for mixer in MIXERS:
        size = mixer.prime - 1
        assert fmpz(mixer.prime).is_prime()
        assert prod(mixer.factors) == size and len(set(mixer.factors)) == len(mixer.factors)
        assert all(fmpz(factor).is_prime() for factor in mixer.factors)
        check_shifted_exponential(mixer)
        roots = check_modular_rank(mixer)
        orders = check_ordinary_invertibility(mixer)
        print(f"{size:,} inputs, eight taps, exact rank {size-len(roots):,} mod {mixer.prime:,}.")
        print(f"Roots {roots}. Ordinary invertibility certified at all {orders} cyclotomic orders.")
