# Jev for shared agents: audit and measured pilot

Reviewed September 23, 2026. Scope: the canonical iCloud agents repository,
Cutnotes' existing Cloudflare evaluator, and the shared Dust Wave Platform adapter.
No production Cloudflare configuration, generation model defaults, credentials,
Cutnotes source, or other Hermes profiles were changed by this work.

## Decision

Use Jev as a small, opt-in semantic evaluator alongside deterministic checks.
Start with Agent Performance Analyst, Prompt Engineer, and AI Workflow Designer.
Keep automatic routing, generation, release approval, security enforcement and
business-state correctness outside Jev. Do not replace the main agent with it.

The immediate savings come from fewer unnecessary calls, small states, and
multiple independent questions in one request—not from adding a new model call
to every user turn. Improve the existing deterministic router before considering
a semantic one. Keep procedures in one portable package rather than expanding
all personas or embedding every skill in every prompt.

## What the audit established

- The canonical repo contains 247 profiles and, before this work, seven portable
  procedure packages. Its aggregate roster was 1,502,061 bytes. Feeding the whole
  aggregate to a judge is wasteful; routing should use a small relevant shortlist.
- Cutnotes uses a Python development evaluator outside its user-facing formatter.
  Its allowlisted synthetic inputs and hash-bound calibration are useful patterns.
  Its default development command is live: do not copy that default into shared
  agent tooling, where many more people and routines may trigger it.
- Platform already owns reusable Choice request construction, Cloudflare
  transport, strict response validation and advisory batch evaluation. Pool and
  Store consume it. This implementation reuses that code, not a third client.
- The generic shared wrapper supports pass/fail/uncertain Choice only. General
  routing Choice, Noul and Score need additional characterized shared support;
  this change does not pretend they are implemented.
- `typesafe/jev` is an alias. Record the returned version and send unfamiliar
  versions to review. Do not claim that an allowlist pins the provider version.
- Historical Cutnotes evidence missed a one-second timestamp mutation caught by
  deterministic checks. Pool observed semantic false alarms and changed decisions
  around saved payment methods versus confirmed pledges. Store observed a stable
  review classification despite a changed leading answer. These are reasons to
  keep abstention and deterministic authority, not tune toward green results.
- Codex mirrors did not expose procedure-skill links. The synchronizer now carries
  compact, deduplicated links without inlining the procedure package.
- The checkout had 250 pre-existing untracked iCloud duplicate-named artifacts.
  They are not part of this change and must not be swept into skill packages.

## Live Cloudflare comparison

The new built-in corpus has eight engineering-authored public synthetic cases,
with two semantic questions per case. Four faithful/flawed pairs cover handoffs,
uncertainty, source grounding, and omitted requirements. Expected labels stayed
outside model inputs. Questions and policy were frozen across variants.

Existing Cutnotes credential discovery supplied credentials only to the child
process environment. No token or account ID was written into the repository or
evidence. No retries, caches, fallback, purchases or credit top-ups occurred.

| Measurement | Batched: two corpus passes | Split: one corpus pass |
|---|---:|---:|
| Network requests | 16 | 16 |
| Questions evaluated | 32 | 16 |
| Matching engineering labels | 32 | 16 |
| False passes / false failures / reviews | 0 / 0 / 0 | 0 / 0 / 0 |
| Decision flips between repeated batched passes | 0 | Not measured |
| Input tokens | 9,692 | 7,226 |
| Output tokens | 1,268 | 658 |
| Median request latency | 358.5 ms | 329 ms |
| Summed request time | 6,655 ms | 6,428 ms |
| Published-rate inference estimate | $0.000407064 | $0.000303492 |

Both variants returned `jev-1.13.0`. For an equal corpus pass:

- Batched checks used 4,846 input tokens versus 7,226: 32.94% fewer, with the same
  percentage reduction in inference cost at the published input-token rate.
