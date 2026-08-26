# Pool/Store Infrastructure Pattern

Use this reference when a project should match Alonso's Pool and Store applications.

## Baseline

- Static site or app shell generated from simple assets, data files, and minimal browser JavaScript.
- Cloudflare Worker under `apps/worker` or `worker` owns validation, sessions, state transitions, admin mutations, signed/private routes, webhooks, email/SMS dispatch, cron, and provider integration.
- D1 or SQLite-compatible migrations hold relational state when the app needs durable structured data.
- KV is for ephemeral, session, rate-limit, and cache records; R2 is for private assets, exports, and backups; Durable Objects are reserved for race-sensitive coordination.
- GitHub Actions handle deployment checks and release/provider evidence.
- Podman or local scripts provide production-like rehearsal where the repo already supports it.

## Trust Rules

- Never trust browser totals, permissions, inventory, payment state, provider status, admin power, or private access claims.
- Keep private responses `Cache-Control: no-store`.
- Validate request bodies at the Worker boundary and store only normalized records.
- Use deterministic idempotency keys for provider callbacks and mutations that can retry.
- Keep provider credentials in Worker secrets or local ignored files, never static config.

## Provider Defaults

- Stripe owns card data; the Worker owns app-side validation, idempotency, webhook verification, settlement state, and reconciliation.
- Resend sends transactional email through Worker-owned templates with no-send dry-run evidence.
- SMS providers must support consent, opt-out, quiet hours, templates, audit logs, and non-production dry runs.
- Google OAuth, Drive, Calendar, Pool, Store, and Social integrations should start behind local or dry-run adapters until credentials and scopes are explicit.

## Common Docs

- `docs/SECURITY.md`: trust boundaries, data classification, auth, secrets, import/export, provider webhooks, and backups.
- `docs/TESTING.md`: unit, security, browser, and provider checks and how to run them.
- `docs/ARCHITECTURE.md`: app shape, data model, Worker/storage responsibilities, and local/offline posture.
- `docs/RELEASE.md`: release checklist and evidence paths.
- ADRs for material decisions such as auth, data model, backup/restore, provider key storage, and offline collaboration.

## Typical Commands

Use existing scripts if present. For new repos, prefer a small baseline such as:

```bash
npm run test
npm run test:security
npm run build
npm run smoke
```

Add provider-specific smoke tests in dry-run mode before live credential paths.
