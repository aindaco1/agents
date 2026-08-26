---
name: macos-dmg-release-validation
description: "Use when hardening or validating a macOS DMG release."
license: "All rights reserved"
metadata:
  version: "1.0.0"
  author: "Dust Wave"
  short-description: "Harden and validate macOS DMG releases"
  hermes:
    tags: [macos, dmg, release, notarization, installer]
    related_skills: [desktop-app-updater-release-validation]
---

# macOS DMG Release Validation

## Overview

Harden and validate a macOS application DMG, including its install affordance, mounted-image contract, signing/notarization evidence, bounded cleanup, and local smoke behavior.

## When to Use

Use for a user-approved macOS release, DMG installer improvement, or signed prerelease smoke test involving installer UX, signing/notarization, tag/release validation, or app-level testing of a published DMG.

Do not use it to publish, tag, merge, delete branches, or replace an installed application without authorization. Do not add an installer dependency solely for drag-to-Applications UX when the existing DMG can be improved and verified natively.

## Inputs and Context

1. Read packaging/release scripts, CI, and the release runbook. Complete when the app bundle name, branch/tag, architecture, and artifact naming contract are known.
2. Inspect the current DMG before designing changes. Complete when its existing app bundle, `/Applications` shortcut, and layout defects are observed directly.
3. Establish whether the request is hardening, release preparation, deployment, or local prerelease QA. Preserve unrelated worktree edits.

## Procedure

1. Prefer a conventional native layout: a top-level app bundle plus `/Applications` shortcut. Keep layout expectations in one shared contract.
2. Add or maintain a fail-closed validator that mounts the image read-only and checks layout, app bundle, signature/notarization, architecture, and project-specific metadata as applicable. Exercise it with a fixture when practical.
3. Run the documented test, build, and release checks, including the mounted-DMG validator before any tag.
4. If merge, tag, or deployment is explicitly approved, verify post-merge main-branch CI before tagging. Record the commit, workflow, artifact checksum, and validation result.
5. Clean only generated artifacts, `.DS_Store`, or branches proven stale or merged and without an open PR.
6. For local prerelease smoke, use the published signed DMG, preserve the installed app as an explicit rollback copy, install the candidate into Applications, and exercise the affected high-risk workflows.

The procedure is complete only when package layout, mounted-image validation, release evidence, and applicable app-level smoke behavior agree.

## Common Pitfalls

1. Valid package, poor installer UX: add and test the `/Applications` shortcut before adopting another packaging dependency.
2. Green CI, broken local workflow: treat the local result as a release blocker or follow-up and identify whether the published artifact includes the fix.
3. Cleanup risks user work: delete only targets proven stale, merged, generated, and recoverable where practical.
4. A local DMG is treated as the public artifact: download and inspect the hosted release candidate separately.

## Verification Checklist

- [ ] DMG has the expected app bundle and `/Applications` affordance.
- [ ] Mounted-image validation covers layout and applicable signing, notarization, architecture, metadata, and checksum gates.
- [ ] Project test/build/release checks pass, and required post-merge CI is green before tagging.
- [ ] Cleanup is limited to verified stale or generated targets.
- [ ] Local smoke preserves rollback and exercises the affected user workflow.
- [ ] Any regression records the exact artifact, environment, symptom, and published-versus-branch status.
