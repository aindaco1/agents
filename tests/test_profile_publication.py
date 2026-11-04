from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import managed_publication as pub

spec = importlib.util.spec_from_file_location("safe_roster", SCRIPTS / "hermes_agent_roster.py")
roster = importlib.util.module_from_spec(spec)
spec.loader.exec_module(roster)


@pytest.fixture
def setup_profile(tmp_path, monkeypatch):
    source = tmp_path / "source" / "test-agent"
    source.mkdir(parents=True)
    for name in roster.REQUIRED_AGENT_FILES:
        (source / name).write_text("Starter " + name + "\n")
    entry = {"slug": "test-agent", "role_name": "Test Agent"}
    (source / "roster_entry.json").write_text(json.dumps(entry))
    home = tmp_path / "hermes"
    home.mkdir()
    (home / "config.yaml").write_text("model:\n  provider: test\n  default: initial\n")
    (home / "model-map.json").write_text(json.dumps({
        "aliases": {"premium": {"provider": "test", "model": "initial"}}
    }))
    monkeypatch.setattr(roster, "DEFAULT_HERMES_HOME", home)
    monkeypatch.setattr(roster, "PROFILES_ROOT", home / "profiles")
    monkeypatch.setattr(roster, "MODEL_MAP_PATH", home / "model-map.json")
    monkeypatch.setattr(roster, "source_revision", lambda: "test-revision")
    return source, home, home / "profiles" / "test-agent"


def compile_profile(source, **options):
    plan = roster.compile_selected([source], **options)
    return roster.compile_selected([source], apply_hash=plan["plan_hash"], **options)


def snapshot(root):
    return {str(p.relative_to(root)): ("link", os.readlink(p)) if p.is_symlink()
            else ("file", p.read_bytes()) if p.is_file() else ("dir", None)
            for p in root.rglob("*")}


def test_compile_preserves_learned_memory_config_and_private_skills(setup_profile):
    source, home, profile = setup_profile
    compile_profile(source)
    memory = profile / "memories" / "MEMORY.md"
    memory.write_bytes(b"Learned fact: use the verified endpoint.\n")
    user = profile / "memories" / "USER.md"
    user.write_bytes(b"User preference learned after bootstrap.\n")
    config = profile / "config.yaml"
    config.write_bytes(b"# Keep my comment too\nmodel:\n  default: custom\n  provider: custom\nunknown_setting: 42\n")
    skill = profile / "skills" / "my-procedure"
    skill.mkdir()
    (skill / "SKILL.md").write_bytes(b"Private learned procedure")
    before = {p: p.read_bytes() for p in [memory, user, config, skill / "SKILL.md"]}
    (source / "SOUL.md").write_text("Updated persona\n")
    (source / "MEMORY.md").write_text("Changed bootstrap should not erase learning\n")
    compile_profile(source)
    compile_profile(source)
    assert {p: p.read_bytes() for p in before} == before
    assert (profile / "SOUL.md").read_text() == "Updated persona\n"
    assert not (profile / "skills").is_symlink()


def test_preview_is_read_only_and_stale_preview_refuses_before_writes(setup_profile):
    source, home, profile = setup_profile
    before = snapshot(home)
    plan = roster.compile_selected([source])
    assert snapshot(home) == before
    (source / "SOUL.md").write_text("New source after review")
    with pytest.raises(pub.PublicationError, match="Stale compile"):
        roster.compile_selected([source], apply_hash=plan["plan_hash"])
    assert snapshot(home) == before


def test_existing_untracked_generated_files_require_explicit_adoption(setup_profile):
    source, home, profile = setup_profile
    profile.mkdir(parents=True)
    (profile / "SOUL.md").write_text("Legacy runtime persona")
    plan = roster.compile_selected([source])
    with pytest.raises(pub.PublicationError, match="conflict"):
        roster.compile_selected([source], apply_hash=plan["plan_hash"])
    compile_profile(source, adopt_existing=True)
    assert (profile / "SOUL.md").read_bytes() == (source / "SOUL.md").read_bytes()


def test_local_generated_edits_survive_until_upstream_also_changes(setup_profile):
    source, home, profile = setup_profile
    compile_profile(source)
    soul = profile / "SOUL.md"
    soul.write_text("Intentional local persona edit")
    compile_profile(source)
    assert soul.read_text() == "Intentional local persona edit"
    (source / "SOUL.md").write_text("Conflicting upstream persona edit")
    plan = roster.compile_selected([source])
    with pytest.raises(pub.PublicationError, match="conflict"):
        roster.compile_selected([source], apply_hash=plan["plan_hash"])
    assert soul.read_text() == "Intentional local persona edit"


def test_existing_shared_skill_link_is_preserved_until_explicit_migration(setup_profile):
    source, home, profile = setup_profile
    profile.mkdir(parents=True)
    shared = home / "skills"
    shared.mkdir()
    (shared / "keep.txt").write_text("Shared learning")
    (profile / "skills").symlink_to(shared)
    compile_profile(source)
    assert (profile / "skills").is_symlink()
    assert (shared / "keep.txt").read_text() == "Shared learning"


