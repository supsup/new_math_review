"""Fit and cross-check the local Lehmer pair picture using mpmath 1.3.0.

The output gives ascending coefficients of the scaled initial wave in the
ordinary zeta-height coordinate d = height - CENTER. The heat parameter is
s = -t, so the operator in this coordinate is exp((s/4) D_d^2).
"""

import json

import mpmath as mp


CENTER = '7005.0817147054928121763114'
COLLISION = '0.0007112047339029822072721'


def initial_wave(center):
    quarter = mp.mpf('0.25')
    base_gamma = mp.re(mp.loggamma(mp.mpc(quarter, center / 2)))
    base_norm = center**2 + quarter

    def scaled(height):
        gamma = mp.re(mp.loggamma(mp.mpc(quarter, height / 2)))
        envelope = (height**2 + quarter) / base_norm * mp.exp(gamma - base_gamma)
        return envelope * mp.siegelz(height)

    return scaled


def heated_polynomial(coefficients, s):
    result = list(coefficients)
    current = list(coefficients)
    for degree in range(1, (len(coefficients) + 1) // 2):
        current = [a * i * (i - 1) * s / (4 * degree) for i, a in enumerate(current) if i >= 2]
        for i, a in enumerate(current):
            result[i] += a
    return result


def gaussian_wave(f, height, s, quadrature):
    if not s:
        return f(height)
    root = mp.sqrt(s)
    return mp.fsum(w * f(height + root * q) for q, w in quadrature) / mp.sqrt(mp.pi)


def collision_from_heat(f, center, s, quadrature):
    y = center
    for _ in range(7):
        h = [mp.mpf(0)] * 4
        root = mp.sqrt(s)
        for q, w in quadrature:
            value = w * f(y + root * q)
            kernel_derivatives = [1, 2*q/root, (4*q*q-2)/s, 8*q*(q*q-mp.mpf('1.5'))/(s*root)]
            for i, kd in enumerate(kernel_derivatives):
                h[i] += value * kd
        jacobian = mp.matrix([[h[1], h[2] / 4], [h[2], h[3] / 4]])
        dy, ds = mp.lu_solve(jacobian, mp.matrix(h[:2]))
        y, s = y - dy, s - ds
        if max(abs(dy), abs(ds)) < mp.mpf('1e-30'):
            break
    assert h[2] != 0
    return y, s


def main():
    mp.mp.dps = 50
    center = mp.mpf(CENTER)
    meet = mp.mpf(COLLISION)
    f = initial_wave(center)
    coefficients = list(reversed(mp.chebyfit(lambda d: f(center + d), [-mp.mpf('0.5'), mp.mpf('0.5')], 24)))
    stored = [mp.mpf(float(c)) for c in coefficients]
    quadrature = list(zip(*mp.gauss_quadrature(28, 'hermite')))
    worst = mp.mpf(0)
    for s in [0, mp.mpf('0.00035'), meet, mp.mpf('0.0011')]:
        poly = heated_polynomial(stored, s)
        for d in map(mp.mpf, ['-0.055', '-0.021', '0', '0.027', '0.055']):
            exact = gaussian_wave(f, center + d, s, quadrature)
            approximate = mp.polyval(poly[::-1], d)
            worst = max(worst, abs(exact - approximate))
    actual_y, actual_s = collision_from_heat(f, center, meet, quadrature)
    assert abs(actual_y - center) < mp.mpf('1e-20')
    assert abs(actual_s - meet) < mp.mpf('1e-24')
    assert worst < mp.mpf('1e-14')
    print(f'Meeting: t = {mp.nstr(-actual_s, 25)}, height = {mp.nstr(actual_y, 25)}')
    print(f'Largest error on 20 spot checks: {mp.nstr(worst, 6)}')
    print(json.dumps([float(c) for c in coefficients]))


if __name__ == '__main__':
    main()
