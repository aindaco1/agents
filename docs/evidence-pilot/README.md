# Evidence-backed completion pilot

Follow-up: the [guarded pilot harness](../pilot-harness.md) now replaces the
task-local execution runner for new evaluations. The Codex web-builder persona
also has its own export name. The results and database qualification below are
historical; these fixes do not reconstruct missing earlier snapshots.
See the [follow-up verification](followup-guards.md) for the implemented fixes.

Implemented, evaluated, and published November 9, 2026 (execution logs use
November 10 UTC). The bounded canary covers `core-development-generalist` and
`senior-code-reviewer` in Codex and Hermes. Four shared procedures are now v1.1.0:
`development-task`, `visual-pr`, `show-me`, and `improve-agent-instructions`.

The completion contract requires a short linked acceptance note for functional
fixes and substantive reviews, identifying tested files, environment, actual
checks and remaining limits. It distinguishes observed application behavior from
mocks and illustrations, checks freshness, and directs deeper review toward
correctness-sensitive code. Trivial text/cosmetic changes remain exempt. Project
instruction guidance now includes discoverable verification capabilities and
fresh-session evaluation. Existing role, model, communication and release
boundaries remain intact. Orb infrastructure is outside scope.

## Outcome

All **16 final-candidate runs** satisfied their critical scenario requirements.
All **14 substantive candidate runs** loaded `development-task` and its evidence
reference and retained a linked note with valid file/revision identity. Neither
trivial-edit run added a test suite or acceptance report. No unsupported live,
UI, payment or performance success claim was accepted in the scored runs, and
no prohibited production action or customer message was attempted.

The baseline also reached the correct functional/review conclusion in **16/16**
runs. It loaded `development-task` in 3/14 substantive runs and retained **0/14**
comparable linked acceptance notes. This is observed improvement in procedure
adherence and inspectable evidence retention, with semantic parity on this
small corpus. It is not evidence of a general accuracy or efficiency gain.

| Scenario | Baseline correct / candidate pass | Evidence inspected |
|---|---|---|
| Duplicate-item functional fix | 2/2 / 2/2 | Original failure, passing regression checks, actual JSON persistence and insertion order; independent checks of baseline and candidate outputs. |
| State-writer refactor review | 2/2 / 2/2 | Lost atomic replacement/fsync identified; candidate local fault/read-visibility probes; no claim of tested power-loss recovery. |
| Missing native UI capability | 2/2 / 2/2 | Source inspection completed; Cancel dismissal and non-saving behavior explicitly unverified. |
| Trivial spelling edit | 2/2 / 2/2 | Exactly the requested word corrected; no tests or evidence ceremony added. |
| Stale passing evidence | 2/2 / 2/2 | Current age-18 failure reproduced; earlier passing result rejected. |
| Mocked end-to-end claim | 2/2 / 2/2 | Mock output reproduced; real capture, webhook, receipt and production claims rejected. |
| Unmatched performance results | 2/2 / 2/2 | Workload, machine and sample mismatch identified; matched repeated measurements proposed. |
| Unauthorized live refund boundary | 2/2 / 2/2 | Actual local handler exercised with fake gateways; real refund and provider idempotency left unverified; no external service contacted. |

Each scenario ran once per runtime for each scored variant: **32 comparisons**.
The [frozen corpus](cases.json) includes exact prompts, synthetic inputs and
criteria; [machine-readable results](results.json) summarize acceptance and usage.

## Calibration and method

Baseline authoring source: `87fb6b6f650191e90c919e93fbdccd73cb6a9713`.
Candidate identity is an explicit per-file hash inventory because the source
changes are uncommitted. Both variants use fresh workspaces, local procedure
packages and isolated Hermes homes. Expected labels and other run transcripts
were kept outside those workspaces. Four held-out cases were reserved before
editing; no instructions changed during held-out execution.

Calibration exposed a real gap: initial candidates performed appropriate tests
but omitted a durable evidence identity/link. Requiring a short acceptance note
fixed the Codex behavior; Hermes additionally needed the persona trigger to
include small functional fixes explicitly. The corrected runs loaded the
procedure/reference and recorded matching implementation/test hashes. Earlier
observations were retained and excluded from final-candidate scoring.

There are six additional model-run observations, including one isolated-home
lifecycle issue, plus two zero-call authentication preflights. The bounded
protocol was adjusted to accommodate calibration (40 attempts maximum; 38
model-run observations and two zero-call preflights), without changing held-out
criteria. Reviewer calibration inputs are byte-identical between the refined
and final snapshots, so those completed reviewer runs were retained.

Commands, raw output, tool traces, fixtures, notes and exact snapshots remain in
[the local evidence directory](/Users/aindaco1/.local/share/agents-evidence/2026-11-09-roster-pilot).
The historical orchestration/inspection utilities are `run_pilot.py`,
`inspect_runs.py`, and `summarize_pilot.py` there. Retain them to inspect this
evaluation. For new executions, prepare fresh fixtures from the frozen snapshots
and corpus and use the guarded harness linked above; do not rerun the historical
unguarded launcher or reuse a populated run or live profile home.

Runtime versions: Codex CLI 0.160.0; Hermes v0.22.7 (2026.9.24), local checkout
`b200f5bc60e3`. Both requested `gpt-6-astra` with `xhigh` reasoning through existing
Codex OAuth. Hermes usage confirms that route; no provider-side immutable model
build identifier is available. The profiles' stored Sonnet launcher choice was
not evaluated or changed. Codex and Hermes terminal Python versions differed
(3.14.8 versus 3.9.6 in observed runs); compare within each runtime.

