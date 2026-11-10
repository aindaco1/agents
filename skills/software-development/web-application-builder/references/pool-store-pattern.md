# Pool/Store Infrastructure Pattern

Use this reference when a project should match Alonso's Pool and Store applications.

## Baseline

- Static site or app shell generated from simple assets, data files, and minimal browser JavaScript.
- Cloudflare Worker under `apps/worker` or `worker` owns validation, sessions, state transitions, admin mutations, signed/private routes, webhooks, email/SMS dispatch, cron, and provider integration.
- D1 or SQLite-compatible migrations hold relational state when the app needs durable structured data.
- KV is for ephemeral, session, rate-limit, and cache records; R2 is for private assets, exports, and backups; Durable Objects are reserved for race-sensitive coordination.
- GitHub Actions handle deployment checks and release/provider evidence.
- Podman or local scripts provide production-like rehearsal where the repo already supports it; prefer rootless Podman containers for the established Jekyll/Worker/browser-test setup.

## Trust Rules

- Never trust browser totals, permissions, inventory, payment state, provider status, admin power, or private access claims.
- Keep private responses `Cache-Control: no-store`.
- Validate request bodies at the Worker boundary and store only normalized records.
- Use deterministic idempotency keys for provider callbacks and mutations that can retry.
- Keep provider credentials in Worker secrets or local ignored files, never static config.
- Use integer cents for runtime money; keep payment, tax, shipping, inventory,
  fulfillment, and access decisions traceable to stored state and tests.
- When new data use, admin power, automation, messaging, public sharing, or
  analytics appear, run an ethical risk review within the task's authorization.

## Provider Defaults

- Stripe owns card data; the Worker owns app-side validation, idempotency, webhook verification, settlement state, and reconciliation.
- Choose PaymentIntents or setup/off-session flows to match the product, and
  verify webhook signatures against the raw request body.
- Resend sends transactional email through Worker-owned templates with no-send dry-run evidence.
- Localize email templates and obtain explicit consent for reminders/blasts.
  Do not rely on Stripe receipts when application-owned copy is required.
- SMS providers must support consent, opt-out, quiet hours, templates, audit logs, and non-production dry runs.
- Google OAuth, Drive, Calendar, Pool, Store, and Social integrations should start behind local or dry-run adapters until credentials and scopes are explicit.

## Common Docs

- `docs/SECURITY.md`: trust boundaries, data classification, auth, secrets, import/export, provider webhooks, and backups.
- `docs/TESTING.md`: unit, security, browser, and provider checks and how to run them.
- `docs/ARCHITECTURE.md`: app shape, data model, Worker/storage responsibilities, and local/offline posture.
- `docs/RELEASE.md`: release checklist and evidence paths.
- ADRs for material decisions such as auth, data model, backup/restore, provider key storage, and offline collaboration.
- Existing `ACCESSIBILITY.md`, `PERFORMANCE.md`, `SEO.md`, `I18N.md`, and
  `CUSTOMIZATION.md` retain their project-specific acceptance rules.

Also inspect the README, CHANGELOG, applicable AGENTS.md, project overview,
Worker README, package scripts, and deployment workflows. Prefer read-only
provider readiness probes where possible.

## Typical Commands

Use existing scripts if present. For new repos, prefer a small baseline such as:

```bash
npm run test
npm run test:security
npm run build
npm run smoke
```

Add provider-specific smoke tests in dry-run mode before live credential paths.

For existing Jekyll Pool/Store projects, retain their established layout and
commands: collections such as `_products` or `_campaigns`, `_config.yml`, and
translation catalogs at `_data/i18n/{lang}.yml`; Worker configuration in
`wrangler.toml`; generated catalog/campaign snapshots; and GitHub Actions for
Pages/Workers. Keep secrets in Wrangler or CI secrets, not static configuration.
These examples apply only when the project's scripts and configuration support
them; inspect the repository before choosing a command.

```bash
npm install
npm run podman:doctor
./scripts/dev.sh --podman
```

The historical local defaults are `http://127.0.0.1:4002` for Jekyll and
`http://127.0.0.1:8989` for the Worker. Confirm the actual configured ports and
readiness signals. Relevant verification examples are:

```bash
bundle exec jekyll build --quiet
npm run sync:worker-config
npm run test:unit
npm run test:seo
npm run test:content-security
npm run test:i18n
npm run test:security
SITE_URL=http://127.0.0.1:4002 WORKER_URL=http://127.0.0.1:8989 ./scripts/test-worker.sh
npm run test:premerge
npm run release:smoke -- --evidence-file /tmp/release-smoke.md
```

Run the relevant subset, then expand when payment, admin, email, or security
surfaces change. Stage only intended files, exclude secrets, and report
pre-existing dirty state separately.

## Additional acceptance details

- Accessibility includes skip links, live-region updates, mobile overflow, and
  200% text scaling. Automated axe/Playwright checks do not replace manual
  judgment on checkout and admin flows.
- Verify CSP/content security, webhook signatures, CSRF/origin boundaries, and
  token-scoped private access where applicable.
- Minify generated assets through project scripts, optimize media and local
  video facades, and avoid idle Worker reads/writes and namespace scans.
- Public SEO output includes canonical and localized alternate URLs,
  Open Graph/Twitter metadata, JSON-LD, sitemaps, and robots/noindex boundaries.
- Keep locale routes and labels consistent with translation catalogs. Do not
  machine-translate names, product titles, legal copy, or user content without
  human review; run locale-completeness and rendered i18n/SEO checks.
