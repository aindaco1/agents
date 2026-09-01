---
name: iterative-ai-detector-humanization
description: "Use when revising prose against a named AI detector."
license: "All rights reserved"
metadata:
  version: "2.0.1"
  author: "Dust Wave"
  short-description: "Revise detector-flagged prose without score gaming"
  hermes:
    tags: [writing, editing, humanize, ai-detection, pangram, zerogpt, gptzero, iterative]
    related_skills: [humanizer, constrained-humanization-editing, anti-machine-writing-editorial-pass]
---

# Iterative AI-Detector Humanization

Use this companion to `humanizer` only when a user names a detector, provides a detector report, or is running repeated scans. The goal is not to launder AI-generated text into a “human” label. The goal is to recover real authorship, improve prose, interpret detector output responsibly, and stop before score-chasing damages the work.

Load `humanizer` first. If Pangram is involved, also load `humanizer` → `references/pangram-4-detector-guidance.md` before editing.

## Hard truth

A model cannot make model-generated prose genuinely human-authored by adding quirks. Surface editing may change a detector result, but it does not change who supplied the ideas, language, examples, and decisions.

Use detector results as fallible diagnostic evidence:

- A **Human** result is not proof of human authorship.
- An **AI/AI-Generated** result is not proof of misconduct.
- An **AI-Assisted/Mixed** result may accurately describe a co-written or materially rewritten document.
- Detector scores do not establish factuality, plagiarism, intent, or the complete writing history.

For consequential decisions, require human review and corroborating process evidence such as notes, drafts, source files, or version history.

## First classify the writing process

| Starting point | Correct response |
|---|---|
| Human draft lightly copyedited by AI | Preserve the original human substrate; make minimal changes; accept that detector output can vary. |
| Human draft materially rewritten by AI | Restore the author’s language and decisions from drafts or notes; an AI-Assisted label may be accurate. |
| AI draft built from the author’s notes | Use the draft as scaffolding. Ask the author for wording, examples, choices, and objections; replace model-authored material with those contributions. |
| Predominantly AI-generated draft with no human source | Do not cosmetically “humanize” it. Return it to the author for substantive rewriting or use a normal editorial workflow after they supply original material. |
| Provenance unknown | State that it is unknown. Do not infer authorship from the detector alone. |

## Detector branch

### `load-bearing` PR-cluster classifier

Louis Abraham's `load-bearing` project includes a classifier derived from an unsupervised GitHub pull-request cluster. It can say that a text resembles the arriving cluster; it cannot identify who wrote it. Its corpus and vocabulary are useful for a technical-prose quality audit, not for authorship accusations or general-prose scoring. If the user names it, load `humanizer` → `references/load-bearing-claude-vocabulary.md`, keep the PR-domain limits visible, and edit clustered sentence behavior rather than deleting isolated high-lift words.

### Pangram 4

Pangram 4 is a supervised deep-learning provenance classifier, not a perplexity or burstiness meter. It predicts Human, AI-Assisted, and AI-Generated segments, uses document context, and includes a separate humanizer detector trained on common evasion transformations.

Follow these rules:

- Scan at least 50 words of complete-sentence natural-language prose.
- Prefer the full prose document over isolated sentences; inspect the paragraph around every flagged segment.
- Record the model version, exact input, document fractions, segment labels, and humanizer flag.
- Do not read highlighted words as exact forensic boundaries; overlapping windows, CRF decoding, sentence voting, and minimum-run merging affect the displayed spans.
- A negative or absent humanizer flag is not an independent clearance because Pangram runs that auxiliary head only after the primary detector finds AI evidence.
- Treat its continuous AI-involvement score as a ranking signal, not the probability that the displayed label is correct.
- Treat its confidence as model-internal certainty, not calibrated proof.
- Remove headers, footers, instructions, references, and unrelated boilerplate for the scan, but preserve an untouched master.
- Do not rely on results for source code, reference lists, technical manuals, tables of contents, math-dominated text, short replies, or other out-of-scope inputs.
- If the result is AI-Assisted and substantial AI rewriting actually occurred, do not chase a Human label. The detector may be describing the process accurately.

#### Evidence audit before editorial inference

When the task asks whether Pangram is reliable—not merely how to respond to one scan—load `references/pangram-evidence-audit-2026-08.md` and separate four evidence classes: vendor methodology, vendor-run evaluation, vendor summaries of outside studies, and the underlying externally run studies.

- Preserve the exact metric name and denominator. TPR, FPR, FNR, AUROC, mean accuracy, and “confidence” are not interchangeable.
- Record the Pangram/API version, operating threshold or label rule, corpus, text length, domain, generator, humanization condition, and whether threshold selection used the evaluation corpus.
- Do not port evidence across versions. A result for API v2025-05 or Pangram 3 is not automatically evidence for Pangram 4.
- Do not translate a low FPR into “the accusation is probably true.” Posterior risk also depends on prevalence and domain fit.
- Do not infer a causal style rule from a flagged span. Pangram uses document context and postprocessed boundaries; its own report says isolated and full-context predictions may differ.
- Treat mixed-authorship claims separately from binary AI-vs-human performance. Mixed labels are thresholded summaries and cannot reconstruct intent, prompts, idea provenance, or the writing history.

### Score-only or sentence-highlighting detectors

ZeroGPT, GPTZero, Originality.ai, Copyleaks, Turnitin, and similar tools expose different labels, thresholds, and spans. Do not transfer a tactic or “noise floor” from one detector to another.

