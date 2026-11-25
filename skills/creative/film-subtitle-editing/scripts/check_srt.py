"""Read-only checks for edited UTF-8 SubRip subtitles."""

import argparse
from dataclasses import dataclass
from html import unescape
import json
import math
from pathlib import Path
import re
import sys

STAMP = r"[0-9]{2,}:[0-5][0-9]:[0-5][0-9],[0-9]{3}"
INTERVAL = re.compile(rf"({STAMP}) --> ({STAMP})")
MARKUP = re.compile(r"</?(?:i|b|u)>|</?font\b[^>]*>|\{\\an[1-9]\}", re.I)


def milliseconds(stamp):
    hours, minutes, seconds, millis = map(int, re.split("[:,]", stamp))
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


@dataclass
class Cue:
    number: int
    start: int
    end: int
    lines: list

    def speaker_marks(self):
        # Wrapping a single speaker may change line count in translation.
        return tuple(i for i, line in enumerate(self.lines) if line.startswith("- "))


def read_cues(path):
    content = path.read_text(encoding="utf-8-sig").strip("\n")
    if not content.strip():
        raise ValueError(f"{path}: empty file")
    cues = []
    for index, block in enumerate(re.split(r"\n[ \t]*\n(?:[ \t]*\n)*", content), 1):
        lines = block.splitlines()
        timing = INTERVAL.fullmatch(lines[1]) if len(lines) >= 3 else None
        if not timing or not re.fullmatch("[0-9]+", lines[0]):
            raise ValueError(f"{path}: malformed block {index}")
        if any(INTERVAL.fullmatch(line) for line in lines[2:]):
            raise ValueError(f"{path}: missing cue separator after block {index}")
        visible = [unescape(MARKUP.sub("", line)).strip() for line in lines[2:]]
        cues.append(Cue(int(lines[0]), *map(milliseconds, timing.groups()), visible))
    return cues


def speech_regions(path):
    """Read speech spans in seconds and merge their union in milliseconds."""
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON array of [start, end] pairs in seconds")
    spans = []
    for i, pair in enumerate(data, 1):
        if not isinstance(pair, list) or len(pair) != 2 or not all(
            type(t) in (int, float) and math.isfinite(t) for t in pair
        ):
            raise ValueError(f"{path}: speech region {i} needs two finite numbers")
        start, end = pair
        if start < 0 or end <= start:
            raise ValueError(f"{path}: invalid speech region {i} ({start}, {end})")
        spans.append((round(start * 1000), round(end * 1000)))
    merged = []
    for start, end in sorted(spans):
        if start == end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def uncovered_speech(cues, regions, minimum_ms):
    """Find nearby bursts in the same subtitle gap. Count only speech time."""
    if not regions:
        return
    gap_start = 0
    region_index = 0
    for gap_end, next_start in [(c.start, c.end) for c in cues] + [(regions[-1][1], None)]:
        while region_index < len(regions) and regions[region_index][1] <= gap_start:
            region_index += 1
        cluster = None
        j = region_index
        while j < len(regions) and regions[j][0] < gap_end:
            start = max(gap_start, regions[j][0])
            end = min(gap_end, regions[j][1])
            j += 1
            if start >= end:
                continue
            if cluster and start - cluster[1] <= 1000:
                cluster = (cluster[0], end, cluster[2] + end - start)
            else:
                if cluster and cluster[2] >= minimum_ms:
                    yield cluster
                cluster = (start, end, end - start)
        if cluster and cluster[2] >= minimum_ms:
            yield cluster
        gap_start = next_start


def timecode(ms):
    seconds, millis = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def inspect(cues, cps, locked):
    errors = []
    review = []
    if locked is not None and len(cues) != len(locked):
        errors.append(f"cue count differs from reference ({len(cues)} vs {len(locked)})")
    for index, cue in enumerate(cues):
        label = f"cue {cue.number}"
        duration = cue.end - cue.start
        if cue.number != index + 1:
            errors.append(f"{label}: expected number {index + 1}")
        if duration <= 0:
            errors.append(f"{label}: nonpositive duration")
        if index and cue.start < cues[index - 1].end:
            errors.append(f"{label}: overlap or out-of-order cue")
        if not all(cue.lines) or any("\ufffd" in line for line in cue.lines):
            errors.append(f"{label}: empty display line or replacement character")
        if locked is not None and index < len(locked):
            source = locked[index]
            if (cue.number, cue.start, cue.end) != (source.number, source.start, source.end):
                errors.append(f"{label}: cue number or timestamp differs from reference")
            if cue.speaker_marks() != source.speaker_marks():
                errors.append(f"{label}: speaker markers differ from reference")
        if len(cue.lines) > 2 or max(map(len, cue.lines)) > 42:
            review.append(f"{label}: exceeds two lines or 42 characters per line")
        if cue.speaker_marks() and (len(cue.lines) != 2 or cue.speaker_marks() != (0, 1)):
            review.append(f"{label}: check speaker dashes")
        if duration > 0:
            if duration < 833 or duration > 7000:
                review.append(f"{label}: duration {duration / 1000:.3f} s")
            speed = len(" ".join(cue.lines)) * 1000 / duration
            if speed > cps:
                review.append(f"{label}: {speed:.2f} characters/s")
    return errors, review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subtitle", type=Path)
    parser.add_argument("--cps", type=int, default=20, help="reading speed review target")
    parser.add_argument("--locked-to", type=Path, help="clean source with fixed timing and turns")
    parser.add_argument("--speech-regions", type=Path,
                        help="review subtitle gaps against a JSON array of [start, end] seconds")
    parser.add_argument("--min-uncovered", type=float, default=1.5, metavar="SECONDS",
                        help="minimum uncovered speech per review window (default: 1.5)")
    args = parser.parse_args()
    if args.cps < 1:
        parser.error("--cps must be positive")
    if not math.isfinite(args.min_uncovered) or args.min_uncovered <= 0:
        parser.error("--min-uncovered must be a positive finite duration")
    try:
        cues = read_cues(args.subtitle)
        locked = read_cues(args.locked_to) if args.locked_to else None
        regions = speech_regions(args.speech_regions) if args.speech_regions else None
    except (ValueError, OSError, OverflowError) as exc:
        print(exc, file=sys.stderr)
        return 1
    errors, review = inspect(cues, args.cps, locked)
    if regions is not None and not errors:
        candidates = sorted(uncovered_speech(cues, regions, args.min_uncovered * 1000),
                            key=lambda window: (-window[2], window[0]))
        print(f"Coverage: {len(regions)} merged speech regions, {len(candidates)} windows to review")
        for start, end, active in candidates:
            review.append(f"speech {timecode(start)} --> {timecode(end)}: "
                          f"{active / 1000:.2f} s of detected speech outside cues")
    for message in errors:
        print("ERROR", message)
    for message in review:
        print("REVIEW", message)
    print(f"{len(cues)} cues, {len(errors)} errors, {len(review)} review flags")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
