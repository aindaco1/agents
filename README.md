# Agents roster

This repository is the canonical authoring source for a roster of specialist agents used by Hermes and mirrored into Codex-compatible skills. The repository currently contains 248 profiles.

## Source of truth

Each profile directory is keyed by its slug and contains:

- `SOUL.md` — runtime persona and operating instructions
- `IDENTITY.md` and `IDENTITY_SUMMARY.md` — full and compact identity references
- `MEMORY.md` and `USER.md` — starter durable-memory and user-context guidance
- `roster_entry.json` — routing, model, invocation, handoff, and display metadata
- optional avatar and reference assets

The root `roster.json` is a generated aggregate catalog; do not edit its agent entries directly. `_MODEL_RECOMMENDATIONS.md` documents the current Hermes model stack and live OpenRouter free-model catalog.

After editing one or more profile entries, regenerate the aggregate and verify that it has no drift:

```bash
python3 scripts/sync_roster_aggregate.py
python3 scripts/sync_roster_aggregate.py --check
```

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

`MEMORY.md`, `USER.md`, and `config.yaml` are seeded only when missing. Recompiling
preserves existing memory and configuration byte-for-byte, including comments and
unknown settings. Private skills, credentials, sessions, and databases are retained.
Generated persona/reference files use a publication baseline: local-only edits survive,
and simultaneous source/local changes require reconciliation. See
[safe profile publication](docs/profile-publication.md) for preview, recovery, and rollback.

## Common commands

The launchers in `~/.local/bin` call `scripts/hermes_agent_roster.py` in this checkout:

```bash
agent-list
agent-compile chief-of-staff --dry-run
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

To preview one changed profile, then apply its exact returned `plan_hash`:

```bash
agent-compile <slug> --dry-run
agent-compile <slug> --apply <plan_hash>
```

For a legacy profile without a baseline, add `--adopt-existing` to both calls and
review the listed changes first. For an isolated staging home, add
`--hermes-home /absolute/path/to/staging-home` to both calls. Never point tests at
the live home. Transactions and manifests live locally under
`~/.hermes/roster-state/<slug>/`; the old `generated/hermes_profiles_manifest.json`
is a historical export, not the publication authority. A batch commits profiles
individually, so check receipts if a later profile fails.

## Codex skill mirrors

`scripts/sync_codex_skills.py` reads the same canonical profile entries as Hermes and mirrors them into `~/.agents/skills` while preserving hand-tuned frontmatter and unrelated third-party skills:

```bash
python3 scripts/sync_codex_skills.py --check
python3 scripts/sync_codex_skills.py --plan
python3 scripts/sync_codex_skills.py --apply <plan_hash>
```

Roster mirrors are persona/routing skills generated from `IDENTITY_SUMMARY.md`, `IDENTITY.md`, and handoff metadata. Optional `codex_interface` metadata in `roster_entry.json` is the source of truth for a profile's Codex display name, short description, and default prompt.

## Portable procedure skills

Reusable procedures that should work unchanged in Codex and Hermes live under `skills/<category>/<name>/`. These are distinct from agent personas: profiles say who should handle a task; procedure skills say how a recurring workflow should be executed and verified.

The canonical skill format uses the frontmatter subset accepted by both runtimes:

- `name` and a trigger-first `description` no longer than 60 characters
- optional `license` and `allowed-tools`
- `metadata` for version, author, and `metadata.hermes` tags/related skills
- optional Codex UI metadata under `agents/openai.yaml`

Validate and synchronize the same source packages into both local libraries:

```bash
python3 scripts/sync_portable_skills.py --check
python3 scripts/sync_portable_skills.py --plan
python3 scripts/sync_portable_skills.py --apply <plan_hash>
```

Codex receives flat packages under `~/.agents/skills/<name>/`. Hermes receives categorized packages under `~/.hermes/skills/<category>/<name>/`. Use `--target codex` or `--target hermes` when only one runtime should be checked or updated.

Add a portable skill name to a profile's `hermes_skills` list when Hermes should prefer that procedure for the profile. Codex discovers the same package directly after synchronization. Do not copy runtime skill edits back blindly: compare them to the canonical package and import only intentional improvements.

### Research paper authoring

`research-paper-authoring` is the shared manuscript procedure for Academic Writer
and Academic Researcher, covering empirical, theoretical, qualitative, humanities,
and review papers. It verifies citations and claim support, records provenance,
reviews figures, and applies the existing `humanizer` in academic mode. The
[source notes](skills/research/research-paper-authoring/references/source-notes.md)
document the IEEE Spectrum investigation, linked research, critiques, and access
limits. The humanizer's academic mode preserves scientific uncertainty, technical
terms, citations, quantities, and AI disclosures.

```bash
python3 scripts/sync_portable_skills.py --skill research-paper-authoring --skill humanizer --plan
python3 scripts/sync_portable_skills.py --skill research-paper-authoring --skill humanizer --apply <plan_hash>
python3 scripts/sync_portable_skills.py --skill research-paper-authoring --skill humanizer --check
```

Invoke with `$research-paper-authoring` in Codex or `/research-paper-authoring`
in Hermes. The distinct name preserves the separately installed, ML-focused
Hermes `research-paper-writing` package. This adds a procedure, so the roster's
persona count is unchanged.

### HumanLayer adaptations

Six procedures from [HumanLayer's skills](https://github.com/humanlayer/skills) are
adapted for both runtimes: `show-me`, `visual-pr`,
`improve-agent-instructions` (upstream `improve-claude-md`),
`narrow-react-prop-types`, `build-iterated-agentic-loop`, and `design-control-loop`.
They live under `skills/software-development/` and use the same portable sync
command. Invoke with `$skill-name` in Codex or `/skill-name` in Hermes.

See [source revision, adaptation notes, and focused sync commands](docs/humanlayer-skills.md).
The automation workflows are reference templates; installing these skills does
not enable schedules, create PRs, or start provider runs.

## Jev semantic evaluation

The shared `jev-evaluation` procedure is an opt-in, advisory evaluator, not a
replacement for the main agent, deterministic tests, or release approval. It
reuses the hash-locked Platform Cloudflare adapter and defaults to a zero-network
preview. No ordinary test or routing command calls Jev.

Read [the audit and measured comparison](docs/jev/README.md) and
[setup/benchmark commands](skills/software-development/jev-evaluation/references/running.md).
Sync only this package with:

```bash
python3 scripts/sync_portable_skills.py --skill jev-evaluation --plan
python3 scripts/sync_portable_skills.py --skill jev-evaluation --apply <plan_hash>
python3 scripts/sync_portable_skills.py --skill jev-evaluation --check
```

This synchronizes the default Hermes and Codex skill libraries. It does not
compile or overwrite other Hermes profiles. Persona-source changes take effect
when their runtime profiles are deliberately reconciled and compiled later.

## Verification

Run the roster tests with:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests
```

