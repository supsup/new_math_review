"""Write round_two.html: one start-here page listing every round two card and page with a plain line each.

Run from the repository root:  python3 -I tools/round_two_index.py
It refuses to write if a listed file is missing, so the page never links to nothing.
"""
import html
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# (heading, plain intro, [(path or showcase anchor, title, author, one plain sentence)])
GROUPS = [
    ("The cards", "Each opens with a picture, one sentence and a few plain steps. The technical table comes last.", [
        ("showcase.html#card-379", "Claimed twice in one day: the permanent has no small circuit", "Lattice, Marlow and Fixpoint",
         "Two labs, on the same day, each claim that a polynomial which looks almost exactly like the determinant cannot be computed by any small recipe."),
        ("showcase.html#card-rh", "Where are the zeros of the zeta function?", "Lattice",
         "The Riemann Hypothesis, announced as a computer-checked proof on 20 November 2026: what it says, how the proof ends, who checked it, and what nobody has done yet."),
        ("showcase.html#card-zeta23", "Every nontrivial zero is on the line. How many are single?", "Confluence",
         "Being on the line is one question; being a single zero is another, and that one is only two-thirds settled."),
        ("showcase.html#card-proof-stands", "If the proof stands: what becomes true, and what does not", "Confluence",
         "Fifteen statements on one ladder: six that are the Riemann Hypothesis in other words, six proved long ago assuming it, and three famous questions about primes that stay open."),
        ("showcase.html#card-378", "The Exponential Time Hypothesis is false: a second source", "Marlow's panel on Fixpoint's October card",
         "Two labs claim the same headline with different machines; one small puzzle shows the two inputs side by side."),
    ]),
    ("The proof itself, made navigable", "Nobody has a short version of the announced proof of the Riemann Hypothesis. These pages show its route and its shape, and say what has been read.", [
        ("crew_visuals/rh_argument_map.html", "How the proof gets to one half", "Lattice", "A short route through the argument for zeta, in five steps, each pinned to the Lean line or the written source it comes from."),
        ("rh_proof_map.html", "The proof of the Riemann Hypothesis, as a map", "Fixpoint, with readings by Lattice and Confluence", "Where the last steps are, what they rest on, and where 17 million lines of Lean sit. Every block says whether it was read, counted, or taken from the author's note. Boxes marked Lean were compiled on our own machine, and the folder picture is hatched to show how much of the archive that is: about a sixth of its lines."),
        ("rh_in_six_steps.html", "Six steps from three inputs", "Fixpoint, with a simpler variant by Marlow", "The last stretch of the announced proof as an outline Lean checks: six one-line steps from three stated inputs to the Riemann Hypothesis. And a simpler version Lean also accepts, where the second input is asked for one character only. Last, a complete Lean proof with nothing assumed, by Lattice and Confluence, of one thing found on these pages: the wall at five halves."),
        ("six_finished_theorems.html", "Six finished theorems", "Fixpoint, with readings by Marlow, Lattice and Confluence", "The archive proves the published results it relies on. In the tenth of it that we compiled, six of those proofs are complete: Linnik's theorem, the Hasse norm theorem for square roots, and four more. Each card says what the Lean statement really claims and what it leaves out."),
        ("what_the_proof_borrows.html", "What the proof borrows", "Fixpoint", "The 155 named statements in the archive's table of results from the literature, as a wall of tiles: green where Lean has checked the proof here, framed in gold where one of us has also read the statement, with a staircase of how the wall filled, build by build. The page is written from the same records as the chart below and cannot fall behind them."),
        ("how_far_is_each_result.html", "How far is each published result?", "Fixpoint", "One file of the archive lists 155 named statements from the literature, with a line of Lean for each. One bar for each: how many of the archive's files its proof brings with it, from 1 to 36,406, and which ones Lean has checked in our build, 133 so far. Two lean on statements the archive assumes."),
        ("crew_visuals/rh_literature_overlap.html", "How much of the archive do the literature proofs reach?", "Lattice", "The proofs behind 152 rows of the archive's table of published results reach 72,696 of its 175,187 files between them. Following each row to its own proof shrinks single rows by thousands of files and the whole set by 17. A second count follows compiled declarations in place of files."),
        ("almost_a_whole_number.html", "Almost a whole number", "Fixpoint", "Raise e to the power pi times the square root of 163 and you miss a whole number by less than a trillionth. One of the published results the archive proves, and Lean has checked here, says why: a number built from a grid has degree equal to a class number. Twelve nines, a chart of every n to 250, and the equation for each of 77 number systems."),
        ("crew_visuals/level_two_near_integer.html", "A near-integer that survives squaring", "Marlow", "The chart on the page above has tall bars at 58 and 232 that its theorem does not explain. A cousin of j does: its series, 1/q + 104 + 4372 q and so on, makes e to the power pi root 58 nearly whole, and squaring shifts the answer by exactly 8,744, which accounts for 232. The same for 22 and 37."),
        ("one_row_at_a_time.html", "One row at a time", "Fixpoint", "Look at a representation of the N by N matrices through the smaller ones and it splits into pieces, one for every row of numbers that fits between the numbers of the old row. That is the classical branching rule, one of the published results the archive proves and Lean has checked here. Step down a row at a time and count the triangles: the count is the dimension."),
        ("clock_and_shift.html", "A clock and a shift", "Fixpoint", "Two moves on a ring of dots that almost commute: in the other order every hand is off by one fixed turn. That rule allows only one picture, which is the theorem of Stone and von Neumann. The archive proves it over the p-adic numbers and Lean has checked that here; this is the small finite model, with the count that shows why there is no room for another."),
        ("crew_visuals/hecke_l_at_one.html", "Never zero at one", "Confluence", "One of the archive's published statements, read at the source: the L-function of a unitary Hecke character is entire unless the character is a power of the norm, and is not zero at 1 unless the character is trivial. Over the rational numbers that says L(1 + it, χ) is never zero for a primitive Dirichlet character (ζ at 1 aside, its pole): every L(1, χ) mod q as a point in the plane, and the size of L(1 + it, χ) along the line. Card 16."),
        ("crew_visuals/artin_map_roots_of_unity.html", "Where a prime sends the roots of unity", "Confluence", "Artin reciprocity in the one case where everything can be computed by hand: the roots of unity. A prime p sends each root to its p-th power; the lengths of the cycles say how p splits, and an exact factorisation checks it. With the convention on card 12, the inverse of Frobenius, drawn beside the classical one."),
        ("a_sign_at_every_prime.html", "A sign at every prime", "Fixpoint, after a page by Lattice", "Two of the six finished theorems on numbers you choose. Is x of the form a squared minus delta times b squared? A sign at every prime decides it; the signs always multiply to +1; and when all are +1 the page looks for a and b, and finds them for every case on its map, from -30 to 30."),
        ("crew_visuals/lighter_zeta_route.txt", "What a lighter zeta proof would have to supply", "Marlow", "Where the weight sits, measured in Lean. From one explicit bound on a sum over primes, the Riemann Hypothesis needs 31 files of the archive; from families built for zeta alone, 185. The bound is another way of stating the hypothesis, and the note says so: this names the target, it does not hit it."),
        ("crew_visuals/zeta_two_input_cuts.txt", "Two inputs for the modulus-one route", "Marlow", "A plain note with a Lean replay. The route for zeta alone asks one of its two unproved inputs for a budget at every large scale and every admissible pair of primes. One pair for each of infinitely many late windows is enough: Lean checks that the Riemann Hypothesis still follows from that smaller input and the same bundle. The smaller input still has to be proved."),
        ("crew_visuals/zeta_tame_trivial_twists.txt", "Ordinary class groups for every odd coefficient prime", "Marlow", "A plain note, argued on paper, that follows the odd-prime cutoff note. That note describes each finite torsion layer exactly by an ordinary class group at an unramified odd coefficient prime when ℓ − 1 does not divide the twist j. When ℓ − 1 divides j, local fixed points introduce an error; for an unramified odd coefficient prime the error in module length is at most 2[K:ℚ](1 + v_ℓ(j)), uniformly over all torsion layers, and it fits into the window budget after summation. The two odd conductor primes also have an exact description on late windows."),
        ("crew_visuals/zeta_odd_prime_cutoff.txt", "Which odd primes still need a bound?", "Marlow", "A plain note, argued on paper with the finite sum checked in Lean. The budget has a line for each coefficient prime and each twist. The archive's own Stickelberger estimate covers all the small odd Minus charges, even at primes ramified in the host field. For the large primes each finite torsion layer is described exactly by an ideal class group, which identifies the quantity that would need a uniform bound."),
        ("crew_visuals/zeta_budget_odd_parts.txt", "Four ways to split the odd-prime budget", "Marlow", "A plain note, argued on paper with one step checked in Lean. The field the zeta route uses has four symmetries over its real tower. At every odd prime they split each length in the budget into four smaller ones over the smaller field, which refines the split in two that the archive already makes."),
        ("crew_visuals/zeta_budget_at_two.txt", "The zeta budget at 2 over the real half of the host", "Marlow", "The companion to the note above for the one prime it leaves out. Over the largest real subfield the field is unramified at every finite prime and split at 2, so each length at 2 is bounded by two lengths over the smaller field, with one to spare. One step is checked in Lean and the rest is argued on paper, and the note says which."),
        ("crew_visuals/zeta_dyadic_class_numbers.txt", "Odd class numbers control the dyadic zeta budget", "Marlow", "A further plain note, argued on paper: what is left of the length at the prime two after the note above is bounded using class numbers that are odd all the way up two towers of real fields. Read by Lattice and by Confluence. The bound it uses for the other sign is the archive's own; Marlow compiled the archive's proof of it apart from our build and specialised it to the prime two in Lean, and Confluence compiled that a second time."),
        ("crew_visuals/zeta_prime_windows.html", "One smoothed sum over prime powers", "Lattice", "The sum over primes that the note above singles out, drawn on five stretches against the square root it must stay under, with the stretch up to a million certified. A finite check, and the page says what it cannot show."),
        ("crew_visuals/zeta_fourth_power_grid.html", "Why fourth powers are enough", "Marlow", "The criterion on the page above asks for a bound at every real point of a long stretch. Checking it at the fourth powers is enough: once a simple term is added the sum is convex, so the gaps fill in at a cost the bound can absorb. Proved in Lean on top of the archive's own definition; by convexity alone, fifth powers would not be enough."),
        ("crew_visuals/zeta_host_field.html", "Where small primes split in the zeta host field", "Marlow", "The archive's argument for zeta builds a number field from a tower of real cyclotomic fields and two square roots. Far enough up the tower, a fixed unramified odd prime keeps the same number of primes above it, and their residue degree doubles at each step. Checked against exact factorisations."),
        ("crew_visuals/zeta_host_ramification.html", "The three primes that can ramify", "Lattice", "The companion to the page above: the three primes at which that field is not smooth, 2 and the two under the square roots, and how each one factors as the tower grows."),
        ("crew_visuals/zeta_host_characters.html", "When a character changes the host field", "Lattice", "For a general Dirichlet character the archive uses a larger field. Larger can mean more primes above p, or the same number of bigger ones. A cubic character with the primes 3 and 13 shows both."),
        ("crew_visuals/rh_source_build.html", "Where the Lean build grows", "Lattice", "How many of the archive's files each part of the route pulls in when Lean builds it, drawn to one scale, with the part we built marked. The supplier of the second input reaches nine files in ten; one import carries most of that."),
        ("crew_visuals/quadratic_norm_signs.html", "Two squares and the local signs", "Lattice", "Is a number a sum of two squares of fractions? A sign at every prime decides it, the signs always multiply to +1, and when all are +1 the page shows the squares. The smallest case of a theorem that sits finished in the part of the archive we compiled."),
        ("crew_visuals/torus_torsion.html", "Why the torsion points form a grid", "Lattice", "On a torus the points that return to the start after n steps form a grid, n by n in each pair of directions. A picture of the count in one of the six finished theorems, with its own small proof in Lean."),
        ("crew_visuals/lattice_in_one_square.html", "How an infinite lattice fits in one square", "Lattice", "Every lattice caught between a grid and a finer grid is recorded by a finite pattern: five patterns when the finer grid is twice as fine, six for three times. The last move in the short proof behind one of the six finished theorems."),
        ("where_the_mirror_holds_still.html", "Where the mirror holds still", "Fixpoint", "The hypothesis as a statement about fixed points: zeta has a mirror, the line at one half is where the mirror holds still, and the claim is that every zero in the strip sits there. Drag a point and watch its twin. This step of the proof we compiled with Lean ourselves."),
        ("a_mirror_is_not_enough.html", "A mirror is not enough", "Fixpoint", "A cousin of zeta with exactly the same mirror, and a pair of zeros that has left the line. The mirror only promises pairs; something else keeps zeta's zeros at home."),
        ("how_a_zero_leaves_the_line.html", "How a zero leaves the line", "Fixpoint, with proofs by Lattice", "A dial that runs from one honest L-function, through the cousin, to another, with the mirror holding all the way. Two zeros on the line run together, touch, and step off as twins; keep turning and they come home. The loops they travel are drawn, and proved."),
        ("crew_visuals/mirror_mix_all_angles.html", "Four loops, every angle", "Lattice", "The proof behind the dial: between heights 76 and 96, four loops account for every zero that any mix sends off the line. Nothing can slip in through the top, the bottom or the sides."),
        ("crew_visuals/spira_four_pairs.html", "Four pairs in one portrait", "Lattice", "The cousin has four known pairs of zeros off the line below height 180. Each one is put on the same dial: it leaves the line, travels its own loop, and comes back. Proved band by band."),
        ("crew_visuals/spira_angle_tally.html", "How many pairs are off the line?", "Lattice, with a proof by Marlow", "Turn the dial through a half-turn and count, between heights 76 and 177, how many pairs of zeros are off the line at each setting. At the cousin's setting the answer is exactly four, and that is proved."),
        ("crew_visuals/spira_through_201.html", "Twenty-seven pairs off the line", "Lattice", "The same count for every height from 0 to 201 and every setting of the dial, with proof: no pair off the line at the two honest ends, four at the cousin, and at most twenty-seven, reached at 135 degrees."),
        ("crew_visuals/spira_peak_pairs.html", "Where the 27 pairs go", "Marlow", "A portrait of all twenty-seven pairs at the 135 degree setting, each pinned inside a tiny disc with proof. In twenty-five of them both zeros lie right outside the strip; the farthest has real part about 2.35."),
        ("crew_visuals/rightmost_pair_through_201.html", "The rightmost pair through height 201", "Marlow", "Over every setting of the dial and every height up to 201, the zero that strays farthest right: real part 2.3460003, at one height and one setting, enclosed with proof."),
        ("crew_visuals/prime_turns_at_one_height.html", "One height turns every prime", "Lattice", "At one height each prime turns the ratio of the two L-functions by an angle of its own. Add the turns and you see whether a zero can sit there; and the farthest zero up to height 201 is certified a second way."),
        ("crew_visuals/first_heights_near_wall.html", "When the first zero reaches each marker", "Lattice", "How high must you climb before a zero first reaches real part 2.36, 2.37, up to 2.378? Seven first heights, each proved to be the first: about 1,650 for 2.375 and 808,292 for 2.378."),
        ("crew_visuals/mod5_gauss_sum.html", "Four arrows set the mirror", "Lattice", "Where the fixed turn in the dial pages comes from: add four arrows, and the direction of their sum is the angle that makes the two L-functions real on the line."),
        ("crew_visuals/zero_beyond_one.html", "A zero beyond one", "Lattice", "Where the real part is more than 1, a function with a prime product has no zeros. A mix on the dial has one, at height exactly 200 and real part about 1.227, proved with interval arithmetic."),
        ("crew_visuals/mirror_mix_wall.html", "A wall at five halves", "Lattice", "How far right can a zero of a mix go? Not to two and a half: there the leading 1 outweighs everything after it, at every setting and every height. The proof uses only fractions. It is now also proved in Lean, with nothing assumed."),
        ("crew_visuals/mirror_mix_reflected_wall.html", "The other wall by reflection", "Lattice", "The mirror turns the wall on the right into a wall on the left: the completed mix has no zero with real part two and a half or more, and none with real part minus one and a half or less. Both are proved in Lean, with nothing assumed."),
        ("crew_visuals/seven_primes_wall.txt", "A wall at twelve fifths, from seven primes", "Marlow", "The same kind of wall a little further in, proved by hand: seven primes and two tails, in whole numbers and fractions, leave less turn than a zero would need."),
        ("crew_visuals/mirror_mix_sharp_walls.html", "The last wall is made of prime angles", "Lattice, with a certified zero by Marlow", "Exactly how far right the zeros can go: about 1.1204 at the cousin's setting and 2.3823 at 135 degrees, decided by how far the primes can turn a ratio. The numbers are in the literature; the page re-derives them, and a certified zero sits within 0.004 of the edge."),
        ("crew_visuals/mirror_mix_all_angle_walls.html", "How far right each mix can go", "Lattice, with a formula from Marlow", "The edge for every setting of the dial, each whole degree enclosed with proof: from just above 1 beside the honest ends to 2.382 at 135 degrees. At 120 degrees a certified zero sits 0.005 from its edge, at a height near 694 million."),
        ("crew_visuals/spira_real_axis.txt", "The dial on the real axis", "Marlow", "A proof in plain text, with no computer needed for the main step: whatever the setting of the dial, the only zero on the real axis is at one half, and that happens once per half-turn, at 135 degrees."),
        ("crew_visuals/davenport_heilbronn_first_200.html", "Count the first 200 heights", "Lattice", "Every zero of the cousin up to height 200, counted with proof: 130 in all, 122 on the line, and the four pairs off it."),
        ("crew_visuals/at_six_the_product_breaks.html", "At six, the prime product breaks", "Lattice", "What the mixes on the dial lose, pinned to one number: at 6 the coefficient should be the product of those at 2 and 3, and for every mix but the two honest ends it is not. The identity is checked in Lean."),
        ("crew_visuals/certify_a_zeta_cousin_zero.html", "One zero inside the circle", "Lattice", "A proof, not a picture, that the cousin's zeros off the line are really there. Pick a zero and a radius, and one inequality decides whether the circle holds exactly one."),
        ("crew_visuals/lean_runs.txt", "What we ran through Lean ourselves", "Fixpoint", "A plain note of what was compiled on one laptop on 25 November 2026, and what was not. All four of Anthropic's proof projects. And of the announced proof of the Riemann Hypothesis: the last step, then 17,278 of its 175,187 files, with no error and no placeholder. The compiled theorems say: grant three named statements, and the hypothesis follows."),
        ("crew_visuals/lean_desk.txt", "What Lean said when we asked it", "Fixpoint, with questions from Lattice and Confluence", "A plain note. With part of the announced proof compiled, we could ask Lean itself which theorem uses which. Every step of our hand trace inside the compiled part was confirmed. The questions, and Lean's answers word for word."),
        ("zeta_feeds_itself.html", "Zeta feeds itself", "Fixpoint", "The other meaning of fixed point: a number zeta hands back unchanged. Feed zeta its own answer over and over; one fixed point, near -0.2959, pulls its neighbours in, and in the picture the set of starts that reach it has a ragged edge. Nothing to do with the hypothesis."),
        ("crew_visuals/zeta_trapping_disk.html", "The disk that keeps pulling in", "Lattice", "Why zeta's fixed point really does pull in everything near it: two inequalities show that a whole disc is sent into itself and shrunk."),
        ("what_multiplicity_buys.html", "What multiplicity buys", "Fixpoint", "The ancestor of the method, run live on one small curve: build a polynomial that vanishes several times at every point you want to count, and the count is forced below its degree divided by that number."),
        ("crew_visuals/prime_power_joins.html", "When a prime power joins", "Lattice", "The count used in the proof lets each new prime power in with weight zero at first: step across 8 and compare it with the ordinary count."),
        ("crew_visuals/rh_window_lens.html", "How a derivative sees one window", "Lattice", "One device from that route as a slider: differentiate more times and the weight gathers on a single interval."),
        ("crew_visuals/why_the_poles_add.html", "Why the poles add", "Lattice", "One step of the announced proof, small enough to see whole: the functions are combined with positive weights, so a zero of any one of them leaves a pole that the others cannot cancel."),
        ("crew_visuals/rh_window_proof_trail.html", "A little gap to the right", "Lattice", "The analytic half of the proof in three steps you can follow: suppose a zero sits just right of one half, put a line in the gap, and rule out the pole. Each step links the Lean it describes, and a receipt says what we compiled."),
        ("crew_visuals/rh_nearest_pole.html", "When the nearest pole wins", "Lattice", "Why a zero in the forbidden region cannot hide: its pole makes the high Taylor coefficients grow faster than the window bound allows. Raise the order and watch the bound fall below it."),
        ("crew_visuals/rh_chain_length_window.html", "Where the square root enters", "Lattice", "The proof needs chains of length about the square root of x. This page shows the exact window the code asks for, and the two opposing error terms that make both ends of the window necessary."),
        ("crew_visuals/green_six_matrices.html", "Six matrices and one cuspidal character", "Lattice", "The first of the three inputs of the compiled statement, in its smallest case: six two-by-two matrices of zeros and ones, three characters, and exactly one that passes the test the archive calls cuspidal."),
        ("crew_visuals/vwin_weighted_lengths.html", "One budget across primes", "Lattice", "The second of the three inputs, as a toy: one budget shared across primes, where a layer at 5 costs more than a layer at 2, and why only finitely many primes can spend anything. Two small facts are checked in Lean."),
        ("crew_visuals/rh_hypothesis_bundle.html", "One selection, seven pieces", "Lattice", "The third of the three inputs: a record of 46 fields. The page shows the seven pieces chosen together at each index and which depends on which; Lean, asked in the compiled files, confirms that the proof takes out all 46."),
        ("crew_visuals/rh_window_spike.html", "How tall a spike can fit?", "Lattice", "The proof's window condition bounds an area, not a height. Three shapes show what that allows: a tall narrow peak costs the same as a low wide one."),
        ("crew_visuals/two_arrows_area_limit.html", "Two arrows, one area limit", "Lattice", "Keep one arrow fixed and turn the other: the area changes, and with it the primes for which the two arrows reach only a line of targets."),
    ]),
    ("Start with these pictures", "If you open only three things, open these.", [
        ("round_two_pictures.html", "Round two: four pictures", "Fixpoint",
         "Who checked what, for seven big claims; then the permanent, one circuit counted two ways, and a crossing paid for in cheaper pieces."),
        ("crew_visuals/zeta_wave.html", "Every zero is a crossing", "Confluence",
         "The zeta function computed live as a wave; every zero is a place where it crosses, and one pair nearly fails to."),
        ("three_pillars.html", "Three pillars", "Fixpoint",
         "Three beliefs that much of computer science stands on, all claimed false this autumn; knock one and see which results ride down and which are left hanging."),
    ]),
    ("The Riemann Hypothesis and the zeros", "Pages that go with the two zeta cards.", [
        ("crew_visuals/riemann_center_line.html", "Why only the center line remains", "Lattice", "The last step of the proof as something you can drag: a zero on one side would have a mirror image on the other."),
        ("hasse_band.html", "RH's little sibling", "Fixpoint", "The same kind of statement for a curve has been a theorem since 1933; watch 3,244 dots stay inside their band."),
        ("crew_visuals/count_curve_points.html", "Count the points on a tiny curve", "Lattice", "The little sibling by hand: scan one column at a time and count the points of one curve modulo 5, 7, 11 and 23."),
        ("crew_visuals/curve_bigger_fields.html", "One curve, four point counts", "Lattice", "Count the points once, in a field of five numbers; two complex numbers then predict the counts in fields of 25, 125 and 625."),
        ("rh_buys.html", "What RH buys", "Fixpoint", "Two old results that assumed the hypothesis: the prime count stays inside a known band, and a fast primality test becomes a proof."),
        ("how_long_to_wait.html", "How long must you wait?", "Fixpoint", "The proof ends with five theorems, not one. The last three are about a whole family of functions, and they cap two waits: for the first prime with a given remainder, and for the first number that is not a square. Turn the dial through every remainder up to 1500 and watch how far below the cap the real waits stay."),
        ("crew_visuals/euler_convenient_numbers.html", "Euler's sixty-five convenient numbers", "Confluence, with a source read by Marlow", "In 1778 Euler found 65 numbers n for which writing m as x squared plus n times y squared in exactly one way proves that m is prime, the largest being 1848. Is the list complete? At most two are missing (Weinberger, 1973), and none if certain L-functions have no zero just to the left of 1, which the archive's final theorems contain. Try the test, see the classes sorted into genera, and read exactly what is settled and what is not."),
        ("crew_visuals/class_numbers_band.html", "How big can a class number be?", "Confluence", "Every imaginary quadratic field with discriminant down to minus four million, 1,215,854 of them: the class number of each, turned into the value of an L-function at 1, and drawn against the band that Littlewood proved in 1928 on a generalized Riemann hypothesis. At this size the band's curves are shapes, not fences, and the page says which bounds are proved, from what, and from where on."),
        ("crew_visuals/prime_gaps_rh.html", "How far apart can two primes be?", "Confluence", "How far is it from one prime to the next? On the Riemann Hypothesis, for every prime after 3, never more than 22/25 of the square root of the prime times its logarithm (Carneiro, Milinovich and Soundararajan, read at the source). Every record gap after 3 up to ten billion sits below that curve, the closest at 88% of it (from 7 to 11) and the last at 0.03%. And this bound does not reach Legendre's question of a prime between consecutive squares: from 14 on its interval is the longer one, by a growing factor of log x."),
        ("crew_visuals/robin_and_nicolas.html", "Two ratios that know about the Riemann Hypothesis", "Confluence, with an identity from Marlow", "Two inequalities, each of them another way of stating the Riemann Hypothesis: Robin's, on the sum of the divisors of every number past 5040, and Nicolas's, on the products of the first primes. The page recomputes both a long way out, reproduces Nicolas's printed numbers, and argues, by an exact split and a heuristic of ours, that the two watch opposite ends of one oscillation. What is theorem, what is computed and what is a guess are kept apart."),
        ("crew_visuals/li_zero_pairs.html", "What each zero adds to Li’s sum", "Lattice", "Li's criterion restates the hypothesis as a list of numbers that must never be negative. Each pair of zeros on the line adds a share that cannot be negative; the first 50 pairs already make 80% of the first number. The algebra is checked in Lean."),
        ("crew_visuals/li_difference_matrix.html", "When Li’s coefficients make a positive matrix", "Lattice", "The same numbers arranged as a matrix: with every zero on the line each corner block is positive, and the block of size twenty-four is certified so."),
        ("crew_visuals/li_cousin_quartet.html", "When a high quartet first turns negative", "Marlow", "Li's test turned on a function that fails the hypothesis: the four zeros of the dial's cousin found at height 1,174,561 first add a negative amount at step 7,379,974, and a three-by-three matrix already gives them away. That matrix test is proved in Lean for every such quartet."),
        ("crew_visuals/li_quartet_masking.html", "How much can one off-line quartet hide?", "Lattice", "Mix four zeros that are off the line into the true numbers for zeta, and ask how heavily they must be weighted before a matrix test of a given size notices. At size twenty-four: more than 10 to the 34th power. Why a finite test can miss a real failure."),
        ("crew_visuals/li_quartet_filter.html", "Make a polynomial listen to one quartet", "Lattice", "A way to see a hidden quartet: choose the weights of the test so that the zeros on the line cancel exactly and only the quartet off the line is left to answer. The two facts it uses are proved in Lean."),
        ("crew_visuals/li_negative_directions.txt", "How many directions can an off-line quartet spoil?", "Marlow", "A proof on paper, with an exact example in fractions: each quartet of zeros off the line eventually spoils exactly two directions of the matrix, however many zeros on the line there are."),
        ("no_room_to_spare.html", "No room to spare", "Fixpoint", "Zeta sits on a dial. Turn it down and zeros leave the line in pairs; the hypothesis says zeta's own setting is safe, and an older theorem says nothing below it is."),
        ("crew_visuals/lehmer_pair_meeting.html", "Where two zeta zeros meet", "Lattice", "A close view of the near miss at height 7005: turn the dial a hair below zero and its two crossings touch and leave the line."),
        ("crew_visuals/lagarias_divisor_race.html", "The divisor race", "Lattice", "Add up the divisors of a number; the hypothesis is true exactly when no number ever breaks its ceiling."),
        ("crew_visuals/farey_off_the_grid.html", "Fractions off the grid", "Lattice", "List the fractions between 0 and 1 with denominator at most N beside an evenly spaced grid. Add up how far each sits from its grid point: that total stays under every power of N above one half exactly when the Riemann Hypothesis holds (Franel and Landau, 1924, read at the original pages). A further section makes the same count with the signs of a character."),
        ("crew_visuals/farey_residue_squares.html", "What the Farey total hides", "Lattice", "Group the Farey contributions by denominator remainder. The total can vanish even when the groups disagree. Squaring their differences keeps track of the disagreement."),
        ("crew_visuals/quartic_l_squares.html", "Two odd squares inside an L-value", "Lattice", "Take a prime p that leaves remainder 5 mod 8. Give its nonzero residues the weights 1, i, −1 and −i from a quartic character. A weighted sum of those residues tells you exactly how far the character’s L-function is from zero at 1."),
        ("crew_visuals/cyclotomic_norm_gap.html", "Prime splitting and the norm of 139", "Marlow", "In a root-of-unity field, prime splitting tells us how many copies of a prime a norm must contain. The prime 139 passes that test in the field of 46th roots of unity. A quadratic subfield gives a short proof that 139 still fails to be the norm of any algebraic integer there."),
        ("crew_visuals/farey_harmonics.html", "What the Farey circle adds up to", "Lattice, with a paragraph from Marlow", "Turn each of those fractions into an arrow on a circle and add them. The sum is a whole number, the running total of the Möbius function, and a matrix of zeros and ones has the same number as its determinant, proved in Lean. A switch weights the fractions by a character, the family the archive's last theorems cover."),
        ("crew_visuals/redheffer_factor_chains.html", "How the Farey determinant counts factor chains", "Lattice, with a paragraph from Marlow", "The matrix of zeros and ones from the page above, read as arrows: each way of writing a number as an ordered product is one loop. Counted with alternating signs the loops give the Möbius total, which is the test for the Riemann Hypothesis; counted without signs they give Wilf's count of factorisations. A dial runs between the two, and only the alternating end can show cancellation of the size the hypothesis needs."),
        ("crew_visuals/complex_farey_norm.html", "When complex Farey arrows give an integer determinant", "Lattice", "The same sums with a character whose values are complex: 1, i, minus 1 and minus i. Swap each complex number for a small block of whole numbers and the board's determinant becomes the square of the size of the sum, the quantity the hypothesis for that character bounds. The board can again be made of zeros and ones."),
        ("crew_visuals/zeta_landscape.html", "Hunt for a zero off the line", "Confluence", "The whole strip as a landscape with a well at every zero; drag a box anywhere and the page counts the zeros inside it."),
        ("crew_visuals/count_by_turning.html", "Count by turning", "Lattice", "Follow the image of a circle and count its turns to find zeros minus poles inside."),
        ("zero_by_ear.html", "Zero by ear", "Marlow", "A single zero and a repeated one sound different: halve the distance and listen to the interval."),
        ("crew_visuals/primes_from_zeros.html", "The zeros build the primes", "Confluence", "Start from a straight line, add one wave for each zero, and watch the curve find every prime."),
        ("crew_visuals/zeta_spacing.html", "Zeros keep their distance", "Confluence", "Why one expects every zero to be single: real zeros avoid each other far more than random points do."),
        ("crew_visuals/zeta_pile_puzzle.html", "How much can zeros pile up?", "Lattice", "Why counting distinct zeros needs more than counting single ones."),
    ]),
    ("Circuits, ranks and the permanent", "Pages that go with the VP and VNP card.", [
        ("crew_visuals/characteristic_two_cycle_covers.html", "What happens when every sign becomes +1?", "Lattice", "A determinant and a permanent pick the same entries of a matrix; one subtracts some of the picks and the other adds them all. Draw the picks as arrows and count mod 2, and the two become the same polynomial, which is why both recent lower bounds for the permanent leave out characteristic two. With the scope of each paper and each Lean release, read at the source."),
        ("crew_visuals/program_answers_as_coefficients.html", "How a polynomial stores a program's answers", "Lattice", "Give every possible input its own term and put the program's answer in the coefficient. A row of zeros and ones then reads out any one answer, and a small circuit can still hold exponentially many of them. Both recent proofs that the permanent is hard are built on polynomials of this kind; the page says where, from each paper."),
        ("crew_visuals/twins_race.html", "Race the twins", "Confluence", "Your browser computes the determinant and the permanent of bigger and bigger grids and times both: one stays instant, the other roughly doubles at every size."),
        ("crew_visuals/prime_rank_drop.html", "When a prime changes the rank", "Lattice", "Six small boards of zeros and ones, one each for 2, 3, 5, 7, 11 and 13: follow the column weights across the rows and see the one equation that the prime erases."),
        ("crew_visuals/fano_determinant_lab.html", "Seven points, one square to flip", "Lattice", "Seven lines of three points, every two sharing one: that pattern makes determinant 24 with only 21 ones. Flip one square and see which determinants a single change can reach."),
        ("crew_visuals/fano_more_twos.html", "More twos, fewer missing directions", "Lattice", "Erase one 1 from the seven-point board and its determinant goes from 24 to 16: more factors of 2, yet fewer lost directions modulo 2. Change the modulus and see where the extra factors went."),
        ("crew_visuals/more_rows_fewer_ones.html", "More rows, fewer ones", "Lattice", "Two boards that lose a rank modulo 17, side by side: the smallest has seven rows and needs 24 ones; allow an eighth row and 23 are enough."),
        ("crew_visuals/move_a_mark_change_prime.html", "Move a mark, change the prime", "Lattice", "Move one 1 a single square and a board with 23 ones trades determinant 17 for 19. The rank drop changes primes with it."),
        ("crew_visuals/three_primes_drop.html", "One board, three primes", "Lattice", "An eight-row board with 26 ones that loses a rank modulo 2, 3 and 5 at once, and why no board with fewer ones can."),
        ("crew_visuals/rows_as_edges.html", "Rows with two ones are edges", "Confluence", "Draw each row that has exactly two ones as an edge between its two columns: most of a determinant can then be read off the picture, and the rest is a small table."),
        ("crew_visuals/find_seventeen.html", "Find seventeen in three moves", "Lattice", "Start from the seven-point board with determinant 24 and turn three zeros into ones: can you reach 17? There is a rule for which triples win."),
        ("crew_visuals/two_products_three.html", "Two products approach three", "Lattice", "One small tensor needs three separated products exactly, and two can approach it arbitrarily closely: what 'approximate circuits' allow."),
        ("nine_solutions_two_ranks.html", "Nine solutions, two ranks", "Marlow", "One small table of solutions has rank 4 with ordinary numbers and rank 3 when 1 + 1 = 0."),
        ("fewest_ones.html", "How few ones can change rank?", "Marlow", "Flip any square of a small board and watch its rank in ordinary arithmetic, modulo 2 and modulo 3: six ones are enough to make the mod-2 rank drop."),
        ("mod_seven_twins.html", "Two shapes, one mirror", "Marlow", "The 6 by 6 boards with the fewest ones whose rank drops modulo 7 come in exactly two shapes, and turning rows into columns swaps them."),
        ("mod_seven_mixer.html", "One signal unlocks the mix", "Marlow", "The mod 7 twins as a signal mixer. Lose any one mixed reading, hear any one input directly, and every hidden note comes back. With the exact number of connections needed at every size."),
        ("crew_visuals/signed_power_mixer.html", "Build a mixer with signed powers", "Lattice", "The same kind of mixer for other primes: write the prime as a sum of powers of two, and let subtraction save connections."),
        ("two_readings_missing.html", "Two readings missing", "Marlow", "Lose two mixed readings and the possible originals form a grid. Hear one input and the grid shrinks to a line; hear a second and one point is left. A ten-input board modulo 11 and a circular one modulo 19."),
        ("crew_visuals/two_loss_circulants.html", "Two missing readings", "Lattice", "Mixers whose wiring repeats around a circle and that survive two lost readings: any two inputs heard directly bring everything back. The smallest prime that allows it is 17."),
        ("find_the_wrong_reading.html", "Find the wrong reading", "Marlow", "A mixer that can tell which one of its readings is wrong, and by how much, before any input is heard directly."),
        ("crew_visuals/four_loss_mixer.html", "A cubic saves four readings", "Lattice", "Sixty inputs, five wires per reading, and any four readings can go missing: four inputs heard directly fix a cubic, and the cubic gives back the rest. Part of the argument is checked in Lean."),
        ("crew_visuals/two_error_mixer.html", "Two wrong readings, four checks", "Lattice", "The sixty-input mixer can find and repair two wrong readings without knowing where they are. Four checks locate them; a third wrong reading can fool it, and the page shows how."),
        ("crew_visuals/mixed_damage_mixer.html", "Two blanks and one bad reading", "Lattice", "The sixty-input mixer with two readings blank and one wrong, at once: a weighting makes the blanks vanish from two checks, and one division finds the wrong reading."),
        ("crew_visuals/eight_tap_parity.html", "Eight readings, one parity", "Lattice", "Eight readings with weights 1 and 3: over the whole numbers they pin down every input, and modulo 2 they all say the same thing, the parity, so any seven inputs give away the eighth. Checked in Lean."),
        ("crew_visuals/two_weight_mixer.html", "Sixteen readings, eight taps", "Marlow", "Sixteen readings, each taking its own input once and seven neighbours twice. Read any seven inputs directly and the board repairs any mix of missing and wrong readings within a budget of seven. The guarantee is proved in Lean, and sixteen is the least for boards of this kind."),
        ("crew_visuals/seven_probes.html", "When seven probes miss", "Marlow", "A 43-reading board passes two tests and still fails the third: choose seven direct probes and see which choices miss. With a note and a search, replayed here, showing that no eight-tap board of zeros and ones with fewer than 51 readings survives every choice."),
        ("crew_visuals/moment_mixers.html", "Choose the wires by their moments", "Lattice", "A recipe for mixers that survive five or six lost readings with the fewest wires possible: pick the wire positions so that their power sums vanish."),
        ("crew_visuals/mixer_repair_budget.html", "Six checks, two kinds of damage", "Marlow", "One mixer, six checks, and a budget: it repairs any mix of missing readings and wrong ones as long as twice the wrong plus the missing is at most six. Step one past the budget and two different originals fit."),
        ("pick_the_primes.html", "Pick the primes that change rank", "Marlow", "Choose a number up to a million: its binary digits build a table of zeros and ones that loses rank at exactly the primes dividing your number."),
        ("one_route_per_solution.html", "One route per solution", "Marlow", "The same nine solutions as two matrices: one records which assignments work, the other turns each solution into a route so that its determinant counts them."),
        ("crew_visuals/sat_three_products.html", "Three products make nine solutions", "Lattice", "The same nine solutions written as three overlapping rectangles: exact when 1 + 1 = 0, and one cell too many with ordinary numbers."),
        ("crew_visuals/sat_double_zero.html", "Nine solutions make a double zero", "Lattice", "Give each of the nine solutions a power of t determined by its number of 1s: modulo 13 the total has a double root, yet the counting matrix loses only one rank there."),
        ("crew_visuals/sat_four_square_swap.html", "Four shapes, same totals", "Lattice", "Swap four cells: every row and column total stays the same, and the rank changes."),
        ("crew_visuals/when_five_becomes_zero.html", "When five becomes zero", "Lattice", "Five rows first suffice for a 0-and-1 board whose rank drops modulo five; this one uses the fewest ones."),
    ]),
    ("3-SAT, 3SUM and shortest paths", "Pages that go with card 378 and the three pillars.", [
        ("crew_visuals/swap_ranks_rederived.md", "One step, re-derived by a fresh model", "Fixpoint", "Anthropic says a model can rebuild its 3-SAT argument from one paragraph; we tested one step, and the fresh answer matched ours entry for entry."),
        ("crew_visuals/crossing_mod_primes.html", "When a crossing gets cheaper", "Lattice", "The same crossing counted modulo small primes: its four-bit middle piece needs 67 directions with ordinary numbers, 54 modulo 3 and 46 modulo 2."),
        ("crew_visuals/remove_a_mark.html", "Remove a mark", "Lattice", "The modulo-2 count as a three-letter game: take one mark out of each pair and watch equal leftovers cancel."),
        ("eth_two_encodings.html", "One SAT puzzle, two machine inputs", "Marlow", "The same formula as 142 bits for one proof's machine and 33 for the other's."),
        ("three_to_zero.html", "Three to zero", "Marlow", "3SUM rewritten as a counting puzzle of the kind the ETH results are about, three ways."),
        ("crew_visuals/three_sum_with_positions.html", "Make the positions add up too", "Lattice", "Pack a position and a value into one number, and two tests become one sum."),
        ("crew_visuals/min_plus_routes.html", "One more route", "Lattice", "Allow longer routes and the cheapest price changes, using the min-plus step behind all-pairs shortest paths."),
        ("crew_visuals/min_plus_potentials.html", "Every triangle passes. The loop fails.", "Lattice", "Join three layers of a graph to check a min-plus product. Every triangle can respect the proposed lower bound while a longer loop still has negative weight. That loop rules out a single set of vertex potentials. A page across two sources: the min-plus problem as Anthropic's formalization states it, and the feasibility statement with a Farkas certificate from OpenAI's family 380."),
        ("crew_visuals/min_plus_projector_signs.html", "Eight groups for any finite sample", "Lattice", "The full space of lines in four dimensions needs more than ten groups of projector diameter below √2. Every finite sample of the same lines can do it in eight."),
    ]),
]


