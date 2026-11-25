"""Repair erased and wrong mixed readings together on the seven-tap board."""

from random import Random

from flint import nmod_mat, nmod_poly

from check_seven_tap_mixer import PRIME, SIZE
from check_three_wrong_readings import collision_word, locate, sample_mix, solve, syndromes


def decode_mixed(checks, erased, address_indices):
    if len(erased) > len(checks):
        return None
    erased_addresses = [pow(2, -i, PRIME) for i in erased]
    erase_filter = nmod_poly([1], PRIME)
    for x in erased_addresses:
        erase_filter *= nmod_poly([-x, 1], PRIME)
    coefficients = [int(coefficient) for coefficient in erase_filter.coeffs()]
    filtered = [
        sum(coefficient * checks[k+j] for j, coefficient in enumerate(coefficients)) % PRIME
        for k in range(len(checks) - len(erased))
    ]

    weights = locate(filtered, address_indices)
    if weights is None or any(erase_filter(x) == 0 for x in weights):
        return None
    errors = {
        address_indices[x]: weight * pow(int(erase_filter(x))*x*x, -1, PRIME) % PRIME
        for x, weight in weights.items()
    }

    if erased:
        remaining = [(a-b) % PRIME for a, b in zip(checks, syndromes(errors))]
        matrix = nmod_mat(
            [[pow(x, k, PRIME) for x in erased_addresses] for k in range(len(erased))], PRIME
        )
        erased_weights = solve(matrix, remaining[:len(erased)])
        errors.update({
            i: weight * pow(x, -2, PRIME) % PRIME
            for i, x, weight in zip(erased, erased_addresses, erased_weights)
        })
    return errors if syndromes(errors) == checks else None


def check_recovery(address_indices):
    rng = Random(2718)
    clean = sample_mix()
    nonzero = [i for i, value in clean.items() if value % PRIME]
    trials = 0
    for r in range(7):
        for e in range((6-r)//2 + 1):
            for _ in range(100):
                erased = rng.sample(nonzero, r)
                candidates = rng.sample(range(SIZE), e+r)
                unknown = [i for i in candidates if i not in erased][:e]
                errors = {i: rng.randrange(1, PRIME) for i in unknown}
                expected = errors | {i: -clean[i] % PRIME for i in erased}
                observed = clean.copy()
                for i, amount in expected.items():
                    observed[i] = (observed.get(i, 0) + amount) % PRIME
                assert decode_mixed(syndromes(observed), erased, address_indices) == expected
                trials += 1
    assert decode_mixed([0]*6, [71], address_indices) == {71: 0}
    assert decode_mixed([0]*6, list(range(7)), address_indices) is None
    return trials


def check_limit():
    word = collision_word()
    for r in range(7):
        # The same observation can be produced from the zero word or from word.
        # Both senders lose the same r positions. They differ on the other 7-r.
        split = r + (7-r)//2
        observation = {i: word[i] for i in range(r, split)}
        changed_from_word = {i: -word[i] % PRIME for i in range(split, 7)}
        erased_from_word = {i: -word[i] % PRIME for i in range(r)}
        assert syndromes(observation) == syndromes(changed_from_word | erased_from_word)
        assert max(len(observation), len(changed_from_word)) == (6-r)//2 + 1


if __name__ == "__main__":
    addresses = {pow(2, -i, PRIME): i for i in range(SIZE)}
    count = check_recovery(addresses)
    check_limit()
    print(f"Repaired {count:,} damaged mixes spanning every budget 2e+r <= 6.")
    print("Checked an ambiguity one error beyond the limit for each of 0–6 erasures.")
