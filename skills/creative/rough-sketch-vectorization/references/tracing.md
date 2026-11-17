# Grayscale sketch tracing

Use the helper for a dark sketch on a light background. It composites transparency onto white, keeps the source dimensions, optionally erases explicitly supplied rectangles, traces nested thresholds with Potrace, and renders the resulting SVG. It does not install tools or alter the source. For colored or inverted artwork, choose a suitable separate preparation step rather than silently discarding meaningful color.

## Dependencies and execution

Use an existing suitable environment or a task-local virtual environment. Python needs Pillow and CairoSVG; Potrace must be on PATH or supplied with `--potrace`. CairoSVG also needs native Cairo. On the Mac used for the chile example, Cairo was available with `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`; this is environment-specific. Do not change global packages to work around a local Python environment problem.

```sh
python scripts/trace_sketch.py /absolute/source.png \
  --output-dir /absolute/task/outputs --name rough-sketch
```

Outputs are `rough-sketch.svg`, `rough-sketch.png`, and `rough-sketch-trace.json`. The JSON records source and output hashes, dimensions, exclusions, tones, tool version, and overlay identity. It is construction evidence, not a visual-quality verdict. Existing outputs are refused unless `--overwrite` is explicit; source and overlay inputs cannot be overwritten even with that flag.

Useful options:

- `--erase-rect x0,y0,x1,y1`, repeatable: inclusive pixel rectangles in the original image coordinates. Inspect each exclusion so labels can be removed without erasing arrows or drawing details. No rectangle is applied by default.
- `--overlay labels.svg`: trusted, self-contained SVG with the exact same zero-origin viewBox. Supply only replacement text/paths and their needed definitions. The helper refuses raster images, scripts, external references, and CSS. Use presentation attributes and inline paths or text. Typeset and outline portable lettering separately; the helper does not choose fonts or convert text to outlines.
- `--trace-scale 3` and `--png-scale 3`: interpolation and export scale. Increased scale does not recover missing detail. The source's aspect ratio remains unchanged.
- `--tones 247:240,237:229,...`: threshold and resulting gray pairs, ordered from pale to dark. Thresholds and gray values must both decrease. More levels reduce banding but increase shape count. Tune on normal-size and enlarged previews.
- `--potrace /absolute/potrace`: select an installed executable.

The defaults come from the accepted chile reconstruction: twelve nested grayscale traces, 3× interpolation, speckle size 2, corner parameter 0.85, and optimization tolerance 0.10. They are a useful first pass for that kind of soft, small source, not a mandate for every drawing. Use fewer tones for a crisp pen drawing, or adapt the helper when the source needs different thresholds or contour treatment.

## Visual acceptance

At normal size, preserve the source's balance between strong contour lines and faint, uneven hatching. In enlarged crops, verify that dark bands do not resemble bevels and that pale bands do not create broad halos or background islands. Do not remove every stray mark: some are intentional corrections that make the sketch read correctly.

Confirm meaningful features independently of tracing output: silhouette, leaf/seed counts, varied light shapes, arrow endpoints, exact words, and open spaces inside loops. A valid SVG and matching dimensions alone are insufficient.

The finished drawing is organized into tone layers of filled paths. This is scalable and shape-editable, but less convenient for moving individual lights or editing stroke widths than a semantic redraw. Choose that tradeoff explicitly when source fidelity and roughness matter most.
