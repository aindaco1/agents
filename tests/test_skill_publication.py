from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from test_portable_package_safety import make_skill, portable_sync, cli_command


def plan(command):
    result = subprocess.run(command + ["--plan"], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["plan_hash"]


def apply(command):
    result = subprocess.run(command + ["--apply", plan(command)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr


def test_both_runtimes_publish_identical_packages_and_protect_maintained_skills(tmp_path):
    repo, destinations = tmp_path / "repo", tmp_path / "runtime"
    skill = make_skill(repo)
    hermes = destinations / "hermes"
    hermes.mkdir(parents=True)
    usage = {skill.name: {"state": "archived", "use_count": 40}, "unrelated": {"locked": False}}
    (hermes / ".usage.json").write_text(json.dumps(usage))
    command = cli_command(repo, destinations)
    apply(command)
    for rel, data in portable_sync.package_files(skill).items():
        assert (destinations / "codex" / skill.name / rel).read_bytes() == data
        assert (hermes / "testing" / skill.name / rel).read_bytes() == data
    after = json.loads((hermes / ".usage.json").read_text())
    assert after[skill.name]["pinned"] and after[skill.name]["locked"]
    assert after[skill.name]["state"] == "active"
    assert after[skill.name]["use_count"] == 40
    assert after["unrelated"] == usage["unrelated"]


def test_skill_conflict_and_stale_preview_fail_before_either_runtime_changes(tmp_path):
    repo, destinations = tmp_path / "repo", tmp_path / "runtime"
    skill = make_skill(repo)
    command = cli_command(repo, destinations)
    apply(command)
    codex = destinations / "codex" / skill.name / "SKILL.md"
    hermes = destinations / "hermes/testing" / skill.name / "SKILL.md"
    before = hermes.read_bytes()
    token = plan(command)
    codex.write_bytes(before + b"\nIntentional local edit\n")
    stale = subprocess.run(command + ["--apply", token], capture_output=True, text=True)
    assert stale.returncode != 0 and "Stale" in stale.stderr
    (skill.source / "SKILL.md").write_bytes(before + b"\nNew canonical procedure\n")
    conflict = subprocess.run(command + ["--apply", plan(command)], capture_output=True, text=True)
    assert conflict.returncode != 0 and "conflicts" in conflict.stderr
    assert hermes.read_bytes() == before
    assert b"Intentional local edit" in codex.read_bytes()


def test_retired_package_is_not_recreated_and_existing_copy_is_retained(tmp_path):
    repo, destinations = tmp_path / "repo", tmp_path / "runtime"
    skill = make_skill(repo)
    apply(cli_command(repo, destinations))
    (repo / "skills/ownership.json").write_text(json.dumps({"schema": 1, "skills": {skill.name: "retired"}}))
    retained = destinations / "codex" / skill.name / "SKILL.md"
    before = retained.read_bytes()
    fresh = tmp_path / "fresh-runtime"
    apply(cli_command(repo, fresh))
    assert not (fresh / "codex" / skill.name).exists()
    apply(cli_command(repo, destinations))
    assert retained.read_bytes() == before


def test_source_and_destination_symlinks_are_refused(tmp_path):
    skill = make_skill(tmp_path / "repo")
    outside = tmp_path / "outside.txt"
    outside.write_text("Keep outside data")
    (skill.source / "outside.txt").symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        portable_sync.sync_package(skill, tmp_path / "dest", check=False)
    assert outside.read_text() == "Keep outside data"
