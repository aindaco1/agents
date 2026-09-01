# Historical ZeroGPT Retrospective: “Low Flame”

This note records why an earlier score-chasing workflow was retired. It is not a strategy guide.

## What happened

A whisper-register audio drama was scanned repeatedly with ZeroGPT. Across seven passes, the reported score moved down, back up, and down again while several kinds of edits were changed at once. The session also included author hand-edits and scope restrictions between scans.

Because the experiment did not hold one variable constant, it cannot establish that fragments, filler, invented quirks, contraction changes, or formatting caused any score movement. It also cannot establish a detector-specific “noise floor.” Those claims were removed from the current skill.

## What remains useful

- Re-read the current file before every pass; author hand-edits are canonical.
- Preserve explicit no-touch sections even when a detector flags them.
- Preserve deliberate repetition and form when the author keeps it after review.
- Record the exact detector, version, input, and before/after report.
- Do not infer a universal writing rule from one document-detector sequence.
- Do not use formatting, errors, filler, fragments, or invented detail as detector entropy.
- Stop when further improvement requires original human language or choices.

## Current rule

Follow the parent skill’s evidence-led ladder. For Pangram, load `humanizer` → `references/pangram-4-detector-guidance.md` and this skill’s `references/pangram-evidence-audit-2026-08.md`.
