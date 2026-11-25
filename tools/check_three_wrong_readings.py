"""Decode three unknown errors on the seven-tap board and exhibit its limit."""

from random import Random

from flint import nmod_mat, nmod_poly

from check_seven_tap_mixer import OFFSETS, PRIME, SIZE


def syndromes(errors):
    return [
        sum(value * pow(root, -index, PRIME) for index, value in errors.items()) % PRIME
        for root in (4, 8, 16, 32, 64, 128)
    ]


def solve(matrix, values):
    column = nmod_mat([[value] for value in values], PRIME)
    return [int(value) for value in matrix.solve(column).entries()]


def locate(checks, address_indices):
    for count in range(len(checks)//2, 0, -1):
        hankel = nmod_mat(
            [[checks[i+j] for j in range(count)] for i in range(count)], PRIME
        )
        if hankel.det():
            break
    else:
        return {} if not any(checks) else None

    coefficients = solve(hankel, [-value for value in checks[count:2*count]])
    addresses = [int(root) for root, _ in nmod_poly(coefficients + [1], PRIME).roots()]
    if len(addresses) != count or any(x not in address_indices for x in addresses):
        return None

    vandermonde = nmod_mat(
        [[pow(x, k, PRIME) for x in addresses] for k in range(count)], PRIME
    )
    return dict(zip(addresses, solve(vandermonde, checks[:count])))


def decode(checks, address_indices):
    weights = locate(checks, address_indices)
    if weights is None:
        return None
    errors = {
        address_indices[x]: weight * pow(x, -2, PRIME) % PRIME
        for x, weight in weights.items()
    }
    return errors if syndromes(errors) == checks else None


def sample_mix():
    source = {0: 8, 41: 702, 55_273: PRIME - 2, SIZE - 1: 740}
    return {
        (i - tap) % SIZE: sum(source.get((i - tap + delta) % SIZE, 0) for delta in OFFSETS)
        for i in source for tap in OFFSETS
    }


def collision_word():
    # The leading coefficient in interpolation gives sum(w*x^k) == 0 for k < 6.
    points = [pow(2, -i, PRIME) for i in range(7)]
    difference = {}
    for index, x in enumerate(points):
        denominator = x*x
        for y in points:
            if y != x:
                denominator = denominator * (x-y) % PRIME
        difference[index] = pow(denominator, -1, PRIME)
    assert syndromes(difference) == [0] * 6
    return difference


def main():
    addresses = {pow(2, -i, PRIME): i for i in range(SIZE)}
    assert len(addresses) == SIZE and 0 not in addresses
    readings = sample_mix()
    assert syndromes(readings) == [0] * 6

    assert decode([0] * 6, addresses) == {}
    rng = Random(4907)
    for count in (1, 2, 3):
        for _ in range(500):
            errors = {i: rng.randrange(1, PRIME) for i in rng.sample(range(SIZE), count)}
            damaged = readings.copy()
            for i, error in errors.items():
                damaged[i] = (damaged.get(i, 0) + error) % PRIME
            assert decode(syndromes(damaged), addresses) == errors

    x, y, z = (pow(2, -i, PRIME) for i in (0, 151, SIZE - 1))
    errors = {
        addresses[a]: w * pow(a, -2, PRIME) % PRIME
        for a, w in zip((x, y, z), (y-z, z-x, x-y))
    }
    checks = syndromes(errors)
    assert checks[:2] == [0, 0] and decode(checks, addresses) == errors

    difference = collision_word()
    four_errors = {i: difference[i] for i in range(4)}
    three_errors = {i: -difference[i] % PRIME for i in range(4, 7)}
    assert syndromes(four_errors) == syndromes(three_errors)
    assert decode(syndromes(four_errors), addresses) == three_errors

    print(f"Recovered 1,500 damaged mixes at prime {PRIME:,}, plus the zero-error case.")
    print(f"Recovered three errors {errors} with checks {checks}.")
    print(f"Four errors {four_errors} have the same checks as three errors {three_errors}.")


if __name__ == "__main__":
    main()
