"""Check the first 50 conjugate-pair contributions to the first Li coefficient."""

import argparse
import json

from flint import acb, arb, ctx


def check():
    ctx.dps = 55
    full = 1 + arb.const_euler()/2 - (4*arb.pi()).log()/2
    zeros = acb.zeta_zeros(1, 50)
    assert len(zeros) == 50
    assert all(z.real == arb("0.5") for z in zeros)
    assert arb("14.13472514173469") < zeros[0].imag < arb("14.13472514173470")
    assert all(a.imag < b.imag for a, b in zip(zeros, zeros[1:]))

    partial = arb(0)
    samples = []
    for z in zeros:
        contribution = 1/(z.imag**2 + arb("0.25"))
        assert contribution > 0
        partial += contribution
        samples.append({
            "height": float(z.imag.mid()),
            "term": float(contribution.mid()),
            "sum": float(partial.mid()),
        })
    share = partial/full
    assert arb("0.8028307112") < share < arb("0.8028307113")
    return full, partial, share, samples


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot-data", action="store_true")
    args = parser.parse_args()
    full, partial, share, samples = check()
    if args.plot_data:
        print(json.dumps({"full": float(full.mid()), "pairs": samples}, separators=(",", ":")))
    else:
        print(f"First Li coefficient: {full.str(17)}.")
        print(f"First 50 pairs: {partial.str(17)}.")
        print(f"Share: {(100*share).str(13)} percent.")
