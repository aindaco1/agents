---
name: design-control-loop
description: Use when designing a measurable code improvement loop.
license: MIT
metadata:
  version: 1.0.0
  author: HumanLayer; adapted for Codex and Hermes
  upstream: https://github.com/humanlayer/skills/tree/ca7c8088db69e315a8b2deea43820270457f8f3c/plugins/design-control-loop/skills/design-control-loop
  upstream_commit: ca7c8088db69e315a8b2deea43820270457f8f3c
  hermes:
    tags:
    - automation
    - control-loops
    - ci
    related_skills:
    - build-iterated-agentic-loop
---

# Design Control Loop

Design and build a loop that moves a measurable property of a codebase toward a target through small, reviewable changes. Use the repository's actual tooling and constraints.

The components are: **set point** (desired state), **sensor** (measurement), **controller** (selection of the next increment), **actuator** (Codex or Hermes applying it), and **disturbances** (other changes to the repo). Explain only the concepts useful to the discussion. Read [the taxonomy](references/control-loop-taxonomy.md) when framing the design and [the example](references/example-control-loop.md) when a concrete illustration helps.

## Discover, then design

Read the instructions, package manifests, CI, tests/static analysis, existing agent skills, golden code patterns, and recent relevant changes. Establish install and validation commands before proposing new tools.

Resolve these decisions from the request and repo, asking concise questions only where needed:

1. What property and writable scope are being improved? Is the set point an invariant, threshold, or downward trend?
2. What measures it repeatably? Prefer a useful existing command over a new subsystem. Discuss cost, false positives, and whether changes can game the metric.
3. What selects one reviewable increment? Set a batch limit, prioritization, skip/no-op conditions, and how feedback changes future selection. Selection can be deterministic, agentic, or fused with another component.
4. What transformation is permitted? Choose Codex or Hermes, established code patterns, and the validation that proves improvement without regressions.
5. What disturbances matter? Consider an optional regression gate comparing the measurement to a baseline; do not add one merely to fill the model.

Record a short design in the repo's existing documentation location: metric and baseline, target, scope, sensor command/output, selection rule, actuator skill, validation, feedback, and stopping conditions. Preserve explicit user choices; do not require a new approval round for decisions already authorized.

## Make the components work locally

Implement only the separation the design needs. Each distinct sensor/controller should be version-controlled and independently runnable:

- Run the sensor on the real repo; inspect actual output and a no-findings/error case.
- Run the controller on that output; confirm the target is eligible and the batch bound holds.
- Apply one selected change in an isolated checkout, validate it, and remeasure. Use the current agent or an authorized runtime invocation; this skill does not require spawning additional agents.
- Preserve the metric definition. Suppressing checks or moving failures outside the measurement is not improvement unless explicitly part of the agreed contract.

If credentials or authorization prevent the actuator trial, finish the independently testable components and report that specific gap. Do not represent an unexecuted trial as success.

## Connect the recurring workflow

Load the installed `build-iterated-agentic-loop` skill for the shared Codex/Hermes runtime, skill/prompt/memory templates, PR bounds, optional `/iterate`, and activation checks. This is the companion package maintained with this skill; do not duplicate its CI machinery here. If unavailable, locate its canonical package or report the missing dependency before wiring CI.

Feed sensor results and controller selection into the actuator prompt. Load standing feedback before selection when it affects eligibility, and into the actuator when it affects transformations. Keep the workflow a thin orchestrator of locally runnable parts. Use the repo's CI platform; translate the companion GitHub template only if that is the chosen platform.

Default to one open PR and manual dispatch until cadence is specified. Feed reviewed outcomes back into selection and skill guidance. Increase batch size or cadence only on evidence that the loop produces useful, validated changes at a sustainable review rate.

Report the written design, local commands/results, before/after measurement, and workflow status separately. A locally validated loop is not proof of a live CI run or a reviewed PR.
