# Independent numbers for 'Signs at every prime'. This program knows nothing about signs or Hilbert symbols.
# For each pair (delta, x) it simply searches for fractions a, b with a*a - delta*b*b = x, with wide limits,
# and counts how many pairs have one. By the Hasse norm theorem (and the trivial case when delta is a square)
# that count must equal the number of pairs where every local sign is +1, which is what the page computes.
from math import isqrt
G = 24
def solvable(x, d, cmax=400, bmax=6000):
    for C in range(1, cmax + 1):
        xc = x * C * C
        for B in range(0, bmax + 1):
            t = xc + d * B * B
            if t >= 0:
                r = isqrt(t)
                if r * r == t: return (r, B, C)
            elif d < 0: break            # t only decreases from here
    return None
pairs = found = 0; biggest = (0, None)
for d in range(-G, G + 1):
    for x in range(-G, G + 1):
        if d == 0 or x == 0: continue
        pairs += 1
        s = solvable(x, d)
        if s:
            found += 1
            if s[2] > biggest[0]: biggest = (s[2], (d, x, s))
print("pairs:", pairs, "; with a solution found:", found, "; largest denominator needed:", biggest)