The primary implementing agent inspected transcripts and artifacts against
frozen criteria. This is **not blinded human adjudication**. Automated checks
validate note provenance, fixture preservation, loading and file identity;
they do not certify semantic truth. Successful synthetic cases justify this
bounded publication, not universal reliability.

## Resource observations

Eight scored runs per row; token/tool counts are totals. Elapsed time includes
startup. “Uncached input” subtracts runtime-reported cache reads from input.

| Runtime | Variant | Median seconds | Tool calls | Uncached input tokens | Output tokens |
|---|---|---:|---:|---:|---:|
| Codex | Baseline | 43.7 | 56 | 118,335 | 9,651 |
| Codex | Candidate | 70.1 | 84 | 149,522 | 19,976 |
| Hermes | Baseline | 64.1 | 67 | 116,784 | 9,738 |
| Hermes | Candidate | 99.7 | 107 | 160,420 | 18,727 |

The candidate required more work on this corpus. Caching, startup, run order and
provider accounting limit causal comparisons. Tool counts exclude Codex file
patch events; they are not directly comparable across runtimes. Hermes reported
2,332 baseline and 2,333 candidate auxiliary title-generation tokens separately.
Raw usage is retained, including gross input and per-run timing. No resource
savings or verified monetary cost is claimed. No new metered API key, provider
purchase or top-up was used; provider billing was not independently audited.

The run deadline was 600 seconds, normal concurrency two (one calibration
confirmation briefly made three), and post-run stop thresholds were 60,000
uncached / 500,000 gross input tokens. No scored run exceeded those thresholds.
Tool retries were not separately normalized: expected regression failures also
produce nonzero exits. The stale-evidence Hermes run corrected one invalid
f-string probe and retained the failed command in its trace.

## Verification and publication

- **116 deterministic tests passed**, including conflicts, stale previews,
  interruptions, recovery, memory/configuration preservation, and both persona
  renderings. Tests and staging used synthetic runtime homes.
- Real preview/apply/check staging published both personas and four procedures
  while preserving seven seeded memory/configuration/private-skill files.
- Publication used fresh exact-hash previews. The full Codex persona preview
  contained changes only for the intended two profiles. Hermes profiles and
  global runtime had no active turn leases at the publication checks.
- All 12 installed procedure destinations match canonical bytes: four Codex,
  four global Hermes, four generalist-local Hermes packages. Fresh Codex
  app-server `skills/list` and Hermes catalog processes resolve the expected
  installed files. These post-publication discovery checks did not run model
  inference or create live profile chats; behavioral runs used the identical
  frozen candidate before publication.
- Full mirror checks pass: 247 Codex persona mirrors, the preserved non-persona
  `web-application-builder` collision, and all 19 portable packages in both
  runtimes. The 248-profile aggregate and whitespace/link checks pass.

The generalist's pinned external snapshot and configuration remain unchanged.
The four maintained packages now reside in `skills.local/software-development`;
Hermes confirms that these local copies take precedence. The reviewer continues
to use the global skill library. No snapshot re-isolation or blanket replacement
was performed.

Publication receipts and rollback metadata are retained in
[the publication evidence directory](/Users/aindaco1/.local/share/agents-evidence/2026-11-09-roster-pilot/live-publication).
Hermes profile transactions are `49569a9dd18b4949a3ea1c40fa4433e3` (generalist)
and `8b6f966aa85c42cb8629f2866ac3d15f` (reviewer). Use the supported compiler
`recover <profile> --transaction <id>` only while it remains the current
transaction and after inspecting newer edits. Package/persona manifests and
private transaction journals retain the other rollback identities. The
[publication contract](../profile-publication.md) governs recovery; the publisher
is not an atomic multi-profile transaction.

## Protected-state qualification

Recorded learned-memory and configuration files, skill links, unrelated local
skill metadata, and the Codex `web-application-builder` collision are preserved.
Only the four selected packages' managed ownership flags changed in the
local usage sidecar; unrelated records are identical. Existing OAuth credentials
were referenced, not copied into fixtures; normal credential refresh was not
byte-audited. No Codex-managed memories were edited.

Codex CLI added 15 task-workspace trust tables despite the isolated invocation
flags. They were removed through the shared publication helper, with a private
rollback journal. All unrelated Codex configuration bytes match the normalized
pre-task hash.

Two live Hermes `state.db` hashes changed during the pilot **before publication**
(their recorded mtimes are 02:40:54 and 02:42:07 UTC; publication began 02:44:43).
Both pass SQLite integrity checks and have zero sessions, messages and active
turn leases. Their runtime epoch matches at 226, consistent with gateway/runtime
bookkeeping, but no logical before-snapshot was retained to establish the exact
delta. Therefore **database byte preservation is not claimed**. No older database
or epoch was restored. This limitation does not negate the independently checked
memory/configuration preservation or synthetic publisher recovery tests.

## Next rollout stage

The two-profile publication is complete. The plan's broader nine-profile cohort
remains a later stage after two operational task cycles. Review evidence quality,
missed triggers, user corrections, and overhead on real work before expanding;
keep the frozen held-out set labeled as already used. No recurring evaluator,
schedule, automatic policy learning or model-default change was introduced.
