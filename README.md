# Agents roster

This repository is the canonical authoring source for a roster of specialist agents used by Hermes and mirrored into Codex-compatible skills. The repository currently contains 247 profiles.

## Source of truth

Each profile directory is keyed by its slug and contains:

- `SOUL.md` — runtime persona and operating instructions
- `IDENTITY.md` and `IDENTITY_SUMMARY.md` — full and compact identity references
- `MEMORY.md` and `USER.md` — starter durable-memory and user-context guidance
- `roster_entry.json` — routing, model, invocation, handoff, and display metadata
- optional avatar and reference assets

The root `roster.json` is the aggregate catalog. `_MODEL_RECOMMENDATIONS.md` documents the current Hermes model stack and live OpenRouter free-model catalog.

Hermes materializes these sources under `~/.hermes/profiles/<slug>/`. Those directories also contain runtime-only state such as `config.yaml`, sessions, databases, logs, and generated context. Do not commit runtime-only state to this repository.

## Repository to Hermes mapping

| Repository | Hermes profile |
|---|---|
| `SOUL.md` | `SOUL.md` |
| `MEMORY.md` | `memories/MEMORY.md` |
| `USER.md` | `memories/USER.md` |
| `IDENTITY.md` | `references/IDENTITY.md` |
| `IDENTITY_SUMMARY.md` | `references/IDENTITY_SUMMARY.md` |
| `roster_entry.json` | `roster_entry.json` |
| `*.webp`, `*.txt` | `assets/` |

If a profile was edited directly in Hermes, compare these mapped files before compiling. Import intentional authoring or memory changes into this repository first; compiling overwrites the mapped runtime copies.

## Common commands

The launchers in `~/.local/bin` call `scripts/hermes_agent_roster.py` in this checkout:

```bash
agent-list
agent-compile chief-of-staff
agent-route --all --top 5 "Plan and delegate this release"
agent-run chief-of-staff --dry-run
agent-run chief-of-staff --alias-override codex --dry-run
```

`agent-run --dry-run` shows the resolved tier, alias, provider, model, fallbacks, and Hermes command without launching a session. Resolution uses `~/.hermes/model-map.json`, whose aliases must match `model_aliases` in `~/.hermes/config.yaml`.

To refresh roster model recommendations after Hermes aliases or OpenRouter's free catalog change:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/hermes-roster-model-sync/scripts/sync.py \
  --agents-dir "/Users/aindaco1/Library/Mobile Documents/com~apple~CloudDocs/agents" \
  --dry-run
```

Review the dry run, then repeat without `--dry-run`. Preserve role-specific notes and annotations when reviewing the resulting diff.

To compile one changed profile into Hermes:

```bash
agent-compile <slug>
```

For a complete roster refresh, pass the slugs returned by `agent-list`. A complete compile updates `generated/hermes_profiles_manifest.json`.

## Codex skill mirrors

`scripts/sync_codex_skills.py` mirrors the roster into `~/.agents/skills` while preserving hand-tuned frontmatter and unrelated third-party skills:

```bash
python3 scripts/sync_codex_skills.py --check
python3 scripts/sync_codex_skills.py
```

## Verification

Run the roster tests with:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_hermes_agent_roster.py
```

Before publishing, also validate JSON, inspect `git diff --check`, review the complete diff, fetch `origin`, and confirm the branch is still based on current `origin/main`.
