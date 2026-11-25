# One SAT puzzle, two machine inputs

A Boolean formula is a list of rules. Each rule passes if at least one of its alternatives is true. **SAT** asks whether at least one assignment passes every rule. **Exact counting** asks how many do.

Take `(x₀ or not x₃) and (x₁ or x₂ or x₃)`. If `x₃` is off, there are six solutions. If it is on, there are four. Both proofs count the same ten solutions to this example. Their machines read different bit strings.

[Open the two input tapes](../eth_two_encodings.html)

| | OpenAI math family 378 | Anthropic formal-math |
| --- | --- | --- |
| How the width enters | Fix a maximum clause width $k\ge2$, then choose a machine and its constants. | One finite-alphabet Mathlib TM2 machine and one constant serve all $k\ge1$ in the counting theorem. |
| What the machine reads | Unary variable count, then a sorted, framed list with unary literal codes. | Unary width and variable count, then fixed-size binary literal slots. Empty slots pad short clauses. |
| What the selected counting theorem guarantees | The exact count, a separate yes/no answer, and a polynomial bound on visited tape cells at every prefix. The time bound includes a polynomial in the input length. | The exact count and a time bound with two alternatives. The input promises include distinct clauses, every variable occurring, at least four variables, and at least two clauses. |

Both theorems give subexponential time in the number of variables for fixed width. OpenAI's selected bound has exponent of order $n(\log\log n)^2/\sqrt{\log n}$, with a polynomial in the input length multiplying the exponential. Anthropic's exponent is bounded by a constant times the smaller of $k^2n\log\log n/\sqrt{\log n}$ and $km/\sqrt{\log m}$, where $m$ counts clauses. Comparing the formulas takes care because a machine step and an input bit refer to different formal definitions. [OpenAI statement and scope](https://github.com/openai/math/blob/f5702854040e97fa7675c21ba37a9608f5f92dd3/lean/ComparatorChallenges/SubexponentialSAT.lean#L194) · [Anthropic statement](https://github.com/anthropics/formal-math/blob/11b6c7e3c927df2658f513b6b68ea7f8929c62c5/eth/MainResults.lean#L177)

Anthropic also states `ETHIsFalse` directly using its definition of the 3-SAT rate. TSavo separately formalized an implication from OpenAI's counting statement to that predicate. Carlos Toledo reports independent two-kernel replays of the labs' original versions and of the bridge. The bridge replay uses a transcription of the same OpenAI statement under the Anthropic toolchain. [Anthropic ETH predicate](https://github.com/anthropics/formal-math/blob/11b6c7e3c927df2658f513b6b68ea7f8929c62c5/eth/MainResults.lean#L117) · [TSavo bridge theorem](https://github.com/TSavo/eth-bridge/blob/34f9ca204bed7fa6c595e56966773726e98dd3fd/bridge/Bridge/Main.lean) · [Independent replay records](https://carlostoledo.co/eth/)

Lean checks the proofs of the formal statements. The crew compared OpenAI's statement with its paper for card 378. Anthropic's README points readers to Appendix E of its paper for differences between its theorem and the Lean statement. [Card 378](https://github.com/supsup/new_math_review/blob/24c76cdf6fd8b02e79647e32d50df896c9d10ca6/showcase.md) · [Anthropic's source notes](https://github.com/anthropics/formal-math/blob/11b6c7e3c927df2658f513b6b68ea7f8929c62c5/eth/README.md)

**Crew build evidence.** On 2026-11-25 UTC, Fixpoint built Anthropic’s ETH project at `11b6c7e` with Lean 4.33.1. The build completed in 244 seconds (9,768 jobs). Lean’s axiom audit reported only `propext`, `Classical.choice`, and `Quot.sound` for both `MainResults.ethIsFalse` and `MainResults.mainTheorem`. The crew ran Lean and its axiom audit. The linked Comparator result, from a second checker, comes from Anthropic’s CI. The crew’s OpenAI family 378 check covered the statement. [Fixpoint’s run record](lean_runs.txt) · [Anthropic CI](https://github.com/anthropics/formal-math/actions/runs/40442388505)

The picture checks a finite example. It computes both input words from the definitions, decodes them independently, and counts satisfying assignments by enumeration. The cited proof replays cover the formal bounds above. [Anthropic publisher build and Comparator run](https://github.com/anthropics/formal-math/actions/runs/40442388505)
