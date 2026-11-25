"""Check simultaneous erasures and errors on the sixty-report mixer."""

from itertools import combinations

from check_two_error_mixer import (
    GAINS, INVERSES, N, NODES, OFFSETS, P, check_left_vectors, syndrome,
)


def decode(sums, blanks):
    first, second = blanks
    x, y = NODES[first], NODES[second]
    sum0, sum1, sum2, sum3 = sums
    reduced0 = (sum2 - (x + y)*sum1 + x*y*sum0) % P
    reduced1 = (sum3 - (x + y)*sum2 + x*y*sum1) % P
    changes = {}
    if reduced0:
        node = reduced1 * INVERSES[reduced0] % P
        index = NODES.index(node)
        factor = (node - x)*(node - y) % P
        assert factor
        weight = reduced0 * INVERSES[factor] % P
        changes[index] = weight * INVERSES[GAINS[index]] % P
        sum0 = (sum0 - weight) % P
        sum1 = (sum1 - node*weight) % P
    else:
        assert reduced1 == 0
    weight_x = (sum1 - y*sum0) * INVERSES[(x-y) % P] % P
    changes[first] = weight_x * INVERSES[GAINS[first]] % P
    changes[second] = (sum0 - weight_x) * INVERSES[GAINS[second]] % P
    return changes


def check_decoding():
    checked = 0
    for first, second in combinations(range(N), 2):
        blanks = (first, second)
        # The two unit checks cover arbitrary erased amounts by linearity.
        for amounts in [(0, 0), (1, 0), (0, 1)]:
            changes = dict(zip(blanks, amounts))
            assert decode(syndrome(changes.items()), blanks) == changes
        for wrong in range(N):
            if wrong in blanks:
                continue
            # Scaling the one visible error leaves its located address unchanged.
            # Its contribution to the corrected readings scales linearly.
            changes = {first: first, second: P-1-second, wrong: 1}
            assert decode(syndrome(changes.items()), blanks) == changes
            checked += 1
    assert checked == 102660
    print(f"{checked:,} choices of two erased positions and one wrong position.")
    print("Linearity covers all erased values and all sixty nonzero visible error amounts.")


def check_collision():
    blanks = (1, 4)
    actual_errors = {7: 54, 13: 60}
    inputs = [(2*i*i + 5*i + 7) % P for i in range(N)]
    sent = [sum(inputs[(i+k) % N] for k in OFFSETS) % P for i in range(N)]
    assert syndrome(enumerate(sent)) == [0]*4
    actual_changes = actual_errors | {i: -sent[i] % P for i in blanks}
    sums = syndrome(actual_changes.items())
    alternative = decode(sums, blanks)
    assert alternative[21] == 51 and alternative.keys() == {1, 4, 21}
    assert all(alternative[i] != actual_changes[i] for i in blanks)
    assert syndrome(alternative.items()) == sums
    print(f"Same four checks {sums} for blanks {blanks} and errors {actual_errors} or {{21: 51}}.")


if __name__ == "__main__":
    check_left_vectors()
    check_decoding()
    check_collision()
