"""Exact certificates for optimum-wire rotating mixers from moment polynomials."""

from math import factorial, isqrt, prod

from flint import nmod_poly

from check_two_loss_circulants import cyclic_polynomial, wiring_polynomial


# Prime, second moment, generator, polynomial roots before normalization, offsets.
EXAMPLES = (
    (4229, 2534, 2, (2476, 2490, 352, 2059, 2139, 3172), (0, 93, 231, 298, 708, 4088)),
    (261587, 120498, 2, (65948, 140616, 95816, 251265, 210676, 180053, 101975),
     (0, 155820, 162656, 176918, 194813, 246353, 256525)),
)
ORDINARY_CONTROL = 65521


def is_prime(p):
    return p >= 2 and all(p % q for q in range(2, isqrt(p) + 1))


def monic_with_roots(roots, prime):
    return prod((nmod_poly([-root, 1], prime) for root in roots), start=nmod_poly([1], prime))


def verify(prime, second_moment, generator, original_addresses, offsets):
    assert is_prime(prime)
    n, weight = prime - 1, len(offsets)
    losses = weight - 1
    assert len(set(offsets)) == weight and all(0 <= offset < n for offset in offsets)
    assert len(set(original_addresses)) == weight and all(0 < address < prime for address in original_addresses)

    # h_j / j! is the coefficient of t^j in exp(t − b t²/2).
    hermite = [1, 1]
    for j in range(1, weight + 1):
        hermite.append((hermite[j] - j*second_moment*hermite[j-1]) % prime)
    assert hermite[weight + 1] == 0
    elementary = [h * pow(factorial(j), -1, prime) % prime for j, h in enumerate(hermite[:-1])]
    coefficients = [(-1)**j * elementary[j] for j in range(weight, -1, -1)]
    assert nmod_poly(coefficients, prime) == monic_with_roots(original_addresses, prime)

    powers = [1]
    for _ in range(n):
        powers.append(powers[-1]*generator % prime)
    assert powers[n] == 1 and len(set(powers[:n])) == n
    normalizer = pow(original_addresses[0], -1, prime)
    assert {a*normalizer % prime for a in original_addresses} == {powers[j] for j in offsets}
    assert sum(original_addresses) % prime == 1
    assert sum(a**2 for a in original_addresses) % prime == second_moment
    assert all(sum(pow(a, j, prime) for a in original_addresses) % prime == 0
               for j in range(3, weight + 2))

    cycle, wiring = cyclic_polynomial(n), wiring_polynomial(n, offsets)
    repeated_roots = powers[3:weight + 2]
    assert len(repeated_roots) == losses
    modular_gcd = nmod_poly(cycle, prime).gcd(nmod_poly(wiring, prime))
    assert modular_gcd == monic_with_roots(repeated_roots, prime)

    # Both integer polynomials are monic. A common rational factor could
    # be taken monic integral, so it would keep its degree modulo this prime.
    control_gcd = nmod_poly(cycle, ORDINARY_CONTROL).gcd(nmod_poly(wiring, ORDINARY_CONTROL))
    assert control_gcd == nmod_poly([1], ORDINARY_CONTROL)
    print(f"mod {prime:,}: {n:,} inputs and {losses} losses at the minimum {weight} wires per report.")
    print(f"  Common roots mod {prime:,}: {repeated_roots}; gcd mod {ORDINARY_CONTROL:,}: 1.")


if __name__ == "__main__":
    assert is_prime(ORDINARY_CONTROL)
    for example in EXAMPLES:
        verify(*example)
