"""Replay for crew_visuals/prime_gaps_rh.html (Confluence).

1. Compile tools/prime_gap_records.c in a temporary directory and run it to 10^10 (about 20 s); compare its JSON,
   minified, with the JSON embedded in the page, byte for byte.
2. Compare the 35 record gaps with the OEIS table A002386 / A005250 as fetched on 2026-11-25 (typed below from
   that fetch), and check pi(10^10) = 455,052,511, the standard value.
3. Check the Carneiro-Milinovich-Soundararajan quantity gap / (sqrt p log p): at most 22/25 for every record
   after 3, largest 0.7769 at p = 7, and above 1 at p = 3 (why their theorem starts after 3).
Standard library only, plus a C compiler. Usage:  python3 tools/check_prime_gaps_rh.py [N]
"""

import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OEIS_PRIMES = [2, 3, 7, 23, 89, 113, 523, 887, 1129, 1327, 9551, 15683, 19609, 31397, 155921, 360653, 370261, 492113,
               1349533, 1357201, 2010733, 4652353, 17051707, 20831323, 47326693, 122164747, 189695659, 191912783,
               387096133, 436273009, 1294268491, 1453168141, 2300942549, 3842610773, 4302407359]
OEIS_GAPS = [1, 2, 4, 6, 8, 14, 18, 20, 22, 34, 36, 44, 52, 72, 86, 96, 112, 114, 118, 132, 148, 154, 180, 210, 220,
             222, 234, 248, 250, 282, 288, 292, 320, 336, 354]


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 10
    page = (ROOT / 'crew_visuals' / 'prime_gaps_rh.html').read_text()
    embedded = re.search(r'<script id="gaps" type="application/json">(.*?)</script>', page, re.S).group(1)
    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / 'gaps'
        subprocess.run(['cc', '-O2', '-o', str(exe), str(ROOT / 'tools' / 'prime_gap_records.c'), '-lm'], check=True)
        out = subprocess.run([str(exe), str(N)], check=True, capture_output=True, text=True).stdout
    fresh = json.loads(out)
    if N == 10 ** 10:
        assert json.dumps(fresh, separators=(',', ':')) == embedded, 'embedded data differ from a fresh run'
        assert fresh['primes'] == 455052511
        assert [r[0] for r in fresh['records']] == OEIS_PRIMES and [r[1] for r in fresh['records']] == OEIS_GAPS
    cms = lambda p: 22 / 25 * math.sqrt(p) * math.log(p)
    assert all(g <= cms(p) for p, g in fresh['records'] if p > 3)
    assert 2 > cms(3)
    p, g, r = fresh['max_ratio']
    assert (p, g) == (7, 4) and abs(r - 4 / (math.sqrt(7) * math.log(7))) < 1e-9
    print(f"Sieve to {N:,}: {fresh['primes']:,} primes, {len(fresh['records'])} record gaps, the last {fresh['records'][-1][1]} after {fresh['records'][-1][0]:,}.")
    if N == 10 ** 10:
        print("The page's data match byte for byte, the records match OEIS A002386/A005250, and pi(10^10) = 455,052,511.")
    print(f"Every record after 3 is within (22/25) sqrt(p) log p. Over all primes after 3 the largest gap / (sqrt p log p) is {r:.6f}, at p = 7, which is {r / 0.88:.1%} of the 22/25 bound; at p = 3 it would be {2 / (math.sqrt(3) * math.log(3)):.4f}, that is {2 / cms(3):.0%} of the bound.")


if __name__ == '__main__':
    main()
