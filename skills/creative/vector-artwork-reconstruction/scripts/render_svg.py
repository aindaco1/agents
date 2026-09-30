#!/usr/bin/env python3
"""Render a trusted self-contained SVG to PNG and report verifiable export details."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET


def positive_int(value: str) -> int:
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return result


def positive_float(value: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError("must be finite and positive")
    return result


def inspect_svg(data: bytes) -> tuple[float, float]:
    root = ET.fromstring(data)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("input must have an SVG root element")
    box = [float(v) for v in re.split(r"[\s,]+", root.attrib.get("viewBox", "").strip())]
    if len(box) != 4 or not all(math.isfinite(v) for v in box) or min(box[2:]) <= 0:
        raise ValueError("a finite viewBox with positive width and height is required")
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] in {"script", "foreignObject"}:
            raise ValueError("script and foreignObject elements are unsupported")
        for key, value in element.attrib.items():
            if key.rsplit("}", 1)[-1] in {"href", "src"}:
                if not value.startswith(("#", "data:image/")):
                    raise ValueError("embed raster images; external references are unsupported")
        css = " ".join(element.attrib.values()) + " " + (element.text or "")
        if "@import" in css:
            raise ValueError("external CSS imports are unsupported")
        for ref in re.findall(r"url\(\s*['\"]?(.*?)['\"]?\s*\)", css):
            if not ref.startswith(("#", "data:image/")):
                raise ValueError("external CSS references are unsupported")
    return box[2], box[3]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--width", type=positive_int, required=True)
    parser.add_argument("--dpi", type=positive_float, default=300.0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    source, destination = args.svg.expanduser().resolve(), args.out.expanduser().resolve()
    if destination == source:
        parser.error("output must not replace the SVG source")
    if destination.suffix.lower() != ".png":
        parser.error("--out must end in .png")
    if destination.exists() and not args.overwrite:
        parser.error("output exists; choose a new filename or explicitly use --overwrite")
    try:
        data = source.read_bytes()
    except OSError as exc:
        parser.error(f"cannot read SVG source: {exc}")
    try:
        width, height = inspect_svg(data)
    except (ValueError, ET.ParseError) as exc:
        parser.error(str(exc))
    try:
        import cairosvg
        from PIL import Image
    except (ImportError, OSError) as exc:
        parser.error(f"CairoSVG, Pillow, and native Cairo are required: {exc}")
    pixels_y = max(1, round(args.width * height / width))
    rendered = cairosvg.svg2png(bytestring=data, output_width=args.width, output_height=pixels_y)
    with Image.open(io.BytesIO(rendered)) as result:
        result.load()
        if result.mode == "RGBA" and result.getchannel("A").getextrema() == (255, 255):
            result = result.convert("RGB")
        buffer = io.BytesIO()
        result.save(buffer, format="PNG", dpi=(args.dpi, args.dpi), optimize=True)
        png = buffer.getvalue()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb" if args.overwrite else "xb") as handle:
        handle.write(png)
    print(json.dumps({
        "source": str(source),
        "output": str(destination),
        "pixels": [args.width, pixels_y],
        "dpi": args.dpi,
        "implied_inches": [args.width / args.dpi, pixels_y / args.dpi],
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "output_sha256": hashlib.sha256(png).hexdigest(),
        "visual_review": "required",
        "detector_result": "not_measured"
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