- Ask for the detector name, version if shown, full report, and exact input.
- Use highlighted spans as pointers to inspect, not as authoritative boundaries.
- Keep the same detector and scan setup across passes.
- Do not assume a score change was caused by the last edit; document context, thresholding, and service updates can all affect output.

## Evidence-led revision ladder

Move down this list only as far as the author’s material and requested scope allow.

1. **Restore the author’s own language.** Pull from their prior draft, notes, interview answers, approved phrases, or voice sample.
2. **Remove model-added scaffolding.** Cut generic openings, thesis restatements, stock transitions, empty balance, redundant conclusions, and explanations the author did not choose.
3. **Reinstate real process residue.** Preserve genuine hesitation, contradiction, asymmetry, repetition, non-linearity, and rough but alive phrasing already present in human source material.
4. **Replace abstraction with author-supplied specifics.** Ask for the actual place, object, source, example, reaction, or decision. Never invent one to lower a score.
5. **Rebuild the flagged passage around human decisions.** If authorial restructuring is allowed, ask what the writer means, rejects, remembers, or wants to emphasize, then use those answers as the source.
6. **Stop and return authorship to the person.** If the remaining passage is predominantly model-generated and no human material exists, another model pass is the wrong tool.

For a compact version, load `references/strategy-ladder.md`.

## Prohibited detector-gaming tactics

Do not use:

- typo injection, misspellings, random grammar errors, or deliberate ESL mimicry
- Unicode spaces, homoglyphs, casing attacks, invisible characters, or OCR-style corruption
- synonym spinning, translation round-trips, or commercial “humanizer” transformations
- forced telegraphic fragments or arbitrary sentence-length variation
- fake spoken filler such as “honestly,” “kind of,” or “you know”
- coined compounds, random contractions, punctuation churn, or italics added as “entropy”
- invented anecdotes, interior details, named objects, quotations, or false citations
- claims that perplexity, burstiness, unusual vocabulary, or inconsistency reliably signal human authorship

These moves degrade the prose, can misrepresent the writer, and are specifically represented in modern detector training. They also confuse appearance with authorship.

## Iteration protocol

1. **Read fresh.** Re-open the current file or paste before each pass; the author may have hand-edited it.
2. **Snapshot inputs.** Preserve the current text and detector report. Record the scanner and version if available.
3. **Set the target.** Define success as truthful provenance plus good writing—not an arbitrary percentage.
4. **Mark preservation anchors.** Claims, names, numbers, citations, quotations, code, intentional repetitions, formatting, and already-human passages stay fixed.
5. **Diagnose each flagged span.** Decide whether it contains model-added scaffolding, missing human material, a detector limitation, or intentional form that should remain.
6. **Choose one rung.** Make the smallest source-grounded change that addresses the diagnosis. Touch only approved spans unless context requires a wider revision and the user agrees.
7. **Verify meaning.** Compare claims, stance, scope, structure, and formatting against the preserved version.
8. **Rescan consistently.** Use the same exact scan setup. Compare document and segment outputs; do not read causality into one fluctuation.
9. **Stop after two detector-driven passes by default.** Continue only if the author is supplying new original material or the user explicitly wants a controlled experiment. If labels merely migrate between spans, stop.

## Controlled experiments

If the user is researching a detector rather than editing for publication:

- change one variable at a time
- retain exact before/after text and reports
- use multiple human and AI controls
- repeat the scan when possible
- describe results as observations for that detector/version/input, not universal writing rules

Anecdotal pass histories can inspire hypotheses, but they are not evidence that a tactic generalizes. `references/joe-frank-low-flame-case-study.md` is retained only as a historical ZeroGPT session log and must not override this workflow.

## Preservation contract

Inherit `constrained-humanization-editing` unless the user explicitly permits developmental or authorial changes:

- no new facts, examples, metaphors, anecdotes, names, or claims
- no stance drift
- preserve formatting and approximate length
- preserve deliberate repetitions and user-approved hand edits
- preserve already-human passages
- verify every revision against the source

If detector pressure conflicts with these rules, preservation wins.

## Stopping rules

Stop when any one is true:

- the prose is accurate, alive, and faithful to the author’s material
- the current label accurately reflects real AI assistance
- further improvement requires original human choices or content
- the detector is being used outside its documented scope
- changes are causing stance drift, false detail, awkwardness, or damage to deliberate form
- scores or labels oscillate without a stable, source-grounded improvement
- two detector-driven passes have not materially improved both prose and provenance

Never promise a target score or a Human classification.

## Output

For each pass, return:

1. the revised text or applied file edit
2. a short preservation note when needed
3. a compact scan log:

```text
Detector/version: [name/version or unknown]
Exact input scope: [full document / section]
Before: [document label/score + relevant spans]
Edits: [source-grounded changes only]
After: [user-supplied result, if available]
Stop reason / next source needed: [plain statement]
```

Do not fabricate an “after” result. Only report a detector outcome the user supplied or a scan actually run with an available tool.

## Related references

- `humanizer` — master router and single-pass editorial audit
- `humanizer` → `references/pangram-4-detector-guidance.md` — concise Pangram architecture, scope, and scan protocol
- `humanizer` → `references/load-bearing-claude-vocabulary.md` — sourced GitHub PR-cluster vocabulary, evidence limits, and technical-prose editing protocol
- `references/pangram-evidence-audit-2026-08.md` — detailed methodology, external-evidence conditions, failure modes, and editorial due-process guidance
- `constrained-humanization-editing` — faithful-editing preservation contract
- `anti-machine-writing-editorial-pass` — broader quality-and-voice pass when no detector loop is needed
- `references/strategy-ladder.md` — compact source-grounded ladder
