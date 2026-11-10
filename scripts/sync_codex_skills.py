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
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import managed_publication as publication


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
    parser.add_argument("--plan", action="store_true", help="Print publication preview JSON")
    parser.add_argument("--apply", metavar="PLAN_HASH", help="Apply the exact preview")
    parser.add_argument("--adopt-existing", action="store_true", help="Reconcile legacy generated copies explicitly")
    return parser.parse_args()


def load_roster(repo: Path) -> list[dict[str, Any]]:
    """Load the same canonical profile entries consumed by Hermes."""
    entries: list[dict[str, Any]] = []
    for path in sorted(repo.glob("*/roster_entry.json")):
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"Unable to load {path}: {exc}") from exc
        if not isinstance(entry, dict):
            raise SystemExit(f"{path}: expected a JSON object")
        if entry.get("role_id") != path.parent.name:
            raise SystemExit(f"{path}: role_id must match the profile directory")
        entries.append(entry)
    if not entries:
        raise SystemExit(f"{repo}: no profile roster entries found")
    return entries


def sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith((".", "!", "?")) else f"{text}."


def codex_skill_name(entry: dict[str, Any]) -> str:
    """Codex export identity; the canonical role/Hermes profile keeps its slug."""
    name = entry.get("codex_skill_name", entry["role_id"])
    if not isinstance(name, str) or len(name) > 63 or not SKILL_NAME_RE.fullmatch(name):
        raise SystemExit(f"{entry['role_id']}: invalid codex_skill_name: {name!r}")
    return name


def validate_export_names(repo: Path, entries: list[dict[str, Any]]) -> dict[str, str]:
    names = {entry['role_id']: codex_skill_name(entry) for entry in entries}
    if len(set(names.values())) != len(names):
        raise SystemExit("Duplicate Codex persona export names")
    procedures = {p.parent.name for p in (repo / 'skills').glob('*/*/SKILL.md')}
    for role, name in names.items():
        if name != role and name in procedures:
            raise SystemExit(f"{role}: Codex alias conflicts with portable procedure {name}")
    return names


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


def build_body(repo: Path, entry: dict[str, Any], export_names=None) -> str:
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

    procedures = list(dict.fromkeys(entry.get("hermes_skills") or []))
    if procedures:
        sections.extend((
            "## Procedure Skills",
            "Load only when relevant; keep the procedure in its shared package, "
            "not duplicated in this persona.\n\n"
            + "\n".join(f"- ${name}" for name in procedures),
        ))

    delegates = (entry.get("handoff_rules") or {}).get("delegate_to") or []
    if delegates:
        export_names = export_names or {}
        handoffs = "\n".join(
            f"- **{export_names.get(item['role_id'], item['role_id'])}** — {item['when']}"
            for item in delegates
        )
        sections.extend(("## Handoffs", handoffs))

    return "\n\n".join(sections) + "\n"


def build_frontmatter(entry: dict[str, Any]) -> str:
    description = build_description(entry)
    return (
        "---\n"
        f"name: {codex_skill_name(entry)}\n"
        f"description: {yaml_single_quote(description)}\n"
        "---\n"
    )


