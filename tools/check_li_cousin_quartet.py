"""Certify the first negative Li-style terms of the 135-degree mod-five quartet."""

from flint import arb, ctx

# Input disk from tools/check_spira_high_root.py at new_math_review 1bba76d.
REAL = '2.378755863122'
HEIGHT = '1174561.0989005927'
RADIUS = '1e-6'
FIRST = 7_379_974
LAST = 7_379_996


def check():
    ctx.dps = 70
    radius = arb(RADIUS).upper()
    beta, height = arb(REAL, radius), arb(HEIGHT, radius)
    square = beta**2 + height**2

    # w = (rho - 1)/rho has argument phi > 0 and modulus exp(-kappa).
    # Compute the tiny logarithm with log1p to retain the enclosure.
    phi = (height / (square - beta)).atan()
    kappa = -((1 - 2 * beta) / square).log1p() / 2
    turn = 2 * arb.pi()
    assert phi > kappa > 0

    def half_width(n):
        return (n * kappa).sinh().atan()

    # The half-width is strictly between 0 and n*kappa, and its derivative
    # is at most kappa. Both n*phi ± half_width(n) are increasing. For
    # n>0 their interval excludes zero, and these tests locate its first
    # meeting with 2*pi, followed by its first exit.
    assert (FIRST - 1) * phi + half_width(FIRST - 1) < turn
    assert FIRST * phi + half_width(FIRST) > turn
    assert LAST * phi - half_width(LAST) < turn
    assert (LAST + 1) * phi - half_width(LAST + 1) > turn
    assert (LAST + 1) * phi + half_width(LAST + 1) < 2 * turn

    def contribution(n):
        # 4(1 - cosh(n*kappa)*cos(n*phi)), evaluated without subtracting two
        # nearly equal numbers near one. Reduce the angle by one full turn.
        sine_square = ((n * phi - turn) / 2).sin()**2
        sinh_square = (n * kappa / 2).sinh()**2
        return 8 * (sine_square - sinh_square * (1 - 2 * sine_square))

    assert contribution(FIRST - 1) > 0
    assert contribution(FIRST) < 0
    assert contribution(LAST) < 0
    assert contribution(LAST + 1) > 0
    print(f'First negative index {FIRST:,}; first consecutive band ends at {LAST:,}.')
    for n in (FIRST - 1, FIRST, 7_379_985, LAST, LAST + 1):
        print(f'{n:,}: {contribution(n).str(8)}')

    # Put a+ib = w+1/w and eta = 2-a. The three Toeplitz diagonals can be
    # written in these terms, avoiding cancellation between adjacent Q_n.
    sine_square = (phi / 2).sin()**2
    sinh_square = (kappa / 2).sinh()**2
    eta = 4 * (sine_square - sinh_square * (1 - 2 * sine_square))
    a = 2 - eta
    b = -2 * kappa.sinh() * phi.sin()
    assert a > 0 and eta > abs(b)
    # Then d0=4*eta > 0, d1=2*eta*a+2*b^2 > 0 and d0-d1>0.
    # The first two sizes are positive definite.
    x = arb('1.999999999999275149')
    delta = x - a
    quadratic = 4 * eta * delta**2 - 8 * b**2 * delta - 4 * eta * b**2
    assert quadratic < 0
    print(f'Sizes 1 and 2 are positive definite. Size 3 gives {quadratic.str(9)} '
          'on the exact vector (1, -1.999999999999275149, 1).')


if __name__ == '__main__':
    check()
