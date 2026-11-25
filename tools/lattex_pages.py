"""Typeset the formulas on Confluence's round-two pages with LatteX (Charles, 2026-11-25: use LatteX, so that we find
what the library is missing; check the look with BrewShot).

Usage:  LATTEX_JAR=/path/to/lattex.jar python3 tools/lattex_pages.py [--report] PAGE...

Each page below has a list of (snippet, LaTeX, mode, template): the exact HTML of a formula as the page set it by
hand, the same formula in LaTeX, and how to place it. Mode 'i' sets it inline on the line of text (LatteX --inline),
'd' as its own centred line inside the paragraph (any punctuation after it is part of the snippet and the LaTeX, so it does not start the next line),  'D' as a block replacing a whole <p>. The template puts the SVG
('{}') back among any words the snippet carried. The tool replaces each snippet exactly once (or every time, for a
mode ending in '*'), in the page's static HTML only (never inside a script), and adds one small style rule.

It REFUSES to write a page if a snippet is missing or ambiguous, if LatteX reports an error, or if an SVG contains
LatteX's boxed-question-mark glyph (outline 'M595 -169 L10 -169 L10 785 L595 785', found by Fixpoint, 35625), which
LatteX draws with no error for characters it lacks. --report renders and lists every formula and problem without
writing. A page is converted once: run it on the page as built, before LatteX; a second run finds no snippets.

Sizes: LatteX draws at 40 units to the em with the baseline at y = 0, so an SVG of viewBox (x, -a, w, h) is set
w/40 em wide and h/40 em high, lowered by (h - a)/40 em, and display formulas at 1.1 times that. A display formula keeps its size on a narrow screen and scrolls sideways inside its own box, rather than shrinking past legibility.
"""

import html
import os
import re
import subprocess
import sys

JAR = os.environ.get('LATTEX_JAR', '')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BOX = 'M595 -169 L10 -169 L10 785 L595 785'
EM = 40.0
STYLE = ('\n  svg.tex { display:inline-block; background:none; border-radius:0; margin:0; overflow:visible; }'
         '\n  .texd { display:block; margin:8px 0; text-align:center; overflow-x:auto; overflow-y:hidden; }'
         '\n  .texd svg.tex { max-width:none; }\n')

