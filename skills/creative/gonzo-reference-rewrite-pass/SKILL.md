---
name: gonzo-reference-rewrite-pass
description: "Use when adapting essays to an irreverent reference."
license: "All rights reserved"
metadata:
  version: "1.0.0"
  author: "Dust Wave"
  short-description: "Shape lively essays from a reference without imitation"
  hermes:
    tags: [writing, editing, reference, voice]
    related_skills: [humanizer, writing-craft-library, anti-machine-writing-editorial-pass, constrained-humanization-editing]
---

When to use
- The user wants a new draft to sound like an existing piece they like.
- The job is not pure copyediting; it requires tone transfer, structural adaptation, and humanizing prose.
- A publication-ready file has to be produced, not just notes.

Workflow
1. Read the reference piece in full.
   - Load the exact article the user wants to emulate.
   - Identify sentence length variation, joke density, level of meanness, rhythm, paragraph size, and how often the piece uses scene-setting or concrete examples.
   - Use `reference-style-rewriting` for access and provenance checks. If only part is accessible, state the limit; do not claim to have read the full piece or infer its ending.
   - For additional craft examples, use `writing-craft-library` and select at most two relevant cards. Transfer high-level techniques, not distinctive phrasing, incidents, or the reference author's opinions.

2. Read the source draft in full.
   - Preserve the argument and facts.
   - Make a short note of what must survive: thesis, anecdotes, named entities, links, intended publication outlet, and any required frontmatter or file structure.

3. Draft the new version in one pass.
   - Rewrite for tone, not mimicry.
   - Favor concrete scenes, stronger nouns and verbs, sharper transitions, and a looser human cadence.
   - Avoid machine-writing tells: repetitive openings, listy rhythm, one-sentence-paragraph overuse, habitual em-dash clauses, and recycled metaphor families.
   - If the user wants gonzo-style energy, allow swagger, humor, and a little menace, but keep the argument legible.
   - Keep already-approved substance and paragraph logic stable during a style-only pass. Preserve a separate version for each major change in intensity.
   - Use only supplied or independently verified facts and scenes. If the source lacks the material a technique requires, omit the technique or identify the gap.

4. Place the draft directly into the destination format.
   - If there is an existing site/article format, write into that format instead of leaving the piece as a loose text draft.
   - Preserve frontmatter, image blocks, captions, and house style.

5. Do a second pass for readability.
   - Tighten sections that sound too symmetrical or synthetic.
   - Replace abstract summary language with a few concrete lines where possible.
   - Break any accidental algorithmic rhythm.

6. Add formatting and links sparingly.
   - Use bold only for central turns, punchlines, or key claims.
   - Use italics for managerial boilerplate, quoted social language, or tonal stress.
   - Add links where cultural or technical references benefit from context, not as decoration.
   - In mixed markdown/HTML files, match the house style already present in the file.

7. Verify by reading the edited file back.
   - Confirm the new links actually exist.
   - Check that emphasis is restrained.
   - Check that no broken markup was introduced.

Editing tactics that worked
- Use the reference piece as a calibration source, then draft the new piece directly rather than trying to patch style sentence by sentence from the start.
- After the main rewrite, do a dedicated anti-machine-writing pass focused on sentence behavior, not just vocabulary.
- If patch-based editing becomes awkward or ambiguous for large prose changes, switch to a full-file read/transform/write workflow rather than forcing brittle patches.
- For the final polish, return to targeted patches for small emphasis or link insertions.

Pitfalls
- Do not overdo bold and italics; the goal is readability, not stage makeup.
- Do not let the rewrite collapse into imitation of surface quirks.
- Do not keep asking the user how aggressive to be when the reference piece already answers that question.
- Do not stop after patching; always read back the final file.
- Do not make every paragraph funny, jagged, or quotable. A deliberate quiet passage may be carrying the contrast.
- If strict faithful editing applies, its preservation contract wins over a reference's energy or structure. Route through `humanizer` when the requested scope is unclear.

Definition of done
- The piece matches the requested tone better than the source draft.
- It reads like a lively human essay rather than machine-smoothed prose.
- The destination file is publication-ready.
- Links and emphasis have been verified in the final file.
