# Writing craft library pilot — November 18, 2026

The annotated library and both previously Hermes-only reference procedures are now canonical and published to Hermes and Codex. The library has **24 development sources under six bylines, 12 craft cards, and 12 held-out articles under three other bylines**. Eight held-out articles supplied preservation inputs; four remain unused reserves. It ships original commentary and provenance, not copied article bodies.

## Pilot result

We completed **24 paired cases (48 writing answers) and 24 blinded model judgments**: eight preservation tasks, eight editing tasks, and eight original drafting briefs. These are exploratory comparisons. The full pilot did **not** clear its acceptance gates: preference wins must exceed losses, and all declared live-state comparisons must pass.

| Task group | Candidate preferred | Baseline preferred | Tie |
|---|---:|---:|---:|
| Preservation | 0 | 0 | 8 |
| Editing | 0 | 0 | 8 |
| Drafting | 0 | 0 | 8 |

Material fidelity failures flagged by the judge: baseline 0, candidate 0. Noncritical instruction failures: baseline 2, candidate 0. The baseline thank-you note and notice were each one word below their minimum under whitespace-based counting. Both conditions left seven of eight preservation excerpts unchanged and made the same small clarity repair in the eighth. Primary-agent review inspected all paired answers and the judge's reasons; it is not independent human adjudication.

Thirteen pairs produced identical text. The remaining eleven received tie judgments. These short, tightly constrained tasks and the fidelity-first rubric may have limited the pilot’s ability to distinguish subtler craft differences.

The library remains optional. This pilot does not establish a general writing-quality improvement or a benefit for the user's own voice. A useful next test would use representative user drafts and blind user preferences; it should run after the live gateway is stable. No detector score or model-weight training was used.

## What changed

- Added [writing-craft-library](../../skills/creative/writing-craft-library/SKILL.md), with cards for qualified judgment, concrete detail, sustained syntax, purposeful repetition, comic distance, distinct speakers, visible uncertainty, attribution, endings, specific criticism, empathy with limits, and precise distinctions.
- Imported [reference-style-rewriting](../../skills/creative/reference-style-rewriting/SKILL.md) and [gonzo-reference-rewrite-pass](../../skills/creative/gonzo-reference-rewrite-pass/SKILL.md), preserving style-only approvals, separate versions, factual limits and existing user preferences. Added portable metadata and access/provenance checks.
- Added optional library guidance to the humanizer and editorial procedures. Replaced the strict editor's sentence-length quota with a requirement to identify an actual problem while preserving deliberate long sentences and repetition.

## Sources and method

The [corpus manifest](corpus.json) records original URLs, capture timestamps, bylines and the development/held-out split. The [case index](cases.json) records identities, criteria and prompt hashes without redistributing archived prose. Source annotations identify the specific inspected paragraphs and limits; they do not endorse entire articles or treat historical opinion as current fact. Interview speakers and letter writers are distinguished from column bylines. Old publication dates do not prove unfamiliarity to the model.

Both conditions used the installed default model, **gpt-6-astra with xhigh reasoning**, through Hermes's AIAgent API. Each case started a fresh agent in a synthetic home with tools, live memory, context files and background review disabled. Relevant procedures were supplied explicitly; the candidate also received the library core and at most two selected cards. This tests supplied-context behavior, not autonomous retrieval. The judge received randomized A/B labels, the task and a fixed rubric, without the procedure packets or label map. The combined candidate cannot isolate the effect of individual cards.

Preservation/editing batches alternated condition order. After a runner correction, all drafting pairs were regenerated in matched baseline/candidate suites with two cases per guarded run. The first four completed baseline drafts were retained but excluded; no candidate draft had completed before the correction. No skill text, task, model, reasoning effort or rubric was tuned after generation began.

## Runner and state-audit limitations

The first connectivity preflight failed and was retained. A fresh preflight passed after disabling dependency auto-provisioning and resolving the provider's public addresses before entering the guard. TLS hostname verification, protected roots and localhost restrictions remained enabled.

The initial 110-second soft agent budget caused Hermes to retire drafting streams after 60 seconds despite progress. The corrected drafting homes used explicit 180-second provider stale timeouts, 195-second request timeouts, a 200-second soft agent budget and no automatic recovery; the harness retained its 600-second hard process limit. The final judge batch also used explicit provider timeouts. Live runtime configuration was not changed.

Before/after SQLite snapshots compare all four declared writing-profile stores. Four generation/judging runs failed their audit or execution gate. During the interrupted candidate batch, all four stores' `runtime_epoch` rows changed from 783 to 784. During later drafting and judging, epochs changed again to 785. Separate gateway logs show watchdog exits and supervised restarts over these intervals, consistent with concurrent service activity; this is not proof of attribution. No conversation-table differences were detected in those comparisons. Failed runs remain failed, and no epoch was ignored or restored. The retained answers can inform the exploratory quality comparison but cannot establish unchanged-state acceptance.

## Resources

Observed counters for the 48 selected writing answers and 24 judgments:

| Condition | Answers | Prompt tokens, including cached | Output tokens | Summed call seconds |
|---|---:|---:|---:|---:|
| Baseline | 24 | 105,942 | 18,963 | 570.2 |
| Candidate | 24 | 143,357 | 20,611 | 608.8 |
| Judge | 24 | 36,730 | 9,498 | 307.0 |

Summed call time is not wall-clock time because some suites overlapped. Counters exclude discarded drafts and incomplete transport attempts; raw logs retain those overheads. The existing subscription OAuth path was used with no paid-API fallback or purchase. Monetary cost is unavailable. No efficiency claim is supported.

## Publication and validation

All **12 runtime package copies** match the frozen candidate sources. Fresh native catalog processes discover all six packages in Codex and in the Hermes Batty, Editor, Creative Writer and Ghostwriter profiles. Codex behavioral inference was not tested. Existing Hermes usage counts and unrelated records were preserved. 2,607 of 2,609 checked unrelated/configuration/memory files were byte-identical. Two Codex-generated files (`~/.codex/memories/raw_memories.md` and `~/.codex/memories/MEMORY.md`) changed over the wider inventory window, outside every skill-publisher write path; the broad file-preservation audit is therefore recorded as failed. The task did not write or restore those files. A separate before/after database comparison across publication and native discovery passed for all four Hermes stores. Publication used an inspected preview, exact plan hash, shared managed-file writer and retained transaction backups outside iCloud. A fixture rehearsal also preserved unknown files and legacy usage history.

Repository validation: **156 passed, 1 skipped**. The skip is an unrelated optional tracing test whose Pillow dependency is absent from the explicit venv. Roster aggregate, Codex persona mirror, portable-skill parity and whitespace checks passed. No persona entries changed, and the web-application-builder procedure was preserved.

The machine-readable [results](results.json) include case judgments, checks, counters and audit statuses. Private source captures, raw inputs/answers, frozen packages, protocol amendments, snapshots, publication receipts and the task record are outside iCloud/Git at `/Users/aindaco1/.local/share/agents-evidence/2026-11-18-writing-pilot`. The baseline repository revision was `c19ab47c0cc7f63e531cce1f3c7e486b450ffebb`; final file hashes identify the working-tree revision actually published. This task made no memory, scheduling or external communication changes.

A subsequent [close reading of 32 Salon articles](salon-close-reading.md) informed later paragraph and transition guidance after Alonso judged three of his own drafts. The pilot results above describe the earlier versions.
