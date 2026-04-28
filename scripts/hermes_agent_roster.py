#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required. Run this with Hermes' Python environment, e.g. "
        "~/.hermes/hermes-agent/venv/bin/python hermes_agent_roster.py ..."
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HERMES_HOME = Path.home() / ".hermes"
PROFILES_ROOT = DEFAULT_HERMES_HOME / "profiles"
GENERATED_ROOT = ROOT / "generated"
MANIFEST_PATH = GENERATED_ROOT / "hermes_profiles_manifest.json"
WRAPPER_NAMES = {
    "agent-list": "list",
    "agent-compile": "compile",
    "agent-run": "run",
    "agent-route": "route",
}

REQUIRED_AGENT_FILES = [
    "SOUL.md",
    "MEMORY.md",
    "USER.md",
    "IDENTITY.md",
    "IDENTITY_SUMMARY.md",
    "roster_entry.json",
]
OPTIONAL_AGENT_GLOBS = ["*.webp", "*.txt"]
PROFILE_DIRS = [
    "memories",
    "sessions",
    "skills",
    "skins",
    "logs",
    "plans",
    "workspace",
    "cron",
    "home",
    "assets",
    "context",
    "references",
]

TARGET_END_SLUG = "data-ai-ml-generalist"
STOPWORDS = {
    "about", "after", "also", "and", "build", "deciding", "design", "for", "from", "help", "into",
    "launch", "lightweight", "need", "service", "sharp", "sharper", "that", "the", "their", "them",
    "this", "what", "week", "with", "work", "workflow",
}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def dump_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True)


def discover_agents() -> list[Path]:
    dirs: list[Path] = []
    for child in ROOT.iterdir():
        if child.name.startswith(".") or not child.is_dir():
            continue
        if (child / "roster_entry.json").exists():
            dirs.append(child)
    return sorted(dirs, key=lambda p: p.name)


def first_target_agents() -> list[Path]:
    dirs = discover_agents()
    selected: list[Path] = []
    for p in dirs:
        selected.append(p)
        if p.name == TARGET_END_SLUG:
            break
    return selected


def validate_agent_dir(agent_dir: Path) -> dict[str, Any]:
    missing = [name for name in REQUIRED_AGENT_FILES if not (agent_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"{agent_dir.name}: missing required files: {', '.join(missing)}")
    with (agent_dir / "roster_entry.json").open("r", encoding="utf-8") as fh:
        entry = json.load(fh)
    if not isinstance(entry, dict):
        raise ValueError(f"{agent_dir.name}: roster_entry.json must be an object")
    slug = entry.get("slug") or entry.get("role_id") or agent_dir.name
    if slug != agent_dir.name:
        raise ValueError(f"{agent_dir.name}: slug mismatch ({slug})")
    return entry


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS]


