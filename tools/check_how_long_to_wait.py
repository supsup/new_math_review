# Independent numbers for the page 'How long must you wait?': written apart from the page's JavaScript, with different methods
# (per-class search by stepping a, a+q, a+2q and a Miller-Rabin test; non-residues by Euler's criterion with pow).
from math import gcd, log
def is_prime(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17):          # deterministic below 3.4e14
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True
def least_prime(a, q):
    n = a if a > 1 else a + q
    while not is_prime(n): n += q
    return n
QMAX = 1500
rows = []
for q in range(2, QMAX + 1):
    cls = [a for a in range(1, q + 1) if gcd(a, q) == 1]
    best = max((least_prime(a % q if a % q else q, q), a % q) for a in cls) if q > 2 else (3, 1)
    phi = len(cls)
    rows.append((q, phi, best[0], best[1], (phi * log(q)) ** 2))
fails = [r[0] for r in rows if r[2] > r[4]]
tight = max(rows[2:], key=lambda r: r[2] / r[4])
worst_vs_q2 = max(rows, key=lambda r: r[2] / r[0] ** 2)
print("q with worst wait above (phi ln q)^2:", fails)
print("tightest for q >= 4:", tight[0], tight[2], round(tight[4], 2), round(tight[2] / tight[4], 4))
print("largest P(q)/q^2:", worst_vs_q2[0], worst_vs_q2[2], round(worst_vs_q2[2] / worst_vs_q2[0] ** 2, 4), "; any P(q) >= q^2:", [r[0] for r in rows if r[2] >= r[0] ** 2])
print("samples:", [(r[0], r[2], r[3]) for r in rows if r[0] in (3, 4, 5, 7, 10, 12, 100, 210, 997, 1000, 1500)])
print("largest worst wait:", max(rows, key=lambda r: r[2])[:4])
# least quadratic non-residue, record holders below 4e6
LIM = 4_000_000
sieve = bytearray([1]) * (LIM + 1); sieve[0] = sieve[1] = 0
for i in range(2, int(LIM ** 0.5) + 1):
    if sieve[i]: sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
small = [p for p in range(2, 200) if sieve[p]]
rec, recs, closest = 0, [], (0, 0.0)
for p in range(3, LIM + 1, 2):
    if not sieve[p]: continue
    for r in small:
        if pow(r, (p - 1) // 2, p) == p - 1:
            if r > rec: rec = r; recs.append((p, r))
            if p >= 5 and r / log(p) ** 2 > closest[1]: closest = (p, r / log(p) ** 2)
            break
print("closest call to (ln p)^2 among primes from 5 on:", closest[0], round(closest[1], 4))
print("record least non-residues:", recs)
print("records with 2 ln^2 p and ln^2 p:", [(p, r, round(2 * log(p) ** 2, 1), round(log(p) ** 2, 1)) for p, r in recs])
