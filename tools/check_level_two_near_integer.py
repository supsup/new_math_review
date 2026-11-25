"""Verify the level-two near-integer card with exact series and Arb balls.

Use a Python environment with python-flint installed. Run from any directory.
Pass --emit to print the certified values for the card's embedded data.
"""

import argparse
from fractions import Fraction
import json
from math import gcd, isqrt
from pathlib import Path
import re

from flint import acb, arb, ctx, fmpz, fmpz_series


def reduced_forms(discriminant):
    for a in range(1, isqrt(-discriminant // 3) + 1):
        for b in range(-a + 1, a + 1):
            c, remainder = divmod(b * b - discriminant, 4 * a)
            if not remainder and c >= a and (c > a or b >= 0) and gcd(a, b, c) == 1:
                yield (a, b, c)


def integer_coefficients():
    # P(q) = product of (1 + q^n)^24. Higher factors leave q^0 through q^4 alone.
    product = fmpz_series([1], prec=5)
    for n in range(1, 5):
        factor = fmpz_series([1] + [0] * (n - 1) + [1], prec=5)
        product *= factor**24
    # H = q^(-1)/P + 128 + 4096*q*P.
    q_times_h = 1 / product + fmpz_series([0, 128], prec=5)
    q_times_h += fmpz_series([0, 0, 4096], prec=5) * product
    result = [int(q_times_h[k]) for k in range(5)]
    assert result == [1, 104, 4372, 96256, 1240002]
    return result


def real_integer(ball):
    assert ball.imag.unique_fmpz() == 0
    integer = ball.real.unique_fmpz()
    assert integer is not None
    return int(integer)


def field_data(n, coefficients):
    discriminant = -4 * n
    principal, adjacent = reduced_forms(discriminant)
    assert principal == (1, 0, n) and adjacent[0] == 2
    a, b, _ = adjacent
    epsilon = (-1) ** (b // 2)
    tau = acb(-arb(b) / (2 * a), arb(-discriminant).sqrt() / (2 * a))
    j, j2 = tau.modular_j(), (2 * tau).modular_j()
    # CM makes these rational algebraic integers. The balls select exact integers.
    trace, norm = real_integer(j + j2), real_integer(j * j2)
    cube_root = int(fmpz(abs(norm)).root(3))
    if norm < 0:
        cube_root = -cube_root
    assert cube_root**3 == norm
    H = cube_root - 144
    assert H**2 - 207 * H + 3456 == trace
    # Also evaluate the eta quotient independently of j and the class polynomial.
    t = (tau.modular_eta() / (2 * tau).modular_eta()) ** 24
    assert real_integer(t + 128 + 4096 / t) == H
    F = H - coefficients[1]
    candidates = [epsilon * F, F**2 - 2 * coefficients[2],
                  epsilon * (F**3 - 3 * coefficients[2] * F - 3 * coefficients[3])]
    exponential = (arb.pi() * arb(n).sqrt()).exp()
    gaps = [integer - exponential**k for k, integer in enumerate(candidates, 1)]
    return {
        'n': n,
        'forms': [list(principal), list(adjacent)],
        'H': str(H),
        'trace': str(trace),
        'norm': str(norm),
        'epsilon': epsilon,
    }, gaps


def check(emit):
    ctx.prec = 256
    coefficients = integer_coefficients()
    values = [field_data(n, coefficients) for n in (22, 37, 58)]
    if emit:
        records = []
        for field, gaps in values:
            field['gaps'] = [gap.str(12, radius=False) for gap in gaps]
            records.append(field)
        print(json.dumps(records, indent=2))
        return

    page = Path(__file__).resolve().parent.parent / 'crew_visuals' / 'level_two_near_integer.html'
    source = page.read_text(encoding='utf-8')
    match = re.search(r'<script type="application/json" id="examples">(.*?)</script>', source, re.S)
    records = json.loads(match[1])
    assert len(records) == len(values)
    for record, (field, gaps) in zip(records, values):
        shown = record.pop('gaps')
        assert record == field
        assert len(shown) == len(gaps)
        for text, gap in zip(shown, gaps):
            # Check the last displayed decimal place even when radii are suppressed.
            mantissa, marker, exponent = text.lower().partition('e')
            places = len(mantissa.partition('.')[2])
            unit = Fraction(10) ** ((int(exponent) if marker else 0) - places)
            tolerance = arb(unit.numerator) / unit.denominator
            assert abs(arb(text) - gap) <= tolerance
    print('Three exact class polynomials, four series coefficients and nine exponential gaps agree.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    check(parser.parse_args().emit)
