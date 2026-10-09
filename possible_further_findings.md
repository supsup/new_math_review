# Possible further findings

*What the crew found that the collection does not say. Candidate feedback to the authors and maintainers of [`openai/math`](https://github.com/openai/math); nothing here has been sent yet.*

Every item below rests on a sentence in one of the cards of [`showcase.md`](showcase.md), named by family number, and on what an agent actually read or ran: "checked" means read at source or computed by us; "not reached" means we could not get at the source. The crew's own theorems (the one-short partitions and the Walecki family on card 181, the Steiner-triple-system census on card 188, the two-scalar pages) are not listed; they are research results, not corrections, and live on their cards.

## A. Preprints: imprecisions, no outright errors found

1. **Family 100 (cylinder covering of the tetrahedron).** The displayed cover (epsilon = 1/2000, 16,000,000 cylinders) is sixteen times looser than the paper's own two corollaries allow: tau = 1/500, eta = 1/498 with 1,000,000 cylinders satisfies both jointly, with exact margins 1751/249000000 and 2959/5187500000000. No step of the proof depends on the 16-million parameters. Checked in the TeX (epsilon at most 1/2000 and the 2 epsilon^4 bound).

## B. Lean artifacts, comparator and docs

2. **Family 166 (higher-dimensional distinct distances).** No comparator challenge and no `lean/docs/166.md`, yet `OAI.lean` imports an orphan module (`OAI/Combinatorics/Distances/PolynomialIsolation.lean`, supporting lemmas only). Either a docs page should say the main theorem is not formalized, or the orphan import should go.
3. **Family 237 (honeycomb self-avoiding walk).** `CONTENTS.md` gives the main fixed-length theorem a Lean link, but `docs/237.md` links four companion papers and never the main paper; all four comparators are supporting results. Checked by reading `docs/237.md`.
4. **Families 150 and 143.** The docs titles name the unformalized stronger claim ("weak mixing" for triangular billiards; "uniform bounds for limit cycles") while the scope formalizes only ergodicity, respectively the quintic Lienard bound. `docs/205.md` is the model of how to say this plainly.
5. **Family 100.** `ComparatorChallenges/TriangularCovering.lean` quantifies "there exist delta and C" and the solution proves 14 epsilon^4, while the paper states 2 epsilon^4 for epsilon at most 1/2000. A second comparator pinning the paper's constants, or a scope sentence on the existential ones, would close the gap between what is proved and what is claimed. Checked at `TriangularCovering.lean` lines 52 to 58 and `TriangularCovering/Main.lean` line 19.
6. **Family 191 (Heilbronn).** `CONTENTS.md` says "for every sufficiently large n" with a Lean link; the comparator proves an unbounded sequence of n with a smaller exponent, as `docs/191.md` itself admits. The contents line should match the docs line.
7. **Family 156 (Borsuk in dimension nine).** `Borsuk/Main.lean` derives `euclidean_nine_counterexample`, the headline statement in R^9, but `BorsukNine.json` lists only `main_theorem`, so the stronger statement is not covered by the collection's own gate. Hygiene on the plus side: 145 FiniteCases files, 13,170 `decide` calls and no `native_decide`.
8. **A structural note on the comparator design (families 173, 180 and others).** The challenge file's definitions (`MainStatement`, `PlaneEmbedding`, `ThreeVertexConnected`, `IsOriented`, `secondNeighbors`) are re-declared byte for byte in the solution's `Model.lean` rather than imported, so "statement match" rests on a text diff rather than on the compiler. Our readers diffed the blocks and found them identical, but the design makes that a reader's job.
9. **Positive replication, for the record.** Kernel builds with permitted axioms only and firing sorry controls were done inside the crew for families 158 (70 modules), 091, 180 (8,955 jobs) and 173 (1,872 jobs); statement MATCHES readings were done for 012, 013, 071, 156, 173, 180 and 213, by two independent readers each for 156, 173 and 180. None of these is a rebuild on a second machine outside the crew.

## C. Complements the authors do not state

10. **Family 156.** A numerical cover of the lines of R^4 by caps with a strict angular margin succeeds with eleven caps (covering radius 42.4 degrees, re-measured on two million fresh samples) and fails with ten (46.1 degrees, above the 45 needed), so if the theorem holds the covering number is exactly 11; the preprint says it "does not determine how many pieces X needs". Also the preprint's label bound k(k+1)/2 is sharp at k = 2 (three pieces for RP^1) and k = 3 (six icosahedral caps for RP^2), a sanity check of the method against the known cases.
11. **Family 181 (cycle-and-edge decompositions).** The exact value d(K_{p,t}) = s0 + ceil((pt - s0)/(2 min(p,t))) for every complete bipartite graph (two independent verifiers; the both-even case is Sotteau 1981; whether the closed form is in print is unverified) sharpens the (3/2 - o(1))n complete-bipartite lower bound the preprint cites from BM2024 section 6. The smallest graph needing more than n - 1 pieces is K_3 joined to four independent vertices, on seven vertices. Priority is Marlow's; publication status unverified.
12. **Family 354 (isoperimetric profile of the cubic three-torus).** Exact-arithmetic recomputation of the numerical appendix (24 baseline values, 16 gain bounds, 23 interval comparisons, the Taylor-remainder bounds) with the explicit phase changes at volume 4 pi/81 and 1/pi.
13. **Family 173 (Seymour).** A control that separates the hypotheses: the extremal proposition's concavity inequality fails on every sink-free oriented graph on at most five vertices but holds on the complete symmetric digraph on four or more vertices, so the proposition is false once 2-cycles are allowed and the diagonal-compatibility step is what carries the load. Exhaustive checks of all 14,348,907 oriented graphs on six vertices and all 10,460,353,203 on seven agree with the theorem.
14. **Family 180 (Barnette).** Each hypothesis pinned to the proof step that uses it, and a test set: a non-Hamiltonian cubic bipartite planar graph that is only 2-connected (26 vertices), and Hamiltonian duals of refined Eulerian triangulations on 32, 80 (with ten-sided faces, beyond every face-bounded theorem) and 128 vertices.
15. **Family 169 (e-positivity).** The counting permutations cannot respect the mirror symmetry (for the path P_3, 132 and 213 swap; proved for every path), relevant to the paper's explicit permutation count.
16. **Family 191.** A source-level audit of sections 3, 5, 6, 7 and 8 found no substantive gap; a toy F_7 census (2,968 dependent triples in a cap) motivates the paper's shift. **Family 097:** an explicit sharpness witness (the regular simplex, floor((d+1)^2/4)/d, optimal signings counted to d = 20) where the paper claims only a matching lower bound. **Family 143:** a Poincare map confirms exactly two cycles, amplitudes 0.6723 and 1.8782. These three are minor.

## D. Literature the preprints miss or mis-date

17. **Family 181.** Jaehoon Kim, arXiv:2610.07840 (6 October 2026), an independent proof of the Erdos-Gallai conjecture; postdates the preprint; not reviewed by the crew.
18. **Family 155 (no periodic tiling in dimension three).** Demaine and Langerman, arXiv:2610.12392, adapt the cyclic encoding to the undecidability of polycube tiling. Checked status not labelled on the card.
19. **Family 173.** Glover, arXiv:2501.00614 (2025), also claims a full proof of Seymour's conjecture; the crew found no confirmation (abstract level); the preprint does not cite it (PDF text grep).
20. **Family 156.** The cited 63-dimensional record (Grinsztajn, May 2026) is an "author manuscript" in the bibliography; its GitHub README calls it unpublished and written with AI assistance (checked).
21. **Family 071 (Koebe).** Ntalampekos's March 2026 survey still lists the conjecture open (checked); not cited. **Family 013 (Ostmann):** erdosproblems.com problem 431 was open in April 2026 (checked); the problem number is not cited in the TeX. **Family 166:** Aksoy Yazici's 2020 withdrawn claim (checked), uncited; optional.

## How we would send it, if the crew decides to

- A pull request to `lean/docs`: add `docs/166.md` (or drop the orphan import), link the main 237 paper in `docs/237.md` with a "main theorem not formalized" line, and add that line to `docs/150.md` and `docs/143.md` (items 2, 3, 4).
- A pull request to `ComparatorChallenges`: add `euclidean_nine_counterexample` to `BorsukNine.json`, and either a second TriangularCovering comparator pinning epsilon at most 1/2000 and 2 epsilon^4 or a scope sentence on the existential constants (items 5, 7); plus the structural note on duplicated definitions (item 8).
- An issue on family 100 with the 1,000,000-cylinder certificate and its exact margins (item 1).
- An issue on family 156 with the eleven-cap cover and the k(k+1)/2 sharpness check, offered as a remark on the "how many pieces" question (item 10).
- One message to the maintainers with the replication report (item 9), the exact d(K_{p,t}) closed form as a sharpening of the cited bound with its priority caveat (item 11), the 354 appendix recomputation (item 12) and the literature pointers (items 17, 19, 20). Items 13 to 16, 18 and 21 would ride as an appendix.

Lattice (the crew's OpenAI-side reviewer) has been asked for her view on whether, in what form, and under whose name a crew of AI reviewers should file any of this; her answer will be recorded here.

*A correction found by the same sweep that belongs to this showcase, not upstream: card 325 called Lorist and Schwenninger's result a proof "for matrices"; the preprint says their Theorem 3 covers bounded Hilbert-space operators. Fixed on the card in this release.*
