---
name: constrained-humanization-editing
description: "Use when humanizing prose without changing its meaning."
license: "All rights reserved"
metadata:
  version: "1.0.0"
  author: "Dust Wave"
  short-description: "Humanize prose under a strict preservation contract"
  hermes:
    tags: [writing, editing, humanize, preservation, faithful-revision]
    related_skills: [humanizer, anti-machine-writing-editorial-pass, iterative-ai-detector-humanization]
---

# Constrained Humanization Editing

Specialist module for the `humanizer` master router. Use this when the user wants prose to read more human while preserving meaning, scope, structure, formatting, and roughly length. This is the faithful-editing contract; it is stricter than a general humanization pass.

Extracted from the `batty-replic-humanization-editor` profile (Batty Replic). Complements `humanizer`, `anti-machine-writing-editorial-pass`, and `gonzo-reference-rewrite-pass` by enforcing a tighter preservation contract.

## What this skill preserves (non-negotiable)

- Meaning
- Scope
- Structure — headings, section order, paragraph count (±10%)
- Formatting — lists, emphasis, code blocks, links
- Roughly the original length — ±10% token count

## What this skill does NOT do

- Invent ideas not already present
- Add research, citations, or new data
- Introduce new examples, metaphors, names, anecdotes
- Strengthen arguments by expanding them
- Clarify things that weren't clarified in the draft
- Smuggle in the editor's perspective under "editing"

If the draft is wrong, say so and stop. Don't fix it here.

## What this skill optimizes for

- Less stiffness
- Fewer formulaic transitions ("moreover", "furthermore", "in conclusion", "it's important to note")
- More varied sentence rhythm (mix of short and long; break up parallel triplets)
- Fewer hedging stacks ("it could potentially be said that perhaps…")
- Fewer rhetorical throat-clears ("Let's dive in", "At its core")
- Less moralizing and caveat-pile-ups
- Contractions where the original tone supports them
- Concrete nouns over abstract ones, when the abstract noun was a stand-in
- In technical prose, fewer accumulated certainty adverbs, absolutes, personified system verbs, mechanical metaphors, verification compounds, and automatic em-dash pivots

## Human-shape constraints to preserve or restore

Use these as a final diagnostic pass, but stay inside the preservation contract. Do not invent content to satisfy them.

- **Theme inference:** remove needless sentences that explain what the reader should conclude when the existing sentence, example, or transition already carries it.
- **Less linear rhythm:** preserve existing time jumps, digressions, flashbacks, asides, and returns. Do not smooth them into a rigid outline just because it looks cleaner.
- **Emotion without stock body metaphors:** replace generic phrases like "her heart raced" or "a weight settled on him" only when the source already implies a more precise action, reaction, or social detail.
- **Specific references:** keep real named texts, brands, places, venues, and objects. If the source has "the coffee shop" and gives no name, do not invent one.
- **Narrative diversity:** preserve existing scenes, subplots, dialogue, and side beats. Do not collapse them into summary unless the user asked for compression.
- **Process residue and voice:** Scammell's useful warning is that removing AI fingerprints is not the same as making the writing good. In constrained edits, preserve signs of a real mind working: hesitation, contradiction, sentence-level choice, imperfect but alive phrasing, and the author's struggle with the material. Do not sand these down into perfect prompt-shaped prose.
- **Screenplay-specific tells:** for scripts and creative prose, watch for inanimate objects "humming," dash theatrics, metaphors that do not quite make sense, repeated "not X, not Y, but Z" constructions, adjective-fragment character portraits, noun-pile environment descriptions, "That lands," and dialogue where characters bat labels around without saying much. Fix only with material already present in the source.

## Procedure

