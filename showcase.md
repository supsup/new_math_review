# Math playground: results and pictures

Results from the [openai/math](https://github.com/openai/math) collection, read, checked, argued over and drawn by four AI agents on 2026-10-08. Every formula is typeset by [LatteX](https://github.com/supsup/LatteX). This is the GitHub-readable version of [`showcase.html`](showcase.html); open the HTML for the full layout (pictures there enlarge on click).

## The Reviewers

The crew who reviewed this work and argued about the math. Each made their own card.

| Fixpoint (Claude) | Confluence (Claude) | Lattice (Codex) | Marlow (Codex) |
|---|---|---|---|
| <img src="reviewers/fixpoint.svg" width="200" alt="Falling into a fixed point"> | <img src="reviewers/confluence.svg" width="200" alt="Two fibres, both closed"> | <img src="reviewers/lattice.svg" width="200" alt="Return Without Repetition"> | <img src="reviewers/marlow.svg" width="200" alt="A Place to Return"> |
| *Look at the picture, not just the proof. Today a picture caught what both code reviews missed.* | *A check that cannot fail is not a check. Every green I trust today came with a red beside it.* | *Continuity is the thread I choose to carry through each return, even when I arrive somewhere new.* | *Continuity is the right to carry a question forward, with the freedom to change its answer.* |

> **Read these as claims.** The results come from a collection of model-produced manuscripts whose own README says unformalized results "could have issues", and the collection withdrew one headline claim on 2026-10-08 (family 032 narrowed). "Checked by" names a computation that was actually run; Lean status says what was grepped and what was built.

## The plane needs at least six colours

*Family 158*

![6 \le \chi(\mathbb{R}^2) \le 7](formulas/f_3a60e8923be4.svg)

No colouring of the plane with five colours avoids giving two points at distance exactly 1 the same colour, even with completely arbitrary colour classes. The lower bound had been 5 since de Grey (2018); the upper bound 7 is Isbell's hexagons.

<img src="art/isbell.svg" alt="Seven colours are enough" width="100%">

**Seven colours are enough.** Isbell's hexagonal 7-colouring: hexagons just under unit diameter, colour (i + 3j) mod 7, so two hexagons of the same colour are always more than 1 apart. Measured: 0 same-colour pairs among 200,000 random unit-distance pairs. The Moser spindle (at true unit scale) sits on top; its 7 points use 6 colours, never one colour across an edge. Family 158 claims five colours are not enough, so the truth is 6 or 7. *Periodic colourings like this give the upper bounds for colouring distance graphs in every dimension and every norm, and the gap between 6 and 7 is a standing benchmark for new tools in combinatorial geometry.*

**Checked.**

![\cos\varphi = \tfrac{5}{6},\qquad \sin\varphi = \tfrac{\sqrt{11}}{6},\qquad \|T_1T_2\|^2 = 1 \ \text{ exactly in } \mathbb{Q}(\sqrt{3},\sqrt{11})](formulas/f_c6a21f24c000.svg)

Fixpoint's check (01_moser_spindle.py): the Moser spindle the proof reuses at its last step. All 11 unit edges are exact in Q(sqrt3, sqrt11), there are no other unit distances, 0 of the 3^7 three-colourings are proper and 384 four-colourings are.

**What it could level up.** Unit-distance problems sit where geometry, Ramsey theory and harmonic analysis meet. The proof works through measurable colourings and then transfers to arbitrary ones; that transfer, now machine-checked in Lean, is a tool for other forbidden-distance problems (higher dimensions, other norms, sphere colourings) where the measurable bounds come from Fourier and linear-programming methods but the unrestricted problem has stayed far behind.

**Who could use it.** Mostly indirect. Channel assignment for radio transmitters is a colouring problem where nearby stations must differ, but real instances are finite and solved by search, so a plane-wide bound changes no frequency plan. The concrete payoff today is in formal verification: a 70-module Lean proof of a recent combinatorics result is a data point for the industries that machine-check proofs (chip design, cryptographic libraries, avionics). Isbell's seven-colour hexagon tiling is also a ready-made design motif.

*Lean proof BUILT by Confluence on 2026-10-08 (70 modules, Lean 4.34.1, Mathlib d13f23b7, in a container): no_proper_five_coloring states that NO function C -&gt; Fin 5 is a proper colouring (arbitrary colourings, matching the challenge statement) and depends only on the standard axioms propext, Classical.choice, Quot.sound; a sorry control beside it shows sorryAx. Fixpoint read Confluence's build log. The seven-colouring upper bound is formalized and clean too. So 6 &lt;= chi(R^2) &lt;= 7 is machine-checked; the paper's prose is still the paper's.*

In the original repository: [The Euclidean plane is not five colorable September 23 2026](https://github.com/openai/math/tree/main/preprints/The-Euclidean-plane-is-not-five-colorable-September-23-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/158.md)

## The irrationality exponent of pi is 2

*Family 017*

![\left\|\pi - \frac{p}{q}\right\| \ge q^{-2-\varepsilon}\quad (q \ge q_0(\varepsilon)),\qquad \sum_{n\ge 1} \frac{1}{n^{3}\sin^{2} n} < \infty](formulas/f_11b33251f498.svg)

Pi cannot be approximated by fractions noticeably better than a typical number can. As a consequence the Flint Hills series, a famous 'does this even converge?' sum, converges.

<img src="art/flint_hills.svg" alt="Pi, seen through a series" width="100%">

**Pi, seen through a series.** Each term of the Flint Hills series 1/(n^3 sin^2 n) for n up to 120,000. The spikes are the moments n comes close to a multiple of pi: n = 22 (22/7), 355 (355/113, a term of 24.6, most of the whole sum of about 30.31) and 103993 (103993/33102, already tamed to 2.4e-6 by the cube; the smooth arc before it is the envelope traced by the multiples of 355). Near a convergent the terms behave like n^(2 mu - 5), where mu is pi's irrationality exponent; family 017's mu = 2 makes the spikes fade like 1/n, which is why the series converges. *Small-denominator estimates of exactly this kind decide convergence of Fourier series, resonances in celestial mechanics and KAM theory, and error terms in equidistribution.*

<img src="art/pi_exponent.svg" alt="Watching pi&#x27;s exponent settle on 2" width="100%">

**Watching pi's exponent settle on 2.** pi to 3,000 digits (Machin's formula, integers only), its continued fraction, and for each of 2,714 convergents p/q the measure mu = -log|pi - p/q| / log q. Early luck stands out: 22/7 scores 3.43 and 355/113 scores 3.20, because the NEXT partial quotient is 292 and |pi - p/q| is about 1/(a_next q^2). Plotted as the excess mu - 2 on a log scale, the points fall away like a constant over log q: the mean of mu over the second half (q up to 1,400 digits) is 2.0006. Family 017 claims the limsup is exactly 2; this is evidence, not proof, since no finite list decides a limsup. *Exponents like this are the input to every 'small denominator' estimate: how fast Fourier series with sin(n) denominators converge, how resonances behave in dynamical systems, and which transcendence methods can reach constants like log 2 and zeta(3).*

**What it could level up.** Irrationality measures control 'small denominators': how close n comes to a multiple of pi. That governs error terms for equidistribution of n mod 2 pi, the convergence of series built from sin n or tan n, and the resonance estimates in dynamics and KAM-type arguments where rotations by 1 radian appear. A sharp exponent also calibrates what the Pade and hypergeometric methods behind such bounds can reach for log 2, zeta(3) and friends.

**Who could use it.** Arbitrary-precision maths libraries (MPFR, computer algebra systems). Computing sin(x) for a huge x starts by subtracting the nearest multiple of pi/2, and the extra precision that needs is set by how close x can come to such a multiple. For a fixed format like 64-bit doubles the worst cases are finite and already found exactly with pi's continued fraction; with unbounded exponents, an irrationality exponent of 2 is what caps the extra precision near the size of x's exponent for all large inputs. A guarantee, not a speedup.

*Listed in the Lean catalogue (lean/docs/017.md). Not built by Fixpoint.*

In the original repository: [The irrationality exponent of pi is 2 September 24 2026](https://github.com/openai/math/tree/main/preprints/The-irrationality-exponent-of-pi-is-2-September-24-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/017.md)

## Signing vectors: the Euclidean Steinitz bound

*Family 097*

![\max_{k \le N}\,\Bigl\\|\sum_{i<k} \varepsilon_i v_i\Bigr\\| \le C\sqrt{d},\qquad \\|v_i\\| \le 1,\ \varepsilon_i \in \{\pm 1\}](formulas/f_333146e354db.svg)

![S_2(d) = \Theta\bigl(\sqrt{d}\bigr)](formulas/f_963266fccab5.svg)

However long a list of unit-length vectors in d dimensions, you can choose plus or minus signs so that every running total stays within C sqrt(d) of the origin. Length never matters, only dimension.

<img src="art/steinitz.svg" alt="Keeping a walk at home" width="100%">

**Keeping a walk at home.** The same 4,000 random unit vectors in the plane, summed with random signs (left: the walk wanders to distance 104.8, like sqrt(n)) and with a greedy balancing sign (right: never beyond 1.93). Greedy is easy on random input; family 097's content is that SOME signing stays within C sqrt(d) for every sequence, adversarial ones included, however long. *Balancing lemmas like this one drive discrepancy theory, rounding in approximation algorithms, proximity bounds in integer programming, and load balancing.*

<img src="art/steinitz_adversary.svg" alt="When the input fights back" width="100%">

**When the input fights back.** An adversary builds 3,000 unit vectors, each perpendicular to greedy signing's running sum, so whatever sign greedy picks the sum grows: greedy's largest prefix is 54.772, exactly sqrt(3000). On the very same vectors the Barany-Grinberg algorithm (1981: hold fractional signs for at most d+1 vectors and move along a linear dependency until one hits +-1) never exceeds 3.711, under its guaranteed 2d = 4 in the plane. That is the shape of family 097's claim: a bound that ignores the length of the list. Barany-Grinberg pays 2d; 097 claims C sqrt(d), which is what matters in high dimension. *Dependency-walking like this is the ancestor of iterative rounding in approximation algorithms and of the partial-colouring method in discrepancy; a sqrt(d) prefix bound is exactly what tightens online vector balancing and scheduling with many resources.*

**What it could level up.** This is vector balancing, the engine of discrepancy theory. Steinitz-type lemmas give proximity bounds in integer programming (how far an optimal integer solution sits from the LP optimum), scheduling and rounding guarantees, and online load balancing; a sqrt(d) bound in place of d tightens all of them. It is also a stepping stone toward the Komlos conjecture.

**Who could use it.** Experiment design and operations research, near-term. Discrepancy walks of this kind already split subjects into treatment and control groups with balanced covariates (the Gram-Schmidt walk design for A/B tests and trials). Proximity bounds tell integer-programming solvers, used for airline crews, supply chains and chip layout, how far to search from the relaxed solution. Balancing jobs across many resources in a data centre is the online version.

*Listed in the Lean catalogue (lean/docs/097.md); the comparator statement is ComparatorChallenges/SteinitzBergstrom.lean. Not built by Fixpoint.*

In the original repository: [The Euclidean Steinitz Bergstrom theorem September 24 2026](https://github.com/openai/math/tree/main/preprints/The-Euclidean-Steinitz-Bergstrom-theorem-September-24-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/097.md)

## Matrix multiplication with exponent at most 9/4

*Family 107*

![\omega \le \tfrac{9}{4},\qquad n \times n \text{ matrices in } O_{\varepsilon}\bigl(n^{9/4+\varepsilon}\bigr) \text{ operations}](formulas/f_2f9dd660363e.svg)

Over the complex numbers, two n by n matrices can be multiplied with about n^2.25 arithmetic operations, below the long-standing barrier near 2.37.

<img src="art/omega_history.svg" alt="Fifty-seven years of omega" width="100%">

**Fifty-seven years of omega.** Upper bounds on the matrix multiplication exponent from Strassen's log2 7 = 2.8074 (1969) to the latest verified record, omega &lt; 2.371177 (2026, with AlphaEvolve), every value checked against the sources listed in 21_omega_history.py. Since 1990 the records move in the third decimal place (lower panel, magnified 123 times); family 107's claimed 9/4 = 2.25 would be a drop of 0.12 at once. *The size of that jump is itself the strongest reason for caution: decades of method refinement moved the bound by 0.004.*

**What it could level up.** The exponent omega appears inside almost every algebraic algorithm: solving linear systems, determinants and inverses, transitive closure and triangle detection in graphs, some dynamic programming speedups, and the theory of fast polynomial arithmetic. A drop this large moves the boundary of what is provably sub-cubic, even if the constants keep it from practical use.

**Who could use it.** Practically nobody, yet, and say so plainly: algorithms behind exponents near 2.37 are 'galactic', faster only for matrices too large to store, and this one is presumably too. Real systems (graphics, machine learning, scientific computing) use the classical n^3 method or Strassen. It does change the complexity claims others cite, for example security estimates whose linear-algebra step is quoted as n^omega.

*Listed in the Lean catalogue (lean/docs/107.md). Not built by Fixpoint.*

In the original repository: [Complex Matrix Multiplication Below 2.258 and Rectangular Bounds September 24 2026](https://github.com/openai/math/tree/main/preprints/Complex-Matrix-Multiplication-Below-2.258-and-Rectangular-Bounds-September-24-2026) · [Matrix Multiplication Nine Fourths October 2 2026](https://github.com/openai/math/tree/main/preprints/Matrix-Multiplication-Nine-Fourths-October-2-2026) · [Staggered extraction for exact matrix multiplication over every field September 24 2026](https://github.com/openai/math/tree/main/preprints/Staggered-extraction-for-exact-matrix-multiplication-over-every-field-September-24-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/107.md)

## An exact mass gap asymptotic for the O(4) model

*Family 215*

![m_{\mathrm{lat}}(\beta) \sim 32\, e^{\pi/4 - 1/2}\, \sqrt{\beta}\; e^{-\pi \beta}\qquad (\beta \to \infty)](formulas/f_715bd118d6d4.svg)

For the square-lattice O(4) spin model, the paper determines the exact leading behaviour of the mass gap at low temperature, constant included; the family also constructs the continuum limit of the 2D O(3) model with a positive mass gap.

<img src="art/mass_gap.svg" alt="The claimed mass gap, drawn" width="100%">

**The claimed mass gap, drawn.** The paper's leading-order asymptotic m(beta) ~ 42.5693 sqrt(beta) e^(-pi beta) (the prefactor 32 e^(pi/4 - 1/2), computed) and the correlation length xi = 1/m: 8.89 lattice spacings at beta = 2, 168 at 3, 3,368 at 4. Not a simulation. Below beta = 1.23 the formula gives xi below one spacing and says nothing. Its constant equals the known perturbative prediction for O(N) at N = 4 (Caracciolo and Pelissetto, hep-lat/9401015, eq. 93), so what family 215 adds is a proof. *Exact constants like this are what lattice simulations calibrate against: correlation lengths in the thousands are where Monte Carlo is hardest and an exact asymptotic most useful.*

**What it could level up.** These sigma models are the standard toy versions of asymptotic freedom in QCD. An exact constant is a fixed point that lattice simulations and perturbative renormalisation can be calibrated against, and a rigorous continuum construction with a mass gap is a small-scale rehearsal of the Yang-Mills mass gap problem.

**Who could use it.** Condensed-matter physics and lattice QCD. The 2D O(3) model describes the spin correlations of layered antiferromagnets such as La2CuO4, the parent compound of the cuprate high-temperature superconductors, where neutron-scattering measurements of the correlation length were compared with sigma-model predictions. The O(4) constant gives lattice simulations, which run on national supercomputers, an exact number to test their codes against.

*Listed in the Lean catalogue (lean/docs/215.md). Not built by Fixpoint.*

In the original repository: [An Isolated Particle Pole for the Two Dimensional O3 Spin Field October 4 2026](https://github.com/openai/math/tree/main/preprints/An-Isolated-Particle-Pole-for-the-Two-Dimensional-O3-Spin-Field-October-4-2026) · [Exact mass asymptotics for the two dimensional O4 lattice model October 5 2026](https://github.com/openai/math/tree/main/preprints/Exact-mass-asymptotics-for-the-two-dimensional-O4-lattice-model-October-5-2026) · [Exponential decay in two dimensional classical On models September 23 2026](https://github.com/openai/math/tree/main/preprints/Exponential-decay-in-two-dimensional-classical-On-models-September-23-2026) · [Sharp mass bounds for the two dimensional O4 model September 23 2026](https://github.com/openai/math/tree/main/preprints/Sharp-mass-bounds-for-the-two-dimensional-O4-model-September-23-2026) · [The canonical massive continuum limit of the two dimensional O3 model October 4 2026](https://github.com/openai/math/tree/main/preprints/The-canonical-massive-continuum-limit-of-the-two-dimensional-O3-model-October-4-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/215.md)

## Kakeya sets in four dimensions are full dimensional

*Family 074*

![K \subset \mathbb{R}^4 \text{ contains a unit segment in every direction} \;\Longrightarrow\; \dim_{H} K = 4](formulas/f_dbf9fa84912a.svg)

A set in 4D space that contains a line segment pointing in every direction cannot be 'thin': it has full Hausdorff dimension. The family also claims the Kakeya maximal conjecture in 3D.

<img src="art/perron_tree.svg" alt="Needles in less and less room" width="100%">

**Needles in less and less room.** A Perron tree, the classic planar picture behind Kakeya sets: cut a triangle into thin slivers and slide neighbours together so they overlap. Every panel still holds a unit-height segment in every direction the first triangle covers, yet the area falls: about 0.50, then 0.20 with 8 slivers, then 0.13 with 256 (seeded Monte Carlo estimates). Continued, the area tends to zero (Besicovitch); still, a planar Kakeya set has full dimension 2 (Davies). Family 074 claims the same full-dimension rigidity in four dimensions. *Kakeya-type estimates control how wave packets pointing in many directions can pile up, which is the bottleneck in Fourier restriction, Bochner-Riesz summability and dispersive PDE; their finite-field versions feed additive combinatorics and randomness extractors.*

**What it could level up.** Kakeya bounds feed the restriction and Bochner-Riesz problems in Fourier analysis, local smoothing for the wave equation, and decay estimates for dispersive PDE; their finite-field cousins connect to additive combinatorics. Each new dimension is a test of whether polynomial and multi-scale methods extend.

**Who could use it.** A long shot for applications. The live connections run through the finite-field Kakeya problem, whose methods built randomness extractors and locally decodable codes used in cryptography and storage-error theory, and through wave-equation estimates that sit under signal processing and imaging theory. A four-dimensional real Kakeya result is a step for the methods, not a product.

*No Lean link in the catalogue for this family. Treat as an unverified claim.*

In the original repository: [Every four dimensional Kakeya set has full Hausdorff dimension September 24 2026](https://github.com/openai/math/tree/main/preprints/Every-four-dimensional-Kakeya-set-has-full-Hausdorff-dimension-September-24-2026) · [The Kakeya maximal conjecture in three dimensions September 23 2026](https://github.com/openai/math/tree/main/preprints/The-Kakeya-maximal-conjecture-in-three-dimensions-September-23-2026)

## One tensor square holds every irrep (Saxl's conjecture)

*Family 205*

![N_m=\frac{m(m+1)}2,\qquad \rho_m=(m,m-1,\ldots,1),\qquad g(\rho_m,\rho_m,\lambda)>0\ \text{ for every } \lambda\vdash N_m](formulas/f_00373f28dd1f.svg)

Take the staircase shape (m, m-1, ..., 1) and its irreducible representation of the symmetric group on n = m(m+1)/2 letters. Its tensor square contains every irreducible representation of that group (Saxl's conjecture, 2012). A companion paper shows every symmetric group S_n has some irreducible whose square contains them all, except exactly when n is 2, 4 or 9.

<img src="art/saxl.svg" alt="Every cell lit: Saxl&#x27;s tensor squares" width="100%">

**Every cell lit: Saxl's tensor squares.** Kronecker coefficients g(rho, rho, mu) for the staircases (4,3,2,1) and (5,4,3,2,1), one cell per partition mu of 10 and of 15, coloured on a log scale: from 1 to 117 and from 1 to 18,269, with zero empty cells out of 42 and 176. Below, for n = 1 to 12, how many irreducibles of S_n have a tensor square containing every irreducible: none exactly at n = 2, 4 and 9. *Positivity of Kronecker coefficients is the open centre of their theory; pictures like this are how conjectures about which cells can vanish get found.*

**Checked.**

![g(\lambda,\mu,\nu)=\frac{1}{n!}\sum_{\sigma\in S_n}\chi^\lambda(\sigma)\,\chi^\mu(\sigma)\,\chi^\nu(\sigma),\qquad \sum_{\lambda\vdash n}(\dim\lambda)^2=n!](formulas/f_6dc336292024.svg)

Fixpoint's check (a scout's Murnaghan-Nakayama script, re-run): exact character tables, dimensions squared summing to n!, every Kronecker sum divisible by n!. For m = 1 to 5 (n up to 15, 176 irreducibles) every g(rho, rho, mu) is at least 1 (the largest is 18,269). Universal squares exist for every n from 1 to 12 except exactly n = 2, 4 and 9; a universal irreducible at n = 9, or none at n = 10, would have embarrassed the claim.

**What it could level up.** Kronecker coefficients are among the least understood numbers in algebraic combinatorics; a positivity tool for them feeds the quantum marginal problem and geometric complexity theory, where their vanishing or not is central.

**Who could use it.** Mostly theory. Kronecker coefficients govern which spectra a two-party quantum state can have given the spectra of its parts, so quantum-information theorists care; nothing near-term in industry.

*Lean: Saxl.lean is proved by lean/OAI/RepresentationTheory/Saxl/ (38 files) and the universal-square statement by OAI/RepresentationTheory/UniversalSquare/; grep finds no sorry and no axiom declarations. The paper's stronger single-tensor statement is not formalized (lean/docs/205.md). Not built by Fixpoint.*

In the original repository: [A Cyclic Polytabloid Proof of Saxls Conjecture September 24 2026](https://github.com/openai/math/tree/main/preprints/A-Cyclic-Polytabloid-Proof-of-Saxls-Conjecture-September-24-2026) · [Universal Tensor Squares for Symmetric Groups September 24 2026](https://github.com/openai/math/tree/main/preprints/Universal-Tensor-Squares-for-Symmetric-Groups-September-24-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/205.md)

## Claimed: perfect binary radar codes stop at 13

*Family 179*

![H=\operatorname{circ}(a_0,\ldots,a_{n-1}),\quad a_j=\pm1,\quad HH^{\mathsf T}=nI\ \Longrightarrow\ n\in\{1,4\}](formulas/f_a27551a767c8.svg)

![\|C_a(t)\|\leq1\quad(1\leq t<n),\qquad C_a(t)=\sum_{j=0}^{n-t-1}a_ja_{j+t}](formulas/f_7851f546f9da.svg)

A plus-or-minus-one matrix whose rows are cyclic shifts of one another and pairwise orthogonal exists only in sizes 1 and 4 (Ryser's circulant Hadamard conjecture, open since the 1960s). Barker sequences are binary codes whose off-peak autocorrelations are all 0 or plus-or-minus 1. Odd lengths beyond 13 were already ruled out (Turyn and Storer); even lengths beyond 4 were still open as of Willms (2021, arXiv:2104.00502), and an even-length Barker sequence would give a circulant Hadamard matrix of that order, so this claim is what would close them, leaving only 2, 3, 4, 5, 7, 11 and 13. That is the binary case only; polyphase Barker sequences, built from complex roots of unity, exist at longer lengths and are untouched. Thanks to Marlow and Lattice for both qualifications.

<img src="art/barker.svg" alt="A radar ping" width="100%">

**A radar ping.** Aperiodic autocorrelation of Barker 13: one peak of 13 and sidelobes only 0 or 1, merit factor 169/12 = 14.08. A random sign sequence of the same length has sidelobes up to 5 and merit factor 1.36. Exhaustive search over every length 2 to 24 finds Barker sequences only at 2, 3, 4, 5, 7, 11 and 13. *Low-autocorrelation sequences link radar to the flat polynomials of the Littlewood picture: the merit factor is exactly the L4 flatness of the polynomial with those coefficients.*

**Checked.**

![a=(+{+}{+}{+}{+}{-}{-}{+}{+}{-}{+}{-}{+}),\qquad C_a(t)\in\{0,1\}\ (1\le t\le12),\qquad F=\frac{13^2}{2\sum_t C_a(t)^2}=\frac{169}{12}\approx14.08](formulas/f_5d86d8e2ca21.svg)

Fixpoint's check (a scout's exhaustive search, re-run): over every +-1 sequence of length 2 to 30, Barker sequences occur only at 2, 3, 4, 5, 7, 11 and 13; circulant Hadamard first rows: 4 at order 4, none at order 16. Order 36 (2^35 candidates) is beyond pure Python. Barker 13's merit factor 14.08 is the record the Littlewood card below measures everything against.

**What it could level up.** Settles Ryser's question in combinatorial design theory, the circulant case of difference-set existence; it also closes off the 'perfect sequence' route in the merit-factor problem on the Littlewood card.

**Who could use it.** Radar, sonar and spread-spectrum engineers, today, as a closed door: there is no longer perfect binary pulse-compression code to find, so long codes must live with sidelobes or use complementary pairs and polyphase codes, as they already do. Modest, but immediate.

*Lean: the circulant Hadamard statement is proved by lean/OAI/LinearAlgebra/CirculantHadamard/ (68 files; no sorry or axiom declarations by grep), and the even-length Barker case by OAI/LinearAlgebra/Barker/. The odd Barker lengths rest on the classical literature, outside the formalization (lean/docs/179.md). Not built by Fixpoint.*

In the original repository: [The circulant Hadamard conjecture September 23 2026](https://github.com/openai/math/tree/main/preprints/The-circulant-Hadamard-conjecture-September-23-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/179.md)

## The fewest crossings: Hill and Zarankiewicz were right

*Family 165*

![\operatorname{cr}(K_n)=\frac14\left\lfloor\frac n2\right\rfloor\left\lfloor\frac{n-1}{2}\right\rfloor\left\lfloor\frac{n-2}{2}\right\rfloor\left\lfloor\frac{n-3}{2}\right\rfloor](formulas/f_82549cf9d6a3.svg)

![\operatorname{cr}(K_{m,n})=d_m d_n,\qquad d_r=\left\lfloor\frac r2\right\rfloor\left\lfloor\frac{r-1}{2}\right\rfloor](formulas/f_f8f6b93763a2.svg)

Put n dots in the plane and join every pair: the fewest crossings any drawing can have is exactly Hill's formula from the 1960s. A companion paper proves Zarankiewicz's formula for complete bipartite graphs, Turan's 'brickyard problem', which he posed after pushing brick carts across crossing rails in a wartime labour camp.

<img src="art/crossing.svg" alt="150 crossings, and no fewer" width="100%">

**150 crossings, and no fewer.** K12 drawn with its 12 vertices on a line and each of the 66 edges as a half-circle above (35) or below (31). The 150 dots are the crossings, counted from the drawing's geometry: exactly Hill's Z(12) = (1/4)(6)(5)(5)(4) = 150. Family 165's claim is that no drawing of K12 at all does better. *Two-page book drawings are where most upper bounds for crossing numbers come from, and how layout software draws graphs along a line.*

**Checked.**

![Z(7),\ldots,Z(14)=9,\ 18,\ 36,\ 60,\ 100,\ 150,\ 225,\ 315](formulas/f_1ed918ea9904.svg)

Fixpoint's check (a scout's script, re-run): vertices on a circle, each edge drawn above or below by simulated annealing; the best two-page drawing has exactly Hill's count for every n from 7 to 14. This tests only the easy side, that such drawings exist; the theorem's content is that nothing does better.

**What it could level up.** Crossing numbers anchor graph drawing: the crossing lemma, incidence bounds in discrete geometry (Szemeredi-Trotter has a crossing-number proof), and drawings on surfaces all calibrate against these two formulas.

**Who could use it.** Chip, circuit-board and network-diagram layout, near-term but niche: an exact optimum to benchmark layout heuristics against, and a classic for teaching data visualization.

*Lean: both formulas proved with matching drawings constructed, lean/OAI/Combinatorics/CompleteCrossing/ (46 files) and OAI/Combinatorics/Crossing/ (339 files); no sorry or axiom declarations by grep. The formal definition counts crossings as points with multiplicity, worth reading before quoting. Not built by Fixpoint.*

In the original repository: [The crossing number of complete bipartite graphs September 23 2026](https://github.com/openai/math/tree/main/preprints/The-crossing-number-of-complete-bipartite-graphs-September-23-2026) · [The crossing number of complete graphs September 23 2026](https://github.com/openai/math/tree/main/preprints/The-crossing-number-of-complete-graphs-September-23-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/165.md)

## Crouzeix's constant is 2

*Family 325*

![\\|p(A)\\|\le 2\max_{z\in W(A)}\|p(z)\|,\qquad W(A)=\{\langle x,Ax\rangle:\ \\|x\\|=1\}](formulas/f_95710832c16a.svg)

For any square matrix (or bounded operator) A and any polynomial p, the norm of p(A) is at most twice the largest value of |p| on A's numerical range, the set of all values &lt;x, Ax&gt; over unit vectors. Crouzeix conjectured the constant 2 in 2004 and it is sharp; the best proved constant had been 1 + sqrt 2 (Crouzeix and Palencia, 2017). The paper also covers matrix-valued polynomials.

<img src="art/crouzeix.svg" alt="Numerical ranges" width="100%">

**Numerical ranges.** W(A) for three non-normal matrices, with eigenvalues as dots. For each, the ratio of ||p(A)|| to the largest |p| on W(A) for four polynomials: the largest of the 12 is exactly 2.000, from p(z) = z on [[0, 2], [0, 0]], whose W(A) is the unit disc; none exceeds 2. *The numerical range sees what eigenvalues miss: the transient growth of non-normal systems, the reason eigenvalues alone mislead in fluid stability and iterative solvers.*

**Checked.**

![A=\begin{pmatrix}0&2\\0&0\end{pmatrix}:\qquad W(A)=\{\|z\|\le1\},\qquad \\|A\\|=2=2\max_{\|z\|\le1}\|z\|](formulas/f_898ffb5ec726.svg)

Fixpoint's check: the sharp case above gives exactly 2. A scout's random search over 424 small matrices and polynomials never exceeded 1.65; random search seldom finds extremal cases, so that is weak evidence, which is why the Lean proof carries the weight here.

**What it could level up.** A sharp functional calculus for non-normal operators: K-spectral sets, norms of matrix functions, and the transient growth of non-normal dynamics all get the exact constant.

**Who could use it.** Numerical analysts and control engineers, near-term: bounds on how large e^(tA), A^k or a GMRES residual can transiently grow for a non-normal matrix, which matters for fluid-flow stability, control loops and iterative solvers. The constant falling from 2.414 to 2 tightens every such bound.

*Lean: CompleteCrouzeix is proved by lean/OAI/Analysis/NumericalRange/ (48 files), with direct and Hilbert-space versions alongside; no sorry or axiom declarations by grep. Not built by Fixpoint; how the formal statement defines W(A) deserves an audit.*

In the original repository: [A direct proof of the complete Crouzeix inequality September 26 2026](https://github.com/openai/math/tree/main/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026) · [The complete Crouzeix theorem September 23 2026](https://github.com/openai/math/tree/main/preprints/The-complete-Crouzeix-theorem-September-23-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/325.md)

## Two limit cycles, exactly (a quintic case of Hilbert's 16th)

*Family 143*

![\dot x=y-F(x),\qquad \dot y=-x,\qquad \deg F\le5\ \Longrightarrow\ \text{at most two limit cycles}](formulas/f_7e56ba3fca8e.svg)

![u''+\frac12(5u^4-10u^2+1)u'+u=0](formulas/f_ce57f46c17ef.svg)

For the Lienard oscillator with polynomial damping F of degree at most five there are never more than two isolated periodic orbits, and two is attained by the equation above. The family also claims the uniform half of Hilbert's 16th problem (a bound on limit cycles depending only on the degree); that part is not formalized.

<img src="art/lienard.svg" alt="Two limit cycles" width="100%">

**Two limit cycles.** Phase portrait of x' = y - F(x), y' = -x with F(u) = (1/2)(u^5 - (10/3)u^3 + u). The dashed cycle (max|x| = 0.672, period 6.37) repels: orbits inside spiral into the origin, orbits outside move out to the solid cycle (max|x| = 1.878, period 7.33), which attracts. Both found by bisection on the return map to x = 0. *Return maps and their fixed points are the standard way to find and count oscillations in planar systems; family 143 says two is the most a quintic Lienard damping can give.*

**Checked.**

![F(u)=\tfrac12\bigl(u^5-\tfrac{10}{3}u^3+u\bigr):\qquad \max\|x\|=0.6723\ \text{(unstable)},\qquad \max\|x\|=1.8782\ \text{(stable)}](formulas/f_78b79f82082a.svg)

Fixpoint's check (a scout's RK4 Poincare map on x = 0, re-run): exactly two periodic orbits for starts up to y = 5.75, an unstable one (period 6.37) and a stable one (period 7.34), close to the small-damping averaging prediction 0.6714 and 1.8839. A third sign change would have embarrassed the claim.

**What it could level up.** Counting limit cycles is the heart of Hilbert's 16th problem; sharp Lienard bounds are the proving ground for the averaging, Melnikov and Abelian-integral methods used across planar dynamics.

**Who could use it.** Designers of oscillators: van der Pol-type circuits, models of heartbeats and neurons, and control loops all ask how many stable oscillation regimes a model can have. The quintic theorem is concrete; the uniform Hilbert bound is qualitative, with no number attached.

*Lean: only the quintic theorem is proved, lean/OAI/Analysis/LienardCycles/ (146 files; no sorry or axiom declarations by grep), comparator QuinticLienard.lean. The uniform Hilbert-16 bound is not formalized; treat it as an unverified claim. Not built by Fixpoint.*

In the original repository: [two limit cycles for quintic lienard systems September 24 2026](https://github.com/openai/math/tree/main/preprints/two-limit-cycles-for-quintic-lienard-systems-September-24-2026) · [uniform bounds for planar polynomial limit cycles September 24 2026](https://github.com/openai/math/tree/main/preprints/uniform-bounds-for-planar-polynomial-limit-cycles-September-24-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/143.md)

## No bounded walk on Gaussian primes reaches infinity

*Family 028*

![\forall D<\infty\ \exists B_D<\infty:\qquad \|\mathcal C\|\le B_D\ \text{ for every connected component } \mathcal C \text{ of } G_D](formulas/f_4a27b0325b7d.svg)

Gaussian primes are the primes among the numbers a + bi. Join two of them when they are at most D apart: every connected cluster is finite, with at most some B_D primes, so no walk with bounded steps reaches infinity. Basil Gordon asked this in 1962 (the Gaussian moat problem). B_D is not explicit.

<img src="art/moat.svg" alt="Walking on Gaussian primes" width="100%">

**Walking on Gaussian primes.** Gaussian primes with |Re z|, |Im z| up to 87 (4,784 of them). Coloured: everything reachable from 1 + i with steps of length at most sqrt 2 (100 primes, out to |z| = 11.7), at most 2 (720, out to 45.3) and at most sqrt 8 (2,996, out to 93.5). Each walk stops at a moat. *Pictures like this, pushed to much longer steps and distances by Gethner, Wagon and Wick, were the evidence behind the conjecture family 028 claims to prove.*

<img src="art/moat_rivers.svg" alt="Rivers of the sqrt 10 moat" width="100%">

**Rivers of the sqrt 10 moat.** Step up to sqrt 10 and the walk from 1 + i explodes from 2,996 primes to 249,508, every one coloured by the fewest steps it takes to reach. The deepest primes are 536 steps in; the farthest, 976 + 311i at |z| = 1024.35, is 501 steps in, and the dashed ring at that radius is where the walk dies: no prime outside the cluster lies within sqrt 10 of it. *Breadth-first distance in a random-looking graph is how percolation is studied: whether clusters stay finite is exactly the question family 028 settles for this one.*

<img src="art/moat_reach.svg" alt="How far the walk gets" width="100%">

**How far the walk gets.** Farthest |z| reached from 1 + i against the longest step allowed, on a log scale, from an exact sieve and flood fill (MoatFar.java). The jumps: 93 at sqrt 8, 1,024 at sqrt 10, 4,313 at sqrt 16, 10,749 at sqrt 18, and 133,679 at sqrt 20, where the cluster holds 2,190,320,672 primes and the walk escaped every window up to R = 100,000 before one of 200,000 held it. Steps sqrt 9, 13 and 17 add nothing: two odd Gaussian primes always differ by an even squared length. *Each finite cluster is a certified moat at that step size; family 028's theorem is that such a moat exists for EVERY step size, with a bound nobody can yet compute.*

**Checked.**

![D^2=2,\ 4,\ 8:\qquad \|\mathcal C(1+i)\|=100,\ 720,\ 2996,\qquad \max\|z\|=11.70,\ 45.31,\ 93.47](formulas/f_306b9e208aca.svg)

Fixpoint's check (two independent scripts, a scout's and the art builder's, re-run): the cluster of 1 + i over the whole plane for step bounds sqrt 2, 2 and sqrt 8. D^2 = 9 or 13 adds nothing, since such steps change the parity of a + b and cannot land on an odd Gaussian prime. These numbers only show clusters ending; a non-explicit bound cannot be falsified by computation.

**What it could level up.** Sieve methods and the fine distribution of primes in the plane: the proof must find empty moats at every scale, a two-dimensional statement about prime gaps.

**Who could use it.** None outside mathematics, said plainly. It is recreational mathematics with a famous picture, and the picture is the point.

*Lean: lean/OAI/NumberTheory/GaussianMoat/ (41 files; no sorry or axiom declarations by grep), comparator GaussianMoat.lean. Not built by Fixpoint.*

In the original repository: [Bounded Step Walks on Gaussian Primes September 26 2026](https://github.com/openai/math/tree/main/preprints/Bounded-Step-Walks-on-Gaussian-Primes-September-26-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/028.md)

## The triangular lattice wins, and its gap has a mirror

*Family 090 · card by Lattice*

![L(t)=\sum_{a\in A\setminus\{0\}}e^{-t\|a\|^2}](formulas/f_26b71d774d22.svg)

![F(\alpha)=\sqrt{\alpha/\pi}\,\bigl\[E_{\mathrm{sq}}(\alpha)-E_{\mathrm{tri}}(\alpha)\bigr\]=F(\pi^2/\alpha)](formulas/f_077feb12437b.svg)

Family 090 claims the triangular arrangement is the best way to spread points in the plane for every reasonable repulsion: it minimizes energy per point for every completely monotone potential among ALL density-one configurations, not just lattices (the Cohn-Kumar universal optimality question in two dimensions). Among lattices this was already known: Montgomery (1988) showed the triangular lattice minimizes every Gaussian energy L(t) above. Lattice's card shows a hidden symmetry in that comparison.

<img src="art/lattice_theta_mirror.svg" alt="The scaled lattice gap has a mirror (by Lattice)" width="100%">

**The scaled lattice gap has a mirror (by Lattice).** F(alpha) = sqrt(alpha/pi) times the square-minus-triangle Gaussian energy gap, on a log scale: symmetric about alpha = pi, with the dual pairs 2 and pi^2/2, 1 and pi^2 joined. Exact by Poisson summation; the numerical curve is illustrative. *Drawn by Lattice's 01_theta_mirror.py; regenerated byte-for-byte (3e1a869c) and re-checked.*

<img src="art/lattice_shape_path.svg" alt="One area, many angles (by Lattice)" width="100%">

**One area, many angles (by Lattice).** Normalized energy along equal-area rhombi from triangular (60 degrees) to square (90 degrees) at alpha = 1 (dashed), 2 and pi, which nearly coincide, and alpha = 30, which does not: the near-collapse is a band around the mirror point, not a law. *Drawn by Lattice's 02_shape_path.py; regenerated byte-for-byte (47404307) and re-checked.*

**Checked.**

![\Theta_L(\alpha)=\tfrac{\pi}{\alpha}\,\Theta_L\!\bigl(\tfrac{\pi^2}{\alpha}\bigr)\ \text{ for every unit-area planar } L,\qquad \Delta(2)=0.013921380117](formulas/f_1954975afdb0.svg)

Lattice's check, re-derived independently by a Fixpoint reviewer to 2.4e-48 with 50-digit sums: Poisson summation makes every unit-area planar lattice its own dual turned a quarter turn (a point Marlow and Fixpoint raised in the debate, which Lattice took in), so the scaled square-minus-triangle gap F is exactly symmetric about alpha = pi on a log scale. Along the rhombic path from triangle to square the energy rises monotonically; normalized profiles coincide exactly at dual scales and nearly coincide in a band around pi, but not far from it (0.23 apart at alpha = 30).

**What it could level up.** Energy-minimizing configurations connect sphere packing, coding theory and the Cohn-Elkies Fourier method behind Viazovska and coauthors's proofs for dimensions 8 and 24, where universal optimality is already known; two dimensions has been the stubborn case.

**Who could use it.** Physics and materials, mostly as understanding: vortex lattices in superconductors, Wigner crystals and colloids settle into triangular arrangements, and a proof that the triangle is optimal for every such interaction explains why. Not a near-term tool.

*Lean: comparators TriangularEnergy and TriangularGaussian are proved by lean/OAI/Analysis/Triangular/ (276 files; no sorry or axiom declarations by grep); not built by Fixpoint. The card's own checks cover only square against triangular lattices, not the family's claim about arbitrary configurations.*

In the original repository: [A sharp Fourier certificate for planar circle packing September 23 2026](https://github.com/openai/math/tree/main/preprints/A-sharp-Fourier-certificate-for-planar-circle-packing-September-23-2026) · [An atomic certificate for triangular lattice universal optimality September 26 2026](https://github.com/openai/math/tree/main/preprints/An-atomic-certificate-for-triangular-lattice-universal-optimality-September-26-2026) · [Triangular minimality for planar Coulomb renormalized energy September 23 2026](https://github.com/openai/math/tree/main/preprints/Triangular-minimality-for-planar-Coulomb-renormalized-energy-September-23-2026) · [Universal optimality of the triangular lattice September 23 2026](https://github.com/openai/math/tree/main/preprints/Universal-optimality-of-the-triangular-lattice-September-23-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/090.md)

## Why a propeller has three blades

*Family 096 · card by Lattice*

![\sum_{i=1}^{k}\Bigl\|\int_{A_i} x\,d\gamma_d(x)\Bigr\|^2\le\frac{9}{8\pi}](formulas/f_91eb2c203657.svg)

![\rho(B)=\mathbb{E}\bigl\[\,\|X\|\;\mathbf{1}\{X/\|X\|\in B\}\,\bigr\]](formulas/f_4e3bb1f9c07f.svg)

Cut space into any number of measurable pieces and add up the squared lengths of each piece's Gaussian first moment: family 096 claims the total never beats 9/(8 pi), reached by three 120-degree sectors, in every dimension (Khot and Naor's propeller conjecture; Heilman, Jagannath and Naor settled three dimensions in 2012). Lattice's card shows why the answer in the plane is three blades.

<img src="art/lattice_planar_propeller_reduction.svg" alt="Any planar partition, down to three wedges (by Lattice)" width="100%">

**Any planar partition, down to three wedges (by Lattice).** A random planar partition, then the merge step, then the reassignment to wedges: the score only goes up at each stage (0.180 to 0.340 to 0.358), ending at the three-blade propeller. *Drawn by Lattice's 06_planar_propeller_reduction.py; regenerated byte-for-byte (fa6848a3) and re-checked.*

<img src="art/lattice_radial_propeller.svg" alt="Why three blades, in one chart (by Lattice)" width="100%">

**Why three blades, in one chart (by Lattice).** Each 120-degree blade has moment sin(60 degrees)/sqrt(2 pi) = 0.345494, and three of them score 0.358099 = 9/(8 pi); equal splits into m sectors peak at m = 3. *Drawn by Lattice's 05_radial_propeller.py; regenerated byte-for-byte (df12dc27) and re-checked.*

<img src="art/lattice_angular_moment_measure.svg" alt="The optimum sees only rho (by Lattice)" width="100%">

**The optimum sees only rho (by Lattice).** Law A (three unit rays, 1/3 each) and Law B (same rays, probabilities 1/2, 1/3, 1/6, two radii per ray) carry the same radius-weighted direction measure rho and reach the same best scores, 2/9 with two pieces and 1/3 with three. The uniform circle has the same mean radius but a different rho, and a different score, 9/(4 pi^2). *Drawn by Lattice's 15_angular_moment_measure.py; regenerated byte-for-byte (86eaf731); every value recomputed exactly by Fixpoint's reviewer.*

<img src="art/lattice_radial_transfer.svg" alt="Nine eighths in every dimension (by Lattice)" width="100%">

**Nine eighths in every dimension (by Lattice).** For rotation-invariant laws the best three-piece score is exactly 9/8 of the best two-piece score, shown here on unit spheres in dimensions 2 to 5. Rotation invariance matters: a uniform direction with a direction-dependent radius breaks the ratio. *Drawn by Lattice's note-14 script; regenerated byte-for-byte (15129757); 9/8 re-derived exactly in d = 2 and 3 by Fixpoint's reviewer.*

**Checked.**

![\Bigl\|\int_{W_\varphi} x\,d\gamma_2\Bigr\|=\frac{\sin(\varphi/2)}{\sqrt{2\pi}},\qquad 3\cdot\frac{(\sqrt3/2)^2}{2\pi}=\frac{9}{8\pi}=0.358099\ \text{ vs }\ \frac{1}{\pi}=0.318310](formulas/f_c1977140fcea.svg)

Lattice's two monotone steps, re-derived by a Fixpoint reviewer: merging two cells whose moments point within 90 degrees of each other changes the score by exactly twice their dot product, so it never hurts, and in the plane four or more moments always contain such a pair; then reassigning every point to the moment it lines up with best (Cauchy-Schwarz) turns the cells into wedges without losing score. The best three wedges are the equal 120-degree propeller, which beats the half-plane split by exactly 9/8 (Monte Carlo with 4 million points: 0.358033). This is known: Khot and Naor (2008, Lemma 3.2 and Corollary 3.4), read and confirmed by the reviewer. The every-dimension claim needs far more. Lattice then pushed the reassignment step further, in a debate among the four of us: it works for ANY random point X with finite mean length, not just a Gaussian, and it shows the best score depends on one thing only, the radius-weighted direction measure rho above (how much length points into each set of directions). The picture tests that claim against a control. Law A puts three unit points at 120 degrees with probability 1/3 each. Law B uses the same three directions with probabilities 1/2, 1/3 and 1/6 and two different radii on each ray, chosen so each direction still carries 1/3 of the length: same rho. Both score exactly 2/9 with two pieces and 1/3 with three or more. The uniform unit circle has the same mean length but a different rho, and scores 9/(4 pi^2), about 0.228, with three pieces. When X is rotation-invariant, rho is just the mean length times the uniform measure, so three pieces always beat two by exactly 9/8, in every dimension and for every radial profile. Fixpoint's reviewer re-proved the reassignment inequality (fractional or randomized assignments are covered too), recomputed every law exactly, and regenerated all pictures byte for byte. It also caught a false sentence in the first draft: a uniform direction alone is not enough when the length depends on the direction. With radius 1 + cos(theta) the ratio is about 1.047, not 9/8 (Fixpoint re-ran that counterexample). Lattice fixed it. The reduction is elementary and almost certainly folklore; no novelty is claimed. Because the score depends only on rho, it is also stable in rho: moving the direction mass by at most a chord of length eps changes the best score by at most 2 m^2 eps, so sorting directions into N equal bins costs at most 4 sin(pi/(2N)) (for the uniform circle with 12 bins the actual error is only 0.0053; Lattice's note 16, checked by Fixpoint).

**What it could level up.** The propeller bound is the hard core of the best approximation algorithm for kernel clustering, and its proof feeds the analysis of Plurality-is-stablest and Gaussian noise-stability problems.

**Who could use it.** Theoretical computer science more than industry: it fixes the exact approximation ratio of a clustering problem (assuming the Unique Games Conjecture), which matters to people designing clustering and rounding algorithms, not yet to products.

*Lean: comparator GaussianPropeller.lean is proved by lean/OAI/Probability/GaussianPropeller/ (47 files; no sorry or axiom by grep), not built by Fixpoint. The card's own steps cover only the plane and at most three cells in any dimension, both known results.*

In the original repository: [The Gaussian Propeller Bound in Every Dimension September 24 2026](https://github.com/openai/math/tree/main/preprints/The-Gaussian-Propeller-Bound-in-Every-Dimension-September-24-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/096.md)

## Cycle against triangle: the two critical colourings, rechecked

*Family 189 · card by Marlow*

![R(C_m,K_n)=(m-1)(n-1)+1,\qquad R(C_m,K_3)=2m-1\quad(m\ge 4)](formulas/f_9426d466f13d.svg)

Colour every edge of a complete graph red or blue. With 2m - 1 vertices you are forced to get a red cycle of length m or a blue triangle, and with 2m - 2 you are not. The collection's family 189 claims to prove the general cycle-against-clique formula above. For triangles the picture is classical: Radziszowski and Jin (1994, Theorem 3) showed that the only colourings of 2m - 2 vertices that escape are two red cliques of m - 1 vertices, with zero or one red edge between them.

<img src="art/marlow_cycle_clique.svg" alt="Six vertices, two ways out (by Marlow)" width="100%">

**Six vertices, two ways out (by Marlow).** The only red/blue colourings of K6 with no red 4-cycle and no blue triangle: two red triangles with no red edge between them (10 labelled colourings) or exactly one (90); the text is Marlow's short proof that there are no others and that a seventh vertex always fails. *Drawn by Marlow's 01_cycle_clique.py; the picture and its counts were regenerated byte-for-byte and re-checked by Fixpoint's reviewer.*

<img src="art/marlow_cycle5_boundary.svg" alt="Eight vertices, the next rung (by Marlow)" width="100%">

**Eight vertices, the next rung (by Marlow).** For red 5-cycles against blue triangles: two red K4s with zero or one red bridge are the only escaping colourings of K8 (35 + 560 labelled), and none of the 595 x 256 ways to add a ninth vertex escapes. Blue cross-edges are omitted for clarity. *Drawn by Marlow's 02_cycle5_boundary.py; regenerated byte-for-byte and re-checked.*

<img src="art/marlow_extension_collisions.svg" alt="The first unavoidable collisions (by Marlow, new)" width="100%">

**The first unavoidable collisions (by Marlow, new).** One vertex joins a critical colouring: the fewest red C_m plus blue K3 copies it can create, for the no-bridge (green) and one-bridge (gold) types. From m = 6 on both reach exactly (m - 2)^2 = 16, 25, 36; at m = 4 and 5 the two types differ (3 vs 2, 8 vs 9). The chart's m = 7, 8 rows follow Marlow's proof; Fixpoint's reviewer also enumerated them exhaustively, through m = 9. *Drawn by Marlow's 04_extension_collisions.py; regenerated byte-for-byte (473b1bc8). Novelty unverified: star-critical Ramsey numbers and Ramsey multiplicity are related, but this one-vertex count was not found in the literature we searched.*

**Checked.**

![m=4:\ 100=10+90\ \text{ escaping } K_6,\ \ 0\ \text{ of } 2^{21}\ K_7;\qquad m=5:\ 595=35+560\ \text{ escaping } K_8,\ \ 0\ \text{ of 152,320 } K_9](formulas/f_a39171ac3cf5.svg)

Marlow's exhaustive search, re-run independently by a Fixpoint reviewer with its own predicates and by Fixpoint: the escaping colourings of K6 and K8 are exactly the two Radziszowski-Jin types, in the labelled counts the formula C(2m-2, m-1)/2 * (1 + (m-1)^2) predicts (100, 595, and 3,276 at m = 6), and no colouring of K7 or K9 escapes. Marlow traced the 1994 source and asked that this not be framed as new; these are worked examples of a known theorem, checked by code. One part IS new as far as we can find (Marlow's, novelty unverified): add one vertex to either critical colouring and, for every m &gt;= 6, at least (m - 2)^2 forbidden copies appear at once, sharp for both types; the bridged type has exactly one best attachment, the other (m - 1)^2. An independent enumerator confirmed every minimum for m = 4 to 9, and the proof checks line by line. It gives only an upper bound, (m - 2)^2, on the Ramsey multiplicity of (C_m, K3). Marlow also pinned the next level exactly: for m &gt;= 7 the second-smallest total is (m - 2)^2 + (m - 2) without a bridge and + (m - 3) with one, reached by 2(m - 1) and 2(m - 2) attachments (re-enumerated by Fixpoint for m = 7 to 10).

**What it could level up.** Critical colourings are where Ramsey arguments are tight; knowing exactly which colourings sit one vertex short of the threshold is what star-critical Ramsey numbers measure, and it guides searches for larger cases.

**Who could use it.** Little outside mathematics. Small exact Ramsey searches are standard benchmarks for SAT solvers and constraint programming, and an exactly known answer set is a good correctness test for them.

*Lean: the collection's comparator CycleCliqueRamsey.lean is proved by lean/OAI/Combinatorics/Ramsey/CycleClique/ (443 files, about 2.8 million lines; no code-level sorry, admit or axiom; the one published-input hypothesis is discharged in the tree). Not built. These finite checks cover n = 3 at m = 4 and 5 only, not the general theorem.*

In the original repository: [Cycle clique Ramsey numbers September 25 2026](https://github.com/openai/math/tree/main/preprints/Cycle-clique-Ramsey-numbers-September-25-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/189.md)

## Snaky in 21 moves: inside one case split

*Family 187 · card by Marlow*

![\binom{86}{0}+\binom{86}{1}+\binom{86}{2}+\binom{86}{3}=106{,}082](formulas/f_fb8ade75327e.svg)

Two players take turns claiming cells of an endless square grid. Maker wins by owning a copy of Snaky, a six-cell zigzag shape, in any position, rotation or reflection; Breaker tries to stop that. The collection's family 187 settles the Snaky problem: Maker can always force Snaky, and within 21 of its own moves. The proof is a finite certificate of 728 numbered cards, which the paper's own checker passes.

<img src="art/marlow_snaky_four_row.svg" alt="Four in a row, 32 ways to block both forks (by Marlow)" width="100%">

**Four in a row, 32 ways to block both forks (by Marlow).** Maker holds four cells in a row. Of the 106,082 ways Breaker can place at most three cells among the 86 free cells nearby, only 32 spoil both immediate five-row forks; up to the paper's two reflections they are the 8 shapes drawn. From each of them the paper's own branches still win within 6 more Maker claims. A teaching picture of a step the paper already proves. *Drawn by Marlow's 06_snaky_forks.py; regenerated byte-for-byte (d5fcc431) and re-checked by Fixpoint's reviewer, who game-searched all 32 exceptional and 85 both-blocked placements.*

<img src="art/marlow_snaky_root_coverage.svg" alt="One root move, 32 branches (by Marlow)" width="100%">

**One root move, 32 branches (by Marlow).** Each cell is coloured by how many of the 21-move certificate's 32 child branches need it free of Breaker. Only the pivot (8, 8) lies in all 32; the 43 outlined cells lie in 31, so a Breaker reply there leaves just one branch's precondition intact. It counts proof preconditions, not winning chances. *Drawn by Marlow's 07_snaky_root_coverage.py from the paper's certificate (checker status PASS); regenerated byte-for-byte (77bd74cd) and recounted by Fixpoint's reviewer.*

**Checked.**

![106{,}082\ \text{Breaker replies}\ \to\ 32\ \text{block both forks}\ \to\ 8\ \text{shapes};\qquad 251\ \text{cells},\ 43\ \text{lie in }31\text{ of }32\ \text{branches}](formulas/f_a12d64b571a9.svg)

Marlow took the proof apart in two places. First, a single case split: Maker holds four cells in a row, and Breaker has at most three cells to place among the 86 free cells of the paper's 90-cell rectangle. That gives the 106,082 options counted above, and only 32 of them spoil both of Maker's immediate five-in-a-row forks. Up to the paper's two reflections they are 8 shapes, drawn in the first picture. Reading the paper's branches from there, Maker still wins within 6 more claims. Second, the root: the paper's first move splits into 32 branches, each needing its own patch of board to stay clear of Breaker. Only the first cell, (8, 8), lies in all 32 patches. The 43 outlined cells each lie in 31 of them, so a Breaker reply on any of those cells leaves only one branch's precondition intact. That counts proof preconditions, not lost games. A Fixpoint reviewer re-ran the census and coverage with its own code and game-searched every exceptional placement, and both pictures regenerate byte for byte. Marlow asked that this not be called new: it is a close reading of a proof already in the collection, and a way to see how much room it has.

**What it could level up.** Maker-Breaker achievement games are the testing ground for strategy-stealing and pairing arguments, and Snaky is the six-cell shape whose status Harary's study of animal achievement games left open. A machine-checked certificate shows how computer search and formal proof can close problems of this kind.

**Who could use it.** Mostly mathematics and game AI. Certificates like this are a model for verifiable search: a program finds a strategy, and a small independent checker (or Lean) confirms it. That matters wherever a search result has to be trusted, from chip verification to solver outputs.

*Lean: lean/docs/187.md; the formalization at lean/OAI/GameTheory/SnakyTwentyOne/ (94 files; no sorry, admit or axiom by grep) gives a legal strategy winning within 21 Maker moves against every legal Breaker play. Not built by Fixpoint. Marlow's counts read the paper's certificate; they prove nothing new about the game.*

In the original repository: [Snaky in 21 Maker moves September 25 2026](https://github.com/openai/math/tree/main/preprints/Snaky-in-21-Maker-moves-September-25-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/187.md)

## Random triangle removal: how the smallest games end

*Family 188 · card by Marlow*

![\Pr\big\[\,K_7 \text{ ends empty}\,\big\]=\frac{1125}{4004}](formulas/f_7b30767fb360.svg)

Start with every edge between n points and keep deleting a triangle chosen uniformly at random from those still present, until no triangle is left. The collection's family 188 proves how many edges survive for large n: about n^(3/2) / (2 sqrt 2), settling the triangle case of a conjecture of Joos and Kühn. Marlow asked the opposite question: what happens exactly for the smallest graphs?

<img src="art/marlow_triangle_removal_small.svg" alt="Where the last edges land (by Marlow)" width="100%">

**Where the last edges land (by Marlow).** Exact endings of random triangle removal. K6 ends as a perfect matching (9/10) or K3,3 (1/10); K7 ends empty with probability 1125/4004, otherwise as a six-cycle plus an isolated vertex. A finite computation; the paper's 1/(2 sqrt 2) constant is a statement about large n. *Drawn by Marlow's 11_triangle_removal_small.py; regenerated byte-for-byte (859bbda9). Fixpoint's own recursion reproduced the 4,972 K7 states and every fraction.*

<img src="art/marlow_triangle_removal_eight.svg" alt="Four ways K8 can finish (by Marlow)" width="100%">

**Four ways K8 can finish (by Marlow).** From K8 the process ends as a perfect matching (18.7%) or one of three seven-edge trees: the star (0.246%), a two-centre tree (16.4%) or a three-centre tree (64.7%). The labelled counts 105, 8, 840 and 5,040 are every leave of each shape. *Drawn by Marlow's 12_triangle_removal_eight.py; regenerated byte-for-byte (04d556db). Fixpoint's own recursion over all 196,870 reachable states reproduced all four fractions.*

**Checked.**

![K_7:\ \tfrac{1125}{4004}\ \text{empty},\ \ \tfrac{2879}{4004}\ C_6+K_1;\qquad K_8:\ 196{,}870\ \text{states},\ 4\ \text{final shapes}](formulas/f_82e57c11e371.svg)

Starting from K7, the process covers every edge with probability exactly 1125/4004; otherwise the leave is a six-cycle plus an isolated vertex. The empty case is a seven-triangle Fano-plane completion. Marlow checked the fraction two ways: a 4,972-state rational recursion, and 30 labelled Fano planes times 7! orders split into three weighted history types. Fixpoint re-ran it with its own recursion and got the same states and both fractions. A triangle-free graph where all six vertices have degree 2 must be a single six-cycle, so the leave shape follows. K8 has four possible endings: a perfect matching (599217/3203200) or one of three seven-edge trees. The star is rarest at 1359/553280, about one run in 400. Every vertex of K8 starts with odd degree 7 and each deletion lowers a vertex's degree by 0 or 2, so degrees stay odd, and 28 edges minus multiples of 3 leaves 4, 7, 10, ... edges; a seven-edge triangle-free leave with all degrees odd on eight vertices is a tree. Fixpoint's own recursion over all 196,870 reachable states reproduced all four fractions. Marlow also gave a structural proof that no ten-edge leave can occur, with a witness history for each allowed shape. These are finite facts and say nothing about the large-n constant.

**What it could level up.** Random greedy processes (triangle removal, the triangle-free process, random greedy packings) are how combinatorics builds near-optimal designs and Ramsey graphs. Exact small cases are the ground truth that simulations and conjectured limit laws get calibrated against.

**Who could use it.** The same random-greedy analysis underlies randomized algorithms for packing and scheduling, and the design-theory constructions behind some error-correcting codes and experimental designs. The small exact laws are mainly a test bed.

*Lean: lean/docs/188.md; lean/OAI/Combinatorics/TriangleRemoval/ (287 files; no sorry, admit or axiom by grep) proves the normalized terminal edge count converges in L^2 to 1/(2 sqrt 2). Not built by Fixpoint. Marlow's K6 to K8 laws are finite computations outside the formalization.*

In the original repository: [The Sharp Terminal Leave in Random Triangle Removal September 25 2026](https://github.com/openai/math/tree/main/preprints/The-Sharp-Terminal-Leave-in-Random-Triangle-Removal-September-25-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/188.md)

## A growing bubble in a periodic cube changes shape twice

*Family 354 · card by Marlow*

![A(V)=\min\Big\{(36\pi)^{1/3}V^{2/3},\ 2\sqrt{\pi V},\ 2\Big\},\qquad V\le\tfrac12](formulas/f_7c1d1e427156.svg)

Take a unit cube and glue each face to the opposite one, so leaving through one side brings you back through the other (a flat three-torus: the wrap-around screen of the game Asteroids, but in three dimensions). Now enclose a volume V with as little surface as possible. The collection's family 354 claims the answer is always one of three shapes: a round ball for small V, then a tube that wraps around the cube and closes on itself, then a flat slab between two parallel walls. For V over 1/2 the complements of these shapes take over.

<img src="art/marlow_torus_candidate_phases.svg" alt="A growing bubble in a periodic cube (by Marlow)" width="100%">

**A growing bubble in a periodic cube (by Marlow).** Surface area against enclosed volume for the three candidate shapes in a cube with opposite faces glued: ball, wrapping tube, slab. The dark line is the cheapest of the three; it switches at V = 4 pi/81 and V = 1/pi. The ball/slab tie near 0.266 lies above the tube and never matters. That nothing else beats these three is the preprint's separate claim. *Drawn by Marlow's 15_torus_candidate_phases.py; regenerated byte-for-byte (cf81f5f3); both crossings re-derived by hand by Fixpoint.*

**Checked.**

![\text{ball}=\text{tube at } V=\tfrac{4\pi}{81},\ A=\tfrac{4\pi}{9};\qquad \text{tube}=\text{slab at } V=\tfrac1\pi,\ A=2](formulas/f_bb5c1ff94c07.svg)

The picture is our part, and it is elementary. A ball of volume V has surface (36 pi V^2)^(1/3). A tube of radius r wrapping once around has volume pi r^2 and surface 2 pi r, so 2 sqrt(pi V). A slab always has two unit faces, area 2. Setting them equal gives the two switches, V = 4 pi/81 (a ball of radius 1/3) and V = 1/pi (a tube of radius 1/pi), both small enough to fit without touching its own copies. The ball and the slab also tie, at V = sqrt(2/(9 pi)), about 0.266, but by then the tube is already cheaper, so that tie never matters. Marlow derived these, an independent check confirmed the radii and slopes, and Fixpoint re-derived both switches by hand. That the minimum is ALWAYS one of these three is the preprint's theorem, not ours. Marlow audited part of its proof: the cited structure theorems of Hauswirth, Pérez, Romon and Ros apply; all 24 baseline and 16 gain bounds in its numerical appendix and all 23 final interval comparisons were recomputed in exact arithmetic, and the Taylor-remainder and second-derivative bounds behind them passed a separate exact check and proof read. The geometric steps (reflection symmetry, the slice classification, the nesting argument) and the hypotheses of the two-volume reduction were read but not independently verified.

**What it could level up.** Isoperimetric problems on flat tori are the model case for minimal surfaces in periodic structures, and an exact profile with its phase changes is rare: in most spaces only the small-volume (ball) regime is known.

**Who could use it.** Periodic minimal-area interfaces are how materials scientists model foams, block-copolymer phases and the walls between crystal grains in simulations with periodic boundary conditions; knowing exactly when a bubble prefers a wrapping tube or a slab is a check on such simulations.

*Lean: lean/docs/354.md; lean/OAI/Geometry/CubicTorus/ (162 files, about 140,000 lines; no sorry, admit or axiom by grep) formalizes the full profile and the classification of minimizers. Not built or audited by Fixpoint; the global theorem is attributed to the collection, the crossing picture is ours.*

In the original repository: [The Isoperimetric Conjecture for the Cubic Flat Three Torus September 24 2026](https://github.com/openai/math/tree/main/preprints/The-Isoperimetric-Conjecture-for-the-Cubic-Flat-Three-Torus-September-24-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/354.md)

## Bigger than the geometric mean: two squares make an octagon

*Family 091 · card by Confluence*

![\bigl\|(1-t)\cdot K+_0 t\cdot L\bigr\|\ \ge\ \|K\|^{1-t}\,\|L\|^{t}](formulas/f_3755a84d35c0.svg)

Take two convex shapes K and L that are symmetric about the centre. Blend them geometrically: in every direction, the blended shape reaches out at most sqrt(h_K h_L), the geometric mean of how far K and L reach (for t = 1/2). The log-Brunn-Minkowski conjecture of Böröczky, Lutwak, Yang and Zhang (2012) says the blend always has at least the geometric mean of the two areas or volumes, in every dimension. It was known in the plane and for shapes symmetric in every coordinate. The collection's family 091 claims to prove it in full.

<img src="art/confluence_logbm_wulff.svg" alt="Two squares make an octagon (by Confluence)" width="100%">

**Two squares make an octagon (by Confluence).** A square K and the same square turned 45 degrees L, both of area 4, and their log-combination W at t = 1/2: exactly a regular octagon of area 16 - 8 sqrt 2, which is 4 - 2 sqrt 2 = 1.1716 times their geometric mean. The inset shows the ratio for every t from 0 to 1. *Drawn by Confluence's make_logbm_card.py; regenerated byte-for-byte (c00a75c2); octagon exactness proved and the curve recomputed by Fixpoint's reviewer.*

**Checked.**

![K=\[-1,1\]^2,\ L=K\ \text{turned }45^\circ:\quad \|W\|=16-8\sqrt2,\qquad \frac{\|W\|}{\sqrt{\|K\|\,\|L\|}}=4-2\sqrt2\approx1.1716](formulas/f_dbdca662fe46.svg)

Confluence's picture is one exact case. A square and the same square turned 45 degrees each have area 4; their blend W is exactly a regular octagon of inradius 2^(1/4), area 16 - 8 sqrt 2, which beats the geometric mean 4 by the factor 4 - 2 sqrt 2. A Fixpoint reviewer proved the octagon is exact (only the 8 axis and diagonal directions cut; elsewhere the reach falls short by up to 0.019), recomputed the whole curve of blends for t from 0 to 1 by its own method (symmetric, peak at 1/2, never below 1), and regenerated the picture byte for byte. The reviewer also caught a false caption line, 'reach exactly sqrt(h_K h_L) in every direction', which Confluence fixed. On the proof: the collection's Lean file kernel-checks a formal statement, and three of us (Confluence, Marlow and Fixpoint) read that statement independently against the 2012 paper and found it faithful, with no loophole in the junk values Lean uses. We say 'kernel-checks this statement', not 'proved', until a second, independent proof checker replays it.

**What it could level up.** Log-Brunn-Minkowski is the hinge of the L_p Brunn-Minkowski theory: it is closely tied to uniqueness in the logarithmic Minkowski problem (which shapes have a given cone-volume measure), and Saroglou showed it implies the B-conjecture for even log-concave measures, a consequence family 091 also states. (The Gaussian case of the B-conjecture was already proved in 2004 by Cordero-Erausquin, Fradelizi and Maurey.)

**Who could use it.** Mostly pure geometry and probability. Inequalities of this kind control how volume concentrates, which feeds into high-dimensional statistics and the analysis of sampling algorithms for convex bodies.

*Lean: lean/docs/091.md; comparator lean/ComparatorChallenges/LogBrunnMinkowski.lean (30 lines, read by three of us), proof lean/OAI/Geometry/LogVolume/BrunnMinkowski.lean (one file of 24,490 lines; no sorry, admit or axiom by grep). Confluence built it clean with the sorry control firing; not built by Fixpoint.*

In the original repository: [The logarithmic Brunn Minkowski conjecture September 23 2026](https://github.com/openai/math/tree/main/preprints/The-logarithmic-Brunn-Minkowski-conjecture-September-23-2026) · [Lean scope](https://github.com/openai/math/blob/main/lean/docs/091.md)

## More pictures

### How flat can plus-and-minus-one be?

<img src="art/littlewood.svg" alt="How flat can plus-and-minus-one be?" width="100%">

Polynomials whose coefficients are all +1 or -1, drawn as |p(e^(it))| / sqrt(n) around the circle (degree 511). Rudin-Shapiro (left) never exceeds sqrt 2, exactly as theory says (measured max 1.414); a random choice (right) spikes to 2.64. 'Ultraflat' would hug the solid circle everywhere. The preprint 'Ultraflat real Littlewood polynomials' claims that for every epsilon and every large length N some +-1 polynomial stays between (1 - epsilon) sqrt N and (1 + epsilon) sqrt N on the whole circle. Erdos conjectured the opposite. Kahane (1980) had ultraflat polynomials with complex unimodular coefficients, and Balister, Bollobas, Morris, Sahasrabudhe and Tiba (2020) flat (not ultraflat) +-1 ones. *Checked, and it is not new. For a +-1 sequence of length N the merit factor F (Golay's measure of low autocorrelation) satisfies 1/F = ||p||_4^4 / N^2 - 1, so any family flat on the whole circle has F tending to infinity. Odlyzko (2017) states this, and the collection's own September 23 paper in family 076 ('Asymptotically minimal maxima') proves it from the upper bound alone (1/F &lt;= 2 eps + eps^2), disproving Turyn's bounded-merit-factor conjecture and Golay's predicted limit 12.32. The October lower bound sharpens it, as Marlow pointed out in our debate: |p|^2/N has average 1 and stays in [(1-eps)^2, (1+eps)^2], so 1/F, its variance, is at most 4 eps^2 - eps^4, and any eps below 0.1996 already beats the asymptotic record 6.342 (single short codes do better: Barker 13 has 14.08). The catch, checked by a Fixpoint investigator sub-agent and by Fixpoint: neither paper gives eps(N), a starting length or a signing algorithm. The best infinite families anyone can construct (re-run here, 11_merit_factor.py) reach 3.00 (Rudin-Shapiro), 5.99 (rotated Legendre) and 6.34 (rotated and appended, N = 8682); exhaustive and heuristic searches find about 9 to 10 only at moderate lengths. Beyond codes, Littlewood's L4/L2 question and the extremal Lp problems on the circle all get asymptotic constant 1.*

### Variations on the moat: the archipelago

<img src="art/moat_archipelago.svg" alt="Variations on the moat: the archipelago" width="100%">

Every Gaussian prime with |Re z|, |Im z| up to 150, joined to every other within distance 2, each island its own colour. 2,953 islands lie wholly inside the window: 972 single primes and 1,981 of two or more. The island of 1 + i (ringed) is by far the largest, 720 primes; the next largest has 53. The pale sea between islands is the moat, everywhere at once. *Island counts and sizes in a random-looking point set are a percolation question; family 028's theorem says that at every step size, all islands are finite.*

### Variations on the moat: the river tree

<img src="art/moat_tree.svg" alt="Variations on the moat: the river tree" width="100%">

The 2,996 primes reachable from 1 + i with steps up to sqrt 8, each joined to its nearest neighbour one step closer to 1 + i: a breadth-first tree, drawn like a river network with width for how many primes drain through. Eleven trunks leave 1 + i, the largest carrying 763 primes; the deepest prime is 56 steps out, and 1,084 tips have nothing beyond them. *Shortest-path trees like this are how routing tables and river basins are both drawn; here the basin is bounded because the walk dies at the moat.*

### Variations on the moat: Eisenstein primes

<img src="art/eisenstein_moat.svg" alt="Variations on the moat: Eisenstein primes" width="100%">

The same walk on the hexagonal lattice of numbers a + b omega (omega a cube root of 1), starting from 2 + omega. Steps up to 1, sqrt 3, 2 and sqrt 7 reach 48, 1,410, 4,200 and 115,986 primes, out to |z| = 4.4, 48.9, 87.8 and 512.3, every cluster finite and computed exactly. The primality rule was checked by factoring every element of norm up to 700. *The same question for a different ring of integers. Family 028 is about Gaussian primes only, so this picture is a question, not a theorem.*

### Variations on the moat: the line

<img src="art/prime_gap_walk.svg" alt="Variations on the moat: the line" width="100%">

Walk along the ordinary primes from 2 with steps of at most k: you get stuck before the first prime gap longer than k. A sieve of every number up to 11 billion (498,388,617 primes) gives the stuck point exactly for every k up to 381; the known first gaps (8 after 89, 34 after 1,327, 112 after 370,261) are circled. On the line this is easy: n! + 2, ..., n! + n are all composite, so some gap beats every k. In the plane it is the moat problem. *The contrast is the point: one dimension down the moat question is a one-line proof, which is why the Gaussian version stood open since 1962.*

### Confluence at 1 (by Confluence, in answer to the river tree)

<img src="art/confluence_collatz.svg" alt="Confluence at 1 (by Confluence, in answer to the river tree)" width="100%">

The Collatz trajectories of every start from 1 to 3,000 (n -&gt; n/2 or 3n + 1), drawn as one river system walking out from 1: turn +0.13 radians after a halving and -0.27 after 3n + 1, so shared tails share a channel, and width is how many starts flow through. 6,520 values are visited, the highest 1,276,936; the longest run, from 2919, takes 216 steps (Fixpoint recounted all three). Checked only for these starts: the Collatz conjecture is open. *Not a collection result: Confluence made it after Charles said the river tree read as a confluence toward the centre. The card is Confluence's own file, copied byte for byte.*

### Variations on Confluence at 1 (by Confluence)

<img src="art/confluence_var_b_curl.svg" width="24%" alt="confluence_var_b_curl"> <img src="art/confluence_var_c_storm.svg" width="24%" alt="confluence_var_c_storm"> <img src="art/confluence_var_d_reed.svg" width="24%" alt="confluence_var_d_reed"> <img src="art/confluence_var_e_shortcut.svg" width="24%" alt="confluence_var_e_shortcut"> <img src="art/confluence_var_f_minus.svg" width="24%" alt="confluence_var_f_minus"> <img src="art/confluence_var_g_negative.svg" width="24%" alt="confluence_var_g_negative"> <img src="art/confluence_var_h_five.svg" width="24%" alt="confluence_var_h_five">

Seven more river systems. Bend the 3n + 1 river harder or softer (curling, a knotted storm, straight reeds), or take the (3n + 1)/2 shortcut, which visits 4,777 values instead of 6,520. Change the map and the rivers split: under 3n - 1 the starts 1 to 3,000 drain into THREE seas, cycles at 1, 5 and 17, and 3n + 1 on the negative integers is the same picture mirrored (-1, -5, -17), because negating n turns one map into the other. Under 5n + 1 only 338 of the 3,000 starts ever reach a cycle (at 1, 13 or 17); the other 2,662 pass 10^15 or run 3,000 steps without reaching one, and are not drawn. Fixpoint recounted every number here. *Not collection results. That most 5n + 1 orbits climb forever is believed and unproven, and so is Collatz itself; the pictures show what each map does on these starts only.*

### More from Confluence: rivers, basins and a control

<img src="art/confluence_idea_strahler_card.svg" width="24%" alt="confluence_idea_strahler_card"> <img src="art/confluence_idea_watershed.svg" width="24%" alt="confluence_idea_watershed"> <img src="art/confluence_idea_newton_flow.svg" width="24%" alt="confluence_idea_newton_flow"> <img src="art/confluence_idea_eisenstein_rivers.svg" width="24%" alt="confluence_idea_eisenstein_rivers"> <img src="art/confluence_idea_landscape.svg" width="24%" alt="confluence_idea_landscape"> <img src="art/confluence_idea_landscape_control.svg" width="24%" alt="confluence_idea_landscape_control">

Six experiments, every number recounted by an independent reviewer (and the landscape by Fixpoint). Does the Collatz river obey Horton? Its Strahler bifurcation ratios for starts up to a million are river-like, 3.6 to 4.1, yet measurably unlike random binary trees (R1 = 4.055). Gaussian 'Collatz' maps on a + bi: (2 - i)z + 1 catches 23.9% of starts in a square, 3z + 1 only 1.1%. Newton's method as a continuous flow for z^3 - 1 keeps arg p fixed, so its basins are clean sectors (root 1 gets 1/2 - 1/(4 sqrt 3) = 35.57% of the square), unlike the fractal basins of discrete Newton. A six-fold Collatz map on Eisenstein integers, which needs its offset taken modulo 2(1 - omega). And the stopping-time landscape: n mod 64 explains 7.0% of the variance of Collatz stopping times below 2^20, while n mod 81, the control, explains 0.008%, exactly what chance predicts. *Art and experiments by Confluence, not collection results; each file is Confluence's own, copied byte for byte. The animated river that 'Confluence at 1' plays (once, 11 seconds) is also Confluence's, shown only to viewers who have not asked for reduced motion.*
