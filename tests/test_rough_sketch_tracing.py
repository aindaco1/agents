"""Observable export and input-preservation checks for the optional helper."""
import importlib.util
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/creative/rough-sketch-vectorization/scripts/trace_sketch.py'
spec = importlib.util.spec_from_file_location('rough_sketch_trace', SCRIPT)
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)


def test_real_trace_preserves_drawing_and_refuses_overwrite(tmp_path):
    if not shutil.which('potrace'):
        pytest.skip('Optional native Potrace is not installed')
    pytest.importorskip('PIL')
    try:
        pytest.importorskip('cairosvg')
    except OSError:
        pytest.skip('Optional native Cairo is unavailable')
    from PIL import Image, ImageDraw, ImageChops, ImageStat
    source = tmp_path / 'source.png'
    im = Image.new('RGB', (90, 140), 'white')
    d = ImageDraw.Draw(im)
    d.line([(20, 18), (24, 40), (21, 58), (30, 89), (56, 117)], fill='#666666', width=2)
    d.ellipse((39, 34, 57, 65), outline='#333333', width=2)
    d.line([(31, 81), (45, 61), (42, 86)], fill='#bbbbbb', width=1)
    im.save(source)
    before = source.read_bytes()
    out = tmp_path / 'export'
    args = [str(source), '--output-dir', str(out)]
    assert trace.main(args) == 0
    assert source.read_bytes() == before
    svg = ET.parse(out / 'rough-sketch.svg').getroot()
    assert svg.get('viewBox') == '0 0 90 140'
    assert not svg.findall(f'.//{{{trace.SVG}}}image')
    rendered = Image.open(out / 'rough-sketch.png').convert('RGB')
    assert rendered.size == (270, 420)
    restored = rendered.resize(im.size, Image.Resampling.LANCZOS)
    assert max(ImageStat.Stat(ImageChops.difference(im, restored)).mean) < 6
    assert min(restored.getpixel((48, 49))) > 245  # Ring hole stays open.
    artifacts = {p: p.read_bytes() for p in out.iterdir()}
    with pytest.raises(SystemExit):
        trace.main(args)
    assert all(p.read_bytes() == content for p, content in artifacts.items())
    with pytest.raises(SystemExit):
        trace.main([str(source), '--output-dir', str(tmp_path), '--name', 'source', '--overwrite'])
    assert source.read_bytes() == before


@pytest.mark.parametrize('content', [
    '<image href="https://example.invalid/image.png"/>',
    '<use href="file:///private/image.svg#x"/>',
    '<path fill="url(https://example.invalid/paint)"/>',
    '<style>path { fill: url(https://example.invalid/paint); }</style>',
    '<g onload="alert(1)"/>',
])
def test_overlay_rejects_active_external_or_raster_content(tmp_path, content):
    overlay = tmp_path / 'overlay.svg'
    overlay.write_text(f'<svg xmlns="{trace.SVG}" viewBox="0 0 90 140">{content}</svg>')
    with pytest.raises(ValueError):
        trace.overlay_root(overlay, 90, 140)


def test_overlay_preserves_local_vector_content_and_canvas(tmp_path):
    overlay = tmp_path / 'labels.svg'
    overlay.write_text(f'<svg xmlns="{trace.SVG}" viewBox="0 0 90 140">'
                      '<text x="12" y="20">Exact wording</text></svg>')
    root, _ = trace.overlay_root(overlay, 90, 140)
    assert root.find(f'{{{trace.SVG}}}text').text == 'Exact wording'
    with pytest.raises(ValueError):
        trace.overlay_root(overlay, 140, 90)
