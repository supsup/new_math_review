#!/usr/bin/env python3
"""check_one_row_at_a_time.py [OUT.json]

The separate program behind one_row_at_a_time.html. For 238 top rows (two to six whole numbers that never go up) it
writes out every candidate triangle, keeps the ones in which every number sits between its two neighbours in the row
above, and compares the count with the hook-content formula for the dimension, a different formula from the one the
page uses. It also checks the three-number formula (m1 + 1)(m2 + 1)(m1 + m2 + 2)/2, three rows with negative entries,
and gives the hook-content value alone for three rows too large to write out. Standard library only."""
# Independent numbers for the page 'One row at a time'. Written apart from the page's JavaScript and by other routes.
# Triangles are counted by writing every candidate out and testing it: each lower row is ANY row of whole numbers that
# never goes up, with entries between the smallest and largest of the top row, and a candidate counts only if every
# number sits between its two neighbours in the row above. Dimensions come from the hook-content formula for
# semistandard tableaux, not from Weyl's product. Standard library only.
import json, sys
from itertools import product
from fractions import Fraction
def rows(n, lo, hi):                       # rows of n whole numbers, hi >= a1 >= ... >= an >= lo
    def rec(k, cap):
        if k == 0: yield (); return
        for v in range(cap, lo - 1, -1):
            for rest in rec(k - 1, v): yield (v,) + rest
    return list(rec(n, hi))
def fits(upper, lower):                    # every number of the lower row between two neighbours of the upper one
    return all(upper[i] >= lower[i] >= upper[i + 1] for i in range(len(lower)))
def brute(lam):                            # write out every candidate triangle under lam and keep the ones that pass
    n = len(lam)
    if n == 1: return 1
    lo, hi = min(lam), max(lam)
    count = 0
    for tri in product(*[rows(k, lo, hi) for k in range(n - 1, 0, -1)]):
        prev, ok = lam, True
        for r in tri:
            if not fits(prev, r): ok = False; break
            prev = r
        count += ok
    return count
def hook_content(lam):                     # number of semistandard tableaux of shape lam with entries 1..n
    n = len(lam); f = Fraction(1)
    for i, row in enumerate(lam):
        for j in range(row):
            arm = row - j - 1; leg = sum(1 for k in range(i + 1, n) if lam[k] > j)
            f *= Fraction(n + j - i, arm + leg + 1)
    assert f.denominator == 1
    return int(f)
out = {"dims": {}, "steps": {}, "su3": [], "hook_only": {}}
checked = 0
for n, top in ((2, 6), (3, 5), (4, 4), (5, 3), (6, 2)):
    for lam in rows(n, 0, top):
        b, h = brute(lam), hook_content(lam)
        assert b == h, (lam, b, h)
        checked += 1
        out["dims"][" ".join(map(str, lam))] = b
        steps = 1
        for i in range(n - 1): steps *= lam[i] - lam[i + 1] + 1
        assert steps == sum(1 for r in rows(n - 1, min(lam), max(lam)) if fits(lam, r))
        out["steps"][" ".join(map(str, lam))] = steps
for m1 in range(0, 5):
    for m2 in range(0, 5):
        lam = (m1 + m2, m2, 0); out["su3"].append([m1, m2, brute(lam), (m1 + 1) * (m2 + 1) * (m1 + m2 + 2) // 2])
        assert out["su3"][-1][2] == out["su3"][-1][3]
# adding the same whole number to every entry does not change the count
for lam in ((3, 1, -2), (0, -1, -1, -4), (2, 2, -1)):
    out["dims"][" ".join(map(str, lam))] = brute(lam)
    assert brute(lam) == hook_content(tuple(v - min(lam) for v in lam))
# rows too large to write out: the hook-content formula alone
for lam in ((9, 7, 5, 3, 1, 0), (6, 4, 4, 1, 0, 0), (8, 8, 2, 0)):
    out["hook_only"][" ".join(map(str, lam))] = hook_content(lam)
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "expect_w.json", "w"))
print("top rows with every candidate triangle written out and tested, against the hook-content formula:", checked, "; largest dimension:", max(out["dims"].values()), "; three-number cases:", len(out["su3"]))
for k in ("4 2 0", "3 3 1 0", "3 2 1 0", "5 3 0", "3 3 2 1 0", "2 2 1 1 0 0"): print(k, out["dims"][k], out["steps"][k])
print("hook-content only:", out["hook_only"])
