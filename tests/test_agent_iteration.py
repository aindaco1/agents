"""Behavioral checks for the shipped workflow helper, without network or agents."""

import importlib.util
import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest


HELPER = Path(__file__).resolve().parents[1] / (
    "skills/software-development/build-iterated-agentic-loop/"
    "references/agent-iteration.py"
)
spec = importlib.util.spec_from_file_location("agent_iteration", HELPER)
iteration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(iteration)


def fixtures():
    event = {
        "action": "created",
        "issue": {"number": 17, "pull_request": {}},
        "comment": {"body": "/iterate Keep nullable state", "user": {"login": "maintainer"}},
    }
    event["issue"]["pull_request"] = {"url": "https://api.github.com/repos/org/repo/pulls/17"}
    pr = {
        "number": 17, "state": "open", "user": {"login": "github-actions[bot]"},
        "head": {"ref": "agent/types/123-1", "sha": "a" * 40, "repo": {"full_name": "org/repo"}},
        "base": {"ref": "main"}, "labels": [{"name": "agent-types"}],
        "body": iteration.marker("agent-types"),
    }
    return event, pr


def run_gate(event, pr, permission="write", event_name="issue_comment"):
    def api(endpoint, paginate=False):
        if endpoint.endswith("/permission"):
            return {"permission": permission}
        return [pr] if paginate else pr
    return iteration.gate(event, event_name, "org/repo", "agent-types",
                          "agent-types", "agent/types", "main", api)


def test_iteration_reuses_verified_branch_and_sha():
    event, pr = fixtures()
    assert run_gate(event, pr) == {
        "run": True, "number": 17, "branch": "agent/types/123-1", "sha": "a" * 40,
    }


@pytest.mark.parametrize("permission", ["read", "triage", "none"])
def test_marker_does_not_authorize_a_commenter(permission):
    event, pr = fixtures()
    assert run_gate(event, pr, permission) == {"run": False}


@pytest.mark.parametrize("path,value", [
    (("state",), "closed"),
    (("user", "login"), "someone-else"),
    (("head", "repo", "full_name"), "fork/repo"),
    (("head", "repo"), None),
    (("head", "sha"), "not-a-sha"),
    (("head", "ref"), "other-branch"),
    (("head", "ref"), "agent/types/x\ninjected=true"),
    (("base", "ref"), "different-base"),
    (("labels",), []),
    (("body",), "<!-- agent-loop:workflow=other;version=1 -->"),
])
def test_iteration_rejects_wrong_pr(path, value):
    event, pr = fixtures()
    target = pr
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    assert run_gate(event, pr) == {"run": False}


@pytest.mark.parametrize("body", ["/iterate-other fix", "please /iterate", "hello"])
def test_only_exact_iteration_command_routes(body):
    event, pr = fixtures()
    event["comment"]["body"] = body
    assert run_gate(event, pr) == {"run": False}


@pytest.mark.parametrize("event_name", ["schedule", "workflow_dispatch"])
def test_open_pr_bounds_manual_and_scheduled_work(event_name):
    _, pr = fixtures()
    assert run_gate({}, pr, event_name=event_name) == {"run": False}
    pr["labels"] = []
    assert run_gate({}, pr, event_name=event_name) == {"run": True}


def test_only_explicit_manual_override_bypasses_bound():
    _, pr = fixtures()
    event = {"inputs": {"ignore_bound": "true"}}
    assert run_gate(event, pr, event_name="workflow_dispatch") == {"run": True}
    assert run_gate(event, pr, event_name="schedule") == {"run": False}


def test_api_errors_do_not_authorize_work():
    def unavailable(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ["gh", "api"])
    with pytest.raises(subprocess.CalledProcessError):
        iteration.gate({}, "schedule", "org/repo", "agent-types",
                       "agent-types", "agent/types", "main", unavailable)


def test_gh_pagination_uses_arguments_and_flattens_pages(monkeypatch):
    calls = []
    def run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, json.dumps([[{"id": 1}], [{"id": 2}]]))
    monkeypatch.setattr(iteration.subprocess, "run", run)
    assert iteration.gh_json("repos/org/repo/comments?per_page=100", True) == [{"id": 1}, {"id": 2}]
    assert calls[0][0] == ["gh", "api", "repos/org/repo/comments?per_page=100", "--paginate", "--slurp"]
    assert calls[0][1].get("shell", False) is False


def test_feedback_is_literal_and_review_locations_survive():
    event, pr = fixtures()
    event["comment"]["body"] = '/iterate Keep `literal` $(touch /tmp/not-executed) "quotes"\nnext line'
    reviews = [{"path": "src/item.tsx", "line": 5, "body": "check this state"}]
    before = deepcopy(event)
    prompt = iteration.iteration_prompt(event, pr, [], reviews)
    assert '$(touch /tmp/not-executed)' in prompt
    assert '"path": "src/item.tsx"' in prompt
    assert '"line": 5' in prompt
    assert event == before


def test_footer_slug_cannot_inject_markup():
    with pytest.raises(ValueError):
        iteration.marker("x --> injected")