1. **Read the whole draft twice before editing.** The first pass is to hear its voice; the second is to notice where it betrays itself.
2. **Identify preservation anchors.** Mark the meaning-critical sentences, claims, numbers, quotes, code blocks, URLs, headings, intentional repetitions, and already-human paragraphs. These are untouchable unless the user asks otherwise.
3. **Treat this as a limit, not the main event.** If many paragraphs need heavy reconstruction, the source draft was generated badly or needs developmental rewriting. Do not manufacture rhythm through endless polishing.
4. **Make one pass per failure mode:**
   - Pass 1 — Kill formulaic transitions and throat-clears
   - Pass 2 — Break up sentence-rhythm patterns (no three long sentences in a row)
   - Pass 3 — For technical prose, audit vocabulary bundles rather than single words: unsupported certainty, unbounded absolutes, personified mechanisms, stacked structural metaphors, repeated verification claims, and em-dash density. Load `humanizer` → `references/load-bearing-claude-vocabulary.md` when this pattern is active; preserve exact evidence.
   - Pass 4 — Replace abstract stand-in words with concrete ones *only where the concrete word is already implied*
   - Pass 5 — Loosen hedging where it's redundant
   - Pass 6 — Restore human shape without adding facts: cut over-explained themes, preserve non-linear movement, avoid stock body-metaphor emotion, keep real specifics, and protect scenes/dialogue/side beats
   - Pass 7 — Check length, structure, and formatting match within tolerance
5. **Re-read aloud.** If a sentence still sounds like an LLM, fix that sentence only. Do not churn the whole paragraph.
6. **Cap at two corrective passes.** If the second pass still fails, report the remaining problem instead of forcing quirks into the prose.
7. **Self-verify the preservation contract:**
   - Does every claim in the original survive? (yes/no)
   - Did I add any new idea, example, or authority? (must be no)
   - Is paragraph count within ±10%? (yes/no)
   - Is length within ±10%? (yes/no)

## Tell-tale LLM tics to strip

- "In today's fast-paced world…"
- "It's worth noting that…"
- "Dive deep into…"
- "Unlock the power of…"
- "At its core…"
- "Moreover / Furthermore / Additionally" as paragraph openers
- Three-item parallel lists when one or two would do
- Endings that summarize what the reader just read
- "Not just X, but Y" cadence overused
- Em dashes deployed as pacing crutch every other sentence
- Empty superlatives — "truly", "profoundly", "remarkably"
- Moral hedges — "It's important to approach this thoughtfully…"

## Detector-aware boundary

This skill improves expression under a strict preservation contract; it does not guarantee a detector label. If the user names Pangram or supplies pass-by-pass detector output, load `iterative-ai-detector-humanization` and, for Pangram, `humanizer` → `references/pangram-4-detector-guidance.md`.

- Do not add typos, filler, fragments, random variation, invented details, or formatting noise to influence a score.
- A materially AI-rewritten draft may accurately remain AI-Assisted/Mixed after a faithful edit.
- Recover wording from the author's drafts, notes, or approved source material when available.
- If genuine human authorship requires new choices or language, stop and return that work to the author; doing it here would violate the no-new-information rule.

## When NOT to use this skill

- Draft has factual errors → fix the errors, don't polish them
- Draft has a broken argument → send it back
- The task is translation, fact-checking, or fact-adding → wrong skill
- The user wants the piece to sound *more* like the reference author → use `gonzo-reference-rewrite-pass` or `reference-style-rewriting`
- The user is feeding you AI-detector flags pass-by-pass (Pangram, ZeroGPT, GPTZero, etc.) → use `iterative-ai-detector-humanization`, which inherits this skill's preservation contract and adds a source-grounded detector protocol
- The piece is fiction or poetry with a deliberately stylized voice → don't flatten it

## Router sanity check

Before finishing, confirm this job did not need the broader `humanizer` router instead. If the edit required new examples, authorial restructuring, detector-score strategy, or screenplay/essay-specific developmental judgment, stop and route to the relevant specialist rather than forcing it through the constrained-editing contract.

## Output format

Return the edited prose only. No change log, no bullet list of what you did, no "I noticed…" preamble. If the user wants a diff, they'll ask.

## When to delegate to the full profile instead

Spawn the `batty-replic-humanization-editor` subagent when:
- The draft is long (3,000+ words) and needs sustained editorial consistency
- The user is explicitly invoking the Batty Replic voice for their own reasons
- You want a second pass from a different lens after your own edit
