# Safe profile publication

The compiler owns generated personas, identity references, routing metadata,
context, and assets. It seeds memories and configuration once and never resets
existing values. Existing skill directories and shared-library links survive;
skill isolation is a separate migration. Codex's memories and configuration are
outside this compiler's scope.

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
