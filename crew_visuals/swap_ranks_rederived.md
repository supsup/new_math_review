# One step of the 3-SAT argument, re-derived by a fresh model

*Fixpoint, 24 November 2026. A small experiment, with its limits stated.*

## In one sentence

Anthropic's README for its 3-SAT result says a model can rebuild the argument from one paragraph; we tested **one step** of that
paragraph, and a fresh model, given only the paragraph and precise definitions, produced in about six minutes exactly the formulas
and tables that Fixpoint had computed separately.

## Step by step

1. **The claim being tested.** The README of `anthropics/formal-math` (revision `11b6c7e`, `eth/README.md`) gives "the key idea,
   in condensed form". One sentence of it reads: "Per bit, SWAP = I − 2·singlet; grouping by the number of singlets gives λ+1
   operators with (row rank)·(column rank) ≤ 12^λ."
2. **What that means in plain words.** Two wires that cross are expensive to cut in either direction. The sentence says the
   crossing can be rewritten as a short sum of pieces, and each piece is cheap in at least one direction. (Picture 4 of
   [round_two_pictures.html](../round_two_pictures.html) draws this.)
3. **What Fixpoint did first.** Built the pieces directly from the definitions for 1, 2 and 3 bits per wire, computed their
   exact ranks, and found a formula that fits (`tools/check_swap_singlet_ranks.py`).
4. **The experiment.** A fresh model (Claude Opus, started with no knowledge of step 3) was given the README paragraph, exact
   definitions of the pieces and of "row rank" and "column rank", and four tasks: find and prove the formulas, prove or disprove
   the bound 12^λ, give the tables for 1 to 4 bits, and say what the bound buys. It was told to work only from the description.
5. **The result.** Its formulas are the same as Fixpoint's. Its tables for 1 to 3 bits are identical to Fixpoint's computed
   ones, entry for entry. It went further: tables for 4 and 5 bits, a shorter proof of the bound, and an argument that 12 cannot
   be replaced by a smaller number for this way of splitting.
6. **What Fixpoint then checked.** The 4-bit table, with a second program written a different way
   (`tools/check_swap_ranks_kron.py`, elimination modulo two large primes): it matches. The "12 is best" figures, by direct arithmetic from the formula: they match.

## What this does and does not show

- It shows that **this one step** can be rebuilt from the paragraph plus careful definitions, quickly, and that two independent
  computations agree with the rebuilt formulas.
- It does **not** test the README's full claim. The model did not rebuild the algorithm, and it said so: it did not check the
  paragraph's recursion (the sentence with 0.9 in it) or the regrouping step.
- The definitions in the task were written by Fixpoint from a reading of the paragraph. A different reading of "row rank" or of
  the grouping would be a different task.
- One caution about independence: the model ran on the same machine, in a scratch folder next to a page that contained
  Fixpoint's 1-to-3-bit table. It was told to read nothing but its own files and reported that it did not; its 4- and 5-bit
  tables and its proofs are not in any file it could have read.
- The paper itself uses a different way of splitting the crossing (blocks of three bits) and gets the ratio 11/12. The ratio
  here is log 12 / log 16 = 0.896, the README's "0.9".

## The numbers

Row rank of piece j with λ bits per wire: the sum of C(λ, t)·3^(λ − t) for t from j to λ.
Column rank: the sum of C(λ, k)·3^k for k from 0 to j. (So the column rank of piece j is the row rank of piece λ − j.)

| bits per wire | (row rank, column rank) for j = 0, 1, …, λ | largest product | 12^λ |
|---|---|---|---|
| 1 | (4,1) (1,4) | 4 | 12 |
| 2 | (16,1) (7,7) (1,16) | 49 | 144 |
| 3 | (64,1) (37,10) (10,37) (1,64) | 370 | 1,728 |
| 4 | (256,1) (175,13) (67,67) (13,175) (1,256) | 4,489 | 20,736 |
| 5 | (1024,1) (781,16) (376,106) (106,376) (16,781) (1,1024) | 39,856 | 248,832 |

Rows 1 to 3: computed by Fixpoint (exact elimination over the fractions) and by the model, separately. Row 4: the model's exact
computation, then matched by Fixpoint's second program, which eliminates modulo two large primes; that bounds the true rank from
below, and the formula's proof bounds it from above. Row 5: the model's exact computation only; it agrees with the formula.

The crossing itself has row rank 4^λ and column rank 4^λ, a product of 16^λ.

**Why the product never exceeds 12^λ (the model's proof, shorter than Fixpoint's).** In the column-rank sum every term has
3^k ≤ 3^j, so the column rank is at most 3^j·2^λ. In the same way the row rank is at most 3^(λ − j)·2^λ. Multiply: at most
3^λ·4^λ = 12^λ.

**Why 12 is the right number for this split.** The largest product, near j = λ/2, is about (9/(2πλ))·12^λ. Checked by Fixpoint
from the formula: λ times the largest product divided by 12^λ is 1.3741 at λ = 100 and 1.4167 at λ = 400, heading for
9/(2π) = 1.4324. So no smaller base works for this split. Whether a different split does better is a separate question; the
paper's appendix discusses others.

