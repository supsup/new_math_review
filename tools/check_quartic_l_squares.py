"""Exact odd quartic moments, with an optional independent Arb replay."""

import argparse
import json
from math import gcd, isqrt
from pathlib import Path
import subprocess


LIMIT = 501


def prime(n):
    return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))


def prime_divisors(n):
    return [p for p in range(2, n + 1) if n % p == 0 and prime(p)]


def quartic_character(p):
    divisors = prime_divisors(p - 1)
    generator = next(g for g in range(2, p) if all(pow(g, (p - 1) // d, p) != 1 for d in divisors))
    exponent = (p - 1) // 4
    fourth_root = pow(generator, exponent, p)
    phases = {1: 0, fourth_root: 1, p - 1: 2, p - fourth_root: 3}
    return generator, [phases[pow(a, exponent, p)] for a in range(1, p)]


def analytic_replay(p, phases, a, b):
    from flint import acb, arb, ctx

    ctx.dps = 65
    i = acb(0, 1)
    values = (acb(1), i, acb(-1), -i)
    L = acb(0)
    tau = acb(0)
    for n, phase in enumerate(phases, 1):
        angle = 2 * arb.pi() * n / p
        chi = values[phase]
        # Laurent constant of the Hurwitz zeta function at 1.
        L -= chi * (arb(n) / p).digamma() / p
        tau += chi * acb(angle.cos(), angle.sin())
    formula = arb.pi() * i * tau * acb(a, -b) / (p * p)
    difference = L - formula
    assert difference.real.contains(0) and difference.imag.contains(0), p
    assert difference.real.rad() < arb("1e-50") and difference.imag.rad() < arb("1e-50")
    norm = p * abs(L)**2 / arb.pi()**2
    assert (norm - arb(a*a + b*b)/(p*p)).contains(0), p
    return [float(L.real.mid()), float(L.imag.mid())]


def check_at_thirteen():
    """Exact period norm and the prime-degree inputs to the Minkowski check."""
    p = 13
    generator, phases = quartic_character(p)
    assert [4 // gcd(4, phases[l - 1]) for l in (2, 3, 5, 7)] == [4, 1, 4, 4]
    assert [a for a, phase in enumerate(phases, 1) if phase == 0] == [1, 3, 9]
    product = [1] + [0] * (p - 1)
    for k in range(4):
        factor = pow(generator, k, p)
        result = [0] * p
        for a, coefficient in enumerate(product):
            for exponent in (1, 3, 9):
                result[(a + factor * exponent) % p] += coefficient
        product = result
    assert product[1:] == [product[1]] * (p - 1)
    assert product[0] - product[1] == 3


def check_class_groups(executable, results):
    """Compute both class groups independently, then certify them with PARI."""
    conductors = list(map(int, results))
    rows = [
        f"k=bnfinit(polsubcyclo({p},4),1); f=bnfinit(polsubcyclo({p},2),1); "
        f"print([{p},k.disc,f.disc,k.no,f.no,bnfcertify(k),bnfcertify(f)]);"
        for p in conductors
    ]
    run = subprocess.run([str(executable), "-fq"], input="\n".join(rows) + "\n",
                         text=True, capture_output=True, check=True)
    output = [json.loads(line) for line in run.stdout.splitlines() if line.strip()]
    assert [row[0] for row in output] == conductors, run.stderr
    for p, disc_k, disc_f, h_k, h_f, cert_k, cert_f in output:
        assert (disc_k, disc_f, cert_k, cert_f) == (p**3, p, 1, 1), p
        _, _, a, b, _ = results[str(p)]
        roots = 10 if p == 5 else 2
        assert 4 * p*p * h_k == roots * (a*a + b*b) * h_f, p


def check(with_arb):
    check_at_thirteen()
    results = {}
    for p in range(5, LIMIT, 8):
        if not prime(p):
            continue
        g, phases = quartic_character(p)
        sums = [0] * 4
        for n, phase in enumerate(phases, 1):
            sums[phase] += n
            assert phases[p - n - 1] == (phase + 2) % 4
        a, b = sums[0] - sums[2], sums[1] - sums[3]
        assert a % 2 == b % 2 == 1, p
        if p > 5:
            assert a % p == b % p == 0, p
            assert ((a//p)**2 + (b//p)**2) % 8 == 2, p
        else:
            assert (a, b) == (-3, -1)
        analytic = analytic_replay(p, phases, a, b) if with_arb else None
        results[str(p)] = [g, sums, a, b, analytic]
    assert results["13"][2:4] == [-13, -13]
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arb", action="store_true", help="check L(1, chi) by Arb's digamma function")
    parser.add_argument("--gp", type=Path, help="path to gp for certified class-group comparison")
    parser.add_argument("--json", type=Path, help="write a browser reference")
    args = parser.parse_args()
    cases = check(args.arb)
    if args.gp:
        check_class_groups(args.gp.resolve(), cases)
    if args.json:
        args.json.write_text(json.dumps(cases), encoding="utf-8")
    print(f"{len(cases)} prime conductors pass the exact quartic moment checks."
          + (" Independent Arb analytic values agree." if args.arb else "")
          + (" Both PARI class groups are certified in every case." if args.gp else ""))
