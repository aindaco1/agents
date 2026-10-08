---
name: visual-pr
description: Use when writing a visual pull request description.
license: MIT
metadata:
  version: 1.0.0
  author: HumanLayer; adapted for Codex and Hermes
  upstream: https://github.com/humanlayer/skills/tree/ca7c8088db69e315a8b2deea43820270457f8f3c/plugins/visual-pr/skills/visual-pr
  upstream_commit: ca7c8088db69e315a8b2deea43820270457f8f3c
  hermes:
    tags:
    - git
    - pull-requests
    - documentation
    related_skills:
    - show-me
---

# Visual PR

Explain a pull request with a concise account of the problem and a structural view of the change. Load [the description template](references/pr-description-template.md). A repository PR template takes precedence; fit the visual outline into it.

1. Establish the requested action: draft, update an existing PR, or create a PR. Skill discovery alone does not authorize a commit, push, or publication. Honor authorization already given in the conversation; do not ask again for the same action.
2. Identify the PR with the available GitHub integration or `gh pr view --json url,number,title,state,baseRefName,headRefName`. If absent, inspect the current branch, status, commits, and remote default branch. For draft-only work, use the branch diff. Create a PR only when requested, following the repo's commit/push conventions and including only task-related changes.
3. Read the complete relevant diff and enough surrounding source to explain behavior. Use verified ticket links and test results. Do not invent a task URL, cloud permalink, or successful check.
4. Write one sentence for **Why the change**, 1–3 reviewer-relevant notes (or `None`), and the smallest useful **Change outline**. Use a focused `diff`, shallow file tree, component tree, call tree, pseudocode, data shape, or Mermaid diagram. See [visual conventions](references/visual-outline.md); skip views that add no information. Include actual validation and its limits.
5. Save a reviewable Markdown draft in the task's existing artifact directory or designated output location. Reuse `.humanlayer/tasks/...` only if this repo already uses it; do not introduce a HumanLayer service dependency.
6. If publication is authorized, use a structured GitHub tool or `gh pr edit NUMBER --body-file PATH` / `gh pr create --body-file PATH`. Pass the literal body through a file, not shell interpolation. Read the PR back and confirm the body and URL.

Return the draft path or verified PR link, a short account of the change, and whether publication occurred. Keep local preparation and remote publication distinct. Codex invocation: `$visual-pr`. Hermes invocation: `/visual-pr` or the available skill loader.