Jev's additional offline replay/transport checks require the pinned Platform
checkout described in the setup guide (no Cloudflare credentials or network):

```bash
DUSTWAVE_PLATFORM_DIR="/absolute/path/to/platform" node --test tests/jev.test.mjs
```

Before publishing, also run `python3 scripts/sync_roster_aggregate.py --check`, validate JSON, inspect `git diff --check`, review the complete diff, fetch `origin`, and confirm the branch is still based on current `origin/main`.

## Publication ownership and development workflow

Both publishers default to a read-only JSON preview. Apply the exact `plan_hash`
with the same selection flags. `--check` remains a read-only content comparison.
Existing modified copies require explicit `--adopt-existing` during their initial
baseline; later conflicting local/source edits stop publication. Each package has
private local transaction backups; no unrelated destination files are deleted.

`skills/ownership.json` declares maintained and retired canonical procedures.
Maintained procedures are published to both runtimes and pinned/locked in Hermes
using its existing usage-sidecar lock protocol. Retired procedures are not
recreated; existing copies and archives are retained for explicit disposition.
A lock controls Hermes tools; it is not a separate operating-system identity.

`development-task` and `review-development-lessons` are the common development
and review procedures. See [the task/review contract](docs/development-workflow.md).
Full-roster routing is now the default; `--first-50` selects the legacy subset.

For a bounded skills-isolation pilot, use
`scripts/isolate_hermes_skills.py <slug>` to preview and repeat with
`--apply <plan_hash>`. The tool only migrates the known global skills symlink.
It publishes a content-addressed local shared snapshot and switches the profile
to its own writable `skills.local` directory, preserving all original shared
content. Only `skills.external_dirs` changes in config. The `.no-bundled-skills`
marker prevents ordinary bundled reseeding; Hermes may retain essential built-ins.
Use `--restore` for interrupted migration or rollback; newer settings cause a
conflict and private learned skills remain recoverable. Publish only to idle
profiles. Unselected profiles retain their existing library wiring.

Shared snapshots are pinned until explicitly refreshed. To refresh a pilot,
review/restore its previous migration and reconcile retained `skills.local` first;
the tool refuses to discard a populated private library. Do not bypass that check.
