"""Read-only checks for edited UTF-8 SubRip subtitles."""

import argparse
from dataclasses import dataclass
from html import unescape
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
    args = parser.parse_args()
    if args.cps < 1:
        parser.error("--cps must be positive")
    try:
        cues = read_cues(args.subtitle)
        locked = read_cues(args.locked_to) if args.locked_to else None
    except (ValueError, OSError) as exc:
        print(exc, file=sys.stderr)
        return 1
    errors, review = inspect(cues, args.cps, locked)
    for message in errors:
        print("ERROR", message)
    for message in review:
        print("REVIEW", message)
    print(f"{len(cues)} cues, {len(errors)} errors, {len(review)} review flags")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