- Requests fell from 16 to 8: 50% fewer.
- Mean summed request time for a batched pass was 3,327.5 ms versus 6,428 ms:
  48.23% less in this run. The two batched passes took 4,020 and 2,635 ms separately.

This is not an end-to-end agent speedup claim. The comparison was small, sequential,
not randomized, and the batched runs preceded the split run. It measures aggregate
request latency, excluding setup, credential acquisition, and file persistence.
Cold starts/service load can explain part of the difference. Labels are engineering
controls, not independent human validation; there are no ambiguous controls here.
Passing them does not establish accuracy on real agent output or bilingual work.

The total published-rate estimate was $0.000710556 against a conservative total
reservation of $0.064512. This is not verified billing. TypeSafe publishes
$0.042/million input tokens and free output. Cloudflare account pricing must be
checked in its dashboard; a 5% credit-purchase fee applies if Unified Billing is
used. The report includes that conditional estimate separately.

Machine-readable results, hashes, and per-repeat measurements:
[2026-09-23-benchmark.json](2026-09-23-benchmark.json).
[Sanitized per-case observations](2026-09-23-observations.json) preserve every
answer distribution, token count, request hash and measured latency for offline
replay in another checkout. Original raw local reports remain gitignored at
`.local/jev/batched/report.json` and `.local/jev/split/report.json`; the summary
records their SHA-256 values. The exact [pilot runner](2026-09-23-pilot-runner.json)
is archived as non-executable text, matching the pilot's runner hash.

After the pilot, review found two evidence-handling defects: arbitrary successful
provider metadata could enter reports, and an interrupted call had no pre-call
checkpoint. Regression tests reproduced both. The current runner persists an
allowlisted response projection and a pending request before transport, and adds
standalone corpus/label provenance. Its source hash therefore differs from the
archived pilot runner. The policy, corpus, shared adapter and reported observations
are unchanged; no post-fix live latency improvement is claimed.

## Implementation and operating policy

The portable [Jev skill](../../skills/software-development/jev-evaluation/SKILL.md)
is the single procedure source for Hermes and Codex. It carries a reproducible
benchmark, public controls, dependency lock, setup guide and contract reference.

- Offline by default; no custom/private corpus upload flag.
- Explicit dependency root, checked against the immutable Platform release's
  module/package hashes before import; no unversioned sibling dependency.
- Preflight of all inputs and aggregate question/spend budgets before credentials.
- Maximum 64 questions and $0.10 conservative reservation per invocation; at most
  three repeats; 32k-byte requests; 1 MB responses; 15-second request deadline.
- No automatic retry/fallback and no response cache during evaluation.
- Exact answer-key and probability validation; unfamiliar versions, uncertainty,
  ties and low margins route to review; transport/validation errors are unavailable.
- Immutable run directories, atomic pre/post-call progress reports, replayable
  allowlisted response evidence, request/corpus/policy/code/dependency hashes,
  label provenance, token usage, latency and repeat flips. Pending attempts may
  or may not have reached the provider; incomplete evidence is not a zero bill.
- The 0.10 review margin is provisional, not calibrated. `releaseAccepted` is
  always false. Failed-request costs are explicitly incomplete.

The runner adds consumer-specific orchestration rather than modifying Platform.
In particular it persists failure timing after the request finishes, avoiding the
current shared batch helper's error-progress ordering issue. That upstream issue
is documented, not silently patched in a separate repository.

## Deterministic and packaging corrections

The router now ignores poor-fit and handoff text as positive evidence, recognizes
whole-token `qa`, `sql`, and `rag`, refuses zero-score automatic execution,
validates positive `--top` values, and selects exactly 50 profiles in first-50
mode. With `--all`, the verified pull-request review example selects
`senior-code-reviewer`; `qa` selects `qa-engineer`. The heuristic is still not a
trained intent classifier. Use an explicit slug or full-roster search when the
first-50 subset cannot contain the required specialist.

