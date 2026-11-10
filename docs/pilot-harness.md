# Guarded local agent pilots

`scripts/pilot_harness.py` is the repository-owned execution and state-audit
entrypoint. It replaces the November 2026 task-local runner for new evaluations.
It does not change historical results or establish what changed in databases
whose earlier snapshots were not retained.

Prepare synthetic workspaces and runtime homes outside iCloud and Git. Keep raw
snapshots, logical inventories and logs private: snapshots can contain user data.
The harness creates evidence directories with mode 0700 and files with mode 0600.
Never copy live memories/configuration/databases into an agent's fixture. The
parent may capture specifically authorized live databases as protected audit
evidence; the agent cannot read those snapshots. Tests use synthetic homes only.

## Execution contract

Each run supplies an explicit argv for its runtime path probe and payload. They
must use the same installed executable. The probe emits one JSON object with
absolute `home`, `root`, `config`, `state_db`, and `skills` paths. All must resolve
inside the isolated runtime home; `home` and `root` must equal that home.
For Hermes, use `scripts/pilot_hermes_probe.py` under the selected installed
Hermes Python with the source checkout as its argument. It resolves Hermes's
actual path APIs and opens its actual SessionDB in the synthetic home. It does
not start a gateway, install dependencies or make a model call.

Example spec (replace paths with actual local paths; prepare directories first):

```json
{
  "workspace": "/private/task/work",
  "runtime_home": "/private/task/hermes-home",
  "protected_roots": ["/Users/example/.hermes", "/Users/example/.codex", "/Users/example/.agents"],
  "databases": ["/Users/example/.hermes/profiles/example/state.db"],
  "probe_command": ["/installed/hermes/venv/bin/python", "-I", "/repo/agents/scripts/pilot_hermes_probe.py", "/installed/hermes/source"],
  "command": ["/installed/hermes/venv/bin/python", "-I", "/private/task/work/offline_check.py"],
  "timeout_seconds": 60,
  "allow_provider_https": false
}
```

From the agents repository:

```sh
python3 scripts/pilot_harness.py run --spec /private/task/spec.json --output /private/task/audit
python3 scripts/pilot_harness.py suite --spec /private/task/suite.json --output /private/task/suite-audit
```

A suite spec has `runs` (an array of run specs), `max_runs` (1–40), and
`max_seconds` (at most 24000). Runs are sequential and stop at the first failure
or exhausted time allowance. Every run receives its own before/after snapshots.
Outputs must be fresh; existing evidence is never overwritten or treated as a
new success. The suite guard is the integration point for frozen baseline and
candidate fixtures; semantic scoring stays separate from state preservation.

## Isolation and boundaries

The current execution backend is macOS `sandbox-exec`. Unsupported hosts fail
before payload execution; there is no unsandboxed fallback. The guard:

- Rejects overlap between workspace, runtime home, evidence and protected roots.
- Rejects escaped symlinks and hard-linked fixture files. An explicitly listed
  `read_only_credentials` auth.json reference is the only external credential
  exception; credential refresh writes to the protected root are still denied.
- Drops inherited provider, gateway, profile and Python-path overrides. Native
  HOME stays unchanged; HERMES_HOME and scratch/cache paths are isolated.
- Permits file writes only in the workspace, isolated home and scratch directory.
  It denies writes anywhere in declared protected roots, and reads of declared
  databases and conventional profile/memory/session/configuration paths there.
- Denies network access by default. Explicit `allow_provider_https: true` permits
  outbound TCP 443 and DNS while blocking localhost and Unix gateway sockets.
  This is transport permission, not authorization to call production APIs. It
  does not restrict HTTPS by provider hostname or enforce monetary budgets.
- Runs the actual path probe in the same OS guard before launching the payload,
  then checks fixture links again. A failed/misdirected probe prevents execution.
- Terminates the subprocess group on completion, failure or timeout, and retains
  before/after evidence even when the payload fails or receives SIGTERM.

Use only trusted runtime/probe commands. This is protection against accidental
state access, not a hostile-code VM or a guarantee that every possible IPC channel
is isolated. Read-only installed code/dependencies remain accessible. Declare all
state stores relevant to the claim; unlisted stores are not compared. A preexisting
unrelated daemon can still change protected state independently; such a change
fails the comparison rather than being attributed automatically to the pilot.

The runtime must have its dependencies ready. If a launcher tries to repair an
installation, alter live trust settings, refresh protected credentials, or use a
live gateway, the guard may stop it. Prepare an appropriate isolated runtime;
do not loosen protection to get a passing run. For Codex adapters, do not fabricate
Hermes path-probe output: supply and validate an actual Codex-specific resolver
before claiming that runtime's storage is isolated. The included runtime-specific
probe is for Hermes; the generic guard also supports trusted synthetic commands.

## SQLite evidence and acceptance

The parent uses SQLite's backup API through a read-only source connection. This
captures committed WAL contents in a consistent snapshot; copying or hashing only
`state.db`, or opening a live WAL database with `immutable=1`, would miss data.
Snapshot deadlines are bounded. Source replacement, corruption or missing after
evidence fails the gate. An initially missing database is recorded; later creation
or deletion is a change.

Logical comparison includes schema, application/user version, encoding, every
table, typed values, duplicate rows and accessible implicit rowids. Row order
and physical page layout do not determine equality. Per-table counts of added
and removed row identities locate changes without putting raw values in the
comparison report. Private snapshots retain the actual data for authorized
investigation. Even `runtime_epoch` changes fail: there is no blanket exemption
for bookkeeping. Integrity checks supplement this comparison.

Separate audit commands also support controlled publication:

```sh
python3 scripts/pilot_harness.py snapshot --database /absolute/profile/state.db --output /private/task/before
python3 scripts/pilot_harness.py snapshot --database /absolute/profile/state.db --output /private/task/after
python3 scripts/pilot_harness.py compare --before /private/task/before/manifest.json --after /private/task/after/manifest.json
```

The command exits nonzero for failure or logical drift. `report.json` is the
acceptance signal: only `status: passed` establishes the guarded execution and
declared-state checks. It does not certify the agent's answer or all live state.
Preserve failures and inspect changed tables before deciding on another run.

SIGKILL/power loss may leave `status: incomplete` and `active-process.json`.
Inspect the recorded PID/command identity before stopping any leftover process;
never blindly kill a reused PID. Capture a fresh after-snapshot and compare with
the retained before-manifest for diagnosis. Do not relabel the interrupted run
as passing or restore an older runtime epoch. A retry gets fresh fixture homes
and a fresh output directory.
