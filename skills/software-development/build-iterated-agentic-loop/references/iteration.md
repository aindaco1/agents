# Optional maintainer iteration

Install `agent-iteration.py` into `.github/scripts/agent-iteration.py` and enable the commented `issue_comment` trigger only if the user wants `/iterate` support. The helper uses Python's standard library and the GitHub CLI, without shell-evaluating event text.

The workflow checks out its trusted default branch first so the gate/helper and prompt are not supplied by a PR. The gate requires current write/maintain/admin permission, an exact `/iterate` command, an open matching PR with label and marker, the expected base and branch prefix, the bot author, and a same-repository head. Adapt the expected bot login for a deliberately configured GitHub App. A marker is only a routing signal.

After the gate passes, fetch the checked SHA and reuse the existing branch. Keep the original task prompt and validation scripts from the trusted checkout. The helper appends the authorized trigger as scoped feedback and JSON-encoded PR/comment context as untrusted evidence. It paginates comments and retains file/line context for review comments.

The agent may propose concise standing feedback in the loop's repository memory file only if this is included in the scope contract. It does not edit personal Hermes/Codex memories. The workflow independently validates, commits and pushes the existing branch without force; a concurrent update causes a normal push failure rather than overwriting another contributor.

Append the same footer marker when updating the PR body so future requests remain routable. The template updates the PR description rather than posting extra comments. If no code or authorized feedback changes, leave the PR alone.

Offline cases to exercise before enabling: unauthorized commenter, `/iterate-other`, wrong label/marker, closed PR, wrong base/prefix, fork head, missing branch SHA, open-PR bound, explicit manual override, API failure, and literal shell-looking feedback. A failed API request must not turn into permission to run.
