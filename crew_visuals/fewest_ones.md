# How few ones can change rank?

In ordinary arithmetic, two equal nonzero contributions add to two. Modulo 2 they add to zero. The same cancellation can make a table of zeros and ones lose an independent row.

[Try the editable board and count all 65,536 four-by-four tables](../fewest_ones.html)

The smallest example modulo 2 has **six ones**. Put a zero on each diagonal square of a three-by-three table and a one everywhere else. Exactly two ways to pick a one in each row and column survive. They have the same sign in the determinant, so the determinant is 2. The table has rank 3 in ordinary arithmetic and rank 2 modulo 2.

**Why five can never suffice.** If a table of ordinary rank $r$ has smaller rank modulo 2, choose an $r$-by-$r$ subtable with nonzero determinant. Its determinant is even, so at least two of its nonzero signed terms have the same sign. Each term chooses one position in each row and uses each column once. Two distinct choices of the same sign must disagree in at least three rows. If they disagreed in just two, they would be one transposition apart and have opposite signs. Together they use at least $r+3$ ones. Since such a pair needs $r\ge3$, six ones is the minimum. The bound $r+3$ is attained for every $r\ge3$ by adjoining independent diagonal ones to the three-by-three example.

**Modulo 3, the smallest four-by-four example has nine ones.** A one- or two-row minor has too few determinant terms. A three-row minor would need all three permutations of one sign, which would fill all nine cells and make the determinant zero. In a four-row minor we need at least three terms of the same sign. Relabel columns so the first choice is the identity. If the second choice is two disjoint swaps, the two choices already use eight ones. Any choices that reuse only those ones must make neither swap, one swap, or both. The only same-sign possibilities are the first two, so a third needs a new one. If the second choice is a three-cycle, the first two use seven ones and leave the fourth row paired only with the fourth column. A third choice that moves the fourth row needs at least two new ones, one from that row and one into that column. If the fourth stays put, the only new same-sign choice is the reverse three-cycle, which needs three new ones. Either way we need at least nine. The board's nine-one example has determinant 3 and rank 3 modulo 3.

The exhibit independently enumerates the four-by-four tables and finds 3,000 whose rank drops modulo 2 and 120 whose rank drops modulo 3. The proof above gives the minimum counts without enumerating tables. The motivating SAT table is Lattice's finite example from the Marginalia discussion, also shown in [Nine solutions, two ranks](../nine_solutions_two_ranks.html).

## A construction for every prime

Use $p+1$ columns numbered 0 through $p$. Put ones in columns 1 through $p$ of the top row. For each $i$ from 1 through $p$, add a row with just two ones, in columns 0 and $i$. This uses $3p$ ones.

The bottom $p$ rows are independent because they each have a private column $i$. Their sum minus the top row leaves $p$ in column 0 and zeros elsewhere. In ordinary arithmetic that gives a new independent direction. Modulo $p$ it vanishes, so the rank drops from $p+1$ to $p$. This gives the six- and nine-one examples when $p$ is 2 or 3.

## Two exhaustive checks beyond 4×4

For 5 and 7 the same phenomenon already happens in smaller boards than that construction gives. The search below checks the minimum size and sparsity for each listed prime.

| Arithmetic | Smallest square size | Fewest ones at that size | How the lower bound was checked |
| --- | --- | --- | --- |
| Mod 2 | 3×3 | 6 | Same-sign choices |
| Mod 3 | 4×4 | 9 | Same-sign choices |
| Mod 5 | 5×5 | 13 | Signed components and exhaustive search |
| Mod 7 | 6×6 | 16 | Exhaustive determinant search |

A full-rank binary square table must have distinct nonzero rows. Permuting the rows changes at most the sign of its determinant. The search therefore sorts the rows and examines each possible set once. It checks 169,911 row sets at size five and 67,945,521 at size six. For the smaller sizes, the maximum absolute determinant is 3 at size four and 5 at size five. A nonzero determinant divisible by 5 or 7 is therefore impossible below its respective minimum size. [Reproducible C++ search](../tools/check_sparse_rank.cpp)

The smallest mod-5 examples are all related by changing the order of the rows and columns. The 720 row-unordered mod-7 examples have two shapes, 360 of each. Swapping rows with columns takes one shape to the other. In the first shape the row counts, sorted, are $2,2,2,3,3,4$ and the column counts are $2,2,3,3,3,3$. Those two lists explain why a row or column shuffle alone cannot produce the transpose. The search canonicalizes by trying every column order and sorting rows. Independently, shuffling a single witness and its transpose generated two disjoint sets of 360, covering every minimum case. [Shuffle and reflect the board](../mod_seven_twins.html)