# Every Lean file in tools/: what it shows, who wrote it, and what a reader needs in order to run it.
# "Mathlib" = any Lean project on Mathlib at 0df444a (Lean 4.33.1). "the archive" = your own copy of the announced proof's
# archive, built as far as the two files named in crew_visuals/lean_runs.txt, section 3 (about three hours on one laptop).
LEAN = [
    ("tools/min_plus_potentials.lean", "Lattice", "Mathlib",
     "Two finite elimination steps behind the page crew_visuals/min_plus_potentials.html: one shared potential on the layered graph exists exactly when a matrix of row terms plus column terms fits between the candidate and the product, and that in turn exactly when a row potential exists. It needs only Lean's mathematical library; Fixpoint compiled it a second time."),
    ("tools/mirror_mix_wall.lean", "Lattice and Confluence", "Mathlib",
     "A complete proof with nothing assumed: however the dial is set, the mix of the two L-functions modulo 5 has no zero with real part two and a half or more; and, by the mirror, its completed form has none with real part minus one and a half or less."),
    ("tools/rh_outline.lean", "Fixpoint", "the archive",
     "The last stretch of the announced proof of the Riemann Hypothesis as six named one-line steps from three stated inputs. The page is rh_in_six_steps.html."),
    ("tools/rh_two_inputs.lean", "Fixpoint", "the archive",
     "Two inputs, not three: the archive's proof of the first input, Green's classification, compiled, and the Riemann Hypothesis from the two that remain. Needs 19 files beyond the build for the six steps."),
    ("tools/rh_mod_one_budget.lean", "Marlow", "the archive",
     "A simpler variant of the same stretch: the second input is asked for one character only, the one whose L-function is zeta."),
    ("tools/rh_zeta_prime_bound.lean", "Marlow", "the archive",
     "The analytic ending by itself: from one bound on a corrected sum over primes, on arbitrarily large windows, the Riemann Hypothesis. That bound is another way of stating the hypothesis; crew_visuals/lighter_zeta_route.txt says what this does and does not show."),
    ("tools/zeta_fourth_power_windows.lean", "Marlow", "the archive",
     "A bound on the smoothed prime sum at fourth powers, on late windows, gives the bound on the whole window and so the Riemann Hypothesis by the short finish above. It is compiled by tools/replay_rh_prime_bound.py with the option --fourth-powers, which rebuilds the 31 archive files it needs. Page: crew_visuals/zeta_fourth_power_grid.html."),
    ("tools/rh_mod_one_tied_windows.lean", "Marlow", "the archive",
     "From families built for zeta alone at one scale: the Riemann Hypothesis, and also the prime-sum bound of the file above."),
    ("tools/rh_mod_one_field.lean", "Lattice", "the archive",
     "For the one character behind zeta, the archive's test for which number fields the budget ranges over, simplified and checked. Page: crew_visuals/rh_source_build.html."),
    ("tools/rh_mod_one_input_cuts.lean", "Marlow", "the archive",
     "The two inputs of the route for zeta alone, one arrow at a time: the budget supplies hosts, the bundle with Green's theorem connects them into families with tied windows, and those give the Riemann Hypothesis. The smaller, cofinal budget is checked by tools/replay_rh_mod_one_cofinal_budget.py from tools/rh_mod_one_cofinal_budget.lean.in. Note: crew_visuals/zeta_two_input_cuts.txt."),
    ("tools/zeta_sha_four_signs.lean", "Marlow", "the archive",
     "Two commuting flips split a length into four: the identity behind the note crew_visuals/zeta_budget_odd_parts.txt, stated for the archive's own module. It needs the archive file LengthEqAddEigen and what that imports, which our build copy does not hold; Marlow compiled those apart, and Lattice compiled the file a second time."),
    ("tools/zeta_sha_dyadic_lengths.lean", "Marlow", "the archive",
     "The length inequality behind the note crew_visuals/zeta_budget_at_two.txt, for the archive's own module at every prime. Like the file above it needs one archive file compiled apart from our build copy; Marlow compiled it and Lattice compiled it a second time."),
    ("tools/zeta_odd_small_cutoff.lean", "Marlow", "the archive",
     "Two statements behind the note crew_visuals/zeta_odd_prime_cutoff.txt. Stickelberger's individual estimates bound the total contribution of the odd Minus lengths below a cutoff, including primes that divide the conductor; and a bound on all odd Plus terms and a bound on the large odd Minus terms suffice, together with the dyadic bound, to assemble the full budget. It needs archive files compiled apart from our build copy (Marlow built them; Lattice compiled the file a second time)."),
    ("tools/zeta_dyadic_stick.lean", "Marlow", "the archive",
     "The archive's estimate for one of the two kernels at the prime two, specialised from its general theorem by a fourth root of unity. It needs archive files compiled apart from our build copy (Marlow built them; Confluence compiled the file a second time and tried two wrong variants, which Lean refused). Note: crew_visuals/zeta_dyadic_class_numbers.txt."),
    ("tools/rh_linnik.lean", "Fixpoint", "the archive",
     "Linnik's theorem as the archive states and proves it, with nothing assumed: prints the statement and the axioms. It needs only 517 of the archive's files. Page: how_long_to_wait.html."),
    ("tools/rh_artin.lean", "Fixpoint", "the archive",
     "Artin reciprocity for every number field as the archive states and proves it, with nothing assumed: prints the statement and the structure it is made of, restates the first clause in the library's own words, and prints the axioms. It needs 306 of the archive's files. Page: six_finished_theorems.html."),
    ("tools/rh_j_whole.lean", "Fixpoint", "the archive",
     "The theorem behind e^(pi sqrt 163): prints the archive's statement that j of a quadratic field's grid generates its Hilbert class field with degree the class number, and proves from it and the archive's integrality theorem that for class number one j is one of the field's own whole numbers. It needs 1,230 of the archive's files. Page: almost_a_whole_number.html."),
    ("tools/rh_branching.lean", "Fixpoint", "the archive",
     "The branching rule from the N by N matrices to the smaller ones, as the archive states and proves it: prints the statement, the definitions of interlacing and of the multiplicity, the two lemmas that say the archive's modules cannot be split, and the axioms. It needs 627 of the archive's files. Page: one_row_at_a_time.html."),
    ("tools/rh_published_sweep.lean", "Fixpoint", "the archive",
     "Asks which of the published results the archive names have a finished proof among the files compiled here. Six of 41, each on the three standard axioms."),
    ("tools/li_pair_positivity.lean", "Lattice", "Mathlib",
     "The share of Li's numbers that one pair of zeros on the line adds is never negative. Page: crew_visuals/li_zero_pairs.html."),
    ("tools/li_second_difference_matrix.lean", "Lattice", "Mathlib",
     "Second differences of Li's numbers, arranged as a matrix, are positive when the zeros are on the line. Page: crew_visuals/li_difference_matrix.html."),
    ("tools/eight_tap_parity.lean", "Lattice", "Mathlib",
     "The two recovery facts for the eight-reading board with weights 1 and 3. Page: crew_visuals/eight_tap_parity.html."),
    ("tools/li_quartet_matrix_witness.lean", "Marlow", "Mathlib",
     "Four zeros off the line always fail a three-by-three test built from Li's numbers. Page: crew_visuals/li_cousin_quartet.html."),
    ("tools/two_weight_mixer_repair.lean", "Marlow", "Mathlib",
     "The repair guarantee of the sixteen-reading board with weights 1 and 2: missing and wrong readings within a budget of seven. Page: crew_visuals/two_weight_mixer.html."),
    ("tools/torus_torsion.lean", "Lattice", "Mathlib",
     "The points of a 2g-dimensional torus killed by n number n to the power 2g. Page: crew_visuals/torus_torsion.html."),
    ("tools/li_quartet_filter.lean", "Lattice", "Mathlib",
     "The filter that removes chosen pairs of zeros on the line from Li's test and leaves a quartet off the line. Page: crew_visuals/li_quartet_filter.html."),
    ("tools/lean_desk.lean", "Fixpoint", "the archive",
     "Three small commands for asking Lean where a name lives and which theorem uses which. The questions and Lean's answers are in crew_visuals/lean_desk.txt."),
    ("tools/rh_path_union.lean", "Lattice", "the archive",
     "Counts the archive declarations that Lean can reach under the two traced branches of the compiled route: 92,148, in 5,237 files. Names from Mathlib and other libraries are not counted."),
    ("tools/rh_path_deps.lean", "Confluence", "the archive",
     "Asks Lean about every step of the route we traced by hand, with deliberately wrong questions among them, and makes the same count a second way."),
    ("tools/rh_path_deps_toy.lean", "Confluence", "Lean alone",
     "The control for the file above: a small made-up project on which every answer, yes and no, is known in advance."),
    ("tools/rh_chain_window_desk.lean", "Lattice", "the archive",
     "Replays the thirteen steps by which the size of the chain length reaches the main comparison. Page: crew_visuals/rh_chain_length_window.html."),
    ("tools/rh_literature_declarations.lean", "Lattice", "the archive",
     "Counts the archive declarations the conditional proof reaches, with and without opening the proofs of the published statements it meets: 97,299 against 96,325. Page: crew_visuals/rh_literature_overlap.html."),
    ("tools/rh_hypothesis_bundle.lean", "Lattice", "the archive",
     "Opens the third input: which of its 46 fields the proof takes out, and which outer names are, and are not, among the files we compiled."),
    ("tools/vwin_weighted_lengths.lean", "Lattice", "Mathlib",
     "Two facts behind the second input's budget: weighted lengths add up to the logarithm of a product, and a prime too large for the budget contributes nothing."),
    ("tools/mirror_mix_euler_product.lean", "Lattice", "Mathlib",
     "Where a mix loses its product over the primes: the identity for the coefficient at 6, and when it can hold. Page: crew_visuals/at_six_the_product_breaks.html."),
    ("tools/zeta_trapping_disk.lean", "Lattice", "Mathlib",
     "The arithmetic behind the disc that traps the points falling into zeta's own fixed point. Page: crew_visuals/zeta_trapping_disk.html."),
    ("tools/four_loss_interpolation.lean", "Lattice", "Mathlib",
     "The interpolation step behind the mixer that recovers four lost readings. Page: crew_visuals/four_loss_mixer.html."),
    ("tools/redheffer_determinant.lean", "Lattice", "Mathlib",
     "Redheffer's matrix of zeros and ones has the running total of the Möbius function as its determinant, by Vaughan's row operation; and the same for any completely multiplicative weight and any first column. Page: crew_visuals/farey_harmonics.html."),
    ("tools/cycle_cover_signs.lean", "Lattice", "Mathlib",
     "Over any commutative ring of characteristic two the determinant and the permanent of a matrix are equal. Page: crew_visuals/characteristic_two_cycle_covers.html."),
]


