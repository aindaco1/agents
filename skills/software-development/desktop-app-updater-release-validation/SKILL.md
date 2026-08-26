---
name: desktop-app-updater-release-validation
description: "Use when adding or validating a signed desktop updater."
license: "All rights reserved"
metadata:
  version: "1.0.0"
  author: "Dust Wave"
  short-description: "Validate signed desktop updater releases"
  hermes:
    tags: [desktop, updater, release, signing, acceptance]
    related_skills: [macos-dmg-release-validation]
---

# Desktop App Updater Release Validation

## Overview

Implement or verify an app-open update check and signed desktop updater path without conflating a reference application with the target project or a local candidate with a released update.

## When to Use

Use for adding a non-blocking update check at app launch, porting a proven updater policy to another desktop app, or validating a signed release/update path involving Sparkle, Tauri, an app-specific `UpdateManager`, an appcast/feed, or a previous-version installation.

Do not use it to publish, tag, delete release artifacts, or modify a different project than the active request. Do not assume one app's updater framework applies to another.

## Inputs and Context

1. Confirm the intended project path, installed version, target version, and whether the request is implementation, release preparation, or acceptance testing. Complete when the target cannot be confused with any reference app.
2. Read project docs, updater architecture, release workflow, feed handling, prior release notes, and existing tests. Complete when the established framework and documented gates are known.
3. Identify the existing abstraction: Sparkle, Tauri updater, an app-specific `UpdateManager`, or another framework. Complete when the implementation can extend rather than replace it.

## Procedure

1. Write the update-policy contract: production-launch behavior, frequency, current/offline behavior, user-visible update behavior, manual fallback, installation consent, and privacy/network constraints.
2. Adapt the existing framework. Keep the manual check available and installation user-triggered unless the user explicitly requests otherwise.
3. Add deterministic tests for the launch-check policy and reuse check/install state so launch and manual paths do not diverge.
4. Run the project's source, test, package, signing, and release gates. If an iCloud-checkout runtime/hash check times out, rerun only that check from an APFS temporary directory and report the distinction.
5. For an approved release, validate public assets, signed feed/appcast, checksums, notarization, staple, Gatekeeper/code-sign, and expected bundle/version metadata.
6. Run the real previous-version acceptance path on a safe test install: check, install, relaunch, and confirm the new version. Preserve a rollback copy when replacing an installed app.

The procedure is complete only when the applicable implementation, public artifact/feed, and previous-version acceptance gates agree. Stop release claims at the first missing gate.

## Common Pitfalls

1. Reference and target apps are conflated. Confirm the checkout before editing.
2. The launch check exists but manual/install state diverges. Reuse state and exercise both paths.
3. A signed or notarized artifact is treated as a working updater. Validate the downloaded public artifact and update/relaunch flow.
4. Green local checks are treated as publication evidence. Inspect the live feed and hosted assets.

## Verification Checklist

- [ ] Intended project and updater framework are confirmed.
- [ ] Launch policy and privacy/network behavior are explicit and tested.
- [ ] Manual update remains available and installation consent matches the request.
- [ ] Source, package, and signing gates pass, with filesystem workarounds reported.
- [ ] Public feed/appcast and artifact match the signed release.
- [ ] A previous version checks, installs, relaunches, and reports the target version.
