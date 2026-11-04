import json
from pathlib import Path
import sys
import subprocess

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import isolate_hermes_skills as isolate


def fixture(tmp_path):
    home = tmp_path / "hermes"
    source = home / "skills/testing/shared"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("---\nname: shared\ndescription: Test\n---\nA shared procedure\n")
    (source / "helper.txt").write_text("support file")
    profile = home / "profiles/test-agent"
    profile.mkdir(parents=True)
    config = b"# preserve comment\nmodel:\n  default: custom\nskills:\n  external_dirs: []\n  write_approval: false\nunknown: 47\n"
    (profile / "config.yaml").write_bytes(config)
    (profile / "skills").symlink_to(home / "skills")
    (profile / "memories").mkdir()
    (profile / "memories/MEMORY.md").write_bytes(b"Keep learned fact")
    return home, source, profile, config


def test_isolation_preserves_settings_memory_and_shared_content_then_restores(tmp_path):
    home, source, profile, config = fixture(tmp_path)
    plan, _, _ = isolate.preview(home, "test-agent")
    assert (profile / "config.yaml").read_bytes() == config
    assert not (home / "skill-releases").exists()
    result = isolate.apply(home, "test-agent", plan["plan_hash"])
    release = Path(result["release"])
    assert (release / "testing/shared/SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes()
    assert (profile / "skills").resolve() == profile / "skills.local"
    (profile / "skills/private").mkdir()
    (profile / "skills/private/SKILL.md").write_text("private learning")
    after = yaml.safe_load((profile / "config.yaml").read_bytes())
    before = yaml.safe_load(config)
    after["skills"]["external_dirs"] = before["skills"]["external_dirs"]
    assert after == before
    assert (profile / "memories/MEMORY.md").read_bytes() == b"Keep learned fact"
    assert json.loads((profile / "skills/.usage.json").read_text())["shared"]["locked"]
    isolate.restore(home, "test-agent")
    assert (profile / "config.yaml").read_bytes() == config
    assert (profile / "skills").resolve() == home / "skills"
    assert (profile / "skills.local/private/SKILL.md").read_text() == "private learning"


def test_changed_config_refuses_stale_isolation_and_preserves_newer_restore_settings(tmp_path):
    home, source, profile, config = fixture(tmp_path)
    plan, _, _ = isolate.preview(home, "test-agent")
    (profile / "config.yaml").write_bytes(config + b"new_setting: keep\n")
    with pytest.raises(ValueError, match="Stale"):
        isolate.apply(home, "test-agent", plan["plan_hash"])
    plan, _, _ = isolate.preview(home, "test-agent")
    isolate.apply(home, "test-agent", plan["plan_hash"])
    with (profile / "config.yaml").open("ab") as handle:
        handle.write(b"later_setting: keep\n")
    with pytest.raises(ValueError, match="newer"):
        isolate.restore(home, "test-agent")


def test_interrupted_link_switch_recovers_without_touching_learning(tmp_path, monkeypatch):
    home, source, profile, config = fixture(tmp_path)
    plan, _, _ = isolate.preview(home, "test-agent")
    original = isolate.switch_link
    monkeypatch.setattr(isolate, "switch_link", lambda *a: (_ for _ in ()).throw(OSError("interrupted")))
    with pytest.raises(OSError):
        isolate.apply(home, "test-agent", plan["plan_hash"])
    monkeypatch.setattr(isolate, "switch_link", original)
    isolate.restore(home, "test-agent")
    assert (profile / "config.yaml").read_bytes() == config
    assert (profile / "memories/MEMORY.md").read_bytes() == b"Keep learned fact"


def test_existing_private_directory_is_not_replaced(tmp_path):
    home, _, profile, _ = fixture(tmp_path)
    (profile / "skills").unlink()
    (profile / "skills").mkdir()
    (profile / "skills/keep.txt").write_text("keep")
    with pytest.raises(ValueError, match="private libraries"):
        isolate.preview(home, "test-agent")
    assert (profile / "skills/keep.txt").read_text() == "keep"


def test_snapshot_keeps_helpers_executable_and_detects_permission_drift(tmp_path):
    home, source, profile, config = fixture(tmp_path)
    helper = source / "helper.sh"
    helper.write_text("#!/bin/sh\nprintf 'helper works'\n")
    helper.chmod(0o755)
    plan, _, _ = isolate.preview(home, "test-agent")
    result = isolate.apply(home, "test-agent", plan["plan_hash"])
    published = Path(result["release"]) / "testing/shared/helper.sh"
    assert published.stat().st_mode & 0o777 == 0o555
    assert subprocess.check_output([str(published)], text=True) == "helper works"
    published.chmod(0o444)
    with pytest.raises(ValueError, match="permissions have drifted"):
        isolate.create_release(home, plan, isolate.inventory(home / "skills")[0])