### Why twelve ones cannot suffice modulo 5

This adapts Lattice's signed-components argument for modulo 7. Every binary 4×4 determinant has absolute value at most 3. Replace each entry $a$ by $1-2a$ and border with a row and column of ones. Subtract the new top row from the other rows. The resulting determinant has absolute value 16 times that of the original, while Hadamard bounds it by $5^{5/2}<64$. Smaller minors can be padded with identity rows and columns. Thus a mod-5 rank drop at size five needs a nonzero full determinant divisible by 5. A row or column with a single 1 would reduce it to a smaller determinant, so every row and column must have at least two ones.

A row with two ones makes two of the unknowns negatives of each other. Join their columns by an edge. A connected component with an odd cycle forces its unknowns to zero, in both ordinary arithmetic and mod 5. Every other component contributes one free unknown, with alternating signs on its two sides. The original rows are independent in ordinary arithmetic, so there is one free variable left per row with three or more ones. Those rows give the remaining equations. A coefficient of magnitude 2 in them needs two columns with the same sign in some component and at least one with the opposite sign.

With at most 12 ones there are at most two rows of weight greater than two. With zero or one such row, there is no nonzero residual determinant divisible by 5 because the possible single remaining coefficient has magnitude at most 4. With two such rows, both have exactly three ones. Their reduced two-by-two determinant has absolute value at most 9. If a coefficient has magnitude 3, it fills its entire row, so the determinant is a multiple of 3 and cannot be 5 or −5. With coefficients of magnitude at most 2, reaching 5 needs terms of magnitudes 4 and 1. This requires a magnitude-2 coefficient in each of the two component columns. Each component needs at least three vertices, which cannot fit in five columns. The 13-one witness therefore meets the lower bound.

To choose several primes at once, multiply them and use a sparse binary path counter to turn that product into a determinant. [Pick the primes that change rank](../pick_the_primes.html)

## A lower bound for prescribing several primes

Suppose a binary table has ordinary rank $r$, contains $w$ ones, and loses rank modulo every prime in a chosen set. Write $P$ for the product of those primes. Each selected prime divides every $r$-by-$r$ determinant. Choose one that is nonzero in ordinary arithmetic. Its absolute value is at least $P$.

If that subtable has $d_i$ ones in row $i$, the length of that row as a vector is $\sqrt{d_i}$. Hadamard's inequality bounds the absolute determinant by the product of the row lengths. Since $d_i\le 2^{d_i-1}$ for positive integers, the product is at most $2^{(w-r)/2}$. Therefore

$$w\;\ge\;r+\lceil 2\log_2 P\rceil.$$

So a logarithmic dependence on the product is necessary, even with arbitrary table dimensions. The reused-route construction attains the same order of growth. For the compact table with determinant 30, $r=16$, this bound requires at least 26 ones and the construction uses 38.

## How few ones let any direct input finish decoding?

For this question a binary $n\times n$ board mixes $n$ input numbers. A 1 connects an input to a reading. We want the board to be invertible over the rationals, singular mod $p$, and recoverable mod $p$ from **any $n-1$ mixed readings and any one direct input**. In the last condition the missing reading and the direct input can be chosen independently. Everything below counts the connections in the board itself.

| Prime $p$ | Sizes $n$ | Exact minimum connections |
| --- | --- | --- |
| 2 | Odd $n\ge3$ | $2n$ |
| 2 | Even $n\ge4$ | $2n+2$ |
| 3 | $n\ge4$ | $2n+1$ |
| 5 | $n=5$; $n\ge6$ | $13$; $2n+2$ |
| 7 | $n=6$; $n\ge7$ | $16$; $2n+3$ |
| 11 | $n\ge9$ | $2n+4$ |
| 13 | $n\ge10$ | $2n+4$ |
| 17 | $n\ge12$ | $2n+4$ |

### What recovery requires

The mod-$p$ rank is $n-1$. A relation among the readings has no zero coefficient, so any one missing reading can be deduced. The vector of invisible input changes also has no zero coordinate, so a direct reading at any one input distinguishes the $p$ possible originals. Conversely, the recovery rule forces both properties. The surviving $n-1$ rows must be independent for every deletion, and a direct read of any coordinate must distinguish the possible originals.

Every row and column therefore needs at least two ones. Write $2n+e$ for the total. At an odd prime the two-input rows form a forest on the inputs. An odd cycle would force some invisible input changes to be zero. An even cycle would give a rational dependence among the rows. If there are $h$ other rows, the forest has $h$ components. Eliminating its leaf variables gives a signed $h\times h$ matrix with the same absolute determinant. Each remaining row originates in a reading with at least three connections, so $1\le h\le e$.

