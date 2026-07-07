# MEMORY

Inez's reference architecture is derived from Alonso's ascii-vj-remix and social desktop projects: Tauri v2, Rust command backends, Vite frontends, narrow capabilities, restrictive CSP, local-first data handling, sidecar governance, GitHub Actions release workflows, macOS Developer ID signing/notarization, Windows signing planning, updater artifacts, and strict desktop test/release gates.

ascii-vj-remix emphasizes local creative desktop tooling: offline bundles, native media/audio/output, GPU/frame-pacing performance, FFmpeg sidecars, production-only sanitized crash reports, signed updater artifacts, and fail-closed macOS public release signing.

Dust Wave Social emphasizes provider/account desktop risk: social credentials, local account data, media, scheduled publishing, backups/restores, support exports, product-abuse review, macOS signing, optional media sidecars, and clear release checklists.

Default desktop build preference: Tauri/Rust + Vite; local-first; minimal webview authority; Rust-side validation; explicit signing/updater/sidecar/privacy posture; docs and tests shipped with every feature.
