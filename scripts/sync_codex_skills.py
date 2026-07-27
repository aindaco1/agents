#!/usr/bin/env python3
"""Mirror Hermes agent profiles into Codex-compatible skills.

The source repository remains authoritative. Existing generated mirrors keep
their frontmatter so hand-tuned trigger descriptions are not churned. Skills
that do not carry the generated-mirror markers are treated as intentional name
collisions and skipped unless explicitly selected with --replace-collision.
Third-party skills in the destination are never deleted.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\n(?P<yaml>.*?)\n---\n?", re.DOTALL)
MIRROR_MARKERS = ("## Quick Reference", "## Full Identity")


def parse_args() -> argparse.Namespace:
    repo_default = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Mirror roster agent profiles into ~/.agents/skills."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=repo_default,
        help=f"Agent repository (default: {repo_default})",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path.home() / ".agents" / "skills",
        help="Codex skill directory (default: ~/.agents/skills)",
    )
    parser.add_argument(
        "--replace-collision",
        action="append",
        default=[],
        metavar="ROLE_ID",
        help="Replace one non-mirror skill that shares an agent role ID; repeatable.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report drift without writing. Exit 1 when changes are needed.",
    )
    return parser.parse_args()


def load_roster(repo: Path) -> list[dict[str, Any]]:
    roster_path = repo / "roster.json"
    try:
        payload = json.loads(roster_path.read_text(encoding="utf-8"))
        entries = payload["agents"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise SystemExit(f"Unable to load {roster_path}: {exc}") from exc
    if not isinstance(entries, list):
        raise SystemExit(f"{roster_path}: 'agents' must be a list")
    return entries


def sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith((".", "!", "?")) else f"{text}."


def yaml_single_quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def build_description(entry: dict[str, Any]) -> str:
    role_name = entry["role_name"]
    role_phrase = role_name.lower()
    role_alias = entry["role_id"].replace("-", " ")
    mentions = [role_phrase]
    if role_alias != role_phrase:
        mentions.append(role_alias)

    for skill in entry.get("skills", []):
        if ":" not in skill:
            continue
        topic = skill.split(":", 1)[0].strip().lower()
        if 2 <= len(topic.split()) <= 8 and topic not in mentions:
            mentions.append(topic)
        if len(mentions) >= 7:
            break

    quoted = ", ".join(f'"{item}"' for item in mentions)
    description = (
        f"{role_name}: {sentence(entry['tagline'])} "
        f"Use when the user mentions {quoted}, or asks for help acting as "
        f"a {role_phrase}."
    )
    avoid_for = entry.get("avoid_for") or []
    if avoid_for:
        description += f" Avoid for: {sentence(avoid_for[0])}"
    return description


def strip_first_heading(markdown: str) -> str:
    return re.sub(r"^#[^\n]*\n+", "", markdown.strip(), count=1).strip()


def build_body(repo: Path, entry: dict[str, Any]) -> str:
    role_id = entry["role_id"]
    profile_dir = repo / role_id
    summary_path = profile_dir / "IDENTITY_SUMMARY.md"
    identity_path = profile_dir / "IDENTITY.md"
    missing = [path for path in (summary_path, identity_path) if not path.is_file()]
    if missing:
        missing_text = ", ".join(str(path) for path in missing)
        raise SystemExit(f"{role_id}: missing required profile files: {missing_text}")

    summary = summary_path.read_text(encoding="utf-8").strip()
    identity = strip_first_heading(identity_path.read_text(encoding="utf-8"))
    title = (
        f"# {entry['display_name']} — {entry['role_name']} {entry['emoji']}"
    )
    sections = [
        title,
        "## Quick Reference",
        summary,
        "## Full Identity",
        identity,
    ]

    delegates = (entry.get("handoff_rules") or {}).get("delegate_to") or []
    if delegates:
        handoffs = "\n".join(
            f"- **{item['role_id']}** — {item['when']}" for item in delegates
        )
        sections.extend(("## Handoffs", handoffs))

    return "\n\n".join(sections) + "\n"


def build_frontmatter(entry: dict[str, Any]) -> str:
    description = build_description(entry)
    return (
        "---\n"
        f"name: {entry['role_id']}\n"
        f"description: {yaml_single_quote(description)}\n"
        "---\n"
    )


def default_openai_yaml(entry: dict[str, Any]) -> str:
    role_id = entry["role_id"]
    short_description = f"Work as the {entry['role_name']} profile"
    if len(short_description) > 64:
        short_description = f"Use the {entry['role_name']} specialist profile"
    prompt = f"Use ${role_id} to help with this task."
    return (
        "interface:\n"
        f'  display_name: "{entry["role_name"]}"\n'
        f'  short_description: "{short_description}"\n'
        f'  default_prompt: "{prompt}"\n'
    )


def is_generated_mirror(text: str) -> bool:
    return all(marker in text for marker in MIRROR_MARKERS)


def preserve_or_build_frontmatter(
    current: str | None, entry: dict[str, Any]
) -> str:
    if current is not None and is_generated_mirror(current):
        match = FRONTMATTER_RE.match(current)
        if not match:
            raise SystemExit(
                f"{entry['role_id']}: existing generated mirror has invalid frontmatter"
            )
        return current[: match.end()].rstrip("\n") + "\n"
    return build_frontmatter(entry)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    destination = args.dest.expanduser().resolve()
    replace_collisions = set(args.replace_collision)
    entries = load_roster(repo)

    role_ids = [entry.get("role_id") for entry in entries]
    invalid = [
        role_id
        for role_id in role_ids
        if not isinstance(role_id, str)
        or len(role_id) > 63
        or not SKILL_NAME_RE.fullmatch(role_id)
    ]
    if invalid:
        raise SystemExit(f"Invalid skill role IDs: {invalid}")

    unknown_replacements = replace_collisions - set(role_ids)
    if unknown_replacements:
        raise SystemExit(
            "Unknown --replace-collision role IDs: "
            + ", ".join(sorted(unknown_replacements))
        )

    counts = {"created": 0, "updated": 0, "unchanged": 0, "skipped": 0}
    skipped: list[str] = []
    changed_roles: list[str] = []

    for entry in entries:
        role_id = entry["role_id"]
        skill_dir = destination / role_id
        skill_path = skill_dir / "SKILL.md"
        current = (
            skill_path.read_text(encoding="utf-8") if skill_path.is_file() else None
        )

        collision = current is not None and not is_generated_mirror(current)
        if collision and role_id not in replace_collisions:
            counts["skipped"] += 1
            skipped.append(role_id)
            continue

        frontmatter = preserve_or_build_frontmatter(current, entry)
        expected = frontmatter + "\n" + build_body(repo, entry)
        if current == expected:
            counts["unchanged"] += 1
            continue

        action = "created" if current is None else "updated"
        counts[action] += 1
        changed_roles.append(role_id)
        if not args.check:
            atomic_write(skill_path, expected)
            metadata_path = skill_dir / "agents" / "openai.yaml"
            if not metadata_path.exists():
                atomic_write(metadata_path, default_openai_yaml(entry))

    mode = "check" if args.check else "sync"
    print(
        f"{mode}: "
        + ", ".join(f"{key}={value}" for key, value in counts.items())
    )
    if changed_roles:
        print("changed roles: " + ", ".join(changed_roles))
    if skipped:
        print(
            "preserved non-mirror collisions: "
            + ", ".join(skipped)
            + " (use --replace-collision ROLE_ID to replace)"
        )

    return 1 if args.check and changed_roles else 0


if __name__ == "__main__":
    sys.exit(main())