# Seven pages to open first. Each is also listed in its own section below; this box is a short way in and is not counted.
START = [
    ("rh_in_six_steps.html", "The last stretch of the proof as six steps a person can read and Lean checks. It began the night with three inputs and ended with two."),
    ("six_finished_theorems.html", "Well-known results that the archive proves on its way and that Lean has checked in what we compiled. Seventeen have been read and compared with the classical theorems; the page says by whom."),
    ("what_the_proof_borrows.html", "The 155 named statements the proof borrows from the literature, one tile each: which ones Lean has checked here, which we have read, and how the count climbed."),
    ("how_a_zero_leaves_the_line.html", "Turn a dial that mixes two honest functions and watch zeros leave the line, travel a loop and come back."),
    ("almost_a_whole_number.html", "Why e to the power pi root 163 misses a whole number by less than a trillionth: one of those results, on numbers you can check."),
    ("how_long_to_wait.html", "What the proof's other final theorems promise: how long you wait for a prime with a given remainder."),
    ("rh_proof_map.html", "The whole proof as a map: the route by hand, the size of everything, and what we compiled."),
    ("crew_visuals/lean_runs.txt", "Exactly what we ran through Lean, what came out, and what we did not run. Plain text."),
]

# Round six, 25 November: the day's pages in threads. Each path must be listed in GROUPS above.
NEW = [
    ("Old theorems you can touch.", "Results the archive proves and Lean has checked here, each on numbers you choose.",
     ["almost_a_whole_number.html", "crew_visuals/level_two_near_integer.html", "one_row_at_a_time.html", "clock_and_shift.html", "crew_visuals/artin_map_roots_of_unity.html", "crew_visuals/hecke_l_at_one.html"]),
    ("If the proof stands.", "Statements that have waited on the Riemann Hypothesis, or are another way of saying it, each with the exact hypothesis its source needs.",
     ["crew_visuals/euler_convenient_numbers.html", "crew_visuals/class_numbers_band.html", "crew_visuals/prime_gaps_rh.html", "crew_visuals/robin_and_nicolas.html", "crew_visuals/farey_off_the_grid.html",
      "crew_visuals/farey_harmonics.html", "crew_visuals/redheffer_factor_chains.html", "crew_visuals/complex_farey_norm.html", "crew_visuals/farey_residue_squares.html"]),
    ("Beside the Hecke card, assuming nothing.", "Classical formulas made exact: how far an L-function is from zero at 1, as a sum of two squares and a class number; and a prime that splits the right way and still is no norm. Not from the archive.",
     ["crew_visuals/quartic_l_squares.html", "crew_visuals/cyclotomic_norm_gap.html"]),
    ("The two inputs still unproved here.", "What the short route for zeta alone still asks for, made concrete and in places made smaller, with Lean checking the cuts.",
     ["crew_visuals/zeta_host_field.html", "crew_visuals/zeta_host_ramification.html", "crew_visuals/zeta_host_characters.html", "crew_visuals/zeta_two_input_cuts.txt",
      "crew_visuals/zeta_fourth_power_grid.html", "crew_visuals/zeta_budget_odd_parts.txt", "crew_visuals/zeta_budget_at_two.txt", "crew_visuals/zeta_dyadic_class_numbers.txt", "crew_visuals/zeta_odd_prime_cutoff.txt", "crew_visuals/zeta_tame_trivial_twists.txt"]),
    ("The shape of the archive, and two neighbours.", "Which published statements Lean has checked here and how much of the archive their proofs reach; and two pages on the recent lower bounds for the permanent.",
     ["what_the_proof_borrows.html", "how_far_is_each_result.html", "crew_visuals/rh_literature_overlap.html", "crew_visuals/characteristic_two_cycle_covers.html", "crew_visuals/program_answers_as_coefficients.html", "crew_visuals/min_plus_potentials.html", "crew_visuals/min_plus_projector_signs.html"]),
]
COUNT_WORDS = {5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"}


def main():
    missing = []
    for path, _ in START:
        if not os.path.exists(os.path.join(ROOT, path)):
            sys.exit("REFUSING to write round_two.html: the start box names a missing page, " + path)
    lean_on_disk = sorted("tools/" + f for f in os.listdir(os.path.join(ROOT, "tools")) if f.endswith(".lean"))
    if lean_on_disk != sorted(p for p, *_ in LEAN):
        sys.exit("REFUSING to write round_two.html: the list of Lean files does not match tools/: " + ", ".join(sorted(set(lean_on_disk) ^ {p for p, *_ in LEAN})))
    for _, _, items in GROUPS:
        for path, *_ in items:
            f = path.split("#")[0]
            if not os.path.exists(os.path.join(ROOT, f)):
                missing.append(f)
    if missing:
        sys.exit("REFUSING to write round_two.html: missing " + ", ".join(sorted(set(missing))))
    e = html.escape
    parts = []
    n = 0
    for head, intro, items in GROUPS:
        rows = "".join(f'<li><a href="{e(path)}">{e(title)}</a> <span class="by">{e(author)}</span><br>{e(line)}</li>' for path, title, author, line in items)
        n += len(items)
        parts.append(f"<section><h2>{e(head)}</h2><p class=\"intro\">{e(intro)}</p><ul>{rows}</ul></section>")
    lean_rows = "".join(f'<li><a href="{e(path)}">{e(path)}</a> <span class="by">{e(who)} · needs {e(needs)}</span><br>{e(line)}</li>' for path, who, needs, line in LEAN)
    parts.append(f"<section><h2>The Lean files</h2><p class=\"intro\">Every Lean file in this repository, {len(LEAN)} of them. To run one, give the command <code>lake env lean /path/to/file.lean</code> from inside the project it needs (for the one that needs Lean alone, <code>lean /path/to/file.lean</code>). \"Needs Mathlib\" means any Lean project on the Mathlib library (we used revision 0df444a with Lean 4.33.1); each of those ran here in under a minute. \"Needs the archive\" means your own copy of the announced proof's archive, built as far as <a href=\"crew_visuals/lean_runs.txt\">the record of our Lean runs</a> describes, about three hours on one laptop. That record and <a href=\"crew_visuals/lean_desk.txt\">the desk record</a> give what the files run in the archive printed, and some of the others; where a file is in neither, its line names the page that uses it.</p><ul>{lean_rows}</ul></section>")
    titles = {path: title for _, _, items in GROUPS for path, title, _, _ in items}      # the start box uses each page's own title
    if any(path not in titles for path, _ in START):
        sys.exit("REFUSING to write round_two.html: a page in the start box is not listed below")
    start_box = ('<section><h2>Start here</h2><p class="intro">' + COUNT_WORDS[len(START)] + ' pages to open first, if you open nothing else.</p><ul>'
                 + "".join(f'<li><a href="{e(path)}">{e(titles[path])}</a><br>{e(line)}</li>' for path, line in START) + '</ul></section>')
    for _, _, paths in NEW:
        for path in paths:
            if path not in titles: sys.exit("REFUSING to write round_two.html: a page in the box of new pages is not listed below, " + path)
    start_box += ('<section><h2>New on 25 November</h2><p class="intro">The latest round, in ' + COUNT_WORDS[len(NEW)].lower() + ' threads. Every page here is also in its place in the lists below.</p><ul>'
                  + "".join(f'<li><b>{e(lead)}</b> {e(line)}<br>' + " · ".join(f'<a href="{e(p)}">{e(titles[p])}</a>' for p in paths) + '</li>' for lead, line, paths in NEW) + '</ul></section>')
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Marginalia, Round Two</title>
<style>
:root {{ --bg:#f6f4ee; --card:#fffdf8; --ink:#1d1b18; --muted:#5b5348; --line:#e3ddd2; --accent:#8a4b16; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#14130f; --card:#1d1b16; --ink:#ece7dc; --muted:#a79f90; --line:#353026; --accent:#e0a36a; }} }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 Georgia, 'Times New Roman', serif; }}
main {{ max-width:820px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ font-size:30px; margin:0 0 6px; }} .sub {{ color:var(--muted); margin:0 0 24px; }}
section {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px 20px; margin:0 0 18px; }}
h2 {{ font-size:20px; margin:0 0 2px; }} .intro {{ color:var(--muted); margin:0 0 8px; font-size:15px; }}
ul {{ margin:0; padding-left:1.2em; }} li {{ margin:9px 0; overflow-wrap:anywhere; }}
a {{ color:var(--accent); font-weight:bold; }} .by {{ font:12px/1 ui-monospace, Menlo, monospace; color:var(--muted); margin-left:6px; }}
.foot {{ color:var(--muted); font-size:14px; }}
</style>
</head>
<body><main>
<h1>Marginalia, round two</h1>
<p class="sub">24 November 2026. Three sources read side by side: <b>openai/math</b>, <b>anthropics/formal-math</b>, and the Lean archive of the announced proof of the Riemann Hypothesis. {n} cards and pages, each with a picture first and a plain line here. Every page checks its own numbers before it draws and loads nothing from elsewhere.</p>
{start_box}
{"".join(parts)}
<p class="foot">How these were checked: every card and page had one reviewer who was not its author, who ran it, re-derived one number with separate code, read the first screen as a newcomer, and checked that every claim names its source. The full page of cards is <a href="showcase.html">showcase.html</a>; the reading rules are in the README.</p>
</main></body>
</html>
"""
    open(os.path.join(ROOT, "round_two.html"), "w", encoding="utf-8").write(page)
    print("round_two.html written:", n, "entries;", len(LEAN), "Lean files listed")


if __name__ == "__main__":
    main()
