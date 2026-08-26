#!/usr/bin/env python3
"""Validate and sync repo-owned procedure skills to Codex and Hermes."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\n(?P<yaml>.*?)\n---\n(?P<body>.*)\Z", re.DOTALL)
CODEX_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
IGNORED_NAMES = {".DS_Store"}


@dataclass(frozen=True)
class PortableSkill:
    name: str
    category: str
    source: Path
    metadata: dict[str, Any]


def parse_args() -> argparse.Namespace:
    repo_default = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Sync canonical procedure skills to Codex and Hermes."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=repo_default,
        help=f"Agents repository (default: {repo_default})",
    )
    parser.add_argument(
        "--codex-dest",
        type=Path,
        default=Path.home() / ".agents" / "skills",
        help="Flat Codex skills directory (default: ~/.agents/skills)",
    )
    parser.add_argument(
        "--hermes-dest",
        type=Path,
        default=Path.home() / ".hermes" / "skills",
        help="Categorized Hermes skills directory (default: ~/.hermes/skills)",
    )
    parser.add_argument(
        "--target",
        choices=("both", "codex", "hermes"),
        default="both",
        help="Runtime library to sync (default: both)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate and report drift without writing; exit 1 if sync is needed.",
    )
    return parser.parse_args()


def load_yaml_mapping(text: str, source: Path) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{source}: invalid YAML: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{source}: expected a YAML mapping")
    return payload


def validate_openai_yaml(path: Path, skill_name: str) -> None:
    if not path.is_file():
        raise ValueError(f"{skill_name}: missing agents/openai.yaml")
    payload = load_yaml_mapping(path.read_text(encoding="utf-8"), path)
    interface = payload.get("interface")
    if not isinstance(interface, dict):
        raise ValueError(f"{path}: missing interface mapping")

    for key in ("display_name", "short_description", "default_prompt"):
        if not isinstance(interface.get(key), str) or not interface[key].strip():
            raise ValueError(f"{path}: interface.{key} must be a non-empty string")

    short_description = interface["short_description"].strip()
    if not 25 <= len(short_description) <= 64:
        raise ValueError(
            f"{path}: short_description must contain 25-64 characters "
            f"(found {len(short_description)})"
        )

    invocation = f"${skill_name}"
    if invocation not in interface["default_prompt"]:
        raise ValueError(f"{path}: default_prompt must mention {invocation}")


def validate_skill_dir(skill_dir: Path, category: str) -> PortableSkill:
    skill_path = skill_dir / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{skill_path}: invalid or missing YAML frontmatter")

    frontmatter = load_yaml_mapping(match.group("yaml"), skill_path)
    unexpected = set(frontmatter) - CODEX_FRONTMATTER_KEYS
    if unexpected:
        raise ValueError(
            f"{skill_path}: Codex-incompatible frontmatter keys: "
            + ", ".join(sorted(unexpected))
        )

    name = frontmatter.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        raise ValueError(f"{skill_path}: invalid skill name {name!r}")
    if name != skill_dir.name:
        raise ValueError(f"{skill_path}: name must match directory {skill_dir.name!r}")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"{skill_path}: description must be a non-empty string")
    if len(description) > 60:
        raise ValueError(
            f"{skill_path}: description exceeds Hermes' 60-character limit "
            f"({len(description)})"
        )
    if not description.startswith("Use when "):
        raise ValueError(f"{skill_path}: description must start with 'Use when '")
    if not match.group("body").strip():
        raise ValueError(f"{skill_path}: skill body must not be empty")

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"{skill_path}: metadata must be a mapping")
    hermes = metadata.get("hermes")
    if not isinstance(hermes, dict):
        raise ValueError(f"{skill_path}: metadata.hermes must be a mapping")
    if not isinstance(hermes.get("tags"), list) or not hermes["tags"]:
        raise ValueError(f"{skill_path}: metadata.hermes.tags must be a non-empty list")
    if not isinstance(hermes.get("related_skills"), list):
        raise ValueError(f"{skill_path}: metadata.hermes.related_skills must be a list")

    validate_openai_yaml(skill_dir / "agents" / "openai.yaml", name)
    return PortableSkill(name=name, category=category, source=skill_dir, metadata=metadata)


def discover_portable_skills(repo: Path) -> list[PortableSkill]:
    skills_root = repo / "skills"
    if not skills_root.is_dir():
        raise ValueError(f"{skills_root}: portable skills directory not found")

    skills: list[PortableSkill] = []
    seen: set[str] = set()
    for skill_path in sorted(skills_root.glob("*/*/SKILL.md")):
        skill_dir = skill_path.parent
        category = skill_dir.parent.name
        skill = validate_skill_dir(skill_dir, category)
        if skill.name in seen:
            raise ValueError(f"Duplicate portable skill name: {skill.name}")
        seen.add(skill.name)
        skills.append(skill)

    if not skills:
        raise ValueError(f"{skills_root}: no portable skills found")
    return skills


def package_files(skill: PortableSkill) -> dict[Path, bytes]:
    files: dict[Path, bytes] = {}
    for path in sorted(skill.source.rglob("*")):
        if not path.is_file() or path.name in IGNORED_NAMES or "__pycache__" in path.parts:
            continue
        files[path.relative_to(skill.source)] = path.read_bytes()
    return files


def destination_state(skill: PortableSkill, destination: Path) -> tuple[str, list[Path]]:
    expected = package_files(skill)
    missing_or_changed = [
        rel
        for rel, content in expected.items()
        if not (destination / rel).is_file() or (destination / rel).read_bytes() != content
    ]
    if not (destination / "SKILL.md").is_file():
        return "created", missing_or_changed
    if missing_or_changed:
        return "updated", missing_or_changed
    return "unchanged", []


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "wb", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def sync_package(skill: PortableSkill, destination: Path, check: bool) -> str:
    state, changed_files = destination_state(skill, destination)
    if state != "unchanged" and not check:
        expected = package_files(skill)
        for rel in changed_files:
            atomic_write(destination / rel, expected[rel])
    return state


def target_destinations(
    skill: PortableSkill,
    target: str,
    codex_dest: Path,
    hermes_dest: Path,
) -> list[tuple[str, Path]]:
    destinations: list[tuple[str, Path]] = []
    if target in {"both", "codex"}:
        destinations.append(("codex", codex_dest / skill.name))
    if target in {"both", "hermes"}:
        destinations.append(("hermes", hermes_dest / skill.category / skill.name))
    return destinations


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    codex_dest = args.codex_dest.expanduser().resolve()
    hermes_dest = args.hermes_dest.expanduser().resolve()

    try:
        skills = discover_portable_skills(repo)
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    counts = {"created": 0, "updated": 0, "unchanged": 0}
    changed: list[str] = []
    for skill in skills:
        for runtime, destination in target_destinations(
            skill, args.target, codex_dest, hermes_dest
        ):
            state = sync_package(skill, destination, args.check)
            counts[state] += 1
            if state != "unchanged":
                changed.append(f"{runtime}:{skill.name}")

    mode = "check" if args.check else "sync"
    print(
        f"{mode}: skills={len(skills)}, target={args.target}, "
        + ", ".join(f"{key}={value}" for key, value in counts.items())
    )
    if changed:
        print("changed packages: " + ", ".join(changed))
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
