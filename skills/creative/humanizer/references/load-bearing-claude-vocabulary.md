# The `load-bearing` Claude-associated PR cluster

## Why this reference exists

Louis Abraham's [`load-bearing`](https://github.com/louisabraham/load-bearing) project groups public GitHub pull-request descriptions by word distribution. It does not begin with a list of supposed AI tells. An unsupervised fit found an arriving cluster whose share rose sharply over 2025–2026; the project associates that writing pattern with Claude.

This adds a missing technical-prose layer to the general AI-pattern catalog. The main signal is not `delve`-style marketing language. It is a recurring bundle of certainty, personified system behavior, mechanical metaphors, verification theater, totalizing scope, productive hyphenation, and em-dash-heavy argument.

Use this reference when editing:

- pull requests, issue reports, changelogs, engineering notes, technical postmortems, or code-review prose;
- drafts known to have been written or heavily rewritten with Claude;
- prose that is technically competent but keeps making every mechanism sound decisive, adversarial, spatial, or courtroom-ready.

Do not load this for every humanization task. Keeping the exact vocabulary behind this reference reduces prompt priming and keeps the main skill lean.

## Source snapshot

The figures below were read from `analysis.js` generated 2026-09-01 at repository commit [`936a1547b6c099757942cf7ad3d52339140835ad`](https://github.com/louisabraham/load-bearing/tree/936a1547b6c099757942cf7ad3d52339140835ad):

- 602 sampled days across 86 complete weeks;
- 467,387 pull-request descriptions;
- 52,506,137 word appearances;
- 20,309 vocabulary items written by at least 50 distinct accounts;
- arriving-cluster share: 0.863% in the first eight weeks and 37.43% in the last eight;
- 39.54% across the latest four complete weeks in that fit;
- 12-week fitted slope: +1.069 percentage points per week.

The repository may move after this snapshot. Re-read its current `analysis.js` before quoting current totals.

### What “lift” means here

The project assigns each description to one of ten word-distribution clusters. It then ranks a word by its frequency inside the arriving cluster divided by its frequency outside that cluster, with a denominator pseudo-count. Lift describes association with this corpus cluster. It does not say that a word caused the assignment, came from Claude, or is bad writing.

## Representative vocabulary

These are diagnostic families, not replacement lists or banned words.

| Family | Representative words and lift in the snapshot |
|---|---|
| Certainty and rhetorical adverbs | `plainly` 34.26×; `quietly` 30.08×; `genuinely` 23.68×; `outright` 22.32×; `deliberately` 20.01×; `precisely` 16.77×; `merely` 14.27×; `honest` 12.78×; `exactly` 9.32× |
| Totalizing scope and negation | `nobody` 29.22×; `nowhere` 22.13×; `nothing` 21.04×; `alone` 14.50×; `ever` 13.38×; `never` 10.78×; `every` 7.36× |
| Personified or dramatized system behavior | `survived` 23.24×; `carries` 22.12×; `rests` 21.16×; `rides` 19.80×; `settles` 17.72×; `holds` 16.90×; `refuses` 15.61×; `survives` 15.33×; `sits` 14.99×; `earns` 14.34×; `decides` 14.07×; `lands` 10.39× |
| Structural and mechanical metaphors | `load-bearing` 19.65×; `asymmetry` 19.58×; `rung` 17.53×; `lever` 15.28×; `wedged` 15.09×; `backstop` 12.11×; `seam` 10.67×; `wedge` 10.07×; `ladder` 9.92×; `chokepoint` 9.69× |
| Proof and verification register | `asserted` 19.79×; `mutation-checked` 19.77×; `mutation-verified` 16.02×; `re-measured` 15.95×; `provably` 15.16×; `byte-identical` 15.13×; `measured` 15.05×; `mutation-tested` 14.99×; `re-verified` 13.85×; `reproduces` 11.92× |

The broader list also contains many productive `re-`, `pre-`, `post-`, `hand-`, `byte-`, `bit-`, `mid-`, and `unit-` compounds. Many are valid technical terms. The tell is the accumulated register: every sentence seems to certify, adjudicate, or mechanize the claim.

### Em dash

The repository treats the em dash as a token because it is unusually informative in this corpus. Its methodology note reports a rise from 0.2 appearances per 10,000 words in early 2024 to 123 per 10,000 by mid-2026. This supports an em-dash-density check, not an em-dash ban. Preserve deliberate punctuation and revise repeated automatic use.

## Editing protocol

1. **Mark bundles, not isolated words.** Treat a passage as a candidate only when it repeats one family or combines at least two families in a short span. A single precise term is not a problem.
2. **Preserve exact evidence.** Keep commands, test names, identifiers, measurements, byte-level comparisons, and verified outcomes when they are true and relevant.
3. **Remove unsupported certainty.** Delete rhetorical certainty adverbs when the sentence does not need them. When evidence exists, state the evidence instead of announcing certainty.
4. **Bound absolutes.** Check the domain of `every`, `never`, `nothing`, and similar terms. Replace them only when the source supports a narrower scope.
5. **Name the mechanism.** When software “refuses,” a guard “wins,” a fix “survives,” or a claim “rests” on something, prefer the literal condition, control flow, state change, or test result when that is already known.
6. **Deflate metaphor stacks.** Mechanical and spatial metaphors can clarify one hard idea. Several in one paragraph make technical prose sound staged. Keep the best one or replace it with the actual relationship.
7. **Consolidate verification.** If several sentences separately announce that a result was measured, checked, reproduced, and verified, combine them into one evidence line. Do not erase distinct tests or outcomes.
8. **Check punctuation density.** Replace repeated em-dash pivots with periods, commas, parentheses, or ordinary clauses where the thought does not require interruption.
9. **Re-read for meaning.** Confirm that the edit preserved the claim, evidence strength, causality, and technical distinctions. Never weaken a proven result merely because its vocabulary appears in the cluster.

Completion criterion: the prose states what happened and how it was established without repeatedly dramatizing its certainty or mechanics.

## Before/after patterns

### Evidence instead of certainty theater

Before:

> The mutation-verified guard plainly proves the old branch can never survive the retry path.

After:

> The mutation test kills the old branch when the retry path runs.

Use the after only when that is what the test actually showed.

### Mechanism instead of personification

Before:

> The fallback quietly carries the stale value until the final check refuses it.

After:

> The fallback retains the stale value until the final check rejects it.

### One structural metaphor, not four

Before:

> The cache key is the load-bearing seam, the backstop that keeps the second rung from collapsing.

After:

> The second stage depends on the cache key.

## Evidence limits

Do not turn this project into a general AI detector.

- The corpus is sampled GitHub pull-request prose, not essays, fiction, email, journalism, or speech.
- The model is unsupervised. It finds word-distribution clusters; it does not train on verified Claude and human labels.
- The project excludes obvious bot accounts, but a human account may paste model output and an automated system may post under an ordinary login.
- The source sampling is truncated to the earliest 100 results inside each five-minute window. It samples; it does not enumerate GitHub.
- `k = 10`, the seed, author cap, lead window, and several thresholds involve disclosed judgment calls.
- The project's own classifier says only whether text resembles the arriving cluster. Its README explicitly says it cannot identify who wrote the text.
- High lift is corpus association, not a causal rule and not a reason to delete a useful word.

Use the findings to sharpen editorial judgment. Do not use them to accuse a writer, launder provenance, or chase a classifier score.

## Sources

- Louis Abraham, [`load-bearing`](https://github.com/louisabraham/load-bearing), MIT license.
- [Methodology and limitations](https://github.com/louisabraham/load-bearing/blob/936a1547b6c099757942cf7ad3d52339140835ad/README.md).
- [Snapshot data](https://github.com/louisabraham/load-bearing/blob/936a1547b6c099757942cf7ad3d52339140835ad/analysis.js).
- [Analysis implementation](https://github.com/louisabraham/load-bearing/blob/936a1547b6c099757942cf7ad3d52339140835ad/analyze.py).
