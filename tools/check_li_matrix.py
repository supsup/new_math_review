"""Enclose Li coefficients and certify an exact positive Toeplitz matrix."""

import argparse
import json

from flint import acb, acb_series, arb, ctx


SIZE = 24


def li_coefficients(size):
    ctx.cap = size+1
    z = acb_series([0, 1], prec=size+1)
    s = 1/(1-z)
    # Evaluate (s-1) zeta(s) at the pole as 1 + (s-1) zeta_deflated(s).
    xi = (s/2)*(1 + (s-1)*s.zeta(deflate=True)) * (-(s/2)*acb.pi().log()).exp() * (s/2).gamma()
    assert xi[0].contains(acb("0.5"))
    logarithm = xi.log()
    assert len(logarithm) == size+1
    coefficients = [arb(0)] + [n*logarithm[n].real for n in range(1, size+1)]
    first = 1 + arb.const_euler()/2 - (4*arb.pi()).log()/2
    assert (coefficients[1] - first).contains(0)
    assert arb("0.02309570896612103") < coefficients[1] < arb("0.02309570896612104")
    return coefficients


def positive_pivots(first_row):
    """Interval LDL^T factorization of the symmetric Toeplitz matrix."""
    size = len(first_row)
    lower = [[arb(0) for _ in range(size)] for _ in range(size)]
    diagonals = []
    for i in range(size):
        pivot = first_row[0] - sum(diagonals[k]*lower[i][k]**2 for k in range(i))
        assert pivot > 0, (i, pivot)
        diagonals.append(pivot)
        for j in range(i+1, size):
            term = first_row[j-i] - sum(
                diagonals[k]*lower[j][k]*lower[i][k] for k in range(i)
            )
            lower[j][i] = term/pivot
    return diagonals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot-data", action="store_true")
    args = parser.parse_args()
    ctx.dps = 500
    coefficients = li_coefficients(SIZE)
    differences = [2*coefficients[1]] + [
        coefficients[n+1] - 2*coefficients[n] + coefficients[n-1] for n in range(1, SIZE)
    ]
    pivots = positive_pivots(differences)
    if args.plot_data:
        print(json.dumps({
            "coefficients": [float(value.mid()) for value in coefficients[:4]],
            "first_row": [float(value.mid()) for value in differences[:3]],
        }, separators=(",", ":")))
    else:
        print(f"The exact {SIZE}×{SIZE} Toeplitz matrix has {len(pivots)} positive pivots.")
        print("First row starts", ", ".join(value.str(15) for value in differences[:3]))
        print("Last pivot:", pivots[-1].str(15))


if __name__ == "__main__":
    main()
