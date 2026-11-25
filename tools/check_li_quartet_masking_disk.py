"""Independently certify the masking brackets over the whole mod-five disk.

Reflecting the coordinates splits a symmetric Toeplitz matrix into two
blocks. The quartet has rank at most two in each block. In the polynomial
coordinate z = w + 1/w - 2, all real cancellations can be done before
substituting the interval for the root.
"""

from flint import acb, acb_poly, arb

from check_li_quartet_masking import brackets, first_rows


def normalized_polynomials(row, size, mirror_sign):
    """Return polynomial coordinates after whitening the zeta block."""
    half = size // 2
    paired = [
        ((half - 1 - j, 1), (size - half + j, mirror_sign))
        for j in range(half)
    ]
    has_middle = size % 2 == 1 and mirror_sign == 1
    basis = [((half, 1),)] + paired if has_middle else paired

    # A mirrored pair has basis value w^a ± w^(-a) in centered coordinates.
    # Peel off a common factor where needed. The remaining polynomials
    # satisfy P_(j+1) = (2+z) P_j - P_(j-1).
    one = acb_poly([1])
    u = acb_poly([2, 1])
    if size % 2:
        polynomials = [one, u]
    else:
        polynomials = [one, u - mirror_sign]
    while len(polynomials) < len(basis):
        previous = 2 * one if has_middle and len(polynomials) == 2 else polynomials[-2]
        polynomials.append(u * polynomials[-1] - previous)
    polynomials = polynomials[:len(basis)]

    # LDL elimination, applied to the polynomial coordinates before they
    # are evaluated. This keeps the interval radius out of the cancellations.
    block = [[sum(a * b * row[abs(i-j)] for i, a in left for j, b in right)
              for right in basis] for left in basis]
    coordinates = []
    for i in range(len(basis)):
        pivot = block[i][i]
        assert pivot > 0
        coordinates.append((1 / pivot.sqrt()) * polynomials[i])
        for j in range(i+1, len(basis)):
            multiplier = block[j][i] / pivot
            polynomials[j] -= multiplier * polynomials[i]
            for k in range(i+1, len(basis)):
                block[j][k] -= multiplier * block[i][k]
    return coordinates


def threshold(polynomials, scale, z):
    """Critical weight of I + weight Re(scale * U Uᵀ) in a whitened block."""
    values = [p(z) for p in polynomials]
    trace = (scale * sum(v * v for v in values)).real
    if len(values) == 1:
        assert trace > 0
        return None
    # For U = a+ib, the two directions use the coefficient matrix
    # [[Re(scale), -Im(scale)], [-Im(scale), -Re(scale)]]. The determinant
    # of the Gram matrix of a,b is the sum of squared two-row minors.
    gram_det = sum(
        (u.real * v.imag - u.imag * v.real)**2
        for i, u in enumerate(values) for v in values[:i]
    )
    negative_det = gram_det * (scale.real**2 + scale.imag**2)
    assert negative_det > 0
    discriminant = (trace**2 + 4 * negative_det).sqrt()
    # Reciprocal of the absolute negative eigenvalue, rationalized when
    # the trace is positive so the near-cancellation never occurs.
    if trace > 0:
        return (trace + discriminant) / (2 * negative_det)
    return 2 / (discriminant - trace)


def verify():
    expected = brackets()
    row, _ = first_rows()
    blocks = [(size, lo, hi, decade, normalized_polynomials(row, size, 1),
               normalized_polynomials(row, size, -1)) for size, lo, hi, decade in expected]
    radius = arb("1e-6")
    real = arb("2.378755863122")
    height = arb("1174561.0989005927")
    # Cover the entire square enclosing the disk by 16 closed boxes.
    offsets = [(2*j-3) * radius / 4 for j in range(4)]
    half_side = (radius / 4).upper()
    at_size_24 = None
    for x in offsets:
        for y in offsets:
            rho = acb(real + x + arb(0, half_side), height + y + arb(0, half_side))
            z = 1 / (rho * (rho - 1))
            d0 = -4 * z.real
            difference = 2 * (z * z).real
            assert d0 > 0 and difference > 0 and 2 * d0 > difference
            for size, lo, hi, decade, mirrored, antimirrored in blocks:
                if size % 2:
                    even_scale = -4 * z
                    odd_scale = 4 * z*z * (z+4)
                else:
                    even_scale = -4 * z * (z+4)
                    odd_scale = 4 * z*z
                even = threshold(mirrored, even_scale, z)
                odd = threshold(antimirrored, odd_scale, z)
                scale = 10**(decade - 3)
                assert lo * scale < even < hi * scale, (size, even)
                assert odd is None or hi * scale < odd, (size, odd)
                if size == 24:
                    assert odd is not None
                    at_size_24 = odd if at_size_24 is None else at_size_24.union(odd)
    assert arb("4.281e42") < at_size_24 < arb("4.282e42")
    print("All 22 display brackets hold throughout the certified disk.")
    print("A mirrored vector always reaches the first failure.")
    print("Size-24 threshold with opposite weights across the center:", at_size_24.str(8))


if __name__ == "__main__":
    verify()
