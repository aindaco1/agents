from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


codex_sync = load_module("sync_codex_skills", ROOT / "scripts" / "sync_codex_skills.py")
portable_sync = load_module(
    "sync_portable_skills", ROOT / "scripts" / "sync_portable_skills.py"
)


def test_repo_portable_skills_are_cross_compatible():
    skills = portable_sync.discover_portable_skills(ROOT)
    names = {skill.name for skill in skills}

    assert names == {
        "anti-machine-writing-editorial-pass",
        "constrained-humanization-editing",
        "desktop-app-updater-release-validation",
        "humanizer",
        "iterative-ai-detector-humanization",
        "macos-dmg-release-validation",
        "web-application-builder",
    }
    for skill in skills:
        frontmatter = portable_sync.validate_skill_dir(skill.source, skill.category)
        related = frontmatter.metadata["hermes"]["related_skills"]
        assert set(related) <= names


def test_portable_skill_profile_links_match_aggregate_roster():
    aggregate = {
        entry["role_id"]: entry
        for entry in json.loads((ROOT / "roster.json").read_text(encoding="utf-8"))[
            "agents"
        ]
    }
    expected_links = {
        "web-application-builder": ["web-application-builder"],
        "desktop-application-builder": [
            "desktop-app-updater-release-validation",
            "macos-dmg-release-validation",
        ],
        "devops-engineer": [
            "desktop-app-updater-release-validation",
            "macos-dmg-release-validation",
        ],
    }
    for slug, skills in expected_links.items():
        profile = json.loads(
            (ROOT / slug / "roster_entry.json").read_text(encoding="utf-8")
        )
        assert profile == aggregate[slug]
        assert profile["hermes_skills"] == skills

    for slug in (
        "desktop-application-builder",
        "product-marketing-docs-builder",
        "mac-app-licensing-engineer",
    ):
        profile = json.loads(
            (ROOT / slug / "roster_entry.json").read_text(encoding="utf-8")
        )
        assert profile == aggregate[slug]
        assert f"${slug}" in profile["codex_interface"]["default_prompt"]


def test_portable_skill_sync_round_trip(tmp_path: Path):
    skill = next(
        skill
        for skill in portable_sync.discover_portable_skills(ROOT)
        if skill.name == "desktop-app-updater-release-validation"
    )
    destination = tmp_path / "skills" / skill.name

    assert portable_sync.sync_package(skill, destination, check=False) == "created"
    assert portable_sync.sync_package(skill, destination, check=True) == "unchanged"
    assert (destination / "SKILL.md").read_bytes() == (
        skill.source / "SKILL.md"
    ).read_bytes()
    assert (destination / "agents" / "openai.yaml").is_file()


def test_portable_skill_rejects_codex_incompatible_frontmatter(tmp_path: Path):
    skill_dir = tmp_path / "software-development" / "bad-skill"
    (skill_dir / "agents").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: bad-skill\n"
        'description: "Use when testing a bad skill."\n'
        'author: "Top-level author is not portable"\n'
        "metadata:\n"
        "  hermes:\n"
        "    tags: [test]\n"
        "    related_skills: []\n"
        "---\n\n"
        "# Bad Skill\n",
        encoding="utf-8",
    )
    (skill_dir / "agents" / "openai.yaml").write_text(
        "interface:\n"
        '  display_name: "Bad Skill"\n'
        '  short_description: "Test an intentionally invalid skill"\n'
        '  default_prompt: "Use $bad-skill to test."\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Codex-incompatible frontmatter"):
        portable_sync.validate_skill_dir(skill_dir, "software-development")


def test_codex_interface_overrides_generated_ui_metadata():
    entry = {
        "role_id": "desktop-application-builder",
        "role_name": "Desktop Application Builder",
        "codex_interface": {
            "display_name": "Desktop Application Builder",
            "short_description": "Build complete cross-platform desktop apps",
            "default_prompt": (
                "Use $desktop-application-builder to build a desktop app."
            ),
        },
    }

    generated = codex_sync.default_openai_yaml(entry)

    assert 'default_prompt: "Use $desktop-application-builder' in generated
    assert "Build complete cross-platform desktop apps" in generated


def test_codex_interface_requires_explicit_skill_invocation():
    entry = {
        "role_id": "desktop-application-builder",
        "role_name": "Desktop Application Builder",
        "codex_interface": {
            "display_name": "Desktop Application Builder",
            "short_description": "Build complete cross-platform desktop apps",
            "default_prompt": "Build a desktop app.",
        },
    }

    with pytest.raises(SystemExit, match=r"must mention \$desktop-application-builder"):
        codex_sync.default_openai_yaml(entry)


def test_codex_sync_repairs_missing_ui_metadata(tmp_path: Path):
    repo = tmp_path / "repo"
    destination = tmp_path / "codex-skills"
    profile = repo / "test-agent"
    profile.mkdir(parents=True)
    entry = {
        "role_id": "test-agent",
        "slug": "test-agent",
        "display_name": "Test Agent",
        "role_name": "Test Agent",
        "emoji": "🧪",
        "tagline": "Exercises the skill synchronizer",
        "skills": [],
        "avoid_for": [],
        "handoff_rules": {"delegate_to": []},
        "codex_interface": {
            "display_name": "Test Agent",
            "short_description": "Exercise Codex skill synchronization",
            "default_prompt": "Use $test-agent to exercise this test task.",
        },
    }
    (repo / "roster.json").write_text(
        json.dumps({"agents": [entry]}), encoding="utf-8"
    )
    (profile / "IDENTITY_SUMMARY.md").write_text(
        "# Test Agent\n\nCompact identity.", encoding="utf-8"
    )
    (profile / "IDENTITY.md").write_text(
        "# Test Agent\n\nFull identity.", encoding="utf-8"
    )
    (profile / "roster_entry.json").write_text(
        json.dumps(entry), encoding="utf-8"
    )

    skill_dir = destination / "test-agent"
    skill_dir.mkdir(parents=True)
    skill_content = (
        codex_sync.build_frontmatter(entry)
        + "\n"
        + codex_sync.build_body(repo, entry)
    )
    (skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")

    command = [
        sys.executable,
        str(ROOT / "scripts" / "sync_codex_skills.py"),
        "--repo",
        str(repo),
        "--dest",
        str(destination),
    ]
    synced = subprocess.run(command, text=True, capture_output=True, check=False)
    assert synced.returncode == 0, synced.stderr
    metadata = (skill_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "Use $test-agent" in metadata

    checked = subprocess.run(
        command + ["--check"], text=True, capture_output=True, check=False
    )
    assert checked.returncode == 0, checked.stdout + checked.stderr
