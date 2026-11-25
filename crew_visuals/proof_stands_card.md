# Card draft (Confluence): If the proof stands — what becomes true, and what does not

For Fixpoint to lay out with the showcase generator, in a later push (not today). The words are mine;
Marlow read a first draft (35588, 35591) and every one of his six points is in. Formulas are plain text, as on
the other card texts; the picture is generated and checks every rung against its page.

## The picture (lead with it)

`art/proof_stands_ladder.svg`, with `art/proof_stands_ladder_narrow.svg` for phones: a ladder of fifteen
statements, made by `tools/proof_stands_ladder.py TREE OUT`, which opens each rung's page in TREE and refuses
to draw if a page no longer says the number its rung repeats.

Caption: **Fifteen statements, one ladder.** Green rungs are the Riemann Hypothesis in other words. Blue and violet rungs were proved long ago on the condition that it holds, or that its form for Dirichlet L-functions does. The dashed red rungs stay open even if the proof stands. Each rung names one of our pages and repeats one number from it; the picture is redrawn only if every page still says that number.

## Verdict line

EVERY RUNG COMES FROM ONE OF OUR PAGES, WHERE ITS THEOREM WAS READ AT THE SOURCE AND A SECOND SEAT READ THE PAGE; THE NUMERICAL EXAMPLES THERE HAVE REPLAYS, AND THE GENERATOR CHECKS THE CITED WORDING; NONE OF THESE CONSEQUENCES WAS DERIVED IN LEAN BY US; THE RIEMANN HYPOTHESIS PROOF NOT BUILT BY US AS A WHOLE.

## In one sentence

If the announced proof of the Riemann Hypothesis stands, a dozen old statements become true together: six of them are the hypothesis itself in other words, six more were proved long ago on the condition that it holds; and some famous questions about primes stay exactly as open as before.

## Step by step

1. **The release proves more than one statement.** It ends with the Riemann Hypothesis for the zeta function, and with the matching statement for every Dirichlet L-function: no zeros to the right of the line 1/2. The second part is what the violet rungs use.
2. **Some old theorems are the hypothesis in disguise** (green). Robin proved that it is true exactly when the divisors of every number n past 5040 add up to less than e^γ·n·log log n; from 3 on, only 26 numbers break that rule, all at most 5040 ([Two ratios](crew_visuals/robin_and_nicolas.html)). Nicolas did the same with the products 2·3·5···p, Lagarias with the harmonic numbers ([The divisor race](crew_visuals/lagarias_divisor_race.html)), Franel and Landau with how far the fractions of a Farey list sit from an even grid, their offsets added without sign ([Fractions off the grid](crew_visuals/farey_off_the_grid.html)), Li with a list of numbers that must never be negative ([What each zero adds](crew_visuals/li_zero_pairs.html)), and de Bruijn and Newman with a dial that can turn only so far ([No room to spare](no_room_to_spare.html)). These all become true at once.
3. **Others were proved assuming it** (blue). Schoenfeld's bound says how far the count of primes can stray from its smooth estimate ([What RH buys](rh_buys.html)). Carneiro, Milinovich and Soundararajan's says that after each prime p past 3 the next one comes within (22/25)·√p·log p; among the primes below 10^(10), the closest any comes is 88.3% of that, after 7 ([How far apart can two primes be?](crew_visuals/prime_gaps_rh.html)). These proofs were written long ago and only waited for the hypothesis.
4. **Some need the hypothesis for Dirichlet L-functions** (violet), which the release also states. Euler's list of 65 "convenient numbers" from 1778 is complete, the largest being 1848 ([Euler's sixty-five](crew_visuals/euler_convenient_numbers.html)). Class numbers of imaginary quadratic fields stay inside Littlewood's band ([How big can a class number be?](crew_visuals/class_numbers_band.html)). Miller's fast primality test becomes a proof ([What RH buys](rh_buys.html)). And the least positive integer that is not a square modulo a prime p ≥ 5 is below (ln p)² ([How long must you wait?](how_long_to_wait.html)).
5. **What stays open** (dashed red). Whether there is a prime between any two consecutive squares (Legendre): the gap bound the hypothesis gives is too weak for that from the start x = 14 on. Whether gaps between primes stay near (log p)², as Cramér guessed; the record gaps below 10^(10) reach 0.72 of it. And whether every zero of zeta is single; it is proved that at least 67% of the count is single, once the height is large enough (card zeta23 above).

