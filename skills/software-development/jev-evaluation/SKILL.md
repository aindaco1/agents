---
name: jev-evaluation
description: "Use when evaluating agent outputs with Jev."
license: MIT
metadata:
  version: 1.0.0
  author: Alonso Indacochea and contributors
  hermes:
    tags: [jev, evaluation, cloudflare, performance, cost]
    related_skills: []
---

# Jev evaluation

## Purpose and boundaries

Use Jev for inexpensive, typed semantic evidence: output grounding, omission checks,
meaning preservation, and handoff completeness. Keep code, source inspection, and
human acceptance authoritative. Jev evaluates text; it does not generate a response,
verify a deployed artifact, authorize a tool, prove safety, or detect AI authorship.

Do not add Jev to generation-model aliases or failure fallbacks. Do not call it for
arithmetic, schema checks, exact identifiers, hashes, or obvious routing. Do not
change mandatory skill-loading rules, existing gates, or the user's default model.
An unavailable judge is unevaluated, never a pass.

## Workflow

1. Run deterministic checks first. Name the remaining semantic question, the
   authoritative source, and what a wrong pass would cost. If code or direct
   inspection answers it, stop without inference.
2. Minimize the state. Supply one candidate plus only the source it needs. Check
   omissions against candidate-only evidence; facts in a reference or question
   must not earn credit for missing candidate content. Keep independent checks
   sharing that state in one request; dependent checks require a separate stage.
   Completion: no complete conversation, roster, credentials, or private material
   is included merely for convenience.
3. Freeze cases, expected labels, questions, policy, parser/dependency versions,
   and model allowlist before comparing variants. Keep expected labels out of
   model inputs. Hold out independently human-labeled realistic cases separately
   from engineering controls. Completion: hashes and label provenance are recorded.
4. Prove the controls before live. Use a faithful simulated judge and a deliberately
   naïve baseline on the same frozen corpus; require the exact predicted false-pass
   count before spending. See [controlled offline probes](references/offline-controls.md).
   The packaged benchmark accepts only its built-in public
   synthetic corpus and defaults to zero network. Use its hash-locked shared
   Platform adapter; never copy a new Cloudflare client into each persona.
   The separate `scripts/live-probe.mjs` accepts caller-owned public synthetic
   controls with explicit `--max-usd` and a new `--out` JSON file. See
   [running the tools](references/running.md) for setup, schema and exact commands.
5. Opt in explicitly to a bounded live run. Preflight the complete batch before
   credentials/network: maximum questions, conservative spend estimate, request
   bytes, timeout, and new evidence path. No automatic retries, fallback,
   credit purchases, or caches. Checkpoint pending intent before each call; failure
   to persist blocks transport. Stop after a transport/validation failure. An
   interrupted pending request may still be billed; never silently replay it.
6. Inspect full distributions and abstentions, not just the winning answer.
   The provisional margin 0.10 is NOT calibrated for shared agents. Unknown model
   versions, ties, uncertainty, and low margins mean review. Do not tune wording,
   labels, or thresholds merely to turn failures green.
7. Compare false passes, false failures, reviews, unevaluated questions, repeat
   flips, request counts, reported tokens, and measured latency. Count review and
   escalation work in cost per successfully completed task. A schema-valid answer
   or high distribution confidence is not proof of correctness. Report estimates
   separately from provider billing. Keep replayable model/usage/answer distributions,
   not arbitrary provider/debug metadata. Completion: sanitized evidence and its
   provenance remain available; limitations accompany every performance claim.

## Shared-agent use

- Agent Performance Analyst owns labeled evidence and whether a change really
  reduces cost without hiding failure/review work.
- Prompt Engineer compares frozen variants; retain a fresh holdout after tuning.
- AI Workflow Designer keeps deterministic routing first and delegates only work
  requiring reasoning. A future Jev shortlist suggestion must be able to reject
  every candidate, must remain advisory, and needs local validation first.

Do not load every skill or dispatch parallel reviewers just to apply this process.
Pass compact, artifact-backed handoffs. Keep the procedure here; persona files
should link to it rather than duplicate it.

## Common pitfalls

- The Cloudflare `typesafe/jev` route is an alias. Record its returned model;
  `jev-1.13.0` in an allowlist does not pin upstream inference.
- The shared adapter currently supports Choice pass/fail/uncertain only. Noul and
  Score exist in the vendor API but require separate characterized support.
- Cache bypass/logging headers are not a promise of provider zero retention.
  Private transcripts, customer data, medical data, and secrets stay local unless
  their owner explicitly approves a separately reviewed data-handling workflow.
- Question keys are identifiers, not instructions. Express the full criterion in
  each question. Jev questions do not read one another's answers.
- Do not cache calibration/repeat trials. Future reuse caches need complete state,
  rubric, parser, model version, and authorization-scope keys plus invalidation.
- A price-based reservation is not a billing cap. Read the account dashboard for
  actual rates, credits and limits; never auto-top-up.
- Wrangler OAuth tokens have short expiration. Check the live clock after credential
  I/O, not at batch start; refuse missing/invalid expiry or 15 minutes or less remaining.
  Ask the operator to run `wrangler login`; never refresh automatically. An explicit
  environment API token takes precedence over the cache.
- Never use `2>&1` into a JSON evidence file. Keep stdout JSON-only and progress on
  stderr, with different paths for `--out`, redirected stdout and logs. For legacy
  mixed logs only, strip a known non-JSON prefix on read, then parse and validate
  the whole remaining JSON document. Do not silently repair canonical evidence.

## Verification

Require passing deterministic tests, a zero-network preview, response validation,
immutable evidence paths, and an honest decision about calibration. Keep Jev out
of ordinary offline tests and release acceptance. Use the linked benchmark as a
smoke test, not proof that real agent outputs are reliable.

Read [the contract and research](references/contract.md) only when designing a new
consumer or changing evaluation policy. The canonical repo's `docs/jev/` contains
the dated audit and measured benchmark, not always-loaded prompt content.
