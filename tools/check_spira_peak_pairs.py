"""Certify the 27 right-side roots at 135° in the height band 0–201."""

import argparse
from fractions import Fraction
import json

from flint import acb, arb, ctx

from check_davenport_heilbronn_disks import exact_kappa
from check_mirror_mix_contacts import hurwitz_parts
from check_mirror_mix_loops import certify_simple_root


RIGHT_CENTERS = (
    ("2.30862294704", "8.91835529211"),
    ("1.94374138070", "18.89939065917"),
    ("2.09106251983", "26.54501134743"),
    ("2.15626398269", "36.55561227126"),
    ("1.50496931988", "44.80568309218"),
    ("2.33262487346", "54.42012973850"),
    ("1.78509441629", "64.37109013653"),
    ("2.17278600542", "72.06370231606"),
    ("0.69340330493", "77.34694077863"),
    ("2.05502529132", "82.05981711516"),
    ("1.83279458302", "89.96306654552"),
    ("2.34551234345", "99.86137594850"),
    ("1.18951929941", "107.10609848017"),
    ("1.33795051352", "109.43894664713"),
    ("2.22292621215", "117.57241862396"),
    ("1.75210458997", "127.67977121110"),
    ("2.10724308160", "135.43458503158"),
    ("2.29837218221", "145.35003777436"),
    ("1.45798549382", "153.03870841959"),
    ("1.21639611420", "154.97197764765"),
    ("2.26644178247", "163.10167592579"),
    ("0.82423381110", "171.28860623878"),
    ("1.64622648969", "173.13617416800"),
    ("2.21685085851", "180.85356165997"),
    ("2.18562441173", "190.78741012426"),
    ("1.33124553424", "198.33258128356"),
    ("1.07309487876", "199.16975733042"),
)
RADIUS = Fraction(1, 10**8)


def check():
    ctx.dps = 60
    kappa = exact_kappa()
    box_radius = arb(str(RADIUS))

    def mixture(s):
        p, q = hurwitz_parts(s)
        return q - kappa*p

    bands = ((0, 76), (76, 177), (177, 201))
    counts = [0]*len(bands)
    beyond_one = beyond_two = 0
    previous_upper = arb(0)
    for real, height in RIGHT_CENTERS:
        x, t = arb(real), arb(height)
        assert x - box_radius > arb("1/2") and x + box_radius < 4
        assert previous_upper < t - box_radius
        previous_upper = t + box_radius
        index = next(i for i, (lo, hi) in enumerate(bands) if lo < t-box_radius and t+box_radius < hi)
        counts[index] += 1
        for edge in (1, 2):
            assert x - box_radius > edge or x + box_radius < edge
        beyond_one += x - box_radius > 1
        beyond_two += x - box_radius > 2
        certify_simple_root(mixture, acb(x, t), RADIUS)

    assert counts == [8, 15, 4] and beyond_one == 25 and beyond_two == 13
    return RIGHT_CENTERS


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot-data", action="store_true")
    args = parser.parse_args()
    results = check()
    if args.plot_data:
        print(json.dumps(results, separators=(",", ":")))
    else:
        print("27 distinct right-side disks of radius 1e-8, each containing a simple zero.")
        print("Band counts 8, 15, 4. Of the right roots, 25 lie beyond Re s = 1 and 13 beyond Re s = 2.")
