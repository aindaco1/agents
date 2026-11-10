# Safe profile publication

The compiler owns generated personas, identity references, routing metadata,
context, and assets. It seeds memories and configuration once and never resets
existing values. Existing skill directories and shared-library links survive;
skill isolation is a separate migration. Codex's memories and configuration are
outside this compiler's scope.

New profiles link to an installed shared skill library, preserving discovery
until the explicit isolation migration. If no library exists yet, compilation
creates an empty private directory and leaves installing skills to runtime setup.

From the repository root:

```sh
python3 scripts/hermes_agent_roster.py compile ai-workflow-designer --dry-run
python3 scripts/hermes_agent_roster.py compile ai-workflow-designer --apply PLAN_HASH
```

The first command is read-only. Replace `PLAN_HASH` with its returned hash. The
hash binds source bytes, compiler implementation, destination state, and previous
manifest. Any drift requires a new preview. Initial adoption of different legacy
generated files requires `--adopt-existing` on both calls. This flag does not
override established three-way conflicts, reset memories, or replace config.

Configuration is generated from the base configuration and roster model map only
for a new profile. Existing profile files remain byte-identical. `agent-run`
retains its existing model-map/alias resolution and explicit provider/model CLI
arguments; these launcher choices can override stored model settings. Use its
`--dry-run` output to inspect actual selection. Compilation does not change model
aliases or runtime choices.

Each profile has a local manifest and private transaction backups under
`HERMES_HOME/roster-state/<slug>/`. No credentials or learned memories enter the
repository manifest. Source commit and per-file hashes identify uncommitted
source edits as well. Source files removed later are retained in the runtime;
removal requires a separate reviewed migration.

Writers use an exclusive local file lock. Each file replacement is atomic and
fsynced; the whole directory is **not** an atomic snapshot for independent
readers. Publish only when the target profile has no active turn. On an ordinary
write failure, generated files are restored. A process kill leaves a journal;
the launcher refuses to start that profile until recovery. Direct Hermes launches
do not consult this journal, so do not bypass recovery with a direct launch.

```sh
python3 scripts/hermes_agent_roster.py recover ai-workflow-designer
python3 scripts/hermes_agent_roster.py recover ai-workflow-designer --transaction TRANSACTION_ID
```

The first form recovers an interrupted publication. The second rolls back only
the current completed transaction. Recovery refuses to overwrite newer generated
file edits. It preserves all seed files, including facts learned after a compile.
Transactions remain available for inspection; no automatic backup deletion runs.

Use `--hermes-home /absolute/staging/home` on compile/recover when testing. The
staging home needs a synthetic `config.yaml` and `model-map.json`. Tests cover
repeated compilation, local/source conflict, stale previews, symlink refusal,
write failure, process death, competing publishers, and rollback after learning:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests
```

Local locks do not coordinate writers on different Macs. Keep runtime state and
publication locks outside iCloud; synchronize reviewed authoring through Git.

## Codex persona export names

`codex_skill_name` in the canonical roster entry controls the Codex directory,
frontmatter name, default invocation and generated handoff name. The canonical
`role_id` and Hermes profile name remain stable. Procedure references in
`hermes_skills` continue to name procedures, not persona exports.

The `web-application-builder` persona exports as `web-application-builder-marisol`.
Its original name belongs to the maintained implementation procedure. Publish
through the usual Codex preview/apply protocol; do not replace that procedure
with `--replace-collision`. Both packages must be discoverable after publication.
The persona's transaction state remains keyed by canonical role ID.

Alias validation rejects traversal, invalid/duplicate export names and aliases
that collide with canonical procedure names. Existing tuned descriptions are
preserved, but the frontmatter name and default prompt must identify the actual
export. Renaming an already-published persona requires a separately reviewed
migration; this publisher refuses to move an existing transaction to a new root.

The November 2026 Marisol rename uses the existing recovery workflow.
The old `web-application-builder-persona`
export was still its initial creation transaction: no previous manifest, two
created managed files, and no later edits. After testing that exact shape in
temporary homes, retain the old package/source and transaction, retire the old
managed files with `managed_publication.recover(old_root, state, transaction)`,
then preview and apply the new export through the normal publisher. The state
directory stays keyed by `web-application-builder`.

Recovery checks the current transaction and file hashes under the writer lock;
it refuses later edits or another writer and leaves unrelated files untouched.
The new publication still needs a fresh exact-hash preview. If it fails, recover
any pending new publication and republish the retained old source through a new
preview/apply. Do not reuse this initial-creation recipe for an export with a
longer publication history. Do not delete populated directories or edit state
manifests by hand. Preserve both transaction histories and verify that runtime
discovery finds only the new persona name plus the separate procedure.

See [Marisol simplification and rename](evidence-pilot/marisol-rename.md) for the
source boundaries, migration checks, and publication evidence.

For stateful canaries, use the SQLite capture/compare commands in the
[pilot harness contract](pilot-harness.md). A fingerprint or integrity check alone
does not establish logical data preservation. Retain private snapshots and stop
on unexplained logical changes; do not automatically restore runtime databases.
