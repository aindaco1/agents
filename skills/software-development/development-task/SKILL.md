---
name: development-task
description: Use when implementing or verifying substantive changes.
metadata:
  version: 1.1.1
  author: Dust Wave
  hermes:
    tags: [development, verification, context]
    related_skills: [improve-agent-instructions, review-development-lessons]
---

# Development task

Inspect the actual checkout and applicable AGENTS.md first. Find the existing
owner of the behavior. Retrieve only the relevant project references and procedure;
do not load the whole roster or wiki. Verify drift-prone claims against code,
configuration, or the live service within the authorized task.

For substantial work, use [task-record.md](templates/task-record.md) in the task's
local working directory. Define the requested observable outcome, allowed scope,
and acceptance evidence. Keep it short and update it at natural handoff points.
For substantive implementation or review, read
[acceptance-evidence.md](references/acceptance-evidence.md). Define what observable
result would establish each important claim before changing or assessing it.
Functional fixes count as substantive even when the diff is small. Before the
final completion report for a functional fix or substantive review, save a short
local acceptance note (reuse the task record when present) with tested file hashes
or commit plus patch/new-file identity, environment, actual checks/results and
remaining limits. Link that note in the report. For source-only review, identify
the inspected files and unperformed runtime checks. Trivial documentation or
cosmetic edits do not require a note or new tests.

Reproduce bugs and identify the smallest coherent fix. Preserve user edits,
compatibility, runtime state, and unrelated behavior. Put shared pure invariants
in their existing shared owner; keep consumer integration and release acceptance
with consumers. Use isolated worktrees/runtime homes when changing stateful tools.

Run focused behavioral tests and required repository checks. Exercise failures,
retries, idempotency, or stale state when relevant. Test before live application;
canary a bounded target, compare protected state, and retain a usable rollback.
For agent pilots, use the owning project's guarded harness: verify resolved
runtime paths, prevent access to live private state, and retain consistent SQLite
before/after snapshots with logical comparisons. Integrity checks or main-file
hashes alone do not prove preservation, especially with WAL enabled. Unexplained
changes or missing snapshots fail the preservation gate; keep the evidence.
UI, hardware, and deployment claims require evidence from those actual surfaces.
Inspect the evidence before citing it; record expected versus observed behavior,
the tested revision/environment, real or simulated boundaries, and relevant
failure checks. Relevant later edits invalidate the affected evidence. When an
essential check is unavailable, finish independent authorized work and identify
the exact unverified claim. Do not turn a trivial edit into a verification project.

When reviewing, retain the full-diff first pass and the role's existing boundaries.
Assess whether evidence supports the current change, then inspect critical code
for correctness, shared contracts, data loss, authorization and concurrency.
Successful demos do not remove review obligations or authorize feature work.

Report the change, validation, and unresolved limitations. Distinguish implemented,
tested, merged, deployed, and verified in the affected workflow. A passing model
score does not replace deterministic tests or release authority.

Capture a learning candidate only when it changes future behavior. Prefer a code
fix or regression test for an enforceable invariant; a skill for a repeatable
procedure; a brief memory entry for an authorized durable fact. Preserve existing
memory permissions. Start a fresh session at a natural task boundary when testing
cross-session recall; a saved file alone does not prove runtime retrieval.