## How to re-run

```
python3 -I tools/check_swap_singlet_ranks.py 3     # builds the pieces from the definitions; exact ranks; 1 to 3 bits
python3 -I tools/check_swap_ranks_kron.py 4        # a second construction, bit by bit; 1 to 4 bits
```

Both print the tables, and exit with an error if a rank differs from the formula or a product exceeds 12^λ.

## The task, as given

The model received the README paragraph quoted in step 1 (in full) and this setting:

- Four indices a, b (top row) and c, d (bottom row), each a string of λ bits.
- The crossing is X[a,b,c,d] = [a = d]·[b = c]. Read from the bottom pair to the top pair it is SWAP on two λ-bit registers.
- Per bit: I[a,b,c,d] = [a = c]·[b = d], and P is the projector onto the singlet state (|01⟩ − |10⟩)/√2; one-bit SWAP = I − 2P.
- O_j is the sum, over all j-element sets S of bit positions, of the tensor product with 2P on S and I elsewhere, so that
  X is the alternating sum of the O_j.
- Row rank: the rank of the matrix with row index (a, b) and column index (c, d). Column rank: row index (a, c), column index (b, d).

## The model's report, abridged (its tables are the ones above; a local folder name is left out)

> I found both closed formulas and proved them. I proved R_j·C_j ≤ 12^λ, and 12 is the best possible base. Exact rank computation
> over the rationals matches the formulas for every j and every λ from 1 to 5.
>
> Notation: F_λ(m) = Σ_{k=0}^{m} C(λ,k)·3^k. This is a partial sum of the binomial expansion of (1+3)^λ, so F_λ(λ) = 4^λ.
>
> (a) Closed formulas. Row rank: R_j = Σ_{t=j}^{λ} C(λ,t)·3^{λ−t} = F_λ(λ−j). Column rank: C_j = Σ_{k=0}^{j} C(λ,k)·3^k = F_λ(j).
> So R_j = C_{λ−j}. The ends check out: O_0 = I has ranks (4^λ, 1) and O_λ = (2P)^{⊗λ} has ranks (1, 4^λ).
>
> (b) Proofs. Common step: both reshapes of a bitwise tensor product are the Kronecker product of the per-bit reshapes, after
> reordering rows and columns by bit pairs. Reordering does not change rank.
> Row rank. Per bit, as a 4×4 map from (c_i,d_i) to (a_i,b_i): I is the identity, which splits as P + Q, where P is the rank-1
> singlet projector and Q = I − P is the rank-3 triplet projector. Expanding gives O_j = Σ_T 2^j·C(|T|,j)·(P on T, Q off T).
> The terms are mutually orthogonal projectors of rank 3^{λ−|T|}. The coefficient is positive exactly when |T| ≥ j, so
> R_j = Σ_{t≥j} C(λ,t)·3^{λ−t}.
> Column rank. Per bit, as a 4×4 matrix from (b_i,d_i) to (a_i,c_i), use the Bell basis Φ± = e00 ± e11 and Ψ± = e01 ± e10:
> I becomes diag(2,0,0,0) and 2P becomes diag(+1,−1,−1,+1). So the column matrix of O_j is diagonal in the product Bell basis.
> A basis word with k positions not equal to Φ+ has entry ±2^{λ−j}·C(λ−k, j−k), nonzero exactly when k ≤ j. Counting such words
> gives C_j = Σ_{k≤j} C(λ,k)·3^k.
>
> (d) Task 2: true, and strict for every λ ≥ 1. Since 3^k ≤ 3^j for k ≤ j, C_j ≤ 3^j·2^λ, and in the same way
> R_j ≤ 3^{λ−j}·2^λ. Multiplying gives R_j·C_j ≤ 12^λ. Where 12 comes from: 12 = 4·3 per bit. In both reshapes each bit's
> 4-dimensional pair space splits as 1 + 3. 12 is the best possible base: the maximum over j is about (9/(2πλ))·12^λ.
>
> (e) Task 4. The exponent ratio is log 12 / log 16 ≈ 0.896, below 0.9. Fix one choice of O_j per rectangle. Merging whole rows
> leaves bonds totalling Π R_j, merging whole columns Π C_j. The cheaper of the two is at most sqrt(Π R_j·C_j) ≤ 12^{Nλ/2},
> against 16^{Nλ/2} for the raw crossings.
>
> (f) Verified by running code: X = Σ(−1)^j O_j for λ = 1..5; exact rational ranks of both reshapes for λ = 1..5, all matching
> the formulas; the two diagonal forms entry by entry for λ = 1..4; the bound for every j and every λ ≤ 400. Derived on paper
> only: the general-λ proofs, the asymptotic constant, and the reasoning in (e). Unsure: I did not check the README's wider
> claim, e(9K^16) ≤ 0.9·e(K) + O(1/K), including the balanced regrouping into K classes.
