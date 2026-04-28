#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: save_latest_generated_avatar.py /abs/path/to/avatar.webp", file=sys.stderr)
        return 2

    out = Path(sys.argv[1]).expanduser().resolve()
    root = Path("/Users/aindaco1/.codex/generated_images")

    try:
        latest = max(root.rglob("*.png"), key=lambda p: p.stat().st_mtime)
    except ValueError:
        print("no generated images found", file=sys.stderr)
        return 1

    tmp = out.with_suffix(".tmp.webp")
    subprocess.run(
        ["/opt/homebrew/bin/magick", str(latest), "-quality", "90", str(tmp)],
        check=True,
    )
    tmp.replace(out)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
