"""Certify a 120° zero near the sharp wall with the direct Dirichlet series."""

from flint import acb, arb, ctx

from check_mirror_mix_contacts import I, root_number


REAL = "2.01236224768"
HEIGHT = "694397677.1926167"
RADIUS = "1e-5"
LIMIT = 1_000_000


def check():
    ctx.dps = 60
    center = acb(arb(REAL), arb(HEIGHT))
    radius = arb(RADIUS)
    left = center.real - radius
    assert left > 2

    # The 120° ratio target is sqrt(3)*epsilon, so the zeros in this
    # half-plane are the zeros of L(s, chi) - sqrt(3)*epsilon*L(s, chibar).
    multiplier = arb(3).sqrt() * root_number()
    char = (acb(0), acb(1), I, -I, acb(-1))
    coefficients = [value - multiplier*value.conjugate() for value in char]
    assert all(value.abs_upper() < 3 for value in coefficients)

    finite_value, derivative, curvature = acb(0), acb(0), arb(0)
    for n in range(1, LIMIT+1):
        if n % 5 == 0:
            continue
        log_n = arb(n).log()
        term = coefficients[n % 5] * (-center*log_n).exp()
        finite_value += term
        derivative -= log_n*term
        curvature += 3*log_n**2*(-left*log_n).exp()

    # Bound the omitted terms uniformly for every point in the disk.
    # Taylor's formula bounds the finite sum's departure from its linear part.
    tail = 3*arb(LIMIT)**(1-left)/(left-1)
    error = finite_value.abs_upper() + radius**2*curvature/2 + tail
    linear = radius*derivative.abs_lower()
    assert error < linear
    assert center.real + radius < arb("2.01758034")
    print(f"One simple 120° zero within {RADIUS} of {REAL} + {HEIGHT}i.")
    print(f"Uniform error {error.str(12)} < linear term {linear.str(12)}.")


if __name__ == "__main__":
    check()
