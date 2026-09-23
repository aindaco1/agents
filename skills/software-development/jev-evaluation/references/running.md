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
