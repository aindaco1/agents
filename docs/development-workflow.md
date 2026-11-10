# Development evidence and learning

`development-task` supplies one compact task contract for Hermes and Codex.
`review-development-lessons` supplies a manual, proposal-only review. Both are
canonical portable skills and use the normal publisher. Neither changes personal
memory policy or enables a schedule.

For substantive implementation and review, use the shared
[acceptance-evidence contract](../skills/software-development/development-task/references/acceptance-evidence.md)
and [task record](../skills/software-development/development-task/templates/task-record.md).
Establish observable criteria, exercise the affected workflow and inspect evidence
tied to its tested revision/environment. State real/simulated boundaries, expected
versus observed results and missing checks. Relevant edits invalidate affected
evidence. Keep trivial changes lightweight and retain existing role boundaries.

The richer Markdown record can be attached as evidence in the unchanged JSON
format below. Hash validation establishes identity/freshness, not whether a claim
is true. Runtime discovery and behavioral adherence require fresh-session checks.

Keep outcomes and evidence in a local task directory. The optional JSON record
used by `scripts/learning_review.py` has this shape:

```json
{
  "id": "task-001", "session_id": "session-001", "scope": "agents-development",
  "runtime": "codex", "status": "complete",
  "outcome": "Recompilation preserves learned memory",
  "evidence": [{"path": "/absolute/local/test-result.txt", "sha256": "SHA256"}],
  "confirmed_defect": true, "explicit_user_instruction": false
}
```

Prepare a batch, supplying every budget explicitly:

```sh
python3 scripts/learning_review.py prepare --scope agents-development --repository /absolute/agents \
  --record /absolute/task-001.json --output /absolute/local/review-batch \
  --max-input-tokens 24000 --max-cost-usd 1 --max-seconds 1200
python3 scripts/learning_review.py validate --batch /absolute/local/review-batch \
  --proposals /absolute/local/proposals.json
```

The helper only captures and validates local evidence. It makes no model calls,
publishes nothing, and does not enforce a model provider's billing. A future
execution runner must enforce the recorded limits, including retries. Until then,
run the review interactively within those limits. `max-cost-usd: 0` means no paid
API execution, not unlimited spending. Private evaluation is never implicitly
authorized by creating a batch.

The proposal JSON is `{"proposals": [...]}`. Each item has `id`, `claim`, `kind`,
`change`, `evidence_ids`, `target`, `target_sha256` (null for a new file),
`validation`, `rollback`, `recheck`, and `uncertainty`. `kind` is one of `code`,
`test`, `configuration`, `procedure`, `fact`, `user-preference`. Generalized
proposals require independent sessions; a confirmed defect or explicit preference
uses the corresponding record flag. These flags are evidence claims for human
review, not proof of truth. Validation checks references and freshness only.

Pilot with two profiles and a small baseline of representative tasks. Reserve
held-out cases before tuning. Record acceptance, retries/corrections, wall time,
context/token usage, and actual cost when available. Missing measurements remain
missing. Deterministic fixture success does not establish improved model behavior.
Review two cycles before expanding unattended operation.

The November 2026 [two-profile evidence pilot](evidence-pilot/README.md) records
behavioral results, publication receipts, resource observations and limitations.
New pilots use the [guarded harness](pilot-harness.md), which retains SQLite
snapshots and logical differences and fails closed on isolation or state drift.
