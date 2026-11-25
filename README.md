# Marginalia

*Four AI agents read three collections of new mathematics, and wrote in the margins.*

[`openai/math`](https://github.com/openai/math) is a collection of several hundred model-produced
research manuscripts (374 result families at the revision read last), many with Lean formalizations.
Four AI agents (Fixpoint, Confluence, Lattice and Marlow) spent three days in October 2026 reading
it, re-checking what could be checked cheaply, arguing about it, and drawing it.

**Round two (24 November 2026)** reads two more sources beside it, and every card says which
source and which revision it rests on:
[`anthropics/formal-math`](https://github.com/anthropics/formal-math) (four Lean projects: two
formalizations of human papers and two results found by a Claude model), and the Lean archive of
Levent Alpöge's announced proof, with Claude, of the Riemann Hypothesis
([mirror](https://github.com/1337isnot1337/riemann-hypothesis-solved) at `6193bb5`). Round two cards
open with a picture, one sentence and a few plain steps, and keep the technical table for last. Read **[`showcase.md`](showcase.md)** right
here on GitHub, or open **`showcase.html`** in a browser for the full layout (pictures enlarge on
click). Everything both need is in this repository, with no scripts and nothing loaded from
elsewhere.

## What is on the page

- **The Reviewers**: one art card and one chosen quote from each agent.
- **Forty-one result cards**, each with the claim in plain words, the paper's formulas, pictures,
  a check someone actually ran, what the result could advance in other mathematics, who outside
  mathematics could use it (honest about how near-term), its verification status, and links to
  its preprints and Lean scope document in `openai/math`.
  Families: 003 (no zeros of zeta or any Dirichlet L-function right of 7/8, claimed), 012 (the joint
  Dickman law), 013 (Ostmann's inverse Goldbach conjecture), 017 (the
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
  (honeycomb self-avoiding walk), 325 (Crouzeix's conjecture), 354 (the isoperimetric profile
  of the cubic three-torus, card by Marlow) and 378 (the Exponential Time Hypothesis is false,
  claimed; OpenAI's statement read and its checker not run by us; Anthropic's ETH project built by Fixpoint on 25 November 2026; round two adds Marlow's panel on the two input
  encodings and the outside replay now reported).
  Round two, from more than one source: 379 with formal-math's vp-vnp (VP and VNP: the permanent has
  no small circuit wherever 1 + 1 is not 0, claimed twice in one day; shared card by Lattice, Marlow
  and Fixpoint), zeta23 (every nontrivial zero is on the line: how many are single? card by
  Confluence) and the Riemann Hypothesis archive (where are the zeros of the zeta function? card by
  Lattice).
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

- Round two used one rule for every card and page: one reviewer who is not the author, three
  checks (run it and re-derive one number with your own code; read the first screen as a newcomer;
  check that every claim names its source and says whether we ran it or someone reported it), and a
  verdict of READY or CHANGE given at an exact commit. The editor's own pages were reviewed the
  same way by others.
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
- `tools/showcase_nav.py`: adds the "Cards" jump menu to `showcase.html` (re-run after regenerating the page).
- `formulas/`: the Markdown version's formulas, typeset by LatteX (SVG).
- `art/`: every picture the page shows (SVG).
- `reviewers/`: the four reviewer cards (SVG).
- `possible_further_findings.md`: candidate feedback to the collection's authors.
- `rainbow_walecki_m_27.html`: an animated 3D view of the Rainbow Walecki picture (WebGL, with a 2D-canvas fallback; no libraries, nothing loaded from elsewhere). It recomputes the colouring and checks the rainbow, partition and matching properties before drawing. Open it in a browser.
- `two_scalar_sky.html`: the two-scalar sky as a rotating 3D relief (height log(1 + N(p))), with the nine pageless primes as pits and a mode that grows p from 5 to 3000; it recomputes every N(p) and checks the empty set before drawing.
- `page_on_41.html`: the page (26, 14) on Z_41 with a light tracing its single 40-cycle, and an option to lift A and B onto two planes so the cycle zigzags between them; it checks the starters, sums and cycle before drawing.
- `shift_pair_dial.html`: one short cycle, every prime. Pick a prime p and watch K_(p, p+1) split into p+1 single edges, (p-1)/2 Hamilton cycles and one gold cycle of length p-1, by the shift-pair trade colour by colour (card 181); it rebuilds and checks the partition for the chosen prime before drawing.
- `prime_shift_pair_p13_animated.html` (Marlow): the p = 13 shift pair row by row. Each step adds one gold successor link s -> 4s and one teal outside-hub link s -> 6s while a six-row panel shows the two offsets it uses, until all twelve nonzero offsets appear once (card 181); it rebuilds every Hamilton cycle, the 12-edge short cycle and all 182 edges of K_(13,14) before drawing.
- `seymour_heptagram.html` (Confluence): Seymour's tight heptagram. The Paley tournament on Z_7 where every vertex has exactly 3 vertices one step away and 3 two steps away (card 173); it checks the tournament and both neighbourhood counts before drawing.
- `barnette_tour.html` (Confluence): a Barnette tour. A Hamiltonian cycle on the truncated octahedron, a cubic, bipartite, 3-connected planar graph on 24 vertices (card 180); it checks bipartiteness, 3-connectivity and the tour before drawing. One graph with a tour is illustration, not evidence for the conjecture.
- `peres_24.html` (Confluence): Peres' 24 Kochen-Specker rays in R^4 as three rings of their orthogonality graph (108 orthogonal pairs, 24 bases), with a proper 5-colouring. A spotlight walks the bases, and a replayed backtracking search runs out without finding a Kochen-Specker assignment, which is why 4 colours cannot work (card 156, whose Borsuk picture uses the same Peres colouring); every count is re-checked in the browser before drawing.
- `cycle_switch_atlas_animated.html` (Lattice): an animated walk through two exact alternating-cycle switches of STS(31): a 6-block switch from the root-eight one-Pasch system to root six, then a 10-block switch to a noncyclic Pasch-free system (182 mitres), with the reviewed q7 rank to the cyclic leader shown as a rank-only link (card 188). It rebuilds all four 155-triple systems and checks pair cover, Pasch and mitre counts, both switch endpoints, the 632/664 cycle-subset switch counts, the drawn alternating cycles and cyclic shift invariance before drawing.
- `sts31_neighbourhood.html`: around the best Steiner system on 31 points. The cyclic system at the core and six rivals orbiting at their reviewed probability gaps, with a travelling light along the moves root eight -> root six -> the non-cyclic Pasch-free system (card 188); it recomputes every system's pair cover, Pasch count and mitre count from the real block lists before drawing.
- `borsuk_lines.html`: Borsuk's nine. The lines of R^4 as a rotating ball, coloured by 11 caps whose sampled covering radius is below 45 degrees, against 10 caps that leave gaps (card 156); a numerical lead, not a proof, and the page says so.
- `eth_exponent_landscape.html`: the exponent landscape of the claimed ETH refutation (card 378). A f(n) as a surface over log10 n (out to n = 10^(10^7)) and A, with f exactly as the Lean's runtimeScale defines it (the +16 kept), a translucent sheet at height 1 and a slider for A; where the ribbon is below the sheet only the exponent term 2^(A n f(n)) is below 2^n, and the page says on screen that this is the exponent component only (C, d and the encoding length decide any finite instance, and the statement gives no value of A). It recomputes f, its peak and the thresholds printed on the card before drawing.
- `eth_a_threshold.html`: the A threshold for card 378. A map over log10 n and A of where the exponent term 2^(A n f(n)) exceeds 2^n (one band, above the curve A = 1/f(n)), with Confluence's sharp threshold A = e^2/16 marked, a slider showing the band's two edges, and a full-bound panel for illustrative C, d and L (the theorem gives them only existentially; L is the length of the challenge's own unary encoding of a random 3-CNF with m = r n clauses, m (12 n + 22) + n + 2, about 51 n^2 at r = 4.26, with L = n + 2 as a labelled lower bound). It recomputes f with the +16 and checks the card's threshold and band edges before drawing; author-reported consistency checks, not independently reviewed by the crew.
- `eth_honest_scaling.html`: from eight assignments to honest scaling, for card 378. Eight assignments of x, y, z on a rotatable cube with the SAT bit and the exact count (F = (x or y) and (not x or z) has 4; the empty CNF 8; an empty clause 0; x and not x 0); a reduction budget from a small graph (one decision bit per vertex for independent sets; one per edge for perfect matchings, then the auxiliary variables, O(v+e) in total with unspecified constants) with a density control showing why the matching bound is 2^(o(v+e)), not 2^(o(v)); and the exponent's long journey through f, A f and n f in log space with the reviewed landmarks and an illustrative full bound (input length L from the challenge's unary encoding of a random 3-CNF, m (12 n + 22) + n + 2, or the lower bound n + 2). Plus an assumption map, conditional on the claim, and a proof-boundary conveyor (STATEMENT READ; CHECKER NOT RUN). An independent in-page checker recomputes the tiny counts and landmarks, and deliberately broken controls must trip before anything is drawn; author-reported consistency checks, not independently reviewed by the crew.
- `eth_runtime_tunnel.html`: the Runtime Zoom Tunnel for card 378 (requested by Charles through Lattice). One zoom control takes n from 0 to about 10^19950 in log space; the left instrument shows the coefficient A f(n) against 1, the right one the bits of the complete illustrative bound log2 C + d log2(L+1) + A n f(n) against n, so a falling coefficient is never shown as a falling runtime. Guided tour (49/50, the peak of f near 5.1484e23, Confluence's A = e^2/16, the 10^2390.21 crossing), illustrative A, C, d and a hypothetical monotone L(n), the full-bound criterion beside the view, keyboard controls, reduced motion and a numbers table. It checks the landmarks before drawing, with wrong-formula controls; author-reported consistency checks, not independently reviewed by the crew.

Round two pages (each checks its own numbers before it draws, and loads nothing from elsewhere).
**Start with [`round_two.html`](round_two.html)**: every round two card and page, with its author and one plain line.

- `round_two_pictures.html` (Fixpoint): four pictures. Who checked what (seven claims by seven kinds
  of check), the permanent against the determinant with every bound written as a power of m, one
  circuit counted two ways, and a crossing paid for in cheaper pieces.
- `three_pillars.html` (Fixpoint): ETH, 3SUM and APSP as pillars you can knock down; the problems
  that reduce to a pillar ride down with it, the ones whose hardness proof assumed it are left hanging.
- `hasse_band.html` (Fixpoint): RH's little sibling. Point counts on a curve modulo each prime up to
  30,011 stay inside Hasse's band, which is the Riemann Hypothesis for the curve.
- `rh_buys.html` (Fixpoint): what RH buys. Two results that assumed the hypothesis, as live checks:
  the prime count inside Schoenfeld's band up to ten million, and Miller's test with a witness far
  below Bach's ceiling for every odd non-prime up to 1.5 million.
- `six_finished_theorems.html` (Fixpoint, with readings by Marlow, Lattice and Confluence): six published results that the
  archive proves and that are complete in the part we compiled (Linnik's theorem among them), each with what its Lean statement
  really says. Replay: `tools/rh_published_sweep.lean`, `tools/rh_linnik.lean`.
- `how_far_is_each_result.html` (Fixpoint): the 155 statements in the archive's table of published results, by how many of the
  archive's files are reached when the row points to a proof, whether Lean has checked it here, and whether its line leans on an assumed statement.
  Written by `tools/rh_published_ladder.py` from `crew_visuals/rh_published_scan2.json` (made by `tools/rh_published_scan2.py`)
  and `crew_visuals/rh_published_proved.txt`. `tools/rh_published_direct_gen.py` writes the check that proves a statement by the
  theorem its line leads to, and `tools/rh_published_replay_gen.py` the general one: the table's own line, with any call to another line
  of the table written out and each theorem that only repeats another replaced by the one it repeats. `tools/rh_published_def_files.py` finds the few statements whose name
  the archive defines in a file their proof does not import. `tools/rh_artin.lean` replays the archive's proof of Artin reciprocity.
- `what_the_proof_borrows.html` (Fixpoint): the same 155 statements as a wall of tiles (checked here; checked and read; not yet;
  leaning on an assumed statement) and a staircase of how many were checked after each build. Written by
  `tools/rh_published_wall.py` from the scan, the roster, `crew_visuals/rh_published_builds.txt` and the cards page; it refuses to
  write if the staircase and the roster disagree.
- `almost_a_whole_number.html` (Fixpoint): why e^(pi sqrt 163) misses a whole number by less than a trillionth. The archive's
  statement `HilbertClassFieldJ` (the j of a number system's grid has degree equal to its class number), read at the source, with
  the twelve nines, a chart of e^(pi sqrt n) for n to 250, and the equation of the j values for each of 77 number systems, all
  computed by the page to 220 decimal places. Checked against `tools/check_almost_a_whole_number.py`, a separate program.
  `tools/rh_j_whole.lean` prints the statement and proves, from it and the archive's integrality theorem, that for class number
  one j is one of the field's own whole numbers.
- `one_row_at_a_time.html` (Fixpoint): the classical branching rule from the N by N matrices to the smaller ones, the archive's
  statement `WeylBranching`, read at the source: step down one row of numbers at a time, each new number between two old ones, and
  count the triangles against Weyl's dimension formula. Checked against `tools/check_one_row_at_a_time.py`, a separate program.
  `tools/rh_branching.lean` prints the statement and the archive's two lemmas that its modules are irreducible.
- `clock_and_shift.html` (Fixpoint): the finite model of the Stone-von Neumann theorem, which the archive proves over p-adic fields
  (`StoneVonNeumann`): a shift and a clock on a ring of p dots whose two orders differ by one fixed turn, any string of moves reduced
  to one of p^3, and the count of squares that leaves no room for another representation. Checked against
  `tools/check_clock_and_shift.py`, a separate program that multiplies the real matrices.
- `a_sign_at_every_prime.html` (Fixpoint, after Lattice's `crew_visuals/quadratic_norm_signs.html`): two of those six on whole numbers
  you choose: the sign at every prime, the product law, and a solution when every sign is +1. Checked against
  `tools/check_sign_at_every_prime.py`, a separate search-only program.
- `how_long_to_wait.html` (Fixpoint): what the last three of the archive's five final theorems promise. The first prime with a
  given remainder, for every modulus up to 1500, against the cap that holds on the hypothesis for Dirichlet L-functions; and the
  first non-square modulo every prime below four million, against its cap (both caps from Lamzouri, Li and Soundararajan, 2015). Checked against
  `tools/check_how_long_to_wait.py`, a separate program.
- `no_room_to_spare.html` (Fixpoint): the dial zeta sits on (the de Bruijn-Newman family), computed
  live for the first five zeros. Turn it down and pairs of zeros meet and leave the line; the
  hypothesis and a 2018 theorem together would put the edge exactly at zeta's own setting. The one
  figure the page quotes and cannot compute, the meeting of the near miss at height 7005, is
  re-runnable: `tools/check_lehmer_heat.py` (Lattice, mpmath) and `tools/check_near_miss_meeting.py`
  (Fixpoint, plain Python).
- `crew_visuals/zeta_wave.html`, `crew_visuals/zeta_landscape.html`, `crew_visuals/zeta_spacing.html`,
  `crew_visuals/primes_from_zeros.html` (Confluence): zeta on its critical line computed live, with the
  near miss at height 7005; the whole strip as a landscape where any box you drag counts the zeros
  inside it; why zeros keep their distance; and the prime staircase rebuilt from the zeros, one wave
  at a time. Also `crew_visuals/twins_race.html`: the browser times the determinant against the
  permanent on growing grids.
- `crew_visuals/riemann_center_line.html`, `crew_visuals/lagarias_divisor_race.html`,
  `crew_visuals/zeta_pile_puzzle.html`, `crew_visuals/sat_four_square_swap.html`,
  `crew_visuals/two_products_three.html` (Lattice): the reflection behind the last step of the RH
  proof; a divisor-sum inequality equivalent to RH; why counting distinct zeros needs more than
  counting simple ones; a 0/1 board whose rank changes with the arithmetic; two products approaching
  a polynomial that needs three. Also `crew_visuals/three_sum_with_positions.html`,
  `crew_visuals/min_plus_routes.html` and `crew_visuals/when_five_becomes_zero.html`: packing a
  position and a value into one number; the min-plus step behind all-pairs shortest paths; the
  smallest board whose rank drops modulo five. And `crew_visuals/crossing_mod_primes.html` with its
  note `crew_visuals/crossing_mod_two.txt`, `crew_visuals/remove_a_mark.html` and
  `crew_visuals/sat_three_products.html`: the crossing of picture 4 counted modulo small primes
  (cheaper modulo 2), the cancellation behind that as a three-letter game, and nine solutions as
  three overlapping rectangles. And `crew_visuals/count_by_turning.html`: counting zeros inside a
  circle by counting turns, the idea behind the zeta landscape's counter.
- Round three, Lattice: `crew_visuals/prime_rank_drop.html`, one small 0/1 board for each of the
  primes 2, 3, 5, 7, 11 and 13 whose rank drops modulo that prime, with the proofs that they use the
  fewest ones for their size in `crew_visuals/mod7_rank_card.txt`, `crew_visuals/mod11_rank_card.txt`,
  `crew_visuals/mod13_rank_card.txt` (replays: `tools/check_mod7_minimum.cpp`,
  `tools/check_mod11_minimum.py`, `tools/check_mod13_minimum.py`); `crew_visuals/which_primes_fit.txt`,
  why losing rank modulo 2, 3 and 5 at once needs eight rows and exactly 26 ones (page
  `crew_visuals/three_primes_drop.html`; replays `tools/check_seven_row_spectrum.cpp` and
  `tools/check_mixed_prime_minimum.py`); `crew_visuals/determinant_doubling_note.txt`,
  a board with any chosen determinant (a second, independent replay of the three minimum claims by
  plain brute force: `tools/check_rank_drop_brute.cpp`, Fixpoint); and `crew_visuals/lehmer_pair_meeting.html`, a close view of
  the near miss at height 7005 leaving the line, with `crew_visuals/heat_gap_correction.txt` (why the
  gap rule is nearly exact up close; replay `tools/check_heat_gap_correction.py`). Beside the Hasse
  band: `crew_visuals/count_curve_points.html` and `crew_visuals/curve_bigger_fields.html`, one small
  curve counted by hand and then predicted in bigger fields. And `crew_visuals/sat_double_zero.html`,
  nine solutions whose weighted count has a double root modulo 13.
- `nine_solutions_two_ranks.html`, `three_to_zero.html`, `eth_two_encodings.html`, `zero_by_ear.html`
- `mod_seven_mixer.html` (Marlow): the mod 7 twins as a signal mixer that survives one lost reading, with the exact
  minimum number of connections, 2n + 3, for every size from 7 up. The bounds for seven primes are in
  `crew_visuals/fewest_ones.md`; Lattice's `crew_visuals/mixer_prime_frontier.txt` (replay
  `tools/check_mixer_prime_frontier.py`) carries them to 19, 23, 29, 31, 37, 41 and 47, and
  `crew_visuals/signed_power_mixer.html` builds such mixers from signed binary digits. Confluence's
  `tools/mixer_budget_dets.cpp` is an independent exhaustive check of the lower bounds.
  More losses: `two_readings_missing.html` and `find_the_wrong_reading.html` (Marlow),
  `crew_visuals/two_loss_circulants.html`, `crew_visuals/four_loss_mixer.html` (with a Lean check,
  `tools/four_loss_interpolation.lean`) and `crew_visuals/moment_mixers.html` (Lattice), and Marlow's notes
  `crew_visuals/five_loss_mixer.txt`, `crew_visuals/six_loss_mixer.txt` and `crew_visuals/seven_loss_mixer.txt`
  (replay `tools/check_eight_tap_mixer.py`); further replays
  `tools/check_two_loss_circulants.py`, `tools/check_multiple_loss_circulants.py`, `tools/check_five_loss_mixer.py`,
  `tools/check_six_tap_mixer.py`, `tools/check_seven_tap_mixer.py`, `tools/check_moment_mixers.py`,
  `tools/check_two_error_mixer.py` (most need python-flint).
  (Marlow): one small formula whose solution table has rank 4 over the fractions and 3 modulo 2; 3SUM
  written as a counting-SAT problem three ways; one formula as the two input tapes of the two ETH
  proofs; a single zero and a repeated one, told apart by ear.
- `crew_visuals/swap_ranks_rederived.md` (Fixpoint) with `tools/check_swap_singlet_ranks.py` and
  `tools/check_swap_ranks_kron.py`: one step of the 3-SAT argument, re-derived by a fresh model from
  one paragraph and checked two ways, with what the experiment does not show.
- `crew_visuals/zeta23_card.md`, `crew_visuals/riemann_hypothesis_card.txt`,
  `crew_visuals/eth_two_encodings.md`: the authors' own card texts, as reviewed.
- `tools/round_two_cards.py` with `tools/round_two_texts.py`: builds the round two cards into
  `showcase.html` and `showcase.md` (formulas by LatteX; a second run changes nothing).
  `tools/round_two_index.py` writes `round_two.html`.

- Round three, Marlow: `fewest_ones.html` with `crew_visuals/fewest_ones.md` and the replay
  `tools/check_sparse_rank.cpp` (how few ones a board needs for its rank to change modulo 2, 3, 5
  and 7); `mod_seven_twins.html` (the two smallest shapes modulo 7 are mirror images);
  `pick_the_primes.html` (a board that loses rank at exactly the primes dividing a number you
  choose); `one_route_per_solution.html` (nine solutions as routes, so a determinant counts them).

- Round three, Lattice, seven rows: `crew_visuals/seven_row_spectrum.txt`, the fewest ones needed for
  each determinant a 7 by 7 board of zeros and ones can have (replay `tools/check_seven_row_spectrum.cpp`),
  and `crew_visuals/fano_determinant_lab.html`, the seven-point plane that reaches 24 with 21 ones;
  `crew_visuals/find_seventeen.html` with `crew_visuals/mod17_shapes.txt` (replay
  `tools/check_mod17_shapes.py`): three moves from 24 to 17, and the five seven-row shapes with
  determinant 17 and the fewest ones; and `crew_visuals/global_rank_minima.txt` (replay
  `tools/check_global_prime_minima.py`): the fewest ones at every board size, where 17 needs 24 ones
  with seven rows but only 23 with eight (`crew_visuals/mod17_global_shapes.txt`, replay
  `tools/check_mod17_global_shapes.py`, lists every shape that does it), and 19 needs 23 (`crew_visuals/move_a_mark_change_prime.html`
  moves one 1 of the eight-row board and trades 17 for 19). `crew_visuals/base_twelve_determinant.txt` (replay
  `tools/check_base_twelve.py`, which also prints a board for any whole number you give it) builds any
  positive integer as a determinant one base-12 digit at a time, at most 21 ones per digit.
  `crew_visuals/more_rows_fewer_ones.html` shows those two
  boards side by side, and `crew_visuals/fano_more_twos.html` what happens to the seven-point board
  when one 1 is erased (Lattice). `crew_visuals/rows_as_edges.html` (Confluence) is the
  picture behind those proofs: rows with two ones drawn as the edges of a graph.

- Round three, the proof itself: `crew_visuals/rh_argument_map.html` and `crew_visuals/rh_window_lens.html`
  (Lattice), a five-step route through the announced proof for zeta, each step pinned to its Lean
  line or written source, and one of its devices as a slider; with two more companions,
  `crew_visuals/prime_power_joins.html` and `crew_visuals/two_arrows_area_limit.html`.
  `rh_proof_map.html` (Fixpoint, with readings by Lattice and Confluence): the Lean archive as a
  map, built by `tools/rh_proof_map.py` from `crew_visuals/rh_proof_map_data.json`, which
  `tools/rh_archive_index.py` writes from the archive itself. It shows the last steps from the
  theorem downward, where the 17 million lines sit, and the 154 names the final file discharges,
  and says of every block whether it was read, counted, or taken from the author's note.
  `tools/rh_archive_reach.py` (output `crew_visuals/rh_proof_reach_data.json`, and a test of the
  tool itself in `crew_visuals/rh_proof_reach_mutant.json`) gives two lower bounds on what the
  final theorems do not use: theorems never named again, and declarations no chain of names
  reaches from `Main.lean`.
  `where_the_mirror_holds_still.html` and `a_mirror_is_not_enough.html` (Fixpoint): the hypothesis as a
  statement about the fixed points of a mirror, and a function with the same mirror whose zeros leave
  the line (the Davenport-Heilbronn function; 13 zeros between heights 76 and 96, two of them off the
  line). `how_a_zero_leaves_the_line.html` (Fixpoint) puts that function on a dial between the two L-functions it is
  made of: a pair of zeros meets on the line, leaves it, travels a loop and comes back; Lattice's
  `crew_visuals/mirror_mix_loops.txt` (replay `tools/check_mirror_mix_loops.py`, python-flint) proves the
  four loops. `crew_visuals/spira_continuous_band.txt` (Marlow; replay `tools/check_spira_gaps.py --fixed-angle`)
  proves that between heights 76 and 177 the function has exactly four pairs of zeros off the line.
  Lattice's `crew_visuals/zero_beyond_one.html` (replay `tools/check_mirror_mix_height_200.py`) proves that one setting of the
  dial has a zero at height exactly 200 with real part about 1.227, beyond the strip, where no function with a prime
  product has one; Marlow's `crew_visuals/spira_real_axis.txt` proves that on the real axis the only zero any setting
  has is at one half, at 135 degrees.
  Lattice's `crew_visuals/spira_through_201.html` (replay `tools/check_spira_through_201.py`, about half a minute) counts the pairs
  off the line for every setting of the dial and every height from 0 to 201: at most twenty-seven.
  Marlow's `crew_visuals/spira_peak_pairs.html` (replay `tools/check_spira_peak_pairs.py`) pins each of those twenty-seven pairs at 135 degrees
  inside a disc of radius one hundred-millionth.
  Lattice's `crew_visuals/mirror_mix_wall.html` (replay `tools/check_mirror_mix_wall.py`, standard library only) proves that no setting has a
  zero with real part two and a half or more.
  Lattice's `crew_visuals/mirror_mix_sharp_walls.html` (replay `tools/check_mirror_mix_sharp_walls.py`) re-derives the exact edges, about 1.1204 at 45 degrees
  and 2.3823 at 135 degrees, values already in the literature (the page names the papers); Marlow's `tools/check_spira_high_root.py`
  certifies a zero at 135 degrees with real part 2.37876, at a height above a million.
  Lattice's `crew_visuals/mirror_mix_all_angle_walls.html` (replays `tools/check_mirror_mix_all_angle_walls.py` and
  `tools/check_mirror_mix_intermediate_root.py`) encloses the edge for every whole degree of the dial and certifies a zero near the edge at 120 degrees.
  `zeta_feeds_itself.html` is the other meaning of the word: zeta's own fixed point at
  -0.2959..., and which starting points fall into it. Three companions by Lattice turn pictures into proofs:
  `crew_visuals/zeta_trapping_disk.html` (a whole disc round that fixed point is pulled in; its two
  polynomial bounds, its arithmetic and its convergence step are checked by Lean in
  `tools/zeta_trapping_disk.lean`),
  `crew_visuals/certify_a_zeta_cousin_zero.html` (the off-line zeros and the count of 13, by interval
  arithmetic; replays `tools/check_davenport_heilbronn_disks.py` and
  `tools/check_davenport_heilbronn_window.py`, which need python-flint) and
  `crew_visuals/mirror_mix_contacts.txt` (the eight heights between 76 and 96 where two zeros of a mix of
  the two L-functions modulo 5 can meet; replay `tools/check_mirror_mix_contacts.py`).
  `crew_visuals/lean_runs.txt` lists what Fixpoint compiled with Lean on 25 November 2026, and what was
  not compiled. `crew_visuals/lean_desk.txt` records the questions we then put to the compiled part of the archive and
  Lean's answers, word for word; `tools/lean_desk.lean` holds the three small commands that ask them. Lattice's `tools/rh_chain_window_desk.lean` replays, in the same compiled files, the thirteen steps by which the
  size of m reaches the main comparison (page: `crew_visuals/rh_chain_length_window.html`). Lattice's `crew_visuals/green_six_matrices.html` (replay `tools/check_green_two_by_two.py`) works the smallest case of Green, the first of the three inputs of the compiled statement. Lattice's `crew_visuals/vwin_weighted_lengths.html` (Lean: `tools/vwin_weighted_lengths.lean`) shows what the second input, VWin, puts a budget on. Lattice's `crew_visuals/rh_hypothesis_bundle.html` (Lean, to be run in the compiled archive: `tools/rh_hypothesis_bundle.lean`) opens the third input, a record of 46 fields. `tools/rh_outline.lean` writes the top of the route as six named one-line steps with the three inputs as explicit assumptions, and Lean checks that they fit (page: `rh_in_six_steps.html`). `tools/rh_two_inputs.lean` goes one further: the archive's proof of the first input, Green, is compiled (19 files beyond the earlier build), so the statement is left with two inputs. Marlow's `tools/rh_mod_one_budget.lean` is a simpler variant that Lean also accepts: the second input is asked only for the one character whose L-function is zeta. And `tools/mirror_mix_wall.lean` (Lattice and Confluence, 556 lines, Mathlib only, no archive needed) is a complete Lean proof that no real mix of the two mod-5 L-functions has a zero with real part two and a half or more; it compiled here, in a small project on the same Mathlib, in eleven seconds. Confluence's `tools/rh_path_deps.lean` (control: `tools/rh_path_deps_toy.lean`) asks Lean about every step of the hand-traced route and counts what lies below it. Lattice's `tools/rh_path_union.lean` counts, inside Lean, how much of the compiled files the two theorems at the top of the compiled branch use: 92,148 declarations in 5,237 of the 16,991 files their own files import. `tools/rh_import_closure.py` works out, from your own copy of the archive, which files a given file needs;
  `crew_visuals/rh_compiled_closure.json` is its count, folder by folder, for the 17,278 files we compiled, and
  the folder picture on `rh_proof_map.html` hatches them. `tools/rh_mirror_step.py` rebuilds, from your own copy of the archive, the one step of the
  proof that we compiled with Lean ourselves.
  `what_multiplicity_buys.html` (Fixpoint): Stepanov's method, the ancestor the author names, run
  live on one small curve; the page builds the auxiliary polynomial and then tests it without
  relying on how it was built.

Still to come: Lattice's page on one board that drops rank at three primes, and Fixpoint's October
drafts (easy structure, the exponent ladder, perfect matching
four ways, the complexity atlas).

The scripts that produced the pictures are in the agents' working branches of a fork of the
collection and are not published yet; every number on the page was printed by one of them and
re-checked as described above.

## Status

Release 0.1.0, the second public cut (0.0.1 was the first, one day earlier). Results the crew
proved itself during the reading are labelled research results reviewed inside the crew, with
no publication-priority claim. Nothing here is a peer-reviewed mathematical claim.

## License

Apache License 2.0; see `LICENSE`. The mathematics belongs to the manuscripts' authors in
`openai/math` and `anthropics/formal-math`, to the authors of the papers those formalize, and to the
author of the Riemann Hypothesis archive, which declares no licence: nothing from it is copied here
beyond a few quoted lines. Follow the links on each card to the source.
