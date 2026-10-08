---
name: build-iterated-agentic-loop
description: Use when building a recurring coding agent workflow.
license: MIT
metadata:
  version: 1.0.0
  author: HumanLayer; adapted for Codex and Hermes
  upstream: https://github.com/humanlayer/skills/tree/ca7c8088db69e315a8b2deea43820270457f8f3c/plugins/build-iterated-agentic-loop/skills/build-iterated-agentic-loop
  upstream_commit: ca7c8088db69e315a8b2deea43820270457f8f3c
  hermes:
    tags:
    - automation
    - ci
    - codex
    - hermes
    related_skills:
    - design-control-loop
    - narrow-react-prop-types
---

# Build Iterated Agentic Loop

Turn a repeatable coding task into a repository-local skill and a bounded Codex or Hermes workflow. Each run selects a reviewable unit, validates it, and proposes a PR. The workflow carries standing feedback between runs and can support maintainer-requested iteration on the same PR.

## Inspect and choose

Read the repository's instructions, CI workflows, package manifests/locks, test commands, existing skills, and automation conventions. Identify its default branch and install/validation commands. Reuse those seams.

Infer choices already settled in the request. Ask only about material gaps: task and writable scope, Codex or Hermes, cadence, reviewable batch size, required validation, and whether `/iterate` feedback is wanted. Start with manual dispatch and one open PR per loop unless the user requested something else. A manual invocation does not bypass the PR bound by default; expose an explicit override if wanted.

State the job in one sentence: what is found, what changes, and how success is verified. If the property or measurement is still unclear, use the installed `design-control-loop` skill first.

## Create the portable task package

Default to `.agents/skills/<skill-name>/SKILL.md`, shared by Codex and supported Hermes installations. Follow a different existing path convention when required, and explicitly load the file if the runtime does not discover it. Hermes project-skill discovery may require `hermes skills trust`; never assume writing a repo-local package makes it load automatically. Global installation is a separate choice.

Use [skill-template.md](references/skill-template.md). Match frontmatter name to directory, keep the trigger concise, and put long conditional material in references. Capture selection evidence, golden examples from this repo, transformation boundaries, validation, and a legitimate no-change result. Do not duplicate the same rules across skill, prompt, and memory.

Create:

- The repo-local task skill and a task-specific [response template](references/response-template.md).
- A prompt based on [prompt-template.md](references/prompt-template.md), naming the skill's exact path, scope, batch, and validation command/script.
- `.github/agent-memory/<task-slug>.md` from [memory-template.md](references/memory-template.md), containing useful standing feedback rather than transcripts. This file is repository configuration, not permission to change personal agent memories.
- A repository validation script that checks both correctness and writable scope, including staged and untracked changes. It must fail on out-of-scope changes and must not weaken the checks used to judge success.

## Wire the runtime and CI

Read [agent-runner-templates.md](references/agent-runner-templates.md), then adapt [workflow-template.yml](references/workflow-template.yml) to the selected runtime and repository. The template is a starting point, not an installed workflow. Replace every `REPLACE_*` value and every setup stub. Preserve existing CI pinning conventions and verify the selected CLI's help before choosing flags.

The agent edits and writes a final report; the workflow owns validation, staging, commits, push, and PR creation. This prevents multiple competing publication paths. Keep GitHub write credentials out of the agent environment and checkout, scoped to publication steps. Use an ephemeral runner with the permissions and provider credentials the user authorized. Never assume a headless agent is sandboxed simply because it runs in CI.

Required workflow behavior:

- A timeout and serialized runs per loop, without cancelling an active run halfway through publication.
- Label-based open-PR bounding before expensive work, with no PR for an unchanged tree (including untracked files in the check).
- Repository-specific dependency setup, a pinned runtime, and the requested provider/model configuration.
- Literal prompt files and environment variables for event inputs; no direct comment text in shell source and no `eval`.
- A nonempty final-response file separate from diagnostics. An agent crash or validation failure stops publication; raw tool logs are not a fallback PR body.
- A configured scope gate and normal required checks after editing, followed by a task-only commit and a PR against the verified base branch. Never auto-merge.

For `/iterate`, read [iteration.md](references/iteration.md) and install its [helper](references/agent-iteration.py). Keep the `issue_comment` trigger disabled if not requested. Check current maintainer write permission, exact command, matching workflow marker and label, open PR, bot ownership, expected branch prefix/base, and same-repository head before checkout. The marker routes events; it is not authentication. Reuse the existing branch, keep standing feedback concise, and update that PR. Do not run fork PR code with secrets.

## Validate before activation

Run the task and validation locally in an isolated checkout when authorized. Parse the rendered YAML, run an available Actions linter, validate shell/helper syntax, resolve referenced paths, and check both runtimes' final-response handling as applicable. Exercise no-change, failed validation, open-PR-bound, and iteration cases without posting or dispatching.

Preparing files does not itself authorize a push, workflow dispatch, provider spend, or recurring schedule. Continue through any of these already authorized by the user. Otherwise finish the concrete local implementation and identify the remaining activation step.

`workflow_dispatch` requires the workflow to exist on the default branch; it does not require a prior successful run. Do not add a temporary push trigger to work around that requirement. Follow the repo's normal review/merge path, then dispatch only within the user's authorization.

Report created paths, local checks, configured runtime, cadence, and PR bound. Distinguish prepared, published, executed, and reviewed; a YAML parse is not a successful live workflow run.
