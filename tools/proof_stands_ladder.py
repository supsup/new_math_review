"""The ladder for the card 'If the proof stands' (Confluence).

Usage:  python3 tools/proof_stands_ladder.py TREE OUT
TREE is a checkout of the site holding the crew pages each rung cites (for example fixpoint/round-six); OUT is where
art/proof_stands_ladder.svg and art/proof_stands_ladder_narrow.svg are written.

Each rung quotes one page of ours. Before drawing anything, the tool opens that page in TREE and refuses to write if
the page is missing or no longer contains the rung's witness strings (the number or phrase the rung repeats from it;
a witness written 'other/page.html::text' is looked for in that page instead),
so the picture cannot drift from the pages it summarises. It decides nothing about the mathematics: each rung's
statement is as its page reads it at its source.
"""

import html
import re
import sys
from pathlib import Path

# kind: 'eq' = equivalent to the Riemann Hypothesis; 'rh' = proved assuming it; 'l' = proved assuming the hypothesis
# for Dirichlet L-functions (the release's other final theorems); 'open' = still open even if the proof stands.
RUNGS = [
    ('eq', 'Robin', 'σ(n) < e^{γ}·n·log log n for every n > 5040', 'σ(n) < e^{γ}·n·log log n past 5040',
     '26 exceptions, all ≤ 5040', 'crew_visuals/robin_and_nicolas.html', ['5040', '26 of them']),
    ('eq', 'Nicolas', 'N/φ(N) > e^{γ}·log log N for every primorial N', 'N/φ(N) > e^{γ}·log log N, N = 2·3·5···p',
     '5,761,455 checked', 'crew_visuals/robin_and_nicolas.html', ['5,761,455']),
    ('eq', 'Lagarias', 'σ(n) ≤ H(n) + exp(H(n))·log H(n) for every n', 'σ(n) ≤ H(n) + exp(H(n))·log H(n)',
     'tightest at n = 12', 'crew_visuals/lagarias_divisor_race.html', ['Lagarias', 'crew_visuals/robin_and_nicolas.html::closest at n = 12']),
    ('eq', 'Franel, Landau', 'the absolute Farey offsets add up to O(N^{1/2+ε})', 'absolute Farey offsets sum to O(N^{1/2+ε})',
     'fractions off the grid', 'crew_visuals/farey_off_the_grid.html', ['Franel', r'N^{1/2+\varepsilon}', 'absolute value']),
    ('eq', 'Li', 'every one of Li’s numbers λₙ is ≥ 0', 'every Li number λₙ is ≥ 0',
     '50 zero pairs: 80.283% of λ₁', 'crew_visuals/li_zero_pairs.html', ['80.283%', 'nonnegative']),
    ('eq', 'de Bruijn, Newman', 'Λ ≤ 0; with Rodgers and Tao’s Λ ≥ 0, Λ = 0', 'Λ = 0, no room to spare',
     'no room to spare', 'no_room_to_spare.html', ['Rodgers and Tao', 'exactly 0']),
    ('rh', 'Schoenfeld', '|π(x) − li(x)| < √x·log x/(8π) for every x ≥ 2657', '|π(x) − li(x)| < √x·log x/(8π)',
     'from x = 2657', 'rh_buys.html', ['Schoenfeld', '2657', '8 * Math.PI']),
    ('rh', 'Carneiro et al.', 'after each prime p > 3, a prime within (22/25)·√p·log p', 'next prime within (22/25)·√p·log p',
     'below 10^{10}, closest 88.3% at 7', 'crew_visuals/prime_gaps_rh.html', ['22/25', '88.3%', '10¹⁰']),
    ('l', 'Littlewood', 'L(1, χ) of a quadratic field stays in a log log band', 'L(1, χ) in a log log band',
     '1,215,854 fields drawn', 'crew_visuals/class_numbers_band.html', ['1,215,854', 'Littlewood']),
    ('l', 'Weinberger, Kani', 'Euler’s convenient numbers are exactly 65', 'Euler’s list is exactly 65 numbers',
     'the largest is 1848', 'crew_visuals/euler_convenient_numbers.html', ['1848', 'exactly 65']),
    ('l', 'Miller, Bach', 'witnesses up to 2·(ln n)² decide whether n is prime', 'witnesses to 2·(ln n)² decide primality',
     'a test becomes a proof', 'rh_buys.html', ['Bach', 'Miller']),
    ('l', 'Lamzouri et al.', 'the least positive non-square mod p is below (ln p)²', 'least non-square mod p below (ln p)²',
     'every prime p ≥ 5', 'how_long_to_wait.html', ['(ln p)²', 'Lamzouri']),
    ('open', 'Legendre', 'a prime between any two consecutive squares', 'a prime between consecutive squares',
     'RH’s gap bound too weak from x = 14 on', 'crew_visuals/prime_gaps_rh.html', ['x = 14', 'Legendre']),
    ('open', 'Cramér', 'gaps between primes never much above (log p)²', 'gaps never much above (log p)²',
     'records to 10^{10}: 0.72·(log p)²', 'crew_visuals/prime_gaps_rh.html', ['0.72', 'Cramér', '10¹⁰']),
    ('open', 'Simple zeros', 'every zero of zeta is a single zero', 'every zero of zeta is single',
     '≥ 67% of the count, far enough up', 'showcase.html', ['67%', 'card-zeta23', 'large enough']),
]
NARROW_HEAD = {'l': 'On the Dirichlet form of it', 'rh': 'Proved long ago, on it', 'eq': 'These are the Riemann Hypothesis',
               'open': 'Still open, even if it stands'}
