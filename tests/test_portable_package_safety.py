from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sync_portable_skills.py"
spec = importlib.util.spec_from_file_location("portable_package_safety_sync", SCRIPT)
assert spec is not None and spec.loader is not None
portable_sync = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = portable_sync
spec.loader.exec_module(portable_sync)


def make_skill(repo: Path, name: str = "safe-package"):
    source = repo / "skills" / "testing" / name
    (source / "agents").mkdir(parents=True)
    (source / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        'description: "Use when testing portable package safety."\n'
        "metadata:\n"
        "  hermes:\n"
        "    tags: [testing]\n"
        "    related_skills: []\n"
        "---\n\n"
        "# Safe package\n",
        encoding="utf-8",
    )
    (source / "agents" / "openai.yaml").write_text(
        "interface:\n"
        '  display_name: "Safe package"\n'
        '  short_description: "Test portable package synchronization"\n'
        f'  default_prompt: "Use ${name} for package safety tests."\n',
        encoding="utf-8",
    )
    return portable_sync.validate_skill_dir(source, "testing")


def test_pytest_ignores_conflict_copies_but_collects_legitimate_numbered_tests(tmp_path: Path):
    conftest = ROOT / "tests" / "conftest.py"
    if conftest.exists():
        (tmp_path / "conftest.py").write_bytes(conftest.read_bytes())
    legitimate = ["test_real.py", "test_v2.py", "test_chapter 2 notes.py"]
    conflicts = ["test_real 2.py", "test_real 123.py"]
    for name in legitimate:
        (tmp_path / name).write_text("def test_real():\n    assert True\n", encoding="utf-8")
    for name in conflicts:
        (tmp_path / name).write_text("raise RuntimeError('Conflict copies must not execute')\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(tmp_path)],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "3 passed" in result.stdout
    for name in conflicts:
        assert (tmp_path / name).read_text(encoding="utf-8") == (
            "raise RuntimeError('Conflict copies must not execute')\n"
        )


def test_sync_excludes_conflict_filenames_without_ignoring_digits(tmp_path: Path):
    skill = make_skill(tmp_path / "repo")
    conflicts = {
        "SKILL 2.md",
        "agents/openai 10.yaml",
        "references/nested/guide 123.md",
    }
    legitimate = {
        "references/guide2.md",
        "references/guide-v2.md",
        "references/02-guide.md",
        "references/3d-model.md",
        "references/chapter 2 notes.md",
    }
    for relative in conflicts | legitimate:
        path = skill.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"Content for {relative}\n", encoding="utf-8")

    expected = {Path(name) for name in legitimate | {"SKILL.md", "agents/openai.yaml"}}
    inventory = portable_sync.package_files(skill)
    assert set(inventory) == expected

    destination = tmp_path / "destination"
    assert portable_sync.sync_package(skill, destination, check=False) == "created"
    actual = {
        path.relative_to(destination): path.read_bytes()
        for path in destination.rglob("*")
        if path.is_file()
    }
    assert actual == inventory
    assert portable_sync.sync_package(skill, destination, check=True) == "unchanged"
    for relative in conflicts:
        assert (skill.source / relative).read_text(encoding="utf-8") == (
            f"Content for {relative}\n"
        )


def cli_command(repo: Path, destinations: Path) -> list[str]:
    return [
        sys.executable,
        str(SCRIPT),
        "--repo", str(repo),
        "--codex-dest", str(destinations / "codex"),
        "--hermes-dest", str(destinations / "hermes"),
        "--target", "both",
    ]


def snapshot(root: Path) -> dict[Path, bytes | None]:
    return {
        path.relative_to(root): path.read_bytes() if path.is_file() else None
        for path in root.rglob("*")
    }


@pytest.mark.parametrize(
    "selected",
    [("second-package",), ("second-package", "first-package", "second-package")],
)
def test_cli_syncs_only_selected_skills(tmp_path: Path, selected: tuple[str, ...]):
    repo = tmp_path / "repo"
    skills = [
        make_skill(repo, name)
        for name in ("first-package", "second-package", "unselected-package")
    ]
    destinations = tmp_path / "destinations"
    for runtime in ("codex", "hermes/testing"):
        root = destinations / runtime
        (root / "unselected-package").mkdir(parents=True)
        (root / "unselected-package" / "SKILL.md").write_bytes(b"Keep old package")
        (root / "second-package").mkdir()
        (root / "second-package" / "extra.txt").write_bytes(b"Keep destination extra")
        (root / "second-package" / "SKILL 2.md").write_bytes(b"Keep existing conflict")
    before = snapshot(destinations)
    command = cli_command(repo, destinations)
    for name in selected:
        command.extend(["--skill", name])

    checked = subprocess.run(command + ["--check"], capture_output=True, text=True)
    assert checked.returncode == 1, checked.stdout + checked.stderr
    assert f"skills={len(set(selected))}, target=both" in checked.stdout
    assert snapshot(destinations) == before

    synced = subprocess.run(command, capture_output=True, text=True)
    assert synced.returncode == 0, synced.stdout + synced.stderr
    assert f"skills={len(set(selected))}, target=both" in synced.stdout
    expected = dict(before)
    for skill in skills:
        if skill.name not in selected:
            continue
        for runtime in ("codex", "hermes/testing"):
            target = Path(runtime) / skill.name
            expected[target] = None
            for rel, content in portable_sync.package_files(skill).items():
                expected[target / rel] = content
                for parent in rel.parents:
                    expected[target / parent] = None
    assert snapshot(destinations) == expected

    checked = subprocess.run(command + ["--check"], capture_output=True, text=True)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert "created=0, updated=0" in checked.stdout
    assert snapshot(destinations) == expected


@pytest.mark.parametrize("check", [False, True])
@pytest.mark.parametrize("existing_destination", [False, True])
def test_cli_rejects_unknown_names_before_any_writes(
    tmp_path: Path, check: bool, existing_destination: bool
):
    repo = tmp_path / "repo"
    make_skill(repo, "known-package")
    destinations = tmp_path / "destinations"
    if existing_destination:
        existing = destinations / "codex" / "known-package"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_bytes(b"Must not update this file")
        (existing / "extra.txt").write_bytes(b"Must not delete this file")
    before = snapshot(destinations)
    command = cli_command(repo, destinations) + [
        "--skill", "known-package",
        "--skill", "missing-package",
        "--skill", "other-missing-package",
    ]
    if check:
        command.append("--check")

    result = subprocess.run(command, capture_output=True, text=True)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "Unknown portable skill name(s): missing-package, other-missing-package" in (
        result.stderr
    )
    assert result.stdout == ""
    assert snapshot(destinations) == before
    assert destinations.exists() == existing_destination
