#!/usr/bin/env python3
"""lattex_probe_chars.py CENSUS.json LATTEX.jar OUT.json: for every non-ASCII character the showcase uses, ask LatteX to set
(a) the character itself, typed raw, and (b) the usual LaTeX spelling of it. A test passes if LatteX returns an SVG and
the SVG has more ink than the same expression without the character (so a silently dropped character is caught; the
two spaces and the combining macron are exempt, since they add no separate mark). A character drawn as the
missing-glyph box passes here: tools/lattex_missing_glyphs.py is the test for that. Three of the spellings below,
mapsup, ding and dottedcircle, are not standard LaTeX (unicode-math and pifont); refusing those is not a gap."""
import json, subprocess, sys, re
census, jar, outp = sys.argv[1:4]
CMD = {
 '−': r'a - b', '≤': r'a \le b', '→': r'a \to b', '√': r'\sqrt{x}', '∀': r'\forall x', '×': r'a \times b', '←': r'a \leftarrow b', '≥': r'a \ge b',
 '≠': r'a \ne b', '∈': r'a \in b', '∧': r'a \wedge b', '∑': r'\sum_{i=1}^{n} a', '±': r'a \pm b', '∃': r'\exists x', '⁻': r'x^{-}', '≈': r'a \approx b',
 '≡': r'a \equiv b', '⊓': r'a \sqcap b', '↑': r'a \uparrow b', '∏': r'\prod_{i=1}^{n} a', '∞': r'\infty', '∨': r'a \vee b', '⋅': r'a \cdot b', '∪': r'a \cup b',
 '↔': r'a \leftrightarrow b', '∉': r'a \notin b', '∣': r'a \mid b', '↦': r'a \mapsto b', '⟹': r'a \Longrightarrow b', '₋': r'x_{-}', '∫': r'\int_0^1 f', '⋯': r'a \cdots b',
 '¬': r'\neg a', '₊': r'x_{+}', '≃': r'a \simeq b', '÷': r'a \div b', '∘': r'a \circ b', '⁺': r'x^{+}', '⊂': r'a \subset b', '⊢': r'a \vdash b', '∅': r'\emptyset',
 '∖': r'a \setminus b', '∂': r'\partial x', '⊔': r'a \sqcup b', '⊥': r'a \perp b', '≪': r'a \ll b', '⊤': r'\top', '⊆': r'a \subseteq b', '⊗': r'a \otimes b',
 '∩': r'a \cap b', '⟺': r'a \Longleftrightarrow b', '∼': r'a \sim b', '⊕': r'a \oplus b', '∄': r'\nexists x', '⇒': r'a \Rightarrow b', '≅': r'a \cong b',
 '↛': r'a \nrightarrow b', '≫': r'a \gg b', '↓': r'a \downarrow b',
 'ε': r'\varepsilon', 'χ': r'\chi', 'σ': r'\sigma', 'λ': r'\lambda', 'ρ': r'\rho', 'ζ': r'\zeta', 'π': r'\pi', 'ℓ': r'\ell', 'θ': r'\theta', 'τ': r'\tau', 'ψ': r'\psi',
 'δ': r'\delta', 'γ': r'\gamma', 'φ': r'\varphi', 'μ': r'\mu', 'η': r'\eta', 'α': r'\alpha', 'κ': r'\kappa', 'β': r'\beta', 'ι': r'\iota', 'ξ': r'\xi', 'ω': r'\omega',
 'ν': r'\nu', '𝔞': r'\mathfrak{a}', '𝔟': r'\mathfrak{b}', 'µ': r'\mu',
 'ö': r'\text{\"o}', 'é': r"\text{\'e}", 'ő': r'\text{\H{o}}', 'ü': r'\text{\"u}', 'ć': r"\text{\'c}", 'ă': r'\text{\u{a}}', 'ş': r'\text{\c{s}}', 'ó': r"\text{\'o}",
 'á': r"\text{\'a}", 'č': r'\text{\v{c}}', 'Ž': r'\text{\v{Z}}',
 'ℝ': r'\mathbb{R}', 'ℂ': r'\mathbb{C}', 'ℕ': r'\mathbb{N}', 'Ω': r'\Omega', 'ℚ': r'\mathbb{Q}', 'ℤ': r'\mathbb{Z}', 'Φ': r'\Phi', 'Σ': r'\Sigma', '𝒞': r'\mathcal{C}',
 'Δ': r'\Delta', 'Λ': r'\Lambda', '𝓞': r'\mathcal{O}', 'Γ': r'\Gamma', '𝔽': r'\mathbb{F}', '𝒜': r'\mathcal{A}', '𝖳': r'\mathsf{T}', 'ℙ': r'\mathbb{P}', 'Π': r'\Pi',
 'Θ': r'\Theta', '𝔼': r'\mathbb{E}', '𝒫': r'\mathcal{P}', 'Ψ': r'\Psi', '𝓝': r'\mathcal{N}',
 '°': r'90^\circ', '✓': r'\checkmark', '↥': r'a \mapsup b', '✗': r'\text{\ding{55}}', '⇑': r'a \Uparrow b', '▸': r'\blacktriangleright', '↻': r'\circlearrowright',
 '△': r'\triangle', '◀': r'\blacktriangleleft', '▶': r'\blacktriangleright', '◌': r'\dottedcircle', '◇': r'\diamond', '↗': r'a \nearrow b', '↪': r'a \hookrightarrow b',
 '²': r'x^{2}', '₂': r'x_{2}', '₀': r'x_{0}', '₁': r'x_{1}', '¹': r'x^{1}', '³': r'x^{3}', '½': r'\tfrac{1}{2}', '₃': r'x_{3}', '⁴': r'x^{4}', '⁰': r'x^{0}', '⁶': r'x^{6}',
 '⁷': r'x^{7}', '₉': r'x_{9}', '⁸': r'x^{8}', '¼': r'\tfrac{1}{4}', '₄': r'x_{4}', '⁵': r'x^{5}', '¾': r'\tfrac{3}{4}', '₅': r'x_{5}', '₆': r'x_{6}', '⁹': r'x^{9}',
 '₈': r'x_{8}', '₇': r'x_{7}', '⅞': r'\tfrac{7}{8}', '⅓': r'\tfrac{1}{3}', '⅙': r'\tfrac{1}{6}', '⅛': r'\tfrac{1}{8}',
 'ᵢ': r'x_{i}', 'ⱼ': r'x_{j}', 'ᵀ': r'A^{T}', 'ˣ': r'K^{\times}', 'ⁿ': r'x^{n}', 'ᵥ': r'x_{v}', 'ₐ': r'x_{a}', 'ₗ': r'x_{l}', 'ₙ': r'x_{n}', 'ₘ': r'x_{m}', 'ʳ': r'x^{r}',
 'ᵃ': r'x^{a}', 'ᵉ': r'x^{e}', 'ᵤ': r'x_{u}', '̄': r'\bar{x}',
 '·': r'a \cdot b', '…': r'a, \ldots, b', '‖': r'\|x\|', '′': r"f'", '§': r'\S', '•': r'\bullet',
 '–': r'\text{a--b}', '—': r'\text{a---b}', '‑': r'\text{a-b}', '⟨': r'\langle x \rangle', '⌊': r'\lfloor x \rfloor', '⟮': r'\lgroup x \rgroup', '⌈': r'\lceil x \rceil',
 '⟩': r'\langle x \rangle', '⌋': r'\lfloor x \rfloor', '⟯': r'\lgroup x \rgroup', '⌉': r'\lceil x \rceil', '“': r"\text{``a''}", '’': r"\text{a's}", '”': r"\text{``a''}",
 ' ': r'a\,b', ' ': r'a~b', '𝟏': r'\mathbf{1}',
}
rows = json.load(open(census, encoding='utf-8'))['rows']
missing = [r['ch'] for r in rows if r['ch'] not in CMD]
if missing: sys.exit('no LaTeX spelling listed for: ' + ' '.join('%s(U+%04X)' % (c, ord(c)) for c in missing))
def raw_expr(ch):
    if ch == '̄': return 'x̄'
    return 'a ' + ch + ' b'