Portable sync excludes conflict-copy filenames and accepts repeatable `--skill`
selection, with unknown names rejected before writes. It leaves source duplicates
and destination extras untouched. Its ordinary check compares canonical files,
not all destination extras; the new Jev package is separately compared as a full
tree during installation verification.

The three agents' identity references, invocation/capability metadata and
`hermes_skills` links were updated, along with the generated aggregate. SOUL.md
writes were denied by the instruction-file guard and were not retried. No runtime
profile, memory, model alias or config was overwritten. Avoid bulk compilation as
a shortcut: the existing compiler overwrites runtime memories/config and replaces
its manifest with the selected batch. This work verifies generated context and
Codex mirrors without recompiling live Hermes profiles.

## Verification completed

- Python repository suite: 60 passing tests.
- Offline Node suite: 10 consumer tests plus 7 shared-adapter tests, all passing.
  Coverage includes successful-response metadata stripping, pre-call checkpoints,
  persistence failure before transport, actual abort-signal delivery, dependency
  symlink escape rejection and replay of every published pilot observation.
- Aggregate roster current; model recommendations and protected SOUL files unchanged.
- The Jev package is synchronized into the default Hermes and Codex skill libraries;
  complete seven-file package trees match byte-for-byte. No other profiles changed.
- Installed-script preview performs zero network calls and remains unevaluated.
- Relative documentation links, evidence hashes and whitespace checks pass.

## Ranked next moves

1. Use batched, candidate-scoped semantic checks on already-authorized public
   synthetic work. Preserve deterministic tests and direct artifact verification.
   Avoid a second expensive agent just to check a closed semantic requirement
   when this small evaluator is sufficient and local validation supports it.
2. Build a realistic human-labeled holdout with ambiguous/partial outputs, missing
   evidence, instruction injection, domain-specific failures and language slices.
   Freeze false-pass tolerance and review cost before selecting thresholds.
   Revalidate after any rubric, parser, model or corpus change.
3. Only then trial skill suggestions in shadow mode: deterministic shortlist,
   compact descriptions, semantic suitability checks that can reject every option,
   no automatic launch and no removal of mandatory skill-loading rules. Measure
   wrong loads, abstentions, context tokens, wall time and cost per completed task.

Do not add a new always-on service, generic paid fallback, automatic retry ladder,
or cache layer yet. Current local routing is fast; quality and avoiding unnecessary
work matter more than shaving microseconds. Production cache reuse, if later
needed, must be keyed by full input, scope, rubric, parser and returned model version;
never count replayed responses as repeatability evidence.

## Source trail

Local implementation reviewed:
- Cutnotes: `scripts/jev_evaluation.py`, `scripts/calibrate-jev.py`,
  `tests/fixtures/jev-policy.json`, saved public synthetic diagnostics.
- Platform: `packages/test-core/src/jev.js`, `jev.d.ts`, and `test/jev.test.js`;
  locked release `60d439b887f1244f82ff232c849d74152b28c776`, Test Core 0.3.0.
- Pool and Store: `docs/release-evidence/2026-09-22-jev-pilot.md`.

Primary external sources, retrieved September 23:
- [Cloudflare Jev](https://developers.cloudflare.com/ai/models/typesafe/jev/)
- [TypeSafe models/pricing](https://docs.typesafe.ai/models.md)
- [API](https://docs.typesafe.ai/api) and [confidence](https://docs.typesafe.ai/confidence)
- [Jev 1.13 limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13)
- [Parallel questions](https://docs.typesafe.ai/cookbooks/parallel_questions)
- [Skill suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion)
- [Cloudflare billing](https://developers.cloudflare.com/ai-gateway/features/unified-billing/)
- [Caching](https://developers.cloudflare.com/ai-gateway/features/caching/) and
  [route limits](https://developers.cloudflare.com/ai-gateway/reference/limits/)

TypeSafe's published skill-selection and speed comparisons used other models,
constructed datasets and earlier Jev versions. They motivated this investigation;
they are not claimed as savings in our agents.
