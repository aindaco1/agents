---
name: anti-machine-writing-editorial-pass
description: "Use when essays need an anti-machine editorial pass."
license: "All rights reserved"
metadata:
  version: "1.0.0"
  author: "Dust Wave"
  short-description: "Remove machine rhythm while preserving live prose"
  hermes:
    tags: [writing, editing, humanize, essays, voice]
    related_skills: [humanizer, constrained-humanization-editing, iterative-ai-detector-humanization]
---

When to use
- The `humanizer` master router selects the essay/article anti-machine mode.
- User says a draft feels like "machine writing," "LLM-ish," too repetitive, too symmetrical, too clean, or too slogan-y.
- You are revising essays, opinion pieces, artist statements, newsletters, or gonzo-style cultural criticism.
- The draft has some good voice already, but certain paragraphs break the illusion by sounding templated.

Do not use this for strict faithful edits where no new examples, scene beats, or structural movement are allowed; use `constrained-humanization-editing` instead.

Goal
Make the piece feel more like a live human mind moving on the page, not a model producing cadence.

Process
1. Identify the real tells
   Look for:
   - repeated sentence openings ("You start... You start... You start...")
   - evenly spaced fragment chains
   - stacked parallel clauses
   - balanced triples and clean rhetorical ladders
   - one-sentence paragraphs used too often
   - over-clean thesis lines that sound pre-packaged
   - repeated metaphor families in nearby paragraphs
   - theme sentences that explain the point after the reader already got it
   - over-straight chronology where a memory, consequence, or later return would feel more natural
   - generic body-metaphor emotion (heart/chest/stomach/breath/weight) standing in for actual behavior
   - generic references where a real text, place, brand, object, venue, or quoted phrase belongs
   - a single clean through-line with no scene changes, side beats, dialogue, or friction
   - lists that read like generated emphasis rather than lived observation
   - inanimate objects vaguely "humming"
   - metaphors that sound elevated but do not actually make sense
   - repeated "not X, not Y, but Z" constructions
   - character descriptions built from fragment chains ("Adjective. Adjective. Compound adjective.")
   - environment descriptions built from noun piles ("Nouns. Nouns. A scattering of nouns.")
   - script beats that announce impact with "That lands" instead of showing the room change
   - dialogue where characters bat labels around without pressure, stakes, or concrete speech
   - in technical prose, clusters of certainty adverbs, totalizing scope, personified system behavior, mechanical metaphors, proof/verification compounds, and dense em-dash pivots

   When the source is a pull request, engineering note, changelog, or known Claude-assisted draft, load `humanizer` → `references/load-bearing-claude-vocabulary.md`. It is a corpus-derived cluster audit, not a word blacklist or authorship test. Preserve exact technical evidence.

2. Preserve the alive paragraphs
   Keep the paragraphs that feel scene-based, specific, and observational. These usually have:
   - concrete setting details
   - irregular sentence lengths
   - human digression
   - attitude without over-explaining
   Use those as the tonal anchor for the rest of the piece.

3. Rewrite by changing sentence behavior, not just words
   The problem is often rhythm, not vocabulary.
   Better moves:
   - collapse repetitive short lines into one longer, more textured sentence
   - replace abstract escalation with one concrete image or social detail
   - vary sentence openings and clause lengths
   - let one sentence do sideways work instead of stacking 4 interchangeable lines
   - combine adjacent mini-paragraphs if they create artificial drama
   - keep a few punchy lines, but make them earned

4. Prefer lived phrasing over generic emphasis
   Example pattern:
   - Bad: repeated moral/rhetorical drumbeat
   - Better: a sentence that notices behavior in a room, a tone, an institution, a social type
   The rewrite should sound like somebody remembering, noticing, judging, and improvising — not presenting a polished content structure.

5. Restore human narrative shape when the brief allows it
   Use the study-backed tells as a practical checklist:
   - **Infer, don't explain:** remove the extra sentence that announces the theme.
   - **Let time move sideways:** essays, memoir, cultural criticism, fiction, and newsletters can jump backward or forward instead of marching point-by-point.
   - **Emotion through behavior:** swap stock bodily feeling for action, attention, interruption, dialogue, omission, or a precise object.
   - **Specific references:** name the actual song, film, street, shop, app, tool, institution, or text when it is true and known. Do not fabricate specificity.
   - **More scenes, more voices:** where authorial scope allows, add a brief exchange, a second scene, a contradiction, or a side beat rather than another summary paragraph.

6. Add formatting sparingly
   Use emphasis only where it helps scanning:
   - italics for quoted language, euphemisms, or internal framing
   - bold for a few core phrases or contrasts
   - links only where they add real referential value
   Do not turn the article into typographic confetti.

7. Verify after editing
   Read back the changed sections and check:
   - does the paragraph still arrive in evenly timed beats?
   - do multiple nearby paragraphs use the same trick?
   - did the rewrite become too polished again?
   - is the emphasis restrained?
   - did you let the reader infer at least some of the meaning?
   - did you preserve or add human specificity without inventing facts?

Heuristics
- Keep some mess. Too much smoothing kills the voice.
- Human writing can be sharp, but it should not sound like it was optimized in a lab.
- If a paragraph feels quotable in every sentence, it is probably overworked.
- A specific room beats a general thesis.
- One good image beats three abstract claims.

Detector boundary
- This is a quality-and-voice pass, not a detector-evasion recipe.
- If the user names Pangram or supplies detector results, route through `iterative-ai-detector-humanization`; for Pangram, load `humanizer` → `references/pangram-4-detector-guidance.md`.
- Do not treat sentence-length variation, unusual vocabulary, perplexity, or burstiness as proof of human authorship.
- Use real human source material—drafts, notes, examples, choices, and voice—not synthetic quirks.
- Never promise a detector score or Human classification. AI-Assisted/Mixed may accurately describe materially co-written prose.

Pitfalls
- Replacing one LLM tell with another, especially chains of clever fragments
- Overusing em dashes or aphoristic endings
- Adding too much bold/italics because the prose still is not carrying its own weight
- Making every paragraph sound equally intense

Useful editorial moves from this session
- Rewrite repeated opener structures into a single sentence with texture and social observation.
- Convert stacked managerial-language lines into a single italicized block, then gloss it once.
- Replace repeated fragment paragraphs with mixed-length sentences and a stronger observational center.
- Add links only to organizations/places actually named in the piece when it helps orientation.

Deliverable
Return the revised file and briefly tell the user what rhythmic/tone problems were corrected, not just that "the draft was improved."