---
name: development-task
description: Use when implementing or fixing substantive code.
metadata:
  version: 1.0.0
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

Reproduce bugs and identify the smallest coherent fix. Preserve user edits,
compatibility, runtime state, and unrelated behavior. Put shared pure invariants
in their existing shared owner; keep consumer integration and release acceptance
with consumers. Use isolated worktrees/runtime homes when changing stateful tools.

Run focused behavioral tests and required repository checks. Exercise failures,
retries, idempotency, or stale state when relevant. Test before live application;
canary a bounded target, compare protected state, and retain a usable rollback.
UI, hardware, and deployment claims require evidence from those actual surfaces.

Report the change, validation, and unresolved limitations. Distinguish implemented,
tested, merged, deployed, and verified in the affected workflow. A passing model
score does not replace deterministic tests or release authority.

Capture a learning candidate only when it changes future behavior. Prefer a code
fix or regression test for an enforceable invariant; a skill for a repeatable
procedure; a brief memory entry for an authorized durable fact. Preserve existing
memory permissions. Start a fresh session at a natural task boundary when testing
cross-session recall; a saved file alone does not prove runtime retrieval.
