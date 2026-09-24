"""Collect canonical tests without executing iCloud conflict copies."""

import re
from pathlib import Path


# Match the portable synchronizer's conflict-copy boundary; keep real v2/02 names.
CONFLICT_COPY_RE = re.compile(r" [0-9]+\.[^.]+$")


def pytest_ignore_collect(collection_path: Path):
    if CONFLICT_COPY_RE.search(collection_path.name):
        return True
    return None
