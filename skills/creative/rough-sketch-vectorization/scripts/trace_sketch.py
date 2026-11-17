#!/usr/bin/env python3
"""Trace source pencil marks into nested grayscale vector paths and a PNG."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
INK = 'http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('', SVG)
ET.register_namespace('inkscape', INK)
DEFAULT_TONES = '247:240,237:229,224:216,210:201,195:185,178:168,160:149,140:128,118:106,95:82,72:59,49:36'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_tones(value):
    try:
        tones = [tuple(int(v) for v in item.split(':')) for item in value.split(',')]
        if not tones or any(len(p) != 2 or not all(0 <= n <= 255 for n in p) for p in tones):
            raise ValueError
        if any(a[0] <= b[0] or a[1] <= b[1] for a, b in zip(tones, tones[1:])):
            raise ValueError
        return tones
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Use decreasing threshold:gray pairs from 0 through 255.') from exc


def rectangle(value):
    try:
        box = tuple(int(v) for v in value.split(','))
        if len(box) != 4 or min(box) < 0 or box[0] > box[2] or box[1] > box[3]:
            raise ValueError
        return box
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Use x0,y0,x1,y1 with nonnegative inclusive pixel coordinates.') from exc


def overlay_root(path, width, height):
    raw = path.read_bytes()
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise ValueError('Overlay must not contain a DTD or entity declarations.')
    root = ET.fromstring(raw)
    if root.tag != f'{{{SVG}}}svg':
        raise ValueError('Overlay must be an SVG document.')
    try:
        view = [float(v) for v in root.get('viewBox', '').replace(',', ' ').split()]
    except ValueError as exc:
        raise ValueError('Overlay needs a numeric viewBox.') from exc
    if view != [0, 0, width, height]:
        raise ValueError(f'Overlay viewBox must be exactly 0 0 {width} {height}.')
    for el in root.iter():
        name = el.tag.rsplit('}', 1)[-1].lower()
        if name in {'image', 'script', 'foreignobject', 'style', 'animate', 'set'}:
            raise ValueError(f'Overlay element is not supported: {name}.')
        for key, val in el.attrib.items():
            local = key.rsplit('}', 1)[-1].lower()
            if local.startswith('on') or local in {'style', 'base'}:
                raise ValueError('Use passive SVG presentation attributes without CSS or base URLs.')
            if local == 'href' and not val.startswith('#'):
                raise ValueError('Overlay references must be local fragments.')
            if 'url(' in val.lower():
                # Only local fragment paint/clip/filter references are allowed.
                import re
                stripped = re.sub(r'url\(\s*[\"\']?#[\w:.-]+[\"\']?\s*\)', '', val, flags=re.I)
                if 'url(' in stripped.lower():
                    raise ValueError('Overlay URL references must be local fragments.')
    return root, digest(raw)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--name', default='rough-sketch')
    parser.add_argument('--erase-rect', type=rectangle, action='append', default=[])
    parser.add_argument('--overlay', type=Path)
    parser.add_argument('--tones', type=parse_tones, default=parse_tones(DEFAULT_TONES))
    parser.add_argument('--trace-scale', type=int, choices=range(1, 7), default=3)
    parser.add_argument('--png-scale', type=int, choices=range(1, 7), default=3)
    parser.add_argument('--potrace', default='potrace')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args(argv)
    try:
        from PIL import Image, ImageDraw, ImageOps
        import cairosvg
    except (ImportError, OSError) as exc:
        parser.error(f'Install Pillow/CairoSVG and native Cairo in a suitable environment: {exc}')
    executable = shutil.which(args.potrace)
    if not executable:
        parser.error('Potrace is unavailable. Install it separately or pass --potrace /absolute/path.')
    if args.name in {'', '.', '..'} or Path(args.name).name != args.name or '\\' in args.name:
        parser.error('--name must be a single nonempty filename stem.')
    source = args.source.expanduser().resolve()
    out = args.output_dir.expanduser().resolve()
    names = [f'{args.name}.svg', f'{args.name}.png', f'{args.name}-trace.json']
    inputs = {source}
    if args.overlay:
        inputs.add(args.overlay.expanduser().resolve())
    for name in names:
        target = out / name
        if target.resolve() in inputs:
            parser.error('An output would overwrite an input file.')
        if target.is_symlink() or (target.exists() and (not args.overwrite or not target.is_file())):
            parser.error(f'Refusing existing output: {target}. Use --overwrite for ordinary output files.')

    original = source.read_bytes()
    with Image.open(source) as source_image:
        rgba = source_image.convert('RGBA')
    width, height = rgba.size
    paper = Image.new('RGBA', rgba.size, 'white')
    paper.alpha_composite(rgba)
    gray = ImageOps.grayscale(paper.convert('RGB'))
    draw = ImageDraw.Draw(gray)
    for box in args.erase_rect:
        if box[2] >= width or box[3] >= height:
            parser.error(f'Exclusion {box} exceeds the {width} × {height} source.')
        draw.rectangle(box, fill=255)
    overlay, overlay_hash = (None, None)
    if args.overlay:
        overlay, overlay_hash = overlay_root(args.overlay.expanduser().resolve(), width, height)
    high = gray.resize((width * args.trace_scale, height * args.trace_scale), Image.Resampling.LANCZOS)
    svg = ET.Element(f'{{{SVG}}}svg', {'width': str(width), 'height': str(height),
        'viewBox': f'0 0 {width} {height}', 'role': 'img', 'aria-labelledby': 'rough-sketch-title'})
    ET.SubElement(svg, f'{{{SVG}}}title', {'id': 'rough-sketch-title'}).text = 'Source-preserving rough sketch vector reconstruction'
    ET.SubElement(svg, f'{{{SVG}}}rect', {'width': str(width), 'height': str(height), 'fill': 'white'})
    counts = []
    with tempfile.TemporaryDirectory(prefix='rough-sketch-') as folder:
        work = Path(folder)
        for threshold, tone in args.tones:
            bitmap, traced_file = work / 'threshold.pbm', work / 'threshold.svg'
            high.point(lambda x: 0 if x < threshold else 255).convert('1').save(bitmap)
            subprocess.run([executable, str(bitmap), '--svg', '--output', str(traced_file),
                '--turdsize', '2', '--alphamax', '0.85', '--opttolerance', '0.10', '--unit', '10'],
                check=True, capture_output=True, timeout=120)
            traced = ET.parse(traced_file).getroot()
            layer = ET.SubElement(svg, f'{{{SVG}}}g', {'id': f'rough-sketch-tone-{threshold}',
                f'{{{INK}}}groupmode': 'layer', f'{{{INK}}}label': f'Graphite gray {tone}',
                'transform': f'scale({1 / args.trace_scale:.10f})'})
            for child in traced:
                if child.tag.rsplit('}', 1)[-1] == 'metadata':
                    continue
                child = deepcopy(child)
                for el in child.iter():
                    if 'fill' in el.attrib and el.get('fill') != 'none':
                        el.set('fill', f'#{tone:02x}{tone:02x}{tone:02x}')
                layer.append(child)
            counts.append({'threshold': threshold, 'gray': tone,
                           'paths': len(layer.findall(f'.//{{{SVG}}}path'))})
        if overlay is not None:
            overlay.set('width', str(width))
            overlay.set('height', str(height))
            svg.append(overlay)
        vector = ET.tostring(svg, encoding='utf-8', xml_declaration=True)
        png_width, png_height = width * args.png_scale, height * args.png_scale
        png = cairosvg.svg2png(bytestring=vector, output_width=png_width, output_height=png_height)
        report = {'source': str(source), 'source_sha256': digest(original),
            'source_dimensions': [width, height], 'png_dimensions': [png_width, png_height],
            'erase_rectangles': args.erase_rect, 'trace_scale': args.trace_scale, 'tones': counts,
            'overlay_sha256': overlay_hash, 'potrace_version': subprocess.run([executable, '--version'],
                capture_output=True, text=True, check=True, timeout=10).stdout.strip(),
            'output_sha256': {names[0]: digest(vector), names[1]: digest(png)}}
        # Stage all results before publishing. No partial export on a trace/render error.
        payloads = [vector, png, (json.dumps(report, indent=2) + '\n').encode()]
        if source.read_bytes() != original:
            raise ValueError('Source changed during tracing; rerun against a stable input.')
        out.mkdir(parents=True, exist_ok=True)
        for name, data in zip(names, payloads):
            target = out / name
            with target.open('wb' if args.overwrite else 'xb') as handle:
                handle.write(data)
    print(json.dumps({'svg': str(out / names[0]), 'png': str(out / names[1]),
                      'notes': str(out / names[2]), 'paths': sum(p['paths'] for p in counts)}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ET.ParseError, subprocess.SubprocessError) as exc:
        raise SystemExit(str(exc))
