---
name: humanizer
description: "Use when prose needs humanization or mode routing."
license: MIT
metadata:
  version: "3.2.0"
  author: "Siqi Chen; extended by Hermes Agent"
  short-description: "Route and humanize prose without flattening voice"
  hermes:
    tags: [writing, editing, humanize, anti-ai-slop, voice, prose, text]
    homepage: https://github.com/blader/humanizer
    related_skills: [constrained-humanization-editing, anti-machine-writing-editorial-pass, iterative-ai-detector-humanization]
---

# Humanizer: master routing skill

Use this as the entry point for any request to humanize, de-AI, de-slop, un-ChatGPT, de-tic, or make writing sound less machine-made.

Core principle: humanization is mostly subtraction plus voice preservation. Remove the machine scaffolding first. Do not spray slang, typos, fragments, contractions, or fake personality onto a flat draft. If the text lacks the material needed for real voice, say so or ask for source material.

## First decision: what kind of job is this?

Pick one mode before editing. Do not blend contracts.

| Mode | Use when | Contract | Load / use |
|---|---|---|---|
| General one-shot cleanup | User asks broadly to humanize pasted text, email, memo, summary, PR text, post, or docs | Preserve meaning and structure; improve wording and rhythm | This skill |
| Constrained faithful edit | User says preserve meaning/length/format, or the draft is already correct but stiff | No new ideas, no new examples, paragraph count and length within about ±10% | `constrained-humanization-editing` |
| Essay/article anti-machine pass | Essay, newsletter, cultural criticism, artist statement, opinion piece; some voice is already present | Preserve the live paragraphs; fix rhythm, symmetry, over-explanation | `anti-machine-writing-editorial-pass` |
| Screenplay / creative prose | Script, fiction, treatment, monologue, artist statement, pitch prose | Preserve process residue; fix scene/dialogue tells; do not over-polish into dead competence | This skill + `references/creative-writing-audit.md` |
| Detector loop | User names Pangram, ZeroGPT, GPTZero, Originality, Copyleaks, Turnitin, gives a score, or pastes flagged spans | Recover real authorship from human source material; interpret spans cautiously; never promise a classification | `iterative-ai-detector-humanization` |
| Voice/reference style | User provides a writing sample or asks to sound like a specific author/reference | Match cadence and selection patterns, not borrowed content | `reference-style-rewriting` or `gonzo-reference-rewrite-pass` when authorial |
| Documentation | Technical docs, README, API guide, codebase docs | Preserve code blocks, commands, URLs, headings, facts; improve scanability | This skill plus docs-specific judgment |
| Claude-associated technical prose | PR descriptions, issue reports, changelogs, or engineering notes with clustered certainty, personified systems, mechanical metaphors, verification stacks, or dense em dashes | Preserve technical evidence; remove accumulated rhetorical staging | This skill + `references/load-bearing-claude-vocabulary.md` |

If multiple modes apply, the strictest preservation contract wins.

## Non-negotiables

- Preserve the user's actual meaning unless they explicitly ask for a rewrite with new ideas.
- Preserve code, commands, URLs, citations, quoted material, legal/statutory text, names, and domain terms.
- Keep already-human passages untouched. Do not revise a paragraph just because you can.
- Do not optimize for detectors at the expense of the work.
- Do not flatten deliberate style: repetition, fragments, dashes, slang, or odd syntax may be the author's voice.
- Do not invent specificity. If a draft needs a real place, object, source, quote, or anecdote, mark the gap or ask.
- Cap ordinary cleanup at two passes. A third pass usually starts manufacturing quirks and damaging voice.

## The routing workflow

1. **Classify the text.** Identify genre, audience, stakes, preservation level, and whether a detector is involved. Completion: one mode selected from the table.
2. **Find preservation anchors.** Mark claims, numbers, names, quotes, code, URLs, headings, intentional repetitions, and the best alive paragraphs. Completion: anchors will not be changed except for typo-level fixes.
3. **Audit for machine residue.** Use the short checklist below first. Use `references/ai-pattern-catalog.md` only when you need the full 29-pattern catalog.
4. **Rewrite only where the audit finds a real problem.** Prefer small targeted edits. For files, use `patch` when practical; use `write_file` only for full-document rewrites.
5. **Second pass: human shape.** Ask whether the draft still feels prompt-shaped: too symmetrical, too explanatory, too clean, too generic, too evenly paced.
6. **Final verification.** Read the changed text aloud mentally. Check preservation, formatting, and whether any new AI tell was introduced.

## Fast audit: highest-yield AI tells

Use this before the long catalog.

### Content and rhetoric
- Inflated significance: "pivotal", "testament", "underscores", "broader landscape".
- Vague authority: "experts say", "industry observers", "many argue" without a source.
- Fake balance: "while X, it is important to note Y".
- Formulaic conclusions: "the future looks bright", "exciting times ahead".
- Meta-signposting: "let's dive in", "here's what you need to know".
- Persuasive authority tropes: "at its core", "the real question is", "what truly matters".

### Sentence behavior
- Rule-of-three everywhere.
- "It's not just X, it's Y" / "not X, not Y, but Z".
- False ranges: "from X to Y" where X/Y are not a real scale.
- Synonym cycling to avoid repetition.
- Present-participle padding: "highlighting", "underscoring", "reflecting", "showcasing".
- Copula avoidance: "serves as", "stands as", "boasts", "features" when "is" or "has" is cleaner.

### Surface tells
- Em dash or en dash overuse as automatic drama.
- Bolded inline-header bullet lists.
- Title Case headings where sentence case fits.
- Emoji decoration in serious prose.
- Chatbot residue: "Of course", "Great question", "I hope this helps", "let me know".
- Uniform hyphenation of common compounds: "high-quality", "data-driven", "cross-functional" everywhere.