### The lower bounds at odd primes

With $e=0$ there would be $n$ forest edges, which is impossible. With $e\le1$ the reduced matrix has one coefficient of magnitude at most 3. With $e\le2$ it has either one coefficient of magnitude at most 4, or two rows whose absolute coefficient sums are at most 3. A concentrated row with coefficient of magnitude 3 makes the determinant a multiple of 3 of magnitude at most 9. Otherwise both row lengths are at most $\sqrt 5$ and the determinant has magnitude at most 5. This proves the lower bounds for 3, 5 and 7.

For $e\le3$, a one-row determinant has magnitude at most 5. A two-row determinant has magnitude at most 12. Its two row budgets are at most 3 and 4. A concentrated coefficient of magnitude 3 in the first or 4 in the second makes the determinant a multiple of that coefficient. Without those cases the row lengths are at most $\sqrt 5$ and $\sqrt{10}$, giving a determinant below 8. With three rows the budgets are all 3. If one row has a coefficient of magnitude 3, the determinant is a multiple of 3 of magnitude at most 27. Otherwise Hadamard gives $|\det|\le5\sqrt 5<12$. The only target still possible is 11. Reaching 11 would require every squared row length to be 5. If any pair has nonzero integer inner product, the square of the determinant is at most $(25-1)5=120$ by bounding the third row's height by its length. If all pairs are orthogonal, the squared determinant is 125. Both exclude $11^2=121$. This proves the lower bounds for 11, 13 and 17.

### Boards that attain the bounds

At $p=2$, all entries of each invisible vector and reading relation are 1, so each row and column has even weight. With exactly $2n$ ones every row and column has degree 2. The two-input graph would be a union of cycles. Its mod-2 kernel has one dimension per component, so there must be one cycle, and ordinary invertibility requires it to be odd. An odd cycle works directly, with determinant of magnitude 2. For even $n$ start at size 4 with rows $1111,1100,1010,1001$. Its determinant is $-2$, and both mod-2 null vectors are all ones.

At $p=3$, start with a three-leaf star and one extra reading that adds its three leaves. At size 5 use the four pair sums on a five-input path and add its first, third and fifth inputs in the fifth reading. Both reduce to a coefficient of magnitude 3. For the path, the reading relation gives the four path rows weights $-1,1,-2,2$ and the last row weight 1 mod 3.

For the other primes a small collection of stars gives the following reduced matrices. In each column use a center for a coefficient $-1$, and as many positive leaves as the largest positive coefficient. Mix each leaf with its center. For the remaining readings, a coefficient $k>0$ uses the first $k$ leaves of that star. Eliminating all leaf rows produces exactly the displayed coefficients, with the leaf side chosen positive.

| $p$ | Reduced rows | Smallest size in this construction | Weights on the last readings mod $p$ |
| --- | --- | --- | --- |
| 5 | $(2,1),(-1,2)$ | 6 | $(1,2)$ |
| 7 | $(2,1),(-1,3)$ | 7 | $(1,2)$ |
| 11 | $(2,1,0),(0,2,1),(1,-1,2)$ | 9 | $(5,9,1)$ |
| 13 | $(2,1,0),(0,2,1),(1,0,3)$ | 10 | $(6,10,1)$ |
| 17 | $(2,1,0,0),(0,2,1,0),(0,0,2,1),(-1,0,0,2)$ | 12 | $(1,8,13,2)$ |

The determinants in the table are $5,7,11,13,17$, respectively. Their invisible changes start at 1 and each successive star's value is $-2$ times the previous one. Every leaf row gets the negative of the sum of the last-reading weights that use its leaf. In the listed constructions each leaf is used by one or two last readings, and these sums are all nonzero mod $p$. The center equations hold because the last-reading weights kill the reduced matrix. Splitting a shared leaf into two leaves of the same center, one for each reading that used it, gives a board one size larger at the same excess. The earlier exhaustive census supplies the sharper lower bounds at size 5 modulo 5 and size 6 modulo 7. The 13-one mod-5 witness has every cofactor nonzero mod 5. Both 16-one twins at size 6 work modulo 7.

To grow by two inputs, replace one occurrence of $x$ by a fresh $z_2$. Add two readings, $x+z_1$ and $z_1+z_2$, using another fresh input $z_1$. The mod-$p$ invisible changes for the new inputs are $-x,x$. In the reading relation the new rows have weights $y,-y$ when the changed reading has weight $y$. Elimination preserves the original determinant, and the step adds exactly four connections. Together the two starting sizes cover both parities.
