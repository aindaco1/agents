from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "sync_roster_aggregate.py"
spec = importlib.util.spec_from_file_location("sync_roster_aggregate", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
sys.modules["sync_roster_aggregate"] = module
spec.loader.exec_module(module)


CURATED_WRITING_PAIRS = {
    "vomit-draft-essay-co-writer": {
        "academic-researcher",
        "academic-writer",
        "blog-writer",
        "brand-voice-manager",
        "competitive-intelligence-analyst",
        "content-generalist",
        "content-strategist",
        "copywriter",
        "creative-writer",
        "data-researcher",
        "editor",
        "ghostwriter",
        "grant-writer",
        "investigative-researcher",
        "linkedin-content-creator",
        "market-researcher",
        "newsletter-writer",
        "podcast-producer",
        "pr-writer",
        "product-director",
        "product-manager",
        "product-marketing-manager",
        "proposal-writer",
        "research-analyst",
        "research-director",
        "research-generalist",
        "strategy-consultant",
        "tiktok-reels-strategist",
        "trend-analyst",
        "twitter-x-strategist",
        "writing-generalist",
        "youtube-content-planner",
    },
    "batty-replic-humanization-editor": {
        "academic-writer",
        "blog-writer",
        "brand-voice-manager",
        "changelog-writer",
        "content-generalist",
        "content-strategist",
        "copywriter",
        "creative-writer",
        "discord-manager",
        "editor",
        "ghostwriter",
        "grant-writer",
        "linkedin-content-creator",
        "localization-specialist",
        "marketing-generalist",
        "meme-humor-writer",
        "newsletter-curator",
        "newsletter-writer",
        "performance-review-writer",
        "podcast-producer",
        "pr-writer",
        "product-marketing-manager",
        "proposal-writer",
        "reddit-community-manager",
        "resume-cv-writer",
        "seo-specialist",
        "social-community-generalist",
        "social-media-manager",
        "technical-writer",
        "tiktok-reels-strategist",
        "twitter-x-strategist",
        "vomit-draft-essay-co-writer",
        "writing-generalist",
        "youtube-content-planner",
    },
    "enheduanna-screenwriting-assistant": {
        "creative-writer",
        "editor",
        "ghostwriter",
        "writing-generalist",
    },
}

CURATED_WRITING_HANDOFFS = {
    "vomit-draft-essay-co-writer": {
        "academic-writer",
        "blog-writer",
        "brand-voice-manager",
        "content-generalist",
        "content-strategist",
        "copywriter",
        "creative-writer",
        "editor",
        "ghostwriter",
        "grant-writer",
        "linkedin-content-creator",
        "newsletter-writer",
        "podcast-producer",
        "pr-writer",
        "product-director",
        "research-analyst",
        "tiktok-reels-strategist",
        "twitter-x-strategist",
        "writing-generalist",
        "youtube-content-planner",
    },
    "batty-replic-humanization-editor": CURATED_WRITING_PAIRS[
        "batty-replic-humanization-editor"
    ],
    "enheduanna-screenwriting-assistant": CURATED_WRITING_PAIRS[
        "enheduanna-screenwriting-assistant"
    ],
}


def load_profile_entries() -> dict[str, dict]:
    return module.discover_profile_entries(ROOT)


def test_repo_aggregate_matches_all_canonical_profile_entries():
    current = module.load_json_object(ROOT / "roster.json")
    entries = load_profile_entries()

    assert module.build_expected_roster(current, entries) == current


def test_legacy_writing_relationships_are_limited_to_curated_profiles():
    entries = load_profile_entries()

    for target, expected_profiles in CURATED_WRITING_PAIRS.items():
        actual_profiles = {
            role_id
            for role_id, entry in entries.items()
            if target in entry.get("pairs_well_with", [])
        }
        assert actual_profiles == expected_profiles

    for target, expected_profiles in CURATED_WRITING_HANDOFFS.items():
        actual_profiles = {
            role_id
            for role_id, entry in entries.items()
            if target
            in {
                item["role_id"]
                for item in (entry.get("handoff_rules") or {}).get(
                    "delegate_to", []
                )
            }
        }
        assert actual_profiles == expected_profiles


def test_build_expected_roster_preserves_catalog_order():
    current = {
        "generated": "2026-01-01",
        "total_agents": 2,
        "gender_distribution": {},
        "agents": [
            {"role_id": "second", "pronouns": "they/them", "old": True},
            {"role_id": "first", "pronouns": "she/her", "old": True},
        ],
    }
    entries = {
        "first": {"role_id": "first", "pronouns": "she/her"},
        "second": {"role_id": "second", "pronouns": "they/them"},
    }

    expected = module.build_expected_roster(current, entries)

    assert [entry["role_id"] for entry in expected["agents"]] == [
        "second",
        "first",
    ]
    assert expected["generated"] == "2026-01-01"
    assert expected["gender_distribution"] == {
        "he_him": 0,
        "she_her": 1,
        "they_them": 1,
    }


def test_codex_loader_reads_canonical_profile_entries(tmp_path: Path):
    profile_dir = tmp_path / "test-agent"
    profile_dir.mkdir()
    entry = {"role_id": "test-agent", "skills": ["canonical capability"]}
    (profile_dir / "roster_entry.json").write_text(
        json.dumps(entry), encoding="utf-8"
    )
    (tmp_path / "roster.json").write_text(
        json.dumps({"agents": [{"role_id": "test-agent", "skills": []}]}),
        encoding="utf-8",
    )

    codex_path = ROOT / "scripts" / "sync_codex_skills.py"
    codex_spec = importlib.util.spec_from_file_location("codex_roster_loader", codex_path)
    codex_module = importlib.util.module_from_spec(codex_spec)
    assert codex_spec is not None and codex_spec.loader is not None
    codex_spec.loader.exec_module(codex_module)

    assert codex_module.load_roster(tmp_path) == [entry]
