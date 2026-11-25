"""Check the fifteen-pair peak at 135 degrees by direct contour counts.

Requires python-flint. This fixed-angle check is separate from the fold tally.
The full contour can take several minutes.
"""

from fractions import Fraction

from flint import acb, arb, ctx

from check_davenport_heilbronn_disks import combination, exact_kappa
from check_spira_gaps import count_winding, line_brackets, rectangle


def check():
    ctx.dps = 48
    bottom, top = Fraction(76), Fraction(177)
    left, right = Fraction(-3), Fraction(4)
    cut = Fraction(501, 1000)
    kappa = -1/exact_kappa()
    log_scale = (arb(5).log() + arb.pi().log()) / 2

    def mixture(s):
        return combination(s, kappa)

    def completed(s):
        # The 135-degree mixture needs the additional factor i to be real
        # on the center line when written as this Hurwitz combination.
        return acb(0, 1) * mixture(s) * (-s*log_scale).exp() * ((s + 1)/2).gamma()

    # Breaking the vertical sides into unit segments gives the interval
    # splitter enough precision near the zeros close to the line.
    slab = [(cut, bottom), (right, bottom)]
    slab.extend((right, Fraction(t)) for t in range(77, 178))
    slab.extend((cut, Fraction(t)) for t in range(177, 76, -1))
    right_count, right_panels = count_winding(mixture, slab)
    assert right_count == 15
    print(f"Right slab: {right_count} zeros ({right_panels} winding panels).", flush=True)

    total, panels = count_winding(mixture, rectangle(left, right, bottom, top))
    on_line = line_brackets(completed, bottom, top, Fraction(1, 40))
    assert total == 74 and on_line == 44
    # The mirror gives the same count on the left as in the right slab.
    # Together with the 44 line brackets this exhausts the full contour.
    assert total == 2*right_count + on_line
    print(f"Entire band: {total} zeros ({panels} winding panels), "
          f"{on_line} distinct line brackets and {right_count} reflected off-line pairs.")


if __name__ == "__main__":
    check()
