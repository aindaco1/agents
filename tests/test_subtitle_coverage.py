"""Exercise the portable checker's public CLI without films or ASR dependencies."""
import json
from pathlib import Path
import subprocess
import sys

import pytest


CHECK = (Path(__file__).resolve().parents[1] / "skills/creative/film-subtitle-editing"
         / "scripts/check_srt.py")


def run_check(tmp_path, regions, *options):
    srt = tmp_path / "film.srt"
    srt.write_text("1\n00:00:02,000 --> 00:00:04,000\nFirst.\n\n"
                   "2\n00:00:09,000 --> 00:00:10,000\nSecond.\n", encoding="utf-8-sig")
    vad = tmp_path / "speech.json"
    vad.write_text(json.dumps(regions))
    return subprocess.run([sys.executable, str(CHECK), str(srt), "--speech-regions",
                           str(vad), *options], capture_output=True, text=True)


def test_opening_internal_and_closing_gaps(tmp_path):
    # Unsorted duplicate and overlapping spans, plus a pause inside the middle exchange.
    result = run_check(tmp_path, [[8, 12], [0, 2.4], [0, 2.4], [3.5, 5.5], [5, 6], [6.5, 7.6]])
    assert result.returncode == 0
    windows = [line for line in result.stdout.splitlines() if line.startswith("REVIEW speech")]
    assert len(windows) == 3
    assert "00:00:04,000 --> 00:00:09,000: 4.10 s" in windows[0]
    assert "00:00:00,000 --> 00:00:02,000: 2.00 s" in windows[1]
    assert "00:00:10,000 --> 00:00:12,000: 2.00 s" in windows[2]


def test_separate_short_replies_and_silence(tmp_path):
    spans = [[1.25, 2.75], [3.25, 4.75], [8.25, 10.75]]
    result = run_check(tmp_path, spans)
    assert result.returncode == 0 and "0 windows to review" in result.stdout
    result = run_check(tmp_path, spans, "--min-uncovered", ".75")
    assert result.returncode == 0 and "4 windows to review" in result.stdout
    result = run_check(tmp_path, [])
    assert result.returncode == 0 and "0 merged speech regions" in result.stdout


@pytest.mark.parametrize("bad", [None, ["1, 2"], [[1, True]], [[3, 2]], [[-1, 2]], [[0, float("nan")]]])
def test_invalid_speech_regions(tmp_path, bad):
    result = run_check(tmp_path, bad)
    assert result.returncode != 0 and "speech" in result.stderr


def test_locked_layout_errors_still_fail(tmp_path):
    source = tmp_path / "source.srt"
    source.write_text("1\n00:00:02,000 --> 00:00:04,000\n- A\n- B\n")
    result = run_check(tmp_path, [], "--locked-to", str(source))
    assert result.returncode == 1
    assert "cue count differs" in result.stdout and "speaker markers differ" in result.stdout