def default_openai_yaml(entry: dict[str, Any]) -> str:
    role_id = entry["role_id"]
    export_name = codex_skill_name(entry)
    configured = entry.get("codex_interface") or {}
    if not isinstance(configured, dict):
        raise SystemExit(f"{role_id}: codex_interface must be an object")

    display_name = configured.get("display_name") or entry["role_name"]
    short_description = configured.get("short_description") or (
        f"Work as the {entry['role_name']} profile"
    )
    if len(short_description) > 64:
        short_description = f"Use the {entry['role_name']} specialist profile"
    prompt = configured.get("default_prompt") or f"Use ${export_name} to help with this task."

    values = {
        "display_name": display_name,
        "short_description": short_description,
        "default_prompt": prompt,
    }
    for key, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"{role_id}: codex_interface.{key} must be a string")
    if not 25 <= len(short_description) <= 64:
        raise SystemExit(
            f"{role_id}: Codex short_description must contain 25-64 characters"
        )
    if not re.search(r"\$" + re.escape(export_name) + r"(?![a-z0-9-])", prompt):
        raise SystemExit(
            f"{role_id}: Codex default_prompt must mention ${export_name}"
        )

    return (
        "interface:\n"
        f"  display_name: {json.dumps(display_name, ensure_ascii=False)}\n"
        f"  short_description: {json.dumps(short_description, ensure_ascii=False)}\n"
        f"  default_prompt: {json.dumps(prompt, ensure_ascii=False)}\n"
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
        name = codex_skill_name(entry)
        if not re.search(r"(?m)^name: *['\"]?" + re.escape(name) + r"['\"]? *$", match['yaml']):
            raise SystemExit(f"{entry['role_id']}: existing mirror name differs from {name}")
        return current[: match.end()].rstrip("\n") + "\n"
    return build_frontmatter(entry)


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    destination = args.dest.expanduser().absolute()
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
    export_names = validate_export_names(repo, entries)

    unknown_replacements = replace_collisions - set(role_ids)
    if unknown_replacements:
        raise SystemExit(
            "Unknown --replace-collision role IDs: "
            + ", ".join(sorted(unknown_replacements))
        )

    counts = {"created": 0, "updated": 0, "unchanged": 0, "skipped": 0}
    metadata_counts = {"created": 0, "updated": 0, "unchanged": 0}
    skipped: list[str] = []
    changed_roles: list[str] = []
    changed_metadata: list[str] = []

    prepared = []
    for entry in entries:
        role_id = entry["role_id"]
        skill_dir = destination / export_names[role_id]
        skill_path = publication.safe_path(skill_dir, "SKILL.md")
        current = (
            skill_path.read_text(encoding="utf-8") if skill_path.is_file() else None
        )

        collision = current is not None and not is_generated_mirror(current)
        if collision and role_id not in replace_collisions:
            counts["skipped"] += 1
            skipped.append(role_id)
            continue

        frontmatter = preserve_or_build_frontmatter(current, entry)
        expected = frontmatter + "\n" + build_body(repo, entry, export_names)
        if current == expected:
            counts["unchanged"] += 1
        else:
            action = "created" if current is None else "updated"
            counts[action] += 1
            changed_roles.append(role_id)

        metadata_path = publication.safe_path(skill_dir, "agents/openai.yaml")
        current_metadata = (
            metadata_path.read_text(encoding="utf-8")
            if metadata_path.is_file()
            else None
        )
        expected_metadata = default_openai_yaml(entry)
        if current_metadata == expected_metadata:
            metadata_counts["unchanged"] += 1
        else:
            action = "created" if current_metadata is None else "updated"
            metadata_counts[action] += 1
            changed_metadata.append(role_id)

        files = {"SKILL.md": expected.encode(), "agents/openai.yaml": expected_metadata.encode()}
        state = destination / ".persona-state" / role_id
        previous = publication.read_json(state / 'manifest.json', {})
        if previous.get('transaction'):
            journal = publication.read_json(
                state / 'transactions' / previous['transaction'] / 'journal.json', {})
            if journal.get('root') != str(skill_dir.absolute()):
                raise SystemExit(f"{role_id}: changing an already-published export name requires a separate migration")
        source = {"owner": "agents-roster", "role_id": role_id,
                  "files": {name: publication.digest(data) for name, data in files.items()}}
        plan = publication.preview(skill_dir, state, files, source=source,
                                   adopt=args.adopt_existing or role_id in replace_collisions)
        prepared.append((skill_dir, state, files, plan))

    if args.apply and (args.check or args.plan):
        raise SystemExit("--apply cannot be combined with --check or --plan")
    plans = [plan for _, _, _, plan in prepared]
    combined = publication.digest(publication.json_bytes(plans))
    if args.plan or (not args.check and not args.apply):
        print(json.dumps({"plan_hash": combined, "packages": plans, "preserved_collisions": skipped}, indent=2))
        return 0
    if args.apply:
        if args.apply != combined:
            raise publication.PublicationError("Stale persona preview; inspect a fresh preview")
        conflicts = [p["root"] + ":" + f["path"] for p in plans for f in p["files"] if f["action"] == "conflict"]
        if conflicts:
            raise publication.PublicationError("Unresolved persona conflicts: " + ", ".join(conflicts))
        for root, state, files, plan in prepared:
            publication.publish(root, state, files, expected=plan["plan_hash"],
                                source=plan["source"], adopt=plan["adopt_existing"])

    mode = "check" if args.check else "sync"
    print(
        f"{mode}: "
        + ", ".join(f"{key}={value}" for key, value in counts.items())
    )
    print(
        "metadata: "
        + ", ".join(f"{key}={value}" for key, value in metadata_counts.items())
    )
    if changed_roles:
        print("changed roles: " + ", ".join(changed_roles))
    if changed_metadata:
        print("changed metadata: " + ", ".join(changed_metadata))
    if skipped:
        print(
            "preserved non-mirror collisions: "
            + ", ".join(skipped)
            + " (use --replace-collision ROLE_ID to replace)"
        )

    return 1 if args.check and (changed_roles or changed_metadata) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
