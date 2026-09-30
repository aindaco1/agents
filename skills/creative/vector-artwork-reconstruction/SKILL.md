---
name: vector-artwork-reconstruction
description: "Use when rebuilding AI graphics as editable vector artwork."
license: "All rights reserved"
metadata:
  version: "1.0.0"
  author: "Dust Wave"
  short-description: "Reconstruct graphics with type, vectors, and sourced textures"
  companion-agent: "vector-reconstruction-designer"
  hermes:
    tags: [graphic-design, vector, svg, typography, reconstruction, image-detectors]
    related_skills: []
---

# Vector Artwork Reconstruction

Rebuild a supplied graphic using actual fonts, deliberate vector geometry, and documented raster assets. Preserve the design's purpose and visual character while replacing inconsistent generated details. Deliver an editable master and an inspected raster export.

## When to Use

Use for posters, labels, decorative notes, badges, title cards, and other graphics dominated by lettering, borders, ornament, or flat composition. Also use when a user wants such a graphic to look less generated or wants to evaluate its AI-image-detector classification through a conventional rebuild.

This workflow is not a substitute for photographic retouching, portrait reconstruction, or a fresh image-generation request. Do not promise that a reconstruction will be undetectable or claim it was made without AI assistance.

## Reconstruction workflow

1. **Inspect the actual reference.** Record exact wording, repeated elements, proportions, hierarchy, palette, and essential imagery. Decide what can be rebuilt as vectors and what needs a real raster source. Preserve the original file. An intentional graphic or collage should not silently disappear merely because it is hard to reconstruct.
2. **Set the composition contract.** Preserve approved wording and identity. Reflow for a changed aspect ratio instead of stretching. Derive physical dimensions and pixel dimensions from one ratio. Treat print size as a requested constraint, not a default for all graphics.
3. **Typeset and redraw.** Use real installed or properly sourced fonts. Inspect a specimen before choosing a substitute. Build repeated motifs once and reuse their geometry. Use a restrained stroke-weight system and named SVG groups. Small optical corrections are appropriate; indiscriminate imperfection or noise is not a substitute for design.
4. **Replace raster layers deliberately.** Use documented photographs, scans, or illustrations when needed. Check the source page, authorship, license, and capture history; an asset labeled “paper texture” or CC0 may itself be AI-generated. Record the actual license wording. Crop, recolor, and reduce contrast to fit the design without inventing a physical provenance.
5. **Keep the master maintainable.** Embed approved raster assets or package relative dependencies. Keep live type when practical; outline a portable copy to prevent missing-font substitutions. If the only master has outlined lettering, call it shape-editable and state that wording changes require re-typesetting. Preserve source wording and font choices in the construction notes.
6. **Render, inspect, refine.** Inspect both a normal-size preview and detail crops. Check exact text, corner consistency, clipping, margins, moiré, aliasing, and thin strokes. Compare against the original brief. Make a targeted visual revision when needed; passing an XML or dimension check does not prove visual quality.
7. **Deliver.** Supply the editable master, final PNG, and short source/construction notes. Show the image inline when supported. Keep work files separate from user-facing outputs. State material visual changes, editability limits, and any unverified detector outcome.

When using programmatic SVG construction, read [the implementation reference](references/vector-construction.md). The optional [render helper](scripts/render_svg.py) exports an inspected, self-contained SVG to PNG and reports dimensions and hashes.

## Optional detector evaluation

Only run this branch when detector evaluation is part of the user's request.

- Use the requested service and the current task's authorized image. Capture a baseline and the chosen final export if access allows.
- Record the exact submitted file/hash, service, date, label, and score only when actually returned. Keep a screenshot or other response evidence where possible.
- A user saying “that worked” is useful acceptance, but it is not an independently recorded detector score. Describe it as user-reported success.
- If uploads, authentication, or service access are blocked, complete the artwork and report the specific testing limitation. Do not route around a denied tool boundary.
- A changed score on one file or service does not establish universal non-detection or human-only authorship. Metadata removal alone is not evidence of a successful reconstruction.
- Do not iterate indefinitely against a score. After a baseline and final check, make further variants only for a concrete visual issue or an explicitly requested bounded comparison. Keep visual quality and the preservation contract intact.

For the successful Indie 50 example and its evidence limits, read [the case study](references/indie-fifty.md).

## Codex and Hermes

The companion persona is `vector-reconstruction-designer`. Both runtimes use this same procedure package; keep the detailed workflow here rather than copying it into the persona. For canonical paths and update commands, read [runtime links](references/runtime-links.md).
