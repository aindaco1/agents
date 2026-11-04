# Review contract

The input batch records its project/privacy scope, exact task/session IDs, current
evidence-file hashes, a maximum of ten tasks and three proposals, and explicit
token, spend, and wall-time limits. Use local files without credentials or raw
customer data. Include only the portions needed for the question under review.

Each proposal contains:

- Claim and exact proposed change.
- Kind: code, test, configuration, procedure, fact, or user preference.
- Destination and current revision/hash.
- Supporting independent task/session IDs and failure/opportunity counts.
- Counterexamples, uncertainty, and why this is the correct owner of the fix.
- Validation, recheck trigger, and rollback reference.

Keep an untouched baseline and reserve held-out cases before instruction tuning.
Compare equivalent model/provider/tool/repository conditions. Record unavailable
measurements as unavailable. Quality, state preservation, and scope come before
efficiency targets. Two successful review cycles are a rollout criterion, not a
reason to create an unattended schedule immediately.