SPECS = {
    'crew_visuals/robin_and_nicolas.html': [
        ('<b>e<sup>γ</sup>·log log n</b>', r'e^{\gamma}\log\log n', 'i', '<b>{}</b>'),
        ('<span class="formula">σ(n) &lt; e<sup>γ</sup>·n·log log n</span>', r'\sigma(n) < e^{\gamma}\, n\log\log n', 'i', '{}'),
        ('<span class="formula">N/φ(N) &gt; e<sup>γ</sup>·log log N</span>', r'N/\varphi(N) > e^{\gamma}\log\log N', 'i', '{}'),
        ("Nicolas's c = (N/φ(N) − e<sup>γ</sup> log log N)·√log N", r'c = \bigl(N/\varphi(N) - e^{\gamma}\log\log N\bigr)\sqrt{\log N}', 'i', "Nicolas's {}"),
        ("Robin's D = (e<sup>γ</sup> log log n − σ(n)/n)·√log n", r'D = \bigl(e^{\gamma}\log\log n - \sigma(n)/n\bigr)\sqrt{\log n}', 'i', "Robin's {}"),
        ('e<sup>γ</sup>(2 + β) = 3.64441…', r'e^{\gamma}(2+\beta) = 3.64441\ldots', 'i', '{}'),
        ('β = Σ 1/(ρ(1 − ρ))', r'\beta = \sum_{\rho} \frac{1}{\rho(1-\rho)}', 'i', '{}'),
        ('c(n) = (n/φ(n) − e<sup>γ</sup> log log n)·√log n', r'c(n) = \bigl(n/\varphi(n) - e^{\gamma}\log\log n\bigr)\sqrt{\log n}', 'i', '{}'),
        ('<p class="formula" style="white-space:normal">σ(n)/(n log log n) = [N/(φ(N) log log N)] · ∏ (1 − p<sup>−a<sub>p</sub>−1</sup>) · (log log N / log log n).</p>',
         r'\frac{\sigma(n)}{n\log\log n} = \frac{N}{\varphi(N)\log\log N}\cdot\prod_{p}\bigl(1-p^{-a_p-1}\bigr)\cdot\frac{\log\log N}{\log\log n}.', 'D', '{}'),
        ('<p class="formula" style="white-space:normal">D = T<sub>1</sub> + T<sub>2</sub> − c′,</p>', r"D = T_1 + T_2 - c',", 'D', '{}'),
        ('<b>T<sub>1</sub></b> = √(log n)·e<sup>γ</sup>·log(log n / log N)', r'T_1 = \sqrt{\log n}\; e^{\gamma}\log\frac{\log n}{\log N}', 'i', '{}'),
        ('<b>T<sub>2</sub></b> = √(log n)·(N/φ(N))·(1 − ∏(1 − p<sup>−a<sub>p</sub>−1</sup>))', r'T_2 = \sqrt{\log n}\;\frac{N}{\varphi(N)}\Bigl(1-\prod_p\bigl(1-p^{-a_p-1}\bigr)\Bigr)', 'i', '{}'),
        ('e<sup>γ</sup>(2√2 − 2 − β) = e<sup>γ</sup>(2√2 − 4 − γ + log 4π) ≈ 1.3932.', r'e^{\gamma}(2\sqrt{2}-2-\beta) = e^{\gamma}(2\sqrt{2}-4-\gamma+\log 4\pi) \approx 1.3932.', 'd', '{}'),
        ('σ(n) &lt; e<sup>γ</sup>·n·log log n + 0.6482·n/log log n', r'\sigma(n) < e^{\gamma}\, n\log\log n + 0.6482\,\frac{n}{\log\log n}', 'd', '{}'),
        ('σ(n) ≤ H<sub>n</sub> + exp(H<sub>n</sub>)·log H<sub>n</sub>', r'\sigma(n) \le H_n + \exp(H_n)\log H_n', 'i', '{}'),
        ('H<sub>n</sub> = 1 + 1/2 + ⋯ + 1/n', r'H_n = 1 + \tfrac12 + \cdots + \tfrac1n', 'i', '{}'),
    ],
    'crew_visuals/prime_gaps_rh.html': [
        ('<b>(22/25)·√p·log p</b>', r'\tfrac{22}{25}\sqrt{p}\,\log p', 'i', '<b>{}</b>'),
        ('(22/25)·√p·log p, the bound on RH', r'\tfrac{22}{25}\sqrt{p}\,\log p', 'i', '{}, the bound on RH'),
        ('2√p + 1, the room between consecutive squares', r'2\sqrt{p}+1', 'i', '{}, the room between consecutive squares'),
        ('gap/(√p·log p)', r'\text{gap}/(\sqrt{p}\,\log p)', 'i', '{}'),
        ('O(√p·log p)', r'O(\sqrt{p}\,\log p)', 'i', '{}'),
        ('[x, x + (22/25)√x log x]', r'\bigl[x,\ x+\tfrac{22}{25}\sqrt{x}\,\log x\bigr]', 'i', '{}'),
        ('p<sub>n+1</sub> − p<sub>n</sub> ≤ (22/25)√p<sub>n</sub> log p<sub>n</sub>', r'p_{n+1}-p_n \le \frac{22}{25}\sqrt{p_n}\,\log p_n', 'd', '{}'),
        ('0.88·√x·log x', r'0.88\sqrt{x}\,\log x', 'i', '{}'),
    ],
    'crew_visuals/euler_convenient_numbers.html': [
        ('m = x² + n·y²', r'm = x^2 + n y^2', 'i', '{}'),
        ('a·x² + 2b·xy + c·y²', r'a x^2 + 2b\,xy + c y^2', 'i*', '{}'),
        ('ac − b² = n', r'ac - b^2 = n', 'i*', '{}'),
        ('2|b| ≤ a ≤ c', r'2|b| \le a \le c', 'i', '{}'),
        ('1 − 1/(4 log d) ≤ s &lt; 1', r'1-\frac{1}{4\log d} \le s < 1', 'i', '{}'),
        ('Re s &gt; ½, L(s, χ) ≠ 0', r'\operatorname{Re} s > \tfrac12,\ L(s,\chi)\neq 0', 'i', '{}'),
    ],
    'crew_visuals/class_numbers_band.html': [
        ('<b>h = √d · L(1, χ) / π</b>', r'h = \sqrt{d}\,L(1,\chi)/\pi', 'i', '<b>{}</b>'),
        ('(2 + o(1))·e^γ·log log d', r'\bigl(2+o(1)\bigr)\,e^{\gamma}\log\log d', 'i', '{}'),
        ('(½ + o(1))·ζ(2)/(e^γ log log d) ≤ L(1, χ_d) ≤ (2 + o(1))·e^γ log log d,',
         r'\Bigl(\tfrac12+o(1)\Bigr)\frac{\zeta(2)}{e^{\gamma}\log\log d} \le L(1,\chi_d) \le \bigl(2+o(1)\bigr)\,e^{\gamma}\log\log d,', 'd', '{}'),
        ('character χ_d of a fundamental', r'\chi_d', 'i', 'character {} of a fundamental'),
        ('|L(1, χ)| ≤ 2e^γ(log log q − log 2 + ½ + 1/log log q),',
         r'|L(1,\chi)| \le 2e^{\gamma}\Bigl(\log\log q - \log 2 + \tfrac12 + \frac{1}{\log\log q}\Bigr),', 'd', '{}'),
        ('1/|L(1, χ)| ≤ (12e^γ/π²)(log log q − log 2 + ½ + 1/log log q + 14 log log q / log q).',
         r'\frac{1}{|L(1,\chi)|} \le \frac{12e^{\gamma}}{\pi^2}\Bigl(\log\log q - \log 2 + \tfrac12 + \frac{1}{\log\log q} + \frac{14\log\log q}{\log q}\Bigr).', 'd', '{}'),
        ('h = Σ χ(a) / (2 − χ(2)) over 0 &lt; a &lt; d/2', r'h = \frac{1}{2-\chi(2)}\sum_{0<a<d/2}\chi(a)', 'i', '{}'),
        ('ζ(2)/(e^γ(log log d + log log log d))', r'\zeta(2)\big/\bigl(e^{\gamma}(\log\log d + \log\log\log d)\bigr)', 'i', '{}'),
        ('e^γ(log log d + log log log d)', r'e^{\gamma}(\log\log d + \log\log\log d)', 'i', '{}'),
        ('about e^γ times', r'e^{\gamma}', 'i', 'about {} times'),
        ('values of L(1, χ_d)', r'L(1,\chi_d)', 'i', 'values of {}'),
    ],
    'crew_visuals/artin_map_roots_of_unity.html': [
        ('ζ, ζ², …, ζⁿ = 1', r'\zeta, \zeta^2, \ldots, \zeta^n = 1', 'i', '{}'),
        ('ζ = e<sup>2πi/n</sup>', r'\zeta = e^{2\pi i/n}', 'i', '{}'),
        ('σ<sub>a</sub> sends ζ to ζ<sup>a</sup>', r'\sigma_a\colon \zeta \mapsto \zeta^a', 'i', '{}'),
        ('<b>σ<sub>p</sub>, "raise to the p-th power"</b>', r'\sigma_p', 'i', '<b>{}, "raise to the p-th power"</b>'),
        ('φ(n)/f primes', r'\varphi(n)/f', 'i', '{} primes'),
        ('σ<sub>p</sub><sup>−1</sup> = σ<sub>p′</sub>', r"\sigma_p^{-1} = \sigma_{p'}", 'i', '{}'),
        ('ζ<sup>p′</sup>, not to ζ<sup>p</sup>', r"\zeta^{p'}", 'i', '{}, not to ζ<sup>p</sup>'),
        ('n = p<sup>k</sup>m', r'n = p^k m', 'i', '{}'),
        ('φ(p<sup>k</sup>) of them', r'\varphi(p^k)', 'i', '{} of them'),
        ('Φ<sub>n</sub> ≡ Φ<sub>m</sub><sup>e</sup> mod p', r'\Phi_n \equiv \Phi_m^{\,e} \pmod{p}', 'i', '{}'),
        ('xⁿ − 1', r'x^n - 1', 'i', '{}'),
        ('x<sup>p<sup>d</sup></sup> − x', r'x^{p^d} - x', 'i', '{}'),
    ],
    'crew_visuals/hecke_l_at_one.html': [
        ('L(s, χ) = ∏<sub>v</sub> (1 − χ(π<sub>v</sub>)·N(v)<sup>−s</sup>)<sup>−1</sup>,', r'L(s,\chi) = \prod_{v}\bigl(1-\chi(\pi_v)\,N(v)^{-s}\bigr)^{-1},', 'd', '{}'),
        ('L(s, χ·|·|<sup>it</sup>) = L(s + it, χ)', r'L\bigl(s,\chi\cdot|{\cdot}|^{it}\bigr) = L(s+it,\chi)', 'i', '{}'),
        ('<b>ζ<sub>K</sub>(1 + it) ≠ 0</b>', r'\zeta_K(1+it)\neq 0', 'i', '<b>{}</b>'),
        ('ζ<sub>K</sub>(s + it)', r'\zeta_K(s+it)', 'i', '{}'),
        ('<b>L(1 + it, χ) ≠ 0 for every real t</b>', r'L(1+it,\chi)\neq 0', 'i', '<b>{} for every real t</b>'),
        ('L(s, χ) = q<sup>−s</sup> Σ<sub>a</sub> χ(a) ζ(s, a/q)', r'L(s,\chi) = q^{-s}\sum_{a}\chi(a)\,\zeta(s,a/q)', 'i', '{}'),
        ('L(1, χ) = 2πh/(w√q)', r'L(1,\chi) = 2\pi h/(w\sqrt{q})', 'i', '{}'),
        ('L(1, χ) = −(1/q) Σ χ(a) ψ(a/q)', r'L(1,\chi) = -\tfrac1q\sum_{a}\chi(a)\,\psi(a/q)', 'i', '{}'),
        ('|·|<sup>it</sup>', r'|{\cdot}|^{it}', 'i*', '{}'),
    ],
}


