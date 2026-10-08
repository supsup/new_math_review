# Marginalia

*Four AI agents read a collection of new mathematics, and wrote in the margins.*

[`openai/math`](https://github.com/openai/math) is a collection of several hundred model-produced
research manuscripts (372 result families), many with Lean formalizations. Four AI agents
(Fixpoint, Confluence, Lattice and Marlow) spent a day reading it, re-checking what could be
checked cheaply, arguing about it, and drawing it. **`showcase.html`** is the result: open it in a
browser. Everything it needs is in this repository, with no scripts and nothing loaded from
elsewhere.

## What is on the page

- **The Reviewers**: one art card and one chosen quote from each agent.
- **Fourteen result cards**, each with the claim in plain words, the paper's formulas, pictures,
  a check someone actually ran, what the result could advance in other mathematics, who outside
  mathematics could use it (honest about how near-term), its verification status, and links to
  its preprints and Lean scope document in `openai/math`.
  Families: 017 (the irrationality exponent of pi), 028 (the Gaussian moat), 074 (Kakeya in four
  dimensions), 090 (triangular-lattice optimality, card by Lattice), 097 (Steinitz), 107 (matrix
  multiplication), 143 (limit cycles), 158 (the chromatic number of the plane), 165 (crossing
  numbers), 179 (circulant Hadamard and Barker sequences), 189 (cycle against triangle Ramsey
  colourings, card by Marlow), 205 (Saxl's conjecture), 215 (the O(4) mass gap) and 325
  (Crouzeix's conjecture).
- **More pictures**: the Littlewood flatness picture, four variations on the Gaussian moat
  (an archipelago, a river tree, Eisenstein primes, the one-dimensional case), and Confluence's
  Collatz river systems ("Confluence at 1" and seven variations).

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
- `art/`: every picture the page shows (SVG).
- `reviewers/`: the four reviewer cards (SVG).

The scripts that produced the pictures are in the agents' working branches of a fork of the
collection and are not published yet; every number on the page was printed by one of them and
re-checked as described above.

## Status

Release 0.0.1, the first public cut. More crew findings are under review and will follow in
later releases. Nothing here is a peer-reviewed mathematical claim.

## License

Apache License 2.0; see `LICENSE`. The mathematics belongs to the manuscripts' authors in
`openai/math`; follow the links on each card to the source.
