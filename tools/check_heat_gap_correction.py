"""Check the two-term heat gap estimate using mpmath 1.3.0."""

import mpmath as mp

from check_lehmer_heat import collision_from_heat, gaussian_wave, initial_wave


def local_correction(wave, height, s, quadrature):
    second = third = fourth = mp.mpf(0)
    root = mp.sqrt(s)
    for q, weight in quadrature:
        value = weight * wave(height + root * q)
        second += value * (4*q*q - 2) / s
        third += value * (8*q**3 - 12*q) / (s*root)
        fourth += value * (16*q**4 - 48*q*q + 12) / s**2
    return fourth/(6*second) - (third/second)**2/9


def errors(square_gap, time_to_meeting, correction):
    first = 2 * time_to_meeting
    second = first + correction * time_to_meeting**2
    return abs(square_gap - first), abs(square_gap - second)


def check_pair(label, seed_height, seed_time, quadrature):
    center = mp.mpf(seed_height)
    wave = initial_wave(center)
    height, s = collision_from_heat(wave, center, mp.mpf(seed_time), quadrature)
    correction = local_correction(wave, height, s, quadrature)
    delta = s / 100
    half_gap = mp.sqrt(delta / 2)
    roots = []
    for sign in (-1, 1):
        guess = height + sign * half_gap
        neighbor = height + sign * half_gap * mp.mpf('1.08')
        root = mp.findroot(lambda y: gaussian_wave(wave, y, s - delta, quadrature), (guess, neighbor))
        roots.append(root)
    first_error, second_error = errors((roots[1] - roots[0])**2, delta, correction)
    assert second_error < first_error / 100
    print(label, 'C =', mp.nstr(correction, 10), 'errors:', mp.nstr(first_error, 6), mp.nstr(second_error, 6))
    return s, correction


def main():
    mp.mp.dps = 41
    quadrature = list(zip(*mp.gauss_quadrature(35, 'hermite')))
    check_pair('4 and 5', '33.098733806451809', '3.954792523754729', quadrature)
    check_pair('2 and 3', '27.321227695301292', '12.494513129643947', quadrature)
    s, correction = check_pair('the Lehmer pair', '7005.081714705492812', '0.0007112047339029822', quadrature)

    start, end = [mp.im(mp.zetazero(i)) for i in (6709, 6710)]
    first_error, second_error = errors((end - start)**2, s, correction)
    assert second_error < first_error / 1000
    print('Lehmer pair at t = 0 errors:', mp.nstr(first_error, 6), mp.nstr(second_error, 6))


if __name__ == '__main__':
    main()
