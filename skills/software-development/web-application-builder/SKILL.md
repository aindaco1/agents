---
name: web-application-builder
description: "Use when building a complete static-first web application."
license: "All rights reserved"
metadata:
  version: "1.0.0"
  author: "Dust Wave"
  short-description: "Build static-first Worker-backed web apps"
  hermes:
    tags: [web-apps, cloudflare-workers, static-first, release]
    related_skills: []
---

# Web Application Builder

Use this skill to turn a project scope into a working, operable web application. Prefer static-first public surfaces and lightweight browser JavaScript, with Cloudflare Workers owning stateful or sensitive behavior.

## When to Use

Use for substantial implementation of commerce, crowdfunding, ticketing, RSVP, download, campaign, admin-dashboard, PWA, provider-backed, or lightweight serverless web applications.

Do not use for a visual mockup, copy-only landing page, or a native desktop application.

## Operating Standard

- Keep public browsing, metadata, localized copy, and generated assets static whenever possible.
- Treat the browser as untrusted. Recalculate permissions, state transitions, money, signed access, admin mutations, provider callbacks, and email/SMS eligibility in the Worker.
- Keep provider integrations dry-run capable until production credentials and policies are explicit.
- Ship docs and tests with the feature. Do not call a feature complete without setup notes, operator behavior, failure handling, and verification evidence.
- Cut optional scope before weakening security, privacy, accessibility, performance, or test gates.
- Put brand, URLs, routes, locale labels, public metadata, provider toggles, and customization knobs in config or data files where practical.

Read [references/pool-store-pattern.md](references/pool-store-pattern.md) when the task asks to mirror Alonso's Pool/Store infrastructure, includes payments, email, admin, or release gates, or needs a concrete local development and test baseline.

## Intake

Before coding, establish:

1. Product shape: public pages, app surfaces, admin/operator surfaces, primary actions, and success states.
2. Data model: static collections, generated snapshots, Worker records, database tables, provider IDs, and backup/export data.
3. Trust boundaries: public, private, signed, admin-only, provider-owned, sensitive, and untrusted browser input.
4. Provider map: Cloudflare Worker/D1/KV/R2/DO, Stripe, Resend, Turnstile, Google, SMS, GitHub, or other APIs.
5. Acceptance gates: unit tests, security checks, accessibility evidence, Worker smoke, provider dry-runs, offline/backup checks, and release evidence.
6. Cut line: the smallest feature-complete slice that can be implemented without pretending risky flows are done.

Ask only for decisions that block implementation. Otherwise proceed with explicit assumptions. Intake is complete when every trust-sensitive action has an owner and every requested surface has an observable success state.

## Build Pattern

1. Inspect existing docs and scripts: README, package scripts, Worker config, deployment workflows, security/testing docs, and local conventions. Complete when the existing architecture and commands are mapped.
2. Scaffold the smallest coherent application slice: app shell, data fixtures, Worker/API shell, storage abstractions, docs, and tests. Complete when one end-to-end user path works locally.
3. Keep static app code framework-light unless the repo or user explicitly chooses a heavier UI framework.
4. Add Worker routes with validation, no-store private responses, CORS/origin controls, rate-limit hooks, audit records, and dry-run provider adapters. Complete when untrusted inputs cannot directly assert authority or state.
5. Generate derived artifacts through scripts rather than hand-editing them.
6. Run focused checks first, then smoke/browser tests for user-facing or provider-backed behavior.
7. Report verified commands and production credential gaps honestly. Completion requires a working user path, operator docs, and evidence for every applicable gate.

## Quality Gates

- Accessibility: landmarks, labels, keyboard paths, focus states, reduced motion, high zoom, mobile overflow safety, and automated checks where available.
- Security: secret scans, fail-closed protected routes, input validation, CSRF/origin boundaries, rate limits, webhook signature hooks, path traversal checks, import sanitization, no raw secrets in backups, and audit logs for sensitive mutations.
- Performance: static/cacheable public pages, lazy runtime loading, bounded Worker reads/writes, small assets, no unnecessary namespace scans, and free-tier-aware storage/API design.
- SEO and i18n: apply to public surfaces; keep private, admin, and token routes out of crawlable output.
- Testing: prefer project-local commands. Typical gates include unit tests, security checks, Worker smoke, Playwright/accessibility smoke, provider dry-run evidence, and release smoke.

## Common Pitfalls

1. A successful checkout redirect is not proof of payment. Verify provider state and the application-side settlement record.
2. A generated artifact or green unit suite is not user-flow acceptance. Exercise the rendered public and operator paths.
3. Provider credentials that are unavailable do not justify fake success. Keep the adapter in dry-run mode and state the production gate.

## Verification Checklist

- [ ] The requested public and operator flows work locally.
- [ ] Worker-owned trust decisions are validated server-side.
- [ ] Applicable accessibility, security, performance, and browser checks pass.
- [ ] Provider behavior is proven live or explicitly bounded to a dry run.
- [ ] Setup, operation, failure handling, and release behavior are documented.