GROUPS = {'eq': ('These are the Riemann Hypothesis', 'each is true exactly when every zero is on the line', '#2f6f4f'),
          'rh': ('Proved long ago, on the Riemann Hypothesis', 'waiting for it', '#2b5c8a'),
          'l': ('Proved on the same hypothesis for Dirichlet L-functions', 'the release’s other final theorems', '#5a4b9a'),
          'open': ('Still open, even if the proof stands', 'what the hypothesis does not reach', '#a3261e')}
INK, MUTED, BG, LINE, RAIL = '#1d1b18', '#6b645a', '#fbf9f4', '#e3ddd2', '#8a4b16'


def page_text(tree, rel):
    p = Path(tree) / rel
    if not p.exists():
        sys.exit(f'REFUSING: {rel} is not in the tree')
    raw = p.read_text(encoding='utf-8')
    return raw, re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', raw)))


def esc(s):
    """Escape, then turn ^{...} into a raised, smaller tspan."""
    out = html.escape(s, quote=True)
    return re.sub(r'\^\{([^}]*)\}', r'<tspan baseline-shift="super" font-size="72%">\1</tspan>', out)


def plain_len(s):
    return len(re.sub(r'\^\{([^}]*)\}', r'\1', s))


def draw(narrow):
    W = 360 if narrow else 880
    L, R = (14, W - 14) if narrow else (34, W - 34)
    rowh = 46 if narrow else 30
    y = 44 if narrow else 48
    out, rails_top = [], y - 10
    title = 'If the proof stands' if narrow else 'If the proof stands: what becomes true, and what does not'
    out.append(f'<text x="{W / 2}" y="26" font-size="{17 if narrow else 19}" text-anchor="middle" fill="{INK}" font-family="Georgia, serif">{esc(title)}</text>')
    last = None
    for kind, name, stmt, short, num, page, _ in RUNGS:
        if kind != last:
            head, sub, col = GROUPS[kind]
            y += 10 if last else 0
            out.append(f'<text x="{L + 6}" y="{y + 12}" font-size="{12 if narrow else 13}" fill="{col}" font-family="Georgia, serif" font-weight="bold">{esc(NARROW_HEAD[kind] if narrow else head)}</text>')
            if not narrow:
                out.append(f'<text x="{R - 6}" y="{y + 12}" font-size="12" fill="{MUTED}" text-anchor="end" font-family="Georgia, serif" font-style="italic">{esc(sub)}</text>')
            y += 20
            last = kind
        head, sub, col = GROUPS[kind]
        dash = ' stroke-dasharray="5 4"' if kind == 'open' else ''
        fill = '#ffffff' if kind != 'open' else BG
        out.append(f'<rect x="{L}" y="{y}" width="{R - L}" height="{rowh - 6}" rx="5" fill="{fill}" stroke="{col}" stroke-width="1.4"{dash}/>')
        if narrow:
            out.append(f'<text x="{L + 8}" y="{y + 16}" font-size="12.5" fill="{col}" font-family="Georgia, serif" font-weight="bold">{esc(name)}</text>')
            out.append(f'<text x="{R - 8}" y="{y + 16}" font-size="11" fill="{MUTED}" text-anchor="end" font-family="Georgia, serif">{esc(num)}</text>')
            out.append(f'<text x="{L + 8}" y="{y + 33}" font-size="12" fill="{INK}" font-family="Georgia, serif">{esc(short)}</text>')
        else:
            out.append(f'<text x="{L + 10}" y="{y + 16}" font-size="13" fill="{col}" font-family="Georgia, serif" font-weight="bold">{esc(name)}</text>')
            out.append(f'<text x="{L + 150}" y="{y + 16}" font-size="13" fill="{INK}" font-family="Georgia, serif">{esc(stmt)}</text>')
            out.append(f'<text x="{R - 10}" y="{y + 16}" font-size="12" fill="{MUTED}" text-anchor="end" font-family="Georgia, serif">{esc(num)}</text>')
        y += rowh
    H = y + 14
    rails = (f'<line x1="{L - 6}" x2="{L - 6}" y1="{rails_top}" y2="{H - 8}" stroke="{RAIL}" stroke-width="3"/>'
             f'<line x1="{R + 6}" x2="{R + 6}" y1="{rails_top}" y2="{H - 8}" stroke="{RAIL}" stroke-width="3"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="A ladder of {len(RUNGS)} statements: six equivalent to the Riemann Hypothesis, six proved on it or on its '
            f'Dirichlet form, and three still open even if the proof stands">'
            f'<rect width="{W}" height="{H}" fill="{BG}"/>{rails}' + ''.join(out) + '</svg>\n')


def main():
    tree, out = sys.argv[1], Path(sys.argv[2])
    for kind, name, stmt, short, num, page, witnesses in RUNGS:
        for w in witnesses:
            src, w = w.split('::') if '::' in w else (page, w)
            raw, text = page_text(tree, src)
            if w not in text and w not in raw:
                sys.exit(f'REFUSING: {src} no longer says {w!r} (rung {name})')
        if plain_len(short) > 46:
            sys.exit(f'REFUSING: the narrow line for {name} is too long for 360 pixels')
    (out / 'art').mkdir(parents=True, exist_ok=True)
    (out / 'art' / 'proof_stands_ladder.svg').write_text(draw(False), encoding='utf-8')
    (out / 'art' / 'proof_stands_ladder_narrow.svg').write_text(draw(True), encoding='utf-8')
    kinds = [r[0] for r in RUNGS]
    print(f'{len(RUNGS)} rungs, each checked against its page: {kinds.count("eq")} equivalent, {kinds.count("rh")} on RH, '
          f'{kinds.count("l")} on the Dirichlet form, {kinds.count("open")} still open. Wrote art/proof_stands_ladder.svg and _narrow.svg.')


if __name__ == '__main__':
    main()
