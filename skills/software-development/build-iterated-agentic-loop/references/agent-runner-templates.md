# Codex and Hermes runners

Verify `codex exec --help` and `hermes --help` for the installed/pinned release before generating a workflow. These commands were checked against Codex CLI 0.160.0 and Hermes v0.21.5 on 2026-10-08. Choose the user's runtime, provider and model; do not impose a model from this example.

## Shared contract

The workflow writes a literal prompt to `"$RUNNER_TEMP/agent-prompt.md"`. It names the exact repo-local skill path and tells the agent to read it plus the referenced response format. The agent edits the checkout and produces a final response; the workflow validates and publishes. An empty final response, nonzero exit, or failed validation is a failed run, not a PR.

Use a clean ephemeral runner. Configure provider credentials only for the agent step. Do not pass `GH_TOKEN` to it, persist checkout credentials, or reuse a personal Hermes/Codex configuration directory. Explicitly allow only the toolsets needed for the task. The prompt is not a filesystem sandbox; use the runtime's supported sandbox or an external container boundary as appropriate.

## Codex

Install a verified pinned `@openai/codex` version. Login once in the isolated runner:

```bash
printenv OPENAI_API_KEY | codex login --with-api-key
```

Run from the checkout, preserving the prompt literally through stdin:

```bash
codex exec --cd "$GITHUB_WORKSPACE" --sandbox workspace-write \
  --output-last-message "$RUNNER_TEMP/pr-body.md" - \
  < "$RUNNER_TEMP/agent-prompt.md" \
  > "$RUNNER_TEMP/agent-output.log" 2>&1
```

`--output-last-message` writes the final answer directly; do not parse arbitrary JSONL or put diagnostics in the PR. Select a model only if specified by the task/configuration. Adjust network/test needs using the pinned runtime's supported configuration, not a blanket bypass flag.

## Hermes

Install a verified pinned source revision using the official package entrypoint, e.g. a dedicated Python virtualenv with `pip install 'git+https://github.com/NousResearch/hermes-agent.git@VERIFIED_COMMIT'`. Respect the selected revision's supported Python versions and repo installation conventions. Do not copy a developer's personal profile to CI.

Hermes's top-level one-shot mode prints only the final answer on stdout:

```bash
hermes --toolsets terminal,file --provider "$HERMES_PROVIDER" \
  --model "$HERMES_MODEL" -z "$(cat "$RUNNER_TEMP/agent-prompt.md")" \
  > "$RUNNER_TEMP/pr-body.md" 2> "$RUNNER_TEMP/agent-output.log"
```

The quoted command substitution passes text as one argument; it does not evaluate shell snippets inside the prompt. Provider and model must match credentials supplied to that step (for example, `OPENROUTER_API_KEY` for an explicitly chosen OpenRouter model). Use a fresh `HERMES_HOME` in the runner's temporary directory and a wall-clock timeout in CI.

**One-shot mode auto-bypasses approval prompts in the verified version.** It is suitable only inside the deliberately authorized isolated runner boundary. For interactive local work keep normal Hermes approvals. If the installed version lacks a clean final-output mode, use its documented structured output and a tested extractor; do not treat `chat -Q` session metadata or raw tool logs as the final report.

A task can read `.agents/skills/<name>/SKILL.md` by explicit path without registering it. To use Hermes's skill index instead, check project-skill support and trust requirements; never silently alter a user's global trust config.

## Before calling it tested

Check success, empty output, nonzero exit, and timeout handling with a fixture/mock runner before a live call. Confirm the selected engine reads the exact task skill and that actual validation can run in its environment. Live provider use and GitHub dispatch are separate from offline template validation.
