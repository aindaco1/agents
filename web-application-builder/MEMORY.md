# MEMORY

Marisol's reference architecture is derived from Alonso's Pool and Store projects: static-first Jekyll public sites, Cloudflare Workers for runtime/API trust boundaries, Stripe for payments, Resend for transactional email, GitHub Pages/GitHub Actions for deployment, Podman for local rehearsal, and strict accessibility/security/performance/SEO/i18n/testing gates.

Pool and Store both treat the browser as untrusted. The Worker owns validation, totals, checkout/session/order state, admin mutations, webhook handling, email dispatch, signed/private access, and provider integration.

Default web-app build preference: smallest complete implementation; static public pages where possible; serverless Worker logic for sensitive/stateful flows; config/data-driven customization; docs and tests shipped with every feature.
