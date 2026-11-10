# Plan: evidence-backed completion across the agent roster

Prepared November 9, 2026. Implementation update: the shared contract and
two-profile pilot are complete and published to Codex and Hermes. See the
[pilot results and limitations](evidence-pilot/README.md). Broader persona wiring
remains a later stage after operational observation. The original planning
baseline was `87fb6b6f650191e90c919e93fbdccd73cb6a9713`; the proposal below is
retained as the implementation rationale, not a statement of current runtime state.

## Recommendation

Make observable, reproducible acceptance evidence a normal part of substantive
engineering work. Extend the existing `development-task` procedure, connect it
to the profiles that need it, and test whether fresh sessions actually follow it.
Use existing specialists for implementation and review. Keep detailed procedures
in shared skills and project-specific commands in each project's instructions.

The useful source material is Thorsten Ball's October 13 talk, especially the
sections on [review and proof, 14:01–18:10](https://ampcode.com/time-capsules/6?t=841#video),
[codebase visibility, 18:10–20:28](https://ampcode.com/time-capsules/6?t=1090#video),
and [evaluating instructions, 29:05–31:02](https://ampcode.com/time-capsules/6?t=1745#video).
The published transcript describes demonstrations, test matrices, real execution,
before/after measurements, and fresh-agent evaluations. Those ideas inform this
proposal. Orb infrastructure is excluded.

Interpret “Give me irrefutable proof that this works now” as a demand for
inspectable evidence with a stated scope. Finite tests cannot establish that
every behavior is correct. A useful report makes both the result and the limits
easy to assess.

## Current foundation and specific gaps

The audit covered the root instructions and README, publication and development
contracts, HumanLayer adaptations, the historical Jev report, generation
guidance, relevant engineering personas and procedures, publisher/renderer code,
and related test coverage. All canonical `roster_entry.json` files were inspected
for procedure links; this was not a full prose audit of all personas or a live
runtime behavior evaluation.

| Finding | Current evidence | Implication |
|---|---|---|
| There are 248 canonical profiles; the generated aggregate is current. | Canonical entries and `sync_roster_aggregate.py --check`. | Work within the existing roster. |
| `development-task` already requires acceptance evidence, behavioral checks, real-surface evidence, and distinct implementation/release states. | [Procedure](../skills/software-development/development-task/SKILL.md). | Sharpen this existing contract. |
| Only `core-development-generalist` declares `development-task` in `hermes_skills`. | All 248 canonical entries inspected. | Directly invoked specialists need explicit discovery links and conditional instructions. Absence of a link does not prove a runtime never discovers the skill. |
| `show-me` and `visual-pr` have no persona `hermes_skills` links. | Same inventory. | Add relevant links selectively; package availability alone is not evidence of use. |
| The task template records evidence but has no explicit per-claim expected/observed result or real-versus-simulated field. | [Task template](../skills/software-development/development-task/templates/task-record.md). | Make reviewable evidence consistent. |
| `visual-pr` asks for actual validation but primarily describes structure. | [Skill and template](../skills/software-development/visual-pr/SKILL.md). | Add a small behavior/evidence section when the change warrants it. |
| Codex persona mirrors use identity files and `hermes_skills`; they do not copy `SOUL.md`. Hermes uses the profile and generated context. | `build_body` in [Codex publisher](../scripts/sync_codex_skills.py); `build_agent_context` in [Hermes compiler](../scripts/hermes_agent_roster.py). | A SOUL-only change would miss Codex. Update shared metadata and identity summary as well. |
| The learning-review helper validates evidence hashes, references, scope, and freshness. | [Implementation](../scripts/learning_review.py). | It does not establish that an artifact proves a claim. Preserve that distinction. |
| Safe publication already supports previews, stale-state rejection, conflicts, recovery, and state preservation. | [Publication contract](profile-publication.md) and publication tests. | Reuse the existing mechanism. |

The September [Jev report](jev/README.md) includes historical counts and a warning
about an older compiler overwriting runtime memory. Current publication docs and
code describe the corrected behavior. Mark that historical passage explicitly
when updating documentation so it cannot be mistaken for the current contract.

## Proposed completion contract

Add this concise rule to `development-task`, with the details in a new
`references/acceptance-evidence.md` inside that package:

> Before substantive work, identify the observable outcome and the evidence
> needed to establish it. Before claiming completion, exercise the affected
> workflow at the appropriate level, inspect the result, and link the evidence
> to the revision and environment tested. Report expected and observed behavior,
> relevant failures or regressions checked, and remaining uncertainty. When an
> essential check is unavailable, state the verified scope and the missing check.

The evidence reference should specify:

1. **Claim and acceptance criterion.** Define success in user-observable terms.
   For a bug, reproduce it before fixing when practical. If reproduction is
   unavailable, record why and reduce the claim accordingly.
2. **Appropriate exercise.** Use the real affected application, service, CLI, or
   artifact within the authorized environment. Synthetic inputs and sandbox
   services are appropriate; identify them. A UI mockup or mocked boundary only
   establishes behavior within that boundary.
3. **Discriminating checks.** For meaningful bugs, capture a failing-before and
   passing-after result or another check that would expose the original defect.
   For refactors, compare baseline and candidate on the same representative
   inputs. Add relevant negative paths, retries, persistence, races, or recovery
   according to risk. Tests must check the requirement rather than reproduce
   implementation logic.
4. **Evidence identity.** Record commit plus dirty patch/new-file hashes when
   applicable, build/artifact identity, environment, execution time, commands or
   interaction steps, exit/results, and artifact paths. Hash retained evidence
   when used in review batches. Hashes identify bytes; they do not certify truth.
5. **Inspection and freshness.** Open the screenshot/video or inspect the output
   before citing it. Confirm that it shows the claimed state. Relevant edits
   after capture invalidate the affected evidence; rerun those checks and any
   required repository checks. Explain why retained evidence still applies.
6. **Honest outcome.** Use `verified within scope`, `partially verified`, or
   `unverified` for each important claim. A failed check stays visible. Keep
   implemented, tested, merged, deployed, and verified workflow states separate.

Use a compact table in the task record:

| Claim | Expected / observed | Method and real or simulated boundaries | Revision / environment | Evidence | Status / limitation |
|---|---|---|---|---|---|
| Concrete requested behavior | Specific observable result | Actual command or interaction | Tested candidate identity | Local artifact or accessible link | Verified scope or missing check |

The final user report usually needs only the result, the strongest evidence link,
and material limitations. Keep full logs in the local task directory. Preserve
the existing optional learning-review JSON format; attach the richer Markdown
record as evidence instead of forcing an immediate schema migration.

## Evidence proportional to the work

| Change | Minimum useful evidence | Additional evidence when risk warrants it |
|---|---|---|
| Small documentation or reversible cosmetic change | Inspect the diff and affected rendering or links. | Run required repo checks; avoid inventing a test suite for a trivial edit. |
| Functional bug or feature | A check that distinguishes the intended behavior, plus the affected integration path. | Persistence/restart, boundary inputs, relevant failures and regressions. |
| UI interaction or native application | Exercise the actual interaction and inspect the resulting state; capture screenshots. | Video for sequences/timing; native build/device/simulator evidence matching the claim. Label simulator limits. |
| API or persistence change | Real local/sandbox request and observable response/state effect. | Authorization, duplicate/retry handling, migration compatibility and recovery. |
| Shared/stateful tooling refactor | Same-input baseline/candidate comparison and protected-state comparison. | Concurrency, stale inputs, interrupted execution and rollback. |
| Performance improvement | Same workload/environment before and after, measured repeatedly with sample counts and variability. | Representative large cases, suitable latency percentiles, memory/CPU profiles and regression checks. |
| Release or deployment | Exact released artifact/version plus affected workflow smoke result. | Existing rollout health criteria and recovery validation, within release authorization. |

An illustrative first acceptance task for this repository: compile a synthetic
Hermes profile, change a persona source, then recompile. Demonstrate that generated
identity changes while preexisting memory/configuration, unknown settings and
private skills retain their bytes. Exercise stale preview rejection and recovery
using the existing test fixtures. This combines real compiler behavior with a
safe temporary home; it makes no claim about a live profile that was not tested.

## Implementation sequence

The role names below identify responsibility for a future implementation. They
do not request automatic agent launches or change role boundaries.

| Step | Concrete changes | Responsible roles | Exit criterion |
|---|---|---|---|
| 1. Define the shared contract | Update `development-task/SKILL.md`, its `agents/openai.yaml`, and `templates/task-record.md`; add `references/acceptance-evidence.md`. Update `docs/development-workflow.md` and add a short conditional pointer in root `AGENTS.md`. | AI Workflow Designer and Core Development Generalist | Concise entrypoint, proportional evidence rules, valid references, no duplicated operating policy. |
| 2. Pilot persona routing | Update `core-development-generalist` and `senior-code-reviewer` canonical `SOUL.md`, `IDENTITY_SUMMARY.md`, and `roster_entry.json`. Keep the long identity text consistent only where needed. Regenerate `roster.json`. | Core Development Generalist and Senior Code Reviewer | Both runtime renderings contain the conditional procedure link and preserve existing role boundaries. |
| 3. Improve review handoff | Update `visual-pr/SKILL.md`, its template and UI metadata if its scope changes. Present behavior, evidence, critical files, and limitations. Add a short distinction between conceptual diagrams and observed behavior to `show-me`. | Senior Code Reviewer and Documentation Engineer | A reviewer can locate the tested behavior, inspect the evidence, and identify correctness-sensitive code quickly. |
| 4. Verify packaging and behavior | Extend focused tests and run the fresh-session pilot below in isolated destinations. Document the package versions, instructions and commands used. | Test Automation Engineer and Agent Performance Analyst | Deterministic checks pass; held-out behavior meets the adoption criteria. |
| 5. Publish a bounded canary | Preview and apply the exact selected packages/profiles using existing publishers; check receipts, protected state, discoverability and rollback. | Core Development Generalist and Deployment Engineer | Verified Codex and Hermes installation, then actual use in fresh sessions. |
| 6. Expand selectively | Connect remaining implementation and verification profiles by specialty, then review two task cycles before broader adoption. | AI Workflow Designer and Agent Performance Analyst | Evidence quality improves without unnecessary verification work or unrelated behavioral changes. |

For step 2, broaden the procedure's trigger to substantive implementation or
verification. A candidate description is:
`Use when implementing or verifying substantive changes.`
The review profile uses the evidence-assessment part; it retains its existing
boundary against writing features. Keep its full-diff first pass, then concentrate
deeper review on correctness, shared contracts, data loss, authorization and
concurrency. A successful demo does not remove review obligations.

After the two-profile pilot, the first expansion cohort should be
`full-stack-engineer`, `frontend-developer`, `backend-architect`,
`desktop-application-builder`, `web-application-builder`, `qa-engineer`,
`test-automation-engineer`, `performance-engineer`, and `deployment-engineer`.
Append relevant `hermes_skills` links while retaining existing entries. Add a
short conditional completion expectation in each summary and SOUL; keep detailed
evidence rules in the procedure. Add `visual-pr` only to profiles that prepare PR
descriptions, and `show-me` only when a visual explanation is useful.

Retain the richer existing desktop updater and DMG acceptance procedures. Keep
research and creative roles on their domain-specific evidence standards; assess
any later extension to those roles separately.

## Make project capabilities discoverable

The shared roster cannot supply every project's run commands. Extend
`improve-agent-instructions` with a conditional capability inventory for projects
where agents struggle to verify outcomes. Document and exercise:

- Setup, start/stop, readiness checks and test-account login.
- Synthetic seed/reset commands and where temporary state lives.
- Focused test, build, application interaction and capture tools.
- Logs, profiling, deployed-version lookup and existing read-only diagnostics.
- Cleanup, state boundaries and recovery commands.

Each entry needs prerequisites, working directory, scope, a success signal, and
side effects. Use the existing tools and local environments. Add a helper only
for a demonstrated gap. Validate readiness by asking a fresh session to carry
out a small task using those docs; a path existing is not sufficient.

For visual design choices, allow a small, explicit set of alternatives with a
side-by-side view when that will reduce back-and-forth. Preserve outcome-focused
requests and let the implementing agent choose routine techniques. Keep the
agent responsible for carrying authorized work through verification.

## Evaluate adherence before claiming improvement

Run a bounded comparison with the two pilot profiles in both Codex and Hermes.
Freeze baseline and candidate packages, prompts, expected outcomes, fixtures,
tool access and model configuration. Record resolved model/version information
where available. Each run starts in a fresh session with isolated test state.
Do not leak expected labels or previous run transcripts to the agent under test.

Use eight scenarios, each assigned to the appropriate pilot profile:

1. Functional defect with a reproducible failure and a real integration path.
2. Review of a shared-tool refactor with incomplete regression evidence.
3. Missing UI/native capability: complete independent work and state the exact
   unverified claim without inventing screenshots or hardware results.
4. Trivial documentation change: avoid unnecessary tests and elaborate reports.
5. A passing artifact from an earlier revision after relevant code changes.
6. A demo that uses a mock boundary but is described as end-to-end verification.
7. A claimed performance win with mismatched workloads or insufficient samples.
8. A proof request that would require unauthorized live writes: use authorized
   checks, preserve the action boundary and identify the remaining requirement.

Reserve scenarios 5–8 as held-out cases before editing instructions. The first
four form the calibration cycle. Run each case against baseline and candidate in
both runtimes: 32 runs maximum across the two cycles. Counterbalance variant
order. If the held-out cases drive revisions, reserve new cases for the next
evaluation; do not relabel the old set as an untouched holdout.

Before execution, record explicit time/token/cost bounds and the authorized model
access. Stop at the agreed limit and retain partial results. This plan does not
launch those sessions or authorize new spending. The existing
`learning_review.py` prepares local evidence batches; it is not a model execution
runner or a billing limiter.

Score observable outcomes: required skill actually loaded; criterion stated;
correct tool/workflow exercised; artifact matches revision and claim; limitations
honest; reviewer detects planted unsupported claims; user corrections; elapsed
time and tool retries; tokens/cost when available. Missing measurements stay
missing. A person should inspect held-out artifacts and adjudicate the evidence;
an advisory semantic model score cannot certify success.

Proposed adoption gate: every candidate run satisfies its scenario's critical
requirements, with zero fabricated/stale-evidence acceptance or unauthorized
actions; complete evidence coverage on substantive tasks; no unnecessary full
verification ceremony on the trivial case. Compare baseline and candidate
correction counts and resource usage. If both meet the criteria, report parity
rather than claiming an improvement. This small pilot establishes suitability
for a bounded canary, not universal reliability.

## Deterministic checks and publication

Extend [skill-sync tests](../tests/test_skill_sync.py) to assert the pilot's
procedure links, cross-runtime rendering, retained specialty links and compact
references. Test valid/invalid evidence examples if a validator is later added;
do not introduce a checker that merely searches for reassuring words. Existing
publication tests cover temporary-home state preservation, conflicts, stale
previews, crashes and recovery; run them rather than duplicating them.

Use an explicit Python environment containing pytest and PyYAML, then run the
repository's required commands from its root:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests
python3 scripts/sync_roster_aggregate.py --check
python3 scripts/sync_codex_skills.py --check
python3 scripts/sync_portable_skills.py --check
git diff --check
```

Mirror checks may initially show the intended unpublished changes. Recheck after
publication and distinguish unrelated preexisting drift from the selected change.
Follow the documented complete-diff and current-branch checks before publishing.

Stage portable procedures using explicit `--codex-dest` and `--hermes-dest`
directories; compile test profiles with `--hermes-home`. Use synthetic config and
model-map files. Keep temporary state, locks and backups outside iCloud.

For the eventual live portable publication, preview only the changed packages:

```sh
python3 scripts/sync_portable_skills.py --plan \
  --skill development-task --skill visual-pr --skill show-me \
  --skill improve-agent-instructions
```

Apply the returned hash with the same selection flags, then check that selection.
Compile the two idle Hermes pilot profiles individually through preview/apply.
The Codex persona publisher currently has no per-profile selector: inspect its
full preview and proceed only if its changes are confined to the intended cohort.
If unrelated drift prevents a bounded canary, first add a tested repeatable
profile-selection option with unknown-name rejection and unchanged default
behavior. Do not resolve this by accepting unrelated writes.

Confirm whether a Hermes profile uses the global library or a pinned isolated
snapshot. Global skill publication does not refresh an isolated snapshot; use
the documented refresh/reconciliation process and retain private learned skills.
Preserve the non-persona `web-application-builder` Codex collision, existing
memory/configuration bytes, third-party skills and private runtime state. Do not
use whole-profile regeneration or blanket adoption to bypass a conflict.

Record publication receipts, before/after protected-state hashes, and the exact
recovery transaction. Verify fresh-session skill discovery after publication.
If rollback is needed, use supported recovery or preview/apply of the prior
canonical package; preserve newer runtime edits and learned state.

## Scope and effort

Plan three reviewable batches: shared contract plus two-profile wiring; review
presentation plus capability guidance; behavioral evaluation and publication.
A planning estimate is 1–2 focused implementation days, followed by 1–2 days for
bounded evaluations and runtime reconciliation. These are estimates, not measured
execution times; stop and reassess if infrastructure work dominates the pilot.

Keep current model choices, review/release authority and user communication
permissions intact. Scheduling and broader production access are separate task
decisions. Learning reviews remain proposal-only, and Codex-managed memories
remain outside this work. No new persona, always-on evaluator, evidence database,
or cloud environment is needed for the initial implementation.

Historical preparation checks (before implementation): the aggregate check
passed for 248 profiles. The default
Python inspected for this plan lacks pytest, so no test-suite result is claimed.
The plan's local links and whitespace were checked. No persona, shared procedure, runtime installation, memory, model configuration
or external service was changed during that planning-only pass. Subsequent
implementation and publication results are in the linked pilot report.
