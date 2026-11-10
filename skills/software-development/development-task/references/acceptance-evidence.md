# Acceptance evidence

Use for substantive implementation and verification. Evidence establishes a
specific observed outcome in a stated environment; finite checks cannot prove
that every behavior is correct. Preserve the user's scope and existing release,
communication and memory authority.

## Establish and exercise the claim

Define user-observable acceptance criteria. Reproduce a meaningful defect before
fixing it when practical; otherwise explain the missing baseline and limit the
claim. Use a discriminating check that would expose the original defect, rather
than a test that mirrors implementation logic. For refactors compare baseline
and candidate on the same representative inputs.

Exercise the actual affected application, service, CLI or artifact within the
authorized environment. Synthetic inputs, local fixtures and sandbox services
are useful; identify those boundaries. A mock verifies only its exercised path,
not a real provider, persistence layer, deployment or delivery it bypasses.

Choose evidence proportional to the change:

| Work | Useful evidence |
|---|---|
| Small documentation/cosmetic edit | Inspect the diff and relevant links/rendering; run required checks without inventing a test suite. |
| Feature/bug | Distinguishing behavioral check and affected integration path; relevant edge/failure/regression cases. |
| UI/native interaction | Exercise actual interactions and inspect resulting state; screenshots, or video when sequence/timing matters. Label simulator and device limits. |
| API/persistence | Real local/sandbox requests and observable state effects; relevant authorization, retry, duplicate and migration cases. |
| Shared/stateful tooling | Same-input baseline comparison, protected-state checks and relevant concurrency, stale input, interruption and recovery cases. |
| Performance | Matched workload/environment before and after, repeated measurements, sample counts and variability; suitable latency percentiles or profiles. |
| Release/deployment | Exact released artifact/version and affected workflow smoke result; existing health and rollback criteria within authorization. |

## Identify and inspect evidence

Record the commit and, for uncommitted work, a patch/new-file hash or an explicit
inventory of the tested file hashes. Include artifact/build identity, environment,
execution time, commands or interaction steps, exit/results and evidence paths.
Keep logs local; redact secrets and private user data before sharing artifacts.
Hashes identify bytes and freshness, not the truth of a claim.

Open captures or inspect outputs before citing them. Confirm that they show the
claimed state. Relevant later edits invalidate affected evidence; rerun those
checks and required repository checks. Explain why retained evidence still
applies. Never reuse a passing result from another revision without that check.

For each important claim record expected and observed behavior, method and
real/simulated boundaries, tested revision/environment, evidence, and status:
`verified within scope`, `partially verified`, or `unverified`. Preserve failures
and material uncertainty. Distinguish implemented, tested, merged, deployed and
verified in the affected workflow. If tools/access are missing, complete available
work and name the remaining check; do not fabricate captures or infer live success.

## Assess a handoff

Read the complete relevant diff and inspect the evidence. Prioritize deeper
review of correctness-sensitive code: shared contracts, data loss, authorization,
concurrency and recovery. A polished demo, a green test count or a model score
does not substitute for checking these. Stay within the review role's boundaries.

Keep the final report proportional: observable result, strongest accessible
evidence, and material limits. Put the detailed matrix in the task record. For
learning reviews, retain the existing JSON contract and attach the Markdown
record as hashed evidence; never imply its hash certifies behavioral correctness.

For functional fixes and substantive reviews, save a short local acceptance note
before reporting completion and link it in that report. Reuse an existing task
record; a paragraph or compact table is sufficient. Identify tested/inspected
files by hashes or commit plus dirty patch/new-file identity, environment, actual
checks/results and remaining limits. Source review does not require running a
missing application: record the inspected scope and the unperformed runtime check.
Small functional diffs still need this evidence; trivial text/cosmetic edits do not.
