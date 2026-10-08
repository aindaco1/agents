---
name: improve-agent-instructions
description: Use when improving AGENTS.md or Hermes instructions.
license: MIT
metadata:
  version: 1.0.0
  author: HumanLayer; adapted for Codex and Hermes
  upstream: https://github.com/humanlayer/skills/tree/ca7c8088db69e315a8b2deea43820270457f8f3c/plugins/improve-claude-md/skills/improve-claude-md
  upstream_commit: ca7c8088db69e315a8b2deea43820270457f8f3c
  hermes:
    tags:
    - instructions
    - codex
    - hermes
    related_skills: []
---

# Improve Agent Instructions

Adapt HumanLayer's conditional-relevance approach to Codex and Hermes. Improve the selected `AGENTS.md`, `AGENTS.override.md`, or explicitly requested Hermes instruction/profile file. If migrating `CLAUDE.md`, retain it unless its removal was requested.

## Inspect the actual instruction chain

Read the target and applicable parent/nested instructions before editing. Check the runtime and repo conventions rather than assuming a filename is loaded. `AGENTS.md` is the shared project convention; Hermes also has profile `SOUL.md` and memory/context files with different roles. Do not silently rewrite global instructions, profile identities, memories, or unrelated scopes.

Inventory:

- Project identity, short directory map, and essential stack context.
- Every existing command, including its working directory, flags, and prerequisites.
- Hard requirements, authorization boundaries, scope-specific rules, and exceptions.
- Repeated, ambiguous, outdated, or mechanically enforced guidance.

Verify paths and commands against the repo. Preserve commands unless demonstrably obsolete; report an obsolete or unverifiable command rather than silently dropping it. Do not run deployment, migration, or destructive commands merely to check documentation.

## Rewrite around applicability

Keep foundational context near the top. Group other guidance under concrete headings such as “When changing database schemas” or “When modifying UI components.” Use one trigger for closely related rules; split unrelated rules.

`<important if="...">` blocks from the upstream skill are optional readable markup, not a Codex/Hermes feature, priority override, or guarantee of adherence. Prefer plain Markdown conditions unless the repo already uses the XML style. Neither form can override higher-priority instructions.

Shorten without changing the contract:

- Merge duplicates while retaining their scope and exceptions.
- Replace long, drifting examples with verified source references when they explain the same requirement.
- Remove vague instructions that add no action or decision criterion.
- Remove style rules only when existing tooling actually enforces them or the rule is redundant. Do not assume “a linter could do it” means a linter does.
- Keep non-obvious requirements, safety boundaries, and explicit user preferences, even if they take more space.
- Use supporting files only for substantial conditional detail, with a clear link explaining when to read them.

## Suggested shape

```markdown
# Project instructions

[One-line project identity and essential stack.]

## Project map

[Short paths and responsibilities.]

## Commands

[All applicable commands with working directories and purpose.]

## When changing [specific area]

[Requirements, exceptions, and verified references.]
```

Preserve existing nested-file precedence; moving a local rule into a parent file changes its scope. Edit the canonical source when the runtime copy is generated, using the repo's existing sync mechanism.

## Verify and report

Compare the before/after instruction inventory: commands retained or explicitly accounted for, hard constraints and exceptions preserved, links resolving, scope unchanged, contradictions named. Inspect the diff for accidental policy changes. Report substantive edits and unresolved ambiguities. Do not claim improved model adherence without an actual behavioral evaluation.

Invoke with `$improve-agent-instructions` in Codex or `/improve-agent-instructions` in Hermes.