tests = []
for r in rows:
    ch = r['ch']; tests.append(('raw', ch, raw_expr(ch))); tests.append(('cmd', ch, CMD[ch]))
base = 'a b'
proc = subprocess.run(['java', '-jar', jar, '--batch'], input='\n'.join([base] + [t[2] for t in tests]) + '\n', capture_output=True, text=True)
recs = proc.stdout.split('\0')
if recs and recs[-1].strip() == '': recs.pop()
if len(recs) != len(tests) + 1: sys.exit('LatteX returned %d records for %d expressions: %s' % (len(recs), len(tests) + 1, proc.stderr[:300]))
def ink(svg): return len(re.findall(r'<(?:path|rect|line|circle|polygon|use)\b', svg))
base_ink = ink(recs[0]); out = {}
for (kind, ch, expr), rec in zip(tests, recs[1:]):
    rec = rec.strip()
    if '<svg' not in rec: res = {'ok': False, 'why': rec[:200]}
    else:
        n = ink(rec); res = {'ok': True, 'ink': n}
        if kind == 'raw' and n <= base_ink and ord(ch) not in (0x2009, 0xA0, 0x304): res = {'ok': False, 'why': 'SILENT: an SVG came back with no more ink than "a b" (%d marks)' % n}
    out.setdefault(ch, {})[kind] = dict(res, expr=expr)
json.dump({'jar': jar.split('/')[-1], 'base_ink': base_ink, 'results': out}, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
both = [c for c in out if not out[c]['raw']['ok'] and not out[c]['cmd']['ok']]
rawonly = [c for c in out if not out[c]['raw']['ok'] and out[c]['cmd']['ok']]
cmdonly = [c for c in out if out[c]['raw']['ok'] and not out[c]['cmd']['ok']]
print('characters:', len(out), '; set both ways:', sum(1 for c in out if out[c]['raw']['ok'] and out[c]['cmd']['ok']))
print('NEITHER way (%d):' % len(both), ' '.join(both))
print('command only, raw character refused or dropped (%d):' % len(rawonly), ' '.join(rawonly))
print('raw only, command refused (%d):' % len(cmdonly), ' '.join(cmdonly))
