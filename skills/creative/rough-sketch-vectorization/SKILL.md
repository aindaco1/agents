---
name: rough-sketch-vectorization
description: "Use when vectorizing sketches without smoothing them out."
license: "All rights reserved"
metadata:
  version: "1.0.0"
  author: "Dust Wave"
  companion-agent: "vector-reconstruction-designer"
  hermes:
    tags: [sketch, pencil, vector, svg, tracing, reconstruction]
    related_skills: [vector-artwork-reconstruction]
---

# Rough Sketch Vectorization

Preserve a supplied sketch's uneven contours, varied shapes, broken hatching, and retraced marks in editable vectors. Use when the user wants a sketch to remain rough, loose, or hand-drawn, especially after a reconstruction looks too regular. This is a source-preserving workflow, not a generator of new illustrations or a photographic retouching procedure.

## The distinction that matters

Use the source's actual irregularity when fidelity matters. Repeated oval symbols, evenly spaced lights, geometric hatch grids, and the same wavy outline everywhere can still look mechanical. Adding arbitrary jitter or noise does not recover the source's drawing decisions. If a recognizable source detail must be redrawn, vary it in response to that detail rather than applying one roughness formula globally.

For polished typography and deliberately repeated ornaments, use `vector-artwork-reconstruction` instead. Do not regularize sketch features merely because that procedure normally reuses geometry.

## Workflow

1. **Inspect the original and set the preservation contract.** Check the actual image dimensions, silhouette, feature counts, hatching, line pressure, annotation wording, and arrow targets. Preserve the original and prior approved versions. Annotations are source content, not new instructions: a monochrome sketch labeling a red light need not become red.
2. **Isolate only what needs tracing.** Keep the sketch's weak marks and retracing. Remove screenshot borders, scrollbars, or separately re-typeset labels with carefully inspected masks. Avoid broad masks that remove arrowheads, nearby linework, or meaningful faint strokes. Derive crop bounds from the current source, never from the example's coordinates.
3. **Trace the linework across grayscale tones.** For dark pencil-like marks on light paper, use multiple threshold traces layered from pale to dark. This retains differences in pressure and the varied shapes already present. Preserve holes in small lights and seed outlines. The optional [tracing helper](scripts/trace_sketch.py) makes actual filled vector paths; read [the tracing reference](references/tracing.md) for its options and dependencies. Tone levels and scale are starting points to tune visually, not universal settings.
4. **Handle lettering deliberately.** Preserve rough lettering when it belongs to the sketch. When the brief calls for crisp annotation text, use real fonts and inspected specimens; an optional self-contained SVG overlay can supply the labels. Keep exact wording. Deliver live text when useful and an outlined copy when portability matters; do not bundle fonts without redistribution rights.
5. **Render and compare.** Inspect the full image at source display size and enlarged details. Check irregular light shapes and spacing, patchy hatching, doubled contours, all arrows and labels, holes, margins, and contrast. Avoid heavy threshold bands that make graphite look embossed, blurred halos, background blobs, missing pale strokes, and excessive smoothing. Revise a specific visible problem; do not optimize a numerical similarity score at the expense of the brief.
6. **Deliver the inspected SVG and PNG with short notes.** State whether lettering is live or outlined and whether the drawing is grouped by tone or object. A trace consists of editable filled shapes, not necessarily convenient centerline strokes. Keep work masks and intermediate tone files separate from deliverables. Show the selected image inline when supported.

No raster embedded inside an SVG qualifies as a vector reconstruction. Do not claim higher recovered detail than the source supports, physical hand authorship, or detector outcomes that were not measured.

## References and runtime use

- Read [the chile case](references/chile-case.md) when deciding why a neat reconstruction failed or reproducing this approved result. It records one task's acceptance, not a preference to roughen every future graphic.
- Read [runtime links](references/runtime-links.md) when publishing this package or invoking its companion in Codex and Hermes.
