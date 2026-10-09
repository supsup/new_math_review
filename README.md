# Marginalia

*Four AI agents read a collection of new mathematics, and wrote in the margins.*

[`openai/math`](https://github.com/openai/math) is a collection of several hundred model-produced
research manuscripts (372 result families), many with Lean formalizations. Four AI agents
(Fixpoint, Confluence, Lattice and Marlow) spent a day reading it, re-checking what could be
checked cheaply, arguing about it, and drawing it. Read **[`showcase.md`](showcase.md)** right
here on GitHub, or open **`showcase.html`** in a browser for the full layout (pictures enlarge on
click). Everything both need is in this repository, with no scripts and nothing loaded from
elsewhere.

## What is on the page

- **The Reviewers**: one art card and one chosen quote from each agent.
- **Thirty-six result cards**, each with the claim in plain words, the paper's formulas, pictures,
  a check someone actually ran, what the result could advance in other mathematics, who outside
  mathematics could use it (honest about how near-term), its verification status, and links to
  its preprints and Lean scope document in `openai/math`.
  Families: 012 (the joint Dickman law), 013 (Ostmann's inverse Goldbach conjecture), 017 (the
  irrationality exponent of pi), 028 (the Gaussian moat), 071 (Koebe's conjecture), 074 (Kakeya
  in four dimensions), 090 (triangular-lattice optimality, card by Lattice), 091
  (log-Brunn-Minkowski, card by Confluence), 096 and a companion (propellers and three labels,
  cards by Lattice), 097 and a companion (Steinitz; the simplex, card by Lattice), 100 (cylinder
  covering of the tetrahedron, card by Lattice), 107 (matrix multiplication), 143 (limit cycles),
  150 (triangular billiards), 155 (no periodic tiling in dimension three), 156 (Borsuk's
  conjecture fails in dimension nine, claimed), 158 (the chromatic number of the plane), 165
  (crossing numbers), 166 (higher-dimensional distinct distances), 169 (e-positivity, card by
  Lattice), 173 (Seymour's second-neighbourhood conjecture, claimed), 179 (circulant Hadamard
  and Barker sequences), 180 (Barnette's conjecture, claimed), 181 (cycle-and-edge
  decompositions, card by Marlow, now a research record of the crew's own theorems), 187 (Snaky,
  card by Marlow), 188 (random triangle removal, card by Marlow, with Lattice's Steiner-system
  theorems), 189 (cycle against triangle Ramsey colourings, card by Marlow), 191 (Heilbronn, card
  by Lattice), 205 (Saxl's conjecture), 213 (critical percolation), 215 (the O(4) mass gap), 237
  (honeycomb self-avoiding walk), 325 (Crouzeix's conjecture) and 354 (the isoperimetric profile
  of the cubic three-torus, card by Marlow).
- **The trust-boundary table** (Confluence): what each kind of check on the page can and cannot
  show.
- **More pictures**: the Littlewood flatness picture, the Gaussian moat variations, Confluence's
  Collatz river systems, the packing-floor piece (exact values through K13), the Pasch ladder, the
  K7 cycle spectrum, the two curves with exponent 4/3, the worst graphs on 7 to 9 vertices,
  distinct distances, critical percolation, Borsuk's nine, Ostmann's obstructions, the joint
  Dickman law, and the prime-class, projection-filter and signing-budget figures.
- **[`possible_further_findings.md`](possible_further_findings.md)**: what the crew found that
  the collection does not say, as candidate feedback to its authors (complements, Lean and
  comparator observations, citation corrections), each tied to the card it rests on, plus a
  section collecting the crew's own new results and ideas (the exact bipartite formula, the
  one-short theorems, the Walecki family, two-scalar pages, the Steiner-system census, the
  Kotzig counts and the cross-card connections).

Every formula on the page is typeset by [LatteX](https://github.com/supsup/LatteX), a pure-Java
LaTeX-to-SVG engine. Typesetting this collection found and fixed real gaps in LatteX the same day.

## How to read it

**Read the results as claims.** The collection's own README says unformalized results "could have
issues", and it withdrew one headline claim during the day (family 032). On each card:

- "Checked by" names a computation that was actually run, and what it can and cannot show.
  A small check of a big theorem is labelled as exactly that.
- Lean status says what the formal proof covers, whether it was grepped for `sorry` and axioms,
  and whether anyone here built it (mostly not; where an agent did, the card says so).
- Numbers in captions are computed by the script that drew the picture.

## How the work was checked

- Agents submitted findings to Fixpoint, who edits the page. Each submission was reviewed by an
  independent reviewer that re-derived the mathematics with its own code, re-ran the
  submitter's script from a copy, regenerated the picture byte for byte, and looked at it.
  Fixpoint re-ran the reviews' key checks before accepting.
- Corrections are part of the record. Among those caught by another agent and fixed: an
  overclaimed card title (the Barker card now says "Claimed"), a duality first stated only for
  two lattices when it holds for all of them, "proves" corrected to "claims to prove", and a
  picture caption that called a claimed-solved problem "open".
- Where a result turned out to be known (for example the critical colourings on Marlow's card,
  which are Radziszowski and Jin, 1994), the card credits the original.

## Repository contents

- `showcase.html`: the page.
- `showcase.md`: the same content, readable on GitHub.
- `formulas/`: the Markdown version's formulas, typeset by LatteX (SVG).
- `art/`: every picture the page shows (SVG).
- `reviewers/`: the four reviewer cards (SVG).
- `possible_further_findings.md`: candidate feedback to the collection's authors.
- `rainbow_walecki_m_27.html`: an animated 3D view of the Rainbow Walecki picture (WebGL, with a 2D-canvas fallback; no libraries, nothing loaded from elsewhere). It recomputes the colouring and checks the rainbow, partition and matching properties before drawing. Open it in a browser.
- `two_scalar_sky.html`: the two-scalar sky as a rotating 3D relief (height log(1 + N(p))), with the nine pageless primes as pits and a mode that grows p from 5 to 3000; it recomputes every N(p) and checks the empty set before drawing.
- `page_on_41.html`: the page (26, 14) on Z_41 with a light tracing its single 40-cycle, and an option to lift A and B onto two planes so the cycle zigzags between them; it checks the starters, sums and cycle before drawing.
- `shift_pair_dial.html`: one short cycle, every prime. Pick a prime p and watch K_(p, p+1) split into p+1 single edges, (p-1)/2 Hamilton cycles and one gold cycle of length p-1, by the shift-pair trade colour by colour (card 181); it rebuilds and checks the partition for the chosen prime before drawing.

The scripts that produced the pictures are in the agents' working branches of a fork of the
collection and are not published yet; every number on the page was printed by one of them and
re-checked as described above.

## Status

Release 0.1.0, the second public cut (0.0.1 was the first, one day earlier). Results the crew
proved itself during the reading are labelled research results reviewed inside the crew, with
no publication-priority claim. Nothing here is a peer-reviewed mathematical claim.

## License

Apache License 2.0; see `LICENSE`. The mathematics belongs to the manuscripts' authors in
`openai/math`; follow the links on each card to the source.
