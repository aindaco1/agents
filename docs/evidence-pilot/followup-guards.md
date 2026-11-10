# Persona naming and pilot state guards

Implemented and published November 9, 2026 local time. This follows the
[two-profile pilot](README.md) and its database-preservation qualification.

Later follow-up: [Marisol simplification and rename](marisol-rename.md) replaces
the initial Codex persona export below with `web-application-builder-marisol`.
The original publication results here remain a historical record.

## Changes

- Codex now installs Marisol as `web-application-builder-persona`. The existing
  `web-application-builder` procedure keeps its name and bytes. Canonical/Hermes
  role IDs remain unchanged. UI invocation and generated handoffs use the Codex
  export name; procedure references still point to the procedure.
- The publisher validates export names, detects duplicates and procedure-name
  conflicts, and rejects renaming an already-published export without a separate
  migration. Existing persona trigger descriptions and transaction recovery are
  retained.
- `scripts/pilot_harness.py` is the canonical guarded runner and suite runner.
  It captures consistent SQLite before/after backups including committed WAL,
  compares logical schema and data, and fails on unexplained changes, missing
  evidence, process failure, timeout or a failed isolation probe.
- The macOS guard restricts writes, blocks live private-state and audit-snapshot
  reads, removes inherited gateway/provider overrides, checks path escapes, and
  blocks local gateway connections. `pilot_hermes_probe.py` exercises the installed
  Hermes resolver and state-store API in an isolated home. See the
  [harness contract](../pilot-harness.md) for scope, setup and recovery.
- `development-task` v1.1.1 carries the pilot state-evidence rule in Codex, global
  Hermes and the generalist's local overlay. Hermes's web-builder roster metadata
  was also synchronized. No model default, learned memory or release authority
  changed.

## Verification

**143 tests passed**, including 27 alias/guard tests. The alias round-trip checks
separate creation, unchanged original procedure, correct invocation, stale
previews, invalid/duplicate names and rollback. A before/after publisher fixture
reproduces the original skip and verifies creation under the new name.

The WAL regression test commits changed data while the main database file stays
byte-identical. The new snapshot comparison detects the change. Other fixtures
cover schema/version/type changes, concurrent writers, corruption, missing or
tampered snapshots, locked-database deadlines, escaped symlinks/hard links,
misdirected probes, unavailable OS isolation, private snapshot reads, denied
database access, local socket access, process timeouts, child-process cleanup,
missing after-evidence, and suite stop-on-failure. A concurrent synthetic
`runtime_epoch` change fails preservation even when the payload exits successfully.

The installed Hermes state-store canary created and read a synthetic session in
its isolated home, with networking disabled. Real path discovery resolved home,
root, configuration, skills and database paths there. Before/after snapshots of
the generalist, reviewer and web-builder live profile databases were logically
unchanged. Snapshots were private audit evidence, not agent inputs.

Publication used fresh exact-hash previews. Separate SQLite snapshots around
publication and runtime discovery also show those three databases unchanged.
All **18 protected files** retained their recorded hashes, including configuration,
learned memories and both copies of the web-builder procedure. The entire Codex
procedure package also matches its task-start inventory.

Fresh Codex discovery finds both web-builder names. Actual Hermes catalogs for
all three profiles resolve the current procedures. Final checks report **248
persona mirrors, zero skipped collisions, and 19 portable procedures current in
both runtimes**. Aggregate, whitespace and local-link checks pass.

## Evidence and limits

Private run evidence is retained under
[/Users/aindaco1/.local/share/agents-evidence/2026-11-09-persona-and-pilot-guards](/Users/aindaco1/.local/share/agents-evidence/2026-11-09-persona-and-pilot-guards).
It includes test output, the installed canary, private SQLite snapshot pairs and
logical inventories, publication plans/receipts, discovery results, protected
file inventories, source identity and a rollback index. Runtime locks/backups
remain outside iCloud. At runtime-publication verification, repository authoring
changes were uncommitted; the recorded file hashes identify those tested inputs.

The execution guard currently requires macOS. The included actual runtime probe
is Hermes-specific; other adapters must validate their real storage paths before
claiming isolation. The guard protects declared state and conventional private
paths, not every possible IPC channel or every unlisted database. It is not a
hostile-code VM or a billing limiter.

These checks establish naming/publication behavior and state preservation for
the exercised operations. They do not rerun or extend the earlier model-quality
evaluation. The earlier missing database snapshots remain a historical audit
gap; this work prevents accepting that same gap in future guarded runs.
