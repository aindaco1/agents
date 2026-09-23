# Contract and sources

Reviewed 2026-09-23. Recheck current vendor/account details before revising limits.

## API and authority

Cloudflare documents POST `/client/v4/accounts/{account}/ai/run` with
`{"model":"typesafe/jev","input":{"state":{},"questions":{}}}`. Credentials
need Workers AI Read. This is not the OpenAI chat-completions contract.
The shared Platform adapter exposes `createJevRequest`, `judgeJevResponse`,
`callCloudflareJev` and `evaluateJevCases` from `@dustwave/test-core/jev`.
Our benchmark reuses request construction, parsing and transport, adding consumer
budgets, label metrics, repetitions and final evidence persistence. It deliberately
does not use the shared batch helper's failure-progress ordering: the current
helper saves an error snapshot before adding elapsedMs in finally.

The shared wrapper supports Choice with exactly pass/fail/uncertain, not general
Choice routing or Noul/Score. It validates answer keys, model, distributions,
winning choice and usage; accepts direct, Cloudflare-envelope and Completed-job
responses; rejects pending jobs rather than polling. An unrecognized model is
review, not approval. Question confidence/probability is evidence, not a locally
measured correctness guarantee.

TypeSafe offers Noul (yes probability), Choice (closed categories) and Score
(ordered levels). Noul has no separate confidence; Score is a weighted ordinal
level, not exact arithmetic. To support these here, extend the shared Platform
contract with tests and independent consumer migration evidence first.

## Pricing and route differences

TypeSafe publishes $0.042/million input tokens and free output. Cloudflare sends
account-specific pricing to its dashboard. Unified Billing passes through provider
rates but applies a 5% credit-purchase fee; the runner presents that conditional
estimate separately. Neither estimate is a billing receipt or an enforced cap.
Gateway core analytics/cache/rate limiting being free does not make inference free.

Cloudflare lists 32k context; TypeSafe lists 64k total with a 32k state-plus-longest-
question constraint. Keep our conservative 32k-byte payload bound. TypeSafe's
published 1,200 requests/minute and 250k tokens/second are changing direct-service
limits. Cloudflare's documented 200 requests/60 seconds per gateway for managed
credentials does not establish this account's actual quota. Handle rejection by
stopping and reporting unavailable, not a retry storm.

## Prior evidence and what it permits

Cutnotes' Python evaluator has source allowlists and hash-bound calibration policy;
it is a development evaluator, not the formatter. Its historical evidence missed
a one-second timestamp mutation that exact checks caught. Pool and Store consume
the existing shared JS adapter, with their own labels and budgets. Pool observed
saved-card/confirmed-pledge false alarms and changed decisions; Store observed a
stable review classification with a changing leading choice. These results justify
abstention and local calibration, not removing tests or lowering thresholds.

This package's eight engineering-authored cases cover handoffs, uncertainty,
source grounding, and omissions. They are simple smoke controls, not independently
labeled production tasks. An operational policy needs human-labeled realistic
positives/negatives and ambiguous cases, held-out validation, per-domain/language
error rates, explicit false-pass tolerance, and retesting after any model, rubric,
parser or fixture change. Keep calibration and validation separate.

## Efficiency decisions

Batch only independent questions sharing the same state. Keep state small; avoid
transmitting all 247 personas or full conversation histories. Deterministic routing
costs no inference and should precede a short advisory semantic check if needed.
The vendor's two-stage skill suggestion first ranks descriptions, then checks a
small shortlist with the ability to reject all candidates. Its published results
used Jev 1.12, Haiku and constructed prompts; they are not evidence for this roster.
Do not inject dynamic system-prompt suggestions into Hermes without checking its
prompt-cache contract. Do not mutate toolsets mid-session to chase small savings.

A later semantic router should be an explicit shadow experiment: fixed shortlist,
no automatic launch, no credentials until approved inputs are bounded, measured
wrong-skill loads and abstentions, and a deterministic fallback. The current
package does not implement that router. Cheap evaluation is useful only when it
removes more expensive review/rework without losing quality.

## Primary sources

- https://developers.cloudflare.com/ai/models/typesafe/jev/
- https://docs.typesafe.ai/models.md
- https://docs.typesafe.ai/api
- https://docs.typesafe.ai/confidence
- https://docs.typesafe.ai/model-jaggedness/jev-1.13
- https://docs.typesafe.ai/cookbooks/parallel_questions
- https://docs.typesafe.ai/cookbooks/skill_suggestion
- https://developers.cloudflare.com/ai-gateway/features/unified-billing/
- https://developers.cloudflare.com/ai-gateway/features/caching/
- https://developers.cloudflare.com/ai-gateway/reference/limits/
- https://hermes-agent.nousresearch.com/docs/user-guide/configuration

Vendor speed and quality claims are not measurements of this user's workflow.
