# Running the shared-agent benchmark

## Dependency, not a copied client

Requires Node 20.9+ and an explicitly selected Platform checkout. No npm install
or new model SDK is needed. `platform-lock.json` records Platform commit
`60d439b887f1244f82ff232c849d74152b28c776`, Test Core 0.3.0, and SHA-256 hashes
of the five package/module files in the transitive import chain. The loader
verifies every file before import. A newer checkout is usable only if those exact
bytes still match. Missing or changed files block evaluation before authentication.

If no matching checkout exists, obtain a separate dependency checkout, not a
checkout/reset of a colleague's working directory:

```sh
git clone --no-checkout https://github.com/aindaco1/dust-wave-platform.git "$HOME/.cache/agents-platform-jev"
git -C "$HOME/.cache/agents-platform-jev" checkout --detach 60d439b887f1244f82ff232c849d74152b28c776
export DUSTWAVE_PLATFORM_DIR="$HOME/.cache/agents-platform-jev"
```

An existing checkout may instead be supplied with `--platform-root PATH` or
`DUSTWAVE_PLATFORM_DIR`. Never resolve an unversioned sibling automatically.
To update the lock, characterize the adapter and all consumer behavior, record a
new immutable commit and hashes, then rerun the frozen benchmark. Do not merely
accept a mismatch. The lock intentionally avoids adding a second Jev client.

## Preview and live