def test_new_profile_can_discover_installed_shared_skills(setup_profile):
    source, home, profile = setup_profile
    shared = home / "skills"
    shared.mkdir()
    (shared / "SKILL.md").write_text("Installed shared procedure")
    compile_profile(source)
    assert (profile / "skills").is_symlink()
    assert (profile / "skills" / "SKILL.md").read_text() == "Installed shared procedure"


@pytest.mark.parametrize("relative", ["SOUL.md", "memories", "config.yaml"])
def test_managed_target_symlinks_refused_without_writes(setup_profile, relative):
    source, home, profile = setup_profile
    profile.mkdir(parents=True)
    outside = home.parent / "outside"
    outside.mkdir()
    (outside / "keep").write_text("Keep")
    (profile / relative).symlink_to(outside)
    before = snapshot(home)
    with pytest.raises(pub.PublicationError, match="Symlink"):
        roster.compile_selected([source])
    assert snapshot(home) == before
    assert (outside / "keep").read_text() == "Keep"


def test_rollback_preserves_memory_learned_after_publication(setup_profile):
    source, home, profile = setup_profile
    compile_profile(source)
    before_soul = (profile / "SOUL.md").read_bytes()
    (source / "SOUL.md").write_text("Second persona")
    result = compile_profile(source)
    memory = profile / "memories" / "MEMORY.md"
    memory.write_text("Learned after publication")
    config = profile / "config.yaml"
    config.write_text("custom: keep\n")
    pub.recover(profile, home / "roster-state" / "test-agent", result["profiles"][0]["transaction"])
    assert (profile / "SOUL.md").read_bytes() == before_soul
    assert memory.read_text() == "Learned after publication"
    assert config.read_text() == "custom: keep\n"


def test_failed_write_restores_previous_generated_files(tmp_path, monkeypatch):
    root, state = tmp_path / "profile", tmp_path / "state"
    files = {"a.md": b"A", "b.md": b"B"}
    plan = pub.preview(root, state, files)
    pub.publish(root, state, files, expected=plan["plan_hash"])
    changed = {"a.md": b"new A", "b.md": b"new B"}
    plan = pub.preview(root, state, changed)
    original = pub.atomic_write
    def fail_once(path, data, mode=0o600):
        if path == root / "b.md" and data == b"new B":
            raise OSError("simulated disk failure")
        original(path, data, mode)
    monkeypatch.setattr(pub, "atomic_write", fail_once)
    with pytest.raises(OSError, match="disk failure"):
        pub.publish(root, state, changed, expected=plan["plan_hash"])
    assert (root / "a.md").read_bytes() == b"A"
    assert (root / "b.md").read_bytes() == b"B"
    assert not (state / "pending.json").exists()


def test_process_crash_is_recoverable_and_cannot_be_silently_republished(tmp_path):
    root, state = tmp_path / "profile", tmp_path / "state"
    files = {"a": b"old A", "b": b"old B"}
    pub.publish(root, state, files, expected=pub.preview(root, state, files)["plan_hash"])
    script = '''
import sys, os
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import managed_publication as p
root, state = Path(sys.argv[2]), Path(sys.argv[3])
files = {"a": b"new A", "b": b"new B"}
plan = p.preview(root, state, files)
original = p.atomic_write
def crash(path, data, mode=0o600):
    original(path, data, mode)
    if path == root / "a": os._exit(71)
p.atomic_write = crash
p.publish(root, state, files, expected=plan["plan_hash"])
'''
    result = subprocess.run([sys.executable, "-c", script, str(SCRIPTS), str(root), str(state)])
    assert result.returncode == 71
    with pytest.raises(pub.PublicationError, match="Interrupted"):
        pub.preview(root, state, files)
    pub.recover(root, state)
    assert (root / "a").read_bytes() == b"old A"
    assert (root / "b").read_bytes() == b"old B"


def test_second_process_cannot_publish_under_active_writer(tmp_path):
    state = tmp_path / "state"
    script = '''
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import managed_publication as p
try:
    with p.writer_lock(Path(sys.argv[2])): pass
except p.PublicationError:
    sys.exit(23)
'''
    with pub.writer_lock(state):
        result = subprocess.run([sys.executable, "-c", script, str(SCRIPTS), str(state)])
    assert result.returncode == 23


def test_stale_destination_and_post_publish_edit_block_overwrite(tmp_path):
    root, state = tmp_path / "profile", tmp_path / "state"
    files = {"a": b"first"}
    result = pub.publish(root, state, files, expected=pub.preview(root, state, files)["plan_hash"])
    plan = pub.preview(root, state, {"a": b"second"})
    (root / "a").write_bytes(b"User edit")
    with pytest.raises(pub.PublicationError, match="Stale"):
        pub.publish(root, state, {"a": b"second"}, expected=plan["plan_hash"])
    with pytest.raises(pub.PublicationError, match="later edit"):
        pub.recover(root, state, result["transaction"])
    assert (root / "a").read_bytes() == b"User edit"
