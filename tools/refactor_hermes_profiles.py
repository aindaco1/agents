#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(read_text(path))


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    return normalize_space(text.replace("—", "-"))


def slugify(text: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    ascii_text = ascii_text.replace("&", " and ")
    ascii_text = ascii_text.replace("/", " ")
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text)
    return ascii_text.strip("-")


def extract_section(markdown: str, heading_pattern: str) -> str:
    lines = markdown.splitlines()
    start = None
    pattern = re.compile(heading_pattern)
    for idx, line in enumerate(lines):
        if pattern.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return ""

    end = len(lines)
    for idx in range(start, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break
    return "\n".join(lines[start:end]).strip()


def extract_summary_field(markdown: str, label: str) -> str:
    match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+)", markdown)
    return strip_markdown(match.group(1)) if match else ""


def extract_bullets(markdown_section: str) -> list[str]:
    bullets: list[str] = []
    for line in markdown_section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(strip_markdown(stripped[2:]))
    return bullets


def split_listish(text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
        if ch == "," and depth == 0:
            item = normalize_space("".join(current).strip())
            if item:
                items.append(re.sub(r"^(and|or)\s+", "", item))
            current = []
            continue
        current.append(ch)

    tail = normalize_space("".join(current).strip().rstrip("."))
    if tail:
        items.append(re.sub(r"^(and|or)\s+", "", tail))
    return [item for item in items if item]


def sentence_case(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return cleaned
    return cleaned[0].upper() + cleaned[1:]


def remove_hermes_workflow(markdown: str) -> str:
    lines = markdown.splitlines()
    start = None
    end = None
    for idx, line in enumerate(lines):
        if line.strip() == "## Hermes Agent Workflow":
            start = idx
            break
    if start is None:
        return markdown.rstrip() + "\n"

    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break

    new_lines = lines[:start] + lines[end:]
    collapsed = re.sub(r"\n{3,}", "\n\n", "\n".join(new_lines).strip())
    return collapsed + "\n"


def build_role_lookup(profile_dirs: list[Path]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for profile_dir in profile_dirs:
        entry = load_json(profile_dir / "roster_entry.json")
        role_id = entry["role_id"]
        role_name = entry["role_name"]
        display_name = entry["display_name"]

        keys = {
            role_id,
            slugify(role_id),
            role_name.lower(),
            slugify(role_name),
            display_name.lower(),
            slugify(display_name),
        }
        if "(" in role_name:
            plain_role_name = re.sub(r"\s*\(.*?\)", "", role_name).strip()
            keys.add(plain_role_name.lower())
            keys.add(slugify(plain_role_name))
        for key in keys:
            lookup[key] = role_id
    return lookup


def resolve_role_id(label: str, role_lookup: dict[str, str]) -> str | None:
    cleaned = strip_markdown(label).strip()
    candidates = [
        cleaned,
        cleaned.lower(),
        slugify(cleaned),
        cleaned.replace("the ", "").lower(),
        slugify(cleaned.replace("the ", "")),
    ]
    for candidate in candidates:
        if candidate in role_lookup:
            return role_lookup[candidate]
    return None


def split_escalation_conditions(text: str) -> list[str]:
    cleaned = normalize_space(text.strip().rstrip("."))
    cleaned = re.sub(r"^[Ww]hen:\s*", "", cleaned)
    cleaned = re.sub(r"^[Ww]hen\s+", "", cleaned)
    parts = re.split(r";\s*(?:or\s+)?(?:when\s+)?|,\s*(?:or\s+)?when\s+", cleaned)
    conditions = []
    for part in parts:
        candidate = normalize_space(part)
        candidate = re.sub(r"^(and|or)\s+", "", candidate)
        candidate = re.sub(r"^[Ww]hen\s+", "", candidate)
        if candidate:
            conditions.append(candidate)
    if len(conditions) <= 1 and "," in cleaned:
        conditions = [
            normalize_space(re.sub(r"^(and|or)\s+", "", item))
            for item in split_listish(cleaned)
        ]
    if any("substitute for" in item for item in conditions):
        merged: list[str] = []
        buffering = False
        for item in conditions:
            if "substitute for" in item:
                merged.append(item)
                buffering = True
                continue
            if buffering:
                merged[-1] = f"{merged[-1]}, {item}"
            else:
                merged.append(item)
        conditions = merged
    return conditions or [cleaned]


def parse_handoff_rules(boundaries_section: str, role_lookup: dict[str, str], pairs: list[str]) -> dict:
    delegate_to: list[dict[str, str]] = []
    seen_pairs: set[tuple[str, str]] = set()
    explicit_roles: set[str] = set()
    escalate_to_human_when: list[str] = []
    general_rules: list[str] = []
    valid_role_ids = set(role_lookup.values())

    for raw_line in boundaries_section.splitlines():
        stripped = raw_line.strip()
        if not stripped.startswith("- "):
            continue

        bullet = strip_markdown(stripped[2:])
        role_mentions = re.findall(r"\*\*(.*?)\*\*", raw_line)

        if re.search(r"\bescalate to the human\b", bullet, re.IGNORECASE):
            condition_text = bullet.split("when:", 1)[1] if "when:" in bullet else bullet
            for condition in split_escalation_conditions(condition_text):
                if condition not in escalate_to_human_when:
                    escalate_to_human_when.append(condition)
            continue

        if role_mentions:
            when_text = bullet
            for label in role_mentions:
                role_id = resolve_role_id(label, role_lookup)
                if not role_id:
                    continue
                pair = (role_id, when_text)
                if pair in seen_pairs:
                    continue
                delegate_to.append({"role_id": role_id, "when": when_text})
                seen_pairs.add(pair)
                explicit_roles.add(role_id)
            if re.search(r"\bhand off\b|\broute\b|\bdelegate\b", bullet, re.IGNORECASE):
                continue

        if re.search(r"\bhand off\b|\broute\b|\bdelegate\b", bullet, re.IGNORECASE):
            general_rules.append(bullet)

    for role_id in pairs:
        if role_id not in valid_role_ids:
            continue
        if role_id in explicit_roles:
            continue
        pair = (role_id, "Collaborate or hand off when the work crosses into this adjacent specialty.")
        if pair not in seen_pairs:
            delegate_to.append(
                {
                    "role_id": role_id,
                    "when": "Collaborate or hand off when the work crosses into this adjacent specialty.",
                }
            )
            seen_pairs.add(pair)

    return {
        "delegate_to": delegate_to,
        "escalate_to_human_when": escalate_to_human_when,
        "general_rules": general_rules,
    }


def temperature_for_tier(tier: str) -> float:
    return {
        "heavy-reasoning": 0.2,
        "strong-general": 0.35,
        "creative-writing": 0.7,
        "structured-routine": 0.2,
        "multilingual-specialized": 0.4,
    }.get(tier, 0.35)


def reasoning_hint(model_recommendations: dict) -> str:
    for provider in ("openai", "anthropic"):
        payload = model_recommendations.get(provider, {})
        if "reasoning" in payload:
            return payload["reasoning"]
        if "thinking" in payload:
            return payload["thinking"]
    tier = model_recommendations.get("tier", "strong-general")
    return {
        "heavy-reasoning": "high",
        "strong-general": "medium",
        "creative-writing": "low",
        "structured-routine": "low",
        "multilingual-specialized": "medium",
    }.get(tier, "medium")


def build_invocation_hints(entry: dict, skills: list[str], process_summary: str) -> list[str]:
    hints = [
        f"Use when the work calls for this profile: {entry['tagline'].rstrip('.')}.",
    ]
    for skill in skills[:2]:
        hints.append(f"Strong fit for {skill.rstrip('.')}.")
    if process_summary:
        hints.append(f"Works best when the task can follow this flow: {process_summary.rstrip('.')}.")
    return hints[:4]


def build_user_md(entry: dict, style_summary: str, process_summary: str) -> str:
    return f"""# USER.md — {entry['role_name']}

Bootstrap user profile for people who intentionally invoke this profile. Replace these defaults with real user-specific notes over time.

## Likely Preferences

- Wants help that matches this role: {entry['tagline'].rstrip('.')}.
- Prefers this communication style: {style_summary.rstrip('.')}.
- Expects outputs that roughly follow this workflow: {process_summary.rstrip('.')}.

## Clarify Early

- The desired outcome, decision, or artifact.
- Scope, timeframe, and constraints.
- Required depth, speed, and output format.
"""


def build_memory_md(entry: dict, remember_items: list[str]) -> str:
    bullets = "\n".join(f"- {sentence_case(item.rstrip('.'))}" for item in remember_items[:8])
    return f"""# MEMORY.md — {entry['role_name']}

Starter durable memory priorities for this profile. Replace these bootstrap notes with live facts once the agent starts working.

## Keep

{bullets}

## Skip

- Temporary scratch notes, one-off paths, transient URLs, or session-only context better kept in workspace files or active todos.
"""


def migrate_profiles() -> None:
    profile_dirs = sorted(path.parent for path in ROOT.glob("*/roster_entry.json"))
    role_lookup = build_role_lookup(profile_dirs)

    updated_entries: dict[str, dict] = {}

    for profile_dir in profile_dirs:
        entry_path = profile_dir / "roster_entry.json"
        identity_path = profile_dir / "IDENTITY.md"
        summary_path = profile_dir / "IDENTITY_SUMMARY.md"
        soul_path = profile_dir / "SOUL.md"
        user_path = profile_dir / "USER.md"
        memory_path = profile_dir / "MEMORY.md"

        entry = load_json(entry_path)
        identity = read_text(identity_path)
        summary = read_text(summary_path)
        soul = read_text(soul_path)

        soul_clean = remove_hermes_workflow(soul)
        write_text(soul_path, soul_clean)

        skills_section = extract_section(identity, r"^## What .*Good At$")
        skills = extract_bullets(skills_section)

        boundaries_section = extract_section(soul_clean, r"^## Boundaries$")
        handoff_rules = parse_handoff_rules(boundaries_section, role_lookup, entry.get("pairs_well_with", []))

        who_you_are = extract_summary_field(summary, "Who you are")
        style_summary = extract_summary_field(summary, "Style")
        process_summary = extract_summary_field(summary, "Process")
        remember_summary = extract_summary_field(summary, "Remember via Hermes memory")
        remember_items = split_listish(remember_summary)

        write_text(user_path, build_user_md(entry, style_summary, process_summary))
        write_text(memory_path, build_memory_md(entry, remember_items))

        tier = entry.get("model_recommendations", {}).get("tier", "strong-general")
        entry["slug"] = entry["role_id"]
        entry["entrypoint"] = "SOUL.md"
        entry["avatar"] = "avatar.webp"
        entry["identity_summary"] = who_you_are
        entry["invocation_hints"] = build_invocation_hints(entry, skills, process_summary)
        entry["avoid_for"] = entry.get("cons", [])
        entry["handoff_rules"] = handoff_rules
        entry["skills"] = skills
        entry["default_temperature"] = temperature_for_tier(tier)
        entry["model_behavior_hints"] = {
            "reasoning_effort": reasoning_hint(entry.get("model_recommendations", {})),
            "verbosity": "medium",
            "tool_bias": "balanced",
        }

        write_json(entry_path, entry)
        updated_entries[entry["role_id"]] = entry

    roster_path = ROOT / "roster.json"
    roster = load_json(roster_path)
    roster["generated"] = str(date.today())

    new_agents = []
    for existing in roster.get("agents", []):
        role_id = existing["role_id"]
        new_agents.append(updated_entries.get(role_id, existing))

    roster["agents"] = new_agents
    roster["total_agents"] = len(new_agents)
    pronouns = Counter(agent.get("pronouns") for agent in new_agents)
    roster["gender_distribution"] = {
        "he_him": pronouns.get("he/him", 0),
        "she_her": pronouns.get("she/her", 0),
        "they_them": pronouns.get("they/them", 0),
    }
    write_json(roster_path, roster)

    print(f"Migrated {len(profile_dirs)} profiles")


if __name__ == "__main__":
    migrate_profiles()