From the agents repo (after sync, use the installed skill's absolute script path):

```sh
node skills/software-development/jev-evaluation/scripts/benchmark.mjs --help
node skills/software-development/jev-evaluation/scripts/benchmark.mjs --out .local/jev/preview-new
```

Default preview makes no credential reads or network calls. It writes all prepared
requests with labels outside the transmitted payload; `complete` and
`releaseAccepted` remain false. The CLI does not accept arbitrary case files.

Live requires process-only `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`.
Resolve them through an already approved local credential source; do not type
secret values into chat, shell arguments, logs, reports, or versioned config.
Cutnotes' `scripts/jev_evaluation.py:credentials()` is an existing local acquisition
path; its account comes from ignored `.cutnotes-development.json` and its token
from the environment or captured, pinned Wrangler authentication. The portable
runner does not discover another project's credentials or refresh them itself.

```sh
node skills/software-development/jev-evaluation/scripts/benchmark.mjs --live --repeats 2 --out .local/jev/batched-new
node skills/software-development/jev-evaluation/scripts/benchmark.mjs --live --split-questions --out .local/jev/split-new
```

Compare equal corpus passes, not raw totals: the example runs two batched passes
and one split pass. Eight cases each contain two semantic questions. Record run
order; time-of-day, cold starts, and service load confound this small comparison.
For stronger latency evidence randomize/interleave variants and repeat on a
separate day, without changing questions or labels.

Limits: repeats 1–3, 64 questions maximum, $0.10 maximum estimated reservation per
invocation, 32,000 bytes per request, 1 MB response, 15-second request deadline,
sequential transport, no retries, no fallback. Reservation uses 32,000 input tokens
per question at the dated rate, not a tokenizer-derived count or provider cap.
Each process gets its own reservation; sum reservations before starting multiple
runs. Request/latency limits are not a substitute for account-level spend controls.

Output directories must be new. `report.json` atomically checkpoints a pending
attempt before transport, then its result/failure and timing. A failed pre-call
checkpoint prevents transport. After interruption, a pending attempt may or may
not have reached the provider; `networkAttempts` is an upper bound until resolved,
not proof of a charge or a zero bill. There is no automatic resume or retry.

Persist only the validated response projection: model, numeric input/output usage,
answers and complete distributions, plus expected labels, findings and provenance.
Arbitrary provider envelope/debug metadata and invalid bodies are not retained.
Partial failures mark token/cost accounting incomplete. Evidence under `.local/jev/`
is gitignored; sanitized per-case evidence belongs in `docs/jev/`, never credentials
or private text. The built-in corpus classification and label provenance travel
with each report so engineering controls cannot be mistaken for calibration.

Exit codes: 0 = successful preview or fully evaluated matching controls;
1 = complete run with mismatch/review; 2 = preflight, transport, validation or
persistence failure. Exit 0 is never release approval.

## Caller-owned controls: bounded live probe

`scripts/live-probe.mjs` is an explicit live command, not the benchmark's default
preview. It reuses the same hash-locked adapter, parser, policy, budget preflight
and pending-attempt orchestration. It works from the repo, Hermes or Codex package
without runtime-specific APIs or a new SDK. The selected Platform dependency is
still required; the package is portable, not a bundled replacement client.

First prove the [controlled offline pattern](offline-controls.md). Supply a UTF-8
JSON corpus with the same schema as `cases.json`, optionally adding `category` on
each case. Labels remain local. Example shape:

```json
{
  "schemaVersion": 1,
  "classification": "public-synthetic",
  "labelProvenance": "Human-assigned engineering controls; not calibration.",
  "cases": [{
    "id": "separate-actions",
    "category": "save-vs-execute",
    "candidate": "Save the draft now. Send it only after approval.",
    "requirements": {"sequence": "Requires saving now and sending only after approval."},
    "expected": {"sequence": "pass"}
  }]
}
```

`reference` is optional per case. IDs must be distinct lowercase letters, digits
or hyphens; requirement keys must start with a lowercase letter and contain only
lowercase letters, digits or underscores (64 characters maximum). Expected keys
must match requirement keys exactly; labels are `pass` or `fail`. Private data is
not authorized by relabeling it `public-synthetic`. Omitted `--category` selects all
cases; a supplied category is an exact case-level filter and an empty match refuses.

```sh
node skills/software-development/jev-evaluation/scripts/live-probe.mjs \
  --controls /absolute/path/to/public-controls.json \
  --category save-vs-execute --max-usd 0.01 \
  --account-id-from /absolute/path/to/ignored-account.json \
  --out .local/jev/new-probe.json \
  > .local/jev/new-probe.stdout.json 2> .local/jev/new-probe.stderr.log
```

Create the redirection parent directory first. Do not redirect stdout onto the
`--out` path: shell redirection would create it before the script can reserve it.
Never merge stderr into a JSON file with `2>&1`. `--help`, successful results and
refusals all write one JSON document to stdout; progress/instructions use stderr.

Required `--max-usd` must be positive and at most $0.10. The complete selected
batch must satisfy `questionCount * 32000 * 0.042 / 1000000 <= maxUsd`, with at most
64 questions. Count questions, not cases; there are no repeats in this command.
All requests are prepared and byte-checked before credential reads or transport.
The same 32,000-byte request, 1 MB response and 15-second request limits apply.
The reservation is an estimate at a dated rate, not a hard provider billing limit.

Credential order:

1. `CLOUDFLARE_ACCOUNT_ID`, otherwise only the caller-selected `--account-id-from`
   JSON's `cloudflare_account_id` key. Never discover a neighboring product's file.
2. `CLOUDFLARE_API_TOKEN`, otherwise
   `~/Library/Preferences/.wrangler/config/default.toml`'s `oauth_token` and
   `expiration_time`. The macOS cache is optional; environment tokens work on other
   hosts and take precedence even if the cache has expired.
3. Cached OAuth must have more than 15 minutes left. Missing, malformed or expired
   timestamps refuse before any provider request. Run `wrangler login` manually
   and start with a new evidence path; no refresh token use or silent renewal.

`--out` is a new JSON file, never an existing file, directory or symlink. It stores
an initial report, then an atomic sanitized pending checkpoint before each call.
Failure to persist prevents transport. Provider/validation failure stops the batch,
without retries. A pending row after interruption or sanitation failure may have
been billed; it is not a pass and must not be replayed automatically.

Evidence is allowlisted: counts, expected labels, decisions, complete answer
probabilities, model, numeric usage, timings, dated price, and provenance hashes.
It excludes candidate/reference/question text, arbitrary fixture metadata, caller
paths, provider envelopes and usage debug fields. Validate values as well as field
names: `model` must be a version-shaped `jev-MAJOR.MINOR.PATCH` identifier (optional
lowercase prerelease suffix, 128 characters maximum), not arbitrary provider prose.
Well-formed unknown versions remain review, never pass; malformed identifiers stop
the batch with the last safe checkpoint intact. `sourceControlsSha256` hashes
the exact input bytes; `corpusSha256` hashes the selected parsed corpus. Keep the
public fixtures for label provenance and request reconstruction. Each checkpoint
is re-read, parsed and scanned for `cfoat_`, `cfort_`, `Bearer ` and complete 32-hex
account-shaped strings (including decoded JSON keys/values). SHA-256 hashes are
64 hex characters and are retained. Unsafe evidence refuses; the last safe pending
checkpoint remains. This scan is a backstop, not authorization to send secrets.

Exit codes remain 0 for fully evaluated matching controls, 1 for mismatch/review,
and 2 for preflight, transport, validation or persistence failure. `releaseAccepted`
is always false. Offline tests use simulated transport and do not call Cloudflare.

## Offline verification

```sh
TMPDIR="$HOME/.hermes/cache/scratch" DUSTWAVE_PLATFORM_DIR="/absolute/path/to/platform" node --test tests/jev.test.mjs
node --test "$DUSTWAVE_PLATFORM_DIR/packages/test-core/test/jev.test.js"
TMPDIR="$HOME/.hermes/cache/scratch" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests
python3 scripts/sync_roster_aggregate.py --check
python3 scripts/sync_portable_skills.py --skill jev-evaluation --check
```

The Node tests use mocked provider responses for deterministic unit behavior and
the real hash-locked adapter for parser/CLI integration. No offline test invokes
Cloudflare. Default Python tests remain offline too.