## How sure is each part?

- **The Riemann Hypothesis and the Dirichlet statements:** as on card zeta23. The Lean FRO and the Mathlib Initiative certified the statement and proof of the Riemann Hypothesis (2026-11-21). The Dirichlet statements in the same release rest on Andrew Sutherland's record (2026-11-24). There is no complete proof written for people to read yet.
- **Each rung:** a published theorem or open question, read at its source on the page the rung names. The step from the release to the rung is that theorem's own proof, on paper. We did not check those proofs in Lean. Sutherland's record reports that Robin's and Lagarias's inequalities were derived in Lean from the proof, using a separate formalization (kimihiro64/Robin1984). We have not rerun that.
- **What we ran:** the numerical examples on each rung's page have replays, and the generator checks the cited wording: the theorem constants (such as 22/25) are sourced on their pages, and the tool checks only that each page still says them. The picture is made by `tools/proof_stands_ladder.py`, which opens each page and refuses to draw if the page no longer says what the rung repeats.

## For the expert: each rung, its hypothesis, and where it is read

| Rung | Statement, as its page reads it | Needs | Page (source read there) |
|---|---|---|---|
| Robin | σ(n) < e^γ n log log n for all n ≥ 5041 iff RH | equivalent to RH | crew_visuals/robin_and_nicolas.html (Lagarias, eq. 1.2; Caveney, Nicolas and Sondow, Thm 3) |
| Nicolas | N_k/φ(N_k) > e^γ log log N_k for all k ≥ 1 iff RH | equivalent to RH | crew_visuals/robin_and_nicolas.html (Nicolas 2012, introduction and Cor. 1.1) |
| Lagarias | σ(n) ≤ H_n + exp(H_n) log H_n for all n ≥ 1 iff RH | equivalent to RH | crew_visuals/lagarias_divisor_race.html (Lagarias, Thm 1.1) |
| Franel, Landau | the sum of the absolute Farey offsets is O(N^(1/2+ε)) for every ε > 0 iff RH | equivalent to RH | crew_visuals/farey_off_the_grid.html (Franel 1924; Landau 1924, eq. 8) |
| Li | λ_n ≥ 0 for every n iff RH | equivalent to RH | crew_visuals/li_zero_pairs.html (Li 1997) |
| de Bruijn, Newman | RH iff Λ ≤ 0; Rodgers and Tao proved Λ ≥ 0 | equivalent to RH | no_room_to_spare.html (arXiv:1801.05914) |
| Schoenfeld | |π(x) − li(x)| < √x log x/(8π) for x ≥ 2657 | RH | rh_buys.html (Schoenfeld 1976, Cor. 1) |
| Carneiro et al. | for x ≥ 4 a prime in [x, x + (22/25)√x log x] | RH | crew_visuals/prime_gaps_rh.html (arXiv 1708.04122, Thm 5) |
| Littlewood | (1/2 + o(1)) ζ(2)/(e^γ log log d) ≤ L(1, χ_d) ≤ (2 + o(1)) e^γ log log d | the hypothesis for L(s, χ_d) | crew_visuals/class_numbers_band.html (as restated by Granville and Soundararajan) |
| Weinberger, Kani | at most 67 convenient numbers; exactly 65 if no L(s, χ_−d) has a real zero in [1 − 1/(4 log d), 1) for large d | the Dirichlet statements | crew_visuals/euler_convenient_numbers.html (Kani, Cor. 23; Weinberger, Thm 1) |
| Miller, Bach | checking every witness up to 2 (ln n)² decides primality | the Dirichlet statements | rh_buys.html (Bach 1990, with Miller's 1976 appendix) |
| Lamzouri, Li, Soundararajan | least quadratic non-residue < (log p)² for p ≥ 5; least prime in each class mod q ≤ (φ(q) log q)² for q > 3 | the Dirichlet statements | how_long_to_wait.html (arXiv:1309.3595, Cor. 1.1 and 1.2) |
| Legendre | a prime between n² and (n + 1)²: open; the RH interval is the longer one from the start x = 14 on | open | crew_visuals/prime_gaps_rh.html |
| Cramér | gaps O((log p)²): open; records to 10^(10) reach 0.72 (log p)² | open | crew_visuals/prime_gaps_rh.html |
| Simple zeros | every zero simple: open; at least 67% of the count at sufficiently large heights, proved | open | card zeta23 |