### Human-shape tells
- Every paragraph has the same logical move.
- Every sentence lands with equal polish.
- The text explains its theme after the reader already got it.
- Emotion is outsourced to stock body metaphors: heart, chest, stomach, breath, weight.
- Generic nouns stand where real objects, institutions, tools, places, or quotes should be.
- The piece has no friction: no contradiction, hesitation, scene, side beat, or process residue.

### Claude-associated technical-prose cluster

For pull requests and engineering prose, also watch the *accumulated register*: certainty adverbs, totalizing scope, personified system behavior, mechanical or spatial metaphors, stacked proof/verification compounds, and dense em-dash pivots. These families come from an unsupervised GitHub PR corpus, not a verified authorship study. Diagnose bundles, not isolated words; preserve exact tests and technical terms. Load `references/load-bearing-claude-vocabulary.md` for the sourced vocabulary, evidence limits, and editing protocol.

## Voice calibration

If the user provides a sample of their writing, analyze it before rewriting.

Look for:
- sentence length distribution
- paragraph openings
- diction level
- punctuation habits
- contraction habits
- tolerance for fragments
- how they transition
- how they joke, hedge, qualify, or refuse polish

Match these patterns without copying phrases or importing ideas. Voice is selection and rhythm, not costume.

## Genre-specific guidance

### Docs and technical writing

Humanize for clarity, not personality.

- Preserve code blocks, CLI commands, flags, paths, URLs, API names, and headings unless wrong.
- Replace passive/abstract process prose with direct instructions.
- Prefer progressive disclosure: start with the useful action, then detail.
- Avoid fake warmth. Good docs sound like a competent person saving the reader time.
- If editing a file, tell the user to review with `git diff` or show the diff.

### Emails, memos, operational writing

- Cut throat-clearing and fake enthusiasm.
- Put the ask or decision near the top.
- Keep the sender's authority level intact.
- Do not over-soften conflict. Clear is kinder than padded.

### Essays, newsletters, criticism

- Preserve alive paragraphs and use them as the tonal anchor.
- Let time move sideways when the form allows it.
- Replace abstract escalation with one concrete image, room, institution, behavior, quote, or contradiction when already available.
- Do not make every paragraph quotable. That is another machine smell.

### Screenplays and creative prose

Use `references/creative-writing-audit.md` for the detailed Scammell pass. Short version:

- Cut objects vaguely "humming" unless the sound is concrete and story-relevant.
- Replace "That lands" with a room reaction, silence, interruption, avoidance, mistake, or changed behavior.
- Fix word-batting dialogue where characters trade labels without pressure or stakes.
- Replace adjective-fragment portraits and noun-pile settings with details that reveal selection.
- Preserve the marks of the writer wrestling with the material. Perfect structure without residue feels dead.

## Detector-aware work

Only enter a detector loop when the user explicitly supplies a detector result or asks for controlled detector research. Load `iterative-ai-detector-humanization`. If Pangram is involved, also load `references/pangram-4-detector-guidance.md`.

- Treat detector output as probabilistic diagnostic evidence, not proof of authorship or misconduct.
- Establish the writing process first: human draft, AI-polished draft, materially co-written draft, or predominantly AI-generated draft.
- Recover the author's real language, choices, notes, examples, and process residue instead of adding synthetic quirks.
- Use flagged spans as pointers and read their context. Pangram 4 uses overlapping document windows and sentence-level postprocessing, so isolated-sentence edits can move neighboring labels.
- Accept AI-Assisted/Mixed when it accurately reflects substantial AI involvement. A model pass should not launder provenance into a Human label.
- Keep the detector/version, input scope, and formatting cleanup fixed across scans. Never infer causality from a single score movement.
- Stop after two detector-driven passes by default or sooner when further improvement requires original human material.

Do not use tokenizer attacks, Unicode tricks, typo spam, synonym spinning, translation-roundtrip laundering, filler, fragment spam, random italics, or invented details. Pangram 4 explicitly trains a humanizer head on common evasion transformations, and these moves damage the work regardless of whether a weaker detector reacts to them.

## Output rules

Default:
- Return the revised text only when the user asks for a practical humanization.
- Preserve markdown structure unless the user asks for reformatting.
- Do not wrap the whole answer in a code fence unless raw markdown copy/paste is required.

When useful or requested:
- Briefly list what changed.
- For file edits, show or summarize the diff.
- If the text cannot be made genuinely human without new material, say exactly what is missing.

## Supporting references

- `references/ai-pattern-catalog.md` — full 29-pattern catalog from `blader/humanizer` / Wikipedia Signs of AI Writing.
- `references/load-bearing-claude-vocabulary.md` — corpus-based Claude-associated technical/PR vocabulary, limits, and cluster-level editing protocol from `louisabraham/load-bearing`.
- `references/creative-writing-audit.md` — Joshua Scammell screenplay and process-residue audit.
- `references/pangram-4-detector-guidance.md` — sourced Pangram 4 architecture, scope, evidence limits, and detector-aware editorial protocol.
- `references/worked-example.md` — full before/draft/audit/final example.

## Attribution

This skill began as a Hermes port of [blader/humanizer](https://github.com/blader/humanizer) by Siqi Chen, MIT licensed, based on Wikipedia's "Signs of AI writing" guide by WikiProject AI Cleanup. The full original pattern catalog is preserved in `references/ai-pattern-catalog.md`. Later Hermes additions add routing, constrained-editing contracts, docs-specific preservation, the Joshua Scammell creative-writing audit, the `louisabraham/load-bearing` technical-prose cluster audit, and Pangram-informed detector safeguards that prioritize truthful provenance over score-gaming.