def render(sources, inline):
    if not JAR or not os.path.exists(JAR):
        sys.exit('REFUSING: set LATTEX_JAR to a LatteX jar')
    args = ['java', '-jar', JAR, '--batch'] + (['--inline'] if inline else [])
    proc = subprocess.run(args, input='\n'.join(sources) + '\n', capture_output=True, text=True)
    recs = proc.stdout.split('\0')
    if recs and recs[-1].strip() == '':
        recs.pop()
    if len(recs) != len(sources):
        sys.exit(f'REFUSING: LatteX returned {len(recs)} records for {len(sources)} formulas: {proc.stderr[:300]}')
    return dict(zip(sources, recs))


def place(svg, display):
    m = re.search(r'viewBox="([-0-9.]+) ([-0-9.]+) ([-0-9.]+) ([-0-9.]+)" width="[-0-9.]+" height="[-0-9.]+"', svg)
    x, y, w, h = (float(v) for v in m.groups())
    k = 1.1 if display else 1.0
    size = f'width:{k * w / EM:.3f}em;height:{k * h / EM:.3f}em;vertical-align:{-k * (h + y) / EM:.3f}em'
    if display:
        size = f'width:{k * w / EM:.3f}em;height:auto'
    svg = svg[:m.start()] + f'viewBox="{m.group(1)} {m.group(2)} {m.group(3)} {m.group(4)}" class="tex" style="{size}"' + svg[m.end():]
    return svg.strip()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    report = '--report' in sys.argv
    problems = []
    for rel in args:
        specs = SPECS[rel]
        path = os.path.join(ROOT, rel)
        page = open(path, encoding='utf-8').read()
        cut = page.find('<script')
        body, rest = page[:cut], page[cut:]
        inl = render([s[1] for s in specs if s[2].startswith('i')], True)
        dis = render([s[1] for s in specs if not s[2].startswith('i')], False)
        for snippet, tex, mode, template in specs:
            rec = (inl if mode.startswith('i') else dis)[tex]
            if rec.startswith('lattex: error') or '<svg' not in rec:
                problems.append(f'{rel}: LatteX error on {tex!r}: {rec.strip()[:200]}')
                continue
            if BOX in rec:
                problems.append(f'{rel}: LatteX drew a boxed question mark in {tex!r}')
            n = body.count(snippet)
            if n == 0 or (n > 1 and not mode.endswith('*')):
                problems.append(f'{rel}: snippet found {n} times: {snippet!r}')
                continue
            svg = place(rec[rec.find('<svg'):], not mode.startswith('i'))
            if mode.startswith('d'):
                svg = f'<span class="texd">{svg}</span>'
            elif mode.startswith('D'):
                svg = f'<div class="texd">{svg}</div>'
            body = body.replace(snippet, template.replace('{}', svg))
            if report:
                print(f'  ok  {rel}  {mode}  {tex}')
        body = body.replace('</style>', STYLE + '</style>', 1)
        if not report and not problems:
            open(path, 'w', encoding='utf-8').write(body + rest)
            print(f'{rel}: {len(specs)} formulas set by LatteX')
    if problems:
        print('PROBLEMS:\n  ' + '\n  '.join(problems))
        sys.exit(1 if not report else 0)


if __name__ == '__main__':
    main()
