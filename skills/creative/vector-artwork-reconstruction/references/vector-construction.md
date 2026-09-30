# Vector construction and export

Use the brief's typography and geometry; do not turn the Indie 50 example into a universal banknote template.

## Practical construction

- Define one logical SVG viewBox, physical size only if requested, and a target raster size. For example, 6.14 × 2.61 inches at 600 PPI gives 3684 × 1566 pixels, with viewBox 0 0 1842 783.
- Use named groups such as paper, border, field, ornaments, numerals, title, and footer. Use shared definitions or functions for repeated elements.
- FontTools TTFont/TTCollection can inspect font names and outlines. SVGPathPen plus TransformPen converts selected glyphs to paths. Flip the font's vertical axis into SVG coordinates and use actual advances. Simple character placement does not handle kerning, ligatures, or complex-script shaping; use a shaping-aware typesetter when those matter.
- Inspect a specimen of candidate fonts and ornament glyphs. A font named “Ornaments” contains drawings, not the letters used to select them.
- For guilloche, tune line count, amplitude, spacing, and opacity at the intended display size. Excessively dense curves become a dark band or moiré.
- Light hatching clipped to title outlines can suggest engraving. Maintain legibility at final size.
- Recolor scanned paper with restrained contrast while retaining its real fibers. Do not add fake camera or scanner metadata.
- Keep fonts out of distributed packages unless their license permits redistribution. Outlined lettering avoids requiring the recipient's font installation, but it is not live text.

## Optional deterministic renderer

The helper accepts trusted, self-contained SVGs with a viewBox and a single output PNG. It refuses external dependencies and will not replace an existing PNG unless --overwrite is supplied.

Dependencies: Python 3, CairoSVG, Pillow, and the native Cairo library. Use an existing suitable environment, or a task-local virtual environment. Do not assume this skill's installation contains dependencies.

Example from a suitable Python environment:

```sh
python /path/to/skill/scripts/render_svg.py artwork.svg --out artwork.png --width 3684 --dpi 600
```

--width selects raster width; height is derived from the viewBox. --dpi writes print-density metadata; it does not independently rescale the artwork. Validate the resulting physical size against the brief.

On the Mac used for the Indie 50 example, Homebrew Cairo required DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib for that command. Treat this as an environment-specific fix, not a portable requirement. A broken cffi import was resolved in the task-local virtual environment; do not change global packages reflexively.

The renderer prints raster dimensions, implied print size, source hash, and output hash. Open the rendered PNG using the runtime's image-viewing tool. It cannot judge visual quality.

## Acceptance

Check exact wording and important imagery against the source, not just generated notes. Inspect the complete frame and zoomed type/ornament. Verify SVG groups and embedded raster sources, PNG dimensions, and requested print proportions. Describe live-text versus outlined-text editability accurately.
