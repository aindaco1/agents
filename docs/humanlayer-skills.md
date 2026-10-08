# HumanLayer skills for Codex and Hermes

Canonical source: `skills/software-development/<name>/`. These are procedure
skills, not new roster personas. Each package carries its own upstream MIT
license, source URL and revision in frontmatter, Hermes discovery metadata, and
Codex UI metadata.

Upstream: [humanlayer/skills](https://github.com/humanlayer/skills/tree/ca7c8088db69e315a8b2deea43820270457f8f3c),
commit `ca7c8088db69e315a8b2deea43820270457f8f3c` (2026-09-17), reviewed 2026-10-08.
All six skill entrypoints at that revision are covered.

| Upstream | Portable name | Adaptation |
|---|---|---|
| show-me | show-me | Native artifact/browser rendering; headless fallback; retained concise visual examples |
| visual-pr | visual-pr | Draft/create/update scope; repo PR templates; actual validation; no cloud-hook or HumanLayer task-path dependency |
| improve-claude-md | improve-agent-instructions | AGENTS.md and explicitly selected Hermes instructions; preserve commands, scope and hard rules; conditional Markdown instead of claims about XML priority |
| narrow-react-prop-types | narrow-react-prop-types | Production evidence plus public API compatibility; repository-derived validation; no hardcoded Bun or CodeLayer workflow |
| build-iterated-agentic-loop | build-iterated-agentic-loop | Codex/Hermes runners, portable task paths, bounded manual/scheduled PRs, optional maintainer iteration |
| design-control-loop | design-control-loop | Local sensor/controller/actuator evidence; reuses the companion loop builder instead of duplicating its CI machinery |

## Runtime and invocation

The shared frontmatter follows this repository's contract (trigger-first
description up to 60 characters; Hermes details nested in `metadata.hermes`).
Codex UI strings live in `agents/openai.yaml`. The adapters remain normally
discoverable; upstream Claude-only `disable-model-invocation` is not copied.
Selecting a skill does not by itself authorize external publication or recurring
automation.

Use `$show-me` in Codex, `/show-me` in Hermes, or ask either agent to use a skill
by name. Hermes can also load its references through `skill_view` when that tool
is available. Read references relative to the loaded skill directory, not the
process working directory. The installed runtime catalog may require a new
session to refresh.

Sync just these packages without refreshing unrelated procedures or personas:

```bash
python3 scripts/sync_portable_skills.py \
  --skill show-me \
  --skill visual-pr \
  --skill improve-agent-instructions \
  --skill narrow-react-prop-types \
  --skill build-iterated-agentic-loop \
  --skill design-control-loop
```

Repeat with `--check` to verify both mirrors. Codex receives flat packages under
`~/.agents/skills/`; the default Hermes library receives them under
`~/.hermes/skills/software-development/`. Isolated Hermes profiles may have their
own libraries; this command does not compile or overwrite those profiles.

## Automation-specific changes

The loop builder contains authoring templates, not enabled workflows. Render
all `REPLACE_*` values and setup stubs for a specific target repository before
use. Select one runtime and remove unused installation steps and secrets.
The optional iteration helper is Python plus `gh`, replacing the upstream
Bun-only helper. It gates on current maintainer permission and PR provenance,
preserves literal feedback, and paginates review context. Its offline behavioral
tests live in `tests/test_agent_iteration.py`.

The workflow owns validation and publication; the agent owns the working-tree
edits and final report. Both manual and scheduled runs obey the one-open-PR bound
unless an operator explicitly overrides it. Validation must include all changed
and untracked paths and reject changes outside the configured scope. No raw agent
logs are published as a PR body. CI credentials and live execution remain part
of configuring a real loop, not installing a skill.

Verified local CLI help: Codex 0.160.0 and Hermes v0.21.5 on 2026-10-08. Recheck
the selected pinned release when generating a workflow. Hermes one-shot mode
prints only the final answer but auto-bypasses approval prompts; use it only
inside an intentionally isolated, authorized runner. Project-local Hermes skill
discovery can require explicit project trust, so prompts can instead read the
exact task skill path.

The upstream suggestion to bootstrap manual dispatch with a temporary push
trigger was removed. GitHub requires a `workflow_dispatch` workflow to exist on
the default branch, not to have completed an earlier run. See
[GitHub's manual workflow documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).
Hermes format and discovery are described in its
[skills documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/).

When refreshing upstream, review semantic changes and preserve these runtime
adaptations; do not overwrite the packages with an unmodified upstream install.
