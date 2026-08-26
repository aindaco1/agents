#!/usr/bin/env python3
"""Regenerate the root roster catalog from canonical profile entries."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    repo_default = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Sync roster.json from profile roster_entry.json files."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=repo_default,
        help=f"Agent repository (default: {repo_default})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report aggregate drift without writing; exit 1 when sync is needed.",
    )
    return parser.parse_args()


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to load {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return payload


def discover_profile_entries(repo: Path) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for path in sorted(repo.glob("*/roster_entry.json")):
        entry = load_json_object(path)
        role_id = entry.get("role_id")
        if not isinstance(role_id, str) or not role_id:
            raise ValueError(f"{path}: role_id must be a non-empty string")
        if role_id != path.parent.name:
            raise ValueError(
                f"{path}: role_id {role_id!r} does not match directory name"
            )
        if role_id in entries:
            raise ValueError(f"Duplicate profile role_id: {role_id}")
        entries[role_id] = entry
    if not entries:
        raise ValueError(f"{repo}: no profile roster entries found")
    return entries


def build_expected_roster(
    current: dict[str, Any], entries: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    aggregate_entries = current.get("agents")
    if not isinstance(aggregate_entries, list):
        raise ValueError("roster.json: 'agents' must be a list")

    aggregate_ids: list[str] = []
    for entry in aggregate_entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("role_id"), str):
            raise ValueError("roster.json: every agent must have a string role_id")
        aggregate_ids.append(entry["role_id"])
    if len(aggregate_ids) != len(set(aggregate_ids)):
        raise ValueError("roster.json: duplicate agent role_id")

    missing = sorted(set(entries) - set(aggregate_ids))
    stale = sorted(set(aggregate_ids) - set(entries))
    if missing or stale:
        details = []
        if missing:
            details.append("missing from aggregate: " + ", ".join(missing))
        if stale:
            details.append("missing profile directories: " + ", ".join(stale))
        raise ValueError("; ".join(details))

    expected = dict(current)
    expected["agents"] = [entries[role_id] for role_id in aggregate_ids]
    expected["total_agents"] = len(entries)
    pronouns = Counter(entry.get("pronouns") for entry in entries.values())
    expected["gender_distribution"] = {
        "he_him": pronouns.get("he/him", 0),
        "she_her": pronouns.get("she/her", 0),
        "they_them": pronouns.get("they/them", 0),
    }
    return expected


def changed_role_ids(
    current: dict[str, Any], expected: dict[str, Any]
) -> list[str]:
    current_by_id = {
        entry["role_id"]: entry for entry in current.get("agents", [])
    }
    return [
        entry["role_id"]
        for entry in expected["agents"]
        if current_by_id.get(entry["role_id"]) != entry
    ]


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    roster_path = repo / "roster.json"
    try:
        current = load_json_object(roster_path)
        entries = discover_profile_entries(repo)
        expected = build_expected_roster(current, entries)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    changed_roles = changed_role_ids(current, expected)
    metadata_changed = any(
        current.get(key) != expected.get(key)
        for key in ("total_agents", "gender_distribution")
    )
    if not changed_roles and not metadata_changed:
        print(f"roster aggregate is current ({len(entries)} profiles)")
        return 0

    summary = f"roster aggregate drift: {len(changed_roles)} profile entries"
    if metadata_changed:
        summary += " plus summary metadata"
    if args.check:
        print(summary)
        if changed_roles:
            print("changed profiles: " + ", ".join(changed_roles))
        return 1

    expected["generated"] = str(date.today())
    roster_path.write_text(
        json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"synchronized roster aggregate ({len(entries)} profiles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