def entry_search_text(entry: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ["slug", "display_name", "role_name", "category", "subcategory", "tagline", "identity_summary"]:
        value = entry.get(key)
        if isinstance(value, str):
            parts.append(value)
    for key in ["invocation_hints", "skills", "avoid_for"]:
        value = entry.get(key) or []
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
    handoffs = (entry.get("handoff_rules") or {}).get("delegate_to") or []
    for item in handoffs:
        if isinstance(item, dict):
            parts.extend(str(item.get(k, "")) for k in ["role_id", "when"])
    return "\n".join(parts).lower()


def route_prompt(prompt: str, entries: list[dict[str, Any]], top_n: int = 3) -> list[dict[str, Any]]:
    prompt_tokens = tokenize(prompt)
    prompt_text = " ".join(prompt_tokens)
    ranked: list[dict[str, Any]] = []

    for entry in entries:
        haystack = entry_search_text(entry)
        role_name = str(entry.get("role_name") or "").lower()
        category = str(entry.get("category") or "").lower()
        slug = str(entry.get("slug") or "")
        role_tokens = set(tokenize(role_name.replace("/", " ").replace("-", " ")))
        slug_tokens = set(tokenize(slug.replace("-", " ")))
        score = 0
        matched: list[str] = []

        for token in sorted(set(prompt_tokens)):
            if len(token) < 4:
                continue
            if token in role_tokens:
                score += 8
                matched.append(f"role:{token}")
            elif token in slug_tokens:
                score += 6
                matched.append(f"slug:{token}")
            elif token in haystack:
                score += 2
                matched.append(token)

        if any(word in prompt_text for word in ["priorit", "sequenc", "delegate", "triage"]):
            if "chief of staff" in role_name:
                score += 20
                matched.append("chief-of-staff-fit")
            elif any(word in role_name for word in ["operations", "workflow", "manager"]):
                score += 8
                matched.append("ops-fit")
        if any(word in prompt_text for word in ["api", "backend", "architecture", "infrastructure", "system"]):
            if "backend architect" in role_name:
                score += 20
                matched.append("backend-architect-fit")
            elif any(word in role_name for word in ["architect", "backend", "engineer", "systems"]):
                score += 8
                matched.append("engineering-fit")
        if any(word in prompt_text for word in ["research", "literature", "sources", "paper", "citation"]):
            if any(word in role_name for word in ["research", "analyst", "scientist"]):
                score += 8
                matched.append("research-fit")
        if any(word in prompt_text for word in ["content", "messaging", "audience", "campaign", "brand"]):
            if any(word in role_name for word in ["content", "writer", "editor", "brand", "marketing", "copywriter"]):
                score += 8
                matched.append("content-fit")

        if category and category in prompt_text:
            score += 2
            matched.append(category)

        ranked.append({
            "slug": slug,
            "role_name": entry.get("role_name"),
            "category": entry.get("category"),
            "score": score,
            "matched_terms": sorted(set(matched)),
        })

    ranked.sort(key=lambda item: (-item["score"], item["slug"]))
    return ranked[:top_n]


def select_profile_runtime(entry: dict[str, Any], base_cfg: dict[str, Any]) -> dict[str, Any]:
    model_cfg = entry.get("model_recommendations") or {}
    behavior = entry.get("model_behavior_hints") or {}
    default_provider = str((base_cfg.get("model") or {}).get("provider") or "openai-codex")
    default_model = str((base_cfg.get("model") or {}).get("default") or "gpt-5.4")

    openai_rec = model_cfg.get("openai") or {}
    provider = default_provider
    model = str(openai_rec.get("model") or default_model)
    reasoning = str(openai_rec.get("reasoning") or behavior.get("reasoning_effort") or "medium")

    fallback_providers: list[dict[str, Any]] = []
    seen_fallbacks: set[tuple[str, str]] = set()

    def add_fallback(provider_name: str, model_name: str) -> None:
        key = (provider_name, model_name)
        if key in seen_fallbacks:
            return
        seen_fallbacks.add(key)
        fallback_providers.append({"provider": provider_name, "model": model_name})

    anthropic_rec = model_cfg.get("anthropic") or {}
    if anthropic_rec.get("model"):
        add_fallback("anthropic", str(anthropic_rec["model"]))

    for fallback in deepcopy(base_cfg.get("fallback_providers") or []):
        if not isinstance(fallback, dict):
            continue
        fallback_provider = str(fallback.get("provider") or "").strip()
        fallback_model = str(fallback.get("model") or "").strip()
        if not fallback_provider or not fallback_model:
            continue
        if fallback_provider == "gemini":
            continue
        add_fallback(fallback_provider, fallback_model)

    return {
        "provider": provider,
        "model": model,
        "reasoning_effort": reasoning,
        "fallback_providers": fallback_providers,
    }


def infer_skill_guidance(entry: dict[str, Any]) -> dict[str, list[str]]:
    role = str(entry.get("role_name") or entry.get("slug") or "").lower()
    category = str(entry.get("category") or "").lower()
    subcategory = str(entry.get("subcategory") or "").lower()

    preferred: list[str] = ["session_search"]
    discouraged: list[str] = []

    if any(k in role for k in ["chief of staff", "operations", "program", "workflow", "manager"]):
        preferred.extend(["todo", "notion", "delegation", "cronjob"])
    if any(k in role for k in ["content", "writer", "copy", "editor", "brand"] ) or category in {"marketing", "communications"}:
        preferred.extend(["notion", "web", "session_search"])
        discouraged.extend(["writing-plans", "plan"])
    if any(k in role for k in ["architect", "engineer", "developer", "backend", "frontend", "systems"] ) or category == "engineering":
        preferred.extend(["terminal", "file", "delegation"])
    if any(k in role for k in ["research", "analyst", "scientist"]):
        preferred.extend(["web", "arxiv", "session_search"])

    # preserve order, drop duplicates
    def dedupe(items: list[str]) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for item in items:
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out

    return {"preferred": dedupe(preferred), "discouraged": dedupe(discouraged)}


def build_agent_context(entry: dict[str, Any], identity_summary: str, identity_md: str) -> str:
    display_name = entry.get("display_name") or entry.get("role_name") or entry.get("slug")
    role_name = entry.get("role_name") or "Agent"
    lines: list[str] = []
    lines.append("# AGENT CONTEXT")
    lines.append("")
    lines.append("## Runtime Identity")
    lines.append("")
    lines.append(f"- Name: {display_name}")
    lines.append(f"- Role: {role_name}")
    if entry.get("tagline"):
        lines.append(f"- Tagline: {entry['tagline']}")
    if entry.get("category"):
        lines.append(f"- Category: {entry['category']}")
    if entry.get("subcategory"):
        lines.append(f"- Subcategory: {entry['subcategory']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(identity_summary.strip() or entry.get("identity_summary") or "No summary provided.")
    lines.append("")

    lines.append("## Default Output Expectations")
    lines.append("")
    lines.append("- Be concise, direct, and role-appropriate.")
    lines.append("- Prefer concrete next steps over abstraction.")
    lines.append("- Use this profile's specialty before generic advice.")
    lines.append("")

    invocation = entry.get("invocation_hints") or []
    lines.append("## Best Fit")
    lines.append("")
    if invocation:
        for item in invocation:
            lines.append(f"- {item}")
    else:
        lines.append("- Use this profile when the task clearly matches its specialty.")
    lines.append("")

    avoid = entry.get("avoid_for") or []
    lines.append("## Poor Fit")
    lines.append("")
    if avoid:
        for item in avoid:
            lines.append(f"- {item}")
    else:
        lines.append("- Escalate when the task falls outside this profile's core specialty.")
    lines.append("")

    handoffs = (entry.get("handoff_rules") or {}).get("delegate_to") or []
    lines.append("## Handoff Rules")
    lines.append("")
    if handoffs:
        for item in handoffs:
            role_id = item.get("role_id", "unknown")
            when = item.get("when", "")
            lines.append(f"- {role_id}: {when}".rstrip())
    else:
        lines.append("- No explicit handoff rules provided.")
    lines.append("")

    guidance = infer_skill_guidance(entry)
    lines.append("## Preferred Hermes Skills")
    lines.append("")
    for item in guidance["preferred"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Discouraged Hermes Skills")
    lines.append("")
    if guidance["discouraged"]:
        for item in guidance["discouraged"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None specified.")
    lines.append("")

    skills = entry.get("skills") or []
    if skills:
        lines.append("## Core Skills")
        lines.append("")
        for item in skills[:12]:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("## Identity Reference Excerpt")
    lines.append("")
    excerpt = identity_md.strip().splitlines()
    for line in excerpt[:40]:
        lines.append(line)
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def ensure_profile_dirs(profile_dir: Path) -> None:
    profile_dir.mkdir(parents=True, exist_ok=True)
    for rel in PROFILE_DIRS:
        (profile_dir / rel).mkdir(parents=True, exist_ok=True)


def write_profile(agent_dir: Path, entry: dict[str, Any], base_cfg: dict[str, Any]) -> dict[str, Any]:
    slug = agent_dir.name
    profile_dir = PROFILES_ROOT / slug
    ensure_profile_dirs(profile_dir)

    shutil.copy2(agent_dir / "SOUL.md", profile_dir / "SOUL.md")
    shutil.copy2(agent_dir / "MEMORY.md", profile_dir / "memories" / "MEMORY.md")
    shutil.copy2(agent_dir / "USER.md", profile_dir / "memories" / "USER.md")
    shutil.copy2(agent_dir / "IDENTITY.md", profile_dir / "references" / "IDENTITY.md")
    shutil.copy2(agent_dir / "IDENTITY_SUMMARY.md", profile_dir / "references" / "IDENTITY_SUMMARY.md")
    shutil.copy2(agent_dir / "roster_entry.json", profile_dir / "roster_entry.json")

    for pattern in OPTIONAL_AGENT_GLOBS:
        for src in agent_dir.glob(pattern):
            shutil.copy2(src, profile_dir / "assets" / src.name)

    identity_summary = (agent_dir / "IDENTITY_SUMMARY.md").read_text(encoding="utf-8")
    identity_md = (agent_dir / "IDENTITY.md").read_text(encoding="utf-8")
    agent_context = build_agent_context(entry, identity_summary, identity_md)
    (profile_dir / "context" / "AGENT_CONTEXT.md").write_text(agent_context, encoding="utf-8")

    runtime = select_profile_runtime(entry, base_cfg)
    cfg = deepcopy(base_cfg)
    cfg.setdefault("model", {})
    cfg["model"]["provider"] = runtime["provider"]
    cfg["model"]["default"] = runtime["model"]
    cfg["fallback_providers"] = runtime["fallback_providers"]
    cfg.setdefault("agent", {})
    cfg["agent"]["reasoning_effort"] = runtime["reasoning_effort"]
    dump_yaml(profile_dir / "config.yaml", cfg)

    env_target = DEFAULT_HERMES_HOME / ".env"
    env_link = profile_dir / ".env"
    if env_link.exists() or env_link.is_symlink():
        env_link.unlink()
    env_link.symlink_to(env_target)

    skills_target = DEFAULT_HERMES_HOME / "skills"
    skills_link = profile_dir / "skills"
    if skills_link.exists() or skills_link.is_symlink():
        if skills_link.is_symlink() or skills_link.is_file():
            skills_link.unlink()
        elif skills_link.is_dir():
            shutil.rmtree(skills_link)
    skills_link.symlink_to(skills_target, target_is_directory=True)

    metadata = {
        "slug": slug,
        "profile_dir": str(profile_dir),
        "display_name": entry.get("display_name"),
        "role_name": entry.get("role_name"),
        "provider": runtime["provider"],
        "model": runtime["model"],
        "reasoning_effort": runtime["reasoning_effort"],
    }
    return metadata


def write_manifest(items: list[dict[str, Any]]) -> None:
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_from": str(ROOT),
        "target_profiles_root": str(PROFILES_ROOT),
        "count": len(items),
        "items": items,
    }
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compile_selected(agent_dirs: list[Path]) -> list[dict[str, Any]]:
    base_cfg = load_yaml(DEFAULT_HERMES_HOME / "config.yaml")
    PROFILES_ROOT.mkdir(parents=True, exist_ok=True)
    written = []
    for agent_dir in agent_dirs:
        entry = validate_agent_dir(agent_dir)
        written.append(write_profile(agent_dir, entry, base_cfg))
    write_manifest(written)
    return written


def route_agents(prompt: str, top_n: int = 3, limit_to_first_50: bool = True) -> list[dict[str, Any]]:
    candidates = first_target_agents() if limit_to_first_50 else discover_agents()
    entries = [validate_agent_dir(path) for path in candidates]
    return route_prompt(prompt, entries, top_n=top_n)


def in_git_repo(cwd: Path | None = None) -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(cwd) if cwd is not None else None,
            check=False,
        )
    except (FileNotFoundError, OSError):
        return False
    return result.returncode == 0


def build_run_command(slug: str, query: str | None, delegated: bool = False, cwd: Path | None = None) -> list[str]:
    cmd = ["hermes"]
    if delegated and in_git_repo(cwd):
        cmd.append("-w")
    cmd.extend(["-p", slug])
    if query is not None:
        cmd.extend(["chat", "-q", query])
    return cmd


def run_profile(slug: str, query: str | None, delegated: bool = False) -> int:
    return subprocess.call(build_run_command(slug, query, delegated=delegated, cwd=Path.cwd()))


def run_routed_profile(
    prompt: str,
    query: str | None = None,
    top_n: int = 3,
    limit_to_first_50: bool = True,
    delegated: bool = False,
) -> int:
    ranked = route_agents(prompt, top_n=top_n, limit_to_first_50=limit_to_first_50)
    if not ranked:
        raise SystemExit(f"No matching agent found for prompt: {prompt}")
    selected = ranked[0]["slug"]
    effective_query = query if query is not None else prompt
    return run_profile(selected, effective_query, delegated=delegated)


def build_wrapper_script(script_path: Path, subcommand: str) -> str:
    script = f'''#!/bin/sh
set -e
exec "{sys.executable}" "{script_path}" {subcommand} "$@"
'''
    return script


def install_launchers(wrapper_dir: Path, script_path: Path | None = None) -> list[Path]:
    script_path = script_path or Path(__file__).resolve()
    wrapper_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, subcommand in WRAPPER_NAMES.items():
        target = wrapper_dir / name
        target.write_text(build_wrapper_script(script_path, subcommand), encoding="utf-8")
        target.chmod(0o755)
        written.append(target)
    return written


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Compile roster agents into Hermes profiles")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List discovered agent slugs")

    p_compile = sub.add_parser("compile", help="Compile one or more agents by slug")
    p_compile.add_argument("slugs", nargs="+", help="Agent slugs")

    p_first = sub.add_parser("compile-first-50", help="Compile the first 50 alphabetical agents")

    p_run = sub.add_parser("run", help="Run Hermes with a generated profile")
    p_run.add_argument("slug", nargs="?", help="Agent slug")
    p_run.add_argument("--query", help="Optional non-interactive query")
    p_run.add_argument("--route", dest="route_prompt", help="Route this task prompt to the best matching agent and run it")
    p_run.add_argument("--top", type=int, default=3, help="How many ranked matches to consider when routing")
    p_run.add_argument("--all", action="store_true", help="Route across all discovered agents instead of the first 50")
    p_run.add_argument("--delegate", action="store_true", help="Run the selected profile as a delegated Hermes subprocess; use worktree mode automatically inside git repos")

    p_route = sub.add_parser("route", help="Recommend the best matching agent for a task prompt")
    p_route.add_argument("prompt", help="Task prompt to route")
    p_route.add_argument("--top", type=int, default=3, help="How many ranked matches to return")
    p_route.add_argument("--all", action="store_true", help="Route across all discovered agents instead of the first 50")

    p_install = sub.add_parser("install-launchers", help="Install agent-list/agent-compile/agent-run wrappers")
    p_install.add_argument(
        "--wrapper-dir",
        default=str(Path.home() / ".local" / "bin"),
        help="Directory to write launcher wrappers into",
    )

    return ap.parse_args()


def main() -> int:
    args = parse_args()
    if args.cmd == "list":
        for p in discover_agents():
            print(p.name)
        return 0
    if args.cmd == "compile":
        lookup = {p.name: p for p in discover_agents()}
        missing = [slug for slug in args.slugs if slug not in lookup]
        if missing:
            raise SystemExit(f"Unknown slugs: {', '.join(missing)}")
        written = compile_selected([lookup[s] for s in args.slugs])
        print(json.dumps({"compiled": written}, indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "compile-first-50":
        selected = first_target_agents()
        written = compile_selected(selected)
        print(json.dumps({"compiled_count": len(written), "last_slug": selected[-1].name if selected else None}, indent=2))
        return 0
    if args.cmd == "run":
        if args.route_prompt:
            return run_routed_profile(
                args.route_prompt,
                query=args.query,
                top_n=args.top,
                limit_to_first_50=not args.all,
                delegated=args.delegate,
            )
        if not args.slug:
            raise SystemExit("run requires either a slug or --route")
        return run_profile(args.slug, args.query, delegated=args.delegate)
    if args.cmd == "route":
        ranked = route_agents(args.prompt, top_n=args.top, limit_to_first_50=not args.all)
        print(json.dumps({"prompt": args.prompt, "matches": ranked}, indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "install-launchers":
        written = install_launchers(Path(args.wrapper_dir))
        print(json.dumps({"installed": [str(p) for p in written]}, indent=2))
        return 0
    raise SystemExit(1)


if __name__ == "__main__":
    raise SystemExit(main())
