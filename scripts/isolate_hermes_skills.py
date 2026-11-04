#!/usr/bin/env python3
"""Pilot private profile skill storage backed by an immutable local shared release."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import managed_publication as pub


def inventory(root: Path) -> tuple[dict[str, bytes], list[str]]:
    pub.safe_path(root)
    files, names = {}, set()
    for skill in sorted(root.rglob("SKILL.md")):
        if any(p.startswith(".") or p == "__pycache__" for p in skill.relative_to(root).parts):
            continue
        text = pub.safe_path(root, str(skill.relative_to(root))).read_text()
        front = re.match(r"\A---\n(.*?)\n---", text, re.S)
        name = (yaml.safe_load(front[1]) or {}).get("name") if front else None
        if not isinstance(name, str) or name in names:
            raise ValueError(f"Missing or duplicate skill name: {skill}")
        names.add(name)
        for path in sorted(skill.parent.rglob("*")):
            if any(p.startswith(".") or p == "__pycache__" for p in path.relative_to(skill.parent).parts):
                continue
            if path.is_symlink():
                raise ValueError(f"Cannot snapshot a skill symlink: {path}")
            if path.is_file():
                files[str(path.relative_to(root))] = path.read_bytes()
    if not files:
        raise ValueError("No skills found for shared release")
    return files, sorted(names)


def config_with_release(raw: bytes, release: Path) -> bytes:
    text = raw.decode()
    cfg = yaml.safe_load(text)
    if not isinstance(cfg, dict) or not isinstance(cfg.get("skills"), dict):
        raise ValueError("Expected an existing skills configuration mapping")
    current = cfg["skills"].get("external_dirs", [])
    if not isinstance(current, list) or any(not isinstance(v, str) for v in current):
        raise ValueError("Expected a list of external skill directories")
    directories = list(dict.fromkeys([str(release), *current]))
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if re.match(r"^skills:\s*(?:#.*)?$", line.rstrip())), None)
    if start is None:
        raise ValueError("Cannot safely edit inline/aliased skills configuration")
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"^[A-Za-z_]", lines[i])), len(lines))
    key = next((i for i in range(start + 1, end) if re.match(r"^  external_dirs:", lines[i])), None)
    block = ["  " + line + "\n" for line in yaml.safe_dump({"external_dirs": directories}, sort_keys=False).splitlines()]
    if key is None:
        lines[start + 1:start + 1] = block
    else:
        stop = next((i for i in range(key + 1, end) if re.match(r"^  [A-Za-z_]\w*:", lines[i])), end)
        lines[key:stop] = block
    rendered = "".join(lines).encode()
    expected = yaml.safe_load(raw)
    expected["skills"]["external_dirs"] = directories
    if yaml.safe_load(rendered) != expected:
        raise ValueError("Config edit changed settings beyond external_dirs")
    return rendered


def preview(home: Path, slug: str) -> tuple[dict, dict[str, bytes], bytes]:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Invalid profile slug")
    profile = pub.safe_path(home, f"profiles/{slug}")
    state = pub.safe_path(home, f"skill-isolation-state/{slug}")
    if (state / "pending.json").exists():
        raise ValueError("Recover interrupted skill isolation first")
    link = profile / "skills"
    if not link.is_symlink() or link.resolve() != (home / "skills").resolve():
        raise ValueError("Pilot requires the original shared skills symlink; private libraries are preserved")
    local = pub.safe_path(profile, "skills.local")
    if local.exists():
        raise ValueError("Existing skills.local requires reconciliation")
    files, names = inventory(home / "skills")
    hashes = {p: pub.digest(b) for p, b in files.items()}
    modes = {p: stat.S_IMODE((home / "skills" / p).stat().st_mode) & 0o555 for p in files}
    release_id = pub.digest(pub.json_bytes({"files": hashes, "modes": modes}))
    release = home / "skill-releases" / release_id
    raw = pub.safe_path(profile, "config.yaml").read_bytes()
    config = config_with_release(raw, release)
    result = {"profile": str(profile), "slug": slug, "release": str(release),
              "files": hashes, "modes": modes, "names": names, "config_before": pub.digest(raw),
              "implementation_sha256": pub.digest(Path(__file__).read_bytes()),
              "config_after": pub.digest(config), "previous_link": os.readlink(link),
              "marker_before": pub.fingerprint(pub.read_file(pub.safe_path(profile, ".no-bundled-skills")))}
    result["plan_hash"] = pub.digest(pub.json_bytes(result))
    return result, files, config


def create_release(home: Path, plan: dict, files: dict[str, bytes]) -> None:
    release = Path(plan["release"])
    with pub.writer_lock(home / "skill-release-state"):
        if release.exists():
            actual, names = inventory(release)
            if {p: pub.digest(b) for p, b in actual.items()} != plan["files"]:
                raise ValueError("Existing immutable skill release has drifted")
            if any(stat.S_IMODE((release / p).stat().st_mode) != mode for p, mode in plan["modes"].items()):
                raise ValueError("Existing immutable skill release permissions have drifted")
            return
        pub.safe_path(release.parent).mkdir(parents=True, exist_ok=True)
        staged = Path(tempfile.mkdtemp(prefix=".staged-", dir=release.parent))
        for name, data in files.items():
            pub.atomic_write(staged / name, data, plan["modes"][name])
        pub.atomic_write(staged / ".release.json", pub.json_bytes({"files": plan["files"], "modes": plan["modes"], "names": plan["names"]}), 0o444)
        for p in sorted(staged.rglob("*"), reverse=True):
            if p.is_dir():
                p.chmod(0o555)
        staged.chmod(0o555)
        os.rename(staged, release)


def switch_link(link: Path, target: str) -> None:
    temp = link.with_name(".skills-switch")
    if temp.exists() or temp.is_symlink():
        raise ValueError("Unfinished skill link switch exists")
    temp.symlink_to(target)
    os.replace(temp, link)


def restore(home: Path, slug: str) -> dict:
    state = pub.safe_path(home, f"skill-isolation-state/{slug}")
    with pub.writer_lock(state):
        receipt = pub.read_json(state / "receipt.json", None)
        if receipt is None or receipt.get("status") == "restored":
            raise ValueError("No current isolation receipt to restore")
        profile = home / "profiles" / slug
        current = pub.safe_path(profile, "config.yaml").read_bytes()
        before = bytes.fromhex(receipt["config_before_hex"])
        if pub.digest(current) not in {pub.digest(before), receipt["config_after"]}:
            raise ValueError("Config has newer edits; reconcile before restoring")
        link = profile / "skills"
        if not link.is_symlink() or os.readlink(link) not in {receipt["previous_link"], str(profile / "skills.local")}:
            raise ValueError("Skills link has newer edits")
        marker = profile / ".no-bundled-skills"
        current_marker = pub.read_file(pub.safe_path(profile, ".no-bundled-skills"))
        old_marker = bytes.fromhex(receipt["marker_before_hex"]) if receipt["marker_before_hex"] is not None else None
        if current_marker not in {old_marker, MARKER}:
            raise ValueError("Bundled-skill marker has newer edits")
        switch_link(link, receipt["previous_link"])
        pub.atomic_write(profile / "config.yaml", before)
        if old_marker is None:
            marker.unlink(missing_ok=True)
        else:
            pub.atomic_write(marker, old_marker)
        receipt["status"] = "restored"
        pub.atomic_write(state / "receipt.json", pub.json_bytes(receipt))
        (state / "pending.json").unlink(missing_ok=True)
        return {"status": "restored", "private_skills_retained": str(profile / "skills.local")}


MARKER = b"Shared bundled skills are supplied by the pinned local release.\n"


def apply(home: Path, slug: str, expected: str) -> dict:
    state = pub.safe_path(home, f"skill-isolation-state/{slug}")
    with pub.writer_lock(state):
        plan, files, config = preview(home, slug)
        if plan["plan_hash"] != expected:
            raise ValueError("Stale skill isolation preview")
        create_release(home, plan, files)
        profile = Path(plan["profile"])
        raw = (profile / "config.yaml").read_bytes()
        marker = pub.read_file(pub.safe_path(profile, ".no-bundled-skills"))
        receipt = {**plan, "config_before_hex": raw.hex(),
                   "marker_before_hex": marker.hex() if marker is not None else None,
                   "status": "prepared"}
        pub.atomic_write(state / "receipt.json", pub.json_bytes(receipt))
        pub.atomic_write(state / "pending.json", b"{}\n")
        local = profile / "skills.local"
        local.mkdir(mode=0o700)
        pub.atomic_write(local / ".usage.json", pub.json_bytes({n: {
            "locked": True, "pinned": True, "state": "active", "portable_owner": "shared-release"
        } for n in plan["names"]}))
        # Recheck settings after preparing the release; do not overwrite an edit
        # made by a concurrently open settings window.
        if pub.digest((profile / "config.yaml").read_bytes()) != plan["config_before"]:
            raise ValueError("Profile settings changed during isolation; recovery required")
        pub.atomic_write(profile / "config.yaml", config)
        pub.atomic_write(profile / ".no-bundled-skills", MARKER)
        switch_link(profile / "skills", str(local))
        receipt["status"] = "complete"
        pub.atomic_write(state / "receipt.json", pub.json_bytes(receipt))
        (state / "pending.json").unlink()
        return {"status": "isolated", "slug": slug, "shared_skills": len(plan["names"]),
                "release": plan["release"], "plan_hash": expected}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("slug")
    p.add_argument("--hermes-home", type=Path, default=Path.home() / ".hermes")
    p.add_argument("--apply", metavar="PLAN_HASH")
    p.add_argument("--restore", action="store_true")
    args = p.parse_args()
    home = args.hermes_home.absolute()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        raise ValueError("Invalid profile slug")
    if args.restore and args.apply:
        raise ValueError("Choose apply or restore")
    result = restore(home, args.slug) if args.restore else apply(home, args.slug, args.apply) if args.apply else preview(home, args.slug)[0]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
