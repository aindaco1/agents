from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "hermes_agent_roster.py"
spec = importlib.util.spec_from_file_location("hermes_agent_roster", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(module)


def test_first_target_agents_stops_at_data_ai_ml_generalist():
    selected = module.first_target_agents()
    discovered = module.discover_agents()
    sentinel_index = next(i for i, path in enumerate(discovered) if path.name == "data-ai-ml-generalist")

    assert selected == discovered[: sentinel_index + 1]
    assert selected[-1].name == "data-ai-ml-generalist"


def test_install_launchers_writes_expected_wrappers(tmp_path: Path):
    wrapper_dir = tmp_path / "bin"
    script_path = Path("/tmp/fake_roster.py")

    written = module.install_launchers(wrapper_dir=wrapper_dir, script_path=script_path)

    assert sorted(p.name for p in written) == ["agent-compile", "agent-list", "agent-route", "agent-run"]
    run_wrapper = wrapper_dir / "agent-run"
    compile_wrapper = wrapper_dir / "agent-compile"

    assert run_wrapper.exists()
    assert compile_wrapper.exists()
    assert run_wrapper.stat().st_mode & 0o111
    assert compile_wrapper.stat().st_mode & 0o111
    assert str(script_path) in run_wrapper.read_text(encoding="utf-8")
    assert "run \"$@\"" in run_wrapper.read_text(encoding="utf-8")
    assert "compile \"$@\"" in compile_wrapper.read_text(encoding="utf-8")


def test_select_profile_runtime_uses_openai_recommendation_and_prefers_anthropic_fallback():
    base_cfg = {
        "model": {"provider": "openai-codex", "default": "gpt-5.4"},
        "fallback_providers": [{"provider": "gemini", "model": "gemma-3-27b-it"}],
    }
    entry = {
        "model_recommendations": {
            "openai": {"model": "gpt-5.4-mini", "reasoning": "medium"},
            "anthropic": {"model": "claude-sonnet-4-6", "thinking": "medium"},
            "google": {"model": "gemini-2.5-pro", "thinking": "enabled"},
        },
        "model_behavior_hints": {"reasoning_effort": "high"},
    }

    runtime = module.select_profile_runtime(entry, base_cfg)

    assert runtime["provider"] == "openai-codex"
    assert runtime["model"] == "gpt-5.4-mini"
    assert runtime["reasoning_effort"] == "medium"
    assert runtime["fallback_providers"][0]["provider"] == "anthropic"
    assert runtime["fallback_providers"][0]["model"] == "claude-sonnet-4-6"
    assert not any(item["provider"] == "gemini" for item in runtime["fallback_providers"])


def test_build_agent_context_contains_sharper_sections():
    entry = {
        "display_name": "Test Agent",
        "role_name": "Workflow Designer",
        "tagline": "Designs systems that reduce chaos.",
        "category": "operations",
        "subcategory": "design",
        "identity_summary": "A concise identity summary.",
        "invocation_hints": ["Use for workflow design.", "Use for routing logic."],
        "avoid_for": ["Do not use for deep legal review."],
        "handoff_rules": {"delegate_to": [{"role_id": "chief-of-staff", "when": "Need leadership triage."}]},
        "skills": ["Workflow mapping", "Triage system design"],
    }
    identity_md = "# Test Agent\n\n## Working Style\n\nClear and operational."

    text = module.build_agent_context(entry, "A concise identity summary.", identity_md)

    assert "## Best Fit" in text
    assert "## Poor Fit" in text
    assert "## Handoff Rules" in text
    assert "## Default Output Expectations" in text
    assert "## Preferred Hermes Skills" in text
    assert "## Discouraged Hermes Skills" in text
    assert "Use for workflow design." in text
    assert "Do not use for deep legal review." in text


def test_infer_skill_guidance_for_content_strategy_profile():
    entry = {
        "role_name": "Content Strategist",
        "category": "marketing",
        "subcategory": "strategy",
        "slug": "content-strategist",
    }
    guidance = module.infer_skill_guidance(entry)
    assert "notion" in guidance["preferred"]
    assert "writing-plans" in guidance["discouraged"]
    assert "plan" in guidance["discouraged"]


def test_infer_skill_guidance_includes_explicit_roster_skills():
    entry = {
        "role_name": "Mac App Licensing Engineer",
        "category": "engineering",
        "subcategory": "macos-payments",
        "slug": "mac-app-licensing-engineer",
        "hermes_skills": ["mac-app-direct-licensing"],
    }

    guidance = module.infer_skill_guidance(entry)

    assert "mac-app-direct-licensing" in guidance["preferred"]


def test_route_prompt_prefers_chief_of_staff_for_planning_and_delegation_prompt():
    entries = [
        {
            "slug": "chief-of-staff",
            "role_name": "Chief of Staff",
            "category": "operations",
            "invocation_hints": ["Use for prioritization, sequencing, and delegation."],
            "skills": ["prioritization", "delegation"],
        },
        {
            "slug": "backend-architect",
            "role_name": "Backend Architect",
            "category": "engineering",
            "invocation_hints": ["Use for API, system design, and infrastructure decisions."],
            "skills": ["backend systems", "architecture"],
        },
    ]

    ranked = module.route_prompt("I need help prioritizing this week, sequencing work, and deciding what to delegate.", entries, top_n=2)

    assert ranked[0]["slug"] == "chief-of-staff"
    assert ranked[0]["score"] > ranked[1]["score"]


def test_route_prompt_prefers_backend_architect_for_api_system_design_prompt():
    entries = [
        {
            "slug": "chief-of-staff",
            "role_name": "Chief of Staff",
            "category": "operations",
            "invocation_hints": ["Use for prioritization, sequencing, and delegation."],
            "skills": ["prioritization", "delegation"],
        },
        {
            "slug": "backend-architect",
            "role_name": "Backend Architect",
            "category": "engineering",
            "invocation_hints": ["Use for API, system design, and infrastructure decisions."],
            "skills": ["backend systems", "architecture"],
        },
    ]

    ranked = module.route_prompt("Design an API and backend architecture for a lightweight workflow service.", entries, top_n=2)

    assert ranked[0]["slug"] == "backend-architect"
    assert ranked[0]["score"] > ranked[1]["score"]


def test_in_git_repo_returns_false_when_git_is_unavailable(monkeypatch):
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module.in_git_repo() is False


def test_build_run_command_uses_worktree_for_delegated_runs_inside_git_repo(monkeypatch):
    monkeypatch.setattr(module, "in_git_repo", lambda cwd=None: True)

    cmd = module.build_run_command("chief-of-staff", "Start with the top 3 priorities", delegated=True)

    assert cmd == ["hermes", "-w", "-p", "chief-of-staff", "chat", "-q", "Start with the top 3 priorities"]


def test_build_run_command_skips_worktree_for_delegated_runs_outside_git_repo(monkeypatch):
    monkeypatch.setattr(module, "in_git_repo", lambda cwd=None: False)

    cmd = module.build_run_command("chief-of-staff", "Start with the top 3 priorities", delegated=True)

    assert cmd == ["hermes", "-p", "chief-of-staff", "chat", "-q", "Start with the top 3 priorities"]


def test_run_profile_uses_delegated_command(monkeypatch):
    called = []

    def fake_call(cmd):
        called.append(cmd)
        return 0

    monkeypatch.setattr(module, "in_git_repo", lambda cwd=None: True)
    monkeypatch.setattr(module.subprocess, "call", fake_call)

    result = module.run_profile("chief-of-staff", "Start with the top 3 priorities", delegated=True)

    assert result == 0
    assert called == [["hermes", "-w", "-p", "chief-of-staff", "chat", "-q", "Start with the top 3 priorities"]]


def test_run_routed_profile_executes_top_match(monkeypatch):
    calls = []

    def fake_route_agents(prompt: str, top_n: int = 3, limit_to_first_50: bool = True):
        assert prompt == "Plan my week and tell me what to delegate"
        assert top_n == 3
        assert limit_to_first_50 is True
        return [
            {"slug": "chief-of-staff", "score": 20},
            {"slug": "account-manager", "score": 8},
        ]

    def fake_run_profile(slug: str, query: str | None, delegated: bool = False):
        calls.append((slug, query, delegated))
        return 0

    monkeypatch.setattr(module, "route_agents", fake_route_agents)
    monkeypatch.setattr(module, "run_profile", fake_run_profile)

    result = module.run_routed_profile("Plan my week and tell me what to delegate", query="Start with the top 3 priorities", delegated=True)

    assert result == 0
    assert calls == [("chief-of-staff", "Start with the top 3 priorities", True)]


def test_run_routed_profile_uses_prompt_as_query_when_query_is_missing(monkeypatch):
    calls = []

    monkeypatch.setattr(module, "route_agents", lambda prompt, top_n=3, limit_to_first_50=True: [{"slug": "chief-of-staff", "score": 20}])

    def fake_run_profile(slug: str, query: str | None, delegated: bool = False):
        calls.append((slug, query, delegated))
        return 0

    monkeypatch.setattr(module, "run_profile", fake_run_profile)

    result = module.run_routed_profile("Plan my week and tell me what to delegate", delegated=True)

    assert result == 0
    assert calls == [("chief-of-staff", "Plan my week and tell me what to delegate", True)]


def test_run_routed_profile_raises_when_no_matches(monkeypatch):
    monkeypatch.setattr(module, "route_agents", lambda prompt, top_n=3, limit_to_first_50=True: [])

    try:
        module.run_routed_profile("Unrouteable task")
    except SystemExit as exc:
        assert "No matching agent found" in str(exc)
    else:
        raise AssertionError("Expected SystemExit when no matches are returned")
