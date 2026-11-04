"""Hash-checked local publication with private backups and crash recovery.

Writers serialize per state directory. Files are atomically replaced individually;
callers must publish to idle runtimes because a multi-file tree is not a snapshot.
"""
from __future__ import annotations

import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
from contextlib import contextmanager
from uuid import uuid4


class PublicationError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def safe_path(root: Path, relative: str = ".") -> Path:
    """Reject traversal, symlinks (including broken links), and special files."""
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise PublicationError(f"Unsafe relative path: {relative}")
    path = root.absolute() / rel
    for part in [*reversed(path.parents), path]:
        if part.is_symlink():
            raise PublicationError(f"Symlink is not a managed publication target: {part}")
        if part.exists() and not (part.is_dir() or part.is_file()):
            raise PublicationError(f"Special file is not a publication target: {part}")
    return path


def read_file(path: Path) -> bytes | None:
    if path.exists() and not path.is_file():
        raise PublicationError(f"Expected a regular file: {path}")
    return path.read_bytes() if path.exists() else None


def fingerprint(data: bytes | None) -> str | None:
    return digest(data) if data is not None else None


def atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    safe_path(path.parent, path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            os.fchmod(handle.fileno(), mode)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read_json(path: Path, default):
    raw = read_file(path)
    return json.loads(raw) if raw is not None else default


@contextmanager
def writer_lock(state: Path):
    safe_path(state)
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    state.chmod(0o700)
    path = safe_path(state, "writer.lock")
    with path.open("a+b") as lock:
        os.chmod(path, 0o600)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise PublicationError(f"Another publisher owns {state}") from exc
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def preview(root: Path, state: Path, files: dict[str, bytes], *,
            seeds=(), source=None, adopt=False) -> dict:
    safe_path(root)
    safe_path(state)
    if read_file(safe_path(state, "pending.json")) is not None:
        raise PublicationError(f"Interrupted publication requires recovery: {state}")
    manifest_raw = read_file(safe_path(state, "manifest.json"))
    manifest = json.loads(manifest_raw) if manifest_raw else {}
    baseline = manifest.get("files", {})
    rows = []
    for name, desired in sorted(files.items()):
        live = read_file(safe_path(root, name))
        actual, wanted = fingerprint(live), digest(desired)
        previous = baseline.get(name)
        if name in seeds and live is not None:
            action = "preserve"
        elif actual == wanted:
            action = "unchanged"
        elif live is None and name not in baseline:
            action = "create"
        elif actual == previous and name in baseline:
            action = "update"
        elif name in baseline and wanted == previous:
            action = "preserve-local"
        elif name not in baseline and adopt:
            action = "adopt-update"
        else:
            action = "conflict"
        rows.append({"path": name, "before": actual, "after": wanted,
                     "action": action, "seed": name in seeds})
    result = {"root": str(root.absolute()), "state": str(state.absolute()),
              "manifest_hash": fingerprint(manifest_raw), "source": source,
              "adopt_existing": adopt, "files": rows}
    result["plan_hash"] = digest(json_bytes(result))
    return result


def _decode(value: str | None) -> bytes | None:
    return base64.b64decode(value, validate=True) if value is not None else None


def _encode(value: bytes | None) -> str | None:
    return base64.b64encode(value).decode() if value is not None else None


def _restore(root: Path, state: Path, journal: dict, *, completed=False) -> None:
    # Preflight the whole restoration before touching any file.
    if journal["root"] != str(root.absolute()):
        raise PublicationError("Recovery root does not match journal")
    restore = []
    for row in journal["writes"]:
        if row["seed"]:  # A newly seeded file may already hold live learning.
            continue
        path = safe_path(root, row["path"])
        actual = fingerprint(read_file(path))
        before = _decode(row["before_data"])
        if actual == fingerprint(before):
            continue
        if actual != row["after"]:
            raise PublicationError(f"Recovery would overwrite a later edit: {path}")
        restore.append((path, before, row["mode"]))
    expected_manifest = journal.get("after_manifest_hash")
    current_manifest = read_file(safe_path(state, "manifest.json"))
    old_manifest = _decode(journal["before_manifest"])
    if fingerprint(current_manifest) not in {fingerprint(old_manifest), expected_manifest}:
        raise PublicationError("Recovery manifest changed after publication")
    for path, before, mode in restore:
        if before is None:
            path.unlink()
        else:
            atomic_write(path, before, mode)
    manifest_path = safe_path(state, "manifest.json")
    if old_manifest is None:
        manifest_path.unlink(missing_ok=True)
    else:
        atomic_write(manifest_path, old_manifest)
    journal["status"] = "rolled-back" if completed else "recovered"
    atomic_write(state / "transactions" / journal["id"] / "journal.json", json_bytes(journal))
    (state / "pending.json").unlink(missing_ok=True)


def recover(root: Path, state: Path, transaction: str | None = None) -> dict:
    with writer_lock(state):
        if transaction is None:
            pending = read_json(safe_path(state, "pending.json"), None)
            if pending is None:
                raise PublicationError("No interrupted publication to recover")
            transaction = pending["id"]
        elif read_file(safe_path(state, "pending.json")) is not None:
            raise PublicationError("Recover the pending publication before rolling back")
        if not re_full_transaction(transaction):
            raise PublicationError("Invalid transaction identifier")
        journal = read_json(safe_path(state, f"transactions/{transaction}/journal.json"), None)
        if journal is None or journal["status"] not in {"prepared", "complete"}:
            raise PublicationError("Transaction is unavailable or already restored")
        if journal["status"] == "complete":
            current = read_json(safe_path(state, "manifest.json"), {})
            if current.get("transaction") != transaction:
                raise PublicationError("Only the current publication can be rolled back")
        _restore(root, state, journal, completed=journal["status"] == "complete")
        return {"transaction": transaction, "status": journal["status"]}


def re_full_transaction(value: str) -> bool:
    return len(value) == 32 and all(c in "0123456789abcdef" for c in value)


def publish(root: Path, state: Path, files: dict[str, bytes], *, expected: str,
            seeds=(), source=None, adopt=False) -> dict:
    with writer_lock(state):
        plan = preview(root, state, files, seeds=seeds, source=source, adopt=adopt)
        if plan["plan_hash"] != expected:
            raise PublicationError("Stale publication preview; inspect a fresh preview")
        conflicts = [r["path"] for r in plan["files"] if r["action"] == "conflict"]
        if conflicts:
            raise PublicationError("Unresolved local/source conflict: " + ", ".join(conflicts))
        previous = read_json(state / "manifest.json", {})
        baseline = dict(previous.get("files", {}))
        writes = []
        for row in plan["files"]:
            if not row["seed"] and row["action"] != "preserve-local":
                baseline[row["path"]] = row["after"]
            if row["action"] in {"create", "update", "adopt-update"}:
                path = safe_path(root, row["path"])
                mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
                writes.append({**row, "before_data": _encode(read_file(path)), "mode": mode})
        if not writes and baseline == previous.get("files", {}) and source == previous.get("source"):
            return {"status": "unchanged", "plan_hash": expected, "transaction": previous.get("transaction")}
        transaction = uuid4().hex
        manifest = {"schema": 1, "transaction": transaction, "source": source, "files": baseline}
        manifest_data = json_bytes(manifest)
        journal = {"id": transaction, "root": str(root.absolute()), "status": "prepared",
                   "writes": writes, "before_manifest": _encode(read_file(state / "manifest.json")),
                   "after_manifest_hash": digest(manifest_data), "plan_hash": expected}
        journal_path = state / "transactions" / transaction / "journal.json"
        atomic_write(journal_path, json_bytes(journal))
        atomic_write(state / "pending.json", json_bytes({"id": transaction}))
        try:
            for row in writes:
                path = safe_path(root, row["path"])
                if fingerprint(read_file(path)) != row["before"]:
                    raise PublicationError(f"Target changed during publication: {path}")
                atomic_write(path, files[row["path"]], row["mode"])
            atomic_write(state / "manifest.json", manifest_data)
            journal["status"] = "complete"
            atomic_write(journal_path, json_bytes(journal))
            (state / "pending.json").unlink()
        except Exception:
            _restore(root, state, journal)
            raise
        return {"status": "published", "transaction": transaction, "plan_hash": expected,
                "changed_paths": [r["path"] for r in writes]}
